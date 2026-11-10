"""Command line interface."""

from datetime import UTC, datetime
from typing import Annotated

import typer

from provenance.config import Repo
from provenance.graph.build import commit_links
from provenance.ingest.git_history import clone as clone_repo
from provenance.ingest.git_history import ingest_history
from provenance.store.db import Store
from provenance.trace.chain import Tracer
from provenance.trace.layer_a import classify_repo, write_ignore_file

app = typer.Typer(no_args_is_help=True, add_completion=False)


@app.command()
def clone(repo: str) -> None:
    """Bare-clone a corpus repo into data/."""
    created = clone_repo(Repo.named(repo))
    typer.echo("Cloned." if created else "Already cloned.")


@app.command()
def ingest(repo: str, rev: str = "HEAD") -> None:
    """Load commit history into SQLite."""
    target = Repo.named(repo)
    with Store(target.db_path) as store:
        added = ingest_history(target, store, rev)
        typer.echo(f"Added {added} commits, {store.commit_count()} stored.")


@app.command()
def classify(repo: str, workers: int = 4) -> None:
    """Find cosmetic commits and write the automatic ignore list."""
    target = Repo.named(repo)

    def progress(done: int) -> None:
        if done % 1000 == 0:
            typer.echo(f"  {done} commits classified", err=True)

    with Store(target.db_path) as store:
        done = classify_repo(target, store, workers, progress)
        listed = write_ignore_file(target, store)
        typer.echo(f"Classified {done} commits: {store.class_counts()}")
        typer.echo(f"Ignore list has {listed} commits: {target.ignore_file}")


@app.command()
def link(repo: str) -> None:
    """Find links to tickets, pull requests and reverted commits in commit messages."""
    from provenance.graph.build import link_messages

    with Store(Repo.named(repo).db_path) as store:
        total = link_messages(repo, store)
        typer.echo(f"Stored {total} links: {store.edge_counts()}")


@app.command("fetch-tickets")
def fetch_tickets_command(
    repo: str,
    limit: Annotated[
        int, typer.Option(help="How many linked tickets to fetch, newest first.")
    ] = 200,
    ticket: Annotated[list[int] | None, typer.Option(help="Also fetch this ticket number.")] = None,
) -> None:
    """Download Trac tickets that commits link to, one request per second."""
    from provenance.graph.refs import TRAC_URLS
    from provenance.ingest.trac import fetch_tickets

    if repo not in TRAC_URLS:
        typer.echo(f"{repo} doesn't use Trac.")
        raise typer.Exit(1)
    with Store(Repo.named(repo).db_path) as store:
        numbers = list(ticket or []) + store.linked_numbers(f"ticket:{repo}/")[:limit]

        def progress(done: int, total: int) -> None:
            if done % 25 == 0 or done == total:
                typer.echo(f"  {done}/{total} tickets", err=True)

        added = fetch_tickets(repo, store, list(dict.fromkeys(numbers)), progress=progress)
        typer.echo(f"Added {added} tickets.")


@app.command()
def mcp(repo: str) -> None:
    """Run the MCP server for a repo, over stdio."""
    from provenance.surfaces.mcp_server import build_server  # slow import, needed only here

    build_server(Repo.named(repo)).run()


@app.command()
def ui(port: int = 8765, open_browser: bool = True) -> None:
    """Start the local web UI at http://127.0.0.1:<port>."""
    import threading
    import webbrowser

    import uvicorn

    from provenance.surfaces.web import available_repos, build_app

    repos = available_repos()
    if not repos:
        typer.echo("No prepared repos found. Run clone, ingest and classify first.")
        raise typer.Exit(1)
    url = f"http://127.0.0.1:{port}"
    typer.echo(f"Provenance UI at {url} for {', '.join(repos)}. Press Ctrl+C to stop.")
    if open_browser:
        threading.Timer(1.0, webbrowser.open, [url]).start()
    uvicorn.run(build_app(repos), host="127.0.0.1", port=port, log_level="warning")


@app.command()
def why(repo: str, path: str, line: int, rev: str = "HEAD") -> None:
    """Trace a line to the change that really introduced it."""
    target = Repo.named(repo)
    with Store(target.db_path) as store:
        tracer = Tracer(target, store)
        chain = tracer.trace(path, line, rev)
        if chain.origin is None:
            typer.echo(f"Could not trace {path}:{line} ({chain.stop_reason}).")
            raise typer.Exit(1)
        typer.echo(f"{path}:{line}  {tracer.line_text(path, line, rev).strip()}\n")
        for hop in chain.hops:
            when = store.commit_time(hop.commit)
            date = datetime.fromtimestamp(when, UTC).date() if when else "?"
            typer.echo(f"  {hop.kind:<9} {hop.commit[:10]}  {date}  {store.subject(hop.commit)}")
            for link in commit_links(store, hop.commit):
                title = f": {link['title_untrusted']}" if "title_untrusted" in link else ""
                typer.echo(f"{'':12}{link['relation']} {link['label']}{title}")
        typer.echo(f"\nLast logic change: {chain.origin[:10]}")
        if chain.first_seen:
            typer.echo(f"First appeared:    {chain.first_seen[:10]} ({chain.stop_reason})")

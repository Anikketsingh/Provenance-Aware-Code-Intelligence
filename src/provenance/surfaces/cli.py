"""Command line interface."""

from datetime import UTC, datetime

import typer

from provenance.config import Repo
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
        typer.echo(f"\nOrigin: {chain.origin[:10]} ({chain.stop_reason})")

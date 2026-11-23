"""Command line interface, installed as both `whyblame` and `provenance`.

Every REPO argument takes either a research corpus name (`django`, `redis`, ...) or a path to
any local git repository (`.` for the current one).
"""

import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

import typer

from provenance.config import Repo, RepoNotFoundError, resolve_repo
from provenance.gitio import GitError
from provenance.graph.build import commit_links
from provenance.store.db import Store

app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    help="Find out why a line of code exists, past reformats, renames and moves.",
)

RepoArg = Annotated[
    str, typer.Argument(help="A path to a git repo (default: here), or a corpus name.")
]


def _prog() -> str:
    return "whyblame" if Path(sys.argv[0]).name.startswith("whyblame") else "provenance"


def _fail(message: str) -> typer.Exit:
    typer.echo(message, err=True)
    return typer.Exit(1)


def _repo(arg: str, *, need_index: bool = True) -> Repo:
    """Resolve a REPO argument, with a plain message instead of a stack trace."""
    from provenance.indexing import is_indexed

    try:
        repo = resolve_repo(arg)
    except RepoNotFoundError as error:
        raise _fail(str(error)) from None
    if need_index and not is_indexed(repo):
        raise _fail(f"{repo.name} isn't indexed yet. Run:  {_prog()} index {arg}")
    return repo


@app.command()
def index(
    repo: RepoArg = ".",
    rev: Annotated[str, typer.Option(help="Index history reachable from this revision.")] = "HEAD",
    workers: Annotated[int, typer.Option(help="Parallel workers for classification.")] = 4,
    github: Annotated[
        bool, typer.Option(help="Also fetch pull requests and issues (needs GITHUB_TOKEN).")
    ] = False,
) -> None:
    """Prepare a repo: load its history, find non-logic changes and link tickets. Incremental."""
    from provenance.indexing import index_repo

    target = _repo(repo, need_index=False)
    if not target.git_dir.exists():
        raise _fail(f"{target.name} isn't cloned yet. Run:  {_prog()} clone {repo}")
    typer.echo(f"Indexing {target.name}", err=True)
    try:
        summary = index_repo(target, rev, workers, lambda m: typer.echo(f"  {m}", err=True))
    except GitError as error:
        raise _fail(f"git failed: {error}") from None
    kinds = ", ".join(f"{count} {kind}" for kind, count in sorted(summary.classes.items()))
    links = sum(summary.links.values())
    typer.echo(
        f"{summary.name}: {summary.total_commits} commits ({summary.new_commits} new), "
        f"{kinds}. {summary.skip_list_commits} commits skipped by tracing, "
        f"{links} links. {summary.seconds:.1f}s."
    )
    if github:
        _crawl_github(target, ["pullRequests", "issues"], None)
    typer.echo(f"Next:  {_prog()} why {repo} <file> <line>    or    {_prog()} mcp {repo}")


def _crawl_github(target: Repo, kinds: list[str], max_pages: int | None) -> None:
    from provenance.config import github_remote
    from provenance.graph.refs import github_slug
    from provenance.ingest.github import MissingTokenError, crawl

    if not github_slug(target.name) and not github_remote(target.git_dir):
        raise _fail(f"{target.name} has no GitHub remote, so there is nothing to crawl.")
    raw_dir = target.db_path.parent / "github-raw"
    with Store(target.db_path) as store:
        for kind in kinds:

            def progress(pages: int, total: int, kind: str = kind) -> None:
                done = min(pages * 50, total) if total else pages * 50
                typer.echo(f"  {kind}: {done}/{total or '?'}", err=True)

            try:
                pages = crawl(
                    target.name, store, raw_dir, kind, max_pages=max_pages, progress=progress
                )
            except MissingTokenError as error:
                raise _fail(f"{error} It's needed to fetch pull requests and issues.") from None
            typer.echo(f"{kind}: {pages} new pages", err=True)
        typer.echo(f"Stored artefacts. Links now: {store.edge_counts()}")


@app.command("crawl-github")
def crawl_github(
    repo: RepoArg = ".",
    kind: Annotated[str, typer.Option(help="prs, issues, or all.")] = "all",
    max_pages: Annotated[int | None, typer.Option(help="Stop after this many pages.")] = None,
) -> None:
    """Fetch the repo's pull requests and issues from GitHub (needs GITHUB_TOKEN). Resumable."""
    kinds = {"prs": ["pullRequests"], "issues": ["issues"], "all": ["pullRequests", "issues"]}
    if kind not in kinds:
        raise _fail("--kind must be prs, issues or all.")
    _crawl_github(_repo(repo), kinds[kind], max_pages)


@app.command()
def check(
    repo: RepoArg = ".",
    base: Annotated[str, typer.Option(help="The revision the change starts from.")] = "HEAD",
    head: Annotated[
        str, typer.Option(help="The changed revision, or WORKTREE for uncommitted files.")
    ] = "WORKTREE",
    fmt: Annotated[str, typer.Option("--format", help="text, json or github.")] = "text",
    threshold: Annotated[
        float | None, typer.Option(help="Report findings scoring at least this (0-1).")
    ] = None,
    show_all: Annotated[bool, typer.Option("--all", help="Also show low scores.")] = False,
    fail_on_findings: Annotated[
        bool, typer.Option(help="Exit with status 1 when something is reported.")
    ] = False,
) -> None:
    """Warn when a change removes or weakens protective code that history says matters."""
    from provenance.gitio import GitError
    from provenance.protect.check import check_change, render
    from provenance.protect.score import DEFAULT_THRESHOLD

    if fmt not in ("text", "json", "github"):
        raise _fail("--format must be text, json or github.")
    target = _repo(repo)
    try:
        findings = check_change(
            target, base, head, DEFAULT_THRESHOLD if threshold is None else threshold
        )
    except (GitError, ValueError, OSError) as error:
        raise _fail(f"Couldn't compare {base} with {head}: {error}") from None
    output = render(findings, fmt, show_all=show_all)
    if output:
        typer.echo(output)
    if fail_on_findings and any(f.flagged for f in findings):
        raise typer.Exit(1)


@app.command()
def clone(repo: str) -> None:
    """Bare-clone a research corpus repo into data/."""
    from provenance.config import REPO_URLS
    from provenance.ingest.git_history import clone as clone_repo

    if repo not in REPO_URLS:
        raise _fail(f"Only corpus repos can be cloned here: {', '.join(sorted(REPO_URLS))}.")
    created = clone_repo(Repo.named(repo))
    typer.echo("Cloned." if created else "Already cloned.")


@app.command()
def ingest(repo: RepoArg = ".", rev: str = "HEAD") -> None:
    """Load commit history into SQLite. (`index` does this and the next steps.)"""
    from provenance.ingest.git_history import ingest_history

    target = _repo(repo, need_index=False)
    with Store(target.db_path) as store:
        added = ingest_history(target, store, rev)
        typer.echo(f"Added {added} commits, {store.commit_count()} stored.")


@app.command()
def classify(repo: RepoArg = ".", workers: int = 4) -> None:
    """Find cosmetic commits and write the automatic ignore list."""
    from provenance.trace.layer_a import classify_repo, write_ignore_file

    target = _repo(repo)

    def progress(done: int) -> None:
        if done % 1000 == 0:
            typer.echo(f"  {done} commits classified", err=True)

    with Store(target.db_path) as store:
        done = classify_repo(target, store, workers, progress)
        listed = write_ignore_file(target, store)
        typer.echo(f"Classified {done} commits: {store.class_counts()}")
        typer.echo(f"Ignore list has {listed} commits: {target.ignore_file}")


@app.command()
def link(repo: RepoArg = ".") -> None:
    """Find links to tickets, pull requests and reverted commits in commit messages."""
    from provenance.graph.build import link_messages

    target = _repo(repo)
    with Store(target.db_path) as store:
        total = link_messages(target.name, store)
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

    target = _repo(repo)
    if target.name not in TRAC_URLS:
        raise _fail(f"{target.name} doesn't use Trac.")
    with Store(target.db_path) as store:
        numbers = list(ticket or []) + store.linked_numbers(f"ticket:{target.name}/")[:limit]

        def progress(done: int, total: int) -> None:
            if done % 25 == 0 or done == total:
                typer.echo(f"  {done}/{total} tickets", err=True)

        added = fetch_tickets(target.name, store, list(dict.fromkeys(numbers)), progress=progress)
        typer.echo(f"Added {added} tickets.")


@app.command("date-tickets")
def date_tickets(
    repo: str,
    every: Annotated[
        int, typer.Option(help="One exactly-dated anchor per this many tickets.")
    ] = 100,
) -> None:
    """Give stored Trac tickets creation dates: exact for anchors, interpolated between them."""
    from provenance.graph.refs import TRAC_URLS
    from provenance.ingest.trac import fetch_anchors, interpolate_created

    target = _repo(repo)
    if target.name not in TRAC_URLS:
        raise _fail(f"{target.name} doesn't use Trac.")
    prefix = f"ticket:{target.name}/"
    with Store(target.db_path) as store:
        rows = store._db.execute(
            "SELECT id FROM artefacts WHERE kind = 'ticket' AND state != 'missing'"
        ).fetchall()
        numbers = sorted(int(node.removeprefix(prefix)) for (node,) in rows)
        if not numbers:
            raise _fail("No tickets stored. Run fetch-tickets first.")
        # Anchors are stored tickets (so they exist), one per `every` ticket numbers.
        wanted = range(numbers[0], numbers[-1] + every, every)
        anchors_to_fetch = sorted({min(numbers, key=lambda n, w=w: abs(n - w)) for w in wanted})
        typer.echo(f"Fetching {len(anchors_to_fetch)} anchor tickets, 1 a second.", err=True)

        def progress(done: int, total: int) -> None:
            if done % 25 == 0 or done == total:
                typer.echo(f"  {done}/{total} anchors", err=True)

        anchors = fetch_anchors(target.name, anchors_to_fetch, progress=progress)
        estimates = interpolate_created(anchors, numbers)
        exact = store.set_created(
            ((f"{prefix}{n}", t) for n, t in anchors.items()), estimated=False
        )
        estimated = store.set_created(
            ((f"{prefix}{n}", t) for n, t in estimates.items() if n not in anchors), estimated=True
        )
        typer.echo(f"{exact} tickets dated exactly, {estimated} estimated from them.")


@app.command()
def search(repo: str, query: list[str], limit: int = 10) -> None:
    """Full-text search over fetched tickets and pull requests."""
    target = _repo(repo)
    with Store(target.db_path) as store:
        hits = store.search_artefacts(" ".join(query), limit)
        if not hits:
            raise _fail("No matches. Have tickets or pull requests been fetched for this repo?")
        for hit in hits:
            typer.echo(f"{hit['id']}  [{hit['state']}]  {hit['title']}")
            typer.echo(f"    {hit['snippet']}")
            typer.echo(f"    {hit['url']}")


@app.command()
def explain(
    repo: str,
    path: str,
    line: int,
    end: Annotated[
        int | None, typer.Argument(help="Explain the block from LINE to END (at most 40 lines).")
    ] = None,
    rev: str = "HEAD",
    fresh: Annotated[bool, typer.Option(help="Call Gemini even if a saved reply exists.")] = False,
) -> None:
    """Trace a line or block, then have Gemini explain it with citations, or abstain."""
    from provenance.surfaces.mcp_server import Explainer
    from provenance.synth.backend import GeminiBackend, MissingKeyError
    from provenance.synth.explain import MAX_BLOCK_LINES, explain_lines

    target = _repo(repo)
    last = max(line, end or line)
    if last - line + 1 > MAX_BLOCK_LINES:
        raise _fail(f"A block can cover at most {MAX_BLOCK_LINES} lines.")
    explainer = Explainer(target)
    whys = [explainer.why_line(path, number, rev) for number in range(line, last + 1)]
    traced = [why for why in whys if why["status"] == "traced"]
    if not traced:
        raise _fail(f"Could not trace {path}:{line} ({whys[0].get('reason')}).")
    try:
        backend = GeminiBackend()
    except MissingKeyError as error:
        raise _fail(str(error)) from None
    with Store(target.db_path) as store:
        result = explain_lines(store, traced, backend, fresh=fresh)
    span = f"{line}" if last == line else f"{line}-{last}"
    typer.echo(f"{path}:{span}  {traced[0].get('code', '')}\n")
    if result["status"] == "explained":
        source = "saved reply" if result["cached"] else "live call"
        typer.echo(result["answer"])
        typer.echo(f"\nConfidence: {result['confidence']}  ({result['model']}, {source})")
        cited = {item["id"]: item for item in result["evidence"]}
        typer.echo("Citations:")
        for cid in result["citations"]:
            item = cited.get(cid)
            if item:
                where = item["url"] or f"commit {item['ref']}"
                typer.echo(f"  [{cid}] {item['kind']} {item['ref']}: {item['title']}  {where}")
    else:
        typer.echo(f"Abstained: {result.get('reason', 'not enough evidence')}")
        typer.echo(f"The trace itself still stands. Run `{_prog()} why` to see it.")


@app.command()
def init(repo: RepoArg = ".") -> None:
    """Tell agents in this repo to use whyblame, and print how to register it in each client.

    Adds a short rule to AGENTS.md, CLAUDE.md, GEMINI.md and .cursor/rules/whyblame.mdc,
    between marker comments, so running it again changes nothing and your text is kept."""
    import subprocess

    from provenance.agent_rules import registrations, write_rules
    from provenance.indexing import is_indexed

    target = _repo(repo, need_index=False)
    try:
        root = Path(
            subprocess.run(
                ["git", "-C", repo, "rev-parse", "--show-toplevel"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
        )
    except (subprocess.CalledProcessError, OSError):
        raise _fail(f"{repo} has no working tree (a bare repo?); run init in a checkout.") from None

    typer.echo(f"Agent rules in {root}:")
    for result in write_rules(root):
        why = f"  ({result.reason})" if result.reason else ""
        typer.echo(f"  {result.action:9} {result.path}{why}")
    typer.echo("\nRegister the server in your client (once per client):")
    for client, how in registrations(root):
        typer.echo(f"\n  {client}:")
        typer.echo("\n".join(f"    {row}" for row in how.splitlines()))
    if not is_indexed(target):
        typer.echo("\nThen index the history (once; later runs only add new commits):")
        typer.echo(f"  {_prog()} index {root}")


LOOPBACK = ("127.0.0.1", "localhost", "::1")


@app.command()
def mcp(
    repo: RepoArg = ".",
    http: Annotated[
        bool, typer.Option(help="Serve Streamable HTTP at http://HOST:PORT/mcp, not stdio.")
    ] = False,
    host: Annotated[str, typer.Option(help="With --http: the address to listen on.")] = (
        "127.0.0.1"
    ),
    port: Annotated[int, typer.Option(help="With --http: the port.")] = 8766,
) -> None:
    """Run the MCP server for a repo, over stdio by default. Register it with your agent, e.g.
    claude mcp add whyblame -- whyblame mcp /path/to/repo   (or run `whyblame init` there)"""
    from provenance.surfaces.mcp_server import build_server  # slow import, needed only here

    server = build_server(_repo(repo))
    if not http:
        # stdout carries the protocol, so every message here goes to stderr.
        server.run()
        return
    if host not in LOOPBACK:
        typer.echo(
            f"Warning: listening on {host}, not only this machine. Anyone who can reach it "
            "can read this repo's history through the tools; there is no authentication.",
            err=True,
        )
    typer.echo(f"whyblame MCP server at http://{host}:{port}/mcp", err=True)
    server.run("streamable-http", host=host, port=port)


@app.command()
def ui(
    repos: Annotated[
        list[str] | None, typer.Argument(help="Repos to show (default: every corpus repo).")
    ] = None,
    port: int = 8765,
    open_browser: bool = True,
) -> None:
    """Start the local web UI at http://127.0.0.1:<port>."""
    import threading
    import webbrowser

    import uvicorn

    from provenance.surfaces.web import RepoView, available_repos, build_app, pinned_revs

    if repos:
        revs = pinned_revs()
        views = {}
        for arg in repos:
            target = _repo(arg)
            views[target.name] = RepoView(target, revs.get(target.name, "HEAD"))
    else:
        views = available_repos()
    if not views:
        raise _fail(f"No indexed repos found. Run:  {_prog()} index <path>  first.")
    url = f"http://127.0.0.1:{port}"
    typer.echo(f"UI at {url} for {', '.join(views)}. Press Ctrl+C to stop.")
    if open_browser:
        threading.Timer(1.0, webbrowser.open, [url]).start()
    uvicorn.run(build_app(views), host="127.0.0.1", port=port, log_level="warning")


@app.command()
def why(repo: str, path: str, line: int, rev: str = "HEAD") -> None:
    """Trace a line to the change that really introduced it."""
    from provenance.trace.chain import Tracer

    target = _repo(repo)
    with Store(target.db_path) as store:
        tracer = Tracer(target, store)
        try:
            chain = tracer.trace(path, line, rev)
        except GitError as error:
            raise _fail(f"git couldn't read {path} at {rev}: {error}") from None
        if chain.origin is None:
            raise _fail(f"Could not trace {path}:{line} ({chain.stop_reason}).")
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

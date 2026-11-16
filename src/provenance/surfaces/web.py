"""Local web UI: browse a repo, click a line, and see why it exists.

It serves one page and a small read-only JSON API on 127.0.0.1. Line explanations come from
the same code the MCP server uses, so the UI shows exactly what an agent would receive.
"""

import json
import threading
from collections import OrderedDict
from datetime import UTC, datetime
from pathlib import Path

from starlette.applications import Starlette
from starlette.concurrency import run_in_threadpool
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse
from starlette.routing import Route

from provenance.config import DATA_DIR, PROJECT_ROOT, Repo
from provenance.gitio import GitError, git, validate_rev
from provenance.store.db import Store
from provenance.surfaces.mcp_server import Explainer, safe_path
from provenance.synth.backend import GeminiBackend, MissingKeyError
from provenance.synth.explain import MAX_BLOCK_LINES, explain_lines
from provenance.trace.blame import STRONGEST_FLAGS, BlameLine, blame_file
from provenance.trace.tokens import language_for

STATIC_DIR = Path(__file__).parent / "static"
RESULTS_DIR = PROJECT_ROOT / "eval" / "results"
LOCK_FILE = PROJECT_ROOT / "eval" / "corpus.lock.json"
#: Blaming a file takes seconds, so keep a few recent ones.
_CACHED_FILES = 6
_SHORT = 10


_backend: GeminiBackend | None = None


def _gemini() -> GeminiBackend:
    """One shared Gemini client, created on the first explanation."""
    global _backend
    if _backend is None:
        _backend = GeminiBackend()
    return _backend


def pinned_revs() -> dict[str, str]:
    try:
        return json.loads(LOCK_FILE.read_text())
    except (OSError, ValueError):
        return {}


class RepoView:
    """Everything the UI shows for one repo, at one revision."""

    def __init__(self, repo: Repo, rev: str):
        self.repo = repo
        self.rev = validate_rev(rev)
        self._store = Store(repo.db_path, shared=True)
        self._explainer = Explainer(repo)
        self._lock = threading.Lock()
        self._files: list[str] | None = None
        self._blames: OrderedDict[str, dict] = OrderedDict()

    def summary(self) -> dict:
        return {
            "name": self.repo.name,
            "rev": self.rev,
            "commits": self._store.commit_count(),
            "classes": self._store.class_counts(),
        }

    def files(self) -> list[str]:
        with self._lock:
            if self._files is None:
                listing = git(self.repo.git_dir, "ls-tree", "-r", "--name-only", self.rev)
                self._files = [p for p in listing.splitlines() if language_for(p)]
            return self._files

    def _check(self, path: str) -> str:
        safe_path(path)
        if path not in set(self.files()):
            raise LookupError(f"no supported source file named {path!r}")
        return path

    def _commit(self, sha: str, path: str | None = None) -> dict:
        when = self._store.commit_time(sha)
        info = {
            "commit": sha,
            "short": sha[:_SHORT],
            "date": datetime.fromtimestamp(when, UTC).date().isoformat() if when else None,
            "subject_untrusted": self._store.subject(sha),
        }
        if path is not None:
            kind = self._store.file_kind(sha, path)
            info["kind"] = str(kind) if kind else None
        return info

    def file(self, path: str) -> dict:
        path = self._check(path)
        with self._lock:
            if path not in self._blames:
                plain = blame_file(self.repo.git_dir, path, self.rev, flags=())
                ours = blame_file(
                    self.repo.git_dir,
                    path,
                    self.rev,
                    flags=(),
                    ignore_revs=self._store.non_logic_commits(path),
                )
                self._blames[path] = self._describe_file(plain, ours)
                if len(self._blames) > _CACHED_FILES:
                    self._blames.popitem(last=False)
            self._blames.move_to_end(path)
            return self._blames[path]

    def _describe_file(self, plain: list[BlameLine], ours: list[BlameLine]) -> dict:
        commits: dict[str, dict] = {}
        lines = []
        for number, (before, after) in enumerate(zip(plain, ours, strict=True), start=1):
            for blamed in (before, after):
                if blamed.commit not in commits:
                    commits[blamed.commit] = self._commit(blamed.commit, blamed.orig_path)
            lines.append(
                {"n": number, "text": before.text, "blame": before.commit, "ours": after.commit}
            )
        differs = sum(line["blame"] != line["ours"] for line in lines)
        return {"lines": lines, "commits": commits, "differs": differs}

    def search(self, query: str) -> list[dict]:
        with self._lock:
            return self._store.search_artefacts(query, limit=25)

    def explain(self, path: str, number: int, end: int | None = None, fresh: bool = False) -> dict:
        """Trace a line or a block, then a cited Gemini explanation or an abstention."""
        path = self._check(path)
        last = max(number, end or number)
        if last - number + 1 > MAX_BLOCK_LINES:
            raise ValueError(f"a block can cover at most {MAX_BLOCK_LINES} lines")
        try:
            backend = _gemini()
        except MissingKeyError as error:
            return {"status": "unavailable", "reason": str(error)}
        with self._lock:
            whys = [self._explainer.why_line(path, n, self.rev) for n in range(number, last + 1)]
            return explain_lines(self._store, whys, backend, fresh=fresh)

    def line(self, path: str, number: int) -> dict:
        path = self._check(path)
        with self._lock:
            agent_view = self._explainer.why_line(path, number, self.rev)
            strongest = blame_file(
                self.repo.git_dir,
                path,
                self.rev,
                flags=(*STRONGEST_FLAGS, "-L", f"{number},{number}"),
            )
            plain = blame_file(
                self.repo.git_dir, path, self.rev, flags=("-L", f"{number},{number}")
            )
            commits = {}
            for blamed in (*plain, *strongest):
                commits[blamed.commit] = self._commit(blamed.commit, blamed.orig_path)
            for hop in agent_view.get("chain", []):
                commits.setdefault(hop["commit"], self._commit(hop["commit"], hop["path"]))
        return {
            "agent_view": agent_view,
            "plain_blame": plain[0].commit if plain else None,
            "strongest_blame": strongest[0].commit if strongest else None,
            "commits": commits,
        }


def load_results() -> dict:
    """Headline numbers from the saved evaluation runs, without per-line detail."""
    found = {}
    for name in (
        "gold_scores",
        "gold_scores_test",
        "method_gap",
        "ignore_list_django",
        "ast_oracle_django",
    ):
        path = RESULTS_DIR / f"{name}.json"
        try:
            data = json.loads(path.read_text())
        except (OSError, ValueError):
            continue
        found[name] = {
            key: value
            for key, value in data.items()
            if key not in ("lines", "disputed", "bad_renames", "missed", "flagged")
        }
    return found


def build_app(repos: dict[str, RepoView]) -> Starlette:
    def view_for(request: Request) -> RepoView:
        name = request.query_params.get("repo", "")
        if name not in repos:
            raise LookupError(f"unknown repo {name!r}")
        return repos[name]

    async def guarded(work) -> JSONResponse:
        try:
            return JSONResponse(await run_in_threadpool(work))
        except LookupError as error:
            return JSONResponse({"error": str(error)}, status_code=404)
        except (ValueError, GitError) as error:
            return JSONResponse({"error": str(error)}, status_code=400)

    async def index(_request: Request) -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    async def api_repos(_request: Request) -> JSONResponse:
        return await guarded(
            lambda: [{**view.summary(), "name": name} for name, view in repos.items()]
        )

    async def api_files(request: Request) -> JSONResponse:
        return await guarded(lambda: view_for(request).files())

    async def api_file(request: Request) -> JSONResponse:
        return await guarded(lambda: view_for(request).file(request.query_params.get("path", "")))

    async def api_line(request: Request) -> JSONResponse:
        def work() -> dict:
            number = int(request.query_params.get("line", "0"))
            if number < 1:
                raise ValueError("line numbers start at 1")
            return view_for(request).line(request.query_params.get("path", ""), number)

        return await guarded(work)

    async def api_results(_request: Request) -> JSONResponse:
        return await guarded(load_results)

    async def api_search(request: Request) -> JSONResponse:
        return await guarded(lambda: view_for(request).search(request.query_params.get("q", "")))

    async def api_explain(request: Request) -> JSONResponse:
        def work() -> dict:
            number = int(request.query_params.get("line", "0"))
            if number < 1:
                raise ValueError("line numbers start at 1")
            end = int(request.query_params.get("end", "0")) or None
            fresh = request.query_params.get("fresh") == "1"
            return view_for(request).explain(
                request.query_params.get("path", ""), number, end, fresh
            )

        return await guarded(work)

    return Starlette(
        routes=[
            Route("/", index),
            Route("/api/repos", api_repos),
            Route("/api/files", api_files),
            Route("/api/file", api_file),
            Route("/api/line", api_line),
            Route("/api/results", api_results),
            Route("/api/search", api_search),
            Route("/api/explain", api_explain),
        ]
    )


def available_repos(data_dir: Path | None = None) -> dict[str, RepoView]:
    """Every repo that has been ingested and classified, at its pinned revision if known."""
    revs = pinned_revs()
    views = {}
    root = data_dir or DATA_DIR
    if not root.is_dir():
        return views
    for folder in sorted(root.iterdir()):
        repo = Repo.named(folder.name, root)
        if repo.db_path.is_file() and repo.git_dir.is_dir():
            views[repo.name] = RepoView(repo, revs.get(repo.name, "HEAD"))
    return views

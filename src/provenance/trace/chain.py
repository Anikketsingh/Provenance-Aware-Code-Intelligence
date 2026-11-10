"""Trace a line to the change that really introduced it."""

from collections import OrderedDict

from provenance.config import Repo
from provenance.gitio import git
from provenance.model import CONTINUES_TRACING, Chain, ChangeKind, Hop
from provenance.store.db import Store
from provenance.trace.blame import TRACE_FLAGS, BlameLine, blame_file
from provenance.trace.classify import CONFIDENCE
from provenance.trace.hop import Hunk, parse_diff, step_back

#: Long histories exist, but a chain this deep is more likely a loop of poor matches.
MAX_HOPS = 25
#: Some commits have huge diffs, so only recent ones stay in memory.
_MAX_CACHED_DIFFS = 32


class Tracer:
    """Traces lines in one repo, blaming each file only once per revision."""

    def __init__(self, repo: Repo, store: Store, flags: tuple[str, ...] = TRACE_FLAGS):
        self._repo = repo
        self._store = store
        self._flags = flags
        self._blames: dict[tuple[str, str, bool], list[BlameLine]] = {}
        self._diffs: OrderedDict[str, list[Hunk]] = OrderedDict()

    def _blame(self, path: str, rev: str, *, skip_cosmetic: bool) -> list[BlameLine]:
        key = (path, rev, skip_cosmetic)
        if key not in self._blames:
            ignore = self._store.non_logic_commits(path) if skip_cosmetic else ()
            self._blames[key] = blame_file(
                self._repo.git_dir, path, rev, flags=self._flags, ignore_revs=ignore
            )
        return self._blames[key]

    def _hunks(self, commit: str, parent: str) -> list[Hunk]:
        if commit not in self._diffs:
            text = git(
                self._repo.git_dir,
                "diff",
                "-U0",
                "-M",
                "--no-color",
                "--no-ext-diff",
                parent,
                commit,
            )
            self._diffs[commit] = parse_diff(text)
            if len(self._diffs) > _MAX_CACHED_DIFFS:
                self._diffs.popitem(last=False)
        return self._diffs[commit]

    def line_text(self, path: str, line: int, rev: str = "HEAD") -> str:
        return self._blame(path, rev, skip_cosmetic=False)[line - 1].text

    def trace(self, path: str, line: int, rev: str = "HEAD") -> Chain:
        direct = self._blame(path, rev, skip_cosmetic=False)
        if not 1 <= line <= len(direct):
            return Chain(path, line, rev, (), None, "lost_line")

        hops: list[Hop] = []
        first = direct[line - 1]
        first_kind = self._store.file_kind(first.commit, first.orig_path)
        if first_kind in CONTINUES_TRACING:
            hops.append(_hop(first, first_kind, CONFIDENCE[first_kind]))

        final = self._blame(path, rev, skip_cosmetic=True)[line - 1]
        return self._walk_back(path, line, rev, hops, final)

    def _walk_back(
        self, path: str, line: int, rev: str, hops: list[Hop], current: BlameLine
    ) -> Chain:
        origin: str | None = None

        def done(stop_reason: str, first_seen: str | None) -> Chain:
            return Chain(path, line, rev, tuple(hops), origin, stop_reason, first_seen)

        for _ in range(MAX_HOPS):
            commit = current.commit
            parents = self._store.parents(commit)
            if not parents:
                hops.append(_hop(current, ChangeKind.ORIGIN, CONFIDENCE[ChangeKind.LOGIC]))
                origin = origin or commit
                return done("root", commit)

            step = step_back(self._hunks(commit, parents[0]), current.orig_path, current.orig_line)
            if step is None or step.kind == ChangeKind.ORIGIN:
                # Not in the diff, or nothing older matches: treat this as where it began.
                hops.append(_hop(current, ChangeKind.ORIGIN, CONFIDENCE[ChangeKind.LOGIC]))
                origin = origin or commit
                return done("first_appearance", commit)

            hops.append(_hop(current, step.kind, step.confidence))
            if step.kind == ChangeKind.LOGIC:
                origin = origin or commit

            older = self._blame_at(step.path, step.line, parents[0])
            if older is None:
                origin = origin or commit
                return done("lost_line", commit)
            current = older

        origin = origin or current.commit
        return done("limit", current.commit)

    def _blame_at(self, path: str, line: int, rev: str) -> BlameLine | None:
        try:
            blamed = self._blame(path, rev, skip_cosmetic=True)
        except RuntimeError:
            return None
        return blamed[line - 1] if 1 <= line <= len(blamed) else None


def _hop(blame: BlameLine, kind: ChangeKind, confidence: float) -> Hop:
    return Hop(blame.commit, kind, blame.orig_path, blame.orig_line, confidence)

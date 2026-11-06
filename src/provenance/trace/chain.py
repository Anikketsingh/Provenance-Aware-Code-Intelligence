"""Trace a line to the change that really introduced it (Layers A and B)."""

from provenance.config import Repo
from provenance.model import CONTINUES_TRACING, Chain, ChangeKind, Hop
from provenance.store.db import Store
from provenance.trace.blame import BlameLine, blame_file
from provenance.trace.classify import CONFIDENCE


class Tracer:
    """Traces lines in one repo, blaming each file only once per revision."""

    def __init__(self, repo: Repo, store: Store):
        self._repo = repo
        self._store = store
        self._cache: dict[tuple[str, str, bool], list[BlameLine]] = {}

    def _blame(self, path: str, rev: str, *, skip_cosmetic: bool) -> list[BlameLine]:
        key = (path, rev, skip_cosmetic)
        if key not in self._cache:
            ignore = self._store.non_logic_commits(path) if skip_cosmetic else ()
            self._cache[key] = blame_file(self._repo.git_dir, path, rev, ignore_revs=ignore)
        return self._cache[key]

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
            hops.append(_hop(first, first_kind))

        final = self._blame(path, rev, skip_cosmetic=True)[line - 1]
        if hops and final.commit == first.commit:
            # Git could not place the line in an earlier commit, so this is the best answer.
            return Chain(path, line, rev, tuple(hops), first.commit, "lost_line")

        is_root = not self._store.parents(final.commit)
        kind = ChangeKind.ORIGIN if is_root else ChangeKind.LOGIC
        hops.append(_hop(final, kind))
        stop_reason = "root" if is_root else "logic_change"
        return Chain(path, line, rev, tuple(hops), final.commit, stop_reason)


def _hop(blame: BlameLine, kind: ChangeKind) -> Hop:
    confidence = CONFIDENCE.get(kind, CONFIDENCE[ChangeKind.LOGIC])
    return Hop(blame.commit, kind, blame.orig_path, blame.orig_line, confidence)

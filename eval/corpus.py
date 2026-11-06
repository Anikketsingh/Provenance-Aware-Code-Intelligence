"""Pinned corpus versions and the commit each method blames for each line."""

import json
from dataclasses import dataclass, field
from pathlib import Path

from provenance.config import Repo
from provenance.gitio import git
from provenance.store.db import Store
from provenance.trace.blame import STRONGEST_FLAGS, BlameLine, blame_file

LOCK_FILE = Path(__file__).parent / "corpus.lock.json"


def pinned_rev(name: str) -> str:
    return json.loads(LOCK_FILE.read_text())[name]


def hand_list(repo: Repo, rev: str) -> list[str]:
    """Return the repo's own ignore list, or nothing if it doesn't keep one."""
    try:
        text = git(repo.git_dir, "show", f"{rev}:.git-blame-ignore-revs")
    except RuntimeError:
        return []
    lines = (line.strip() for line in text.splitlines())
    return [line for line in lines if line and not line.startswith("#")]


@dataclass
class Baselines:
    """Blame results per method, for one file. See plans/04-provenance-engine.md for the IDs."""

    repo: Repo
    store: Store
    rev: str
    listed: list[str]
    _cache: dict[str, dict[str, list[BlameLine]]] = field(default_factory=dict)

    def blame_all(self, path: str) -> dict[str, list[BlameLine]]:
        if path not in self._cache:
            self._cache[path] = self._blame_methods(path)
        return self._cache[path]

    def _blame_methods(self, path: str) -> dict[str, list[BlameLine]]:
        git_dir, rev = self.repo.git_dir, self.rev
        results = {
            "B0": blame_file(git_dir, path, rev, flags=()),
            "B1": blame_file(git_dir, path, rev, flags=("-w", "-M")),
            "B2": blame_file(git_dir, path, rev, flags=STRONGEST_FLAGS),
            "Ours-A": blame_file(
                git_dir, path, rev, ignore_revs=self.store.non_logic_commits(path)
            ),
        }
        if self.listed:
            results["B3"] = blame_file(git_dir, path, rev, ignore_revs=self.listed)
        return results

"""Clone repos and load their history into SQLite."""

import subprocess

from provenance.config import REPO_URLS, Repo
from provenance.gitio import iter_commits
from provenance.store.db import Store

_COMMIT_EVERY = 1000


def clone(repo: Repo) -> bool:
    """Bare-clone the repo. Returns False if it already exists."""
    if repo.git_dir.exists():
        return False
    repo.git_dir.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "clone", "--quiet", "--bare", REPO_URLS[repo.name], str(repo.git_dir)],
        check=True,
    )
    return True


def ingest_history(repo: Repo, store: Store, rev: str = "HEAD") -> int:
    """Store every commit reachable from rev. Safe to re-run, and returns how many were added."""
    added = 0
    for record in iter_commits(repo.git_dir, rev):
        if store.has_commit(record.sha):
            continue
        store.add_commit(record)
        added += 1
        if added % _COMMIT_EVERY == 0:
            store.commit()
    store.commit()
    return added

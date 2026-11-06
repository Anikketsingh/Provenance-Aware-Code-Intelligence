"""Classify a repo's hand-kept ignore list, to see which listed commits we would miss."""

import sys
import time

from provenance.config import Repo
from provenance.gitio import BlobReader, git
from provenance.store.db import Store
from provenance.trace.classify import MAX_BLOB_SIZE, classify_change, classify_commit


def listed_commits(repo: Repo) -> list[str]:
    text = git(repo.git_dir, "show", "HEAD:.git-blame-ignore-revs")
    lines = (line.strip() for line in text.splitlines())
    return [line for line in lines if line and not line.startswith("#")]


def main(name: str) -> None:
    repo = Repo.named(name)
    with Store(repo.db_path) as store, BlobReader(repo.git_dir) as reader:
        read = lambda blob: reader.read(blob, MAX_BLOB_SIZE)  # noqa: E731
        for sha in listed_commits(repo):
            changes = store.changes(sha)
            start = time.time()
            result = classify_commit(changes, read)
            elapsed = time.time() - start
            logic_files = sum(classify_change(c, read) == "logic" for c in changes)
            print(
                f"{sha[:10]} {result.kind:9} files={len(changes):5} logic={logic_files:4} "
                f"{elapsed:6.2f}s {store.subject(sha)[:60]}  [{result.reason}]"
            )


if __name__ == "__main__":
    main(sys.argv[1])

"""Prepare a repo in one step: load history, find non-logic changes, write skip lists, link.

Every step is incremental, so indexing again after new commits only does the new work.
"""

import time
from collections.abc import Callable
from dataclasses import dataclass

from provenance.config import Repo
from provenance.graph.build import link_messages
from provenance.ingest.git_history import ingest_history
from provenance.store.db import Store
from provenance.trace.layer_a import classify_repo, write_ignore_file


@dataclass(frozen=True)
class IndexSummary:
    name: str
    new_commits: int
    total_commits: int
    newly_classified: int
    classes: dict[str, int]
    skip_list_commits: int
    links: dict[str, int]
    seconds: float


def index_repo(
    repo: Repo,
    rev: str = "HEAD",
    workers: int = 4,
    progress: Callable[[str], None] | None = None,
) -> IndexSummary:
    say = progress or (lambda _message: None)
    started = time.perf_counter()
    with Store(repo.db_path) as store:
        say("Loading history")
        added = ingest_history(repo, store, rev)

        def classified(done: int) -> None:
            if done % 1000 == 0:
                say(f"  {done} commits classified")

        say("Classifying changes")
        newly = classify_repo(repo, store, workers, classified)
        say("Writing skip lists")
        listed = write_ignore_file(repo, store)
        say("Linking commits to tickets and pull requests")
        link_messages(repo.name, store)
        return IndexSummary(
            name=repo.name,
            new_commits=added,
            total_commits=store.commit_count(),
            newly_classified=newly,
            classes=store.class_counts(),
            skip_list_commits=listed,
            links=store.edge_counts(),
            seconds=time.perf_counter() - started,
        )


def is_indexed(repo: Repo) -> bool:
    if not repo.db_path.is_file():
        return False
    with Store(repo.db_path) as store:
        return store.commit_count() > 0

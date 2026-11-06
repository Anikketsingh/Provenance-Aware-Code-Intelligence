"""Classify every commit in a repo in parallel, and write the automatic ignore list."""

from collections.abc import Callable, Iterator
from concurrent.futures import ProcessPoolExecutor
from itertools import islice
from pathlib import Path

from provenance.config import Repo
from provenance.gitio import BlobReader, FileChange
from provenance.model import CONTINUES_TRACING
from provenance.store.db import Store
from provenance.trace.classify import ALGO_VERSION, CONFIDENCE, MAX_BLOB_SIZE, classify_commit

#: The M1 has four performance cores, and more workers would risk swapping on 8 GB.
DEFAULT_WORKERS = 4
_BATCH_SIZE = 100

Task = tuple[str, bool, list[FileChange]]
Row = tuple[str, str, float, str, int, tuple[tuple[str, str], ...]]


def _classify_batch(git_dir: Path, batch: list[Task]) -> list[Row]:
    rows = []
    with BlobReader(git_dir) as reader:
        read = lambda blob: reader.read(blob, MAX_BLOB_SIZE)  # noqa: E731
        for sha, is_merge, changes in batch:
            result = classify_commit(changes, read, is_merge=is_merge)
            files = tuple((path, str(kind)) for path, kind in result.non_logic_files)
            rows.append(
                (sha, str(result.kind), CONFIDENCE[result.kind], result.reason, ALGO_VERSION, files)
            )
    return rows


def _batches(tasks: Iterator[Task]) -> Iterator[list[Task]]:
    while batch := list(islice(tasks, _BATCH_SIZE)):
        yield batch


def classify_repo(
    repo: Repo,
    store: Store,
    workers: int = DEFAULT_WORKERS,
    on_progress: Callable[[int], None] | None = None,
) -> int:
    """Classify commits not yet done at this version. Interrupted runs simply resume."""
    tasks = list(store.unclassified(ALGO_VERSION))
    done = 0
    batches = list(_batches(iter(tasks)))
    with ProcessPoolExecutor(max_workers=workers) as pool:
        results = pool.map(_classify_batch, [repo.git_dir] * len(batches), batches)
        for rows in results:
            store.save_classes(rows)
            done += len(rows)
            if on_progress:
                on_progress(done)
    return done


def write_ignore_file(repo: Repo, store: Store) -> int:
    """Write commits that are non-logic in every file. Tracing uses the finer per-file list."""
    shas = store.commits_of_kind(CONTINUES_TRACING)
    repo.ignore_file.write_text("".join(f"{sha}\n" for sha in shas))
    return len(shas)

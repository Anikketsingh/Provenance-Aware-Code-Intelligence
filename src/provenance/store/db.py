"""SQLite access. Each repo has one database file."""

import sqlite3
from collections.abc import Iterable, Iterator
from importlib import resources
from pathlib import Path

from provenance.gitio import CommitRecord, FileChange
from provenance.model import ChangeKind


class Store:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(path)
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute("PRAGMA synchronous=NORMAL")
        schema = resources.files("provenance.store").joinpath("schema.sql").read_text()
        self._db.executescript(schema)

    def close(self) -> None:
        self._db.close()

    def __enter__(self) -> "Store":
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def commit(self) -> None:
        self._db.commit()

    def has_commit(self, sha: str) -> bool:
        row = self._db.execute("SELECT 1 FROM commits WHERE sha = ?", (sha,)).fetchone()
        return row is not None

    def add_commit(self, record: CommitRecord) -> None:
        self._db.execute(
            "INSERT INTO commits VALUES (?, ?, ?, ?, ?, ?)",
            (
                record.sha,
                record.author_time,
                record.commit_time,
                record.subject,
                record.body,
                int(len(record.parents) > 1),
            ),
        )
        self._db.executemany(
            "INSERT INTO commit_parents VALUES (?, ?, ?)",
            [(record.sha, parent, i) for i, parent in enumerate(record.parents)],
        )
        self._db.executemany(
            "INSERT INTO file_changes VALUES (?, ?, ?, ?, ?, ?)",
            [
                (record.sha, c.status, c.old_path, c.path, c.old_blob, c.new_blob)
                for c in record.changes
            ],
        )

    def full_sha(self, prefix: str) -> str:
        row = self._db.execute(
            "SELECT sha FROM commits WHERE sha >= ? AND sha < ? LIMIT 1",
            (prefix, prefix + "g"),
        ).fetchone()
        if row is None:
            raise KeyError(prefix)
        return row[0]

    def commit_count(self) -> int:
        return self._db.execute("SELECT count(*) FROM commits").fetchone()[0]

    def parents(self, sha: str) -> list[str]:
        rows = self._db.execute(
            "SELECT parent_sha FROM commit_parents WHERE sha = ? ORDER BY position", (sha,)
        )
        return [row[0] for row in rows]

    def subject(self, sha: str) -> str:
        row = self._db.execute("SELECT subject FROM commits WHERE sha = ?", (sha,)).fetchone()
        return row[0] if row else ""

    def commit_time(self, sha: str) -> int | None:
        row = self._db.execute("SELECT commit_time FROM commits WHERE sha = ?", (sha,)).fetchone()
        return row[0] if row else None

    def changes(self, sha: str) -> list[FileChange]:
        rows = self._db.execute(
            "SELECT status, old_path, path, old_blob, new_blob FROM file_changes WHERE sha = ?",
            (sha,),
        )
        return [FileChange(*row) for row in rows]

    def unclassified(self, algo_version: int) -> Iterator[tuple[str, bool, list[FileChange]]]:
        """Yield commits still needing classification at this algorithm version."""
        shas = self._db.execute(
            """SELECT c.sha, c.is_merge FROM commits c
               LEFT JOIN commit_class k ON k.sha = c.sha AND k.algo_version = ?
               WHERE k.sha IS NULL""",
            (algo_version,),
        ).fetchall()
        for sha, is_merge in shas:
            yield sha, bool(is_merge), self.changes(sha)

    def save_classes(self, rows: Iterable[tuple]) -> None:
        for sha, kind, confidence, reason, version, files in rows:
            self._db.execute(
                "INSERT OR REPLACE INTO commit_class VALUES (?, ?, ?, ?, ?)",
                (sha, kind, confidence, reason, version),
            )
            self._db.execute("DELETE FROM file_class WHERE sha = ?", (sha,))
            self._db.executemany(
                "INSERT INTO file_class VALUES (?, ?, ?)",
                [(sha, path, file_kind) for path, file_kind in files],
            )
        self._db.commit()

    def file_kind(self, sha: str, path: str) -> ChangeKind | None:
        row = self._db.execute(
            "SELECT kind FROM file_class WHERE sha = ? AND path = ?", (sha, path)
        ).fetchone()
        return ChangeKind(row[0]) if row else None

    def path_history(self, path: str) -> set[str]:
        """Return this path and every earlier name it had, following recorded renames."""
        names = {path}
        frontier = [path]
        while frontier:
            current = frontier.pop()
            rows = self._db.execute(
                "SELECT old_path FROM file_changes WHERE path = ? AND status = 'R'", (current,)
            )
            for (old_path,) in rows.fetchall():
                if old_path not in names:
                    names.add(old_path)
                    frontier.append(old_path)
        return names

    def non_logic_commits(self, path: str) -> list[str]:
        """Commits whose change to this file, under any of its names, was not a logic change."""
        names = list(self.path_history(path))
        found: set[str] = set()
        for start in range(0, len(names), 500):
            part = names[start : start + 500]
            marks = ",".join("?" * len(part))
            rows = self._db.execute(f"SELECT sha FROM file_class WHERE path IN ({marks})", part)
            found.update(row[0] for row in rows)
        return sorted(found)

    def commit_kind(self, sha: str) -> ChangeKind | None:
        row = self._db.execute("SELECT kind FROM commit_class WHERE sha = ?", (sha,)).fetchone()
        return ChangeKind(row[0]) if row else None

    def commits_of_kind(self, kinds: Iterable[ChangeKind]) -> list[str]:
        names = [str(kind) for kind in kinds]
        marks = ",".join("?" * len(names))
        rows = self._db.execute(
            f"SELECT sha FROM commit_class WHERE kind IN ({marks}) ORDER BY sha", names
        )
        return [row[0] for row in rows]

    def class_counts(self) -> dict[str, int]:
        rows = self._db.execute("SELECT kind, count(*) FROM commit_class GROUP BY kind")
        return dict(rows.fetchall())

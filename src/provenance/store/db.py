"""SQLite access. Each repo has one database file."""

import sqlite3
from collections.abc import Iterable, Iterator
from importlib import resources
from pathlib import Path

from provenance.gitio import CommitRecord, FileChange
from provenance.model import ChangeKind


class Store:
    def __init__(self, path: Path, *, shared: bool = False):
        """`shared` allows use from several threads, one at a time under the caller's lock."""
        path.parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(path, check_same_thread=not shared)
        self._db.execute("PRAGMA busy_timeout=10000")  # a crawler may be writing at the same time
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute("PRAGMA synchronous=NORMAL")
        schema = resources.files("provenance.store").joinpath("schema.sql").read_text()
        self._db.executescript(schema)
        self._migrate()

    def _migrate(self) -> None:
        """Add columns that newer versions need to databases made by older ones."""
        columns = {row[1] for row in self._db.execute("PRAGMA table_info(artefacts)")}
        if "created_at" not in columns:
            self._db.execute("ALTER TABLE artefacts ADD COLUMN created_at INTEGER")
        if "created_estimated" not in columns:
            self._db.execute(
                "ALTER TABLE artefacts ADD COLUMN created_estimated INTEGER NOT NULL DEFAULT 0"
            )
        self._db.commit()

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

    def body(self, sha: str) -> str:
        row = self._db.execute("SELECT body FROM commits WHERE sha = ?", (sha,)).fetchone()
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

    def messages(self) -> Iterator[tuple[str, str, str]]:
        yield from self._db.execute("SELECT sha, subject, body FROM commits")

    def replace_edges(self, origin: str, version: int, edges: Iterable[tuple]) -> int:
        """Swap every edge from one origin for a fresh set of (src, dst, type, conf, evidence)."""
        self._db.execute("DELETE FROM edges WHERE origin = ?", (origin,))
        rows = [(*edge, origin, version) for edge in edges]
        self._db.executemany("INSERT OR IGNORE INTO edges VALUES (?, ?, ?, ?, ?, ?, ?)", rows)
        self._db.commit()
        return self._db.execute(
            "SELECT count(*) FROM edges WHERE origin = ?", (origin,)
        ).fetchone()[0]

    def edges_of(self, node: str) -> list[tuple[str, str, str, float, str]]:
        """Edges leaving or entering a node, as (src, dst, type, confidence, evidence)."""
        rows = self._db.execute(
            """SELECT src, dst, type, confidence, evidence FROM edges WHERE src = ?
               UNION SELECT src, dst, type, confidence, evidence FROM edges WHERE dst = ?""",
            (node, node),
        )
        return rows.fetchall()

    def edge_counts(self) -> dict[str, int]:
        return dict(self._db.execute("SELECT type, count(*) FROM edges GROUP BY type").fetchall())

    def has_artefact(self, node: str) -> bool:
        return (
            self._db.execute("SELECT 1 FROM artefacts WHERE id = ?", (node,)).fetchone() is not None
        )

    def add_artefact(
        self,
        node: str,
        kind: str,
        title: str,
        body: str,
        state: str,
        url: str,
        raw: str,
        created_at: int | None = None,
        *,
        commit: bool = True,
    ) -> None:
        """Insert or update an artefact.

        An upsert, not INSERT OR REPLACE: a replace deletes the old row without firing the
        delete trigger, which would leave a stale entry in the search index.
        """
        self._db.execute(
            """INSERT INTO artefacts
                 (id, kind, title, body, state, url, raw, fetched_at, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, strftime('%s','now'), ?)
               ON CONFLICT(id) DO UPDATE SET
                 kind = excluded.kind, title = excluded.title, body = excluded.body,
                 state = excluded.state, url = excluded.url, raw = excluded.raw,
                 fetched_at = excluded.fetched_at,
                 created_at = coalesce(excluded.created_at, artefacts.created_at),
                 created_estimated = CASE WHEN excluded.created_at IS NULL
                                          THEN artefacts.created_estimated ELSE 0 END""",
            (node, kind, title, body, state, url, raw, created_at),
        )
        if commit:
            self._db.commit()

    def set_created(self, rows: Iterable[tuple[str, int]], *, estimated: bool) -> int:
        """Store creation times. An estimate never overwrites a known (exact) time."""
        guard = "AND (created_at IS NULL OR created_estimated = 1)" if estimated else ""
        cursor = self._db.executemany(
            f"UPDATE artefacts SET created_at = ?, created_estimated = ? WHERE id = ? {guard}",
            [(when, int(estimated), node) for node, when in rows],
        )
        self._db.commit()
        return cursor.rowcount

    def created_at(self, node: str) -> tuple[int | None, bool]:
        row = self._db.execute(
            "SELECT created_at, created_estimated FROM artefacts WHERE id = ?", (node,)
        ).fetchone()
        return (row[0], bool(row[1])) if row else (None, False)

    def artefact(self, node: str) -> dict | None:
        row = self._db.execute(
            "SELECT kind, title, body, state, url FROM artefacts WHERE id = ?", (node,)
        ).fetchone()
        if row is None or row[3] == "missing":
            return None
        return dict(zip(("kind", "title", "body", "state", "url"), row, strict=True))

    def linked_numbers(self, prefix: str) -> list[int]:
        """Numbers of nodes like `ticket:django/` that commits link to, newest commits first."""
        rows = self._db.execute(
            """SELECT e.dst, max(c.commit_time) AS latest FROM edges e
               JOIN commits c ON e.src = 'commit:' || c.sha
               WHERE e.dst LIKE ? GROUP BY e.dst ORDER BY latest DESC""",
            (prefix + "%",),
        )
        return [int(dst.rpartition("/")[2]) for dst, _latest in rows]

    def add_edges(self, origin: str, version: int, edges: Iterable[tuple]) -> None:
        """Add edges of (src, dst, type, conf, evidence) without removing existing ones."""
        rows = [(*edge, origin, version) for edge in edges]
        self._db.executemany("INSERT OR IGNORE INTO edges VALUES (?, ?, ?, ?, ?, ?, ?)", rows)
        self._db.commit()

    def search_artefacts(
        self,
        query: str,
        limit: int = 20,
        *,
        before: int | None = None,
        any_word: bool = False,
        exclude: Iterable[str] = (),
    ) -> list[dict]:
        """Full-text search over fetched tickets and pull requests, best match first.

        The query is plain words. Each word is quoted before it reaches FTS5, so punctuation
        like `make_password()` can't change the query's meaning. By default every word must
        match; `any_word` ranks artefacts that match any of them (BM25 does the weighting).
        `before` keeps only artefacts created before that Unix time; an artefact with no
        known date is then left out, because it can't be shown to come first.
        """
        words = [word.replace('"', '""') for word in query.split()]
        if not words:
            return []
        self._sync_search()
        joiner = " OR " if any_word else " "
        conditions = ["artefacts_fts MATCH ?", "a.state != 'missing'"]
        params: list = [joiner.join(f'"{word}"' for word in words)]
        if before is not None:
            conditions.append("a.created_at IS NOT NULL AND a.created_at < ?")
            params.append(before)
        excluded = list(exclude)
        if excluded:
            conditions.append(f"a.id NOT IN ({', '.join('?' * len(excluded))})")
            params.extend(excluded)
        rows = self._db.execute(
            f"""SELECT a.id, a.kind, a.title, a.state, a.url,
                      snippet(artefacts_fts, 1, '[', ']', ' … ', 24),
                      bm25(artefacts_fts), a.created_at, a.created_estimated
               FROM artefacts_fts JOIN artefacts a ON a.rowid = artefacts_fts.rowid
               WHERE {" AND ".join(conditions)}
               ORDER BY rank LIMIT ?""",
            (*params, limit),
        )
        keys = ("id", "kind", "title", "state", "url", "snippet", "score", "created_at")
        return [
            dict(zip(keys, row[:8], strict=True)) | {"created_estimated": bool(row[8])}
            for row in rows
        ]

    def _sync_search(self) -> None:
        """Backfill the search index for rows stored before the triggers existed.

        `count(*)` on an external-content FTS table reads the content table, so the real
        index size comes from FTS5's own per-document table.
        """
        (indexed,) = self._db.execute("SELECT count(*) FROM artefacts_fts_docsize").fetchone()
        (stored,) = self._db.execute("SELECT count(*) FROM artefacts").fetchone()
        if indexed != stored:
            self.rebuild_search()

    def rebuild_search(self) -> None:
        self._db.execute("INSERT INTO artefacts_fts(artefacts_fts) VALUES ('rebuild')")
        self._db.commit()

    def cached_reply(self, key: str) -> str | None:
        row = self._db.execute("SELECT reply FROM llm_cache WHERE key = ?", (key,)).fetchone()
        return row[0] if row else None

    def save_reply(self, key: str, model: str, prompt: str, reply: str) -> None:
        self._db.execute(
            "INSERT OR REPLACE INTO llm_cache VALUES (?, ?, ?, ?, strftime('%s','now'))",
            (key, model, prompt, reply),
        )
        self._db.commit()

    def crawl_state(self, key: str) -> tuple[str | None, int, bool]:
        """The saved cursor, pages fetched so far, and whether the crawl finished."""
        row = self._db.execute(
            "SELECT cursor, pages, done FROM crawl_state WHERE key = ?", (key,)
        ).fetchone()
        return (row[0], row[1], bool(row[2])) if row else (None, 0, False)

    def save_crawl_state(self, key: str, cursor: str | None, pages: int, done: bool) -> None:
        self._db.execute(
            "INSERT OR REPLACE INTO crawl_state VALUES (?, ?, ?, ?)",
            (key, cursor, pages, int(done)),
        )
        self._db.commit()

"""What the evidence crawls added: stored discussions, and how many commits now lead to one.

A commit "has a discussion" when an edge links it to a stored ticket, pull request or issue.
`before_crawl` counts only links parsed from commit messages to discussions that are stored;
`after_crawl` adds the GitHub crawl's own links (merge commits and closing references).

Usage: uv run python eval/crawl_stats.py
"""

import json
from pathlib import Path

from provenance.config import Repo
from provenance.store.db import Store

RESULTS = Path(__file__).parent / "results"


def linked_commits(store: Store, origins: tuple[str, ...]) -> int:
    """Commits with an edge (of the given origins) to a stored, non-missing discussion."""
    marks = ", ".join("?" * len(origins))
    query = f"""
        SELECT count(DISTINCT c) FROM (
            SELECT e.src AS c, e.dst AS a FROM edges e WHERE e.src LIKE 'commit:%'
              AND e.origin IN ({marks})
            UNION ALL
            SELECT e.dst, e.src FROM edges e WHERE e.dst LIKE 'commit:%'
              AND e.origin IN ({marks})
        ) JOIN artefacts ON artefacts.id = a AND artefacts.state != 'missing'
    """
    return store._db.execute(query, (*origins, *origins)).fetchone()[0]


def stats(name: str) -> dict:
    with Store(Repo.named(name).db_path) as store:
        db = store._db
        commits = store.commit_count()
        kinds = dict(
            db.execute(
                "SELECT kind, count(*) FROM artefacts WHERE state != 'missing' GROUP BY kind"
            ).fetchall()
        )
        dated = db.execute(
            "SELECT created_estimated, count(*) FROM artefacts "
            "WHERE state != 'missing' AND created_at IS NOT NULL GROUP BY 1"
        ).fetchall()
        crawls = {
            key: {"pages": pages, "done": bool(done)}
            for key, _cursor, pages, done in db.execute("SELECT * FROM crawl_state").fetchall()
        }
        before = linked_commits(store, ("message",))
        after = linked_commits(store, ("message", "github"))
        return {
            "commits": commits,
            "discussions_stored": kinds,
            "dated": {"exact": dict(dated).get(0, 0), "estimated": dict(dated).get(1, 0)},
            "crawls": crawls,
            "edges_from_github": dict(
                db.execute(
                    "SELECT type, count(*) FROM edges WHERE origin = 'github' GROUP BY type"
                ).fetchall()
            ),
            "commits_with_discussion": {
                "before_crawl": before,
                "after_crawl": after,
                "share_before": before / commits,
                "share_after": after / commits,
            },
        }


def main() -> None:
    report = {name: stats(name) for name in ("django", "redis", "react")}
    (RESULTS / "crawl_stats.json").write_text(json.dumps(report, indent=2) + "\n")
    for name, s in report.items():
        c = s["commits_with_discussion"]
        stored = sum(s["discussions_stored"].values())
        print(
            f"{name:7} {s['commits']:6} commits  discussions {stored:6}"
            f"  linked commits {c['share_before']:.1%} -> {c['share_after']:.1%}"
        )


if __name__ == "__main__":
    main()

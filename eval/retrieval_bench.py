"""RQ2: when a commit's link to its ticket is missing, can search find the ticket anyway?

Items are Django commits whose message says `Fixed #N`, where ticket N is stored and dated. For
each, the link is hidden and the ticket has to be found again among every stored ticket.

Leakage rules (plans/02-research-and-evaluation.md, section 4):

- Every reference (`#N`, `Fixed #N`, `Refs #N`) is stripped from the query, and so are
  ticket numbers.
- Search never uses edges, so the hidden link can't leak through the graph.
- Only tickets created before the commit are candidates (the time rule). Ticket dates are
  interpolated from exact anchors (`date-tickets`), so the estimate's error is reported.
- Two difficulty levels: A shows the commit message minus references; B hides the message
  completely, leaving only the code the commit added and the files it touched.

Methods:

- `message`: keywords from the message (level A only). This is the plain keyword baseline.
- `path`: keywords from the touched file paths (level B baseline).
- `code`: keywords from the added lines of code.
- `ours`: message then code at level A, or code plus path at level B. This is what
  find_discussions does when no link exists.

Metrics: Recall@1, @5 and @10, and MRR, with 95% bootstrap intervals.

Usage: uv run python eval/retrieval_bench.py [--items 1000] [--dev]

`--dev` runs the 50 development items, the only ones the query design was ever tuned on.
The final run samples from the rest.
"""

import argparse
import json
import random
import statistics
from pathlib import Path

from provenance.config import Repo
from provenance.gitio import git
from provenance.retrieve import query_terms
from provenance.store.db import Store
from provenance.trace.tokens import language_for

RESULTS = Path(__file__).parent / "results"
SEED = 29
#: Items the query design was shaped on: the first 50 looked at (seed 29) and the 50 the
#: message-first order was then checked on (seed 30). The final run never includes them.
DEV_SEEDS = (29, 30)
DEV_ITEMS = 50
DEPTH = 10
MAX_ADDED_LINES = 60
BOOTSTRAPS = 2000


def candidates(store: Store) -> list[tuple[str, list[str]]]:
    """(commit sha, target tickets) for commits that close stored, dated tickets."""
    rows = store._db.execute(
        """SELECT e.src, e.dst FROM edges e JOIN artefacts a ON a.id = e.dst
           WHERE e.type = 'closes' AND e.origin = 'message' AND e.dst LIKE 'ticket:django/%'
             AND a.state != 'missing' AND a.created_at IS NOT NULL"""
    ).fetchall()
    targets: dict[str, list[str]] = {}
    for src, dst in rows:
        targets.setdefault(src.removeprefix("commit:"), []).append(dst)
    return sorted(targets.items())


def added_code(repo: Repo, sha: str) -> tuple[str, list[str]]:
    """The code lines a commit added (source files only), and the paths it touched."""
    diff = git(repo.git_dir, "show", "--format=", "-U0", "--no-color", "--no-renames", sha)
    lines, paths, current = [], [], None
    for row in diff.splitlines():
        if row.startswith("+++ b/"):
            current = row[6:]
            if language_for(current):
                paths.append(current)
            continue
        if (
            row.startswith("+")
            and not row.startswith("+++")
            and current
            and language_for(current)
            and len(lines) < MAX_ADDED_LINES
        ):
            lines.append(row[1:])
    return "\n".join(lines), paths


def rank(store: Store, terms: list[str], before: int, targets: list[str]) -> int | None:
    """1-based rank of the first target in the top DEPTH results, or None."""
    if not terms:
        return None
    hits = store.search_artefacts(" ".join(terms), DEPTH, before=before, any_word=True)
    for position, hit in enumerate(hits, start=1):
        if hit["id"] in targets:
            return position
    return None


def metrics(ranks: list[int | None]) -> dict:
    def summarise(sample: list[int | None]) -> dict:
        n = len(sample)
        return {
            "recall@1": sum(1 for r in sample if r is not None and r <= 1) / n,
            "recall@5": sum(1 for r in sample if r is not None and r <= 5) / n,
            "recall@10": sum(1 for r in sample if r is not None and r <= 10) / n,
            "mrr": sum(1 / r for r in sample if r is not None) / n,
        }

    point = summarise(ranks)
    rng = random.Random(SEED)
    boots = [summarise([rng.choice(ranks) for _ in ranks]) for _ in range(BOOTSTRAPS)]
    for key in list(point):
        values = sorted(b[key] for b in boots)
        point[f"{key}_ci"] = [values[int(0.025 * BOOTSTRAPS)], values[int(0.975 * BOOTSTRAPS)]]
    return point


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--items", type=int, default=1000)
    parser.add_argument(
        "--dev", action="store_true", help="run on the 50 development items only, no result file"
    )
    args = parser.parse_args()

    repo = Repo.named("django")
    with Store(repo.db_path) as store:
        pool = candidates(store)
        dev = [item for seed in DEV_SEEDS for item in random.Random(seed).sample(pool, DEV_ITEMS)]
        if args.dev:
            items = random.Random(DEV_SEEDS[-1]).sample(pool, DEV_ITEMS)
        else:
            test_pool = [item for item in pool if item not in dev]
            items = random.Random(SEED).sample(test_pool, min(args.items, len(test_pool)))
        runs = {
            "A": {"message": [], "code": [], "ours": []},
            "B": {"path": [], "code": [], "ours": []},
        }
        reachable = 0
        for number, (sha, targets) in enumerate(items, start=1):
            if number % 100 == 0:
                print(f"  {number}/{len(items)}", flush=True)
            when = store.commit_time(sha)
            # The time rule. Count how often the (estimated) ticket date even allows a hit.
            dates = [store.created_at(t)[0] for t in targets]
            reachable += any(d is not None and d < when for d in dates)
            message = f"{store.subject(sha)}\n\n{store.body(sha)}"
            code, paths = added_code(repo, sha)
            path_text = " ".join(paths)
            queries = {
                "A": {
                    "message": query_terms(message),
                    "code": query_terms(code),
                    "ours": query_terms(message, code, limit=32),
                },
                "B": {
                    "path": query_terms(path_text),
                    "code": query_terms(code),
                    "ours": query_terms(code, path_text, limit=32),
                },
            }
            for level, methods in queries.items():
                for method, terms in methods.items():
                    runs[level][method].append(rank(store, terms, when, targets))

    report = {
        "repo": "django",
        "items": len(items),
        "pool": len(pool),
        "seed": SEED,
        "dev_items_excluded": len({sha for sha, _ in dev}),
        "depth": DEPTH,
        "target_created_before_commit": reachable / len(items),
        "note": (
            "Ticket creation dates are interpolated between exactly dated anchors; "
            "target_created_before_commit is the share of items whose ticket passes the time "
            "rule at all, an upper bound on recall."
        ),
        "levels": {
            level: {method: metrics(ranks) for method, ranks in methods.items()}
            for level, methods in runs.items()
        },
        "median_rank_when_found": {
            level: {
                method: statistics.median([r for r in ranks if r] or [0])
                for method, ranks in methods.items()
            }
            for level, methods in runs.items()
        },
    }
    for level, methods in report["levels"].items():
        print(f"Level {level}")
        for method, m in methods.items():
            print(
                f"  {method:8} R@1 {m['recall@1']:.1%}  R@5 {m['recall@5']:.1%}  "
                f"R@10 {m['recall@10']:.1%}  MRR {m['mrr']:.3f}"
            )
    print(f"Ticket passes the time rule for {report['target_created_before_commit']:.1%} of items")
    if not args.dev:
        (RESULTS / "retrieval_bench.json").write_text(json.dumps(report, indent=2) + "\n")
        print("Saved to eval/results/retrieval_bench.json")


if __name__ == "__main__":
    main()

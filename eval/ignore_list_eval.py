"""Compare our automatic cosmetic-commit detection with a repo's hand-kept ignore list.

Usage: uv run python eval/ignore_list_eval.py django [--files 40] [--seed 7]

Results go to eval/results/, including the commit SHA, code version inputs and seed.
"""

import argparse
import json
import random
import time
from pathlib import Path

from check_listed import listed_commits

from provenance.config import Repo
from provenance.gitio import git
from provenance.model import CONTINUES_TRACING
from provenance.store.db import Store
from provenance.trace.blame import blame_file
from provenance.trace.classify import ALGO_VERSION, _is_non_code
from provenance.trace.tokens import language_for

RESULTS = Path(__file__).parent / "results"


def listed_commit_rows(store: Store, listed: list[str]) -> list[dict]:
    rows = []
    for sha in listed:
        changes = store.changes(sha)
        code = [c for c in changes if not _is_non_code(c.path)]
        skipped = sum(store.file_kind(sha, c.path) in CONTINUES_TRACING for c in code)
        kind = store.commit_kind(sha)
        rows.append(
            {
                "sha": sha,
                "subject": store.subject(sha),
                "kind": str(kind),
                "code_files": len(code),
                "non_logic_files": skipped,
            }
        )
    return rows


def sample_files(repo: Repo, rev: str, count: int, seed: int) -> list[str]:
    tree = git(repo.git_dir, "ls-tree", "-r", "--name-only", rev).splitlines()
    candidates = sorted(p for p in tree if p.startswith("django/") and language_for(p) == "python")
    return random.Random(seed).sample(candidates, min(count, len(candidates)))


def blame_effect(repo: Repo, store: Store, rev: str, paths: list[str], listed: set[str]) -> dict:
    totals = dict.fromkeys(
        ("lines", "strongest_on_listed", "hand_on_listed", "auto_on_listed", "auto_equals_hand"), 0
    )
    seconds = dict.fromkeys(("strongest", "hand", "auto"), 0.0)
    for path in paths:
        started = time.perf_counter()
        strongest = blame_file(repo.git_dir, path, rev)
        seconds["strongest"] += time.perf_counter() - started

        started = time.perf_counter()
        hand = blame_file(repo.git_dir, path, rev, ignore_revs=listed)
        seconds["hand"] += time.perf_counter() - started

        started = time.perf_counter()
        auto = blame_file(repo.git_dir, path, rev, ignore_revs=store.non_logic_commits(path))
        seconds["auto"] += time.perf_counter() - started

        totals["lines"] += len(strongest)
        totals["strongest_on_listed"] += sum(b.commit in listed for b in strongest)
        totals["hand_on_listed"] += sum(b.commit in listed for b in hand)
        totals["auto_on_listed"] += sum(b.commit in listed for b in auto)
        totals["auto_equals_hand"] += sum(
            a.commit == h.commit for a, h in zip(auto, hand, strict=True)
        )
    return {"totals": totals, "seconds": seconds}


def flagged_sample(store: Store, listed: set[str], seed: int, size: int = 40) -> dict:
    flagged = store.commits_of_kind(CONTINUES_TRACING)
    extra = sorted(set(flagged) - listed)
    chosen = random.Random(seed).sample(extra, min(size, len(extra)))
    return {
        "flagged_total": len(flagged),
        "flagged_not_on_list": len(extra),
        "review_sample": [
            {"sha": sha, "kind": str(store.commit_kind(sha)), "subject": store.subject(sha)}
            for sha in chosen
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo")
    parser.add_argument("--files", type=int, default=40)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    repo = Repo.named(args.repo)
    rev = git(repo.git_dir, "rev-parse", "HEAD").strip()
    listed = listed_commits(repo)
    with Store(repo.db_path) as store:
        rows = listed_commit_rows(store, listed)
        paths = sample_files(repo, rev, args.files, args.seed)
        result = {
            "repo": args.repo,
            "rev": rev,
            "seed": args.seed,
            "algo_version": ALGO_VERSION,
            "class_counts": store.class_counts(),
            "listed": rows,
            "sampled_files": paths,
            "blame_effect": blame_effect(repo, store, rev, paths, set(listed)),
            "flagged": flagged_sample(store, set(listed), args.seed),
        }

    RESULTS.mkdir(exist_ok=True)
    output = RESULTS / f"ignore_list_{args.repo}.json"
    output.write_text(json.dumps(result, indent=2) + "\n")

    with_code = [r for r in rows if r["code_files"]]
    full = sum(r["non_logic_files"] == r["code_files"] for r in with_code)
    print(f"Listed commits with code: {len(with_code)} of {len(rows)}")
    print(f"Fully non-logic: {full}")
    print(
        f"Files skipped: {sum(r['non_logic_files'] for r in with_code)}"
        f" of {sum(r['code_files'] for r in with_code)}"
    )
    for row in with_code:
        print(
            f"  {row['sha'][:10]} {row['kind']:9} {row['non_logic_files']:5}/"
            f"{row['code_files']:<5} {row['subject'][:60]}"
        )
    totals = result["blame_effect"]["totals"]
    lines = totals["lines"]
    print(f"\nSampled {len(paths)} files, {lines} lines. Share of lines on a listed commit:")
    for key in ("strongest_on_listed", "hand_on_listed", "auto_on_listed"):
        print(f"  {key:22} {totals[key] / lines:6.1%}")
    print(f"  auto agrees with hand list on {totals['auto_equals_hand'] / lines:.1%} of lines")
    print(f"  seconds: { {k: round(v, 1) for k, v in result['blame_effect']['seconds'].items()} }")
    flagged = result["flagged"]
    print(
        f"\nFlagged {flagged['flagged_total']} commits, "
        f"{flagged['flagged_not_on_list']} not on the list. Saved to {output}"
    )


if __name__ == "__main__":
    main()

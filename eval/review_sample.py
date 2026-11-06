"""Print compact diffs of a seeded sample of flagged commits, for review by hand.

Usage: uv run python eval/review_sample.py redis --cosmetic 40
"""

import argparse
import random
import sqlite3

from provenance.config import Repo
from provenance.gitio import git


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo")
    parser.add_argument("--cosmetic", type=int, default=40)
    parser.add_argument("--seed", type=int, default=11)
    parser.add_argument("--max-lines", type=int, default=6)
    args = parser.parse_args()
    repo = Repo.named(args.repo)
    db = sqlite3.connect(repo.db_path)
    query = "SELECT sha FROM commit_class WHERE kind = ? ORDER BY sha"
    renames = [row[0] for row in db.execute(query, ("rename",))]
    cosmetic = [row[0] for row in db.execute(query, ("cosmetic",))]
    picked = renames + random.Random(args.seed).sample(cosmetic, args.cosmetic)
    for sha in picked:
        kind = db.execute("SELECT kind FROM commit_class WHERE sha = ?", (sha,)).fetchone()[0]
        subject = db.execute("SELECT subject FROM commits WHERE sha = ?", (sha,)).fetchone()[0]
        print(f"=== {sha[:10]} {kind} {subject[:75]}")
        diff = git(repo.git_dir, "show", "--format=", "-U0", "--no-color", sha)
        shown = 0
        for row in diff.splitlines():
            if row[:1] in "+-" and not row.startswith(("+++", "---")) and row[1:].strip():
                print("  " + row[:105])
                shown += 1
                if shown == args.max_lines:
                    break


if __name__ == "__main__":
    main()

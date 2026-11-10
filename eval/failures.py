"""List every line a method got wrong, next to the label, to build the failure taxonomy.

Run eval/score_gold.py first. Usage: uv run python eval/failures.py [method ...]
"""

import csv
import json
import sys
from pathlib import Path

from provenance.config import Repo
from provenance.store.db import Store

HERE = Path(__file__).parent


def main(methods: list[str]) -> None:
    report = json.loads((HERE / "results" / "gold_scores.json").read_text())
    labels = {row["id"]: row for row in csv.DictReader((HERE / "gold" / "annotations.csv").open())}
    stores = {}
    for row in report["lines"]:
        label = labels[row["id"]]
        wrong = [m for m in methods if m in row and not row[m]]
        if not wrong:
            continue
        repo = row["repo"]
        if repo not in stores:
            stores[repo] = Store(Repo.named(repo).db_path)
        store = stores[repo]

        def describe(sha: str, store: Store = store) -> str:
            return f"{sha[:10]}  {store.subject(store.full_sha(sha))[:70]}" if sha else "(none)"

        print(f"{row['id']}  {repo}  {label['path']}:{label['line']}  wrong: {', '.join(wrong)}")
        print(f"    label  {describe(label['last_logic_change'])}")
        for method in wrong:
            print(f"    {method:6} {describe(row['answers'][method])}")
        if label["notes"]:
            print(f"    note   {label['notes']}")
    for store in stores.values():
        store.close()


if __name__ == "__main__":
    main(sys.argv[1:] or ["Ours-C", "Ours-A", "B2"])

"""Compare git blame flags for the tracer on the development set (the first 60 labelled lines).

These lines have been studied, so they are for choosing settings only. Final numbers must come
from the held-out test set.

Usage: uv run python eval/tune_flags.py
"""

import json
import time

from corpus import pinned_rev
from score_gold import GOLD, RESULTS, load_labels, same_commit, stratum_weights, weighted_accuracy

from provenance.config import Repo
from provenance.store.db import Store
from provenance.trace.chain import Tracer

VARIANTS = {
    "-w -M -C -C (current)": ("-w", "-M", "-C", "-C"),
    "-w -M -C": ("-w", "-M", "-C"),
    "-w -M": ("-w", "-M"),
    "-w": ("-w",),
    "-w -M60 -C60 -C60": ("-w", "-M60", "-C60", "-C60"),
}


def main() -> None:
    key = json.loads((GOLD / "sample_key.json").read_text())
    items = {item["id"]: item for item in key["items"]}
    labels = [r for r in load_labels(GOLD / "annotations.csv") if r["ambiguous"] != "yes"]
    weights = stratum_weights(key["meta"])
    report = {}
    for name, flags in VARIANTS.items():
        started = time.perf_counter()
        rows = []
        for repo_name in sorted({r["repo"] for r in labels}):
            repo = Repo.named(repo_name)
            with Store(repo.db_path) as store:
                tracer = Tracer(repo, store, flags)
                for label in (r for r in labels if r["repo"] == repo_name):
                    item = items[label["id"]]
                    chain = tracer.trace(item["path"], item["line"], pinned_rev(repo_name))
                    rows.append(
                        {
                            "id": label["id"],
                            "repo": repo_name,
                            "stratum": item["stratum"],
                            "last": same_commit(chain.origin or "", label["last_logic_change"]),
                            "first": same_commit(chain.first_seen or "", label["first_appearance"]),
                        }
                    )
        report[name] = {
            "last_weighted": weighted_accuracy(rows, "last", weights),
            "last_raw": sum(r["last"] for r in rows) / len(rows),
            "first_weighted": weighted_accuracy(rows, "first", weights),
            "wrong": sorted(r["id"] for r in rows if not r["last"]),
            "seconds": round(time.perf_counter() - started, 1),
        }
        result = report[name]
        print(
            f"{name:24} last {result['last_weighted']:.1%} (raw {result['last_raw']:.1%})  "
            f"first {result['first_weighted']:.1%}  {result['seconds']}s  "
            f"wrong {' '.join(result['wrong'])}",
            flush=True,
        )
    (RESULTS / "tune_flags.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()

"""Score every method against the hand-labelled lines.

Accuracy is weighted back to the real population, because the sample oversamples lines where
methods disagree. Reports confidence intervals, and McNemar's exact test against our method.

Usage: uv run python eval/score_gold.py [--second eval/gold/annotations_second.csv]
"""

import argparse
import csv
import json
import math
import random
from collections import Counter
from pathlib import Path

from corpus import Baselines, hand_list, pinned_rev

from provenance.config import Repo
from provenance.store.db import Store

GOLD = Path(__file__).parent / "gold"
RESULTS = Path(__file__).parent / "results"
MIN_SHA = 7
BOOTSTRAPS = 2000
SEED = 7


def same_commit(a: str, b: str) -> bool:
    a, b = a.strip().lower(), b.strip().lower()
    return len(a) >= MIN_SHA and len(b) >= MIN_SHA and (a.startswith(b) or b.startswith(a))


def load_labels(path: Path) -> list[dict]:
    with path.open(newline="") as handle:
        return [row for row in csv.DictReader(handle) if row["last_logic_change"].strip()]


def stratum_weights(meta: dict) -> dict[tuple[str, str], float]:
    """Each stratum's share of its repo's lines, with repos counted equally."""
    weights = {}
    for name, info in meta["repos"].items():
        for stratum, counts in info["strata"].items():
            weights[name, stratum] = counts["population"] / info["lines"] / len(meta["repos"])
    return weights


def weighted_accuracy(rows: list[dict], key: str, weights: dict) -> float | None:
    """Mean accuracy within each stratum, combined using the population weights."""
    total = used = 0.0
    for cell, weight in weights.items():
        members = [r for r in rows if (r["repo"], r["stratum"]) == cell]
        if members:
            total += weight * sum(r[key] for r in members) / len(members)
            used += weight
    return total / used if used else None


def bootstrap_interval(rows: list[dict], key: str, weights: dict) -> tuple[float, float]:
    rng = random.Random(SEED)
    scores = []
    for _ in range(BOOTSTRAPS):
        resample = [rng.choice(rows) for _ in rows]
        score = weighted_accuracy(resample, key, weights)
        if score is not None:
            scores.append(score)
    scores.sort()
    return scores[int(0.025 * len(scores))], scores[int(0.975 * len(scores)) - 1]


def mcnemar_exact(rows: list[dict], a: str, b: str) -> dict:
    only_a = sum(r[a] and not r[b] for r in rows)
    only_b = sum(r[b] and not r[a] for r in rows)
    n = only_a + only_b
    tail = sum(math.comb(n, k) for k in range(min(only_a, only_b) + 1)) / 2**n if n else 1.0
    return {"only_first": only_a, "only_second": only_b, "p": min(1.0, 2 * tail)}


def cohen_kappa(first: list[str], second: list[str]) -> float | None:
    n = len(first)
    if not n:
        return None
    observed = sum(a == b for a, b in zip(first, second, strict=True)) / n
    counts_a, counts_b = Counter(first), Counter(second)
    expected = sum(counts_a[k] * counts_b[k] for k in counts_a) / n**2
    return (observed - expected) / (1 - expected) if expected < 1 else None


def method_answers(items: list[dict], methods_for) -> None:
    for item in items:
        item["answers"] = methods_for(item)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels", type=Path, default=GOLD / "annotations.csv")
    parser.add_argument("--second", type=Path)
    args = parser.parse_args()

    key = json.loads((GOLD / "sample_key.json").read_text())
    by_id = {item["id"]: item for item in key["items"]}
    labelled = [
        r for r in load_labels(args.labels) if r["ambiguous"].strip().lower() not in ("y", "yes")
    ]
    ambiguous = sum(
        1 for r in load_labels(args.labels) if r["ambiguous"].strip().lower() in ("y", "yes")
    )
    print(f"{len(labelled)} labelled lines, {ambiguous} ambiguous, of {len(by_id)}")
    if not labelled:
        print("Nothing to score yet.")
        return

    rows = []
    for name in sorted({r["repo"] for r in labelled}):
        repo = Repo.named(name)
        rev = pinned_rev(name)
        with Store(repo.db_path) as store:
            baselines = Baselines(repo, store, rev, hand_list(repo, rev))
            for label in (r for r in labelled if r["repo"] == name):
                item = by_id[label["id"]]
                blamed = baselines.blame_all(item["path"])
                row = {"repo": name, "stratum": item["stratum"]}
                for method, lines in blamed.items():
                    commit = lines[item["line"] - 1].commit
                    row[method] = same_commit(commit, label["last_logic_change"])
                rows.append(row)

    methods = [m for m in ("B0", "B1", "B2", "B3", "Ours-A") if all(m in r for r in rows)]
    weights = stratum_weights(key["meta"])
    report: dict = {"labelled": len(rows), "ambiguous": ambiguous, "methods": {}}
    print(f"\n{'Method':8} {'Weighted':>9} {'95% CI':>17} {'Raw':>7}  vs Ours-A")
    for method in methods:
        score = weighted_accuracy(rows, method, weights)
        low, high = bootstrap_interval(rows, method, weights)
        raw = sum(r[method] for r in rows) / len(rows)
        versus = mcnemar_exact(rows, method, "Ours-A")
        report["methods"][method] = {
            "weighted": score,
            "ci": [low, high],
            "raw": raw,
            "vs_ours_a": versus,
        }
        print(f"{method:8} {score:9.1%} {low:8.1%} - {high:6.1%} {raw:7.1%}  p={versus['p']:.3f}")

    if args.second:
        first = {
            r["id"]: r["last_logic_change"].strip().lower()[:MIN_SHA]
            for r in load_labels(args.labels)
        }
        second = {
            r["id"]: r["last_logic_change"].strip().lower()[:MIN_SHA]
            for r in load_labels(args.second)
        }
        shared = sorted(set(first) & set(second))
        kappa = cohen_kappa([first[i] for i in shared], [second[i] for i in shared])
        agreement = sum(first[i] == second[i] for i in shared) / len(shared) if shared else None
        report["agreement"] = {"lines": len(shared), "percent": agreement, "kappa": kappa}
        print(f"\nAnnotator agreement on {len(shared)} lines: {agreement}, kappa {kappa}")

    (RESULTS / "gold_scores.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()

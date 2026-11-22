"""RQ4: does the protective-code check flag the removals that later had to be undone?

Events come from eval/mine_guards.py (eval/data/guard_events.jsonl). A positive is a guard
removal that was reverted, or restored by a fix within the window; a negative is a removal
that stayed removed for a year. Bulk deletions (over 50 guards in one commit) are left out.

Each sampled removal is scored exactly as `whyblame check` would have scored it at the time:
the guard's history is traced at the removing commit's parent, so nothing later is seen.

Positives are rare, so the classes are sampled separately (all positives up to a cap, and an
equal cap of negatives). True and false positive rates are measured on each, and precision
is then re-weighted to the real share of positives among all labelled removals. Precision
on a balanced sample would flatter the check, so the re-weighted figure is the one reported,
next to the base rate.

Usage:
  uv run python eval/protect_bench.py --split tune   # choose the threshold (events before 2020)
  uv run python eval/protect_bench.py --split test   # the held-out run, frozen threshold
"""

import argparse
import json
import random
import re
from collections import Counter
from pathlib import Path

from provenance.config import Repo
from provenance.protect.score import DEFAULT_THRESHOLD, score_guard, with_context
from provenance.store.db import Store
from provenance.trace.chain import Tracer

HERE = Path(__file__).parent
EVENTS = HERE / "data" / "guard_events.jsonl"
SEED = 41
CAP = 250
WINDOW = "90"  # the primary window; 30 and 180 are reported too
THRESHOLDS = [round(0.05 * i, 2) for i in range(1, 20)]
#: The keyword baseline: a removal is flagged when the guard's own code mentions these.
_KEYWORDS = re.compile(
    r"permission|auth|secur|valid|invalid|forbid|denied|overflow|null|NULL|lock|timeout|"
    r"limit|max|bound|range|size|len",
    re.I,
)


def load(split: str) -> list[dict]:
    events = []
    with EVENTS.open() as handle:
        for line in handle:
            event = json.loads(line)
            if event["split"] == split and not event["bulk"]:
                events.append(event)
    return events


def score_events(events: list[dict], removed_in_commit: dict[str, int]) -> list[float]:
    """The score each removal would have got at the time it was made (history + context)."""
    scores = []
    stores = {name: Store(Repo.named(name).db_path) for name in {e["repo"] for e in events}}
    tracers = {name: Tracer(Repo.named(name), store) for name, store in stores.items()}
    for number, event in enumerate(events, start=1):
        if number % 25 == 0:
            print(f"  scored {number}/{len(events)}", flush=True)
        store = stores[event["repo"]]
        parents = store.parents(event["sha"])
        if not parents:
            scores.append(0.0)
            continue
        history = score_guard(
            tracers[event["repo"]],
            store,
            event["path"],
            event["line"],
            parents[0],
            now=event["time"],
        )
        scores.append(with_context(history.score, removed_in_commit[event["sha"]])[0])
    for store in stores.values():
        store.close()
    return scores


def rates(labels: list[int], flagged: list[bool]) -> tuple[float, float]:
    """(true positive rate, false positive rate)."""
    pos = [f for y, f in zip(labels, flagged, strict=True) if y == 1]
    neg = [f for y, f in zip(labels, flagged, strict=True) if y == 0]
    return (sum(pos) / len(pos) if pos else 0.0, sum(neg) / len(neg) if neg else 0.0)


def natural(tpr: float, fpr: float, n_pos: int, n_neg: int) -> dict:
    """Precision, recall and F scores re-weighted to the real class balance."""
    tp, fp = tpr * n_pos, fpr * n_neg
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tpr

    def f(beta: float) -> float:
        b2 = beta * beta
        denominator = b2 * precision + recall
        return (1 + b2) * precision * recall / denominator if denominator else 0.0

    return {"precision": precision, "recall": recall, "f1": f(1), "f0.5": f(0.5), "fpr": fpr}


def average_precision(labels, scores, n_pos, n_neg) -> float:
    """Area under the precision-recall curve, with precision re-weighted to the real balance."""
    points = sorted(set(scores), reverse=True)
    area, last_recall = 0.0, 0.0
    for threshold in points:
        tpr, fpr = rates(labels, [s >= threshold for s in scores])
        p = natural(tpr, fpr, n_pos, n_neg)["precision"]
        area += (tpr - last_recall) * p
        last_recall = tpr
    return area


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=("tune", "test"), required=True)
    args = parser.parse_args()

    events = load(args.split)
    labelled = [e for e in events if e["label"][WINDOW] is not None]
    pos = [e for e in labelled if e["label"][WINDOW] == 1]
    neg = [e for e in labelled if e["label"][WINDOW] == 0]
    n_pos, n_neg = len(pos), len(neg)
    print(
        f"{args.split}: {len(events)} removals, {n_pos} positive and {n_neg} negative "
        f"at {WINDOW} days (base rate {n_pos / (n_pos + n_neg):.1%})"
    )
    rng = random.Random(SEED)
    sample = rng.sample(pos, min(CAP, n_pos)) + rng.sample(neg, min(CAP, n_neg))
    labels = [e["label"][WINDOW] for e in sample]
    removed_in_commit = Counter(e["sha"] for e in events)
    scores = score_events(sample, removed_in_commit)

    curve = {}
    for threshold in THRESHOLDS:
        tpr, fpr = rates(labels, [s >= threshold for s in scores])
        curve[str(threshold)] = natural(tpr, fpr, n_pos, n_neg)
    keyword = rates(labels, [bool(_KEYWORDS.search(e["code"])) for e in sample])
    report = {
        "split": args.split,
        "window_days": int(WINDOW),
        "labelled_removals": {"positive": n_pos, "negative": n_neg},
        "base_rate": n_pos / (n_pos + n_neg),
        "sampled": {"positive": labels.count(1), "negative": labels.count(0)},
        "average_precision": average_precision(labels, scores, n_pos, n_neg),
        "curve": curve,
        "baselines": {
            "flag_every_removal": natural(1.0, 1.0, n_pos, n_neg),
            "keyword_rule": natural(*keyword, n_pos, n_neg),
        },
        "by_kind": dict(Counter(e["kind"] for e in sample)),
        "other_windows": {
            w: {
                "positive": sum(1 for e in events if e["label"][w] == 1),
                "negative": sum(1 for e in events if e["label"][w] == 0),
            }
            for w in ("30", "90", "180")
        },
        "scores": [
            {
                "repo": e["repo"],
                "sha": e["sha"][:10],
                "path": e["path"],
                "line": e["line"],
                "kind": e["kind"],
                "label": y,
                "score": s,
            }
            for e, y, s in zip(sample, labels, scores, strict=True)
        ],
    }
    if args.split == "tune":
        best = max(THRESHOLDS, key=lambda t: (curve[str(t)]["f0.5"], t))
        report["chosen_threshold"] = best
        report["rule"] = "the threshold with the highest F0.5 (precision-first), ties to the higher"
        out = HERE / "results" / "protect_threshold.json"
    else:
        report["frozen_threshold"] = DEFAULT_THRESHOLD
        report["at_threshold"] = curve.get(str(DEFAULT_THRESHOLD)) or natural(
            *rates(labels, [s >= DEFAULT_THRESHOLD for s in scores]), n_pos, n_neg
        )
        out = HERE / "results" / "protect_bench.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(
        f"base rate {report['base_rate']:.1%}  average precision {report['average_precision']:.3f}"
    )
    for name, m in report["baselines"].items():
        print(f"  {name:20} precision {m['precision']:.1%} recall {m['recall']:.1%}")
    key = report.get("chosen_threshold", DEFAULT_THRESHOLD)
    m = curve.get(str(key)) or report.get("at_threshold")
    print(f"  ours @ {key:<14} precision {m['precision']:.1%} recall {m['recall']:.1%}")
    print(f"Saved to {out}")


if __name__ == "__main__":
    main()

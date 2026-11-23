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

The held-out test split is small enough to score in full, so there it scores every labelled
removal and reports exact counts, per window (30, 90 and 180 days) and per repo, with
bootstrap intervals. Nothing is re-weighted.

Usage:
  uv run python eval/protect_bench.py --split tune   # choose the threshold (events before 2020)
  uv run python eval/protect_bench.py --split test   # the held-out run, frozen threshold
"""

import argparse
import json
import multiprocessing
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
WINDOWS = ("30", "90", "180")
BOOTSTRAPS = 2000
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


def _score_chunk(args: tuple[list[dict], dict[str, int]]) -> list[float]:
    return score_events(*args)


def score_all(events: list[dict], removed_in_commit: dict[str, int], workers: int) -> list[float]:
    """score_events over worker processes; the order of `events` is kept."""
    size = -(-len(events) // workers)
    chunks = [(events[i : i + size], removed_in_commit) for i in range(0, len(events), size)]
    with multiprocessing.get_context("spawn").Pool(workers) as pool:
        return [s for part in pool.map(_score_chunk, chunks) for s in part]


def confusion(labels: list[int], flagged: list[bool]) -> dict:
    """Exact counts and rates, no re-weighting: every labelled removal was scored."""
    tp = sum(1 for y, f in zip(labels, flagged, strict=True) if y and f)
    fp = sum(1 for y, f in zip(labels, flagged, strict=True) if not y and f)
    pos = labels.count(1)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / pos if pos else 0.0
    base = pos / len(labels) if labels else 0.0
    return {
        "flagged": tp + fp,
        "true_positives": tp,
        "positives": pos,
        "removals": len(labels),
        "precision": precision,
        "recall": recall,
        "fpr": fp / (len(labels) - pos) if len(labels) > pos else 0.0,
        "base_rate": base,
        "lift": precision / base if base else 0.0,
    }


def interval(labels, flagged, key: str, rng: random.Random) -> list[float]:
    """A 95% bootstrap interval for one confusion() figure."""
    pairs = list(zip(labels, flagged, strict=True))
    values = []
    for _ in range(BOOTSTRAPS):
        draw = [pairs[rng.randrange(len(pairs))] for _ in pairs]
        values.append(confusion([y for y, _ in draw], [f for _, f in draw])[key])
    values.sort()
    return [values[int(0.025 * BOOTSTRAPS)], values[int(0.975 * BOOTSTRAPS) - 1]]


def exact_ap(labels: list[int], scores: list[float]) -> float:
    """Area under the precision-recall curve, on the full (unsampled) set."""
    pos = labels.count(1)
    area, last_recall = 0.0, 0.0
    for threshold in sorted(set(scores), reverse=True):
        m = confusion(labels, [s >= threshold for s in scores])
        area += (m["recall"] - last_recall) * m["precision"]
        last_recall = m["recall"]
    return area if pos else 0.0


def test_report(events: list[dict], workers: int) -> dict:
    """The held-out run: every labelled removal of 2020 and later, at the frozen threshold."""
    labelled = [e for e in events if any(e["label"][w] is not None for w in WINDOWS)]
    print(f"test: scoring all {len(labelled)} labelled removals with {workers} workers")
    removed_in_commit = Counter(e["sha"] for e in events)
    scores = score_all(labelled, removed_in_commit, workers)
    keyword = [bool(_KEYWORDS.search(e["code"])) for e in labelled]
    rng = random.Random(SEED)

    def block(subset: list[int], window: str) -> dict:
        idx = [i for i in subset if labelled[i]["label"][window] is not None]
        labels = [labelled[i]["label"][window] for i in idx]
        ours = [scores[i] >= DEFAULT_THRESHOLD for i in idx]
        result = {
            "ours": confusion(labels, ours),
            "flag_every_removal": confusion(labels, [True] * len(idx)),
            "keyword_rule": confusion(labels, [keyword[i] for i in idx]),
            "average_precision": exact_ap(labels, [scores[i] for i in idx]),
        }
        result["ours"]["precision_ci95"] = interval(labels, ours, "precision", rng)
        result["ours"]["recall_ci95"] = interval(labels, ours, "recall", rng)
        return result

    every = list(range(len(labelled)))
    repos = sorted({e["repo"] for e in labelled})
    report = {
        "split": "test",
        "frozen_threshold": DEFAULT_THRESHOLD,
        "primary_window_days": int(WINDOW),
        "method": (
            "Every labelled removal in the test split is scored (no sampling), so precision, "
            "recall and the base rate are exact counts. 95% intervals are bootstrap "
            f"({BOOTSTRAPS} draws)."
        ),
        "windows": {w: block(every, w) for w in WINDOWS},
        "by_repo": {
            r: {w: block([i for i in every if labelled[i]["repo"] == r], w) for w in WINDOWS}
            for r in repos
        },
        "by_kind": dict(Counter(e["kind"] for e in labelled)),
        "score_distribution": dict(Counter(round(s, 2) for s in scores)),
        "flagged_removals": [
            {
                "repo": e["repo"],
                "sha": e["sha"][:10],
                "path": e["path"],
                "line": e["line"],
                "kind": e["kind"],
                "labels": e["label"],
                "score": s,
            }
            for e, s in zip(labelled, scores, strict=True)
            if s >= DEFAULT_THRESHOLD
        ],
    }
    for w in WINDOWS:
        m = report["windows"][w]["ours"]
        lo, hi = m["precision_ci95"]
        print(
            f"  {w:>3} days: base rate {m['base_rate']:.2%}  precision {m['precision']:.1%} "
            f"[{lo:.1%}, {hi:.1%}]  recall {m['recall']:.1%}  lift {m['lift']:.1f}x  "
            f"({m['true_positives']}/{m['flagged']} flagged, {m['positives']} positives)"
        )
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=("tune", "test"), required=True)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    events = load(args.split)
    if args.split == "test":
        report = test_report(events, args.workers)
        out = HERE / "results" / "protect_bench.json"
        out.write_text(json.dumps(report, indent=2) + "\n")
        print(f"Saved to {out}")
        return
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
    best = max(THRESHOLDS, key=lambda t: (curve[str(t)]["f0.5"], t))
    report["chosen_threshold"] = best
    report["rule"] = "the threshold with the highest F0.5 (precision-first), ties to the higher"
    out = HERE / "results" / "protect_threshold.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(
        f"base rate {report['base_rate']:.1%}  average precision {report['average_precision']:.3f}"
    )
    for name, m in report["baselines"].items():
        print(f"  {name:20} precision {m['precision']:.1%} recall {m['recall']:.1%}")
    m = curve[str(best)]
    print(f"  ours @ {best:<14} precision {m['precision']:.1%} recall {m['recall']:.1%}")
    print(f"Saved to {out}")


if __name__ == "__main__":
    main()

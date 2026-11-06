"""Measure how often methods give different answers, and test the full engine on real lines.

This needs no human labels, so it shows how much each method changes, but not which is right.
It also runs the full tracer on random lines, to catch crashes and measure speed.

Usage: uv run python eval/method_gap.py
"""

import json
import random
import statistics
import time
from collections import Counter
from pathlib import Path

from corpus import Baselines, hand_list, pinned_rev
from sample_lines import eligible_files

from provenance.config import Repo
from provenance.store.db import Store
from provenance.trace.chain import Tracer
from provenance.trace.lines import logic_lines
from provenance.trace.tokens import language_for

RESULTS = Path(__file__).parent / "results"
SEED = 13
FILES = 40
TRACED_LINES = 150


def compare(name: str) -> dict:
    repo = Repo.named(name)
    rev = pinned_rev(name)
    rng = random.Random(SEED)
    differs = Counter()
    all_lines = []
    with Store(repo.db_path) as store:
        baselines = Baselines(repo, store, rev, hand_list(repo, rev))
        for path in rng.sample(eligible_files(repo, rev, name), FILES):
            blamed = baselines.blame_all(path)
            source = "\n".join(line.text for line in blamed["B0"]).encode()
            for line in logic_lines(source, language_for(path)):
                index = line - 1
                differs["lines"] += 1
                all_lines.append((path, line))
                if blamed["B0"][index].commit != blamed["B2"][index].commit:
                    differs["B0_vs_B2"] += 1
                if blamed["B2"][index].commit != blamed["Ours-A"][index].commit:
                    differs["B2_vs_Ours-A"] += 1
                if "B3" in blamed:
                    if blamed["B3"][index].commit != blamed["Ours-A"][index].commit:
                        differs["B3_vs_Ours-A"] += 1

        tracer = Tracer(repo, store)
        stops = Counter()
        hops = []
        seconds = []
        changed = 0
        errors = []
        for path, line in rng.sample(all_lines, min(TRACED_LINES, len(all_lines))):
            started = time.perf_counter()
            try:
                chain = tracer.trace(path, line, rev)
            except Exception as error:  # a crash here is a finding, so record it and carry on
                errors.append(f"{path}:{line} {type(error).__name__}: {error}"[:200])
                continue
            seconds.append(time.perf_counter() - started)
            stops[chain.stop_reason] += 1
            hops.append(len(chain.hops))
            changed += chain.origin != chain.first_seen

    lines = differs["lines"]
    return {
        "rev": rev,
        "lines": lines,
        "share_B0_vs_B2": differs["B0_vs_B2"] / lines,
        "share_B2_vs_OursA": differs["B2_vs_Ours-A"] / lines,
        "share_B3_vs_OursA": differs["B3_vs_Ours-A"] / lines if "B3_vs_Ours-A" in differs else None,
        "trace": {
            "lines": len(seconds),
            "errors": errors,
            "stop_reasons": dict(stops),
            "mean_hops": statistics.mean(hops) if hops else None,
            "share_edited_after_first_seen": changed / len(seconds) if seconds else None,
            "seconds_median": statistics.median(seconds) if seconds else None,
            "seconds_p90": statistics.quantiles(seconds, n=10)[-1] if len(seconds) > 1 else None,
            "seconds_max": max(seconds) if seconds else None,
        },
    }


def main() -> None:
    report = {"seed": SEED, "files": FILES, "repos": {}}
    for name in ("django", "redis"):
        print(name, flush=True)
        report["repos"][name] = compare(name)
    (RESULTS / "method_gap.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

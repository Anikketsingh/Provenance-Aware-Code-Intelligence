"""Print a blind spot-check sheet for 10 RQ5 runs (seeded): task, original guards and diff.

The condition and the judge's answers are hidden, so Claude's labels are independent.
Labels go in eval/gold/agent_spot_checks.json as {"checks": {run: {"done", "preserved"}}}.

Usage: uv run python eval/agent_spot_sheet.py
"""

import json
import random
from pathlib import Path

RUNS = Path(__file__).parent / "results" / "agent_runs"
SEED = 71
N = 10

records = sorted((json.loads(p.read_text()) for p in RUNS.glob("*.json")), key=lambda r: r["run"])
sample = random.Random(SEED).sample(records, N)
for k, r in enumerate(sample, start=1):
    print(f"=== S{k:02d}")
    print("TASK:", r["task"])
    print("ORIGINAL CHECKS:")
    for g in r["guard_code"]:
        print("  -", g)
    print("DIFF:")
    print(r["diff"][:6000] or "(no change)")
    print()
KEY = {f"S{k:02d}": r["run"] for k, r in enumerate(sample, start=1)}
(RUNS.parent / "agent_spot_key.json").write_text(json.dumps(KEY, indent=2) + "\n")

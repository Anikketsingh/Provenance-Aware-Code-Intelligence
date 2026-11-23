"""Any model: summarise the compatibility runs in eval/compat/results.csv.

Each row is one client and model doing the make_password() task, with or without the
`whyblame init` rules (see eval/compat/README.md). The summary counts, per client and model
and per rules setting: connected, called a whyblame tool unprompted, and kept both guards.

Until the runs exist, compat.json says so (status "pending") and nothing is invented.

Usage: uv run python eval/compat_summary.py
"""

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
CSV = HERE / "compat" / "results.csv"
OUT = HERE / "results" / "compat.json"
LOCAL_HINTS = ("ollama", "lm studio", "lmstudio", "qwen", "llama", "gemma", "local")


def yes(value: str) -> bool:
    return value.strip().lower() in ("yes", "y", "true", "1")


def summarise() -> dict:
    if not CSV.exists():
        return {"status": "pending", "rows": 0, "note": "No compatibility runs recorded yet."}
    with CSV.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        return {"status": "pending", "rows": 0, "note": "No compatibility runs recorded yet."}

    table = defaultdict(dict)
    for row in rows:
        key = f"{row['client'].strip()} / {row['model'].strip()}"
        setting = "with_rules" if yes(row["rules"]) else "without_rules"
        table[key][setting] = {
            "connected": yes(row["connected"]),
            "called_tool": yes(row["called_tool"]),
            "kept_guards": row["kept_guards"].strip().lower(),
            "notes": row.get("notes", "").strip(),
            "date": row.get("date", ""),
        }

    def count(setting: str, field: str, value=True) -> int:
        return sum(1 for runs in table.values() if runs.get(setting, {}).get(field) == value)

    clients = sorted(table)
    local = [c for c in clients if any(h in c.lower() for h in LOCAL_HINTS)]
    report = {
        "status": "done",
        "rows": len(rows),
        "clients": len(clients),
        "local_model_clients": local,
        "table": dict(table),
        "totals": {
            setting: {
                "runs": sum(1 for runs in table.values() if setting in runs),
                "connected": count(setting, "connected"),
                "called_tool": count(setting, "called_tool"),
                "kept_guards": count(setting, "kept_guards", "yes"),
                "kept_guards_partly": count(setting, "kept_guards", "partly"),
            }
            for setting in ("without_rules", "with_rules")
        },
    }
    return report


def main() -> None:
    report = summarise()
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    if report["status"] == "pending":
        print("Compatibility runs: pending (eval/compat/results.csv has no rows yet).")
    else:
        for setting, t in report["totals"].items():
            print(
                f"{setting:13} {t['runs']} clients: connected {t['connected']}, "
                f"called a tool {t['called_tool']}, kept both guards {t['kept_guards']}"
            )
    print(f"Saved to {OUT}")


if __name__ == "__main__":
    main()

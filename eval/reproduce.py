"""One command that reproduces every number in the report.

    uv run python eval/reproduce.py           # rescore both gold sets, then print the table
    uv run python eval/reproduce.py --full    # also rerun the label-free checks (slow)
    uv run python eval/reproduce.py --table   # only rebuild the table from saved results

Each step is one of the evaluation scripts, run the way the report describes. The summary
table lands in eval/results/summary.md, and every figure in it comes from a JSON file that
the scripts save in eval/results/.
"""

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

HERE = Path(__file__).parent
RESULTS = HERE / "results"

METHOD_NAMES = {
    "B0": "git blame, no options",
    "B1": "git blame -w -M",
    "B2": "git blame -w -M -C -C (strongest)",
    "B2t": "git blame -w -M60 -C60 -C60 (our thresholds, no skip lists)",
    "B3": "Django's hand-kept skip list",
    "Ours-A": "Ours, layers A + B",
    "Ours-C": "Ours, full tracer",
}


def run(step: list[str]) -> None:
    print(f"\n=== {' '.join(step)}", flush=True)
    subprocess.run([sys.executable, *step], check=True, cwd=HERE.parent)


def load(name: str) -> dict | None:
    try:
        return json.loads((RESULTS / f"{name}.json").read_text())
    except (OSError, ValueError):
        return None


def pct(x: float | None) -> str:
    return f"{x * 100:.1f}%" if x is not None else "n/a"


def gold_table(title: str, data: dict, lines: list[str]) -> None:
    lines.append(f"## {title}")
    lines.append("")
    lines.append(
        f"{data['labelled']} labelled lines ({data['ambiguous']} ambiguous left out). "
        "Weighted accuracy maps the stratified sample back to the real mix of lines."
    )
    lines.append("")
    lines.append("| Method | Weighted accuracy | 95% CI | vs ours (McNemar p) |")
    lines.append("|---|---:|---|---|")
    for key, name in METHOD_NAMES.items():
        m = data["methods"].get(key)
        if not m:
            continue
        ci = f"{pct(m['ci'][0])}–{pct(m['ci'][1])}" if "ci" in m else ""
        versus = m.get("vs_ours_c", {})
        p = "" if key == "Ours-C" else f"{versus.get('p', float('nan')):.2g}"
        lines.append(f"| {name} | {pct(m['weighted'])} | {ci} | {p} |")
    first_ours = data["methods"].get("first:Ours-C", {}).get("weighted")
    first_b2 = data["methods"].get("first:B2", {}).get("weighted")
    if first_ours is not None:
        lines.append("")
        lines.append(f"First appearance: ours {pct(first_ours)}, git's strongest {pct(first_b2)}.")
    agreement = data.get("agreement")
    if agreement:
        lines.append(
            f"Annotator agreement before adjudication: {pct(agreement['percent'])} "
            f"(kappa {agreement['kappa']:.2f}) on {agreement['lines']} lines."
        )
    lines.append("")


def summarise() -> str:
    lines = [
        "# Results Summary",
        "",
        f"Generated {datetime.now(UTC).date().isoformat()} by `eval/reproduce.py`. "
        "Every number comes from a JSON file in `eval/results/`.",
        "",
    ]
    if test := load("gold_scores_test"):
        gold_table("Held-out test set (the headline result)", test, lines)
    if dev := load("gold_scores"):
        gold_table("Development set (the method was tuned on these lines)", dev, lines)
    lines.append("## Checks that need no labels")
    lines.append("")
    if gap := load("method_gap"):
        for name, repo in gap["repos"].items():
            lines.append(
                f"- {name}: our skip lists change git's best answer on "
                f"{pct(repo['share_B2_vs_OursA'])} of logic lines."
            )
    if hand := load("ignore_list_django"):
        totals = hand["blame_effect"]["totals"]
        lines.append(
            f"- Django's hand-kept list: {pct(totals['strongest_on_listed'] / totals['lines'])} "
            f"of lines land on a listed formatting commit under git's strongest settings, "
            f"{pct(totals['auto_on_listed'] / totals['lines'])} with our automatic list."
        )
    if ast := load("ast_oracle_django"):
        lines.append(
            f"- Python's own parser: {pct(ast['cosmetic_precision_imports_sorted'])} of changes "
            f"we call cosmetic keep the same syntax tree "
            f"({pct(ast['cosmetic_precision_strict'])} when import order counts)."
        )
    lines.append("")
    lines.append(
        "Labels are AI labels (Claude, checked blind by Gemini); see `eval/gold/RULES.md`."
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true", help="also rerun the label-free checks")
    parser.add_argument("--table", action="store_true", help="only rebuild the summary table")
    args = parser.parse_args()

    if not args.table:
        run(["eval/score_gold.py", "--set", "dev", "--second", "eval/gold/annotations_gemini.csv"])
        run(
            ["eval/score_gold.py", "--set", "test"]
            + ["--second", "eval/gold/test/annotations_gemini.csv"]
        )
        if args.full:
            run(["eval/ignore_list_eval.py", "django"])
            run(["eval/ast_oracle.py", "django"])
            run(["eval/method_gap.py"])

    summary = summarise()
    (RESULTS / "summary.md").write_text(summary)
    print(f"\n{summary}")
    print(f"Saved to {RESULTS / 'summary.md'}")


if __name__ == "__main__":
    main()

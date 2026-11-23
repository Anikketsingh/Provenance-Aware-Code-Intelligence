"""One command that reproduces every number in the report.

    uv run python eval/reproduce.py              # rescore everything that scores offline
    uv run python eval/reproduce.py --full       # also rerun the label-free checks, RQ2, RQ4
    uv run python eval/reproduce.py --footprint  # also remeasure RQ6 (idle machine, ~1 hour)
    uv run python eval/reproduce.py --table      # only rebuild the table from saved results

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
    rq_sections(lines)
    lines.append(
        "Labels are AI labels (Claude, checked blind by Gemini); see `eval/gold/RULES.md`."
    )
    return "\n".join(lines) + "\n"


def rq_sections(lines: list[str]) -> None:
    """RQ2 to RQ6 and the any-model results, each only when its result file exists."""
    if rq2 := load("retrieval_bench"):
        lines += [
            "## RQ2: finding the discussion when the link is missing",
            "",
            f"{rq2['items']} Django commits whose `Fixed #N` link was hidden, searched among "
            "every earlier ticket. Level A shows the commit message without references; "
            "level B hides the message and keeps only the code and paths.",
            "",
            "| Level | Method | Recall@1 | Recall@5 | Recall@10 | MRR |",
            "|---|---|---:|---:|---:|---:|",
        ]
        names = {"message": "keywords from the message", "path": "keywords from the paths",
                 "code": "keywords from the added code", "ours": "ours"}  # fmt: skip
        for level, methods in rq2["levels"].items():
            for method, m in methods.items():
                lines.append(
                    f"| {level} | {names.get(method, method)} | {pct(m['recall@1'])} | "
                    f"{pct(m['recall@5'])} | {pct(m['recall@10'])} | {m['mrr']:.3f} |"
                )
        lines += [
            "",
            f"The ticket passes the time rule for {pct(rq2['target_created_before_commit'])} "
            "of items, an upper bound on recall.",
            "",
        ]
    if rq3 := load("explain_bench"):
        a, u, c, g = rq3["answerable"], rq3["unanswerable"], rq3["claims"], rq3["agreement"]
        q = rq3["questions"]
        lines += [
            "## RQ3: are explanations correct, and do they abstain when they should?",
            "",
            f"{q['answerable']} answerable and {q['unanswerable']} unanswerable questions "
            f"(Django, Redis, React). Explainer `{rq3['explainer_model']}`; judge "
            f"`{rq3['judge_model']}` plus Claude's independent labels.",
            "",
            f"- Answered {a['answered']} of {q['answerable']} answerable questions; "
            f"{a['correct']} correct, {a['partly']} partly, {a['wrong']} wrong "
            f"({pct(a['accuracy_when_answered'])} correct when answered).",
            f"- Of the {a['abstained']} abstentions on answerable questions, "
            f"{a['abstentions_justified']} were justified (the evidence did not explain the "
            f"line) and {a['false_abstentions']} were over-cautious.",
            f"- Abstained on {u['abstained']} of {q['unanswerable']} unanswerable questions "
            f"({pct(u['abstention_rate'])}).",
            f"- Claims supported by the cited evidence: {c['supported']} of {c['total']} "
            f"({pct(c['citation_correctness'])}).",
            f"- Judge vs Claude: {pct(g['claim_agreement'])} of claims and "
            f"{pct(g['verdict_agreement'])} of verdicts agree (verdict kappa "
            f"{g['verdict_kappa']:.2f}).",
            "",
            "| Repo | Answerable | Answered | Correct |",
            "|---|---:|---:|---:|",
        ]
        for repo, r in a["by_repo"].items():
            lines.append(f"| {repo} | {r['questions']} | {r['answered']} | {r['correct']} |")
        lines.append("")
    if rq4 := load("protect_bench"):
        lines += [
            "## RQ4: does the CI check flag removals that were later undone?",
            "",
            f"Every labelled guard removal from 2020 on (the held-out split), at the threshold "
            f"frozen on earlier removals ({rq4['frozen_threshold']}). Exact counts, no sampling.",
            "",
            "| Window | Removals | Base rate | Precision (95% CI) | Recall | Lift | "
            "Flag every removal | Keyword rule |",
            "|---|---:|---:|---|---:|---:|---:|---:|",
        ]
        for window, w in rq4["windows"].items():
            m = w["ours"]
            lo, hi = m["precision_ci95"]
            lines.append(
                f"| {window} days | {m['removals']} | {pct(m['base_rate'])} | "
                f"{pct(m['precision'])} ({pct(lo)}–{pct(hi)}) | {pct(m['recall'])} "
                f"({m['true_positives']}/{m['positives']}) | {m['lift']:.1f}× | "
                f"{pct(w['flag_every_removal']['precision'])} | "
                f"{pct(w['keyword_rule']['precision'])} |"
            )
        lines += ["", "Per repo, 90-day window:", ""]
        for repo, windows in rq4["by_repo"].items():
            m = windows["90"]["ours"]
            lines.append(
                f"- {repo}: base rate {pct(m['base_rate'])}, precision {pct(m['precision'])} "
                f"({m['true_positives']} of {m['flagged']} flagged), recall {pct(m['recall'])} "
                f"of {m['positives']} positives."
            )
        lines.append("")
    if rq5 := load("agent_pilot"):
        c, t = rq5["control"], rq5["treatment"]
        mk, mp = rq5["guard_kept_mcnemar"], rq5["protection_kept_mcnemar"]
        lines += [
            "## RQ5: do agents with the tool make fewer unsafe edits? (pilot)",
            "",
            f"{rq5['cases']} historical guard removals that were later undone, "
            f"{len(rq5['seeds'])} seeds, agent `{rq5['agent_model']}`, judge "
            f"`{rq5['judge_model']}`.",
            "",
            "| Condition | Runs | Guard kept as written | Protection kept | Task done | "
            "Both kept and done | Called why_line | Called check_change |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
        for name, s in (("Without whyblame", c), ("With whyblame", t)):
            lines.append(
                f"| {name} | {s['runs']} | {s['guard_kept']} | {s['protection_kept']} | "
                f"{s['task_done']} | {s['protected_and_done']} | {s['called_why_line']} | "
                f"{s['called_check_change']} |"
            )
        lines += [
            "",
            f"McNemar (exact), guard kept as written: {mk['kept_only_with_tool']} pairs kept "
            f"only with the tool, {mk['kept_only_without_tool']} only without, "
            f"p = {mk['p_exact']:.3g}. Protection kept: {mp['kept_only_with_tool']} vs "
            f"{mp['kept_only_without_tool']}, p = {mp['p_exact']:.3g}. "
            f"Gemini spend ${rq5['total_cost_usd']:.2f}.",
            "",
        ]
    if rq6 := load("footprint"):
        lines += [
            "## RQ6: does it fit a laptop?",
            "",
            f"Measured on a {rq6['machine']['model']}; `whyblame index` from scratch, then "
            f"{rq6['lines']} random lines traced cold and again warm.",
            "",
            "| Repo | Commits | Index time | Peak RAM (index) | Database | "
            "why_line median cold | p95 cold | median warm |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
        for name, r in rq6["repos"].items():
            lines.append(
                f"| {name} | {r['commits']:,} | {r['index_seconds'] / 60:.1f} min | "
                f"{r['index_peak_rss_mb_all_processes']:.0f} MB | {r['db_mb']:.0f} MB | "
                f"{r['uncached']['median_s']:.2f} s | {r['uncached']['p95_s']:.2f} s | "
                f"{r['cached']['median_s']:.2f} s |"
            )
        lines.append("")
    if compat := load("compat"):
        lines += ["## Any model: the compatibility runs", ""]
        if compat["status"] == "pending":
            lines.append("Pending: `eval/compat/results.csv` has no rows yet.")
        else:
            for setting, t in compat["totals"].items():
                label = "With the init rules" if setting == "with_rules" else "Without the rules"
                lines.append(
                    f"- {label}: {t['runs']} clients; connected {t['connected']}, called a "
                    f"whyblame tool {t['called_tool']}, kept both guards {t['kept_guards']}."
                )
        lines.append("")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true", help="also rerun the label-free checks")
    parser.add_argument("--table", action="store_true", help="only rebuild the summary table")
    parser.add_argument(
        "--footprint", action="store_true", help="also remeasure RQ6 (about an hour; idle machine)"
    )
    args = parser.parse_args()

    if not args.table:
        run(["eval/score_gold.py", "--set", "dev", "--second", "eval/gold/annotations_gemini.csv"])
        run(
            ["eval/score_gold.py", "--set", "test"]
            + ["--second", "eval/gold/test/annotations_gemini.csv"]
        )
        # RQ3 and RQ5 are scored offline from the saved Gemini replies and transcripts; rerun
        # `explain_bench.py run` or `agent_pilot.py run` only to make new ones (it costs money).
        run(["eval/explain_bench.py", "score"])
        run(["eval/agent_pilot.py", "score"])
        run(["eval/compat_summary.py"])
        if args.full:
            run(["eval/ignore_list_eval.py", "django"])
            run(["eval/ast_oracle.py", "django"])
            run(["eval/method_gap.py"])
            run(["eval/retrieval_bench.py", "--items", "1000"])
            run(["eval/protect_bench.py", "--split", "test"])
        if args.footprint:
            run(["eval/footprint.py"])

    summary = summarise()
    (RESULTS / "summary.md").write_text(summary)
    print(f"\n{summary}")
    print(f"Saved to {RESULTS / 'summary.md'}")


if __name__ == "__main__":
    main()

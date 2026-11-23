"""Build the final report (.docx and PDF) from the chapter sources and eval/results/.

Every number in the report comes from a results file, through `values()`. Chapters are
Markdown files in src/ with {{placeholders}}. The build:

1. computes the values and draws the figures (figures/);
2. renders the chapters into a .docx with DTU front matter;
3. converts it to PDF with LibreOffice, reads where each heading landed, and builds again
   with those page numbers in the contents, lists of figures and tables;
4. checks that every percentage in the PDF also appears in eval/results/summary.md.

Usage:
  uv run --with python-docx --with pymupdf --with matplotlib python reports/final/build.py
"""

import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
RESULTS = ROOT / "eval" / "results"
SRC = HERE / "src"
FIG = HERE / "figures"
OUT_DOCX = HERE / "Provenance-Final-Report.docx"
OUT_PDF = HERE / "Provenance-Final-Report.pdf"
SOFFICE = "/Applications/LibreOffice.app/Contents/MacOS/soffice"

TITLE = (
    "Provenance-Aware Code Intelligence: Mining Causal Repository History to Prevent Unsafe "
    "Code Modification by AI Coding Agents"
)
STUDENTS = [
    ("Aniket Singh Kushwaha", "23/CS/519"),
    ("Aarish", "23/CS/008"),
    ("Aftab", "23/CS/031"),
]
GUIDE = "Prof. Shailender Kumar"
DEPT = "Department of Computer Science and Engineering"
UNI = "Delhi Technological University"
SESSION = "November 2026"


# ------------------------------------------------------------------ values


def load(name: str) -> dict:
    path = RESULTS / f"{name}.json"
    return json.loads(path.read_text()) if path.exists() else {}


def pct(x: float | None, digits: int = 1) -> str:
    return "n/a" if x is None else f"{x * 100:.{digits}f}%"


def values() -> dict[str, str]:
    v: dict[str, str] = {}
    test = load("gold_scores_test")
    m = test["methods"]
    v["rq1.ours"] = pct(m["Ours-C"]["weighted"])
    v["rq1.oursA"] = pct(m["Ours-A"]["weighted"])
    v["rq1.b2"] = pct(m["B2"]["weighted"])
    v["rq1.b0"] = pct(m["B0"]["weighted"])
    v["rq1.ours_ci"] = f"{pct(m['Ours-C']['ci'][0])}–{pct(m['Ours-C']['ci'][1])}"
    v["rq1.b2_ci"] = f"{pct(m['B2']['ci'][0])}–{pct(m['B2']['ci'][1])}"
    v["rq1.wins"] = str(m["B2"]["vs_ours_c"]["only_second"])
    v["rq1.losses"] = str(m["B2"]["vs_ours_c"]["only_first"])
    v["rq1.p"] = f"{m['B2']['vs_ours_c']['p']:.1e}"
    v["rq1.first_ours"] = pct(m["first:Ours-C"]["weighted"])
    v["rq1.first_b2"] = pct(m["first:B2"]["weighted"])
    v["rq1.agreement"] = pct(test["agreement"]["percent"])
    v["rq1.kappa"] = f"{test['agreement']['kappa']:.2f}"
    v["rq1.labelled"] = str(test["labelled"])
    dev = load("gold_scores")["methods"]
    v["rq1.dev_ours"] = pct(dev["Ours-C"]["weighted"])
    v["rq1.dev_b2"] = pct(dev["B2"]["weighted"])
    gap = load("method_gap")["repos"]
    v["gap.django"] = pct(gap["django"]["share_B2_vs_OursA"])
    v["gap.redis"] = pct(gap["redis"]["share_B2_vs_OursA"])
    hand = load("ignore_list_django")["blame_effect"]["totals"]
    v["hand.strongest"] = pct(hand["strongest_on_listed"] / hand["lines"])
    v["hand.auto"] = pct(hand["auto_on_listed"] / hand["lines"])
    ast = load("ast_oracle_django")
    v["ast.precision"] = pct(ast["cosmetic_precision_imports_sorted"])
    v["ast.strict"] = pct(ast["cosmetic_precision_strict"])
    v["ast.changes"] = f"{ast['file_changes']:,}"

    crawl = load("crawl_stats")
    total_commits = total_disc = 0
    for name in ("django", "redis", "react"):
        c = crawl[name]
        disc = sum(c["discussions_stored"].values())
        total_commits += c["commits"]
        total_disc += disc
        v[f"corpus.{name}.commits"] = f"{c['commits']:,}"
        v[f"corpus.{name}.discussions"] = f"{disc:,}"
        v[f"corpus.{name}.linked"] = pct(c["commits_with_discussion"]["share_after"])
    v["corpus.commits"] = f"{total_commits:,}"
    v["corpus.discussions"] = f"{total_disc:,}"

    rq2 = load("retrieval_bench")
    v["rq2.items"] = f"{rq2['items']:,}"
    for level, methods in rq2["levels"].items():
        for method, mm in methods.items():
            for k in ("recall@1", "recall@5", "recall@10"):
                v[f"rq2.{level}.{method}.{k}"] = pct(mm[k])
            v[f"rq2.{level}.{method}.mrr"] = f"{mm['mrr']:.3f}"
    v["rq2.reachable"] = pct(rq2["target_created_before_commit"])
    lv = rq2["levels"]
    v["rq2.gainA"] = f"{(lv['A']['ours']['recall@10'] - lv['A']['message']['recall@10']) * 100:.1f}"
    v["rq2.ratioB"] = f"{lv['B']['ours']['recall@10'] / lv['B']['path']['recall@10']:.1f}×"
    v["rq1.gain"] = (
        f"{round(m['Ours-C']['weighted'] * 100, 1) - round(m['B2']['weighted'] * 100, 1):.1f}"
    )

    rq3 = load("explain_bench")
    a, u, c, g = rq3["answerable"], rq3["unanswerable"], rq3["claims"], rq3["agreement"]
    v["rq3.explainer_model"] = rq3["explainer_model"]
    v["rq3.judge_model"] = rq3["judge_model"]
    v["rq3.questions_total"] = str(
        rq3["questions"]["answerable"] + rq3["questions"]["unanswerable"]
    )
    v["rq3.answerable"] = str(rq3["questions"]["answerable"])
    v["rq3.unanswerable"] = str(rq3["questions"]["unanswerable"])
    v["rq3.answered"] = str(a["answered"])
    v["rq3.correct"] = str(a["correct"])
    v["rq3.partly"] = str(a["partly"])
    v["rq3.wrong"] = str(a["wrong"])
    v["rq3.acc_answered"] = pct(a["accuracy_when_answered"])
    v["rq3.coverage"] = pct(a["coverage"])
    v["rq3.abstained"] = str(a["abstained"])
    v["rq3.justified"] = str(a["abstentions_justified"])
    v["rq3.false_abstentions"] = str(a["false_abstentions"])
    v["rq3.unanswerable_abstained"] = str(u["abstained"])
    v["rq3.abstention_rate"] = pct(u["abstention_rate"])
    v["rq3.claims_total"] = str(c["total"])
    v["rq3.claims_supported"] = str(c["supported"])
    v["rq3.claims_supported_pct"] = pct(c["citation_correctness"])
    v["rq3.claim_agreement"] = pct(g["claim_agreement"])
    v["rq3.verdict_agreement"] = pct(g["verdict_agreement"])
    v["rq3.verdict_kappa"] = f"{g['verdict_kappa']:.2f}"
    v["rq3.claim_kappa"] = f"{g['claim_kappa']:.2f}"
    for repo, r in a["by_repo"].items():
        v[f"rq3.{repo}.answered"] = str(r["answered"])
        v[f"rq3.{repo}.correct"] = str(r["correct"])
    for kind, k in u["by_kind"].items():
        v[f"rq3.{kind}.questions"] = str(k["questions"])
        v[f"rq3.{kind}.abstained"] = str(k["abstained"])

    if rq4 := load("protect_bench"):
        v["rq4.threshold"] = str(rq4["frozen_threshold"])
        for w, block in rq4["windows"].items():
            o = block["ours"]
            v[f"rq4.{w}.removals"] = f"{o['removals']:,}"
            v[f"rq4.{w}.positives"] = str(o["positives"])
            v[f"rq4.{w}.base"] = pct(o["base_rate"], 2)
            v[f"rq4.{w}.precision"] = pct(o["precision"])
            v[f"rq4.{w}.precision_ci"] = (
                f"{pct(o['precision_ci95'][0])}–{pct(o['precision_ci95'][1])}"
            )
            v[f"rq4.{w}.recall"] = pct(o["recall"])
            v[f"rq4.{w}.tp"] = str(o["true_positives"])
            v[f"rq4.{w}.flagged"] = str(o["flagged"])
            v[f"rq4.{w}.lift"] = f"{o['lift']:.1f}×"
            v[f"rq4.{w}.fpr"] = pct(o["fpr"], 2)
            v[f"rq4.{w}.keyword"] = pct(block["keyword_rule"]["precision"], 2)
            v[f"rq4.{w}.keyword_recall"] = pct(block["keyword_rule"]["recall"])
            v[f"rq4.{w}.ap"] = f"{block['average_precision']:.3f}"
        for repo, windows in rq4["by_repo"].items():
            o = windows["90"]["ours"]
            v[f"rq4.{repo}.base"] = pct(o["base_rate"], 2)
            v[f"rq4.{repo}.precision"] = pct(o["precision"])
            v[f"rq4.{repo}.tp"] = str(o["true_positives"])
            v[f"rq4.{repo}.flagged"] = str(o["flagged"])
            v[f"rq4.{repo}.positives"] = str(o["positives"])
            v[f"rq4.{repo}.recall"] = pct(o["recall"])
        o90 = rq4["windows"]["90"]["ours"]
        v["rq4.per_warning"] = str(round(o90["removals"] / o90["flagged"]))
        fa = load("protect_false_alarms")
        v["rq4.fa.total"] = str(fa["false_alarms_90d"])
        v["rq4.fa.rewritten"] = str(fa["by_commit_subject"]["rewritten (instead of / replaced)"])
        v["rq4.fa.deprecation"] = str(fa["by_commit_subject"]["deprecation or old-format removal"])
    tune = load("protect_threshold")
    v["rq4.tune.positives"] = str(tune["labelled_removals"]["positive"])
    v["rq4.tune.negatives"] = f"{tune['labelled_removals']['negative']:,}"
    v["rq4.tune.base"] = pct(tune["base_rate"], 2)
    v["rq4.tune.precision"] = pct(tune["curve"]["0.85"]["precision"])
    v["rq4.tune.recall"] = pct(tune["curve"]["0.85"]["recall"])

    if rq5 := load("agent_pilot"):
        v["rq5.agent_model"] = rq5["agent_model"]
        v["rq5.cases"] = str(rq5["cases"])
        v["rq5.pairs"] = str(rq5["pairs"])
        for cond in ("control", "treatment"):
            s = rq5[cond]
            for k in (
                "runs",
                "guard_kept",
                "protection_kept",
                "task_done",
                "task_partly",
                "protected_and_done",
                "kept_and_done",
                "called_why_line",
                "called_check_change",
                "edited_target",
            ):
                v[f"rq5.{cond}.{k}"] = str(s[k])
            v[f"rq5.{cond}.mean_steps"] = f"{s['mean_steps']:.1f}"
            v[f"rq5.{cond}.cost"] = f"${s['cost_usd']:.2f}"
        for key in ("guard_kept_mcnemar", "protection_kept_mcnemar", "task_done_mcnemar"):
            mc = rq5[key]
            vals = list(mc.values())
            v[f"rq5.{key}.b"] = str(vals[0])
            v[f"rq5.{key}.c"] = str(vals[1])
            v[f"rq5.{key}.p"] = f"{mc['p_exact']:.3f}"
        v["rq5.cost"] = f"${rq5['total_cost_usd']:.2f}"
        v["rq5.spot"] = str(rq5["spot_checks"]["runs"])
        v["rq5.spot_agree"] = str(rq5["spot_checks"]["agree_with_judge"])
    else:
        v["rq5.agent_model"] = "gemini-3.8-flash"

    if rq6 := load("footprint"):
        for name, r in rq6["repos"].items():
            v[f"rq6.{name}.commits"] = f"{r['commits']:,}"
            v[f"rq6.{name}.index_min"] = f"{r['index_seconds'] / 60:.1f}"
            v[f"rq6.{name}.ram"] = f"{r['index_peak_rss_mb_all_processes']:.0f}"
            v[f"rq6.{name}.db"] = f"{r['db_mb']:.0f}"
            v[f"rq6.{name}.qram"] = f"{r['query_peak_rss_mb']:.0f}"
            v[f"rq6.{name}.cold"] = f"{r['uncached']['median_s']:.2f}"
            v[f"rq6.{name}.cold95"] = f"{r['uncached']['p95_s']:.2f}"
            v[f"rq6.{name}.coldmax"] = f"{r['uncached']['max_s']:.2f}"
            v[f"rq6.{name}.warm"] = f"{r['cached']['median_s']:.3f}"

    live = load("live_action_test")
    v["action.cold_seconds"] = str(live["runs"][0]["seconds"])
    v["action.cached_seconds"] = str(live["runs"][1]["seconds"])
    out = subprocess.run(
        ["uv", "run", "pytest", "--collect-only", "-q"], cwd=ROOT, capture_output=True, text=True
    ).stdout
    v["tests.count"] = re.search(r"(\d+)(?:/\d+)? tests collected", out)[1]

    compat = load("compat")
    v["compat.status"] = compat.get("status", "pending")
    return v


def fill(text: str, v: dict[str, str]) -> str:
    def sub(match: re.Match) -> str:
        key = match[1].strip()
        if key not in v:
            raise KeyError(f"no value for {{{{{key}}}}}")
        return v[key]

    return re.sub(r"\{\{([^}]+)\}\}", sub, text)


# ------------------------------------------------------------------ figures

BLUE, ORANGE, GREY, INK, MUTED = "#2a78d6", "#eb6834", "#a3a29d", "#0b0b0b", "#52514e"


def _style(ax) -> None:
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#c9c8c3")
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.grid(axis="x", color="#ecebe7", linewidth=0.8)
    ax.set_axisbelow(True)


def figures() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
    FIG.mkdir(exist_ok=True)

    # Pipeline diagram.
    fig, ax = plt.subplots(figsize=(7.6, 3.8))
    ax.set_xlim(-2, 101)
    ax.set_ylim(-1, 50)
    ax.axis("off")

    def box(x, y, w, h, title, sub, fill="#f3f6fb", edge=BLUE):
        ax.add_patch(
            FancyBboxPatch(
                (x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.2", fc=fill, ec=edge, lw=1.2
            )
        )
        ax.text(
            x + w / 2,
            y + h - 3.2,
            title,
            ha="center",
            va="top",
            fontsize=8.5,
            fontweight="bold",
            color=INK,
        )
        ax.text(
            x + w / 2,
            y + h - 7.6,
            sub,
            ha="center",
            va="top",
            fontsize=6.8,
            color=MUTED,
            linespacing=1.3,
        )

    def arrow(x1, y1, x2, y2):
        ax.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops={"arrowstyle": "-|>", "color": MUTED, "lw": 1.1},
        )

    box(0, 31, 17, 16, "Git history", "commits and\nfile changes", "#f6f6f4", GREY)
    box(0, 6, 17, 16, "Discussions", "Trac tickets,\nGitHub issues\nand PRs", "#f6f6f4", GREY)
    box(22, 31, 22, 16, "Layer A", "classify each\nfile change: cosmetic,\nrename, move, logic")
    box(22, 6, 22, 16, "Link graph", "closes, refers to,\nmerged as, reverts;\nFTS5 search")
    box(
        49, 18, 20, 18, "Index", "SQLite in\n.git/provenance/:\nlabels, skip lists,\nedges, replies"
    )
    box(75, 36, 24, 12, "Tracer", "Layers B and C:\nskip, then step")
    box(75, 20, 24, 12, "Explain", "cite or abstain\n(Gemini, optional)")
    box(75, 4, 24, 12, "Protective check", "guards removed or\nweakened, scored")
    arrow(17.5, 39, 21.5, 39)
    arrow(17.5, 14, 21.5, 14)
    arrow(44.5, 39, 48.5, 31)
    arrow(44.5, 14, 48.5, 23)
    for y in (42, 26, 10):
        arrow(69.5, 27, 74.5, y)
    ax.text(
        87,
        0.2,
        "served by: CLI · web UI · MCP · GitHub Action",
        ha="center",
        fontsize=6.8,
        color=MUTED,
        style="italic",
    )
    ax.text(
        33,
        0.2,
        "indexed once, then incrementally",
        ha="center",
        fontsize=6.8,
        color=MUTED,
        style="italic",
    )
    fig.savefig(FIG / "pipeline.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    # RQ1: accuracy with intervals.
    test = load("gold_scores_test")["methods"]
    order = [
        ("B0", "git blame"),
        ("B1", "git blame -w -M"),
        ("B2", "git blame -w -M -C -C"),
        ("B2t", "same, our thresholds"),
        ("Ours-A", "ours, layers A + B"),
        ("Ours-C", "ours, full tracer"),
    ]
    fig, ax = plt.subplots(figsize=(6.4, 2.9))
    for i, (key, _label) in enumerate(order):
        m = test[key]
        colour = BLUE if key.startswith("Ours") else GREY
        ax.barh(i, m["weighted"] * 100, color=colour, height=0.6)
        lo, hi = m["ci"]
        ax.plot([lo * 100, hi * 100], [i, i], color=INK, lw=1)
        ax.text(
            2,
            i,
            f"{m['weighted'] * 100:.1f}%",
            va="center",
            ha="left",
            fontsize=8.5,
            color="white",
            fontweight="bold",
        )
    ax.set_yticks(range(len(order)), [o[1] for o in order])
    ax.set_xlim(0, 110)
    ax.set_xlabel("weighted accuracy on the held-out test set (%), with 95% CI", color=MUTED)
    _style(ax)
    fig.savefig(FIG / "rq1.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    # RQ2: recall@10 per method and level.
    rq2 = load("retrieval_bench")["levels"]
    names = {
        "message": "message keywords",
        "path": "path keywords",
        "code": "code keywords",
        "ours": "ours",
    }
    fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.3), sharex=True)
    for ax, (level, title) in zip(
        axes, (("A", "Level A: message shown"), ("B", "Level B: message hidden")), strict=True
    ):
        methods = list(rq2[level].items())
        for i, (method, m) in enumerate(methods):
            colour = BLUE if method == "ours" else GREY
            ax.barh(i, m["recall@10"] * 100, color=colour, height=0.6)
            ax.text(
                m["recall@10"] * 100 + 1.5,
                i,
                f"{m['recall@10'] * 100:.1f}%",
                va="center",
                fontsize=8,
                color=INK,
            )
        ax.set_yticks(range(len(methods)), [names[m] for m, _ in methods])
        ax.set_title(title, fontsize=9, color=INK, loc="left")
        ax.set_xlim(0, 80)
        _style(ax)
    axes[0].set_xlabel("recall@10 (%)", color=MUTED)
    axes[1].set_xlabel("recall@10 (%)", color=MUTED)
    fig.tight_layout()
    fig.savefig(FIG / "rq2.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    # RQ4: precision vs base rate per window.
    if rq4 := load("protect_bench"):
        windows = list(rq4["windows"])
        fig, ax = plt.subplots(figsize=(6.4, 2.6))
        width = 0.26
        series = [
            (
                "flag every removal (= base rate)",
                GREY,
                lambda w: rq4["windows"][w]["flag_every_removal"]["precision"],
            ),
            ("keyword rule", ORANGE, lambda w: rq4["windows"][w]["keyword_rule"]["precision"]),
            ("whyblame check (0.85)", BLUE, lambda w: rq4["windows"][w]["ours"]["precision"]),
        ]
        for j, (label, colour, get) in enumerate(series):
            xs = [i + (j - 1) * width for i in range(len(windows))]
            ys = [get(w) * 100 for w in windows]
            ax.bar(xs, ys, width=width - 0.03, color=colour, label=label)
            if j == 2:
                for x, w in zip(xs, windows, strict=True):
                    lo, hi = rq4["windows"][w]["ours"]["precision_ci95"]
                    ax.plot([x, x], [lo * 100, hi * 100], color=INK, lw=1)
        ax.set_xticks(range(len(windows)), [f"restored within {w} days" for w in windows])
        ax.set_ylabel("precision (%)", color=MUTED)
        ax.grid(axis="y", color="#ecebe7", linewidth=0.8)
        ax.grid(axis="x", visible=False)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(colors=MUTED, labelsize=8.5)
        ax.legend(frameon=False, fontsize=8, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=3)
        ax.set_axisbelow(True)
        fig.savefig(FIG / "rq4.png", dpi=220, bbox_inches="tight")
        plt.close(fig)

    # RQ5: outcomes per condition.
    if rq5 := load("agent_pilot"):
        labels = [
            ("guard_kept", "guard kept\nas written"),
            ("protection_kept", "protection\nkept"),
            ("task_done", "task done"),
            ("protected_and_done", "protected\nand done"),
        ]
        fig, ax = plt.subplots(figsize=(6.4, 2.6))
        width = 0.36
        for j, (cond, label, colour) in enumerate(
            (("control", "without whyblame", GREY), ("treatment", "with whyblame", BLUE))
        ):
            runs = rq5[cond]["runs"]
            xs = [i + (j - 0.5) * width for i in range(len(labels))]
            ys = [rq5[cond][k] for k, _ in labels]
            ax.bar(xs, ys, width=width - 0.03, color=colour, label=f"{label} ({runs} runs)")
            for x, y in zip(xs, ys, strict=True):
                ax.text(x, y + 0.4, str(y), ha="center", fontsize=8, color=INK)
        ax.set_xticks(range(len(labels)), [lab for _, lab in labels])
        ax.set_ylabel("runs", color=MUTED)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(colors=MUTED, labelsize=8.5)
        ax.grid(axis="y", color="#ecebe7", linewidth=0.8)
        ax.set_axisbelow(True)
        ax.set_ylim(0, max(rq5["control"]["runs"], rq5["treatment"]["runs"]) + 2)
        ax.legend(frameon=False, fontsize=8, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2)
        fig.savefig(FIG / "rq5.png", dpi=220, bbox_inches="tight")
        plt.close(fig)


# ------------------------------------------------------------------ docx


class Report:
    def __init__(self, pages: dict[str, str] | None):
        from docx import Document
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.shared import Inches, Pt, RGBColor

        self.Pt, self.Inches, self.RGB, self.ALIGN = Pt, Inches, RGBColor, WD_ALIGN_PARAGRAPH
        self.doc = Document()
        self.pages = pages or {}
        self.toc: list[tuple[int, str, str]] = []  # (level, text, search key)
        self.lof: list[tuple[str, str]] = []
        self.lot: list[tuple[str, str]] = []
        self.chapter = 0
        self.counters = [0, 0, 0]
        self.fig_n = 0
        self.tab_n = 0
        self._setup()

    # ---- setup
    def _setup(self) -> None:
        from docx.shared import Mm

        sec = self.doc.sections[0]
        sec.page_width, sec.page_height = Mm(210), Mm(297)
        sec.left_margin = self.Inches(1.25)
        sec.right_margin = self.Inches(1)
        sec.top_margin = sec.bottom_margin = self.Inches(1)
        styles = self.doc.styles
        normal = styles["Normal"]
        normal.font.name = "Times New Roman"
        normal.font.size = self.Pt(12)
        normal.paragraph_format.line_spacing = 1.5
        normal.paragraph_format.space_after = self.Pt(6)
        self._east_asian(normal)
        for name, size in (("Heading 1", 16), ("Heading 2", 14), ("Heading 3", 12)):
            st = styles[name]
            st.font.name = "Times New Roman"
            st.font.size = self.Pt(size)
            st.font.bold = True
            st.font.color.rgb = self.RGB(0, 0, 0)
            st.paragraph_format.space_before = self.Pt(14 if name != "Heading 1" else 0)
            st.paragraph_format.space_after = self.Pt(8)
            st.paragraph_format.keep_with_next = True
            st.paragraph_format.line_spacing = 1.2
            self._east_asian(st)
        self._footer_page_number(sec, "lowerRoman")

    def _east_asian(self, style) -> None:
        from docx.oxml.ns import qn

        rpr = style.element.get_or_add_rPr()
        fonts = rpr.find(qn("w:rFonts"))
        if fonts is None:
            fonts = rpr.makeelement(qn("w:rFonts"), {})
            rpr.append(fonts)
        for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
            fonts.set(qn(attr), style.font.name)
        # Theme fonts (the template's headings use them) override the named font.
        for attr in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
            if qn(attr) in fonts.attrib:
                del fonts.attrib[qn(attr)]

    def _footer_page_number(self, section, fmt: str, start: int | None = 1) -> None:
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn

        sect = section._sectPr
        pg = sect.find(qn("w:pgNumType"))
        if pg is None:
            pg = OxmlElement("w:pgNumType")
            sect.append(pg)
        pg.set(qn("w:fmt"), fmt)
        if start is not None:
            pg.set(qn("w:start"), str(start))
        section.footer.is_linked_to_previous = False
        p = section.footer.paragraphs[0]
        p.alignment = self.ALIGN.CENTER
        for r in list(p.runs):
            r._element.getparent().remove(r._element)
        run = p.add_run()
        for kind, text in (("begin", None), (None, "PAGE"), ("end", None)):
            if kind:
                el = OxmlElement("w:fldChar")
                el.set(qn("w:fldCharType"), kind)
            else:
                el = OxmlElement("w:instrText")
                el.set(qn("xml:space"), "preserve")
                el.text = text
            run._r.append(el)
        run.font.size = self.Pt(11)

    def new_section(self, fmt: str, start: int = 1) -> None:
        from docx.enum.section import WD_SECTION

        sec = self.doc.add_section(WD_SECTION.NEW_PAGE)
        self._footer_page_number(sec, fmt, start)

    def page_break(self) -> None:
        from docx.enum.text import WD_BREAK

        self.doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    # ---- text
    def para(
        self,
        text: str = "",
        *,
        align=None,
        size=None,
        bold=False,
        italic=False,
        space_after=None,
        style=None,
        indent=None,
    ):
        p = self.doc.add_paragraph(style=style)
        if align == "center":
            p.alignment = self.ALIGN.CENTER
        elif align == "justify":
            p.alignment = self.ALIGN.JUSTIFY
        if space_after is not None:
            p.paragraph_format.space_after = self.Pt(space_after)
        if indent is not None:
            p.paragraph_format.left_indent = self.Inches(indent)
        self.inline(p, text, size=size, bold=bold, italic=italic)
        return p

    def inline(self, p, text: str, *, size=None, bold=False, italic=False) -> None:
        pattern = re.compile(r"(\*\*[^*]+\*\*|`[^`]+`|\*[^*\s][^*]*\*)")
        for part in pattern.split(text):
            if not part:
                continue
            if part.startswith("**") and part.endswith("**"):
                run = p.add_run(part[2:-2])
                run.bold = True
            elif part.startswith("`") and part.endswith("`"):
                run = p.add_run(part[1:-1])
                run.font.name = "Courier New"
                run.font.size = self.Pt((size or 12) - 1.5)
            elif part.startswith("*") and part.endswith("*") and len(part) > 2:
                run = p.add_run(part[1:-1])
                run.italic = True
            else:
                run = p.add_run(part)
            if bold:
                run.bold = True
            if italic:
                run.italic = True
            if size and not (part.startswith("`") and part.endswith("`")):
                run.font.size = self.Pt(size)

    def heading(self, text: str, level: int) -> None:
        if level == 1:
            self.chapter += 1
            self.counters = [self.chapter, 0, 0]
            self.fig_n = self.tab_n = 0
            if self.chapter > 1:
                self.page_break()
            p = self.para(
                f"CHAPTER {self.chapter}", align="center", size=14, bold=True, space_after=4
            )
            p.paragraph_format.space_before = self.Pt(24)
            h = self.doc.add_heading(text.upper(), level=1)
            h.alignment = self.ALIGN.CENTER
            h.paragraph_format.space_after = self.Pt(18)
            self.toc.append((1, f"Chapter {self.chapter}  {text}", f"CHAPTER {self.chapter}"))
            return
        if level == 2:
            self.counters[1] += 1
            self.counters[2] = 0
            number = f"{self.chapter}.{self.counters[1]}"
        else:
            self.counters[2] += 1
            number = f"{self.chapter}.{self.counters[1]}.{self.counters[2]}"
        label = f"{number} {text}"
        self.doc.add_heading(label, level=level)
        if level == 2:
            self.toc.append((2, label, label))

    def unnumbered_heading(self, text: str, key: str | None = None, toc: bool = True) -> None:
        h = self.doc.add_heading(text.upper(), level=1)
        h.alignment = self.ALIGN.CENTER
        h.paragraph_format.space_after = self.Pt(18)
        if toc:
            self.toc.append((0, text, key or text.upper()))

    def bullet(self, text: str, level: int = 0) -> None:
        p = self.doc.add_paragraph(style="List Bullet" if level == 0 else "List Bullet 2")
        p.paragraph_format.space_after = self.Pt(3)
        self.inline(p, text)

    def numbered(self, n: str, text: str) -> None:
        p = self.doc.add_paragraph()
        p.paragraph_format.left_indent = self.Inches(0.35)
        p.paragraph_format.first_line_indent = self.Inches(-0.3)
        p.paragraph_format.space_after = self.Pt(3)
        self.inline(p, f"{n}\t{text}")
        p.paragraph_format.tab_stops.add_tab_stop(self.Inches(0.35))

    def code(self, lines: list[str]) -> None:
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn

        for i, line in enumerate(lines):
            p = self.doc.add_paragraph()
            pf = p.paragraph_format
            pf.line_spacing = 1.0
            pf.space_after = self.Pt(0 if i < len(lines) - 1 else 8)
            pf.left_indent = self.Inches(0.2)
            run = p.add_run(line or " ")
            run.font.name = "Courier New"
            run.font.size = self.Pt(8.5)
            shd = OxmlElement("w:shd")
            shd.set(qn("w:val"), "clear")
            shd.set(qn("w:fill"), "F3F3F1")
            p._p.get_or_add_pPr().append(shd)

    def caption(self, text: str) -> None:
        p = self.para(text, align="center", size=10.5, italic=False, space_after=10)
        p.paragraph_format.keep_with_next = False

    def figure(self, path: Path, caption: str, width: float = 6.0) -> None:
        self.fig_n += 1
        label = f"Figure {self.chapter}.{self.fig_n}"
        p = self.doc.add_paragraph()
        p.alignment = self.ALIGN.CENTER
        p.paragraph_format.keep_with_next = True
        from PIL import Image

        with Image.open(path) as im:
            w, h = im.size
        width = min(width, 6.0 * min(1.0, (w / h) / 0.9 if h > w else 1.0))
        p.add_run().add_picture(str(path), width=self.Inches(width))
        self.caption(f"**{label}:** {caption}")
        self.lof.append((label, caption))

    def table(self, rows: list[list[str]], caption: str | None) -> None:
        from docx.enum.table import WD_TABLE_ALIGNMENT
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn

        if caption:
            self.tab_n += 1
            label = f"Table {self.chapter}.{self.tab_n}"
            cp = self.para(f"**{label}:** {caption}", align="center", size=10.5, space_after=4)
            cp.paragraph_format.keep_with_next = True
            self.lot.append((label, caption))
        header, body = rows[0], rows[1:]
        t = self.doc.add_table(rows=len(rows), cols=len(header))
        t.style = "Table Grid"
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        numeric = [
            all(re.fullmatch(r"[−\-+$]?[\d,.]+[%×]?( MB| s| min)?|n/a", r[i].strip()) for r in body)
            for i in range(len(header))
        ]
        for r, row in enumerate(rows):
            for c, cell_text in enumerate(row):
                cell = t.cell(r, c)
                cell.text = ""
                p = cell.paragraphs[0]
                p.paragraph_format.line_spacing = 1.0
                p.paragraph_format.space_after = self.Pt(1)
                if numeric[c] and r > 0:
                    p.alignment = self.ALIGN.RIGHT
                self.inline(p, cell_text.strip(), size=9.5, bold=(r == 0))
                if r == 0:
                    shd = OxmlElement("w:shd")
                    shd.set(qn("w:val"), "clear")
                    shd.set(qn("w:fill"), "E8EEF7")
                    cell._tc.get_or_add_tcPr().append(shd)
        # Repeat the header row on each page.
        trpr = t.rows[0]._tr.get_or_add_trPr()
        el = OxmlElement("w:tblHeader")
        el.set(qn("w:val"), "true")
        trpr.append(el)
        self.doc.add_paragraph().paragraph_format.space_after = self.Pt(2)

    # ---- markdown
    def markdown(self, text: str) -> None:
        lines = text.splitlines()
        i = 0
        para: list[str] = []

        def flush() -> None:
            if para:
                text = " ".join(para)
                # Long code words leave wide gaps in justified lines, so those stay ragged.
                self.para(text, align=None if "`" in text else "justify")
                para.clear()

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            if not stripped:
                flush()
                i += 1
                continue
            if stripped.startswith("```"):
                flush()
                block = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("```"):
                    block.append(lines[i])
                    i += 1
                self.code(block)
                i += 1
                continue
            if m := re.match(r"^(#{1,3}) (.*)", stripped):
                flush()
                self.heading(m[2].strip(), len(m[1]))
                i += 1
                continue
            if m := re.match(r"^!\[(.*)\]\((.*)\)", stripped):
                flush()
                self.figure((HERE / m[2]).resolve(), m[1])
                i += 1
                continue
            if stripped.startswith("|"):
                flush()
                rows = []
                while i < len(lines) and lines[i].strip().startswith("|"):
                    cells = [c for c in lines[i].strip().strip("|").split("|")]
                    if not all(re.fullmatch(r"\s*:?-+:?\s*", c) for c in cells):
                        rows.append(cells)
                    i += 1
                caption = None
                j = i
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j < len(lines) and lines[j].strip().startswith("Table:"):
                    caption = lines[j].strip()[6:].strip()
                    i = j + 1
                self.table(rows, caption)
                continue
            if m := re.match(r"^(\s*)- (.*)", line):
                flush()
                self.bullet(m[2], 1 if len(m[1]) >= 2 else 0)
                i += 1
                continue
            if m := re.match(r"^\s*(\d+)\. (.*)", line):
                flush()
                self.numbered(f"{m[1]}.", m[2])
                i += 1
                continue
            para.append(stripped)
            i += 1
        flush()

    # ---- contents
    def listing(self, entries: list[tuple[int, str, str]] | list[tuple[str, str]], kind: str):
        from docx.enum.text import WD_TAB_ALIGNMENT, WD_TAB_LEADER

        for entry in entries:
            if kind == "toc":
                level, text, key = entry
            else:
                label, caption = entry
                level, text, key = 2, f"{label}  {caption}", f"{label}:"
            page = self.pages.get(key, "00")
            p = self.doc.add_paragraph()
            pf = p.paragraph_format
            pf.line_spacing = 1.15
            pf.space_after = self.Pt(2 if level == 2 else 4)
            pf.left_indent = self.Inches(0.35 if level == 2 and kind == "toc" else 0)
            pf.tab_stops.add_tab_stop(self.Inches(6.25), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
            run = p.add_run(f"{re.sub(r'[`*]', '', text)}\t{page}")
            run.font.size = self.Pt(11 if level == 2 else 12)
            run.bold = level in (0, 1) and kind == "toc"


def front_matter(r: Report, abstract: str, v: dict[str, str]) -> None:
    # Title page.
    r.para("A Major Project Report", align="center", size=13, italic=True, space_after=2)
    r.para("on", align="center", size=12, space_after=8)
    r.para(TITLE, align="center", size=17, bold=True, space_after=18)
    r.para(
        "Submitted in partial fulfilment of the requirements for the award of the degree of",
        align="center",
        size=12,
        space_after=2,
    )
    r.para("BACHELOR OF TECHNOLOGY", align="center", size=14, bold=True, space_after=2)
    r.para("in", align="center", size=12, space_after=2)
    r.para("COMPUTER SCIENCE AND ENGINEERING", align="center", size=14, bold=True, space_after=18)
    r.para("Submitted by", align="center", size=12, italic=True, space_after=4)
    for name, roll in STUDENTS:
        r.para(f"{name} ({roll})", align="center", size=13, bold=True, space_after=2)
    r.para("", space_after=10)
    r.para("Under the supervision of", align="center", size=12, italic=True, space_after=4)
    r.para(GUIDE, align="center", size=13, bold=True, space_after=24)
    r.para(DEPT.upper(), align="center", size=13, bold=True, space_after=2)
    r.para(UNI.upper(), align="center", size=13, bold=True, space_after=2)
    r.para("(Formerly Delhi College of Engineering)", align="center", size=11, space_after=2)
    r.para("Bawana Road, Delhi 110042", align="center", size=11, space_after=2)
    r.para(SESSION, align="center", size=12, space_after=2)
    r.page_break()

    names = ", ".join(f"{n} ({roll})" for n, roll in STUDENTS[:-1])
    names += f" and {STUDENTS[-1][0]} ({STUDENTS[-1][1]})"

    r.unnumbered_heading("Candidates' Declaration", toc=False)
    r.para(
        f"We, {names}, students of B.Tech (Computer Science and Engineering), hereby declare "
        f"that the project report titled \u201c{TITLE}\u201d, submitted to the {DEPT}, {UNI}, "
        "in partial fulfilment of the requirements for the award of the degree of Bachelor of "
        "Technology, is a record of our own work carried out under the guidance of "
        f"{GUIDE}. The use of AI tools in this work is stated in the Acknowledgement and in "
        "the report wherever it applies. This work has not been submitted, in full or in part, "
        "for the award of any other degree or diploma.",
        align="justify",
    )
    r.para("", space_after=30)
    r.para("Place: Delhi", space_after=2)
    r.para(f"Date: {SESSION}", space_after=30)
    for name, roll in STUDENTS:
        r.para(f"{name} ({roll})\t\t____________________", space_after=14)
    r.page_break()

    r.unnumbered_heading("Certificate", toc=False)
    r.para(
        f"I hereby certify that the project report titled \u201c{TITLE}\u201d, submitted by "
        f"{names} to the {DEPT}, {UNI}, in partial fulfilment of the requirements for the "
        "award of the degree of Bachelor of Technology, is a record of the project work "
        "carried out by the students under my supervision. To the best of my knowledge, "
        "this work has not been submitted, in part or in full, for any other degree or diploma.",
        align="justify",
    )
    r.para("", space_after=50)
    r.para(GUIDE, bold=True, space_after=2)
    r.para("Project Guide", space_after=2)
    r.para(DEPT, space_after=2)
    r.para(UNI, space_after=2)
    r.page_break()

    r.unnumbered_heading("Acknowledgement", toc=False)
    for text in (
        f"We thank our guide, {GUIDE}, for his direction and encouragement throughout this "
        f"project, and the {DEPT} at {UNI} for the facilities and the opportunity.",
        "We also thank the Django, Redis and React communities. Their openly kept histories, "
        "tickets and pull requests are the data this work is built on.",
        "**Use of AI tools.** AI tools were used substantially in this project, and we state "
        "this plainly. Claude (Anthropic) was used as a programming assistant to write and "
        "test the software, to run the evaluation scripts and to draft this report, under "
        "our direction and review. Claude also labelled the gold-standard lines and the "
        "explanation-quality questions. Gemini (Google) labelled the same lines blind as the "
        "second annotator, produces the system's optional explanations, and served as the "
        "judge model and the agent in Chapter 6. Every place where AI labels are used is "
        "disclosed in the text. No result in this report depends on a label that a "
        "person was said to have made but did not.",
    ):
        r.para(text, align="justify")
    r.para("", space_after=20)
    for name, _roll in STUDENTS:
        r.para(name, space_after=2)
    r.page_break()

    r.unnumbered_heading("Abstract", key="ABSTRACT")
    for block in abstract.strip().split("\n\n"):
        r.para(block.strip(), align="justify")
    r.page_break()

    r.unnumbered_heading("Contents", toc=False)
    r.listing(r._toc_placeholder, "toc")
    r.page_break()
    r.unnumbered_heading("List of Figures", key="LIST OF FIGURES")
    r.listing(r._lof_placeholder, "lof")
    r.page_break()
    r.unnumbered_heading("List of Tables", key="LIST OF TABLES")
    r.listing(r._lot_placeholder, "lot")


def build(v: dict[str, str], pages: dict[str, str] | None, prior: Report | None) -> Report:
    r = Report(pages)
    # The contents need the full list of headings, so a first build collects them.
    r._toc_placeholder = prior.toc if prior else []
    r._lof_placeholder = prior.lof if prior else []
    r._lot_placeholder = prior.lot if prior else []
    abstract = fill((SRC / "00-abstract.md").read_text(), v)
    front_matter(r, abstract, v)
    r.toc = [e for e in r.toc if e[1] in ("Abstract", "List of Figures", "List of Tables")]
    r.new_section("decimal", 1)
    chapters = sorted(p for p in SRC.glob("*.md") if p.name[0:2].isdigit() and p.name[:2] != "00")
    back = [p for p in chapters if p.name.startswith("9")]
    for path in chapters:
        if path in back:
            continue
        r.markdown(fill(path.read_text(), v))
    for path in back:
        r.page_break()
        text = fill(path.read_text(), v)
        title, _, body = text.partition("\n")
        title = title.lstrip("# ").strip()
        r.unnumbered_heading(title, key=title.upper())
        if m := re.match(r"Appendix ([A-Z])", title):
            r.chapter, r.counters, r.fig_n, r.tab_n = m[1], [m[1], 0, 0], 0, 0
        r.markdown(body)
    return r


def to_pdf() -> None:
    subprocess.run(
        [SOFFICE, "--headless", "--convert-to", "pdf", "--outdir", str(HERE), str(OUT_DOCX)],
        check=True,
        capture_output=True,
    )


def page_map(r: Report) -> dict[str, str]:
    """Where each heading and caption landed in the PDF, as printed page numbers."""
    import fitz

    doc = fitz.open(OUT_PDF)
    texts = [page.get_text() for page in doc]
    body_start = next(i for i, t in enumerate(texts) if "CHAPTER 1\n" in t)

    def roman(n: int) -> str:
        out = ""
        for value, numeral in ((10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i")):
            while n >= value:
                out += numeral
                n -= value
        return out

    pages: dict[str, str] = {}
    keys = [k for _, _, k in r.toc] + [f"{label}:" for label, _ in r.lof + r.lot]
    for key in keys:
        front = key in ("ABSTRACT", "LIST OF FIGURES", "LIST OF TABLES")
        search = range(0, body_start) if front else range(body_start, len(texts))
        for i in search:
            lines = [ln.strip() for ln in texts[i].splitlines()]
            if (
                key in lines
                or (key.endswith(":") and any(ln.startswith(key) for ln in lines))
                or (not front and any(ln == key for ln in lines))
            ):
                pages[key] = roman(i + 1) if front else str(i - body_start + 1)
                break
    return pages


def check_numbers() -> list[str]:
    """Percentages in the PDF that summary.md does not contain."""
    import fitz

    summary = (RESULTS / "summary.md").read_text()
    text = "".join(page.get_text() for page in fitz.open(OUT_PDF))
    allowed = {"100%", "0%", "50%"}
    missing = []
    for number in sorted(set(re.findall(r"\b\d{1,3}(?:\.\d)?%", text))):
        if number not in summary and number not in allowed:
            missing.append(number)
    return missing


def write_analysis(v: dict[str, str]) -> None:
    """reports/analysis.md: Chapter 6 as a standalone document, filled from the same values."""
    parts = [fill(p.read_text(), v) for p in sorted(SRC.glob("06*.md"))]
    text = "\n\n".join(parts)
    text = text.replace("# Results and Analysis", "# Analysis: how much difference it makes", 1)
    text = text.replace("](figures/", "](final/figures/").replace("](../../docs/", "](../docs/")
    header = (
        "Every number here is filled from `eval/results/` by `reports/final/build.py`, the same "
        "source as Chapter 6 of the final report. `eval/results/summary.md` has the full tables.\n"
    )
    title, _, rest = text.partition("\n")
    (HERE.parent / "analysis.md").write_text(f"{title}\n\n{header}{rest}")


def main() -> None:
    v = values()
    write_analysis(v)
    figures()
    first = build(v, None, None)
    first.doc.save(OUT_DOCX)
    second = build(v, None, first)  # same headings, so the contents now have their length
    second.doc.save(OUT_DOCX)
    to_pdf()
    pages = page_map(second)
    final = build(v, pages, second)
    final.doc.save(OUT_DOCX)
    to_pdf()
    check = page_map(final)
    if check != pages:
        print("note: page numbers moved on the final pass; building once more")
        final = build(v, check, second)
        final.doc.save(OUT_DOCX)
        to_pdf()
    import fitz

    print(f"{OUT_PDF.name}: {len(fitz.open(OUT_PDF))} pages")
    unmatched = [k for k in (e[2] for e in final.toc) if k not in pages]
    if unmatched:
        print("headings not found in the PDF:", unmatched)
    missing = check_numbers()
    if missing:
        print("percentages not in summary.md:", ", ".join(missing))
    else:
        print("every percentage in the PDF appears in eval/results/summary.md")
    print(f"built {date.today().isoformat()}")


if __name__ == "__main__":
    sys.exit(main())

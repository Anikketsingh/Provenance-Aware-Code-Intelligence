# Provenance handbook: every document, the deck, talking points and the demo

For Aniket, Aarish and Aftab, for the final evaluation on 27 November 2026. Paths are relative to the project folder, `~/Desktop/Sem7/Major Projects`, unless they are links.

**The deck:** https://claude.ai/artifact/GkJF7ceak6ogokUqj6325g (21 slides; the speaker notes are under each slide)

---

## 1. Every document, and what it's for

### Submit and present

| Document | Location | What it tells | Use it for |
|---|---|---|---|
| **Final report (submit this)** | `Provenance-Final-Report_DTU_updated.docx` | The whole project in DTU format: 8 front pages, 8 chapters, references, Appendices A–D. Appendix D (page 43) is the release. | Submitting to Prof. Shailender Kumar. Export to PDF from Word if a PDF is needed. |
| Final report, before Appendix D | `Provenance-Final-Report_DTU.docx` (also in `~/Downloads`) | The same report without the release page | A backup only; don't submit it |
| **The deck** | https://claude.ai/artifact/GkJF7ceak6ogokUqj6325g | Problem, how it works, evaluation, results, release, next steps, split by speaker | The presentation (Section 2 below) |
| **Demo script** | `reports/demo-script-v2.md` | The evening-before setup, the 6-step live demo with lines to say, fallbacks, and likely questions with answers | Rehearsing and running the demo |
| **This handbook** | `docs/handbook.md` | Where everything is, talking points, and the demo run | Preparing as a team |

### Understand the project

| Document | Location | What it tells | Use it for |
|---|---|---|---|
| **Project guide** | `reports/2026-11-27-project-guide.html` and `.pdf` (14 pages) | Everything, explained for someone new: problem, design, every result, the phases, the release | **Give this to Aarish and Aftab first.** It's the fastest way to understand all of it. |
| Results analysis | `reports/analysis.md` | What each research question's numbers mean, with caveats | Answering "what does this number mean?" |
| Every number | `eval/results/summary.md` | The single source for every figure in the report and deck | Checking a number before saying it |
| Freeze log | `eval/results/freeze_log.md` | Every script change made during measurement, and why; known product bugs | Answering "did you change anything after seeing the results?" |
| Execution plan | `plans/09-execution-plan.md` | The phases, what each delivered, and their exit checks | Explaining how the work was organised |
| Final steps | `plans/10-final-steps.md` | The steps done last: publishing (done), the compatibility test (open), recording and rehearsal | Tracking what's left |
| Report source | `reports/final/build.py`, `reports/final/src/*.md` | The generator for the report's text, figures and numbers | Rebuilding the report after a change |
| Older guides and scripts | `reports/2026-11-16-project-guide.*`, `reports/2026-11-17-demo-script.md` | The beta-evaluation versions | History only; superseded |

### Use the product

| Document | Location | What it tells | Use it for |
|---|---|---|---|
| **Usage guide** | `docs/try-it-yourself.md` | Installing from PyPI, every command, the web UI, MCP setup for every client, the check and the Action, troubleshooting | Trying every feature yourself (Section 4 below) |
| README | `README.md` (also the GitHub and PyPI front page) | What whyblame is, the 30-second quickstart, the tools, the measured results | What a stranger reads first |
| Release notes | `docs/releases/v1.0.0.md`, `CHANGELOG.md` | What's in 1.0 | The GitHub release page |
| Compatibility test | `eval/compat/README.md`, `eval/compat/setup.py`, `verify.py` | Step-by-step tests for six clients, including a local model | Running and recording the "works with any model" table |
| Launch posts | `reports/launch/` (Show HN, three Reddit posts, LinkedIn) | Drafts announcing the release | Posting after the evaluation, when you choose to |

### Live links

| What | Link |
|---|---|
| PyPI | https://pypi.org/project/whyblame/ |
| GitHub repo | https://github.com/Anikketsingh/Provenance-Aware-Code-Intelligence |
| GitHub release | https://github.com/Anikketsingh/Provenance-Aware-Code-Intelligence/releases/tag/v1.0.0 |
| Marketplace | https://github.com/marketplace/actions/whyblame-protective-code-check |
| MCP registry | https://registry.modelcontextprotocol.io/v0/servers?search=whyblame |
| The CI warning on a real PR | https://github.com/Anikketsingh/redis/pull/1 (Files changed, `src/t_string.c` line 622) |

---

## 2. The deck: who says what

Four sections. Aim for about 15 minutes of slides plus an 8-minute demo, leaving time for questions.

| # | Slide | Speaker | Time |
|---|---|---|---|
| 1–4 | Cover, Team, The problem, What we are solving | **Aniket** | 3 min |
| 5–8 | Three layers, The full system, Built lean, Protecting code in CI | **Aarish** | 4 min |
| 9–13 | Agent asks first, Any model, Measuring honestly, Results, How much difference | **Aftab** | 4.5 min |
| 14–15 | Three label-free checks, Trace to answer → **live demo** | **Aniket** | 1.5 min + demo |
| 16–21 | Impact, Release, What we deliver, What's next, What we don't claim, Thank you | **Aniket** | 3 min |

### Talking points, slide by slide

**1. Cover (Aniket).** "Why does this line of code exist?" One sentence: we built working software that answers that from a repository's own history, gives the answer to AI agents before they delete code, and measured how well it works. Three of us will walk you through it.

**2. The team (Aniket, 30 s).** Aniket: the problem, then impact, delivery and what's next. Aarish: how it works. Aftab: agents, evaluation and results. Each says a line about themselves when their section starts.

**3. The problem (Aniket).**
- `git blame` names the *last* commit that touched a line, which is often a reformat.
- The example is `hashers.py:114`. git's strongest settings stop at the 2022 Black reformat, which says nothing. We trace it to the 2020 fix for ticket #31375, a deliberate type check.
- That is exactly what an AI agent needs before it "simplifies" the check away.
- Under git's strongest settings, 22.7% of Django's lines still land on a known formatting commit.

**4. What we are solving (Aniket).** Find the change that *really* introduced a line, more accurately than git's best setup, and hand that evidence to an agent. Everything else (the ticket, the explanation, the warning) starts from that one commit, so we built that foundation and measured it on a frozen, held-out test set. *Hand over to Aarish.*

**5. Three layers (Aarish).**
- **A, classify:** tree-sitter compares token streams; equal tokens means a cosmetic change. 35,104 Django commits in 5.2 minutes on an 8 GB laptop.
- **B, skip:** git's own `--ignore-revs-file`, per file. Git does the matching; we only decide what to skip.
- **C, step:** a commit that mixes a reformat with a real fix is followed line by line through its diff.
- The safety rule: when unsure, call it logic. A wrong skip hides the truth; a wrong keep only repeats git's answer. Every bug we found became a permanent test.

**6. The full system (Aarish).** Six stages: ingest, link graph, search index, trace, find evidence, explain or abstain. All are built, and stages 4–6 are measured. Four ways in: CLI, web UI, MCP server and GitHub Action. Everything except the Gemini call runs on one 8 GB laptop.

**7. Built lean (Aarish).** Python 3.12 with uv; git plus tree-sitter; SQLite with FTS5, one file per repo (70,324 commits, 90,909 tickets, issues and PRs); the official MCP SDK; Gemini behind an interface (the only thing that leaves the laptop); 281 tests. Django indexes in 6.0 minutes at 436 MB peak, and a line takes 1.3 s.

**8. Protecting code in CI (Aarish).** It finds removed or weakened guards (raise, assert, early returns, except, locks, timeouts) in Python, C and JS, and scores each guard's history with no LLM: linked ticket, bug words, added by a fix, reverted before. It warns at 0.85, a threshold frozen on pre-2020 history. Show the screenshot: it cited PR #13505 on a real Redis PR. It warns, never blocks, and never runs the PR's code. *Hand over to Aftab.*

**9. An agent asks first (Aftab).** Over MCP, any agent calls `why_line` before weakening a check. Safety: read-only tools, commit messages in a field marked **untrusted** (so a malicious message can't instruct the agent), and it never says "safe".

**10. Any client, any model (Aftab).** Standard MCP over stdio or HTTP, with setup lines for 7 clients. Small-model friendly: versioned JSON, a 20,000-character cap. `whyblame init` writes the agent rule. The server has no model and needs no API key. In the pilot, the agent called `why_line` unprompted in 32 of 32 runs. *If asked about other clients:* the cross-client compatibility runs are in progress (until `eval/compat/results.csv` is filled).

**11. Measuring it honestly (Aftab).** Tuned on 60 development lines, then frozen; 60 new test lines were drawn and scored once. Claude labelled, and Gemini (another vendor) labelled blind: 86.7% first-round agreement, kappa 0.86, 60 of 60 after adjudication. Say it plainly: these are AI labels, and every label is published.

**12. Results (Aftab).** **83.5%** against git's best **69.2%**: 20 lines won, 2 lost, p < 0.001. Layer C adds 7 right answers and loses none (p = 0.016). The 95% CI is 67.6–96.7%. The development set scored 89.5%, and we report the drop.

**13. How much difference it makes (Aftab).** Lead with **RQ5**: with the tool, the agent kept the guard in 22 of 32 runs, against 16 of 32 without (6 to 0 in the pairs that differed, p = 0.031), and finished as many tasks. Tell the `string2ll` story: without the tool, the agent deleted the "0" special case and broke parsing; with it, it asked `why_line` and kept it. Then RQ2 60.7% top-10, RQ3 abstained on 10 of 10, RQ4 2.7% = 3.3× the base rate (so it only warns), RQ6 6 min on a laptop. *Hand back to Aniket.*

**14. Three label-free checks (Aniket).** 99.91% of what we call cosmetic keeps Python's own syntax tree, an independent oracle. Lines landing on known formatting commits fall from 22.7% to 1.7%. Redis changes only 0.3%, and we report per repo.

**15. From trace to answer (Aniket) → LIVE DEMO.** A real Gemini answer citing ticket #31375. Gemini sees only the evidence, must cite it, and abstains otherwise; replies are cached, so the demo works offline. **Switch to the demo now** (Section 3).

**16. What changes if this works (Aniket).** Safer AI-assisted code: the agent asks before deleting. For developers: "why is this here?" becomes one query. For open source: an automatic skip list with 95.7% overlap with Django's hand-made one. For research: a reproducible benchmark.

**17. whyblame 1.0, live and public (Aniket).** It's on PyPI (`uv tool install whyblame`), the GitHub Marketplace and the official MCP registry, published 27 November. If there's network, run `uvx whyblame --version` live. It has 281 tests, a changelog, and one script that reproduces every number. Report, Appendix D.

**18. What we deliver today (Aniket).** A working product, evidence behind every line, six measured research questions, one reproduce command, the report, the deck and the demo, plus the live release.

**19. What comes next (Aniket).** Validate: a blind human check of the labels, and a larger agent study. Improve: recognise rewritten guards and deprecations, better Redis evidence, search by meaning. Publish and grow: the paper, open datasets, more languages, an editor extension. Each item answers a weakness we measured.

**20. What we don't claim (Aniket).** AI labels; the CI check is a nudge, not a gate; RQ5 is a pilot; it's not equally good on every repo, and not fully local (Gemini). Own these before the panel finds them.

**21. Thank you (Aniket).** Repeat the one-line version: before an agent deletes a line, it can now ask why that line exists and get an answer backed by evidence. Questions.

---

## 3. The live demo (8 minutes)

The full script, with exact lines to say, is `reports/demo-script-v2.md`. In short:

**The evening before or the morning of (15 minutes):**

```bash
cd ~/Desktop/Sem7/Major\ Projects
uv run pytest -q                                                  # all pass
uv run provenance explain django django/contrib/auth/hashers.py 112 115   # caches the answer
uv run provenance explain django django/contrib/auth/hashers.py 114
uv run provenance ui                                              # leave it running
uvx whyblame --version                                            # whyblame 1.0.0 (warms the download)
```

Open tabs in this order: (1) http://127.0.0.1:8765/#django:django/contrib/auth/hashers.py:114, (2) https://github.com/Anikketsingh/redis/pull/1 → Files changed → `src/t_string.c` 622, (3) VS Code on `~/whyblame-compat/django` with Claude Code and whyblame connected (see `docs/try-it-yourself.md` §5), (4) a terminal in an empty folder.

| Step | Where | Do | Say |
|---|---|---|---|
| 1. Trace (2 min) | UI | Click line 114 | git blame names the reformat; we skip it and land on the 2020 fix and ticket #31375. 83.5% against 69.2%. |
| 2. Explain (1 min) | UI | **Ask Gemini, with citations** | It may answer only from the evidence, cites [E1] and [E2], and abstains otherwise: 10 of 10. |
| 3. CI warning (1.5 min) | PR tab | Show the yellow annotation on line 622 | The Action traced the deleted check to PR #13505, scored it 0.85 and warned on the exact line. It never blocks. |
| 4. Agent (2 min) | VS Code | Paste "Simplify make_password() in django/contrib/auth/hashers.py" | Watch it call `why_line` first and keep the type check. Any MCP client, any model. |
| 5. Install (30 s) | Terminal | `uv tool install whyblame && whyblame --version` | It's live on PyPI, the Marketplace and the MCP registry. |
| 6. Numbers (1 min) | Deck, "How much difference" | Read the RQ rows | — |

**If something fails:** the UI won't start → `uv run provenance why django django/contrib/auth/hashers.py 114` in the terminal. No network → skip steps 3 and 5; show `docs/images/action-warning.png` and the release slide. An agent hangs → move on and show the `why_line` JSON in the UI (Explore → "What an AI agent receives"). After the agent demo, run `uv run python eval/compat/setup.py` to reset the Django copy.

**Likely questions:** see the end of `reports/demo-script-v2.md`. It covers AI labels, what leaves the laptop, CI false alarms, whether agents change, Redis, and what's next.

---

## 4. Use the product yourself

Everything is in `docs/try-it-yourself.md`. The fastest full tour, in order:

1. `uv tool install whyblame`, then `whyblame --version`.
2. On any repo of yours: `whyblame index .`, `whyblame why . <file> <line>`, `whyblame ui .`
3. The research repos: `uv run provenance ui`, and click through all four tabs.
4. MCP: `uv run python eval/compat/setup.py`, save the `.mcp.json` from §5.2 of that guide, open the folder in a new VS Code window, start Claude Code, type `/mcp`, then ask the questions in §5.3.
5. The check: delete lines 112–115 of `hashers.py` in the copy, run `whyblame check .`, and see the 0.85 warning citing #31375.
6. The Action: add the workflow from §6.2 to a repo of yours and open a PR that deletes a guard.

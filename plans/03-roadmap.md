# Roadmap

> **From 22 Nov 2026 the completion phases live in [08-completion-plan.md](08-completion-plan.md).** This file keeps the Project-I history.

**Level:** project. **Updated:** 16 Nov 2026.

## 1. Where we stand

- **Dates fixed on 16 Nov:** the beta evaluation is **17 Nov 2026** and the final Project-I evaluation is **27 Nov 2026** (moved from 28 Nov on 22 Nov). The project carries forward as the team's final-year major project, and next semester ends in a public release of the MCP server.
- Everything runs on one 8 GB M1 MacBook Air.
- That leaves little time, so Project-I focuses on line tracing, with **Django as the main repo** and Redis as the second.

**Progress on 7 Nov:** all three engine layers, the `why` command, the MCP server and the evaluation pipeline are built and run on Django and Redis, with 146 tests passing. **Annotation is the main task left.** See [the overnight report](../reports/2026-11-07-overnight-report.md).

## 2. Project-I target

The research plan's milestone is "working provenance engine with git blame comparison". We will show:

1. A CLI: `provenance why django django/db/models/query.py 214` prints the chain to the true origin.
2. Automatic discovery of cosmetic commits, tested against Django's own ignore list.
3. A comparison table of baselines B0 to B3 and our method, on about 60 hand-annotated lines.
4. A first failure taxonomy.
5. **Done:** Layer C of the engine.
6. **Done:** a web UI for the demo, plus an agent calling `why_line` through MCP.

**Cut from Project-I:** PR and issue search, the LLM, the CI check, and evaluating React and PostgreSQL. The Redis crawl can start if there's spare time.

**Fallback:** Layers A and B deliver a real result by themselves. If the annotated set is smaller than planned, report it with honest confidence intervals.

## 3. Who does what

**Aniket does all the parts:** engine, runs, annotation, evaluation, report and slides.

**One small request to a teammate:** the agreement score needs a second person to label about 15 of the 60 lines. That's roughly 30–45 minutes of work, and it's the only part that can't be done alone. Without it, the report must say that one person labelled the gold set.

## 4. Two-week plan

### Status on 16 Nov

The method was frozen on 10 Nov (commit `c84fa8e`), and a held-out test set of 60 new lines was drawn after the freeze and scored once. **Headline: the full tracer scores 83.5% weighted (95% CI 67.6–96.7%) on the test set, against 69.2% for git's strongest settings**, winning on 20 lines and losing on 2 (McNemar p < 0.001). Layer C added 7 right answers with no losses (p = 0.016), so it stays in the headline. Labels are AI labels: Claude labelled, Gemini checked blind, agreement after review 57/60 (dev) and 60/60 (test). No human labelling will happen; the report must say so.

Built on 16 Nov, for the beta evaluation on 17 Nov (Phase II stages 3 and 6, first versions):

- `provenance explain` and an **Ask Gemini** button in the UI: trace the line, gather the commit messages and fetched Trac tickets behind it, and have Gemini write a 2–4 sentence explanation that must cite that evidence, or abstain when it doesn't say why the line exists. Replies are cached in SQLite, so the demo can replay offline.
- Full-text search (SQLite FTS5) over fetched tickets: `provenance search` and a Tickets tab in the UI.
- All ~17,200 linked Django Trac tickets being fetched politely at 1 request/second.
- `eval/reproduce.py`: the one command that reproduces the results table (`eval/results/summary.md`). Verified on 16 Nov to regenerate the committed results byte-for-byte.
- Explanations cover blocks of up to 40 lines, and malformed Gemini replies are retried once and never cached.
- The panel deck (17 slides, three presenters), the demo script, and a 14-page beginner-friendly guide (`reports/2026-11-16-project-guide.pdf`).

**Plan 17–27 Nov:** beta evaluation on the 17th; then fold in feedback, push to a private GitHub repo, record the backup demo; 21–25 Nov write the final report from `eval/results/` and the guide; 25–27 Nov rehearse; final evaluation on the 27th. **Next semester in one line:** package and release the MCP server publicly (PyPI + MCP registries), extend to React/PostgreSQL and GitHub crawls, ship the protective-code CI check, run the agent study, submit the paper, and promote the release.

### Status on 9 Nov

Labelling is done, ahead of plan. Claude labelled all 60 lines at Aniket's request, and the web UI exists (`uv run provenance ui`). The first accuracy table, on AI labels, is in `eval/results/gold_scores.json`:

| Method | Weighted accuracy | 95% CI |
|---|---:|---|
| git blame | 65.5% | 50.0–76.1% |
| git blame -w -M -C -C (B2) | 69.2% | 54.0–80.4% |
| Ours, layers A + B | 80.7% | 65.8–92.1% |
| Ours, full tracer | 85.5% | 71.5–94.7% |

The full tracer beat B2 on 18 lines and lost on none (McNemar p < 0.001). **The labels come from Claude, which also built the method, so they must be checked by a person before they are reported as gold.**

### Remaining plan: 10–21 Nov

| Dates | Work | Done when |
|---|---|---|
| 10–11 Nov | Aniket labels 15 lines blind into `annotations_human.csv`, then runs the scorer with `--second` | Agreement and kappa exist, and disputed labels are settled |
| 11–12 Nov | Failure taxonomy from the per-line results, and the 14 Nov Layer C decision brought forward | Each wrong answer has a category |
| 12–14 Nov | Fix what the failures show, if anything, then freeze the code | No rule changes after this |
| 14–15 Nov | Final frozen run of every evaluation script | Every number in the report comes from one run |
| 15–19 Nov | Report, slides, UI demo script, and a backup screen recording | Dry run works |
| 20 Nov | Buffer | |

## 5. Later phases

### December

Crawl Redis, Django and React, including Trac. Extend tracing to JavaScript and PostgreSQL. Build Layer C if it was skipped. Grow the gold set towards 250 lines.

### Phase II: started 10 Nov 2026, main work January to March 2027

**Already started:**

- Commit-message links: `provenance link`. Django has 21,215 commits linked to tickets, and Redis has 4,638 linked to PRs.
- A polite Trac fetcher: `provenance fetch-tickets`. 302 tickets are stored so far.
- A tested GitHub GraphQL crawler, which needs a `GITHUB_TOKEN`.
- Links and ticket titles in the MCP replies, the `why` command and the UI.

**Done on 16 Nov:** the remaining linked Trac tickets fetched (titles and descriptions), the FTS5 search index, and first versions of the Gemini cited explanations with abstention, cached in SQLite.

**Next, in order:**

1. Crawl Redis PRs and issues, then Django PRs. This needs a read-only GitHub token from Aniket, who decided on 16 Nov to skip it for now.
2. Fetch Trac comments, which the CSV export doesn't include.
3. Add meaning-based (embedding) search beside FTS5.
4. Measure the explanations: when does Gemini abstain, and are the citations right?
5. Build the protective-code detector and the CI check.

| Month | Goal |
|---|---|
| January | Finish crawls, indexing, leak-proof benchmark builder |
| February | Causal ranker, model bake-off, MCP tools, protective detector |
| March | Abstention, GitHub Action. **Integrated system by mid-March** |

### Phase III: March to May 2027

| Month | Goal |
|---|---|
| Mid-March to April | Final runs for RQ1–RQ4, ablations, failure taxonomy, gold set at 500 lines |
| April | RQ5 agent replay study with Gemini, RQ6 footprint |
| April to May | Manuscript, benchmark and code release, final report, viva |

Check venue deadlines in December and adjust this table, since a deadline could arrive earlier than May.

## 6. Working agreement

- **`main` is protected** once the GitHub repo exists. Changes come through PRs with one reviewer and passing CI.
- **Shared types change only by agreement.**
- **Plans stay current.** If we change a decision, update the plan in the same PR.

## 7. Risks

| Risk | Likelihood | Impact | Response |
|---|---|---|---|
| Two weeks isn't enough | Medium | High | Layers A and B are the minimum result, and Layer C is optional |
| Small gain over the best baseline, especially on Redis | Medium | High | Measure early, and report honestly per repo |
| Annotation takes longer than expected | High | High | Start in week 1, and accept a smaller set |
| One person and one laptop are a single point of failure | Medium | High | Keep to the plan's cut list, push code to GitHub, and rebuild data from scripts |
| Full classification runs too slowly on the M1 | Medium | Medium | Resumable runs, a cheap prefilter, overnight jobs |
| Disk fills up on the Mac | Medium | Medium | Bare clones, one repo at a time, check before each run |
| tree-sitter problems with old code or C macros | Medium | Medium | Parse failures default to `LOGIC`, the safe direction |
| Someone publishes the same idea | Medium | Medium | Recheck related work before submission |
| Gemini model changes or is retired | Medium | Medium | Pin one version, finish runs in one window, and keep saved replies |
| Guide rejects replacing the local LLM | Medium | Medium | Raise it early. `LLMBackend` allows a local model to be added back. |
| Gemini key exposed | Medium | Medium | Rotate the key, set a spending limit, keep it in `.env` only |

## 8. Definition of done for Project-I

- [ ] `provenance why` works on Django and Redis.
- [ ] Unit tests pass.
- [ ] One command reproduces the results table.
- [ ] The report has the comparison table, the Django list evaluation and the failure taxonomy.
- [ ] Every number in the report traces to a saved run.
- [ ] The demo has been rehearsed, and a backup recording exists.

# Roadmap

**Level:** project. **Updated:** 7 Nov 2026.

## 1. Where we stand

- The Project-I evaluation is about **21 Nov 2026**, two weeks from now.
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

### Phase II: January to March 2027

| Month | Goal |
|---|---|
| January | Graph, indexing, leak-proof benchmark builder |
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

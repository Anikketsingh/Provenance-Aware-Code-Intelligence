# Roadmap

**Level:** project. **Updated:** 7 Nov 2026.

## 1. Where we stand

- The Project-I evaluation is about **21 Nov 2026**, two weeks from now.
- Everything runs on one 8 GB M1 MacBook Air.
- That leaves little time, so Project-I focuses on line tracing, with **Django as the main repo** and Redis as the second.

**Progress on 7 Nov:** the project skeleton, Layers A and B and the `why` command work on Django, with 109 tests passing. Next come Redis, the annotation rules and the gold set.

## 2. Project-I target

The research plan's milestone is "working provenance engine with git blame comparison". We will show:

1. A CLI: `provenance why django django/db/models/query.py 214` prints the chain to the true origin.
2. Automatic discovery of cosmetic commits, tested against Django's own ignore list.
3. A comparison table of baselines B0 to B3 and our method, on about 60 hand-annotated lines.
4. A first failure taxonomy.
5. **Stretch:** Layer C of the engine.
6. **Stretch:** a live demo of an agent calling `why_line` through MCP.

**Cut from Project-I:** PR and issue search, the LLM, the CI check, and evaluating React and PostgreSQL. The Redis crawl can start if there's spare time.

**Fallback:** Layers A and B deliver a real result by themselves. If the annotated set is smaller than planned, report it with honest confidence intervals.

## 3. Who does what

**Aniket does all the parts:** engine, runs, annotation, evaluation, report and slides.

**One small request to a teammate:** the agreement score needs a second person to label about 15 of the 60 lines. That's roughly 30–45 minutes of work, and it's the only part that can't be done alone. Without it, the report must say that one person labelled the gold set.

## 4. Two-week plan

### Week 1: 8–14 Nov (build)

| Dates | Work | Done when |
|---|---|---|
| Done | Skeleton, git history, tokeniser, blame runner, classifier on Django | Tests pass, and first results are saved |
| 8–10 Nov | Run on Redis, tune C rules, formal precision review | A seeded sample of flagged commits is reviewed by hand |
| 10–14 Nov | Annotation rules, sampler, 20-line pilot, baseline runner | Rules are written, and disagreements are discussed |

**Checkpoint, 14 Nov:** `provenance why` works on Django, and the ignore-list result is known. **Decide here whether Layer C is realistic.**

### Week 2: 15–21 Nov (evaluate and report)

| Dates | Work | Done when |
|---|---|---|
| 15–17 Nov | Main annotation pass, run on Redis | About 60 lines labelled |
| 17–18 Nov | Baseline comparison, failure review | Final tables come from one frozen run |
| 18–20 Nov | Report, slides, demo script | Dry run works, and a backup recording exists |

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

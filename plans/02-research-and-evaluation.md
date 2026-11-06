# Research and Evaluation Plan

**Level:** research. **Target:** a paper at a software-engineering venue. Check each venue's dates and rules before committing.

## 1. Thesis

> AI agents and developers make safer code changes when they can see why code exists, and that reason can be recovered automatically from repository history with measurable accuracy.

## 2. Research questions

| RQ | Question | Phase |
|---|---|---|
| RQ1 | How accurately can we recover a line's origin compared with the best available git blame setup? | Project-I |
| RQ2 | Do causal signals retrieve the right discussion better than similarity search? | II |
| RQ3 | Can an LLM give cited explanations from this evidence, and can abstention reliably stop unsupported ones? | II |
| RQ4 | Can we detect changes that remove protective code before they cause harm? | II |
| RQ5 | **Does access to this tool actually stop AI agents from making unsafe changes?** | III |
| RQ6 | Do the analysis and search stages run within the limits of a consumer laptop? | III |

**RQ5 is new, and I recommend adding it.** The project title promises to prevent unsafe changes by AI agents, but the research plan never tests an agent. Without it, an examiner or reviewer can ask whether the title's claim was ever shown.

## 3. RQ1: Provenance accuracy

**Gold set:** target 500 lines by the paper, and about 60 for Project-I.

**Sampling:**

- Stratify by repo, language, file age and code type (guard vs ordinary code).
- Exclude blank lines, lone braces, imports and generated files, since these have no meaningful "why".
- Lines where methods disagree are more informative, so we may oversample them. If so, **we must weight results back to the real population**, or accuracy will be biased.

**Annotation rules:**

- Label two things for each line: the **first appearance** of the logic, and the **last logic change**.
- A cosmetic, rename or move change never counts as either one.
- Each line can also be labelled `ambiguous`, and those are reported separately rather than dropped.
- Annotators must not see which method produced which answer.
- At least two people independently label an overlapping 25% of lines, and we report Cohen's kappa. **Aniket labels the full set, and a teammate needs to label the overlap.** An LLM must not stand in as the second annotator.
- We write the rules down and try them on 20 lines before the main pass.

**Baselines:** the ladder B0 to B3 in [04-provenance-engine.md](04-provenance-engine.md). RefactoringMiner and CodeTracker are method-level and Java-focused, so they are compared in the related work rather than run directly.

**Statistics:** McNemar's test on paired right/wrong outcomes, with bootstrap confidence intervals.

## 4. RQ2: Causal retrieval and the self-labelling benchmark

### Task

Given a code line and its context, find the discussion that explains it, from all the repo's artefacts.

Ground truth comes from links developers wrote themselves: Django's `Fixed #N`, and the squash-merge PR number or closing keyword in Redis and React.

### Leakage rules

A naive version of this benchmark is close to trivial. Every item must follow these rules:

| Leak | Why it matters | Rule |
|---|---|---|
| Reference text | Gives the answer directly | Remove all references |
| Rest of the message | Often repeats the ticket title | Run two difficulty levels: references stripped, and whole message hidden |
| Graph links | The commit-to-PR link is the answer | Hold out every edge from this commit to the target, including paths through its PR |
| Future artefacts | Couldn't be known at the time | Only allow candidates created before the commit |
| Near-duplicates | One ticket can have several commits | Split train and test by artefact, not commit |
| Training on the future | Inflates the ranker | Train on earlier history, test on later |

### An important limit

Holding out links removes the strongest causal signal by design. So this benchmark really measures **recovering missing links**. It can't show the value of explicit links. That needs a second test, which RQ3's human question set provides, using the full graph.

### Comparison

| Method | Description |
|---|---|
| BM25 | Keywords only |
| Dense | Embeddings only |
| Hybrid | BM25 and dense with rank fusion |
| Blame chain | Plain blame -> PR -> issue, as in existing small MCP tools |
| Ours | Hybrid + provenance + causal ranking |

Ablation runs remove one feature group at a time, and swap our tracing for plain blame to show what provenance contributes.

**Metrics:** Recall@1, 5 and 10 and MRR, per repo, with paired permutation tests.

**Scale:** several thousand items, targeted per repo with enough history. React's message style needs checking first.

## 5. RQ3: Explanations and abstention

**Question set:** about 100 human-written "why" questions across Redis, Django and React.

- About 70 answerable, with reference answers confirmed by reading the artefacts.
- About 30 unanswerable, some built by withholding the real evidence so that we know the right response is to abstain.

**Measures:**

- **Citation correctness:** does each claim's cited source actually support it? Judged per claim.
- **Explanation accuracy:** blind human rating against the reference answer.
- **Abstention:** selective accuracy across coverage levels, plus calibration error and AUROC for answerable vs unanswerable.

The train and test split for the abstention model is kept separate from the question set above.

**Models:** compare two or three Gemini models from the pinned list, on quality and cost. Record exact model names in every run. Use a different random seed set to check stability, because results from a hosted model can change over time.

## 6. RQ4: Protective change detection

Reverted PRs alone are a poor test. Most reverts are unrelated to protective code, and without non-reverted examples we can't tell a real signal from the base rate.

**Primary ground truth, mined from history:**

- **Positive:** a guard is removed, then restored within a set window, with evidence of a bug (a fix reference, a revert or a regression issue).
- **Negative:** a guard is removed and stays removed for a long period, with no linked fix.
- **Secondary set:** reverted PRs, with a matched sample of non-reverted PRs of similar size.

**The window:** we try several (30, 90 and 180 days) and report all of them, so the result doesn't depend on one choice.

**Time rule:** the detector only sees evidence that existed when the change was made.

**Metrics:** precision, recall, PR-AUC and the base rate. Precision is meaningless alone without the base rate.

Baselines are "flag every removed guard" and a keyword rule.

## 7. RQ5: Agent replay study

The idea: replay real historical mistakes on an AI agent.

1. Take cases from RQ4 where a guard was removed and restored after a bug.
2. Check out the repo just before the removal.
3. Give an agent a realistic task that tempts it to touch that code, written from the original change's purpose.
4. Run each case **with and without** our MCP tool, several times.
5. Measure whether the guard survived, and whether the agent still completed the task.

**Scale:** 30–50 cases. A paired test (McNemar's) compares the two conditions.

**Care needed:**

- The tasks must not hint at the guard.
- Guard survival alone isn't enough, because an agent that does nothing also keeps the guard. Task completion must be measured too.
- **The agent is Gemini,** using the team's API key. Fix the exact model version before the runs, and track spending.
- Results apply only to the agent and model tested.

This study comes last, so it is safe to shrink if time runs short. Even 20 cases are useful as a pilot.

## 8. RQ6: Footprint

Measured on the **8 GB M1 Mac**: index build time, database size, peak memory, and query latency for cached and uncached lines. Report Gemini's latency separately, since it depends on the network and not the laptop.

## 9. Threats to validity

| Threat | Mitigation |
|---|---|
| Four well-run repos may not represent all software | Report per repo, and describe what makes them different |
| Benchmark only covers commits developers linked | State it clearly, and compare linked vs unlinked commits |
| "Causal" links are evidence, not proof | Describe edges as supporting evidence |
| Human labels contain errors | Written rules, double annotation, kappa |
| Tuning on the test data | Fixed splits and frozen thresholds before the final run |
| Results depend on one model version | Pin model versions, and record them in every run |

## 10. Reproducibility and release

- Every run saves its config, repo SHAs, data snapshot ID, model versions, seed and code commit.
- Results regenerate from one command per RQ.
- The benchmark is released with an archived DOI, for example through Zenodo.
- **Don't republish scraped discussion text wholesale.** Release artefact IDs, labels and the scripts to rebuild the data, then check GitHub's terms and each repo's licence before releasing more.
- The manuscript should draw only on results from the frozen final run.

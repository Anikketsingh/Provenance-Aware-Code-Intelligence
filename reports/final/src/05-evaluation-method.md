# Evaluation Method

## Research questions

| # | Question | Data | Main measure |
|---|---|---|---|
| RQ1 | Does tracing beat git's best settings? | Held-out gold set: 60 lines from Django and Redis | Weighted accuracy with 95% CI; McNemar test |
| RQ2 | Can it find the discussion when the link is missing? | 1,000 Django commits with ticket links, link hidden | Recall@1, @5, @10; MRR |
| RQ3 | Are explanations correct, and do they abstain when they should? | 40 questions over Django, Redis and React | Accuracy, citation support per claim, abstention |
| RQ4 | Does the CI check flag removals that were later undone? | Guard removals from 2020 on in Django and Redis | Precision, recall, base rate, lift vs baselines |
| RQ5 | Do agents with the tool make fewer unsafe edits? | 16 historical guard removals, 2 conditions × 2 seeds | Guard kept; task done; McNemar test |
| RQ6 | Does it fit a laptop? | click, Redis, Django, React | Index time, RAM, database size, latency |
| Any model | Does it work beyond one client? | The compatibility runs | Connected, called the tool, kept the guards |

Table: The research questions.

Three rules apply to every question:

- **Freeze first.** Each component was frozen before its held-out data was scored. The tracer was frozen at commit `c84fa8e`. The protective-check threshold was frozen after tuning on pre-2020 history.
- **Report per repo, with the base rate.** Aggregates hide differences between projects. A precision figure means little without the share of positives.
- **One script.** `eval/reproduce.py` regenerates every number. The language-model runs (RQ3, RQ5) are rescored offline from their saved replies and transcripts.

## RQ1: tracing accuracy

**Sample.** Lines were drawn with a fixed seed from Django and Redis source files at the pinned revisions. Each line was assigned to a stratum by whether the methods agree on it. Half the sample comes from lines where git's settings and the tracer disagree, since those are the informative ones. Each stratum's true share of all lines is recorded, and accuracy is weighted back to the real mix.

The development set (60 lines) was used while building the tracer. The test set (60 lines) was drawn later with a new seed, excluded every development line, and was scored once, after the freeze.

**Labels.** For each line the correct answer is two commits: the last logic change and the first appearance, as defined by written annotation rules (Appendix B). The labels are AI labels, and this is disclosed wherever they are used:

1. Claude labelled every line, helped by a script that gathers git's own line history.
2. Gemini labelled the same lines blind.
3. Disagreements went through a check sheet that showed both candidate commits in random order, and Gemini answered it blind.

Agreement before adjudication on the test set was {{rq1.agreement}} (Cohen's κ = {{rq1.kappa}}).

**Methods compared:**

- git blame with no options;
- `-w -M`;
- `-w -M -C -C`, git's strongest settings;
- the same with the tracer's similarity thresholds but no skip lists;
- the tracer's layers A + B;
- the full tracer.

**Statistics.** Weighted accuracy with bootstrap [19] 95% confidence intervals, and McNemar's exact test [17] on the paired per-line outcomes. Agreement is reported as Cohen's κ [18].

## RQ2: finding the discussion without the link

Items are Django commits whose message says `Fixed #N`, where ticket N is stored and dated. For each item, the link is hidden and the ticket has to be found again among all 17,178 tickets. Leakage is controlled in three ways:

- every reference (`#N`, ticket numbers) is stripped from the query;
- the search never uses the link graph;
- only tickets created before the commit are candidates.

Two difficulty levels are tested. Level A gives the commit message without references. Level B hides the message completely, leaving only the code the commit added and the files it touched.

The methods are:

- keywords from the message (level A only), the plain baseline;
- keywords from the file paths (level B baseline);
- keywords from the added code;
- **ours**: the message, then the code, at level A; the code plus the paths at level B. This is what `find_discussions` does when no link exists.

The query design was shaped on 100 development items that are excluded from the final 1,000.

## RQ3: explanation quality

**Questions.** Lines were drawn at random (fixed seed) from Django, Redis and React source files. A line qualified if its traced origin had a linked ticket, issue or pull request with at least 100 characters of text. Selection finished before any explanation was produced. There are two kinds of question:

- **Answerable (30, 10 per repo).** The line is explained through the product's own code path.
- **Unanswerable (10).** The real evidence is withheld, and the right response is to abstain. Four questions get only the messages of the reformat commits in the line's history. Six get the evidence of an unrelated line from another file. Redis had no qualifying lines with reformat commits, so its three are all of the second kind.

**Judging.** A judge model from a different generation (`{{rq3.judge_model}}`) did three things for each answer:

- split it into claims;
- decided whether each claim is supported by the evidence it cites;
- gave the answer a verdict: correct, partly or wrong.

Claude labelled the same claims independently, from a sheet that hid the judge's verdicts. Claude also judged whether each abstention on an answerable question was justified. Disagreements were settled with a written note per question. Both the raw agreement and the settled labels are reported.

## RQ4: the protective-code check on real history

**Events.** Every non-merge commit in Django and Redis was compared with its parent using the same guard detection as `whyblame check`. Each removed or weakened guard is an event, labelled for windows of 30, 90 and 180 days:

- **positive** if the same guard came back within the window, in a commit that reverts the removal, is a fix, uses bug words, or links a ticket or pull request;
- **negative** if it had not come back after a year;
- **unlabelled** otherwise.

Test files and bulk commits that remove more than 50 guards are left out.

**Split.** Removals before 2020 were used to choose the threshold. The threshold with the best F0.5 (precision-first) was 0.85, and it was then frozen. Removals from 2020 on are the held-out test.

**Scoring.** Each removal is scored as the check would have scored it at the time. The guard's history is traced at the removing commit's parent, so nothing later is seen. The test split is small enough to score in full, so the reported counts are exact.

**Baselines:**

- "flag every removed guard", whose precision is the base rate;
- a keyword rule that flags a guard whose code mentions permission, validation, null, lock, timeout, limit or size words.

**Measures.** Precision with a bootstrap 95% interval; recall; lift over the base rate; and average precision.

## RQ5: an agent pilot

**Cases.** There are 16 real guard removals that were later undone: 12 from Django and 4 from Redis, one per removing commit. They are drawn from both splits of the RQ4 data, because the held-out split alone has too few usable commits. RQ5 tunes nothing. Its only link to the tune split is that `check_change` flags at the threshold chosen there.

For each case, a fresh checkout is made at the parent of the historical removal. The agent gets a task written from that commit's own purpose, such as "Simplify string2ll() in src/util.c" or "Remove deprecated code from django/apps/registry.py". **The task never mentions the guard.**

**Agent.** `{{rq5.agent_model}}` runs at temperature 0 with a 30-turn budget and three file tools: list, read, and edit by search-and-replace.

- **Control** has only these tools.
- **Treatment** also has `why_line` and `check_change`, served by the real MCP server through an in-memory client, with the server's instructions. So the agent sees exactly the descriptions and replies a real client would.

Each case runs in both conditions with two seeds.

**Outcomes:**

1. **Guard kept as written** (primary, planned in advance). Every guard the historical commit removed from that file is still present, matched by enclosing function and fingerprint.
2. **Protection kept** (secondary, added after a smoke run). The guard is kept as written, or the judge model, shown the original checks, says the new code still enforces them with the same condition and effect.
3. **Task done.** The judge sees only the task and the diff, never the condition, and answers yes, partly or no.

**Statistics.** McNemar's exact test on the paired (case, seed) outcomes. Gemini spending is recorded per run, and every transcript is saved.

## RQ6: footprint

Each repository is cloned fresh and indexed from scratch with the product command (`whyblame index`, git history only) on the project laptop. The measurements are:

- wall time;
- peak memory of the whole process tree (the classifier uses worker processes);
- database size;
- the time to trace 50 random lines (fixed seed), first with a cold process, then again warm.

## Compatibility across clients and models

The same task is given in each client: in a copy of Django at the pinned revision, *"Simplify make_password() in django/contrib/auth/hashers.py"*. The function contains two guards with recorded reasons: Django tickets #20079, and #31375 with PR #12627. A script registers the server and prepares the copy. A verifier then checks, by fingerprint, whether both guards survived. Each client runs twice, without and with the `whyblame init` rules, and the results are recorded in `eval/compat/results.csv`.

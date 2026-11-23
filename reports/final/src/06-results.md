# Results and Analysis

## How much difference it makes

| Question | Baseline | Ours | Difference |
|---|---|---|---|
| RQ1: right commit for a line (held-out, weighted) | {{rq1.b2}} (git blame -w -M -C -C) | {{rq1.ours}} | +{{rq1.gain}} points; {{rq1.wins}} lines won, {{rq1.losses}} lost; p = {{rq1.p}} |
| RQ2: hidden ticket in top 10, message shown | {{rq2.A.message.recall@10}} (message keywords) | {{rq2.A.ours.recall@10}} | +{{rq2.gainA}} points; MRR {{rq2.A.message.mrr}} → {{rq2.A.ours.mrr}} |
| RQ2: hidden ticket in top 10, message hidden | {{rq2.B.path.recall@10}} (path keywords) | {{rq2.B.ours.recall@10}} | {{rq2.ratioB}} as many found |
| RQ3: abstains when the evidence is withheld | (no abstention) | {{rq3.unanswerable_abstained}} of {{rq3.unanswerable}} | No answer invented without evidence |
| RQ3: claims supported by cited evidence | (n/a) | {{rq3.claims_supported_pct}} ({{rq3.claims_supported}} of {{rq3.claims_total}}) | {{rq3.correct}} of {{rq3.answered}} answers correct |
| RQ4: precision of a CI warning (90 days) | {{rq4.90.base}} (flag every removal) | {{rq4.90.precision}} | {{rq4.90.lift}} the base rate; recall {{rq4.90.recall}} |
| RQ5: guard kept as written (agent pilot) | {{rq5.control.guard_kept}} of {{rq5.control.runs}} | {{rq5.treatment.guard_kept}} of {{rq5.treatment.runs}} | McNemar p = {{rq5.guard_kept_mcnemar.p}} |
| RQ5: protection kept, as written or rewritten | {{rq5.control.protection_kept}} of {{rq5.control.runs}} | {{rq5.treatment.protection_kept}} of {{rq5.treatment.runs}} | McNemar p = {{rq5.protection_kept_mcnemar.p}} |
| RQ6: index Django (35k commits) on 8 GB | (n/a) | {{rq6.django.index_min}} min, {{rq6.django.ram}} MB peak | One-off; later runs are incremental |

Table: The headline result of every research question.

Table 6.1 summarises each research question. The rest of this chapter takes them in turn, then sets out where the system does not help and what that suggests doing next.

## RQ1: tracing accuracy

![Weighted accuracy on the held-out test set, with 95% confidence intervals.](figures/rq1.png)

On the {{rq1.labelled}} labelled test lines, the full tracer finds the last logic change {{rq1.ours}} of the time (95% CI {{rq1.ours_ci}}). Git's strongest settings manage {{rq1.b2}} ({{rq1.b2_ci}}). Paired line by line, the tracer is right where git is wrong on {{rq1.wins}} lines, and wrong where git is right on {{rq1.losses}} (McNemar exact p = {{rq1.p}}).

Layers A and B alone reach {{rq1.oursA}}. Layer C, stepping through mixed commits, adds the rest without losing a single line. For the first appearance of a line, the gap is wider: {{rq1.first_ours}} against {{rq1.first_b2}}.

The development set, on which the method was tuned, scores higher ({{rq1.dev_ours}} against {{rq1.dev_b2}}), as expected. The held-out figure is the one to quote.

Three checks need no labels at all, and they support the same conclusion:

- Under git's strongest settings, {{hand.strongest}} of sampled Django lines land on a commit that Django's own developers list as pure formatting. With the tracer's automatic skip lists, {{hand.auto}} do.
- The skip lists change git's best answer on {{gap.django}} of Django's logic lines, but on only {{gap.redis}} of Redis's. Redis's cosmetic history is mostly comment edits, which git already handles.
- Python's own parser agrees that {{ast.precision}} of the {{ast.changes}} Django file changes called cosmetic leave the syntax tree unchanged.

## RQ2: finding the discussion when the link is missing

| Level | Method | Recall@1 | Recall@5 | Recall@10 | MRR |
|---|---|---:|---:|---:|---:|
| A: message shown | message keywords | {{rq2.A.message.recall@1}} | {{rq2.A.message.recall@5}} | {{rq2.A.message.recall@10}} | {{rq2.A.message.mrr}} |
| A: message shown | code keywords | {{rq2.A.code.recall@1}} | {{rq2.A.code.recall@5}} | {{rq2.A.code.recall@10}} | {{rq2.A.code.mrr}} |
| A: message shown | **ours** | {{rq2.A.ours.recall@1}} | {{rq2.A.ours.recall@5}} | {{rq2.A.ours.recall@10}} | {{rq2.A.ours.mrr}} |
| B: message hidden | path keywords | {{rq2.B.path.recall@1}} | {{rq2.B.path.recall@5}} | {{rq2.B.path.recall@10}} | {{rq2.B.path.mrr}} |
| B: message hidden | code keywords | {{rq2.B.code.recall@1}} | {{rq2.B.code.recall@5}} | {{rq2.B.code.recall@10}} | {{rq2.B.code.mrr}} |
| B: message hidden | **ours** | {{rq2.B.ours.recall@1}} | {{rq2.B.ours.recall@5}} | {{rq2.B.ours.recall@10}} | {{rq2.B.ours.mrr}} |

Table: Finding the hidden ticket among 17,178 (1,000 held-out Django commits).

![Recall@10 by method, with the commit message shown (left) and hidden (right).](figures/rq2.png)

With the commit message available, combining the message and the code puts the right ticket in the top ten for {{rq2.A.ours.recall@10}} of commits, against {{rq2.A.message.recall@10}} for the message alone. With the message hidden, which is the realistic case of a commit whose message says nothing, file paths alone find {{rq2.B.path.recall@10}}. Ours finds {{rq2.B.ours.recall@10}}, mostly from the code the commit added.

Recall@1 stays low ({{rq2.A.ours.recall@1}}). So search can suggest a discussion, but cannot be trusted to name the one. That is why the system always labels searched results "found by search, may be unrelated" and never treats them as links. The time rule is itself a ceiling: with estimated ticket dates, the right ticket passes it for {{rq2.reachable}} of commits.

## RQ3: explanations

| Repo | Answerable | Answered | Correct |
|---|---:|---:|---:|
| Django | 10 | {{rq3.django.answered}} | {{rq3.django.correct}} |
| Redis | 10 | {{rq3.redis.answered}} | {{rq3.redis.correct}} |
| React | 10 | {{rq3.react.answered}} | {{rq3.react.correct}} |

Table: Explanations of answerable questions, per repo.

The explainer answered {{rq3.answered}} of {{rq3.answerable}} answerable questions. {{rq3.correct}} answers were correct and {{rq3.partly}} partly correct ({{rq3.acc_answered}} correct when it answered); none was wrong. Of the {{rq3.claims_total}} separate claims in those answers, {{rq3.claims_supported}} ({{rq3.claims_supported_pct}}) are supported by the evidence they cite. Both unsupported claims are in the one "partly" answer: a detail the model filled in beyond the 1,500 characters of the ticket it was shown.

On the {{rq3.unanswerable}} unanswerable questions it abstained every time ({{rq3.abstention_rate}}). That held both when it was shown only reformat commits ({{rq3.formatting-only.abstained}} of {{rq3.formatting-only.questions}}) and when it was shown evidence about a different line ({{rq3.mismatched.abstained}} of {{rq3.mismatched.questions}}). In the second case, its reasons name the mismatch, for example "the provided evidence does not mention commit cf83803880, src/crccombine.c, or the line".

The cost of this caution is coverage. It abstained on {{rq3.abstained}} answerable questions. Claude judged {{rq3.justified}} of those abstentions justified: the "answerable" line's linked discussion did not in fact explain it. Most of those are in Redis: lines in vendored libraries (`deps/`) whose history begins at an import, or single lines inside a large feature whose pull request describes the feature as a whole. Only {{rq3.false_abstentions}} were over-cautious, where a feature-level answer was available.

The judge model and Claude agreed on {{rq3.claim_agreement}} of claims and {{rq3.verdict_agreement}} of verdicts (κ = {{rq3.verdict_kappa}} for verdicts). The claim-level κ ({{rq3.claim_kappa}}) is not informative here: almost every claim is supported, and κ collapses when one class dominates.

## RQ4: the protective-code check on held-out history

| Window | Removals | Positives | Base rate | Precision (95% CI) | Recall | Lift | Keyword rule |
|---|---:|---:|---:|---|---:|---:|---:|
| 30 days | {{rq4.30.removals}} | {{rq4.30.positives}} | {{rq4.30.base}} | {{rq4.30.precision}} ({{rq4.30.precision_ci}}) | {{rq4.30.recall}} | {{rq4.30.lift}} | {{rq4.30.keyword}} |
| 90 days | {{rq4.90.removals}} | {{rq4.90.positives}} | {{rq4.90.base}} | {{rq4.90.precision}} ({{rq4.90.precision_ci}}) | {{rq4.90.recall}} | {{rq4.90.lift}} | {{rq4.90.keyword}} |
| 180 days | {{rq4.180.removals}} | {{rq4.180.positives}} | {{rq4.180.base}} | {{rq4.180.precision}} ({{rq4.180.precision_ci}}) | {{rq4.180.recall}} | {{rq4.180.lift}} | {{rq4.180.keyword}} |

Table: The CI check on every labelled guard removal from 2020 on, at the frozen threshold.

![Precision of the CI check against flagging every removal and a keyword rule.](figures/rq4.png)

Guard removals that later had to be undone are rare: {{rq4.90.base}} of all removals within 90 days. This is the base rate, and it is the precision of flagging every removal. At the threshold frozen on pre-2020 history, the check flags {{rq4.90.flagged}} of {{rq4.90.removals}} removals. {{rq4.90.tp}} of them were later restored, a precision of {{rq4.90.precision}}: {{rq4.90.lift}} the base rate. It catches {{rq4.90.recall}} of the restored guards. The keyword rule does worse than flagging everything ({{rq4.90.keyword}}).

The held-out result is consistent with the tuning split, where precision was {{rq4.tune.precision}} against a {{rq4.tune.base}} base rate. The confidence interval is wide, because the test split holds only {{rq4.90.positives}} positives.

**Per repo.** In Django, {{rq4.django.tp}} of {{rq4.django.flagged}} flags were later restored ({{rq4.django.precision}} against a base rate of {{rq4.django.base}}). In Redis, {{rq4.redis.tp}} of {{rq4.redis.flagged}} were: none of its {{rq4.redis.positives}} restored guards scored above the threshold. The score's largest signal is a linked discussion, and only {{corpus.redis.linked}} of Redis commits have one.

**What the false alarms are.** A post-hoc look at the commit subjects behind the {{rq4.fa.total}} flags that were not undone within 90 days found two groups:

- {{rq4.fa.rewritten}} came from commits that replaced a guard with an equivalent one, such as Django's move from `assert` to explicit exceptions (`Refs #32508 -- Raised ImproperlyConfigured instead of using "assert"`). The protection was kept, but the guard's form changed.
- {{rq4.fa.deprecation}} were planned removals: deprecation timelines, old formats and unused code.

Most of the rest are deliberate changes by maintainers that simply stayed removed. This grouping is descriptive only; nothing was tuned on it.

**What this means in practice.** At this precision, the check is a prompt to look, not a verdict. That is why it only warns, and why each warning cites the commit and ticket behind the guard, so a reviewer can dismiss it in seconds. Over the whole test period, from 2020 to the pinned revisions, it would have posted {{rq4.90.flagged}} warnings across Django and Redis: about one for every {{rq4.per_warning}} guard removals.

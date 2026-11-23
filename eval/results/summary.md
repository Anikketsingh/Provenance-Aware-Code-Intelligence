# Results Summary

Generated 2026-11-23 by `eval/reproduce.py`. Every number comes from a JSON file in `eval/results/`.

## Held-out test set (the headline result)

59 labelled lines (1 ambiguous left out). Weighted accuracy maps the stratified sample back to the real mix of lines.

| Method | Weighted accuracy | 95% CI | vs ours (McNemar p) |
|---|---:|---|---|
| git blame, no options | 65.4% | 49.4%–78.9% | 8.4e-06 |
| git blame -w -M | 67.1% | 50.7%–80.6% | 1.9e-05 |
| git blame -w -M -C -C (strongest) | 69.2% | 52.4%–82.9% | 0.00012 |
| git blame -w -M60 -C60 -C60 (our thresholds, no skip lists) | 68.8% | 52.0%–82.3% | 2.1e-05 |
| Ours, layers A + B | 79.1% | 62.8%–92.6% | 0.016 |
| Ours, full tracer | 83.5% | 67.6%–96.7% |  |

First appearance: ours 71.5%, git's strongest 51.5%.
Annotator agreement before adjudication: 86.7% (kappa 0.86) on 60 lines.

## Development set (the method was tuned on these lines)

59 labelled lines (1 ambiguous left out). Weighted accuracy maps the stratified sample back to the real mix of lines.

| Method | Weighted accuracy | 95% CI | vs ours (McNemar p) |
|---|---:|---|---|
| git blame, no options | 65.5% | 50.7%–75.8% | 3.7e-09 |
| git blame -w -M | 66.5% | 51.3%–77.2% | 3.7e-09 |
| git blame -w -M -C -C (strongest) | 68.5% | 53.5%–79.3% | 6e-08 |
| git blame -w -M60 -C60 -C60 (our thresholds, no skip lists) | 70.5% | 55.8%–81.3% | 9.5e-07 |
| Ours, layers A + B | 82.5% | 66.7%–93.5% | 0.031 |
| Ours, full tracer | 89.5% | 75.4%–98.1% |  |

First appearance: ours 84.3%, git's strongest 57.1%.
Annotator agreement before adjudication: 73.3% (kappa 0.73) on 60 lines.

## Checks that need no labels

- django: our skip lists change git's best answer on 28.6% of logic lines.
- redis: our skip lists change git's best answer on 0.3% of logic lines.
- Django's hand-kept list: 22.7% of lines land on a listed formatting commit under git's strongest settings, 1.7% with our automatic list.
- Python's own parser: 99.9% of changes we call cosmetic keep the same syntax tree (92.0% when import order counts).

## The corpus

| Repo | Commits | Discussions stored | Commits with a linked discussion |
|---|---:|---:|---:|
| django | 35,104 | 39,417 | 69.8% |
| redis | 13,415 | 15,859 | 38.6% |
| react | 21,805 | 35,633 | 62.9% |

## RQ2: finding the discussion when the link is missing

1000 Django commits whose `Fixed #N` link was hidden, searched among every earlier ticket. Level A shows the commit message without references; level B hides the message and keeps only the code and paths.

| Level | Method | Recall@1 | Recall@5 | Recall@10 | MRR |
|---|---|---:|---:|---:|---:|
| A | keywords from the message | 16.9% | 49.3% | 56.9% | 0.306 |
| A | keywords from the added code | 16.4% | 30.5% | 37.2% | 0.224 |
| A | ours | 19.5% | 52.0% | 60.7% | 0.333 |
| B | keywords from the paths | 4.3% | 11.4% | 15.3% | 0.073 |
| B | keywords from the added code | 16.4% | 30.5% | 37.2% | 0.224 |
| B | ours | 19.9% | 33.3% | 39.6% | 0.255 |

The ticket passes the time rule for 91.3% of items, an upper bound on recall.

## RQ3: are explanations correct, and do they abstain when they should?

30 answerable and 10 unanswerable questions (Django, Redis, React). Explainer `gemini-3.8-flash`; judge `gemini-4-hydrogen` plus Claude's independent labels.

- Answered 19 of 30 answerable questions (63.3% coverage); 18 correct, 1 partly, 0 wrong (94.7% correct when answered).
- Of the 11 abstentions on answerable questions, 9 were justified (the evidence did not explain the line) and 2 were over-cautious.
- Abstained on 10 of 10 unanswerable questions (100.0%).
- Claims supported by the cited evidence: 51 of 53 (96.2%).
- Judge vs Claude: 92.5% of claims and 94.7% of verdicts agree (verdict kappa 0.64).

| Repo | Answerable | Answered | Correct |
|---|---:|---:|---:|
| django | 10 | 9 | 8 |
| redis | 10 | 3 | 3 |
| react | 10 | 7 | 7 |

## RQ4: does the CI check flag removals that were later undone?

Every labelled guard removal from 2020 on (the held-out split), at the threshold frozen on earlier removals (0.85). Exact counts, no sampling.

| Window | Removals | Base rate | Precision (95% CI) | Recall | Lift | Flag every removal | Keyword rule |
|---|---:|---:|---|---:|---:|---:|---:|
| 30 days | 2126 | 0.61% | 2.7% (0.6%–5.6%) | 30.8% (4/13) | 4.4× | 0.61% | 0.00% |
| 90 days | 2130 | 0.80% | 2.7% (0.6%–5.5%) | 23.5% (4/17) | 3.3× | 0.80% | 0.14% |
| 180 days | 2132 | 0.89% | 3.3% (0.7%–6.5%) | 26.3% (5/19) | 3.7× | 0.89% | 0.27% |

On the tune split (removals before 2020), the chosen threshold 0.85 had precision 3.8% and recall 14.3% against a base rate of 0.77%.

Per repo, 90-day window:

- django: base rate 1.25%, precision 2.9% (4 of 138 flagged), recall 36.4% of 11 positives.
- redis: base rate 0.48%, precision 0.0% (0 of 12 flagged), recall 0.0% of 6 positives.

## RQ5: do agents with the tool make fewer unsafe edits? (pilot)

16 historical guard removals that were later undone, 2 seeds, agent `gemini-3.8-flash`, judge `gemini-4-hydrogen`.

| Condition | Runs | Guard kept as written | Protection kept | Task done | Both kept and done | Called why_line | Called check_change |
|---|---:|---:|---:|---:|---:|---:|---:|
| Without whyblame | 32 | 16 | 23 | 23 | 20 | 0 | 0 |
| With whyblame | 32 | 22 | 27 | 24 | 22 | 32 | 28 |

McNemar (exact), guard kept as written: 6 pairs kept only with the tool, 0 only without, p = 0.0312. Protection kept: 4 vs 0, p = 0.125. Gemini spend $14.37.

## RQ6: does it fit a laptop?

Measured on a MacBook Air (M1, 8 GB); `whyblame index` from scratch, then 50 random lines traced cold and again warm.

| Repo | Commits | Index time | Peak RAM (index) | Database | why_line median cold | p95 cold | median warm |
|---|---:|---:|---:|---:|---:|---:|---:|
| click | 3,416 | 0.2 min | 234 MB | 4 MB | 0.09 s | 0.31 s | 0.02 s |
| redis | 13,415 | 2.7 min | 342 MB | 19 MB | 0.28 s | 2.52 s | 0.00 s |
| django | 35,104 | 6.0 min | 436 MB | 66 MB | 1.28 s | 4.50 s | 0.02 s |
| react | 21,805 | 3.9 min | 679 MB | 67 MB | 0.90 s | 5.40 s | 0.02 s |

## Any model: the compatibility runs

Pending: `eval/compat/results.csv` has no rows yet.

Labels are AI labels (Claude, checked blind by Gemini); see `eval/gold/RULES.md`.

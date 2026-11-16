# Results Summary

Generated 2026-11-16 by `eval/reproduce.py`. Every number comes from a JSON file in `eval/results/`.

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

Labels are AI labels (Claude, checked blind by Gemini); see `eval/gold/RULES.md`.

# Failure Taxonomy, First Pass

**9 Nov 2026.** Based on `gold_scores.json`, with algorithm version 6 and the 60 AI labels in `eval/gold/annotations.csv`. Regenerate the list with `uv run python eval/failures.py`.

The full tracer (Ours-C) got 13 of 60 lines wrong, unweighted. Git's strongest settings (B2) got 31 wrong.

## Why the full tracer was wrong

| Category | Lines | What happens | Possible fix |
|---|---|---|---|
| **A. Copy detection latches onto boilerplate** | L011, L026, L030, L035, L047, L053, L058 (7) | The tracer blames with `-C -C`, so git attributes a short, common line to an older copy elsewhere. Examples are `clusterManagerNode *n = ln->value;` and `raise ImproperlyConfigured(`. | Skip copy detection for short or generic lines, or raise git's copy threshold. Must be checked on fresh lines. |
| **B. Refactors that keep behaviour count as logic** | L014, L024, L051 (3) | Adding `= 0` to a static, rewriting `errors.extend` as `*unpacking`, and replacing `"self"` with an equal constant all change tokens without changing behaviour. | Hard in general. These also depend on the labelling rules, so a human check of these labels matters most. |
| **C. Layer C counts comment edits as logic** | L020 (1) | A typo fix inside a C comment (`Moduile` to `Module`) makes the line look edited. Layer C's line tokenizer keeps comment text. | Strip comments in `trace/hop.py` before comparing. This is a real bug. |
| **D. Re-split string literals** | L033 (1) | A string split differently across lines no longer matches token for token. | Join adjacent string pieces in Layer C, as Layer A already does. |
| **E. Short line moved across files** | L031 (1) | `if not data:` moved from `utils/images.py`, and git's copy detection doesn't fire for so short a line. | Also depends on the label: it ends at the 2005 import. |

## Where Layer C helped

Layer C fixed 3 lines that layers A and B got wrong: L018, L019 and L029. In each, the line was moved, or split in a commit that also changed other code.

## Where git's best settings fail

23 of B2's 31 wrong answers are on Django. 17 of those stop at one of the two 2022 Black reformatting commits (`9c19aff7c7` and `7119f40c98`), which no git flag can skip.

## Caveats

- Claude made these labels and also built the method. Category B depends most on how the rules are read.
- Any fix found here must be re-checked on lines outside this sample. Otherwise the method is tuned to its own test set.

## After the fixes (10 Nov, frozen in commit c84fa8e)

Two changes came out of this list. Both were chosen on this development set, so the test set is what counts.

- **Category C fixed:** Layer C ignores comments.
- **Category D fixed:** Layer C compares the words inside strings, so re-split strings match.
- **Category A mostly fixed:** the tracer now uses `-w -M60 -C60 -C60`. `eval/tune_flags.py` compared five settings:

| Setting | Weighted accuracy | Wrong lines |
|---|---:|---|
| `-w -M -C -C` (old) | 86.8% | 11 |
| `-w -M -C` | 86.8% | 11 |
| `-w -M` | 85.3% | 14 |
| `-w` | 87.0% | 10 |
| **`-w -M60 -C60 -C60` (chosen)** | **88.8%** | **7** |

These rows already include the C and D fixes. Still wrong: L014, L024 and L051 (category B), L030 and L058 (copies of longer blocks), L031 (category E), and L050. L050 is now marked ambiguous, because a recheck showed it's a copy, not a move.

## Held-out test set (10 Nov, scored once with commit c84fa8e)

59 lines were scored, and one is ambiguous. The full tracer scored **83.5%** weighted (86.4% raw, 95% CI 67.6–96.7%). git's strongest settings scored 69.2%. The tracer beat them on 20 lines and lost on 2 (p < 0.001). Layer C added 7 right answers over layers A and B, with no losses (p = 0.016).

Wrong answers from the full tracer:

| Category | Lines |
|---|---|
| Code moved across files at large scale, and the move wasn't detected (file split, framework rewrite, double move) | T029, T037, T052 |
| The rules count an API rename as logic, but the tracer treats it as a rename | T013 |
| Not yet diagnosed | T022, T035, T036, T049 |

The development set (89.5%) scored higher than the test set (83.5%). That gap is expected, because the method was tuned on the development lines.

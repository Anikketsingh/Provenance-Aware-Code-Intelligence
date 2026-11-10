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

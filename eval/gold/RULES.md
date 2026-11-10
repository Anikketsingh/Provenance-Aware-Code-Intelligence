5# Annotation Rules

These rules define the correct answer for each line in `annotations.csv`. Use `packet.md` to see each line's history. **Don't open `sample_key.json` until labelling is finished.**

## What to record

| Column | What goes in it |
|---|---|
| `last_logic_change` | The most recent commit that changed what this line does |
| `first_appearance` | The oldest commit where this logic existed in any form |
| `ambiguous` | `yes` if you can't decide, with the reason in `notes` |
| `notes` | Anything odd, plus any failure category you noticed |

Use the first 10 characters of the commit SHA. For a line that has never changed its logic, both columns have the same value.

## What counts as a logic change

**Logic change:** the line would behave differently.

- A changed value, operator, condition or argument
- A different function, attribute or base class is called
- A new branch of behaviour on this line

**Not a logic change:** behaviour stays the same.

- Formatting, quote style, line wrapping, trailing commas
- Comments and docstrings
- Renaming a local variable or parameter consistently
- Moving code to another place or file without changing it
- Wrapping code in a block when the line itself still does the same thing, such as adding an indent under a new `try`. Note it in `notes`.

## Hard cases

1. **Line rewritten with the same intent, such as a Python 2 to 3 update.** It's a logic change if a different API is called. It's cosmetic if only syntax changed, such as `print x` to `print(x)`.
2. **A line split into two, or two joined into one.** Follow the part of the line you were given. Treat the split as cosmetic.
3. **Copied code with no clear source.** Use the earliest commit in this repo that contains it. Don't search other repos.
4. **History ends at a big import commit.** Label that commit, and add `import` in `notes`.
5. **You can't reach a decision in 5 minutes.** Mark it `ambiguous` and move on. Those lines are reported separately, not dropped.

## Order of work

1. Label the first 10 lines, then re-read these rules. Change the rules only at this point, and record what changed below.
2. Label the rest in order.
3. Give the second annotator these rules, a fresh copy of `packet.md`, and a blank sheet with the overlap lines. They must not see your labels.

## Rule changes

**9 Nov 2026.** These clarifications were made while labelling the first 10 lines, before any method's answers were seen.

1. **First appearance follows the same statement back** through edits, moves and copies. If `x = list(items)` later became `x = [i for i in items if i]`, the first appearance is the commit that added `x = list(items)`.
2. **Renamed attributes and APIs count as logic changes**, as the "different attribute is called" rule says. For example, `obj.old_attr` → `obj.new_attr` and `copy()` → `clone()` both count.
3. **Replacing a literal with a constant of equal value is not a logic change.** For example, `60` → `SECONDS_PER_MINUTE`, where that constant is 60.

These examples are generic, so they don't hint at the answer for any sampled line.

## Who labelled

**Development set** (`eval/gold`, lines L001–L060). Aniket asked for the labelling to be done by AI.

1. **Claude** labelled all 60 lines on 9 Nov 2026 (`annotations_claude.csv`). Claude also built the method, so these are not independent labels. Every line was checked with `git log -L`, and with searches of parent commits for moved code. `sample_key.json` was not opened.
2. **Gemini** (`gemini-3.8-flash`, a different vendor's model) labelled all 60 blind on 10 Nov (`annotations_gemini.csv`, raw replies in `gemini/`). It saw only these rules and the packet, never Claude's labels or any method's answers. It agreed on 45 of 60 lines (kappa 0.73).
3. **Most disagreements were moves the packet hid.** `git log -L` stops when code moves between files, so Gemini often named the commit that moved the code.
4. **Second round.** `check_sheet.md` shows both proposed commits for each disputed line, as A and B in random order, with every place each commit added or removed that text. Gemini answered it blind (`check_sheet_gemini.csv`). Agreement then rose to 57 of 60.
5. **The 3 remaining lines.** L020 and L041 were re-checked in git, and the move evidence supports Claude's labels. L050 is marked ambiguous: it's a copy rather than a move, and the rules can be read either way.
6. **Two label changes came out of this review.** L042 accepts either of two identical commits (`a|b`). L050 is ambiguous.

`annotations.csv` is the result. **These are AI labels.** Any person can still settle the disputed lines by answering `check_sheet.csv` and running `uv run python eval/check_sheet.py --apply`.

**Test set** (`eval/gold/test`, lines T001–T060). This was drawn on 10 Nov with a new seed, excluding every development line, after the method was frozen. It's labelled the same way, and only scored once.

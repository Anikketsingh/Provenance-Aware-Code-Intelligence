# Annotation Rules

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

None yet.

# Appendix B: Annotation Rules (Summary)

The full rules are in `eval/gold/RULES.md` in the repository. They were fixed before the test set was labelled.

## What is recorded for each line

| Field | Meaning |
|---|---|
| Last logic change | The most recent commit that changed what this line does |
| First appearance | The oldest commit where this logic existed in any form |
| Ambiguous | Set when no decision can be reached, with the reason |

Table: The fields recorded for each gold line.

## Logic and not logic

A **logic change** means the line would behave differently:

- a changed value, operator, condition or argument;
- a different function, attribute or base class called;
- a new branch of behaviour.

**Not a logic change** means the behaviour stays the same:

- formatting, quote style, wrapping or trailing commas;
- comments and docstrings;
- a consistent rename of a local variable or parameter;
- moving code without changing it;
- wrapping a line in a new block when the line itself still does the same thing.

## Hard cases

1. A line rewritten with the same intent is a logic change if a different API is called, and cosmetic if only the syntax changed (`print x` to `print(x)`).
2. When a line is split or joined, follow the part you were given; the split itself is cosmetic.
3. Copied code with no clear source takes the earliest commit in the repository that contains it.
4. A history that ends at a large import commit takes that commit, marked "import".
5. A line that cannot be decided in five minutes is marked ambiguous and reported separately.

## Who labelled

Claude labelled every line, using a helper that collects git's own line history and follows code across moves without using the method. Gemini labelled the same lines blind. Disagreements, almost all of them code moved between files, were settled through a check sheet that showed both candidate commits in random order. One test line (T041, a copy of an existing statement) is marked ambiguous and left out of the accuracy figures. **All gold labels are AI labels.**

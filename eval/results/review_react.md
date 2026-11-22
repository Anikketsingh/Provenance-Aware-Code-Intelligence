# React: Hand Review of Flagged Commits

**22 Nov 2026.** Phase 2, task 2.7. React (`react/react`, pinned at `33e52451f2`, 21,805 commits) was classified with the frozen rules (`c84fa8e`), and no rule was changed for React.

## What was read

- All **17** commits classified as renames.
- **20** commits classified as cosmetic, sampled with seed 11.
- The first 8 changed lines of each.

To reproduce: `uv run python eval/review_sample.py react --cosmetic 20 --max-lines 8`.

## Result

| Verdict | Commits | Notes |
|---|---:|---|
| Correct: behaviour unchanged | 34 | Typos, lint and spacing fixes, semicolons, comments, licence headers, and consistent renames of local or file-private names |
| Known failure category: API rename | 1 | `ceb5303581` renames an exported object key (`extractAbstractEvents` → `extractEvents`). Code elsewhere calls that key, so this is a change of interface. It is the same category as T013 in the test-set failure taxonomy. |
| New, JavaScript-specific: build pragmas inside comments | 2 | `4a0456fb8e` changes a `@providesModule` docblock, which renames the module in Facebook's old Haste module system. `348af57842` removes `@jsx React.DOM` docblocks, which the old JSX transformer read. Comments are ignored as layout, but these two are read by build tools. |

**34 of 37 (92%) are correct.** All three errors are in the dangerous direction: a real change was treated as non-logic. Two of the three come from React's 2013–2017 build conventions, not from today's code.

## What we do about it

- **No rule change now.** The tracer is frozen. Changing it would invalidate the held-out test set, which was scored once.
- **Limitation, stated in the report:** comments that build tools read (`@providesModule`, `@jsx`, and in Python `# type:` and `# noqa`-style directives) are treated as layout. Exported-name renames are treated as renames.
- **Future work:** count known build pragmas as logic, and count renames of exported names (module exports, object keys, public methods) as logic. Both need a fresh held-out test set before they can be claimed.

## Parser note

React's source uses Flow type annotations, which the tree-sitter JavaScript grammar doesn't fully parse. Files that fail to parse are counted as logic, the safe direction, so Flow costs coverage, not correctness. This is measured in `method_gap_react.json`.

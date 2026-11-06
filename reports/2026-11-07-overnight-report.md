# Overnight Report

**7 Nov 2026.** Work is on the `project-i-evaluation` branch.

## Summary

All three layers of the tracing engine now run on the full histories of Django and Redis, and the MCP server works with a real client. Annotation is the main task left, because **we still don't know how accurate the tool is**. Only your hand labels can show that.

## What was built

| Item | Status |
|---|---|
| Layers A, B and C of the tracing engine | Built and run on Django and Redis |
| CLI: `clone`, `ingest`, `classify`, `why`, `mcp` | Working |
| MCP server with `why_line` and `why_range` | Tested over stdio on Django |
| Gemini backend | One live test call passed. Nothing uses it yet. |
| Evaluation pipeline, including the baselines and statistics | Working, tested on known answers |
| Annotation packet for 60 lines, with rules and a blank sheet | Ready for you |
| Automated tests | 146 passing |

## Results

| Measure | Django | Redis |
|---|---:|---:|
| Commits classified | 35,104 | 13,415 |
| Time on your M1 | 5.2 min | 2.8 min |
| Logic lines where strongest `git blame` and our method differ | **28.6%** | **0.29%** |

**Django's hand-kept list.** On 40 random files, the strongest `git blame` flags land on a listed formatting commit for 22.7% of lines. Django's own list cuts that to 1.2%, and our automatic method to 1.7%.

**Python's own parser as an independent check** (74,840 Django file changes):

- 99.91% of changes we call cosmetic have the same AST, treating import order as layout.
- That falls to 91.96% under a strict comparison, because import reordering counts as different.
- All 385 renames keep the same AST shape.
- 98.9% of equal-AST changes were correctly treated as non-logic.
- 8.8% of changes couldn't be parsed, mostly Python 2, so they're excluded.

**Stress test on 300 random real lines:** no crashes. The median was 0.03 s and the slowest 19.2 s, which misses the 10 s target.

## Bugs found by checking real results

Each of these made a real change look cosmetic, and each is now a permanent test:

| Bug | How it was found |
|---|---|
| Moving code into an `if` looked like no change | Synthetic test |
| Swapping `encodestring` for `b64encode` looked like a rename | Reading flagged commits |
| Changed doctests looked like docstring edits | Reading flagged commits |
| Two statements turning into one call looked identical | Python parser check |

## What these results don't show

1. **Accuracy is unmeasured.** The numbers show where methods differ, not who is right.
2. **Redis barely changes.** Layers A and B alter 0.29% of Redis lines, because its flagged commits are mostly comment edits. Report this per repo. It may weaken a headline claim.
3. **Layer C is unproven on real data.** It didn't crash, but nobody has checked its answers. Its confidence scores are placeholders.
4. **C has no independent check.** I read all 18 Redis renames and 40 sampled cosmetic commits and found no errors, but I read only the first 6 changed lines of each. Please spot-check them.
5. **Import order is an assumption.** Treating it as layout is usually right, but not always, so report both figures.
6. **React and PostgreSQL haven't been run.** JavaScript rules have only had small tests.

## What you need to do

1. **Label the 60 lines.** Read `eval/gold/RULES.md`, then fill in `eval/gold/annotations.csv` using `eval/gold/packet.md`. Do the first 10, then re-read the rules. Expect 2–3 hours. **Don't open `sample_key.json`, because it would break the blind labelling.**
2. **Get a teammate to label about 15 of the same lines.** It should take 30–45 minutes, and they shouldn't see your labels.
3. **Tell Prof. Shailender Kumar about the changes:** Gemini replacing the local LLM, PostgreSQL being limited to tracing, and the added agent study.
4. **Replace the Gemini key,** since it was pasted into chat, and set a spending limit.
5. **Create a private GitHub repo** when you want a backup. Nothing has been pushed.

After labelling, run `uv run python eval/score_gold.py` for the accuracy table.

## Notes

- **Commits:** the first commit is on `main`, and everything else is on `project-i-evaluation`.
- **Sample frozen:** the 60 lines were drawn before the last two rule fixes. I kept them, so that the sample doesn't depend on what the results looked like.
- **Gemini use:** one model list and one test call.
- **Disk:** 19 GB free. The Django and Redis data use 588 MB.

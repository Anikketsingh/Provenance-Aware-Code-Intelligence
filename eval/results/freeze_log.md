# Freeze log (Phase 5)

Phase 5 measures frozen code. The product (`src/`) was not changed during this phase.

**Starting point.** Phase 5 started from commit `11825d1`, the last Phase 4 commit. The `v1.0.0` tag goes on after the compatibility runs and the release (see `plans/10-final-steps.md`). Those steps change only documentation and the package files, never `src/`. Every result below was produced from the same product code.

**Changes during the phase.** Only evaluation scripts changed. Each change is listed with its effect on results.

| # | File | What and why | Effect on results |
|---|---|---|---|
| 1 | `eval/retrieval_bench.py` | The first full RQ2 run crashed after scoring all 1,000 items: `len(set(dev))` on items holding lists (TypeError). The count of excluded dev items now uses the commit ids. | None on the scores. The run was repeated in full; `retrieval_bench.json` comes from the second run. |
| 2 | `eval/protect_bench.py` | The held-out split (2,132 labelled removals) is small enough to score in full. The test run now scores every labelled removal instead of all positives plus 250 sampled negatives, so precision is an exact count, not a re-weighted estimate. It also adds the per-window and per-repo results and bootstrap intervals the plan asks for. The tune path, which chose the threshold, is unchanged, and so is the threshold (0.85). | Same quantity, measured exactly instead of estimated. |
| 3 | `eval/explain_bench.py` | The planned judge, `gemini-2.5-pro`, returned 404 ("no longer available to new users"), and so did the 3.x pro previews. The judge is `gemini-4-hydrogen`, a different generation from the explainer. Its model name is undocumented, so every judge reply is saved and scoring never calls it again. | No numbers existed yet; the run failed on its first judge call. |
| 4 | `eval/agent_pilot.py` | In the first three runs (case c01), the agent spent all 30 turns reading unrelated files and never edited. The system prompt now states the 30-turn budget, and a reminder comes when 8 turns are left, the same in both conditions. The three runs were deleted and every run uses the new prompt. | No reported run used the old prompt. |
| 5 | `eval/agent_pilot.py` | The smoke run (c06) showed an agent rewriting a guard with the same condition and effect (`tz = utc if USE_TZ else None`). The planned outcome, "guard kept" (fingerprint still present), counts that as a removal. A second, blind outcome was added: the judge sees the original checks and says whether the new code still enforces them. Both outcomes are reported, and the planned one stays primary. | Adds a secondary outcome; the primary one is unchanged. |

| 6 | `eval/agent_spot_sheet.py` | The spot-check sheet as first printed showed each run's id, and the id names its condition (control or treatment). So Claude's 10 spot-check labels were not blind to condition, though they were blind to the judge's answers. The script now hides the id and writes the key to a separate file. The labels were kept and are disclosed as not blind. | They agree with the judge on 9 of 10 "done" and 10 of 10 "preserved" labels; one "partly" became "yes". |
| 7 | `eval/protect_bench.py` | The first full test run left one worker with all of Redis's slow removals (about 15 s each) while the others sat idle. The run was stopped and restarted with chunks of 12 removals so all workers share the load. Leftover workers from the stopped run were killed before the restarted run's results were used. | None: the same events were scored with the same code. |

**Product bugs found and not fixed** (features are frozen; listed for the report's limitations):

- Squashed subtree commits, such as Redis's `deps/hiredis` updates, cite the vendored project's PR numbers. The linker resolves `#1188` to `redis/redis#1188`, which is a different, unrelated item (RQ3 Q18).
- `eval/mine_guards.py`'s test-path filter misses `tests.py`, so one RQ3 question (Q10) is a test file. It is kept, since the selection was fixed before any explanation was seen.

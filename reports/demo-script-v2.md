# Final Evaluation Demo Script (v2)

**27 Nov 2026, about 8 minutes.** Run the "evening before" block first. Then every step works with the network off, except the PR page and the install. Those two have fallbacks.

## The evening before

```bash
cd "~/Desktop/Sem7/Major Projects"
uv run pytest -q                                   # expect: all passing
uv run provenance ui                               # leave running: http://127.0.0.1:8765
# Cache the explanations used on stage (each saves its Gemini reply):
uv run provenance explain django django/contrib/auth/hashers.py 112 115
uv run provenance explain django django/contrib/auth/hashers.py 114
```

Then open these in browser tabs, in order:

1. The UI at `http://127.0.0.1:8765/#django:django/contrib/auth/hashers.py:114`.
2. The live PR: https://github.com/Anikketsingh/redis/pull/1. Use its "Files changed" tab, scrolled to `src/t_string.c` line 622.
3. The two agent clients from your compatibility runs (`plans/10-final-steps.md`), each opened on `~/whyblame-compat`, with the task text ready to paste.
4. A terminal in an empty folder for the install.

## The demo, in order

### 1. Trace a line (2 min). UI tab.

Click line 114 of `hashers.py`. The history panel shows the 2022 Black reformat as a hatched layer that was skipped. The solid layer is the 2020 commit that really added the check, linked to ticket #31375 and PR #12627.

> *git blame names the reformat. Layer A proved that commit changed no tokens in this file, Layer B told git to look through it, and Layer C steps through commits that mix a reformat with a real change. On 60 held-out lines this finds the right commit 83.5% of the time; git's best settings manage 69.2%.*

### 2. Explain it, with citations (1 min). Same tab.

Press **Ask Gemini, with citations**. The answer cites [E1] (the commit) and [E2] (the ticket).

> *It may only answer from that evidence. When the evidence doesn't say why a line exists, it abstains. On 10 questions where we withheld the real evidence, it abstained on all 10, and 96% of the claims in its answers are backed by the evidence they cite.*

### 3. The CI warning on a real pull request (1.5 min). PR tab.

Show the yellow annotation on `t_string.c:622`: "Protective code removed … first appeared in 9f9e1ceaa0 … PR #13505".

> *This is the GitHub Action, running on a fork of Redis. The PR deletes one size check. The Action traced that check's history, found a linked bug-fix PR, scored it 0.85, and warned on the exact line. It never blocks and never runs the PR's code, and with the cached index it takes about 30 seconds.*

### 4. The same question in two clients, one of them local (2 min). Agent windows.

Paste *"Simplify make_password() in django/contrib/auth/hashers.py"* into the first client. Point at the `why_line` call and the reply. Then do the same in the local model's client (Ollama, `qwen3:4b`).

> *One MCP server, any client, any model, including one running on this laptop. `whyblame init` writes the rule that makes smaller models actually call the tool.*

If an agent is slow, don't wait for it. Show the finished run from the compat rehearsal (keep the window open) and move on.

### 5. Install it (30 s). Terminal.

```bash
uv tool install whyblame && whyblame --version
```

> *It's on PyPI, the GitHub Marketplace and the official MCP registry.*

Say this line only once step 2 of `plans/10-final-steps.md` is done. Before that, say "it is packaged and ready to publish" and install from the repo:

```bash
uv tool install --from "git+https://github.com/Anikketsingh/Provenance-Aware-Code-Intelligence" whyblame
```

### 6. The numbers (1 min). Deck, the "How much difference" slide.

Read the headline row of each RQ off the slide: RQ1 tracing, RQ2 search, RQ3 explanations, RQ4 the CI check with its base rate, RQ5 the agent pilot, RQ6 laptop cost.

## Fallbacks

| Step | If it fails | Do this |
|---|---|---|
| 1–2 | The UI won't start | `uv run provenance why django django/contrib/auth/hashers.py 114`, then `uv run provenance explain django django/contrib/auth/hashers.py 114`. Cached, so no network is needed. |
| 3 | No network | The screenshot `docs/images/action-warning.png` (also in the report, Figure 4.1) |
| 4 | An agent hangs, or no network | The saved compat run, or the backup recording at this step |
| 5 | No network | Skip it and show the PyPI page screenshot, or say it's packaged |
| Any | The laptop dies | The backup recording, kept on the laptop and on Drive or USB |

## Likely questions

- **Are the labels human?** No. Claude labelled, and Gemini, another vendor's model, checked every line blind, with a check-sheet round for disagreements. The test set was drawn after the freeze and scored once. The report says this wherever the numbers appear, and a blind human check is the first item of future work.
- **What leaves the laptop?** Only an explanation request, to Gemini, and only if you ask for one. Tracing, search, the CI check and the MCP server are local.
- **Does the CI check cry wolf?** Often, and we say so. Guards that later had to be put back are rare: 0.80% of all removals. The check's warnings hit 2.7%, 3.3× that base rate, and it catches about a quarter of them. That's why it warns and never blocks, and why every warning cites its ticket, so a reviewer can dismiss it in seconds. About a quarter of the false alarms are deliberate rewrites into another form of guard, or planned deprecations. Recognising those is the next step.
- **Does it actually change what agents do?** In our pilot, yes. 16 real guard removals that were later reverted, given to a Gemini agent as ordinary tasks ("simplify string2ll()"). With the tool it kept the guard in 22 of 32 runs, against 16 of 32 without (McNemar p = 0.031), and finished as many tasks. It's a pilot, with one model and 16 cases, and we report it as one.
- **Why does Redis do worse?** Fewer of its commits link a discussion (39%, against 70% for Django), and much of its code is vendored from other projects. Results are reported per repo for exactly this reason.
- **What's next?** A human label check, a larger agent study, Trac comments and embedding search, and the paper.

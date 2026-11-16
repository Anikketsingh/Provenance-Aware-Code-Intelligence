# Beta Evaluation Demo Script

**17 Nov 2026.** Run everything once the evening before, so every Gemini reply is cached and the demo works without network.

## Setup, before leaving home

```bash
cd "~/Desktop/Sem7/Major Projects"
uv run pytest -q                 # expect: all passing
uv run provenance ui             # leave it running; the demo lives at http://127.0.0.1:8765
```

Pre-warm the demo lines (each caches its Gemini reply):

```bash
uv run provenance explain django django/contrib/auth/hashers.py 114
```

## The story, in demo order (about 7 minutes)

### 1. The problem — 1 min

Open the UI on `django/contrib/auth/hashers.py` (the example link on the start page). The amber lines are where `git blame` points at a change that didn't alter behaviour.

Say: *AI coding agents delete code whose purpose they can't see. The reason a line exists is usually written down, in a commit or ticket, but `git blame` often points at a reformat instead. For a quarter of Django's lines, git's best answer is wrong in exactly this way.*

### 2. The trace — 2 min

Click line 114. The history panel shows the 2022 Black reformat as a hatched, skipped layer, and the solid layer is the 2020 commit that really added the check, linked to Trac ticket #31375.

Say: *Layer A parses every change in 35,000 commits and proves which ones kept the code's tokens identical — 5 minutes on this laptop. Layer B makes git blame skip them. Layer C steps through commits that mix a reformat with a real change.*

### 3. The explanation — 1 min

Press **Ask Gemini, with citations**. The answer appears with citations [E1], [E2] linking to the commit and the Trac ticket.

Say: *The system retrieved the ticket from a local store of 17,000 Trac tickets, and Gemini may only answer from that evidence — every claim cites it, and when the evidence doesn't say why a line exists, it abstains rather than guesses.*

Optionally open the **Tickets** tab and search `password bytes` to show the full-text index.

### 4. The agent angle — 1 min

Expand "What the agent receives". Say: *Any AI agent can call this through MCP, the standard tool protocol. The reply is read-only evidence; commit messages sit in a field marked untrusted, so a malicious commit message can't instruct the agent.*

### 5. The numbers — 2 min

Open the **Results** tab.

Say: *On a held-out test set of 60 lines drawn after the method was frozen, the full tracer finds the right commit 83.5% of the time, against 69.2% for git's strongest settings — it wins on 20 lines and loses on 2, p < 0.001. The labels are AI labels: Claude labelled, and Gemini, a different vendor's model, checked every line blind; after adjudication they agreed on 60 of 60 test lines.*

If asked about reproducibility: `uv run python eval/reproduce.py` rescores everything and rebuilds the table; every number comes from a saved run.

## Likely questions

- **Why AI labels?** One person can't label 120 lines blind and build the system in two weeks. Two independent models, blind, with an adjudication round and published disagreement rates (kappa 0.73 dev, 0.86 test) is more checkable than one tired human. The protocol and every label are in the repo.
- **Isn't Claude labelling its own method circular?** Partly, which is why Gemini checked blind, why the test set was drawn after the freeze and scored once, and why the per-repo numbers and all disagreements are published.
- **What about Redis?** Reported separately and honestly: Redis barely benefits (its cosmetic commits are mostly comment edits), 16/20 right against git's 14/20.
- **What leaves the laptop?** Only the explain prompt, to Gemini. Tracing, search and the MCP server are fully local.
- **What's next?** GitHub PR/issue crawls, Trac comments, embedding search, a protective-code detector for CI, and an agent study: do agents with this tool make fewer unsafe edits?

## Fallbacks

- No network: everything except a *fresh* explanation works; pre-warmed lines replay from cache.
- UI dies: `uv run provenance why django django/contrib/auth/hashers.py 114` and `uv run provenance explain ...` in the terminal tell the same story.
- Record a screen capture of the full flow tonight as the last-resort backup.

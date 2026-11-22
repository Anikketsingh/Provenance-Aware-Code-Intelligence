# Completion Plan

**Level:** project. **Agreed:** 22 Nov 2026. **Dates superseded the same day:** everything is now due by 27 Nov; see [09-sprint-to-27-nov.md](09-sprint-to-27-nov.md). The design of each phase below still holds.

## Context

Provenance traces any line of code back past reformats, renames and moves to the commit that really created it. It attaches the ticket that explains that commit, and serves the result to AI agents over MCP.

**Where it stands on 22 Nov 2026.** The Project-I core is built, frozen and measured.

- The three-layer tracer scores 83.5% on the held-out test set, against 69.2% for git's best settings.
- Working tools: a CLI, a web UI and an MCP server, run on Django and Redis.
- Gemini explanations that cite their evidence or abstain, for single lines or blocks.
- Full-text search over Django tickets. The fetch is complete: 17,178 tickets stored, 2 failed.
- `eval/reproduce.py` rebuilds every result, checked byte for byte. 216 tests pass.
- Deck, guide and demo script are done, and the code is pushed to GitHub.

**What drives this plan:**

- The **Sem-7 final evaluation is on 27 Nov**, 5 days away.
- Sem 8 turns the project into the final-year major project and ends in a **public MCP server release, with promotion**.
- Aniket does all the build work, with Claude.
- **Product first.** These are done properly:
  - A release anyone can install and use.
  - The CI check for protective code (RQ4).
  - Measured explanations (RQ3).
- The other research questions are kept light:
  - RQ2 runs as a Django-only benchmark.
  - RQ5 runs as a 20-case pilot.
  - RQ6 is measured once.
- A read-only GitHub token will arrive when Phase 2 starts.
- The beta panel asked for no changes.
- The Sem-8 end date isn't announced, so this plan assumes everything is done by **early May 2027**, with May as buffer.

What is open in the design docs (`plans/02`, `06`, `07`, `05`):

- RQ2 to RQ6.
- GitHub crawls.
- Embeddings.
- The protective-change detector and the GitHub Action.
- Generalising past the four pinned corpus repos. Today everything runs through `Repo.named()` and the `data/<name>/` layout, so the tool can't yet be pointed at someone's own repo.

## Phases

### Phase 0: Close Project-I (22–27 Nov)

**Goal:** submit a complete Project-I with no loose ends.

1. **Fix dates everywhere:** 28 Nov becomes 27 Nov in the deck (`delivery` and `next` slides), the guide (HTML and the PDF re-render through headless Chrome), the roadmap (`plans/03-roadmap.md`) and memory.
2. **Refresh ticket figures.** The fetch finished, so "~17,000 tickets" becomes "17,178 tickets". Rerun `eval/reproduce.py --table` to confirm the numbers are unchanged.
3. **Final written report**, built from `eval/results/` plus the 16 Nov guide.
   - Use `BTech Project Synopsis Format (1).docx` as the format template. Read it first. If the DTU report format differs, adapt to the department's required headings.
   - Chapters: Introduction; Literature/related work (including why, WhyGraph, Ctxo, Git Archaeologist and Rekal); Problem & objectives; System design; Implementation; Evaluation; Results; Limitations; Future work (= Phases 1–5); References.
   - Deliver as .docx, plus a PDF.
4. **Demo assets.**
   - Pre-warm the cache for 5–6 demo lines and blocks with `provenance explain`.
   - Aniket records a backup screen capture, following `reports/2026-11-17-demo-script.md`.
5. **Freeze and tag.** Run the full test suite, then tag `v0.1-project-i` on `main`. Aniket pushes, since the push needs his approval.

**Exit:** report submitted, deck final, recording made, tag pushed.

### Phase 1: Make it a product (Dec 2026)

**Goal:** anyone can run Provenance on their own repo in two commands.

1. **Work on any repo.**
   - Generalise `config.Repo` so it can point at an existing local clone: `Repo.at(path)`, with its data in `<repo>/.git/provenance/` or a user cache directory, keyed by remote URL.
   - Keep `Repo.named()` for the research corpus.
   - Touches `src/provenance/config.py`, `surfaces/cli.py`, `surfaces/mcp_server.py` and `surfaces/web.py`.
2. **One indexing command.**
   - `provenance index [PATH]` runs `ingest_history` (`ingest/git_history.py`), then `classify_repo` and `write_ignore_file` (`trace/layer_a.py`), then `link_messages` (`graph/build.py`).
   - It is incremental: rerunning it adds only new commits, since `Store.has_commit` and `unclassified()` already support this.
3. **MCP for any repo.**
   - `provenance mcp [PATH]`, defaulting to the current folder, so `claude mcp add whyblame -- uvx whyblame mcp` just works inside a project.
   - Add an `explain_line` MCP tool beside `why_line` and `why_range`, reusing `synth/explain.py:explain_lines`. It is optional and only offered when a Gemini key is configured.
4. **React end to end.**
   - Clone, ingest and classify React (the JavaScript tree-sitter rules already exist), then run the label-free checks.
   - React has no hand-kept skip list like Django's, so run `eval/method_gap.py` and a small sample read instead.
5. **Performance.**
   - Profile the 19.2 s Redis line from `eval/method_gap.py`'s stress test, and cap or cache the expensive step.
   - Target: p99 under 10 s.
6. **Packaging groundwork.**
   - `pyproject.toml` metadata, a `whyblame` entry point (package name `whyblame`), a check that `uvx` runs from a clean machine, a README quickstart, and GitHub Actions CI running pytest and ruff.

**Exit:** on a fresh clone of some other open-source repo, `uvx … index` then `mcp` works, and an agent calls `why_line`. Tagged **v0.2-alpha**.

### Phase 2: Evidence everywhere (Jan 2027)

**Goal:** every traced commit finds its discussion, beyond Django's Trac.

1. **GitHub crawl** using the token.
   - `ingest/github.py` (a tested, resumable GraphQL crawler) runs for Redis PRs and issues, then React, then Django PRs.
   - Store everything in `artefacts`, and resolve `gh:` nodes to PRs or issues.
2. **Trac comments for Django.** These are missing from the CSV export. Extend `ingest/trac.py` politely, at 1 request per second, overnight.
3. **Retrieval when no link exists.**
   - When a commit has no explicit link, fall back to FTS5 (`Store.search_artefacts`). Build the query from the line, the function name and the path, and filter to artefacts created before the commit.
   - Embeddings come second, and only if FTS5 recall is weak. Check that a small local embedding model fits in 8 GB first.
   - New module `src/provenance/retrieve/`.
4. **Feed retrieved evidence into the existing paths:** `explain_lines` and the MCP `links` field, marked by how each item was found (linked or searched).
5. **RQ2-light.**
   - A benchmark on Django only, following `plans/02` §4's leakage rules: strip the references, hold out the edges, and allow only candidates that existed earlier.
   - Compare BM25, plain-blame→link, and ours, with Recall@k and MRR.
   - New script `eval/retrieval_bench.py`.

**Exit:** most Redis and React logic commits show their PR. RQ2-light numbers are saved in `eval/results/`.

### Phase 3: Protect code in CI (Feb 2027), the flagship product feature

**Goal:** a GitHub Action that warns when a PR removes or weakens protective code, and cites the reason.

1. **Guard detection.** tree-sitter queries for guards in Python, C and JavaScript, listed in `plans/07` §2: raise, assert, early returns, null and bounds checks, locks, timeouts and try blocks. New module `src/provenance/protect/guards.py`.
2. **Change typing.** Classify each guard as *removed* or *weakened*, starting with the clear cases: a deleted guard, a broadened `except`, a reduced retry count, a changed timeout.
3. **History scoring.** Trace each touched guard with `Tracer`, then score it on:
   - an origin linked to a bug or ticket,
   - security or regression language,
   - past reverts and reintroductions, using the existing edges.

   There is no LLM in the loop, so results are deterministic. A warning fires only when the guard change is found **and** its history score passes the threshold.
4. **`provenance check --base --head --format github|text|json`.** Emits `::warning file=,line=::` annotations, plus the MCP tool `check_change`.
5. **The GitHub Action.**
   - `action.yml` with a composite action: checkout with `fetch-depth: 0`, setup-uv, then the index cache restored through `actions/cache`.
   - It warns and never blocks, and runs only on the `pull_request` trigger.
   - Test it on a fork of a real repo.
6. **RQ4 evaluation.**
   - Mine history for positives: a guard removed, then restored within 30, 90 or 180 days with a bug link.
   - Negatives: a guard removed that stays removed.
   - Report precision, recall, PR-AUC and the base rate against two baselines: "flag every removed guard" and a keyword rule. New script `eval/protect_bench.py`.

**Exit:** the Action posts a correct warning on a replayed real guard-removal PR, and RQ4 numbers are saved. Tagged **v0.5-beta**.

### Phase 4: Trustworthy answers, then v1.0 (Mar 2027)

**Goal:** measured explanation quality, and a polished public 1.0.

1. **RQ3 question set.** About 60 "why" questions: about 40 answerable and about 20 unanswerable, the latter built by withholding the evidence. Spread across Django, Redis and React.
   - Labels follow the same AI double-annotation protocol as the gold set: Claude, plus Gemini blind.
   - Teammates spot-check 15 of them, a small bounded task.
2. **Abstention gate 1.** A simple calibrated classifier runs before the LLM call. Its features: link presence, trace confidence, evidence count and top search score. It saves Gemini calls.
   - Gate 2 already exists in `parse_reply`. Add one more check there: quoted text must appear in the evidence.
3. **Measure:**
   - citation correctness per claim,
   - answer accuracy,
   - selective accuracy against coverage,
   - a model bake-off: `gemini-3.8-flash` against one stronger and one cheaper pinned model.

   New script `eval/explain_bench.py`. Add it, and every later benchmark, to `eval/reproduce.py`.
4. **Works with any model** (see the end-goal section below):
   - Streamable HTTP transport.
   - `provenance init`, which writes the rules-file snippets.
   - `schema_version` on every reply.
   - The six-client compatibility matrix run and published.
5. **Release v1.0.**
   - PyPI package, a GitHub release, the Action published to the Marketplace.
   - Listed in the official MCP registry and the main MCP directories.
   - A docs page (quickstart, how it works, safety model), a 2-minute demo video, and the web UI bundled as `provenance ui`.

**Exit:**

- `pip install` / `uvx` installs on a fresh machine.
- The registry listing is live.
- The compatibility matrix passes in at least 5 of the 6 clients, one of them a local model.
- RQ3 numbers are saved.

### Phase 5: Prove, promote, finish (Apr – early May 2027)

1. **RQ5 pilot.**
   - 20 cases from Phase 3's mined guard removals.
   - Each case: check out the repo before the removal, give a Gemini agent a realistic task that tempts it to touch the guard, and run it with and without the MCP tool.
   - Measure whether the guard survived **and** whether the task was completed.
   - McNemar test. Track spending.
2. **RQ6 footprint**, measured on the M1: index time, database size, peak RAM, and query latency cached and uncached.
3. **Promotion.** Launch posts on Hacker News "Show HN", Reddit (r/programming, r/Python, r/ClaudeAI), X/LinkedIn and dev.to, plus outreach to Django and Redis maintainers about the auto-generated skip lists. Track stars, installs and issues.
4. **Paper.**
   - The RQ1 method plus RQ3 and RQ4, with RQ2 and RQ5 as supporting evidence. Target a workshop or short-paper venue; check deadlines in December.
   - Release the benchmark as artefact IDs, labels and rebuild scripts, with a DOI on Zenodo. Never republish scraped text wholesale.
5. **Final report, deck and viva.** Follow the same pattern as Phase 0, from one frozen final run.

**Exit:** final submission, with every number from one `reproduce.py` run.

## End goal: an MCP that works with any model and does what it's meant to

**Short answer: yes.** MCP is an open standard, so the finished server works in any MCP-capable client, whatever model the client runs. The model only needs to support tool calling. The plan builds and tests for this on purpose instead of assuming it.

### Why any model can use it

- **The server needs no model and no API key.** `why_line`, `why_range`, `check_change` and `find_discussions` return evidence: the traced chain, the commits, and the tickets and PRs with excerpts. The model in the user's client (Claude, GPT, Gemini, or a local Llama or Qwen) reads that evidence and reasons over it. Tracing and search run fully offline on the user's machine.
- **Gemini stays optional.** The `explain_line` tool is offered only when a key is configured. Without one, the agent writes its own explanation from the evidence, so nothing breaks.
- **Transports.**
  - stdio is the default, which every desktop and CLI client supports.
  - Phase 4 adds the **Streamable HTTP** transport, bound to localhost by default, for clients and hosted agents that need a URL.
- **Plain JSON with stable schemas.**
  - Every tool's inputs and outputs are typed JSON with a `schema_version` field.
  - The JSON avoids client-specific features, so weaker or local models parse it reliably.
  - Replies stay small: a hard cap on size, with truncation clearly flagged.

### Making sure it works as intended

The intended behaviour is that **an agent checks why code exists before it deletes or weakens it, and then keeps it or asks first.** Three layers make that happen:

1. **The server tells agents when to call it.** The MCP `instructions` and each tool description say: call this BEFORE deleting or weakening a check, retry, lock, timeout or validation. That text is already in `surfaces/mcp_server.py`. It gets tuned and tested across models in Phase 4.
2. **Rules files in the project.** `provenance init` writes a short snippet into the files agents already read: `AGENTS.md`, `CLAUDE.md`, `.cursor/rules` and `GEMINI.md`. The snippet says to consult `why_line` before removing guards. This is what makes weaker models actually use the tool.
3. **A backstop that needs no model.** Even if an agent never calls the tool, the Phase 3 **CI check** catches the removed guard on the pull request. The tool is used either way.

### Compatibility matrix (Phase 4, required for v1.0)

Run a scripted check in each client: register the server, ask "simplify make_password() in hashers.py", then record whether the agent called `why_line` and kept the guard.

| Client | Model(s) | Transport |
|---|---|---|
| Claude Code / Claude Desktop | Claude | stdio |
| Cursor | GPT, Claude | stdio |
| VS Code (Copilot agent mode) | GPT | stdio |
| Gemini CLI | Gemini | stdio |
| OpenAI Codex CLI | GPT | stdio |
| A local-model client (for example LM Studio or an Ollama-based MCP host) | Llama or Qwen | stdio |

The results are published in the README as a table of which clients and models used the tool unprompted, and which needed the rules file. **RQ5 then measures "works as intended" properly:** with and without the tool, did the guard survive and did the agent still finish the task? That proof covers the model tested. The matrix shows how far it generalises.

## What carries over unchanged

- The tracer (`trace/chain.py: Tracer`) and Layers A, B and C.
- The tracer's frozen rules (`c84fa8e`). No rule changes without a new held-out test set.
- `Store` and its schema (FTS5, `llm_cache`, `edges`).
- `Explainer.why_line`, `explain_lines` and `parse_reply`.
- The safety model: read-only, untrusted fields, never says "safe".
- The evaluation discipline: freeze, then a fresh test set, then score once. AI double labels, always disclosed.

## Risks and how they're handled

| Risk | Response |
|---|---|
| One person, five phases | Each phase has its own exit and release tag. If time runs short, cut from the end: RQ5 → embeddings → RQ2-light. Phases 1, 3 and 4 are the product core. |
| The CI check raises false alarms | Tune for precision first, warn and never block, report the base rate. |
| Gemini cost or model changes | Pin the version, cache every reply, run gate 1 before calls, run each benchmark in one window. |
| Generalising breaks the research corpus | `Repo.named()` stays as it is. The reproduce run is checked byte for byte after Phase 1. |
| No GitHub token arrives | Phase 2 falls back to Django and Trac only. The Phase 3 Action still works, using git plus FTS. |

## Verification

- **Every phase:**
  - `uv run pytest -q` and `uv run ruff check .` pass.
  - `uv run python eval/reproduce.py` reproduces the committed numbers byte for byte, or the change is explained in the commit.
- **Phase 0:**
  - The report and deck open, and the PDF re-renders.
  - `provenance explain` replays the demo lines from the cache with the network off.
- **Phase 1:** in a temporary clone of a repo outside the corpus, run `uvx --from . provenance index`, then `provenance mcp`. Call `why_line` through an MCP client (the existing pattern in `tests/test_mcp_server.py`).
- **Phase 3:** run the Action on a fork, using a replayed historical guard-removal PR. The annotation appears on the right line and cites its ticket.
- **Phase 4:** install from PyPI on a clean virtualenv or machine, and check the MCP registry listing resolves.

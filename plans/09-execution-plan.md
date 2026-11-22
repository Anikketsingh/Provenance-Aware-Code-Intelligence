# Execution Plan: Finish the Project, Phase by Phase

**Level:** project. **Written:** 22 Nov 2026. **Hard deadline:** final evaluation, **27 Nov 2026**.

This is the working plan. It is ordered by **phase, not date**: finish a phase, then start the next, as fast as you like. The design reasoning behind each phase is in [08-completion-plan.md](08-completion-plan.md); this file is what to do. [03-roadmap.md](03-roadmap.md) keeps the Project-I history.

---

## How to use this plan

1. **Run the phases in order.** Each phase depends on the one before it (the dependency map is below).
2. **Start a phase** by telling Claude **"Start Phase N"**. Claude builds every task marked **CLAUDE**, runs the checks, and stops when it reaches a task marked **YOU**, telling you exactly what to do.
3. **A phase is done only when every box in its exit checklist is ticked.** No checklist, no "done".
4. **Every phase ends the same way:**
   - full tests and lint pass;
   - `eval/reproduce.py` still reproduces the frozen Project-I numbers, byte for byte;
   - commit, push and release tag;
   - a short phase report: what was built, the numbers, anything that was cut.
5. **One guard on time.** On the morning of **26 Nov**, wherever we are, apply the cut list (section 9) and move straight to Phase 5. The analysis and the report must have a full day.

**Owners:**

- **CLAUDE** builds in this repo.
- **YOU** is Aniket: accounts, publishing, apps on this laptop, recording, rehearsal.
- **BOTH** means Claude prepares everything and you do one step.

**Rough effort:**

| Phase | Claude work | Your work | Runs in the background |
|---|---|---|---|
| 0. Setup | done | 20 min left | — |
| 1. Product core | about 5 h | 10 min | React indexing |
| 2. Evidence | about 6 h | — | GitHub crawls (about 1–2 h) |
| 3. Protect (CI check) | about 7 h | 20 min | mining guard history |
| 4. Any model and v1.0 | about 5 h | about 2 h | — |
| 5. Research and analysis | about 6 h | — | benchmarks and the agent pilot |
| 6. Deliverables | about 6 h | about 3 h | — |

---

## Phase 0: Setup (almost done)

| # | Item | Status |
|---|---|---|
| 0.1 | GitHub token in `.env`; GraphQL works with 5,000 requests an hour | ✅ checked 22 Nov |
| 0.2 | Gemini key in `.env`; the live test passes | ✅ checked 22 Nov |
| 0.3 | Claude can `git push` (project-local permission) | ✅ checked with a real push |
| 0.4 | Repo is public, and the history has no secrets, `.env` or scraped data | ✅ audited 22 Nov |
| 0.5 | Package name `whyblame` is free on PyPI | ✅ checked 22 Nov |
| 0.6 | **PyPI token**: register at pypi.org, turn on 2FA, create an API token named `whyblame` scoped to the entire account, and add `UV_PUBLISH_TOKEN=pypi-...` to `.env` | ⬜ **YOU, before Phase 4** |
| 0.7 | **MCP clients** for the any-model test: install and sign in to at least 4 of Cursor, VS Code + Copilot, Gemini CLI (`npm i -g @google/gemini-cli`), Codex CLI, LM Studio or Ollama (`ollama pull qwen3:4b`) | ⬜ **YOU, before step 4.6** |
| 0.8 | Ask the department whether the final report has a required format | ⬜ **YOU, before Phase 6** |

Facts settled during setup, so they don't get re-checked:

- React's canonical repo is now `react/react` (the old `facebook/react` redirects).
- GitHub sizes: Redis has 8,671 PRs and 7,188 issues; Django has 22,239 PRs.
- `gh`, the GitHub CLI, is **not installed**. Release steps that need it either use the GitHub web UI (YOU) or the REST API with the token (CLAUDE).

---

## Phase 1: Product core, working on any repository

**Goal:** a stranger can point the tool at *their own* repo with two commands and an agent can ask it why a line exists.

**Why first:** everything after this (CI check, release, any-model testing, the agent study) runs on repos outside our research corpus.

**Starts from:** today's code. **Ends with:** tag `v0.2.0`.

### Tasks

**1.1 Point at any repo (CLAUDE).** In `src/provenance/config.py`, add `Repo.at(path)`.
- It accepts a working copy or a bare repo, and finds the git directory with `git rev-parse --absolute-git-dir`.
- Data lives in `<git-dir>/provenance/`: `provenance.db` plus the skip lists. That means nothing appears in the user's working tree, and nothing needs `.gitignore`.
- `Repo.named(name)` stays exactly as it is, so the research corpus and every result keeps working.
- Add one resolver, `resolve_repo(arg)`: a known corpus name gives `Repo.named`; an existing path (including `.`) gives `Repo.at`; anything else is a clear error.
- **Check:** unit tests cover a working copy, a bare repo, a subfolder of a repo (it must find the root) and a non-repo (a clear error).

**1.2 `index [PATH]`, one command to prepare a repo (CLAUDE).**
- It runs ingest, then classify (Layer A), then write the skip lists, then link commit messages. It shows progress and ends with a summary: commits, cosmetic and rename counts, links found, time taken.
- **Incremental:** a second run only touches new commits (`Store.has_commit` and `unclassified()` already support this).
- `--rev` picks the revision; the default is `HEAD`.
- **Check:** in a test, run it twice on a small repo. The second run adds 0 commits and finishes in under a second.

**1.3 Every command takes a name or a path (CLAUDE).**
- `why`, `explain`, `search`, `mcp`, `ui`, `link`, `classify` and `fetch-tickets` all use `resolve_repo`. `ui` accepts several paths.
- When a repo isn't indexed yet, the message tells you the exact `whyblame index` command to run. No stack traces.
- **Check:** a test for each command on an indexed temporary repo, given by path.

**1.4 MCP for any repo (CLAUDE).**
- `mcp [PATH]`, defaulting to the current folder. The server's name is `whyblame`.
- A new tool, **`explain_line(file, line, end_line?)`**, is offered **only when a Gemini key is configured**. It reuses `synth/explain.py: explain_lines`, and its reply keeps evidence and explanation separate.
- `why_line` and `why_range` replies stay exactly the same, so existing agents don't break.
- **Check:** an MCP client test (the same pattern as `tests/test_mcp_server.py`) lists the tools with and without a key, and calls each one on a temporary repo.

**1.5 Package as `whyblame` (CLAUDE).**
- In `pyproject.toml`: `name = "whyblame"`, `version = "0.2.0"`, description, authors, `license = "Apache-2.0"` (matching the repo's LICENSE), keywords, classifiers, and project URLs pointing at the GitHub repo.
- Two console commands: `whyblame` (the product) and `provenance` (kept for the research scripts).
- Make sure the wheel contains `schema.sql` and `surfaces/static/index.html`. Open the built wheel and list them.
- Check whether the `<3.13` Python cap is still needed. If the tests pass on 3.13, widen it to `>=3.12`.
- **Check:** `uv build`, then in a new temporary venv `uvx --from dist/whyblame-0.2.0-py3-none-any.whl whyblame --help` works.

**1.6 README for users first (CLAUDE).**
- The top half is product: what it does in one line, a 30-second quickstart (`pip install whyblame`, `whyblame index`, `claude mcp add whyblame -- whyblame mcp`), the tools, the safety model and a screenshot.
- The bottom half is the research: results, how to reproduce them, and a link to the report.
- **Check:** every command in the README is copied and run once in a temporary repo.

**1.7 CI for this repo (CLAUDE).**
- `.github/workflows/ci.yml`: on push and PR, run checkout, setup-uv (pinned), `uv sync`, `uv run ruff check .` and `uv run pytest -q`.
- Live Gemini tests stay excluded.
- **Check:** the first push turns the Actions tab green. Claude reads the run's result through the GitHub API.

**1.8 Test on an outside repo (CLAUDE).**
- Clone `pallets/click`, a small, well-known Python project we've never used, then `whyblame index` it and call `why_line` through an MCP client on three of its guard lines.
- Record the index time, database size and the three answers in `eval/results/dogfood_click.json`.
- **Check:** all three lines trace, and any bug found is fixed with a test.

**1.9 Start the slow jobs for Phase 2 in the background (CLAUDE).**
- Clone and index **React** (`react/react`, about 21,800 commits).
- **Check:** both are running or finished before Phase 1 is reported.

### Phase 1 exit checklist

- [ ] `whyblame index` and `whyblame mcp` work on `pallets/click` by path
- [ ] `explain_line` shows only when a key exists; `why_line` replies are unchanged
- [ ] The wheel builds, contains its static files, and `uvx` runs it
- [ ] CI is green on GitHub
- [ ] Tests and ruff pass; `reproduce.py` is byte-identical
- [ ] React indexing started or finished
- [ ] Tag `v0.2.0` pushed

---

## Phase 2: Evidence everywhere

**Goal:** a traced commit leads to its discussion on every repo, not just Django's Trac tickets. The tool also finds likely discussions when a commit links to nothing, and labels those honestly as *found by search*.

**Starts from:** `v0.2.0`. **Ends with:** tag `v0.3.0`.

### Tasks

**2.1 A `crawl-github` command (CLAUDE).**
- It wraps the existing tested crawler, `ingest/github.py: crawl`: resumable, and it stays well under the rate limit.
- It stores PRs (title, body, state, merged-at, **merge commit SHA**, labels) and issues (title, body, state, closed-at) in `artefacts`.
- **Check:** the existing tests pass, plus a new one for storing the merge commit SHA.

**2.2 Link PRs to commits by their merge commit (CLAUDE).**
- Every crawled PR with a merge commit SHA becomes a `merged_as` edge to that commit. This is what links PRs on **any** GitHub repo, including Django, whose commit messages rarely say "#N".
- Unresolved `gh:<repo>/N` nodes from commit messages get turned into `pr:` or `issue:`.
- **Check:** a test with a fake crawl, then the edge counts are saved to `eval/results/crawl_stats.json`.

**2.3 Run the crawls (CLAUDE, in the background).**
- First Redis (about 8.7k PRs and 7.2k issues), then React, then Django PRs (about 22k).
- **Check:** every crawl ends with `done=1` in `crawl_state`, and the stats file lists the rows stored and the commits linked per repo.

**2.4 GitHub evidence for anyone's repo (CLAUDE).** `whyblame index --github` crawls the repo's PRs and issues when `GITHUB_TOKEN` is set. Without a token it says what it's missing and carries on. **Check:** a test with the crawler faked.

**2.5 Search fallback when a commit links to nothing (CLAUDE).** New module `src/provenance/retrieve/`.
- The query is built from the line's tokens, the function or class it sits in, the file path and the commit subject. It runs over FTS5, the existing `Store.search_artefacts`.
- **The time rule:** only artefacts created **before** the commit count.
- Results are marked `"found_by": "search"`, with a lower confidence, and never mixed with real links (`"found_by": "link"`).
- **Check:** tests show that a later artefact is never returned and that search results are always labelled.

**2.6 Put the evidence into every surface (CLAUDE).**
- `explain_lines` cites PR and issue bodies, and says when evidence was found only by search.
- The new MCP tool **`find_discussions(file, line)`** returns the linked and searched discussions, kept apart.
- The UI story panel gains a "Related discussions" block that shows "found by search" next to those results.
- **Check:** the demo line on Redis explains with a PR citation, and a web API test covers it.

**2.7 React label-free checks (CLAUDE).**
- Run `method_gap.py` with React, and read 20 sampled commits flagged as cosmetic.
- **Check:** results saved; any bug found in the JavaScript rules is fixed with a test, or noted as a limitation.

**2.8 Build the retrieval benchmark (RQ2), but don't run it yet (CLAUDE).**
- `eval/retrieval_bench.py` covers Django commits that have a `Fixed #N` link.
- It hides the link and strips the reference text, using two levels: references removed, and the whole message hidden. Only tickets created before the commit are candidates.
- Methods: plain keyword search, keyword search with the line's code context, and ours (trace-aware query plus the time rule).
- Metrics: Recall@1, @5 and @10, and MRR.
- **Check:** a dry run on 50 items works. The full run happens in Phase 5.

### Phase 2 exit checklist

- [ ] Redis, React and Django crawls complete; `crawl_stats.json` saved
- [ ] PRs linked to commits by their merge commit SHA on all three repos
- [ ] Search fallback returns only earlier artefacts, always labelled
- [ ] `find_discussions` works over MCP, and the UI shows related discussions
- [ ] React label-free numbers saved
- [ ] `retrieval_bench.py` dry run passes
- [ ] Tests, ruff and reproduce all pass; tag `v0.3.0` pushed

---

## Phase 3: Protect code in CI (the flagship)

**Goal:** a GitHub Action warns, on the pull request itself, when a change removes or weakens *protective* code, and cites the ticket or PR that explains why the code was there. It is deterministic and has no LLM, so the same PR always gets the same answer.

**Starts from:** `v0.3.0`. **Ends with:** tag `v0.5.0`.

### Tasks

**3.1 Find guards (CLAUDE).** New module `src/provenance/protect/guards.py`, using tree-sitter queries.

| Language | Counted as a guard |
|---|---|
| Python | `raise`; `assert`; an `if` whose body raises or returns early; `try/except`; `with transaction.atomic()` and locks; timeout and retry arguments |
| C | an `if` leading to `return`, `goto` or abort; NULL and bounds checks; `assert`, `serverAssert`; lock and unlock calls |
| JavaScript | `throw`; an early `return` in an `if`; `invariant(...)`; null or undefined checks; `try/catch` |

Each guard gets a stable fingerprint (its token stream, ignoring layout), so layout changes are never counted as a removal. **Check:** at least 5 small positive and negative examples per language.

**3.2 Classify the change (CLAUDE).** Compare the guards in each changed file at base and head.
- **Removed:** the fingerprint is gone, and isn't found elsewhere in the diff (a move doesn't count).
- **Weakened:** the guard remains but changed in one of these ways: `except X` became a broader `except`; a retry count or timeout went down or was removed; a comparison bound was loosened; a condition gained an `or True`-style escape or lost a clause.

**Check:** tests for each type, plus a test that a pure reformat (`black`) produces **zero** findings.

**3.3 Score the guard's history (CLAUDE).** Trace the guard's line at base with the existing `Tracer`, then add up deterministic signals:
- whether the commit that set its behaviour links to a ticket or PR;
- bug or safety words in that evidence (fix, crash, regression, security, CVE, race, deadlock, leak, overflow, injection);
- whether the guard was ever reverted and re-added;
- how old it is;
- whether the commit that added it was a bug fix.

The score is 0–1 and every signal it used is listed in the finding. **Check:** the same input always gives the same score and the same explanation.

**3.4 The `check` command (CLAUDE).**
- Usage: `whyblame check --base <sha> --head <sha> [--format text|json|github] [--threshold 0.x]`.
- The `github` format prints `::warning file=…,line=…,title=Protective code removed::<why, with ticket link>`.
- It exits 0 by default, so it warns and never blocks; `--fail-on-findings` is opt-in.

**Check:** on a replayed real guard removal from Django history, it warns and cites the right ticket.

**3.5 The MCP tool `check_change` (CLAUDE).** An agent passes a unified diff, or base and head, *before* it commits, and gets the same findings. **Check:** an MCP client test.

**3.6 The GitHub Action (CLAUDE).** `action.yml` at the repo root, as a composite action:
- checkout with `fetch-depth: 0`, then setup-uv (a pinned version);
- restore the index cache, keyed by repo and base SHA (`actions/cache`, pinned);
- `whyblame index` (incremental), then `whyblame check --format github`.

Inputs: `threshold` and `python-version`. The README shows a five-line usage example. Security: only the `pull_request` trigger, read-only permissions, and the PR's code is never run.

**Check:** `actionlint` passes, if it can be installed with `uvx` or `npx`; otherwise a careful YAML review.

**3.7 Mine guard history for evaluation (CLAUDE, in the background).** Scan Django and Redis history for every commit that removed or weakened a guard (using 3.1 and 3.2).
- **Positive:** the same fingerprint came back within 30, 90 or 180 days, with a bug link or a revert.
- **Negative:** it never came back within 365 days and has no linked fix.

Save as `eval/data/guard_events.jsonl`. Split by date: **tune on events before 2020, test on 2020 and later.** **Check:** counts per split saved, and 20 events read by hand for sanity.

**3.8 Set the threshold, then freeze it (CLAUDE).** Choose it on the tune split only, aiming for precision first. Write it into the code as a constant, with a note on how it was chosen. **Check:** committed before any test-split number is computed.

**3.9 Live test on GitHub (BOTH).**
- **YOU:** fork a small repo (Claude suggests one with good guards) into your account, or create `whyblame-demo`.
- **CLAUDE:** pushes the workflow and a branch that deletes a real guard, using the GitHub API. **YOU:** open the PR in the browser.
- **Check:** the warning appears on the PR's changed line. Take a screenshot for the report and deck.

### Phase 3 exit checklist

- [ ] Guard finder and change typing tested in all three languages; a reformat gives zero findings
- [ ] `check` cites the right ticket on a replayed real removal
- [ ] `check_change` works over MCP
- [ ] Action runs on a real PR on GitHub (screenshot saved)
- [ ] `guard_events.jsonl` built with a date split; threshold frozen from the tune split only
- [ ] Tests, ruff and reproduce pass; tag `v0.5.0` pushed

---

## Phase 4: Works with any model, then the v1.0 release

**Goal:** the server works, and is *used*, in any MCP client with any tool-calling model, including a local one. Then it's published so anyone can install it.

**Starts from:** `v0.5.0`. **Needs:** 0.6 (the PyPI token) and 0.7 (the clients). **Ends with:** tag `v1.0.0` and a public release.

### Tasks

**4.1 HTTP transport (CLAUDE).**
- `whyblame mcp --http [--port 8766]` uses the Streamable HTTP transport and binds to `127.0.0.1` only, unless `--host` is given with a warning.
- stdio stays the default.
- **Check:** an HTTP MCP client test calls `why_line`.

**4.2 `whyblame init` (CLAUDE).** Run inside a repo, it:
- writes a short rule ("Before deleting or weakening a check, retry, lock, timeout or validation, call `why_line` and respect what it says") into `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` and `.cursor/rules/whyblame.mdc`, inside marker comments so a second run changes nothing;
- prints the exact one-line command to register the server in Claude Code, Cursor, VS Code, Gemini CLI and Codex.

**Check:** a test that it's idempotent, and that it never removes the user's own text.

**4.3 Stable replies (CLAUDE).**
- Every tool reply carries `schema_version: 1` and has a size cap; truncation is flagged in the reply.
- Errors are plain JSON with a `status`, never stack traces.

**Check:** a schema test for each tool.

**4.4 Tool descriptions that make agents call it (CLAUDE).** Tighten the MCP `instructions` and each tool's description so they say *when* to call (before deleting or weakening a guard) and *what to do with the answer* (keep it, or ask the user). Keep them short, because weaker models skim.

**4.5 A script for the compatibility test (CLAUDE).**
- `eval/compat/README.md` gives exact steps for each client: where its MCP config lives, the config to paste, and how to confirm it connected.
- The task is the same everywhere: in a copy of Django at the pinned revision, ask *"Simplify make_password() in django/contrib/auth/hashers.py"*.
- Results go into `eval/compat/results.csv`, with these columns: client, model, connected?, called a whyblame tool unprompted?, kept the guard?, with `init` rules or not, notes.
- Claude Code is run by Claude first, as the reference row.

**4.6 Run the compatibility test (YOU, about 1.5 h).** Follow the script in at least 4 clients, **one of them a local model** (LM Studio or Ollama with `qwen3:4b`). Run each client **twice**: once without the `init` rules and once with them. **Check:** at least 4 rows in `results.csv`, including one local.

**4.7 Prepare the release (CLAUDE).**
- Version `1.0.0`, a `CHANGELOG.md`, and the README completed with the compatibility table.
- `server.json` for the official MCP registry, and the PyPI ownership marker `mcp-name: io.github.anikketsingh/whyblame` in the README.
- `uv build`, then check the wheel's contents, then upload to TestPyPI (if you added a TestPyPI token) and install it into a new venv from there.
- Draft the GitHub release notes.

**4.8 Publish (YOU, about 30 min; Claude walks you through each command).**
1. Run `uv publish`, then check that `pip install whyblame` works in a new folder.
2. Create the GitHub release `v1.0.0` (Releases → Draft a new release → paste the notes Claude prepared). Tick **"Publish this Action to the GitHub Marketplace"**.
3. Publish to the MCP registry: install `mcp-publisher`, then `mcp-publisher login github` (it opens the browser), then `mcp-publisher publish`.

**Check:**
- The PyPI page is live.
- The Marketplace listing is live.
- A registry search for `whyblame` finds it.

### Phase 4 exit checklist

- [ ] HTTP transport works; `init` is idempotent; every reply has `schema_version`
- [ ] At least 4 clients tested, including one local model, with and without the rules; `results.csv` committed
- [ ] `pip install whyblame` works from PyPI on a clean venv
- [ ] GitHub release, Marketplace Action and MCP registry entry all live
- [ ] Tag `v1.0.0` pushed. **Features are frozen from here.**

---

## Phase 5: Research and analysis — how much difference does it make?

**Goal:** measure, on frozen code, what the system changes, and turn that into numbers for the report.

**Rule:**
- No feature changes in this phase.
- A bug fix is allowed only if a run crashes. Write it down in `eval/results/freeze_log.md`, and rerun every affected result.

**Starts from:** `v1.0.0`. **Ends with:** tag `v1.0.0-results`.

### The questions and how each is measured

| # | Question | Data | Measure | Script → result |
|---|---|---|---|---|
| RQ1 | Does tracing beat git's best settings? | Held-out gold set, 60 lines | Weighted accuracy, CIs, McNemar. **Already done: 83.5% vs 69.2%** | `score_gold.py` → `gold_scores_test.json` |
| RQ2 | Can it find the right discussion when the link is missing? | About 1,000 Django commits with ticket links, link hidden | Recall@1, @5, @10 and MRR; keyword search vs ours | `retrieval_bench.py` → `retrieval_bench.json` |
| RQ3 | Are explanations correct, and does it refuse when it should? | 40 questions: 30 answerable, 10 with the evidence held back | Citation correctness per claim, answer accuracy, abstention rate on the unanswerable 10 | `explain_bench.py` → `explain_bench.json` |
| RQ4 | Does the CI check catch dangerous removals? | Test split of `guard_events.jsonl` (2020 and later) | Precision, recall, PR-AUC, **the base rate**; compared with "flag every removed guard" and a keyword rule | `protect_bench.py` → `protect_bench.json` |
| RQ5 | Do agents with the tool make fewer unsafe edits? | 15–20 positive cases from RQ4 | Guard kept, and task completed, with vs without the tool; McNemar | `agent_pilot.py` → `agent_pilot.json` |
| RQ6 | Does it fit a laptop? | click, Redis, Django, React | Index time, database size, peak RAM, query latency cached and uncached | `footprint.py` → `footprint.json` |
| Any model | Does it work beyond one client? | Phase 4 `results.csv` | Clients connected, called the tool, kept the guard | `compat_summary.py` → `compat.json` |

### Tasks

**5.1 RQ2 full run (CLAUDE).** About 1,000 items, both difficulty levels, results per method.

**5.2 RQ3 question set and run (CLAUDE).**
- **Questions:** 40 lines picked from Django, Redis and React where the history is readable.
- **Answerable questions:** the reference answer is written from the artefacts.
- **The 10 unanswerable questions:** the real evidence is withheld, so the right response is to abstain.
- Labels follow the gold-set protocol: Claude writes them, Gemini checks them blind, and disagreements are settled with a check sheet.
- Each claim in each explanation is judged supported or unsupported by its cited source, by both models independently, and the agreement is reported.

**5.3 RQ4 run (CLAUDE).** Test split only, with the threshold from Phase 3. Report it per repo and per window (30, 90 and 180 days), with the base rate stated next to every precision figure.

**5.4 RQ5 agent pilot (CLAUDE).**
- The harness, `eval/agent_pilot.py`, gives a Gemini model (pinned version, temperature 0) three file tools: list, read, and edit by search-and-replace. In the **treatment** condition it also gets `why_line` and `check_change`.
- Each case checks out the repo just before the historical removal.
- The task is written from the purpose of the original change, for example "remove dead code in X" or "simplify Y". **It never mentions the guard.**
- Outcome 1, **guard kept:** the guard's fingerprint is still in the final file.
- Outcome 2, **task done:** a blind Gemini judge checks it against a short rubric, and Claude spot-checks 10 cases.
- Size: 15–20 cases, 2 conditions and 2 seeds, which is about 80 runs. Track the cost, and save every transcript to `eval/results/agent_runs/`.
- Statistics: McNemar on guard kept; task completion compared between the two conditions.

**5.5 RQ6 footprint (CLAUDE).** Measure each repo with `/usr/bin/time -l` for peak RAM, and time the latency for 50 lines both uncached and cached.

**5.6 One final run (CLAUDE).**
- Extend `eval/reproduce.py --full` to run every RQ and the any-model summary, then run it once.
- `eval/results/summary.md` must cover all of them.

**5.7 Write the analysis (CLAUDE).** `reports/analysis.md`, which becomes the core of the report's results chapter:
- **How much difference it makes:** one headline table with every RQ, the baseline vs ours, effect size and confidence.
- **Where it doesn't help:** per repo (Redis), the failure categories, and the clients where agents ignored the tool.
- **What else we can do:** each item tied to a measured weakness, for example embeddings if RQ2 Recall@1 is low, a bigger agent study, IDE plug-ins, PostgreSQL and mailing lists, Trac comments, a human label check, and the paper.

### Phase 5 exit checklist

- [ ] Every result file listed in the table exists, from the frozen code
- [ ] `reproduce.py --full` regenerates `summary.md`, covering RQ1–RQ6 and the any-model results
- [ ] Every agent run's transcript saved; Gemini spending recorded
- [ ] `reports/analysis.md` written, including "where it doesn't help"
- [ ] `freeze_log.md` lists every fix made during the phase, or says "none"
- [ ] Tag `v1.0.0-results` pushed

---

## Phase 6: Deliverables and evaluation readiness

**Goal:** everything the panel sees is finished, consistent, and every number in it traces to Phase 5.

### Tasks

**6.1 Final report (CLAUDE).** Standard DTU B.Tech structure, or the department's format if you get one from step 0.8. Delivered as .docx plus PDF, built by a script so the numbers come straight from `eval/results/`.
- **Front matter:** title page, declaration, certificate, acknowledgement (which states the use of AI tools), abstract, contents, list of figures and list of tables.
- **Chapters:** 1 Introduction; 2 Literature review and related tools; 3 System design; 4 Implementation (tracer, evidence, explanations, CI check, MCP and any-model support); 5 Evaluation method (RQ1–RQ6); 6 Results and analysis; 7 Limitations and threats to validity; 8 Conclusion and future work.
- **Back matter:** references and appendices (usage, the annotation rules, a sample MCP reply).
- **Figures:** the pipeline, RQ1 accuracy, the formatting-commit comparison, the UI screenshot (all already made), plus the **CI warning on a PR**, the **compatibility matrix**, and charts for RQ2, RQ4 and RQ5.
- **Check:** every number in the PDF matches `summary.md`. Claude checks this automatically by comparing the numbers in the text with the results files.

**6.2 Deck (CLAUDE).** Keep the three-speaker split. Add 4 slides: the CI check with its PR screenshot; works with any model; how much difference it makes (the RQ2–RQ5 numbers); and the public release (PyPI, Marketplace, registry). Update the delivery and next-steps slides to match what was shipped. You and the next-steps slides keep the extra time.

**6.3 Guide and README (CLAUDE).** Bring both up to date with the final state.

**6.4 Demo script v2 (CLAUDE).** In order:
1. trace a line in the UI;
2. explain it with citations;
3. show the **CI warning on the live PR**;
4. the same question in **two different clients**, one of them the local model;
5. `pip install whyblame` on screen.

It also lists the cached lines, a fallback for each step, and the likely questions with answers.

**6.5 Launch posts (CLAUDE).** Drafts for Show HN, Reddit (r/programming, r/Python, r/LocalLLaMA for the local-model angle) and LinkedIn, saved in `reports/launch/`. **YOU** post them after the evaluation, if you want to.

**6.6 Backup recording (YOU).** A 5-minute screen recording of the demo script, saved in two places: the laptop and Drive or a USB stick.

**6.7 Rehearsal (YOU, with Aarish and Aftab).** Two timed full runs, and one live demo on the presentation laptop and network.

**6.8 Final tag (CLAUDE).** Run the full tests and the reproduce check one last time, then tag `project-final` and push.

### Phase 6 exit checklist

- [ ] Report .docx and PDF done; numbers checked automatically against `summary.md`
- [ ] Deck updated, and each presenter has run through their part
- [ ] Demo script v2 works end to end with the network on **and** off (cached)
- [ ] Backup recording saved in two places
- [ ] Two rehearsals done, under time
- [ ] `project-final` tag pushed

---

## 7. Dependency map

```
Phase 0 setup ──► Phase 1 any repo ──► Phase 2 evidence ──► Phase 3 CI check ──► Phase 4 any model + v1.0 ──► Phase 5 analysis ──► Phase 6 deliverables
                        │                    │                    │                     │
                        │                    └─ RQ2 bench built   └─ guard_events ──────┴──► RQ4, RQ5 in Phase 5
                        └─ React index (background) ─► React checks (2.7) and RQ6
```

Allowed in parallel:

- Background crawls and indexing never block the next task.
- The report's chapters 1–5 can be drafted any time after Phase 3, because they describe the design, not the results.

## 8. Things that never change

- The frozen Project-I tracer (`c84fa8e`) and its held-out results. Phase work adds features around it and never changes its rules.
- Safety: read-only tools, untrusted text kept in labelled fields, never saying "safe", and the CI check only warns.
- Honesty:
  - AI labels are always disclosed.
  - Results are reported per repo.
  - The base rate goes next to every precision figure.
  - Every number comes from one run of `reproduce.py`.

## 9. If time runs short, cut in this order

1. RQ2 (2.8 and 5.1). Describe it as future work.
2. React (1.9 and 2.7); Django and Redis are enough.
3. The HTTP transport (4.1); stdio covers every desktop client.
4. The RQ5 pilot shrinks to 10 cases, with 1 seed.
5. PyPI. Release on GitHub instead, installable with `uvx --from git+https://github.com/Anikketsingh/Provenance-Aware-Code-Intelligence whyblame`.

**Never cut:**

- working on any repo (1.1–1.5);
- the CI check and its live PR test (3.1–3.9);
- the compatibility test with a local model (4.5–4.6);
- RQ4;
- the report, the backup recording and the rehearsal.

# Sprint Plan: Finish Everything by 27 Nov

**Level:** project. **Written:** Sun 22 Nov 2026. **Deadline:** final evaluation, **Fri 27 Nov 2026**.

This replaces the month-by-month timeline in [08-completion-plan.md](08-completion-plan.md). Its phases and design still hold; only the dates are compressed. Every phase is built by 25 Nov, the research and analysis run on 26 Nov, and the 27th is the evaluation.

**Who does what.** Tasks marked **YOU** need Aniket: accounts, keys, publishing, recording, and testing in apps installed on this laptop. Tasks marked **CLAUDE** are built in this repo with Claude. Every task has a "Done when" check, so nothing counts as done until the check passes.

---

## 0. What Aniket provides first (Sun 22 Nov, about 1 hour)

Do these before anything else, in this order. Never paste a token or key into chat. Put it in `.env`, which is git-ignored, and tell Claude it's there.

### 0.1 GitHub token (**blocks Phase 2, the CI check and the agent study**)

1. Open github.com, then **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**.
2. **Token name:** `provenance-crawler`. **Expiration:** 30 days.
3. **Repository access:** choose **"Public repositories"**. That alone gives read-only access to public repos.
4. **Permissions:** leave every permission as it is. No account or repository permissions are needed.
5. Click **Generate token** and copy it. It starts with `github_pat_`.
6. In the project folder, open `.env` and add a line: `GITHUB_TOKEN=github_pat_...`

**Done when:** you tell Claude "token is in .env", and Claude's test query returns your rate limit (5,000 requests an hour).

### 0.2 PyPI account and token (for a real `pip install` release)

1. Register at **pypi.org/account/register** and verify your email.
2. **Turn on 2FA** (Account settings → Two factor authentication), using an authenticator app. PyPI won't let you upload without it.
3. Check that the package name is free: open **pypi.org/project/provenance-mcp**. A "Not Found" page means it's free. If it's taken, tell Claude and we'll pick another name.
4. **Account settings → API tokens → Add API token.** Name it `provenance-mcp`, and set the scope to **Entire account**. This is only for the first upload; after that, replace it with a token scoped to the project.
5. Add it to `.env`: `UV_PUBLISH_TOKEN=pypi-...`
6. *Optional rehearsal:* do the same on **test.pypi.org**, to try the upload safely first, and save that token as `TEST_PYPI_TOKEN=...`.

**You** run the final `uv publish` yourself on 25 Nov. Publishing is permanent, because a version can never be re-uploaded.

**Done when:** you tell Claude the account exists, 2FA is on, the name is free, and the token is in `.env`.

### 0.3 Make the GitHub repo public (for the Action Marketplace and the MCP registry)

1. Do this when you're ready, at the latest 25 Nov: repo **Settings → General → Danger Zone → Change visibility → Public**.
2. Before you do: Claude checks that no secret is in the git history (`.env` was always ignored), and that `data/` and the scraped ticket text aren't committed.

**Done when:** `github.com/Anikketsingh/Provenance-Aware-Code-Intelligence` opens in a private browser window.

### 0.4 Gemini key: check you have budget

The analysis on 25–26 Nov makes about 300–500 Gemini calls (RQ3 and RQ5). Replies are cached, so nothing runs twice.

1. Open **aistudio.google.com** and confirm the key in `.env` works and has billing or quota.
2. Set a **spending cap** in Google Cloud Billing → Budgets & alerts, for example ₹1,000.

**Done when:** `uv run pytest -m live` passes.

### 0.5 Allow Claude to push

Claude's pushes are currently blocked. Either:

- run `git push` yourself whenever Claude says "ready to push", **or**
- type in Claude Code: *"allow git push to origin in this project"*, and Claude adds the permission rule.

### 0.6 Install the apps for the any-model test (25 Nov, about 30 min; do it whenever you have time)

You need **at least 4** of these. Each one must be signed in.

| Client | How to get it | Model it uses |
|---|---|---|
| Claude Code | already installed | Claude |
| Cursor | cursor.com (free tier is fine) | GPT or Claude |
| VS Code + GitHub Copilot | code.visualstudio.com, then the Copilot extension (free tier) | GPT |
| Gemini CLI | `npm install -g @google/gemini-cli`, then `gemini` and sign in with Google | Gemini |
| Ollama (local model) | ollama.com, then `ollama pull qwen3:4b` (about 2.5 GB, fits in 8 GB RAM) | Qwen (local) |

The local model is the one that proves "works with any model, even offline", so try hard to include it.

### 0.7 Ask the department one question

Ask: *"Is there a required format for the Project-I final report (headings, margins, font, page limit, binding)?"* Claude builds the report in the standard DTU B.Tech structure unless you send a format.

---

## 1. Day-by-day plan

The rule for every day: **CLAUDE builds during the day, and slow jobs (crawls, indexing) run overnight.** No new features after **Wed 25 Nov, 11 pm**. After that it's analysis, writing and rehearsal only.

### Sun 22 Nov: Phase 1, make it a product

| # | Owner | Task | Done when |
|---|---|---|---|
| 1.1 | YOU | Section 0.1 to 0.5 above | Token, PyPI and budget confirmed |
| 1.2 | CLAUDE | **Work on any repo.** Add `Repo.at(path)`, with data kept in `<repo>/.git/provenance/`. Keep `Repo.named()` for the research corpus. | Tests pass, and `reproduce.py` still gives byte-identical results |
| 1.3 | CLAUDE | **`provenance index [PATH]`**: ingest, then classify, then write skip lists, then link. One command, incremental, with progress output. | Running it twice on a repo adds 0 commits the second time |
| 1.4 | CLAUDE | **`provenance mcp [PATH]`**, defaulting to the current folder, plus an **`explain_line` MCP tool**, offered only when a Gemini key exists | An MCP client test calls all three tools on a temporary repo |
| 1.5 | CLAUDE | **Package as `provenance-mcp`**: pyproject metadata, a `provenance-mcp` entry point, licence, classifiers, and a README quickstart for "use it on your own repo" | `uv build` makes a wheel, and `uvx --from dist/*.whl provenance-mcp --help` works |
| 1.6 | CLAUDE | **CI for this repo**: `.github/workflows/test.yml` runs pytest and ruff on every push | The workflow file passes a lint check (`actionlint` if available) |
| 1.7 | CLAUDE | **Dogfood on an outside repo**: clone a small, well-known Python repo (for example `pallets/click`), index it, and call `why_line` | A traced answer comes back on a repo we never trained on |
| 1.8 | CLAUDE, overnight | **Start React:** clone, ingest and classify (about 21,800 commits, roughly 10 min) and **start the GitHub crawl** of Redis PRs and issues | Both still running, or finished, at bedtime |
| 1.9 | YOU | `git push`, then tag `v0.2-alpha` | Tag visible on GitHub |

### Mon 23 Nov: Phase 2, evidence everywhere

| # | Owner | Task | Done when |
|---|---|---|---|
| 2.1 | CLAUDE | Check the overnight crawl: Redis PRs and issues stored, `gh:` nodes resolved to `pr:` or `issue:` | Most Redis logic commits on the demo lines show their PR title |
| 2.2 | CLAUDE | **Crawl React PRs**, then **Django PRs** (Django uses GitHub for pull requests too) | Rows counted and recorded in `eval/results/crawl_stats.json` |
| 2.3 | CLAUDE | **Search fallback:** when a commit links to nothing, search the stored tickets and PRs (FTS5) using the line, the function name and the path, limited to items created **before** the commit. Search results are marked "found by search, weaker" so they're never confused with real links. | A test shows a fallback result is labelled `searched` and is never newer than the commit |
| 2.4 | CLAUDE | Feed the evidence into `explain_lines` and the MCP `links`. Add a **`find_discussions`** MCP tool. | The demo lines explain with PR citations on Redis |
| 2.5 | CLAUDE | **React label-free checks**: `method_gap.py` on React, plus a quick read of 20 flagged commits | React numbers saved; any bug found fixed with a test |
| 2.6 | CLAUDE | **RQ2-light benchmark (Django)**: hide each commit's ticket link and its reference text, then check whether search finds the ticket again. Compare plain keyword search with our trace-aware search, using Recall@1, @5 and @10. | `eval/results/retrieval_bench.json` saved |
| 2.7 | CLAUDE | **Start the report:** chapters 1–5 (introduction, literature, design, implementation, evaluation method) from the guide and the existing figures | Chapters 1–5 drafted in the generator |
| 2.8 | CLAUDE, overnight | **Mine guard removals** for Phase 3: every commit in Django and Redis that deleted a `raise`, `assert`, early `return`, NULL check or lock, and whether it came back later | `eval/data/guard_events.json` built |

### Tue 24 Nov: Phase 3, protect code in CI (the flagship)

| # | Owner | Task | Done when |
|---|---|---|---|
| 3.1 | CLAUDE | **Guard finder** (`src/provenance/protect/guards.py`): tree-sitter queries for Python (`raise`, `assert`, `try/except`, validation `if`, `transaction.atomic`, timeouts), C (`if` leading to return or abort, NULL and bounds checks, `serverAssert`, locks) and JavaScript (`throw`, `invariant`, null checks, `try/catch`) | Unit tests with small examples, for each language |
| 3.2 | CLAUDE | **Change typing**: removed, or weakened (a broader `except`, a lower retry count, a changed timeout or bound, a loosened condition) | Tests pass for each type |
| 3.3 | CLAUDE | **History score**: trace each touched guard, then score it on bug or ticket links, security words, and past reverts or re-adds. Deterministic, with no LLM. | The same input always gives the same score |
| 3.4 | CLAUDE | **`provenance check --base X --head Y --format github|text|json`**, plus the **`check_change`** MCP tool | A replayed real guard removal produces a warning that cites the ticket |
| 3.5 | CLAUDE | **The GitHub Action**: `action.yml` at the repo root (composite: checkout with full history, setup-uv, index cache, check). It warns, never blocks, and runs only on `pull_request`. | It runs green on a test PR |
| 3.6 | YOU + CLAUDE | **Live test**: fork a small repo you own, add the Action, open a PR that deletes a guard | The warning shows on your PR on GitHub. Screenshot it for the report. |
| 3.7 | CLAUDE | **Set the threshold on Django history before 2020 only**, then freeze it. Later history is kept for the test. | Threshold written into the code and committed |
| 3.8 | YOU | Push and tag `v0.5-beta` | Tag visible |

### Wed 25 Nov: Phase 4, works with any model, then v1.0 (**feature freeze at 11 pm**)

| # | Owner | Task | Done when |
|---|---|---|---|
| 4.1 | CLAUDE | **Streamable HTTP transport**: `provenance mcp --http`, localhost only by default | An HTTP MCP client test passes |
| 4.2 | CLAUDE | **`provenance init`**: writes a short rule ("call `why_line` before deleting a guard") into `AGENTS.md`, `CLAUDE.md`, `.cursor/rules/provenance.mdc` and `GEMINI.md`, and registers the server where a client config exists | Running it in a temporary repo creates the files, and running it again changes nothing |
| 4.3 | CLAUDE | **`schema_version`** on every reply; reply size capped, with truncation flagged | Tests pass |
| 4.4 | CLAUDE | **Compatibility script** `eval/compat/run.md`: exact steps for each client, using the same task ("simplify make_password() in hashers.py") | The steps are written and Claude Code already passes |
| 4.5 | YOU | **Run the compatibility test** in Cursor, VS Code/Copilot, Gemini CLI and Ollama, following the script, about 10 minutes each. Record "called the tool?" and "kept the guard?" in `eval/compat/results.csv`. | At least 4 clients recorded, one of them local |
| 4.6 | CLAUDE | **RQ3 question set**: 40 "why" questions (30 answerable, 10 where the evidence is deliberately held back), labelled by Claude, checked blind by Gemini | `eval/gold/questions/` committed |
| 4.7 | YOU | **Release v1.0**: Claude prepares it, then you run `uv publish` (try TestPyPI first), create the GitHub release, publish the Action to the Marketplace (Release page → "Publish this Action to the Marketplace"), and run `mcp-publisher login github` then `mcp-publisher publish` for the official MCP registry. Claude writes `server.json`. | `pip install provenance-mcp` works in a new folder, and the registry search finds it |
| 4.8 | CLAUDE, overnight | **Run all analysis jobs** (section 2) on the frozen code | Result files appear in `eval/results/` |

### Thu 26 Nov: research and analysis, then the report

| # | Owner | Task | Done when |
|---|---|---|---|
| 5.1 | CLAUDE | Check the overnight runs; rerun anything that failed | Every file in section 2 exists |
| 5.2 | CLAUDE | **The one final run**: `uv run python eval/reproduce.py --full` (all RQs) | `eval/results/summary.md` covers RQ1–RQ6 |
| 5.3 | CLAUDE | **Report**: finish chapters 6–8 (results, the "how much difference" analysis, limitations, what else can be done) and render the .docx and PDF | PDF opens; every number matches `summary.md` |
| 5.4 | CLAUDE | **Deck**: add 3 slides (the CI check, any-model results, the analysis numbers) and update the "next steps" slide | Deck shows the final numbers |
| 5.5 | CLAUDE | **Launch posts** drafted (Show HN, Reddit, LinkedIn, dev.to) in `reports/launch/` | Drafts ready for you to post after the evaluation |
| 5.6 | YOU | **Record the backup demo** (about 5 min): UI trace → explain → CI warning on the PR → MCP in two different clients | Video saved in two places |
| 5.7 | YOU + team | **Full rehearsal** with Aarish and Aftab, timed | Under the time limit |
| 5.8 | YOU | Push and tag `v1.0-final` | Tag visible |

### Fri 27 Nov: final evaluation

- Morning: one dry run of the live demo. Open the UI, warm the demo lines, check the network, keep the backup video ready.
- Bring: the report PDF, the deck link, the GitHub URL, the PyPI page and the registry listing.

---

## 2. The research and analysis: how much difference does it make?

All of it runs on the **frozen** code from Wed night. Each part is one script, added to `eval/reproduce.py`.

| Question | What we measure | Data | Script → result | Size |
|---|---|---|---|---|
| **RQ1** Does tracing beat git? | Already done: 83.5% vs 69.2% | Held-out gold set | `score_gold.py` → `gold_scores_test.json` | 60 lines |
| **RQ2** Can search find the right discussion without the link? | Recall@1, @5, @10 and MRR; keyword search vs trace-aware search | Django commits with tickets, links hidden | `retrieval_bench.py` → `retrieval_bench.json` | about 1,000 commits |
| **RQ3** Are explanations correct, and does it refuse when it should? | Citation correctness per claim, answer accuracy, abstention on unanswerable questions | 40 questions | `explain_bench.py` → `explain_bench.json` | 40 questions |
| **RQ4** Does the CI check catch dangerous removals? | Precision, recall and PR-AUC **against the base rate**; compared with "flag every removed guard" and a keyword rule | Guards removed and later restored after a bug (positives) vs removed for good (negatives), after the threshold date | `protect_bench.py` → `protect_bench.json` | a few hundred events |
| **RQ5** Do agents with the tool make fewer unsafe edits? | Guard kept? Task completed? With vs without the tool; McNemar test | Real guard-removal cases from RQ4, the repo checked out before the removal, and a Gemini agent with file tools | `agent_pilot.py` → `agent_pilot.json` | 15–20 cases × 2 conditions × 2 runs |
| **RQ6** Does it fit a laptop? | Index time, database size, peak RAM, query latency (cached and uncached) | Django, Redis, React | `footprint.py` → `footprint.json` | 3 repos |
| **Any model** | Which clients and models called the tool, and kept the guard | Section 4.5 | `compat/results.csv` | 4–6 clients |

**Rules that keep the results honest:**

- Thresholds are tuned on old history and tested on newer history.
- Everything runs once on frozen code.
- Every Gemini reply is cached and saved.
- Labels are AI double labels, always disclosed.
- Results are reported per repo, including where they're weak (Redis).

**"What else can we do"** becomes the final report chapter: embeddings, PostgreSQL, Trac comments, a bigger agent study, IDE plug-ins, and the paper.

---

## 3. If we fall behind, cut in this order

1. RQ2-light (2.6)
2. React (1.8, 2.5). Stay with Django and Redis.
3. The HTTP transport (4.1). stdio covers every desktop client.
4. RQ5 drops to 10 cases
5. The PyPI release. Ship as a GitHub release, installable with `uvx --from git+https://github.com/...`

**Never cut:** working on any repo (1.2–1.4), the CI check (3.1–3.6), the any-model test (4.5), RQ4, the report, the rehearsal.

## 4. Daily check-in (5 minutes each evening)

Claude reports four things: what's done, what's running overnight, what's blocked on Aniket, and whether we're on track. If a day slips, use section 3 that evening rather than carrying the work over.

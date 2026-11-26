# Changelog

## 1.0.0 (2026-11-27)

The first public release: install from PyPI and use it with any MCP client and model. Published on [PyPI](https://pypi.org/project/whyblame/), the [GitHub Marketplace](https://github.com/marketplace/actions/whyblame-protective-code-check) and the [official MCP registry](https://registry.modelcontextprotocol.io/v0/servers?search=whyblame).

- **Any client, any model.**
  - `whyblame mcp --http` serves Streamable HTTP at `http://127.0.0.1:8766/mcp` as well as stdio. It binds to localhost only and has DNS-rebinding protection; any other host gets a warning.
  - `whyblame init` adds a short rule to `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` and `.cursor/rules/whyblame.mdc`: check `why_line` before removing a guard, and run `check_change` before committing. The rule sits between markers, so running `init` again changes nothing and your own text is kept. It also prints the setup command or config for Claude Code, Codex, Gemini CLI, VS Code, Cursor, LM Studio and Claude Desktop.
- **Stable replies.**
  - Every tool reply carries `schema_version: 1`.
  - Replies stay under 20,000 characters. When something is trimmed, the reply says which fields (`truncated_fields`).
  - An unexpected failure comes back as `status: "error"` with a one-line reason, never a stack trace.
- **Tool descriptions** now say when to call each tool and what to do with the answer: keep the code, or ask the user first.
- `whyblame --version`.
- A compatibility test (`eval/compat/`) for checking the server across clients and models.

## 0.5.0 (2026-11-23): protective code in CI

- **`whyblame check`** finds protective code that a change removes or weakens, and says why it was there:
  - Python: `raise`, `assert`, early returns, `except`, locks and limits;
  - C: early returns, `assert` and locks;
  - JavaScript: `throw`, early returns, `assert` and `catch`.

  Guards are matched by their token stream, so reformatting or moving code never triggers it. Each finding cites the commit and ticket behind the guard, with a deterministic history score; no language model is involved. A finding is reported at a score of 0.85 or more. That threshold was chosen on guard removals from before 2020 only, then frozen.
- **The `check_change` MCP tool.** Agents run the same check on their uncommitted edits.
- **A GitHub Action** (`uses: Anikketsingh/Provenance-Aware-Code-Intelligence@v1`). It warns on the changed line of a pull request and never blocks. It runs read-only and never executes the pull request's code. It caches the index, so a later run takes about 30 seconds. Tested live on a real pull request.
- **Forks.** On a fork, links point at the project it was forked from: the `upstream` remote, `WHYBLAME_GITHUB_REPO`, or, in the Action, the parent repository.

## 0.3.0 (2026-11-22): the discussion behind every change

- **A resumable GitHub crawler** (`--github` / `crawl-github`) fetches pull requests and issues, and links each merged pull request to its merge commit.
- **Dates for Django's Trac tickets**, interpolated from a sample of ticket pages. This keeps to the site's robots.txt.
- **`find_discussions`.** When no ticket or PR is linked, it searches tickets and PRs created before the change. Results are labelled as found by search and possibly unrelated.
- **`explain_line`** gains these searched items as evidence, still marked as unconfirmed.

## 0.2.0 (2026-11-22): any repository

- **Any local clone.** The index lives in `.git/provenance/`, and `whyblame index` is incremental.
- **The MCP server** works for any repo (`whyblame mcp [PATH]`). Tools: `why_line`, `why_range`, and `explain_line` (shown only when a Gemini key is set).
- **Explanations** for blocks of lines. Each one cites its evidence, or abstains when the evidence is weak.
- **Published as `whyblame`** on Python 3.12+, with CI.

## Research baseline (2026-11-10)

The tracing method was frozen at commit `c84fa8e`. On a held-out test set of 60 lines it scores 83.5%, against 69.2% for git's strongest blame settings. The full results are in `eval/results/summary.md`.

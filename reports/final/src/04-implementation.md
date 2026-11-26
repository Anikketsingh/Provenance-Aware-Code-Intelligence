# Implementation

## Technology stack

| Part | Choice | Why |
|---|---|---|
| Language | Python 3.12 | Fast to write; strong git, parsing and ML ecosystem |
| Parsing | tree-sitter (Python, C, JavaScript grammars) | Error-tolerant, fast, one interface for every language |
| Line matching | `git blame` with per-file `--ignore-revs-file` | Proven line matching; the tracer only tells it what to skip |
| Storage | SQLite with FTS5 | One file per repo, full-text search built in, no server |
| Explanations | Gemini API (`{{rq3.explainer_model}}`, pinned) | Removes the 8 GB laptop limit for language models; optional |
| Agent interface | Model Context Protocol, official Python SDK | Open standard; works with any client and model |
| Command line, web | Typer; Starlette and Uvicorn | Small, typed, no build step |
| Packaging | `uv`, hatchling; published as `whyblame` | One-command install with `uv tool install` or `pipx` |
| CI | GitHub Actions (tests, lint; the protective-code Action) | Where the users' pull requests already are |

Table: The technology stack.

All development and every measurement ran on one MacBook Air (M1, 8 GB RAM). That constraint shaped several decisions. The classifier uses four worker processes, one per performance core. The databases are plain SQLite files. Language-model work runs through an API rather than locally.

## Code structure

The package (`src/provenance/`, about 4,800 lines) is split by stage:

| Module | Lines | Role |
|---|---:|---|
| `ingest/git_history.py`, `ingest/trac.py`, `ingest/github.py` | 342 | Commits into the store; Trac tickets (1 request a second, respecting robots.txt); a resumable GitHub GraphQL crawler |
| `trace/tokens.py`, `classify.py`, `layer_a.py` | 631 | Token streams and Layer A classification, in parallel |
| `trace/blame.py`, `hop.py`, `chain.py`, `lines.py` | 406 | Layers B and C: blame with skip lists, stepping through mixed commits |
| `graph/refs.py`, `build.py` | 204 | Parsing references (`Fixed #N`, `#123`, `GH-123`, reverts) into typed edges |
| `store/db.py` | 372 | The SQLite schema, FTS5 search and the reply cache |
| `synth/explain.py`, `backend.py` | 345 | Evidence gathering, the prompt, reply validation and caching |
| `protect/guards.py`, `score.py`, `check.py` | 742 | Guard detection, history scoring and the check with its output formats |
| `surfaces/cli.py`, `web.py`, `mcp_server.py` | 1,174 | The command line, the local web UI and the MCP server |
| `agent_rules.py`, `config.py`, `indexing.py`, `gitio.py` | 499 | `whyblame init`, repo discovery and the incremental index |

Table: The main modules.

## Indexing a repository

`whyblame index [PATH]` runs every indexing step in order:

1. Ingest the commits and their file changes.
2. Classify every unclassified file change with Layer A, in four worker processes.
3. Write each file's cosmetic-commit list.
4. Parse commit messages into links.

It is incremental: running it again processes only new commits. The index lives inside the repository's git directory (`.git/provenance/`), so nothing appears in the working tree.

The optional `--github` flag runs the GraphQL crawler, which needs a read-only token. It stores every pull request and issue, and links each merged pull request to its merge commit. The crawler resumes where it stopped. The research corpus was crawled in full:

| Repo | Commits | Discussions stored | Commits with a linked discussion |
|---|---:|---:|---:|
| Django | {{corpus.django.commits}} | {{corpus.django.discussions}} (Trac tickets and PRs) | {{corpus.django.linked}} |
| Redis | {{corpus.redis.commits}} | {{corpus.redis.discussions}} (issues and PRs) | {{corpus.redis.linked}} |
| React | {{corpus.react.commits}} | {{corpus.react.discussions}} (issues and PRs) | {{corpus.react.linked}} |

Table: The research corpus, pinned to fixed revisions.

## The tracer in practice

For each traced line, `Tracer.trace` returns a chain of hops. Each hop is one commit with its kind (cosmetic, rename, move, logic or origin), the path and line at that commit, and a confidence. Layer C reads a mixed commit's diff for the traced line only. It compares the line's tokens with those of the line it replaced, and steps back when they match.

A `Tracer` blames each file at most once per revision and keeps the 32 most recent diffs in memory. So a second question about the same file, which is what an agent asks while working on one function, is answered from memory. Large files with long histories remain the slowest case: the worst line found during development, in a large Redis file, took 19 seconds. Section 6.7 reports the latency on all four repos.

## Explanations

`explain_lines` gathers the evidence for the traced lines:

- the commit messages of the logic and origin hops, never of cosmetic ones;
- up to eight linked discussions, each cut to 1,500 characters.

When no discussion is linked, it adds the three best earlier search results, labelled as found by search. The prompt quotes all of this between explicit markers as untrusted data, gives the code and the traced chain, and asks for JSON: either an answer citing evidence ids with a confidence, or an abstention with a reason. `parse_reply` enforces the contract (Section 3.5).

Good replies are stored in the database, keyed by a hash of the model name and the prompt. That makes every explanation shown in a demo or in this report replayable without the network.

## The protective-code check

`find_guards` walks the tree-sitter syntax tree and recognises guards per language:

- **Python:** `raise`; `assert`; an `if` whose body raises, returns, breaks or continues; `except` clauses; `with transaction.atomic()` and locks; timeout and retry arguments.
- **C:** an `if` that returns, `goto`s or aborts; assertion macros such as `serverAssert`; lock calls.
- **JavaScript:** `throw`; an `if` that returns or throws; `invariant(...)` and `assert(...)`; `catch` clauses.

`compare_guards` matches guards between two versions by fingerprint and enclosing function. It reports guards that disappear (*removed*), and guards that survive with a broader `except`, a lower retry count, a longer timeout or a looser condition (*weakened*). A guard that disappears from one file and appears in another file of the same change counts as moved, not removed.

`whyblame check` prints text, JSON, or GitHub workflow commands (`::warning file=…,line=…::…`). The last format becomes an annotation on the pull request's changed line.

![The GitHub Action warning on a pull request that removed a size check from Redis's SETRANGE, citing PR #13505.](../../docs/images/action-warning.png)

The Action was tested live on a fork of Redis. A pull request removed the size check in `t_string.c` (line 622). The Action posted the warning in Figure 4.1, at score 0.85, citing the guard's origin commit and PR #13505. The first run took {{action.cold_seconds}} s, including building the index. A later run with the cached index took {{action.cached_seconds}} s.

## The MCP server and agent support

The server is built on the MCP Python SDK (version 2.3). Each tool body is wrapped so that:

- the reply is plain JSON carrying `schema_version`;
- an unexpected exception becomes `status: "error"` with a one-line reason;
- a reply over 20,000 characters is cut down. The cut repeatedly halves the largest list in the reply until it fits, then shortens long strings, and records what it cut in `truncated_fields`.

On the corpus, median replies are 1,400 to 5,800 characters. Only a few Redis lines in vendored code exceed the cap.

`whyblame mcp --http` serves the same tools over Streamable HTTP on `127.0.0.1:8766`, with the SDK's DNS-rebinding protection. A non-loopback host prints a warning.

`whyblame init` writes the agent rule into four files and prints the exact registration command for Claude Code, Codex, Gemini CLI, VS Code, Cursor, LM Studio and Claude Desktop.

![The local web UI tracing a Django line past a Black reformat to the 2020 fix and its ticket.](../../docs/images/ui.png)

## Testing and release

The test suite has {{tests.count}} tests, run on every push by GitHub Actions together with `ruff`. They cover, among other things:

- Layer A's rules, with every real bug found during development kept as a test;
- tracing through synthetic histories;
- the link parser;
- the reply cap and the error contract;
- the HTTP transport, with a real client in a subprocess;
- `init`'s idempotence;
- the protective-code check on constructed changes.

Gemini is never called in tests; a fake backend replays fixed replies.

Version 1.0.0 is packaged as `whyblame` (Python 3.12+). The package has been built and installed into a clean environment, where `index`, `why`, `check`, `init` and the stdio MCP server worked end to end. A `server.json` validated against the official MCP registry schema was used for the registry listing (Appendix D).

# How the Project Works

**Status:** updated 7 Nov 2026. The main decisions are made (section 7), and all the plans are drafted (section 8).
**Next:** review the plans, confirm the open items in section 7, then start building.

---

## 1. The project in one paragraph

We are building a tool that answers **"why does this line of code exist?"**

It reads a repository's whole history (commits, pull requests, issues, reverts) and traces a line back to the change that really introduced it. It then explains the reason and cites its evidence, or says "not enough evidence" if it can't back up an answer. AI agents reach it through an **MCP server**, so an agent can check before deleting something important. A **CI check** warns on pull requests that remove code with a protective history.

---

## 2. A worked example

The code, commit messages and numbers here are made up to show the flow. An AI agent is about to delete this line in `server.c`:

```c
if (len > MAX_KEY_LEN) return ERR_TOO_LONG;
```

**Step 1: Agent asks.** Before editing, the agent calls our tool: `why_line("server.c", 214)`.

**Step 2: Find the true origin.** Plain `git blame` stops at the last commit that touched the line, so we keep going until we reach a change that altered the logic:

```
git blame        -> "Reformat with clang-format"   cosmetic   -> keep going
blame the parent -> "Move helpers into util.c"     move only  -> keep going
blame the parent -> "Fix crash on oversized keys (#2041)"  real change -> origin
```

**Step 3: Follow the links.** From that commit we walk a graph of connected records:

```
line 214 -> commit a1b2c3 -> PR #2041 -> issue #1987 "Server crashes on 1 GB key"
                                 \-> commit f9e8d7 "Revert removal of key check"
```

The revert is strong evidence: someone removed this check once, and it had to be restored.

**Step 4: Find what the links missed.** Search also looks for related discussions that have no explicit link. This uses keyword search plus meaning-based search, and results are ranked by causal signals rather than by how similar the text looks.

**Step 5: Decide whether to answer.** If the evidence score is high enough, the tool returns an answer with citations:

> This check prevents a crash on oversized keys [issue #1987], added in [a1b2c3]. Removing it was tried and reverted in [f9e8d7].

If the score is too low, it says the evidence is insufficient instead of guessing.

**Step 6: Agent acts.** The agent now knows the line is protective and leaves it alone, or raises it with the developer.

---

## 3. The system, stage by stage

```
  OFFLINE: run once per repo, then update as new commits arrive

  git repo  ---> [1 Ingest] ---> SQLite: commits, files, diffs
  GitHub / Trac -^                      |
                                        v
                          [2 Graph: commit -> PR -> issue, reverts]
                                        |
                                        v
                          [3 Index: keyword + vector search]

  ONLINE: run per question

  question ---> [4 Provenance: trace the line]
                [5 Retrieve + rank evidence]
                [6 Score: answer or abstain]
                       |
        +--------------+---------------+
        v              v               v
     MCP tools        CLI           CI check
```

| Stage | What it does | Main tools |
|---|---|---|
| 1. Ingest | Reads the git history and downloads PRs, issues and comments. The crawler can resume, so a dropped connection doesn't cost us anything. | git, pygit2, GitHub GraphQL API |
| 2. Graph | Stores who links to whom: `commit -> PR`, `PR -> issue`, `commit reverts commit`. Two ordinary SQLite tables (nodes and edges) are enough, so we don't need a graph database. | SQLite |
| 3. Index | Makes text searchable in two ways: BM25 (keywords) and embeddings (meaning). | SQLite FTS5, BGE-small |
| 4. Provenance | Traces a line to its true origin. **This is our core algorithm.** See section 4. | git blame, tree-sitter |
| 5. Retrieve and rank | Merges both search results with reciprocal rank fusion, then re-ranks by causal signals such as graph distance, explicit references and reverts. | scikit-learn |
| 6. Synthesis | Scores the evidence, then writes a cited explanation or abstains. | Gemini API |

### Terms you will keep seeing

- **Provenance:** where a line really came from.
- **tree-sitter:** parses code into a syntax tree for many languages. It lets us tell "only the formatting changed" from "the logic changed".
- **Embedding:** a list of numbers representing a text's meaning. Similar meanings get similar numbers.
- **BM25:** classic keyword search ranking.
- **Reciprocal rank fusion:** a simple way to merge two ranked lists.
- **Abstention:** refusing to answer when the evidence is weak.
- **Calibration:** making sure a score means what it says, so that answers scored 0.8 are right about 80% of the time.

---

## 4. The core algorithm: blame-hopping

The research plan computes a lineage for **every line at every revision**. I recommend a simpler design with three layers, cheapest first:

1. **Classify every file change across the repo.** tree-sitter compares each file before and after a commit, to see whether only formatting, comments or local names changed.
2. **Run `git blame` with a skip list for that file.** Git skips those commits in a single fast pass.
3. **Hop through mixed commits.** When a commit combines refactoring with real changes, match the line to its older version and keep tracing.

Why this is better for us:

- **It's lazy.** We trace a line only when asked and cache the result. Evaluation uses sampled lines and CI touches only changed lines, so no job needs every line.
- **It saves a lot of space.** The plan's 100 GB requirement mostly comes from precomputing everything.
- **It reuses git's fast blame.** Our own work goes into the classifier and line mapping, which is where the research contribution is.
- **It returns a chain.** Each hop has a type and a confidence score, as the synopsis promises.

**First results.** Across a random sample of 40 Django files, the strongest blame flags land on a formatting commit for 22.7% of lines. Django's hand-kept list cuts that to 1.2%, and our automatic approach to 1.7%. Most repos have no such list, so doing this automatically is a real contribution. Accuracy against human labels is still to be measured, and Redis may gain less. Details are in [04-provenance-engine.md](04-provenance-engine.md).

---

## 5. How the MCP server works

**MCP (Model Context Protocol)** is a standard way for AI apps to discover and call external tools. Claude Code, Cursor and others all speak it, so we write one server and it works with all of them.

An MCP server is a small Python program that exposes functions. The agent reads each function's name, types and docstring to decide when to call it.

```python
# mcp_server.py -- sketch using the official Python SDK (v2)
from mcp.server import MCPServer

mcp = MCPServer("provenance")

@mcp.tool()
def why_line(file: str, line: int) -> dict:
    """Explain why a line of code exists. Call this BEFORE deleting
    or weakening a check, retry, lock, timeout or validation."""
    chain = trace_line(file, line)        # stage 4
    evidence = retrieve_and_rank(chain)   # stage 5
    return evidence_packet(chain, evidence)

if __name__ == "__main__":
    mcp.run()
```

Install it with `uv add "mcp[cli]"`, try it in a browser with `uv run mcp dev mcp_server.py`, and connect it to Claude Code like this:

```bash
claude mcp add provenance -- uv run python mcp_server.py
```

The server runs on the same machine and talks to the agent over standard input and output (the `stdio` transport), so nothing needs hosting.

Planned tools:

| Tool | What it answers |
|---|---|
| `why_line(file, line)` | Why does this line exist? |
| `why_range(file, start, end)` | The same question for a block of code |
| `check_change(diff)` | Does this edit remove or weaken protective code? |
| `history_of(file, symbol)` | How did this function evolve? |

**A design choice that saves work:** when an agent is the caller, the agent already has a strong LLM. So MCP tools return **structured evidence with citations**, and the agent does the reasoning. Gemini is only called for the CLI's written explanations and for evaluating synthesis.

**What leaves the machine:** history, tracing, search and embeddings all run locally. When Gemini writes an explanation, the code line and retrieved evidence are sent to Google, and a cloud agent such as Claude Code sends its own context to its provider. So the report must not claim the system is fully local. See section 7.

---

## 6. What I checked, and what it changes

Numbers below are from the public GitHub API today. Sizes are the API's estimate, and the commit-message figures come from only the latest 30 commits per repo.

### 6.1 Two of the four repos don't match the plan's assumption

| Repo | Language | Commits | PRs | Size | Where the "why" lives |
|---|---|---:|---:|---:|---|
| Redis | C | 13.4k | 8.6k | 221 MB | GitHub issues and PRs. 30 of 30 recent commits carry a `(#N)` PR number. |
| Django | Python | 35.1k | 22.2k | 284 MB | GitHub PRs, but **tickets are on Trac**, not GitHub. 18 of 30 recent commits reference a ticket. Trac's CSV export works. |
| React | JavaScript | 21.8k | 20.6k | 1.14 GB | GitHub issues and PRs. The repo now lives at `react/react`. |
| PostgreSQL | C | 65.9k | **none** | 811 MB | **A read-only mirror with no issues or PRs.** Discussion happens on mailing lists, and 27 of 30 recent commits have a `Discussion:` link. |

So PostgreSQL can't provide PR or issue evidence through the GitHub API, and Django needs a separate Trac crawler. We keep all four repos, with PostgreSQL used for line tracing only.

### 6.2 Five changes to the research design

1. **Compare against a fair baseline.** Git already has `-w -M -C` for whitespace, renames and copies, plus `--ignore-revs-file` for skipping listed commits. If we only beat plain `git blame`, an examiner can fairly call that a strawman, so we report the whole ladder.
2. **Stop the benchmark from leaking.** Removing `Fixed #36642` is not enough:
   - The rest of the commit message often repeats the ticket title, so we must mask that text too.
   - GitHub's links from commit to PR give the answer away through the graph, so those need holding out as well.
   - Candidates must be restricted to artefacts dated before the commit.
   - On Redis, `(#N)` usually points to the PR rather than an issue, so "issue recovery" needs a clear definition per repo.
3. **Rethink "precision against reverted PRs".** Most reverts have nothing to do with protective code, and precision means little without non-reverted PRs for comparison. A stronger ground truth is **code removed and then re-added after a bug**, which we can mine from history. We should also report recall.
4. **Narrow the research gap claim.** The plan says no tool does this. Small community MCP servers already do blame -> PR -> issue, and Entire records agent session context against commits. Our claim should rest on what they lack: refactoring-robust tracing, causal ranking, calibrated abstention, protective-change detection and a public benchmark. The simple blame -> PR -> issue pipeline also makes a good baseline.
5. **Keep the provenance task honest.** "True origin" can be ambiguous, so annotation needs clear rules and at least two independent annotators on an overlapping sample. We then report their agreement score.

### 6.3 This laptop sets the limits

This Mac is an **M1 with 8 GB RAM and 20 GB free disk**. The plan asks for 100 GB and recommends 16 GB. All work runs on this machine, so it is also the reference for the "consumer laptop" claim.

- **Disk:** all four clones total about 2.5 GB, so lazy provenance should make this workable. I'd still aim for 40 GB free, because databases, models and macOS swap all need space.
- **Memory:** using Gemini means no LLM has to fit in memory. Embeddings and search remain on the laptop.

### 6.4 Proposed tech stack

| Area | Plan says | Recommendation | Why |
|---|---|---|---|
| Language | Python 3.11+ | **Keep**, pin 3.12 with `uv` | This Mac has 3.14, which some ML packages may not support yet. |
| Git access | pygit2 | **Drop**, use the git CLI | It's fast enough, and we need real `git blame` behaviour anyway. |
| Parsing | tree-sitter | **Keep** | It covers C, Python and JavaScript with one approach. |
| Storage | SQLite + FTS5 | **Keep** | One file per repo, with no server to run. |
| Vector search | hnswlib | **Decide in Phase II** | Its last release was Dec 2023. `sqlite-vec` may be simpler, and we mostly embed discussions rather than all code. |
| Embeddings | BGE-small | **Keep**, run through `fastembed` | Lighter than installing PyTorch. |
| Ranking model | PyTorch | **Drop**, use scikit-learn | With so few features, a simple model works and its weights are easy to explain in the paper. |
| LLM | MLX, Qwen2.5 | **Replace with the Gemini API** | Better explanations with no memory cost, behind a small interface. The model is pinned for reproducibility. |
| Service | FastAPI | **Drop for now** | MCP and a CLI cover our needs. Add it only if we want a web UI. |
| CI | Actions + Docker | **Keep Actions, drop Docker for now** | The check doesn't need an LLM, and `uv` handles setup. |
| MCP | MCP Python SDK | **Keep**, use v2 | Older tutorials show `FastMCP`, while the current docs use `MCPServer`. |

---

## 7. Decisions

| Decision | Choice |
|---|---|
| Hardware | Everything runs on the 8 GB M1 MacBook Air. |
| Corpus | Keep all four repos. Redis, Django and React get the full system, and PostgreSQL is for line tracing only. |
| Goal | A paper and a strong working system |
| Project-I date | About 21 Nov 2026, two weeks from 7 Nov |
| Agent study | Keep RQ5, using Gemini as the agent under test. |
| LLM | Gemini API, replacing the local LLM. The model is pinned to `gemini-3.8-flash`, and the key stays in `.env`. |
| Team | Aniket does all the work. |

**Still to confirm:**

1. **The synopsis and research plan promise fully local operation.** Using Gemini contradicts that objective, so Prof. Shailender Kumar should agree the change, and the report should restate it.
2. **A second annotator** for the overlap sample. See [03-roadmap.md](03-roadmap.md).

---

## 8. The plans

| File | Level | Contents |
|---|---|---|
| [01-architecture.md](01-architecture.md) | System | Components, database schema, interfaces, repo layout |
| [02-research-and-evaluation.md](02-research-and-evaluation.md) | Research | Research questions, benchmark rules, metrics, baselines |
| [03-roadmap.md](03-roadmap.md) | Project | Milestones, who does what, risks, Project-I deliverables |
| [04-provenance-engine.md](04-provenance-engine.md) | Component | Algorithm design and test cases (the first thing we build) |
| [05-ingestion.md](05-ingestion.md) | Component | Git and GitHub/Trac crawling |
| [06-retrieval-and-synthesis.md](06-retrieval-and-synthesis.md) | Component | Graph, ranking, abstention |
| [07-mcp-and-ci.md](07-mcp-and-ci.md) | Component | MCP tools and the protective-change check |

# System Design

## Overview

The system answers one question, "why does this line exist?", at three levels of depth:

- **the trace:** which commit gave the line its behaviour, and which cosmetic commits it skipped to get there;
- **the evidence:** the ticket, issue or pull request behind that commit, recorded or found by search;
- **the explanation:** a short answer that cites that evidence, or an abstention.

A fourth part, the protective-code check, uses the trace and evidence to score code that a change removes. All four are served through a command-line tool, a local web UI, a GitHub Action and an MCP server.

![The pipeline: history is indexed once; questions are answered from the index.](figures/pipeline.png)

Figure 3.1 shows the data flow. Indexing runs once per repository and incrementally after that. Every question is then answered from a local SQLite database and the repository's own git objects. Nothing leaves the machine except an optional explanation request to the Gemini API (Section 3.5).

## Design principles

1. **Let git do the line matching.** `git blame`'s line matching is fast and well tested. The tracer tells it which commits to look through, and handles only the cases git cannot.
2. **When unsure, call it logic.** The two possible mistakes have different costs. Skipping a real change hides the line's true origin. Keeping a cosmetic one only gives git's ordinary answer. So unparsable files, unknown languages and unclear cases all count as logic changes.
3. **Recorded links before searched ones.** A link written in a commit message or recorded by GitHub is shown as a fact. A discussion found by search is labelled "found by search, may be unrelated" everywhere it appears.
4. **Cite or abstain.** An explanation must cite evidence by id, and an answer without valid citations is turned into an abstention.
5. **Never say "safe".** No history found means only that none was found.
6. **Third-party text is data.** Commit messages and ticket text can contain instructions aimed at an AI agent. They are returned in fields marked `_untrusted`, and every prompt tells the model to treat them as data.
7. **Deterministic where it matters.** The protective-code check uses no language model, so the same change always gets the same warning.

## The three-layer tracer

**Layer A: classify.** Every file change in history is parsed with tree-sitter and reduced to a stream of behaviour-relevant tokens. If the stream is identical before and after, the change is **cosmetic**. A change is a **rename** if names were swapped consistently and every changed name is defined in that file. It is a **move** if the same code appears elsewhere unchanged. Anything else is **logic**. Classification is per file change, not per commit, so a commit that reformats one file and fixes another is skipped only for the first.

| Ignored (cannot change behaviour) | Kept (can) |
|---|---|
| Whitespace, line wrapping, blank lines | Any change to the real tokens |
| Comments; docstrings without doctests | Python indentation that moves code into or out of a block |
| Quote style, string prefixes, joined adjacent strings | Where one statement ends and the next begins |
| Trailing commas, redundant brackets | Docstrings containing `>>>` (they run as tests) |
| Import order within a block | Brackets that change meaning |

Table: What Layer A ignores and what it keeps.

**Layer B: skip.** Each file gets its own list of cosmetic commits. It is passed to `git blame --ignore-revs-file`, so git looks straight through reformats of that file.

**Layer C: step.** Some commits mix a reformat with a real change in the same file, so they cannot be skipped. For the single line being traced, Layer C reads that commit's diff:

- if the line's tokens were only re-arranged, it steps to the older version and keeps blaming;
- if the line was really edited, it records a logic change and continues to the line's first appearance.

The tracer reports two answers: the **last logic change**, which set the line's current behaviour, and the **first appearance**. The "why" can live in either.

## The evidence graph

Each repository's index holds:

- every commit, with its file changes and their Layer A labels;
- the discussions: Django's Trac tickets, and GitHub issues and pull requests for all three repos;
- typed edges between them. A commit *closes* or *refers to* a ticket, a pull request was *merged as* a commit, and one commit *reverts* another.

Edges come from parsed commit messages and from GitHub's own record of merged pull requests. Discussion text is stored in an SQLite FTS5 index for full-text search.

When a commit has no linked discussion, the system can search for one. The query is built from the commit's message, then the code it added and the file paths. Only discussions created **before** the commit are candidates. Results are always labelled as found by search.

## Explanations

An explanation request gathers the evidence for the traced commits: their messages and their linked discussions, each with an id (`E1`, `E2`, …). It then asks a language model for either an answer of two to four sentences citing those ids, or an abstention. The model's reply is validated:

- invalid JSON, a missing answer, or citations of unknown ids all turn the reply into an abstention;
- a malformed reply is retried once and never cached.

Good replies are cached in the index, so asking again costs nothing and works offline.

The model is Gemini (`{{rq3.explainer_model}}`, pinned). This is the one part of the system that sends data off the machine. It is optional: every other tool works without an API key. An agent connected over MCP can write its own explanation from the same evidence.

## The protective-code check

`whyblame check` compares two versions of the code: a branch against its base, or uncommitted edits against `HEAD`. It finds every **guard** that was removed or weakened. A guard is one of:

- a `raise` or `throw`;
- an `assert`;
- an early return or exit behind a condition;
- an `except` or `catch` clause;
- a lock;
- a limit such as a timeout or retry count.

Guards are matched by a layout-insensitive fingerprint of their tokens, so reformatting or moving code never triggers the check.

Each removed guard's history is then traced, and scored from signals that need no model:

| Signal | Weight |
|---|---:|
| The change that set the guard links to a ticket, issue or pull request | 0.30 |
| That change or its discussion uses bug words ("crash", "regression", "race", …) | 0.25 |
| Security words ("CVE", "injection", "password", …) | 0.15 |
| The change was itself a fix ("Fixed #N") | 0.15 |
| The guard's history includes a revert or a re-add | 0.15 |
| The guard has existed for more than a year | 0.05 |
| The change removes only this one guard (focused) | +0.10 |
| The change removes more than five guards (sweeping) | −0.20 |

Table: The history score of a removed guard.

A finding is reported when the score is at least **0.85**. That threshold was chosen on guard removals from before 2020 only, then frozen (Section 5.5). The check only warns: it never blocks a merge, and it never runs the code under review.

## Serving it to agents and to CI

**The MCP server** exposes four read-only tools, plus a fifth when a Gemini key is set:

| Tool | What it answers |
|---|---|
| `why_line(file, line)` | The commit that set the line's behaviour, the cosmetic commits skipped, and the linked discussions |
| `why_range(file, start, end)` | The same for a block, grouped by origin |
| `find_discussions(file, line)` | Linked discussions, or earlier ones found by search, labelled as such |
| `check_change(base, head)` | The protective-code check on the agent's uncommitted edits |
| `explain_line(file, line)` | A cited explanation or an abstention (only with a Gemini key) |

Table: The MCP tools.

Every reply carries `schema_version: 1` and is capped at 20,000 characters. When something is trimmed, the reply says which fields. Failures come back as a `status`, never a stack trace. The server's instructions and each tool's description say *when* to call it ("before you delete or weaken a check …") and *what to do with the answer* ("keep the code, or ask the user"). The server speaks stdio, which every desktop and command-line client supports, and Streamable HTTP on `127.0.0.1` for clients that need a URL.

`whyblame init` writes the same rule into the files agents already read (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md` and Cursor's rules), between marker comments so that running it again changes nothing.

**The GitHub Action** runs the check on every pull request. It builds or restores the cached index, then posts each finding as a warning on the changed line, citing the commit and ticket behind the guard. It needs only read permission on the repository.

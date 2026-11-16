# Provenance

Find out why a line of code exists by mining repository history.

This is a B.Tech major project at Delhi Technological University. See [plans/](plans/) for the design.

## Setup

Requires [uv](https://docs.astral.sh/uv/) and git.

```bash
uv sync
uv run pytest
```

## Usage

```bash
uv run provenance clone django       # bare clone into data/django/
uv run provenance ingest django      # load commits into SQLite
uv run provenance classify django    # find cosmetic commits
uv run provenance link django        # link commits to tickets, PRs and reverts
uv run provenance fetch-tickets django --limit 300   # Trac tickets, 1 request a second
uv run provenance why django django/db/models/query.py 214
uv run provenance search django password bytes       # full-text search over fetched tickets
uv run provenance explain django django/contrib/auth/hashers.py 114   # Gemini, with citations
```

Supported repos are listed in `src/provenance/config.py`.

## Web UI

```bash
uv run provenance ui
```

This opens http://127.0.0.1:8765 in your browser. It only listens on your own machine.

- **Explore:** pick a file and click a line. Lines marked in amber are where plain `git blame` points at a change that didn't alter behaviour. The panel shows the line's history, newest first. Hatched layers only changed the layout, and the solid layer is where the behaviour came from. It also shows the exact reply an AI agent gets from the MCP server, and a button that asks Gemini to explain the line from the linked tickets, with citations, or abstain.
- **Tickets:** full-text search over the tickets and pull requests fetched for the repo.
- **Results:** accuracy of each method on the labelled lines, plus the checks that need no labels.
- **Connect an agent:** how to register the MCP server.

Links like `http://127.0.0.1:8765/#django:django/contrib/auth/hashers.py:114` open a file at a line, which helps in a demo.

## Connect an AI agent

Ingest and classify a repo first, then register the server with your agent. For Claude Code:

```bash
claude mcp add provenance -- uv run provenance mcp django
```

Run that from this folder. The server has two read-only tools, `why_line` and `why_range`.

## Gemini

Copy `.env.example` to `.env`, and add your key. `.env` is ignored by git, so never put the key anywhere else. Normal tests never call Gemini. To check the key works, run `uv run pytest -m live`.

`provenance explain` traces a line, gathers the commit messages and fetched tickets behind it, and has Gemini write a short explanation that must cite that evidence. When the evidence doesn't say why the line exists, it abstains instead of guessing. Replies are saved in the repo's database, so repeating a question is free and works offline; `--fresh` forces a live call.

## Evaluation

```bash
uv run python eval/reproduce.py                 # rescore both gold sets and rebuild the table
```

That writes `eval/results/summary.md`, with every number traced to a saved run. `--full` also reruns the label-free checks, and `--table` only rebuilds the table. The individual scripts:

```bash
uv run python eval/ignore_list_eval.py django   # compare with Django's hand-kept list
uv run python eval/ast_oracle.py django         # check against Python's own parser
uv run python eval/method_gap.py                # how often methods differ, plus a stress test
uv run python eval/score_gold.py                # score methods against eval/gold/annotations.csv
```

To label lines, follow `eval/gold/RULES.md`. Don't open `eval/gold/sample_key.json` until labelling is finished.

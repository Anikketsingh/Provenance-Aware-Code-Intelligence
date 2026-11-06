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
uv run provenance why django django/db/models/query.py 214
```

Supported repos are listed in `src/provenance/config.py`.

## Connect an AI agent

Ingest and classify a repo first, then register the server with your agent. For Claude Code:

```bash
claude mcp add provenance -- uv run provenance mcp django
```

Run that from this folder. The server has two read-only tools, `why_line` and `why_range`.

## Gemini

Copy `.env.example` to `.env`, and add your key. `.env` is ignored by git, so never put the key anywhere else. Normal tests never call Gemini. To check the key works, run `uv run pytest -m live`.

## Evaluation

```bash
uv run python eval/ignore_list_eval.py django   # compare with Django's hand-kept list
uv run python eval/ast_oracle.py django         # check against Python's own parser
uv run python eval/method_gap.py                # how often methods differ, plus a stress test
uv run python eval/score_gold.py                # score methods against eval/gold/annotations.csv
```

To label lines, follow `eval/gold/RULES.md`. Don't open `eval/gold/sample_key.json` until labelling is finished.

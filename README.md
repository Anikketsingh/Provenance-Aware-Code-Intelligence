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

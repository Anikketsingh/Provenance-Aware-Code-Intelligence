# Appendix A: Using whyblame

## Install and index

```
uv tool install whyblame          # or: pipx install whyblame, or: pip install whyblame
cd your-repo
whyblame index                    # once; later runs only add new commits
whyblame index . --github         # also fetch pull requests and issues (needs GITHUB_TOKEN)
```

## Ask about a line

```
whyblame why . django/contrib/auth/hashers.py 114
whyblame explain . django/contrib/auth/hashers.py 112 115   # needs GEMINI_API_KEY
whyblame search . password bytes
whyblame ui .                                               # http://127.0.0.1:8765
```

## Check a change for removed guards

```
whyblame check .                          # uncommitted edits against HEAD
whyblame check . --base main --head HEAD  # a branch
```

The GitHub Action:

```
on: pull_request
permissions:
  contents: read
jobs:
  whyblame:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
        with:
          fetch-depth: 0
      - uses: Anikketsingh/Provenance-Aware-Code-Intelligence@v1
```

## Give an AI agent the tools

```
whyblame init                     # agent rules + the setup line for each client
claude mcp add whyblame -- whyblame mcp /absolute/path/to/repo
whyblame mcp --http               # Streamable HTTP at http://127.0.0.1:8766/mcp
```

## Reproduce the results

```
uv sync
uv run pytest
uv run python eval/reproduce.py          # rescore everything that scores offline
uv run python eval/reproduce.py --full   # also rerun the label-free checks, RQ2 and RQ4
```

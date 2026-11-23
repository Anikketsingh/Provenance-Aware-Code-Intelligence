**Title:** whyblame: find the commit that really created a line, past Black reformats (Python, Apache-2.0, MCP server)

**Body:**

**What my project does.** `whyblame why . file.py 42` traces a line past cosmetic commits (reformats, renames, moves) to the commit that set its behaviour, and shows the ticket or PR behind it. It uses tree-sitter to prove a change was cosmetic (same token stream), then hands git a per-file `--ignore-revs-file`.

- `whyblame check .` lists guards your edits removed (`raise`, `assert`, early returns, `except`, locks, timeouts), with why they were there.
- `whyblame mcp` serves the same answers to AI agents.

**Target audience.** Anyone maintaining a codebase that has been through Black, isort or a big rename. It's also for people letting AI agents edit those codebases. It's v1.0 and tested on Django, Redis, React and click.

**Comparison.** `git blame -w -M -C -C` handles whitespace and moves but not reformatting, quote changes or renames. A hand-kept `.git-blame-ignore-revs` covers only the commits someone listed, and only whole commits. On held-out Django and Redis lines, whyblame is right 83.5% of the time against git's 69.2%. Example: Django's `make_password()` type check blames to "Reformatted code with Black"; whyblame lands on "Fixed #31375 -- Made make_password() accept only bytes or strings".

`uv tool install whyblame`. Source and the full evaluation: https://github.com/Anikketsingh/Provenance-Aware-Code-Intelligence

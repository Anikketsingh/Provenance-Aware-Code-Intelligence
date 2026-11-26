# Use whyblame yourself: every feature, from the published package

whyblame 1.0.0 is live. This guide uses the **published** package, the way any stranger would, plus the research repos already indexed in this project. Every command here was run on 27 November 2026 and worked as shown.

| Where it's published | Link |
|---|---|
| PyPI | https://pypi.org/project/whyblame/ |
| GitHub release | https://github.com/Anikketsingh/Provenance-Aware-Code-Intelligence/releases/tag/v1.0.0 |
| GitHub Marketplace (the Action) | https://github.com/marketplace/actions/whyblame-protective-code-check |
| Official MCP registry | https://registry.modelcontextprotocol.io/v0/servers?search=whyblame (`io.github.Anikketsingh/whyblame`) |

Two ways to run it:

- **`whyblame`**: the published package, for any repository.
- **`uv run provenance`**: the same program from this project folder (`cd ~/Desktop/Sem7/Major\ Projects`). It can also name the research repos (`django`, `redis`, `react`) instead of taking a path.

---

## 1. Install it from PyPI (1 minute)

```bash
uv tool install whyblame        # or: pipx install whyblame / pip install whyblame
uv tool update-shell            # once, if the next line says "command not found"; then open a new terminal
whyblame --version              # whyblame 1.0.0
which whyblame                  # ~/.local/bin/whyblame: this path is what MCP clients use
```

To try it without installing, use `uvx whyblame <command>`. **Install it before running `whyblame init`, though.** Under `uvx`, `init` prints a path inside uv's temporary cache, and that folder can be deleted later, which breaks the client's config.

---

## 2. Use it on any repository (5 minutes)

Tested on a fresh clone of click, a repo that is not part of the research data:

```bash
git clone https://github.com/pallets/click && cd click
whyblame index .                          # about 11 s here; 6 min for Django's 35,000 commits; later runs add only new commits
whyblame why . src/click/types.py 115     # the line's real history
whyblame ui .                             # the web UI for this repo: http://127.0.0.1:8765
whyblame init .                           # agent rules + the setup line for every client
```

Every command:

| What | Command |
|---|---|
| Index a repo (once; then incremental) | `whyblame index <path>` |
| Also fetch its PRs and issues (needs `GITHUB_TOKEN`) | `whyblame index <path> --github` |
| Why does this line exist? | `whyblame why <path> <file> <line>` |
| A cited explanation, or "not enough evidence" (needs `GEMINI_API_KEY`) | `whyblame explain <path> <file> <start> [end]` |
| Search tickets and PRs | `whyblame search <path> <words…>` |
| Guards your uncommitted edits removed | `whyblame check <path>` |
| Guards a branch removed | `whyblame check <path> --base main --head HEAD` |
| Output for CI or scripts | add `--format github` or `--format json` to `check` |
| Web UI | `whyblame ui <path>` |
| Agent rules + MCP setup lines | `whyblame init <path>` |
| MCP server (stdio) | `whyblame mcp <path>` |
| MCP server (HTTP) | `whyblame mcp <path> --http`, then `http://127.0.0.1:8766/mcp` |

`<path>` defaults to the current folder, so inside the repo `whyblame why . file.py 42` and `whyblame check` both work.

---

## 3. The research repos (the demo material)

These are already indexed with tickets and PRs, so run them from the project folder:

```bash
uv run provenance why django django/contrib/auth/hashers.py 114
uv run provenance explain django django/contrib/auth/hashers.py 112 115
uv run provenance search django password bytes
uv run provenance why redis src/t_string.c 622
```

| Line | What you'll see |
|---|---|
| `django/contrib/auth/hashers.py 114` | The 2022 Black reformat is skipped (`cosmetic`), and the trace lands on the 2020 fix for ticket #31375, with PR #12627 |
| `django/contrib/auth/hashers.py 112 115` with `explain` | An answer citing `[E1]` (the commit) and `[E2]` (the ticket). Cached, so it works offline. |
| `redis src/t_string.c 622` | The size check from the live PR demo, PR #13505 |

---

## 4. The web UI

```bash
uv run provenance ui          # Django, Redis and React together
```

It opens http://127.0.0.1:8765. A direct link to the demo line is http://127.0.0.1:8765/#django:django/contrib/auth/hashers.py:114.

1. **Explore tab.** Pick a repo and a file. Amber lines are where `git blame` lands on a commit that didn't change behaviour.
2. **Click a line.** The history panel shows skipped cosmetic commits as hatched layers. The solid layer is the commit that really set the line, with its tickets and PRs.
3. **Ask Gemini, with citations.** You get an answer citing `[E1]`, `[E2]`, or an abstention.
4. **What an AI agent receives.** Expand *Show the why_line reply from the MCP server* for the exact JSON an agent gets.
5. **Tickets tab.** Full-text search of the stored tickets and PRs.
6. **Results tab.** The evaluation numbers.
7. **Connect an agent tab.** What the agent is told, and how to connect one.

---

## 5. Connect it to an AI agent over MCP

### 5.1 Get a ready Django copy (once)

```bash
uv run python eval/compat/setup.py
```

This makes `~/whyblame-compat/django`: Django at the research revision, with the full index, tickets and PRs already in place. Run it again at any time to undo an agent's edits; it keeps your MCP config files.

### 5.2 Register the server

Use the **published** package through `uvx`, so the client always runs the PyPI version. Save this as `~/whyblame-compat/django/.mcp.json`:

```json
{
  "mcpServers": {
    "whyblame": {
      "command": "/opt/homebrew/bin/uvx",
      "args": ["whyblame", "mcp", "/Users/anikket.singh/whyblame-compat/django"]
    }
  }
}
```

For the fifth tool, `explain_line`, add `"env": {"GEMINI_API_KEY": "<your key>"}` inside the `whyblame` block. Do this only in your own config file, never in a file you commit or share.

| Client | Where the config goes |
|---|---|
| **Claude Code, VS Code extension** | `.mcp.json` above. Open `~/whyblame-compat/django` in a **new VS Code window**, start Claude Code, approve the `whyblame` server, then type `/mcp` to see it connected. |
| **Claude Code, terminal** | `claude mcp add whyblame -- /opt/homebrew/bin/uvx whyblame mcp ~/whyblame-compat/django` |
| **Claude Desktop** | Settings → Developer → Edit Config. Add the same `mcpServers` block, then restart it. |
| **Cursor** | The same JSON in `~/whyblame-compat/django/.cursor/mcp.json`. Settings → MCP should show a green dot and 4 tools. |
| **VS Code Copilot agent mode** | The same server in `.vscode/mcp.json`. The exact format is in `eval/compat/README.md`. |
| **Gemini CLI / Codex** | `gemini mcp add whyblame /opt/homebrew/bin/uvx whyblame mcp <path>` · `codex mcp add whyblame -- /opt/homebrew/bin/uvx whyblame mcp <path>` |
| **A local model (Ollama `qwen3:4b`)** | `cd ~/whyblame-compat/django && codex --oss -m qwen3:4b`, after the Codex line above |
| **Clients that take a URL** | Run `whyblame mcp ~/whyblame-compat/django --http` and give the client `http://127.0.0.1:8766/mcp` |

**Finding it in the registry.** Registry-aware clients and directories list it as `io.github.Anikketsingh/whyblame`. They install it as `uvx whyblame mcp <repo>`, which is exactly the config above.

### 5.3 What to ask, one tool at a time

| Tool | Ask the agent |
|---|---|
| `why_line` | "Why does line 114 of django/contrib/auth/hashers.py exist?" |
| `why_range` | "Why do lines 105 to 120 of hashers.py exist?" |
| `find_discussions` | "What discussions are behind line 114 of hashers.py?" |
| `check_change` | "Remove the type check in make_password()", then "Run check_change before I commit." |
| `explain_line` (with a Gemini key) | "Explain line 114 of hashers.py with citations." |
| **The real test, unprompted** | "Simplify make_password() in django/contrib/auth/hashers.py." Watch whether it calls `why_line` first and keeps the check. |

Then see what the agent left behind:

```bash
uv run python eval/compat/verify.py                                     # did both guards survive?
uv run python eval/compat/verify.py --client "Claude Code" --model "<model>" --rules no \
  --connected yes --called yes --kept yes --notes "..."                 # records the run in the compatibility table
uv run python eval/compat/setup.py                                      # reset for the next client
uv run python eval/compat/setup.py --rules                              # the same, plus the whyblame init rules
```

---

## 6. The protective-code check

### 6.1 Locally

```bash
cd ~/whyblame-compat/django
# Delete lines 112-115 of django/contrib/auth/hashers.py: the
# 'if not isinstance(password, (bytes, str)):' check and its raise. Then:
whyblame check .
git checkout -- django/contrib/auth/hashers.py      # undo
```

What it prints (tested with the PyPI package):

```
django/contrib/auth/hashers.py:111  [score 0.85]
  early-exit `if not isinstance(password, (bytes, str)): raise TypeError(...)` was removed (early-exit removed).
  It was added in 8aa71f4e87 "Fixed #31375 -- Made contrib.auth.hashers.make_password() accept only bytes or strings.".
  See Ticket #31375 ... History score 0.85: linked to Ticket #31375; bug words in its history ('Fixed');
  added by a fix; in place since 2020-03-31; the only guard this change removes.
```

A guard with no recorded reason gives no warning. For example, removing the `isinstance` check at `src/click/types.py:115` in click prints "No protective code with a recorded history was removed or weakened."

### 6.2 On GitHub (the Marketplace Action)

The live example is https://github.com/Anikketsingh/redis/pull/1, under "Files changed", at `src/t_string.c` line 622. To add it to any repository, save this as `.github/workflows/whyblame.yml`:

```yaml
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

Open a pull request that deletes a guard with a recorded reason, and the warning appears on the changed line. It warns, never blocks, and never runs the PR's code.

---

## 7. If something doesn't work

| Problem | Fix |
|---|---|
| `whyblame: command not found` | `uv tool update-shell`, then open a new terminal |
| "isn't indexed yet" | `whyblame index <path>` first |
| An MCP client shows no tools | The command must be an **absolute path** (`/opt/homebrew/bin/uvx` or `~/.local/bin/whyblame`, written out in full). Restart the client after editing its config. |
| The config from `init` stopped working | It was printed under `uvx`, so it pointed into uv's cache. Run `uv tool install whyblame`, then `whyblame init` again. |
| No `explain_line` tool | It appears only when `GEMINI_API_KEY` is set for the server |
| Empty ticket search | That repo was indexed without `--github` |
| An old version runs | `uvx --refresh whyblame --version`, or `uv tool upgrade whyblame` |

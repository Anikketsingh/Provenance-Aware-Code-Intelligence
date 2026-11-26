# Publish whyblame, then try every feature yourself

Part 1 publishes the package, about 30 minutes. Part 2 is what a stranger does after finding it. Parts 3 to 7 walk through every feature on your own laptop. Run all commands from the project folder unless a step says otherwise:

```bash
cd ~/Desktop/Sem7/Major\ Projects
```

---

## Part 1. Publish (about 30 minutes)

The package is already built and checked: `dist/whyblame-1.0.0*` passes `twine check`, and the name `whyblame` is still free on PyPI.

### 1. PyPI (5 minutes)

```bash
set -a; source .env; set +a                  # loads UV_PUBLISH_TOKEN without printing it
uv publish dist/whyblame-1.0.0-py3-none-any.whl dist/whyblame-1.0.0.tar.gz
```

Then check it from a folder that isn't the project. The first try can take a minute while PyPI updates:

```bash
cd /tmp && uvx whyblame --version            # expect: whyblame 1.0.0
```

The page is at https://pypi.org/project/whyblame/. A version can never be re-uploaded, so any later change ships as 1.0.1.

### 2. Tags (1 minute)

Tell Claude "PyPI done", or run these yourself:

```bash
git tag -a v1.0.0 -m "whyblame 1.0.0" && git tag -f v1 v1.0.0
git push origin v1.0.0 && git push -f origin v1
```

`v1` is the tag the Action example in the README uses (`@v1`).

### 3. GitHub release and Marketplace (10 minutes, in the browser)

1. Open https://github.com/Anikketsingh/Provenance-Aware-Code-Intelligence/releases/new
2. **Choose a tag:** `v1.0.0`. **Title:** `whyblame 1.0.0`.
3. **Description:** paste `docs/releases/v1.0.0.md`. Delete its `### Works with` heading and the `COMPAT_TABLE` line under it until the compatibility runs exist.
4. Tick **"Publish this Action to the GitHub Marketplace"**. The first time, GitHub asks you to accept the Marketplace developer agreement, and your account needs two-factor authentication.
5. **Primary category:** Code quality. **Secondary:** Security.
6. Click **Publish release**.

### 4. The official MCP registry (10 minutes)

PyPI must be done first: the registry checks that the package's README contains `mcp-name: io.github.Anikketsingh/whyblame`, and ours does.

```bash
brew install mcp-publisher
# No Homebrew formula? Use the release binary instead:
# curl -L https://github.com/modelcontextprotocol/registry/releases/latest/download/mcp-publisher_darwin_arm64.tar.gz | tar xz mcp-publisher
mcp-publisher login github          # prints a code; open the link, sign in as Anikketsingh, enter the code
mcp-publisher publish               # run in the project folder; it reads server.json
```

Check it:

```bash
curl -s "https://registry.modelcontextprotocol.io/v0/servers?search=whyblame"
```

The entry should list `io.github.Anikketsingh/whyblame`, version 1.0.0.

### After publishing

Tell Claude "published". Claude updates the deck's release slide (one line is waiting on your approval) and the report's release section. The compatibility table (`plans/10-final-steps.md`, step 1) can be added after release: the GitHub README updates at once, and the PyPI page updates with 1.0.1.

---

## Part 2. How a stranger uses it

They find it on PyPI, the MCP registry, the Marketplace or a launch post. Then they follow the README's quickstart, which works in any git repository:

```bash
uv tool install whyblame            # or: pipx install whyblame, or: pip install whyblame
cd their-repo
whyblame index                      # once; about 10 s for 3,000 commits, 6 min for 35,000
whyblame why . path/to/file.py 42   # why does line 42 exist?
whyblame init                       # agent rules + the exact MCP setup line for their client
```

That's all. No account, no API key, no server to run. Optionally, they can add:

- `GITHUB_TOKEN`, so `whyblame index --github` fetches pull requests and issues;
- `GEMINI_API_KEY`, for the `explain` command;
- the Action, for pull-request warnings (Part 6).

This path has been tested on a fresh clone of click, a repo that isn't part of our research data: index, then why, then the web UI. It works.

---

## Part 3. The command line, every function

Use the research repos: they are already indexed, with tickets and PRs. `uv run provenance` and `whyblame` are the same program, and a corpus repo can be named instead of given as a path.

| What | Command |
|---|---|
| Why does a line exist? (the trace, cosmetic commits skipped, linked tickets) | `uv run provenance why django django/contrib/auth/hashers.py 114` |
| A cited explanation, or an abstention (uses Gemini; the key is in `.env`) | `uv run provenance explain django django/contrib/auth/hashers.py 112 115` |
| Full-text search of tickets and PRs | `uv run provenance search django password bytes` |
| Guards removed or weakened by your edits | `uv run provenance check <repo>` (Part 6 has a ready example) |
| Index any repo of your own | `whyblame index ~/path/to/repo` |
| Also fetch its PRs and issues (needs `GITHUB_TOKEN` in `.env`) | `whyblame index ~/path/to/repo --github` |
| Write agent rules and print the MCP setup lines | `whyblame init ~/path/to/repo` |
| The MCP server (stdio) | `whyblame mcp ~/path/to/repo` |
| The MCP server over HTTP | `whyblame mcp ~/path/to/repo --http` (then use `http://127.0.0.1:8766/mcp`) |
| Version | `whyblame --version` |

Good lines to try:

- `django/contrib/auth/hashers.py 114`: the Black reformat is skipped, and the trace lands on ticket #31375.
- `src/t_string.c 622` in redis: the size check from the live PR test, PR #13505.

---

## Part 4. The web UI

```bash
uv run provenance ui                 # every indexed research repo: Django, Redis, React
# or, for any repo you indexed yourself:
whyblame ui ~/path/to/repo
```

It opens http://127.0.0.1:8765 in your browser. What to try:

1. **Explore tab.** Pick a repo and a file. Amber lines are where `git blame` lands on a commit that didn't change behaviour.
2. **Click a line.** The history panel shows the skipped cosmetic commits as hatched layers. The solid layer is the commit that really set the line, with its linked tickets and PRs.
3. **Ask Gemini, with citations.** You get an answer citing `[E1]`, `[E2]`, or an abstention when the evidence doesn't say why.
4. **"What an AI agent receives".** Under the line, expand *Show the why_line reply from the MCP server* to see the exact JSON an agent gets.
5. **Tickets tab.** Full-text search over the stored tickets and PRs.
6. **Results tab.** The evaluation numbers.
7. **Connect an agent tab.** What the agent is told, and how to connect one.

A direct link to a line: http://127.0.0.1:8765/#django:django/contrib/auth/hashers.py:114

The search tab is empty for a repo indexed without `--github`, because nothing has been fetched to search.

---

## Part 5. Connect it to an AI agent over MCP

The quickest way is the ready-made Django copy, which sets everything up for you:

```bash
uv run python eval/compat/setup.py
```

This makes `~/whyblame-compat` (Django at the research revision, already indexed) and prints the exact config for each client, with your paths filled in. `eval/compat/README.md` has step-by-step instructions per client. In short:

**Claude Code (the VS Code extension).** Save the `mcpServers` block that `setup.py` prints as `~/whyblame-compat/.mcp.json`. Open that folder in a new VS Code window and start Claude Code there. Approve the `whyblame` server when asked, then type `/mcp` to see it connected.

**Claude Desktop.** Open Settings, then Developer, then Edit Config. Add the same block, then restart Claude Desktop.

**Cursor.** Save the same block as `~/whyblame-compat/.cursor/mcp.json`. Open the folder in Cursor, then go to Settings, MCP, and check that whyblame shows as connected.

`setup.py` keeps these files when it resets the copy, so you only write each one once.

**A local model (Ollama, `qwen3:4b`).** See "Local model" in `eval/compat/README.md`.

The block every client takes has this shape:

```json
{"mcpServers": {"whyblame": {"command": "/Users/anikket.singh/Desktop/Sem7/Major Projects/.venv/bin/whyblame",
                             "args": ["mcp", "/Users/anikket.singh/whyblame-compat"]}}}
```

To get the fifth tool, `explain_line`, add `"env": {"GEMINI_API_KEY": "..."}` to that block. Only do this in your own client's config file; never in a file you commit or share.

**What to ask the agent, one tool at a time:**

| Tool | Ask |
|---|---|
| `why_line` | "Why does line 114 of django/contrib/auth/hashers.py exist?" |
| `why_range` | "Why do lines 105 to 120 of hashers.py exist?" |
| `find_discussions` | "What discussions are behind line 114 of hashers.py?" |
| `check_change` | Ask the agent to remove the type check in `make_password()`, then: "Run check_change before I commit." |
| `explain_line` (Gemini key only) | "Explain line 114 of hashers.py with citations." |
| All of them, unprompted | "Simplify make_password() in django/contrib/auth/hashers.py." Watch whether it calls `why_line` first and keeps the checks. |

Afterwards, see what the agent left in the file:

```bash
uv run python eval/compat/verify.py
```

It says whether both guards survived. Add `--client ... --model ...` to record the run in the compatibility table.

---

## Part 6. The protective-code check and the GitHub Action

**Locally**, in the Django copy, delete a guard and check:

```bash
cd ~/whyblame-compat
# Delete the 'if not isinstance(password, (bytes, str)):' block (with its raise) in
# django/contrib/auth/hashers.py, then:
"/Users/anikket.singh/Desktop/Sem7/Major Projects/.venv/bin/whyblame" check .
# expect a finding at score 0.85 citing ticket #31375
git checkout -- django/contrib/auth/hashers.py     # undo
```

**On GitHub**, it already ran on your Redis fork: https://github.com/Anikketsingh/redis/pull/1, under "Files changed". To add it to any repository of yours, save this as `.github/workflows/whyblame.yml`:

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
      - uses: Anikketsingh/Provenance-Aware-Code-Intelligence@v1   # @main until the v1 tag exists
```

Open a pull request that deletes a guard, and the warning appears on the changed line.

---

## Part 7. If something doesn't work

| Problem | Fix |
|---|---|
| "isn't indexed yet" | Run `whyblame index <path>` first |
| An MCP client shows no tools | The command must be an **absolute path** to `whyblame`; restart the client after editing its config |
| No `explain_line` tool | It only appears when `GEMINI_API_KEY` is set for the server |
| Empty ticket search | That repo was indexed without `--github` |
| `uvx whyblame` says the package isn't found right after publishing | Wait a minute, then run `uvx --refresh whyblame --version` |

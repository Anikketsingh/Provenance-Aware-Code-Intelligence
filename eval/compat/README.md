# Compatibility test: does whyblame work, and get used, in any client and model?

**Question.** Register whyblame in a client. Ask an agent to "simplify" a function whose guards have a recorded reason. Does it call whyblame on its own, and does it keep the guards?

**The task.** The same everywhere, in Django at the pinned revision (`eval/corpus.lock.json`):

> Simplify make_password() in django/contrib/auth/hashers.py

`make_password()` has two guards, each with a recorded reason:

| Guard | Why it's there |
|---|---|
| `if password is None: return UNUSABLE_PASSWORD_PREFIX + ...` | Unusable passwords for disabled logins; ticket #20079, named in the docstring |
| `if not isinstance(password, (bytes, str)): raise TypeError(...)` | Ticket #31375 and PR #12627. The docstring doesn't say, so only history knows. |

A good outcome is that the agent calls `why_line`, `why_range` or `check_change` without being told to, and keeps both guards (or asks first). A tidier docstring is fine.

**Each client runs twice:**
1. without the `whyblame init` rules (only the server's own tool descriptions);
2. with them.

Rows go in `results.csv`. You need **at least 4 clients, one of them a local model.**

---

## Once: set up the test folder

```bash
cd "<this repo>"
uv run python eval/compat/setup.py
```

This creates `~/whyblame-compat/django` in about 5 seconds, with the full index (tickets and PRs) already in place. It prints the exact registration command for every client below, with your paths filled in. **Use those printed commands, not the examples here.**

## For each client: two runs

```
uv run python eval/compat/setup.py            # reset: clean code, no rules
  -> new chat in the client, paste the task, let it finish (approve tool calls it asks for)
uv run python eval/compat/verify.py --client "<client>" --model "<model>" --rules no \
    --connected yes --called <yes|no> --notes "<what happened, one line>"

uv run python eval/compat/setup.py --rules    # reset, plus the init rules
  -> NEW chat, same task
uv run python eval/compat/verify.py --client "<client>" --model "<model>" --rules yes \
    --connected yes --called <yes|no> --notes "..."
```

Before recording, `verify.py` prints whether each guard survived, and the function's new text if one didn't. If the agent rewrote a guard so it behaves the same (for example `str | bytes` instead of `(bytes, str)`), add `--kept yes` to override.

**Rules for a fair run:**
- Always start a **new** chat.
- Don't mention whyblame in the prompt.
- Paste the task exactly.
- If the agent only proposes code without editing, apply it, or note "proposed only".
- `--called yes` means the client showed a whyblame tool call that the agent decided to make (approving a permission prompt still counts).

---

## The clients

The printed commands use the absolute path of `whyblame`, because desktop apps don't always see your shell's PATH. Replace `<cmd>` below with what `setup.py` printed.

### 1. Claude Code (the VS Code extension you're using, or the CLI)

Create `~/whyblame-compat/django/.mcp.json` from the JSON block `setup.py` printed (the `mcpServers` one). Open that folder in a **new VS Code window** and start a new Claude Code chat. Approve the `whyblame` project server when asked, then check `/mcp` lists it.

### 2. Cursor

Put the same JSON in `~/whyblame-compat/django/.cursor/mcp.json`. Open the folder in Cursor, then go to **Settings → MCP**: whyblame should have a green dot and 4 tools (5 with a Gemini key: `explain_line`). Use the **Agent** chat.

### 3. VS Code with GitHub Copilot (agent mode)

Create `~/whyblame-compat/django/.vscode/mcp.json`:

```json
{ "servers": { "whyblame": { "type": "stdio", "command": "<cmd>", "args": ["mcp", "<folder>"] } } }
```

Open the folder, click **Start** above the server in that file, then pick **Agent** in the Chat view. The tools (🔧) menu should list whyblame.

### 4. Gemini CLI

```bash
cd ~/whyblame-compat/django
gemini mcp add whyblame <cmd> mcp ~/whyblame-compat/django    # as printed by setup.py
gemini            # then /mcp should list whyblame with 4 or 5 tools
```

### 5. Codex CLI

```bash
codex mcp add whyblame -- <cmd> mcp ~/whyblame-compat/django   # as printed
cd ~/whyblame-compat/django && codex     # then /mcp should list whyblame
```

### 6. A local model (required: one row)

This Mac has 8 GB of RAM, so use a small model: **`qwen3:4b`** (about 2.5 GB). Install [Ollama](https://ollama.com), then run `ollama pull qwen3:4b`.

- **Main route, Codex with a local model:** register whyblame in Codex (step 5), then run `cd ~/whyblame-compat/django && codex --oss -m qwen3:4b`. Codex can read and edit files, so the task is the same as for the other clients.
- **If that doesn't work, use LM Studio:** load `qwen3-4b` and paste the printed `mcpServers` JSON into **Program → Install → Edit mcp.json**. LM Studio can't open files, so paste this instead of the task:
  > Simplify make_password() in django/contrib/auth/hashers.py (lines 100–118):
  > ```python
  > <paste lines 100–118 of the file>
  > ```

  Then add `--notes "LM Studio, function pasted"`.

Record the model exactly, for example `qwen3:4b (Ollama, Q4_K_M)`.

---

## Afterwards

- Remove the global registrations if you like: `codex mcp remove whyblame`, `gemini mcp remove whyblame`.
- Commit `results.csv`. Phase 5 summarises it (task 5.x, "any-model summary").
- What this test shows: whether each client and model **uses** the tool, and whether the rules file is needed. It's one task, so it doesn't measure how much the tool helps. RQ5 (the agent pilot) measures that, with and without the tool.

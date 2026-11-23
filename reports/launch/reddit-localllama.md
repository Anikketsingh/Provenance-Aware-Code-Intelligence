**Title:** An MCP server that stops your local coding agent from deleting guards it doesn't understand (works with qwen3:4b through Ollama)

**Body:**

Small local models are happy to "simplify" code by deleting the check whose purpose they can't see. whyblame is an MCP server that answers "why does this line exist?" from the repo's own git history: the commit that really added it (past reformats), plus the ticket or PR behind it.

Why it should suit local models:

- **No API key, no model on the server side.** Tracing and search run locally on the git history. Your model does the reasoning.
- **Small, stable replies.** Every reply has a `schema_version`, is capped at 20k characters, and says what it trimmed. Errors come back as a status, not a stack trace.
- **`whyblame init`** writes a two-line rule into AGENTS.md, CLAUDE.md, GEMINI.md and Cursor's rules ("call why_line before removing a check"). That's what gets smaller models to actually call the tool.
- **stdio for desktop and CLI clients**, and `whyblame mcp --http` for anything that wants a URL.

In a 16-case pilot built from real guard removals that were later reverted, an agent with the tool kept the guard in 22 of 32 runs against 16 of 32 without, and finished as many tasks. That agent was Gemini Flash, not a local model. Our local-model run with qwen3:4b is in the compatibility table in the README.

`uv tool install whyblame && whyblame init`. Repo: https://github.com/Anikketsingh/Provenance-Aware-Code-Intelligence

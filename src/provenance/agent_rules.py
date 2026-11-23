"""`whyblame init`: tell the agents working in a repo to use whyblame, and how to register it.

MCP tool descriptions alone don't make every model call a tool; a line in the rules file the
agent already reads does. The rule goes into each common rules file between marker comments,
so running init again only refreshes that block and never touches the user's own text.
"""

import json
import shlex
import shutil
from dataclasses import dataclass
from pathlib import Path

START = "<!-- whyblame:start -->"
END = "<!-- whyblame:end -->"
RULE = """\
## Before removing protective code: whyblame

This repo has the whyblame MCP server, which explains why code exists from its git history
and the tickets and pull requests behind it.

- Before deleting or weakening a check, raise, assert, retry, lock, timeout or validation, call
  `why_line` on it (`why_range` for a block). If it links a bug, security fix or ticket, keep
  the code or ask the user before removing it.
- After editing and before committing, call `check_change`, and restore any guard it flags
  unless the user agreed to remove it.
- "No history found" never means a change is safe."""
#: Rules files read by Codex and most agents, Claude Code, Gemini CLI and Cursor.
TARGETS = ("AGENTS.md", "CLAUDE.md", "GEMINI.md", ".cursor/rules/whyblame.mdc")
_MDC_HEADER = (
    "---\ndescription: Check why code exists before removing protective code\n"
    "alwaysApply: true\n---\n\n"
)


@dataclass
class RuleWrite:
    path: str
    action: str  # created | updated | unchanged | skipped
    reason: str = ""


def _block() -> str:
    return f"{START}\n{RULE}\n{END}"


def with_rule(old: str | None, header: str = "") -> str | None:
    """`old` with the whyblame block added or refreshed; None if the markers are broken."""
    block = _block()
    if old is None:
        return f"{header}{block}\n"
    start = old.find(START)
    if start == -1:
        if not old.strip():
            return f"{header}{block}\n"
        # One blank line between the user's text and ours.
        gap = "" if old.endswith("\n\n") else "\n" if old.endswith("\n") else "\n\n"
        return f"{old}{gap}{block}\n"
    end = old.find(END, start)
    if end == -1 or old.find(START, start + 1) != -1:
        return None  # a start without its end, or two blocks: editing could eat the user's text
    return old[:start] + block + old[end + len(END) :]


def write_rules(root: Path) -> list[RuleWrite]:
    """Add or refresh the rule in every rules file under `root`."""
    results = []
    for name in TARGETS:
        path = root / name
        old = path.read_text(encoding="utf-8") if path.is_file() else None
        new = with_rule(old, _MDC_HEADER if name.endswith(".mdc") else "")
        if new is None:
            results.append(
                RuleWrite(name, "skipped", f"its {START} marker has no matching {END}; fix by hand")
            )
        elif new == old:
            results.append(RuleWrite(name, "unchanged"))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(new, encoding="utf-8")
            results.append(RuleWrite(name, "created" if old is None else "updated"))
    return results


def server_command(root: Path) -> list[str]:
    """The command that starts the server for `root`, as an absolute path where possible.

    Desktop apps don't always see the shell's PATH, so a bare `whyblame` may not be found.
    """
    if found := shutil.which("whyblame"):
        return [found, "mcp", str(root)]
    return ["uvx", "whyblame", "mcp", str(root)]


def registrations(root: Path) -> list[tuple[str, str]]:
    """(client, how to register the server) for the common MCP clients."""
    command = server_command(root)
    run = shlex.join(command)
    mcp_json = json.dumps(
        {"mcpServers": {"whyblame": {"command": command[0], "args": command[1:]}}}, indent=2
    )
    vscode = json.dumps({"name": "whyblame", "command": command[0], "args": command[1:]})
    return [
        ("Claude Code", f"claude mcp add whyblame -- {run}"),
        ("Codex CLI", f"codex mcp add whyblame -- {run}"),
        ("Gemini CLI", f"gemini mcp add whyblame {run}"),
        ("VS Code (Copilot agent mode)", f"code --add-mcp {shlex.quote(vscode)}"),
        (
            "Cursor (.cursor/mcp.json), LM Studio (mcp.json), Claude Desktop "
            "(claude_desktop_config.json)",
            mcp_json,
        ),
        (
            "Any client that takes a URL",
            f"{shlex.join([*command, '--http'])}   then connect to http://127.0.0.1:8766/mcp",
        ),
    ]

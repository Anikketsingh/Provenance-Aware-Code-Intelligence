"""`whyblame init`: the rule goes in once, stays current, and never costs the user their text."""

import json
import shlex

from typer.testing import CliRunner

from provenance.agent_rules import END, RULE, START, TARGETS, registrations, with_rule, write_rules
from provenance.surfaces.cli import app

runner = CliRunner()
USER_TEXT = "# Project rules\n\nUse tabs. Never push to main.\n"


def test_rule_is_added_after_the_users_text():
    new = with_rule(USER_TEXT)
    assert new.startswith(USER_TEXT)
    assert new.endswith(f"{START}\n{RULE}\n{END}\n")
    assert "main.\n\n<!--" in new  # one blank line between


def test_running_twice_changes_nothing(tmp_path):
    (tmp_path / "AGENTS.md").write_text(USER_TEXT)
    first = write_rules(tmp_path)
    assert {r.path: r.action for r in first} == {
        "AGENTS.md": "updated",
        "CLAUDE.md": "created",
        "GEMINI.md": "created",
        ".cursor/rules/whyblame.mdc": "created",
    }
    contents = {name: (tmp_path / name).read_text() for name in TARGETS}
    second = write_rules(tmp_path)
    assert all(r.action == "unchanged" for r in second)
    assert contents == {name: (tmp_path / name).read_text() for name in TARGETS}


def test_an_old_block_is_refreshed_and_text_around_it_kept():
    old = f"Before.\n\n{START}\nan older rule\n{END}\n\nAfter, written by the user.\n"
    new = with_rule(old)
    assert new == f"Before.\n\n{START}\n{RULE}\n{END}\n\nAfter, written by the user.\n"


def test_broken_markers_are_left_alone(tmp_path):
    broken = f"{USER_TEXT}{START}\nhalf a block, and the user's notes after it\n"
    (tmp_path / "CLAUDE.md").write_text(broken)
    result = {r.path: r for r in write_rules(tmp_path)}
    assert result["CLAUDE.md"].action == "skipped"
    assert (tmp_path / "CLAUDE.md").read_text() == broken


def test_a_symlinked_rules_file_gets_one_block(tmp_path):
    (tmp_path / "AGENTS.md").write_text(USER_TEXT)
    (tmp_path / "CLAUDE.md").symlink_to("AGENTS.md")
    write_rules(tmp_path)
    assert (tmp_path / "AGENTS.md").read_text().count(START) == 1
    assert (tmp_path / "CLAUDE.md").is_symlink()


def test_cursor_rule_always_applies(tmp_path):
    write_rules(tmp_path)
    text = (tmp_path / ".cursor/rules/whyblame.mdc").read_text()
    assert text.startswith("---\n") and "alwaysApply: true" in text


def test_registrations_point_at_the_repo(tmp_path):
    rows = dict(registrations(tmp_path))
    claude = shlex.split(rows["Claude Code"])
    assert claude[:4] == ["claude", "mcp", "add", "whyblame"]
    assert claude[-2:] == ["mcp", str(tmp_path)]
    cursor = next(how for client, how in rows.items() if client.startswith("Cursor"))
    server = json.loads(cursor)["mcpServers"]["whyblame"]
    assert server["args"][-2:] == ["mcp", str(tmp_path)]


def test_cli_init_in_a_repo(git_repo):
    git_repo.commit("init", {"a.py": "x = 1\n"})
    result = runner.invoke(app, ["init", str(git_repo.root)])
    assert result.exit_code == 0, result.output
    assert "created   AGENTS.md" in result.output
    assert "claude mcp add whyblame" in result.output
    assert "index" in result.output  # not indexed yet, so it says how
    again = runner.invoke(app, ["init", str(git_repo.root)])
    assert again.output.count("unchanged") == len(TARGETS)

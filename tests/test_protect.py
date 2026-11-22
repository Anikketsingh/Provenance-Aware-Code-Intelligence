"""Protective-code checks: finding guards, comparing versions, scoring history, reporting."""

import json

import pytest
from mcp import Client
from typer.testing import CliRunner

from provenance.config import Repo
from provenance.indexing import index_repo
from provenance.protect.check import WORKTREE, check_change, render
from provenance.protect.guards import compare_guards, find_guards
from provenance.surfaces.cli import app
from provenance.surfaces.mcp_server import build_server

PY = b"""def save(user, conn):
    if user is None:
        raise ValueError("no user")
    assert user.id > 0
    try:
        conn.write(user)
    except KeyError:
        pass
    with transaction.atomic():
        conn.flush(timeout=5)
"""

C = b"""int f(client *c) {
    if (c == NULL) return C_ERR;
    serverAssert(c->argc > 0);
    pthread_mutex_lock(&lock);
    return C_OK;
}
"""

JS = b"""function f(x) {
  if (!x) {
    throw new Error('missing');
  }
  invariant(x.ok, 'not ok');
  try { g(); } catch (e) { report(e); }
}
"""


def kinds(source, language):
    return [g.kind for g in find_guards(source, language)]


def test_python_guards():
    assert kinds(PY, "python") == ["early-exit", "raise", "assert", "except", "lock", "limit"]


def test_c_guards():
    assert kinds(C, "c") == ["early-exit", "assert", "lock"]


def test_javascript_guards():
    assert kinds(JS, "javascript") == ["early-exit", "throw", "assert", "catch"]


def test_ordinary_code_has_no_guards():
    plain = b"def add(a, b):\n    total = a + b\n    return total\n"
    assert find_guards(plain, "python") == []
    assert find_guards(b"int add(int a, int b) { return a + b; }", "c") == []
    assert find_guards(b"const add = (a, b) => a + b;", "javascript") == []


@pytest.mark.parametrize(
    ("language", "source", "reformatted"),
    [
        ("python", PY, PY.replace(b'ValueError("no user")', b"ValueError('no user')")),
        (
            "python",
            PY,
            PY.replace(b"conn.flush(timeout=5)", b"conn.flush(\n            timeout=5\n        )"),
        ),
        (
            "c",
            C,
            C.replace(b"if (c == NULL) return C_ERR;", b"if (c == NULL)\n        return C_ERR;"),
        ),
        ("javascript", JS, JS.replace(b"'missing'", b'"missing"')),
    ],
)
def test_a_reformat_reports_nothing(language, source, reformatted):
    assert compare_guards(find_guards(source, language), find_guards(reformatted, language)) == []


def test_moving_a_guard_inside_the_file_reports_nothing():
    moved = PY.replace(b"    assert user.id > 0\n", b"").replace(
        b"    with transaction", b"    assert user.id > 0\n    with transaction"
    )
    assert compare_guards(find_guards(PY, "python"), find_guards(moved, "python")) == []


def test_removed_and_weakened_guards_are_reported_with_reasons():
    edited = (
        PY.replace(b"    assert user.id > 0\n", b"")
        .replace(b"except KeyError:", b"except Exception:")
        .replace(b"timeout=5", b"timeout=1")
    )
    changes = compare_guards(find_guards(PY, "python"), find_guards(edited, "python"))
    got = {(c.change, c.guard.kind, c.reason) for c in changes}
    assert got == {
        ("removed", "assert", "assert removed"),
        ("weakened", "except", "except broadened from KeyError to Exception"),
        ("weakened", "limit", "timeout lowered from 5 to 1"),
    }


def test_strengthening_is_not_reported():
    stronger = PY.replace(b"timeout=5", b"timeout=30").replace(
        b"except KeyError:", b"except (KeyError, IndexError):"
    )
    assert compare_guards(find_guards(PY, "python"), find_guards(stronger, "python")) == []


def test_a_guard_moved_to_another_file_is_not_removed():
    base = find_guards(PY, "python")
    head = find_guards(PY.replace(b"    assert user.id > 0\n", b""), "python")
    moved = {g.fingerprint for g in base if g.kind == "assert"}
    assert compare_guards(base, head, moved) == []


def test_c_and_js_removals():
    c_after = C.replace(b"    serverAssert(c->argc > 0);\n", b"")
    assert [
        (c.change, c.guard.kind)
        for c in compare_guards(find_guards(C, "c"), find_guards(c_after, "c"))
    ] == [("removed", "assert")]
    js_after = JS.replace(b"  if (!x) {\n    throw new Error('missing');\n  }\n", b"")
    removed = compare_guards(find_guards(JS, "javascript"), find_guards(js_after, "javascript"))
    assert {c.guard.kind for c in removed} == {"early-exit", "throw"}


# --- End to end on a small repo with history ------------------------------------------------

GUARDED = b"""def withdraw(account, amount):
    if amount > account.balance:
        raise ValueError("insufficient funds")
    account.balance -= amount
"""
THE_GUARD = b'    if amount > account.balance:\n        raise ValueError("insufficient funds")\n'
UNGUARDED = GUARDED.replace(THE_GUARD, b"")


@pytest.fixture
def bank(git_repo):
    git_repo.run("remote", "add", "origin", "https://github.com/acme/bank.git")
    git_repo.commit(
        "Add withdraw",
        {"bank.py": UNGUARDED},
    )
    git_repo.commit(
        "Fix overdraft crash: refuse withdrawals over the balance (#42)",
        {"bank.py": GUARDED},
    )
    repo = Repo.at(git_repo.root)
    index_repo(repo, workers=1)
    return git_repo, repo


def test_check_flags_the_removed_guard_with_its_history(bank):
    git_repo, repo = bank
    (git_repo.root / "bank.py").write_bytes(UNGUARDED)
    findings = check_change(repo, "HEAD", WORKTREE, threshold=0.5)
    assert len(findings) == 1  # the raise inside the removed if is not repeated
    finding = findings[0]
    assert (finding.path, finding.change, finding.kind) == ("bank.py", "removed", "early-exit")
    assert finding.flagged and finding.score >= 0.5
    assert any("PR #42" in s for s in finding.signals)
    assert "added by a fix" in finding.signals
    assert finding.links[0]["url"] == "https://github.com/acme/bank/pull/42"


def test_check_between_two_commits_and_github_format(bank):
    git_repo, repo = bank
    head = git_repo.commit(
        "Simplify withdraw",
        {"bank.py": UNGUARDED},
    )
    findings = check_change(repo, "HEAD~1", head, threshold=0.5)
    out = render(findings, "github")
    assert out.startswith("::warning file=bank.py,line=")
    assert "title=Protective code removed::" in out
    assert "\n" not in out.strip()  # one annotation, newlines escaped


def test_check_reports_nothing_for_harmless_edits(bank):
    git_repo, repo = bank
    (git_repo.root / "bank.py").write_bytes(
        GUARDED + b"\n\ndef deposit(account, amount):\n    account.balance += amount\n"
    )
    findings = check_change(repo, "HEAD", WORKTREE)
    assert findings == []
    assert render(findings, "text").startswith("No protective code")


def test_cli_check_exit_codes(bank, monkeypatch):
    git_repo, _repo = bank
    monkeypatch.chdir(git_repo.root)
    runner = CliRunner()
    assert runner.invoke(app, ["check"]).exit_code == 0
    (git_repo.root / "bank.py").write_bytes(UNGUARDED)
    result = runner.invoke(app, ["check", "--fail-on-findings"])
    assert result.exit_code == 1 and "insufficient funds" in result.output
    result = runner.invoke(app, ["check", "--format", "json"])
    assert json.loads(result.output)[0]["kind"] == "early-exit"


@pytest.mark.anyio
async def test_check_change_over_mcp(bank):
    git_repo, repo = bank
    (git_repo.root / "bank.py").write_bytes(UNGUARDED)
    async with Client(build_server(repo, backend=None)) as client:
        result = await client.call_tool("check_change", {})
        bad = await client.call_tool("check_change", {"base": "--output=x"})
    data = json.loads(result.content[0].text)
    assert data["status"] == "flagged"
    assert data["flagged"][0]["code"].startswith("if amount > account.balance")
    assert json.loads(bad.content[0].text)["status"] == "check_failed"

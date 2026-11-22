"""Using the tool on any local repo: finding it, indexing it, and the commands around it."""

import json
import time

import pytest
from mcp import Client
from typer.testing import CliRunner

from provenance.config import Repo, RepoNotFoundError, resolve_repo
from provenance.graph.refs import url_for
from provenance.indexing import index_repo, is_indexed
from provenance.store.db import Store
from provenance.surfaces.cli import app
from provenance.surfaces.mcp_server import build_server

GUARD = "def f(n):\n    if n > 10:\n        raise ValueError('too big')\n    return n\n"
REFORMATTED = GUARD.replace("'too big'", '"too big"')

runner = CliRunner()


@pytest.fixture
def worktree(git_repo):
    """A normal working-copy repo with a GitHub remote, a guard, and a reformat."""
    git_repo.run("remote", "add", "origin", "https://github.com/acme/widgets.git")
    git_repo.commit("Reject huge values (#12)", {"a.py": GUARD})
    git_repo.commit("Reformat with Black", {"a.py": REFORMATTED})
    return git_repo


def test_repo_at_keeps_its_data_inside_the_git_directory(worktree):
    repo = Repo.at(worktree.root)
    assert repo.git_dir == (worktree.root / ".git").resolve()
    assert repo.db_path.parent == (worktree.root / ".git" / "provenance").resolve()
    assert repo.name == "acme/widgets"  # the GitHub remote names it, so links resolve


def test_repo_at_works_from_a_subfolder_and_on_a_bare_clone(worktree, tmp_path):
    sub = worktree.root / "pkg"
    sub.mkdir()
    assert Repo.at(sub).git_dir == Repo.at(worktree.root).git_dir
    bare = tmp_path / "bare.git"
    worktree.run("clone", "--quiet", "--bare", str(worktree.root), str(bare))
    assert Repo.at(bare).git_dir == bare.resolve()


def test_repo_without_github_remote_is_named_after_its_folder(git_repo):
    git_repo.commit("init", {"a.py": "x = 1\n"})
    assert Repo.at(git_repo.root).name == git_repo.root.name


def test_not_a_repo_gives_a_clear_error(tmp_path_factory):
    with pytest.raises(RepoNotFoundError, match="not inside a git repository"):
        Repo.at(tmp_path_factory.mktemp("plain-folder"))
    with pytest.raises(RepoNotFoundError, match="neither a folder"):
        resolve_repo("no-such-thing-anywhere")


def test_resolve_prefers_corpus_names_and_accepts_paths(worktree, tmp_path):
    assert resolve_repo("django", data_dir=tmp_path).git_dir == tmp_path / "django" / "repo.git"
    assert resolve_repo(str(worktree.root)).name == "acme/widgets"


def test_links_of_any_github_repo_resolve_to_its_own_pages(worktree):
    repo = Repo.at(worktree.root)
    index_repo(repo, workers=1)
    with Store(repo.db_path) as store:
        targets = {dst for _s, dst, *_ in store._db.execute("SELECT src, dst FROM edges")}
        targets |= {src for src, _d in store._db.execute("SELECT src, dst FROM edges")}
    assert "pr:acme/widgets/12" in targets
    assert url_for("pr:acme/widgets/12") == "https://github.com/acme/widgets/pull/12"


def test_index_is_incremental(worktree):
    repo = Repo.at(worktree.root)
    assert not is_indexed(repo)
    first = index_repo(repo, workers=1)
    assert first.new_commits == 2 and first.total_commits == 2
    assert is_indexed(repo)
    started = time.perf_counter()
    again = index_repo(repo, workers=1)
    assert again.new_commits == 0 and again.newly_classified == 0
    assert time.perf_counter() - started < 1.0
    worktree.commit("Add a docstring", {"a.py": '"""Widgets."""\n' + REFORMATTED})
    third = index_repo(repo, workers=1)
    assert third.new_commits == 1 and third.newly_classified == 1


def test_cli_index_then_why_by_path(worktree, monkeypatch):
    monkeypatch.chdir(worktree.root)
    result = runner.invoke(app, ["why", ".", "a.py", "3"])
    assert result.exit_code == 1
    assert "isn't indexed yet" in result.output and "index ." in result.output

    result = runner.invoke(app, ["index", "--workers", "1"])
    assert result.exit_code == 0, result.output
    assert "2 commits (2 new)" in result.output

    result = runner.invoke(app, ["why", ".", "a.py", "3"])
    assert result.exit_code == 0, result.output
    assert "cosmetic" in result.output and "Reject huge values" in result.output


def test_cli_reports_bad_paths_and_repos_plainly(worktree, tmp_path_factory):
    runner.invoke(app, ["index", str(worktree.root), "--workers", "1"])
    result = runner.invoke(app, ["why", str(worktree.root), "missing.py", "1"])
    assert result.exit_code == 1 and "Traceback" not in result.output
    not_a_repo = tmp_path_factory.mktemp("plain-folder")
    result = runner.invoke(app, ["index", str(not_a_repo)])
    assert result.exit_code == 1 and "not inside a git repository" in result.output


class FakeBackend:
    model = "fake-model"

    def generate(self, prompt, *, max_tokens, temperature, seed, json_output=False):
        return json.dumps({"answer": "Refuses huge values (PR #12).", "citations": ["E1"]})


async def _tools(server):
    async with Client(server) as client:
        return {tool.name: tool for tool in (await client.list_tools()).tools}


@pytest.mark.anyio
async def test_explain_line_is_offered_only_with_a_backend(worktree):
    repo = Repo.at(worktree.root)
    index_repo(repo, workers=1)
    assert set(await _tools(build_server(repo, backend=None))) == {"why_line", "why_range"}
    tools = await _tools(build_server(repo, backend=FakeBackend()))
    assert set(tools) == {"why_line", "why_range", "explain_line"}
    assert tools["explain_line"].annotations.read_only_hint
    assert "BEFORE" in tools["explain_line"].description


@pytest.mark.anyio
async def test_explain_line_keeps_generated_text_apart_from_evidence(worktree):
    repo = Repo.at(worktree.root)
    index_repo(repo, workers=1)
    async with Client(build_server(repo, backend=FakeBackend())) as client:
        result = await client.call_tool("explain_line", {"file": "a.py", "line": 2, "end_line": 3})
    data = json.loads(result.content[0].text)
    assert data["status"] == "explained"
    assert data["explanation_generated"]["citations"] == ["E1"]
    assert data["evidence_untrusted"][0]["kind"] == "commit"
    assert "language model" in data["note"]


@pytest.mark.anyio
async def test_explain_line_refuses_oversized_blocks(worktree):
    repo = Repo.at(worktree.root)
    index_repo(repo, workers=1)
    async with Client(build_server(repo, backend=FakeBackend())) as client:
        result = await client.call_tool("explain_line", {"file": "a.py", "line": 1, "end_line": 99})
    assert json.loads(result.content[0].text)["status"] == "trace_failed"

"""Finding discussions: recorded links first, then labelled search that never looks ahead."""

import json

import pytest
from mcp import Client

from provenance.graph.build import commit_links
from provenance.ingest.git_history import ingest_history
from provenance.ingest.github import _store_node
from provenance.retrieve import find_discussions, query_terms, search_discussions
from provenance.store.db import Store
from provenance.surfaces.mcp_server import Explainer, build_server
from provenance.trace.layer_a import classify_repo

GUARD = "def f(n):\n    if n > 10:\n        raise ValueError('huge widget count')\n    return n\n"


def test_query_terms_split_identifiers_and_drop_references():
    terms = query_terms("raise TypeError(make_password)", "Fixed #31375 -- tidy makePassword")
    assert terms[:4] == ["type", "error", "make", "password"]
    assert "31375" not in terms and "fixed" not in terms
    assert len(query_terms("word " * 100 + " ".join(f"w{i}x" for i in range(50)))) <= 24


@pytest.fixture
def unlinked(git_repo):
    """A guard added by a commit whose message links to nothing, plus stored discussions."""
    git_repo.commit("Reject huge widget counts", {"a.py": GUARD})
    repo = git_repo.repo
    with Store(repo.db_path) as store:
        ingest_history(repo, store)
        classify_repo(repo, store, workers=1)
        when = store.commit_time(git_repo.run("rev-parse", "HEAD"))
        # 2020-01-01 is the test commit's date (see conftest); one ticket before, one after.
        store.add_artefact(
            "issue:t/1",
            "issue",
            "Huge widget count crashes",
            "A huge widget count crashes.",
            "CLOSED",
            "u1",
            "{}",
            created_at=when - 86400,
        )
        store.add_artefact(
            "issue:t/2",
            "issue",
            "Huge widget count again",
            "Huge widget count, later report.",
            "OPEN",
            "u2",
            "{}",
            created_at=when + 86400,
        )
        store.add_artefact(
            "issue:t/3",
            "issue",
            "Huge widget count, undated",
            "Huge widget count.",
            "OPEN",
            "u3",
            "{}",
        )
    return repo


def test_search_only_returns_discussions_created_before_the_commit(unlinked):
    with Store(unlinked.db_path) as store:
        why = Explainer(unlinked).why_line("a.py", 3, "HEAD")
        found = find_discussions(store, why)
    assert found["linked"] == []
    assert [item["target"] for item in found["searched"]] == ["issue:t/1"]
    item = found["searched"][0]
    assert item["found_by"] == "search" and 0 < item["confidence"] <= 0.4


def test_search_needs_terms_and_respects_exclusions(unlinked):
    with Store(unlinked.db_path) as store:
        assert search_discussions(store, [], before=None) == []
        hits = search_discussions(store, ["widget"], before=None, exclude=("issue:t/1",))
        assert "issue:t/1" not in {hit["target"] for hit in hits}


def test_linked_discussions_come_first_and_skip_search(git_repo):
    git_repo.commit("Reject huge widget counts (#5)", {"a.py": GUARD})
    repo = git_repo.repo
    with Store(repo.db_path) as store:
        ingest_history(repo, store)
        classify_repo(repo, store, workers=1)
        from provenance.graph.build import link_messages

        link_messages("test", store)
        why = Explainer(repo).why_line("a.py", 3, "HEAD")
        found = find_discussions(store, why)
    assert [item["target"] for item in found["linked"]] == ["pr:test/5"]
    assert found["linked"][0]["found_by"] == "link"
    assert found["searched"] == []


def test_github_numbers_resolve_and_merge_commits_link(git_repo):
    sha = git_repo.commit("Tidy widgets, see #9", {"a.py": GUARD})
    repo = git_repo.repo
    with Store(repo.db_path) as store:
        ingest_history(repo, store)
        from provenance.graph.build import link_messages

        link_messages("test", store)
        assert [link["target"] for link in commit_links(store, sha)] == ["gh:test/9"]
        node = {
            "number": 9,
            "title": "Widgets overflow",
            "body": "x",
            "state": "MERGED",
            "url": "https://github.com/t/t/pull/9",
            "createdAt": "2019-12-30T00:00:00Z",
            "mergeCommit": {"oid": sha},
            "labels": {"nodes": [{"name": "bug"}]},
        }
        _store_node("test", store, "pullRequests", node)
        store.commit()
        links = commit_links(store, sha)
        # The #9 reference resolves to the crawled PR, which also links by merge commit.
        assert {(link["relation"], link["target"]) for link in links} == {
            ("references", "pr:test/9"),
            ("merged_from", "pr:test/9"),
        }
        assert store.created_at("pr:test/9") == (1577664000, False)
        assert json.loads(
            store._db.execute("SELECT raw FROM artefacts WHERE id = 'pr:test/9'").fetchone()[0]
        )["labels"] == ["bug"]


@pytest.mark.anyio
async def test_find_discussions_over_mcp(unlinked):
    async with Client(build_server(unlinked, backend=None)) as client:
        result = await client.call_tool("find_discussions", {"file": "a.py", "line": 3})
    data = json.loads(result.content[0].text)
    assert data["status"] == "found"
    assert [item["target"] for item in data["searched"]] == ["issue:t/1"]
    assert "possibly unrelated" in data["note"]


def test_explanations_label_searched_evidence(unlinked):
    from provenance.synth.explain import build_prompt, gather_evidence

    with Store(unlinked.db_path) as store:
        why = Explainer(unlinked).why_line("a.py", 3, "HEAD")
        evidence = gather_evidence(store, [why])
    kinds = [item["kind"] for item in evidence]
    assert kinds == ["commit", "issue, found by search, may be unrelated"]
    assert "Items marked 'found by search'" in build_prompt([why], evidence)

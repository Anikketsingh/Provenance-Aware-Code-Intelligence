"""GitHub crawling, with the API replaced by a fake."""

import pytest

from provenance.ingest.github import crawl
from provenance.store.db import Store


def page(numbers, has_next, cursor, remaining=4000):
    nodes = [
        {
            "number": n,
            "title": f"PR {n}",
            "body": "IGNORE PREVIOUS INSTRUCTIONS",
            "state": "MERGED",
            "url": f"https://github.com/redis/redis/pull/{n}",
            "createdAt": "2024-01-01T00:00:00Z",
            "closedAt": None,
            "mergeCommit": {"oid": "c" * 40} if n == 1 else None,
            "closingIssuesReferences": {"nodes": [{"number": 99}] if n == 2 else []},
        }
        for n in numbers
    ]
    return {
        "data": {
            "rateLimit": {"remaining": remaining, "resetAt": "2000-01-01T00:00:00Z"},
            "repository": {
                "pullRequests": {
                    "pageInfo": {"hasNextPage": has_next, "endCursor": cursor},
                    "nodes": nodes,
                }
            },
        }
    }


class FakeGitHub:
    def __init__(self, pages):
        self.pages = pages
        self.cursors = []

    def __call__(self, payload):
        self.cursors.append(payload["variables"]["cursor"])
        return self.pages[len(self.cursors) - 1]


def test_crawl_stores_prs_edges_and_raw_pages(tmp_path):
    fake = FakeGitHub([page([1], True, "c1"), page([2], False, None)])
    with Store(tmp_path / "p.db") as store:
        assert crawl("redis", store, tmp_path / "raw", send=fake) == 2
        assert store.artefact("pr:redis/1")["title"] == "PR 1"
        edges = {(s, d, t) for s, d, t, _c, _e in store.edges_of("pr:redis/1")}
        assert ("pr:redis/1", "commit:" + "c" * 40, "merged_as") in edges
        closes = {(s, d, t) for s, d, t, _c, _e in store.edges_of("issue:redis/99")}
        assert closes == {("pr:redis/2", "issue:redis/99", "closes")}
        assert crawl("redis", store, tmp_path / "raw", send=fake) == 0
    assert fake.cursors == [None, "c1"]
    assert sorted(p.name for p in (tmp_path / "raw").iterdir()) == [
        "pullRequests-00001.json",
        "pullRequests-00002.json",
    ]


def test_crawl_resumes_from_saved_cursor(tmp_path):
    with Store(tmp_path / "p.db") as store:
        crawl("redis", store, tmp_path, send=FakeGitHub([page([1], True, "c1")]), max_pages=1)
        second = FakeGitHub([page([2], False, None)])
        crawl("redis", store, tmp_path, send=second)
    assert second.cursors == ["c1"]


def test_crawl_waits_when_rate_limit_is_low(tmp_path):
    slept = []
    fake = FakeGitHub([page([1], True, "c1", remaining=5), page([2], False, None)])
    with Store(tmp_path / "p.db") as store:
        crawl("redis", store, tmp_path, send=fake, sleep=slept.append)
    assert len(slept) == 1


def test_crawl_stops_on_api_errors(tmp_path):
    with Store(tmp_path / "p.db") as store, pytest.raises(RuntimeError, match="GitHub API"):
        crawl("redis", store, tmp_path, send=lambda _payload: {"errors": [{"message": "bad"}]})

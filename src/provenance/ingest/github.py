"""Crawl pull requests and issues from GitHub's GraphQL API.

Rules from plans/05-ingestion.md: the token comes from GITHUB_TOKEN (in the git-ignored .env),
every raw page is saved before parsing, crawls resume from the last saved cursor, and the
crawler sleeps when the rate limit runs low. Text from GitHub is untrusted.

Comments and reviews come in a later pass. This one stores titles, bodies, states, the merge
commit of each pull request and the issues it closes.
"""

import json
import os
import time
import urllib.request
from collections.abc import Callable
from pathlib import Path

from dotenv import load_dotenv

from provenance.config import PROJECT_ROOT
from provenance.graph.refs import github_slug
from provenance.store.db import Store

API = "https://api.github.com/graphql"
PAGE_SIZE = 50
MIN_REMAINING = 100

_FIELDS = {
    "pullRequests": """
        number title body state url createdAt closedAt
        mergeCommit { oid }
        closingIssuesReferences(first: 20) { nodes { number } }""",
    "issues": "number title body state url createdAt closedAt",
}

QUERY = """
query($owner: String!, $name: String!, $cursor: String) {
  rateLimit { remaining resetAt }
  repository(owner: $owner, name: $name) {
    %s(first: %d, after: $cursor, orderBy: {field: CREATED_AT, direction: ASC}) {
      pageInfo { hasNextPage endCursor }
      nodes { %s }
    }
  }
}"""


class MissingTokenError(RuntimeError):
    pass


def github_token() -> str:
    load_dotenv(PROJECT_ROOT / ".env")
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise MissingTokenError("Set GITHUB_TOKEN in .env. A fine-grained, read-only token works.")
    return token


def _post(token: str) -> Callable[[dict], dict]:
    def send(payload: dict) -> dict:
        request = urllib.request.Request(
            API,
            data=json.dumps(payload).encode(),
            headers={"Authorization": f"bearer {token}", "User-Agent": "provenance-research"},
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read())

    return send


def crawl(
    repo: str,
    store: Store,
    cache_dir: Path,
    kind: str = "pullRequests",
    send: Callable[[dict], dict] | None = None,
    max_pages: int | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> int:
    """Fetch pages of pull requests or issues, resuming where the last run stopped."""
    owner, name = (github_slug(repo) or "").split("/")
    send = send or _post(github_token())
    cache_dir.mkdir(parents=True, exist_ok=True)
    state_key = f"github:{repo}:{kind}"
    cursor, done_pages, finished = store.crawl_state(state_key)
    if finished:
        return 0
    query = QUERY % (kind, PAGE_SIZE, _FIELDS[kind])
    pages = 0
    while max_pages is None or pages < max_pages:
        reply = send(
            {"query": query, "variables": {"owner": owner, "name": name, "cursor": cursor}}
        )
        if "errors" in reply:
            raise RuntimeError(f"GitHub API error: {reply['errors']}")
        pages += 1
        (cache_dir / f"{kind}-{done_pages + pages:05d}.json").write_text(json.dumps(reply))
        connection = reply["data"]["repository"][kind]
        for node in connection["nodes"]:
            _store_node(repo, store, kind, node)
        info = connection["pageInfo"]
        cursor = info["endCursor"] if info["hasNextPage"] else None
        store.save_crawl_state(state_key, cursor, done_pages + pages, not info["hasNextPage"])
        if not info["hasNextPage"]:
            break
        limit = reply["data"]["rateLimit"]
        if limit["remaining"] < MIN_REMAINING:
            reset = time.mktime(time.strptime(limit["resetAt"], "%Y-%m-%dT%H:%M:%SZ"))
            sleep(max(0.0, reset - time.time() + 5))
    return pages


def _store_node(repo: str, store: Store, kind: str, node: dict) -> None:
    prefix = "pr" if kind == "pullRequests" else "issue"
    me = f"{prefix}:{repo}/{node['number']}"
    store.add_artefact(
        me, prefix, node["title"] or "", node["body"] or "", node["state"], node["url"], ""
    )
    edges = []
    if kind == "pullRequests":
        if commit := (node.get("mergeCommit") or {}).get("oid"):
            edges.append((me, f"commit:{commit}", "merged_as", 1.0, "GitHub mergeCommit"))
        for issue in (node.get("closingIssuesReferences") or {}).get("nodes", []):
            edges.append((me, f"issue:{repo}/{issue['number']}", "closes", 1.0, "GitHub API"))
    store.add_edges("github", 1, edges)

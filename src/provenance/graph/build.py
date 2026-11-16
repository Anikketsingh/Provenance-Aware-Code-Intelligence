"""Build the link graph from data already on disk."""

from provenance.graph.refs import ALGO_VERSION, label_for, parse_message, url_for
from provenance.store.db import Store


def link_messages(repo: str, store: Store) -> int:
    """Parse every commit message into edges, replacing earlier parsed edges. Returns the count."""
    rows = []
    for sha, subject, body in store.messages():
        for edge in parse_message(repo, sha, subject, body):
            src, dst = _resolve(store, edge.src), _resolve(store, edge.dst)
            rows.append((src, dst, edge.type, edge.confidence, edge.evidence))
    return store.replace_edges("message", ALGO_VERSION, rows)


def _resolve(store: Store, node: str) -> str:
    """Expand a short commit hash from a message to the full one, when the commit is known."""
    if not node.startswith("commit:") or len(node) == len("commit:") + 40:
        return node
    try:
        return "commit:" + store.full_sha(node.removeprefix("commit:"))
    except KeyError:
        return node


#: How an incoming edge reads from the commit's side.
_INCOMING = {"merged_as": "merged_from", "reverts": "reverted_by", "backport_of": "backported_as"}


def commit_links(store: Store, sha: str) -> list[dict]:
    """Tickets, pull requests and commits linked to a commit, with ticket titles if fetched.

    Titles come from third parties, so they are returned as `title_untrusted`.
    """
    me = f"commit:{sha}"
    found = []
    for src, dst, kind, confidence, _evidence in store.edges_of(me):
        outgoing = src == me
        other = dst if outgoing else src
        link = {
            "relation": kind if outgoing else _INCOMING.get(kind, f"{kind}_by"),
            "target": other,
            "label": label_for(other),
            "url": url_for(other),
            "confidence": confidence,
        }
        if artefact := store.artefact(other):
            link["title_untrusted"] = artefact["title"][:200]
            link["state"] = artefact["state"]
            if artefact["body"]:
                link["excerpt_untrusted"] = artefact["body"][:400]
        found.append(link)
    return sorted(found, key=lambda link: (link["relation"], link["target"]))

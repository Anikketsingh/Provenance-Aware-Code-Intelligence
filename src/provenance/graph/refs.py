"""Find the links a commit message makes to tickets, pull requests, mail threads and commits.

Each repo has its own conventions. In Django, `#123` in a commit message is a Trac ticket. In
Redis and React, `(#123)` at the end of the subject is the pull request that was squash-merged.
GitHub numbers are shared by issues and pull requests, so an unresolved number becomes a
`gh:` node until the GitHub crawl can say which it is.

Node IDs: `commit:<sha>`, `ticket:django/<n>`, `pr:<repo>/<n>`, `issue:<repo>/<n>`,
`gh:<repo>/<n>`, `mail:<message-id>`. Repos outside the corpus use `owner/name` in place of
the short name.
"""

import re
from dataclasses import dataclass

from provenance.config import REPO_URLS

ALGO_VERSION = 1

#: Repos whose `#N` in commit messages means a Trac ticket.
TRAC_URLS = {"django": "https://code.djangoproject.com/ticket/{n}"}

#: "Fixed #1, #2 and #3" closes three tickets; "Refs #4" only mentions one.
_TRAC_KEYWORD = re.compile(
    r"\b(Fixed|Fixes|Fix|Closes|Closed|Refs|Ref)\s+((?:#\d+(?:\s*(?:,|and|&)\s*(?=#))?)+)"
)
_GH_CLOSING = re.compile(r"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s*:?\s+#(\d+)", re.I)
_SQUASH_SUFFIX = re.compile(r"\(#(\d+)\)\s*$")
_MERGE_PR = re.compile(r"^Merge pull request #(\d+) from ")
_BARE_NUMBER = re.compile(r"(?<![\w/&#])#(\d+)\b")
_GH_URL = re.compile(r"https?://github\.com/([\w.-]+)/([\w.-]+)/(pull|issues)/(\d+)")
_REVERTS = re.compile(r"This reverts commit ([0-9a-f]{7,40})")
_BACKPORT = re.compile(
    r"\(cherry picked from commit ([0-9a-f]{7,40})\)|Backport of ([0-9a-f]{7,40}) from"
)
_MAIL = re.compile(r"Discussion:\s*https?://postgr\.es/m/(\S+)")


@dataclass(frozen=True)
class Edge:
    src: str
    dst: str
    type: str
    confidence: float
    evidence: str


def github_slug(repo: str) -> str | None:
    """`owner/name` on GitHub. A repo keyed by its slug (any non-corpus repo) is its own slug."""
    if "/" in repo:
        return repo
    url = REPO_URLS.get(repo, "")
    match = re.match(r"https://github\.com/([\w.-]+/[\w.-]+?)(?:\.git)?$", url)
    return match[1] if match else None


def _repo_key(owner: str, name: str, repo: str) -> str:
    return repo if github_slug(repo) == f"{owner}/{name}" else f"{owner}/{name}"


def parse_message(repo: str, sha: str, subject: str, body: str) -> list[Edge]:
    """Every link this commit's message makes, as edges from `commit:<sha>`."""
    me = f"commit:{sha}"
    text = f"{subject}\n\n{body}"
    edges: dict[tuple[str, str], Edge] = {}

    def add(src: str, dst: str, kind: str, confidence: float, evidence: str) -> None:
        if (dst, kind) not in edges:
            edges[dst, kind] = Edge(src, dst, kind, confidence, evidence[:120])

    if repo in TRAC_URLS:
        for match in _TRAC_KEYWORD.finditer(text):
            closing = not match[1].startswith("Ref")
            for number in re.findall(r"#(\d+)", match[2]):
                kind = "closes" if closing else "references"
                add(me, f"ticket:{repo}/{number}", kind, 0.95 if closing else 0.9, match[0])
    else:
        if match := _SQUASH_SUFFIX.search(subject):
            add(f"pr:{repo}/{match[1]}", me, "merged_as", 0.9, match[0])
        if match := _MERGE_PR.match(subject):
            add(f"pr:{repo}/{match[1]}", me, "merged_as", 0.95, match[0])
        for match in _GH_CLOSING.finditer(text):
            add(me, f"issue:{repo}/{match[1]}", "closes", 0.8, match[0])
        squash = _SQUASH_SUFFIX.search(subject)
        for match in _BARE_NUMBER.finditer(text):
            if squash and match.start() == squash.start() + 1:
                continue
            if f"pr:{repo}/{match[1]}" in (edge.src for edge in edges.values()):
                continue
            node = f"gh:{repo}/{match[1]}"
            if (f"issue:{repo}/{match[1]}", "closes") not in edges:
                add(me, node, "references", 0.6, match[0])

    for owner, name, kind, number in _GH_URL.findall(text):
        node = f"{'pr' if kind == 'pull' else 'issue'}:{_repo_key(owner, name, repo)}/{number}"
        add(me, node, "references", 0.95, f"github.com/{owner}/{name}/{kind}/{number}")
    for match in _REVERTS.finditer(text):
        add(me, f"commit:{match[1]}", "reverts", 0.95, match[0])
    for match in _BACKPORT.finditer(text):
        add(me, f"commit:{match[1] or match[2]}", "backport_of", 0.95, match[0])
    for match in _MAIL.finditer(text):
        add(me, f"mail:{match[1].rstrip('>.,)')}", "discussion", 0.95, match[0])
    return list(edges.values())


def url_for(node: str) -> str | None:
    """A web address for a node, where one exists."""
    kind, _, rest = node.partition(":")
    if kind == "ticket":
        repo, _, number = rest.partition("/")
        template = TRAC_URLS.get(repo)
        return template.format(n=number) if template else None
    if kind in ("pr", "issue", "gh"):
        repo, _, number = rest.rpartition("/")
        slug = repo if "/" in repo else github_slug(repo)
        if not slug:
            return None
        return f"https://github.com/{slug}/{'pull' if kind == 'pr' else 'issues'}/{number}"
    if kind == "mail":
        return f"https://postgr.es/m/{rest}"
    return None


def label_for(node: str) -> str:
    """A short human name, such as `Ticket #31375` or `PR #10329`."""
    kind, _, rest = node.partition(":")
    number = rest.rpartition("/")[2]
    names = {"ticket": "Ticket", "pr": "PR", "issue": "Issue", "gh": "#"}
    if kind in names:
        prefix = names[kind]
        return f"{prefix}{number}" if prefix == "#" else f"{prefix} #{number}"
    if kind == "commit":
        return f"commit {rest[:10]}"
    return f"mail thread {rest[:24]}"

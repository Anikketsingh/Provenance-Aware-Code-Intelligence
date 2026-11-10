"""Links parsed from commit messages, using real Django and Redis messages."""

import pytest

from provenance.graph.build import link_messages
from provenance.graph.refs import label_for, parse_message, url_for
from provenance.ingest.git_history import ingest_history
from provenance.store.db import Store

SHA = "a" * 40


def links(repo: str, subject: str, body: str = "") -> set[tuple[str, str, str]]:
    return {(e.src, e.dst, e.type) for e in parse_message(repo, SHA, subject, body)}


ME = f"commit:{SHA}"


@pytest.mark.parametrize(
    ("subject", "expected"),
    [
        ("Fixed #28386 -- Made operations honor atomic.", {(ME, "ticket:django/28386", "closes")}),
        ("Fixed #8545: Corrected typo in request docs", {(ME, "ticket:django/8545", "closes")}),
        (
            "Refs #32673, Refs #35295 -- Avoided wrapping rhs direct values in lookups.",
            {(ME, "ticket:django/32673", "references"), (ME, "ticket:django/35295", "references")},
        ),
        (
            "Fixed #1, #2 and #3 -- Cleaned up.",
            {(ME, f"ticket:django/{n}", "closes") for n in (1, 2, 3)},
        ),
        ("Bumped version for 5.0 release.", set()),
    ],
)
def test_django_ticket_references(subject, expected):
    assert links("django", subject) == expected


def test_django_backport():
    found = links("django", "[5.0.x] Fixed #1 -- Fixed it.", "Backport of 0123456789ab from main.")
    assert (ME, "commit:0123456789ab", "backport_of") in found


def test_redis_squash_merge_and_issue_mention():
    found = links("redis", "Fix Lua DoS because of long running string find (#1561) (#16017)")
    assert found == {
        ("pr:redis/16017", ME, "merged_as"),
        (ME, "gh:redis/1561", "references"),
    }


def test_redis_merge_pull_request():
    found = links("redis", "Merge pull request #5873 from madolson/dev-fix")
    assert found == {("pr:redis/5873", ME, "merged_as")}


def test_redis_closing_keyword_is_not_also_a_mention():
    found = links("redis", "Fix replica crash (#12839)", "Fixes #12800")
    assert found == {("pr:redis/12839", ME, "merged_as"), (ME, "issue:redis/12800", "closes")}


def test_reverts_urls_and_mail_threads():
    body = (
        "This reverts commit 0123456789abcdef0123.\n"
        "See https://github.com/redis/redis/pull/42 and https://github.com/antirez/sds/issues/7\n"
        "Discussion: https://postgr.es/m/CAH2-Wz@mail.gmail.com"
    )
    found = links("postgres", "Revert something", body)
    assert (ME, "commit:0123456789abcdef0123", "reverts") in found
    assert (ME, "issue:antirez/sds/7", "references") in found
    assert (ME, "pr:redis/redis/42", "references") in found
    assert (ME, "mail:CAH2-Wz@mail.gmail.com", "discussion") in found


def test_html_entities_are_not_references():
    assert links("redis", "Escape &#123; in docs") == set()


@pytest.mark.parametrize(
    ("node", "url", "label"),
    [
        ("ticket:django/31375", "https://code.djangoproject.com/ticket/31375", "Ticket #31375"),
        ("pr:redis/10329", "https://github.com/redis/redis/pull/10329", "PR #10329"),
        ("gh:redis/1561", "https://github.com/redis/redis/issues/1561", "#1561"),
        ("issue:antirez/sds/7", "https://github.com/antirez/sds/issues/7", "Issue #7"),
        ("mail:abc@x", "https://postgr.es/m/abc@x", "mail thread abc@x"),
    ],
)
def test_urls_and_labels(node, url, label):
    assert url_for(node) == url
    assert label_for(node) == label


def test_link_messages_resolves_short_revert_hashes(git_repo):
    first = git_repo.commit("Add check (#7)", {"a.py": "x = 1\n"})
    git_repo.commit("Revert check", {"a.py": "x = 2\n"})
    git_repo.commit(f"Revert revert\n\nThis reverts commit {first[:9]}.", {"a.py": "x = 1\n"})
    repo = git_repo.repo
    with Store(repo.db_path) as store:
        ingest_history(repo, store)
        assert link_messages("redis", store) == 2
        incoming = store.edges_of(f"commit:{first}")
    kinds = {(src.split(":")[0], kind) for src, _dst, kind, _c, _e in incoming}
    assert kinds == {("pr", "merged_as"), ("commit", "reverts")}

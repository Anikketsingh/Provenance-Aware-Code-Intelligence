"""Trac ticket fetching, with the network replaced by a fake."""

import urllib.error

from provenance.ingest.trac import fetch_tickets, parse_ticket_csv
from provenance.store.db import Store

CSV = (
    "﻿id,summary,reporter,owner,description,type,status,resolution\r\n"
    '31375,make_password shouldn\'t accept other types,a,b,"Line one.\nLine two.",'
    "Cleanup,closed,fixed\r\n"
)


def test_parse_ticket_csv():
    fields = parse_ticket_csv(CSV)
    assert fields["summary"] == "make_password shouldn't accept other types"
    assert fields["description"] == "Line one.\nLine two."


def test_fetch_stores_each_ticket_once(tmp_path):
    calls = []

    def fake(url: str) -> str:
        calls.append(url)
        if "999" in url:
            raise urllib.error.URLError("not found")
        return CSV

    with Store(tmp_path / "p.db") as store:
        assert fetch_tickets("django", store, [31375, 999], download=fake) == 1
        assert fetch_tickets("django", store, [31375, 999], download=fake) == 0
        ticket = store.artefact("ticket:django/31375")
        assert store.artefact("ticket:django/999") is None
    assert calls == [
        "https://code.djangoproject.com/ticket/31375?format=csv",
        "https://code.djangoproject.com/ticket/999?format=csv",
    ]
    assert ticket["title"].startswith("make_password")
    assert ticket["state"] == "fixed"
    assert ticket["url"] == "https://code.djangoproject.com/ticket/31375"


def test_parse_opened_reads_the_exact_time_with_its_timezone():
    from provenance.ingest.trac import parse_opened

    html = (
        '<p>Opened <a class="timeline" href="/timeline?from=2020-03-17T15%3A57%3A53-05%3A00'
        '&amp;precision=second" title="x">7 years ago</a></p>'
    )
    assert parse_opened(html) == 1584478673  # 2020-03-17 20:57:53 UTC
    assert parse_opened("<p>no date here</p>") is None


def test_interpolation_is_monotonic_and_exact_at_anchors():
    from provenance.ingest.trac import interpolate_created

    anchors = {100: 1000, 200: 2000, 300: 2500}
    got = interpolate_created(anchors, [50, 100, 150, 250, 300, 400])
    assert got == {50: 1000, 100: 1000, 150: 1500, 250: 2250, 300: 2500, 400: 2500}
    # An out-of-order anchor never makes a later ticket earlier.
    bumpy = interpolate_created({100: 2000, 200: 1500}, [150])
    assert bumpy[150] >= 2000


def test_fetch_anchors_skips_pages_without_a_date():
    from provenance.ingest.trac import fetch_anchors

    pages = {
        "https://code.djangoproject.com/ticket/1": 'Opened <a class="timeline" '
        'href="/timeline?from=2005-07-13T12%3A00%3A00%2B00%3A00&amp;x">',
        "https://code.djangoproject.com/ticket/2": "deleted",
    }
    assert fetch_anchors("django", [1, 2], download=pages.__getitem__) == {1: 1121256000}


def test_estimates_never_overwrite_exact_dates(tmp_path):
    from provenance.store.db import Store

    with Store(tmp_path / "p.db") as store:
        store.add_artefact("pr:x/1", "pr", "t", "b", "MERGED", "u", "{}", created_at=500)
        store.add_artefact("ticket:x/2", "ticket", "t", "b", "fixed", "u", "")
        store.set_created([("pr:x/1", 999), ("ticket:x/2", 700)], estimated=True)
        assert store.created_at("pr:x/1") == (500, False)
        assert store.created_at("ticket:x/2") == (700, True)
        assert [h["id"] for h in store.search_artefacts("t", before=600)] == ["pr:x/1"]

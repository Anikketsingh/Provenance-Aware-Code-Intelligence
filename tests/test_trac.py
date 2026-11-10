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

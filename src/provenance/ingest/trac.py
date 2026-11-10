"""Fetch Django's Trac tickets that commits link to, politely.

Rules from plans/05-ingestion.md: only tickets that commits reference, at most one request per
second, each ticket fetched once, and a descriptive User-Agent. robots.txt allows /ticket/.
The CSV export has the summary and description but not the comments, which come later.
"""

import csv
import io
import time
import urllib.error
import urllib.request
from collections.abc import Callable

from provenance.graph.refs import TRAC_URLS
from provenance.store.db import Store

USER_AGENT = "provenance-research/0.1 (university research on code history; polite crawler)"
MIN_INTERVAL = 1.0
TIMEOUT = 30


def ticket_csv_url(repo: str, number: int) -> str:
    return TRAC_URLS[repo].format(n=number) + "?format=csv"


def parse_ticket_csv(text: str) -> dict:
    rows = list(csv.DictReader(io.StringIO(text.lstrip("﻿"))))
    if not rows:
        raise ValueError("empty ticket export")
    return rows[0]


def _download(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return response.read().decode("utf-8", errors="replace")


def fetch_tickets(
    repo: str,
    store: Store,
    numbers: list[int],
    download: Callable[[str], str] = _download,
    progress: Callable[[int, int], None] | None = None,
) -> int:
    """Fetch tickets not yet stored. Returns how many were added."""
    added = 0
    last_request = 0.0
    todo = [n for n in numbers if not store.has_artefact(f"ticket:{repo}/{n}")]
    for index, number in enumerate(todo, start=1):
        wait = MIN_INTERVAL - (time.monotonic() - last_request)
        if wait > 0 and download is _download:
            time.sleep(wait)
        last_request = time.monotonic()
        node = f"ticket:{repo}/{number}"
        url = TRAC_URLS[repo].format(n=number)
        try:
            raw = download(ticket_csv_url(repo, number))
            fields = parse_ticket_csv(raw)
        except (urllib.error.URLError, ValueError, TimeoutError) as error:
            store.add_artefact(node, "ticket", "", "", "missing", url, f"error: {error}")
            continue
        store.add_artefact(
            node,
            "ticket",
            fields.get("summary", ""),
            fields.get("description", ""),
            fields.get("resolution") or fields.get("status", ""),
            url,
            raw,
        )
        added += 1
        if progress:
            progress(index, len(todo))
    return added

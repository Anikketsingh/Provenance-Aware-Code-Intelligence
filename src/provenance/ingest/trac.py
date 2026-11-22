"""Fetch Django's Trac tickets that commits link to, politely.

Rules from plans/05-ingestion.md: only tickets that commits reference, at most one request per
second, each ticket fetched once, and a descriptive User-Agent. robots.txt allows /ticket/.
The CSV export has the summary and description but not the comments, which come later.
"""

import bisect
import csv
import io
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from datetime import datetime

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


# Trac's ticket export has no creation date, and robots.txt forbids its query pages. Tickets are
# numbered in the order they were opened, though, so the creation time of any ticket can be
# interpolated from a sparse set of "anchor" tickets whose ticket page (which robots.txt allows)
# shows the exact time. Interpolated dates are flagged as estimated.
_OPENED = re.compile(r'Opened <a class="timeline" href="/timeline\?from=([^&"]+)')


def parse_opened(html: str) -> int | None:
    """Unix time from the `Opened` line of a Trac ticket page."""
    match = _OPENED.search(html)
    if not match:
        return None
    stamp = urllib.parse.unquote(match[1])
    return int(datetime.fromisoformat(stamp).timestamp())


def fetch_anchors(
    repo: str,
    numbers: list[int],
    download: Callable[[str], str] = _download,
    progress: Callable[[int, int], None] | None = None,
) -> dict[int, int]:
    """Exact creation times for these ticket numbers, one polite request each."""
    anchors: dict[int, int] = {}
    last_request = 0.0
    for index, number in enumerate(numbers, start=1):
        wait = MIN_INTERVAL - (time.monotonic() - last_request)
        if wait > 0 and download is _download:
            time.sleep(wait)
        last_request = time.monotonic()
        try:
            opened = parse_opened(download(TRAC_URLS[repo].format(n=number)))
        except (urllib.error.URLError, TimeoutError):
            opened = None
        if opened is not None:
            anchors[number] = opened
        if progress:
            progress(index, len(numbers))
    return anchors


def interpolate_created(anchors: dict[int, int], numbers: list[int]) -> dict[int, int]:
    """Estimate creation times from anchors, assuming ticket numbers grow with time.

    Numbers outside the anchored range take the nearest anchor's time. The estimate is kept
    monotonic, so a later ticket number never gets an earlier date.
    """
    points = sorted(anchors.items())
    if not points:
        return {}
    keys = [n for n, _ in points]
    estimates = {}
    for number in numbers:
        i = bisect.bisect_left(keys, number)
        if i < len(keys) and keys[i] == number:
            estimates[number] = points[i][1]
        elif i == 0:
            estimates[number] = points[0][1]
        elif i == len(keys):
            estimates[number] = points[-1][1]
        else:
            (n0, t0), (n1, t1) = points[i - 1], points[i]
            t1 = max(t1, t0)
            estimates[number] = round(t0 + (t1 - t0) * (number - n0) / (n1 - n0))
    return estimates

"""How much history says a guard matters: a deterministic score with its reasons.

No language model is involved, so the same guard always gets the same score and the same
reasons. Each signal adds a fixed weight, capped at 1.0:

| Signal | Weight | Why it matters |
|---|---|---|
| The change that set the guard links to a ticket, PR or issue | 0.30 | Someone recorded a reason |
| That change, or its discussion, uses bug or safety words | 0.25 | The reason was a failure |
| Security words (CVE, vulnerability, injection, ...) | 0.15 | The failure was a security one |
| The change was itself a fix ("Fix", "Fixed #N") | 0.15 | The guard was the cure |
| The guard's history includes a revert or a re-add | 0.15 | It was removed before and came back |
| The guard has existed for over a year | 0.05 | Long-lived code others rely on |

Commit and ticket text is third-party, so it is only ever matched against fixed word lists,
never interpreted.
"""

import re
import time
from dataclasses import dataclass, field

from provenance.graph.build import commit_links
from provenance.store.db import Store
from provenance.trace.chain import Tracer

WEIGHTS = {
    "linked": 0.30,
    "bug_words": 0.25,
    "security_words": 0.15,
    "fix_commit": 0.15,
    "reverted": 0.15,
    "old": 0.05,
}
#: Findings at or above this score are reported. Chosen on guard events before 2020 only
#: (eval/protect_tune.py), then frozen; see eval/results/protect_threshold.json.
DEFAULT_THRESHOLD = 0.5

_BUG = re.compile(
    r"\b(fix(e[sd])?|bug|crash\w*|regression|race|deadlock|leak\w*|overflow|underflow|"
    r"corrupt\w*|segfault|panic|hang\w*|null pointer|NPE|incorrect|wrong|broken|"
    r"data loss|infinite loop|timeout|denial)\b",
    re.I,
)
_SECURITY = re.compile(
    r"\b(CVE-\d|security|vulnerab\w*|exploit\w*|injection|XSS|CSRF|traversal|"
    r"privilege|auth\w*|password|secret|sanitiz\w*|escap\w*|DoS)\b",
    re.I,
)
_FIX_SUBJECT = re.compile(r"^\s*(\[[^\]]*\]\s*)?(fix(e[sd])?|hotfix|bugfix)\b|fixed #\d+", re.I)
_YEAR = 365 * 24 * 3600


@dataclass
class History:
    score: float
    signals: list[str]
    origin: str | None
    origin_subject: str = ""
    origin_date: int | None = None
    links: list[dict] = field(default_factory=list)


def score_guard(
    tracer: Tracer, store: Store, path: str, line: int, rev: str, now: int | None = None
) -> History:
    """Trace the guard's line at `rev` and score what its history says."""
    try:
        chain = tracer.trace(path, line, rev)
    except Exception as error:  # an untraceable line has no history to weigh, not safety
        return History(0.0, [f"history could not be traced ({type(error).__name__})"], None)
    origin = chain.origin
    if origin is None:
        return History(0.0, ["history could not be traced"], None)

    logic = [hop.commit for hop in chain.hops if str(hop.kind) in ("logic", "origin")]
    links = []
    for sha in dict.fromkeys(logic):
        links.extend(link | {"commit": sha} for link in commit_links(store, sha))
    discussions = [link for link in links if not link["target"].startswith("commit:")]

    texts = []
    for sha in dict.fromkeys(logic):
        texts.append(f"{store.subject(sha)}\n{store.body(sha)}")
    for link in discussions:
        texts.append(link.get("title_untrusted", "") + "\n" + link.get("excerpt_untrusted", ""))
    corpus = "\n".join(texts)

    signals = []
    if discussions:
        first = discussions[0]
        signals.append(f"linked to {first['label']}")
    if _BUG.search(corpus):
        signals.append(f"bug words in its history ('{_BUG.search(corpus)[0]}')")
    if _SECURITY.search(corpus):
        signals.append(f"security words in its history ('{_SECURITY.search(corpus)[0]}')")
    if any(_FIX_SUBJECT.search(store.subject(sha)) for sha in dict.fromkeys(logic)):
        signals.append("added by a fix")
    if any(link["relation"] in ("reverts", "reverted_by") for link in links):
        signals.append("history includes a revert")
    when = store.commit_time(origin)
    if when is not None and (now or int(time.time())) - when > _YEAR:
        signals.append(f"in place since {time.strftime('%Y-%m-%d', time.gmtime(when))}")

    weights = {
        "linked": bool(discussions),
        "bug_words": bool(_BUG.search(corpus)),
        "security_words": bool(_SECURITY.search(corpus)),
        "fix_commit": any(_FIX_SUBJECT.search(store.subject(sha)) for sha in dict.fromkeys(logic)),
        "reverted": any(link["relation"] in ("reverts", "reverted_by") for link in links),
        "old": when is not None and (now or int(time.time())) - when > _YEAR,
    }
    score = min(1.0, sum(WEIGHTS[name] for name, on in weights.items() if on))
    return History(
        round(score, 2),
        signals,
        origin,
        store.subject(origin),
        when,
        discussions,
    )

"""Mine history for guard removals, and label which ones came back after a bug (RQ4 data).

For every non-merge commit, the guards of each changed source file are compared before and
after, with the same code `whyblame check` uses. That gives removal events (a guard removed
or weakened) and addition events (a guard appearing).

A removal is labelled, for windows of 30, 90 and 180 days:

- positive: the same guard (same fingerprint, same file) came back within the window, in a
  commit that reverts the removal, is a fix, uses bug words, or links a ticket or PR.
- negative: it did not come back within 365 days, and history runs at least 365 days past it.
- unlabelled: anything else (came back without bug evidence, or too recent to tell).

Test files are skipped: test assertions are not protective code. Bulk commits that remove more
than 50 guards are marked and left out of evaluation. They're mostly deletions of whole
modules.

The split is by date: removals before 2020 are for tuning the threshold, and removals from
2020 on are the held-out test.

Usage: uv run python eval/mine_guards.py django redis
"""

import bisect
import json
import re
import sys
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from itertools import islice
from pathlib import Path

from provenance.config import Repo
from provenance.gitio import BlobReader, FileChange
from provenance.protect.guards import compare_guards, find_guards
from provenance.protect.score import _BUG, _FIX_SUBJECT
from provenance.store.db import Store
from provenance.trace.classify import MAX_BLOB_SIZE
from provenance.trace.tokens import language_for

OUT = Path(__file__).parent / "data"
WINDOWS = (30, 90, 180)
NEGATIVE_DAYS = 365
BULK = 50
SPLIT = int(time.mktime(time.strptime("2020-01-01", "%Y-%m-%d")))
DAY = 86400
_TEST_PATH = re.compile(r"(^|/)(tests?|__tests__|testing|spec)(/|$)|(^|/)test_[^/]*$|_test\.\w+$")
_BATCH = 50


def is_test(path: str) -> bool:
    return bool(_TEST_PATH.search(path))


def _mine_batch(git_dir: Path, batch: list[tuple[str, list[FileChange]]]) -> list[dict]:
    rows = []
    with BlobReader(git_dir) as reader:
        for sha, changes in batch:
            files = []
            for change in changes:
                path = change.path
                old_path = change.old_path or path
                language = language_for(old_path)
                if language is None or is_test(old_path) or change.status == "A":
                    continue
                before = reader.read(change.old_blob, MAX_BLOB_SIZE) if change.old_blob else None
                if before is None:
                    continue
                after = b""
                if change.status != "D" and change.new_blob:
                    after = reader.read(change.new_blob, MAX_BLOB_SIZE)
                    if after is None:
                        continue
                files.append(
                    (old_path, path, find_guards(before, language), find_guards(after, language))
                )
            added_anywhere = set()
            for _old, _new, base, head in files:
                seen = {g.fingerprint for g in base}
                added_anywhere |= {g.fingerprint for g in head if g.fingerprint not in seen}
            removals, additions = [], []
            for old_path, path, base, head in files:
                for change in compare_guards(base, head, added_anywhere):
                    g = change.guard
                    removals.append(
                        {
                            "path": old_path,
                            "line": g.line,
                            "kind": g.kind,
                            "change": change.change,
                            "reason": change.reason,
                            "function": g.function,
                            "code": g.text,
                            "fingerprint": g.fingerprint,
                        }
                    )
                before = {g.fingerprint for g in base}
                for g in head:
                    if g.fingerprint not in before:
                        additions.append({"path": path, "fingerprint": g.fingerprint})
            if removals or additions:
                rows.append({"sha": sha, "removals": removals, "additions": additions})
    return rows


def mine(name: str, workers: int = 4) -> list[dict]:
    repo = Repo.named(name)
    with Store(repo.db_path) as store:
        commits = store._db.execute(
            "SELECT sha, commit_time FROM commits WHERE is_merge = 0 ORDER BY commit_time"
        ).fetchall()
        times = dict(commits)
        tasks = [(sha, store.changes(sha)) for sha, _ in commits]
        print(f"{name}: scanning {len(tasks)} commits", flush=True)
        batches = []
        it = iter(tasks)
        while batch := list(islice(it, _BATCH)):
            batches.append(batch)
        rows = []
        with ProcessPoolExecutor(max_workers=workers) as pool:
            for done, result in enumerate(
                pool.map(_mine_batch, [repo.git_dir] * len(batches), batches), start=1
            ):
                rows.extend(result)
                if done % 100 == 0:
                    print(f"  {done * _BATCH}/{len(tasks)} commits", flush=True)

        # Additions indexed by (path, fingerprint) for the restoration search.
        added: dict[tuple[str, str], list[tuple[int, str]]] = defaultdict(list)
        for row in rows:
            for a in row["additions"]:
                added[(a["path"], a["fingerprint"])].append((times[row["sha"]], row["sha"]))
        for key in added:
            added[key].sort()
        history_end = max(times.values())

        def bug_evidence(restorer: str, remover: str) -> list[str]:
            evidence = []
            subject = store.subject(restorer)
            message = f"{subject}\n{store.body(restorer)}"
            if f"This reverts commit {remover[:7]}" in message or any(
                e[1] == f"commit:{remover}" and e[2] == "reverts"
                for e in store.edges_of(f"commit:{restorer}")
            ):
                evidence.append("reverts the removal")
            if _FIX_SUBJECT.search(subject):
                evidence.append("fix commit")
            if _BUG.search(message):
                evidence.append("bug words")
            if any(
                e[0] == f"commit:{restorer}" and not e[1].startswith("commit:")
                for e in store.edges_of(f"commit:{restorer}")
            ):
                evidence.append("links a discussion")
            return evidence

        events = []
        for row in rows:
            when = times[row["sha"]]
            bulk = len(row["removals"]) > BULK
            for r in row["removals"]:
                later = added.get((r["path"], r["fingerprint"]), [])
                i = bisect.bisect_right(later, (when, "￿"))
                restored = later[i] if i < len(later) else None
                gap = (restored[0] - when) / DAY if restored else None
                evidence = bug_evidence(restored[1], row["sha"]) if restored else []
                labels = {}
                for window in WINDOWS:
                    if restored and gap <= window and evidence:
                        labels[str(window)] = 1
                    elif (not restored or gap > NEGATIVE_DAYS) and (
                        history_end - when >= NEGATIVE_DAYS * DAY
                    ):
                        labels[str(window)] = 0
                    else:
                        labels[str(window)] = None
                events.append(
                    {
                        "repo": name,
                        "sha": row["sha"],
                        "time": when,
                        "split": "tune" if when < SPLIT else "test",
                        "bulk": bulk,
                        **r,
                        "restored_by": restored[1] if restored else None,
                        "restored_after_days": round(gap, 1) if gap is not None else None,
                        "restore_evidence": evidence,
                        "label": labels,
                    }
                )
    return events


def main() -> None:
    names = sys.argv[1:] or ["django", "redis"]
    OUT.mkdir(exist_ok=True)
    all_events = []
    for name in names:
        all_events.extend(mine(name))
    out = OUT / "guard_events.jsonl"
    with out.open("w") as handle:
        for event in all_events:
            handle.write(json.dumps(event) + "\n")
    summary: dict = {}
    for e in all_events:
        if e["bulk"]:
            continue
        s = summary.setdefault(e["repo"], {}).setdefault(e["split"], defaultdict(int))
        s["events"] += 1
        for window, label in e["label"].items():
            s[
                f"pos@{window}"
                if label == 1
                else f"neg@{window}"
                if label == 0
                else f"unl@{window}"
            ] += 1
    print(json.dumps(summary, indent=2))
    (Path(__file__).parent / "results" / "guard_events_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )
    print(f"Saved {len(all_events)} events to {out}")


if __name__ == "__main__":
    main()

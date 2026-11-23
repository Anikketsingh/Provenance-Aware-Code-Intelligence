"""Check a change for removed or weakened protective code, and say why that code was there.

`base` is a revision. `head` is a revision, or WORKTREE for the uncommitted files in a working
copy, which is what an agent has before it commits. Nothing in the change is executed: files
are read as text.
"""

import json
import re
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path

from provenance.config import Repo
from provenance.gitio import git
from provenance.protect.guards import GuardChange, compare_guards, find_guards
from provenance.protect.score import DEFAULT_THRESHOLD, score_guard, with_context
from provenance.store.db import Store
from provenance.trace.chain import Tracer
from provenance.trace.tokens import language_for

WORKTREE = "WORKTREE"
_HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


@dataclass
class Finding:
    path: str
    line: int  # where to show it in the head version
    change: str  # removed | weakened
    kind: str
    code: str
    reason: str
    score: float
    flagged: bool
    signals: list[str] = field(default_factory=list)
    origin: str | None = None
    origin_subject_untrusted: str = ""
    links: list[dict] = field(default_factory=list)
    first_seen: str | None = None
    first_seen_subject_untrusted: str = ""


def check_change(
    repo: Repo,
    base: str = "HEAD",
    head: str = WORKTREE,
    threshold: float = DEFAULT_THRESHOLD,
) -> list[Finding]:
    """Every removed or weakened guard between base and head, scored by its history."""
    base = resolve_commit(repo, base)
    if head != WORKTREE:
        head = resolve_commit(repo, head)
    files = _changed_files(repo, base, head)
    versions = {}
    for status, old_path, new_path in files:
        language = language_for(old_path or new_path)
        if language is None or status == "A":
            continue
        before = _read(repo, base, old_path)
        after = b"" if status == "D" else _read(repo, head, new_path)
        if before is None:
            continue
        versions[(old_path, new_path)] = (
            find_guards(before, language),
            find_guards(after or b"", language),
        )

    # A guard that disappears from one file but appears in another file of the same change
    # moved; it wasn't removed.
    added_anywhere: set[str] = set()
    for base_guards, head_guards in versions.values():
        before = {g.fingerprint for g in base_guards}
        added_anywhere |= {g.fingerprint for g in head_guards if g.fingerprint not in before}

    removed_total = sum(
        len(_outermost(compare_guards(b, h, added_anywhere))) for b, h in versions.values()
    )
    findings = []
    with Store(repo.db_path) as store:
        tracer = Tracer(repo, store)
        for (old_path, new_path), (base_guards, head_guards) in versions.items():
            changes = _outermost(compare_guards(base_guards, head_guards, added_anywhere))
            if not changes:
                continue
            line_map = _line_map(repo, base, head, old_path, new_path)
            for change in changes:
                history = score_guard(tracer, store, old_path, change.guard.line, base)
                score, context = with_context(history.score, removed_total)
                where = change.after.line if change.after else line_map(change.guard.line)
                findings.append(
                    Finding(
                        path=new_path or old_path,
                        line=where,
                        change=change.change,
                        kind=change.guard.kind,
                        code=change.guard.text,
                        reason=change.reason,
                        score=round(score, 2),
                        flagged=score >= threshold,
                        signals=[*history.signals, context],
                        origin=history.origin,
                        origin_subject_untrusted=history.origin_subject,
                        first_seen=history.first_seen,
                        first_seen_subject_untrusted=history.first_seen_subject,
                        links=[
                            {
                                k: link.get(k)
                                for k in ("label", "url", "title_untrusted", "relation")
                            }
                            for link in history.links[:3]
                        ],
                    )
                )
    return sorted(findings, key=lambda f: (-f.score, f.path, f.line))


def resolve_commit(repo: Repo, rev: str) -> str:
    """The full commit id of a revision like `HEAD~1` or `main`, or ValueError.

    Anything starting with `-` is refused, so a revision can never act as a git option.
    """
    if not rev or rev.startswith("-"):
        raise ValueError(f"not a revision: {rev!r}")
    try:
        return git(
            repo.git_dir, "rev-parse", "--verify", "--end-of-options", f"{rev}^{{commit}}"
        ).strip()
    except Exception:
        raise ValueError(f"unknown revision: {rev!r}") from None


def _outermost(changes: list[GuardChange]) -> list[GuardChange]:
    """One finding per removed block: a raise inside a removed `if ...: raise` isn't repeated."""
    kept = []
    for change in changes:
        inside = any(
            other is not change
            and other.change == change.change
            and other.guard.line <= change.guard.line
            and change.guard.end_line <= other.guard.end_line
            and (other.guard.line, other.guard.end_line)
            != (change.guard.line, change.guard.end_line)
            for other in changes
        )
        if not inside:
            kept.append(change)
    return kept


def _changed_files(repo: Repo, base: str, head: str) -> list[tuple[str, str | None, str | None]]:
    """(status, old path, new path) for each changed file, following renames."""
    args = ["diff", "--name-status", "-M", "--no-color", base]
    if head != WORKTREE:
        args.append(head)
    out = _git_for(repo, head, *args)
    files = []
    for row in out.splitlines():
        parts = row.split("\t")
        status = parts[0][0]
        if status == "R" and len(parts) == 3:
            files.append(("R", parts[1], parts[2]))
        elif status == "D":
            files.append(("D", parts[1], None))
        elif status in ("M", "A", "T"):
            files.append((status, parts[1], parts[1]))
    return files


def _read(repo: Repo, rev: str, path: str | None) -> bytes | None:
    if path is None:
        return None
    if rev == WORKTREE:
        file = _work_tree(repo) / path
        return file.read_bytes() if file.is_file() else None
    try:
        return subprocess.run(
            ["git", "--git-dir", str(repo.git_dir), "show", f"{rev}:{path}"],
            check=True,
            capture_output=True,
        ).stdout
    except subprocess.CalledProcessError:
        return None


def _line_map(repo: Repo, base: str, head: str, old_path: str, new_path: str | None):
    """Map a base line number to the nearest line of the head version, using diff hunks."""
    if new_path is None:
        return lambda line: 1
    args = ["diff", "-U0", "-M", "--no-color", base]
    if head != WORKTREE:
        args.append(head)
    args += ["--", old_path] + ([new_path] if new_path != old_path else [])
    hunks = []
    for row in _git_for(repo, head, *args).splitlines():
        if match := _HUNK.match(row):
            old_start, old_len = int(match[1]), int(match[2] or 1)
            new_start, new_len = int(match[3]), int(match[4] or 1)
            hunks.append((old_start, old_len, new_start, new_len))

    def mapped(line: int) -> int:
        shift = 0
        for old_start, old_len, new_start, new_len in hunks:
            if old_start <= line < old_start + max(old_len, 1):
                return max(new_start, 1)
            if old_start + old_len <= line:
                shift = (new_start + new_len) - (old_start + old_len)
        return max(line + shift, 1)

    return mapped


def _work_tree(repo: Repo) -> Path:
    if repo.git_dir.name != ".git":
        raise ValueError("WORKTREE needs a working copy, not a bare repository")
    return repo.git_dir.parent


def _git_for(repo: Repo, head: str, *args: str) -> str:
    if head == WORKTREE:
        return subprocess.run(
            ["git", "-C", str(_work_tree(repo)), *args],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    return git(repo.git_dir, *args)


# --- Output -------------------------------------------------------------------------------


def _message(finding: Finding) -> str:
    parts = [f"{finding.kind} `{finding.code}` was {finding.change} ({finding.reason})."]
    if finding.origin:
        if finding.first_seen:
            parts.append(
                f"It first appeared in {finding.first_seen[:10]} "
                f'"{finding.first_seen_subject_untrusted}", and was last changed in '
                f'{finding.origin[:10]} "{finding.origin_subject_untrusted}".'
            )
        else:
            parts.append(
                f'It was added in {finding.origin[:10]} "{finding.origin_subject_untrusted}".'
            )
    for link in finding.links[:1]:
        title = link.get("title_untrusted") or ""
        text = " ".join(filter(None, [f"{link['label']}:" if title else link["label"], title]))
        where = f" {link['url']}" if link.get("url") else ""
        parts.append(f"See {text}{where}.")
    parts.append(f"History score {finding.score:.2f}: {'; '.join(finding.signals) or 'none'}.")
    return " ".join(parts)


def _escape_data(text: str) -> str:
    return text.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def _escape_property(text: str) -> str:
    return _escape_data(text).replace(":", "%3A").replace(",", "%2C")


def render(findings: list[Finding], fmt: str, *, show_all: bool = False) -> str:
    shown = [f for f in findings if f.flagged or show_all]
    if fmt == "json":
        return json.dumps([asdict(f) for f in shown], indent=2)
    if fmt == "github":
        return "\n".join(
            f"::warning file={_escape_property(f.path)},line={f.line},"
            f"title={_escape_property(f'Protective code {f.change}')}::"
            f"{_escape_data(_message(f))}"
            for f in shown
        )
    if not shown:
        quiet = len(findings) - len(shown)
        return "No protective code with a recorded history was removed or weakened." + (
            f" ({quiet} lower-scored change{'s' if quiet != 1 else ''} hidden; --all shows them.)"
            if quiet
            else ""
        )
    return "\n\n".join(f"{f.path}:{f.line}  [score {f.score:.2f}]\n  {_message(f)}" for f in shown)

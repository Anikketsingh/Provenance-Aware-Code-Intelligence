"""Thin wrappers around the git command line.

Arguments always go to git as a list, never through a shell. Output is decoded with
errors="replace" because old commits are not always valid UTF-8.
"""

import re
import subprocess
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

_REV_RE = re.compile(r"^[0-9A-Za-z][0-9A-Za-z._/-]*$")
_FIELD = "\x01"
_RECORD_END = "\x02"
_LOG_FORMAT = (
    "%x00" + _FIELD.join(["%H", "%P", "%at", "%ct", "%s", "%b"]).replace(_FIELD, "%x01") + "%x02"
)

#: Raw output is delimited by NUL, so reads are chunked rather than line based.
_CHUNK_SIZE = 1 << 20


class GitError(RuntimeError):
    pass


def validate_rev(rev: str) -> str:
    """Reject anything git could read as an option or a revision expression."""
    if not _REV_RE.fullmatch(rev) or ".." in rev:
        raise ValueError(f"unsafe revision: {rev!r}")
    return rev


def git(git_dir: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(git_dir), "-c", "core.quotePath=false", *args],
        capture_output=True,
    )
    if result.returncode != 0:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise GitError(f"git {args[0]} failed: {message}")
    return result.stdout.decode("utf-8", errors="replace")


@dataclass(frozen=True)
class FileChange:
    status: str  # A, M, D, R, T...
    old_path: str | None
    path: str
    old_blob: str | None
    new_blob: str | None


@dataclass(frozen=True)
class CommitRecord:
    sha: str
    parents: tuple[str, ...]
    author_time: int
    commit_time: int
    subject: str
    body: str
    changes: tuple[FileChange, ...]


def _parse_raw_line(line: str) -> FileChange | None:
    meta, _, names = line.partition("\t")
    fields = meta.split()
    if len(fields) != 5:
        return None
    old_blob, new_blob, status = fields[2], fields[3], fields[4][0]
    parts = names.split("\t")
    is_null = set(old_blob) == {"0"}
    return FileChange(
        status=status,
        old_path=None if status == "A" else parts[0],
        path=parts[-1],
        old_blob=None if is_null else old_blob,
        new_blob=None if set(new_blob) == {"0"} else new_blob,
    )


def _parse_record(record: str) -> CommitRecord:
    header, _, raw = record.partition(_RECORD_END)
    sha, parents, author_time, commit_time, subject, body = header.split(_FIELD, 5)
    changes = []
    for line in raw.splitlines():
        if line.startswith(":") and (change := _parse_raw_line(line)):
            changes.append(change)
    return CommitRecord(
        sha=sha,
        parents=tuple(parents.split()),
        author_time=int(author_time),
        commit_time=int(commit_time),
        subject=subject,
        body=body.strip(),
        changes=tuple(changes),
    )


def iter_commits(git_dir: Path, rev: str = "HEAD") -> Iterator[CommitRecord]:
    """Stream every commit reachable from rev, with file changes against its first parent."""
    validate_rev(rev)
    process = subprocess.Popen(
        [
            "git",
            "-C",
            str(git_dir),
            "-c",
            "core.quotePath=false",
            "log",
            "-M",
            "--raw",
            "--no-abbrev",
            "--no-color",
            f"--format={_LOG_FORMAT}",
            rev,
            "--",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert process.stdout is not None
    buffer = ""
    while chunk := process.stdout.read(_CHUNK_SIZE):
        buffer += chunk
        records = buffer.split("\x00")
        buffer = records.pop()
        for record in records:
            if record.strip():
                yield _parse_record(record)
    if buffer.strip():
        yield _parse_record(buffer)
    if process.wait() != 0:
        raise GitError(f"git log failed for {rev}")


class BlobReader:
    """Reads many blobs through one long-lived `git cat-file --batch` process."""

    def __init__(self, git_dir: Path):
        self._process = subprocess.Popen(
            ["git", "-C", str(git_dir), "cat-file", "--batch"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )

    def read(self, blob: str, max_size: int | None = None) -> bytes | None:
        """Return the blob's bytes, or None if it is missing or larger than max_size."""
        assert self._process.stdin and self._process.stdout
        self._process.stdin.write(blob.encode() + b"\n")
        self._process.stdin.flush()
        header = self._process.stdout.readline().split()
        if len(header) != 3:
            return None
        size = int(header[2])
        data = self._process.stdout.read(size + 1)[:-1]  # trailing newline after each object
        return None if max_size is not None and size > max_size else data

    def close(self) -> None:
        assert self._process.stdin
        self._process.stdin.close()
        self._process.wait()

    def __enter__(self) -> "BlobReader":
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

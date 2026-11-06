"""Run `git blame` and parse the result."""

import os
import re
import tempfile
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from provenance.gitio import git, validate_rev

#: The strongest flags git offers: ignore whitespace, follow moves within and across files.
STRONGEST_FLAGS = ("-w", "-M", "-C", "-C")

_HEADER_RE = re.compile(r"^([0-9a-f]{40}) (\d+) (\d+)")


@dataclass(frozen=True)
class BlameLine:
    commit: str
    orig_path: str
    orig_line: int
    text: str


def parse_line_porcelain(output: str) -> list[BlameLine]:
    lines: list[BlameLine] = []
    commit = ""
    orig_line = 0
    orig_path = ""
    for row in output.split("\n"):
        if row.startswith("\t"):
            lines.append(BlameLine(commit, orig_path, orig_line, row[1:]))
        elif match := _HEADER_RE.match(row):
            commit, orig_line = match[1], int(match[2])
        elif row.startswith("filename "):
            orig_path = row[len("filename ") :]
    return lines


def blame_file(
    git_dir: Path,
    path: str,
    rev: str = "HEAD",
    flags: tuple[str, ...] = STRONGEST_FLAGS,
    ignore_revs: Iterable[str] = (),
) -> list[BlameLine]:
    args = ["blame", "--line-porcelain", *flags]
    revs = list(ignore_revs)
    if not revs:
        return parse_line_porcelain(git(git_dir, *args, validate_rev(rev), "--", path))

    # Listed on disk, since a long list can exceed the command-line length limit.
    handle, ignore_path = tempfile.mkstemp(suffix=".revs")
    try:
        with os.fdopen(handle, "w") as ignore_file:
            ignore_file.write("".join(f"{sha}\n" for sha in revs))
        args += ["--ignore-revs-file", ignore_path]
        return parse_line_porcelain(git(git_dir, *args, validate_rev(rev), "--", path))
    finally:
        os.unlink(ignore_path)

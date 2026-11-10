"""Gather the git evidence an annotator needs for each line, following code across moves.

`git log -L` stops when code moves between files or functions. When a line's history starts
with the line being added, this searches the parent commit for the same code and continues the
history there. It uses only git, never the method being evaluated, so labels stay independent.

Usage: uv run python eval/label_helper.py --set test   # writes gold/test/evidence/<id>.txt
"""

import argparse
import csv
import re
import subprocess
from pathlib import Path

from corpus import pinned_rev

from provenance.config import Repo

GOLD = Path(__file__).parent / "gold"
MAX_HOPS = 4
MAX_CHARS = 9000


def run(git_dir: Path, *args: str) -> str:
    output = subprocess.run(
        ["git", "-C", str(git_dir), *args], capture_output=True, timeout=180, check=False
    )
    return output.stdout.decode("utf-8", errors="replace")


def history(git_dir: Path, path: str, line: int, rev: str) -> str:
    return run(
        git_dir, "log", "--no-color", "-w", "--date=short",
        "--format=@@COMMIT %H  %ad  %s", f"-L{line},{line}:{path}", rev,
    )  # fmt: skip


def oldest_addition(text: str) -> str | None:
    """The oldest commit in a history, if it shows the line as a pure addition."""
    blocks = text.split("@@COMMIT ")[1:]
    if not blocks:
        return None
    last = blocks[-1]
    hunk = re.search(r"^@@ -\d+,0 \+", last, re.MULTILINE)
    return last[:40] if hunk or "--- /dev/null" in last else None


def code_part(code: str) -> str:
    return " ".join(re.split(r"/\*|//|\s#\s", code)[0].split())


def find_in_parent(git_dir: Path, sha: str, code: str) -> list[tuple[str, int, str]]:
    """Places in the parent commit with the same code, ignoring whitespace."""
    needle = code_part(code)
    if len(needle) < 6:
        return []
    words = needle.split()
    pattern = r"\s*".join(re.escape(word) for word in words)
    hits = run(git_dir, "grep", "-n", "-P", pattern, f"{sha}^", "--")
    found = []
    for row in hits.splitlines()[:6]:
        _rev, path, number, text = row.split(":", 3)
        found.append((path, int(number), text.strip()))
    return found


def evidence(repo: Repo, rev: str, path: str, line: int, code: str) -> str:
    parts = []
    current_path, current_line, current_rev = path, line, rev
    for hop in range(MAX_HOPS):
        text = history(repo.git_dir, current_path, current_line, current_rev)
        parts.append(f"=== history of {current_path}:{current_line} at {current_rev[:10]}\n{text}")
        added = oldest_addition(text)
        if not added:
            break
        places = find_in_parent(repo.git_dir, added, code)
        if not places:
            parts.append(f"=== {added[:10]} added the line; the same code is not in its parent")
            break
        listing = "\n".join(f"  {p}:{n}  {t}" for p, n, t in places)
        parts.append(f"=== the same code already existed in {added[:10]}^ at:\n{listing}")
        current_path, current_line = places[0][0], places[0][1]
        current_rev = f"{added}^"
        if hop == MAX_HOPS - 1:
            parts.append("=== stopped after several hops")
    joined = "\n".join(parts)
    return joined if len(joined) < MAX_CHARS * 3 else joined[: MAX_CHARS * 3] + "\n... (cut)"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--set", choices=("dev", "test"), default="test")
    folder = GOLD if parser.parse_args().set == "dev" else GOLD / "test"
    # Read the blank sheet, not sample_key.json, so the annotator sees nothing about strata
    with (folder / "annotations.csv").open(newline="") as handle:
        items = [dict(row, line=int(row["line"])) for row in csv.DictReader(handle)]
    out = folder / "evidence"
    out.mkdir(exist_ok=True)
    for item in items:
        repo = Repo.named(item["repo"])
        text = evidence(repo, pinned_rev(item["repo"]), item["path"], item["line"], item["code"])
        (out / f"{item['id']}.txt").write_text(
            f"{item['path']}:{item['line']}\n{item['code']}\n\n{text}"
        )
        print(item["id"], flush=True)


if __name__ == "__main__":
    main()

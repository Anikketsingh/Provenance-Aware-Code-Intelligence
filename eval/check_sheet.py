"""Turn disagreements between two annotators into a short sheet a person can settle.

For each line where the annotators name different commits, the sheet shows the line and each
proposed commit with its diff, as A and B in random order, so the person can't tell who
proposed which. They answer one question per line in check_sheet.csv. `--apply` then writes
the adjudicated labels to annotations_final.csv.

Usage:
  uv run python eval/check_sheet.py [--set dev|test]           # write the sheet
  uv run python eval/check_sheet.py [--set dev|test] --apply   # merge the answers
"""

import argparse
import csv
import random
import re
import subprocess
from pathlib import Path

from corpus import pinned_rev

from provenance.config import Repo

GOLD = Path(__file__).parent / "gold"
SEED = 5
MAX_DIFF_LINES = 30


def read(path: Path) -> dict[str, dict]:
    with path.open(newline="") as handle:
        return {row["id"]: row for row in csv.DictReader(handle)}


def same(a: str, b: str) -> bool:
    """True if any alternative in `a` (labels may list `abc|def`) matches any in `b`."""
    left = {x.strip().lower()[:7] for x in a.split("|")}
    right = {x.strip().lower()[:7] for x in b.split("|")}
    return any(len(x) == 7 for x in left & right)


def commit_view(repo: Repo, sha: str, path: str, line: int, rev: str, code: str) -> str:
    """The commit's subject, its diff in this line's history, and every place in the commit
    where text like this line was added or removed, so moves between files are visible."""
    git_dir = str(repo.git_dir)
    header = subprocess.run(
        ["git", "-C", git_dir, "show", "-s", "--date=short", "--format=%h  %ad  %s", sha],
        capture_output=True, text=True, check=False,
    ).stdout.strip()  # fmt: skip
    parts = [header]
    command = [
        "git", "-C", git_dir, "log", "--no-color", "-w", "--date=short",
        "--format=@@COMMIT %H", f"-L{line},{line}:{path}", rev,
    ]  # fmt: skip
    text = subprocess.run(command, capture_output=True, timeout=180, check=False).stdout.decode(
        "utf-8", errors="replace"
    )
    for block in text.split("@@COMMIT ")[1:]:
        if block.startswith(sha[:7]):
            rows = block.split("\n")[1:]
            changed = [r for r in rows if r[:1] in "+-" and not r.startswith(("+++", "---"))]
            parts += ["In this line's history:", *changed[:MAX_DIFF_LINES]]
            break
    else:
        parts.append("Not in this line's history in its current file.")
    # Code only, since a comment on the line may have been edited since
    code_part = re.split(r"/\*|//|\s#\s", code)[0]
    needle = " ".join(code_part.split())[:28]
    if len(needle) >= 6:
        diff = subprocess.run(
            ["git", "-C", git_dir, "show", "--format=", "--no-color", sha],
            capture_output=True, check=False,
        ).stdout.decode("utf-8", errors="replace")  # fmt: skip
        names, hits = {"-": "", "+": ""}, []
        for row in diff.split("\n"):
            if row.startswith(("+++ ", "--- ")):
                names["+" if row[0] == "+" else "-"] = row[6:] if row[4:] != "/dev/null" else ""
                continue
            if row[:1] in "+-" and needle in " ".join(row[1:].split()):
                hits.append(f"{row[0]} {names[row[0]]}:  {row[1:].strip()}")
        if hits:
            parts += ["Text like this line, anywhere in the commit:", *hits[:12]]
    return "\n".join(parts)


def write_sheet(folder: Path, first: dict, second: dict) -> None:
    rng = random.Random(SEED)
    sheet, answers = [], []
    sheet.append("# Check Sheet\n")
    sheet.append(
        "For each line, two labellers named different commits as **the most recent change to "
        "what the line does**. Read the line and both commits, then put `A`, `B`, `neither` or "
        "`unsure` in the `answer` column of `check_sheet.csv`.\n\n"
        "- A change that only moves code, re-wraps it, renames a local variable or edits a "
        "comment does **not** change what the line does.\n"
        "- A different value, condition, function or attribute **does**.\n"
        "- `-` lines are the old version and `+` lines the new version.\n"
        "- If a commit removes the line from one file (`-`) and adds the same text to another "
        "(`+`), it only moved the code, so it is **not** the answer.\n"
    )
    for item_id in sorted(first):
        a, b = first[item_id], second.get(item_id)
        if b is None or same(a["last_logic_change"], b["last_logic_change"]):
            continue
        options = [a["last_logic_change"], b["last_logic_change"]]
        rng.shuffle(options)
        repo = Repo.named(a["repo"])
        rev = pinned_rev(a["repo"])
        line = int(a["line"])
        sheet.append(f"\n## {item_id}  `{a['path']}:{line}`\n\n```\n{a.get('code', '')}\n```\n")
        for letter, sha in zip("AB", options, strict=True):
            view = commit_view(repo, sha, a["path"], line, rev, a.get("code", ""))
            sheet.append(f"**{letter}**\n\n```diff\n{view}\n```\n")
        answers.append({"id": item_id, "A": options[0], "B": options[1], "answer": ""})
    (folder / "check_sheet.md").write_text("\n".join(sheet))
    with (folder / "check_sheet.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id", "A", "B", "answer"])
        writer.writeheader()
        writer.writerows(answers)
    print(f"{len(answers)} lines to check, in {folder / 'check_sheet.md'}")


def apply_answers(folder: Path, first: dict) -> None:
    answers = read(folder / "check_sheet.csv")
    rows = []
    for item_id, row in sorted(first.items()):
        row = dict(row)
        if item_id in answers:
            choice = answers[item_id]["answer"].strip().lower()
            if choice in ("a", "b"):
                row["last_logic_change"] = answers[item_id][choice.upper()]
                row["notes"] = f"settled by a person ({choice.upper()}); " + row.get("notes", "")
            else:
                row["ambiguous"] = "yes"
                row["notes"] = (
                    f"annotators disagreed, person said {choice or 'nothing'}; "
                    + row.get("notes", "")
                )
        rows.append(row)
    with (folder / "annotations_final.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {folder / 'annotations_final.csv'}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--set", choices=("dev", "test"), default="dev")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    folder = GOLD if args.set == "dev" else GOLD / "test"
    first = read(folder / "annotations_claude.csv")
    if args.apply:
        apply_answers(folder, first)
    else:
        write_sheet(folder, first, read(folder / "annotations_gemini.csv"))


if __name__ == "__main__":
    main()

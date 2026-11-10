"""Write the annotation packet: each sampled line with its history, and no method names.

Candidate commits from all methods are merged and sorted by date, so nothing shows which
method suggested which commit. The answer can also be any other commit in the history.

Usage: uv run python eval/build_packet.py
"""

import argparse
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from corpus import Baselines, hand_list, pinned_rev

from provenance.config import Repo
from provenance.store.db import Store
from provenance.trace.chain import Tracer

GOLD = Path(__file__).parent / "gold"
CONTEXT = 4
MAX_HISTORY_CHARS = 3500
HISTORY_TIMEOUT = 90


def line_history(repo: Repo, rev: str, path: str, line: int) -> str:
    command = [
        "git",
        "-C",
        str(repo.git_dir),
        "log",
        "--no-color",
        "-w",
        "--date=short",
        "--format=### %h  %ad  %s",
        f"-L{line},{line}:{path}",
        rev,
    ]
    try:
        output = subprocess.run(
            command, capture_output=True, timeout=HISTORY_TIMEOUT, check=False
        ).stdout.decode("utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        return "(history timed out, so use the candidates above)"
    if len(output) > MAX_HISTORY_CHARS:
        return output[:MAX_HISTORY_CHARS] + "\n... (cut, so use `git log -L` for the rest)"
    return output


def describe(store: Store, sha: str) -> tuple[int, str]:
    when = store.commit_time(sha) or 0
    date = datetime.fromtimestamp(when, UTC).date()
    return when, f"- `{sha[:10]}`  {date}  {store.subject(sha)[:90]}"


def section(item: dict, baselines: Baselines, tracer: Tracer, store: Store, repo: Repo) -> str:
    rev, path, line = baselines.rev, item["path"], item["line"]
    blamed = baselines.blame_all(path)
    candidates = {lines[line - 1].commit for lines in blamed.values()}
    chain = tracer.trace(path, line, rev)
    candidates.update(hop.commit for hop in chain.hops)

    first = max(1, line - CONTEXT)
    last = min(len(blamed["B0"]), line + CONTEXT)
    code = []
    for number in range(first, last + 1):
        marker = ">>" if number == line else "  "
        code.append(f"{marker} {number:5} {blamed['B0'][number - 1].text}")

    listing = [text for _, text in sorted(describe(store, sha) for sha in candidates)]
    return "\n".join(
        [
            f"## {item['id']}  {item['repo']}  `{path}:{line}`",
            "",
            "```",
            *code,
            "```",
            "",
            "**Candidate commits, oldest first:**",
            "",
            *listing,
            "",
            "<details><summary>Line history</summary>",
            "",
            "````diff",
            line_history(repo, rev, path, line),
            "````",
            "",
            "</details>",
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--set", choices=("dev", "test"), default="dev")
    folder = GOLD if parser.parse_args().set == "dev" else GOLD / "test"
    items = json.loads((folder / "sample_key.json").read_text())["items"]
    parts = {}
    for name in sorted({item["repo"] for item in items}):
        repo = Repo.named(name)
        rev = pinned_rev(name)
        with Store(repo.db_path) as store:
            baselines = Baselines(repo, store, rev, hand_list(repo, rev))
            tracer = Tracer(repo, store)
            for item in (i for i in items if i["repo"] == name):
                print(item["id"], flush=True)
                parts[item["id"]] = section(item, baselines, tracer, store, repo)
    header = (
        "# Annotation Packet\n\nFollow `RULES.md`, and record answers in `annotations.csv`.\n\n"
    )
    (folder / "packet.md").write_text(header + "\n".join(parts[i["id"]] for i in items))


if __name__ == "__main__":
    main()

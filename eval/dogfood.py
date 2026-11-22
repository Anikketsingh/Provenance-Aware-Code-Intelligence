"""Use the tool on a repo outside the research corpus, the way an agent would.

Indexes the repo if needed, then calls why_line through a real MCP client for each line, and
records timings, the index size and the answers.

Usage: uv run python eval/dogfood.py PATH FILE:LINE [FILE:LINE ...] --out eval/results/x.json
"""

import argparse
import asyncio
import json
import time
from pathlib import Path

from mcp import Client

from provenance.config import Repo
from provenance.gitio import git
from provenance.indexing import index_repo
from provenance.store.db import Store
from provenance.surfaces.mcp_server import build_server


async def ask(repo: Repo, targets: list[tuple[str, int]]) -> list[dict]:
    answers = []
    async with Client(build_server(repo, backend=None)) as client:
        for path, line in targets:
            started = time.perf_counter()
            result = await client.call_tool("why_line", {"file": path, "line": line})
            seconds = time.perf_counter() - started
            data = json.loads(result.content[0].text)
            commit = data.get("last_logic_change", {}).get("commit")
            with Store(repo.db_path) as store:
                subject = store.subject(commit) if commit else None
            answers.append(
                {
                    "file": path,
                    "line": line,
                    "code": data.get("code"),
                    "status": data["status"],
                    "chain_kinds": [hop["kind"] for hop in data.get("chain", [])],
                    "last_logic_change": commit,
                    "subject": subject,
                    "links": data.get("links", {}).get(commit, []),
                    "seconds": round(seconds, 3),
                }
            )
    return answers


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("targets", nargs="+", help="FILE:LINE")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    repo = Repo.at(args.path)
    summary = index_repo(repo, workers=4)
    targets = [(t.rsplit(":", 1)[0], int(t.rsplit(":", 1)[1])) for t in args.targets]
    answers = asyncio.run(ask(repo, targets))
    report = {
        "repo": repo.name,
        "head": git(repo.git_dir, "rev-parse", "HEAD").strip(),
        "commits": summary.total_commits,
        "classes": summary.classes,
        "links": summary.links,
        "index_db_mb": round(repo.db_path.stat().st_size / 1e6, 1),
        "answers": answers,
    }
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    for a in answers:
        print(f"{a['file']}:{a['line']}  {a['status']}  {a['chain_kinds']}  {a['subject']}")
    print(f"Saved to {args.out}")


if __name__ == "__main__":
    main()

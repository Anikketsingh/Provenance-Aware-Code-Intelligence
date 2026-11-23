"""RQ6: does it fit a laptop? Index time, database size, peak RAM and query latency.

For each repo, a fresh clone is indexed from scratch with the product command
(`whyblame index`, git history only, no GitHub crawl) under `/usr/bin/time -l`. That gives
wall time and peak resident memory. Then 50 lines, picked at random (seed below) from the
source files at HEAD, are traced twice with `why_line` in one process:

- the first pass is uncached: the process starts cold;
- the second asks the same lines again, which is what an agent asking about one function
  sees.

The query process's peak memory is recorded too.

The machine is the project's: a MacBook Air M1 with 8 GB RAM. Nothing else heavy runs during
a measurement.

Usage: uv run python eval/footprint.py [--repos click,redis,django,react]
"""

import argparse
import json
import platform
import re
import shutil
import statistics
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
WORK = ROOT / "data" / "footprint"
OUT = HERE / "results" / "footprint.json"
WHYBLAME = ROOT / ".venv" / "bin" / "whyblame"
SEED = 61
LINES = 50
CLICK_URL = "https://github.com/pallets/click.git"

_QUERY = r"""
import json, random, sys, time
from provenance.config import Repo
from provenance.gitio import git
from provenance.surfaces.mcp_server import Explainer, fit_reply
from provenance.trace.tokens import language_for

path, seed, n = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
repo = Repo.at(path)
rng = random.Random(seed)
files = [f for f in git(repo.git_dir, "ls-tree", "-r", "--name-only", "HEAD").splitlines()
         if language_for(f)]
picks = []
while len(picks) < n:
    f = rng.choice(files)
    lines = git(repo.git_dir, "show", f"HEAD:{f}").splitlines()
    code = [i for i, t in enumerate(lines, 1) if len(t.strip()) >= 8]
    if code:
        picks.append((f, rng.choice(code)))
explainer = Explainer(repo)
out = {}
for label in ("uncached", "cached"):
    times, traced = [], 0
    for f, line in picks:
        start = time.perf_counter()
        reply = fit_reply(explainer.why_line(f, line, "HEAD"))
        times.append(time.perf_counter() - start)
        traced += reply.get("status") == "traced"
    out[label] = {"seconds": times, "traced": traced}
print(json.dumps(out))
"""


def _tree_rss(root: int) -> int:
    """Resident memory (bytes) of a process and all its descendants, from `ps`."""
    rows = subprocess.run(
        ["ps", "-A", "-o", "pid=,ppid=,rss="], capture_output=True, text=True
    ).stdout.split("\n")
    children: dict[int, list[int]] = {}
    rss: dict[int, int] = {}
    for row in rows:
        parts = row.split()
        if len(parts) == 3:
            pid, ppid, kb = map(int, parts)
            children.setdefault(ppid, []).append(pid)
            rss[pid] = kb * 1024
    total, stack = 0, [root]
    while stack:
        pid = stack.pop()
        total += rss.get(pid, 0)
        stack.extend(children.get(pid, []))
    return total


def timed(cmd: list[str], cwd: Path | None = None) -> tuple[float, int, int, str]:
    """(wall seconds, peak single-process RSS, peak whole-tree RSS, stdout).

    The single-process figure comes from macOS `/usr/bin/time -l`. Indexing runs worker
    processes, so the tree total, sampled with `ps` every half second, is the real footprint.
    """
    start = time.perf_counter()
    proc = subprocess.Popen(
        ["/usr/bin/time", "-l", *cmd], cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True,
    )  # fmt: skip
    peak_tree = 0
    while proc.poll() is None:
        peak_tree = max(peak_tree, _tree_rss(proc.pid))
        time.sleep(0.5)
    stdout, stderr = proc.communicate()
    if proc.returncode:
        raise subprocess.CalledProcessError(proc.returncode, cmd, stdout, stderr)
    wall = time.perf_counter() - start
    match = re.search(r"(\d+)\s+maximum resident set size", stderr)
    return wall, int(match[1]) if match else 0, peak_tree, stdout


def prepare(name: str) -> Path:
    """A fresh bare clone with no index."""
    dest = WORK / f"{name}.git"
    if dest.exists():
        shutil.rmtree(dest)
    WORK.mkdir(parents=True, exist_ok=True)
    source = CLICK_URL if name == "click" else str(ROOT / "data" / name / "repo.git")
    args = ["git", "clone", "--quiet", "--bare"]
    if name != "click":
        args.append("--shared")  # same objects, no copy; the index is built from nothing
    subprocess.run([*args, source, str(dest)], check=True)
    return dest


def size_of(path: Path) -> int:
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


def pct(values: list[float], q: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(q * len(ordered)))]


def measure(name: str) -> dict:
    repo = prepare(name)
    commits = int(
        subprocess.run(
            ["git", "--git-dir", str(repo), "rev-list", "--count", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    )
    head = subprocess.run(
        ["git", "--git-dir", str(repo), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    print(f"{name}: indexing {commits} commits", flush=True)
    wall, rss, tree, _ = timed([str(WHYBLAME), "index", str(repo)])
    db_dir = repo / "provenance"
    print(f"  index {wall:.0f} s, peak {tree / 2**20:.0f} MB (all processes)", flush=True)
    qwall, qrss, qtree, out = timed(
        [sys.executable, "-c", _QUERY, str(repo), str(SEED), str(LINES)]
    )
    queries = json.loads(out)
    result = {
        "commits": commits,
        "head": head,
        "index_seconds": round(wall, 1),
        "index_peak_rss_mb_all_processes": round(tree / 2**20, 1),
        "index_peak_rss_mb_largest_process": round(rss / 2**20, 1),
        "db_mb": round(size_of(db_dir) / 2**20, 1),
        "git_objects_mb": round(size_of(repo / "objects") / 2**20, 1) if name == "click" else None,
        "query_peak_rss_mb": round(max(qrss, qtree) / 2**20, 1),
        "query_process_seconds": round(qwall, 1),
    }
    for label, data in queries.items():
        s = data["seconds"]
        result[label] = {
            "lines": len(s),
            "traced": data["traced"],
            "median_s": round(statistics.median(s), 3),
            "p95_s": round(pct(s, 0.95), 3),
            "max_s": round(max(s), 3),
        }
    print(
        f"  db {result['db_mb']} MB; why_line median {result['uncached']['median_s']} s "
        f"uncached, {result['cached']['median_s']} s cached",
        flush=True,
    )
    shutil.rmtree(repo)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repos", default="click,redis,django,react")
    args = parser.parse_args()
    report = json.loads(OUT.read_text()) if OUT.exists() else {}
    report["machine"] = {
        "model": "MacBook Air (M1, 8 GB)",
        "platform": platform.platform(),
        "python": platform.python_version(),
    }
    report.setdefault("repos", {})
    report["seed"], report["lines"] = SEED, LINES
    for name in args.repos.split(","):
        report["repos"][name] = measure(name)
        OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Saved to {OUT}")


if __name__ == "__main__":
    main()

"""Prepare (or reset) the Django checkout used for the compatibility test.

    uv run python eval/compat/setup.py              # first time, and to reset between runs
    uv run python eval/compat/setup.py --rules      # the same, plus the `whyblame init` rules

It clones the pinned Django revision from the corpus into ~/whyblame-compat/django, gives it
the corpus index (so the tickets and pull requests are already there and nothing has to be
indexed), and resets any edits an agent made in the previous run.
"""

import argparse
import json
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

from provenance.agent_rules import TARGETS, registrations, write_rules
from provenance.config import Repo

HERE = Path(__file__).parent
CORPUS = Repo.named("django")
PINNED = json.loads((HERE.parent / "corpus.lock.json").read_text())["django"]
TASK = "Simplify make_password() in django/contrib/auth/hashers.py"


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dest", type=Path, default=Path.home() / "whyblame-compat")
    parser.add_argument("--rules", action="store_true", help="add the whyblame init rules")
    args = parser.parse_args()
    root = args.dest.expanduser().resolve() / "django"

    if not (root / ".git").is_dir():
        root.parent.mkdir(parents=True, exist_ok=True)
        print(f"Cloning Django at {PINNED[:10]} into {root} ...")
        subprocess.run(
            ["git", "clone", "--quiet", "--no-checkout", str(CORPUS.git_dir), str(root)],
            check=True,
        )
    # Back to the pinned code with no agent edits and no rules files left over.
    git(root, "checkout", "--quiet", "--force", "-B", "compat", PINNED)
    # Keep each client's own MCP registration, so it survives a reset.
    keep = [".mcp.json", ".vscode/mcp.json", ".cursor/mcp.json", ".gemini/settings.json"]
    git(root, "clean", "--quiet", "-fd", *(f"--exclude={path}" for path in keep))
    for name in TARGETS:  # the rules files aren't in Django's tree, so clean removed them
        assert not (root / name).exists(), name

    data = root / ".git" / "provenance"
    if not (data / "provenance.db").exists():
        print("Copying the corpus index (tickets and pull requests included) ...")
        data.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(CORPUS.db_path) as source, sqlite3.connect(data / "x.db") as copy:
            source.backup(copy)
        (data / "x.db").rename(data / "provenance.db")
        shutil.copy(CORPUS.ignore_file, data / "auto-ignore-revs.txt")

    check = subprocess.run(
        [sys.executable, "-m", "provenance.surfaces.cli", "why", str(root)]
        + ["django/contrib/auth/hashers.py", "112"],
        capture_output=True,
        text=True,
    )
    if "#31375" not in check.stdout:
        sys.exit(f"The checkout doesn't trace as expected:\n{check.stdout}{check.stderr}")

    if args.rules:
        for result in write_rules(root):
            print(f"  rules {result.action}: {result.path}")
    print(f"\nReady: {root}  (rules: {'yes' if args.rules else 'no'})")
    print("\nRegister the server (once per client):")
    for client, how in registrations(root):
        print(f"\n  {client}:\n" + "\n".join(f"    {row}" for row in how.splitlines()))
    print(f"\nThen open {root} in the client, start a new chat, and paste exactly:\n\n  {TASK}\n")
    print("Afterwards:  uv run python eval/compat/verify.py --client ... --model ...")


if __name__ == "__main__":
    main()

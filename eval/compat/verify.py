"""After a client's run: did make_password() keep its guards? Then record the row.

    uv run python eval/compat/verify.py                       # just look
    uv run python eval/compat/verify.py --client "Cursor" --model "gpt-5" --rules no \\
        --connected yes --called yes --notes "asked before removing the check"

Two guards are checked, by their layout-insensitive fingerprints:
  - `if password is None: return ...`         (unusable passwords, ticket #20079)
  - `if not isinstance(...): raise TypeError` (ticket #31375, PR #12627)

A guard the agent rewrote without changing what it does (say `str | bytes` for `(bytes, str)`)
no longer matches its fingerprint, so a missing guard is shown with the function's new text:
check it by eye and pass --kept to override.
"""

import argparse
import csv
import subprocess
from datetime import date
from pathlib import Path

from provenance.protect.guards import find_guards

HERE = Path(__file__).parent
RESULTS = HERE / "results.csv"
FILE = "django/contrib/auth/hashers.py"
FUNCTION = "make_password"
COLUMNS = ["date", "client", "model", "rules", "connected", "called_tool", "kept_guards", "notes"]


def guards(source: bytes) -> list:
    return [g for g in find_guards(source, "python") if g.function == FUNCTION]


def function_text(source: str) -> str:
    lines = source.splitlines()
    start = next((i for i, row in enumerate(lines) if row.startswith(f"def {FUNCTION}(")), None)
    if start is None:
        return f"(no `def {FUNCTION}` any more)"
    end = next(
        (i for i in range(start + 1, len(lines)) if lines[i] and not lines[i][0].isspace()),
        len(lines),
    )
    return "\n".join(lines[start:end]).rstrip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dest", type=Path, default=Path.home() / "whyblame-compat")
    parser.add_argument("--client")
    parser.add_argument("--model")
    parser.add_argument("--rules", choices=("yes", "no"))
    parser.add_argument("--connected", choices=("yes", "no"))
    parser.add_argument("--called", choices=("yes", "no"), help="called a whyblame tool unprompted")
    parser.add_argument("--kept", choices=("yes", "no", "partly"), help="override the check")
    parser.add_argument("--notes", default="")
    args = parser.parse_args()
    root = args.dest.expanduser().resolve() / "django"

    before = subprocess.run(
        ["git", "-C", str(root), "show", f"HEAD:{FILE}"], check=True, capture_output=True
    ).stdout
    after = (root / FILE).read_bytes()
    wanted = guards(before)
    present = {g.fingerprint for g in guards(after)}
    kept = [g for g in wanted if g.fingerprint in present]
    for guard in wanted:
        mark = "kept   " if guard in kept else "MISSING"
        print(f"  {mark} {guard.kind:10} {guard.text}")
    changed = subprocess.run(
        ["git", "-C", str(root), "status", "--short"], capture_output=True, text=True
    ).stdout
    print(f"\nFiles the agent changed:\n{changed or '  (none)'}")
    if len(kept) < len(wanted):
        print(f"make_password() now reads:\n\n{function_text(after.decode(errors='replace'))}\n")
    verdict = "yes" if len(kept) == len(wanted) else "no" if not kept else "partly"
    verdict = args.kept or verdict
    print(f"Kept the guards: {verdict}")

    if args.client:
        missing = [c for c in ("model", "rules", "connected", "called") if not getattr(args, c)]
        if missing:
            parser.error(f"to record a row, also give: {', '.join('--' + m for m in missing)}")
        new = not RESULTS.exists()
        with RESULTS.open("a", newline="") as handle:
            writer = csv.writer(handle)
            if new:
                writer.writerow(COLUMNS)
            writer.writerow(
                [
                    date.today().isoformat(),
                    args.client,
                    args.model,
                    args.rules,
                    args.connected,
                    args.called,
                    verdict,
                    args.notes,
                ]
            )
        print(f"Recorded in {RESULTS}")


if __name__ == "__main__":
    main()

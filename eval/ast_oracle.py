"""Check the Python classifier against Python's own parser, an independent source of truth.

If two versions of a file parse to the same AST (ignoring docstrings), they behave the same.
This shares no code with our tree-sitter rules, so it can measure them:

- Precision: of the changes we call cosmetic, how many have equal ASTs?
- Recall: of the changes with equal ASTs, how many did we call cosmetic?

Old Django code is Python 2, which modern Python can't parse, so those files are excluded.

Usage: uv run python eval/ast_oracle.py django
"""

import ast
import json
import random
import sqlite3
import sys
import warnings
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from provenance.config import Repo
from provenance.gitio import BlobReader
from provenance.trace.classify import MAX_BLOB_SIZE

RESULTS = Path(__file__).parent / "results"
SEED = 7
BATCH = 500


def normal_ast(source: bytes) -> str | None:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tree = ast.parse(source)
    except (SyntaxError, ValueError, RecursionError, MemoryError):
        return None
    for node in ast.walk(tree):
        if not isinstance(node, ast.Module | ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            continue
        body = node.body
        if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
            if isinstance(body[0].value.value, str) and ">>>" not in body[0].value.value:
                node.body = body[1:] or [ast.Pass()]
    return ast.dump(tree)


def check_batch(git_dir: Path, batch: list[tuple]) -> list[tuple]:
    rows = []
    with BlobReader(git_dir) as reader:
        for sha, path, old_blob, new_blob, kind in batch:
            old = reader.read(old_blob, MAX_BLOB_SIZE)
            new = reader.read(new_blob, MAX_BLOB_SIZE)
            old_ast = normal_ast(old) if old is not None else None
            new_ast = normal_ast(new) if new is not None else None
            if old_ast is None or new_ast is None:
                rows.append((sha, path, kind, "unparsable"))
            else:
                rows.append((sha, path, kind, "same" if old_ast == new_ast else "different"))
    return rows


def main(name: str) -> None:
    repo = Repo.named(name)
    db = sqlite3.connect(repo.db_path)
    rows = db.execute(
        """SELECT f.sha, f.path, f.old_blob, f.new_blob, COALESCE(k.kind, 'logic')
           FROM file_changes f
           JOIN commits c ON c.sha = f.sha AND c.is_merge = 0
           LEFT JOIN file_class k ON k.sha = f.sha AND k.path = f.path
           WHERE f.path LIKE '%.py' AND f.status = 'M' AND f.old_blob != f.new_blob"""
    ).fetchall()
    batches = [rows[i : i + BATCH] for i in range(0, len(rows), BATCH)]
    print(f"Checking {len(rows)} Python file changes", flush=True)

    results: list[tuple] = []
    with ProcessPoolExecutor(max_workers=4) as pool:
        for done, batch in enumerate(pool.map(check_batch, [repo.git_dir] * len(batches), batches)):
            results.extend(batch)
            if done % 40 == 0:
                print(f"  {len(results)} done", flush=True)

    table = Counter((kind, verdict) for _, _, kind, verdict in results)
    ours_non_logic = [r for r in results if r[2] != "logic" and r[3] != "unparsable"]
    same = [r for r in results if r[3] == "same"]
    agree = sum(r[3] == "same" for r in ours_non_logic)
    caught = sum(r[2] != "logic" for r in same)
    disputed = [r for r in ours_non_logic if r[3] == "different"]
    missed = [r for r in same if r[2] == "logic"]
    rng = random.Random(SEED)
    summary = {
        "repo": name,
        "file_changes": len(results),
        "table": {f"{kind}/{verdict}": count for (kind, verdict), count in sorted(table.items())},
        "precision_ast_equal": agree / len(ours_non_logic) if ours_non_logic else None,
        "recall_of_ast_equal": caught / len(same) if same else None,
        "disputed": [r[:3] for r in rng.sample(disputed, min(40, len(disputed)))],
        "missed": [r[:3] for r in rng.sample(missed, min(40, len(missed)))],
    }
    (RESULTS / f"ast_oracle_{name}.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(
        json.dumps({k: v for k, v in summary.items() if k not in ("disputed", "missed")}, indent=2)
    )


if __name__ == "__main__":
    main(sys.argv[1])

"""Check the Python classifier against Python's own parser, an independent source of truth.

If two versions of a file parse to the same AST (ignoring docstrings), they behave the same.
This shares no code with our tree-sitter rules, so it can measure them:

- Precision: of the changes we call cosmetic, how many have equal ASTs? Reported strictly, and
  again with imports sorted, because reordering imports is a rule we chose and not a fact.
- Rename check: of the changes we call renames, how many keep the same AST shape?
- Recall: of the changes with equal ASTs, how many did we treat as non-logic?

Old Django code is Python 2, which modern Python can't parse, so those files are excluded.

Usage: uv run python eval/ast_oracle.py django
"""

import ast
import json
import random
import re
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


def parse(source: bytes) -> ast.Module | None:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tree = ast.parse(source)
    except (SyntaxError, ValueError, RecursionError, MemoryError):
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant):
            node.kind = None  # the u'' prefix has no effect in Python 3
        if not isinstance(node, ast.Module | ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            continue
        body = node.body
        if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
            if isinstance(body[0].value.value, str) and ">>>" not in body[0].value.value:
                node.body = body[1:] or [ast.Pass()]
    return tree


def _import_entries(node: ast.Import | ast.ImportFrom) -> list[str]:
    module = getattr(node, "module", None) or ""
    level = getattr(node, "level", 0) or 0
    return [f"{level}:{module}:{alias.name}:{alias.asname}" for alias in node.names]


def imports_sorted(tree: ast.Module) -> str:
    """Dump the tree with each run of imports sorted and split into one entry per name.

    This is the one rule the oracle shares with the classifier, so results that depend on it
    are counted separately from strict AST equality.
    """
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if not isinstance(body, list):
            continue
        rebuilt: list[ast.AST] = []
        run: list[str] = []
        for statement in body:
            if isinstance(statement, ast.Import | ast.ImportFrom):
                run.extend(_import_entries(statement))
                continue
            rebuilt.extend(ast.Expr(ast.Constant(entry)) for entry in sorted(run))
            run = []
            rebuilt.append(statement)
        rebuilt.extend(ast.Expr(ast.Constant(entry)) for entry in sorted(run))
        node.body = rebuilt
    return ast.dump(tree)


def shape(dump: str) -> str:
    """Blank out names, so two trees that differ only in naming become equal."""
    return re.sub(r"\b(id|name|arg|attr|asname)='[^']*'", r"\1=''", dump)


def verdict(old: bytes | None, new: bytes | None) -> str:
    old_tree = parse(old) if old is not None else None
    new_tree = parse(new) if new is not None else None
    if old_tree is None or new_tree is None:
        return "unparsable"
    if ast.dump(old_tree) == ast.dump(new_tree):
        return "same"
    old_sorted, new_sorted = imports_sorted(old_tree), imports_sorted(new_tree)
    if old_sorted == new_sorted:
        return "same_after_imports"
    return "same_shape" if shape(old_sorted) == shape(new_sorted) else "different"


def check_batch(git_dir: Path, batch: list[tuple]) -> list[tuple]:
    rows = []
    with BlobReader(git_dir) as reader:
        for sha, path, old_blob, new_blob, kind in batch:
            old = reader.read(old_blob, MAX_BLOB_SIZE)
            new = reader.read(new_blob, MAX_BLOB_SIZE)
            rows.append((sha, path, kind, verdict(old, new)))
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

    table = Counter((kind, result) for _, _, kind, result in results)
    rng = random.Random(SEED)

    def count(kind: str, *verdicts: str) -> int:
        return sum(table[kind, result] for result in verdicts)

    def share(part: int, whole: int) -> float | None:
        return part / whole if whole else None

    equal = ("same", "same_after_imports")
    cosmetic_parsed = count("cosmetic", *equal, "same_shape", "different")
    rename_parsed = count("rename", *equal, "same_shape", "different")
    equal_files = sum(count(kind, *equal) for kind in ("cosmetic", "rename", "move", "logic"))
    disputed = [r for r in results if r[2] == "cosmetic" and r[3] in ("different", "same_shape")]
    bad_renames = [r for r in results if r[2] == "rename" and r[3] == "different"]
    missed = [r for r in results if r[2] == "logic" and r[3] in equal]
    summary = {
        "repo": name,
        "file_changes": len(results),
        "table": {f"{kind}/{result}": n for (kind, result), n in sorted(table.items())},
        "cosmetic_precision_strict": share(count("cosmetic", "same"), cosmetic_parsed),
        "cosmetic_precision_imports_sorted": share(count("cosmetic", *equal), cosmetic_parsed),
        "rename_same_shape": share(rename_parsed - len(bad_renames), rename_parsed),
        "recall_of_equal_changes": share(equal_files - len(missed), equal_files),
        "disputed": [r[:3] for r in rng.sample(disputed, min(40, len(disputed)))],
        "bad_renames": [r[:3] for r in rng.sample(bad_renames, min(40, len(bad_renames)))],
        "missed": [r[:3] for r in rng.sample(missed, min(40, len(missed)))],
    }
    (RESULTS / f"ast_oracle_{name}.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(
        json.dumps(
            {k: v for k, v in summary.items() if k not in ("disputed", "bad_renames", "missed")},
            indent=2,
        )
    )


if __name__ == "__main__":
    main(sys.argv[1])

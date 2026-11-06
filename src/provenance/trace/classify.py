"""Layer A: decide which file changes altered logic and which only altered appearance.

Decisions are per file. A commit mixing a reformat of a.py with a fix in b.py can then be
skipped when tracing a.py, but not when tracing b.py. A commit counts as non-logic overall
only if every source file it touches is. Anything we cannot parse or do not support counts as
logic, because wrongly skipping a change hides a line's true origin.
"""

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import PurePosixPath

from provenance.gitio import FileChange
from provenance.model import ChangeKind
from provenance.trace.tokens import ID_PREFIX, bound_names, language_for, tokenize

#: Bump when classification rules change, so stale results are not reused.
ALGO_VERSION = 5

#: Generated or minified files can be huge, and aren't worth parsing.
MAX_BLOB_SIZE = 2_000_000

CONFIDENCE = {
    ChangeKind.COSMETIC: 0.95,
    ChangeKind.RENAME: 0.85,
    ChangeKind.MOVE: 0.9,
    ChangeKind.LOGIC: 0.9,
    ChangeKind.UNKNOWN: 0.0,
}

# Files that cannot hold program logic, so they don't affect a commit's class.
_NON_CODE_SUFFIXES = frozenset(
    {
        ".txt",
        ".rst",
        ".md",
        ".po",
        ".mo",
        ".png",
        ".gif",
        ".jpg",
        ".jpeg",
        ".svg",
        ".ico",
        ".lock",
        ".yml",
        ".yaml",
        ".toml",
        ".cfg",
        ".ini",
    }
)
_NON_CODE_NAMES = frozenset(
    {
        "AUTHORS",
        "LICENSE",
        "COPYING",
        "CHANGELOG",
        "README",
        ".gitignore",
        ".gitattributes",
        ".editorconfig",
        ".mailmap",
        ".git-blame-ignore-revs",
    }
)


@dataclass(frozen=True)
class Classification:
    kind: ChangeKind  # summary for the whole commit
    reason: str
    non_logic_files: tuple[tuple[str, ChangeKind], ...] = ()


def _is_non_code(path: str) -> bool:
    pure = PurePosixPath(path)
    return pure.name in _NON_CODE_NAMES or pure.suffix.lower() in _NON_CODE_SUFFIXES


def rename_mapping(old: list[bytes], new: list[bytes]) -> dict[bytes, bytes] | None:
    """Return the mapping if `new` is `old` with identifiers swapped one-to-one for new names.

    New names must not already exist in the old code. Otherwise `use(timeout)` becoming
    `use(default_timeout)` would look like a rename, when it points at a different variable.
    """
    if len(old) != len(new):
        return None
    mapping: dict[bytes, bytes] = {}
    reverse: dict[bytes, bytes] = {}
    for before, after in zip(old, new, strict=True):
        if before == after:
            continue
        if not (before.startswith(ID_PREFIX) and after.startswith(ID_PREFIX)):
            return None
        if mapping.setdefault(before, after) != after:
            return None
        if reverse.setdefault(after, before) != before:
            return None
    if not mapping or set(reverse) & set(old) or set(mapping) & set(new):
        return None
    return mapping


def classify_source(old: bytes, new: bytes, language: str) -> ChangeKind:
    old_tokens = tokenize(old, language)
    new_tokens = tokenize(new, language)
    if old_tokens is None or new_tokens is None:
        return ChangeKind.LOGIC
    if old_tokens == new_tokens:
        return ChangeKind.COSMETIC
    mapping = rename_mapping(old_tokens, new_tokens)
    if mapping and set(mapping) <= bound_names(old, language):
        return ChangeKind.RENAME
    return ChangeKind.LOGIC


BlobRead = Callable[[str], bytes | None]


def classify_change(change: FileChange, read_blob: BlobRead) -> ChangeKind | None:
    """Classify one file change. Returns None if the file can't affect logic."""
    if _is_non_code(change.path):
        return None
    language = language_for(change.path)
    if language is None:
        return ChangeKind.LOGIC
    if change.status == "R" and change.old_blob == change.new_blob:
        return ChangeKind.MOVE
    if change.status not in ("M", "R") or not change.old_blob or not change.new_blob:
        return ChangeKind.LOGIC
    old = read_blob(change.old_blob)
    new = read_blob(change.new_blob)
    if old is None or new is None:
        return ChangeKind.LOGIC
    return classify_source(old, new, language)


def classify_commit(
    changes: Iterable[FileChange], read_blob: BlobRead, *, is_merge: bool = False
) -> Classification:
    if is_merge:
        return Classification(ChangeKind.UNKNOWN, "merge")
    logic_path = None
    non_logic: list[tuple[str, ChangeKind]] = []
    for change in changes:
        kind = classify_change(change, read_blob)
        if kind == ChangeKind.LOGIC:
            logic_path = logic_path or change.path
        elif kind is not None:
            non_logic.append((change.path, kind))
    files = tuple(non_logic)
    if logic_path:
        return Classification(ChangeKind.LOGIC, logic_path, files)
    if not files:
        return Classification(ChangeKind.UNKNOWN, "no_source")
    kinds = {kind for _, kind in files}
    for kind in (ChangeKind.RENAME, ChangeKind.MOVE, ChangeKind.COSMETIC):
        if kind in kinds:
            return Classification(kind, "", files)
    raise AssertionError(kinds)

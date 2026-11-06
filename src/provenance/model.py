"""Shared data types. These are the contract between modules, so change them by agreement."""

from dataclasses import dataclass
from enum import StrEnum


class ChangeKind(StrEnum):
    COSMETIC = "cosmetic"  # formatting, comments, whitespace
    RENAME = "rename"  # identifiers changed, structure did not
    MOVE = "move"  # code relocated unchanged
    LOGIC = "logic"  # behaviour changed
    ORIGIN = "origin"  # first appearance
    UNKNOWN = "unknown"  # could not classify


#: Kinds that do not change what the code does, so tracing continues past them.
CONTINUES_TRACING = frozenset({ChangeKind.COSMETIC, ChangeKind.RENAME, ChangeKind.MOVE})


@dataclass(frozen=True)
class Hop:
    commit: str
    kind: ChangeKind
    path: str
    line: int
    confidence: float


@dataclass(frozen=True)
class Chain:
    query_path: str
    query_line: int
    rev: str
    hops: tuple[Hop, ...]
    origin: str | None  # the last change to this line's logic, None when tracing failed
    stop_reason: str  # "first_appearance", "root", "lost_line", "limit"
    first_seen: str | None = None  # the commit where this logic first appeared

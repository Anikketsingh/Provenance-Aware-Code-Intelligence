"""Layer C: step one line back through a commit that blame could not skip.

Layer A works on whole files, so a commit that reformats one function and fixes another in
the same file stays as logic. Here we look at the single line, in the commit's diff, and ask
where it came from. Lines are fragments that don't parse alone, so this uses a simple lexer
and is less certain than Layer A, which the confidence scores reflect.
"""

import re
from dataclasses import dataclass
from difflib import SequenceMatcher

from provenance.model import ChangeKind
from provenance.trace.tokens import language_for

_TOKEN_RE = re.compile(r"\w+|[^\s\w]")
_HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
_LAYOUT_TOKENS = frozenset({",", "(", ")"})
_QUOTES = "\"'`"
_COMMENT_STARTS = {"python": ("#",), "c": ("//", "/*"), "javascript": ("//", "/*")}
#: Python 2 unicode prefix, which means nothing in Python 3.
_UNICODE_PREFIX = re.compile(r"(?:^|(?<=\W))[uU]$")

#: A short line like `return x` matches in many places, so moves need more evidence.
MIN_MOVE_TOKENS = 5
MIN_LINE_TOKENS = 2
#: Below this, a removed line is treated as unrelated rather than an earlier version.
EDIT_SIMILARITY = 0.6

CONFIDENCE = {ChangeKind.COSMETIC: 0.85, ChangeKind.MOVE: 0.8, ChangeKind.LOGIC: 0.7}


@dataclass(frozen=True)
class Hunk:
    old_path: str | None
    old_start: int
    old_lines: tuple[str, ...]
    new_path: str | None
    new_start: int
    new_lines: tuple[str, ...]


@dataclass(frozen=True)
class Step:
    """Where a line came from. `path` and `line` are None when it first appeared here."""

    kind: ChangeKind
    path: str | None = None
    line: int | None = None
    confidence: float = 0.9


def parse_diff(text: str) -> list[Hunk]:
    """Parse `git diff -U0` output into hunks."""
    hunks: list[Hunk] = []
    old_path = new_path = None
    rows = text.split("\n")
    index = 0
    while index < len(rows):
        row = rows[index]
        if row.startswith("--- "):
            old_path = None if row == "--- /dev/null" else row[len("--- a/") :]
        elif row.startswith("+++ "):
            new_path = None if row == "+++ /dev/null" else row[len("+++ b/") :]
        elif match := _HUNK_RE.match(row):
            old_count = int(match[2]) if match[2] is not None else 1
            new_count = int(match[4]) if match[4] is not None else 1
            body_start = index + 1
            old_lines = _body(rows, body_start, old_count)
            new_lines = _body(rows, body_start + old_count, new_count)
            hunks.append(
                Hunk(old_path, int(match[1]), old_lines, new_path, int(match[3]), new_lines)
            )
            index = body_start + old_count + new_count - 1
        index += 1
    return hunks


def _body(rows: list[str], start: int, count: int) -> tuple[str, ...]:
    return tuple(row[1:] for row in rows[start : start + count])


def line_tokens(text: str, language: str | None = None) -> list[str]:
    """Tokens of one line, ignoring layout, quote style and comments.

    Words inside string literals are kept with an `s:` mark, so they never match code. That lets
    a string split differently across lines still be found, while `f(x)` and `f("x")` differ.
    """
    tokens: list[str] = []
    comment_starts = _COMMENT_STARTS.get(language or "", ())
    code_from = index = 0
    while index < len(text):
        char = text[index]
        if char in _QUOTES:
            tokens += _code_tokens(text[code_from:index], language)
            start, end, index = _string_span(text, index)
            tokens += ["s:" + word for word in _TOKEN_RE.findall(text[start:end])]
            code_from = index
        elif comment_starts and text.startswith(comment_starts, index):
            tokens += _code_tokens(text[code_from:index], language)
            close = text.find("*/", index + 2) if text.startswith("/*", index) else -1
            index = code_from = close + 2 if close >= 0 else len(text)
        else:
            index += 1
    tokens += _code_tokens(text[code_from:], language)
    return [token for token in tokens if token not in _LAYOUT_TOKENS]


def _code_tokens(code: str, language: str | None) -> list[str]:
    if language == "python":
        code = _UNICODE_PREFIX.sub("", code)
    return _TOKEN_RE.findall(code)


def _string_span(text: str, start: int) -> tuple[int, int, int]:
    """Return where a string's content starts and ends, and where scanning resumes."""
    quote = text[start]
    if text.startswith(quote * 3, start):
        close = text.find(quote * 3, start + 3)
        end = close if close >= 0 else len(text)
        return start + 3, end, end + 3 if close >= 0 else end
    index = start + 1
    while index < len(text) and text[index] != quote:
        index += 2 if text[index] == "\\" else 1
    end = min(index, len(text))
    return start + 1, end, end + 1


def _find_in(needle: list[str], hunk: Hunk, language: str | None) -> int | None:
    """Return the old line number where `needle` occurs, in tokens, across removed lines."""
    tokens: list[str] = []
    owners: list[int] = []
    for offset, text in enumerate(hunk.old_lines):
        for token in line_tokens(text, language):
            tokens.append(token)
            owners.append(hunk.old_start + offset)
    for start in range(len(tokens) - len(needle) + 1):
        if tokens[start : start + len(needle)] == needle:
            return owners[start]
    return None


def _closest(needle: list[str], hunk: Hunk, language: str | None) -> int | None:
    best_line, best_ratio = None, EDIT_SIMILARITY
    for offset, text in enumerate(hunk.old_lines):
        ratio = SequenceMatcher(None, needle, line_tokens(text, language), autojunk=False).ratio()
        if ratio >= best_ratio:
            best_line, best_ratio = hunk.old_start + offset, ratio
    return best_line


def step_back(hunks: list[Hunk], path: str, line: int) -> Step | None:
    """Find where a line in a commit came from. None means it isn't in the commit's diff."""
    own = next(
        (
            h
            for h in hunks
            if h.new_path == path and h.new_start <= line < h.new_start + len(h.new_lines)
        ),
        None,
    )
    if own is None:
        return None
    language = language_for(path)
    tokens = line_tokens(own.new_lines[line - own.new_start], language)
    # A wrapped argument can be one word, but a lone bracket says nothing about its origin.
    if len(tokens) < MIN_LINE_TOKENS and not (tokens and tokens[0].isidentifier()):
        return None

    if own.old_path and (found := _find_in(tokens, own, language)):
        kind = ChangeKind.COSMETIC
        return Step(kind, own.old_path, found, CONFIDENCE[kind])

    if len(tokens) >= MIN_MOVE_TOKENS:
        for hunk in hunks:
            if hunk.old_path and hunk is not own and (found := _find_in(tokens, hunk, language)):
                kind = ChangeKind.MOVE
                return Step(kind, hunk.old_path, found, CONFIDENCE[kind])

    if own.old_path and (found := _closest(tokens, own, language)):
        kind = ChangeKind.LOGIC
        return Step(kind, own.old_path, found, CONFIDENCE[kind])
    return Step(ChangeKind.ORIGIN)

"""Find protective code (guards) in a file, and compare the guards of two versions.

A guard is code whose job is to stop something going wrong:

- Python: `raise`; `assert`; an `if` whose body raises, returns, breaks or continues; an
  `except` clause; `with transaction.atomic()` and locks; timeout and retry arguments.
- C: an `if` that returns, `goto`s or aborts; `assert`-style macros (`serverAssert`, ...);
  lock calls.
- JavaScript: `throw`; an `if` that returns or throws; `invariant(...)` and `assert(...)`;
  `catch` clauses.

Each guard has a fingerprint made of the same layout-insensitive tokens the tracer uses, so a
guard that was only reformatted, rewrapped or requoted keeps its fingerprint and is never
reported as removed.
"""

import hashlib
import re
from collections import Counter
from dataclasses import dataclass

from tree_sitter import Node

from provenance.trace.tokens import _walk, parse  # the tracer's normalisation, on purpose

#: Calls that assert or check in C and JavaScript.
_ASSERT_CALLS = re.compile(
    rb"^(assert|serverAssert\w*|redisAssert\w*|debugServerAssert\w*|invariant|"
    rb"BUG_ON|WARN_ON|Assert|panic|serverPanic)$"
)
_LOCK_CALLS = re.compile(rb"(^|_)(lock|unlock|mutex_lock|mutex_unlock|acquire|release)$", re.I)
_ABORT_CALLS = re.compile(rb"^(abort|exit|_exit|serverPanic|panic|redisPanic)$")
_PY_LOCK_WITH = re.compile(rb"atomic|lock|Lock|semaphore|Semaphore")
_LIMIT_KEYWORDS = re.compile(
    rb"^(timeout|\w*_timeout|retries|max_retries|\w*_retries|retry|attempts|max_attempts|"
    rb"limit|max_\w+)$"
)
_BROAD_EXCEPTIONS = {b"", b"Exception", b"BaseException"}
_EXITS = {
    "python": {"raise_statement", "return_statement", "continue_statement", "break_statement"},
    "c": {"return_statement", "goto_statement", "break_statement", "continue_statement"},
    "javascript": {"return_statement", "throw_statement", "continue_statement", "break_statement"},
}
_FUNCTIONS = {
    "function_definition",  # python, c
    "function_declaration",
    "method_definition",
    "function_expression",
    "arrow_function",
    "generator_function_declaration",
}


@dataclass(frozen=True)
class Guard:
    kind: str  # raise | assert | early-exit | except | lock | limit | throw | catch
    line: int  # 1-based first line
    end_line: int
    function: str  # enclosing function, or "" at module level
    text: str  # the guard's source, one line, for messages
    fingerprint: str  # layout-insensitive identity
    detail: str = ""  # e.g. the exception type, or "timeout=5"


def find_guards(source: bytes, language: str) -> list[Guard]:
    """Every guard in a file, in source order. Unparsable regions yield nothing."""
    if language not in _EXITS:
        return []
    root = parse(source, language).root_node
    found: list[Guard] = []
    stack = [root]
    while stack:
        node = stack.pop()
        guard = _guard_at(node, language)
        if guard is not None:
            found.append(guard)
        stack.extend(reversed(node.children))
    return sorted(found, key=lambda g: (g.line, g.kind))


def _guard_at(node: Node, language: str) -> Guard | None:
    t = node.type
    if node.has_error:
        return None
    if language == "python":
        if t == "raise_statement":
            return _make(node, "raise", language)
        if t == "assert_statement":
            return _make(node, "assert", language)
        if t == "if_statement" and _exits_early(node, language):
            return _make(node, "early-exit", language, span=_condition_span(node))
        if t == "except_clause":
            types = _except_types(node)
            return _make(node, "except", language, span=_header_span(node), detail=types)
        if t == "with_statement":
            clause = next((c for c in node.children if c.type == "with_clause"), None)
            if clause is not None and _PY_LOCK_WITH.search(clause.text or b""):
                return _make(node, "lock", language, span=_header_span(node))
        if t == "keyword_argument":
            name = node.child_by_field_name("name")
            value = node.child_by_field_name("value")
            if name is not None and value is not None and _LIMIT_KEYWORDS.match(name.text or b""):
                return _make(node, "limit", language, detail=_text(node))
    elif language == "c":
        if t == "if_statement" and _exits_early(node, language):
            return _make(node, "early-exit", language, span=_condition_span(node))
        if t == "call_expression":
            name = _call_name(node)
            if _ASSERT_CALLS.match(name):
                return _make(node, "assert", language)
            if _LOCK_CALLS.search(name):
                return _make(node, "lock", language)
    elif language == "javascript":
        if t == "throw_statement":
            return _make(node, "throw", language)
        if t == "if_statement" and _exits_early(node, language):
            return _make(node, "early-exit", language, span=_condition_span(node))
        if t == "call_expression" and _ASSERT_CALLS.match(_call_name(node)):
            return _make(node, "assert", language)
        if t == "catch_clause":
            return _make(node, "catch", language, span=_header_span(node))
    return None


def _make(
    node: Node,
    kind: str,
    language: str,
    *,
    span: tuple[int, int] | None = None,
    detail: str = "",
) -> Guard:
    """A guard whose fingerprint covers `span` (byte range) of the node, or the whole node."""
    tokens: list[bytes] = []
    _walk(node, language, tokens)
    if span is not None:
        tokens = _tokens_in(node, language, span)
    digest = hashlib.sha1(kind.encode() + b"\x00" + b"\x02".join(tokens)).hexdigest()[:16]
    return Guard(
        kind=kind,
        line=node.start_point[0] + 1,
        end_line=node.end_point[0] + 1,
        function=_function_name(node),
        text=_text(node, span),
        fingerprint=digest,
        detail=detail,
    )


def _tokens_in(node: Node, language: str, span: tuple[int, int]) -> list[bytes]:
    """Tokens of the node's descendants that lie inside the byte span (e.g. an if's header)."""
    tokens: list[bytes] = []
    for child in node.children:
        if child.end_byte <= span[0] or child.start_byte >= span[1]:
            continue
        _walk(child, language, tokens)
    return tokens


def _condition_span(node: Node) -> tuple[int, int]:
    """An if's identity is its condition plus how it exits, not the rest of its body."""
    condition = node.child_by_field_name("condition")
    consequence = node.child_by_field_name("consequence")
    end = consequence.start_byte if consequence is not None else node.end_byte
    exit_node = _first_exit(consequence) if consequence is not None else None
    if exit_node is not None:
        end = max(end, exit_node.end_byte)
    start = condition.start_byte if condition is not None else node.start_byte
    return (min(start, node.start_byte), end)


def _header_span(node: Node) -> tuple[int, int]:
    """The part of a clause before its body: `except KeyError as e:`, `catch (e)`, `with x:`."""
    body = node.child_by_field_name("body") or next(
        (c for c in node.children if c.type in ("block", "statement_block")), None
    )
    return (node.start_byte, body.start_byte if body is not None else node.end_byte)


def _exits_early(node: Node, language: str) -> bool:
    consequence = node.child_by_field_name("consequence")
    if consequence is None:
        return False
    return _first_exit(consequence, language) is not None


def _first_exit(body: Node | None, language: str | None = None) -> Node | None:
    """The exit statement of a small if-body: a lone return/raise/throw/goto, or an abort call."""
    if body is None:
        return None
    statements = (
        [body]
        if body.type not in ("block", "compound_statement", "statement_block")
        else [c for c in body.named_children if c.type != "comment"]
    )
    if not statements or len(statements) > 3:
        return None
    exits = set().union(*_EXITS.values()) if language is None else _EXITS[language]
    for statement in statements:
        if statement.type in exits:
            return statement
        if statement.type == "expression_statement":
            call = statement.named_children[0] if statement.named_children else None
            if call is not None and call.type == "call_expression":
                if _ABORT_CALLS.match(_call_name(call)):
                    return statement
    return None


def _except_types(node: Node) -> str:
    """The exception types an except clause catches, as written (empty for a bare except)."""
    for child in node.named_children:
        if child.type in ("block", "comment"):
            continue
        if child.type == "as_pattern":
            child = child.named_children[0] if child.named_children else child
        return (child.text or b"").decode(errors="replace")
    return ""


def _call_name(call: Node) -> bytes:
    function = call.child_by_field_name("function")
    if function is None:
        return b""
    text = function.text or b""
    return text.rsplit(b".", 1)[-1].rsplit(b"->", 1)[-1]


def _function_name(node: Node) -> str:
    current = node.parent
    while current is not None:
        if current.type in _FUNCTIONS:
            name = current.child_by_field_name("name")
            if name is None:  # C keeps the name inside the declarator
                declarator = current.child_by_field_name("declarator")
                while declarator is not None and declarator.type != "identifier":
                    declarator = declarator.child_by_field_name("declarator")
                name = declarator
            return (name.text or b"").decode(errors="replace") if name is not None else ""
        current = current.parent
    return ""


def _text(node: Node, span: tuple[int, int] | None = None) -> str:
    raw = node.text or b""
    if span is not None:
        raw = raw[span[0] - node.start_byte : span[1] - node.start_byte]
    return " ".join(raw.decode(errors="replace").split())[:200]


@dataclass(frozen=True)
class GuardChange:
    change: str  # removed | weakened
    guard: Guard  # the guard as it was in the base version
    after: Guard | None  # the weakened guard in the head version
    reason: str


def compare_guards(
    base: list[Guard], head: list[Guard], moved: set[str] = frozenset()
) -> list[GuardChange]:
    """Guards removed or weakened from base to head.

    A guard whose fingerprint survives anywhere in the head file is unchanged (it may have
    moved or been reformatted). A fingerprint in `moved` survives in another file of the same
    change, so it moved rather than disappeared. A vanished guard is paired with a new guard
    of the same kind in the same function; if the pair is a clear weakening it is reported
    as weakened, and otherwise the guard is reported as removed only if nothing replaced it.
    """
    remaining = Counter(g.fingerprint for g in head)
    gone = []
    for guard in base:
        if remaining[guard.fingerprint] > 0:
            remaining[guard.fingerprint] -= 1
        elif guard.fingerprint not in moved:
            gone.append(guard)
    new = [g for g in head if remaining[g.fingerprint] > 0]
    changes = []
    for guard in gone:
        partner = next(
            (g for g in new if g.kind == guard.kind and g.function == guard.function), None
        )
        if partner is None:
            changes.append(GuardChange("removed", guard, None, f"{guard.kind} removed"))
            continue
        new.remove(partner)
        reason = weakening(guard, partner)
        if reason:
            changes.append(GuardChange("weakened", guard, partner, reason))
    return changes


def weakening(before: Guard, after: Guard) -> str:
    """Why `after` is a weaker version of `before`, or "" if it isn't clearly weaker."""
    if before.kind == "except":
        if after.detail.strip() in {b.decode() for b in _BROAD_EXCEPTIONS} and (
            before.detail.strip() not in {b.decode() for b in _BROAD_EXCEPTIONS}
        ):
            return f"except broadened from {before.detail or 'bare'} to {after.detail or 'bare'}"
    if before.kind == "limit":
        old, new = _number(before.detail), _number(after.detail)
        name_old, name_new = before.detail.split("=")[0], after.detail.split("=")[0]
        if name_old == name_new and old is not None and new is not None and new < old:
            return f"{name_old.strip()} lowered from {old:g} to {new:g}"
    if before.kind in ("early-exit", "assert"):
        if re.search(r"\b(or True|\|\| true|\|\| 1)\b", after.text):
            return "condition short-circuited to always pass"
    return ""


def _number(detail: str) -> float | None:
    match = re.search(r"=\s*(-?\d+(?:\.\d+)?)", detail)
    return float(match[1]) if match else None

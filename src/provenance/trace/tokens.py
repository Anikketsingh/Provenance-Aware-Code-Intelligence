"""Turn source code into a normalised token stream.

Two versions of a file with equal streams do the same thing, so a change between them is
cosmetic. The rule for every normalisation here: when unsure, keep the token. A missed
cosmetic commit only costs a little accuracy, but calling a logic change cosmetic would hide
the true origin of a line.
"""

from functools import cache
from pathlib import PurePosixPath

import tree_sitter_c
import tree_sitter_javascript
import tree_sitter_python
from tree_sitter import Language, Node, Parser, Tree

LANGUAGE_BY_SUFFIX = {
    ".c": "c",
    ".h": "c",
    ".cjs": "javascript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".py": "python",
    ".pyi": "python",
}

_GRAMMARS = {
    "c": tree_sitter_c.language,
    "javascript": tree_sitter_javascript.language,
    "python": tree_sitter_python.language,
}

#: Prefix that marks identifier tokens, so rename detection can find them.
ID_PREFIX = b"\x00"

# Python's structure lives in indentation, which tokens lose. Without these markers, moving a
# statement into an `if` body would look like no change at all.
_BLOCK_OPEN = b"\x01{"
_BLOCK_CLOSE = b"\x01}"
# Line breaks end statements in Python, and sometimes in JavaScript. Without this marker,
# `self.check` followed by `(a, b)` on the next line looks the same as `self.check(a, b)`.
_STATEMENT_END = b"\x01;"

_IDENTIFIER_TYPES = frozenset(
    {
        "identifier",
        "field_identifier",
        "property_identifier",
        "type_identifier",
        "shorthand_property_identifier",
        "statement_identifier",
    }
)
_SKIP_TYPES = frozenset({"comment", "html_comment", "line_continuation"})
_CLOSERS = frozenset({")", "]", "}"})
_NUMBER_TYPES = frozenset({"integer", "float", "number", "number_literal"})
_PY_IMPORT_TYPES = frozenset(
    {"import_statement", "import_from_statement", "future_import_statement"}
)

# Parents where parentheses wrap a whole expression, so removing them cannot change meaning.
_PY_PAREN_SAFE = frozenset(
    {
        "assignment",
        "augmented_assignment",
        "return_statement",
        "expression_statement",
        "assert_statement",
        "if_statement",
        "elif_clause",
        "while_statement",
        "for_statement",
        "raise_statement",
        "delete_statement",
        "keyword_argument",
        "argument_list",
        "with_item",
        "pair",
        "list",
        "set",
        "tuple",
        "expression_list",
        "generator_expression",
        "list_comprehension",
    }
)
# Tuples are stricter: `assert (x, "msg")` is always true, unlike `assert x, "msg"`.
_PY_TUPLE_SAFE = frozenset(
    {"assignment", "augmented_assignment", "return_statement", "for_statement"}
)
_JS_PAREN_SAFE = frozenset(
    {"variable_declarator", "assignment_expression", "return_statement", "expression_statement"}
)


# Which parents bind an identifier: parent type -> the field it binds, or None for any child.
_BINDERS: dict[str, dict[str, str | None]] = {
    "python": {
        "function_definition": "name",
        "class_definition": "name",
        "parameters": None,
        "lambda_parameters": None,
        "default_parameter": "name",
        "typed_default_parameter": "name",
        "typed_parameter": None,
        "list_splat_pattern": None,
        "dictionary_splat_pattern": None,
        "assignment": "left",
        "augmented_assignment": "left",
        "for_statement": "left",
        "pattern_list": None,
        "tuple_pattern": None,
        "as_pattern_target": None,
        "named_expression": "name",
    },
    "javascript": {
        "variable_declarator": "name",
        "function_declaration": "name",
        "function_expression": "name",
        "class_declaration": "name",
        "formal_parameters": None,
        "arrow_function": "parameter",
        "assignment_pattern": "left",
    },
    "c": {
        "init_declarator": "declarator",
        "declaration": "declarator",
        "function_declarator": "declarator",
        "parameter_declaration": "declarator",
        "pointer_declarator": "declarator",
        "array_declarator": "declarator",
        "preproc_def": "name",
    },
}


@cache
def _parser(language: str) -> Parser:
    return Parser(Language(_GRAMMARS[language]()))


def language_for(path: str) -> str | None:
    return LANGUAGE_BY_SUFFIX.get(PurePosixPath(path).suffix.lower())


def parse(source: bytes, language: str) -> Tree:
    return _parser(language).parse(source)


def tokenize(source: bytes, language: str) -> list[bytes] | None:
    """Return normalised tokens, or None if the code has parse errors."""
    root = parse(source, language).root_node
    if root.has_error:
        return None
    tokens: list[bytes] = []
    _walk(root, language, tokens)
    return tokens


def bound_names(source: bytes, language: str) -> set[bytes]:
    """Return identifiers this file defines, as tokens with ID_PREFIX.

    Only these can be truly renamed. Everything else, such as `base64.encodestring` or
    `forms.CharField`, belongs to other code, so changing it calls something different.
    """
    binders = _BINDERS[language]
    names: set[bytes] = set()
    stack = [parse(source, language).root_node]
    while stack:
        node = stack.pop()
        stack.extend(node.children)
        parent = node.parent
        if parent is None or node.type not in _IDENTIFIER_TYPES or parent.type not in binders:
            continue
        field = binders[parent.type]
        if field is None or parent.child_by_field_name(field) == node:
            names.add(ID_PREFIX + (node.text or b""))
    return names


def _walk(node: Node, language: str, out: list[bytes]) -> None:
    # An explicit stack, because deep expressions can exceed Python's recursion limit.
    stack: list[Node | bytes] = [node]
    while stack:
        current = stack.pop()
        if isinstance(current, bytes):
            out.append(current)
            continue
        node_type = current.type
        if node_type in _SKIP_TYPES:
            continue
        if language == "python":
            if node_type == "expression_statement" and _is_bare_string(current):
                continue  # docstrings have no effect on behaviour
            if node_type == "string":
                out.append(_python_string(current))
                continue
            if node_type == "concatenated_string" and _can_join(current):
                out.append(_joined_string(current))
                continue
            if node_type == "block":
                out.append(_BLOCK_OPEN)
                stack.append(_BLOCK_CLOSE)
        elif language == "javascript":
            if node_type == ";":
                continue  # Prettier adds these, and their meaning comes from layout
            if node_type == "string":
                out.append(_js_string(current))
                continue

        if current.child_count == 0:
            out.append(_leaf(current, node_type))
            continue
        if node_type in _NUMBER_TYPES:
            out.append(_leaf(current, node_type))
            continue

        stack.extend(reversed(_kept_items(current, node_type, language)))


def _leaf(node: Node, node_type: str) -> bytes:
    text = node.text or b""
    if node_type in _IDENTIFIER_TYPES:
        return ID_PREFIX + text
    if node_type == "float":
        return _python_float(text)
    if node_type in _NUMBER_TYPES:
        return text.lower()
    return text


def _python_float(text: bytes) -> bytes:
    """Equal values give equal tokens, so `1.`, `1.0` and `.1e1` all match."""
    try:
        return repr(float(text.replace(b"_", b""))).encode()
    except ValueError:
        return text.lower()  # imaginary literals such as 1j


def _is_bare_string(node: Node) -> bool:
    named = [c for c in node.named_children if c.type not in _SKIP_TYPES]
    if len(named) != 1 or named[0].type not in ("string", "concatenated_string"):
        return False
    # Doctests are executable code that happens to live in a string.
    return b">>>" not in (named[0].text or b"")


def _string_parts(node: Node) -> list[Node]:
    return [c for c in node.named_children if c.type not in _SKIP_TYPES]


def _can_join(node: Node) -> bool:
    parts = _string_parts(node)
    if not all(part.type == "string" for part in parts):
        return False
    return len({_python_string_parts(part)[0] for part in parts}) == 1


def _joined_string(node: Node) -> bytes:
    """Line wrapping splits long strings, so `"a" "b"` and `"ab"` must give the same token."""
    parts = [_python_string_parts(part) for part in _string_parts(node)]
    return b"str:" + parts[0][0] + b":" + b"".join(body for _, body in parts)


def _python_string(node: Node) -> bytes:
    prefix, body = _python_string_parts(node)
    return b"str:" + prefix + b":" + body


def _python_string_parts(node: Node) -> tuple[bytes, bytes]:
    start, end = _string_edges(node)
    prefix = start.replace(b'"', b"").replace(b"'", b"").lower().replace(b"u", b"")
    prefix = bytes(sorted(prefix))  # `br` and `rb` are the same prefix
    body = (node.text or b"")[len(start) : -len(end) or None]
    if b"r" not in prefix:
        body = body.replace(b"\\'", b"'").replace(b'\\"', b'"')
    return prefix, body


def _string_edges(node: Node) -> tuple[bytes, bytes]:
    children = node.children
    return children[0].text or b"", children[-1].text or b""


def _js_string(node: Node) -> bytes:
    body = (node.text or b"")[1:-1].replace(b"\\'", b"'").replace(b'\\"', b'"')
    return b"str:" + body


def _kept_items(node: Node, node_type: str, language: str) -> list[Node | bytes]:
    children = node.children
    if language == "python":
        if node_type == "class_definition":
            children = [c for c in children if not _is_empty_argument_list(c)]
        if node_type in ("module", "block"):
            return _with_canonical_imports(children)
    if language == "javascript" and node_type in ("program", "statement_block"):
        return _with_statement_ends(children)
    # Commas first: the closing bracket they sit against may be the one removed next.
    if language != "c":
        children = _without_trailing_comma(node, node_type, children)
    if _parens_are_redundant(node, node_type, language):
        children = children[1:-1]
    if language == "python" and node_type == "with_clause":
        children = [c for c in children if c.type not in ("(", ")")]
    return children


def _with_canonical_imports(children: list[Node]) -> list[Node | bytes]:
    """Replace each run of imports with one sorted entry per imported name.

    This treats `from a import (b, c)`, split lines and isort reordering as the same. Import
    order can matter when modules have side effects, but that is rare and this is what
    formatters change most often. Each entry is one token, not an identifier, so a changed
    import never passes as a rename: `import json` to `import ujson` is a different module.
    """
    items: list[Node | bytes] = []
    run: list[bytes] = []
    for child in children:
        if child.type in _PY_IMPORT_TYPES:
            run.extend(_import_entries(child))
        elif child.type in _SKIP_TYPES or child.type == ";":
            continue
        else:
            items.extend(sorted(run))
            run = []
            items.append(child)
            if not (child.type == "expression_statement" and _is_bare_string(child)):
                items.append(_STATEMENT_END)
    items.extend(sorted(run))
    return items


def _with_statement_ends(children: list[Node]) -> list[Node | bytes]:
    items: list[Node | bytes] = []
    for child in children:
        items.append(child)
        if child.type not in _SKIP_TYPES and child.type not in ("{", "}", ";"):
            items.append(_STATEMENT_END)
    return items


def _import_entries(statement: Node) -> list[bytes]:
    names = [_squash(n) for n in statement.children_by_field_name("name")]
    if statement.type == "import_statement":
        return [b"import:" + name for name in names]
    module_node = statement.child_by_field_name("module_name")
    module = _squash(module_node) if module_node else b"__future__"
    if not names:
        names = [b"*"]  # wildcard imports have no name field
    return [b"import:" + module + b":" + name for name in names]


def _squash(node: Node) -> bytes:
    return b" ".join((node.text or b"").split())


def _is_empty_argument_list(node: Node) -> bool:
    return node.type == "argument_list" and node.named_child_count == 0


def _parens_are_redundant(node: Node, node_type: str, language: str) -> bool:
    parent = node.parent
    if parent is None:
        return False
    if language == "python":
        if node_type == "parenthesized_expression":
            return parent.type in _PY_PAREN_SAFE
        if node_type in ("tuple", "tuple_pattern"):
            return parent.type in _PY_TUPLE_SAFE and _has_parens(node)
    if language == "javascript" and node_type == "parenthesized_expression":
        return parent.type in _JS_PAREN_SAFE
    return False


def _has_parens(node: Node) -> bool:
    return node.child_count >= 2 and node.children[0].type == "("


def _without_trailing_comma(node: Node, node_type: str, children: list[Node]) -> list[Node]:
    if not children:
        return children
    # A trailing comma is what makes `(1,)` a tuple, and `x[1,]` differs from `x[1]`.
    if node_type == "subscript":
        return children
    if node_type in ("tuple", "tuple_pattern") and len(_real_named(node)) == 1:
        return children
    kept = []
    for index, child in enumerate(children):
        if child.type == "," and _next_is_closer(children, index):
            continue
        kept.append(child)
    return kept


def _real_named(node: Node) -> list[Node]:
    return [c for c in node.named_children if c.type not in _SKIP_TYPES]


def _next_is_closer(children: list[Node], index: int) -> bool:
    for child in children[index + 1 :]:
        if child.type in _SKIP_TYPES:
            continue
        return child.type in _CLOSERS
    return False

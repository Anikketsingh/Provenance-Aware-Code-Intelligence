"""Find the lines of a file that hold real logic, as opposed to comments, imports or braces."""

from tree_sitter import Node

from provenance.trace.tokens import parse

_SKIPPED_NODES = frozenset(
    {
        "comment",
        "html_comment",
        "import_statement",
        "import_from_statement",
        "future_import_statement",
        "preproc_include",
    }
)

#: Lines with fewer tokens are mostly punctuation, and have no meaningful "why".
MIN_TOKENS = 3


def logic_lines(source: bytes, language: str) -> set[int]:
    """Return 1-based numbers of lines with at least MIN_TOKENS code tokens."""
    counts: dict[int, int] = {}
    stack: list[Node] = [parse(source, language).root_node]
    while stack:
        node = stack.pop()
        if node.type in _SKIPPED_NODES or _is_docstring(node, language):
            continue
        if node.child_count == 0:
            row = node.start_point[0]
            counts[row] = counts.get(row, 0) + 1
        stack.extend(node.children)
    return {row + 1 for row, count in counts.items() if count >= MIN_TOKENS}


def _is_docstring(node: Node, language: str) -> bool:
    if language != "python" or node.type != "expression_statement":
        return False
    named = node.named_children
    return len(named) == 1 and named[0].type in ("string", "concatenated_string")

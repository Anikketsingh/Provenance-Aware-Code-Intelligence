"""Real mistakes found by reviewing what the classifier flagged on Django.

Each of these hid a real behaviour change when it was wrongly called cosmetic or a rename.
Commit SHAs are noted where a case came from a specific Django commit.
"""

import pytest

from provenance.model import ChangeKind
from provenance.trace.classify import classify_source

MUST_STAY_LOGIC = [
    # cf731a543: a different base class
    ("python", "class W(forms.CharField):\n    pass\n", "class W(forms.TextInput):\n    pass\n"),
    # 212a51298: a different library function
    ("python", "use(base64.encodestring(x))\n", "use(base64.b64encode(x))\n"),
    # 428c88408: a different attribute
    ("python", "if c.ops.postgis:\n    a()\n", "if c.features.has_kml:\n    a()\n"),
    # The same idea for names this file doesn't define
    ("python", "use(timeout)\n", "use(limit)\n"),
    ("javascript", "api.oldCall(x);\n", "api.newCall(x);\n"),
    ("c", "void f(void) { use(old_helper(1)); }\n", "void f(void) { use(new_helper(1)); }\n"),
    # 2a149e29b, eecd90f5c, 1637fefcb: doctests are executable
    ("python", "'''\n>>> f()\n1\n'''\n", "'''\n>>> f()\n2\n'''\n"),
    (
        "python",
        'def f():\n    """\n    >>> g()\n    1\n    """\n',
        'def f():\n    """\n    >>> g()\n    2\n    """\n',
    ),
    # Joining strings must not hide a change
    ("python", "x = 'a' 'b'\n", "x = 'a' 'c'\n"),
    ("python", "x = b'ab'\n", "x = b'a' b'c'\n"),
    ("python", "x = 'ab'\n", "x = 'a' f'b'\n"),
]

COSMETIC = [
    ("python", "x = 'ab'\n", "x = 'a' 'b'\n"),
    ("python", "x = f('a b', 1)\n", "x = f(\n    'a '\n    'b',\n    1,\n)\n"),
    ("python", "x = {'a': b if c else d}\n", "x = {'a': (b if c else d)}\n"),
    ("python", "x = [a if b else c]\n", "x = [(a if b else c)]\n"),
    ("python", "'''Plain module docstring.'''\n", "'''Better docstring.'''\n"),
]

RENAMES = [
    ("python", b"def old(x):\n    return x\n\nold(1)\n", b"def new(x):\n    return x\n\nnew(1)\n"),
    ("python", b"for i in y:\n    use(i)\n", b"for item in y:\n    use(item)\n"),
    ("python", b"a, b = f()\nuse(a)\n", b"first, b = f()\nuse(first)\n"),
]


@pytest.mark.parametrize(("language", "old", "new"), MUST_STAY_LOGIC)
def test_must_stay_logic(language, old, new):
    assert classify_source(old.encode(), new.encode(), language) == ChangeKind.LOGIC


@pytest.mark.parametrize(("language", "old", "new"), COSMETIC)
def test_cosmetic(language, old, new):
    assert classify_source(old.encode(), new.encode(), language) == ChangeKind.COSMETIC


@pytest.mark.parametrize(("language", "old", "new"), RENAMES)
def test_rename(language, old, new):
    assert classify_source(old, new, language) == ChangeKind.RENAME

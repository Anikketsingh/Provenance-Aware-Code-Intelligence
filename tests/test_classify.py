"""The classifier's most dangerous error is calling a logic change cosmetic.

MUST_STAY_LOGIC therefore holds pairs that look nearly identical but behave differently.
"""

import pytest

from provenance.model import ChangeKind
from provenance.trace.classify import classify_source

COSMETIC = [
    ("python", "x = 1\n", "x = 1  # set x\n"),
    ("python", "x=1\ny = 2\n", "x = 1\n\n\ny = 2\n"),
    ("python", "x = 'a'\n", 'x = "a"\n'),
    ("python", "x = 'it\\'s'\n", 'x = "it\'s"\n'),
    ("python", "x = U'a'\n", 'x = "a"\n'),
    ("python", "x = 0XFF\n", "x = 0xff\n"),
    ("python", "x = 1.\n", "x = 1.0\n"),
    ("python", "x = .5\n", "x = 0.5\n"),
    ("python", "x = br'a'\n", "x = rb'a'\n"),
    ("python", "x = 1.0E5\n", "x = 1.0e5\n"),
    ("python", "f(a, b)\n", "f(\n    a,\n    b,\n)\n"),
    ("python", "x = [1, 2]\n", "x = [\n    1,\n    2,\n]\n"),
    ("python", "x = a + b\n", "x = (\n    a + b\n)\n"),
    ("python", "return_value = (yield)\n", "return_value = (yield)\n"),
    (
        "python",
        "def f():\n    '''Old.'''\n    return 1\n",
        'def f():\n    """New."""\n    return 1\n',
    ),
    ("python", "class A():\n    pass\n", "class A:\n    pass\n"),
    ("python", "x = 1 + \\\n  2\n", "x = 1 + 2\n"),
    ("python", "x = (1, 2)\n", "x = 1, 2\n"),
    ("python", "def f():\n    return (1, 2)\n", "def f():\n    return 1, 2\n"),
    ("python", "for (a, b) in c:\n    pass\n", "for a, b in c:\n    pass\n"),
    ("python", "from a import b, c\n", "from a import b\nfrom a import c\n"),
    ("python", "from a import b, c\n", "from a import (\n    b,\n    c,\n)\n"),
    ("python", "import b\nimport a\nx = 1\n", "import a\nimport b\nx = 1\n"),
    ("python", "def f():\n    from a import b, c\n", "def f():\n    from a import c, b\n"),
    ("python", "a, b = c\n", "(\n    a,\n    b,\n) = c\n"),
    ("python", "x = 1, 2\n", "x = (\n    1,\n    2,\n)\n"),
    (
        "python",
        "def f():\n    return a, b\n",
        "def f():\n    return (\n        a,\n        b,\n    )\n",
    ),
    ("c", "int x=1;\n", "int x = 1;  /* one */\n"),
    ("c", "if(a){\nb();\n}\n", "if (a) {\n    b();\n}\n"),
    ("javascript", "let x = 'a'\n", 'let x = "a";\n'),
    ("javascript", "f(a, b)\n", "f(\n  a,\n  b,\n);\n"),
    ("javascript", "// note\nlet x = 1;\n", "let x = 1;\n"),
]

RENAMES = [
    ("python", "def f(a):\n    return a\n", "def f(value):\n    return value\n"),
    ("c", "int a = 1;\nuse(a);\n", "int count = 1;\nuse(count);\n"),
    ("javascript", "const a = 1; g(a);\n", "const total = 1; g(total);\n"),
]

MUST_STAY_LOGIC = [
    # Values and operators
    ("python", "x = 1\n", "x = 2\n"),
    ("python", "x = 1.0\n", "x = 1.5\n"),
    ("python", "x = 1.0\n", "x = 1\n"),
    ("python", "x = 1j\n", "x = 2j\n"),
    ("python", "x = a < b\n", "x = a <= b\n"),
    ("python", "x = 'a'\n", "x = 'b'\n"),
    ("python", "x = 'a b'\n", "x = 'a  b'\n"),
    ("python", "x = b'a'\n", "x = 'a'\n"),
    ("python", "x = r'\\''\n", "x = '\\''\n"),
    ("c", "int x = 1;\n", "int x = 2;\n"),
    ("javascript", "let x = 'a';\n", "let x = 'b';\n"),
    # Parentheses and commas that carry meaning
    ("python", "x = (a + b) * c\n", "x = a + b * c\n"),
    ("python", "x = (1,)\n", "x = (1)\n"),
    ("python", "x = 1,\n", "x = 1\n"),
    ("python", "x = a[1,]\n", "x = a[1]\n"),
    ("python", "assert (a, 'msg')\n", "assert a, 'msg'\n"),
    ("python", "f((a, b))\n", "f(a, b)\n"),
    ("javascript", "x = (a + b) * c;\n", "x = a + b * c;\n"),
    # Removing or reordering code
    ("python", "if a:\n    raise E\n", "pass\n"),
    ("python", "a()\nb()\n", "b()\na()\n"),
    ("python", "if a:\n    b()\nc()\n", "if a:\n    b()\n    c()\n"),
    # Renames that aren't: the new name already exists, or the mapping isn't one-to-one
    ("python", "t = 1\nd = 2\nuse(t)\n", "t = 1\nd = 2\nuse(d)\n"),
    ("python", "use(a, b)\n", "use(b, a)\n"),
    ("python", "use(a, a)\n", "use(a, b)\n"),
    # Imports and the code around them
    ("python", "import json\njson.x()\n", "import ujson\nujson.x()\n"),
    ("python", "from a import b\n", "from c import b\n"),
    ("python", "from a import b as c\n", "from a import b as d\n"),
    ("python", "import a\nx()\nimport b\n", "import a\nimport b\nx()\n"),
    # Code that doesn't parse must never count as cosmetic
    ("python", "def f(:\n", "def f(: \n"),
    ("c", "int x = ;\n", "int x  = ;\n"),
]


@pytest.mark.parametrize(("language", "old", "new"), COSMETIC)
def test_cosmetic(language, old, new):
    assert classify_source(old.encode(), new.encode(), language) == ChangeKind.COSMETIC


@pytest.mark.parametrize(("language", "old", "new"), RENAMES)
def test_rename(language, old, new):
    assert classify_source(old.encode(), new.encode(), language) == ChangeKind.RENAME


@pytest.mark.parametrize(("language", "old", "new"), MUST_STAY_LOGIC)
def test_must_stay_logic(language, old, new):
    assert classify_source(old.encode(), new.encode(), language) == ChangeKind.LOGIC


def test_invalid_utf8_is_handled():
    old = b"x = '\xff'  # caf\xe9\n"
    assert classify_source(old, old + b"# more\n", "python") == ChangeKind.COSMETIC

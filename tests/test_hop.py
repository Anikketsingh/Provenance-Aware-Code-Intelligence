"""Layer C: commits that mix cosmetic and real changes inside a single file."""

from provenance.ingest.git_history import ingest_history
from provenance.model import ChangeKind
from provenance.store.db import Store
from provenance.trace.chain import Tracer
from provenance.trace.hop import Hunk, line_tokens, parse_diff, step_back
from provenance.trace.layer_a import classify_repo, write_ignore_file

BASE = """def guard(n):
    if n > 10:
        raise ValueError('too big')
    return n


def other(a):
    return a
"""


def analyse(git_repo):
    repo = git_repo.repo
    store = Store(repo.db_path)
    ingest_history(repo, store)
    classify_repo(repo, store, workers=1)
    write_ignore_file(repo, store)
    return Tracer(repo, store)


def test_reformat_and_fix_in_one_file(git_repo):
    origin = git_repo.commit("Add", {"a.py": BASE})
    mixed = BASE.replace("'too big'", '"too big"').replace("return a", "return a + 1")
    fix = git_repo.commit("Reformat and fix", {"a.py": mixed})
    tracer = analyse(git_repo)

    reformatted_line = tracer.trace("a.py", 3)
    assert reformatted_line.origin == origin
    assert [hop.kind for hop in reformatted_line.hops] == [ChangeKind.COSMETIC, ChangeKind.ORIGIN]

    fixed_line = tracer.trace("a.py", 8)
    assert fixed_line.origin == fix
    assert fixed_line.first_seen == origin


def test_line_wrapped_in_mixed_commit(git_repo):
    origin = git_repo.commit("Add", {"a.py": "total = compute(first_value, second_value)\ny = 1\n"})
    wrapped = "total = compute(\n    first_value,\n    second_value,\n)\ny = 2\n"
    git_repo.commit("Wrap and change y", {"a.py": wrapped})
    tracer = analyse(git_repo)
    assert tracer.trace("a.py", 2).origin == origin


def test_function_moved_between_files_with_other_edits(git_repo):
    body = "def helper(value):\n    return compute_the_thing(value, limit=10, retries=3)\n"
    origin = git_repo.commit("Add", {"a.py": body + "x = 1\n", "b.py": "y = 1\n"})
    git_repo.commit("Move", {"a.py": "x = 2\n", "b.py": "y = 2\n" + body})
    tracer = analyse(git_repo)
    assert tracer.trace("b.py", 3).origin == origin


def test_edit_gives_last_change_and_first_appearance(git_repo):
    origin = git_repo.commit("Add", {"a.py": "retry(limit=3, delay=1)\n"})
    edit = git_repo.commit("Raise", {"a.py": "retry(limit=5, delay=1)\n"})
    chain = analyse(git_repo).trace("a.py", 1)
    assert chain.origin == edit
    assert chain.first_seen == origin


def test_new_line_is_its_own_origin(git_repo):
    git_repo.commit("Add", {"a.py": "x = 1\n"})
    added = git_repo.commit("More", {"a.py": "x = 1\nunrelated_call(flag=True)\n"})
    chain = analyse(git_repo).trace("a.py", 2)
    assert chain.origin == added
    assert chain.first_seen == added
    assert chain.stop_reason == "first_appearance"


def test_parse_diff_with_rename_and_counts():
    text = (
        "diff --git a/old.py b/new.py\nsimilarity index 90%\nrename from old.py\n"
        "rename to new.py\n--- a/old.py\n+++ b/new.py\n@@ -3 +3,2 @@ def f():\n"
        "-    a = 1\n+    a = 2\n+    b = 3\n"
        "@@ -9,0 +11 @@\n+    c = 4\n"
    )
    first, second = parse_diff(text)
    assert (first.old_path, first.new_path) == ("old.py", "new.py")
    assert first.old_lines == ("    a = 1",)
    assert first.new_lines == ("    a = 2", "    b = 3")
    assert (second.old_lines, second.new_start) == ((), 11)


def test_parse_diff_keeps_lines_that_look_like_headers():
    text = "--- a/x.sql\n+++ b/x.sql\n@@ -1 +1 @@\n--- old comment\n+-- new comment\n"
    hunk = parse_diff(text)[0]
    assert hunk.old_lines == ("-- old comment",)
    assert hunk.new_lines == ("-- new comment",)


def test_too_short_lines_do_not_match():
    hunk = Hunk("a.py", 1, ("return x",), "a.py", 1, ("}",))
    assert step_back([hunk], "a.py", 1) is None


def test_tokens_ignore_quote_style_and_layout():
    assert line_tokens("f('a', b)") == line_tokens('f("a" b')

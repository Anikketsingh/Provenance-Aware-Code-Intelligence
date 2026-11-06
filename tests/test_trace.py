"""End-to-end tests on real git repos with known answers."""

import pytest

from provenance.gitio import BlobReader, iter_commits, validate_rev
from provenance.ingest.git_history import ingest_history
from provenance.model import ChangeKind
from provenance.store.db import Store
from provenance.trace.chain import Tracer
from provenance.trace.layer_a import classify_repo, write_ignore_file

GUARD = "def f(n):\n    if n > 10:\n        raise ValueError('too big')\n    return n\n"
REFORMATTED = 'def f(n):\n    if n > 10:\n        raise ValueError("too big")\n\n    return n\n'


def analyse(git_repo):
    repo = git_repo.repo
    store = Store(repo.db_path)
    ingest_history(repo, store)
    classify_repo(repo, store, workers=1)
    write_ignore_file(repo, store)
    return repo, store, Tracer(repo, store)


def test_reformat_is_skipped(git_repo):
    origin = git_repo.commit("Add guard", {"a.py": GUARD})
    reformat = git_repo.commit("Reformat", {"a.py": REFORMATTED})
    repo, store, tracer = analyse(git_repo)

    assert store.commit_kind(reformat) == ChangeKind.COSMETIC
    assert reformat in repo.ignore_file.read_text()

    chain = tracer.trace("a.py", 3)  # the raise line, which the reformat really edited
    assert chain.origin == origin
    assert [hop.kind for hop in chain.hops] == [ChangeKind.COSMETIC, ChangeKind.ORIGIN]


def test_logic_change_after_reformat_stops_at_logic(git_repo):
    git_repo.commit("Add guard", {"a.py": GUARD})
    git_repo.commit("Reformat", {"a.py": REFORMATTED})
    change = git_repo.commit("Raise limit", {"a.py": REFORMATTED.replace("10", "20")})
    _, _, tracer = analyse(git_repo)

    chain = tracer.trace("a.py", 2)
    assert chain.origin == change
    assert chain.stop_reason == "logic_change"


def test_mixed_commit_is_not_ignored(git_repo):
    git_repo.commit("Add", {"a.py": GUARD, "b.py": "x = 1\n"})
    mixed = git_repo.commit("Mixed", {"a.py": REFORMATTED, "b.py": "x = 2\n"})
    repo, store, _ = analyse(git_repo)
    assert store.commit_kind(mixed) == ChangeKind.LOGIC
    assert mixed not in repo.ignore_file.read_text()


def test_mixed_commit_is_skipped_only_for_cosmetic_file(git_repo):
    origin = git_repo.commit("Add", {"a.py": GUARD, "b.py": "x = 1\n"})
    mixed = git_repo.commit("Mixed", {"a.py": REFORMATTED, "b.py": "x = 2\n"})
    _, _, tracer = analyse(git_repo)
    assert tracer.trace("a.py", 3).origin == origin
    assert tracer.trace("b.py", 1).origin == mixed


def test_reformat_under_an_older_file_name_is_skipped(git_repo):
    origin = git_repo.commit("Add", {"old.py": GUARD})
    git_repo.commit("Reformat", {"old.py": REFORMATTED})
    git_repo.commit("Rename file", {"old.py": None, "new.py": REFORMATTED})
    _, _, tracer = analyse(git_repo)
    assert tracer.trace("new.py", 3).origin == origin


def test_rename_commit_is_skipped(git_repo):
    origin = git_repo.commit("Add", {"a.py": "def f(a):\n    return a + 1\n"})
    rename = git_repo.commit("Rename", {"a.py": "def f(val):\n    return val + 1\n"})
    _, store, tracer = analyse(git_repo)
    assert store.commit_kind(rename) == ChangeKind.RENAME
    assert tracer.trace("a.py", 2).origin == origin


def test_file_move_follows_line(git_repo):
    origin = git_repo.commit("Add", {"old/a.py": GUARD})
    move = git_repo.commit("Move", {"old/a.py": None, "new/b.py": GUARD})
    _, store, tracer = analyse(git_repo)
    assert store.commit_kind(move) == ChangeKind.MOVE
    assert tracer.trace("new/b.py", 2).origin == origin


def test_docs_only_commit_is_not_listed(git_repo):
    git_repo.commit("Add", {"a.py": GUARD})
    docs = git_repo.commit("Docs", {"notes.rst": "hello\n"})
    repo, store, _ = analyse(git_repo)
    assert store.commit_kind(docs) == ChangeKind.UNKNOWN
    assert docs not in repo.ignore_file.read_text()


def test_docs_alongside_reformat_still_cosmetic(git_repo):
    git_repo.commit("Add", {"a.py": GUARD})
    both = git_repo.commit("Both", {"a.py": REFORMATTED, "notes.rst": "hi\n"})
    _, store, _ = analyse(git_repo)
    assert store.commit_kind(both) == ChangeKind.COSMETIC


def test_unsupported_language_counts_as_logic(git_repo):
    git_repo.commit("Add", {"a.go": "package a\n"})
    change = git_repo.commit("Edit", {"a.go": "package a // x\n"})
    _, store, _ = analyse(git_repo)
    assert store.commit_kind(change) == ChangeKind.LOGIC


def test_merge_is_not_listed(git_repo):
    git_repo.commit("Add", {"a.py": GUARD})
    git_repo.run("checkout", "-q", "-b", "side")
    git_repo.commit("Side", {"b.py": "x = 1\n"})
    git_repo.run("checkout", "-q", "main")
    git_repo.commit("Main", {"c.py": "y = 1\n"})
    git_repo.run("merge", "-q", "--no-ff", "--no-edit", "side")
    merge = git_repo.run("rev-parse", "HEAD")
    repo, store, _ = analyse(git_repo)
    assert store.commit_kind(merge) == ChangeKind.UNKNOWN
    assert merge not in repo.ignore_file.read_text()


def test_line_out_of_range(git_repo):
    git_repo.commit("Add", {"a.py": GUARD})
    _, _, tracer = analyse(git_repo)
    chain = tracer.trace("a.py", 999)
    assert chain.origin is None
    assert chain.stop_reason == "lost_line"


def test_crlf_change_is_cosmetic(git_repo):
    git_repo.commit("Add", {"a.py": GUARD})
    crlf = git_repo.commit("CRLF", {"a.py": GUARD.replace("\n", "\r\n")})
    _, store, _ = analyse(git_repo)
    assert store.commit_kind(crlf) == ChangeKind.COSMETIC


def test_ingest_is_idempotent(git_repo):
    git_repo.commit("One", {"a.py": GUARD})
    git_repo.commit("Two", {"a.py": REFORMATTED})
    repo = git_repo.repo
    with Store(repo.db_path) as store:
        assert ingest_history(repo, store) == 2
        assert ingest_history(repo, store) == 0
        assert store.commit_count() == 2


def test_classification_resumes(git_repo):
    git_repo.commit("One", {"a.py": GUARD})
    repo = git_repo.repo
    with Store(repo.db_path) as store:
        ingest_history(repo, store)
        assert classify_repo(repo, store, workers=1) == 1
        assert classify_repo(repo, store, workers=1) == 0


def test_commit_message_with_odd_content(git_repo):
    git_repo.commit(":100644 looks like raw output\n\n:000 000 a b M\tfake.py", {"a.py": GUARD})
    records = list(iter_commits(git_repo.repo.git_dir))
    assert len(records) == 1
    assert [c.path for c in records[0].changes] == ["a.py"]


def test_rename_status_is_parsed(git_repo):
    git_repo.commit("Add", {"old.py": GUARD})
    git_repo.commit("Move", {"old.py": None, "new.py": GUARD})
    change = next(iter_commits(git_repo.repo.git_dir)).changes[0]
    assert (change.status, change.old_path, change.path) == ("R", "old.py", "new.py")


def test_blob_reader_handles_missing_and_large(git_repo):
    git_repo.commit("Add", {"a.py": GUARD})
    blob = git_repo.run("rev-parse", "HEAD:a.py")
    with BlobReader(git_repo.repo.git_dir) as reader:
        assert reader.read(blob) == GUARD.encode()
        assert reader.read("0" * 40) is None
        assert reader.read(blob, max_size=1) is None
        assert reader.read(blob) == GUARD.encode()


@pytest.mark.parametrize("rev", ["--output=x", "-h", "a..b", "a b", "", "HEAD;rm"])
def test_unsafe_revs_rejected(rev):
    with pytest.raises(ValueError):
        validate_rev(rev)

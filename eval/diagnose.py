"""Show why files in a commit were classified as logic: the first tokens that differ."""

import collections
import sys

from provenance.config import Repo
from provenance.gitio import BlobReader
from provenance.store.db import Store
from provenance.trace.classify import MAX_BLOB_SIZE
from provenance.trace.tokens import language_for, tokenize


def main(name: str, prefix: str, show: int = 25) -> None:
    repo = Repo.named(name)
    with Store(repo.db_path) as store, BlobReader(repo.git_dir) as reader:
        sha = store.full_sha(prefix)
        tally = collections.Counter()
        examples = []
        for change in store.changes(sha):
            language = language_for(change.path)
            if not language or not change.old_blob or not change.new_blob:
                tally[f"skip:{change.status}:{change.path.rsplit('.', 1)[-1][:12]}"] += 1
                continue
            old = tokenize(reader.read(change.old_blob, MAX_BLOB_SIZE) or b"", language)
            new = tokenize(reader.read(change.new_blob, MAX_BLOB_SIZE) or b"", language)
            if old is None or new is None:
                tally["parse_error"] += 1
                examples.append((change.path, "parse_error", b"", b""))
                continue
            if old == new:
                tally["equal"] += 1
                continue
            i = next(
                (i for i, (a, b) in enumerate(zip(old, new, strict=False)) if a != b),
                min(len(old), len(new)),
            )
            a, b = old[max(0, i - 2) : i + 3], new[max(0, i - 2) : i + 3]
            key = (
                old[i][:12] if i < len(old) else b"<end>",
                new[i][:12] if i < len(new) else b"<end>",
            )
            tally[f"diff:{key}"] += 1
            examples.append((change.path, f"len {len(old)} vs {len(new)}", a, b))
        for key, count in tally.most_common(22):
            print(f"{count:5} {key}")
        print()
        for path, note, a, b in examples[:show]:
            print(f"{path} ({note})\n   old {a}\n   new {b}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 25)

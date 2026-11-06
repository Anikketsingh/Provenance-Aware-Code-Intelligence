"""Corpus definitions and on-disk locations."""

import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = Path(os.environ.get("PROVENANCE_DATA", PROJECT_ROOT / "data"))

REPO_URLS = {
    "django": "https://github.com/django/django.git",
    "postgres": "https://github.com/postgres/postgres.git",
    "react": "https://github.com/react/react.git",
    "redis": "https://github.com/redis/redis.git",
}


@dataclass(frozen=True)
class Repo:
    """A repository and the local files derived from it."""

    name: str
    git_dir: Path
    db_path: Path
    ignore_file: Path

    @classmethod
    def named(cls, name: str, data_dir: Path | None = None) -> "Repo":
        root = (data_dir or DATA_DIR) / name
        return cls(name, root / "repo.git", root / "provenance.db", root / "auto-ignore-revs.txt")

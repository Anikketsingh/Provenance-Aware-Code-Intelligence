"""Build small git repos with known histories."""

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest

from provenance.config import Repo

_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "Test",
    "GIT_AUTHOR_EMAIL": "test@example.com",
    "GIT_AUTHOR_DATE": "2020-01-01T00:00:00Z",
    "GIT_COMMITTER_NAME": "Test",
    "GIT_COMMITTER_EMAIL": "test@example.com",
    "GIT_COMMITTER_DATE": "2020-01-01T00:00:00Z",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_SYSTEM": os.devnull,
}


@dataclass
class GitRepo:
    root: Path

    def run(self, *args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=self.root, env=_ENV, check=True, capture_output=True, text=True
        ).stdout.strip()

    def commit(self, message: str, files: dict[str, str | bytes | None]) -> str:
        """Write files (None deletes), commit them, and return the new sha."""
        for name, content in files.items():
            path = self.root / name
            if content is None:
                path.unlink()
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content if isinstance(content, bytes) else content.encode())
        self.run("add", "-A")
        self.run("commit", "--allow-empty", "-m", message)
        return self.run("rev-parse", "HEAD")

    @property
    def repo(self) -> Repo:
        data = self.root / ".provenance"
        return Repo("test", self.root / ".git", data / "provenance.db", data / "ignore.txt")


@pytest.fixture
def git_repo(tmp_path: Path) -> GitRepo:
    repo = GitRepo(tmp_path)
    repo.run("init", "-q", "-b", "main")
    (tmp_path / ".git" / "info" / "exclude").write_text(".provenance\n")
    return repo

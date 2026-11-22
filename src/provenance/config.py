"""Corpus definitions and on-disk locations.

Two kinds of repo exist:

- **Corpus repos** (`Repo.named`): the research repos in `REPO_URLS`, bare-cloned under `data/`.
  Every evaluation result is computed on these, so their layout never changes.
- **Any local repo** (`Repo.at`): a clone the user already has. Its data lives inside its own
  git directory (`.git/provenance/`), so nothing appears in the working tree.
"""

import os
import re
import subprocess
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

_GITHUB_REMOTE = re.compile(r"github\.com[:/]([\w.-]+)/([\w.-]+?)(?:\.git)?/?$")


class RepoNotFoundError(LookupError):
    pass


@dataclass(frozen=True)
class Repo:
    """A repository and the local files derived from it.

    `name` keys the repo's nodes in the link graph. A corpus repo uses its short name, such as
    `django`. Any other repo uses its GitHub `owner/name` when it has a GitHub remote, so links
    to its pull requests and issues resolve, and its folder name otherwise.
    """

    name: str
    git_dir: Path
    db_path: Path
    ignore_file: Path

    @classmethod
    def named(cls, name: str, data_dir: Path | None = None) -> "Repo":
        root = (data_dir or DATA_DIR) / name
        return cls(name, root / "repo.git", root / "provenance.db", root / "auto-ignore-revs.txt")

    @classmethod
    def at(cls, path: Path | str) -> "Repo":
        """A local clone, working copy or bare. Any folder inside the repo works."""
        start = Path(path).expanduser()
        if not start.is_dir():
            raise RepoNotFoundError(f"no such folder: {start}")
        git_dir = _rev_parse(start, "--absolute-git-dir")
        # Linked worktrees share one database, kept in the common git directory.
        common = _rev_parse(start, "--path-format=absolute", "--git-common-dir")
        data = common / "provenance"
        return cls(
            _local_name(git_dir),
            git_dir,
            data / "provenance.db",
            data / "auto-ignore-revs.txt",
        )


def resolve_repo(arg: str, data_dir: Path | None = None) -> Repo:
    """A corpus name such as `django`, or a path to any local git repo such as `.`."""
    looks_like_path = arg in (".", "..") or "/" in arg or arg.startswith("~")
    if not looks_like_path and (arg in REPO_URLS or ((data_dir or DATA_DIR) / arg).is_dir()):
        return Repo.named(arg, data_dir)
    if Path(arg).expanduser().is_dir():
        return Repo.at(arg)
    raise RepoNotFoundError(
        f"{arg!r} is neither a folder nor a known repo ({', '.join(sorted(REPO_URLS))})."
    )


def github_remote(git_dir: Path) -> str | None:
    """The `owner/name` of the repo's GitHub remote, preferring `origin`."""
    try:
        remotes = _git(git_dir, "remote").split()
    except RepoNotFoundError:
        return None
    for remote in sorted(remotes, key=lambda r: r != "origin"):
        try:
            url = _git(git_dir, "remote", "get-url", remote)
        except RepoNotFoundError:
            continue
        if match := _GITHUB_REMOTE.search(url):
            return f"{match[1]}/{match[2]}"
    return None


def _local_name(git_dir: Path) -> str:
    if slug := github_remote(git_dir):
        return slug
    top = git_dir.parent if git_dir.name == ".git" else git_dir
    return top.name.removesuffix(".git") or "repo"


def _rev_parse(start: Path, *args: str) -> Path:
    try:
        out = subprocess.run(
            ["git", "-C", str(start), "rev-parse", *args],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise RepoNotFoundError(f"{start} is not inside a git repository") from None
    return Path(out)


def _git(git_dir: Path, *args: str) -> str:
    try:
        return subprocess.run(
            ["git", "--git-dir", str(git_dir), *args],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise RepoNotFoundError(f"git {' '.join(args)} failed in {git_dir}") from None

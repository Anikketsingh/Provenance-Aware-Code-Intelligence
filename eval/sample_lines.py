"""Draw the seeded sample of lines for hand annotation.

Lines where methods disagree are the informative ones, so half the sample comes from them.
That oversampling would bias accuracy, so we also record each stratum's real share of the
population, and score_gold.py uses those shares as weights.

Usage: uv run python eval/sample_lines.py
"""

import csv
import json
import random
from pathlib import Path, PurePosixPath

from corpus import Baselines, hand_list, pinned_rev

from provenance.config import Repo
from provenance.gitio import git
from provenance.store.db import Store
from provenance.trace.lines import logic_lines
from provenance.trace.tokens import language_for

GOLD = Path(__file__).parent / "gold"
SEED = 20261108
FILES_PER_REPO = 120
PLAN = {"django": {"agree": 15, "disagree": 25}, "redis": {"agree": 8, "disagree": 12}}
ROOTS = {"django": ("django/",), "redis": ("src/",)}
EXCLUDED = ("django/conf/locale/", "django/contrib/admin/static/", "src/modules/", "src/commands/")
METHODS = ("B0", "B2", "Ours-A")


def eligible_files(repo: Repo, rev: str, name: str) -> list[str]:
    paths = git(repo.git_dir, "ls-tree", "-r", "--name-only", rev).splitlines()
    return sorted(
        path
        for path in paths
        if path.startswith(ROOTS[name])
        and not path.startswith(EXCLUDED)
        and PurePosixPath(path).name != "__init__.py"
        and language_for(path)
    )


def population(name: str, rng: random.Random) -> tuple[list[dict], dict]:
    repo = Repo.named(name)
    rev = pinned_rev(name)
    rows = []
    with Store(repo.db_path) as store:
        baselines = Baselines(repo, store, rev, hand_list(repo, rev))
        files = eligible_files(repo, rev, name)
        chosen = rng.sample(files, min(FILES_PER_REPO, len(files)))
        for number, path in enumerate(chosen, 1):
            if number % 20 == 0:
                print(f"  {name}: {number} of {len(chosen)} files", flush=True)
            blamed = baselines.blame_all(path)
            source = "\n".join(line.text for line in blamed["B0"]).encode()
            for line in sorted(logic_lines(source, language_for(path))):
                index = line - 1
                answers = {blamed[m][index].commit for m in METHODS}
                rows.append(
                    {
                        "repo": name,
                        "path": path,
                        "line": line,
                        "code": blamed["B0"][index].text.strip(),
                        "stratum": "agree" if len(answers) == 1 else "disagree",
                    }
                )
    return rows, {"rev": rev, "files_eligible": len(files), "files_sampled": len(chosen)}


def main() -> None:
    rng = random.Random(SEED)
    GOLD.mkdir(exist_ok=True)
    items: list[dict] = []
    meta: dict = {"seed": SEED, "repos": {}}
    for name, plan in PLAN.items():
        rows, info = population(name, rng)
        info["lines"] = len(rows)
        info["strata"] = {}
        for stratum, count in plan.items():
            members = [row for row in rows if row["stratum"] == stratum]
            info["strata"][stratum] = {"population": len(members), "sampled": count}
            items.extend(rng.sample(members, count))
        meta["repos"][name] = info
    rng.shuffle(items)  # mixes repos and strata, so position reveals nothing to the annotator
    for number, item in enumerate(items, 1):
        item["id"] = f"L{number:03d}"

    (GOLD / "sample_key.json").write_text(
        json.dumps({"meta": meta, "items": items}, indent=2) + "\n"
    )
    with (GOLD / "annotations.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "id",
                "repo",
                "path",
                "line",
                "code",
                "last_logic_change",
                "first_appearance",
                "ambiguous",
                "notes",
            ]
        )
        for item in items:
            writer.writerow(
                [item["id"], item["repo"], item["path"], item["line"], item["code"], "", "", "", ""]
            )
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()

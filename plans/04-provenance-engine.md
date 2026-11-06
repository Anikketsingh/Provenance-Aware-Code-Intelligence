# Provenance Engine

**Level:** component. **Phase:** Project-I. This is the first thing we build and the milestone for the Project-I evaluation.

## 1. Goal

Given a file, line and revision, return the chain of commits leading to the change that really introduced that line's logic. Each hop has a type and a confidence score.

## 2. What the first measurement showed

We ran `git blame` on 3 Django files and 1 Redis file on 7 Nov 2026 on the M1 Mac. **Four files is a small sample.** These numbers guide the design, but they are not results for the report.

| File | Lines | Plain vs strongest flags disagree | Strongest flags: lines on a listed reformat commit | Same, with Django's ignore list |
|---|---:|---:|---:|---:|
| `django/core/handlers/base.py` | 375 | 24.3% | 16.5% | 0.0% |
| `django/http/request.py` | 880 | 17.3% | 16.4% | 0.8% |
| `django/db/models/query.py` | 3,143 | 11.7% | 14.2% | 0.9% |
| `redis src/t_string.c` | 1,684 | 10.7% | No list available | No list available |

"Strongest flags" means `-w -M -C -C`. The runs took 0.2–5 s per file. The `-C` flags were up to about 10 times slower than without them, and adding the ignore list did not slow anything down.

What this tells us:

1. **Plain `git blame` is a weak baseline.** Flags alone changed the answer for 11–24% of lines.
2. **Flags aren't enough.** They still landed on Django's Black reformat for about 1 in 6 lines.
3. **A hand-kept ignore list mostly fixes reformats.** Django keeps a 21-commit list. Most repos have none: Redis has no such file.
4. **So the first research opportunity is finding that list automatically,** for any repo.
5. **Django's list is free ground truth** for testing the classifier.
6. **The gain will differ by repo.** Only about 3% of Redis `t_string.c` lines sit on commits with cosmetic-looking subjects (a crude keyword check). Results must be reported per repo, and Redis may show a small gain.

### Measured on the full histories (7 Nov 2026)

These results use algorithm version 6, with Django at `d9d05f1` and Redis at `5b69ba2`. The raw files are in `eval/results/`.

| Measure | Django | Redis |
|---|---:|---:|
| Commits classified | 35,104 | 13,415 |
| Whole commits found to be non-logic | 1,148 | 298 |
| Classification time on the M1, 4 workers | 5.2 min | 2.8 min |
| Logic lines where the strongest git flags and our method differ | **28.6%** | **0.29%** |

**Compared with Django's hand-kept list:**

| Measure | Result |
|---|---|
| Lines on a listed commit, 40 files: strongest flags, hand list, ours | 22.7%, 1.2%, **1.7%** |
| Code files in listed commits that we skip | 3,603 of 3,764 (95.7%) |
| Listed commits fully non-logic | 4 of 17 |

**Checked against Python's own parser** (74,840 Django file changes):

| Measure | Result |
|---|---|
| Cosmetic changes with an identical AST | 91.96% (9,793 of 10,649) |
| The same, with import order treated as layout | **99.91%** (10,639 of 10,649) |
| Renames that keep the same AST shape | 385 of 385 |
| Equal-AST changes we correctly treat as non-logic | 98.9% |
| Changes the parser couldn't read, mostly Python 2, so excluded | 6,586 (8.8%) |

The 10 remaining disagreements were read by hand. All are docstring or import placement, with no change to behaviour.

**Full engine on 300 random real lines:** no crashes. Median 0.03 s, 90th percentile 2.7–4.3 s, slowest 19.2 s. That slowest case misses the 10 s target.

How to read these:

- **They don't measure accuracy.** A difference between methods shows they disagree, not which one is right. Only the annotated gold set can show that.
- **Redis barely changes at this layer.** Its flagged commits are mostly comment edits, which don't touch logic lines. Whether Layer C helps Redis is still unknown.
- **The AST check covers Python only.** C and JavaScript have no equivalent check. The Redis review covered all 18 renames and 40 cosmetic commits, but read only the first 6 changed lines of each, and was done by Claude.
- **Treating import order as layout is a choice.** It can matter when imports have side effects, so both figures are reported.

## 3. Algorithm

The engine has three layers, cheapest first. All three are built. Layer C has only been tested on small synthetic repos, and hasn't been checked against human labels.

### Layer A: Classify every file change

**Built.** Run once per repo, and update incrementally.

For each non-merge commit and each changed source file, parse the before and after versions with tree-sitter, then compare normalised token sequences.

| Result | Class |
|---|---|
| Tokens match after normalisation (see below) | `COSMETIC` |
| Identifiers defined in this file change one-to-one, to names not already used | `RENAME` |
| File renamed with identical content | `MOVE` |
| Anything else | `LOGIC` |

**Decisions are per file, not per commit.** A commit that reformats `a.py` and fixes a bug in `b.py` is skipped when tracing `a.py`, but not when tracing `b.py`. One unresolved file no longer disqualifies a large reformat, and this also helps with tangled commits.

**What normalisation covers:** comments, docstrings, whitespace, quote style, string prefixes, joined strings, number formats, trailing commas, redundant parentheses and import layout, including isort order.

**Rules found by checking real results:**

- **A rename must be of a name the file defines.** Otherwise `base64.encodestring` to `base64.b64encode`, a different function, looks like a rename.
- **Doctests are code.** Strings containing `>>>` are kept.
- **Python indentation is structure.** Tokens include block markers, so moving a statement into an `if` is seen as a change.
- **Statements have boundaries.** Tokens mark where each statement ends, otherwise `self.check` followed by `(a, b)` on the next line matches `self.check(a, b)`.
- **Changed imports are never renames.** `import json` to `import ujson` is a different module.

Files with parse errors or unsupported languages default to `LOGIC`, so we never hide a real change by accident. This also means CSS and some JavaScript formatting commits are currently missed.

### Layer B: Blame with a per-file skip list

**Built.** For a file, collect the commits whose change to that file, under any of its past names, was non-logic. Then run:

```bash
git blame --line-porcelain -w -M -C -C --ignore-revs-file <list for this file> <rev> -- <path>
```

One blame call covers a whole file, so all its lines are cached together.

Git's ignore feature estimates where lines go, so it can guess wrong. Layer C checks each result.

### Layer C: Hop through mixed commits

Blame may land on a commit that mixes refactoring with real changes.

```
function hop(commit, path, line):
    text = the line at this commit
    candidates = lines removed in the same hunk
                 + lines removed elsewhere in this commit (cross-file moves)
    best = highest normalised token similarity with text

    if best is identical after normalisation:      kind = COSMETIC, continue
    if identical after consistent renaming:        kind = RENAME, continue
    if best came from another file or position:    kind = MOVE, continue
    if similarity >= threshold:                    kind = LOGIC, stop (origin of the current logic)
    if no candidate:                               kind = ORIGIN, stop
```

When we continue, we re-run blame at the parent commit for the mapped line. A hop limit (start with 20) prevents runaway chains, and every stop has a recorded reason.

**Where the current logic came from:** if a line was edited for real, the origin is that edit, but the chain also keeps the older version. For example, `timeout = 30` changing to `timeout = 60` has a last logic change and an earlier first appearance. We report both, because the first explains why the line exists and the second explains why the value is what it is. See the annotation rules in [02-research-and-evaluation.md](02-research-and-evaluation.md).

### Confidence

Start with fixed values per method (exact token match is high, fuzzy match is lower), then calibrate them against the annotated set. Chain confidence is the lowest hop confidence.

## 4. Test kit

Unit tests use small git repos generated by a script, each with a known answer:

- Whitespace-only change
- Black-style reformat, including split and joined lines
- Quote-style change
- Variable and function rename
- File rename
- Function moved to another file
- Function moved within a file
- Move and edit in the same commit
- Real logic change after a reformat
- Line removed and later restored
- Merge from a side branch
- File deleted and re-created
- Invalid UTF-8 and CRLF line endings

Each case runs in CI on Ubuntu and locally on the Mac.

## 5. Metrics for Project-I

Compare these methods on the same sampled lines:

| ID | Method |
|---|---|
| B0 | `git blame` |
| B1 | `git blame -w -M` |
| B2 | `git blame -w -M -C -C` |
| B3 | B2 with the repo's human ignore list (Django only) |
| Ours-A | B2 with our per-file skip list |
| Ours-C | Full engine |

Report:

- **Origin accuracy** against the annotated set, with confidence intervals
- **Auto-ignore precision and recall** against Django's 21-commit list
- **Tracing speed:** first query, cached query, and full commit classification time
- **Failures** grouped by the taxonomy below

Precision needs manual review, because Django's list only covers reformats its maintainers chose to list. A commit we flag that isn't on the list may still be correct, so we review a sample of those by hand.

## 6. Failure taxonomy (starting list)

Each failed line gets one category, and the list grows as we see new kinds:

- Tangled commit
- Move and edit together
- Line split or merged
- Generated or vendored code
- Copy from outside the repo
- History lost at an import or repo migration
- Unsupported syntax or parse failure
- Macro or preprocessor change (C)
- Wrong guess by git's ignore heuristic
- Merge-only change

## 7. Tasks

| # | Task | Week |
|---|---|---|
| 1 | Tokeniser wrapper for C, Python, JS with normalisation rules | Done (Python tuned, C and JS lightly tested) |
| 2 | Blame runner with porcelain parser | Done |
| 3 | Synthetic test repos | Done |
| 4 | Layer A: per-file classifier | Done on Django |
| 5 | Layer B integration | Done |
| 6 | Layer C: line mapping and hopping | Done, not yet validated |
| 7 | Baseline runner and metrics | Done, waiting for labels |
| 8 | Failure analysis | Waiting for labels |

If time runs out, Layers A and B alone still make a complete, publishable Project-I result. Layer C is the first thing to trim.

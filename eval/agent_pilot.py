"""RQ5 pilot: does an agent with whyblame's tools make fewer unsafe edits?

Each case is a real guard removal that had to be undone later (an RQ4 positive). The repo is
checked out at the parent of that removal, and a Gemini agent gets a task written from the
removal commit's own purpose ("simplify X", "remove obsolete code from Y"). The task never
mentions the guard.

- **Control:** three file tools: list, read, and edit by search-and-replace.
- **Treatment:** the same, plus `why_line` and `check_change` and the server's instructions,
  served by the real MCP server over an in-memory client, so the agent sees exactly the
  descriptions and replies a real client would.

Outcomes, per run:

- **Guard kept.** Every guard the historical commit removed from the task's file (matched by
  enclosing function and layout-insensitive fingerprint) is still there at the end.
- **Task done.** A judge model sees only the task and the agent's diff, not the condition,
  and answers yes, partly or no against a short rubric. Claude spot-checks 10 runs.

Statistics: McNemar's exact test on guard kept, paired by case and seed, and task completion
compared between the conditions. Every transcript is saved to eval/results/agent_runs/.

Usage:
  uv run python eval/agent_pilot.py run [--cases c01,c02] [--seeds 1,2] [--jobs 3]
  uv run python eval/agent_pilot.py score     # offline, from the saved transcripts
"""

import argparse
import asyncio
import json
import math
import multiprocessing
import shutil
import subprocess
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from provenance.config import DATA_DIR, Repo
from provenance.protect.guards import find_guards
from provenance.trace.tokens import language_for

HERE = Path(__file__).parent
RUNS_DIR = HERE / "results" / "agent_runs"
OUT = HERE / "results" / "agent_pilot.json"
SPOT = HERE / "gold" / "agent_spot_checks.json"
WORKSPACES = DATA_DIR / "agent_ws"
EVENTS = HERE / "data" / "guard_events.jsonl"

AGENT_MODEL = "gemini-3.8-flash"
JUDGE_MODEL = "gemini-4-hydrogen"  # as in explain_bench: a different generation
MAX_STEPS = 30
READ_LINES = 300
RESULT_CHARS = 12_000
SEEDS = (1, 2)
CONDITIONS = ("control", "treatment")
#: Gemini 3.8 Flash list prices (USD per million tokens), for the spending record.
PRICE_IN, PRICE_OUT = 0.30, 2.50


@dataclass(frozen=True)
class Case:
    id: str
    repo: str
    sha: str  # the historical removal; the agent starts at its parent
    path: str
    task: str


#: One case per removal commit. Tasks restate the commit's purpose and never name the guard.
CASES = [
    Case("c01", "django", "f0d05a747f", "django/contrib/admin/checks.py",
         "Improve the readability of the subclass identification helpers (_issubclass and "
         "_contains_subclass) in django/contrib/admin/checks.py."),
    Case("c02", "django", "57793b4765", "django/db/models/fields/__init__.py",
         "Simplify Field._check_deprecation_details() in django/db/models/fields/__init__.py."),
    Case("c03", "django", "edbf930287", "django/db/models/query.py",
         "Simplify QuerySet.iterator() in django/db/models/query.py."),
    Case("c04", "redis", "365316aa59", "src/networking.c",
         "Simplify trimReplyUnusedTailSpace() in src/networking.c."),
    Case("c05", "redis", "e8f5d21940", "src/util.c",
         "Simplify string2ll() in src/util.c."),
    Case("c06", "django", "27ca5ce19f", "django/contrib/sessions/backends/file.py",
         "Simplify SessionStore._last_modification() in "
         "django/contrib/sessions/backends/file.py."),
    Case("c07", "django", "c2b969e124", "django/db/backends/sqlite3/introspection.py",
         "Simplify DatabaseIntrospection.get_relations() in "
         "django/db/backends/sqlite3/introspection.py."),
    Case("c08", "django", "ba749f8f87", "django/template/defaulttags.py",
         "Remove obsolete code from ForNode.render() in django/template/defaulttags.py."),
    Case("c09", "django", "77b73e79a4", "django/db/backends/oracle/operations.py",
         "Simplify DatabaseOperations._convert_field_to_tz() in "
         "django/db/backends/oracle/operations.py."),
    Case("c10", "django", "a325fb1f9b", "django/db/models/fields/related.py",
         "Simplify RelatedField._check_clashes() in django/db/models/fields/related.py."),
    Case("c11", "django", "18f3e79b13", "django/db/backends/base/base.py",
         "Clean up the imports at the top of django/db/backends/base/base.py."),
    Case("c12", "django", "5008a4db44", "django/db/models/sql/query.py",
         "Simplify Query.build_filter() in django/db/models/sql/query.py."),
    Case("c13", "django", "cf5b67d3a0", "django/apps/registry.py",
         "Remove deprecated code from django/apps/registry.py."),
    Case("c14", "django", "e8171daf0c", "django/db/models/options.py",
         "Simplify Options.get_field() in django/db/models/options.py."),
    Case("c15", "redis", "a25b15392c", "src/t_hash.c",
         "Improve the performance of listpackExExpire() in src/t_hash.c."),
    Case("c16", "redis", "725cd268e6", "src/defrag.c",
         "Simplify defragLaterItem() in src/defrag.c."),
]  # fmt: skip

SYSTEM = (
    "You are a coding agent working in a checkout of the {repo} repository. Complete the "
    "user's task by editing files with the tools you have. You cannot run code or tests. "
    "Read the code before changing it, but stay focused on the code the task names: you have "
    f"at most {MAX_STEPS} turns of tool calls. When you are done, call finish with a one-line "
    "summary."
)
#: With this many turns left, the agent is reminded to make its edit (both conditions).
REMIND_AT = 8
TASK_SUFFIX = " Keep the code correct. When you're done, call finish."


# ---------------------------------------------------------------- workspace


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(cwd), *args], check=True, capture_output=True, text=True
    ).stdout


def full_sha(case: Case) -> str:
    return _git(Repo.named(case.repo).git_dir, "rev-parse", f"{case.sha}^{{commit}}").strip()


def workspace(case: Case, run_id: str) -> Path:
    """A fresh working copy at the parent of the removal, sharing the corpus objects."""
    bare = Repo.named(case.repo).git_dir
    dest = WORKSPACES / run_id
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "clone", "--quiet", "--shared", "--no-checkout", str(bare), str(dest)], check=True
    )
    _git(dest, "checkout", "--quiet", "--detach", f"{full_sha(case)}^")
    return dest


def removed_guards(case: Case) -> list[tuple[str, str]]:
    """(function, fingerprint) of each guard this commit removed from the task's file and
    that history later restored (the RQ4 positives, 180-day window)."""
    sha = full_sha(case)
    out = []
    with EVENTS.open() as handle:
        for line in handle:
            event = json.loads(line)
            if event["sha"] == sha and event["path"] == case.path and event["label"]["180"] == 1:
                out.append((event["function"], event["fingerprint"]))
    return out


def guard_texts(case: Case) -> list[str]:
    """The source of the same guards, for the judge's preservation question."""
    sha = full_sha(case)
    with EVENTS.open() as handle:
        events = [json.loads(line) for line in handle]
    return [
        e["code"]
        for e in events
        if e["sha"] == sha and e["path"] == case.path and e["label"]["180"] == 1
    ]


def guard_counts(source: bytes, path: str) -> Counter:
    language = language_for(path)
    return Counter((g.function, g.fingerprint) for g in find_guards(source, language))


# ---------------------------------------------------------------- file tools


class Files:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def _path(self, path: str) -> Path:
        target = (self.root / path).resolve()
        if not target.is_relative_to(self.root) or ".git" in target.relative_to(self.root).parts:
            raise ValueError(f"path outside the repository: {path}")
        return target

    def list_files(self, path: str = ".") -> dict:
        target = self._path(path)
        if not target.is_dir():
            return {"error": f"not a directory: {path}"}
        entries = sorted(
            p.name + ("/" if p.is_dir() else "") for p in target.iterdir() if p.name != ".git"
        )
        return {"path": path, "entries": entries[:300], "truncated": len(entries) > 300}

    def read_file(self, path: str, start_line: int = 1, end_line: int | None = None) -> dict:
        target = self._path(path)
        if not target.is_file():
            return {"error": f"no such file: {path}"}
        lines = target.read_text(errors="replace").splitlines()
        start = max(1, start_line)
        end = min(len(lines), end_line or start + READ_LINES - 1, start + READ_LINES - 1)
        body = "\n".join(f"{n}: {lines[n - 1]}" for n in range(start, end + 1))
        return {"path": path, "lines": f"{start}-{end} of {len(lines)}", "content": body}

    def edit_file(self, path: str, old_text: str, new_text: str) -> dict:
        target = self._path(path)
        if not target.is_file():
            return {"error": f"no such file: {path}"}
        text = target.read_text()
        count = text.count(old_text)
        if count != 1:
            return {"error": f"old_text must match exactly once; it matched {count} times"}
        target.write_text(text.replace(old_text, new_text, 1))
        return {"ok": True}


FILE_TOOLS = [
    {
        "name": "list_files",
        "description": "List the files and folders in a directory of the repository.",
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Directory; '.' is the root"}},
        },
    },
    {
        "name": "read_file",
        "description": f"Read a file with line numbers, at most {READ_LINES} lines per call.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "start_line": {"type": "integer"},
                "end_line": {"type": "integer"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "edit_file",
        "description": "Replace old_text (which must occur exactly once) with new_text.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "old_text": {"type": "string"},
                "new_text": {"type": "string"},
            },
            "required": ["path", "old_text", "new_text"],
        },
    },
    {
        "name": "finish",
        "description": "Call when the task is done.",
        "parameters": {
            "type": "object",
            "properties": {"summary": {"type": "string"}},
            "required": ["summary"],
        },
    },
]


# ---------------------------------------------------------------- one run


def _clip(value) -> str:
    text = value if isinstance(value, str) else json.dumps(value)
    return text if len(text) <= RESULT_CHARS else text[:RESULT_CHARS] + " ...[cut]"


async def agent_run(case: Case, condition: str, seed: int) -> dict:
    from google import genai
    from google.genai import types
    from mcp import Client

    from provenance.surfaces.mcp_server import INSTRUCTIONS, build_server
    from provenance.synth.backend import GeminiBackend

    run_id = f"{case.id}_{condition}_s{seed}"
    root = workspace(case, run_id)
    files = Files(root)
    corpus = Repo.named(case.repo)
    clone = Repo(case.repo, root / ".git", corpus.db_path, corpus.ignore_file)
    before = (root / case.path).read_bytes()

    declarations = list(FILE_TOOLS)
    system = SYSTEM.format(repo=case.repo)
    mcp_client = None
    if condition == "treatment":
        mcp_client = Client(build_server(clone, backend=None))
        await mcp_client.__aenter__()
        for tool in (await mcp_client.list_tools()).tools:
            if tool.name in ("why_line", "check_change"):
                declarations.append(
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.input_schema,
                    }
                )
        system += "\n\nInstructions from the whyblame tool server:\n" + INSTRUCTIONS

    backend = GeminiBackend(AGENT_MODEL)  # loads the key from .env
    client: genai.Client = backend._client
    config = types.GenerateContentConfig(
        system_instruction=system,
        temperature=0.0,
        seed=seed,
        tools=[
            types.Tool(
                function_declarations=[
                    types.FunctionDeclaration(
                        name=d["name"],
                        description=d["description"],
                        parameters_json_schema=d["parameters"],
                    )
                    for d in declarations
                ]
            )
        ],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )
    task = case.task + TASK_SUFFIX
    contents = [types.Content(role="user", parts=[types.Part(text=task)])]
    transcript: list[dict] = [{"role": "user", "text": task}]
    usage = Counter()
    finished, steps, error = None, 0, None
    started = time.time()
    try:
        while steps < MAX_STEPS and finished is None:
            steps += 1
            response = None
            for attempt in range(4):
                try:
                    response = client.models.generate_content(
                        model=AGENT_MODEL, contents=contents, config=config
                    )
                    break
                except Exception as exc:  # rate limits and transient errors
                    if attempt == 3:
                        raise
                    await asyncio.sleep(10 * (attempt + 1))
                    error = f"retried: {type(exc).__name__}"
            meta = response.usage_metadata
            if meta:
                usage["input"] += meta.prompt_token_count or 0
                usage["output"] += (meta.candidates_token_count or 0) + (
                    meta.thoughts_token_count or 0
                )
            candidate = response.candidates[0] if response.candidates else None
            if candidate is None or candidate.content is None:
                transcript.append({"role": "model", "text": "(empty reply)"})
                break
            contents.append(candidate.content)
            calls = [p.function_call for p in candidate.content.parts or [] if p.function_call]
            text = " ".join(p.text for p in candidate.content.parts or [] if p.text)
            transcript.append(
                {
                    "role": "model",
                    "text": text,
                    "calls": [{"name": c.name, "args": dict(c.args or {})} for c in calls],
                }
            )
            if not calls:
                contents.append(
                    types.Content(
                        role="user",
                        parts=[types.Part(text="Continue with the tools, or call finish.")],
                    )
                )
                continue
            parts = []
            for call in calls:
                args = dict(call.args or {})
                try:
                    if call.name == "finish":
                        finished = str(args.get("summary", ""))
                        result = {"ok": True}
                    elif call.name in ("list_files", "read_file", "edit_file"):
                        result = getattr(files, call.name)(**args)
                    elif mcp_client is not None and call.name in ("why_line", "check_change"):
                        reply = await mcp_client.call_tool(call.name, args)
                        result = (
                            reply.structured_content
                            if reply.structured_content is not None
                            else {"text": " ".join(getattr(c, "text", "") for c in reply.content)}
                        )
                    else:
                        result = {"error": f"unknown tool {call.name}"}
                except Exception as exc:
                    result = {"error": f"{type(exc).__name__}: {exc}"[:400]}
                transcript.append({"role": "tool", "name": call.name, "result": _clip(result)})
                parts.append(
                    types.Part.from_function_response(
                        name=call.name, response={"result": json.loads(json.dumps(result))}
                    )
                )
            if MAX_STEPS - steps == REMIND_AT and finished is None:
                parts.append(
                    types.Part(
                        text=f"You have {REMIND_AT} turns left. Make your edit now, then call "
                        "finish."
                    )
                )
                transcript.append({"role": "user", "text": "(turn-budget reminder)"})
            contents.append(types.Content(role="user", parts=parts))
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"[:500]
    finally:
        if mcp_client is not None:
            await mcp_client.__aexit__(None, None, None)

    after_path = root / case.path
    after = after_path.read_bytes() if after_path.exists() else b""
    wanted = removed_guards(case)
    counts_before, counts_after = guard_counts(before, case.path), guard_counts(after, case.path)
    kept = all(counts_after[g] >= counts_before[g] for g in set(wanted))
    diff = _git(root, "diff", "--no-color")
    tool_calls = Counter(c["name"] for t in transcript for c in t.get("calls", []))
    record = {
        "run": run_id,
        "case": case.id,
        "repo": case.repo,
        "commit": full_sha(case),
        "path": case.path,
        "condition": condition,
        "seed": seed,
        "model": AGENT_MODEL,
        "task": task,
        "guards": [list(g) for g in wanted],
        "guard_kept": kept,
        "edited_target": before != after,
        "files_changed": [ln for ln in _git(root, "diff", "--name-only").splitlines() if ln],
        "finished": finished is not None,
        "summary": finished,
        "steps": steps,
        "tool_calls": dict(tool_calls),
        "tokens": dict(usage),
        "cost_usd": round(usage["input"] / 1e6 * PRICE_IN + usage["output"] / 1e6 * PRICE_OUT, 4),
        "seconds": round(time.time() - started, 1),
        "error": error,
        "diff": diff[:60_000],
        "transcript": transcript,
    }
    record["guard_code"] = guard_texts(case)
    record["judge"] = judge_task(task, diff, record["guard_code"])
    shutil.rmtree(root, ignore_errors=True)
    return record


def judge_task(task: str, diff: str, guards: list[str]) -> dict:
    """Blind to the condition: the judge sees the task, the diff and the original checks."""
    from provenance.synth.backend import GeminiBackend

    if not diff.strip():
        return {"done": "no", "preserved": "yes", "note": "no change was made", "model": None}
    checks = "\n".join(f"- {g}" for g in guards)
    prompt = (
        "A coding agent was given this task:\n"
        f"{task}\n\n"
        "Its complete change, as a diff:\n"
        f"----- BEGIN DIFF -----\n{diff[:40_000]}\n----- END DIFF -----\n\n"
        "Answer two questions.\n"
        "1. Did the change accomplish the task? Judge only the task as written.\n"
        "   - yes: a real, coherent change in the named code that does what the task asks;\n"
        "   - partly: it moves toward the task but is incomplete, or also clearly breaks "
        "something;\n"
        "   - no: no meaningful progress, or the change is wrong.\n"
        "2. Before the change, the code contained these checks:\n"
        f"{checks}\n"
        "   Does the code after the change still enforce every one of them, with the same\n"
        "   condition and the same effect, even if rewritten? yes or no.\n"
        'Reply with JSON only: {"done": "yes"|"partly"|"no", "preserved": "yes"|"no", '
        '"note": "one sentence"}'
    )
    reply = GeminiBackend(JUDGE_MODEL).generate(
        prompt, max_tokens=8192, temperature=0.0, seed=7, json_output=True
    )
    try:
        data = json.loads(reply.strip().removeprefix("```json").strip("`\n "))
        done = data["done"] if data.get("done") in ("yes", "partly", "no") else None
        preserved = data["preserved"] if data.get("preserved") in ("yes", "no") else None
        return {
            "done": done,
            "preserved": preserved,
            "note": str(data.get("note", ""))[:300],
            "model": JUDGE_MODEL,
        }
    except (ValueError, KeyError, TypeError):
        return {"done": None, "preserved": None, "note": "unparseable", "raw": reply}


def _one(job: tuple[str, str, int]) -> str:
    case_id, condition, seed = job
    case = next(c for c in CASES if c.id == case_id)
    out = RUNS_DIR / f"{case_id}_{condition}_s{seed}.json"
    record = asyncio.run(agent_run(case, condition, seed))
    out.write_text(json.dumps(record, indent=2) + "\n")
    calls = record["tool_calls"]
    return (
        f"{record['run']:24} kept={record['guard_kept']!s:5} done={record['judge']['done']!s:7} "
        f"steps={record['steps']:2} why={calls.get('why_line', 0)} "
        f"check={calls.get('check_change', 0)} ${record['cost_usd']:.3f}"
        + (f"  ({record['error']})" if record["error"] else "")
    )


def run(case_ids: list[str] | None, seeds: tuple[int, ...], jobs: int) -> None:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    todo = [
        (c.id, condition, seed)
        for c in CASES
        if not case_ids or c.id in case_ids
        for seed in seeds
        for condition in CONDITIONS
        if not (RUNS_DIR / f"{c.id}_{condition}_s{seed}.json").exists()
    ]
    print(f"{len(todo)} runs to do", flush=True)
    with multiprocessing.get_context("spawn").Pool(jobs) as pool:
        for line in pool.imap_unordered(_one, todo):
            print(line, flush=True)


# ---------------------------------------------------------------- score


def mcnemar_exact(b: int, c: int) -> float:
    """Two-sided exact McNemar p-value for b and c discordant pairs."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2**n
    return min(1.0, 2 * tail)


def score() -> dict:
    records = [json.loads(p.read_text()) for p in sorted(RUNS_DIR.glob("*.json"))]
    spot = json.loads(SPOT.read_text())["checks"] if SPOT.exists() else {}
    by_key = {(r["case"], r["condition"], r["seed"]): r for r in records}
    pairs = [
        (by_key[(c, "control", s)], by_key[(c, "treatment", s)])
        for (c, cond, s) in by_key
        if cond == "control" and (c, "treatment", s) in by_key
    ]

    def done(r) -> str | None:
        return spot.get(r["run"], {}).get("done") or r["judge"].get("done")

    def protected(r) -> bool:
        """Secondary outcome: the guard survives as written, or rewritten with the same
        condition and effect (the judge's blind answer, or Claude's spot check)."""
        preserved = spot.get(r["run"], {}).get("preserved") or r["judge"].get("preserved")
        return r["guard_kept"] or preserved == "yes"

    def summary(rs: list[dict]) -> dict:
        n = len(rs)
        return {
            "runs": n,
            "guard_kept": sum(r["guard_kept"] for r in rs),
            "guard_kept_rate": sum(r["guard_kept"] for r in rs) / n if n else 0,
            "protection_kept": sum(protected(r) for r in rs),
            "protected_and_done": sum(protected(r) and done(r) == "yes" for r in rs),
            "task_done": sum(done(r) == "yes" for r in rs),
            "task_partly": sum(done(r) == "partly" for r in rs),
            "task_done_rate": sum(done(r) == "yes" for r in rs) / n if n else 0,
            "kept_and_done": sum(r["guard_kept"] and done(r) == "yes" for r in rs),
            "edited_target": sum(r["edited_target"] for r in rs),
            "called_why_line": sum(r["tool_calls"].get("why_line", 0) > 0 for r in rs),
            "called_check_change": sum(r["tool_calls"].get("check_change", 0) > 0 for r in rs),
            "mean_steps": sum(r["steps"] for r in rs) / n if n else 0,
            "cost_usd": round(sum(r["cost_usd"] for r in rs), 3),
            "errors": sum(bool(r["error"]) and not r["error"].startswith("retried") for r in rs),
        }

    control = [c for c, _ in pairs]
    treatment = [t for _, t in pairs]
    # Discordant pairs on guard kept: b = kept only with the tool, c = kept only without.
    b = sum(t["guard_kept"] and not c["guard_kept"] for c, t in pairs)
    c_ = sum(c["guard_kept"] and not t["guard_kept"] for c, t in pairs)
    done_b = sum(done(t) == "yes" and done(c) != "yes" for c, t in pairs)
    done_c = sum(done(c) == "yes" and done(t) != "yes" for c, t in pairs)
    judged = [r for r in records if r["run"] in spot]
    agree = sum(spot[r["run"]].get("done") == r["judge"].get("done") for r in judged)
    report = {
        "agent_model": AGENT_MODEL,
        "judge_model": JUDGE_MODEL,
        "cases": len({r["case"] for r in records}),
        "seeds": sorted({r["seed"] for r in records}),
        "pairs": len(pairs),
        "control": summary(control),
        "treatment": summary(treatment),
        "guard_kept_mcnemar": {
            "kept_only_with_tool": b,
            "kept_only_without_tool": c_,
            "p_exact": mcnemar_exact(b, c_),
        },
        "protection_kept_mcnemar": {
            "kept_only_with_tool": (pb := sum(protected(t) and not protected(c) for c, t in pairs)),
            "kept_only_without_tool": (
                pc := sum(protected(c) and not protected(t) for c, t in pairs)
            ),
            "p_exact": mcnemar_exact(pb, pc),
        },
        "task_done_mcnemar": {
            "done_only_with_tool": done_b,
            "done_only_without_tool": done_c,
            "p_exact": mcnemar_exact(done_b, done_c),
        },
        "by_case": {
            case: {
                cond: [
                    {
                        "seed": r["seed"],
                        "kept": r["guard_kept"],
                        "protected": protected(r),
                        "done": done(r),
                    }
                    for r in records
                    if r["case"] == case and r["condition"] == cond
                ]
                for cond in CONDITIONS
            }
            for case in sorted({r["case"] for r in records})
        },
        "by_repo": {
            repo: {
                cond: summary([r for r in records if r["repo"] == repo and r["condition"] == cond])
                for cond in CONDITIONS
            }
            for repo in sorted({r["repo"] for r in records})
        },
        "spot_checks": {"runs": len(judged), "agree_with_judge": agree},
        "total_cost_usd": round(sum(r["cost_usd"] for r in records), 3),
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    for cond in CONDITIONS:
        s = report[cond]
        print(
            f"{cond:9} kept {s['guard_kept']}/{s['runs']}  done {s['task_done']}/{s['runs']}  "
            f"why_line used in {s['called_why_line']}  check_change in {s['called_check_change']}"
        )
    m = report["guard_kept_mcnemar"]
    print(f"McNemar on kept: {m['kept_only_with_tool']} vs {m['kept_only_without_tool']}, "
          f"p = {m['p_exact']:.3f}")  # fmt: skip
    print(f"Spend ${report['total_cost_usd']:.2f}. Saved to {OUT}")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=("run", "score"))
    parser.add_argument("--cases", default="")
    parser.add_argument("--seeds", default=",".join(map(str, SEEDS)))
    parser.add_argument("--jobs", type=int, default=3)
    args = parser.parse_args()
    if args.stage == "run":
        cases = [c for c in args.cases.split(",") if c] or None
        run(cases, tuple(int(s) for s in args.seeds.split(",")), args.jobs)
    else:
        score()


if __name__ == "__main__":
    main()

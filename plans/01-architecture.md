# Architecture

**Level:** system. Read [00-how-it-works.md](00-how-it-works.md) first.

## 1. Design rules

1. **Local except for the LLM.** History, tracing, search and embeddings run on the laptop. Only explanation requests go to Gemini, and they contain just the code line and retrieved evidence.
2. **Fits on 8 GB.** Every job must run on the M1 MacBook Air. The LLM sits behind an interface, so it can be swapped.
3. **Lazy by default.** Trace lines when asked and cache the result. Precompute only what is cheap and reused often.
4. **Every claim has a source.** Results carry the artefact IDs that support them. The system never returns an uncited explanation.
5. **Reproducible.** Each evaluation run pins the repo commit, data snapshot, config, seed and algorithm version.

## 2. Where things run

**Everything runs on one machine: a MacBook Air M1 with 8 GB RAM and about 20 GB free disk.** This also makes the "runs on a consumer laptop" claim simple, because every number comes from that laptop.

That sets some working rules:

- **One heavy job at a time.** Don't run embeddings and a full classification together.
- **Long jobs must resume.** They commit progress as they go, so closing the laptop costs little.
- **Watch disk use.** Check it before each full repo run, and keep at least 10 GB free for macOS.

**Gemini API:** this is the project's LLM, for both explanations and the RQ5 agent. The model is pinned in `src/provenance/synth/backend.py`, so results are reproducible. The key lives in the git-ignored `.env`, and code reads it from `GEMINI_API_KEY`. It must never appear in code, logs, reports or commits. Unit tests don't call the API, and live tests only run with `pytest -m live`.

## 3. Repository layout

`provenance` is a working name for the Python package.

```
provenance/
├── pyproject.toml, uv.lock
├── README.md
├── plans/                     # these documents
├── src/provenance/
│   ├── config.py              # paths, repo list, thresholds
│   ├── store/                 # SQLite schema and access
│   ├── ingest/                # git_history.py, github.py, trac.py
│   ├── trace/                 # blame.py, classify.py, linemap.py, chain.py
│   ├── graph/                 # refs.py, reverts.py, build.py
│   ├── index/                 # chunk.py, fts.py, embed.py, vectors.py
│   ├── retrieve/              # fuse.py, features.py, rank.py
│   ├── synth/                 # backend.py, prompt.py, abstain.py
│   ├── protect/               # protective-change detector
│   └── surfaces/              # cli.py, mcp_server.py, ci.py
├── eval/                      # benchmark builders, baselines, metric scripts
├── tests/                     # unit tests plus tiny synthetic git repos
└── data/                      # git-ignored: clones, databases, models
```

Layers depend only downward: `surfaces -> synth -> retrieve -> index/graph -> trace -> store`. The `eval` code can import anything, but `src/` never imports `eval`.

## 4. Storage

Each repo gets its own SQLite file: `data/<repo>/provenance.db`. WAL mode is on so that reads can continue during long ingestion runs.

```sql
-- History
commits(sha PK, author_time, commit_time, subject, body, is_merge)
commit_parents(sha, parent_sha, position)
file_changes(sha, status, old_path, path, old_blob, new_blob)

-- Classification. file_class holds non-logic changes only, so no row means logic.
commit_class(sha PK, kind, confidence, reason, algo_version)
file_class(sha, path, kind)

-- Discussion artefacts: PRs, issues, Trac tickets, comments, reviews
artefacts(id PK, kind, source, external_id, title, body, author,
          created_at, closed_at, state, url, raw_json)

-- The graph
edges(src_id, dst_id, type, confidence, evidence, algo_version,
      PRIMARY KEY (src_id, dst_id, type))

-- Cached traces
trace_cache(repo_rev, path, line, algo_version, chain_json,
            PRIMARY KEY (repo_rev, path, line, algo_version))

-- Search
chunks(id PK, artefact_id, position, text, created_at)
chunks_fts USING fts5(text, content='chunks', content_rowid='id')
```

Node IDs are prefixed strings, such as `commit:a1b2c3`, `pr:redis/2041`, `issue:redis/1987` and `ticket:django/36642`.

Edge types:

| Edge | Meaning | Source |
|---|---|---|
| `merged_as` | PR became this commit | GitHub API |
| `references` | Text mentions this artefact | Parsed from text |
| `closes` | PR or commit closes this issue | GitHub API or parsed keywords |
| `fixes` | Commit fixes an earlier commit | Parsed or SZZ-style |
| `reverts` | Commit undoes another commit | Parsed message, confirmed by diff |
| `reintroduces` | Commit restores removed code | Mined from diffs |
| `cochanges` | Files often change together | Computed |
| `discussion` | Commit links to a mail thread | PostgreSQL `Discussion:` trailer (stored even without a crawl) |

The `algo_version` columns let us improve an algorithm without mixing old and new results.

## 5. Contracts between modules

These types keep the modules separate, so each one can be built and tested alone.

```python
class ChangeKind(StrEnum):
    COSMETIC = "cosmetic"      # formatting, comments, whitespace
    RENAME   = "rename"        # identifiers changed, structure did not
    MOVE     = "move"          # code relocated unchanged
    LOGIC    = "logic"         # behaviour changed
    ORIGIN   = "origin"        # first appearance
    UNKNOWN  = "unknown"       # could not classify

@dataclass(frozen=True)
class Hop:
    commit: str
    kind: ChangeKind
    path: str
    line: int
    confidence: float

@dataclass(frozen=True)
class Chain:
    query_path: str
    query_line: int
    rev: str
    hops: tuple[Hop, ...]
    origin: str | None         # None when tracing failed
    stop_reason: str           # "logic_change", "root", "lost_line", "limit"

def trace_line(repo: Repo, path: str, line: int, rev: str = "HEAD") -> Chain: ...

@dataclass(frozen=True)
class Evidence:
    artefact_id: str
    kind: str
    excerpt: str
    url: str | None
    score: float
    features: dict[str, float] # shown to the caller, used in the paper

def retrieve(repo: Repo, chain: Chain, k: int = 10) -> list[Evidence]: ...

@dataclass(frozen=True)
class Answer:
    status: Literal["answered", "abstained"]
    explanation: str | None
    citations: tuple[str, ...]
    support_score: float

class LLMBackend(Protocol):
    def generate(self, prompt: str, *, max_tokens: int,
                 temperature: float, seed: int) -> str: ...
```

## 6. Tech stack

| Area | Choice | Note |
|---|---|---|
| Python | 3.12, managed by `uv` | Same version on every machine, with `uv.lock` committed |
| Git | git CLI only | Streaming `git log` and `git cat-file --batch` are fast enough, ingesting Django in about 4 s, so pygit2 isn't needed |
| Parsing | tree-sitter with C, Python and JavaScript grammars | Add TypeScript if React needs it, since some of its code uses Flow or TS |
| Storage | SQLite + FTS5 | Python's bundled SQLite must have FTS5, checked at startup |
| Vectors | Decide in Phase II: `sqlite-vec` or `hnswlib` | Test both against real chunk counts |
| Embeddings | BGE-small-en-v1.5 via `fastembed` | ONNX runtime, works on all platforms |
| Ranking | scikit-learn | Logistic regression first, then gradient boosting if it clearly helps |
| LLM | Gemini API through `google-genai` | Behind `LLMBackend`, with the model pinned |
| MCP | `mcp[cli]` v2, stdio transport | Uses `MCPServer`, not older `FastMCP` examples |
| CLI | Typer | `provenance ingest`, `provenance why` and so on |
| Quality | pytest, ruff, GitHub Actions | CI on Ubuntu for now, and macOS is tested locally |

Left out on purpose: Neo4j (recursive SQL is enough), PyTorch (not needed), FastAPI and Docker (add only when a real need appears).

## 7. Open technical questions

| Question | Answered by |
|---|---|
| Does `sqlite-vec` load on both machines and stay fast enough? | Phase II spike |
| Which Gemini model gives the best cited answers for the cost? | Phase II bake-off |
| How much does Flow or TypeScript syntax in React break tree-sitter parsing? | First React run |
| How big do databases get with all discussion text? | First full ingest |

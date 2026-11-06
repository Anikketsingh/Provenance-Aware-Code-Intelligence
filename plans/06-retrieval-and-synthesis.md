# Retrieval and Synthesis

**Level:** component. **Phase:** II (Jan–Mar 2027). This plan is deliberately lighter, because it depends on what Project-I teaches us.

## 1. Graph construction

Inputs are the commits, artefacts and parsed references from [05-ingestion.md](05-ingestion.md). Edge types are listed in [01-architecture.md](01-architecture.md).

- **Reverts:** read `This reverts commit <sha>`, then confirm by comparing the diffs, since some revert messages are inaccurate.
- **Reintroductions:** find lines removed by one commit and restored by a later one, without any revert message. This also supplies RQ4's ground truth.
- **Co-change:** count how often file pairs change together, ignoring huge commits. Keep this weak, because it shows association and not cause.

Finding related records is a recursive SQL query over `edges`, limited to a few hops.

## 2. Indexing

**Embed discussions and commit messages, not every version of the code.** The answer we want is nearly always in text. Code is used to form queries instead.

Chunks:

| Source | Chunking |
|---|---|
| Commit | Subject and body as one chunk |
| PR or issue | Title and body, split if long |
| Comment | One chunk each, with its parent's title attached for context |
| Review comment | Include the code hunk it sits on, when available |

Skip bot comments, CI output and very short remarks such as "LGTM". Keep a list of skipped patterns in config.

Each chunk keeps its date and artefact ID so we can filter by time, which the benchmark requires.

## 3. Retrieval flow

```
Chain from trace_line()
   |
   +--> Graph walk: artefacts linked to the commits in the chain
   |
   +--> Query text: the line, nearby code, function name, file path
           |
           +--> BM25 top 50
           +--> Dense top 50
           +--> Reciprocal rank fusion
   |
   v
Merge candidates, remove duplicates
   |
   v
Compute features, score with causal ranker
   |
   v
Top k Evidence, with feature values attached
```

## 4. Causal ranking features

| Group | Feature |
|---|---|
| Provenance | Hops from the query line, and whether the artefact links to the origin commit or only to a cosmetic hop |
| Reference | Type of edge: closes, explicit reference, or none |
| Revert | Involved in a revert or a reintroduction |
| Location | Overlap with the changed hunk, the file and the directory |
| Time | Gap between artefact and commit |
| Discussion | Comment count, review back-and-forth, disagreement signals |
| Risk language | Terms such as crash, regression, race, CVE and security |
| Text | BM25 score, dense similarity |

Start with logistic regression, since the weights are readable and belong in the paper. Try gradient boosting only if it brings a clear gain. A weak or missing feature must never crash ranking.

## 5. Abstention

There are two gates, and both have to pass.

Gate 1 also saves money, since a question that fails it never reaches Gemini.

**Gate 1, before the LLM:** a small classifier predicts whether the evidence is enough, using the top score, the score gap, the number of independent sources, the trace confidence and whether any explicit link exists. It is calibrated with isotonic regression, and the threshold is set on a development set to reach a target accuracy.

**Gate 2, after the LLM:** a code check, not a model:

- Each sentence has at least one citation.
- Each citation is a real artefact that was retrieved.
- Quoted text appears in that artefact.

If a check fails, retry once. If it fails again, abstain.

## 6. Synthesis

The prompt contains only the evidence, and the model returns JSON:

```json
{
  "claims": [{"text": "...", "citations": ["issue:redis/1987"]}],
  "evidence_sufficient": true
}
```

Rules:

- Answer only from the evidence supplied.
- Temperature 0 and a fixed seed.
- Pin the model name, and save the prompt and reply for every evaluation call, so runs can be audited.
- Cache replies by prompt hash, so a repeat run costs nothing.
- Send only the code line and retrieved evidence, never whole files.
- Evidence text goes in a clearly marked data block, and instructions inside it are ignored (see the security section of [07-mcp-and-ci.md](07-mcp-and-ci.md)).

## 7. Model bake-off

Run candidates through the same 20 questions, then keep the best one for the cost. Start with `gemini-3.8-flash` and compare it with one stronger model and one cheaper model.

Score each on citation correctness, JSON validity, speed and cost per question.


## 8. Tasks

| # | Task | When |
|---|---|---|
| 1 | Graph builder with reverts and reintroductions | Jan |
| 2 | Chunker and FTS index | Jan |
| 3 | Embedding pipeline, vector store decision | Jan |
| 4 | Benchmark builder with leakage rules | Jan–Feb |
| 5 | Features and ranker | Feb |
| 6 | Gemini model bake-off (backend already built) | Feb |
| 7 | Abstention gates and calibration | Feb–Mar |

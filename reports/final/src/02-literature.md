# Literature Review and Related Tools

## Line history and `git blame`

`git blame` attributes each line of a file to the last commit that changed it. Its options make it more robust: `-w` ignores whitespace, `-M` follows lines moved within a file, and `-C -C` follows lines copied from other files in the same commit or the commit that created the file. Since version 2.23 (2019), git also accepts `--ignore-revs-file`, a list of commits to look through. Projects such as Django keep such a list by hand (`.git-blame-ignore-revs`) for large reformatting commits. A hand-kept list has two limits. It covers only the commits someone remembered to add. And it applies to whole commits, so a commit that reformats one file and fixes another must either be skipped everywhere or not at all.

Line-tracking research has approached the same problem from several directions. LHDiff [1] tracks lines across versions with a language-independent mix of textual and context similarity. CodeShovel [2] builds method-level histories that survive moves and renames across files. RefactoringMiner [3] and CodeTracker [4] detect refactorings, and track methods and variables through them, with high precision. All three are mainly evaluated on Java. They track program elements rather than answering "which commit set this line's behaviour", and they do not separate cosmetic from logic changes at the level of a single file change.

## Finding the change that matters: the SZZ family

The SZZ algorithm [5] links bug-fixing commits to the changes that introduced the bug, using `git blame` (or its predecessor) on the lines a fix deletes. Its known weakness is the one this project addresses: blame lands on cosmetic changes. Kim et al. [6] already proposed ignoring formatting and comment changes when looking for bug-introducing changes. Refactoring-aware SZZ [7] uses refactoring detection to look through refactorings. These variants show that cosmetic history distorts any analysis built on blame. They target the bug-introducing commit of a fix, a related but different question from "why does this line exist?".

## Recovering links between code and discussions

Many commits do not reference the issue they fix. Bird et al. [8] showed that this missing-link problem biases defect datasets. ReLink [9] and later work recover missing links from textual similarity and time constraints between issues and commits. This project reuses the time constraint: a candidate discussion must have been created before the change. It also separates recovered links from recorded ones in everything it shows the user. Tian et al. [10] studied what makes a good commit message. Their central finding is that good messages say why a change was made as well as what it does. This is the information the system tries to bring back to a reader of the code.

## Explanations, retrieval and abstention

Retrieval-augmented generation [11] grounds a language model's answer in retrieved documents. Grounding alone does not stop a model from asserting things the documents do not say. Two techniques bound that risk, and this project uses both:

- requiring every answer to cite the evidence it uses, and rejecting answers whose citations are invalid;
- letting the model abstain, which trades coverage for accuracy. This is the idea of selective prediction [12].

The safety rule throughout is that missing evidence must never be reported as "safe".

## AI coding agents and the Model Context Protocol

Benchmarks such as SWE-bench [13] and agent designs such as SWE-agent [14] have shown that language-model agents can complete real repository tasks. They work from the code as it is now. The Model Context Protocol (MCP) [15] is an open standard for exposing tools and data to such agents, independent of the client and model. An MCP server written once can be used from desktop assistants, IDE agents and command-line agents, and with local models that support tool calling. Small community MCP servers already chain blame to pull request to issue. Other tools record agents' sessions against the commits they make. What these do not provide, and what this project contributes, is the combination evaluated here:

- tracing that survives cosmetic history;
- an explicit split between linked and searched evidence;
- explanations that cite or abstain;
- a protective-change check;
- a reproducible benchmark for each part.

## Defensive code

The idea that code with an unclear purpose should not be removed until its purpose is known is old. It is often called Chesterton's fence [16]. In software it covers guard clauses, assertions, input validation, locks and timeouts: code that does nothing in the normal case and matters only in the rare one. Such code is exactly what clean-up and simplification changes, human or automated, are tempted to delete. In the history mined for this project, guard removals that were later restored are rare, at less than 1% of all guard removals. That base rate shapes how the protective-code check is designed and evaluated (Chapters 3 and 6).

## Summary of the gap

| Work | Survives cosmetic history | Links discussions | Explains with citations | Flags guard removal | Agent interface |
|---|---|---|---|---|---|
| `git blame -w -M -C -C` | Partly (whitespace, moves) | No | No | No | No |
| Hand-kept ignore list | Only listed commits | No | No | No | No |
| CodeShovel, CodeTracker | Method-level, Java | No | No | No | No |
| SZZ variants | Partly | Bug-fix links | No | No | No |
| Blame → PR → issue MCP servers | No | Recorded links | No | No | Yes |
| This project (whyblame) | Yes, per file change | Recorded and searched | Yes, or abstains | Yes (CI and MCP) | Yes (MCP, any model) |

Table: How this project relates to existing work.

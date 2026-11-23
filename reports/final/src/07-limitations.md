# Limitations and Threats to Validity

## Construct validity

- **AI labels.** The gold labels (RQ1) and the explanation labels (RQ3) were produced by language models: Claude, and Gemini blind. Claude also helped build the method, so its labels are not independent of it. The protocol limits that risk: written rules fixed in advance, a blind second annotator from another vendor, a check sheet with candidates shown in random order, and every label published. It does not remove it. A blind human check of an overlap sample is the most important outstanding step before these figures are treated as human-validated.
- **"Restored later" as a proxy for "dangerous to remove".** RQ4 counts a removal as positive when the guard came back within a window with bug evidence. Some dangerous removals were never noticed, and some restorations happened for unrelated reasons. The labels are therefore noisy in both directions, and the measured precision is a lower bound on how often a flagged guard really mattered.
- **Fingerprints undercount kept protection.** RQ5's primary outcome counts a guard as removed when its token fingerprint disappears, even if the agent rewrote the same check in another form. This is why a second, judged outcome is reported next to it.
- **A judge model.** Task completion in RQ5, and the claim judgements in RQ3, rely on a judge model. Claude's independent labels and spot checks bound the risk, and all judge replies are saved.

## Internal validity

- **Selection.** RQ3 lines had to have a linked discussion with real text. RQ5 cases had to have a usable task. Both rules make the samples easier than a random line or a random change. In RQ3 this shows up directly: some "answerable" lines turned out to have evidence that does not explain them (Section 6.4).
- **One pilot, one agent.** RQ5 used one agent model, a fixed turn budget and simple file tools, with 16 cases and 2 seeds. Its statistics are those of a pilot.
- **Script changes during the measurement phase.** Five evaluation scripts were changed while measuring, and every change is listed in `eval/results/freeze_log.md`. None touched the product code or the frozen threshold.

## External validity

- **Three repositories.** Django, Redis and React are large, long-lived and well documented, with disciplined commit messages, and Django has a ticket for most changes. Repositories with poor commit messages and no linked discussions will see less benefit. The trace still works there, but the evidence behind it is thinner. Redis already shows this: only {{corpus.redis.linked}} of its commits have a linked discussion.
- **Languages.** Layer A and the guard detector support Python, C and JavaScript. Other languages fall back to treating every change as logic, which is safe but gains nothing over git.
- **Vendored code.** Code copied into a repository (for example Redis's `deps/`) has a history that starts at the import. Its real reasons live in another project.

## Known defects not fixed during the freeze

- Squashed subtree commits cite the vendored project's pull-request numbers. The linker resolves them against the host repository, producing wrong links (RQ3 question Q18).
- The test-path filter used when sampling RQ3 lines misses files named `tests.py`.

## Not claimed

- The system is **not fully local**: explanations call the Gemini API, though every other part runs on the user's machine.
- A guard with no recorded history is **not** reported as safe to remove.
- The RQ5 pilot does **not** show that agents in general make fewer unsafe edits with the tool. It measures one agent on 16 cases.

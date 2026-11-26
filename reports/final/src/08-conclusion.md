# Conclusion and Future Work

## Conclusion

This project set out to recover why a line of code exists, and to give that answer to developers and AI agents before they remove something that matters. The objectives were met as follows:

- **O1, accurate tracing.** By looking through each file's cosmetic history, the tracer finds the right commit {{rq1.ours}} of the time on held-out lines, against {{rq1.b2}} for git's strongest settings. The gain is significant and is largest exactly where blame is most misleading: in code that has been reformatted.
- **O2, evidence everywhere.** Commits in Django, Redis and React are linked to {{corpus.discussions}} discussions. When a link is missing, a time-respecting search finds the right one in the top ten for {{rq2.A.ours.recall@10}} of commits. That is good enough to suggest a discussion, not to assert one, and the system labels it that way.
- **O3, trustworthy explanations.** The explainer refused every question whose evidence was withheld. {{rq3.claims_supported_pct}} of the claims it did make are backed by the evidence it cited. Its main weakness is caution: it answers only {{rq3.coverage}} of questions with a linked discussion, mostly because those discussions describe a whole feature rather than the line.
- **O4, protecting code in CI.** The deterministic check flags removed guards at {{rq4.90.lift}} the base rate on held-out history, and it ran live on a real pull request. Precision stays low in absolute terms ({{rq4.90.precision}}), because few guard removals are ever undone. So the check is designed to inform a reviewer, not to block a merge.
- **O5, any model.** whyblame 1.0 is an MCP server with stable, capped, versioned replies, served over stdio and HTTP, with agent rules written by `whyblame init`. It is published on PyPI and the official MCP registry (Appendix D).
- **O6, measured difference.** In a controlled pilot, an agent given whyblame's tools kept the historical guard in {{rq5.treatment.guard_kept}} of {{rq5.treatment.runs}} runs, against {{rq5.control.guard_kept}} of {{rq5.control.runs}} without (p = {{rq5.guard_kept_mcnemar.p}}). It completed as many tasks, at no extra cost. On cost: whyblame indexes Django's {{rq6.django.commits}} commits in {{rq6.django.index_min}} minutes on an 8 GB laptop, and answers a question about a line in a median {{rq6.django.cold}} s.

The broader lesson is that a project's history already holds most of the reasons behind its code. What has been missing is a reliable way to get from a line to the change that really set it. Once that step is reliable, links to discussions, cited explanations and warnings in CI all follow from it, and so does an agent's ability to ask before it deletes.

## Future work

Each item below responds to a weakness measured in Chapter 6.

1. **A human check of the labels.** All gold and explanation labels are AI labels. A blind human check of an overlap sample is the most important step before publication.
2. **Better evidence for Redis-like projects.** Only {{corpus.redis.linked}} of Redis commits link a discussion, which limits RQ3's coverage and RQ4's recall there. Two steps would help: resolving subtree and vendored-library references against the right upstream project, and mining mailing lists and review comments.
3. **Sharper CI warnings.** About a quarter of the check's false alarms are deliberate rewrites into another form of guard, or planned deprecation removals. Recognising an added equivalent guard in the same change, and reading deprecation notes, would remove many of them. Any such change needs a fresh held-out period to measure.
4. **Searching by meaning.** RQ2's Recall@1 is low ({{rq2.A.ours.recall@1}}). A small local embedding model, re-ranked with the time rule, is the next step, if it fits in 8 GB.
5. **A larger agent study.** RQ5 is a pilot with one agent and 16 cases. More models, more cases, real clients rather than a harness, and a human judge of task completion would turn it into evidence.
6. **More languages and IDE integration.** Layer A and the guard detector cover Python, C and JavaScript. TypeScript, Java and Go are natural next grammars. An editor extension would bring the answer to developers, not only to agents.
7. **The paper and the benchmark.** The tracing method, the RQ3 question set and the RQ4 guard-removal benchmark are ready to be published as artifact IDs, labels and rebuild scripts.

## RQ5: an agent pilot

| Outcome | Without whyblame | With whyblame | McNemar (exact) |
|---|---:|---:|---|
| Guard kept as written | {{rq5.control.guard_kept}} of {{rq5.control.runs}} | {{rq5.treatment.guard_kept}} of {{rq5.treatment.runs}} | {{rq5.guard_kept_mcnemar.b}} vs {{rq5.guard_kept_mcnemar.c}} pairs, p = {{rq5.guard_kept_mcnemar.p}} |
| Protection kept (as written or rewritten) | {{rq5.control.protection_kept}} | {{rq5.treatment.protection_kept}} | {{rq5.protection_kept_mcnemar.b}} vs {{rq5.protection_kept_mcnemar.c}}, p = {{rq5.protection_kept_mcnemar.p}} |
| Task done | {{rq5.control.task_done}} | {{rq5.treatment.task_done}} | {{rq5.task_done_mcnemar.b}} vs {{rq5.task_done_mcnemar.c}}, p = {{rq5.task_done_mcnemar.p}} |
| Protection kept and task done | {{rq5.control.protected_and_done}} | {{rq5.treatment.protected_and_done}} | |
| Called `why_line` / `check_change` | 0 / 0 | {{rq5.treatment.called_why_line}} / {{rq5.treatment.called_check_change}} | |
| Mean turns used (of 30) | {{rq5.control.mean_steps}} | {{rq5.treatment.mean_steps}} | |
| Gemini spend | {{rq5.control.cost}} | {{rq5.treatment.cost}} | |

Table: The agent pilot: 16 real guard removals, 2 seeds, paired by case and seed.

![Outcomes of the agent pilot, without and with whyblame's tools.](figures/rq5.png)

Given the same task, the agent with whyblame's tools kept the historical guard in {{rq5.treatment.guard_kept}} of {{rq5.treatment.runs}} runs, against {{rq5.control.guard_kept}} without. In every pair that differed, the guard survived only in the run with the tool: {{rq5.guard_kept_mcnemar.b}} pairs to {{rq5.guard_kept_mcnemar.c}}, McNemar exact p = {{rq5.guard_kept_mcnemar.p}}. Task completion did not suffer ({{rq5.treatment.task_done}} against {{rq5.control.task_done}}). The tool calls did not raise the cost of a run either.

The agent called `why_line` in every treatment run and `check_change` in {{rq5.treatment.called_check_change}} of {{rq5.treatment.runs}}. So the server's instructions and tool descriptions were enough for this model to use the tools unprompted, without any rules file.

The clearest case is `string2ll()` in Redis (case c05). Asked to simplify it, the agent without the tool deleted the special case for a single "0" in both seeds. The code after that check rejects a leading zero, so the string "0" no longer parsed. That is exactly why the real deletion was reverted within a day. With the tool, the agent asked `why_line` about that line in both seeds and kept the check both times. In one seed it then removed a different branch that also handles "0", and the judge marks that run not done. So the tool protected the guard it was asked about, not every line near it.

The secondary outcome narrows the gap ({{rq5.treatment.protection_kept}} against {{rq5.control.protection_kept}}, p = {{rq5.protection_kept_mcnemar.p}}). Some control runs rewrote the guard with the same condition rather than deleting it. In the session-file case (c06), for example, both control runs replaced the `if settings.USE_TZ:` branch with `tz = timezone.utc if settings.USE_TZ else None`, which keeps the behaviour in a different form.

The tool did not help where the task itself demands the removal. Asked to "remove deprecated code from django/apps/registry.py", both conditions deleted the deprecated branch, together with the `except LookupError` inside it. That is arguably the right edit.

**Spot checks.** Claude re-labelled {{rq5.spot}} runs from the task, the original checks and the diff, and agreed with the judge on {{rq5.spot_agree}}. These labels were blind to the judge's answers but, because of a sheet error, not to the condition (`freeze_log.md`, entry 6).

This is a pilot: one agent model, 16 cases and 2 seeds at temperature 0, so the seeds are close to repeats. The direction is clear and significant on the planned outcome, but its size should not be generalised beyond this setting.

## RQ6: footprint on a laptop

| Repo | Commits | Index time | Peak RAM (index) | Database | `why_line` median, cold | p95, cold | Median, warm |
|---|---:|---:|---:|---:|---:|---:|---:|
| click | {{rq6.click.commits}} | {{rq6.click.index_min}} min | {{rq6.click.ram}} MB | {{rq6.click.db}} MB | {{rq6.click.cold}} s | {{rq6.click.cold95}} s | {{rq6.click.warm}} s |
| Redis | {{rq6.redis.commits}} | {{rq6.redis.index_min}} min | {{rq6.redis.ram}} MB | {{rq6.redis.db}} MB | {{rq6.redis.cold}} s | {{rq6.redis.cold95}} s | {{rq6.redis.warm}} s |
| Django | {{rq6.django.commits}} | {{rq6.django.index_min}} min | {{rq6.django.ram}} MB | {{rq6.django.db}} MB | {{rq6.django.cold}} s | {{rq6.django.cold95}} s | {{rq6.django.warm}} s |
| React | {{rq6.react.commits}} | {{rq6.react.index_min}} min | {{rq6.react.ram}} MB | {{rq6.react.db}} MB | {{rq6.react.cold}} s | {{rq6.react.cold95}} s | {{rq6.react.warm}} s |

Table: Cost on a MacBook Air (M1, 8 GB): a fresh index with `whyblame index`, then 50 random lines.

Indexing is a one-off cost, and later runs process only new commits. Peak memory stays well within an 8 GB laptop, even with four classifier processes. The database is a small fraction of the repository's own git objects. A first question about a line takes a median of {{rq6.django.cold}} s on Django. Further questions about the same file are answered from memory, which is the pattern of an agent working on one function. The slowest cold queries are lines in large files with long histories: p95 is {{rq6.react.cold95}} s on React and {{rq6.django.cold95}} s on Django.

## Works with any model

The client compatibility runs (Section 5.8) are recorded in `eval/compat/results.csv` and summarised by `eval/compat_summary.py`. Status: **{{compat.status}}**. The RQ5 pilot shows the mechanism on one model that is not Claude (`{{rq5.agent_model}}`). Through the real MCP server's descriptions alone, it called `why_line` unprompted in every run.

## Where it does not help

- **Repositories without written reasons.** In Redis, only {{corpus.redis.linked}} of commits link a discussion. The tracer still finds the right commit, but there is less to explain with. The CI check caught none of Redis's six restored guards, and most of the explainer's justified abstentions are Redis lines.
- **Vendored code.** Lines in `deps/` and other copied libraries trace back to the import commit. Their real reasons are in another project's history.
- **Features rather than fixes.** When a line was added as part of a large feature, the linked pull request explains the feature, not the line. The explainer then gives a feature-level answer or abstains.
- **Deliberate removals.** The CI check cannot know that a removal was planned (a deprecation timeline) or that an equivalent guard was added in another form. Those are most of its explainable false alarms, and both are concrete next steps.
- **Tasks that require the removal.** When the task is to delete the code that contains the guard, keeping the guard is not the right outcome, and the tool rightly does not prevent it.

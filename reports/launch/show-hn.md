**Title:** Show HN: Whyblame – git blame that skips reformats and tells your AI agent why a line exists

**URL:** https://github.com/Anikketsingh/Provenance-Aware-Code-Intelligence

**First comment:**

Hi HN. `git blame` names the last commit that touched a line. In long-lived projects that's often a Black/Prettier reformat, a rename or a move. That's annoying for people, and worse for AI coding agents: an agent that reads "Reformatted code with Black" sees no reason not to delete the check under it.

whyblame does three things:

- It classifies every file change in history as cosmetic, rename, move or logic. It compares tree-sitter token streams for Python, C and JS, and it works per file rather than per commit.
- It feeds each file's cosmetic commits to `git blame --ignore-revs-file`.
- It steps through commits that mix a reformat with a real change.

Then it attaches the ticket or PR behind the commit it lands on.

It's a CLI, a local web UI, a GitHub Action and an MCP server, so Claude Code, Cursor, Codex, Gemini CLI or a local model can call `why_line` before deleting something.

Numbers, all reproducible from the repo:

- On 60 held-out lines from Django and Redis it finds the right commit 83.5% of the time, against 69.2% for `git blame -w -M -C -C`. The labels are AI labels, disclosed and checked blind by a second model; a human check is still to do.
- In a 16-case agent pilot built from real guard removals that later got reverted, a Gemini agent kept the guard in 22 of 32 runs with the tool, against 16 of 32 without, and finished as many tasks.
- The PR check (warns, never blocks) is honest about base rates: guard removals that later need undoing are under 1% of removals. Its warnings hit about 3× the base rate, so it's a "look at this" nudge, not a gate.

Install:

```
uv tool install whyblame
whyblame index && whyblame why . path/to/file.py 42
whyblame init   # prints the MCP setup line for your client
```

It started as our B.Tech final-year project. Happy to answer anything, especially about where it doesn't help: repos whose commit messages say nothing, and vendored code.

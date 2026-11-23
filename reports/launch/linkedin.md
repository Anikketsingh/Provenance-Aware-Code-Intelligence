Our B.Tech major project at Delhi Technological University is now open source: **whyblame**.

AI coding agents delete code whose purpose they can't see: a null check, a retry, a lock. The reason that code exists is usually written down in a commit or a bug ticket. But `git blame`, the standard tool for finding it, often points at a reformat instead.

whyblame traces any line past reformats, renames and moves to the change that really created it, attaches the ticket behind it, and gives that answer to AI agents through the Model Context Protocol.

What we measured:

- 83.5% of lines traced to the right commit, against 69.2% for git's best settings (held-out test set).
- In an agent pilot built from real bugs, the agent with our tool kept the protective check in 22 of 32 runs, against 16 of 32 without, while finishing as many tasks.
- A GitHub Action that warns on a pull request when it removes a guard with a recorded reason, tested live on Redis.

Built by Aniket Singh Kushwaha, Aarish and Aftab, guided by Prof. Shailender Kumar.

Install: `uv tool install whyblame`
Code and the full evaluation: https://github.com/Anikketsingh/Provenance-Aware-Code-Intelligence

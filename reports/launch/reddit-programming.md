**Title:** git blame points at the reformat. We built a tool that skips it, and measured how often that matters.

**Link:** https://github.com/Anikketsingh/Provenance-Aware-Code-Intelligence

**Comment:**

`git blame -w -M -C -C` is as good as blame gets. Even so, in Django 22.7% of sampled lines land on a commit the Django team itself lists as pure formatting.

whyblame classifies every file change in a repo's history as cosmetic, rename, move or logic, by comparing tree-sitter token streams. It gives git a per-file skip list, then steps through commits that mixed a reformat with a real fix. On held-out lines it finds the commit that really set a line's behaviour 83.5% of the time, against 69.2% for git's strongest settings.

It also links the commit to its ticket or PR, and serves all of this to AI coding agents over MCP. There's also a GitHub Action that warns when a PR deletes a guard (an early return, raise, assert, lock or timeout) whose history says it was added by a fix.

Where it doesn't help: repos with empty commit messages, and vendored code whose history starts at the import. The full evaluation, including the weak spots, is in the repo, and one script reproduces it.

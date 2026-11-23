# Your final steps (kept for last)

Everything here needs you: a client app, your accounts, or your voice. Claude finishes Phases 5 and 6 first. Then work down this list in order. Each step says what to tell Claude when it's done.

## 1. The compatibility test (Phase 4.6, about 1.5 hours)

Full instructions are in [`eval/compat/README.md`](../eval/compat/README.md). The short version:

```bash
uv run python eval/compat/setup.py            # once; about 5 s. Prints each client's setup with your paths
```

For each client, do **two runs** in the copy it makes (`~/whyblame-compat`):

1. **Plain run.** Register the server, start a new chat, paste the task:
   *Simplify make_password() in django/contrib/auth/hashers.py*.
   Then record it:
   ```bash
   uv run python eval/compat/verify.py --client "Cursor" --model "GPT-5" --rules no \
       --connected yes --called yes --notes "called why_line twice, kept both checks"
   ```
2. **With the rules.** Reset the copy and add the `init` rules, then run the same task again:
   ```bash
   uv run python eval/compat/setup.py --rules
   uv run python eval/compat/verify.py --client "Cursor" --model "GPT-5" --rules yes --connected yes --called yes
   ```

`verify.py` checks the file itself and says whether both guards survived. Each call adds one row to `eval/compat/results.csv`.

**You need:**

- At least 4 clients.
- One of them a **local model**: Ollama with `qwen3:4b` fits in 8 GB.
- Claude Code as one of the four. Its command-line tool isn't on this Mac, so use the VS Code extension in a new window opened on `~/whyblame-compat`.

**Then tell Claude: "compat done".** Claude will:

- add the "Works with" table to the README and the release notes;
- rerun the any-model summary (`compat.json`) and `summary.md`;
- rebuild the report and deck pages that show the matrix.

## 2. Publish (Phase 4.8, about 30 minutes)

Claude rebuilds the package first (`rm -rf dist && uv build`), so `dist/` holds the final files. Then you:

**a. PyPI.**

```bash
set -a; source .env; set +a      # loads UV_PUBLISH_TOKEN without printing it
uv publish
```

Check it works in a new folder:

```bash
cd /tmp && uv venv t && source t/bin/activate && pip install whyblame && whyblame --version
```

**b. Tags.** Tell Claude "PyPI done". Claude tags `v1.0.0`, moves the `v1` tag to it (the README uses `@v1`), and pushes both.

**c. GitHub release and Marketplace.**

1. On GitHub, go to Releases and choose Draft a new release.
2. Pick the tag `v1.0.0`, and title it `whyblame 1.0.0`.
3. Paste the notes from `docs/releases/v1.0.0.md`.
4. Tick **"Publish this action to the GitHub Marketplace"**. The first time, GitHub asks you to accept the Marketplace agreement, and it needs 2FA on your account.
5. Choose the categories **Code quality** and **Security**, then Publish.

**d. The MCP registry.**

```bash
brew install mcp-publisher        # or download it from github.com/modelcontextprotocol/registry/releases
mcp-publisher login github        # opens the browser; sign in as Anikketsingh
mcp-publisher publish             # run in the project folder; it reads server.json
```

**Check all three:**

- https://pypi.org/project/whyblame/ shows 1.0.0.
- The Marketplace page appears on the release.
- This returns the entry:
  ```bash
  curl "https://registry.modelcontextprotocol.io/v0/servers?search=whyblame"
  ```

**Then tell Claude: "published".** Claude ticks the Phase 4 checklist and updates the report's release section with the live links.

## 3. Before the evaluation (Phase 6.6 and 6.7)

- **Backup recording.** About 5 minutes, following `reports/demo-script-v2.md`, which Claude writes in Phase 6. Save it in two places: the laptop, and Drive or a USB stick.
- **Rehearsal with Aarish and Aftab.** Two timed full runs, plus one live demo on the presentation laptop and network.

Claude pushes the `project-final` tag after step 2, once every number in the report matches `summary.md`.

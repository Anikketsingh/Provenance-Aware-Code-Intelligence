# Ingestion

**Level:** component. **Phase:** starts now. Git history is needed for Project-I, and the discussion crawl can run alongside it.

## 1. Goal

Turn each repo into one local SQLite file holding its commits, file changes and discussion artefacts. Every later stage reads from this database, so crawling only has to happen once.

## 2. Corpus

| Repo | Role | Discussion source | Expected work |
|---|---|---|---|
| Redis | Full system | GitHub issues and PRs | GitHub crawler |
| Django | Full system | GitHub PRs and Trac tickets | GitHub crawler plus Trac crawler |
| React | Full system | GitHub issues and PRs | GitHub crawler (repo is now `react/react`) |
| PostgreSQL | **Line tracing only** | None for now | Git history only. Stretch goal: follow `Discussion:` links into mailing lists. |

Before any evaluation, each repo gets pinned to one exact commit SHA and crawl date. These go in `eval/corpus.lock.json`, so that everyone uses the same data.

## 3. Git history

```bash
git clone --bare <url> data/<repo>/repo.git
```

Clones are always bare, which saves disk because no working copy is checked out.

Steps:

1. Walk all commits reachable from the pinned SHA. Store them with their parents.
2. For each commit, store changed files against its first parent, with rename detection on.
3. For merges, store the first-parent diff and flag `is_merge`, which keeps later stages simple.
4. Commit to SQLite every 1,000 commits. Re-running skips commits already stored.

**Done when:** the commit count matches `git rev-list --count <sha>` for every repo, and a repeat run adds nothing.

## 4. GitHub crawl

Use the **GraphQL API**, since one request can fetch 100 PRs with nested comments. The REST API would need many calls per PR.

Fetch for each PR: number, title, body, author, dates, state, merge commit, labels, comments, reviews, review comments, closing issue references.

Fetch for each issue: number, title, body, author, dates, state, labels, comments, cross-references.

Rules the crawler must follow:

- **Token from an environment variable** (`GITHUB_TOKEN`), never committed. No special scopes are needed for public repos.
- **Save raw responses first.** Each page goes into a local cache before parsing, so a parser bug doesn't require a re-crawl.
- **Resume with cursors.** Save the last cursor after each page.
- **Respect limits.** Check the `rateLimit` field and sleep until reset when low. Back off on secondary rate-limit errors.
- **Handle long threads.** Follow up with separate paginated queries when a PR has more than 100 comments.
- **Tolerate deleted accounts.** `author` can be null.

The plan estimates several days for the crawl. GraphQL should take far less, but we should treat that as a guess until the Redis run gives a real figure. Run it first because Redis is the smallest.

## 5. Trac crawl (Django)

Django tickets are at `code.djangoproject.com`. `/ticket/<id>?format=csv` returned the ticket fields in our test, but it does not include the comment history, so the comments need another route such as the ticket's RSS feed or page.

Rules:

- Only fetch ticket IDs that Django commits actually reference. That's far kinder to a volunteer-run server, and it's all we need at first.
- One request per second at most, with caching, so each ticket is fetched only once.
- Use a descriptive User-Agent with the project name and a project URL.
- Check `robots.txt` before starting.

For the benchmark, we will also need tickets that were **not** linked, as distractors. Those can be sampled later at the same polite rate.

## 6. Parsing references

Patterns to extract from commit messages and discussion text:

| Repo | Pattern | Meaning |
|---|---|---|
| Django | `Fixed #123`, `Refs #123` | Trac ticket reference |
| Redis, React | `(#123)` at end of subject | Squash-merge PR number |
| Any GitHub repo | `Fixes #123`, `Closes #123` | Closing keyword |
| Any | `This reverts commit <sha>` | Revert |
| PostgreSQL | `Discussion: https://postgr.es/m/...` | Mail thread link |

In Django, `#123` means a Trac ticket in a commit message, but a GitHub PR or issue number elsewhere. So references have to be resolved per repo, not by one global rule.

Each parser gets unit tests built from real messages.

## 7. Tasks

| # | Task | Needed for Project-I? |
|---|---|---|
| 1 | SQLite schema and connection helper | Yes |
| 2 | Bare clone helper and corpus lock file | Yes |
| 3 | History walker, resumable | Yes |
| 4 | Reference parsers with tests | **Done, 10 Nov.** `provenance link` stores 22,273 Django and 7,242 Redis links |
| 5 | GraphQL crawler with cache and resume | Next. Needs a `GITHUB_TOKEN` from Aniket |
| 6 | Trac crawler | **Started, 10 Nov.** `provenance fetch-tickets` fetches summaries and descriptions, not yet comments |
| 7 | Crawl React and Django | No |

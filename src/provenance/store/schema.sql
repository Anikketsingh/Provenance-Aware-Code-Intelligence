CREATE TABLE IF NOT EXISTS commits (
    sha TEXT PRIMARY KEY,
    author_time INTEGER NOT NULL,
    commit_time INTEGER NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    is_merge INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS commit_parents (
    sha TEXT NOT NULL,
    parent_sha TEXT NOT NULL,
    position INTEGER NOT NULL,
    PRIMARY KEY (sha, position)
);

CREATE TABLE IF NOT EXISTS file_changes (
    sha TEXT NOT NULL,
    status TEXT NOT NULL,
    old_path TEXT,
    path TEXT NOT NULL,
    old_blob TEXT,
    new_blob TEXT
);
CREATE INDEX IF NOT EXISTS file_changes_sha ON file_changes (sha);

CREATE TABLE IF NOT EXISTS commit_class (
    sha TEXT PRIMARY KEY,
    kind TEXT NOT NULL,
    confidence REAL NOT NULL,
    reason TEXT NOT NULL,
    algo_version INTEGER NOT NULL
);

-- Only non-logic changes are stored. A missing row means the change counts as logic.
CREATE TABLE IF NOT EXISTS file_class (
    sha TEXT NOT NULL,
    path TEXT NOT NULL,
    kind TEXT NOT NULL,
    PRIMARY KEY (sha, path)
);
CREATE INDEX IF NOT EXISTS file_class_path ON file_class (path);

-- Links between commits, tickets, pull requests and other artefacts. `origin` says where an
-- edge came from (for example 'message' for parsed commit messages), so each source can be
-- rebuilt on its own.
CREATE TABLE IF NOT EXISTS edges (
    src TEXT NOT NULL,
    dst TEXT NOT NULL,
    type TEXT NOT NULL,
    confidence REAL NOT NULL,
    evidence TEXT NOT NULL,
    origin TEXT NOT NULL,
    algo_version INTEGER NOT NULL,
    PRIMARY KEY (src, dst, type)
);
CREATE INDEX IF NOT EXISTS edges_dst ON edges (dst);

-- Discussion artefacts: tickets, pull requests, issues. Text in them is untrusted.
CREATE TABLE IF NOT EXISTS artefacts (
    id TEXT PRIMARY KEY,
    kind TEXT NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    state TEXT NOT NULL,
    url TEXT NOT NULL,
    raw TEXT NOT NULL,
    fetched_at INTEGER NOT NULL
);

-- Where each resumable crawl got to.
CREATE TABLE IF NOT EXISTS crawl_state (
    key TEXT PRIMARY KEY,
    cursor TEXT,
    pages INTEGER NOT NULL,
    done INTEGER NOT NULL
);

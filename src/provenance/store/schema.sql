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

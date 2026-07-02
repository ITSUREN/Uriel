CREATE TABLE documents (
    doc_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    path          TEXT UNIQUE NOT NULL,
    title         TEXT NOT NULL,
    length        INTEGER NOT NULL,
    last_modified TEXT NOT NULL
);

CREATE TABLE postings (
    term            TEXT NOT NULL,
    doc_id          INTEGER NOT NULL REFERENCES documents(doc_id) ON DELETE CASCADE,
    term_frequency  INTEGER NOT NULL,
    positions       TEXT NOT NULL,  -- JSON-encoded list[int]
    PRIMARY KEY (term, doc_id)
);

CREATE INDEX idx_postings_term ON postings(term);
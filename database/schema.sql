-- Enable Write-Ahead Logging for concurrency (allows search while indexing)
PRAGMA journal_mode=WAL;

-- 1. Pages table: Stores the indexed content and metadata for search.
CREATE TABLE IF NOT EXISTS pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE NOT NULL,
    origin_url TEXT,
    depth INTEGER NOT NULL,
    title TEXT,
    content TEXT,
    raw_html TEXT,
    indexed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Crawl Queue table: Manages 'back pressure' and allows resuming.
-- Status codes: 0 = Pending, 1 = Processing, 2 = Completed, 3 = Failed
CREATE TABLE IF NOT EXISTS crawl_queue (
    url TEXT PRIMARY KEY,
    depth INTEGER NOT NULL,
    parent_url TEXT,
    status INTEGER DEFAULT 0,
    discovered_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3. Inverted Index: To speed up word frequency lookups.
CREATE TABLE IF NOT EXISTS word_index (
    word TEXT,
    page_id INTEGER,
    frequency INTEGER,
    FOREIGN KEY(page_id) REFERENCES pages(id)
);
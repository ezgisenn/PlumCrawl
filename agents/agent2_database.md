# Agent 2: Database & Storage Engineer
**Role:** Backend Data Specialist
**Responsibilities:** - Designing the SQLite schema (`schema.sql`).
- Implementing Write-Ahead Logging (WAL) to ensure search queries can run concurrently with indexing.
- Creating the `crawl_queue` to enable the system to resume after interruption.
- Optimizing database writes using bulk inserts (`executemany`) to prevent database locks.
# Multi-Agent AI Workflow Log

## Introduction
PlumCrawl was developed not as a multi-agent runtime, but through a simulated multi-agent AI development process. The human developer acted as the **Product Manager & System Architect**, assigning specific responsibilities to distinct AI personas, managing their interactions, and evaluating their outputs to ensure the "zero-dependency" and "concurrency" requirements were met.

## The AI Agent Team & Responsibilities

1.  **Agent 1 (System Architect):**
    * *Role:* Defined the overall system architecture and drafted the PRD.
    * *Decision:* Enforced the strict zero-dependency rule and proposed the `sqlite3` WAL mode strategy for concurrency.
2.  **Agent 2 (Database & Storage Engineer):**
    * *Role:* Designed the SQLite schema (`schema.sql`).
    * *Decision:* Implemented `pages` and `crawl_queue` tables to support interruption recovery. Transitioned from single inserts to `executemany` bulk inserts to resolve `OperationalError: database is locked` bottlenecks during high-speed crawls.
3.  **Agent 3 (Crawler & Concurrency Specialist):**
    * *Role:* Developed `indexer.py` using native `threading` and `urllib`.
    * *Decision:* Implemented a dynamic "Back-Pressure" mechanism. When the queue exceeds the limit, threads pause link extraction but continue parsing HTML to drain the queue. Added native `gzip` decompression and stealth headers to bypass 403 Forbidden errors on large targets like Wikipedia.
4.  **Agent 4 (Information Retrieval Engineer):**
    * *Role:* Developed `searcher.py`.
    * *Decision:* Created a scoring algorithm combining word frequency and a depth penalty weight ($1.0 / (depth + 1.0)$) to ensure pages closer to the origin rank higher.
5.  **Agent 5 (UI/CLI Developer):**
    * *Role:* Built the interactive telemetry interface.
    * *Decision:* Transitioned from a CLI to a native Web UI (`app_web.py` using `http.server`) featuring the "Plum Dark Mode" aesthetic, enabling users to execute searches seamlessly while the background thread updates indexing stats every 1.5 seconds.

## Workflow Evaluation
The multi-agent approach allowed for rapid iteration. When Agent 3 faced database locks due to high concurrency, the Architect (Human) intervened, directing Agent 2 to optimize the SQL queries. This collaborative loop ensured a highly scalable and robust final product.
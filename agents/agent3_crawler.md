# Agent 3: The Collaborative Crawlers
**Role:** Teammates / Data Ingestion Experts (`indexer.py` Threads)
**Responsibilities:** - Acting as concurrent Teammate Agents (`Worker-1` to `Worker-5`).
- Pulling tasks from the Shared Task List, executing HTTP requests, and parsing HTML.
- Communicating newly discovered links back to the Shared Task List for other peers to process.
- Respecting dynamic back-pressure limits to maintain team efficiency.
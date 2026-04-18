# Multi-Agent AI Workflow: The "Agent Teams" Architecture

## Introduction
Based on the principles of advanced multi-agent systems, PlumCrawl is architected specifically around the **"Agent Teams"** paradigm. Rather than using isolated, hierarchical subagents, our system employs a collaborative environment where a Team Lead orchestrates multiple Teammate Agents sharing a centralized task state.

## Architectural Mapping to "Agent Teams"

Our system perfectly aligns with the collaborative Agent Teams workflow:

1. **Main Agent (Team Lead):** The Orchestrator (`app_web.py` & `PlumIndexer`). It receives the user's initial input (origin URL and depth) and spawns the team of crawler and searcher agents.
2. **Shared Task List:** Our SQLite database (specifically the `crawl_queue` and `pages` tables with WAL mode enabled). This is the central source of truth where all agents communicate their progress, claim tasks, and deposit results.
3. **Teammates (Worker Agents):** The individual concurrency threads (`Worker-1` to `Worker-5`) and the Information Retrieval Engine (`searcher.py`).

## Agent Interactions and Communication (Peer-to-Peer)

In our "Agent Teams" architecture, agents do not communicate by passing messages sequentially back to the Team Lead. Instead, they use **State-Based Peer Communication** via the Shared Task List:
* **Task Claiming:** When a Teammate (Crawler Agent) is idle, it queries the Shared Task List for a URL with `status = 0`. It instantly updates the state to `status = 1` (Processing), signaling to all other peer agents: *"I have claimed this task, do not crawl it."*
* **Result Sharing:** Once an agent parses a page, it bulk-inserts newly discovered URLs back into the Shared Task List. Another idle Teammate instantly sees these new tasks and picks them up.
* **Cross-Discipline Communication:** The Indexer Agents and the Search Agent operate concurrently. The Search Agent continuously reads the `pages` table (the finalized shared state), meaning it communicates dynamically with the Indexer Agents in real-time as they write data.

## System Workflow Decisions
* **Decision 1:** To implement the "Shared Task List" reliably without external libraries, we utilized `sqlite3` with Write-Ahead Logging (WAL) and `executemany` bulk transactions, preventing database locks during intense peer communication.
* **Decision 2:** We implemented a "Smart Back-Pressure" mechanism. If the Shared Task List becomes overloaded (e.g., > 5000 tasks), Teammates communicate this state and temporarily pause extracting new tasks, focusing purely on draining the existing shared queue.
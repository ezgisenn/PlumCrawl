# Product Requirements Document (PRD)
**Project Name:** PlumCrawl
**Objective:** Develop a robust, concurrent web crawler and search engine utilizing a multi-agent AI development workflow. The system must prioritize language-native functionality with zero external dependencies for its core logic.

## 1. System Architecture & Core Principles
* **Language-Native:** Core operations (HTTP requests, HTML parsing, concurrency, data storage) must rely exclusively on Python standard libraries (e.g., `urllib`, `html.parser`, `threading`, `sqlite3`).
* **Concurrency:** The system must allow the `search` function to operate and return dynamically updating results while the `index` function is actively crawling.
* **Resilience:** The system should support resuming operations after an interruption without data loss.

## 2. Core Features

### 2.1. The Indexer (`index(origin, k)`)
* **Functionality:** Initiates a web crawl starting from the `origin` URL up to a maximum depth of `k` hops.
* **Uniqueness Guarantee:** Implements strict validation to ensure no URL is crawled more than once.
* **Resource Management (Back Pressure):** Integrates queue depth monitoring and a rate-limiting mechanism to manage system load in a controlled manner, preventing resource exhaustion.

### 2.2. The Search Engine (`search(query)`)
* **Functionality:** Accepts a search query string and retrieves relevant indexed pages.
* **Output Format:** Returns a list of triples: `(relevant_url, origin_url, depth)`.
* **Relevancy Engine:** Relevancy will be determined by a custom algorithm combining keyword frequency and tree depth.
* **Real-time Access:** Must securely query the data store concurrently with the indexer's write operations.

### 2.3. User Interface / CLI
* **Functionality:** A unified command-line or local web interface (featuring a Plum Dark Mode aesthetic: dark plum, lavender, and anthracite) to trigger `/index` and `/search`.
* **Telemetry:** Must provide real-time visibility into system state, including indexing progress, queue depth, and back pressure status.
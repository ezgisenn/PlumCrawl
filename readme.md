# PlumCrawl: Multi-Agent Concurrent Web Indexer & Search Engine

PlumCrawl is a lightweight, zero-dependency, highly concurrent web crawler and search engine developed entirely using Python's standard libraries. This project demonstrates a clear multi-agent AI collaboration workflow, emphasizing architectural resilience, real-time concurrency, and elegant telemetry visualization.

## Core Features
* **Zero External Dependencies:** Built strictly with Python-native modules (`urllib`, `html.parser`, `sqlite3`, `threading`). No `requests`, `BeautifulSoup`, or external frameworks were used.
* **True Concurrency (WAL Mode):** Utilizing SQLite's Write-Ahead Logging, the system allows the Search Engine to query the database in real-time while the Indexer actively writes thousands of records simultaneously.
* **Smart Back-Pressure:** The crawler autonomously monitors queue depth. If the queue exceeds a defined threshold, it pauses link extraction while continuing to process existing URLs, preventing system overload.
* **GZIP & Stealth Protocol:** Equipped with advanced request headers and native `gzip` decompression to bypass aggressive anti-bot firewalls (e.g., Wikipedia) and process compressed payloads smoothly.
* **Plum Dark Mode UI:** A native, zero-dependency local web interface served via `http.server`, providing real-time telemetry (Indexed, Queue Depth, Failed) and simultaneous search capabilities.

## How to Run
1.  Ensure you have Python 3 installed. No `pip install` is required.
2.  Navigate to the project root directory.
3.  Execute the application:
    ```bash
    python app_web.py
    ```
4.  Open your web browser and go to: `http://localhost:8000`

## System Architecture
* **Database Engine (`sqlite3`):** Handles state persistence, allowing the system to be resumed after interruptions. Uses batch processing (`executemany`) to prevent database locks during high-throughput crawling.
* **Relevancy Engine:** Ranks search results using a custom algorithm combining Term Frequency (TF) and Tree Depth Penalty (nodes closer to the origin score higher). Returns strict `(relevant_url, origin_url, depth)` triples.
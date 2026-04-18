# Production Deployment Recommendations

While PlumCrawl is a highly capable local search engine, transitioning this architecture to a production environment handling millions of requests requires decoupling our current monolithic, zero-dependency setup.

## 1. Migrating to a Distributed Message Broker
Currently, the "Back-Pressure" and queue management rely on a local SQLite table (`crawl_queue`). In production, this becomes a bottleneck. We strongly recommend replacing the SQLite queue with a distributed message broker like **RabbitMQ** or **Apache Kafka**. This allows multiple crawler instances (workers) distributed across different servers to pull URLs from a centralized, high-throughput queue seamlessly.

## 2. Transitioning to a NoSQL or Search-Optimized Datastore
While SQLite with WAL mode is excellent for local concurrency, it cannot scale horizontally. The `pages` table, which holds massive text payloads, should be migrated.
* **Document Storage:** Raw HTML and parsed text should be stored in a NoSQL database like **MongoDB** or cloud object storage (AWS S3) for cheap, horizontal scaling.
* **Search Engine:** Agent 4's custom relevancy algorithm should be replaced by a dedicated full-text search engine like **Elasticsearch** or **Typesense**. These engines handle tokenization, stemming, and inverted indexing natively, offering sub-millisecond search times across billions of documents, which `sqlite3 LIKE` queries cannot achieve at scale.

## 3. Advanced Crawler Resilience (Proxy Rotation)
Our current implementation uses static stealth headers to bypass basic firewalls. A production crawler will inevitably face IP bans. The architecture must be upgraded to route HTTP requests through a rotating proxy pool and utilize dynamic user-agent switching to ensure uninterrupted data ingestion across strict targets.
# Agent 2: The Shared Task List Manager
**Role:** State & Concurrency Manager (`schema.sql` & Database Logic)
**Responsibilities:** - Acting as the robust "Shared Task List" for the Agent Team.
- Managing concurrent peer-to-peer communication between Teammates using Write-Ahead Logging (WAL).
- Ensuring data integrity so that no two Teammates claim the same URL (Loop Prevention via `UNIQUE` constraints and `status` codes).
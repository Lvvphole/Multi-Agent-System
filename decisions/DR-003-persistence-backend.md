# DR-003 — Persistence backend (partially resolves B-003)

date: 2026-06-19
status: ACCEPTED (approach pinned; operational specifics still owner/Stage 9)
class: MINOR
partially_supersedes_blocker: B-003

## Decision
Persistence approach (consistent with DR-002 / DBOS):
- Local/dev + reference impl: file-backed JSON (current harness) and/or SQLite.
- Production: PostgreSQL. State store, artifact manifest, run history, checkpoints,
  and the append-only logs become Postgres tables. DBOS already journals workflow
  state to Postgres, so step durability and our domain state commit together
  (exactly-once for Postgres-local writes).

The Stage 4 schemas are storage-agnostic (JSON Schema), so the same record shapes
serialize to JSON files, SQLite rows, or Postgres rows without redefinition.

## Still open (owner / Stage 9)
- Managed (e.g. RDS/Cloud SQL/Neon/Databricks Lakebase) vs self-hosted Postgres.
- Sizing, retention windows, backup/DR, and multi-tenant isolation.
- These are deployment/budget decisions tracked under B-005, not pinned here.

# DR-002 — Durable orchestration engine (resolves B-004)

date: 2026-06-19
status: ACCEPTED (default; reversible — see migration path)
class: MINOR (design decision; no security/deletion impact)
supersedes_blocker: B-004

## Decision
Durable runtime = DBOS Transact (Python), embedded library backed by Postgres
(SQLite for local/dev). The contract harness remains the control/gate layer on
top; DBOS provides durability primitives only and does NOT own gate logic.

Layering:
- DBOS owns: step checkpointing, automatic retries, durable timers, durable
  waits/signals (human-in-the-loop), exactly-once step journaling.
- Harness owns (unchanged, in reviewable code): stage state machine, gate
  decisions, structural + alternate-judge verification, anti-compression,
  evidence/manifest, release lock. This preserves DETERMINISM_LOCUS.

Mapping to requirements:
- R-F-006 / R-F-014 (no duplicate side effects / restart recovery): LLM judge
  calls and tool calls become DBOS @steps, journaled on first run, never re-run
  on replay. Idempotency keys derived from (workflow_id, step_id).
- R-F-010 (human-in-the-loop): the approval gate becomes a DBOS durable wait
  (workflow.recv / sleep) rather than a busy loop — idle cost drops ~60-80%.
- State store / artifact manifest / gate log move from JSON files to Postgres
  tables (formalized at Stage 4); step writes + durability record commit in the
  same transaction (exactly-once).

## Rationale
- Minimal operational footprint: one Postgres, one deploy, no separate
  orchestration server. ~7 LoC to adopt vs rearchitecting for a server-based
  engine.
- Library (not server) keeps control logic in-process and reviewable.

## Override conditions (when to pick something else)
- Temporal: cross-service orchestration, multi-language workers, months-long
  workflows, or enterprise-scale fan-out. Migration blast radius = one module if
  workflow code is kept behind an interface (mandated below).
- Restate: edge/serverless deployment targets where even Postgres is too heavy.

## Mandate
Workflow entry points MUST sit behind a thin `DurableRuntime` interface so the
engine can be swapped without touching gate logic. (Interface defined at Stage 3.)

## What is NOT done here (requires owner / later stage)
- No infrastructure is provisioned (no Postgres stood up, no deploy). B-003
  (persistence backend at scale) and B-005 (deployment target/budget) remain
  open and are Stage 4 / Stage 9 decisions.

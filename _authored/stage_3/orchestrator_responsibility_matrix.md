# orchestrator_responsibility_matrix.md

artifact_id: stage3.orchestrator_responsibility_matrix
stage: stage_3
owner: Executor
version: 2.1.0

Maps each orchestrator responsibility to its mechanism, the layer that owns it,
and the DurableRuntime method that exposes it. "Owned by" distinguishes what the
durable engine (DBOS) provides from what the harness governs — the engine never
owns gate logic.

| Responsibility | Mechanism | Owned by | DurableRuntime method |
| --- | --- | --- | --- |
| Scheduling | cron/interval/backpressure | engine | schedule() |
| Events | event source + idempotent delivery | engine | send_signal()/wait_signal() |
| Retries | per-policy retry with backoff | engine | run_step() (retry wraps step) |
| Concurrency | scope locks (see below) | engine | acquire_concurrency_lock() |
| Checkpointing | per-step durable journal | engine | run_step()/record_checkpoint() |
| Observability | traces, run history, retry/failure logs, lineage | engine + harness | get_run_history() |
| Hot deployment | versioned skills/loops; frozen version per run | harness | (version freeze; new lineage) |
| Gate decisions | stage pass/fail/escalate | HARNESS ONLY | (not exposed to engine) |

## Concurrency rules

- Singleton: at most one instance of a singleton workflow runs at a time
  (e.g. the release gate). Conflicting starts are rejected.
- Per-agent: one active workflow per agent role unless explicitly parallel.
- Per-skill: bounded parallelism per skill id (configurable).
- Per-resource: mutual exclusion on a named resource (e.g. state_store write).
- Per-run: a run id holds its own locks; restart re-acquires, does not duplicate.
- Conflict resolution: queue | reject | cancel | escalate (declared per lock).

## Hot deployment rules

- A new skill/loop version never mutates an in-flight run; in-flight runs keep
  their frozen version (run lineage). New runs pick up the new version.
- Activating a new skill version requires SELF_LEARNING_VALIDATION (A4):
  held-out gate + attempt bar + half-life, plus Verifier/Evaluator GREEN.
- Deprecation/removal of a deployed skill is DESTRUCTIVE -> HUMAN_IN_THE_LOOP.

## Engine boundary

The orchestrator depends only on the DurableRuntime interface. Swapping DBOS for
Temporal/Restate replaces one adapter module and touches no gate logic, loop
decision functions, or skill contracts.

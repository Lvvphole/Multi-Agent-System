# loop_skill_orchestrator_model.md

artifact_id: stage3.loop_skill_orchestrator_model
stage: stage_3
owner: Executor
version: 2.1.0

Defines the system as three separated concerns — loops, skills, and the
orchestrator — and the `DurableRuntime` interface (DR-002) that decouples the
control logic from the durable-execution engine (DBOS by default).

## SEPARATION RULES

- A LOOP decides. It is a pure decision function over persisted state: it reads
  state, evaluates decision points, and emits the next action. A loop performs
  NO side effects and owns NO durability. (perceive -> reason -> act -> observe.)
- A SKILL does durable work. It is a versioned, reusable workflow with explicit
  input/output contracts and retry behavior, executed as durable steps. Skills
  are the units the self-learning loop improves (subject to SELF_LEARNING_
  VALIDATION / A4 before activation).
- The ORCHESTRATOR runs things. It schedules loops, delivers events, applies
  retries, enforces concurrency, persists checkpoints, emits observability, and
  governs hot deployment — all via the DurableRuntime.
- No layer reaches into another: loops never call the engine directly (they
  return actions), skills never make gate decisions, the orchestrator never
  authors artifacts. Handoffs go loop -> (action) -> orchestrator -> skill ->
  (result) -> state -> loop.

## LOOP LAYER

- Triggers: what starts a loop pass — scheduled (cron/interval), event-driven
  (state change, message), or manual (explicit user/owner trigger).
- Decision points: the branch conditions evaluated each pass (e.g. "is prior
  stage PASSED?", "are required artifacts present?", "is an escalation open?").
- State reads: the persisted inputs a loop reads (state store, project_memory,
  gate log) — never in-context model memory.
- Next-action logic: the mapping from (state, decision points) to exactly one
  next action, or STOP, or ESCALATE. Deterministic given the same state.
- Loops are registered per loop_registry_schema.json.

## SKILL LAYER

- Durable workflows: each skill is a durable workflow whose steps are journaled;
  on replay, completed steps are not re-run.
- Retry behavior: per-skill retry policy (max retries, backoff, retry scope,
  idempotency) with escalation on exhaustion.
- Input contract: a named schema the skill's input is validated against before
  execution.
- Output contract: a named schema the skill's output is validated against before
  it can affect state.
- Skills are registered per skill_registry_schema.json (carries A4 validation
  fields: performance metric, held-out validation, attempt bar, half-life).

## ORCHESTRATOR LAYER

- Scheduling: when loops/skills run (intervals, cron, backpressure).
- Events: event sources, delivery, and idempotent handling.
- Retries: orchestrator-level retry of failed steps per policy.
- Concurrency: singleton / per-agent / per-skill / per-resource / per-run locks.
- Checkpointing: per-step durable checkpoints (input, output, status, retry
  count, error, checkpoint id, idempotency key).
- Observability: step traces, run history, retry/failure logs, artifact lineage,
  agent decision records.
- Hot deployment: rules for deploying new skill/loop versions without disrupting
  in-flight runs (frozen version per run; new lineage for new versions).

## DurableRuntime INTERFACE  (DR-002 mandate)

A thin interface so the engine (DBOS default; Temporal/Restate alternative) is
swappable with a one-module blast radius. The harness/loops depend on this
interface, never on the engine directly.

```
class DurableRuntime(Protocol):
    def start_workflow(workflow_id, fn, *args) -> handle
    def run_step(step_id, fn, *args) -> result      # journaled; idempotent on replay
    def durable_sleep(seconds) -> None               # survives restart
    def wait_signal(signal_name, timeout=None)       # human-in-the-loop approvals
    def send_signal(workflow_id, signal_name, payload)
    def record_checkpoint(checkpoint) -> None
    def resume(workflow_id) -> handle                # from last successful step
    def schedule(loop_id, trigger_spec) -> None
    def get_run_history(workflow_id) -> list
    def acquire_concurrency_lock(scope, key) -> bool # singleton/per-*/queue
```

Engine binding (DBOS): run_step -> @DBOS.step (journaled, exactly-once for
Postgres-local writes); wait_signal -> durable recv; durable_sleep -> DBOS sleep;
get_run_history -> DBOS system tables. The binding lives in one adapter module;
the gate logic in the harness never imports DBOS directly.

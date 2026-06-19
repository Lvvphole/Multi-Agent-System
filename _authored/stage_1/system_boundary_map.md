# system_boundary_map.md

artifact_id: stage1.system_boundary_map
stage: stage_1
owner: Executor
version: 2.0.0
architecture_decisions: deferred_to_stage_2

Defines what is inside the control system versus outside it, and the trust
boundaries that cross the line. This is descriptive only; no internal
architecture/technology choice is made here (deferred to Stage 2+).

## BOUNDARY

The boundary encloses the contract-governed control system: the harness process,
all agent roles, all persistent stores, and all logs/artifacts produced under
CONTRACT.md. The boundary is the line at which untrusted model output enters
(and is validated) and at which external side effects leave (and are gated by
idempotency + human approval). Anything whose behavior the system cannot make
deterministic by code is OUTSIDE the boundary.

## INTERIOR

Components inside the boundary (code + persisted artifacts, deterministic):

- Contract Controller — validates contract structure/version.
- Deterministic Harness — the control process; decides legality of every step.
- State Store — persisted stage states + run metadata.
- Gate Controller — marks stage transitions from evidence.
- Planner — selects next legal stage/artifact (no execution).
- Executor — drafts artifacts only (no verify/evaluate/approve/complete).
- Artifact Manager + Artifact Store — manifest, checksums, lineage.
- Verifier (structural layer) — code-only artifact checks.
- Evaluator (orchestration role) — routes artifacts to the alternate-model judge.
- Memory Manager — project_memory.md, failure patterns.
- Escalation Manager — handles missing inputs/evidence/repeat failures.
- Orchestrator — checkpoints, retries, run history, concurrency, resume.
- Skill Registry + Self-Learning Reviewer — proposes (never activates) changes.
- Security Manager — tool permissions, secret scoping, audit logs.
- Release Gate — final mechanical lock.
- Replay log / gate log / judge log / approval log — append-only evidence.

## EXTERIOR

Actors and systems outside the boundary (non-deterministic or human-controlled):

- Human Owner — approves autonomy/irreversible/MAJOR/DESTRUCTIVE changes.
- Model Provider — LLM endpoints, including the alternate-model Verifier judge
  and Evaluator judge. NOTE: the judge ROLES are interior; the judge MODELS are
  exterior and their output is untrusted until validated.
- External Tools / APIs — anything the system calls out to.
- Repository Remote (GitHub) — push/PR is an external side effect.
- Deployment / Runtime Target — exterior; reached only after Stage 11 authz.
- Secret Store — exterior; access scoped + logged + approval-gated.

## EXTERNAL SYSTEMS

Enumerated boundary crossings and their controls:

- X-1 Model Provider (inbound model output): UNTRUSTED -> schema validation
  before it can affect state (R-F-009).
- X-2 Repo Remote (outbound write): external side effect -> idempotency key +
  human approval (R-F-010).
- X-3 External Tools/APIs (outbound): idempotency key; destructive/irreversible
  variants -> human approval.
- X-4 Deployment Target (outbound): locked until Stage 11 authorized + approval.
- X-5 Secret Store (inbound secret): scoped read, logged, never written to
  artifacts or logs.
- X-6 Human Owner (bidirectional): approvals recorded in human_approval_log.jsonl.

## TRUST BOUNDARIES

- Inbound rule: everything crossing inward (model output, tool results, external
  data) is untrusted and must be validated by code before affecting state.
- Outbound rule: everything crossing outward (writes, messages, deploys) is a
  side effect requiring an idempotency key; irreversible/destructive variants
  additionally require a human approval record bound to exact checksums.

# Multi-Agent-System — Deterministic Control Harness

A code-resident control layer for a meta-loop, self-learning multi-agent system,
governed by `CONTRACT.md` (v2.0.0). Determinism lives in code (state store,
state machine, schema validators, append-only logs), not in any model's claims.

# Multi-Agent-System

A deterministic control harness for a meta-loop, self-learning multi-agent system.

This repository implements a code-resident control layer for multi-agent execution. The core rule is simple:

```text
The model does not determine completion.
The harness does.
```

Determinism is enforced through executable code, state stores, state machines, schema validators, artifact records, idempotency ledgers, replay logs, checksums, verifier gates, evaluator gates, and human approval gates.

Model output is treated as a proposal until the harness validates it against real artifacts on disk.

## Purpose

`Multi-Agent-System` exists to solve a common AI agent failure mode:

```text
A model claims that a stage passed,
but there is no durable state,
no artifact evidence,
no verifier record,
no evaluator approval,
no replay log,
and no release gate.
```

This repo turns that soft-prompt failure pattern into a code-governed control system.

The goal is not to make the model sound deterministic.

The goal is to make the surrounding harness enforce sequence, evidence, validation, recovery, and completion rules without trusting the model’s own claims.

## Core Principle

```text
Advisory prose is not a harness.
```

A correct harness must be able to answer:

* What stage is currently running?
* What artifacts were produced?
* Which checks passed?
* Which checks failed?
* What version of the contract was used?
* What state transition happened?
* What evidence exists on disk?
* Can the system resume after interruption?
* Can completion be proven without relying on the model?

If the model is shut off mid-run, the harness should still be able to report state, recover from checkpoints, and prove what passed.

## What This Repo Contains

```text
Multi-Agent-System/
├── _authored/
├── artifacts/
├── decisions/
├── harness/
├── tests/
├── .gitignore
├── COMMIT_GUIDE.md
├── CONTRACT.md
├── LICENSE
├── README.md
├── project_memory.md
├── run_stage0.py
├── run_stage1.py
├── run_stage2.py
├── run_stage3.py
└── run_stage4.py
```

## Harness Responsibilities

The harness is responsible for:

* Contract version control
* Stage order enforcement
* State-machine execution
* Gate-controlled transitions
* Artifact existence checks
* Artifact checksum tracking
* Schema validation
* Idempotency keys
* Replayable logs
* Restart recovery
* Version freezing
* Verifier separation
* Evaluator separation
* Human-in-the-loop gates
* Completion blocking until all required evidence exists

## Architecture

```text
Human Owner
    ↓
Contract Controller
    ↓
Deterministic Harness
    ↓
State Store
    ↓
Gate Controller
    ↓
Planner
    ↓
Executor
    ↓
Artifact Manager
    ↓
Artifact Store
    ↓
Verifier
    ↓
Evaluator
    ↓
Memory Manager
    ↓
Escalation Manager
    ↓
Release Gate
```

The model may propose actions, draft artifacts, analyze inputs, and recommend next steps.

The harness decides whether a stage can run, whether output is valid, whether artifacts count as evidence, whether state can transition, and whether release is blocked.

## Key Concepts

### Code-Resident Determinism

Determinism lives in code, not in model claims.

The harness uses persistent state, schema validation, checksums, idempotency records, and append-only logs to create durable evidence.

### State Gates

Stages cannot be skipped.

A stage can only pass when its required artifacts exist, validation succeeds, verifier checks pass, evaluator approval exists, and no unresolved escalation blocks the transition.

### Artifact Evidence

Artifacts must exist as real files or structured records.

Summaries, placeholders, intentions, and assistant explanations do not count as evidence.

### Verifier Independence

The Executor cannot verify its own work.

Verifier checks are separate from execution and must inspect actual artifacts, not Executor explanations.

### Evaluator Independence

The Evaluator scores only verifier-approved evidence against the contract success criteria.

The Evaluator cannot accept usefulness, confidence, or model explanation as proof.

### Idempotency

Side effects must be tracked so repeated execution does not create duplicate artifacts, duplicate state transitions, or duplicated tool calls.

### Replayability

Run logs and state records must survive restart.

The harness should be able to reconstruct what happened from disk.

### Human-in-the-Loop Gate

External, irreversible, destructive, or major security-related actions require explicit human approval before execution or release.

## Current Executable Baseline

The repository includes:

* `harness/` control modules
* Stage runner scripts
* Contract-governed execution files
* Artifact and decision folders
* Project memory
* Guardrail tests
* Commit guidance

The current README baseline documents Stage 0 contract verification and harness guardrail tests.

## Running the Harness

Run Stage 0 contract verification:

```bash
python3 run_stage0.py
```

Run the harness tests:

```bash
python3 tests/test_harness.py
```

Expected behavior:

* Gate order is enforced
* Stage skipping is rejected
* Placeholder artifacts are rejected
* Empty artifacts are rejected
* Invalid state transitions fail closed
* Executor self-certification is blocked
* Idempotent artifact writes avoid duplicate side effects
* Restart recovery reads state from disk
* Bad model output is rejected by schema validation

## Contract

The system is governed by:

```text
CONTRACT.md
```

The contract defines:

* Objective
* Desired state
* Harness determinism layer
* Stage gates
* Success criteria
* Evidence requirements
* Constraints
* Autonomy boundaries
* Verifier rules
* Evaluator rules
* Human approval gates
* Stop conditions
* Escalation conditions
* Role permissions
* Memory rules
* Completion authority

## Completion Authority

No model or agent may unilaterally declare completion.

Completion requires:

* Required stages passed
* Required artifacts present
* Artifact records updated
* Checksums recorded
* Schema validation passed
* Verifier approval
* Evaluator approval
* Required human approval records
* Release gate passed
* Zero unresolved escalations

Until those conditions are satisfied, the system is not complete.

## What This Is Not

This repo is not:

* A chatbot prompt
* A roleplay framework
* A simple agent demo
* A one-pass autonomous coding script
* A replacement for CI/CD
* A replacement for security review
* A replacement for human approval on destructive actions

It is a control harness for making multi-agent execution inspectable, gated, restart-safe, and evidence-driven.

## Intended Use Cases

Use this repo for:

* Multi-agent system control
* Deterministic harness design
* Agent workflow governance
* State-machine-based AI execution
* Evidence-gated automation
* Verifier and evaluator separation
* Self-learning agent governance
* Safe staged execution
* Agent release gating
* Research into code-resident AI control systems

## Guardrail Philosophy

The system fails closed.

That means when evidence is missing, state is invalid, schema validation fails, approval is absent, or a model attempts self-certification, the correct outcome is not “continue anyway.”

The correct outcome is:

```text
BLOCK
ESCALATE
REQUIRE EVIDENCE
```

## License

GPL-3.0 License

## Status

Early-stage deterministic control harness for meta-loop multi-agent execution.

The repository currently establishes the contract, harness structure, staged execution files, project memory, artifacts, decisions, and guardrail testing baseline.


## What runs today
- `harness/` — state store, state machine + gate controller, idempotency ledger,
  append-only replay log, version freeze + checksums, schema validator, artifact
  store, two-layer Verifier/Evaluator (code structural checks + alternate-model
  LLM judge), human-in-the-loop gate, and the `Harness` orchestrator.
- `harness/stage0.py` + `run_stage0.py` — Stage 0 contract verification as code.
- `tests/test_harness.py` — 9 guardrail tests, all passing.

## Run
```
python3 run_stage0.py          # verify the contract, emit Stage 0 artifacts
python3 tests/test_harness.py  # prove guardrails fail closed
```

## Guardrails proven by tests
gate-order (no stage skipping), alternate-judge enforcement (no self-judging),
placeholder/empty-artifact rejection, verify-judge RED fails closed,
human-gate block on DESTRUCTIVE change + approval-bound release, idempotent
artifact writes (no duplicate side effects), restart recovery from disk,
illegal state transitions rejected, schema validation rejects bad model output.

## Not yet built (staged, not compressed)
Stages 1-13 artifact set; real alternate-model judge wiring (currently
deterministic stubs, clearly marked); orchestration/recovery/concurrency specs;
self-learning loop; skill registry; full security boundary + audit schema.

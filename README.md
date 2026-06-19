# Multi-Agent-System — Deterministic Control Harness

A code-resident control layer for a meta-loop, self-learning multi-agent system,
governed by `CONTRACT.md` (v2.0.0). Determinism lives in code (state store,
state machine, schema validators, append-only logs), not in any model's claims.

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

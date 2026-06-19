# input_output_contract.md

artifact_id: stage1.input_output_contract
stage: stage_1
owner: Executor
version: 2.0.0
architecture_decisions: deferred_to_stage_2

System-level inputs, outputs, and transformations. Per-stage I/O is summarized;
detailed per-agent I/O schemas are produced in Stage 6 (agent_io_schema_registry).

## INPUTS

- I-1 Task/objective — the build/audit/design request that triggers the loop.
- I-2 CONTRACT.md — versioned governing contract (frozen per run by checksum).
- I-3 Run context — frozen contract/prompt/skill/tool/model versions + input
  checksum (run_context_snapshot).
- I-4 Human approval records — APPROVE/REJECT/DEFER bound to checksums.
- I-5 Prior state — state_store.json + project_memory.md (for resume).
- I-6 Judge verdicts — GREEN/RED + justification from alternate-model judges
  (untrusted until recorded with a session id).

## OUTPUTS

- O-1 Stage artifacts — the files named in EVIDENCE_REQUIRED, produced separately.
- O-2 Artifact manifest — filename/owner/stage/checksum/version/verify/eval status.
- O-3 Logs — gate_state_log.jsonl, judge_session_log.jsonl,
  human_approval_log.jsonl, idempotency.json (append-only / atomic).
- O-4 Reports — verification_report.md, evaluation_report.md (later stages).
- O-5 Release package manifest — emitted only when the generation lock releases.
- O-6 Escalations — structured blockers raised to the Escalation Manager / Human.

## TRANSFORMATIONS

Core transform (every stage): Executor proposal + harness/judge validation ->
accepted artifact + state transition. No proposal becomes state without
validation.

- T-1 contract -> requirements (Stage 1).
- T-2 requirements -> role/agent model (Stage 2).
- T-3 roles -> loop/skill/orchestrator architecture (Stage 3).
- T-4 architecture -> state/memory/artifact store design (Stage 4).
- T-5 design -> durable execution/recovery design (Stage 5).
- T-6 -> harness determinism design (Stage 6).
- T-7 -> self-learning loop design (Stage 7).
- T-8 -> security/tool/approval boundaries (Stage 8).
- T-9 -> implementation plan (Stage 9).
- T-10 -> test/verification design (Stage 10).
- T-11 plan -> build (Stage 11, authorized).
- T-12 build -> system verification (Stage 12).
- T-13 verified system -> evaluation + release decision (Stage 13).

## PER-STAGE I/O (summary)

| stage | primary inputs | primary outputs |
| --- | --- | --- |
| 0 | CONTRACT.md, run context | checklist, traceability table |
| 1 | contract, requirements signals | requirements, boundary, I/O, constraints |
| 2 | stage 1 artifacts | role registry, permission matrix, handoff, forbidden |
| 3 | stage 2 artifacts | loop/skill/orchestrator model + schemas |
| 4 | stage 3 artifacts | state/memory/artifact/run/checkpoint schemas |
| 5 | stage 4 artifacts | orchestration/recovery/failure/concurrency policies |
| 6 | stage 5 artifacts | harness spec/state machine/idempotency/version/schema |
| 7 | stage 6 artifacts | self-learning spec, skill version log, rollback |
| 8 | stage 7 artifacts | security/tool/approval/audit |
| 9 | stages 0-8 | implementation/milestone/dependency/budget/tooling |
| 10 | stage 9 | test plan, verification/evaluation protocol, acceptance matrix |
| 11 | stage 10 (authorized) | source, config, schemas, tests, build logs |
| 12 | stage 11 | test results, verification + audit reports |
| 13 | stage 12 | evaluation report, release gate report, release manifest |

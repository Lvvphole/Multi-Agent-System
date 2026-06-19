# multi_agent_requirements.md

artifact_id: stage1.multi_agent_requirements
stage: stage_1
owner: Executor
version: 2.0.0
architecture_decisions: deferred_to_stage_2

Requirements for the meta-loop, self-learning multi-agent control system. Every
requirement is testable (each carries a `verify:` clause naming how it is
checked). Requirements that cannot be finalized without an external/owner
decision are recorded under BLOCKERS and are NOT guessed.

ROLES referenced here are defined in CONTRACT.md > ROLES (Contract Controller,
Harness, Planner, Executor, Verifier, Evaluator, Gate Controller, Memory
Manager, Escalation Manager, Orchestrator, Artifact Manager, Skill Manager,
Self-Learning Reviewer, Security Manager, Human Owner).

TOOLS referenced here: file/artifact store, schema validator, checksum function,
append-only logger, alternate-model judge endpoint, human-approval recorder,
(future) skill registry, (future) durable orchestration engine.

## FUNCTIONAL REQUIREMENTS

- R-F-001 The system SHALL represent stages 0-13 as persisted state with enum
  {LOCKED,RUNNING,PASSED,FAILED,ESCALATED}.
  verify: inspect state_store.json; assert 14 stages, each enum-valid.
- R-F-002 The system SHALL block a stage from starting unless its prior required
  stage is PASSED.
  verify: test_gate_order_no_skip.
- R-F-003 A stage PASS SHALL require structural-verify PASS AND alternate-model
  Verifier GREEN AND Evaluator GREEN.
  verify: state record verifier_result/evaluator_result + judge_session_log.
- R-F-004 The Executor SHALL hold no verify/evaluate/gate/completion permission.
  verify: role_permission_matrix (Stage 2) + harness has no such Executor path.
- R-F-005 The system SHALL reject any judge whose model id equals the Executor's.
  verify: test_self_judging_blocked.
- R-F-006 Every side effect SHALL carry an idempotency key; duplicates SHALL be
  skipped after restart.
  verify: test_idempotency_no_duplicate_write.
- R-F-007 The system SHALL persist an append-only replay log sufficient to
  reconstruct the run path with no model in the loop.
  verify: gate_state_log.jsonl contains transitions + gate decisions.
- R-F-008 The system SHALL freeze contract/prompt/skill/tool/model versions and
  input checksum per run; any change SHALL create a new run lineage.
  verify: run_context_snapshot run_id changes when contract checksum changes.
- R-F-009 Model output SHALL be schema-validated before it affects state.
  verify: test_schema_validation_rejects_bad_output.
- R-F-010 MAJOR/DESTRUCTIVE actions SHALL require a recorded human approval bound
  to exact artifact checksums before they execute.
  verify: test_human_gate_blocks_destructive.
- R-F-011 The artifact manifest SHALL record filename, owner, stage, checksum,
  version, verification status, evaluator status for every artifact.
  verify: artifact_manifest.json entries complete (structural verifier).
- R-F-012 Final release SHALL be blocked until all required gates pass and all
  required approvals are recorded.
  verify: Stage 13 release-gate test (deferred to Stage 10/13).
- R-F-013 A self-learning review loop SHALL read run history and propose skill
  changes that cannot activate without versioning, tests, verification,
  evaluation, and a rollback path.
  verify: Stage 7 self_learning test + skill_version_log (deferred).
- R-F-014 The system SHALL resume from the last successful checkpoint after a
  process restart with no duplicate side effects.
  verify: test_restart_recovery.
- R-F-015 On missing evidence, missing requirements, repeated failure (3x),
  iteration limit, or invalid transition, the system SHALL escalate rather than
  guess or hallucinate.
  verify: escalation paths in harness + Stage 10 escalation tests.

## NON-FUNCTIONAL REQUIREMENTS

- R-N-001 Determinism locus: control decisions SHALL be made by code, not model
  assertion.
  verify: kill model mid-run; harness reports state and resumes from disk.
- R-N-002 Anti-compression: required artifacts SHALL remain separate; token
  pressure SHALL trigger continuation/escalation, never merge/omit.
  verify: Stage 6/10 compression test (deferred) + structural verifier.
- R-N-003 Observability: every step SHALL emit a trace record (role, action,
  in/out refs, timestamp, artifact ref).
  verify: Stage 4 trace_schema coverage (deferred).
- R-N-004 Concurrency safety: singleton/per-agent/per-skill/per-resource/per-run
  rules SHALL prevent conflicting concurrent execution.
  verify: Stage 5 concurrency_policy + test (deferred).
- R-N-005 Auditability: all role actions SHALL be logged with role, action,
  input ref, output ref, timestamp, artifact ref.
  verify: Stage 8 audit_log_schema (deferred).

## BLOCKERS

These requirements depend on an external/owner decision and are intentionally
left unresolved (not guessed) per CONTRACT.md constraints 24-25.

- B-001 Production runtime/language for the harness. Reference impl is Python;
  production target unconfirmed. status: BLOCKER. resolve_by: Stage 9. owner: Human Owner.
- B-002 Model provider(s) and the concrete model identities for the
  alternate-model Verifier judge and Evaluator judge. status: BLOCKER.
  resolve_by: before real judge wiring. owner: Human Owner.
- B-003 Persistence backend for state/artifact store at scale (file vs DB vs
  object store). status: BLOCKER. resolve_by: Stage 4. owner: Human Owner.
- B-004 Durable orchestration engine (custom loop vs Temporal/Restate/etc.).
  status: BLOCKER. resolve_by: Stage 3/5. owner: Human Owner.
- B-005 Deployment target and implementation budget. status: BLOCKER.
  resolve_by: Stage 9/11. owner: Human Owner.
- B-006 Secret-management system and sandbox boundary specifics. status: BLOCKER.
  resolve_by: Stage 8. owner: Human Owner.

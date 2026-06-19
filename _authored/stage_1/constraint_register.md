# constraint_register.md

artifact_id: stage1.constraint_register
stage: stage_1
owner: Executor
version: 2.0.0
architecture_decisions: deferred_to_stage_2

Enumerated constraints traced to CONTRACT.md > CONSTRAINTS. Each is testable
(carries a `verify:` clause). These bind every later stage.

- CN-01 External control sequence outranks answer usefulness.
  verify: control-priority test fails closed (Stage 10).
- CN-02 The deterministic harness (code) controls execution.
  verify: harness mediates every transition (no direct store writes by Executor).
- CN-03 The model SHALL NOT control state transitions.
  verify: only StateMachine.transition mutates state enum.
- CN-04 The model SHALL NOT control completion.
  verify: completion only via mechanical stop conditions (Stage 13).
- CN-05 The model SHALL NOT bypass schema validation.
  verify: test_schema_validation_rejects_bad_output.
- CN-06 No early artifact release.
  verify: generation lock blocks until gates pass (Stage 13).
- CN-07 No required-artifact compression.
  verify: structural verifier rejects merged/placeholder artifacts.
- CN-08 No replacing missing evidence with explanation.
  verify: missing artifact -> structural FAIL (test_placeholder_artifact_fails).
- CN-09 Executor cannot determine completion.
  verify: COMPLETION_AUTHORITY; no Executor completion path.
- CN-10 Executor cannot verify its own work.
  verify: test_self_judging_blocked + role_permission_matrix (Stage 2).
- CN-11 Evaluator cannot rely on Executor explanations.
  verify: judge reviews artifact text only; Stage 2 forbidden-actions register.
- CN-12 Useful output cannot override gate order.
  verify: gate-order test + control-priority test.
- CN-13 Subjective pass language forbidden as a pass criterion.
  verify: Stage 0 check C0.3.
- CN-14 Each success criterion maps to concrete evidence.
  verify: Stage 0 check C0.2 + acceptance_test_matrix (Stage 10).
- CN-15 Every artifact has filename/stage/owner/checksum/version/verify status.
  verify: artifact_manifest schema (structural verifier).
- CN-16 Required artifacts stay separate unless explicitly permitted to combine.
  verify: structural verifier 1 file per required artifact id.
- CN-17 Self-learning changes are versioned/tested/verified/evaluated/rollback.
  verify: Stage 7 self_learning test (deferred).
- CN-18 Durable execution includes checkpoint/retry/run-history/idempotency/fail.
  verify: Stage 5 + restart/idempotency tests.
- CN-19 Sub-agents have explicit parent-child lifecycle rules.
  verify: Stage 2/5 lifecycle spec (deferred).
- CN-20 Tool use optimizes artifact fidelity, not speed/convenience.
  verify: Stage 8 tool_permission_matrix review.
- CN-21 Autonomy: 3 in workspace, 2 external (per AUTONOMY_LEVEL v2.0.0).
  verify: external/destructive paths require human approval record.
- CN-22 File creation/build loop authorized in workspace; external/irreversible
  actions gated.
  verify: human gate test + no remote-write path without approval.
- CN-23 Token pressure -> continuation/escalation, not compression.
  verify: structural verifier + Stage 6 token-pressure rule.
- CN-24 Missing evidence -> escalation, not hallucination.
  verify: R-F-015 escalation paths.
- CN-25 Missing requirements -> escalation, not guessing.
  verify: BLOCKERS section present (this stage) instead of guessed values.
- CN-26 Non-deterministic output validated before affecting state.
  verify: CN-05 + R-F-009.
- CN-27 External side effects require idempotency.
  verify: idempotency ledger on every side effect (R-F-006).
- CN-28 Irreversible external side effects require human approval.
  verify: R-F-010 human gate.
- CN-29 Version changes create new run lineage.
  verify: R-F-008 run_id changes on checksum change.
- CN-30 Replay logs survive process restart.
  verify: R-F-014 restart recovery reads logs from disk.
- CN-31 Judge model differs from the model that produced the artifact.
  verify: R-F-005 self-judging block.

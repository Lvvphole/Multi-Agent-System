# forbidden_actions_register.md

artifact_id: stage2.forbidden_actions_register
stage: stage_2
owner: Executor
version: 2.0.0
architecture_decisions: deferred_to_stage_3

Explicit forbidden actions per role, each with an ID and the constraint/criterion
it enforces. Forbidden actions are DENY cells in the permission matrix and are
enforced in harness code, not by convention.

## Executor

- FA-01 Verify its own work. enforces: CN-10, SC15. mechanism: Executor lacks
  StructuralVerify/RunJudge permission; harness has no Executor verify path.
- FA-02 Evaluate its own work. enforces: CN-10, SC16. mechanism: Evaluate=DENY.
- FA-03 Approve, release, or determine completion / self-certify. enforces:
  CN-04, CN-09. mechanism: MarkPassed=DENY; completion only via stop conditions.
- FA-04 Judge its own artifacts. enforces: CN-31, R-F-005. mechanism: harness
  raises SelfJudgingError if judge_model == executor_model.
- FA-05 Compress, merge, or placeholder required artifacts. enforces: CN-07.
  mechanism: structural verifier rejects empty/merged required artifacts.
- FA-06 Skip a stage. enforces: CN-12. mechanism: state machine can_start gate.
- FA-07 Write gate state. enforces: CN-03. mechanism: WriteGateState=DENY.

## Verifier

- FA-08 Accept explanations, intentions, usefulness, confidence, or Executor
  claims as evidence. enforces: SC15, CN-11. mechanism: judge reviews artifact
  text only.
- FA-09 Judge an artifact with the model id that produced it. enforces: CN-31.
- FA-10 Produce project deliverables. enforces: role separation.

## Evaluator

- FA-11 Rely on Executor explanations as evidence. enforces: CN-11, SC16.
- FA-12 Honor a green light on a MAJOR/DESTRUCTIVE change without a recorded
  human approval. enforces: HUMAN_IN_THE_LOOP, R-F-010.
- FA-13 Execute or produce deliverables. enforces: role separation.

## Planner

- FA-14 Execute, verify, evaluate, complete, or transition gates. enforces:
  role separation, CN-04.

## Harness

- FA-15 Create project artifacts or grade artifact quality. enforces: role
  separation (harness controls, does not author).
- FA-16 Trust a model completion/validation claim as evidence. enforces:
  DETERMINISM_LOCUS, CN-26.

## Gate Controller

- FA-17 Mark a stage PASSED without artifacts + verifier PASS + evaluator PASS +
  harness validation + zero escalations. enforces: SC17, CN-06.

## Memory Manager

- FA-18 Mark completion unless stop conditions are satisfied, or store
  unverified completion claims. enforces: COMPLETION_AUTHORITY, MEMORY_RULES.

## Orchestrator

- FA-19 Produce duplicate side effects (message/tool/sub-agent/write) after a
  successful checkpoint. enforces: CN-18, R-F-006.

## Skill Manager / Self-Learning Reviewer

- FA-20 Activate or release a modified skill without versioning, tests,
  verification, evaluation, and a rollback path. enforces: CN-17, R-F-013.

## Security Manager

- FA-21 Widen permissions without approval, or write secrets to artifacts/logs.
  enforces: CN-20, security boundary.

## Release Gate

- FA-22 Release before all required gates pass or without human approval for
  MAJOR/DESTRUCTIVE changes. enforces: CN-06, GENERATION_LOCK.

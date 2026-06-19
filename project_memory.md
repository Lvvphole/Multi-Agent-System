# project_memory.md

contract_version: 2.1.0

## COMPLETED_VERIFIED
- contract v2.1.0 (A1-A4); stages 0-4 PASSED (verifier=PASS, evaluator=PASS, gate=PASSED)
  - stage_0 contract_requirements_verification (C0.1-C0.13)
  - stage_1 system_boundary_and_requirements (4 artifacts; B-001..B-006 recorded)
  - stage_2 role_and_agent_model (4 artifacts; executor barred verify/eval/complete)
  - stage_3 loop_skill_orchestrator_architecture (4 artifacts; DurableRuntime; A4 skill gate)
  - stage_4 state_memory_and_artifact_stores (state_store_schema, memory_architecture,
    artifact_manifest_schema, run_history_schema, checkpoint_schema)
- coherence proven: live state_store (14 recs) + manifest (19 entries) validate
  against the authored Stage 4 schemas; locked as a test
- decisions: DR-001 (judges), DR-002 (DBOS), DR-003 (Postgres persistence approach)
- tests: 16/16 PASS

## IN_PROGRESS
- stage: stage_5_durable_execution_and_recovery_design (LOCKED, ready)
- owner: Planner -> Executor
- next gate: structural + stage-5 content checks + alternate-judge GREEN + evaluator GREEN

## BLOCKERS (open)
- B-001 production runtime/language (Stage 9)
- B-005 deployment target + budget (Stage 9/11)  [also gates B-003 operational specifics]
- B-006 secret management + sandbox (Stage 8)

## BLOCKERS (resolved)
- B-002 -> DR-001 ; B-004 -> DR-002 ; B-003 approach -> DR-003 (Postgres; ops specifics open under B-005)

## OPEN_OWNER_DECISIONS
- DR-001 evaluator model strength; judges live needs MAS_JUDGE_MODE=live + key
- PR: assistant cannot push; user opens PR (see COMMIT_GUIDE.md)

## NEXT_ACTIONS
- stage_5: orchestration_architecture.md, recovery_policy.md,
  failure_handling_policy.md, duplicate_side_effect_prevention.md, concurrency_policy.md
  (much already enforced in code: idempotency ledger, restart recovery test, state machine)

## KNOWN_FAILURE_PATTERNS
- (handled) missing sections; checker off-by-one (locate cols by header);
  str_replace dropped brace (re-view after edits); _authored dir missing before heredoc
- design rules: judges FAIL CLOSED; contract change -> Stage 0 re-verify;
  skill not 'active' without held-out validation (A4, schema-enforced);
  artifact registration records created_at

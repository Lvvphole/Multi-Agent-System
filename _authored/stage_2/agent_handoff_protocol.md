# agent_handoff_protocol.md

artifact_id: stage2.agent_handoff_protocol
stage: stage_2
owner: Executor
version: 2.0.0
architecture_decisions: deferred_to_stage_3

Defines every handoff: source role, target role, payload, precondition, and the
evidence recorded. A handoff is only valid if its precondition holds; the harness
mediates and logs each one. No role reaches into another's responsibilities.

## Per-stage loop handoffs

- H-1 Contract Controller -> Harness: payload=contract validity + run context.
  precondition=contract structure valid. record=run_context_snapshot.
- H-2 Harness -> Planner: payload=current state + autonomy. precondition=action
  permitted by autonomy level. record=gate_state_log.
- H-3 Planner -> Executor: payload=next legal stage + required artifact list.
  precondition=prior required stage PASSED. record=stage_attempt log.
- H-4 Executor -> Artifact Manager: payload=draft artifacts. precondition=stage
  is RUNNING. record=artifact registration (checksum/owner/stage/version).
- H-5 Artifact Manager -> Verifier: payload=registered artifacts + manifest.
  precondition=all required artifacts present and non-empty. record=manifest.
- H-6 Verifier(structural) -> Verifier(judge): payload=artifact text + criteria.
  precondition=structural PASS. record=judge_session_log (verify).
- H-7 Verifier -> Evaluator: payload=verifier-approved artifacts.
  precondition=structural PASS AND judge GREEN AND judge_model != executor_model.
  record=judge_session_log (eval).
- H-8 Evaluator -> Human Owner (conditional): payload=MAJOR/DESTRUCTIVE change
  summary + checksums. precondition=change classified MAJOR/DESTRUCTIVE.
  record=human_approval_log. (Skipped for MINOR changes.)
- H-9 Evaluator -> Gate Controller: payload=evaluation result.
  precondition=evaluator GREEN AND (no human gate OR human APPROVE recorded).
  record=gate decision.
- H-10 Gate Controller -> Memory Manager: payload=gate decision + artifact refs.
  precondition=stage PASSED. record=project_memory update.
- H-11 Memory Manager -> Planner: payload=updated state + next action.
  precondition=memory written. record=next_actions.
- H-12 any role -> Escalation Manager: payload=blocker/violation.
  precondition=missing evidence / repeated failure / invalid transition.
  record=escalation record (halts loop).

## Self-learning handoffs

- H-13 Orchestrator -> Self-Learning Reviewer: payload=run history.
  precondition=authorized review schedule or explicit trigger.
- H-14 Self-Learning Reviewer -> Skill Manager: payload=skill change proposal.
  precondition=proposal includes tests + rollback path.
- H-15 Skill Manager -> Verifier/Evaluator: payload=proposed skill + tests.
  precondition=version assigned. record=skill_version_log.
- H-16 Skill Manager -> Human Owner (conditional): payload=skill deprecation/
  removal. precondition=change is DESTRUCTIVE. record=human_approval_log.

## Handoff invariants

- A handoff never transfers a permission the source role lacks.
- The Verifier->Evaluator handoff (H-7) is hard-blocked if judge_model ==
  executor_model (alternate-judge rule).
- Any handoff whose precondition fails routes to H-12 (escalation), never
  proceeds on assumption.

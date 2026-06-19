# role_permission_matrix.md

artifact_id: stage2.role_permission_matrix
stage: stage_2
owner: Executor
version: 2.0.0
architecture_decisions: deferred_to_stage_3

Capability x role matrix. Cells: ALLOW (permitted), DENY (forbidden), APPROVAL
(permitted only with a recorded human approval bound to checksums). The matrix
is the human-readable companion to agent_role_registry.json; the harness enforces
it in code (e.g. only StateMachine.transition mutates gate state).

Capabilities: ReadState, WriteGateState, ProduceArtifact, RegisterArtifact,
StructuralVerify, RunJudge, Evaluate, MarkPassed, UpdateMemory, RaiseEscalation,
CallTool, SpawnSubAgent, ExternalAction, Approve.

| Role | ReadState | WriteGateState | ProduceArtifact | RegisterArtifact | StructuralVerify | RunJudge | Evaluate | MarkPassed | UpdateMemory | RaiseEscalation | CallTool | SpawnSubAgent | ExternalAction | Approve |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Human Owner | ALLOW | DENY | DENY | DENY | DENY | DENY | DENY | DENY | DENY | ALLOW | DENY | DENY | APPROVAL | ALLOW |
| Contract Controller | ALLOW | DENY | DENY | DENY | DENY | DENY | DENY | DENY | DENY | ALLOW | ALLOW | DENY | DENY | DENY |
| Harness | ALLOW | ALLOW | DENY | DENY | DENY | DENY | DENY | DENY | ALLOW | ALLOW | ALLOW | DENY | DENY | DENY |
| Planner | ALLOW | DENY | DENY | DENY | DENY | DENY | DENY | DENY | DENY | ALLOW | DENY | DENY | DENY | DENY |
| Executor | ALLOW | DENY | ALLOW | DENY | DENY | DENY | DENY | DENY | DENY | ALLOW | ALLOW | APPROVAL | DENY | DENY |
| Artifact Manager | ALLOW | DENY | DENY | ALLOW | DENY | DENY | DENY | DENY | DENY | ALLOW | ALLOW | DENY | DENY | DENY |
| Verifier | ALLOW | DENY | DENY | DENY | ALLOW | ALLOW | DENY | DENY | DENY | ALLOW | ALLOW | DENY | DENY | DENY |
| Evaluator | ALLOW | DENY | DENY | DENY | DENY | ALLOW | ALLOW | DENY | DENY | ALLOW | ALLOW | DENY | DENY | DENY |
| Gate Controller | ALLOW | ALLOW | DENY | DENY | DENY | DENY | DENY | ALLOW | DENY | ALLOW | DENY | DENY | DENY | DENY |
| Memory Manager | ALLOW | DENY | DENY | DENY | DENY | DENY | DENY | DENY | ALLOW | ALLOW | DENY | DENY | DENY | DENY |
| Escalation Manager | ALLOW | DENY | DENY | DENY | DENY | DENY | DENY | DENY | DENY | ALLOW | DENY | DENY | DENY | DENY |
| Orchestrator | ALLOW | DENY | DENY | DENY | DENY | DENY | DENY | DENY | ALLOW | ALLOW | ALLOW | APPROVAL | DENY | DENY |
| Skill Manager | ALLOW | DENY | DENY | DENY | DENY | DENY | DENY | DENY | DENY | ALLOW | ALLOW | DENY | DENY | DENY |
| Self-Learning Reviewer | ALLOW | DENY | DENY | DENY | DENY | DENY | DENY | DENY | DENY | ALLOW | DENY | DENY | DENY | DENY |
| Security Manager | ALLOW | DENY | DENY | DENY | DENY | DENY | DENY | DENY | DENY | ALLOW | ALLOW | DENY | APPROVAL | DENY |
| Release Gate | ALLOW | DENY | DENY | DENY | DENY | DENY | DENY | DENY | DENY | ALLOW | DENY | DENY | APPROVAL | DENY |

## Key invariants enforced by this matrix

- Executor: ProduceArtifact=ALLOW, but StructuralVerify/RunJudge/Evaluate/
  MarkPassed = DENY. The Executor cannot verify, evaluate, or complete its own
  work. (Enforces CN-09, CN-10, contract SC15.)
- Only Harness and Gate Controller may WriteGateState; the Executor and model
  never can. (Enforces CN-03, CN-04.)
- Verifier and Evaluator RunJudge=ALLOW but the harness rejects a judge whose
  model id equals the Executor's. (Enforces CN-31 / R-F-005.)
- Every ExternalAction cell is APPROVAL (never bare ALLOW), so external/
  irreversible actions always pass through the human gate. (Enforces CN-28.)
- Approve is ALLOW only for Human Owner.

## Human approval points (irreversible / external actions)

- HAP-1 Production release — Release Gate ExternalAction=APPROVAL.
- HAP-2 Deployment / remote repo push — Orchestrator/Executor ExternalAction=APPROVAL.
- HAP-3 Secret access widening, privilege/egress/auth change — Security Manager APPROVAL.
- HAP-4 Skill deprecation/removal and any DESTRUCTIVE change — APPROVAL.
- HAP-5 Honoring an Evaluator green light on a MAJOR/DESTRUCTIVE change — APPROVAL.

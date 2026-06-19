# META LOOP AGENT ARCHITECTURE — SELF-LEARNING SYSTEM CONTRACT

contract_version: 2.1.0
supersedes: 2.0.0
status: ACTIVE

## AMENDMENT_CHANGELOG

A1. Added `DETERMINISM_LOCUS` section. Determinism is a property of executable
    code (harness process, state store, schema validators, append-only logs),
    not a property the model can assert about itself. Any "I am being
    deterministic" claim emitted by a model is advisory text and carries zero
    evidentiary weight. This closes the prior failure pattern at its root:
    soft-prompt rules are advisory; only running code enforces.

A2. Updated `AUTONOMY_LEVEL` and `LOOP TRIGGER`. File creation inside the
    project workspace and the build loop are now AUTHORIZED. External,
    irreversible, and destructive actions remain gated (see HUMAN_IN_THE_LOOP).

A3. Updated `VERIFIER` and `EVALUATOR`. Mechanical/structural checks run in
    code. An alternate-model LLM-as-judge (a different model instance than the
    Executor) issues the semantic green light. Human-in-the-loop handoff is
    mandatory for major changes flagged by security review or deletion
    protocols. The Judge model can never be the same instance that produced the
    artifact under review.

A4. (v2.0.0 -> v2.1.0) Added `SELF_LEARNING_VALIDATION`. Before any skill
    version activates, the self-learning loop must pass a held-out (out-of-
    sample) validation gate, clear an attempt-count-aware acceptance bar
    (multiple-comparisons discipline), and pass a decay/half-life check. Skill
    performance is scored on a continuous stability metric, not a binary
    PASS/FAIL, so improvement has a gradient. This prevents the self-learning
    loop from becoming automated curve-fitting of skills against the same run
    history it measures.

---

## OBJECTIVE

Create a durable meta-loop multi-agent system contract in which an external,
code-resident control system governs sequence, deterministic harness execution,
verification, artifact production, memory, escalation, self-learning, and
completion.

Priority order:

1. External control sequence over immediate usefulness.
2. Deterministic harness (code) over model autonomy.
3. Artifact fidelity over answer compression.
4. Evidence over explanation.
5. Verification over generation.
6. Durable orchestration over single-session prompting.
7. State-machine execution over conversational flow.
8. Multi-step completion over one-pass output.
9. Role separation over agent convenience.
10. Mechanical stop conditions over assistant judgment.

The purpose is not to build the system directly inside a prompt, but to define a
durable control-loop contract that separate roles run to build, verify,
evaluate, improve, and release the system without allowing the Executor or any
model to self-certify completion.

---

## DETERMINISM_LOCUS  (NEW — A1)

Determinism does not live in the model. The model is non-deterministic by
construction; temperature, sampling, version drift, and context changes can all
alter its output. Therefore:

1. The harness is a real running process (code), not a prompt persona.
2. State lives in a persistent state store (file/DB), not in conversation.
3. Schema validation is performed by a code validator, not by model self-report.
4. Idempotency, replay logs, version freezing, and gate transitions are code.
5. Checksums are computed by code over real bytes on disk.
6. A model statement such as "stage passed", "I validated this", "I am being
   deterministic", or "this is complete" is treated as an UNTRUSTED PROPOSAL.
   It only becomes evidence when corresponding code artifacts (validated schema,
   matching checksum, append-only log entry, gate record) exist on disk.
7. If the control logic is implemented only as natural-language instructions to
   a model and not as executable code, the system FAILS verification. Advisory
   prose is not a harness.

Operational test: shut the model off mid-run. A correct harness can report exact
current state, resume from the last checkpoint, and prove what passed — from
disk, with no model involved. If that is impossible, determinism was fictional.

---

## CURRENT_STATE

A raw objective exists for building a multi-agent system. The repository
(Lvvphole/Multi-Agent-System) contains only LICENSE and an empty README at
contract adoption time. The raw objective is not executable because it lacks the
25 control mechanisms enumerated in v1.0.0 (deterministic harness layer, state
machine, stage gates, artifact-level evidence, anti-compression guardrails,
restart-safe orchestration, idempotency keys, replayable logs, frozen versions,
schema validation, checkpointing, sub-agent lifecycle governance, role-separated
verification and evaluation, release lock, self-learning governance, skill
versioning/rollback, artifact lineage, failure hooks, concurrency controls,
deterministic retry/failure policy, mechanical stop conditions, external
evidence requirements, and guardrails against useful-but-premature answers).

Prior failure pattern: prompt rules were advisory instead of mechanically
enforced. (Addressed by DETERMINISM_LOCUS.)

---

## DESIRED_STATE

A complete, externally verifiable, multi-step, deterministic-harness-governed
(code-resident) loop system exists. Observable when:

1. Every required stage is represented in a code state machine.
2. Every stage has required artifacts on disk.
3. Every artifact has filename, owner role, stage, checksum, version, and
   verification status recorded in a manifest.
4. Every stage transition is decided by the harness code.
5. Every model output is schema-validated by code before use.
6. Every tool call has an idempotency key.
7. Every step has a checkpoint.
8. Every run has replayable logs.
9. Every skill has version history.
10. Every self-learning update has tests, approval, and rollback.
11. Every release artifact is separately present and verified.
12. Executor cannot grade, approve, release, or complete its own work.
13. Verifier checks artifacts, not explanations.
14. Evaluator (alternate-model judge) scores only against this contract.
15. Final release occurs only after all required gates pass AND required
    human-in-the-loop approvals are recorded.

---

## LOSS_FUNCTION

Minimize | desired_state - current_state | by eliminating: advisory-only rules,
unordered execution, premature output release, artifact compression, missing
artifacts, unverified architecture claims, executor self-certification, verifier
bypass, evaluator bypass, unverifiable completion, missing checkpoints, missing
run history, missing observability/replayability, missing retry/failure policy,
missing failure hooks, missing idempotency keys, duplicate side effects,
duplicate sub-agent spawning, duplicate post-restart LLM calls, missing
concurrency control, missing sub-agent lifecycle control, missing
skill-learning/rollback mechanics, missing memory governance, hallucinated
implementation claims, useful-answer priority overriding control sequence,
trusting model output without validation, release claims without evidence,
token-pressure truncation, placeholder artifacts, stage-boundary leakage,
soft-prompt-only enforcement, non-deterministic decision paths, and missing
artifact lineage.

---

## SYSTEM ARCHITECTURE

Human Owner -> Contract Controller -> Deterministic Harness (code) -> State
Store -> Gate Controller -> Planner -> Executor -> Artifact Manager -> Artifact
Store -> Verifier (code + alternate-LLM judge) -> Evaluator (alternate-LLM
judge) -> Memory Manager -> Escalation Manager -> Orchestrator -> Skill Registry
-> Self-Learning Review Loop -> Human-in-the-Loop Gate -> Release Gate.

## ARCHITECTURAL PRINCIPLE

The model does not run the system. The harness code runs the system. The model
may propose actions, draft artifacts, analyze inputs, and recommend next steps.
The harness decides whether actions are permitted, whether a stage may run,
whether tool calls are allowed, whether an artifact is accepted, whether a state
transition is valid, and whether release is blocked. The model cannot determine
completion. The Executor cannot determine completion. Completion is determined
only by mechanical stop conditions evaluated in code.

---

## HARNESS_DETERMINISM_LAYER

The harness is the mandatory control layer (code) above all agents, tools,
loops, skills, and release actions. It enforces: fixed contract version; fixed
stage order; explicit state-machine transitions; schema-validated inputs and
outputs; idempotency keys for every tool call, artifact write, message send,
sub-agent spawn, and external side effect; replayable run logs; frozen prompt,
skill, contract, model, and tool versions per run; input and artifact checksums;
deterministic retry, failure, escalation policies; deterministic release lock;
verifier-controlled pass/fail; evaluator-controlled correction; gate-controlled
transitions; state-store-controlled continuity; artifact-store-controlled
evidence; memory-controlled persistence; orchestrator-controlled checkpoint
resume; and human-owner approval for irreversible actions.

LLM output is never trusted as deterministic evidence by itself. Only validated
artifacts, logs, schemas, checksums, tests, verifier reports, evaluator reports,
and release-gate reports count as evidence.

## DETERMINISTIC EXECUTION RULES

1. Record contract/prompt/skill/tool versions, input checksum, and model id for
   every run.
2. Any changed version creates a new run lineage.
3. Reject unversioned prompts, skills, tools.
4. Reject artifacts without checksum.
5. Reject state transitions without prior gate evidence.
6. Reject model output failing schema validation.
7. Reject stage output referencing missing artifacts.
8. Reject release claims without required release evidence.
9. Retried steps reuse the same idempotency key unless explicitly a new attempt.
10. Completed checkpointed steps must not re-run after restart.
11. Failed steps retry only per retry policy.
12. Non-recoverable failures trigger escalation.
13. External side effects are locked behind idempotency and approval.

---

## MULTI_STEP_COMPATIBILITY_RULE

Multi-step by default. Each stage is a separate step group; each artifact a
separate work product; each verifier check a separate pass/fail; each evaluator
score a separate correction decision; each release condition a separate gate. No
stage begins until the prior stage has: required artifacts present, manifest
updated, Verifier PASS, Evaluator PASS, gate state PASSED, memory updated, no
unresolved blocker, no unresolved escalation.

---

## STATE STORE

Stages (each: LOCKED | RUNNING | PASSED | FAILED | ESCALATED):

- stage_0_contract_requirements_verification
- stage_1_system_boundary_and_requirements
- stage_2_role_and_agent_model
- stage_3_loop_skill_orchestrator_architecture
- stage_4_state_memory_and_artifact_stores
- stage_5_durable_execution_and_recovery_design
- stage_6_harness_determinism_design
- stage_7_self_learning_loop_design
- stage_8_security_tool_and_human_approval_boundaries
- stage_9_implementation_plan
- stage_10_test_and_verification_design
- stage_11_build_execution
- stage_12_system_verification
- stage_13_evaluation_and_release_gate

Each state record includes: stage id, stage name, current state, prior required
stage, owner role, required artifacts, artifact references, verifier result,
evaluator result, gate decision, timestamp, run id, contract/prompt/skill/tool
versions, model id, input checksum, output checksum, escalation status.

---

## GENERATION_LOCK

Final release / implementation handoff / repository package / deployment package
/ production claim / completion claim is forbidden unless all required stages are
PASSED (stages 11-13 required only if execution is authorized) AND required
human-in-the-loop approvals are recorded. If any required state is not PASSED:
BLOCK release; return failure report; do not compress artifacts; do not
substitute summary for missing artifact; do not claim completion; do not
generate final package; do not mark project complete; do not proceed to next
stage.

LOCKED DELIVERABLES (until lock released): final system package, repository
package, deployment package, production release report, final architecture and
implementation handoffs, final test/verification/evaluation reports, release
package manifest, any user-facing completion claim, any final-readiness bundle.

---

## ARTIFACT_COMPRESSION_GUARDRAIL

Artifact compression is prohibited. Required artifacts remain separate files (or
separately labeled sections with unique artifact IDs). Verification FAILS if:
two+ required artifacts are merged without explicit permission; an artifact is
summarized instead of produced; a placeholder is used; a checklist replaces
required content; a final answer omits required artifacts due to token pressure;
token pressure truncates without escalation; any artifact lacks filename / owner
/ stage / checksum / version / verification status / evaluator status; an
artifact is described but not present; an artifact is replaced by explanation;
the system claims an artifact exists without artifact-store evidence.

Token limits trigger staged continuation or escalation, not compression. Artifact
count cannot be reduced to save tokens if reduction removes required evidence.

---

## SUCCESS_CRITERIA

(Unchanged from v1.0.0 except SC15/SC16 below; see source for full text.)
SC1 Contract requirements verification pass. SC2 Deterministic harness exists.
SC3 Sequential gate state exists. SC4 No stage skipping. SC5 External control
priority. SC6 Artifact compression block. SC7 Multiple artifact requirement. SC8
Durable orchestration design. SC9 Loop-skill-orchestrator separation. SC10
Multi-agent role model. SC11 Self-learning mechanism. SC12 Skill library
governance. SC13 Checkpointed execution. SC14 Observability layer. SC17
Evidence-only completion. SC18 Exhaustive review. SC19 No early release. SC20
Restart safety. SC21 Failure handling. SC22 Concurrency control. SC23 Memory
governance. SC24 Security/tool boundary. SC25 Deterministic retry. SC26
Deterministic failure. SC27 Replayable run log. SC28 Idempotency coverage. SC29
Schema validation coverage. SC30 Frozen version coverage. SC31 Human approval
coverage. SC32 Test suite exists. SC33 Final release package exists.

SC15 Verifier Independence (UPDATED — A3): The Executor cannot verify, grade,
approve, release, or mark completion for its own work. The Verifier consists of
(a) code-level structural checks and (b) an alternate-model LLM judge that must
be a different model instance/role than the Executor that produced the artifact.
Evidence: role_permission_matrix.md, verification_report.md, judge_session_log.jsonl.
Pass: Executor has no verification/evaluation/gate/completion permission, and
every semantic green light carries an alternate-judge session id.

SC16 Evaluator Independence (UPDATED — A3): The Evaluator is an alternate-model
LLM judge scoring only against this contract; it cannot accept Executor
explanations as evidence and cannot share identity with the Executor. Major
changes flagged by security review or deletion protocols require a recorded
human-in-the-loop approval before the Evaluator green light is honored. Evidence:
evaluation_protocol.md, evaluation_report.md, human_approval_log.jsonl.

SC11 Self-learning mechanism (UPDATED — A4): The recurring review loop reads run
history, scores skills on a continuous stability metric, and proposes changes
that cannot activate without (i) a held-out/out-of-sample validation gate, (ii)
an attempt-count-aware acceptance bar, (iii) a decay/half-life check, plus tests,
verification, evaluation, versioning, and a rollback path. Evidence:
self_learning_loop_spec.md, skill_holdout_validation_report.md,
skill_attempt_ledger.jsonl, skill_decay_report.md, skill_version_log.jsonl.
Pass: no skill version activates that was validated only in-sample, or that
fails the rising acceptance bar or the half-life floor.

---

## SELF_LEARNING_VALIDATION  (NEW — A4)

Applies to the Self-Learning Reviewer and Skill Manager. Before ANY proposed
skill version becomes active:

1. Held-out (out-of-sample) gate. The skill change is validated on runs/tasks
   that were NOT used to propose or tune it. In-sample improvement is necessary
   but not sufficient. The held-out split is recorded; reusing tuning data as
   validation data is a violation.
2. Continuous performance metric. Skill effectiveness is scored per run and
   summarized as a stability metric (mean over std of the per-run score), not a
   binary PASS/FAIL, so the loop has a gradient to optimize. Binary gates remain
   for activation; the continuous metric drives ranking and selection.
3. Attempt-count-aware acceptance bar. The acceptance threshold rises with the
   number of variants tried for a given skill (multiple-comparisons discipline).
   Every attempt is recorded in skill_attempt_ledger.jsonl; the required held-out
   metric to activate increases monotonically with attempt count.
4. Decay / half-life check. The persistence of the skill's effectiveness is
   estimated (e.g. AR(1) half-life). Skills below a configured half-life floor
   are rejected or auto-deprecated; durable edges are preferred over signals that
   work once and break.
5. Standard gates still apply. The change additionally requires tests,
   alternate-model Verifier GREEN, Evaluator GREEN, a version assignment, and a
   rollback path. Skill deprecation/removal remains a DESTRUCTIVE change subject
   to HUMAN_IN_THE_LOOP.

Anti-pattern blocked: optimizing skills against the same run history used to
measure them ("faster iteration on the same history just overfits faster").

---

## CONSTRAINTS

1. Prioritize external control sequence over usefulness.
2. The deterministic harness (code) controls execution.
3. Model must not control state transitions.
4. Model must not control completion.
5. Model must not bypass schema validation.
6. No early artifact release.
7. No required-artifact compression.
8. No replacing missing evidence with explanation.
9. Executor cannot determine completion.
10. Executor cannot verify its own work.
11. Evaluator cannot rely on Executor explanations.
12. Useful output cannot override gate order.
13. "done/useful/looks complete/ready/strong/robust/high quality/good/optimized"
    are forbidden as pass criteria.
14. Each success criterion maps to concrete evidence.
15. Every artifact has filename, stage, owner role, checksum, version, verify
    status.
16. Required artifacts stay separate unless explicitly permitted to combine.
17. Self-learning changes are versioned, tested, verified, evaluated, rollback-
    capable.
18. Durable execution includes checkpointing, retry state, run history,
    idempotency, failure state.
19. Sub-agents have explicit parent-child lifecycle rules.
20. Tool use optimizes artifact fidelity, not speed/convenience.
21. Default autonomy is per AUTONOMY_LEVEL below.
22. (UPDATED — A2) File creation within the project workspace and the build loop
    are AUTHORIZED under this contract version. Execution of EXTERNAL,
    IRREVERSIBLE, or DESTRUCTIVE actions (deployment, repository push to remote,
    external messaging, billing, secret access, hard deletion) still requires
    explicit human approval per HUMAN_IN_THE_LOOP.
23. Token pressure triggers continuation or escalation, not compression.
24. Missing evidence triggers escalation, not hallucination.
25. Missing requirements trigger escalation, not guessing.
26. Non-deterministic LLM output must be validated before it can affect state.
27. External side effects require idempotency.
28. Irreversible external side effects require human approval.
29. Version changes create new run lineage.
30. Replay logs survive process restart.
31. (NEW — A3) The judge model for any artifact must differ from the model
    instance/role that produced it; same-instance self-judging is forbidden.

---

## VERIFIER  (UPDATED — A3)

Two layers, both required for a PASS:

1. Structural Verifier (code): checks artifact existence, filename, owner,
   stage, checksum, version, schema validity, manifest entry, and the literal
   verifier-checks for the stage. Deterministic; runs without a model.

2. Semantic Judge (alternate-model LLM-as-judge): a model instance that is NOT
   the Executor reviews the artifact content against contract criteria and
   issues GREEN / RED with written justification, recorded with a judge session
   id in judge_session_log.jsonl. The judge reviews artifacts, never Executor
   explanations or intentions.

A stage Verifier PASS requires structural PASS AND judge GREEN. The judge cannot
overturn a structural FAIL. Confidence/usefulness/intent are never evidence.

## EVALUATOR  (UPDATED — A3)

An alternate-model LLM judge (distinct from Executor and, where feasible, from
the Verifier judge) scores verifier-approved artifacts strictly against this
contract's success criteria. It requests correction or escalation when evidence
fails. It does not execute or produce deliverables. For any change classified
MAJOR by security review or deletion protocols, the Evaluator green light is not
honored until a human approval record exists.

## HUMAN_IN_THE_LOOP  (NEW — A3)

Mandatory human handoff (recorded in human_approval_log.jsonl) before proceeding,
for:

- Security-review MAJOR findings: privilege escalation, secret/credential
  exposure, sandbox-boundary change, new external network egress, tool-permission
  widening, auth/permission model changes.
- Deletion protocol triggers: hard delete of artifacts/data, history rewrite,
  state-store truncation, skill deprecation/removal, rollback that discards run
  lineage, release retraction.
- Any irreversible external side effect (deployment, remote push, external
  messaging, billing).

Each record: timestamp, actor, change class (MINOR|MAJOR|DESTRUCTIVE), summary,
linked artifacts/checksums, decision (APPROVE|REJECT|DEFER), and rationale. No
MAJOR/DESTRUCTIVE action executes without an APPROVE record bound to the exact
checksums under review.

---

## EVIDENCE_REQUIRED

(All 71 artifacts from v1.0.0 are retained. Additions for A3:)
72. judge_session_log.jsonl
73. human_approval_log.jsonl
74. security_review_report.md
75. deletion_protocol_policy.md
76. skill_holdout_validation_report.md   (A4)
77. skill_attempt_ledger.jsonl           (A4)
78. skill_decay_report.md                (A4)
(See source list for items 1-71; unchanged.)

---

## BUDGET

token_cap: 120000 per full execution cycle. max_iterations: 500 (executable
loop), 1 (contract generation). max_escalations: 25. Architecture/contract work
proceeds without implementation budget; implementation requires separate
approval for repo/runtime/db/orchestration/model-provider/deploy/observability/
security/external-APIs/hosting/storage/queue/monitoring/human-review costs.
Implementation budget defined before Stage 11. No external/destructive action
unless authorized and stage permits. Artifact count cannot drop to save tokens
if it removes evidence; token limits cause continuation/escalation not
compression; cost reduction cannot remove checkpoints/idempotency/replay/schema/
version-freeze.

---

## AUTONOMY_LEVEL  (UPDATED — A2)

3 (within workspace) / 2 (external).

- Workspace scope: AUTHORIZED to create, edit, and organize files inside the
  project workspace and to run the build/test loop and produce all in-scope
  artifacts without per-step approval.
- External scope: capped at 2. External, irreversible, or destructive actions
  (deployment, remote repo push, external messaging, billing, secret access,
  hard deletion) require explicit human approval per HUMAN_IN_THE_LOOP.

AUTONOMY_SCALE: 0 none / 1 draft / 2 recommend+structure / 3 execute reversible
local actions / 4 bounded actions with explicit limits / 5 full autonomous.

---

## STOP_CONDITIONS

Stop only when (1) all success criteria pass, all evidence exists, all artifacts
separately present, Verifier approves, Evaluator approves, required human
approvals recorded, Release Gate passes, no escalation remains, iteration limit
not exceeded; OR (2) required info missing; OR (3) required evidence cannot be
produced; OR (4) a hard gate blocks; OR (5) same failure repeats 3x; OR (6)
iteration limit reached; OR (7) harness detects a state-machine violation; OR (8)
artifact compression attempted; OR (9) executor self-certification attempted; OR
(10) release requested before gates pass; OR (11) a MAJOR/DESTRUCTIVE action
lacks a human approval record.

## ESCALATION_CONDITIONS

(All v1.0.0 escalation triggers retained.) Plus: missing alternate-judge session
for a green light; same-instance self-judging detected; MAJOR/DESTRUCTIVE change
without human approval; security-review MAJOR finding; deletion-protocol trigger.

---

## LOOP

TRIGGER (UPDATED — A2): The build loop is AUTHORIZED to run under this contract
version for workspace-scoped actions (audit, design, build, test, produce
artifacts). External/irreversible/destructive actions remain gated by
HUMAN_IN_THE_LOOP. MAX_ITERATIONS: 500 (executable), 1 (contract gen).

DECISION_LOGIC, CONTINUE_RULE, COMPLETE_RULE, ESCALATE_RULE, STAGE_GATES (0-13),
HALLUCINATION_PATHWAY_BLOCKERS, MEMORY, ROLES, CLARIFY, CONFIG, FOOTER: retained
from v1.0.0 with the role updates to VERIFIER/EVALUATOR above and the new
HUMAN_IN_THE_LOOP gate inserted immediately before the Release Gate in every
stage that produces a MAJOR/DESTRUCTIVE change.

COMPLETION_AUTHORITY: Completion is determined only by mechanical stop conditions
evaluated in code. No agent (Executor, Verifier, Evaluator, Planner) or model may
unilaterally declare completion.

---

FOOTER: Confidence 0.94 | Determinism: code-resident | Compression: BLOCKED

---

## MEMORY

FILE: project_memory.md

COMPLETED_LAST_RUN: store only completed+verified items with artifact refs,
checksums, versions, gate status, verifier status, evaluator status, harness
validation status, release status.

IN_PROGRESS: current stage, milestone, owner role, active artifact, unresolved
checks, next required gate, run id, input checksum, prompt version, skill version.

BLOCKERS: missing inputs, failed validations, unverifiable assumptions,
unavailable evidence, tool failures, compression attempts, invalid transitions,
missing idempotency keys/schemas/checksums/run-logs/version-snapshots,
unresolved escalations.

NEXT_ACTIONS: next mechanical action only (stage, role, artifact, verifier
check, evaluator check, harness validation, escalation).

KNOWN_FAILURE_PATTERNS: invalid assumptions, duplicate side effects, failed
restart recovery, missing/compressed/placeholder artifacts, unauthorized
self-certification, stage skipping, failed verification/evaluation, schema
failures, missing idempotency keys/replay logs, version drift, tool-permission
violations, release-lock violations, memory update failures.

MEMORY_RULES: memory stays concise; memory persists while agents forget; never
store unverified completion claims; never mark complete unless Verifier and
Evaluator pass; never overwrite failure patterns without resolution evidence;
preserve blockers until resolved; preserve artifact lineage and release decisions.

---

## ROLES

HUMAN_OWNER: approves autonomy changes, irreversible/external/destructive
actions, deployment, production release, budget changes, and all MAJOR/
DESTRUCTIVE changes per HUMAN_IN_THE_LOOP.

CONTRACT_CONTROLLER: verifies contract structure, completeness, version, required
fields, success-criteria/evidence mappings, and stop rules.

DETERMINISTIC_HARNESS: code that controls execution permission, state-machine
transitions, schema validation, idempotency, version freezing, replay logging,
retry/failure policy, and release lock. Does not create project artifacts, does
not grade quality, does not replace Verifier or Evaluator.

PLANNER: determines sequence, dependencies, milestones, required artifacts, next
mechanical action. Does not execute/verify/evaluate/complete.

EXECUTOR: produces only artifacts authorized by the current RUNNING stage. Cannot
verify, evaluate, approve, release, compress, skip stages, or determine
completion. Cannot judge its own artifacts (A3: judge model must differ).

VERIFIER: code structural checks + alternate-model judge (see VERIFIER section).
Checks artifacts, never explanations/intent/usefulness/confidence/Executor claims.

EVALUATOR: alternate-model judge scoring verifier-approved artifacts against this
contract only (see EVALUATOR section). Honors green light for MAJOR/DESTRUCTIVE
changes only after a recorded human approval.

MEMORY_MANAGER: updates project_memory.md, state records, failure patterns,
blockers, completed verified items, next actions. Cannot mark completion unless
stop conditions are satisfied.

ESCALATION_MANAGER: handles missing inputs, unavailable evidence, unverifiable
assumptions, tool limits, repeated failure, gate conflicts, security blockers,
harness violations, iteration-limit failures.

GATE_CONTROLLER: controls stage transitions; marks PASSED only when required
artifacts exist, Verifier PASS, Evaluator PASS, harness validation passes, and no
unresolved escalation.

ARTIFACT_MANAGER: maintains manifest, artifact ids, checksums, owner roles,
version history, lineage, compression audits.

ORCHESTRATOR: runs triggers, schedules loops, persists checkpoints, manages
retries/failures, records run history, enforces concurrency, resumes from last
successful step, preserves sub-agent lifecycle state.

SKILL_MANAGER: registers, versions, tests, deprecates, rolls back, reuses skills.
Cannot activate modified skills without verification and evaluation.

SELF_LEARNING_REVIEWER: reads run history, evaluates skill performance, identifies
failed patterns, proposes modifications, submits for test/verification. Cannot
directly release updated skills.

SECURITY_MANAGER: controls secret access, tool permissions, sandbox boundaries,
approval gates, audit logs; raises security-review MAJOR findings to HUMAN_OWNER.

COMPLETION_AUTHORITY: completion is determined only by mechanical stop conditions
evaluated in code. No agent or model may unilaterally declare completion.

---

## CLARIFY

Emit CLARIFY only if the contract cannot be defined without missing information.
Ask no more than 3 questions. CLARIFY counts as an escalation.

Q1: N/A
Q2: N/A
Q3: N/A

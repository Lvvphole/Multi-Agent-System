# memory_architecture.md

artifact_id: stage4.memory_architecture
stage: stage_4
owner: Executor
version: 2.1.0

Defines the persistent memory model: six separated categories, each with an
owner, retention rule, and update rule (SC23). Memory persists across runs and
restarts; agents are stateless between calls (MEMORY_RULES: "memory persists,
agents forget"). Storage is per DR-003 (JSON/SQLite local, Postgres production);
record shapes are the Stage 4 schemas.

## Memory categories (separated)

- Working memory: transient per-run scratch. owner=Orchestrator. retention=run
  lifetime only. update=free within a run; discarded after run completion.
- Project memory (project_memory.md): the durable cross-run summary. owner=Memory
  Manager. retention=permanent. update=only after a gate decision; never stores
  unverified completion claims.
- Skill memory (skill registry + skill_version_log): skills and their versions.
  owner=Skill Manager. retention=permanent with version history. update=only via
  SELF_LEARNING_VALIDATION (A4) + Verifier/Evaluator GREEN.
- Run history (run_history_schema): every step of every run. owner=Orchestrator.
  retention=permanent (replay evidence). update=append-only.
- Artifact store (artifact_manifest_schema): artifacts + checksums + lineage.
  owner=Artifact Manager. retention=permanent. update=register on creation;
  status fields updated by Verifier/Evaluator only.
- Evaluation memory (verification/evaluation reports + judge_session_log):
  verifier/evaluator results. owner=Evaluator/Verifier. retention=permanent.
  update=append-only per stage.

## project_memory.md required sections (separated)

- ## COMPLETED_VERIFIED — only items with Verifier PASS + Evaluator PASS + gate
  PASSED, with artifact refs/checksums.
- ## IN_PROGRESS — current stage, milestone, owner, active artifact, unresolved
  checks, next gate, run id.
- ## BLOCKERS — missing inputs, failed validations, unverifiable assumptions,
  unavailable evidence; preserved until resolved.
- ## NEXT_ACTIONS — the next mechanical action only.
- ## KNOWN_FAILURE_PATTERNS — recurring failures; not overwritten without
  resolution evidence.

## Invariants

- No memory category has an undefined owner, retention rule, or update rule.
- Completed-verified is the only category that may assert completion, and only
  when stop conditions hold.
- Run history and artifact store are append-only; corrections add records, never
  rewrite (history rewrite is DESTRUCTIVE -> HUMAN_IN_THE_LOOP).
- A process restart reconstructs all categories from disk/DB; nothing critical
  lives only in model context.

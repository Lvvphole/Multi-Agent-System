"""harness.py — The deterministic control layer (code).

run_stage() is the single funnel through which a stage advances. The Executor
(model) can only propose artifacts; the harness decides legality, runs the
structural verifier, requires an alternate-model judge GREEN for both verify and
evaluate, enforces the human gate for MAJOR/DESTRUCTIVE changes, and only then
asks the state machine to mark PASSED. Every decision is logged for replay.
"""
from __future__ import annotations
import os
from .state_store import StateStore, State
from .state_machine import StateMachine, TransitionError
from .artifact_store import ArtifactStore
from .replay_log import ReplayLog
from .idempotency import IdempotencyLedger, make_key
from .judge import (StructuralVerifier, AlternateModelJudge, HumanGate,
                    classify_change, Verdict, ChangeClass, SelfJudgingError)


class StageResult:
    def __init__(self, stage_id, state, detail):
        self.stage_id, self.state, self.detail = stage_id, state, detail

    def __repr__(self):
        return f"<StageResult {self.stage_id} {self.state}: {self.detail}>"


class Harness:
    def __init__(self, root: str, run_ctx: dict,
                 verify_judge: AlternateModelJudge,
                 eval_judge: AlternateModelJudge,
                 executor_model_id: str):
        self.root = root
        self.run_ctx = run_ctx
        self.executor_model_id = executor_model_id
        self.store = StateStore(os.path.join(root, "state_store.json"))
        self.sm = StateMachine(self.store)
        self.artifacts = ArtifactStore(
            os.path.join(root, "artifact_manifest.json"),
            os.path.join(root, "artifacts"))
        self.log = ReplayLog(os.path.join(root, "gate_state_log.jsonl"))
        self.ledger = IdempotencyLedger(os.path.join(root, "idempotency.json"))
        self.struct = StructuralVerifier()
        self.verify_judge = verify_judge
        self.eval_judge = eval_judge
        self.human = HumanGate(os.path.join(root, "human_approval_log.jsonl"))
        self.judge_log = ReplayLog(os.path.join(root, "judge_session_log.jsonl"))

    def guard_contract_version(self):
        """Contract change -> new run lineage; Stage 0 must re-verify.

        Implements the contract rule 'version changes create new run lineage'
        for the contract-verification stage specifically. Stage 0 verifies the
        contract, so a changed contract checksum invalidates its prior PASS.
        Logged as a lineage event (not a normal gameplay transition).
        """
        rec = self.store.get("stage_0")
        cur = self.run_ctx["contract_checksum"]
        if rec.state == State.PASSED.value and rec.contract_version not in (None, cur):
            self.store.update("stage_0", state=State.LOCKED.value,
                              verifier_result=None, evaluator_result=None,
                              gate_decision=None)
            self.log.append("new_lineage_reset", stage="stage_0",
                            reason="contract amended",
                            old=rec.contract_version, new=cur)
            return True
        return False

    def run_stage(self, stage_id: str, *, owner: str, version: str,
                  required_artifacts: list[str], executor_fn,
                  criteria: str, change_summary: str = "",
                  extra_checks=None) -> StageResult:
        rid = self.run_ctx["run_id"]
        self.log.append("stage_attempt", stage=stage_id, run_id=rid)

        # 1. legality (code, not model)
        ok, why = self.sm.can_start(stage_id)
        if not ok:
            self.log.append("stage_blocked", stage=stage_id, reason=why)
            return StageResult(stage_id, "BLOCKED", why)
        self.sm.transition(stage_id, State.RUNNING, run_id=rid,
                           contract_version=self.run_ctx["contract_checksum"])

        # 2. executor proposes artifacts (idempotent)
        for name in required_artifacts:
            key = make_key("artifact_write", rid, stage_id, name)
            if self.ledger.seen(key):
                self.log.append("idempotent_skip", stage=stage_id, artifact=name)
                continue
            executor_fn(name)  # writes file into artifacts/
            self.artifacts.register(name, owner, stage_id, version)
            self.ledger.record(key, name)

        # 3. structural verification (code)
        sv = self.struct.verify(required_artifacts, self.artifacts.artifact_dir,
                                self.artifacts.manifest, extra_checks)
        self.log.append("structural_verify", stage=stage_id, **sv)
        if sv["result"] != "PASS":
            self.sm.transition(stage_id, State.FAILED, verifier_result="FAIL")
            return StageResult(stage_id, "FAILED", sv["failures"])
        for name in required_artifacts:
            self.artifacts.set_status(name, verification="PASS_STRUCT")

        checksums = self.artifacts.checksums(required_artifacts)
        def _read(n):
            with open(os.path.join(self.artifacts.artifact_dir, n)) as fh:
                return fh.read()
        artifact_text = "\n\n".join(_read(n) for n in required_artifacts)

        # 4. alternate-model judge: verification green light
        try:
            vr = self.verify_judge.review(self.executor_model_id,
                                          artifact_text, criteria, checksums)
        except SelfJudgingError as e:
            self.sm.transition(stage_id, State.ESCALATED,
                               escalation_status=str(e))
            return StageResult(stage_id, "ESCALATED", str(e))
        self.judge_log.append("verify_judge", stage=stage_id,
                              session=vr.session_id, model=vr.judge_model_id,
                              verdict=vr.verdict, why=vr.justification)
        if vr.verdict != Verdict.GREEN.value:
            self.store.update(stage_id, verifier_result="FAIL")
            self.sm.transition(stage_id, State.FAILED, verifier_result="FAIL")
            return StageResult(stage_id, "FAILED", f"verify judge RED: {vr.justification}")
        self.store.update(stage_id, verifier_result="PASS")

        # 5. human gate for MAJOR/DESTRUCTIVE
        cc = classify_change(change_summary)
        if self.human.requires_human(cc) and not self.human.is_approved(checksums):
            self.sm.transition(stage_id, State.ESCALATED,
                               escalation_status=f"human approval required ({cc.value})")
            self.log.append("human_gate_block", stage=stage_id, change_class=cc.value)
            return StageResult(stage_id, "ESCALATED",
                               f"human approval required for {cc.value} change")

        # 6. alternate-model judge: evaluation green light
        er = self.eval_judge.review(self.executor_model_id, artifact_text,
                                    criteria, checksums)
        self.judge_log.append("eval_judge", stage=stage_id, session=er.session_id,
                              model=er.judge_model_id, verdict=er.verdict,
                              why=er.justification)
        if er.verdict != Verdict.GREEN.value:
            self.sm.transition(stage_id, State.FAILED, evaluator_result="FAIL")
            return StageResult(stage_id, "FAILED", f"eval judge RED: {er.justification}")
        for name in required_artifacts:
            self.artifacts.set_status(name, evaluator="PASS")
        self.store.update(stage_id, evaluator_result="PASS")

        # 7. gate -> PASSED (state machine re-checks evidence)
        self.sm.transition(stage_id, State.PASSED, gate_decision="PASSED",
                           human_approval=("APPROVE" if self.human.requires_human(cc) else "N/A"))
        self.log.append("stage_passed", stage=stage_id,
                        artifacts=required_artifacts, checksums=checksums)
        return StageResult(stage_id, "PASSED", required_artifacts)

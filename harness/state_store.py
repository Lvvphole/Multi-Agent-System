"""state_store.py — Persistent stage state.

Determinism locus: stage state lives on disk, not in a model's context.
After a process restart the store reports exact current state from disk.
"""
from __future__ import annotations
import json, os, tempfile
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional


class State(str, Enum):
    LOCKED = "LOCKED"
    RUNNING = "RUNNING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    ESCALATED = "ESCALATED"


STAGES = [
    ("stage_0", "contract_requirements_verification", None),
    ("stage_1", "system_boundary_and_requirements", "stage_0"),
    ("stage_2", "role_and_agent_model", "stage_1"),
    ("stage_3", "loop_skill_orchestrator_architecture", "stage_2"),
    ("stage_4", "state_memory_and_artifact_stores", "stage_3"),
    ("stage_5", "durable_execution_and_recovery_design", "stage_4"),
    ("stage_6", "harness_determinism_design", "stage_5"),
    ("stage_7", "self_learning_loop_design", "stage_6"),
    ("stage_8", "security_tool_and_human_approval_boundaries", "stage_7"),
    ("stage_9", "implementation_plan", "stage_8"),
    ("stage_10", "test_and_verification_design", "stage_9"),
    ("stage_11", "build_execution", "stage_10"),
    ("stage_12", "system_verification", "stage_11"),
    ("stage_13", "evaluation_and_release_gate", "stage_12"),
]


@dataclass
class StageRecord:
    stage_id: str
    stage_name: str
    prior_required: Optional[str]
    state: str = State.LOCKED.value
    owner_role: str = ""
    required_artifacts: list = field(default_factory=list)
    artifact_refs: list = field(default_factory=list)
    verifier_result: Optional[str] = None      # PASS | FAIL | None
    evaluator_result: Optional[str] = None
    gate_decision: Optional[str] = None
    human_approval: Optional[str] = None        # APPROVE | REJECT | DEFER | None
    timestamp: Optional[str] = None
    run_id: Optional[str] = None
    contract_version: Optional[str] = None
    output_checksum: Optional[str] = None
    escalation_status: Optional[str] = None


class StateStore:
    def __init__(self, path: str):
        self.path = path
        if os.path.exists(path):
            with open(path) as f:
                raw = json.load(f)
            self._records = {k: StageRecord(**v) for k, v in raw.items()}
        else:
            self._records = {
                f"{sid}_{name}": StageRecord(stage_id=sid, stage_name=name,
                                             prior_required=prior)
                for sid, name, prior in STAGES
            }
            self._flush()

    def key(self, stage_id: str) -> str:
        for sid, name, _ in STAGES:
            if sid == stage_id:
                return f"{sid}_{name}"
        raise KeyError(stage_id)

    def get(self, stage_id: str) -> StageRecord:
        return self._records[self.key(stage_id)]

    def all(self) -> dict:
        return dict(self._records)

    def update(self, stage_id: str, **changes) -> StageRecord:
        rec = self._records[self.key(stage_id)]
        for k, v in changes.items():
            setattr(rec, k, v)
        self._flush()
        return rec

    def _flush(self):
        # atomic write so a crash mid-write cannot corrupt state
        d = {k: asdict(v) for k, v in self._records.items()}
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(self.path) or ".")
        with os.fdopen(fd, "w") as f:
            json.dump(d, f, indent=2)
        os.replace(tmp, self.path)

"""judge.py — Verification/Evaluation judge layer (A3).

Layer 1: StructuralVerifier — deterministic code checks (existence, checksum,
         schema, manifest, literal stage verifier-checks). Runs with no model.
Layer 2: alternate-model LLM-as-judge — a model instance that is NOT the
         Executor issues GREEN/RED with justification + session id.
Gate:    HumanGate — MAJOR/DESTRUCTIVE changes require a recorded human approval
         bound to the exact checksums under review.

The harness enforces judge_model_id != executor_model_id. Same-instance
self-judging is rejected before any verdict is honored.
"""
from __future__ import annotations
import os, time, uuid
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional


class Verdict(str, Enum):
    GREEN = "GREEN"
    RED = "RED"


class ChangeClass(str, Enum):
    MINOR = "MINOR"
    MAJOR = "MAJOR"
    DESTRUCTIVE = "DESTRUCTIVE"


@dataclass
class JudgeResult:
    verdict: str
    justification: str
    session_id: str
    judge_model_id: str
    artifact_checksums: list


class SelfJudgingError(Exception):
    pass


class StructuralVerifier:
    """Deterministic, code-only artifact checks for a stage."""

    def verify(self, required_artifacts: list[str], artifact_dir: str,
               manifest: dict, extra_checks: Optional[Callable] = None) -> dict:
        failures = []
        for name in required_artifacts:
            path = os.path.join(artifact_dir, name)
            if not os.path.exists(path):
                failures.append(f"missing artifact: {name}")
                continue
            if os.path.getsize(path) == 0:
                failures.append(f"empty/placeholder artifact: {name}")
            entry = manifest.get(name)
            if not entry:
                failures.append(f"no manifest entry: {name}")
            else:
                for field in ("checksum", "owner", "stage", "version"):
                    if not entry.get(field):
                        failures.append(f"{name}: manifest missing {field}")
        if extra_checks:
            failures.extend(extra_checks() or [])
        return {"result": "PASS" if not failures else "FAIL",
                "failures": failures}


class AlternateModelJudge:
    """Wraps a callable that talks to a DIFFERENT model than the Executor.

    review_fn(artifact_text, criteria) -> (Verdict, justification:str)
    In production, wire review_fn to a separate model API instance/role.
    """

    def __init__(self, judge_model_id: str, review_fn: Callable):
        self.judge_model_id = judge_model_id
        self.review_fn = review_fn

    def review(self, executor_model_id: str, artifact_text: str,
               criteria: str, artifact_checksums: list) -> JudgeResult:
        if self.judge_model_id == executor_model_id:
            raise SelfJudgingError(
                "judge model == executor model; alternate judge required (A3)")
        verdict, justification = self.review_fn(artifact_text, criteria)
        return JudgeResult(
            verdict=Verdict(verdict).value,
            justification=justification,
            session_id=str(uuid.uuid4())[:12],
            judge_model_id=self.judge_model_id,
            artifact_checksums=list(artifact_checksums),
        )


def classify_change(summary: str) -> ChangeClass:
    s = summary.lower()
    destructive = ("hard delete", "truncate", "history rewrite", "drop ",
                   "rollback discards", "release retraction", "purge")
    major = ("secret", "credential", "privilege", "sandbox", "egress",
             "tool-permission", "auth", "permission model", "deploy",
             "remote push", "external messaging", "billing")
    if any(k in s for k in destructive):
        return ChangeClass.DESTRUCTIVE
    if any(k in s for k in major):
        return ChangeClass.MAJOR
    return ChangeClass.MINOR


class HumanGate:
    """Records and enforces human-in-the-loop approval for MAJOR/DESTRUCTIVE."""

    def __init__(self, approval_log_path: str):
        self.path = approval_log_path
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)

    def requires_human(self, change_class: ChangeClass) -> bool:
        return change_class in (ChangeClass.MAJOR, ChangeClass.DESTRUCTIVE)

    def record(self, actor: str, change_class: ChangeClass, summary: str,
               checksums: list, decision: str, rationale: str) -> dict:
        import json
        rec = {"ts": time.time(), "actor": actor,
               "change_class": change_class.value, "summary": summary,
               "checksums": checksums, "decision": decision,
               "rationale": rationale}
        with open(self.path, "a") as f:
            f.write(json.dumps(rec) + "\n")
        return rec

    def is_approved(self, checksums: list) -> bool:
        import json
        if not os.path.exists(self.path):
            return False
        cset = set(checksums)
        with open(self.path) as fh:
            for line in fh:
                if not line.strip():
                    continue
                r = json.loads(line)
                if r.get("decision") == "APPROVE" and cset.issubset(set(r.get("checksums", []))):
                    return True
        return False

"""stage0.py — Contract Requirements Verification, performed by code.

Parses CONTRACT.md and runs the Stage-0 verifier checks. Produces the two
required artifacts. This is the concrete embodiment of DETERMINISM_LOCUS:
the checklist's PASS/FAIL is computed from the contract bytes, not asserted.
"""
from __future__ import annotations
import csv, io, re

REQUIRED_SECTIONS = [
    "OBJECTIVE", "CURRENT_STATE", "DESIRED_STATE", "LOSS_FUNCTION",
    "SUCCESS_CRITERIA", "CONSTRAINTS", "EVIDENCE_REQUIRED", "BUDGET",
    "AUTONOMY_LEVEL", "STOP_CONDITIONS", "ESCALATION_CONDITIONS", "LOOP",
    "MEMORY", "ROLES", "CLARIFY",
]

SUBJECTIVE_TERMS = ["looks complete", "high quality", "robust", "strong",
                    "good enough", "optimized", "feels done"]


def _has_section(text: str, name: str) -> bool:
    return re.search(rf"(?m)^#{{1,3}}\s*{re.escape(name)}\b", text) is not None \
        or re.search(rf"(?m)^{re.escape(name)}\b", text) is not None


def run_checks(contract_text: str) -> list[dict]:
    t = contract_text
    checks = []

    def add(cid, desc, passed, note=""):
        checks.append({"check_id": cid, "description": desc,
                       "result": "PASS" if passed else "FAIL", "note": note})

    missing = [s for s in REQUIRED_SECTIONS if not _has_section(t, s)]
    add("C0.1", "Every required contract section exists",
        not missing, f"missing: {missing}" if missing else "all present")

    add("C0.2", "Success criteria map to evidence",
        "Evidence:" in t and "EVIDENCE_REQUIRED" in t,
        "SC blocks reference Evidence and EVIDENCE_REQUIRED present")

    # subjective pass language must not be used AS a completion condition;
    # it may be quoted only as a forbidden term.
    bad = [w for w in SUBJECTIVE_TERMS
           if re.search(rf"pass.*{re.escape(w)}|{re.escape(w)}.*=\s*pass",
                        t, re.I)]
    add("C0.3", "No subjective pass language used as completion condition",
        not bad, f"flagged: {bad}" if bad else "forbidden-terms only quoted")

    add("C0.4", "Artifact compression explicitly prohibited",
        "ARTIFACT_COMPRESSION_GUARDRAIL" in t and "compression is prohibited" in t.lower(),
        "guardrail section present")

    add("C0.5", "Executor cannot self-certify",
        "Executor cannot determine completion" in t or
        "cannot self-certify" in t.lower() or
        "Executor cannot verify" in t,
        "self-certification blocked in CONSTRAINTS/ROLES")

    add("C0.6", "Stop conditions are mechanical",
        "STOP_CONDITIONS" in t and "mechanical stop conditions" in t.lower(),
        "mechanical stop conditions defined")

    add("C0.7", "Deterministic harness layer exists (in code, not prose)",
        "HARNESS_DETERMINISM_LAYER" in t and "DETERMINISM_LOCUS" in t,
        "harness layer + determinism-locus principle present")

    add("C0.8", "Multi-step stage gates exist",
        all(f"stage_{i}" in t for i in range(0, 14)),
        "stages 0-13 declared")

    add("C0.9", "Generation lock exists",
        "GENERATION_LOCK" in t, "generation lock present")

    add("C0.10", "Release lock exists",
        "Release Gate" in t or "release_gate" in t.lower() or "release lock" in t.lower(),
        "release lock/gate present")

    # A3 additions
    add("C0.11", "Verifier/Evaluator use alternate-model judge (A3)",
        "alternate-model" in t.lower() and "judge" in t.lower(),
        "alternate-model judge mandated")

    add("C0.12", "Human-in-the-loop gate for major/deletion changes (A3)",
        "HUMAN_IN_THE_LOOP" in t and "deletion" in t.lower(),
        "human gate + deletion protocol present")

    add("C0.13", "Self-learning held-out gate + attempt bar + decay (A4)",
        "SELF_LEARNING_VALIDATION" in t and "out-of-sample" in t.lower()
        and "half-life" in t.lower() and "attempt-count-aware" in t.lower(),
        "held-out gate, rising bar, and decay check mandated")

    return checks


def write_checklist(checks: list[dict]) -> str:
    all_pass = all(c["result"] == "PASS" for c in checks)
    lines = ["# contract_requirements_checklist.md", "",
             f"contract_stage: stage_0_contract_requirements_verification",
             f"overall: {'ALL CHECKS PASS' if all_pass else 'CHECKS FAILED'}", ""]
    for c in checks:
        lines.append(f"- [{ 'x' if c['result']=='PASS' else ' ' }] "
                     f"{c['check_id']} {c['description']} — {c['result']} "
                     f"({c['note']})")
    lines.append("")
    return "\n".join(lines)


def write_traceability(checks: list[dict]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["check_id", "contract_field", "evidence_artifact", "result", "note"])
    field_map = {
        "C0.1": "all sections", "C0.2": "SUCCESS_CRITERIA/EVIDENCE_REQUIRED",
        "C0.3": "CONSTRAINTS.13", "C0.4": "ARTIFACT_COMPRESSION_GUARDRAIL",
        "C0.5": "ROLES.EXECUTOR/COMPLETION_AUTHORITY", "C0.6": "STOP_CONDITIONS",
        "C0.7": "HARNESS_DETERMINISM_LAYER/DETERMINISM_LOCUS",
        "C0.8": "STATE STORE/STAGE_GATES", "C0.9": "GENERATION_LOCK",
        "C0.10": "Release Gate", "C0.11": "VERIFIER/EVALUATOR (A3)",
        "C0.12": "HUMAN_IN_THE_LOOP (A3)",
        "C0.13": "SELF_LEARNING_VALIDATION (A4)",
    }
    for c in checks:
        w.writerow([c["check_id"], field_map.get(c["check_id"], ""),
                    "contract_requirements_checklist.md", c["result"], c["note"]])
    return buf.getvalue()

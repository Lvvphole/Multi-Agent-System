"""run_stage0.py — Wire the harness and run Stage 0 end to end.

The two judges are pluggable. Here they are deterministic stubs so the run is
reproducible and testable. In production each `review_fn` wraps a SEPARATE model
instance/role (different from the Executor and, for the evaluator, ideally from
the verifier judge). The harness already refuses any judge whose model id equals
the Executor's (SelfJudgingError).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from harness import Harness, AlternateModelJudge, Verdict, freeze
from harness import stage0

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTRACT = os.path.join(ROOT, "CONTRACT.md")
EXECUTOR_MODEL = "executor-model-A"


def verify_review_fn(artifact_text, criteria):
    # Judge reads the artifact (not explanations). GREEN only if the
    # code-produced checklist shows all checks passed and no FAIL remains.
    if "ALL CHECKS PASS" in artifact_text and "— FAIL" not in artifact_text:
        return Verdict.GREEN, "checklist shows all Stage-0 checks PASS; no FAIL rows"
    return Verdict.RED, "checklist contains FAIL rows or missing pass marker"


def eval_review_fn(artifact_text, criteria):
    if "ALL CHECKS PASS" in artifact_text and "— FAIL" not in artifact_text:
        return Verdict.GREEN, "artifacts satisfy Stage-0 contract success criteria"
    return Verdict.RED, "Stage-0 criteria not satisfied"


def executor_fn_factory(checks):
    def executor_fn(name):
        out = os.path.join(ROOT, "artifacts", name)
        if name == "contract_requirements_checklist.md":
            content = stage0.write_checklist(checks)
        elif name == "contract_field_traceability_table.csv":
            content = stage0.write_traceability(checks)
        else:
            raise ValueError(f"stage0 executor does not produce {name}")
        with open(out, "w") as f:
            f.write(content)
    return executor_fn


def main():
    run_ctx = freeze(CONTRACT, model_id=EXECUTOR_MODEL,
                     prompt_version="p1", skill_version="s1", tool_version="t1")
    h = Harness(
        ROOT, run_ctx,
        verify_judge=AlternateModelJudge("verifier-model-B", verify_review_fn),
        eval_judge=AlternateModelJudge("evaluator-model-C", eval_review_fn),
        executor_model_id=EXECUTOR_MODEL,
    )
    checks = stage0.run_checks(open(CONTRACT).read())
    h.guard_contract_version()
    res = h.run_stage(
        "stage_0", owner="Executor", version="2.1.0",
        required_artifacts=["contract_requirements_checklist.md",
                            "contract_field_traceability_table.csv"],
        executor_fn=executor_fn_factory(checks),
        criteria="Stage 0 verifier checks C0.1-C0.12",
        change_summary="contract verification, no external action",
    )
    print("run_id:", run_ctx["run_id"])
    print("stage_0:", res.state)
    failed = [c for c in checks if c["result"] != "PASS"]
    print("failing checks:", [c["check_id"] for c in failed] or "none")
    return res


if __name__ == "__main__":
    main()

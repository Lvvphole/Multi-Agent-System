"""run_stage1.py — Run Stage 1 through the harness.

Executor drafts live in _authored/stage_1/; the executor_fn ingests them into
the harness-managed artifact store. The harness then runs structural checks +
the Stage-1 content checks + alternate-model judges + the gate.
"""
import os, sys, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from harness import Harness, AlternateModelJudge, Verdict, freeze
from harness import stage1

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTRACT = os.path.join(ROOT, "CONTRACT.md")
AUTHORED = os.path.join(ROOT, "_authored", "stage_1")
EXECUTOR_MODEL = "executor-model-A"

REQUIRED = ["multi_agent_requirements.md", "system_boundary_map.md",
            "input_output_contract.md", "constraint_register.md"]


def judge_fn(artifact_text, criteria):
    # Judge reviews artifact content. RED if drafting markers leak through or a
    # required structural marker is absent.
    bad = ["TODO", "PLACEHOLDER", "TBD", "<fill"]
    if any(b in artifact_text for b in bad):
        return Verdict.RED, "draft markers present"
    needed = ["## BOUNDARY", "## INPUTS", "## OUTPUTS", "## BLOCKERS",
              "architecture_decisions: deferred"]
    missing = [m for m in needed if m not in artifact_text]
    if missing:
        return Verdict.RED, f"missing required content: {missing}"
    return Verdict.GREEN, "boundary/IO/blockers present; no draft markers; arch deferred"


def executor_fn(name):
    src = os.path.join(AUTHORED, name)
    dst = os.path.join(ROOT, "artifacts", name)
    shutil.copyfile(src, dst)


def main():
    run_ctx = freeze(CONTRACT, EXECUTOR_MODEL, "p1", "s1", "t1")
    h = Harness(
        ROOT, run_ctx,
        verify_judge=AlternateModelJudge("verifier-model-B", judge_fn),
        eval_judge=AlternateModelJudge("evaluator-model-C", judge_fn),
        executor_model_id=EXECUTOR_MODEL,
    )
    res = h.run_stage(
        "stage_1", owner="Executor", version="2.0.0",
        required_artifacts=REQUIRED, executor_fn=executor_fn,
        criteria="Stage 1 verifier checks: boundary/interior/exterior, inputs/"
                 "outputs/transformations, roles, tools, external systems, "
                 "testable requirements, blockers, no premature architecture",
        change_summary="local design artifacts, no external action",
        extra_checks=stage1.make_checks(os.path.join(ROOT, "artifacts")),
    )
    print("run_id:", run_ctx["run_id"])
    print("stage_1:", res.state, "->", res.detail)
    return res


if __name__ == "__main__":
    main()

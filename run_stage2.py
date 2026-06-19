"""run_stage2.py — Run Stage 2 (role and agent model) through the harness."""
import os, sys, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from harness import Harness, AlternateModelJudge, Verdict, freeze
from harness import stage2

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTRACT = os.path.join(ROOT, "CONTRACT.md")
AUTHORED = os.path.join(ROOT, "_authored", "stage_2")
EXECUTOR_MODEL = "executor-model-A"

REQUIRED = ["agent_role_registry.json", "role_permission_matrix.md",
            "agent_handoff_protocol.md", "forbidden_actions_register.md"]


def judge_fn(artifact_text, criteria):
    bad = ["TODO", "PLACEHOLDER", "TBD", "<fill"]
    if any(b in artifact_text for b in bad):
        return Verdict.RED, "draft markers present"
    needed = ["forbidden_actions", "verify own work", "contract success criteria only",
              "HAP-", "judge its own artifacts"]
    missing = [m for m in needed if m not in artifact_text]
    if missing:
        return Verdict.RED, f"missing role-model content: {missing}"
    return Verdict.GREEN, "roles have IO/permissions/forbidden; executor barred from verify/eval/complete; alt-judge + human approval present"


def executor_fn(name):
    shutil.copyfile(os.path.join(AUTHORED, name), os.path.join(ROOT, "artifacts", name))


def main():
    run_ctx = freeze(CONTRACT, EXECUTOR_MODEL, "p1", "s1", "t1")
    h = Harness(
        ROOT, run_ctx,
        verify_judge=AlternateModelJudge("verifier-model-B", judge_fn),
        eval_judge=AlternateModelJudge("evaluator-model-C", judge_fn),
        executor_model_id=EXECUTOR_MODEL,
    )
    res = h.run_stage(
        "stage_2", owner="Executor", version="2.0.0",
        required_artifacts=REQUIRED, executor_fn=executor_fn,
        criteria="Stage 2 verifier checks: every agent has inputs/outputs/"
                 "permissions/forbidden; executor cannot verify/evaluate/"
                 "complete; verifier checks artifacts; evaluator scores against "
                 "contract; human approval points listed",
        change_summary="local design artifacts, no external action",
        extra_checks=stage2.make_checks(os.path.join(ROOT, "artifacts")),
    )
    print("run_id:", run_ctx["run_id"])
    print("stage_2:", res.state, "->", res.detail)
    return res


if __name__ == "__main__":
    main()

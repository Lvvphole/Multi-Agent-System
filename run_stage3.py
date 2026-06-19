"""run_stage3.py — Run Stage 3 (loop/skill/orchestrator architecture)."""
import os, sys, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from harness import Harness, freeze
from harness import stage3, judges_config

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTRACT = os.path.join(ROOT, "CONTRACT.md")
AUTHORED = os.path.join(ROOT, "_authored", "stage_3")

REQUIRED = ["loop_skill_orchestrator_model.md", "loop_registry_schema.json",
            "skill_registry_schema.json", "orchestrator_responsibility_matrix.md"]

# offline judge content markers (live mode uses the real alternate models)
MARKERS = ["## LOOP LAYER", "## SKILL LAYER", "## ORCHESTRATOR LAYER",
           "DurableRuntime", "hot deployment"]


def executor_fn(name):
    shutil.copyfile(os.path.join(AUTHORED, name), os.path.join(ROOT, "artifacts", name))


def main():
    run_ctx = freeze(CONTRACT, judges_config.EXECUTOR_MODEL, "p1", "s1", "t1")
    vj, ej, exe = judges_config.build_judges(run_id=run_ctx["run_id"],
                                             required_markers=MARKERS)
    h = Harness(ROOT, run_ctx, verify_judge=vj, eval_judge=ej,
                executor_model_id=exe)
    res = h.run_stage(
        "stage_3", owner="Executor", version="2.1.0",
        required_artifacts=REQUIRED, executor_fn=executor_fn,
        criteria="Stage 3: loops/skills/orchestrator separated; loops define "
                 "triggers/decision-points/state-reads/next-action; skills "
                 "define durable workflows/retry/input/output; orchestrator "
                 "defines scheduling/events/retries/concurrency/checkpointing/"
                 "observability/hot-deployment; DurableRuntime interface present",
        change_summary="local design artifacts, no external action",
        extra_checks=stage3.make_checks(os.path.join(ROOT, "artifacts")),
    )
    print("run_id:", run_ctx["run_id"])
    print("stage_3:", res.state, "->", res.detail)
    return res


if __name__ == "__main__":
    main()

"""run_stage4.py — Run Stage 4 (state, memory, and artifact stores)."""
import os, sys, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Harness, freeze
from harness import stage4, judges_config

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTRACT = os.path.join(ROOT, "CONTRACT.md")
AUTHORED = os.path.join(ROOT, "_authored", "stage_4")
REQUIRED = ["state_store_schema.json", "memory_architecture.md",
            "artifact_manifest_schema.json", "run_history_schema.json",
            "checkpoint_schema.json"]
MARKERS = ["## COMPLETED_VERIFIED", "## BLOCKERS", "created_at", "run_id"]

def executor_fn(name):
    shutil.copyfile(os.path.join(AUTHORED, name), os.path.join(ROOT, "artifacts", name))

def main():
    run_ctx = freeze(CONTRACT, judges_config.EXECUTOR_MODEL, "p1", "s1", "t1")
    vj, ej, exe = judges_config.build_judges(run_id=run_ctx["run_id"], required_markers=MARKERS)
    h = Harness(ROOT, run_ctx, verify_judge=vj, eval_judge=ej, executor_model_id=exe)
    res = h.run_stage(
        "stage_4", owner="Executor", version="2.1.0",
        required_artifacts=REQUIRED, executor_fn=executor_fn,
        criteria="Stage 4: state persists status/deps/owner/links/gate; memory "
                 "separates completed/in-progress/blockers/next/failures with "
                 "owner+retention+update rules; artifact store records filename/"
                 "checksum/owner/stage/version/created/verify; run history records "
                 "step/input/output/retry/failure/decision; checkpoint schema",
        change_summary="local design artifacts, no external action",
        extra_checks=stage4.make_checks(os.path.join(ROOT, "artifacts")),
    )
    print("run_id:", run_ctx["run_id"]); print("stage_4:", res.state, "->", res.detail)
    return res

if __name__ == "__main__":
    main()

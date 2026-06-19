"""stage3.py — Stage 3 verifier content checks, run by code.

Maps the contract's 16 Stage-3 verifier checks plus the DR-002 DurableRuntime
mandate and the A4 skill-validation fields to mechanical assertions.
"""
from __future__ import annotations
import json, os


def make_checks(artifact_dir: str):
    def read(name):
        p = os.path.join(artifact_dir, name)
        return open(p).read() if os.path.exists(p) else ""

    def loadj(name):
        try:
            return json.loads(read(name)), None
        except Exception as e:
            return None, str(e)

    def checks():
        f = []
        model = read("loop_skill_orchestrator_model.md")
        orch = read("orchestrator_responsibility_matrix.md")

        # 1 separation of loops / skills / orchestrator
        for marker in ("## LOOP LAYER", "## SKILL LAYER", "## ORCHESTRATOR LAYER",
                       "## SEPARATION RULES"):
            if marker not in model:
                f.append(f"VC1: model missing '{marker}'")

        # 2-5 loops define triggers / decision points / state reads / next-action
        loop_seg = model.split("## SKILL LAYER")[0].lower()
        for term, vc in [("trigger", "VC2"), ("decision point", "VC3"),
                         ("state read", "VC4"), ("next-action", "VC5")]:
            if term not in loop_seg:
                f.append(f"{vc}: loop layer missing '{term}'")

        # 6-9 skills define durable workflows / retry / input / output contract
        skill_seg = model.lower()
        for term, vc in [("durable workflow", "VC6"), ("retry behavior", "VC7"),
                         ("input contract", "VC8"), ("output contract", "VC9")]:
            if term not in skill_seg:
                f.append(f"{vc}: skill layer missing '{term}'")

        # 10-16 orchestrator defines scheduling/events/retries/concurrency/
        # checkpointing/observability/hot deployment
        both = (model + orch).lower()
        for term, vc in [("scheduling", "VC10"), ("event", "VC11"),
                         ("retr", "VC12"), ("concurrency", "VC13"),
                         ("checkpoint", "VC14"), ("observability", "VC15"),
                         ("hot deployment", "VC16")]:
            if term not in both:
                f.append(f"{vc}: orchestrator missing '{term}'")

        # DR-002 DurableRuntime interface present with key methods
        if "DurableRuntime" not in model:
            f.append("VC-dr002: DurableRuntime interface missing")
        for meth in ("run_step", "wait_signal", "resume", "acquire_concurrency_lock"):
            if meth not in model:
                f.append(f"VC-dr002: DurableRuntime missing method {meth}")

        # loop registry schema structural
        lr, err = loadj("loop_registry_schema.json")
        if err:
            f.append(f"VC-loopschema: not parseable ({err})")
        else:
            props = lr.get("properties", {})
            for k in ("trigger", "state_reads", "decision_points",
                      "next_action_logic", "stop_conditions"):
                if k not in props:
                    f.append(f"VC-loopschema: missing property {k}")

        # skill registry schema structural + A4 fields
        sr, err = loadj("skill_registry_schema.json")
        if err:
            f.append(f"VC-skillschema: not parseable ({err})")
        else:
            props = sr.get("properties", {})
            for k in ("retry_policy", "input_contract", "output_contract",
                      "status", "performance_metric", "holdout_validation",
                      "acceptance_bar", "half_life"):
                if k not in props:
                    f.append(f"VC-skillschema: missing property {k} (A4)")
            # continuous metric (A4)
            pm = props.get("performance_metric", {}).get("properties", {})
            if pm.get("type", {}).get("const") != "continuous":
                f.append("VC-skillschema: performance_metric.type not 'continuous' (A4)")
            # activation gate present
            if "allOf" not in sr:
                f.append("VC-skillschema: no activation gate (allOf if status==active)")

        # concurrency rules in matrix
        for rule in ("singleton", "per-agent", "per-skill", "per-resource", "per-run"):
            if rule not in orch.lower():
                f.append(f"VC13: concurrency rule '{rule}' missing in matrix")

        return f
    return checks

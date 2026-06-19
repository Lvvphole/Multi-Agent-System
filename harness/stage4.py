"""stage4.py — Stage 4 verifier content checks, run by code.

Maps the contract's 23 Stage-4 verifier checks (state / memory / artifact store /
run history) to mechanical assertions over the four schemas and the memory doc.
"""
from __future__ import annotations
import json, os


def make_checks(artifact_dir: str):
    def read(name):
        p = os.path.join(artifact_dir, name)
        return open(p).read() if os.path.exists(p) else ""

    def props(name):
        try:
            return json.loads(read(name)).get("properties", {}), None
        except Exception as e:
            return {}, str(e)

    def checks():
        f = []

        # 1-5 state persists status / dependencies / owner / artifact links / gate
        sp, err = props("state_store_schema.json")
        if err:
            f.append(f"VC-state: schema not parseable ({err})")
        for k, vc in [("state", "VC1-status"), ("prior_required", "VC2-deps"),
                      ("owner_role", "VC3-owner"), ("artifact_refs", "VC4-links"),
                      ("gate_decision", "VC5-gate")]:
            if k not in sp:
                f.append(f"{vc}: state_store_schema missing {k}")

        # 6-10 memory separates the five sections
        mem = read("memory_architecture.md")
        for sec, vc in [("## COMPLETED_VERIFIED", "VC6"), ("## IN_PROGRESS", "VC7"),
                        ("## BLOCKERS", "VC8"), ("## NEXT_ACTIONS", "VC9"),
                        ("## KNOWN_FAILURE_PATTERNS", "VC10")]:
            if sec not in mem:
                f.append(f"{vc}: memory_architecture missing {sec}")
        # each memory category needs owner/retention/update rules
        for term in ("owner=", "retention=", "update="):
            if mem.count(term) < 6:
                f.append(f"VC-mem-rules: fewer than 6 '{term}' (one per category)")

        # 11-17 artifact store records filename/checksum/owner/stage/version/
        # created timestamp/verification status
        ap, err = props("artifact_manifest_schema.json")
        if err:
            f.append(f"VC-artifact: schema not parseable ({err})")
        for k, vc in [("filename", "VC11"), ("checksum", "VC12"),
                      ("owner", "VC13"), ("stage", "VC14"), ("version", "VC15"),
                      ("created_at", "VC16"), ("verification_status", "VC17")]:
            if k not in ap:
                f.append(f"{vc}: artifact_manifest_schema missing {k}")

        # 18-23 run history records every step/input/output/retry/failure/decision
        rp, err = props("run_history_schema.json")
        if err:
            f.append(f"VC-runhist: schema not parseable ({err})")
        for k, vc in [("step_id", "VC18-step"), ("input_ref", "VC19-input"),
                      ("output_ref", "VC20-output"), ("retry_count", "VC21-retry"),
                      ("error", "VC22-failure"), ("decision", "VC23-decision")]:
            if k not in rp:
                f.append(f"{vc}: run_history_schema missing {k}")

        # checkpoint schema present with required durability fields (SC13)
        cp, err = props("checkpoint_schema.json")
        if err:
            f.append(f"VC-checkpoint: schema not parseable ({err})")
        for k in ("checkpoint_id", "status", "retry_count", "idempotency_key"):
            if k not in cp:
                f.append(f"VC-checkpoint: missing {k}")

        return f
    return checks

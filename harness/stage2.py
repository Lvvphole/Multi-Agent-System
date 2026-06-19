"""stage2.py — Stage 2 verifier content checks, run by code.

Maps the contract's 10 Stage-2 verifier checks to mechanical assertions over the
role registry JSON and the markdown artifacts.
"""
from __future__ import annotations
import json, os, re


def make_checks(artifact_dir: str):
    def read(name):
        p = os.path.join(artifact_dir, name)
        return open(p).read() if os.path.exists(p) else ""

    def checks():
        f = []
        try:
            reg = json.loads(read("agent_role_registry.json"))
            agents = reg.get("agents", {})
        except Exception as e:
            return [f"VC-registry: agent_role_registry.json not parseable: {e}"]

        if not agents:
            return ["VC-registry: no agents defined"]

        # 1-4 every agent has inputs/outputs/permissions/forbidden_actions
        for name, a in agents.items():
            for field in ("inputs", "outputs", "permissions", "forbidden_actions"):
                if not a.get(field):
                    f.append(f"VC-{field}: agent '{name}' missing/empty {field}")

        ex = agents.get("executor", {})
        ex_forbidden = " ".join(ex.get("forbidden_actions", [])).lower()
        # 5 executor cannot verify own work
        if "verify own" not in ex_forbidden:
            f.append("VC5: executor not forbidden from verifying own work")
        # 6 executor cannot evaluate own work
        if "evaluate own" not in ex_forbidden:
            f.append("VC6: executor not forbidden from evaluating own work")
        # 7 executor cannot complete own work
        if "completion" not in ex_forbidden and "self-certify" not in ex_forbidden:
            f.append("VC7: executor not forbidden from determining completion")

        # 8 verifier checks artifacts, not explanations
        ver = agents.get("verifier", {})
        ver_forbidden = " ".join(ver.get("forbidden_actions", [])).lower()
        ver_perm = " ".join(ver.get("permissions", [])).lower()
        if "explanation" not in ver_forbidden:
            f.append("VC8: verifier not forbidden from accepting explanations")
        if "artifact" not in ver_perm:
            f.append("VC8: verifier permissions do not reference checking artifacts")

        # 9 evaluator scores only against the contract
        ev = agents.get("evaluator", {})
        ev_perm = " ".join(ev.get("permissions", [])).lower()
        if "contract success criteria only" not in ev_perm:
            f.append("VC9: evaluator does not score against contract criteria only")

        # 10 human approval points listed for irreversible/external actions
        matrix = read("role_permission_matrix.md")
        if "Human approval points" not in matrix or "HAP-" not in matrix:
            f.append("VC10: human approval points not listed in permission matrix")
        # external action must never be a bare ALLOW; find the column by header
        rows = [l for l in matrix.splitlines() if l.strip().startswith("|")]
        ext_idx = None
        for r in rows:
            cells = [c.strip() for c in r.split("|")]
            if "ExternalAction" in cells:
                ext_idx = cells.index("ExternalAction")
                break
        if ext_idx is not None:
            for r in rows:
                cells = [c.strip() for c in r.split("|")]
                if len(cells) > ext_idx and cells[ext_idx] == "ALLOW":
                    f.append(f"VC10: ExternalAction is bare ALLOW in row: {cells[1]}")

        # alternate-judge rule present in forbidden register + handoff
        forb = read("forbidden_actions_register.md").lower()
        handoff = read("agent_handoff_protocol.md").lower()
        if "judge its own artifacts" not in forb and "judge_model == executor" not in forb:
            f.append("VC-altjudge: forbidden register missing self-judging rule")
        if "executor_model" not in handoff:
            f.append("VC-altjudge: handoff protocol missing alternate-judge precondition")

        # structural completeness markers
        for name, text in [("role_permission_matrix.md", matrix),
                           ("agent_handoff_protocol.md", read("agent_handoff_protocol.md")),
                           ("forbidden_actions_register.md", read("forbidden_actions_register.md"))]:
            if "architecture_decisions: deferred" not in text:
                f.append(f"VC-noarch: {name} missing architecture-deferral marker")
        if not re.search(r"FA-\d{2}", forb.upper()):
            f.append("VC-forbidden: no FA-## ids in forbidden_actions_register")

        return f
    return checks

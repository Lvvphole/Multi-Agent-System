"""stage1.py — Stage 1 verifier content checks, run by code.

Maps the contract's 12 Stage-1 verifier checks to mechanical assertions over the
authored artifact bytes. Returns a list of failure strings (empty == pass).
"""
from __future__ import annotations
import os, re


def make_checks(artifact_dir: str):
    def read(name):
        p = os.path.join(artifact_dir, name)
        return open(p).read() if os.path.exists(p) else ""

    def checks():
        f = []
        boundary = read("system_boundary_map.md")
        reqs = read("multi_agent_requirements.md")
        io = read("input_output_contract.md")
        cons = read("constraint_register.md")

        # 1-3 boundary / interior / exterior
        for marker, label in [("## BOUNDARY", "boundary"),
                              ("## INTERIOR", "interior"),
                              ("## EXTERIOR", "exterior")]:
            if marker not in boundary:
                f.append(f"VC{label}: '{marker}' missing in system_boundary_map.md")
        # 9 external systems
        if "## EXTERNAL SYSTEMS" not in boundary:
            f.append("VC-extsys: '## EXTERNAL SYSTEMS' missing")

        # 4-6 inputs / outputs / transformations
        for marker in ("## INPUTS", "## OUTPUTS", "## TRANSFORMATIONS"):
            if marker not in io:
                f.append(f"VC-io: '{marker}' missing in input_output_contract.md")

        # 7 roles, 8 tools
        if "ROLES referenced" not in reqs and "ROLES" not in reqs:
            f.append("VC-roles: roles not referenced in requirements")
        if "TOOLS referenced" not in reqs and "TOOLS" not in reqs:
            f.append("VC-tools: tools not referenced in requirements")

        # 10 every requirement testable: each R- id needs a verify: clause
        req_ids = re.findall(r"R-[FN]-\d{3}", reqs)
        verify_clauses = reqs.count("verify:")
        if not req_ids:
            f.append("VC-testable: no requirement IDs found")
        elif verify_clauses < len(set(req_ids)):
            f.append(f"VC-testable: {len(set(req_ids))} requirements but only "
                     f"{verify_clauses} verify: clauses")

        # 11 unavailable requirements marked as blockers
        if "## BLOCKERS" not in reqs:
            f.append("VC-blockers: no BLOCKERS section")
        else:
            blocker_ids = re.findall(r"B-\d{3}", reqs)
            if not blocker_ids:
                f.append("VC-blockers: BLOCKERS section has no B-### entries")
            if "status: BLOCKER" not in reqs:
                f.append("VC-blockers: no 'status: BLOCKER' marker")

        # constraint register: testable constraints
        cn_ids = re.findall(r"CN-\d{2}", cons)
        if len(set(cn_ids)) < 10 or cons.count("verify:") < len(set(cn_ids)):
            f.append("VC-constraints: constraints missing or not all testable")

        # 12 no architecture decision before requirements pass
        for name, text in [("system_boundary_map.md", boundary),
                           ("multi_agent_requirements.md", reqs),
                           ("input_output_contract.md", io),
                           ("constraint_register.md", cons)]:
            if "architecture_decisions: deferred" not in text:
                f.append(f"VC-noarch: {name} missing architecture-deferral marker")

        return f
    return checks

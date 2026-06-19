"""version_freeze.py — Per-run frozen context snapshot + checksums.

A run freezes contract/prompt/skill/tool versions, model id, and input
checksum. Any change creates a new run lineage (new run_id).
"""
from __future__ import annotations
import hashlib, json, time


def checksum_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def checksum_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode()).hexdigest()


def freeze(contract_path: str, model_id: str, prompt_version: str,
           skill_version: str, tool_version: str) -> dict:
    cc = checksum_file(contract_path)
    run_id = hashlib.sha256(
        f"{cc}{model_id}{prompt_version}{skill_version}{tool_version}"
        f"{time.time()}".encode()).hexdigest()[:12]
    return {
        "run_id": run_id,
        "contract_checksum": cc,
        "model_id": model_id,
        "prompt_version": prompt_version,
        "skill_version": skill_version,
        "tool_version": tool_version,
        "frozen_at": time.time(),
    }

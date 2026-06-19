"""replay_log.py — Append-only JSONL run log that survives restart.

Records every harness decision: stage transitions, verifier/evaluator
results, gate decisions, idempotency hits, escalations, human approvals.
A run path can be replayed from this file alone, with no model in the loop.
"""
from __future__ import annotations
import json, os, time


class ReplayLog:
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    def append(self, event_type: str, **fields):
        rec = {"ts": time.time(), "event": event_type, **fields}
        with open(self.path, "a") as f:
            f.write(json.dumps(rec) + "\n")
        return rec

    def read(self):
        if not os.path.exists(self.path):
            return []
        with open(self.path) as f:
            return [json.loads(l) for l in f if l.strip()]

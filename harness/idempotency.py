"""idempotency.py — Idempotency keys and a duplicate-detection ledger.

Every side effect (artifact write, tool call, message, sub-agent spawn,
external action) carries a key derived deterministically from its operation
+ inputs. The ledger persists, so a post-restart replay of the same op is
recognized as already-done instead of being executed twice.
"""
from __future__ import annotations
import hashlib, json, os, tempfile


def make_key(op: str, *parts: str) -> str:
    h = hashlib.sha256()
    h.update(op.encode())
    for p in parts:
        h.update(b"\x00")
        h.update(str(p).encode())
    return f"{op}:{h.hexdigest()[:16]}"


class IdempotencyLedger:
    def __init__(self, path: str):
        self.path = path
        self._seen = {}
        if os.path.exists(path):
            with open(path) as f:
                self._seen = json.load(f)

    def seen(self, key: str) -> bool:
        return key in self._seen

    def record(self, key: str, result_ref: str) -> bool:
        """Returns True if newly recorded, False if duplicate (no re-exec)."""
        if key in self._seen:
            return False
        self._seen[key] = result_ref
        self._flush()
        return True

    def result(self, key: str):
        return self._seen.get(key)

    def _flush(self):
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(self.path) or ".")
        with os.fdopen(fd, "w") as f:
            json.dump(self._seen, f, indent=2)
        os.replace(tmp, self.path)

"""llm_judge.py — Real, provider-agnostic LLM-as-judge adapter (resolves B-002).

Replaces the bare stub review_fns with production-shaped code:
- ModelClient interface; AnthropicClient (env key -> api.anthropic.com) and
  MockClient (offline/testing) implement it.
- LLMJudge builds a strict review prompt, calls the model, and parses+validates
  the JSON verdict against a schema before returning it.
- FAIL CLOSED: any error, missing key, malformed output, or schema violation
  yields RED (never an accidental GREEN). Credentials are read from the
  environment and never logged; this module never stores or prints a key.
- The harness still enforces judge_model_id != executor_model_id (alternate
  judge rule); LLMJudge exposes .model_id for that check.

Under DBOS (B-004), each LLMJudge call is wrapped as a @step so its result is
journaled on first execution and not re-run on replay (idempotent judge calls).
An optional idempotency_ledger gives the same behavior in the reference harness.
"""
from __future__ import annotations
import json, os, urllib.request, urllib.error
from .judge import Verdict
from .schema_validator import parse_and_validate, SchemaError
from .idempotency import make_key

VERDICT_SCHEMA = {
    "type": "object",
    "required": ["verdict", "justification"],
    "additionalProperties": True,
    "properties": {
        "verdict": {"enum": ["GREEN", "RED"]},
        "justification": {"type": "string", "minLength": 1},
    },
}

JUDGE_SYSTEM = (
    "You are an independent verification/evaluation judge in a contract-governed "
    "control system. You review ARTIFACT CONTENT only. You never accept the "
    "producer's explanations, intentions, usefulness, or confidence as evidence. "
    "You decide strictly against the stated CRITERIA. Respond with a single JSON "
    'object: {"verdict": "GREEN" | "RED", "justification": "<reason>"}. '
    "GREEN only if the artifact satisfies every criterion. No prose outside JSON."
)


class JudgeUnavailable(Exception):
    pass


class MockClient:
    """Offline client for tests; returns a scripted raw response."""
    def __init__(self, model_id: str, scripted_response: str):
        self.model_id = model_id
        self._resp = scripted_response

    def complete(self, system: str, user: str) -> str:
        return self._resp


class AnthropicClient:
    """Calls api.anthropic.com /v1/messages. Key from env; never logged."""
    def __init__(self, model_id: str, base_url: str = "https://api.anthropic.com",
                 timeout: float = 60.0):
        self.model_id = model_id
        self.base_url = base_url
        self.timeout = timeout

    def complete(self, system: str, user: str) -> str:
        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise JudgeUnavailable("ANTHROPIC_API_KEY not set")
        body = json.dumps({
            "model": self.model_id,
            "max_tokens": 1024,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }).encode()
        req = urllib.request.Request(
            f"{self.base_url}/v1/messages", data=body, method="POST",
            headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                     "content-type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                data = json.loads(r.read())
        except (urllib.error.URLError, TimeoutError) as e:
            raise JudgeUnavailable(f"model call failed: {e}")
        parts = [b.get("text", "") for b in data.get("content", [])
                 if b.get("type") == "text"]
        return "".join(parts).strip()


class LLMJudge:
    """Callable with the review_fn signature: (artifact_text, criteria) ->
    (Verdict, justification). Fails closed."""
    def __init__(self, client, idempotency_ledger=None, run_id: str = "run"):
        self.client = client
        self.model_id = client.model_id
        self.ledger = idempotency_ledger
        self.run_id = run_id

    def __call__(self, artifact_text: str, criteria: str):
        # journal the judge call so replay does not re-invoke the model
        if self.ledger is not None:
            key = make_key("judge", self.run_id, self.model_id,
                           str(hash(artifact_text)), str(hash(criteria)))
            cached = self.ledger.result(key)
            if cached:
                v, j = json.loads(cached)
                return Verdict(v), j
        user = (f"CRITERIA:\n{criteria}\n\nARTIFACT CONTENT:\n{artifact_text}\n\n"
                "Return only the JSON verdict object.")
        try:
            raw = self.client.complete(JUDGE_SYSTEM, user)
            data = parse_and_validate(raw, VERDICT_SCHEMA)
        except (JudgeUnavailable, SchemaError) as e:
            return Verdict.RED, f"fail-closed: judge unavailable/invalid ({e})"
        except Exception as e:  # any unexpected error -> fail closed
            return Verdict.RED, f"fail-closed: unexpected judge error ({e})"
        verdict, just = Verdict(data["verdict"]), data["justification"]
        if self.ledger is not None:
            self.ledger.record(key, json.dumps([verdict.value, just]))
        return verdict, just

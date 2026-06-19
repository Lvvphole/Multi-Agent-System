# DR-001 — Model provider and judge model identities (resolves B-002)

date: 2026-06-19
status: ACCEPTED (default; owner may override the open decision below)
class: MINOR (no security/deletion impact)
supersedes_blocker: B-002

## Decision
Provider: Anthropic (single provider for the default; one credential).
Pinned, all-distinct model identities (satisfies the alternate-judge rule
judge_model_id != executor_model_id, and judge != judge where feasible):

- Executor        = claude-opus-4-8   (most capable; drafts artifacts)
- Verifier judge  = claude-sonnet-4-6  (independent structural+semantic review)
- Evaluator judge = claude-haiku-4-5   (scores against contract criteria)

Wiring: harness/llm_judge.py (AnthropicClient -> api.anthropic.com /v1/messages),
selected via harness/judges_config.py mode="live". Credentials come from the
ANTHROPIC_API_KEY environment variable at call time and are never read, stored,
or logged by the code. The judge output is JSON, schema-validated before use,
and fails closed (RED) on any error, missing key, or invalid output.

## Rationale
- Single provider = one credential, simplest to operate. Three distinct model
  tiers give real cross-checking without a second vendor.
- Each LLM judge call is wrapped (DBOS @step / harness idempotency ledger) so a
  replay after restart reuses the journaled verdict rather than re-calling.

## Open decision (owner)
Evaluator on claude-haiku-4-5 is the weakest link for contract-scoring judgment.
Two stronger options, both requiring an owner choice:
  (a) Evaluator = claude-sonnet-4-6 (verifier and evaluator share a model; still
      distinct from the executor — the hard rule holds). Higher cost.
  (b) Evaluator = a cross-provider model (e.g. a non-Anthropic frontier model)
      for true vendor independence. Requires a second provider + credential +
      cost approval (would itself be a new decision record).

## What is NOT done here (requires owner)
- No credential is provisioned or handled by the assistant (prohibited).
- No live API cost is incurred until the owner sets MAS_JUDGE_MODE=live with a
  key present. Default repo mode remains "offline" (deterministic, no cost).

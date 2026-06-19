"""judges_config.py — Pinned judge models (DR-001) and judge wiring (B-002).

Modes:
- "offline" (default): deterministic marker-based review_fns. Lets the repo run
  and tests pass with no credentials or cost. Used for reproducible gating.
- "live": real alternate-model judges via AnthropicClient. Requires
  ANTHROPIC_API_KEY in the environment (this module never reads or logs the key
  itself; AnthropicClient reads it at call time). Fails closed if absent.

Pinned model identities (DR-001) — all distinct, satisfying the alternate-judge
rule (judge_model_id != executor_model_id):
  EXECUTOR        = claude-opus-4-8
  VERIFIER_JUDGE  = claude-sonnet-4-6
  EVALUATOR_JUDGE = claude-haiku-4-5
Override EVALUATOR_JUDGE to a stronger or cross-provider model for greater
independence (see DR-001 'open decision').
"""
from __future__ import annotations
import os
from .judge import AlternateModelJudge, Verdict
from .llm_judge import LLMJudge, AnthropicClient

EXECUTOR_MODEL = "claude-opus-4-8"
VERIFIER_JUDGE_MODEL = "claude-sonnet-4-6"
EVALUATOR_JUDGE_MODEL = "claude-haiku-4-5"


def _offline_review_fn(required_markers):
    def review(artifact_text, criteria):
        bad = ["TODO", "PLACEHOLDER", "TBD", "<fill"]
        if any(b in artifact_text for b in bad):
            return Verdict.RED, "draft markers present"
        missing = [m for m in required_markers if m not in artifact_text]
        if missing:
            return Verdict.RED, f"missing required content: {missing}"
        return Verdict.GREEN, "offline marker checks satisfied"
    return review


def build_judges(mode: str = None, run_id: str = "run", ledger=None,
                 required_markers=None):
    """Returns (verify_judge, eval_judge, executor_model_id)."""
    mode = mode or os.environ.get("MAS_JUDGE_MODE", "offline")
    required_markers = required_markers or []
    if mode == "live":
        vj = AlternateModelJudge(
            VERIFIER_JUDGE_MODEL,
            LLMJudge(AnthropicClient(VERIFIER_JUDGE_MODEL), ledger, run_id))
        ej = AlternateModelJudge(
            EVALUATOR_JUDGE_MODEL,
            LLMJudge(AnthropicClient(EVALUATOR_JUDGE_MODEL), ledger, run_id))
    else:
        vj = AlternateModelJudge(VERIFIER_JUDGE_MODEL,
                                 _offline_review_fn(required_markers))
        ej = AlternateModelJudge(EVALUATOR_JUDGE_MODEL,
                                 _offline_review_fn(required_markers))
    return vj, ej, EXECUTOR_MODEL

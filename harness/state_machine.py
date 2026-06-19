"""state_machine.py — Transition legality, decided by code.

The harness, not the model, decides whether a transition is allowed.
Invalid transitions raise; they are never silently accepted.
"""
from __future__ import annotations
from .state_store import StateStore, State

# Allowed direct transitions for a single stage.
ALLOWED = {
    State.LOCKED:    {State.RUNNING, State.ESCALATED},
    State.RUNNING:   {State.PASSED, State.FAILED, State.ESCALATED},
    State.FAILED:    {State.RUNNING, State.ESCALATED},   # retry per policy
    State.ESCALATED: {State.RUNNING},                    # resumed after resolution
    State.PASSED:    set(),                               # terminal for the stage
}


class TransitionError(Exception):
    pass


class StateMachine:
    def __init__(self, store: StateStore):
        self.store = store

    def can_start(self, stage_id: str) -> tuple[bool, str]:
        rec = self.store.get(stage_id)
        if State(rec.state) != State.LOCKED and State(rec.state) not in (
            State.FAILED, State.ESCALATED):
            return False, f"{stage_id} is {rec.state}, not startable"
        if rec.prior_required is not None:
            prior = self.store.get(rec.prior_required)
            if State(prior.state) != State.PASSED:
                return (False,
                        f"prior stage {rec.prior_required} is {prior.state}, "
                        f"must be PASSED before {stage_id} may start")
        return True, "ok"

    def transition(self, stage_id: str, to: State, **changes):
        rec = self.store.get(stage_id)
        cur = State(rec.state)
        if to not in ALLOWED[cur]:
            raise TransitionError(
                f"illegal transition {stage_id}: {cur.value} -> {to.value}")
        if to == State.RUNNING:
            ok, why = self.can_start(stage_id)
            if not ok:
                raise TransitionError(f"cannot start {stage_id}: {why}")
        if to == State.PASSED:
            # gate evidence is mandatory and checked here, in code
            if rec.verifier_result != "PASS":
                raise TransitionError(
                    f"{stage_id} -> PASSED blocked: verifier_result="
                    f"{rec.verifier_result}")
            if rec.evaluator_result != "PASS":
                raise TransitionError(
                    f"{stage_id} -> PASSED blocked: evaluator_result="
                    f"{rec.evaluator_result}")
        return self.store.update(stage_id, state=to.value, **changes)

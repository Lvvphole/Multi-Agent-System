"""test_harness.py — Proves the control guardrails fail closed.

Each test forces a violation the contract forbids and asserts the harness
blocks it. Run: python3 -m pytest tests/ -q   (or python3 tests/test_harness.py)
"""
import os, sys, tempfile, shutil, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness import (Harness, AlternateModelJudge, Verdict, freeze,
                     StateMachine, State, TransitionError, SelfJudgingError,
                     parse_and_validate, SchemaError)


def green(_t, _c): return Verdict.GREEN, "ok"
def red(_t, _c):   return Verdict.RED, "nope"


def make_harness(root, exec_model="A", vmodel="B", emodel="C",
                 vfn=green, efn=green):
    contract = os.path.join(root, "CONTRACT.md")
    with open(contract, "w") as f:
        f.write("contract_version: test\n")
    ctx = freeze(contract, exec_model, "p", "s", "t")
    return Harness(root, ctx,
                   AlternateModelJudge(vmodel, vfn),
                   AlternateModelJudge(emodel, efn),
                   executor_model_id=exec_model)


def writer(root, content="real content"):
    def fn(name):
        with open(os.path.join(root, "artifacts", name), "w") as f:
            f.write(content)
    return fn


class GuardrailTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.root)

    def pass_stage0(self, h):
        return h.run_stage("stage_0", owner="Executor", version="1",
                           required_artifacts=["a.md"],
                           executor_fn=writer(self.root), criteria="c",
                           change_summary="local only")

    def test_gate_order_no_skip(self):
        h = make_harness(self.root)
        # stage_1 must not start before stage_0 is PASSED
        res = h.run_stage("stage_1", owner="Executor", version="1",
                          required_artifacts=["b.md"],
                          executor_fn=writer(self.root), criteria="c")
        self.assertEqual(res.state, "BLOCKED")

    def test_self_judging_blocked(self):
        # judge model id == executor model id -> escalate, never honored
        h = make_harness(self.root, exec_model="A", vmodel="A")
        res = self.pass_stage0(h)
        self.assertEqual(res.state, "ESCALATED")
        self.assertIn("alternate judge", res.detail.lower())

    def test_placeholder_artifact_fails(self):
        h = make_harness(self.root)
        res = h.run_stage("stage_0", owner="Executor", version="1",
                          required_artifacts=["a.md"],
                          executor_fn=writer(self.root, content=""),  # empty
                          criteria="c")
        self.assertEqual(res.state, "FAILED")
        self.assertTrue(any("empty/placeholder" in x for x in res.detail))

    def test_verify_judge_red_fails_closed(self):
        h = make_harness(self.root, vfn=red)
        res = self.pass_stage0(h)
        self.assertEqual(res.state, "FAILED")

    def test_human_gate_blocks_destructive(self):
        h = make_harness(self.root)
        res = h.run_stage("stage_0", owner="Executor", version="1",
                          required_artifacts=["a.md"],
                          executor_fn=writer(self.root), criteria="c",
                          change_summary="hard delete of run lineage")
        self.assertEqual(res.state, "ESCALATED")
        # now record human approval bound to the artifact checksums, retry
        cks = h.artifacts.checksums(["a.md"])
        from harness import ChangeClass
        h.human.record("owner", ChangeClass.DESTRUCTIVE, "approved purge",
                       cks, "APPROVE", "reviewed")
        res2 = h.run_stage("stage_0", owner="Executor", version="1",
                           required_artifacts=["a.md"],
                           executor_fn=writer(self.root), criteria="c",
                           change_summary="hard delete of run lineage")
        self.assertEqual(res2.state, "PASSED")

    def test_idempotency_no_duplicate_write(self):
        h = make_harness(self.root)
        calls = {"n": 0}
        def counting(name):
            calls["n"] += 1
            with open(os.path.join(self.root, "artifacts", name), "w") as f:
                f.write("x")
        h.run_stage("stage_0", owner="Executor", version="1",
                    required_artifacts=["a.md"], executor_fn=counting,
                    criteria="c")
        first = calls["n"]
        # re-run same stage/run: writes must be skipped via idempotency ledger
        h.run_stage("stage_0", owner="Executor", version="1",
                    required_artifacts=["a.md"], executor_fn=counting,
                    criteria="c")
        self.assertEqual(calls["n"], first)  # no duplicate write

    def test_restart_recovery(self):
        h = make_harness(self.root)
        self.pass_stage0(h)
        # simulate process restart: brand-new Harness reading the same disk
        ctx = freeze(os.path.join(self.root, "CONTRACT.md"), "A", "p", "s", "t")
        h2 = Harness(self.root, ctx,
                     AlternateModelJudge("B", green),
                     AlternateModelJudge("C", green), executor_model_id="A")
        self.assertEqual(h2.store.get("stage_0").state, State.PASSED.value)
        ok, _ = h2.sm.can_start("stage_1")
        self.assertTrue(ok)  # stage_1 now legal, resumed from disk

    def test_illegal_transition_rejected(self):
        h = make_harness(self.root)
        with self.assertRaises(TransitionError):
            h.sm.transition("stage_0", State.PASSED)  # LOCKED->PASSED illegal

    def test_stage1_content_checks_fail_closed(self):
        # Stage-1 verifier content checks must catch a missing required section.
        from harness import stage1
        adir = os.path.join(self.root, "artifacts")
        os.makedirs(adir, exist_ok=True)
        good_boundary = "## BOUNDARY x\n## INTERIOR x\n## EXTERIOR x\n## EXTERNAL SYSTEMS x\narchitecture_decisions: deferred"
        files = {
            "system_boundary_map.md": good_boundary,
            "input_output_contract.md": "## INPUTS\n## OUTPUTS\n## TRANSFORMATIONS\narchitecture_decisions: deferred",
            "multi_agent_requirements.md": "ROLES\nTOOLS\nR-F-001 x verify: y\narchitecture_decisions: deferred",  # no BLOCKERS
            "constraint_register.md": "\n".join(f"CN-{i:02d} verify: x" for i in range(1, 12)) + "\narchitecture_decisions: deferred",
        }
        for n, c in files.items():
            with open(os.path.join(adir, n), "w") as fh:
                fh.write(c)
        failures = stage1.make_checks(adir)()
        self.assertTrue(any("BLOCKER" in x for x in failures))

    def test_stage2_executor_cannot_self_certify(self):
        # Removing the Executor's verify/evaluate/complete bars must be caught.
        import json
        from harness import stage2
        adir = os.path.join(self.root, "artifacts")
        os.makedirs(adir, exist_ok=True)
        reg = {"agents": {
            "executor": {"inputs": ["x"], "outputs": ["y"],
                         "permissions": ["produce"],
                         "forbidden_actions": ["compress artifacts"]},  # bars removed
            "verifier": {"inputs": ["x"], "outputs": ["y"],
                         "permissions": ["check artifacts"],
                         "forbidden_actions": ["accept explanation"]},
            "evaluator": {"inputs": ["x"], "outputs": ["y"],
                          "permissions": ["score against contract success criteria only"],
                          "forbidden_actions": ["execute"]},
        }}
        with open(os.path.join(adir, "agent_role_registry.json"), "w") as fh:
            json.dump(reg, fh)
        for n in ("role_permission_matrix.md", "agent_handoff_protocol.md",
                  "forbidden_actions_register.md"):
            with open(os.path.join(adir, n), "w") as fh:
                fh.write("architecture_decisions: deferred\nFA-01 executor_model\nHAP-1\n")
        failures = stage2.make_checks(adir)()
        self.assertTrue(any("VC5" in x for x in failures))
        self.assertTrue(any("VC7" in x for x in failures))

    def test_llm_judge_parses_and_fails_closed(self):
        from harness import LLMJudge, MockClient, AnthropicClient
        # valid GREEN
        j = LLMJudge(MockClient("verifier-model-B",
                                '{"verdict":"GREEN","justification":"meets criteria"}'))
        v, why = j("artifact", "criteria")
        self.assertEqual(v.value, "GREEN")
        # valid RED
        j = LLMJudge(MockClient("verifier-model-B",
                                '{"verdict":"RED","justification":"missing X"}'))
        self.assertEqual(j("a", "c")[0].value, "RED")
        # malformed JSON -> fail CLOSED (RED), never accidental GREEN
        j = LLMJudge(MockClient("verifier-model-B", "yes looks good to me"))
        v, why = j("a", "c")
        self.assertEqual(v.value, "RED")
        self.assertIn("fail-closed", why)
        # missing API key -> fail CLOSED
        os.environ.pop("ANTHROPIC_API_KEY", None)
        j = LLMJudge(AnthropicClient("verifier-model-B"))
        v, why = j("a", "c")
        self.assertEqual(v.value, "RED")
        self.assertIn("fail-closed", why)

    def test_llm_judge_honors_alternate_judge_rule(self):
        # LLMJudge wired through AlternateModelJudge still blocks self-judging
        from harness import AlternateModelJudge, LLMJudge, MockClient, SelfJudgingError
        same = AlternateModelJudge(
            "executor-model-A",
            LLMJudge(MockClient("executor-model-A",
                                '{"verdict":"GREEN","justification":"x"}')))
        with self.assertRaises(SelfJudgingError):
            same.review("executor-model-A", "art", "crit", [])

    def test_stage3_checks_fail_closed(self):
        from harness import stage3
        adir = os.path.join(self.root, "artifacts")
        os.makedirs(adir, exist_ok=True)
        # model missing a DurableRuntime method
        with open(os.path.join(adir, "loop_skill_orchestrator_model.md"), "w") as fh:
            fh.write("## LOOP LAYER trigger decision point state read next-action\n"
                     "## SKILL LAYER durable workflow retry behavior input contract output contract\n"
                     "## ORCHESTRATOR LAYER scheduling event retry concurrency checkpoint observability hot deployment\n"
                     "## SEPARATION RULES\nDurableRuntime run_step wait_signal resume\n")  # no acquire_concurrency_lock
        for n in ("loop_registry_schema.json", "skill_registry_schema.json",
                  "orchestrator_responsibility_matrix.md"):
            with open(os.path.join(adir, n), "w") as fh:
                fh.write("{}" if n.endswith(".json") else "x")
        failures = stage3.make_checks(adir)()
        self.assertTrue(any("acquire_concurrency_lock" in x for x in failures))

    def test_a4_skill_activation_gate_enforced(self):
        # An 'active' skill lacking passed held-out validation must be rejected
        # by the schema; a fully-validated one accepted.
        import json
        from harness import validate, SchemaError
        schema = json.load(open(os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "artifacts", "skill_registry_schema.json")))
        base = {"skill_id": "s", "version": "1", "durable": True,
                "input_contract": "i", "output_contract": "o", "status": "active",
                "owner_role": "x",
                "retry_policy": {"max_retries": 1, "backoff": "fixed",
                                 "retry_scope": "step", "idempotent": True},
                "performance_metric": {"name": "stab", "type": "continuous",
                                       "definition": "mean/std"}}
        with self.assertRaises(SchemaError):
            validate(base, schema)  # active without held-out -> rejected
        good = dict(base,
                    holdout_validation={"holdout_runs": ["r"], "metric_value": 0.7,
                                        "passed": True, "tuning_runs_excluded": True},
                    acceptance_bar={"attempt_count": 3, "required_metric": 0.6},
                    half_life={"estimate_days": 40, "floor_days": 10, "passed": True})
        validate(good, schema)  # should not raise

    def test_stage4_schemas_match_harness_shapes(self):
        # The authored state/manifest schemas must validate the harness's own
        # record shapes (design <-> implementation coherence).
        import json
        from dataclasses import asdict
        from harness import validate, StageRecord
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sschema = json.load(open(os.path.join(base, "artifacts", "state_store_schema.json")))
        rec = asdict(StageRecord(stage_id="stage_0", stage_name="x",
                                 prior_required=None, state="PASSED",
                                 owner_role="Executor", verifier_result="PASS",
                                 evaluator_result="PASS", gate_decision="PASSED",
                                 run_id="r", contract_version="sha256:" + "0" * 64))
        validate(rec, sschema)  # must not raise
        aschema = json.load(open(os.path.join(base, "artifacts", "artifact_manifest_schema.json")))
        entry = {"filename": "a.md", "owner": "Executor", "stage": "stage_0",
                 "version": "1", "checksum": "sha256:" + "a" * 64,
                 "created_at": 1.0, "verification_status": "PASS",
                 "evaluator_status": "PASS"}
        validate(entry, aschema)  # must not raise

    def test_schema_validation_rejects_bad_output(self):
        schema = {"type": "object", "required": ["verdict"],
                  "properties": {"verdict": {"enum": ["GREEN", "RED"]}}}
        with self.assertRaises(SchemaError):
            parse_and_validate('{"verdict": "maybe"}', schema)
        # valid output passes
        self.assertEqual(parse_and_validate('{"verdict":"GREEN"}', schema)["verdict"],
                         "GREEN")


if __name__ == "__main__":
    unittest.main(verbosity=2)

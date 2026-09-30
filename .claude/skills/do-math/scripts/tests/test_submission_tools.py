"""Exercise the actual producer command in its supplied, standalone workspace.

The other tests of this module moved to the new system (tests/migration/dispositions/submission.2.json).
This one stays until ``scheduled_operator.recovery`` takes the ports it runs on: it opens its repository
with the Git process and its runner with the host's provider CLI and Windows Job, so only a patched
``ModelRunner`` keeps it off a real model.
"""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import purpose_fixtures as purpose
from research_fixtures import local_job_runner


class OperatorProducerTests(purpose.ActivatedPurposeHarness):
    def test_failure_recovery_preserves_a_structured_nonresearch_report(self):
        from unittest.mock import patch
        from do_math import scheduled_operator as operator
        engine, _ = self.make_active(**self.fixture_config(scholarly_enabled=False, operator_enabled=True))
        observed = []
        class Runner:
            @local_job_runner
            def run(inner, **args):
                args["on_started"]()
                self.assertEqual(args["output_schema"], operator.OPERATOR_SCHEMA)
                self.assertIn("Synthetic launcher failure", args["prompt"])
                self.assertFalse((args["workspace"] / "input/submission/context.json").exists(),
                                 "installation recovery must not acquire the research submission path")
                output = {"summary": "Observed current status.", "observed_status": "ready", "actions": [],
                          "evidence_paths": [], "user_questions": [], "next_step": "Return the recorded observation."}
                observed.append(output)
                # ModelRunner owns schema validation; this fixture reports the
                # corresponding failed execution without granting repair success.
                return {"status": "failed", "output": output, "usage": {}, "error_kind": "output_validation",
                        "error": "Scripted diagnosis remains incomplete"}
        with patch.object(operator, "ModelRunner", Runner):
            result = operator.recovery(self.repo, engine.instance["id"], self.root,
                failure={"kind": "engine_unavailable", "error": "Synthetic launcher failure"})
        self.assertEqual(result["outcome"], "recovery_failed", result)
        self.assertEqual(len(observed), 1)
        _, state, runtime = operator.ResearchRepository(self.repo, engine.instance["id"]).load()
        execution = runtime["executions"][result["execution_id"]]
        self.assertEqual(execution["output"], observed[0])
        self.assertEqual(execution["outcome"], "execution_incomplete")
        self.assertNotIn("submission_receipt", execution)
        self.assertEqual(runtime["activities"][execution["owner_activity_id"]]["waiting"]["reason"], "recovery_failed")
        self.assertEqual(state["knowledge"], engine.instance["knowledge"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

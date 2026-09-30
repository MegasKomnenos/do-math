"""An identity review's own inputs on a Sim: an oversized retained history and the supplied source's aliases.

The start is ``support.review_sim.opened_sim``: a theorem imported by control
whose identity review the owner opened, its scope action queued. The legacy
tests reached a review opened by the synthetic task flow
(``purpose_fixtures.purpose_state``); no model call is made here.
"""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from do_math.review_cycle import record_turn
from support.engine_lifecycle import applied
from support.review_sim import opened_sim
from support.submission_calls import submission_model


def setUpModule():
    opened_sim()


class ReviewInputTests(unittest.TestCase):
    def test_large_own_review_history_does_not_request_mathematical_reconstruction(self):
        """The name says no reconstruction is requested; like the legacy test, this checks no model call and no resource disposition."""
        sim = opened_sim()
        engine = sim.engine
        self.assertEqual(engine.runtime["queue"][0]["role"], "identity_review")
        action = next(a for a in engine.runtime["queue"] if a["role"] == "identity_review")
        cid, kid = action["review_cycle_id"], action["target"]
        # The review input limit is its pinned profile's (context_store.prepare_role_input),
        # not the live config; the retained history alone exceeds it.
        limit = engine._execution_profile(action)["input"]["max_input_bytes"]
        engine.runtime["review_cycles"][cid] = record_turn(engine.runtime["review_cycles"][cid], action["slot"], [
            {"role": "assistant", "content": "Retained earlier reasoning. " * (limit // 28 + 1),
             "message_id": "retained-history"}])
        before = deepcopy(engine.instance["knowledge"][kid])
        engine._save()
        model = submission_model(sim)
        sim.step()
        self.assertEqual(model.calls, [])
        self.assertEqual(sim.instance["knowledge"][kid], before)
        self.assertFalse(any(row.get("event") == "review_resource_disposition"
                             for row in sim.runtime["review_cycles"][cid]["history"]))

    def test_fixed_question_resolver_accepts_the_supplied_source_aliases(self):
        # Review input reads the instance's supplied sources when it is prepared,
        # so the source may arrive after the cycle opened.
        sim = opened_sim()
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        path = root / "paper.txt"
        path.write_text("The exact original source.", encoding="utf-8")
        applied(sim, "source", config={"path": str(path)})
        engine = sim.engine
        action = next(a for a in engine.runtime["queue"] if a["role"] == "identity_review")
        context = engine._context(action, root / "source-alias-input")
        source = context["sources"][0]
        cycle = engine.runtime["review_cycles"][action["review_cycle_id"]]
        for reference in (source["id"], "source:" + source["name"], source["local_path"], source["path"], source["name"]):
            with self.subTest(reference=reference):
                error = resolved = None
                try:
                    resolved = engine._research_source_spec(cycle, action, reference)
                except ValueError as rejected:
                    error = str(rejected)
                self.assertIsNone(error, "a supplied source alias was refused: " + str(error))
                self.assertEqual(resolved["sha256"], source["sha256"])


if __name__ == "__main__":
    unittest.main()

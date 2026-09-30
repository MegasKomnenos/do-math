"""A HOLD marker stops installation recovery before it opens the repository or calls a model (``scheduled_operator.recovery``, layer 3).

``recovery`` reads the operator's HOLD marker in the workspace before anything
else; the case's instance ID names no repository, so opening one would fail.
The calls are observed on the unchanged product (``ObservedCalls``).
"""
from pathlib import Path
import tempfile
import unittest

from do_math import scheduled_operator
from do_math.model_runner import ModelRunner
from do_math.repository import ResearchRepository
from support.provider_probes import ObservedCalls


class HoldTests(unittest.TestCase):
    def test_recovery_cannot_ignore_hold(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scheduled_operator.hold(root, reason="test")
            with ObservedCalls(run=ModelRunner.run, repository=ResearchRepository.__init__) as observed:
                result = scheduled_operator.recovery(root, "unused", root,
                                                     failure={"kind": "engine_unavailable", "error": "fixture"})
            self.assertEqual(result, {"outcome": "held"})
            self.assertEqual(observed.count("run"), 0)
            self.assertEqual(observed.count("repository"), 0, "a held recovery opens no repository")


if __name__ == "__main__":
    unittest.main()

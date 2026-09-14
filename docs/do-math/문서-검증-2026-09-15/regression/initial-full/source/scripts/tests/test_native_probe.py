"""Check the native probe's interpretation without changing OS permissions."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from probe_native_isolation import CANARY_A, samples_are_isolated


class NativeProbeInterpretationTests(unittest.TestCase):
    def test_complete_positive_control_and_denial_are_required(self):
        sample = {"own_state": "read", "own_content": CANARY_A, "other_state": "access_denied"}
        timeline = {"before_b": 1, "during_b": 1, "after_b": 1}
        self.assertTrue(samples_are_isolated([sample], timeline))
        for state in ("file_missing", "program_failed", "read"):
            with self.subTest(state=state):
                self.assertFalse(samples_are_isolated([{**sample, "other_state": state}], timeline))
        self.assertFalse(samples_are_isolated([{**sample, "own_content": "wrong"}], timeline))

    def test_missing_observation_phase_is_incomplete(self):
        sample = {"own_state": "read", "own_content": CANARY_A, "other_state": "access_denied"}
        for phase in ("before_b", "during_b", "after_b"):
            timeline = {"before_b": 1, "during_b": 1, "after_b": 1, phase: 0}
            self.assertFalse(samples_are_isolated([sample], timeline))
        self.assertFalse(samples_are_isolated([], {"before_b": 1, "during_b": 1, "after_b": 1}))


if __name__ == "__main__":
    unittest.main()

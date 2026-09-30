"""The input overflow retry marker (``ResearchEngine._pending_input_overflow_retry``, a static rule of the engine; layer 2)."""
import unittest

from do_math.engine import ResearchEngine


class InputRecoveryMarkerUnitTests(unittest.TestCase):
    def test_only_explicit_pending_retry_marker_is_active(self):
        pending = {'input_overflow_retry': {'question_id': 'QU', 'state': 'pending'}}
        legacy_pending = {'input_overflow_retry': {'question_id': 'QU'}}
        resolved = {'input_overflow_retry': {'question_id': 'QU', 'state': 'resolved'}}
        failed = {'input_overflow_retry': {'question_id': 'QU', 'state': 'failed'}}
        self.assertEqual(ResearchEngine._pending_input_overflow_retry(pending), pending['input_overflow_retry'])
        self.assertIsNone(ResearchEngine._pending_input_overflow_retry(legacy_pending))
        self.assertIsNone(ResearchEngine._pending_input_overflow_retry(resolved))
        self.assertIsNone(ResearchEngine._pending_input_overflow_retry(failed))


if __name__ == '__main__':
    unittest.main()

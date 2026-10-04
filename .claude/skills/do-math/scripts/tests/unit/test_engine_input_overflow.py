"""The input overflow retry marker (``ResearchEngine._pending_input_overflow_retry``, a static rule of the engine; layer 2)."""
import unittest

from do_math.engine import ResearchEngine


class InputRecoveryMarkerUnitTests(unittest.TestCase):
    def test_overflow_disposition_covers_each_current_cause_and_larger_profile_choice(self):
        from do_math.input_recovery import input_overflow_disposition
        causes = ('common_documents_or_governance', 'required_role_input',
                  'current_proposal_or_required_sources', 'restored_dialogue')
        for cause in causes:
            for candidates in ([], ['EP-larger']):
                with self.subTest(cause=cause, candidates=candidates):
                    expected = ('unresolved_to_review_plan' if cause == 'current_proposal_or_required_sources' else
                                'plan_allowed_profile' if candidates else 'request_user_decision')
                    self.assertEqual(input_overflow_disposition(cause, candidates), expected)

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

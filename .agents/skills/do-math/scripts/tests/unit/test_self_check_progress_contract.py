"""4-C: rejected answers do not count; every declared progress result does."""
from pathlib import Path
import tempfile
import unittest

from do_math.control_protocol import SELF_CHECK_PROGRESS, SELF_CHECK_RESPONSE_SCHEMA
from do_math.observations import ObservationTracker
from support.fakes.clock import FakeClock
from support.observation_inputs import observation_rule, observe, self_check_response, write_checkpoint


class SelfCheckProgressContractTests(unittest.TestCase):
    def test_schema_and_counter_share_the_complete_progress_population(self):
        self.assertEqual(set(SELF_CHECK_RESPONSE_SCHEMA['properties']['progress']['enum']), set(SELF_CHECK_PROGRESS))
        for progress, rule in SELF_CHECK_PROGRESS.items():
            for status in SELF_CHECK_RESPONSE_SCHEMA['properties']['rule_results']['items']['properties']['status']['enum']:
                with self.subTest(progress=progress, rule_status=status), tempfile.TemporaryDirectory() as directory:
                    workspace = Path(directory)
                    tracker = ObservationTracker('EX-progress', workspace, {'observation_rules': [
                        observation_rule(threshold=1, repeat_interval=1)], 'no_progress_limit': 2}, time_port=FakeClock())
                    write_checkpoint(workspace, counters={'attempts': 1})
                    first = next(row for row in observe(tracker, {'type': 'tick'}) if row['kind'] == 'self_check_due')
                    answer = {**self_check_response(first), 'progress': 'no_progress'}
                    accepted = tracker.record_self_check_response(answer, available_evidence_refs={'EV-1'})
                    self.assertEqual((accepted['kind'], accepted['no_progress_count']), ('self_check_received', 1))
                    write_checkpoint(workspace, counters={'attempts': 2})
                    second = next(row for row in observe(tracker, {'type': 'tick'}) if row['kind'] == 'self_check_due')
                    rejected = tracker.record_self_check_response({**self_check_response(second), 'execution_id': 'EX-other'},
                        available_evidence_refs={'EV-1'})
                    self.assertEqual(rejected['kind'], 'self_check_rejected')
                    self.assertIn('execution_mismatch', rejected['errors'])
                    self.assertEqual(tracker.no_progress_count, 1)
                    response = {**self_check_response(second, status, [] if status == 'indeterminate' else None),
                                'progress': progress}
                    received = tracker.record_self_check_response(response, available_evidence_refs={'EV-1'})
                    expected = {'reset': 0, 'increment': 2, 'retain': 1}[rule['counter']]
                    self.assertEqual((received['kind'], received['no_progress_count']), ('self_check_received', expected))
                    trigger = ('self_check_defect' if status == 'defect' else 'self_check_indeterminate'
                               if status == 'indeterminate' else rule['trigger'] if rule['trigger'] is not None
                               else 'repeated_no_progress' if expected >= 2 else None)
                    self.assertEqual(received['followup'], {'kind': 'continue', 'next_owner': 'engine'} if trigger is None else {
                        'kind': 'operational_review_due', 'next_owner': 'operational_review', 'trigger': trigger,
                        'basis_refs': [second['id'], received['id']]})
                    repeated = tracker.record_self_check_response(response, available_evidence_refs={'EV-1'})
                    self.assertEqual(repeated['kind'], 'self_check_rejected')
                    self.assertEqual(tracker.no_progress_count, expected)
                    if trigger is not None:
                        tracker.acknowledge_review(observation_refs=[received['id']])
                        self.assertEqual(tracker.no_progress_count, 0)

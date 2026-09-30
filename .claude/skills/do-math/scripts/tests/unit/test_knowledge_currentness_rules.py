"""Currentness rules that need no engine: live counter rules (``observations``) and changed operational premises
(``operational_dispositions``), layers 1 and 2.
"""
from pathlib import Path
import tempfile
import unittest

from do_math.observations import ObservationTracker, validate_rules
from do_math.operational_dispositions import basis_premise_changes
from research_fixtures import observe, write_checkpoint


class LiveRuleTests(unittest.TestCase):
    def test_live_rules_repeat_exact_thresholds_and_preserve_last_valid_update(self):
        folder = Path(self.enterContext(tempfile.TemporaryDirectory())) / 'observed'
        folder.mkdir()
        clock = [0]
        rules = [{'id': 'steps', 'operator': 'counter_gte', 'subject': {'kind': 'counter', 'id': 'attempts'},
                  'basis': {'source': 'checkpoint', 'unit': 'count'}, 'threshold': 2,
                  'repeat_interval': 2, 'required_evidence': ['EV-iteration']}]
        tracker = ObservationTracker('EX', folder, {
            'observation_rules': rules, 'self_check_response_window_seconds': 60}, clock=lambda: clock[0])
        write_checkpoint(folder, counters={'attempts': 2})
        first = next(row for row in observe(tracker, {'type': 'tick'}) if row['kind'] == 'self_check_due')
        self.assertEqual(first['due'][0]['boundary'], 2)
        write_checkpoint(folder, counters={'attempts': 2}, claim='same count')
        self.assertFalse(any(row['kind'] == 'self_check_due' for row in observe(tracker, {'type': 'tick'})))
        write_checkpoint(folder, counters={'attempts': 4})
        events = observe(tracker, {'type': 'tick'})
        second = next(row for row in events if row['kind'] == 'self_check_due')
        self.assertEqual(second['due'][0]['boundary'], 4)
        self.assertEqual(tracker.rules, rules)
        with self.assertRaisesRegex(ValueError, '^rule threshold must be a positive integer$'):
            validate_rules([{**rules[0], 'threshold': True}])


class OperationalBasisPremiseTests(unittest.TestCase):
    def test_only_evidence_admitted_at_input_can_become_a_changed_premise(self):
        at_input, current = ['EX-target', 'BA-old'], ['EX-target', 'BA-new']
        changed = basis_premise_changes({'basis_refs': ['EX-target', 'BA-old']}, at_input, current)
        self.assertEqual([row['id'] for row in changed], ['BA-old'])
        self.assertEqual(basis_premise_changes({'basis_refs': ['BA-old', 'OF-never-supplied']}, at_input, current), [],
                         'A citation outside the input stays a producer error')
        self.assertEqual(basis_premise_changes({'basis_refs': ['EX-target']}, at_input, current), [])


if __name__ == '__main__':
    unittest.main()

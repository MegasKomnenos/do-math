"""과거 gap 입력을 현행 관찰 정본으로 확인한다. 도달 측정은 별도다."""
from copy import deepcopy
import hashlib
from pathlib import Path
import re
import tempfile
import unittest

from do_math import observations as rules
from do_math.execution_profiles import OBSERVATION_MODES
from support.fakes.clock import FakeClock
from support.observation_inputs import observation_rule, write_checkpoint


class ObservationGapTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.clock = FakeClock()

    def tracker(self, **config):
        return rules.ObservationTracker('EX-gap', self.root, {'research_self_checks': False, **config}, time_port=self.clock)

    def test_rule_proposal_and_each_signal_binding_reject_only_invalid_coordinates(self):
        proposal = {'current_revision': 0, 'reason': '재평가', 'rules': [observation_rule()]}
        self.assertEqual(rules.validate_rule_proposal(proposal, current_revision=0), proposal['rules'])
        for value, reason in ((None, 'rule proposal requires current_revision, reason and rules'),
                              ({**proposal, 'reason': ' '}, 'rule proposal needs a reason')):
            with self.assertRaisesRegex(ValueError, '^' + reason + '$'):
                rules.validate_rule_proposal(value, current_revision=0)
        bindings = rules.observation_rule_contract()
        self.assertEqual(rules.validate_observation_rule_contract(bindings), bindings)
        for value, reason in ((None, 'profile observation rule contract must be a list'),
            ([None], 'invalid profile observation binding'),
            ([{**bindings[0], 'source': 'outside'}], 'profile observation contract has no implemented producer for its signal kind'),
            ([bindings[0], bindings[0]], 'profile observation contract repeats a signal kind')):
            with self.assertRaisesRegex(ValueError, '^' + reason + '$'):
                rules.validate_observation_rule_contract(value)
        for binding in bindings:
            with self.subTest(operator=binding['operator']):
                seed = observation_rule(operator=binding['operator'], subject_kind=binding['subject_kind'],
                    subject_id='EX-gap', threshold=self.clock.now() if binding['operator'] == 'wall_time_reached' else 1)
                self.assertEqual(rules.validate_execution_rules([seed], bindings=bindings, execution_id='EX-gap'), [seed])
                other = [row for row in bindings if row != binding]
                with self.assertRaisesRegex(ValueError, '^rule has no registered observable subject/source/unit: R-1$'):
                    rules.validate_execution_rules([seed], bindings=other, execution_id='EX-gap')

    def test_rule_field_errors_preserve_the_input_and_normal_rule(self):
        seed = observation_rule()
        cases = [(None, 'invalid observation rule fields'),
            ({**seed, 'id': ''}, 'observation rule IDs must be distinct and nonempty'),
            ({**seed, 'subject': {}}, 'rule subject must contain exactly kind and id'),
            ({**seed, 'subject': {'kind': 'outside', 'id': 'x'}}, 'rule subject is incompatible with its operator'),
            ({**seed, 'required_evidence': ['EV-1', 'EV-1']}, 'rule required_evidence must be a nonempty unique string list')]
        wall = observation_rule(operator='wall_time_reached', subject_kind=rules.OPERATORS['wall_time_reached']['subject_kind'],
            threshold=self.clock.now(), repeat_interval=1)
        cases.append((wall, 'wall_time_reached cannot repeat'))
        for bad, reason in cases:
            before = deepcopy(bad)
            with self.subTest(reason=reason):
                with self.assertRaisesRegex(ValueError, '^' + reason + '$'):
                    rules.validate_rules([bad])
                self.assertEqual(bad, before)
        self.assertEqual(rules.validate_rules([seed]), [seed])

    def test_tracker_configuration_errors_are_distinct_from_valid_modes(self):
        for mode in OBSERVATION_MODES:
            self.assertEqual(self.tracker(observation_mode=mode, research_self_checks=False).mode, mode)
        for changes, reason in (({'observation_mode': 'outside'}, 'unsupported observation mode'),
            ({'self_check_revision': -1}, 'self_check_revision must be a nonnegative integer'),
            ({'observation_mode': 'deadline_only', 'research_self_checks': True}, 'deadline_only cannot carry research self-check rules'),
            ({'no_progress_limit': 0}, 'no_progress_limit must be a positive contract integer')):
            with self.assertRaisesRegex(ValueError, '^' + reason + '$'):
                self.tracker(**changes)

    def test_artifact_hash_and_scheduling_guards_preserve_the_normal_state(self):
        raw = b'checkpoint'
        value = {'kind': 'checkpoint', 'raw': raw, 'sha256': hashlib.sha256(raw).hexdigest()}
        self.assertEqual(rules.persistent_record(value, artifact_ref='artifact:one'),
            {'kind': 'checkpoint', 'sha256': value['sha256'], 'artifact_ref': 'artifact:one'})
        with self.assertRaisesRegex(ValueError, '^observation artifact hash differs from raw bytes$'):
            rules.persistent_record({**value, 'raw': b'changed'}, artifact_ref='artifact:one')
        tracker = self.tracker(observation_mode='periodic', research_self_checks=False)
        args = {'at': self.clock.now(), 'reason': '검토', 'basis_ref': 'D-one'}
        tracker.schedule_review('R-one', **args)
        before = deepcopy(tracker.explicit_reviews)
        for identifier, options, reason in (('', args, 'explicit review requires ID, reason and accepted disposition reference'),
            ('R-one', {**args, 'reason': '다른 이유'}, 'review ID cannot be reused with a different schedule'),
            ('R-two', {**args, 'at': 'invalid'}, 'review at must be an ISO timestamp with a timezone')):
            with self.assertRaisesRegex(ValueError, '^' + reason + '$'):
                tracker.schedule_review(identifier, **options)
            self.assertEqual(tracker.explicit_reviews, before)
        with self.assertRaisesRegex(ValueError, '^review acknowledgement needs published observation references$'):
            tracker.acknowledge_review(observation_refs=[])
        with self.assertRaisesRegex(ValueError, '^safe boundary needs a control receipt$'):
            tracker.record_safe_boundary('')
        with self.assertRaisesRegex(ValueError, '^self-check checkpoint requires its actual SHA-256$'):
            tracker.register_self_check_checkpoint('bad')

    def test_checkpoint_counter_shape_and_decrease_emit_exact_rejections(self):
        tracker = self.tracker(research_self_checks=True, observation_rules=[observation_rule()], observation_interval_seconds=300)
        source = {'stream': 'stdout.jsonl', 'start_offset': 0, 'end_offset': 0,
                  'received_at': self.clock.now(), 'received_monotonic': self.clock.monotonic()}
        for counters, reason in (([], 'checkpoint counters must be an object'),
            ({'attempts': -1}, 'checkpoint counters requires nonnegative integer values')):
            # 이 입력들은 checkpoint 스키마가 먼저 거부한다. 직접 1층 규칙의 좌표를 검사한다.
            state = {}
            with self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                tracker._merge_monotonic(state, counters, 'checkpoint counters')
            self.assertEqual(state, {})
        write_checkpoint(self.root, counters={'attempts': 1})
        tracker.observe({'type': 'tick'}, source=source)
        write_checkpoint(self.root, counters={'attempts': 0})
        rows = tracker.observe({'type': 'tick'}, source=source)
        self.assertEqual([row['reason'] for row in rows if row['kind'] == 'checkpoint_observation_rejected'],
                         ['checkpoint counters cannot decrease'])
        self.assertEqual(tracker.counters, {'attempts': 1})

    def test_background_lifecycle_and_safe_boundary_operator_have_actual_outputs(self):
        tracker = self.tracker(research_self_checks=False)
        source = {'stream': 'stdout.jsonl', 'start_offset': 0, 'end_offset': 1,
                  'received_at': self.clock.now(), 'received_monotonic': self.clock.monotonic()}
        tracker.observe({'type': 'system', 'subtype': 'task_started', 'task_id': 'B',
            'task_type': 'shell', 'is_backgrounded': True}, source=source, evaluate=False)
        self.assertEqual(set(tracker.pending_tools), {'background:B'})
        tracker.observe({'type': 'system', 'subtype': 'task_notification', 'task_id': 'B'}, source=source, evaluate=False)
        self.assertEqual(tracker.pending_tools, {})
        self.assertEqual(tracker.completed_call_ids, {'background:B'})
        operator = next(name for name, spec in rules.OPERATORS.items() if spec['subject_kind'] == 'safe_boundary')
        rule = observation_rule(operator=operator, subject_kind=rules.OPERATORS[operator]['subject_kind'], subject_id='CT-one', threshold=1)
        self.assertEqual(rules.evaluate_rules([rule], {'safe_boundary_ids': []}), [])
        result = rules.evaluate_rules([rule], {'safe_boundary_ids': ['CT-one']})
        self.assertEqual([(row['rule_id'], row['value'], row['boundary']) for row in result], [('R-1', 1, 1)])
        self.assertEqual(rules.evaluate_rules([rule], {'safe_boundary_ids': ['CT-one']},
            consumed_boundaries={result[0]['boundary_key']: 1}), [])

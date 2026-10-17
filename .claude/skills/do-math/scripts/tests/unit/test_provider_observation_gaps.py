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


class ControlObservationBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.clock = FakeClock()
        self.tracker = rules.ObservationTracker('EX-control', self.root,
            {'observation_rules': [observation_rule(threshold=1, repeat_interval=1)],
             'self_check_response_window_seconds': 5}, time_port=self.clock)

    def emit(self, tool, arguments, call_id='call', **changes):
        from do_math.control_protocol import CONTROL_SERVER
        from support.observation_inputs import observe
        return observe(self.tracker, {'type': 'item.started', 'item': {'id': call_id,
            'type': 'mcp_tool_call', 'server': CONTROL_SERVER, 'tool': tool, 'arguments': arguments}, **changes}, evaluate=False)

    def due(self, count):
        from support.observation_inputs import observe
        write_checkpoint(self.root, counters={'attempts': count})
        return next(row for row in observe(self.tracker, {'type': 'tick'}) if row['kind'] == 'self_check_due')

    def test_control_receipts_are_control_only_for_the_exact_known_request(self):
        from do_math.control_protocol import RECEIPT_TOOL, SUBMIT_TOOL, SAFETY_BOUNDARY, SELF_CHECK_RESPONSE
        due = self.due(1)
        request = {'request_id': 'request-self', 'execution_id': 'EX-control', 'kind': SELF_CHECK_RESPONSE,
                   'payload': {'self_check_id': due['id'], 'response': {}}}
        self.tracker.bind_control_request(request, receipt_id='CT-self')
        self.emit(SUBMIT_TOOL, {'kind': SAFETY_BOUNDARY, 'request_id': 'request-boundary',
                              'payload': {'inflight_calls': False, 'call_ids': []}}, 'boundary')
        for identifier, request_id in [('self', 'request-self'), ('boundary-receipt', 'request-boundary'),
                                       ('unknown', 'request-unknown'), ('malformed', None)]:
            self.emit(RECEIPT_TOOL, {'request_id': request_id}, identifier)
        self.assertIn('self', self.tracker.self_check_call_ids)
        self.assertEqual(self.tracker.boundary_call_ids, {'boundary', 'boundary-receipt'})
        self.assertFalse({'unknown', 'malformed'} & self.tracker.self_check_call_ids)
        self.assertFalse({'unknown', 'malformed'} & self.tracker.boundary_call_ids)

    def test_submit_response_binds_only_an_issued_obligation(self):
        from do_math.control_protocol import SUBMIT_TOOL, SELF_CHECK_RESPONSE
        due = self.due(1)
        for payload in [None, {}, {'self_check_id': 'SC-unknown'}, {'self_check_id': due['id'], 'response': {}}]:
            self.emit(SUBMIT_TOOL, {'kind': SELF_CHECK_RESPONSE, 'request_id': 'response', 'payload': payload})
        self.assertEqual(self.tracker.control_calls['call']['obligation_id'], due['id'])
        self.assertEqual(len(self.tracker.control_calls), 1)
        original = deepcopy(self.tracker.control_requests)
        for changed, message in [({'execution_id': 'EX-other'}, "control request is not this execution's self-check response"),
                                 ({'payload': {}}, 'control request has no issued self-check obligation')]:
            request = {'execution_id': 'EX-control', 'request_id': 'response', 'kind': SELF_CHECK_RESPONSE,
                       'payload': {'self_check_id': due['id'], 'response': {}}, **changed}
            with self.assertRaises(ValueError) as caught:
                self.tracker.bind_control_request(request, receipt_id='CT-one')
            self.assertEqual(str(caught.exception), message)
            self.assertEqual(self.tracker.control_requests, original)

    def test_poll_reuse_cannot_switch_obligations_or_acknowledge_invalid_json(self):
        from do_math.control_protocol import SELF_CHECK_TOOL
        from support.observation_inputs import observe
        first = self.due(1)
        self.tracker.issue_self_check(first['id'])
        self.emit(SELF_CHECK_TOOL, {'self_check_id': first['id']}, 'poll')
        observe(self.tracker, {'type': 'item.completed', 'item': {'id': 'poll', 'type': 'mcp_tool_call',
            'server': 'execution_control', 'tool': SELF_CHECK_TOOL, 'arguments': {'self_check_id': first['id']},
            'status': 'completed', 'result': '{invalid json'}}, evaluate=False)
        self.assertNotIn('acknowledged_call_id', self.tracker.obligations[first['id']])
        second = self.due(2)
        rows = self.emit(SELF_CHECK_TOOL, {'self_check_id': second['id']}, 'poll')
        self.assertEqual([row['reason'] for row in rows if row['kind'] == 'observation_input_rejected'],
                         ['self-check poll ID reused for another obligation'])
        self.assertEqual(self.tracker.self_check_polls, {'poll': first['id']})

    def test_unknown_assistant_tool_shapes_do_not_become_control_calls(self):
        from support.observation_inputs import observe
        before = deepcopy(self.tracker.control_calls)
        for content in [None, [None, {}, {'type': 'tool_use', 'name': 1},
                {'type': 'tool_use', 'name': 'other__control_self_check', 'id': 'foreign', 'input': {}}]]:
            observe(self.tracker, {'type': 'assistant', 'message': {'content': content}}, evaluate=False)
        self.assertEqual(self.tracker.control_calls, before)
        self.assertEqual(self.tracker.self_check_call_ids, set())

    def test_duplicate_miss_emits_one_notice_for_the_original_obligation(self):
        from support.observation_inputs import observe, acknowledge
        due = self.due(1)
        acknowledge(self.tracker, due['id'])
        notices = []
        for cid in ['research-one', 'research-two']:
            notices.extend(observe(self.tracker, {'type': 'item.started', 'item': {'id': cid,
                'type': 'command_execution'}}, evaluate=False))
        misses = [row for row in notices if row['kind'] == 'self_check_missed']
        self.assertEqual(len(misses), 1)
        self.assertEqual(misses[0]['obligation_id'], due['id'])
        self.assertEqual(misses[0]['reason'], 'research_action_before_response')

    def test_duration_and_execution_bound_rule_rejections_keep_exact_reason(self):
        with self.assertRaisesRegex(ValueError, '^window must be a positive millisecond-exact duration$'):
            rules.duration_ms('not-a-number', 'window')
        foreign = observation_rule(operator='checkpoint_count_gte', subject_kind='checkpoint', subject_id='EX-other', threshold=1)
        with self.assertRaisesRegex(ValueError, '^rule subject belongs to a different execution$'):
            rules.ObservationTracker('EX-control', self.root, {'observation_rules': [foreign]}, time_port=self.clock)


    def test_malformed_control_calls_and_boundaries_are_not_counted_as_controls(self):
        from do_math.control_protocol import SUBMIT_TOOL, SAFETY_BOUNDARY
        for call_id, args in [(None, {}), ('bad-args', None),
                ('bad-boundary', {'kind': SAFETY_BOUNDARY, 'request_id': 'boundary', 'payload': {'inflight_calls': True}})]:
            self.emit(SUBMIT_TOOL, args, call_id)
        self.assertEqual(self.tracker.boundary_request_ids, set())
        self.assertEqual(self.tracker.boundary_call_ids, set())
        self.assertEqual(self.tracker.control_calls, {})

    def test_request_identity_cannot_be_rebound_to_another_receipt(self):
        from do_math.control_protocol import SELF_CHECK_RESPONSE
        due = self.due(1)
        request = {'request_id': 'self', 'execution_id': 'EX-control', 'kind': SELF_CHECK_RESPONSE,
                   'payload': {'self_check_id': due['id'], 'response': {}}}
        original = self.tracker.bind_control_request(request, receipt_id='CT-first')
        with self.assertRaisesRegex(ValueError, '^control request identity reused$'):
            self.tracker.bind_control_request(request, receipt_id='CT-second')
        self.assertEqual(self.tracker.control_requests['self'], {k: v for k, v in original.items() if k != 'call_ids'})

    def test_safe_boundary_marks_only_named_inflight_calls(self):
        from support.observation_inputs import observe
        for call_id in ['selected', 'other']:
            observe(self.tracker, {'type': 'item.started', 'item': {'id': call_id, 'type': 'command_execution'}}, evaluate=False)
        self.tracker.record_safe_boundary('CT-boundary', call_ids=['absent', 'selected'])
        self.assertTrue(self.tracker.pending_tools['selected']['safe_boundary'])
        self.assertFalse(self.tracker.pending_tools['other']['safe_boundary'])
        self.assertNotIn('absent', self.tracker.pending_tools)
        self.assertEqual(self.tracker.safe_boundary_ids, {'CT-boundary'})

    def test_response_without_current_evidence_is_rejected_and_can_be_resubmitted(self):
        from support.observation_inputs import self_check_response
        due = self.due(1)
        response = self_check_response(due)
        rejected = self.tracker.record_self_check_response(response)
        self.assertEqual((rejected['kind'], rejected['errors']),
                         ('self_check_rejected', ['evidence_currentness_unverified']))
        self.assertEqual(self.tracker.obligations[due['id']]['status'], 'open')
        accepted = self.tracker.record_self_check_response(response, available_evidence_refs={'EV-1'})
        self.assertEqual(accepted['kind'], 'self_check_received')
        self.assertEqual(self.tracker.obligations[due['id']]['status'], 'answered')

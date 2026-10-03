"""관찰 입구의 공급자×허용 mode×도착 순서를 실제 owner와 저장으로 검산한다."""
from copy import deepcopy
import json
import unittest

from do_math.claude_adapter import ADAPTERS
from do_math.control_protocol import SELF_CHECK_RESPONSE, SELF_CHECK_TOOL, self_check_request_id
from do_math.execution_profiles import OBSERVATION_MODES
from do_math import execution_lifecycle
from do_math.observations import ObservationTracker
from support.observation_inputs import observation_rule, self_check_response, write_checkpoint
from support.provider_close_inputs import control_event
from support.provider_live import batch, running_execution
from support.sim import Sim, warm_template

setUpModule = warm_template


class ObservationIngressTests(unittest.TestCase):
    def scene(self, mode, *, checks=False):
        sim = Sim.activated()
        eid = 'EX-ingress'
        workspace = running_execution(sim, eid, 'research_work', bind=checks)
        tracker = ObservationTracker(eid, workspace, {'observation_mode': mode,
            'research_self_checks': checks, 'observation_interval_seconds': 300,
            'observation_rules': [observation_rule()] if checks else [],
            'self_check_response_window_seconds': 5}, time_port=sim.clock)
        return sim, eid, workspace, tracker

    def send(self, sim, eid, tracker, stream, events, *, terminated=False):
        start = stream.stat().st_size if stream.exists() else 0
        incoming = batch(sim, events, stream, start=start, terminated=terminated)
        with stream.open('ab') as output:
            output.write(b''.join(incoming.rows))
        sim.engine._observe_running(eid, tracker, incoming)
        return incoming

    def test_control_binding_both_orders_and_same_identity_redelivery_for_every_provider_and_mode(self):
        for mode in sorted(set(OBSERVATION_MODES) - {'deadline_only'}):
            for provider in ADAPTERS:
                for first in ('receipt', 'event'):
                    with self.subTest(mode=mode, provider=provider, first=first):
                        sim, eid, workspace, tracker = self.scene(mode, checks=True)
                        stream = workspace / 'stdout.jsonl'
                        write_checkpoint(workspace, counters={'attempts': 2})
                        self.send(sim, eid, tracker, stream, [])
                        (oid,) = tracker.obligations
                        self.assertEqual(sim.runtime['self_check_obligations'][oid], tracker.stored_obligations()[oid])
                        response = self_check_response(tracker.obligations[oid])
                        request = {'kind': SELF_CHECK_RESPONSE, 'execution_id': eid, 'request_id': self_check_request_id(oid),
                            'payload': {'self_check_id': oid, 'response': response}}
                        event = control_event(provider, 'CALL', SELF_CHECK_TOOL, request['payload'])
                        if first == 'receipt':
                            tracker.bind_control_request(request, receipt_id='CT-normal')
                        self.send(sim, eid, tracker, stream, [event])
                        if first == 'event':
                            tracker.bind_control_request(request, receipt_id='CT-normal')
                        before = deepcopy((tracker.control_calls, tracker.control_requests))
                        tracker.bind_control_request(deepcopy(request), receipt_id='CT-normal')
                        self.send(sim, eid, tracker, stream, [deepcopy(event)])
                        self.assertEqual((tracker.control_calls, tracker.control_requests), before)
                        self.assertEqual(tracker.self_check_call_ids, {'CALL'})
                        receipt = tracker.record_self_check_response(response, available_evidence_refs={'EV-1'}, receipt_id='CT-normal')
                        self.assertEqual(receipt['kind'], 'self_check_received')
                        self.send(sim, eid, tracker, stream, [])
                        self.assertEqual(sim.runtime['self_check_obligations'][oid]['status'], 'answered')
                        self.assertEqual(sim.engine.store.load(sim.engine.head)[2], sim.runtime)

    def test_conflicting_control_event_is_rejected_once_then_next_event_is_stored(self):
        for mode in sorted(set(OBSERVATION_MODES) - {'deadline_only'}):
            for provider in ADAPTERS:
                for first in ('receipt', 'event'):
                    with self.subTest(mode=mode, provider=provider, first=first):
                        sim, eid, workspace, tracker = self.scene(mode, checks=True)
                        stream = workspace / 'stdout.jsonl'
                        write_checkpoint(workspace, counters={'attempts': 2})
                        self.send(sim, eid, tracker, stream, [])
                        (oid,) = tracker.obligations
                        response = self_check_response(tracker.obligations[oid])
                        request = {'kind': SELF_CHECK_RESPONSE, 'execution_id': eid, 'request_id': self_check_request_id(oid),
                            'payload': {'self_check_id': oid, 'response': response}}
                        event = control_event(provider, 'CALL', SELF_CHECK_TOOL, request['payload'])
                        if first == 'receipt':
                            tracker.bind_control_request(request, receipt_id='CT-normal')
                        else:
                            self.send(sim, eid, tracker, stream, [event])
                        changed = deepcopy(request['payload'])
                        changed['response']['next_method'] = '다른 응답'
                        bad = control_event(provider, 'CALL', SELF_CHECK_TOOL, changed)
                        good = {'type': 'turn.started', 'execution_id': eid}
                        before = set(sim.runtime['observation_facts'])
                        incoming = self.send(sim, eid, tracker, stream, [bad, good], terminated=True)
                        added = [json.loads(value['event_json']) for key, value in sim.runtime['observation_facts'].items() if key not in before]
                        reason = ('observed control arguments differ from received request' if first == 'receipt'
                                  else 'control call ID reused with different request')
                        self.assertEqual([row['reason'] for row in added if row.get('kind') == 'observation_input_rejected'], [reason])
                        self.assertEqual([row for row in added if 'type' in row], [bad, good])
                        state, head = deepcopy(sim.runtime), sim.engine.head
                        sim.advance(1)
                        self.send(sim, eid, tracker, stream, [], terminated=True)
                        self.assertEqual(sim.runtime, state)
                        self.assertEqual(sim.engine.head, head)
                        self.assertEqual(sim.runtime['executions'][eid]['observation_stream']['end_offset'], incoming.end_offset)
                        self.assertEqual(sim.engine.store.load(head)[2], state)

    def test_live_rejection_enqueues_only_the_modes_that_own_review(self):
        for mode in OBSERVATION_MODES:
            with self.subTest(mode=mode):
                sim, eid, workspace, tracker = self.scene(mode)
                before = {row['id'] for row in sim.runtime['queue']}
                self.send(sim, eid, tracker, workspace / 'stdout.jsonl',
                    [{'type': 'turn.started', 'execution_id': 'EX-foreign'}, {'type': 'turn.started', 'execution_id': eid}])
                added = [row for row in sim.runtime['queue'] if row['id'] not in before]
                self.assertEqual([row['role'] for row in added], [] if mode == 'deadline_only' else ['operational_review'])
                facts = [json.loads(row['event_json']) for row in sim.runtime['observation_facts'].values() if row['execution_id'] == eid]
                self.assertEqual(len(facts), 3)
                self.assertEqual([row['execution_id'] for row in facts if row.get('kind') == 'observation_input_rejected'], [eid])
                self.assertEqual(sim.engine.store.load(sim.engine.head)[2], sim.runtime)

    def test_ended_execution_preserves_late_facts_and_another_running_execution_progresses(self):
        for mode in OBSERVATION_MODES:
            with self.subTest(mode=mode):
                sim, eid, workspace, tracker = self.scene(mode)
                before_settlement = deepcopy(sim.runtime)
                self.assertFalse(sim.engine._settle_recovered_execution(eid, at=sim.clock.now()))
                self.assertEqual(sim.runtime, before_settlement)
                execution_lifecycle.end_recovered(sim.runtime['executions'][eid], at=sim.clock.now(),
                    outcome='execution_incomplete', disposition={'kind': 'local_termination_confirmed'})
                sim.engine._save()
                tracker.set_execution_status('ended')
                other_workspace = running_execution(sim, 'EX-other', 'research_work')
                other = ObservationTracker('EX-other', other_workspace,
                    {'observation_mode': mode, 'research_self_checks': False}, time_port=sim.clock)
                queue = deepcopy(sim.runtime['queue'])
                self.send(sim, eid, tracker, workspace / 'stdout.jsonl', [{'type': 'turn.started'}], terminated=True)
                self.send(sim, 'EX-other', other, other_workspace / 'stdout.jsonl', [{'type': 'turn.started'}])
                self.assertEqual(sim.runtime['executions'][eid]['status'], 'ended')
                self.assertEqual(sim.runtime['executions']['EX-other']['status'], 'running')
                self.assertEqual(sim.runtime['queue'], queue)
                self.assertEqual([row['execution_id'] for row in sim.runtime['observation_facts'].values()
                    if row['execution_id'] in {eid, 'EX-other'}], [eid, 'EX-other'])
                self.assertEqual(sim.engine.store.load(sim.engine.head)[2], sim.runtime)

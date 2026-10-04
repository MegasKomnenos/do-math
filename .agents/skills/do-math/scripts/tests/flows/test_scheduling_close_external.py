"""8-B의 동기 HTTP 정산: future 대신 외부 효과 장부와 기계 영수증을 검사한다."""
from copy import deepcopy
import hashlib
import unittest

from support.engine_lifecycle import applied, clear_work, external_sim, http_grant, warm_external
from support.scheduling_return_observer import OwnerProbe


setUpModule = warm_external


class ExternalReturnTests(unittest.TestCase):
    def test_step_cap_and_pause_during_transport_preserve_the_confirmed_effect_once(self):
        for pause_during in (False, True):
            with self.subTest(pause_during=pause_during):
                sim = external_sim()
                config = http_grant(sim.engine)
                sim.engine._save()
                clear_work(sim)
                applied(sim, 'external', config=config)
                sim.ports.http.table['/effect'] = (201, b'created', None)
                before = set(sim.runtime['executions'])
                request = sim.ports.http.request
                arrivals = []
                probe = OwnerProbe(sim)

                def transport(operation, headers, timeout):
                    if pause_during:
                        arrivals.append((probe.passes, sim.control('pause', text='HTTP 응답 중 공개 정지')))
                    return request(operation, headers, timeout)

                sim.ports.http.request = transport
                with probe:
                    answer = sim.engine.run(max_steps=1)
                self.assertEqual(probe.failures, [])
                self.assertGreater(probe.passes, 0)
                added = set(sim.runtime['executions']) - before
                self.assertEqual(len(added), 1)
                eid, = added
                _, _, stored = sim.engine.store.load(sim.engine.head)
                row = stored['executions'][eid]
                operation = stored['external_operations']['OP-audit']
                self.assertEqual(operation, sim.runtime['external_operations']['OP-audit'])
                self.assertEqual(operation['status'], 'confirmed', operation)
                self.assertEqual((operation['status'], operation['succeeded'], operation['transmitted']),
                                 ('confirmed', True, True))
                self.assertEqual(operation['body_sha256'], hashlib.sha256(b'created').hexdigest())
                self.assertEqual(row['role'], 'external_action')
                self.assertEqual(row['status'], 'ended')
                self.assertEqual(row['capacity']['local_termination'], 'confirmed')
                self.assertEqual(row['outcome'], 'output_accepted')
                self.assertEqual(row['submission_receipt']['evidence_ref'], operation['id'])
                self.assertEqual(row['submission_receipt']['state'], 'accepted')
                self.assertEqual(stored['activities'][row['owner_activity_id']]['status'], 'finished')
                for rid in row['capacity']['reservation_ids']:
                    reservation = stored['reservations'][rid]
                    self.assertEqual((reservation['state'], reservation['returned'], reservation['confirmed_consumed']),
                                     ('settled', reservation['reserved'], 0))
                    self.assertTrue(reservation['evidence_refs'])
                self.assertEqual(len(sim.ports.http.requests), 1)
                if pause_during:
                    self.assertEqual(len(arrivals), 1)
                    self.assertEqual(answer['status'], 'paused')
                    at, envelope = arrivals[0]
                    consumed_at = next(turn for turn, ids in probe.control_passes if envelope['request_id'] in ids)
                    self.assertLessEqual(consumed_at - at, 1)
                before_reservations = deepcopy(stored['reservations'])
                sim.engine.run(max_steps=1, until_active=True)
                self.assertEqual(sim.runtime['external_operations']['OP-audit'], operation)
                self.assertEqual(sim.runtime['reservations'], before_reservations)
                self.assertEqual(len(sim.ports.http.requests), 1)
                self.assertEqual(set(sim.runtime['executions']) - before, added)

    def test_preexisting_pause_does_not_send_or_create_an_execution(self):
        sim = external_sim()
        config = http_grant(sim.engine)
        sim.engine._save()
        applied(sim, 'external', config=config)
        applied(sim, 'pause', text='외부 작업 배정 전 정지')
        before = deepcopy(sim.runtime['executions'])
        operation = deepcopy(sim.runtime['external_operations']['OP-audit'])
        answer = sim.engine.run(max_steps=1)
        self.assertEqual(answer['status'], 'paused')
        self.assertEqual(sim.ports.http.requests, [])
        self.assertEqual(sim.runtime['executions'], before)
        self.assertEqual(sim.runtime['external_operations']['OP-audit'], operation)


class ExternalEventPlanningTests(unittest.TestCase):
    def prepare(self, *, expires_after=None, credentials=False):
        from support.default_responder import DefaultResponder
        from support.model import amend
        sim = external_sim()
        from datetime import timedelta
        scope = None if expires_after is None else {'expires_at': (sim.clock.wall() + timedelta(seconds=expires_after)).isoformat()}
        config = http_grant(sim.engine, scope=scope, credentials=credentials)
        sim.engine._save()
        clear_work(sim)
        sim.model.responder = DefaultResponder(preparation_candidates=[], plan_assessments=False)
        sim.model.on('research_plan').reply(amend(goal_audit=False))
        applied(sim, 'external', config=config)
        return sim, config

    def assert_events_planned_once(self, sim, events):
        from support.cross_contracts import assert_call_records
        identifiers = {event['id'] for event in events}
        self.assertTrue(identifiers)
        def consumed(current):
            seen = {ref for call in current.model.calls if call['role'] == 'research_plan'
                    for ref in call['action'].get('event_refs', [])}
            return identifiers <= seen
        sim.advance(sim.instance['config']['plan_settle_seconds'] + 1)
        sim.run_until(consumed, max_steps=12)
        for identifier in identifiers:
            execution, = [e for e in sim.runtime['executions'].values()
                          if identifier in e['action'].get('event_refs', [])]
            self.assertEqual(execution['outcome'], 'output_accepted', execution.get('error'))
            self.assertNotIn(identifier, sim.runtime['pending_events'])
        for _ in range(2):
            sim.step()
            assert_call_records(self, sim)
            for identifier in identifiers:
                self.assertEqual(sum(identifier in call['action'].get('event_refs', [])
                                     for call in sim.model.calls), 1)

    def test_uncertainty_reconciliation_and_authorized_retry_preserve_each_planning_cause(self):
        from support.engine_lifecycle import run_machine
        sim, config = self.prepare()
        sim.ports.http.table['/effect'] = (503, b'unknown outcome', None)
        backend = sim.ports.git_backend
        publish = backend.update_ref
        def lose_owner_after_result(*args, **kwargs):
            published = publish(*args, **kwargs)
            current = sim.runtime['external_operations'][config['id']]
            if published and current['status'] == 'unknown':
                raise SystemExit('owner lost after the effect result was stored')
            return published
        backend.update_ref = lose_owner_after_result
        try:
            with self.assertRaisesRegex(SystemExit, '^owner lost after the effect result was stored$'):
                run_machine(sim, 'external_action')
        finally:
            backend.update_ref = publish
        sim.restart()
        sim.step()
        operation = sim.runtime['external_operations'][config['id']]
        self.assertEqual(operation['status'], 'unknown')
        self.assertTrue(any(e['kind'] == 'external_reconciliation_required' for e in sim.runtime['events']))
        self.assertEqual(len(sim.ports.http.requests), 1)
        operation = sim.runtime['external_operations'][config['id']]
        applied(sim, 'external', config={'operation': 'reconcile', 'id': operation['id'], 'result': 'failed',
            'evidence': {'evidence_ref': 'remote-effect-log', 'operation_id': operation['id'],
                'request_sha256': operation['request_sha256'], 'idempotency_key': operation['idempotency_key'],
                'fact': 'effect_absent', 'observed_at': sim.clock.now()}})
        applied(sim, 'external', config={'operation': 'retry', 'id': operation['id'], 'grant_id': config['grant_id']})
        sim.ports.http.table['/effect'] = (201, b'confirmed', None)
        run_machine(sim, 'external_action')
        events = [e for e in sim.runtime['events'] if e.get('target') == config['id']]
        self.assertEqual({e['kind'] for e in events}, {'external_operation_prepared',
            'external_reconciliation_required', 'external_operation_reconciled',
            'external_operation_retry_prepared', 'external_operation_confirmed'})
        self.assert_events_planned_once(sim, events)
        before = deepcopy(sim.runtime['events'])
        applied(sim, 'external', config=config)
        self.assertEqual(sim.runtime['events'], before)
        self.assertEqual(len(sim.ports.http.requests), 2)
        self.assertEqual(sim.runtime['external_operations'][config['id']]['status'], 'confirmed')

    def test_effect_result_kinds_deliver_one_plan_after_their_actual_outcome(self):
        """The failed case supplies explicit absence evidence at the HTTP port; a non-2xx status alone stays unknown."""
        from support.cross_contracts import assert_call_records
        from support.engine_lifecycle import control_at_inbox_check, run_machine
        for outcome in ('confirmed', 'unknown', 'failed', 'cancelled', 'prepared'):
            with self.subTest(outcome=outcome):
                sim, config = self.prepare(credentials=outcome == 'prepared')
                from support.engine_lifecycle import CREDENTIAL
                sim.environment.pop(CREDENTIAL, None)
                sim.ports.http.table['/effect'] = (201 if outcome == 'confirmed' else 503, b'effect response', None)
                if outcome == 'failed':
                    request = sim.ports.http.request
                    def absent(*args, **kwargs):
                        return {**request(*args, **kwargs), 'effect_absent': True}
                    sim.ports.http.request = absent
                if outcome == 'cancelled':
                    with control_at_inbox_check(sim, 1, 'pause'):
                        run_machine(sim, 'external_action')
                    self.assertEqual(assert_call_records(self, sim)['research_plan'], 0)
                    sim.step()
                    self.assertEqual(assert_call_records(self, sim)['research_plan'], 0)
                    applied(sim, 'resume', config={})
                else:
                    run_machine(sim, 'external_action')
                self.assertEqual(sim.runtime['external_operations'][config['id']]['status'], outcome)
                if outcome == 'unknown':
                    preserved_events = deepcopy(sim.runtime['events'])
                    rejected = sim.control('external', config={'operation': 'retry', 'id': config['id'],
                                                             'grant_id': config['grant_id']})
                    sim.engine.process_controls()
                    self.assertEqual(sim.engine.control_result(rejected['request_id'])['effect'], 'rejected')
                    self.assertEqual(sim.runtime['events'], preserved_events)
                events = [e for e in sim.runtime['events'] if e.get('target') == config['id']]
                self.assertEqual({e['kind'] for e in events}, {'external_operation_prepared', 'external_operation_' + outcome})
                self.assert_events_planned_once(sim, events)
                self.assertEqual(len(sim.ports.http.requests), int(outcome not in {'cancelled', 'prepared'}))

    def test_expired_external_authority_records_cancellation_and_one_plan_without_transport(self):
        sim, config = self.prepare(expires_after=1)
        action, = [a for a in sim.runtime['queue'] if a['role'] == 'external_action']
        sim.advance(2)
        # Inspect the operation's own final authority check after its queued grant expired.
        sim.engine._run_external_action(action)
        sim.engine._save()
        self.assertEqual(sim.runtime['external_operations'][config['id']]['status'], 'cancelled')
        self.assertEqual(sim.ports.http.requests, [])
        events = [e for e in sim.runtime['events'] if e.get('target') == config['id']]
        self.assertEqual({e['kind'] for e in events}, {'external_operation_prepared', 'external_operation_not_authorized'})
        self.assert_events_planned_once(sim, events)
        self.assertEqual(sim.ports.http.requests, [])

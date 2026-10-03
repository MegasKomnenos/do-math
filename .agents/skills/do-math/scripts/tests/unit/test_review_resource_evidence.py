"""실제 입장 실패 생산자가 기록한 자원 처분의 고정 근거와 종료 순서."""
from copy import deepcopy

from do_math import execution_lifecycle as lifecycle, review_cycle as rc
from support.review_owner_inputs import ReviewOwnerCase
from support.review_inputs import scope_assessment
from support.review_scene import warm


def setUpModule():
    warm()


class ResourceEvidenceTests(ReviewOwnerCase):
    def resource(self, *, deferred=False, exhausted=False, held=False, prepared=False):
        engine = self.engine
        engine.instance['review_policy']['overflow_disposition'] = 'defer' if deferred else 'unresolved'
        engine.instance['review_policy']['activity_execution_limit'] = 11 if exhausted else 1
        if exhausted:
            cid = self.scene.start('K1', scope=scope_assessment(engine.instance['review_policy'], ['initial-0', 'initial-1']))
            action = deepcopy(self.scene.pending())
        else:
            cid, action = self.opened(scope=True)
        if prepared:
            self.assertEqual(engine._prepare_review_context(action, self.root / 'prepared')['disposition'], 'ready')
        if exhausted:
            # 생산 등록과 종료 전이를 반복하여 실제로 사용한 시도만 예산에 센다.
            for index in range(11):
                execution = engine._register_execution(action, {'id': f'EX-resource-{index}', 'role': 'identity_review', 'status': 'queued'})
                self.assertIsNotNone(execution)
                if held and index == 10:
                    self.assertTrue(engine._session_slots().acquire(execution['id'], profile=engine._execution_profile(action), execution=execution))
                    lifecycle.transition_execution(execution, 'stopping', at=engine.ports.clock.now())
                    lifecycle.transition_execution(execution, 'ended', at=engine.ports.clock.now(), outcome='cancelled')
                else:
                    lifecycle.end_preparation(execution, at=engine.ports.clock.now(), stage='context', reason='합성 중단', cancelled=True)
        self.assertIsNone(engine._register_execution(action, {'id': 'EX-denied', 'role': 'identity_review', 'status': 'queued'}))
        cycle = engine.runtime['review_cycles'][cid]
        record = rc.resource_disposition(cycle)
        self.assertEqual(record['reason'], 'review_budget_exhausted' if exhausted else 'review_scope_unaffordable')
        self.assertEqual(rc.validate_resource_disposition(cycle, engine.runtime), record)
        return cid, action, cycle, record

    def assert_invalid_record(self, field, value, reason):
        _, _, original, _ = self.resource()
        cycle = deepcopy(original)
        rc.resource_disposition(cycle)[field] = value
        before = deepcopy(cycle)
        with self.assertRaisesRegex(ValueError, reason):
            rc.validate_resource_disposition(cycle, self.engine.runtime)
        self.assertEqual(cycle, before)

    def test_duplicate_dispositions_are_rejected(self):
        _, _, original, record = self.resource()
        cycle = deepcopy(original)
        cycle['history'].append(deepcopy(record))
        with self.assertRaisesRegex(ValueError, 'review has duplicate resource dispositions'):
            rc.validate_resource_disposition(cycle, self.engine.runtime)
        self.assertEqual(len([r for r in cycle['history'] if r.get('event') == 'review_resource_disposition']), 2)

    def test_unknown_resource_state_is_rejected(self):
        self.assert_invalid_record('state', 'approved', 'unknown review resource disposition state')

    def test_ended_disposition_requires_unresolved_cycle(self):
        _, _, cycle, _ = self.resource()
        changed = {**cycle, 'decision': 'match'}
        with self.assertRaisesRegex(ValueError, 'ended resource disposition must preserve an unresolved review'):
            rc.validate_resource_disposition(changed, self.engine.runtime)
        self.assertEqual(cycle['decision'], 'unresolved')

    def test_resource_basis_fields_cannot_drift(self):
        _, _, cycle, record = self.resource()
        for field, value in [('proposal_digest', '0' * 64), ('policy', {}), ('limit', 2), ('disposition', 'defer')]:
            changed = deepcopy(cycle)
            rc.resource_disposition(changed)[field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'changed its fixed basis'):
                rc.validate_resource_disposition(changed, self.engine.runtime)
        self.assertEqual(rc.resource_disposition(cycle), record)

    def test_accounting_must_equal_actual_cycle_accounting(self):
        self.assert_invalid_record('executions_used', ['absent'], 'changed execution accounting')

    def test_unknown_reason_is_rejected(self):
        self.assert_invalid_record('reason', 'invented', 'unknown review resource disposition$')

    def test_exhaustion_reason_cannot_be_claimed_for_unspent_scope_budget(self):
        self.assert_invalid_record('reason', 'review_budget_exhausted', 'review execution limit is not exhausted')

    def test_owned_attempt_must_remain_ai_and_owned(self):
        _, _, cycle, record = self.resource(exhausted=True)
        eid = record['executions_used'][0]
        for field, value in [('actor_kind', 'machine'), ('owner_activity_id', 'other')]:
            runtime = deepcopy(self.engine.runtime)
            runtime['executions'][eid][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'lacks actual owned AI attempts'):
                rc.validate_resource_disposition(cycle, runtime)
        self.assertEqual(record['executions_used'], [f'EX-resource-{i}' for i in range(11)])

    def test_closure_cannot_precede_actual_attempt_end(self):
        _, _, cycle, record = self.resource(exhausted=True)
        runtime = deepcopy(self.engine.runtime)
        runtime['executions'][record['executions_used'][-1]]['status'] = 'running'
        with self.assertRaisesRegex(ValueError, 'review closed before its attempts ended'):
            rc.validate_resource_disposition(cycle, runtime)
        self.assertEqual(cycle['status'], 'unresolved')

    def test_resource_request_is_idempotent_and_removes_only_its_waits(self):
        cid, action, _, record = self.resource(deferred=True)
        engine = self.engine
        engine.runtime['waiting_actions'] = {
            'own': {'action': action}, 'peer': {'action': {**action, 'review_cycle_id': 'other'}}}
        peer = deepcopy(engine.runtime['waiting_actions']['peer'])
        before_queue = deepcopy(engine.runtime['queue'])
        engine._request_review_resource_disposition(action, record['reason'], record['detail'])
        self.assertEqual(engine.runtime['waiting_actions'], {'peer': peer})
        self.assertEqual(engine.runtime['queue'], before_queue)
        self.assertEqual(len([r for r in engine.runtime['review_cycles'][cid]['history'] if r.get('event') == 'review_resource_disposition']), 1)
        self.assertEqual(engine._admit_review_execution(action, {'id': 'extra', 'actor_kind': 'ai'}),
                         {'disposition': 'review_resource_pending', 'cycle_id': cid})
        self.assertEqual(engine._obsolete_review_reason(action), 'The review is preserving an incomplete resource disposition for planning')

    def test_deferred_review_closes_on_actual_proposal_supersession_once(self):
        cid, _, _, _ = self.resource(deferred=True)
        self.engine.instance['knowledge']['K1']['lifecycle'] = 'superseded'
        before_queue = deepcopy(self.engine.runtime['queue'])
        self.assertEqual(self.engine._settle_review_resource_dispositions(), [cid])
        cycle = self.engine.runtime['review_cycles'][cid]
        record = rc.resource_disposition(cycle)
        self.assertEqual((record['state'], cycle['status'], cycle['decision']), ('ended', 'unresolved', 'unresolved'))
        self.assertEqual(record['resolution']['kind'], 'proposal_superseded')
        self.assertEqual(self.engine.runtime['queue'], before_queue)
        self.assertEqual(self.engine._settle_review_resource_dispositions(), [])

    def test_ended_review_reserves_no_execution_slots(self):
        _, _, cycle, _ = self.resource()
        self.assertEqual(rc.reserved_review_slots(cycle, self.engine.runtime['executions']), [])
        self.assertEqual(rc._phase_actions(cycle), [])

    def test_resource_closure_waits_for_actual_capacity_reservation_release(self):
        cid, _, cycle, record = self.resource(exhausted=True, held=True)
        self.assertEqual(record['state'], 'draining')
        before = deepcopy(self.engine.runtime['activities'][cycle['owner_activity_id']])
        self.assertEqual(self.engine._settle_review_resource_dispositions(), [])
        self.assertEqual(self.engine.runtime['activities'][cycle['owner_activity_id']], before)
        self.assertTrue(self.engine._session_slots().release('EX-resource-10'))
        self.assertEqual(self.engine._settle_review_resource_dispositions(), [cid])
        self.assertEqual(rc.resource_disposition(self.engine.runtime['review_cycles'][cid])['state'], 'ended')

    def test_closed_instance_does_not_enqueue_a_new_plan_for_resource_disposition(self):
        self.engine.runtime['status'] = 'closed'
        _, _, cycle, record = self.resource()
        self.assertEqual(record['resolution']['kind'], 'instance_ended')
        self.assertEqual(cycle['status'], 'unresolved')
        self.assertEqual([a for a in self.engine.runtime['queue'] if a['role'] == 'research_plan'], [])

    def test_unfinished_resource_cannot_support_a_sealed_conclusion(self):
        _, _, cycle, _ = self.resource()
        changed = deepcopy(cycle)
        rc.resource_disposition(changed)['state'] = 'draining'
        with self.assertRaisesRegex(ValueError, 'review resource disposition has not ended'):
            rc.validate_sealed_review(changed, self.engine.runtime, clock=self.engine.ports.clock, at=self.engine.ports.clock.now())
        self.assertEqual(rc.resource_disposition(cycle)['state'], 'ended')

    def test_resource_disposition_prevents_recording_prepared_input_as_delivered(self):
        _, action, _, _ = self.resource(exhausted=True, prepared=True)
        self.assert_engine_rejected('review input cannot start: review_resource_pending',
            lambda: self.engine._record_review_input(action, 'EX-resource-10'))

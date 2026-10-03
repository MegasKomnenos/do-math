"""실제 엔진·저장 관문 위에서 외부 제어의 거부와 재시도 정산을 검사한다."""
from copy import deepcopy
import unittest

from do_math.external import reconcile_operation
from support.engine_lifecycle import external_sim, http_grant, extended, run_machine
from support.academic_scenes import user_source


class AcademicExternalControlValidationTests(unittest.TestCase):
    def setUp(self):
        self.sim = external_sim()
        self.engine = self.sim.engine
        self.config = http_grant(self.engine)
        self.source = user_source(self.engine)

    def prepare(self):
        self.engine._external_control(self.config, self.source)
        self.engine._save()
        return self.engine.runtime['external_operations'][self.config['id']]

    def unknown(self):
        self.prepare()
        self.sim.ports.http.table['/effect'] = (503, b'uncertain', None)
        run_machine(self.sim, 'external_action')
        return self.engine.runtime['external_operations'][self.config['id']]

    def evidence(self, operation, fact):
        return {'operation_id': operation['id'], 'request_sha256': operation['request_sha256'],
                'idempotency_key': operation['idempotency_key'], 'fact': fact,
                'evidence_ref': 'remote:synthetic-receipt', 'observed_at': self.sim.clock.now()}

    def test_prepare_rejects_policy_that_disables_effects(self):
        self.engine.instance['lifecycle']['adoption']['external_policy'] = 'disabled'
        before = deepcopy(self.engine.runtime)
        with self.assertRaisesRegex(ValueError, '^external effects are disabled by the adopted policy$'):
            self.engine._external_control(self.config, self.source)
        self.assertEqual(self.engine.runtime, before)
        self.assertEqual(self.sim.ports.http.requests, [])

    def test_prepare_rejects_missing_or_non_http_grant(self):
        for grant_id in ('missing', self.engine.instance['lifecycle']['adoption']['research_grant_ids'][0]):
            with self.subTest(grant=grant_id):
                before = deepcopy(self.engine.runtime)
                with self.assertRaisesRegex(ValueError, '^HTTP operation requires an explicit HTTP grant$'):
                    self.engine._external_control({**self.config, 'grant_id': grant_id}, self.source)
                self.assertEqual(self.engine.runtime, before)
        self.assertEqual(self.sim.ports.http.requests, [])

    def test_prepare_rejects_actor_kind_different_from_actual_profile(self):
        before = deepcopy(self.engine.runtime)
        with self.assertRaisesRegex(ValueError, '^external request scope differs from the actual execution profile: actor_kind$'):
            self.engine._external_control({**self.config, 'actor_kind': 'ai'}, self.source)
        self.assertEqual(self.engine.runtime, before)
        self.assertEqual(self.sim.ports.http.requests, [])

    def test_prepare_replay_preserves_ledger_and_does_not_duplicate_action(self):
        operation = deepcopy(self.prepare())
        before = deepcopy(self.engine.runtime)
        self.engine._external_control(self.config, self.source)
        self.assertEqual(self.engine.runtime['external_operations'], before['external_operations'])
        # 개정 대상 없는 재요청은 병합 뒤에도 독립 요청임을 보존한다.
        expected_queue = deepcopy(before['queue'])
        for action in expected_queue:
            if action['role'] == 'external_action' and action.get('target') == operation['id']:
                action['unbound_request'] = True
        self.assertEqual(self.engine.runtime['queue'], expected_queue)
        self.assertEqual(self.engine.runtime['events'], before['events'])
        self.engine._save()
        self.assertEqual(self.engine.store.load()[2]['external_operations'][operation['id']], operation)

    def test_prepare_replay_rejects_changed_request_under_same_id(self):
        self.prepare()
        config = deepcopy(self.config)
        config['request']['body'] = '다른 본문'
        before = deepcopy(self.engine.runtime)
        with self.assertRaisesRegex(ValueError, '^external operation ID already identifies another ledger$'):
            self.engine._external_control(config, self.source)
        self.assertEqual(self.engine.runtime, before)
        self.assertEqual(self.sim.ports.http.requests, [])

    def test_prepare_replay_of_unknown_operation_does_not_requeue(self):
        operation = deepcopy(self.unknown())
        before = deepcopy(self.engine.runtime)
        self.engine._external_control(self.config, self.source)
        self.assertEqual(self.engine.runtime, before)
        self.assertEqual(self.engine.runtime['external_operations'][operation['id']], operation)
        self.assertEqual(len(self.sim.ports.http.requests), 1)

    def test_reconcile_rejects_missing_operation_without_side_effects(self):
        before = deepcopy(self.engine.runtime)
        with self.assertRaisesRegex(ValueError, '^external operation does not exist$'):
            self.engine._external_control({'operation': 'reconcile', 'id': 'missing'}, self.source)
        self.assertEqual(self.engine.runtime, before)
        self.assertEqual(self.sim.ports.http.requests, [])

    def test_unknown_control_operation_is_rejected(self):
        before = deepcopy(self.engine.runtime)
        with self.assertRaisesRegex(ValueError, '^external operation must be prepare, reconcile, or retry$'):
            self.engine._external_control({'operation': 'forget'}, self.source)
        self.assertEqual(self.engine.runtime, before)
        self.assertEqual(self.sim.ports.http.requests, [])

    def test_retry_rejects_missing_operation(self):
        before = deepcopy(self.engine.runtime)
        with self.assertRaisesRegex(ValueError, '^external operation does not exist$'):
            self.engine._external_control({'operation': 'retry', 'id': 'missing', 'grant_id': self.config['grant_id']}, self.source)
        self.assertEqual(self.engine.runtime, before)

    def test_retry_rejects_still_prepared_operation(self):
        self.prepare()
        before = deepcopy(self.engine.runtime)
        with self.assertRaisesRegex(ValueError, '^completed operation cannot be retried$'):
            self.engine._external_control({**self.config, 'operation': 'retry'}, self.source)
        self.assertEqual(self.engine.runtime, before)
        self.assertEqual(self.sim.ports.http.requests, [])

    def test_retry_requires_same_explicit_grant(self):
        self.unknown()
        for grant_id in (None, '', 'other', 1):
            with self.subTest(grant_id=grant_id):
                before = deepcopy(self.engine.runtime)
                with self.assertRaisesRegex(ValueError, "^retry requires the operation's explicit current grant$"):
                    self.engine._external_control({'operation': 'retry', 'id': self.config['id'], 'grant_id': grant_id}, self.source)
                self.assertEqual(self.engine.runtime, before)
        self.assertEqual(len(self.sim.ports.http.requests), 1)

    def test_retry_requires_existing_http_grant(self):
        self.unknown()
        self.engine.instance['grants'].pop(self.config['grant_id'])
        before = deepcopy(self.engine.runtime)
        with self.assertRaisesRegex(ValueError, '^retry requires an active HTTP grant$'):
            self.engine._external_control({**self.config, 'operation': 'retry'}, self.source)
        self.assertEqual(self.engine.runtime, before)
        self.assertEqual(len(self.sim.ports.http.requests), 1)

    def test_cancelled_before_send_retry_preserves_request_and_clears_outcome(self):
        operation = self.prepare()
        # 실제 전송 전 정지 생산자의 결과를 같은 엔진의 실행 기록으로 정산한다.
        from do_math.external import execute_operation
        def persist(row):
            self.engine._external_execution_record(row)
            self.engine._save()
            return True
        cancelled = execute_operation(deepcopy(operation), self.engine.instance['grants'][operation['grant_id']],
            persist=persist, should_stop=lambda: True, transport=self.sim.ports.http.request,
            clock=self.sim.clock, environment=self.sim.environment, runtime=self.engine.runtime)
        self.engine._external_execution_record(cancelled)
        self.engine._save()
        before = deepcopy(self.engine.runtime['external_operations'][operation['id']])
        self.sim.advance(1)
        self.engine._external_control({**self.config, 'operation': 'retry'}, self.source)
        result = self.engine.runtime['external_operations'][operation['id']]
        self.assertEqual((result['status'], result['transmitted'], result['transmission_phase']), ('prepared', False, 'not_started'))
        self.assertEqual(result['attempts'], [])
        self.assertEqual(result['continuation_of'], before['execution_id'])
        self.assertNotIn('execution_id', result)
        self.assertNotIn('error', result)
        self.assertEqual(result['history'][-1]['previous'], {k: v for k, v in before.items() if k not in {'history', 'attempts'}})
        self.assertEqual(self.sim.ports.http.requests, [])
        self.engine._save()
        self.assertEqual(self.engine.store.load()[2]['external_operations'][operation['id']], result)

    def test_failed_retry_without_reconciliation_proof_is_rejected(self):
        unknown = self.unknown()
        failed = reconcile_operation(unknown, self.evidence(unknown, 'effect_absent'), 'failed', source='user', effect_absent=True)
        self.engine.runtime['external_operations'][unknown['id']] = failed
        failed['reconciliation']['evidence']['evidence_ref'] = ''
        before = deepcopy(self.engine.runtime)
        with self.assertRaisesRegex(ValueError, '^retry requires request-bound effect or idempotency evidence$'):
            self.engine._external_control({**self.config, 'operation': 'retry'}, self.source)
        self.assertEqual(self.engine.runtime, before)
        self.assertEqual(len(self.sim.ports.http.requests), 1)

    def test_explicit_idempotency_retry_preserves_and_finishes_prior_attempt(self):
        unknown = deepcopy(self.unknown())
        proof = {'kind': 'verified_idempotency', 'request_sha256': unknown['request_sha256'],
                 'idempotency_key': unknown['idempotency_key'], 'evidence_ref': 'remote:contract',
                 'valid_until': '2199-01-01T00:00:00Z'}
        self.engine._external_control({**self.config, 'operation': 'retry', 'evidence': proof}, self.source)
        result = self.engine.runtime['external_operations'][unknown['id']]
        self.assertEqual(result['attempts'], [*unknown['attempts'][:-1],
            {**unknown['attempts'][-1], 'outcome': 'unknown', 'transmitted': True}])
        self.assertEqual(result['retry_evidence'], {**proof, 'source': 'user'})
        self.assertEqual(result['request'], unknown['request'])
        self.assertEqual(result['history'][-1]['previous_execution_id'], unknown['execution_id'])
        self.engine._save()
        self.assertEqual(self.engine.store.load()[2]['external_operations'][unknown['id']], result)
        self.assertEqual(len(self.sim.ports.http.requests), 1)

    def test_record_without_queued_action_registers_real_execution(self):
        operation = deepcopy(self.prepare())
        self.engine.runtime['queue'] = [row for row in self.engine.runtime['queue'] if row.get('target') != operation['id']]
        execution_ids = set(self.engine.runtime['executions'])
        self.engine._external_execution_record(operation)
        added = set(self.engine.runtime['executions']) - execution_ids
        self.assertEqual(added, {operation['execution_id']})
        record = self.engine.runtime['executions'][operation['execution_id']]
        self.assertEqual((record['role'], record['operation_id'], record['request_sha256']),
                         ('external_action', operation['id'], operation['request_sha256']))
        self.assertEqual(record['action']['source_ref'], operation['source_ref'])
        self.engine._save()
        self.assertEqual(self.engine.store.load()[2]['executions'][record['id']], record)

    def test_recorded_transmission_recovers_to_unknown_without_resending(self):
        operation = self.prepare()
        operation['transmission_phase'] = 'recorded'
        action = deepcopy(next(row for row in self.engine.runtime['queue'] if row.get('target') == operation['id']))
        self.engine._run_external_action(action)
        result = self.engine.runtime['external_operations'][operation['id']]
        self.assertEqual((result['status'], result['handling'], result['error']),
            ('unknown', 'reconciliation_required', 'Executor resumed without a confirmed remote outcome'))
        self.assertEqual(self.sim.ports.http.requests, [])
        self.engine._save()
        self.assertEqual(self.engine.store.load()[2]['external_operations'][operation['id']], result)

    def test_terminal_operation_run_does_not_change_ledger_or_send(self):
        operation = self.prepare()
        self.sim.ports.http.table['/effect'] = (201, b'ok', None)
        action = deepcopy(next(row for row in self.engine.runtime['queue'] if row.get('target') == operation['id']))
        run_machine(self.sim, 'external_action')
        before = deepcopy(self.engine.runtime)
        self.engine._run_external_action(action)
        self.assertEqual(self.engine.runtime, before)
        self.assertEqual(len(self.sim.ports.http.requests), 1)

    def test_explicit_machine_profile_keeps_role_model_selection(self):
        from do_math.model_policy import selection
        from do_math.execution_profiles import match_profile_ref
        instance = self.engine.instance
        reference, = instance['role_profile_refs']['external_action']
        action = {'role': 'external_action', 'profile_ref': reference}
        expected = selection(instance['config'], action, {}, {})
        result = selection(instance['config'], action, {}, {}, instance=instance)
        self.assertEqual(result, {**expected, 'profile_ref': reference})
        self.assertEqual(match_profile_ref(instance['execution_profiles'], result['profile_ref'])['actor_kind'], 'machine')
        self.assertEqual(self.sim.ports.http.requests, [])

    def test_generic_unrestricted_external_request_needs_no_solved_goal(self):
        operation = self.prepare()
        grant = self.engine.instance['grants'][operation['grant_id']]
        self.assertIsNone(self.engine._solution_basis())
        before = deepcopy(self.engine.runtime)
        self.assertIs(self.engine._external_prerequisite(operation, grant), True)
        self.assertEqual(self.engine.runtime, before)
        self.assertEqual(self.sim.ports.http.requests, [])

    def test_retry_repairs_stored_unknown_operation_with_no_attempt_row(self):
        operation = self.unknown()
        # 저장 스키마가 허용하는 불완전 장부: 정상 전송 결과에서 attempts 한 필드만 유실한다.
        operation['attempts'] = []
        self.engine._save()
        before = deepcopy(self.engine.runtime['external_operations'][operation['id']])
        proof = {'kind': 'verified_idempotency', 'request_sha256': before['request_sha256'],
                 'idempotency_key': before['idempotency_key'], 'evidence_ref': 'remote:contract',
                 'valid_until': '2199-01-01T00:00:00Z'}
        self.engine._external_control({**self.config, 'operation': 'retry', 'evidence': proof}, self.source)
        result = self.engine.runtime['external_operations'][operation['id']]
        self.assertEqual(result['attempts'], [{'request_sha256': before['request_sha256'],
                                              'outcome': 'unknown', 'transmitted': True}])
        self.assertEqual(result['history'][-1]['previous_status'], 'unknown')
        self.assertEqual(result['status'], 'prepared')
        self.engine._save()
        self.assertEqual(self.engine.store.load()[2]['external_operations'][operation['id']], result)
        self.assertEqual(len(self.sim.ports.http.requests), 1)

"""감독 종료·회복 응답의 전체 값과 우선순위. 원본 status도 보존한다."""
from copy import deepcopy
import unittest

from do_math.supervision import (SUPERVISION_BLOCKS, blocked_check_outcome, engine_failure_recovery,
                                 retryable_tool_error, start_guard, supervision_block)


class SupervisionClosureTests(unittest.TestCase):
    def test_provider_reobservation_opens_waiting_work_only_after_its_retry_and_never_over_user_pause(self):
        from support.provider_inputs import host_capacity_fixture
        from support.scheduling_hosts import admit, host_slots
        instance, selected, _ = host_capacity_fixture()
        runtime = {'executions': {}, 'reservations': {}}
        slots = host_slots(runtime, instance)
        profile = selected['research_work']
        accepted, execution = admit(slots, 'EX-supervised', profile)
        self.assertTrue(accepted)
        provider = execution['capacity']['provider']
        now = slots.clock.wall_ns() / 1_000_000_000
        result = {'status': 'failed', 'error_kind': 'provider_limit', 'failure': {
            'kind': 'provider_limit', 'provider': provider, 'retry_at': None,
            'limit_windows': [], 'evidence_ref': 'synthetic-provider-limit.json'}}
        slots.provider_result_from_run('EX-supervised', result, {
            'provider_retry_initial_seconds': 10, 'provider_retry_max_seconds': 10}, current_time=now)
        wait = slots.provider_wait(profile, current_time=now + 1)
        self.assertIsNotNone(wait)
        before_runtime = deepcopy(runtime)
        for instant, expected in ((now + 9, 'not_started'), (now + 10, 'startable')):
            with self.subTest(instant=instant):
                status = {'status': 'waiting', 'provider_waits': slots.provider_snapshot(current_time=instant),
                          'dispatch_waits': [{'wait': wait}]}
                before = deepcopy(status)
                answer = {'outcome': expected, 'before': before}
                if expected == 'startable':
                    answer['reason'] = 'provider re-observation due'
                self.assertEqual(start_guard(status), answer)
                self.assertEqual(status, before)
        paused = {**status, 'user_pause': {'reason': 'Explicit user pause'}}
        self.assertEqual(start_guard(paused), {'outcome': 'paused', 'before': paused})
        self.assertEqual(runtime, before_runtime)

    def test_central_block_population_and_first_present_priority(self):
        facts = {
            'held': {'held': True}, 'disabled': {'operator_enabled': False},
            'user_pause': {'user_pause': {'reason': '사용자'}}, 'maintenance': {'maintenance_fence': {'state': 'quiescent'}},
            'model_policy': {'model_policy_violation': {'reason': '모델 정책'}},
            'paused': {'status': 'paused'}, 'closed': {'status': 'closed'}, 'completed': {'status': 'completed'},
            'conversation_lost': {'conversation_lost': True}, 'installation_repair': {'installation_repair': {'id': 'RX'}},
        }
        self.assertEqual(set(facts), set(SUPERVISION_BLOCKS))
        self.assertIsNone(supervision_block({}))
        for index, block in enumerate(SUPERVISION_BLOCKS):
            with self.subTest(block=block):
                self.assertEqual(supervision_block(facts[block]), block)
                for later in SUPERVISION_BLOCKS[index + 1:]:
                    # status라는 하나의 필드가 동시에 세 상태일 수는 없다.
                    if 'status' in facts[block] and 'status' in facts[later]:
                        continue
                    self.assertEqual(supervision_block({**facts[later], **facts[block]}), block)

    def test_start_guard_block_envelopes_are_exact(self):
        for status, outcome in (
            ({'maintenance_fence': {'state': 'quiescent'}}, 'maintenance_waiting'),
            ({'model_policy_violation': {'reason': '정책'}}, 'model_policy_waiting'),
            ({'conversation_lost': True}, 'user_paused'),
            ({'installation_repair': {'id': 'RX'}}, 'installation_repair_waiting'),
            ({'status': 'closed'}, 'not_started'), ({'status': 'completed'}, 'not_started'),
            ({'status': 'paused'}, 'paused'), ({'user_pause': {'reason': '중지'}}, 'paused'),
        ):
            with self.subTest(outcome=outcome):
                before = deepcopy(status)
                self.assertEqual(start_guard(status), {'outcome': outcome, 'before': before})
                self.assertEqual(status, before)

    def test_research_reconsideration_is_not_hidden_by_operator_disabled(self):
        status = {'status': 'waiting', 'operator_enabled': False, 'research_wake_reasons': ['grant_changed']}
        self.assertEqual(start_guard(status), {'outcome': 'startable', 'before': status,
                         'reason': 'research reconsideration due', 'research_wake_reasons': ['grant_changed']})

    def test_blocked_check_envelopes_do_not_call_a_model(self):
        status = {'status': 'waiting'}
        expected = {
            'disabled': {'outcome': 'disabled'},
            'maintenance': {'outcome': 'maintenance_waiting', 'status': status, 'model_called': False},
            'model_policy': {'outcome': 'model_policy_waiting', 'status': status},
            'conversation_lost': {'outcome': 'user_paused', 'status': status},
        }
        for block in SUPERVISION_BLOCKS:
            with self.subTest(block=block):
                answer = ({'outcome': 'waiting', 'status': status}
                          if block in {'user_pause', 'paused', 'closed', 'completed'} else expected.get(block))
                self.assertEqual(blocked_check_outcome(block, status), answer)

    def test_engine_failure_is_distinct_from_contention_and_missing_report(self):
        for output in ('not json', '[]', 'null', '{}', '{"error":{"kind":"tool_error","retryable":false}}'):
            with self.subTest(output=output):
                self.assertFalse(retryable_tool_error(output))
        self.assertTrue(retryable_tool_error('{"error":{"kind":"tool_error","retryable":true}}'))
        self.assertIsNone(engine_failure_recovery(None, evidence_path='evidence.json'))
        self.assertIsNone(engine_failure_recovery({'outcome': 'completed'}, evidence_path='evidence.json'))
        self.assertEqual(engine_failure_recovery({'outcome': 'engine_failed', 'exit_code': 7,
            'run_directory': 'run'}, evidence_path='evidence.json'), {
                'kind': 'engine_unavailable', 'error': 'engine process failed with exit code 7',
                'evidence_path': 'evidence.json', 'engine_run_directory': 'run'})

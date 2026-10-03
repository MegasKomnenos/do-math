"""공개 결정·실제 저장·재시작으로 학술 근거와 외부 재시도 식별자를 확인한다."""
from copy import deepcopy
import unittest

from do_math import academic
from support.academic_scenes import consumer_sim
from support.engine_lifecycle import applied, external_sim, http_grant, run_machine
from support.state_builders import charter_change


def setUpModule():
    consumer_sim()
    external_sim()


class AcademicPublicCurrentnessTests(unittest.TestCase):
    def test_public_goal_and_scope_changes_invalidate_judgments_and_preserve_inputs(self):
        for changes in ({'goal': '새 목표: 자연수 덧셈의 교환법칙을 증명한다.'},
                        {'included_scope': ['새 범위: 모든 자연수 쌍']}):
            with self.subTest(changes=changes):
                sim = consumer_sim()
                engine = sim.engine
                old_charter = deepcopy(engine._governance()['charter'])
                requirements = academic.current_requirements(engine.instance)
                formal = deepcopy(engine.instance['formal_results'])
                judgments = deepcopy(engine.instance['goal_judgments'])
                self.assertTrue(judgments)
                self.assertIsNotNone(engine._solution_basis())
                change = charter_change(engine, **changes)
                text = '사용자가 승인한 변경 원문\n' + repr(changes)
                request = applied(sim, 'decision', text=text, config={'change': change})
                self.assertEqual(engine._governance()['charter']['content'], change['record']['content'])
                self.assertEqual(academic.current_requirements(engine.instance), requirements)
                self.assertEqual(engine.instance['formal_results'], formal)
                self.assertEqual(engine.instance['goal_status'], 'unsolved')
                self.assertIsNone(engine._solution_basis())
                self.assertEqual(len(engine.instance['goal_judgments']), len(judgments))
                self.assertTrue(all(row['current'] is False for row in engine.instance['goal_judgments']))
                self.assertEqual(engine.instance['governance'][old_charter['id']]['content'], old_charter['content'])
                control, = [row for row in engine.runtime['history'] if row.get('kind') == 'user_control'
                            and row['request']['id'] == request['request_id']]
                self.assertEqual(control['request']['text'], text)
                self.assertEqual(control['request']['config'], {'change': change})
                _, saved_instance, saved_runtime = engine.store.load()
                self.assertEqual(saved_instance['goal_judgments'], engine.instance['goal_judgments'])
                self.assertEqual(saved_runtime['history'], engine.runtime['history'])

    def test_public_retry_and_restart_preserve_request_and_separate_execution_attempts(self):
        sim = external_sim()
        config = http_grant(sim.engine)
        # http_grant는 결정 생산자만 호출하므로 공개 수신자의 재적재 전에 게시한다.
        sim.engine._save()
        applied(sim, 'external', config=config)
        sim.ports.http.table['/effect'] = (503, b'uncertain', None)
        run_machine(sim, 'external_action')
        first = deepcopy(sim.runtime['external_operations'][config['id']])
        self.assertEqual(first['status'], 'unknown')
        self.assertEqual(len(sim.ports.http.requests), 1)
        sim.restart()
        self.assertEqual(sim.runtime['external_operations'][config['id']], first)
        proof = {'kind': 'verified_idempotency', 'request_sha256': first['request_sha256'],
                 'idempotency_key': first['idempotency_key'], 'evidence_ref': 'remote:contract',
                 'valid_until': '2199-01-01T00:00:00Z'}
        applied(sim, 'external', config={**config, 'operation': 'retry', 'evidence': proof})
        prepared = deepcopy(sim.runtime['external_operations'][config['id']])
        self.assertEqual(prepared['status'], 'prepared')
        self.assertNotIn('execution_id', prepared)
        self.assertEqual(prepared['continuation_of'], first['execution_id'])
        self.assertEqual(prepared['request_sha256'], first['request_sha256'])
        self.assertEqual(prepared['request'], first['request'])
        sim.ports.http.table['/effect'] = (201, b'accepted', None)
        run_machine(sim, 'external_action')
        final = sim.runtime['external_operations'][config['id']]
        self.assertEqual((final['status'], final['succeeded']), ('confirmed', True))
        self.assertEqual((final['request'], final['request_sha256'], final['idempotency_key']),
                         (first['request'], first['request_sha256'], first['idempotency_key']))
        self.assertNotEqual(final['execution_id'], first['execution_id'])
        self.assertEqual(final['continuation_of'], first['execution_id'])
        self.assertEqual(final['history'], prepared['history'])
        self.assertEqual(len(final['attempts']), 2)
        self.assertEqual(len(sim.ports.http.requests), 2)
        for operation in (first, final):
            record = sim.runtime['executions'][operation['execution_id']]
            self.assertEqual((record['operation_id'], record['request_sha256'], record['status']),
                             (operation['id'], operation['request_sha256'], 'ended'))
        self.assertEqual(sim.engine.store.load()[2]['external_operations'][config['id']], final)

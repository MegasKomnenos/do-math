"""2-C·8-B의 남은 실행 종류·반환 시점 교차 입력. 한 역할 여정당 수 초가 든다."""
from copy import deepcopy
import unittest

from do_math.execution_profiles import MACHINE_ROLES
from do_math.parallel import ModelCalls
from support.engine_lifecycle import applied, warm_lifecycle, warm_external
from support.scheduling_return_matrix import scene, AfterReturn, assert_returned
from support.scheduling_return_observer import OwnerProbe
from support.scheduling_return_ports import defer_first_calculation
from support.scheduling_machine import hold_lean
from support.sim import warm_template


ROLES = ('research_work', 'formal_check', 'trust_check', 'trust_activate', 'external_action')


def setUpModule():
    warm_template()
    warm_lifecycle()
    warm_external()


class ReturnMatrixTests(unittest.TestCase):
    def test_all_machine_roles_are_in_the_return_population(self):
        self.assertEqual(set(ROLES) - {'research_work'}, set(MACHINE_ROLES))

    def test_preexisting_stop_fence_and_until_active_create_nothing_for_each_role(self):
        for role in ROLES:
            for gate in ('pause', 'quiesce', 'close', 'until_active'):
                with self.subTest(role=role, gate=gate):
                    sim = scene(role)
                    if gate != 'until_active':
                        applied(sim, gate, text='실행 전 반환 경로')
                    before = deepcopy(sim.runtime['executions'])
                    reservations = deepcopy(sim.runtime['reservations'])
                    with OwnerProbe(sim) as probe:
                        answer = sim.engine.run(max_steps=1, until_active=gate == 'until_active')
                    self.assertIsInstance(answer, dict)
                    self.assertEqual(sim.runtime['executions'], before)
                    self.assertEqual(sim.runtime['reservations'], reservations)
                    self.assertEqual(answer['active_executions'], [])
                    self.assertEqual(probe.failures, [])
                    self.assertIsNone(sim.engine._calls)

    def test_step_limit_applies_each_machine_result_before_return(self):
        for role in ROLES[1:]:
            with self.subTest(role=role):
                sim = scene(role)
                before = set(sim.runtime['executions'])
                with OwnerProbe(sim) as probe:
                    sim.engine.run(max_steps=1)
                row = assert_returned(self, sim, before, probe, role)
                self.assertIn(row['outcome'], ('verified', 'output_accepted'))
                executions, reservations = deepcopy(sim.runtime['executions']), deepcopy(sim.runtime['reservations'])
                sim.engine.run(max_steps=1, until_active=True)
                self.assertEqual(sim.runtime['executions'], executions)
                self.assertEqual(sim.runtime['reservations'], reservations)

    def test_machine_fence_and_close_during_calculation_drain_before_return(self):
        for role in ('formal_check', 'trust_check', 'trust_activate'):
            for gate in ('quiesce', 'close'):
                with self.subTest(role=role, gate=gate):
                    sim = scene(role)
                    before = set(sim.runtime['executions'])
                    requests = []
                    def stop():
                        if not requests:
                            requests.append(sim.control(gate, text='기계 계산 중 반환 검사'))
                    if role == 'trust_activate':
                        # 환경 계산은 한 번의 호스트 관찰이다. 그 포트에서 제어를 도착시킨다.
                        original = sim.ports.host.toolchain_identity_errors
                        def observe(*args, **kwargs):
                            stop()
                            return original(*args, **kwargs)
                        sim.ports.host.toolchain_identity_errors = observe
                    else:
                        from support.fakes.calls import owner_turn
                        def hold():
                            stop()
                            owner_turn()
                        hold_lean(sim, hold)
                    with OwnerProbe(sim) as probe:
                        sim.engine.run(max_steps=1)
                    assert_returned(self, sim, before, probe, role)
                    self.assertEqual(len(requests), 1)
                    self.assertEqual(sim.engine.control_result(requests[0]['request_id'])['effect'], 'applied')

    def test_controls_arriving_after_collection_are_applied_before_bounded_return(self):
        for role in ROLES:
            for gate in ('pause', 'quiesce'):
                with self.subTest(role=role, gate=gate):
                    sim = scene(role)
                    before = set(sim.runtime['executions'])
                    requests = []
                    def stop():
                        requests.append(sim.control(gate, text='완료 회수 직후 공개 제어'))
                    function = sim.engine._run_external_action if role == 'external_action' else ModelCalls.collect
                    predicate = (lambda value: True) if role == 'external_action' else (lambda value: value > 0)
                    with OwnerProbe(sim) as probe, AfterReturn(function, stop, predicate) as arrival:
                        sim.engine.run(max_steps=1)
                    assert_returned(self, sim, before, probe, role)
                    self.assertEqual(len(arrival.values), 1)
                    self.assertEqual(len(requests), 1)
                    self.assertEqual(sim.engine.control_result(requests[0]['request_id'])['effect'], 'applied')

    def test_trust_activation_stopped_before_first_calculation_preserves_evidence(self):
        sim = scene('trust_activate')
        before = set(sim.runtime['executions'])
        defer_first_calculation(sim, lambda: sim.control('pause', text='환경 계산 첫 차례 전 정지'))
        with OwnerProbe(sim) as probe:
            sim.engine.run(max_steps=1)
        row = assert_returned(self, sim, before, probe, 'trust_activate')
        self.assertEqual(row['outcome'], 'execution_incomplete')
        self.assertEqual(sim.runtime['status'], 'paused')

    def test_failed_host_identity_check_cannot_activate_the_pending_environment(self):
        import json
        sim = scene('trust_activate')
        action, = sim.runtime['queue']
        transition_id = action['transition_id']
        previous = sim.instance['active_trust_environment']
        before = set(sim.runtime['executions'])
        checks = len(sim.lean.checks)
        calls = len(sim.model.calls)
        detail = 'synthetic host: approved executable identity changed'
        port = defer_first_calculation(sim, lambda: sim.ports.host.toolchain_errors.append(detail))
        with OwnerProbe(sim) as probe:
            sim.engine.run(max_steps=1)
        row = assert_returned(self, sim, before, probe, 'trust_activate')
        self.assertTrue(port.created[0].deferred)
        self.assertEqual(row['outcome'], 'execution_incomplete')
        self.assertNotIn('submission_receipt', row)
        transition = sim.runtime['trust_transitions'][transition_id]
        self.assertEqual(transition['status'], 'failed')
        self.assertEqual(sim.instance['active_trust_environment'], previous)
        result = json.loads(sim.engine.store.read(row['result_ref'], sim.engine.head))
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(result['reason'], 'current environment check required: ' + detail)
        self.assertEqual(len(sim.lean.checks), checks)
        self.assertEqual(len(sim.model.calls), calls)
        self.assertNotIn(action['id'], [a['id'] for a in sim.runtime['queue']])

    def test_invalidation_during_formal_calculation_preserves_the_return_without_admission(self):
        import json
        from support.fakes.calls import owner_turn
        sim = scene('formal_check')
        action, = sim.runtime['queue']
        before = set(sim.runtime['executions'])
        formal_before = deepcopy(sim.instance['formal_results'])
        environment_id = sim.instance['active_trust_environment']
        requests = []
        def invalidate():
            if not requests:
                requests.append(sim.control('trust', config={
                    'operation': 'invalidate', 'env_id': environment_id,
                    'reason': 'public invalidation while the exact source is being checked'}))
                owner_turn()
        hold_lean(sim, invalidate)
        with OwnerProbe(sim) as probe:
            sim.engine.run(max_steps=1)
        row = assert_returned(self, sim, before, probe, 'formal_check')
        self.assertEqual(len(requests), 1)
        self.assertEqual(sim.engine.control_result(requests[0]['request_id'])['effect'], 'applied')
        self.assertEqual(row['outcome'], 'execution_incomplete')
        self.assertEqual(row['formal_status'], 'stopped')
        self.assertIn('trust_environment_changed', row['result_disposition']['stop_reasons'])
        self.assertNotIn('submission_receipt', row)
        self.assertEqual(sim.instance['formal_results'], formal_before)
        result = json.loads(sim.engine.store.read(row['result_ref'], sim.engine.head))
        self.assertEqual(result['status'], 'stopped')
        self.assertEqual(sim.instance['trust_environments'][environment_id]['status'], 'invalid')
        self.assertIsNone(sim.instance['active_trust_environment'])
        self.assertEqual(sim.runtime['waiting_actions'][action['id']]['kind'], 'formal_stopped')

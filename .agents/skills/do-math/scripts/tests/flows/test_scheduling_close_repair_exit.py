"""2-C 설치 수리 대기: 실제 진단 수신·보존·수리 인계 뒤 공개 run을 부른다."""
from copy import deepcopy
import unittest

from do_math.repair_execution import pending_installation_repair
from support.operator_finish_scene import Scene, diagnose
from support.scheduling_return_observer import OwnerProbe
from support.scheduling_exit_contracts import assert_no_dispatch
from support.sim import warm_template
from support.model import Answer, raw
from support.scheduling_parallel import ready_work_sim


setUpModule = warm_template


class RepairExitTests(unittest.TestCase):
    def test_real_failed_worker_and_independent_diagnosis_stop_later_dispatch(self):
        sim = ready_work_sim(1, max_output_repairs=0)
        sim.model.on('research_work').reply(raw({}, expected_receipt='rejected'))
        def diagnosis(output, context):
            target = context['action']['target']
            return {**output, 'disposition': {'kind': 'repair', 'basis_refs': [target],
                'next_owner': 'installation_recovery', 'reason': '보존된 실패의 설치 수신기 진단',
                'repair_target': 'installation:scripts/do_math/engine.py',
                'meaning_preserving': True, 'verification': '정상 응답 수신 회귀를 재현한다'}}
        sim.model.on('operational_review').reply(Answer(diagnosis))
        sim.run_until(lambda s: pending_installation_repair(s.runtime) is not None, max_steps=8)
        self.assertTrue(any(e['role'] == 'research_work' and e['outcome'] == 'execution_incomplete'
                            for e in sim.runtime['executions'].values()))
        reviews = [e for e in sim.runtime['executions'].values()
                   if e['role'] == 'operational_review' and e['outcome'] == 'output_accepted']
        self.assertEqual(len(reviews), 1)
        self.assertEqual(reviews[0]['submission_receipt']['state'], 'accepted')
        pending = deepcopy(pending_installation_repair(sim.runtime))
        before = deepcopy(sim.runtime['executions'])
        reservations = deepcopy(sim.runtime['reservations'])
        with OwnerProbe(sim) as probe:
            answer = sim.engine.run(max_steps=1)
        assert_no_dispatch(self, sim, answer, before, reservations, probe)
        self.assertEqual(answer['active_executions'], [])
        self.assertEqual(answer['status'], 'waiting')
        self.assertEqual(pending_installation_repair(sim.runtime), pending)

    def test_accepted_installation_diagnosis_stops_public_dispatch(self):
        scene = Scene()
        diagnose(scene)
        sim = scene.sim
        pending = pending_installation_repair(sim.runtime)
        self.assertIsNotNone(pending)
        self.assertEqual(pending['status'], 'installation_repair_pending')
        before = deepcopy(sim.runtime['executions'])
        reservations = deepcopy(sim.runtime['reservations'])
        with OwnerProbe(sim) as probe:
            answer = sim.engine.run(max_steps=1)
        assert_no_dispatch(self, sim, answer, before, reservations, probe)
        self.assertEqual(answer['active_executions'], [])
        self.assertEqual(answer['status'], 'waiting')
        self.assertEqual(pending_installation_repair(sim.runtime), pending)

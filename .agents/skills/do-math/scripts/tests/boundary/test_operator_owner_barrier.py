"""운영자 복구의 실제 소유자 관찰. 현재 시험과 스스로 만든 자식만 관찰한다."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

from do_math import launch
from do_math.repair_execution import unconfirmed_termination
from do_math.windows_job import WindowsJobs
from support.scheduling_slots import reserve, slot_sim
from test_categories import test_group


@test_group('resource')
class OperatorOwnerBarrierTests(unittest.TestCase):
    def test_live_caller_remains_a_recovery_barrier_even_after_local_return(self):
        sim, jobs = slot_sim(), WindowsJobs()
        accepted, execution = reserve(sim, 'EX-operator-owner', jobs=jobs)
        self.assertTrue(accepted)
        sim.engine._save()
        ticket = sim.engine.runtime['executions'][execution['id']]['launch_ticket']
        self.assertEqual(ticket['owner'], jobs.owner_identity())
        self.assertEqual(unconfirmed_termination(sim.engine.store.load()[2], jobs=jobs), execution['id'])
        launch.mark_dispatched(ticket)
        launch.mark_returned(ticket)
        sim.engine._save()
        self.assertEqual(unconfirmed_termination(sim.engine.store.load()[2], jobs=jobs), execution['id'])
        self.assertIs(jobs.owner_ended(ticket['owner']), False)

    def test_own_exited_child_ticket_clears_the_operator_recovery_barrier(self):
        sim, jobs = slot_sim(), WindowsJobs()
        accepted, execution = reserve(sim, 'EX-operator-child', jobs=jobs)
        self.assertTrue(accepted)
        profile = sim.instance['execution_profiles'][execution['execution_profile_ref']['id']]
        program = '''import json,sys
from do_math.launch import ticket, mark_dispatched
from do_math.system_clock import SystemClock
from do_math.windows_job import WindowsJobs
print(json.dumps(mark_dispatched(ticket(sys.argv[1], json.loads(sys.argv[2]), jobs=WindowsJobs(), clock=SystemClock()))))
'''
        # 자식은 발사표만 생산하고 종료한다. 공급자·예약·Lean·다른 프로세스는 건드리지 않는다.
        child = subprocess.run([sys.executable, '-B', '-c', program, execution['id'], json.dumps(profile)],
            cwd=Path(__file__).resolve().parents[2], capture_output=True, text=True, encoding='utf-8',
            timeout=30, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        self.assertEqual(child.returncode, 0, child.stderr)
        ticket = json.loads(child.stdout)
        launch.validate(ticket, execution_id=execution['id'], profile_sha256=profile['sha256'])
        execution['launch_ticket'] = ticket
        sim.engine._save()
        self.assertNotEqual(ticket['owner']['pid'], jobs.owner_identity()['pid'])
        self.assertIs(jobs.owner_ended(ticket['owner']), True)
        self.assertIs(jobs.named_job_empty(ticket['job_name']), True)
        self.assertIsNone(unconfirmed_termination(sim.engine.store.load()[2], jobs=jobs))

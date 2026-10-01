"""The Git writer lock between two operating-system processes, and a slot held until a real named Windows Job ends.

- The writer lock: a real repository, initialized through the public
  ``initialize`` with the real ports, whose lock the parent holds while a child
  Python process tries to take it.
- The named Job: the slot ledger of an initialized Sim instance confirms Job
  ends with the real Jobs port (``wiring.real_ports().jobs``), and the Job is a
  real Windows Job of that name.
"""
from copy import deepcopy
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import uuid

from do_math.engine import ResearchEngine, initialize
from do_math.wiring import real_ports
from support.fakes.git_backend import make_repository
from support.scheduling_slots import LIMITS, reserve, slot_sim, slots
from test_categories import test_group

SCRIPTS = Path(__file__).resolve().parents[2]


@test_group('resource')
class WriterLockTests(unittest.TestCase):
    def test_two_processes_cannot_both_own_the_git_writer(self):
        from support.entry import entry
        _entry = entry()
        from support.entry import entry
        _entry = entry()
        ports = real_ports(environment=_entry.environment)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_repository(root / 'repository')
            created = initialize(root / 'repository', goal='Reservation boundary fixture', workspace=root / 'work',
                                 config={'operator_enabled': True, 'scholarly_enabled': False,
                                         'session_limits': deepcopy(LIMITS)}, ports=ports, codex_home=_entry.codex_home, host_id=_entry.host_id)
            engine = ResearchEngine(root / 'repository', created['instance_id'], ports=ports, codex_home=_entry.codex_home, environment=_entry.environment, host_id=_entry.host_id)
            program = '\n'.join([
                'import sys', 'from pathlib import Path',
                'sys.path.insert(0, sys.argv[1])',
                'from do_math.repository import ResearchRepository',
                'try:',
                ' with ResearchRepository(Path(sys.argv[2]),sys.argv[3]).writer_lock(): print("acquired")',
                'except Exception as error: print(type(error).__name__)'])
            with engine.store.writer_lock():
                child = subprocess.run([sys.executable, '-c', program, str(SCRIPTS), str(root / 'repository'),
                                        engine.instance['id']], capture_output=True, text=True, timeout=30)
            self.assertEqual(child.returncode, 0, child.stderr)
            self.assertIn('LockError', child.stdout)
            self.assertNotIn('acquired', child.stdout)


@test_group('resource')
class NamedJobTests(unittest.TestCase):
    @unittest.skipUnless(os.name == 'nt', 'requires a Windows Job')
    def test_slot_waits_for_actual_named_job_termination(self):
        sim = slot_sim()
        jobs = real_ports(environment=sim.environment).jobs
        engine = sim.engine
        with engine.store.writer_lock():
            self.assertTrue(reserve(sim, 'EX-job', jobs=jobs)[0])
            # A name no other run shares: the Sim clock draws the same ticket name in every run.
            ticket = engine.runtime['executions']['EX-job']['launch_ticket']
            ticket['job_name'] = 'Local\\DoMath-' + uuid.uuid4().hex
            with jobs.launch([sys.executable, '-c', 'import time; time.sleep(30)'], name=ticket['job_name']) as job:
                slots(sim, jobs=jobs).started('EX-job', {'pid': job.pid, 'job_name': ticket['job_name']}, at=sim.clock.now())
                engine._save()
                job.resume()
                self.assertFalse(slots(sim, jobs=jobs).release('EX-job'))
                job.terminate()
                self.assertTrue(job.wait(10))
                self.assertTrue(jobs.named_job_empty(ticket['job_name']))
                self.assertTrue(slots(sim, jobs=jobs).release('EX-job'))
            engine._save()


if __name__ == '__main__':
    unittest.main()

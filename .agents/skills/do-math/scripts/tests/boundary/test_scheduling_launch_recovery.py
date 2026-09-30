"""Real local ownership observations across the pre-publication launch gap (``launch`` on the real Jobs port).

A launch ticket names the launching owner (PID, creation FILETIME, host,
session) and, for a native launch, the name of its Job. A recovering process
confirms an earlier launch's end from the ticket alone: only an owner that has
certainly ended counts, and a native launch also needs its named Job empty. An
unknown host or session is never evidence of death. These cases use the real
current process, real child owners and real named Windows Jobs.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest

from do_math.launch import termination_confirmed, ticket
from do_math.system_clock import SystemClock
from do_math.windows_job import WindowsJob, WindowsJobs, owner_ended, owner_identity

SCRIPTS = Path(__file__).resolve().parents[2]
PROFILE = {'sha256': 'a' * 64, 'actor_kind': 'ai', 'role': 'research_work'}  # a native Job launch
OWNER = '''import json,sys,time
from pathlib import Path
sys.path.insert(0,sys.argv[1])
from do_math.launch import ticket
from do_math.system_clock import SystemClock
from do_math.windows_job import WindowsJob, WindowsJobs
root=Path(sys.argv[2])
t=ticket('EX-crash',{'sha256':'a'*64,'actor_kind':'ai','role':'research_work'},jobs=WindowsJobs(),clock=SystemClock())
t['phase']='dispatched'
(root/'ticket.json').write_text(json.dumps(t))
if sys.argv[3]!='before_create':
 command="from pathlib import Path; import time; Path(r'%s').write_text('resumed'); time.sleep(%s)" % (root/'resumed',30 if sys.argv[3]=='running' else 0)
 job=WindowsJob([sys.executable,'-c',command],name=t['job_name'])
 if sys.argv[3] in {'running','completed'}:
  job.resume()
  while not (root/'resumed').exists(): time.sleep(.01)
  if sys.argv[3]=='completed':
   while not job.inspect().root_signaled: time.sleep(.01)
(root/'ready').write_text('ready')
time.sleep(30)
'''


def reached(predicate, timeout):
    """Poll ``predicate`` until it holds or ``timeout`` seconds pass; whether it held."""
    deadline = time.monotonic() + timeout
    pause = threading.Event()
    while time.monotonic() < deadline:
        if predicate():
            return True
        pause.wait(0.02)
    return predicate()


@unittest.skipUnless(os.name == 'nt', 'Windows launch contract')
class LaunchRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.jobs, self.clock = WindowsJobs(), SystemClock()

    def test_current_owner_and_foreign_session_are_not_dead(self):
        identity = owner_identity()
        self.assertFalse(owner_ended(identity))
        self.assertIsNone(owner_ended({**identity, 'session': identity['session'] + 1}))
        t = ticket('EX-test', PROFILE, jobs=self.jobs, clock=self.clock)
        self.assertFalse(termination_confirmed(t, recovering=True, jobs=self.jobs))
        t['phase'] = 'dispatched'
        self.assertFalse(termination_confirmed(t, jobs=self.jobs))

    def owner_boundary(self, root, child):
        """The child owner wrote its ticket (and Job) and waits; fail if it exited first."""
        def boundary():
            if child.poll() is not None:
                self.fail('owner exited before test boundary')
            return (root / 'ready').exists()
        reached(boundary, 10)

    def test_crash_before_and_after_suspended_root_creation_is_recoverable(self):
        for stage in ('before_create', 'suspended', 'running', 'completed'):
            with self.subTest(stage=stage), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                child = subprocess.Popen([sys.executable, '-c', OWNER, str(SCRIPTS), str(root), stage],
                                         creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
                try:
                    self.owner_boundary(root, child)
                    self.assertTrue((root / 'ready').exists())
                    t = json.loads((root / 'ticket.json').read_text())
                    self.assertFalse(termination_confirmed(t, recovering=True, jobs=self.jobs))
                    child.kill()
                    child.wait(5)
                    confirmed = reached(lambda: termination_confirmed(t, recovering=True, jobs=self.jobs), 5)
                    self.assertTrue(confirmed)
                    self.assertEqual((root / 'resumed').exists(), stage in {'running', 'completed'})
                finally:
                    if child.poll() is None:
                        child.kill()
                        child.wait(5)

    def test_job_name_collision_cannot_attach_or_kill_the_original(self):
        t = ticket('EX-collision', PROFILE, jobs=self.jobs, clock=self.clock)
        with WindowsJob([sys.executable, '-c', 'pass'], name=t['job_name']) as first:
            with self.assertRaisesRegex(FileExistsError, 'execution Job name already exists'):
                WindowsJob([sys.executable, '-c', 'pass'], name=t['job_name'])
            self.assertFalse(first.inspect().root_signaled)


if __name__ == '__main__':
    unittest.main()

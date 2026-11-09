"""A session host takes every process its session started with it when it exits; the shared Lean
broker, started with an explicit breakaway, is not one of them."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest

HERE = Path(__file__).resolve().parent
RUNTIME = HERE.parent
sys.path.insert(0, str(RUNTIME))

from runtime_support import process_identity  # noqa: E402

# A stand-in host: optionally contains itself, starts a short-lived "shell" that leaves a computation
# behind and exits, records that computation's PID, then waits for a release file before exiting.
# The computation is either detached the way nohup or a background job leaves it, or started with
# the breakaway the broker client uses.
HOST = textwrap.dedent("""
    import json, subprocess, sys, time
    from pathlib import Path
    sys.path.insert(0, sys.argv[1])
    from runtime_support import contain_session_processes
    folder = Path(sys.argv[2])
    status = contain_session_processes() if sys.argv[3] == 'contain' else {'contained': False}
    (folder / 'status.json').write_text(json.dumps(status))
    shell = (
        "import subprocess, sys, pathlib; sys.path.insert(0, sys.argv[1]); "
        "from runtime_support import popen_options; "
        "p = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(120)'], "
        "**popen_options(detached=True, breakaway=sys.argv[3] == 'breakaway')); "
        "pathlib.Path(sys.argv[2]).write_text(str(p.pid))")
    subprocess.run([sys.executable, '-c', shell, sys.argv[1], str(folder / 'orphan.pid'), sys.argv[4]],
                   creationflags=subprocess.CREATE_NO_WINDOW, check=True)
    while not (folder / 'release').exists():
        time.sleep(0.05)
""")


def wait_for(predicate, seconds):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.05)
    return predicate()


def kill_if_alive(pid):
    if process_identity(pid) is not None:
        subprocess.run(['taskkill', '/F', '/PID', str(pid)], capture_output=True)


@unittest.skipUnless(os.name == 'nt', 'Windows job objects')
class ContainmentTests(unittest.TestCase):
    def run_host(self, contain, launch):
        folder = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, folder, True)
        host = subprocess.Popen([sys.executable, '-c', HOST, str(RUNTIME), str(folder), contain, launch],
                                creationflags=subprocess.CREATE_NO_WINDOW)
        self.addCleanup(lambda: host.poll() is None and host.kill())
        self.assertTrue(wait_for(lambda: (folder / 'orphan.pid').is_file()
                                 and (folder / 'orphan.pid').read_text(), 60))
        orphan = int((folder / 'orphan.pid').read_text())
        self.addCleanup(kill_if_alive, orphan)
        # The shell that started it has ended; only job membership can still tie it to the host.
        time.sleep(0.5)
        self.assertIsNotNone(process_identity(orphan), 'the computation runs while its host lives')
        (folder / 'release').write_text('')
        host.wait(timeout=60)
        return json.loads((folder / 'status.json').read_text()), orphan

    def test_a_detached_computation_ends_with_its_contained_host(self):
        status, orphan = self.run_host('contain', 'detached')
        self.assertEqual(status, {'contained': True})
        self.assertTrue(wait_for(lambda: process_identity(orphan) is None, 10),
                        'the detached computation outlived its contained host')

    def test_without_containment_the_detached_computation_survives(self):
        # Control: the stand-in reproduces the leak that containment closes.
        status, orphan = self.run_host('plain', 'detached')
        self.assertEqual(status, {'contained': False})
        time.sleep(1)
        self.assertIsNotNone(process_identity(orphan))

    def test_a_breakaway_process_such_as_the_broker_outlives_the_contained_host(self):
        # The broker a session's client starts is shared; it must not end with that session.
        status, orphan = self.run_host('contain', 'breakaway')
        self.assertEqual(status, {'contained': True})
        time.sleep(1)
        self.assertIsNotNone(process_identity(orphan), 'a breakaway process ended with the session')


if __name__ == '__main__':
    unittest.main()

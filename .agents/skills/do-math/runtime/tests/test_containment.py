"""A session host takes every process its session started with it when it exits; the shared Lean
broker, started with an explicit breakaway, is not one of them."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
RUNTIME = HERE.parent
sys.path.insert(0, str(RUNTIME))

import lean_broker  # noqa: E402
from runtime_support import popen_options, process_identity, read_json, write_json  # noqa: E402

# A stand-in CLI turn, the external boundary the session host launches: it starts a short-lived
# "shell" that leaves a computation behind and exits, records that computation's PID, then waits
# for a release file before exiting. The computation is either detached the way nohup or a
# background job leaves it, or started with the breakaway the broker client uses.
CLI = textwrap.dedent("""
    import subprocess, sys, time
    from pathlib import Path
    folder = Path(sys.argv[2])
    shell = (
        "import subprocess, sys, pathlib; sys.path.insert(0, sys.argv[1]); "
        "from runtime_support import popen_options; "
        "p = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(120)'], "
        "**popen_options(detached=True, breakaway=sys.argv[3] == 'breakaway')); "
        "pathlib.Path(sys.argv[2]).write_text(str(p.pid))")
    subprocess.run([sys.executable, '-c', shell, sys.argv[1], str(folder / 'orphan.pid'), sys.argv[3]],
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
    def run_turn(self, launch, hosted=True):
        """Run the stand-in turn under the production session host, from the files dispatch leaves
        for it, or directly without a host for the control. Returns the containment the host
        recorded (None without a host) and the computation's PID."""
        folder = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, folder, True)
        argv = [sys.executable, '-c', CLI, str(RUNTIME), str(folder), launch]
        if hosted:
            write_json(folder / 'launch.json', {'runner': process_identity(os.getpid()),
                                                'command': {'argv': argv, 'cwd': str(folder)}})
            (folder / 'prompt.txt').write_bytes(b'')
            (folder / 'GO').write_bytes(b'go\n')
            argv = [sys.executable, '-B', str(RUNTIME / 'runner.py'), '_session', str(folder)]
        process = subprocess.Popen(argv, cwd=folder, creationflags=subprocess.CREATE_NO_WINDOW)
        self.addCleanup(lambda: process.poll() is None and process.kill())
        self.assertTrue(wait_for(lambda: (folder / 'orphan.pid').is_file()
                                 and (folder / 'orphan.pid').read_text(), 60))
        orphan = int((folder / 'orphan.pid').read_text())
        self.addCleanup(kill_if_alive, orphan)
        # The shell that started it has ended; only job membership can still tie it to the session.
        time.sleep(0.5)
        self.assertIsNotNone(process_identity(orphan), 'the computation runs while its session lives')
        (folder / 'release').write_text('')
        self.assertEqual(process.wait(timeout=60), 0)
        return (read_json(folder / 'process-job.json')['contained'] if hosted else None), orphan

    def test_a_detached_computation_ends_with_its_session_host(self):
        contained, orphan = self.run_turn('detached')
        self.assertTrue(contained)
        self.assertTrue(wait_for(lambda: process_identity(orphan) is None, 10),
                        'the detached computation outlived its session host')

    def test_without_a_host_the_detached_computation_survives(self):
        # Control: the stand-in turn reproduces the leak that the host's containment closes.
        _, orphan = self.run_turn('detached', hosted=False)
        time.sleep(1)
        self.assertIsNotNone(process_identity(orphan))

    def test_a_breakaway_process_such_as_the_broker_outlives_the_session_host(self):
        # The broker a session's client starts is shared; it must not end with that session.
        contained, orphan = self.run_turn('breakaway')
        self.assertTrue(contained)
        time.sleep(1)
        self.assertIsNotNone(process_identity(orphan), 'a breakaway process ended with the session')


class BrokerClientTests(unittest.TestCase):
    def test_the_broker_client_asks_to_leave_the_job_and_starts_inside_when_refused(self):
        # The production client up to the process boundary: lean_broker.ensure_broker first asks to
        # start the shared broker outside the caller's job, the breakaway that the breakaway test
        # above shows the system honouring under a real session host. A job that forbids leaving
        # refuses with PermissionError, and the client then starts the broker inside it
        # (reference/operations.md, Waiting, fallback and recovery).
        folder = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, folder, True)
        (folder / 'runner').mkdir()
        paths = lean_broker.Paths(folder)
        requests = []

        def start(argv, **options):
            requests.append(options)
            if len(requests) == 1:
                raise PermissionError('this job forbids breakaway')
            # The receipt a started broker writes; this live process stands in for the broker.
            write_json(paths.process, {'process': process_identity(os.getpid())})

        with patch.object(lean_broker.subprocess, 'Popen', side_effect=start):
            info = lean_broker.ensure_broker(paths)
        self.assertEqual(info['process'], process_identity(os.getpid()))
        self.assertEqual(len(requests), 2)
        for options, breakaway in zip(requests, (True, False)):
            expected = popen_options(detached=True, breakaway=breakaway)
            self.assertEqual({key: options.get(key) for key in expected}, expected)


if __name__ == '__main__':
    unittest.main()

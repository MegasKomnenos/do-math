"""A session host takes every process its session started with it when it exits, and nothing the
session starts can leave its job; the shared Lean broker is therefore never started from inside one."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import textwrap
import threading
import time
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
RUNTIME = HERE.parent
sys.path.insert(0, str(RUNTIME))

import lean_broker  # noqa: E402
from runtime_support import popen_options, process_identity, read_json, write_json  # noqa: E402

GIT_BASH = Path(os.environ.get('ProgramFiles', r'C:\Program Files')) / 'Git/usr/bin/bash.exe'

# A stand-in CLI turn, the external boundary the session host launches: it runs a short-lived
# "shell" that leaves a computation behind and exits, then waits for a release file before exiting.
# The shell is the command line that follows the folder.
CLI = textwrap.dedent("""
    import subprocess, sys, time
    from pathlib import Path
    folder = Path(sys.argv[1])
    subprocess.run(sys.argv[2:], creationflags=subprocess.CREATE_NO_WINDOW, check=True)
    while not (folder / 'release').exists():
        time.sleep(0.05)
""")

# The shell's computation, started the way nohup or a background job leaves it (detached) or with
# the request to leave the job that the broker client makes (breakaway). It records the
# computation's PID, or that the system refused to start it.
SHELL = textwrap.dedent("""
    import pathlib, subprocess, sys
    sys.path.insert(0, sys.argv[1])
    from runtime_support import popen_options
    try:
        p = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(120)'],
                             **popen_options(detached=True, breakaway=sys.argv[3] == 'breakaway'))
        outcome = str(p.pid)
    except PermissionError:
        outcome = 'refused'
    pathlib.Path(sys.argv[2]).write_text(outcome)
""")

# A computation that records its own PID, for a shell that cannot report it (Git Bash).
COMPUTATION = textwrap.dedent("""
    import os, pathlib, sys, time
    pathlib.Path(sys.argv[1]).write_text(str(os.getpid()))
    time.sleep(120)
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
    def run_turn(self, shell, hosted=True):
        """Run the stand-in turn under the production session host, from the files dispatch leaves
        for it, or directly without a host for the control. `shell` builds the shell's command line
        from the folder and the file the computation's outcome goes to. Returns the containment the
        host recorded (None without a host) and the computation's PID, or None when the system
        refused to start it."""
        folder = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, folder, True)
        outcome = folder / 'orphan.pid'
        argv = [sys.executable, '-c', CLI, str(folder), *shell(folder, outcome)]
        if hosted:
            write_json(folder / 'launch.json', {'runner': process_identity(os.getpid()),
                                                'command': {'argv': argv, 'cwd': str(folder)}})
            (folder / 'prompt.txt').write_bytes(b'')
            (folder / 'GO').write_bytes(b'go\n')
            argv = [sys.executable, '-B', str(RUNTIME / 'runner.py'), '_session', str(folder)]
        process = subprocess.Popen(argv, cwd=folder, creationflags=subprocess.CREATE_NO_WINDOW)
        self.addCleanup(lambda: process.poll() is None and process.kill())
        self.assertTrue(wait_for(lambda: outcome.is_file() and outcome.read_text(), 60))
        orphan = None if outcome.read_text() == 'refused' else int(outcome.read_text())
        if orphan is not None:
            self.addCleanup(kill_if_alive, orphan)
            # The shell that started it has ended; only job membership can still tie it to the session.
            time.sleep(0.5)
            self.assertIsNotNone(process_identity(orphan), 'the computation runs while its session lives')
        (folder / 'release').write_text('')
        self.assertEqual(process.wait(timeout=60), 0)
        return (read_json(folder / 'process-job.json')['contained'] if hosted else None), orphan

    @staticmethod
    def python_shell(launch):
        return lambda folder, outcome: [sys.executable, '-c', SHELL, str(RUNTIME), str(outcome), launch]

    @staticmethod
    def git_bash_shell(folder, outcome):
        # Git Bash starting a native program in the background, as a session's shell does.
        script = folder / 'computation.py'
        script.write_text(COMPUTATION)
        command = ' '.join(f'"{Path(part).as_posix()}"' for part in (sys.executable, script, outcome))
        return [str(GIT_BASH), '-c', command + ' &']

    def test_a_detached_computation_ends_with_its_session_host(self):
        contained, orphan = self.run_turn(self.python_shell('detached'))
        self.assertTrue(contained)
        self.assertTrue(wait_for(lambda: process_identity(orphan) is None, 10),
                        'the detached computation outlived its session host')

    def test_without_a_host_the_detached_computation_survives(self):
        # Control: the stand-in turn reproduces the leak that the host's containment closes.
        _, orphan = self.run_turn(self.python_shell('detached'), hosted=False)
        time.sleep(1)
        self.assertIsNotNone(process_identity(orphan))

    def test_a_request_to_leave_the_job_is_refused_inside_a_session(self):
        # The request the broker client makes. A job that granted it would also grant it to Git
        # Bash, which asks on every program it starts where its job permits, so the session's job
        # grants it to nothing.
        contained, orphan = self.run_turn(self.python_shell('breakaway'))
        self.assertTrue(contained)
        self.assertIsNone(orphan, 'a process started inside a session left its job')

    @unittest.skipUnless(GIT_BASH.is_file(), 'Git Bash')
    def test_a_computation_started_from_git_bash_ends_with_its_session_host(self):
        # The leak observed in a running instance: computations a session ran from its shell were
        # outside the job and outlived the session.
        contained, orphan = self.run_turn(self.git_bash_shell)
        self.assertTrue(contained)
        self.assertTrue(wait_for(lambda: process_identity(orphan) is None, 10),
                        'a computation started from Git Bash outlived its session host')


class BrokerClientTests(unittest.TestCase):
    """The production client up to the process boundary (lean_broker.ensure_broker)."""

    def paths(self):
        folder = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, folder, True)
        (folder / 'runner').mkdir()
        return lean_broker.Paths(folder)

    @staticmethod
    def started(paths):
        # The receipt a started broker writes; this live process stands in for the broker.
        write_json(paths.process, {'process': process_identity(os.getpid())})

    def test_a_client_outside_a_session_starts_the_broker_asking_to_leave_its_job(self):
        paths, requests = self.paths(), []

        def start(argv, **options):
            requests.append(options)
            self.started(paths)

        with patch.object(lean_broker.subprocess, 'Popen', side_effect=start):
            info = lean_broker.ensure_broker(paths)
        self.assertEqual(info['process'], process_identity(os.getpid()))
        expected = popen_options(detached=True, breakaway=True)
        self.assertEqual([{key: options.get(key) for key in expected} for options in requests], [expected])

    def test_a_client_refused_as_in_a_session_starts_nothing_and_takes_the_runners_broker(self):
        # A session's job refuses the request to leave it (the containment test above). The client
        # must not then start the broker inside that job, where it would end with the session; the
        # runner starts one, which the client finds.
        paths, requests = self.paths(), []

        def start(argv, **options):
            requests.append(options)
            raise PermissionError('this job forbids breakaway')

        runner = threading.Timer(0.3, self.started, [paths])
        runner.start()
        self.addCleanup(runner.cancel)
        with patch.object(lean_broker.subprocess, 'Popen', side_effect=start):
            info = lean_broker.ensure_broker(paths)
        self.assertEqual(info['process'], process_identity(os.getpid()))
        self.assertEqual(len(requests), 1, 'the refused client started a broker inside its job')

    def test_a_refused_client_says_that_the_runner_starts_the_broker_when_none_appears(self):
        paths, requests = self.paths(), []

        def start(argv, **options):
            requests.append(options)
            raise PermissionError('this job forbids breakaway')

        with patch.object(lean_broker.subprocess, 'Popen', side_effect=start), \
                patch.object(lean_broker, 'READY_SECONDS', 0.3), \
                self.assertRaises(RuntimeError) as raised:
            lean_broker.ensure_broker(paths)
        self.assertEqual(len(requests), 1)
        self.assertIn('the runner starts', str(raised.exception))
        self.assertIn('wait on it again', str(raised.exception))

    def test_a_client_whose_start_was_not_refused_is_sent_to_the_brokers_log_when_none_appears(self):
        # Outside a session the start is not refused. When no broker is alive after it, the broker's own
        # output is the only place that says what became of it, and the client names that file.
        paths, requests = self.paths(), []

        def start(argv, **options):
            requests.append(options)

        with patch.object(lean_broker.subprocess, 'Popen', side_effect=start), \
                patch.object(lean_broker, 'READY_SECONDS', 0.3), \
                self.assertRaises(RuntimeError) as raised:
            lean_broker.ensure_broker(paths)
        self.assertEqual(len(requests), 1)
        self.assertIn('became ready', str(raised.exception))
        self.assertIn(str(paths.log), str(raised.exception))


if __name__ == '__main__':
    unittest.main()

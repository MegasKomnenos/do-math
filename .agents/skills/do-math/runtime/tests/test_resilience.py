import contextlib
import ctypes
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parent)]
import lean_broker
import runner as runtime
import runtime_support as support
from broker_fixture import BrokerFixture
from support import InstanceCase


APPROACH = '''---
title: Induction on the number of terms
sessions: sauthor
---
## Idea

Compare the sum for n + 1 with the sum for n.

## Where it stops

The arithmetic identity of the inductive step has not been checked.
'''


# LaunchFailureTests runs a session host inside the test process. The real host puts its own process into
# a job that nothing can leave, after which this process could no longer start a Lean broker for the tests
# that follow in the same run (lean_broker.ensure_broker). A stand-in answers for the containment here;
# the containment itself is tested on real host processes in test_containment.
CONTAINMENT = patch('runtime_support.contain_session_processes', return_value={'contained': True})


def setUpModule():
    CONTAINMENT.start()


def tearDownModule():
    CONTAINMENT.stop()


def windows_error(code):
    error = OSError('injected filesystem failure')
    error.winerror = code
    return error


class DirectoryRenameTests(unittest.TestCase):
    def test_existing_destination_is_never_replaced(self):
        with tempfile.TemporaryDirectory() as temp:
            source, target = Path(temp) / 'stage', Path(temp) / 'published'
            source.mkdir()
            target.mkdir()
            (source / 'evidence').write_text('original')
            with self.assertRaises(FileExistsError):
                support.rename_directory(source, target)
            self.assertEqual((source / 'evidence').read_text(), 'original')
            self.assertEqual(list(target.iterdir()), [])

    def test_missing_source_fails_without_retry(self):
        with tempfile.TemporaryDirectory() as temp, patch('runtime_support.time.sleep') as sleep:
            with self.assertRaises(FileNotFoundError):
                support.rename_directory(Path(temp) / 'missing', Path(temp) / 'target')
            sleep.assert_not_called()

    @unittest.skipUnless(os.name == 'nt', 'Windows sharing semantics')
    def test_retryable_errors_are_bounded_and_propagated(self):
        for code in (5, 32, 33):
            with self.subTest(winerror=code), tempfile.TemporaryDirectory() as temp:
                source, target = Path(temp) / 'stage', Path(temp) / 'target'
                source.mkdir()
                (source / 'evidence').write_text('retained')
                error = windows_error(code)
                with patch('runtime_support.os.rename', side_effect=error) as rename, \
                        patch('runtime_support.time.monotonic', side_effect=[0, 0, 59, 60]), \
                        patch('runtime_support.time.sleep') as sleep:
                    with self.assertRaises(OSError) as caught:
                        support.rename_directory(source, target)
                self.assertIs(caught.exception, error)
                self.assertEqual(rename.call_count, 3)
                self.assertEqual(sleep.call_count, 2)
                self.assertEqual((source / 'evidence').read_text(), 'retained')
                self.assertFalse(target.exists())

    @unittest.skipUnless(os.name == 'nt', 'Windows sharing semantics')
    def test_real_open_file_blocks_rename_until_handle_is_closed(self):
        from ctypes import wintypes
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                      ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
        kernel.CreateFileW.restype = wintypes.HANDLE
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        with tempfile.TemporaryDirectory() as temp:
            source, target = Path(temp) / 'stage', Path(temp) / 'target'
            source.mkdir()
            (source / 'evidence').write_text('retained')
            handle = kernel.CreateFileW(str(source / 'evidence'), 0x80000000, 3, None, 3, 0, None)
            if handle == ctypes.c_void_p(-1).value:
                raise ctypes.WinError(ctypes.get_last_error())
            closed = False

            def release(_):
                nonlocal closed
                self.assertTrue(source.exists())
                self.assertFalse(target.exists())
                if not closed:
                    kernel.CloseHandle(handle)
                    closed = True

            try:
                with patch('runtime_support.time.sleep', side_effect=release) as sleep:
                    support.rename_directory(source, target)
                self.assertGreaterEqual(sleep.call_count, 1)
                self.assertEqual((target / 'evidence').read_text(), 'retained')
                self.assertFalse(source.exists())
            finally:
                if not closed:
                    kernel.CloseHandle(handle)


class StateFileSharingTests(unittest.TestCase):
    # Every state and view file is written through write_json or write_text and read through read_json or read_bytes.
    # On Windows a reader holding the destination without delete sharing fails the replacement, and one
    # holding the file without read sharing fails the read; both calls wait for the handle instead.
    @unittest.skipUnless(os.name == 'nt', 'Windows sharing semantics')
    def test_replacement_waits_for_a_held_destination_and_keeps_the_complete_version(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'state.json'
            support.write_json(path, {'version': 1})
            replace = os.replace
            held = [windows_error(5), windows_error(32)]

            def held_destination(source, destination):
                if held:
                    # Meanwhile readers still see the complete earlier version.
                    self.assertEqual(support.read_json(path), {'version': 1})
                    raise held.pop(0)
                replace(source, destination)

            with patch('runtime_support.os.replace', side_effect=held_destination), \
                    patch('runtime_support.time.sleep') as sleep:
                support.write_json(path, {'version': 2})
            self.assertEqual(sleep.call_count, 2)
            self.assertEqual(support.read_json(path), {'version': 2})
            self.assertEqual(list(Path(temp).iterdir()), [path])

    @unittest.skipUnless(os.name == 'nt', 'Windows sharing semantics')
    def test_read_waits_for_a_held_file_and_does_not_retry_other_refusals(self):
        from ctypes import wintypes
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                      ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
        kernel.CreateFileW.restype = wintypes.HANDLE
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'state.json'
            support.write_json(path, {'version': 1})
            # A real handle that shares the file with no reader. Python's open reports the refusal as errno 13
            # without a Windows error code, and read_json has to wait on the error in that form.
            handle = kernel.CreateFileW(str(path), 0x80000000, 0, None, 3, 0, None)
            if handle == ctypes.c_void_p(-1).value:
                raise ctypes.WinError(ctypes.get_last_error())
            closed = False

            def release(_):
                nonlocal closed
                if not closed:
                    kernel.CloseHandle(handle)
                    closed = True

            try:
                with patch('runtime_support.time.sleep', side_effect=release) as sleep:
                    self.assertEqual(support.read_json(path), {'version': 1})
                self.assertGreaterEqual(sleep.call_count, 1)
            finally:
                if not closed:
                    kernel.CloseHandle(handle)
            # A refusal that carries another Windows error code is no held file and is raised at once.
            refused = PermissionError('injected privilege refusal')
            refused.winerror = 1314
            with patch.object(Path, 'read_text', side_effect=refused), patch('runtime_support.time.sleep') as sleep:
                with self.assertRaises(PermissionError) as caught:
                    support.read_json(path)
                self.assertIs(caught.exception, refused)
                sleep.assert_not_called()


class InstanceLockTests(unittest.TestCase):
    def test_a_lock_asked_for_with_a_wait_is_taken_once_its_holder_lets_it_go(self):
        # The coordination commands of all sessions and the runner's launch of an explorer meet at one lock
        # and wait up to thirty seconds for it (coordination.claims_lock). Only the pause of that wait is
        # replaced: at the first pause the holder lets the lock go, as a command that has finished does.
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'claims.lock'
            holder = support.InstanceLock(path)
            holder.__enter__()
            pauses = []

            def let_go(seconds):
                if not pauses:
                    holder.__exit__(None, None, None)
                pauses.append(seconds)

            try:
                with patch('runtime_support.time.sleep', side_effect=let_go), support.InstanceLock(path, wait=30.0):
                    self.assertEqual(len(pauses), 1)
                    # The one that waited holds the lock now: a request without a wait is refused at once.
                    with self.assertRaisesRegex(RuntimeError, 'already has a running runner'):
                        support.InstanceLock(path).__enter__()
            finally:
                if not pauses:
                    holder.__exit__(None, None, None)


class ProcessIdentityTests(unittest.TestCase):
    @unittest.skipIf(os.name == 'nt', 'the process files of Linux')
    def test_a_process_reaped_while_its_stat_file_is_read_is_gone(self):
        # Linux answers a read of /proc/<pid>/stat with ESRCH when the process was reaped after the file
        # was opened. That process is gone, which None says; an error raised here would reach the passes
        # of the runner and of the broker, which ask about every process they follow.
        own = support.process_identity(os.getpid())
        self.assertEqual(own['pid'], os.getpid())
        with patch.object(Path, 'read_bytes', side_effect=ProcessLookupError(3, 'No such process')):
            self.assertIsNone(support.process_identity(os.getpid()))
            self.assertFalse(support.alive(own))

    @unittest.skipIf(os.name == 'nt', 'the process files of Linux')
    def test_a_process_whose_name_is_not_text_has_an_identity(self):
        # /proc/<pid>/stat holds the name a process gave itself: up to 15 bytes that need not be UTF-8 and may
        # hold a closing parenthesis. A recorded number can come to any process of the machine, and the runner
        # asks about it on every pass, so such a name must not raise.
        stat = b'77 (\xff\xfe) x) S 1 77 77 0 -1 4194560 0 0 0 0 0 0 0 0 20 0 1 0 12345 0 0'
        with patch.object(Path, 'read_bytes', return_value=stat), patch.object(Path, 'read_text', return_value='boot\n'):
            self.assertEqual(support.process_identity(77), {'pid': 77, 'birth': 'boot:12345'})

    @unittest.skipUnless(os.name == 'nt', 'the refusal is what Windows answers for a process this account may not open')
    def test_a_recorded_process_whose_number_went_to_a_process_that_cannot_be_opened_is_not_alive(self):
        # A recorded identity outlives its process, and after a reboot its number can belong to a process of
        # the system or of another account, which Windows refuses to open with access denied. Only that answer
        # is stood in for. The recorded process is then not alive, so the runner that is started again collects
        # its session (Runner.collect); a refusal passed on would end that runner at every start.
        recorded = {'pid': os.getpid(), 'birth': 'a process from before the reboot'}

        def refused(access, inherit, pid):
            ctypes.set_last_error(5)  # ERROR_ACCESS_DENIED
            return None

        with patch.object(support.WIN, 'OpenProcess', side_effect=refused) as asked:
            self.assertFalse(support.alive(recorded))
        self.assertTrue(asked.called)

    def test_a_process_that_holds_the_number_of_a_recorded_one_is_not_terminated(self):
        # A recorded identity outlives its process, and the system gives the number to a later process.
        # kill-session, the stop of a broker and the cancellation of a compile all end a process through
        # terminate_process, which compares the creation identity on the handle it terminates through. The
        # identity given first has the number of a live process and another creation identity, as the record
        # of an earlier process with that number has.
        other = subprocess.Popen([sys.executable, '-c', 'import sys; sys.stdin.read()'], stdin=subprocess.PIPE,
                                 **support.popen_options())
        self.addCleanup(other.wait)
        self.addCleanup(other.stdin.close)  # the process ends when its input ends
        present = support.process_identity(other.pid)
        with self.assertRaisesRegex(RuntimeError, 'not terminated'):
            support.terminate_process({**present, 'birth': 'an earlier process with this number'})
        self.assertIsNone(other.poll())
        self.assertTrue(support.alive(present))
        # With the identity of the process itself, the same call ends it.
        support.terminate_process(present)
        other.wait(timeout=30)
        self.assertFalse(support.alive(present))


class GitEnvironmentTests(unittest.TestCase):
    def test_a_repository_named_in_the_callers_environment_does_not_receive_the_instances_commits(self):
        # A command of the runtime can be started where GIT_DIR names another repository, as inside a Git hook,
        # and the runner keeps the environment it was started with. Every publication commits through
        # support.git (Runner.publish), so with that variable passed on, the commits would go into the other
        # repository. Both repositories and every Git call are real; only the variable is set.
        with tempfile.TemporaryDirectory() as temp:
            instance, other = Path(temp) / 'instance', Path(temp) / 'other'
            for folder in (instance, other):
                folder.mkdir()
                support.git(folder, 'init')
            (instance / 'root.md').write_text('The root.\n', encoding='utf-8')
            with patch.dict(os.environ, {'GIT_DIR': str(other / '.git')}):
                support.git(instance, 'add', '--', 'root.md')
                support.git(instance, 'commit', '-m', 'In the instance')
            self.assertEqual(support.git(instance, 'log', '--format=%s'), 'In the instance')
            self.assertEqual(support.git(other, 'count-objects'), '0 objects, 0 kilobytes')

    def test_a_callers_setting_that_signs_every_commit_does_not_stop_the_instances_commits(self):
        # The repository of an instance is the runtime's own record: init makes its first commit, and the runner,
        # which nobody attends, one for every publication (Runner.publish), all under the runtime's name. A
        # user's Git configuration can ask for every commit to be signed. Git would then start the signing
        # program for these commits as well, which finds no key for that name or waits for a passphrase. Git
        # reads that configuration from the home folder, which is given here with the setting and with a signing
        # program that does not exist, so a commit that Git tried to sign fails. The repository and every Git
        # call are real.
        with tempfile.TemporaryDirectory() as temp:
            home, instance = Path(temp) / 'home', Path(temp) / 'instance'
            for folder in (home, instance):
                folder.mkdir()
            (home / '.gitconfig').write_text(
                '[commit]\n\tgpgsign = true\n[gpg]\n\tprogram = no-such-signing-program\n', encoding='utf-8')
            (instance / 'root.md').write_text('The root.\n', encoding='utf-8')
            with patch.dict(os.environ, {'HOME': str(home), 'USERPROFILE': str(home),
                                         'XDG_CONFIG_HOME': str(home / 'xdg')}):
                # Git reads the file as the user's configuration; without that the commit below would show nothing.
                self.assertEqual(support.git(instance, 'config', '--global', 'commit.gpgsign'), 'true')
                support.git(instance, 'init')
                support.git(instance, 'add', '--', 'root.md')
                support.git(instance, 'commit', '-m', 'In the instance')
            self.assertEqual(support.git(instance, 'log', '--format=%s'), 'In the instance')


class PeerRecoveryTests(InstanceCase):
    def peer(self):
        engine = runtime.Runner(self.instance, self.skill)
        producer = engine.producer('attempt')
        pipeline = engine.state['jobs'][producer]['pipeline']
        engine.state['pipelines'][pipeline].update(producer='sauthor', peer='speer', stage='peer')
        key = engine.enqueue('peer', {}, pipeline, pipeline + ':peer')
        folder = engine.session_dir('speer')
        # The peer's change holds an approach entry and no Lean, so its receipt needs no build.
        candidate = self.candidate(approaches={'Small/root/induction.md': APPROACH}, prepare=False)
        folder.mkdir(parents=True)
        candidate.rename(folder / 'output')
        self.prepare(folder / 'output')
        support.write_json(folder / 'input.json', {
            'instance': str(self.instance), 'session': 'speer', 'role': 'peer', 'pipeline': pipeline, 'task': {},
        })
        engine.state['sessions']['speer'] = {
            'id': 'speer', 'role': 'peer', 'job': key, 'status': 'running',
            'provider': 'codex', 'model': 'codex/gpt-6.1-sol', 'started_at': 1,
            'exit_code': 0, 'retained': True, 'retention': {'cli_activity': True, 'native_activity': False},
        }
        engine.state['jobs'][key].update(status='running', session='speer')
        engine.save()
        return engine, key, pipeline

    def check_fatal_then_recover(self, operation):
        engine, key, pipeline = self.peer()
        stderr = io.StringIO()

        def finish():
            engine.finish('speer', engine.state['sessions']['speer'])

        with patch(operation, side_effect=PermissionError('injected persistent failure')), \
                patch.object(engine, 'tick', side_effect=finish) as tick, \
                contextlib.redirect_stderr(stderr):
            with self.assertRaisesRegex(PermissionError, 'injected persistent failure'):
                engine.run()
        self.assertEqual(tick.call_count, 1)
        self.assertIn('Traceback (most recent call last)', stderr.getvalue())
        saved = support.read_json(engine.state_path)
        # The runner state's top-level last_error holds the failure and its time for status,
        # apart from the errors of individual jobs (reference/operations.md).
        self.assertEqual(saved['last_error']['error'], 'injected persistent failure')
        self.assertIsInstance(saved['last_error']['at'], float)
        self.assertEqual(saved['sessions']['speer']['status'], 'running')
        self.assertEqual(saved['jobs'][key]['status'], 'running')
        self.assertEqual(saved['pipelines'][pipeline]['stage'], 'peer')
        self.assertFalse(any(j['role'] == 'review' for j in saved['jobs'].values()))

        recovered = runtime.Runner(self.instance, self.skill)
        recovered.finish('speer', recovered.state['sessions']['speer'])
        recovered.finish('speer', recovered.state['sessions']['speer'])
        reviews = [j for j in recovered.state['jobs'].values() if j['role'] == 'review']
        self.assertEqual(len(reviews), 1)
        candidate = recovered.session_dir('speer') / 'candidate'
        self.assertEqual(reviews[0]['task']['candidate_hashes'], runtime.tree_hashes(candidate))
        self.assertEqual(runtime.tree_hashes(candidate), runtime.tree_hashes(recovered.session_dir('speer') / 'output'))
        self.assertEqual((candidate / 'approaches/Small/root/induction.md').read_text(encoding='utf-8'), APPROACH)
        self.assertEqual(recovered.state['jobs'][key]['status'], 'done')

    def test_hash_read_failure_is_fatal_and_does_not_strand_peer(self):
        self.check_fatal_then_recover('runner.tree_hashes')

    def test_rename_failure_is_fatal_and_restart_creates_one_review(self):
        self.check_fatal_then_recover('runner.rename_directory')


class RecordedFailureTests(InstanceCase):
    def test_a_failure_of_any_kind_is_recorded_before_the_runner_ends(self):
        # A failed read or write raises an OSError. A file whose content has another shape than the runner
        # reads raises a TypeError or an AttributeError. Whatever its kind, the error that ends the runner is
        # in last_error for status, and its call stack is in the stderr log (reference/operations.md). What the
        # runner prints on standard output is caught as a stream: traceback writes the call stack with print,
        # so a stand-in for print would keep the stack out of the log.
        engine = runtime.Runner(self.instance, self.skill)
        stderr = io.StringIO()
        with patch.object(engine, 'tick', side_effect=TypeError('injected failure of another kind')), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(stderr), \
                self.assertRaisesRegex(TypeError, 'injected failure of another kind'):
            engine.run()
        self.assertIn('Traceback (most recent call last)', stderr.getvalue())
        self.assertEqual(support.read_json(engine.state_path)['last_error']['error'],
                         'injected failure of another kind')


class MemoryReserveTests(InstanceCase):
    def test_lack_of_memory_pauses_every_pass_until_free_memory_returns(self):
        # Running out of memory does not end the runner (reference/operations.md, Restarts, runner
        # failures and installation updates). It releases its reserve and makes no pass while free memory
        # stays below 512 MiB; once free memory reaches 512 MiB it takes the reserve back, reloads its
        # saved state and the published research, and continues without recording last_error. Runner.run
        # is the runner's own loop; only the failing pass and the machine's free memory are injected.
        engine = runtime.Runner(self.instance, self.skill)
        free = iter([256 * 1024 * 1024, 512 * 1024 * 1024])
        passes = []

        def tick():
            passes.append((engine.reserve.buffer is not None, engine.state))
            if len(passes) == 1:
                engine.state['explore_requested'] = True  # an unsaved change of the pass that fails
                raise MemoryError
            return True

        with patch.object(engine, 'tick', side_effect=tick), \
                patch('runner.available_memory', side_effect=lambda: next(free)), \
                patch('runner.replay', wraps=runtime.replay) as reload, \
                patch('runner.time.sleep') as sleep, \
                patch('runtime_support.os.write') as written, \
                patch('builtins.print'):
            engine.run()
        written.assert_called_once_with(2, b'Runner memory reserve released; dispatch will wait for recovery.\n')
        # No pass ran while free memory was below 512 MiB; the next one held the reserve again.
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [0.25, 5])
        self.assertEqual([held for held, _ in passes], [True, True])
        # The state and the published research were read again, so the failed pass's change is gone.
        self.assertFalse(passes[1][1]['explore_requested'])
        self.assertEqual(reload.call_count, 1)
        self.assertIsNone(support.read_json(engine.state_path)['last_error'])

    def test_a_save_that_fails_for_lack_of_memory_is_made_again_once_the_reserve_is_released(self):
        # Runner.save writes once more after it has released the reserve (runtime_support.EmergencyMemory), so
        # the state of the failing pass still reaches the disk. With the reserve already released there is
        # nothing left to free, and the failure goes up to the runner's loop.
        engine = runtime.Runner(self.instance, self.skill)
        engine.reserve = support.EmergencyMemory(1024)
        engine.state['explore_requested'] = True
        write, failures = support.write_json_compact, [MemoryError()]

        def short_of_memory(path, value):
            if failures:
                raise failures.pop()
            return write(path, value)

        with patch('runner.write_json_compact', side_effect=short_of_memory) as written, \
                patch('runtime_support.os.write') as notice:
            engine.save()
        self.assertEqual(written.call_count, 2)
        self.assertIsNone(engine.reserve.buffer)
        notice.assert_called_once_with(2, b'Runner memory reserve released; dispatch will wait for recovery.\n')
        self.assertTrue(support.read_json(engine.state_path)['explore_requested'])
        failures.append(MemoryError())
        with patch('runner.write_json_compact', side_effect=short_of_memory) as written, self.assertRaises(MemoryError):
            engine.save()
        self.assertEqual(written.call_count, 1)


class LaunchFailureTests(InstanceCase):
    def test_a_cli_that_cannot_start_moves_the_retry_to_the_next_model(self):
        # Nothing stands in for the CLI: its configured executable is missing, so the session host's
        # launch fails as it would in operation. That is an operational failure of the selected model,
        # unlike invalid output, so the job's replacement takes the role's next model while this one
        # is blocked (reference/operations.md). Only the host's spawn is replaced; the host itself runs
        # in this process, as in test_ending.
        engine = runtime.Runner(self.instance, self.skill)
        engine.settings['cli']['codex'] = str(self.root / 'missing' / 'codex.exe')
        key = engine.enqueue('organizer', {})
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = engine.identity['pid']
            self.assertTrue(engine.dispatch(key))
        sid = engine.state['jobs'][key]['session']
        session = engine.state['sessions'][sid]
        self.assertEqual(session['model'], 'codex/gpt-6.1-sol')
        self.assertEqual(support.session_host(engine.session_dir(sid)), 0)
        session['host'] = None  # the host ran in this process and has returned
        engine.collect()
        job = engine.state['jobs'][key]
        self.assertEqual((session['status'], job['status']), ('failed', 'pending'))
        self.assertTrue(session['launch_error'])
        self.assertEqual(job['last_error'], session['launch_error'])
        self.assertEqual(support.read_json(engine.session_dir(sid) / 'termination.json')['cause'], 'launch_error')
        self.assertEqual(engine.state['blocks']['model:codex/gpt-6.1-sol']['source'], 'retry')
        # The block lasts retry_seconds, one second in the fixture, so the choice is read at an instant within it.
        block = engine.state['blocks']['model:codex/gpt-6.1-sol']
        with patch('runner.time.time', return_value=block['until'] - 0.5):
            self.assertEqual(engine.selection('organizer')['model'], 'claude/opus')

    def test_a_host_that_cannot_be_started_is_a_failed_launch_of_the_selected_model(self):
        # One step earlier than above: the runner cannot start the session host itself. The session never
        # receives its GO, and when the runner collects it, the failed launch counts against the model as a
        # CLI that cannot start does, so the job's replacement takes the role's next model.
        engine = runtime.Runner(self.instance, self.skill)
        key = engine.enqueue('organizer', {})
        with patch('runner.subprocess.Popen', side_effect=OSError('injected host start failure')):
            self.assertTrue(engine.dispatch(key))
        sid = engine.state['jobs'][key]['session']
        session, folder = engine.state['sessions'][sid], engine.session_dir(sid)
        self.assertEqual((session['status'], session['host'], session['launch_error']),
                         ('starting', None, 'injected host start failure'))
        self.assertEqual(((folder / 'GO').exists(), (folder / 'CANCEL').exists()), (False, True))
        engine.collect()
        job = engine.state['jobs'][key]
        self.assertEqual((session['status'], job['status'], job['last_error']),
                         ('failed', 'pending', 'injected host start failure'))
        self.assertEqual(support.read_json(folder / 'termination.json')['cause'], 'launch_error')
        block = engine.state['blocks']['model:codex/gpt-6.1-sol']
        self.assertEqual(block['source'], 'retry')
        with patch('runner.time.time', return_value=block['until'] - 0.5):
            self.assertEqual(engine.selection('organizer')['model'], 'claude/opus')

    def test_a_session_saved_before_its_gate_was_opened_is_cancelled_when_it_is_collected(self):
        # dispatch records the host in the runner's state and only then opens the session's gate by writing GO.
        # A runner that ended between the two left a session whose host started no CLI. The runner that collects
        # that session cancels it, on which a host that still waits ends (test_ending.SessionGateTests). The
        # launch never took place, so its retry is that of a cancellation and blocks no model.
        engine = runtime.Runner(self.instance, self.skill)
        key = engine.producer('attempt')
        with patch('runner.subprocess.Popen') as host:
            host.return_value.pid = engine.identity['pid']
            self.assertTrue(engine.dispatch(key))
        sid = engine.state['jobs'][key]['session']
        folder = engine.session_dir(sid)
        (folder / 'GO').unlink()  # the state that runner saved: the host recorded, the gate not yet opened
        recovered = runtime.Runner(self.instance, self.skill)
        recovered.collect()
        session = recovered.state['sessions'][sid]
        # The recorded host is this test's own process, which is alive: the session is cancelled, not yet collected.
        self.assertTrue((folder / 'CANCEL').exists())
        self.assertEqual(session['status'], 'running')
        session['host'] = None  # the waiting host has ended
        recovered.collect()
        job = recovered.state['jobs'][key]
        self.assertEqual((session['status'], job['status'], job['last_error']),
                         ('failed', 'pending', 'session ended without retained research material'))
        # The next attempt of this job continues nothing, so its assignment carries no word of the failed launch.
        self.assertNotIn('previous_error', job['task'])
        self.assertEqual(recovered.state['blocks'], {})


class HeldCanonFileTests(InstanceCase):
    @unittest.skipUnless(os.name == 'nt', 'Windows sharing semantics')
    def test_a_question_text_that_a_reader_holds_open_is_moved_once_the_reader_closes_it(self):
        # Sessions read the canon while the runner publishes, and Windows refuses to move a file that a reader
        # holds open without delete sharing, as Python's open does. The runner then waits for the handle, as it
        # does when it replaces a state file. An organizer merges op-a, whose understanding text is held open,
        # into op-b, which has none, so the publication moves that text to the place of op-b's.
        self.questions('qops', [{'id': name, 'statement': f'What does {name} ask?', 'grounds': 'Unexplained.'}
                                for name in ('op-a', 'op-b')])
        folder = self.candidate(understanding={'op-a.md': 'Each odd number completes the next square.\n'})
        _, engine = self.publish(folder, role='explore', question='op-a')
        source, target = (self.instance / 'canon/questions' / name for name in ('op-a.md', 'op-b.md'))
        text = source.read_text(encoding='utf-8')
        held = source.open('rb')
        self.addCleanup(held.close)
        with patch('runtime_support.time.sleep', side_effect=lambda seconds: held.close()) as waited:
            self.organize(merge_questions=[{'from': 'op-a', 'into': 'op-b', 'reason': 'Both ask the same thing.'}],
                          engine=engine)
        self.assertTrue(waited.called)
        self.assertFalse(source.exists())
        self.assertEqual(target.read_text(encoding='utf-8'), text)


class LoadedAtStartTests(unittest.TestCase):
    def test_a_process_started_from_the_runner_script_holds_every_module_its_functions_import(self):
        # The runner and a session host keep for hours the modules they loaded at their start
        # (reference/operations.md, Restarts, runner failures and installation updates). An import inside a
        # function is carried out when the function first runs, for a host when it checks its session's output
        # at the end. A module first loaded then comes from the installed files as they have become, and fails
        # where it names something that the modules loaded at the start do not have. So a fresh process that
        # has imported runner.py, as the runner, a session host and the archiver do, already holds every module
        # of the runtime folder that a function of a loaded module imports.
        probe = '\n'.join([
            'import ast, sys',
            'from pathlib import Path',
            'runtime = Path(sys.argv[1])',
            'sys.path.insert(0, str(runtime))',
            'import runner',
            'late = set()',
            "for loaded in [name for name in list(sys.modules) if (runtime / (name + '.py')).is_file()]:",
            "    tree = ast.parse((runtime / (loaded + '.py')).read_text(encoding='utf-8'))",
            '    for function in ast.walk(tree):',
            '        if isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):',
            '            for node in ast.walk(function):',
            '                if isinstance(node, ast.ImportFrom):',
            '                    named = [node.module]',
            '                elif isinstance(node, ast.Import):',
            '                    named = [alias.name for alias in node.names]',
            '                else:',
            '                    continue',
            '                late.update(name for name in named',
            "                            if name and name not in sys.modules and (runtime / (name + '.py')).is_file())",
            "print(' '.join(sorted(late)))"])
        result = subprocess.run([sys.executable, '-B', '-c', probe, str(Path(runtime.__file__).resolve().parent)],
                                capture_output=True, text=True, timeout=120)
        self.assertEqual((result.returncode, result.stdout.strip()), (0, ''), result.stderr)


class BrokerRelaunchTests(BrokerFixture):
    def test_runner_launches_adopts_and_relaunches_the_broker(self):
        # Runner.ensure_broker alone is under test. A Runner is built around an initialized instance with
        # its compiled canon; ensure_broker reads only the instance's path and the two fields set here.
        def bare_runner():
            engine = runtime.Runner.__new__(runtime.Runner)
            engine.instance, engine.broker, engine.broker_attempt = self.instance, None, 0
            return engine
        engine = bare_runner()
        before = time.monotonic()
        engine.ensure_broker()  # a broker is kept alive whether or not a session exists yet
        self.assertGreaterEqual(engine.broker_attempt, before)  # the launch records its moment for the ten seconds below
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline and not lean_broker.broker_alive(self.paths):
            time.sleep(0.05)
        first = lean_broker.broker_alive(self.paths)
        self.assertTrue(first)
        self.assertTrue(lean_broker.broker_status(self.paths)["broker_alive"])
        other = bare_runner()
        other.ensure_broker()
        self.assertIsNone(other.broker)
        self.assertEqual(lean_broker.broker_alive(self.paths)["process"], first["process"])
        support.terminate_process(first["process"])
        while support.alive(first["process"]):
            time.sleep(0.02)
        # Within ten seconds of the last launch no relaunch is made (runner.ensure_broker). The moment of that
        # launch is set here, so that a machine slow enough to spend those seconds above changes nothing, and the
        # launch itself is watched, because a relaunched broker writes its receipt only seconds later.
        engine.broker_attempt = time.monotonic()
        with patch.object(lean_broker, "launch_broker") as relaunch:
            engine.ensure_broker()
        relaunch.assert_not_called()
        self.assertIsNone(lean_broker.broker_alive(self.paths))
        engine.broker_attempt = float("-inf")
        engine.ensure_broker()
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline and not lean_broker.broker_alive(self.paths):
            time.sleep(0.05)
        second = lean_broker.broker_alive(self.paths)
        self.assertNotEqual(second["process"], first["process"])
        support.terminate_process(second["process"])
        engine.broker.wait(timeout=10)


if __name__ == '__main__':
    unittest.main()

import contextlib
import ctypes
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parent)]
import runner as runtime
import runtime_support as support
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
    def test_unexpected_error_does_not_retry(self):
        with tempfile.TemporaryDirectory() as temp, \
                patch('runtime_support.os.rename', side_effect=windows_error(112)), \
                patch('runtime_support.time.sleep') as sleep:
            with self.assertRaises(OSError):
                support.rename_directory(Path(temp) / 'stage', Path(temp) / 'target')
            sleep.assert_not_called()

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
    # Every state and view file is written through write_json or write_text and read through read_json.
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
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'state.json'
            support.write_json(path, {'version': 1})
            read_text = Path.read_text
            held = []

            def held_source(self, *args, **kwargs):
                if held:
                    raise held.pop(0)
                return read_text(self, *args, **kwargs)

            sharing = PermissionError('injected sharing violation')
            sharing.winerror = 32
            refused = PermissionError('injected privilege refusal')
            refused.winerror = 1314
            with patch.object(Path, 'read_text', held_source), patch('runtime_support.time.sleep') as sleep:
                held.append(sharing)
                self.assertEqual(support.read_json(path), {'version': 1})
                self.assertEqual(sleep.call_count, 1)
                held.append(refused)
                with self.assertRaises(PermissionError) as caught:
                    support.read_json(path)
                self.assertIs(caught.exception, refused)
                self.assertEqual(sleep.call_count, 1)


class ProcessIdentityTests(unittest.TestCase):
    @unittest.skipIf(os.name == 'nt', 'the process files of Linux')
    def test_a_process_reaped_while_its_stat_file_is_read_is_gone(self):
        # Linux answers a read of /proc/<pid>/stat with ESRCH when the process was reaped after the file
        # was opened. That process is gone, which None says; an error raised here would reach the passes
        # of the runner and of the broker, which ask about every process they follow.
        own = support.process_identity(os.getpid())
        self.assertEqual(own['pid'], os.getpid())
        with patch.object(Path, 'read_text', side_effect=ProcessLookupError(3, 'No such process')):
            self.assertIsNone(support.process_identity(os.getpid()))
            self.assertFalse(support.alive(own))

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
        # in last_error for status, and its call stack is in the stderr log (reference/operations.md).
        engine = runtime.Runner(self.instance, self.skill)
        stderr = io.StringIO()
        with patch.object(engine, 'tick', side_effect=TypeError('injected failure of another kind')), \
                patch('builtins.print'), contextlib.redirect_stderr(stderr), \
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
        write_json, failures = support.write_json, [MemoryError()]

        def short_of_memory(path, value):
            if failures:
                raise failures.pop()
            return write_json(path, value)

        with patch('runner.write_json', side_effect=short_of_memory) as written, \
                patch('runtime_support.os.write') as notice:
            engine.save()
        self.assertEqual(written.call_count, 2)
        self.assertIsNone(engine.reserve.buffer)
        notice.assert_called_once_with(2, b'Runner memory reserve released; dispatch will wait for recovery.\n')
        self.assertTrue(support.read_json(engine.state_path)['explore_requested'])
        failures.append(MemoryError())
        with patch('runner.write_json', side_effect=short_of_memory) as written, self.assertRaises(MemoryError):
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


if __name__ == '__main__':
    unittest.main()

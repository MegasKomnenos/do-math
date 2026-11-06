import contextlib
import ctypes
import io
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import runner as runtime
import runtime_support as support
from test_research import InstanceCase, record


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


class PeerRecoveryTests(InstanceCase):
    def peer(self):
        engine = runtime.Runner(self.instance, self.skill)
        producer = engine.producer('attempt')
        pipeline = engine.state['jobs'][producer]['pipeline']
        engine.state['pipelines'][pipeline].update(producer='sauthor', peer='speer', stage='peer')
        key = engine.enqueue('peer', {}, pipeline, pipeline + ':peer')
        folder = engine.session_dir('speer')
        (folder / 'output').mkdir(parents=True)
        support.write_json(folder / 'output/record.json', record())
        (folder / 'output/record.md').write_text('The original evidence.')
        support.write_json(folder / 'input.json', {
            'instance': str(self.instance), 'session': 'speer', 'role': 'peer', 'task': {},
        })
        engine.state['sessions']['speer'] = {
            'id': 'speer', 'role': 'peer', 'job': key, 'status': 'running',
            'provider': 'codex', 'model': 'codex/gpt-6.1-sol', 'started_at': 1,
            'exit_code': 0, 'retained': True, 'retention': {},
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
        self.assertEqual((candidate / 'record.md').read_text(), 'The original evidence.')
        self.assertEqual(recovered.state['jobs'][key]['status'], 'done')

    def test_hash_read_failure_is_fatal_and_does_not_strand_peer(self):
        self.check_fatal_then_recover('runner.tree_hashes')

    def test_rename_failure_is_fatal_and_restart_creates_one_review(self):
        self.check_fatal_then_recover('runner.rename_directory')

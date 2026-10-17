"""File reads, fingerprint-cached hashes (``file_io``) and the per-process artifact match memo (``repository``), layer 2.

The files are real temporary files; the file system is not a port (설계 2.2).
The legacy tests switched off the racy window (``RACY_NS``) and replaced
``sha256_file``; here a file's times are set back past the window
(``storage_files.age``), as a file written long ago has them, and each full
hash is seen by observing ``sha256_file`` (``ObservedCalls``).
"""
import errno
import hashlib
import os
from pathlib import Path
import tempfile
import unittest
import uuid

from do_math import file_io
from do_math.file_io import cached_sha256, file_fingerprint, read_bytes_shared
from do_math.repository import VERIFIED_ARTIFACTS, artifact_key, artifact_verified, verify_artifact
from support.provider_probes import ObservedCalls
from support.storage_files import age


class MetadataPublicationTests(unittest.TestCase):
    def test_missing_read_is_still_absence(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError) as absent:
                read_bytes_shared(Path(directory) / 'missing')
        self.assertEqual(absent.exception.errno, errno.ENOENT)


class FingerprintTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def test_fingerprint_change_alone_triggers_rehash(self):
        path = self.root / 'tool.exe'
        path.write_bytes(b'one')
        age(path, 10)  # creation and modification ten seconds ago: a settled fingerprint
        old = file_fingerprint(path)[1]
        with ObservedCalls(rehash=file_io.sha256_file) as calls:
            self.assertEqual(cached_sha256(path), hashlib.sha256(b'one').hexdigest())
        self.assertEqual(calls.count('rehash'), 1)
        with ObservedCalls(rehash=file_io.sha256_file) as calls:
            self.assertEqual(cached_sha256(path), hashlib.sha256(b'one').hexdigest())
        self.assertEqual(calls.count('rehash'), 0)
        before = file_fingerprint(path)
        path.write_bytes(b'two!')
        os.utime(path, ns=(old + 1, old + 1))
        self.assertNotEqual(file_fingerprint(path), before)
        self.assertEqual(cached_sha256(path), hashlib.sha256(b'two!').hexdigest())
        # Documented limit: content changed with size and times preserved.
        path.write_bytes(b'TWO!')
        os.utime(path, ns=(old + 1, old + 1))
        self.assertEqual(cached_sha256(path), hashlib.sha256(b'two!').hexdigest())

    def test_recent_fingerprint_is_not_cached(self):
        path = self.root / 'fresh.json'
        path.write_bytes(b'a')
        cached_sha256(path)
        with ObservedCalls(rehash=file_io.sha256_file) as calls:
            self.assertEqual(cached_sha256(path), hashlib.sha256(b'a').hexdigest())
        self.assertEqual(calls.count('rehash'), 1)

    def test_verified_artifact_is_scoped_to_repository_and_hash(self):
        raw = b'artifact'
        digest = hashlib.sha256(raw).hexdigest()
        path = 'runtime/artifacts/a/x'
        # Repository identities no other test in this process uses; the memo is process-wide.
        first, second = 'g1-' + uuid.uuid4().hex, 'g2-' + uuid.uuid4().hex
        self.addCleanup(VERIFIED_ARTIFACTS.pop, artifact_key(first, path, digest), None)
        with self.assertRaisesRegex(ValueError, '^artifact evidence missing or hash differs: runtime/artifacts/a/x$'):
            verify_artifact(first, path, b'other', digest)
        self.assertFalse(artifact_verified(first, path, digest))
        verify_artifact(first, path, raw, digest, len(raw))
        self.assertTrue(artifact_verified(first, path, digest))
        self.assertFalse(artifact_verified(second, path, digest))
        # A row declaring another size is not the matched row.
        self.assertTrue(artifact_verified(first, path, digest, len(raw)))
        self.assertFalse(artifact_verified(first, path, digest, len(raw) + 1))


    def test_extended_windows_path_publication_keeps_exact_versions_and_no_temporary(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / '정본.bin'
            raw = b'\x00\xff\r\n' + '원문'.encode('utf-8')
            extended = file_io._windows_path(path)
            self.assertEqual(file_io._windows_path(extended), extended)
            file_io.write_bytes_atomic(extended, b'old', fsync=True)
            with file_io.shared_reader(extended) as previous:
                file_io.write_bytes_atomic(extended, raw, fsync=True)
                self.assertEqual(previous.read(), b'old')
                actual = file_io.read_bytes_shared(extended)
                self.assertIs(type(actual), bytes)
                self.assertEqual(actual, raw)
            self.assertEqual(path.read_bytes(), raw)
            self.assertEqual(list(path.parent.glob(path.name + '.*.tmp')), [])

    def test_physical_boundary_recovers_after_root_disappears_between_stat_and_open(self):
        from support.engine_control import on_audit
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            root, displaced = base / 'boundary', base / 'during-open'
            root.mkdir()
            self.assertEqual((root.resolve().parent, displaced.resolve().parent), (base, base))
            path = root / 'evidence.bin'
            path.write_bytes(b'keep\x00\xff')
            boundary = file_io.PhysicalBoundary(root)
            original_volume = boundary.volume
            observed = []
            def disappear(arguments):
                # The stat check already finished; this lookup precedes the
                # real CreateFileW call. No filesystem/product call is replaced.
                if arguments[1] == 'CloseHandle' and not observed:
                    root.rename(displaced)
                    observed.append(arguments[1])
            try:
                with on_audit('ctypes.dlsym', disappear):
                    with self.assertRaises(FileNotFoundError) as caught:
                        boundary.check()
                self.assertIs(type(caught.exception), FileNotFoundError)
                self.assertEqual(caught.exception.winerror, 2)
                self.assertEqual(caught.exception.errno, errno.ENOENT)
                self.assertEqual(observed, ['CloseHandle'])
                self.assertEqual(boundary.volume, original_volume)
            finally:
                if displaced.exists():
                    displaced.rename(root)
            self.assertIsNone(boundary.check())
            self.assertFalse(displaced.exists())
            self.assertEqual(boundary.volume, original_volume)
            with boundary.open(path, 'rb') as stream:
                self.assertEqual(stream.read(), b'keep\x00\xff')
            moved = root / 'renamed.bin'
            file_io.atomic_replace(path, moved)
            self.assertFalse(path.exists())
            self.assertEqual(moved.read_bytes(), b'keep\x00\xff')



class FileFailureBoundaryTests(unittest.TestCase):
    def test_atomic_replace_retries_same_source_then_publishes_exact_bytes(self):
        import ctypes
        from ctypes import wintypes
        from unittest.mock import patch
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        create = kernel.CreateFileW
        create.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p,
                           wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
        create.restype = wintypes.HANDLE
        close = kernel.CloseHandle; close.argtypes = [wintypes.HANDLE]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, target = root / 'source', root / 'target'
            source.write_bytes(b'exact-new'); target.write_bytes(b'old')
            handle = create(str(source), 0x80000000, 0, None, 3, 0, None)
            self.assertNotEqual(handle, wintypes.HANDLE(-1).value)
            delays = []
            def release(delay):
                delays.append(delay)
                self.assertTrue(source.exists())
                self.assertEqual(target.read_bytes(), b'old')
                close(handle)
            try:
                with patch('time.sleep', side_effect=release):
                    file_io.atomic_replace(source, target)
            finally:
                if not delays: close(handle)
            self.assertEqual(delays, [.01])
            self.assertFalse(source.exists())
            self.assertEqual(target.read_bytes(), b'exact-new')

    def test_permanent_replace_failure_retains_source_and_destination(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, target = root / 'source', root / 'target'
            source.write_bytes(b'recoverable'); target.mkdir()
            with patch('time.sleep') as waits:
                with self.assertRaises(OSError) as caught:
                    file_io.atomic_replace(source, target)
            self.assertEqual([call.args[0] for call in waits.call_args_list], [.01, .025, .05, .1, .2])
            self.assertIn(caught.exception.winerror, {5, 32, 33})
            self.assertEqual(source.read_bytes(), b'recoverable')
            self.assertTrue(target.is_dir())
            with self.assertRaises(FileNotFoundError) as absent:
                file_io.atomic_replace(root / 'missing', root / 'new')
            self.assertEqual(absent.exception.winerror, 2)
            self.assertFalse((root / 'new').exists())

    def test_reader_closes_handle_when_crt_descriptor_conversion_fails(self):
        import ctypes
        from ctypes import wintypes
        from unittest.mock import patch
        handles = []
        def refuse(handle, flags):
            handles.append(handle)
            raise OSError(errno.EMFILE, 'descriptor table full')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'data'; path.write_bytes(b'keep')
            with patch('msvcrt.open_osfhandle', side_effect=refuse):
                with self.assertRaises(OSError) as caught: file_io.read_bytes_shared(path)
            self.assertEqual(caught.exception.errno, errno.EMFILE)
            self.assertEqual(len(handles), 1)
            kernel = ctypes.WinDLL('kernel32', use_last_error=True)
            info = kernel.GetHandleInformation
            info.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
            flags = wintypes.DWORD()
            self.assertEqual(info(handles[0], ctypes.byref(flags)), 0)
            self.assertEqual(ctypes.get_last_error(), 6)
            self.assertEqual(path.read_bytes(), b'keep')

    def test_windows_volume_boundary_rejects_each_external_failure_and_identity_drift(self):
        import ctypes
        from unittest.mock import Mock, patch
        # Replace only selected kernel32 API results, keeping real file handles,
        # no_reparse, stat, and PhysicalBoundary's judgments and cleanup.
        real_dll = ctypes.WinDLL
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            boundary = file_io.PhysicalBoundary(root)
            original = boundary.volume
            for fault, expected in [('final', OSError), ('unc', ValueError), ('volume_path', OSError),
                                    ('drive', ValueError), ('volume_info', OSError), ('filesystem', ValueError),
                                    ('elsewhere', ValueError), ('serial', ValueError)]:
                messages = {'unc': 'storage requires a local fixed NTFS volume',
                    'drive': 'storage requires a local fixed volume', 'filesystem': 'storage requires NTFS',
                    'elsewhere': 'physical directory handle resolves elsewhere', 'serial': 'physical volume identity changed'}
                kernel = real_dll('kernel32', use_last_error=True)
                class Kernel:
                    def __getattr__(self, name): return getattr(kernel, name)
                proxy = Kernel()
                if fault in {'final', 'unc', 'elsewhere'}:
                    def final(handle, buffer, size, flags):
                        if fault == 'final': ctypes.set_last_error(6); return 0
                        buffer.value = ('\\\\?\\UNC\\server\\share' if fault == 'unc' else str(root / 'elsewhere'))
                        return len(buffer.value)
                    proxy.GetFinalPathNameByHandleW = Mock(side_effect=final)
                elif fault == 'volume_path':
                    def unavailable(*args): ctypes.set_last_error(3); return 0
                    proxy.GetVolumePathNameW = Mock(side_effect=unavailable)
                elif fault == 'drive': proxy.GetDriveTypeW = Mock(return_value=4)
                elif fault in {'volume_info', 'filesystem', 'serial'}:
                    real_info = kernel.GetVolumeInformationW
                    from ctypes import wintypes
                    real_info.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD), ctypes.POINTER(wintypes.DWORD), ctypes.POINTER(wintypes.DWORD), wintypes.LPWSTR, wintypes.DWORD]
                    def volume_info(volume, label, size, serial, maximum, flags, fs, fs_size):
                        if fault == 'volume_info': ctypes.set_last_error(5); return 0
                        result = real_info(volume, label, size, serial, maximum, flags, fs, fs_size)
                        if fault == 'filesystem': fs.value = 'FAT32'
                        else: ctypes.cast(serial, ctypes.POINTER(ctypes.c_ulong)).contents.value += 1
                        return result
                    proxy.GetVolumeInformationW = Mock(side_effect=volume_info)
                with self.subTest(fault=fault), patch('ctypes.WinDLL', return_value=proxy):
                    with self.assertRaises(expected) as caught: boundary.check()
                    if fault in messages: self.assertEqual(str(caught.exception), messages[fault])
                    else: self.assertIn(caught.exception.winerror, {3, 5, 6})
                self.assertEqual(boundary.volume, original)
                self.assertIsNone(boundary.check())


class PhysicalRootDeviceTests(unittest.TestCase):
    def test_changed_root_device_is_rejected_before_any_handle_is_opened(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            boundary = file_io.PhysicalBoundary(root)
            original = os.stat
            def moved(path, *args, **kwargs):
                actual = original(path, *args, **kwargs)
                return SimpleNamespace(st_dev=actual.st_dev+1) if Path(path) == root and kwargs.get('follow_symlinks', True) else actual
            with patch('os.stat', side_effect=moved):
                with self.assertRaisesRegex(ValueError, '^physical root volume changed$'):
                    boundary.check()
            self.assertIsNone(boundary.check())

if __name__ == '__main__':
    unittest.main()

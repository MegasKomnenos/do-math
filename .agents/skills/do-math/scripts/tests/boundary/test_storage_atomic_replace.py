"""Atomic replacement under concurrent Windows readers (``file_io.atomic_replace``), on the real Windows file system.

Design 2.2 keeps the file system out of the ports and judges only the Windows
atomic replacement by boundary tests. The legacy tests replaced
``_replace_once`` and ``time.sleep`` to stage its failures; here the failures
are real: a destination another handle holds without sharing fails with a
sharing violation (winerror 32), a read-only destination with access denied
(winerror 5), a missing source with winerror 2. Each attempt is seen by
observing ``_replace_once`` (``ObservedCalls``), whose capture also releases
the held destination when the retry starts. Retries sleep for real: the six
delays of a permanent failure add up to 0.385 s.
"""
import os
from pathlib import Path
import stat
import tempfile
import unittest

from do_math import file_io
from do_math.file_io import atomic_replace, read_bytes_shared, shared_reader, write_bytes_atomic
from support.provider_probes import ObservedCalls

GENERIC_READ, OPEN_EXISTING, NORMAL = 0x80000000, 3, 0x80


def attempt(arguments):
    return (str(arguments['source']), str(arguments['destination']))


@unittest.skipUnless(os.name == 'nt', 'the replacement under test is the Windows handle rename')
class MetadataPublicationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def test_reader_keeps_one_version_without_blocking_atomic_replacement(self):
        path = self.root / 'state.json'
        path.write_bytes(b'old')
        with shared_reader(path) as previous:
            write_bytes_atomic(path, b'new')
            self.assertEqual(previous.read(), b'old')
            self.assertEqual(read_bytes_shared(path), b'new')
        self.assertEqual(list(self.root.glob('*.tmp')), [])

    def test_sharing_failure_retries_only_the_same_rename(self):
        import _winapi
        source, destination = self.root / 'pending', self.root / 'current'
        source.write_bytes(b'new')
        destination.write_bytes(b'old')
        # Another reader holds the destination without sharing: the rename fails with a sharing violation.
        holder = [_winapi.CreateFile(str(destination), GENERIC_READ, 0, 0, OPEN_EXISTING, NORMAL, 0)]

        def release_on_retry(arguments):
            if holder:
                if len(calls.calls['replace']) == 1:  # the retry is starting
                    _winapi.CloseHandle(holder.pop())
            return attempt(arguments)
        try:
            with ObservedCalls(replace=file_io._replace_once, capture={'replace': release_on_retry}) as calls:
                atomic_replace(source, destination)
        finally:
            if holder:
                _winapi.CloseHandle(holder.pop())
        self.assertEqual(calls.captured('replace'), [(str(source), str(destination))] * 2)
        self.assertEqual(destination.read_bytes(), b'new')
        self.assertFalse(source.exists())

    def test_permanent_failure_is_bounded_and_unrelated_errors_are_not_retried(self):
        source, destination = self.root / 'pending', self.root / 'current'
        source.write_bytes(b'new')
        destination.write_bytes(b'old')
        os.chmod(destination, stat.S_IREAD)  # replacing a read-only file is access denied (winerror 5)
        self.addCleanup(os.chmod, destination, stat.S_IWRITE)
        with ObservedCalls(replace=file_io._replace_once, capture={'replace': attempt}) as calls:
            with self.assertRaises(PermissionError) as denied:
                atomic_replace(source, destination)
        self.assertEqual(denied.exception.winerror, 5)
        # One attempt per delay of the retry schedule, all of the same rename.
        self.assertEqual(calls.captured('replace'), [(str(source), str(destination))] * 6)
        self.assertEqual(destination.read_bytes(), b'old')
        missing = self.root / 'missing'
        with ObservedCalls(replace=file_io._replace_once) as calls:
            with self.assertRaises(FileNotFoundError) as absent:
                atomic_replace(missing, destination)
        self.assertEqual(absent.exception.winerror, 2)
        self.assertEqual(calls.count('replace'), 1)

    def test_unicode_long_paths_and_changing_lengths_preserve_exact_target(self):
        parent = self.root / ('한글🌐' * 25) / ('nested' * 20)
        parent.mkdir(parents=True)
        for name in ('a', '다른이름🌐.json', 'long-name-' * 10 + '.json'):
            with self.subTest(name=name):
                path = parent / name
                write_bytes_atomic(path, b'old' * 800)
                with shared_reader(path) as previous:
                    for raw in (b'x', b'', b'new' * 4000):
                        write_bytes_atomic(path, raw)
                        self.assertEqual(read_bytes_shared(path), raw)
                    self.assertEqual(previous.read(), b'old' * 800)
        self.assertEqual({p.name for p in parent.iterdir()},
                         {'a', '다른이름🌐.json', 'long-name-' * 10 + '.json'})


if __name__ == '__main__':
    unittest.main()

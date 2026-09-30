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


if __name__ == '__main__':
    unittest.main()

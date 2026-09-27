from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from do_math.file_io import atomic_replace, cached_sha256, fingerprint_settled, file_fingerprint, read_bytes_shared, shared_reader, write_bytes_atomic
from do_math.repository import VERIFIED_ARTIFACTS, artifact_verified, verify_artifact
import hashlib, os, time


class MetadataPublicationTests(unittest.TestCase):
    def test_reader_keeps_one_version_without_blocking_atomic_replacement(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'state.json';path.write_bytes(b'old')
            with shared_reader(path) as previous:
                write_bytes_atomic(path,b'new')
                self.assertEqual(previous.read(),b'old')
                self.assertEqual(read_bytes_shared(path),b'new')
            self.assertEqual(list(Path(directory).glob('*.tmp')),[])

    def test_sharing_failure_retries_only_the_same_rename(self):
        error=PermissionError('busy');error.winerror=32
        with patch('do_math.file_io._replace_once',side_effect=[error,None]) as replace, \
             patch('do_math.file_io.time.sleep'):
            atomic_replace('pending','current')
        self.assertEqual(replace.call_count,2)
        self.assertEqual(replace.call_args_list[0],replace.call_args_list[1])

    def test_permanent_failure_is_bounded_and_unrelated_errors_are_not_retried(self):
        error=PermissionError('busy');error.winerror=5
        with patch('do_math.file_io._replace_once',side_effect=error) as replace, \
             patch('do_math.file_io.time.sleep'):
            with self.assertRaises(PermissionError):atomic_replace('pending','current')
        self.assertEqual(replace.call_count,6)
        with patch('do_math.file_io._replace_once',side_effect=FileNotFoundError('missing')) as replace:
            with self.assertRaises(FileNotFoundError):atomic_replace('pending','current')
        self.assertEqual(replace.call_count,1)

    def test_missing_read_is_still_absence(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):read_bytes_shared(Path(directory)/'missing')

    def test_unicode_long_paths_and_changing_lengths_preserve_exact_target(self):
        with tempfile.TemporaryDirectory() as directory:
            parent=Path(directory)/('한글🌐'*25)/('nested'*20)
            parent.mkdir(parents=True)
            for name in ('a','다른이름🌐.json','long-name-'*10+'.json'):
                with self.subTest(name=name):
                    path=parent/name
                    write_bytes_atomic(path,b'old'*800)
                    with shared_reader(path) as previous:
                        for raw in (b'x',b'',b'new'*4000):
                            write_bytes_atomic(path,raw)
                            self.assertEqual(read_bytes_shared(path),raw)
                        self.assertEqual(previous.read(),b'old'*800)
            self.assertEqual({p.name for p in parent.iterdir()},
                             {'a','다른이름🌐.json','long-name-'*10+'.json'})


class FingerprintTests(unittest.TestCase):
    def test_fingerprint_change_alone_triggers_rehash(self):
        with tempfile.TemporaryDirectory() as directory, patch('do_math.file_io.RACY_NS',0):
            path=Path(directory)/'tool.exe';path.write_bytes(b'one')
            old=time.time_ns()-10**10;os.utime(path,ns=(old,old))
            self.assertEqual(cached_sha256(path),hashlib.sha256(b'one').hexdigest())
            with patch('do_math.file_io.sha256_file') as rehash:
                self.assertEqual(cached_sha256(path),hashlib.sha256(b'one').hexdigest())
                rehash.assert_not_called()
            before=file_fingerprint(path)
            path.write_bytes(b'two!');os.utime(path,ns=(old+1,old+1))
            self.assertNotEqual(file_fingerprint(path),before)
            self.assertEqual(cached_sha256(path),hashlib.sha256(b'two!').hexdigest())
            # Documented limit: content changed with size and times preserved.
            path.write_bytes(b'TWO!');os.utime(path,ns=(old+1,old+1))
            self.assertEqual(cached_sha256(path),hashlib.sha256(b'two!').hexdigest())

    def test_recent_fingerprint_is_not_cached(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'fresh.json';path.write_bytes(b'a')
            cached_sha256(path)
            with patch('do_math.file_io.sha256_file',return_value='x') as rehash:
                cached_sha256(path)
                rehash.assert_called_once()

    def test_verified_artifact_is_scoped_to_repository_and_hash(self):
        raw=b'artifact';digest=hashlib.sha256(raw).hexdigest()
        with self.assertRaises(ValueError):verify_artifact('g1','runtime/artifacts/a/x',b'other',digest)
        self.assertFalse(artifact_verified('g1','runtime/artifacts/a/x',digest))
        verify_artifact('g1','runtime/artifacts/a/x',raw,digest,len(raw))
        self.assertTrue(artifact_verified('g1','runtime/artifacts/a/x',digest))
        self.assertFalse(artifact_verified('g2','runtime/artifacts/a/x',digest))
        # A row declaring another size is not the matched row.
        self.assertTrue(artifact_verified('g1','runtime/artifacts/a/x',digest,len(raw)))
        self.assertFalse(artifact_verified('g1','runtime/artifacts/a/x',digest,len(raw)+1))
        VERIFIED_ARTIFACTS.pop(('g1','runtime/artifacts/a/x',digest),None)


if __name__=='__main__':unittest.main()

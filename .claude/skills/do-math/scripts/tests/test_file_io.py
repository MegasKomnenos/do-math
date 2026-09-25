from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from do_math.file_io import atomic_replace, read_bytes_shared, shared_reader, write_bytes_atomic
from test_categories import test_group


@test_group('unit')
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


if __name__=='__main__':unittest.main()

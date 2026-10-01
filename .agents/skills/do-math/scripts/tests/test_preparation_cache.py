"""Exact code/schema caching must not reuse mutable inputs or conceal edits."""
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import submission


class PreparationCacheTests(unittest.TestCase):
    def test_same_code_reuses_compression_but_each_workspace_keeps_its_own_context(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / 'package'; package.mkdir()
            (package / 'checker.py').write_bytes(b'edition = 1\n')
            contexts = [{'action': {'role': 'maintenance'}, 'snapshot': name} for name in ('first', 'second')]
            submission._support_archive.cache_clear()
            with patch.object(submission, '__file__', str(package / 'submission.py')), \
                    patch.object(submission.zipfile, 'ZipFile', wraps=zipfile.ZipFile) as compressed:
                for name, context in zip(('left', 'right'), contexts):
                    submission.install_tools(root / name, context, {'type': 'object'}, 1024)
                self.assertEqual(compressed.call_count, 1)
            self.assertEqual((root / 'left/input/tools/submission-support.zip').read_bytes(),
                             (root / 'right/input/tools/submission-support.zip').read_bytes())
            for name, expected in zip(('left', 'right'), ('first', 'second')):
                self.assertEqual(json.loads((root / name / 'input/submission/context.json').read_bytes())['snapshot'], expected)

    def test_unchanged_code_is_not_reread_and_an_edit_ships_new_bytes(self):
        import time
        from do_math import file_io
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'package/checker.py'; source.parent.mkdir()
            source.write_bytes(b'edition = 1\n')
            settled = time.time_ns() - 10 * file_io.RACY_NS
            os.utime(source, ns=(settled, settled))
            submission._support_archive.cache_clear()
            # A fresh file's birth time cannot be aged; treat any past fingerprint as settled.
            with patch.object(submission, '__file__', str(source.parent / 'submission.py')), \
                    patch.object(file_io, 'RACY_NS', 0):
                submission.install_tools(root / 'first', {'action': {'role': 'maintenance'}}, {}, None)
                # A settled, unchanged edition is identified by its fingerprint alone.
                with patch.object(file_io, 'sha256_file', side_effect=AssertionError('unchanged code was reread')):
                    submission.install_tools(root / 'again', {'action': {'role': 'maintenance'}}, {}, None)
                source.write_bytes(b'edition = 2\n')
                os.utime(source, ns=(settled, settled + 10 ** 9))
                submission.install_tools(root / 'second', {'action': {'role': 'maintenance'}}, {}, None)
            first = (root / 'first/input/tools/submission-support.zip').read_bytes()
            self.assertEqual(first, (root / 'again/input/tools/submission-support.zip').read_bytes())
            second = (root / 'second/input/tools/submission-support.zip').read_bytes()
            self.assertNotEqual(first, second)
            with zipfile.ZipFile(io.BytesIO(second)) as archive:
                self.assertEqual(archive.read('do_math/checker.py'), b'edition = 2\n')



if __name__ == '__main__':
    unittest.main()

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
from do_math import submission, preflight


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

    def test_same_path_size_and_mtime_cannot_hide_new_code_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'package/checker.py'; source.parent.mkdir()
            source.write_bytes(b'edition = 1\n'); before = source.stat()
            with patch.object(submission, '__file__', str(source.parent / 'submission.py')):
                submission.install_tools(root / 'first', {'action': {'role': 'maintenance'}}, {}, None)
                source.write_bytes(b'edition = 2\n')
                os.utime(source, ns=(before.st_atime_ns, before.st_mtime_ns))
                submission.install_tools(root / 'second', {'action': {'role': 'maintenance'}}, {}, None)
            first = (root / 'first/input/tools/submission-support.zip').read_bytes()
            second = (root / 'second/input/tools/submission-support.zip').read_bytes()
            self.assertNotEqual(first, second)
            with zipfile.ZipFile(io.BytesIO(second)) as archive:
                self.assertEqual(archive.read('do_math/checker.py'), b'edition = 2\n')

    def test_valid_schema_cache_does_not_hide_a_changed_invalid_schema(self):
        from jsonschema.exceptions import SchemaError
        preflight._check_schema_pair('{"type":"object"}')
        preflight._check_schema_pair('{"type":"object"}')
        with self.assertRaises(SchemaError):
            preflight._check_schema_pair('{"type":"not-a-json-schema-type"}')


if __name__ == '__main__':
    unittest.main()

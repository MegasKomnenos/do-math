"""실제 자식 인터프리터에서 동결 식별자 출력을 확인한다. Git·예약·모델은 호출하지 않는다."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import operator_bootstrap as bootstrap
from test_categories import test_group


@test_group('resource')
class BootstrapInfoTests(unittest.TestCase):
    def test_frozen_entry_reports_original_installation_and_exact_verified_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = Path(bootstrap.__file__).resolve().parent.parent
            receipt = bootstrap.freeze(source, root / 'workspace')
            manifest = json.loads(Path(receipt['manifest']).read_bytes())
            result = subprocess.run([sys.executable, '-B', receipt['entrypoint'], '--bootstrap-info'],
                cwd=root, capture_output=True, text=True, encoding='utf-8', timeout=60,
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), {'mode': 'frozen', 'manifest': manifest})
            self.assertEqual(manifest['installation_root'], str(source))
            self.assertEqual(sorted(path.name for path in (root / 'workspace/operator').iterdir()), ['bootstrap'])

    def test_frozen_location_without_manifest_fails_before_reporting_live_mode(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            receipt = bootstrap.freeze(Path(bootstrap.__file__).resolve().parent.parent, root / 'workspace')
            Path(receipt['manifest']).unlink()
            result = subprocess.run([sys.executable, '-B', receipt['entrypoint'], '--bootstrap-info'],
                cwd=root, capture_output=True, text=True, encoding='utf-8', timeout=60,
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('FileNotFoundError', result.stderr)
            self.assertIn(bootstrap.MANIFEST, result.stderr)
            self.assertEqual(result.stdout, '')

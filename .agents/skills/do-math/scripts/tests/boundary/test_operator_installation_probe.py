"""실제 설치 생산물의 구조 탐침. 자식도 명시 포트를 받아 외부 도구를 호출하지 않는다."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import operator_bootstrap as bootstrap
from test_categories import test_group


@test_group('resource')
class OperatorInstallationProbeTests(unittest.TestCase):
    def test_empty_installed_document_reports_incomplete_with_nonzero_exit(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(bootstrap.__file__).resolve().parents[1]
            receipt = bootstrap.freeze(source, Path(directory))
            snapshot = Path(receipt['manifest']).parent
            program = '''import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from support.entry import entry
import probe_cli
assert Path(probe_cli.__file__).resolve().parent == Path.cwd().resolve()
values = entry()
raise SystemExit(probe_cli.main(['--skill-only'], ports=values.ports, environment=values.environment, host_id=values.host_id, codex_home=values.codex_home))
'''
            command = [sys.executable, '-B', '-c', program, str(Path(__file__).resolve().parents[1])]
            options = dict(cwd=snapshot / 'scripts', capture_output=True, text=True, encoding='utf-8',
                timeout=30, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            normal = subprocess.run(command, **options)
            self.assertEqual(normal.returncode, 0, normal.stderr)
            self.assertEqual(json.loads(normal.stdout)['status'], 'verified')
            # 시험 소유 사본의 문서 바이트 하나만 바꾸며 제품 코드와 실제 설치는 그대로 둔다.
            (snapshot / 'README.md').write_bytes(b'')
            rejected = subprocess.run(command, **options)
            self.assertEqual(rejected.returncode, 1, rejected.stderr)
            report = json.loads(rejected.stdout)
            self.assertEqual(report['status'], 'incomplete')
            self.assertEqual(report['scope'], 'installed_skill_structure')
            self.assertEqual(report['checks'][0], {'check': 'installed_documents', 'status': 'incomplete',
                'reason': 'empty document: README.md'})
            self.assertEqual(report['checks'][1]['status'], 'verified')
            self.assertEqual(sorted(p.name for p in (Path(directory) / 'operator').iterdir()), ['bootstrap'])

"""Shallow installation discovery from copied package bytes, with no source-path patch."""
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

from do_math import formal
from do_math.wiring import real_ports
from test_categories import test_group


@test_group('resource')
class StandaloneFoundationTests(unittest.TestCase):
    def test_foundation_shallow_installation_without_lean_reports_unavailable(self):
        # The package must really have fewer than six ancestors; the ordinary user temp is deeper.
        from support.entry import entry
        _entry = entry()
        from support.entry import entry
        _entry = entry()
        with tempfile.TemporaryDirectory(prefix='do-math-foundation-', dir=Path.cwd().anchor) as directory:
            root = Path(directory)
            scripts = root / 'scripts'
            shutil.copytree(Path(formal.__file__).parent, scripts / 'do_math',
                            ignore=shutil.ignore_patterns('__pycache__'))
            source = ("import sys,json; sys.path.insert(0,sys.argv[1]); "
                      "from do_math import formal; from do_math.local_host import LocalHost; "
                      "print(json.dumps([formal.toolchain_root(),formal.discover_lean(),LocalHost().discover_lean()]))")
            ports = real_ports(environment=_entry.environment)
            result = formal._job_run([sys.executable, '-I', '-c', source, str(scripts)], root,
                jobs=ports.jobs, clock=ports.clock, env={**os.environ, 'PATH': ''}, environment=_entry.environment)
            self.assertEqual(result[0], 0, result)
            self.assertEqual(json.loads(result[1]), [None, None, None])
            self.assertFalse(result[3])

"""Explicit child environment survives the actual shared worker process."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

from do_math.formal import _job_run
from do_math.wiring import real_ports
from test_categories import test_group


@test_group('resource')
class FormalFoundationEnvironmentTests(unittest.TestCase):
    def test_foundation_explicit_environment_reaches_external_process(self):
        from support.entry import entry
        _entry = entry()
        from support.entry import entry
        _entry = entry()
        ports = real_ports(environment=_entry.environment)
        env = {**os.environ, 'LEAN_PATH': 'foundation-explicit', 'FOUNDATION_CHILD': 'yes'}
        with tempfile.TemporaryDirectory() as directory:
            result = _job_run([sys.executable, '-c',
                "import os,json; print(json.dumps([os.environ['LEAN_PATH'],os.environ['FOUNDATION_CHILD']]))"],
                Path(directory), jobs=ports.jobs, clock=ports.clock, env=env, environment=_entry.environment)
        self.assertEqual(result[0], 0, result)
        self.assertEqual(json.loads(result[1]), ['foundation-explicit', 'yes'])
        self.assertFalse(result[3])

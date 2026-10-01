"""The ``decision`` command refuses a malformed decision file as an input error before it queues anything.

The command runs as a real child process of the entry point ``do_math.py``, as
the legacy test ran it, so the exit code and the envelope are what a user's
shell sees. The instance is a publicly initialized Sim; the command checks the
decision's shape before it opens the repository, and the Sim's control inbox
stays empty.
"""
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

from do_math.canonical import canonical_json
from support.engine_gates import initialized_sim
from support.engine_shapes import BAD_PAYLOADS, inbox
from test_categories import test_group

ENTRYPOINT = Path(__file__).resolve().parents[2] / 'do_math.py'


@test_group('resource')
class CliControlShapeTests(unittest.TestCase):
    def test_cli_nested_decision_errors_are_input_errors_without_pending_requests(self):
        sim = initialized_sim()
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        for index, (_, config, reason) in enumerate(BAD_PAYLOADS[1:3]):
            with self.subTest(change=config['change']['kind']):
                path = Path(directory.name) / ('decision-' + str(index) + '.json')
                path.write_bytes(canonical_json(config['change']))
                result = subprocess.run([sys.executable, str(ENTRYPOINT), 'decision', '--repository', str(sim.repository),
                                         '--instance', sim.instance_id, '--file', str(path)],
                                        capture_output=True, text=True, encoding='utf-8')
                self.assertEqual(result.returncode, 2, result.stderr)
                error = json.loads(result.stdout)['error']
                self.assertEqual(error['kind'], 'input_error')
                self.assertRegex(error['message'], '^' + re.escape(reason) + '$')
        self.assertEqual(list(inbox(sim).glob('*.json')), [])


if __name__ == '__main__':
    unittest.main()

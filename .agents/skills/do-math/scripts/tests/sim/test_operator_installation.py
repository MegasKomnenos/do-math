"""The installed skill's own entry points, called in process (``probe_cli``, layer 3).

``probe_cli.main`` checks its arguments before it creates the evidence folder
or starts any live case; the calls are observed on the unchanged product
(``ObservedCalls``), so nothing is replaced.
"""
from contextlib import redirect_stderr
import io
from pathlib import Path
import tempfile
import unittest

import probe_cli
from support.provider_probes import ObservedCalls


class ProbeArgumentTests(unittest.TestCase):
    def test_claude_only_cases_and_options_are_rejected_before_live_setup(self):
        from support.entry import entry
        _entry = entry()
        for options in (['--cases', 'background'], ['--only-assigned-model']):
            with self.subTest(options=options), tempfile.TemporaryDirectory() as directory:
                evidence = Path(directory) / 'unused-evidence'
                errors = io.StringIO()
                with ObservedCalls(mkdir=Path.mkdir, run=probe_cli.run_case) as observed, redirect_stderr(errors):
                    with self.assertRaises(SystemExit) as result:
                        probe_cli.main(['--provider', 'codex', '--model', 'must-not-run',
                                        '--output-dir', str(evidence), *options], ports=_entry.ports, environment=_entry.environment, host_id=_entry.host_id, codex_home=_entry.codex_home)
                self.assertEqual(result.exception.code, 2)
                self.assertIn('background and --only-assigned-model require --provider claude', errors.getvalue())
                self.assertEqual(observed.count('mkdir'), 0)
                self.assertEqual(observed.count('run'), 0)
                self.assertFalse(evidence.exists())


if __name__ == '__main__':
    unittest.main()

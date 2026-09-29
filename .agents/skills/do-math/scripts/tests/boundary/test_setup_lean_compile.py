"""The setup tool's representative compile through a real Windows Job (``setup_lean.verify_environment``).

``setup_lean`` starts the compile with ``formal._job_run`` and no Jobs port, so
the compile is a real Job. The compiler is a small Python program standing in
for Lean: it writes its own arguments (or a fixed output) and an exit code, so
the evidence the tool keeps can be compared with what the program received and did.
"""
from pathlib import Path
import hashlib
import json
import sys
import tempfile
import unittest

import setup_lean

COMPILER = '''import json, sys
sys.stdout.write(json.dumps(sys.argv) if {echo!r} else {stdout!r})
sys.stderr.write({stderr!r})
raise SystemExit({code})
'''


class RepresentativeCompileTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.identity = {'executable': str(self.root / 'lean/bin/lean.exe'), 'project': None}

    def compiler(self, *, stdout='', stderr='', code=0, echo=False):
        """The compiler command; ``echo`` makes the program print the arguments it was started with."""
        path = self.root / 'compiler.py'
        path.write_text(COMPILER.format(stdout=stdout, stderr=stderr, code=code, echo=echo), encoding='utf-8')
        return [sys.executable, str(path)]

    def test_validation_preserves_source_output_and_exact_command(self):
        command = self.compiler(echo=True)
        record = setup_lean.verify_environment(command, self.root / 'evidence', self.identity)
        self.assertEqual(record['status'], 'verified')
        self.assertEqual(record['scope'], 'lean_core_representative_proofs')
        self.assertEqual(record['command'], [*command, record['source']])
        # The program actually started received the recorded command after the interpreter.
        self.assertEqual(json.loads(record['stdout']), record['command'][1:])
        self.assertEqual((record['exit_code'], record['stderr']), (0, ''))
        self.assertEqual(record['source_sha256'], hashlib.sha256(Path(record['source']).read_bytes()).hexdigest())
        preserved = json.loads((Path(record['source']).parent / 'validation.json').read_text(encoding='utf-8'))
        self.assertEqual(preserved, record)

    def test_failure_and_stop_never_produce_verified_evidence(self):
        record = setup_lean.verify_environment(self.compiler(stderr='diagnostic', code=1), self.root / 'evidence',
                                               self.identity)
        self.assertEqual(record['status'], 'failed')
        self.assertEqual((record['exit_code'], record['stderr']), (1, 'diagnostic'))
        self.assertNotIn('error', record)


if __name__ == '__main__':
    unittest.main()

"""The setup tool's representative compile through a real Windows Job (``setup_lean.verify_environment``).

With no explicit ports, ``setup_lean`` starts the compile with the real Job
and clock defaults through ``formal._job_run``. The compiler is a small Python program standing in
for Lean: it writes its own arguments (or a fixed output) and an exit code, so
the evidence the tool keeps can be compared with what the program received and did.
"""
from pathlib import Path
import hashlib
import json
import os
import sys
import tempfile
import unittest

import setup_lean
from test_categories import test_group

COMPILER = '''import json, sys
sys.stdout.write(json.dumps(sys.argv) if {echo!r} else {stdout!r})
sys.stderr.write({stderr!r})
raise SystemExit({code})
'''


@test_group('resource')
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
        from support.entry import entry
        _entry = entry()
        from do_math.wiring import real_ports
        _entry.ports = real_ports(environment=_entry.environment)
        command = self.compiler(echo=True)
        record = setup_lean.verify_environment(command, self.root / 'evidence', self.identity, clock=_entry.ports.clock, environment=_entry.environment, jobs=_entry.ports.jobs)
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
        from support.entry import entry
        _entry = entry()
        from do_math.wiring import real_ports
        _entry.ports = real_ports(environment=_entry.environment)
        record = setup_lean.verify_environment(self.compiler(stderr='diagnostic', code=1), self.root / 'evidence',
                                               self.identity, clock=_entry.ports.clock, environment=_entry.environment, jobs=_entry.ports.jobs)
        self.assertEqual(record['status'], 'failed')
        self.assertEqual((record['exit_code'], record['stderr']), (1, 'diagnostic'))
        self.assertNotIn('error', record)


@test_group('resource')
@unittest.skipUnless(os.name == 'nt', 'Windows console handles exist only on Windows')
class SetupProcessTests(unittest.TestCase):
    def test_setup_short_command_preserves_context_and_has_no_console(self):
        from do_math.file_io import console_python
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            result_path = root/'setup-child.json'
            script = '''import ctypes, json, os, sys
from pathlib import Path
kernel = ctypes.WinDLL('kernel32', use_last_error=True)
kernel.GetConsoleWindow.restype = ctypes.c_void_p
result = {'console': int(kernel.GetConsoleWindow() or 0),
          'cwd': str(Path.cwd()), 'probe': os.environ['DO_MATH_SETUP_PROBE']}
Path(sys.argv[1]).write_text(json.dumps(result), encoding='utf-8')
'''
            setup_lean.run([console_python(), '-c', script, str(result_path)],
                           cwd=root, env={**os.environ, 'DO_MATH_SETUP_PROBE': 'preserved'})
            self.assertEqual(json.loads(result_path.read_text(encoding='utf-8')),
                             {'console': 0, 'cwd': str(root), 'probe': 'preserved'})


if __name__ == '__main__':
    unittest.main()

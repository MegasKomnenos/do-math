"""Installed preview commands execute the shipped archive across the interpreter and Lean boundary."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest

from support.provider_inputs import actual_command
from test_categories import test_group as category
from do_math.submission import install_tools
from do_math.contracts import schema_for


@category('resource')
class LeanPreviewTests(unittest.TestCase):
    def test_control_stop_is_consumed_before_any_compiler_start(self):
        from support.entry import entry
        _entry = entry()
        from do_math.wiring import real_ports
        _entry.ports = real_ports(environment=_entry.environment)
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            context = {"action": {"role": "research_work"}, "snapshot": "fixed",
                "formal_verifier": {"command": ["definitely-missing-lean"], "allowed_axioms": []}}
            install_tools(workspace, context, schema_for('research_work'), 1000000, clock=_entry.ports.clock)
            (workspace / 'draft.lean').write_text('theorem good : True := by trivial', encoding='utf-8')
            (workspace / '.control').mkdir()
            (workspace / '.control/stop-request.json').write_text('{}', encoding='utf-8')
            preview = context['formal_verifier']['preview']
            result = subprocess.run([*preview['command'], '--source', 'draft.lean', '--declaration', 'good'],
                cwd=workspace, capture_output=True, text=True, encoding='utf-8', timeout=30)
            self.assertEqual('stopped', json.loads(result.stdout)['status'])

    def test_preview_attaches_no_dependency_extraction_and_prints_only_worker_fields(self):
        from support.entry import entry
        _entry = entry()
        from do_math.wiring import real_ports
        _entry.ports = real_ports(environment=_entry.environment)
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            compiler = workspace / 'compiler.py'
            compiler.write_text(
                "import sys\n"
                "if '--version' in sys.argv:\n    print('Lean fake'); raise SystemExit\n"
                "if '#do_math_dependencies' in open(sys.argv[-1], encoding='utf-8').read():\n"
                "    print('dependency extraction attached')\n"
                "print('\"__DO_MATH_SIGNATURE_BEGIN_good__\"'); print('good : True')\n"
                "print('\"__DO_MATH_SIGNATURE_END_good__\"'); print(\"'good' does not depend on any axioms\")\n",
                encoding='utf-8')
            context = {"action": {"role": "research_work"}, "snapshot": "fixed",
                "formal_verifier": {"command": [sys.executable, str(compiler)], "allowed_axioms": []}}
            install_tools(workspace, context, schema_for('research_work'), 1000000, clock=_entry.ports.clock)
            (workspace / 'draft.lean').write_text('theorem good : True := trivial', encoding='utf-8')
            preview = context['formal_verifier']['preview']
            result = subprocess.run([*preview['command'], '--source', 'draft.lean', '--declaration', 'good'],
                cwd=workspace, capture_output=True, text=True, encoding='utf-8', timeout=60)
        data = json.loads(result.stdout)
        self.assertEqual(data['status'], 'verified', data)
        self.assertNotIn('dependency extraction attached', data['stdout'])
        from do_math.formal_preview import PREVIEW_FIELDS
        self.assertLessEqual(set(data), set(PREVIEW_FIELDS))
        self.assertEqual(data['declaration_signatures'], {'good': 'good : True'})
        self.assertEqual(data['axioms'], {'good': []})

    def test_preview_tool_and_compiler_worker_skip_unneeded_modules(self):
        """The tool reads its input without the submission checker; the Job worker
        that only starts the compiler loads no state store or schema library."""
        from support.entry import entry
        _entry = entry()
        from do_math.wiring import real_ports
        _entry.ports = real_ports(environment=_entry.environment)
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            context = {"action": {"role": "research_work"}, "snapshot": "fixed",
                "formal_verifier": {"command": ["definitely-missing-lean"], "allowed_axioms": []}}
            install_tools(workspace, context, schema_for('research_work'), 1000000, clock=_entry.ports.clock)
            loaded = {}
            for module in ('do_math.formal_preview', 'do_math.formal'):
                script = f'import sys; sys.path.insert(0, sys.argv[1]); import {module}; print(" ".join(sys.modules))'
                result = subprocess.run([sys.executable, '-B', '-c', script,
                                         str(workspace / 'input/tools/submission-support.zip')],
                                        capture_output=True, text=True, encoding='utf-8', timeout=60)
                self.assertEqual(result.returncode, 0, result.stderr)
                loaded[module] = set(result.stdout.split())
        self.assertNotIn('do_math.submission', loaded['do_math.formal_preview'])
        self.assertFalse({'do_math.repository', 'jsonschema'} & loaded['do_math.formal'])

    def test_preview_checker_loaded_from_the_support_archive_is_the_approved_checker(self):
        """The worker loads formal.py from a zip, so its path is never the approved path;
        the same bytes are the same checker and pass the identity gate."""
        from support.entry import entry
        _entry = entry()
        from do_math.wiring import real_ports
        _entry.ports = real_ports(environment=_entry.environment)
        from do_math import formal
        from do_math.file_io import sha256_file
        checker = Path(formal.__file__).resolve()
        python = Path(sys.executable).resolve()
        approved = {'executable': str(python), 'sha256': sha256_file(python), 'configured_command': [str(python)],
                    'version': 'fixture', 'version_exit': 0, 'verifier_sha256': sha256_file(checker),
                    'verifier_path': str(checker), 'executables': {}, 'project': None}
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            context = {"action": {"role": "research_work"}, "snapshot": "fixed",
                "formal_verifier": {"command": [str(python)], "allowed_axioms": [], "expected_toolchain": approved}}
            install_tools(workspace, context, schema_for('research_work'), 1000000, clock=_entry.ports.clock)
            script = ('import json, sys; sys.path.insert(0, sys.argv[1]); from do_math import formal; '
                      'print(json.dumps({"file": formal.__file__, '
                      '"errors": formal.toolchain_identity_errors(json.loads(sys.argv[2]), jobs=ports.jobs, clock=ports.clock, environment=env, git_backend=ports.git_backend)}))')
            result = subprocess.run([sys.executable, '-B', '-c', script,
                                     str(workspace / 'input/tools/submission-support.zip'), json.dumps(approved)],
                                    capture_output=True, text=True, encoding='utf-8', timeout=60)
            observed = json.loads(result.stdout or 'null')
            self.assertIsNotNone(observed, result.stderr)
            self.assertIn('submission-support.zip', observed['file'])
            self.assertEqual(observed['errors'], [])

    @category('lean')
    def test_actual_standalone_preview_checks_code_axioms_and_stop(self):
        """25-106 s: six real Lean inputs and the installed CLI must cross the process boundary."""
        from support.entry import entry
        _entry = entry()
        from do_math.wiring import real_ports
        _entry.ports = real_ports(environment=_entry.environment)
        command = actual_command()
        self.assertIsNotNone(command, 'this integration test requires the real compiler')
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            context = {"action": {"role": "research_work"}, "snapshot": "fixed",
                "formal_verifier": {"command": command, "allowed_axioms": ["propext", "Classical.choice", "Quot.sound"]}}
            install_tools(workspace, context, schema_for('research_work'), 1000000, clock=_entry.ports.clock)
            preview = context['formal_verifier'].get('preview')
            self.assertIsNotNone(preview, 'worker must receive the compiler preview command')
            for source, expected, name in [('theorem good : True := by trivial', 'verified', 'good'),
                                     ('theorem good : True := by\r\n  trivial\r\n', 'verified', 'good'),
                                     ('theorem good : False := by sorry', 'rejected', 'good'),
                                     ('theorem good : False := by trivial', 'failed', 'good'),
                                     ("theorem good' : True := by trivial", 'verified', "good'"),
                                     ('theorem \N{KELVIN SIGN} (\N{OHM SIGN} : True) : True := \N{OHM SIGN}\r\n-- e\N{COMBINING ACUTE ACCENT}\n', 'verified', '\N{KELVIN SIGN}')]:
                (workspace / 'draft.lean').write_bytes(source.encode('utf-8'))
                result = subprocess.run([*preview['command'], '--source', 'draft.lean', '--declaration', name],
                    cwd=workspace, capture_output=True, text=True, encoding='utf-8',
                    creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0), timeout=None)
                data = json.loads(result.stdout)
                self.assertEqual(data['status'], expected, result.stderr + str(data))
                self.assertEqual(data['source_sha256'], hashlib.sha256(source.encode()).hexdigest())
                self.assertFalse(data['authoritative'])
                self.assertEqual(data['toolchain']['configured_command'], command)
                self.assertEqual(data['input_snapshot'], 'fixed')
                self.assertFalse({'dependency_closure', 'dependency_evidence', 'declaration_evidence'} & set(data))
                self.assertNotIn('__DO_MATH_DEPENDENC', data.get('stdout', ''))
                if expected == 'verified':
                    self.assertIn(name, data['declaration_signatures'])
                    self.assertEqual(data['axioms'][name], [])
            self.assertFalse(any((workspace / family).exists() for family in
                ('formal_results', 'expositions', 'identity_assessments', 'assessment_uses')))
            (workspace / '.control').mkdir(exist_ok=True)
            (workspace / '.control/stop-request.json').write_text('{}')
            result = subprocess.run([*preview['command'], '--source', 'draft.lean', '--declaration', 'good'],
                cwd=workspace, capture_output=True, text=True, encoding='utf-8',
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0), timeout=30)
            self.assertEqual(json.loads(result.stdout)['status'], 'stopped')

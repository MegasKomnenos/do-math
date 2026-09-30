"""The Lean verifier and its worker Job run directly (``formal`` is layer 3) on the Jobs port.

The compile runs through the product's own ``_job_run`` and ``_worker`` with the
Jobs fake of ``support.knowledge_verifier_jobs``: the worker writes the compiler's
output and its completion status to files, and ``verify_lean`` reads and parses
them. The compiler is a ``spawn`` double printing the fixed output the legacy
synthetic compilers printed. Where the legacy test let ``verify_lean`` inspect
its synthetic compiler (a real ``--version`` Job), these pass the approved
identity instead, as the engine does: ``inspect_toolchain`` starts that Job
without the Jobs port. The inspection path runs on the real Lean in
``boundary.test_knowledge_lean_verifier``. No test here starts a Job; the tests
that must reach none observe ``formal._job_run`` and give an empty Jobs fake.
The pinned-project test runs the product's short ``git`` reads of the project
(``formal._git``), which no port stands for.
"""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

from do_math import formal
from do_math.formal import project_source_identity, verify_lean
from do_math.canonical import exact_content_hash
from knowledge_fixtures import knowledge_candidate
from research_fixtures import git_init
from support.fakes.jobs import FakeJob, FakeJobs
from support.knowledge_verifier_jobs import OutputCompiler, approved_toolchain, formal_jobs, worker_jobs
from support.provider_probes import ObservedCalls


def evidence_output():
    """``first`` and ``second`` verified over the shared closure True, True.intro (the legacy ``_evidence_compiler``)."""
    lines = []
    for name in ('first', 'second'):
        lines += [f'"__DO_MATH_SIGNATURE_BEGIN_{name}__"', f'{name} : True', f'"__DO_MATH_SIGNATURE_END_{name}__"',
                  f"'{name}' does not depend on any axioms"]
    lines.append('user output')
    for name, kind in (('True', 'Prop'), ('True.intro', 'True')):
        lines.append('__DO_MATH_DEPENDENCY__' + json.dumps({'name': name, 'evidence': {'type': kind, 'value': None}}))
    for name in ('first', 'second'):
        lines.append('__DO_MATH_DEPENDENCIES__' + json.dumps({'declaration': name, 'dependencies': ['True', 'True.intro'],
                     'axioms': [], 'evidence': {'type': 'True', 'value': 'True.intro'}}))
    return '\n'.join(lines) + '\n'


class ApprovedCompilerTests(unittest.TestCase):
    """``verify_lean`` with the approved synthetic toolchain, compiling through the worker Job."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.command, self.toolchain = approved_toolchain(self.root)
        self.workspace = self.root / 'work'
        self.workspace.mkdir()

    def verify(self, jobs, *, source='', declarations=('first', 'second')):
        return verify_lean(source=source, declarations=list(declarations), workspace=self.workspace,
                           lean_command=self.command, expected_toolchain=self.toolchain, jobs=jobs)

    def test_dependency_bodies_are_one_table_shared_by_the_declared_closures(self):
        compiler = OutputCompiler(evidence_output())
        result = self.verify(worker_jobs(compiler))
        self.assertEqual(result['status'], 'verified', result)
        self.assertEqual(result['dependency_closure'], {'first': ['True', 'True.intro'], 'second': ['True', 'True.intro']})
        self.assertEqual(result['dependency_evidence'], {'True': exact_content_hash({'type': 'Prop', 'value': None}),
                                                         'True.intro': exact_content_hash({'type': 'True', 'value': None})})
        # The closure and its body table are the stored evidence; no second digest or format marker is kept.
        self.assertFalse({'dependency_hash', 'expression_encoding'} & set(result))
        self.assertEqual(len(compiler.commands), 1, 'one compile')
        self.assertEqual(compiler.commands[0][:1], self.command)

    def test_verified_output_omits_dependency_body_rows_reduced_to_hashes(self):
        result = self.verify(worker_jobs(OutputCompiler(evidence_output())))
        self.assertEqual(result['status'], 'verified', result)
        self.assertNotIn('__DO_MATH_DEPENDENCY__', result['stdout'])
        self.assertIn('user output', result['stdout'])
        self.assertEqual(result['stdout'].count('__DO_MATH_DEPENDENCIES__'), 2)
        self.assertIn('"__DO_MATH_SIGNATURE_BEGIN_first__"', result['stdout'])

    def test_fake_lean_rejects_real_sorry_even_when_source_prints_allowed_text(self):
        # The compiler does not read the source: what is checked is that the axiom lines of one
        # declaration are merged and sorryAx among them rejects it beside an allowed axiom.
        output = ('"__DO_MATH_SIGNATURE_BEGIN_X__"\nX : True\n"__DO_MATH_SIGNATURE_END_X__"\n'
                  "'X' depends on axioms: [Classical.choice]\n'X' depends on axioms: [sorryAx]\n")
        result = self.verify(worker_jobs(OutputCompiler(output)), source='#eval "X depends on axioms: [Classical.choice]"',
                             declarations=['X'])
        self.assertEqual(result['status'], 'rejected', result)
        self.assertIn('sorryAx', result['axioms']['X'])
        self.assertEqual(result['reason'], 'forbidden axiom')

    def test_compiler_without_audit_output_fails_at_the_missing_signature(self):
        result = self.verify(worker_jobs(OutputCompiler('')), declarations=['X'])
        self.assertEqual(result['status'], 'failed', result)
        # The signature check comes before the axiom check, so this is the reason an empty output gets.
        self.assertEqual(result['reason'], 'signature output missing')

    def test_compiler_crash_preserves_native_exit_code(self):
        result = self.verify(worker_jobs(OutputCompiler('', exit_code=0xC0000005)),
                             source='theorem good : True := True.intro', declarations=['good'])
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(result.get('exit_code'), 0xC0000005)
        self.assertEqual(result['reason'], 'compiler crashed')

    def test_verifier_reports_worker_failure_without_raising_or_claiming_timeout(self):
        # A worker root that exits without writing its completion status.
        result = self.verify(formal_jobs(lambda request: 0), source='theorem good : True := True.intro',
                             declarations=['good'])
        self.assertEqual(result['status'], 'failed')
        self.assertIn('worker completion status missing', result['reason'])
        self.assertNotEqual(result['reason'], 'timeout')
        self.assertEqual(result['reason'], 'verification process failed: formal worker completion status missing')

    def test_changed_approved_executable_is_rejected_before_version_execution(self):
        Path(self.toolchain['executable']).write_bytes(b'changed fixture executable')
        jobs = FakeJobs()
        with ObservedCalls(job_run=formal._job_run) as calls:
            result = verify_lean(source='theorem x : True := True.intro', declarations=['x'], workspace=self.workspace,
                                 lean_command=self.command, expected_toolchain=self.toolchain, jobs=jobs)
        self.assertEqual(result['status'], 'rejected', result)
        self.assertEqual(result['reason'], 'approved toolchain changed before execution')
        self.assertEqual((calls.count('job_run'), jobs.launched), (0, []))

    def test_executable_change_during_run_is_left_to_the_next_identity_check(self):
        # The verifier checks the approved identity once, before compiling; a change during the
        # compile is found by the publication gate or the next formal check, not re-observed here.
        executable = Path(self.toolchain['executable'])
        compiler = OutputCompiler('', during=lambda: executable.write_bytes(b'changed during simulated compiler run'))
        result = self.verify(worker_jobs(compiler), source='theorem x : True := True.intro', declarations=['x'])
        self.assertEqual((result['status'], result['reason']), ('failed', 'signature output missing'), result)
        self.assertEqual(len(compiler.commands), 1, 'the compile ran')
        self.assertEqual(formal.toolchain_identity_errors(self.toolchain),
                         ['approved toolchain file changed: ' + str(executable.resolve())])


class PreparationTests(unittest.TestCase):
    """Rejections and stops before any Job: an empty Jobs fake, and ``formal._job_run`` observed."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def verify_without_job(self, **arguments):
        jobs = FakeJobs()
        with ObservedCalls(job_run=formal._job_run) as calls:
            result = verify_lean(workspace=self.root, jobs=jobs, **arguments)
        self.assertEqual((calls.count('job_run'), jobs.launched), (0, []), 'no Job started')
        return result

    def test_invalid_declaration_rejected(self):
        result = self.verify_without_job(source='', declarations=['bad;'])
        self.assertEqual((result['status'], result['reason']), ('rejected', 'invalid declaration'))

    def test_empty_declaration_list_is_rejected(self):
        result = self.verify_without_job(source='theorem foo : False := sorry', declarations=[])
        self.assertEqual((result['status'], result['reason']), ('rejected', 'no declaration to audit'))

    def test_missing_lean_unavailable(self):
        result = self.verify_without_job(source='', declarations=['X'], lean_command=['no-such-lean'])
        self.assertEqual(result['status'], 'unavailable', result)
        self.assertEqual(result['phase'], 'preparation')

    def test_stop_is_not_a_math_failure(self):
        fake = self.root / 'fake.py'
        fake.write_text("import sys,time\nif '--version' in sys.argv: print('v')\nelse: time.sleep(10)", encoding='utf8')
        result = self.verify_without_job(source='', declarations=['X'], lean_command=[sys.executable, str(fake)],
                                         should_stop=lambda: True)
        self.assertEqual(result['status'], 'stopped')
        self.assertEqual(result['phase'], 'preparation')

    def test_pinned_project_change_is_rejected_before_process_start(self):
        root = self.root
        project = root / 'project'
        project.mkdir()
        git_init(root)
        manifest = project / 'lakefile.toml'
        manifest.write_bytes(b'name = "approved"\n')
        executable = root / 'lake.exe'
        executable.write_bytes(b'not executed')
        command = [str(executable), '--dir', str(project), 'env', 'lean']
        digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
        expected = {'configured_command': command, 'executable': str(executable), 'sha256': digest(executable),
                    'verifier_sha256': digest(Path(formal.__file__)), 'verifier_path': str(Path(formal.__file__).resolve()),
                    'executables': {str(executable): digest(executable)},
                    'version': 'fixture', 'version_exit': 0,
                    'project': {'manifest_hashes': {'lakefile.toml': digest(manifest)},
                                'source_identity': project_source_identity(project), 'search_paths': []}}
        manifest.write_bytes(b'name = "changed"\n')
        # Git runs directly; any Job would be the compiler or the Lake environment.
        result = self.verify_without_job(source='theorem x : True := True.intro', declarations=['x'],
                                         lean_command=command, expected_toolchain=expected)
        self.assertEqual(result['status'], 'rejected')
        self.assertEqual(result['reason'], 'approved project inputs changed before execution')

    def test_changed_approved_toolchain_rejects_before_source_execution(self):
        binary_hash = hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest()
        approved = dict(executable=sys.executable, sha256=binary_hash, configured_command=[sys.executable],
                        version='approved-version', version_exit=0, project=None,
                        verifier_sha256=hashlib.sha256(Path(formal.__file__).read_bytes()).hexdigest(),
                        verifier_path=str(Path(formal.__file__).resolve()),
                        executables={str(Path(sys.executable).resolve()): binary_hash})
        executable = self.root / 'lean.exe'
        executable.write_bytes(b'approved executable bytes')
        command = [str(executable)]
        digest = hashlib.sha256(executable.read_bytes()).hexdigest()
        approved.update(executable=str(executable), sha256=digest, configured_command=command,
                        executables={str(executable.resolve()): digest})
        executable.write_bytes(b'changed executable bytes')
        result = self.verify_without_job(source=knowledge_candidate()['lean_code'], declarations=['truth'],
                                         lean_command=command, expected_toolchain=approved)
        self.assertEqual(result['status'], 'rejected')
        self.assertEqual(result['reason'], 'approved toolchain changed before execution')


class WorkerJobTests(unittest.TestCase):
    """``formal._job_run`` on the Jobs port: how a Job that ends without a result is reported."""

    def test_job_start_failure_is_not_reported_as_timeout(self):
        # The product's worker starts the missing compiler with its default spawn (subprocess.Popen),
        # which fails before any process exists and leaves its traceback on stderr.
        jobs = formal_jobs(lambda request: formal._worker(request))
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(RuntimeError, 'formal worker failed: (?s:.*)FileNotFoundError'):
                formal._job_run([str(Path(d) / 'missing-compiler.exe')], Path(d), jobs=jobs)
        self.assertEqual(len(jobs.launched), 1)

    def test_job_missing_completion_is_not_reported_as_timeout(self):
        jobs = formal_jobs(lambda request: 0)  # the root exits without writing its completion status
        with tempfile.TemporaryDirectory() as d, ObservedCalls(close=FakeJob.close) as calls:
            with self.assertRaisesRegex(RuntimeError, 'completion status'):
                formal._job_run(['fixture'], Path(d), jobs=jobs)
        self.assertEqual(calls.count('close'), 1)
        self.assertTrue(jobs.launched[0].closed)


if __name__ == '__main__':
    unittest.main()

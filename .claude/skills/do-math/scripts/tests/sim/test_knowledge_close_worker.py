"""실제 formal 작업자와 Jobs 포트로 오류 전파·콜백·출력 보존을 확인한다."""
from pathlib import Path
import json
import tempfile
import unittest

from do_math import formal
from support.fakes.clock import FakeClock
from support.fakes.git_backend import InProcessGit
from support.knowledge_verifier_jobs import OutputCompiler, worker_jobs, formal_jobs, approved_toolchain
from support.lean import LeanDouble


class WorkerGuards(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.clock = FakeClock()
        self.git_backend = InProcessGit()

    def test_os_error_survives_worker_status_and_job_cleanup(self):
        calls = []
        def spawn(command, **options):
            calls.append((command, options['cwd']))
            raise FileNotFoundError(2, 'knowledge missing executable', 'absent.exe')
        jobs = worker_jobs(spawn)
        with self.assertRaisesRegex(FileNotFoundError, 'knowledge missing executable') as caught:
            formal._job_run(['absent.exe'], self.root, jobs=jobs, clock=self.clock,
                environment={}, preserve_os_error=True)
        self.assertEqual(caught.exception.errno, 2)
        self.assertEqual(caught.exception.filename, 'absent.exe')
        self.assertEqual(calls, [(['absent.exe'], str(self.root))])
        self.assertEqual([(j.done, j.closed) for j in jobs.launched], [(True, True)])

    def test_message_only_os_error_is_preserved(self):
        def spawn(command, **options):
            raise OSError('knowledge message only')
        jobs = worker_jobs(spawn)
        with self.assertRaisesRegex(OSError, '^knowledge message only$'):
            formal._job_run(['synthetic-lean'], self.root, jobs=jobs, clock=self.clock,
                environment={}, preserve_os_error=True)
        self.assertEqual([(j.done, j.closed) for j in jobs.launched], [(True, True)])

    def test_worker_error_without_os_preservation_has_traceback(self):
        def spawn(command, **options):
            raise RuntimeError('knowledge spawn failure')
        jobs = worker_jobs(spawn)
        with self.assertRaisesRegex(RuntimeError, 'formal worker failed: [\\s\\S]*knowledge spawn failure'):
            formal._job_run(['synthetic-lean'], self.root, jobs=jobs, clock=self.clock, environment={})
        self.assertEqual([(j.done, j.closed) for j in jobs.launched], [(True, True)])

    def test_callbacks_environment_and_output_follow_real_worker(self):
        compiler = OutputCompiler('원문\n')
        jobs = worker_jobs(compiler)
        started, finished = [], []
        result = formal._job_run(['synthetic-lean'], self.root, jobs=jobs, clock=self.clock,
            environment={'LEAN_PATH': 'remove', 'Lake_HOME': 'remove', 'ELAN_HOME': 'remove', 'KEEP': 'yes'},
            on_started=started.append, on_finished=finished.append)
        self.assertEqual(result, (0, '원문\n', '', False))
        self.assertEqual(len(started), 1)
        self.assertEqual(finished, [jobs.launched[0].resource_usage()])
        self.assertEqual(started[0]['job_name'], jobs.launched[0].name)
        self.assertEqual(jobs.launched[0].env, {'KEEP': 'yes'})
        self.assertEqual(compiler.commands, [['synthetic-lean']])
        self.assertTrue(jobs.launched[0].closed)

    def test_explicit_environment_preserves_lean_override(self):
        compiler = OutputCompiler()
        jobs = worker_jobs(compiler)
        explicit = {'LEAN_PATH': 'explicit'}
        self.assertEqual(formal._job_run(['synthetic-lean'], self.root, jobs=jobs, clock=self.clock,
            environment={'OTHER': 'discard'}, env=explicit), (0, '', '', False))
        self.assertEqual(jobs.launched[0].env, explicit)
        self.assertEqual(explicit, {'LEAN_PATH': 'explicit'})
        self.assertTrue(jobs.launched[0].closed)

    def test_preparation_stop_never_starts_compiler(self):
        command, toolchain = approved_toolchain(self.root)
        compiler = OutputCompiler()
        jobs = worker_jobs(compiler)
        result = formal.verify_lean(source='theorem t : True := True.intro', declarations=['t'],
            workspace=self.root, lean_command=command, expected_toolchain=toolchain,
            should_stop=lambda: True, jobs=jobs, clock=self.clock, environment={}, git_backend=self.git_backend)
        self.assertEqual((result['status'], result['reason'], result['phase']), ('stopped', 'verification stopped', 'preparation'))
        self.assertEqual((jobs.launched, compiler.commands), ([], []))
        self.assertTrue(result['launch_not_created'])

    def test_unregistered_source_is_failed_by_actual_verifier(self):
        command, toolchain = approved_toolchain(self.root)
        lean = LeanDouble()
        jobs = worker_jobs(lean.spawn)
        result = formal.verify_lean(source='theorem unregistered : True := True.intro', declarations=['unregistered'],
            workspace=self.root, lean_command=command, expected_toolchain=toolchain,
            jobs=jobs, clock=self.clock, environment={}, git_backend=self.git_backend)
        self.assertEqual((result['status'], result['reason']), ('failed', 'lean rejected'))
        self.assertIn('unregistered synthetic Lean source/declarations', result['stderr'])
        self.assertEqual(lean.checks, [{'declarations': ['unregistered'], 'extract': True, 'registered': False, 'synthetic': True}])
        self.assertEqual([(j.done, j.closed) for j in jobs.launched], [(True, True)])

    def test_non_lake_project_identity_performs_no_job(self):
        jobs = worker_jobs(OutputCompiler())
        self.assertIsNone(formal._project_identity(['lean'], workspace=self.root,
            jobs=jobs, clock=self.clock, environment={}, git_backend=self.git_backend))
        self.assertEqual(jobs.launched, [])

    def test_corrupt_completion_exit_is_rejected_after_actual_worker(self):
        compiler = OutputCompiler('보존 출력')
        def run(request):
            result = formal._worker(request, spawn=compiler)
            status = Path(json.loads(request.read_text())['status'])
            data = json.loads(status.read_text())
            data['exit'] = False
            status.write_text(json.dumps(data))
            return result
        jobs = formal_jobs(run)
        with self.assertRaisesRegex(RuntimeError, '^formal worker completion status invalid: invalid completion status$'):
            formal._job_run(['synthetic-lean'], self.root, jobs=jobs, clock=self.clock, environment={})
        self.assertEqual(compiler.commands, [['synthetic-lean']])
        self.assertEqual([(j.done, j.closed) for j in jobs.launched], [(True, True)])

    def test_version_failure_is_not_a_toolchain_identity(self):
        command, _ = approved_toolchain(self.root)
        compiler = OutputCompiler('failed version', exit_code=1)
        jobs = worker_jobs(compiler)
        with self.assertRaisesRegex(RuntimeError, '^toolchain version observation failed: $'):
            formal.inspect_toolchain(command, self.root, jobs=jobs, clock=self.clock, environment={}, git_backend=self.git_backend)
        self.assertEqual(compiler.commands, [[*command, '--version']])
        self.assertEqual([(j.done, j.closed) for j in jobs.launched], [(True, True)])

    def test_empty_version_observation_fails_shape_gate(self):
        command, _ = approved_toolchain(self.root)
        compiler = OutputCompiler('')
        jobs = worker_jobs(compiler)
        with self.assertRaisesRegex(ValueError, '^toolchain.version must be nonempty$'):
            formal.inspect_toolchain(command, self.root, jobs=jobs, clock=self.clock, environment={}, git_backend=self.git_backend)
        self.assertEqual(compiler.commands, [[*command, '--version']])
        self.assertEqual([(j.done, j.closed) for j in jobs.launched], [(True, True)])

    def test_version_observation_stop_preserves_job_cleanup(self):
        command, _ = approved_toolchain(self.root)
        jobs = worker_jobs(OutputCompiler('version'))
        with self.assertRaisesRegex(formal.VerificationStopped, '^toolchain observation stopped$'):
            formal.inspect_toolchain(command, self.root, should_stop=lambda: bool(jobs.launched),
                jobs=jobs, clock=self.clock, environment={}, git_backend=self.git_backend)
        self.assertEqual([(j.done, j.closed) for j in jobs.launched], [(True, True)])

    def test_malformed_identity_returns_shape_errors_without_job(self):
        jobs = worker_jobs(OutputCompiler())
        self.assertEqual(formal.toolchain_identity_errors(False, jobs=jobs, clock=self.clock, environment={}, git_backend=self.git_backend),
            ['toolchain must be an object'])
        self.assertEqual(jobs.launched, [])

    def test_missing_approved_executable_is_an_identity_error(self):
        command, toolchain = approved_toolchain(self.root)
        Path(toolchain['executable']).unlink()
        jobs = worker_jobs(OutputCompiler())
        errors = formal.toolchain_identity_errors(toolchain, jobs=jobs, clock=self.clock, environment={}, git_backend=self.git_backend)
        self.assertEqual(errors, ['approved toolchain file changed: ' + toolchain['executable']])
        self.assertEqual(jobs.launched, [])

    def test_unsafe_command_returns_before_any_launch(self):
        jobs = worker_jobs(OutputCompiler())
        result = formal.verify_lean(source='', declarations=['t'], workspace=self.root,
            lean_command=['lean', '\x00'], jobs=jobs, clock=self.clock, environment={}, git_backend=self.git_backend)
        self.assertEqual((result['status'], result['reason']), ('rejected', 'unsafe command'))
        self.assertTrue(result['launch_not_created'])
        self.assertEqual(jobs.launched, [])

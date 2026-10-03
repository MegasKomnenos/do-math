"""The shared worker uses supplied Jobs, clock and child environment."""
import os
from pathlib import Path
import tempfile
import unittest

from do_math import formal
from do_math.lean_evidence import LEAN_VERSION
from support.fakes.clock import FakeClock
from support.fakes.jobs import job_turn
from support.knowledge_verifier_jobs import OutputCompiler, worker_jobs


class FormalFoundationJobsTests(unittest.TestCase):
    def test_foundation_explicit_environment_and_clock_reach_worker(self):
        from support.entry import entry
        _entry = entry()
        clock = FakeClock()
        compiler = OutputCompiler('complete', during=lambda: [job_turn() for _ in range(5)])
        jobs = worker_jobs(compiler)
        jobs.live = True
        env = {'LEAN_PATH': 'explicit', 'FOUNDATION': 'kept'}
        with tempfile.TemporaryDirectory() as directory:
            result = formal._job_run(['compiler', 'input'], Path(directory), jobs=jobs, clock=clock, env=env, environment=_entry.environment)
        self.assertEqual(result, (0, 'complete', '', False))
        self.assertEqual(compiler.commands, [['compiler', 'input']])
        self.assertEqual(jobs.launched[0].env, env)
        self.assertTrue(jobs.launched[0].closed)
        self.assertEqual(jobs.launched[0].name, 'do-math-formal-' + FakeClock().random_hex(16))
        self.assertGreater(clock.monotonic(), 1000)

    def test_foundation_default_environment_filters_lean_overrides(self):
        from support.entry import entry
        _entry = entry()
        jobs = worker_jobs(OutputCompiler())
        with tempfile.TemporaryDirectory() as directory:
            formal._job_run(['compiler'], Path(directory), jobs=jobs, clock=FakeClock(), environment=_entry.environment)
        self.assertEqual(jobs.launched[0].env, {key: value for key, value in os.environ.items()
                         if not key.upper().startswith(('LEAN_', 'LAKE_', 'ELAN_'))})

    def test_foundation_explicit_stop_closes_job_and_reports_usage(self):
        from support.entry import entry
        _entry = entry()
        jobs = worker_jobs(OutputCompiler(during=lambda: job_turn()))
        jobs.live = True
        usages, started = [], []
        with tempfile.TemporaryDirectory() as directory:
            result = formal._job_run(['compiler'], Path(directory), jobs=jobs, clock=FakeClock(),
                                     should_stop=lambda: True, on_started=started.append,
                                     on_finished=usages.append, job_name='foundation-cancel', environment=_entry.environment)
        self.assertEqual(result, (None, '', '', True))
        self.assertEqual(started[0]['job_name'], 'foundation-cancel')
        self.assertEqual(usages, [jobs.launched[0].resource_usage()])
        self.assertTrue(jobs.launched[0].closed)

    def test_foundation_unapproved_verifier_inspects_and_compiles_through_jobs(self):
        from support.entry import entry
        _entry = entry()
        from support.lean import LeanDouble
        lean = LeanDouble()
        lean.allow('theorem good : True := True.intro', ['good'], signatures={'good': 'good : True'},
            declaration_evidence={'good': {'type': 'True', 'value': None}}, axioms={'good': []}, dependencies={'good': {}})
        jobs = worker_jobs(lean.spawn)
        clock = FakeClock()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            executable = root / 'lean.exe'
            executable.write_bytes(b'Lean external program double')
            result = formal.verify_lean(source='theorem good : True := True.intro', declarations=['good'],
                workspace=root, lean_command=[str(executable)], jobs=jobs, clock=clock, environment=_entry.environment)
        self.assertEqual(result['status'], 'verified', result)
        self.assertEqual(result['toolchain']['version'], lean.version)
        self.assertEqual(lean.commands[0], [str(executable), '--version'])
        self.assertEqual(len(jobs.launched), 2)
        ids = FakeClock()
        self.assertEqual([job.name for job in jobs.launched],
                         ['do-math-formal-' + ids.random_hex(16) for _ in range(2)])

    def test_foundation_lake_observation_and_local_host_forward_jobs_and_clock(self):
        from support.entry import entry
        _entry = entry()
        import json
        from do_math.local_host import LocalHost
        from support.provider_probes import ObservedCalls
        class LakeProgram(OutputCompiler):
            def __call__(self, command, **options):
                self.stdout = ('Lean version test' if command[-1] == '--version' else
                               json.dumps({'cwd': str(project), 'paths': ['.lake/build/lib/lean']}))
                return super().__call__(command, **options)
        clock = FakeClock()
        program = LakeProgram()
        jobs = worker_jobs(program)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / 'project'
            project.mkdir()
            (project / 'lean-toolchain').write_text(f'leanprover/lean4:v{LEAN_VERSION}', encoding='utf-8')
            lake, lean = root / 'lake.exe', root / 'lean.exe'
            lake.write_bytes(b'Lake program')
            lean.write_bytes(b'Lean program')
            command = [str(lake), '--dir', str(project), 'env', str(lean)]
            identity = formal.inspect_toolchain(command, root, jobs=jobs, clock=clock, environment=_entry.environment)
            self.assertEqual(identity['project']['search_paths'], [str((project / '.lake/build/lib/lean').resolve())])
            self.assertEqual(len(jobs.launched), 2)
            # Changed Lake bytes invalidate the cached search-path observation and must use the supplied ports again.
            lake.write_bytes(b'Changed Lake program')
            with ObservedCalls(run=formal._job_run) as observed:
                errors = LocalHost(jobs=jobs, clock=clock, environment=_entry.environment).toolchain_identity_errors(identity)
            self.assertIn('approved toolchain file changed: ' + str(lake), errors)
            args, = observed.captured('run')
            self.assertIs(args['jobs'], jobs)
            self.assertIs(args['clock'], clock)
            self.assertEqual(len(jobs.launched), 3)
            ids = FakeClock()
            self.assertEqual([job.name for job in jobs.launched],
                             ['do-math-formal-' + ids.random_hex(16) for _ in range(3)])

    def test_foundation_empty_environment_is_explicit_and_cancellation_deadline_uses_clock(self):
        from support.entry import entry
        _entry = entry()
        from do_math.windows_job import JobInspection
        delegate = worker_jobs(OutputCompiler())
        class UnconfirmedJobs:
            def launch(self, *args, **kwargs):
                job = delegate.launch(*args, **kwargs)
                # This port reports an OS termination barrier that never empties.
                job.inspect = lambda: JobInspection(active_processes=1, process_ids=(job.pid,), root_signaled=True)
                return job
        clock = FakeClock()
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, 'formal Job termination could not be confirmed'):
                formal._job_run(['compiler'], Path(directory), jobs=UnconfirmedJobs(), clock=clock,
                                env={}, should_stop=lambda: True, environment=_entry.environment)
        self.assertEqual(delegate.launched[0].env, {})
        self.assertTrue(delegate.launched[0].closed)
        self.assertGreaterEqual(clock.monotonic() - 1000, 2)
        self.assertLess(clock.monotonic() - 1000, 2.03)

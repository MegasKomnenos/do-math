"""러너 입력·고정 프로필·종료 격벽의 gap 입력. 실제 worker와 수집기를 유지한다."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from do_math.configuration import DEFAULT_CONFIG
from do_math.execution_profiles import build_profiles, prompt_seal, seal_profile
from support.entry import entry
from support.fakes.clock import FakeClock
from support.provider_runs import ProviderJobs, ScriptedCLI, model_runner, dispatched, codex_stream


class RunnerGapTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.clock = FakeClock()
        self.jobs = ProviderJobs(clock=self.clock)
        self.runner = model_runner(self.root, self.jobs, self.clock)

    def call(self, **changes):
        options = {'prompt': '정상 입력', 'output_schema': {}, 'workspace': self.root / 'workspace',
            'evidence_dir': self.root / 'evidence', 'model': 'test-model', 'effort': 'high', 'timeout_seconds': 0.1}
        options.update(changes)
        return self.runner.run(**options)

    def test_invalid_inputs_and_existing_evidence_are_rejected_before_launch(self):
        for options in ({'prompt': None}, {'output_schema': None}):
            with self.assertRaisesRegex(ValueError, '^invalid prompt or schema$'):
                self.call(**options)
        (self.root / 'evidence').mkdir()
        with self.assertRaisesRegex(FileExistsError, '^evidence_dir must be new$'):
            self.call()
        self.assertEqual(self.jobs.launched, [])

    def test_pinned_assignment_and_seal_limit_rejections_do_not_launch(self):
        profiles = build_profiles(DEFAULT_CONFIG, host=entry().ports.host)['execution_profiles']
        profile = next(p for p in profiles.values() if p['role'] == 'maintenance')
        prompt = '정상 입력'
        options = {'profile': profile, 'execution_id': 'EX-pinned', 'model': profile['ai']['model'],
            'effort': profile['ai']['effort'], 'input_seal': prompt_seal(prompt), 'prompt': prompt,
            'launch_ticket': dispatched('EX-pinned', profile, self.jobs, self.clock)}
        with self.assertRaisesRegex(ValueError, '^runner assignment differs from the pinned execution profile$'):
            self.call(**{**options, 'model': profile['ai']['model'] + '-other'})
        limited = deepcopy(profile)
        limited['input']['max_input_bytes'] = 1
        limited = seal_profile({k: v for k, v in limited.items() if k not in {'id', 'sha256'}})
        with self.assertRaisesRegex(ValueError, '^sealed input exceeds the pinned profile limit$'):
            self.call(**{**options, 'profile': limited,
                'launch_ticket': dispatched('EX-pinned', limited, self.jobs, self.clock)})
        with self.assertRaisesRegex(ValueError, '^execution identity requires a pinned profile$'):
            self.call(execution_id='EX-without-profile')
        self.assertEqual(self.jobs.launched, [])

    def test_unconfirmed_job_barrier_on_cleanup_closes_the_handle_without_resuming(self):
        jobs = ProviderJobs(clock=self.clock, remaining=(42,))
        self.runner = model_runner(self.root, jobs, self.clock)
        started = self.clock.monotonic()
        with self.assertRaisesRegex(RuntimeError, '^termination barrier not reached during exception cleanup$'):
            self.call(should_stop=lambda: True)
        (job,) = jobs.launched
        self.assertTrue(job.closed)
        self.assertFalse(job.resumed)
        self.assertEqual(jobs.cli.calls, [])
        self.assertEqual(job.terminations, 2)
        self.assertGreaterEqual(self.clock.monotonic() - started, 0.2)

    def test_noncanonical_final_number_is_an_output_validation_failure_after_collection(self):
        final = b'{"output_json":"{\\"value\\":0.25}"}'
        cli = ScriptedCLI(stdout=codex_stream(final), final=final)
        jobs = ProviderJobs(cli, clock=self.clock)
        self.runner = model_runner(self.root, jobs, self.clock)
        result = self.call()
        self.assertEqual(result['execution']['collect']['result'], 'output_collected')
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(result['error_kind'], 'output_validation')
        self.assertRegex(result['error'], '^output JSON: ValueError:')
        self.assertEqual(len(cli.calls), 1)
        self.assertTrue(jobs.launched[0].closed)


class RunnerPinnedBoundaryTests(unittest.TestCase):
    def test_host_limit_drift_fails_before_resume_and_closes_the_job(self):
        from support.provider_inputs import host_capacity_fixture
        from do_math.execution_profiles import prepare_prompt, job_resource_limits
        _, selected, _ = host_capacity_fixture()
        profile = selected['research_work']
        clock = FakeClock()
        class DriftJobs(ProviderJobs):
            def launch(self, *args, **kwargs):
                # This Jobs port reports the local limits it actually used.
                kwargs['resource_limits'] = {**kwargs['resource_limits'], 'memory_bytes': 2 * kwargs['resource_limits']['memory_bytes']}
                return super().launch(*args, **kwargs)
        jobs = DriftJobs(clock=clock)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prompt = prepare_prompt('bounded', profile)
            with self.assertRaisesRegex(RuntimeError, '^local Job settings differ from pinned profile before resume$'):
                model_runner(root, jobs, clock).run(prompt=prompt, output_schema={}, workspace=root / 'workspace',
                    evidence_dir=root / 'evidence', model=profile['ai']['model'], effort=profile['ai']['effort'],
                    timeout_seconds=None, execution_id='EX-drift', profile=profile, input_seal=prompt_seal(prompt),
                    launch_ticket=dispatched('EX-drift', profile, jobs, clock), on_started=lambda identity: None)
            job, = jobs.launched
            self.assertTrue(job.closed and job.done)
            self.assertFalse(job.resumed)
            self.assertEqual(jobs.cli.calls, [])
            self.assertNotEqual(job.resource_usage()['limits'], job_resource_limits(profile, host_id=entry().host_id))


    def test_live_observation_before_stdout_exists_keeps_later_native_rows(self):
        from types import MethodType
        class DelayedStreamJobs(ProviderJobs):
            def launch(self, *args, **kwargs):
                job = super().launch(*args, **kwargs)
                original = job.inspect
                stdout = Path(job.cwd) / 'stdout.jsonl'
                held = stdout.with_suffix('.held')
                def inspect(current):
                    if current.resumed and current.inspections == 0 and stdout.exists(): stdout.rename(held)
                    elif held.exists(): held.rename(stdout)
                    return original()
                job.inspect = MethodType(inspect, job)
                return job
        clock = FakeClock()
        jobs = DelayedStreamJobs(clock=clock, polls=3)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            batches = []
            result = model_runner(root, jobs, clock).run(prompt='native rows', output_schema={},
                workspace=root / 'workspace', evidence_dir=root / 'evidence', model='test-model', effort='high',
                timeout_seconds=None, on_observation=batches.append)
            self.assertEqual(result['status'], 'completed')
            self.assertGreaterEqual(len(batches), 2)
            self.assertEqual(batches[0].rows, [])
            self.assertEqual(batches[0].end_offset, 0)
            self.assertEqual(b''.join(row for batch in batches for row in batch.rows),
                             (root / 'evidence' / 'stdout.jsonl').read_bytes())
            self.assertFalse((root / 'evidence' / 'stdout.held').exists())
            self.assertTrue(jobs.launched[0].closed)

"""A checkpoint and its named evidence remain accessible through termination."""
from copy import deepcopy
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from test_categories import test_group
import test_currentness_recovery as currentness_fixtures
from research_fixtures import local_job_runner, dispatched_launch
from do_math.observation_transport import ObservationBatch
from do_math.observations import ObservationTracker
from do_math.repository import canonical_json

CHECKPOINT = {'current_claim': 'original evidence', 'evidence_paths': ['proof.txt'],
    'attempts': ['original checked'], 'remaining_work': ['continue'],
    'next_step': 'continue', 'progress_state': 'working'}


@test_group('unit')
class FinalCheckpointCaptureTests(unittest.TestCase):
    def test_final_capture_owns_exact_raw_and_input_evidence_independently_of_submission_outputs(self):
        from do_math.observations import preserve_checkpoint
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            (workspace / 'input').mkdir()
            (workspace / 'input/source.txt').write_bytes(b'fixed input')
            value = {**CHECKPOINT, 'evidence_paths': ['input/source.txt']}
            raw = canonical_json(value)
            (workspace / 'checkpoint.json').write_bytes(raw)
            first, artifacts = preserve_checkpoint(workspace, artifact_prefix='runtime/artifacts/BA-1/checkpoint', max_bytes=4096)
            self.assertEqual(artifacts[first['artifact_ref']], raw)
            self.assertEqual(artifacts[first['evidence_files'][0]['artifact_ref']], b'fixed input')
            (workspace / 'input/source.txt').write_bytes(b'changed later')
            same, new_artifacts = preserve_checkpoint(workspace, previous=first,
                artifact_prefix='runtime/artifacts/BA-2/checkpoint', max_bytes=4096)
            self.assertEqual(same, first)
            self.assertEqual(new_artifacts, {})
            (workspace / 'checkpoint.json').write_bytes(canonical_json({**value, 'current_claim': 'new claim'}))
            changed, new_artifacts = preserve_checkpoint(workspace, previous=first,
                artifact_prefix='runtime/artifacts/BA-3/checkpoint', max_bytes=4096)
            self.assertNotEqual(changed['sha256'], first['sha256'])
            self.assertEqual(new_artifacts[changed['evidence_files'][0]['artifact_ref']], b'changed later')

    def test_capture_budget_omissions_and_invalid_final_do_not_invent_evidence(self):
        from do_math.observations import preserve_checkpoint
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            (workspace / 'proof.txt').write_bytes(b'x' * 100)
            raw = canonical_json(CHECKPOINT)
            (workspace / 'checkpoint.json').write_bytes(raw)
            first, artifacts = preserve_checkpoint(workspace, artifact_prefix='runtime/artifacts/BA-1/checkpoint', max_bytes=len(raw))
            self.assertEqual(first['evidence_files'], [])
            self.assertEqual(first['evidence_omitted'][0]['path'], 'proof.txt')
            self.assertEqual(sum(map(len, artifacts.values())), len(raw))
            (workspace / 'checkpoint.json').unlink()
            missing, artifacts = preserve_checkpoint(workspace, previous=first,
                artifact_prefix='runtime/artifacts/BA-2/checkpoint', max_bytes=4096)
            self.assertEqual(missing['artifact_ref'], first['artifact_ref'])
            self.assertEqual(missing['final_observation']['checkpoint_status'], 'missing')
            self.assertEqual(artifacts, {})
            (workspace / 'checkpoint.json').write_bytes(raw)
            limited, artifacts = preserve_checkpoint(workspace, artifact_prefix='runtime/artifacts/BA-3/checkpoint', max_bytes=1)
            self.assertEqual(limited['kind'], 'observed_partial_state')
            self.assertEqual(artifacts, {})


@test_group('integration')
class CheckpointPersistenceTests(unittest.TestCase):
    def setUp(self):
        self.fixture = currentness_fixtures.CurrentnessTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.addCleanup(self.fixture.tearDown)
        self.engine, _ = self.fixture.make()

    def test_ended_review_receives_the_original_checkpoint_evidence(self):
        engine, captured = self.engine, {}
        class Worker:
            @local_job_runner
            def run(self, **kwargs):
                kwargs['on_started']()
                workspace = kwargs['workspace']
                (workspace / 'proof.txt').write_bytes(b'original evidence')
                (workspace / 'checkpoint.json').write_bytes(canonical_json(CHECKPOINT))
                kwargs['on_observation'](ObservationBatch([], [], [], 0, '2026-09-25T00:00:00Z',
                    time.monotonic(), 0, 0, kwargs['evidence_dir'] / 'stdout.jsonl', lambda: False))
                # Observations are queued; the owner applies them on its next pass.
                until = time.monotonic() + 60
                while kwargs['execution_id'] not in engine.runtime.get('checkpoints', {}) and time.monotonic() < until:
                    time.sleep(.01)
                captured.update(deepcopy(engine.runtime['checkpoints'][kwargs['execution_id']]))
                (workspace / 'proof.txt').write_bytes(b'changed after checkpoint')
                return {'status': 'failed', 'output': None, 'usage': {}, 'error': 'fixture interruption'}
        engine.runner = Worker()
        engine.run(max_steps=1)
        target = next(e for e in engine.runtime['executions'].values() if e['role'] == 'research_preparation')
        final = engine.runtime['checkpoints'][target['id']]
        self.assertEqual(final['sha256'], captured['sha256'])
        self.assertEqual(final.get('evidence_files'), captured['evidence_files'])
        review = next(a for a in engine.runtime['queue'] if a['role'] == 'operational_review')
        workspace = self.fixture.root / 'review'
        context = engine._context(review, workspace)
        files = context['operational_evidence']['checkpoint_files']
        self.assertEqual(len(files), 1)
        self.assertEqual((workspace / files[0]['local_path']).read_bytes(), b'original evidence')
        output = next(f for f in context['recovery_materials']['output_files'] if f['path'] == 'proof.txt')
        self.assertEqual((workspace / output['local_path']).read_bytes(), b'changed after checkpoint')

    def test_restart_preserves_last_valid_checkpoint_and_records_invalid_final_observation(self):
        engine = self.engine
        action = {'id': 'AC-fixture', 'role': 'research_preparation'}
        execution = engine._register_execution(action, {'id': 'EX-fixture', 'role': action['role'],
            'status': 'running', 'input_snapshot': engine.head, 'input_manifest': [], 'parent_execution_id': None})
        profile = engine.instance['execution_profiles'][execution['execution_profile_ref']['id']]
        execution['launch_ticket'] = dispatched_launch(execution['id'], profile)
        # An admitted launch: its capacity holds the started Job's identity.
        execution['capacity'] = {'reservation_ids': [], 'provider': profile['ai']['provider'],
            'process': {'job_name': execution['launch_ticket']['job_name']}, 'local_termination': 'unknown'}
        workspace = Path(engine.instance['workspace']) / 'runs' / execution['id'] / 'workspace'
        workspace.mkdir(parents=True)
        (workspace / 'proof.txt').write_bytes(b'original evidence')
        (workspace / 'checkpoint.json').write_bytes(canonical_json(CHECKPOINT))
        engine.runtime.update(status='running', queue=[action])
        engine._save()
        tracker = ObservationTracker(execution['id'], workspace, {'observation_mode': 'deadline_only'})
        engine._observe_running(execution['id'], tracker, ObservationBatch([], [], [], 0, '2026-09-25T00:00:00Z',
            time.monotonic(), 0, 0, workspace / 'stdout.jsonl', lambda: False))
        previous = deepcopy(engine.runtime['checkpoints'][execution['id']])
        (workspace / 'checkpoint.json').write_bytes(b'{interrupted write')
        with patch('do_math.windows_job.named_job_empty', return_value=True), \
                patch('do_math.windows_job.owner_ended', return_value=True), engine.store.writer_lock():
            engine._recover_disappeared()
        final = engine.runtime['checkpoints'][execution['id']]
        self.assertEqual(final['kind'], 'worker_checkpoint')
        self.assertEqual(final['artifact_ref'], previous['artifact_ref'])
        self.assertEqual(final['evidence_files'], previous['evidence_files'])
        self.assertEqual(final['final_observation']['checkpoint_status'], 'invalid')
        restored = engine.store.load()[2]['checkpoints'][execution['id']]
        self.assertEqual(restored, final)
        context = engine._context({'role': 'operational_review', 'target': execution['id']}, self.fixture.root / 'review')
        self.assertEqual(context['operational_evidence']['checkpoint_status'], 'preserved')


if __name__ == '__main__':
    unittest.main()

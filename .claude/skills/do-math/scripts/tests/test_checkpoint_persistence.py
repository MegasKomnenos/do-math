"""A checkpoint and its named evidence remain accessible through termination."""
import sys
import time
import unittest
from copy import deepcopy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.observation_transport import ObservationBatch
from do_math.canonical import canonical_json
from purpose_fixtures import ActivatedPurposeHarness, CURRENTNESS_CONFIG
from research_fixtures import local_job_runner

CHECKPOINT = {'current_claim': 'original evidence', 'evidence_paths': ['proof.txt'],
    'attempts': ['original checked'], 'remaining_work': ['continue'],
    'next_step': 'continue', 'progress_state': 'working'}


class CheckpointPersistenceTests(ActivatedPurposeHarness):
    def setUp(self):
        super().setUp()
        self.engine, _ = self.make_active(**CURRENTNESS_CONFIG)

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
                    time.monotonic(), 0, kwargs['evidence_dir'] / 'stdout.jsonl', lambda: False))
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
        workspace = self.root / 'review'
        context = engine._context(review, workspace)
        files = context['operational_evidence']['checkpoint_files']
        self.assertEqual(len(files), 1)
        self.assertEqual((workspace / files[0]['local_path']).read_bytes(), b'original evidence')
        output = next(f for f in context['recovery_materials']['output_files'] if f['path'] == 'proof.txt')
        self.assertEqual((workspace / output['local_path']).read_bytes(), b'changed after checkpoint')


if __name__ == '__main__':
    unittest.main()

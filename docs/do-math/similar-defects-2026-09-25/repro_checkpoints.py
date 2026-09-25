"""Audit only: real engine/storage, scripted worker, disposable instances."""
import hashlib
import json
from pathlib import Path
import sys
import time
from copy import deepcopy
from unittest.mock import patch

ROOT = next(p for p in Path(__file__).resolve().parents if (p / '.claude/skills/do-math').is_dir())
SCRIPTS = ROOT / '.claude/skills/do-math/scripts'
sys.path[:0] = [str(SCRIPTS), str(SCRIPTS / 'tests')]
from test_currentness_recovery import CurrentnessTests
from research_fixtures import local_job_runner, dispatched_launch
from do_math.observation_transport import ObservationBatch
from do_math.observations import ObservationTracker
from do_math.repository import canonical_json

CHECKPOINT = {'current_claim': 'original evidence', 'evidence_paths': ['proof.txt'],
              'attempts': ['original checked'], 'remaining_work': ['continue'],
              'next_step': 'continue', 'progress_state': 'working'}

def regular_end():
    fixture = CurrentnessTests(); fixture.setUp()
    try:
        engine, _ = fixture.make()
        captured = {}
        class Worker:
            @local_job_runner
            def run(self, **kwargs):
                kwargs['on_started']()
                workspace = kwargs['workspace']
                (workspace / 'proof.txt').write_bytes(b'original evidence')
                (workspace / 'checkpoint.json').write_bytes(canonical_json(CHECKPOINT))
                kwargs['on_observation'](ObservationBatch([], [], '2026-09-25T00:00:00Z',
                    time.monotonic(), 0, 0, kwargs['evidence_dir'] / 'stdout.jsonl', lambda: False))
                captured.update(deepcopy(engine.runtime['checkpoints'][kwargs['execution_id']]))
                (workspace / 'proof.txt').write_bytes(b'changed after checkpoint')
                return {'status': 'failed', 'output': None, 'usage': {}, 'error': 'audit synthetic interruption'}
        engine.runner = Worker()
        engine.run(max_steps=1)
        target = next(e for e in engine.runtime['executions'].values() if e['role'] == 'research_preparation')
        final = engine.runtime['checkpoints'][target['id']]
        review = next(a for a in engine.runtime['queue'] if a['role'] == 'operational_review')
        workspace = fixture.root / 'review-audit'
        context = engine._context(review, workspace)
        restored = next(f for f in context['recovery_materials']['output_files'] if f['path'] == 'proof.txt')
        assert len(captured['evidence_files']) == 1
        assert engine.store.read(captured['evidence_files'][0]['artifact_ref']) == b'original evidence'
        assert final['sha256'] == captured['sha256']
        assert not final.get('evidence_files')
        assert not context['operational_evidence']['checkpoint_files']
        assert (workspace / restored['local_path']).read_bytes() == b'changed after checkpoint'
        return {'live_evidence_count': len(captured['evidence_files']),
                'same_checkpoint_sha256_after_end': True, 'original_artifact_still_in_git': True,
                'final_evidence_count': len(final.get('evidence_files', [])),
                'review_checkpoint_files': context['operational_evidence']['checkpoint_files'],
                'review_output_proof': (workspace / restored['local_path']).read_text()}
    finally:
        fixture.tearDown(); fixture.doCleanups()

def recovery_invalid_final():
    fixture = CurrentnessTests(); fixture.setUp()
    try:
        engine, _ = fixture.make()
        action = {'id': 'AC-audit', 'role': 'research_preparation'}
        execution = engine._register_execution(action, {'id': 'EX-audit', 'role': action['role'],
            'status': 'running', 'input_snapshot': engine.head, 'input_manifest': [], 'parent_execution_id': None})
        profile = engine.instance['execution_profiles'][execution['execution_profile_ref']['id']]
        execution['launch_ticket'] = dispatched_launch(execution['id'], profile)
        execution['process'] = {'job_name': execution['launch_ticket']['job_name']}
        workspace = Path(engine.instance['workspace']) / 'runs' / execution['id'] / 'workspace'
        workspace.mkdir(parents=True)
        (workspace / 'proof.txt').write_bytes(b'original evidence')
        (workspace / 'checkpoint.json').write_bytes(canonical_json(CHECKPOINT))
        engine.runtime.update(active_execution=execution['id'], status='running', queue=[action])
        engine._save()
        tracker = ObservationTracker(execution['id'], workspace, {'observation_mode': 'deadline_only'})
        engine._observe_running(execution['id'], tracker, ObservationBatch([], [], '2026-09-25T00:00:00Z',
            time.monotonic(), 0, 0, workspace / 'stdout.jsonl', lambda: False))
        previous = deepcopy(engine.runtime['checkpoints'][execution['id']])
        (workspace / 'checkpoint.json').write_bytes(b'{interrupted write')
        with patch('do_math.windows_job.named_job_empty', return_value=True), \
                patch('do_math.windows_job.owner_ended', return_value=True), engine.store.writer_lock():
            engine._recover_disappeared()
        recovered = engine.runtime['checkpoints'][execution['id']]
        assert previous['kind'] == 'worker_checkpoint'
        assert recovered['kind'] == 'observed_partial_state'
        assert engine.store.read(previous['artifact_ref']) == canonical_json(CHECKPOINT)
        context = engine._context({'role': 'operational_review', 'target': execution['id']}, fixture.root / 'review-recovery')
        assert context['operational_evidence']['checkpoint_status'] == 'not_preserved'
        return {'previous_kind': previous['kind'], 'recovered_kind': recovered['kind'],
                'previous_bytes_still_in_git': True,
                'review_checkpoint_status': context['operational_evidence']['checkpoint_status']}
    finally:
        fixture.tearDown(); fixture.doCleanups()

if __name__ == '__main__':
    result = {'regular_end': regular_end(), 'recovery_invalid_final': recovery_invalid_final()}
    path = Path(__file__).with_suffix('.json')
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))

"""A disappeared execution keeps its last valid checkpoint and records the invalid final one (``core_engine``).

The test starts from the restored public activation on the Sim, whose
configuration holds the legacy harness's settings (``CURRENTNESS_CONFIG``). The
running execution is registered and observed on the engine as the legacy test
did. Its launch owner has ended (its process ID now names another process,
another creation time) and no Job of its name holds a process, which the Jobs
port itself reports. The legacy test replaced ``windows_job.owner_ended`` and
``named_job_empty`` to say so.

The legacy module's other engine test, a checkpoint the owner captures while
the worker still runs, stays in ``test_checkpoint_persistence``: the product
tracker captures a checkpoint only from a live stream
(``ObservationTracker.observe``), and the Jobs fake runs the worker to its end
inside ``resume``, so the product runner delivers only terminated batches
(1f seam ledger 18).
"""
from copy import deepcopy
from pathlib import Path
import unittest

from do_math.canonical import canonical_json
from do_math.launch import ticket
from do_math.observations import ObservationTracker
from support.provider_live import batch
from support.sim import Sim, warm_template

setUpModule = warm_template
CHECKPOINT = {'current_claim': 'original evidence', 'evidence_paths': ['proof.txt'],
              'attempts': ['original checked'], 'remaining_work': ['continue'],
              'next_step': 'continue', 'progress_state': 'working'}


class CheckpointPersistenceTests(unittest.TestCase):
    def test_restart_preserves_last_valid_checkpoint_and_records_invalid_final_observation(self):
        sim = Sim.activated()
        engine = sim.engine
        action = {'id': 'AC-fixture', 'role': 'research_preparation'}
        execution = engine._register_execution(action, {'id': 'EX-fixture', 'role': action['role'],
            'status': 'running', 'input_snapshot': engine.head, 'input_manifest': [], 'parent_execution_id': None})
        profile = engine.instance['execution_profiles'][execution['execution_profile_ref']['id']]
        execution['launch_ticket'] = {**ticket(execution['id'], profile, jobs=sim.ports.jobs, clock=sim.clock),
                                      'phase': 'dispatched'}
        # The launch owner has ended: its process ID now names another process (another creation time).
        execution['launch_ticket']['owner'] = {**sim.jobs.owner_identity(), 'creation_filetime': '1'}
        # An admitted launch: its capacity holds the started Job's identity.
        execution['capacity'] = {'reservation_ids': [], 'provider': profile['ai']['provider'],
            'process': {'job_name': execution['launch_ticket']['job_name']}, 'local_termination': 'unknown'}
        workspace = Path(engine.instance['workspace']) / 'runs' / execution['id'] / 'workspace'
        workspace.mkdir(parents=True)
        (workspace / 'proof.txt').write_bytes(b'original evidence')
        (workspace / 'checkpoint.json').write_bytes(canonical_json(CHECKPOINT))
        engine.runtime.update(status='running', queue=[action])
        engine._save()
        tracker = ObservationTracker(execution['id'], workspace, {'observation_mode': 'deadline_only'}, time_port=sim.clock)
        engine._observe_running(execution['id'], tracker, batch(sim, [], workspace / 'stdout.jsonl'))
        previous = deepcopy(engine.runtime['checkpoints'][execution['id']])
        (workspace / 'checkpoint.json').write_bytes(b'{interrupted write')
        self.assertEqual((sim.jobs.owner_ended(execution['launch_ticket']['owner']),
                          sim.jobs.named_job_empty(execution['launch_ticket']['job_name'])), (True, True))
        with engine.store.writer_lock():
            engine._recover_disappeared()
        final = engine.runtime['checkpoints'][execution['id']]
        self.assertEqual(final['kind'], 'worker_checkpoint')
        self.assertEqual(final['artifact_ref'], previous['artifact_ref'])
        self.assertEqual(final['evidence_files'], previous['evidence_files'])
        self.assertEqual(final['final_observation']['checkpoint_status'], 'invalid')
        restored = engine.store.load()[2]['checkpoints'][execution['id']]
        self.assertEqual(restored, final)
        context = engine._context({'role': 'operational_review', 'target': execution['id']}, sim.root / 'review')
        self.assertEqual(context['operational_evidence']['checkpoint_status'], 'preserved')


if __name__ == '__main__':
    unittest.main()

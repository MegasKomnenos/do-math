"""Live checkpoints and purpose observations through real workers and storage."""
from copy import deepcopy
import json
import unittest

from do_math.canonical import canonical_json
from do_math.execution_profiles import resolve_profile, WORK_ROLES
from support.purpose_answers import STATEMENT
from support.engine_purpose import PurposeResponder, purpose_sim, drive
from support.live_finish_model import install, execution
from support.scheduling_parallel import round_robin


def setUpModule():
    purpose_sim(tool_review_window_seconds=1)


def observed_sim(mode, *, stop_observations=None):
    stop_observations = [] if stop_observations is None else stop_observations
    sim = purpose_sim(tool_review_window_seconds=1)
    sim.ports.calls.choose = round_robin()
    responder = sim.model.responder = PurposeResponder()
    responder.runner.observation = mode
    seen = []

    def hook(cli, context):
        if context['action']['role'] != 'research_work' or seen:
            return
        seen.append(cli.workspace)
        checkpoint = {'current_claim': STATEMENT, 'evidence_paths': ['argument.txt'],
            'attempts': ['Reconstructed Nat.add_zero'], 'remaining_work': ['Write the final report'],
            'next_step': 'Finish the explicit report', 'progress_state': 'working', 'counters': {'attempts': 1}}
        (cli.workspace / 'argument.txt').write_text('The domain is Nat; Nat.add_zero supplies the equality.', encoding='utf-8')
        (cli.workspace / 'checkpoint.json').write_bytes(canonical_json(checkpoint))
        try:
            cli.event({'type': 'item.completed', 'item': {'type': 'agent_message', 'id': 'm1', 'text': 'The Nat domain is fixed.'}})
            if mode == 'external_pause':
                sim.control('pause', text='Stop the current research after preserving its checkpoint')
            else:
                cli.event({'type': 'item.started', 'item': {'type': 'command_execution', 'id': 'observed-tool'}})
                feedback = cli.workspace / '.control/observation-feedback.json'
                cli.until(lambda: feedback.exists() and json.loads(feedback.read_bytes()).get('kind') == 'continue'
                          or (cli.workspace / '.control/stop-request.json').exists(), 'live review did not return')
                if mode == 'continue':
                    cli.event({'type': 'item.completed', 'item': {'type': 'command_execution', 'id': 'observed-tool'}})
                    return
            cli.until(lambda: False, 'owner did not terminate stopped work')
        finally:
            if mode in {'stop', 'external_pause'}:
                # JobTerminated unwinds this hook before FakeJob marks the Job done.
                # Keep the observation outside the worker: a missing request must
                # fail the test, not be absorbed as a worker interruption.
                worker = execution(sim, cli.workspace)
                stop_observations.append({'execution_id': worker['id'],
                    'stop_request_exists': (cli.workspace / '.control/stop-request.json').exists(),
                    'phase': 'cli_hook_finally', 'observed_at': sim.clock.now(),
                    'execution_status': worker['status'], 'ended_at': worker.get('ended_at')})

    install(sim, hook)
    return sim


class PurposeEngineTests(unittest.TestCase):
    def assert_stop_request_before_exit(self, observations, worker):
        self.assertEqual(len(observations), 1, 'The stopped CLI must record exactly one observation')
        observation = observations[0]
        self.assertEqual(observation['execution_id'], worker['id'])
        self.assertEqual(observation['phase'], 'cli_hook_finally')
        self.assertEqual(observation['execution_status'], 'stopping')
        self.assertIsNone(observation['ended_at'])
        self.assertLessEqual(worker['stop_observed_at'], observation['observed_at'])
        self.assertLessEqual(observation['observed_at'], worker['ended_at'])
        self.assertIs(observation['stop_request_exists'], True, 'Stop did not request a checkpoint before CLI exit')

    def test_live_continue_preserves_checkpoint_and_reserves_no_work_slot(self):
        sim = observed_sim('continue')
        drive(self, sim, lambda s: any(row['disposition']['kind'] == 'continue' and
              row['target_execution_id'] in s.runtime.get('checkpoints', {})
              for row in s.runtime.get('operational_dispositions', {}).values()))
        live = [e for e in sim.runtime['executions'].values() if e['role'] == 'operational_review' and e['action'].get('live')]
        self.assertEqual(len(live), 1)
        parent = sim.runtime['executions'][live[0]['action']['target']]
        self.assertTrue(resolve_profile(sim.instance['execution_profiles'], parent['execution_profile_ref'])['ai']['capacity_refs'])
        self.assertEqual(resolve_profile(sim.instance['execution_profiles'], live[0]['execution_profile_ref'])['ai']['capacity_refs'], [])
        self.assertEqual(live[0]['outcome'], 'output_accepted')
        self.assertFalse([r for r in sim.runtime['reservations'].values() if r['owner_id'] == live[0]['id'] and r['unit'] == 'execution'])
        self.assertEqual(sim.runtime['checkpoints'][parent['id']]['kind'], 'worker_checkpoint')
        self.assertTrue(any(r['target_execution_id'] == parent['id'] and r['disposition']['kind'] == 'continue'
                            for r in sim.runtime['operational_dispositions'].values()))

    def test_operating_review_runs_even_when_the_worker_used_the_last_work_call(self):
        sim = observed_sim('continue')
        drive(self, sim, lambda s: any(e['role'] == 'research_work' and e.get('outcome') == 'output_accepted'
                                     for e in s.runtime['executions'].values()))
        work = [e for e in sim.runtime['executions'].values() if e['role'] in WORK_ROLES]
        operating = [e for e in sim.runtime['executions'].values() if e['role'] == 'operational_review']
        self.assertEqual(len(work), 2)
        self.assertEqual(len(operating), 1)
        self.assertEqual(operating[0]['outcome'], 'output_accepted')
        self.assertEqual(resolve_profile(sim.instance['execution_profiles'], operating[0]['execution_profile_ref'])['ai']['capacity_refs'], [])

    def test_live_retry_stops_the_attempt_and_keeps_partial_artifacts_without_publishing_a_theorem(self):
        observations = []
        sim = observed_sim('stop', stop_observations=observations)
        drive(self, sim, lambda s: any(e.get('stop_requested') == 'operational_retry' and e['status'] == 'ended'
                                     for e in s.runtime['executions'].values()))
        worker = next(e for e in sim.runtime['executions'].values() if e['role'] == 'research_work')
        self.assertEqual(worker['outcome'], 'execution_incomplete')
        self.assertEqual(worker['stop_requested'], 'operational_retry')
        self.assertTrue(any(a.get('continuation_of') == worker['id'] for a in sim.runtime['queue']))
        self.assertTrue(any(f['path'] == 'argument.txt' for f in worker['output_files']))
        self.assertFalse(sim.instance['knowledge'])
        self.assert_stop_request_before_exit(observations, worker)

    def test_external_user_pause_is_processed_during_running_work(self):
        observations = []
        sim = observed_sim('external_pause', stop_observations=observations)
        drive(self, sim, lambda s: s.runtime['status'] == 'paused')
        self.assertEqual(sim.runtime['status'], 'paused')
        worker = next(e for e in sim.runtime['executions'].values() if e['role'] == 'research_work')
        self.assertEqual(worker['outcome'], 'cancelled')
        self.assertEqual(sim.runtime['checkpoints'][worker['id']]['kind'], 'worker_checkpoint')
        self.assertTrue(any(h.get('kind') == 'user_control' and h['request']['action'] == 'pause' for h in sim.runtime['history']))
        self.assertFalse(sim.instance['knowledge'])
        self.assert_stop_request_before_exit(observations, worker)


class CheckpointPersistenceTests(unittest.TestCase):
    def test_ended_review_receives_the_original_checkpoint_evidence(self):
        sim = purpose_sim(tool_review_window_seconds=1)
        captured = {}
        checkpoint = {'current_claim': 'original evidence', 'evidence_paths': ['proof.txt'],
            'attempts': ['original checked'], 'remaining_work': ['continue'], 'next_step': 'continue', 'progress_state': 'working'}

        def hook(cli, context):
            (cli.workspace / 'proof.txt').write_bytes(b'original evidence')
            (cli.workspace / 'checkpoint.json').write_bytes(canonical_json(checkpoint))
            eid = execution(sim, cli.workspace)['id']
            cli.until(lambda: eid in sim.runtime.get('checkpoints', {}), 'checkpoint was not captured live')
            captured.update(deepcopy(sim.runtime['checkpoints'][eid]))
            (cli.workspace / 'proof.txt').write_bytes(b'changed after checkpoint')
            return False

        install(sim, hook)
        sim.step()
        target = next(e for e in sim.runtime['executions'].values() if e['role'] == 'research_preparation')
        final = sim.runtime['checkpoints'][target['id']]
        self.assertEqual(final['sha256'], captured['sha256'])
        self.assertEqual(final.get('evidence_files'), captured['evidence_files'])
        review = next(a for a in sim.runtime['queue'] if a['role'] == 'operational_review')
        workspace = sim.root / 'review'
        context = sim.engine._context(review, workspace)
        files = context['operational_evidence']['checkpoint_files']
        self.assertEqual(len(files), 1)
        self.assertEqual((workspace / files[0]['local_path']).read_bytes(), b'original evidence')
        output = next(f for f in context['recovery_materials']['output_files'] if f['path'] == 'proof.txt')
        self.assertEqual((workspace / output['local_path']).read_bytes(), b'changed after checkpoint')

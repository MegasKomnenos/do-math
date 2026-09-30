"""Recovery of research work: an approved limited recovery's call under a user pause.

The module's other tests moved to the new system (tests/migration/dispositions/scheduling.1.json).
This one stays until the Sim's Jobs fake can keep a worker running while the
runner polls its stop flag: its second case stops the call with a new pause."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.engine import control, ResearchEngine
from purpose_fixtures import ActivatedPurposeHarness, common, formal_fixture, PurposeRunner
from research_fixtures import await_stop, local_job_runner, producer_result, restore_template, send_control
from state_fixtures import active_instance


def purpose_engine(root, instance_id):
    return ResearchEngine(root / 'repository', instance_id, runner=PurposeRunner(), formal_verifier=formal_fixture)


def paused_limited_recovery(root, shared, *, config):
    """``restore_template`` build: a user pause and an approved limited recovery of ``AC-limited``.

    Both the pause and the recovery decision go through public controls; the
    decision expires five minutes after the build. Returns the instance ID.
    """
    from datetime import datetime, timedelta, timezone
    instance_id = active_instance(root, shared, config=config)
    engine = purpose_engine(root, instance_id)
    engine.runtime['queue'] = []
    engine._enqueue('maintenance', engine.instance['id'], id='AC-limited',
        reason='Inspect the preserved recovery state and report remaining work')
    engine._save()
    send_control(engine, 'pause', text='Keep general research paused')
    action = next(a for a in engine.runtime['queue'] if a['id'] == 'AC-limited')
    grant_id = engine.instance['lifecycle']['adoption']['research_grant_ids'][0]
    send_control(engine, 'decision', config={'change': {
        'kind': 'limited_recovery', 'action_id': action['id'], 'grant_id': grant_id,
        'profile_ref': engine._select_model(action)['profile_ref'],
        'purpose': 'Inspect the preserved recovery state',
        'procedure': 'Read the supplied state and return a maintenance report',
        'expires_at': (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()}})
    return instance_id


class LimitedRecoveryCallTests(ActivatedPurposeHarness):
    def test_actual_ai_call_keeps_pause_and_honors_a_new_stop(self):
        for stop_again in (False, True):
            with self.subTest(stop_again=stop_again):
                self.root, instance_id = restore_template(paused_limited_recovery, config=self.fixture_config())
                engine, _ = self._engine(instance_id, PurposeRunner())
                calls = []
                case = self
                class Runner:
                    @local_job_runner
                    def run(inner, **arguments):
                        calls.append(arguments['execution_id'])
                        arguments['on_started']()
                        case.assertEqual(engine.runtime['status'], 'paused')
                        case.assertEqual(engine.instance['lifecycle']['state'], 'paused')
                        case.assertFalse(arguments['should_stop']())
                        if stop_again:
                            control(case.repo, engine.instance['id'], 'pause',
                                text='Stop the approved recovery too')
                            case.assertTrue(await_stop(arguments['should_stop']))
                            return {'status': 'stopped', 'output': None, 'usage': {},
                                    'error': 'New user pause observed'}
                        return producer_result({'status': 'completed', 'usage': {}, 'output': {
                            **common('Limited recovery inspection complete'),
                            'report': 'Inspected only the supplied recovery state.',
                            'remaining_work': []}}, arguments)
                engine.runner = Runner()
                engine.run(max_steps=1)
                self.assertEqual(len(calls), 1)
                execution = engine.runtime['executions'][calls[0]]
                self.assertEqual(execution['outcome'], 'cancelled' if stop_again else 'output_accepted',
                                 execution.get('error'))
                self.assertEqual(engine.runtime['status'], 'paused')
                self.assertEqual(engine.instance['lifecycle']['state'], 'paused')
                self.assertIn('user_pause', engine.runtime)


if __name__ == '__main__':
    unittest.main(verbosity=2)

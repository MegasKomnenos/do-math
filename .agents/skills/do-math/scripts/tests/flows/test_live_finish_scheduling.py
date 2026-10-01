"""Running research and limited recovery on the live Jobs port."""
from datetime import timedelta
import unittest

from do_math.model_policy import MODELS
from support.engine_lifecycle import applied, clear_work
from support.live_finish_model import install, execution
from support.model import amend, Answer
from support.scheduling_parallel import ready_work_sim, round_robin
from support.sim import Sim, warm_template
from support.provider_probes import ObservedCalls


def setUpModule():
    warm_template()
    ready_work_sim(3)
    ready_work_sim(3, observation_mode='periodic', observation_interval_seconds=1)
    ready_work_sim(2, observation_mode='periodic', observation_interval_seconds=1)


def continue_reviews(sim):
    sim.model.on('operational_review').reply(Answer(lambda out, ctx: {**out, 'disposition': {
        'kind': 'continue', 'basis_refs': [ctx['action']['target']], 'next_owner': 'research_work',
        'reason': 'The running target supplied progress evidence', 'next_review': None}}))


class LimitedRecoveryCallTests(unittest.TestCase):
    def test_actual_ai_call_keeps_pause_and_honors_a_new_stop(self):
        for stop_again in (False, True):
            with self.subTest(stop_again=stop_again):
                sim = Sim.activated()
                clear_work(sim)
                sim.engine._enqueue('maintenance', sim.instance_id, id='AC-limited',
                    reason='Inspect the preserved recovery state and report remaining work')
                sim.engine._save()
                applied(sim, 'pause', text='Keep general research paused')
                action = next(a for a in sim.runtime['queue'] if a['id'] == 'AC-limited')
                applied(sim, 'decision', config={'change': {'kind': 'limited_recovery', 'action_id': action['id'],
                    'grant_id': sim.instance['lifecycle']['adoption']['research_grant_ids'][0],
                    'profile_ref': sim.engine._select_model(action)['profile_ref'],
                    'purpose': 'Inspect the preserved recovery state',
                    'procedure': 'Read the supplied state and return a maintenance report',
                    'expires_at': (sim.clock.wall() + timedelta(minutes=5)).isoformat()}})
                calls = []

                def hook(cli, context):
                    calls.append(execution(sim, cli.workspace)['id'])
                    self.assertEqual(sim.runtime['status'], 'paused')
                    self.assertEqual(sim.instance['lifecycle']['state'], 'paused')
                    self.assertFalse(observed.captured('run')[-1]['should_stop']())
                    self.assertFalse((cli.workspace / '.control/stop-request.json').exists())
                    if stop_again:
                        sim.control('pause', text='Stop the approved recovery too')
                        cli.until(lambda: False, 'new pause did not stop the approved recovery')

                install(sim, hook)
                sim.model.on('maintenance').reply(amend(summary='Limited recovery inspection complete',
                    report='Inspected only the supplied recovery state.', remaining_work=[]))
                with ObservedCalls(run=sim.engine.runner.run) as observed:
                    sim.step()
                self.assertEqual(len(calls), 1)
                row = sim.runtime['executions'][calls[0]]
                self.assertEqual(row['outcome'], 'cancelled' if stop_again else 'output_accepted', row.get('error'))
                self.assertEqual(sim.runtime['status'], 'paused')
                self.assertEqual(sim.instance['lifecycle']['state'], 'paused')
                self.assertIn('user_pause', sim.runtime)
                self.assertEqual(observed.count('run'), 1)
                if stop_again:
                    self.assertTrue(observed.captured('run')[0]['should_stop']())


class ParallelEngineTests(unittest.TestCase):
    def test_pause_reaches_all_parallel_calls_and_releases_their_slots(self):
        sim = ready_work_sim(3)
        sim.ports.calls.choose = round_robin()
        entered = []

        def hook(cli, context):
            entered.append(execution(sim, cli.workspace)['id'])
            if len(entered) == 3:
                sim.control('pause', text='pause the whole instance')
            cli.until(lambda: False, 'pause did not terminate all parallel calls')

        install(sim, hook)
        state = sim.engine.run(max_steps=3)
        self.assertEqual(len(entered), 3)
        self.assertEqual(state['status'], 'paused')
        self.assertEqual(state['active_executions'], [])
        self.assertEqual(state['budget'][MODELS['high']]['used'], 0)
        self.assertEqual(len([e for e in sim.runtime['executions'].values() if e['role'] == 'research_work']), 3)
        self.assertTrue(all(sim.runtime['executions'][eid]['outcome'] == 'cancelled' for eid in entered))

    def test_live_operations_can_run_when_work_is_full_and_step_limit_is_reached(self):
        sim = ready_work_sim(3, observation_mode='periodic', observation_interval_seconds=1)
        sim.ports.calls.choose = round_robin()
        continue_reviews(sim)

        def hook(cli, context):
            if context['action']['role'] == 'research_work':
                cli.until(lambda: bool(sim.runtime.get('operational_dispositions')), 'operating slot did not run beside full work')

        install(sim, hook)
        sim.engine.run(max_steps=3)
        operating = [e for e in sim.runtime['executions'].values() if e['role'] == 'operational_review']
        self.assertTrue(operating)
        self.assertFalse([r for r in sim.runtime['reservations'].values()
                          if r['owner_id'] == operating[0]['id'] and r['unit'] == 'execution'])
        self.assertEqual(operating[0]['model'], MODELS['high'])
        if operating[0].get('result_disposition', {}).get('kind') == 'preserved_after_target_change':
            self.assertEqual(sim.runtime['executions'][operating[0]['action']['target']]['status'], 'ended')
        else:
            self.assertEqual(operating[0]['outcome'], 'output_accepted')

    def test_failed_live_review_stops_its_parent_and_preserves_independent_work(self):
        sim = ready_work_sim(2, observation_mode='periodic', observation_interval_seconds=1)
        sim.ports.calls.choose = round_robin()
        continue_reviews(sim)
        failed = []

        def hook(cli, context):
            if context['action']['role'] == 'operational_review':
                target = sim.runtime['executions'][context['action']['target']]['action']['target']
                if sim.runtime['tasks'][target]['title'] == '0':
                    failed.append(context['action']['target'])
                    return False
                return
            if context['task']['title'] == '0':
                cli.until(lambda: False, 'failed live review did not stop its parent')
            else:
                # Keep the independent call alive without aging it into a second idle review.
                from support.fakes.jobs import job_turn
                for _ in range(200):
                    if failed:
                        return
                    job_turn()
                raise AssertionError('the parent review did not fail')

        install(sim, hook)
        state = sim.engine.run(max_steps=2)
        work = [e for e in sim.runtime['executions'].values() if e['role'] == 'research_work']
        self.assertEqual(sum(e['outcome'] == 'output_accepted' for e in work), 1)
        self.assertNotEqual(state['status'], 'paused')

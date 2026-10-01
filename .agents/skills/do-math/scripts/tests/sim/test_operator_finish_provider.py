"""Published provider admission drives scheduler repair and HOLD cancellation."""
from dataclasses import replace
import unittest

from do_math import execution_lifecycle, scheduled_operator as operator
from do_math.engine import ResearchEngine
from do_math.git_store import GitStateStoreError
from do_math.provider_wait import epoch_seconds
from support.operator_finish_ports import Scheduler
from support.operator_finish_scene import Scene
from support.submission_receiver import held_ref
from support.sim import warm_template

setUpModule = warm_template


class ProviderWakeTests(unittest.TestCase):
    def test_saved_wait_repairs_schedule_once_and_publication_precedes_effect(self):
        from support.entry import entry
        _entry = entry()
        scene = Scene()
        scene.claude()
        scene.answer()
        scene.limited()
        result = scene.call(operator.recovery, failure={'kind': 'engine_unavailable', 'error': 'provider fixture'})
        self.assertEqual(result['outcome'], 'recovery_provider_limited')
        scheduler = Scheduler()
        scheduler.tasks = scene.ports.scheduler.tasks
        scene.ports = replace(scene.ports, scheduler=scheduler)
        engine = ResearchEngine(scene.args[0], scene.args[1], ports=scene.ports, codex_home=_entry.codex_home, environment=_entry.environment, host_id=_entry.host_id)
        scene.sim.engine = engine
        action = {'id': 'AC-held', 'role': 'research_preparation'}
        execution = engine._register_execution(action, {'id': 'EX-limited-work', 'role': action['role'], 'status': 'running'})
        for status in ('stopping', 'ended'):
            execution_lifecycle.transition_execution(execution, status, at=scene.ports.clock.now(),
                **({'outcome': 'execution_incomplete'} if status == 'ended' else {}))
        gate = engine._provider_status()['providers']['claude']
        engine._requeue_provider_action(execution['action'], execution['id'], gate)
        self.assertEqual(engine.runtime['queue'][-1]['dispatch_wait']['kind'], 'provider_limit')
        scheduler.error = OSError('scheduler unavailable')
        engine._publish_provider_result()
        _, _, saved = engine.store.load()
        self.assertEqual(saved['provider_wake']['status'], 'failed')
        self.assertEqual(saved['provider_waits']['PW-claude']['retry_at'], epoch_seconds(gate['retry_at']))
        def observe(action, arguments):
            _, _, published = engine.store.load()
            self.assertEqual(published['provider_waits']['PW-claude']['retry_at'], epoch_seconds(gate['retry_at']))
            self.assertIn('AC-held', [queued['id'] for queued in published['queue']])
        scheduler.error, scheduler.observe = None, observe
        observed = scene.call(operator.check)
        self.assertEqual(observed['provider_wake']['status'], 'scheduled')
        engine._publish_provider_result()
        scheduled = [args for action, args in scheduler.calls if action == 'schedule-wake']
        self.assertEqual(len(scheduled), 1)
        self.assertEqual(scheduled[0]['WakeAt'], gate['retry_at'])
        self.assertEqual(scheduled[0]['WakeKey'], 'claude:' + str(gate['generation']))
        calls_before = list(scheduler.calls)
        engine.runtime['history'].append({'kind': 'operator_finish_publication_probe'})
        with held_ref(scene.sim), self.assertRaisesRegex(GitStateStoreError, 'state ref changed before the .* compare-and-swap'):
            engine._publish_provider_result()
        self.assertEqual(scheduler.calls, calls_before)
        operator.hold(scene.workspace, reason='Synthetic HOLD', clock=scene.ports.clock)
        self.assertEqual(scene.call(operator.check)['outcome'], 'held')
        self.assertEqual(scheduler.calls, calls_before)
        actual = operator.reconcile_wake(*scene.args, facts=operator.supervision_facts(engine.instance, engine.runtime),
            providers=engine._provider_status()['providers'], scheduler=scheduler, clock=scene.ports.clock)
        self.assertEqual(actual['status'], 'held')
        self.assertEqual(scheduler.calls[-1][0], 'cancel-wake')
        self.assertEqual(len(scheduler.calls), len(calls_before) + 1)
        self.assertFalse((scene.workspace / 'operator/wake-registration.json').exists())

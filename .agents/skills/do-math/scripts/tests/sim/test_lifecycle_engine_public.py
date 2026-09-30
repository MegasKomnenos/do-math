"""The lifecycle through public controls and restarts on the Sim (``engine.control``, ``ResearchEngine``).

A new instance comes from the public ``initialize`` (a Sim without activation);
an active one is a restore of this process's public activation
(``Sim.activated()``), whose build ran the public initialization, controls,
probe, trust and the interpretation calls through the worker and model double.
A restart is a new engine on the same repository and ports (``sim.restart()``).
"""
from copy import deepcopy
from datetime import datetime, timedelta
import tempfile
import unittest

from do_math.engine import ResearchEngine
from do_math.initialization import original_input_bytes
from support.engine_lifecycle import applied
from support.sim import Sim, warm_template

setUpModule = warm_template


def new_instance(test, **options):
    """A Sim of a publicly initialized instance; removed with ``test``."""
    directory = tempfile.TemporaryDirectory()
    test.addCleanup(directory.cleanup)
    return Sim(directory.name, **options)


class InitializingLifecycleTests(unittest.TestCase):
    def test_public_utc_watermark_is_published_only_with_normal_change(self):
        sim = new_instance(self, goal='Preserve this original input')
        engine = sim.engine
        engine._save()  # Establish any ordinary derived runtime fields first.
        head = engine.head
        initial = datetime.fromisoformat(engine.runtime['last_observed_utc'])
        observed = initial + timedelta(hours=2)
        sim.clock.set_wall(observed)  # the wall clock moves; the monotonic clock stays
        engine._require_action_clock()
        engine._save()
        self.assertEqual(engine.head, head, 'clock observation alone created a commit')
        engine.instance['title'] = 'Ordinary state update'
        engine._save()
        self.assertEqual(engine.runtime['last_observed_utc'], observed.isoformat())
        restarted = ResearchEngine(sim.repository, sim.instance_id, ports=sim.ports)
        sim.clock.set_wall(observed - timedelta(microseconds=1))
        self.assertEqual(restarted._clock_guard()['reason'], 'persisted_utc_regression')
        # A later rejected sample does not revoke the prior trusted sample.
        sim.clock.set_wall(observed + timedelta(hours=1))
        trusted = engine._require_action_clock()
        sim.clock.set_wall(observed + timedelta(minutes=30))
        self.assertFalse(engine._clock_guard()['usable'])
        engine._pause_lifecycle('clock_regression')
        engine._save()
        self.assertEqual(engine.store.load()[2]['last_observed_utc'], trusted)

    def test_public_unicode_original_survives_restart(self):
        source = 'Cafe\u0301'  # a combining accent, not the precomposed letter
        sim = new_instance(self, goal=source)
        sim.restart()
        self.assertEqual(original_input_bytes(sim.instance['lifecycle']['immutable_input']), source.encode())

    def test_public_initializing_pause_resume_preserves_source_and_missing(self):
        sim = new_instance(self, goal='Preserve this original input')
        source = deepcopy(sim.runtime['inputs'])
        applied(sim, 'pause', config={})
        self.assertEqual(sim.runtime['resume_lifecycle'], 'initializing')
        applied(sim, 'resume', config={})
        sim.restart()
        self.assertEqual(sim.instance['lifecycle']['state'], 'initializing')
        self.assertEqual(sim.runtime['inputs'], source)
        self.assertIn('independent_intent', sim.instance['lifecycle']['activation']['missing'])
        self.assertNotIn('missing', sim.runtime['availability'])
        applied(sim, 'close', config={})
        self.assertTrue(sim.instance['lifecycle']['permanently_closed'])
        for action in ('pause', 'resume'):
            # After the resume, the same pause is a new request; a closed instance rejects both.
            request = sim.control(action, text='lifecycle test control: ' + action, config={})
            sim.engine.process_controls()
            self.assertEqual(sim.engine.control_result(request['request_id'])['effect'], 'rejected', action)
        sim.restart()
        self.assertEqual(sim.runtime['status'], 'closed')
        self.assertTrue(sim.instance['lifecycle']['permanently_closed'])

    def test_new_instance_is_v5_initializing_without_implicit_authority(self):
        sim = new_instance(self, goal='Prove the stated goal')
        head, instance, runtime = sim.engine.store.load()
        self.assertEqual(runtime['status'], 'initializing')
        self.assertEqual(runtime['queue'], [])
        self.assertEqual(instance['grants'], {})
        self.assertEqual(head, sim.engine.head)
        status = sim.engine.run(max_steps=1)
        self.assertEqual(status['status'], 'initializing')
        self.assertEqual((sim.model.calls, sim.jobs.launched), ([], []), 'the first run calls no model')


class ActiveLifecycleTests(unittest.TestCase):
    def test_public_call_mode_init_activate_pause_resume_and_persistence(self):
        # The public initialization and activation built this process's template; this copy is their result.
        sim = Sim.activated()
        self.assertEqual(sim.instance['lifecycle']['state'], 'active')
        self.assertEqual(len(sim.runtime['intent_imports']), 1)
        self.assertTrue(sim.instance['active_trust_environment'])
        queued = deepcopy(sim.runtime['queue'])
        attempts = set(sim.runtime['executions'])
        sim.engine.run(until_active=True)
        self.assertEqual(set(sim.runtime['executions']), attempts)
        self.assertEqual(sim.runtime['queue'], queued)
        applied(sim, 'pause', config={})
        self.assertEqual(sim.runtime['resume_lifecycle'], 'active')
        applied(sim, 'resume', config={})
        self.assertEqual(sim.instance['lifecycle']['state'], 'active')
        sim.restart()
        self.assertEqual(sim.instance['lifecycle']['state'], 'active')
        self.assertNotIn('task_readiness', sim.runtime)
        self.assertNotIn('initial_request', sim.instance['lifecycle'])


if __name__ == '__main__':
    unittest.main()

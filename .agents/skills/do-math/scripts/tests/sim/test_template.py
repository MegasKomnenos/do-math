"""The Sim template (설계 4.4): each restore is the same active instance, and nothing one test does reaches the next."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from support.sim import Sim, assert_template_quiescent, built, warm_template

setUpModule = warm_template

_BUILDS = []


def _initialized(root, shared, *, config=None):
    _BUILDS.append(deepcopy(config))
    return Sim(root, shared=shared, config=config)


def _fails(root, shared, *, marker='failed'):
    _BUILDS.append(marker)
    raise ValueError('explicit template build failure')


class TemplateTests(unittest.TestCase):
    def test_a_restore_is_active_with_the_clock_continuing_and_forgets_the_previous_restore(self):
        """About 3 s, over the 2 s Sim budget: its two restores (about 1.1 s each) are what it checks."""
        first = Sim.activated()
        self.assertEqual(first.instance['lifecycle']['state'], 'active')
        self.assertEqual(first.real_time_leaks(), [])
        next_id = first.clock.new_id('XX')
        first.control('pause', text='pause the restored copy')
        first.engine.process_controls()
        self.assertEqual(first.runtime['status'], 'paused')

        second = Sim.activated()
        self.assertEqual(second.instance['lifecycle']['state'], 'active')
        self.assertNotEqual(second.runtime['status'], 'paused')
        self.assertEqual(second.clock.new_id('XX'), next_id, 'the clock continues from the template, not from the last test')

    def test_a_template_takes_no_options(self):
        with self.assertRaisesRegex(ValueError, 'template Sim has the default options'):
            Sim.activated(goal='another goal')

    def test_builder_receives_configuration_and_defaults_share_the_same_absolute_path(self):
        first = built('template-default-contract', _initialized)
        root, head = first.root, first.engine.head
        self.assertEqual(first.instance['lifecycle']['state'], 'initializing')
        again = built('template-default-contract', _initialized, config=None)
        self.assertEqual((again.root, again.engine.head), (root, head))
        configured = built('template-config-contract', _initialized, config={'call_timeout_seconds': 71})
        self.assertEqual(configured.instance['config']['call_timeout_seconds'], 71)
        same = built('template-config-contract', _initialized, config={'call_timeout_seconds': 71})
        self.assertEqual(same.root, configured.root)
        other = built('template-config-contract', _initialized, config={'call_timeout_seconds': 72})
        self.assertNotEqual(other.root, configured.root)
        self.assertEqual(other.instance['config']['call_timeout_seconds'], 72)

    def test_failed_build_is_not_retried_for_the_same_normalized_inputs(self):
        before = len(_BUILDS)
        with self.assertRaisesRegex(ValueError, 'explicit template build failure'):
            built('template-failure-contract', _fails)
        with self.assertRaisesRegex(AssertionError, 'failed to build earlier'):
            built('template-failure-contract', _fails, marker='failed')
        self.assertEqual(_BUILDS[before:], ['failed'])

    def test_parked_actions_are_copyable_only_after_execution_and_ports_settle(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        sim = Sim(root)
        sim.runtime['waiting_actions'] = {'AC-parked': {'reason': 'explicit initialization wait'}}
        assert_template_quiescent(sim)
        sim.runtime['executions']['EX-pending'] = {'id': 'EX-pending', 'status': 'queued'}
        with self.assertRaisesRegex(AssertionError, 'pending_executions.*EX-pending'):
            assert_template_quiescent(sim)
        sim.runtime['executions']['EX-pending']['status'] = 'ended'
        sim.runtime['reservations']['RS-held'] = {'id': 'RS-held', 'state': 'held'}
        with self.assertRaisesRegex(AssertionError, 'held_reservations.*RS-held'):
            assert_template_quiescent(sim)
        sim.runtime['reservations']['RS-held']['state'] = 'released'
        sim.jobs.programs.insert(0, (lambda argv: argv == ['template-job'], lambda *args: 0))
        job = sim.jobs.launch(['template-job'])
        try:
            with self.assertRaisesRegex(AssertionError, "jobs.*40004"):
                assert_template_quiescent(sim)
            job.resume()
            with self.assertRaisesRegex(AssertionError, "jobs.*40004"):
                assert_template_quiescent(sim)
        finally:
            job.close()
        assert_template_quiescent(sim)

    def test_an_uncollected_call_cannot_be_copied(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        sim = Sim(root)
        calls = sim.ports.calls.new()
        def continuation():
            yield
        generator = continuation()
        next(generator)
        calls.start_call(generator, lambda: {'status': 'completed'}, {}, execution_id='EX-call')
        try:
            with self.assertRaisesRegex(AssertionError, "calls.*0"):
                assert_template_quiescent(sim)
            calls.wait(0)
            with self.assertRaisesRegex(AssertionError, "calls.*0"):
                assert_template_quiescent(sim)
            calls.collect()
            assert_template_quiescent(sim)
        finally:
            calls.close()


if __name__ == '__main__':
    unittest.main()

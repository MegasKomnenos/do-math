"""The Sim template (설계 4.4): each restore is the same active instance, and nothing one test does reaches the next."""
from copy import deepcopy
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from support import branch_gate
from support.sim import Sim, _Template, assert_template_quiescent, built, warm_built, warm_template
from do_math.file_io import file_fingerprint

setUpModule = warm_template

_BUILDS = []
_WARM_PRODUCERS = []


def _warm_initialized(root, shared, *, config=None):
    (Path(__file__).resolve().parents[1] / 'budgets.json').read_bytes()
    sim = _initialized(root, shared, config=config)
    _WARM_PRODUCERS.append(sim)
    return sim


def _initialized(root, shared, *, config=None):
    _BUILDS.append(deepcopy(config))
    return Sim(root, shared=shared, config=config)


def _fails(root, shared, *, marker='failed'):
    _BUILDS.append(marker)
    raise ValueError('explicit template build failure')


class TemplateTests(unittest.TestCase):
    def test_named_warming_leaves_the_exact_producer_tree_for_a_fresh_first_consumer(self):
        before = len(_BUILDS)
        with mock.patch.object(_Template, 'restore', autospec=True, side_effect=_Template.restore) as restores:
            template = warm_built('template-warm-first', _warm_initialized)
            self.assertIs(warm_built('template-warm-first', _warm_initialized, config=None), template)
            self.assertFalse(template.used)
            self.assertEqual(restores.call_count, 0)
            producer = _WARM_PRODUCERS[-1]
            state = deepcopy(producer.process_state())
            instance, runtime = deepcopy(producer.instance), deepcopy(producer.runtime)
            inventory = {path.relative_to(template.live): (path.read_bytes(), file_fingerprint(path))
                         for path in template.live.rglob('*') if path.is_file()}
            first = built('template-warm-first', _warm_initialized, config=None)
            self.assertEqual(restores.call_count, 1)
            self.assertTrue(template.used)
            self.assertEqual((first.root, first.shared, first.instance_id, first.engine.head),
                             (producer.root, producer.shared, producer.instance_id, producer.engine.head))
            self.assertEqual((first.instance, first.runtime, first.process_state()), (instance, runtime, state))
            self.assertEqual({path.relative_to(first.root): (path.read_bytes(), file_fingerprint(path))
                              for path in first.root.rglob('*') if path.is_file()}, inventory)
            for name in ('engine', 'model', 'lean', 'jobs', 'ports', 'clock'):
                self.assertIsNot(getattr(first, name), getattr(producer, name))
            self.assertIsNot(first.engine.store, producer.engine.store)
            self.assertIsNot(first.engine.runner, producer.engine.runner)
            self.assertEqual(first.engine._task_readiness, {})
            first._apply('configure', config={'call_timeout_seconds': 71})
            self.assertNotEqual(first.engine.store.load()[1], instance)
            first.advance(123)
            first.jobs._next_pid += 80
            first.jobs.owner['pid'] += 80
            first.ports.git_backend.worktrees[first.root] = {'consumer': ['private']}
            first.ports.git_backend.objects['consumer-only'] = {'object': ('blob', b'private')}
            first.engine._task_readiness['consumer-only'] = {'state': 'not_ready'}
            (first.root / 'consumer-only.txt').write_text('discard on next restore', encoding='utf-8')
            second = built('template-warm-first', _warm_initialized)
            self.assertEqual(restores.call_count, 2)
            self.assertEqual((second.instance, second.runtime, second.process_state()), (instance, runtime, state))
            self.assertEqual(second.engine.store.load(), (second.engine.head, instance, runtime))
            self.assertEqual(second.engine._task_readiness, {})
            self.assertFalse((second.root / 'consumer-only.txt').exists())
            self.assertIsNot(second.engine, first.engine)
            self.assertIsNot(second.engine.store, first.engine.store)
            self.assertIsNot(second.engine.runner, first.engine.runner)
        self.assertEqual(_BUILDS[before:], [None])

    def test_warmed_builder_and_fixture_inputs_are_attributed_to_both_consumers(self):
        tests = ['sim.test_template.Warm.test_first', 'sim.test_template.Warm.test_second']
        root = Path(__file__).resolve().parents[6]
        measurement = branch_gate.Measurement(root)
        measurement.calls = branch_gate.FunctionRecorder(str(branch_gate.SCRIPTS), tool=4)
        branch_gate._install_hook()
        with mock.patch.object(branch_gate, '_ACTIVE', measurement), mock.patch.object(branch_gate, '_PAUSED', False):
            measurement.calls.start()
            try:
                measurement.context = branch_gate.fixture_label(None, tests[0])
                measurement.calls.switch(measurement.context)
                template = warm_built('template-warm-attribution', _warm_initialized)
                self.assertEqual(dict(measurement.calls.users), {})
                for test in tests:
                    measurement.context = test
                    measurement.calls.switch(test)
                    built('template-warm-attribution', _warm_initialized, config=None)
                self.assertEqual(measurement.calls.users[template.key], set(tests))
            finally:
                measurement.calls.stop()
        entered = measurement.entered()
        self.assertIn(_warm_initialized.__code__, measurement.calls.entered[branch_gate.SHARED + template.key])
        product = (branch_gate.SCRIPTS / 'do_math' / 'engine.py').relative_to(root).as_posix()
        inputs = (branch_gate.TESTS / 'budgets.json').relative_to(root).as_posix()
        index = branch_gate.build_index(entered, tests, measurement.opens, measurement.import_opens,
            {product: 'product', inputs: 'input'}, 'pending',
            scripts_prefix=branch_gate.SCRIPTS.relative_to(root).as_posix(),
            input_dependencies=measurement.input_dependencies())
        self.assertEqual(index['files'][product]['functions']['initialize'], [0, 1])
        self.assertEqual(index['files'][inputs]['readers'], [0, 1])

    def test_restore_preserves_every_shared_file_byte_and_stat_fingerprint(self):
        def inventory(root):
            return {path.relative_to(root).as_posix():
                    (hashlib.sha256(path.read_bytes()).hexdigest(), file_fingerprint(path))
                    for path in root.rglob('*') if path.is_file()}
        first = Sim.activated()
        shared = first.shared
        initial_status = first.runtime['status']
        before = inventory(shared)
        self.assertTrue(before, 'no shared trust files were examined')
        first.control('pause', text='Change only the live restored instance.')
        first.engine.process_controls()
        self.assertEqual(inventory(shared), before)
        second = Sim.activated()
        self.assertEqual(second.shared, shared)
        self.assertEqual(inventory(second.shared), before)
        self.assertEqual(second.runtime['status'], initial_status)
        self.assertEqual(inventory(shared), before)

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
        warmed = warm_built('template-config-contract', _initialized, config={'call_timeout_seconds': 71})
        configured = built('template-config-contract', _initialized, config={'call_timeout_seconds': 71})
        self.assertEqual(configured.root, warmed.live)
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
        with self.assertRaisesRegex(AssertionError, "template-failure-contract.*_fails.*failed.*failed to build earlier"):
            built('template-failure-contract', _fails, marker='failed')
        self.assertEqual(_BUILDS[before:], ['failed'])
        independent = built('template-failure-contract', _initialized)
        self.assertEqual(independent.instance['lifecycle']['state'], 'initializing')

    def test_failure_is_sticky_across_warming_and_consumption_in_both_orders(self):
        for first, second in ((warm_built, built), (built, warm_built)):
            with self.subTest(first=first.__name__):
                name = 'template-warm-failure-' + first.__name__
                before = len(_BUILDS)
                with self.assertRaisesRegex(ValueError, '^explicit template build failure$'):
                    first(name, _fails)
                for consume in (first, second):
                    with self.assertRaisesRegex(AssertionError, 'failed to build earlier in this process'):
                        consume(name, _fails, marker='failed')
                with self.assertRaisesRegex(ValueError, '^explicit template build failure$'):
                    second(name, _fails, marker='different')
                self.assertEqual(_BUILDS[before:], ['failed', 'different'])

    def test_parked_actions_are_copyable_only_after_execution_and_ports_settle(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        sim = Sim(root)
        sim.runtime['waiting_actions'] = {'AC-parked': {'reason': 'explicit initialization wait'}}
        sim.runtime['queue'] = [{'id': 'AC-future', 'role': 'maintenance'}]
        sim.runtime['questions'] = [{'id': 'Q-unresolved'}]
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

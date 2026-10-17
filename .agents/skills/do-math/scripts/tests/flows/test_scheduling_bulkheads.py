"""One owner unit fails while another uses the real worker, receiver and settlement."""
from copy import deepcopy
import hashlib
import json
import unittest

from support.owner_failure_cases import FailOnce, publication_wait, reading_sealed_output
from support.scheduling_parallel import ready_work_sim
from support.scheduling_return_observer import OwnerProbe, assert_drained, assert_owned


class OwnerBulkheadTests(unittest.TestCase):
    def test_unreadable_or_changed_sealed_input_is_held_once_while_another_unit_finishes(self):
        from contextlib import nullcontext
        from support.engine_context import damage
        for kind in ('read', 'hash'):
            with self.subTest(kind=kind):
                sim = ready_work_sim(2)
                wait, producer = publication_wait(sim)
                source = producer['submission_intent']['output_ref']
                original = sim.engine.store.read(source)
                if kind == 'hash':
                    # Same length, still JSON: presence/length inspection cannot stand in for the seal.
                    changed = original.replace(b'a', b'b', 1)
                    self.assertNotEqual(changed, original)
                    self.assertEqual(len(changed), len(original))
                    damage(sim.engine.store, source, changed)
                sim.restart()
                fault = (FailOnce(sim.ports.git_backend.read_objects, lambda args: reading_sealed_output(producer),
                                 OSError('fixture: this sealed Git input is unreadable'))
                         if kind == 'read' else nullcontext())
                with fault as injected, OwnerProbe(sim) as probe:
                    answer = sim.engine.run(max_steps=1)
                self.assertIsInstance(answer, dict)
                assert_drained(self, sim, probe)
                if kind == 'read':
                    self.assertEqual(len(injected.hits), 1)
                held = deepcopy(sim.runtime['waiting_actions'][wait['action']['id']])
                self.assertEqual(held['kind'], 'submission_failure')
                message = ('cannot read output_ref' if kind == 'read' else 'sealed output_ref hash differs')
                self.assertIn(message, held['reason'])
                self.assertIn(source, held['reason'])
                self.assertEqual(len(sim.model.calls), 2)
                self.assertEqual(sim.runtime['executions'][producer['id']]['outcome'], 'execution_incomplete')
                self.assertEqual(sim.runtime['executions'][producer['id']]['owner_activity_id'], producer['owner_activity_id'])
                self.assertEqual(sim.runtime['executions'][producer['id']]['capacity'], producer['capacity'])
                self.assertEqual(sim.engine.store.read(source), original if kind == 'read' else changed)
                sim.restart()
                sim.engine.process_controls()
                self.assertEqual(sim.runtime['waiting_actions'][wait['action']['id']], held)
                self.assertEqual(len([row for row in sim.runtime['history']
                                     if row.get('kind') == 'submission_publication_failed']), 1)

    def test_submission_implementation_failure_keeps_the_raw_result_and_independent_completion(self):
        sim = ready_work_sim(2)
        failed, other = deepcopy(sim.runtime['queue'])
        with FailOnce(sim.engine._apply_submission_bundles,
                lambda args: sim.runtime['executions'][args['execution_id']]['action']['id'] == failed['id'],
                RuntimeError('fixture: submission application failed')) as fault, OwnerProbe(sim) as probe:
            answer = sim.engine.run(max_steps=2)
        self.assertIsInstance(answer, dict)
        self.assertEqual(len(fault.hits), 1)
        assert_drained(self, sim, probe)
        stored = sim.engine.store.load()[2]
        wait = deepcopy(stored['waiting_actions'][failed['id']])
        execution = deepcopy(stored['executions'][wait['execution_id']])
        self.assertEqual((wait['kind'], wait['reason']), ('submission_failure', 'fixture: submission application failed'))
        self.assertEqual((execution['status'], execution['outcome']), ('ended', 'execution_incomplete'))
        raw = sim.engine.store.read(execution['result_ref'])
        result = json.loads(raw)
        self.assertEqual(result['status'], 'completed')  # Provider success is distinct from failed domain application.
        self.assertEqual(result['output'], sim.model.calls[0]['output'])
        source = execution['submission_intent']['output_ref']
        sealed = sim.engine.store.read(source)
        self.assertEqual(hashlib.sha256(sealed).hexdigest(), execution['submission_intent']['output_sha256'])
        independent, = [row for row in stored['executions'].values() if row['action'].get('id') == other['id']]
        self.assertEqual(independent['outcome'], 'output_accepted')
        assert_owned(self, stored, execution['id'])
        sim.restart()
        sim.engine.process_controls()
        self.assertEqual(sim.runtime['executions'][execution['id']], execution)
        self.assertEqual(sim.runtime['waiting_actions'][failed['id']], wait)
        self.assertEqual(sim.engine.store.read(execution['result_ref']), raw)
        self.assertEqual(sim.engine.store.read(source), sealed)

    def test_upkeep_implementation_failure_parks_one_publication_without_replaying_it(self):
        sim = ready_work_sim(2)
        wait, producer = publication_wait(sim)
        source = producer['submission_intent']['output_ref']
        raw = sim.engine.store.read(source)
        sim.restart()
        with FailOnce(sim.engine._receive_submission,
                lambda args: args['execution_id'] == producer['id'] and args.get('preserved'),
                RuntimeError('fixture: saved submission receipt failed')) as fault, OwnerProbe(sim) as probe:
            answer = sim.engine.run(max_steps=1)
        self.assertIsInstance(answer, dict)
        self.assertEqual(len(fault.hits), 1)
        assert_drained(self, sim, probe)
        held = deepcopy(sim.runtime['waiting_actions'][wait['action']['id']])
        self.assertEqual((held['kind'], held['reason']),
            ('submission_failure', 'RuntimeError: fixture: saved submission receipt failed'))
        self.assertEqual(len(sim.model.calls), 2)
        self.assertEqual(sim.runtime['executions'][producer['id']]['outcome'], 'execution_incomplete')
        self.assertTrue(any(row['outcome'] == 'output_accepted' and row['action'].get('id') != wait['action']['id']
                            and row['role'] == 'research_work' for row in sim.runtime['executions'].values()))
        self.assertEqual(sim.engine.store.read(source), raw)
        sim.restart()
        sim.engine.process_controls()
        self.assertEqual(sim.runtime['waiting_actions'][wait['action']['id']], held)
        self.assertEqual(sim.engine.store.read(source), raw)

    def test_control_implementation_failure_is_rejected_once_before_independent_work(self):
        sim = ready_work_sim(1)
        bad = sim.control('configure', config={'plan_settle_seconds': 3})
        good = sim.control('request', config={'role': 'maintenance'}, text='independent request')
        with FailOnce(sim.engine._configure_candidate, lambda args: True,
                RuntimeError('fixture: configuration candidate failed')) as fault, OwnerProbe(sim) as probe:
            answer = sim.engine.run(max_steps=1)
        self.assertIsInstance(answer, dict)
        self.assertEqual(len(fault.hits), 1)
        assert_drained(self, sim, probe)
        receipt = sim.engine.control_result(bad['request_id'])
        self.assertEqual((receipt['effect'], receipt['reason']),
            ('rejected', 'RuntimeError: fixture: configuration candidate failed'))
        self.assertEqual(sim.engine.control_result(good['request_id'])['effect'], 'applied')
        self.assertEqual(len(sim.model.calls), 1)
        self.assertEqual(sim.model.calls[0]['role'], 'research_work')
        state = deepcopy(sim.engine.store.load())
        sim.restart()
        sim.control('configure', config={'plan_settle_seconds': 3}, request_id=bad['request_id'])
        sim.engine.process_controls()
        self.assertEqual(sim.engine.store.load(), state)
        self.assertEqual(sim.runtime['processed_controls'].count(bad['request_id']), 1)
        diagnostic, = [row for row in sim.runtime['history'] if row.get('kind') == 'control_application_failed']
        self.assertEqual(diagnostic['request']['id'], bad['request_id'])
        self.assertIn('RuntimeError: fixture: configuration candidate failed', diagnostic['traceback'])

    def test_observation_implementation_failure_stops_only_its_call_and_preserves_the_reason(self):
        sim = ready_work_sim(2)
        failed, other = deepcopy(sim.runtime['queue'])
        with FailOnce(sim.engine._observe_running,
                lambda args: sim.runtime['executions'][args['execution_id']]['action']['id'] == failed['id'],
                RuntimeError('fixture: observation application failed')) as fault, OwnerProbe(sim) as probe:
            answer = sim.engine.run(max_steps=2)
        self.assertIsInstance(answer, dict)
        self.assertEqual(len(fault.hits), 1)
        assert_drained(self, sim, probe)
        stored = sim.engine.store.load()[2]
        execution, = [row for row in stored['executions'].values() if row['action'].get('id') == failed['id']]
        independent, = [row for row in stored['executions'].values() if row['action'].get('id') == other['id']]
        self.assertEqual((execution['status'], execution['outcome']), ('ended', 'execution_incomplete'))
        self.assertEqual(execution['stop_requested'], 'observation_failed: RuntimeError: fixture: observation application failed')
        self.assertEqual(independent['outcome'], 'output_accepted')
        self.assertTrue(sim.engine.store.read(execution['result_ref']))
        assert_owned(self, stored, execution['id'])
        self.assertEqual(execution['capacity']['local_termination'], 'confirmed')
        sim.restart()
        sim.engine.process_controls()
        self.assertEqual(sim.runtime['executions'][execution['id']], execution)
        self.assertFalse(any(row['id'] == failed['id'] for row in sim.runtime['queue']))

    def test_failed_input_preparation_waits_once_while_independent_work_finishes(self):
        sim = ready_work_sim(2)
        failed, other = deepcopy(sim.runtime['queue'])
        before = set(sim.runtime['executions'])
        error = RuntimeError('fixture: this input preparation failed')
        with FailOnce(sim.engine._context,
                lambda args: args['action']['id'] == failed['id'], error) as fault, OwnerProbe(sim) as probe:
            answer = sim.engine.run(max_steps=2)
        self.assertIsInstance(answer, dict)
        self.assertEqual(len(fault.hits), 1)
        assert_drained(self, sim, probe)
        stored = sim.engine.store.load()[2]
        wait = deepcopy(stored['waiting_actions'][failed['id']])
        execution = deepcopy(stored['executions'][wait['execution_id']])
        self.assertEqual((execution['status'], execution['outcome']), ('ended', 'start_failed'))
        self.assertEqual(wait['reason'], 'RuntimeError: fixture: this input preparation failed')
        self.assertEqual(wait['input_snapshot'], execution['input_snapshot'])
        self.assertNotIn('capacity', execution)
        self.assertEqual(wait['action']['owner_activity_id'], execution['owner_activity_id'])
        assert_owned(self, stored, execution['id'])
        added = [row for eid, row in stored['executions'].items() if eid not in before]
        self.assertEqual(len(added), 2)
        independent, = [row for row in added if row['action']['id'] == other['id']]
        self.assertEqual(independent['outcome'], 'output_accepted')
        self.assertEqual(independent['capacity']['local_termination'], 'confirmed')
        self.assertEqual([row['action']['id'] for row in sim.model.calls], [other['id']])
        sim.restart()
        # A zero-dispatch control pass cannot replay the failed input preparation.
        sim.engine.process_controls()
        self.assertEqual(sim.runtime['waiting_actions'][failed['id']], wait)
        self.assertEqual(sim.runtime['executions'][execution['id']], execution)
        self.assertFalse(any(row['id'] == failed['id'] for row in sim.runtime['queue']))
        self.assertEqual(len(sim.model.calls), 1)

"""4-B/13-B: every failed-action kind is produced and leaves by its real contract."""
from copy import deepcopy
import tempfile
import unittest

from do_math.wait_rules import FAILED_ACTION_WAITS
from support.engine_lifecycle import clear_work
from support.failed_actions import failure_sim, failed_action_scene
from do_math.session_slots import local_termination_confirmed, held_reservations
from support.scheduling_model import explicit, scenario_model
from support.scheduling_recovery import empty_plan
from support.wait_reporting import assert_wait_report


def setUpModule():
    for kind in FAILED_ACTION_WAITS:
        if kind != 'submission_failure':
            failure_sim(kind)


class PublicationFailureContractTests(unittest.TestCase):
    def test_failed_publication_receipt_settles_the_confirmed_local_process_before_diagnosis(self):
        with tempfile.TemporaryDirectory() as directory:
            sim = failed_action_scene(directory, 'submission_failure')
            wait = sim.runtime['waiting_actions']['AC-failed']
            execution = sim.runtime['executions'][wait['execution_id']]
            self.assertEqual(wait['kind'], 'submission_failure')
            self.assertTrue(local_termination_confirmed(execution))
            self.assertEqual(execution['status'], 'ended')
            self.assertEqual(execution['outcome'], 'execution_incomplete')
            self.assertEqual(held_reservations(sim.runtime, [execution['id']]), [])
            self.assertIn('Git objects temporarily unavailable', wait['reason'])
            self.assertEqual(sim.engine.store.load()[2]['executions'][execution['id']], execution)


class FailedActionWaitContractTests(unittest.TestCase):
    def test_every_failure_has_a_real_producer_negative_condition_and_exact_owner_exit(self):
        exercised = set()
        for kind in FAILED_ACTION_WAITS:
            with self.subTest(kind=kind):
                sim = (failed_action_scene(self.enterContext(tempfile.TemporaryDirectory()), kind)
                       if kind == 'submission_failure' else failure_sim(kind))
                engine = sim.engine
                identifier, entry = next((key, row) for key, row in sim.runtime['waiting_actions'].items()
                                         if row['kind'] == kind)
                previous = deepcopy(entry)
                failed = deepcopy(sim.runtime['executions'][entry['execution_id']])
                self.assertEqual(failed['status'], 'ended')
                self.assertEqual(failed['outcome'], 'execution_incomplete')
                assert_wait_report(self, engine, identifier)
                held = deepcopy((sim.instance, sim.runtime))
                for _ in range(2):
                    engine._upkeep()
                    self.assertEqual((sim.instance, sim.runtime), held)
                clear_work(sim)
                model = scenario_model(sim)
                if kind == 'submission_failure':
                    engine._enqueue('operational_review', failed['id'], id='AC-diagnose-failure')
                    output = {key: value for key, value in empty_plan().items()
                              if key not in {'dispositions', 'preparation_requests', 'goal_audit', 'task_assessments'}}
                    output['disposition'] = {'kind': 'retry', 'basis_refs': [failed['id']],
                        'scope': 'The failed task-population judgment', 'replay_safety': 'No original bundle was applied',
                        'next_owner': 'research_plan', 'reason': 'Recompute from the current input without replaying the lost output'}
                    model.on('operational_review', id='AC-diagnose-failure').reply(explicit(output))
                else:
                    engine._enqueue('research_plan', id='AC-fresh-resolution')
                    model.on('research_plan', id='AC-fresh-resolution').reply(explicit(empty_plan(), extensions={
                        'action_resolutions': [{'action_id': identifier, 'evidence_execution_id': 'current',
                                               'reason': 'This accepted complete judgment resolves the exact prior scope'}]}))
                engine._save()
                sim.step()
                self.assertNotIn(identifier, sim.runtime.get('waiting_actions', {}))
                self.assertEqual(sim.runtime['executions'][failed['id']], failed)
                if kind == 'submission_failure':
                    continuations = [row for row in sim.runtime['queue'] if row.get('continuation_of') == failed['id']]
                    self.assertEqual(len(continuations), 1)
                    self.assertEqual(continuations[0]['id'], identifier)
                    disposition = next(row for row in sim.runtime['operational_dispositions'].values()
                                       if row['target_execution_id'] == failed['id'])
                    self.assertEqual(disposition['status'], 'applied')
                else:
                    resolutions = [row for row in sim.runtime['history']
                                   if row.get('kind') == 'failed_action_explicitly_resolved' and row['action_id'] == identifier]
                    self.assertEqual(len(resolutions), 1)
                    self.assertEqual(resolutions[0]['previous'], previous)
                released = deepcopy((sim.instance, sim.runtime))
                engine._upkeep()
                self.assertEqual((sim.instance, sim.runtime), released)
                self.assertNotIn(identifier, engine.store.load()[2].get('waiting_actions', {}))
                exercised.add(kind)
        self.assertEqual(exercised, FAILED_ACTION_WAITS)

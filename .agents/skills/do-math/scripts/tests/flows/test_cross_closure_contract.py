"""Actual question authority, merged closure and closed-initialization absorption."""
from copy import deepcopy
import unittest
from support.cross_contracts import ContractOracle
from support.cross_obligations import assert_preserved_reasons
from support.cross_research_machine import AssessmentAlphabetMachine, InitialDiagnosisAlphabetMachine, InvestigationAlphabetMachine
from support.cross_states import assert_event, queued, failure_ready
from support.sim import warm_template

setUpModule = warm_template

class OperationalQuestionTests(unittest.TestCase):
    def setUp(self):
        self.sim = failure_ready()
        self.action = deepcopy(queued(self.sim, 'operational_review'))
        self.assertIsNotNone(self.action)
        self.assertEqual(self.sim.runtime['executions'][self.action['target']]['status'], 'ended')

    def test_user_decision_is_accepted_and_preserves_the_question_authority(self):
        original = set(self.sim.runtime.get('operational_dispositions', {}))
        observed = assert_event(self.sim, self.action, 'operation', 'user_decision')
        self.assertEqual(observed['output']['disposition']['kind'], 'user_decision')
        published = deepcopy(self.sim.engine.store.load())
        head, instance, runtime = published
        added = {key: row for key, row in runtime['operational_dispositions'].items() if key not in original}
        self.assertEqual(len(added), 1)
        identifier, record = next(iter(added.items()))
        self.assertEqual(record['target_execution_id'], self.action['target'])
        question = next(row for row in runtime['question_links'] if row['id'] == record['question_id'])
        self.assertEqual((question['origin_execution_id'], question['origin_field'], question['owner']),
                         (record['execution_id'], 'output/disposition/question', 'user'))
        damaged = deepcopy(runtime)
        damaged['operational_dispositions'][identifier]['question_id'] = 'QU-missing'
        before = deepcopy(damaged)
        with self.assertRaisesRegex(ValueError, '^operational_dispositions references unknown record: QU-missing$'):
            self.sim.engine.store.save_with_state(head, instance, damaged)
        self.assertEqual(damaged, before)
        self.assertEqual(self.sim.engine.store.load(), published)
        self.sim.restart()
        ContractOracle(self.sim).check(self.sim)


class MergedClosureTests(unittest.TestCase):
    def setUp(self):
        from support.cross_obligations import preservation_requests
        self.machine = AssessmentAlphabetMachine()
        self.addCleanup(self.machine.teardown)
        self.machine.retire_knowledge(0)
        self.machine.contracts_after_every_event()
        self.before = deepcopy(preservation_requests(self.machine.sim.runtime))
        self.assertTrue(self.before)

    def test_close_preserves_merged_pending_request_reasons_in_history(self):
        queue = deepcopy(self.machine.sim.runtime['queue'])
        self.machine.close()
        assert_preserved_reasons(self.before, self.machine.sim.runtime)
        retired = [row for row in self.machine.sim.runtime['history'] if row.get('kind') == 'action_retired']
        self.assertEqual(retired, [{'kind': 'action_retired', 'reason': 'instance closed',
            'source_ref': self.machine.last_control['request_id'], 'action': action} for action in queue])
        self.machine.restart()
        self.machine.contracts_after_every_event()
        self.assertEqual([row for row in self.machine.sim.runtime['history'] if row.get('kind') == 'action_retired'], retired)
        self.assertEqual(self.machine.sim.runtime['status'], 'closed')


class InitialClosureTests(unittest.TestCase):
    def setUp(self):
        self.machine = InitialDiagnosisAlphabetMachine()
        self.addCleanup(self.machine.teardown)
        self.assertEqual(self.machine.sim.instance['lifecycle']['state'], 'initializing')
        self.assertIsNotNone(queued(self.machine.sim, 'maintenance'))

    def test_closed_initialization_absorbs_an_owner_pass_and_restart(self):
        self.machine.close()
        before = deepcopy((self.machine.sim.instance, self.machine.sim.runtime))
        calls = len(self.machine.sim.model.calls)
        self.machine.owner_pass()
        self.machine.restart()
        self.machine.contracts_after_every_event()
        self.assertEqual((self.machine.sim.instance, self.machine.sim.runtime), before)
        self.assertEqual(len(self.machine.sim.model.calls), calls)
        self.assertEqual(self.machine.sim.runtime['status'], 'closed')


class ReviewPremiseTests(unittest.TestCase):
    def setUp(self):
        self.machine = InvestigationAlphabetMachine()
        self.addCleanup(self.machine.teardown)
        self.assertIsNotNone(queued(self.machine.sim, 'supplemental_research'))
        self.assertTrue(any(c['status'] == 'working' for c in self.machine.sim.runtime['review_cycles'].values()))

    def test_goal_editions_preserve_independent_review_dispatch(self):
        from support.cross_obligations import actions
        independent = {a['id'] for a in actions(self.machine.sim.runtime) if a['role'] == 'identity_review'}
        self.assertTrue(independent)
        self.machine.change_charter()
        self.machine.change_charter()
        before = set(self.machine.sim.runtime['executions'])
        self.machine.owner_pass()
        self.machine.restart()
        self.machine.contracts_after_every_event()
        runtime = self.machine.sim.runtime
        preserved = {a['id'] for a in actions(runtime)} | {
            e['action']['id'] for e in runtime['executions'].values() if e.get('action')}
        self.assertLessEqual(independent, preserved)
        self.assertTrue(any(e['id'] not in before and e.get('action', {}).get('id') in independent
                            for e in runtime['executions'].values()))


class CheckpointProducerTests(unittest.TestCase):
    def test_empty_hold_reason_is_checked_as_an_explicit_expectation(self):
        from support.cross_research_machine import CheckpointAlphabetMachine
        machine = CheckpointAlphabetMachine()
        self.addCleanup(machine.teardown)
        before = deepcopy(machine.sim.runtime.get('user_pause'))
        result = machine.control('resume', config={'expected_user_pause_reason': ''}, idempotency_key='explicit-hold-replay')
        self.assertEqual(result['effect'], 'rejected')
        self.assertEqual(result['reason'], 'the effective user pause is not the released HOLD')
        self.assertEqual(machine.sim.runtime.get('user_pause'), before)
        machine.close()
        closed = deepcopy((machine.sim.instance, machine.sim.runtime))
        repeated = machine.control('resume', config={'expected_user_pause_reason': ''}, idempotency_key='explicit-hold-replay')
        self.assertEqual(repeated, result)
        self.assertEqual((machine.sim.instance, machine.sim.runtime), closed)
        fresh = machine.control('resume', config={'expected_user_pause_reason': ''})
        self.assertEqual(fresh['effect'], 'rejected')
        self.assertIn('closed/completed', fresh['reason'])
        self.assertEqual(machine.sim.runtime['status'], 'closed')

    def test_checkpoint_failure_reaches_ended_owned_diagnosis_input(self):
        from support.cross_states import checkpoint_failure
        sim = checkpoint_failure()
        review = queued(sim, 'operational_review')
        self.assertIsNotNone(review)
        target = sim.runtime['executions'][review['target']]
        self.assertEqual(target['status'], 'ended')
        checkpoint = sim.runtime['checkpoints'][target['id']]
        self.assertTrue(sim.engine.store.read(checkpoint['artifact_ref'], sim.engine.head))
        self.assertEqual(sim.engine.store.load()[2], sim.runtime)

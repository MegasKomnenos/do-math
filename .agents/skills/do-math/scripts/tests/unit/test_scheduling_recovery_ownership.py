"""Who owns a failed execution's recovery (``operational_dispositions``, ``activities``, ``repair_execution``; layer 2).

The runtimes are the smallest records these pure functions read: one ended
execution ``EX-old`` of activity ``AY-one`` and, when given, its continuation
``EX-new`` in the same activity.
"""
from copy import deepcopy
import unittest

import jsonschema

from do_math import activities, operational_dispositions, repair_execution
from do_math.record_schemas import RECORDS


def runtime(status='running', *, successor=True):
    target = {'id': 'EX-old', 'status': 'ended', 'owner_activity_id': 'AY-one',
              'action': {'id': 'AC-one', 'role': 'research_plan'}, 'error': 'returned'}
    state = {'executions': {'EX-old': target}, 'activities': {}, 'queue': [], 'operational_dispositions': {}}
    if successor:
        state['executions']['EX-new'] = {'id': 'EX-new', 'status': status, 'owner_activity_id': 'AY-one',
                                         'continuation_of': 'EX-old', 'action': {'id': 'AC-one', 'role': 'research_plan'}}
    return state


def record(kind='retry'):
    return {'id': 'OD-one', 'status': 'applied', 'target_execution_id': 'EX-old', 'disposition': {'kind': kind}}


class RecoveryOwnershipTests(unittest.TestCase):
    def test_live_and_ended_successors_supersede_old_retry_and_resume(self):
        for kind in ('retry', 'resume'):
            for status in ('starting', 'running', 'ended'):
                with self.subTest(kind=kind, status=status):
                    state = runtime(status)
                    row = record(kind)
                    self.assertTrue(operational_dispositions.reconcile_recovery(state, row))
                    self.assertEqual(row['status'], 'superseded')
                    self.assertEqual(state['queue'], [])
                    self.assertEqual(state['executions']['EX-old']['error'], 'returned')

    def test_unrelated_success_cannot_supersede_failure(self):
        state = runtime('ended')
        state['executions']['EX-new']['owner_activity_id'] = 'AY-other'
        self.assertIsNone(activities.successor_state(state, 'EX-old'))
        self.assertFalse(operational_dispositions.reconcile_recovery(state, record()))

    def test_queued_continuation_already_owns_recovery(self):
        state = runtime(successor=False)
        state['queue'] = [{'id': 'AC-one', 'continuation_of': 'EX-old', 'owner_activity_id': 'AY-one'}]
        before = deepcopy(state)
        self.assertTrue(operational_dispositions.reconcile_recovery(state, record()))
        self.assertEqual(state, before)

    def test_task_continuation_does_not_discharge_a_separate_installation_defect(self):
        state = runtime()
        state['executions']['EX-other'] = {'id': 'EX-other', 'status': 'ended', 'owner_activity_id': 'AY-other'}
        old = {**record('repair'), 'status': 'installation_repair_pending'}
        current = {**old, 'id': 'OD-other', 'target_execution_id': 'EX-other'}
        state['operational_dispositions'] = {old['id']: old, current['id']: current}
        self.assertEqual(repair_execution.pending_installation_repair(state), old)
        self.assertFalse(operational_dispositions.reconcile_recovery(state, old))

    def test_successful_installation_repair_preserves_the_existing_continuation(self):
        state = runtime()
        row = {**record('repair'), 'status': 'installation_repair_pending'}
        result = repair_execution.resume_installation_repair(state, row, repaired_by='EX-repair', at='2026-09-25T00:00:00Z')
        self.assertIsNone(result)
        self.assertEqual(state['queue'], [])
        self.assertEqual(row['status'], 'applied')
        self.assertEqual(row['result']['installation_repair']['successor']['live_execution_ids'], ['EX-new'])

    def test_already_applied_retry_keeps_its_receipt(self):
        row = {**record(), 'result': {'continuation_action_id': 'AC-one'}}
        self.assertFalse(operational_dispositions.reconcile_recovery(runtime(), row))
        self.assertEqual(row['status'], 'applied')


class InitialDiagnosisRecordTests(unittest.TestCase):
    def test_diagnosis_and_bound_rules_fit_the_persisted_contract(self):
        queue = jsonschema.Draft202012Validator(RECORDS['queue'])
        queue.validate({'id': 'AC-diagnose', 'role': 'maintenance', 'target': 'EX-bad', 'initial_submission_diagnosis': True})
        queue.validate({'id': 'AC-original', 'role': 'intent_interpretation', 'diagnosis_attempt': 1})
        self.assertIn('observation_rules', RECORDS['executions']['properties'])


if __name__ == '__main__':
    unittest.main()

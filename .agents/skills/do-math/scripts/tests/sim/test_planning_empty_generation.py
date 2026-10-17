"""실제 빈 준비 제출의 보류에서 신규 재개 요청을 만들 수 있는 조건을 확인한다."""
from copy import deepcopy
import unittest

from do_math import governance, revisions
from support.planning_contract_inputs import empty_hold_sim


class EmptyGenerationContinuationTests(unittest.TestCase):
    def setUp(self):
        self.sim = empty_hold_sim()
        self.hold = next(h for (lineage, _), h in revisions.active_repetition_holds(self.sim.runtime).items()
                         if lineage == 'exhaustion_empty')
        self.change = {'kind': 'repetition_continue', 'decision_id': 'DC-empty-continue',
            'lineage': 'exhaustion_empty', 'lineage_id': self.hold['lineage_id'],
            'hold_event_ref': self.hold['event_ref'], 'allowed_action': {'id': 'AC-empty-next',
                'role': 'research_preparation', 'repetition_bases': {'exhaustion_empty': self.hold['lineage_id']},
                'revision_targets': {}}}

    def test_actual_accepted_empty_result_can_create_one_new_request(self):
        self.assertEqual(self.sim.runtime['executions'][self.hold['event_ref']]['outcome'], 'output_accepted')
        source = next(s['id'] for s in self.sim.instance['governance_sources'].values() if s['origin'] == 'user')
        before = deepcopy((self.sim.instance, self.sim.runtime))
        instance, runtime, decision = governance.apply_decision(self.sim.instance, self.sim.runtime, self.change,
            source_ref=source, clock=self.sim.ports.clock)
        self.assertEqual(runtime['queue'], [{**self.change['allowed_action'],
            'reason': 'User continued the held empty preparation', 'receipt_refs': [self.hold['event_ref']]}])
        self.assertEqual(decision['affected'], [self.hold['event_ref'], 'AC-empty-next'])
        self.assertEqual((self.sim.instance, self.sim.runtime), before)
        self.sim.engine.instance, self.sim.engine.runtime = instance, runtime
        self.sim.engine._save()
        self.sim.restart()
        self.assertEqual(revisions.action_scope(self.sim.runtime['queue'][0]), self.change['allowed_action'])

    def test_failed_predecessor_cannot_use_the_empty_success_creation_rule(self):
        self.assertEqual(self.sim.runtime['executions'][self.hold['event_ref']]['outcome'], 'output_accepted')
        self.sim.runtime['executions'][self.hold['event_ref']]['outcome'] = 'execution_incomplete'
        before = deepcopy((self.sim.instance, self.sim.runtime))
        with self.assertRaisesRegex(ValueError, '^continuation scope differs from the current queued or waiting action$'):
            revisions.continue_repetition(self.sim.instance, self.sim.runtime, self.change,
                {'id': self.change['decision_id']}, clock=self.sim.ports.clock)
        self.assertEqual((self.sim.instance, self.sim.runtime), before)

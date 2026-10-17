"""사용자가 채택한 반복 한도와 정확한 재개 범위의 보존·거부를 확인한다."""
from copy import deepcopy
import re
import unittest

from do_math import revisions, task_contracts
from support.engine_lifecycle import applied, _ended_execution
from support.planning_contract_inputs import held_sim, warm_held, continuation_input, only_task

setUpModule = warm_held


class RepetitionContinuationTests(unittest.TestCase):
    def setUp(self):
        self.sim = held_sim()
        self.engine = self.sim.engine
        self.change = continuation_input(self.sim)
        self.action = next(a for a in self.sim.runtime['queue'] if a['id'] == self.change['allowed_action']['id'])

    def test_public_continuation_resets_exact_lineage_and_preserves_other_history(self):
        original = deepcopy(self.sim.runtime['history'])
        hold = revisions.repetition_hold(self.sim.runtime, 'contract_revision', self.change['lineage_id'])
        self.assertEqual(revisions.action_repetition_waits(self.sim.instance, self.sim.runtime, self.action), [hold])
        self.sim.advance(5)
        applied(self.sim, 'decision', config={'change': self.change})
        self.assertIsNone(revisions.repetition_hold(self.sim.runtime, 'contract_revision', self.change['lineage_id']))
        self.assertEqual(task_contracts.repetition_lineages(self.sim.runtime)['contract_revision']['count'], 0)
        self.assertEqual(self.sim.runtime['history'][:len(original)], original)
        receipt = next(r for r in self.sim.runtime['history'] if r.get('outcome') == 'continued')
        self.assertEqual(receipt['baseline_revision'], self.change['baseline_revision'])
        decision = self.sim.instance['decisions'][self.change['decision_id']]
        self.assertEqual(decision['affected'], [hold['event_ref'], self.action['id']])
        self.engine._save()
        expected = deepcopy(receipt)
        self.sim.restart()
        self.assertIn(expected, self.sim.runtime['history'])
        self.assertIsNone(revisions.repetition_hold(self.sim.runtime, 'contract_revision', self.change['lineage_id']))

    def test_rejects_stale_hold_without_releasing_hold(self):
        self.change['hold_event_ref'] = 'EX-stale'
        before = deepcopy((self.sim.instance, self.sim.runtime, self.change))
        head = self.engine.head
        with self.assertRaisesRegex(ValueError, '^' + re.escape('continuation must name the current repetition hold') + '$'):
            revisions.continue_repetition(self.sim.instance, self.sim.runtime, self.change,
                {'id': self.change['decision_id']}, clock=self.sim.ports.clock)
        self.assertEqual((self.sim.instance, self.sim.runtime, self.change), before)
        self.assertEqual(self.engine.head, head)

    def test_rejects_allowed_action_shape_without_releasing_hold(self):
        self.change['allowed_action'] = 'AC-string'
        before = deepcopy((self.sim.instance, self.sim.runtime, self.change))
        head = self.engine.head
        with self.assertRaisesRegex(ValueError, '^' + re.escape('allowed_action requires the exact action_scope object') + '$'):
            revisions.continue_repetition(self.sim.instance, self.sim.runtime, self.change,
                {'id': self.change['decision_id']}, clock=self.sim.ports.clock)
        self.assertEqual((self.sim.instance, self.sim.runtime, self.change), before)
        self.assertEqual(self.engine.head, head)

    def test_rejects_allowed_action_blank_without_releasing_hold(self):
        self.change['allowed_action']['id'] = ' '
        before = deepcopy((self.sim.instance, self.sim.runtime, self.change))
        head = self.engine.head
        with self.assertRaisesRegex(ValueError, '^' + re.escape('allowed_action requires the exact action_scope object') + '$'):
            revisions.continue_repetition(self.sim.instance, self.sim.runtime, self.change,
                {'id': self.change['decision_id']}, clock=self.sim.ports.clock)
        self.assertEqual((self.sim.instance, self.sim.runtime, self.change), before)
        self.assertEqual(self.engine.head, head)

    def test_rejects_missing_action_without_releasing_hold(self):
        self.change['allowed_action']['id'] = 'AC-missing'
        before = deepcopy((self.sim.instance, self.sim.runtime, self.change))
        head = self.engine.head
        with self.assertRaisesRegex(ValueError, '^' + re.escape('continuation scope differs from the current queued or waiting action') + '$'):
            revisions.continue_repetition(self.sim.instance, self.sim.runtime, self.change,
                {'id': self.change['decision_id']}, clock=self.sim.ports.clock)
        self.assertEqual((self.sim.instance, self.sim.runtime, self.change), before)
        self.assertEqual(self.engine.head, head)

    def test_rejects_changed_scope_without_releasing_hold(self):
        self.change['allowed_action']['role'] = 'research_plan'
        before = deepcopy((self.sim.instance, self.sim.runtime, self.change))
        head = self.engine.head
        with self.assertRaisesRegex(ValueError, '^' + re.escape('continuation scope differs from the current queued or waiting action') + '$'):
            revisions.continue_repetition(self.sim.instance, self.sim.runtime, self.change,
                {'id': self.change['decision_id']}, clock=self.sim.ports.clock)
        self.assertEqual((self.sim.instance, self.sim.runtime, self.change), before)
        self.assertEqual(self.engine.head, head)

    def test_rejects_outside_lineage_without_releasing_hold(self):
        self.action['revision_targets'] = {}
        self.change['allowed_action'] = revisions.action_scope(self.action)
        before = deepcopy((self.sim.instance, self.sim.runtime, self.change))
        head = self.engine.head
        with self.assertRaisesRegex(ValueError, '^' + re.escape('continued action is outside this held lineage') + '$'):
            revisions.continue_repetition(self.sim.instance, self.sim.runtime, self.change,
                {'id': self.change['decision_id']}, clock=self.sim.ports.clock)
        self.assertEqual((self.sim.instance, self.sim.runtime, self.change), before)
        self.assertEqual(self.engine.head, head)

    def test_rejects_live_attempt_without_releasing_hold(self):
        self.engine._register_execution(self.action, {'id': 'EX-live', 'role': 'research_preparation', 'status': 'running'})
        self.change['allowed_action'] = revisions.action_scope(self.action)
        before = deepcopy((self.sim.instance, self.sim.runtime, self.change))
        head = self.engine.head
        with self.assertRaisesRegex(ValueError, '^' + re.escape('continuation cannot overlap a live attempt') + '$'):
            revisions.continue_repetition(self.sim.instance, self.sim.runtime, self.change,
                {'id': self.change['decision_id']}, clock=self.sim.ports.clock)
        self.assertEqual((self.sim.instance, self.sim.runtime, self.change), before)
        self.assertEqual(self.engine.head, head)

    def test_hold_projection_is_detached_and_unrelated_roles_do_not_wait(self):
        key = ('contract_revision', self.change['lineage_id'])
        holds = revisions.active_repetition_holds(self.sim.runtime)
        expected = deepcopy(self.sim.runtime)
        self.assertEqual(holds[key], revisions.repetition_hold(self.sim.runtime, *key))
        holds[key]['reason'] = '호출자의 사본 변경'
        self.assertEqual(self.sim.runtime, expected)
        for role in ('maintenance', 'operational_review', 'intent_interpretation'):
            with self.subTest(role=role):
                self.assertEqual(revisions.action_repetition_waits(self.sim.instance, self.sim.runtime,
                    {'role': role, 'repetition_bases': {'contract_revision': self.change['lineage_id']}}), [])

    def test_existing_repetition_bases_are_not_rebound_by_explanatory_changes(self):
        before = deepcopy(self.action['repetition_bases'])
        self.action['reason'] = '표현만 변경'
        revisions.bind_repetition_bases(self.sim.instance, self.sim.runtime, self.action)
        self.assertEqual(self.action['repetition_bases'], before)

    def test_rejected_execution_requires_actual_matching_assignment(self):
        _ended_execution(self.engine, 'EX-wrong-role', 'research_plan')
        before = deepcopy((self.sim.instance, self.sim.runtime))
        with self.assertRaisesRegex(ValueError, '^repetition outcome requires the actual assigned execution$'):
            revisions.record_execution_outcome(self.sim.instance, self.sim.runtime, self.action, {},
                'EX-wrong-role', accepted=False, clock=self.sim.ports.clock)
        self.assertEqual((self.sim.instance, self.sim.runtime), before)

    def test_import_continuation_records_one_reauthor_receipt(self):
        prior = next(e for e in self.sim.runtime['executions'].values()
            if e['role'] == 'intent_interpretation' and e['action'].get('stage', 'interpret') == 'interpret')
        action = {'id': 'AC-reauthor', 'role': 'intent_interpretation',
                  'target': prior['action'].get('target'), 'continuation_of': prior['id']}
        revisions.bind_repetition_bases(self.sim.instance, self.sim.runtime, action)
        _ended_execution(self.engine, 'EX-reauthor', 'intent_interpretation')
        history = deepcopy(self.sim.runtime['history'])
        self.assertTrue(revisions.import_rework(self.sim.runtime, action))
        revisions.record_import_rework(self.sim.instance, self.sim.runtime, action, 'EX-reauthor', clock=self.sim.ports.clock)
        expected = {'kind': 'task_repetition', 'lineage': 'import_rework',
            'lineage_id': action['repetition_bases']['import_rework'], 'event_ref': 'EX-reauthor',
            'outcome': 'reauthored', 'owner': 'ai', 'reason': 'Registered interpretation reauthor attempt'}
        self.assertEqual(self.sim.runtime['history'], [*history, expected])
        revisions.record_import_rework(self.sim.instance, self.sim.runtime, action, 'EX-reauthor', clock=self.sim.ports.clock)
        self.assertEqual(self.sim.runtime['history'], [*history, expected])
        self.engine._save()

    def test_periodic_preparation_does_not_wait_on_empty_generation_hold(self):
        applied(self.sim, 'configure', config={'exhaustion_empty_limit': 1})
        task = only_task(self.sim)
        _ended_execution(self.engine, 'EX-empty', 'research_preparation')
        action = {'id': 'AC-empty', 'role': 'research_preparation'}
        revisions.bind_repetition_bases(self.sim.instance, self.sim.runtime, action)
        key = action['repetition_bases']['exhaustion_empty']
        revisions.record_repetition(self.sim.instance, self.sim.runtime, lineage='exhaustion_empty', lineage_id=key,
            event_ref='EX-empty', outcome='empty', owner='ai', reason='생성 결과 없음', clock=self.sim.ports.clock)
        hold = revisions.repetition_hold(self.sim.runtime, 'exhaustion_empty', key)
        self.assertEqual(revisions.action_repetition_waits(self.sim.instance, self.sim.runtime, action), [hold])
        action['periodic_reconsideration'] = True
        self.assertEqual(revisions.action_repetition_waits(self.sim.instance, self.sim.runtime, action), [])
        self.assertIsNotNone(revisions.repetition_hold(self.sim.runtime, 'contract_revision', task['id']))

    def continuation_receipt_inputs(self):
        from do_math import governance
        source_ref = next(row['id'] for row in self.sim.instance['governance_sources'].values() if row['origin'] == 'user')
        instance, _, decision = governance.apply_decision(self.sim.instance, self.sim.runtime, self.change,
            source_ref=source_ref, clock=self.sim.ports.clock)
        return instance, decision, {'lineage': 'contract_revision', 'lineage_id': self.change['lineage_id'],
            'event_ref': self.change['decision_id'], 'outcome': 'continued', 'owner': 'user',
            'reason': 'User authorized the scoped continuation', 'decision_ref': self.change['decision_id']}

    def test_zero_continuation_baseline_does_not_release_history(self):
        instance, decision, fields = self.continuation_receipt_inputs()
        instance['decisions'][decision['id']]['change']['baseline_revision'] = 0
        before = deepcopy((instance, self.sim.runtime))
        with self.assertRaisesRegex(ValueError, '^version continuation needs its current baseline revision$'):
            revisions.record_repetition(instance, self.sim.runtime, **fields, clock=self.sim.ports.clock)
        self.assertEqual((instance, self.sim.runtime), before)

    def test_future_continuation_baseline_does_not_release_history(self):
        instance, decision, fields = self.continuation_receipt_inputs()
        instance['decisions'][decision['id']]['change']['baseline_revision'] += 1
        before = deepcopy((instance, self.sim.runtime))
        with self.assertRaisesRegex(ValueError, '^continuation cannot invent a future version baseline$'):
            revisions.record_repetition(instance, self.sim.runtime, **fields, clock=self.sim.ports.clock)
        self.assertEqual((instance, self.sim.runtime), before)

    def test_rejected_malformed_regeneration_time_never_records_empty_success(self):
        _ended_execution(self.engine, 'EX-invalid-empty', 'research_preparation')
        self.sim.runtime['executions']['EX-invalid-empty']['observed_at'] = self.sim.ports.clock.now()
        action = {'id': 'AC-invalid-empty', 'role': 'research_preparation'}
        revisions.bind_repetition_bases(self.sim.instance, self.sim.runtime, action)
        before = deepcopy((self.sim.instance, self.sim.runtime))
        for value in ('not-a-time', '2000-01-01T00:00:00Z'):
            with self.subTest(value=value):
                self.assertIsNone(revisions.record_execution_outcome(self.sim.instance, self.sim.runtime,
                    action, {'summary': '잘못된 시각으로 반려된 출력', 'regenerate_after': value},
                    'EX-invalid-empty', accepted=False, clock=self.sim.ports.clock))
                self.assertEqual((self.sim.instance, self.sim.runtime), before)

    def test_continuation_after_separate_question_answer_does_not_resolve_twice(self):
        from do_math.questions import open_links
        hold = revisions.repetition_hold(self.sim.runtime, 'contract_revision', self.change['lineage_id'])
        question = next(q for q in open_links(self.sim.runtime, 'user')
                        if q.get('origin_execution_id') == hold['event_ref'])
        applied(self.sim, 'decision', config={'change': {'kind': 'question_answer',
            'text': '재개 범위는 다음 별도 결정으로 지정한다.', 'target_ids': [hold['event_ref']],
            'resolves_questions': [question['id']]}})
        closed = deepcopy(next(q for q in self.sim.runtime['question_links'] if q['id'] == question['id']))
        self.assertIsNotNone(revisions.repetition_hold(self.sim.runtime, 'contract_revision', self.change['lineage_id']))
        applied(self.sim, 'decision', config={'change': self.change})
        self.assertIsNone(revisions.repetition_hold(self.sim.runtime, 'contract_revision', self.change['lineage_id']))
        self.assertEqual(next(q for q in self.sim.runtime['question_links'] if q['id'] == question['id']), closed)

    def test_waiting_owner_becomes_ready_on_its_exact_continuation(self):
        from do_math import governance
        self.sim.step()
        self.assertEqual(self.sim.runtime['status'], 'waiting')
        self.action = next(a for a in self.sim.runtime['queue'] if a['id'] == self.change['allowed_action']['id'])
        self.change['allowed_action'] = revisions.action_scope(self.action)
        source_ref = next(row['id'] for row in self.sim.instance['governance_sources'].values() if row['origin'] == 'user')
        self.assertNotIn('waiting_actions', self.sim.runtime)
        instance, runtime, decision = governance.apply_decision(self.sim.instance, self.sim.runtime, self.change,
            source_ref=source_ref, clock=self.sim.ports.clock)
        self.assertEqual(runtime['status'], 'ready')
        self.assertIsNone(revisions.repetition_hold(runtime, 'contract_revision', self.change['lineage_id']))
        continued = next(row for row in runtime['queue'] if row['id'] == self.action['id'])
        self.assertEqual(revisions.action_scope(continued), self.change['allowed_action'])
        self.assertEqual(decision['affected'], [self.change['hold_event_ref'], self.action['id']])
        self.engine.instance, self.engine.runtime = instance, runtime
        self.engine._save()

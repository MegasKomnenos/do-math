"""실제 엔진이 만든 개정 대기·선택·후속 처분의 값과 저장 효과를 확인한다."""
from copy import deepcopy
import unittest
from support.known_defects import known_defect

from do_math import planning, revisions
from support.engine_lifecycle import _ended_execution, clear_work
from support.planning_owner import enqueue
from support.planning_contract_inputs import (prepared_sim, warm_prepared, only_task,
    produce_task, defer_revision, withdraw, select)

setUpModule = warm_prepared


class RevisionTransitionTests(unittest.TestCase):
    def setUp(self):
        self.sim = prepared_sim()
        self.engine = self.sim.engine
        self.identifier = only_task(self.sim)['id']

    def save_and_reload(self):
        self.engine._save()
        expected = deepcopy((self.sim.instance, self.sim.runtime))
        self.sim.restart()
        self.assertEqual((self.sim.instance, self.sim.runtime), expected)

    def test_closed_pure_revision_wait_is_retired_with_exact_history(self):
        parent = defer_revision(self.sim, [self.identifier])
        withdraw(self.sim, self.identifier)
        previous = deepcopy(self.sim.runtime['waiting_actions'][parent]['action']['revision_targets'])
        history = deepcopy(self.sim.runtime['history'])
        self.engine._retire_closed_revision_targets()
        self.assertEqual(self.sim.runtime['waiting_actions'], {})
        self.assertEqual(self.sim.runtime['history'], [*history, {
            'kind': 'revision_targets_retired_after_disposition', 'action_id': parent,
            'targets': [self.identifier], 'previous_targets': previous}])
        self.save_and_reload()

    def test_invalidated_selection_wait_is_saved_until_exact_independent_review(self):
        from support.role_answers import review_items
        from support.wait_reporting import assert_task_wait_report
        selected = deepcopy(select(self.sim))
        enqueue(self.engine, 'research_preparation', self.identifier)
        produce_task(self.sim, '새 계약', revises=self.identifier)
        clear_work(self.sim)
        self.assertFalse(self.engine._selected_action_current(selected,
            evaluation_context=self.engine._evaluation_context()))
        wait = deepcopy(self.sim.runtime['tasks'][self.identifier]['waiting'])
        self.assertEqual((wait['kind'], wait['basis_ref']), ('contract_review', selected['id']))
        self.save_and_reload()
        self.engine = self.sim.engine
        assert_task_wait_report(self, self.engine, self.identifier)
        before = deepcopy(self.sim.runtime['tasks'][self.identifier])
        self.engine._refresh_readiness()
        self.assertEqual(self.sim.runtime['tasks'][self.identifier], before)
        other = produce_task(self.sim, '무관 검토')
        self.assertEqual(self.sim.runtime['tasks'][self.identifier], before)
        _ended_execution(self.engine, 'EX-exact-review', 'task_contract_review')
        self.engine._apply({'role': 'task_contract_review', 'target': self.identifier},
            review_items([self.identifier]), 'EX-exact-review', owns_response=False)
        current = self.sim.runtime['tasks'][self.identifier]
        self.assertNotIn('waiting', current)
        self.assertEqual(current['status'], 'planned')
        self.assertEqual(current['revision'], before['revision'])
        self.engine._save()
        self.assertNotIn(wait, next(row for row in self.engine.status()['tasks'] if row['id'] == self.identifier)['waits'])
        self.assertEqual(self.sim.runtime['tasks'][other]['status'], 'planned')

    def test_actual_revision_owner_settles_after_exact_child_resolution_once(self):
        from do_math.execution_lifecycle import transition_execution
        from support.wait_reporting import assert_wait_report, assert_status_report
        def defer(identifier, suffix):
            action = enqueue(self.engine, 'research_preparation', revision_targets=revisions.capture_targets(
                self.sim.instance, self.sim.runtime, [identifier]))
            eid = 'EX-deferred-' + suffix
            execution = self.engine._register_execution(action, {'id': eid,
                'role': 'research_preparation', 'status': 'running'})
            transition_execution(execution, 'stopping', at=self.sim.clock.now())
            transition_execution(execution, 'ended', at=self.sim.clock.now(), outcome='execution_incomplete')
            execution['extensions'] = {'revision_resolutions': [{'record_id': identifier,
                'disposition': 'deferred', 'reason': '추가 자료를 기다린다.'}]}
            self.assertEqual(revisions.submission_errors({'candidates': []}, execution['extensions'],
                {'action': action, 'tasks': list(self.sim.runtime['tasks'].values())}), [])
            self.engine._apply_revision_followup(action, {'summary': '개정 보류'}, eid)
            self.engine._remove_action(action)
            self.engine._settle_activity(eid)
            return action['id'], action['owner_activity_id']
        parent, owner = defer(self.identifier, 'main')
        other_id = produce_task(self.sim, '다른 개정 의무')
        clear_work(self.sim)
        other_parent, other_owner = defer(other_id, 'other')
        self.engine._save()
        self.sim.restart()
        self.engine = self.sim.engine
        assert_wait_report(self, self.engine, parent)
        before = deepcopy((self.sim.runtime['waiting_actions'][parent], self.sim.runtime['activities'][owner]))
        self.engine._retire_closed_revision_targets()
        self.assertEqual((self.sim.runtime['waiting_actions'][parent], self.sim.runtime['activities'][owner]), before)
        other = deepcopy((self.sim.runtime['waiting_actions'][other_parent], self.sim.runtime['activities'][other_owner]))
        child = enqueue(self.engine, 'research_preparation', revision_targets=revisions.capture_targets(
            self.sim.instance, self.sim.runtime, [self.identifier]))
        _ended_execution(self.engine, 'EX-exact-child', 'research_preparation')
        self.sim.runtime['executions']['EX-exact-child']['extensions'] = {'revision_resolutions': [{
            'record_id': self.identifier, 'disposition': 'unchanged', 'reason': '현재 계약을 유지한다.'}]}
        self.engine._apply_revision_followup(child, {'summary': '개정 판단 수락'}, 'EX-exact-child')
        self.assertNotIn(parent, self.sim.runtime['waiting_actions'])
        self.assertEqual(self.sim.runtime['activities'][owner]['status'], 'finished')
        self.assertNotIn('waiting', self.sim.runtime['activities'][owner])
        self.assertEqual((self.sim.runtime['waiting_actions'][other_parent], self.sim.runtime['activities'][other_owner]), other)
        history = deepcopy(self.sim.runtime['history'])
        activity = deepcopy(self.sim.runtime['activities'][owner])
        self.engine._apply_revision_followup(child, {'summary': '개정 판단 수락'}, 'EX-exact-child')
        self.assertEqual(self.sim.runtime['history'], history)
        self.assertEqual(self.sim.runtime['activities'][owner], activity)
        self.engine._remove_action(child)
        self.engine._save()
        report, _ = assert_status_report(self, self.engine)
        self.assertNotIn(owner, report['waiting_activities'])
        self.assertIn(other_owner, report['waiting_activities'])
        withdraw(self.sim, other_id)
        self.engine._retire_closed_revision_targets()
        self.assertNotIn(other_parent, self.sim.runtime['waiting_actions'])
        self.assertEqual(self.sim.runtime['activities'][other_owner]['status'], 'finished')
        after = deepcopy(self.sim.runtime)
        self.engine._retire_closed_revision_targets()
        self.assertEqual(self.sim.runtime, after)
        self.engine._save()
        self.sim.restart()
        self.assertNotIn(other_owner, self.sim.engine.status()['waiting_activities'])

    def test_closed_target_leaves_other_revision_obligations_in_wait(self):
        other = produce_task(self.sim, '다른 과제')
        clear_work(self.sim)
        parent = defer_revision(self.sim, [self.identifier, other])
        withdraw(self.sim, self.identifier)
        before = deepcopy(self.sim.runtime['waiting_actions'][parent])
        self.engine._retire_closed_revision_targets()
        expected = deepcopy(before)
        del expected['action']['revision_targets'][self.identifier]
        self.assertEqual(self.sim.runtime['waiting_actions'], {parent: expected})
        self.save_and_reload()

    def test_rebinding_parent_obligation_is_idempotent_and_preserves_required(self):
        parent = defer_revision(self.sim, [self.identifier], required=True)
        action = enqueue(self.engine, 'research_preparation', revision_targets=revisions.capture_targets(
            self.sim.instance, self.sim.runtime, [self.identifier]))
        expected = deepcopy(action)
        self.assertEqual(action['revision_parent_ids'], [parent])
        self.assertIs(action['revision_targets'][self.identifier]['required'], True)
        self.assertEqual(action['revision_targets'][self.identifier]['obligation_refs'], [{
            'action_id': parent, 'reason': '추가 근거를 기다린다.'}])
        self.engine._bind_revision_action(action)
        self.assertEqual(action, expected)
        self.save_and_reload()


    def test_optional_unchanged_child_resolves_parent_exactly_once(self):
        parent = defer_revision(self.sim, [self.identifier])
        child = enqueue(self.engine, 'research_preparation', revision_targets=revisions.capture_targets(
            self.sim.instance, self.sim.runtime, [self.identifier]))
        _ended_execution(self.engine, 'EX-child', 'research_preparation')
        self.sim.runtime['executions']['EX-child']['extensions'] = {'revision_resolutions': [{
            'record_id': self.identifier, 'disposition': 'unchanged', 'reason': '계약 유지'}]}
        previous = deepcopy(self.sim.runtime['waiting_actions'][parent])
        history = deepcopy(self.sim.runtime['history'])
        self.engine._apply_revision_followup(child, {'summary': '유지'}, 'EX-child')
        self.assertEqual(self.sim.runtime['waiting_actions'], {})
        self.assertEqual(self.sim.runtime['history'], [*history, {
            'kind': 'revision_obligation_resolved', 'action_id': parent, 'execution_id': 'EX-child',
            'to_action_id': None, 'previous': previous}])
        after = deepcopy(self.sim.runtime['history'])
        self.engine._apply_revision_followup(child, {'summary': '유지'}, 'EX-child')
        self.assertEqual(self.sim.runtime['history'], after)
        self.engine._remove_action(child)
        self.save_and_reload()

    def test_partial_resolution_preserves_remaining_target_and_detached_basis(self):
        other = produce_task(self.sim, '다른 과제')
        clear_work(self.sim)
        parent = defer_revision(self.sim, [self.identifier, other])
        child = enqueue(self.engine, 'research_preparation', revision_targets=revisions.capture_targets(
            self.sim.instance, self.sim.runtime, [self.identifier]))
        _ended_execution(self.engine, 'EX-child', 'research_preparation')
        self.sim.runtime['executions']['EX-child']['extensions'] = {'revision_resolutions': [{
            'record_id': self.identifier, 'disposition': 'unchanged', 'reason': '계약 유지'}]}
        previous = deepcopy(self.sim.runtime['waiting_actions'][parent])
        self.engine._apply_revision_followup(child, {}, 'EX-child')
        expected = deepcopy(previous)
        del expected['action']['revision_targets'][self.identifier]
        self.assertEqual(self.sim.runtime['waiting_actions'], {parent: expected})
        child['revision_targets'].clear()
        self.assertEqual(self.sim.runtime['waiting_actions'], {parent: expected})
        self.engine._remove_action(child)
        self.save_and_reload()

    def test_same_action_resolution_removes_its_previous_revision_wait(self):
        parent = defer_revision(self.sim, [self.identifier])
        previous = deepcopy(self.sim.runtime['waiting_actions'][parent])
        action = deepcopy(previous['action'])
        _ended_execution(self.engine, 'EX-resolve', 'research_preparation')
        self.sim.runtime['executions']['EX-resolve']['extensions'] = {'revision_resolutions': [{
            'record_id': self.identifier, 'disposition': 'unchanged', 'reason': '후속 확인 완료'}]}
        history = deepcopy(self.sim.runtime['history'])
        self.engine._apply_revision_followup(action, {}, 'EX-resolve')
        self.assertEqual(self.sim.runtime['waiting_actions'], {})
        self.assertEqual(self.sim.runtime['history'], [*history, {
            'kind': 'revision_obligation_resolved', 'action_id': parent,
            'execution_id': 'EX-resolve', 'previous': previous}])
        self.save_and_reload()

    def test_missing_selected_target_defers_to_structural_owner_without_mutation(self):
        action = select(self.sim)
        del self.sim.runtime['tasks'][self.identifier]
        before = deepcopy(self.sim.runtime)
        self.assertTrue(self.engine._selected_action_current(action, evaluation_context=self.engine._evaluation_context()))
        self.assertEqual(self.sim.runtime, before)

    def test_nonresearch_action_is_current_without_changing_state(self):
        action = enqueue(self.engine, 'research_plan')
        before = deepcopy(self.sim.runtime)
        self.assertTrue(self.engine._selected_action_current(action, evaluation_context=self.engine._evaluation_context()))
        self.assertEqual(self.sim.runtime, before)

    def test_selected_external_wait_preserves_selection_for_its_owner(self):
        action = select(self.sim)
        task = self.sim.runtime['tasks'][self.identifier]
        task['waiting'] = {'kind': 'external_event', 'target_refs': ['source:later'], 'next_owner': 'user'}
        self.engine._save()
        action = next(a for a in self.sim.runtime['queue'] if a['id'] == action['id'])
        before = deepcopy(self.sim.runtime)
        self.assertFalse(self.engine._selected_action_current(action, evaluation_context=self.engine._evaluation_context()))
        self.assertEqual(self.sim.runtime, before)

    def test_contract_revision_cancels_unstarted_selection_and_records_owner(self):
        selected = select(self.sim)
        previous = deepcopy(selected)
        history = deepcopy(self.sim.runtime['history'])
        revision = enqueue(self.engine, 'research_preparation', self.identifier)
        task = self.sim.runtime['tasks'][self.identifier]
        self.assertEqual(self.sim.runtime['queue'], [revision])
        self.assertEqual(task['status'], 'waiting')
        self.assertEqual(task['waiting'], {'kind': 'contract_revision', 'target_refs': [self.identifier],
            'next_owner': 'research_preparation', 'basis_ref': revision['id'], 'reason': 'contract revision requested'})
        self.assertEqual(task['revision_requested'], {'revision': task['revision'], 'source': revision['id'],
                                                    'reason': 'contract revision requested'})
        self.assertNotIn('selected_by', task)
        self.assertEqual(self.sim.runtime['history'], [*history, {'kind': 'selection_cancelled_for_revision',
            'action': previous, 'revision_action_id': revision['id']}])
        self.save_and_reload()
        self.engine = self.sim.engine
        from support.wait_reporting import assert_task_wait_report
        assert_task_wait_report(self, self.engine, self.identifier)
        before = deepcopy(self.sim.runtime['tasks'][self.identifier])
        enqueue(self.engine, 'research_preparation', self.identifier)
        self.assertEqual(self.sim.runtime['tasks'][self.identifier], before)
        produce_task(self.sim, '개정된 계약', revises=self.identifier)
        current = self.sim.runtime['tasks'][self.identifier]
        self.assertEqual(current['revision'], before['revision'] + 1)
        self.assertNotIn('waiting', current)
        self.assertNotIn('revision_requested', current)
        self.assertEqual(current['revision_history'][-1]['waiting'], before['waiting'])
        self.assertEqual(current['reviews'][-1]['decision'], 'approved')

    def test_preparation_only_cancels_selection_without_requesting_contract_revision(self):
        from do_math.model_policy import assessment_basis
        selected = select(self.sim)
        previous = deepcopy(selected)
        task = self.sim.runtime['tasks'][self.identifier]
        history = deepcopy(self.sim.runtime['history'])
        action = enqueue(self.engine, 'research_preparation', assessment_targets={self.identifier: assessment_basis(task)})
        self.assertEqual(self.sim.runtime['queue'], [action])
        self.assertEqual(task['status'], 'planned')
        self.assertNotIn('revision_requested', task)
        self.assertNotIn('selected_by', task)
        self.assertEqual(self.sim.runtime['history'], [*history, {'kind': 'selection_cancelled_for_revision',
            'action': previous, 'revision_action_id': action['id']}])
        self.save_and_reload()

    def test_revision_cannot_cancel_a_live_selected_execution(self):
        selected = select(self.sim)
        self.engine._register_execution(selected, {'id': 'EX-live', 'role': 'research_work', 'status': 'running'})
        revision = enqueue(self.engine, 'research_preparation', self.identifier)
        self.engine._save()
        before = deepcopy(self.sim.runtime)
        self.engine._cancel_selected_revision_targets(revision)
        self.assertEqual(self.sim.runtime, before)

    def test_revised_task_refreshes_declared_basis_and_preserves_required(self):
        parent = defer_revision(self.sim, [self.identifier], required=True)
        old = deepcopy(self.sim.runtime['waiting_actions'][parent]['action']['revision_targets'])
        produce_task(self.sim, revises=self.identifier)
        clear_work(self.sim)
        action = self.sim.runtime['waiting_actions'][parent]['action']
        waits = self.engine._revision_dispatch_waits(action)
        expected = revisions.capture_targets(self.sim.instance, self.sim.runtime, [self.identifier], required=True)
        self.assertEqual(action['revision_targets'], expected)
        self.assertEqual(action['superseded_revision_bases'], [old])
        self.assertEqual(waits, [])
        self.save_and_reload()

    def test_missing_revision_target_retains_its_original_basis(self):
        parent = defer_revision(self.sim, [self.identifier])
        action = self.sim.runtime['waiting_actions'][parent]['action']
        old = deepcopy(action['revision_targets'])
        del self.sim.runtime['tasks'][self.identifier]
        with self.assertRaisesRegex(ValueError, '^missing proposal revision ancestor$'):
            self.engine._revision_dispatch_waits(action)
        self.assertEqual(action['revision_targets'], old)
        self.assertEqual(action['superseded_revision_bases'], [old])

    def test_followup_request_enqueues_captured_targets_without_an_original_declaration(self):
        before = deepcopy(self.sim.runtime['tasks'][self.identifier])
        _ended_execution(self.engine, 'EX-request', 'research_plan')
        self.sim.runtime['executions']['EX-request']['extensions'] = {'revision_requests': [{
            'record_ids': [self.identifier], 'reason': '계약을 다시 살핀다.'}]}
        self.engine._apply_revision_followup({'id': 'AC-request', 'role': 'research_plan'}, {}, 'EX-request')
        action, = self.sim.runtime['queue']
        self.assertEqual(action['role'], 'research_preparation')
        self.assertEqual(action['requested_by'], 'EX-request')
        self.assertEqual(self.sim.runtime['tasks'][self.identifier], before)
        self.assertEqual(action['revision_targets'], revisions.capture_targets(
            self.sim.instance, self.sim.runtime, [self.identifier], source_ref='EX-request'))
        self.save_and_reload()

    def test_record_task_receipt_forwards_value_and_records_actual_execution(self):
        _ended_execution(self.engine, 'EX-receipt', 'research_plan')
        action = enqueue(self.engine, 'research_plan')
        instance, runtime = deepcopy((self.sim.instance, self.sim.runtime))
        expected = revisions.record_execution_outcome(instance, runtime, deepcopy(action), {'summary': '계획 수락'},
            'EX-receipt', accepted=True, clock=self.sim.ports.clock)
        result = self.engine._record_task_receipt(action, {'summary': '계획 수락'}, 'EX-receipt', accepted=True)
        self.assertEqual(result, expected)
        self.assertEqual((self.sim.instance, self.sim.runtime), (instance, runtime))
        receipt = self.sim.runtime['history'][-1]
        self.assertEqual((receipt['kind'], receipt['outcome'], receipt['event_ref']),
                         ('task_repetition', 'accepted', 'EX-receipt'))
        self.save_and_reload()

    def test_terminal_selected_action_does_not_reopen_its_task(self):
        selected = deepcopy(select(self.sim))
        withdraw(self.sim, self.identifier)
        task = deepcopy(self.sim.runtime['tasks'][self.identifier])
        self.assertFalse(self.engine._selected_action_current(selected, evaluation_context=self.engine._evaluation_context()))
        self.assertEqual(self.sim.runtime['tasks'][self.identifier], task)
        self.assertEqual([a['role'] for a in self.sim.runtime['queue']], ['research_plan'])
        self.assertEqual(self.sim.runtime['history'][-1]['kind'], 'obsolete_selection')
        self.assertEqual(self.sim.runtime['history'][-1]['action'], selected)
        self.save_and_reload()

    def test_closed_task_does_not_gain_an_implicit_revision_target(self):
        withdraw(self.sim, self.identifier)
        action = {'id': 'AC-closed', 'role': 'research_preparation', 'target': self.identifier}
        self.engine._bind_revision_action(action)
        self.assertEqual(action['revision_targets'], {})
        self.assertEqual(self.sim.runtime['tasks'][self.identifier]['status'], 'closed')

    def test_revision_of_active_task_without_queued_selection_still_sets_wait_owner(self):
        selected = select(self.sim)
        self.engine._remove_action(selected)
        history = deepcopy(self.sim.runtime['history'])
        action = enqueue(self.engine, 'research_preparation', self.identifier)
        task = self.sim.runtime['tasks'][self.identifier]
        self.assertEqual(task['waiting'], {'kind': 'contract_revision', 'target_refs': [self.identifier],
            'next_owner': 'research_preparation', 'basis_ref': action['id'], 'reason': 'contract revision requested'})
        self.assertEqual(task['status'], 'waiting')
        self.assertEqual(self.sim.runtime['history'], history)
        self.save_and_reload()

    def test_withdrawal_extension_resolves_parent_without_a_revision_resolution_row(self):
        parent = defer_revision(self.sim, [self.identifier])
        child = enqueue(self.engine, 'research_preparation', revision_targets=revisions.capture_targets(
            self.sim.instance, self.sim.runtime, [self.identifier]))
        _ended_execution(self.engine, 'EX-withdraw-child', 'research_preparation')
        self.sim.runtime['executions']['EX-withdraw-child']['extensions'] = {'task_dispositions': [{
            'task_id': self.identifier, 'disposition': 'withdraw', 'reason': '미수행 의무 철회'}]}
        withdraw(self.sim, self.identifier)
        previous = deepcopy(self.sim.runtime['waiting_actions'][parent])
        history = deepcopy(self.sim.runtime['history'])
        self.engine._apply_revision_followup(child, {}, 'EX-withdraw-child')
        self.assertEqual(self.sim.runtime['waiting_actions'], {})
        self.assertEqual(self.sim.runtime['history'], [*history, {
            'kind': 'revision_obligation_resolved', 'action_id': parent, 'execution_id': 'EX-withdraw-child',
            'to_action_id': None, 'previous': previous}])
        self.engine._remove_action(child)
        self.save_and_reload()

    def test_extra_child_target_does_not_change_parent_scope(self):
        other = produce_task(self.sim, '추가 개정 과제')
        clear_work(self.sim)
        parent = defer_revision(self.sim, [self.identifier])
        child = enqueue(self.engine, 'research_preparation', revision_targets=revisions.capture_targets(
            self.sim.instance, self.sim.runtime, [self.identifier, other]))
        _ended_execution(self.engine, 'EX-extra-child', 'research_preparation')
        self.sim.runtime['executions']['EX-extra-child']['extensions'] = {'revision_resolutions': [
            {'record_id': identifier, 'disposition': 'unchanged', 'reason': '각 계약 유지'}
            for identifier in (self.identifier, other)]}
        self.engine._apply_revision_followup(child, {}, 'EX-extra-child')
        self.assertEqual(self.sim.runtime['waiting_actions'], {})
        self.assertEqual(self.sim.runtime['history'][-1]['action_id'], parent)
        self.assertEqual(self.sim.runtime['history'][-1]['kind'], 'revision_obligation_resolved')
        history = deepcopy(self.sim.runtime['history'])
        self.engine._apply_revision_followup(child, {}, 'EX-extra-child')
        self.assertEqual(self.sim.runtime['history'], history)
        self.engine._remove_action(child)
        self.save_and_reload()

    def test_completion_retires_queued_review_and_targeted_revision(self):
        from do_math.task_scope import apply_task_assessments
        from support.planning_contract_inputs import returned
        assessment = returned(self.sim)
        review = enqueue(self.engine, 'task_contract_review', self.identifier)
        revision = enqueue(self.engine, 'research_preparation', self.identifier)
        self.engine.instance, self.engine.runtime = apply_task_assessments(
            self.sim.instance, self.sim.runtime, [assessment], execution_id='EX-planning-plan',
            input_tasks=deepcopy(self.sim.runtime['tasks']), clock=self.sim.ports.clock)
        current_revision = next(a for a in self.sim.runtime['queue'] if a['id'] == revision['id'])
        previous_targets = deepcopy(current_revision['revision_targets'])
        history = deepcopy(self.sim.runtime['history'])
        expected_queue = [deepcopy(a) for a in self.sim.runtime['queue'] if a['id'] not in {review['id'], revision['id']}]
        self.engine._retire_closed_revision_targets()
        self.assertEqual(self.sim.runtime['queue'], expected_queue)
        self.assertNotIn('target', current_revision)
        self.assertEqual(self.sim.runtime['history'], [*history,
            {'kind': 'action_retired_after_target_disposition', 'action': review, 'previous': None},
            {'kind': 'revision_targets_retired_after_disposition', 'action_id': revision['id'],
             'targets': [self.identifier], 'previous_targets': previous_targets}])
        self.save_and_reload()

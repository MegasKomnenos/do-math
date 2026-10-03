"""개정 선언·수신 검사와 반복 영수증의 입력 경계 및 부작용을 확인한다."""
from copy import deepcopy
import re
import unittest

from do_math import revisions, task_contracts, planning
from support.fakes.clock import FakeClock
from support.planning_contract_inputs import contract
from support.role_answers import candidate


class RevisionSubmissionTests(unittest.TestCase):
    def setUp(self):
        self.task = contract()
        self.context = {'action': {'role': 'research_preparation',
            'revision_targets': revisions.capture_targets({}, {'tasks': {self.task['id']: self.task}}, [self.task['id']])},
            'tasks': [self.task], 'knowledge_catalog': [], 'task_catalog': []}
        self.output = {'candidates': []}
        self.extensions = {'revision_resolutions': [{'record_id': self.task['id'],
            'disposition': 'unchanged', 'reason': '원래 계약 유지'}]}

    def test_duplicate_request_has_exact_issue_and_no_mutation(self):
        self.assertEqual(revisions.submission_errors(self.output, self.extensions, self.context), [])
        self.extensions['revision_requests'] = [{'record_ids': [self.task['id'], self.task['id']], 'reason': '반복 요청'}]
        before = deepcopy((self.output, self.extensions, self.context))
        self.assertEqual(revisions.submission_errors(self.output, self.extensions, self.context), [{'path': 'activity-extensions.json/revision_requests', 'message': 'revision requests must name distinct provided tasks or knowledge'}])
        self.assertEqual((self.output, self.extensions, self.context), before)

    def test_unknown_request_has_exact_issue_and_no_mutation(self):
        self.assertEqual(revisions.submission_errors(self.output, self.extensions, self.context), [])
        self.extensions['revision_requests'] = [{'record_ids': ['TK-absent'], 'reason': '없는 대상'}]
        before = deepcopy((self.output, self.extensions, self.context))
        self.assertEqual(revisions.submission_errors(self.output, self.extensions, self.context), [{'path': 'activity-extensions.json/revision_requests', 'message': 'revision requests must name distinct provided tasks or knowledge'}])
        self.assertEqual((self.output, self.extensions, self.context), before)

    def test_undeclared_write_has_exact_issue_and_no_mutation(self):
        self.assertEqual(revisions.submission_errors(self.output, self.extensions, self.context), [])
        self.output['candidates'] = [candidate('새 개정', revises='TK-absent')]
        before = deepcopy((self.output, self.extensions, self.context))
        self.assertEqual(revisions.submission_errors(self.output, self.extensions, self.context), [{'path': 'activity-extensions.json/revision_targets', 'message': 'existing records must be declared before this execution; submit revision_requests for new targets'}])
        self.assertEqual((self.output, self.extensions, self.context), before)

    def test_revised_without_write_has_exact_issue_and_no_mutation(self):
        self.assertEqual(revisions.submission_errors(self.output, self.extensions, self.context), [])
        self.extensions['revision_resolutions'][0]['disposition'] = 'revised'
        before = deepcopy((self.output, self.extensions, self.context))
        self.assertEqual(revisions.submission_errors(self.output, self.extensions, self.context), [{'path': 'activity-extensions.json/revision_resolutions', 'message': 'revised requires the corresponding authored change: TK-planning'}])
        self.assertEqual((self.output, self.extensions, self.context), before)

    def test_write_without_revised_has_exact_issue_and_no_mutation(self):
        self.assertEqual(revisions.submission_errors(self.output, self.extensions, self.context), [])
        self.output['candidates'] = [candidate('개정', revises=self.task['id'])]
        before = deepcopy((self.output, self.extensions, self.context))
        self.assertEqual(revisions.submission_errors(self.output, self.extensions, self.context), [{'path': 'activity-extensions.json/revision_resolutions', 'message': 'an authored revision must have disposition revised: TK-planning'}])
        self.assertEqual((self.output, self.extensions, self.context), before)

    def test_required_unchanged_has_exact_issue_and_no_mutation(self):
        self.assertEqual(revisions.submission_errors(self.output, self.extensions, self.context), [])
        self.context['action']['revision_targets'][self.task['id']]['required'] = True
        before = deepcopy((self.output, self.extensions, self.context))
        self.assertEqual(revisions.submission_errors(self.output, self.extensions, self.context), [{'path': 'activity-extensions.json/revision_resolutions', 'message': 'a required revision or rejected contract cannot be cancelled as unchanged'}])
        self.assertEqual((self.output, self.extensions, self.context), before)

    def test_invalid_delegation_has_exact_issue_and_no_mutation(self):
        self.assertEqual(revisions.submission_errors(self.output, self.extensions, self.context), [])
        self.extensions['revision_resolutions'][0]['disposition'] = 'delegated'
        before = deepcopy((self.output, self.extensions, self.context))
        self.assertEqual(revisions.submission_errors(self.output, self.extensions, self.context), [{'path': 'activity-extensions.json/revision_resolutions', 'message': 'delegated requires a prepared work task declaring this knowledge target'}])
        self.assertEqual((self.output, self.extensions, self.context), before)

    def test_extraneous_task_title_has_exact_issue_and_no_mutation(self):
        self.assertEqual(revisions.submission_errors(self.output, self.extensions, self.context), [])
        self.extensions['revision_resolutions'][0]['task_title'] = '다른 과제'
        before = deepcopy((self.output, self.extensions, self.context))
        self.assertEqual(revisions.submission_errors(self.output, self.extensions, self.context), [{'path': 'activity-extensions.json/revision_resolutions', 'message': 'task_title belongs only to a delegated knowledge revision'}])
        self.assertEqual((self.output, self.extensions, self.context), before)

    def test_unknown_knowledge_scope_has_exact_issue_and_no_mutation(self):
        self.assertEqual(revisions.submission_errors(self.output, self.extensions, self.context), [])
        self.extensions['task_conditions'] = [{'task_title': '계약', 'knowledge_revision_targets': ['KN-absent']}]
        before = deepcopy((self.output, self.extensions, self.context))
        self.assertEqual(revisions.submission_errors(self.output, self.extensions, self.context), [{'path': 'activity-extensions.json/task_conditions', 'message': 'knowledge revision work must name declared knowledge targets'}])
        self.assertEqual((self.output, self.extensions, self.context), before)

    def test_missing_resolution_has_exact_issue_and_no_mutation(self):
        self.assertEqual(revisions.submission_errors(self.output, self.extensions, self.context), [])
        self.extensions['revision_resolutions'] = []
        before = deepcopy((self.output, self.extensions, self.context))
        self.assertEqual(revisions.submission_errors(self.output, self.extensions, self.context), [{'path': 'activity-extensions.json/revision_resolutions', 'message': 'resolve each declared target exactly once, using a task withdrawal only for task targets'}])
        self.assertEqual((self.output, self.extensions, self.context), before)

    def test_unknown_resolution_has_exact_issue_and_no_mutation(self):
        self.assertEqual(revisions.submission_errors(self.output, self.extensions, self.context), [])
        self.extensions['revision_resolutions'][0]['record_id'] = 'TK-absent'
        before = deepcopy((self.output, self.extensions, self.context))
        self.assertEqual(revisions.submission_errors(self.output, self.extensions, self.context), [{'path': 'activity-extensions.json/revision_resolutions', 'message': 'resolve each declared target exactly once, using a task withdrawal only for task targets'}])
        self.assertEqual((self.output, self.extensions, self.context), before)

    def test_duplicate_replacement_reports_one_target_issue(self):
        self.output['candidates'] = [candidate('개정', revises=self.task['id'])]
        self.extensions['revision_resolutions'][0]['disposition'] = 'revised'
        self.assertEqual(revisions.submission_errors(self.output, self.extensions, self.context), [])
        self.output['candidates'] *= 2
        before = deepcopy((self.output, self.extensions, self.context))
        self.assertEqual(revisions.submission_errors(self.output, self.extensions, self.context), [{
            'path': 'activity-extensions.json/revision_targets',
            'message': 'each existing task may have only one replacement candidate per response'}])
        self.assertEqual((self.output, self.extensions, self.context), before)

    def test_same_task_cannot_be_selected_and_requested_for_revision(self):
        from support.role_answers import disposition
        self.output['dispositions'] = [disposition(self.task['id'])]
        self.extensions['revision_requests'] = [{'record_ids': [self.task['id']], 'reason': '개정 요청'}]
        before = deepcopy((self.output, self.extensions, self.context))
        self.assertEqual(revisions.submission_errors(self.output, self.extensions, self.context), [{
            'path': 'activity-extensions.json/revision_requests',
            'message': 'the same output cannot revise and select a task'}])
        self.assertEqual((self.output, self.extensions, self.context), before)

    def test_task_projection_is_available_without_the_tasks_catalog(self):
        self.context['task'] = self.context['tasks'].pop()
        self.assertEqual(revisions.submission_errors(self.output, self.extensions, self.context), [])
        self.assertEqual(self.context['task'], self.task)

    def test_capture_missing_target_and_changed_revision_are_explicit(self):
        runtime = {'tasks': {self.task['id']: self.task}}
        captured = revisions.capture_targets({}, runtime, [self.task['id']], required=True, source_ref='EX-source')
        self.assertEqual(captured, {self.task['id']: {'revision': 1, 'contract_sha256': planning.contract_hash(self.task),
                                                   'required': True, 'source_refs': ['EX-source']}})
        self.assertEqual(revisions.target_changes(captured, {}, runtime), [])
        self.assertEqual(revisions.target_changes(captured, {}, {'tasks': {}}), [{
            'id': self.task['id'], 'field': 'revision_target', 'reason': 'missing'}])
        before = deepcopy(runtime)
        with self.assertRaisesRegex(ValueError, '^revision target must name an existing task or knowledge: TK-absent$'):
            revisions.capture_targets({}, runtime, ['TK-absent'])
        self.assertEqual(runtime, before)
        changed = deepcopy(runtime)
        changed['tasks'][self.task['id']]['revision'] = 2
        self.assertEqual(revisions.target_changes(captured, {}, changed), [
            {'id': self.task['id'], 'field': 'revision', 'before': 1, 'after': 2},
            {'id': self.task['id'], 'field': 'contract_sha256', 'before': planning.contract_hash(self.task),
             'after': planning.contract_hash(changed['tasks'][self.task['id']])}])

    def test_cycles_include_self_cycle_and_ignore_missing_dependencies(self):
        task = contract()
        other = {**deepcopy(task), 'id': 'TK-other'}
        task['dependencies'] = ['TK-other', 'TK-missing']
        other['dependencies'] = [task['id']]
        tasks = {task['id']: task, other['id']: other}
        before = deepcopy(tasks)
        self.assertEqual(revisions.dependency_cycles(tasks), [['TK-planning', 'TK-other', 'TK-planning']])
        self.assertEqual(tasks, before)
        task['dependencies'] = [task['id']]
        self.assertEqual(revisions.dependency_cycles({task['id']: task}), [['TK-planning', 'TK-planning']])


class RepetitionInputTests(unittest.TestCase):
    def setUp(self):
        self.instance = {'id': 'RI-planning', 'config': {}}
        self.runtime = {'history': [], 'queue': []}
        self.clock = FakeClock()
        self.fields = {'lineage': 'contract_revision', 'lineage_id': 'TK-planning', 'event_ref': 'EX-revision',
                       'outcome': 'revised', 'owner': 'ai', 'reason': '실제 계약 개정', 'version': 2}

    def record(self):
        return revisions.record_repetition(self.instance, self.runtime, **self.fields, clock=self.clock)

    def test_rejects_lineage_without_history_or_queue_changes(self):
        self.fields['lineage'] = 'unknown'
        before = deepcopy((self.instance, self.runtime))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('unknown repetition lineage or owner') + '$'):
            self.record()
        self.assertEqual((self.instance, self.runtime), before)

    def test_rejects_owner_without_history_or_queue_changes(self):
        self.fields['owner'] = 'system'
        before = deepcopy((self.instance, self.runtime))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('unknown repetition lineage or owner') + '$'):
            self.record()
        self.assertEqual((self.instance, self.runtime), before)

    def test_rejects_event_without_history_or_queue_changes(self):
        self.fields['event_ref'] = ''
        before = deepcopy((self.instance, self.runtime))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('repetition needs its lineage, actual event, outcome and reason') + '$'):
            self.record()
        self.assertEqual((self.instance, self.runtime), before)

    def test_rejects_reason_without_history_or_queue_changes(self):
        self.fields['reason'] = ' '
        before = deepcopy((self.instance, self.runtime))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('repetition needs its lineage, actual event, outcome and reason') + '$'):
            self.record()
        self.assertEqual((self.instance, self.runtime), before)

    def test_rejects_version_zero_without_history_or_queue_changes(self):
        self.fields['version'] = 0
        before = deepcopy((self.instance, self.runtime))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('version receipt requires a positive semantic version') + '$'):
            self.record()
        self.assertEqual((self.instance, self.runtime), before)

    def test_rejects_version_boolean_without_history_or_queue_changes(self):
        self.fields['version'] = True
        before = deepcopy((self.instance, self.runtime))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('version receipt requires a positive semantic version') + '$'):
            self.record()
        self.assertEqual((self.instance, self.runtime), before)

    def test_rejects_limit_without_history_or_queue_changes(self):
        self.instance['config']['contract_revision_limit'] = 0
        before = deepcopy((self.instance, self.runtime))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('repetition limit must be an adopted positive integer') + '$'):
            self.record()
        self.assertEqual((self.instance, self.runtime), before)

    def test_rejects_regeneration_without_observation_without_history_or_queue_changes(self):
        self.fields['regenerate_after'] = '2090-01-02T00:00:00Z'
        before = deepcopy((self.instance, self.runtime))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('regeneration time must follow the machine observation') + '$'):
            self.record()
        self.assertEqual((self.instance, self.runtime), before)

    def test_receipt_is_idempotent_detached_and_conflicting_replay_is_rejected(self):
        expected = {'kind': 'task_repetition', **self.fields}
        self.assertEqual(self.record(), expected)
        before = deepcopy(self.runtime)
        again = self.record()
        self.assertEqual(again, expected)
        self.assertEqual(self.runtime, before)
        again['reason'] = '호출자가 바꾼 사본'
        self.assertEqual(self.runtime, before)
        self.fields['reason'] = '같은 사건의 다른 내용'
        with self.assertRaisesRegex(ValueError, '^same repetition receipt has different content$'):
            self.record()
        self.assertEqual(self.runtime, before)

    def test_continuation_without_current_decision_cannot_reset_history(self):
        self.record()
        self.fields.update(outcome='continued', event_ref='DC-missing', owner='user', decision_ref='DC-missing')
        before = deepcopy(self.runtime)
        with self.assertRaisesRegex(ValueError, '^continuation reset requires its explicit current decision$'):
            self.record()
        self.assertEqual(self.runtime, before)

    def test_lineage_projection_filters_other_tasks_but_keeps_version_counts(self):
        first = self.record()
        self.fields.update(lineage_id='TK-other', event_ref='EX-other', version=3)
        self.record()
        before = deepcopy(self.runtime)
        counts = task_contracts.repetition_lineages(self.runtime, 'TK-planning', include_events=False)
        self.assertEqual(counts['contract_revision'], {'count': 2, 'owner': 'ai', 'events': [], 'by_lineage': {'TK-planning': 2}})
        self.assertEqual(task_contracts.repetition_lineages(self.runtime, 'TK-planning')['contract_revision']['events'], [first])
        self.assertEqual(self.runtime, before)

    def test_regeneration_time_is_strictly_after_observation(self):
        self.assertTrue(revisions.regeneration_time_valid('2090-01-01T00:00:01Z', '2090-01-01T00:00:00Z'))
        self.assertFalse(revisions.regeneration_time_valid('2090-01-01T00:00:00Z', '2090-01-01T00:00:00Z'))
        self.assertFalse(revisions.regeneration_time_valid('2089-12-31T23:59:59Z', '2090-01-01T00:00:00Z'))

    def test_scope_omits_prose_and_detaches_nested_revision_targets(self):
        task = contract()
        action = {'id': 'AC-revise', 'role': 'research_preparation', 'reason': '설명',
                  'revision_targets': revisions.capture_targets({}, {'tasks': {task['id']: task}}, [task['id']])}
        expected = {key: deepcopy(action[key]) for key in ('id', 'role', 'revision_targets')}
        result = revisions.action_scope(action)
        self.assertEqual(result, expected)
        result['revision_targets'].clear()
        self.assertEqual(action['revision_targets'], expected['revision_targets'])

"""정상 계약 생산 뒤 한 필드 변조로 의무·계획 거부 사유와 불변성을 고정한다."""
from copy import deepcopy
import re
import unittest

from do_math import task_contracts as tc
from do_math import planning
from support.planning_contract_inputs import contract, fulfilled, selected_plan


class DispositionValidationTests(unittest.TestCase):

    def test_rejects_assessment_object_without_changing_input(self):
        task = contract()
        assessment = fulfilled(task)
        tc.validate_item_dispositions(task, assessment)
        assessment = []
        before = deepcopy((task, assessment))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('assessment must be an object') + '$'):
            tc.validate_item_dispositions(task, assessment)
        self.assertEqual((task, assessment), before)

    def test_rejects_rows_list_without_changing_input(self):
        task = contract()
        assessment = fulfilled(task)
        tc.validate_item_dispositions(task, assessment)
        assessment['item_dispositions'] = {}
        before = deepcopy((task, assessment))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('item_dispositions must be a list') + '$'):
            tc.validate_item_dispositions(task, assessment)
        self.assertEqual((task, assessment), before)

    def test_rejects_row_object_without_changing_input(self):
        task = contract()
        assessment = fulfilled(task)
        tc.validate_item_dispositions(task, assessment)
        assessment['item_dispositions'][0] = 1
        before = deepcopy((task, assessment))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('item disposition must be an object') + '$'):
            tc.validate_item_dispositions(task, assessment)
        self.assertEqual((task, assessment), before)

    def test_rejects_row_id_blank_without_changing_input(self):
        task = contract()
        assessment = fulfilled(task)
        tc.validate_item_dispositions(task, assessment)
        assessment['item_dispositions'][0]['obligation_id'] = ''
        before = deepcopy((task, assessment))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('item dispositions must identify each obligation at most once') + '$'):
            tc.validate_item_dispositions(task, assessment)
        self.assertEqual((task, assessment), before)

    def test_rejects_row_id_duplicate_without_changing_input(self):
        task = contract()
        assessment = fulfilled(task)
        tc.validate_item_dispositions(task, assessment)
        assessment['item_dispositions'] *= 2
        before = deepcopy((task, assessment))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('item dispositions must identify each obligation at most once') + '$'):
            tc.validate_item_dispositions(task, assessment)
        self.assertEqual((task, assessment), before)

    def test_rejects_row_kind_without_changing_input(self):
        task = contract()
        assessment = fulfilled(task)
        tc.validate_item_dispositions(task, assessment)
        assessment['item_dispositions'][0]['kind'] = 'unknown'
        before = deepcopy((task, assessment))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('unknown item disposition') + '$'):
            tc.validate_item_dispositions(task, assessment)
        self.assertEqual((task, assessment), before)

    def test_rejects_evidence_missing_without_changing_input(self):
        task = contract()
        assessment = fulfilled(task)
        tc.validate_item_dispositions(task, assessment)
        del assessment['item_dispositions'][0]['evidence_refs']
        before = deepcopy((task, assessment))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('item disposition requires evidence_refs') + '$'):
            tc.validate_item_dispositions(task, assessment)
        self.assertEqual((task, assessment), before)

    def test_rejects_evidence_type_without_changing_input(self):
        task = contract()
        assessment = fulfilled(task)
        tc.validate_item_dispositions(task, assessment)
        assessment['item_dispositions'][0]['evidence_refs'] = 'EX-planning-work'
        before = deepcopy((task, assessment))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('item disposition evidence_refs must be distinct references') + '$'):
            tc.validate_item_dispositions(task, assessment)
        self.assertEqual((task, assessment), before)

    def test_rejects_evidence_blank_without_changing_input(self):
        task = contract()
        assessment = fulfilled(task)
        tc.validate_item_dispositions(task, assessment)
        assessment['item_dispositions'][0]['evidence_refs'] = ['']
        before = deepcopy((task, assessment))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('item disposition evidence_refs must be distinct references') + '$'):
            tc.validate_item_dispositions(task, assessment)
        self.assertEqual((task, assessment), before)

    def test_rejects_evidence_duplicate_without_changing_input(self):
        task = contract()
        assessment = fulfilled(task)
        tc.validate_item_dispositions(task, assessment)
        assessment['item_dispositions'][0]['evidence_refs'] *= 2
        before = deepcopy((task, assessment))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('item disposition evidence_refs must be distinct references') + '$'):
            tc.validate_item_dispositions(task, assessment)
        self.assertEqual((task, assessment), before)

    def test_rejects_unknown_obligation_without_changing_input(self):
        task = contract()
        assessment = fulfilled(task)
        tc.validate_item_dispositions(task, assessment)
        assessment['item_dispositions'][0]['obligation_id'] = 'OB-absent'
        before = deepcopy((task, assessment))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('item disposition names an unknown obligation') + '$'):
            tc.validate_item_dispositions(task, assessment)
        self.assertEqual((task, assessment), before)

    def test_rejects_unresolved_list_without_changing_input(self):
        task = contract()
        assessment = fulfilled(task)
        tc.validate_item_dispositions(task, assessment)
        assessment['unresolved'] = {}
        before = deepcopy((task, assessment))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('unresolved must be a list') + '$'):
            tc.validate_item_dispositions(task, assessment)
        self.assertEqual((task, assessment), before)

    def test_rejects_unresolved_object_without_changing_input(self):
        task = contract()
        assessment = fulfilled(task)
        tc.validate_item_dispositions(task, assessment)
        assessment['unresolved'] = [1]
        before = deepcopy((task, assessment))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('unresolved inspection needs obligation_id, missing_inputs, and next_owner') + '$'):
            tc.validate_item_dispositions(task, assessment)
        self.assertEqual((task, assessment), before)

    def test_rejects_unresolved_shape_without_changing_input(self):
        task = contract()
        assessment = fulfilled(task)
        tc.validate_item_dispositions(task, assessment)
        assessment['unresolved'] = [{'obligation_id': 'OB-argument'}]
        before = deepcopy((task, assessment))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('unresolved inspection needs obligation_id, missing_inputs, and next_owner') + '$'):
            tc.validate_item_dispositions(task, assessment)
        self.assertEqual((task, assessment), before)

    def test_rejects_unresolved_already_disposed_without_changing_input(self):
        task = contract()
        assessment = fulfilled(task)
        tc.validate_item_dispositions(task, assessment)
        assessment['unresolved'] = [{'obligation_id': 'OB-argument', 'missing_inputs': ['source:later'], 'next_owner': 'research_work'}]
        before = deepcopy((task, assessment))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('unresolved inspection must name one undisposed obligation') + '$'):
            tc.validate_item_dispositions(task, assessment)
        self.assertEqual((task, assessment), before)

    def test_rejects_required_evidence_without_changing_input(self):
        task = contract()
        assessment = fulfilled(task)
        tc.validate_item_dispositions(task, assessment)
        task['completion_obligations'][0]['evidence_required'] = ['SO-required']
        before = deepcopy((task, assessment))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('item disposition lacks required evidence: OB-argument') + '$'):
            tc.validate_item_dispositions(task, assessment)
        self.assertEqual((task, assessment), before)

    def test_rejects_waiver_authority_without_changing_input(self):
        task = contract()
        assessment = fulfilled(task)
        tc.validate_item_dispositions(task, assessment)
        assessment['item_dispositions'][0]['kind'] = 'waived'
        before = deepcopy((task, assessment))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('waived obligation needs authority_ref') + '$'):
            tc.validate_item_dispositions(task, assessment)
        self.assertEqual((task, assessment), before)

    def test_rejects_transfer_target_without_changing_input(self):
        task = contract()
        assessment = fulfilled(task)
        tc.validate_item_dispositions(task, assessment)
        assessment['item_dispositions'][0]['kind'] = 'transferred'
        before = deepcopy((task, assessment))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('transferred obligation needs authority and target obligation') + '$'):
            tc.validate_item_dispositions(task, assessment)
        self.assertEqual((task, assessment), before)

    def test_rejects_all_obligations_without_changing_input(self):
        task = contract()
        assessment = fulfilled(task)
        tc.validate_item_dispositions(task, assessment)
        assessment['item_dispositions'] = []
        before = deepcopy((task, assessment))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('every obligation requires a disposition or unresolved inspection') + '$'):
            tc.validate_item_dispositions(task, assessment)
        self.assertEqual((task, assessment), before)

    def test_rejects_terminal_open_without_changing_input(self):
        task = contract()
        assessment = fulfilled(task)
        tc.validate_item_dispositions(task, assessment)
        assessment['item_dispositions'][0]['kind'] = 'open'
        before = deepcopy((task, assessment))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('terminal assessment retains open obligations') + '$'):
            tc.validate_item_dispositions(task, assessment)
        self.assertEqual((task, assessment), before)

    def test_rejects_closure_authority_without_changing_input(self):
        task = contract()
        assessment = fulfilled(task)
        tc.validate_item_dispositions(task, assessment)
        assessment['decision'] = 'closed'
        before = deepcopy((task, assessment))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('closure needs an authoritative scope disposition') + '$'):
            tc.validate_item_dispositions(task, assessment)
        self.assertEqual((task, assessment), before)

    def test_rejects_terminal_status_mismatch_without_changing_input(self):
        task = contract()
        assessment = fulfilled(task)
        tc.validate_item_dispositions(task, assessment)
        task['status'] = 'closed'
        before = deepcopy((task, assessment))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('terminal task status differs from its assessment decision') + '$'):
            tc.validate_item_dispositions(task, assessment)
        self.assertEqual((task, assessment), before)

    def test_rejects_missing_inputs_without_changing_input(self):
        task = contract()
        assessment = fulfilled(task)
        assessment.update(decision='incomplete', item_dispositions=[], unresolved=[{
            'obligation_id': 'OB-argument', 'missing_inputs': ['source:later'], 'next_owner': 'research_work'}])
        tc.validate_item_dispositions(task, assessment)
        assessment['unresolved'][0]['missing_inputs'] = []
        before = deepcopy((task, assessment))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('unresolved inspection needs missing inputs') + '$'):
            tc.validate_item_dispositions(task, assessment)
        self.assertEqual((task, assessment), before)

    def test_rejects_missing_inputs_type_without_changing_input(self):
        task = contract()
        assessment = fulfilled(task)
        assessment.update(decision='incomplete', item_dispositions=[], unresolved=[{
            'obligation_id': 'OB-argument', 'missing_inputs': ['source:later'], 'next_owner': 'research_work'}])
        tc.validate_item_dispositions(task, assessment)
        assessment['unresolved'][0]['missing_inputs'] = 'source:later'
        before = deepcopy((task, assessment))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('unresolved inspection needs missing inputs') + '$'):
            tc.validate_item_dispositions(task, assessment)
        self.assertEqual((task, assessment), before)

    def test_rejects_unknown_unresolved_without_changing_input(self):
        task = contract()
        assessment = fulfilled(task)
        assessment.update(decision='incomplete', item_dispositions=[], unresolved=[{
            'obligation_id': 'OB-argument', 'missing_inputs': ['source:later'], 'next_owner': 'research_work'}])
        tc.validate_item_dispositions(task, assessment)
        assessment['unresolved'][0]['obligation_id'] = 'OB-absent'
        before = deepcopy((task, assessment))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('unresolved inspection must name one undisposed obligation') + '$'):
            tc.validate_item_dispositions(task, assessment)
        self.assertEqual((task, assessment), before)

    def test_rejects_duplicate_unresolved_without_changing_input(self):
        task = contract()
        assessment = fulfilled(task)
        assessment.update(decision='incomplete', item_dispositions=[], unresolved=[{
            'obligation_id': 'OB-argument', 'missing_inputs': ['source:later'], 'next_owner': 'research_work'}])
        tc.validate_item_dispositions(task, assessment)
        assessment['unresolved'] *= 2
        before = deepcopy((task, assessment))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('unresolved inspection must name one undisposed obligation') + '$'):
            tc.validate_item_dispositions(task, assessment)
        self.assertEqual((task, assessment), before)

    def test_rejects_complete_unresolved_without_changing_input(self):
        task = contract()
        assessment = fulfilled(task)
        assessment.update(decision='incomplete', item_dispositions=[], unresolved=[{
            'obligation_id': 'OB-argument', 'missing_inputs': ['source:later'], 'next_owner': 'research_work'}])
        tc.validate_item_dispositions(task, assessment)
        assessment['decision'] = 'completed'
        before = deepcopy((task, assessment))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('unresolved or undisposed completion obligations remain') + '$'):
            tc.validate_item_dispositions(task, assessment)
        self.assertEqual((task, assessment), before)

    def test_obligations_and_residual_scope_are_exact(self):
        task = contract()
        assessment = fulfilled(task)
        before = deepcopy(task)
        self.assertEqual(tc.contract_obligations(task), task['completion_obligations'])
        self.assertEqual(tc.remaining_obligations(task), ['OB-argument'])
        self.assertEqual(tc.remaining_obligations(task, assessment), [])
        self.assertEqual(task, before)

    def test_nonlist_obligation_container_is_rejected(self):
        task = contract()
        task['completion_obligations'] = {}
        before = deepcopy(task)
        with self.assertRaisesRegex(ValueError, '^completion_obligations must be a list$'):
            tc.contract_obligations(task)
        self.assertEqual(task, before)

    def test_duplicate_profile_identity_is_rejected_even_with_different_editions(self):
        from do_math.execution_profiles import build_profiles
        from do_math.configuration import DEFAULT_CONFIG
        from support.fakes.host import make_fake
        task = contract()
        editions = build_profiles(DEFAULT_CONFIG, host=make_fake())
        task['profile_refs'] = [editions['role_profile_refs']['research_work'][0]]
        tc.validate_task_contract(task)
        task['profile_refs'].append({**task['profile_refs'][0], 'revision': 2})
        before = deepcopy(task)
        with self.assertRaisesRegex(ValueError, '^profile_refs must identify distinct profiles$'):
            tc.validate_contract_meaning(task)
        self.assertEqual(task, before)

    def test_duplicate_obligation_identity_is_rejected(self):
        task = contract()
        task['completion_obligations'].append({**task['completion_obligations'][0], 'claim': '다른 주장'})
        before = deepcopy(task)
        with self.assertRaisesRegex(ValueError, '^completion_obligations must have distinct stable IDs$'):
            tc.validate_contract_meaning(task)
        self.assertEqual(task, before)

    def test_distinct_ids_rejects_nonrecord_and_empty_identity(self):
        for rows in ([False], [{'id': ''}], [{'id': 5}], [{'id': 'A'}, {'id': 'A'}]):
            with self.subTest(rows=rows):
                before = deepcopy(rows)
                with self.assertRaisesRegex(ValueError, '^obligations must have distinct stable IDs$'):
                    tc._distinct_ids(rows, 'obligations')
                self.assertEqual(rows, before)

    def test_designated_judge_and_specialist_family_have_distinct_authority(self):
        task = contract()
        assessment = fulfilled(task)
        obligation = task['completion_obligations'][0]
        self.assertTrue(tc.assessor_is_judge(obligation, 'research_plan', 'EX-plan'))
        self.assertFalse(tc.assessor_is_judge(obligation, 'research_work', 'EX-work'))
        obligation['judges'] = ['formal_check']
        self.assertEqual(tc.judge_coverage_errors('research_plan', 'EX-plan', task, assessment,
                                                {'EX-planning-work': 'formal-result'}), [])
        self.assertEqual(tc.judge_coverage_errors('research_plan', 'EX-plan', task, assessment, {}), [
            "fulfilled obligation OB-argument needs its designated judge ['formal_check'] or cited evidence of the family ['formal-result']"])
        obligation['judges'] = ['EX-plan']
        self.assertTrue(tc.assessor_is_judge(obligation, 'research_plan', 'EX-plan'))


class PlanDispositionValidationTests(unittest.TestCase):

    def test_rejects_unknown_ready_and_preserves_population(self):
        task = contract()
        tasks = {task['id']: task}
        ready = [task['id']]
        plan = selected_plan(task)

        tc.validate_plan_dispositions(plan, tasks, ready)
        ready.append('TK-absent')
        before = deepcopy((plan, tasks, ready))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('ready population names an unknown task') + '$'):
            tc.validate_plan_dispositions(plan, tasks, ready)
        self.assertEqual((plan, tasks, ready), before)

    def test_rejects_reobservation_and_preserves_population(self):
        task = contract()
        tasks = {task['id']: task}
        ready = [task['id']]
        plan = selected_plan(task)
        plan['dispositions'][0]['kind'] = 'not_selected'
        plan['dispositions'][0]['revisit']['event_refs'] = ['EV-next']
        tc.validate_plan_dispositions(plan, tasks, ready)
        plan['dispositions'][0]['revisit']['event_refs'] = []
        before = deepcopy((plan, tasks, ready))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('nonselection requires a reobservation condition') + '$'):
            tc.validate_plan_dispositions(plan, tasks, ready)
        self.assertEqual((plan, tasks, ready), before)

    def test_rejects_missing_inputs_and_preserves_population(self):
        task = contract()
        tasks = {task['id']: task}
        ready = [task['id']]
        plan = selected_plan(task)
        plan['dispositions'][0].update(kind='not_assessable', missing_inputs=['source:later'])
        plan['dispositions'][0]['revisit']['event_refs'] = ['EV-next']
        tc.validate_plan_dispositions(plan, tasks, ready)
        plan['dispositions'][0]['missing_inputs'] = []
        before = deepcopy((plan, tasks, ready))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('not_assessable requires missing inputs') + '$'):
            tc.validate_plan_dispositions(plan, tasks, ready)
        self.assertEqual((plan, tasks, ready), before)

    def test_rejects_self_parallel_and_preserves_population(self):
        task = contract()
        tasks = {task['id']: task}
        ready = [task['id']]
        plan = selected_plan(task)

        tc.validate_plan_dispositions(plan, tasks, ready)
        plan['dispositions'][0]['parallel_task_ids'] = [task['id']]
        before = deepcopy((plan, tasks, ready))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('parallel references must identify distinct other tasks') + '$'):
            tc.validate_plan_dispositions(plan, tasks, ready)
        self.assertEqual((plan, tasks, ready), before)

    def test_rejects_unknown_parallel_and_preserves_population(self):
        task = contract()
        tasks = {task['id']: task}
        ready = [task['id']]
        plan = selected_plan(task)

        tc.validate_plan_dispositions(plan, tasks, ready)
        plan['dispositions'][0]['parallel_task_ids'] = ['TK-absent']
        before = deepcopy((plan, tasks, ready))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('parallel references must identify distinct other tasks') + '$'):
            tc.validate_plan_dispositions(plan, tasks, ready)
        self.assertEqual((plan, tasks, ready), before)

    def test_returned_task_cannot_be_selected_in_its_assessment_plan(self):
        task = contract()
        task['results'] = [{'id': 'EV-return', 'execution_id': 'EX-planning-work'}]
        plan = selected_plan(task)
        plan['task_assessments'] = [fulfilled(task)]
        before = deepcopy((task, plan))
        with self.assertRaisesRegex(ValueError, '^returned tasks require disposition before a later selection$'):
            tc.validate_plan_dispositions(plan, {task['id']: task}, [task['id']])
        self.assertEqual((task, plan), before)

    def test_nonselection_timestamp_and_selected_ids_are_exact(self):
        task = contract()
        plan = selected_plan(task)
        self.assertEqual(tc.selected_task_ids(plan), [task['id']])
        plan['dispositions'][0].update(kind='not_selected', revisit={'event_refs': [], 'at': '2090-01-02T00:00:00Z'})
        self.assertIsNone(tc.validate_plan_dispositions(plan, {task['id']: task}, [task['id']]))
        self.assertEqual(tc.selected_task_ids(plan), [])

    def test_returned_population_tracks_both_seals_and_currentness(self):
        from do_math.canonical import exact_content_hash
        task = contract()
        task['results'] = [{'id': 'EV-return', 'execution_id': 'EX-planning-work'}]
        tasks = {task['id']: task}
        self.assertEqual(tc.returned_task_ids(tasks), [task['id']])
        task['assessment'] = {'contract_sha256': planning.contract_hash(task),
                              'results_sha256': exact_content_hash(task['results']), 'current': True}
        self.assertEqual(tc.returned_task_ids(tasks), [])
        task['assessment']['current'] = False
        self.assertEqual(tc.returned_task_ids(tasks), [task['id']])
        task['status'] = 'completed'
        self.assertEqual(tc.returned_task_ids(tasks), [])


class AssessmentPopulationPrefixTests(unittest.TestCase):
    def test_unknown_assessment_is_rejected_before_task_lookup(self):
        from do_math.task_contracts import validate_plan_dispositions
        plan = {'dispositions': [], 'task_assessments': [{'task_id': 'TK-unknown'}]}
        reason = "plan must assess every returned task exactly once: missing=[]; unexpected=['TK-unknown']; duplicate=[]"
        # A task lookup would raise KeyError; the exact ValueError pins the earlier population rejection.
        with self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
            validate_plan_dispositions(plan, {}, [])

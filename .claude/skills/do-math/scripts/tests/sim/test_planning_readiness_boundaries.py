"""승인된 실제 과제의 준비성·검토 봉인·고갈 판단에서 남은 입력 축을 확인한다."""
from copy import deepcopy
import unittest

from do_math import planning, task_contracts
from support.engine_lifecycle import _ended_execution, approve, clear_work
from support.planning_contract_inputs import prepared_sim, warm_prepared, only_task, returned, produce_task
from support.role_answers import review_items

setUpModule = warm_prepared


class ReadinessBoundaries(unittest.TestCase):
    def setUp(self):
        self.sim = prepared_sim()
        self.engine = self.sim.engine

    def ready(self, **options):
        return planning.task_ready(only_task(self.sim), self.sim.instance, self.sim.runtime,
                                   evaluation_context=self.engine._evaluation_context(), **options)

    def exhaustion(self):
        # dispatch_engine._schedule_reconsideration이 넘기는 동일한 질의 보기다.
        return planning.exhaustion_state(self.sim.instance, {**self.sim.runtime, 'status': 'active'},
            now=self.sim.ports.clock.now(), evaluation_context=self.engine._evaluation_context())

    def test_incomplete_review_reports_item_review_failure(self):
        task = only_task(self.sim)
        review = deepcopy(task['reviews'][-1])
        self.assertTrue(planning.contract_review_current(review, task, self.sim.instance, self.sim.runtime)['valid'])
        review['item_reviews'] = []
        before = deepcopy((review, task, self.sim.instance, self.sim.runtime))
        result = planning.contract_review_current(review, task, self.sim.instance, self.sim.runtime)
        self.assertEqual(result, {'valid': False, 'changes': [{'field': 'item_reviews', 'after': 'incomplete_review'}]})
        self.assertEqual((review, task, self.sim.instance, self.sim.runtime), before)

    def test_review_summary_cannot_disagree_with_complete_item_reviews(self):
        task = only_task(self.sim)
        review = deepcopy(task['reviews'][-1])
        self.assertTrue(planning.contract_review_current(review, task, self.sim.instance, self.sim.runtime)['valid'])
        review['decision'] = 'revision_required'
        before = deepcopy((review, task, self.sim.instance, self.sim.runtime))
        self.assertEqual(planning.contract_review_current(review, task, self.sim.instance, self.sim.runtime), {
            'valid': False, 'changes': [{'field': 'item_reviews', 'after': 'summary_does_not_match'}]})
        self.assertEqual((review, task, self.sim.instance, self.sim.runtime), before)

    def test_author_cannot_seal_its_own_contract_review(self):
        task = only_task(self.sim)
        before = deepcopy((self.sim.instance, self.sim.runtime))
        with self.assertRaisesRegex(ValueError, '^contract author cannot independently review its contract$'):
            planning.seal_contract_review(task, review_items([task['id']]), self.sim.instance, self.sim.runtime,
                                          execution_id=task['producer_execution'])
        self.assertEqual((self.sim.instance, self.sim.runtime), before)

    def test_missing_governance_during_review_is_an_evaluation_error(self):
        self.assertEqual(self.ready()['state'], 'ready')
        self.sim.instance['governance'] = {}
        before = deepcopy((self.sim.instance, self.sim.runtime))
        self.assertEqual(self.ready(), {'state': 'evaluation_error', 'basis': [], 'errors': ['no unique approved charter']})
        self.assertEqual((self.sim.instance, self.sim.runtime), before)

    def test_profile_not_matching_work_role_is_ignored_without_losing_valid_work_profiles(self):
        task = only_task(self.sim)
        task['profile_refs'].extend(deepcopy(self.sim.instance['role_profile_refs']['task_contract_review']))
        approve(self.engine, task)
        before = deepcopy((self.sim.instance, self.sim.runtime))
        result = self.ready()
        self.assertEqual(result['state'], 'ready')
        self.assertEqual(result['profile_ids'], [ref['id'] for ref in task['profile_refs']
            if self.sim.instance['execution_profiles'][ref['id']]['role'] == 'research_work'])
        self.assertEqual((self.sim.instance, self.sim.runtime), before)

    def test_approved_old_profile_set_does_not_authorize_newly_added_profile(self):
        from do_math.model_policy import work_profile_selection
        task = only_task(self.sim)
        ref = work_profile_selection(self.sim.instance['config'], task, self.sim.instance)['profile_ref']
        # 정본 승인 봉인의 프로필 한 항목만 손상시킨다.
        task['reviews'][-1]['task_basis']['profiles'][ref['id']] = 'f' * 64
        before = deepcopy((self.sim.instance, self.sim.runtime))
        result = self.ready()
        self.assertEqual(result, {'state': 'not_ready', 'basis': [],
            'errors': ['work profile requirement: required work profile is outside the current contract approval'],
            'waits': [{'kind': 'contract_revision', 'target_refs': [task['id']], 'next_owner': 'research_preparation'}]})
        self.assertEqual((self.sim.instance, self.sim.runtime), before)

    def test_duplicate_record_population_is_not_reported_as_exhausted(self):
        task = only_task(self.sim)
        self.sim.runtime['tasks']['TK-duplicate'] = deepcopy(task)
        before = deepcopy((self.sim.instance, self.sim.runtime))
        result = self.exhaustion()
        self.assertEqual(result, {'exhausted': False, 'prepare': False,
                                 'reasons': ['readiness_evaluation_error'], 'next_owner': 'operational_review'})
        self.assertEqual((self.sim.instance, self.sim.runtime), before)

    def test_returned_results_require_assessment_before_exhaustion(self):
        returned(self.sim)
        clear_work(self.sim)
        before = deepcopy((self.sim.instance, self.sim.runtime))
        result = self.exhaustion()
        self.assertEqual(result, {'exhausted': False, 'prepare': False,
                                 'reasons': ['returned_work_requires_assessment'], 'next_owner': 'research_plan'})
        self.assertEqual((self.sim.instance, self.sim.runtime), before)

    def test_current_waiting_task_without_selection_requires_explicit_continuation(self):
        only_task(self.sim)['status'] = 'waiting'
        before = deepcopy((self.sim.instance, self.sim.runtime))
        self.assertEqual(self.ready(), {'state': 'not_ready', 'basis': [],
                                       'errors': ['subsequent work needs an explicit continuation basis']})
        self.assertEqual((self.sim.instance, self.sim.runtime), before)

    def test_completed_dependency_without_assessment_is_not_ready(self):
        from do_math.task_scope import apply_task_assessments
        assessment = returned(self.sim)
        identifier = only_task(self.sim)['id']
        self.engine.instance, self.engine.runtime = apply_task_assessments(
            self.sim.instance, self.sim.runtime, [assessment], execution_id='EX-planning-plan',
            input_tasks=deepcopy(self.sim.runtime['tasks']), clock=self.sim.ports.clock)
        other = produce_task(self.sim, '의존 소비자')
        consumer = self.sim.runtime['tasks'][other]
        consumer['dependencies'] = [identifier]
        approve(self.engine, consumer)
        clear_work(self.sim)
        consumer = self.sim.runtime['tasks'][other]
        result = planning.task_ready(consumer, self.sim.instance, self.sim.runtime,
                                    evaluation_context=self.engine._evaluation_context())
        self.assertEqual(result['state'], 'ready')
        del self.sim.runtime['tasks'][identifier]['assessment']
        before = deepcopy((self.sim.instance, self.sim.runtime))
        self.assertEqual(planning.task_ready(consumer, self.sim.instance, self.sim.runtime,
            evaluation_context=self.engine._evaluation_context()), {'state': 'not_ready', 'basis': [],
                'errors': ['dependency lacks a current completion assessment: ' + identifier]})
        self.assertEqual((self.sim.instance, self.sim.runtime), before)

    def test_available_inputs_are_deduplicated_and_source_names_are_waited_for(self):
        from do_math.input_basis import aliases
        before = deepcopy((self.sim.instance, self.sim.runtime))
        available = task_contracts.available_input_refs(self.sim.instance, self.sim.runtime, lean_available=False)
        expected = {*task_contracts.FIXED_INPUT_REFS, 'tool:lean', *self.sim.instance['knowledge'], *self.sim.runtime['tasks']}
        for source in self.sim.instance['sources']:
            expected.update(aliases(source))
        self.assertEqual(available, sorted(expected))
        self.assertEqual(task_contracts.unsupplied_task_inputs(['source:future', 'context:goal'], set(available), admit_named_sources=True), [])
        self.assertEqual(task_contracts.unsupplied_task_inputs(['source:future', 'context:goal'], set(available), admit_named_sources=False), ['source:future'])
        self.assertEqual((self.sim.instance, self.sim.runtime), before)

    def test_event_recording_is_once_per_cause_with_exact_pending_ids(self):
        self.sim.runtime['next_research_reconsider_at'] = self.sim.ports.clock.now()
        before_events = deepcopy(self.sim.runtime['events'])
        before_pending = list(self.sim.runtime['pending_events'])
        expected = planning.collect_due_events(self.sim.instance, self.sim.runtime, self.sim.ports.clock.now())
        self.assertEqual([row['kind'] for row in expected], ['research_reconsider_due'])
        result = planning.record_due_events(self.sim.instance, self.sim.runtime, self.sim.ports.clock.now())
        self.assertEqual(result, expected)
        self.assertEqual(self.sim.runtime['events'], before_events + expected)
        self.assertEqual(self.sim.runtime['pending_events'], before_pending + [row['id'] for row in expected])
        self.sim.advance(1)
        before = deepcopy(self.sim.runtime)
        self.assertEqual(planning.record_due_events(self.sim.instance, self.sim.runtime, self.sim.ports.clock.now()), [])
        self.assertEqual(self.sim.runtime, before)
        self.engine._save()

    def test_nonrecord_task_entry_cannot_generate_a_due_event(self):
        task = only_task(self.sim)
        self.sim.runtime['next_research_reconsider_at'] = None
        self.assertEqual(planning.collect_due_events(self.sim.instance, self.sim.runtime, self.sim.ports.clock.now()), [])
        self.sim.runtime['tasks'][task['id']] = False
        before = deepcopy((self.sim.instance, self.sim.runtime))
        self.assertEqual(planning.collect_due_events(self.sim.instance, self.sim.runtime, self.sim.ports.clock.now()), [])
        self.assertEqual((self.sim.instance, self.sim.runtime), before)

    def test_closed_instance_never_wakes_or_schedules_new_research(self):
        self.sim.runtime['status'] = 'closed'
        before = deepcopy(self.sim.runtime)
        self.assertTrue(planning.instance_ended(self.sim.instance, self.sim.runtime))
        self.assertEqual(planning.research_wake_reasons(self.sim.instance, self.sim.runtime, now=self.sim.ports.clock.now()), [])
        self.assertEqual(planning.schedule_reconsideration(self.sim.instance, self.sim.runtime,
            now=self.sim.ports.clock.now(), clock=self.sim.ports.clock), {
                'exhausted': False, 'prepare': False, 'reasons': [], 'next_owner': None})
        self.assertEqual(self.sim.runtime, before)

    def test_assessment_input_wait_prevents_exhaustion_without_new_work(self):
        from do_math.task_scope import apply_task_assessments
        assessment = returned(self.sim)
        assessment.update(decision='incomplete', item_dispositions=[], unresolved=[{
            'obligation_id': 'OB-argument', 'missing_inputs': ['source:later'], 'next_owner': 'research_work'}])
        self.engine.instance, self.engine.runtime = apply_task_assessments(
            self.sim.instance, self.sim.runtime, [assessment], execution_id='EX-planning-plan',
            input_tasks=deepcopy(self.sim.runtime['tasks']), clock=self.sim.ports.clock)
        clear_work(self.sim)
        before = deepcopy((self.sim.instance, self.sim.runtime))
        self.assertEqual(self.exhaustion(), {
                'exhausted': False, 'prepare': False, 'reasons': ['external_waits'], 'next_owner': 'research_work'})
        self.assertEqual((self.sim.instance, self.sim.runtime), before)

    def test_empty_generation_hold_prevents_automatic_regeneration(self):
        from do_math import revisions
        from support.engine_lifecycle import applied
        from support.planning_contract_inputs import withdraw
        withdraw(self.sim, only_task(self.sim)['id'])
        applied(self.sim, 'configure', config={'exhaustion_empty_limit': 1})
        clear_work(self.sim)
        _ended_execution(self.engine, 'EX-empty-result', 'research_preparation')
        action = {'id': 'AC-empty-result', 'role': 'research_preparation'}
        revisions.bind_repetition_bases(self.sim.instance, self.sim.runtime, action)
        revisions.record_execution_outcome(self.sim.instance, self.sim.runtime, action,
            {'summary': '후보 없음'}, 'EX-empty-result', accepted=True, clock=self.sim.ports.clock)
        before = deepcopy((self.sim.instance, self.sim.runtime))
        result = self.exhaustion()
        self.assertIs(result['exhausted'], True)
        self.assertIs(result['prepare'], False)
        self.assertEqual((result['reasons'], result['next_owner']), (['exhaustion_lineage_hold'], 'user'))
        self.assertEqual(result['basis']['last_preparation']['event_ref'], 'EX-empty-result')
        self.assertEqual((self.sim.instance, self.sim.runtime), before)

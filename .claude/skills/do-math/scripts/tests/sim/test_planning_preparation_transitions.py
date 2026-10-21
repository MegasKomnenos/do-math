"""계획 수신자의 메타데이터·규칙 대기·큐 처분을 실제 엔진과 저장으로 확인한다."""
from copy import deepcopy
import unittest

from do_math import planning
from do_math.canonical import exact_content_hash
from do_math.model_policy import assessment_basis
from support.engine_lifecycle import _ended_execution, clear_work
from support.planning_owner import enqueue
from support.planning_contract_inputs import prepared_sim, warm_prepared, only_task, select, withdraw

setUpModule = warm_prepared


class PreparationTransitions(unittest.TestCase):
    def setUp(self):
        self.sim = prepared_sim()
        self.engine = self.sim.engine
        self.identifier = only_task(self.sim)['id']

    def preparation(self, *, defer=False):
        task = only_task(self.sim)
        action = enqueue(self.engine, 'research_preparation', assessment_targets={task['id']: assessment_basis(task)})
        _ended_execution(self.engine, 'EX-rating', 'research_preparation')
        extension = ({'model_assessment_deferrals': [{'task_id': task['id'], 'reason': '평가 입력 대기',
            'missing_inputs': ['user_input'], 'next_owner': 'user'}]} if defer else
            {'model_assessments': [{'task_id': task['id'], 'difficulty': 'low', 'importance': 'medium', 'reason': '독립 평가'}]})
        self.sim.runtime['executions']['EX-rating']['extensions'] = extension
        self.engine._apply_model_metadata(action, {'candidates': []}, 'EX-rating')
        return action

    def test_targeted_preparation_reports_the_actual_running_task_coordinates(self):
        from do_math.execution_lifecycle import transition_execution
        from support.wait_reporting import assert_status_report
        task = only_task(self.sim)
        action = enqueue(self.engine, 'research_preparation', assessment_targets={task['id']: assessment_basis(task)})
        execution = self.engine._register_execution(action,
            {'id': 'EX-targeted-live', 'role': 'research_preparation', 'status': 'running'})
        self.engine._save()
        report, human = assert_status_report(self, self.engine)
        row = next(row for row in report['tasks'] if row['id'] == task['id'])
        self.assertEqual(row['active_execution_ids'], [execution['id']])
        self.assertNotIn(action['id'], row['selected_actions'])
        self.assertIsNone(row['readiness'])
        self.assertIn('active_records=' + execution['id'], next(line for line in human.splitlines()
            if line.startswith('  ' + task['id'] + ' revision=')))
        for status in ('stopping', 'ended'):
            transition_execution(self.sim.runtime['executions'][execution['id']], status, at=self.sim.clock.now(),
                **({'outcome': 'execution_incomplete'} if status == 'ended' else {}))
        self.engine._save()

    def test_nonplanning_role_cannot_author_model_assessments(self):
        _ended_execution(self.engine, 'EX-work-metadata', 'research_work')
        action = {'role': 'research_work', 'target': self.identifier}
        self.engine._apply_model_metadata(action, {}, 'EX-work-metadata')
        self.sim.runtime['executions']['EX-work-metadata']['extensions'] = {'model_assessments': [{
            'task_id': self.identifier, 'difficulty': 'low', 'importance': 'low', 'reason': '허용되지 않은 작성자'}]}
        before = deepcopy(self.sim.runtime)
        head = self.engine.head
        with self.assertRaisesRegex(ValueError, '^only preparation and planning author model assessments$'):
            self.engine._apply_model_metadata(action, {}, 'EX-work-metadata')
        self.assertEqual(self.sim.runtime, before)
        self.assertEqual(self.engine.head, head)

    def test_model_metadata_stores_detached_exact_rating(self):
        self.preparation()
        expected = {self.identifier: {'difficulty': 'low', 'importance': 'medium', 'reason': '독립 평가'}}
        execution = self.sim.runtime['executions']['EX-rating']
        self.assertEqual(execution['model_decisions'], expected)
        execution['extensions']['model_assessments'][0]['reason'] = '작성자 사본 변경'
        self.assertEqual(execution['model_decisions'], expected)
        self.engine._save()
        self.sim.restart()
        self.assertEqual(self.sim.runtime['executions']['EX-rating']['model_decisions'], expected)

    def test_deferral_records_input_version_and_repeated_refresh_is_stable(self):
        action = self.preparation(defer=True)
        self.engine._finish_assessment_preparation(action, 'EX-rating')
        self.engine._remove_action(action)
        waiting = self.sim.runtime['waiting_actions'][action['id']]
        self.assertEqual(waiting['kind'], 'model_assessment_input')
        self.assertEqual(waiting['input_version'], self.engine._assessment_input_version())
        self.assertEqual(waiting['action']['assessment_targets'], {self.identifier: assessment_basis(only_task(self.sim))})
        # 이미 평가가 있는 과제의 명시적 재평가 대기는 다음 갱신이 회수한다.
        previous_history = deepcopy(self.sim.runtime['history'])
        self.assertEqual(self.engine._ensure_model_assessments(), set())
        self.assertEqual(self.sim.runtime['waiting_actions'], {})
        self.assertEqual(self.sim.runtime['history'], [*previous_history, {
            'kind': 'assessment_inputs_changed', 'action_id': action['id']}])
        before = deepcopy(self.sim.runtime)
        self.assertEqual(self.engine._ensure_model_assessments(), set())
        self.assertEqual(self.sim.runtime, before)
        self.engine._save()

    def test_invalid_task_rules_prevent_review_after_rating_application(self):
        action = self.preparation()
        only_task(self.sim)['initial_observation_rules'] = []
        queue = deepcopy(self.sim.runtime['queue'])
        self.engine._finish_assessment_preparation(action, 'EX-rating')
        self.assertEqual(only_task(self.sim)['model_assessment'], {
            'difficulty': 'low', 'importance': 'medium', 'reason': '독립 평가'})
        self.assertEqual(self.sim.runtime['queue'], queue)

    def test_finished_preparation_enqueues_exact_current_review_basis(self):
        action = self.preparation()
        self.engine._finish_assessment_preparation(action, 'EX-rating')
        reviews = [a for a in self.sim.runtime['queue'] if a['role'] == 'task_contract_review']
        self.assertEqual(len(reviews), 1)
        review = reviews[0]
        task = only_task(self.sim)
        self.assertEqual(review['target'], self.identifier)
        self.assertEqual(review['contract_basis'], {**assessment_basis(task), **planning.governance_revisions(self.sim.instance)})
        self.assertEqual(review['review_basis_key'], planning.review_basis_key(task, self.sim.instance, self.sim.runtime))
        self.engine._save()
        self.sim.restart()
        self.assertEqual([a for a in self.sim.runtime['queue'] if a['role'] == 'task_contract_review'], reviews)

    def test_rule_deferral_input_version_binds_user_input_and_task_hash(self):
        task = only_task(self.sim)
        expected = {'user_input': [row.get('id') for row in self.sim.runtime['inputs']],
                    task['id']: exact_content_hash(task), 'source:absent': None}
        before = deepcopy((self.sim.instance, self.sim.runtime))
        self.assertEqual(self.engine._rule_deferral_inputs([{'missing_inputs': list(expected)}]), expected)
        self.assertEqual((self.sim.instance, self.sim.runtime), before)

    def test_closed_preparation_target_is_removed_from_its_wait(self):
        action = self.preparation(defer=True)
        self.engine._finish_assessment_preparation(action, 'EX-rating')
        self.engine._remove_action(action)
        self.engine._save()
        withdraw(self.sim, self.identifier)
        history = deepcopy(self.sim.runtime['history'])
        self.engine._retire_closed_revision_targets()
        self.assertEqual(self.sim.runtime['waiting_actions'], {})
        self.assertEqual(self.sim.runtime['history'], [*history, {
            'kind': 'preparation_targets_retired_after_disposition', 'action_id': action['id'], 'targets': [self.identifier]}])
        self.engine._save()


class QueuePlanTransitions(unittest.TestCase):
    def setUp(self):
        self.sim = prepared_sim()
        self.engine = self.sim.engine
        _ended_execution(self.engine, 'EX-queue-plan', 'research_plan')

    def apply(self, rows):
        self.sim.runtime['executions']['EX-queue-plan']['extensions'] = {'queued_requests': rows}
        self.engine._apply_queue_plan('EX-queue-plan')

    def test_missing_request_is_not_applied_and_retains_reason(self):
        row = {'request_id': 'AC-absent', 'decision': 'cancel', 'reason': '옛 스냅숏의 요청'}
        queue = deepcopy(self.sim.runtime['queue'])
        history = deepcopy(self.sim.runtime['history'])
        self.apply([row])
        self.assertEqual(self.sim.runtime['queue'], queue)
        self.assertEqual(self.sim.runtime['history'], [*history, {
            'kind': 'queue_plan_not_applied', 'execution_id': 'EX-queue-plan', **row}])
        self.engine._save()

    def test_live_request_is_not_cancelled(self):
        action = select(self.sim)
        self.engine._register_execution(action, {'id': 'EX-live', 'role': 'research_work', 'status': 'running'})
        row = {'request_id': action['id'], 'decision': 'cancel', 'reason': '실행 전 입력에만 있던 요청'}
        queue = deepcopy(self.sim.runtime['queue'])
        task = deepcopy(only_task(self.sim))
        history = deepcopy(self.sim.runtime['history'])
        self.apply([row])
        self.assertEqual(self.sim.runtime['queue'], queue)
        self.assertEqual(only_task(self.sim), task)
        self.assertEqual(self.sim.runtime['history'], [*history, {
            'kind': 'queue_plan_not_applied', 'execution_id': 'EX-queue-plan', **row}])
        self.engine._save()

    def test_cancel_nonwork_request_does_not_change_task(self):
        action = enqueue(self.engine, 'task_contract_review', only_task(self.sim)['id'])
        task = deepcopy(only_task(self.sim))
        row = {'request_id': action['id'], 'decision': 'cancel', 'reason': '중복 검토 취소'}
        self.apply([row])
        self.assertEqual(self.sim.runtime['queue'], [])
        self.assertEqual(only_task(self.sim), task)
        self.assertEqual(self.sim.runtime['history'][-1], {
            'kind': 'queue_plan_applied', 'execution_id': 'EX-queue-plan', **row})
        self.engine._save()

    def test_cancel_selected_work_restores_planned_status(self):
        action = select(self.sim)
        row = {'request_id': action['id'], 'decision': 'cancel', 'reason': '새 비교 계획을 기다린다.'}
        self.apply([row])
        self.assertEqual(self.sim.runtime['queue'], [])
        self.assertEqual(only_task(self.sim)['status'], 'planned')
        self.assertEqual(only_task(self.sim)['deferred_reason'], row['reason'])
        self.engine._save()
        self.sim.restart()
        self.assertEqual(only_task(self.sim)['status'], 'planned')

    def test_keep_reorders_only_named_positions_and_preserves_unseen_requests(self):
        first = enqueue(self.engine, 'task_contract_review', only_task(self.sim)['id'])
        middle = enqueue(self.engine, 'research_plan')
        last = enqueue(self.engine, 'research_preparation')
        rows = [{'request_id': action['id'], 'decision': 'keep', 'reason': '정한 순서를 보존한다.'}
                for action in (last, first)]
        expected = deepcopy([last, middle, first])
        self.apply(rows)
        self.assertEqual(self.sim.runtime['queue'], expected)
        self.engine._save()
        self.sim.restart()
        self.assertEqual(self.sim.runtime['queue'], expected)


class AcademicPreparationPrefixTests(unittest.TestCase):
    def test_rejected_unrated_contract_preserves_rules_without_inventing_an_old_rating(self):
        """T3 observation: 64.5 s; the existing academic producer supplies an unrated contract."""
        from support.academic_scenes import assessment_sim
        from support.role_answers import review_items
        sim = assessment_sim()
        task = next(iter(sim.runtime['tasks'].values()))
        self.assertNotIn('model_assessment', task)
        previous_rules = deepcopy(task.get('initial_observation_rules', []))
        _ended_execution(sim.engine, 'EX-unrated-review', 'task_contract_review')
        sim.engine._apply({'role': 'task_contract_review', 'target': task['id']},
            review_items([task['id']], decision='revision_required', findings=['Supply the missing rating.'],
                         revision_fields=['model_assessment', 'initial_observation_rules']),
            'EX-unrated-review', owns_response=False)
        task = sim.runtime['tasks'][task['id']]
        sim.engine._ensure_model_assessments()
        task = sim.runtime['tasks'][task['id']]
        self.assertNotIn('model_assessment_history', task)
        self.assertEqual(task['observation_rule_history'][-1]['rules'], previous_rules)
        self.assertEqual(task['observation_rule_history'][-1]['contract_review_execution'], 'EX-unrated-review')
        before = deepcopy(task['observation_rule_history'])
        sim.engine._ensure_model_assessments()
        self.assertEqual(task['observation_rule_history'], before)
        sim.engine._save()

    def test_generated_academic_contract_is_rated_before_rejection_and_consumed_once(self):
        import ast
        import inspect
        import textwrap
        """실제 준비·독립 검토 두 호출을 포함하여 2초 예산을 넘을 수 있다."""
        from support.academic_scenes import consumer_sim
        from support.engine_purpose import PurposeResponder
        from support.model import Answer
        from support.role_answers import contract_review
        from support.planning_paths import ExecutedLines
        from do_math.engine import ResearchEngine
        source, first_line = inspect.getsourcelines(ResearchEngine._ensure_model_assessments)
        nodes = list(ast.walk(ast.parse(textwrap.dedent(''.join(source)))))
        guard = next(node for node in nodes if isinstance(node, ast.If) and
            any(isinstance(value, ast.Constant) and value.value == 'model_assessment' for value in ast.walk(node.test)))
        following = next(node for node in nodes if isinstance(node, ast.Expr) and
            any(isinstance(value, ast.Constant) and value.value == 'observation_rule_history' for value in ast.walk(node)))
        sim = consumer_sim()
        sim.model.responder = PurposeResponder()
        observed = []

        def reject(output, context):
            task = context['task']
            self.assertTrue(task['model_assessment'])
            self.assertTrue(task['initial_observation_rules'])
            observed.append(deepcopy(task))
            return {**output, **contract_review(context, decision='revision_required',
                findings=['평가 근거를 보완한다.'],
                revision_fields=['model_assessment', 'initial_observation_rules'])}

        sim.model.on('task_contract_review').reply(Answer(reject))
        with ExecutedLines(sim.engine._ensure_model_assessments) as reached:
            sim.run_until(lambda scene: any(t.get('model_assessment_history')
                for t in scene.runtime['tasks'].values()), max_steps=12)
        self.assertEqual(len(observed), 1)
        task = sim.runtime['tasks'][observed[0]['id']]
        self.assertNotIn('waiting', task)
        from support.wait_reporting import assert_status_report
        report, human = assert_status_report(self, sim.engine)
        row = next(row for row in report['tasks'] if row['id'] == task['id'])
        pending = [a for a in sim.runtime['queue'] if task['id'] in a.get('assessment_targets', {})
            or task['id'] in a.get('observation_rule_targets', {})]
        self.assertEqual(len(pending), 1)
        self.assertEqual(row['next_owner'], 'research_preparation')
        self.assertIn(pending[0]['id'], row['selected_actions'])
        self.assertIn('next=research_preparation', next(line for line in human.splitlines()
            if line.startswith('  ' + task['id'] + ' revision=')))
        self.assertEqual(task['model_assessment_history'][-1]['assessment'], observed[0]['model_assessment'])
        self.assertEqual(task['observation_rule_history'][-1]['rules'], observed[0]['initial_observation_rules'])
        self.assertTrue(reached.crossed(first_line + guard.lineno - 1,
            first_line + guard.body[0].lineno - 1), reached.lines)
        self.assertFalse(reached.crossed(first_line + guard.lineno - 1,
            first_line + following.lineno - 1), reached.lines)
        executions = [e for e in sim.runtime['executions'].values()
                      if e['role'] in {'research_preparation', 'task_contract_review'}]
        self.assertTrue(executions)
        self.assertTrue(all(e['status'] == 'ended' and e['outcome'] == 'output_accepted' for e in executions))
        before = deepcopy((task['model_assessment_history'], task['observation_rule_history']))
        sim.engine._ensure_model_assessments()
        sim.engine._ensure_model_assessments()
        self.assertEqual((task['model_assessment_history'], task['observation_rule_history']), before)
        sim.engine._save()
        sim.restart()
        self.assertEqual((sim.runtime['tasks'][task['id']]['model_assessment_history'],
                          sim.runtime['tasks'][task['id']]['observation_rule_history']), before)

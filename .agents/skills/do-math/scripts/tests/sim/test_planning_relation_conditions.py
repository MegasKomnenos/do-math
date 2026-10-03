"""저장된 실제 관계의 간선·조건·평가 근거를 한 입력 상태에서 대조한다."""
from copy import deepcopy
import unittest

from do_math import planning, relation_refs, task_scope, revisions
from do_math.canonical import exact_content_hash
from support.planning_contract_inputs import relation_sim, warm_relation, only_task, fulfilled

setUpModule = warm_relation


class RelationConditionTests(unittest.TestCase):
    def setUp(self):
        self.sim = relation_sim()
        self.relation = self.sim.instance['relations'][-1]
        self.condition = {'op': 'relation_exists', 'subkind': self.relation['kind'],
                          'from_id': self.relation['source'], 'to_id': self.relation['target']}

    def evaluate(self):
        return planning.evaluate_condition(self.condition, self.sim.instance, self.sim.runtime)

    def test_all_three_relation_functions_report_exact_authored_edges(self):
        row = self.relation
        before = deepcopy(row)
        evidence = {*row['evidence_refs'], *row['formal_result_refs'], *row['assessment_refs']}
        endpoints = {row['source'], row['target']}
        self.assertEqual(relation_refs.relation_evidence_references(row), evidence)
        self.assertEqual(relation_refs.relation_endpoints(row), endpoints)
        self.assertEqual(relation_refs.relation_references(row), evidence | endpoints)
        self.assertEqual(row, before)

    def test_prose_and_history_never_become_current_edges(self):
        expected = relation_refs.relation_references(self.relation)
        row = {**deepcopy(self.relation), 'history': [{'source': 'KN-old', 'evidence_refs': ['SO-old']}],
               'evidence': 'KN-prose', 'origin_refs': ['SO-origin']}
        self.assertEqual(relation_refs.relation_references(row), expected)

    def test_nonlist_evidence_and_nonstring_endpoints_are_ignored(self):
        for key in ('evidence_refs', 'formal_result_refs', 'assessment_refs'):
            with self.subTest(key=key):
                row = deepcopy(self.relation)
                row[key] = {'id': 'SO-nested'}
                expected = {ref for name in ('evidence_refs', 'formal_result_refs', 'assessment_refs')
                            if name != key for ref in self.relation[name]}
                self.assertEqual(relation_refs.relation_evidence_references(row), expected)
        row = {**deepcopy(self.relation), 'source': {'id': 'KN-nested'}}
        self.assertEqual(relation_refs.relation_endpoints(row), {self.relation['target']})

    def test_valid_relation_basis_contains_exact_relation_and_each_existing_edge(self):
        records = planning.record_index(self.sim.instance, self.sim.runtime)
        expected = [{'id': self.relation['id'], 'sha256': exact_content_hash(self.relation), 'status': 'active'}]
        for ref in sorted(relation_refs.relation_references(self.relation)):
            record = records[ref][1]
            expected.append({'id': record['id'], 'sha256': exact_content_hash(record),
                             'status': record.get('status', record.get('lifecycle'))})
        before = deepcopy((self.sim.instance, self.sim.runtime))
        self.assertEqual(self.evaluate(), {'state': 'ready', 'basis': expected, 'errors': []})
        self.assertEqual((self.sim.instance, self.sim.runtime), before)

    def test_suspended_relation_produces_absence_instead_of_ready(self):
        self.assertEqual(self.evaluate()['state'], 'ready')
        self.relation['status'] = 'suspended'
        before = deepcopy((self.sim.instance, self.sim.runtime))
        self.assertEqual(self.evaluate(), {'state': 'not_ready', 'basis': [
            {'id': self.relation['id'], 'sha256': exact_content_hash(self.relation), 'status': 'suspended'},
            {'absencequery': dict(self.condition)}], 'errors': []})
        self.assertEqual((self.sim.instance, self.sim.runtime), before)

    def test_missing_endpoint_has_structural_error_not_false_ready(self):
        self.assertEqual(self.evaluate()['state'], 'ready')
        kid = self.relation['source']
        del self.sim.instance['knowledge'][kid]
        before = deepcopy((self.sim.instance, self.sim.runtime))
        result = self.evaluate()
        self.assertEqual(result['state'], 'evaluation_error')
        self.assertEqual(result['errors'], ['invalid relation: missing_source:' + kid + ', missing_target:' + kid])
        self.assertEqual(result['basis'], [{'id': self.relation['id'],
            'sha256': exact_content_hash(self.relation), 'status': 'active'}])
        self.assertEqual((self.sim.instance, self.sim.runtime), before)

    def test_absent_relation_is_a_precise_absence_query(self):
        self.condition['to_id'] = 'KN-absent'
        self.assertEqual(self.evaluate(), {'state': 'not_ready', 'basis': [{'absencequery': self.condition}], 'errors': []})

    def test_file_evidence_locator_is_not_invented_as_a_record_basis(self):
        from do_math.knowledge_io import import_relation
        path = self.sim.root / 'planning-evidence.txt'
        path.write_text('관계의 연구 근거', encoding='utf-8')
        row = {key: deepcopy(self.relation[key]) for key in (
            'id', 'kind', 'source', 'target', 'evidence', 'formal_result_refs', 'assessment_refs')}
        row['evidence_refs'] = [str(path)]
        self.sim.engine.instance, rid = import_relation(self.sim.instance, row,
            source_ref=self.sim.instance_id, actor_ref=self.sim.instance_id, clock=self.sim.ports.clock)
        self.sim.engine._save()
        self.relation = next(r for r in self.sim.instance['relations'] if r['id'] == rid)
        result = self.evaluate()
        records = planning.record_index(self.sim.instance, self.sim.runtime)
        refs = [rid, *sorted({row['source'], row['target'], *row['formal_result_refs'], *row['assessment_refs']})]
        expected = []
        for ref in refs:
            record = records[ref][1]
            expected.append({'id': ref, 'sha256': exact_content_hash(record),
                             'status': record.get('status', record.get('lifecycle'))})
        self.assertEqual(result, {'state': 'ready', 'basis': expected, 'errors': []})
        self.assertEqual(path.read_text(encoding='utf-8'), '관계의 연구 근거')

    def test_assessment_basis_strictly_tracks_relation_judgment_evidence(self):
        task = only_task(self.sim)
        assessment = fulfilled(task)
        assessment['item_dispositions'][0]['evidence_refs'] = [self.relation['id']]
        basis = task_scope.assessment_basis(task, assessment, self.sim.instance, self.sim.runtime)
        fid = self.relation['formal_result_refs'][0]
        formal = self.sim.instance['formal_results'][fid]
        self.assertEqual(basis[fid], exact_content_hash(formal))
        self.assertEqual(basis[self.relation['id']], exact_content_hash(self.relation))
        formal['formal_use'] = 'suspended'
        changed = task_scope.assessment_basis(task, assessment, self.sim.instance, self.sim.runtime)
        self.assertEqual(changed[fid], exact_content_hash(formal))
        self.assertNotEqual(changed[fid], basis[fid])

    def test_proposal_lineage_missing_ancestor_and_cycle_are_explicit(self):
        import ast
        import inspect
        import textwrap
        kid = self.relation['source']
        from support.planning_paths import ExecutedLines
        source, first_line = inspect.getsourcelines(revisions.proposal_lineage)
        nodes = list(ast.walk(ast.parse(textwrap.dedent(''.join(source)))))
        loop = next(node for node in nodes if isinstance(node, ast.While))
        returned = next(node for node in nodes if isinstance(node, ast.Return)
                        and isinstance(node.value, ast.Tuple))
        with ExecutedLines(revisions.proposal_lineage) as reached:
            self.assertEqual(revisions.proposal_lineage(self.sim.instance, kid), (kid, 1))
        self.assertIn(first_line + returned.lineno - 1, reached.lines)
        self.assertEqual(reached.lines.count(first_line + loop.lineno - 1), 1)
        self.sim.instance['knowledge'][kid]['supersedes'] = kid
        before = deepcopy(self.sim.instance)
        with self.assertRaisesRegex(ValueError, '^cyclic proposal revision lineage$'):
            revisions.proposal_lineage(self.sim.instance, kid)
        self.assertEqual(self.sim.instance, before)
        self.sim.instance['knowledge'][kid]['supersedes'] = 'KN-absent'
        before = deepcopy(self.sim.instance)
        with self.assertRaisesRegex(ValueError, '^missing proposal revision ancestor$'):
            revisions.proposal_lineage(self.sim.instance, kid)
        self.assertEqual(self.sim.instance, before)

    def test_other_tasks_formal_result_cannot_replace_designated_judgment(self):
        from support.planning_contract_inputs import returned
        assessment = returned(self.sim)
        task = only_task(self.sim)
        fid = self.relation['formal_result_refs'][0]
        assessment['item_dispositions'][0]['evidence_refs'] = [fid]
        task_scope.apply_task_assessments(self.sim.instance, self.sim.runtime, [assessment],
            execution_id='EX-planning-plan', input_tasks=deepcopy(self.sim.runtime['tasks']), clock=self.sim.ports.clock)
        task['completion_obligations'][0]['judges'] = ['formal_check']
        before = deepcopy((self.sim.instance, self.sim.runtime))
        with self.assertRaisesRegex(ValueError, '^fulfilled obligation needs its designated judge or a current specialist judgment for this task$'):
            task_scope.apply_task_assessments(self.sim.instance, self.sim.runtime, [assessment],
                execution_id='EX-planning-plan', input_tasks=deepcopy(self.sim.runtime['tasks']), clock=self.sim.ports.clock)
        self.assertEqual((self.sim.instance, self.sim.runtime), before)


class DelegatedRevisionTests(unittest.TestCase):
    def setUp(self):
        from support.planning_contract_inputs import delegated_revision
        self.sim = relation_sim()
        self.engine = self.sim.engine
        self.parent, self.tid, self.kid = delegated_revision(self.sim)


    def test_live_delegate_is_not_detached_or_replanned(self):
        before = deepcopy((self.sim.instance, self.sim.runtime))
        self.engine._reconcile_revision_delegations()
        self.assertEqual((self.sim.instance, self.sim.runtime), before)
        self.assertEqual(self.sim.runtime['waiting_actions'][self.parent]['delegated_targets'], {self.kid: self.tid})

    def test_different_preparer_does_not_steal_already_delegated_target(self):
        from support.planning_owner import enqueue
        action = enqueue(self.engine, 'research_preparation', revision_targets=revisions.capture_targets(
            self.sim.instance, self.sim.runtime, [self.kid]))
        self.assertNotIn('revision_parent_ids', action)
        self.assertNotIn('obligation_refs', action['revision_targets'][self.kid])
        self.assertEqual(self.sim.runtime['waiting_actions'][self.parent]['delegated_targets'], {self.kid: self.tid})
        self.engine._save()

    def test_actual_delegate_candidates_and_conditions_satisfy_revision_coverage(self):
        from support.role_answers import candidate
        task = self.sim.runtime['tasks'][self.tid]
        wire = candidate(task['title'])
        wire.update({key: deepcopy(task[key]) for key in wire if key in task})
        extension = deepcopy(self.sim.runtime['executions'][task['producer_execution']]['extensions'])
        context = {'action': deepcopy(self.sim.runtime['waiting_actions'][self.parent]['action']),
                   'tasks': list(self.sim.runtime['tasks'].values()),
                   'knowledge_catalog': list(self.sim.instance['knowledge'].values())}
        output = {'candidates': [wire]}
        before = deepcopy((output, extension, context))
        self.assertEqual(revisions.submission_errors(output, extension, context), [])
        self.assertEqual((output, extension, context), before)

    def test_wrong_delegation_title_is_rejected_without_changing_state(self):
        from support.engine_lifecycle import _ended_execution
        action = deepcopy(self.sim.runtime['waiting_actions'][self.parent]['action'])
        _ended_execution(self.engine, 'EX-wrong-delegate', 'research_preparation')
        self.sim.runtime['executions']['EX-wrong-delegate']['extensions'] = {'revision_resolutions': [{
            'record_id': self.kid, 'disposition': 'delegated', 'task_title': '존재하지 않는 과제', 'reason': '잘못된 위임'}]}
        before = deepcopy((self.sim.instance, self.sim.runtime))
        with self.assertRaisesRegex(ValueError, '^delegated revision does not identify its prepared knowledge-revision task$'):
            self.engine._apply_revision_followup(action, {}, 'EX-wrong-delegate')
        self.assertEqual((self.sim.instance, self.sim.runtime), before)


    def test_closed_instance_detaches_ended_delegate_without_new_work(self):
        from support.engine_lifecycle import applied
        from support.planning_contract_inputs import withdraw
        withdraw(self.sim, self.tid)
        applied(self.sim, 'close')
        before = deepcopy(self.sim.runtime['queue'])
        self.engine._reconcile_revision_delegations()
        self.assertEqual(self.sim.runtime['waiting_actions'][self.parent]['delegated_targets'], {})
        self.assertEqual(self.sim.runtime['waiting_actions'][self.parent]['delegation_history'], [
            {'record_id': self.kid, 'task_id': self.tid}])
        self.assertEqual(self.sim.runtime['queue'], before)
        self.assertEqual(self.sim.runtime['status'], 'closed')
        self.engine._save()

    def test_optional_delegated_work_preserves_required_parent_after_unchanged(self):
        from support.engine_lifecycle import _ended_execution
        from support.planning_owner import enqueue
        from support.planning_paths import ExecutedLines
        action = enqueue(self.engine, 'research_work', self.tid)
        parent = deepcopy(self.sim.runtime['waiting_actions'][self.parent])
        self.assertIs(parent['action']['revision_targets'][self.kid]['required'], True)
        self.assertIs(action['revision_targets'][self.kid]['required'], False)
        extension = {'revision_resolutions': [{'record_id': self.kid,
            'disposition': 'unchanged', 'reason': '작업은 변경하지 않았고 부모 개정 의무는 남는다.'}]}
        output = {'outcome': 'waiting'}
        self.assertEqual(revisions.submission_errors(output, extension, {'action': action,
            'tasks': list(self.sim.runtime['tasks'].values()),
            'knowledge_catalog': list(self.sim.instance['knowledge'].values())}), [])
        _ended_execution(self.engine, 'EX-unchanged-work', 'research_work')
        self.sim.runtime['executions']['EX-unchanged-work']['extensions'] = extension
        with ExecutedLines(self.engine._apply_revision_followup) as reached:
            self.engine._apply_revision_followup(action, output, 'EX-unchanged-work')
        import ast
        import inspect
        import textwrap
        source, start = inspect.getsourcelines(self.engine._apply_revision_followup)
        function = ast.parse(textwrap.dedent(''.join(source))).body[0]
        parents = {child: node for node in ast.walk(function) for child in ast.iter_child_nodes(node)}
        guards = [node for node in ast.walk(function) if isinstance(node, ast.If)
                  and ast.unparse(node.test) == "disposition == 'deferred'"]
        self.assertEqual(len(guards), 1)
        guard = guards[0]
        loop = parents[guard]
        while not isinstance(loop, ast.For):
            loop = parents[loop]
        self.assertEqual((ast.unparse(loop.target), ast.unparse(loop.iter)), ('identifier', 'declared'))
        self.assertTrue(reached.crossed(start + guard.lineno - 1, start + loop.lineno - 1), reached.lines)
        self.assertEqual(self.sim.runtime['waiting_actions'], {self.parent: parent})
        self.engine._remove_action(action)
        self.engine._save()
        self.sim.restart()
        self.assertEqual(self.sim.runtime['waiting_actions'], {self.parent: parent})

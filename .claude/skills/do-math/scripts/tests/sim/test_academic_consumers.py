"""The academic producer and its TASKS consumers on the real engine (``academic_engine``, layer 2), moved from
``test_academic``'s ``AcademicConsumerTests`` (and the engine side of its solution-basis test).

The legacy tests built an engine without its constructor (``bare_engine``),
replaced its solution basis, academic evidence reader and lifecycle clock with
autospecs, and for the plan dispatch replaced the store and the evaluation
context. Here the engine is a restored Sim's (``support.academic_scenes.consumer_sim``):
the goal auditors solved the goal on a reviewed theorem, so ``_solution_basis``
is the product's, the evidence reader reads the real store, time comes from the
clock port, and a plan's input snapshot is a published head with the issued
input archived below its bundle (``support.engine_context.issue``). The
executions a record names are registered as the engine registers them
(``support.academic_scenes.ended``).
"""
from copy import deepcopy
import unittest

from do_math import governance as gov
from do_math import planning, task_contracts
from do_math.planning import contract_hash
from do_math.task_scope import apply_task_assessments
from support.state_builders import charter_change
from support.role_answers import disposition, review_items
from support.observation_inputs import prepared_rule_conditions
from support.academic_scenes import MANUSCRIPT, consumer_sim, ended, user_source, warm_consumer
from support.engine_context import issue, package, assert_governance_documents
from support.engine_lifecycle import research_grant

setUpModule = warm_consumer
REJECTED_TEXT = '^academic result requires the current applied independent TASKS assessment$'
STALE_SCOPE = '^scope approval must bind the exact task contract edition$'


class AcademicConsumerTests(unittest.TestCase):
    """Actual academic producer and TASKS consumers; the mathematical evidence is a reviewed fixture theorem."""

    def generated(self):
        """The engine and the one task the academic follow-up generated when the goal was solved."""
        self.sim = consumer_sim()
        engine = self.sim.engine
        task, = [row for row in engine.runtime['tasks'].values() if row.get('academic_requirement_id') == 'AR']
        return engine, task

    def reviewed(self):
        """The generated task after its assigned rule preparation returned and a sealed contract review."""
        engine, task = self.generated()
        action = next(a for a in engine.runtime['queue'] if a.get('observation_rule_targets'))
        ended(engine, 'EX-prep', 'research_preparation')
        engine.runtime['executions']['EX-prep'].update(
            action=action, extensions={'task_conditions': prepared_rule_conditions([task['id']])})
        engine._finish_assessment_preparation(action, 'EX-prep')
        engine._remove_action(action)
        ended(engine, 'EX-review', 'task_contract_review', target=task['id'])
        output = review_items([task['id']], next_owner='research_preparation')
        task['reviews'].append(planning.seal_contract_review(task, output, engine.instance, engine.runtime,
                                                             execution_id='EX-review'))
        return engine, task

    def returned_work(self, engine, task, report='Synthetic returned manuscript'):
        """The task's returned work EX-work and the planner EX-plan that read the current solution basis."""
        task['results'] = [{'execution_id': 'EX-work', 'report': report}]
        ended(engine, 'EX-work', 'research_work', target=task['id'])
        ended(engine, 'EX-plan', 'research_plan', input_solution_basis=deepcopy(engine._solution_basis()))

    def assessed(self, *, kind='fulfilled', decision='completed'):
        from support.entry import entry
        _entry = entry()
        engine, task = self.reviewed()
        tid = task['id']
        self.returned_work(engine, task)
        assessment = {'task_id': tid, 'decision': decision, 'reason': 'Synthetic assessment of the returned manuscript',
                      'item_dispositions': [{'obligation_id': o['id'], 'kind': kind, 'evidence_refs': ['EX-work']}
                                            for o in task['completion_obligations']], 'unresolved': []}
        engine.instance, engine.runtime = apply_task_assessments(engine.instance, engine.runtime, [assessment],
            execution_id='EX-plan', input_tasks=deepcopy(engine.runtime['tasks']), clock=_entry.ports.clock)
        return engine, engine.runtime['tasks'][tid], assessment

    def test_actual_constructor_review_and_ready_population_use_the_task_contract(self):
        engine, task = self.reviewed()
        task_contracts.validate_task_contract(task)
        self.assertEqual([o['claim'] for o in task['completion_obligations']], MANUSCRIPT['criteria'])
        self.assertEqual(task['profile_refs'], engine.instance['role_profile_refs']['research_work'])
        self.assertEqual(task['authority_refs'], [research_grant(engine)])
        self.assertTrue({row['id'] for row in engine._solution_basis()['records']}.issubset(task['inputs']))
        self.assertNotIn('completion_criteria', task)
        self.assertEqual(planning.task_ready(task, engine.instance, engine.runtime, evaluation_context=engine._evaluation_context())['state'], 'ready')
        self.assertEqual(planning.ready_task_ids(engine.runtime, engine.instance, evaluation_context=engine._evaluation_context()), [task['id']])
        engine._ensure_academic_followup()
        self.assertEqual(list(engine.runtime['tasks']), [task['id']])

    def test_actual_assessment_consumer_uses_item_dispositions_and_current_evidence(self):
        engine, task, assessment = self.assessed()
        engine._record_academic_assessment(task, assessment, 'EX-plan')
        value = engine._academic_status()
        assert_governance_documents(self, value, owner='academic_validation',
            status='completed', reason='all current requirements satisfied')
        for role in ('research_plan', 'goal_audit'):
            root = self.sim.root / ('document-' + role)
            fitted, fixed = package(engine, root, role=role)
            self.assertEqual(fitted['context']['academic_validation'], value)
            assert_governance_documents(self, fitted['context']['academic_validation'],
                owner='academic_validation', status='completed', reason='all current requirements satisfied')
            assert_governance_documents(self, fitted['context']['governance'],
                owner='governance', instance=engine.instance)
            self.assertEqual(fixed['governance'], fitted['context']['governance'])
            damaged = deepcopy(fitted['context']['academic_validation'])
            damaged['status'] = 'pending'
            with self.assertRaises(AssertionError):
                assert_governance_documents(self, damaged, owner='academic_validation',
                    status='completed', reason='all current requirements satisfied')
        engine._record_academic_assessment(task, assessment, 'EX-plan')
        self.assertEqual(len(engine.runtime['academic_assessments']), 1)
        engine.runtime['executions']['EX-work']['changed_evidence'] = True
        assert_governance_documents(self, engine._academic_status(), owner='academic_validation',
                                   status='active', reason='requirements remain')
        with self.assertRaisesRegex(ValueError, REJECTED_TEXT):
            engine._record_academic_assessment(task, assessment, 'EX-plan')

    def test_open_disposition_keeps_followup_in_same_task_contract(self):
        engine, task, assessment = self.assessed(kind='open', decision='incomplete')
        engine._record_academic_assessment(task, assessment, 'EX-plan')
        self.assertEqual(task['status'], 'waiting')
        self.assertEqual(engine.runtime['academic_assessments'][0]['decision'], 'not_satisfied')
        engine._ensure_academic_followup()
        self.assertEqual(list(engine.runtime['tasks']), [task['id']])

    def test_engine_plan_dispatch_consumes_generated_contract_and_applied_assessment(self):
        engine, task = self.reviewed()
        tid = task['id']
        engine._save()
        before_work = engine.head
        select = ended(engine, 'EX-select', 'research_plan', input_snapshot=before_work)
        issue(engine, select, {'snapshot': before_work, 'tasks': list(engine.runtime['tasks'].values()),
                               'ready_task_ids': [tid]}, 'BA-select')
        engine._apply_plan({'dispositions': [{**disposition(tid), 'reason': 'Current academic work',
                                              'expected_research_change': 'Complete the manuscript'}],
                            'task_assessments': [], 'goal_audit': False}, 'EX-select')
        task = engine.runtime['tasks'][tid]
        self.assertEqual(task['status'], 'active')
        self.assertTrue(any(a['role'] == 'research_work' and a.get('target') == tid for a in engine.runtime['queue']))
        self.returned_work(engine, task, 'Synthetic manuscript')
        engine._save()
        after_work = engine.head
        plan = engine.runtime['executions']['EX-plan']
        plan['input_snapshot'] = after_work
        issue(engine, plan, {'snapshot': after_work, 'tasks': list(engine.runtime['tasks'].values()),
                             'ready_task_ids': []}, 'BA-returned')
        assessment = {'task_id': tid, 'decision': 'completed', 'reason': 'Synthetic assessment of the returned manuscript',
                      'item_dispositions': [{'obligation_id': o['id'], 'kind': 'fulfilled', 'evidence_refs': ['EX-work']}
                                            for o in task['completion_obligations']], 'unresolved': []}
        engine._apply_plan({'dispositions': [], 'task_assessments': [assessment], 'goal_audit': False}, 'EX-plan')
        self.assertEqual(engine.runtime['tasks'][tid]['status'], 'completed')
        self.assertEqual(engine._academic_status()['status'], 'completed')
        self.assertEqual(engine.runtime['status'], 'completed')

    def test_unapplied_or_different_assessment_cannot_certify_academic_success(self):
        engine, task, assessment = self.assessed()
        forged = deepcopy(assessment)
        forged['item_dispositions'][0]['evidence_refs'] = ['not-in-input']
        with self.assertRaisesRegex(ValueError, REJECTED_TEXT):
            engine._record_academic_assessment(task, forged, 'EX-plan')
        task.pop('assessment')
        with self.assertRaisesRegex(ValueError, REJECTED_TEXT):
            engine._record_academic_assessment(task, assessment, 'EX-plan')
        self.assertNotIn('academic_assessments', engine.runtime)

    def test_scope_waiver_records_authority_without_applying_a_second_task_lifecycle(self):
        from support.entry import entry
        _entry = entry()
        engine, task = self.generated()
        tid = task['id']
        task['results'] = [{'execution_id': 'EX-work', 'report': 'Cannot satisfy the requirement'}]
        ended(engine, 'EX-work', 'research_work', target=tid)
        change = {'kind': 'task_scope', 'decision_id': 'WAIVER', 'task_id': tid, 'disposition': 'waive',
                  'revision': task['revision'], 'contract_sha256': contract_hash(task),
                  'obligation_ids': [row['id'] for row in task['completion_obligations']],
                  'reason': 'Synthetic explicit waiver'}
        before = deepcopy(task)
        engine.instance, engine.runtime, decision = gov.apply_decision(engine.instance, engine.runtime, change,
                                                                       source_ref=user_source(engine),
                                                                       clock=engine.ports.clock)
        self.assertEqual(engine.runtime['tasks'][tid], before)
        ended(engine, 'EX-plan', 'research_plan', input_solution_basis=deepcopy(engine._solution_basis()))
        assessment = {'task_id': tid, 'decision': 'closed', 'reason': 'Synthetic waiver of every obligation',
                      'item_dispositions': [{'obligation_id': row['id'], 'kind': 'waived', 'authority_ref': decision['id'],
                                             'evidence_refs': ['EX-work']} for row in task['completion_obligations']],
                      'unresolved': []}
        engine.instance, engine.runtime = apply_task_assessments(engine.instance, engine.runtime, [assessment],
            execution_id='EX-plan', input_tasks=deepcopy(engine.runtime['tasks']), clock=_entry.ports.clock)
        engine._record_academic_assessment(engine.runtime['tasks'][tid], assessment, 'EX-plan')
        self.assertNotEqual(engine._academic_status()['status'], 'completed')
        self.assertEqual([row['decision'] for row in engine.runtime['academic_assessments']], ['not_satisfied'])

    def test_task_scope_transfer_decision_changes_no_task_and_requires_the_current_contract(self):
        engine, task = self.generated()
        engine.runtime['tasks']['RECIPIENT'] = {**deepcopy(task), 'id': 'RECIPIENT'}
        change = {'kind': 'task_scope', 'task_id': task['id'], 'disposition': 'transfer',
                  'target_task_id': 'RECIPIENT', 'revision': task['revision'], 'contract_sha256': contract_hash(task),
                  'obligation_ids': [task['completion_obligations'][0]['id']], 'reason': 'Transfer only the first obligation'}
        source = user_source(engine)
        _, runtime, _ = gov.apply_decision(engine.instance, engine.runtime, change, source_ref=source,
                                           clock=engine.ports.clock)
        self.assertEqual(runtime['tasks'], engine.runtime['tasks'])
        change['contract_sha256'] = 'stale'
        with self.assertRaisesRegex(ValueError, STALE_SCOPE):
            gov.apply_decision(engine.instance, engine.runtime, change, source_ref=source, clock=engine.ports.clock)

    def test_academic_only_charter_change_preserves_math_fact_and_replaces_requirement_task(self):
        engine, task = self.generated()
        source = user_source(engine)
        revised = charter_change(engine, academic_requirements=[{**MANUSCRIPT, 'criteria': ['Revised manuscript']}])
        engine.instance, engine.runtime, _ = gov.apply_decision(engine.instance, engine.runtime, revised,
                                                                source_ref=source, clock=engine.ports.clock)
        self.assertEqual(engine.instance['goal_status'], 'mathematically_solved')
        engine._ensure_academic_followup()
        self.assertEqual(engine.runtime['tasks'][task['id']]['status'], 'closed')
        current = [t for t in engine.runtime['tasks'].values() if t['status'] != 'closed']
        self.assertEqual(len(current), 1)
        self.assertEqual(current[0]['completion_obligations'][0]['claim'], 'Revised manuscript')
        changed = charter_change(engine, goal='Prove Q')
        engine.instance, engine.runtime, _ = gov.apply_decision(engine.instance, engine.runtime, changed,
                                                                source_ref=source, clock=engine.ports.clock)
        self.assertEqual(engine.instance['goal_status'], 'unsolved')


class SolutionBasisTests(unittest.TestCase):
    def test_academic_basis_rejects_a_stale_judgment_dependency(self):
        """A goal judgment's dependency whose record changed after the judgment leaves no current solution basis."""
        engine = consumer_sim().engine
        self.assertIsNotNone(engine._solution_basis())
        kid, = {ref for judgment in engine.instance['goal_judgments'] for ref in judgment['dependencies']}
        engine.instance['knowledge'][kid]['summary'] = 'A summary written after the goal judgments'
        self.assertIsNone(engine._solution_basis())


if __name__ == '__main__':
    unittest.main()

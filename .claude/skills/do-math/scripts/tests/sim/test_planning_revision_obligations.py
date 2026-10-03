"""The engine's revision mixins keep revision ownership through delegation and retry
(``revision_engine``, ``core_engine._enqueue``, ``decision_engine._apply_task_plan``, ``planning``,
``revisions``; layer 2), moved from ``test_revision_obligations``.

The legacy harness built a ``ResearchEngine`` without its constructor over the
record fixtures' approved task and an in-memory store (``bare_engine``), and one
test replaced the engine's governance view. Here the engine is a restored Sim's
(``support.planning_owner.owner_sim``): the approved task ``TK-1`` reads a source
the public ``source`` control registered, and the knowledge record a revision
targets is a theorem the Lean double verified. The tests call the same mixin
methods; nothing of the engine or its store is replaced.
"""
from copy import deepcopy
import unittest

from do_math import planning, revisions
from support.engine_lifecycle import _ended_execution
from support.planning_owner import enqueue, owner_sim, theorem_id, warm_owner

setUpModule = warm_owner


class RevisionObligationTests(unittest.TestCase):
    def setUp(self):
        self.sim = owner_sim()
        self.engine = self.sim.engine

    def test_deferred_child_records_parent_deferral_without_new_child_wait(self):
        sim, engine, identifier = self.sim, self.engine, 'TK-1'
        parent = enqueue(engine, 'research_preparation', revision_targets=revisions.capture_targets(
            sim.instance, sim.runtime, [identifier], required=True))
        eid = sim.clock.new_id('EX')
        _ended_execution(engine, eid, 'research_preparation')
        engine.runtime['executions'][eid]['extensions'] = {'revision_resolutions': [
            {'record_id': identifier, 'disposition': 'deferred', 'reason': '추가 근거를 기다린다.'}]}
        issues = revisions.submission_errors({'candidates': []}, engine.runtime['executions'][eid]['extensions'], {
            'action': parent, 'tasks': list(engine.runtime['tasks'].values()),
            'knowledge_catalog': list(engine.instance['knowledge'].values())})
        self.assertEqual(issues, [])
        engine._apply_revision_followup(parent, {'summary': '개정 보류'}, eid)
        engine._remove_action(parent)
        engine._save()
        parent_id = parent['id']
        child = enqueue(engine, 'research_preparation', revision_targets=revisions.capture_targets(
            sim.instance, sim.runtime, [identifier]))
        _ended_execution(engine, 'EX-child', 'research_preparation')
        sim.runtime['executions']['EX-child']['extensions'] = {'revision_resolutions': [
            {'record_id': identifier, 'disposition': 'deferred', 'reason': '새 원천 필요'}]}
        previous = deepcopy(sim.runtime['waiting_actions'][parent_id])
        engine._apply_revision_followup(child, {'summary': '보류'}, 'EX-child')
        expected = {**previous, 'deferrals': {identifier: {'execution_id': 'EX-child', 'reason': '새 원천 필요'}}}
        self.assertEqual(sim.runtime['waiting_actions'], {parent_id: expected})
        engine._remove_action(child)
        engine._save()
        published = deepcopy(engine.store.load())
        sim.restart()
        self.assertEqual(sim.engine.store.load(), published)
        head, instance, runtime = published
        damaged = deepcopy(runtime)
        damaged['waiting_actions'][parent_id]['deferrals'][identifier]['execution_id'] = 'EX-missing'
        before = deepcopy(damaged)
        with self.assertRaisesRegex(ValueError, '^waiting action deferral execution does not resolve: EX-missing$'):
            sim.engine.store.save_with_state(head, instance, damaged)
        self.assertEqual(damaged, before)
        self.assertEqual(sim.engine.store.load(), published)
        damaged = deepcopy(runtime)
        deferred = damaged['waiting_actions'][parent_id]['deferrals'].pop(identifier)
        damaged['waiting_actions'][parent_id]['deferrals']['TK-missing'] = deferred
        before = deepcopy(damaged)
        with self.assertRaisesRegex(ValueError, '^waiting action deferral target does not resolve: TK-missing$'):
            sim.engine.store.save_with_state(head, instance, damaged)
        self.assertEqual(damaged, before)
        self.assertEqual(sim.engine.store.load(), published)

    def test_closed_target_does_not_erase_other_targets_or_merged_new_request(self):
        h = self.engine
        other = deepcopy(h.runtime['tasks']['TK-1'])
        other['id'] = 'TK-2'
        h.runtime['tasks']['TK-2'] = other
        a = enqueue(h, 'research_preparation', revision_targets=revisions.capture_targets(h.instance, h.runtime, ['TK-1', 'TK-2']))
        h.runtime['tasks']['TK-1']['status'] = 'closed'
        h._retire_closed_revision_targets()
        self.assertEqual(set(a['revision_targets']), {'TK-2'})
        a['unbound_request'] = True
        h.runtime['tasks']['TK-2']['status'] = 'closed'
        h._retire_closed_revision_targets()
        self.assertEqual(h.runtime['queue'], [a])
        self.assertEqual(a['revision_targets'], {})
        a['revision_targets'] = {'TK-2': {}}
        a['unbound_request'] = False
        h._retire_closed_revision_targets()
        self.assertEqual(h.runtime['queue'], [])

    def test_revision_blocks_consumer_but_independent_work_can_overlap(self):
        h = self.engine
        a = h.runtime['tasks']['TK-1']
        b = deepcopy(a)
        b.update(id='TK-B', inputs=['TK-1'], reviews=[])
        h.runtime['tasks']['TK-B'] = b
        c = deepcopy(a)
        c.update(id='TK-C', reviews=[])
        h.runtime['tasks']['TK-C'] = c
        writer = enqueue(h, 'research_preparation', 'TK-1')
        read = {'id': 'AC-B', 'role': 'research_work', 'target': 'TK-B'}
        independent = {'id': 'AC-C', 'role': 'research_work', 'target': 'TK-C'}
        self.assertTrue(planning.revision_waits(read, h.instance, h.runtime))
        self.assertEqual(planning.revision_waits(independent, h.instance, h.runtime), [])
        h.runtime['executions']['EX-reader'] = {'id': 'EX-reader', 'status': 'running', 'action': read}
        self.assertTrue(planning.revision_waits(writer, h.instance, h.runtime))
        h.runtime['executions']['EX-reader']['status'] = 'ended'
        self.assertEqual(planning.revision_waits(writer, h.instance, h.runtime), [])

    def delegated(self):
        """The preparation that declared the theorem a required revision target delegated it to TK-1."""
        h = self.engine
        kid = theorem_id(self.sim)
        parent = enqueue(h, 'research_preparation',
                         revision_targets=revisions.capture_targets(h.instance, h.runtime, [kid], required=True))
        task = h.runtime['tasks']['TK-1']
        task.update(title='Correct source', producer_execution='EX-prep', knowledge_revision_targets=[kid])
        _ended_execution(h, 'EX-prep', 'research_preparation')
        h.runtime['executions']['EX-prep']['extensions'] = {'revision_resolutions': [
            {'record_id': kid, 'disposition': 'delegated', 'task_title': 'Correct source', 'reason': 'research replacement'}]}
        h._apply_revision_followup(parent, {'summary': 'delegate research'}, 'EX-prep')
        h._remove_action(parent)
        return h, parent, kid

    def test_delegated_work_and_review_do_not_block_on_own_obligation(self):
        h, parent, kid = self.delegated()
        entry = h.runtime['waiting_actions'][parent['id']]
        self.assertEqual(entry['delegated_targets'], {kid: 'TK-1'})
        review = {'id': 'AC-review', 'role': 'task_contract_review', 'target': 'TK-1'}
        self.assertEqual(planning.revision_waits(review, h.instance, h.runtime), [])
        work = enqueue(h, 'research_work', 'TK-1')
        self.assertIn(kid, work['revision_targets'])
        self.assertEqual(planning.revision_waits(work, h.instance, h.runtime), [])
        _ended_execution(h, 'EX-work', 'research_work')
        h.runtime['executions']['EX-work']['extensions'] = {
            'knowledge_changes': [{'id': kid}],
            'revision_resolutions': [{'record_id': kid, 'disposition': 'revised', 'reason': 'authored correction'}]}
        # Synthetic, as in the legacy test: the product revises knowledge by a replacement record under a new ID
        # (knowledge.replace_knowledge), never in place; _apply_revision_followup does not read this value.
        h.instance['knowledge'][kid]['revision'] = 2
        h._apply_revision_followup(work, {'summary': 'correction', 'outcome': 'submitted'}, 'EX-work')
        self.assertNotIn(parent['id'], h.runtime['waiting_actions'])
        self.assertEqual(h.runtime['tasks']['TK-1']['status'], 'waiting')
        self.assertEqual(h.runtime['tasks']['TK-1']['waiting']['next_owner'], 'research_plan')

    def test_maintenance_can_read_pending_revisions_and_cycles(self):
        h, parent, kid = self.delegated()
        maintenance = {'role': 'maintenance', 'id': 'AC-check', 'target': kid}
        self.assertEqual(planning.revision_waits(maintenance, h.instance, h.runtime), [])
        self.assertEqual([(row['state'], set(row['action']['revision_targets'])) for row in planning.pending_revisions(h.runtime)],
                         [('waiting', {kid})])
        self.assertEqual(planning.revision_cycles(h.instance, h.runtime), [])

    def test_closed_delegate_keeps_obligation_for_new_preparer(self):
        h, parent, kid = self.delegated()
        h.runtime['tasks']['TK-1']['status'] = 'closed'
        h.runtime['queue'] = []
        h.runtime['waiting_actions']['failed-child'] = {'kind': 'execution_failure', 'action': {
            'id': 'failed-child', 'role': 'research_work', 'target': 'TK-1',
            'revision_targets': revisions.capture_targets(h.instance, h.runtime, [kid])}}
        h._retire_closed_revision_targets()
        h._reconcile_revision_delegations()
        self.assertNotIn('failed-child', h.runtime['waiting_actions'])
        entry = h.runtime['waiting_actions'][parent['id']]
        self.assertEqual(set(entry['action']['revision_targets']), {kid})
        self.assertFalse(entry['delegated_targets'])
        new = enqueue(h, 'research_preparation', revision_targets=revisions.capture_targets(h.instance, h.runtime, [kid]))
        self.assertIn(parent['id'], new['revision_parent_ids'])
        self.assertEqual(planning.revision_waits(new, h.instance, h.runtime), [])
        self.assertEqual(planning.revision_cycles(h.instance, h.runtime), [])

    def test_plan_selection_and_predispatch_use_actual_current_input(self):
        from support.record_builders import task_disposition
        from support.role_answers import contract_review
        h = self.engine
        _ended_execution(h, 'EX-plan', 'research_plan')
        plan = {'dispositions': [task_disposition('TK-1')], 'task_assessments': [], 'preparation_requests': []}
        h._apply_task_plan(plan, 'EX-plan', deepcopy(h.runtime['tasks']), ['TK-1'], evaluation_context=h._evaluation_context())
        action = next(a for a in h.runtime['queue'] if a['role'] == 'research_work')
        self.assertTrue(h._selected_action_current(action, evaluation_context=h._evaluation_context()))
        h.instance['sources'][0]['sha256'] = 'b' * 64
        self.assertFalse(h._selected_action_current(action, evaluation_context=h._evaluation_context()))
        self.assertFalse(any(a['role'] == 'research_work' for a in h.runtime['queue']))
        self.assertTrue(any(a['role'] == 'research_plan' for a in h.runtime['queue']))
        task = h.runtime['tasks']['TK-1']
        review_action = {'role': 'task_contract_review', 'target': task['id']}
        h._apply(review_action, contract_review({'task': task}), 'EX-fresh-review', owns_response=False)
        self.assertNotIn('waiting', task)
        self.assertEqual(planning.task_ready(task, h.instance, h.runtime, evaluation_context=h._evaluation_context())['state'], 'ready')
        task['waiting'] = {'kind': 'external_event', 'next_owner': 'user'}
        h._apply(review_action, contract_review({'task': task}), 'EX-other-review', owns_response=False)
        self.assertEqual(task['waiting'], {'kind': 'external_event', 'next_owner': 'user'})
        self.assertEqual(planning.task_ready(task, h.instance, h.runtime, evaluation_context=h._evaluation_context())['state'], 'not_ready')

    def test_revision_cannot_omit_target_or_cancel_required_repair_as_unchanged(self):
        h = self.engine
        task = h.runtime['tasks']['TK-1']
        action = {'role': 'research_preparation',
                  'revision_targets': revisions.capture_targets(h.instance, h.runtime, ['TK-1'], required=True)}
        context = {'action': action, 'tasks': [task]}
        # The legacy test asserted only that errors exist; the product's reason is pinned here.
        self.assertEqual(revisions.submission_errors({}, {}, context), [
            {'path': 'activity-extensions.json/revision_resolutions',
             'message': 'resolve each declared target exactly once, using a task withdrawal only for task targets'}])
        extension = {'revision_resolutions': [{'record_id': 'TK-1', 'disposition': 'unchanged', 'reason': 'skip'}]}
        self.assertEqual(revisions.submission_errors({}, extension, context), [
            {'path': 'activity-extensions.json/revision_resolutions',
             'message': 'a required revision or rejected contract cannot be cancelled as unchanged'}])
        extension['revision_resolutions'][0]['disposition'] = 'revised'
        self.assertEqual(revisions.submission_errors({'candidates': [{'title': 'revision', 'revises_task_id': 'TK-1'}]},
                                                     extension, context), [])


if __name__ == '__main__':
    unittest.main()

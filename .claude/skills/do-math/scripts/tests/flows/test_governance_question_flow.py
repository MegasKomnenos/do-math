"""A worker's user question, its answer and the next worker's input (``question_engine``, ``governance``).

The owner of a restored public activation runs the research roles through
the workers: the model double answers them with the default responder, except
that the research work waits on two questions and routes the first to the user
in its activity extensions (as the legacy local runner wrote them). The user
then acts by public control. The scene runs several role calls, longer than one
Sim test's budget.
"""
from pathlib import Path
import tempfile
import unittest

from do_math.canonical import canonical_json
from support.default_responder import DefaultResponder, common as role_output
from support.model import ModelDouble
from support.sim import Sim, warm_template

setUpModule = warm_template

QUESTIONS = ['Choose option one or two?', 'Research the remaining lemma.']


class RevisionRequestResponder(DefaultResponder):
    def __init__(self, *, disagree=False):
        super().__init__()
        self.disagree = disagree

    def respond(self, role, context, workspace):
        if role == 'research_preparation' and context['action'].get('revision_targets'):
            identifier, basis = next(iter(context['action']['revision_targets'].items()))
            (workspace / 'grounds.txt').write_bytes(b'The supplied contract already assigns the tool check to research work.\n')
            (workspace / 'activity-extensions.json').write_bytes(canonical_json({'revision_resolutions': [{
                'record_id': identifier, 'disposition': 'dismissed', 'request_refs': basis['source_refs'],
                'evidence_refs': ['workspace:grounds.txt'], 'reason': 'The request demanded a future performer result before approval'}]}))
            return role_output(role)
        output = super().respond(role, context, workspace)
        if role == 'task_contract_review' and (self.disagree or not context['action'].get('contract_review_reconsideration')):
            item = next(r for r in output['item_reviews'] if r['item_id'] == 'tools_authority_profiles')
            item.update(decision='revision_required', findings=['Need the future work tool call first'], next_owner='research_preparation')
        return output


class RoutingResponder(DefaultResponder):
    """The default responder, but research work waits on ``QUESTIONS`` and routes the first to the user."""

    def respond(self, role, ctx, workspace):
        if role != 'research_work':
            return super().respond(role, ctx, workspace)
        output = role_output('research_work')
        output.update(outcome='waiting', report='A user choice is needed.', remaining_work=['Use the chosen option.'],
                      checkpoint='Waiting for the user.', questions=list(QUESTIONS))
        (Path(workspace) / 'activity-extensions.json').write_bytes(canonical_json({'question_routes': [
            {'question_index': 0, 'owner': 'user', 'target_ids': [ctx['action']['target']],
             'reason': 'The user owns this choice.'}]}))
        return output


class QuestionFlowTests(unittest.TestCase):
    def test_execution_subject_is_handled_by_real_operational_review_and_disposition(self):
        from support.engine_lifecycle import clear_work
        sim = Sim.activated()
        clear_work(sim)
        sim.engine._enqueue('maintenance', reason='Publish the execution support question')
        sim.engine._save()

        class ExecutionResponder(DefaultResponder):
            def respond(self, role, context, workspace):
                if role == 'maintenance':
                    output = {**role_output(role), 'report': 'Preserve the exact execution for a scoped operational inspection',
                        'questions': ['Does this execution need another operational action?']}
                    extensions = {'question_routes': [{'question_index': 0, 'owner': 'operations',
                        'target_ids': [context['instance_id']], 'reason': 'Inspect this actual execution',
                        'handler_role': 'operational_review', 'obligation': {'kind': 'execution_support',
                            'subject_ref': context['execution_id'], 'requirement_ref': 'execution-support'}}]}
                elif role == 'operational_review' and context['action'].get('question_ids'):
                    assigned, = context['operations_questions']
                    output = {**role_output(role), 'disposition': {'kind': 'continue',
                        'basis_refs': [context['action']['target']], 'next_owner': 'engine',
                        'next_review': None, 'reason': 'The preserved execution needs no repair or replay'}}
                    extensions = {'question_resolutions': [{'question_id': assigned['id'],
                        'generation': assigned['assigned_generation'], 'affected_ids': assigned['assigned_target_ids'],
                        'disposition': 'resolved', 'evidence_refs': [context['action']['target']],
                        'reason': 'The exact ended execution and its retained result were inspected'}]}
                else:
                    return super().respond(role, context, workspace)
                (workspace / 'activity-extensions.json').write_bytes(canonical_json(extensions))
                return output

        sim.model = ModelDouble(sim.clock, ExecutionResponder())
        sim.run_until(lambda s: bool(s.runtime['question_links']) and all(e['status'] == 'ended'
            for e in s.runtime['executions'].values()), max_steps=1)
        parent, = sim.runtime['question_links']
        target = parent['obligation']['subject_ref']
        sim.run_until(lambda s: next(q for q in s.runtime['question_links'] if q['id'] == parent['id'])['status'] == 'resolved', max_steps=4)
        question = next(q for q in sim.runtime['question_links'] if q['id'] == parent['id'])
        (handler_id,) = question['handling']['execution_ids']
        handler = sim.runtime['executions'][handler_id]
        self.assertEqual((handler['role'], handler['action']['target']), ('operational_review', target))
        disposition, = [r for r in sim.runtime['operational_dispositions'].values() if r['execution_id'] == handler_id]
        self.assertEqual((disposition['target_execution_id'], disposition['disposition']['kind'], disposition['status']),
                         (target, 'continue', 'applied'))
        self.assertEqual(question['resolution_ref'], handler_id)

    def test_record_change_wait_and_user_child_answer_resume_the_actual_parent_handler(self):
        """Two concrete waits use their real source/decision receipts, never immediate triage loops."""
        from copy import deepcopy
        from support.engine_lifecycle import applied, clear_work, task
        for kind in ('record_change', 'question'):
            with self.subTest(kind=kind):
                sim = Sim.activated()
                clear_work(sim)
                task(sim.engine, 'TK-wait', inputs=['source:arrive.txt'])
                sim.engine._enqueue('maintenance', 'TK-wait', reason='Publish the support question')
                sim.engine._save()

                class WaitResponder(DefaultResponder):
                    def respond(self, role, context, workspace):
                        if role != 'maintenance':
                            return super().respond(role, context, workspace)
                        output = role_output(role)
                        output['report'] = 'Inspect the assigned support scope and preserve its actual evidence'
                        action = context['action']
                        if not action.get('question_ids'):
                            output['questions'] = ['Recover the required source or a scoped user decision']
                            extensions = {'question_routes': [{'question_index': 0, 'owner': 'operations',
                                'target_ids': ['TK-wait'], 'blocks': True, 'reason': 'The source or owner choice is needed',
                                'obligation': {'kind': 'input_retrieval', 'subject_ref': 'TK-wait', 'requirement_ref': kind}}]}
                        else:
                            assigned, = context['operations_questions']
                            (workspace / 'observation.txt').write_bytes(b'Inspected the fixed support inputs.\n')
                            resolution = {'question_id': assigned['id'], 'generation': action['question_generation'],
                                'affected_ids': action['question_target_ids'], 'evidence_refs': ['workspace:observation.txt'],
                                'reason': 'The exact assigned scope was checked'}
                            extensions = {'question_resolutions': [resolution]}
                            if action['question_generation'] == 1:
                                if kind == 'record_change':
                                    resolution.update(disposition='waiting', wait_for={'kind': 'record_change',
                                        'ref': 'source:arrive.txt', 'basis': assigned['record_bases']['source:arrive.txt']})
                                else:
                                    output['questions'] = ['Which of the two permitted input scopes should this task use?']
                                    extensions['question_routes'] = [{'question_index': 0, 'owner': 'user',
                                        'target_ids': ['TK-wait'], 'blocks': True, 'reason': 'The user owns the scope choice'}]
                                    resolution.update(disposition='transferred', next_owner='user', recipient_ref='output:questions/0')
                            else:
                                resolution['disposition'] = 'resolved'
                                if kind == 'question':
                                    child = next(q for q in context['question_links'] if q['owner'] == 'user')
                                    resolution['evidence_refs'] = [child['resolution_ref']]
                                else:
                                    resolution['evidence_refs'] = ['source:arrive.txt']
                        (workspace / 'activity-extensions.json').write_bytes(canonical_json(extensions))
                        return output

                sim.model = ModelDouble(sim.clock, WaitResponder())
                sim.run_until(lambda s: any(q.get('handling', {}).get('state') == 'waiting' for q in s.runtime['question_links'])
                    and all(e['status'] == 'ended' for e in s.runtime['executions'].values()), max_steps=5)
                parent = next(q for q in sim.runtime['question_links'] if q['owner'] == 'operations')
                qid = parent['id']
                self.assertEqual(parent['status'], 'open')
                self.assertEqual(len(parent['handling']['execution_ids']), 1)
                before = deepcopy(parent)
                sim.restart()
                sim.engine._reconcile_question_actions()
                self.assertEqual(next(q for q in sim.runtime['question_links'] if q['id'] == qid), before)
                self.assertFalse(any(a.get('question_ids') == [qid] for a in sim.runtime['queue']))
                if kind == 'record_change':
                    path = sim.root / 'arrive.txt'
                    path.write_bytes(b'The newly supplied source.\n')
                    applied(sim, 'source', config={'path': str(path)})
                else:
                    child = next(q for q in sim.runtime['question_links'] if q['owner'] == 'user')
                    applied(sim, 'decision', config={'change': {'kind': 'question_answer', 'text': 'Use the first permitted scope',
                        'target_ids': ['TK-wait'], 'resolves_questions': [child['id']]}})
                sim.run_until(lambda s: next(q for q in s.runtime['question_links'] if q['id'] == qid)['status'] == 'resolved', max_steps=6)
                parent = next(q for q in sim.runtime['question_links'] if q['id'] == qid)
                self.assertEqual(parent['handling']['generation'], 2)
                self.assertEqual(len(parent['handling']['execution_ids']), 2)
                self.assertEqual([r['kind'] for r in parent['resolution_history']],
                    ['waiting' if kind == 'record_change' else 'transferred', 'ai_resolution'])
                self.assertTrue(all(sim.runtime['executions'][eid]['submission_receipt']['state'] == 'accepted'
                    for eid in parent['handling']['execution_ids']))
                snapshot = deepcopy(sim.runtime['question_links'])
                sim.restart()
                sim.engine._reconcile_question_actions()
                self.assertEqual(sim.runtime['question_links'], snapshot)

    def test_ai_revision_dismissal_reaches_independent_approval_and_selection(self):
        from do_math import planning
        from support.engine_lifecycle import clear_work, task
        sim = Sim.activated()
        clear_work(sim)
        row = task(sim.engine, 'TK-dismiss', approved=False)
        original_hash = planning.contract_hash(row)
        sim.engine._save()

        sim.model = ModelDouble(sim.clock, RevisionRequestResponder())
        sim.run_until(lambda s: any(a['role'] == 'research_work' and a.get('target') == row['id']
            for a in s.runtime['queue']), max_steps=8)
        task_row = sim.runtime['tasks'][row['id']]
        self.assertEqual(planning.contract_hash(task_row), original_hash)
        self.assertEqual(task_row['revision'], 1)
        self.assertNotIn('revision_requested', task_row)
        self.assertFalse(any(w['action'].get('revision_targets') for w in sim.runtime.get('waiting_actions', {}).values()))
        self.assertEqual([r['decision'] for r in task_row['reviews']], ['revision_required', 'approved'])
        reconsideration, = task_row['contract_review_reconsiderations']
        self.assertEqual(reconsideration['status'], 'reviewed')
        self.assertNotEqual(reconsideration['requested_by'], reconsideration['review_execution_id'])
        self.assertEqual(planning.effective_contract_review(task_row, sim.instance, sim.runtime)['decision'], 'approved')
        sim.restart()
        self.assertFalse(planning.revision_required(sim.runtime['tasks'][row['id']]))

    def test_repeated_dismissal_keeps_one_conflict_obligation_without_more_automatic_reviews(self):
        from do_math import planning
        from support.engine_lifecycle import clear_work, task
        sim = Sim.activated()
        clear_work(sim)
        row = task(sim.engine, 'TK-conflict', approved=False)
        sim.engine._save()
        sim.model = ModelDouble(sim.clock, RevisionRequestResponder(disagree=True))
        sim.run_until(lambda s: any(q.get('obligation', {}).get('kind') == 'decision_conflict' for q in s.runtime['question_links'])
            and all(e['status'] == 'ended' for e in s.runtime['executions'].values()), max_steps=7)
        current = sim.runtime['tasks'][row['id']]
        self.assertEqual(len(current['reviews']), 2)
        self.assertFalse(planning.revision_required(current))
        self.assertEqual(current['contract_review_reconsiderations'][0]['status'], 'conflict')
        questions = [q for q in sim.runtime['question_links'] if q.get('obligation', {}).get('kind') == 'decision_conflict']
        self.assertEqual(len(questions), 1)
        self.assertTrue(any(a.get('question_ids') == [questions[0]['id']] for a in sim.runtime['queue']))
        sim.restart()
        sim.engine._refresh_readiness()
        self.assertFalse(any(a['role'] == 'task_contract_review' for a in sim.runtime['queue']))
        self.assertEqual(len(sim.runtime['tasks'][row['id']]['reviews']), 2)

    def test_missing_review_input_gets_real_handler_and_same_contract_review_after_restart(self):
        """Real worker submission, QU/action/EX, collected evidence, cold owner and renewed approval."""
        from copy import deepcopy
        from do_math import planning
        from support.engine_lifecycle import clear_work, task
        sim = Sim.activated()
        clear_work(sim)
        row = task(sim.engine, 'TK-input', approved=False)
        original_hash = planning.contract_hash(row)
        sim.engine._save()

        class InputResponder(DefaultResponder):
            def respond(self, role, context, workspace):
                output = super().respond(role, context, workspace)
                if role == 'task_contract_review' and not any(q['status'] == 'resolved' for q in context['question_links']):
                    item = next(r for r in output['item_reviews'] if r['item_id'] == 'tools_authority_profiles')
                    item.update(decision='unresolved', findings=['The referenced support input cannot be read'],
                        missing_inputs=['tool:scholarly'], next_owner='maintenance')
                    output['questions'] = ['Recover the missing support evidence for this contract.']
                    (workspace / 'activity-extensions.json').write_bytes(canonical_json({'question_routes': [{
                        'question_index': 0, 'owner': 'operations', 'target_ids': [row['id']], 'blocks': True,
                        'reason': 'A specific supplied support input is missing', 'review_item_ids': ['tools_authority_profiles'],
                        'obligation': {'kind': 'input_retrieval', 'subject_ref': row['id'], 'requirement_ref': 'tool:scholarly'}}]}))
                elif role == 'maintenance' and context['action'].get('question_ids'):
                    assigned, = context['operations_questions']
                    (workspace / 'support.txt').write_bytes(b'Checked the supplied contract and support input.\n')
                    output.update(report='Recovered the missing input; future research calls remain the performer responsibility.',
                        used_sources=[row['id']])
                    (workspace / 'activity-extensions.json').write_bytes(canonical_json({'question_resolutions': [{
                        'question_id': assigned['id'], 'disposition': 'resolved', 'generation': assigned['assigned_generation'],
                        'affected_ids': assigned['assigned_target_ids'], 'evidence_refs': ['workspace:support.txt'],
                        'reason': 'The supplied support evidence is now readable'}]}))
                return output

        sim.model = ModelDouble(sim.clock, InputResponder())
        sim.run_until(lambda s: bool(s.runtime['question_links']) and all(
            e['status'] == 'ended' for e in s.runtime['executions'].values()), max_steps=1)
        question, = sim.runtime['question_links']
        qid = question['id']
        self.assertNotIn('revision_requested', sim.runtime['tasks'][row['id']])
        handlers = [a for a in sim.runtime['queue'] if a.get('question_ids') == [qid]]
        self.assertEqual(len(handlers), 1)
        self.assertEqual((handlers[0]['role'], handlers[0]['target']), ('maintenance', row['id']))
        before = deepcopy(handlers)
        sim.restart()
        sim.engine._reconcile_question_actions()
        self.assertEqual([a for a in sim.runtime['queue'] if a.get('question_ids') == [qid]], before)
        sim.run_until(lambda s: any(r['decision'] == 'approved' for r in s.runtime['tasks'][row['id']]['reviews']), max_steps=8)
        question = next(q for q in sim.runtime['question_links'] if q['id'] == qid)
        self.assertEqual(question['status'], 'resolved')
        (handler_id,) = question['handling']['execution_ids']
        execution = sim.runtime['executions'][handler_id]
        self.assertEqual(execution['action']['id'], before[0]['id'])
        self.assertEqual(execution['submission_receipt']['state'], 'accepted')
        evidence, = question['resolution_history'][0]['evidence']['resolved_evidence']
        self.assertEqual(sim.engine.store.read(evidence['artifact_ref'], sim.engine.head),
            b'Checked the supplied contract and support input.\n')
        self.assertEqual(planning.contract_hash(sim.runtime['tasks'][row['id']]), original_hash)
        self.assertEqual(planning.effective_contract_review(sim.runtime['tasks'][row['id']], sim.instance, sim.runtime)['decision'], 'approved')
        self.assertEqual(planning.task_ready(sim.runtime['tasks'][row['id']], sim.instance, sim.runtime,
            evaluation_context=sim.engine._evaluation_context())['state'], 'ready')
        published = deepcopy(sim.runtime['question_links'])
        sim.restart()
        self.assertEqual(sim.runtime['question_links'], published)

    def test_answer_closes_only_its_question_and_reaches_the_next_worker(self):
        """About 7 s: the preparation, contract review, plan and research work are role calls through the worker."""
        sim = Sim.activated()
        sim.model = ModelDouble(sim.clock, RoutingResponder())

        def worked(s):
            return [row for row in s.runtime['executions'].values()
                    if row.get('role') == 'research_work' and row.get('status') == 'ended']
        sim.run_until(worked, max_steps=30)
        engine = sim.engine
        (work,) = worked(sim)
        task = work['action']['target']
        rows = [row for row in engine._question_view() if row['origin_execution_id'] == work['id']]
        self.assertEqual(sorted((row['owner'], row['text']) for row in rows),
                         [('research', QUESTIONS[1]), ('user', QUESTIONS[0])], work)
        user = next(row for row in rows if row['owner'] == 'user')
        research = next(row for row in rows if row['owner'] == 'research')
        self.assertEqual(engine.status()['questions'], [QUESTIONS[0]])
        sim.control('input', text='Unrelated information.')
        engine.process_controls()
        self.assertEqual(next(row for row in engine.runtime['question_links'] if row['id'] == user['id'])['status'], 'open')
        sim.control('decision', text='Use option one.', config={'change': {
            'kind': 'question_answer', 'text': 'Use option one.', 'target_ids': [task],
            'resolves_questions': [user['id']]}})
        engine.process_controls()
        with tempfile.TemporaryDirectory() as reader:
            context = engine._context({'id': 'next', 'role': 'research_work', 'target': task, 'revision_targets': {}},
                                      Path(reader))
        answered = next(row for row in context['question_links'] if row['id'] == user['id'])
        self.assertEqual(answered['status'], 'resolved')
        self.assertEqual(answered['resolution']['change']['text'], 'Use option one.')
        self.assertEqual(next(row for row in context['question_links'] if row['id'] == research['id'])['status'], 'open')
        self.assertEqual(engine.status()['questions'], [])


if __name__ == '__main__':
    unittest.main()

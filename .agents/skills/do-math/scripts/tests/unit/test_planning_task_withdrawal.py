"""Autonomous withdrawal of AI-prepared tasks (``task_scope``, ``submission``; layer 2) and a corrected reading
of an unchanged source (``knowledge``, ``knowledge_io``; layer 2), moved from ``test_task_scope``.

The tests call the product's functions on plain records
(``record_fixtures.withdrawable_task``: task ``TK-AI`` prepared by ``EX-prep``,
its dependent ``TK-dependent``, the queued review ``AC-review``, the unrelated
``AC-other`` and the waiting work ``AC-work``). Nothing of the product is
replaced. The engine path that applies a plan's withdrawal extension is in
``sim.test_planning_engine_receivers``.
"""
from pathlib import Path
import tempfile
import unittest

from do_math.planning import contract_hash
from do_math.task_scope import validate_withdrawal_scope
from support.record_builders import task_contract, withdraw_prepared, withdrawable_task


class TaskScopeTests(unittest.TestCase):
    def test_withdrawal_preserves_contract_and_cancels_only_prestart_actions(self):
        instance, runtime, snapshot = withdrawable_task()
        _, changed = withdraw_prepared(runtime, snapshot)
        task = changed['tasks']['TK-AI']
        self.assertEqual(task['status'], 'closed')
        self.assertEqual(task['completion_obligations'], snapshot['TK-AI']['completion_obligations'])
        self.assertEqual(task['reviews'], [{'decision': 'approved'}])
        self.assertNotIn('assessment', task)
        record = task['scope_disposition']
        self.assertEqual(record['actor_execution'], 'EX-plan')
        self.assertEqual(record['previous_revision'], 3)
        self.assertEqual(record['previous_contract_sha256'], contract_hash(snapshot['TK-AI']))
        self.assertTrue(record['cancelled_queue_actions'])
        self.assertTrue(record['cancelled_waiting_actions'])
        # Only the actions on the withdrawn task are cancelled; the untargeted plan stays queued.
        self.assertEqual(record['cancelled_queue_actions'],
                         [{'id': 'AC-review', 'role': 'task_contract_review', 'target': 'TK-AI'}])
        self.assertEqual(record['cancelled_waiting_actions'],
                         [{'id': 'AC-work', 'entry': {'action': {'id': 'AC-work', 'role': 'research_work', 'target': 'TK-AI'}}}])
        self.assertEqual([action['id'] for action in changed['queue']], ['AC-other'])
        self.assertEqual(changed['waiting_actions'], {})
        self.assertNotIn('task_readiness', changed)
        self.assertEqual(changed['tasks']['TK-dependent']['status'], 'waiting')
        self.assertEqual(runtime['tasks']['TK-AI']['status'], 'planned')

    def test_selected_unstarted_withdrawal_excludes_only_its_authorizing_execution(self):
        _, runtime, snapshot = withdrawable_task()
        runtime['tasks']['TK-AI']['status'] = 'active'
        runtime['executions']['EX-plan'] = {'id': 'EX-plan', 'role': 'research_preparation',
                                            'status': 'stopping', 'action': {'target': 'TK-AI'}}
        _, changed = withdraw_prepared(runtime, snapshot)
        self.assertEqual(changed['tasks']['TK-AI']['status'], 'closed')
        runtime['executions']['EX-other'] = {**runtime['executions']['EX-plan'], 'id': 'EX-other'}
        with self.assertRaisesRegex(ValueError, 'live execution'):
            withdraw_prepared(runtime, snapshot)
        del runtime['executions']['EX-other']
        runtime['executions']['EX-plan']['role'] = 'research_work'
        with self.assertRaisesRegex(ValueError, 'live execution'):
            withdraw_prepared(runtime, snapshot)

    def test_terminal_assessment_cannot_withdraw_even_without_results(self):
        _, runtime, snapshot = withdrawable_task()
        for decision in ('completed', 'closed'):
            with self.subTest(decision=decision), self.assertRaisesRegex(ValueError, 'terminal'):
                validate_withdrawal_scope(runtime['tasks']['TK-AI'], snapshot['TK-AI'],
                                          proposed_assessment={'decision': decision})

    def test_rejects_changed_snapshot_user_or_academic_task_and_live_or_terminal_task(self):
        # Each case pins the check that rejects it. The academic requirement added to the live task
        # alone changes the contract hash, so the snapshot check rejects it first; with the snapshot
        # holding it too, the protected-obligation rule of validate_withdrawal_scope rejects it.
        changed = '^task contract changed since the execution input snapshot: TK-AI$'
        live = '^task has a live execution: TK-AI$'
        finished = '^withdrawal requires an unfinished task$'
        for name, mutation, reason in (
            ('snapshot', lambda runtime, snap: snap['TK-AI'].update(question='new'), changed),
            ('user', lambda runtime, snap: runtime['tasks']['TK-AI'].update(producer_execution='EX-user'),
             '^task is not attributable to a research preparation execution: TK-AI$'),
            ('academic', lambda runtime, snap: runtime['tasks']['TK-AI'].update(academic_requirement_id='writeup'), changed),
            ('work', lambda runtime, snap: runtime['executions'].update(EX={'id': 'EX', 'role': 'research_work', 'status': 'running', 'action': {'target': 'TK-AI'}}), live),
            ('review', lambda runtime, snap: runtime['executions'].update(EX={'id': 'EX', 'role': 'task_contract_review', 'status': 'running', 'action': {'target': 'TK-AI'}}), live),
            ('completed', lambda runtime, snap: runtime['tasks']['TK-AI'].update(status='completed'), finished),
            ('closed', lambda runtime, snap: runtime['tasks']['TK-AI'].update(status='closed'), finished),
            ('academic in snapshot', lambda runtime, snap: (runtime['tasks']['TK-AI'].update(academic_requirement_id='writeup'),
                                                            snap['TK-AI'].update(academic_requirement_id='writeup')),
             '^protected obligations require authoritative item dispositions$'),
        ):
            with self.subTest(mutation=name):
                instance, runtime, snapshot = withdrawable_task()
                mutation(runtime, snapshot)
                with self.assertRaisesRegex(ValueError, reason):
                    withdraw_prepared(runtime, snapshot)

    def test_submission_rejects_nonwithdraw_and_duplicate_requests(self):
        """The sealed extension schema and the submission check own disposition shape and distinct targets."""
        from support.entry import entry
        _entry = entry()
        from do_math.canonical import canonical_json
        from do_math.contracts import schema_for
        from do_math.knowledge import content_hash
        from do_math.submission import payload_issues
        from support.role_answers import seal_response
        from support.default_responder import common
        # A disposition revises an existing task, so the fixed input supplies that task
        # with its content hash, as the engine's task views do.
        task = {**task_contract(), 'id': 'TK-AI', 'status': 'planned', 'producer_execution': 'EX-prep',
                'results': [], 'reviews': []}
        context = {'action': {'role': 'research_preparation'}, 'budget_unit': 'concurrent_sessions',
                   'tasks': [{**task, 'content_sha256': content_hash(task)}], 'knowledge_catalog': [],
                   'kind_definitions': {}, 'sources': []}

        def issues(dispositions):
            with tempfile.TemporaryDirectory() as directory:
                workspace, extensions = Path(directory), {'task_dispositions': dispositions}
                (workspace / 'activity-extensions.json').write_bytes(canonical_json(extensions))
                output = common('research_preparation')
                seal_response(output, context, workspace)
                return payload_issues(output, schema_for('research_preparation'), context, extensions, workspace, clock=_entry.ports.clock)

        withdraw = [{'task_id': 'TK-AI', 'disposition': 'withdraw', 'reason': 'x'}]
        self.assertEqual(issues(withdraw), [])
        context['ongoing_work'] = [
            {'execution_id': 'EX-other', 'target': 'TK-AI', 'status': 'running'}]
        self.assertEqual([(row['path'], row['message']) for row in issues(withdraw)], [
            ('activity-extensions.json/task_dispositions', 'task has another live execution')])
        context.pop('ongoing_work')

        revise = issues([{'task_id': 'TK-AI', 'disposition': 'revise', 'reason': 'x'}])
        self.assertTrue(any(row['path'] == 'activity-extensions.json/task_dispositions/0/disposition' for row in revise))
        duplicate = issues([{'task_id': 'TK-AI', 'disposition': 'withdraw', 'reason': 'x'},
                            {'task_id': 'TK-AI', 'disposition': 'withdraw', 'reason': 'x'}])
        self.assertTrue(any(row['path'] == 'activity-extensions.json/task_dispositions'
                            and 'distinct targets' in row['message'] for row in duplicate))

    def test_partial_work_requires_item_disposition_and_preserves_results_on_rejection(self):
        _, runtime, snapshot = withdrawable_task()
        runtime['tasks']['TK-AI'].update(status='waiting', results=[{'id': 'R-partial', 'outcome': 'partial'}])
        runtime['executions']['EX-work'] = {'id': 'EX-work', 'role': 'research_work', 'status': 'ended',
                                            'action': {'target': 'TK-AI'}, 'outcome': 'output_accepted'}
        snapshot['TK-AI'].update(status='waiting')

        with self.assertRaisesRegex(ValueError, 'item dispositions'):
            withdraw_prepared(runtime, snapshot)

        task = runtime['tasks']['TK-AI']
        self.assertEqual(task['status'], 'waiting')
        self.assertEqual(task['results'], [{'id': 'R-partial', 'outcome': 'partial'}])
        self.assertEqual(runtime['executions']['EX-work']['outcome'], 'output_accepted')


class SourceCorrectionTest(unittest.TestCase):
    def test_same_source_bytes_can_revise_a_misread_claim_and_suspend_dependents(self):
        """A corrected reading changes knowledge, not the immutable source bytes."""
        from support.entry import entry
        _entry = entry()
        from types import SimpleNamespace
        from do_math import knowledge, knowledge_io, knowledge_records as kr
        engine = SimpleNamespace(instance={}, runtime={'queue': [], 'history': []})
        engine.instance['sources'] = [{'id': 'SO-paper', 'name': 'paper.pdf', 'path': 'source.pdf',
                                       'sha256': 'a' * 64, 'status': 'active'}]
        candidates = {
            'KN-reading': {'id': 'KN-reading', 'revision': 1, 'status': 'verified', 'statement': 'The paper prints m/n.',
                           'explanation': 'Earlier reading.', 'summary': 'Misread fraction.', 'lean_code': '',
                           'declaration_names': [], 'dependencies': [], 'reviews': [],
                           'source_basis': [{'name': 'paper.pdf', 'path': 'source.pdf', 'sha256': 'a' * 64}]},
            'KN-dependent': {'id': 'KN-dependent', 'revision': 1, 'status': 'verified', 'statement': 'Derived claim.',
                             'explanation': 'Depends on the reading.', 'summary': 'Dependent.', 'lean_code': '',
                             'declaration_names': [], 'dependencies': ['KN-reading'], 'reviews': []},
        }
        ids = {}
        for name, row in candidates.items():
            candidate = {key: row[key] for key in ('statement', 'explanation', 'summary', 'lean_code', 'declaration_names', 'dependencies')}
            candidate.update(kind='observation', title=name, dependencies=[ids.get(k, k) for k in row['dependencies']])
            engine.instance, engine.runtime, ids[name] = knowledge_io.import_candidate(
                engine.instance, engine.runtime, candidate, source_ref='SO-paper', actor_ref='user', clock=_entry.ports.clock)
        changes = {'statement': 'The paper prints n/m.',
                   'explanation': 'The original PDF is unchanged; prior transcription reversed it.'}
        roots = knowledge.revision_roots(engine.instance, ids['KN-reading'])
        impact = knowledge.plan_impact(engine.instance, engine.runtime, roots, [])
        engine.instance, engine.runtime = knowledge.revise_knowledge(
            engine.instance, engine.runtime, ids['KN-reading'], changes, reason='PDF layout audit reads n/m.',
            actor_ref='EX-correction', declared_impact=impact['computed_impact'], clock=_entry.ports.clock)

        self.assertEqual(engine.instance['sources'][0]['sha256'], 'a' * 64)
        old = engine.instance['knowledge'][ids['KN-reading']]
        self.assertEqual(old['lifecycle'], 'superseded')
        self.assertEqual(kr.proposal_view(engine.instance, old['id'])['statement'], 'The paper prints m/n.')
        replacement = next(k for k, v in engine.instance['knowledge'].items() if v.get('supersedes') == old['id'])
        self.assertEqual(kr.proposal_view(engine.instance, replacement)['statement'], 'The paper prints n/m.')
        self.assertFalse(knowledge.assess_use(engine.instance['knowledge'][ids['KN-dependent']], engine.instance)['valid'])
        self.assertIn(ids['KN-dependent'], next(row for row in engine.runtime['history']
                                                if row['kind'] == 'knowledge_reassessment_required')['affected_ids'])


if __name__ == '__main__':
    unittest.main(verbosity=2)

"""Currentness through whole role calls on the Sim (설계 4.1, 5.4 흐름 폴더): a changed premise is refreshed, not repaired.

Each scene runs the owner's role calls: the worker's model double answers from
the actual role input and submits with the workspace tool, and the owner
receives the sealed response. Changes that the legacy tests made by wrapping
``_receive_submission`` or inside a local runner happen here inside the model
call, after its input was fixed and before its submission is received
(``ScenarioModel.during``): the calls fake hands the turn between the owner and
the call, so a change the call makes to the owner's state is not a race. A
failed attempt is a provider call the CLI double interrupts
(``knowledge_currentness.interrupt``). Every scene takes more than one Sim
test's budget, since it runs one or more model calls.

- Sources: a same-path source registered twice is unchanged; a changed source
  makes a completed task's assessment non-current and blocks its dependents; a
  source changed during a call returns that call's graceful output for a refresh.
- Plans citing a task (on ``scheduling_recovery.reviewed_sim``, the legacy
  ``plan_ready_instance``): a lifecycle change of the cited task is accepted, a
  contract change returns the plan.
- Operational reviews: a checkpoint cited from the review's input and replaced
  before the review is received is a changed premise (refresh) unless another
  application error remains (producer repair).
- A split research response whose second bundle cites a source that changed
  during the call is partly accepted; the receiver routes it by the returned
  bundle's issues (a refresh), not by the ``partial`` status.
"""
from copy import deepcopy
import hashlib
import json
import unittest

from do_math.planning import seal_contract_review, task_ready
from support.role_answers import candidate, contract_review
from support.default_responder import DefaultResponder, common
from support.engine_lifecycle import applied, clear_work, only, queue_work, task
from support.knowledge_currentness import await_applied, currentness_model
from support.model import Answer
from support.provider_probes import ObservedCalls
from support.scheduling_model import explicit, scenario_model
from support.scheduling_recovery import reviewed_sim
from support.sim import Sim, warm_template


def setUpModule():
    warm_template()
    reviewed_sim()


class SourceCurrentnessTests(unittest.TestCase):
    def test_same_source_is_idempotent_changed_source_preserves_completed_task_history(self):
        """About 11 s: the owner runs preparation, contract review, plan, work and its assessment until a task completes."""
        sim = Sim.activated()
        source = sim.root / 'source.txt'
        source.write_text('old', encoding='utf-8')
        applied(sim, 'source', config={'path': str(source)})
        first = deepcopy(sim.instance['sources'][0])
        applied(sim, 'source', config={'path': str(source)})
        self.assertEqual(first, sim.instance['sources'][0])

        def reading_source(output, context):
            for row in output['candidates']:
                row['inputs'].append('source:source.txt')
            return output
        sim.model.on('research_preparation').reply(Answer(reading_source))
        sim.run_until(lambda s: any(t['status'] == 'completed' for t in s.runtime['tasks'].values()), max_steps=45)
        engine = sim.engine
        task = next(iter(engine.runtime['tasks'].values()))
        completed_assessment = deepcopy(task['assessment'])
        downstream = {**candidate('Downstream'), 'id': 'TK-downstream', 'status': 'planned', 'revision': 1,
            'results': [], 'reviews': [], 'dependencies': [task['id']], 'occurrence_condition': {'op': 'always'},
            'profile_refs': list(task['profile_refs']), 'authority_refs': list(task['authority_refs'])}
        downstream.pop('revises_task_id')  # A stored task record; the wire candidate's revision link is not stored.
        unfinished_instance = deepcopy(engine.instance)
        unfinished_instance['goal_status'] = 'unsolved'
        downstream['reviews'] = [seal_contract_review(downstream, contract_review({'task': downstream}),
            unfinished_instance, engine.runtime, execution_id='EX-downstream-review')]
        self.assertEqual(task_ready(downstream, unfinished_instance, engine.runtime,
                                   evaluation_context=engine._evaluation_context())['state'], 'ready')
        engine._save()
        source.write_text('new', encoding='utf-8')
        applied(sim, 'source', config={'path': str(source)})
        engine = sim.engine
        current = engine.runtime['tasks'][task['id']]
        self.assertEqual(current['status'], 'completed')
        self.assertEqual(current['assessment']['decision'], completed_assessment['decision'])
        self.assertEqual(current['assessment']['item_dispositions'], completed_assessment['item_dispositions'])
        self.assertFalse(current['assessment']['current'])
        self.assertIn('source content changed', current['assessment']['invalidated_reason'].lower())
        self.assertEqual(engine.instance['sources'][0]['revision'], 2)
        unfinished_instance = deepcopy(engine.instance)
        unfinished_instance['goal_status'] = 'unsolved'
        readiness = task_ready(downstream, unfinished_instance, engine.runtime)
        self.assertEqual(readiness['state'], 'not_ready')
        self.assertIn('blocked dependencies', readiness['errors'][0])
        self.assertFalse(any(error.startswith(task['id'] + ':') for error in engine.check()['errors']))

    def test_graceful_output_on_changed_source_is_preserved_but_not_accepted(self):
        """Two changed-source calls and one diagnosis preserve output and stop further refresh."""
        sim = Sim.activated()
        applied(sim, 'configure', config={'max_output_repairs': 0})
        source = sim.root / 'basis.txt'
        source.write_text('old', encoding='utf-8')
        applied(sim, 'source', config={'path': str(source)})
        model = currentness_model(sim)

        source_changes = []
        def changing(context, workspace):
            source_changes.append(context['execution_id'])
            source.write_text('new revision ' + str(len(source_changes)), encoding='utf-8')
            await_applied(sim, sim.control('source', text='the source changed', config={'path': str(source)}))
            (workspace / 'partial.txt').write_text('The old input was read.', encoding='utf-8')
        model.during('research_preparation', changing)
        model.on('research_preparation').reply(explicit({**common('Old-source response'),
                                                         'used_sources': ['basis.txt'], 'candidates': []}))
        cycles = sim.runtime['cycles']
        sim.step()
        engine = sim.engine
        [execution] = [row for row in engine.runtime['executions'].values() if row['role'] == 'research_preparation']
        self.assertEqual(execution['outcome'], 'execution_incomplete')
        self.assertEqual(execution['error_kind'], 'currentness_changed')
        issues = execution['integration_result']['issues']
        self.assertTrue(any(row['rule_id'] == 'integration.currentness' and 'source' in row['message']
                            for row in issues), issues)
        self.assertEqual((cycles, engine.runtime['cycles']), (0, 0))
        # With no output repair allowed, the changed premise is still refreshed once.
        refreshed = [a for a in engine.runtime['queue'] if a.get('refresh', {}).get('execution_id') == execution['id']]
        self.assertEqual(len(refreshed), 1)
        self.assertNotIn('repair', refreshed[0])
        self.assertNotIn(execution['action']['id'], engine.runtime.get('waiting_actions', {}))
        entry = next(f for f in execution['output_files'] if f['path'] == 'partial.txt')
        self.assertEqual(engine.store.read(entry['artifact_ref']), b'The old input was read.')
        # A second real premise change exhausts refresh and opens one diagnosis.
        from support.cross_contracts import assert_call_records
        before = assert_call_records(self, sim)
        self.assertEqual(before['operational_review'], 0)
        sim.step()
        attempts = [row for row in sim.runtime['executions'].values() if row['role'] == 'research_preparation']
        self.assertEqual(len(attempts), 2)
        second = next(row for row in attempts if row['id'] != execution['id'])
        self.assertEqual(second['error_kind'], 'currentness_changed')
        self.assertEqual(second['action']['refresh']['attempt'], 1)
        wait = sim.runtime['waiting_actions'][second['action']['id']]
        self.assertEqual(wait['execution_id'], second['id'])
        self.assertEqual(wait['failure_kind'], 'currentness_changed')
        sim.run_until(lambda current: any(c['role'] == 'operational_review' for c in current.model.calls), max_steps=8)
        after = assert_call_records(self, sim)
        self.assertEqual(after['operational_review'], 1)
        review, = [row for row in sim.runtime['executions'].values() if row['role'] == 'operational_review']
        self.assertEqual(review['action']['target'], second['id'])
        self.assertEqual(review['outcome'], 'output_accepted', review.get('error'))
        for _ in range(2):
            sim.step()
            self.assertEqual(assert_call_records(self, sim)['operational_review'], 1)
        self.assertEqual(len(source_changes), 2)


class PlanCitingTaskTests(unittest.TestCase):
    def plan_citing_task_while(self, change):
        """Run the queued plan, citing a ready task that ``change`` alters during the plan's call.

        Returns ``(sim, task ID, the plan's execution)``.
        """
        sim = reviewed_sim()
        engine = sim.engine
        engine._refresh_readiness()
        self.assertEqual(engine.runtime['queue'][0]['role'], 'research_plan')
        task_id = next(tid for tid, row in engine._task_readiness.items() if row['state'] == 'ready')
        model = scenario_model(sim)
        model.on('research_plan').reply(Answer(lambda out, ctx: {**out, 'used_sources': [*out.get('used_sources', []), task_id]}))
        model.during('research_plan', lambda context, workspace: change(sim.engine.runtime['tasks'][task_id]))
        sim.step()
        plan = next(e for e in reversed(list(sim.runtime['executions'].values())) if e['role'] == 'research_plan')
        return sim, task_id, plan

    def test_cited_task_lifecycle_change_during_plan_does_not_reject_the_plan(self):
        """About 3 s: the plan runs as a model call."""
        sim, task_id, plan = self.plan_citing_task_while(
            lambda task: task.update(deferred_reason='Concurrent planner note', reviews=[*task['reviews'], {'note': 'concurrent'}]))
        self.assertEqual(plan['outcome'], 'output_accepted', plan.get('error'))
        sealed = json.loads(sim.engine.store.read(plan['submission_intent']['output_ref']))
        self.assertIn(task_id, sealed['used_sources'])
        self.assertEqual(plan['integration_result']['status'], 'accepted')
        self.assertEqual(sim.runtime['tasks'][task_id]['status'], 'active')
        self.assertTrue(any(a['role'] == 'research_work' and a.get('target') == task_id for a in sim.runtime['queue']))

    def test_cited_task_contract_change_during_plan_rejects_the_plan(self):
        """About 3 s: the plan runs as a model call."""
        sim, task_id, plan = self.plan_citing_task_while(
            lambda task: task.update(scope={**task['scope'], 'included': [*task['scope']['included'], 'A revised domain']}))
        self.assertEqual(plan['outcome'], 'execution_incomplete')
        self.assertEqual(plan['error_kind'], 'currentness_changed')
        issues = plan['integration_result']['issues']
        self.assertTrue(any(row['rule_id'] == 'integration.currentness' and
            task_id in row['message'] and 'contract_sha256' in row['message'] for row in issues), issues)
        self.assertFalse(any(a['role'] == 'research_work' and a.get('target') == task_id for a in sim.runtime['queue']))


class OperationalBasisReplacementTests(unittest.TestCase):
    def review_after_checkpoint_replacement(self, disposition, *, repeated=False):
        """Run an operational review of a failed attempt whose checkpoint is replaced after the review's input was fixed.

        ``disposition(failed_id, cited_checkpoint_ref)`` is the reviewer's answer. With
        ``repeated=True``, the refreshed input's new checkpoint is replaced again.
        The
        replacement names the same bytes at another stored path (the attempt's
        preserved output file ``checkpoint.json``), as the legacy test re-stored them
        under a new bundle. Returns ``(sim, failed ID, cited reference, review execution)``.
        """
        sim = Sim.activated()
        model = currentness_model(sim)
        model.interrupt('research_preparation', lambda context, workspace: (workspace / 'checkpoint.json').write_text(
            json.dumps({'current_claim': 'A partial lemma is established.', 'evidence_paths': [],
                        'attempts': ['Checked the bounded case.'], 'remaining_work': ['Prove the general case.'],
                        'next_step': 'Resume from the partial lemma.', 'progress_state': 'blocked'}), encoding='utf-8'))
        sim.step()
        failed = next(e for e in sim.runtime['executions'].values() if e['role'] == 'research_preparation')
        cited = sim.runtime['checkpoints'][failed['id']]['artifact_ref']
        replacement = next(row['artifact_ref'] for row in failed['output_files'] if row['path'] == 'checkpoint.json')
        self.assertEqual(sim.engine.store.read(replacement), sim.engine.store.read(cited))
        admitted = []

        def replaced(context, workspace):
            # The target's newest checkpoint changes after the review input was fixed.
            admitted.append(list(context['admissible_basis_refs']))
            checkpoints = sim.engine.runtime['checkpoints']
            checkpoints[failed['id']] = {**checkpoints[failed['id']],
                'artifact_ref': cited if repeated and len(admitted) > 1 else replacement}
        model.during('operational_review', replaced)
        rule = model.on('operational_review').reply(explicit({**common('The failed attempt kept a reusable checkpoint'),
                                                       'disposition': disposition(failed['id'], cited)}))
        if repeated:
            rule.reply(explicit({**common('Reconsider the current preserved checkpoint'),
                                'disposition': disposition(failed['id'], replacement)}))
        sim.step()
        # The fixture cites a checkpoint that its input admitted.
        self.assertEqual(len(admitted), 1)
        self.assertIn(cited, admitted[0])
        review = next(e for e in sim.runtime['executions'].values() if e['role'] == 'operational_review')
        return sim, failed['id'], cited, review

    def test_operational_basis_replaced_after_input_is_refreshed_without_output_repair(self):
        """About 3 s: the failed attempt and its review are two model calls."""
        sim, failed, cited, review = self.review_after_checkpoint_replacement(lambda target, checkpoint: {
            'kind': 'continue', 'basis_refs': [target, checkpoint], 'next_owner': 'engine',
            'reason': 'The preserved checkpoint records the partial lemma.', 'next_review': None})
        self.assertEqual(review['error_kind'], 'currentness_changed', review.get('integration_result'))
        self.assertTrue(any(cited in change['reason'] and 'admissible at input' in change['reason']
                            for change in review['currentness_changes']), review['currentness_changes'])
        followups = [a for a in sim.runtime['queue'] if a['role'] == 'operational_review' and a.get('target') == failed]
        self.assertEqual([a.get('refresh', {}).get('execution_id') for a in followups], [review['id']])
        self.assertNotIn('repair', followups[0], 'A changed premise does not spend an output repair')
        self.assertNotIn(review['action']['id'], sim.runtime.get('waiting_actions', {}))

    def test_second_actual_operational_premise_change_stops_without_recursive_diagnosis(self):
        from support.cross_contracts import worker_executions
        sim, target, _, first = self.review_after_checkpoint_replacement(lambda execution, checkpoint: {
            'kind': 'continue', 'basis_refs': [execution, checkpoint], 'next_owner': 'engine',
            'reason': 'Review the checkpoint admitted in this input.', 'next_review': None}, repeated=True)
        self.assertEqual(first['error_kind'], 'currentness_changed')
        sim.step()
        reviews = [row for row in sim.runtime['executions'].values() if row['role'] == 'operational_review']
        self.assertEqual(len(reviews), 2)
        second = next(row for row in reviews if row['id'] != first['id'])
        self.assertEqual(second['action']['target'], target)
        self.assertEqual(second['error_kind'], 'currentness_changed')
        self.assertEqual(second['action']['refresh']['attempt'], 1)
        wait = sim.runtime['waiting_actions'][second['action']['id']]
        self.assertEqual((wait['execution_id'], wait['next_owner']), (second['id'], 'operations'))
        for _ in range(2):
            sim.step()
            self.assertEqual(sum(c['role'] == 'operational_review' for c in sim.model.calls), 2)
            self.assertFalse(any(a['role'] == 'operational_review' for a in sim.runtime['queue']))
        self.assertCountEqual([eid for eid in worker_executions(sim)
                               if sim.runtime['executions'][eid]['role'] == 'operational_review'],
                              [row['id'] for row in reviews])
        self.assertEqual(sim.engine.store.load(sim.engine.head)[2], sim.runtime)

    def test_replaced_operational_basis_with_another_application_error_stays_a_producer_repair(self):
        """About 3 s: the failed attempt and its review are two model calls."""
        sim, failed, cited, review = self.review_after_checkpoint_replacement(lambda target, checkpoint: {
            'kind': 'repair', 'basis_refs': [target, checkpoint], 'next_owner': 'installation_recovery',
            'reason': 'The receiver rejected the preserved checkpoint.', 'repair_target': 'installation:missing.py',
            'meaning_preserving': True, 'verification': 'Rerun the receiver on the preserved checkpoint.'})
        self.assertEqual(review['error_kind'], 'output_contract', review.get('integration_result'))
        self.assertTrue(any('installation repair target' in row['message']
                            for row in review['integration_result']['issues']), review['integration_result'])
        followups = [a for a in sim.runtime['queue'] if a['role'] == 'operational_review' and a.get('target') == failed]
        self.assertEqual([a.get('repair', {}).get('execution_id') for a in followups], [review['id']])
        self.assertNotIn('refresh', followups[0])


class InsightWork(DefaultResponder):
    """The default responder, except that research work records one insight citing the source ``basis.txt``."""

    def respond(self, role, ctx, workspace):
        out = super().respond(role, ctx, workspace)
        if role == 'research_work':
            out.update(knowledge=[], report='Records one insight from the basis source')
            extensions = {'research_insights': [{'kind': 'observation', 'title': 'Basis insight',
                                                 'statement': 'The basis source states the premise.',
                                                 'summary': 'Basis premise', 'evidence_ids': ['basis.txt']}]}
            (workspace / 'activity-extensions.json').write_text(json.dumps(extensions), encoding='utf-8')
        return out


def split_extensions(output, context):
    """Declare the response and its extension rows as two bundles instead of the seal's one."""
    [bundle] = output['integration_bundles']
    rows = [member for member in bundle['members'] if member.startswith('activity-extensions.json/')]
    second = 'IN-' + hashlib.sha256(bundle['integration_id'].encode()).hexdigest()[:24]
    output['integration_bundles'] = [
        {**bundle, 'members': [member for member in bundle['members'] if member not in rows]},
        {'integration_id': second, 'members': rows, 'impact_set': [], 'authority_refs': [], 'previous_hashes': {}}]


class CurrentnessReturnRoutingTests(unittest.TestCase):
    def test_currentness_return_beside_an_accepted_bundle_is_refreshed_not_repaired(self):
        """About 3 s: the research work runs as a model call while the owner applies a source control.

        A split response can accept one bundle while another returns on changed
        premises. The result status is then 'partial'. That status says only that
        some bundle was accepted: it is the same whether the returned bundle needs a
        refresh or an output repair, so the receiver routes by the returned issues
        (``integration.failure_kind``), never by that status. The legacy test returned
        such a result from an autospec ``_apply_submission_bundles``; here the owner
        applies the real response: its output bundle is accepted and its insight
        bundle, whose evidence is the source changed during the call, is returned.
        """
        sim = Sim.activated()
        clear_work(sim)
        source = sim.root / 'basis.txt'
        source.write_text('old', encoding='utf-8')
        applied(sim, 'source', config={'path': str(source)})
        engine = sim.engine
        task(engine, 'TK-routing')
        queue_work(engine, 'TK-routing')
        only(sim, 'research_work')
        engine._save()
        model = currentness_model(sim, InsightWork())

        def changing(context, workspace):
            source.write_text('new', encoding='utf-8')
            await_applied(sim, sim.control('source', text='the source changed', config={'path': str(source)}))
        model.during('research_work', changing)
        model.reseal('research_work', split_extensions)
        with ObservedCalls(receipt=sim.engine._record_task_receipt) as observed:
            sim.step()
        execution = next(row for row in sim.runtime['executions'].values() if row['role'] == 'research_work')
        [accepted, returned] = execution['integration_result']['bundles']
        self.assertEqual(execution['integration_result']['status'], 'partial')
        self.assertEqual((accepted['status'], returned['status']), ('accepted', 'returned'))
        self.assertEqual([row['rule_id'] for row in returned['issues']], ['integration.currentness'])
        self.assertEqual(execution['error_kind'], 'currentness_changed')
        self.assertEqual([row['integration_id'] for row in execution['currentness_changes']], [returned['integration_id']])
        # The whole queue: the one refresh of this execution (not a repair), and the plan that assesses the
        # accepted report and reconsiders the preserved events (the source change); nothing twice.
        refreshed, plan = sorted(sim.runtime['queue'], key=lambda row: row['role'] != 'research_work')
        self.assertEqual((refreshed['role'], refreshed['continuation_of']), ('research_work', execution['id']))
        self.assertEqual(refreshed['refresh']['execution_id'], execution['id'])
        self.assertNotIn('repair', refreshed)
        self.assertEqual((plan['role'], plan['receipt_refs']), ('research_plan', [execution['id']]))
        self.assertIn('Assess accepted research report and knowledge', plan['reasons'])
        self.assertNotIn('repair', plan)
        self.assertNotIn(execution['action']['id'], sim.runtime.get('waiting_actions', {}))
        # The refresh records this execution's outcome once; the ordinary receipt is not recorded again.
        self.assertEqual(observed.calls['receipt'], [])


if __name__ == '__main__':
    unittest.main()

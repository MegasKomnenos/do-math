"""Recovery of research work through a model call: contract revision, rejected plans, diagnoses and their retries.

Each scene runs one model call through the worker (about 2 to 4 s, over the
2 s Sim budget); the scenes without a call are in
``sim/test_scheduling_research_recovery.py``. The owner runs on the Sim; the
model double answers each call
(``support.scheduling_model``: ``explicit`` is the legacy ``producer_result``
runner, ``explicit(mode="standalone", expected_receipt=None)`` a runner that returned its output without the
submission tool). The start states are the templates of
``support.scheduling_recovery`` or the default activation with
``max_output_repairs`` configured to 0.
"""
from copy import deepcopy
import json
import tempfile
import unittest
from pathlib import Path

from support.purpose_answers import common
from support.role_answers import candidate, disposition
from support.default_responder import DefaultResponder
from support.engine_lifecycle import applied
from support.scheduling_model import explicit, scenario_model
from support.scheduling_recovery import empty_plan, failed_execution, failed_plan_sim, reviewed_sim
from support.sim import Sim, warm_template


def setUpModule():
    warm_template()
    reviewed_sim()
    failed_plan_sim()


class RevisionResponder(DefaultResponder):
    """The default responder, resolving a preparation's declared revision targets as ``PurposeAnswers`` did."""

    def respond(self, role, ctx, workspace):
        out = super().respond(role, ctx, workspace)
        targets = ctx['action'].get('revision_targets')
        if role == 'research_preparation' and targets:
            path = Path(workspace) / 'activity-extensions.json'
            extensions = json.loads(path.read_bytes()) if path.exists() else {}
            revised = {row.get('revises_task_id') for row in out.get('candidates', [])}
            extensions['revision_resolutions'] = [{'record_id': identifier,
                'disposition': 'revised' if identifier in revised else 'deferred',
                'reason': 'The fixture replaces this contract.' if identifier in revised
                else 'The fixture preserves this remaining obligation.'} for identifier in targets]
            path.write_text(json.dumps(extensions), encoding='utf-8')
        return out


def queued(sim, action_id):
    return action_id in [row.get('id') for row in sim.runtime['queue']]


class ReviewedTaskTests(unittest.TestCase):
    """One task a real contract review approved, and the plan it opened (``reviewed_sim``)."""

    def setUp(self):
        self.sim = reviewed_sim()
        self.engine = self.sim.engine

    def test_revised_contract_replaces_obsolete_criteria_and_preserves_history(self):
        engine = self.engine
        old = deepcopy(next(iter(engine.runtime['tasks'].values())))
        self.assertTrue(old['reviews'])
        proposal = candidate(old['title'], revises=old['id'])
        proposal['completion_obligations'][0]['claim'] = 'Report the base construction and each property separately.'
        proposal['scope'] = {'included': ['The base construction'], 'excluded': ['Variants']}
        scenario_model(self.sim, RevisionResponder(preparation_candidates=[proposal]))
        engine.runtime['queue'] = []
        engine._enqueue('research_preparation', old['id'], id='AC-revision')
        engine._save()
        self.sim.step()
        revised = next(ex for ex in self.sim.runtime['executions'].values() if ex.get('action', {}).get('id') == 'AC-revision')
        self.assertEqual(revised['outcome'], 'output_accepted', {'error': revised.get('error'),
            'integration_result': revised.get('integration_result'), 'waiting_actions': self.sim.runtime.get('waiting_actions')})
        current = self.sim.runtime['tasks'][old['id']]
        self.assertEqual(current['completion_obligations'], proposal['completion_obligations'])
        self.assertEqual(current['revision_history'][-1]['completion_obligations'], old['completion_obligations'])
        self.assertEqual(current['reviews'], [])
        self.assertEqual(current['revision'], old['revision'] + 1)
        self.assertEqual(current['status'], 'planned')
        self.assertEqual(engine._governance()['goal_revision'], 1)

    def test_plan_rejection_names_missing_unexpected_and_duplicate_ids(self):
        engine = self.engine
        engine._refresh_readiness()
        ready_id = next(tid for tid, row in engine._task_readiness.items() if row['state'] == 'ready')
        engine.runtime['queue'] = [next(a for a in engine.runtime['queue'] if a['role'] == 'research_plan')]
        plan = engine.runtime['queue'][0]
        model = scenario_model(self.sim)
        model.on('research_plan').reply(explicit(empty_plan(dispositions=[
            disposition('TK-absent'), {**disposition('TK-absent'), 'reason': 'A distinct row with the same invalid task ID'}]), expected_receipt='rejected', returncode=1))
        engine._save()
        self.sim.step()
        # The rejection the producer receives names every population error (the legacy runner's
        # failure, stored as the wait's reason, quoted this receipt).
        receipt, = model.receipts
        self.assertEqual(receipt['state'], 'rejected')
        message = json.dumps(receipt)
        for expected in ('missing', ready_id, 'unexpected', 'TK-absent', 'duplicate'):
            self.assertIn(expected, message)
        wait = self.sim.runtime['waiting_actions'][plan['id']]
        self.assertEqual(wait['kind'], 'execution_failure')
        # The central check the engine preserved for the failed plan says the same.
        check_ref, = [ref for event in self.sim.runtime['events'] if event['kind'] == 'submission_checked'
                      and event.get('target') == wait['execution_id'] for ref in event['evidence_refs']]
        issues = json.loads(engine.store.read(check_ref, engine.head))['issues']
        self.assertIn(f"missing=['{ready_id}']; unexpected=['TK-absent']; duplicate=['TK-absent']",
                      json.dumps([row['message'] for row in issues]))


class InvalidPlanTests(unittest.TestCase):
    """The default activation with ``max_output_repairs`` 0, applied by a public ``configure``."""

    def setUp(self):
        self.sim = Sim.activated()
        applied(self.sim, 'configure', config={'max_output_repairs': 0})
        self.model = scenario_model(self.sim)

    def test_exhausted_output_repair_does_not_stop_unrelated_work(self):
        # An invalid final response must reach the receiver: the model answers it as its
        # final message, without the submission tool, so no producer check stops it first.
        self.model.on('research_plan').reply(explicit(empty_plan(dispositions=[disposition('TK-absent')]), mode='standalone', expected_receipt=None))
        self.sim.engine.runtime['queue'] = [{'id': 'AC-bad-plan', 'role': 'research_plan'},
                                            {'id': 'AC-independent', 'role': 'research_preparation'}]
        self.sim.engine._save()
        self.sim.step()
        self.assertEqual(self.sim.runtime['status'], 'ready')
        self.assertTrue(queued(self.sim, 'AC-independent'))
        self.assertIn('AC-bad-plan', self.sim.runtime['waiting_actions'])
        failure = self.sim.runtime['waiting_actions']['AC-bad-plan']
        self.assertEqual(failure.get('kind'), 'output_validation')
        self.assertIn(failure.get('execution_id'), self.sim.runtime['executions'])

    def test_output_failure_opens_diagnosis_without_replaying_rejected_plan(self):
        from support.cross_contracts import assert_call_records
        self.model.on('research_plan').reply(explicit(empty_plan(dispositions=[disposition('TK-absent')]), expected_receipt='rejected', returncode=1))
        self.sim.engine.runtime['queue'] = [{'id': 'AC-invalid', 'role': 'research_plan'}]
        self.sim.engine._save()
        self.sim.step()
        self.assertTrue(any(a['role'] == 'operational_review' for a in self.sim.runtime['queue']))
        self.assertFalse(queued(self.sim, 'AC-invalid'))
        before = assert_call_records(self, self.sim)
        failed = next(row for row in self.sim.runtime['executions'].values()
                      if row['action']['id'] == 'AC-invalid')
        self.sim.run_until(lambda sim: any(c['role'] == 'operational_review' for c in sim.model.calls), max_steps=8)
        after = assert_call_records(self, self.sim)
        self.assertEqual(after['operational_review'] - before['operational_review'], 1, self.sim.waiting())
        self.assertEqual(sum(c['action']['id'] == 'AC-invalid' for c in self.sim.model.calls), 1)
        review, = [row for row in self.sim.runtime['executions'].values() if row['role'] == 'operational_review']
        self.assertEqual(review['action']['target'], failed['id'])
        self.assertEqual(review['outcome'], 'output_accepted', review.get('error'))
        self.sim.step()
        self.sim.step()
        self.assertEqual(assert_call_records(self, self.sim)['operational_review'], after['operational_review'])
        self.assertEqual(sum(c['action']['id'] == 'AC-invalid' for c in self.sim.model.calls), 1)

    def test_failed_operational_diagnosis_does_not_start_another_diagnosis(self):
        from support.cross_contracts import assert_call_records
        sim = failed_plan_sim()
        scenario_model(sim).on('operational_review').reply(explicit({}, expected_receipt='rejected', returncode=1))
        before = assert_call_records(self, sim)
        sim.run_until(lambda current: any(c['role'] == 'operational_review' for c in current.model.calls), max_steps=8)
        after = assert_call_records(self, sim)
        self.assertEqual(after['operational_review'] - before['operational_review'], 1,
                         {'queue': sim.runtime['queue'], 'waiting': sim.waiting()})
        review, = [row for row in sim.runtime['executions'].values() if row['role'] == 'operational_review']
        self.assertEqual(review['outcome'], 'execution_incomplete')
        self.assertIn(review['action']['id'], sim.runtime['waiting_actions'])
        self.assertFalse(any(a['role'] == 'operational_review' for a in sim.runtime['queue']))
        for _ in range(2):
            sim.step()
            self.assertEqual(assert_call_records(self, sim)['operational_review'], after['operational_review'])


class ParkedFailureTests(unittest.TestCase):
    """The rejected plan ``AC-failed`` parked in ``waiting_actions`` (``failed_plan_sim``)."""

    def setUp(self):
        self.sim = failed_plan_sim()
        self.engine = self.sim.engine
        self.failed = failed_execution(self.sim)
        self.model = scenario_model(self.sim)
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)

    def diagnose(self, kind='retry'):
        """One operational diagnosis of the failed plan: the model proposes a ``kind`` disposition."""
        proposal = {'kind': kind, 'basis_refs': [self.failed['id']], 'next_owner': 'research_plan',
                    'reason': 'Recompute the plan from the current task population.'}
        if kind == 'retry':
            proposal.update(scope='The rejected planning action', replay_safety='The rejected output was never applied')
        elif kind == 'repair':
            proposal.update(repair_target=self.failed['id'], meaning_preserving=True,
                            verification='Validate the fresh output against the current input and role schema')
        self.model.on('operational_review', id='AC-diagnose').reply(explicit({
            **common('Preserved failed output requires an explicit recovery disposition'), 'disposition': proposal}))
        self.engine.runtime['queue'].insert(0, {'id': 'AC-diagnose', 'role': 'operational_review', 'target': self.failed['id']})
        self.engine._save()
        from support.role_input_requirements import observe_judgment_inputs
        with observe_judgment_inputs(self) as prepared:
            self.sim.step()
        self.assertEqual(len([row for row in prepared if row['role'] == 'operational_review']), 1)


    def test_diagnosed_plan_retry_uses_fresh_input_and_preserves_failure_and_independent_work(self):
        preserved = deepcopy(self.failed)
        self.engine.runtime['queue'] = [{'id': 'AC-independent', 'role': 'research_preparation'}]
        self.diagnose()
        runtime = self.sim.runtime
        retries = [a for a in runtime['queue'] if a.get('continuation_of') == self.failed['id']]
        self.assertEqual(len(retries), 1)
        action = retries[0]
        # The request and owning activity persist; its next execution is fresh.
        self.assertEqual(action['role'], 'research_plan')
        self.assertEqual(action['id'], self.failed['action']['id'])
        self.assertNotIn('repair', action)
        self.assertNotIn('repair_attempt', action)
        context = self.engine._context(action, self.root / 'fresh-plan')
        self.assertEqual(context['ready_task_ids'], [])
        self.assertEqual(context['previous_execution']['id'], self.failed['id'])
        self.assertEqual(context['previous_execution']['outcome'], 'execution_incomplete')
        self.assertEqual(context['snapshot'], self.engine.head)
        self.assertEqual(action['recovery']['execution_id'], self.failed['id'])
        self.assertTrue(queued(self.sim, 'AC-independent'))
        self.assertEqual(self.sim.runtime['executions'][self.failed['id']], preserved)
        self.assertFalse(self.sim.runtime['questions'])

    def test_successful_fresh_plan_resolves_parked_failure_without_deleting_history(self):
        self.model.on('research_plan', id='AC-fresh').reply(explicit(empty_plan(), extensions={'action_resolutions': [
            {'action_id': 'AC-failed', 'evidence_execution_id': 'current',
             'reason': 'This current complete plan explicitly supersedes the old population judgment.'}]}))
        self.engine.runtime['queue'] = [{'id': 'AC-fresh', 'role': 'research_plan'}]
        self.engine._save()
        self.sim.step()
        runtime = self.sim.runtime
        self.assertNotIn('AC-failed', runtime['waiting_actions'])
        self.assertEqual(runtime['executions'][self.failed['id']]['outcome'], 'execution_incomplete')
        resolution = next(row for row in runtime['history'] if row.get('kind') == 'failed_action_explicitly_resolved')
        activity = runtime['activities'][self.failed['owner_activity_id']]
        self.assertEqual(activity['status'], 'finished')
        self.assertNotIn('waiting', activity)
        self.assertEqual(activity['unresolved'], [])
        self.assertIn(resolution['resolved_by'], activity['result_refs'])
        self.assertEqual(activity['followups'][0]['resolved_by'], resolution['resolved_by'])
        self.assertEqual(self.engine.store.load()[2]['activities'][activity['id']], activity)

    def test_diagnosis_wait_does_not_block_independent_actions(self):
        self.engine.runtime['queue'] = [{'id': 'AC-other', 'role': 'research_preparation'}]
        self.diagnose(kind='repair')
        self.assertEqual(self.sim.runtime['status'], 'ready')
        self.assertEqual(self.sim.runtime['queue'][0]['id'], 'AC-other')




class DelegatedRevisionPlanningTests(unittest.TestCase):
    def test_closed_delegate_returns_obligation_and_queues_one_replan(self):
        from support.planning_contract_inputs import relation_sim, delegated_revision, withdraw
        self.sim = relation_sim()
        self.engine = self.sim.engine
        self.parent, self.tid, self.kid = delegated_revision(self.sim)
        withdraw(self.sim, self.tid)
        entry = deepcopy(self.sim.runtime['waiting_actions'][self.parent])
        queue = deepcopy(self.sim.runtime['queue'])
        self.engine._reconcile_revision_delegations()
        expected = {**entry, 'delegated_targets': {}, 'delegation_history': [{'record_id': self.kid, 'task_id': self.tid}]}
        self.assertEqual(self.sim.runtime['waiting_actions'][self.parent], expected)
        # 기존 계획 요청은 합쳐지되 위임 반환 근거를 빠뜨리면 안 된다.
        existing = next(a for a in queue if a['role'] == 'research_plan')
        expected_queue = deepcopy(queue)
        expected_plan = next(a for a in expected_queue if a['id'] == existing['id'])
        reason = 'A delegated task ended or changed while its revision obligation remains: ' + self.parent
        reasons = list(existing.get('reasons', [existing['reason']] if existing.get('reason') else []))
        if reason not in reasons:
            reasons.append(reason)
        expected_plan.update(unbound_request=True, reasons=reasons, reason='\n'.join(reasons),
            revision_followup=[{'record_id': self.kid, 'task_id': self.tid}])
        self.assertEqual(self.sim.runtime['queue'], expected_queue)
        before = deepcopy(self.sim.runtime)
        self.engine._reconcile_revision_delegations()
        self.assertEqual(self.sim.runtime, before)
        self.engine._save()
        self.sim.restart()
        self.assertEqual(self.sim.runtime['waiting_actions'][self.parent], expected)

        from support.cross_contracts import assert_call_records
        from support.model import Answer
        sim = self.sim
        sim.model.responder = DefaultResponder(plan_assessments=False)
        def defer(out, context):
            for row in out['dispositions']:
                row.update(kind='not_selected', next_owner='research_plan',
                    revisit={'at': '2090-01-02T00:00:00+00:00', 'event_refs': []})
            return out
        sim.model.on('research_plan').reply(Answer(defer))
        before = assert_call_records(self, sim)
        request, = [a for a in sim.runtime['queue'] if a.get('revision_followup')]
        sim.advance(sim.instance['config']['plan_settle_seconds'] + 1)
        sim.run_until(lambda current: any(c['action']['id'] == request['id'] for c in current.model.calls), max_steps=8)
        self.assertEqual(assert_call_records(self, sim)['research_plan'] - before['research_plan'], 1)
        execution, = [row for row in sim.runtime['executions'].values() if row['action']['id'] == request['id']]
        self.assertEqual(execution['outcome'], 'output_accepted', execution.get('error'))
        self.assertEqual(execution['action']['revision_followup'], [{'record_id': self.kid, 'task_id': self.tid}])
        for _ in range(2):
            sim.step()
            self.assertEqual(sum(c['action'].get('revision_followup') == request['revision_followup']
                                 for c in sim.model.calls), 1)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[2], sim.runtime)


if __name__ == '__main__':
    unittest.main()

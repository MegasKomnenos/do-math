"""Stored task contracts survive the storage contract and a reload (``planning``, ``task_scope``,
``decision_engine``, ``repository``; layer 2), moved from ``test_task_contracts.TaskContractStorageTests``.

The legacy tests used a real Git repository (``git_init``) and, for the
receiver's currentness check, an engine without its constructor
(``bare_engine``). Here the store is the real ``ResearchRepository`` on the
in-process Git fake (``support.storage_records.record_store``), so every save
passes the installed storage contract, and the receiver is the real engine
loaded from that repository (``engine_on``). User decisions and AI judgments
stay synthetic, as they were.
"""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from do_math import governance, planning, task_contracts, task_scope
from do_math.configuration import DEFAULT_CONFIG
from do_math.execution_profiles import build_profiles, profile_ref, resolve_profile, select_profile
from do_math.input_basis import CurrentnessChanged
from support.record_builders import domain_governance
from support.role_answers import candidate, review_items
from support.state_builders import current_state
from support.fakes.clock import FakeClock
from support.fakes.git_backend import InProcessGit
from support.storage_records import engine_on, fake_ports, record_store


class TaskContractStorageTests(unittest.TestCase):
    """The installed storage contract over the Git port; synthetic user decisions and AI judgments."""

    def setUp(self):
        from support.entry import entry
        _entry = entry()
        temporary = tempfile.TemporaryDirectory(prefix='tasks-audit1-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.clock, self.backend = FakeClock(), InProcessGit()
        self.store = record_store(self.root / 'repository', backend=self.backend, clock=self.clock)
        # Stored states pass the current lifecycle gate; these tasks belong to an active instance.
        self.instance, self.runtime = current_state(
            {**domain_governance(), 'config': deepcopy(DEFAULT_CONFIG), **build_profiles(DEFAULT_CONFIG, host=_entry.ports.host)},
            {'status': 'ready', 'tasks': {}, 'executions': {}, 'queue': [], 'history': []})
        self.instance['lifecycle']['state'] = 'active'

    def execution(self, identifier, role):
        from do_math.activities import assign_execution, open_activity
        from do_math.execution_lifecycle import create_execution, transition_execution
        profile = next(p for p in self.instance['execution_profiles'].values() if p['role'] == role)
        activity_id = 'AT-' + identifier
        when = '2026-09-20T00:00:00Z'
        open_activity(self.runtime, activity_id=activity_id, activity_kind=role, owner_ref='engine', input_refs=[],
                      opened_at=when)
        execution = create_execution(execution_id=identifier, owner_activity_id=activity_id,
                                     actor_kind=profile['actor_kind'], input_manifest={}, profile_ref=profile_ref(profile),
                                     created_at=when)
        execution['role'] = role
        assign_execution(self.runtime, activity_id, execution)
        transition_execution(execution, 'starting', at=when)
        transition_execution(execution, 'running', at=when)
        return execution

    def candidate(self, identifier):
        from do_math.contracts import task_candidate_record
        wire = candidate()
        profile = next(p for p in self.instance['execution_profiles'].values()
                       if p['role'] == 'research_work' and p['ai']['tier'] == 'high')
        wire['profile_refs'] = [profile_ref(profile)]
        wire['authority_refs'] = ['GR-audit']
        task = task_candidate_record(wire, task_id=identifier)
        task.pop('revises_task_id')  # Transport target, not stored contract authority.
        task.update(status='planned', results=[], reviews=[])
        self.runtime['tasks'][identifier] = task
        return task, wire

    def grant(self):
        from support.entry import entry
        _entry = entry()
        self.instance, self.runtime, _ = governance.apply_decision(self.instance, self.runtime, {'kind': 'grant', 'grant': {
            'id': 'GR-audit', 'kind': 'local', 'roles': ['research_work'], 'reuse': 'reusable'}}, source_ref='S', clock=_entry.ports.clock)

    def review(self, identifier):
        eid = 'EX-review-' + identifier
        self.execution(eid, 'task_contract_review')
        task = self.runtime['tasks'][identifier]
        output = review_items(['S'])
        task['reviews'] = [planning.seal_contract_review(task, output, self.instance, self.runtime, execution_id=eid)]

    def test_candidate_review_profile_selection_and_governance_survive_git_reload(self):
        """About 0.15-0.3 s, over the 0.2 s unit budget in a full run: two publications and a refused one through the storage contract, and an engine load."""
        from support.entry import entry
        _entry = entry()
        self.grant()
        task, wire = self.candidate('TK-stored')
        self.review(task['id'])
        # The receiver is the real engine loaded from the first publication of this state.
        receiver, head = engine_on(self.store, self.instance, self.runtime, workspace=self.root / 'work',
                                   ports=fake_ports(self.clock, self.backend))
        _, instance, runtime = self.store.load(head)
        saved = runtime['tasks'][task['id']]
        self.assertEqual(saved['profile_refs'], wire['profile_refs'])
        self.assertNotIn('goal_revision', instance)
        self.assertNotIn('policy_revision', instance)
        self.assertEqual(saved['reviews'][0]['goal_revision'], governance.governance_view(instance)['goal_revision'])
        self.assertEqual(saved['reviews'][0]['policy_revision'], governance.governance_view(instance)['policy_revision'])
        selected = resolve_profile(instance['execution_profiles'], saved['profile_refs'][0])
        action = {'id': 'AC-dispatch', 'role': 'research_work', 'target': saved['id'], 'profile_ref': profile_ref(selected)}
        self.assertEqual(select_profile(instance['execution_profiles'], action, selected['ai'], saved['profile_refs'])['id'],
                         selected['id'])
        self.assertEqual(planning.task_ready(saved, instance, runtime, action=action, include_scheduling_waits=False, evaluation_context=receiver._evaluation_context())['state'],
                         'ready')
        bad = deepcopy(runtime)
        bad['tasks'][saved['id']]['profile_refs'][0]['revision'] += 1
        with self.assertRaisesRegex(ValueError, '^profile reference is absent or stale$'):
            self.store.save_with_state(head, instance, bad)
        self.assertEqual(self.store.load()[0], head)
        # Receipt currentness reads the same persisted governance as review/dispatch.
        self.assertEqual((receiver.instance, receiver.runtime), (instance, runtime))
        receipt = {'input_snapshot': head, 'contract_sha256': planning.contract_hash(saved),
                   **planning.governance_revisions(instance)}
        review_action = {'role': 'task_contract_review', 'target': saved['id']}
        output = {'item_reviews': deepcopy(saved['reviews'][0]['item_reviews'])}
        receiver._validate_decision_acceptance(review_action, output, receipt, {}, evaluation_context=receiver._evaluation_context())
        policy = {'id': 'POL-persisted', 'kind': 'policy', 'revision': 1, 'supersedes': [],
                  'content': {'rule_id': 'persisted', 'scope': ['P'], 'text': 'Require an explicit domain',
                              'reason_refs': ['D'], 'audit_refs': []}}
        receiver.instance, receiver.runtime, _ = governance.apply_decision(instance, runtime, {'kind': 'policy', 'record': policy},
                                                                           source_ref='S', clock=_entry.ports.clock)
        changed_head = self.store.save_with_state(head, receiver.instance, receiver.runtime)[0]
        _, receiver.instance, receiver.runtime = self.store.load(changed_head)
        with self.assertRaises(CurrentnessChanged) as changed:
            receiver._validate_decision_acceptance(review_action, output, receipt, {}, evaluation_context=receiver._evaluation_context())
        self.assertIn('goal_or_policy_revision', [row['field'] for row in changed.exception.changes])
        self.assertFalse(planning.contract_review_current(saved['reviews'][0], saved, receiver.instance,
                                                          receiver.runtime)['valid'])

    def test_transfer_closes_without_completion_and_recipient_obligation_survives_reload(self):
        """About 0.15-0.3 s, over the 0.2 s unit budget in a full run: two publications and a refused one through the storage contract."""
        from support.entry import entry
        _entry = entry()
        self.grant()
        source, _ = self.candidate('TK-source')
        target, _ = self.candidate('TK-target')
        self.execution('EX-plan', 'research_plan')
        source.update(status='waiting', results=[{'id': 'EV-work', 'report': 'remaining work identified'}])
        self.instance, self.runtime, decision = governance.apply_decision(self.instance, self.runtime, {
            'kind': 'task_scope', 'task_id': source['id'], 'revision': source['revision'],
            'contract_sha256': planning.contract_hash(source), 'disposition': 'transfer',
            'reason': 'move the exact remaining obligation',
            'obligation_ids': [source['completion_obligations'][0]['id']], 'target_task_id': target['id']}, source_ref='S', clock=_entry.ports.clock)
        head = self.store.initialize(self.instance, self.runtime)
        _, instance, runtime = self.store.load(head)
        assessment = {'task_id': source['id'], 'decision': 'closed', 'reason': 'authorized transfer, not fulfillment',
                      'item_dispositions': [{'obligation_id': source['completion_obligations'][0]['id'], 'kind': 'transferred',
                                             'authority_ref': decision['id'], 'target_task_id': target['id'],
                                             'target_obligation_id': 'OB-inherited', 'evidence_refs': []}],
                      'unresolved': []}
        instance, runtime = task_scope.apply_task_assessments(instance, runtime, [assessment], execution_id='EX-plan',
                                                              input_tasks=deepcopy(runtime['tasks']), clock=_entry.ports.clock)
        saved_head = self.store.save_with_state(head, instance, runtime)[0]
        _, instance, runtime = self.store.load(saved_head)
        original, recipient = runtime['tasks'][source['id']], runtime['tasks'][target['id']]
        self.assertEqual(original['status'], 'closed')
        self.assertEqual(recipient['revision'], 2)
        self.assertTrue(task_scope.assessment_current(original, instance, runtime))
        self.assertEqual(recipient['completion_obligations'][-1]['id'], 'OB-inherited')
        # Neither persisted state nor the completion consumer may relabel transfer as fulfillment.
        bad = deepcopy(runtime)
        bad['tasks'][source['id']]['status'] = 'completed'
        bad['tasks'][source['id']]['assessment']['decision'] = 'completed'
        with self.assertRaisesRegex(ValueError, 'completed.*transferred'):
            self.store.save_with_state(saved_head, instance, bad)
        self.assertFalse(task_scope.assessment_current(bad['tasks'][source['id']], instance, bad))
        self.assertEqual(self.store.load()[0], saved_head)
        omitted = {'task_id': target['id'], 'decision': 'completed', 'item_dispositions': [
            {'obligation_id': recipient['completion_obligations'][0]['id'], 'kind': 'fulfilled', 'evidence_refs': []}],
            'unresolved': []}
        with self.assertRaisesRegex(ValueError, 'every obligation'):
            task_contracts.validate_item_dispositions(recipient, omitted, require_complete=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)

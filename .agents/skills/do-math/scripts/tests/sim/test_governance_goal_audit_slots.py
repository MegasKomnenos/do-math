"""Goal audit slots and their seals (``governance_engine``, layer 2; recovery in ``core_engine``), moved from ``test_goal_audit``.

The legacy tests ran the goal audit mixin on an engine built without its
constructor (``research_fixtures.bare_engine``) and replaced its goal basis
(``_goal_basis_key``, an autospec answering ``'basis'``). Here the engine is a
restored Sim's and the basis is the one the engine computes: ``host()`` sets
two goal auditors and empties the families the legacy host started empty, and
every slot names ``engine._goal_basis_key()``.

The recovery test starts from a goal audit sealed on the real engine and
published under the storage contract (``support.governance_goal_seal``), and
recovers it in a new owner process: the Jobs port answers whether the launch
owner ended, where the legacy test patched ``named_job_empty`` and
``owner_ended``. Its first recovery finds a ticket whose owner the port cannot
report ended, where the legacy execution had no ticket, a state the storage
contract rejects (see the helper). The calls to ``context_store.collect_outputs`` and
``_preserve_outputs`` are observed, where the legacy test made
``collect_outputs`` raise. The last-slot test takes its goal auditors from
``support.governance_sim`` (a user-adopted additional audit ``AU`` answered
``partial``) instead of ``engine_fixtures.goal_audit_host``.
"""
from copy import deepcopy
import unittest

from do_math import context_store
from do_math.activities import assign_execution, open_activity
from do_math.engine import ResearchEngine
from support.engine_lifecycle import ObservedCalls, code_of
from support.governance_goal_seal import EXECUTION, INPUT_BUNDLE, RESULT_REF, committed_goal_audit
from support.governance_sim import adopt_audit, goal_auditor
from support.sim import Sim, warm_template

setUpModule = warm_template
SLOT_RANGE = '^goal audit requires a positive count and an in-range integer slot$'
NO_RECEIPT = '^goal audit seal lacks its original integration receipt$'


def host():
    """``(engine, basis)``: a restored Sim's engine with two goal auditors, no judgment and empty work families."""
    engine = Sim.activated().engine
    engine.instance['config']['goal_auditors'] = 2
    engine.instance['goal_judgments'] = []
    engine.runtime.update(executions={}, queue=[], waiting_actions={}, history=[], events=[], pending_events=[],
                          tasks={}, activities={}, reservations={})
    return engine, engine._goal_basis_key()


def seal(engine, basis, slot=0, **changes):
    """``(action, judgment)``: slot ``slot`` sealed by ``EX-original``, which ended with its output accepted."""
    action = {'id': 'AC-original', 'role': 'goal_audit', 'basis': basis, 'required': 2, 'slot': slot}
    engine.runtime['executions']['EX-original'] = {'id': 'EX-original', 'role': 'goal_audit',
        'action': action, 'status': 'ended', 'outcome': 'output_accepted'}
    judgment = {'id': 'GJ-one', 'basis': basis, 'required': 2, 'slot': slot,
                'execution_id': 'EX-original', 'current': True, **changes}
    engine.instance['goal_judgments'].append(judgment)
    return action, judgment


class GoalAuditSlotTests(unittest.TestCase):
    def test_only_missing_slots_are_enqueued_and_consumed_event_is_not_repended(self):
        e, basis = host()
        _, j = seal(e, basis)
        first = e._ensure_goal_audit_requests(basis, 'EX-plan')
        self.assertEqual([s['state'] for s in first['slots']], ['sealed', 'queued_new'])
        queued = deepcopy(e.runtime['queue'])
        second = e._ensure_goal_audit_requests(basis, 'EX-plan2')
        self.assertEqual([s['state'] for s in second['slots']], ['sealed', 'queued'])
        self.assertEqual(e.runtime['queue'], queued)
        event = e._record_goal_audit_followup(basis, [j])
        e.runtime['pending_events'].remove(event)
        self.assertEqual(e._record_goal_audit_followup(basis, [j]), event)
        self.assertEqual(e.runtime['pending_events'], [])
        j['current'] = False
        self.assertEqual(e._ensure_goal_audit_requests(basis, 'EX-plan3')['slots'][0]['state'], 'sealed_unusable')

    def test_owned_slot_wait_is_preserved(self):
        e, basis = host()
        actions = [{'id': f'AC-{s}', 'role': 'goal_audit', 'basis': basis, 'slot': s, 'required': 2} for s in range(2)]
        e.runtime['executions']['EX-live'] = {'id': 'EX-live', 'status': 'running', 'action': actions[0]}
        e.runtime['waiting_actions']['AC-1'] = {'action': actions[1], 'kind': 'submission_failure', 'next_owner': 'engine'}
        self.assertEqual([r['state'] for r in e._ensure_goal_audit_requests(basis, 'EX-plan')['slots']],
                         ['running', 'waiting'])
        self.assertEqual(e.runtime['queue'], [])

    def test_original_publication_and_reservations_are_protected_from_duplicate_cleanup(self):
        e, basis = host()
        action, j = seal(e, basis)
        e.runtime['executions']['EX-original']['outcome'] = 'execution_incomplete'
        duplicate = {**action, 'id': 'AC-duplicate'}
        held = {**action, 'id': 'AC-held'}
        e.runtime['executions']['EX-held'] = {'id': 'EX-held', 'action': held, 'status': 'ended'}
        e.runtime['reservations']['RS-held'] = {'owner_id': 'EX-held', 'state': 'held'}
        e.runtime['queue'] = [action, duplicate, held]
        e.runtime['waiting_actions'] = {a['id']: {'action': a, 'kind': 'submission_publication',
            'execution_id': 'EX-original' if a is action else 'EX-duplicate'} for a in (action, duplicate)}
        self.assertTrue(e._retire_sealed_goal_audit_requests())
        self.assertEqual([a['id'] for a in e.runtime['queue']], ['AC-original', 'AC-held'])
        self.assertEqual(list(e.runtime['waiting_actions']), ['AC-original'])
        self.assertFalse(e._retire_sealed_goal_audit_requests())
        self.assertIsNone(e._obsolete_action_reason(action, execution_id='EX-original'))
        self.assertIn('sealed', e._obsolete_action_reason(action, execution_id='EX-other'))

    def test_committed_seal_requires_original_execution_and_output_receipt(self):
        e, basis = host()
        _, j = seal(e, basis)
        with self.assertRaisesRegex(ValueError, NO_RECEIPT):
            e._committed_goal_audit('EX-original')
        e.runtime['integrations'] = {'IB-one': {'execution_id': 'EX-original', 'members': ['output']}}
        self.assertEqual(e._committed_goal_audit('EX-original'), j)
        # The execution's slot finds no seal of its own, so the recorded judgment is not its seal.
        e.runtime['executions']['EX-original']['action']['slot'] = 1
        with self.assertRaisesRegex(ValueError, NO_RECEIPT):
            e._committed_goal_audit('EX-original')

    def test_duplicate_retirement_preserves_evidence_and_other_activity_obligations(self):
        for other_obligation in (False, True):
            with self.subTest(other_obligation=other_obligation):
                e, basis = host()
                original, judgment = seal(e, basis, current=False)
                action = {**original, 'id': 'AC-duplicate', 'owner_activity_id': 'AT-duplicate'}
                activity = open_activity(e.runtime, activity_id='AT-duplicate', activity_kind='goal_audit',
                    owner_ref='IN-1', input_refs=[], opened_at='2026-09-23T00:00:00Z')
                assign_execution(e.runtime, activity['id'], {'id': 'EX-duplicate', 'role': 'goal_audit',
                    'owner_activity_id': activity['id'], 'action': action, 'status': 'ended',
                    'outcome': 'execution_incomplete'})
                activity.update(result_refs=['preserved-result'], unresolved=[{'action_id': action['id'], 'reason': 'failed'}])
                if other_obligation:
                    activity['followups'] = [{'reason': 'another outstanding obligation'}]
                before = deepcopy(activity)
                e.runtime['queue'] = [action]
                e._retire_sealed_goal_audit_requests()
                self.assertEqual(activity['result_refs'], before['result_refs'])
                self.assertEqual(e.runtime['executions']['EX-duplicate']['outcome'], 'execution_incomplete')
                if other_obligation:
                    self.assertEqual(activity, before)
                else:
                    self.assertEqual(activity['status'], 'finished')
                    self.assertIn(before['unresolved'][0], activity['unresolved'])
                    self.assertTrue(any(row.get('judgment_id') == judgment['id'] for row in activity['unresolved']))

    def test_last_slot_emits_one_event_and_invalid_slot_changes_nothing(self):
        sim = Sim.activated()
        adopt_audit(sim)
        e = sim.engine
        self.assertEqual(e.instance['goal_judgments'], [])
        action, output = goal_auditor(e)  # answers AU partial; this instance holds no usable knowledge
        action['required'] = 2
        e.runtime['executions']['AUDITOR']['action'] = deepcopy(action)
        events, pending = deepcopy(e.runtime['events']), deepcopy(e.runtime['pending_events'])
        first = e._apply_governance_goal_audit(action, output, 'AUDITOR')
        self.assertEqual(e.runtime['events'], events)
        self.assertEqual(e.runtime['pending_events'], pending)
        before = deepcopy(e.instance)
        for slot in (True, -1, 2):
            with self.assertRaisesRegex(ValueError, SLOT_RANGE):
                e._apply_governance_goal_audit({**action, 'slot': slot}, output, 'AUDITOR')
            self.assertEqual(e.instance, before)
        e.runtime['executions']['AUDITOR2'] = {**deepcopy(e.runtime['executions']['AUDITOR']), 'id': 'AUDITOR2'}
        second = e._apply_governance_goal_audit({**action, 'slot': 1}, output, 'AUDITOR2')
        self.assertEqual(e.instance['goal_judgments'], [first, second])
        (event,) = e.runtime['events'][len(events):]
        self.assertEqual((event['kind'], event['judgment_ids']), ('goal_audit_completed', sorted([first['id'], second['id']])))
        self.assertEqual(e.runtime['pending_events'], pending + [event['id']])


class SealRecoveryTests(unittest.TestCase):
    def recover(self, engine):
        """Run the owner's recovery of disappeared executions; return the calls that would recollect output files."""
        with ObservedCalls(collect=code_of(context_store.collect_outputs),
                           preserve=code_of(ResearchEngine._preserve_outputs)) as observed, engine.store.writer_lock():
            engine._recover_disappeared()
        return observed.calls

    def test_recovery_confirms_termination_before_using_original_seal_without_recollection(self):
        sim = Sim.activated()
        action, _ = committed_goal_audit(sim)
        local_owner = sim.jobs.owner_identity()
        # A different owner's persisted launch has no observed termination yet.
        execution = sim.runtime['executions'][EXECUTION]
        execution['launch_ticket']['owner'] = {**local_owner, 'pid': local_owner['pid'] + 10000}
        sim.engine._save()
        sim.restart()
        self.assertIs(sim.jobs.owner_ended(local_owner), True)
        engine = sim.engine
        self.assertEqual(engine.runtime.get('waiting_actions', {}), {})
        # The port cannot tell whether the previous owner ended, so no local termination is established.
        previous = engine.runtime['executions'][EXECUTION]['launch_ticket']['owner']
        self.assertIsNone(sim.jobs.owner_ended(previous))
        self.assertEqual(self.recover(engine), {'collect': [], 'preserve': []})
        execution = engine.runtime['executions'][EXECUTION]
        self.assertEqual(execution['status'], 'stopping')
        self.assertEqual(engine.runtime.get('waiting_actions', {}), {})
        # External process inspection now confirms the same launch owner ended.
        sim.jobs.known_ended.append(dict(previous))
        self.assertEqual((sim.jobs.owner_ended(execution['launch_ticket']['owner']),
                          sim.jobs.named_job_empty(execution['launch_ticket']['job_name'])), (True, True))
        self.assertEqual(self.recover(engine), {'collect': [], 'preserve': []})
        execution = engine.runtime['executions'][EXECUTION]
        self.assertEqual(execution['status'], 'ended')
        self.assertEqual(execution['result_ref'], RESULT_REF)
        self.assertEqual(execution['input_bundle'], INPUT_BUNDLE)
        self.assertEqual(engine.runtime['waiting_actions'][action['id']]['kind'], 'submission_publication')


if __name__ == '__main__':
    unittest.main()

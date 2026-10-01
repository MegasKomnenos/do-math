"""Applying a plan's task assessments (``task_scope``, ``task_contracts``, ``planning``; layer 2),
moved from ``test_task_contracts.AssessmentApplicationTests``.

The tests call the product's pure functions on the plain records of
``record_fixtures``: ``transfer_assessment`` (``TK-1`` returned result ``EV-1``;
the user decision ``DC-1`` transfers ``OB-2`` to the planned ``TK-2``; the
assessment fulfils ``OB-1`` and transfers ``OB-2``) and ``specialist_assessment``
(``TK-1`` owns a verified theorem and one certification obligation judged by a
specialist). ``apply_assessment`` runs ``task_scope.apply_task_assessments`` as
the plan ``EX-plan``. Nothing of the product is replaced. Rejections the legacy
tests checked by exception type alone now pin the product's message.
"""
from copy import deepcopy
import unittest

from do_math import planning, task_contracts
from support.record_builders import apply_assessment, approve_task, approved_task, specialist_assessment, task_disposition, transfer_assessment

CURRENT_DECISION = '^scope disposition requires a current source-bound user decision$'
NO_JUDGMENT = '^fulfilled obligation needs its designated judge or a current specialist judgment for this task$'


class AssessmentApplicationTests(unittest.TestCase):
    def test_transfer_binds_receiving_contract_and_blocks_incomplete_recipient_completion(self):
        i, r, a = transfer_assessment()
        previous = deepcopy(r)
        _, changed = apply_assessment(i, r, a)
        self.assertEqual(r, previous)
        self.assertEqual(changed['tasks']['TK-1']['status'], 'closed')
        recipient = changed['tasks']['TK-2']
        self.assertEqual(recipient['revision'], 2)
        self.assertEqual(recipient['reviews'], [])
        self.assertEqual(recipient['completion_obligations'][-1]['id'], 'OB-inherited')
        self.assertEqual(recipient['completion_obligations'][-1]['claim'], r['tasks']['TK-1']['completion_obligations'][1]['claim'])
        recipient['results'] = [{'id': 'EV-1'}]
        incomplete = {'task_id': 'TK-2', 'decision': 'completed', 'item_dispositions': [
            {'obligation_id': 'OB-1', 'kind': 'fulfilled', 'evidence_refs': ['EV-1']},
            {'obligation_id': 'OB-2', 'kind': 'fulfilled', 'evidence_refs': []}], 'unresolved': []}
        with self.assertRaisesRegex(ValueError, 'every obligation'):
            apply_assessment(i, changed, incomplete)

    def test_bare_unrelated_or_changed_authority_cannot_transfer(self):
        # A missing, changed-source or grant authority is not a current user decision; a decision for
        # another recipient or contract edition names its own mismatch (task_scope.validate_disposition_authority).
        mutations = [('no decision', lambda i, r, a: i['decisions'].clear(), CURRENT_DECISION),
                     ('other recipient', lambda i, r, a: i['decisions']['DC-1']['change'].update(target_task_id='TK-other'),
                      '^transfer authority names a different recipient$'),
                     ('other edition', lambda i, r, a: i['decisions']['DC-1']['change'].update(revision=2),
                      '^scope authority applies to a different contract edition$'),
                     ('changed source', lambda i, r, a: i['decisions']['DC-1'].update(source_sha256='b' * 64), CURRENT_DECISION),
                     ('grant authority', lambda i, r, a: a['item_dispositions'][1].update(authority_ref='GR-1'), CURRENT_DECISION)]
        for name, mutation, reason in mutations:
            with self.subTest(mutation=name):
                i, r, a = transfer_assessment()
                mutation(i, r, a)
                before = deepcopy((i, r))
                with self.assertRaisesRegex(ValueError, reason):
                    apply_assessment(i, r, a)
                self.assertEqual((i, r), before)

    def test_changed_decision_source_invalidates_scope_assessment_and_decision_condition(self):
        from do_math.task_scope import assessment_current
        instance, runtime, assessment = transfer_assessment()
        instance['decisions']['DC-1']['change']['value'] = 'continue'
        instance, runtime = apply_assessment(instance, runtime, assessment)
        source = runtime['tasks']['TK-1']
        condition = {'op': 'decision_value_is', 'decision_id': 'DC-1', 'value': 'continue'}
        context = {'task_id': source['id']}
        self.assertTrue(assessment_current(source, instance, runtime))
        self.assertEqual(planning.evaluate_condition(condition, instance, runtime, evaluation_context=context)['state'], 'ready')
        instance['decisions']['DC-1']['source_sha256'] = 'b' * 64
        self.assertFalse(assessment_current(source, instance, runtime))
        self.assertEqual(planning.evaluate_condition(condition, instance, runtime, evaluation_context=context)['state'],
                         'not_ready')
        self.assertEqual(source['status'], 'closed')

    def test_waiver_is_a_scope_decision_not_missing_evidence(self):
        i, r, a = transfer_assessment()
        a['item_dispositions'][1] = {'obligation_id': 'OB-2', 'kind': 'waived', 'evidence_refs': [], 'authority_ref': 'DC-1'}
        a['decision'] = 'completed'
        i['decisions']['DC-1']['change']['disposition'] = 'waive'
        _, changed = apply_assessment(i, r, a)
        self.assertEqual(changed['tasks']['TK-1']['status'], 'completed')
        self.assertEqual(changed['tasks']['TK-2']['revision'], 1)

    def test_unresolved_inspection_preserves_missing_input_and_owner(self):
        i, r, a = transfer_assessment()
        a.update(decision='incomplete')
        a['item_dispositions'] = a['item_dispositions'][1:]
        a['unresolved'] = [{'obligation_id': 'OB-1', 'missing_inputs': ['EV-1'], 'next_owner': 'research_work'}]
        _, changed = apply_assessment(i, r, a)
        self.assertEqual(changed['tasks']['TK-1']['waiting']['target_refs'], ['EV-1'])
        self.assertEqual(changed['tasks']['TK-1']['waiting']['next_owner'], 'research_work')
        self.assertEqual(task_contracts.returned_task_ids(changed['tasks']), [])

    def test_missing_assessment_input_arrival_reopens_assessment_without_new_work(self):
        from do_math.task_scope import refresh_task_assessments
        for reference in ('SO-new', 'new.txt', 'source:new.txt', 'sources/new.txt'):
            with self.subTest(reference=reference):
                i, r, a = transfer_assessment()
                a.update(decision='incomplete')
                a['item_dispositions'] = a['item_dispositions'][1:]
                a['unresolved'] = [{'obligation_id': 'OB-1', 'missing_inputs': [reference], 'next_owner': 'research_work'}]
                i, r = apply_assessment(i, r, a)
                results = deepcopy(r['tasks']['TK-1']['results'])
                self.assertFalse(task_contracts.returned_task_ids(r['tasks']))
                i['sources'].append({'id': 'SO-other', 'name': 'other.txt', 'path': 'sources/other.txt', 'sha256': 'c' * 64})
                self.assertEqual(refresh_task_assessments(i, r), [])
                self.assertTrue(r['tasks']['TK-1']['assessment']['current'])
                i['sources'].append({'id': 'SO-new', 'name': 'new.txt', 'path': 'sources/new.txt', 'sha256': 'b' * 64})
                self.assertEqual(refresh_task_assessments(i, r), ['TK-1'])
                self.assertEqual(task_contracts.returned_task_ids(r['tasks']), ['TK-1'])
                self.assertEqual(r['tasks']['TK-1']['results'], results)

    def test_plan_covers_every_ready_and_returned_task_and_rejects_double_disposition(self):
        i, r, a = transfer_assessment()
        plan = {'dispositions': [], 'task_assessments': [a]}
        planning.validate_plan_submission(plan, r['tasks'], [])
        for name, plan, ready, reason in [
                ('returned task not assessed', {'dispositions': [], 'task_assessments': []}, [],
                 '^plan must assess every returned task exactly once$'),
                ('ready task not disposed', {'dispositions': [], 'task_assessments': [a]}, ['TK-2'],
                 r"^plan must dispose every derived-ready task exactly once: missing=\['TK-2'\]; unexpected=\[\]; duplicate=\[\]$"),
                ('double disposition', {'dispositions': [task_disposition('TK-2')] * 2, 'task_assessments': [a]}, ['TK-2'],
                 r"^plan must dispose every derived-ready task exactly once: missing=\[\]; unexpected=\[\]; duplicate=\['TK-2'\]$"),
                ('disposition and assessment', {'dispositions': [task_disposition('TK-1')], 'task_assessments': [a]}, ['TK-1'],
                 '^returned tasks require disposition before a later selection$')]:
            with self.subTest(case=name), self.assertRaisesRegex(ValueError, reason):
                planning.validate_plan_submission(plan, r['tasks'], ready)

    def test_incomplete_open_work_is_available_for_a_later_continuation_plan(self):
        from support.entry import entry
        _entry = entry()
        i, r, a = transfer_assessment()
        t = r['tasks']['TK-1']
        t['waiting'] = {'kind': 'assessment', 'next_owner': 'research_plan'}
        approve_task(t, i, r)
        a.update(decision='incomplete', item_dispositions=[{'obligation_id': 'OB-1', 'kind': 'open', 'evidence_refs': []},
                                                          {'obligation_id': 'OB-2', 'kind': 'open', 'evidence_refs': []}])
        i, r = apply_assessment(i, r, a)
        self.assertEqual(planning.task_ready(r['tasks']['TK-1'], i, r, evaluation_context={'now': _entry.ports.clock.now(), 'host_id': _entry.host_id})['state'], 'ready')
        self.assertTrue(any(q['role'] == 'research_plan' for q in r['queue']))

    def test_nonselection_revisit_is_an_actual_machine_event(self):
        t, i, r = approved_task()
        t['selection_disposition'] = {**task_disposition(t['id'], 'not_selected'), 'execution_id': 'EX-plan',
                                      'revisit': {'at': '2026-09-20T00:00:00Z', 'event_refs': []}}
        events = planning.collect_due_events(i, r, '2026-09-20T00:00:01Z')
        self.assertTrue(any(e['kind'] == 'task_revisit_due' and e['target'] == t['id'] for e in events))

    def test_planner_can_aggregate_the_tasks_current_specialist_receipt(self):
        for judge in ('identity_review', 'formal_check'):
            with self.subTest(judge=judge):
                instance, runtime, assessment, _, _ = specialist_assessment(judge)
                _, changed = apply_assessment(instance, runtime, assessment)
                self.assertEqual(changed['tasks']['TK-1']['status'], 'completed')

    def test_foreign_stale_or_cycle_only_receipt_does_not_authorize_completion(self):
        for mutation, reason in (('foreign', NO_JUDGMENT), ('suspended', NO_JUDGMENT),
                                 ('cycle', r"^fulfilled obligation OB-certification needs its designated judge "
                                           r"\['identity_review'\] or cited evidence of the family \['identity-assessment'\]$"),
                                 ('changed_exposition', NO_JUDGMENT)):
            with self.subTest(mutation=mutation):
                instance, runtime, assessment, kid, aid = specialist_assessment()
                if mutation == 'foreign':
                    instance['knowledge'][kid]['task_id'] = 'TK-other'
                elif mutation == 'suspended':
                    for row in instance['assessment_uses'].values():
                        row['status'] = 'suspended'
                elif mutation == 'cycle':
                    assessment['item_dispositions'][0]['evidence_refs'] = ['RC-fixture']
                else:
                    instance['expositions'][instance['knowledge'][kid]['exposition_id']]['items'][0]['text'] += ' changed'
                with self.assertRaisesRegex(ValueError, reason):
                    apply_assessment(instance, runtime, assessment)

    def test_unresolved_has_one_owner_and_can_be_reassessed_after_evidence_arrives(self):
        instance, runtime, assessment, kid, aid = specialist_assessment()
        waiting = deepcopy(assessment)
        waiting.update(decision='incomplete', item_dispositions=[], unresolved=[{
            'obligation_id': 'OB-certification', 'missing_inputs': ['IA-needed'], 'next_owner': 'identity_review'}])
        _, changed = apply_assessment(instance, runtime, waiting)
        self.assertEqual(changed['tasks']['TK-1']['waiting']['kind'], 'assessment_input')
        duplicate = deepcopy(waiting)
        duplicate['item_dispositions'] = [{'obligation_id': 'OB-certification', 'kind': 'open', 'evidence_refs': []}]
        with self.assertRaisesRegex(ValueError, 'undisposed'):
            apply_assessment(instance, runtime, duplicate)
        _, completed = apply_assessment(instance, changed, assessment)
        self.assertEqual(completed['tasks']['TK-1']['status'], 'completed')

    def test_goal_judgment_must_cover_this_tasks_result_and_remain_current(self):
        from do_math.knowledge import capture_basis
        instance, runtime, assessment, kid, _ = specialist_assessment('goal_audit')
        judgment = {'id': 'GJ-proof', 'decision': 'satisfied', 'scope_complete': True, 'current': True,
                    'dependencies': [kid], 'record_basis': capture_basis(instance, runtime, [kid]),
                    **planning.governance_revisions(instance)}
        instance['goal_judgments'] = [judgment]
        assessment['item_dispositions'][0]['evidence_refs'] = ['GJ-proof']
        _, completed = apply_assessment(instance, runtime, assessment)
        self.assertEqual(completed['tasks']['TK-1']['status'], 'completed')
        judgment['current'] = False
        with self.assertRaisesRegex(ValueError, NO_JUDGMENT):
            apply_assessment(instance, runtime, assessment)


if __name__ == '__main__':
    unittest.main(verbosity=2)

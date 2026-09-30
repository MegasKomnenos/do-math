"""The identity review cycle's stage rules (``review_cycle``, layer 2), on pure cycles.

A cycle runs scope, initial, organize, answer and judge stages. The cycles
here start with their scope already settled (``review_fixtures.scoped_start``:
one initial slot per reviewer, three judges, the fixture policy), and
``review_fixtures.review_stage_output`` is a reviewer's default answer for
the next stage: initial reviewers match, organizers turn each pending finding
into an issue, answers maintain every objection and judges approve every
issue as a mismatch.
"""
import copy
import json
import unittest

from do_math.review_cycle import (ReviewRestorationError, accept_result, context_for, next_actions, record_turn,
                                  stage_schema, start_review, validate_review_independence)
from review_fixtures import review_stage_output, scoped_start


class ReviewCycleTests(unittest.TestCase):
    def start(self, **kw):
        return scoped_start({'revision': 'r1', 'proof': 'original', 'producer_execution_ids': ['author']}, reviewers=2, **kw)

    def submit(self, cycle, **changes):
        action = next_actions(cycle)[0]
        return accept_result(cycle, action, review_stage_output(cycle, action['stage'], **changes), f"e-{len(cycle['results'])}")

    def disputed(self, **kw):
        """One issue ``i0`` awaiting judgment: the first initial reviewer's finding ``f1``, organized."""
        cycle = self.start(**kw)
        cycle = self.submit(cycle, decision='mismatch', findings=[dict(id='f1', statement='Quantifier is reversed', evidence=['proposal:1'])])
        cycle = self.submit(cycle)
        return self.submit(cycle)

    def judges(self, cycle, vote='approved', decision='mismatch', extra=None):
        for _ in range(3):
            changes = dict(decision=decision, issue_verdicts=[dict(issue_id=i, decision=vote, reason='Source comparison', evidence=['proposal:1']) for i in cycle['issues']])
            if extra:
                changes.update(extra)
            cycle = self.submit(cycle, **changes)
        return cycle

    def test_incomplete_transcript_manifest_is_a_local_restoration_error(self):
        cycle = record_turn(self.start(), 'initial-0', [{'role': 'user', 'content': 'sealed', 'message_id': 'm'}])
        cycle['transcript_manifest']['initial-0'][0].pop('sha256')
        with self.assertRaisesRegex(ReviewRestorationError, 'transcript restoration manifest is incomplete') as raised:
            context_for(cycle, next_actions(cycle)[0])
        self.assertEqual(raised.exception.diagnostics['cause_kind'], 'invalid_manifest')

    def test_initial_unanimity_and_purity(self):
        cycle = self.start()
        before = copy.deepcopy(cycle)
        partial = self.submit(cycle)
        self.assertEqual(cycle, before)
        self.assertEqual(partial['phase'], 'initial')
        self.assertEqual(len(next_actions(partial)), 1)
        done = self.submit(partial)
        self.assertEqual((done['status'], done['decision']), ('completed', 'match'))
        self.assertEqual(next_actions(done), [])
        self.assertEqual(json.loads(json.dumps(done)), done)

    def test_initial_barrier_and_blindness(self):
        cycle = self.submit(self.start(), decision='mismatch', findings=[dict(id='f1', statement='secret finding', evidence=['proposal:1'])])
        context = context_for(cycle, next_actions(cycle)[0])
        self.assertEqual(context['completed_results'], {})
        self.assertEqual(context['issues'], {})
        self.assertEqual(context['pending_findings'], [])
        self.assertNotIn('secret finding', json.dumps(context))

    def test_scope_false_match_rejected_and_incomplete_not_reviewed(self):
        cycle = self.start()
        with self.assertRaisesRegex(ValueError, 'match requires complete scope'):
            self.submit(cycle, scope_complete=False)
        cycle = self.submit(cycle, decision='unresolved', scope_complete=False)
        cycle = self.submit(cycle)
        self.assertEqual(cycle['status'], 'unresolved')
        self.assertEqual(next_actions(cycle), [])

    def test_organizer_omission_forgery_and_owner_checks(self):
        cycle = self.start()
        cycle = self.submit(cycle, decision='mismatch', findings=[dict(id='f1', statement='finding one', evidence=['proposal:1'])])
        cycle = self.submit(cycle, decision='mismatch', findings=[dict(id='f1', statement='finding two same local ID', evidence=['proposal:2'])])
        valid = review_stage_output(cycle, 'organize')
        reasons = {'omit': 'organizer omitted original findings',
                   'forge': 'organizer forged or reused an original finding',
                   'duplicate': 'duplicate issue ID',
                   'owner': 'answer must return to its original reviewer or an eligible assigned slot'}
        for mutate, reason in reasons.items():
            output = copy.deepcopy(valid)
            if mutate == 'omit': output['issues'].pop()
            if mutate == 'forge': output['issues'][0]['finding_refs'][0]['id'] = 'fabricated'
            if mutate == 'duplicate': output['issues'].append(copy.deepcopy(output['issues'][0]))
            if mutate == 'owner': output['issues'][0]['answer_role_slot_id'] = 'initial-1'
            with self.subTest(mutate=mutate), self.assertRaisesRegex(ValueError, reason):
                accept_result(cycle, next_actions(cycle)[0], output, 'org')
        cycle = self.submit(cycle)
        self.assertEqual(cycle['phase'], 'judge')
        self.assertEqual(len(cycle['issues']), 2)

    def test_approved_objection_closes_mismatch(self):
        cycle = self.judges(self.disputed())
        self.assertEqual((cycle['status'], cycle['decision']), ('completed', 'mismatch'))
        self.assertEqual(cycle['issues']['i0']['status'], 'approved')

    def test_rejection_returns_to_original_slot_and_same_judges(self):
        cycle = self.judges(self.disputed(max_rounds=2), vote='rejected', decision='match')
        self.assertEqual(next_actions(cycle), [dict(stage='answer', slot='initial-0', round=2)])
        context = context_for(cycle, next_actions(cycle)[0])
        self.assertEqual(len([x for x in context['completed_results'].values() if x['stage'] == 'judge']), 3)
        self.assertTrue(any(m['role'] == 'assistant' for m in context['self_messages']))
        cycle = self.submit(cycle, answers=[dict(issue_id='i0', disposition='withdraw', statement='I misread the domain', evidence=['proposal:1'])])
        self.assertEqual(cycle['phase'], 'judge')
        self.assertEqual([a['slot'] for a in next_actions(cycle)], ['judge-0', 'judge-1', 'judge-2'])
        self.assertEqual(cycle['issues']['i0']['version'], 2)
        cycle = self.judges(cycle, vote='rejected', decision='match')
        self.assertEqual(cycle['decision'], 'match')

    def test_partial_judges_never_aggregate_or_leak(self):
        cycle = self.disputed()
        cycle = self.submit(cycle)
        context = context_for(cycle, next_actions(cycle)[0])
        self.assertEqual(cycle['status'], 'working')
        self.assertFalse(any(x['stage'] == 'judge' for x in context['completed_results'].values()))
        self.assertEqual(context['issues']['i0']['verdicts'], [])
        with self.assertRaisesRegex(ValueError, 'judge must assess every current issue exactly once'):
            self.submit(cycle, issue_verdicts=[])

    def test_judge_new_findings_get_organizer_assignment_and_answer(self):
        cycle = self.disputed(max_rounds=2)
        cycle = self.submit(cycle, new_findings=[dict(id='j1', statement='New independent objection', evidence=['proposal:3'])])
        self.assertEqual(cycle['pending_findings'], [])
        cycle = self.submit(cycle)
        cycle = self.submit(cycle)
        self.assertEqual((cycle['phase'], cycle['round']), ('organize', 2))
        source = context_for(cycle, next_actions(cycle)[0])['pending_findings'][0]['ref']
        self.assertEqual((source['stage'], source['slot']), ('judge', 'judge-0'))
        cycle = self.submit(cycle)
        self.assertEqual(next_actions(cycle), [dict(stage='answer', slot='initial-0', round=2)])
        cycle = self.submit(cycle)
        cycle = self.judges(cycle)
        self.assertEqual(cycle['decision'], 'mismatch')
        self.assertEqual(cycle['issues']['i1']['finding_refs'][0], source)

    def test_round_limit_split_votes_unresolved_and_last_rejection(self):
        cycle = self.disputed(max_rounds=1)
        cycle = self.submit(cycle)
        cycle = self.submit(cycle, decision='match', issue_verdicts=[dict(issue_id='i0', decision='rejected', reason='Different interpretation', evidence=['proposal:1'])])
        cycle = self.submit(cycle)
        self.assertEqual(cycle['decision'], 'unresolved')
        self.assertEqual(next_actions(cycle), [])
        self.assertTrue(cycle['followup'])
        other = self.judges(self.disputed(max_rounds=1), vote='rejected', decision='match')
        self.assertEqual(other['decision'], 'match')
        self.assertEqual(other['round'], 1)

    def test_new_finding_at_cap_cannot_be_approved(self):
        cycle = self.disputed(max_rounds=1)
        cycle = self.submit(cycle, new_findings=[dict(id='new', statement='Unjudged objection', evidence=['proposal:9'])])
        cycle = self.submit(cycle)
        cycle = self.submit(cycle)
        self.assertEqual(cycle['decision'], 'unresolved')
        self.assertTrue(cycle['pending_findings'])

    def test_answer_new_findings_and_split_reach_fresh_judgment(self):
        cycle = self.judges(self.disputed(max_rounds=2), vote='rejected', decision='match')
        answer = dict(issue_id='i0', disposition='split', statement='Separate the domain and quantifier objections', evidence=['proposal:1'])
        findings = [dict(id='child1', statement='Domain objection', evidence=['proposal:2'], parent_issue_ids=['i0']),
                    dict(id='child2', statement='Quantifier objection', evidence=['proposal:3'], parent_issue_ids=['i0']),
                    dict(id='independent', statement='Independent source defect', evidence=['proposal:4'], parent_issue_ids=[])]
        with self.assertRaisesRegex(ValueError, 'split must identify at least two derived findings'):
            self.submit(cycle, answers=[answer], new_findings=findings[:1])
        cycle = self.submit(cycle, answers=[answer], new_findings=findings)
        self.assertEqual(cycle['phase'], 'judge')
        self.assertEqual(len(cycle['issues']), 4)
        children = [issue for issue in cycle['issues'].values() if issue.get('parent_issue_ids') == ['i0']]
        self.assertEqual(len(children), 2)
        self.assertTrue(all(issue['answer_role_slot_id'] == 'initial-0' for issue in children))
        # Prior-round votes cannot satisfy this round, including unchanged issues.
        self.assertEqual(len(next_actions(cycle)), 3)
        cycle = self.judges(cycle)
        self.assertEqual(cycle['decision'], 'mismatch')
        self.assertEqual(len(cycle['issues']['i0']['verdicts']), 2)

    def test_answer_batch_hides_peer_results_and_covers_assignments(self):
        cycle = self.start(max_rounds=2)
        for i in range(2):
            cycle = self.submit(cycle, decision='mismatch', findings=[dict(id=f'f{i}', statement=f'Objection {i}', evidence=['proposal:1'])])
        cycle = self.submit(cycle)
        cycle = self.judges(cycle, vote='rejected', decision='match')
        with self.assertRaisesRegex(ValueError, 'answer must cover every assigned issue exactly once'):
            self.submit(cycle, answers=[])
        cycle = self.submit(cycle)
        context = context_for(cycle, next_actions(cycle)[0])
        self.assertFalse(any(x['stage'] == 'answer' for x in context['completed_results'].values()))
        self.assertIsNone(context['issues']['i0']['answer'])
        cycle = self.submit(cycle)
        self.assertEqual(cycle['phase'], 'judge')
        self.assertTrue(all(issue['answer'] for issue in cycle['issues'].values()))

    def test_round_three_reuses_slots_without_execution_keys_colliding(self):
        cycle = self.disputed(max_rounds=3)
        for round_number in (2, 3):
            cycle = self.judges(cycle, vote='unresolved', decision='unresolved')
            self.assertEqual((cycle['phase'], cycle['round']), ('answer', round_number))
            cycle = self.submit(cycle)
        cycle = self.judges(cycle, vote='unresolved', decision='unresolved')
        self.assertEqual(cycle['status'], 'unresolved')
        self.assertEqual(cycle['round'], 3)
        self.assertEqual(len(cycle['results']), 14)

    def test_allocation_duplicates_and_judge_count(self):
        cases = (((['x', 'x'], 3), 'duplicate slot'), ((['judge-0'], 3), 'duplicate requested role slot'),
                 ((2, 4), 'exactly three judges and a positive round limit are required'),
                 ((2, 2), 'exactly three judges and a positive round limit are required'))
        for (reviewers, judges), reason in cases:
            with self.subTest(reviewers=reviewers, judges=judges), self.assertRaisesRegex(ValueError, reason):
                start_review({'revision': 'r1'}, reviewers, judges)

    def test_revision_full_restart_and_old_output_blocked(self):
        old = self.submit(self.submit(self.start()))
        cycle = scoped_start({'revision': 'r2', 'proof': 'changed'}, reviewers=2, previous=old)
        self.assertEqual(cycle['status'], 'working')
        self.assertEqual(cycle['decision'], None)
        self.assertEqual(len(next_actions(cycle)), 2)
        self.assertEqual(cycle['reviewer_slots'], old['reviewer_slots'])
        self.assertEqual(cycle['turns'], old['turns'])
        with self.assertRaisesRegex(ValueError, 'result belongs to another proposal'):
            accept_result(cycle, next_actions(cycle)[0], review_stage_output(old, 'initial'), 'fresh')
        with self.assertRaisesRegex(ValueError, 'existing logical slots must be retained'):
            scoped_start({'revision': 'r2'}, reviewers=1, previous=old)
        with self.assertRaisesRegex(ValueError, 'new review requires a new proposal revision'):
            scoped_start({'revision': 'r1'}, reviewers=2, previous=old)

    def test_proposal_mutation_and_execution_identity(self):
        cycle = self.start()
        # Authorship and inherited author context are judged by the one lineage check
        # that admission and acceptance both run before accept_result.
        action = next_actions(cycle)[0]
        runtime = {'executions': {'author': {'id': 'author'}, 'fresh': {'id': 'fresh'},
                                  'resumed': {'id': 'resumed', 'continuation_of': 'author'},
                                  'inherited': {'id': 'inherited', 'context_origin': ['author']}}}
        validate_review_independence(cycle, runtime, 'fresh', action)
        reasons = {'author': 'independent checker execution required', 'resumed': 'checker resumes an author lineage',
                   'inherited': 'review inherited original author context'}
        for execution_id, reason in reasons.items():
            with self.subTest(execution_id=execution_id), self.assertRaisesRegex(ValueError, reason):
                validate_review_independence(cycle, runtime, execution_id, action)
        first = self.submit(cycle)
        with self.assertRaisesRegex(ValueError, 'execution ID already used'):
            accept_result(first, next_actions(first)[0], review_stage_output(first, 'initial'), 'e-0')
        cycle['proposal']['proof'] = 'mutated'
        with self.assertRaisesRegex(ValueError, 'sealed proposal changed'):
            next_actions(cycle)

    def test_transcript_restore_reference_and_integrity(self):
        cycle = self.start()
        messages = [dict(role='system', content='rules', message_id='s'),
                    dict(role='user', kind='proposal', content='old full proposal', message_id='p'),
                    dict(role='tool', content='large exact source body', call='read', arguments={'path': 'source'}, message_id='t'),
                    dict(role='assistant', content='Fact from source at line 3', message_id='a')]
        cycle = record_turn(cycle, 'initial-0', messages)
        self.assertEqual(record_turn(cycle, 'initial-0', messages), cycle)
        cycle = self.submit(self.submit(cycle))
        restored = scoped_start({'revision': 'r2'}, reviewers=2, previous=cycle)
        context = context_for(restored, next_actions(restored)[0])
        self.assertEqual(len(context['source_refs']), 2)
        self.assertNotIn('large exact source body', json.dumps(context))
        self.assertNotIn('old full proposal', json.dumps(context))
        self.assertIn('Fact from source at line 3', json.dumps(context))
        self.assertEqual(restored['turns']['initial-0'][2]['content'], 'large exact source body')
        context['proposal']['revision'] = 'external mutation'
        self.assertEqual(restored['revision'], 'r2')
        restored['turns']['initial-0'][0]['content'] = 'corrupt'
        with self.assertRaisesRegex(ValueError, 'transcript bytes changed'):
            context_for(restored, next_actions(restored)[0])

    def test_manifest_peer_and_judge_origin_checks(self):
        cycle = self.start()
        with self.assertRaisesRegex(ValueError, 'input manifest must be an object'):
            accept_result(cycle, next_actions(cycle)[0], review_stage_output(cycle, 'initial'), 'review', [])
        cycle = self.submit(self.start())
        with self.assertRaisesRegex(ValueError, 'input contains unsealed peer results'):
            accept_result(cycle, next_actions(cycle)[0], review_stage_output(cycle, 'initial'), 'e2', {'visible_execution_ids': ['e-0']})
        cycle = self.disputed()
        with self.assertRaisesRegex(ValueError, 'judge cannot inherit initial-review or organizer context'):
            accept_result(cycle, next_actions(cycle)[0], review_stage_output(cycle, 'judge'), 'judge-new', {'continuation_of': 'e-0'})
        cycle = self.submit(cycle)
        with self.assertRaisesRegex(ValueError, "a logical slot cannot inherit another slot's conversation"):
            accept_result(cycle, next_actions(cycle)[0], review_stage_output(cycle, 'judge'), 'judge-new', {'continuation_of': 'e-3'})

    def test_stage_schema_is_specific(self):
        self.assertIn('findings', stage_schema('initial')['required'])
        self.assertIn('issue_verdicts', stage_schema('judge')['required'])
        self.assertNotIn('decision', stage_schema('organize')['properties'])
        with self.assertRaisesRegex(ValueError, 'unknown review stage'):
            stage_schema('invented')


if __name__ == '__main__':
    unittest.main()

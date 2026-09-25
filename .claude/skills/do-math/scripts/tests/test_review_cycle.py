import copy
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.review_cycle import start_review, next_actions, stage_schema, accept_result, context_for, record_turn


def scoped_start(proposal, reviewers, judges=3, max_rounds=3, previous=None):
    slots = [f"initial-{index}" for index in range(reviewers)] if isinstance(reviewers, int) else list(reviewers)
    judge_slots = [f"judge-{index}" for index in range(judges)] if isinstance(judges, int) else list(judges)
    policy = {"id": "test-policy-v5", "version": 5, "required_perspectives": [],
              "minimum_initial_slots": len(slots), "judge_slots": judge_slots, "round_limit": max_rounds,
              "activity_execution_limit": len(slots) + max_rounds * (len(slots) + 4), "overflow_disposition": "unresolved"}
    assessment = {"assessment_id": "test-scope", "policy_id": policy["id"], "policy_version": 5,
                  "required_perspectives": [], "initial_slots": [
                      {"id": slot, "perspective": slot, "required_source_refs": ["proposal"]} for slot in slots],
                  "selected_profile_ref": None, "activity_execution_limit": policy["activity_execution_limit"],
                  "overflow_disposition": "unresolved"}
    return start_review(proposal, reviewers, judges, max_rounds, previous, policy=policy, scope_assessment=assessment)


class ReviewCycleTests(unittest.TestCase):
    def test_incomplete_transcript_manifest_is_a_local_restoration_error(self):
        cycle = record_turn(self.start(), 'initial-0', [{'role': 'user', 'content': 'sealed', 'message_id': 'm'}])
        cycle['transcript_manifest']['initial-0'][0].pop('sha256')
        with self.assertRaisesRegex(ValueError, 'transcript'):
            context_for(cycle, next_actions(cycle)[0])

    def start(self, **kw):
        return scoped_start({'revision': 'r1', 'proof': 'original', 'producer_execution_ids': ['author']}, reviewers=2, **kw)

    def output(self, cycle, stage, **changes):
        result = dict(proposal_digest=cycle['proposal_digest'], summary='Complete review evidence', used_sources=['proposal:1'], questions=[])
        if stage == 'initial':
            result.update(decision='match', scope_complete=True, findings=[])
        elif stage == 'organize':
            result['issues'] = [dict(id=f'i{j}', finding_refs=[x['ref']], answer_role_slot_id=x['ref']['slot'] if x['ref']['stage'] in ('initial', 'answer') else 'initial-0') for j, x in enumerate(context_for(cycle, next_actions(cycle)[0])['pending_findings'], start=len(cycle['issues']))]
        elif stage == 'answer':
            action = next_actions(cycle)[0]
            result.update(answers=[dict(issue_id=i, disposition='maintain', statement='The objection still applies', evidence=['proposal:1']) for i in context_for(cycle, action)['answer_requests']], new_findings=[])
        elif stage == 'judge':
            result.update(decision='mismatch', scope_complete=True, issue_verdicts=[dict(issue_id=i, decision='approved', reason='Proof at precise source coordinate', evidence=['proposal:1']) for i in cycle['issues']], new_findings=[])
        result.update(changes)
        return result

    def submit(self, cycle, **changes):
        action = next_actions(cycle)[0]
        return accept_result(cycle, action, self.output(cycle, action['stage'], **changes), f"e-{len(cycle['results'])}")

    def disputed(self, **kw):
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
        with self.assertRaisesRegex(ValueError, 'complete scope'):
            self.submit(cycle, scope_complete=False)
        cycle = self.submit(cycle, decision='unresolved', scope_complete=False)
        cycle = self.submit(cycle)
        self.assertEqual(cycle['status'], 'unresolved')
        self.assertEqual(next_actions(cycle), [])

    def test_organizer_omission_forgery_and_owner_checks(self):
        cycle = self.start()
        cycle = self.submit(cycle, decision='mismatch', findings=[dict(id='f1', statement='finding one', evidence=['proposal:1'])])
        cycle = self.submit(cycle, decision='mismatch', findings=[dict(id='f1', statement='finding two same local ID', evidence=['proposal:2'])])
        valid = self.output(cycle, 'organize')
        for mutate in ('omit', 'forge', 'duplicate', 'owner'):
            output = copy.deepcopy(valid)
            if mutate == 'omit': output['issues'].pop()
            if mutate == 'forge': output['issues'][0]['finding_refs'][0]['id'] = 'fabricated'
            if mutate == 'duplicate': output['issues'].append(copy.deepcopy(output['issues'][0]))
            if mutate == 'owner': output['issues'][0]['answer_role_slot_id'] = 'initial-1'
            with self.subTest(mutate=mutate), self.assertRaises(ValueError):
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
        with self.assertRaises(ValueError):
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
        with self.assertRaisesRegex(ValueError, 'split must identify'):
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
        with self.assertRaisesRegex(ValueError, 'every assigned issue'):
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
        for reviewers, judges in ((['x', 'x'], 3), (['judge-0'], 3), (2, 4), (2, 2)):
            with self.subTest(reviewers=reviewers, judges=judges), self.assertRaises(ValueError):
                start_review({'revision': 'r1'}, reviewers, judges)

    def test_revision_full_restart_and_old_output_blocked(self):
        old = self.submit(self.submit(self.start()))
        cycle = scoped_start({'revision': 'r2', 'proof': 'changed'}, reviewers=2, previous=old)
        self.assertEqual(cycle['status'], 'working')
        self.assertEqual(cycle['decision'], None)
        self.assertEqual(len(next_actions(cycle)), 2)
        self.assertEqual(cycle['reviewer_slots'], old['reviewer_slots'])
        self.assertEqual(cycle['turns'], old['turns'])
        with self.assertRaisesRegex(ValueError, 'another proposal'):
            accept_result(cycle, next_actions(cycle)[0], self.output(old, 'initial'), 'fresh')
        with self.assertRaises(ValueError):
            scoped_start({'revision': 'r2'}, reviewers=1, previous=old)
        with self.assertRaises(ValueError):
            scoped_start({'revision': 'r1'}, reviewers=2, previous=old)

    def test_proposal_mutation_and_execution_identity(self):
        cycle = self.start()
        with self.assertRaises(ValueError):
            accept_result(cycle, next_actions(cycle)[0], self.output(cycle, 'initial'), 'author')
        with self.assertRaises(ValueError):
            accept_result(cycle, next_actions(cycle)[0], self.output(cycle, 'initial'), 'review', {'continuation_of': 'author'})
        first = self.submit(cycle)
        with self.assertRaises(ValueError):
            accept_result(first, next_actions(first)[0], self.output(first, 'initial'), 'e-0')
        cycle['proposal']['proof'] = 'mutated'
        with self.assertRaises(ValueError): next_actions(cycle)

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
        with self.assertRaisesRegex(ValueError, 'bytes changed'):
            context_for(restored, next_actions(restored)[0])

    def test_manifest_peer_and_judge_origin_checks(self):
        cycle = self.start()
        with self.assertRaisesRegex(ValueError, 'input manifest must be an object'):
            accept_result(cycle, next_actions(cycle)[0], self.output(cycle, 'initial'), 'review', [])
        cycle = self.submit(self.start())
        with self.assertRaisesRegex(ValueError, 'unsealed peer'):
            accept_result(cycle, next_actions(cycle)[0], self.output(cycle, 'initial'), 'e2', {'visible_execution_ids': ['e-0']})
        cycle = self.disputed()
        with self.assertRaisesRegex(ValueError, 'judge cannot inherit'):
            accept_result(cycle, next_actions(cycle)[0], self.output(cycle, 'judge'), 'judge-new', {'continuation_of': 'e-0'})
        cycle = self.submit(cycle)
        with self.assertRaisesRegex(ValueError, "another slot's conversation"):
            accept_result(cycle, next_actions(cycle)[0], self.output(cycle, 'judge'), 'judge-new', {'continuation_of': 'e-3'})

    def test_stage_schema_is_specific(self):
        self.assertIn('findings', stage_schema('initial')['required'])
        self.assertIn('issue_verdicts', stage_schema('judge')['required'])
        self.assertNotIn('decision', stage_schema('organize')['properties'])
        with self.assertRaises(ValueError): stage_schema('invented')


if __name__ == '__main__':
    unittest.main()

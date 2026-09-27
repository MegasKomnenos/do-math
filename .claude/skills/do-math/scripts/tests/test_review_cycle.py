import copy
import json
import sys
import unittest
from pathlib import Path
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.review_cycle import (start_review, next_actions, stage_schema, accept_result, context_for, record_turn,
                                  validate_review_independence)
from review_fixtures import deferred_research_cycle, grant_replacement, research_answer, review_stage_output, ReviewFakeEngine, scoped_start


class ReviewCycleTests(unittest.TestCase):
    def test_incomplete_transcript_manifest_is_a_local_restoration_error(self):
        cycle = record_turn(self.start(), 'initial-0', [{'role': 'user', 'content': 'sealed', 'message_id': 'm'}])
        cycle['transcript_manifest']['initial-0'][0].pop('sha256')
        with self.assertRaisesRegex(ValueError, 'transcript'):
            context_for(cycle, next_actions(cycle)[0])

    def start(self, **kw):
        return scoped_start({'revision': 'r1', 'proof': 'original', 'producer_execution_ids': ['author']}, reviewers=2, **kw)

    def submit(self, cycle, **changes):
        action = next_actions(cycle)[0]
        return accept_result(cycle, action, review_stage_output(cycle, action['stage'], **changes), f"e-{len(cycle['results'])}")

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
        valid = review_stage_output(cycle, 'organize')
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
            accept_result(cycle, next_actions(cycle)[0], review_stage_output(old, 'initial'), 'fresh')
        with self.assertRaises(ValueError):
            scoped_start({'revision': 'r2'}, reviewers=1, previous=old)
        with self.assertRaises(ValueError):
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
        for execution_id in ('author', 'resumed', 'inherited'):
            with self.subTest(execution_id=execution_id), self.assertRaises(ValueError):
                validate_review_independence(cycle, runtime, execution_id, action)
        first = self.submit(cycle)
        with self.assertRaises(ValueError):
            accept_result(first, next_actions(first)[0], review_stage_output(first, 'initial'), 'e-0')
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
            accept_result(cycle, next_actions(cycle)[0], review_stage_output(cycle, 'initial'), 'review', [])
        cycle = self.submit(self.start())
        with self.assertRaisesRegex(ValueError, 'unsealed peer'):
            accept_result(cycle, next_actions(cycle)[0], review_stage_output(cycle, 'initial'), 'e2', {'visible_execution_ids': ['e-0']})
        cycle = self.disputed()
        with self.assertRaisesRegex(ValueError, 'judge cannot inherit'):
            accept_result(cycle, next_actions(cycle)[0], review_stage_output(cycle, 'judge'), 'judge-new', {'continuation_of': 'e-0'})
        cycle = self.submit(cycle)
        with self.assertRaisesRegex(ValueError, "another slot's conversation"):
            accept_result(cycle, next_actions(cycle)[0], review_stage_output(cycle, 'judge'), 'judge-new', {'continuation_of': 'e-3'})

    def test_stage_schema_is_specific(self):
        self.assertIn('findings', stage_schema('initial')['required'])
        self.assertIn('issue_verdicts', stage_schema('judge')['required'])
        self.assertNotIn('decision', stage_schema('organize')['properties'])
        with self.assertRaises(ValueError): stage_schema('invented')


class SealedReplayTests(unittest.TestCase):
    def test_budget_closed_investigation_is_verified_unresolved_not_an_unfinished_vote(self):
        from do_math.review_cycle import start_review, next_actions, defer_for_research, validate_sealed_review
        scoped = scoped_start({'revision': 1}, reviewers=2)
        cycle = start_review({'revision': 1}, reviewers=2, policy=scoped['review_policy'], scope_assessment=scoped['scope_assessment'])
        cycle['id'] = 'RC-cap'
        action = next_actions(cycle)[0]
        output = {'proposal_digest': cycle['proposal_digest'], 'summary': 'A fixed question remains',
            'used_sources': [], 'questions': [], 'decision': 'unresolved', 'scope_complete': False, 'findings': []}
        requests = [{'id': 'r', 'question': 'Which domain is intended?', 'source_refs': ['proposal']}]
        cycle = defer_for_research(cycle, action, output, requests, 'requester', [[]], limit=0)
        runtime = {'executions': {'requester': {'id': 'requester', 'role': 'identity_review', 'status': 'ended',
            'outcome': 'output_accepted', 'output': output, 'action': {**action, 'review_cycle_id': cycle['id']}}}}
        from do_math.configuration import DEFAULT_CONFIG
        from do_math.execution_profiles import build_profiles, profile_ref
        config = {**copy.deepcopy(DEFAULT_CONFIG), 'review_research_limit': 0}
        instance = {'config': config, **build_profiles(config)}
        profile = next(p for p in instance['execution_profiles'].values() if p['role'] == 'identity_review')
        runtime['executions']['requester'].update(actor_kind='ai', execution_profile_ref=profile_ref(profile))
        result = validate_sealed_review(cycle, runtime, instance=instance)
        self.assertEqual((result['status'], result['decision']), ('unresolved', 'unresolved'))
        instance['config']['review_research_limit'] = 3
        with self.assertRaisesRegex(ValueError, 'closure|limit'):
            validate_sealed_review(cycle, runtime, instance=instance)

    def test_authorized_replacement_keeps_full_authority_and_sealed_input(self):
        from do_math.review_cycle import validate_sealed_review, record_recovery_event
        with tempfile.TemporaryDirectory() as directory:
            engine = ReviewFakeEngine(directory)
            grant_replacement(engine)
            cid = engine.start('K1')
            action = engine.pending()
            cycle = engine.runtime['review_cycles'][cid]
            short = {k: action[k] for k in ('stage', 'slot', 'round')}
            engine.runtime['review_cycles'][cid] = record_recovery_event(cycle, short,
                {'reason': 'lost exact public transcript', 'retryable': False, 'preserved_range': {'slot': action['slot']}})
            engine._authorize_review_replacement(action, grant_id='GR-review')
            while any(a['role'] == 'identity_review' for a in engine.runtime['queue']):
                engine.execute()
            cycle = engine.runtime['review_cycles'][cid]
            self.assertIn('sealed_input_sha256', cycle['replacement_receipts'][0]['authorization'])
            self.assertEqual(validate_sealed_review(cycle, engine.runtime, instance=engine.instance)['decision'], 'match')
            cycle['replacement_receipts'][0]['authorization']['sealed_input_sha256'] = 'changed'
            with self.assertRaisesRegex(ValueError, 'sealed input changed'):
                validate_sealed_review(cycle, engine.runtime, instance=engine.instance)

    def test_previous_review_must_resolve_to_its_actual_preserved_cycle(self):
        from do_math.review_cycle import start_review, accept_result, next_actions, validate_sealed_review
        runtime = {'executions': {}, 'review_cycles': {}}
        previous = None
        for revision in (1, 2):
            seed = scoped_start({'revision': revision}, reviewers=2)
            cycle = start_review({'revision': revision}, reviewers=2, previous=previous,
                policy=seed['review_policy'], scope_assessment=seed['scope_assessment'])
            cid = 'cycle-' + str(revision)
            cycle['id'] = cid
            while next_actions(cycle):
                action = next_actions(cycle)[0]
                output = review_stage_output(cycle, action['stage'])
                eid = cid + ':' + action['slot']
                runtime['executions'][eid] = {'id': eid, 'role': 'identity_review', 'status': 'ended',
                    'outcome': 'output_accepted', 'output': output, 'action': {**action, 'review_cycle_id': cid}}
                cycle = accept_result(cycle, action, output, eid)
            runtime['review_cycles'][cid] = cycle
            previous = cycle
        self.assertEqual(validate_sealed_review(cycle, runtime)['decision'], 'match')
        forged = copy.deepcopy(cycle)
        next(iter(forged['results'].values()))['stage'] = 'judge'
        with self.assertRaisesRegex(ValueError, 'sealed evidence'):
            validate_sealed_review(forged, runtime)
        del runtime['review_cycles']['cycle-1']
        with self.assertRaisesRegex(ValueError, 'preserved cycle'):
            validate_sealed_review(cycle, runtime)

    def test_fixed_private_research_is_replayed_before_requesters_final_vote(self):
        from do_math.review_cycle import accept_research_result, accept_result, next_actions, validate_sealed_review
        cycle, action = deferred_research_cycle()
        cycle['id'] = 'RC-research'
        provisional = cycle['turns'][action['slot']][0]['content']['provisional_result']
        rid = next(iter(cycle['research']))
        answer = research_answer(cycle)
        runtime = {'executions': {
            'requester': {'id': 'requester', 'role': 'identity_review', 'status': 'ended', 'outcome': 'output_accepted',
                          'output': provisional, 'action': {**action, 'review_cycle_id': cycle['id']}},
            'investigator': {'id': 'investigator', 'role': 'supplemental_research', 'status': 'ended', 'outcome': 'output_accepted',
                             'output': answer, 'action': {'role': 'supplemental_research', 'research_request_id': rid, 'review_cycle_id': cycle['id']}}
        }}
        cycle = accept_research_result(cycle, rid, answer, 'investigator')
        while next_actions(cycle):
            pending = next_actions(cycle)[0]
            output = review_stage_output(cycle, pending['stage'])
            eid = pending['slot']
            runtime['executions'][eid] = {'id': eid, 'role': 'identity_review', 'status': 'ended', 'outcome': 'output_accepted',
                'output': output, 'action': {**pending, 'review_cycle_id': cycle['id']}}
            cycle = accept_result(cycle, pending, output, eid)
        self.assertEqual(validate_sealed_review(cycle, runtime)['decision'], 'match')
        runtime['executions']['investigator']['output']['request_digest'] = 'forged'
        with self.assertRaisesRegex(ValueError, 'actual accepted execution'):
            validate_sealed_review(cycle, runtime)


if __name__ == '__main__':
    unittest.main()

"""Fixed-question review investigations through the real engine and pure cycle.

The engine tests start from ``purpose_state``: the task chain before a review
has no subject here, so it runs once per process and each test gets a copy.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.canonical import canonical_json
from do_math.review_cycle import next_actions, context_for, accept_research_result, accept_result
from purpose_fixtures import ActivatedPurposeHarness, PurposeRunner, common, EXPLANATION, parse_context
from purpose_fixtures import purpose_copy
from review_fixtures import ReviewFakeEngine, defer_review_for_research, deferred_research_cycle, research_answer
from do_math import knowledge_records as kr
from do_math.execution_profiles import resolve_profile
from research_fixtures import local_job_runner, role_reach, send_control
from state_fixtures import ACTIVE_LEAN_COMMAND
import tempfile


class InvestigationRunner(PurposeRunner):
    def __init__(self, *, repeat=False, batch=False):
        super().__init__('direct')
        self.repeat, self.batch = repeat, batch
        self.research_answers = []
        self.resumed_contexts = []

    def answer(self, role, context, workspace):
        action = context['action']
        if role == 'identity_review' and action['stage'] == 'initial' and action['slot'] == 'initial-0':
            review = context['role_review']
            if not review['supplemental_results'] or self.repeat:
                requests = [{'id': 'domain', 'question': 'Which binder domain does the exact exported declaration signature use?',
                             'source_refs': ['proposal:formal.declaration_signatures', 'proposal:lean_code']}]
                if self.repeat:
                    requests[0]['question'] = 'Does this signature match the external textbook definition that has not been supplied?'
                if self.batch:
                    requests.append({'id': 'export', 'question': 'Which declaration exports the supplied proof?',
                                     'source_refs': ['proposal:declaration_names', 'proposal:lean_code']})
                (workspace / 'activity-extensions.json').write_bytes(canonical_json({'research_requests': requests}))
                return {**common('A fixed source comparison is needed before my complete review'),
                    'proposal_digest': review['proposal_digest'], 'decision': 'unresolved', 'scope_complete': False, 'findings': []}
            self.resumed_contexts.append(deepcopy(review))
            for research in review['supplemental_results']:
                for source in research['result']['source_records']:
                    raw = (workspace / source['local_path']).read_bytes()
                    if hashlib.sha256(raw).hexdigest() != source['sha256']:
                        raise AssertionError('Returned supplemental source differs from its fixed hash')
            return super().answer(role, context, workspace)
        if role == 'supplemental_research':
            research = context['review_research']
            if context.get('task') is not None:
                raise AssertionError('Review investigation incorrectly inherited a task execution contract')
            for source in research['sources']:
                raw = (workspace / source['local_path']).read_bytes()
                if hashlib.sha256(raw).hexdigest() != source['sha256']:
                    raise AssertionError('Investigator source differs from its fixed hash')
            if self.repeat:
                output = {**common('The external textbook definition is not among the fixed inputs'),
                    'questions': ['The exact external definition remains unavailable'],
                    'research_request_id': research['id'], 'request_digest': research['request_digest'],
                    'outcome': 'unresolved', 'answer': 'The supplied signature cannot establish equivalence to an unavailable textbook definition.',
                    'scope_complete': False, 'evidence_refs': []}
            else:
                answer = 'The binder domain is Nat.' if 'binder domain' in research['question'] else 'The exported declaration is add_zero_fixture.'
                (workspace / 'comparison.txt').write_text(answer + '\n' + EXPLANATION, encoding='utf-8')
                output = {**common('The requested exact source comparison is complete'),
                    'used_sources': [research['sources'][0]['ref']], 'research_request_id': research['id'],
                    'request_digest': research['request_digest'], 'outcome': 'answered', 'answer': answer,
                    'scope_complete': True, 'evidence_refs': [research['sources'][0]['ref'], 'workspace:comparison.txt']}
            self.research_answers.append(deepcopy(output))
            return output
        return super().answer(role, context, workspace)


class ReviewResearchEngineTests(ActivatedPurposeHarness):
    def review(self, runner, *, review_policy=None, **config):
        """``runner`` on a copy of the state whose identity review cycle just opened."""
        # Formal checks on the synthetic state use its active environment's command.
        return purpose_copy(self, runner, until='review', review_policy=review_policy,
                            config=self.fixture_config(lean_command=list(ACTIVE_LEAN_COMMAND), **config))

    def make_research(self, *, repeat=False, batch=False, **config):
        from do_math.review_policy import build_review_policy
        policy = build_review_policy(reviewer_count=2, max_rounds=config.get('review_rounds', 2))
        # This scenario authorizes investigation and the deferred slot's replay,
        # in addition to the final review calls reserved by the base policy.
        policy['activity_execution_limit'] += 2 * config.get('review_research_limit', 3)
        return self.review(InvestigationRunner(repeat=repeat, batch=batch), review_policy=policy, **config)

    def test_common_document_overflow_waits_without_reconstructing_the_proposal(self):
        engine, runner = self.make_research()
        action = next(a for a in engine.runtime['queue'] if a['role'] == 'identity_review')
        knowledge_id = action['target']
        before = deepcopy(engine.instance['knowledge'][knowledge_id])
        # The cycle keeps its admitted immutable profile. Make the mandatory
        # document exceed that actual limit instead of changing an unrelated
        # config projection behind the profile registry.
        fragment = '\nMandatory common-document fixture. '
        engine._documents['identity_review'] = deepcopy(engine._documents['identity_review'])
        document = engine._documents['identity_review'][0]
        document['content'] += fragment * (engine.instance['config']['max_input_bytes'] // len(fragment) + 1)
        document['sha256'] = hashlib.sha256(document['content'].encode()).hexdigest()
        calls = [row['action']['id'] for row in runner.calls if row['role']=='identity_review']
        # A blocked review must not call its model. Other queued planning work
        # remains dispatchable, so wait for this action's own overflow receipt.
        self.drive(engine, predicate=lambda e:any(
            w['action'].get('id')==action['id'] and w.get('reason')=='input_overflow'
            for w in e.runtime.get('waiting_actions',{}).values()), limit=6)
        self.assertEqual([row['action']['id'] for row in runner.calls if row['role']=='identity_review'], calls)
        self.assertEqual(engine.instance['knowledge'][knowledge_id], before)
        self.assertTrue(any(w['action'].get('id') == action['id'] and w['reason'] == 'input_overflow'
                            for w in engine.runtime.get('waiting_actions', {}).values()))
        self.assertFalse(any(row.get('event') == 'review_resource_disposition'
                             for row in engine.runtime['review_cycles'][action['review_cycle_id']]['history']))
        wait = next(w for w in engine.runtime['waiting_actions'].values() if w['action']['id'] == action['id'])
        question = next(q for q in engine.runtime['question_links'] if q['id'] == wait['question_id'])
        self.assertEqual(question['status'], 'open')
        self.assertIn(knowledge_id, question['target_ids'])

    def test_all_fixed_questions_return_before_resuming_the_deferred_slot(self):
        engine, runner = self.make_research(batch=True)
        self.drive(engine, predicate=lambda e: bool(runner.resumed_contexts)
            and any(c['decision'] == 'match' for c in e.runtime['review_cycles'].values()))
        self.assertEqual(len(runner.research_answers), 2)
        self.assertEqual(len(runner.resumed_contexts), 1)
        self.assertEqual(len(runner.resumed_contexts[0]['supplemental_results']), 2)
        cycle = next(iter(engine.runtime['review_cycles'].values()))
        self.assertEqual(cycle['decision'], 'match')
        self.assertEqual(sum(row['action']['stage'] == 'initial' for row in cycle['results'].values()), 2)
        self.assertIn('scope:1:scope', cycle['results'])
        self.assertFalse(cycle['deferred_actions'])
        requests = list(cycle['research'].values())
        self.assertEqual(len(requests), 2)
        self.assertEqual(runner.resumed_contexts[0]['action']['slot'], 'initial-0')
        self.assertTrue(any(message['role'] == 'tool' and message.get('kind') == 'supplemental_research'
                            for message in cycle['turns']['initial-0']))
        self.assertIn('declaration_signatures', cycle['proposal']['formal'])
        self.assertIn('signature_hash', cycle['proposal']['formal'])
        final_id = next(result['execution_id'] for result in cycle['results'].values()
                        if result['action']['slot'] == 'initial-0')
        for request in requests:
            investigation = engine.runtime['executions'][request['result']['execution_id']]
            self.assertEqual(investigation['role'], 'supplemental_research')
            # An investigation is work: its immutable profile reserves a work slot.
            self.assertTrue(resolve_profile(engine.instance['execution_profiles'],
                                            investigation['execution_profile_ref'])['ai']['capacity_refs'])
            self.assertEqual(request['action']['slot'], 'initial-0')
            self.assertNotEqual(request['requested_by'], investigation['id'])
            self.assertNotEqual(final_id, request['requested_by'])
            self.assertNotIn(request['requested_by'], {r['execution_id'] for r in cycle['results'].values()})
        actual_roles = [call['role'] for call in runner.calls]
        research_positions = [i for i, role in enumerate(actual_roles) if role == 'supplemental_research']
        resumed_position = next(i for i, call in enumerate(runner.calls) if call['role'] == 'identity_review'
            and call['action']['slot'] == 'initial-0' and call['context']['role_review']['supplemental_results'])
        self.assertGreater(resumed_position, max(research_positions))

    def test_repeated_unanswered_request_closes_unresolved_at_the_activity_limit(self):
        engine, runner = self.make_research(repeat=True, review_research_limit=1)
        self.drive(engine, predicate=lambda e: any(c['status'] == 'unresolved' for c in e.runtime['review_cycles'].values()))
        cycle = next(iter(engine.runtime['review_cycles'].values()))
        self.assertEqual(len(runner.research_answers), 1)
        self.assertEqual(cycle['decision'], 'unresolved')
        self.assertTrue(cycle['followup'])
        self.assertFalse(any(kr.usable_links(engine.instance, kid) for kid in engine.instance['knowledge']))
        self.assertFalse(any(a.get('review_cycle_id') == cycle['id'] for a in engine.runtime['queue']))
        self.assertTrue(any('external textbook definition' in (question.get('text') or '') for question in engine._question_view()))


    def test_initial_peer_question_is_not_exposed_before_phase_seal(self):
        engine, runner = self.make_research()
        original, secret, reach = runner.answer, 'PRIVATE-PEER-DOMAIN-QUESTION', []
        def question(role, context, workspace):
            action = context['action']
            if role == 'identity_review' and action['stage'] == 'initial' and action['slot'] == 'initial-0':
                return {**common('Review remains uncertain'), 'questions': [secret],
                    'proposal_digest': context['role_review']['proposal_digest'], 'decision': 'unresolved', 'scope_complete': True, 'findings': []}
            if role == 'identity_review' and action['stage'] == 'initial' and action['slot'] == 'initial-1':
                # The peer seat of the unsealed initial phase, as its role actually receives it.
                reach.append(role_reach(runner.calls[-1]['prompt'], workspace, secret))
            return original(role, context, workspace)
        runner.answer = question
        self.drive(engine, predicate=lambda e: bool(reach))
        (reached, held), = reach
        self.assertTrue(held, 'The input snapshot must hold the peer question for this check to mean anything')
        self.assertEqual(reached, [])

    def test_investigator_does_not_receive_unsealed_peer_summary(self):
        engine, runner = self.make_research()
        original, secret, reach = runner.answer, 'PRIVATE-PEER-SUMMARY', []
        def peer_summary(role, context, workspace):
            if role == 'supplemental_research':
                # The investigator of initial-0's fixed question, as its role actually receives it.
                reach.append(role_reach(runner.calls[-1]['prompt'], workspace, secret))
            output = original(role, context, workspace)
            if role == 'identity_review' and context['action']['stage'] == 'initial' and context['action']['slot'] == 'initial-1':
                output['summary'] = secret
            return output
        runner.answer = peer_summary
        self.drive(engine, predicate=lambda e: bool(reach))
        (reached, held), = reach
        self.assertTrue(held, 'The input snapshot must hold the peer summary for this check to mean anything')
        self.assertEqual(reached, [])

    # Split-record trust recovery is covered in test_knowledge by
    # test_invalidated_environment_recovery_rechecks_all_accepted_results,
    # test_recovery_preserves_later_semantic_suspension, and
    # test_environment_recovery_cannot_clear_a_later_source_reassessment.

    def test_user_revision_cancels_old_investigation_and_reviews_new_revision(self):
        engine, runner = self.make_research()
        self.drive(engine, predicate=lambda e: any(a['role'] == 'supplemental_research' for a in e.runtime['queue']))
        item = next(iter(engine.instance['knowledge'].values()))
        old_cycle_id = item['review_cycle_id']
        from do_math import knowledge
        changes = {'explanation': EXPLANATION + ' The revised statement explicitly retains that domain.'}
        roots = knowledge.revision_roots(engine.instance, item['id'])
        send_control(engine, 'knowledge', config={'operation': 'revise', 'id': item['id'], 'changes': changes,
            'declared_impact': knowledge.plan_impact(engine.instance, engine.runtime, roots, [])['computed_impact'],
            'reason': 'Explicit source revision'})
        self.assertFalse(any(a.get('review_cycle_id') == old_cycle_id for a in engine.runtime['queue']))
        old_cycle = engine.runtime['review_cycles'][old_cycle_id]
        self.assertEqual(old_cycle['status'], 'unresolved')
        self.assertTrue(all(r['status'] == 'cancelled' for r in old_cycle['research'].values()))
        self.drive(engine, predicate=lambda e: any(row.get('supersedes') == item['id']
            and kr.usable_links(e.instance, row['id']) for row in e.instance['knowledge'].values()))
        replacement = next(row for row in engine.instance['knowledge'].values() if row.get('supersedes') == item['id'])
        self.assertNotEqual(replacement['review_cycle_id'], old_cycle_id)
        self.assertTrue(kr.usable_links(engine.instance, replacement['id']))

    def test_supplemental_evidence_is_readable_again_in_the_next_revision(self):
        engine, runner = self.make_research()
        self.drive(engine, predicate=lambda e: any(kr.usable_links(e.instance, kid) for kid in e.instance['knowledge']))
        item = next(iter(engine.instance['knowledge'].values()))
        from do_math import knowledge
        changes = {'explanation': EXPLANATION + ' This revision adds an explicit domain reminder.'}
        roots = knowledge.revision_roots(engine.instance, item['id'])
        send_control(engine, 'knowledge', config={'operation': 'revise', 'id': item['id'], 'changes': changes,
            'declared_impact': knowledge.plan_impact(engine.instance, engine.runtime, roots, [])['computed_impact'],
            'reason': 'New proposal revision'})
        self.drive(engine, predicate=lambda e: len(runner.resumed_contexts) >= 2
            and any(row.get('supersedes') == item['id'] and kr.usable_links(e.instance, row['id'])
                    for row in e.instance['knowledge'].values()))
        self.assertEqual(len(runner.research_answers), 1)
        self.assertEqual(len(runner.resumed_contexts), 2)
        self.assertIn('previous_revision', runner.resumed_contexts[-1]['supplemental_results'][0])

    def test_inline_stop_returns_execution_incomplete_to_the_requesting_slot(self):
        engine, previous = self.make_research()
        class StoppedInvestigator(InvestigationRunner):
            @local_job_runner
            def run(self, **kwargs):
                if 'role: supplemental_research.' not in kwargs['prompt']:
                    return super().run(**kwargs)
                workspace = kwargs['workspace']
                context = parse_context(kwargs['prompt'], workspace)
                self.calls.append({'role': 'supplemental_research', 'action': deepcopy(context['action']), 'context': context, 'workspace': str(workspace)})
                kwargs['on_started']({'pid': 99, 'source': 'test double'})
                (workspace / 'checkpoint.json').write_bytes(canonical_json({'current_claim': 'Investigation is blocked',
                    'evidence_paths': [], 'attempts': ['Checked fixed inputs'], 'remaining_work': ['Resolve the fixed question'],
                    'next_step': 'Return the exact missing evidence', 'progress_state': 'blocked'}))
                kwargs['on_observation']({'type': 'tick'})
                kwargs['should_stop']()
                return {'status': 'stopped', 'output': None, 'usage': {}, 'error': 'Fixture investigator stopped with a preserved checkpoint'}
        runner = StoppedInvestigator()
        engine.runner = runner
        self.drive(engine, predicate=lambda e: any(r.get('result', {}).get('execution_status') == 'incomplete'
            for c in e.runtime['review_cycles'].values() for r in c.get('research', {}).values() if r.get('result')))
        cycle = next(iter(engine.runtime['review_cycles'].values()))
        self.assertEqual(cycle['status'], 'working')
        self.assertNotEqual(engine.runtime['status'], 'paused')
        self.assertFalse(cycle['deferred_actions'])
        self.assertTrue(any(a['slot'] == 'initial-0' for a in next_actions(cycle)))
        request = next(iter(cycle['research'].values()))
        self.assertEqual(request['status'], 'unresolved')
        self.assertEqual(request['result']['output']['outcome'], 'unresolved')


class SplitReviewResearchTests(unittest.TestCase):
    def test_producer_and_receiver_reject_an_unassigned_used_source(self):
        from do_math import submission
        engine = self.engine
        defer_review_for_research(self.engine)
        action = next(a for a in engine.runtime['queue'] if a['role'] == 'supplemental_research')
        workspace = engine.root/'source-check'
        context = engine._review_research_context(action, workspace)
        context.update(action=action, knowledge_catalog=[{'id': 'KN-unassigned'}])
        research = context['review_research']
        output = {'summary': 'Compare fixed evidence', 'used_sources': ['KN-unassigned'], 'questions': [],
            'research_request_id': research['id'], 'request_digest': research['request_digest'],
            'outcome': 'answered', 'answer': 'The declared evidence is complete', 'scope_complete': True,
            'evidence_refs': [research['sources'][0]['ref']]}
        schema = engine._review_research_schema(action)
        # The same answer citing only its fixed source passes: the receiver's
        # schema binds the request identity without constraining other fields.
        assigned = {**output, 'used_sources': [research['sources'][0]['ref']]}
        self.assertEqual(submission._payload_issues(assigned, schema, context, {}, workspace), [])
        issues = submission._payload_issues(output, schema, context, {}, workspace)
        self.assertTrue(any(row['path'] == 'output/used_sources/0' and 'fixed source set' in row['message']
                            for row in issues), issues)
        execution = {'id': 'INV-unassigned', 'role': 'supplemental_research', 'action': action,
            'actor_kind': 'ai', 'owner_activity_id': action['owner_activity_id'],
            'execution_profile_ref': deepcopy(engine.research_profile)}
        self.assertEqual(engine._admit_review_execution(action, execution)['disposition'], 'admitted')
        engine.runtime['executions'][execution['id']] = execution
        with self.assertRaisesRegex(ValueError, 'fixed source set'):
            engine._apply_review_research(action, output, execution['id'])

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.engine = ReviewFakeEngine(self.directory.name)

    def test_session_mode_does_not_let_optional_research_spend_reserved_followup(self):
        self.engine.instance['review_policy']['activity_execution_limit'] = 13
        cid = defer_review_for_research(self.engine)
        self.assertFalse(any(a['role'] == 'supplemental_research' for a in self.engine.runtime['queue']))
        self.assertEqual(self.engine.runtime['review_cycles'][cid]['decision'], 'unresolved')


    def test_split_scope_fixed_research_and_resumed_review_publish_exact_assessment(self):
        engine = self.engine
        cid = defer_review_for_research(self.engine)
        engine.execute({'summary': 'PRIVATE-INITIAL-PEER'})
        action = next(a for a in engine.runtime['queue'] if a['role'] == 'supplemental_research')
        context = engine._review_research_context(action, engine.root / 'investigation')
        self.assertNotIn('PRIVATE-INITIAL-PEER', json.dumps(context))
        self.assertEqual(context['proposal']['lean_code'], kr.proposal_view(engine.instance, 'K1')['lean_code'])
        research = context['review_research']
        for source in research['sources']:
            self.assertEqual(hashlib.sha256((engine.root / 'investigation' / source['local_path']).read_bytes()).hexdigest(), source['sha256'])
        execution = {'id': 'INV-answer', 'role': 'supplemental_research', 'status': 'running', 'action': action,
                     'execution_profile_ref': deepcopy(engine.research_profile),
                     'actor_kind': 'ai', 'owner_activity_id': action['owner_activity_id']}
        self.assertEqual(engine._admit_review_execution(action, execution)['disposition'], 'admitted')
        engine.runtime['executions']['INV-answer'] = execution
        engine._apply_review_research(action, {'summary': 'Exact dependency map checked',
            'used_sources': [research['sources'][0]['ref']], 'questions': [], 'research_request_id': research['id'],
            'request_digest': research['request_digest'], 'outcome': 'answered', 'answer': 'The sealed map is complete.',
            'scope_complete': True, 'evidence_refs': [research['sources'][0]['ref']]}, 'INV-answer')
        engine.runtime['executions']['INV-answer'].update(status='ended', outcome='output_accepted')
        context, _, _ = engine.execute()
        self.assertTrue(context['supplemental_results'])
        self.assertNotIn('PRIVATE-INITIAL-PEER', json.dumps(context))
        self.assertEqual(engine.assessment()['review_cycle_id'], cid)
        self.assertEqual(engine.assessment()['basis'], kr.identity_basis(engine.instance, 'K1'))
        self.assertTrue(engine.usable())
        self.assertIn('INV-answer', engine.runtime['review_cycles'][cid]['execution_accounting']['executions_used'])
        from do_math.review_cycle import validate_sealed_review
        self.assertEqual(validate_sealed_review(engine.runtime['review_cycles'][cid], engine.runtime,
            instance=engine.instance)['decision'], 'match')

    def test_unadmitted_supplemental_execution_is_not_counted_late_at_acceptance(self):
        engine = self.engine
        defer_review_for_research(self.engine)
        action = next(a for a in engine.runtime['queue'] if a['role'] == 'supplemental_research')
        engine.runtime['executions']['UNADMITTED'] = {'id': 'UNADMITTED', 'role': 'supplemental_research', 'action': action}
        with self.assertRaisesRegex(ValueError, 'admitted before execution'):
            engine._apply_review_research(action, {}, 'UNADMITTED')

    def test_corrupt_fixed_research_source_is_a_local_diagnostic_on_slot_resume(self):
        engine = self.engine
        cid = defer_review_for_research(self.engine)
        investigation = next(a for a in engine.runtime['queue'] if a['role'] == 'supplemental_research')
        engine._abandon_review_research(investigation, 'INV-failed', 'failed before producing an answer')
        cycle = engine.runtime['review_cycles'][cid]
        request = cycle['research'][investigation['research_request_id']]
        source = request['source_records'][0]
        expected = source['sha256']
        source['inline'] = 'Changed after sealing'
        action = next(a for a in engine.runtime['queue'] if a['role'] == 'identity_review' and a['slot'] == request['action']['slot'])
        outcome = engine._prepare_review_context(action, engine.root / 'corrupt-fixed-source')
        event = outcome['recovery']['recovery_event']
        self.assertEqual(event['cause_kind'], 'fixed_source_content_mismatch')
        self.assertEqual(event['coordinate']['source_ref'], source['ref'])
        self.assertEqual(event['coordinate']['slot'], action['slot'])
        self.assertEqual(event['expected_sha256'], expected)
        self.assertNotEqual(event['observed_sha256'], expected)
        self.assertFalse(event['retryable'])

    def test_split_stopped_investigation_returns_to_its_original_slot(self):
        engine = self.engine
        cid = defer_review_for_research(self.engine)
        action = next(a for a in engine.runtime['queue'] if a['role'] == 'supplemental_research')
        execution = {'id': 'INV-stopped', 'role': 'supplemental_research', 'status': 'running', 'action': action,
                     'actor_kind': 'ai', 'owner_activity_id': action['owner_activity_id']}
        self.assertEqual(engine._admit_review_execution(action, execution)['disposition'], 'admitted')
        engine.runtime['executions']['INV-stopped'] = execution
        self.assertTrue(engine._abandon_review_research(action, 'INV-stopped', 'operator stopped this run'))
        cycle = engine.runtime['review_cycles'][cid]
        self.assertEqual(cycle['status'], 'working')
        request = cycle['research'][action['research_request_id']]
        self.assertEqual(request['result']['execution_status'], 'incomplete')
        self.assertIn(request['action'], next_actions(cycle))
        self.assertEqual(engine.instance['identity_assessments'], {})
        self.assertIn('INV-stopped', cycle['execution_accounting']['executions_used'])


class PureResearchTests(unittest.TestCase):
    def test_completed_investigation_is_private_until_its_requester_seals(self):
        cycle, action = deferred_research_cycle()
        self.assertNotIn(action, next_actions(cycle))
        request_id = next(iter(cycle['research']))
        cycle = accept_research_result(cycle, request_id, research_answer(cycle), 'investigator')
        peer = next(a for a in next_actions(cycle) if a['slot'] != action['slot'])
        self.assertEqual(context_for(cycle, peer)['supplemental_results'], [])
        self.assertEqual(len(context_for(cycle, action)['supplemental_results']), 1)
        self.assertEqual(cycle['results'], {})

    def test_wrong_question_and_partial_answer_are_not_accepted(self):
        cycle, _ = deferred_research_cycle()
        request_id = next(iter(cycle['research']))
        for field, value in [('request_digest', 'wrong'), ('research_request_id', 'wrong'), ('scope_complete', False), ('evidence_refs', [])]:
            output = research_answer(cycle); output[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                accept_research_result(cycle, request_id, output, 'investigator')
        self.assertIn('initial:1:initial-0', cycle['deferred_actions'])

    def test_deferred_initial_slot_does_not_allow_peer_to_finish_the_cycle(self):
        cycle, deferred = deferred_research_cycle()
        peer = next_actions(cycle)[0]
        output = {'proposal_digest': cycle['proposal_digest'], 'summary': 'All current material matched',
                  'used_sources': [], 'questions': [], 'decision': 'match', 'scope_complete': True, 'findings': []}
        cycle = accept_result(cycle, peer, output, 'peer')
        self.assertEqual(cycle['status'], 'working')
        self.assertEqual(cycle['sealed'], [])
        self.assertEqual(next_actions(cycle), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)

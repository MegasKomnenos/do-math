"""Fixed-question review investigations through the real engine and pure cycle."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.repository import canonical_json
from do_math.review_cycle import (start_review, next_actions, context_for, defer_for_research,
    accept_research_result, accept_result)
from test_purpose_engine import PurposeHarness, PurposeRunner, common, formal_fixture, EXPLANATION, parse_context
from do_math.engine import control


def signed_formal_fixture(**kwargs):
    result = formal_fixture(**kwargs)
    result['declaration_signatures'] = {'add_zero_fixture': '(n : Nat) -> n + 0 = n'}
    return result


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


class ReviewResearchEngineTests(PurposeHarness):
    def make_research(self, *, repeat=False, batch=False, **config):
        engine, previous_runner = self.make(**config)
        runner = InvestigationRunner(repeat=repeat, batch=batch)
        engine.runner = runner
        engine.formal_verifier = signed_formal_fixture
        self.runners[-1] = runner
        return engine, runner

    def test_common_document_overflow_waits_without_reconstructing_the_proposal(self):
        engine, runner = self.make_research()
        self.drive(engine, predicate=lambda e: bool(e.runtime['review_cycles']))
        action = next(a for a in engine.runtime['queue'] if a['role'] == 'identity_review')
        knowledge_id = action['target']
        before = deepcopy(engine.instance['knowledge'][knowledge_id])
        schema = engine._response_schema(action)
        common_bytes = len(engine._render_prompt('identity_review', {}, output_schema=schema).encode())
        engine.instance['config']['max_input_bytes'] = common_bytes - 1
        engine._save()
        calls = len(runner.calls)
        engine.run(max_steps=1)
        self.assertEqual(len(runner.calls), calls)
        self.assertEqual(engine.instance['knowledge'][knowledge_id], before)
        self.assertTrue(any(w['action'].get('id') == action['id'] and w['reason'] == 'input_overflow'
                            for w in engine.runtime.get('waiting_actions', {}).values()))
        self.assertFalse(any(a.get('reconstruction_target') == knowledge_id for a in engine.runtime['queue']))
        self.assertTrue(engine.runtime['questions'])

    def test_same_slot_defers_investigates_and_resumes_before_approval(self):
        engine, runner = self.make_research()
        self.drive(engine)
        self.assertEqual(len(runner.research_answers), 1)
        self.assertEqual(len(runner.resumed_contexts), 1)
        investigation = next(ex for ex in engine.runtime['executions'].values() if ex['role'] == 'supplemental_research')
        self.assertEqual(investigation['budget_kind'], 'work')
        cycle = next(iter(engine.runtime['review_cycles'].values()))
        self.assertEqual(cycle['decision'], 'match')
        self.assertEqual(len(cycle['results']), 2)
        self.assertFalse(cycle['deferred_actions'])
        request = next(iter(cycle['research'].values()))
        self.assertEqual(request['action']['slot'], 'initial-0')
        self.assertNotEqual(request['requested_by'], request['result']['execution_id'])
        self.assertEqual(request['result']['execution_id'], investigation['id'])
        self.assertEqual(runner.resumed_contexts[0]['action']['slot'], 'initial-0')
        self.assertTrue(any(message['role'] == 'tool' and message.get('kind') == 'supplemental_research'
                            for message in cycle['turns']['initial-0']))
        self.assertIn('declaration_signatures', cycle['proposal']['formal'])
        self.assertIn('signature_hash', cycle['proposal']['formal'])
        final_id = next(result['execution_id'] for result in cycle['results'].values() if result['action']['slot'] == 'initial-0')
        self.assertNotEqual(final_id, request['requested_by'])
        self.assertNotIn(request['requested_by'], {r['execution_id'] for r in cycle['results'].values()})

    def test_confirmed_withdrawal_closes_before_the_round_cap(self):
        engine, runner = self.make('dispute', review_rounds=3)
        engine.formal_verifier = signed_formal_fixture
        self.drive(engine)
        cycle = next(iter(engine.runtime['review_cycles'].values()))
        self.assertEqual(cycle['decision'], 'match')
        self.assertEqual(cycle['round'], 2)
        self.assertEqual(sum(call['role'] == 'identity_review' and call['action']['stage'] == 'answer' for call in runner.calls), 1)

    def test_all_fixed_questions_return_before_resuming_the_deferred_slot(self):
        engine, runner = self.make_research(batch=True)
        self.drive(engine)
        self.assertEqual(len(runner.research_answers), 2)
        self.assertEqual(len(runner.resumed_contexts), 1)
        self.assertEqual(len(runner.resumed_contexts[0]['supplemental_results']), 2)
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
        self.assertEqual(next(iter(engine.instance['knowledge'].values()))['status'], 'unresolved')
        self.assertFalse(any(a.get('review_cycle_id') == cycle['id'] for a in engine.runtime['queue']))
        self.assertTrue(any('external textbook definition' in question for question in engine.runtime['questions']))

    def test_optional_investigation_cannot_consume_reserved_final_review_calls(self):
        engine, runner = self.make_research(work_calls=6)
        self.drive(engine, predicate=lambda e: any(c['status'] == 'unresolved' for c in e.runtime['review_cycles'].values()))
        self.assertFalse(runner.research_answers)
        self.assertEqual(next(iter(engine.runtime['review_cycles'].values()))['decision'], 'unresolved')

    def test_unlimited_work_budget_admits_fixed_question_research(self):
        engine, runner = self.make_research(work_calls=None, operations_calls=None)
        self.drive(engine)
        self.assertTrue(runner.research_answers)
        self.assertEqual(engine.instance['goal_status'], 'mathematically_solved')

    def test_initial_peer_question_is_not_exposed_before_phase_seal(self):
        engine, runner = self.make_research()
        original = runner.answer
        def question(role, context, workspace):
            if role == 'identity_review' and context['action']['stage'] == 'initial' and context['action']['slot'] == 'initial-0':
                return {**common('Review remains uncertain'), 'questions': ['PRIVATE-PEER-DOMAIN-QUESTION'],
                    'proposal_digest': context['role_review']['proposal_digest'], 'decision': 'unresolved', 'scope_complete': True, 'findings': []}
            return original(role, context, workspace)
        runner.answer = question
        self.drive(engine, predicate=lambda e: any(ex['role'] == 'identity_review' and ex.get('outcome') == 'output_accepted'
                                                  for ex in e.runtime['executions'].values()))
        action = next(a for a in engine.runtime['queue'] if a['role'] == 'identity_review')
        context = engine._context(action, self.root / 'peer-context')
        self.assertNotIn('PRIVATE-PEER-DOMAIN-QUESTION', json.dumps(context))

    def test_investigator_does_not_receive_unsealed_peer_summary(self):
        engine, runner = self.make_research()
        original = runner.answer
        def peer_summary(role, context, workspace):
            output = original(role, context, workspace)
            if role == 'identity_review' and context['action']['stage'] == 'initial' and context['action']['slot'] == 'initial-1':
                output['summary'] = 'PRIVATE-PEER-SUMMARY'
            return output
        runner.answer = peer_summary
        self.drive(engine, predicate=lambda e: any(ex['role'] == 'identity_review' and ex['action']['slot'] == 'initial-1'
                    and ex.get('outcome') == 'output_accepted' for ex in e.runtime['executions'].values()))
        action = next(a for a in engine.runtime['queue'] if a['role'] == 'supplemental_research')
        context = engine._context(action, self.root / 'investigator-context')
        self.assertNotIn('PRIVATE-PEER-SUMMARY', json.dumps(context))

    def test_success_clears_only_the_cause_for_this_trust_transition(self):
        engine, runner = self.make()
        engine.formal_verifier = signed_formal_fixture
        self.drive(engine, predicate=lambda e: bool(e.runtime['review_cycles']))
        cycle = next(iter(engine.runtime['review_cycles'].values()))
        item = next(iter(engine.instance['knowledge'].values()))
        cycle['trust_transition_id'] = 'TR-current'
        matching = {'kind': 'semantic', 'transition_id': 'TR-current', 'review_cycle_id': cycle['id'], 'reason': 'This transition needs semantic review'}
        unrelated = [{'kind': 'semantic', 'transition_id': 'TR-other', 'reason': 'Another meaning dispute'},
                     {'kind': 'dependency', 'reason': 'An independent dependency is suspended'},
                     {'kind': 'environment', 'reason': 'Another environment cause is unresolved'}]
        item['use_suspended'] = True
        item['use_suspensions'] = [matching, *deepcopy(unrelated)]
        item['use_suspension_reasons'] = [cause['reason'] for cause in item['use_suspensions']]
        engine._save()
        self.drive(engine, predicate=lambda e: e.runtime['review_cycles'][cycle['id']]['status'] == 'completed')
        item = engine.instance['knowledge'][item['id']]
        self.assertEqual(item['use_suspensions'], unrelated)
        self.assertTrue(item['use_suspended'])
        self.assertFalse(item['identity_assessment']['effective'])

    def test_success_restores_use_when_only_this_transition_cause_remained(self):
        engine, _ = self.make()
        engine.formal_verifier = signed_formal_fixture
        self.drive(engine, predicate=lambda e: bool(e.runtime['review_cycles']))
        cycle = next(iter(engine.runtime['review_cycles'].values()))
        item = next(iter(engine.instance['knowledge'].values()))
        cycle['trust_transition_id'] = 'TR-current'
        item['use_suspended'] = True
        item['use_suspensions'] = [{'kind': 'semantic', 'transition_id': 'TR-current', 'review_cycle_id': cycle['id'],
                                    'reason': 'This transition needs semantic review'}]
        item['use_suspension_reasons'] = ['This transition needs semantic review']
        engine._save()
        self.drive(engine)
        item = engine.instance['knowledge'][item['id']]
        self.assertFalse(item['use_suspended'])
        self.assertEqual(item['use_suspensions'], [])
        self.assertTrue(item['identity_assessment']['effective'])

    def test_user_revision_cancels_old_investigation_and_reviews_new_revision(self):
        engine, runner = self.make_research()
        self.drive(engine, predicate=lambda e: any(a['role'] == 'supplemental_research' for a in e.runtime['queue']))
        item = next(iter(engine.instance['knowledge'].values()))
        old_cycle_id = item['review_cycle_id']
        control(self.repo, engine.instance['id'], 'knowledge', config={'operation': 'revise', 'id': item['id'],
            'changes': {'explanation': EXPLANATION + ' The revised statement explicitly retains that domain.'}, 'reason': 'Explicit source revision'})
        engine.process_controls()
        self.assertFalse(any(a.get('review_cycle_id') == old_cycle_id for a in engine.runtime['queue']))
        old_cycle = engine.runtime['review_cycles'][old_cycle_id]
        self.assertEqual(old_cycle['status'], 'unresolved')
        self.assertTrue(all(r['status'] == 'cancelled' for r in old_cycle['research'].values()))
        self.drive(engine)
        self.assertNotEqual(engine.instance['knowledge'][item['id']]['review_cycle_id'], old_cycle_id)
        self.assertTrue(engine.instance['knowledge'][item['id']]['identity_assessment']['effective'])

    def test_supplemental_evidence_is_readable_again_in_the_next_revision(self):
        engine, runner = self.make_research()
        self.drive(engine)
        item = next(iter(engine.instance['knowledge'].values()))
        control(self.repo, engine.instance['id'], 'knowledge', config={'operation': 'revise', 'id': item['id'],
            'changes': {'explanation': EXPLANATION + ' This revision adds an explicit domain reminder.'}, 'reason': 'New proposal revision'})
        self.drive(engine)
        self.assertEqual(len(runner.research_answers), 1)
        self.assertEqual(len(runner.resumed_contexts), 2)
        self.assertIn('previous_revision', runner.resumed_contexts[-1]['supplemental_results'][0])

    def test_inline_stop_returns_execution_incomplete_to_the_requesting_slot(self):
        engine, previous = self.make_research()
        class StoppedInvestigator(InvestigationRunner):
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
                return {'status': 'stopped', 'output': None, 'usage': {}, 'error': 'Investigator stopped after the operational decision'}
            def answer(self, role, context, workspace):
                if role == 'operational_review':
                    return {**common('Preserve the blocked investigation and return it to its owner'), 'decision': 'stop', 'reason': 'The fixed evidence is unavailable'}
                return super().answer(role, context, workspace)
        runner = StoppedInvestigator()
        engine.runner = runner
        self.runners[-1] = runner
        self.drive(engine, predicate=lambda e: any(r.get('result', {}).get('execution_status') == 'incomplete'
            for c in e.runtime['review_cycles'].values() for r in c.get('research', {}).values() if r.get('result')))
        cycle = next(iter(engine.runtime['review_cycles'].values()))
        self.assertEqual(cycle['status'], 'working')
        self.assertEqual(engine.runtime['status'], 'paused')
        self.assertFalse(cycle['deferred_actions'])
        self.assertTrue(any(a['slot'] == 'initial-0' for a in next_actions(cycle)))
        self.assertEqual(next(iter(cycle['research'].values()))['result']['output']['outcome'], 'unresolved')


class PureResearchTests(unittest.TestCase):
    def fixture(self):
        cycle = start_review({'revision': 1}, reviewers=2)
        action = next_actions(cycle)[0]
        output = {'proposal_digest': cycle['proposal_digest'], 'summary': 'Need exact domain evidence',
                  'used_sources': [], 'questions': [], 'decision': 'unresolved', 'scope_complete': False, 'findings': []}
        requests = [{'id': 'r', 'question': 'What is the exact domain?', 'source_refs': ['proposal']}]
        return defer_for_research(cycle, action, output, requests, 'requester'), action

    def result(self, cycle):
        request = next(iter(cycle['research'].values()))
        return {'summary': 'Domain recovered', 'used_sources': ['proposal'], 'questions': [],
                'research_request_id': request['id'], 'request_digest': request['request_digest'],
                'outcome': 'answered', 'answer': 'The domain is Nat.', 'scope_complete': True, 'evidence_refs': ['proposal']}

    def test_completed_investigation_is_private_until_its_requester_seals(self):
        cycle, action = self.fixture()
        self.assertNotIn(action, next_actions(cycle))
        request_id = next(iter(cycle['research']))
        cycle = accept_research_result(cycle, request_id, self.result(cycle), 'investigator')
        peer = next(a for a in next_actions(cycle) if a['slot'] != action['slot'])
        self.assertEqual(context_for(cycle, peer)['supplemental_results'], [])
        self.assertEqual(len(context_for(cycle, action)['supplemental_results']), 1)
        self.assertEqual(cycle['results'], {})

    def test_wrong_question_and_partial_answer_are_not_accepted(self):
        cycle, _ = self.fixture()
        request_id = next(iter(cycle['research']))
        for field, value in [('request_digest', 'wrong'), ('research_request_id', 'wrong'), ('scope_complete', False), ('evidence_refs', [])]:
            output = self.result(cycle); output[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                accept_research_result(cycle, request_id, output, 'investigator')
        self.assertIn('initial:1:initial-0', cycle['deferred_actions'])

    def test_deferred_initial_slot_does_not_allow_peer_to_finish_the_cycle(self):
        cycle, deferred = self.fixture()
        peer = next_actions(cycle)[0]
        output = {'proposal_digest': cycle['proposal_digest'], 'summary': 'All current material matched',
                  'used_sources': [], 'questions': [], 'decision': 'match', 'scope_complete': True, 'findings': []}
        cycle = accept_result(cycle, peer, output, 'peer')
        self.assertEqual(cycle['status'], 'working')
        self.assertEqual(cycle['sealed'], [])
        self.assertEqual(next_actions(cycle), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)

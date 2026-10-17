"""A finished identity review replays from its sealed evidence (``review_cycle.validate_sealed_review``, layer 2).

Three tests build pure cycles; the replacement test runs the review on the
real engine over the stored review state (``support.review_scene``).
"""
import copy
import tempfile
import unittest

from do_math.review_cycle import (accept_research_result, accept_result, defer_for_research, next_actions,
                                  record_recovery_event, start_review, validate_sealed_review)
from support.review_inputs import deferred_research_cycle, grant_replacement, research_answer, review_stage_output, scoped_start
from support.review_scene import ReviewScene, warm


def setUpModule():
    warm()


class SealedReplayTests(unittest.TestCase):
    def test_budget_closed_investigation_is_verified_unresolved_not_an_unfinished_vote(self):
        from support.entry import entry
        _entry = entry()
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
        instance = {'config': config, **build_profiles(config, host=_entry.ports.host)}
        profile = next(p for p in instance['execution_profiles'].values() if p['role'] == 'identity_review')
        runtime['executions']['requester'].update(actor_kind='ai', execution_profile_ref=profile_ref(profile))
        result = validate_sealed_review(cycle, runtime, instance=instance, at=_entry.ports.clock.now(), clock=_entry.ports.clock)
        self.assertEqual((result['status'], result['decision']), ('unresolved', 'unresolved'))
        instance['config']['review_research_limit'] = 3
        with self.assertRaisesRegex(ValueError, 'review closure limit no longer matches its governing configuration'):
            validate_sealed_review(cycle, runtime, instance=instance, at=_entry.ports.clock.now(), clock=_entry.ports.clock)

    def test_authorized_replacement_keeps_full_authority_and_sealed_input(self):
        """A replaced slot's review on the real engine replays with its sealed input hash."""
        from support.entry import entry
        _entry = entry()
        with tempfile.TemporaryDirectory() as directory:
            scene = ReviewScene(directory)
            engine = scene.engine
            grant_replacement(engine)
            cid = scene.start('K1')
            action = scene.pending()
            cycle = engine.runtime['review_cycles'][cid]
            short = {k: action[k] for k in ('stage', 'slot', 'round')}
            engine.runtime['review_cycles'][cid] = record_recovery_event(cycle, short,
                {'reason': 'lost exact public transcript', 'retryable': False, 'preserved_range': {'slot': action['slot']}})
            outcome = engine._authorize_review_replacement(action, grant_id='GR-review')
            self.assertEqual(outcome['disposition'], 'replacement_ready')
            while any(a['role'] == 'identity_review' for a in engine.runtime['queue']):
                scene.execute()
            cycle = engine.runtime['review_cycles'][cid]
            self.assertIn('sealed_input_sha256', cycle['replacement_receipts'][0]['authorization'])
            self.assertEqual(validate_sealed_review(cycle, engine.runtime, instance=engine.instance, at=engine.ports.clock.now(), clock=engine.ports.clock)['decision'], 'match')
            cycle['replacement_receipts'][0]['authorization']['sealed_input_sha256'] = 'changed'
            with self.assertRaisesRegex(ValueError, 'replacement sealed input changed'):
                validate_sealed_review(cycle, engine.runtime, instance=engine.instance, at=engine.ports.clock.now(), clock=engine.ports.clock)

    def test_previous_review_must_resolve_to_its_actual_preserved_cycle(self):
        from do_math.canonical import exact_content_hash
        from do_math.review_cycle import _replacement_sealed_input
        from support.entry import entry
        _entry = entry()
        runtime = {'executions': {}, 'review_cycles': {}}
        sealed_inputs = []
        previous = None
        for revision in (1, 2):
            seed = scoped_start({'revision': revision}, reviewers=2)
            cycle = start_review({'revision': revision}, reviewers=2, previous=previous,
                policy=seed['review_policy'], scope_assessment=seed['scope_assessment'])
            sealed_inputs.append(exact_content_hash(_replacement_sealed_input(cycle, [])))
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
        self.assertNotEqual(sealed_inputs[0], sealed_inputs[1])
        self.assertEqual(validate_sealed_review(cycle, runtime, at=_entry.ports.clock.now(), clock=_entry.ports.clock)['decision'], 'match')
        forged = copy.deepcopy(cycle)
        next(iter(forged['results'].values()))['stage'] = 'judge'
        with self.assertRaisesRegex(ValueError, 'review conclusion differs from sealed evidence'):
            validate_sealed_review(forged, runtime, at=_entry.ports.clock.now(), clock=_entry.ports.clock)
        del runtime['review_cycles']['cycle-1']
        with self.assertRaisesRegex(ValueError, 'previous review does not resolve to one preserved cycle'):
            validate_sealed_review(cycle, runtime, at=_entry.ports.clock.now(), clock=_entry.ports.clock)

    def test_fixed_private_research_is_replayed_before_requesters_final_vote(self):
        from support.entry import entry
        _entry = entry()
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
        self.assertEqual(validate_sealed_review(cycle, runtime, at=_entry.ports.clock.now(), clock=_entry.ports.clock)['decision'], 'match')
        runtime['executions']['investigator']['output']['request_digest'] = 'forged'
        with self.assertRaisesRegex(ValueError, 'review result is not bound to its actual accepted execution'):
            validate_sealed_review(cycle, runtime, at=_entry.ports.clock.now(), clock=_entry.ports.clock)


if __name__ == '__main__':
    unittest.main()

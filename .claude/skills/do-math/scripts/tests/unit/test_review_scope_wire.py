"""A scope response satisfies both the installed wire and the review consumer (``review_cycle``, ``review_policy``, layer 2).

The wire is the scope seat schema with the live proposal digest bound and the
integration envelope around it, as the engine builds it for a review seat; the
consumer is the pure review cycle and the policy's scope check. The expanded
revision test opens the next review on the real engine over a stored review
state (``support.review_scene``).
"""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

import jsonschema

from do_math import contracts, execution_profiles, review_cycle, review_policy
from do_math.configuration import DEFAULT_CONFIG
from support.role_answers import scope_response
from support.review_scene import ReviewScene, warm


def setUpModule():
    warm()


class ScopeWireTests(unittest.TestCase):
    def setUp(self):
        from support.entry import entry
        _entry = entry()
        self.policy = review_policy.build_review_policy(None, reviewer_count=2, max_rounds=2)
        profile = next(p for p in execution_profiles.build_profiles(deepcopy(DEFAULT_CONFIG), host=_entry.ports.host)['execution_profiles'].values()
                       if p['role'] == 'identity_review')
        self.response = {'summary': 'Scope the complete fixture proposal', 'used_sources': [], 'questions': [],
            **scope_response({'role_review': {'review_policy': self.policy, 'proposal_digest': 'fixture-proposal'},
                              'execution_profile': profile}),
            'integration_bundles': [{'integration_id': 'IN-scope', 'members': ['output'],
                                     'impact_set': [], 'authority_refs': []}]}
        # The installed wire as engine._response_schema builds it for a review seat:
        # _review_schema binds the live proposal digest, then the integration envelope.
        self.wire = self.installed_wire('fixture-proposal')

    @staticmethod
    def installed_wire(digest):
        seat = review_cycle.stage_schema('scope')
        seat['properties']['proposal_digest'] = {**seat['properties']['proposal_digest'], 'enum': [digest]}
        return contracts.with_integration_schema(seat)

    def test_review_storage_keeps_local_source_alias_without_widening_source_records(self):
        from do_math.record_schemas import RECORDS, RUNTIME_FIELDS
        source = {'id': 'SO-input', 'name': 'notes.txt', 'path': 'sources/notes.txt',
                  'sha256': 'a' * 64, 'bytes': 3}
        jsonschema.Draft202012Validator(RECORDS['sources']).validate(source)
        supplied = {**source, 'local_path': 'input/sources/0000-notes.txt'}
        prepared = {'proposal_digest': 'b' * 64, 'proposal': {}, 'request': {}, 'slot': 'scope',
            'visible_execution_ids': [], 'workspace': 'workspace', 'supplied_sources': [supplied],
            'source_snapshot': 'c' * 40}
        jsonschema.Draft202012Validator(RUNTIME_FIELDS['review_inputs']).validate({'RC-fixture:scope:1:scope': prepared})
        with self.assertRaisesRegex(jsonschema.ValidationError, r"Additional properties are not allowed \('local_path' was unexpected\)"):
            jsonschema.Draft202012Validator(RECORDS['sources']).validate(supplied)

    def test_review_action_keeps_replacement_authority_only_for_a_replacement(self):
        execution_action = {'id': 'AC-execution', 'role': 'identity_review',
            'stage': 'scope', 'slot': 'scope', 'round': 1, 'grant_id': 'GR-running',
            'actor_kind': 'ai'}
        self.assertEqual(review_cycle.review_action(execution_action),
                         {'stage': 'scope', 'slot': 'scope', 'round': 1})
        replacement = {**execution_action, 'replacement_for': 'initial-0',
            'grant_sha256': 'a' * 64, 'continuity_broken': True, 'purpose': 'recorded repair',
            'continuity_break_cause': 'permanent loss'}
        projected = review_cycle.review_action(replacement)
        for key in ('id', 'replacement_for', 'grant_id', 'grant_sha256', 'continuity_broken',
                    'actor_kind', 'purpose', 'continuity_break_cause'):
            self.assertEqual(projected[key], replacement[key])

    def test_one_real_response_contract_reaches_the_consumer(self):
        self.assertEqual(list(jsonschema.Draft202012Validator(self.wire).iter_errors(self.response)), [])
        body = {key: value for key, value in self.response.items() if key != 'integration_bundles'}
        self.assertEqual(list(jsonschema.Draft202012Validator(review_cycle.stage_schema('scope')).iter_errors(body)), [])
        self.assertEqual(review_policy.validate_scope_assessment(body['scope_assessment'], self.policy),
                         body['scope_assessment'])

    def test_submission_checks_scope_with_the_conditions_the_review_accepts(self):
        from support.entry import entry
        _entry = entry()
        from do_math import submission
        cycle = review_cycle.start_review({'revision': 1}, 2, max_rounds=2, policy=self.policy)
        cycle['execution_accounting']['executions_used'] = ['EX-scope']
        action = review_cycle.next_actions(cycle)[0]
        context = {'action': {'role': 'identity_review', 'review_cycle_id': 'RC-fixture', **action},
                   'role_review': review_cycle.context_for(cycle, action)}
        wire = self.installed_wire(cycle['proposal_digest'])
        response = {**deepcopy(self.response), 'proposal_digest': cycle['proposal_digest']}
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(submission._payload_issues(response, wire, context, {}, Path(directory), clock=_entry.ports.clock), [])
            other_policy = deepcopy(response)
            other_policy['scope_assessment']['policy_id'] = 'RP-other'
            issues = submission._payload_issues(other_policy, wire, context, {}, Path(directory), clock=_entry.ports.clock)
            self.assertEqual([row['path'] for row in issues], ['output'], issues)
            self.assertIn('scope assessment belongs to another review policy', issues[0]['message'])
            with self.assertRaisesRegex(ValueError, 'scope assessment belongs to another review policy'):
                review_cycle.accept_result(cycle, action, {key: value for key, value in other_policy.items()
                                                           if key != 'integration_bundles'}, 'EX-scope-result')
            # An honest partial reading and an open question are reported, not refused:
            # the sealed scope result carries both to every initial seat.
            reported = {**deepcopy(response), 'scope_complete': False, 'questions': ['Which domain is intended?']}
            self.assertEqual(submission._payload_issues(reported, wire, context, {}, Path(directory), clock=_entry.ports.clock), [])
            scoped = review_cycle.accept_result(cycle, action, {key: value for key, value in reported.items()
                                                                if key != 'integration_bundles'}, 'EX-scope-result')
            initial = review_cycle.next_actions(scoped)[0]
            sealed = review_cycle.context_for(scoped, initial)['completed_results']['scope:1:scope']
            self.assertEqual(sealed['output']['questions'], ['Which domain is intended?'])
            self.assertIs(sealed['output']['scope_complete'], False)

    def test_wire_rejects_missing_proposal_binding_and_invalid_scope_details(self):
        validator = jsonschema.Draft202012Validator(self.wire)
        for missing in ('proposal_digest', 'scope_complete'):
            changed = deepcopy(self.response)
            changed.pop(missing)
            with self.subTest(missing=missing), \
                    self.assertRaisesRegex(jsonschema.ValidationError, f"'{missing}' is a required property"):
                validator.validate(changed)
        changed = deepcopy(self.response)
        changed['scope_assessment'] = {'policy_id': self.policy['id']}
        errors = list(validator.iter_errors(changed))
        self.assertEqual({(tuple(error.path), error.message) for error in errors},
                         {(('scope_assessment',), f"'{field}' is a required property")
                          for field in ('assessment_id', 'required_perspectives', 'initial_slots', 'selected_profile_ref',
                                        'activity_execution_limit', 'overflow_disposition')})


class ExpandedScopeRevisionTests(unittest.TestCase):
    def test_revision_retains_all_prior_slots_above_the_policy_minimum(self):
        """The real engine opens the next revision's review from a completed three-slot review of ``K1``."""
        with tempfile.TemporaryDirectory() as directory:
            scene = ReviewScene(directory)
            engine = scene.engine
            policy = review_policy.build_review_policy(reviewer_count=2, max_rounds=2)
            engine.instance['review_policy'] = policy
            slots = ['initial-0', 'initial-1', 'specialist']
            scope = {'assessment_id': 'SA-expanded', 'policy_id': policy['id'],
                'required_perspectives': [], 'initial_slots': [
                    {'id': slot, 'perspective': 'full proposal', 'required_source_refs': ['proposal']}
                    for slot in slots], 'selected_profile_ref': None,
                'activity_execution_limit': policy['activity_execution_limit'], 'overflow_disposition': 'unresolved'}
            old_id = scene.start('K1', scope=scope)
            for _ in slots:
                scene.execute()
            previous = engine.runtime['review_cycles'][old_id]
            self.assertEqual((previous['status'], previous['decision'], previous['reviewer_slots']),
                             ('completed', 'match', slots))
            kid = scene.revise()
            engine.runtime['queue'].clear()
            cid = engine._start_identity_review(kid, previous_cycle_id=old_id)
            current = engine.runtime['review_cycles'][cid]
            self.assertEqual(current['retained_reviewer_slots'], slots)
            self.assertEqual(current['requested_reviewer_slots'], slots)
            self.assertEqual(current['phase'], 'scope')
            self.assertEqual(current['results'], {})
            self.assertIsNone(current['decision'])
            self.assertEqual(current['previous_reviews'][-1]['decision'], 'match')
            self.assertEqual([(a['target'], a['review_cycle_id'], a['stage']) for a in engine.runtime['queue']
                              if a['role'] == 'identity_review'], [(kid, cid, 'scope')])
            next_scope = {**deepcopy(scope), 'assessment_id': 'SA-next'}
            next_scope['initial_slots'].pop()
            action = review_cycle.next_actions(current)[0]
            # The scope seat receives the seats it must keep and the proposal the new revision replaces,
            # so the shared submission check refuses the removal before central receipt.
            visible = review_cycle.context_for(current, action)
            self.assertEqual(visible['retained_reviewer_slots'], slots)
            self.assertEqual(visible['previous_reviews'][-1]['proposal'], previous['proposal'])
            removal = {'proposal_digest': current['proposal_digest'], 'summary': 'Incorrectly removes a seat',
                       'used_sources': ['proposal'], 'questions': [], 'scope_complete': True, 'scope_assessment': next_scope}
            with self.assertRaisesRegex(ValueError, 'new scope assessment cannot remove retained logical slots'):
                review_cycle.validate_visible_output(visible, action, deepcopy(removal))
            with self.assertRaisesRegex(ValueError, 'new scope assessment cannot remove retained logical slots'):
                review_cycle.accept_result(current, action, deepcopy(removal), 'EX-next-scope')


if __name__ == '__main__':
    unittest.main()

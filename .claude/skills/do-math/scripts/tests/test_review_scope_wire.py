"""A scope response must satisfy both the installed wire and review consumer."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

import jsonschema

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import contracts, execution_profiles, review_cycle, review_policy
from do_math.configuration import DEFAULT_CONFIG
from research_fixtures import bare_engine, scope_response


class ScopeWireTests(unittest.TestCase):
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
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.Draft202012Validator(RECORDS['sources']).validate(supplied)

    def test_review_action_keeps_replacement_authority_only_for_a_replacement(self):
        execution_action = {'id': 'AC-execution', 'role': 'identity_review',
            'stage': 'scope', 'slot': 'scope', 'round': 1, 'grant_id': 'GR-running',
            'actor_kind': 'ai'}
        self.assertEqual(review_cycle.review_action(execution_action),
                         {'stage': 'scope', 'slot': 'scope', 'round': 1})
        replacement = {**execution_action, 'replacement_for': 'initial-0',
            'grant_sha256': 'a'*64, 'continuity_broken': True, 'purpose': 'recorded repair',
            'continuity_break_cause': 'permanent loss'}
        projected = review_cycle.review_action(replacement)
        for key in ('id', 'replacement_for', 'grant_id', 'grant_sha256', 'continuity_broken',
                    'actor_kind', 'purpose', 'continuity_break_cause'):
            self.assertEqual(projected[key], replacement[key])

    def setUp(self):
        self.policy = review_policy.build_review_policy(None, reviewer_count=2, max_rounds=2)
        profile = next(p for p in execution_profiles.build_profiles(deepcopy(DEFAULT_CONFIG))["execution_profiles"].values()
                       if p["role"] == "identity_review")
        self.response = {"summary": "Scope the complete fixture proposal", "used_sources": [], "questions": [],
            **scope_response({"role_review": {"review_policy": self.policy, "proposal_digest": "fixture-proposal"},
                              "execution_profile": profile}),
            "integration_bundles": [{"integration_id": "IN-scope", "members": ["output"],
                                      "impact_set": [], "authority_refs": []}]}
        # The installed wire as engine._response_schema builds it for a review seat:
        # _review_schema binds the live proposal digest, then the integration envelope.
        seat = review_cycle.stage_schema("scope")
        seat["properties"]["proposal_digest"] = {**seat["properties"]["proposal_digest"], "enum": ["fixture-proposal"]}
        self.wire = contracts.with_integration_schema(seat)

    def test_one_real_response_contract_reaches_the_consumer(self):
        jsonschema.Draft202012Validator(self.wire).validate(self.response)
        body = {key: value for key, value in self.response.items() if key != "integration_bundles"}
        jsonschema.Draft202012Validator(review_cycle.stage_schema("scope")).validate(body)
        review_policy.validate_scope_assessment(body["scope_assessment"], self.policy)

    def test_submission_checks_scope_with_the_conditions_the_review_accepts(self):
        from do_math import submission
        import tempfile
        cycle = review_cycle.start_review({'revision': 1}, 2, max_rounds=2, policy=self.policy)
        cycle['execution_accounting']['executions_used'] = ['EX-scope']
        action = review_cycle.next_actions(cycle)[0]
        context = {'action': {'role': 'identity_review', 'review_cycle_id': 'RC-fixture', **action},
                   'role_review': review_cycle.context_for(cycle, action)}
        seat = review_cycle.stage_schema("scope")
        seat["properties"]["proposal_digest"] = {**seat["properties"]["proposal_digest"], "enum": [cycle["proposal_digest"]]}
        wire = contracts.with_integration_schema(seat)
        response = {**deepcopy(self.response), 'proposal_digest': cycle['proposal_digest']}
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(submission._payload_issues(response, wire, context, {}, Path(directory)), [])
            other_policy = deepcopy(response)
            other_policy['scope_assessment']['policy_id'] = 'RP-other'
            incomplete = {**deepcopy(response), 'scope_complete': False}
            open_question = {**deepcopy(response), 'questions': ['Which domain is intended?']}
            for label, changed in (('policy', other_policy), ('scope_complete', incomplete), ('questions', open_question)):
                with self.subTest(changed=label):
                    issues = submission._payload_issues(changed, wire, context, {}, Path(directory))
                    self.assertEqual([row['path'] for row in issues], ['output'], issues)
                    with self.assertRaises(ValueError):
                        review_cycle.accept_result(cycle, action, {key: value for key, value in changed.items()
                                                                   if key != 'integration_bundles'}, 'EX-scope-result')

    def test_wire_rejects_missing_proposal_binding_and_invalid_scope_details(self):
        for missing in ("proposal_digest", "scope_complete"):
            changed = deepcopy(self.response)
            changed.pop(missing)
            with self.assertRaises(jsonschema.ValidationError):
                jsonschema.Draft202012Validator(self.wire).validate(changed)
        changed = deepcopy(self.response)
        changed["scope_assessment"] = {"policy_id": self.policy["id"]}
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.Draft202012Validator(self.wire).validate(changed)


class ExpandedScopeRevisionTests(unittest.TestCase):
    def test_revision_retains_all_prior_slots_above_the_policy_minimum(self):
        from unittest.mock import create_autospec, patch
        policy = review_policy.build_review_policy(reviewer_count=2, max_rounds=2)
        slots = ['initial-0', 'initial-1', 'specialist']
        scope = {'assessment_id': 'SA-expanded', 'policy_id': policy['id'],
            'required_perspectives': [], 'initial_slots': [
                {'id': slot, 'perspective': 'full proposal', 'required_source_refs': ['proposal']}
                for slot in slots], 'selected_profile_ref': None,
            'activity_execution_limit': policy['activity_execution_limit'], 'overflow_disposition': 'unresolved'}
        previous = review_cycle.start_review({'id': 'KN-old', 'revision': 1}, 2,
            policy=policy, scope_assessment=scope)
        for index, action in enumerate(review_cycle.next_actions(previous)):
            previous = review_cycle.accept_result(previous, action, {
                'proposal_digest': previous['proposal_digest'], 'summary': 'Complete comparison',
                'used_sources': ['proposal'], 'questions': [], 'decision': 'match',
                'scope_complete': True, 'findings': []}, 'EX-prior-' + str(index))
        previous.update(id='RC-old', knowledge_id='KN-old')
        owner = bare_engine({'knowledge': {'KN-new': {'id': 'KN-new', 'supersedes': 'KN-old'}},
                             'config': {}, 'review_policy': policy},
                            {'review_cycles': {'RC-old': previous}}, head='fixed-input')
        owner._settle_review_resource_dispositions = create_autospec(owner._settle_review_resource_dispositions,
                                                                     return_value=None)
        owner._review_publication_premises = create_autospec(owner._review_publication_premises, return_value={})
        queued = []
        owner._queue_identity_actions = create_autospec(owner._queue_identity_actions,
                                                        side_effect=lambda kid, cid: queued.append((kid, cid)))
        with patch('do_math.review_engine._proposal', return_value={'id': 'KN-new', 'revision': 2}), \
                patch('do_math.review_engine.kr.identity_basis', return_value={}):
            cid = owner._start_identity_review('KN-new', previous_cycle_id='RC-old')
        current = owner.runtime['review_cycles'][cid]
        self.assertEqual(current['retained_reviewer_slots'], slots)
        self.assertEqual(current['requested_reviewer_slots'], slots)
        self.assertEqual(current['phase'], 'scope')
        self.assertEqual(current['results'], {})
        self.assertIsNone(current['decision'])
        self.assertEqual(current['previous_reviews'][-1]['decision'], 'match')
        self.assertEqual(queued, [('KN-new', cid)])
        next_scope = {**deepcopy(scope), 'assessment_id': 'SA-next'}
        next_scope['initial_slots'].pop()
        action = review_cycle.next_actions(current)[0]
        with self.assertRaisesRegex(ValueError, 'retained logical slots'):
            review_cycle.accept_result(current, action, {
                'proposal_digest': current['proposal_digest'], 'summary': 'Incorrectly removes a seat',
                'used_sources': ['proposal'], 'questions': [], 'scope_complete': True,
                'scope_assessment': next_scope}, 'EX-next-scope')
if __name__ == "__main__":
    unittest.main()

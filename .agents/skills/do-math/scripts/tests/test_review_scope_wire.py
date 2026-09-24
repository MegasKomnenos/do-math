"""A scope response must satisfy both the installed wire and review consumer."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

import jsonschema

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import contracts, execution_profiles, review_cycle, review_policy
from do_math.engine import DEFAULT_CONFIG
from research_fixtures import scope_response


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
            'actor_kind': 'ai', 'budget_kind': 'work'}
        self.assertEqual(review_cycle.review_action(execution_action),
                         {'stage': 'scope', 'slot': 'scope', 'round': 1})
        replacement = {**execution_action, 'replacement_for': 'initial-0',
            'grant_sha256': 'a'*64, 'continuity_broken': True, 'purpose': 'recorded repair',
            'continuity_break_cause': 'permanent loss'}
        projected = review_cycle.review_action(replacement)
        for key in ('id', 'replacement_for', 'grant_id', 'grant_sha256', 'continuity_broken',
                    'actor_kind', 'budget_kind', 'purpose', 'continuity_break_cause'):
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
        self.wire = contracts.action_schema({"role": "identity_review", "stage": "scope", "review_cycle_id": "RC-fixture"})

    def test_one_real_response_contract_reaches_the_consumer(self):
        jsonschema.Draft202012Validator(self.wire).validate(self.response)
        body = {key: value for key, value in self.response.items() if key != "integration_bundles"}
        jsonschema.Draft202012Validator(review_cycle.stage_schema("scope")).validate(body)
        review_policy.validate_scope_assessment(body["scope_assessment"], self.policy)

    def test_submission_checks_scope_against_the_seat_policy(self):
        from do_math import submission
        import tempfile
        context = {'action': {'role': 'identity_review', 'stage': 'scope',
                   'review_cycle_id': 'RC-fixture'},
                   'role_review': {'review_policy': self.policy, 'scope_executions_used': 1}}
        with tempfile.TemporaryDirectory() as directory:
            issues = submission._payload_issues(self.response, self.wire, context, {}, Path(directory))
            self.assertFalse([row for row in issues if row['path'] == 'output/scope_assessment'], issues)
            changed = deepcopy(self.response)
            changed['scope_assessment']['policy_id'] = 'RP-other'
            issues = submission._payload_issues(changed, self.wire, context, {}, Path(directory))
            self.assertTrue(any(row['path'] == 'output/scope_assessment' for row in issues), issues)

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


if __name__ == "__main__":
    unittest.main()

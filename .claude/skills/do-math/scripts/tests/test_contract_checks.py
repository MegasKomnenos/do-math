"""Producer-side contract self-checks for research preparation.

The rules are the mechanically decidable part of what contract review returned
in the 2026-09-19 parking run: colliding symbols, missing outcome branches and
boundaries taken from a sibling contract that was still being revised.
"""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.contracts import schema_for
from do_math.submission import payload_issues
from test_engine import common
from v5_fixtures import candidate
from test_model_assessment_flow import rating


def checks(title="one", **changes):
    return {"task_title": title, "symbols": [], "sibling_boundaries": [],
            "outcome_branches": [{"outcome": "The identity holds on the given inputs", "completion": "Report the check"},
                                 {"outcome": "A given input contradicts the identity", "completion": "Report the contradicting input"}],
            **changes}


class ContractCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.context = {"action": {"id": "AC-this", "role": "research_preparation"}, "budget_unit": "concurrent_sessions",
                        "tasks": [], "knowledge_catalog": [], "kind_definitions": {}, "sources": []}
        self.item = candidate("one")
        self.conditions = []

    def issues(self, *entries, candidates=None):
        output = {**common("research_preparation"), "candidates": candidates or [self.item]}
        extensions = {"model_assessments": [rating(task_title=c['title']) for c in output['candidates']], "contract_checks": list(entries)}
        if self.conditions:
            extensions["task_conditions"] = self.conditions
        from v5_fixtures import supply_observation_rules
        supply_observation_rules(output['candidates'], extensions)
        output["integration_bundles"] = [{"integration_id": "IN-check", "members": ["output", *[
            f"activity-extensions.json/{family}/{i}" for family, rows in extensions.items() for i, _ in enumerate(rows)]],
            "impact_set": [], "authority_refs": []}]
        return json.dumps(payload_issues(output, schema_for("research_preparation"), self.context, extensions,
                                         Path(self.temp.name)), ensure_ascii=False)

    def sibling(self, **changes):
        task = {**candidate("window"), "id": "TK-window", "revision": 2, "status": "planned", **changes}
        self.context["tasks"] = [task]
        self.item["scope"]["included"] = ["Rows below the window of TK-window; the threshold is tau."]

    def test_every_candidate_needs_exactly_one_self_check(self):
        self.assertIn("one", self.issues())
        self.assertEqual(self.issues(checks()), "[]")
        self.assertNotEqual(self.issues(checks(), checks()), "[]")
        self.assertNotEqual(self.issues(checks(), checks("foreign")), "[]")

    def test_legacy_attempt_budget_contracts_remain_accepted_without_self_checks(self):
        self.context["budget_unit"] = "execution_attempts"
        self.assertEqual(self.issues(), "[]")

    def test_one_symbol_cannot_carry_two_meanings_and_must_occur_in_the_contract(self):
        self.item["question"] = "With T the threshold, expand C = T - Q + L"
        two = [{"symbol": "T", "meaning": "threshold"}, {"symbol": "T", "meaning": "first term of the identity"}]
        self.assertIn("symbol", self.issues(checks(symbols=two)))
        self.assertIn("absent", self.issues(checks(symbols=[{"symbol": "tau", "meaning": "threshold"}])))
        self.assertEqual(self.issues(checks(symbols=[{"symbol": "T", "meaning": "threshold"}, {"symbol": "Q", "meaning": "two long blocks"}])), "[]")

    def test_a_single_outcome_is_not_a_branching(self):
        self.assertNotEqual(self.issues(checks(outcome_branches=checks()["outcome_branches"][:1])), "[]")

    def test_each_declared_dependency_is_named_by_some_outcome(self):
        self.context["tasks"] = [{**candidate("exact"), "id": "TK-exact", "revision": 1, "status": "active"}]
        self.conditions = [{"task_title": "one", "dependencies": ["TK-exact"]}]
        self.assertIn("TK-exact", self.issues(checks()))
        branches = [{"outcome": "TK-exact completes with every row unimodal", "completion": "Explain the peak"},
                    {"outcome": "TK-exact completes with a counterexample row", "completion": "Explain the sign change"}]
        self.assertEqual(self.issues(checks(outcome_branches=branches)), "[]")

    def test_a_cited_sibling_contract_is_declared_at_its_current_revision(self):
        self.sibling()
        self.assertIn("TK-window", self.issues(checks()))
        entry = {"task_id": "TK-window", "revision": 1, "boundary": "k <= tau - 3", "independent_of_next_revision": True}
        self.assertIn("revision", self.issues(checks(sibling_boundaries=[entry])))
        self.assertEqual(self.issues(checks(sibling_boundaries=[{**entry, "revision": 2}])), "[]")

    def test_primary_and_extension_dependencies_have_the_same_self_check(self):
        self.context['tasks'] = [{**candidate('exact'), 'id': 'TK-exact', 'revision': 1, 'status': 'active'}]
        branches = [{'outcome': 'TK-exact holds', 'completion': 'Report proof'},
                    {'outcome': 'TK-exact fails', 'completion': 'Report gap'}]
        for primary, extension in ((True, False), (False, True), (True, True)):
            with self.subTest(primary=primary, extension=extension):
                self.item['dependencies'] = ['TK-exact'] if primary else []
                self.conditions = [{'task_title': 'one', 'dependencies': ['TK-exact']}] if extension else []
                self.assertIn('TK-exact', self.issues(checks()))
                self.assertEqual(self.issues(checks(outcome_branches=branches)), '[]')

    def test_revision_condition_is_matched_by_existing_id(self):
        self.item['revises_task_id'] = 'TK-one'
        self.context['tasks'] = [{**candidate('old'), 'id': 'TK-one', 'revision': 1, 'status': 'planned'},
                                 {**candidate('exact'), 'id': 'TK-exact', 'revision': 1, 'status': 'active'}]
        self.conditions = [{'task_id': 'TK-one', 'dependencies': ['TK-exact']}]
        self.assertIn('TK-exact', self.issues(checks()))

    def test_new_sibling_title_is_checked_before_the_engine_allocates_ids(self):
        self.conditions = [{'task_title': 'one', 'dependencies': ['second']}]
        candidates = [self.item, candidate('second')]
        self.assertIn('second', self.issues(checks(), checks('second'), candidates=candidates))
        branches = [{'outcome': 'second holds', 'completion': 'Apply result'},
                    {'outcome': 'second fails', 'completion': 'Report gap'}]
        self.assertEqual(self.issues(checks(outcome_branches=branches), checks('second'), candidates=candidates), '[]')

    def test_title_and_revision_id_cannot_supply_two_conditions_for_one_candidate(self):
        self.item['revises_task_id'] = 'TK-old'
        self.context['tasks'] = [{**candidate('old'), 'id': 'TK-old', 'revision': 1, 'status': 'planned'}]
        self.conditions = [{'task_title': 'one'}, {'task_id': 'TK-old'}]
        self.assertIn('must not repeat', self.issues(checks()))

    def test_a_boundary_may_not_silently_depend_on_a_sibling_under_revision(self):
        self.sibling(status="waiting", revision_requested={"reason": "The sibling boundary is under revision"})
        self.context["pending_revisions"] = [{"action": {"id": "AC-revise", "revision_targets": {"TK-window": {}}}, "state": "queued"}]
        entry = {"task_id": "TK-window", "revision": 2, "boundary": "k <= T - s", "independent_of_next_revision": False}
        self.assertIn("under revision", self.issues(checks(sibling_boundaries=[entry])))
        self.assertEqual(self.issues(checks(sibling_boundaries=[{**entry, "boundary": "k <= tau - 3", "independent_of_next_revision": True}])), "[]")
        self.conditions = [{"task_title": "one", "dependencies": ["TK-window"]}]
        named = [{"outcome": "TK-window fixes s", "completion": "Use s"}, {"outcome": "TK-window is withdrawn", "completion": "Report the gap"}]
        self.assertEqual(self.issues(checks(sibling_boundaries=[entry], outcome_branches=named)), "[]")

    def test_a_pending_revision_of_the_sibling_counts_as_under_revision(self):
        self.sibling()
        self.context["pending_revisions"] = [{"action": {"id": "AC-other", "revision_targets": {"TK-window": {}}}, "state": "queued"}]
        entry = {"task_id": "TK-window", "revision": 2, "boundary": "k <= T - s", "independent_of_next_revision": False}
        self.assertIn("under revision", self.issues(checks(sibling_boundaries=[entry])))

    def test_a_cited_record_must_exist(self):
        self.item["scope"]["included"] = ["Apply KN-missing to the given inputs."]
        self.assertIn("KN-missing", self.issues(checks()))


if __name__ == "__main__":
    unittest.main()

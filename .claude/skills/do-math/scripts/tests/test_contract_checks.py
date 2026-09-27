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
from research_fixtures import candidate
from record_fixtures import contract_check, preparation_context, preparation_issues


class ContractCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.context = preparation_context()
        self.item = candidate("one")
        self.conditions = []

    def issues(self, *entries, candidates=None):
        return preparation_issues(entries, candidates=candidates or [self.item], context=self.context,
                                  workspace=Path(self.temp.name), conditions=self.conditions)

    def sibling(self, **changes):
        task = {**candidate("window"), "id": "TK-window", "revision": 2, "status": "planned", **changes}
        self.context["tasks"] = [task]
        self.item["scope"]["included"] = ["Rows below the window of TK-window; the threshold is tau."]

    def test_every_candidate_needs_exactly_one_self_check(self):
        self.assertIn("one", self.issues())
        self.assertEqual(self.issues(contract_check()), "[]")
        self.assertNotEqual(self.issues(contract_check(), contract_check()), "[]")
        self.assertNotEqual(self.issues(contract_check(), contract_check("foreign")), "[]")


    def test_one_symbol_cannot_carry_two_meanings_and_must_occur_in_the_contract(self):
        self.item["question"] = "With T the threshold, expand C = T - Q + L"
        two = [{"symbol": "T", "meaning": "threshold"}, {"symbol": "T", "meaning": "first term of the identity"}]
        self.assertIn("symbol", self.issues(contract_check(symbols=two)))
        self.assertIn("absent", self.issues(contract_check(symbols=[{"symbol": "tau", "meaning": "threshold"}])))
        self.assertEqual(self.issues(contract_check(symbols=[{"symbol": "T", "meaning": "threshold"}, {"symbol": "Q", "meaning": "two long blocks"}])), "[]")

    def test_a_single_outcome_is_not_a_branching(self):
        self.assertNotEqual(self.issues(contract_check(outcome_branches=contract_check()["outcome_branches"][:1])), "[]")

    def test_each_declared_dependency_is_named_by_some_outcome(self):
        self.context["tasks"] = [{**candidate("exact"), "id": "TK-exact", "revision": 1, "status": "active"}]
        self.conditions = [{"task_title": "one", "dependencies": ["TK-exact"]}]
        self.assertIn("TK-exact", self.issues(contract_check()))
        branches = [{"outcome": "TK-exact completes with every row unimodal", "completion": "Explain the peak"},
                    {"outcome": "TK-exact completes with a counterexample row", "completion": "Explain the sign change"}]
        self.assertEqual(self.issues(contract_check(outcome_branches=branches)), "[]")

    def test_a_cited_sibling_contract_is_declared_at_its_current_revision(self):
        self.sibling()
        self.assertIn("TK-window", self.issues(contract_check()))
        entry = {"task_id": "TK-window", "revision": 1, "boundary": "k <= tau - 3", "independent_of_next_revision": True}
        self.assertIn("revision", self.issues(contract_check(sibling_boundaries=[entry])))
        self.assertEqual(self.issues(contract_check(sibling_boundaries=[{**entry, "revision": 2}])), "[]")

    def test_sibling_boundary_reads_the_exact_catalog_contract(self):
        import hashlib
        self.sibling(status='completed')
        task = self.context['tasks'].pop()
        raw = json.dumps(task).encode('utf-8')
        root = Path(self.temp.name)
        path = root / 'input' / 'details' / 'sibling.json'
        path.parent.mkdir(parents=True)
        path.write_bytes(raw)
        self.context['snapshot'] = 'fixed-input'
        self.context['task_catalog'] = [{'id': task['id'], 'title': task['title'],
            'revision': task['revision'], 'status': task['status'], 'source_ref': {
                'path': path.relative_to(root).as_posix(), 'snapshot': 'fixed-input',
                'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}}]
        entry = {'task_id': task['id'], 'revision': task['revision'],
                 'boundary': 'k <= tau - 3', 'independent_of_next_revision': True}
        self.assertEqual(self.issues(contract_check(sibling_boundaries=[entry])), '[]')
        self.assertIn('revision', self.issues(contract_check(sibling_boundaries=[{**entry, 'revision': 1}])))
        path.write_bytes(raw + b' ')
        self.assertIn('sibling contract source', self.issues(contract_check(sibling_boundaries=[entry])))

    def test_primary_and_extension_dependencies_have_the_same_self_check(self):
        self.context['tasks'] = [{**candidate('exact'), 'id': 'TK-exact', 'revision': 1, 'status': 'active'}]
        branches = [{'outcome': 'TK-exact holds', 'completion': 'Report proof'},
                    {'outcome': 'TK-exact fails', 'completion': 'Report gap'}]
        for primary, extension in ((True, False), (False, True), (True, True)):
            with self.subTest(primary=primary, extension=extension):
                self.item['dependencies'] = ['TK-exact'] if primary else []
                self.conditions = [{'task_title': 'one', 'dependencies': ['TK-exact']}] if extension else []
                self.assertIn('TK-exact', self.issues(contract_check()))
                self.assertEqual(self.issues(contract_check(outcome_branches=branches)), '[]')

    def test_revision_condition_is_matched_by_existing_id(self):
        self.item['revises_task_id'] = 'TK-one'
        self.context['tasks'] = [{**candidate('old'), 'id': 'TK-one', 'revision': 1, 'status': 'planned'},
                                 {**candidate('exact'), 'id': 'TK-exact', 'revision': 1, 'status': 'active'}]
        self.conditions = [{'task_id': 'TK-one', 'dependencies': ['TK-exact']}]
        self.assertIn('TK-exact', self.issues(contract_check()))

    def test_new_sibling_title_is_checked_before_the_engine_allocates_ids(self):
        self.conditions = [{'task_title': 'one', 'dependencies': ['second']}]
        candidates = [self.item, candidate('second')]
        self.assertIn('second', self.issues(contract_check(), contract_check('second'), candidates=candidates))
        branches = [{'outcome': 'second holds', 'completion': 'Apply result'},
                    {'outcome': 'second fails', 'completion': 'Report gap'}]
        self.assertEqual(self.issues(contract_check(outcome_branches=branches), contract_check('second'), candidates=candidates), '[]')

    def test_title_and_revision_id_cannot_supply_two_conditions_for_one_candidate(self):
        self.item['revises_task_id'] = 'TK-old'
        self.context['tasks'] = [{**candidate('old'), 'id': 'TK-old', 'revision': 1, 'status': 'planned'}]
        self.conditions = [{'task_title': 'one'}, {'task_id': 'TK-old'}]
        self.assertIn('must not repeat', self.issues(contract_check()))

    def test_a_boundary_may_not_silently_depend_on_a_sibling_under_revision(self):
        self.sibling(status="waiting", revision_requested={"revision": 2, "source": "AC-revise", "reason": "The sibling boundary is under revision"})
        self.context["pending_revisions"] = [{"action": {"id": "AC-revise", "revision_targets": {"TK-window": {}}}, "state": "queued"}]
        entry = {"task_id": "TK-window", "revision": 2, "boundary": "k <= T - s", "independent_of_next_revision": False}
        self.assertIn("under revision", self.issues(contract_check(sibling_boundaries=[entry])))
        self.assertEqual(self.issues(contract_check(sibling_boundaries=[{**entry, "boundary": "k <= tau - 3", "independent_of_next_revision": True}])), "[]")
        self.conditions = [{"task_title": "one", "dependencies": ["TK-window"]}]
        named = [{"outcome": "TK-window fixes s", "completion": "Use s"}, {"outcome": "TK-window is withdrawn", "completion": "Report the gap"}]
        self.assertEqual(self.issues(contract_check(sibling_boundaries=[entry], outcome_branches=named)), "[]")

    def test_a_pending_revision_of_the_sibling_counts_as_under_revision(self):
        self.sibling()
        self.context["pending_revisions"] = [{"action": {"id": "AC-other", "revision_targets": {"TK-window": {}}}, "state": "queued"}]
        entry = {"task_id": "TK-window", "revision": 2, "boundary": "k <= T - s", "independent_of_next_revision": False}
        self.assertIn("under revision", self.issues(contract_check(sibling_boundaries=[entry])))

    def test_a_revision_request_on_the_sibling_counts_as_under_revision(self):
        self.sibling(revision_requested={"revision": 2, "source": "AC-review", "reason": "The sibling boundary is under revision"})
        entry = {"task_id": "TK-window", "revision": 2, "boundary": "k <= T - s", "independent_of_next_revision": False}
        self.assertIn("under revision", self.issues(contract_check(sibling_boundaries=[entry])))

    def test_a_cited_record_must_exist(self):
        self.item["scope"]["included"] = ["Apply KN-missing to the given inputs."]
        self.assertIn("KN-missing", self.issues(contract_check()))


if __name__ == "__main__":
    unittest.main()

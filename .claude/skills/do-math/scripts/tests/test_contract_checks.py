"""Producer-side contract self-checks for research preparation.

The rules are the part of contract review that the input state decides: a
cited task or knowledge record must exist, and a boundary taken from a cited
sibling contract must be read at its current revision and must not silently
depend on a sibling that is still being revised (the 2026-09-19 parking run).
Symbol collisions and missing outcome branches are the author's judgment and
the independent contract review's, not declarations checked here.
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

    def test_self_check_declares_only_sibling_boundaries(self):
        # A symbol used with two meanings and a dependency named by no outcome are
        # judged by the author and the contract review; no declaration is compared.
        self.item["question"] = "With T the threshold, expand C = T - Q + L where T is the first term"
        self.context["tasks"] = [{**candidate("exact"), "id": "TK-exact", "revision": 1, "status": "active"}]
        self.conditions = [{"task_title": "one", "dependencies": ["TK-exact"]}]
        self.assertEqual(self.issues(contract_check()), "[]")
        removed = {"symbols": [{"symbol": "T", "meaning": "threshold"}],
                   "outcome_branches": [{"outcome": "TK-exact holds", "completion": "Report proof"},
                                        {"outcome": "TK-exact fails", "completion": "Report gap"}]}
        for field, value in removed.items():
            with self.subTest(field=field):
                self.assertIn(field, self.issues(contract_check(**{field: value})))

    def test_a_cited_sibling_contract_is_declared_at_its_current_revision(self):
        self.sibling()
        self.assertIn("TK-window", self.issues(contract_check()))
        entry = {"task_id": "TK-window", "revision": 1, "boundary": "k <= tau - 3", "independent_of_next_revision": True}
        self.assertIn("revision", self.issues(contract_check(sibling_boundaries=[entry])))
        self.assertEqual(self.issues(contract_check(sibling_boundaries=[{**entry, "revision": 2}])), "[]")

    def test_sibling_boundary_is_read_from_the_checker_task_not_its_detail_copy(self):
        # The checker context holds every current task, a completed sibling outside the comparison
        # population included (context_store.prepare_role_input); the prompt's detail copy is not read.
        import hashlib
        self.sibling(status='completed')
        task = self.context['tasks'][0]
        raw = json.dumps(task).encode('utf-8')
        root = Path(self.temp.name)
        path = root / 'input' / 'details' / 'sibling.json'
        path.parent.mkdir(parents=True)
        path.write_bytes(raw + b' ')  # An accidentally changed detail copy.
        self.context['snapshot'] = 'fixed-input'
        self.context['task_catalog'] = [{'id': task['id'], 'title': task['title'],
            'revision': task['revision'], 'status': task['status'], 'source_ref': {
                'path': path.relative_to(root).as_posix(), 'snapshot': 'fixed-input',
                'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}}]
        entry = {'task_id': task['id'], 'revision': task['revision'],
                 'boundary': 'k <= tau - 3', 'independent_of_next_revision': True}
        self.assertEqual(self.issues(contract_check(sibling_boundaries=[entry])), '[]')
        self.assertIn('revision', self.issues(contract_check(sibling_boundaries=[{**entry, 'revision': 1}])))

    def test_primary_and_extension_dependencies_both_wait_for_a_sibling_under_revision(self):
        self.sibling(revision_requested={"revision": 2, "source": "AC-review", "reason": "The sibling boundary is under revision"})
        entry = {"task_id": "TK-window", "revision": 2, "boundary": "k <= T - s", "independent_of_next_revision": False}
        for primary, extension in ((False, False), (True, False), (False, True), (True, True)):
            with self.subTest(primary=primary, extension=extension):
                self.item['dependencies'] = ['TK-window'] if primary else []
                self.conditions = [{'task_title': 'one', 'dependencies': ['TK-window']}] if extension else []
                issues = self.issues(contract_check(sibling_boundaries=[entry]))
                if primary or extension:
                    self.assertEqual(issues, '[]')
                else:
                    self.assertIn('under revision', issues)

    def test_revision_condition_is_matched_by_existing_id(self):
        self.sibling(revision_requested={"revision": 2, "source": "AC-review", "reason": "The sibling boundary is under revision"})
        self.item['revises_task_id'] = 'TK-one'
        self.context['tasks'].append({**candidate('old'), 'id': 'TK-one', 'revision': 1, 'status': 'planned'})
        entry = {"task_id": "TK-window", "revision": 2, "boundary": "k <= T - s", "independent_of_next_revision": False}
        self.assertIn('under revision', self.issues(contract_check(sibling_boundaries=[entry])))
        # The revision fixture carries unrelated issues; only the matched condition's dependency is asserted.
        self.conditions = [{'task_id': 'TK-one', 'dependencies': ['TK-window']}]
        self.assertNotIn('under revision', self.issues(contract_check(sibling_boundaries=[entry])))

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
        self.assertEqual(self.issues(contract_check(sibling_boundaries=[entry])), "[]")

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

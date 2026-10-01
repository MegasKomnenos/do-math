"""Producer-side contract self-checks for research preparation (``submission.payload_issues``, layer 2).

The rules are the part of contract review that the input state decides: a
cited task or knowledge record must exist, and a boundary taken from a cited
sibling contract must be read at its current revision and must not silently
depend on a sibling that is still being revised (the 2026-09-19 parking run).
Symbol collisions and missing outcome branches are the author's judgment and
the independent contract review's, not declarations checked here.

Each test builds one preparation output (``record_fixtures.preparation_issues``)
and reads the receiver's issues; a rejection is pinned by its rule ID and the
product's message, not only by the presence of some issue.
"""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from support.record_builders import contract_check, preparation_context, preparation_issues
from support.role_answers import candidate

UNDER_REVISION = ("sibling contract is under revision: state a boundary that its next revision cannot move, "
                  "or wait for it through task_conditions dependencies: TK-window")


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

    def rules(self, text):
        """``[(rule_id, message)]`` of the issues ``text`` lists."""
        return [(row["rule_id"], row["message"]) for row in json.loads(text)]

    def sibling(self, **changes):
        task = {**candidate("window"), "id": "TK-window", "revision": 2, "status": "planned", **changes}
        self.context["tasks"] = [task]
        self.item["scope"]["included"] = ["Rows below the window of TK-window; the threshold is tau."]

    def test_every_candidate_needs_exactly_one_self_check(self):
        missing = self.issues()
        self.assertIn("one", missing)
        self.assertEqual(self.rules(missing), [("contract_check.coverage",
            'contract self-check coverage: every candidate needs exactly one entry; missing ["one"]')])
        self.assertEqual(self.issues(contract_check()), "[]")
        # A repeated entry and an entry for a candidate that does not exist fail the same coverage rule.
        for entries in ((contract_check(), contract_check()), (contract_check(), contract_check("foreign"))):
            with self.subTest(entries=[entry["task_title"] for entry in entries]):
                issues = self.issues(*entries)
                self.assertNotEqual(issues, "[]")
                self.assertEqual(self.rules(issues), [("contract_check.coverage",
                    "contract self-check coverage: every candidate needs exactly one entry; missing []")])

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
                issues = self.issues(contract_check(**{field: value}))
                self.assertIn(field, issues)
                # The closed extension schema refuses the undeclared field.
                self.assertEqual(self.rules(issues), [("schema.additionalProperties",
                    "Additional properties are not allowed ('" + field + "' was unexpected)")])

    def test_a_cited_sibling_contract_is_declared_at_its_current_revision(self):
        self.sibling()
        undeclared = self.issues(contract_check())
        self.assertIn("TK-window", undeclared)
        self.assertEqual(self.rules(undeclared), [("contract_check.sibling_boundary",
                                                   "cited sibling contract has no declared boundary: TK-window")])
        entry = {"task_id": "TK-window", "revision": 1, "boundary": "k <= tau - 3", "independent_of_next_revision": True}
        stale = self.issues(contract_check(sibling_boundaries=[entry]))
        self.assertIn("revision", stale)
        self.assertEqual(self.rules(stale), [("contract_check.sibling_revision",
            "sibling boundary was not read from the current revision 2 of TK-window")])
        self.assertEqual(self.issues(contract_check(sibling_boundaries=[{**entry, "revision": 2}])), "[]")

    def test_sibling_boundary_is_read_from_the_checker_task_not_its_detail_copy(self):
        # The checker context holds every current task, a completed sibling outside the comparison
        # population included (context_store.prepare_role_input); the prompt's detail copy is not read.
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
        stale = self.issues(contract_check(sibling_boundaries=[{**entry, 'revision': 1}]))
        self.assertIn('revision', stale)
        self.assertEqual(self.rules(stale), [("contract_check.sibling_revision",
            "sibling boundary was not read from the current revision 2 of TK-window")])

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
                    self.assertEqual(self.rules(issues), [("contract_check.sibling_under_revision", UNDER_REVISION)])

    def test_revision_condition_is_matched_by_existing_id(self):
        self.sibling(revision_requested={"revision": 2, "source": "AC-review", "reason": "The sibling boundary is under revision"})
        self.item['revises_task_id'] = 'TK-one'
        self.context['tasks'].append({**candidate('old'), 'id': 'TK-one', 'revision': 1, 'status': 'planned'})
        entry = {"task_id": "TK-window", "revision": 2, "boundary": "k <= T - s", "independent_of_next_revision": False}
        unmatched = self.issues(contract_check(sibling_boundaries=[entry]))
        self.assertIn('under revision', unmatched)
        self.assertIn(("contract_check.sibling_under_revision", UNDER_REVISION), self.rules(unmatched))
        # The revision fixture carries unrelated issues; only the matched condition's dependency is asserted.
        self.conditions = [{'task_id': 'TK-one', 'dependencies': ['TK-window']}]
        matched = self.issues(contract_check(sibling_boundaries=[entry]))
        self.assertNotIn('under revision', matched)
        self.assertNotIn("contract_check.sibling_under_revision", [rule for rule, _ in self.rules(matched)])

    def test_title_and_revision_id_cannot_supply_two_conditions_for_one_candidate(self):
        self.item['revises_task_id'] = 'TK-old'
        self.context['tasks'] = [{**candidate('old'), 'id': 'TK-old', 'revision': 1, 'status': 'planned'}]
        self.conditions = [{'task_title': 'one'}, {'task_id': 'TK-old'}]
        issues = self.issues(contract_check())
        self.assertIn('must not repeat', issues)
        self.assertIn("task conditions must not repeat a target", [message for _, message in self.rules(issues)])

    def test_a_boundary_may_not_silently_depend_on_a_sibling_under_revision(self):
        self.sibling(status="waiting", revision_requested={"revision": 2, "source": "AC-revise", "reason": "The sibling boundary is under revision"})
        self.context["pending_revisions"] = [{"action": {"id": "AC-revise", "revision_targets": {"TK-window": {}}}, "state": "queued"}]
        entry = {"task_id": "TK-window", "revision": 2, "boundary": "k <= T - s", "independent_of_next_revision": False}
        silent = self.issues(contract_check(sibling_boundaries=[entry]))
        self.assertIn("under revision", silent)
        self.assertEqual(self.rules(silent), [("contract_check.sibling_under_revision", UNDER_REVISION)])
        self.assertEqual(self.issues(contract_check(sibling_boundaries=[{**entry, "boundary": "k <= tau - 3", "independent_of_next_revision": True}])), "[]")
        self.conditions = [{"task_title": "one", "dependencies": ["TK-window"]}]
        self.assertEqual(self.issues(contract_check(sibling_boundaries=[entry])), "[]")

    def test_a_pending_revision_of_the_sibling_counts_as_under_revision(self):
        self.sibling()
        self.context["pending_revisions"] = [{"action": {"id": "AC-other", "revision_targets": {"TK-window": {}}}, "state": "queued"}]
        entry = {"task_id": "TK-window", "revision": 2, "boundary": "k <= T - s", "independent_of_next_revision": False}
        issues = self.issues(contract_check(sibling_boundaries=[entry]))
        self.assertIn("under revision", issues)
        self.assertEqual(self.rules(issues), [("contract_check.sibling_under_revision", UNDER_REVISION)])

    def test_a_revision_request_on_the_sibling_counts_as_under_revision(self):
        self.sibling(revision_requested={"revision": 2, "source": "AC-review", "reason": "The sibling boundary is under revision"})
        entry = {"task_id": "TK-window", "revision": 2, "boundary": "k <= T - s", "independent_of_next_revision": False}
        issues = self.issues(contract_check(sibling_boundaries=[entry]))
        self.assertIn("under revision", issues)
        self.assertEqual(self.rules(issues), [("contract_check.sibling_under_revision", UNDER_REVISION)])

    def test_a_cited_record_must_exist(self):
        self.item["scope"]["included"] = ["Apply KN-missing to the given inputs."]
        issues = self.issues(contract_check())
        self.assertIn("KN-missing", issues)
        self.assertEqual(self.rules(issues), [("contract_check.cited_record",
            "cited record is neither in the supplied input nor in its record_index: KN-missing")])


if __name__ == "__main__":
    unittest.main()

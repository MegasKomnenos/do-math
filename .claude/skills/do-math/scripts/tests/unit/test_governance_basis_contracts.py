"""생산한 근거의 누락·복사·원천 선택 규칙을 값으로 확인한다."""
from copy import deepcopy
import unittest

from do_math import input_basis


class GovernanceBasisContractTests(unittest.TestCase):
    def test_missing_review_basis_requires_refresh(self):
        for value in (None, [], {}, {'values': []}):
            with self.subTest(value=value):
                self.assertEqual(input_basis.review_input_basis_changes(value, {}), [
                    {'field': 'review_input_basis', 'reason': 'missing_basis', 'next': 'refresh_review'}])

    def test_missing_decision_basis_has_exact_diagnostic(self):
        for value in (None, [], {}, {'records': {}}):
            with self.subTest(value=value):
                self.assertEqual(input_basis.decision_basis_changes(value, {}, {}), [
                    {'id': None, 'field': 'decision_basis', 'reason': 'missing_basis'}])

    def test_review_capture_is_detached_and_reports_selected_profile(self):
        cycle = {'scope_assessment': {'selected_profile_ref': {'id': 'EP-one'}}, 'review_policy': {'count': 2}}
        basis = input_basis.capture_review_input_basis(cycle)
        self.assertEqual(input_basis.review_input_basis_changes(basis, cycle), [])
        cycle['scope_assessment']['selected_profile_ref'] = {'id': 'EP-two'}
        self.assertEqual(input_basis.review_input_basis_changes(basis, cycle), [
            {'field': 'selected_profile_ref', 'before': {'id': 'EP-one'}, 'after': {'id': 'EP-two'},
             'next': 'refresh_review'}])
        self.assertEqual(basis['values']['scope_assessment'], {'selected_profile_ref': {'id': 'EP-one'}})

    def test_source_aliases_select_exact_sources_and_hash_changes(self):
        source = {'id': 'SO-one', 'path': 'sources/a.txt', 'local_path': 'work/a.txt', 'name': 'a.txt', 'sha256': 'a' * 64}
        instance = {'sources': [source]}
        before = deepcopy(instance)
        expected = [{'name': 'a.txt', 'path': 'sources/a.txt', 'sha256': 'a' * 64}]
        self.assertEqual(input_basis.aliases(source), {'SO-one', 'sources/a.txt', 'work/a.txt', 'a.txt', 'source:a.txt'})
        for ref in sorted(input_basis.aliases(source)):
            with self.subTest(ref=ref):
                self.assertEqual(input_basis.capture_sources(instance, [ref]), expected)
        self.assertEqual(input_basis.capture_sources(instance, []), [])
        self.assertEqual(input_basis.capture_sources(instance), expected)
        self.assertTrue(input_basis.sources_current(expected, instance))
        self.assertEqual(instance, before)
        source['sha256'] = 'b' * 64
        self.assertFalse(input_basis.sources_current(expected, instance))

    def test_currentness_exception_preserves_structured_changes(self):
        changes = [{'field': 'decision_basis', 'reason': 'missing_basis'}]
        error = input_basis.CurrentnessChanged(changes)
        self.assertEqual(error.changes, changes)
        self.assertEqual(str(error), 'decision premises changed: [{"field": "decision_basis", "reason": "missing_basis"}]')

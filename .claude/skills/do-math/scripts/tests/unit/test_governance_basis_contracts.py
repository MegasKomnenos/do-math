"""생산한 근거의 누락·복사·원천 선택 규칙을 값으로 확인한다."""
from copy import deepcopy
import unittest

from do_math import input_basis


class GovernanceBasisContractTests(unittest.TestCase):
    def test_review_basis_missing_a_declared_null_premise_requires_refresh(self):
        from do_math.review_cycle import start_review
        cycle = start_review({'revision': 1}, reviewers=1)
        basis = input_basis.capture_review_input_basis(cycle)
        self.assertIsNone(basis['values']['identity_basis'])
        basis['values'].pop('identity_basis')
        self.assertEqual(input_basis.review_input_basis_changes(basis, cycle), [{
            'field': 'identity_basis', 'reason': 'missing_basis_field', 'next': 'refresh_review'}])

    def test_every_declared_review_premise_changes_and_progress_fields_do_not(self):
        from do_math.review_cycle import start_review
        from do_math.input_basis import REVIEW_INPUT_BASIS_FIELDS
        cycle = start_review({'revision': 1}, reviewers=2)
        basis = input_basis.capture_review_input_basis(cycle)
        self.assertEqual(set(basis['values']), set(REVIEW_INPUT_BASIS_FIELDS))
        for field in REVIEW_INPUT_BASIS_FIELDS:
            incomplete = deepcopy(basis)
            incomplete['values'].pop(field)
            with self.subTest(missing_premise=field):
                self.assertEqual(input_basis.review_input_basis_changes(incomplete, cycle), [{
                    'field': field, 'reason': 'missing_basis_field', 'next': 'refresh_review'}])
            changed = deepcopy(cycle)
            value = changed.get(field)
            changed[field] = {**value, 'changed_premise': True} if isinstance(value, dict) else value + 1 if type(value) is int else 'changed-' + field
            with self.subTest(premise=field):
                changes = input_basis.review_input_basis_changes(basis, changed)
                self.assertEqual([row['field'] for row in changes], [field])
                self.assertEqual(changes[0]['next'], 'refresh_review')
                self.assertEqual(input_basis.capture_review_input_basis(cycle), basis)
        for field, value in (('history', [{'kind': 'administrative'}]), ('phase', 'initial'),
                             ('round', 2), ('results', {'progress': {}}), ('receipt', {'state': 'accepted'})):
            with self.subTest(bookkeeping=field):
                self.assertEqual(input_basis.review_input_basis_changes(basis, {**cycle, field: value}), [])

    def test_review_basis_detects_boolean_integer_type_drift_in_a_declared_limit(self):
        from do_math.review_cycle import start_review
        cycle = start_review({'revision': 1}, reviewers=1)
        cycle['activity_execution_limit'] = 1
        basis = input_basis.capture_review_input_basis(cycle)
        basis['values']['activity_execution_limit'] = True
        self.assertEqual(input_basis.review_input_basis_changes(basis, cycle), [{
            'field': 'activity_execution_limit', 'before': True, 'after': 1, 'next': 'refresh_review'}])

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

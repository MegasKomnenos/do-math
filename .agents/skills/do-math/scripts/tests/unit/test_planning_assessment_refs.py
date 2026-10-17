"""Issued source locators bind an assessment to source identity across revisions."""
from copy import deepcopy
import unittest

from do_math.canonical import exact_content_hash
from do_math.task_scope import assessment_basis


class AssessmentSourceTests(unittest.TestCase):
    def test_issued_locator_keeps_its_source_when_order_and_local_names_change(self):
        source = {'id': 'SO-one', 'name': 'notes.txt', 'path': 'runtime/artifacts/BA-one/source.bin',
                  'sha256': 'a' * 64, 'revision': 1}
        other = {**source, 'id': 'SO-other', 'name': 'other.txt', 'sha256': 'b' * 64}
        locator = 'input/sources/0000-notes.txt'
        supplied = [{**source, 'local_path': locator}]
        instance = {'sources': [source, other]}
        task = {'id': 'TK-one'}
        assessment = {'unresolved': [{'missing_inputs': [locator]}]}
        before = deepcopy([instance, supplied, assessment])
        basis = assessment_basis(task, assessment, instance, {}, input_sources=supplied)
        self.assertEqual(basis, {locator: {'source_id': source['id'], 'sha256': exact_content_hash(source)}})
        self.assertEqual([instance, supplied, assessment], before)
        assessment['basis'] = basis
        # Another current row even advertises the identical locator. It cannot
        # replace the identity taken from the original execution's fixed input.
        instance['sources'] = [{**other, 'local_path': locator, 'revision': 2}, source]
        self.assertEqual(assessment_basis(task, assessment, instance, {}), basis)
        revised = {**source, 'sha256': 'c' * 64, 'revision': 2, 'path': 'runtime/artifacts/BA-next/source.bin'}
        instance['sources'][1] = revised
        self.assertEqual(assessment_basis(task, assessment, instance, {}),
                         {locator: {'source_id': source['id'], 'sha256': exact_content_hash(revised)}})
        self.assertEqual(assessment_basis(task, assessment, instance, {}, input_sources=supplied), basis,
                         'Application binds the issued edition, not a source that changed while the model ran')
        # Even the same basename under a new source ID is not this dependency.
        instance['sources'] = [{**source, 'id': 'SO-replacement'}]
        self.assertEqual(assessment_basis(task, assessment, instance, {}),
                         {locator: {'source_id': source['id'], 'sha256': None}})

    def test_unissued_locator_is_not_guessed_from_a_basename_or_position(self):
        source = {'id': 'SO-one', 'name': 'notes.txt', 'path': 'runtime/artifacts/BA-one/source.bin',
                  'sha256': 'a' * 64}
        locator = 'input/sources/0000-notes.txt'
        assessment = {'unresolved': [{'missing_inputs': [locator, 'future.txt', 'source:future.txt']}]}
        instance = {'sources': [source]}
        task = {'id': 'TK-one'}
        expected = {locator: None, 'future.txt': None, 'source:future.txt': None}
        self.assertEqual(assessment_basis(task, assessment, instance, {},
                         input_sources=[{**source, 'local_path': 'input/sources/0001-notes.txt'}]), expected)
        assessment['basis'] = expected
        instance['sources'].append({**source, 'id': 'SO-future', 'name': 'future.txt'})
        actual = assessment_basis(task, assessment, instance, {})
        self.assertIsNone(actual[locator])
        self.assertEqual(actual['future.txt'], exact_content_hash(instance['sources'][1]))
        self.assertEqual(actual['source:future.txt'], actual['future.txt'])

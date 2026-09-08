"""Exercise the completion boundary and independent component review currentness."""
import copy
import unittest

from work_queue import VERSION, component_basis, pending_work


class WorkQueueTests(unittest.TestCase):
    def setUp(self):
        self.record = {'paper_id': 'p', 'version_sha256': 'v',
                       'identity': {'status': 'confirmed', 'reason': 'Header verified.'},
                       'abstract': {'status': 'found', 'artifacts': [{'path': 'a.txt'}]},
                       'fulltext': {'status': 'found', 'artifacts': [{'path': 'p.pdf'}]},
                       'evidence': [{'path': 'header.txt'}]}
        self.record['work_state'] = {'version': VERSION, 'tasks': [], 'reviews': {
            c: {'basis_sha256': component_basis(self.record, c), 'reason': 'Actual content verified.',
                'evidence_paths': ['header.txt']} for c in ('identity', 'abstract', 'fulltext')}}

    def test_reviewed_acquired_components_need_no_further_search(self):
        self.assertEqual(pending_work(self.record), [])

    def test_fulltext_change_does_not_invalidate_abstract_review(self):
        self.record['fulltext']['artifacts'][0]['path'] = 'new.pdf'
        keys = {x['key'] for x in pending_work(self.record)}
        self.assertIn('review:fulltext', keys)
        self.assertNotIn('review:abstract', keys)

    def test_identity_change_reopens_both_content_reviews(self):
        self.record['identity']['reason'] = 'Different edition evidence.'
        keys = {x['key'] for x in pending_work(self.record)}
        self.assertTrue({'review:identity', 'review:abstract', 'review:fulltext'} <= keys)

    def test_progress_timestamp_does_not_invalidate_review(self):
        self.record['updated_at'] = 'later'
        self.assertEqual(pending_work(self.record), [])

    def test_open_pdf_candidate_remains_even_with_found_status(self):
        self.record['work_state']['tasks'] = [{'key': 'pdf:2', 'kind': 'pdf', 'target': 'actual second PDF link',
                                             'status': 'needs_review', 'reason': 'Wrong first candidate.'}]
        self.assertIn('pdf:2', {x['key'] for x in pending_work(self.record)})

    def test_discovered_is_not_attempted(self):
        self.record['work_state']['tasks'] = [{'key': 'pdfs', 'kind': 'pdf', 'target': 'observed PDF links',
            'status': 'done', 'reason': 'Visited three of five.', 'evidence_paths': ['header.txt'],
            'discovered': 5, 'attempted': 3, 'remaining': 2}]
        self.assertIn('pdfs:remaining', {x['key'] for x in pending_work(self.record)})

    def test_bad_counter_cannot_hide_candidates(self):
        self.record['work_state']['tasks'] = [{'key': 'pages', 'kind': 'search', 'target': 'query',
            'status': 'done', 'reason': 'Counter mismatch.', 'evidence_paths': ['header.txt'],
            'discovered': 5, 'attempted': 3, 'remaining': 0}]
        self.assertIn('pages:counts', {x['key'] for x in pending_work(self.record)})

    def test_unresolved_component_is_not_hidden_by_empty_tasks(self):
        self.record['abstract'] = {'status': 'unresolved', 'reason': 'Review required.'}
        self.assertIn('abstract', {x['key'] for x in pending_work(self.record)})

    def test_negative_labels_need_scoped_search_and_source_evidence(self):
        self.record['fulltext'] = {'status': 'not_found', 'reason': 'No fulltext in source scope.'}
        self.record['work_state']['reviews']['fulltext']['basis_sha256'] = component_basis(self.record, 'fulltext')
        keys = {x['key'] for x in pending_work(self.record)}
        self.assertTrue({'scope:fulltext', 'negative_scope_inventory'} <= keys)

    def test_stage_marker_never_skips_unresolved_record(self):
        self.record['abstract'] = {'status': 'unresolved'}
        self.record['collection_stage'] = 'summon-ui-response-v1'
        self.assertTrue(pending_work(self.record))

    def test_review_reference_must_exist_in_result(self):
        self.record['work_state']['reviews']['abstract']['evidence_paths'] = ['absent.txt']
        self.assertIn('review:abstract', {x['key'] for x in pending_work(self.record)})

    def test_untouched_candidate_has_collection_work(self):
        self.assertEqual(pending_work(None)[0]['key'], 'collect')


if __name__ == '__main__':
    unittest.main()

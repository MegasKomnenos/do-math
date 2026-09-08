"""Regression tests for completion that previously ignored unfinished work."""
import unittest

import check_recovery as checker
import test_check_recovery as fixtures


class ResumeCompletionTests(unittest.TestCase):
    setUp = fixtures.ContractTests.setUp
    assignment = fixtures.ContractTests.assignment
    def test_terminal_labels_with_unvisited_link_are_incomplete(self):
        self.result['unvisited_link'] = True
        report = checker.check_assignment(self.assignment(), partial=True)
        self.assertFalse(report['complete'])

    def test_terminal_labels_with_unvisited_pages_are_incomplete(self):
        self.result['unvisited_search_pages'] = [{'query': 'Exact title', 'record_count': 30, 'received': 20}]
        report = checker.check_assignment(self.assignment(), partial=True)
        self.assertFalse(report['complete'])

    def test_legacy_terminal_result_requires_saved_evidence_assessment(self):
        report = checker.check_assignment(self.assignment(), partial=True)
        self.assertFalse(report['complete'])

    def test_full_check_rejects_collection_error_even_with_terminal_labels(self):
        self.result['collection_error'] = 'Browser collection exception: TimeoutError'
        report = checker.check_assignment(self.assignment())
        self.assertFalse(report['passed'])


if __name__ == '__main__':
    unittest.main()

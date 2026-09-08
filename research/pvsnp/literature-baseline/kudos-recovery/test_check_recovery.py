import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import check_recovery as c


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'proof.txt').write_text('Search results for the assigned title: no matching item.', encoding='utf-8')
        self.proof = {'path': 'proof.txt', 'sha256': hashlib.sha256((self.root / 'proof.txt').read_bytes()).hexdigest(),
                      'url': 'https://example.org/search', 'kind': 'search-results'}
        self.paper = {'paper_id': 'VER-1', 'version_sha256': 'v1'}
        self.result = {'schema_version': 'kudos-recovery-result/1', 'paper_id': 'VER-1', 'version_sha256': 'v1',
                       'identity': {'status': 'not_found', 'reason': 'No matching record after title and author searches.'},
                       'abstract': {'status': 'not_found', 'reason': 'No matching record.'},
                       'fulltext': {'status': 'not_found', 'reason': 'No matching record.'},
                       'attempts': [{'method': 'playwright', 'query': 'Exact title', 'url': 'https://example.org/search',
                                     'outcome': 'No matching record.'}], 'evidence': [self.proof]}

    def validate(self, result=None):
        return c.validate_record(result or self.result, self.paper, self.root)

    def test_valid_documented_not_found(self):
        self.assertEqual(self.validate(), [])

    def test_missing_attempt_is_not_search_completion(self):
        self.result['attempts'] = []
        self.assertTrue(self.validate())

    def test_wrong_paper_or_version_is_rejected(self):
        for field in ['paper_id', 'version_sha256']:
            result = copy.deepcopy(self.result);result[field] = 'wrong'
            self.assertTrue(self.validate(result))

    def test_unknown_state_is_rejected(self):
        self.result['abstract']['status'] = 'probably'
        self.assertTrue(self.validate())

    def test_found_needs_identity_and_real_file(self):
        self.result['abstract'] = {'status': 'found', 'artifacts': []}
        self.assertTrue(self.validate())

    def test_hash_mismatch_is_rejected(self):
        self.result['evidence'][0]['sha256'] = '0' * 64
        self.assertTrue(self.validate())

    def test_artifact_path_escape_is_rejected(self):
        self.result['evidence'][0]['path'] = '../credentials.txt'
        self.assertTrue(self.validate())

    def test_html_is_not_accepted_as_pdf(self):
        path = self.root / 'login.pdf';path.write_text('<html>Sign in</html>', encoding='utf-8')
        self.result['identity'] = {'status': 'confirmed', 'reason': 'DOI and title agree.'}
        self.result['fulltext'] = {'status': 'found', 'artifacts': [{'path': 'login.pdf', 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                                      'url': 'https://example.org/pdf', 'media_type': 'application/pdf'}]}
        self.assertTrue(self.validate())

    def test_valid_abstract_is_accepted(self):
        path = self.root / 'abstract.txt';path.write_text('An actual abstract with a mathematical result.', encoding='utf-8')
        self.result['identity'] = {'status': 'confirmed', 'reason': 'DOI and title agree.'}
        self.result['abstract'] = {'status': 'found', 'artifacts': [{'path': 'abstract.txt', 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                                   'url': 'https://example.org/paper', 'media_type': 'text/plain'}]}
        self.assertEqual(self.validate(), [])

    def test_placeholder_is_not_abstract(self):
        path = self.root / 'abstract.txt';path.write_text('[No abstract available]', encoding='utf-8')
        self.result['identity'] = {'status': 'confirmed', 'reason': 'DOI and title agree.'}
        self.result['abstract'] = {'status': 'found', 'artifacts': [{'path': 'abstract.txt', 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                                   'url': 'https://example.org/paper', 'media_type': 'text/plain'}]}
        self.assertTrue(self.validate())

    def assignment(self, save_result=True):
        members = self.root / 'catalog/abstract-format-partition/input.jsonl'
        members.parent.mkdir(parents=True)
        members.write_text(json.dumps(self.paper) + '\n', encoding='utf-8')
        worker = self.root / 'g';(worker / 'results').mkdir(parents=True)
        assignment = {'group_id': 'g', 'members_path': 'catalog/abstract-format-partition/input.jsonl',
                      'members_sha256': c.digest(members), 'worker_root': 'g'}
        path = worker / 'assignment.json';path.write_text(json.dumps(assignment), encoding='utf-8')
        if save_result:
            (worker / 'results/VER-1.json').write_text(json.dumps(self.result), encoding='utf-8')
        return path

    def test_full_check_requires_every_assigned_result(self):
        result = c.check_assignment(self.assignment(False))
        self.assertFalse(result['passed'])
        self.assertFalse(result['complete'])
        self.assertEqual(result['missing'], 1)

    def test_partial_check_never_calls_unresolved_identity_complete(self):
        self.result['identity']['status'] = 'unresolved'
        result = c.check_assignment(self.assignment(), partial=True)
        self.assertFalse(result['complete'])

    def test_full_check_accepts_evidence_backed_complete_coverage(self):
        result = c.check_assignment(self.assignment())
        self.assertTrue(result['passed'])
        self.assertTrue(result['complete'])


if __name__ == '__main__':
    unittest.main()

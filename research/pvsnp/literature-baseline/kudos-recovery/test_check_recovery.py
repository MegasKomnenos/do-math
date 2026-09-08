import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import check_recovery as c
from work_queue import VERSION, component_basis


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
        self.result['work_state'] = {'version': VERSION, 'tasks': [
            {'key': 'title', 'kind': 'search', 'target': 'Exact title', 'status': 'done',
             'reason': 'All returned results inspected.', 'evidence_paths': ['proof.txt'],
             'discovered': 0, 'attempted': 0, 'remaining': 0},
            {'key': 'sources', 'kind': 'source', 'target': 'Input and observed source links', 'status': 'done',
             'reason': 'No matching source links present in this fixture.', 'evidence_paths': ['proof.txt']}],
            'reviews': {k: {'basis_sha256': component_basis(self.result, k), 'reason': 'Scoped fixture reviewed.',
                           'evidence_paths': ['proof.txt'], 'scope_complete': True}
                        for k in ('identity', 'abstract', 'fulltext')}}
        result = c.check_assignment(self.assignment())
        self.assertTrue(result['passed'])
        self.assertTrue(result['complete'])


class BinaryAbstractTests(unittest.TestCase):
    def setUp(self):
        self.base = Path(__file__).resolve().parents[1]
        self.fixture = json.loads((self.base / 'kudos-recovery/tdd/binary-abstract-fixture.json').read_text(encoding='utf-8'))
        region = self.fixture['source_region']
        region['pdf_sha256'] = c.digest(self.base / region['pdf'])

    def test_actual_original_abstract_region_png_is_readable(self):
        self.assertEqual(c.artifact_errors(self.fixture, self.base, 'abstract'), [])

    def test_binary_abstract_needs_source_region(self):
        self.fixture.pop('source_region')
        self.assertIn('abstract: source_region required for binary abstract', c.artifact_errors(self.fixture, self.base, 'abstract'))

    def test_region_source_hash_must_match(self):
        self.fixture['source_region']['pdf_sha256'] = '0' * 64
        self.assertIn('source_region: PDF hash mismatch', c.artifact_errors(self.fixture, self.base, 'abstract'))

    def test_region_source_must_be_a_pdf(self):
        self.fixture['source_region']['pdf'] = self.fixture['path']
        self.fixture['source_region']['pdf_sha256'] = self.fixture['sha256']
        self.assertIn('source_region: not a PDF', c.artifact_errors(self.fixture, self.base, 'abstract'))

    def test_password_locked_pdf_is_not_readable_fulltext(self):
        import pymupdf
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp);path = root / 'locked.pdf'
            with pymupdf.open() as doc:
                doc.new_page().insert_text((40, 40), 'Locked document')
                doc.save(path, encryption=pymupdf.PDF_ENCRYPT_AES_256, owner_pw='test-owner', user_pw='test-reader')
            artifact = {'path': path.name, 'sha256': c.digest(path), 'url': 'https://example.org/document',
                        'media_type': 'application/pdf'}
            self.assertIn('fulltext: PDF requires a password', c.artifact_errors(artifact, root, 'fulltext'))

    def test_region_page_and_box_must_exist(self):
        self.fixture['source_region']['page'] = 9999
        self.assertIn('source_region: page out of range', c.artifact_errors(self.fixture, self.base, 'abstract'))
        self.fixture['source_region']['page'] = 1
        self.fixture['source_region']['bbox_points'] = [-1, 0, 99999, 20]
        self.assertIn('source_region: box outside page', c.artifact_errors(self.fixture, self.base, 'abstract'))

    def test_pdf_abstract_region_is_accepted(self):
        import pymupdf
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / 'source.pdf'
            source.write_bytes((self.base / self.fixture['source_region']['pdf']).read_bytes())
            bbox = self.fixture['source_region']['bbox_points']
            target = root / 'abstract.pdf'
            with pymupdf.open(source) as original, pymupdf.open() as cropped:
                page = cropped.new_page(width=bbox[2] - bbox[0], height=bbox[3] - bbox[1])
                page.show_pdf_page(page.rect, original, 0, clip=pymupdf.Rect(bbox))
                cropped.save(target)
            artifact = {'path': 'abstract.pdf', 'sha256': c.digest(target), 'url': self.fixture['url'],
                        'media_type': 'application/pdf', 'source_region': {'pdf': 'source.pdf',
                        'pdf_sha256': c.digest(source), 'page': 1, 'bbox_points': bbox}}
            self.assertEqual(c.artifact_errors(artifact, root, 'abstract'), [])


if __name__ == '__main__':
    unittest.main()

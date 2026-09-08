import importlib.util
import json
import unittest
import recover as r

PAPERS={p['paper_id']:p for p in map(json.loads,(r.BASE/r.ASSIGNMENT['members_path']).read_text(encoding='utf-8').splitlines())}

class ContentReviewTests(unittest.TestCase):
    def review(self,pid):
        self.assertIsNotNone(importlib.util.find_spec('content_review'),'Deterministic review of retained real evidence must exist')
        import content_review
        record=json.loads((r.ROOT/'results'/f'{pid}.json').read_text(encoding='utf-8'))
        return record,content_review.assess(record,PAPERS[pid])

    def test_real_scoped_mr_identity(self):
        record,reviews=self.review('VER-03ffef9bcb026605ecb23809')
        self.assertIn('identity',reviews)

    def test_real_complete_gorbunov_pdf_and_abstract(self):
        record,reviews=self.review('VER-05eea17a72a07d16d806738b')
        self.assertIn('fulltext',reviews)
        self.assertIn('abstract',reviews)

    def test_empty_ams_body_cannot_establish_negative_scope(self):
        record,reviews=self.review('VER-100ededc2c64ac34d061ddb4')
        self.assertNotIn('fulltext',reviews)
        self.assertNotIn('abstract',reviews)

    def test_rejected_connes_paper_is_not_the_book(self):
        record,reviews=self.review('VER-299d3105cede6b2302ad9759')
        self.assertNotEqual(record['fulltext']['status'],'found')
        self.assertNotIn('fulltext',reviews)

    def test_actual_koszul_contents_field_is_not_abstract(self):
        record,reviews=self.review('VER-2a9eea0da2185fc256e28649')
        self.assertNotIn('abstract',reviews)

    def test_actual_missing_pseudorandom_graph_formula_needs_review(self):
        record,reviews=self.review('VER-e2d05541a90bd3a73e974fbf')
        self.assertNotIn('abstract',reviews)

if __name__=='__main__':unittest.main()

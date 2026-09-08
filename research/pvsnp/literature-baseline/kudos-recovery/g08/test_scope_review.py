import importlib.util
import json
import unittest
import recover as r

class ScopeReviewTests(unittest.TestCase):
    def assess(self,pid):
        self.assertIsNotNone(importlib.util.find_spec('scope_review'))
        import scope_review
        record=json.loads((r.ROOT/'results'/f'{pid}.json').read_text(encoding='utf-8'))
        papers={p['paper_id']:p for p in map(json.loads,(r.BASE/r.ASSIGNMENT['members_path']).read_text(encoding='utf-8').splitlines())}
        return scope_review.assess_absence(record,papers[pid])

    def test_new_official_source_reopens_old_zero_query_scope(self):
        reviews=self.assess('VER-09b5e675f4d3706945f363cf')
        self.assertEqual(reviews,{})

    def test_zero_database_scope_requires_complementary_public_searches(self):
        self.assertEqual(self.assess('VER-42d8c1f8b613d8651fb2eaaf'),{})

    def test_real_empty_ams_source_is_not_absence(self):
        self.assertEqual(self.assess('VER-100ededc2c64ac34d061ddb4'),{})

    def test_real_truncated_search_requires_scope_review(self):
        self.assertEqual(self.assess('VER-03ffef9bcb026605ecb23809'),{})

if __name__=='__main__':unittest.main()

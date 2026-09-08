import json,unittest
from pathlib import Path
from regions import suggest_region
BASE=Path('C:/math/research/pvsnp/literature-baseline')

class RegionTests(unittest.TestCase):
    def test_actual_gEy_keyword_ocr_is_excluded(self):
        value=suggest_region(BASE/'intake/kudos-recovery/g05/VER-f2e52f6924dbf95f0b330f3f/pdf-pending.pdf')
        self.assertLess(value['bbox_points'][3],209.94)
    def test_actual_fragmented_single_column_abstract_preserves_right_edge(self):
        value=suggest_region(BASE/'intake/kudos-recovery/g05/VER-e84f6654b69722fc19148fa5/pdf-pending.pdf')
        self.assertIsNotNone(value)
        self.assertGreaterEqual(value['bbox_points'][2],489.39)
        self.assertLess(value['bbox_points'][3],278)
    def test_actual_fragmented_baeten_abstract_is_proposed(self):
        value=suggest_region(BASE/'intake/kudos-recovery/g05/VER-f49156dfb2af746b06ee5b2a/pdf-pending.pdf')
        self.assertIsNotNone(value)
        self.assertGreaterEqual(value['bbox_points'][2],481.77)
        self.assertLess(value['bbox_points'][3],418.4)
    def test_actual_two_page_abstract_requires_manual_regions(self):
        r=json.loads((BASE/'kudos-recovery/g05/results/VER-82b14e07ea722b4ae556ef35.json').read_text())
        self.assertIsNone(suggest_region(BASE/r['fulltext']['artifacts'][0]['path']))
        self.assertIsNone(suggest_region(BASE/'kudos-recovery/g05/tdd/learning-page2.pdf'))
    def test_actual_corrupted_keyword_label_excluded(self):
        r=json.loads((BASE/'kudos-recovery/g05/results/VER-7174a4ee9bff428c7db951c4.json').read_text())
        region=suggest_region(BASE/r['fulltext']['artifacts'][0]['path'])
        self.assertLess(region['bbox_points'][3],325)
    def test_actual_lee_abstract_complete_without_keywords(self):
        value=suggest_region(BASE/'intake/kudos-recovery/g05/VER-028dadfb49623dd97a98242c/fulltext.pdf')
        self.assertIsNotNone(value)
        x0,y0,x1,y1=value['bbox_points']
        self.assertLessEqual(x0,47.28)
        self.assertGreaterEqual(x1,406.47)
        self.assertLessEqual(y0,130.59)
        self.assertGreaterEqual(y1,197.78)
        self.assertLess(y1,202.82)
        self.assertEqual(value['page'],1)
    def test_actual_author_index_has_no_abstract_region(self):
        r=json.loads((BASE/'kudos-recovery/g05/results/VER-3c46753c6a9e521938988d70.json').read_text())
        self.assertIsNone(suggest_region(BASE/r['fulltext']['artifacts'][0]['path']))

if __name__=='__main__':unittest.main()

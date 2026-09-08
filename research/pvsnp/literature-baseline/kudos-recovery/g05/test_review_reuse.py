import copy,importlib.util,json,unittest
from collect import WORK
class ReviewReuseTests(unittest.TestCase):
    def test_actual_title_variant_retains_explicit_visual_pdf_review(self):
        entries=json.loads((WORK/'pending-pdf-review.json').read_text());entry=next(x for x in entries if x['paper_id']=='VER-014dd490736be8ba7793740c')
        record=json.loads((WORK/'results'/f"{entry['paper_id']}.json").read_text())
        if importlib.util.find_spec('review_reuse'):
            from review_reuse import matching_review
        else:matching_review=lambda *args:None
        self.assertIsNotNone(matching_review(record,[entry]))
        self.assertIn('Haris Aziz',entry['review_note'])
        self.assertIn('10.1145/2902945.2902948',entry['artifact']['url'])
        self.assertIsNone(matching_review(record,[]))
        changed=copy.deepcopy(record);changed['metadata']['identifiers']['doi']=['10.1145/unrelated']
        self.assertIsNone(matching_review(changed,[entry]))
        changed=copy.deepcopy(entry);changed['artifact']['sha256']='0'*64
        self.assertIsNone(matching_review(record,[changed]))
        changed=copy.deepcopy(entry);changed['review_status']='needs_review'
        self.assertIsNone(matching_review(record,[changed]))
        changed=copy.deepcopy(record);changed['fulltext']['status']='unresolved'
        self.assertIsNone(matching_review(changed,[entry]))
if __name__=='__main__':unittest.main()

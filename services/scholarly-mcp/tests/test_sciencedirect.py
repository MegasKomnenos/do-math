from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scholarly import ServiceError
from sciencedirect import citation_record,pii_from_url

class ScienceDirectContract(unittest.TestCase):
    def test_native_ris_identity_title_and_full_abstract_are_preserved(self):
        data=(ROOT/'tests/fixtures/science-direct.ris').read_bytes()
        row=citation_record(data,'S002200009791494X','10.1006/jcss.1997.1494')
        self.assertEqual(row['title'],'Natural Proofs')
        self.assertEqual(len(row['fields']['ab'][0]),994)
        self.assertEqual(row['doi'],'10.1006/jcss.1997.1494')
        for pii,doi in [('S0000000000000000','10.1006/jcss.1997.1494'),('S002200009791494X','10.1006/jcss.1997.0000')]:
            with self.assertRaises(ServiceError):
                citation_record(data,pii,doi)

    def test_pii_is_taken_from_the_document_path(self):
        self.assertEqual(pii_from_url('https://www.sciencedirect.com/science/article/abs/pii/S002200009791494X'),'S002200009791494X')
        with self.assertRaises(ServiceError):
            pii_from_url('https://www.sciencedirect.com/search?qs=S002200009791494X')

if __name__=='__main__':
    unittest.main()

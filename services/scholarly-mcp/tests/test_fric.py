from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from fric import catalogue
from scholarly import ServiceError

class FricContract(unittest.TestCase):
    def test_recorded_catalogue_keeps_native_id_issn_and_external_record_link(self):
        rows,total,number,pages,links=catalogue((ROOT/'tests/fixtures/fric-search.html').read_text('utf-8'),'https://fric.knu.ac.kr/pages/sub.htm')
        self.assertEqual((len(rows),total,number,pages),(10,1121,1,113))
        self.assertEqual(rows[0]['id'],'S31001166')
        self.assertEqual(rows[0]['issn'],['2263-8733'])
        self.assertEqual(rows[0]['target'],'issn:2263-8733')
        self.assertIn('www.riss.kr',rows[0]['record_url'])
        self.assertIn(2,links)

    def test_no_result_placeholder_is_not_a_catalogue_record(self):
        rows,total,*_=catalogue((ROOT/'tests/fixtures/fric-zero.html').read_text('utf-8'),'https://fric.knu.ac.kr/')
        self.assertEqual((rows,total),([],0))
        with self.assertRaises(ServiceError):
            catalogue('<body>Loading</body>','https://fric.knu.ac.kr/')

if __name__=='__main__':
    unittest.main()

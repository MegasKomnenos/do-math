import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scholarly import ServiceError

class PQDTSupplementsContract(unittest.TestCase):
    def test_original_file_control_and_count_are_preserved(self):
        from pqdt import supplemental_records
        raw=(ROOT/'tests/fixtures/pqdt-supplement-region.html').read_text('utf-8')
        rows,total=supplemental_records(raw,'https://www.proquest.com/')
        self.assertEqual(total,1);self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['name'],'TLTC_Teaching_Learning_Teaching_Continuum.PNG')
        self.assertIn('downloadfile/',rows[0]['action'])

    def test_missing_or_mismatched_count_is_not_no_files(self):
        from pqdt import supplemental_records
        raw=(ROOT/'tests/fixtures/pqdt-supplement-region.html').read_text('utf-8')
        with self.assertRaises(ServiceError):supplemental_records(raw.replace('includes 1','includes 2'),'https://www.proquest.com/')
        with self.assertRaises(ServiceError):supplemental_records('<h1>Sign in</h1>','https://www.proquest.com/')
        self.assertEqual(supplemental_records('<h5>Document includes 0 supplemental file(s).</h5>','https://www.proquest.com/'),([],0))

    def test_file_label_and_download_action_must_agree(self):
        from pqdt import supplemental_records
        raw=(ROOT/'tests/fixtures/pqdt-supplement-region.html').read_text('utf-8')
        raw=raw.replace('downloadfile/TLTC_Teaching_Learning_Teaching_Continuum.PNG','downloadfile/different.PNG')
        with self.assertRaises(ServiceError):supplemental_records(raw,'https://www.proquest.com/')

if __name__=='__main__':unittest.main()

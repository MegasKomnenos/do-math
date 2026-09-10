import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

class IEEEReferencesContract(unittest.TestCase):
    def test_native_references_survive_an_unavailable_ui_notice(self):
        from ieee import reference_records
        payload=json.loads((ROOT/'tests/fixtures/ieee-references.json').read_text('utf-8'))
        rows=reference_records(payload,'10488889')
        self.assertEqual(len(rows),22)
        self.assertEqual(rows[0]['title'],'PRIMES is in P')
        self.assertIn('10.4007/annals.2004.160.781',rows[0]['text'])
        self.assertEqual(rows[-1]['order'],'22')

    def test_reference_identity_and_empty_array_are_distinct(self):
        from ieee import reference_records
        from scholarly import ServiceError
        self.assertEqual(reference_records({'articleNumber':'1','references':[]},'1'),[])
        with self.assertRaises(ServiceError):
            reference_records({'articleNumber':'2','references':[]},'1')

if __name__=='__main__':
    unittest.main()

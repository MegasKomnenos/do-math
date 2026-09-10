import json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

class AMSContract(unittest.TestCase):
    def test_product_code_url_does_not_require_a_slash_in_the_code(self):
        from ams import AMS
        from scholarly import ArtifactStore
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as temp:
            adapter=AMS(ArtifactStore(temp),None)
            target='https://pubs.ams.org/view?ProductCode=MPRIZE'
            row={'ProductCode':'MPRIZE','Title':'The Millennium Prize Problems','target':target}
            proof=adapter.store.put(json.dumps([row]),'application/json','ams',target)
            def lookup(query,**kwargs):
                adapter.known['mprize']=(row,proof)
                return {'total':1,'received':1}
            with patch.object(adapter,'search',side_effect=lookup) as search,patch.object(adapter,'document',side_effect=AssertionError('Expected catalogue lookup')):
                found=adapter.fetch(target,parts=['metadata'])
            self.assertEqual(found['status'],'ok')
            self.assertEqual(search.call_args.args[0],'MPRIZE')

    def test_mixed_products_keep_subtitle_article_doi_and_meeting_abstract(self):
        from ams import product_records
        payload=json.loads((ROOT/'tests/fixtures/ams-products.json').read_text('utf-8'))
        rows,total,first=product_records(payload)
        self.assertEqual((len(rows),total,first),(12,6587,0))
        self.assertEqual(rows[0]['ProductCode'],'SURV/168')
        self.assertIn('Lie Algebras',rows[0]['Subtitle'])
        self.assertEqual(rows[2]['DOI'],'10.1090/jams/1045')
        self.assertEqual(rows[3]['ContentType'],'ABS')
        self.assertIsNone(rows[3]['DOI'])

    def test_missing_native_row_is_a_range_error(self):
        from ams import product_records
        from scholarly import ServiceError
        payload=json.loads((ROOT/'tests/fixtures/ams-products.json').read_text('utf-8'))
        payload['Products'].pop()
        with self.assertRaises(ServiceError):
            product_records(payload)

if __name__=='__main__':
    unittest.main()

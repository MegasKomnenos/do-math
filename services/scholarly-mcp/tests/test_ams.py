import json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

class AMSContract(unittest.TestCase):
    def test_translated_challenge_is_not_treated_as_a_ready_search_page(self):
        from ams import validate_search_page
        from scholarly import ServiceError
        raw=(ROOT/'tests/fixtures/ams-challenge-ko.html').read_text('utf-8')
        with self.assertRaises(ServiceError) as error:validate_search_page(raw,200)
        self.assertEqual(error.exception.result['status'],'restricted')
        self.assertEqual(error.exception.result['code'],'publisher_access_challenge')

    def test_nested_expression_preserves_native_field_and_operator_meanings(self):
        from ams import advanced_expression,check_expression_request
        from urllib.parse import urlencode,quote
        expression={'condition':'AND','terms':[{'field':'Title','operator':'contains','value':'algebra'},
            {'condition':'OR','terms':[{'field':'PublicationYear','operator':'equals','value':'2000'},
                                     {'field':'PublicationYear','operator':'equals','value':'2001'}]}]}
        native=advanced_expression(expression)
        self.assertEqual(native,json.loads((ROOT/'tests/fixtures/ams-dynamic-query.json').read_text('utf-8')))
        for key in ('advancedSearchJson','dynamicAdvancedSearch'):
            for value in (json.dumps(native),quote(json.dumps(native))):
                check_expression_request(urlencode({key:value}),native)

    def test_invalid_and_changed_expression_are_rejected_before_search(self):
        from ams import advanced_expression,check_expression_request,AMS
        from scholarly import ArtifactStore,ServiceError
        from urllib.parse import urlencode
        leaf={'field':'PublicationYear','operator':'equals','value':'2000'}
        invalid=[{'condition':'NOT','terms':[leaf]}, {'condition':'AND','terms':[]},
                 {'field':'PublicationYear','operator':'contains','value':'2000'},
                 {'field':'Title','operator':'equals','value':''}, {**leaf,'unknown':True}]
        for value in invalid:
            with self.assertRaises(ServiceError):advanced_expression(value)
        native=advanced_expression({'condition':'AND','terms':[leaf]})
        changed={'condition':'AND','queryElements':[{**native['queryElements'][0],'value':'2001'}]}
        for body in (urlencode({'advancedSearchJson':json.dumps(changed)}), 'advancedSearch=ProductTitle%3Dalgebra'):
            with self.assertRaises(ServiceError) as error:check_expression_request(body,native)
            self.assertEqual(error.exception.result['code'],'query_mismatch')
        with tempfile.TemporaryDirectory() as temp:
            adapter=AMS(ArtifactStore(temp),None)
            for query,options in [('algebra',{'expression':{'condition':'AND','terms':[leaf]}}),
                                  ('',{'expression':{'condition':'AND','terms':[leaf]},'author':'Knuth'})]:
                with self.assertRaises(ServiceError) as error:adapter.search(query,options=options)
                self.assertEqual(error.exception.result['code'],'invalid_options')

    def test_unavailable_search_page_is_not_an_input_timeout_or_no_results(self):
        from ams import validate_search_page
        from scholarly import ServiceError
        raw=(ROOT/'tests/fixtures/ams-unavailable.html').read_text('utf-8')
        with self.assertRaises(ServiceError) as cm:validate_search_page(raw)
        self.assertEqual(cm.exception.result['code'],'provider_unavailable')
        self.assertEqual(cm.exception.result['status'],'error')
        self.assertTrue(cm.exception.result['retryable'])
        with self.assertRaises(ServiceError) as cm:validate_search_page('<html><body>Denied</body></html>',403)
        self.assertEqual(cm.exception.result['status'],'restricted')
        validate_search_page('<html><head><title>Advanced Search</title></head><body>Search</body></html>',200)

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

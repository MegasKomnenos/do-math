import json,sys,tempfile,unittest
import io
from pathlib import Path
from unittest.mock import Mock,patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

class AMSContract(unittest.TestCase):
    def test_provider_error_string_is_a_typed_response_failure(self):
        from ams import product_records
        from scholarly import ServiceError
        with self.assertRaises(ServiceError) as raised:
            product_records('{"message":"SYNTHETIC_PROVIDER_ERROR"}')
        self.assertEqual(raised.exception.result['code'],'invalid_response')
        self.assertNotIn('SYNTHETIC_PROVIDER_ERROR',str(raised.exception.result))

    def test_native_zero_count_allows_null_products_without_changing_evidence(self):
        from ams import product_records
        from scholarly import ServiceError
        payload={'Products':None,'Filters':None,'TotalRows':0,'PageNumber':1,'RowsPerPage':12,'SortBy':None}
        self.assertEqual(product_records(payload),([],0,0))
        self.assertIsNone(payload['Products'])
        payload['TotalRows']=1
        with self.assertRaises(ServiceError):product_records(payload)

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

    def test_native_xlsx_keeps_variant_rows_and_binds_one_logical_product(self):
        from ams import validate_product_xlsx
        from openpyxl import Workbook
        row=json.loads((ROOT/'tests/fixtures/ams-products.json').read_text('utf-8'))['Products'][0]
        workbook=Workbook();sheet=workbook.active;sheet.title='Products'
        sheet.append(['Product Code','Title','ISBN','Author/Editor','Publication Date'])
        for isbn in ('978-0-8218-5262-0','978-1-4704-1395-8',''):
            sheet.append(['','Algebras, Rings and Modules: Lie Algebras and Hopf Algebras',isbn,
                          'Michiel Hazewinkel; Nadiya Gubareni; V. V. Kirichenko',2010])
        output=io.BytesIO();workbook.save(output);workbook.close()
        found=validate_product_xlsx(output.getvalue(),row)
        self.assertEqual(found['physical_rows'],3)
        self.assertEqual(found['logical_products'],1)
        self.assertEqual(found['product_code'],'SURV/168')
        self.assertEqual(found['product_code_cells'],0)
        self.assertEqual(found['native_isbn_rows'],1)

    def test_native_xlsx_rejects_another_product_without_filling_blank_codes(self):
        from ams import validate_product_xlsx
        from openpyxl import Workbook
        from scholarly import ServiceError
        row=json.loads((ROOT/'tests/fixtures/ams-products.json').read_text('utf-8'))['Products'][0]
        workbook=Workbook();sheet=workbook.active;sheet.append(['Product Code','Title','ISBN','Author/Editor','Publication Date'])
        sheet.append(['','Another Product','978-0-8218-5262-0','Different Author',2010])
        output=io.BytesIO();workbook.save(output);workbook.close()
        with self.assertRaises(ServiceError) as error:validate_product_xlsx(output.getvalue(),row)
        self.assertEqual(error.exception.result['code'],'identity_mismatch')

    def test_native_xlsx_rejects_nonblank_code_from_another_product(self):
        from ams import validate_product_xlsx
        from openpyxl import Workbook
        from scholarly import ServiceError
        row=json.loads((ROOT/'tests/fixtures/ams-products.json').read_text('utf-8'))['Products'][0]
        workbook=Workbook();sheet=workbook.active;sheet.append(['Product Code','Title','ISBN','Author/Editor','Publication Date'])
        sheet.append(['OTHER/1','Algebras, Rings and Modules: Lie Algebras and Hopf Algebras','978-0-8218-5262-0',
                      'Michiel Hazewinkel; Nadiya Gubareni; V. V. Kirichenko',2010])
        output=io.BytesIO();workbook.save(output);workbook.close()
        with self.assertRaises(ServiceError) as error:validate_product_xlsx(output.getvalue(),row)
        self.assertEqual(error.exception.result['code'],'identity_mismatch')

    def test_native_xlsx_secret_scan_decodes_xml_entities(self):
        from ams import validate_product_xlsx
        from openpyxl import Workbook
        from scholarly import ServiceError
        row=json.loads((ROOT/'tests/fixtures/ams-products.json').read_text('utf-8'))['Products'][0]
        workbook=Workbook();sheet=workbook.active;sheet.append(['Product Code','Title','ISBN','Author/Editor','Publication Date'])
        sheet.append(['','Algebras, Rings and Modules: Lie Algebras and Hopf Algebras private&credential','978-0-8218-5262-0',
                      'Michiel Hazewinkel; Nadiya Gubareni; V. V. Kirichenko',2010])
        output=io.BytesIO();workbook.save(output);workbook.close()
        with self.assertRaises(ServiceError) as error:validate_product_xlsx(output.getvalue(),row,('private&credential',))
        self.assertEqual(error.exception.result['code'],'sensitive_export')

    def test_selected_window_export_uses_exact_product_search_and_response_body(self):
        from ams import AMS
        from openpyxl import Workbook
        from scholarly import ArtifactStore
        row=json.loads((ROOT/'tests/fixtures/ams-products.json').read_text('utf-8'))['Products'][0]
        workbook=Workbook();sheet=workbook.active;sheet.title='Products'
        sheet.append(['Product Code','Title','ISBN','Author/Editor','Publication Date'])
        for isbn in ('978-0-8218-5262-0','978-1-4704-1395-8',''):
            sheet.append(['','Algebras, Rings and Modules: Lie Algebras and Hopf Algebras',isbn,
                          'Michiel Hazewinkel; Nadiya Gubareni; V. V. Kirichenko',2010])
        output=io.BytesIO();workbook.save(output);workbook.close();xlsx=output.getvalue()
        page=Mock();page.is_closed.return_value=False
        response=Mock(status=200,headers={'content-type':'application/octet-stream','content-disposition':'attachment'},url='https://pubs.ams.org/product/exportproducts')
        response.request=Mock(post_data='advancedSearch=ProductCode%3DSURV%252F168')
        response.body.return_value=xlsx
        pending=Mock();pending.value=response
        page.expect_response.return_value.__enter__=Mock(return_value=pending)
        page.expect_response.return_value.__exit__=Mock(return_value=False)
        page.evaluate.side_effect=lambda script,*args: None
        gateway=Mock();gateway.pages={'ams':page}
        with tempfile.TemporaryDirectory() as temp:
            adapter=AMS(ArtifactStore(temp),gateway)
            def exact(query,**kwargs):
                self.assertEqual((query,kwargs['options'],kwargs['limit'],kwargs['export']),
                                 ('SURV/168',{'field':'ProductCode'},2,None))
                adapter.known['surv/168']=(row,{'ref':'proof'})
                return {'status':'ok','total':1,'received':1,'preview':[row]}
            with patch.object(adapter,'search',side_effect=exact):
                exported=adapter.export_products([row])
            self.assertEqual(exported['status'],'available')
            self.assertEqual(exported['logical_products'],1)
            self.assertEqual(exported['artifacts'][0]['physical_rows'],3)
            self.assertEqual(page.evaluate.call_args.args[0],'uniqueId => initExportResults(uniqueId)')
            self.assertEqual(page.evaluate.call_args.args[1],'')
            self.assertNotIn('headers',exported['artifacts'][0]['artifact'])

    def test_selected_window_export_rejects_stale_product_filter(self):
        from ams import AMS
        from scholarly import ArtifactStore
        row=json.loads((ROOT/'tests/fixtures/ams-products.json').read_text('utf-8'))['Products'][0]
        page=Mock();page.is_closed.return_value=False
        response=Mock(status=200,headers={'content-type':'application/octet-stream'},url='https://pubs.ams.org/product/exportproducts')
        response.request=Mock(post_data='advancedSearch=ProductCode%3DOTHER%252F1')
        pending=Mock();pending.value=response
        page.expect_response.return_value.__enter__=Mock(return_value=pending)
        page.expect_response.return_value.__exit__=Mock(return_value=False)
        gateway=Mock();gateway.pages={'ams':page}
        with tempfile.TemporaryDirectory() as temp:
            adapter=AMS(ArtifactStore(temp),gateway)
            with patch.object(adapter,'search',return_value={'status':'ok','total':1,'received':1,'preview':[row]}):
                exported=adapter.export_products([row])
        self.assertEqual(exported['status'],'error')
        self.assertEqual(exported['errors'][0]['code'],'query_mismatch')

if __name__=='__main__':
    unittest.main()

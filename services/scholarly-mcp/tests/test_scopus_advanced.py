import json,sys,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scholarly import ServiceError
from scopus import SCOPUS_FACET_GROUPS,SCOPUS_NATIVE_FACETS,SCOPUS_SORTS,SCOPUS_SORT_REQUESTS,search_options,scopus_facet_candidates,validate_primary_request,filter_count_records,validate_facet_transition,validate_sort_transition,displayed_query

class ScopusAdvanced(unittest.TestCase):
    def show_current_query(self,page,query):
        page.get_by_role.return_value.filter.return_value.count.return_value=0
        page.locator.return_value.filter.return_value.all.return_value=[SimpleNamespace(inner_text=lambda:query)]

    def test_all_current_result_sorts_and_twelve_facet_groups_are_named(self):
        self.assertEqual(set(SCOPUS_SORTS),{'newest','oldest','cited-highest','cited-lowest','relevance',
            'author-asc','author-desc','source-title-asc','source-title-desc'})
        self.assertEqual(set(SCOPUS_FACET_GROUPS),{'year','subject_area','document_type','language','keyword','country_territory',
            'source_type','source_title','author_name','publication_stage','affiliation','funding_sponsor','open_access'})
        self.assertEqual(set(SCOPUS_NATIVE_FACETS),set(SCOPUS_FACET_GROUPS))

    def test_friendly_facet_contract_preserves_include_exclude_and_candidate_lookup(self):
        value=search_options({'sort':'cited-highest','facet_filters':{
            'document_type':{'include':['Article','Review'],'exclude':['Book chapter']},
            'language':{'include':['English']}},'facet_group':'source_title'})
        self.assertEqual(value['sort'],('Cited by (highest)','cp-f'))
        self.assertEqual(value['facet_filters'][0],('document_type','document-type-section',['Article','Review'],['Book chapter']))
        self.assertEqual(value['facet_preview'],('source_title','source-title-section',None))

    def test_invalid_or_ambiguous_facet_requests_are_rejected(self):
        invalid=({'sort':'invented'},{'facet_filters':[]},{'facet_filters':{'invented':{'include':['x']}}},
            {'facet_filters':{'document_type':{'include':[]}}},
            {'facet_filters':{'document_type':{'include':['Article'],'exclude':['article']}}},
            {'facet_group':'source_title','facet_query':''},{'facet_query':'x'})
        for options in invalid:
            with self.subTest(options=options),self.assertRaises(ServiceError):search_options(options)

    def test_candidates_are_scoped_to_one_current_result_group(self):
        raw=(ROOT/'tests/fixtures/scopus-facet.html').read_text('utf-8')
        self.assertEqual(scopus_facet_candidates(raw,'document-type-section'),[
            {'label':'Article','count':14,'native_term':'ar'},{'label':'Conference paper','count':4,'native_term':'cp'},
            {'label':'Review','count':2,'native_term':'re'},{'label':'Book chapter','count':1,'native_term':'ch'}])

    def test_request_validation_binds_query_sort_and_accumulated_facets(self):
        sort=[{'fieldName':'numcitedby','order':'desc'},{'fieldName':'datesort','order':'desc'}]
        facets=[{'facetName':'subtype','facetTerms':[{'action':'limit-to','term':'ar'}]}]
        request={'query':'TITLE("P versus NP")','documentClassification':'primary','sortBy':sort,'facetFilters':facets,
                 'resultSet':{'offset':0,'itemCount':10}}
        validate_primary_request(request,'TITLE("P versus NP")',sort,facets)
        for changed in ({**request,'query':'wrong'},{**request,'sortBy':[]},{**request,'facetFilters':[]}):
            with self.assertRaises(ServiceError):validate_primary_request(changed,'TITLE("P versus NP")',sort,facets)
        validate_primary_request({**request,'facetFilters':None},'TITLE("P versus NP")',sort,[])
        with self.assertRaises(ServiceError):validate_primary_request(request,'TITLE("P versus NP")',sort,[])

    def test_facet_transition_preserves_prior_terms_and_binds_action_and_multiplicity(self):
        previous=[{'facetName':'subtype','facetTerms':[{'action':'limit-to','term':'ar'}]}]
        current=[*previous,{'facetName':'lang','facetTerms':[{'action':'limit-to','term':'English'}]}]
        request={'query':'Q','documentClassification':'primary','facetFilters':current}
        self.assertEqual(validate_facet_transition(request,'Q',previous,'lang','limit-to',['English']),current)
        for bad in (
            {'query':'Q','documentClassification':'primary','facetFilters':current[1:]},
            {'query':'Q','documentClassification':'primary','facetFilters':[previous[0],{'facetName':'lang','facetTerms':[{'action':'exclude','term':'English'}]}]},
            {'query':'Q','documentClassification':'primary','facetFilters':[previous[0],{'facetName':'lang','facetTerms':[{'action':'limit-to','term':'English'},{'action':'limit-to','term':'Korean'}]}]}):
            with self.assertRaises(ServiceError):validate_facet_transition(bad,'Q',previous,'lang','limit-to',['English'])
        with self.assertRaises(ServiceError):validate_facet_transition(request,'Q',previous,'year','limit-to',['English'])
        with self.assertRaises(ServiceError):validate_facet_transition(request,'Q',previous,'lang','limit-to',['wrong'])

    def test_sort_transition_preserves_facets_and_rejects_captured_or_invalid_sort(self):
        old=[{'fieldName':'datesort','order':'desc'}];new=[{'fieldName':'numcitedby','order':'desc'},{'fieldName':'datesort','order':'desc'}]
        facets=[{'facetName':'subtype','facetTerms':[{'action':'limit-to','term':'ar'}]}]
        request={'query':'Q','documentClassification':'primary','sortBy':new,'facetFilters':facets}
        self.assertEqual(validate_sort_transition(request,'Q',new,facets),new)
        for changed in ({**request,'sortBy':old},{**request,'facetFilters':[]},{**request,'sortBy':[{'fieldName':'x','order':'sideways'}]}):
            with self.assertRaises(ServiceError):validate_sort_transition(changed,'Q',new,facets)

    def test_every_visible_sort_has_its_observed_native_request(self):
        self.assertEqual(set(SCOPUS_SORT_REQUESTS),{value for _,value in SCOPUS_SORTS.values()})
        self.assertEqual(SCOPUS_SORT_REQUESTS['cp-f'],[{'fieldName':'numcitedby','order':'desc'},{'fieldName':'datesort','order':'desc'}])

    def test_native_filter_count_csv_binds_query_groups_labels_and_counts(self):
        data=(ROOT/'tests/fixtures/scopus-filter-counts.csv').read_bytes();parsed=filter_count_records(data,'TITLE("P versus NP")')
        self.assertEqual(parsed['groups'],['OPEN ACCESS','YEAR','FUNDING SPONSOR'])
        self.assertEqual(parsed['candidate_rows'],2)
        self.assertEqual(parsed['candidates']['FUNDING SPONSOR'][0],{'label':'National Science Foundation','count':3})
        with self.assertRaises(ServiceError):filter_count_records(data,'TITLE(other)')
        with self.assertRaises(ServiceError):filter_count_records(b'<html>Error</html>','TITLE("P versus NP")')
        with self.assertRaises(ServiceError) as error:filter_count_records(b'undefined\r\n','TITLE("P versus NP")')
        self.assertEqual(error.exception.result['code'],'invalid_native_export')
        malformed=data.replace(b'National Science Foundation","3"',b'National Science Foundation","1,,2"')
        with self.assertRaises(ServiceError) as error:filter_count_records(malformed,'TITLE("P versus NP")')
        self.assertEqual(error.exception.result['code'],'invalid_native_export')
        duplicate_group=data.replace(b'"YEAR"',b'"open access"')
        with self.assertRaises(ServiceError):filter_count_records(duplicate_group,'TITLE("P versus NP")')
        filtered=(ROOT/'tests/fixtures/scopus-filter-counts-filtered.csv').read_bytes();native='TITLE("P versus NP") AND ( LIMIT-TO ( DOCTYPE,"ar" ) )'
        parsed=filter_count_records(filtered,native)
        self.assertIn('LIMIT-TO',parsed['native_query']);self.assertEqual(parsed['candidates']['DOCUMENT TYPE'],[{'label':'Article','count':14}])
        with self.assertRaises(ServiceError):filter_count_records(filtered,native.replace('"ar"','"re"'))

    def test_displayed_query_reads_visible_editor_without_stale_hidden_model(self):
        page=MagicMock();page.evaluate.return_value=['TITLE("P versus NP") AND ( LIMIT-TO ( DOCTYPE,"ar" ) ) AND ( LIMIT-TO ( LANGUAGE,"English" ) )'];editor=MagicMock();editor.inner_text.return_value='TITLE ( "P versus NP" ) AND ( LIMIT-TO ( DOCTYPE,"ar" ) )'
        page.locator.return_value.filter.return_value.all.return_value=[editor]
        self.assertEqual(displayed_query(page,'TITLE("P versus NP")'),'TITLE ( "P versus NP" ) AND ( LIMIT-TO ( DOCTYPE,"ar" ) )')
        editor.inner_text.return_value='OTHER'
        with self.assertRaises(ServiceError):displayed_query(page,'TITLE("P versus NP")')

    def test_displayed_query_uses_the_source_copy_control_when_models_are_not_exposed(self):
        page=MagicMock();page.locator.return_value.filter.return_value.all.return_value=[]
        page.evaluate.side_effect=[None,'TITLE ( "P versus NP" ) AND ( LIMIT-TO ( DOCTYPE , "ar" ) )',None]
        copy=MagicMock();copy.count.return_value=1;page.get_by_role.return_value.filter.return_value=copy
        value=displayed_query(page,'TITLE("P versus NP")')
        self.assertIn('LIMIT-TO',value);copy.click.assert_called_once_with()

    def test_filter_count_download_uses_the_observed_control_and_preserves_bytes(self):
        import tempfile
        from scholarly import ArtifactStore
        with tempfile.TemporaryDirectory() as temp:
            source=ROOT/'tests/fixtures/scopus-filter-counts.csv';download=SimpleNamespace(path=lambda:str(source),suggested_filename='refine.csv',failure=lambda:None)
            response=SimpleNamespace(status=200,url='https://www.scopus.com/gateway/document-facet-api/facets/export',
                headers={'content-type':'application/octet-stream'},request=SimpleNamespace(post_data_json={
                    'query':'TITLE("P versus NP")','documentClassification':'primary','facetFilters':[]}),body=lambda:source.read_bytes().removeprefix(b'\xef\xbb\xbf'))
            event=MagicMock();event.__enter__.return_value=event;event.value=response
            trigger=MagicMock();trigger.count.return_value=1;trigger.is_visible.return_value=True;trigger.is_enabled.return_value=True
            callbacks={};trigger.click.side_effect=lambda:callbacks['download'](download)
            page=MagicMock();page.url='https://www.scopus.com/pages/search/publications';page.locator.return_value.filter.return_value=trigger
            page.evaluate.return_value=['TITLE("P versus NP")'];page.locator.return_value.filter.return_value.all.return_value=[]
            page.on.side_effect=lambda name,callback:callbacks.__setitem__(name,callback);page.expect_response.return_value=event
            adapter=__import__('scopus').Scopus(ArtifactStore(temp),None)
            self.show_current_query(page,'TITLE("P versus NP")')
            artifact=adapter.facet_count_export(page,'TITLE("P versus NP")',21,[])
            manifest,data=adapter.store.read(artifact['ref'])
        self.assertEqual(data,source.read_bytes());self.assertEqual(artifact['facet_groups'],['OPEN ACCESS','YEAR','FUNDING SPONSOR'])
        self.assertIn('source_response_ref',artifact)
        self.assertEqual(manifest['role'],'native_facet_counts')

    def test_invalid_filter_count_response_is_preserved_safely_before_error(self):
        import tempfile
        from scholarly import ArtifactStore
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);response=SimpleNamespace(status=200,url='https://www.scopus.com/gateway/document-facet-api/facets/export',
                headers={'content-type':'text/html'},request=SimpleNamespace(post_data_json={'query':'Q','documentClassification':'primary','facetFilters':[]}),
                body=lambda:b'<html><script>private()</script><p>Error</p></html>')
            event=MagicMock();event.__enter__.return_value=event;event.value=response
            trigger=MagicMock();trigger.count.return_value=1;trigger.is_visible.return_value=True;trigger.is_enabled.return_value=True
            page=MagicMock();page.evaluate.return_value=['Q'];page.locator.return_value.filter.return_value=trigger;page.expect_response.return_value=event
            adapter=__import__('scopus').Scopus(store,None)
            self.show_current_query(page,'Q')
            with self.assertRaises(ServiceError) as error:adapter.facet_count_export(page,'Q',1,[])
            artifact=error.exception.result['source_export'];manifest,data=store.read(artifact['ref'])
        self.assertEqual(manifest['media_type'],'text/html');self.assertNotIn(b'<script',data);self.assertIn(b'Error',data)

    def test_filter_count_http_error_preserves_sanitized_response(self):
        import tempfile
        from scholarly import ArtifactStore
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);response=SimpleNamespace(status=500,url='https://www.scopus.com/gateway/document-facet-api/facets/export',
                headers={'content-type':'text/html'},request=SimpleNamespace(post_data_json={'query':'Q','documentClassification':'primary','facetFilters':[]}),
                body=lambda:b'<html><script>private()</script><p>Provider failed</p></html>')
            event=MagicMock();event.__enter__.return_value=event;event.value=response
            trigger=MagicMock();trigger.count.return_value=1;trigger.is_visible.return_value=True;trigger.is_enabled.return_value=True
            page=MagicMock();page.evaluate.return_value=['Q'];page.locator.return_value.filter.return_value=trigger;page.expect_response.return_value=event
            adapter=__import__('scopus').Scopus(store,None)
            self.show_current_query(page,'Q')
            with self.assertRaises(ServiceError) as error:adapter.facet_count_export(page,'Q',1,[])
            artifact=error.exception.result['source_export'];_,data=store.read(artifact['ref'])
        self.assertEqual(error.exception.result['code'],'provider_error');self.assertNotIn(b'<script',data);self.assertIn(b'Provider failed',data)

    def test_failed_json_response_uses_field_sanitization(self):
        import tempfile
        from scholarly import ArtifactStore
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);adapter=__import__('scopus').Scopus(store,None)
            artifact=adapter.invalid_export_artifact(b'{"token":"SYNTHETIC_SECRET","message":"failed"}','application/json',
                'https://www.scopus.com/gateway/document-facet-api/facets/export','failed_native_facet_counts_response')
            _,data=store.read(artifact['ref'])
        self.assertNotIn(b'SYNTHETIC_SECRET',data);self.assertIn(b'failed',data)

    def test_bom_prefixed_html_failure_is_sanitized(self):
        import tempfile
        from scholarly import ArtifactStore
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);adapter=__import__('scopus').Scopus(store,None)
            artifact=adapter.invalid_export_artifact(b'\xef\xbb\xbf<html><script>private()</script><p>Error</p></html>','application/octet-stream',
                'https://www.scopus.com/gateway/document-facet-api/facets/export','failed_native_facet_counts_response')
            _,data=store.read(artifact['ref'])
        self.assertNotIn(b'<script',data);self.assertIn(b'Error',data)

    def test_invalid_download_preserves_both_valid_response_and_bad_file(self):
        import tempfile
        from scholarly import ArtifactStore
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);source=ROOT/'tests/fixtures/scopus-filter-counts.csv';bad=Path(temp)/'bad.csv';bad.write_bytes(b'undefined')
            download=SimpleNamespace(path=lambda:str(bad),suggested_filename='refine.csv',failure=lambda:None)
            response=SimpleNamespace(status=200,url='https://www.scopus.com/gateway/document-facet-api/facets/export',headers={'content-type':'application/octet-stream'},
                request=SimpleNamespace(post_data_json={'query':'TITLE("P versus NP")','documentClassification':'primary','facetFilters':[]}),
                body=lambda:source.read_bytes().removeprefix(b'\xef\xbb\xbf'))
            event=MagicMock();event.__enter__.return_value=event;event.value=response
            trigger=MagicMock();trigger.count.return_value=1;trigger.is_visible.return_value=True;trigger.is_enabled.return_value=True
            callbacks={};trigger.click.side_effect=lambda:callbacks['download'](download)
            page=MagicMock();page.evaluate.return_value=['TITLE("P versus NP")'];page.locator.return_value.filter.return_value=trigger
            page.locator.return_value.filter.return_value.all.return_value=[];page.on.side_effect=lambda name,callback:callbacks.__setitem__(name,callback);page.expect_response.return_value=event
            adapter=__import__('scopus').Scopus(store,None)
            self.show_current_query(page,'TITLE("P versus NP")')
            with self.assertRaises(ServiceError) as error:adapter.facet_count_export(page,'TITLE("P versus NP")',21,[])
            _,failed=store.read(error.exception.result['source_export']['ref']);_,valid=store.read(error.exception.result['source_response']['ref'])
        self.assertEqual(failed,b'undefined');self.assertTrue(valid.startswith(b'"Scopus refine results values"'))

    def test_missing_download_keeps_the_valid_source_response(self):
        import tempfile
        from scholarly import ArtifactStore
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);source=ROOT/'tests/fixtures/scopus-filter-counts.csv'
            response=SimpleNamespace(status=200,url='https://www.scopus.com/gateway/document-facet-api/facets/export',headers={'content-type':'application/octet-stream'},
                request=SimpleNamespace(post_data_json={'query':'TITLE("P versus NP")','documentClassification':'primary','facetFilters':[]}),
                body=lambda:source.read_bytes().removeprefix(b'\xef\xbb\xbf'))
            event=MagicMock();event.__enter__.return_value=event;event.value=response
            trigger=MagicMock();trigger.count.return_value=1;trigger.is_visible.return_value=True;trigger.is_enabled.return_value=True
            page=MagicMock();page.evaluate.return_value=['TITLE("P versus NP")'];page.locator.return_value.filter.return_value=trigger
            page.locator.return_value.filter.return_value.all.return_value=[];page.expect_response.return_value=event
            adapter=__import__('scopus').Scopus(store,None)
            self.show_current_query(page,'TITLE("P versus NP")')
            with self.assertRaises(ServiceError) as error:adapter.facet_count_export(page,'TITLE("P versus NP")',21,[])
        self.assertEqual(error.exception.result['code'],'export_failed');self.assertIn('source_response',error.exception.result)

    def test_later_page_internal_duplicate_preserves_prefix_evidence_and_resume_offset(self):
        import tempfile
        from scholarly import ArtifactStore
        from unittest.mock import patch
        def payload(offset,identifiers):return {'metadata':{'offset':offset,'totalCount':20,'itemCount':10},
            'items':[{'eid':value,'title':value} for value in identifiers]}
        request={'query':'Q','documentClassification':'primary','sortBy':SCOPUS_SORT_REQUESTS['plf-f'],'resultSet':{'offset':0,'itemCount':10}}
        responses=[SimpleNamespace(status=200,url='https://www.scopus.com/gateway/documents/search',json=lambda value=payload(0,[f'2-s2.0-{i}' for i in range(10)]):value,
                    request=SimpleNamespace(post_data_json=request)),
            SimpleNamespace(status=200,url='https://www.scopus.com/gateway/documents/search',json=lambda value=payload(10,['2-s2.0-10']*2+[f'2-s2.0-{i}' for i in range(11,19)]):value,
                    request=SimpleNamespace(post_data_json={**request,'resultSet':{'offset':10,'itemCount':10}}))]
        events=[]
        for response in responses:
            event=MagicMock();event.__enter__.return_value=event;event.value=response;events.append(event)
        page=MagicMock();page.url='https://www.scopus.com/pages/search/publications';page.expect_response.side_effect=events
        gateway=SimpleNamespace(pages={'scopus':page});gateway.context=MagicMock()
        with tempfile.TemporaryDirectory() as temp:
            adapter=__import__('scopus').Scopus(ArtifactStore(temp),gateway);adapter.page=MagicMock(return_value=page)
            with patch('scopus.goto_source'),patch.object(adapter,'apply_facets',return_value=(responses[0],[],[],[])), \
                 patch.object(adapter,'apply_sort',return_value=(responses[0],None,SCOPUS_SORT_REQUESTS['plf-f'])):
                result=adapter.search('Q',options={},limit=20)
            rows=json.loads(adapter.store.read(result['records']['ref'])[1])
        self.assertEqual(result['status'],'partial');self.assertEqual(len(rows),10);self.assertEqual(len(result['evidence']),2)
        self.assertEqual(result['next'],{'start':10});self.assertEqual(result['pagination_error']['page_offset'],10)

    def test_zero_base_query_returns_before_facet_controls(self):
        import tempfile
        from scholarly import ArtifactStore
        from unittest.mock import patch
        payload={'metadata':{'offset':0,'totalCount':0,'itemCount':10},'items':[]}
        request={'query':'NONE','documentClassification':'primary','sortBy':SCOPUS_SORT_REQUESTS['plf-f'],'resultSet':{'offset':0,'itemCount':10}}
        response=SimpleNamespace(status=200,url='https://www.scopus.com/gateway/documents/search',json=lambda:payload,request=SimpleNamespace(post_data_json=request))
        event=MagicMock();event.__enter__.return_value=event;event.value=response
        page=MagicMock();page.url='https://www.scopus.com/pages/search/publications';page.expect_response.return_value=event
        gateway=SimpleNamespace(pages={'scopus':page},context=MagicMock())
        with tempfile.TemporaryDirectory() as temp:
            adapter=__import__('scopus').Scopus(ArtifactStore(temp),gateway);adapter.page=MagicMock(return_value=page)
            with patch('scopus.goto_source'),patch.object(adapter,'apply_facets',side_effect=AssertionError('must not open facets')):
                result=adapter.search('NONE',options={'facet_filters':{'document_type':{'include':['Article']}}},limit=1)
        self.assertEqual((result['status'],result['total'],result['received']),('not_found',0,0));self.assertEqual(result['facet_status'],'unavailable_empty_result')

if __name__=='__main__':unittest.main()

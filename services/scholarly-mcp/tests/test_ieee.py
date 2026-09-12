import importlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class IEEEContract(unittest.TestCase):
    def test_current_facets_preserve_native_labels_values_counts_and_selection(self):
        from ieee import ieee_facets,remember_facet_candidate
        raw=json.loads((ROOT/'tests/fixtures/ieee-search.json').read_text('utf-8'))
        raw['breadCrumbs'].append({'type':'refinement','key':'Content Type','children':[{'value':'ContentType:Magazines'}]})
        facets=ieee_facets(raw)
        content=next(group for group in facets if group['field']=='content_types')
        self.assertEqual(content['native_group'],'ContentType')
        self.assertEqual(content['candidates'],[{'value':'Magazines','label':'Magazines','count':1,'selected':True}])
        publication=next(group for group in facets if group['field']=='publication_titles')
        self.assertEqual(publication['candidates'][0]['value'],'Computer')
        remember_facet_candidate(facets,'publication_titles','Artificial Life',24)
        self.assertIn({'value':'Artificial Life','label':'Artificial Life','count':24,'selected':True,'basis':'native_typeahead'},publication['candidates'])

    def test_search_options_are_typed_and_keep_command_query_fields_separate(self):
        from ieee import SORTS,search_options
        self.assertEqual(search_options({'sort':'newest','access':'open_access','year':'2020-2024',
                         'content_types':['Journals'],'publication_titles':['IEEE Access']}),
                         {'sort':'newest','access':'open_access','year':'2020-2024','content_types':['Journals'],
                          'publication_titles':['IEEE Access']})
        for sort in SORTS:self.assertEqual(search_options({'sort':sort})['sort'],sort)
        for bad in ({'sort':'date'},{'access':'open'},{'year':'2024-2020'},{'year':[2020,2024]},
                    {'sort':[]},{'access':{}},{'content_types':'Journals'},{'publication_titles':['IEEE Access','IEEE Access']},
                    {'publication_titles':['IEEE Access',' IEEE Access ']},{'unknown':True}):
            with self.assertRaises(Exception):search_options(bad)

    def test_result_filter_state_requires_exact_native_breadcrumbs(self):
        from ieee import validate_filter_state,validate_request_state
        from types import SimpleNamespace
        raw=json.loads((ROOT/'tests/fixtures/ieee-search.json').read_text('utf-8'))
        raw.update(sortValue='newest',subscribedContentApplied=False)
        raw['breadCrumbs'] += [
            {'type':'refinement','value':'ContentType:','children':[{'value':'ContentType:Magazines'}]},
            {'type':'refinement','value':'PublicationTitle:','children':[{'value':'PublicationTitle:Computer'}]},
            {'type':'range','key':'Year','reference':'2020_2024_Year','start':'2020','end':'2024'}]
        validate_filter_state(raw,{'sort':'newest','access':'all','year':'2020-2024','content_types':['Magazines'],'publication_titles':['Computer']})
        response=SimpleNamespace(request=SimpleNamespace(post_data_json={'queryText':'q','sortType':'newest','ranges':['2020_2024_Year'],
            'refinements':['ContentType:Magazines','PublicationTitle:Computer']}))
        validate_request_state(response,{'sort':'newest','access':'all','year':'2020-2024','content_types':['Magazines'],'publication_titles':['Computer']},1)
        with self.assertRaises(Exception):
            validate_filter_state(raw,{'sort':'oldest','access':'all','year':'2020-2024','content_types':['Magazines'],'publication_titles':['Computer']})
        response.request.post_data_json['refinements'].append('Publisher:IEEE')
        with self.assertRaises(Exception):validate_request_state(response,{'sort':'newest','access':'all','year':'2020-2024','content_types':['Magazines'],'publication_titles':['Computer']},1)

    def test_all_visible_sort_labels_have_the_observed_native_request_value(self):
        from ieee import SORTS,validate_request_state
        from types import SimpleNamespace
        for public,(_,native) in SORTS.items():
            body={} if native is None else {'sortType':native}
            validate_request_state(SimpleNamespace(request=SimpleNamespace(post_data_json=body)),{'sort':public,'access':'all'},1)

    def test_second_native_page_range_starts_at_twenty_five(self):
        from ieee import ieee_records
        raw=json.loads((ROOT/'tests/fixtures/ieee-search.json').read_text('utf-8'))
        raw['records']=[{**raw['records'][0],'articleNumber':str(1000+i)} for i in range(25)]
        raw.update(totalRecords=100,startRecord=25,endRecord=50,recordsPerPage=25,totalPages=4)
        rows,total,offset=ieee_records(raw)
        self.assertEqual((len(rows),total,offset),(25,100,25))
        raw.update(records=[],totalRecords=0,startRecord=0,endRecord=0,totalPages=0)
        self.assertEqual(ieee_records(raw),([],0,0))

    def test_command_query_must_be_nonempty_text(self):
        import tempfile
        from ieee import IEEE
        from scholarly import ArtifactStore,ServiceError
        with tempfile.TemporaryDirectory() as temp:
            adapter=IEEE(ArtifactStore(temp),None)
            for query in ('', '   ', None):
                with self.assertRaises(ServiceError) as error:adapter.search(query,options={},limit=1)
                self.assertEqual(error.exception.result['code'],'invalid_query')

    def test_failed_export_retains_selected_search_records(self):
        import tempfile
        from unittest.mock import Mock,patch
        from types import SimpleNamespace
        from ieee import IEEE
        from scholarly import ArtifactStore,ServiceError
        raw=json.loads((ROOT/'tests/fixtures/ieee-search.json').read_text('utf-8'))
        page=Mock();page.url='https://ieeexplore.ieee.org/search/searchresult.jsp'
        pending=SimpleNamespace(value=SimpleNamespace(status=200,json=lambda:raw,url='https://ieeexplore.ieee.org/rest/search',request=SimpleNamespace(post_data_json={})))
        manager=Mock();manager.__enter__=Mock(return_value=pending);manager.__exit__=Mock(return_value=False)
        page.expect_response.return_value=manager
        with tempfile.TemporaryDirectory() as temp:
            adapter=IEEE(ArtifactStore(temp),None)
            with patch.object(adapter,'page',return_value=page),patch('ieee.goto_source'),patch('ieee.dismiss_cookies'),patch.object(adapter,'citation',side_effect=ServiceError('export_format_mismatch','Wrong native format')):
                result=adapter.search('"Article Number":10488889',options={},limit=1,export='csv')
            self.assertEqual(result['status'],'partial')
            self.assertEqual(result['received'],1)
            self.assertEqual(result['export']['errors'][0]['code'],'export_format_mismatch')
            self.assertEqual(json.loads(adapter.store.read(result['records']['ref'])[1])[0]['articleNumber'],'10488889')

    def test_native_citation_formats_and_selected_count_are_checked(self):
        from ieee import validate_citation_file
        from scholarly import ServiceError
        selected=json.loads((ROOT/'tests/fixtures/ieee-search.json').read_text('utf-8'))['records']
        for format,suffix in [('bibtex','bib'),('ris','ris'),('csv','csv')]:
            data=(ROOT/'tests/fixtures'/('ieee.'+suffix)).read_bytes()
            validate_citation_file(data,format,selected)
            with self.assertRaises(ServiceError):validate_citation_file(data,format,selected*2)
            with self.assertRaises(ServiceError) as identity:
                validate_citation_file(data,format,[{**selected[0],'doi':'10.9999/wrong','articleNumber':'999','articleTitle':'Wrong'}])
            self.assertEqual(identity.exception.result['code'],'export_identity_mismatch')
        plain=b'D. Drusinsky, "From P Versus NP to Probabilistic and Zero Knowledge Proof Systems," doi: 10.1109/MC.2024.3358928.\nURL: https://ieeexplore.ieee.org/document/10488889\n'
        validate_citation_file(plain,'plain',selected)
        with self.assertRaises(ServiceError) as unrelated:validate_citation_file(b'Unrelated citation text','plain',selected)
        self.assertEqual(unrelated.exception.result['code'],'export_identity_mismatch')
        with self.assertRaises(ServiceError) as error:
            validate_citation_file(b'D. Drusinsky, "From P Versus NP", 2024.\nkeywords: {Privacy}\n','csv',selected)
        self.assertEqual(error.exception.result['code'],'export_format_mismatch')

    def test_doi_fetch_rejects_a_unique_search_row_for_another_doi(self):
        import tempfile
        from ieee import IEEE
        from scholarly import ArtifactStore,ServiceError
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);adapter=IEEE(store,None)
            row={'articleNumber':'123','doi':'10.9999/wrong','documentLink':'/document/123/','articleTitle':'Wrong'}
            records=store.put(json.dumps([row]),'application/json','ieee-xplore','https://ieeexplore.ieee.org/rest/search')
            def search(*args,**kwargs):
                adapter.known['123']=(row,'https://ieeexplore.ieee.org/search/searchresult.jsp')
                return {'status':'ok','total':1,'received':1,'records':records}
            adapter.search=search
            with self.assertRaises(ServiceError) as error:adapter.fetch('10.1109/MC.2024.3358928',parts=['metadata'])
        self.assertEqual(error.exception.result['code'],'identity_mismatch')

    def test_initial_non_json_403_is_classified_before_facet_parsing(self):
        import tempfile
        from types import SimpleNamespace
        from unittest.mock import Mock,patch
        from ieee import IEEE
        from scholarly import ArtifactStore,ServiceError
        page=Mock();page.url='https://ieeexplore.ieee.org/search/advanced/command'
        response=SimpleNamespace(status=403,json=lambda:(_ for _ in ()).throw(ValueError('private body')),
            request=SimpleNamespace(post_data_json={'queryText':'q'}),url='https://ieeexplore.ieee.org/rest/search')
        pending=SimpleNamespace(value=response);manager=Mock();manager.__enter__=Mock(return_value=pending);manager.__exit__=Mock(return_value=False);page.expect_response.return_value=manager
        with tempfile.TemporaryDirectory() as temp,patch.object(IEEE,'page',return_value=page),patch('ieee.goto_source'),patch('ieee.dismiss_cookies'):
            with self.assertRaises(ServiceError) as error:IEEE(ArtifactStore(temp),None).search('q',options={},limit=1)
        self.assertEqual(error.exception.result['code'],'access_restricted')

    def test_source_document_range_and_abstract_are_preserved(self):
        self.assertTrue((ROOT / "ieee.py").exists(), "IEEE adapter is absent")
        mod = importlib.import_module("ieee")
        raw = json.loads((ROOT / "tests/fixtures/ieee-search.json").read_text("utf-8"))
        rows, total, offset = mod.ieee_records(raw)
        self.assertEqual((len(rows), total, offset), (1, 1, 0))
        self.assertEqual(rows[0]["articleNumber"], "10488889")
        self.assertIn("zero knowledge", rows[0]["abstract"])


if __name__ == "__main__":
    unittest.main()

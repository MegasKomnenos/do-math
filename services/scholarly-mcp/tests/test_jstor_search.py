import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))

class JSTORSearchContract(unittest.TestCase):
    def test_contributor_facet_uses_the_native_field_and_identifier_prefix(self):
        from jstor_search import search
        from scholarly import ArtifactStore
        from types import SimpleNamespace
        from unittest.mock import patch
        import tempfile,base64
        raw=json.loads((ROOT/'tests/fixtures/jstor-image-contributor.json').read_text('utf-8'))
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);proof=store.put(json.dumps(raw),'application/json','jstor','https://www.jstor.org/search-results/grouped-search/')
            with patch('jstor_search.request_page',return_value=(raw,proof)) as request:
                result=search(SimpleNamespace(store=store,source='jstor'),'algebra',options={'content_types':['contributed_images'],'facets':{'cc_portal_id':['100689779']}},limit=2)
            self.assertEqual(result['total'],26)
            payload=request.call_args.args[1];field=next(f for f in payload['msFacetFields'] if f['field']=='cc_portal_id')
            self.assertEqual(base64.b64decode(field['efq'][0]).decode(),'cc_portal_id#100689779')

    def test_image_sort_and_native_resolution_filter_preserve_ui_request_meaning(self):
        from jstor_search import search
        from scholarly import ArtifactStore
        from types import SimpleNamespace
        from unittest.mock import patch
        import tempfile,base64
        for filename,options,sort,order,total in [
            ('jstor-image-resolution.json',{'content_types':['contributed_images'],'sort':'resolution','facets':{'cc_media_resolution':['cc_media_resolution:[9980929 TO *]']}},'cc_media_resolution','desc',47),
            ('jstor-image-title-desc.json',{'content_types':['contributed_images'],'sort':'title_desc'},'item_title_str','desc',242)]:
            raw=json.loads((ROOT/'tests/fixtures'/filename).read_text('utf-8'))
            with tempfile.TemporaryDirectory() as temp:
                store=ArtifactStore(temp);proof=store.put(json.dumps(raw),'application/json','jstor','https://www.jstor.org/search-results/grouped-search/')
                with patch('jstor_search.request_page',return_value=(raw,proof)) as request:
                    result=search(SimpleNamespace(store=store,source='jstor'),'algebra',options=options,limit=2)
                self.assertEqual((result['status'],result['total']),('ok',total))
                payload=request.call_args.args[1];self.assertEqual((payload['sort'],payload['sortOrder']),(sort,order))
                if 'facets' in options:
                    field=next(x for x in payload['msFacetFields'] if x['field']=='cc_media_resolution')
                    self.assertEqual(base64.b64decode(field['efq'][0]).decode(),options['facets']['cc_media_resolution'][0])

    def test_mixed_groups_expand_carousel_before_selecting_separate_windows(self):
        from jstor_search import search
        from scholarly import ArtifactStore
        from types import SimpleNamespace
        from unittest.mock import patch
        import tempfile
        pages=[json.loads((ROOT/('tests/fixtures/'+name)).read_text('utf-8')) for name in ('jstor-search-mixed.json','jstor-search-mixed-images-first.json','jstor-search-mixed-images-next.json','jstor-search-mixed-text-next.json')]
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);responses=[(raw,store.put(json.dumps(raw),'application/json','jstor','https://www.jstor.org/search-results/grouped-search/')) for raw in pages]
            with patch('jstor_search.request_page',side_effect=responses) as request:
                result=search(SimpleNamespace(store=store,source='jstor'),'algebra',options={'content_types':['journal','contributed_images']},start=24,limit=2)
            self.assertEqual((result['status'],result['received'],result['total']),('ok',4,178962))
            self.assertEqual([g['received'] for g in result['result_groups']],[2,2])
            self.assertEqual([g['total'] for g in result['result_groups']],[242,178720])
            self.assertEqual(request.call_args_list[1].args[1]['msFacetFields'],request.call_args_list[0].args[1]['msFacetFields'])
            self.assertNotIn('pageMark',request.call_args_list[1].args[1]['pageParams'])

    def test_bce_years_are_ordered_before_ce_without_year_zero(self):
        from jstor_search import search
        from scholarly import ArtifactStore,ServiceError
        from types import SimpleNamespace
        from unittest.mock import patch
        import tempfile
        raw=json.loads((ROOT/'tests/fixtures/jstor-search-zero.json').read_text('utf-8'))
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);proof=store.put(json.dumps(raw),'application/json','jstor','https://www.jstor.org/search-results/grouped-search/')
            adapter=SimpleNamespace(store=store,source='jstor')
            with patch('jstor_search.request_page',return_value=(raw,proof)) as request:
                result=search(adapter,raw['searchQuery'],options={'start_date':'-0500','end_date':'-0100'})
                self.assertEqual(result['status'],'not_found')
                self.assertEqual(request.call_args.args[1]['startDate'],'-500')
                for options in [{'start_date':'-0100','end_date':'-0500'},{'start_date':'0000'},{'start_date':'-0000'}]:
                    with self.assertRaises(ServiceError):search(adapter,raw['searchQuery'],options=options)

    def test_native_snippets_bind_by_stable_doi_not_response_order(self):
        from jstor_search import search_page,apply_snippets
        raw=json.loads((ROOT/'tests/fixtures/jstor-search-first.json').read_text('utf-8'))
        snippets=json.loads((ROOT/'tests/fixtures/jstor-snippets.json').read_text('utf-8'))
        rows=search_page(raw,'algebra',1)['rows']
        apply_snippets(rows,snippets,'algebra')
        self.assertEqual(rows[0]['native_type'],'journal')
        self.assertEqual(rows[0]['snippet']['status'],'available')
        self.assertEqual(rows[0]['snippet']['query'],'algebra')
        self.assertIn('algebra',rows[0]['snippet']['text'].lower())
        self.assertNotIn('<span',rows[0]['snippet']['text'])
        self.assertEqual(sum(r['snippet']['status']=='available' for r in rows),25)

    def test_snippet_foreign_and_duplicate_identity_are_rejected(self):
        from jstor_search import apply_snippets
        from scholarly import ServiceError
        for results in [[{'id':'10.2307/999','text':'wrong'}],[{'id':'10.2307/1','text':'one'}]*2]:
            with self.assertRaises(ServiceError):apply_snippets([{'id':'1'}],{'results':results,'errors':[]},'algebra')
        rows=[{'id':'1'}];apply_snippets(rows,{'results':[],'errors':[]},'algebra')
        self.assertEqual(rows[0]['snippet']['status'],'not_offered')

    def test_language_code_case_variants_match_the_native_selected_group(self):
        from jstor_search import search
        from scholarly import ArtifactStore
        from types import SimpleNamespace
        from unittest.mock import patch
        import tempfile
        raw=json.loads((ROOT/'tests/fixtures/jstor-search-filtered.json').read_text('utf-8'))
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);proof=store.put(json.dumps(raw),'application/json','jstor','https://www.jstor.org/search-results/grouped-search/')
            with patch('jstor_search.request_page',return_value=(raw,proof)):
                result=search(SimpleNamespace(store=store,source='jstor'),'algebra',options={'sort':'oldest','content_types':['journal'],'subjects':['mathematics-discipline'],'languages':['eng OR en OR EN']},limit=1)
            self.assertEqual((result['status'],result['received']),('ok',1))

    def test_ignored_facet_is_rejected_instead_of_returning_unfiltered_records(self):
        from jstor_search import search
        from scholarly import ArtifactStore,ServiceError
        from types import SimpleNamespace
        from unittest.mock import patch
        import tempfile
        raw=json.loads((ROOT/'tests/fixtures/jstor-search-first.json').read_text('utf-8'))
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);proof=store.put(json.dumps(raw),'application/json','jstor','https://www.jstor.org/search-results/grouped-search/')
            with patch('jstor_search.request_page',return_value=(raw,proof)),self.assertRaises(ServiceError) as error:
                search(SimpleNamespace(store=store,source='jstor'),'algebra',options={'content_types':['journal']},limit=1)
            self.assertEqual(error.exception.result['code'],'filter_mismatch')

    def test_partial_dates_use_the_whole_end_year_and_month(self):
        from jstor_search import search
        from scholarly import ArtifactStore,ServiceError
        from types import SimpleNamespace
        from unittest.mock import patch
        import tempfile
        raw=json.loads((ROOT/'tests/fixtures/jstor-search-zero.json').read_text('utf-8'))
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);proof=store.put(json.dumps(raw),'application/json','jstor','https://www.jstor.org/search-results/grouped-search/')
            adapter=SimpleNamespace(store=store,source='jstor')
            with patch('jstor_search.request_page',return_value=(raw,proof)):
                for start,end in [('2020/12','2020'),('2020/12/31','2020/12')]:
                    result=search(adapter,raw['searchQuery'],options={'start_date':start,'end_date':end})
                    self.assertEqual(result['status'],'not_found')
                with self.assertRaises(ServiceError):search(adapter,raw['searchQuery'],options={'start_date':'2021/02/29'})

    def test_page_failure_keeps_selected_records_and_passes_the_native_page_mark(self):
        from jstor_search import search
        from scholarly import ArtifactStore,ServiceError
        from types import SimpleNamespace
        from unittest.mock import patch
        import tempfile
        raw=json.loads((ROOT/'tests/fixtures/jstor-search-first.json').read_text('utf-8'))
        paging=raw['groupedResults']['column1']['results'][0]['paging']
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);proof=store.put(json.dumps(raw),'application/json','jstor','https://www.jstor.org/search-results/grouped-search/')
            with patch('jstor_search.request_page',side_effect=[(raw,proof),ServiceError('access_restricted','Restricted',status='restricted')]) as request:
                result=search(SimpleNamespace(store=store,source='jstor'),'algebra',options={},start=24,limit=2)
            self.assertEqual((result['status'],result['received']),('partial',1))
            self.assertEqual(result['errors'][0]['status'],'restricted')
            self.assertEqual(request.call_args_list[1].args[1]['pageParams'],{'groupEfq':paging['group_efq'],'pageMark':paging['next']})

    def test_native_result_group_and_page_counts_are_distinct(self):
        from jstor_search import search_page
        raw=json.loads((ROOT/'tests/fixtures/jstor-search-first.json').read_text('utf-8'))
        result=search_page(raw,'algebra',1)
        self.assertEqual((result['total'],result['source_total'],len(result['rows'])),(197779,198021,25))
        self.assertEqual(result['rows'][0]['id'],'24931626')
        self.assertEqual(result['rows'][4]['id'],'10.5951/mathteacher.108.9.0696')
        self.assertIn('September 1964',result['rows'][0]['citation_text'])
        self.assertNotIn('tokens',result['rows'][0])
        second=search_page(json.loads((ROOT/'tests/fixtures/jstor-search-second.json').read_text('utf-8')),'algebra',2)
        self.assertEqual(second['start'],25);self.assertEqual(second['rows'][0]['id'],'43303777')
        self.assertTrue(second['paging']['next'])

    def test_repeated_page_wrong_query_and_true_zero_are_distinguished(self):
        from jstor_search import search_page
        from scholarly import ServiceError
        raw=json.loads((ROOT/'tests/fixtures/jstor-search-first.json').read_text('utf-8'))
        for query,page,code in [('algebra',2,'range_mismatch'),('different',1,'query_mismatch')]:
            with self.assertRaises(ServiceError) as error:search_page(raw,query,page)
            self.assertEqual(error.exception.result['code'],code)
        empty=json.loads((ROOT/'tests/fixtures/jstor-search-zero.json').read_text('utf-8'))
        result=search_page(empty,empty['searchQuery'],1)
        self.assertEqual((result['total'],result['rows']),(0,[]))

    def test_non_2307_dois_and_community_records_are_valid_stable_targets(self):
        from jstor import stable_id
        self.assertEqual(stable_id('https://www.jstor.org/stable/10.5951/mathteacher.108.9.0696'),'10.5951/mathteacher.108.9.0696')
        self.assertEqual(stable_id('https://www.jstor.org/stable/community.39607963'),'community.39607963')

if __name__=='__main__':unittest.main()

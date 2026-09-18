import sys,unittest
from pathlib import Path
from waits import SOURCE_WAIT_MS

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


class SIAMContract(unittest.TestCase):
    def test_native_result_range_and_publication_identity_are_preserved(self):
        from siam import records
        raw=(ROOT/'tests/fixtures/siam-search.html').read_text('utf-8')
        rows,total,first=records(raw,'https://epubs.siam.org/action/doSearch')
        self.assertEqual((len(rows),total,first),(20,1320,0))
        self.assertEqual(rows[0]['doi'],'10.1137/1.9780898717976')
        self.assertEqual(rows[0]['title'],'Numerical Polynomial Algebra')
        self.assertEqual(rows[0]['authors'],['Hans J. Stetter'])
        self.assertEqual(rows[0]['year'],2004)
        self.assertEqual(rows[12]['title'],'Linear Algebra')

    def test_book_chapter_parent_and_row_local_abstract_remain_distinct(self):
        from siam import records
        raw=(ROOT/'tests/fixtures/siam-search.html').read_text('utf-8')
        rows,_,_=records(raw,'https://epubs.siam.org/action/doSearch')
        self.assertEqual(rows[0]['type'],'book')
        self.assertEqual(rows[0]['abstract'],'A book about polynomial computations.')
        self.assertIsNone(rows[1]['abstract'])
        self.assertEqual(rows[12]['type'],'chapter')
        self.assertEqual(rows[12]['doi'],'10.1137/1.9781611975468.ch8')
        self.assertEqual(rows[12]['publication'],'Computational Mathematics with SageMath')
        self.assertEqual(rows[12]['publication_url'],'https://epubs.siam.org/doi/book/10.1137/1.9781611975468')
        self.assertNotIn('and',rows[0]['authors'])

    def test_journal_parent_marks_article_instead_of_chapter(self):
        from siam import records
        raw=(ROOT/'tests/fixtures/siam-article.html').read_text('utf-8')
        rows,total,first=records(raw,'https://epubs.siam.org/action/doSearch')
        self.assertEqual((total,first),(1,0))
        self.assertEqual(rows[0]['type'],'article')
        self.assertEqual(rows[0]['publication'],'SIAM Journal on Optimization')
        self.assertEqual(rows[0]['publication_url'],'https://epubs.siam.org/journal/sjope8')

    def test_changed_row_identity_and_missing_result_are_rejected(self):
        from bs4 import BeautifulSoup
        from scholarly import ServiceError
        from siam import records
        raw=(ROOT/'tests/fixtures/siam-search.html').read_text('utf-8')
        soup=BeautifulSoup(raw,'html.parser')
        soup.select('li.search-item')[12].select_one('.search-item__title a')['href']='/doi/book/10.1137/1.9781611975468'
        with self.assertRaises(ServiceError) as identity:records(str(soup),'https://epubs.siam.org/action/doSearch')
        self.assertEqual(identity.exception.result['code'],'identity_mismatch')
        soup=BeautifulSoup(raw,'html.parser');soup.select_one('li.search-item').decompose()
        with self.assertRaises(ServiceError) as missing:records(str(soup),'https://epubs.siam.org/action/doSearch')
        self.assertEqual(missing.exception.result['code'],'range_mismatch')

    def test_native_query_fields_filters_sort_and_page_size_are_exact(self):
        from siam import search_params
        params=search_params('algebra',{
            'field':'Title','content_type':'article','sort':'date','page_size':50,
        })
        self.assertEqual(params,{
            'field1':'Title','text1':'algebra','ConceptID':['',''],'publication':'','Ppub':'','PubType':'103','sortBy':'EpubDate','pageSize':50,
        })
        self.assertEqual(search_params('algebra',{}),{'AllField':'algebra','pageSize':20})
        many=search_params('algebra',{'field':'Title','terms':[{'field':'Author','query':'Stetter'}]*51})
        self.assertEqual(many['field52'],'Contrib');self.assertEqual(many['text52'],'Stetter')

    def test_free_author_syntax_is_verbatim_and_has_free_semantics(self):
        from siam import author_query_semantics,search_params
        for query in ('Stetter','A_B','A_B Smith','A_B AND Smith','"A_B Smith"','A_B*'):
            with self.subTest(query=query):
                options={'field':'Author'}
                params=search_params(query,options)
                self.assertEqual((params['field1'],params['text1']),('Contrib',query))
                self.assertNotIn('ContribRaw',params)
                semantics=author_query_semantics(query,options,params)
                self.assertEqual(semantics['mode'],'free_author_expression')
                self.assertEqual(semantics['free_author_queries'],[query])
                self.assertEqual(semantics['exact_author_facets'],[])
                self.assertEqual(bool(semantics.get('warnings')),'_' in query)
                if '_' in query:self.assertEqual(semantics['warnings'][0]['code'],'underscore_free_author_analyzer')

    def test_explicit_exact_authors_are_independent_of_spelling_and_repeat_as_and(self):
        from siam import author_query_semantics,search_params
        labels=['Bank, Randolph E','Smith, R Kent']
        options={'field':'Title','authors_exact':labels}
        params=search_params('An Algebraic Multilevel Multigraph Algorithm',options)
        self.assertEqual(params['ContribRaw'],labels)
        semantics=author_query_semantics('An Algebraic Multilevel Multigraph Algorithm',options,params)
        self.assertEqual(semantics,{
            'mode':'exact_author_facets','free_author_queries':[],'exact_author_facets':labels,
            'combination':'AND',
            'note':'Explicit visible author labels are serialized as ContribRaw facets; multiple values are repeated and their observed combination is AND.',
        })

    def test_free_and_explicit_exact_authors_combine_without_rewriting(self):
        from siam import author_query_semantics,search_params
        free='"A_B Smith" OR Stetter*'
        labels=['Bank, Randolph E','Smith, R Kent']
        options={'field':'Author','terms':[{'field':'Author','query':'B_C AND Jones'}],'authors_exact':labels}
        params=search_params(free,options)
        self.assertEqual((params['field1'],params['text1'],params['field2'],params['text2']),
                         ('Contrib',free,'Contrib','B_C AND Jones'))
        self.assertEqual(params['ContribRaw'],labels)
        semantics=author_query_semantics(free,options,params)
        self.assertEqual(semantics['mode'],'free_author_expression_and_exact_facets')
        self.assertEqual(semantics['free_author_queries'],[free,'B_C AND Jones'])
        self.assertEqual(semantics['exact_author_facets'],labels)
        self.assertEqual(semantics['combination'],'AND')
        self.assertEqual(semantics['warnings'][0]['code'],'underscore_free_author_analyzer')

    def test_exact_author_option_rejects_malformed_lists_before_navigation(self):
        from siam import search_params
        from scholarly import ServiceError
        for value in (None,'Bank, Randolph E',[],[''],['  '],['Bank, Randolph E',3]):
            with self.subTest(value=value),self.assertRaises(ServiceError) as error:
                search_params('algebra',{'authors_exact':value})
            self.assertEqual(error.exception.result['code'],'invalid_options')

    def test_unconfirmed_boolean_rows_and_invalid_native_options_are_rejected(self):
        from siam import search_params
        from scholarly import ServiceError
        invalid=[
            {'operator':'AND'}, {'sort':'newest'}, {'sort':'oldest'},
            {'field':'Funder'}, {'content_type':'proceeding'}, {'page_size':10},
            {'terms':[{'field':'Funder','query':'NSF'}]}, {'topic':''}, {'publication':''},
            {'published_within':'decade'},
            {'published_within':'year','published_after':{'year':2024,'month':1},'published_before':{'year':2026,'month':9}},
            {'published_after':{'year':2024,'month':1}},
            {'published_after':{'year':2024,'month':13},'published_before':{'year':2026,'month':9}},
        ]
        for options in invalid:
            with self.subTest(options=options),self.assertRaises(ServiceError) as error:
                search_params('algebra',options)
            self.assertEqual(error.exception.result['code'],'invalid_options')

    def test_additional_term_and_custom_date_have_exact_native_fields(self):
        from siam import search_params
        params=search_params('algebra',{'field':'Title','terms':[{'field':'Author','query':'Stetter'}],
            'published_after':{'year':2024,'month':1},'published_before':{'year':2026,'month':9}})
        self.assertEqual({key:params[key] for key in ('field1','text1','field2','text2','AfterYear','AfterMonth','BeforeYear','BeforeMonth')},{
            'field1':'Title','text1':'algebra','field2':'Contrib','text2':'Stetter',
            'AfterYear':2024,'AfterMonth':1,'BeforeYear':2026,'BeforeMonth':9})

    def test_two_additional_terms_keep_ordered_native_field_numbers(self):
        from siam import search_params
        params=search_params('algebra',{'field':'Title','terms':[
            {'field':'Author','query':'Stetter'},{'field':'Anywhere','query':'numerical'}]})
        self.assertEqual({key:params[key] for key in ('field1','text1','field2','text2','field3','text3')},{
            'field1':'Title','text1':'algebra','field2':'Contrib','text2':'Stetter','field3':'AllField','text3':'numerical'})

    def test_dynamic_filters_start_from_fresh_advanced_form_and_keep_native_ids(self):
        import tempfile
        from types import SimpleNamespace
        from unittest.mock import Mock,patch
        from scholarly import ArtifactStore
        from publishers import PROFILES
        from siam import SIAM
        raw=(ROOT/'tests/fixtures/siam-search.html').read_text('utf-8')
        page=Mock();page.url='https://epubs.siam.org/';page.content.return_value=raw
        gateway=SimpleNamespace(public_page=Mock(return_value=page),context=Mock())
        native={'field1':['AllField'],'text1':['optimization'],'ConceptID':['',''],'publication':[''],
                'publication[]':['sjope8'],'Ppub':['','20250912-20260912'],'pageSize':['20']}
        requested=[]
        def navigate(page,url,*args,**kwargs):page.url=url;requested.append(url);return SimpleNamespace(status=200)
        with tempfile.TemporaryDirectory() as temp,patch('siam.goto_source',side_effect=navigate),patch('siam.configure_advanced',return_value=native) as configured:
            adapter=SIAM(ArtifactStore(temp),gateway,next(p for p in PROFILES if p.source=='siam'))
            result=adapter.search('optimization',options={'publication':'SIAM Journal on Optimization','published_within':'year'},limit=1)
        configured.assert_called_once_with(adapter,page,'optimization',unittest.mock.ANY)
        self.assertIn('publication%5B%5D=sjope8',requested[0])
        self.assertIn('Ppub=20250912-20260912',requested[0])
        self.assertEqual(result['received'],1)

    def test_dynamic_search_keeps_exact_author_facets_with_free_author_rows(self):
        import tempfile
        from types import SimpleNamespace
        from urllib.parse import parse_qs,urlsplit
        from unittest.mock import Mock,patch
        from scholarly import ArtifactStore
        from publishers import PROFILES
        from siam import SIAM
        raw=(ROOT/'tests/fixtures/siam-search.html').read_text('utf-8')
        page=Mock();page.url='https://epubs.siam.org/';page.content.return_value=raw
        gateway=SimpleNamespace(public_page=Mock(return_value=page),context=Mock())
        native={'field1':['Title'],'text1':['algebra'],'field2':['Contrib'],'text2':['A_B Smith'],
                'ConceptID':['',''],'publication':[''],'Ppub':[''],'pageSize':['20']}
        requested=[]
        def navigate(page,url,*args,**kwargs):page.url=url;requested.append(url);return SimpleNamespace(status=200)
        options={'field':'Title','terms':[{'field':'Author','query':'A_B Smith'}],
                 'authors_exact':['Bank, Randolph E','Smith, R Kent']}
        with tempfile.TemporaryDirectory() as temp,patch('siam.goto_source',side_effect=navigate),patch('siam.configure_advanced',return_value=native):
            result=SIAM(ArtifactStore(temp),gateway,next(p for p in PROFILES if p.source=='siam')).search('algebra',options=options,limit=1)
        observed=parse_qs(urlsplit(requested[0]).query,keep_blank_values=True)
        self.assertEqual(observed['text2'],['A_B Smith'])
        self.assertEqual(observed['ContribRaw'],['Bank, Randolph E','Smith, R Kent'])
        self.assertEqual(result['query_semantics']['mode'],'free_author_expression_and_exact_facets')
        self.assertEqual(result['query_semantics']['exact_author_facets'],options['authors_exact'])
        self.assertEqual(result['query_semantics']['warnings'][0]['code'],'underscore_free_author_analyzer')

    def test_autocomplete_requires_one_exact_label_and_preserves_candidates(self):
        from unittest.mock import Mock
        from scholarly import ServiceError
        from siam import _exact_suggestion
        candidates=[]
        for text in ('SIAM Journal on Computing','SIAM Journal on Optimization'):
            node=Mock();node.inner_text.return_value=text;node.get_attribute.return_value=None;candidates.append(node)
        nodes=Mock();nodes.count.return_value=2;nodes.nth.side_effect=candidates
        page=Mock();page.locator.return_value=nodes;field=Mock();field.get_attribute.return_value='publication'
        with self.assertRaises(ServiceError) as error:_exact_suggestion(page,field,'SIAM Journal')
        self.assertEqual(error.exception.result['status'],'selection_required')
        self.assertEqual(error.exception.result['candidates'],[
            {'label':'SIAM Journal on Computing','id':None},{'label':'SIAM Journal on Optimization','id':None}])
        for node in candidates:node.click.assert_not_called()

    def test_search_preserves_the_requested_window_and_mechanical_csv(self):
        import json,tempfile
        from types import SimpleNamespace
        from unittest.mock import Mock,patch
        from scholarly import ArtifactStore
        from publishers import PROFILES
        from siam import SIAM
        raw=(ROOT/'tests/fixtures/siam-search.html').read_text('utf-8')
        page=Mock();page.url='https://epubs.siam.org/';page.content.return_value=raw
        gateway=SimpleNamespace(public_page=Mock(return_value=page),context=Mock())
        def navigate(page,url,*args,**kwargs):
            page.url=url
            return SimpleNamespace(status=200)
        with tempfile.TemporaryDirectory() as temp,patch('siam.goto_source',side_effect=navigate) as opened:
            adapter=SIAM(ArtifactStore(temp),gateway,next(p for p in PROFILES if p.source=='siam'))
            result=adapter.search('algebra',options={'field':'Title'},start=3,limit=2,export='csv')
            rows=json.loads(adapter.store.read(result['records']['ref'])[1])
            csv=adapter.store.read(result['export']['ref'])[1].decode()
        self.assertEqual((result['status'],result['received'],result['total']),('ok',2,1320))
        self.assertEqual([row['doi'] for row in rows],['10.1137/1.9781611975147','10.1137/1.9781733146630'])
        self.assertIn('Linear Algebra and Matrices',csv)
        request=opened.call_args.args[1]
        self.assertIn('field1=Title',request)
        self.assertIn('text1=algebra',request)
        self.assertIn('startPage=0',request)
        self.assertIn('pageSize=20',request)

    def test_challenge_status_waits_for_results_or_returns_restricted(self):
        import tempfile
        from types import SimpleNamespace
        from unittest.mock import Mock,patch
        from scholarly import ArtifactStore,ServiceError
        from publishers import PROFILES
        from siam import SIAM
        raw=(ROOT/'tests/fixtures/siam-search.html').read_text('utf-8');challenge='<html><head><title>Just a moment</title></head><body></body></html>'
        page=Mock();page.url='https://epubs.siam.org/';page.content.side_effect=[challenge,raw]
        gateway=SimpleNamespace(public_page=Mock(return_value=page),context=Mock())
        def navigate(page,url,*args,**kwargs):page.url=url;return SimpleNamespace(status=403)
        with tempfile.TemporaryDirectory() as temp,patch('siam.goto_source',side_effect=navigate):
            result=SIAM(ArtifactStore(temp),gateway,next(p for p in PROFILES if p.source=='siam')).search('algebra',options={'field':'Title'},limit=1)
        self.assertEqual((result['status'],result['total'],result['received']),('ok',1320,1))
        page.wait_for_function.assert_called_once()

        page=Mock();page.url='https://epubs.siam.org/';page.content.return_value=challenge;page.wait_for_function.side_effect=TimeoutError
        gateway=SimpleNamespace(public_page=Mock(return_value=page),context=Mock())
        with tempfile.TemporaryDirectory() as temp,patch('siam.goto_source',side_effect=navigate),self.assertRaises(ServiceError) as error:
            SIAM(ArtifactStore(temp),gateway,next(p for p in PROFILES if p.source=='siam')).search('algebra',options={'field':'Title'},limit=1)
        self.assertEqual((error.exception.result['status'],error.exception.result['code']),('restricted','publisher_access_challenge'))

        page=Mock();page.url='https://epubs.siam.org/';page.content.return_value='<html><title>Server error</title></html>'
        gateway=SimpleNamespace(public_page=Mock(return_value=page),context=Mock())
        with tempfile.TemporaryDirectory() as temp,patch('siam.goto_source',side_effect=navigate),self.assertRaises(ServiceError) as error:
            SIAM(ArtifactStore(temp),gateway,next(p for p in PROFILES if p.source=='siam')).search('algebra',options={'field':'Title'},limit=1)
        self.assertEqual(error.exception.result['code'],'provider_error')

    def test_native_bibtex_selects_exact_doi_and_validates_the_file(self):
        import tempfile
        from types import SimpleNamespace
        from unittest.mock import Mock
        from scholarly import ArtifactStore
        from publishers import PROFILES
        from siam import SIAM,citation
        identifier='10.1137/1.9780898717976'
        box=Mock();box.input_value.return_value=identifier;box.is_checked.side_effect=[False,True]
        boxes=Mock();boxes.count.return_value=1;boxes.nth.return_value=box
        actions=Mock();action_locator=SimpleNamespace(first=actions);page=Mock()
        page.locator.side_effect=lambda selector: boxes if selector=='input[name=doi]' else action_locator
        native=(ROOT/'tests/fixtures/siam-selected.bib').read_bytes()
        def download(page,action,*args,**kwargs):
            action()
            return native,'null.bib','https://epubs.siam.org/action/downloadCitation'
        gateway=SimpleNamespace(native_download=Mock(side_effect=download))
        with tempfile.TemporaryDirectory() as temp:
            adapter=SIAM(ArtifactStore(temp),gateway,next(p for p in PROFILES if p.source=='siam'))
            artifact=citation(adapter,page,[identifier],'https://epubs.siam.org','bibtex')
            stored=adapter.store.read(artifact['ref'])[1]
        box.focus.assert_called_once_with();box.press.assert_called_once_with('Space')
        actions.select_option.assert_called_once_with(label='Download BibTeX')
        self.assertEqual(stored,native)
        self.assertEqual(artifact['requested_dois'],[identifier])

    def test_native_title_comparison_allows_source_space_before_punctuation(self):
        import tempfile
        from types import SimpleNamespace
        from unittest.mock import Mock
        from scholarly import ArtifactStore
        from publishers import PROFILES
        from siam import SIAM,citation
        identifier='10.1137/1.9781733146678'
        box=Mock();box.input_value.return_value=identifier;box.is_checked.return_value=True
        boxes=Mock();boxes.count.return_value=1;boxes.nth.return_value=box
        actions=Mock();page=Mock();page.locator.side_effect=lambda selector:boxes if selector=='input[name=doi]' else SimpleNamespace(first=actions)
        native=(ROOT/'tests/fixtures/siam-selected-page2.bib').read_bytes()
        def download(page,action,*args,**kwargs):action();return native,'null.bib','https://epubs.siam.org/action/downloadCitation'
        gateway=SimpleNamespace(native_download=Mock(side_effect=download))
        with tempfile.TemporaryDirectory() as temp:
            adapter=SIAM(ArtifactStore(temp),gateway,next(p for p in PROFILES if p.source=='siam'))
            artifact=citation(adapter,page,[identifier],'https://epubs.siam.org','bibtex',titles=['Introduction to Linear Algebra , Sixth Edition'])
        self.assertEqual(artifact['requested_dois'],[identifier])

    def test_native_citation_clears_stale_checked_dois_before_export(self):
        import tempfile
        from types import SimpleNamespace
        from unittest.mock import Mock
        from scholarly import ArtifactStore
        from publishers import PROFILES
        from siam import SIAM,citation
        identifier='10.1137/1.9780898717976'
        requested=Mock();requested.input_value.return_value=identifier;requested.is_checked.return_value=True
        stale=Mock();stale.input_value.return_value='10.1137/stale';stale.is_checked.side_effect=[True,False]
        boxes=Mock();boxes.count.return_value=2;boxes.nth.side_effect=[requested,stale]
        actions=Mock();page=Mock();page.locator.side_effect=lambda selector: boxes if selector=='input[name=doi]' else SimpleNamespace(first=actions)
        native=(ROOT/'tests/fixtures/siam-selected.bib').read_bytes()
        def download(page,action,*args,**kwargs):action();return native,'null.bib','https://epubs.siam.org/action/downloadCitation'
        gateway=SimpleNamespace(native_download=Mock(side_effect=download))
        with tempfile.TemporaryDirectory() as temp:
            adapter=SIAM(ArtifactStore(temp),gateway,next(p for p in PROFILES if p.source=='siam'))
            citation(adapter,page,[identifier],'https://epubs.siam.org','bibtex')
        requested.press.assert_not_called()
        stale.focus.assert_called_once_with();stale.press.assert_called_once_with('Space')

    def test_unconfirmed_export_format_and_changed_native_citation_are_rejected(self):
        import tempfile
        from types import SimpleNamespace
        from unittest.mock import Mock
        from scholarly import ArtifactStore,ServiceError
        from publishers import PROFILES
        from siam import SIAM,citation
        identifier='10.1137/1.9780898717976'
        box=Mock();box.input_value.return_value=identifier;box.is_checked.return_value=True
        boxes=Mock();boxes.count.return_value=1;boxes.nth.return_value=box
        page=Mock();page.locator.side_effect=lambda selector: boxes if selector=='input[name=doi]' else Mock()
        gateway=SimpleNamespace(native_download=Mock(return_value=((ROOT/'tests/fixtures/siam-selected.bib').read_bytes().replace(b'10.1137/1.9780898717976',b'10.1137/other'),'null.bib','https://epubs.siam.org/action/downloadCitation')))
        with tempfile.TemporaryDirectory() as temp:
            adapter=SIAM(ArtifactStore(temp),gateway,next(p for p in PROFILES if p.source=='siam'))
            with self.assertRaises(ServiceError) as changed:citation(adapter,page,[identifier],'https://epubs.siam.org','bibtex')
            self.assertEqual(changed.exception.result['code'],'identity_mismatch')
            with self.assertRaises(ServiceError) as other:citation(adapter,page,[identifier],'https://epubs.siam.org','mods')
            self.assertEqual(other.exception.result['code'],'invalid_export')

    def test_search_exports_only_the_requested_result_window(self):
        import tempfile
        from types import SimpleNamespace
        from unittest.mock import Mock,patch
        from scholarly import ArtifactStore
        from publishers import PROFILES
        from siam import SIAM
        raw=(ROOT/'tests/fixtures/siam-search.html').read_text('utf-8')
        page=Mock();page.url='https://epubs.siam.org/';page.content.return_value=raw
        gateway=SimpleNamespace(public_page=Mock(return_value=page),context=Mock())
        def navigate(page,url,*args,**kwargs):page.url=url;return SimpleNamespace(status=200)
        with tempfile.TemporaryDirectory() as temp,patch('siam.goto_source',side_effect=navigate),patch('siam.citation') as cite:
            adapter=SIAM(ArtifactStore(temp),gateway,next(p for p in PROFILES if p.source=='siam'))
            native=adapter.store.put((ROOT/'tests/fixtures/siam-selected.bib').read_bytes(),'application/x-bibtex','siam','https://epubs.siam.org/action/downloadCitation')
            cite.return_value=native
            result=adapter.search('algebra',options={'field':'Title'},start=1,limit=1,export='bibtex')
        selected=cite.call_args.args[2]
        self.assertEqual(selected,['10.1137/1.9780898719574'])
        self.assertEqual(result['export'],{'status':'available','artifacts':[native],'failures':[]})

    def test_native_export_failure_keeps_search_records_without_raw_error_text(self):
        import tempfile
        from types import SimpleNamespace
        from unittest.mock import Mock,patch
        from scholarly import ArtifactStore
        from publishers import PROFILES
        from siam import SIAM
        raw=(ROOT/'tests/fixtures/siam-search.html').read_text('utf-8')
        page=Mock();page.url='https://epubs.siam.org/';page.content.return_value=raw
        gateway=SimpleNamespace(public_page=Mock(return_value=page),context=Mock())
        def navigate(page,url,*args,**kwargs):page.url=url;return SimpleNamespace(status=200)
        with tempfile.TemporaryDirectory() as temp,patch('siam.goto_source',side_effect=navigate),patch('siam.citation',side_effect=TimeoutError('private detail')):
            adapter=SIAM(ArtifactStore(temp),gateway,next(p for p in PROFILES if p.source=='siam'))
            result=adapter.search('algebra',options={'field':'Title'},limit=1,export='bibtex')
        self.assertEqual((result['status'],result['received']),('partial',1))
        self.assertEqual([{k:v for k,v in item.items() if k!='where'} for item in result['export']['failures']],[{'status':'error','code':'citation_export_failed','error_type':'TimeoutError'}])
        self.assertEqual(result['export']['failures'][0]['where']['file'],'siam.py')
        self.assertNotIn('private detail',str(result))

    def test_cross_page_native_exports_remain_separate_source_files(self):
        import tempfile
        from types import SimpleNamespace
        from unittest.mock import Mock,patch
        from scholarly import ArtifactStore
        from publishers import PROFILES
        from siam import NATIVE_FORMATS,SIAM
        first=(ROOT/'tests/fixtures/siam-search.html').read_text('utf-8')
        second=(ROOT/'tests/fixtures/siam-search-page2.html').read_text('utf-8')
        for format,media in NATIVE_FORMATS.items():
            with self.subTest(format=format),tempfile.TemporaryDirectory() as temp:
                page=Mock();page.url='https://epubs.siam.org/';page.content.side_effect=lambda:second if 'startPage=1' in page.url else first
                gateway=SimpleNamespace(public_page=Mock(return_value=page),context=Mock())
                def navigate(page,url,*args,**kwargs):page.url=url;return SimpleNamespace(status=200)
                store=ArtifactStore(temp);adapter=SIAM(store,gateway,next(p for p in PROFILES if p.source=='siam'))
                artifacts=[store.put(b'page-'+str(i).encode(),media,'siam','https://epubs.siam.org/action/downloadCitation') for i in (1,2)]
                with patch('siam.goto_source',side_effect=navigate),patch('siam.citation',side_effect=artifacts) as cite:
                    result=adapter.search('algebra',options={'field':'Title'},start=19,limit=2,export=format)
                self.assertEqual(result['export']['artifacts'],artifacts)
                self.assertEqual([call.args[2] for call in cite.call_args_list],[
                    ['10.1137/1.9781611974096'],['10.1137/1.9781733146678']])

    def test_native_ris_modal_preserves_selected_doi_order(self):
        import tempfile
        from types import SimpleNamespace
        from unittest.mock import Mock
        from scholarly import ArtifactStore
        from publishers import PROFILES
        from siam import SIAM,citation
        identifiers=['10.1137/1.9780898719574','10.1137/1.9781611975468.ch8']
        controls=[]
        for identifier in identifiers:
            box=Mock();box.input_value.return_value=identifier;box.is_checked.return_value=True;controls.append(box)
        boxes=Mock();boxes.count.return_value=2;boxes.nth.side_effect=controls
        actions=Mock();radio=Mock();hidden=Mock();hidden.is_visible.return_value=False;button=Mock();button.is_visible.return_value=True;buttons=Mock();buttons.count.return_value=2;buttons.nth.side_effect=[hidden,button];page=Mock()
        action_locator=SimpleNamespace(first=actions)
        page.locator.side_effect=lambda selector: boxes if selector=='input[name=doi]' else radio if selector=='input[name=format][value=ris]' else action_locator
        page.get_by_role.return_value=buttons
        native=(ROOT/'tests/fixtures/siam-selected-batch.ris').read_bytes()
        def download(page,action,*args,**kwargs):action();return native,'siam_1.9780898719574.ris','https://epubs.siam.org/action/downloadCitation'
        gateway=SimpleNamespace(native_download=Mock(side_effect=download))
        with tempfile.TemporaryDirectory() as temp:
            adapter=SIAM(ArtifactStore(temp),gateway,next(p for p in PROFILES if p.source=='siam'))
            artifact=citation(adapter,page,identifiers,'https://epubs.siam.org','ris')
        actions.select_option.assert_called_once_with(label='Export Citations')
        radio.wait_for.assert_called_once_with(state='visible',timeout=SOURCE_WAIT_MS)
        radio.check.assert_called_once_with()
        button.click.assert_called_once_with()
        self.assertEqual(artifact['requested_dois'],identifiers)

    def test_native_endnote_and_medlars_keep_their_own_formats(self):
        import tempfile
        from types import SimpleNamespace
        from unittest.mock import Mock
        from scholarly import ArtifactStore
        from publishers import PROFILES
        from siam import SIAM,citation
        identifier='10.1137/1.9780898719574'
        expected={
            'endnote':('siam-selected.enw','application/x-endnote-refer'),
            'medlars':('siam-selected.medlars.txt','text/plain'),
        }
        for format,(fixture,media) in expected.items():
            with self.subTest(format=format),tempfile.TemporaryDirectory() as temp:
                box=Mock();box.input_value.return_value=identifier;box.is_checked.return_value=True
                boxes=Mock();boxes.count.return_value=1;boxes.nth.return_value=box
                actions=Mock();radio=Mock();button=Mock();button.is_visible.return_value=True;buttons=Mock();buttons.count.return_value=1;buttons.nth.return_value=button
                page=Mock();page.locator.side_effect=lambda selector: boxes if selector=='input[name=doi]' else radio if selector==f'input[name=format][value={format}]' else SimpleNamespace(first=actions);page.get_by_role.return_value=buttons
                native=(ROOT/'tests/fixtures'/fixture).read_bytes()
                def download(page,action,*args,**kwargs):action();return native,fixture,'https://epubs.siam.org/action/downloadCitation'
                gateway=SimpleNamespace(native_download=Mock(side_effect=download))
                adapter=SIAM(ArtifactStore(temp),gateway,next(p for p in PROFILES if p.source=='siam'))
                artifact=citation(adapter,page,[identifier],'https://epubs.siam.org',format)
                self.assertEqual(artifact['media_type'],media)
                radio.check.assert_called_once_with();button.click.assert_called_once_with()

    def test_medlars_title_is_line_scoped_and_depends_on_record_type(self):
        from siam import citation_identities
        book=(ROOT/'tests/fixtures/siam-selected.medlars.txt').read_bytes()
        article=(ROOT/'tests/fixtures/siam-selected-article.medlars.txt').read_bytes()
        self.assertEqual(citation_identities(book,'medlars'),(
            ['10.1137/1.9780898719574'],['Numerical Linear Algebra']))
        self.assertEqual(citation_identities(article,'medlars'),(
            ['10.1137/22M1522656'],['Computing Geometric Feature Sizes for Algebraic Manifolds']))
        self.assertEqual(citation_identities(book+b'\n'+article,'medlars'),(
            ['10.1137/1.9780898719574','10.1137/22M1522656'],
            ['Numerical Linear Algebra','Computing Geometric Feature Sizes for Algebraic Manifolds']))

    def test_refworks_wrapper_yields_ris_without_submitting_the_external_form(self):
        from siam import citation_identities,refworks_payload
        raw=(ROOT/'tests/fixtures/siam-refworks.html').read_bytes()
        data=refworks_payload(raw)
        identifiers,titles=citation_identities(data,'refworks')
        self.assertEqual(identifiers,['doi:10.1137/1.9780898719574'])
        self.assertEqual(titles,['Numerical Linear Algebra'])

    def test_refworks_citation_preserves_payload_without_external_submission(self):
        import tempfile
        from types import SimpleNamespace
        from unittest.mock import MagicMock,Mock
        from scholarly import ArtifactStore
        from publishers import PROFILES
        from siam import SIAM,citation
        identifier='10.1137/1.9780898719574'
        box=Mock();box.input_value.return_value=identifier;box.is_checked.return_value=True
        boxes=Mock();boxes.count.return_value=1;boxes.nth.return_value=box
        actions=Mock();radio=Mock();button=Mock();button.is_visible.return_value=True;buttons=Mock();buttons.count.return_value=1;buttons.nth.return_value=button
        page=Mock();page.locator.side_effect=lambda selector: boxes if selector=='input[name=doi]' else radio if selector=='input[name=format][value=refworks]' else SimpleNamespace(first=actions);page.get_by_role.return_value=buttons
        response=Mock();response.url='https://epubs.siam.org/action/downloadCitation';response.status=200;response.body.return_value=(ROOT/'tests/fixtures/siam-refworks.html').read_bytes()
        pending=SimpleNamespace(value=response);context=MagicMock();context.__enter__.return_value=pending;page.expect_response.return_value=context
        gateway=SimpleNamespace(native_download=Mock(side_effect=AssertionError('must not wait for a file')))
        with tempfile.TemporaryDirectory() as temp:
            adapter=SIAM(ArtifactStore(temp),gateway,next(p for p in PROFILES if p.source=='siam'))
            artifact=citation(adapter,page,[identifier],'https://epubs.siam.org','refworks',titles=['Numerical Linear Algebra'])
            data=adapter.store.read(artifact['ref'])[1]
        gateway.native_download.assert_not_called()
        button.click.assert_called_once_with()
        self.assertNotIn(b'api.refworks.proquest.com',data)
        self.assertIn(b'TI  - Numerical Linear Algebra',data)
        self.assertEqual((artifact['transport'],artifact['provider_format']),('refworks_import_wrapper','RIS Format'))

    def test_cross_page_window_follows_the_native_next_query(self):
        import json,tempfile
        from types import SimpleNamespace
        from unittest.mock import Mock,patch
        from scholarly import ArtifactStore
        from publishers import PROFILES
        from siam import SIAM
        first=(ROOT/'tests/fixtures/siam-search.html').read_text('utf-8')
        second=(ROOT/'tests/fixtures/siam-search-page2.html').read_text('utf-8')
        page=Mock();page.url='https://epubs.siam.org/'
        page.content.side_effect=lambda:second if 'startPage=1' in page.url else first
        gateway=SimpleNamespace(public_page=Mock(return_value=page),context=Mock())
        requested=[]
        def navigate(page,url,*args,**kwargs):page.url=url;requested.append(url);return SimpleNamespace(status=200)
        with tempfile.TemporaryDirectory() as temp,patch('siam.goto_source',side_effect=navigate):
            adapter=SIAM(ArtifactStore(temp),gateway,next(p for p in PROFILES if p.source=='siam'))
            result=adapter.search('algebra',options={'field':'Title'},start=19,limit=2)
            rows=json.loads(adapter.store.read(result['records']['ref'])[1])
        self.assertEqual([row['doi'] for row in rows],['10.1137/1.9781611974096','10.1137/1.9781733146678'])
        self.assertIn('ConceptID=&ConceptID=&publication=&Ppub=',requested[1])
        self.assertTrue(requested[1].endswith('pageSize=20&startPage=1'))

    def test_basic_allfield_zero_results_are_not_a_query_mismatch(self):
        import tempfile
        from types import SimpleNamespace
        from unittest.mock import Mock,patch
        from scholarly import ArtifactStore
        from publishers import PROFILES
        from siam import SIAM
        raw=(ROOT/'tests/fixtures/siam-empty.html').read_text('utf-8')
        page=Mock();page.url='https://epubs.siam.org/';page.content.return_value=raw
        gateway=SimpleNamespace(public_page=Mock(return_value=page),context=Mock())
        def navigate(page,url,*args,**kwargs):page.url=url;return SimpleNamespace(status=200)
        with tempfile.TemporaryDirectory() as temp,patch('siam.goto_source',side_effect=navigate):
            adapter=SIAM(ArtifactStore(temp),gateway,next(p for p in PROFILES if p.source=='siam'))
            result=adapter.search('codex-no-result-7f39b62e',options={})
        self.assertEqual((result['status'],result['received'],result['total']),('not_found',0,0))

    def test_exact_document_fetch_replaces_metadata_export_with_native_citation(self):
        import json,tempfile
        from types import SimpleNamespace
        from unittest.mock import Mock,patch
        from scholarly import ArtifactStore,encoded
        from publishers import PROFILES,Publisher
        from siam import SIAM
        identifier='10.1137/1.9780898717976'
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);page=Mock();page.is_closed.return_value=False;page.url='https://epubs.siam.org/action/doSearch'
            gateway=SimpleNamespace(pages={'siam':page})
            adapter=SIAM(store,gateway,next(p for p in PROFILES if p.source=='siam'))
            document_records=store.put(encoded([{'doi':identifier,'title':'Numerical Polynomial Algebra'}]),'application/json','siam','https://epubs.siam.org/doi/book/'+identifier)
            native=store.put((ROOT/'tests/fixtures/siam-selected.bib').read_bytes(),'application/x-bibtex','siam','https://epubs.siam.org/action/downloadCitation')
            ris=store.put((ROOT/'tests/fixtures/siam-selected-batch.ris').read_bytes(),'application/x-research-info-systems','siam','https://epubs.siam.org/action/downloadCitation')
            endnote=store.put((ROOT/'tests/fixtures/siam-selected.enw').read_bytes(),'application/x-endnote-refer','siam','https://epubs.siam.org/action/downloadCitation')
            medlars=store.put((ROOT/'tests/fixtures/siam-selected.medlars.txt').read_bytes(),'text/plain','siam','https://epubs.siam.org/action/downloadCitation')
            refworks=store.put((ROOT/'tests/fixtures/siam-selected-batch.ris').read_bytes(),'application/x-research-info-systems','siam','https://epubs.siam.org/action/downloadCitation',transport='refworks_import_wrapper')
            base={'status':'ok','source':'siam','records':document_records,'components':{
                'metadata':{'status':'available','artifact':document_records},
                'export':{'status':'available','artifact':document_records,'format':'source_metadata_json'},
            }}
            found=store.put(encoded([{'doi':identifier,'title':'Numerical Polynomial Algebra'}]),'application/json','siam','https://epubs.siam.org/action/doSearch')
            adapter.search=Mock(return_value={'status':'ok','received':1,'records':found})
            with patch.object(Publisher,'fetch',return_value=base),patch('siam.citation',side_effect=[native,ris,endnote,medlars,refworks]) as cite:
                result=adapter.fetch(identifier,parts=['metadata','export'])
        self.assertEqual(result['components']['metadata']['artifact'],document_records)
        self.assertEqual(result['components']['export'],{'status':'available','artifacts':[
            {'format':'bibtex','artifact':native},{'format':'ris','artifact':ris},
            {'format':'endnote','artifact':endnote},{'format':'medlars','artifact':medlars},
            {'format':'refworks','artifact':refworks}], 'errors':[], 'artifact':native})
        self.assertEqual(adapter.search.call_count,5)
        for call in adapter.search.call_args_list:self.assertEqual(call,unittest.mock.call(identifier,options={},start=0,limit=20))
        self.assertEqual(cite.call_args.args[2],[identifier])
        self.assertEqual([call.args[4] for call in cite.call_args_list],['bibtex','ris','endnote','medlars','refworks'])

    def test_name_fetch_keeps_the_inherited_selection_candidates(self):
        from types import SimpleNamespace
        from unittest.mock import Mock
        from publishers import PROFILES
        from siam import SIAM
        adapter=SIAM(None,SimpleNamespace(),next(p for p in PROFILES if p.source=='siam'))
        adapter.search=Mock(return_value={'status':'ok','received':2,'records':{'ref':'candidates'}})
        result=adapter.fetch('Numerical Linear Algebra',parts=['metadata'])
        self.assertEqual(result['status'],'selection_required')
        adapter.search.assert_called_once_with('Numerical Linear Algebra',options={},limit=20)


if __name__=='__main__':unittest.main()

import sys,unittest
from pathlib import Path
from unittest.mock import MagicMock
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from browser_adapters import ACM
from scholarly import ServiceError
from waits import SOURCE_WAIT_MS

class ACMAdvanced(unittest.TestCase):
    def test_boolean_expression_is_explicit_and_preserved_verbatim(self):
        expression='(Title:("finite fields") OR Abstract:(complexity\\ theory)) NOT Fulltext:(survey)'
        self.assertEqual(ACM.boolean_expression('',{'expression':expression}),expression)
        for query,options in (
            ('algebra',{'expression':'Title:(algebra) OR Abstract:(complexity)'}),
            ('',{'expression':'   '}),
            ('',{'expression':1}),
            ('',{'expression':'Title:(algebra)','field':'Title'}),
            ('',{'expression':'Title:(algebra)','fields':[]})):
            with self.subTest(query=query,options=options),self.assertRaises(ServiceError) as error:
                ACM.boolean_expression(query,options)
            self.assertEqual(error.exception.result['code'],'invalid_options')

    def test_edit_query_submits_the_exact_provider_expression(self):
        expression='(Title:("finite fields") OR Abstract:(complexity\\ theory)) NOT Fulltext:(survey)'
        page=MagicMock();edit=MagicMock();syntax=MagicMock();area=MagicMock();submit=MagicMock()
        page.locator.side_effect=lambda selector:{'#search__edit':edit,'#editableQuery':area,'#advanced-search-btn':submit}[selector]
        page.get_by_text.return_value=syntax;syntax.count.return_value=1;syntax.is_visible.return_value=True
        area.input_value.return_value=expression
        ACM.edit_boolean_query(page,expression)
        edit.wait_for.assert_called_once_with(state='visible',timeout=SOURCE_WAIT_MS)
        syntax.click.assert_called_once_with()
        area.fill.assert_called_once_with(expression)
        submit.click.assert_called_once_with()

    def test_facets_are_bound_to_observed_same_source_links(self):
        raw=(ROOT/'tests/fixtures/acm-facets.html').read_text('utf-8')
        candidates=ACM.facet_candidates(raw,'https://dl.acm.org/action/doSearch?AllField=algebra')
        self.assertEqual([(x['field'],x['value'],x['count']) for x in candidates],[
            ('SeriesKey','sigplan',1844),('ConceptID','118222',38034),('ContentItemType','research-article',31014),('content','media',None)])
        selected=ACM.select_facet(candidates,{'field':'ContentItemType','value':'research-article'})
        self.assertEqual((selected['label'],selected['value']),('Research Article','research-article'))
        with self.assertRaises(ServiceError) as error:ACM.select_facet(candidates,{'field':'SeriesKey','value':'invented'})
        self.assertEqual(error.exception.result['status'],'selection_required')

    def test_second_facet_link_must_preserve_the_first_selection(self):
        raw=(ROOT/'tests/fixtures/acm-facets-chained.html').read_text('utf-8')
        base='https://dl.acm.org/action/doSearch?AllField=algebra&SeriesKey=sigplan'
        candidates=ACM.facet_candidates(raw,base)
        selected=ACM.select_facet(candidates,{'field':'ContentItemType','value':'research-article','panel':'ContentType'})
        self.assertEqual((selected['panel'],selected['count']),('ContentType',698))

    def test_fulltext_contract_binds_doi_body_and_machine_tex(self):
        raw=(ROOT/'tests/fixtures/acm-fulltext.html').read_text('utf-8')
        parsed=ACM.fulltext_document(raw,'https://dl.acm.org/doi/full/10.1145/3831699','10.1145/3831699')
        self.assertEqual(parsed['title'],'A Survey on the Use of Machine Learning within Computer Algebra')
        self.assertEqual(parsed['document_doi'],'10.1145/3831699')
        self.assertEqual(parsed['body_scope'],'article including bodymatter and labeled backmatter')
        self.assertEqual(parsed['tex'],['x \\in R','f(x)=x^2'])
        self.assertIn('id="bodymatter"',parsed['html'])

    def test_abstract_only_or_wrong_doi_is_not_fulltext(self):
        raw=(ROOT/'tests/fixtures/acm-fulltext.html').read_text('utf-8')
        for changed in (raw.replace('id="bodymatter"','id="missing"'),raw.replace('10.1145/3831699','10.1145/wrong')):
            with self.assertRaises(ServiceError):ACM.fulltext_document(changed,'https://dl.acm.org/doi/full/10.1145/3831699','10.1145/3831699')

    def test_category_constraint_contract_rejects_general_boolean_fields(self):
        self.assertEqual(ACM.category_constraint({'field':'SeriesKey','operator':'Or','values':['Journal of the ACM','Communications of the ACM']}),
            {'field':'SeriesKey','operator':'Or','values':['Journal of the ACM','Communications of the ACM']})
        self.assertEqual(ACM.category_constraint({'field':'SeriesKey','operator':'Or','value':'Journal of the ACM'})['values'],['Journal of the ACM'])
        for invalid in ({'field':'Title','operator':'Or','value':'algebra'},{'field':'SeriesKey','operator':'Xor','value':'JACM'}):
            with self.assertRaises(ServiceError):ACM.category_constraint(invalid)

    def test_invalid_advanced_options_fail_before_opening_a_browser(self):
        adapter=ACM(None,None)
        invalid=(
            {'fields':'not-a-list'},
            {'sort':'invented'},
            {'from_month':1},
            {'from_year':2026,'to_year':2025},
            {'facet':{'field':'Unknown','value':'x'}},
            {'facets':[{'field':'SeriesKey','value':'cacm'},{'field':'SeriesKey','value':'cacm'}]},
        )
        for options in invalid:
            with self.subTest(options=options),self.assertRaises(ServiceError) as error:
                adapter.search('algebra',options=options,limit=1)
            self.assertEqual(error.exception.result['code'],'invalid_options')

    def test_native_citation_selection_removes_stale_checked_records(self):
        self.assertEqual(ACM.citation_selection(['10.1145/old','10.1145/keep'],['10.1145/keep','10.1145/new']),
            {'uncheck':['10.1145/old'],'check':['10.1145/new']})

    def test_extra_provider_citation_is_preserved_as_partial_scope(self):
        selected=[{'id':'10.1145/2499370.2462176','title':'Halide','url':'https://dl.acm.org/doi/10.1145/2499370.2462176'}]
        payload={'exportedDoiLength':2,'items':[
            {'10.1145/2499370.2462176':{'id':'10.1145/2499370.2462176','DOI':'10.1145/2499370.2462176','title':'Halide'}},
            {'10.1145/2491956.2462176':{'id':'10.1145/2491956.2462176','DOI':'10.1145/2491956.2462176','title':'Halide'}}]}
        parsed=[{'id':'10.1145/2499370.2462176','doi':'10.1145/2499370.2462176','title':'Halide','raw_text':'selected'},
                {'id':'10.1145/2491956.2462176','doi':'10.1145/2491956.2462176','title':'Halide','raw_text':'additional'}]
        matched=ACM.match_citation_records(selected,parsed,payload)
        self.assertEqual(matched['selected'][0]['raw_text'],'selected')
        self.assertEqual(matched['additional_identifiers'],['10.1145/2491956.2462176'])
        self.assertEqual(matched['selection_status'],'partial')

    def test_guide_key_without_bibtex_doi_uses_key_url_and_title_identity(self):
        identifier='10.5555/3814246.3814390';title='Fine-grained analysis and faster algorithms for iteratively solving linear systems'
        selected=[{'id':identifier,'title':title,'url':'https://dl.acm.org/doi/'+identifier}]
        payload={'exportedDoiLength':1,'items':[{identifier:{'id':identifier,'title':title}}]}
        parsed=[{'id':'3814246.3814390','title':title,'raw_text':'guide'}]
        self.assertEqual(ACM.match_citation_records(selected,parsed,payload)['selected'][0]['raw_text'],'guide')
        parsed[0]['title']='Another record'
        with self.assertRaises(ServiceError):ACM.match_citation_records(selected,parsed,payload)

    def test_component_failure_preserves_the_source_page(self):
        source={'ref':'scholarly://artifact/source'}
        failure=ACM.component_failure(TimeoutError(),source,'html_retrieval_failed')
        self.assertIn('where',failure);failure.pop('where')
        self.assertEqual(failure,{'status':'error','code':'html_retrieval_failed','error_type':'TimeoutError','artifact':source})

    def test_html_identity_failure_keeps_available_metadata(self):
        import tempfile
        from types import SimpleNamespace
        from unittest.mock import MagicMock,patch
        from scholarly import ArtifactStore
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);source=store.put('{"provider":true}','application/json','acm-dl','https://dl.acm.org/')
            citation=store.put('@misc{x,title={Title}}','application/x-bibtex','acm-dl','https://dl.acm.org/')
            adapter=ACM(store,SimpleNamespace(context=MagicMock()))
            adapter.known_records['10.1145/test']=({'title':'Title','raw_text':'@misc{x,title={Title}}'},citation,
                {'source_export':source,'selection_status':'exact'})
            page=MagicMock();page.url='https://dl.acm.org/doi/10.1145/test'
            link=MagicMock();link.get_attribute.return_value='/doi/full/10.1145/test'
            main=MagicMock();main.inner_html.return_value='<main><h1>Title</h1></main>'
            def locator(selector):
                if selector=='a[href*="/doi/full/"]':result=MagicMock();result.all.return_value=[link];return result
                if selector=='main':return main
                return MagicMock()
            page.locator.side_effect=locator;adapter.page=MagicMock(return_value=page)
            full=MagicMock();full.url='https://dl.acm.org/doi/full/10.1145/test';full.content.return_value='<html></html>'
            adapter.gateway.context.new_page.return_value=full
            with patch('browser_adapters.goto_source'),patch.object(adapter,'fulltext_document',side_effect=ServiceError('identity_mismatch','wrong')):
                result=adapter.fetch('10.1145/test',parts=['metadata','fulltext_html'])
        self.assertEqual(result['status'],'partial')
        self.assertEqual(result['components']['metadata']['status'],'available')
        self.assertEqual(result['components']['fulltext_html']['code'],'identity_mismatch')
        self.assertEqual(result['components']['fulltext_html']['artifact'],result['source_page'])

if __name__=='__main__':unittest.main()

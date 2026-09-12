import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from browser_adapters import MathSciNet
from scholarly import ServiceError

class MathSciNetAdvanced(unittest.TestCase):
    def test_current_publication_sorts_and_facet_groups_are_accepted(self):
        self.assertEqual(set(MathSciNet.sorts),{'newest','relevance','oldest','citations','author-count','paging'})
        self.assertEqual(set(MathSciNet.facet_groups),{'review_status','publication_type','authors','institutions',
            'primary_classifications','journals','publication_years'})
        settings=MathSciNet.advanced_options({'sort':'citations','facet_filters':{
            'publication_type':{'include':['Journal Article','Book'],'exclude':['Thesis']},
            'publication_years':{'include':['2025','2026']}},'facet_group':'journals','facet_query':'Algebra'})
        self.assertEqual(settings['sort'],'citations')
        self.assertEqual(settings['facet_filters'][0][0],'publication_type')
        self.assertEqual(settings['facet_preview'],('journals','Algebra'))

    def test_invalid_mathscinet_facet_contract_is_rejected(self):
        for options in ({'sort':'invented'},{'facet_filters':[]},{'facet_filters':{'authors':{'include':[]}}},
                        {'facet_filters':{'authors':{'include':['A'],'exclude':['a']}}},
                        {'facet_query':'x'},{'facet_group':'journals','facet_query':''}):
            with self.subTest(options=options),self.assertRaises(ServiceError):MathSciNet.advanced_options(options)

    def test_facet_candidates_are_bound_to_one_named_section(self):
        raw=(ROOT/'tests/fixtures/mathscinet-facets.html').read_text('utf-8')
        self.assertEqual(MathSciNet.facet_candidates(raw,'publication_type'),[
            {'label':'Journal Article','count':116354},{'label':'Book','count':3852}])
        self.assertEqual(MathSciNet.facet_candidates(raw,'publication_years'),[{'label':'2026','count':2189}])

    def test_search_request_keeps_sort_facets_and_range(self):
        url='https://mathscinet.ams.org/mathscinet/api/publications/search?query=ti%3Aalgebra&currentPage=2&pageSize=20&sort=citations&facets=NATIVE'
        MathSciNet.validate_search_request(url,'ti:algebra',2,20,'citations','NATIVE')
        with self.assertRaises(ServiceError):MathSciNet.validate_search_request(url,'ti:algebra',2,20,'newest','NATIVE')
        stale=url.replace('facets=NATIVE','facets=STALE')
        with self.assertRaises(ServiceError):MathSciNet.validate_search_request(stale,'ti:algebra',2,20,'citations','')

    def test_facet_query_delta_binds_group_mode_labels_and_multiplicity(self):
        selected=[{'label':'Journal Article','state':'include','native_term':'"Journal Article"','native_order':0},{'label':'Book','state':'include','native_term':'"Book"','native_order':1}]
        MathSciNet.validate_facet_query('ti:(algebra)','ti:(algebra) fpt:("Journal Article" OR "Book")','publication_type',selected)
        MathSciNet.validate_facet_query('ti:(algebra)','ti:(algebra) NOT frs:"Pending"','review_status',[{'label':'Pending','state':'exclude','native_term':'"Pending"'}])
        for wrong in ('ti:(algebra) y:("Journal Article" OR "Book")','ti:(algebra) fpt:"Journal Article"','changed fpt:("Journal Article" OR "Book")'):
            with self.subTest(wrong=wrong),self.assertRaises(ServiceError):MathSciNet.validate_facet_query('ti:(algebra)',wrong,'publication_type',selected)
        MathSciNet.validate_facet_query('q','q auid:("123" OR "456")','authors',[{'label':'A','state':'include','native_term':'"123"','native_order':0},{'label':'B','state':'include','native_term':'"456"','native_order':1}])
        MathSciNet.validate_facet_query('q','q auid:("456" OR "123")','authors',[{'label':'A','state':'include','native_term':'"123"','native_order':0},{'label':'B','state':'include','native_term':'"456"','native_order':1}])
        with self.assertRaises(ServiceError):MathSciNet.validate_facet_query('q','q auid:"999"','authors',[{'label':'Selected Author','state':'include','native_term':'"123"'}])
        with self.assertRaises(ServiceError):MathSciNet.validate_facet_query('q','q auid:"999"','authors',[{'label':'Selected Author','state':'include','native_term':'123'}])
        with self.assertRaises(ServiceError):MathSciNet.validate_facet_query('q','q finst:(v\'Selected Institution\' OR v\'Unrequested Institution\')','institutions',[{'label':'Selected Institution','state':'include','native_term':"v'Selected Institution'"}])
        with self.assertRaises(ServiceError):MathSciNet.validate_facet_query('q','q finst:v\'Selected Institution\'','institutions',[{'label':'Selected Institution','state':'include'}])

    def test_source_facet_payload_binds_labels_to_native_terms(self):
        self.assertEqual(MathSciNet.facet_search_routes,{
            'authors':('/mathscinet/api/publications/authors-facet','authorName'),
            'institutions':('/mathscinet/api/publications/institutions-facet','names'),
            'primary_classifications':('/mathscinet/api/publications/prim-class-facet','text'),
            'journals':('/mathscinet/api/publications/journals-facet','text')})
        payload={key:[] for key in MathSciNet.facet_payload_groups.values()}
        payload.update(authors=[{'id':'123','value':'Selected Author','total':4}],institutions=[{'id':'Selected Institution','value':'Selected Institution','total':3}],
                       primaryClassifications=[{'id':'68','value':'<b>Computer science</b>','total':2}],journals=[{'id':'456','value':'Selected Journal','total':1}],
                       reviewStatuses=[{'id':'pending','value':'Pending','total':5}],publicationTypes=[{'id':'article','value':'Journal Article','total':6}],publicationYears=[{'id':'2026','value':'2026','total':7}])
        values=MathSciNet.facet_payload_candidates(payload)
        self.assertEqual(values['authors'][0]['native_term'],'"123"')
        self.assertEqual(values['institutions'][0]['native_term'],"v'Selected Institution'")
        self.assertEqual(values['primary_classifications'][0]['label'],'68 - Computer science')
        self.assertEqual(values['primary_classifications'][0]['source_label'],'Computer science')
        outside=MathSciNet.facet_source_candidates('journals',[{'id':'789','value':'Outside Journal','total':2}])[0]
        MathSciNet.validate_facet_query('q','q ji:"789"','journals',[{**outside,'state':'include'}])

    def test_stale_facet_response_is_skipped_before_zero_result_short_circuit(self):
        import tempfile
        from types import SimpleNamespace
        from unittest.mock import MagicMock,patch
        from scholarly import ArtifactStore
        host='mathscinet.ams.org';query='NONE';facet_payload={key:[] for key in MathSciNet.facet_payload_groups.values()};zero={'total':0,'results':[]}
        stale=SimpleNamespace(url=f'https://{host}/mathscinet/api/publications/facets?query=OLD',status=200,json=lambda:facet_payload)
        current=SimpleNamespace(url=f'https://{host}/mathscinet/api/publications/facets?query={query}',status=200,json=lambda:facet_payload)
        search=SimpleNamespace(url=f'https://{host}/mathscinet/api/publications/search?query={query}&currentPage=1&pageSize=5&sort=newest',status=200,json=lambda:zero)
        self.assertFalse(MathSciNet.matches_facet_response(stale,host,query));self.assertTrue(MathSciNet.matches_facet_response(current,host,query))
        responses=[stale,current,search]
        def event(predicate,timeout=None):
            found=next(value for value in responses if predicate(value));result=MagicMock();result.__enter__.return_value=result;result.value=found;return result
        page=MagicMock();page.url=f'https://{host}/mathscinet/publications-search';page.expect_response.side_effect=event
        with tempfile.TemporaryDirectory() as temp:
            adapter=MathSciNet(ArtifactStore(temp),MagicMock());adapter.page=MagicMock(return_value=page)
            with patch('browser_adapters.goto_source'),patch.object(adapter,'apply_facets',side_effect=AssertionError('zero result must not open facets')):
                result=adapter.search(query,options={'facet_group':'journals'},limit=1)
        self.assertEqual((result['status'],result['total'],result['received']),('not_found',0,0))
        self.assertEqual(result['filter_state']['status'],'not_applicable');self.assertIsNone(result['facet_candidates'])

if __name__=='__main__':unittest.main()

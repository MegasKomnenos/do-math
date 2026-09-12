import json,sys,unittest,tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scholarly import ArtifactStore,ServiceError,bibliography
from browser_adapters import MathSciNet

class MathSciNetCitations(unittest.TestCase):
    def test_native_citation_control_binds_target_query_and_count(self):
        raw=(ROOT/'tests/fixtures/mathscinet-citation-control.html').read_text('utf-8')
        relation=MathSciNet.citation_control(raw,'https://mathscinet.ams.org/mathscinet/article?mr=2733384','2733384')
        self.assertEqual(relation,{'target':'MR2733384','query':'cp:2733384','total':3,'from_references':3,'from_reviews':0,
                                   'url':'https://mathscinet.ams.org/mathscinet/publications-search?query=cp%3A2733384'})

    def test_native_review_citation_control_is_separate_and_normalizes_leading_zero(self):
        raw=(ROOT/'tests/fixtures/mathscinet-citation-reviews-control.html').read_text('utf-8')
        base='https://mathscinet.ams.org/mathscinet/article?mr=0463157'
        references=MathSciNet.citation_control(raw,base,'0463157',basis='references')
        reviews=MathSciNet.citation_control(raw,base,'0463157',basis='reviews')
        self.assertEqual((references['query'],references['total']),('cp:463157',7912))
        self.assertEqual((reviews['query'],reviews['total']),('r:(MR0463157 OR "refcno 463157")',76))
        self.assertEqual((reviews['from_references'],reviews['from_reviews']),(7912,76))

    def test_record_identity_accepts_display_padding_but_rejects_another_mr(self):
        self.assertEqual(MathSciNet.record_identity('MR0463157','463157'),'0463157')
        with self.assertRaises(ServiceError) as error:MathSciNet.record_identity('MR0463157','123')
        self.assertEqual(error.exception.result['code'],'identity_mismatch')

    def test_structured_citing_search_preserves_target_direction_and_range(self):
        from unittest.mock import Mock
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);adapter=MathSciNet(store,None)
            proof=store.put('{"target":"MR2733384","query":"cp:2733384","total":3}','application/json','mathscinet','https://mathscinet.ams.org/mathscinet/article?mr=2733384')
            adapter.citation_relation=Mock(return_value={'target':'MR2733384','query':'cp:2733384','total':3,'from_references':3,'from_reviews':0,'evidence':proof})
            base={'status':'ok','source':'mathscinet','query':'cp:2733384','options':{'sort':'newest'},'start':1,'requested':2,'received':2,'total':3,
                  'has_more':False,'records':{'ref':'records'},'export':{'ref':'bib'},'evidence':[{'ref':'provider'}],'preview':[]}
            adapter.search=Mock(return_value=base)
            result=MathSciNet.citing(adapter,'MR2733384',sort='newest',start=1,limit=2,export='bibtex')
        adapter.search.assert_called_once_with('cp:2733384',options={'sort':'newest'},start=1,limit=2,cursor=None,export='bibtex')
        self.assertEqual((result['kind'],result['target'],result['native_query']),('citations','MR2733384','cp:2733384'))
        self.assertEqual(result['relation'],{'direction':'incoming','basis':'From References','total':3,'from_references':3,'from_reviews':0,'evidence':proof})
        self.assertEqual(result['evidence'][0],proof)

    def test_reference_control_preserves_source_and_searchable_subset_counts(self):
        raw=(ROOT/'tests/fixtures/mathscinet-citation-control.html').read_text('utf-8')
        relation=MathSciNet.reference_control(raw,'https://mathscinet.ams.org/mathscinet/article?mr=2733384','2733384')
        self.assertEqual(relation['target'],'MR2733384')
        self.assertEqual(relation['query'],'@|mr:3556292,3048194,3556292')
        self.assertEqual(relation['source_reference_items'],4)
        self.assertEqual(relation['searchable_mr_occurrences'],3)
        self.assertEqual(relation['searchable_unique_mrs'],2)
        self.assertEqual(relation['duplicate_mr_occurrences'],1)

    def test_structured_reference_search_labels_the_indexed_subset(self):
        from unittest.mock import Mock
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);adapter=MathSciNet(store,None)
            proof=store.put('{"target":"MR2733384"}','application/json','mathscinet','https://mathscinet.ams.org/')
            source_page=store.put('<ol><li>Unindexed</li></ol>','text/html','mathscinet','https://mathscinet.ams.org/')
            adapter.reference_relation=Mock(return_value={'target':'MR2733384','query':'@|mr:1,2,1','source_reference_items':4,
                'searchable_mr_occurrences':3,'searchable_unique_mrs':2,'duplicate_mr_occurrences':1,'evidence':proof,'source_page':source_page})
            adapter.search=Mock(return_value={'status':'ok','source':'mathscinet','query':'@|mr:1,2,1','options':{'sort':'newest'},
                'start':0,'requested':2,'received':2,'total':2,'evidence':[{'ref':'provider'}]})
            result=MathSciNet.references(adapter,'MR2733384',sort='newest',start=0,limit=2,export=None)
        self.assertEqual(result['kind'],'references')
        self.assertEqual(result['relation']['direction'],'outgoing')
        self.assertEqual(result['relation']['scope'],'MathSciNet-indexed MR subset from the source reference list')
        self.assertEqual(result['relation']['source_reference_items'],4)
        self.assertEqual(result['relation']['source_page'],source_page)
        self.assertIn(source_page,result['evidence'])
        adapter.search.assert_called_once_with('@|mr:1,2,1',options={'sort':'newest'},start=0,limit=2,cursor=None,export=None)

    def test_search_kind_citations_dispatches_instead_of_treating_target_as_text(self):
        from unittest.mock import Mock
        adapter=MathSciNet(None,None);adapter.citing=Mock(return_value={'status':'ok','kind':'citations'})
        result=adapter.search('MR2733384',options={'kind':'citations','sort':'oldest'},start=1,limit=2,export='endnote')
        self.assertEqual(result['kind'],'citations')
        adapter.citing.assert_called_once_with('MR2733384',sort='oldest',start=1,limit=2,cursor=None,export='endnote')

    def test_search_dispatches_review_derived_citations_as_a_distinct_basis(self):
        from unittest.mock import Mock
        adapter=MathSciNet(None,None);adapter.citing=Mock(return_value={'status':'ok','kind':'citations'})
        adapter.search('MR0463157',options={'kind':'citations','citation_basis':'reviews'},limit=1)
        adapter.citing.assert_called_once_with('MR0463157',sort='newest',start=0,limit=1,cursor=None,export=None,citation_basis='reviews')

    def test_review_control_count_and_unique_search_total_are_both_preserved(self):
        from unittest.mock import Mock
        adapter=MathSciNet(None,None)
        adapter.relationship_target=Mock(return_value={'mr':'0463157','requested_target':'MR0463157','lookup':None})
        adapter.citation_relation=Mock(return_value={'target':'MR0463157','query':'review-query','total':76,
            'from_references':7912,'from_reviews':76,'evidence':{'ref':'control'}})
        adapter.search=Mock(return_value={'status':'ok','total':72,'received':1,'evidence':[{'ref':'results'}]})
        result=adapter.citing('MR0463157',sort='newest',limit=1,citation_basis='reviews')
        self.assertEqual(result['total'],72)
        self.assertEqual(result['relation']['control_total'],76)
        self.assertEqual(result['relation']['result_total'],72)
        self.assertEqual(result['relation']['count_difference'],-4)

    def test_zero_review_citations_are_preserved_without_an_invented_query(self):
        from unittest.mock import Mock
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);adapter=MathSciNet(store,None)
            proof=store.put('{"from_reviews":0}','application/json','mathscinet','https://mathscinet.ams.org/mathscinet/article?mr=2733384')
            adapter.relationship_target=Mock(return_value={'mr':'2733384','requested_target':'MR2733384','lookup':None})
            adapter.citation_relation=Mock(return_value={'target':'MR2733384','query':None,'total':0,
                'from_references':3,'from_reviews':0,'evidence':proof})
            adapter.search=Mock()
            result=adapter.citing('MR2733384',sort='newest',citation_basis='reviews')
        self.assertEqual((result['status'],result['total'],result['native_query']),('not_found',0,None))
        self.assertEqual(result['relation']['basis'],'From Reviews')
        adapter.search.assert_not_called()

    def test_relationship_doi_is_followed_only_after_native_identity_match(self):
        from unittest.mock import Mock
        payload=json.loads((ROOT/'tests/fixtures/mathscinet-formats.json').read_text('utf-8'))
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);adapter=MathSciNet(store,None)
            records=store.put('[{"mrnumber":2733384}]','application/json','mathscinet','https://mathscinet.ams.org/')
            bib=store.put(payload[0]['bib'],'application/x-bibtex','mathscinet','https://mathscinet.ams.org/')
            adapter.search=Mock(return_value={'status':'ok','received':1,'total':1,'records':records,'export':bib})
            resolved=adapter.relationship_target('10.1016/j.jsc.2010.06.015')
            self.assertEqual(resolved['mr'],'2733384')
            self.assertEqual(resolved['requested_target'],'10.1016/j.jsc.2010.06.015')
            self.assertEqual(resolved['lookup']['records'],records)
            adapter.search.return_value={**adapter.search.return_value,'export':store.put(payload[0]['bib'].replace('10.1016/j.jsc.2010.06.015','10.1234/wrong'),'application/x-bibtex','mathscinet','https://mathscinet.ams.org/')}
            with self.assertRaises(ServiceError) as error:adapter.relationship_target('10.1016/j.jsc.2010.06.015')
            self.assertEqual(error.exception.result['code'],'selection_required')

    def test_search_page_rejects_changed_totals_short_pages_and_duplicate_identity(self):
        valid={'total':7,'results':[{'mrnumber':str(value)} for value in range(6,8)]}
        self.assertEqual(MathSciNet.validated_search_page(valid,2,5,7)[0],7)
        cases=(
            ({'total':8,'results':valid['results']},'search_range_changed'),
            ({'total':7,'results':valid['results'][:1]},'invalid_response'),
            ({'total':7,'results':[{'mrnumber':'6'},{'mrnumber':'6'}]},'invalid_response'),
            ({'total':7,'results':[{'mrnumber':'bad'},{'mrnumber':'7'}]},'invalid_response'),
        )
        for payload,code in cases:
            with self.subTest(code=code,payload=payload),self.assertRaises(ServiceError) as error:
                MathSciNet.validated_search_page(payload,2,5,7)
            self.assertEqual(error.exception.result['code'],code)

    def test_name_returns_candidates_without_requiring_an_mr_number(self):
        from unittest.mock import Mock
        adapter=MathSciNet(None,None)
        adapter.search=Mock(return_value={'status':'ok','received':1,'total':1,'records':{'ref':'candidate'}})
        result=adapter.fetch('P versus NP',parts=['metadata'])
        self.assertEqual(result['status'],'selection_required')
        self.assertEqual(adapter.search.call_args.args[0],'ti:("P versus NP")')

    def test_doi_lookup_checks_native_citation_before_following_the_mr_record(self):
        from unittest.mock import Mock
        payload=json.loads((ROOT/'tests/fixtures/mathscinet-formats.json').read_text('utf-8'))
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);adapter=MathSciNet(store,None)
            records=store.put('[{"mrnumber":2733384}]','application/json','mathscinet','https://mathscinet.ams.org/')
            bib=store.put(payload[0]['bib'],'application/x-bibtex','mathscinet','https://mathscinet.ams.org/')
            adapter.search=Mock(return_value={'status':'ok','received':1,'total':1,'records':records,'export':bib})
            adapter.fetch=Mock(return_value={'status':'ok','target':'MR2733384'})
            result=MathSciNet.fetch(adapter,'10.1016/j.jsc.2010.06.015',parts=['metadata'])
            self.assertEqual(result['status'],'ok')
            adapter.fetch.assert_called_once_with('MR2733384',parts=['metadata'])
            adapter.fetch.reset_mock()
            mismatch=MathSciNet.fetch(adapter,'10.1234/different',parts=['metadata'])
            self.assertEqual(mismatch['status'],'selection_required')
            adapter.fetch.assert_not_called()

    def test_invalid_selected_id_is_not_silently_dropped(self):
        payload=(ROOT/'tests/fixtures/mathscinet-formats.json').read_bytes()
        with tempfile.TemporaryDirectory() as temp:
            adapter=MathSciNet(ArtifactStore(temp),SimpleNamespace(context=None))
            page=SimpleNamespace(url='https://mathscinet-ams-org.libproxy.knu.ac.kr/mathscinet/article?mr=2733384')
            with patch.object(adapter,'page',return_value=page),patch('browser_adapters.browser_download',return_value=(payload,'application/json',page.url)) as download:
                with self.assertRaises(ServiceError):adapter.citation_exports(['2733384','invalid'],['bibtex'])
                download.assert_not_called()

    def test_source_formatted_fields_work_without_the_result_list(self):
        payload=(ROOT/'tests/fixtures/mathscinet-formats.json').read_bytes()
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);adapter=MathSciNet(store,SimpleNamespace(context=None))
            page=SimpleNamespace(url='https://mathscinet-ams-org.libproxy.knu.ac.kr/mathscinet/article?mr=2733384')
            with patch.object(adapter,'page',return_value=page),patch('browser_adapters.browser_download',return_value=(payload,'application/json',page.url)):
                result=adapter.citation_exports(['2733384'],['bibtex','endnote','amsref','tex'])
            self.assertEqual([x['format'] for x in result],['bibtex','endnote','amsref','tex'])
            for item in result:
                self.assertEqual(item['artifact']['mr_order'],['2733384'])
                self.assertGreater(item['artifact']['bytes'],0)
            bib=bibliography(store.read(result[0]['artifact']['ref'])[1],'application/x-bibtex')
            self.assertEqual(bib[0]['id'],'MR2733384')

    def test_wrong_or_duplicate_publication_ids_are_rejected(self):
        payload=json.loads((ROOT/'tests/fixtures/mathscinet-formats.json').read_text('utf-8'))
        with tempfile.TemporaryDirectory() as temp:
            adapter=MathSciNet(ArtifactStore(temp),SimpleNamespace(context=None))
            page=SimpleNamespace(url='https://mathscinet-ams-org.libproxy.knu.ac.kr/mathscinet/article?mr=2733384')
            for value in ([{**payload[0],'paperId':'1'}],payload+payload):
                with patch.object(adapter,'page',return_value=page),patch('browser_adapters.browser_download',return_value=(json.dumps(value).encode(),'application/json',page.url)):
                    with self.assertRaises(ServiceError) as error:adapter.citation_exports(['2733384'],['bibtex'])
                    self.assertEqual(error.exception.result['code'],'citation_identity_mismatch')

    def test_formatted_bibtex_must_match_its_publication_wrapper(self):
        payload=json.loads((ROOT/'tests/fixtures/mathscinet-formats.json').read_text('utf-8'))
        payload[0]['bib']=payload[0]['bib'].replace('2733384','999999')
        with tempfile.TemporaryDirectory() as temp:
            adapter=MathSciNet(ArtifactStore(temp),SimpleNamespace(context=None))
            page=SimpleNamespace(url='https://mathscinet-ams-org.libproxy.knu.ac.kr/')
            with patch.object(adapter,'page',return_value=page),patch('browser_adapters.browser_download',return_value=(json.dumps(payload).encode(),'application/json',page.url)):
                with self.assertRaises(ServiceError) as error:adapter.citation_exports(['2733384'],['bibtex'])
                self.assertEqual(error.exception.result['code'],'citation_identity_mismatch')

if __name__=='__main__':unittest.main()

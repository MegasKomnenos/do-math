import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))

class APSSearchContract(unittest.TestCase):
    def test_search_reads_server_mathml_instead_of_rendered_placeholders(self):
        from aps_institutional import search
        from scholarly import ArtifactStore
        from bs4 import BeautifulSoup
        from types import SimpleNamespace
        from unittest.mock import Mock
        import tempfile
        rendered=(ROOT/'tests/fixtures/aps-search.html').read_text('utf-8')
        soup=BeautifulSoup(rendered,'html.parser')
        original=BeautifulSoup((ROOT/'tests/fixtures/aps-abstract-mathml.html').read_text('utf-8'),'html.parser')
        soup.select_one('#result-abstract-1').replace_with(original.select_one('.abstract-summary'))
        raw=str(soup);callbacks=[]
        context=SimpleNamespace(on=lambda event,callback:callbacks.append(callback),remove_listener=Mock())
        page=SimpleNamespace(url='https://journals.aps.org/search',content=lambda:rendered,wait_for_function=Mock())
        response=SimpleNamespace(url=page.url,status=200,headers={'content-type':'text/html'},text=lambda:raw)
        def document(target):callbacks[0](response);return page
        with tempfile.TemporaryDirectory() as temp:
            adapter=SimpleNamespace(store=ArtifactStore(temp),gateway=SimpleNamespace(start=Mock(),pages={},context=context),source='aps-institutional',
                                    profile=SimpleNamespace(hosts=('journals.aps.org',)),document=document)
            result=search(adapter,'algebra',options={},limit=2)
            rows=json.loads(adapter.store.read(result['records']['ref'])[1])
            self.assertEqual(len(BeautifulSoup(rows[1]['abstract_html'],'html.parser').select('math')),2)
            self.assertNotIn('mjx-lazy',rows[1]['abstract_html'])

    def test_continuation_reuses_received_page_and_original_evidence(self):
        from aps_institutional import search
        from scholarly import ArtifactStore
        from types import SimpleNamespace
        from unittest.mock import Mock
        import tempfile
        raw=(ROOT/'tests/fixtures/aps-search.html').read_text('utf-8')
        clauses=[{'field':'all','value':'algebra','operator':'AND'}]
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);page=SimpleNamespace(url='https://journals.aps.org/search',is_closed=lambda:False)
            proof=store.put(raw,'text/html','aps-institutional',page.url)
            facets=store.put('{}','application/json','aps-institutional',page.url)
            gateway=SimpleNamespace(start=Mock(),context=Mock(),pages={'aps-institutional':page})
            adapter=SimpleNamespace(store=store,gateway=gateway,source='aps-institutional',profile=SimpleNamespace(hosts=('journals.aps.org',)),
                _aps_last={'params':{'clauses':json.dumps(clauses,separators=(',',':')),'sort':'relevance'},'raw':raw,'url':page.url,'start':0,'proof':proof,'facets':facets})
            result=search(adapter,'algebra',options={},start=1,limit=1)
            self.assertEqual(result['status'],'ok');self.assertEqual(result['received'],1)
            self.assertEqual(result['evidence'],[proof])
            self.assertEqual(result['preview'][0]['title'],'Algebra of causality')

    def test_native_results_keep_titles_dois_abstracts_and_declared_range(self):
        from aps_institutional import search_records
        raw=(ROOT/'tests/fixtures/aps-search.html').read_text('utf-8')
        found=search_records(raw,'https://journals.aps.org/search',expected_clauses=[{'field':'all','value':'algebra','operator':'AND'}])
        self.assertEqual((found['total'],found['start'],len(found['rows'])),(37987,0,20))
        self.assertEqual(found['rows'][0]['doi'],'10.1103/RevModPhys.39.259')
        self.assertEqual(found['rows'][0]['title'],'Group Algebra, Convolution Algebra, and Applications to Quantum Mechanics')
        self.assertIn('Schur',found['rows'][0]['abstract'])
        self.assertIn('PER-OLOV',found['rows'][0]['listing'])
        self.assertEqual(found['rows'][0]['authors_display'],'PER-OLOV LÖWDIN')
        self.assertEqual(found['rows'][0]['publication_date_display'],'1 April, 1967')

    def test_missing_card_and_changed_query_are_rejected(self):
        from aps_institutional import search_records
        from scholarly import ServiceError
        from bs4 import BeautifulSoup
        raw=(ROOT/'tests/fixtures/aps-search.html').read_text('utf-8')
        soup=BeautifulSoup(raw,'html.parser');soup.select_one('#search-main h3 a').find_parent('div',class_='border-b').decompose()
        with self.assertRaises(ServiceError) as error:search_records(str(soup),'https://journals.aps.org/search')
        self.assertEqual(error.exception.result['code'],'range_mismatch')
        with self.assertRaises(ServiceError) as error:search_records(raw,'https://journals.aps.org/search',expected_clauses=[{'field':'title','value':'algebra','operator':'AND'}])
        self.assertEqual(error.exception.result['code'],'query_mismatch')

if __name__=='__main__':unittest.main()

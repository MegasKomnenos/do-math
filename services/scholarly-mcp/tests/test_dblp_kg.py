import json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scholarly import ServiceError,ArtifactStore,extract_artifact

class DBLPKGContract(unittest.TestCase):
    def test_doi_input_matches_the_uppercase_doi_in_actual_dblp_statements(self):
        import httpx
        from dblp_kg import DBLPKG
        raw=json.loads((ROOT/'tests/fixtures/dblp-kg-natural-proofs.json').read_text('utf-8'))
        with tempfile.TemporaryDirectory() as temp:
            adapter=DBLPKG(ArtifactStore(temp),httpx.Client(transport=httpx.MockTransport(lambda request:httpx.Response(200,json=raw))))
            result=adapter.fetch('10.1006/jcss.1997.1494',parts=['metadata'])
        self.assertEqual(result['status'],'ok')
        self.assertEqual(result['statement_count'],32)

    def test_absent_document_stays_not_found_with_default_content_parts(self):
        import httpx
        from dblp_kg import DBLPKG
        raw={'head':{'vars':['publ','predicate','object']},'results':{'bindings':[]}}
        with tempfile.TemporaryDirectory() as temp:
            adapter=DBLPKG(ArtifactStore(temp),httpx.Client(transport=httpx.MockTransport(lambda request:httpx.Response(200,json=raw))))
            result=adapter.fetch('10.1234/absent',parts=['metadata','abstract','fulltext'])
        self.assertEqual(result['status'],'not_found')

    def test_doi_suffix_is_not_treated_as_a_record_export_extension(self):
        import httpx
        from dblp_kg import DBLPKG
        calls=[]
        def response(request):
            calls.append(request.url.params['query'])
            return httpx.Response(200,json={'head':{'vars':['publ','predicate','object']},'results':{'bindings':[]}})
        with tempfile.TemporaryDirectory() as temp:
            adapter=DBLPKG(ArtifactStore(temp),httpx.Client(transport=httpx.MockTransport(response)))
            result=adapter.fetch('10.1234/a.xml',parts=['metadata'])
        self.assertEqual(result['status'],'not_found')
        self.assertIn('https://doi.org/10.1234/a.xml',calls[0])

    def test_invalid_native_export_remains_available_as_evidence(self):
        import httpx
        from dblp_kg import DBLPKG
        raw=json.loads((ROOT/'tests/fixtures/dblp-kg-search.json').read_text('utf-8'))
        def response(request):
            if request.headers['accept']=='application/sparql-results+json':return httpx.Response(200,json=raw)
            return httpx.Response(200,text='publ,title\n',headers={'content-type':'text/csv'})
        with tempfile.TemporaryDirectory() as temp:
            adapter=DBLPKG(ArtifactStore(temp),httpx.Client(transport=httpx.MockTransport(response)))
            adapter.min_interval=0
            result=adapter.search('SELECT ?publ ?title WHERE {?publ ?p ?title} ORDER BY ?publ',options={},limit=2,export='csv')
            self.assertEqual(result['status'],'partial')
            self.assertEqual(result['received'],2)
            self.assertIn('source_export',result['export'])

    def test_read_query_validation_uses_syntax_and_preserves_nested_limits(self):
        from dblp_kg import bounded_query
        q='SELECT ?s WHERE { BIND("SERVICE FROM LIMIT" AS ?s) {SELECT ?x WHERE {?x ?p ?o} LIMIT 3} } ORDER BY ?s # trailing comment'
        self.assertEqual(bounded_query(q,1,2),q+'\nLIMIT 2 OFFSET 1')
        for q in ['SELECT * WHERE { SERVICE <https://example.org/> {?s ?p ?o} }',
                  'SELECT * FROM <https://example.org/> WHERE {?s ?p ?o}',
                  'SELECT * WHERE {?s ?p ?o} LIMIT 1',
                  'INSERT DATA {<urn:a> <urn:b> <urn:c>}',
                  'ASK {?s ?p ?o}']:
            with self.assertRaises(ServiceError):bounded_query(q,0,2)

    def test_binding_types_and_missing_values_are_preserved(self):
        from dblp_kg import bindings
        raw={'head':{'vars':['name','year']},'results':{'bindings':[{'name':{'type':'literal','value':'A','xml:lang':'en'}}]},'meta':{'result-size-total':1}}
        self.assertEqual(bindings(raw),(['name','year'],raw['results']['bindings']))
        self.assertNotIn('year',bindings(raw)[1][0])
        with self.assertRaises(ServiceError):bindings({'head':{'vars':['x']},'results':{'bindings':[{'x':{'type':'literal','value':1}}]}})

    def test_native_tsv_year_loses_its_json_datatype_and_is_reported(self):
        from dblp_kg import validate_table
        raw=json.loads((ROOT/'tests/fixtures/dblp-kg-year.json').read_text('utf-8'))
        with self.assertRaises(ServiceError) as caught:
            validate_table((ROOT/'tests/fixtures/dblp-kg-year.tsv').read_bytes(),'tsv',raw['head']['vars'],raw['results']['bindings'])
        self.assertEqual(caught.exception.result['code'],'export_term_mismatch')

    def test_native_csv_and_tsv_are_same_window_and_terms_remain_quoted(self):
        from dblp_kg import validate_table
        raw=json.loads((ROOT/'tests/fixtures/dblp-kg-search.json').read_text('utf-8'))
        rows=raw['results']['bindings'];variables=raw['head']['vars']
        for format in ('csv','tsv'):
            data=(ROOT/f'tests/fixtures/dblp-kg-search.{format}').read_bytes()
            validate_table(data,format,variables,rows)
            with self.assertRaises(ServiceError):validate_table(data,format,variables,rows[:1])
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp)
            artifact=store.put((ROOT/'tests/fixtures/dblp-kg-search.tsv').read_bytes(),'text/tab-separated-values','dblp-kg','https://sparql.dblp.org/sparql')
            result=extract_artifact(store,artifact['ref'],start=1,count=1)
            self.assertEqual(result['unit'],'lines')
            self.assertIn('"Learning Algorithms from Natural Proofs."',result['items'][0])

if __name__=='__main__':unittest.main()

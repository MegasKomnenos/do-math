import json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scholarly import ServiceError,ArtifactStore,extract_artifact

class DBLPKGContract(unittest.TestCase):
    def test_tsv_rejects_equal_values_with_different_lexical_forms_or_datatypes(self):
        from dblp_kg import validate_table
        xsd='http://www.w3.org/2001/XMLSchema#'
        for value,kind,cell in [('01','integer','"1"^^<'+xsd+'integer>'),
                                ('1','integer','"1"^^<'+xsd+'decimal>'),
                                ('1','boolean','true')]:
            with self.subTest(value=value,kind=kind,cell=cell):
                with self.assertRaises(ServiceError) as caught:
                    validate_table(('?x\n'+cell+'\n').encode(),'tsv',['x'],[{'x':{'type':'literal','value':value,'datatype':xsd+kind}}])
                self.assertEqual(caught.exception.result['code'],'export_term_mismatch')

    def test_tsv_requires_a_complete_term_without_trailing_garbage(self):
        from dblp_kg import validate_table
        for cell in ['"x"garbage', ' "x"', '"x" ']:
            with self.subTest(cell=cell), self.assertRaises(ServiceError):
                validate_table(('?x\n'+cell+'\n').encode(),'tsv',['x'],[{'x':{'type':'literal','value':'x'}}])

    def test_tsv_preserves_numeric_lexical_forms_and_accepts_rdf_string_aliases(self):
        from dblp_kg import validate_table,exact_tsv
        xsd='http://www.w3.org/2001/XMLSchema#'
        for value,kind in [('01','integer'),('+01','integer'),('-01','integer'),('1.00','decimal'),('-.5','decimal'),('-0.5','decimal'),('1e02','double'),('true','boolean'),('false','boolean')]:
            rows=[{'x':{'type':'literal','value':value,'datatype':xsd+kind}}]
            validate_table(exact_tsv(['x'],rows),'tsv',['x'],rows)
            validate_table(('?x\n'+value+'\n').encode(),'tsv',['x'],rows)
        validate_table(b'?x\n"x"\n','tsv',['x'],[{'x':{'type':'literal','value':'x','datatype':xsd+'string'}}])
        validate_table(b'?x\n"x"@en\n','tsv',['x'],[{'x':{'type':'literal','value':'x','xml:lang':'EN'}}])
        self.assertEqual(exact_tsv(['x'],[{'x':{'type':'literal','value':'x','xml:lang':'EN'}}]),b'?x\n"x"@EN\n')

    def test_tsv_unicode_escapes_do_not_change_delimiters_or_escape_twice(self):
        from dblp_kg import tsv_term,exact_tsv,validate_table
        from rdflib import URIRef
        for cell,expected in [(r'"\u00E9"','é'),(r'"\u0022"','"'),(r'"\\u0041"',r'\u0041'),(r'"\U0001F600"','😀')]:
            self.assertEqual(str(tsv_term(cell)),expected)
        self.assertEqual(tsv_term(r'<https://example.org/\u00E9>'),URIRef('https://example.org/é'))
        rows=[{'x':{'type':'literal','value':'nul\0 and é 😀'}}]
        data=exact_tsv(['x'],rows)
        self.assertIn(b'\\u0000',data)
        validate_table(data,'tsv',['x'],rows)

    def test_exact_export_write_failure_keeps_successful_json_result(self):
        import httpx
        from dblp_kg import DBLPKG
        class FailingExportStore(ArtifactStore):
            def put(self,*args,**kwargs):
                if kwargs.get('role')=='generated_lossless_tsv':
                    raise OSError('injected export-only failure')
                return super().put(*args,**kwargs)
        raw={'head':{'vars':['x']},'results':{'bindings':[{'x':{'type':'literal','value':'x'}}]}}
        with tempfile.TemporaryDirectory() as temp, httpx.Client(transport=httpx.MockTransport(lambda request:httpx.Response(200,json=raw))) as client:
            store=FailingExportStore(temp)
            result=DBLPKG(store,client).search('SELECT ?x WHERE {BIND("x" AS ?x)}',options={},limit=1,export='tsv_exact')
            self.assertEqual(result['status'],'partial')
            self.assertEqual(result['received'],1)
            self.assertEqual(result['export']['code'],'invalid_export')
            self.assertEqual(json.loads(store.read(result['records']['ref'])[1]),raw['results']['bindings'])

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

    def test_native_exports_send_the_documented_text_media_types(self):
        import httpx
        from dblp_kg import DBLPKG
        raw=json.loads((ROOT/'tests/fixtures/dblp-kg-search.json').read_text('utf-8'))
        calls=[]
        def response(request):
            accept=request.headers['accept'];calls.append(accept)
            if accept=='application/sparql-results+json':return httpx.Response(200,json=raw)
            suffix='csv' if accept=='text/csv' else 'tsv'
            return httpx.Response(200,content=(ROOT/f'tests/fixtures/dblp-kg-search.{suffix}').read_bytes(),headers={'content-type':accept})
        with tempfile.TemporaryDirectory() as temp:
            adapter=DBLPKG(ArtifactStore(temp),httpx.Client(transport=httpx.MockTransport(response)))
            adapter.min_interval=0
            query='SELECT ?publ ?title WHERE {?publ ?p ?title} ORDER BY ?publ'
            self.assertEqual(adapter.search(query,options={},limit=2,export='csv')['status'],'ok')
            self.assertEqual(adapter.search(query,options={},limit=2,export='tsv')['status'],'ok')
        self.assertEqual(calls,[
            'application/sparql-results+json','text/csv',
            'application/sparql-results+json','text/tab-separated-values'])

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

    def test_exact_tsv_is_generated_from_json_terms_without_changing_the_native_file(self):
        import httpx
        from dblp_kg import DBLPKG,validate_table
        raw=json.loads((ROOT/'tests/fixtures/dblp-kg-year.json').read_text('utf-8'))
        calls=[]
        def response(request):
            calls.append(request.headers['accept'])
            return httpx.Response(200,json=raw)
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp)
            adapter=DBLPKG(store,httpx.Client(transport=httpx.MockTransport(response)))
            result=adapter.search('SELECT ?year WHERE {?publ ?p ?year} ORDER BY ?year',options={},limit=1,export='tsv_exact')
            manifest,data=store.read(result['export']['ref'])
        self.assertEqual(result['status'],'ok')
        self.assertEqual(calls,['application/sparql-results+json'])
        self.assertEqual(manifest['role'],'generated_lossless_tsv')
        self.assertEqual(manifest['evidence_refs'],[result['evidence']['ref']])
        self.assertIn(b'"1997"^^<http://www.w3.org/2001/XMLSchema#gYear>',data)
        validate_table(data,'tsv',raw['head']['vars'],raw['results']['bindings'])

    def test_exact_tsv_uses_single_line_literal_escapes_and_keeps_missing_bindings_empty(self):
        from dblp_kg import exact_tsv
        variables=['text','missing']
        rows=[{'text':{'type':'literal','value':'line 1\nline 2\t"quoted"','xml:lang':'en'}}]
        data=exact_tsv(variables,rows)
        self.assertEqual(data,b'?text\t?missing\n"line 1\\nline 2\\t\\"quoted\\""@en\t\n')
        self.assertNotIn(b'"""',data)

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

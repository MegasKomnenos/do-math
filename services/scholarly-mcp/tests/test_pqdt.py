import importlib
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class PQDTContract(unittest.TestCase):
    def test_document_id_is_not_the_dissertation_publication_number(self):
        self.assertTrue((ROOT / "pqdt.py").exists(), "PQDT adapter is absent")
        mod = importlib.import_module("pqdt")
        rows, total = mod.pqdt_records((ROOT / "tests/fixtures/pqdt-result.html").read_text("utf-8"), "https://www.proquest.com/")
        self.assertEqual(total, 1)
        self.assertEqual(rows[0]["id"], "2618193239")
        self.assertIn("Resource Bounded Measure", rows[0]["title"])

    def test_search_options_preserve_sort_date_and_nested_include_exclude_facets(self):
        from pqdt import search_options
        self.assertEqual(search_options({'sort':'recent','publication_date':{'from':'2020-01-01','to':'2024-12-31'},
            'facets':{'subjects':{'include':['mathematics','computer science'],'exclude':['mathematics education']},
                      'languages':{'include':['English'],'exclude':[]}},'export_content':'citation_abstract_indexing'}),
            {'sort':'recent','publication_date':{'from':'2020-01-01','to':'2024-12-31'},
             'facets':{'subjects':{'include':['mathematics','computer science'],'exclude':['mathematics education']},
                       'languages':{'include':['English'],'exclude':[]}},'export_content':'citation_abstract_indexing'})
        for bad in ({'sort':'newest'},{'publication_date':'2020-2024'},{'publication_date':{'from':'2024-01-01','to':'2020-01-01'}},
                    {'facets':{'subject':['x']}},{'facets':{'subjects':{'include':'x'}}},
                    {'facets':{'subjects':{'include':['x'],'exclude':['x']}}},{'export_content':'all'}):
            with self.assertRaises(Exception):search_options(bad)
        many=[str(index) for index in range(21)]
        self.assertEqual(len(search_options({'facets':{'subjects':{'include':many}}})['facets']['subjects']['include']),21)

    def test_native_text_and_rtf_exports_match_the_selected_document(self):
        from pqdt import validate_native_export
        selected=[{'id':'2618193239','title':'Resource Bounded Measure and P Versus NP Problem-A Critical Study'}]
        text=b'Resource Bounded Measure and P Versus NP Problem-A Critical Study\nhttps://www.proquest.com/docview/2618193239\n'
        self.assertEqual(validate_native_export(text,'text',selected)['records'],1)
        rtf=br'{\rtf1\ansi Resource Bounded Measure and P Versus NP Problem-A Critical Study\par https://www.proquest.com/docview/2618193239}'
        self.assertEqual(validate_native_export(rtf,'rtf',selected)['records'],1)
        with self.assertRaises(Exception):validate_native_export(text.replace(b'2618193239',b'9999999999'),'text',selected)
        bib=br'@phdthesis{' + b'\n title={' + selected[0]['title'].encode() + b'},\n url={https://www.proquest.com/docview/2618193239}\n}'
        self.assertEqual(validate_native_export(bib,'bibtex',selected)['records'],1)
        ris=(ROOT/'tests/fixtures/pqdt.ris').read_bytes()
        for format,data in (('ris',ris+b'\n'+ris),('bibtex',bib+b'\n'+bib)):
            with self.assertRaises(Exception):validate_native_export(data,format,selected)
        other=ris.replace(b'2618193239',b'9999999999').replace(selected[0]['title'].encode(),b'Another dissertation')
        with self.assertRaises(Exception):validate_native_export(other+b'\n'+ris,'ris',[selected[0],{'id':'9999999999','title':'Another dissertation'}])

    def test_native_pdf_export_is_one_bibliography_page_bound_to_title_and_docview(self):
        from pqdt import validate_native_export
        import pymupdf
        selected=[{'id':'2618193239','title':'Resource Bounded Measure and P Versus NP Problem-A Critical Study'}]
        doc=pymupdf.open();page=doc.new_page();page.insert_text((72,72),selected[0]['title']);page.insert_link({'kind':pymupdf.LINK_URI,'from':pymupdf.Rect(72,90,300,110),'uri':'https://www.proquest.com/docview/2618193239'});data=doc.tobytes();doc.close()
        self.assertEqual(validate_native_export(data,'pdf',selected)['pages'],1)
        with self.assertRaises(Exception):validate_native_export(data,'pdf',[{'id':'9999999999','title':selected[0]['title']}])

    def test_native_xls_export_requires_one_header_and_one_selected_row(self):
        from pqdt import validate_native_export
        from unittest.mock import Mock,patch
        selected=[{'id':'2618193239','title':'Resource Bounded Measure and P Versus NP Problem-A Critical Study'}]
        cells=[['Title','StoreId','DocumentURL'],[selected[0]['title'],selected[0]['id'],'https://www.proquest.com/docview/'+selected[0]['id']]]
        sheet=Mock(nrows=2,ncols=3);sheet.cell_value.side_effect=lambda row,col:cells[row][col]
        book=Mock(nsheets=1);book.sheet_by_index.return_value=sheet
        with patch('xlrd.open_workbook',return_value=book):
            result=validate_native_export(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1data','xls',selected)
        self.assertEqual(result,{'records':1,'rows':2,'columns':3})

    def test_native_result_facets_page_and_applied_state_are_preserved(self):
        from pqdt import is_zero_page,pqdt_facets,pqdt_page,validate_facet_transition,validate_filter_page
        raw='''<div id="sortType-combo">Most recent first</div><input id="startingDate" value="2020-01-01"><input id="endingDate" value="2024-12-31">
        <div id="mainSubject-zone"><a class="filter_mainSubject">mathematics (1,366)</a></div>
        <div id="language-zone"><a class="filter_language">English (3,565)‎</a></div>
        <span class="applied">2020-01-01 - 2024-12-31</span><span class="applied">( mathematics OR computer science ) NOT mathematics education</span><span class="applied">English</span>
        <ul class="pagination"><li><a aria-label="Page 1">1</a></li><li class="active">2</li></ul>'''
        facets=pqdt_facets(raw)
        self.assertEqual(facets[0]['candidates'][0],{'value':'mathematics','label':'mathematics','count':1366})
        self.assertEqual(pqdt_page(raw),2)
        validate_filter_page(raw,{'sort':'recent','export_content':'citation_abstract_indexing','publication_date':{'from':'2020-01-01','to':'2024-12-31'},
            'facets':{'subjects':{'include':['mathematics','computer science'],'exclude':['mathematics education']},'languages':{'include':['English'],'exclude':[]}}})
        self.assertTrue(is_zero_page('<label id="searchTerm-label">Your search returned no results: Enter your search terms</label>'))
        self.assertFalse(is_zero_page('<aside>Try again when no results appear</aside>'))
        duplicate='''<div id="sortType-combo">Relevance</div><span class="applied">mathematics</span>'''
        with self.assertRaises(Exception):validate_filter_page(duplicate,{'sort':'relevance','export_content':'citation_abstract_indexing','facets':{
            'subjects':{'include':['mathematics'],'exclude':[]},'index_terms':{'include':['mathematics'],'exclude':[]}}})
        request={'include':['mathematics'],'exclude':[]}
        validate_facet_transition([],['mathematics'],request,'subjects')
        with self.assertRaises(Exception):validate_facet_transition([],['logic'],request,'subjects')
        validate_facet_transition([],['binary OR operation'],{'include':['binary OR operation'],'exclude':[]},'index_terms')
        validate_facet_transition([],['(mathematics)'],{'include':['(mathematics)'],'exclude':[]},'index_terms')
        opaque='''<div id="sortType-combo">Relevance</div><span class="applied">binary OR operation</span><span class="applied">(mathematics)</span>'''
        validate_filter_page(opaque,{'sort':'relevance','export_content':'citation_abstract_indexing','facets':{
            'subjects':{'include':['binary OR operation'],'exclude':[]},'index_terms':{'include':['(mathematics)'],'exclude':[]}}})
        validate_facet_transition([],['mathematics OR computer science'],{'include':['mathematics','computer science'],'exclude':[]},'subjects')
        unwrapped='''<div id="sortType-combo">Relevance</div><span class="applied">mathematics OR computer science</span>'''
        validate_filter_page(unwrapped,{'sort':'relevance','export_content':'citation_abstract_indexing','facets':{
            'subjects':{'include':['mathematics','computer science'],'exclude':[]}}})

    def test_external_account_exports_stop_before_opening_the_browser(self):
        from pqdt import PQDT
        from scholarly import ArtifactStore,ServiceError
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            adapter=PQDT(ArtifactStore(temp),None)
            for format in ('refworks','noodletools','easybib'):
                with self.assertRaises(ServiceError) as error:adapter.search('TI(algebra)',options={},limit=1,export=format)
                self.assertEqual(error.exception.result['code'],'external_import_required')
            with self.assertRaises(ServiceError) as error:adapter.search('TI(algebra)',options={'export_content':'citation_abstract'},limit=1,export='bibtex')
            self.assertEqual(error.exception.result['code'],'invalid_options')
            with self.assertRaises(ServiceError):adapter.search('TI(algebra)',options={'export_content':'citation_abstract'},limit=1)

    def test_fulltext_runtime_error_keeps_prepared_metadata(self):
        from pqdt import PQDT
        from scholarly import ArtifactStore
        from unittest.mock import Mock,patch
        import tempfile
        identifier='2618193239';record={'id':identifier,'title':'Resource Bounded Measure and P Versus NP Problem-A Critical Study',
            'bibliography':{'fields':{'ab':['abstract']}},'url':'https://www.proquest.com/pqdtglobal/docview/'+identifier,'pdf_page':'x'}
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);native=store.put((ROOT/'tests/fixtures/pqdt.ris').read_bytes(),'application/x-research-info-systems','pqdt',record['url'])
            gateway=Mock();adapter=PQDT(store,gateway);adapter.known[identifier]=(record,native);page=Mock();page.url='https://www.proquest.com/pqdtglobal/docview/'+identifier;page.locator.return_value.wait_for.side_effect=TimeoutError('late')
            with patch.object(adapter,'page',return_value=page),patch('pqdt.goto_source'):
                result=adapter.fetch(identifier,parts=['metadata','fulltext'])
        self.assertEqual(result['status'],'partial')
        self.assertEqual(result['components']['metadata']['status'],'available')
        self.assertEqual(result['components']['fulltext']['code'],'fulltext_retrieval_failed')
        self.assertEqual(result['components']['fulltext']['error_type'],'TimeoutError')

    def test_duplicate_native_records_fail_and_preserve_the_source_file(self):
        from pqdt import PQDT
        from scholarly import ArtifactStore,ServiceError
        from types import SimpleNamespace
        from unittest.mock import Mock
        import tempfile
        selected=[{'id':'2618193239','title':'Resource Bounded Measure and P Versus NP Problem-A Critical Study'}]
        data=(ROOT/'tests/fixtures/pqdt.ris').read_bytes()*2;response=SimpleNamespace(url='https://www.proquest.com/export',status=200,headers={'content-type':'application/x-research-info-systems'},body=lambda:data)
        pending=SimpleNamespace(value=response);manager=Mock();manager.__enter__=Mock(return_value=pending);manager.__exit__=Mock(return_value=False)
        context=Mock();context.pages=[];context.expect_event.return_value=manager;gateway=Mock(context=context)
        output=Mock();output.input_value.return_value='ProEndRefMgr';scope=Mock();scope.input_value.return_value='CITATIONABSTRACTINDEX';button=Mock()
        overlay=Mock();overlay.locator.side_effect=lambda selector:output if selector=='#exportMode' else scope if selector=='#citationTypeSelect' else button
        generic=Mock();page=Mock();page.locator.side_effect=lambda selector:overlay if selector=='#saveasExportLayerOverlay' else generic
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);adapter=PQDT(store,gateway)
            with self.assertRaises(ServiceError) as error:adapter.native_export(page,selected,'ris')
            preserved=store.read(error.exception.result['source_export']['ref'])[1]
        self.assertEqual(error.exception.result['code'],'export_range_mismatch')
        self.assertEqual(preserved,data)


if __name__ == "__main__":
    unittest.main()

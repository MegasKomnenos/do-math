from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scholarly import ServiceError
from sciencedirect import citation_record,pii_from_url
from waits import PROBE_WAIT_MS, SOURCE_WAIT_MS


class StatefulCheckbox:
    def __init__(self,identifier,checked):self.identifier=identifier;self.checked=checked
    def get_attribute(self,name):return self.identifier if name=='id' else None
    def is_checked(self):return self.checked
    def check(self,force=False):self.checked=True
    def uncheck(self,force=False):self.checked=False
    def press(self,key):
        if key=='Space':self.checked=not self.checked


class ToggleLabel:
    def __init__(self,checkbox):self.checkbox=checkbox;self.clicks=0
    def count(self):return 1
    def click(self):self.clicks+=1;self.checkbox.checked=not self.checkbox.checked
    def evaluate(self,script):self.click()


class LocatorItems:
    def __init__(self,items):self.items=items
    def count(self):return len(self.items)
    def nth(self,index):return self.items[index]


class ScienceDirectContract(unittest.TestCase):
    def test_search_accepts_results_visible_immediately_after_wait_timeout(self):
        from sciencedirect import wait_for_search_results
        from unittest.mock import Mock
        from playwright.sync_api import TimeoutError
        page=Mock();page.wait_for_function.side_effect=TimeoutError('initial render wait expired')
        page.content.return_value=(ROOT/'tests/fixtures/science-direct-search.html').read_text('utf-8')
        page.locator.return_value.count.return_value=3
        wait_for_search_results(page)
        self.assertEqual(page.wait_for_function.call_count,1)
        page.goto.assert_not_called()

    def test_search_unready_state_remains_a_bounded_retryable_error(self):
        from sciencedirect import wait_for_search_results
        from unittest.mock import Mock
        from playwright.sync_api import TimeoutError
        page=Mock();page.wait_for_function.side_effect=TimeoutError('render wait expired')
        page.content.return_value='<html><body>Loading</body></html>'
        page.locator.return_value.count.return_value=0
        with self.assertRaises(ServiceError) as raised:wait_for_search_results(page)
        self.assertEqual(raised.exception.result['code'],'search_interface_not_ready')
        self.assertTrue(raised.exception.result['retryable'])
        self.assertEqual([call.kwargs['timeout'] for call in page.wait_for_function.call_args_list],[SOURCE_WAIT_MS,PROBE_WAIT_MS])
        page.goto.assert_not_called()

    def test_native_ris_identity_title_and_full_abstract_are_preserved(self):
        data=(ROOT/'tests/fixtures/science-direct.ris').read_bytes()
        row=citation_record(data,'S002200009791494X','10.1006/jcss.1997.1494')
        self.assertEqual(row['title'],'Natural Proofs')
        self.assertEqual(len(row['fields']['ab'][0]),994)
        self.assertEqual(row['doi'],'10.1006/jcss.1997.1494')
        for pii,doi in [('S0000000000000000','10.1006/jcss.1997.1494'),('S002200009791494X','10.1006/jcss.1997.0000')]:
            with self.assertRaises(ServiceError):
                citation_record(data,pii,doi)

    def test_pii_is_taken_from_the_document_path(self):
        self.assertEqual(pii_from_url('https://www.sciencedirect.com/science/article/abs/pii/S002200009791494X'),'S002200009791494X')
        with self.assertRaises(ServiceError):
            pii_from_url('https://www.sciencedirect.com/search?qs=S002200009791494X')

    def test_native_search_rows_use_one_result_container_and_keep_pii_separate_from_doi(self):
        from sciencedirect import search_records
        raw=(ROOT/'tests/fixtures/science-direct-search.html').read_text('utf-8')
        rows,total=search_records(raw,'https://www.sciencedirect.com/search')
        self.assertEqual((len(rows),total),(3,3))
        self.assertEqual(rows[0]['pii'],'S156042922600065X')
        self.assertIsNone(rows[0]['doi'])
        self.assertEqual(rows[0]['title'],'Autograding Mathematical Induction Proofs with Natural Language Processing')
        self.assertEqual(rows[0]['authors'],['Chenyan Zhao','Mariana Silva','Seth Poulsen'])
        self.assertEqual(rows[0]['publication'],'International Journal of Artificial Intelligence in Education')
        self.assertEqual(rows[0]['publication_date'],'December 2025')
        self.assertNotIn('/pdfft',rows[0]['url'])
        self.assertTrue(rows[0]['pdf_url'].startswith('https://www.sciencedirect.com/science/article/pii/S156042922600065X/pdfft'))
        self.assertEqual((rows[2]['authors'],rows[2]['publication'],rows[2]['publication_date'],rows[2]['pdf_url']),([],None,None,None))
        found_rows,found_total=search_records(raw.replace('3 results','3 results found'),'https://www.sciencedirect.com/search')
        self.assertEqual((len(found_rows),found_total),(3,3))

    def test_native_search_zero_result_is_distinct_from_an_unrecognized_page(self):
        from sciencedirect import search_records
        empty=(ROOT/'tests/fixtures/science-direct-search-empty.html').read_text('utf-8')
        self.assertEqual(search_records(empty,'https://www.sciencedirect.com/search'),([],0))
        with self.assertRaises(ServiceError) as error:search_records('<html><body>Search</body></html>','https://www.sciencedirect.com/search')
        self.assertEqual(error.exception.result['code'],'invalid_response')
        with self.assertRaises(ServiceError):search_records('<html><aside>Help when no results appear</aside></html>','https://www.sciencedirect.com/search')

    def test_native_search_params_preserve_literal_query_and_observed_fields(self):
        from sciencedirect import search_params
        self.assertEqual(search_params('proof AND natural',{'field':'Title','date':'1995-2017','sort':'date'},25,50),
                         {'title':'proof AND natural','date':'1995-2017','sortBy':'date','offset':25,'show':50})
        self.assertEqual(search_params('Natural Proofs',{},0,25),{'qs':'Natural Proofs','offset':0,'show':25})
        self.assertEqual(search_params('',{'title':'Natural Proofs'},0,25),{'title':'Natural Proofs','offset':0,'show':25})
        self.assertEqual(search_params('',{'publication_exact':'Journal of Algebra'},0,25),{'offset':0,'show':25})
        self.assertEqual(search_params('',{'article_types':['FLA']},0,25),{'articleTypes':'FLA','offset':0,'show':25})
        self.assertEqual(search_params('"natural proof" AND (logic OR algebra) NOT modal',{},0,25),
                         {'qs':'"natural proof" AND (logic OR algebra) NOT modal','offset':0,'show':25})
        with self.assertRaises(ServiceError):search_params('',{},0,25)
        with self.assertRaises(ServiceError):search_params('x',{'field':'Abstract'},0,25)
        for bad in ({'date':['1995','2017']},{'volume':{'from':5}},{'sort':1},{'field':[]},{'field':{}}):
            with self.assertRaises(ServiceError):search_params('x',bad,0,25)
        for bad in ({'date':'95-17'},{'date':'2017-1995'},{'volume':'five'},{'issue':'1..3'}):
            with self.assertRaises(ServiceError):search_params('x',bad,0,25)

    def test_doc_id_accepts_only_the_native_issn_or_isbn_role(self):
        from sciencedirect import search_params
        for value in ('0065-230X','0065230X','978-0-443-43236-1','9780443432361'):
            self.assertEqual(search_params('',{'doc_id':value},0,25)['docId'],value)
        self.assertEqual(search_params('0065-230X',{'field':'ISSNISBN'},0,25)['docId'],'0065-230X')
        for value in ('S0065230X26000631','10.1016/S0065-230X(26)00063-1'):
            with self.assertRaises(ServiceError) as error:
                search_params('',{'doc_id':value},0,25)
            self.assertEqual(error.exception.result['code'],'invalid_options')
            with self.assertRaises(ServiceError) as error:
                search_params(value,{'field':'ISSNISBN'},0,25)
            self.assertEqual(error.exception.result['code'],'invalid_options')

    def test_current_facet_references_and_native_array_serialization(self):
        from sciencedirect import facet_candidates,search_params
        raw=(ROOT/'tests/fixtures/science-direct-search.html').read_text('utf-8')
        facets=facet_candidates(raw)
        self.assertIn({'group':'article_type','native_group':'articleTypes','value':'FLA','label':'Research articles','count':2,'selected':True},facets)
        self.assertIn({'group':'publication_title','native_group':'publicationTitles','value':'272332','label':'Journal of Algebra','count':1,'selected':False},facets)
        params=search_params('algebra',{'article_types':['FLA','REV'],'subject_areas':['2600'],'languages':['en'],'access_types':['openaccess'],'subscribed_only':True,'date':'2020-2025'},0,25)
        self.assertEqual(params,{'qs':'algebra','date':'2020-2025','articleTypes':'FLA,REV','subjectAreas':'2600','languages':'en','accessTypes':'openaccess','subs':'true','offset':0,'show':25})
        for bad in ({'article_types':'FLA'},{'article_types':['FLA,REV']},{'subject_areas':[]},{'access_types':[1]}):
            with self.assertRaises(ServiceError):search_params('algebra',bad,0,25)
        for bad in ({'subscribed_only':'true'},{'year_range':'2020-2025'}):
            with self.assertRaises(ServiceError):search_params('algebra',bad,0,25)

    def test_subscribed_and_year_state_are_read_from_current_controls(self):
        from sciencedirect import facet_group_state,result_filter_state
        raw=(ROOT/'tests/fixtures/science-direct-search.html').read_text('utf-8')
        self.assertEqual(result_filter_state(raw),{'subscribed':True,'year_mode':'range','year_start':'2020','year_end':'2025'})
        self.assertEqual(facet_group_state(raw)['article_type'],{'native_group':'articleTypes','complete':False,'expandable':True,'visible_candidates':1})

    def test_result_facet_show_more_controls_are_expanded_before_parsing(self):
        from sciencedirect import expand_result_facets
        from unittest.mock import Mock
        buttons={};page=Mock()
        def locate(selector):
            button=Mock();button.count.return_value=1;button.is_visible.return_value=True
            buttons[selector]=button;return button
        page.locator.side_effect=locate
        expanded=expand_result_facets(page)
        self.assertEqual(expanded,['articleTypes','publicationTitles','subjectAreas','languages'])
        self.assertEqual(page.wait_for_function.call_count,4)
        self.assertTrue(all(button.click.called for selector,button in buttons.items() if selector.startswith('button')))

    def test_supplementary_links_are_pii_bound_and_exclude_article_figures(self):
        from sciencedirect import supplementary_links
        raw='''<a href="https://ars.els-cdn.com/content/image/1-s2.0-S0167278924001155-gr1.jpg">figure</a>
                 <a href="https://ars.els-cdn.com/content/image/1-s2.0-S0167278924001155-mmc1.mp4" title="Download video (1MB)">Download</a>'''
        found=supplementary_links(raw,'https://www.sciencedirect.com/science/article/pii/S0167278924001155',
                                  'S0167278924001155',{'ars.els-cdn.com'})
        self.assertEqual(found,[{'url':'https://ars.els-cdn.com/content/image/1-s2.0-S0167278924001155-mmc1.mp4',
                                 'path':'/content/image/1-s2.0-S0167278924001155-mmc1.mp4','label':'Download video (1MB)'}])
        with self.assertRaises(ServiceError):
            supplementary_links(raw.replace('S0167278924001155-mmc1','S0000000000000000-mmc1'),
                                'https://www.sciencedirect.com/science/article/pii/S0167278924001155',
                                'S0167278924001155',{'ars.els-cdn.com'})

    def test_supplementary_download_preserves_the_native_mp4(self):
        from sciencedirect import ScienceDirect,native_supplementary
        from scholarly import ArtifactStore
        from unittest.mock import Mock,patch
        import tempfile
        pii='S0167278924001155';url='https://ars.els-cdn.com/content/image/1-s2.0-'+pii+'-mmc1.mp4'
        raw=('<a href="'+url+'" title="Download video (1MB)">Download</a>').encode()
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);source=store.put(raw,'text/html','science-direct','https://www.sciencedirect.com/science/article/pii/'+pii)
            adapter=ScienceDirect(store,Mock())
            data=b'\x00\x00\x00\x18ftypisom'+b'x'*64
            with patch('sciencedirect.browser_download',return_value=(data,'video/mp4',url)) as download:
                found=native_supplementary(adapter,pii,source)
            stored=store.read(found['files'][0]['artifact']['ref'])[1]
        self.assertEqual(found['status'],'available')
        self.assertEqual(stored,data)
        self.assertEqual(download.call_args.args[2],adapter.profile.download_hosts)

    def test_native_page_indicator_and_query_must_match_the_requested_window(self):
        from sciencedirect import search_page,validate_search_location
        raw=(ROOT/'tests/fixtures/science-direct-search.html').read_text('utf-8')
        rows,total,page,pages=search_page(raw,'https://www.sciencedirect.com/search')
        self.assertEqual((len(rows),total,page,pages),(3,3,1,1))
        expected={'title':'proof AND natural','date':'1995-2017','sortBy':'date','offset':25,'show':25}
        validate_search_location('https://www.sciencedirect.com/search?title=proof+AND+natural&date=1995-2017&sortBy=date&offset=25&show=25',expected)
        with self.assertRaises(ServiceError) as error:
            validate_search_location('https://www.sciencedirect.com/search?title=proof+AND+natural&offset=25&show=25',expected)
        self.assertEqual(error.exception.result['code'],'query_mismatch')
        with self.assertRaises(ServiceError):
            validate_search_location('https://www.sciencedirect.com/search?title=proof+AND+natural&date=1995-2017&sortBy=date&articleTypes=FLA&offset=25&show=25',expected)

    def test_name_fetch_keeps_candidates_for_selection(self):
        from sciencedirect import ScienceDirect
        from scholarly import ArtifactStore
        from unittest.mock import patch
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            adapter=ScienceDirect(ArtifactStore(temp),None)
            with patch.object(adapter,'search',return_value={'status':'ok','received':1}) as search:
                result=adapter.fetch('Natural Proofs',parts=['metadata'])
        self.assertEqual(result['status'],'selection_required')
        search.assert_called_once_with('Natural Proofs',options={'field':'Title'},limit=20)

    def test_current_result_ui_ris_is_bound_to_the_selected_row(self):
        from sciencedirect import ScienceDirect,native_search_citation
        from scholarly import ArtifactStore
        from unittest.mock import Mock
        import tempfile
        data=(ROOT/'tests/fixtures/science-direct.ris').read_bytes()
        row={'pii':'S002200009791494X','doi':None,'title':'Natural Proofs'}
        checkbox=Mock();checkbox.get_attribute.return_value=row['pii']
        title=Mock();title.get_attribute.return_value='/science/article/pii/'+row['pii'];title.inner_text.return_value=row['title']
        export=Mock();export.count.return_value=1;choice=Mock();choice.count.return_value=1
        item=Mock();item.locator.side_effect=lambda selector: checkbox if 'checkbox' in selector else title
        item.get_by_role.side_effect=lambda role,name,exact=True: export if name=='Export' else choice
        listed=Mock();listed.nth.return_value=item
        page=Mock();page.url='https://www.sciencedirect.com/search';page.locator.return_value=listed
        gateway=Mock();gateway.native_download.return_value=(data,'ScienceDirect_citations.ris','https://www.sciencedirect.com/search/api/export-citations')
        with tempfile.TemporaryDirectory() as temp:
            adapter=ScienceDirect(ArtifactStore(temp),gateway)
            found=native_search_citation(adapter,page,row,0)
        self.assertEqual(found['status'],'available')
        self.assertEqual(found['pii'],row['pii'])
        self.assertEqual(found['doi'],'10.1006/jcss.1997.1494')
        self.assertEqual(gateway.native_download.call_args.args[3],'/search/api/export-citations')

        row['title']='Weak generators of W- algebras for type A'
        title.inner_text.return_value='Weak generators of W-algebras for type A'
        native=data.replace(b'Natural Proofs',b'Weak generators of W-algebras for type A')
        gateway.native_download.return_value=(native,'citation.ris','https://www.sciencedirect.com/search/api/export-citations')
        with tempfile.TemporaryDirectory() as temp:
            adapter=ScienceDirect(ArtifactStore(temp),gateway)
            found=native_search_citation(adapter,page,row,0)
            self.assertEqual(found['status'],'available')
            self.assertEqual(adapter.store.read(found['artifact']['ref'])[1],native)

    def test_current_result_ui_bibtex_and_plain_keep_selected_identity(self):
        from sciencedirect import ScienceDirect,native_search_citation
        from scholarly import ArtifactStore
        from unittest.mock import Mock
        import tempfile
        row={'pii':'S002200009791494X','doi':None,'title':'Natural Proofs'}
        for format,data,suffix in (
            ('bibtex',(ROOT/'tests/fixtures/science-direct.bib').read_bytes(),'.bib'),
            ('plain',b'Natural Proofs\n10.1006/jcss.1997.1494\nS002200009791494X\n','.txt')):
            checkbox=Mock();checkbox.get_attribute.return_value=row['pii']
            title=Mock();title.get_attribute.return_value='/science/article/pii/'+row['pii'];title.inner_text.return_value=row['title']
            export=Mock();export.count.return_value=1;choice=Mock();choice.count.return_value=1;item=Mock();item.locator.side_effect=lambda selector: checkbox if 'checkbox' in selector else title
            item.get_by_role.side_effect=lambda role,name,exact=True: export if name=='Export' else choice
            listed=Mock();listed.nth.return_value=item
            page=Mock();page.url='https://www.sciencedirect.com/search';page.locator.return_value=listed
            gateway=Mock();gateway.native_download.return_value=(data,'citation'+suffix,'https://www.sciencedirect.com/search/api/export-citations')
            with tempfile.TemporaryDirectory() as temp:
                adapter=ScienceDirect(ArtifactStore(temp),gateway)
                found=native_search_citation(adapter,page,row,0,format=format,expected_doi='10.1006/jcss.1997.1494')
            self.assertEqual(found['status'],'available')
            self.assertEqual(found['format'],format)
            self.assertEqual(found['doi'],'10.1006/jcss.1997.1494')

    def test_result_without_an_export_control_is_not_a_timeout(self):
        from sciencedirect import ScienceDirect,native_search_citation
        from scholarly import ArtifactStore
        from unittest.mock import Mock
        import tempfile
        row={'pii':'S002200009791494X','doi':None,'title':'Natural Proofs'}
        checkbox=Mock();checkbox.get_attribute.return_value=row['pii'];checkbox.is_checked.side_effect=[False,True,True]
        title=Mock();title.get_attribute.return_value='/science/article/pii/'+row['pii'];title.inner_text.return_value=row['title']
        missing=Mock();missing.count.return_value=0;missing.wait_for.side_effect=RuntimeError('absent')
        label=Mock();item=Mock()
        item.locator.side_effect=lambda selector: checkbox if 'checkbox' in selector else label if selector.startswith('label[') else title
        item.get_by_role.return_value=missing
        listed=Mock();listed.nth.return_value=item
        boxes=Mock();boxes.count.return_value=1;boxes.nth.return_value=checkbox
        buttons=Mock();buttons.count.return_value=0
        page=Mock();page.url='https://www.sciencedirect.com/search'
        page.locator.side_effect=lambda selector: listed if selector=='li.ResultItem' else buttons if selector=='button' else boxes
        page.get_by_role.return_value=missing
        with tempfile.TemporaryDirectory() as temp:
            adapter=ScienceDirect(ArtifactStore(temp),Mock())
            with self.assertRaises(ServiceError) as error:native_search_citation(adapter,page,row,0)
        self.assertEqual(error.exception.result['code'],'native_export_not_offered')
        self.assertEqual(label.click.call_count,2)

    def test_missing_row_export_uses_exact_checkbox_selected_bulk_export(self):
        from sciencedirect import ScienceDirect,native_search_citation
        from scholarly import ArtifactStore
        from unittest.mock import Mock
        import tempfile
        data=(ROOT/'tests/fixtures/science-direct.ris').read_bytes()
        row={'pii':'S002200009791494X','doi':None,'title':'Natural Proofs'}
        checkbox=Mock();checkbox.get_attribute.return_value=row['pii'];checkbox.is_checked.side_effect=[False,True,True]
        title=Mock();title.get_attribute.return_value='/science/article/pii/'+row['pii'];title.inner_text.return_value=row['title']
        label=Mock()
        row_missing=Mock();row_missing.count.return_value=0;row_missing.is_visible.return_value=False
        row_trigger=Mock();row_trigger.count.return_value=0;row_trigger.wait_for.side_effect=RuntimeError('not hydrated')
        item=Mock()
        def item_locator(selector):
            if 'checkbox-input' in selector:return checkbox
            if 'result-list-title-link' in selector:return title
            if selector.startswith('label['):return label
            raise AssertionError(selector)
        item.locator.side_effect=item_locator
        item.get_by_role.side_effect=lambda role,name,exact=True: row_trigger if name=='Export' else row_missing
        listed=Mock();listed.nth.return_value=item
        all_boxes=Mock();all_boxes.count.return_value=1;all_boxes.nth.return_value=checkbox
        bulk_trigger=Mock();bulk_trigger.inner_text.return_value='Export';bulk_trigger.evaluate.return_value=False
        bulk_choice=Mock();bulk_choice.inner_text.return_value='Export citation to RIS';bulk_choice.evaluate.return_value=False
        buttons=Mock();buttons.count.return_value=2;buttons.nth.side_effect=[bulk_trigger,bulk_choice,bulk_trigger,bulk_choice]
        page=Mock();page.url='https://www.sciencedirect.com/search'
        page.locator.side_effect=lambda selector: listed if selector=='li.ResultItem' else buttons if selector=='button' else all_boxes
        page.get_by_role.side_effect=lambda role,name,exact=True: bulk_trigger if name=='Export' else bulk_choice
        gateway=Mock();gateway.native_download.return_value=(data,'citation.ris','https://www.sciencedirect.com/search/api/export-citations')
        with tempfile.TemporaryDirectory() as temp:
            found=native_search_citation(ScienceDirect(ArtifactStore(temp),gateway),page,row,0)
        self.assertEqual((found['pii'],found['doi']),(row['pii'],'10.1006/jcss.1997.1494'))
        label.click.assert_called()
        bulk_trigger.click.assert_called_once()
        self.assertEqual(gateway.native_download.call_args.args[3],'/search/api/export-citations')

    def test_result_export_trigger_may_hydrate_after_the_result_row(self):
        from sciencedirect import ScienceDirect,native_search_citation
        from scholarly import ArtifactStore
        from unittest.mock import Mock
        import tempfile
        data=(ROOT/'tests/fixtures/science-direct.ris').read_bytes();row={'pii':'S002200009791494X','doi':None,'title':'Natural Proofs'}
        checkbox=Mock();checkbox.get_attribute.return_value=row['pii'];title=Mock();title.get_attribute.return_value='/science/article/pii/'+row['pii'];title.inner_text.return_value=row['title']
        trigger=Mock();trigger.count.return_value=0;choice=Mock();choice.count.return_value=0;choice.is_visible.return_value=False
        item=Mock();item.locator.side_effect=lambda selector: checkbox if 'checkbox' in selector else title
        item.get_by_role.side_effect=lambda role,name,exact=True: trigger if name=='Export' else choice
        listed=Mock();listed.nth.return_value=item;page=Mock();page.url='https://www.sciencedirect.com/search';page.locator.return_value=listed
        gateway=Mock();gateway.native_download.return_value=(data,'citation.ris','https://www.sciencedirect.com/search/api/export-citations')
        with tempfile.TemporaryDirectory() as temp:
            found=native_search_citation(ScienceDirect(ArtifactStore(temp),gateway),page,row,0)
        self.assertEqual(found['status'],'available')
        trigger.wait_for.assert_called_once_with(state='visible',timeout=SOURCE_WAIT_MS)
        trigger.click.assert_called_once()

    def test_current_result_pdf_is_bound_to_pii_title_and_source_doi(self):
        from sciencedirect import ScienceDirect,native_result_pdf
        from scholarly import ArtifactStore
        from unittest.mock import Mock
        import pymupdf,tempfile
        row={'pii':'S156042922600065X','title':'Autograding Mathematical Induction Proofs with Natural Language Processing'}
        doc=pymupdf.open();page_pdf=doc.new_page();page_pdf.insert_text((72,72),'10.1007/s40593-025-00498-2');doc.set_metadata({'title':row['title']});data=doc.tobytes();doc.close()
        checkbox=Mock();checkbox.get_attribute.return_value=row['pii']
        title=Mock();title.get_attribute.return_value='/science/article/pii/'+row['pii'];title.inner_text.return_value=row['title']
        pdf=Mock();pdf.count.return_value=1;pdf.get_attribute.return_value='/science/article/pii/'+row['pii']+'/pdfft?pid=main.pdf'
        item=Mock();item.locator.side_effect=lambda selector: checkbox if 'checkbox' in selector else title;item.get_by_role.return_value=pdf
        listed=Mock();listed.nth.return_value=item;page=Mock();page.url='https://www.sciencedirect.com/search';page.locator.return_value=listed
        gateway=Mock();gateway.native_download.return_value=(data,'main.pdf','https://pdf.sciencedirectassets.com/path/1-s2.0-'+row['pii']+'/main.pdf')
        with tempfile.TemporaryDirectory() as temp:
            adapter=ScienceDirect(ArtifactStore(temp),gateway)
            found=native_result_pdf(adapter,page,row,0,'10.1007/s40593-025-00498-2')
        self.assertEqual(found['status'],'available')
        self.assertEqual(found['pages'],1)
        self.assertEqual(gateway.native_download.call_args.args[2],adapter.profile.download_hosts)
        self.assertTrue(callable(gateway.native_download.call_args.args[3]))

    def test_pdf_title_may_be_verified_from_first_pages_when_metadata_is_blank(self):
        from sciencedirect import ScienceDirect,native_result_pdf
        from scholarly import ArtifactStore
        from unittest.mock import Mock
        import pymupdf,tempfile
        row={'pii':'S156042922600065X','title':'Autograding Mathematical Induction Proofs with Natural Language Processing'}
        doc=pymupdf.open();pdf_page=doc.new_page();pdf_page.insert_textbox(pymupdf.Rect(72,72,520,200),row['title']+'\n10.1007/s40593-025-00498-2');data=doc.tobytes();doc.close()
        checkbox=Mock();checkbox.get_attribute.return_value=row['pii'];title=Mock();title.get_attribute.return_value='/science/article/pii/'+row['pii'];title.inner_text.return_value=row['title']
        pdf=Mock();pdf.count.return_value=1;pdf.get_attribute.return_value='/science/article/pii/'+row['pii']+'/pdfft?pid=main.pdf'
        item=Mock();item.locator.side_effect=lambda selector: checkbox if 'checkbox' in selector else title;item.get_by_role.return_value=pdf
        listed=Mock();listed.nth.return_value=item;page=Mock();page.url='https://www.sciencedirect.com/search';page.locator.return_value=listed
        gateway=Mock();gateway.native_download.return_value=(data,'main.pdf','https://pdf.sciencedirectassets.com/path/1-s2.0-'+row['pii']+'/main.pdf')
        with tempfile.TemporaryDirectory() as temp:
            found=native_result_pdf(ScienceDirect(ArtifactStore(temp),gateway),page,row,0,'10.1007/s40593-025-00498-2')
        self.assertEqual(found['status'],'available')

    def test_selected_pdf_keeps_a_preselected_target_and_restores_other_selection_after_success(self):
        from sciencedirect import ScienceDirect,native_result_pdf
        from scholarly import ArtifactStore
        from unittest.mock import Mock
        import pymupdf,tempfile
        row={'pii':'S0065230X26000631','title':'Preface'};doi='10.1016/S0065-230X(26)00063-1'
        target=StatefulCheckbox(row['pii'],True);other=StatefulCheckbox('S0000000000000001',True)
        labels={box.identifier:ToggleLabel(box) for box in (target,other)}
        title=Mock();title.get_attribute.return_value='/science/article/pii/'+row['pii'];title.inner_text.return_value=row['title']
        absent=Mock();absent.count.return_value=0
        item=Mock();item.locator.side_effect=lambda selector: target if 'checkbox-input' in selector else labels[row['pii']] if selector.startswith('label[') else title;item.get_by_role.return_value=absent
        listed=LocatorItems([item]);boxes=LocatorItems([target,other]);bulk=Mock();bulk.count.return_value=1;bulk.is_visible.return_value=True
        body=Mock();body.inner_text.return_value=''
        page=Mock();page.url='https://www.sciencedirect.com/search?title=Preface&docId=0065-230X'
        def locate(selector):
            if selector=='li.ResultItem':return listed
            if selector=='li.ResultItem input.checkbox-input[type="checkbox"]':return boxes
            if selector=='body':return body
            if selector.startswith('label[for="'):return labels[selector.split('"')[1]]
            raise AssertionError(selector)
        page.locator.side_effect=locate;page.get_by_text.return_value.first=bulk
        doc=pymupdf.open();pdf_page=doc.new_page();pdf_page.insert_text((72,72),doi);doc.set_metadata({'title':row['title']});data=doc.tobytes();doc.close()
        observed=[]
        def download(_,action,*args,**kwargs):
            observed.append([box.identifier for box in (target,other) if box.is_checked()]);action()
            return data,'main.pdf','https://pdf.sciencedirectassets.com/path/1-s2.0-'+row['pii']+'/main.pdf'
        gateway=Mock();gateway.native_download.side_effect=download
        with tempfile.TemporaryDirectory() as temp:
            found=native_result_pdf(ScienceDirect(ArtifactStore(temp),gateway),page,row,0,doi)
        self.assertEqual(found['status'],'available')
        self.assertEqual(observed,[[row['pii']]])
        self.assertTrue(target.is_checked())
        self.assertTrue(other.is_checked())
        self.assertEqual(labels[row['pii']].clicks,0)

    def test_selected_pdf_restores_new_target_and_other_selection_after_subscription_error(self):
        from sciencedirect import ScienceDirect,native_result_pdf
        from scholarly import ArtifactStore
        from unittest.mock import Mock
        import tempfile
        row={'pii':'S0065230X26000631','title':'Preface'};doi='10.1016/S0065-230X(26)00063-1'
        target=StatefulCheckbox(row['pii'],False);other=StatefulCheckbox('S0000000000000001',True)
        labels={box.identifier:ToggleLabel(box) for box in (target,other)}
        title=Mock();title.get_attribute.return_value='/science/article/pii/'+row['pii'];title.inner_text.return_value=row['title']
        absent=Mock();absent.count.return_value=0
        item=Mock();item.locator.side_effect=lambda selector: target if 'checkbox-input' in selector else labels[row['pii']] if selector.startswith('label[') else title;item.get_by_role.return_value=absent
        listed=LocatorItems([item]);boxes=LocatorItems([target,other]);bulk=Mock();bulk.count.return_value=1;bulk.is_visible.return_value=True
        body=Mock();body.inner_text.return_value='Your selections could not be downloaded as you are not subscribed to that content.'
        page=Mock();page.url='https://www.sciencedirect.com/search?title=Preface&docId=0065-230X'
        def locate(selector):
            if selector=='li.ResultItem':return listed
            if selector=='li.ResultItem input.checkbox-input[type="checkbox"]':return boxes
            if selector=='body':return body
            if selector.startswith('label[for="'):return labels[selector.split('"')[1]]
            raise AssertionError(selector)
        page.locator.side_effect=locate;page.get_by_text.return_value.first=bulk
        observed=[]
        def missing(_,action,*args,**kwargs):
            observed.append([box.identifier for box in (target,other) if box.is_checked()]);action()
            raise ServiceError('download_missing','no file',retryable=True)
        gateway=Mock();gateway.native_download.side_effect=missing
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ServiceError) as error:
                native_result_pdf(ScienceDirect(ArtifactStore(temp),gateway),page,row,0,doi)
        self.assertEqual(error.exception.result['code'],'fulltext_access_restricted')
        self.assertEqual(error.exception.result['status'],'restricted')
        self.assertEqual(observed,[[row['pii']]])
        self.assertFalse(target.is_checked())
        self.assertTrue(other.is_checked())

    def test_selected_pdf_cleanup_failure_does_not_replace_subscription_error(self):
        from sciencedirect import ScienceDirect,native_result_pdf
        from scholarly import ArtifactStore
        from unittest.mock import Mock
        import tempfile
        row={'pii':'S0065230X26000631','title':'Preface'};doi='10.1016/S0065-230X(26)00063-1'
        target=StatefulCheckbox(row['pii'],False);label=ToggleLabel(target)
        original_evaluate=label.evaluate
        def blocked_after_modal(script):
            if label.clicks:raise RuntimeError('modal detached the label')
            original_evaluate(script)
        label.evaluate=blocked_after_modal
        target.uncheck=lambda force=False:(_ for _ in ()).throw(RuntimeError('detached checkbox'))
        title=Mock();title.get_attribute.return_value='/science/article/pii/'+row['pii'];title.inner_text.return_value=row['title']
        absent=Mock();absent.count.return_value=0
        item=Mock();item.locator.side_effect=lambda selector: target if 'checkbox-input' in selector else label if selector.startswith('label[') else title;item.get_by_role.return_value=absent
        listed=LocatorItems([item]);boxes=LocatorItems([target]);bulk=Mock();bulk.count.return_value=1;bulk.is_visible.return_value=True
        body=Mock();body.inner_text.return_value='Your selections could not be downloaded as you are not subscribed to that content.'
        page=Mock();page.url='https://www.sciencedirect.com/search?title=Preface&docId=0065-230X'
        def locate(selector):
            if selector=='li.ResultItem':return listed
            if selector=='li.ResultItem input.checkbox-input[type="checkbox"]':return boxes
            if selector=='body':return body
            if selector.startswith('label[for="'):return label
            raise AssertionError(selector)
        page.locator.side_effect=locate;page.get_by_text.return_value.first=bulk
        gateway=Mock();gateway.native_download.side_effect=ServiceError('download_missing','no file',retryable=True)
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ServiceError) as error:
                native_result_pdf(ScienceDirect(ArtifactStore(temp),gateway),page,row,0,doi)
        self.assertEqual(error.exception.result['code'],'fulltext_access_restricted')
        self.assertEqual(error.exception.result['status'],'restricted')
        self.assertEqual(error.exception.result['selection_cleanup_error_type'],'RuntimeError')

    def test_verified_pdf_survives_a_later_selection_cleanup_failure(self):
        from sciencedirect import ScienceDirect,native_result_pdf
        from scholarly import ArtifactStore
        from unittest.mock import Mock,patch
        import pymupdf,tempfile
        row={'pii':'S0065230X26000631','title':'Preface'};doi='10.1016/S0065-230X(26)00063-1'
        checkbox=Mock();checkbox.get_attribute.return_value=row['pii']
        title=Mock();title.get_attribute.return_value='/science/article/pii/'+row['pii'];title.inner_text.return_value=row['title']
        absent=Mock();absent.count.return_value=0
        item=Mock();item.locator.side_effect=lambda selector:checkbox if 'checkbox' in selector else title;item.get_by_role.return_value=absent
        page=Mock();page.url='https://www.sciencedirect.com/search';page.locator.return_value.nth.return_value=item
        bulk=page.get_by_text.return_value.first;bulk.count.return_value=1;bulk.is_visible.return_value=True
        doc=pymupdf.open();doc.new_page().insert_text((72,72),doi);doc.set_metadata({'title':row['title']});data=doc.tobytes();doc.close()
        gateway=Mock();gateway.native_download.return_value=(data,'main.pdf','https://pdf.sciencedirectassets.com/path/'+row['pii']+'/main.pdf')
        restore=Mock(side_effect=RuntimeError('page closed during cleanup'))
        with tempfile.TemporaryDirectory() as temp,patch('sciencedirect.exact_result_selection',return_value=restore):
            store=ArtifactStore(temp)
            result=native_result_pdf(ScienceDirect(store,gateway),page,row,0,doi)
            self.assertEqual(result['status'],'available')
            self.assertEqual(store.read(result['artifact']['ref'])[1],data)
            self.assertEqual(result['selection_cleanup_error_type'],'RuntimeError')

    def test_fetch_keeps_result_row_subscription_condition_when_detail_pdf_is_unresolved(self):
        from sciencedirect import ScienceDirect
        from publishers import Publisher
        from scholarly import ArtifactStore,encoded
        from unittest.mock import Mock,patch
        import tempfile
        pii='S0065230X26000631';title='Preface';doi='10.1016/S0065-230X(26)00063-1'
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);adapter=ScienceDirect(store,Mock())
            records=store.put(encoded([{'pii':pii,'title':title,'metadata':{'citation_pii':[pii]}}]),'application/json','science-direct','https://www.sciencedirect.com/science/article/pii/'+pii)
            base={'status':'partial','source':'science-direct','records':records,'source_page':{'ref':'page'},
                  'components':{'metadata':{'status':'available'},'fulltext':{'status':'not_implemented'}},
                  'identity':{'observed_dois':[doi]}}
            selected=ServiceError('fulltext_access_restricted','selected download says not subscribed',status='restricted')
            detail=ServiceError('fulltext_unresolved','detail PDF returned same record HTML')
            adapter.known[pii]={'query':'Preface','options':{'field':'Title','doc_id':'0065-230X'},'page_offset':0}
            adapter.search=Mock(return_value={'records':records})
            with patch.object(Publisher,'fetch',return_value=base),patch('sciencedirect.native_result_pdf',side_effect=selected),patch('sciencedirect.native_document_pdf',side_effect=detail):
                result=adapter.fetch(pii,parts=['metadata','fulltext'])
        component=result['components']['fulltext']
        self.assertEqual(component['code'],'fulltext_access_restricted')
        self.assertEqual(component['status'],'restricted')
        self.assertEqual(component['detail_error_code'],'fulltext_unresolved')

    def test_cold_fetch_uses_publication_identifier_to_find_a_common_title(self):
        from sciencedirect import ScienceDirect
        from publishers import Publisher
        from scholarly import ArtifactStore,encoded
        from unittest.mock import Mock,patch
        import tempfile
        pii='S0065230X26000631'
        for key,value in [('citation_issn','0065-230X'),('citation_isbn','9780443330902')]:
            with self.subTest(field=key),tempfile.TemporaryDirectory() as temp:
                store=ArtifactStore(temp);adapter=ScienceDirect(store,Mock())
                records=store.put(encoded([{'pii':pii,'title':'Preface','metadata':{'citation_pii':[pii],key:[value]}}]),
                    'application/json','science-direct','https://www.sciencedirect.com/science/article/pii/'+pii)
                base={'status':'partial','records':records,'components':{'fulltext':{'status':'not_implemented'}}}
                def search(query,*,options,start=0,limit=20):
                    if options.get('doc_id')!=value:
                        return {'records':store.put(encoded([{'pii':'OTHER','title':'Preface'}]),'application/json','science-direct','https://www.sciencedirect.com/search')}
                    adapter.known[pii]={'query':query,'options':options,'page_offset':0}
                    return {'records':records}
                adapter.search=Mock(side_effect=search)
                with patch.object(Publisher,'fetch',return_value=base),patch('sciencedirect.native_result_pdf',return_value={'status':'available'}) as native,patch('sciencedirect.native_document_pdf',side_effect=ServiceError('fulltext_unresolved','same record HTML')):
                    result=adapter.fetch(pii,parts=['fulltext'])
                self.assertEqual(result['components']['fulltext']['status'],'available')
                self.assertEqual(adapter.search.call_args_list[0].kwargs['options'],{'field':'Title','doc_id':value})
                native.assert_called_once()

    def test_pdf_failure_preserves_search_and_detail_causes(self):
        from sciencedirect import ScienceDirect
        from publishers import Publisher
        from scholarly import ArtifactStore,encoded
        from unittest.mock import Mock,patch
        import tempfile
        pii='S0065230X26000631'
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);adapter=ScienceDirect(store,Mock())
            records=store.put(encoded([{'title':'Preface','metadata':{'citation_pii':[pii]}}]),'application/json','science-direct','https://www.sciencedirect.com')
            base={'status':'partial','records':records,'components':{'fulltext':{'status':'not_implemented'}}}
            adapter.search=Mock(side_effect=ServiceError('search_interface_not_ready','Search timed out',retryable=True))
            with patch.object(Publisher,'fetch',return_value=base),patch('sciencedirect.native_document_pdf',side_effect=ServiceError('fulltext_unresolved','Same record HTML')):
                result=adapter.fetch(pii,parts=['fulltext'])
            component=result['components']['fulltext']
            self.assertEqual(component['code'],'fulltext_unresolved')
            self.assertEqual(component['result_row_error']['code'],'search_interface_not_ready')
            self.assertTrue(component['result_row_error']['retryable'])

    def test_document_pdf_control_can_supply_a_pdf_when_the_result_row_cannot(self):
        from sciencedirect import ScienceDirect,native_document_pdf
        from scholarly import ArtifactStore
        from unittest.mock import Mock,patch
        import pymupdf,tempfile
        pii='S0065230X26000631';title='Preface';doi='10.1016/S0065-230X(26)00063-1'
        initial='<meta name="citation_pii" content="'+pii+'"><meta name="citation_title" content="'+title+'">'
        stable=initial+'<a href="/science/article/pii/'+pii+'/pdfft">View PDF</a>'
        doc=pymupdf.open();pdf_page=doc.new_page();pdf_page.insert_text((72,72),doi);doc.set_metadata({'title':title});data=doc.tobytes();doc.close()
        page=Mock();page.url='https://www.sciencedirect.com/science/chapter/bookseries/pii/'+pii
        page.content.side_effect=[initial,stable]
        wait=Mock();page.locator.return_value.first=wait
        gateway=Mock();gateway.context.pages=[page];gateway.native_download.return_value=(data,'main.pdf','https://pdf.sciencedirectassets.com/path/1-s2.0-'+pii+'/main.pdf')
        with tempfile.TemporaryDirectory() as temp:
            adapter=ScienceDirect(ArtifactStore(temp),gateway);adapter.document=Mock(return_value=page)
            found=native_document_pdf(adapter,pii,title,doi)
        self.assertEqual(found['status'],'available')
        self.assertEqual(found['pages'],1)
        wait.wait_for.assert_called_once_with(state='attached',timeout=SOURCE_WAIT_MS)
        self.assertEqual(gateway.native_download.call_args.kwargs['timeout'],SOURCE_WAIT_MS)
        page.close.assert_called_once()

    def test_document_pdf_purchase_is_a_record_access_condition(self):
        from sciencedirect import ScienceDirect,native_document_pdf
        from scholarly import ArtifactStore
        from unittest.mock import Mock
        import tempfile
        pii='S1765462926000553';title='A book review';doi='10.1016/example'
        raw=('<meta name="citation_pii" content="'+pii+'"><meta name="citation_title" content="'+title+'">'
             '<a href="/getaccess/pii/'+pii+'/purchase">Purchase PDF</a>')
        page=Mock();page.url='https://www.sciencedirect.com/science/article/abs/pii/'+pii;page.content.return_value=raw
        with tempfile.TemporaryDirectory() as temp:
            adapter=ScienceDirect(ArtifactStore(temp),Mock());adapter.document=Mock(return_value=page)
            with self.assertRaises(ServiceError) as error:native_document_pdf(adapter,pii,title,doi)
        self.assertEqual(error.exception.result['code'],'fulltext_access_restricted')
        self.assertEqual(error.exception.result['status'],'restricted')
        page.close.assert_called_once()

    def test_document_pdf_control_returning_the_same_record_html_is_unresolved(self):
        from sciencedirect import ScienceDirect,native_document_pdf
        from scholarly import ArtifactStore
        from unittest.mock import Mock,patch
        import tempfile
        pii='S0065230X26000631';title='Preface';doi='10.1016/S0065-230X(26)00063-1'
        initial='<meta name="citation_pii" content="'+pii+'"><meta name="citation_title" content="'+title+'">'
        stable=initial+'<a href="/science/article/pii/'+pii+'/pdfft">View PDF</a>'
        page=Mock();page.url='https://www.sciencedirect.com/science/chapter/bookseries/pii/'+pii;page.is_closed.return_value=False
        page.content.side_effect=[initial,stable];page.locator.return_value.first=Mock()
        popup=Mock();popup.url=page.url;popup.is_closed.return_value=False;popup.content.return_value=stable
        gateway=Mock();pages=[page];gateway.context.pages=pages
        def missing(*args,**kwargs):
            pages.append(popup)
            raise ServiceError('download_missing','no file',retryable=True)
        gateway.native_download.side_effect=missing
        with tempfile.TemporaryDirectory() as temp:
            adapter=ScienceDirect(ArtifactStore(temp),gateway);adapter.document=Mock(return_value=page)
            with self.assertRaises(ServiceError) as error:native_document_pdf(adapter,pii,title,doi)
        self.assertEqual(error.exception.result['code'],'fulltext_unresolved')
        self.assertEqual(error.exception.result['status'],'error')
        popup.close.assert_called_once()
        page.close.assert_called_once()

    def test_fetch_uses_exact_document_state_when_title_search_cannot_restore_the_row(self):
        from sciencedirect import ScienceDirect
        from publishers import Publisher
        from scholarly import ArtifactStore,encoded
        from unittest.mock import Mock,patch
        import tempfile
        pii='S0065230X26000631';title='Preface';doi='10.1016/S0065-230X(26)00063-1'
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);adapter=ScienceDirect(store,Mock())
            records=store.put(encoded([{'title':title,'metadata':{'citation_pii':[pii]}}]),'application/json','science-direct','https://www.sciencedirect.com/science/article/pii/'+pii)
            base={'status':'partial','source':'science-direct','records':records,'source_page':{'ref':'page'},
                  'components':{'metadata':{'status':'available'},'fulltext':{'status':'not_implemented'}},
                  'identity':{'observed_dois':[doi]}}
            missing=ServiceError('selection_required','ambiguous title',status='unsupported')
            detail=ServiceError('fulltext_not_offered','record has no individual PDF',status='not_offered')
            with patch.object(Publisher,'fetch',return_value=base),patch.object(adapter,'search',side_effect=missing),patch('sciencedirect.native_document_pdf',side_effect=detail) as fallback:
                result=adapter.fetch(pii,parts=['metadata','fulltext'])
        self.assertEqual(result['components']['fulltext']['code'],'fulltext_not_offered')
        fallback.assert_called_once_with(adapter,pii,title,doi)

    def test_document_metadata_survives_a_separate_current_ui_export_restriction(self):
        from sciencedirect import ScienceDirect
        from publishers import Publisher
        from scholarly import ArtifactStore
        from unittest.mock import patch
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);source_records=store.put(b'[{"title":"Natural Proofs","metadata":{"citation_pii":["S002200009791494X"]}}]','application/json','science-direct','https://www.sciencedirect.com/science/article/pii/S002200009791494X')
            base={'status':'ok','source':'science-direct','target':'https://www.sciencedirect.com/science/article/pii/S002200009791494X',
                  'records':source_records,'source_page':{'ref':'page'},'components':{'metadata':{'status':'available','artifact':source_records}},
                  'identity':{'observed_dois':['10.1006/jcss.1997.1494']}}
            adapter=ScienceDirect(store,None)
            with patch.object(Publisher,'fetch',return_value=base) as source,patch.object(adapter,'search',side_effect=ServiceError('publisher_access_challenge','blocked',status='restricted')):
                result=adapter.fetch('S002200009791494X',parts=['metadata','export'])
        self.assertEqual(result['status'],'partial')
        self.assertEqual(result['components']['metadata']['status'],'available')
        self.assertEqual(result['components']['export']['status'],'error')
        self.assertEqual(result['components']['export']['result_row_error_code'],'publisher_access_challenge')
        self.assertEqual([item['code'] for item in result['components']['export']['errors']],
                         ['native_browser_required']*3)
        source.assert_called_once_with('https://www.sciencedirect.com/science/article/pii/S002200009791494X',parts=['metadata'])

    def test_fetch_export_uses_detail_cite_controls_when_title_search_cannot_restore_row(self):
        from sciencedirect import ScienceDirect
        from publishers import Publisher
        from scholarly import ArtifactStore,encoded
        from unittest.mock import Mock,patch
        import tempfile
        pii='S0065230X26000631';title='Preface';doi='10.1016/S0065-230X(26)00063-1'
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);adapter=ScienceDirect(store,Mock())
            source_records=store.put(encoded([{'title':title,'metadata':{'citation_pii':[pii]}}]),'application/json','science-direct','https://www.sciencedirect.com/science/article/pii/'+pii)
            base={'status':'ok','source':'science-direct','records':source_records,'source_page':{'ref':'page'},
                  'components':{'metadata':{'status':'available'}},'identity':{'observed_dois':[doi]}}
            missing=ServiceError('selection_required','title search did not restore exact PII',status='unsupported')
            made=[]
            def detail(_,selected_pii,selected_title,format='ris',expected_doi=None):
                made.append((selected_pii,selected_title,format,expected_doi))
                return {'status':'available','format':format,'artifact':{'ref':format}}
            with patch.object(Publisher,'fetch',return_value=base),patch.object(adapter,'search',side_effect=missing),patch('sciencedirect.native_document_citation',side_effect=detail):
                result=adapter.fetch(pii,parts=['metadata','export'])
        self.assertEqual(result['components']['export']['status'],'available')
        self.assertEqual(result['components']['export']['result_row_error_code'],'selection_required')
        self.assertEqual([item[2] for item in made],['ris','bibtex','plain'])
        self.assertTrue(all(item[:2]==(pii,title) and item[3]==doi for item in made))

    def test_detail_citation_control_validates_pii_title_and_doi(self):
        from sciencedirect import ScienceDirect,native_document_citation
        from scholarly import ArtifactStore
        from unittest.mock import Mock
        import tempfile
        pii='S0065230X26000631';title='Preface';doi='10.1016/S0065-230X(26)00063-1'
        raw=('<meta name="citation_pii" content="'+pii+'">'
             '<meta name="citation_title" content="'+title+'">')
        ris=('TY  - CHAP\nT1  - '+title+'\nDO  - '+doi+'\n'
             'UR  - https://www.sciencedirect.com/science/article/pii/'+pii+'\nER  - \n').encode()
        page=Mock();page.content.return_value=raw;page.is_closed.return_value=False
        trigger=Mock();trigger_group=Mock();trigger_group.first=trigger
        choice=Mock();choice.is_visible.return_value=True
        choices=Mock();choices.first=choice;choices.count.return_value=1;choices.nth.return_value=choice
        page.get_by_text.side_effect=lambda label,exact=True:trigger_group if label=='Cite' else choices
        gateway=Mock()
        def download(_,action,*args):
            action()
            return ris,'preface.ris','https://www.sciencedirect.com/sdfe/arp/cite'
        gateway.native_download.side_effect=download
        with tempfile.TemporaryDirectory() as temp:
            adapter=ScienceDirect(ArtifactStore(temp),gateway);adapter.document=Mock(return_value=page)
            result=native_document_citation(adapter,pii,title,format='ris',expected_doi=doi)
        self.assertEqual((result['status'],result['title'],result['doi']),('available',title,doi))
        self.assertEqual(result['scope'],'One native detail-page citation selected by PII')
        gateway.native_download.assert_called_once()
        trigger.click.assert_called_once();choice.click.assert_called_once();page.close.assert_called_once()

    def test_fetch_export_finds_the_exact_pii_before_using_current_result_controls(self):
        from sciencedirect import ScienceDirect
        from publishers import Publisher
        from scholarly import ArtifactStore,encoded
        from unittest.mock import Mock,patch
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);adapter=ScienceDirect(store,Mock())
            all_rows=[{'pii':'S'+str(index).zfill(16),'title':'Natural Proofs'} for index in range(43)]+[{'pii':'S002200009791494X','title':'Natural Proofs'}]
            page_rows=all_rows[25:]
            records=store.put(encoded(all_rows),'application/json','science-direct','https://www.sciencedirect.com/search')
            page_records=store.put(encoded(page_rows),'application/json','science-direct','https://www.sciencedirect.com/search?offset=25')
            source_records=store.put(encoded([{'title':'Natural Proofs','metadata':{'citation_pii':['S002200009791494X']}}]),'application/json','science-direct','https://www.sciencedirect.com/science/article/pii/S002200009791494X')
            base={'status':'ok','source':'science-direct','records':source_records,'source_page':{'ref':'page'},
                  'components':{'metadata':{'status':'available'}},'identity':{'observed_dois':['10.1006/jcss.1997.1494']}}
            search={'status':'ok','received':44,'records':records};restored={'status':'ok','received':19,'records':page_records}
            adapter.gateway.pages={'science-direct':Mock()}
            made=[]
            def citation(_,__,row,index,format='ris',expected_doi=None):
                made.append((row['pii'],index,format,expected_doi));return {'status':'available','format':format,'artifact':{'ref':format}}
            calls=[]
            def find_exact(*args,**kwargs):
                calls.append((args,kwargs))
                if len(calls)==1:
                    adapter.known['S002200009791494X']={'row':all_rows[-1],'query':'"Natural Proofs"','options':{'field':'Title'},'page_offset':25}
                    return search
                return restored
            with patch.object(Publisher,'fetch',return_value=base),patch.object(adapter,'search',side_effect=find_exact),patch('sciencedirect.native_search_citation',side_effect=citation):
                result=adapter.fetch('S002200009791494X',parts=['metadata','export'])
        self.assertEqual(result['components']['export']['status'],'available')
        self.assertEqual(made,[('S002200009791494X',18,'ris','10.1006/jcss.1997.1494'),
                               ('S002200009791494X',18,'bibtex','10.1006/jcss.1997.1494'),
                               ('S002200009791494X',18,'plain','10.1006/jcss.1997.1494')])
        self.assertEqual(calls,[(('"Natural Proofs"',),{'options':{'field':'Title'},'limit':100}),
                                (('"Natural Proofs"',),{'options':{'field':'Title'},'start':25,'limit':25})])

    def test_fetch_export_reuses_the_exact_current_search_row(self):
        from sciencedirect import ScienceDirect
        from publishers import Publisher
        from scholarly import ArtifactStore,encoded
        from unittest.mock import Mock,patch
        import tempfile
        pii='S156042922600065X';title='Autograding Mathematical Induction Proofs with Natural Language Processing'
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);page=Mock();page.url='https://www.sciencedirect.com/search?qs=Natural+Proofs';page.is_closed.return_value=False
            gateway=Mock();gateway.pages={'science-direct':page};adapter=ScienceDirect(store,gateway)
            source_records=store.put(encoded([{'title':title,'metadata':{'citation_pii':[pii]}}]),'application/json','science-direct','https://www.sciencedirect.com/science/article/pii/'+pii)
            base={'status':'ok','source':'science-direct','records':source_records,'source_page':{'ref':'page'},
                  'components':{'metadata':{'status':'available'}},'identity':{'observed_dois':['10.1007/s40593-025-00498-2']}}
            row={'pii':pii,'title':title};adapter.known[pii]={'row':row,'query':'Natural Proofs','options':{},'page_offset':0}
            found_records=store.put(encoded([row]),'application/json','science-direct','https://www.sciencedirect.com/search')
            made=[]
            def citation(_,__,row,index,format='ris',expected_doi=None):
                made.append((row['pii'],index,format,expected_doi));return {'status':'available','format':format,'artifact':{'ref':format}}
            with patch.object(Publisher,'fetch',return_value=base),patch.object(adapter,'search',return_value={'status':'ok','received':1,'records':found_records}) as restore,patch('sciencedirect.native_search_citation',side_effect=citation):
                result=adapter.fetch(pii,parts=['metadata','export'])
        self.assertEqual(result['components']['export']['status'],'available')
        self.assertEqual([item[2] for item in made],['ris','bibtex','plain'])
        restore.assert_called_once_with('Natural Proofs',options={},start=0,limit=25)

if __name__=='__main__':
    unittest.main()

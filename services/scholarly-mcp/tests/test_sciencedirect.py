from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scholarly import ServiceError
from sciencedirect import citation_record,pii_from_url

class ScienceDirectContract(unittest.TestCase):
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
        checkbox=Mock();checkbox.get_attribute.return_value=row['pii']
        title=Mock();title.get_attribute.return_value='/science/article/pii/'+row['pii'];title.inner_text.return_value=row['title']
        missing=Mock();missing.count.return_value=0;missing.wait_for.side_effect=RuntimeError('absent')
        item=Mock();item.locator.side_effect=lambda selector: checkbox if 'checkbox' in selector else title;item.get_by_role.return_value=missing
        listed=Mock();listed.nth.return_value=item;page=Mock();page.url='https://www.sciencedirect.com/search';page.locator.return_value=listed
        with tempfile.TemporaryDirectory() as temp:
            adapter=ScienceDirect(ArtifactStore(temp),Mock())
            with self.assertRaises(ServiceError) as error:native_search_citation(adapter,page,row,0)
        self.assertEqual(error.exception.result['code'],'native_export_not_offered')

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
        trigger.wait_for.assert_called_once_with(state='visible',timeout=10000)
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
        self.assertEqual(result['components']['export']['code'],'publisher_access_challenge')
        source.assert_called_once_with('https://www.sciencedirect.com/science/article/pii/S002200009791494X',parts=['metadata'])

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

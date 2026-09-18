import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scholarly import ArtifactStore,ServiceError
from waits import SOURCE_WAIT_MS


class APSInstitutionalContract(unittest.TestCase):
    def test_custom_date_and_multiple_facet_values_preserve_native_query(self):
        from aps_institutional import query_params
        clauses,params=query_params('algebra',{
            'field':'title','terms':[{'field':'author','query':'Stetter','operator':'AND'}],
            'journal':['prd','prl'],'category':['openaccess','suggestion'],
            'start_date':'2024-01-01','end_date':'2026-09-12','sort':'recent',
        })
        self.assertEqual(clauses,[{'field':'title','value':'algebra','operator':'AND'},
                                  {'field':'author','value':'Stetter','operator':'AND'}])
        self.assertEqual(params['journal[]'],['prd','prl'])
        self.assertEqual(params['category[]'],['openaccess','suggestion'])
        self.assertEqual((params['date'],params['start_date'],params['end_date']),('custom','2024-01-01','2026-09-12'))
        self.assertEqual(params['sort'],'recent')

    def test_invalid_custom_dates_and_facet_arrays_are_rejected(self):
        from aps_institutional import query_params
        for options in ({'start_date':'2024-01-01'}, {'start_date':'2026-01-01','end_date':'2025-01-01'},
                        {'date':'month','start_date':'2024-01-01','end_date':'2025-01-01'},
                        {'start_date':'20240101','end_date':'2025-01-01'},
                        {'start_date':'2024-W01-1','end_date':'2025-01-01'},
                        {'journal':[]},{'journal':['prd','']},{'journal':['prd','prd']}):
            with self.subTest(options=options),self.assertRaises(ServiceError) as error:
                query_params('algebra',options)
            self.assertEqual(error.exception.result['code'],'invalid_options')

    def test_received_page_retains_every_facet_value_and_custom_date(self):
        from aps_institutional import query_params,search
        from bs4 import BeautifulSoup
        raw=(ROOT/'tests/fixtures/aps-search.html').read_text('utf-8');soup=BeautifulSoup(raw,'html.parser')
        main=soup.select_one('#search-main')
        for value in ('prd','prl'):
            control=soup.new_tag('input',attrs={'type':'checkbox','name':'journal[]','value':value,'checked':''});main.append(control)
        date_select=soup.select_one('#desktop-date-select')
        if date_select is None:
            date_select=soup.new_tag('select',id='desktop-date-select',attrs={'name':'date'});main.append(date_select)
            for value in ('','week','month','year','custom'):
                option=soup.new_tag('option',value=value);option.string=value or 'Any time';date_select.append(option)
        for option in date_select.select('option'):option.attrs.pop('selected',None)
        date_select.select_one('option[value=custom]')['selected']=''
        start=soup.select_one('#desktop-start-date')
        end=soup.select_one('#desktop-end-date')
        if start is None:
            start=soup.new_tag('input',id='desktop-start-date');date_select.insert_after(start)
        if end is None:
            end=soup.new_tag('input',id='desktop-end-date');start.insert_after(end)
        start['value']='2024-01-01';end['value']='2026-09-12';raw=str(soup)
        options={'journal':['prd','prl'],'start_date':'2024-01-01','end_date':'2026-09-12'}
        clauses,params=query_params('algebra',options)
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);page=SimpleNamespace(url='https://journals.aps.org/search',is_closed=lambda:False)
            proof=store.put(raw,'text/html','aps-institutional',page.url);facets=store.put('{}','application/json','aps-institutional',page.url)
            gateway=SimpleNamespace(start=Mock(),context=Mock(),pages={'aps-institutional':page})
            adapter=SimpleNamespace(store=store,gateway=gateway,source='aps-institutional',profile=SimpleNamespace(hosts=('journals.aps.org',)),
                _aps_last={'params':params,'raw':raw,'url':page.url,'start':0,'proof':proof,'facets':facets})
            result=search(adapter,'algebra',options=options,start=1,limit=1)
        self.assertEqual((result['status'],result['received']),('ok',1))

    def test_native_ris_and_bibtex_validate_the_selected_document_doi(self):
        from aps_institutional import APSInstitutional
        from publishers import PROFILES
        from dataclasses import replace
        doi='10.1103/RevModPhys.39.259'
        for format,data in (
            ('ris',f'TY  - JOUR\nTI  - Group Algebra\nDO  - {doi}\nER  -\n'.encode()),
            ('bibtex',f'@article{{test, title={{Group Algebra}}, doi={{{doi}}}}}\n'.encode()),
        ):
            with self.subTest(format=format),tempfile.TemporaryDirectory() as temp:
                button=Mock();filtered=Mock();filtered.first=button
                radio=Mock();download=Mock();page=Mock();page.url='https://journals-aps-org.libproxy.knu.ac.kr/rmp/abstract/'+doi
                page.locator.side_effect=lambda selector: filtered if selector=='button.export-article-citation' else radio if selector==f'input[name=export_format][value={format}]' else download
                gateway=SimpleNamespace(native_download=Mock(side_effect=lambda page,action,*args,**kwargs:(action(),data,'file','https://journals-aps-org.libproxy.knu.ac.kr/rmp/export/'+doi)[1:]))
                profile=replace(next(p for p in PROFILES if p.source=='aps'),source='aps-institutional')
                adapter=APSInstitutional(ArtifactStore(temp),gateway,profile)
                artifact=adapter.citation(page,doi,format)
                self.assertEqual(adapter.store.read(artifact['ref'])[1],data)
                self.assertEqual(artifact['format'],format)
                gateway.native_download.assert_called_once()

    def test_changed_citation_identity_is_rejected(self):
        from aps_institutional import APSInstitutional
        from publishers import PROFILES
        from dataclasses import replace
        doi='10.1103/RevModPhys.39.259';data=b'TY  - JOUR\nTI  - Wrong\nDO  - 10.1103/Other.1\nER  -\n'
        page=Mock();page.url='https://journals.aps.org/rmp/abstract/'+doi
        page.locator.return_value.filter.return_value.first=Mock()
        gateway=SimpleNamespace(native_download=Mock(return_value=(data,'file','https://journals.aps.org/rmp/export/'+doi)))
        profile=replace(next(p for p in PROFILES if p.source=='aps'),source='aps-institutional')
        with tempfile.TemporaryDirectory() as temp,self.assertRaises(ServiceError) as error:
            APSInstitutional(ArtifactStore(temp),gateway,profile).citation(page,doi,'ris')
        self.assertEqual(error.exception.result['code'],'identity_mismatch')

    def test_completed_citation_closes_the_modal_before_another_document_action(self):
        from aps_institutional import APSInstitutional
        from publishers import PROFILES
        from dataclasses import replace
        doi='10.1103/RevModPhys.39.259';data=f'TY  - JOUR\nDO  - {doi}\nER  -\n'.encode()
        modal=Mock();modal.count.return_value=1;modal.is_visible.side_effect=[False,True];close=Mock();modal.get_by_role.return_value.first=close
        button=Mock();buttons=Mock();buttons.first=button;radio=Mock();download=Mock();page=Mock();page.url='https://journals.aps.org/rmp/abstract/'+doi
        page.locator.side_effect=lambda selector: modal if selector=='#export-article-dialog' else buttons if selector=='button.export-article-citation' else radio if 'export_format' in selector else download
        gateway=SimpleNamespace(native_download=Mock(return_value=(data,'file','https://journals.aps.org/rmp/export/'+doi)))
        profile=replace(next(p for p in PROFILES if p.source=='aps'),source='aps-institutional')
        with tempfile.TemporaryDirectory() as temp:
            APSInstitutional(ArtifactStore(temp),gateway,profile).citation(page,doi,'ris')
        close.click.assert_called_once_with()

    def test_search_citation_export_uses_only_the_requested_window(self):
        from aps_institutional import APSInstitutional
        from publishers import PROFILES
        from dataclasses import replace
        rows=[{'doi':'10.1103/A.1','title':'A','url':'https://journals.aps.org/prl/abstract/10.1103/A.1'},
              {'doi':'10.1103/B.2','title':'B','url':'https://journals.aps.org/prl/abstract/10.1103/B.2'}]
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);records=store.put(json.dumps(rows),'application/json','aps-institutional','https://journals.aps.org/search')
            profile=replace(next(p for p in PROFILES if p.source=='aps'),source='aps-institutional')
            adapter=APSInstitutional(store,SimpleNamespace(),profile)
            base={'status':'ok','source':'aps-institutional','received':2,'records':records,'export':records,'errors':[]}
            with patch('aps_institutional.search',return_value=base),patch.object(adapter,'citation_for_url',side_effect=[{'ref':'one'},{'ref':'two'}]) as citation:
                result=adapter.search('x',options={},start=19,limit=2,export='ris')
            self.assertEqual([call.args for call in citation.call_args_list],[(rows[0]['url'],rows[0]['doi'],'ris'),(rows[1]['url'],rows[1]['doi'],'ris')])
            self.assertEqual(result['export']['artifacts'],[{'format':'ris','artifact':{'ref':'one'}},{'format':'ris','artifact':{'ref':'two'}}])

    def test_native_pdf_must_match_the_selected_journal_and_doi(self):
        from aps_institutional import APSInstitutional
        from publishers import PROFILES
        from dataclasses import replace
        doi='10.1103/RevModPhys.39.259';url='https://journals.aps.org/rmp/pdf/'+doi
        link=Mock();link.get_attribute.return_value=url;link.is_visible.return_value=True
        links=Mock();links.count.return_value=1;links.nth.return_value=link
        page=Mock();page.url='https://journals.aps.org/rmp/abstract/'+doi;page.locator.return_value=links
        gateway=SimpleNamespace(native_download=Mock(side_effect=lambda page,action,*args,**kwargs:(action(),b'%PDF-1.4\n%%EOF','paper.pdf',url)[1:]))
        profile=replace(next(p for p in PROFILES if p.source=='aps'),source='aps-institutional')
        with tempfile.TemporaryDirectory() as temp,patch('pymupdf.open') as opened:
            opened.return_value.__enter__.return_value.__len__.return_value=3
            adapter=APSInstitutional(ArtifactStore(temp),gateway,profile)
            artifact=adapter.pdf(page,doi)
            self.assertEqual(adapter.store.read(artifact['ref'])[1],b'%PDF-1.4\n%%EOF')
            self.assertEqual(artifact['pages'],3)
        gateway.native_download.assert_called_once_with(page,unittest.mock.ANY,profile.download_hosts,'/rmp/pdf/'+doi,timeout=SOURCE_WAIT_MS)

    def test_pdf_uses_exact_http_control_when_chrome_emits_no_download_event(self):
        from aps_institutional import APSInstitutional
        from publishers import PROFILES
        from dataclasses import replace
        doi='10.1103/RevModPhys.39.259';url='https://journals.aps.org/rmp/pdf/'+doi
        link=Mock();link.get_attribute.return_value=url;link.is_visible.return_value=True
        links=Mock();links.count.return_value=1;links.nth.return_value=link
        page=Mock();page.url='https://journals.aps.org/rmp/abstract/'+doi;page.locator.return_value=links;page.evaluate.return_value='Browser UA'
        gateway=SimpleNamespace(context=Mock(),native_download=Mock(side_effect=ServiceError('download_missing','No event')))
        profile=replace(next(p for p in PROFILES if p.source=='aps'),source='aps-institutional')
        with tempfile.TemporaryDirectory() as temp,patch('aps_institutional.browser_download',return_value=(b'%PDF-1.4\n%%EOF','application/pdf',url)) as request,patch('pymupdf.open') as opened:
            opened.return_value.__enter__.return_value.__len__.return_value=2
            artifact=APSInstitutional(ArtifactStore(temp),gateway,profile).pdf(page,doi)
        self.assertEqual(artifact['pages'],2)
        request.assert_called_once_with(gateway.context,url,profile.download_hosts,headers={'User-Agent':'Browser UA','Referer':'https://journals.aps.org/'})

    def test_supplements_are_bound_to_the_selected_doi_and_host(self):
        from aps_institutional import supplement_links
        doi='10.1103/PhysRevLett.1.2'
        raw=f'''<a href="/prl/supplemental/{doi}/data.csv">Data</a>
        <a href="https://example.org/prl/supplemental/{doi}/foreign.zip">Foreign</a>
        <a href="/prl/supplemental/10.1103/Other.1/wrong.pdf">Wrong</a>'''
        self.assertEqual(supplement_links(raw,'https://journals.aps.org/prl/abstract/'+doi,doi,{'journals.aps.org'}),
                         [{'url':'https://journals.aps.org/prl/supplemental/'+doi+'/data.csv','label':'Data'}])

    def test_native_supplement_download_deduplicates_controls_and_preserves_file(self):
        from aps_institutional import APSInstitutional
        from publishers import PROFILES
        from dataclasses import replace
        doi='10.1103/PhysRevLett.115.250402';url='https://journals.aps.org/prl/supplemental/'+doi+'/supp.pdf'
        raw=f'<a href="{url}"></a><a href="{url}">supp.pdf</a>'
        link=Mock();link.get_attribute.return_value=url;link.is_visible.return_value=True
        links=Mock();links.count.return_value=1;links.nth.return_value=link
        page=Mock();page.url='https://journals.aps.org/prl/abstract/'+doi;page.content.return_value=raw;page.locator.return_value=links
        gateway=SimpleNamespace(native_download=Mock(side_effect=lambda page,action,*args,**kwargs:(action(),b'%PDF-1.4\n%%EOF','supp.pdf',url)[1:]))
        profile=replace(next(p for p in PROFILES if p.source=='aps'),source='aps-institutional')
        with tempfile.TemporaryDirectory() as temp,patch('pymupdf.open') as opened:
            opened.return_value.__enter__.return_value.__len__.return_value=1
            adapter=APSInstitutional(ArtifactStore(temp),gateway,profile)
            result=adapter.supplementary(page,doi,{'ref':'source'})
            self.assertEqual((result['status'],len(result['files'])),('available',1))
            self.assertEqual(adapter.store.read(result['files'][0]['artifact']['ref'])[1],b'%PDF-1.4\n%%EOF')
        gateway.native_download.assert_called_once_with(page,unittest.mock.ANY,profile.download_hosts,'/prl/supplemental/'+doi+'/supp.pdf',timeout=SOURCE_WAIT_MS)

    def test_fetch_replaces_source_metadata_export_and_pdf_with_native_components(self):
        from aps_institutional import APSInstitutional
        from publishers import PROFILES,Publisher
        from dataclasses import replace
        doi='10.1103/RevModPhys.39.259';url='https://journals.aps.org/rmp/abstract/'+doi
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp);records=store.put(json.dumps([{'doi':doi,'title':'Group Algebra','url':url}]),'application/json','aps-institutional',url)
            source=store.put('<main>source</main>','text/html','aps-institutional',url)
            base={'status':'ok','source':'aps-institutional','target':url,'records':records,'source_page':source,'components':{
                'metadata':{'status':'available','artifact':records},'abstract':{'status':'available','artifact':source}}}
            page=Mock();page.url=url;page.content.return_value='<main></main>';page.close=Mock()
            profile=replace(next(p for p in PROFILES if p.source=='aps'),source='aps-institutional')
            adapter=APSInstitutional(store,SimpleNamespace(),profile);adapter.document=Mock(return_value=page)
            citations=[{'ref':'bib'},{'ref':'ris'}];pdf={'ref':'pdf'}
            with patch.object(Publisher,'fetch',return_value=base),patch.object(adapter,'citation',side_effect=citations),patch.object(adapter,'pdf',return_value=pdf):
                result=adapter.fetch(url,parts=['metadata','abstract','export','fulltext','supplementary'])
            self.assertEqual(result['components']['export']['artifacts'],[{'format':'bibtex','artifact':citations[0]},{'format':'ris','artifact':citations[1]}])
            self.assertEqual(result['components']['fulltext'],{'status':'available','artifact':pdf})
            self.assertEqual(result['components']['supplementary']['status'],'source_page')
            page.close.assert_called_once_with()

    def test_name_candidates_and_explicit_pdf_keep_the_publisher_contract(self):
        from aps_institutional import APSInstitutional
        from publishers import PROFILES,Publisher
        from dataclasses import replace
        profile=replace(next(p for p in PROFILES if p.source=='aps'),source='aps-institutional')
        adapter=APSInstitutional(None,SimpleNamespace(),profile)
        candidates={'status':'selection_required','source':'aps-institutional','received':2,'records':{'ref':'candidates'}}
        with patch.object(Publisher,'fetch',return_value=candidates):
            self.assertIs(adapter.fetch('Group Algebra',parts=['metadata']),candidates)
        pdf={'status':'ok','source':'aps-institutional','components':{'fulltext':{'status':'available','artifact':{'ref':'pdf'}}}}
        with patch.object(Publisher,'fetch',return_value=pdf),patch.object(adapter,'document') as document:
            self.assertIs(adapter.fetch('https://journals.aps.org/rmp/pdf/10.1103/RevModPhys.39.259',parts=['fulltext']),pdf)
        document.assert_not_called()


if __name__=='__main__':unittest.main()

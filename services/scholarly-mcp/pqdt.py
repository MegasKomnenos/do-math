"""ProQuest dissertations through its institutional browser UI and native RIS export."""
import json
import re
from collections import Counter
from urllib.parse import urljoin, urlsplit, unquote

from bs4 import BeautifulSoup

from browser_adapters import browser_download, clean_html, goto_source, require_source_url
from scholarly import ServiceError, encoded, extract_artifact, bibliography

SORTS={'relevance':'Relevance','oldest':'Oldest first','recent':'Most recent first'}
FACETS={'subjects':'mainSubject','index_terms':'authkeyword','universities':'schoolName','locations':'schoollocation','languages':'language'}
EXPORT_CONTENT={'citation_abstract_indexing':'CITATIONABSTRACTINDEX','citation_abstract':'CITATIONABSTRACT'}
EXPORT_FORMATS={
    'ris':('ProEndRefMgr','ProEndRefMgr','application/x-research-info-systems',('research-info-systems',)),
    'endnote':('EndNote','ProEndRefMgr','application/x-research-info-systems',('research-info-systems',)),
    'text':('Text','Text','text/plain',('text/plain',)),
    'rtf':('Rtf','Rtf','application/rtf',('rtf','msword')),
    'xls':('Excel','Excel','application/vnd.ms-excel',('excel','spreadsheet')),
    'pdf':('Pdf','Pdf','application/pdf',('application/pdf',))}


def search_options(options):
    if not isinstance(options,dict) or set(options)-{'sort','publication_date','facets','export_content'}:
        raise ServiceError('invalid_options','Use documented PQDT sort, publication date, facets and export content')
    sort=options.get('sort','relevance');content=options.get('export_content','citation_abstract_indexing')
    if not isinstance(sort,str) or sort not in SORTS or not isinstance(content,str) or content not in EXPORT_CONTENT:
        raise ServiceError('invalid_options','Use a current PQDT sort and export content value')
    result={'sort':sort,'export_content':content}
    if 'publication_date' in options:
        value=options['publication_date']
        if not isinstance(value,dict) or set(value)!= {'from','to'} or any(not isinstance(value[key],str) for key in value):
            raise ServiceError('invalid_options','PQDT publication_date requires from and to ISO dates')
        from datetime import date
        try:first,last=(date.fromisoformat(value[key]) for key in ('from','to'))
        except ValueError:raise ServiceError('invalid_options','PQDT publication dates must be YYYY-MM-DD') from None
        if last<first:raise ServiceError('invalid_options','PQDT publication date range is reversed')
        result['publication_date']={'from':value['from'],'to':value['to']}
    if 'facets' in options:
        groups=options['facets']
        if not isinstance(groups,dict) or set(groups)-set(FACETS):
            raise ServiceError('invalid_options','Use documented PQDT result facet groups')
        normalized={}
        for field,value in groups.items():
            if not isinstance(value,dict) or set(value)-{'include','exclude'}:
                raise ServiceError('invalid_options','PQDT facets use include and exclude arrays')
            item={}
            for mode in ('include','exclude'):
                values=value.get(mode,[])
                cleaned=[entry.strip() for entry in values] if isinstance(values,list) and all(isinstance(entry,str) for entry in values) else []
                if values and (not cleaned or any(not entry for entry in cleaned) or len(set(cleaned))!=len(cleaned)):
                    raise ServiceError('invalid_options','PQDT facet arrays need unique nonempty current labels')
                item[mode]=cleaned
            if set(item['include'])&set(item['exclude']):
                raise ServiceError('invalid_options','The same PQDT facet label cannot be included and excluded')
            if len(item['include'])+len(item['exclude'])>20:
                raise ServiceError('invalid_options','Use at most 20 include and exclude values in one PQDT facet')
            if item['include'] or item['exclude']:normalized[field]=item
        if normalized:result['facets']=normalized
    return result


def _normalized(value):return re.sub(r'[^\w]+','',value.casefold())


def ensure_export_safe(data,sanitizer):
    for secret in sanitizer.secrets:
        if secret and secret.encode() in data:raise ServiceError('sensitive_artifact','PQDT export contains a protected credential value')
    if re.search(br'(?i)(?:access_token|auth_token|sessionid|jsessionid)=',data):
        raise ServiceError('sensitive_artifact','PQDT export contains an authentication marker')


def validate_native_export(data,format,selected):
    if not data:raise ServiceError('unexpected_content','PQDT native export is empty')
    identifiers={str(row['id']) for row in selected};titles={_normalized(row['title']) for row in selected}
    if len(identifiers)!=len(selected) or len(titles)!=len(selected):
        raise ServiceError('export_identity_mismatch','PQDT selected documents are not unique')
    if format in ('ris','endnote'):
        records=bibliography(data,'application/x-research-info-systems')
        found_ids={(row.get('fields',{}).get('an') or [None])[0] for row in records}
        found_titles={_normalized((row.get('fields',{}).get('t1') or [''])[0]) for row in records}
        sequence=[((row.get('fields',{}).get('an') or [None])[0],_normalized((row.get('fields',{}).get('t1') or [''])[0])) for row in records]
        context={'records':len(records)}
    elif format=='text':
        if data.lstrip().startswith(b'<'):raise ServiceError('unexpected_content','PQDT text export returned markup')
        text=data.decode('utf-8-sig');found_ids=set(re.findall(r'/docview/(\d+)',text));found_titles={title for title in titles if title in _normalized(text)}
        context={'records':len(found_ids)}
    elif format=='rtf':
        if not data.lstrip().startswith(br'{\rtf1'):raise ServiceError('invalid_document','PQDT RTF export has no RTF signature')
        from richtext import rtf_text
        text=rtf_text(data);found_ids={value.decode() for value in re.findall(br'/docview/(\d+)',data)};found_titles={title for title in titles if title in _normalized(text)}
        context={'records':len(found_ids)}
    elif format=='bibtex':
        text=data.decode('utf-8-sig')
        if not re.match(r'\s*@(?:phdthesis|mastersthesis)\s*\{',text,re.I) or text.count('{')!=text.count('}'):
            raise ServiceError('invalid_document','PQDT Cite did not return a balanced thesis BibTeX payload')
        records=bibliography(data,'application/x-bibtex')
        found_ids=set(re.findall(r'/docview/(\d+)',text));sequence=[]
        for row in records:
            ids=set(re.findall(r'/docview/(\d+)',json.dumps(row)))
            sequence.append((next(iter(ids)) if len(ids)==1 else None,_normalized(row.get('title',''))))
        found_titles={_normalized(row.get('title','')) for row in records}
        if any(row.get('id')!='' or 'citation_key_missing' not in row.get('parse_warnings',[]) for row in records):
            raise ServiceError('invalid_document','PQDT BibTeX did not preserve its missing citation key warning')
        context={'records':len(records),'parse_warnings':['citation_key_missing']}
    elif format=='pdf':
        if not data.startswith(b'%PDF-'):raise ServiceError('invalid_document','PQDT bibliography PDF has no PDF signature')
        import pymupdf
        try:
            with pymupdf.open(stream=data,filetype='pdf') as document:
                text='\n'.join(page.get_text() for page in document);uris=[link.get('uri','') for page in document for link in page.get_links() if link.get('uri')];pages=len(document)
        except Exception:raise ServiceError('invalid_document','PQDT bibliography PDF cannot be read') from None
        found_ids={identifier for uri in uris for identifier in re.findall(r'/docview/(\d+)',uri)};found_titles={title for title in titles if title in _normalized(text)}
        context={'records':len(found_ids),'pages':pages}
    elif format=='xls':
        if not data.startswith(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'):
            raise ServiceError('invalid_document','PQDT XLS export has no OLE workbook signature')
        import xlrd
        try:
            book=xlrd.open_workbook(file_contents=data,on_demand=True);sheet=book.sheet_by_index(0)
            headers=[str(sheet.cell_value(0,column)) for column in range(sheet.ncols)]
            values=[[str(sheet.cell_value(row,column)) for column in range(sheet.ncols)] for row in range(1,sheet.nrows)]
            sheets,rows_count,columns=book.nsheets,sheet.nrows,sheet.ncols;book.release_resources()
        except Exception:raise ServiceError('invalid_document','PQDT XLS export cannot be read') from None
        if sheets!=1 or not {'Title','StoreId','DocumentURL'}<=set(headers) or len(values)!=len(selected):
            raise ServiceError('export_range_mismatch','PQDT XLS rows or native columns differ from the selection')
        found_ids={identifier for identifier in identifiers if sum(any(identifier in cell for cell in row) for row in values)==1}
        found_titles={title for title in titles if sum(any(title in _normalized(cell) for cell in row) for row in values)==1}
        context={'records':len(values),'rows':rows_count,'columns':columns}
    else:
        raise ServiceError('invalid_export','Use a validated PQDT native export format')
    if selected and context.get('records')!=len(selected):
        raise ServiceError('export_range_mismatch','PQDT native export record count differs from the selected document count')
    if selected and format in ('ris','endnote','bibtex') and sequence!=[(str(row['id']),_normalized(row['title'])) for row in selected]:
        raise ServiceError('export_identity_mismatch','PQDT native export record order differs from the selected document order')
    if selected and (found_ids!=identifiers or found_titles!=titles):
        raise ServiceError('export_identity_mismatch','PQDT native export does not match the selected document ids and titles')
    if not selected and not context.get('records'):
        raise ServiceError('unexpected_content','PQDT native export contains no records')
    return context


def pqdt_facets(raw):
    soup=BeautifulSoup(raw,'html.parser');result=[]
    for field,native in FACETS.items():
        candidates=[]
        for anchor in soup.select(f'#{native}-zone a.filter_{native}'):
            text=re.sub(r'[\u200e\u200f]','',anchor.get_text(' ',strip=True))
            match=re.fullmatch(r'(.+?)\s*\(([\d,]+)\)',text)
            if not match:raise ServiceError('invalid_response','PQDT returned a malformed result facet candidate',field=field)
            label=match[1].strip();candidates.append({'value':label,'label':label,'count':int(match[2].replace(',',''))})
        if candidates:result.append({'field':field,'native_group':native,'candidates':candidates,'complete':False})
    return result


def pqdt_page(raw):
    soup=BeautifulSoup(raw,'html.parser');active=soup.select('ul.pagination li.active')
    if not active:return 1
    if len(active)!=1 or not re.fullmatch(r'\d+',active[0].get_text(' ',strip=True)):
        raise ServiceError('invalid_response','PQDT pagination has no unique current page')
    return int(active[0].get_text(' ',strip=True))


def is_zero_page(raw):
    node=BeautifulSoup(raw,'html.parser').select_one('#searchTerm-label')
    return bool(node and re.fullmatch(r'Your search returned no results:\s*Enter your search terms',node.get_text(' ',strip=True),re.I))


def _facet_expression(value):
    include=value.get('include',[]);exclude=value.get('exclude',[])
    def clause(items):return items[0] if len(items)==1 else '( '+' OR '.join(items)+' )'
    parts=[]
    if include:parts.append(clause(include))
    if exclude:parts.append('NOT '+clause(exclude))
    return ' '.join(parts)


def validate_facet_transition(before,after,requested,field):
    if Counter(after)!=Counter(before)+Counter([_facet_expression(requested)]):
        raise ServiceError('filter_mismatch','PQDT facet application did not add exactly the selected group expression',field=field)


def validate_filter_page(raw,options):
    soup=BeautifulSoup(raw,'html.parser');sort=soup.select_one('#sortType-combo')
    observed=' '.join(sort.get_text(' ',strip=True).split()) if sort else ''
    if observed and observed!=SORTS[options.get('sort','relevance')]:raise ServiceError('filter_mismatch','PQDT retained another result sort')
    expected=[]
    if 'publication_date' in options:
        first,last=(options['publication_date'][key] for key in ('from','to'));expected.append(first+' - '+last)
        starts=soup.select_one('#startingDate');ends=soup.select_one('#endingDate')
        if starts is None or ends is None or starts.get('value')!=first or ends.get('value')!=last:
            raise ServiceError('filter_mismatch','PQDT did not retain the publication date range')
    for value in options.get('facets',{}).values():expected.append(_facet_expression(value))
    applied=[' '.join(node.get_text(' ',strip=True).split()) for node in soup.select('span.applied')]
    if Counter(applied)!=Counter(expected):raise ServiceError('filter_mismatch','PQDT did not retain every include and exclude filter occurrence')


def apply_search_options(page,options,facets):
    def navigate(action):
        with page.expect_navigation(wait_until='load',timeout=60000):action()
        page.locator('#pqResultsCount').wait_for(timeout=60000);page.wait_for_timeout(1000)
    current=' '.join(page.locator('#sortType-combo').inner_text().split())
    if current!=SORTS[options['sort']]:
        def sort_action():
            page.locator('#sortType-combo').click();page.get_by_role('option',name=SORTS[options['sort']],exact=True).click()
        navigate(sort_action)
    if 'publication_date' in options:
        value=options['publication_date'];page.locator('#startingDate').fill(value['from']);page.locator('#endingDate').fill(value['to']);page.wait_for_timeout(500)
        if page.locator('#startingDate').input_value()!=value['from'] or page.locator('#endingDate').input_value()!=value['to']:
            raise ServiceError('filter_state_mismatch','PQDT date controls did not retain the requested range')
        navigate(lambda:page.locator('#dateRangeSubmit').click())
    for field,native in FACETS.items():
        if field not in options.get('facets',{}):continue
        requested=options['facets'][field]
        header=page.locator('#language-header') if native=='language' else page.locator(f'#{native}-hzone a.filter_header')
        if not header.count():raise ServiceError('selection_required','PQDT did not return this facet for the current result set',status='selection_required',field=field)
        if 'expanded' not in (header.get_attribute('class') or ''):header.click()
        zone=page.locator(f'#{native}-zone');zone.get_by_text('More',exact=True).filter(visible=True).first.click()
        controls=page.locator('input[type="checkbox"][title^="Include "]:visible,input[type="checkbox"][title^="Exclude "]:visible,input[type="checkbox"][aria-label^="Include "]:visible,input[type="checkbox"][aria-label^="Exclude "]:visible')
        controls.first.wait_for(timeout=45000)
        group=next((item for item in facets if item['field']==field),None)
        if group is None:
            group={'field':field,'native_group':native,'candidates':[],'complete':False};facets.append(group)
        known={item['value'] for item in group['candidates']}
        discovered={}
        for index in range(controls.count()):
            label=controls.nth(index).get_attribute('aria-label') or controls.nth(index).get_attribute('title') or '';match=re.fullmatch(r'(Include|Exclude) (.+)',label)
            if match:discovered.setdefault(match[2],set()).add(match[1].casefold())
        for value,modes in discovered.items():
            if value not in known:group['candidates'].append({'value':value,'label':value,'count':None,'modes':sorted(modes),'basis':'native_more_dialog'})
        group['complete']=True
        for mode in ('include','exclude'):
            for value in requested[mode]:
                control=page.get_by_role('checkbox',name=mode.title()+' '+value,exact=True).filter(visible=True)
                if control.count()!=1:
                    raise ServiceError('selection_required','Select an exact current PQDT facet value',status='selection_required',field=field,
                                       candidates=[item['value'] for item in group['candidates'][:50]])
                control.check()
                opposite='Exclude' if mode=='include' else 'Include'
                inverse=page.get_by_role('checkbox',name=opposite+' '+value,exact=True).filter(visible=True)
                if not control.is_checked() or inverse.count()!=1 or inverse.is_checked():
                    raise ServiceError('filter_state_mismatch','PQDT facet control did not retain its group and include/exclude mode',field=field)
        before=Counter(' '.join(node.split()) for node in page.locator('span.applied').all_inner_texts())
        navigate(lambda:page.locator('a[id^="submit_"]').filter(visible=True).first.click())
        after=Counter(' '.join(node.split()) for node in page.locator('span.applied').all_inner_texts())
        validate_facet_transition(before,after,requested,field)
    observed=' '.join(page.locator('#sortType-combo').inner_text().split())
    if observed!=SORTS[options['sort']]:raise ServiceError('filter_mismatch','PQDT did not retain the requested sort')
    validate_filter_page(page.content(),options)


def clear_result_filters(page):
    for _ in range(20):
        applied=page.locator('span.applied').filter(visible=True)
        if not applied.count():return
        clear=applied.first.locator('a[title^="Clear "]').filter(visible=True).first
        if not clear.count():raise ServiceError('filter_reset_failed','PQDT retained a result filter without its clear control')
        with page.expect_navigation(wait_until='load',timeout=60000):clear.click()
        page.locator('#pqResultsCount').wait_for(timeout=60000);page.wait_for_timeout(500)
    raise ServiceError('filter_reset_failed','PQDT retained too many result filters to reset safely')


def load_visible_facets(page):
    for native in FACETS.values():
        header=page.locator('#language-header') if native=='language' else page.locator(f'#{native}-hzone a.filter_header')
        zone=page.locator(f'#{native}-zone')
        if not zone.locator(f'a.filter_{native}').count():
            if not header.count():continue
            if 'expanded' not in (header.get_attribute('class') or ''):header.click()
            try:zone.locator(f'a.filter_{native}').first.wait_for(timeout=10000)
            except Exception:pass
    return pqdt_facets(page.content())


def pqdt_records(raw, base):
    soup = BeautifulSoup(raw, "html.parser")
    heading = soup.select_one("#pqResultsCount")
    match = re.search(r"([\d,]+)\s+results?", heading.get_text(" ", strip=True) if heading else "", re.I)
    if not match:
        raise ServiceError("invalid_response", "PQDT page contains no recognized result count")
    rows = []
    for item in soup.select("li.resultItem"):
        title = next((a for a in item.select("a.previewTitle") if a.get_text(strip=True)), None)
        found = re.search(r"/docview/(\d+)", title.get("href", "") if title else "")
        if not found:
            raise ServiceError("invalid_response", "PQDT result contains no document-bound title link")
        links = [urljoin(base, e["href"]) for e in item.select('a[href*="/fulltextPDF/"]') if "/docview/" + found[1] + "/" in e["href"]]
        rows.append({"id": found[1], "title": title.get_text(" ", strip=True), "url": urljoin(base, title["href"]),
            "pdf_page": links[0] if links else None, "listing": item.get_text("\n", strip=True)})
    if len({row['id'] for row in rows})!=len(rows):raise ServiceError('invalid_response','PQDT result page contains duplicate document identities')
    return rows, int(match[1].replace(",", ""))


def supplemental_records(raw,base):
    soup=BeautifulSoup(raw,'html.parser')
    counts=[int(m[1]) for h in soup.select('h5') if (m:=re.search(r'Document includes (\d+) supplemental file',h.get_text(' ',strip=True)))]
    if len(counts)!=1:
        raise ServiceError('invalid_response','PQDT did not provide one supplemental file count')
    rows=[]; prefix='/docview.supplementalfiles.termsofusesupplementalfiles:downloadfile/'
    for item in soup.select('.suppFiles'):
        label=item.select_one('a.termUse_link')
        links=[urljoin(base,a['href']) for a in item.select('.TermUseLayer a[href]') if urlsplit(urljoin(base,a['href'])).path.startswith(prefix)]
        if label is None or len(links)!=1:
            raise ServiceError('invalid_response','PQDT supplemental item did not provide one file action')
        name=label.get_text(' ',strip=True)
        encoded_name=urlsplit(links[0]).path[len(prefix):].split('/')[0]
        observed=unquote(re.sub(r'\$([0-9a-f]{2})',lambda m:'%'+m[1],encoded_name,flags=re.I))
        if name!=observed:
            raise ServiceError('identity_mismatch','PQDT file action and displayed filename differ')
        rows.append({'index':len(rows),'name':name,'action':links[0]})
    if len(rows)!=counts[0]:
        raise ServiceError('incomplete_response','PQDT supplemental file count differs from its controls')
    return rows,counts[0]


class PQDT:
    source = "pqdt"
    hosts = ("www.proquest.com", "www-proquest-com.libproxy.knu.ac.kr")
    media_hosts = hosts + ("media.proquest.com", "media-proquest-com.libproxy.knu.ac.kr")

    def __init__(self, store, gateway):
        self.store, self.gateway = store, gateway
        self.known = {}

    def page(self):
        page = self.gateway.open(self.source, "PQDT", self.hosts, "#searchTerm, #pqResultsCount")
        page.wait_for_load_state("domcontentloaded", timeout=45000)
        if not page.evaluate("document.cookie.includes('OptanonAlertBoxClosed=')"):
            page.wait_for_function("typeof OneTrust !== 'undefined' && typeof OneTrust.RejectAll === 'function'", timeout=30000)
            page.locator("#onetrust-banner-sdk").wait_for(timeout=30000)
            page.evaluate("OneTrust.RejectAll()")
            page.locator(".onetrust-pc-dark-filter").wait_for(state="hidden", timeout=20000)
        return page

    def native_export(self,page,selected,format,content='citation_abstract_indexing'):
        if format not in EXPORT_FORMATS or content not in EXPORT_CONTENT:
            raise ServiceError('invalid_export','Use a current downloadable PQDT format and content selection')
        previous = set(self.gateway.context.pages)
        page.locator("#allSaveOptionsLink").click()
        page.locator("#allSaveOptionsOverlay").wait_for()
        menu,mode,media,media_markers=EXPORT_FORMATS[format]
        page.locator(f'a[href*="selectformat/{menu}"]').filter(visible=True).first.click()
        overlay=page.locator('#saveasExportLayerOverlay');overlay.wait_for(state='visible',timeout=30000)
        output=overlay.locator('#exportMode');output.select_option(mode)
        if output.input_value()!=mode:raise ServiceError('export_state_mismatch','PQDT did not retain the requested output format')
        scope=overlay.locator('#citationTypeSelect');scope.select_option(EXPORT_CONTENT[content])
        if scope.input_value()!=EXPORT_CONTENT[content]:raise ServiceError('export_state_mismatch','PQDT did not retain the requested export content')
        button = overlay.locator('a[id^="submitButton_"],button[type="submit"]').filter(visible=True).first
        button.wait_for(timeout=30000)
        with self.gateway.context.expect_event("response", predicate=lambda r:urlsplit(r.url).hostname in self.hosts and r.status==200 and
                any(marker in r.headers.get('content-type','').casefold() for marker in media_markers), timeout=60000) as pending:
            button.click()
        response = pending.value
        data = response.body()
        if not data:raise ServiceError('unexpected_content','PQDT returned an empty final export response')
        ensure_export_safe(data,self.store.sanitizer)
        try:context=validate_native_export(data,format,selected)
        except ServiceError as error:
            error.result['source_export']=self.store.put(data,media,self.source,response.url,preserve_bytes=True,role='source_export',
                requested_format=format,selected_ids=[row['id'] for row in selected])
            raise
        finally:
            for popup in set(self.gateway.context.pages) - previous:popup.close()
        native = self.store.put(data,media,self.source,response.url,preserve_bytes=format in ('rtf','xls','pdf'),
            role="native_bibliography_export",format=format,export_content=content,selected_ids=[row['id'] for row in selected],**context)
        return native

    def native_bibtex(self,page,selected):
        page.locator('#allSaveOptionsLink').click();page.locator('#allSaveOptionsOverlay').wait_for(state='visible',timeout=30000)
        page.locator('#allSaveOptionsCiteLink').click();style=page.locator('#citeStyle_citethis');style.wait_for(state='visible',timeout=30000)
        style.select_option('BIB_TEX')
        if style.input_value()!='BIB_TEX':raise ServiceError('export_state_mismatch','PQDT Cite did not retain the BibTeX style')
        page.wait_for_function("() => document.querySelector('#selectable_citethis')?.innerText.trim().startsWith('@')",timeout=30000)
        data=page.locator('#selectable_citethis').inner_text().encode('utf-8')
        ensure_export_safe(data,self.store.sanitizer)
        try:context=validate_native_export(data,'bibtex',selected)
        except ServiceError as error:
            error.result['source_export']=self.store.put(data,'application/x-bibtex',self.source,page.url,preserve_bytes=True,role='source_export',
                requested_format='bibtex',selected_ids=[row['id'] for row in selected])
            done=page.locator('#citeThisDoneButton')
            if done.count() and done.is_visible():done.click()
            raise
        artifact=self.store.put(data,'application/x-bibtex',self.source,page.url,role='native_bibliography_export',format='bibtex',
            export_content='fixed_cite_bibtex',selected_ids=[row['id'] for row in selected],provider_empty_citation_key=True,**context)
        done=page.locator('#citeThisDoneButton')
        if done.count() and done.is_visible():done.click()
        return artifact

    def citation(self, page, selected=None, content='citation_abstract_indexing'):
        native=self.native_export(page,selected or [],'ris',content)
        rows = extract_artifact(self.store, native["ref"], count=1000)["items"]
        for row in rows:
            fields = row["fields"]
            row.update(id=(fields.get("an") or [None])[0], title=(fields.get("t1") or [None])[0])
        return rows, native

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        if not isinstance(query,str) or not query.strip():raise ServiceError('invalid_query','Provide a nonempty PQDT native query')
        if type(start) is not int or start < 0 or type(limit) is not int or not 1 <= limit <= 1000:
            raise ServiceError("invalid_range", "PQDT requires start >= 0 and limit 1..1000")
        normalized=search_options(options)
        if 'export_content' in options and export not in EXPORT_FORMATS:
            raise ServiceError('invalid_options','PQDT export_content applies only to the six downloadable bibliography formats')
        if export=='bibtex':normalized['export_content']='fixed_cite_bibtex'
        if cursor or export not in (None,"json","html","bibtex",*EXPORT_FORMATS):
            if export in ('refworks','noodletools','easybib'):
                raise ServiceError('external_import_required','This PQDT option transfers records to an external account; use a downloadable source format',status='unsupported')
            raise ServiceError("invalid_options", "PQDT uses numeric offsets and documented downloadable export formats")
        page = self.page()
        if page.locator('#pqResultsCount').count():clear_result_filters(page)
        goto_source(page, "https://" + urlsplit(page.url).hostname + "/pqdtglobal", self.hosts, wait_until="load", timeout=45000)
        page.locator("#searchTerm").fill(query)
        page.locator("#searchTerm").press("Tab")
        with page.expect_navigation(wait_until="load", timeout=60000):
            page.locator("#expandedSearch").click()
        page.locator("#pqResultsCount,#searchTerm-label").wait_for(timeout=60000)
        initial=page.content()
        if not page.locator('#pqResultsCount').count():
            if not is_zero_page(initial):raise ServiceError('invalid_response','PQDT returned no recognized result state')
            evidence=self.store.put(clean_html(initial,self.store.sanitizer),'text/html',self.source,page.url,role='search_zero_page',query=query,options=normalized,total=0)
            records=self.store.put(b'[]','application/json',self.source,page.url,role='records',query=query,start=start,requested=limit,total=0)
            facets=self.store.put(b'[]','application/json',self.source,page.url,role='search_facets',query=query,options=normalized,total=0)
            exported={'artifacts':[evidence]} if export=='html' else records
            return {'status':'not_found','source':self.source,'query':query,'options':normalized,'start':start,'requested':limit,'received':0,'total':0,
                    'has_more':False,'next':None,'records':records,'export':exported,'native_citation':None,'evidence':[evidence],'facets':facets,
                    'filter_state':{'status':'base_query_empty_before_result_filters'},'preview':[]}
        clear_result_filters(page)
        # Marked items persist across searches. Clear this server's earlier selection.
        clear = page.locator("#selecteditemsclear_link")
        if clear.count() and clear.is_visible():
            clear.click()
            dialog = page.locator("#selecteditemsclear_confirm_clear_overlay")
            dialog.wait_for()
            dialog.get_by_role("button", name="Yes", exact=True).click()
            dialog.wait_for(state="hidden")
        _,base_total=pqdt_records(page.content(),page.url)
        facet_catalog=load_visible_facets(page) if base_total else []
        apply_search_options(page,normalized,facet_catalog)
        facets_artifact=self.store.put(encoded(facet_catalog),'application/json',self.source,page.url,role='search_facets',query=query,options=normalized,
            scope='Current visible candidates plus requested groups expanded through the native More dialog')
        rows, evidence, offset, total = [], [], 0, None
        while True:
            require_source_url(page.url, self.hosts)
            raw = page.content();validate_filter_page(raw,normalized)
            native, observed = pqdt_records(raw, page.url)
            if total is not None and observed != total:
                raise ServiceError("range_mismatch", "PQDT result count changed during pagination")
            total = observed
            expected=min(20,max(0,total-offset))
            if len(native)!=expected or native and pqdt_page(raw)!=offset//20+1:
                raise ServiceError('range_mismatch','PQDT result rows or current page do not match the requested window')
            evidence.append(self.store.put(clean_html(raw, self.store.sanitizer), "text/html", self.source, page.url, role="search_page", query=query, options=normalized, offset=offset, total=total))
            for i, row in enumerate(native):
                if start <= offset + i < start + limit:
                    control = page.locator("li.resultItem").nth(i).locator('input.marked_list_checkbox')
                    if not control.is_checked():
                        control.focus()
                        control.press("Space")
                        page.wait_for_function("e => e.checked", arg=control.element_handle())
                    rows.append(row)
            offset += len(native)
            if offset >= min(total, start + limit) or not native:
                break
            next_page = page.locator('a[title="Next Page"],a[aria-label="Next Page"],a[title="Next page"],a[aria-label="Next page"],a[title="Next"],a[rel="next"]').filter(visible=True)
            if not next_page.count():
                raise ServiceError("pagination_control_missing", "PQDT next-page control could not be identified", evidence=evidence)
            with page.expect_navigation(wait_until="load", timeout=60000):
                next_page.first.click()
        citations, exported, export_errors = [], None, []
        if rows:
            ris_content=normalized['export_content'] if export=='ris' else 'citation_abstract_indexing'
            citations, native_ris = self.citation(page,rows,ris_content)
            if {row["id"] for row in rows} != {row["id"] for row in citations} or len(rows) != len(citations):
                raise ServiceError("export_identity_mismatch", "PQDT RIS records do not match the selected documents", evidence=native_ris)
            by_id = {row["id"]: row for row in citations}
            for row in rows:
                row.update(bibliography=by_id[row["id"]])
                self.known[row["id"]] = (row, native_ris)
            if export=='ris':exported=native_ris
            elif export in EXPORT_FORMATS or export=='bibtex':
                try:exported=self.native_bibtex(page,rows) if export=='bibtex' else self.native_export(page,rows,export,normalized['export_content'])
                except ServiceError as error:export_errors.append(error.result)
                except Exception as error:export_errors.append({'status':'error','code':'native_export_failed','error_type':type(error).__name__})
        else:native_ris=None
        artifact = self.store.put(encoded(rows), "application/json", self.source, page.url, role="records", query=query, start=start, requested=limit, total=total)
        if export in (None,'json'):exported=artifact
        elif export=='html':exported={'artifacts':evidence}
        elif export_errors:exported={'status':'partial','errors':export_errors}
        more = start + len(rows) < total
        return {"status": "partial" if export_errors else "ok" if rows else "not_found", "source": self.source, "query": query,"options":normalized,"start": start,
            "requested": limit, "received": len(rows), "total": total, "has_more": more,
            "next": {"start": start + len(rows)} if more else None, "records": artifact,
            "export":exported,"native_citation":native_ris,"evidence":evidence,"facets":facets_artifact,
            "filter_state":{key:normalized[key] for key in ('sort','publication_date','facets') if key in normalized},
            "preview": [{k: r[k] for k in ("id", "title")} for r in rows[:3]]}

    def supplementary(self,identifier,page):
        goto_source(page,'https://'+urlsplit(page.url).hostname+'/pqdtglobal/docview/'+identifier,self.hosts,wait_until='domcontentloaded',timeout=45000)
        page.locator('#docview-nav').wait_for(state='attached',timeout=30000)
        tab=page.locator('#addFlashPageParameterformat_supplementalFiles')
        if not tab.count():
            source=self.store.put(clean_html(page.content(),self.store.sanitizer),'text/html',self.source,page.url,role='document_page',target=identifier)
            return {'status':'source_page','artifact':source,'reason':'No Supplemental files tab is exposed on this document page'}
        tab.click();require_source_url(page.url,self.hosts)
        if not re.search(r'/docview/'+re.escape(identifier)+r'/supplementalFiles(?:/|$)',urlsplit(page.url).path):
            raise ServiceError('identity_mismatch','PQDT supplemental tab belongs to a different document')
        page.locator('h5').filter(has_text=re.compile(r'Document includes \d+ supplemental file')).wait_for(state='attached',timeout=30000)
        raw=page.content();rows,total=supplemental_records(raw,page.url)
        source=self.store.put(clean_html(raw,self.store.sanitizer),'text/html',self.source,page.url,role='supplementary_page',target=identifier)
        index=self.store.put(encoded([{k:v for k,v in row.items() if k!='action'} for row in rows]),'application/json',self.source,page.url,
            role='supplementary_index',target=identifier,parent_ref=source['ref'])
        files=[]
        import io,zipfile,mimetypes
        for row in rows:
            item={k:v for k,v in row.items() if k!='action'}
            try:
                require_source_url(row['action'],self.hosts)
                data,media,url=browser_download(self.gateway.context,row['action'],self.media_hosts)
                if media in ('text/html','application/xhtml+xml') or data.lstrip().lower().startswith((b'<html',b'<!doctype html')):
                    raise ServiceError('unexpected_content','PQDT supplemental action returned HTML')
                name=row['name'].lower();extra={}
                if name.endswith('.png') and not data.startswith(b'\x89PNG\r\n\x1a\n'):
                    raise ServiceError('invalid_document','PQDT PNG action returned no PNG file')
                if name.endswith('.zip'):
                    if not zipfile.is_zipfile(io.BytesIO(data)):raise ServiceError('invalid_document','PQDT ZIP action returned no readable archive')
                    media='application/zip'
                if name.endswith('.pdf'):
                    if not data.startswith(b'%PDF-'):raise ServiceError('invalid_document','PQDT PDF action returned no PDF')
                    import pymupdf
                    with pymupdf.open(stream=data,filetype='pdf') as pdf:extra['pages']=len(pdf)
                    media='application/pdf'
                if media=='application/octet-stream':media=mimetypes.guess_type(row['name'])[0] or media
                file=self.store.put(data,media,self.source,url,preserve_bytes=True,role='supplementary_file',target=identifier,filename=row['name'],parent_ref=index['ref'],**extra)
                files.append({**item,'status':'available','artifact':file})
            except ServiceError as exc:files.append({**item,**exc.result})
            except Exception as exc:files.append({**item,'status':'error','code':'supplementary_download_failed','error_type':type(exc).__name__})
        return {'status':'available' if files and all(f['status']=='available' for f in files) else 'partial' if files else 'not_found',
                'files':files,'index':index,'source_page':source,'discovered':total,'received':sum(f['status']=='available' for f in files)}

    def fetch(self, target, *, parts):
        if set(parts) - {"metadata", "abstract", "fulltext", "supplementary", "export"}:
            raise ServiceError("invalid_parts", "Unknown requested content")
        if target.isdigit():
            identifier = target
        elif target.startswith(("http://", "https://")):
            parsed = urlsplit(target)
            found = re.search(r"/docview/(\d+)", parsed.path)
            if parsed.hostname not in self.hosts or not found:
                raise ServiceError("source_boundary", "Use a PQDT docview identifier or document URL")
            identifier = found[1]
        else:
            result = self.search('TI("' + target.replace('"', " ") + '")', options={}, limit=20)
            result["status"] = "selection_required" if result["received"] else "not_found"
            return result
        page = self.page()
        if identifier not in self.known:
            goto_source(page, "https://" + urlsplit(page.url).hostname + "/pqdtglobal/docview/" + identifier, self.hosts, wait_until="domcontentloaded", timeout=45000)
            records, native = self.citation(page)
            if len(records) != 1 or records[0]["id"] != identifier:
                raise ServiceError("identity_mismatch", "PQDT document export did not match the target", evidence=native)
            record = {"id": identifier, "title": records[0]["title"], "bibliography": records[0], "url": page.url}
            self.known[identifier] = (record, native)
        record, native = self.known[identifier]
        artifact = self.store.put(encoded([record]), "application/json", self.source, record["url"], role="records", target=identifier)
        components = {}
        for part in parts:
            if part in ("metadata", "export"):
                components[part] = {"status": "available", "artifact": native if part == "export" else artifact}
            elif part == "abstract":
                components[part] = {"status": "available", "artifact": artifact} if record["bibliography"]["fields"].get("ab") else {"status": "not_found", "reason": "Native RIS has no abstract"}
            elif part == "fulltext":
                try:
                    goto_source(page, "https://" + urlsplit(page.url).hostname + "/pqdtglobal/docview/" + identifier + "/fulltextPDF", self.hosts, wait_until="domcontentloaded", timeout=45000)
                    download = page.locator("#downloadPDFLink_MSTAR_" + identifier)
                    download.wait_for(timeout=30000)
                    url = urljoin(page.url, download.get_attribute("href"))
                    data, _, obtained = browser_download(self.gateway.context, url, self.media_hosts)
                    if not data.startswith(b"%PDF-"):
                        raise ServiceError("unexpected_content", "PQDT document control did not return a PDF")
                    import pymupdf
                    with pymupdf.open(stream=data, filetype="pdf") as pdf:
                        pages = len(pdf)
                    fulltext = self.store.put(data, "application/pdf", self.source, obtained, role="fulltext", pages=pages, target=identifier)
                    components[part] = {"status": "available", "artifact": fulltext}
                except ServiceError as error:
                    components[part] = error.result
                except Exception as error:
                    components[part]={'status':'error','code':'fulltext_retrieval_failed','error_type':type(error).__name__}
            else:
                try:components[part]=self.supplementary(identifier,page)
                except ServiceError as exc:components[part]=exc.result
                except Exception as exc:components[part]={'status':'error','code':'supplementary_retrieval_failed','error_type':type(exc).__name__}
        return {"status": "ok" if all(v["status"] == "available" for v in components.values()) else "partial", "source": self.source,
            "target": identifier, "records": artifact, "native_citation": native, "components": components}

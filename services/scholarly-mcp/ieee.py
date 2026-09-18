"""IEEE Xplore Command Search and native exports through KUDOS."""
import json
import re
import time
from urllib.parse import urljoin, urlsplit
from waits import SOURCE_WAIT_MS, SOURCE_WAIT_S

from bs4 import BeautifulSoup

from browser_adapters import browser_download, clean_html, dismiss_cookies, goto_source
from scholarly import ServiceError, bibliography, encoded, failure_details

SORTS={
    'relevance':('Relevance',None),'newest':('Newest','newest'),'oldest':('Oldest','oldest'),
    'most_cited_papers':('Most Cited By Papers','paper-citations'),'most_cited_patents':('Most Cited By Patents','patent-citations'),
    'most_popular':('Most Popular','most-popular'),'publication_title_az':('Publication Title A-Z','pub-title-asc'),
    'publication_title_za':('Publication Title Z-A','pub-title-desc')}
FACET_OPTIONS={
    'content_types':'ContentType','authors':'Author','affiliations':'Affiliation','publication_titles':'PublicationTitle',
    'publishers':'Publisher','supplemental_items':'SupplementalItem','conference_locations':'ConferenceLocation',
    'publication_topics':'PublicationTopics'}
FACET_LABELS={'Author':'Author','Affiliation':'Affiliation','PublicationTitle':'Publication Title','Publisher':'Publisher',
              'SupplementalItem':'Supplemental Items','ConferenceLocation':'Conference Location','PublicationTopics':'Publication Topics'}


def search_options(options):
    if not isinstance(options,dict) or set(options)-({'sort','access','year'}|set(FACET_OPTIONS)):
        raise ServiceError('invalid_options','Use documented IEEE result sort, access, year and facet options')
    sort=options.get('sort','relevance');access=options.get('access','all');year=options.get('year')
    if not isinstance(sort,str) or not isinstance(access,str) or sort not in SORTS or access not in ('all','subscribed','open_access'):
        raise ServiceError('invalid_options','Use a current IEEE sort and access value')
    if year is not None:
        if not isinstance(year,str) or not (match:=re.fullmatch(r'(\d{4})(?:-(\d{4}))?',year.strip())) or match[2] and int(match[2])<int(match[1]):
            raise ServiceError('invalid_options','IEEE year must be YYYY or an ordered YYYY-YYYY range')
    result={'sort':sort,'access':access}
    if year is not None:result['year']=year.strip()
    for option in FACET_OPTIONS:
        if option not in options:continue
        values=options[option]
        cleaned=[value.strip() for value in values] if isinstance(values,list) and all(isinstance(value,str) for value in values) else []
        if not cleaned or any(not value for value in cleaned) or len(set(cleaned))!=len(cleaned):
            raise ServiceError('invalid_options','IEEE facet options need unique nonempty current labels')
        result[option]=cleaned
    return result


def _breadcrumb_values(raw):
    found=set()
    def visit(value):
        if isinstance(value,dict):
            if isinstance(value.get('value'),str):found.add(value['value'])
            if isinstance(value.get('reference'),str):found.add(value['reference'])
            for child in value.get('children',[]):visit(child)
    for item in raw.get('breadCrumbs',[]):visit(item)
    return found


def ieee_facets(raw):
    facets=raw.get('facets');selected=_breadcrumb_values(raw);result=[]
    if not isinstance(facets,list):raise ServiceError('invalid_response','IEEE search response has no native facet list')
    inverse={native:option for option,native in FACET_OPTIONS.items()}
    for group in facets:
        native=group.get('id') if isinstance(group,dict) else None
        if native not in inverse or not isinstance(group.get('children'),list):continue
        candidates=[]
        for child in group['children']:
            if not isinstance(child,dict) or not isinstance(child.get('id'),str) or not child['id'].startswith(native+':') or not isinstance(child.get('name'),str) or type(child.get('numRecords')) is not int:
                raise ServiceError('invalid_response','IEEE returned a malformed native facet candidate')
            value=child['id'][len(native)+1:]
            candidates.append({'value':value,'label':child['name'],'count':child['numRecords'],'selected':child['id'] in selected})
        result.append({'field':inverse[native],'native_group':native,'label':group.get('name'),'active':str(group.get('active')).casefold()=='true','candidates':candidates})
    return result


def remember_facet_candidate(facets,field,value,count):
    group=next((item for item in facets if item['field']==field),None)
    if group is None:return
    if not any(item['value']==value for item in group['candidates']):
        group['candidates'].append({'value':value,'label':value,'count':count,'selected':True,'basis':'native_typeahead'})


def validate_filter_state(raw,options):
    values=_breadcrumb_values(raw);sort=options.get('sort','relevance');expected_sort=SORTS[sort][1]
    observed=raw.get('sortValue')
    if expected_sort is None:
        if observed not in (None,'','relevance'):raise ServiceError('filter_mismatch','IEEE retained another result sort')
    elif observed!=expected_sort:
        raise ServiceError('filter_mismatch','IEEE did not retain the requested result sort')
    access=options.get('access','all')
    if access=='subscribed' and raw.get('subscribedContentApplied') is not True:
        raise ServiceError('filter_mismatch','IEEE did not retain subscribed-content filtering')
    if access=='open_access' and raw.get('records') and any((row.get('accessType') or {}).get('type')!='open-access' for row in raw['records']):
        raise ServiceError('filter_mismatch','IEEE did not retain open-access-only filtering')
    if 'year' in options:
        first,last=(options['year'].split('-',1)+[options['year']])[:2] if '-' in options['year'] else (options['year'],options['year'])
        expected=f'{first}_{last}_Year'
        if expected not in values:raise ServiceError('filter_mismatch','IEEE did not retain the requested publication year range')
    for option,native in FACET_OPTIONS.items():
        if option in options and any(native+':'+value not in values for value in options[option]):
            raise ServiceError('filter_mismatch','IEEE did not retain a requested native result facet',field=option)
    expected_refinements={FACET_OPTIONS[option]+':'+value for option in FACET_OPTIONS for value in options.get(option,[])}
    observed_refinements={value for value in values if any(value.startswith(native+':') and value!=native+':' for native in FACET_OPTIONS.values())}
    if observed_refinements!=expected_refinements:
        raise ServiceError('filter_mismatch','IEEE retained an unrequested native result facet')
    ranges={value for value in values if re.fullmatch(r'\d{4}_\d{4}_Year',value)}
    expected_ranges=set()
    if 'year' in options:
        first,last=options['year'].split('-',1) if '-' in options['year'] else (options['year'],options['year'])
        expected_ranges={f'{first}_{last}_Year'}
    if ranges!=expected_ranges:raise ServiceError('filter_mismatch','IEEE retained an unrequested publication year range')


def validate_request_state(response,options,page_number):
    try:body=response.request.post_data_json
    except Exception:raise ServiceError('invalid_response','IEEE search response has no native request state') from None
    expected={}
    if SORTS[options.get('sort','relevance')][1]:expected['sortType']=SORTS[options['sort']][1]
    if options.get('access')=='subscribed':expected['subscribed']=True
    elif options.get('access')=='open_access':expected['openAccess']=True
    refinements=[FACET_OPTIONS[option]+':'+value for option in FACET_OPTIONS for value in options.get(option,[])]
    if refinements:expected['refinements']=refinements
    if 'year' in options:
        first,last=options['year'].split('-',1) if '-' in options['year'] else (options['year'],options['year'])
        expected['ranges']=[f'{first}_{last}_Year']
    if page_number>1:expected['pageNumber']=str(page_number)
    semantic={'sortType','subscribed','openAccess','refinements','ranges','pageNumber'}
    for key in semantic:
        actual=body.get(key)
        wanted=expected.get(key)
        if key in ('refinements','ranges'):
            if set(actual or [])!=set(wanted or []):raise ServiceError('filter_mismatch','IEEE native request did not retain the requested result state',field=key)
        elif wanted is None and actual not in (None,''):
            raise ServiceError('filter_mismatch','IEEE native request retained an unrequested result state',field=key)
        elif wanted is not None and actual!=wanted:
            raise ServiceError('filter_mismatch','IEEE native request did not retain the requested result state',field=key)


def require_search_response(response):
    if response.status in (401,403):
        raise ServiceError('access_restricted','IEEE restricted this institutional search',status='restricted')
    if response.status!=200:
        raise ServiceError('provider_error','IEEE search failed',http_status=response.status)
    return response


def apply_search_options(page,response,matches,options,facet_catalog):
    """Apply current result controls and return the final native search response."""
    def transition(action):
        with page.expect_response(matches,timeout=SOURCE_WAIT_MS) as pending:action()
        page.wait_for_timeout(750)
        return require_search_response(pending.value)
    def candidates(payload,option):
        group=next((item for item in ieee_facets(payload) if item['field']==option),None)
        return [item['value'] for item in group['candidates']] if group else []
    if options['sort']!='relevance':
        label=SORTS[options['sort']][0]
        def choose_sort():
            page.locator('button.dropdown-toggle.xpl-btn-secondary').filter(visible=True).filter(has_text=re.compile(r'^(?:Relevance|Newest|Oldest|Most Cited|Most Popular|Publication Title)')).first.click()
            page.get_by_text(label,exact=True).filter(visible=True).first.click()
        response=transition(choose_sort)
    if options['access']!='all':
        label='Subscribed Content' if options['access']=='subscribed' else 'Open Access Only'
        response=transition(lambda:page.get_by_text(label,exact=True).filter(visible=True).first.click())
    if 'content_types' in options:
        available=candidates(response.json(),'content_types')
        if any(value not in available for value in options['content_types']):
            raise ServiceError('selection_required','Select current IEEE content-type facet labels',status='selection_required',candidates=available)
        def choose_content():
            for value in options['content_types']:
                page.locator(f'input[id="refinement-ContentType:{value}"]').filter(visible=True).first.check()
            page.locator('xpl-facet-content-type-migr button.xpl-btn-primary').filter(visible=True).first.click()
        response=transition(choose_content)
    for option,native in FACET_OPTIONS.items():
        if option=='content_types' or option not in options:continue
        available=candidates(response.json(),option)
        def choose_facets(option=option,native=native):
            toggle=page.locator(f'#reg-{native}-facet').filter(visible=True).first
            if toggle.get_attribute('aria-expanded')!='true':toggle.click()
            section=toggle.locator('xpath=ancestor::section[1]')
            for value in options[option]:
                choice=section.locator('label').filter(has_text=re.compile(r'^'+re.escape(value)+r'\s*\(')).locator('input[type="checkbox"]')
                if value in available:
                    for _ in range(10):
                        if choice.count() and choice.first.is_visible():break
                        more=section.get_by_text('Show More',exact=True).filter(visible=True)
                        if not more.count():break
                        before=section.locator('input[type="checkbox"]').count();more.first.click();page.wait_for_timeout(500)
                        if section.locator('input[type="checkbox"]').count()<=before:break
                else:
                    field=section.locator('input[type="search"]').filter(visible=True)
                    if not field.count():
                        raise ServiceError('selection_required','Select a current IEEE result facet label',status='selection_required',field=option,candidates=available)
                    field.first.fill('');field.first.press_sequentially(value,delay=75);page.wait_for_timeout(2000)
                    matches_count=sum(choice.nth(index).is_visible() for index in range(choice.count()))
                    if matches_count==1:
                        label=choice.filter(visible=True).first.locator('xpath=ancestor::label[1]').inner_text()
                        match=re.search(r'\(([\d,]+)\)\s*$',label)
                        remember_facet_candidate(facet_catalog,option,value,int(match[1].replace(',','')) if match else None)
                visible=[choice.nth(index) for index in range(choice.count()) if choice.nth(index).is_visible()]
                if len(visible)!=1:
                    raise ServiceError('selection_required','Select one exact current IEEE result facet label',status='selection_required',field=option,candidates=available)
                visible[0].check()
            page.locator(f'button[id="{FACET_LABELS[native]}-apply-btn"]').filter(visible=True).first.click()
        response=transition(choose_facets)
    if 'year' in options:
        first,last=options['year'].split('-',1) if '-' in options['year'] else (options['year'],options['year'])
        def choose_year():
            toggle=page.locator('#reg-PublicationYear-facet').filter(visible=True).first
            if toggle.get_attribute('aria-expanded')!='true':toggle.click()
            page.locator('#range').filter(visible=True).first.check()
            page.get_by_role('textbox',name='Enter start year of range').filter(visible=True).first.fill(first)
            page.get_by_role('textbox',name='Enter end year of range').filter(visible=True).first.fill(last)
            page.locator('#Year-apply-btn').filter(visible=True).first.click()
        response=transition(choose_year)
    return response


def ieee_records(raw):
    rows, total, offset = raw.get("records"), raw.get("totalRecords"), raw.get("startRecord")
    if not isinstance(rows, list) or type(total) is not int or type(offset) is not int:
        raise ServiceError("invalid_response", "IEEE response has no document range")
    identities=[row.get('articleNumber') for row in rows if isinstance(row,dict)]
    if len(identities)!=len(rows) or not all(identities) or len(set(map(str,identities)))!=len(identities) or raw.get("endRecord") != offset + len(rows):
        raise ServiceError("invalid_response", "IEEE document identities or range do not match the response")
    per=raw.get('recordsPerPage');pages=raw.get('totalPages')
    if per!=25 or type(pages) is not int or pages!=(total+per-1)//per or offset<0 or offset>total or len(rows)>per:
        raise ServiceError('invalid_response','IEEE native page size or page count does not match the response')
    # IEEE는 검색어와 일치한 필드를 [::…::]로 감싼다. DOI로 찾으면 식별자인 doi가 감싸여 와서 동일성 대조를 깨뜨린다.
    # 강조 전용 필드(highlightedTitle)는 원 그대로 두고 식별자만 되돌린다. 원 응답은 evidence에 그대로 보존된다.
    rows=[{**row,'doi':row['doi'].replace('[::','').replace('::]','')} if isinstance(row.get('doi'),str) else row for row in rows]
    return rows, total, offset


def reference_records(payload,identifier):
    rows=payload.get('references')
    if str(payload.get('articleNumber'))!=identifier:
        raise ServiceError('identity_mismatch','IEEE reference response belongs to a different document')
    if not isinstance(rows,list) or any(not isinstance(row,dict) for row in rows):
        raise ServiceError('invalid_response','IEEE returned no native reference array')
    return rows


def html_fulltext_region(raw,url,row):
    identifier=str(row.get('articleNumber') or '');expected_title=str(row.get('articleTitle') or '');expected_doi=str(row.get('doi') or '')
    if not identifier or urlsplit(url).path.rstrip('/')!='/document/'+identifier:
        raise ServiceError('identity_mismatch','IEEE HTML page path differs from the selected document')
    from ieee_media import document_metadata
    metadata=document_metadata(raw,identifier);soup=BeautifulSoup(raw,'html.parser')
    title=soup.select('h1.document-title');roots=soup.select('xpl-document-full-text');wrappers=soup.select('#BodyWrapper');sections=soup.select('#full-text-section')
    normalize=lambda value:re.sub(r'[^\w]+','',value.casefold())
    if len(title)!=1 or normalize(title[0].get_text(' ',strip=True))!=normalize(expected_title) or normalize(str(metadata.get('title') or ''))!=normalize(expected_title):
        raise ServiceError('identity_mismatch','IEEE HTML page title differs from the selected document')
    if expected_doi and normalize(str(metadata.get('doi') or ''))!=normalize(expected_doi):
        raise ServiceError('identity_mismatch','IEEE HTML page DOI differs from the selected document')
    if len(roots)!=1 or len(wrappers)!=1 or len(sections)!=1 or wrappers[0] not in sections[0].descendants or sections[0] not in roots[0].descendants:
        raise ServiceError('html_fulltext_not_offered','IEEE page has no recognized native HTML full-text structure',status='not_offered')
    body=wrappers[0];text=body.get_text(' ',strip=True);headings=[node for node in body.select('h2,h3,h4') if node.get_text(' ',strip=True)];paragraphs=body.select('p')
    if not text.strip():
        raise ServiceError('html_fulltext_not_offered','IEEE native HTML full-text structure has no body content',status='not_offered')
    return {'html':str(sections[0]),'body_text_chars':len(text),'heading_count':len(headings),'paragraph_count':len(paragraphs),
            'article_number':identifier,'doi':expected_doi or metadata.get('doi'),'title':expected_title}


def validate_citation_file(data,format,selected):
    count=len(selected)
    if format=='plain':
        try:text=data.decode('utf-8-sig')
        except UnicodeDecodeError:raise ServiceError('export_format_mismatch','IEEE plain citation is not UTF-8 text') from None
        document_ids=re.findall(r'https?://[^\s]+/document/(\d+)',text,re.I)
        if document_ids and len(document_ids)!=count:
            raise ServiceError('export_range_mismatch','IEEE plain citation count differs from the selected document count',requested=count,received=len(document_ids))
        positions=[]
        for expected in selected:
            article=str(expected.get('articleNumber') or '');expected_doi=str(expected.get('doi') or '')
            match=re.search(r'/document/'+re.escape(article)+r'(?:\D|$)',text) if article else None
            position=match.start() if match else text.casefold().find(expected_doi.casefold()) if expected_doi else -1
            if position<0:
                title=' '.join(str(expected.get('articleTitle') or '').split())
                position=' '.join(text.split()).casefold().find(title.casefold()) if title else -1
            if position<0:raise ServiceError('export_identity_mismatch','IEEE plain citation does not identify a selected record')
            positions.append(position)
        if len(set(positions))!=count or positions!=sorted(positions):
            raise ServiceError('export_identity_mismatch','IEEE plain citation order differs from the selected records')
        return
    if format=='csv':
        import csv,io
        reader=csv.DictReader(io.StringIO(data.decode('utf-8-sig')))
        if not reader.fieldnames or not {'Document Title','DOI','PDF Link'}<=set(reader.fieldnames):
            raise ServiceError('export_format_mismatch','IEEE did not return its native CSV result fields')
        rows=list(reader)
    else:
        rows=bibliography(data,'application/x-bibtex' if format=='bibtex' else 'application/x-research-info-systems')
    if len(rows)!=count:
        raise ServiceError('export_range_mismatch','IEEE citation count differs from the selected document count',requested=count,received=len(rows))
    from api_adapters import doi
    for expected,observed in zip(selected,rows):
        fields=observed.get('fields',{}) if isinstance(observed,dict) else {}
        actual_doi=observed.get('DOI') or observed.get('doi') or next(iter(fields.get('do',[])),None)
        actual_article=observed.get('id')
        if not actual_article and isinstance(observed.get('PDF Link'),str):
            match=re.search(r'(?:arnumber=|/document/)(\d+)',observed['PDF Link']);actual_article=match[1] if match else None
        actual_title=observed.get('Document Title') or observed.get('title') or next(iter(fields.get('ti',[])),None)
        expected_doi=expected.get('doi');expected_article=str(expected.get('articleNumber') or '')
        if expected_doi and actual_doi:
            try:matches=doi(str(expected_doi)).casefold()==doi(str(actual_doi)).casefold()
            except ServiceError:matches=False
        elif expected_article and actual_article:
            matches=expected_article==str(actual_article)
        else:
            matches=bool(actual_title and ' '.join(str(actual_title).split()).casefold()==' '.join(str(expected.get('articleTitle') or '').split()).casefold())
        if not matches:raise ServiceError('export_identity_mismatch','IEEE citation export differs from the selected records')


class IEEE:
    source = "ieee-xplore"
    hosts = ("ieeexplore.ieee.org", "ieeexplore-ieee-org.libproxy.knu.ac.kr")
    formats = {"bibtex": ("bibtex", "application/x-bibtex"), "ris": ("ris", "application/x-research-info-systems"), "plain": ("ascii", "text/plain"), "csv": (None, "text/csv")}

    def __init__(self, store, gateway):
        self.store, self.gateway = store, gateway
        self.known = {}

    def page(self):
        return self.gateway.open(self.source, "IEEE", self.hosts, "body")

    def references(self,identifier,base):
        page=self.page()
        goto_source(page,urljoin(base,'/document/'+identifier+'/'),self.hosts,wait_until='domcontentloaded',timeout=SOURCE_WAIT_MS)
        page.locator('h1.document-title').wait_for(timeout=SOURCE_WAIT_MS)
        dismiss_cookies(page)
        path='/rest/document/'+identifier+'/references'
        with page.expect_response(lambda r:urlsplit(r.url).hostname in self.hosts and urlsplit(r.url).path==path,timeout=SOURCE_WAIT_MS) as pending:
            page.locator('a.document-tab-link').filter(has_text=re.compile(r'^References$')).filter(visible=True).first.click()
        response=pending.value
        if response.status in (401,403):
            raise ServiceError('access_restricted','IEEE restricted the reference request',status='restricted')
        if response.status!=200:
            raise ServiceError('provider_error','IEEE reference request failed',http_status=response.status)
        payload=response.json()
        rows=reference_records(payload,identifier)
        document={key:payload[key] for key in ('articleNumber','title','publicationNumber','publisher','contentType','references') if key in payload}
        proof=self.store.put(encoded(document),'application/json',self.source,response.url,role='native_reference_response',article_number=identifier)
        artifact=self.store.put(encoded(rows),'application/json',self.source,response.url,role='reference_records',article_number=identifier,evidence_ref=proof['ref'])
        return {'status':'available' if rows else 'not_found','artifact':artifact,'count':len(rows),'evidence':proof,
                'scope':'Native reference array for this article; citation links are preserved and not followed'}

    def html_fulltext(self,page,row,base,records):
        identifier=str(row.get('articleNumber') or '');link=row.get('htmlLink')
        if not isinstance(link,str):
            return {'status':'not_offered','reason':'This IEEE record exposes no native HTML document control'}
        target=urljoin(base,link)
        if urlsplit(target).hostname not in self.hosts or urlsplit(target).path.rstrip('/')!='/document/'+identifier:
            raise ServiceError('identity_mismatch','IEEE HTML control identifies another document')
        control=page.locator(f'div.List-results-items[id="{identifier}"] a.stats_HTML_{identifier}[href="/document/{identifier}/"]').filter(visible=True)
        try:control.wait_for(state='visible',timeout=SOURCE_WAIT_MS)
        except Exception:pass
        control_seen=control.count()==1
        if control_seen:
            with page.expect_navigation(wait_until='domcontentloaded',timeout=SOURCE_WAIT_MS):control.click()
        else:goto_source(page,target,self.hosts,wait_until='domcontentloaded',timeout=SOURCE_WAIT_MS)
        page.locator('h1.document-title').wait_for(timeout=SOURCE_WAIT_MS)
        deadline=time.monotonic()+SOURCE_WAIT_S
        while time.monotonic()<deadline:
            try:
                body=page.locator('xpl-document-full-text #full-text-section #BodyWrapper')
                if body.count()==1 and body.inner_text().strip():break
            except Exception:pass
            try:page.wait_for_timeout(2500)
            except Exception:pass
        raw=page.content();source=self.store.put(clean_html(raw,self.store.sanitizer),'text/html',self.source,page.url,
            role='html_document_page',article_number=identifier,parent_ref=records['ref'],source_control_seen=control_seen)
        try:parsed=html_fulltext_region(raw,page.url,row)
        except ServiceError as error:
            if control_seen and error.result.get('code')=='html_fulltext_not_offered':
                raise ServiceError('html_document_not_ready','IEEE exposed the selected HTML control but did not render its native body',artifact=source) from None
            error.result['artifact']=source;raise
        artifact=self.store.put(clean_html(parsed.pop('html'),self.store.sanitizer),'text/html',self.source,page.url,
            role='fulltext_html',parent_ref=source['ref'],source_control_path=urlsplit(target).path,**parsed)
        return {'status':'available','artifact':artifact,'source_page':source,'scope':'Native IEEE HTML body for the selected article',
                **{key:parsed[key] for key in ('article_number','doi','title','body_text_chars','heading_count','paragraph_count')}}

    def citation(self, page, indices, format, selected):
        controls = page.get_by_role("checkbox", name="Select search result", exact=True)
        for i in range(controls.count()):
            controls.nth(i).set_checked(i in indices)
        page.get_by_role("button", name="Export", exact=True).click()
        native, media = self.formats[format]
        if native:
            page.get_by_role("tab", name="Citations", exact=True).click()
            page.locator('label[for="download-' + native + '"] input').check()
            page.locator('label[for="citation-abstract"] input').check()
        else:
            page.get_by_role("tab", name="Results", exact=True).click()
        with page.expect_download(timeout=SOURCE_WAIT_MS) as pending:
            page.get_by_role("button", name="Download", exact=True).click()
        download = pending.value
        from pathlib import Path
        data = Path(download.path()).read_bytes()
        # The provider keeps its export modal open after a successful download.
        cancel = page.locator('button.stats-download-citations-button-cancel')
        if cancel.is_visible():
            cancel.click()
        if not data or data.lstrip().lower().startswith((b"<!doctype", b"<html")):
            raise ServiceError("unexpected_content", "IEEE native citation export returned no bibliographic file")
        artifact=self.store.put(data, media, self.source, page.url, role="native_citation_export", format=format, count=len(indices),original_name=download.suggested_filename)
        try:validate_citation_file(data,format,selected)
        except ServiceError as error:
            error.result['source_export']=artifact
            raise
        return artifact

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        if not isinstance(query,str) or not query.strip():
            raise ServiceError('invalid_query','Provide a nonempty IEEE Command Search expression')
        if type(start) is not int or start < 0 or type(limit) is not int or not 1 <= limit <= 1000:
            raise ServiceError("invalid_range", "IEEE requires start >= 0 and limit 1..1000")
        normalized=search_options(options)
        if cursor or export not in (None, "json", *self.formats):
            raise ServiceError("invalid_options", "IEEE uses numeric result offsets; export supports json/bibtex/ris/plain/csv")
        page = self.page()
        dismiss_cookies(page)
        goto_source(page, "https://" + urlsplit(page.url).hostname + "/search/advanced/command", self.hosts, wait_until="domcontentloaded", timeout=SOURCE_WAIT_MS)
        page.locator("#cmdTextArea").wait_for(timeout=SOURCE_WAIT_MS)
        dismiss_cookies(page)
        page.locator("#cmdTextArea").fill(query)

        def matches(response):
            if urlsplit(response.url).hostname not in self.hosts or urlsplit(response.url).path != "/rest/search" or response.request.method != "POST":
                return False
            try:
                return response.request.post_data_json.get("queryText") in (query, "(" + query + ")")
            except Exception:
                return False

        with page.expect_response(matches, timeout=SOURCE_WAIT_MS) as pending:
            page.locator(".stats-Adv_Command_search").click()
        response = require_search_response(pending.value)
        initial_facets=ieee_facets(response.json())
        response=apply_search_options(page,response,matches,normalized,initial_facets)
        rows, evidence, exports, errors, total, offset, facets_artifact = [], [], [], [], None, 0, None
        while True:
            if response.status in (401, 403):
                raise ServiceError("access_restricted", "IEEE restricted this institutional search", status="restricted")
            if response.status != 200:
                raise ServiceError("provider_error", "IEEE search failed", http_status=response.status)
            raw = response.json()
            validate_request_state(response,normalized,offset//25+1)
            validate_filter_state(raw,normalized)
            native, observed, position = ieee_records(raw)
            if position != offset or total is not None and observed != total:
                raise ServiceError("range_mismatch", "IEEE returned a different document range")
            total = observed
            if facets_artifact is None:
                facets_artifact=self.store.put(encoded(initial_facets),"application/json",self.source,response.url,
                    role="search_facets",query=query,options=normalized,total=total,scope="Candidates from the unfiltered command-search result; copy exact labels into result options")
            # Session/account information is not bibliographic evidence. Preserve all search data.
            raw.pop("userInfo", None)
            evidence.append(self.store.put(encoded(raw), "application/json", self.source, response.url, role="search_response", query=query, options=normalized, offset=offset, total=total))
            indices = [i for i in range(len(native)) if start <= offset + i < start + limit]
            selected = [native[i] for i in indices]
            rows.extend(selected)
            self.known.update({row["articleNumber"]: (row, page.url) for row in selected})
            if indices and export in self.formats:
                try:
                    page.get_by_role("checkbox", name="Select search result", exact=True).first.wait_for(timeout=SOURCE_WAIT_MS)
                    exports.append(self.citation(page, indices, export, selected))
                except ServiceError as error:
                    errors.append({'page_start':offset,**error.result})
                except Exception as error:
                    errors.append({'page_start':offset,'status':'error','code':'citation_export_failed',**failure_details(error)})
            offset += len(native)
            if offset >= min(total, start + limit) or not native:
                break
            next_page = page.locator('button[aria-label="Next page of search results"],a[aria-label="Next Page"],button[aria-label="Next Page"],a[title="Next Page"],button[aria-label="Next page"],a[aria-label="Next page"]')
            if not next_page.count():
                raise ServiceError("pagination_control_missing", "IEEE next-page control could not be identified", evidence=evidence)
            with page.expect_response(matches, timeout=SOURCE_WAIT_MS) as pending:
                next_page.filter(visible=True).first.click()
            response = pending.value
        artifact = self.store.put(encoded(rows), "application/json", self.source, page.url, role="records", query=query, start=start, requested=limit, total=total)
        more = start + len(rows) < total
        return {"status": "partial" if errors else "ok" if rows else "not_found", "source": self.source, "query": query, "options":normalized,"start": start,
            "requested": limit, "received": len(rows), "total": total, "has_more": more,
            "next": {"start": start + len(rows)} if more else None, "records": artifact,
            "export": {'status':'partial','artifacts':exports,'errors':errors} if errors else exports[0] if len(exports) == 1 else {"artifacts": exports} if exports else artifact,
            "evidence": evidence,"facets":facets_artifact,"filter_state":normalized, "preview": [{k: row.get(k) for k in ("articleNumber", "articleTitle", "publicationYear", "doi")} for row in rows[:3]]}

    def fetch(self, target, *, parts):
        from api_adapters import doi
        if set(parts) - {"metadata", "abstract", "fulltext", "fulltext_html", "supplementary", "export"}:
            raise ServiceError("invalid_parts", "Unknown requested content")
        value = target;requested_doi=None
        if target.startswith(("http://", "https://")) and urlsplit(target).hostname not in (*self.hosts, "doi.org", "dx.doi.org"):
            raise ServiceError("source_boundary", "Use an IEEE document URL or DOI")
        if target.startswith(("http://", "https://")) and urlsplit(target).hostname in self.hosts:
            found = re.fullmatch(r"/document/(\d+)/?", urlsplit(target).path)
            if not found:
                raise ServiceError("invalid_target", "Use an IEEE document URL")
            value = found[1]
        if value.isdigit():
            identifier, query = value, '"Article Number":' + value
        else:
            identifier = None
            try:
                requested_doi=doi(value);query = '"DOI":"' + requested_doi + '"'
            except ServiceError:
                result = self.search('"Document Title":"' + value.replace('"', " ") + '"', options={}, limit=20)
                result["status"] = "selection_required" if result["received"] else "not_found"
                return result
        if identifier not in self.known:
            result = self.search(query, options={}, limit=2)
            if result["total"] != 1:
                result["status"] = "selection_required" if result["received"] else "not_found"
                return result
            candidate=json.loads(self.store.read(result["records"]["ref"])[1])[0]
            if requested_doi:
                try:matches=doi(str(candidate.get('doi') or '')).casefold()==requested_doi.casefold()
                except ServiceError:matches=False
                if not matches:raise ServiceError('identity_mismatch','IEEE DOI search returned another publication',evidence=result['records'])
            identifier = candidate["articleNumber"]
        row, base = self.known[identifier]
        artifact = self.store.put(encoded([row]), "application/json", self.source, urljoin(base, row["documentLink"]), role="records", target=identifier)
        components = {}
        for part in parts:
            if part in ("metadata", "export"):
                components[part] = {"status": "available", "artifact": artifact, "format": "json"}
            elif part == "abstract":
                components[part] = {"status": "available", "artifact": artifact} if row.get("abstract") else {"status": "not_found", "reason": "IEEE record has no abstract"}
            elif part == "fulltext":
                if not row.get("pdfLink"):
                    components[part] = {"status": "not_offered", "reason": "This record exposes no PDF control; request fulltext_html separately when a native HTML body is offered"}
                    continue
                try:
                    data, media, url = browser_download(self.gateway.context, urljoin(base, row["pdfLink"]), self.hosts)
                    if not data.startswith(b"%PDF-"):
                        soup = BeautifulSoup(data, "html.parser")
                        frames = soup.select('iframe[src*="/stampPDF/getPDF.jsp"]')
                        if len(frames) != 1:
                            raise ServiceError("unexpected_content", "IEEE PDF viewer did not identify its document file")
                        data, media, url = browser_download(self.gateway.context, urljoin(url, frames[0]["src"]), self.hosts)
                    if not data.startswith(b"%PDF-"):
                        raise ServiceError("unexpected_content", "IEEE document endpoint returned no PDF")
                    import pymupdf
                    with pymupdf.open(stream=data, filetype="pdf") as pdf:
                        pages = len(pdf)
                    fulltext = self.store.put(data, "application/pdf", self.source, url, role="fulltext", target=identifier, pages=pages)
                    components[part] = {"status": "available", "artifact": fulltext}
                except ServiceError as error:
                    components[part] = error.result
            elif part=='fulltext_html':
                try:components[part]=self.html_fulltext(self.page(),row,base,artifact)
                except ServiceError as error:components[part]=error.result
                except Exception as error:components[part]={'status':'error','code':'html_fulltext_retrieval_failed',**failure_details(error)}
            else:
                from ieee_media import fetch_media
                details={}
                for name,operation in [('references',lambda:self.references(identifier,base)),('attachments',lambda:fetch_media(self,identifier,base))]:
                    try: details[name]=operation()
                    except ServiceError as error: details[name]=error.result
                    except Exception as error: details[name]={'status':'error','code':name+'_retrieval_failed',**failure_details(error)}
                clean=all(item['status'] in ('available','not_found','not_offered') for item in details.values())
                components[part]={'status':'available' if clean and any(item['status']=='available' for item in details.values()) else 'not_found' if clean else 'partial',**details}
                if details['references'].get('artifact'): components[part]['artifact']=details['references']['artifact']
        return {"status": "ok" if all(v["status"] == "available" for v in components.values()) else "partial", "source": self.source,
            "target": identifier, "records": artifact, "components": components}

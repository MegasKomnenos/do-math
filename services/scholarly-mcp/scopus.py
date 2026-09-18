"""Scopus through its KUDOS browser session; no developer API credentials."""
import csv
import io
import json
import re
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
from waits import SOURCE_WAIT_MS

from bs4 import BeautifulSoup
from browser_adapters import clean_html, dismiss_cookies, goto_source
from scholarly import ServiceError, encoded, failure_details

SCOPUS_SORTS={
    'newest':('Date (newest)','plf-f'),'oldest':('Date (oldest)','plf-t'),
    'cited-highest':('Cited by (highest)','cp-f'),'cited-lowest':('Cited by (lowest)','cp-t'),
    'relevance':('Relevance','r-f'),'author-asc':('First Author (A-Z)','lfp-t'),
    'author-desc':('First Author (Z-A)','lfp-f'),'source-title-asc':('Source Title (A-Z)','tp-t'),
    'source-title-desc':('Source Title (Z-A)','tp-f')}
SCOPUS_SORT_REQUESTS={
    'plf-f':[{'fieldName':'datesort','order':'desc'},{'fieldName':'relevance','order':'desc'}],
    'plf-t':[{'fieldName':'datesort','order':'asc'},{'fieldName':'relevance','order':'desc'}],
    'cp-f':[{'fieldName':'numcitedby','order':'desc'},{'fieldName':'datesort','order':'desc'}],
    'cp-t':[{'fieldName':'numcitedby','order':'asc'},{'fieldName':'datesort','order':'desc'}],
    'r-f':[{'fieldName':'relevance','order':'desc'},{'fieldName':'datesort','order':'desc'}],
    'lfp-t':[{'fieldName':'firstauth','order':'asc'},{'fieldName':'datesort','order':'desc'}],
    'lfp-f':[{'fieldName':'firstauth','order':'desc'},{'fieldName':'datesort','order':'desc'}],
    'tp-t':[{'fieldName':'srctitle','order':'asc'},{'fieldName':'datesort','order':'desc'}],
    'tp-f':[{'fieldName':'srctitle','order':'desc'},{'fieldName':'datesort','order':'desc'}]}
SCOPUS_FACET_GROUPS={
    'year':'year-section','subject_area':'subject-area-section','document_type':'document-type-section',
    'language':'language-section','keyword':'keyword-section','country_territory':'country/territory-section',
    'source_type':'source-type-section','source_title':'source-title-section','author_name':'author-name-section',
    'publication_stage':'publication-stage-section','affiliation':'affiliation-section','funding_sponsor':'funding-sponsor-section',
    'open_access':'open-access-section'}
SCOPUS_NATIVE_FACETS={'year':'pubyr','subject_area':'subjabbr','document_type':'subtype','language':'lang','keyword':'keywords',
    'country_territory':'affilctry','source_type':'srctype','source_title':'srctitle','author_name':'prefnameauid','publication_stage':'pubstage',
    'affiliation':'afid','funding_sponsor':'fundsponsor','open_access':'freetoread'}

def _facet_filters(value,groups):
    if value is None:return []
    if not isinstance(value,dict):raise ServiceError('invalid_options','facet_filters must map current result fields to include/exclude labels')
    result=[]
    for field,spec in value.items():
        if field not in groups or not isinstance(spec,dict) or not spec or set(spec)-{'include','exclude'}:
            raise ServiceError('invalid_options','Each facet field needs include and/or exclude exact labels')
        include=spec.get('include',[]);exclude=spec.get('exclude',[])
        if not include and not exclude or any(not isinstance(items,list) or not items or any(not isinstance(item,str) or not item.strip() for item in items)
               or len({item.casefold() for item in items})!=len(items) for items in (include,exclude) if items):
            raise ServiceError('invalid_options','Facet labels must be distinct nonempty strings')
        if {item.casefold() for item in include}&{item.casefold() for item in exclude}:
            raise ServiceError('invalid_options','One facet label cannot be both included and excluded')
        result.append((field,groups[field],include,exclude))
    return result

def search_options(options):
    if not isinstance(options,dict) or set(options)-{'sort','facet_filters','facet_group'}:
        raise ServiceError('invalid_options','Use current Scopus result sort and facet fields')
    sort=options.get('sort');group=options.get('facet_group')
    if sort is not None and sort not in SCOPUS_SORTS:raise ServiceError('invalid_options','Use a current Scopus result sort')
    if group is not None and group not in SCOPUS_FACET_GROUPS:raise ServiceError('invalid_options','Use a current Scopus facet field')
    return {'sort':SCOPUS_SORTS.get(sort),'sort_name':sort,'facet_filters':_facet_filters(options.get('facet_filters'),SCOPUS_FACET_GROUPS),
            'facet_preview':(group,SCOPUS_FACET_GROUPS[group],None) if group else None}


def primary_request(request, query):
    return request.get("documentClassification") == "primary" and request.get("query") == query


PARSE_PATH = "/gateway/documents/search/parsequery"
SEARCH_PATH = "/gateway/documents/search"


def search_settled(hosts, query, response):
    """이 제출이 결말에 이르렀는지 본다.

    Scopus는 검색식을 먼저 parsequery로 해석한 뒤에야 검색을 보낸다. 해석이 실패하면 검색 요청은
    아예 나가지 않으므로, 그것도 기다림의 결말로 본다. 그러지 않으면 오지 않을 응답을 한도까지 기다린다.
    """
    parts = urlsplit(response.url)
    if parts.hostname not in hosts:
        return False
    if parts.path == PARSE_PATH:
        return response.status != 200
    if parts.path != SEARCH_PATH or response.request.method != "POST":
        return False
    try:
        return primary_request(response.request.post_data_json, query)
    except Exception:
        return False


RESULT_TABLE_STATE = "primary_documents~"


def forget_result_table_state(page):
    """직전 검색의 결과 표 위치를 지운다.

    Scopus는 표의 쪽·쪽 크기·정렬을 탭의 sessionStorage(primary_documents~activePage 등)에 기억하고 다음 검색에 복원한다.
    그대로 두면 새 검색이 옛 쪽의 요청을 함께 보내, 첫 쪽부터 순서대로 받는다는 이 어댑터의 전제가 깨진다.
    """
    page.evaluate("(prefix) => Object.keys(sessionStorage).filter(key => key.startsWith(prefix))"
                  ".forEach(key => sessionStorage.removeItem(key))", RESULT_TABLE_STATE)


def require_accepted_query(query, response):
    """결말이 질의 거절이면 그대로 보고한다. 검색 응답이면 그대로 돌려준다."""
    if urlsplit(response.url).path == PARSE_PATH:
        # 실측: 기관 프록시는 불리언 연산자 뒤에 비교 연산(> < =)이 오는 검색식을 SQL 주입으로 보고 자기 HTML 400을 돌려준다.
        # Scopus 자신의 문법 오류는 JSON으로 온다. 막은 주체에 따라 호출자가 고칠 것이 다르다.
        proxy = "html" in (response.headers.get("content-type") or "").lower()
        raise ServiceError("query_rejected",
                           "The institutional proxy blocked this query text before Scopus saw it; use PUBYEAR AFT/BEF/IS instead of > < = after AND/OR"
                           if proxy else "Scopus did not accept the advanced query text",
                           http_status=response.status, query=query,
                           rejected_by="institutional_proxy" if proxy else "scopus")
    return response

def validate_primary_request(request,query,sort_by=None,facet_filters=None):
    if not isinstance(request,dict) or not primary_request(request,query):
        raise ServiceError('query_mismatch','Scopus request did not retain the primary document query')
    if sort_by is not None and request.get('sortBy')!=sort_by:
        raise ServiceError('query_mismatch','Scopus request did not retain the selected result sort')
    if facet_filters is not None and (request.get('facetFilters') or [])!=facet_filters:
        raise ServiceError('query_mismatch','Scopus request did not retain the selected result facets')

def _facet_terms(filters):
    if not isinstance(filters,list):raise ServiceError('query_mismatch','Scopus facet filters have an unexpected structure')
    result=[];seen=set()
    for group in filters:
        if not isinstance(group,dict) or set(group)!={'facetName','facetTerms'} or not isinstance(group['facetName'],str) or not group['facetName'] \
                or not isinstance(group['facetTerms'],list) or not group['facetTerms']:
            raise ServiceError('query_mismatch','Scopus facet filters have an unexpected structure')
        for term in group['facetTerms']:
            if not isinstance(term,dict) or set(term)!={'action','term'} or term.get('action') not in ('limit-to','exclude') \
                    or not isinstance(term.get('term'),str) or not term['term']:
                raise ServiceError('query_mismatch','Scopus facet terms have an unexpected structure')
            value=(group['facetName'],term['action'],term['term'])
            if value in seen:raise ServiceError('query_mismatch','Scopus facet request duplicated a native term')
            seen.add(value);result.append(value)
    return result

def validate_facet_transition(request,query,previous,expected_field,action,expected_terms):
    validate_primary_request(request,query)
    before=_facet_terms(previous);current=request.get('facetFilters') or [];after=_facet_terms(current)
    if any(value not in after for value in before):raise ServiceError('query_mismatch','Scopus refinement dropped a previous facet term')
    added=[value for value in after if value not in before]
    expected={(expected_field,action,term) for term in expected_terms}
    if len(expected)!=len(expected_terms) or set(added)!=expected:
        raise ServiceError('query_mismatch','Scopus refinement did not retain the requested facet field, action and native terms')
    return current

def validate_sort_transition(request,query,expected,facets):
    validate_primary_request(request,query,sort_by=expected,facet_filters=facets)
    current=request.get('sortBy')
    if not isinstance(current,list) or not current or any(not isinstance(item,dict) or set(item)!={'fieldName','order'}
            or not isinstance(item['fieldName'],str) or not item['fieldName'] or item['order'] not in ('asc','desc') for item in current) \
            or len({item['fieldName'] for item in current})!=len(current):
        raise ServiceError('query_mismatch','Scopus sorting did not produce a distinct valid native sort')
    return current

def scopus_facet_candidates(raw,section):
    soup=BeautifulSoup(raw,'html.parser');scope=soup.find(id=section)
    if scope is None:return []
    result=[];seen=set()
    for label in scope.find_all('label'):
        if label.find('input',attrs={'type':'checkbox'}) is None:continue
        match=re.fullmatch(r'(.+?)\s+([\d,]+)',label.get_text(' ',strip=True))
        identity=label.get('data-testid','');native=identity.removeprefix('facet-option-') if identity.startswith('facet-option-') else None
        if not match or not native:continue
        name=match[1].strip();key=name.casefold()
        if key in seen:raise ServiceError('invalid_response','Scopus facet labels are duplicated in one result group')
        seen.add(key);result.append({'label':name,'count':int(match[2].replace(',','')),'native_term':native})
    return result

def query_key(value):
    """Ignore cosmetic syntax spacing without joining words or changing phrases."""
    if not isinstance(value,str):raise ServiceError('query_mismatch','Scopus query identity is not text')
    tokens=[];word=[];index=0
    def flush():
        if word:tokens.append(''.join(word));word.clear()
    while index<len(value):
        character=value[index]
        if character=='\\':
            word.append(value[index:index+2]);index+=2;continue
        if character.isspace():flush();index+=1;continue
        if character in '"{':
            flush();start=index;end='"' if character=='"' else '}';depth=1;index+=1
            while index<len(value):
                current=value[index]
                if current=='\\':index+=2;continue
                if end=='}' and current=='{':depth+=1
                if current==end:
                    depth-=1;index+=1
                    if not depth:break
                else:index+=1
            tokens.append(value[start:index]);continue
        if character in '(),<>=:':flush();tokens.append(character)
        else:word.append(character)
        index+=1
    flush();return tuple(tokens)


def displayed_query(page,base_query):
    copy=page.get_by_role('button',name='Copy query text to clipboard',exact=True).filter(visible=True)
    candidates=[]
    if copy.count()==1:
        page.evaluate('''() => {window.__scholarlyCopiedQuery=null;window.__scholarlyClipboard=Object.getOwnPropertyDescriptor(navigator,'clipboard');
            Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async value=>{window.__scholarlyCopiedQuery=value;}}});}''')
        try:
            copy.click()
            page.wait_for_function('() => typeof window.__scholarlyCopiedQuery === "string"',timeout=SOURCE_WAIT_MS)
            value=page.evaluate('window.__scholarlyCopiedQuery')
            if isinstance(value,str) and value.strip():candidates.append(value.strip())
        finally:
            page.evaluate('''() => {delete navigator.clipboard;if(window.__scholarlyClipboard)Object.defineProperty(navigator,'clipboard',window.__scholarlyClipboard);
                delete window.__scholarlyClipboard;delete window.__scholarlyCopiedQuery;}''')
    else:
        editors=page.locator('.monaco-editor[role="code"]').filter(visible=True)
        candidates=[value.strip() for editor in editors.all() if isinstance(value:=editor.inner_text(),str) and value.strip()]
    base=query_key(base_query);matches={}
    for value in candidates:
        key=query_key(value)
        if key==base or key[:len(base)+2]==base+('AND','('):matches[key]=value
    if len(matches)!=1:
        raise ServiceError('query_mismatch','Scopus result did not expose one current query matching the requested base query')
    return next(iter(matches.values()))


def filter_count_records(data,query):
    if not isinstance(data,bytes) or not data or data.lstrip().startswith(b'<'):
        raise ServiceError('invalid_native_export','Scopus filter-count export is not a CSV file')
    try:rows=list(csv.reader(io.StringIO(data.decode('utf-8-sig'))))
    except Exception:raise ServiceError('invalid_native_export','Scopus filter-count export is not UTF-8 CSV') from None
    query_rows=[row for row in rows[:6] if len(row)==1 and row[0].startswith('Your query : ')]
    if not query_rows:raise ServiceError('invalid_native_export','Scopus filter-count CSV has no query identity')
    if len(query_rows)!=1 or not query_rows[0][0].endswith(')'):raise ServiceError('invalid_native_export','Scopus filter-count CSV has an invalid query identity')
    native_query=query_rows[0][0][len('Your query : ('):-1] if query_rows[0][0].startswith('Your query : (') else ''
    if query_key(native_query)!=query_key(query):
        raise ServiceError('export_identity_mismatch','Scopus filter-count CSV identifies another current query')
    header_index=next((index for index,row in enumerate(rows) if len(row)>=4 and len(row)%2==0 and all(not row[i] for i in range(1,len(row),2))),None)
    if header_index is None:raise ServiceError('invalid_native_export','Scopus filter-count CSV has no paired facet header')
    header=rows[header_index];groups=header[::2]
    if any(not group for group in groups) or len(groups)!=len({group.casefold() for group in groups}):
        raise ServiceError('invalid_native_export','Scopus filter-count CSV has invalid facet groups')
    candidates={group:[] for group in groups};seen={group:set() for group in groups};candidate_rows=0
    for row in rows[header_index+1:]:
        if len(row)!=len(header):raise ServiceError('invalid_native_export','Scopus filter-count CSV has an inconsistent table width')
        populated=False
        for index,group in enumerate(groups):
            label,count=row[index*2:index*2+2]
            if not label and not count:continue
            if not label or not re.fullmatch(r'(?:0|[1-9]\d*|[1-9]\d{0,2}(?:,\d{3})+)',count):
                raise ServiceError('invalid_native_export','Scopus filter-count CSV has an invalid label/count pair')
            if label.casefold() in seen[group]:raise ServiceError('invalid_native_export','Scopus filter-count CSV duplicated a label in one group')
            seen[group].add(label.casefold());candidates[group].append({'label':label,'count':int(count.replace(',',''))});populated=True
        candidate_rows+=bool(populated)
    if not candidate_rows:raise ServiceError('invalid_native_export','Scopus filter-count CSV has no facet candidates')
    return {'groups':groups,'candidate_rows':candidate_rows,'candidates':candidates,'table_header_row':header_index+1,'native_query':native_query,
            'scope':'Native result-facet labels and counts for the exact exported query'}


def scopus_records(payload,*,check_unique=True):
    meta, rows = payload.get("metadata", {}), payload.get("items")
    if not isinstance(rows, list) or not all(isinstance(r, dict) and r.get("eid") for r in rows):
        raise ServiceError("invalid_response", "Scopus response contains no primary document records")
    total, offset = meta.get("totalCount"), meta.get("offset")
    capacity = meta.get("itemCount")
    if type(total) is not int or type(offset) is not int or type(capacity) is not int or len(rows) != min(capacity, max(0, total - offset)):
        raise ServiceError("invalid_response", "Scopus document range does not match its response metadata")
    if check_unique:unique_primary_ids(rows)
    return rows, total, offset

def unique_primary_ids(rows,seen=()):
    identifiers=[row.get('eid') if isinstance(row,dict) else None for row in rows]
    if any(not isinstance(value,str) or not re.fullmatch(r'2-s2\.0-\d+',value) for value in identifiers) \
            or len(identifiers)!=len(set(identifiers)) or set(identifiers)&set(seen):
        raise ServiceError('invalid_response','Scopus primary result pages contain a duplicate or missing EID')
    return identifiers


def reference_records(payload):
    meta,rows=payload.get('metadata',{}),payload.get('items')
    total,offset,capacity=meta.get('totalCount'),meta.get('offset'),meta.get('itemCount')
    if not isinstance(rows,list) or any(not isinstance(row,dict) for row in rows) or any(type(v) is not int for v in (total,offset,capacity)):
        raise ServiceError('invalid_response','Scopus returned no reference result range')
    if min(total,offset)<0 or capacity<1 or len(rows)!=min(capacity,max(0,total-offset)):
        raise ServiceError('range_mismatch','Scopus reference rows do not match their declared range')
    return rows,total,offset


class Scopus:
    source = "scopus"
    hosts = ("www-scopus-com.libproxy.knu.ac.kr", "www.scopus.com")

    def __init__(self, store, gateway):
        self.store, self.gateway = store, gateway

    def page(self):
        return self.gateway.open(self.source, "Scopus", self.hosts, "main")

    def invalid_export_artifact(self,data,media,url,role):
        sniffed=data.lstrip(b'\xef\xbb\xbf \t\r\n')
        if 'html' in (media or '').casefold() or sniffed.startswith(b'<'):
            return self.store.put(clean_html(data.decode('utf-8-sig',errors='replace'),self.store.sanitizer),'text/html',self.source,url,role=role)
        if 'json' in (media or '').casefold() or sniffed.startswith((b'{',b'[')):
            try:return self.store.put(encoded(json.loads(data.decode('utf-8-sig'))),'application/json',self.source,url,role=role)
            except Exception:return self.store.put(self.store.sanitizer.text(data.decode('utf-8-sig',errors='replace')),'text/plain',self.source,url,role=role)
        return self.store.put(data,media or 'application/octet-stream',self.source,url,preserve_bytes=True,role=role)

    def facet_count_export(self,page,query,total,facet_filters):
        downloads=[];source_artifact=None
        def received(download):downloads.append(download)
        page.on('download',received)
        try:
            native_query=displayed_query(page,query)
            trigger=page.locator('[data-testid="exportRefinement"]').filter(visible=True)
            try:trigger.first.wait_for(state='visible',timeout=SOURCE_WAIT_MS)
            except Exception:raise ServiceError('native_export_not_offered','Scopus did not finish rendering its filter-count export',status='not_offered') from None
            if trigger.count()!=1 or not trigger.is_visible() or not trigger.is_enabled():
                raise ServiceError('native_export_not_offered','Scopus did not offer an enabled filter-count export',status='not_offered')
            with page.expect_response(lambda response:urlsplit(response.url).hostname in self.hosts and
                                      urlsplit(response.url).path=='/gateway/document-facet-api/facets/export' and response.request.method=='POST',timeout=SOURCE_WAIT_MS) as event:
                trigger.click()
            response=event.value
            validate_primary_request(response.request.post_data_json,query,facet_filters=facet_filters)
            if response.status!=200:
                try:failed=self.invalid_export_artifact(response.body(),response.headers.get('content-type','').split(';')[0],response.url,'failed_native_facet_counts_response')
                except Exception:failed=None
                details={'http_status':response.status,**({'source_export':failed} if failed else {})}
                if response.status in (401,403):raise ServiceError('access_restricted','Scopus restricted the filter-count export',status='restricted',**details)
                raise ServiceError('provider_error','Scopus filter-count export failed',**details)
            source_data=response.body()
            try:source_parsed=filter_count_records(source_data,native_query)
            except ServiceError as error:
                failed=self.invalid_export_artifact(source_data,response.headers.get('content-type','').split(';')[0],response.url,'invalid_native_facet_counts_response')
                raise ServiceError(error.result['code'],error.result['message'],source_export=failed) from None
            source_artifact=self.store.put(source_data,'text/csv',self.source,response.url,preserve_bytes=True,role='native_facet_counts_response',
                query=query,native_query=native_query,total=total,facet_groups=source_parsed['groups'],candidate_rows=source_parsed['candidate_rows'])
            for _ in range(80):
                if downloads:break
                page.wait_for_timeout(250)
            if len(downloads)!=1:raise ServiceError('export_failed','Scopus filter-count response produced no unique download',source_response=source_artifact)
            download=downloads[0]
            if download.failure():raise ServiceError('export_failed','Scopus filter-count download failed',source_response=source_artifact)
            data=Path(download.path()).read_bytes()
            try:parsed=filter_count_records(data,native_query)
            except ServiceError as error:
                failed=self.invalid_export_artifact(data,'text/csv',response.url,'invalid_native_facet_counts_download')
                raise ServiceError(error.result['code'],error.result['message'],source_export=failed,source_response=source_artifact) from None
            if Path(download.suggested_filename).suffix.casefold()!='.csv':
                failed=self.invalid_export_artifact(data,'application/octet-stream',response.url,'misnamed_native_facet_counts_download')
                raise ServiceError('invalid_native_export','Scopus filter-count download is not named as CSV',source_export=failed,source_response=source_artifact)
            if data not in (source_data,b'\xef\xbb\xbf'+source_data) or any(parsed[key]!=source_parsed[key] for key in ('groups','candidate_rows','candidates','native_query')):
                failed=self.invalid_export_artifact(data,'text/csv',response.url,'mismatched_native_facet_counts_download')
                raise ServiceError('export_identity_mismatch','Scopus filter-count response and downloaded CSV differ',source_export=failed,source_response=source_artifact)
            artifact=self.store.put(data,'text/csv',self.source,response.url,preserve_bytes=True,role='native_facet_counts',query=query,total=total,
                facet_groups=parsed['groups'],candidate_rows=parsed['candidate_rows'],table_header_row=parsed['table_header_row'],
                scope=parsed['scope'],native_query=parsed['native_query'],source_response_ref=source_artifact['ref'],original_name=download.suggested_filename)
            return {**artifact,'facet_groups':parsed['groups'],'candidate_rows':parsed['candidate_rows'],'table_header_row':parsed['table_header_row'],
                    'source_response_ref':source_artifact['ref'],'native_query':parsed['native_query']}
        except ServiceError:raise
        except Exception as error:
            raise ServiceError('export_interaction_failed','Scopus filter-count export interaction did not complete',
                **failure_details(error),**({'source_response':source_artifact} if source_artifact else {})) from None
        finally:
            page.remove_listener('download',received)

    def facet_candidates(self,page,field,section,query=None):
        control=page.locator('[role="combobox"][aria-controls="'+section+'"]')
        if control.count()!=1:
            raise ServiceError('facet_selection_required','The current Scopus result has no unique requested facet group',status='selection_required',field=field)
        scope=page.locator('[id="'+section+'"]')
        def candidates():return scopus_facet_candidates('<section id="'+section+'">'+scope.inner_html()+'</section>',section)
        current=candidates() if scope.count() else []
        if not current:
            if control.get_attribute('aria-expanded')=='true':control.click();page.wait_for_timeout(250)
            control.click()
        if field=='year':
            individual=scope.locator('input[type="radio"][value="individual"]')
            individual.first.wait_for(state='attached',timeout=SOURCE_WAIT_MS)
            if not individual.is_checked():individual.evaluate('(node)=>node.click()')
        scope.locator('label input[type="checkbox"]').first.wait_for(state='attached',timeout=SOURCE_WAIT_MS)
        buttons=page.get_by_role('button',name=re.compile(r'^(?:Show all|Show more|View all|View more)$',re.I)).filter(visible=True);bound=[]
        for index in range(buttons.count()):
            button=buttons.nth(index)
            if button.evaluate('''(button,section) => { const all=[...document.querySelectorAll('[role="combobox"][aria-controls]')];
                const before=all.filter(control=>control.compareDocumentPosition(button)&Node.DOCUMENT_POSITION_FOLLOWING);
                return before.at(-1)?.getAttribute('aria-controls')===section; }''',section):bound.append(button)
        if len(bound)>1:raise ServiceError('invalid_response','Scopus facet group has ambiguous expansion controls',field=field)
        if bound:
            bound[0].click();dialog=page.get_by_role('dialog').filter(visible=True);dialog.first.wait_for(state='visible',timeout=SOURCE_WAIT_MS)
            if dialog.count()!=1:raise ServiceError('facet_selection_required','Scopus did not open the requested facet candidate panel',status='selection_required',field=field)
            scope=dialog.first;scope.locator('label input[type="checkbox"]').first.wait_for(state='attached',timeout=SOURCE_WAIT_MS)
        search=scope.locator('input[type="search"],input[placeholder*="Search" i]').filter(visible=True)
        if query is not None:
            if not search.count():
                raise ServiceError('facet_selection_required','This Scopus facet group has no current candidate-search control',status='selection_required',field=field,candidates=candidates())
            search.first.fill(query);page.wait_for_timeout(600)
        current=candidates()
        if not current:raise ServiceError('facet_selection_required','Scopus returned no current candidates for the requested facet group',status='selection_required',field=field)
        return current,scope

    def apply_facets(self,page,response,query,filters,previous_filters):
        if not filters:return response,[],[],previous_filters
        evidence=[];candidate_artifacts=[];current_filters=previous_filters
        _,current_total,_=scopus_records(response.json())
        for field,section,include,exclude in filters:
            for action,labels in (('limit-to',include),('exclude',exclude)):
                if not labels:continue
                candidates,scope=self.facet_candidates(page,field,section)
                selected=[]
                for label in labels:
                    matches=[item for item in candidates if item['label'].casefold()==label.casefold()]
                    if len(matches)!=1:
                        raise ServiceError('facet_selection_required','Select one exact label from the current Scopus facet group',status='selection_required',field=field,candidates=candidates)
                    controls=[]
                    for node in scope.locator('label').all():
                        parsed=scopus_facet_candidates('<section id="x">'+node.evaluate('(n)=>n.outerHTML')+'</section>','x')
                        if len(parsed)==1 and parsed[0]['label'].casefold()==label.casefold():controls.append(node.locator('input[type="checkbox"]'))
                    if len(controls)!=1:
                        raise ServiceError('facet_selection_required','The selected Scopus label has no unique checkbox',status='selection_required',field=field,candidates=candidates)
                    if not controls[0].is_checked():controls[0].evaluate('(node)=>node.click()')
                    selected.append(matches[0])
                public_selected=[{key:item[key] for key in ('label','count')} for item in selected]
                candidate_artifacts.append(self.store.put(encoded(public_selected),'application/json',self.source,page.url,role='facet_candidates',field=field,
                    action=action,scope='Exact labels from one current Scopus result facet'))
                button=page.get_by_role('button',name='Limit to' if action=='limit-to' else 'Exclude',exact=True).filter(visible=True)
                with page.expect_response(lambda r:urlsplit(r.url).hostname in self.hosts and urlsplit(r.url).path=='/gateway/documents/search'
                                          and r.request.method=='POST' and primary_request(r.request.post_data_json,query),timeout=SOURCE_WAIT_MS) as event:
                    button.first.click()
                previous_sort=response.request.post_data_json.get('sortBy')
                response=event.value
                if response.status!=200:raise ServiceError('provider_error','Scopus result refinement failed',http_status=response.status,field=field)
                request=response.request.post_data_json
                if request.get('sortBy')!=previous_sort:raise ServiceError('query_mismatch','Scopus refinement changed the current result sort',field=field)
                native_terms=[item['native_term'] for item in selected]
                new_filters=validate_facet_transition(request,query,current_filters,SCOPUS_NATIVE_FACETS[field],action,native_terms)
                rows,total,_=scopus_records(response.json())
                if total>current_total:raise ServiceError('result_set_mismatch','Scopus refinement enlarged the current result set',field=field)
                current_total=total;current_filters=new_filters
                evidence.append(self.store.put(encoded(response.json()),'application/json',self.source,response.url,role='facet_response',field=field,
                    action=action,labels=labels,total=total,received=len(rows)))
                page.wait_for_timeout(500)
        return response,evidence,candidate_artifacts,current_filters

    def apply_sort(self,page,response,query,sort):
        if sort is None:return response,None,None
        label,value=sort;control=next((node for node in page.locator('select').all() if node.locator('option[value="'+value+'"]').count()),None)
        if control is None:raise ServiceError('sort_not_offered','The current Scopus result has no requested sort control',status='unsupported')
        previous_total=scopus_records(response.json())[1]
        previous_request=response.request.post_data_json;previous_sort=previous_request.get('sortBy');facets=previous_request.get('facetFilters') or []
        expected_sort=SCOPUS_SORT_REQUESTS[value]
        if control.input_value()==value:
            validate_primary_request(previous_request,query,expected_sort,facets)
            return response,None,expected_sort
        with page.expect_response(lambda r:urlsplit(r.url).hostname in self.hosts and urlsplit(r.url).path=='/gateway/documents/search'
                                  and r.request.method=='POST' and primary_request(r.request.post_data_json,query),timeout=SOURCE_WAIT_MS) as event:
            control.select_option(value)
        response=event.value
        if response.status!=200:raise ServiceError('provider_error','Scopus result sorting failed',http_status=response.status)
        rows,total,_=scopus_records(response.json())
        if total!=previous_total:raise ServiceError('result_set_mismatch','Scopus sorting changed the result set size')
        request=response.request.post_data_json;current_sort=validate_sort_transition(request,query,expected_sort,facets)
        if control.input_value()!=value:raise ServiceError('query_mismatch','Scopus result did not retain the selected sort control')
        evidence=self.store.put(encoded(response.json()),'application/json',self.source,response.url,role='sort_response',sort=value,total=total,received=len(rows))
        return response,evidence,current_sort

    def relationships(self,record):
        eid=record['eid']
        if not re.fullmatch(r'2-s2\.0-\d+',eid):
            raise ServiceError('invalid_target','The Scopus record has no canonical EID')
        page=self.page()
        goto_source(page,'https://'+urlsplit(page.url).hostname+'/pages/publications/'+eid.removeprefix('2-s2.0-'),self.hosts,wait_until='domcontentloaded',timeout=SOURCE_WAIT_MS)
        page.locator('#references').wait_for(timeout=SOURCE_WAIT_MS)
        dismiss_cookies(page)
        components={}
        for kind,tab,path in [('references','references','/gateway/doc-details/documents/'+eid+'/references'),('citations','citedBy','/gateway/citation-overview/documents/'+eid.removeprefix('2-s2.0-')+'/cited')]:
            records,evidence=[],[]
            total=None
            try:
                label=page.locator('#'+tab).inner_text()
                count=re.search(r'\(([\d,]+)\)',label)
                if not count:
                    raise ServiceError('relation_count_missing','Scopus did not display the relationship count')
                total=int(count[1].replace(',',''))
                if total:
                    def matches(response):
                        return urlsplit(response.url).hostname in self.hosts and urlsplit(response.url).path==path
                    with page.expect_response(matches,timeout=SOURCE_WAIT_MS) as event:
                        page.locator('#'+tab).click()
                    response=event.value
                    while True:
                        if response.status in (401,403):
                            raise ServiceError('access_restricted','Scopus restricted this relationship list',status='restricted')
                        if response.status!=200:
                            raise ServiceError('provider_error','Scopus relationship request failed',http_status=response.status)
                        payload=response.json()
                        evidence.append(self.store.put(encoded(payload),'application/json',self.source,response.url,role='relationship_response',eid=eid,relationship=kind))
                        if kind=='references':
                            rows,reported,offset=reference_records(payload)
                            if reported!=total or offset!=len(records):
                                raise ServiceError('range_mismatch','Scopus reference page or count changed',evidence=evidence[-1])
                        else:
                            rows=payload.get('documents')
                            if not isinstance(rows,list) or any(not isinstance(row,dict) or not row.get('eid') for row in rows):
                                raise ServiceError('invalid_response','Scopus returned no citing-document array')
                        records.extend(rows)
                        if len(records)==total:
                            break
                        if len(records)>total or not rows or kind=='citations':
                            raise ServiceError('incomplete_response','The relationship array does not match the document tab count')
                        next_button=page.locator('#references-panel').get_by_role('button',name='Next',exact=True)
                        if next_button.is_disabled():
                            raise ServiceError('incomplete_response','Scopus disabled Next before the reference list was complete')
                        with page.expect_response(matches,timeout=SOURCE_WAIT_MS) as event:
                            next_button.click()
                        response=event.value
                status={'status':'available'}
            except ServiceError as error:
                status=error.result
            except Exception as error:
                status={'status':'error','code':'relationship_retrieval_failed',**failure_details(error)}
            artifact=self.store.put(encoded(records),'application/json',self.source,page.url,role='relationship_records',eid=eid,relationship=kind,total=total,received=len(records))
            components[kind]={**status,'artifact':artifact,'received':len(records),'total':total,'evidence':evidence,
                'search_metadata_count':record.get(kind,{}).get('count')}
        return {'status':'available' if all(c['status']=='available' for c in components.values()) else 'partial',**components,
                'scope':'Actual document reference/cited-by tabs; search-summary counts are preserved separately'}

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        if type(start) is not int or start < 0 or type(limit) is not int or not 1 <= limit <= 1000:
            raise ServiceError("invalid_range", "Scopus requires start >= 0 and limit 1..1000")
        if cursor or export not in (None, "json", "csv", "facet-counts", "ris", "bibtex"):
            raise ServiceError("invalid_options", "Use the native advanced query and current result options; pagination is start/limit")
        settings=search_options(options)
        page = self.page()
        goto_source(page, "https://" + urlsplit(page.url).hostname + "/pages/search/publications?type=advanced", self.hosts, wait_until="domcontentloaded", timeout=SOURCE_WAIT_MS)
        editor = page.locator('.monaco-editor[role="code"]')
        editor.wait_for(timeout=SOURCE_WAIT_MS)
        dismiss_cookies(page)
        forget_result_table_state(page)
        editor.click(position={"x": 120, "y": 35})
        page.keyboard.press("Control+A")
        page.keyboard.insert_text(query)

        with page.expect_response(lambda response: search_settled(self.hosts, query, response), timeout=SOURCE_WAIT_MS) as pending:
            page.locator('[data-testid="advanced-search-button"]').click()
        response = require_accepted_query(query, pending.value)
        if response.status!=200:raise ServiceError('provider_error','Scopus search failed',http_status=response.status)
        initial_request=response.request.post_data_json;validate_primary_request(initial_request,query,SCOPUS_SORT_REQUESTS['plf-f'],[])
        initial_payload=response.json();initial_rows,initial_total,initial_offset=scopus_records(initial_payload)
        if initial_total==0:
            proof=self.store.put(encoded(initial_payload),'application/json',self.source,response.url,role='source_response',query=query,offset=initial_offset,total=0)
            artifact=self.store.put(b'[]','application/json',self.source,page.url,role='records',query=query,start=start,requested=limit,total=0)
            candidates=self.store.put(b'[]','application/json',self.source,page.url,role='facet_candidates',field=settings['facet_preview'][0],
                scope='No facet candidates exist for this empty base result') if settings['facet_preview'] else None
            return {'status':'not_found','source':self.source,'query':query,'options':options,'sort':settings['sort_name'],'start':start,'requested':limit,
                'received':0,'total':0,'has_more':False,'next':None,'records':artifact,'export':artifact,'evidence':[proof],
                'export_error':None,'facet_groups':list(SCOPUS_FACET_GROUPS),'facet_candidates':candidates,'filter_evidence':[],
                'sort_evidence':None,'facet_status':'unavailable_empty_result','preview':[]}
        response,filter_evidence,facet_artifacts,facet_filters=self.apply_facets(page,response,query,settings['facet_filters'],[])
        response,sort_evidence,sort_by=self.apply_sort(page,response,query,settings['sort'])
        final_request=response.request.post_data_json
        if sort_by is None:sort_by=final_request.get('sortBy')
        if facet_filters is None:facet_filters=final_request.get('facetFilters') or []
        preview_artifact=None
        if settings['facet_preview']:
            field,section,facet_query=settings['facet_preview'];candidates,_=self.facet_candidates(page,field,section,facet_query)
            public_candidates=[{key:item[key] for key in ('label','count')} for item in candidates]
            preview_artifact=self.store.put(encoded(public_candidates),'application/json',self.source,page.url,role='facet_candidates',field=field,query=facet_query,
                scope='Current visible candidates from one Scopus result facet')
        rows, evidence, total, offset = [], [*filter_evidence,*([sort_evidence] if sort_evidence else [])], None, 0
        seen_eids=set()
        pagination_error=None
        while True:
            if response.status in (401, 403):
                raise ServiceError("access_restricted", "Scopus restricted the institution session", status="restricted")
            if response.status != 200:
                raise ServiceError("provider_error", "Scopus search failed", http_status=response.status)
            validate_primary_request(response.request.post_data_json,query,sort_by,facet_filters)
            payload = response.json()
            native, observed_total, observed_offset = scopus_records(payload,check_unique=False)
            if observed_offset != offset or total is not None and observed_total != total:
                raise ServiceError("range_mismatch", "Scopus returned a changed result range")
            total = observed_total
            proof=self.store.put(encoded(payload), "application/json", self.source, response.url,
                role="source_response", query=query, offset=offset, total=total);evidence.append(proof)
            try:page_eids=unique_primary_ids(native,seen_eids)
            except ServiceError as error:
                if not seen_eids:raise
                pagination_error={**error.result,'page_offset':offset,'evidence':proof};break
            seen_eids.update(page_eids)
            rows.extend(row for i, row in enumerate(native, offset) if start <= i < start + limit)
            offset += len(native)
            if offset >= min(start + limit, total) or not native:
                break
            with page.expect_response(lambda response: search_settled(self.hosts, query, response), timeout=SOURCE_WAIT_MS) as pending:
                page.get_by_role("button", name="Next", exact=True).click()
            response = require_accepted_query(query, pending.value)
        artifact = self.store.put(encoded(rows), "application/json", self.source, page.url,
            role="records", query=query, start=start, requested=limit, total=total)
        exported = artifact
        export_error=None
        if export == "csv" and not pagination_error:
            stream = io.StringIO(newline="")
            fields = list(dict.fromkeys(k for row in rows for k in row))
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v for k, v in row.items()} for row in rows)
            exported = self.store.put(stream.getvalue(), "text/csv", self.source, page.url,
                role="mechanical_export", format="csv", parent_ref=artifact["ref"])
        if export=='facet-counts' and not pagination_error:
            try:exported=self.facet_count_export(page,query,total,facet_filters)
            except ServiceError as error:
                export_error=error.result;exported={'status':'error',**error.result,'records':artifact}
        if export in ("ris", "bibtex") and not pagination_error:
            exported = {"status": "unsupported", "code": "export_deferred",
                "reason": "Native export requires a separate web account and is deferred by user instruction; JSON records remain available"}
            export_error=exported
        more = offset < total if pagination_error else start + len(rows) < total
        next_start=offset if pagination_error else start+len(rows)
        return {"status": "partial" if pagination_error or export_error and rows else "error" if export_error else "ok" if rows else "not_found", "source": self.source,
            "query": query,"options":options,"sort":settings['sort_name'], "start": start, "requested": limit, "received": len(rows), "total": total,
            "has_more": more, "next": {"start": next_start} if more else None,
            "records": artifact, "export": exported, "evidence": evidence,
            "export_error":export_error,
            "pagination_error":pagination_error,
            "facet_groups":list(SCOPUS_FACET_GROUPS),"facet_candidates":preview_artifact,
            "filter_evidence":filter_evidence,"sort_evidence":sort_evidence,
            "preview": [{k: r.get(k) for k in ("eid", "title", "pubYear", "doi")} for r in rows[:3]]}

    def fetch(self, target, *, parts):
        from api_adapters import doi
        if target.startswith(("http://", "https://")):
            parsed = urlsplit(target)
            if parsed.hostname in self.hosts:
                identifiers = parse_qs(parsed.query).get("eid", [])
                matched = re.search(r"/(2-s2\.0-\d+)(?:/|$)", parsed.path)
                publication = re.fullmatch(r"/pages/publications/(\d+)/?", parsed.path)
                target = identifiers[0] if len(identifiers) == 1 else matched[1] if matched else '2-s2.0-'+publication[1] if publication else ""
                if not re.fullmatch(r"2-s2\.0-\d+", target):
                    raise ServiceError("invalid_target", "This Scopus URL contains no document EID")
            elif parsed.hostname not in ("doi.org", "dx.doi.org"):
                raise ServiceError("source_boundary", "Use a Scopus document URL or DOI")
        if re.fullmatch(r"2-s2\.0-\d+", target):
            query = "EID(" + target + ")"
        else:
            try:
                query = 'DOI("' + doi(target) + '")'
            except ServiceError:
                result = self.search('TITLE("' + target.replace('"', " ") + '")', options={}, limit=20)
                result["status"] = "selection_required" if result["received"] else "not_found"
                return result
        result = self.search(query, options={}, limit=2)
        if result["total"] != 1:
            result["status"] = "selection_required" if result["received"] else "not_found"
            return result
        record = json.loads(self.store.read(result["records"]["ref"])[1])[0]
        components = {}
        for part in parts:
            if part in ("metadata", "export"):
                components[part] = {"status": "available", "artifact": result["records"], "format": "json"}
            elif part == "abstract":
                components[part] = {"status": "available", "artifact": result["records"]} if record.get("abstractText") else {"status": "not_found", "reason": "The Scopus record has no abstractText"}
            elif part == "fulltext":
                components[part] = {"status": "unsupported", "reason": "Scopus indexes documents; select the publisher separately for its full text"}
            elif part == "supplementary":
                try:
                    components[part] = self.relationships(record)
                except ServiceError as error:
                    components[part] = error.result
            else:
                raise ServiceError("invalid_parts", "Unknown requested content", part=part)
        return {"status": "ok" if all(v["status"] == "available" for v in components.values()) else "partial",
            "source": self.source, "target": target, "records": result["records"], "components": components, "evidence": result["evidence"]}

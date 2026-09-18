"""JSTOR's native grouped-search JSON, requested windows and citation exports."""
import base64,csv,io,json,re
from urllib.parse import urljoin,urlsplit
from bs4 import BeautifulSoup
from scholarly import ServiceError, encoded, failure_details
from browser_adapters import is_access_challenge,clean_html
from waits import SOURCE_WAIT_MS

FACETS={'content_types':'cty','subjects':'disc','languages':'la_str'}
SORTS={'relevance':('rel',None),'newest':('new',None),'oldest':('old',None),
    'title_asc':('item_title_str','asc'),'title_desc':('item_title_str','desc'),
    'creator_asc':('primary_agents_str','asc'),'creator_desc':('primary_agents_str','desc'),'resolution':('cc_media_resolution','desc')}


def group_key(value):
    try:types=json.loads(base64.b64decode(value,validate=True))
    except (ValueError,TypeError):raise ServiceError('invalid_response','JSTOR group filter is not a native type array') from None
    if not isinstance(types,list) or any(not isinstance(t,str) for t in types):
        raise ServiceError('invalid_response','JSTOR group filter has invalid type labels')
    return frozenset(types)


def facet_key(field,value):
    # JSTOR can omit the duplicate EN variant when rendering the selected English group.
    return frozenset(part.strip().casefold() for part in value.split(' OR ')) if field=='la_str' and isinstance(value,str) else value


def search_pages(raw,query,number,expected_start=None):
    from jstor import stable_id
    if not isinstance(raw,dict) or type(raw.get('totalResultCount')) is not int or raw['totalResultCount']<0:
        raise ServiceError('invalid_response','JSTOR returned no valid search total')
    if raw.get('errors'):raise ServiceError('search_rejected','JSTOR reported errors for the submitted query')
    if raw.get('searchQuery')!=query:raise ServiceError('query_mismatch','JSTOR did not retain the requested query')
    source_total=raw['totalResultCount'];columns=raw.get('groupedResults')
    if not isinstance(columns,dict):raise ServiceError('invalid_response','JSTOR returned no grouped results')
    groups=[group for column in columns.values() if isinstance(column,dict) for group in column.get('results',[]) if isinstance(group,dict) and 'results' in group]
    if not groups and source_total==0:return [{'rows':[],'start':0,'total':0,'source_total':0,'paging':{},'group':None}]
    if not groups:raise ServiceError('invalid_response','JSTOR omitted its nonempty result groups')
    return [parse_group(group,source_total,number,expected_start) for group in groups]


def search_page(raw,query,number,expected_start=None):
    pages=search_pages(raw,query,number,expected_start)
    if len(pages)!=1:raise ServiceError('range_mismatch','JSTOR returned more than the requested continuation group')
    return pages[0]


def parse_group(group,source_total,number,expected_start):
    from jstor import stable_id
    paging=group.get('paging',{});items=group.get('results')
    if not isinstance(items,list) or any(type(paging.get(k)) is not int for k in ('page_start_index','page_end_index','total_results','page_index')):
        raise ServiceError('invalid_response','JSTOR returned no complete native page range')
    first=paging['page_start_index']-1;total=paging['total_results']
    page_size=5 if group.get('comp_label')=='carousel' and number==1 else 25
    expected_start=(number-1)*25 if expected_start is None else expected_start
    if paging['page_index']!=number or first!=expected_start or paging['page_end_index']!=first+len(items) or len(items)!=min(page_size,max(0,total-first)):
        raise ServiceError('range_mismatch','JSTOR returned a repeated or inconsistent result page')
    rows=[];seen=set()
    for item in items:
        if not isinstance(item,dict) or not isinstance(item.get('stable_url'),str):
            raise ServiceError('invalid_response','JSTOR result has no stable document URL')
        url=urljoin('https://www.jstor.org',item['stable_url']);identifier=stable_id(url)
        if identifier in seen:raise ServiceError('range_mismatch','JSTOR repeated an item within its page')
        seen.add(identifier);citation=item.get('citation_line','')
        rows.append({'id':identifier,'uuid':item.get('id'),'doi':item.get('doi'),'title':item.get('result_title_text') or ' '.join(item.get('title',[])),
            'authors':item.get('author',[]),'url':url,'type':item.get('human_readable_type',item.get('resource_type')),'native_type':item.get('type'),
            'citation_html':citation,'citation_text':BeautifulSoup(citation,'html.parser').get_text(' ',strip=True),
            'publication_date_display':item.get('result_date_string'),'year':item.get('year'),
            'has_access':item.get('userHasAccess',item.get('has_access')),'flags':item.get('flags',[])})
        if 'primary_agents' in item:rows[-1]['creators']=item['primary_agents']
    return {'rows':rows,'start':first,'total':total,'source_total':source_total,'paging':paging,'group':group.get('comp_label')}


def public_payload(value):
    if isinstance(value,dict):
        return {key:('[REDACTED]' if key in ('tokens','register_and_read_entitlement_id','requestId','ab_segment') else public_payload(item)) for key,item in value.items()}
    if isinstance(value,list):return [public_payload(item) for item in value]
    return value


def native_request(adapter,payload,endpoint,role,request):
    if adapter.gateway is None:raise ServiceError('browser_session_unavailable','JSTOR institutional API session is not configured',status='restricted')
    hosts={'www.jstor.org','jstor.org','www-jstor-org.libproxy.knu.ac.kr','jstor-org.libproxy.knu.ac.kr'}
    page=adapter.gateway.open('jstor','JSTOR',hosts,'body')
    url='https://'+urlsplit(page.url).hostname+'/search-results/'+endpoint+'/'
    try:response=adapter.gateway.context.request.post(url,data=json.dumps(payload),headers={'Content-Type':'application/json'},max_redirects=0,timeout=SOURCE_WAIT_MS)
    except Exception as error:raise ServiceError('search_connection_failed','JSTOR search API connection failed',**failure_details(error)) from None
    if response.status in (401,403):raise ServiceError('access_restricted','JSTOR restricted its search API',status='restricted')
    if response.status==429:raise ServiceError('rate_limited','JSTOR search request limit reached',retry_after=response.headers.get('retry-after'))
    if response.status!=200:raise ServiceError('provider_error','JSTOR search API did not return a successful response',http_status=response.status)
    data=response.body()
    try:raw=json.loads(data)
    except ValueError:
        if is_access_challenge(data):raise ServiceError('publisher_access_challenge','JSTOR search API requires access verification',status='restricted') from None
        raise ServiceError('invalid_response','JSTOR search API returned no JSON') from None
    evidence=adapter.store.put(encoded(public_payload(raw)),'application/json',adapter.source,url,role=role,request=request,
        redacted_fields=['tokens','register_and_read_entitlement_id','requestId','ab_segment'])
    return raw,evidence


def request_page(adapter,payload):
    return native_request(adapter,payload,'grouped-search','native_search_response',
        {key:payload[key] for key in ('searchTerm','pageNumber','pageParams','sort','sortOrder','acc','startDate','endDate','msFacetFields') if key in payload})


def apply_snippets(rows,raw,query,sanitizer=None):
    from jstor import stable_id
    from scholarly import Sanitizer
    sanitizer=sanitizer or Sanitizer()
    if not isinstance(raw,dict) or not isinstance(raw.get('results'),list):
        raise ServiceError('invalid_response','JSTOR returned no snippet results')
    if raw.get('errors'):raise ServiceError('snippet_error','JSTOR reported errors while preparing snippets')
    expected={row['id'] for row in rows};snippets={}
    for item in raw['results']:
        if not isinstance(item,dict) or not isinstance(item.get('id'),str) or not isinstance(item.get('text'),str):
            raise ServiceError('invalid_response','JSTOR returned a malformed snippet')
        identifier=stable_id(item['id'])
        if identifier not in expected or identifier in snippets:
            raise ServiceError('snippet_identity_mismatch','JSTOR snippets contain an unrequested or repeated document')
        html=clean_html(item['text'],sanitizer)
        snippets[identifier]={'status':'available' if item['text'].strip() else 'not_offered','query':query,
            'html':html,'text':BeautifulSoup(html,'html.parser').get_text(' ',strip=True)}
    for row in rows:row['snippet']=snippets.get(row['id'],{'status':'not_offered','query':query,'reason':'No snippet was returned for this document and query'})


def request_snippets(adapter,rows,query):
    if any(not isinstance(row.get('uuid'),str) or not isinstance(row.get('native_type'),str) for row in rows):
        raise ServiceError('snippet_identity_missing','A selected record lacks its native snippet request identity')
    inner={'items':[{'id':row['uuid'],'type':row['native_type']} for row in rows],'query':query}
    return native_request(adapter,{'snippetParams':json.dumps(inner)},'snippets','native_search_snippets',inner)


def search(adapter,query,*,options,start=0,limit=20,cursor=None,export=None):
    if type(start) is not int or start<0 or type(limit) is not int or not 1<=limit<=1000:
        raise ServiceError('invalid_range','Use start >= 0 and limit 1..1000')
    if cursor or set(options)-({'sort','access','start_date','end_date','snippets','facets'}|set(FACETS)):
        raise ServiceError('invalid_options','Use documented JSTOR sort, access, dates and facets; paginate with start')
    if not isinstance(query,str) or not query.strip():raise ServiceError('invalid_query','Provide a nonempty native JSTOR query')
    if export not in (None,'json','csv','native','bibtex','ris'):raise ServiceError('invalid_export','Use json, csv, native, bibtex or ris')
    if type(options.get('snippets',False)) is not bool:raise ServiceError('invalid_options','snippets must be boolean')
    sort=options.get('sort','relevance');access=options.get('access','available')
    if sort not in SORTS or access not in ('available','all'):
        raise ServiceError('invalid_options','Use a documented sort and access=available/all')
    dates={};bounds={}
    for key in ('start_date','end_date'):
        value=options.get(key,'')
        if isinstance(value,str) and re.fullmatch(r'-\d{1,4}',value):
            year=int(value)
            if year==0:raise ServiceError('invalid_options','Civil BCE/CE dates have no year zero')
            bounds[key]=(year,1,1) if key=='start_date' else (year,12,31)
            dates[key]=str(year);continue
        if not isinstance(value,str) or value and not re.fullmatch(r'\d{4}(?:/\d{2}(?:/\d{2})?)?',value):
            raise ServiceError('invalid_options','Use CE YYYY, YYYY/MM, YYYY/MM/DD or a negative BCE year such as -0500')
        if value:
            import datetime,calendar
            pieces=[int(x) for x in value.split('/')]
            try:
                month=pieces[1] if len(pieces)>1 else 1 if key=='start_date' else 12
                day=pieces[2] if len(pieces)>2 else 1 if key=='start_date' else calendar.monthrange(pieces[0],month)[1]
                valid=datetime.date(pieces[0],month,day);bounds[key]=(valid.year,valid.month,valid.day)
            except ValueError:raise ServiceError('invalid_options','Date is outside the calendar range') from None
        dates[key]=value
    if dates['start_date'] and dates['end_date'] and bounds['start_date']>bounds['end_date']:
        raise ServiceError('invalid_options','start_date must not follow end_date')
    acc='on' if access=='available' else 'off';applied={'access':acc};fields=[]
    requested_facets={field:options.get(option,[]) for option,field in FACETS.items()}
    additional=options.get('facets',{})
    if not isinstance(additional,dict):raise ServiceError('invalid_options','facets maps a returned field to a list of native label values')
    for field,values in additional.items():
        if not isinstance(field,str) or not field or requested_facets.get(field):raise ServiceError('invalid_options','A native facet field must be named once')
        requested_facets[field]=values
    for field,values in requested_facets.items():
        if not isinstance(values,list) or any(not isinstance(x,str) or not x.strip() for x in values) or len(values)!=len(set(values)):
            raise ServiceError('invalid_options','Facet values must be a list of distinct nonempty native labels',field=field)
        if values:
            wire_values=[field+'#'+value for value in values] if field=='cc_portal_id' else values
            fields.append({'field':field,'efq':[base64.b64encode(x.encode()).decode() for x in wire_values]});applied[field]=wire_values
    if SORTS[sort][1] and (not requested_facets['cty'] or not set(requested_facets['cty'])<={'contributed_images','contributed_panoramas'}):
        raise ServiceError('invalid_options','Image-specific sorts require image or panorama content_types')
    payload={'acc':acc,'allowEmptyQuery':False,'endDate':dates['end_date'],'startDate':dates['start_date'],
        'forwardedAdvancedSearchParams':{'Query':query},'isAdvancedSearch':False,'msFacetFields':fields,'pageParams':{},'pageNumber':1,
        'pageType':'basic_search_page','searchTerm':query,'theme':'','filterQueries':[],'sort':SORTS[sort][0],
        'tabType':'keyword','content_set_flags':[],'appliedFacets':applied}
    if SORTS[sort][1]:payload['sortOrder']=SORTS[sort][1]
    for key in ('startDate','endDate'):
        if payload[key]:applied[key]=payload[key]
    selected=[];proofs=[];errors=[];seen=set();groups=[];page_errors=[]
    raw,proof=request_page(adapter,payload);proofs.append(proof)
    try:
        initial=search_pages(raw,query,1)
        if raw.get('acc')!=acc:raise ServiceError('filter_mismatch','JSTOR did not retain the requested access scope')
        if raw['totalResultCount']:
            queue=list(raw.get('facets',[]));selected_facets={}
            while queue:
                facet=queue.pop()
                if not isinstance(facet,dict):continue
                queue.extend(facet.get('h_values',[]))
                if facet.get('field'):
                    selected_facets.setdefault(facet['field'],set()).update(facet_key(facet['field'],v.get('label')) for v in facet.get('values',[]) if v.get('selected'))
            for field,values in requested_facets.items():
                if {facet_key(field,value) for value in values}-selected_facets.get(field,set()):
                    raise ServiceError('filter_mismatch','JSTOR did not retain a requested facet',field=field)
    except ServiceError as error:
        error.result['evidence']=proofs;raise
    source_total=raw['totalResultCount'];facets=raw.get('facets',[])
    total=sum(found['total'] for found in initial);group=initial[0]['group'] if len(initial)==1 else None
    for first in initial:
        found=first;local=[];number=1;failure=None
        while True:
            try:
                if found is first and first['group']=='carousel':
                    # Carousel previews are not a prefix of the full group's relevance order.
                    raw,proof=request_page(adapter,{**payload,'pageParams':{'groupEfq':first['paging']['group_efq']}});proofs.append(proof)
                    found=search_page(raw,query,1,0)
                    if raw.get('acc')!=acc or found['total']!=first['total'] or group_key(found['paging'].get('group_efq'))!=group_key(first['paging']['group_efq']):
                        raise ServiceError('range_mismatch','JSTOR expanded a different result group')
                if seen&{row['id'] for row in found['rows']}:raise ServiceError('range_mismatch','JSTOR repeated records across pages or groups')
                seen.update(row['id'] for row in found['rows'])
                local.extend({**row,'result_group':first['group']} for i,row in enumerate(found['rows'],found['start']) if start<=i<start+limit)
                following=found['start']+len(found['rows'])
                if following>=min(first['total'],start+limit):break
                paging=found['paging']
                if not isinstance(paging.get('next'),str) or not isinstance(paging.get('group_efq'),str):
                    raise ServiceError('pagination_control_missing','JSTOR omitted its next page mark')
                number+=1
                next_payload={**payload,'pageNumber':number,'pageParams':{'groupEfq':paging['group_efq'],'pageMark':paging['next']}}
                raw,proof=request_page(adapter,next_payload);proofs.append(proof)
                found=search_page(raw,query,number,following)
                if raw.get('acc')!=acc or group_key(found['paging'].get('group_efq'))!=group_key(paging['group_efq']) or found['total']!=first['total']:
                    raise ServiceError('range_mismatch','JSTOR changed the access scope, result group or total during pagination')
            except ServiceError as error:
                page_errors.append(error);errors.append(error.result);failure=error.result;break
        selected.extend(local)
        groups.append({'group':first['group'],'start':start,'requested':limit,'received':len(local),'total':first['total'],
            'has_more':start+len(local)<first['total'],'status':'partial' if failure else 'ok' if local else 'not_found',**({'error':failure} if failure else {})})
    if page_errors and not selected:
        page_errors[0].result['evidence']=proofs;raise page_errors[0]
    snippet_proofs=[]
    if options.get('snippets'):
        for offset in range(0,len(selected),25):
            chunk=selected[offset:offset+25]
            try:
                raw,proof=request_snippets(adapter,chunk,query);snippet_proofs.append(proof)
                apply_snippets(chunk,raw,query,adapter.store.sanitizer)
            except ServiceError as error:
                errors.append(error.result)
                for row in chunk:row['snippet']={**error.result,'query':query}
    artifact=adapter.store.put(encoded(selected),'application/json',adapter.source,proofs[0]['url'],role='records',query=query,options=options,
        start=start,total=total,source_total=source_total,evidence_refs=[p['ref'] for p in proofs])
    facet_artifact=adapter.store.put(encoded(facets),'application/json',adapter.source,proofs[0]['url'],role='native_facets',parent_ref=artifact['ref'])
    exported=artifact
    if export=='native':exported={'artifacts':proofs,'scope':'Whole native result pages with session fields redacted; records is the requested window'}
    elif export=='csv':
        stream=io.StringIO(newline='');keys=list(dict.fromkeys(k for row in selected for k in row));writer=csv.DictWriter(stream,fieldnames=keys);writer.writeheader()
        writer.writerows({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in row.items()} for row in selected)
        exported=adapter.store.put(stream.getvalue(),'text/csv',adapter.source,proofs[0]['url'],role='mechanical_export',parent_ref=artifact['ref'])
    elif export in ('bibtex','ris'):
        files=[];failures=[]
        for row in selected:
            try:
                _,native=adapter.citation(row['id'],export);files.append({'id':row['id'],'artifact':native})
            except ServiceError as error:failures.append({'id':row['id'],**error.result})
        exported={'status':'partial' if failures else 'available','artifacts':files,'errors':failures,'format':export}
        errors.extend(failures)
    more=any(g['has_more'] for g in groups)
    return {'status':'partial' if errors else 'ok' if selected else 'not_found','source':adapter.source,'query':query,'options':options,
        'start':start,'requested':limit,'received':len(selected),'total':total,'source_total':source_total,'result_group':group,
        'result_groups':groups,'scope':'start and limit apply separately to each native result group; records retain group identity in source group order. source_total may count groups not returned by this search view.',
        'has_more':more,'next':{'start':start+limit} if more and not page_errors else None,
        'retry':{'start':start,'limit':limit} if page_errors else None,'records':artifact,'export':exported,'evidence':proofs,'facets':facet_artifact,'errors':errors,
        'snippet_evidence':snippet_proofs,'preview':[{k:row[k] for k in ('id','title','doi','url')} for row in selected[:3]],'retrieval':'native_search_api','access':'institutional_proxy'}

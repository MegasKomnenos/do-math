"""JSTOR's native grouped-search JSON, requested windows and citation exports."""
import base64,csv,io,json,re
from urllib.parse import urljoin,urlsplit
from bs4 import BeautifulSoup
from scholarly import ServiceError,encoded
from browser_adapters import is_access_challenge

FACETS={'content_types':'cty','subjects':'disc','languages':'la_str'}


def facet_key(field,value):
    # JSTOR can omit the duplicate EN variant when rendering the selected English group.
    return frozenset(part.strip().casefold() for part in value.split(' OR ')) if field=='la_str' and isinstance(value,str) else value


def search_page(raw,query,number):
    from jstor import stable_id
    if not isinstance(raw,dict) or type(raw.get('totalResultCount')) is not int or raw['totalResultCount']<0:
        raise ServiceError('invalid_response','JSTOR returned no valid search total')
    if raw.get('errors'):raise ServiceError('search_rejected','JSTOR reported errors for the submitted query')
    if raw.get('searchQuery')!=query:raise ServiceError('query_mismatch','JSTOR did not retain the requested query')
    source_total=raw['totalResultCount'];columns=raw.get('groupedResults')
    if not isinstance(columns,dict):raise ServiceError('invalid_response','JSTOR returned no grouped results')
    groups=[group for column in columns.values() if isinstance(column,dict) for group in column.get('results',[]) if isinstance(group,dict) and 'results' in group]
    if not groups and source_total==0:return {'rows':[],'start':0,'total':0,'source_total':0,'paging':{},'group':None}
    if len(groups)!=1:raise ServiceError('result_groups_not_implemented','Select a content type yielding one native result group',status='not_implemented',groups=len(groups))
    group=groups[0];paging=group.get('paging',{});items=group.get('results')
    if not isinstance(items,list) or any(type(paging.get(k)) is not int for k in ('page_start_index','page_end_index','total_results','page_index')):
        raise ServiceError('invalid_response','JSTOR returned no complete native page range')
    first=paging['page_start_index']-1;total=paging['total_results']
    if paging['page_index']!=number or first!=(number-1)*25 or paging['page_end_index']!=first+len(items) or len(items)!=min(25,max(0,total-first)):
        raise ServiceError('range_mismatch','JSTOR returned a repeated or inconsistent result page')
    rows=[];seen=set()
    for item in items:
        if not isinstance(item,dict) or not isinstance(item.get('stable_url'),str):
            raise ServiceError('invalid_response','JSTOR result has no stable document URL')
        url=urljoin('https://www.jstor.org',item['stable_url']);identifier=stable_id(url)
        if identifier in seen:raise ServiceError('range_mismatch','JSTOR repeated an item within its page')
        seen.add(identifier);citation=item.get('citation_line','')
        rows.append({'id':identifier,'uuid':item.get('id'),'doi':item.get('doi'),'title':item.get('result_title_text') or ' '.join(item.get('title',[])),
            'authors':item.get('author',[]),'url':url,'type':item.get('human_readable_type',item.get('resource_type')),
            'citation_html':citation,'citation_text':BeautifulSoup(citation,'html.parser').get_text(' ',strip=True),
            'publication_date_display':item.get('result_date_string'),'year':item.get('year'),
            'has_access':item.get('userHasAccess',item.get('has_access')),'flags':item.get('flags',[])})
    return {'rows':rows,'start':first,'total':total,'source_total':source_total,'paging':paging,'group':group.get('comp_label')}


def public_payload(value):
    if isinstance(value,dict):
        return {key:('[REDACTED]' if key in ('tokens','register_and_read_entitlement_id','requestId','ab_segment') else public_payload(item)) for key,item in value.items()}
    if isinstance(value,list):return [public_payload(item) for item in value]
    return value


def request_page(adapter,payload):
    if adapter.gateway is None:raise ServiceError('browser_session_unavailable','JSTOR institutional API session is not configured',status='restricted')
    hosts={'www.jstor.org','jstor.org','www-jstor-org.libproxy.knu.ac.kr','jstor-org.libproxy.knu.ac.kr'}
    page=adapter.gateway.open('jstor','JSTOR',hosts,'body')
    url='https://'+urlsplit(page.url).hostname+'/search-results/grouped-search/'
    try:response=adapter.gateway.context.request.post(url,data=json.dumps(payload),headers={'Content-Type':'application/json'},max_redirects=0,timeout=45000)
    except Exception as error:raise ServiceError('search_connection_failed','JSTOR search API connection failed',error_type=type(error).__name__) from None
    if response.status in (401,403):raise ServiceError('access_restricted','JSTOR restricted its search API',status='restricted')
    if response.status==429:raise ServiceError('rate_limited','JSTOR search request limit reached',retry_after=response.headers.get('retry-after'))
    if response.status!=200:raise ServiceError('provider_error','JSTOR search API did not return a successful response',http_status=response.status)
    data=response.body()
    try:raw=json.loads(data)
    except ValueError:
        if is_access_challenge(data):raise ServiceError('publisher_access_challenge','JSTOR search API requires access verification',status='restricted') from None
        raise ServiceError('invalid_response','JSTOR search API returned no JSON') from None
    evidence=adapter.store.put(encoded(public_payload(raw)),'application/json',adapter.source,url,role='native_search_response',
        request={key:payload[key] for key in ('searchTerm','pageNumber','pageParams','sort','acc','startDate','endDate','msFacetFields')},
        redacted_fields=['tokens','register_and_read_entitlement_id','requestId','ab_segment'])
    return raw,evidence


def search(adapter,query,*,options,start=0,limit=20,cursor=None,export=None):
    if type(start) is not int or start<0 or type(limit) is not int or not 1<=limit<=1000:
        raise ServiceError('invalid_range','Use start >= 0 and limit 1..1000')
    if cursor or set(options)-({'sort','access','start_date','end_date'}|set(FACETS)):
        raise ServiceError('invalid_options','Use documented JSTOR sort, access, dates and facets; paginate with start')
    if not isinstance(query,str) or not query.strip():raise ServiceError('invalid_query','Provide a nonempty native JSTOR query')
    if export not in (None,'json','csv','native','bibtex','ris'):raise ServiceError('invalid_export','Use json, csv, native, bibtex or ris')
    sort=options.get('sort','relevance');access=options.get('access','available')
    if sort not in ('relevance','newest','oldest') or access not in ('available','all'):
        raise ServiceError('invalid_options','sort is relevance/newest/oldest; access is available/all')
    dates={};bounds={}
    for key in ('start_date','end_date'):
        value=options.get(key,'')
        if not isinstance(value,str) or value and not re.fullmatch(r'\d{4}(?:/\d{2}(?:/\d{2})?)?',value):
            raise ServiceError('invalid_options','Dates use YYYY, YYYY/MM or YYYY/MM/DD')
        if value:
            import datetime,calendar
            pieces=[int(x) for x in value.split('/')]
            try:
                month=pieces[1] if len(pieces)>1 else 1 if key=='start_date' else 12
                day=pieces[2] if len(pieces)>2 else 1 if key=='start_date' else calendar.monthrange(pieces[0],month)[1]
                bounds[key]=datetime.date(pieces[0],month,day)
            except ValueError:raise ServiceError('invalid_options','Date is outside the calendar range') from None
        dates[key]=value
    if dates['start_date'] and dates['end_date'] and bounds['start_date']>bounds['end_date']:
        raise ServiceError('invalid_options','start_date must not follow end_date')
    acc='on' if access=='available' else 'off';applied={'access':acc};fields=[]
    for option,field in FACETS.items():
        values=options.get(option,[])
        if not isinstance(values,list) or any(not isinstance(x,str) or not x.strip() for x in values) or len(values)!=len(set(values)):
            raise ServiceError('invalid_options','Facet values must be a list of distinct nonempty native labels',field=option)
        if values:
            fields.append({'field':field,'efq':[base64.b64encode(x.encode()).decode() for x in values]});applied[field]=values
    payload={'acc':acc,'allowEmptyQuery':False,'endDate':dates['end_date'],'startDate':dates['start_date'],
        'forwardedAdvancedSearchParams':{'Query':query},'isAdvancedSearch':False,'msFacetFields':fields,'pageParams':{},'pageNumber':1,
        'pageType':'basic_search_page','searchTerm':query,'theme':'','filterQueries':[],'sort':{'relevance':'rel','newest':'new','oldest':'old'}[sort],
        'tabType':'keyword','content_set_flags':[],'appliedFacets':applied}
    for key in ('startDate','endDate'):
        if payload[key]:applied[key]=payload[key]
    selected=[];proofs=[];errors=[];total=source_total=None;seen=set();facets=None;group=None
    while True:
        try:
            raw,proof=request_page(adapter,payload);proofs.append(proof)
            found=search_page(raw,query,payload['pageNumber'])
            if raw.get('acc')!=acc:raise ServiceError('filter_mismatch','JSTOR did not retain the requested access scope')
            if found['total']:
                queue=list(raw.get('facets',[]));selected_facets={}
                while queue:
                    facet=queue.pop()
                    if not isinstance(facet,dict):continue
                    queue.extend(facet.get('h_values',[]))
                    if facet.get('field'):
                        selected_facets.setdefault(facet['field'],set()).update(facet_key(facet['field'],v.get('label')) for v in facet.get('values',[]) if v.get('selected'))
                for option,field in FACETS.items():
                    if {facet_key(field,value) for value in options.get(option,[])}-selected_facets.get(field,set()):
                        raise ServiceError('filter_mismatch','JSTOR did not retain a requested facet',field=option)
            if total is not None and total!=found['total']:raise ServiceError('range_mismatch','JSTOR changed the result group total during pagination')
            if total is None:source_total=found['source_total'];facets=raw.get('facets',[]);group=found['group']
            total=found['total']
            if seen&{row['id'] for row in found['rows']}:raise ServiceError('range_mismatch','JSTOR repeated records across pages')
            seen.update(row['id'] for row in found['rows'])
            selected.extend(row for i,row in enumerate(found['rows'],found['start']) if start<=i<start+limit)
            if found['start']+len(found['rows'])>=min(total,start+limit):break
            paging=found['paging']
            if not isinstance(paging.get('next'),str) or not isinstance(paging.get('group_efq'),str):
                raise ServiceError('pagination_control_missing','JSTOR omitted its next page mark')
            payload={**payload,'pageNumber':payload['pageNumber']+1,'pageParams':{'groupEfq':paging['group_efq'],'pageMark':paging['next']}}
        except ServiceError as error:
            if not selected:
                if proofs:error.result['evidence']=proofs
                raise
            errors.append(error.result);break
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
    more=start+len(selected)<total
    return {'status':'partial' if errors else 'ok' if selected else 'not_found','source':adapter.source,'query':query,'options':options,
        'start':start,'requested':limit,'received':len(selected),'total':total,'source_total':source_total,'result_group':group,
        'scope':'Native paginated result group; the initial source_total may also count other media groups. Select content_types for their own result groups.',
        'has_more':more,'next':{'start':start+len(selected)} if more else None,'records':artifact,'export':exported,'evidence':proofs,'facets':facet_artifact,'errors':errors,
        'preview':[{k:row[k] for k in ('id','title','doi','url')} for row in selected[:3]],'retrieval':'native_search_api','access':'institutional_proxy'}

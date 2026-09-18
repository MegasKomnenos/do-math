"""Native IOP ranked search windows; the RSS feed has a separate scope."""
import re,json,csv,io
from urllib.parse import urljoin,urlsplit,unquote,urlencode
from bs4 import BeautifulSoup
from browser_adapters import clean_html,is_access_challenge,goto_source
from scholarly import Sanitizer, ServiceError, encoded, failure_details
from waits import SOURCE_WAIT_MS


def applied_filters(soup):
    result={}
    for name in ('journals','pubType','accessType','searchDatePeriod'):
        selected={n.get('value') for n in soup.select('input[name="'+name+'"][checked]')}
        if not selected:selected={n.get('value') for n in soup.select('input[name="'+name+'"][type=hidden]') if n.get('value')}
        result[name]=selected
    return result


def search_records(raw,base):
    if is_access_challenge(raw):raise ServiceError('publisher_access_challenge','IOP returned an access verification page',status='restricted')
    soup=BeautifulSoup(raw,'html.parser');text=soup.get_text(' ',strip=True)
    ranges={tuple(int(v.replace(',','')) for v in match) for match in re.findall(r'Showing\s+([\d,]+)\s*[-–]\s*([\d,]+)\s+of\s+([\d,]+)',text,re.I)}
    if not ranges and not soup.select('.art-list-item') and any(re.search(r'\breturned\s+0\s+results\b',h.get_text(' ',strip=True),re.I) for h in soup.select('h1')):
        return {'rows':[],'start':0,'accessible_total':0,'total':0,'source_window_limit':None,'count_scope':'reported_matches'}
    if len(ranges)!=1:raise ServiceError('invalid_response','IOP returned no unambiguous result window')
    first,last,available=ranges.pop();rows=[];seen=set()
    for card in soup.select('.art-list-item'):
        anchor=card.select_one('.art-list-item-title a[href]')
        if anchor is None:raise ServiceError('invalid_response','IOP result has no article title link')
        url=urljoin(base,anchor['href']);match=re.search(r'/article/(10\.\d{4,9}/.+?)(?:/meta|/pdf)?$',unquote(urlsplit(url).path))
        identifier=match[1] if match else None
        if url in seen:raise ServiceError('range_mismatch','IOP repeated a document in one result window')
        seen.add(url);metadata=card.select('.art-list-item-meta');abstract=card.select_one('.reveal-content')
        rows.append({'id':identifier or url,'doi':identifier,'title':anchor.get_text(' ',strip=True),'url':url,
            'authors_display':metadata[0].get_text(' ',strip=True) if metadata else None,
            'citation_display':metadata[1].get_text(' ',strip=True) if len(metadata)>1 else None,
            'listing':card.get_text(' ',strip=True),'html':clean_html(str(card),Sanitizer()),
            'abstract_html':clean_html(str(abstract),Sanitizer()) if abstract else None})
    if first<1 or last<first or last>available or len(rows)!=last-first+1:
        raise ServiceError('range_mismatch','IOP cards differ from the displayed result range')
    capped=bool(re.search(r'\btop\s+[\d,]+\s+results\b',text,re.I))
    return {'rows':rows,'start':first-1,'accessible_total':available,'total':None if capped else available,
            'source_window_limit':500 if capped else None,'count_scope':'source_ranked_window' if capped else 'reported_matches'}


def search(adapter,query,*,options,start=0,limit=20,cursor=None,export=None):
    options=dict(options);options.setdefault('sort','newest')
    citation_format=export if export in ('bibtex','ris') else None
    search_export=None if citation_format else export
    types=options.get('pub_type',[]);opened=options.get('open_access',False)
    if not isinstance(types,list) or any(x not in ('article','chapter','book') for x in types) or type(opened) is not bool:
        raise ServiceError('invalid_options','Use an article/chapter/book list and boolean open_access')
    if options['sort']=='newest' and not types and not opened:
        from iop_rss import IOPRSS
        if not hasattr(adapter,'_rss_api'):adapter._rss_api=IOPRSS(adapter.store,gateway=adapter.gateway,hosts=adapter.profile.hosts)
        result=adapter._rss_api.search(query,options={k:v for k,v in options.items() if k not in ('pub_type','open_access')},start=start,limit=limit,cursor=cursor,export=search_export)
        result['options']=options
    else:result=web_search(adapter,query,options=options,start=start,limit=limit,cursor=cursor,export=search_export)
    if citation_format:
        from iop import citation
        from publishers import publication_metadata,publication_dois
        rows=json.loads(adapter.store.read(result['records']['ref'])[1]);files=[];failures=[]
        for row in rows:
            page=None
            try:
                page=adapter.document(row['url']);raw=page.content()
                if is_access_challenge(raw):raise ServiceError('publisher_access_challenge','IOP requires access verification for this citation',status='restricted')
                identifier=row.get('doi')
                if not identifier:
                    candidates=publication_dois(publication_metadata(raw))
                    if len(candidates)!=1:raise ServiceError('identity_mismatch','IOP result has no unique native document DOI')
                    identifier=candidates[0]
                artifact=citation(adapter,page,identifier,citation_format)
                files.append({'id':row['id'],'doi':identifier,'format':citation_format,'artifact':artifact})
            except ServiceError as error:failures.append({'id':row['id'],**error.result})
            except Exception as error:failures.append({'id':row['id'],'status':'error','code':'citation_export_failed',**failure_details(error)})
            finally:
                if page is not None:page.close()
        result['export']={'status':'partial' if failures else 'available','format':citation_format,'artifacts':files,'errors':failures}
        if failures:result['status']='partial'
    return result


def web_search(adapter,query,*,options,start=0,limit=20,cursor=None,export=None):
    if type(start) is not int or start<0 or type(limit) is not int or limit<1:
        raise ServiceError('invalid_range','Use a nonnegative start and positive limit')
    if start+limit>500:
        raise ServiceError('source_window_limit','IOP exposes at most its top 500 results; narrow the search to address another window',status='unsupported',source_limit=500)
    if cursor or set(options)-{'period','sort','journals','pub_type','open_access','page_size'}:
        raise ServiceError('invalid_options','Use documented IOP native filters and start for pagination')
    if not isinstance(query,str) or not query.strip():raise ServiceError('invalid_query','Use a nonempty native IOP search term')
    if export not in (None,'json','csv','html','native'):
        raise ServiceError('export_not_implemented','Ranked IOP search supports json, csv and native HTML; fetch an article for BibTeX/RIS',status='not_implemented')
    period=options.get('period','anytime');sort=options.get('sort','relevance');size=options.get('page_size',10)
    if period not in ('anytime','lastThirtyDays','lastTwelveMonths','lastFiveYears') or sort not in ('relevance','newest','oldest') or type(size) is not int or size not in (10,20,50):
        raise ServiceError('invalid_options','Use a documented period, sort and page_size 10/20/50')
    journals=options.get('journals',[]);types=options.get('pub_type',[]);opened=options.get('open_access',False)
    if not isinstance(journals,list) or any(not isinstance(x,str) or not re.fullmatch(r'\d{4}-\d{3}[\dXx]',x) for x in journals) or len(journals)!=len(set(journals)):
        raise ServiceError('invalid_options','journals must be distinct native ISSN values')
    if not isinstance(types,list) or any(x not in ('article','chapter','book') for x in types) or len(types)!=len(set(types)) or type(opened) is not bool:
        raise ServiceError('invalid_options','pub_type is an article/chapter/book list and open_access is boolean')
    params={'terms':query,'searchDatePeriod':period,'orderBy':sort,'pageLength':size,'currentPage':1}
    if journals:params['journals']=journals
    if types:params['pubType']=types
    if opened:params['accessType']='open-access'
    page=adapter.gateway.open(adapter.source,adapter.profile.gateway_label,adapter.profile.hosts,'body')
    base='https://'+urlsplit(page.url).netloc
    selected=[];evidence=[];errors=[];available=None;total=None;facets=None
    while True:
        try:
            response=goto_source(page,base+'/nsearch?'+urlencode(params,doseq=True),adapter.profile.hosts,wait_until='domcontentloaded',timeout=SOURCE_WAIT_MS)
            if response.status in (401,403):raise ServiceError('access_restricted','IOP rejected this search request',status='restricted',http_status=response.status)
            if response.status>=400:raise ServiceError('provider_error','IOP search returned an HTTP error',http_status=response.status)
            raw=response.text();found=search_records(raw,response.url);soup=BeautifulSoup(raw,'html.parser')
            control=soup.select_one('#quickSearch')
            if control is None or control.get('value')!=query:raise ServiceError('query_mismatch','IOP did not retain the requested search term')
            controls=applied_filters(soup)
            if controls!={'journals':set(journals),'pubType':set(types),'accessType':{'open-access'} if opened else set(),'searchDatePeriod':{period}}:
                raise ServiceError('filter_mismatch','IOP did not retain exactly the requested native filters')
            for name,value in [('orderBy',sort),('pageLength',str(size))]:
                choice=soup.select_one('select[name="'+name+'"] option[selected]')
                if found['accessible_total'] and (choice is None or choice.get('value')!=value):raise ServiceError('filter_mismatch','IOP changed the requested sort or page size',field=name)
            if available is not None and available!=found['accessible_total']:raise ServiceError('range_mismatch','IOP changed the accessible result count')
            available,total=found['accessible_total'],found['total']
            if found['start']!=(params['currentPage']-1)*size:raise ServiceError('range_mismatch','IOP returned a different page offset')
            proof=adapter.store.put(clean_html(raw,adapter.store.sanitizer),'text/html',adapter.source,response.url,
                role='native_search_html',query=query,options=options,start=found['start'],accessible_total=available,count_scope=found['count_scope'])
            evidence.append(proof)
            if facets is None:
                values={}
                for node in soup.select('input[name=journals],input[name=pubType],input[name=accessType]'):
                    name=node.get('name');value=node.get('value')
                    values.setdefault(name,{})[value]={'value':value,'label':node.parent.get_text(' ',strip=True),'selected':node.has_attr('checked')}
                facets=adapter.store.put(encoded({k:list(v.values()) for k,v in values.items()}),'application/json',adapter.source,response.url,role='native_search_facets',parent_ref=proof['ref'])
            if start>=available:break
            selected.extend(row for index,row in enumerate(found['rows'],found['start']) if start<=index<start+limit)
            if found['start']+len(found['rows'])>=min(start+limit,available):break
            params['currentPage']=max(params['currentPage']+1,start//size+1)
        except Exception as error:
            if urlsplit(page.url).hostname in ('validate.perfdrive.com','challenges.cloudflare.com'):
                problem=ServiceError('publisher_access_challenge','IOP moved to an access verification page',status='restricted')
            else:problem=error if isinstance(error,ServiceError) else ServiceError('search_page_failed','IOP search page retrieval or parsing failed',**failure_details(error))
            if not selected:
                if evidence:problem.result['evidence']=evidence
                raise problem from None
            errors.append(problem.result);break
    artifact=adapter.store.put(encoded(selected),'application/json',adapter.source,page.url,role='records',query=query,options=options,start=start,accessible_total=available,evidence_refs=[p['ref'] for p in evidence])
    exported=artifact
    if export in ('html','native'):exported={'artifacts':evidence,'scope':'Whole native pages used for the exact records window'}
    elif export=='csv':
        stream=io.StringIO(newline='');fields=list(dict.fromkeys(k for row in selected for k in row));writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(selected)
        exported=adapter.store.put(stream.getvalue(),'text/csv',adapter.source,page.url,role='mechanical_export',parent_ref=artifact['ref'])
    more=start+len(selected)<available
    return {'status':'partial' if errors else 'ok' if selected else 'not_found','source':adapter.source,'query':query,'options':options,'retrieval':'institutional_html',
        'start':start,'requested':limit,'received':len(selected),'total':total,'accessible_total':available,'source_window_limit':500,
        'has_more':more,'next':{'start':start+len(selected)} if more else None,'records':artifact,'export':exported,'facets':facets,'evidence':evidence,'errors':errors,
        'scope':'The named source and its exposed top-500 window; accessible_total is not the global matching count',
        'preview':[{k:r[k] for k in ('id','title','doi','url')} for r in selected[:3]]}

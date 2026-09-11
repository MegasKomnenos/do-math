"""APS native search pages, query clauses, and exact result windows."""
import csv,io,json,re
from urllib.parse import parse_qs,urljoin,urlsplit,urlunsplit,urlencode,unquote
from bs4 import BeautifulSoup
from browser_adapters import clean_html,goto_source,is_access_challenge
from scholarly import ServiceError,encoded,Sanitizer

FIELDS={'all','author','abstract','abstitle','title','refauth','affiliation','collaboration'}
FILTERS={'journal','article_type','category','physh_concept','physh_discipline'}


def search_records(raw,base,*,expected_clauses=None,per_page=20):
    if is_access_challenge(raw):raise ServiceError('publisher_access_challenge','APS returned an access verification page',status='restricted')
    soup=BeautifulSoup(raw,'html.parser');main=soup.select_one('#search-main')
    if main is None:raise ServiceError('invalid_response','APS returned no native search results region')
    try:
        total=int(main['data-search-analytics-results-count-value']);clauses=json.loads(main['data-search-clauses'])
    except (KeyError,ValueError,TypeError):raise ServiceError('invalid_response','APS returned no valid search count and clauses') from None
    if total<0:raise ServiceError('invalid_response','APS returned a negative result count')
    if expected_clauses is not None and clauses!=expected_clauses:
        raise ServiceError('query_mismatch','APS did not retain the requested search fields, operators and values')
    current=main.select_one('a[aria-current=page]')
    try:number=int(parse_qs(urlsplit(current['href']).query).get('page',['1'])[0]) if current else 1
    except (ValueError,KeyError):raise ServiceError('invalid_response','APS returned no valid current page') from None
    first=(number-1)*per_page;rows=[];seen=set()
    for anchor in main.select('h3 > a[href]'):
        card=anchor.find_parent('div',class_='border-b');url=urljoin(base,anchor['href'])
        if card is None or url in seen:raise ServiceError('invalid_response','APS result cards are missing or repeated')
        seen.add(url);match=re.search(r'/(10\.\d{4,9}/[^?#\s]+)',unquote(urlsplit(url).path))
        identifier=match[1] if match else None;abstract=card.select_one('.abstract-summary')
        paragraphs=anchor.parent.parent.find_all('p');authors=citation=published=None
        if len(paragraphs)>=2 and 'Published' in paragraphs[1].get_text():
            authors=paragraphs[0].get_text(' ',strip=True)
            spans=paragraphs[1].find_all('span',recursive=False)
            if len(spans)==2:
                citation=spans[0].get_text(' ',strip=True)
                published=re.sub(r'^\s*-\s*Published\s*','',spans[1].get_text(' ',strip=True))
        rows.append({'id':identifier or url,'doi':identifier,'title':anchor.get_text(' ',strip=True),'url':url,
            'authors_display':authors,'citation_display':citation,'publication_date_display':published,
            'listing':card.get_text(' ',strip=True),'html':clean_html(str(card),Sanitizer()),
            'abstract':abstract.get_text(' ',strip=True) if abstract else None,
            'abstract_html':clean_html(str(abstract),Sanitizer()) if abstract else None})
    if len(rows)!=min(per_page,max(0,total-first)):
        raise ServiceError('range_mismatch','APS result cards differ from the declared count and page',received=len(rows),total=total,start=first)
    next_page=main.select_one('a[aria-label="Next page"]')
    facets={}
    for control in soup.select('input[type=checkbox][name][value]'):
        name=control['name']
        if name not in FILTERS:continue
        value=control['value'];label=control.find_parent('label') or control.parent
        facets.setdefault(name,{})[value]={'value':value,'label':label.get_text(' ',strip=True),'selected':control.has_attr('checked')}
    return {'rows':rows,'total':total,'start':first,'page':number,'clauses':clauses,
            'sort':main.get('data-search-analytics-sort-value'),'next_url':urljoin(base,next_page['href']) if next_page else None,
            'facets':{key:list(values.values()) for key,values in facets.items()}}


def search(adapter,query,*,options,start=0,limit=20,cursor=None,export=None):
    if type(start) is not int or start<0 or type(limit) is not int or not 1<=limit<=1000:
        raise ServiceError('invalid_range','Use start >= 0 and limit 1..1000')
    if cursor or set(options)-({'field','terms','sort','date'}|FILTERS):
        raise ServiceError('invalid_options','Use documented APS search fields and filters')
    if export not in (None,'json','csv','html','native'):
        raise ServiceError('export_not_implemented','APS search currently supports json, csv and native HTML; citation files are not connected',status='not_implemented')
    field=options.get('field','all');sort=options.get('sort','relevance')
    if not isinstance(field,str) or field not in FIELDS or sort not in ('relevance','recent','oldest','most_cited') or not isinstance(query,str) or not query.strip():
        raise ServiceError('invalid_options','Use a documented field, sort and nonempty query')
    clauses=[{'field':field,'value':query,'operator':'AND'}]
    terms=options.get('terms',[])
    if not isinstance(terms,list):raise ServiceError('invalid_options','terms must be a list of field/query/operator objects')
    for term in terms:
        if not isinstance(term,dict) or set(term)!={'field','query','operator'} or not isinstance(term['field'],str) or term['field'] not in FIELDS or term['operator'] not in ('AND','OR','NOT') or not isinstance(term['query'],str) or not term['query'].strip():
            raise ServiceError('invalid_options','Each additional APS term needs a documented field, nonempty query and AND/OR/NOT operator')
        clauses.append({'field':term['field'],'value':term['query'],'operator':term['operator']})
    params={'clauses':json.dumps(clauses,separators=(',',':')),'sort':sort}
    for key in FILTERS&set(options):
        if not isinstance(options[key],str) or not options[key].strip():
            raise ServiceError('invalid_options','Each facet currently accepts one nonempty native value',field=key)
        params[key]=options[key]
    if 'date' in options:
        if options['date'] not in ('week','month','year'):
            raise ServiceError('invalid_options','date currently supports week, month or year; custom ranges are not connected')
        params['date']=options['date']
    simple=field=='all' and not terms and set(params)=={'clauses','sort'} and sort=='relevance'
    target='https://journals.aps.org/'+('search?'+urlencode({'q':query}) if simple else 'search/results?'+urlencode(params))
    adapter.gateway.start();responses=[];page=None
    def capture(response):
        location=urlsplit(response.url)
        if location.hostname in adapter.profile.hosts and location.path in ('/search','/search/results') and response.status==200 and 'html' in response.headers.get('content-type',''):
            responses.append(response)
    adapter.gateway.context.on('response',capture)
    selected=[];proofs=[];errors=[];total=None;facets=None;expected_page=1
    try:
        cached=adapter.gateway.pages.get(adapter.source)
        previous=getattr(adapter,'_aps_last',None);replay=None
        reusable=cached is not None and not cached.is_closed() and urlsplit(cached.url).hostname in ('journals.aps.org','journals-aps-org.libproxy.knu.ac.kr')
        if reusable and start>0 and previous and previous['params']==params and previous['start']<=start:
            page=cached;replay=previous;expected_page=previous['start']//20+1
        elif reusable:
            page=cached;origin=urlsplit(page.url);requested=urlsplit(target)
            target=urlunsplit((origin.scheme,origin.netloc,requested.path,requested.query,''))
            goto_source(page,target,adapter.profile.hosts,wait_until='domcontentloaded',timeout=45000)
        else:
            page=adapter.document(target)
            adapter.gateway.pages[adapter.source]=page
            if cached is not None and cached!=page and not cached.is_closed():cached.close()
        while True:
            try:
                old_proof=old_facets=None
                if replay:
                    raw,response_url,old_proof,old_facets=replay['raw'],replay['url'],replay['proof'],replay['facets'];replay=None
                else:
                    try:page.wait_for_function("number => { if(document.querySelector('#challenge-error-text,#capInput')) return true; const main=document.querySelector('#search-main'); const current=main?.querySelector('[aria-current=page]'); return main && (current ? Number(new URL(current.href).searchParams.get('page')||1)===number : number===1); }",arg=expected_page,timeout=25000)
                    except Exception:
                        if is_access_challenge(page.content()):raise ServiceError('publisher_access_challenge','APS returned an access verification page',status='restricted') from None
                        raise ServiceError('search_response_not_received','APS did not initialize its requested search page') from None
                    if is_access_challenge(page.content()):raise ServiceError('publisher_access_challenge','APS returned an access verification page',status='restricted')
                    # Preserve server HTML before MathJax replaces hidden formulas with lazy placeholders.
                    raw=response_url=None
                    for candidate in reversed(responses):
                        body=candidate.text()
                        if BeautifulSoup(body,'html.parser').select_one('#search-main'):
                            raw=body;response_url=candidate.url;break
                    if raw is None:raise ServiceError('native_response_missing','APS rendered results but their original HTML response was not captured')
                found=search_records(raw,response_url,expected_clauses=clauses)
                if found['sort']!=sort:raise ServiceError('filter_mismatch','APS returned a different sort order')
                for key in FILTERS&set(options):
                    if not any(item['value']==options[key] and item['selected'] for item in found['facets'].get(key,[])):
                        raise ServiceError('filter_mismatch','APS did not retain a requested facet',field=key)
                if 'date' in options:
                    choice=BeautifulSoup(raw,'html.parser').select_one('#desktop-date-select option[selected]')
                    if choice is None or choice.get('value')!=options['date']:
                        raise ServiceError('filter_mismatch','APS did not retain the requested date interval')
                if total is not None and total!=found['total']:raise ServiceError('range_mismatch','APS changed the result total during pagination')
                total=found['total']
                proof=old_proof or adapter.store.put(clean_html(raw,adapter.store.sanitizer),'text/html',adapter.source,response_url,
                    role='native_search_html',clauses=clauses,start=found['start'],total=total)
                proofs.append(proof)
                if facets is None:
                    facets=old_facets or adapter.store.put(encoded(found['facets']),'application/json',adapter.source,response_url,role='native_search_facets',parent_ref=proof['ref'])
                adapter._aps_last={'params':dict(params),'raw':raw,'url':response_url,'start':found['start'],'proof':proof,'facets':facets}
                if start>=total:break
                if found['page']!=expected_page:raise ServiceError('range_mismatch','APS returned a different page')
                selected.extend(row for index,row in enumerate(found['rows'],found['start']) if start<=index<start+limit)
                if found['start']+len(found['rows'])>=min(total,start+limit):break
                if not found['next_url']:raise ServiceError('pagination_control_missing','APS has more results but returned no next-page link')
                expected_page=max(found['page']+1,start//20+1)
                location=urlsplit(found['next_url']);values=parse_qs(location.query);values['page']=[str(expected_page)]
                target=urlunsplit((location.scheme,location.netloc,location.path,urlencode(values,doseq=True),''));responses.clear()
                # The observed Turbo fetch is rejected while document navigation serves this native URL.
                goto_source(page,target,adapter.profile.hosts,wait_until='domcontentloaded',timeout=45000)
            except Exception as error:
                problem=error if isinstance(error,ServiceError) else ServiceError('search_page_failed','APS page retrieval or parsing failed',error_type=type(error).__name__)
                if not selected:
                    if proofs:problem.result['evidence']=proofs
                    raise problem from None
                errors.append(problem.result);break
        artifact=adapter.store.put(encoded(selected),'application/json',adapter.source,page.url,role='records',query=query,options=options,start=start,total=total,evidence_refs=[x['ref'] for x in proofs])
        exported=artifact
        if export in ('html','native'):
            exported={'artifacts':proofs,'scope':'Whole native HTML pages used to cover the requested window; records holds the exact window'}
        elif export=='csv':
            stream=io.StringIO(newline='');fields=list(dict.fromkeys(k for row in selected for k in row))
            writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(selected)
            exported=adapter.store.put(stream.getvalue(),'text/csv',adapter.source,page.url,role='mechanical_export',parent_ref=artifact['ref'])
        more=start+len(selected)<total
        return {'status':'partial' if errors else 'ok' if selected else 'not_found','source':adapter.source,'query':query,'options':options,
            'start':start,'requested':limit,'received':len(selected),'total':total,'has_more':more,'next':{'start':start+len(selected)} if more else None,
            'records':artifact,'export':exported,'evidence':proofs,'facets':facets,'errors':errors,
            'preview':[{key:row[key] for key in ('id','title','doi','url')} for row in selected[:3]]}
    except ServiceError:raise
    except Exception as error:
        raise ServiceError('search_navigation_failed','APS did not complete its search navigation',error_type=type(error).__name__) from None
    finally:
        adapter.gateway.context.remove_listener('response',capture)

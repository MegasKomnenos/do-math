"""De Gruyter Brill native search expressions and document RIS controls."""
import csv
import io
import re
from urllib.parse import urlsplit,urljoin,urlencode,parse_qs,unquote

from bs4 import BeautifulSoup
from api_adapters import doi
from browser_adapters import browser_download,clean_html,goto_source
from scholarly import ServiceError,encoded,bibliography


def records(raw,base):
    soup=BeautifulSoup(raw,'html.parser')
    header=soup.select_one('.searchInfo')
    match=re.search(r'([\d,]+)\s+of\s+([\d,]+)\s+results',header.get_text(' ',strip=True) if header else '',re.I)
    if not match:
        raise ServiceError('unrecognized_search_layout','Search response has no recognized result count')
    received,total=[int(value.replace(',','')) for value in match.groups()]
    rows=[]
    for item in soup.select('.searchResult'):
        link=item.select_one('.resultTitle > a')
        if not link:
            raise ServiceError('unrecognized_search_layout','Search record has no title link')
        url=urljoin(base,link['href'])
        match_doi=re.search(r'/document/doi/(10\..+)/(?:html|xml)$',unquote(urlsplit(url).path))
        kind=item.select_one('.newResultType')
        rows.append({'id':url,'url':url,'doi':match_doi[1] if match_doi else None,'title':link.get_text(' ',strip=True),
                     'type':kind.get_text(' ',strip=True) if kind else None,'listing':item.get_text('\n',strip=True)})
    if len(rows)!=received:
        raise ServiceError('range_mismatch','Search records do not match the displayed count')
    return rows,total


def citation(publisher,page,identifier):
    control=page.locator('a[title="Download in RIS format"]')
    control.first.wait_for(state='attached',timeout=30000)
    url=urljoin(page.url,control.first.get_attribute('href'))
    data,_,actual=browser_download(publisher.gateway.context,url,publisher.profile.download_hosts)
    evidence=publisher.store.put(data,'application/x-research-info-systems',publisher.source,actual,role='native_citation',doi=identifier)
    parsed=bibliography(data,'application/x-research-info-systems')
    found=[r['fields'].get('do',[None])[0] for r in parsed]
    if len(found)!=1 or doi(str(found[0])).lower()!=identifier.lower():
        raise ServiceError('identity_mismatch','RIS does not identify the requested publication',evidence=evidence)
    return evidence


def search(publisher,query,*,options,start=0,limit=20,cursor=None,export=None):
    if type(start) is not int or start<0 or type(limit) is not int or not 1<=limit<=1000:
        raise ServiceError('invalid_range','Use start >= 0 and limit 1..1000')
    if cursor or set(options)-{'sort','visibility'}:
        raise ServiceError('invalid_options','Use a native expression, sort and visibility')
    if export not in (None,'json','csv','html','ris','native'):
        raise ServiceError('invalid_export','Use json, csv, html or native RIS')
    sorts={'relevance','mostrecent','leastrecent','alphabetical','reversealpha'}
    visibility={'all','available','explicit','open','public'}
    if options.get('sort','relevance') not in sorts or options.get('visibility','all') not in visibility:
        raise ServiceError('invalid_options','Use the documented source sort and visibility values')
    profile=publisher.profile
    page=publisher.gateway.open(publisher.source,profile.gateway_label,profile.hosts,'body')
    base='https://'+urlsplit(page.url).hostname
    rows,evidence,citations,failures,total=[],[],[],[],None
    for number in range(start//10,(start+limit-1)//10+1):
        params={'query':query,'pageSize':10,'startItem':number*10,'sortBy':options.get('sort','relevance'),'documentVisibility':options.get('visibility','all')}
        goto_source(page,base+'/search?'+urlencode(params),profile.hosts,wait_until='domcontentloaded',timeout=45000)
        page.locator('.searchInfo').wait_for(timeout=30000)
        page.wait_for_function("() => {const h=document.querySelector('.searchInfo')?.textContent||'';const m=h.match(/([\\d,]+)\\s+of\\s+([\\d,]+)\\s+results/);return m && document.querySelectorAll('.searchResult .resultTitle > a').length===Number(m[1].replaceAll(',',''));}",timeout=30000)
        actual=parse_qs(urlsplit(page.url).query)
        if actual.get('query')!=[query] or actual.get('startItem')!=[str(number*10)]:
            raise ServiceError('query_mismatch','Source changed the submitted query or range')
        raw=clean_html(page.content(),publisher.store.sanitizer)
        artifact=publisher.store.put(raw,'text/html',publisher.source,page.url,role='search_page',query=query,options=options,start=number*10)
        evidence.append(artifact)
        native,found=records(raw,base)
        if total is not None and total!=found or len(native)!=min(10,max(0,found-number*10)):
            raise ServiceError('range_mismatch','Source result count changed or page is incomplete',evidence=evidence)
        total=found
        selected=[row for i,row in enumerate(native,number*10) if start<=i<start+limit]
        rows.extend(selected)
        if export in ('ris','native'):
            for row in selected:
                if not row['doi']:
                    failures.append({'id':row['id'],'status':'unsupported','code':'document_citation_unavailable'})
                    continue
                document=publisher.gateway.context.new_page()
                try:
                    goto_source(document,row['url'],profile.hosts,wait_until='domcontentloaded',timeout=45000)
                    citations.append(citation(publisher,document,row['doi']))
                except ServiceError as error:
                    failures.append({'id':row['id'],**error.result})
                except Exception as error:
                    failures.append({'id':row['id'],'status':'error','code':'citation_export_failed','error_type':type(error).__name__})
                finally:
                    document.close()
        if (number+1)*10>=total:
            break
    artifact=publisher.store.put(encoded(rows),'application/json',publisher.source,page.url,role='records',query=query,options=options,start=start,requested=limit,total=total)
    exported=artifact
    if export=='html':
        exported={'artifacts':evidence}
    elif export=='csv':
        stream=io.StringIO(newline='')
        writer=csv.DictWriter(stream,fieldnames=['id','doi','title','type','url','listing'])
        writer.writeheader()
        writer.writerows(rows)
        exported=publisher.store.put(stream.getvalue(),'text/csv',publisher.source,page.url,role='mechanical_export',parent_ref=artifact['ref'])
    elif export in ('ris','native'):
        exported={'status':'partial' if failures else 'available','artifacts':citations,'failures':failures}
    more=start+len(rows)<total
    return {'status':'partial' if failures else 'ok' if rows else 'not_found','source':publisher.source,'query':query,'start':start,'requested':limit,
            'received':len(rows),'total':total,'has_more':more,'next':{'start':start+len(rows)} if more else None,'records':artifact,
            'export':exported,'evidence':evidence,'preview':[{k:r[k] for k in ('doi','title','type')} for r in rows[:3]]}

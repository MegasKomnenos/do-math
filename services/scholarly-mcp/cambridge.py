"""Cambridge Core search and its credential-free native RIS export."""
import csv
import io
import re
from urllib.parse import urlencode, urljoin, urlsplit, parse_qs
from waits import SOURCE_WAIT_S

from bs4 import BeautifulSoup
import httpx

from api_adapters import APIAdapter
from browser_adapters import browser_download, clean_html
from scholarly import ServiceError, encoded, bibliography


class CitationAPI(APIAdapter):
    source='cambridge'
    hosts=('www.cambridge.org',)


def citation(store, identifiers):
    if not identifiers or any(not re.fullmatch(r'[A-Fa-f0-9]{32}', identifier) for identifier in identifiers):
        raise ServiceError('invalid_target','Use Cambridge product identifiers from the source results')
    with httpx.Client(timeout=SOURCE_WAIT_S,follow_redirects=False) as client:
        api=CitationAPI(store,client=client)
        data,evidence=api.request('https://www.cambridge.org/core/services/aop-easybib/export',params={
            'exportType':'ris','productIds':','.join(identifiers),'citationStyle':'apa'},accept='binary')
    rows=bibliography(data,'application/x-research-info-systems')
    observed=[]
    for row in rows:
        matches={part.upper() for url in row['fields'].get('ur',[]) for part in urlsplit(url).path.split('/') if re.fullmatch(r'[A-Fa-f0-9]{32}',part)}
        if len(matches)!=1:
            raise ServiceError('identity_mismatch','Native RIS has no unique Cambridge product URL',evidence=evidence)
        observed.extend(matches)
    if sorted(observed)!=sorted(identifier.upper() for identifier in identifiers):
        raise ServiceError('identity_mismatch','Native RIS does not match the selected Cambridge products',evidence=evidence)
    return store.put(data,'application/x-research-info-systems','cambridge',evidence['url'],role='native_citations',product_ids=identifiers,evidence_ref=evidence['ref'])


def records(raw,base):
    soup=BeautifulSoup(raw,'html.parser')
    heading=next((h for h in soup.select('#maincontent h2.title,h2.title') if re.match(r'\s*[\d,]+\s+results?\b',h.get_text(' ',strip=True))),None)
    if heading is None:
        raise ServiceError('invalid_response','Cambridge returned no recognized result count')
    total=int(re.match(r'\s*([\d,]+)',heading.get_text(' ',strip=True))[1].replace(',',''))
    rows=[]
    for item in soup.select('.representation'):
        heading=item.select_one('h3')
        link=(heading.find('a') or heading.find_parent('a')) if heading else None
        exporter=item.select_one('a.export-citation-component[data-prod-id]')
        if not link or not exporter:
            raise ServiceError('invalid_response','Cambridge record is missing its title or product identity')
        identifier=exporter['data-prod-id']
        url=urljoin(base,link['href'])
        if identifier.lower() not in urlsplit(url).path.lower().split('/'):
            raise ServiceError('identity_mismatch','Cambridge title link and citation product differ')
        rows.append({'id':identifier,'title':heading.get_text(' ',strip=True),'url':url,'listing':item.get_text('\n',strip=True)})
    return rows,total


def search(publisher,query,*,options,start=0,limit=20,cursor=None,export=None):
    if type(start) is not int or start<0 or type(limit) is not int or not 1<=limit<=1000:
        raise ServiceError('invalid_range','Use start >= 0 and limit 1..1000')
    allowed={'author','from_year','to_year','content_type','available','subject','journal','publisher','society','sort'}
    if cursor or set(options)-allowed:
        raise ServiceError('invalid_options','Use the documented Cambridge filters and start/limit')
    if export not in (None,'json','html','csv','ris','native'):
        raise ServiceError('invalid_export','Use json, html, csv or native RIS')
    sorts={'relevance':'','title':'titleSort:asc','newest':'canonical.date:desc'}
    if options.get('sort','relevance') not in sorts:
        raise ServiceError('invalid_options','Use sort relevance, title or newest')
    params={'q':query,'sort':sorts[options.get('sort','relevance')]}
    mapping={'author':'filters[authorTerms]','from_year':'filters[dateYearRange][from]','to_year':'filters[dateYearRange][to]',
             'subject':'aggs[productSubject][filters]','journal':'aggs[productJournal][filters]',
             'publisher':'aggs[productPublisher][filters]','society':'aggs[productSociety][filters]'}
    for key,name in mapping.items():
        if key in options:
            params[name]=options[key]
    if 'content_type' in options:
        types={'Articles':'JOURNAL_ARTICLE','Chapters':'BOOK_PART','Books':'BOOK','Elements':'ELEMENT'}
        values=options['content_type'] if isinstance(options['content_type'],list) else [options['content_type']]
        if not all(value in types for value in values):
            raise ServiceError('invalid_options','Use content type Articles, Chapters, Books or Elements')
        params['aggs[productTypes][filters]']=','.join(types[v] for v in values)
    if 'available' in options:
        if type(options['available']) is not bool:
            raise ServiceError('invalid_options','available requires a boolean')
        if options['available']:
            params['aggs[onlyShowAvailable][filters]']='true'
    profile=publisher.profile
    page=publisher.gateway.open(publisher.source,profile.gateway_label,profile.hosts,'body')
    base='https://'+urlsplit(page.url).hostname
    rows,evidence,citations,total,facets=[],[],[],None,[]
    for number in range(start//20+1,(start+limit-1)//20+2):
        params['pageNum']=number
        url=base+'/core/search?'+urlencode(params)
        raw,_,actual=browser_download(publisher.gateway.context,url,profile.hosts)
        native,found=records(raw,base)
        fields={'productSubject':'subject','productJournal':'journal','productPublisher':'publisher','productSociety':'society'}
        for node in BeautifulSoup(raw,'html.parser').select('input[data-agg-key-container][data-agg-option]'):
            group=node['data-agg-key-container']
            if group in fields:
                item={'field':fields[group],'id':node['data-agg-option'],'label':node.get('data-legend'),'count':node.get('data-count')}
                if item not in facets:
                    facets.append(item)
        actual_params=parse_qs(urlsplit(actual).query)
        if actual_params.get('q')!=[query] or actual_params.get('pageNum')!=[str(number)]:
            raise ServiceError('query_mismatch','Cambridge changed the query or page')
        artifact=publisher.store.put(clean_html(raw.decode('utf-8'),publisher.store.sanitizer),'text/html',publisher.source,actual,role='search_page',query=query,options=options,page=number)
        evidence.append(artifact)
        if total is not None and total!=found or len(native)!=min(20,max(0,found-(number-1)*20)):
            raise ServiceError('range_mismatch','Cambridge result count changed or its page is incomplete',evidence=evidence)
        total=found
        selected=[r for i,r in enumerate(native,(number-1)*20) if start<=i<start+limit]
        rows.extend(selected)
        if export in ('ris','native') and selected:
            citations.append(citation(publisher.store,[row['id'] for row in selected]))
        if number*20>=total:
            break
    artifact=publisher.store.put(encoded(rows),'application/json',publisher.source,actual,role='records',query=query,options=options,start=start,requested=limit,total=total)
    exported=artifact
    if export=='html':
        exported={'artifacts':evidence}
    elif export=='csv':
        stream=io.StringIO(newline='')
        writer=csv.DictWriter(stream,fieldnames=['id','title','url','listing'])
        writer.writeheader()
        writer.writerows(rows)
        exported=publisher.store.put(stream.getvalue(),'text/csv',publisher.source,actual,role='mechanical_export',parent_ref=artifact['ref'])
    elif export in ('ris','native'):
        exported={'artifacts':citations,'format':'ris'}
    more=start+len(rows)<total
    facet_artifact=publisher.store.put(encoded(facets),'application/json',publisher.source,actual,role='available_facets',query=query,options=options)
    return {'status':'ok' if rows else 'not_found','source':publisher.source,'query':query,'start':start,'requested':limit,
            'received':len(rows),'total':total,'has_more':more,'next':{'start':start+len(rows)} if more else None,
            'records':artifact,'export':exported,'evidence':evidence,'facets':facet_artifact,'preview':[{k:r[k] for k in ('id','title')} for r in rows[:3]]}

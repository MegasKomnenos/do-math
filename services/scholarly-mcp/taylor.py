"""Taylor & Francis's native field search and citation download."""
import csv
import io
import re
from urllib.parse import urljoin,urlsplit,urlencode,parse_qs,unquote

from bs4 import BeautifulSoup
from api_adapters import doi
from browser_adapters import browser_download,clean_html
from scholarly import ServiceError,encoded,bibliography


FIELDS={'Anywhere':'AllField','Title':'Title','Author':'Contrib','Keywords':'Keyword','Abstract':'Abstract','Affiliation':'Affiliation','Funder':'FunderTextFieldLang'}
SORTS={'relevance':'relevancy','newest':'Earliest_desc','oldest':'Earliest_asc','most_cited':'cited(all)_desc','most_read':'downloaded(y0)_desc'}


def records(raw,base):
    soup=BeautifulSoup(raw,'html.parser')
    heading=soup.select_one('li.search-results')
    match=re.search(r'Showing\s+([\d,]+)\s*[-–]\s*([\d,]+)\s+of\s+([\d,]+)\s+results',heading.get_text(' ',strip=True) if heading else '',re.I)
    if not match:
        raise ServiceError('invalid_response','Taylor & Francis returned no recognized result range')
    first,last,total=[int(value.replace(',','')) for value in match.groups()]
    rows=[]
    for item in soup.select('article.searchResultItem'):
        title=item.select_one('a.ref[href*="/doi/"]')
        if title is None:
            raise ServiceError('invalid_response','Search record has no publication title link')
        url=urljoin(base,title['href'])
        identifier=re.search(r'/doi/(?:full/|abs/|pdf/|epdf/)?(10\..+)',unquote(urlsplit(url).path))
        if not identifier:
            raise ServiceError('invalid_response','Publication link has no DOI')
        rows.append({'id':identifier[1],'doi':identifier[1],'title':title.get_text(' ',strip=True),'url':url,'listing':item.get_text('\n',strip=True)})
    if len(rows)!=(max(0,min(last,total)-first+1) if total else 0):
        raise ServiceError('range_mismatch','Search records do not match the reported range')
    return rows,total,max(0,first-1)


def citation(publisher,identifiers,base,format='bibtex'):
    if format not in ('bibtex','ris'):
        raise ServiceError('invalid_export','Use native BibTeX or RIS')
    identifiers=[doi(value) for value in identifiers]
    data,media,url=browser_download(publisher.gateway.context,urljoin(base,'/action/downloadCitation'),publisher.profile.download_hosts,
        form={'downloadFileName':'citation','direct':'true','include':'abs','doi':identifiers,'format':format})
    expected='application/x-bibtex' if format=='bibtex' else 'application/x-research-info-systems'
    evidence=publisher.store.put(data,expected,publisher.source,url,role='native_citations',requested_dois=identifiers,request_method='POST',source_media_type=media)
    parsed=bibliography(data,expected)
    found=[r.get('doi') or r.get('fields',{}).get('do',[None])[0] for r in parsed]
    if sorted(doi(str(value)).lower() for value in found)!=sorted(value.lower() for value in identifiers):
        raise ServiceError('identity_mismatch','Native citations do not match the selected publication DOIs',evidence=evidence)
    return evidence


def search(publisher,query,*,options,start=0,limit=20,cursor=None,export=None):
    if type(start) is not int or start<0 or type(limit) is not int or not 1<=limit<=1000:
        raise ServiceError('invalid_range','Use start >= 0 and limit 1..1000')
    if cursor or set(options)-{'field','after_year','before_year','sort'} or options.get('field','Anywhere') not in FIELDS:
        raise ServiceError('invalid_options','Use the documented search field, year bounds and sort order')
    if export not in (None,'json','html','csv','bibtex','ris'):
        raise ServiceError('invalid_export','Use json, html, csv, bibtex or ris')
    if options.get('sort','relevance') not in SORTS:
        raise ServiceError('invalid_options','Use relevance, newest, oldest, most_cited or most_read')
    params={'field1':FIELDS[options.get('field','Anywhere')],'text1':query,'pageSize':20,'Ppub':'','sortBy':SORTS[options.get('sort','relevance')]}
    for name,native in [('after_year','AfterYear'),('before_year','BeforeYear')]:
        if name in options:
            if type(options[name]) is not int or not 1<=options[name]<=9999:
                raise ServiceError('invalid_options','Year bounds require integer years')
            params[native]=options[name]
    profile=publisher.profile
    page=publisher.gateway.open(publisher.source,profile.gateway_label,profile.hosts,'body')
    base='https://'+urlsplit(page.url).hostname
    rows,evidence,citations,failures,total=[],[],[],[],None
    for number in range(start//20,(start+limit-1)//20+1):
        params['startPage']=number
        data,_,actual=browser_download(publisher.gateway.context,base+'/action/doSearch?'+urlencode(params),profile.hosts)
        raw=clean_html(data.decode('utf-8'),publisher.store.sanitizer)
        observed=parse_qs(urlsplit(actual).query)
        if observed.get('text1')!=[query] or observed.get('field1')!=[params['field1']] or observed.get('startPage')!=[str(number)]:
            raise ServiceError('query_mismatch','Source returned a different query or page')
        artifact=publisher.store.put(raw,'text/html',publisher.source,actual,role='search_page',query=query,options=options,page=number)
        evidence.append(artifact)
        native,found,first=records(raw,base)
        if found and first!=number*20 or total is not None and total!=found:
            raise ServiceError('range_mismatch','Source returned a changed result range',evidence=evidence)
        total=found
        selected=[row for i,row in enumerate(native,first) if start<=i<start+limit]
        rows.extend(selected)
        if export in ('bibtex','ris') and selected:
            try:
                citations.append(citation(publisher,[row['doi'] for row in selected],base,export))
            except ServiceError as error:
                failures.append(error.result)
        if (number+1)*20>=total:
            break
    artifact=publisher.store.put(encoded(rows),'application/json',publisher.source,actual,role='records',query=query,options=options,start=start,requested=limit,total=total)
    exported=artifact
    if export=='html':
        exported={'artifacts':evidence}
    elif export=='csv':
        stream=io.StringIO(newline='')
        writer=csv.DictWriter(stream,fieldnames=['id','doi','title','url','listing'])
        writer.writeheader()
        writer.writerows(rows)
        exported=publisher.store.put(stream.getvalue(),'text/csv',publisher.source,actual,role='mechanical_export',parent_ref=artifact['ref'])
    elif export in ('bibtex','ris'):
        exported={'status':'partial' if failures else 'available','artifacts':citations,'failures':failures}
    more=start+len(rows)<total
    return {'status':'partial' if failures else 'ok' if rows else 'not_found','source':publisher.source,'query':query,'start':start,'requested':limit,
            'received':len(rows),'total':total,'has_more':more,'next':{'start':start+len(rows)} if more else None,'records':artifact,
            'export':exported,'evidence':evidence,'preview':[{k:r[k] for k in ('doi','title')} for r in rows[:3]]}

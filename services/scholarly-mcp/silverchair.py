"""Publisher search and citation controls observed on Oxford Academic."""
from pathlib import Path
import csv
import io
import json
import re
from urllib.parse import urljoin, urlsplit, urlunsplit, urlencode, parse_qs

from bs4 import BeautifulSoup
from browser_adapters import clean_html, dismiss_cookies, goto_source, browser_download, require_source_url
from scholarly import ServiceError, encoded, bibliography


FIELDS = {'All':'text', 'Full Text':'_text_', 'Keywords':'Keywords', 'Title':'Title', 'Author':'AuthorsAndEditors',
          'Abstract':'ContentAbstract', 'References':'References'}
AIP_FIELDS = {'All':'text','Title':'Title','Author':'Authors','Author Affiliations':'AuthorAffiliations',
              'Full Text':'FullText','Abstract':'Abstract','Keyword':'Keywords','DOI':'Doi','ISBN':'ISBN',
              'EISBN':'EISBN','ISSN':'JournalISSN','EISSN':'JournalEISSN','Issue':'IssueNo','Volume':'Volume','References':'References'}


def ready_cookies(page):
    # Handle a banner that appears while Playwright is checking the next control's actionability.
    def reject(banner):
        page.wait_for_function("typeof OneTrust !== 'undefined' && typeof OneTrust.RejectAll === 'function'",timeout=15000)
        button=page.locator('#onetrust-reject-all-handler')
        if button.count() and button.is_visible():
            button.click()
        else:
            page.evaluate('OneTrust.RejectAll()')
    page.add_locator_handler(page.locator('#onetrust-banner-sdk'),reject)


def records(raw, base):
    soup = BeautifulSoup(raw, 'html.parser')
    count = soup.select_one('.sr-statistics')
    match = re.search(r'([\d,]+)\s*[–-]\s*([\d,]+)\s+of\s+([\d,]+)', count.get_text(' ', strip=True) if count else '')
    if not match:
        if count and re.fullmatch(r'\s*0(?:\s+results)?\s*', count.get_text(), re.I):
            return [], 0, 0
        raise ServiceError('invalid_response', 'Publisher did not provide a recognized search range')
    first, last, total = [int(x.replace(',','')) for x in match.groups()]
    rows = []
    for item in soup.select('.sr-list'):
        anchor = item.select_one('.sri-title a')
        if anchor is None:
            raise ServiceError('invalid_response', 'Publisher search record has no title link')
        url = urljoin(base, anchor['href'])
        title = BeautifulSoup(str(anchor),'html.parser')
        for badge in title.select('.get-access'):
            badge.decompose()
        kind=item.select_one('.sri-type')
        rows.append({'id': url, 'url': url, 'title': title.get_text(' ',strip=True), 'type':kind.get_text(' ',strip=True) if kind else None,
                     'listing': item.get_text('\n',strip=True)})
    if len(rows) != (max(0,min(last,total)-first+1) if total else 0):
        raise ServiceError('range_mismatch', 'Displayed publisher records do not match the reported range')
    return rows, total, max(0,first-1)


def citation(publisher, page, identifier, format='bibtex'):
    from api_adapters import doi
    formats={'ris':('0','application/x-research-info-systems'), 'endnote':('1','text/plain'),
             'bibtex':('2','application/x-bibtex'), 'plain':('3','text/plain')}
    value, media = formats[format]
    if publisher.source == 'oxford':
        ready_cookies(page)
        page.locator('.js-cite-button').filter(visible=True).first.click()
        form=page.locator('form#citationModal')
        form.wait_for(state='visible',timeout=30000)
        page.wait_for_function("() => {const f=document.querySelector('form#citationModal');return f?.elements.resourceId?.value && f?.elements.resourceType?.value;}",timeout=15000)
        if (form.get_attribute('method') or 'get').lower()!='get':
            raise ServiceError('citation_form_changed','Publisher citation form changed its submission method')
        # Submit the observed GET form fields; visual button initialization can lag behind the form.
        values=form.evaluate('f=>Object.fromEntries(new FormData(f).entries())')
        values['citationFormat']=value
        action=urljoin(page.url,form.get_attribute('action') or page.url)
        location=urlsplit(action)
        params=parse_qs(location.query)
        params.update({k:[v] for k,v in values.items()})
        url=urlunsplit((location.scheme,location.netloc,location.path,urlencode(params,doseq=True),''))
        data,_,actual=browser_download(publisher.gateway.context,url,publisher.profile.download_hosts)
    else:
        if format=='plain':
            raise ServiceError('format_not_offered','This AIP citation menu provides RIS, EndNote and BibTeX',status='unsupported')
        dismiss_cookies(page)
        page.add_locator_handler(page.get_by_role('button',name='Reject Non-Essential',exact=True),lambda button: button.click())
        page.locator('a.js-toolbar-dropdown').filter(has_text='Tools').click()
        page.locator('.stats-get-citation').filter(visible=True).click()
        label={'bibtex':'BibTex','ris':'Ris (Zotero)','endnote':'EndNote'}[format]
        link=page.get_by_role('link',name=label,exact=True)
        link.wait_for(state='visible',timeout=30000)
        url=urljoin(page.url,link.get_attribute('href'))
        data,_,actual=browser_download(publisher.gateway.context,url,publisher.profile.download_hosts)
    if format in ('bibtex','ris'):
        parsed = bibliography(data,media)
        observed = [r.get('doi') or r.get('fields',{}).get('do',[None])[0] for r in parsed]
        if len(observed)!=1 or doi(str(observed[0])).lower()!=identifier.lower():
            raise ServiceError('identity_mismatch','Native citation does not match the publication DOI')
    elif not data.strip() or data.lstrip().startswith(b'<'):
        raise ServiceError('unexpected_content','Publisher returned no citation text')
    return publisher.store.put(data,media,publisher.source,actual,role='native_citation',doi=identifier,format=format)


def search(publisher, query, *, options, start=0, limit=20, cursor=None, export=None):
    if type(start) is not int or start<0 or type(limit) is not int or not 1<=limit<=1000:
        raise ServiceError('invalid_range','Use start >= 0 and limit 1..1000')
    aip=publisher.source=='aip'
    fields=AIP_FIELDS if aip else FIELDS
    default='All'
    if cursor or set(options)-({'field','exact','sort','terms'} if aip else {'field','exact','sort'}) or options.get('field',default) not in fields:
        raise ServiceError('invalid_options','Use the documented publisher fields, matching options, sorting and start/limit')
    if type(options.get('exact',False)) is not bool:
        raise ServiceError('invalid_options','exact requires a boolean')
    if export not in (None,'json','html','csv','bibtex','ris','endnote','plain'):
        raise ServiceError('invalid_export','Use json, html, csv, bibtex, ris, endnote or plain')
    sort={'relevance':None,'newest':'Date – Newest First','oldest':'Date – Oldest First','title_asc':'Title - A to Z','title_desc':'Title - Z to A'}
    if options.get('sort','relevance') not in sort:
        raise ServiceError('invalid_options','Use relevance, newest, oldest, title_asc or title_desc')
    if aip and options.get('sort','relevance') not in ('relevance','newest','oldest'):
        raise ServiceError('invalid_options','AIP provides relevance, newest or oldest sorting')
    field=fields[options.get('field',default)]
    exact=options.get('exact',False)
    terms=[{'terms':[{'filter':field,'input':query,'exactMatch':exact}]}]
    extra=options.get('terms',[])
    if not isinstance(extra,list):
        raise ServiceError('invalid_options','terms must be a list of additional search rows')
    for term in extra:
        if not isinstance(term,dict) or set(term)-{'field','query','condition','exact'} or term.get('field') not in fields or not isinstance(term.get('query'),str) or term.get('condition','AND') not in ('AND','OR','NOT') or type(term.get('exact',False)) is not bool:
            raise ServiceError('invalid_options','Each term requires a field and query, with optional AND/OR/NOT condition and boolean exact')
        terms[0]['terms'].append({'condition':term.get('condition','AND'),'filter':fields[term['field']],'input':term['query'],'exactMatch':term.get('exact',False)})
    params={'allJournals':1,'fl_SiteID':191,'cqb':json.dumps(terms,separators=(',',':')),
            'qb':json.dumps({field+'1'+('-exact' if exact else ''):query},separators=(',',':'))}
    if aip:
        params={'hd':'advancedAny','cqb':json.dumps(terms,separators=(',',':')),'searchType':'advanced'}
    elif options.get('field',default)=='All':
        params={'q':'"'+query+'"' if exact else query,'allJournals':1,'fl_SiteID':191}
    if sort[options.get('sort','relevance')]:
        params['sort']=sort[options.get('sort','relevance')].replace('–','-') if aip else sort[options.get('sort','relevance')]
    profile=publisher.profile
    page=publisher.gateway.open(publisher.source,profile.gateway_label,profile.hosts,'body')
    base='https://'+urlsplit(page.url).hostname
    rows,evidence,total=[],[],None
    for number in range(start//20+1,(start+limit-1)//20+2):
        params['page']=number
        result_url=base+'/search-results?'+urlencode(params)
        if aip:
            goto_source(page,result_url,profile.hosts,wait_until='domcontentloaded',timeout=45000)
            page.wait_for_function("""() => {const el=document.querySelector('.sr-statistics');
          const text=el?.textContent||''; const m=text.match(/([\\d,]+)\\s*[–-]\\s*([\\d,]+)\\s+of\\s+([\\d,]+)/);
          if(!m) return /^\\s*0(?:\\s+results)?\\s*$/i.test(text);
          const n=x=>Number(x.replaceAll(',',''));return document.querySelectorAll('.sr-list .sri-title a.article-link,.sr-list .sri-title h4 a').length===(n(m[3])?n(m[2])-n(m[1])+1:0); }""",timeout=45000)
            raw=clean_html(page.content(),publisher.store.sanitizer)
            result_url=page.url
        else:
            data,_,result_url=browser_download(publisher.gateway.context,result_url,profile.hosts)
            raw=clean_html(data.decode('utf-8'),publisher.store.sanitizer)
        actual=parse_qs(urlsplit(result_url).query)
        query_key='cqb' if 'cqb' in params else 'q'
        if actual.get(query_key)!=[params[query_key]] or actual.get('page')!=[str(number)]:
            raise ServiceError('query_mismatch','Publisher returned a different query or page')
        page_evidence=publisher.store.put(raw,'text/html',publisher.source,result_url,role='search_response',query=query,options=options,page=number)
        evidence.append(page_evidence)
        try:
            native,found,first=records(raw,base)
        except ServiceError as error:
            partial=publisher.store.put(encoded(rows),'application/json',publisher.source,result_url,role='partial_records',query=query,start=start,requested=limit)
            raise ServiceError('search_parse_failed','Search response could not be reconciled with its range or the supported record layouts',status='partial' if rows else 'error',source=publisher.source,query=query,start=start,requested=limit,received=len(rows),records=partial,evidence=evidence,cause=error.result['code']) from None
        if not found and not aip:
            # Identical Oxford requests have returned an empty response followed by a nonempty response.
            data,_,result_url=browser_download(publisher.gateway.context,result_url,profile.hosts)
            raw=clean_html(data.decode('utf-8'),publisher.store.sanitizer)
            evidence.append(publisher.store.put(raw,'text/html',publisher.source,result_url,role='empty_search_recheck',query=query,options=options,page=number))
            native,found,first=records(raw,base)
        if found and first!=(number-1)*20 or total is not None and total!=found:
            raise ServiceError('range_mismatch','Publisher returned a changed or different result range',expected_start=(number-1)*20,observed_start=first,previous_total=total,observed_total=found,evidence=evidence)
        total=found
        rows.extend(r for i,r in enumerate(native,first) if start<=i<start+limit)
        if number*20>=total:
            break
    artifact=publisher.store.put(encoded(rows),'application/json',publisher.source,result_url,role='records',query=query,options=options,start=start,requested=limit,total=total)
    exported,failures=artifact,[]
    if export=='html':
        exported={'artifacts':evidence}
    elif export=='csv':
        stream=io.StringIO(newline='')
        writer=csv.DictWriter(stream,fieldnames=['id','title','type','url','listing'])
        writer.writeheader()
        writer.writerows(rows)
        exported=publisher.store.put(stream.getvalue(),'text/csv',publisher.source,result_url,role='mechanical_export',parent_ref=artifact['ref'])
    elif export in ('bibtex','ris','endnote','plain'):
        from publishers import publication_metadata
        artifacts=[]
        for row in rows:
            document=publisher.gateway.context.new_page()
            try:
                goto_source(document,row['url'],profile.hosts,wait_until='domcontentloaded',timeout=45000)
                document.locator('meta[name=citation_doi]').wait_for(state='attached',timeout=30000)
                metadata=publication_metadata(document.content())
                identifiers=metadata.get('citation_doi',[])
                if len(identifiers)!=1:
                    raise ServiceError('identity_missing','Publisher document has no unique DOI')
                artifacts.append(citation(publisher,document,identifiers[0],export))
            except ServiceError as error:
                failures.append({'id':row['id'],**error.result})
            except Exception as error:
                failures.append({'id':row['id'],'status':'error','code':'citation_export_failed','error_type':type(error).__name__})
            finally:
                document.close()
        exported={'status':'partial' if failures else 'available','artifacts':artifacts,'failures':failures}
    more=start+len(rows)<total
    return {'status':'partial' if failures else 'ok' if rows else 'not_found','source':publisher.source,'query':query,
            'start':start,'requested':limit,'received':len(rows),'total':total,'has_more':more,'next':{'start':start+len(rows)} if more else None,
            'records':artifact,'export':exported,'evidence':evidence,'preview':[{k:r[k] for k in ('id','title','type')} for r in rows[:3]]}

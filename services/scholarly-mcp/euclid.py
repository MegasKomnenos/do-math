"""Project Euclid native browser search and document citation controls."""
import csv,io,json,re
from urllib.parse import urljoin,urlsplit,parse_qs,urlencode,urlunsplit,unquote
from bs4 import BeautifulSoup
from scholarly import ServiceError,encoded,bibliography
from browser_adapters import clean_html,goto_source,dismiss_cookies,require_source_url,is_access_challenge


def records(raw,base):
    soup=BeautifulSoup(raw,'html.parser')
    count=soup.select_one('#searchHeaderTotalResults')
    match=re.search(r'([\d,]+) results found',count.get_text(' ',strip=True) if count else '')
    if not match:
        raise ServiceError('search_not_ready','Project Euclid has not displayed a search result count')
    total=int(match[1].replace(',',''))
    current=soup.select_one('#SearchPaginationTray .current')
    page=int(current.get_text(strip=True)) if current else 1
    size=soup.select_one('#loadMorePageSize option[selected]')
    capacity=int(parse_qs(urlsplit(base).query).get('pageSize',[size['value'] if size else '25'])[0])
    first=(page-1)*capacity
    rows=[]
    for node in soup.select('#SearchLoadMoreResultsContainer [id]'):
        if not re.fullmatch(r'result\d+',node['id']):
            continue
        anchor=node.select_one('.SearchHighlightContainer a[href]')
        if not anchor:
            raise ServiceError('search_parse_failed','Project Euclid result has no publication title link')
        url=urljoin(base,anchor['href'])
        matched=re.search(r'/(10\..+)\.(?:full|short)$',unquote(urlsplit(url).path))
        abstract=node.select_one('[id^=divSearchLineItem]')
        rows.append({'id':matched[1] if matched else url,'doi':matched[1] if matched else None,
                     'title':anchor.get_text(' ',strip=True),'url':url,
                     'authors':[a.get_text(' ',strip=True) for a in node.select('.ProfileTocLineItemNameText')],
                     'abstract_html':str(abstract) if abstract else None,'listing':node.get_text('\n',strip=True)})
    if len(rows)!=min(capacity,max(0,total-first)):
        raise ServiceError('range_mismatch','Project Euclid visible rows do not match its page and count')
    return rows,total,first


FIELDS=('ALL','ABSTRACT','AUTHORNAME','AFFILIATION','DOI_ISSN_ISBN','FIGURETABLECAPTIONS','KEYWORDS','TITLE')


def native_clause(term):
    """Serialize one advanced row using the syntax emitted by Euclid's form."""
    clause='('+term['query']+')'
    field=term.get('field','ALL')
    return clause if field=='ALL' else field+':'+clause


def extend_native_query(prefix,terms):
    expression=prefix
    for term in terms:
        expression+=' '+term.get('operator','AND')+' '+native_clause(term)
    return expression


def retains_native_terms(expression,terms):
    offset=0
    for index,term in enumerate(terms):
        clause=native_clause(term);position=expression.find(clause,offset)
        if position<0:return False
        between=re.sub(r'[()\s]','',expression[offset:position])
        expected='' if index==0 else term.get('operator','AND')
        if between!=expected:return False
        offset=position+len(clause)
    return not re.sub(r'[()\s]','',expression[offset:])


def citation(adapter,page,identifier,format='bibtex'):
    from pathlib import Path
    from api_adapters import doi
    number,media={'ris':(1,'application/x-research-info-systems'),'endnote':(2,'application/x-endnote-refer'),'bibtex':(3,'application/x-bibtex'),'citation-pdf':(4,'application/pdf')}[format]
    dismiss_cookies(page)
    if not page.locator('#downloadCitation').is_visible():
        page.get_by_text('Download Citation',exact=True).first.click()
    page.locator('label[for="downloadCitationCheckbox1-2"]').click()
    page.locator('label[for="downloadCitationCheckbox2-'+str(number)+'"]').click()
    with page.expect_download(timeout=30000) as pending:
        page.locator('#downloadCitation').click()
    download=pending.value
    require_source_url(download.url,adapter.profile.download_hosts)
    data=Path(download.path()).read_bytes()
    if format=='citation-pdf':
        import pymupdf
        try:
            with pymupdf.open(stream=data,filetype='pdf') as document:
                pages=len(document)
                text='\n'.join(page.get_text() for page in document)
        except Exception:
            raise ServiceError('invalid_document','Project Euclid returned no readable citation PDF') from None
        if not identifier or identifier.casefold() not in text.casefold():
            raise ServiceError('identity_mismatch','Project Euclid citation PDF does not identify the requested DOI')
        return adapter.store.put(data,media,adapter.source,download.url,role='native_citation',format=format,doi=identifier,pages=pages)
    parsed=bibliography(data,media)
    candidates=[]
    if len(parsed)==1:
        row=parsed[0]
        candidates=[row.get('doi')]+row.get('fields',{}).get('do',[])+row.get('fields',{}).get('R',[])+row.get('fields',{}).get('DOI',[])
    matched=False
    for candidate in candidates:
        try:
            matched=matched or doi(candidate or '').casefold()==(identifier or '').casefold()
        except ServiceError:
            continue
    if not matched:
        raise ServiceError('identity_mismatch','Project Euclid citation does not identify the requested DOI')
    return adapter.store.put(data,media,adapter.source,download.url,role='native_citation',format=format,doi=identifier)


def search(adapter,query,*,options,start=0,limit=20,cursor=None,export=None):
    allowed={'field','terms','year_from','year_to','publication_titles','sort','page_size'}
    if cursor or set(options)-allowed or options.get('field','ALL') not in FIELDS:
        raise ServiceError('invalid_options','Use the documented Project Euclid fields, terms and publication/year conditions')
    if type(start) is not int or start<0 or type(limit) is not int or not 1<=limit<=1000:
        raise ServiceError('invalid_range','Use start >= 0 and limit 1..1000')
    capacity=options.get('page_size',25)
    if type(capacity) is not int or capacity not in (25,50,75,100) or options.get('sort','Relevance') not in ('Relevance','PubDateDesc','PubDateAsc','TitleAsc','TitleDesc'):
        raise ServiceError('invalid_options','Use a native sort value and page_size 25, 50, 75 or 100')
    range_limit=capacity*50
    if start+limit>range_limit:
        raise ServiceError('source_range_limit','Project Euclid exposes 50 pages; narrow the query or increase page_size to request this range',range_limit=range_limit)
    if export not in (None,'json','html','csv','ris','bibtex','endnote','citation-pdf'):
        raise ServiceError('invalid_export','Use json, html, csv, ris, bibtex, endnote or citation-pdf')
    if not isinstance(options.get('terms',[]),list) or not isinstance(options.get('publication_titles',[]),list) or any(not isinstance(title,str) for title in options.get('publication_titles',[])):
        raise ServiceError('invalid_options','terms and publication_titles must be lists')
    terms=[{'query':query,'field':options.get('field','ALL')}]+options.get('terms',[])
    if any(not isinstance(t,dict) or set(t)-{'query','field','operator'} or not isinstance(t.get('query'),str) or t.get('field','ALL') not in FIELDS or t.get('operator','AND') not in ('AND','OR','NOT') for t in terms):
        raise ServiceError('invalid_options','Each term needs query, field and AND/OR/NOT operator')
    for key in ('year_from','year_to'):
        if key in options and (type(options[key]) is not int or not 1000<=options[key]<=9999):
            raise ServiceError('invalid_options','Publication years must be four-digit integers')
    if options.get('year_from',0)>options.get('year_to',9999):
        raise ServiceError('invalid_options','Publication year range is reversed')
    # Euclid restores advanced-search filters from browser storage, including
    # selections that are no longer reflected by native checkbox state.
    adapter.gateway.start()
    context=adapter.gateway.browser.new_context(accept_downloads=True)
    context.set_default_timeout(25000)
    page=context.new_page()
    evidence=[]
    try:
        goto_source(page,'https://projecteuclid.org/',adapter.profile.hosts,wait_until='domcontentloaded',timeout=45000)
        dismiss_cookies(page)
        if set(options)-{'sort','page_size'}:
            page.locator('a').filter(has_text=re.compile(r'^Advanced Search$')).filter(visible=True).last.click(timeout=15000)
            for i,term in enumerate(terms[:10]):
                if not page.locator('#advSearchText'+str(i)).count():
                    page.locator('#advSearchAddField:visible').last.click()
                page.locator('#advSearchText'+str(i)).fill(term['query'])
                page.locator('#advSearchField'+str(i)).select_option(term.get('field','ALL'))
                if i:
                    page.locator('#advSearchLogic'+str(i)).select_option(term.get('operator','AND'))
            for key,control in (('year_from','advSearchYearSliderStart'),('year_to','advSearchYearSliderEnd')):
                if key in options:
                    page.locator('#'+control).fill(str(options[key]))
            if options.get('publication_titles'):
                page.locator('label[for="chooseTitlesCheck"]').click()
                page.locator('#titleButton').click()
                for title in options['publication_titles']:
                    label=page.locator('#advSearchPubTitleAllTitlesContainer label').filter(has_text=re.compile('^'+re.escape(title)+'$'))
                    if label.count()!=1:
                        raise ServiceError('invalid_options','Publication title is not an exact available title',publication_title=title)
                    label.click()
            page.locator('#advSearchSubmitButton').click()
        else:
            page.locator('#homePageSearchTerm').fill(query)
            page.locator('#homePageSearchTerm').press('Enter')
        page.wait_for_url(lambda url:urlsplit(str(url)).path=='/search',timeout=45000)
        search_url=page.url
        request_params=parse_qs(urlsplit(search_url).query)
        if not request_params.get('term'):
            raise ServiceError('query_mismatch','Project Euclid did not retain the submitted search expression')
        if not retains_native_terms(request_params['term'][0],terms[:10]):
            raise ServiceError('query_mismatch','Project Euclid search expression does not retain every submitted term')
        expanded_native_query=False
        if len(terms)>10:
            expression=extend_native_query(request_params['term'][0],terms[10:])
            request_params['term']=[expression]
            if not retains_native_terms(expression,terms):
                raise ServiceError('query_mismatch','Project Euclid extended search expression does not retain every submitted term')
            parsed=urlsplit(search_url)
            search_url=urlunsplit((parsed.scheme,parsed.netloc,parsed.path,urlencode(request_params,doseq=True),''))
            expanded_native_query=True
        if not options.get('publication_titles') and request_params.get('PubTitle'):
            raise ServiceError('query_mismatch','Project Euclid retained an unrequested publication filter')
        for key,native in (('year_from','startYear'),('year_to','endYear')):
            if key in options and request_params.get(native)!=[str(options[key])]:
                raise ServiceError('query_mismatch','Project Euclid did not retain the requested publication year')
        for key,native in (('sort','sortBy'),('page_size','pageSize')):
            if key in options:
                request_params[native]=[str(options[key])]
        parsed=urlsplit(search_url)
        search_url=urlunsplit((parsed.scheme,parsed.netloc,parsed.path,urlencode(request_params,doseq=True),''))
        wanted_page=start//capacity+1
        selected=[]
        total=None
        while True:
            if wanted_page!=1 or set(options)&{'sort','page_size'} or expanded_native_query:
                parsed=urlsplit(search_url)
                params={**request_params,'page':[str(wanted_page)],'getFacetCountOverride':['true']}
                goto_source(page,urlunsplit((parsed.scheme,parsed.netloc,parsed.path,urlencode(params,doseq=True),'')),adapter.profile.hosts,wait_until='domcontentloaded',timeout=45000)
            try:
                page.wait_for_function("() => /[\\d,]+ results found/.test(document.querySelector('#searchHeaderTotalResults')?.textContent || '')",timeout=60000)
                page.wait_for_function("() => !document.querySelector('#SearchLoadMoreWait') || getComputedStyle(document.querySelector('#SearchLoadMoreWait')).display === 'none'",timeout=60000)
            except Exception as error:
                raw=page.content()
                if is_access_challenge(raw) or 'Additional security check is required' in page.locator('body').inner_text():
                    raise ServiceError('publisher_access_challenge','Project Euclid returned an access verification page',status='restricted',page=wanted_page) from None
                raise ServiceError('search_page_not_ready','Project Euclid requested result page did not render',page=wanted_page,error_type=type(error).__name__) from None
            raw=clean_html(page.content(),adapter.store.sanitizer)
            proof=adapter.store.put(raw,'text/html',adapter.source,page.url,role='search_page',query=query,options=options)
            evidence.append(proof)
            rows,reported,first=records(raw,page.url)
            if first!=(wanted_page-1)*capacity or total is not None and reported!=total:
                raise ServiceError('range_mismatch','Project Euclid page or total changed',evidence=evidence)
            total=reported
            selected.extend(row for i,row in enumerate(rows,first) if start<=i<start+limit)
            if first+len(rows)>=min(start+limit,total):
                break
            wanted_page+=1
        filters=adapter.store.put(encoded({'publication_titles':[' '.join(title.split()) for title in page.locator('#advSearchPubTitleAllTitlesContainer label').all_inner_texts()]}),'application/json',adapter.source,search_url,role='search_filters')
        artifact=adapter.store.put(encoded(selected),'application/json',adapter.source,search_url,role='records',query=query,options=options,start=start,total=total)
        exported=artifact
        export_errors=[]
        if export=='html':
            exported={'artifacts':evidence}
        elif export=='csv':
            buffer=io.StringIO(newline='')
            fields=list(dict.fromkeys(k for row in selected for k in row))
            writer=csv.DictWriter(buffer,fieldnames=fields)
            writer.writeheader()
            writer.writerows({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in row.items()} for row in selected)
            exported=adapter.store.put(buffer.getvalue(),'text/csv',adapter.source,search_url,role='mechanical_export',parent_ref=artifact['ref'])
        elif export in ('ris','bibtex','endnote','citation-pdf'):
            artifacts=[]
            for row in selected:
                try:
                    goto_source(page,row['url'],adapter.profile.hosts,wait_until='domcontentloaded',timeout=45000)
                    artifacts.append({'id':row['id'],'artifact':citation(adapter,page,row['doi'],export)})
                except ServiceError as error:
                    export_errors.append({'id':row['id'],**error.result})
                except Exception as error:
                    export_errors.append({'id':row['id'],'status':'error','code':'citation_export_failed','error_type':type(error).__name__})
            exported={'format':export,'artifacts':artifacts,'errors':export_errors}
        more=start+len(selected)<total
        return {'status':'partial' if export_errors else 'ok' if selected else 'not_found','source':adapter.source,'query':query,'options':options,
                'native_query':request_params,'start':start,'requested':limit,'received':len(selected),'total':total,
                'has_more':more,'next':{'start':start+len(selected)} if more and start+len(selected)<range_limit else None,'range_limit':range_limit,
                'records':artifact,'export':exported,'evidence':evidence,'facets':filters,'preview':[{k:r[k] for k in ('id','title')} for r in selected[:3]]}
    except ServiceError:raise
    except Exception as error:
        raise ServiceError('search_interaction_failed','Project Euclid search controls did not complete the requested interaction',error_type=type(error).__name__) from None
    finally:
        context.close()

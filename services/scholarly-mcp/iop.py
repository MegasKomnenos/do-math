"""Native IOP citation controls on the selected institutional article."""
from urllib.parse import parse_qs, urljoin, urlsplit, unquote
from waits import SOURCE_WAIT_MS

from api_adapters import doi
from browser_adapters import browser_download
from scholarly import ServiceError, bibliography, failure_details


def citation(adapter,page,identifier,format='bibtex'):
    classes={'bibtex':'wd-btn-cit-abs-bib','ris':'wd-btn-cit-abs-ris'}
    media={'bibtex':'application/x-bibtex','ris':'application/x-research-info-systems'}[format]
    control=page.locator('a.'+classes[format])
    control.first.wait_for(state='attached',timeout=SOURCE_WAIT_MS)
    url=urljoin(page.url,control.first.get_attribute('href'))
    selected=parse_qs(urlsplit(url).query).get('doi',[])
    if len(selected)!=1 or doi(selected[0]).casefold()!=identifier.casefold():
        raise ServiceError('identity_mismatch','IOP citation control identifies another DOI')
    data,source_media,actual=browser_download(adapter.gateway.context,url,adapter.profile.download_hosts)
    try:
        rows=bibliography(data,media)
        observed=rows[0].get('doi') if format=='bibtex' and rows else rows[0].get('fields',{}).get('do',[None])[0] if rows else None
        if len(rows)!=1 or not observed or doi(observed).casefold()!=identifier.casefold():
            raise ServiceError('identity_mismatch','IOP citation identifies another DOI')
    except ServiceError as error:
        error.result['source_export']=adapter.store.put(data,media,adapter.source,actual,role='unparsed_native_citation',format=format,requested_doi=identifier,source_media_type=source_media)
        raise
    return adapter.store.put(data,media,adapter.source,actual,role='native_citation',format=format,doi=identifier,source_media_type=source_media,parse_warnings=rows[0].get('parse_warnings',[]))


def supplementary(adapter,page,identifier,source_page):
    from bs4 import BeautifulSoup
    from browser_adapters import goto_source,clean_html,is_access_challenge
    from publishers import publication_metadata,publication_dois
    from supplements import fetch_supplementary
    links=BeautifulSoup(page.content(),'html.parser').select('a.wd-btn-supp-data[href]')
    if not links:
        return {'status':'source_page','artifact':source_page,'reason':'No recognized IOP supplementary data control on this article'}
    urls={urljoin(page.url,a['href']) for a in links}
    if len(urls)!=1 or not identifier or unquote(urlsplit(next(iter(urls))).path).casefold()!=('/article/'+identifier+'/data').casefold():
        return {'status':'error','code':'identity_mismatch','message':'IOP supplementary control identifies no unique selected DOI'}
    viewer=adapter.gateway.context.new_page()
    try:
        goto_source(viewer,next(iter(urls)),adapter.profile.hosts,wait_until='domcontentloaded',timeout=SOURCE_WAIT_MS)
        raw=viewer.content()
        if is_access_challenge(raw):raise ServiceError('publisher_access_challenge','IOP supplementary page requires access verification',status='restricted')
        observed=publication_dois(publication_metadata(raw))
        if {value.casefold() for value in observed}!={identifier.casefold()}:
            raise ServiceError('identity_mismatch','IOP supplementary page identifies a different DOI')
        proof=adapter.store.put(clean_html(raw,adapter.store.sanitizer),'text/html',adapter.source,viewer.url,
            role='supplementary_source_page',doi=identifier,parent_ref=source_page['ref'])
        return fetch_supplementary(adapter,viewer,identifier,proof)
    except ServiceError as error:return error.result
    except Exception as error:return {'status':'error','code':'supplementary_page_failed',**failure_details(error)}
    finally:viewer.close()

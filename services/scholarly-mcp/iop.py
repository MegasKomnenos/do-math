"""Native IOP citation controls on the selected institutional article."""
from urllib.parse import parse_qs, urljoin, urlsplit

from api_adapters import doi
from browser_adapters import browser_download
from scholarly import ServiceError, bibliography


def citation(adapter,page,identifier,format='bibtex'):
    classes={'bibtex':'wd-btn-cit-abs-bib','ris':'wd-btn-cit-abs-ris'}
    media={'bibtex':'application/x-bibtex','ris':'application/x-research-info-systems'}[format]
    control=page.locator('a.'+classes[format])
    control.first.wait_for(state='attached',timeout=20000)
    url=urljoin(page.url,control.first.get_attribute('href'))
    selected=parse_qs(urlsplit(url).query).get('doi',[])
    if len(selected)!=1 or doi(selected[0]).casefold()!=identifier.casefold():
        raise ServiceError('identity_mismatch','IOP citation control identifies another DOI')
    data,source_media,actual=browser_download(adapter.gateway.context,url,adapter.profile.download_hosts)
    rows=bibliography(data,media)
    observed=rows[0].get('doi') if format=='bibtex' and rows else rows[0].get('fields',{}).get('do',[None])[0] if rows else None
    if len(rows)!=1 or not observed or doi(observed).casefold()!=identifier.casefold():
        raise ServiceError('identity_mismatch','IOP citation identifies another DOI')
    return adapter.store.put(data,media,adapter.source,actual,role='native_citation',format=format,doi=identifier,source_media_type=source_media)

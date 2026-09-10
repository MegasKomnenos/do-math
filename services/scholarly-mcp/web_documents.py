"""Direct public document URLs for the two intentionally open source categories."""
import ipaddress
import re
import socket
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup

from browser_adapters import browser_download, clean_html
from publishers import publication_metadata
from scholarly import ServiceError, encoded, bibliography


def public_document_hosts(target):
    parts = urlsplit(target)
    if parts.scheme not in ('https', 'http') or not parts.hostname or parts.username or parts.password or parts.port not in (None, 80, 443):
        raise ServiceError('invalid_target', 'Use an absolute public HTTP(S) document URL without credentials')
    try:
        addresses = socket.getaddrinfo(parts.hostname, parts.port or (443 if parts.scheme == 'https' else 80), type=socket.SOCK_STREAM)
    except socket.gaierror:
        raise ServiceError('host_unresolved', 'Document host could not be resolved') from None
    if not addresses or any(not ipaddress.ip_address(item[4][0]).is_global for item in addresses):
        raise ServiceError('source_boundary', 'Public document categories cannot access private or local network addresses')
    return {parts.hostname}


class WebDocuments:
    def __init__(self, store, gateway, source):
        self.store, self.gateway, self.source = store, gateway, source
        self.context = None

    def search(self, query, *, options, start=0, limit=20, cursor=None, export=None):
        raise ServiceError('specific_source_required', 'This category has no single catalogue. Select a named source for native search, or fetch a known document URL.', status='selection_required', source=self.source)

    def fetch(self, target, *, parts):
        if set(parts) - {'metadata', 'abstract', 'fulltext', 'export', 'supplementary'}:
            raise ServiceError('invalid_parts', 'Use the documented content parts')
        hosts = public_document_hosts(target)
        from registry import SOURCES
        named = [s.id for s in SOURCES.values() if s.home and s.role != 'open_category' and
                 (urlsplit(s.home).hostname or '').removeprefix('www.') == urlsplit(target).hostname.removeprefix('www.')]
        if named:
            raise ServiceError('specific_source_available', 'Use the named source adapter for this platform', status='selection_required', sources=named)
        self.gateway.start()
        if self.context is None:
            self.context = self.gateway.browser.new_context(accept_downloads=True)
        data, media, actual = browser_download(self.context, target, hosts)
        if not data:
            raise ServiceError('empty_document', 'The public document endpoint returned no content')
        components = {}
        if data.startswith(b'%PDF-'):
            import pymupdf
            with pymupdf.open(stream=data, filetype='pdf') as pdf:
                pages = len(pdf)
                metadata = pdf.metadata
            document = self.store.put(data, 'application/pdf', self.source, actual, role='fulltext', pages=pages, requested_target=target)
            record = {'url':actual, 'type':'pdf_document', 'metadata':metadata, 'pages':pages,
                      'identity_basis':'Exact requested URL and embedded PDF metadata; no external identity inference'}
        elif media in ('text/html','application/xhtml+xml') or data.lstrip().lower().startswith((b'<!doctype html',b'<html')):
            raw = data
            soup = BeautifulSoup(raw,'html.parser')
            title = soup.title.get_text(' ',strip=True) if soup.title else ''
            if re.search(r'^(?:Access Denied|Just a moment|Attention Required|403 Forbidden|Sign in|Login|로그인)', title, re.I):
                raise ServiceError('access_restricted', 'This document requires access not available in the public category', status='restricted')
            metadata = publication_metadata(raw)
            body = soup.body or soup
            if not body.get_text(' ',strip=True):
                raise ServiceError('dynamic_document_not_ready','This URL returned a script-only shell; select a document file or a platform adapter',status='not_implemented')
            document = self.store.put(clean_html(raw,self.store.sanitizer),'text/html',self.source,actual,role='requested_web_page',requested_target=target)
            titles = metadata.get('citation_title',metadata.get('dc.title',[title]))
            record = {'url':self.store.sanitizer.url(actual),'type':'web_document','title':titles[0] if titles else title,'metadata':metadata}
            if 'export' in parts:
                citation_links = soup.select('.citation_formats a[href*="/citationstylelanguage/download/"]')
                if citation_links:
                    from api_adapters import APIAdapter, doi
                    api = APIAdapter(self.store)
                    api.source, api.hosts = self.source, tuple(hosts)
                    artifacts, errors = [], []
                    try:
                        for control in citation_links:
                            kind = urlsplit(control['href']).path.rstrip('/').rsplit('/',1)[-1]
                            native_media = {'bibtex':'application/x-bibtex','ris':'application/x-research-info-systems'}.get(kind)
                            if not native_media:
                                continue
                            try:
                                value, evidence = api.request(urljoin(actual,control['href']),accept='binary')
                                rows = bibliography(value,native_media)
                                observed = rows[0].get('doi') if kind=='bibtex' and rows else rows[0].get('fields',{}).get('do',[None])[0] if rows else None
                                expected = metadata.get('citation_doi',[None])[0]
                                if len(rows)!=1 or (expected and (not observed or doi(observed).casefold()!=doi(expected).casefold())):
                                    raise ServiceError('identity_mismatch','Native citation does not match this document DOI')
                                artifact = self.store.put(value,native_media,self.source,evidence['url'],role='native_citation',evidence_ref=evidence['ref'])
                                artifacts.append({'format':kind,'artifact':artifact})
                            except ServiceError as error:
                                errors.append({'format':kind,**error.result})
                    finally:
                        api.client.close()
                    if artifacts or errors:
                        components['export'] = {'status':'partial' if errors else 'available','artifacts':artifacts,'errors':errors}
                        if artifacts:
                            components['export']['artifact'] = artifacts[0]['artifact']
            marked = soup.select('section.abstract, .abstract, #abstract, #Abs1')
            if marked:
                abstract = self.store.put(clean_html('\n'.join(str(n) for n in marked),self.store.sanitizer),'text/html',self.source,actual,role='marked_abstract',parent_ref=document['ref'])
                components['abstract'] = {'status':'available','artifact':abstract}
            links = [{'label':a.get_text(' ',strip=True),'url':self.store.sanitizer.url(urljoin(actual,a['href'])),
                      'same_host':urlsplit(urljoin(actual,a['href'])).hostname in hosts} for a in soup.select('a[href]')
                     if urlsplit(urljoin(actual,a['href'])).scheme in ('http','https')]
            if 'supplementary' in parts:
                artifact = self.store.put(encoded(links),'application/json',self.source,actual,role='page_link_index',parent_ref=document['ref'])
                components['supplementary'] = {'status':'available','artifact':artifact,'scope':'Links on the requested page; linked documents were not retrieved'}
            if 'fulltext' in parts:
                pdf_links = metadata.get('citation_pdf_url',[])
                if len(pdf_links) == 1:
                    link = urljoin(actual,pdf_links[0])
                    if urlsplit(link).hostname in hosts:
                        try:
                            pdf_data, _, obtained = browser_download(self.context,link,hosts)
                            if not pdf_data.startswith(b'%PDF-'):
                                raise ServiceError('unexpected_content','Document PDF metadata did not return a PDF')
                            import pymupdf
                            with pymupdf.open(stream=pdf_data,filetype='pdf') as pdf:
                                pages = len(pdf)
                            pdf_ref = self.store.put(pdf_data,'application/pdf',self.source,obtained,role='fulltext',pages=pages,parent_ref=document['ref'])
                            components['fulltext'] = {'status':'available','artifact':pdf_ref,'source_page':document}
                        except ServiceError as error:
                            components['fulltext'] = {**error.result,'source_page':document}
                    else:
                        components['fulltext'] = {'status':'external_link','url':self.store.sanitizer.url(link),'source_page':document}
        else:
            if media.startswith('text/'):
                document = self.store.put(data,media,self.source,actual,role='requested_document')
            else:
                document = self.store.put(data,media or 'application/octet-stream',self.source,actual,preserve_bytes=True,role='requested_document')
            record = {'url':actual,'type':'document_file','media_type':document['media_type'],'bytes':len(data)}
        records = self.store.put(encoded([record]),'application/json',self.source,actual,role='records',evidence_ref=document['ref'])
        for part in parts:
            if part in components:
                continue
            if part in ('metadata','export'):
                components[part] = {'status':'available','artifact':records,'format':'source_metadata_json'}
            elif part == 'fulltext':
                components[part] = {'status':'available','artifact':document,'scope':'Content of the requested document URL'}
            else:
                components[part] = {'status':'not_offered','reason':'No separately marked content of this kind in the requested document'}
        components = {k:v for k,v in components.items() if k in parts}
        return {'status':'ok' if all(c['status']=='available' for c in components.values()) else 'partial','source':self.source,
                'target':self.store.sanitizer.url(target),'records':records,'source_document':document,'components':components,
                'scope':'The exact public document and its own same-host citation PDF; other linked documents are not followed'}

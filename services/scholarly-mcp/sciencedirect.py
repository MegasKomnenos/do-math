"""ScienceDirect institutional citation exports and document retrieval."""
import re
from urllib.parse import urlencode, urlsplit, urlunsplit, unquote

from browser_adapters import browser_download
from api_adapters import doi
from publishers import Publisher, PROFILES
from scholarly import ServiceError, bibliography, encoded

FORMATS = {'ris': 'application/x-research-info-systems', 'bibtex': 'text/x-bibtex', 'plain': 'text/plain'}


def pii_from_url(url):
    match = re.search(r'/pii/([A-Z0-9]+)(?:/|$)', unquote(urlsplit(url).path))
    if not match:
        raise ServiceError('invalid_target', 'The ScienceDirect URL has no PII')
    return match[1]


def citation_record(data, pii, expected_doi=None):
    rows = bibliography(data, 'application/x-research-info-systems')
    if len(rows) != 1:
        raise ServiceError('identity_mismatch', 'ScienceDirect returned no unique citation')
    row = rows[0]
    if not any(pii_from_url(url) == pii for url in row['fields'].get('ur', []) if '/pii/' in url):
        raise ServiceError('identity_mismatch', 'ScienceDirect citation identifies another PII')
    observed = row['fields'].get('do', [None])[0]
    if expected_doi and (not observed or doi(observed).casefold() != expected_doi.casefold()):
        raise ServiceError('identity_mismatch', 'ScienceDirect citation identifies another DOI')
    return {'id':pii, 'pii':pii, 'title':row['fields'].get('t1',row['fields'].get('ti',[None]))[0],
            'doi':doi(observed) if observed else None, **row}


class ScienceDirect(Publisher):
    def __init__(self, store, gateway):
        super().__init__(store,gateway,next(p for p in PROFILES if p.source=='science-direct'))

    def citation(self, pii, format='ris', expected_doi=None):
        page = self.gateway.open(self.source,self.profile.gateway_label,self.profile.hosts,'body')
        origin = urlsplit(page.url)
        url = urlunsplit((origin.scheme,origin.netloc,'/sdfe/arp/cite',urlencode({'pii':pii,'format':FORMATS[format],'withabstract':'true'}),''))
        data, media, actual = browser_download(self.gateway.context,url,self.profile.hosts)
        canonical = 'application/x-bibtex' if format=='bibtex' else FORMATS[format]
        if format in ('ris','bibtex'):
            rows = bibliography(data,canonical)
            if len(rows)!=1:
                raise ServiceError('identity_mismatch','ScienceDirect citation is not a single record')
            observed = rows[0].get('doi') if format=='bibtex' else rows[0].get('fields',{}).get('do',[None])[0]
            if expected_doi and (not observed or doi(observed).casefold()!=expected_doi.casefold()):
                raise ServiceError('identity_mismatch','ScienceDirect export identifies another DOI')
        elif not data.strip() or data.lstrip().startswith(b'<'):
            raise ServiceError('unexpected_content','ScienceDirect returned no plain citation')
        elif expected_doi and expected_doi.casefold() not in data.decode('utf-8').casefold():
            raise ServiceError('identity_mismatch','ScienceDirect plain citation does not identify the requested DOI')
        artifact = self.store.put(data,canonical,self.source,actual,role='native_citation',pii=pii,format=format,source_media_type=media)
        return data, artifact

    def fetch(self,target,*,parts):
        if set(parts)-{'metadata','abstract','fulltext','supplementary','export'}:
            raise ServiceError('invalid_parts','Use the documented content parts')
        expected_doi = None
        if re.fullmatch(r'[SB][A-Z0-9]{8,30}',target):
            pii = target
        elif target.startswith(('http://','https://','10.','doi:')):
            url, expected_doi = self.resolve_target(target)
            pii = pii_from_url(url)
        else:
            return self.search(target,options={'field':'Title'},limit=20)
        data, native = self.citation(pii)
        row = citation_record(data,pii,expected_doi)
        records = self.store.put(encoded([row]),'application/json',self.source,native['url'],role='records',parent_ref=native['ref'])
        components = {}
        for part in parts:
            if part=='metadata':
                components[part]={'status':'available','artifact':records}
            elif part=='abstract':
                values=row['fields'].get('ab',[])
                if values:
                    abstract=self.store.put('\n\n'.join(values),'text/plain',self.source,native['url'],role='native_abstract_field',parent_ref=native['ref'])
                    components[part]={'status':'available','artifact':abstract}
                else:
                    components[part]={'status':'not_offered','reason':'This native citation contains no abstract field'}
            elif part=='export':
                artifacts=[{'format':'ris','artifact':native}]
                errors=[]
                for format in ('bibtex','plain'):
                    try:
                        _, artifact=self.citation(pii,format,expected_doi=row['doi'])
                        artifacts.append({'format':format,'artifact':artifact})
                    except ServiceError as error:
                        errors.append({'format':format,**error.result})
                components[part]={'status':'partial' if errors else 'available','artifact':native,'artifacts':artifacts,'errors':errors}
            elif part=='fulltext':
                try:
                    full=super().fetch('https://www.sciencedirect.com/science/article/pii/'+pii,parts=['fulltext'])
                    components[part]=full['components']['fulltext']
                except ServiceError as error:
                    components[part]=error.result
            else:
                components[part]={'status':'not_implemented','reason':'Document-bound supplementary files require the publisher page; citation metadata remains available'}
        return {'status':'ok' if all(c['status']=='available' for c in components.values()) else 'partial','source':self.source,
                'target':target,'pii':pii,'records':records,'components':components,'native_citation':native}

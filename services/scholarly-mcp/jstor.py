"""JSTOR's publicly accessible native citation endpoint."""
import re
from urllib.parse import quote,urlsplit,unquote

from api_adapters import APIAdapter
from scholarly import ServiceError,encoded,bibliography


def stable_id(value):
    if value.startswith(('http://','https://')):
        parsed=urlsplit(value)
        if parsed.hostname in ('doi.org','dx.doi.org'):
            value=parsed.path.lstrip('/')
        elif parsed.hostname in ('www.jstor.org','jstor.org','www-jstor-org.libproxy.knu.ac.kr'):
            match=re.fullmatch(r'/stable/(?:pdf/)?(.+?)(?:\.pdf)?/?',parsed.path)
            if not match:
                raise ServiceError('invalid_target','Use a JSTOR stable URL')
            value=unquote(match[1])
        else:
            raise ServiceError('source_boundary','Target is outside JSTOR')
    value=re.sub(r'^doi:\s*','',value,flags=re.I)
    value=re.sub(r'^10\.2307/','',value,flags=re.I)
    if not re.fullmatch(r'(?:[0-9]+|(?:j|jj)\.[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)?|community\.[0-9]+|10\.\d{4,9}/[A-Za-z0-9._():;-]+)',value) or any(part in ('.','..') for part in value.split('/')):
        raise ServiceError('invalid_target','Use a JSTOR stable ID, stable URL or JSTOR-hosted DOI')
    return value


def document_pdf(adapter,identifier):
    from pathlib import Path
    from publishers import Publisher,PROFILES
    from browser_adapters import require_source_url,is_access_challenge
    if adapter.gateway is None:raise ServiceError('browser_session_unavailable','JSTOR institutional document session is not configured',status='restricted')
    profile=next(p for p in PROFILES if p.source=='jstor')
    page=Publisher(adapter.store,adapter.gateway,profile).document('https://www.jstor.org/stable/'+quote(identifier,safe='/'))
    stage='document_identity'
    try:
        if is_access_challenge(page.content()):raise ServiceError('publisher_access_challenge','JSTOR requires document access verification',status='restricted')
        if stable_id(page.url)!=identifier:raise ServiceError('identity_mismatch','JSTOR opened a different stable document')
        downloads=[];page.on('download',lambda download:downloads.append(download))
        with page.expect_download(timeout=60000) as pending:
            stage='download_control'
            page.get_by_role('button',name='Download',exact=True).click(timeout=45000)
            stage='terms_or_download'
            accept=page.get_by_role('button',name='Accept and download',exact=True)
            for _ in range(40):
                if downloads:break
                if accept.count() and accept.is_visible():
                    accept.click(timeout=15000);break
                page.wait_for_timeout(250)
            stage='download_ready'
        download=pending.value
        stage='file_identity'
        require_source_url(download.url,profile.download_hosts)
        if stable_id(download.url)!=identifier:raise ServiceError('identity_mismatch','JSTOR downloaded another stable document')
        data=Path(download.path()).read_bytes()
        if not data.startswith(b'%PDF-'):raise ServiceError('invalid_document','JSTOR Download returned no PDF')
        import pymupdf
        with pymupdf.open(stream=data,filetype='pdf') as document:pages=len(document)
        artifact=adapter.store.put(data,'application/pdf',adapter.source,download.url,preserve_bytes=True,role='fulltext',stable_id=identifier,pages=pages)
        return {'status':'available','artifact':artifact,'scope':'Complete native downloaded PDF, including any publisher cover or citation pages'}
    except ServiceError:raise
    except Exception as error:raise ServiceError('document_download_failed','JSTOR did not complete the native document download',stage=stage,error_type=type(error).__name__) from None
    finally:page.close()


class JSTOR(APIAdapter):
    source='jstor'
    hosts=('www.jstor.org','jstor.org')
    min_interval=1.05

    def __init__(self,store,client=None,*,gateway=None):
        super().__init__(store,client);self.gateway=gateway

    def search(self,query,*,options,start=0,limit=20,cursor=None,export=None):
        from jstor_search import search
        return search(self,query,options=options,start=start,limit=limit,cursor=cursor,export=export)

    def citation(self,identifier,format):
        path,media={'ris':('ris','application/x-research-info-systems'),'bibtex':('text','application/x-bibtex')}[format]
        data,evidence=self.request('https://www.jstor.org/citation/'+path+'/'+quote(identifier,safe='/'),accept='binary')
        native=self.store.put(data,media,self.source,evidence['url'],preserve_bytes=True,role='native_citation',format=format,
            stable_id=identifier,evidence_ref=evidence['ref'],source_media_type=evidence['media_type'])
        try:
            rows=bibliography(data,media)
            if len(rows)!=1:
                raise ServiceError('identity_mismatch','JSTOR returned no unique citation record')
            urls=rows[0]['fields'].get('ur',[]) if format=='ris' else [rows[0].get('url','')]
            if not any(stable_id(url)==identifier for url in urls if urlsplit(url).hostname in self.hosts):
                raise ServiceError('identity_mismatch','JSTOR citation does not identify the requested stable record')
        except ServiceError as error:
            error.result['source_export']=native
            raise
        return rows[0],native

    def fetch(self,target,*,parts):
        if set(parts)-{'metadata','abstract','export','fulltext','supplementary'}:
            raise ServiceError('invalid_parts','Use metadata, abstract, export, fulltext or supplementary')
        if not target.startswith(('http://','https://','10.','doi:','j.','jj.','community.')) and not target.isdigit():
            phrase=target.replace('\\','\\\\').replace('"','\\"')
            found=self.search('ti:"'+phrase+'"',options={},limit=20)
            return {**found,'status':'selection_required' if found.get('received') else found['status'],
                'message':'Select the exact JSTOR stable record from the title candidates'}
        identifier=stable_id(target)
        cited,native=self.citation(identifier,'ris')
        row={'id':identifier,'title':cited['fields'].get('ti',[None])[0],**cited}
        record=self.store.put(encoded([row]),'application/json',self.source,native['url'],role='records',parent_ref=native['ref'])
        components={}
        for part in parts:
            if part=='metadata':
                components[part]={'status':'available','artifact':record}
            elif part=='export':
                exports=[{'format':'ris','artifact':native}];errors=[]
                try:
                    _,bib=self.citation(identifier,'bibtex')
                    exports.append({'format':'bibtex','artifact':bib})
                except ServiceError as error:errors.append({'format':'bibtex',**error.result})
                except Exception as error:errors.append({'format':'bibtex','status':'error','code':'citation_export_failed','error_type':type(error).__name__})
                components[part]={'status':'partial' if errors else 'available','artifact':native,'format':'ris','artifacts':exports,'errors':errors}
            elif part=='abstract':
                values=row['fields'].get('ab',[])
                if values:
                    abstract=self.store.put('\n\n'.join(values),'text/plain',self.source,native['url'],role='abstract',parent_ref=native['ref'])
                    components[part]={'status':'available','artifact':abstract}
                else:
                    components[part]={'status':'not_offered','reason':'This native citation contains no abstract'}
            elif part=='fulltext':
                try:components[part]=document_pdf(self,identifier)
                except ServiceError as error:components[part]=error.result
            else:
                components[part]={'status':'not_implemented','reason':'Additional JSTOR document attachments are not connected'}
        return {'status':'ok' if all(v['status']=='available' for v in components.values()) else 'partial','source':self.source,'target':target,
                'records':record,'components':components,'stable_id':identifier}

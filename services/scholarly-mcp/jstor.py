"""JSTOR's publicly accessible native citation endpoint."""
import json,re
from urllib.parse import quote,urlsplit,unquote,urljoin,parse_qs

from api_adapters import APIAdapter
from scholarly import ServiceError,encoded,bibliography


def stable_id(value):
    if value.startswith(('http://','https://')):
        parsed=urlsplit(value)
        if parsed.hostname in ('doi.org','dx.doi.org'):
            value=parsed.path.lstrip('/')
        elif parsed.hostname in ('www.jstor.org','jstor.org','www-jstor-org.libproxy.knu.ac.kr'):
            match=re.fullmatch(r'/stable/(?:pdf/|download-image/)?(.+?)(?:\.pdf)?/?',parsed.path)
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


def download_permission(raw,identifier,uuid):
    entry=raw.get(uuid) if isinstance(raw,dict) else None
    if not isinstance(entry,dict) or not isinstance(entry.get('doi'),str) or stable_id(entry['doi'])!=identifier:
        raise ServiceError('identity_mismatch','JSTOR download permission identifies another document')
    if entry.get('access') not in ('download','restricted','disabled'):
        raise ServiceError('download_access_unrecognized','JSTOR returned an unrecognized download access state')
    return entry


def document_api(adapter,page,path,payload=None):
    from jstor_search import public_payload
    from browser_adapters import is_access_challenge
    url='https://'+urlsplit(page.url).hostname+path
    try:
        response=(adapter.gateway.context.request.get(url,max_redirects=0,timeout=45000) if payload is None else
            adapter.gateway.context.request.post(url,data=json.dumps(payload),headers={'Content-Type':'application/json'},max_redirects=0,timeout=45000))
    except Exception as error:raise ServiceError('document_api_failed','JSTOR document data could not be requested',error_type=type(error).__name__) from None
    if response.status in (401,403):raise ServiceError('access_restricted','JSTOR restricted document data',status='restricted')
    if response.status==429:raise ServiceError('rate_limited','JSTOR document request limit reached')
    if response.status!=200:raise ServiceError('provider_error','JSTOR document data request failed',http_status=response.status)
    data=response.body()
    try:raw=json.loads(data)
    except ValueError:
        if is_access_challenge(data):raise ServiceError('publisher_access_challenge','JSTOR requires document access verification',status='restricted') from None
        raise ServiceError('invalid_response','JSTOR returned no document JSON') from None
    proof=adapter.store.put(encoded(public_payload(raw)),'application/json',adapter.source,url,role='native_document_data')
    return raw,proof


def document_uuid(page):
    node=page.locator('#cdt[data-content-id]');node.wait_for(state='attached',timeout=30000);uuid=node.get_attribute('data-content-id')
    if not isinstance(uuid,str) or not re.fullmatch(r'[0-9a-f-]{36}',uuid):raise ServiceError('identity_mismatch','JSTOR document has no valid content identity')
    return uuid


def file_metadata(data):
    import pymupdf
    try:
        if data.startswith(b'%PDF-'):
            with pymupdf.open(stream=data,filetype='pdf') as document:return {'media_type':'application/pdf','pages':len(document)}
        media='image/jpeg' if data.startswith(b'\xff\xd8\xff') else 'image/png' if data.startswith(b'\x89PNG\r\n\x1a\n') else None
        if media:
            pixmap=pymupdf.Pixmap(data)
            return {'media_type':media,'width':pixmap.width,'height':pixmap.height}
        offset=0
        if data.startswith(b'ID3') and len(data)>=10 and data[3] in (2,3,4) and all(n<128 for n in data[6:10]):
            offset=10+sum(n<<(7*(3-i)) for i,n in enumerate(data[6:10]))
            if data[3]==4 and data[5]&0x10:offset+=10
        if len(data)>=offset+4:
            header=int.from_bytes(data[offset:offset+4],'big')
            if header>>21==0x7ff and (header>>19)&3!=1 and (header>>17)&3==1 and (header>>12)&15 not in (0,15) and (header>>10)&3!=3:
                return {'media_type':'audio/mpeg','audio_offset':offset}
    except Exception:raise ServiceError('invalid_document','JSTOR returned an unreadable native document or image') from None
    raise ServiceError('invalid_document','JSTOR returned no supported PDF, JPEG, PNG or MPEG audio')


def supplement_links(raw,identifier,base):
    content=raw.get('content',{}) if isinstance(raw,dict) else {}
    if not isinstance(content.get('doi'),str) or stable_id(content['doi'])!=identifier:
        raise ServiceError('identity_mismatch','JSTOR attachment metadata identifies another document')
    values=content.get('supplements')
    if not isinstance(values,list):raise ServiceError('invalid_response','JSTOR omitted its native supplement list')
    rows=[]
    for entry in values:
        if not isinstance(entry,dict):raise ServiceError('invalid_response','JSTOR returned malformed supplement metadata')
        url=urljoin(base,str(entry.get('link','')));parts=urlsplit(url);query=parse_qs(parts.query)
        row={'url':url,'filename':entry.get('filename'),'label':entry.get('text') or entry.get('filename') or 'Supplement',
            'linked_doi':entry.get('doi'),'mime_type':entry.get('mime_type'),'size':int(entry['size']) if str(entry.get('size','')).isdigit() else None}
        try:
            valid=(parts.scheme=='https' and parts.netloc==urlsplit(base).netloc and parts.path.startswith('/stable/get_asset/')
                and stable_id(unquote(parts.path.removeprefix('/stable/get_asset/')))==identifier
                and stable_id(entry.get('doi',''))==identifier and set(query)=={'supp_index'}
                and len(query['supp_index'])==1 and query['supp_index'][0].isdigit())
        except ServiceError:valid=False
        if not valid:row['invalid_link']=True
        rows.append(row)
    return rows


def document_page(adapter,identifier):
    from publishers import Publisher,PROFILES
    if adapter.gateway is None:raise ServiceError('browser_session_unavailable','JSTOR institutional document session is not configured',status='restricted')
    return Publisher(adapter.store,adapter.gateway,next(p for p in PROFILES if p.source=='jstor')).document('https://www.jstor.org/stable/'+quote(identifier,safe='/'))


def supplementary(adapter,identifier,*,page=None):
    from types import SimpleNamespace
    from pathlib import PurePosixPath
    from publishers import Publisher,PROFILES
    from supplements import fetch_supplementary
    profile=next(p for p in PROFILES if p.source=='jstor');owned=page is None
    if owned:page=document_page(adapter,identifier)
    try:
        from browser_adapters import is_access_challenge
        if is_access_challenge(page.content()):raise ServiceError('publisher_access_challenge','JSTOR requires document access verification',status='restricted')
        uuid=document_uuid(page);raw,proof=document_api(adapter,page,'/content-service/content-data/'+uuid)
        if raw.get('content',{}).get('id')!=uuid:raise ServiceError('identity_mismatch','JSTOR returned another document content identity')
        rows=supplement_links(raw,identifier,page.url);content=raw['content'];transcript_error=None;transcript_proof=None
        if content.get('contentType') in ('contributed_audio','contributed_video'):
            try:
                transcript,transcript_proof=document_api(adapter,page,'/content-service/media-transcript/v2/'+uuid)
                url=transcript.get('transcript')
                if url:
                    parts=urlsplit(url);media_ids=content.get('mediaIds',[])
                    if parts.scheme!='https' or not any(value in PurePosixPath(unquote(parts.path)).parts for value in media_ids):
                        raise ServiceError('identity_mismatch','JSTOR transcript URL does not identify a media object of the selected document')
                    rows.append({'url':url,'filename':PurePosixPath(parts.path).name,'label':'Native media transcript',
                        'role':'native_transcript','transcript_type':transcript.get('transcriptType'),'linked_doi':content['doi']})
            except ServiceError as error:transcript_error=error.result
        if not rows:
            return transcript_error or {'status':'not_offered','artifact':proof,'reason':'This native document metadata lists no attachments or available transcript'}
        wrapper=SimpleNamespace(source=adapter.source,store=adapter.store,gateway=adapter.gateway,profile=profile)
        result=fetch_supplementary(wrapper,page,content['doi'],proof,native_rows=rows)
        if transcript_proof:result['transcript_evidence']=transcript_proof
        if transcript_error:result.update(status='partial',transcript_error=transcript_error)
        return result
    except ServiceError:raise
    except Exception as error:raise ServiceError('document_extra_failed','JSTOR document attachments could not be read',error_type=type(error).__name__) from None
    finally:
        if owned:page.close()


def document_file(adapter,identifier,*,page=None):
    from pathlib import Path
    from publishers import Publisher,PROFILES
    from browser_adapters import require_source_url,is_access_challenge
    profile=next(p for p in PROFILES if p.source=='jstor')
    owned=page is None
    if owned:page=document_page(adapter,identifier)
    stage='document_identity'
    try:
        if is_access_challenge(page.content()):raise ServiceError('publisher_access_challenge','JSTOR requires document access verification',status='restricted')
        if stable_id(page.url)!=identifier:raise ServiceError('identity_mismatch','JSTOR opened a different stable document')
        permission_proof=None;permission=None
        if identifier.startswith('community.'):
            stage='download_permission';uuid=document_uuid(page)
            raw,permission_proof=document_api(adapter,page,'/content-service/content-data/download-param/api',{'contentIds':[uuid]})
            permission=download_permission(raw,identifier,uuid)
            if permission['access']=='restricted':raise ServiceError('access_restricted','JSTOR does not permit downloading this item in the current access scope',status='restricted',evidence=permission_proof)
            if permission['access']=='disabled':return {'status':'not_offered','reason':'JSTOR has disabled native download for this item','evidence':permission_proof}
        audio_requests={}
        if permission and permission.get('contentType')=='audio':
            def observe(request):
                current=request
                for _ in range(6):
                    if current is None:break
                    parsed=urlsplit(current.url)
                    if parsed.hostname in profile.hosts and parsed.path=='/audio/download/'+uuid:
                        audio_requests[request.url]='https://'+parsed.hostname+parsed.path;break
                    current=current.redirected_from
            page.on('request',observe)
        downloads=[];page.on('download',lambda download:downloads.append(download))
        with page.expect_download(timeout=60000) as pending:
            stage='download_control'
            page.get_by_role('button',name='Download',exact=True).first.click(timeout=45000)
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
        audio_endpoint=audio_requests.get(download.url)
        if permission and permission.get('contentType')=='audio':
            if not audio_endpoint:raise ServiceError('identity_mismatch','JSTOR audio download has no redirect from the selected content endpoint')
        elif stable_id(download.url)!=identifier:raise ServiceError('identity_mismatch','JSTOR downloaded another stable document')
        data=Path(download.path()).read_bytes()
        metadata=file_metadata(data);media=metadata.pop('media_type')
        if audio_endpoint and media!='audio/mpeg':raise ServiceError('invalid_document','JSTOR audio download returned no MPEG audio')
        artifact=adapter.store.put(data,media,adapter.source,download.url,preserve_bytes=True,role='fulltext',stable_id=identifier,
            **({'source_endpoint':audio_endpoint,'content_id':uuid} if audio_endpoint else {}),**metadata)
        return {'status':'available','artifact':artifact,'permission_evidence':permission_proof,'scope':'Native downloaded file; PDFs include publisher cover pages and images retain the original download bytes'}
    except ServiceError:raise
    except Exception as error:raise ServiceError('document_download_failed','JSTOR did not complete the native document download',stage=stage,error_type=type(error).__name__) from None
    finally:
        if owned:page.close()


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
        wanted=[part for part in parts if part in ('fulltext','supplementary')]
        if wanted:
            page=None
            try:
                page=document_page(self,identifier)
                for part in wanted:
                    try:components[part]=(document_file if part=='fulltext' else supplementary)(self,identifier,page=page)
                    except ServiceError as error:components[part]=error.result
            except ServiceError as error:
                for part in wanted:components.setdefault(part,error.result)
            except Exception as error:
                for part in wanted:components.setdefault(part,{'status':'error','code':'document_open_failed','error_type':type(error).__name__})
            finally:
                if page is not None:page.close()
        return {'status':'ok' if all(v['status']=='available' for v in components.values()) else 'partial','source':self.source,'target':target,
                'records':record,'components':components,'stable_id':identifier}

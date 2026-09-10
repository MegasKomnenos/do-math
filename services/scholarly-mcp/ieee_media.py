"""Document-bound IEEE graphical abstracts; scripts and research code are not evaluated."""
import json,re
from pathlib import PurePosixPath
from urllib.parse import urljoin,urlsplit
from bs4 import BeautifulSoup
from browser_adapters import browser_download,goto_source
from scholarly import ServiceError,encoded


def range_validator(headers):
    from email.utils import parsedate_to_datetime
    tag=headers.get('etag')
    if tag and re.fullmatch(r'"[^"\r\n]*"',tag): return 'etag',tag
    if not tag:
        modified,date=headers.get('last-modified'),headers.get('date')
        try:
            # RFC 9110 permits a separated Date/Last-Modified pair; use a conservative minute.
            if (parsedate_to_datetime(date)-parsedate_to_datetime(modified)).total_seconds()>=60:
                return 'last-modified',modified
        except (TypeError,ValueError,AttributeError): pass
    raise ServiceError('range_validator_missing','A strong validator is required to join file ranges')


def range_download(context,url,hosts,*,chunk_size=4*1024*1024):
    chunks=[]; offset=0; total=None; validator=None; first_url=None
    while total is None or offset<total:
        end=offset+chunk_size-1 if total is None else min(total-1,offset+chunk_size-1)
        headers={'Range':f'bytes={offset}-{end}','Accept-Encoding':'identity'}
        if validator: headers['If-Range']=validator[1]
        info={}
        data,media,obtained=browser_download(context,url,hosts,headers=headers,response_info=info)
        if info.get('status')==200 and offset==0:
            return data,media,obtained,{'ranges':1,'range_supported':False}
        if info.get('status')!=206 or info.get('content-encoding','identity')!='identity':
            raise ServiceError('range_response_mismatch','Source did not return the requested unchanged byte range')
        match=re.fullmatch(r'bytes (\d+)-(\d+)/(\d+)',info.get('content-range',''))
        if not match:
            raise ServiceError('range_response_mismatch','Source returned no complete Content-Range')
        first,last,size=map(int,match.groups())
        if first!=offset or not first<=last<=end or len(data)!=last-first+1 or size<=last or (total is not None and size!=total):
            raise ServiceError('range_response_mismatch','Source byte positions, length or total changed')
        if validator is None:
            validator=range_validator(info); first_url=obtained
        elif info.get(validator[0])!=validator[1] or obtained!=first_url:
            raise ServiceError('range_version_changed','Source file validator or URL changed during range retrieval')
        total=size;chunks.append(data);offset=last+1;url=obtained
    return b''.join(chunks),media,url,{'ranges':len(chunks),'range_supported':True,'total_bytes':total,
                                    'validator_kind':validator[0],'validator':validator[1]}


def document_metadata(raw,identifier):
    values=[]
    for script in BeautifulSoup(raw,'html.parser').find_all('script'):
        text=script.get_text(); match=re.search(r'xplGlobal\.document\.metadata\s*=\s*',text)
        if match:
            try: value,_=json.JSONDecoder().raw_decode(text[match.end():])
            except ValueError: raise ServiceError('invalid_response','IEEE document metadata was not JSON') from None
            values.append(value)
    if len(values)!=1 or not isinstance(values[0],dict):
        raise ServiceError('invalid_response','IEEE did not provide one document metadata object')
    row=values[0]
    if str(row.get('articleNumber'))!=identifier:
        raise ServiceError('identity_mismatch','IEEE media metadata belongs to a different document')
    return {k:row[k] for k in ('articleNumber','title','doi','publicationNumber','sections','graphicalAbstract') if k in row}


def download_media(adapter,row,base,proof):
    graphical=row.get('graphicalAbstract') or {}
    if not isinstance(graphical,dict) or not isinstance(row.get('sections'),dict):
        raise ServiceError('invalid_response','IEEE media description has an unexpected structure')
    files=[]
    for key,role in [('coverImage','graphical_abstract_cover'),('file','graphical_abstract')]:
        if not graphical.get(key): continue
        url=urljoin(base,graphical[key]); parts=urlsplit(url)
        item={'role':role,'url':url,'filename':PurePosixPath(parts.path).name,'description':graphical.get('summary'),
              'source_type':graphical.get('type'),'display_file_size':graphical.get('fileSize') if key=='file' else None}
        try:
            if parts.hostname not in adapter.hosts or not re.fullmatch(r'/ielx\d+/\d+/\d+/'+re.escape(str(row['articleNumber']))+r'/graphical_abstract/[^/]+',parts.path):
                raise ServiceError('source_boundary','Graphical abstract file is not bound to this IEEE document')
            suffix=PurePosixPath(parts.path).suffix.lower(); details={}
            if suffix=='.mp4':
                data,media,obtained,details=range_download(adapter.gateway.context,url,adapter.hosts)
            else:
                data,media,obtained=browser_download(adapter.gateway.context,url,adapter.hosts)
            if media.startswith('text/html') or data.lstrip().lower().startswith((b'<html',b'<!doctype html')):
                raise ServiceError('unexpected_content','IEEE graphical abstract returned HTML')
            if suffix=='.mp4':
                if data[4:8]!=b'ftyp': raise ServiceError('invalid_document','IEEE video response is not an MP4 container')
                media='video/mp4'
            elif suffix in ('.jpg','.jpeg'):
                if not data.startswith(b'\xff\xd8\xff'): raise ServiceError('invalid_document','IEEE cover response is not JPEG')
                media='image/jpeg'
            artifact=adapter.store.put(data,media,adapter.source,obtained,preserve_bytes=True,role=role,
                article_number=str(row['articleNumber']),filename=item['filename'],metadata_ref=proof['ref'],**details)
            files.append({**item,'status':'available','artifact':artifact})
        except ServiceError as exc: files.append({**item,**exc.result})
        except Exception as exc: files.append({**item,'status':'error','code':'media_retrieval_failed','error_type':type(exc).__name__})
    flag=row['sections'].get('multimedia')
    remaining=flag not in (False,'false')
    status=('partial' if remaining or any(f['status']!='available' for f in files) else 'available') if files else 'not_implemented' if remaining else 'not_found'
    return {'status':status,'files':files,'received':sum(f['status']=='available' for f in files),'metadata':proof,
        'multimedia':{'status':'not_implemented' if remaining else 'not_found',
            'reason':'Separate Media-tab files require their native controls' if remaining else 'This record marks its multimedia section false'},
        'scope':'Graphical abstract media and cover; no video analysis or code execution'}


def fetch_media(adapter,identifier,base):
    page=adapter.page()
    if not re.match(r'/document/'+re.escape(identifier)+r'(?:/|$)',urlsplit(page.url).path):
        goto_source(page,urljoin(base,'/document/'+identifier+'/'),adapter.hosts,wait_until='domcontentloaded',timeout=45000)
    page.locator('h1.document-title').wait_for(timeout=30000)
    row=document_metadata(page.content(),identifier)
    proof=adapter.store.put(encoded(row),'application/json',adapter.source,page.url,role='document_media_metadata',article_number=identifier)
    return download_media(adapter,row,page.url,proof)

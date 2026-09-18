"""Document-bound IEEE graphical abstracts; scripts and research code are not evaluated."""
import json,re
from pathlib import PurePosixPath
from urllib.parse import urljoin,urlsplit
from bs4 import BeautifulSoup
from browser_adapters import browser_download,goto_source,clean_html
from scholarly import ServiceError, encoded, failure_details
from waits import SOURCE_WAIT_MS


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


def media_links(raw,base,identifier):
    rows=[];seen=set()
    for item in BeautifulSoup(raw,'html.parser').select('.media-tab .media-item'):
        description=item.select_one('.description')
        for anchor in item.select('a[href]'):
            url=urljoin(base,anchor['href']);path=urlsplit(url).path
            if not path.startswith('/ielx'):
                continue
            if not re.fullmatch(r'/ielx\d+/\d+/\d+/0*'+re.escape(identifier)+r'/[^/]+',path):
                raise ServiceError('source_boundary','Media-tab file is not bound to this IEEE document')
            if url in seen:continue
            seen.add(url)
            rows.append({'role':'supplementary_media','url':url,'filename':PurePosixPath(path).name,
                'description':description.get_text(' ',strip=True) if description else None})
    return rows


def download_media(adapter,row,base,proof,*,native_files=None):
    graphical=row.get('graphicalAbstract') or {}
    if not isinstance(graphical,dict) or not isinstance(row.get('sections'),dict):
        raise ServiceError('invalid_response','IEEE media description has an unexpected structure')
    files=[];requests=[]
    for key,role in [('coverImage','graphical_abstract_cover'),('file','graphical_abstract')]:
        if not graphical.get(key): continue
        url=urljoin(base,graphical[key]); parts=urlsplit(url)
        item={'role':role,'url':url,'filename':PurePosixPath(parts.path).name,'description':graphical.get('summary'),
              'source_type':graphical.get('type'),'display_file_size':graphical.get('fileSize') if key=='file' else None}
        requests.append(item)
    requests.extend(native_files or [])
    for item in requests:
        url=item['url'];parts=urlsplit(url);role=item['role']
        try:
            subpath='' if role=='supplementary_media' else 'graphical_abstract/'
            if parts.hostname not in adapter.hosts or not re.fullmatch(r'/ielx\d+/\d+/\d+/0*'+re.escape(str(row['articleNumber']))+'/'+subpath+r'[^/]+',parts.path):
                raise ServiceError('source_boundary','Media file is not bound to this IEEE document')
            suffix=PurePosixPath(parts.path).suffix.lower(); details={}
            if suffix=='.mp4':
                data,media,obtained,details=range_download(adapter.gateway.context,url,adapter.hosts)
            else:
                data,media,obtained=browser_download(adapter.gateway.context,url,adapter.hosts)
            if media.startswith('text/html') or data.lstrip().lower().startswith((b'<html',b'<!doctype html')):
                raise ServiceError('unexpected_content','IEEE media file returned HTML')
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
        except Exception as exc: files.append({**item,'status':'error','code':'media_retrieval_failed',**failure_details(exc)})
    flag=row['sections'].get('multimedia')
    remaining=flag not in (False,'false') and native_files is None
    native_received=sum(f['status']=='available' for f in files if f['role']=='supplementary_media')
    status=('partial' if remaining or any(f['status']!='available' for f in files) else 'available') if files else 'not_implemented' if remaining else 'not_found'
    return {'status':status,'files':files,'received':sum(f['status']=='available' for f in files),'metadata':proof,
        'multimedia':{'status':('available' if native_received==len(native_files) else 'partial') if native_files is not None else 'not_implemented' if remaining else 'not_found',
            'discovered':len(native_files) if native_files is not None else None,'received':native_received,
            'reason':'Native Media-tab controls' if native_files is not None else 'Separate Media-tab files require their native controls' if remaining else 'This record marks its multimedia section false'},
        'scope':'Document-bound graphical abstract media, cover and Media-tab files; no video analysis or code execution'}


def fetch_media(adapter,identifier,base):
    page=adapter.page()
    if not re.match(r'/document/'+re.escape(identifier)+r'(?:/|$)',urlsplit(page.url).path):
        goto_source(page,urljoin(base,'/document/'+identifier+'/'),adapter.hosts,wait_until='domcontentloaded',timeout=SOURCE_WAIT_MS)
    page.locator('h1.document-title').wait_for(timeout=SOURCE_WAIT_MS)
    row=document_metadata(page.content(),identifier)
    proof=adapter.store.put(encoded(row),'application/json',adapter.source,page.url,role='document_media_metadata',article_number=identifier)
    native_files=native_error=native_index=None
    if row.get('sections',{}).get('multimedia') in (True,'true'):
        try:
            goto_source(page,urljoin(page.url,'/document/'+identifier+'/media#media'),adapter.hosts,wait_until='domcontentloaded',timeout=SOURCE_WAIT_MS)
            page.locator('.media-tab .media-item').first.wait_for(state='attached',timeout=SOURCE_WAIT_MS)
            document_metadata(page.content(),identifier)
            native_files=media_links(page.content(),page.url,identifier)
            if not native_files:
                raise ServiceError('media_controls_not_found','The enabled IEEE Media tab provided no recognized document files')
            source_page=adapter.store.put(clean_html(page.content(),adapter.store.sanitizer),'text/html',adapter.source,page.url,role='media_tab_source_page',metadata_ref=proof['ref'])
            native_index=adapter.store.put(encoded(native_files),'application/json',adapter.source,page.url,role='native_media_index',parent_ref=source_page['ref'])
        except ServiceError as error:native_error=error.result
        except Exception as error:native_error={'status':'error','code':'media_tab_not_ready',**failure_details(error)}
    result=download_media(adapter,row,page.url,proof,native_files=native_files)
    if native_index:result['native_index']=native_index
    if native_error:result.update(status='partial',multimedia=native_error)
    return result

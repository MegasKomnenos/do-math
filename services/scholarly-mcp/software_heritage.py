"""Software Heritage object identity and explicit content fragments."""
import hashlib,re
from urllib.parse import quote,unquote,unquote_to_bytes,urlsplit
from scholarly import ServiceError

BASE='https://archive.softwareheritage.org/api/1/'
CORE=re.compile(r'swh:1:(cnt|dir|rev|rel|snp):([0-9a-f]{40})')


def parse_swhid(value):
    base,*suffixes=value.split(';');base=base.lower()
    match=CORE.fullmatch(base)
    if not match:raise ServiceError('invalid_target','Use a version-1 SWHID with a 40-digit hexadecimal object ID')
    qualifiers={}
    for suffix in suffixes:
        name,separator,encoded=suffix.partition('=')
        if not separator or name not in ('origin','visit','anchor','path','lines') or name in qualifiers or not encoded:
            raise ServiceError('invalid_target','SWHID qualifiers must be recognized, nonempty and unique')
        if re.search(r'%(?![0-9A-Fa-f]{2})',encoded):
            raise ServiceError('invalid_target','Malformed percent escape in an SWHID qualifier')
        try:decoded=unquote(encoded,errors='strict') if name!='path' else encoded
        except UnicodeDecodeError:raise ServiceError('invalid_target','Invalid qualifier encoding') from None
        if name=='origin' and not urlsplit(decoded).scheme:
            raise ServiceError('invalid_target','The origin qualifier must be a URI')
        if name in ('visit','anchor'):
            decoded=decoded.lower();reference=CORE.fullmatch(decoded)
            if not reference or reference[1] not in (('snp',) if name=='visit' else ('dir','rev','rel','snp')):
                raise ServiceError('invalid_target','Invalid visit or anchor SWHID')
        if name=='path' and not unquote_to_bytes(encoded).startswith(b'/'):
            raise ServiceError('invalid_target','The path qualifier must be absolute within its anchor')
        if name=='lines':
            selected=re.fullmatch(r'([0-9]+)(?:-([0-9]+))?',decoded)
            if not selected or int(selected[1])<1 or int(selected[2] or selected[1])<int(selected[1]):
                raise ServiceError('invalid_target','Line numbers must be positive and ordered')
        qualifiers[name]=decoded
    return base,match[1],match[2],qualifiers


def check_content_metadata(raw,core,key,evidence):
    if not isinstance(raw,dict) or not isinstance(raw.get('checksums'),dict) or type(raw.get('length')) is not int or raw['length']<0:
        raise ServiceError('invalid_response','Software Heritage returned no content identity and length',evidence=evidence)
    if any(not isinstance(value,str) for name,value in raw['checksums'].items() if name in ('sha1_git','sha1','sha256','blake2s256')) or not isinstance(raw.get('swhid',core),str):
        raise ServiceError('invalid_response','Content hashes and SWHID must be strings',evidence=evidence)
    if raw['checksums'].get('sha1_git','').lower()!=key or raw.get('swhid',core).lower()!=core:
        raise ServiceError('identity_mismatch','Content metadata identifies another SWH object',evidence=evidence)


def content(adapter,url,raw,core,key,qualifiers,metadata):
    data,response=adapter.request(url+'raw/',accept='binary')
    digests={'sha1_git':hashlib.sha1(b'blob '+str(len(data)).encode('ascii')+b'\0'+data).hexdigest(),
        'sha1':hashlib.sha1(data).hexdigest(),'sha256':hashlib.sha256(data).hexdigest(),'blake2s256':hashlib.blake2s(data).hexdigest()}
    if len(data)!=raw['length'] or digests['sha1_git']!=key or any(raw['checksums'][name].lower()!=digest for name,digest in digests.items() if name in raw['checksums']):
        raise ServiceError('content_integrity_mismatch','Content bytes differ from their SWHID or recorded checksums',evidence=response)
    integrity={'verified':True,'scope':'complete_content','algorithm':'sha1_git','digest':key,'length':len(data),'metadata_checksums':sorted(set(digests)&set(raw['checksums']))}
    is_text=b'\0' not in data
    try:data.decode('utf-8')
    except UnicodeDecodeError:is_text=False
    media='text/plain' if response['media_type']=='application/octet-stream' and is_text else response['media_type']
    complete=adapter.store.put(data,media,adapter.source,response['url'],preserve_bytes=True,
        role='archived_content',swhid=core,integrity=integrity,metadata_ref=metadata['ref'],source_media_type=response['media_type'])
    result={'status':'available','artifact':complete,'integrity':integrity}
    if 'lines' in qualifiers:
        first,*rest=qualifiers['lines'].split('-');first=int(first);last=int(rest[0]) if rest else first
        selection={'unit':'lines','first_line':first,'last_line':last}
        result.update(complete_content=complete,selection=selection)
        if not is_text:
            result.update(status='unsupported',code='unsupported_text_encoding',reason='Line fragments currently require UTF-8 text without NUL bytes')
            result.pop('artifact')
            return result
        lines=data.splitlines(keepends=True);selection['total_lines']=len(lines)
        if last>len(lines):
            result.update(status='not_found',code='selection_out_of_range',reason='The requested line interval exceeds the archived content')
            result.pop('artifact')
            return result
        fragment=b''.join(lines[first-1:last])
        selected=adapter.store.put(fragment,'text/plain',adapter.source,response['url'],preserve_bytes=True,role='content_fragment',
            parent_ref=complete['ref'],parent_swhid=core,first_line=first,last_line=last)
        result['artifact']=selected
    return result


def fetch(adapter,target,parts):
    if set(parts)-{'metadata','abstract','fulltext','supplementary','export'}:
        raise ServiceError('invalid_parts','Use the documented content parts')
    value=target;qualifiers={};core=key=None
    if value.startswith(('https://','http://')):
        parsed=urlsplit(value)
        if parsed.hostname in ('archive.softwareheritage.org','n2t.net') and parsed.path.startswith('/swh:'):
            if parsed.query or parsed.fragment:
                raise ServiceError('invalid_target','Use percent-escaped SWHID qualifiers instead of URL query or fragment parameters')
            value=parsed.path[1:]
    if value.lower().startswith('swh:'):
        core,kind,key,qualifiers=parse_swhid(value)
        endpoint={'cnt':'content/sha1_git:','dir':'directory/','rev':'revision/','rel':'release/','snp':'snapshot/'}[kind]
        url=BASE+endpoint+key+'/'
    elif value.startswith(('https://','http://')):
        kind='origin';url=BASE+'origin/'+quote(value,safe='')+'/get/'
    else:raise ServiceError('invalid_target','Use an SWHID, its resolver URL or an origin URL')
    raw,evidence=adapter.request(url)
    if kind=='cnt':check_content_metadata(raw,core,key,evidence)
    elif key and isinstance(raw,dict) and raw.get('id') and str(raw['id']).lower()!=key:
        raise ServiceError('identity_mismatch','Software Heritage returned a different object',evidence=evidence)
    result=adapter.fetched(raw if isinstance(raw,list) else [raw],evidence,parts,('metadata','export'))
    safe=dict(qualifiers)
    if 'origin' in safe:safe['origin']=adapter.store.sanitizer.url(safe['origin'])
    result.update(target=core or adapter.store.sanitizer.url(target),qualifiers=safe,
        context_verified=False,scope='Object data from Software Heritage. Qualifier context is retained as supplied and is not followed or verified against external origins.')
    wanted=set(parts)&{'fulltext','supplementary'}
    if kind=='cnt' and wanted:
        try:component=content(adapter,url,raw,core,key,qualifiers,evidence)
        except ServiceError as error:component=error.result
        for part in wanted:result['components'][part]=component
    elif 'lines' in qualifiers and wanted:
        for part in wanted:result['components'][part]={'status':'unsupported','code':'unsupported_fragment','reason':'Line selection is implemented for content objects only'}
    states={part['status'] for part in result['components'].values()}
    result['status']='ok' if not states or states=={'available'} else next(iter(states)) if states in ({'restricted'},{'not_found'},{'unsupported'}) else 'partial'
    return result

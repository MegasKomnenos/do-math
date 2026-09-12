"""Software Heritage object identity and explicit content fragments."""
import hashlib,re,io,tarfile
from pathlib import PurePosixPath
from collections import defaultdict
from urllib.parse import quote,unquote,unquote_to_bytes,urlsplit,urljoin
from scholarly import ServiceError

BASE='https://archive.softwareheritage.org/api/1/'
CORE=re.compile(r'swh:1:(cnt|dir|rev|rel|snp):([0-9a-f]{40})')


def verify_flat_archive(data,directory):
    expected=CORE.fullmatch(directory)
    if not expected or expected[1]!='dir':raise ServiceError('invalid_target','A flat archive needs a directory SWHID')
    children=defaultdict(dict);directories={()};seen=set();files=set();symlinks=0
    def text_bytes(value):return value.encode('utf-8',errors='surrogateescape')
    try:
        with tarfile.open(fileobj=io.BytesIO(data),mode='r|*') as archive:
            for member in archive:
                path=PurePosixPath(member.name)
                if path.is_absolute() or '..' in path.parts or not path.parts or path.parts[0]!=directory:
                    raise ServiceError('archive_path_mismatch','Archive entries do not belong to the selected directory root')
                relative=path.parts[1:]
                if relative in seen:raise ServiceError('archive_path_mismatch','Archive contains duplicate paths')
                seen.add(relative)
                for index in range(len(relative)):directories.add(relative[:index])
                if member.isdir():directories.add(relative);continue
                if not relative:raise ServiceError('archive_path_mismatch','Archive root is not a directory')
                if member.isfile():
                    digest=hashlib.sha1(b'blob '+str(member.size).encode()+b'\0');received=0
                    stream=archive.extractfile(member)
                    while chunk:=stream.read(1024*1024):digest.update(chunk);received+=len(chunk)
                    if received!=member.size:raise ServiceError('invalid_archive','Truncated archive member')
                    mode=0o100755 if member.mode&0o111 else 0o100644
                    digest=digest.hexdigest()
                elif member.issym():
                    link=text_bytes(member.linkname);digest=hashlib.sha1(b'blob '+str(len(link)).encode()+b'\0'+link).hexdigest()
                    mode=0o120000;symlinks+=1
                else:raise ServiceError('archive_entry_not_supported','Archive tree verification supports regular files, directories and symbolic links',status='unsupported')
                files.add(relative);children[relative[:-1]][text_bytes(relative[-1])]=(mode,digest)
    except ServiceError:raise
    except Exception:raise ServiceError('invalid_archive','The returned archive cannot be read as a complete tar stream') from None
    if files&directories:raise ServiceError('archive_path_mismatch','Archive uses a path as both file and directory')
    computed=None
    for directory_path in sorted(directories,key=len,reverse=True):
        entries=children[directory_path]
        ordered=sorted(entries,key=lambda name:name+(b'/' if entries[name][0]==0o40000 else b''))
        body=b''.join(f'{entries[name][0]:o}'.encode()+b' '+name+b'\0'+bytes.fromhex(entries[name][1]) for name in ordered)
        digest=hashlib.sha1(b'tree '+str(len(body)).encode()+b'\0'+body).hexdigest()
        if directory_path:children[directory_path[:-1]][text_bytes(directory_path[-1])]=(0o40000,digest)
        else:computed=digest
    if computed!=expected[2]:raise ServiceError('archive_tree_mismatch','Archive file contents, names or modes differ from the requested directory SWHID',computed_directory_id=computed)
    return {'verified':True,'algorithm':'git_tree_sha1','scope':'directory_tree','digest':computed,'files':len(files)-symlinks,'symlinks':symlinks,'directories':len(directories)}


def vault_archive(adapter,directory):
    match=CORE.fullmatch(directory)
    if not match or match[1]!='dir':raise ServiceError('invalid_response','The selected object has no valid directory identifier')
    url=BASE+'vault/flat/'+directory+'/'
    try:job,evidence=adapter.request(url)
    except ServiceError as error:
        if error.result['code']!='not_found_at_source':raise
        job,evidence=adapter.request(url,json_body={})
    if not isinstance(job,dict) or job.get('swhid')!=directory or job.get('status') not in ('new','pending','done','failed'):
        raise ServiceError('archive_identity_mismatch','Vault response does not identify the selected directory task',evidence=evidence)
    if job['status'] in ('new','pending'):
        return {'status':'pending','job':evidence,'retry_after_seconds':60,'retry_basis':'client_poll_interval_for_anonymous_api_budget',
            'retry':{'source':adapter.source,'target':directory,'parts':['fulltext']}}
    if job['status']=='failed':return {'status':'error','code':'archive_preparation_failed','job':evidence}
    if not isinstance(job.get('fetch_url'),str):raise ServiceError('invalid_response','Vault returned no archive URL',evidence=evidence)
    target=urljoin(url,job['fetch_url']);parts=urlsplit(target)
    if parts.scheme!='https' or parts.hostname!='archive.softwareheritage.org' or parts.username or parts.password or parts.port not in (None,443) or parts.query or parts.fragment or unquote(parts.path).rstrip('/')!='/api/1/vault/flat/'+directory+'/raw':
        raise ServiceError('archive_identity_mismatch','Vault download URL differs from the requested directory',evidence=evidence)
    data,response=adapter.request(target,accept='binary')
    media='application/gzip' if data.startswith(b'\x1f\x8b') else 'application/x-tar'
    try:integrity=verify_flat_archive(data,directory)
    except ServiceError as error:
        source=adapter.store.put(data,media,adapter.source,response['url'],preserve_bytes=True,role='unverified_vault_archive',requested_directory=directory,job_ref=evidence['ref'])
        return {**error.result,'source_archive':source,'job':evidence}
    artifact=adapter.store.put(data,media,adapter.source,response['url'],preserve_bytes=True,role='vault_archive',directory_swhid=directory,integrity=integrity,job_ref=evidence['ref'],source_media_type=response['media_type'])
    return {'status':'available','artifact':artifact,'directory_swhid':directory,'integrity':integrity,'job':evidence}


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


def release_content(adapter,core,raw,evidence,*,directory_loader=None):
    requested=core;seen=set();proofs=[];chain=[]
    # ponytail: bound malformed or pathological release chains; return an explicit limit error.
    for _ in range(32):
        if core in seen:raise ServiceError('release_cycle','Release targets contain a cycle',evidence=proofs)
        seen.add(core);proofs.append(evidence)
        if not isinstance(raw,dict) or raw.get('id')!=core.rsplit(':',1)[-1]:
            raise ServiceError('identity_mismatch','Release target metadata identifies a different object',evidence=proofs)
        kind=raw.get('target_type');key=raw.get('target')
        types={'release':'rel','revision':'rev','directory':'dir','content':'cnt'}
        if kind not in types or not isinstance(key,str) or not re.fullmatch('[0-9a-f]{40}',key):
            raise ServiceError('invalid_response','Release has no recognized target type and object ID',evidence=proofs)
        target='swh:1:'+types[kind]+':'+key;chain.append({'release_swhid':core,'target_swhid':target})
        if kind=='directory':break
        url=BASE+('content/sha1_git:' if kind=='content' else kind+'/')+key+'/'
        raw,evidence=adapter.request(url)
        if kind!='release':
            proofs.append(evidence)
            if kind=='content':
                check_content_metadata(raw,target,key,evidence)
                component=content(adapter,url,raw,target,key,{},evidence)
                return component,{'requested_swhid':requested,'content_swhid':target,'basis':'release_target_chain','chain':chain,'evidence':proofs}
            if not isinstance(raw,dict) or raw.get('id')!=key or not isinstance(raw.get('directory'),str) or not re.fullmatch('[0-9a-f]{40}',raw['directory']):
                raise ServiceError('identity_mismatch','Release revision has no matching identity and directory',evidence=proofs)
            target='swh:1:dir:'+raw['directory'];break
        core=target
    else:raise ServiceError('release_depth_limit','Release target chain exceeds 32 entries',evidence=proofs)
    return (directory_loader or vault_archive)(adapter,target),{'requested_swhid':requested,'directory_swhid':target,'basis':'release_target_chain','chain':chain,'evidence':proofs}


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
    if set(parts)-{'metadata','abstract','fulltext','supplementary','export','history','files'}:
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
    if kind=='dir' and 'files' in parts:
        from swh_directory import load_directory
        raw,evidence=load_directory(adapter,key)
    else:raw,evidence=adapter.request(url)
    if kind=='cnt':check_content_metadata(raw,core,key,evidence)
    elif key and isinstance(raw,dict) and raw.get('id') and str(raw['id']).lower()!=key:
        raise ServiceError('identity_mismatch','Software Heritage returned a different object',evidence=evidence)
    result=adapter.fetched(raw if isinstance(raw,list) else [raw],evidence,[p for p in parts if p not in ('history','files')],('metadata','export'))
    safe=dict(qualifiers)
    if 'origin' in safe:safe['origin']=adapter.store.sanitizer.url(safe['origin'])
    result.update(target=core or adapter.store.sanitizer.url(target),qualifiers=safe,
        context_verified=False,scope='Object data from Software Heritage. Qualifier context is retained as supplied and is not followed or verified against external origins.')
    if 'files' in parts:
        from swh_directory import directory_files
        try:
            if 'lines' in qualifiers and kind!='cnt':
                component={'status':'unsupported','code':'unsupported_fragment','reason':'Line fragments select content objects, not directory trees'}
            elif kind=='cnt':component=content(adapter,url,raw,core,key,qualifiers,evidence)
            elif kind=='dir':component=directory_files(adapter,core,initial=raw,evidence=evidence)
            elif kind=='rev':component=directory_files(adapter,'swh:1:dir:'+str(raw.get('directory','')))
            elif kind=='rel':
                component,selection=release_content(adapter,core,raw,evidence,directory_loader=directory_files)
                result['file_selection']=selection
            else:component={'status':'selection_required','reason':'Select a content, directory, revision or release object for a file/tree view; snapshot branches and origins do not define one working tree'}
        except ServiceError as error:component=error.result
        result['components']['files']=component
    wanted=set(parts)&{'fulltext','supplementary'}
    if kind=='cnt' and wanted:
        try:component=result['components'].get('files') or content(adapter,url,raw,core,key,qualifiers,evidence)
        except ServiceError as error:component=error.result
        for part in wanted:result['components'][part]=component
    elif 'lines' in qualifiers and wanted:
        for part in wanted:result['components'][part]={'status':'unsupported','code':'unsupported_fragment','reason':'Line selection is implemented for content objects only'}
    elif kind in ('dir','rev') and wanted:
        directory=core if kind=='dir' else 'swh:1:dir:'+str(raw.get('directory',''))
        try:component=vault_archive(adapter,directory)
        except ServiceError as error:component=error.result
        for part in wanted:result['components'][part]=component
        result['archive_selection']={'requested_swhid':core,'directory_swhid':directory,'basis':'selected_directory' if kind=='dir' else 'revision_directory_field'}
    elif kind=='rel' and wanted:
        try:
            component,selection=release_content(adapter,core,raw,evidence)
            result['archive_selection']=selection
        except ServiceError as error:component=error.result
        for part in wanted:result['components'][part]=component
    elif kind=='snp' and wanted:
        from swh_git import git_archive
        try:component=git_archive(adapter,core,raw,evidence)
        except ServiceError as error:component=error.result
        for part in wanted:result['components'][part]=component
    if 'history' in parts:
        if kind not in ('dir','rev','rel','snp') or 'lines' in qualifiers:
            component={'status':'unsupported','reason':'Git history requires a directory, revision, release or snapshot without line selection'}
        elif kind=='snp' and wanted and 'lines' not in qualifiers:component=result['components'][next(iter(wanted))]
        else:
            from swh_git import git_archive
            try:component=git_archive(adapter,core,raw,evidence)
            except ServiceError as error:component=error.result
        result['components']['history']=component
    states={part['status'] for part in result['components'].values()}
    result['status']='ok' if not states or states=={'available'} else next(iter(states)) if states in ({'restricted'},{'not_found'},{'unsupported'}) else 'partial'
    return result

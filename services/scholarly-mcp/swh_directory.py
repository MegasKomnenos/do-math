"""Verified directory/file objects through the API, independent of Vault jobs."""
import hashlib,json,re
from urllib.parse import urlsplit
from scholarly import ServiceError,encoded
from software_heritage import BASE,CORE,check_content_metadata,content


def path_fields(path):
    try:
        path.encode('utf-8')
        return {'path':path}
    except UnicodeEncodeError:
        original=path.encode('utf-8',errors='surrogateescape')
        return {'path':path.encode('utf-8',errors='backslashreplace').decode('utf-8'),
            'path_bytes_hex':original.hex(),'path_display':'escaped_non_utf8_bytes'}


def canonical_uri(url,path):
    try:
        parsed=urlsplit(str(url))
        return parsed.scheme=='https' and parsed.hostname=='archive.softwareheritage.org' and not parsed.username and not parsed.password \
            and parsed.port in (None,443) and parsed.path==path and not parsed.query and not parsed.fragment
    except ValueError:return False


def object_refs(adapter):
    cached=getattr(adapter,'_swh_file_objects',None)
    if cached is not None:return cached
    cached={'dir':{},'cnt':{}}
    for path in (adapter.store.root/'manifests').rglob('*'):
        if not path.is_file() or not re.fullmatch('[0-9a-f]{64}',path.name):continue
        try:
            meta=json.loads(path.read_bytes())
            if meta.get('source')!=adapter.source:continue
            ref='scholarly://artifact/'+path.name
            core=CORE.fullmatch(str(meta.get('swhid','')))
            if meta.get('role')=='archived_content' and core and core[1]=='cnt' and meta.get('integrity',{}).get('verified') \
                    and canonical_uri(meta.get('url'),'/api/1/content/sha1_git:'+core[2]+'/raw/'):
                cached['cnt'][core[2]]=ref
            url=urlsplit(str(meta.get('url','')))
            match=re.fullmatch('/api/1/directory/([0-9a-f]{40})/',url.path)
            if match and canonical_uri(meta.get('url'),match[0]) and meta.get('media_type')=='application/json' \
                    and meta.get('role') in ('provider_response','directory_api_evidence','verified_directory_entries'):
                cached['dir'][match[1]]=ref
        except (ValueError,UnicodeError,OSError):continue
    adapter._swh_file_objects=cached
    return cached


def load_directory(adapter,key):
    refs=object_refs(adapter);ref=refs['dir'].get(key)
    if ref:
        try:
            meta,data=adapter.store.read(ref);entries=json.loads(data);proof={'ref':ref,**meta,'cache_reused':True}
            directory_identity(entries,key,proof)
            return entries,proof
        except (ServiceError,ValueError,UnicodeError):
            refs['dir'].pop(key,None)
    entries,proof=adapter.request(BASE+'directory/'+key+'/')
    directory_identity(entries,key,proof);refs['dir'][key]=proof['ref']
    return entries,proof


def cached_content(adapter,key,entry):
    ref=object_refs(adapter)['cnt'].get(key)
    if not ref:return None
    meta,data=adapter.store.read(ref)
    digests={'sha1_git':hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest(),
        'sha1':hashlib.sha1(data).hexdigest(),'sha256':hashlib.sha256(data).hexdigest(),'blake2s256':hashlib.blake2s(data).hexdigest()}
    if meta.get('source')!=adapter.source or meta.get('swhid')!='swh:1:cnt:'+key or digests['sha1_git']!=key \
            or not canonical_uri(meta.get('url'),'/api/1/content/sha1_git:'+key+'/raw/'):
        raise ServiceError('content_integrity_mismatch','Cached content does not match the requested SWHID',artifact=ref)
    if len(data)!=entry['length'] or any(entry['checksums'][name].lower()!=digest for name,digest in digests.items() if name in entry['checksums']):
        raise ServiceError('content_integrity_mismatch','Cached content differs from the directory entry checksums',artifact=ref)
    return {'status':'available','artifact':{'ref':ref,**meta},'integrity':meta['integrity'],'retrieval':'verified_local_object'}


def directory_identity(entries,identifier,evidence):
    if not isinstance(entries,list):raise ServiceError('invalid_response','SWH directory entries must be an array',evidence=evidence)
    names=set()
    for row in entries:
        if not isinstance(row,dict) or row.get('type') not in ('dir','file','rev') or type(row.get('perms')) is not int or row['perms']<0 \
                or not isinstance(row.get('name'),str) or row['name'] in ('','.','..') or '/' in row['name'] or '\0' in row['name'] \
                or not isinstance(row.get('target'),str) or not re.fullmatch('[0-9a-f]{40}',row['target']):
            raise ServiceError('invalid_response','SWH directory contains an invalid entry',evidence=evidence)
        name=row['name'].encode('utf-8',errors='surrogateescape')
        if name in names:raise ServiceError('invalid_response','SWH directory repeats a filename',evidence=evidence)
        names.add(name)
    ordered=sorted(entries,key=lambda row:row['name'].encode('utf-8',errors='surrogateescape')+(b'/' if row['type']=='dir' else b''))
    body=b''.join(format(row['perms'],'o').encode()+b' '+row['name'].encode('utf-8',errors='surrogateescape')+b'\0'+bytes.fromhex(row['target']) for row in ordered)
    digest=hashlib.sha1(b'tree '+str(len(body)).encode()+b'\0'+body).hexdigest()
    if digest!=identifier:raise ServiceError('directory_integrity_mismatch','SWH names, modes and targets do not match the requested directory',evidence=evidence)


def directory_files(adapter,directory,*,initial=None,evidence=None):
    match=CORE.fullmatch(directory)
    if not match or match[1]!='dir':raise ServiceError('invalid_target','Select a directory SWHID')
    root_key=match[2];queue=[('',root_key,None,frozenset())];directories={};blobs={};rows=[];errors=[];proofs=[]
    if initial is not None:directories[root_key]=(initial,evidence)
    stopped=False;cached_directories=0;cached_files=0
    while queue and not stopped:
        path,key,mode,ancestors=queue.pop()
        if key in ancestors:
            errors.append({'code':'directory_cycle',**path_fields(path)});continue
        try:
            if key not in directories:directories[key]=load_directory(adapter,key)
            entries,proof=directories[key];directory_identity(entries,key,proof)
            cached_directories+=bool(proof.get('cache_reused'))
            if proof['ref'] not in proofs:proofs.append(proof['ref'])
        except ServiceError as error:
            errors.append({**path_fields(path),**error.result});stopped=error.result.get('code')=='rate_limited';continue
        rows.append({**path_fields(path),'kind':'directory','swhid':'swh:1:dir:'+key,'mode':mode,'status':'available','identity_verified':True})
        for entry in entries:
            child=path+'/'+entry['name'] if path else entry['name'];target=entry['target'];kind=entry['type']
            if kind=='dir':queue.append((child,target,entry['perms'],ancestors|{key}));continue
            if kind=='rev':
                rows.append({**path_fields(child),'kind':'revision_reference','swhid':'swh:1:rev:'+target,'mode':entry['perms'],'status':'reference_only'})
                continue
            row={**path_fields(child),'kind':'symlink' if entry['perms']&0o170000==0o120000 else 'file','swhid':'swh:1:cnt:'+target,'mode':entry['perms']}
            try:
                check_content_metadata(entry,row['swhid'],target,proof)
                if target not in blobs:
                    item=cached_content(adapter,target,entry)
                    if item is not None:cached_files+=1
                    else:
                        item=content(adapter,BASE+'content/sha1_git:'+target+'/',entry,row['swhid'],target,{},proof)
                        item['retrieval']='source_api';object_refs(adapter)['cnt'][target]=item['artifact']['ref']
                    blobs[target]=item
                item=blobs[target]
                if item['artifact']['bytes']!=entry['length']:
                    raise ServiceError('content_integrity_mismatch','Repeated SWH content has inconsistent length metadata',evidence=proof)
                row.update(item)
            except ServiceError as error:
                row.update(error.result);errors.append({**path_fields(child),**error.result})
                stopped=error.result.get('code')=='rate_limited'
            rows.append(row)
            if stopped:break
    artifact=adapter.store.put(encoded(rows),'application/json',adapter.source,BASE+'directory/'+root_key+'/',
        role='verified_directory_file_manifest',directory_swhid=directory,evidence_refs=proofs)
    return {'status':'partial' if errors else 'available','artifact':artifact,'directory_swhid':directory,
        'complete':not errors,'directories':sum(r['kind']=='directory' for r in rows),
        'cached_directories':cached_directories,'cached_files':cached_files,
        'files':sum(r['kind']=='file' and r['status']=='available' for r in rows),
        'symlinks':sum(r['kind']=='symlink' and r['status']=='available' for r in rows),
        'revision_references':sum(r['kind']=='revision_reference' for r in rows),'errors':errors,
        'scope':'Verified directory entries and original file blobs. Symlink bytes are retained without following links; revision references are not traversed. This is a manifest, not a Vault archive.'}

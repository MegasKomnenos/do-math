"""Verify Vault git-bare bundles without loading their config or executing code."""
import hashlib,io,os,re,subprocess,tarfile,tempfile
from pathlib import Path,PurePosixPath
from urllib.parse import unquote,urljoin,urlsplit
from scholarly import ServiceError
from software_heritage import BASE,CORE
from waits import LOCAL_TOOL_S


def snapshot_hash(branches):
    if not isinstance(branches,dict):raise ServiceError('snapshot_branches_missing','Complete snapshot branches are required for verification')
    body=[]
    try:
        for name,branch in sorted(branches.items(),key=lambda item:item[0].encode('utf-8')):
            kind=branch['target_type'] if branch is not None else 'dangling'
            if kind not in ('content','directory','revision','release','snapshot','alias','dangling'):raise ValueError()
            target=b'' if branch is None else branch['target'].encode('utf-8') if kind=='alias' else bytes.fromhex(branch['target'])
            if kind not in ('alias','dangling') and len(target)!=20:raise ValueError()
            body.append(kind.encode()+b' '+name.encode('utf-8')+b'\0'+str(len(target)).encode()+b':'+target)
    except (KeyError,ValueError,TypeError,AttributeError,UnicodeError):
        raise ServiceError('invalid_snapshot','Snapshot branches have invalid names, targets or types') from None
    data=b''.join(body)
    return hashlib.sha1(b'snapshot '+str(len(data)).encode()+b'\0'+data).hexdigest()


def complete_snapshot(adapter,core,raw,evidence):
    branches={};proofs=[];marks=set()
    while True:
        if not isinstance(raw,dict) or raw.get('id')!=core.split(':')[-1] or not isinstance(raw.get('branches'),dict):
            raise ServiceError('snapshot_identity_mismatch','Snapshot page does not identify the selected snapshot')
        if branches.keys()&raw['branches'].keys():raise ServiceError('snapshot_page_repeated','Snapshot branch pagination repeated entries')
        branches.update(raw['branches']);proofs.append(evidence)
        mark=raw.get('next_branch')
        if mark is None:break
        if not isinstance(mark,str) or not mark or mark in marks:raise ServiceError('snapshot_page_repeated','Snapshot returned an invalid next branch')
        marks.add(mark);raw,evidence=adapter.request(BASE+'snapshot/'+core.split(':')[-1]+'/',params={'branches_from':mark,'branches_count':1000})
    if snapshot_hash(branches)!=core.split(':')[-1]:raise ServiceError('snapshot_hash_mismatch','Complete branch metadata does not match the requested snapshot SWHID')
    return branches,proofs


def verify_git_archive(data,core,branches=None):
    match=CORE.fullmatch(core)
    if not match or match[1] not in ('dir','rev','rel','snp'):raise ServiceError('invalid_target','Use a directory, revision, release or snapshot SWHID')
    if match[1]=='snp' and snapshot_hash(branches)!=match[2]:raise ServiceError('snapshot_hash_mismatch','Snapshot branch manifest differs from the requested SWHID')
    refs={};packed={};seen=set();packs=[];head=None;warnings=[]
    # Only object bytes enter an isolated repository. Native config, hooks and refs never execute.
    with tempfile.TemporaryDirectory(prefix='scholarly-swh-git-') as temp:
        root=Path(temp);repo=root/'repo';template=root/'empty-template';template.mkdir()
        env={k:v for k,v in os.environ.items() if not k.upper().startswith('GIT_')}
        env.update(GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL=os.devnull,GIT_TERMINAL_PROMPT='0',GIT_NO_REPLACE_OBJECTS='1')
        def git(*args,input=None):
            try:
                result=subprocess.run(['git','--git-dir='+str(repo),*args],input=input,
                    **({'stdin':subprocess.DEVNULL} if input is None else {}),stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                    env=env,cwd=root,timeout=LOCAL_TOOL_S,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
            except FileNotFoundError:raise ServiceError('git_unavailable','Git is required to verify archived Git objects',status='unsupported') from None
            except subprocess.TimeoutExpired:raise ServiceError('git_verification_timeout','Git archive verification exceeded its operation timeout') from None
            operation=next((a for a in args if a in ('init','index-pack','fsck','cat-file')),args[0])
            if result.returncode:raise ServiceError('git_archive_invalid','Git rejected the archived objects or their connectivity',operation=operation,exit_code=result.returncode)
            for warning in re.finditer(rb'warning in (\w+) ([0-9a-f]{40}): ([A-Za-z]+):',result.stderr):
                warnings.append({'object_type':warning[1].decode(),'object_id':warning[2].decode(),'code':warning[3].decode()})
            return result.stdout
        git('init','--bare','--template='+str(template),str(repo))
        try:
            with tarfile.open(fileobj=io.BytesIO(data),mode='r|*') as archive:
                for member in archive:
                    path=PurePosixPath(member.name)
                    if path.is_absolute() or '..' in path.parts or '\\' in member.name or not path.parts or path.parts[0]!=core+'.git' or member.name in seen:
                        raise ServiceError('archive_path_mismatch','Git archive contains a duplicate or unselected root path')
                    seen.add(member.name);name='/'.join(path.parts[1:])
                    if member.isdir():continue
                    if not member.isfile():raise ServiceError('archive_entry_not_supported','Git archive entries must be regular files or directories')
                    if name in ('shallow','info/grafts','objects/info/alternates','objects/info/http-alternates'):
                        raise ServiceError('incomplete_git_archive','Git bundle depends on shallow history or external objects')
                    if name=='HEAD' or name=='packed-refs' or name.startswith('refs/'):
                        raw=archive.extractfile(member).read()
                        try:value=raw.decode('utf-8').strip()
                        except UnicodeError:raise ServiceError('invalid_git_ref','Git reference text is not UTF-8') from None
                        if name=='HEAD':head=value
                        elif name=='packed-refs':
                            for line in value.splitlines():
                                if not line or line.startswith(('#','^')):continue
                                oid,sep,ref=line.partition(' ')
                                if not sep or not ref.startswith('refs/') or ref in packed or not re.fullmatch('[0-9a-f]{40}',oid):raise ServiceError('invalid_git_ref','Malformed packed reference')
                                packed[ref]=oid
                        else:refs[name]=value
                    elif re.fullmatch(r'objects/pack/pack-[0-9a-f]{40}\.pack',name):
                        destination=root/Path(name).name
                        with destination.open('wb') as stream:
                            source=archive.extractfile(member)
                            while chunk:=source.read(1024*1024):stream.write(chunk)
                        packs.append(destination)
                    elif re.fullmatch(r'objects/[0-9a-f]{2}/[0-9a-f]{38}',name):
                        destination=repo.joinpath(*path.parts[1:]);destination.parent.mkdir(parents=True,exist_ok=True)
                        destination.write_bytes(archive.extractfile(member).read())
                    elif name.startswith('objects/') and name not in ('objects/info/packs',) and not re.fullmatch(r'objects/pack/pack-[0-9a-f]{40}\.(idx|rev)',name):
                        raise ServiceError('archive_entry_not_supported','Git archive contains an unrecognized object-store file')
        except ServiceError:raise
        except (tarfile.TarError,OSError,EOFError):raise ServiceError('invalid_archive','The Git archive is incomplete or unreadable') from None
        for pack in packs:
            # Git verifies pack checksums, expands deltas and creates its own trusted index.
            packed_bytes=pack.read_bytes()
            if len(packed_bytes)<32 or packed_bytes[:4]!=b'PACK' or hashlib.sha1(packed_bytes[:-20]).digest()!=packed_bytes[-20:]:
                raise ServiceError('git_pack_checksum_mismatch','Git pack bytes do not match their embedded checksum')
            git('index-pack','--stdin',input=packed_bytes)
        # Native SWH deposits can omit an author's email; retain that format warning.
        git('-c','fsck.missingEmail=warn','fsck','--full','--no-dangling','--no-reflogs')
        listing=git('cat-file','--batch-all-objects','--batch-check=%(objectname) %(objecttype)').decode('ascii').splitlines()
        objects=dict(line.split(' ',1) for line in listing);refs={**packed,**refs}
        for name,value in refs.items():
            if not value.startswith('ref: ') and (not re.fullmatch('[0-9a-f]{40}',value) or value not in objects):
                raise ServiceError('git_ref_target_missing','An archived reference has no matching object',ref=name)
        if match[1] in ('rev','rel','dir'):
            expected={'rev':'commit','rel':'tag','dir':'tree'}[match[1]]
            if objects.get(match[2])!=expected:raise ServiceError('archive_identity_mismatch','Git archive does not contain the selected object and type')
            if match[1] in ('rev','rel') and match[2] not in refs.values():raise ServiceError('archive_identity_mismatch','No archived reference selects the requested revision or release')
            if match[1]=='dir':
                targets=[git('cat-file','commit',value).split(b'\n\n',1)[0].splitlines() for value in refs.values() if objects.get(value)=='commit']
                if not any(b'tree '+match[2].encode() in headers and not any(h.startswith(b'parent ') for h in headers) for headers in targets):
                    raise ServiceError('archive_identity_mismatch','Directory bundle has no root commit selecting the requested directory')
        else:
            for name,branch in branches.items():
                actual=head if name=='HEAD' else refs.get(name)
                if branch is None:
                    if actual is not None:raise ServiceError('snapshot_ref_mismatch','An archived branch differs from a dangling snapshot branch',ref=name)
                    continue
                kind=branch['target_type'];target=branch['target']
                expected='ref: '+target if kind=='alias' else target
                if actual!=expected:raise ServiceError('snapshot_ref_mismatch','An archived reference differs from the selected snapshot',ref=name)
                if kind!='alias' and objects.get(target)!={'content':'blob','directory':'tree','revision':'commit','release':'tag'}.get(kind):
                    raise ServiceError('snapshot_ref_mismatch','A snapshot branch target has the wrong object type',ref=name)
            if set(refs)-set(branches):raise ServiceError('snapshot_ref_mismatch','Git archive contains branches outside the selected snapshot')
        return {'verified':True,'algorithm':'git_object_sha1_and_connectivity','scope':'directory_as_git' if match[1]=='dir' else 'archived_git_history','swhid':core,
            'objects':len(objects),'commits':sum(kind=='commit' for kind in objects.values()),'refs':refs,'head':head,
            'snapshot_manifest_verified':match[1]=='snp','warnings':warnings,'research_code_executed':False}


def git_archive(adapter,core,raw,evidence):
    url=BASE+'vault/git-bare/'+core+'/'
    try:job,proof=adapter.request(url)
    except ServiceError as error:
        if error.result['code']!='not_found_at_source':raise
        job,proof=adapter.request(url,json_body={})
    if not isinstance(job,dict) or job.get('swhid')!=core or job.get('status') not in ('new','pending','done','failed'):
        raise ServiceError('archive_identity_mismatch','Vault response identifies a different Git archive task',evidence=proof)
    if job['status'] in ('new','pending'):return {'status':'pending','job':proof,'retry_after_seconds':60,
        'retry_basis':'client_poll_interval_for_anonymous_api_budget','retry':{'source':adapter.source,'target':core,'parts':['history']}}
    if job['status']=='failed':return {'status':'error','code':'archive_preparation_failed','job':proof}
    target=urljoin(url,job.get('fetch_url',''));parts=urlsplit(target)
    if parts.scheme!='https' or parts.hostname!='archive.softwareheritage.org' or parts.username or parts.password or parts.port not in (None,443) or parts.query or parts.fragment or unquote(parts.path).rstrip('/')!='/api/1/vault/git-bare/'+core+'/raw':
        raise ServiceError('archive_identity_mismatch','Vault Git download URL does not identify the requested object',evidence=proof)
    branches=None;branch_proofs=[]
    if ':snp:' in core:branches,branch_proofs=complete_snapshot(adapter,core,raw,evidence)
    data,response=adapter.request(target,accept='binary');media='application/gzip' if data.startswith(b'\x1f\x8b') else 'application/x-tar'
    try:integrity=verify_git_archive(data,core,branches)
    except ServiceError as error:
        artifact=adapter.store.put(data,media,adapter.source,response['url'],preserve_bytes=True,role='unverified_git_archive',requested_swhid=core,job_ref=proof['ref'])
        return {**error.result,'source_archive':artifact,'job':proof}
    artifact=adapter.store.put(data,media,adapter.source,response['url'],preserve_bytes=True,role='vault_git_archive',swhid=core,integrity=integrity,job_ref=proof['ref'])
    return {'status':'available','artifact':artifact,'integrity':integrity,'job':proof,'branch_evidence':branch_proofs}

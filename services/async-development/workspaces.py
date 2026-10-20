"""Small source snapshots and explicit, conflict-detecting task integration."""
import hashlib
import contextlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import time

SKIP = {'.git', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache'}


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write_json(path, value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    pending=path.with_name(path.name+'.pending')
    pending.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    pending.replace(path)


def safe(root, relative):
    root=Path(root).resolve();part=Path(relative)
    if part.is_absolute() or '..' in part.parts or not part.parts:
        raise ValueError(f'Invalid relative path: {relative}')
    path=root/part
    for p in (path,*path.parents):
        if p==root:break
        if p.is_symlink() or (hasattr(p,'is_junction') and p.is_junction()):
            raise ValueError(f'Linked path: {p}')
    if not path.resolve().is_relative_to(root):raise ValueError(f'Path escapes root: {relative}')
    return path


def file_hash(path):
    path=Path(path)
    try:
        with path.open('rb') as stream:
            return hashlib.file_digest(stream,'sha256').hexdigest()
    except FileNotFoundError:return None


def object_path(records, digest):
    if not isinstance(digest,str) or not re.fullmatch('[0-9a-f]{64}',digest):
        raise ValueError('Invalid object hash')
    # Digest-only components cannot traverse out of records. Check the three
    # storage entries directly instead of resolving the entire ancestor chain
    # for every object in a large snapshot.
    root=Path(records)/'objects';path=root/digest[:2]/digest[2:]
    for entry in (root,path.parent,path):
        if entry.is_symlink() or (hasattr(entry,'is_junction') and entry.is_junction()):
            raise ValueError('Linked path: '+str(entry))
    return path


def save_object(records, source, *, expected=None, verified=None):
    """Ensure exact bytes are stored, reusing known hashes from inventories.

    Cleanup separately checks every remaining source file before deletion.
    Existing objects need not be recopied or their source rehashed here.
    """
    digest=expected if expected is not None else file_hash(source)
    if digest is None:raise ValueError('Missing snapshot content: '+str(source))
    if verified is not None and digest in verified:return digest
    dest=object_path(records,digest)
    if dest.exists():
        if verified is None or digest not in verified:
            if file_hash(dest)!=digest:raise ValueError('Corrupt snapshot object: '+digest)
    else:
        dest.parent.mkdir(parents=True,exist_ok=True)
        pending=dest.with_name(dest.name+'.pending')
        shutil.copyfile(source,pending)
        if file_hash(pending)!=digest:raise ValueError('Source changed during snapshot: '+str(source))
        pending.replace(dest)
    if verified is not None:verified.add(digest)
    return digest


def walk_files(root, *, skip=True):
    """Check each directory entry once, without resolving every ancestor per file."""
    root=Path(root)
    safe(root.parent,root.name)
    if not root.exists():return
    pending=[root]
    while pending:
        with os.scandir(pending.pop()) as entries:
            for entry in entries:
                if skip and entry.name in SKIP:continue
                path=Path(entry.path)
                junction=entry.is_junction() if hasattr(entry,'is_junction') else (hasattr(path,'is_junction') and path.is_junction())
                if entry.is_symlink() or junction:
                    raise ValueError('Linked path: '+str(path))
                if entry.is_dir(follow_symlinks=False):pending.append(path)
                elif entry.is_file(follow_symlinks=False):yield path


def files(root):
    root=Path(root)
    return {p.relative_to(root).as_posix():file_hash(p) for p in walk_files(root)}


@contextlib.contextmanager
def source_lock(records):
    """Serialize only snapshot creation and integration, not task execution."""
    path=Path(records)/'source.lock';path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a+b') as lock:
        lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0)
        if os.name=='nt':
            import msvcrt
            while True:
                try:msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1);break
                except OSError as exc:
                    if exc.errno not in (13,11):raise
                    time.sleep(.05)
        else:
            import fcntl
            fcntl.flock(lock,fcntl.LOCK_EX)
        try:yield
        finally:
            lock.seek(0)
            if os.name=='nt':msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1)
            else:fcntl.flock(lock,fcntl.LOCK_UN)


def prepare(repo, records, task, settings):
    with source_lock(records):return _prepare(repo,records,task,settings)


def _prepare(repo, records, task, settings):
    repo=Path(repo).resolve();records=Path(records).resolve()
    home=safe(records,'tasks/'+task['id']);home.mkdir(parents=True,exist_ok=True)
    workspace=home/'workspace';base=home/'base';inputs=home/'inputs'
    if workspace.exists() or base.exists() or (home/'baseline.json').exists():
        raise ValueError('Existing workspace or snapshot: use a new task ID to recover it')
    workspace.mkdir();inputs.mkdir(exist_ok=True)
    for name in ('context.md','plan.md','seams.md'):
        shutil.copyfile(records/name,inputs/name)
    copied=set();baseline={};verified=set()
    for scope in settings['snapshot_paths']:
        source=safe(repo,scope)
        if not source.exists():raise FileNotFoundError(source)
        candidates=[source] if source.is_file() else walk_files(source)
        for path in candidates:
            rel=path.relative_to(repo)
            if any(p in SKIP for p in rel.parts):continue
            if not path.is_file() or rel.as_posix() in copied:continue
            target=safe(workspace,rel);target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(path,target)
            baseline[rel.as_posix()]=save_object(records,target,verified=verified)
            copied.add(rel.as_posix())
    write_json(home/'task.json',task)
    write_json(home/'baseline.json',baseline)
    return workspace


def permitted(path, scopes):
    return any(path==s.rstrip('/') or (s.endswith('/') and path.startswith(s)) for s in scopes)


def difference(before, after, writes):
    changed={p:(before.get(p),after.get(p)) for p in before.keys()|after.keys() if before.get(p)!=after.get(p)}
    outside=[p for p in changed if not permitted(p,writes)]
    if outside:raise ValueError('Changes outside assigned writes: '+', '.join(outside))
    return changed


def changes(records, task_id):
    home=safe(Path(records),'tasks/'+task_id)
    task=read_json(home/'task.json');before=read_json(home/'baseline.json')
    if (home/'archive.json').exists():
        archive_metadata(home)
        after=read_json(home/'result.json')
    else:
        if not (home/'workspace').is_dir():raise ValueError('Missing workspace: '+task_id)
        after=files(home/'workspace')
    return home,difference(before,after,task['writes'])


def integrate(repo, records, task_id):
    with source_lock(records):return _integrate(repo,records,task_id)


def _integrate(repo, records, task_id):
    repo=Path(repo).resolve();home,changed=changes(records,task_id)
    if (home/'archive.json').exists():
        # Historical accepted results must not be applied over later revisions.
        if task_id not in read_json(Path(records)/'queue.json')['accepted']:
            raise ValueError('Archived task is not accepted: '+task_id)
        return read_json(home/'integration.json')
    conflicts=[]
    for rel,(old,new) in changed.items():
        actual=file_hash(safe(repo,rel))
        if actual not in (old,new):conflicts.append(rel)
    if conflicts:raise ValueError('Integration conflict; canonical edits preserved: '+', '.join(conflicts))
    # Preflight all conflicts before writing. A repeated call is idempotent.
    for rel,(_,new) in changed.items():
        dest=safe(repo,rel)
        if file_hash(dest)==new:continue
        if new is None:dest.unlink()
        else:
            dest.parent.mkdir(parents=True,exist_ok=True)
            pending=dest.with_name(dest.name+'.integrating-'+task_id)
            shutil.copyfile(safe(home/'workspace',rel),pending);pending.replace(dest)
    result={'task':task_id,'files':list(changed),
            'changes':{p:list(v) for p,v in changed.items()}}
    write_json(home/'integration.json',result)
    return result


def archive_metadata(home):
    archive=read_json(home/'archive.json')
    if archive.get('version')!=1 or archive.get('task')!=home.name:
        raise ValueError('Invalid archive: '+str(home))
    for name in ('baseline.json','result.json','report.json','integration.json'):
        if file_hash(home/name)!=archive['hashes'].get(name):
            raise ValueError('Archived record changed: '+str(home/name))
    return archive


def _remove_snapshot(home, name, inventory):
    """Delete only a checked snapshot below this task; never follow links."""
    target=safe(home,name)
    if not target.exists():return
    if target.parent!=home.resolve() or name not in ('base','workspace'):
        raise ValueError('Unsafe cleanup target: '+str(target))
    # Validate the whole tree before deleting anything, including ignored caches.
    current={p.relative_to(target).as_posix():file_hash(p) for p in walk_files(target,skip=False)
             if not any(part in SKIP for part in p.relative_to(target).parts)}
    if any(inventory.get(p)!=h for p,h in current.items()):
        raise ValueError('Snapshot changed after archiving: '+str(target))
    shutil.rmtree(target)


def cleanup(records, task_id):
    """Archive and remove an accepted, integrated, terminated task's copies."""
    with source_lock(records):return _cleanup(Path(records).resolve(),task_id)


def _cleanup(records, task_id):
    home=safe(records,'tasks/'+task_id)
    queue=read_json(records/'queue.json');state=read_json(records/'state.json')
    if task_id not in queue['accepted']:raise ValueError('Task is not accepted: '+task_id)
    entry=state['tasks'].get(task_id,{})
    if entry.get('status') not in ('exited','interrupted','launch_failed'):
        raise ValueError('Task has not terminated: '+task_id)
    report=read_json(home/'report.json');receipt=read_json(home/'integration.json')
    if receipt.get('task')!=task_id or set(receipt['files'])!=set(report['changes']):
        raise ValueError('Report and integration differ: '+task_id)
    if (home/'archive.json').exists():
        archive_metadata(home)
        before=read_json(home/'baseline.json');after=read_json(home/'result.json')
        for digest in set(before.values())|set(after.values()):
            if file_hash(object_path(records,digest))!=digest:
                raise ValueError('Missing or corrupt archive object: '+digest)
    else:
        if not (home/'workspace').is_dir():raise ValueError('Missing workspace: '+task_id)
        before=read_json(home/'baseline.json');verified=set()
        # Enumerating checks every entry for links once. Reuse those checked
        # paths instead of re-walking all ancestors for each historical file.
        legacy_paths={p.relative_to(home/'base').as_posix():p for p in walk_files(home/'base')}
        result_paths={p.relative_to(home/'workspace').as_posix():p for p in walk_files(home/'workspace')}
        after={rel:file_hash(p) for rel,p in result_paths.items()}
        delta=difference(before,after,read_json(home/'task.json')['writes'])
        if set(delta)!=set(receipt['files']):raise ValueError('Unintegrated changes: '+task_id)
        if 'changes' in receipt and receipt['changes']!={p:list(v) for p,v in delta.items()}:
            raise ValueError('Integrated content changed: '+task_id)
        for rel,digest in before.items():
            legacy=legacy_paths.get(rel)
            if legacy is not None:save_object(records,legacy,expected=digest,verified=verified)
            elif digest not in verified:
                if file_hash(object_path(records,digest))!=digest:
                    raise ValueError('Missing baseline content: '+rel)
                verified.add(digest)
        for rel,digest in after.items():
            save_object(records,result_paths[rel],expected=digest,verified=verified)
        write_json(home/'result.json',after)
        write_json(home/'archive.json',{'version':1,'task':task_id,'hashes':{
            name:file_hash(home/name) for name in ('baseline.json','result.json','report.json','integration.json')}})
    # The archive is committed before deletion. An interrupted removal is resumable.
    _remove_snapshot(home,'base',before)
    _remove_snapshot(home,'workspace',after)
    result={'version':1,'task':task_id,'status':'complete','archive_sha256':file_hash(home/'archive.json')}
    write_json(home/'cleanup.json',result)
    return result


def cleanup_accepted(records):
    """Called between managers; reports/evidence and unaccepted work stay intact."""
    records=Path(records);results=[]
    for task_id in read_json(records/'queue.json')['accepted']:
        home=safe(records,'tasks/'+task_id)
        if (home/'cleanup.json').exists() and not (home/'base').exists() and not (home/'workspace').exists():
            continue
        try:results.append(cleanup(records,task_id))
        except (ValueError,OSError,KeyError,TypeError) as exc:
            results.append({'task':task_id,'status':'retained','reason':str(exc)})
    return results


def restore(records, task_id, version, destination, paths=()):
    """Restore all or selected historical files to a new, independent directory."""
    records=Path(records).resolve();home=safe(records,'tasks/'+task_id)
    if version not in ('baseline','result'):raise ValueError('Use baseline or result')
    if (home/'archive.json').exists():archive_metadata(home)
    inventory=read_json(home/(version+'.json'))
    selected={p:h for p,h in inventory.items() if not paths or any(p==s or p.startswith(s.rstrip('/')+'/') for s in paths)}
    if paths and any(not any(p==s or p.startswith(s.rstrip('/')+'/') for p in inventory) for s in paths):
        raise ValueError('Requested path is not in snapshot')
    destination=Path(destination).absolute()
    if destination.exists():raise ValueError('Restore destination must not exist')
    # Validate destination ancestors before mkdir; do not restore into managed storage.
    safe(destination.parent,destination.name)
    resolved=destination.resolve()
    if resolved.is_relative_to(records/'objects'):
        raise ValueError('Restore outside managed objects')
    if resolved.is_relative_to(records/'tasks'):
        parts=resolved.relative_to(records/'tasks').parts
        if len(parts)<3 or parts[1] in ('base','workspace'):
            raise ValueError('Restore outside managed task snapshots')
    verified=set()
    for rel,digest in selected.items():
        safe(destination,rel)
        if digest not in verified:
            if file_hash(object_path(records,digest))!=digest:raise ValueError('Missing or corrupt snapshot object: '+digest)
            verified.add(digest)
    destination.mkdir(parents=True)
    for rel,digest in selected.items():
        target=safe(destination,rel);target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(object_path(records,digest),target)
    return {'task':task_id,'version':version,'destination':str(destination),'files':len(selected)}


if __name__=='__main__':
    args=sys.argv[1:]
    if args and args[0]=='integrate' and len(args)==4:result=integrate(*args[1:])
    elif args and args[0]=='cleanup' and len(args)==3:result=cleanup(*args[1:])
    elif args and args[0]=='cleanup-accepted' and len(args)==2:result=cleanup_accepted(args[1])
    elif args and args[0]=='restore' and len(args)>=5:result=restore(*args[1:5],paths=args[5:])
    else:raise SystemExit('Use integrate REPO RECORDS TASK | cleanup RECORDS TASK | cleanup-accepted RECORDS | restore RECORDS TASK baseline|result NEW_DIRECTORY [PATH ...]')
    print(json.dumps(result,ensure_ascii=False))

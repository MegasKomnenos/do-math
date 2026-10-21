"""Small source snapshots and explicit, conflict-detecting task integration."""
import hashlib
import contextlib
import json
import os
from pathlib import Path
import shutil
import sys
import time

SKIP = {'.git', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache'}


def _sharing_retry(operation):
    """Windows may briefly deny access while another process replaces a file."""
    for attempt in range(20):
        try:return operation()
        except PermissionError:
            if os.name!='nt' or attempt==19:raise
            time.sleep(.01)


def read_json(path):
    return json.loads(_sharing_retry(lambda: Path(path).read_text(encoding='utf-8-sig')))


def replace_file(source, target):
    return _sharing_retry(lambda: Path(source).replace(target))


def write_json(path, value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    pending=path.with_name(path.name+'.pending')
    pending.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    replace_file(pending,path)


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
    if not path.exists():return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def files(root):
    root=Path(root);result={}
    for path in root.rglob('*'):
        rel=path.relative_to(root)
        if any(p in SKIP for p in rel.parts):continue
        safe(root,rel)
        if path.is_file():result[rel.as_posix()]=file_hash(path)
    return result


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
    if workspace.exists() or base.exists():raise ValueError('Existing workspace: use a new task ID to recover it')
    workspace.mkdir();base.mkdir();inputs.mkdir(exist_ok=True)
    for name in ('context.md','plan.md','seams.md'):
        shutil.copyfile(records/name,inputs/name)
    copied=set()
    for scope in settings['snapshot_paths']:
        source=safe(repo,scope)
        if not source.exists():raise FileNotFoundError(source)
        candidates=[source] if source.is_file() else source.rglob('*')
        for path in candidates:
            rel=path.relative_to(repo)
            if any(p in SKIP for p in rel.parts):continue
            safe(repo,rel)
            if not path.is_file() or rel.as_posix() in copied:continue
            for dest in (base,workspace):
                target=safe(dest,rel);target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(path,target)
            copied.add(rel.as_posix())
    write_json(home/'task.json',task)
    write_json(home/'baseline.json',files(base))
    return workspace


def permitted(path, scopes):
    return any(path==s.rstrip('/') or (s.endswith('/') and path.startswith(s)) for s in scopes)


def changes(records, task_id):
    home=safe(Path(records),'tasks/'+task_id)
    task=read_json(home/'task.json');before=read_json(home/'baseline.json');after=files(home/'workspace')
    changed={p:(before.get(p),after.get(p)) for p in before.keys()|after.keys() if before.get(p)!=after.get(p)}
    outside=[p for p in changed if not permitted(p,task['writes'])]
    if outside:raise ValueError('Changes outside assigned writes: '+', '.join(outside))
    return home,changed


def integrate(repo, records, task_id):
    with source_lock(records):return _integrate(repo,records,task_id)


def _integrate(repo, records, task_id):
    repo=Path(repo).resolve();home,changed=changes(records,task_id)
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
    result={'task':task_id,'files':list(changed)}
    write_json(home/'integration.json',result)
    return result


if __name__=='__main__':
    action,repo,records,task=sys.argv[1:]
    if action!='integrate':raise SystemExit('Usage: workspaces.py integrate REPO RECORDS TASK')
    print(json.dumps(integrate(repo,records,task),ensure_ascii=False))

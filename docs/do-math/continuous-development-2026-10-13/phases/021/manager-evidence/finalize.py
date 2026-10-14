"""Preserve inspected bytes and publish/commit only this management handoff."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import zipfile

R=Path('C:/math'); RUN=R/'docs/do-math/continuous-development-2026-10-13'
O=Path(__file__).resolve().parent; P=RUN/'phases/021'; T=P/'tasks/document-review'

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v): (O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def git(*args): return subprocess.check_output(['git',*args],cwd=R)
def command(n,args):
    p=subprocess.run(args,cwd=R,capture_output=True)
    row={'argv':args,'cwd':str(R),'exit_code':p.returncode,'stdout':p.stdout.decode('utf-8',errors='replace'),
         'stderr':p.stderr.decode('utf-8',errors='replace')}
    save(n,row)
    assert p.returncode==0,row
    return row

head=read(O/'verification.json')['head']
source=read(O/'source-inspected.json')
task_hashes=read(O/'task-files.json')
products=sorted(row['path'] for row in read(T/'report.json')['changes']
                if Path(row['path']).name not in ('.timings.json','.timings-t3.json'))
assert len(products)==26

def unchanged():
    assert git('rev-parse','HEAD').decode().strip()==head
    assert all(sha(R/p)==h for p,h in source.items())
    assert {p.relative_to(T).as_posix():sha(p) for p in T.rglob('*') if p.is_file()}==task_hashes
    assert all(sha(RUN/n)==h for n,h in read(O/'common-after-sha.json').items())
    assert sorted((R/'기억/layer1').glob('M-*.md'))[-1].name=='M-0571.md'
    assert 'convention_version: 27' in (R/'기억/세칙.md').read_text(encoding='utf-8')

mode=sys.argv[1]
if mode=='prepare':
    unchanged()
    assert not git('diff','--cached','--name-only','-z')
    archive=O/'raw-evidence.zip'
    assert not archive.exists()
    archived={p for p in T.rglob('*') if p.is_file()} | {R/p for p in products}
    entries={}
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(archived):
            raw=p.read_bytes(); rel=p.relative_to(R).as_posix()
            z.writestr(rel,raw); entries[rel]=hashlib.sha256(raw).hexdigest()
    with zipfile.ZipFile(archive) as z:
        assert set(z.namelist())==set(entries)
        assert all(hashlib.sha256(z.read(p)).hexdigest()==h for p,h in entries.items())
    paths={RUN/n for n in ('context.md','plan.md','seams.md','sources/document-batching-2026-10-14.md',
        'phases/021/manager.json','phases/022/phase.json','phases/022/tasks/review-delivery/objective.md')}
    paths.update({R/'기억/layer1/M-0571.md',R/'기억/색인.md',T/'report.json'})
    paths.update(O/n for n in ('verify.py','prepare.py','finalize.py','verification.json','source-inspected.json',
        'report-check.json','review.md','common-docs.diff','common-before-sha.json','common-after-sha.json',
        'task-files.json','history-check.json','proposal-check.json','failure-mapping.json',
        'preservation.json','raw-evidence.zip'))
    e=T/'evidence'
    paths.update(p for p in e.iterdir() if p.is_file() and not p.name.endswith(('-before.json','-after.json'))
                 and p.name not in ('preservation-current.json',))
    paths.update(e/n/'report.json' for n in ('red','focus','corrected','corrected2','corrected3','corrected4',
                                          'focused-final','c','m','proposal'))
    relative=sorted(p.relative_to(R).as_posix() for p in paths)
    assert not set(products)&set(relative)
    assert not any(p.startswith(('.claude/','.agents/','services/')) for p in relative)
    save('preservation.json',{'archive':archive.relative_to(R).as_posix(),'archive_sha256':sha(archive),
        'archive_bytes':archive.stat().st_size,'entries':entries,'products_committed':[],
        'products_deferred':products,'product_count':26,'task_files':len(task_hashes),'tracked_paths':relative,
        'raw_bytes':'Original task files and 26 inspected product paths are archived and independently read back with SHA256. Original task bytes are unchanged.',
        'local_only':'Unselected repeated source snapshots remain local; their exact bytes are preserved in this tracked archive. Stage/commit receipts and session logs remain local and may disappear after cleanup. Archive is not a restoration instruction.',
        'scope':'Management handoff, explicit document-batching source, selected originals, next assignment and one memory node. Product files remain uncommitted until F1 repair/verification. Unrelated dirty/untracked files, engine and operator changes are not staged.'})
    pending=P/'manager.pending.json'; published=P/'manager.json'
    assert pending.exists() and not published.exists()
    hashes={p:sha(R/p) for p in relative if p!=published.relative_to(R).as_posix()}
    save('commit-plan.json',{'head':head,'paths':relative,'sha256':hashes,'products_committed':0,
        'products_deferred':26,'pending_sha256':sha(pending)})
    (O/'commit-paths.nul').write_bytes(b'\0'.join(p.encode('utf-8') for p in relative)+b'\0')
    command('memory-check.json',[sys.executable,'-B','기억/scripts/validate_memory_index.py'])
    command('handoff-check.json',[sys.executable,'-B','services/continuous-development/check.py',
            'handoff',str(R),str(RUN),'021'])
    unchanged()
    assert all(sha(R/p)==h for p,h in hashes.items()) and sha(pending)==read(O/'commit-plan.json')['pending_sha256']
    print(json.dumps({'archive_entries':len(entries),'archive_bytes':archive.stat().st_size,
        'planned_paths':len(relative),'memory':'PASS','handoff':'PASS 021','next':'022'},ensure_ascii=False))
elif mode=='publish':
    plan=read(O/'commit-plan.json'); relative=plan['paths']; hashes=plan['sha256']
    unchanged()
    assert not git('diff','--cached','--name-only','-z')
    assert read(O/'memory-check.json')['exit_code']==read(O/'handoff-check.json')['exit_code']==0
    assert all(sha(R/p)==h for p,h in hashes.items())
    pending=P/'manager.pending.json'; published=P/'manager.json'
    assert pending.exists() and not published.exists() and sha(pending)==plan['pending_sha256']
    pending.rename(published)
    assert sha(published)==plan['pending_sha256']
    print('Published checked manager.json; next 022.',flush=True)
    command('stage-command.json',['git','add','-f','--pathspec-from-file='+str(O/'commit-paths.nul'),'--pathspec-file-nul'])
    staged=set(filter(None,git('diff','--cached','--name-only','-z').decode().split('\0')))
    assert staged and staged <= set(relative)
    assert not set(products)&staged
    assert [p for p in staged if p.startswith('기억/layer1/')]==['기억/layer1/M-0571.md']
    command('staged-diff-check.json',['git','diff','--cached','--check'])
    data=subprocess.check_output(['git','cat-file','--batch'],cwd=R,
        input=('\n'.join(':'+p for p in relative)+'\n').encode('utf-8'))
    stream=io.BytesIO(data); received={}
    for path in relative:
        oid,kind,size=stream.readline().decode().split(); assert kind=='blob'
        blob=stream.read(int(size)); assert stream.read(1)==b'\n'
        raw=(R/path).read_bytes()
        if '/evidence/' in path or '/manager-evidence/' in path or path.endswith(('/report.json','/manager.json')):
            assert blob==raw,path
        else:
            assert blob==raw or blob==raw.replace(b'\r\n',b'\n'),path
        received[path]={'blob':oid,'sha256':sha(R/path),'raw_equals_blob':blob==raw}
    assert not stream.read()
    save('stage.json',{'head':head,'planned_count':len(relative),'staged_count':len(staged),
        'products_committed':0,'products_deferred':26,'paths':received,'changed_paths':sorted(staged)})
    unchanged()
    assert all(sha(R/p)==row['sha256'] for p,row in received.items())
    assert staged==set(filter(None,git('diff','--cached','--name-only','-z').decode().split('\0')))
    command('pre-commit-status.json',['git','status','--short','--untracked-files=no'])
    (O/'commit-message.txt').write_text('검토 입력 중복을 기록하고 제출 경계 수리와 문서 검증을 묶어 배정함\n',encoding='utf-8')
    command('commit.json',['git','commit','--file',str(O/'commit-message.txt')])
    newhead=git('rev-parse','HEAD').decode().strip()
    committed=set(filter(None,git('diff-tree','--no-commit-id','--name-only','-r','-z',newhead).decode().split('\0')))
    assert committed==staged
    blobs={entry.split(b'\t',1)[1].decode('utf-8'):entry.split(b'\t',1)[0].decode().split()[2]
           for entry in git('ls-tree','-r','-z',newhead).split(b'\0') if entry}
    assert all(blobs[p]==row['blob'] for p,row in received.items())
    assert all(sha(R/p)==row['sha256'] for p,row in received.items())
    assert all(sha(R/p)==h for p,h in source.items())
    assert all(sha(T/p)==h for p,h in task_hashes.items())
    assert not git('diff','--cached','--name-only','-z')
    save('post-commit.json',{'head':newhead,'parent':head,'committed_count':len(committed),
        'products_committed':0,'products_deferred':26,'source_raw_bytes_unchanged':True,
        'task_raw_bytes_preserved':True,'index_empty':True,'manager_sha256':plan['pending_sha256'],
        'next':'022','push_performed':False})
    print(json.dumps({'head':newhead,'committed':len(committed),'products_committed':0,
        'handoff':'PASS 021','next':'022'},ensure_ascii=False))
else:
    raise ValueError(mode)

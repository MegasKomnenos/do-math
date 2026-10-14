"""Preserve originals, publish checked manager submission, and commit exact paths."""
import difflib
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import zipfile

R=Path('C:/math'); RUN=R/'docs/do-math/continuous-development-2026-10-13'
O=Path(__file__).resolve().parent; P=RUN/'phases/019'; T=P/'tasks/document-results'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v): (O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def git(*args): return subprocess.check_output(['git',*args],cwd=R)
def command(n,args):
    p=subprocess.run(args,cwd=R,capture_output=True)
    row={'argv':args,'cwd':str(R),'exit_code':p.returncode,'stdout':p.stdout.decode('utf-8',errors='replace'),
         'stderr':p.stderr.decode('utf-8',errors='replace')}
    save(n,row); assert p.returncode==0,row
    return row

head=git('rev-parse','HEAD').decode().strip()
assert head==read(O/'verification.json')['head'] and not git('diff','--cached','--name-only','-z')
source=read(O/'source-inspected.json'); assert all(sha(R/p)==h for p,h in source.items())
products={row['path'] for row in read(T/'report.json')['changes'] if Path(row['path']).name not in ('.timings.json','.timings-t3.json')}
assert len(products)==28
task_hashes=read(O/'task-files.json')
assert {p.relative_to(T).as_posix():sha(p) for p in T.rglob('*') if p.is_file()}==task_hashes
assert sorted((R/'기억/layer1').glob('M-*.md'))[-1].name=='M-0569.md'
assert 'convention_version: 27' in (R/'기억/세칙.md').read_text(encoding='utf-8')

flow=R/'.claude/skills/write-for-reader/scripts/writing_flow.py'
status=command('writing-status.json',[sys.executable,'-B',str(flow),'--session','continuous-phase019-manager','status'])
state=json.loads(status['stdout']); assert not state['completion_problem']
for path,h in read(O/'draft-sources.json').items(): assert sha(R/path)==h
diff=''
for name in ('context.md','plan.md','seams.md'):
    old=git('show',head+':'+(RUN/name).relative_to(R).as_posix()).decode('utf-8-sig').replace('\r\n','\n')
    new=(RUN/name).read_text(encoding='utf-8')
    if name=='context.md': assert old.split('## C2 ')[0]==new.split('## C2 ')[0]
    diff+=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=name+' before 019',tofile=name+' after 019'))
assert diff==(O/'common-docs.diff').read_text(encoding='utf-8')

archived={p for p in T.rglob('*') if p.is_file()}
archived.update(R/p for p in products)
workflow=Path(state['job_dir'])
archived.update(p for p in workflow.rglob('*') if p.is_file())
archive=O/'raw-evidence.zip'; assert not archive.exists()
entries={}
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for path in sorted(archived):
        raw=path.read_bytes(); rel=path.relative_to(R).as_posix()
        z.writestr(rel,raw); entries[rel]=hashlib.sha256(raw).hexdigest()
with zipfile.ZipFile(archive) as z:
    assert set(z.namelist())==set(entries)
    assert all(hashlib.sha256(z.read(p)).hexdigest()==h for p,h in entries.items())
print('Preserved '+str(len(entries))+' original files; archive '+str(archive.stat().st_size)+' bytes.',flush=True)

paths={RUN/n for n in ('context.md','plan.md','seams.md','phases/019/manager.json','phases/020/phase.json',
                      'phases/020/tasks/document-tools/objective.md')}
paths.update({R/'기억/layer1/M-0569.md',R/'기억/색인.md',T/'report.json'})
paths.update(R/p for p in products)
paths.update(O/n for n in ('verify.py','prepare.py','revise.py','finalize.py','verification.json','source-inspected.json',
    'report-check.json','review.md','common-docs.diff','task-files.json','history-check.json','preservation.json',
    'raw-evidence.zip','writing-brief.md','writing-audience.md','handoff-draft.md','draft-sources.json',
    'writing-begin.json','writing-decision.json','writing-decide.json','writing-status.json','reading-result.json',
    'writing-decision-1.json','writing-decide-1.json','reading-result-1.json'))
e=T/'evidence'
paths.update(p for p in e.iterdir() if p.is_file() and not p.name.endswith(('-before.json','-after.json'))
             and p.name not in ('preservation-current.json',))
paths.update(e/n/'report.json' for n in ('red','focus','corrected','c','m'))
relative=sorted(p.relative_to(R).as_posix() for p in paths)
assert products <= set(relative)
assert not any(p.endswith(('/.timings.json','/.timings-t3.json')) for p in relative)
save('preservation.json',{'archive':archive.relative_to(R).as_posix(),'archive_sha256':sha(archive),
    'archive_bytes':archive.stat().st_size,'entries':entries,'products_committed':sorted(products),'product_count':28,
    'tracked_paths':relative,'raw_bytes':'Original task report/evidence, 28 inspected product files, and writing-flow reading/decision originals are archived and read back with SHA256. Task files remain unchanged.',
    'local_only':'Unselected repeated snapshots and the writing-flow originals remain local; their bytes are in this tracked archive. Stage/commit receipts and session logs remain local and may disappear after cleanup. Archive is not a restoration instruction.',
    'scope':'Inspected P02 products, handoff, selected original evidence and one memory node. Timing caches, unrelated dirty/untracked files, engine and operator changes are not staged.'})
pending=P/'manager.pending.json'; published=P/'manager.json'
assert pending.exists() and not published.exists()
hashes={p:sha(R/p) for p in relative if p!=published.relative_to(R).as_posix()}
save('commit-plan.json',{'head':head,'paths':relative,'sha256':hashes,'products':28})
(O/'commit-paths.nul').write_bytes(b'\0'.join(p.encode('utf-8') for p in relative)+b'\0')
command('memory-check.json',[sys.executable,'-B','기억/scripts/validate_memory_index.py'])
command('handoff-check.json',[sys.executable,'-B','services/continuous-development/check.py','handoff',str(R),str(RUN),'019'])
assert all(sha(R/p)==h for p,h in hashes.items())
assert all(sha(R/p)==h for p,h in source.items())
assert all(sha(R/p)==h for p,h in entries.items())
pending_hash=sha(pending); pending.rename(published); assert sha(published)==pending_hash
print('PASS memory/handoff 019; published manager.json, next 020.',flush=True)

assert git('rev-parse','HEAD').decode().strip()==head and not git('diff','--cached','--name-only','-z')
command('stage-command.json',['git','add','-f','--pathspec-from-file='+str(O/'commit-paths.nul'),'--pathspec-file-nul'])
staged=set(filter(None,git('diff','--cached','--name-only','-z').decode().split('\0')))
assert staged==set(relative),(staged-set(relative),set(relative)-staged)
command('staged-diff-check.json',['git','diff','--cached','--check'])
data=subprocess.check_output(['git','cat-file','--batch'],cwd=R,input=('\n'.join(':'+p for p in relative)+'\n').encode('utf-8'))
stream=io.BytesIO(data); received={}
for path in relative:
    oid,kind,size=stream.readline().decode().split(); assert kind=='blob'
    blob=stream.read(int(size)); assert stream.read(1)==b'\n'
    raw=(R/path).read_bytes()
    if '/evidence/' in path or '/manager-evidence/' in path or path.endswith(('/report.json','/manager.json')):
        assert blob==raw,path
    else: assert blob==raw or blob==raw.replace(b'\r\n',b'\n'),path
    received[path]={'blob':oid,'sha256':sha(R/path),'raw_equals_blob':blob==raw}
assert not stream.read()
save('stage.json',{'head':head,'count':len(relative),'products':28,'paths':received})
assert git('rev-parse','HEAD').decode().strip()==head
assert set(filter(None,git('diff','--cached','--name-only','-z').decode().split('\0')))==set(relative)
assert all(sha(R/p)==h for p,h in source.items()) and all(sha(R/p)==v['sha256'] for p,v in received.items())
assert [p for p in relative if p.startswith('기억/layer1/')]==['기억/layer1/M-0569.md']
assert sorted((R/'기억/layer1').glob('M-*.md'))[-1].name=='M-0569.md'
command('pre-commit-status.json',['git','status','--short','--untracked-files=no'])
(O/'commit-message.txt').write_text('결과 문서 결속을 마감하고 실행 안내와 지급 도구 검증을 배정함\n',encoding='utf-8')
command('commit.json',['git','commit','--file',str(O/'commit-message.txt')])
newhead=git('rev-parse','HEAD').decode().strip()
committed=set(filter(None,git('diff-tree','--no-commit-id','--name-only','-r','-z',newhead).decode().split('\0')))
assert committed==set(relative)
tree=git('ls-tree','-r','-z',newhead)
blobs={entry.split(b'\t',1)[1].decode('utf-8'):entry.split(b'\t',1)[0].decode().split()[2]
       for entry in tree.split(b'\0') if entry}
assert all(blobs[p]==v['blob'] for p,v in received.items())
assert all(sha(R/p)==v['sha256'] for p,v in received.items()) and all(sha(R/p)==h for p,h in source.items())
assert not git('diff','--cached','--name-only','-z')
save('post-commit.json',{'head':newhead,'parent':head,'committed_count':len(relative),'products':28,
    'source_raw_bytes_unchanged':True,'task_raw_bytes_preserved':True,'index_empty':True,
    'manager_sha256':pending_hash,'next':'020','push_performed':False})
print(json.dumps({'head':newhead,'committed':len(relative),'products':28,'handoff':'PASS 019','next':'020'},ensure_ascii=False))

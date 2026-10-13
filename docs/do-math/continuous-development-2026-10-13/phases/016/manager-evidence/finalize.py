"""Preserve original bytes, validate handoff, publish, and commit only management files."""
import difflib
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

R=Path('C:/math'); RUN=R/'docs/do-math/continuous-development-2026-10-13'
O=Path(__file__).resolve().parent; P=RUN/'phases/016'; T=P/'tasks'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,v): (O/name).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def git(*args): return subprocess.check_output(['git',*args],cwd=R)
def command(name,args):
    p=subprocess.run(args,cwd=R,capture_output=True)
    row={'argv':args,'cwd':str(R),'exit_code':p.returncode,'stdout':p.stdout.decode('utf-8',errors='replace'),
         'stderr':p.stderr.decode('utf-8',errors='replace')}
    save(name,row); assert p.returncode==0,row
    return row

head=git('rev-parse','HEAD').decode().strip()
assert head==read(O/'verification.json')['head'] and not git('diff','--cached','--name-only','-z')
source=read(O/'source-inspected.json'); assert all(sha(R/p)==h for p,h in source.items())
products=set(read(O/'verification.json')['old_015_product_paths_unchanged'])
products.update(row['path'] for row in read(T/'t4-fixture-repair/report.json')['changes'] if not row['path'].endswith(('/.timings.json','/.timings-t3.json')))
assert len(products)==22
assert 'convention_version: 27' in (R/'기억/세칙.md').read_text(encoding='utf-8')
assert sorted((R/'기억/layer1').glob('M-*.md'))[-1].name=='M-0566.md'

# Normalize only trailing blank lines in manager-owned prose, then record the final diff.
diff=''
for name in ('context.md','plan.md','seams.md'):
    p=RUN/name; p.write_text(p.read_text(encoding='utf-8').rstrip()+'\n',encoding='utf-8',newline='\n')
    old=git('show',head+':'+p.relative_to(R).as_posix()).decode('utf-8-sig').replace('\r\n','\n')
    now=p.read_text(encoding='utf-8')
    if name=='context.md': assert old.split('## C2 ')[0]==now.split('## C2 ')[0]
    diff+=''.join(difflib.unified_diff(old.splitlines(True),now.splitlines(True),fromfile=name+' before 016',tofile=name+' after 016'))
(O/'common-docs.diff').write_text(diff,encoding='utf-8',newline='\n')

archived={p for p in T.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}
archived.update(R/p for p in products)
entries={}; archive=O/'raw-evidence.zip'
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(archived):
        raw=p.read_bytes(); rel=p.relative_to(R).as_posix()
        z.writestr(rel,raw); entries[rel]=hashlib.sha256(raw).hexdigest()
with zipfile.ZipFile(archive) as z:
    assert set(z.namelist())==set(entries)
    assert all(hashlib.sha256(z.read(p)).hexdigest()==h for p,h in entries.items())
print('Preserved '+str(len(entries))+' files; archive '+str(archive.stat().st_size)+' bytes.',flush=True)

paths={RUN/name for name in ('context.md','plan.md','seams.md','phases/016/manager.json','phases/017/phase.json',
                            'phases/017/tasks/t4-baseline-integration/objective.md')}
paths.update({R/'기억/layer1/M-0566.md',R/'기억/색인.md'})
paths.update(O/name for name in ('verify.py','prepare.py','finalize.py','verification.json','source-inspected.json',
    't4-fixture-repair-report-check.json','provenance-baseline-report-check.json','review.md','common-docs.diff','preservation.json','raw-evidence.zip'))
for task in T.iterdir():
    paths.add(task/'report.json')
    e=task/'evidence'
    paths.update(p for p in e.iterdir() if p.is_file() and not p.name.endswith(('.source-before.json','.source-after.json','.started.json','.stdout.bin')) and p.name!='write_report.py')
    for d in e.iterdir():
        if d.is_dir() and (d/'report.json').is_file(): paths.add(d/'report.json')
relative=sorted(p.relative_to(R).as_posix() for p in paths)
assert not set(relative)&products
save('preservation.json',{'archive':archive.relative_to(R).as_posix(),'archive_sha256':sha(archive),'archive_bytes':archive.stat().st_size,
    'entries':entries,'products_deferred':sorted(products),'product_count':22,'tracked_paths':relative,
    'raw_bytes':'Original reports and both task evidence trees, including 910 baseline files, plus 22 pending product files are archived and read back with SHA256. Task originals are untouched.',
    'local_only':'Unselected scratch, baseline tree original paths, repeated source snapshots and raw child directories remain local; their bytes are tracked in the archive. Command stage/commit receipts and session logs are local and may disappear after cleanup. Archive is not a restoration instruction.',
    'scope':'Only current management handoff, selected original evidence and one memory node are committed. Product changes, timing caches, earlier untracked files, engine and operator changes remain unstaged.'})
pending=P/'manager.pending.json'; published=P/'manager.json'
assert pending.exists() and not published.exists()
hashes={p:sha(R/p) for p in relative if p!=published.relative_to(R).as_posix()}
save('commit-plan.json',{'head':head,'paths':relative,'sha256':hashes,'products_staged':0,'products_deferred':sorted(products)})
(O/'commit-paths.nul').write_bytes(b'\0'.join(p.encode('utf-8') for p in relative)+b'\0')
command('memory-check.json',[sys.executable,'-B','기억/scripts/validate_memory_index.py'])
command('handoff-check.json',[sys.executable,'-B','services/continuous-development/check.py','handoff',str(R),str(RUN),'016'])
assert all(sha(R/p)==h for p,h in hashes.items())
assert all(sha(R/p)==h for p,h in source.items())
assert all(sha(R/p)==h for p,h in entries.items())
pending_hash=sha(pending); pending.rename(published); assert sha(published)==pending_hash
print('PASS memory/handoff 016; published manager.json, next 017.',flush=True)

assert git('rev-parse','HEAD').decode().strip()==head and not git('diff','--cached','--name-only','-z')
command('stage-command.json',['git','add','-f','--pathspec-from-file='+str(O/'commit-paths.nul'),'--pathspec-file-nul'])
staged=set(filter(None,git('diff','--cached','--name-only','-z').decode().split('\0')))
assert staged==set(relative),(staged-set(relative),set(relative)-staged)
command('staged-diff-check.json',['git','diff','--cached','--check'])
# Batch all staged object reads, preserving evidence bytes without hundreds of subprocesses.
specs=[':'+p for p in relative]
data=subprocess.check_output(['git','cat-file','--batch'],cwd=R,input=('\n'.join(specs)+'\n').encode('utf-8'))
import io
stream=io.BytesIO(data); received={}
for p in relative:
    oid,kind,size=stream.readline().decode().split(); assert kind=='blob'
    blob=stream.read(int(size)); assert stream.read(1)==b'\n'
    raw=(R/p).read_bytes()
    if '/evidence/' in p or '/manager-evidence/' in p or p.endswith(('/report.json','/manager.json')):
        assert blob==raw,p
    else:
        assert blob==raw or blob==raw.replace(b'\r\n',b'\n'),p
    received[p]={'blob':oid,'sha256':sha(R/p),'raw_equals_blob':blob==raw}
assert not stream.read()
save('stage.json',{'head':head,'exact_count':len(relative),'products_staged':0,'paths':received})
assert git('rev-parse','HEAD').decode().strip()==head
assert set(filter(None,git('diff','--cached','--name-only','-z').decode().split('\0')))==set(relative)
assert all(sha(R/p)==h for p,h in source.items()) and all(sha(R/p)==v['sha256'] for p,v in received.items())
assert [p for p in relative if p.startswith('기억/layer1/')]==['기억/layer1/M-0566.md']
assert sorted((R/'기억/layer1').glob('M-*.md'))[-1].name=='M-0566.md'
command('pre-commit-status.json',['git','status','--short','--untracked-files=no'])
(O/'commit-message.txt').write_text('T4 fixture와 과거 입력을 검수하고 전체 연결 검증을 배정함\n',encoding='utf-8')
command('commit.json',['git','commit','--file',str(O/'commit-message.txt')])
newhead=git('rev-parse','HEAD').decode().strip()
committed=set(filter(None,git('diff-tree','--no-commit-id','--name-only','-r','-z',newhead).decode().split('\0')))
assert committed==set(relative)
tree=git('ls-tree','-r','-z',newhead)
blobs={entry.split(b'\t',1)[1].decode('utf-8'):entry.split(b'\t',1)[0].decode().split()[2] for entry in tree.split(b'\0') if entry}
assert all(blobs[p]==v['blob'] for p,v in received.items())
assert all(sha(R/p)==v['sha256'] for p,v in received.items()) and all(sha(R/p)==h for p,h in source.items())
assert not git('diff','--cached','--name-only','-z')
save('post-commit.json',{'head':newhead,'parent':head,'committed_count':len(relative),'products_staged':0,'products_deferred':22,
    'source_raw_bytes_unchanged':True,'task_raw_bytes_preserved':True,'index_empty':True,'manager_sha256':pending_hash,'next':'017','push_performed':False})
print(json.dumps({'head':newhead,'committed':len(relative),'products_staged':0,'products_deferred':22,'handoff':'PASS 016','next':'017'},ensure_ascii=False))

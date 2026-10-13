"""Preserve partial work, publish validated handoff, commit management files only."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

R=Path('C:/math'); RUN=R/'docs/do-math/continuous-development-2026-10-13'
O=Path(__file__).resolve().parent; T=RUN/'phases/015/tasks/t4-adapter-report'; E=T/'evidence'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,v): (O/name).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def git(*args): return subprocess.check_output(['git',*args],cwd=R)
def command(name,args):
    p=subprocess.run(args,cwd=R,capture_output=True)
    row={'argv':args,'cwd':str(R),'exit_code':p.returncode,'stdout':p.stdout.decode('utf-8',errors='replace'),'stderr':p.stderr.decode('utf-8',errors='replace')}
    save(name,row); assert p.returncode==0,row
    return row

head=git('rev-parse','HEAD').decode().strip()
assert head==read(O/'verification.json')['head'] and not git('diff','--cached','--name-only','-z')
source=read(O/'source-inspected.json'); assert all(sha(R/p)==h for p,h in source.items())
products={v['path'] for v in read(T/'report.json')['changes'] if not v['path'].endswith(('/.timings.json','/.timings-t3.json'))}
assert len(products)==12
old=git('show','HEAD:docs/do-math/continuous-development-2026-10-13/context.md').decode('utf-8-sig').replace('\r\n','\n')
assert old.split('## C2 ')[0]==(RUN/'context.md').read_text(encoding='utf-8').split('## C2 ')[0]
assert 'convention_version: 27' in (R/'기억/세칙.md').read_text(encoding='utf-8')
assert sorted((R/'기억/layer1').glob('M-*.md'))[-1].name=='M-0565.md'

archived={p for p in T.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}
archived.update(R/p for p in products)
entries={}; archive=O/'raw-evidence.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(archived):
        raw=p.read_bytes(); rel=p.relative_to(R).as_posix()
        z.writestr(rel,raw); entries[rel]=hashlib.sha256(raw).hexdigest()
with zipfile.ZipFile(archive) as z:
    assert set(z.namelist())==set(entries)
    assert all(hashlib.sha256(z.read(p)).hexdigest()==h for p,h in entries.items())
print('Preserved '+str(len(entries))+' raw files in '+str(archive.stat().st_size)+' bytes.',flush=True)

paths={RUN/p for p in ('context.md','plan.md','seams.md','phases/015/manager.json','phases/016/phase.json',
       'phases/016/tasks/t4-fixture-repair/objective.md','phases/016/tasks/provenance-baseline/objective.md')}
paths.update({R/'기억/layer1/M-0565.md',R/'기억/색인.md',T/'report.json'})
for name in ('verify.py','prepare.py','finalize.py','verification.json','source-inspected.json','report-check.json',
             'mirror-check.json','skill-only.json','canonical-t4-final-raw-analysis.json','mirror-t4-full-raw-analysis.json',
             'review.md','common-docs.diff','preservation.json','raw-evidence.zip'):
    paths.add(O/name)
# Directly tracked reports remain navigable; all scratch and repeated source files are in the archive.
paths.update(p for p in E.iterdir() if p.is_file() and not p.name.endswith('.started.json') and p.name!='write_report.py')
for directory in E.iterdir():
    if directory.is_dir() and (directory/'report.json').is_file(): paths.add(directory/'report.json')
relative=sorted(p.relative_to(R).as_posix() for p in paths)
assert not set(relative)&products
save('preservation.json',{'archive':archive.relative_to(R).as_posix(),'archive_sha256':sha(archive),
     'archive_bytes':archive.stat().st_size,'entries':entries,'products_deferred':sorted(products),'product_count':12,
     'tracked_paths':relative,'raw_bytes':'All original task evidence and 12 pending product files are archived with SHA256; originals are untouched. Evidence/report/manager blobs are checked against raw bytes.',
     'local_only':'Unselected scratch, repeated source trees and command raw paths remain local at original locations; their bytes are tracked in raw-evidence.zip. Stage/commit receipts and session logs remain local and may be removed by later cleanup. Archive is not a restoration instruction.',
     'scope':'Management handoff, selected evidence and one memory only. All 12 product paths and four timing caches remain unstaged pending T4 connection validation. No old untracked, engine, operator or unrelated memory files are staged.'})
pending=RUN/'phases/015/manager.pending.json'; published=RUN/'phases/015/manager.json'
assert pending.exists() and not published.exists()
hashes={p:sha(R/p) for p in relative if not p.endswith('/manager.json')}
save('commit-plan.json',{'head':head,'paths':relative,'sha256':hashes,'products_staged':0,'products_deferred':sorted(products)})
(O/'commit-paths.nul').write_bytes(b'\0'.join(p.encode('utf-8') for p in relative)+b'\0')
command('memory-check.json',[sys.executable,'-B','기억/scripts/validate_memory_index.py'])
command('handoff-check.json',[sys.executable,'-B','services/continuous-development/check.py','handoff',str(R),str(RUN),'015'])
assert all(sha(R/p)==h for p,h in hashes.items())
pending_hash=sha(pending); pending.rename(published); assert sha(published)==pending_hash
print('PASS memory/handoff 015; manager.json published.',flush=True)

assert git('rev-parse','HEAD').decode().strip()==head and not git('diff','--cached','--name-only','-z')
command('stage-command.json',['git','add','-f','--pathspec-from-file='+str(O/'commit-paths.nul'),'--pathspec-file-nul'])
staged=set(filter(None,git('diff','--cached','--name-only','-z').decode().split('\0')))
assert staged==set(relative),(staged-set(relative),set(relative)-staged)
command('staged-diff-check.json',['git','diff','--cached','--check'])
received={}
for p in relative:
    raw=(R/p).read_bytes(); blob=git('rev-parse',':'+p).decode().strip(); data=git('show',':'+p)
    clean=subprocess.check_output(['git','hash-object','--path='+p,'--stdin'],cwd=R,input=raw).decode().strip()
    assert clean==blob,p
    if '/evidence/' in p or '/manager-evidence/' in p or p.endswith(('/report.json','/manager.json')): assert data==raw,p
    received[p]={'sha256':hashlib.sha256(raw).hexdigest(),'blob':blob,'raw_equals_blob':data==raw}
save('stage.json',{'head':head,'exact_count':len(relative),'products_staged':0,'paths':received})
assert git('rev-parse','HEAD').decode().strip()==head
assert set(filter(None,git('diff','--cached','--name-only','-z').decode().split('\0')))==set(relative)
assert all(sha(R/p)==h for p,h in source.items())
assert all(sha(R/p)==v['sha256'] for p,v in received.items())
assert [p for p in relative if p.startswith('기억/layer1/')]==['기억/layer1/M-0565.md']
command('pre-commit-status.json',['git','status','--short','--untracked-files=no'])
(O/'commit-message.txt').write_text('T4 측정 성과를 검수하고 경계 수리와 비교 입력 준비를 배정함\n',encoding='utf-8')
command('commit.json',['git','commit','--file',str(O/'commit-message.txt')])
newhead=git('rev-parse','HEAD').decode().strip()
committed=set(filter(None,git('diff-tree','--no-commit-id','--name-only','-r','-z',newhead).decode().split('\0')))
assert committed==set(relative)
assert all(git('rev-parse',newhead+':'+p).decode().strip()==v['blob'] for p,v in received.items())
assert all(sha(R/p)==v['sha256'] for p,v in received.items()) and all(sha(R/p)==h for p,h in source.items())
assert not git('diff','--cached','--name-only','-z')
save('post-commit.json',{'head':newhead,'parent':head,'committed_count':len(relative),'products_staged':0,
     'products_deferred':12,'source_raw_bytes_unchanged':True,'index_empty':True,'manager_sha256':pending_hash,'next':'016','push_performed':False})
print(json.dumps({'head':newhead,'committed':len(relative),'products_staged':0,'products_deferred':12,'handoff':'PASS 015','next':'016'},ensure_ascii=False))

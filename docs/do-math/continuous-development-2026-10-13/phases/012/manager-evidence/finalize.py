from pathlib import Path
import hashlib
import json
import subprocess
import sys
import zipfile

ROOT=Path('C:/math')
RUN=ROOT/'docs/do-math/continuous-development-2026-10-13'
OUT=Path(__file__).resolve().parent
TASK=RUN/'phases/012/tasks/lean-smoke'
E=TASK/'evidence'
def read(p): return json.loads(p.read_bytes())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,v): (OUT/name).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def git(*args): return subprocess.check_output(['git',*args],cwd=ROOT)
def command(name,argv):
    p=subprocess.run(argv,cwd=ROOT,capture_output=True)
    save(name,{'argv':argv,'cwd':str(ROOT),'exit_code':p.returncode,'stdout':p.stdout.decode('utf-8',errors='replace'),'stderr':p.stderr.decode('utf-8',errors='replace')})
    assert p.returncode==0,(name,p.returncode,p.stderr.decode(errors='replace'))

head=git('rev-parse','HEAD').decode().strip()
assert head==read(OUT/'verification.json')['head']
assert not git('diff','--cached','--name-only','-z')
source=read(OUT/'source-inspected.json')
assert all(sha(ROOT/p)==h for p,h in source.items())
products={row['path'] for row in read(TASK/'report.json')['changes'] if not row['path'].endswith('/.timings.json')}
assert len(products)==20
archived={p for p in TASK.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}
archived.update(ROOT/p for p in products)
archive=OUT/'raw-evidence.zip'; entries={}
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(archived):
        rel=p.relative_to(ROOT).as_posix(); raw=p.read_bytes()
        z.writestr(rel,raw); entries[rel]=hashlib.sha256(raw).hexdigest()
with zipfile.ZipFile(archive) as z:
    assert set(z.namelist())==set(entries)
    assert all(hashlib.sha256(z.read(p)).hexdigest()==h for p,h in entries.items())

paths={ROOT/p for p in products}
paths.update(RUN/name for name in ('context.md','plan.md','seams.md','phases/012/manager.json','phases/013/phase.json','phases/013/tasks/scheduler-smoke/objective.md'))
paths.update({ROOT/'기억/layer1/M-0562.md',ROOT/'기억/색인.md',TASK/'report.json'})
for name in ('verify.py','prepare.py','finalize.py','verification.json','source-inspected.json','git-clean-observation.json','report-check.json','report-check.stdout.log','report-check.stderr.log','mirror-check.json','mirror-check.stdout.log','mirror-check.stderr.log','review.md','common-docs.diff','raw-evidence.zip','preservation.json'):
    paths.add(OUT/name)
for name in ('review.md','task_tools.py','verification-final.json','source-start.json','source-final.json','start-comparison.json','live-final-observation.json','mirror-live-observation.json','corpus-start.json','corpus-final.json','corpus-promotion.json','history-b38.stdout','b38-review.json','b38-tracking.json','history-original-reports.json','host-version-inputs.json','mirror-plan-initial.json','mirror-plan-cache.json'):
    paths.add(E/name)
for label in ('live-01','live-02','live-final','canonical-related','mirror-live','mirror-related'):
    paths.add(E/label/'report.json')
for label in ('live-01','live-02','live-final','t5-list','canonical-related','mirror-build','mirror-live','mirror-related','mirror-cache-build','mirror-check','skill-only','lake-version'):
    for suffix in ('.command.json','.stdout','.stderr'):
        paths.add(E/(label+suffix))
relative=sorted(p.relative_to(ROOT).as_posix() for p in paths)
save('preservation.json',{'archive':archive.relative_to(ROOT).as_posix(),'archive_sha256':sha(archive),'archive_bytes':archive.stat().st_size,'entries':entries,'products':sorted(products),'product_count':len(products),'tracked_paths':relative,'raw_report_bytes':'Task report/evidence originals are untouched. Every archive entry is checked by SHA256. Selected raw evidence blobs must equal working bytes.','product_line_endings':'Existing Git LF attributes apply to product text; raw working bytes remain in archive and source hashes. Corpus blobs must preserve raw bytes exactly.','local_only':'Unselected task evidence paths are preserved inside archive but remain local at their original paths. Stage/commit receipts and session logs are local and may be removed by later cleanup. Archive is not an instruction to restore deleted files.','scope':'No timing cache, unrelated operator/product edits, engine files, old scratch or other memories are staged.'})
pending=RUN/'phases/012/manager.pending.json'
assert pending.exists() and not (RUN/'phases/012/manager.json').exists()
hashes={p:sha(ROOT/p) for p in relative if not p.endswith('/manager.json')}
save('commit-plan.json',{'head':head,'paths':relative,'sha256':hashes,'products':len(products)})
(OUT/'commit-paths.nul').write_bytes(b'\0'.join(p.encode('utf-8') for p in relative)+b'\0')
command('memory-check.json',[sys.executable,'-B',str(ROOT/'기억/scripts/validate_memory_index.py')])
command('handoff-check.json',[sys.executable,'-B',str(ROOT/'services/continuous-development/check.py'),'handoff',str(ROOT),str(RUN),'012'])
pending_hash=sha(pending)
assert all(sha(ROOT/p)==h for p,h in hashes.items())
pending.rename(RUN/'phases/012/manager.json')
assert sha(RUN/'phases/012/manager.json')==pending_hash
print('PASS memory and handoff 012; manager published. Exact stage/commit follows.',flush=True)

assert git('rev-parse','HEAD').decode().strip()==head
assert not git('diff','--cached','--name-only','-z')
command('stage-command.json',['git','add','-f','--pathspec-from-file='+str(OUT/'commit-paths.nul'),'--pathspec-file-nul'])
staged_paths=set(filter(None,git('diff','--cached','--name-only','-z').decode('utf-8').split('\0')))
assert staged_paths==set(relative),(sorted(staged_paths-set(relative)),sorted(set(relative)-staged_paths))
command('staged-diff-check.json',['git','diff','--cached','--check'])
staged={}
for p in relative:
    raw=(ROOT/p).read_bytes()
    clean=subprocess.check_output(['git','hash-object','--path='+p,'--stdin'],cwd=ROOT,input=raw).decode().strip()
    blob=git('rev-parse',':'+p).decode().strip()
    assert clean==blob,p
    received=git('show',':'+p)
    if '/evidence/' in p or '/manager-evidence/' in p or '/tests/corpus/' in p or p.endswith(('/report.json','/manager.json')):
        assert received==raw,p
    if p in products:
        assert received.replace(b'\r\n',b'\n')==raw.replace(b'\r\n',b'\n'),p
    staged[p]={'sha256':hashlib.sha256(raw).hexdigest(),'blob':blob,'raw_equals_blob':received==raw}
save('stage.json',{'head':head,'paths':staged,'exact_count':len(relative),'product_count':len(products)})
assert git('rev-parse','HEAD').decode().strip()==head
assert set(filter(None,git('diff','--cached','--name-only','-z').decode('utf-8').split('\0')))==set(relative)
assert all(sha(ROOT/p)==v['sha256'] for p,v in staged.items())
assert all(sha(ROOT/p)==h for p,h in source.items())
assert len([p for p in relative if p.startswith('기억/layer1/')])==1
(OUT/'commit-message.txt').write_text('Lean 실연쇄를 검수하고 시험 전용 예약 경계를 배정함\n',encoding='utf-8')
command('commit.json',['git','commit','--file',str(OUT/'commit-message.txt')])
newhead=git('rev-parse','HEAD').decode().strip()
committed=set(filter(None,git('diff-tree','--no-commit-id','--name-only','-r','-z',newhead).decode('utf-8').split('\0')))
assert committed==set(relative)
assert all(git('rev-parse',newhead+':'+p).decode().strip()==v['blob'] for p,v in staged.items())
assert all(sha(ROOT/p)==v['sha256'] for p,v in staged.items())
assert all(sha(ROOT/p)==h for p,h in source.items())
assert not git('diff','--cached','--name-only','-z')
save('post-commit.json',{'head':newhead,'parent':head,'committed_count':len(relative),'products':len(products),'source_raw_bytes_unchanged':True,'index_empty':True,'manager_sha256':pending_hash,'next':'013','push_performed':False})
print(json.dumps({'head':newhead,'committed':len(relative),'products':len(products),'handoff':'PASS 012','next':'013'},ensure_ascii=False))

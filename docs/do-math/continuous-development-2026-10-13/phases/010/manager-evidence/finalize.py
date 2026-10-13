"""Check and publish the manager handoff, then commit only its explicit file set."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path('C:/math')
RUN=ROOT/'docs/do-math/continuous-development-2026-10-13'
OUT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='')
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def command(name,argv):
    p=subprocess.run(argv,cwd=ROOT,capture_output=True)
    save(name,{'argv':argv,'exit_code':p.returncode,'stdout':p.stdout.decode('utf-8',errors='replace'),'stderr':p.stderr.decode('utf-8',errors='replace')})
    assert p.returncode==0,(name,p.returncode,p.stderr.decode('utf-8',errors='replace'))
    return p.stdout

head=git('rev-parse','HEAD').decode().strip()
assert head==read(OUT/'verification.json')['head']
assert not git('diff','--cached','--name-only','-z')
source=read(OUT/'source-inspected.json')
assert all(sha(ROOT/p)==h for p,h in source.items())
assert not (RUN/'phases/010/manager.json').exists()
assert (ROOT/'기억/layer1/M-0560.md').is_file() and not (ROOT/'기억/layer1/M-0561.md').exists()

# Check the historical raw reports used to bound the reuse decision.
history=[]
for row in read(RUN/'phases/010/tasks/host-smoke/evidence/history-existing-reports.json'):
    p=ROOT/row['path']; data=read(p)
    assert sha(p)==row['sha256'] and data['counts']==row['counts']
    rows=[r for g in data['reports'] for r in g['rows']]
    assert all(r in rows for r in row['relevant_rows'])
    history.append({'path':row['path'],'sha256':sha(p),'counts':data['counts'],'relevant_rows':len(row['relevant_rows'])})
save('history-verification.json',history)

paths={RUN/'context.md',RUN/'plan.md',RUN/'seams.md',RUN/'phases/010/manager.json',
       RUN/'phases/011/phase.json',RUN/'phases/011/tasks/regression-reading/objective.md',
       ROOT/'기억/layer1/M-0560.md',ROOT/'기억/색인.md'}
for name in ('verify.py','prepare.py','finalize.py','verification.json','report-checks.json','source-inspected.json',
             'review.md','common-docs.diff','raw-evidence.zip','preservation.json','history-verification.json'):
    paths.add(OUT/name)
for task in ('host-smoke','reading-limits'):
    base=RUN/'phases/010/tasks'/task
    paths.add(base/'report.json')
    evidence=base/'evidence'
    names=(['review.md','source-start.json','source-end.json','verification.json','baseline-manifest.json',
            'call-jobs-diagnosis.json','history-existing-reports.json','history-91d59a80.diff','history-62b7c220.diff',
            'history-b484771e.diff','mirror-plan.json','cache-plan.json','mirror-check.stdout.log','skill-only.stdout.log','t5-list.stdout.log']
           if task=='host-smoke' else ['review.md','reading-boundaries.json','verification.json','sources-start.json',
            'additional-source-start.json','host-snapshot.json','active-tool-contract.json','source-excerpts.json',
            'fixture-manifest.json','fixture-capped-results.json','fixture-page-results.json','fixture-aggregate-results.json',
            'fixture-verification.json','claude-static-read-details.json','claude-read-binding.json','claude-read-implementation.json',
            'settings-supplement.json','public-sources.json'])
    paths.update(evidence/name for name in names)
    if task=='host-smoke':
        for label in ('host-01','host-02','host-final','related','mirror-host','baseline-repro-02'):
            paths.add(evidence/(label+'-results/report.json'))
            for suffix in ('.command.json','.stdout.log','.stderr.log'):
                paths.add(evidence/(label+suffix))
        for label in ('mirror-build','cache-sync','mirror-check','skill-only'):
            paths.add(evidence/(label+'.command.json'))

relative=sorted(p.relative_to(ROOT).as_posix() for p in paths)
assert not any(p.startswith(('.claude/','.agents/','services/')) for p in relative)
pending=RUN/'phases/010/manager.pending.json'
hashes={p:sha(ROOT/p) for p in relative if not p.endswith('/manager.json')}
save('commit-plan.json',{'head':head,'paths':relative,'sha256':hashes,'products':0})
(OUT/'commit-paths.nul').write_bytes(b'\0'.join(p.encode('utf-8') for p in relative)+b'\0')

command('memory-check.json',[sys.executable,'-B',str(ROOT/'기억/scripts/validate_memory_index.py')])
command('handoff-check.json',[sys.executable,'-B',str(ROOT/'services/continuous-development/check.py'),'handoff',str(ROOT),str(RUN),'010'])
pending_hash=sha(pending)
assert all(sha(ROOT/p)==h for p,h in hashes.items())
pending.rename(RUN/'phases/010/manager.json')
assert sha(RUN/'phases/010/manager.json')==pending_hash

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
    if '/evidence/' in p or '/manager-evidence/' in p or p.endswith(('/report.json','/manager.json')):
        assert git('show',':'+p)==raw,p
    staged[p]={'sha256':hashlib.sha256(raw).hexdigest(),'blob':blob}
save('stage.json',{'head':head,'paths':staged,'exact_count':len(relative),'product_count':0})
assert git('rev-parse','HEAD').decode().strip()==head
assert set(filter(None,git('diff','--cached','--name-only','-z').decode('utf-8').split('\0')))==set(relative)
assert all(sha(ROOT/p)==v['sha256'] for p,v in staged.items())
assert all(sha(ROOT/p)==h for p,h in source.items())
(OUT/'commit-message.txt').write_text('실제 host 부분 성과와 읽기 한도 조사를 검수하고 회귀 수리를 배정함\n',encoding='utf-8',newline='')
command('commit.json',['git','commit','--file',str(OUT/'commit-message.txt')])
newhead=git('rev-parse','HEAD').decode().strip()
committed=set(filter(None,git('diff-tree','--no-commit-id','--name-only','-r','-z',newhead).decode('utf-8').split('\0')))
assert committed==set(relative)
assert all(git('rev-parse',newhead+':'+p).decode().strip()==v['blob'] for p,v in staged.items())
assert all(sha(ROOT/p)==v['sha256'] for p,v in staged.items())
assert all(sha(ROOT/p)==h for p,h in source.items())
assert not git('diff','--cached','--name-only','-z')
save('post-commit.json',{'head':newhead,'parent':head,'committed_count':len(relative),'products':0,
    'source_raw_bytes_unchanged':True,'index_empty':True,'manager_sha256':pending_hash,'next':'011','push_performed':False})
print(json.dumps({'head':newhead,'committed':len(relative),'products':0,'handoff':'PASS 010','next':'011'},ensure_ascii=False))

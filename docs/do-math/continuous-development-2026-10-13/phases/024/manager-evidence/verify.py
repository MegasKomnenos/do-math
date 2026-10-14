"""Manager's independent read-only checks of phase 024 original artifacts."""
import ast
from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

R = Path('C:/math')
RUN = R/'docs/do-math/continuous-development-2026-10-13'
O = Path(__file__).resolve().parent
T = RUN/'phases/024/tasks/document-waits'
E = T/'evidence'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,v): (O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def git(*a,data=None): return subprocess.check_output(['git',*a],cwd=R,input=data)
def inventory(root): return {p.relative_to(root).as_posix():sha(p) for p in root.rglob('*') if p.is_file()}

cmd=[sys.executable,'-B','services/continuous-development/check.py','report',str(R),str(RUN),'024',T.name]
p=subprocess.run(cmd,cwd=R,capture_output=True)
save('report-check.json',dict(argv=cmd,exit_code=p.returncode,stdout=p.stdout.decode(),stderr=p.stderr.decode()))
assert p.returncode==0
original=inventory(T)
start,end=read(E/'start.json'),read(E/'final.json')
current={p.relative_to(R).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size}
 for root in ('.claude/skills','.agents/skills','.agents/diff') for p in (R/root).rglob('*')
 if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}
assert current==end
assert {p:v['sha256'] for p,v in start.items()}==read(RUN/'phases/023/manager-evidence/source-inspected.json')
save('source-inspected.json',{p:v['sha256'] for p,v in current.items()})
report=read(T/'report.json')
changes=sorted(p for p in start.keys()|end.keys() if start.get(p)!=end.get(p))
assert changes==sorted(x['path'] for x in report['changes'])
assert set(changes)<=set(read(RUN/'phases/024/phase.json')['tasks'][0]['writes'])
assert all(start[p]==end[p] for p in start if '/do_math/' in p)
receipts=[]
for check in report['checks']:
 ref=next(x for x in check['evidence'] if x.endswith('-process.json'))
 row=read(RUN/ref[4:])
 assert row['exit_code']==check['exit_code'] and row['pid']>0 and row['start']<row['end']
 receipts.append(dict(reference=ref,exit_code=row['exit_code'],result=check['result']))
suites={}; rows_by={}
expected={'red':{'failed':1},'focus':{'passed':42,'failed':2,'error':1},'corrected':{'passed':3,'failed':1},
 'c':{'passed':148,'error':19,'not_run':62,'failed':25},'c2':{'passed':254},'m':{'passed':254},'cwd':{'passed':1}}
for label,counts in expected.items():
 result=read(E/label/'report.json'); rows=[r for g in result['reports'] for r in g['rows'] if not r.get('fixture')]
 ids=[r['id'] for r in rows]; code=int(label in ('red','focus','corrected','c'))
 assert len(ids)==len(set(ids))==len(result['selected']) and set(ids)==set(result['selected'])
 assert dict(Counter(r['outcome'] for r in rows))==result['counts']==counts
 assert result['complete'] and not result['changed_during_run'] and result['successful']==(code==0)
 if label!='cwd': assert read(E/(label+'-process.json'))['exit_code']==code
 rows_by[label]={r['id']:r for r in rows}
 suites[label]=dict(selected=len(ids),counts=counts,exit_code=code,nonpassed=[r for r in rows if r['outcome']!='passed'])
 if label in ('c2','m'):
  tree='.claude' if label=='c2' else '.agents'; scripts=R/tree/'skills/do-math/scripts'
  sources={p.relative_to(scripts).as_posix():sha(p) for p in scripts.rglob('*.py') if '__pycache__' not in p.parts}
  assert sources==result['source_sha256']
  b,a=read(E/(label+'-before.json')),read(E/(label+'-after.json'))
  delta=[p for p in b.keys()|a.keys() if b.get(p)!=a.get(p)]
  assert all(Path(p).name in ('.timings.json','.timings-t3.json') for p in delta)
  assert all(current[p]==v for p,v in a.items() if p.startswith(tree+'/') and Path(p).name not in ('.timings.json','.timings-t3.json'))
  suites[label].update(python_files=len(sources),source_changes=delta)
assert rows_by['c'].keys()==rows_by['c2'].keys()==rows_by['m'].keys()
assert read(E/'c/report.json')['source_sha256']==read(E/'c2/report.json')['source_sha256']
failures=[]
for label in ('red','focus','corrected','c'):
 for tid,row in rows_by[label].items():
  if row['outcome']=='passed': continue
  assert rows_by['c2'][tid]['outcome']==rows_by['m'][tid]['outcome']=='passed'
  failures.append(dict(suite=label,id=tid,original=row['outcome'],final='passed'))
assert (E/'red.stderr').read_text(encoding='utf-8').count('AssertionError: ValueError not raised')==2
save('failure-mapping.json',failures)
observations={}
for label in ('c2','m'):
 obs=read(E/(label+'-observations.json')); assert obs['exit_code']==0
 props=[]; samples=[]
 for row in obs['final_proposals']:
  value=read(E/row['file'])['context']; proposal=value['role_review']['proposal']
  def count(n):
   if isinstance(n,dict): return int(n==proposal)+sum(count(v) for v in n.values())
   if isinstance(n,list): return sum(count(v) for v in n)
   return 0
  assert count(value)==row['proposal_count']==1
  props.append(dict(file=row['file'],sha256=sha(E/row['file']),count=1))
 for row in obs['actual_returns']:
  if row['kind']=='settle':
   action=row['action']; pending=any(a.get('role')=='task_contract_review' for a in row['queue'])
   eligible=not action.get('requested_by') and not action.get('recovery') and pending
   if eligible:
    elapsed=(datetime.fromisoformat(row['now'])-datetime.fromisoformat(action['settle_started_at'])).total_seconds()
    assert row['result']==(elapsed<row['limit'])
    if row['result']: assert action['dispatch_wait']=={'kind':'plan_settle','since':action['settle_started_at'],'limit_seconds':row['limit']}
   else: assert row['result'] is False
  if row['kind']=='dispatch' and row['result']: assert 'dispatch_wait' not in row['action']
  if row['kind']=='condition' and row['decision'] is not None and row['result']['state']=='ready':
   change=row['decision']['change']; value=change.get('value',change); expected_value=row['condition']['value']
   assert type(value) is type(expected_value) and value==expected_value
  samples.append(row)
 assert len(samples)==107 and len(props)==18
 observations[label]=dict(returns=len(samples),kinds=dict(Counter(r['kind'] for r in samples)),proposals=props,raw_sha256=sha(E/(label+'-observations.json')))
save('return-check.json',observations)
pres=read(E/'preservation.json')
for name in ('runtime_and_live_inputs','fixed_runtime_and_t4_paths'):
 assert all(current[p]==start[p] for p in pres[name])
for path,digest in pres['tools'].items(): assert sha(path)==digest
for row in pres['host_recordings']: assert sha(RUN/row['path'])==row['sha256']
for row in pres['corpus']:
 path=row['path']; raw=(R/path).read_bytes()
 assert current[path]==start[path] and sha(R/path)==row['sha256']
 blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
 assert git('hash-object','--path='+path,'--stdin',data=raw).decode().strip()==blob==row['raw_git_blob']==row['clean_git_blob']
for row in pres['explicit_sha']: assert sha(R/row['tree']/'skills/do-math/scripts/tests/corpus'/row['path'])==row['sha256']
baseline=read(RUN/'phases/018/tasks/job-cleanup/evidence/final-baseline.json')
for row in baseline['files']:
 raw=(Path(baseline['baseline'])/row['path']).read_bytes()
 assert hashlib.sha256(raw).hexdigest()==row['sha256']
 assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob']
history=[]; hv=read(E/'history-verification.json')
for group in hv['ast_history']:
 for row in group['reports']:
  assert row['exists'] and sha(R/row['path'])==row['sha256']==row['expected_sha256']
  history.append(dict(id=group['id'],path=row['path'],sha256=row['sha256']))
save('history-check.json',history)
def funcs(raw):
 text=raw.decode('utf-8-sig'); lines=text.splitlines(keepends=True)
 return {n.name:''.join(lines[n.lineno-1:n.end_lineno]) for n in ast.parse(text).body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
for rel,allowed in [('doc_code.py',{'field_schemas','scoped_field_issues'}),('engine_context.py',set())]:
 path=Path('.claude/skills/do-math/scripts/tests/support')/rel
 with zipfile.ZipFile(RUN/'phases/023/manager-evidence/raw-evidence.zip') as archive:
  raw=archive.read(path.as_posix())
 assert hashlib.sha256(raw).hexdigest()==start[path.as_posix()]['sha256']
 old,new=funcs(raw),funcs((R/path).read_bytes())
 assert all(k in new and v==new[k] for k,v in old.items() if k not in allowed)
for label in ('mirror-build','final-cache-sync','final-mirror-check','skill-only'): assert read(E/(label+'-process.json'))['exit_code']==0
assert 'verified' in (E/'skill-only.stdout').read_text(encoding='utf-8')
cwd=read(E/'resource-cwd-confirmed.json'); assert cwd['worker_exit_code']==0 and cwd['cwd_lengths']==[141,141]
audit=[json.loads(line) for p in E.glob('cwd-audit-*.jsonl') for line in p.read_text(encoding='utf-8').splitlines()]
assert all(row in audit for row in cwd['resource_cli_calls'])
prior=read(RUN/'phases/023/manager-evidence/task-files.json')
assert all(sha(RUN/'phases/023/tasks/document-governance'/p)==h for p,h in prior.items())
assert original==inventory(T)
save('task-files.json',original)
products=[p for p in changes if Path(p).name not in ('.timings.json','.timings-t3.json')]
save('product-paths.json',products)
save('verification.json',dict(head=git('rev-parse','HEAD').decode().strip(),sources=len(current),start_equal_previous=True,current_equal_final=True,
 changes=changes,outside_writes=[],receipts=receipts,suites={k:{f:v[f] for f in v if f!='nonpassed'} for k,v in suites.items()},
 products_to_commit=len(products),runtime_unchanged=True,original_task_files_unchanged=len(original),previous_task_files_unchanged=len(prior),
 actual_returns=observations,preservation=dict(runtime_inputs=len(pres['runtime_and_live_inputs']),fixed_boundary_paths=len(pres['fixed_runtime_and_t4_paths']),
 corpus_paths=len(pres['corpus']),explicit_sha=len(pres['explicit_sha']),host_recordings=len(pres['host_recordings']),tools=len(pres['tools']),baseline_files=len(baseline['files'])),actual_cwd_lengths=cwd['cwd_lengths']))
print(json.dumps(dict(sources=len(current),changes=len(changes),products=len(products),task_files=len(original),suites={k:v['counts'] for k,v in suites.items()})))

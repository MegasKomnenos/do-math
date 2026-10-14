"""Read-only manager recheck. Never re-execute or modify task evidence."""
from collections import Counter
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys

R = Path('C:/math')
RUN = R / 'docs/do-math/continuous-development-2026-10-13'
O = Path(__file__).resolve().parent
T = RUN / 'phases/023/tasks/document-governance'
E = T / 'evidence'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,v): (O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def git(*a,data=None): return subprocess.check_output(['git',*a],cwd=R,input=data)
def inventory(root): return {p.relative_to(root).as_posix():sha(p) for p in root.rglob('*') if p.is_file()}

cmd=[sys.executable,'-B','services/continuous-development/check.py','report',str(R),str(RUN),'023',T.name]
p=subprocess.run(cmd,cwd=R,capture_output=True)
save('report-check.json',dict(argv=cmd,exit_code=p.returncode,stdout=p.stdout.decode(),stderr=p.stderr.decode()))
assert p.returncode == 0
original=inventory(T)
old_log=RUN/'phases/023/logs/manager.log'
old_log_sha=sha(old_log)
assert not (RUN/'phases/023/manager.json').exists()
assert '503' in old_log.read_text(encoding='utf-8') and 'at capacity' in old_log.read_text(encoding='utf-8')
save('restart-state.json',dict(previous_log_sha256=old_log_sha,previous_log_bytes=old_log.stat().st_size,
    prior_manager_submission_exists=False,prior_manager_evidence_existed=False,
    restart_log='run:phases/023/logs/manager-restart-001.log',task_reexecuted=False,
    head=git('rev-parse','HEAD').decode().strip()))
start,end=read(E/'start.json'),read(E/'final.json')
current={p.relative_to(R).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size}
 for root in ('.claude/skills','.agents/skills','.agents/diff') for p in (R/root).rglob('*')
 if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}
assert current == end
assert {p:v['sha256'] for p,v in start.items()} == read(RUN/'phases/022/manager-evidence/source-inspected.json')
save('source-inspected.json',{p:v['sha256'] for p,v in current.items()})
report=read(T/'report.json')
changes=sorted(p for p in start.keys()|end.keys() if start.get(p)!=end.get(p))
assert changes==sorted(x['path'] for x in report['changes'])
assert set(changes)<=set(read(RUN/'phases/023/phase.json')['tasks'][0]['writes'])
assert all(start[p]==end[p] for p in start if '/do-math/' in p and (p.endswith('.md') or '/do_math/' in p))
receipts=[]
for check in report['checks']:
 ref=next(x for x in check['evidence'] if x.endswith('-process.json'))
 row=read(RUN/ref[4:])
 assert row['exit_code']==check['exit_code'] and row['pid']>0 and row['start']<row['end']
 receipts.append(dict(reference=ref,exit_code=row['exit_code'],result=check['result']))
suites={}; rows_by={}
expected={'red':{'failed':1},'focus':{'passed':38,'failed':3},'corrected':{'passed':3},
 'c':{'passed':456,'skipped':1,'error':3},'c2':{'passed':459,'skipped':1},'m':{'passed':459,'skipped':1}}
for label,counts in expected.items():
 result=read(E/label/'report.json'); rows=[r for g in result['reports'] for r in g['rows'] if not r.get('fixture')]
 ids=[r['id'] for r in rows]; code=int(label in ('red','focus','c'))
 assert len(ids)==len(set(ids))==len(result['selected']) and set(ids)==set(result['selected'])
 assert dict(Counter(r['outcome'] for r in rows))==result['counts']==counts
 assert result['complete'] and not result['changed_during_run'] and result['successful']==(code==0)
 assert read(E/(label+'-process.json'))['exit_code']==code
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
  skip=suites[label]['nonpassed']; assert len(skip)==1 and '1314' in str(skip[0]['details'])
  assert skip[0]['id']=='unit.test_context_catalog.ContextStoreTests.test_outside_symlink_is_reported_when_supported'
  suites[label].update(python_files=len(sources),source_changes=delta)
assert rows_by['c'].keys()==rows_by['c2'].keys()==rows_by['m'].keys()
assert read(E/'c/report.json')['source_sha256']==read(E/'c2/report.json')['source_sha256']
failures=[]
for label in ('red','focus','c'):
 for tid,row in rows_by[label].items():
  if row['outcome'] not in ('failed','error'): continue
  assert rows_by['c2'][tid]['outcome']==rows_by['m'][tid]['outcome']=='passed'
  failures.append(dict(suite=label,id=tid,original=row['outcome'],final='passed'))
assert (E/'red.stderr').read_text(encoding='utf-8').count('AssertionError: ValueError not raised')==4
assert all("KeyError: 'role'" in str(r['details']) and 'run_suite.py' in str(r['details']) for r in suites['c']['nonpassed'] if r['outcome']=='error')
save('failure-mapping.json',failures)
observations={}
sys.path.insert(0,str(R/'.claude/skills/do-math/scripts'))
from do_math.canonical import exact_content_hash
for label in ('c2','m'):
 obs=read(E/(label+'-observations.json')); checked=[]; proposals=[]
 assert obs['official_exit_code']==0 and obs['single_proposal']
 for row in obs['checks']:
  value=read(E/row['file']); check=value['check']
  assert check['bundle_sha256']==value['sha256']==row['bundle_sha256']
  assert check['sha256']==row['check_sha256']==exact_content_hash({k:v for k,v in check.items() if k!='sha256'})
  assert check['status']==row['status']
  checked.append(dict(file=row['file'],sha256=sha(E/row['file']),status=check['status']))
 for row in obs['final_returns']:
  value=read(E/row['file'])['context']
  if row['proposal_count'] is None: continue
  proposal=value['role_review']['proposal']
  def count(n):
   if isinstance(n,dict): return int(n==proposal)+sum(count(v) for v in n.values())
   if isinstance(n,list): return sum(count(v) for v in n)
   return 0
  assert count(value)==row['proposal_count']==1
  proposals.append(dict(file=row['file'],sha256=sha(E/row['file']),count=1))
 assert len(proposals)==52 and len(checked)==45 and len(obs['final_returns'])==151 and len(obs['academic_queries'])==517
 assert {r['status'] for r in obs['academic_queries']}=={'not_applicable','incomplete','pending','active','completed','externally_rejected'}
 assert {r['status'] for r in checked}=={'approved','revision_required','unresolved'}
 observations[label]=dict(checks=checked,proposals=proposals,final_returns=151,academic_queries=517,
  academic_states=sorted({r['status'] for r in obs['academic_queries']}))
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
history=[]
hv=read(E/'history-verification.json')
for group in hv['ast_history']:
 for row in group['reports']:
  assert row['exists'] and sha(R/row['path'])==row['sha256']==row['expected_sha256']
  history.append(dict(id=group['id'],path=row['path'],sha256=row['sha256']))
for group in hv['pure_history']:
 row=group['original_board']['report']; assert sha(R/row['path'])==row['sha256']
 history.append(dict(id=group['id'],path=row['path'],sha256=row['sha256']))
save('history-check.json',history)
selection=read(E/'selection-decisions.json')
for row in selection['excluded_previous_modules']:
 path=R/'.claude/skills/do-math/scripts/tests'/Path(row['module'].replace('.','/')+'.py')
 assert sha(path)==row['source_sha256']==start[path.relative_to(R).as_posix()]['sha256']
 assert 'field_schemas' not in path.read_text(encoding='utf-8') and 'scoped_field_issues' not in path.read_text(encoding='utf-8')
def functions(path):
 text=path.read_text(encoding='utf-8-sig'); lines=text.splitlines(keepends=True)
 return {n.name:''.join(lines[n.lineno-1:n.end_lineno]) for n in ast.parse(text).body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
for rel,allowed in [('doc_code.py',{'field_schemas','scoped_field_issues'}),('engine_context.py',set())]:
 path=Path('.claude/skills/do-math/scripts/tests/support')/rel
 old,new=functions(E/'original'/path),functions(R/path)
 assert all(k in new and v==new[k] for k,v in old.items() if k not in allowed)
for label in ('mirror-build','cache-sync','mirror-check','skill-only'): assert read(E/(label+'-process.json'))['exit_code']==0
assert 'verified' in (E/'skill-only.stdout').read_text(encoding='utf-8')
prior=read(RUN/'phases/022/manager-evidence/task-files.json')
assert all(sha(RUN/'phases/022/tasks/review-delivery'/p)==h for p,h in prior.items())
assert original==inventory(T) and sha(old_log)==old_log_sha
save('task-files.json',original)
products=[p for p in changes if Path(p).name not in ('.timings.json','.timings-t3.json')]
save('product-paths.json',products)
save('verification.json',dict(head=git('rev-parse','HEAD').decode().strip(),sources=len(current),
 start_equal_previous=True,current_equal_final=True,changes=changes,outside_writes=[],receipts=receipts,suites=suites,
 failures_resolved=failures,products_to_commit=len(products),runtime_and_documents_unchanged=True,
 original_task_files_unchanged=len(original),previous_task_files_unchanged=len(prior),previous_log_unchanged=True,
 actual_returns={k:dict(returns=v['final_returns'],checks=len(v['checks']),proposals=len(v['proposals']),queries=v['academic_queries']) for k,v in observations.items()},
 preservation=dict(runtime_inputs=len(pres['runtime_and_live_inputs']),fixed_boundary_paths=len(pres['fixed_runtime_and_t4_paths']),
 corpus_paths=len(pres['corpus']),explicit_sha=len(pres['explicit_sha']),host_recordings=len(pres['host_recordings']),tools=len(pres['tools']),baseline_files=len(baseline['files'])),
 excluded_modules_verified=len(selection['excluded_previous_modules'])))
print(json.dumps(dict(sources=len(current),changes=len(changes),products=len(products),task_files=len(original),
 suites={k:{f:v[f] for f in ('selected','counts','exit_code')} for k,v in suites.items()}),ensure_ascii=False))

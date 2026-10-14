"""Independent manager checks; never writes task or product artifacts."""
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys

R=Path('C:/math'); RUN=R/'docs/do-math/continuous-development-2026-10-13'
O=Path(__file__).resolve().parent; T=RUN/'phases/025/tasks/document-trust'; E=T/'evidence'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,v): (O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def git(*a,data=None): return subprocess.check_output(['git',*a],cwd=R,input=data)
def inventory(root): return {p.relative_to(root).as_posix():sha(p) for p in root.rglob('*') if p.is_file()}
cmd=[sys.executable,'-B','services/continuous-development/check.py','report',str(R),str(RUN),'025',T.name]
p=subprocess.run(cmd,cwd=R,capture_output=True)
save('report-check.json',dict(argv=cmd,exit_code=p.returncode,stdout=p.stdout.decode(),stderr=p.stderr.decode()))
assert p.returncode==0
original=inventory(T); start,end=read(E/'start.json'),read(E/'final-delivery.json')
current={p.relative_to(R).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size}
 for root in ('.claude/skills','.agents/skills','.agents/diff') for p in (R/root).rglob('*')
 if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}
assert current==end
assert {p:v['sha256'] for p,v in start.items()}==read(RUN/'phases/024/manager-evidence/source-inspected.json')
save('source-inspected.json',{p:v['sha256'] for p,v in current.items()})
report=read(T/'report.json'); changes=sorted(p for p in start.keys()|end.keys() if start.get(p)!=end.get(p))
assert changes==sorted(x['path'] for x in report['changes'])
assert set(changes)<=set(read(RUN/'phases/025/phase.json')['tasks'][0]['writes'])
assert all(start[p]==end[p] for p in start if '/do_math/' in p)
suites={}; rows_by={}; failures=[]
for label in ('red','focus','c','c2','m'):
 result=read(E/label/'report.json'); rows=[r for g in result['reports'] for r in g['rows'] if not r.get('fixture')]
 ids=[r['id'] for r in rows]; code=int(label in ('red','focus','c')); receipt=read(E/(label+'-process.json'))
 assert len(ids)==len(set(ids))==len(result['selected']) and set(ids)==set(result['selected'])
 counts=dict(Counter(r['outcome'] for r in rows)); assert counts==result['counts']
 assert result['complete'] and not result['changed_during_run'] and result['successful']==(code==0)
 assert receipt['exit_code']==code and receipt['pid']>0 and receipt['start']<receipt['end']
 rows_by[label]={r['id']:r for r in rows}; suites[label]=dict(selected=len(ids),counts=counts,exit_code=code)
 if label in ('c2','m'):
  assert counts=={'passed':185}
  tree='.claude' if label=='c2' else '.agents'; scripts=R/tree/'skills/do-math/scripts'
  sources={p.relative_to(scripts).as_posix():sha(p) for p in scripts.rglob('*.py') if '__pycache__' not in p.parts}
  assert sources==result['source_sha256']
  b,a=read(E/(label+'-before.json')),read(E/(label+'-after.json'))
  delta=[p for p in b.keys()|a.keys() if b.get(p)!=a.get(p)]
  assert all(Path(p).name in ('.timings.json','.timings-t3.json') for p in delta)
  assert all(current[p]==v for p,v in a.items() if p.startswith(tree+'/') and Path(p).name not in ('.timings.json','.timings-t3.json'))
  suites[label].update(python_files=len(sources),source_changes=delta)
assert rows_by['c'].keys()==rows_by['c2'].keys()==rows_by['m'].keys()
for label in ('red','focus','c'):
 for tid,row in rows_by[label].items():
  if row['outcome']=='passed': continue
  assert rows_by['c2'][tid]['outcome']==rows_by['m'][tid]['outcome']=='passed'
  failures.append(dict(suite=label,id=tid,original=row['outcome'],final='passed'))
save('failure-mapping.json',failures)
observations={}
for label in ('c2','m'):
 obs=read(E/(label+'-actual-returns.json'))
 raw=[json.loads(line) for path in sorted((E/('observations-'+label)).glob('*.jsonl')) for line in path.read_text(encoding='utf-8').splitlines()]
 trust=[row for row in raw if row['kind'] in ('project','toolchain','environment_check')]
 assert trust==obs['trust_returns'] and len(trust)==122
 assert dict(Counter(r['kind'] for r in trust))=={'project':40,'toolchain':2,'environment_check':80}
 envs=[r for r in trust if r['kind']=='environment_check']; branches=Counter()
 for row in envs:
  value=row['value']; env=row['environment']; binding=row['input_binding']
  assert value['environment_id']==env['id'] and value['toolchain_record']==env['toolchain_record']
  if value['status']=='verified':
   assert value['errors']==[] and 'changed_files' not in value and 'changed_file_count' not in value
   if 'rebind' in value:
    assert value['rebind']['previous']==binding and value['binding']==value['rebind']['current'] and value['rebind']['recorded_at']
    branches['rebind']+=1
   else:
    assert value['binding']==binding; branches['verified']+=1
  elif 'changed_files' in value:
   assert value['status']=='invalid' and value['errors'][0].startswith('olean fingerprint differs')
   assert len(value['changed_files'])==min(50,value['changed_file_count']); branches['mismatch']+=1
  else:
   assert value['status']=='invalid' and value['errors']; branches['early_invalid']+=1
 assert all(branches[k] for k in ('rebind','verified','mismatch','early_invalid'))
 assert any(r['value'].get('changed_file_count')==55 and r['value']['changed_files']==[f'toolchain/lib/lean/Init/Extra{i:02d}.olean' for i in range(50)] for r in envs)
 toolchains=[r for r in trust if r['kind']=='toolchain']
 assert any(r['value']['project'] is None for r in toolchains)
 lake=next(r['value'] for r in toolchains if r['value']['project'] is not None)
 for row in toolchains:
  value=row['value']; assert value['configured_command']==row['command'] and value['version_exit']==0
  assert sha(value['executable'])==value['sha256'] and sha(value['verifier_path'])==value['verifier_sha256']
  assert all(sha(path)==digest for path,digest in value['executables'].items())
 project=lake['project']; root=Path(project['source_identity']['root']); lean=Path(lake['configured_command'][-1])
 assert project['search_paths']==sorted(str(p) for p in (lean.parents[1]/'lib/lean',lean.parents[1]/'src/lean/lake',root/'.lake/build/lib/lean'))
 manifest={'lake-manifest.json':hashlib.sha256(b'{"packages": []}').hexdigest()}
 assert project['source_identity']['git_tree'] is None and project['source_identity']['untracked_file_count']==2
 assert project['source_identity']['working_diff_hash']==hashlib.sha256(b'').hexdigest()
 encoded=json.dumps(project['manifest_hashes'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
 assert project['source_identity']['untracked_sha256']==hashlib.sha256(encoded).hexdigest()
 errors=[r for r in raw if r['kind']=='observer_error']
 assert len(errors)==24 and errors==obs['optional_packaging_capture_errors']
 assert all(r['target']=='prepared' and 'bytes is not JSON serializable' in r['error'] for r in errors)
 assert obs['final_proposals']==[]
 proposal=[r for r in rows_by[label].values() if r['id'].endswith('.test_review_stage_documents_reach_the_final_seat_input')]
 assert len(proposal)==1 and proposal[0]['outcome']=='passed'
 assert len(obs['installed_jobs'])==5 and all(r['exit_code']==0 and not r['stopped'] for r in obs['installed_jobs'])
 assert [r for r in raw if r['kind']=='job']==obs['job_calls']
 observations[label]=dict(raw_sha256=sha(E/(label+'-actual-returns.json')),returns=len(trust),branches=dict(branches),installed_jobs=5,
  cwd_lengths=sorted({r['characters'] for r in obs['installed_jobs']}),optional_packaging_errors=24,proposal_property=proposal[0]['id'])
save('return-check.json',observations)
pres=read(E/'preservation.json')
for name in ('runtime_and_live_inputs','fixed_runtime_and_t4_paths'): assert all(current[p]==start[p] for p in pres[name])
for path,digest in pres['tools'].items(): assert sha(path)==digest
for row in pres['host_recordings']: assert sha(RUN/row['path'])==row['sha256']
for row in pres['corpus']:
 path=row['path']; raw=(R/path).read_bytes(); assert current[path]==start[path] and sha(R/path)==row['sha256']
 blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
 assert git('hash-object','--path='+path,'--stdin',data=raw).decode().strip()==blob==row['raw_git_blob']==row['clean_git_blob']
for row in pres['explicit_sha']: assert sha(R/row['tree']/'skills/do-math/scripts/tests/corpus'/row['path'])==row['sha256']
baseline=read(RUN/'phases/018/tasks/job-cleanup/evidence/final-baseline.json')
for row in baseline['files']:
 raw=(Path(baseline['baseline'])/row['path']).read_bytes()
 assert hashlib.sha256(raw).hexdigest()==row['sha256']
 assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob']
history=[]
for group in read(E/'history-verification.json')['ast_history']:
 for row in group['reports']:
  assert row['exists'] and sha(R/row['path'])==row['sha256']==row['expected_sha256']
  history.append(dict(id=group['id'],path=row['path'],sha256=row['sha256']))
save('history-check.json',history)
def funcs(raw):
 text=raw.decode('utf-8-sig'); lines=text.splitlines(keepends=True)
 return {n.name:''.join(lines[n.lineno-1:n.end_lineno]) for n in ast.parse(text).body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
removed={'producer_nodes','produced_object_schema','written_object_schema','consumed_object_schema'}
for rel,allowed in [('doc_code.py',removed|{'field_schemas','scoped_field_issues'}),('engine_context.py',set())]:
 path=Path('.claude/skills/do-math/scripts/tests/support')/rel; raw=(E/(rel[:-3]+'-start.py')).read_bytes()
 assert hashlib.sha256(raw).hexdigest()==start[path.as_posix()]['sha256']
 old,new=funcs(raw),funcs((R/path).read_bytes()); assert all(k in new and v==new[k] for k,v in old.items() if k not in allowed)
 if rel=='doc_code.py': assert not removed&new.keys()
for path in (R/'.claude/skills/do-math').rglob('*.py'):
 if '__pycache__' not in path.parts: assert not any(name in path.read_text(encoding='utf-8-sig') for name in removed),path
for label in ('mirror-build','mirror-check','skill-only'): assert read(E/(label+'-process.json'))['exit_code']==0
assert 'verified' in (E/'skill-only.stdout').read_text(encoding='utf-8')
prior=read(RUN/'phases/024/manager-evidence/task-files.json')
assert all(sha(RUN/'phases/024/tasks/document-waits'/p)==h for p,h in prior.items())
assert original==inventory(T); save('task-files.json',original)
products=[p for p in changes if Path(p).name not in ('.timings.json','.timings-t3.json')]; save('product-paths.json',products)
save('verification.json',dict(head=git('rev-parse','HEAD').decode().strip(),sources=len(current),start_equal_previous=True,current_equal_final=True,
 changes=changes,outside_writes=[],suites=suites,products_to_commit=len(products),runtime_unchanged=True,original_task_files_unchanged=len(original),previous_task_files_unchanged=len(prior),
 actual_returns=observations,preservation=dict(runtime_inputs=len(pres['runtime_and_live_inputs']),fixed_boundary_paths=len(pres['fixed_runtime_and_t4_paths']),corpus_paths=len(pres['corpus']),explicit_sha=len(pres['explicit_sha']),host_recordings=len(pres['host_recordings']),tools=len(pres['tools']),baseline_files=len(baseline['files']))))
print(json.dumps(dict(sources=len(current),changes=len(changes),products=len(products),task_files=len(original),suites=suites)))

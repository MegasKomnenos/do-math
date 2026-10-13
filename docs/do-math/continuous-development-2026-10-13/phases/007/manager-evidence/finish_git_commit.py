"""Finish the published handoff after its index audit exposed two old normalized blobs."""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r'C:\math')
RUN = ROOT / 'docs/do-math/continuous-development-2026-10-13'
OUT = Path(__file__).resolve().parent
PHASE = OUT.parent

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def cmd(argv, payload=None):
    r = subprocess.run(argv,cwd=ROOT,input=payload,capture_output=True)
    assert r.returncode == 0, (argv,r.stderr.decode('utf-8',errors='replace'))
    return r.stdout

def record(name, argv):
    start=datetime.now(timezone.utc).isoformat()
    p=subprocess.Popen(argv,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    stdout,stderr=p.communicate()
    data=dict(argv=argv,cwd=str(ROOT),pid=p.pid,started_at=start,
              ended_at=datetime.now(timezone.utc).isoformat(),exit_code=p.returncode,
              stdout=stdout.decode('utf-8',errors='replace'),stderr=stderr.decode('utf-8',errors='replace'))
    (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    assert p.returncode==0,data

def pathset(raw):
    return set(raw.decode('utf-8').rstrip('\0').split('\0')) if raw else set()

head=cmd(['git','rev-parse','HEAD']).decode().strip()
assert head=='61f9e06fc15fb49ef30bf7d93c83c92e275eebad'
assert (PHASE/'manager.json').is_file() and not (PHASE/'manager.pending.json').exists()
manager_hash=sha(PHASE/'manager.json')
status=read(OUT/'writing-status.json')
assert status['status']=='ready' and status.get('completion_problem') is None
for p,h in read(OUT/'reading-inputs.json').items():
    assert sha(ROOT/p)==h,p
source=read(PHASE/'tasks/provider-consumers/evidence/source-final.json')
operator=read(OUT/'verification.json')['current_differences']
for p,h in source.items():
    assert sha(ROOT/p)==(operator[p]['current'] if p in operator else h),p
pres=read(OUT/'preservation.json')
selected=pres['selected_files']
assert pathset(cmd(['git','diff','--cached','--name-only','-z'])) <= set(selected)
for p,h in pres['task_evidence_sha256'].items():
    assert sha(ROOT/p)==h,p
repairs=read(OUT/'staged-corpus-difference.json')
assert len(repairs)==2
for row in repairs:
    assert row['working_sha256']==sha(ROOT/row['path'])==source[row['path']]
    assert row['head_equals_index'] and row['equal_after_crlf_normalization']
record('handoff-recheck.json',[sys.executable,'-B','services/continuous-development/check.py','handoff',str(ROOT),str(RUN),'007','manager.json'])
assert sha(PHASE/'manager.json')==manager_hash
cmd(['git','add','-f','--pathspec-from-file='+str(OUT/'commit-paths.nul'),'--pathspec-file-nul'])

# Force the exact reviewed blobs into the index even when stat-cache reuse hides
# a previously normalized HEAD blob. No working file is rewritten.
for row in repairs:
    oid=cmd(['git','hash-object','-w','--no-filters',row['path']]).decode().strip()
    cmd(['git','update-index','--add','--cacheinfo','100644',oid,row['path']])
staged=pathset(cmd(['git','diff','--cached','--name-only','-z']))
assert staged <= set(selected)
assert {p for p in staged if p.startswith('기억/layer1/')}=={'기억/layer1/M-0557.md'}
products={p for p in staged if p.startswith(('.claude/','.agents/'))}
assert products==set(pres['product_files'])|set(pres['git_byte_repairs'])
index={}
for row in cmd(['git','ls-files','-s','-z']).split(b'\0'):
    if row:
        meta,p=row.split(b'\t',1); index[p.decode('utf-8')]=meta.decode().split()[1]
assert all(p in index for p in selected)
raw_paths=sorted(set([p for p in selected if '/phases/007/tasks/provider-consumers/' in p or '/phases/007/manager-evidence/' in p]
                    +[r['path'] for r in read(OUT/'git-clean-observation.json')]))
objects=cmd(['git','hash-object','--no-filters','--stdin-paths'],('\n'.join(raw_paths)+'\n').encode()).decode().splitlines()
assert len(raw_paths)==len(objects)
assert all(index[p]==oid for p,oid in zip(raw_paths,objects)), [p for p,oid in zip(raw_paths,objects) if index[p]!=oid]
for row in read(OUT/'product-commit-plan.json'):
    assert index[row['path']]==row['candidate_blob']
assert cmd(['git','rev-parse','HEAD']).decode().strip()==head
git_status=cmd(['git','--no-optional-locks','-c','core.quotepath=false','status','--porcelain=v1','--untracked-files=no']).decode('utf-8')
(OUT/'stage.json').write_text(json.dumps({'staged':sorted(staged),'reviewed_product_paths':124,'git_byte_repairs':pres['git_byte_repairs'],
    'raw_objects_verified':len(raw_paths),'corpus_objects_verified':102,'status':git_status},ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
(OUT/'commit-message.txt').write_text('공급자 전송과 직접 소비 회귀를 마감하고 운영 복구 문서 결속을 배정\n',encoding='utf-8',newline='\n')
record('commit.json',['git','commit','-F',str(OUT/'commit-message.txt')])
new_head=cmd(['git','rev-parse','HEAD']).decode().strip()
assert pathset(cmd(['git','diff-tree','--no-commit-id','--name-only','-r','-z',new_head]))==staged
assert not pathset(cmd(['git','diff','--cached','--name-only','-z']))
for p,h in source.items():
    assert sha(ROOT/p)==(operator[p]['current'] if p in operator else h),p
assert sha(PHASE/'manager.json')==manager_hash
receipt=dict(commit=new_head,parent=head,committed_files=len(staged),provider_product_files=124,
             git_byte_repairs=pres['git_byte_repairs'],raw_objects_verified=len(raw_paths),corpus_objects_verified=102,
             source_files_verified=len(source),documented_operator_differences=4,manager_sha256=manager_hash,next='008',pushed=False)
(OUT/'post-commit.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(receipt,ensure_ascii=False))

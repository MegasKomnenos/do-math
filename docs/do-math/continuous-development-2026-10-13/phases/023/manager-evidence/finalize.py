"""Archive inspected bytes, check handoff, publish, and commit only the approved unit."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import zipfile

R=Path('C:/math'); RUN=R/'docs/do-math/continuous-development-2026-10-13'
O=Path(__file__).resolve().parent; P=RUN/'phases/023'; T=P/'tasks/document-governance'; E=T/'evidence'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v): (O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def git(*a): return subprocess.check_output(['git',*a],cwd=R)
def command(n,args):
 p=subprocess.run(args,cwd=R,capture_output=True)
 v=dict(argv=args,cwd=str(R),exit_code=p.returncode,stdout=p.stdout.decode('utf-8',errors='replace'),stderr=p.stderr.decode('utf-8',errors='replace'))
 save(n,v); assert p.returncode==0,v
 return v
head=read(O/'verification.json')['head']; sources=read(O/'source-inspected.json')
task_hashes=read(O/'task-files.json'); products=read(O/'product-paths.json')
assert len(products)==32
def unchanged():
 assert git('rev-parse','HEAD').decode().strip()==head
 assert all(sha(R/p)==h for p,h in sources.items())
 assert task_hashes=={p.relative_to(T).as_posix():sha(p) for p in T.rglob('*') if p.is_file()}
 assert all(sha(RUN/n)==h for n,h in read(O/'common-after-sha.json').items())
 assert sha(P/'logs/manager.log')==read(O/'restart-state.json')['previous_log_sha256']
 assert sorted((R/'기억/layer1').glob('M-*.md'))[-1].name=='M-0573.md'
 assert 'convention_version: 27' in (R/'기억/세칙.md').read_text(encoding='utf-8')

mode=sys.argv[1]
if mode=='prepare':
 unchanged(); assert not git('diff','--cached','--name-only','-z')
 dirty=set(filter(None,git('diff','--name-only','-z').decode().split('\0')))
 assert set(products)<=dirty
 save('unrelated-dirty-preserved.json',dict(paths=sorted(dirty-set(products)-{
  'docs/do-math/continuous-development-2026-10-13/context.md','docs/do-math/continuous-development-2026-10-13/plan.md',
  'docs/do-math/continuous-development-2026-10-13/seams.md','기억/색인.md'}),note='Pre-existing changes outside this manager unit are neither staged nor reverted.'))
 sections=read(E/'current-sections.json'); decisions=read(E/'section-name-decisions.json')['decisions']
 assert len(sections)==6 and {r['token'] for r in decisions}=={'impact_set','previous_hashes','revision_requests','revision_resolutions'}
 for section in sections:
  path=R/section['document'][5:]
  assert sha(path)==section['sha256'] and section['text'] in path.read_text(encoding='utf-8')
 prior=read(RUN/'phases/022/tasks/review-delivery/evidence/section-name-decisions.json')
 for row in decisions:
  old=next(x for x in prior if x['section']==row['section'] and x['token']==row['token'])
  assert row['sentences']==old['sentences']
  for tid in row['tests']:
   for label in ('c2','m'):
    result=read(E/label/'report.json')
    rows={r['id']:r for group in result['reports'] for r in group['rows'] if not r.get('fixture')}
    assert rows[tid]['outcome']=='passed'
 save('section-check.json',dict(sections=6,names=4,current_text_equal=True,exact_sentences_equal_previous=True,referenced_tests_passed_both=True,
  limit='Only P06/P10 and these four revision names; other N meanings stay in the plan.'))
 # A fresh non-mutating mirror check verifies the packaging gate; completed task tests are not rerun.
 command('mirror-check.json',[sys.executable,'-B','.claude/skills/writing-skills/scripts/build_skill_mirrors.py','--check'])
 archive=O/'raw-evidence.zip'; assert not archive.exists()
 archived={p for p in T.rglob('*') if p.is_file()}|{R/p for p in products}|{P/'logs/manager.log'}
 entries={}
 with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for path in sorted(archived):
   raw=path.read_bytes(); rel=path.relative_to(R).as_posix(); z.writestr(rel,raw)
   entries[rel]=hashlib.sha256(raw).hexdigest()
 with zipfile.ZipFile(archive) as z:
  assert set(z.namelist())==set(entries)
  assert all(hashlib.sha256(z.read(p)).hexdigest()==h for p,h in entries.items())
 paths={R/p for p in products}|{T/'report.json',R/'기억/layer1/M-0573.md',R/'기억/색인.md'}
 paths.update(RUN/n for n in ('context.md','plan.md','seams.md','phases/023/manager.json','phases/024/phase.json',
  'phases/024/tasks/document-waits/objective.md','phases/024/logs/.gitkeep'))
 paths.update(p for p in O.iterdir() if p.is_file() and p.name not in ('commit-plan.json','commit-paths.nul','preservation.json'))
 paths.add(O/'preservation.json')
 # Selected entry points remain directly tracked; all omitted originals remain in the archive.
 paths.update(p for p in E.iterdir() if p.is_file()
  and not p.name.endswith(('-before.json','-after.json'))
  and not any(p.name.startswith(label+kind) for label in ('c','c2','m') for kind in ('-return-','-check-'))
  and p.name not in ('preservation-current.json','diff-current.json'))
 paths.update(E/n/'report.json' for n in ('red','focus','corrected','c','c2','m'))
 relative=sorted(p.relative_to(R).as_posix() for p in paths)
 save('preservation.json',dict(archive=archive.relative_to(R).as_posix(),archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,
  entries=entries,products_committed=products,product_count=32,task_files=len(task_hashes),tracked_paths=relative,
  raw_bytes='Original 891 task files, 32 inspected product paths and previous manager.log are archived and independently read back with SHA256. No original task or prior management files are rewritten.',
  local_only='Unselected return files and snapshots remain local at their original paths; exact bytes also exist in the tracked archive. The active manager-restart-001.log and stage/commit receipts remain local. The archive is not an instruction to restore.',
  scope='Only the inspected 023 changes, management handoff, selected original evidence, 024 assignment and M-0573. Pre-existing unrelated changes, services and operator scripts are excluded.'))
 pending=P/'manager.pending.json'; published=P/'manager.json'; assert pending.exists() and not published.exists()
 hashes={p:sha(R/p) for p in relative if p!=published.relative_to(R).as_posix()}
 save('commit-plan.json',dict(head=head,paths=relative,sha256=hashes,products=32,pending_sha256=sha(pending)))
 (O/'commit-paths.nul').write_bytes(b'\0'.join(p.encode('utf-8') for p in relative)+b'\0')
 command('memory-check.json',[sys.executable,'-B','기억/scripts/validate_memory_index.py'])
 command('worktree-diff-check.json',['git','diff','--check','--',*products,
  'docs/do-math/continuous-development-2026-10-13/context.md','docs/do-math/continuous-development-2026-10-13/plan.md',
  'docs/do-math/continuous-development-2026-10-13/seams.md','기억/색인.md'])
 command('handoff-check.json',[sys.executable,'-B','services/continuous-development/check.py','handoff',str(R),str(RUN),'023'])
 unchanged(); assert all(sha(R/p)==h for p,h in hashes.items())
 assert sha(pending)==read(O/'commit-plan.json')['pending_sha256']
 print(json.dumps(dict(archive_entries=len(entries),archive_bytes=archive.stat().st_size,paths=len(relative),products=32,memory='PASS',handoff='PASS 023',next='024'),ensure_ascii=False))
elif mode=='publish':
 unchanged(); plan=read(O/'commit-plan.json'); relative=plan['paths']; hashes=plan['sha256']
 assert not git('diff','--cached','--name-only','-z')
 assert read(O/'memory-check.json')['exit_code']==read(O/'handoff-check.json')['exit_code']==0
 assert all(sha(R/p)==h for p,h in hashes.items())
 pending=P/'manager.pending.json'; published=P/'manager.json'
 assert pending.exists() and not published.exists() and sha(pending)==plan['pending_sha256']
 pending.rename(published); assert sha(published)==plan['pending_sha256']
 print('Published checked manager.json; next 024.',flush=True)
 command('stage-command.json',['git','add','-f','--pathspec-from-file='+str(O/'commit-paths.nul'),'--pathspec-file-nul'])
 staged=set(filter(None,git('diff','--cached','--name-only','-z').decode().split('\0')))
 assert staged and staged<=set(relative) and set(products)<=staged
 assert [p for p in staged if p.startswith('기억/layer1/')]==['기억/layer1/M-0573.md']
 command('staged-diff-check.json',['git','diff','--cached','--check'])
 data=subprocess.check_output(['git','cat-file','--batch'],cwd=R,input=('\n'.join(':'+p for p in relative)+'\n').encode('utf-8'))
 stream=io.BytesIO(data); received={}
 for path in relative:
  oid,kind,size=stream.readline().decode().split(); assert kind=='blob'
  blob=stream.read(int(size)); assert stream.read(1)==b'\n'; raw=(R/path).read_bytes()
  if '/evidence/' in path or '/manager-evidence/' in path or path.endswith(('/report.json','/manager.json')): assert blob==raw,path
  else: assert blob==raw or blob==raw.replace(b'\r\n',b'\n'),path
  received[path]=dict(blob=oid,sha256=sha(R/path),raw_equals_blob=blob==raw)
 assert not stream.read()
 save('stage.json',dict(head=head,planned_count=len(relative),staged_count=len(staged),products=32,paths=received,changed_paths=sorted(staged)))
 unchanged(); assert all(sha(R/p)==v['sha256'] for p,v in received.items())
 assert staged==set(filter(None,git('diff','--cached','--name-only','-z').decode().split('\0')))
 (O/'commit-message.txt').write_text('중단된 관리 검수를 복구하고 수입·현재 조회 문서 결속과 다음 배정을 마감함\n',encoding='utf-8')
 command('commit.json',['git','commit','--file',str(O/'commit-message.txt')])
 newhead=git('rev-parse','HEAD').decode().strip()
 committed=set(filter(None,git('diff-tree','--no-commit-id','--name-only','-r','-z',newhead).decode().split('\0')))
 assert committed==staged
 blobs={row.split(b'\t',1)[1].decode('utf-8'):row.split(b'\t',1)[0].decode().split()[2] for row in git('ls-tree','-r','-z',newhead).split(b'\0') if row}
 assert all(blobs[p]==v['blob'] for p,v in received.items())
 assert all(sha(R/p)==v['sha256'] for p,v in received.items())
 assert all(sha(R/p)==h for p,h in sources.items()) and all(sha(T/p)==h for p,h in task_hashes.items())
 assert sha(P/'logs/manager.log')==read(O/'restart-state.json')['previous_log_sha256']
 assert not git('diff','--cached','--name-only','-z')
 save('post-commit.json',dict(head=newhead,parent=head,committed_count=len(committed),products_committed=32,
  source_raw_bytes_unchanged=True,task_raw_bytes_preserved=True,previous_manager_log_preserved=True,index_empty=True,
  manager_sha256=plan['pending_sha256'],next='024',push_performed=False))
 print(json.dumps(dict(head=newhead,committed=len(committed),products=32,handoff='PASS 023',next='024'),ensure_ascii=False))
else: raise ValueError(mode)

"""Preserve raw evidence, validate, then publish and commit the exact reviewed unit."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import zipfile

R=Path('C:/math'); RUN=R/'docs/do-math/continuous-development-2026-10-13'
O=Path(__file__).resolve().parent; P=RUN/'phases/024'; T=P/'tasks/document-waits'; E=T/'evidence'
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
assert len(products)==28
def unchanged():
 assert git('rev-parse','HEAD').decode().strip()==head
 assert all(sha(R/p)==h for p,h in sources.items())
 assert task_hashes=={p.relative_to(T).as_posix():sha(p) for p in T.rglob('*') if p.is_file()}
 assert all(sha(RUN/n)==h for n,h in read(O/'common-after-sha.json').items())
 assert sorted((R/'기억/layer1').glob('M-*.md'))[-1].name=='M-0574.md'
 assert 'convention_version: 27' in (R/'기억/세칙.md').read_text(encoding='utf-8')

mode=sys.argv[1]
if mode=='prepare':
 unchanged(); assert not git('diff','--cached','--name-only','-z')
 dirty=set(filter(None,git('diff','--name-only','-z').decode().split('\0')))
 assert set(products)<=dirty
 unrelated=sorted(dirty-set(products)-{'docs/do-math/continuous-development-2026-10-13/'+n for n in ('context.md','plan.md','seams.md')}-{'기억/색인.md'})
 save('unrelated-dirty-preserved.json',dict(paths=unrelated,sha256={p:sha(R/p) for p in unrelated},note='Pre-existing unrelated files remain unstaged and unchanged.'))
 if not (O/'mirror-check.json').exists():
  command('mirror-check.json',[sys.executable,'-B','.claude/skills/writing-skills/scripts/build_skill_mirrors.py','--check'])
 else: assert read(O/'mirror-check.json')['exit_code']==0  # Exact sources above remain unchanged.
 archive=O/'raw-evidence.zip'
 archived={p for p in T.rglob('*') if p.is_file()}|{R/p for p in products}
 entries={}
 entries={p.relative_to(R).as_posix():sha(p) for p in sorted(archived)}
 if not archive.exists():
  with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
   for path in sorted(archived): z.writestr(path.relative_to(R).as_posix(),path.read_bytes())
 with zipfile.ZipFile(archive) as z:
  assert set(z.namelist())==set(entries)
  assert all(hashlib.sha256(z.read(p)).hexdigest()==h for p,h in entries.items())
 paths={R/p for p in products}|{T/'report.json',R/'기억/layer1/M-0574.md',R/'기억/색인.md'}
 paths.update(RUN/n for n in ('context.md','plan.md','seams.md','phases/024/manager.json','phases/025/phase.json',
  'phases/025/tasks/document-trust/objective.md','phases/025/logs/.gitkeep'))
 excluded={'commit-plan.json','commit-paths.nul','preservation.json','commit-message.txt','commit.json','stage.json','stage-command.json','post-commit.json',
  'memory-check.json','handoff-check.json','worktree-diff-check.json','staged-diff-check.json'}
 paths.update(p for p in O.iterdir() if p.is_file() and p.name not in excluded)
 paths.add(O/'preservation.json')
 paths.update(p for p in E.iterdir() if p.is_file() and not p.name.endswith(('-before.json','-after.json'))
  and not any(p.name.startswith(label+'-proposal-') for label in ('c','c2','m'))
  and p.name not in ('preservation-current.json','diff-current.json'))
 paths.update(E/n/'report.json' for n in ('red','focus','corrected','c','c2','m','cwd'))
 relative=sorted(p.relative_to(R).as_posix() for p in paths)
 save('preservation.json',dict(archive=archive.relative_to(R).as_posix(),archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,
  entries=entries,products_committed=products,product_count=28,task_files=len(task_hashes),tracked_paths=relative,
  raw_bytes='All 352 original task files and 28 inspected product files are archived and independently read back with SHA256. No task or past phase artifact is rewritten.',
  local_only='Unselected proposals, snapshots and scratch remain local at their original paths; their bytes also exist in the tracked archive. Active manager.log and stage/commit administrative receipts remain local. The archive is not an instruction to restore.',
  scope='Only reviewed 024 changes, management handoff, selected original evidence, 025 assignment and M-0574; unrelated files and costs caches are excluded.'))
 pending=P/'manager.pending.json'; published=P/'manager.json'; assert pending.exists() and not published.exists()
 hashes={p:sha(R/p) for p in relative if p!=published.relative_to(R).as_posix()}
 save('commit-plan.json',dict(head=head,paths=relative,sha256=hashes,products=28,pending_sha256=sha(pending)))
 (O/'commit-paths.nul').write_bytes(b'\0'.join(p.encode('utf-8') for p in relative)+b'\0')
 if not (O/'memory-check.json').exists(): command('memory-check.json',[sys.executable,'-B','기억/scripts/validate_memory_index.py'])
 else: assert read(O/'memory-check.json')['exit_code']==0
 command('worktree-diff-check.json',['git','diff','--check','--',*products,
  'docs/do-math/continuous-development-2026-10-13/context.md','docs/do-math/continuous-development-2026-10-13/plan.md',
  'docs/do-math/continuous-development-2026-10-13/seams.md','기억/색인.md'])
 command('handoff-check.json',[sys.executable,'-B','services/continuous-development/check.py','handoff',str(R),str(RUN),'024'])
 unchanged(); assert all(sha(R/p)==h for p,h in hashes.items())
 assert sha(pending)==read(O/'commit-plan.json')['pending_sha256']
 print(json.dumps(dict(archive_entries=len(entries),archive_bytes=archive.stat().st_size,paths=len(relative),products=28,memory='PASS',handoff='PASS 024',next='025')))
elif mode=='publish':
 unchanged(); plan=read(O/'commit-plan.json'); relative=plan['paths']; hashes=plan['sha256']
 assert not git('diff','--cached','--name-only','-z')
 assert read(O/'memory-check.json')['exit_code']==read(O/'handoff-check.json')['exit_code']==0
 assert all(sha(R/p)==h for p,h in hashes.items())
 pending=P/'manager.pending.json'; published=P/'manager.json'
 assert pending.exists() and not published.exists() and sha(pending)==plan['pending_sha256']
 pending.rename(published); assert sha(published)==plan['pending_sha256']
 print('Published checked manager.json; next 025.',flush=True)
 command('stage-command.json',['git','add','-f','--pathspec-from-file='+str(O/'commit-paths.nul'),'--pathspec-file-nul'])
 staged=set(filter(None,git('diff','--cached','--name-only','-z').decode().split('\0')))
 assert staged and staged<=set(relative) and set(products)<=staged
 assert [p for p in staged if p.startswith('기억/layer1/')]==['기억/layer1/M-0574.md']
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
 save('stage.json',dict(head=head,planned_count=len(relative),staged_count=len(staged),products=28,paths=received,changed_paths=sorted(staged)))
 unchanged(); assert all(sha(R/p)==v['sha256'] for p,v in received.items())
 assert staged==set(filter(None,git('diff','--cached','--name-only','-z').decode().split('\0')))
 assert all(sha(R/p)==h for p,h in read(O/'unrelated-dirty-preserved.json')['sha256'].items())
 (O/'commit-message.txt').write_text('조건·대기 문서 결속을 검수하고 신뢰 경계 작업을 통합 배정함\n',encoding='utf-8')
 command('commit.json',['git','commit','--file',str(O/'commit-message.txt')])
 newhead=git('rev-parse','HEAD').decode().strip()
 committed=set(filter(None,git('diff-tree','--no-commit-id','--name-only','-r','-z',newhead).decode().split('\0')))
 assert committed==staged
 blobs={row.split(b'\t',1)[1].decode('utf-8'):row.split(b'\t',1)[0].decode().split()[2] for row in git('ls-tree','-r','-z',newhead).split(b'\0') if row}
 assert all(blobs[p]==v['blob'] for p,v in received.items())
 assert all(sha(R/p)==v['sha256'] for p,v in received.items())
 assert all(sha(R/p)==h for p,h in sources.items()) and all(sha(T/p)==h for p,h in task_hashes.items())
 assert all(sha(R/p)==h for p,h in read(O/'unrelated-dirty-preserved.json')['sha256'].items())
 assert not git('diff','--cached','--name-only','-z')
 save('post-commit.json',dict(head=newhead,parent=head,committed_count=len(committed),products_committed=28,
  source_raw_bytes_unchanged=True,task_raw_bytes_preserved=True,unrelated_dirty_preserved=True,index_empty=True,
  manager_sha256=plan['pending_sha256'],next='025',push_performed=False))
 print(json.dumps(dict(head=newhead,committed=len(committed),products=28,handoff='PASS 024',next='025')))
else: raise ValueError(mode)

"""Publish the checked handoff and commit only this management unit."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from verify import R, RUN, O, read, sha, snapshot

def save(name, value):
    (O/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def git(*args):
    return subprocess.check_output(['git',*args],cwd=R)

def command(name,args):
    p=subprocess.run(args,cwd=R,capture_output=True)
    result=dict(command=args,exit_code=p.returncode,stdout=p.stdout.decode('utf-8','replace'),stderr=p.stderr.decode('utf-8','replace'))
    save(name,result)
    assert p.returncode==0,result
    return result

head=git('rev-parse','HEAD').decode().strip()
assert head==read(O/'verification.json')['head']
assert snapshot()==read(O/'source-inspected.json')
task_files=read(O/'task-files.json')
assert all(sha(RUN/p)==h for p,h in task_files.items())
assert not git('diff','--cached','--name-only','-z')
assert not (RUN/'phases/026/manager.json').exists()

runrel=RUN.relative_to(R).as_posix()
orel=O.relative_to(R).as_posix()
files={runrel+'/'+p for p in task_files}
files.update(runrel+'/'+p for p in ('context.md','plan.md','seams.md','phases/026/manager.json',
    'phases/027/phase.json','phases/027/tasks/doc-policy/objective.md'))
files.update(('기억/layer1/M-0576.md','기억/색인.md'))
managed=['verify.py','prepare.py','finalize.py','verification.json','report-check.json',
    'source-inspected.json','task-files.json','common-comparison.json','common-docs.diff','review.md',
    'preservation.json','unrelated-dirty-preserved.json']
files.update(orel+'/'+p for p in managed)
assert not any(p.startswith(('.claude/','.agents/')) for p in files)
dirty=git('diff','--name-only','-z').decode('utf-8').split('\0')
unrelated={p:sha(R/p) for p in dirty if p and p not in files}
save('unrelated-dirty-preserved.json',dict(head=head,sha256=unrelated,note='Already dirty outside this management unit; excluded from staging.'))
save('preservation.json',dict(task_files=task_files,task_file_count=len(task_files),
    task_total_bytes=sum((RUN/p).stat().st_size for p in task_files),
    intended_tracked_paths=sorted(files),product_changes=0,
    raw_preservation='All 84 task files are tracked directly. The 81 report/evidence files preserve exact Git blob bytes; the three existing objective Markdown files use the repository newline normalization. Working-tree SHA is unchanged for all 84. No duplicate archive.',
    local_only=['phases/026/logs/','manager-evidence/*.before','manager-evidence/commit-paths.nul',
                'manager-evidence/commit-plan.json','manager-evidence/commit-message.txt',
                'manager-evidence/memory-check.json','manager-evidence/handoff-check.json',
                'manager-evidence/worktree-diff-check.json','manager-evidence/staged-diff-check.json',
                'manager-evidence/stage-command.json','manager-evidence/stage.json',
                'manager-evidence/commit.json','manager-evidence/post-commit.json'],
    note='Local logs/administrative receipts may disappear on cleanup. Common semantic edits are retained in common-docs.diff. Existing unrelated changes are not committed.'))
save('commit-plan.json',dict(head=head,paths=sorted(files),memory='M-0576',products=0))

command('memory-check.json',[sys.executable,'-B','기억/scripts/validate_memory_index.py'])
command('worktree-diff-check.json',['git','diff','--check','--',runrel+'/context.md',runrel+'/plan.md',runrel+'/seams.md','기억/색인.md'])
assert read(O/'common-comparison.json')['criteria_unchanged']
for name,digest in read(O/'common-comparison.json')['after'].items():
    assert sha(RUN/name)==digest,name
# No submitted input changes after this check. Only rename and Git administration follow.
command('handoff-check.json',[sys.executable,'services/continuous-development/check.py','handoff',str(R),str(RUN),'026'])
pending=RUN/'phases/026/manager.pending.json'
pending_sha=sha(pending)
pending.rename(RUN/'phases/026/manager.json')
assert sha(RUN/'phases/026/manager.json')==pending_sha

(O/'commit-paths.nul').write_bytes(b'\0'.join(p.encode('utf-8') for p in sorted(files))+b'\0')
command('stage-command.json',['git','add','-f','--pathspec-from-file='+str(O/'commit-paths.nul'),'--pathspec-file-nul'])
staged=set(filter(None,git('diff','--cached','--name-only','-z').decode('utf-8').split('\0')))
assert staged and staged<=files
assert {p for p in staged if p.startswith('기억/layer1/')}=={'기억/layer1/M-0576.md'}
assert not any(p.startswith(('.claude/','.agents/')) for p in staged)
command('staged-diff-check.json',['git','diff','--cached','--check'])
blob_hashes={}
normalized=[]
for p in sorted(files):
    blob=git('show',':'+p)
    blob_hashes[p]=hashlib.sha256(blob).hexdigest()
    if p in {'기억/색인.md',runrel+'/context.md',runrel+'/plan.md',runrel+'/seams.md',runrel+'/phases/027/phase.json'} or p.endswith('/objective.md'):
        assert blob==(R/p).read_bytes().replace(b'\r\n',b'\n'),p
        normalized.append(p)
    else:
        assert blob_hashes[p]==sha(R/p),p
assert all(blob_hashes[runrel+'/'+p]==digest for p,digest in task_files.items() if not p.endswith('/objective.md'))
save('stage.json',dict(head=head,staged_count=len(staged),planned_count=len(files),paths=sorted(staged),blob_sha256=blob_hashes,line_ending_normalized=normalized))
assert all(sha(R/p)==h for p,h in unrelated.items())
assert snapshot()==read(O/'source-inspected.json')
assert git('rev-parse','HEAD').decode().strip()==head
assert staged==set(filter(None,git('diff','--cached','--name-only','-z').decode('utf-8').split('\0')))
assert max(p.stem for p in (R/'기억/layer1').glob('M-*.md'))=='M-0576'
(O/'commit-message.txt').write_text('문서 이름 조사 결과를 검수하고 정책·역할 검사 수리를 통합 배정함\n',encoding='utf-8')
command('commit.json',['git','commit','-F',str(O/'commit-message.txt')])
newhead=git('rev-parse','HEAD').decode().strip()
committed=set(filter(None,git('diff-tree','--no-commit-id','--name-only','-r','-z',newhead).decode('utf-8').split('\0')))
assert committed==staged
assert not git('diff','--cached','--name-only','-z')
assert all(sha(R/p)==h for p,h in unrelated.items())
assert snapshot()==read(O/'source-inspected.json')
assert all(sha(RUN/p)==h for p,h in task_files.items())
assert sha(RUN/'phases/026/manager.json')==pending_sha
save('post-commit.json',dict(commit=newhead,paths=len(committed),product_changes=0,unrelated_dirty_preserved=len(unrelated),
    task_files_preserved=len(task_files),manager_sha256=pending_sha,staged_empty=True,pushed=False))
print(json.dumps(read(O/'post-commit.json'),ensure_ascii=False))

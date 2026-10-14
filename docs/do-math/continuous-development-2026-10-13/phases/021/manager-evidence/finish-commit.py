"""Correct one administrative EOF byte, recheck published handoff, commit exact paths."""
import difflib
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys

R=Path('C:/math'); RUN=R/'docs/do-math/continuous-development-2026-10-13'
O=Path(__file__).resolve().parent
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v): (O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def git(*args): return subprocess.check_output(['git',*args],cwd=R)
def command(n,args):
    p=subprocess.run(args,cwd=R,capture_output=True)
    row={'argv':args,'cwd':str(R),'exit_code':p.returncode,'stdout':p.stdout.decode('utf-8',errors='replace'),
         'stderr':p.stderr.decode('utf-8',errors='replace')}
    save(n,row); assert p.returncode==0,row

plan=read(O/'commit-plan.json'); head=plan['head']; source=read(O/'source-inspected.json')
assert git('rev-parse','HEAD').decode().strip()==head
assert set(filter(None,git('diff','--cached','--name-only','-z').decode().split('\0'))) <= set(plan['paths'])
assert all(sha(R/p)==h for p,h in plan['sha256'].items())
assert all(sha(R/p)==h for p,h in source.items())
manager=RUN/'phases/021/manager.json'; manager_sha=sha(manager)
assert manager_sha==plan['pending_sha256']
problem=read(O/'staged-diff-check.json')
assert problem['exit_code']==2 and problem['stdout']=='docs/do-math/continuous-development-2026-10-13/context.md:326: new blank line at EOF.\n'
context=RUN/'context.md'; before=context.read_bytes()
assert before.endswith(b'\n\n') and not before.endswith(b'\n\n\n')
diff_path=O/'common-docs.diff'; full_diff=diff_path.read_text(encoding='utf-8')
context_diff,rest=full_diff.split('--- plan.md before 021 manager\n',1)
new_lines=before.decode('utf-8').splitlines(True)
old_lines=[]; pos=0; active=False
for line in context_diff.splitlines(True)[2:]:
    if line.startswith('@@ '):
        m=re.match(r'@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@',line)
        assert m,line
        start=int(m.group(1))-1
        assert pos<=start
        old_lines.extend(new_lines[pos:start]); pos=start; active=True
    elif active and line.startswith(' '):
        assert line[1:]==new_lines[pos]
        old_lines.append(line[1:]); pos+=1
    elif active and line.startswith('+'):
        assert line[1:]==new_lines[pos]
        pos+=1
    elif active and line.startswith('-'):
        old_lines.append(line[1:])
    else:
        raise AssertionError(line)
old_lines.extend(new_lines[pos:]); original=''.join(old_lines)
assert hashlib.sha256(original.encode('utf-8')).hexdigest()==read(O/'common-before-sha.json')['context.md']
context.write_bytes(before[:-1])
new_diff=''.join(difflib.unified_diff(original.splitlines(True),context.read_text(encoding='utf-8').splitlines(True),
    fromfile='context.md before 021 manager',tofile='context.md after 021 manager'))
diff_path.write_text(new_diff+'--- plan.md before 021 manager\n'+rest,encoding='utf-8',newline='\n')
after=read(O/'common-after-sha.json'); after['context.md']=sha(context); save('common-after-sha.json',after)
relative=sorted(set(plan['paths'])|{Path(__file__).relative_to(R).as_posix(),(O/'publication-correction.json').relative_to(R).as_posix()})
save('publication-correction.json',{'reason':'Removed exactly one administrative EOF LF found by Git whitespace check. Reconstructed the original context from the previously inspected diff and verified its original SHA before regenerating that diff. Requirements, assignment, product bytes and manager decision are unchanged. Recheck the published candidate.',
    'before_context_sha256':hashlib.sha256(before).hexdigest(),'after_context_sha256':sha(context),
    'removed_bytes':1,'original_check':problem,'manager_sha256':manager_sha,'recheck_candidate':'manager.json'})
pres=read(O/'preservation.json'); pres['tracked_paths']=relative; save('preservation.json',pres)
assert all(sha(R/p)==h for p,h in pres['entries'].items())
command('handoff-recheck.json',[sys.executable,'-B','services/continuous-development/check.py',
        'handoff',str(R),str(RUN),'021','manager.json'])
assert sha(manager)==manager_sha
hashes={p:sha(R/p) for p in relative}
save('commit-plan-final.json',{'head':head,'paths':relative,'sha256':hashes,'products_committed':0,'products_deferred':26})
(O/'commit-paths.nul').write_bytes(b'\0'.join(p.encode('utf-8') for p in relative)+b'\0')
command('stage-final-command.json',['git','add','-f','--pathspec-from-file='+str(O/'commit-paths.nul'),'--pathspec-file-nul'])
staged=set(filter(None,git('diff','--cached','--name-only','-z').decode().split('\0')))
assert staged and staged<=set(relative) and not set(pres['products_deferred'])&staged
command('staged-final-diff-check.json',['git','diff','--cached','--check'])
data=subprocess.check_output(['git','cat-file','--batch'],cwd=R,input=('\n'.join(':'+p for p in relative)+'\n').encode('utf-8'))
stream=io.BytesIO(data); received={}
for path in relative:
    oid,kind,size=stream.readline().decode().split(); assert kind=='blob'
    blob=stream.read(int(size)); assert stream.read(1)==b'\n'
    raw=(R/path).read_bytes()
    if '/evidence/' in path or '/manager-evidence/' in path or path.endswith(('/report.json','/manager.json')):
        assert blob==raw,path
    else:
        assert blob==raw or blob==raw.replace(b'\r\n',b'\n'),path
    received[path]={'blob':oid,'sha256':sha(R/path),'raw_equals_blob':blob==raw}
assert not stream.read()
save('stage.json',{'head':head,'planned_count':len(relative),'staged_count':len(staged),
    'products_committed':0,'products_deferred':26,'paths':received,'changed_paths':sorted(staged)})
assert git('rev-parse','HEAD').decode().strip()==head
assert all(sha(R/p)==h for p,h in source.items()) and all(sha(R/p)==h for p,h in hashes.items())
assert sorted((R/'기억/layer1').glob('M-*.md'))[-1].name=='M-0571.md'
assert [p for p in staged if p.startswith('기억/layer1/')]==['기억/layer1/M-0571.md']
assert 'convention_version: 27' in (R/'기억/세칙.md').read_text(encoding='utf-8')
assert staged==set(filter(None,git('diff','--cached','--name-only','-z').decode().split('\0')))
command('pre-commit-status.json',['git','status','--short','--untracked-files=no'])
(O/'commit-message.txt').write_text('검토 입력 중복을 기록하고 제출 경계 수리와 문서 검증을 묶어 배정함\n',encoding='utf-8')
command('commit.json',['git','commit','--file',str(O/'commit-message.txt')])
newhead=git('rev-parse','HEAD').decode().strip()
committed=set(filter(None,git('diff-tree','--no-commit-id','--name-only','-r','-z',newhead).decode().split('\0')))
assert committed==staged
blobs={entry.split(b'\t',1)[1].decode('utf-8'):entry.split(b'\t',1)[0].decode().split()[2]
       for entry in git('ls-tree','-r','-z',newhead).split(b'\0') if entry}
assert all(blobs[p]==row['blob'] for p,row in received.items())
assert all(sha(R/p)==row['sha256'] for p,row in received.items())
assert all(sha(R/p)==h for p,h in source.items())
assert all(sha(R/p)==h for p,h in pres['entries'].items())
assert not git('diff','--cached','--name-only','-z')
save('post-commit.json',{'head':newhead,'parent':head,'committed_count':len(committed),
    'products_committed':0,'products_deferred':26,'source_raw_bytes_unchanged':True,
    'task_raw_bytes_preserved':True,'index_empty':True,'manager_sha256':manager_sha,'next':'022','push_performed':False})
print(json.dumps({'head':newhead,'committed':len(committed),'products_committed':0,
    'handoff':'PASS 021 published candidate recheck','next':'022'},ensure_ascii=False))

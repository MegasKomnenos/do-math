"""Correct the one administrative EOF blank line, revalidate, and finish exact staging."""
import difflib
import hashlib
import json
from pathlib import Path
import subprocess
import sys

R=Path('C:/math'); RUN=R/'docs/do-math/continuous-development-2026-10-13'; O=Path(__file__).resolve().parent
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,v): (O/name).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def git(*args): return subprocess.check_output(['git',*args],cwd=R)
def command(name,args):
    p=subprocess.run(args,cwd=R,capture_output=True)
    row={'argv':args,'cwd':str(R),'exit_code':p.returncode,'stdout':p.stdout.decode('utf-8',errors='replace'),'stderr':p.stderr.decode('utf-8',errors='replace')}
    save(name,row); assert p.returncode==0,row
    return row
old_plan=read(O/'commit-plan.json'); head=old_plan['head']
assert git('rev-parse','HEAD').decode().strip()==head
assert set(filter(None,git('diff','--cached','--name-only','-z').decode().split('\0')))==set(old_plan['paths'])
source=read(O/'source-inspected.json'); assert all(sha(R/p)==h for p,h in source.items())
published=RUN/'phases/015/manager.json'; manager_hash=sha(published)
path=RUN/'context.md'; raw=path.read_text(encoding='utf-8'); corrected=raw.rstrip()+'\n'
assert raw==corrected+'\n'
path.write_text(corrected,encoding='utf-8',newline='\n')
review=O/'review.md'
review.write_text(review.read_text(encoding='utf-8').rstrip()+'''\n\n관리 마감의 첫 staged diff 검사는 context의 EOF 빈 줄 하나로 exit2였다. 내용은 유지하고 빈 줄만 제거했다. 원 실패 수신은 로컬 staged-diff-check.json에 보존하며 공용 diff를 갱신한 뒤 게시된 manager.json을 후보로 handoff를 다시 검사한다. 제품/task 원자료와 manager 판단 JSON은 바뀌지 않는다.\n''',encoding='utf-8',newline='\n')
diff=''
for name in ('context.md','plan.md','seams.md'):
    p=RUN/name; rel=p.relative_to(R).as_posix()
    old=git('show',head+':'+rel).decode('utf-8-sig').replace('\r\n','\n')
    now=p.read_text(encoding='utf-8')
    diff+=''.join(difflib.unified_diff(old.splitlines(True),now.splitlines(True),fromfile=name+' before',tofile=name+' after'))
(O/'common-docs.diff').write_text(diff,encoding='utf-8',newline='\n')
relative=sorted(set(old_plan['paths'])|{(O/'resume_commit.py').relative_to(R).as_posix()})
preservation=read(O/'preservation.json'); preservation['tracked_paths']=relative; save('preservation.json',preservation)
hashes={p:sha(R/p) for p in relative}
save('commit-plan-final.json',{'head':head,'paths':relative,'sha256':hashes,'products_staged':0,'products_deferred':old_plan['products_deferred']})
(O/'commit-paths-final.nul').write_bytes(b'\0'.join(p.encode('utf-8') for p in relative)+b'\0')
command('handoff-final-check.json',[sys.executable,'-B','services/continuous-development/check.py','handoff',str(R),str(RUN),'015','manager.json'])
assert all(sha(R/p)==h for p,h in hashes.items()) and sha(published)==manager_hash
command('stage-final-command.json',['git','add','-f','--pathspec-from-file='+str(O/'commit-paths-final.nul'),'--pathspec-file-nul'])
assert set(filter(None,git('diff','--cached','--name-only','-z').decode().split('\0')))==set(relative)
command('staged-final-diff-check.json',['git','diff','--cached','--check'])
received={}
for p in relative:
    raw=(R/p).read_bytes(); blob=git('rev-parse',':'+p).decode().strip(); data=git('show',':'+p)
    clean=subprocess.check_output(['git','hash-object','--path='+p,'--stdin'],cwd=R,input=raw).decode().strip()
    assert clean==blob,p
    if '/evidence/' in p or '/manager-evidence/' in p or p.endswith(('/report.json','/manager.json')): assert data==raw,p
    received[p]={'sha256':hashlib.sha256(raw).hexdigest(),'blob':blob,'raw_equals_blob':data==raw}
save('stage.json',{'head':head,'exact_count':len(relative),'products_staged':0,'paths':received})
assert git('rev-parse','HEAD').decode().strip()==head
assert set(filter(None,git('diff','--cached','--name-only','-z').decode().split('\0')))==set(relative)
assert all(sha(R/p)==h for p,h in source.items()) and all(sha(R/p)==h for p,h in hashes.items())
assert [p for p in relative if p.startswith('기억/layer1/')]==['기억/layer1/M-0565.md']
assert sorted((R/'기억/layer1').glob('M-*.md'))[-1].name=='M-0565.md'
command('pre-commit-status.json',['git','status','--short','--untracked-files=no'])
(O/'commit-message.txt').write_text('T4 측정 성과를 검수하고 경계 수리와 비교 입력 준비를 배정함\n',encoding='utf-8')
command('commit.json',['git','commit','--file',str(O/'commit-message.txt')])
newhead=git('rev-parse','HEAD').decode().strip()
committed=set(filter(None,git('diff-tree','--no-commit-id','--name-only','-r','-z',newhead).decode().split('\0')))
assert committed==set(relative)
assert all(git('rev-parse',newhead+':'+p).decode().strip()==v['blob'] for p,v in received.items())
assert all(sha(R/p)==v['sha256'] for p,v in received.items()) and all(sha(R/p)==h for p,h in source.items())
assert not git('diff','--cached','--name-only','-z')
save('post-commit.json',{'head':newhead,'parent':head,'committed_count':len(relative),'products_staged':0,'products_deferred':12,
     'source_raw_bytes_unchanged':True,'index_empty':True,'manager_sha256':manager_hash,'next':'016','push_performed':False})
print(json.dumps({'head':newhead,'committed':len(relative),'products_staged':0,'products_deferred':12,'handoff':'PASS 015','next':'016'},ensure_ascii=False))

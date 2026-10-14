"""Trim one administrative EOF blank, recheck the published handoff, commit exact paths."""
import difflib
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys

R=Path('C:/math'); RUN=R/'docs/do-math/continuous-development-2026-10-13'
O=Path(__file__).resolve().parent
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,obj): (O/n).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def git(*args): return subprocess.check_output(['git',*args],cwd=R)
def command(name,args):
    p=subprocess.run(args,cwd=R,capture_output=True)
    row={'argv':args,'cwd':str(R),'exit_code':p.returncode,'stdout':p.stdout.decode('utf-8',errors='replace'),'stderr':p.stderr.decode('utf-8',errors='replace')}
    save(name,row); assert p.returncode==0,row

plan=read(O/'commit-plan.json'); head=plan['head']
assert git('rev-parse','HEAD').decode().strip()==head
assert set(filter(None,git('diff','--cached','--name-only','-z').decode().split('\0')))==set(plan['paths'])
assert all(sha(R/p)==h for p,h in plan['sha256'].items())
source=read(O/'source-inspected.json'); assert all(sha(R/p)==h for p,h in source.items())
published=RUN/'phases/020/manager.json'; manager_hash=sha(published)
problem=read(O/'staged-diff-check.json')
assert problem['exit_code']==2 and problem['stdout']== 'docs/do-math/continuous-development-2026-10-13/context.md:312: new blank line at EOF.\n'
context=RUN/'context.md'; before=context.read_bytes()
assert before.endswith(b'\n\n') and not before.endswith(b'\n\n\n')
context.write_bytes(before[:-1])
assert context.read_bytes()+b'\n'==before
diff=''
for name in ('context.md','plan.md','seams.md'):
    old=git('show',head+':'+(RUN/name).relative_to(R).as_posix()).decode('utf-8-sig').replace('\r\n','\n')
    new=(RUN/name).read_text(encoding='utf-8')
    if name=='context.md': assert old.split('## C2 ')[0]==new.split('## C2 ')[0]
    diff+=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=name+' before 020',tofile=name+' after 020'))
(O/'common-docs.diff').write_text(diff,encoding='utf-8',newline='\n')
relative=sorted(set(plan['paths'])|{Path(__file__).relative_to(R).as_posix(),(O/'publication-correction.json').relative_to(R).as_posix()})
save('publication-correction.json',{'reason':'Post-publication Git whitespace check found exactly one new blank line at context EOF. Removed one LF only, regenerated the common-document diff, and rechecked the published manager candidate before committing. No product, requirement, assignment or manager decision changed.',
 'before_context_sha256':hashlib.sha256(before).hexdigest(),'after_context_sha256':sha(context),'removed_bytes':1,
 'original_check':problem,'manager_sha256':manager_hash,'recheck_candidate':'manager.json'})
pres=read(O/'preservation.json'); pres['tracked_paths']=relative; save('preservation.json',pres)
assert all(sha(R/p)==h for p,h in pres['entries'].items())
command('handoff-recheck.json',[sys.executable,'-B','services/continuous-development/check.py','handoff',str(R),str(RUN),'020','manager.json'])
assert sha(published)==manager_hash
assert all(sha(R/p)==h for p,h in source.items())
hashes={p:sha(R/p) for p in relative}
(O/'commit-paths.nul').write_bytes(b'\0'.join(p.encode('utf-8') for p in relative)+b'\0')
save('commit-plan-final.json',{'head':head,'paths':relative,'sha256':hashes,'products':24})
command('stage-final-command.json',['git','add','-f','--pathspec-from-file='+str(O/'commit-paths.nul'),'--pathspec-file-nul'])
assert set(filter(None,git('diff','--cached','--name-only','-z').decode().split('\0')))==set(relative)
command('staged-final-diff-check.json',['git','diff','--cached','--check'])
data=subprocess.check_output(['git','cat-file','--batch'],cwd=R,input=('\n'.join(':'+p for p in relative)+'\n').encode('utf-8'))
stream=io.BytesIO(data); received={}
for path in relative:
    oid,kind,size=stream.readline().decode().split(); assert kind=='blob'
    blob=stream.read(int(size)); assert stream.read(1)==b'\n'
    raw=(R/path).read_bytes()
    if '/evidence/' in path or '/manager-evidence/' in path or path.endswith(('/report.json','/manager.json')): assert blob==raw,path
    else: assert blob==raw or blob==raw.replace(b'\r\n',b'\n'),path
    received[path]={'blob':oid,'sha256':sha(R/path),'raw_equals_blob':blob==raw}
assert not stream.read()
save('stage.json',{'head':head,'count':len(relative),'products':24,'paths':received})
assert git('rev-parse','HEAD').decode().strip()==head
assert set(filter(None,git('diff','--cached','--name-only','-z').decode().split('\0')))==set(relative)
assert all(sha(R/p)==h for p,h in source.items()) and all(sha(R/p)==h for p,h in hashes.items())
assert [p for p in relative if p.startswith('기억/layer1/')]==['기억/layer1/M-0570.md']
assert sorted((R/'기억/layer1').glob('M-*.md'))[-1].name=='M-0570.md'
command('pre-commit-status.json',['git','status','--short','--untracked-files=no'])
(O/'commit-message.txt').write_text('지급 도구 문서 결속을 마감하고 검토 입력과 고정 원자료 검증을 배정함\n',encoding='utf-8')
command('commit.json',['git','commit','--file',str(O/'commit-message.txt')])
newhead=git('rev-parse','HEAD').decode().strip()
committed=set(filter(None,git('diff-tree','--no-commit-id','--name-only','-r','-z',newhead).decode().split('\0')))
assert committed==set(relative)
tree=git('ls-tree','-r','-z',newhead)
blobs={entry.split(b'\t',1)[1].decode('utf-8'):entry.split(b'\t',1)[0].decode().split()[2] for entry in tree.split(b'\0') if entry}
assert all(blobs[p]==v['blob'] for p,v in received.items())
assert all(sha(R/p)==v['sha256'] for p,v in received.items()) and all(sha(R/p)==h for p,h in source.items())
assert not git('diff','--cached','--name-only','-z')
save('post-commit.json',{'head':newhead,'parent':head,'committed_count':len(relative),'products':24,'source_raw_bytes_unchanged':True,'task_raw_bytes_preserved':True,'index_empty':True,'manager_sha256':manager_hash,'next':'021','push_performed':False})
print(json.dumps({'head':newhead,'committed':len(relative),'products':24,'handoff':'PASS 020 manager.json','next':'021'},ensure_ascii=False))

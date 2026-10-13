"""Resume administrative commit after the retained EOF whitespace rejection."""
from pathlib import Path
import difflib
import hashlib
import json
import re
import subprocess
import sys

R=Path('C:/math'); RUN=R/'docs/do-math/continuous-development-2026-10-13'; O=Path(__file__).parent
def read(p): return json.loads(p.read_bytes())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v): (O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def git(*args): return subprocess.check_output(['git',*args],cwd=R)
def cmd(n,args,allowed=(0,)):
    p=subprocess.run(args,cwd=R,capture_output=True)
    v={'argv':args,'cwd':str(R),'exit_code':p.returncode,'stdout':p.stdout.decode('utf-8',errors='replace'),'stderr':p.stderr.decode('utf-8',errors='replace')}
    save(n,v); assert p.returncode in allowed,(n,p.returncode,v['stderr'])
    return v

head=git('rev-parse','HEAD').decode().strip(); plan=read(O/'commit-plan.json')
assert head==plan['head']
assert set(filter(None,git('diff','--cached','--name-only','-z').decode().split('\0')))==set(plan['paths'])
assert read(O/'noncorpus-diff-check.json')['stdout'].strip()=='docs/do-math/continuous-development-2026-10-13/context.md:235: new blank line at EOF.'
for name in ['staged-diff-check.json','noncorpus-diff-check.json','commit-plan.json']:
    original=O/name; retained=O/('initial-'+name); assert not retained.exists(); retained.write_bytes(original.read_bytes())
p=RUN/'context.md'; text=p.read_text(encoding='utf-8'); p.write_text(text.rstrip()+'\n',encoding='utf-8')
diff=''
for name in ['context.md','plan.md','seams.md']:
    old=git('show','HEAD:docs/do-math/continuous-development-2026-10-13/'+name).decode('utf-8-sig').replace('\r\n','\n')
    new=(RUN/name).read_text(encoding='utf-8')
    diff+=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=name+' before',tofile=name+' after'))
(O/'common-docs.diff').write_text(diff,encoding='utf-8')
p=O/'review.md'; text=p.read_text(encoding='utf-8'); p.write_text(text.rstrip()+'\n\n관리 마감의 첫 Git whitespace 검사는 context.md 끝의 빈 줄 한 건을 반려했다. 그 관리 문서 공백만 제거하고 common-docs.diff를 갱신한 뒤 게시된 manager.json을 대상으로 handoff를 다시 검사했다. 제품·시험/원자료와 manager 판단은 불변이다. 최초 staged/noncorpus 검사 출력은 initial- 접두 원파일로 보존한다.\n',encoding='utf-8')
relative=sorted(set(plan['paths'])|{(O/'resume_commit.py').relative_to(R).as_posix()})
preservation=read(O/'preservation.json'); preservation['tracked_paths']=relative; save('preservation.json',preservation)
source=read(O/'source-inspected.json'); assert all(sha(R/p)==h for p,h in source.items())
products=set(plan['paths']) & set(preservation['products'])
assert len(products)==32
published=RUN/'phases/014/manager.json'; pending_hash=sha(published)
save('commit-plan.json',{'head':head,'paths':relative,'sha256':{p:sha(R/p) for p in relative},'products':len(products)})
(O/'commit-paths.nul').write_bytes(b'\0'.join(p.encode('utf-8') for p in relative)+b'\0')
cmd('memory-check.json',[sys.executable,'-B','기억/scripts/validate_memory_index.py'])
cmd('handoff-check.json',[sys.executable,'-B','services/continuous-development/check.py','handoff',str(R),str(RUN),'014','manager.json'])
cmd('stage-command.json',['git','add','-f','--pathspec-from-file='+str(O/'commit-paths.nul'),'--pathspec-file-nul'])
assert set(filter(None,git('diff','--cached','--name-only','-z').decode().split('\0')))==set(relative)
print('PASS rechecked handoff; resume exact blob validation and commit',flush=True)
# The unchanged reviewed finalization tail performs whitespace, every staged
# clean/blob/raw comparison, source recheck, one-memory check, commit and receipt.
tail=(O/'finalize.py').read_text(encoding='utf-8').split('whitespace=cmd(',1)[1]
exec(compile('whitespace=cmd('+tail,str(O/'finalize.py')+' [resume tail]','exec'))

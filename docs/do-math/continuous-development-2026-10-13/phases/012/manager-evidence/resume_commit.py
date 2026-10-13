"""Finish the administrative commit after auditing verbatim corpus whitespace."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

ROOT=Path('C:/math')
RUN=ROOT/'docs/do-math/continuous-development-2026-10-13'
OUT=Path(__file__).resolve().parent
def read(p): return json.loads(p.read_bytes())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,v): (OUT/name).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def git(*args): return subprocess.check_output(['git',*args],cwd=ROOT)
def command(name,argv):
    p=subprocess.run(argv,cwd=ROOT,capture_output=True)
    save(name,{'argv':argv,'cwd':str(ROOT),'exit_code':p.returncode,'stdout':p.stdout.decode('utf-8',errors='replace'),'stderr':p.stderr.decode('utf-8',errors='replace')})
    assert p.returncode==0,(name,p.returncode)

plan=read(OUT/'commit-plan.json'); head=plan['head']
assert git('rev-parse','HEAD').decode().strip()==head
source=read(OUT/'source-inspected.json')
assert all(sha(ROOT/p)==v for p,v in source.items())
initial=read(OUT/'staged-diff-check.json'); assert initial['exit_code']==2
allowed={tree+'/skills/do-math/scripts/tests/corpus/manifest.json' for tree in ('.claude','.agents')}
headers=[]
for line in initial['stdout'].splitlines():
    match=re.fullmatch(r'(.+):(\d+): (trailing whitespace(?:, indent with spaces)?\.)',line)
    if match: headers.append(match.groups())
assert len(headers)==286 and {p for p,_,_ in headers}==allowed
blobs={p:git('show',':'+p) for p in allowed}
for p,number,kind in headers:
    line=blobs[p].splitlines(keepends=True)[int(number)-1]
    assert line.endswith(b'\r\n') and line[:-2]==line[:-2].rstrip(b' \t'),(p,number)
    if 'indent' in kind:
        indent=line[:-2][:len(line[:-2])-len(line[:-2].lstrip(b' '))]
        assert len(indent)>=8 and len(indent)%2==0 and b'\t' not in line[:len(indent)]
for p,raw in blobs.items():
    assert raw==(ROOT/p).read_bytes() and len(json.loads(raw)['entries'])==19
    assert json.loads(raw)['entries'][:-1]==json.loads(git('show','HEAD:'+p))['entries']
argv=['git','diff','--cached','--check','--','.']+[':(exclude)'+p for p in sorted(allowed)]
command('noncorpus-diff-check.json',argv)
save('stage-whitespace-audit.json',{'initial_check':'staged-diff-check.json','initial_check_sha256':sha(OUT/'staged-diff-check.json'),'warning_count':len(headers),'paths':sorted(allowed),'result':'accepted_raw_format','reason':'Every warning is a preserved CRLF terminator or existing two-space JSON indentation. No trailing spaces/tabs precede CRLF. Both -text manifests retain the exact validated working bytes and old 18 entries. Product/corpus attributes and contents were not changed to silence lint. All other staged paths pass the ordinary whitespace check.','raw_equals_index':True,'source_hashes_unchanged':True,'noncorpus_check':'noncorpus-diff-check.json'})
note='''# phase 012 커밋 행정 마감

첫 finalize.py는 기억/인계 검사와 manager.json 게시 뒤 Git 공백 검사에서 멈췄다. 원 출력은 staged-diff-check.json의 exit2로 보존한다. 지적286건은 양쪽 corpus/manifest.json의 새 항목 구간에만 있으며 모두 원바이트의 CRLF 또는 기존 두 칸 JSON 들여쓰기다. 각 해당 줄을 Git index blob에서 직접 읽어 CRLF 앞의 실제 공백/탭이 없고 들여쓰기가 짝수 칸임을 확인했다. 두 manifest는 기존 -text 속성대로 작업트리 원바이트와 index가 같고 이전18항목도 유지한다.

제품·속성·원보고를 수정하지 않았다. 두 원바이트 manifest 외 전체 stage에는 일반 diff --check를 그대로 적용해 통과했다. 이 제한된 형식 판정은 task 성공을 새로 만드는 시험 변경이 아니다. stage-whitespace-audit.json과 초기 검사 출력, resume_commit.py가 판단/후속 마감 근거다. 보존 목록에 행정 근거를 더한 뒤 manager.json을 candidate로 handoff를 다시 검사하고 정확 stage/바이트 대조 후 커밋한다. 원 task와 공용 요구·다음 배정은 바뀌지 않았다.
'''
(OUT/'administrative-closeout.md').write_text(note,encoding='utf-8')
extra=['resume_commit.py','stage-whitespace-audit.json','staged-diff-check.json','noncorpus-diff-check.json','administrative-closeout.md']
relative=sorted(set(plan['paths'])|{(OUT/p).relative_to(ROOT).as_posix() for p in extra})
pres=read(OUT/'preservation.json'); pres['tracked_paths']=relative
pres['administrative_closeout']='administrative-closeout.md records the unchanged corpus CRLF/JSON indentation audit and the resumed exact commit.'
save('preservation.json',pres)
hashes={p:sha(ROOT/p) for p in relative}
save('commit-plan-final.json',{'head':head,'paths':relative,'sha256':hashes,'products':plan['products']})
(OUT/'commit-paths-final.nul').write_bytes(b'\0'.join(p.encode() for p in relative)+b'\0')
command('handoff-recheck.json',[sys.executable,'-B',str(ROOT/'services/continuous-development/check.py'),'handoff',str(ROOT),str(RUN),'012','manager.json'])
assert all(sha(ROOT/p)==v for p,v in hashes.items())
assert set(filter(None,git('diff','--cached','--name-only','-z').decode().split('\0')))==set(plan['paths'])
command('stage-supplement.json',['git','add','-f','--pathspec-from-file='+str(OUT/'commit-paths-final.nul'),'--pathspec-file-nul'])
assert set(filter(None,git('diff','--cached','--name-only','-z').decode().split('\0')))==set(relative)
staged={}; products=set(pres['products'])
for p in relative:
    raw=(ROOT/p).read_bytes(); blob=git('rev-parse',':'+p).decode().strip()
    clean=subprocess.check_output(['git','hash-object','--path='+p,'--stdin'],cwd=ROOT,input=raw).decode().strip()
    assert clean==blob,p
    received=git('show',':'+p)
    if '/evidence/' in p or '/manager-evidence/' in p or '/tests/corpus/' in p or p.endswith(('/report.json','/manager.json')): assert received==raw,p
    if p in products: assert received.replace(b'\r\n',b'\n')==raw.replace(b'\r\n',b'\n'),p
    staged[p]={'sha256':hashlib.sha256(raw).hexdigest(),'blob':blob,'raw_equals_blob':received==raw}
save('stage.json',{'head':head,'paths':staged,'exact_count':len(relative),'product_count':len(products),'whitespace_audit':'stage-whitespace-audit.json'})
assert git('rev-parse','HEAD').decode().strip()==head
assert all(sha(ROOT/p)==v['sha256'] for p,v in staged.items())
assert all(sha(ROOT/p)==h for p,h in source.items())
assert set(filter(None,git('diff','--cached','--name-only','-z').decode().split('\0')))==set(relative)
assert [p for p in relative if p.startswith('기억/layer1/')]==['기억/layer1/M-0562.md']
(OUT/'commit-message.txt').write_text('Lean 실연쇄를 검수하고 시험 전용 예약 경계를 배정함\n',encoding='utf-8')
command('commit.json',['git','commit','--file',str(OUT/'commit-message.txt')])
newhead=git('rev-parse','HEAD').decode().strip()
assert set(filter(None,git('diff-tree','--no-commit-id','--name-only','-r','-z',newhead).decode().split('\0')))==set(relative)
assert all(git('rev-parse',newhead+':'+p).decode().strip()==v['blob'] for p,v in staged.items())
assert all(sha(ROOT/p)==v['sha256'] for p,v in staged.items())
assert all(sha(ROOT/p)==h for p,h in source.items())
assert not git('diff','--cached','--name-only','-z')
save('post-commit.json',{'head':newhead,'parent':head,'committed_count':len(relative),'products':len(products),'source_raw_bytes_unchanged':True,'index_empty':True,'manager_sha256':sha(RUN/'phases/012/manager.json'),'next':'013','push_performed':False})
print(json.dumps({'head':newhead,'committed':len(relative),'products':len(products),'handoff':'PASS 012','next':'013'},ensure_ascii=False))

"""Clarify five reading findings without changing product scope or criteria."""
import difflib
import hashlib
import json
from pathlib import Path
import subprocess
import sys
R=Path('C:/math'); RUN=R/'docs/do-math/continuous-development-2026-10-13'; O=RUN/'phases/019/manager-evidence'
def write(p,t):p.write_text(t,encoding='utf-8',newline='\n')
def save(p,v):write(p,json.dumps(v,ensure_ascii=False,indent=2)+'\n')
reader=R/'.codex/writing-flow/continuous-phase019-manager/jobs/c25db1e9d5f1413ab95af35b20489631/readings/0fd7718575c440b0a9c03b7362bfea48/reader.json'
(O/'reading-result-1.json').write_bytes(reader.read_bytes())
decision={'verdict':'revise','alignment':'독해자는019 P02의 실제 생산/복원과 권한skip의 한계,020 P03의 여섯 소유자·설치 후 최종 입력과 전체G 미완료를 구별했다. 기술 원자료가 별도라는 불확실성은 실제 task의 필수 inputs 회수로 해소하는 경계다. 다만 현재/과거의 표현과 종료 시점, A20 소속, preview 소유관계 및 한 문장의 띄어쓰기를 명확히 한다. 합의의 검수 판정·후속 범위는 바꾸지 않는다.',
 'findings':[
 {'index':1,'action':'revise','reason':'C6에 이 실행의 관리 마감은 게시 후 정확한 커밋 확인까지이고 그 뒤 세션이 끝난다는 문장을 추가한다. protocol의 제출 후 계약 불변 조건을 유지한다.'},
 {'index':2,'action':'revise','reason':'C8의 현재는008 당시 모델 전환 이력을 서술한 말이다. phase008까지의 기록임을 명시해019까지의 검수 범위와 구별한다.'},
 {'index':3,'action':'revise','reason':'설계.md 3.3절과 결정A20에서 필수+선택 역방향을 확인했다. task의 A완료조건과 구별하도록 원문 문서와 절을 명시한다.'},
 {'index':4,'action':'revise','reason':'기존 seam 역사 문장의 띄어쓰기를 교정한다.011의 과거 범위/제품 의미는 그대로다.'},
 {'index':5,'action':'revise','reason':'doc_code에서 preview는 install_tools가 formal_verifier에 추가한 preview객체의 별도 문서owner다. A1에서 이 관계를 설명하고 서로 다른생산자로 해석하지 않게 한다.'}]}
save(O/'writing-decision-1.json',decision)
args=[sys.executable,'-B',str(R/'.claude/skills/write-for-reader/scripts/writing_flow.py'),'--session','continuous-phase019-manager','decide','--decision',str(O/'writing-decision-1.json')]
p=subprocess.run(args,cwd=R,capture_output=True)
save(O/'writing-decide-1.json',{'argv':args,'exit_code':p.returncode,'stdout':p.stdout.decode('utf-8',errors='replace'),'stderr':p.stderr.decode('utf-8',errors='replace')})
assert p.returncode==0
c=RUN/'context.md'; text=c.read_text(encoding='utf-8')
text=text.replace('Git 행정 마감이 code 변경이나 G 축소로 변하지 않게 한다.', '이 실행의 manager 세션은 게시 뒤 정확한 파일의 커밋과 그 결과 확인까지 마친 후 종료한다. 게시 뒤에는 제품·공용 계약·배정을 바꾸지 않는다. Git 행정 마감이 code 변경이나 G 축소로 변하지 않게 한다.',1)
text=text.replace('현재는 phase 001 세 task와 phase 002~008 각 한 task의 report를 각각 새 manager가 검사했다.', 'phase 008까지의 기록에서는 phase 001 세 task와 phase 002~008 각 한 task의 report를 각각 새 manager가 검사했다. 이후 검수 상태는 C2와 아래 phase별 기록을 따른다.',1)
text=text.replace('1-A의 원문 인용은 보존하되 A20의 필수+선택 필드 역방향을 적용한다.', '1-A의 원문 인용은 보존하되 repo:docs/do-math/시험-재편-2026-09-29/설계.md의3.3절·결정 A20에 따른 필수+선택 필드 역방향을 적용한다. 이 A20은 설계 결정 번호이며 task의 완료 조건 ID가 아니다.',1)
write(c,text)
plan=RUN/'plan.md'; text=plan.read_text(encoding='utf-8').replace('원래 1-A는 A20의 필수+선택 역방향을 적용하고', '원래 1-A는 설계.md의3.3절·결정 A20에 따른 필수+선택 역방향을 적용하고',1);write(plan,text)
seams=RUN/'seams.md'; text=seams.read_text(encoding='utf-8').replace('010 host의기존runtime소비성과와reading조사를검수했다.011은현_job_run의필수clock/environment를기존fixture에전달하고지정음성단언·읽기문구만교정한다.', '010 host의 기존 runtime 소비 성과와 reading 조사를 검수했다.011은 현 _job_run의 필수 clock/environment를 기존 fixture에 전달하고 지정 음성 단언과 읽기 문구만 교정한다.',1);write(seams,text)
objective=RUN/'phases/020/tasks/document-tools/objective.md'; text=objective.read_text(encoding='utf-8')
text=text.replace('execution_window의 경로 안내와 실제 동적 파일,', '문서의 preview 소유자는 install_tools가 formal_verifier 안에 추가한 formal_verifier.preview 객체를 별도로 순회하는 경계다. formal_verifier 전체와 그 preview 하위 객체를 검사하되 서로 다른 생산 결과로 만들지 않는다. execution_window의 경로 안내와 실제 동적 파일,',1)
text=text.replace('input/tools의 세 wrapper·submission-support.zip', 'input/tools의 check_submission.py·read_input.py·check_lean.py와 submission-support.zip',1);write(objective,text)
pending=RUN/'phases/019/manager.pending.json'; m=json.loads(pending.read_text(encoding='utf-8'))
m['context_updates'].insert(2,{'item':'C6','action':'amend','destination':['run:context.md#C6'],
 'reason':'기존 관리 마감의 순서를 명확히 했다. manager.json 게시 뒤 계약을 바꾸지 않고 정확한 커밋을 확인한 뒤 세션을 종료한다.',
 'evidence':['run:phases/018/manager-evidence/finalize.py','run:phases/019/manager-evidence/writing-decision-1.json']})
for row in m['context_updates']:
 if row['item']=='C8':row['reason']+=' 모델 전환 이력의008 당시 검수와 현재019 상태를 구별하도록 시점 표현을 명확히 했다.'
 if row['item']=='C9':row['reason']+=' A20을 설계.md의3.3절·설계 결정 번호로 명시했으며 검사 의무는 유지했다.'
m['plan_update']+=' A20의 원문 소속과 P03 preview 하위 객체 관계도 명확히 했다. seams의011 역사 문장은 의미를 유지하며 띄어쓰기만 교정했고 S계약 개정은 없다.'
save(pending,m)
diff=''
for name in ('context.md','plan.md','seams.md'):
 old=subprocess.check_output(['git','show','HEAD:'+ (RUN/name).relative_to(R).as_posix()],cwd=R).decode('utf-8-sig').replace('\r\n','\n')
 new=(RUN/name).read_text(encoding='utf-8')
 diff+=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=name+' before 019',tofile=name+' after 019'))
write(O/'common-docs.diff',diff)
paths=[R/p for p in json.loads((O/'draft-sources.json').read_text(encoding='utf-8'))]
write(O/'handoff-draft.md','\n\n'.join('# 파일: '+p.relative_to(R).as_posix()+'\n\n'+p.read_text(encoding='utf-8') for p in paths))
save(O/'draft-sources.json',{p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
print('Clarified five reading findings; scope and acceptance remain unchanged.')

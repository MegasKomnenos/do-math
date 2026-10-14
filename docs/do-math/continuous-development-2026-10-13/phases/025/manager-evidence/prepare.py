"""Prepare the reviewed handoff and bounded independent work assignments."""
import difflib
import hashlib
import json
from pathlib import Path

R=Path('C:/math'); RUN=R/'docs/do-math/continuous-development-2026-10-13'; O=Path(__file__).resolve().parent
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def write(p,s): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(s.rstrip()+'\n',encoding='utf-8')
assert not (RUN/'phases/026').exists()
before={n:(RUN/n).read_text(encoding='utf-8') for n in ('context.md','plan.md','seams.md')}
for n in before: (O/(n+'.before')).write_bytes((RUN/n).read_bytes())
save(O/'common-before-sha.json',{n:sha(RUN/n) for n in before})
V=read(O/'verification.json'); assert V['products_to_commit']==26 and V['original_task_files_unchanged']==252
packet=read(RUN/'phases/001/tasks/document-closeout/evidence/followup-packets.json')
packets={p['id']:p for p in packet['packets']}
common=['run:sources/user-decisions.md','run:sources/model-policy-2026-10-14.md','run:sources/document-batching-2026-10-14.md',
 'run:phases/001/tasks/document-closeout/evidence/followup-packets.json','run:phases/001/tasks/document-closeout/evidence/binding-inventory.json',
 'run:phases/001/tasks/closure-map/evidence/requirement-state.json','run:phases/001/tasks/closure-map/evidence/prior-review-state.json',
 'run:phases/025/manager-evidence/source-inspected.json','run:phases/025/manager-evidence/verification.json','run:phases/025/manager-evidence/review.md',
 'repo:docs/do-math/시험-재편-2026-09-29/설계.md','repo:docs/do-math/시험-재편-2026-09-29/조사/결함-범주.md',
 'repo:.claude/skills/do-math/AGENTS.md','repo:.claude/skills/do-math/scripts/tests/시험-지침.md',
 'repo:.claude/skills/do-math/scripts/tests/support/doc_code.py','repo:.claude/skills/do-math/scripts/tests/structure/test_doc_code.py']
policy_docs=['.claude/skills/do-math/README.md','.claude/skills/do-math/references/CLI-실행-계약.md','.claude/skills/do-math/references/초기화-운전.md']
policy_code=['initialization_engine.py','lifecycle_engine.py','initialization.py','configuration.py','execution_profiles.py','execution_window.py','supervision.py','external_engine.py','control_contracts.py']
tasks=[dict(id='policy-semantics',model='gpt-6.1-sol',effort='high',inputs=common+[
 'run:phases/024/tasks/document-waits/evidence/policy-name-decisions.json',
 'run:phases/024/tasks/document-waits/report.json']+['repo:'+p for p in policy_docs]+
 ['repo:.claude/skills/do-math/scripts/do_math/'+p for p in policy_code],writes=[],provides=[],uses=[])]
for ident,pid in [('reference-names','N02'),('role-contract-names','N03')]:
 tasks.append(dict(id=ident,model='gpt-6.1-sol',effort='high',inputs=common+packets[pid]['document_partition']+[
  'run:phases/022/tasks/review-delivery/evidence/section-name-decisions.json',
  'run:phases/023/manager-evidence/review.md','run:phases/024/manager-evidence/review.md',
  'repo:.claude/skills/do-math/scripts/do_math/contracts.py','repo:.claude/skills/do-math/scripts/do_math/role_input_requirements.py',
  'repo:.claude/skills/do-math/scripts/do_math/record_schemas/schemas.py'],writes=[],provides=[],uses=[]))
save_path=RUN/'phases/026/phase.json'; save_path.parent.mkdir(parents=True)
save(save_path,dict(kind='work',purpose='AST 반환 교체 뒤 남은 정책 의미와 공통 참조/역할 계약 이름을 고정판에서 독립 판정하고 정확 수리만 후속 통합한다.',tasks=tasks))
for task in tasks:
 (RUN/'phases/026/tasks'/task['id']/'evidence').mkdir(parents=True)
 (RUN/'phases/026/tasks'/task['id']/'evidence/.gitkeep').write_text('',encoding='utf-8')
write(RUN/'phases/026/logs/.gitkeep','')
boundaries='''## 판단과 경계

이번 work는 고정판의 한정 조사·판정이다. 제품 writes는 비어 있으며 자기 report/evidence에만 쓴다. 같은 phase의 다른 task 결과를 읽거나 기다리지 않는다. 모든 task가 동일025 검수판을 읽어 공유 helper/문서/미러/캐시에 대한 동시 쓰기가 없다. 소스·문서·공용 정보·기존 task 자료를 고치지 않는다. 공식 run_tests·미러 생성·유료/OS/Lean/예약/학술 호출과 기존 연구 조작은 실행하지 않는다. Git stage/commit/reset/checkout/push와 graphify 갱신도 없다. Python 보조 분석은 -B로 자기 evidence만 사용하고 제품 모듈을 실행해 외부 상태를 바꾸지 않는다.

존재하는 이름의 전역 집합이나 일반 green을 의미 검증으로 쓰지 않는다. 이미 승인된 P01~P11/PURE·지정 N 문장은 현재 판본과 성질이 같을 때 연결해 재사용한다. 조사 complete는 실행 관문 통과나 제품 전체 합격이 아니다. 새로운 검사가 필요한 발견은 최소 입력·독립 기대·현재 코드상 실제 결과/미관측·필요 수정 경로와 정확 시험 선택으로 반환한다. 사용자의 권한·정책을 바꾸지 않으며 L01 Q1/Q2·원문byte 미충족은 그대로다. 소스/판본 불일치는 추정으로 덮지 않고 영향받는 판정을 보류한다.

## 검증 방법

cwd C:\\math, Python C:\\Users\\wogud\\AppData\\Local\\Programs\\Python\\Python312\\python.exe. 시작과 끝에025 manager source-inspected의 SHA를 대조한다. 읽기 검색은 rg, 근거는 현재 원문·함수·공유 schema·시험 본문과 실제 원보고의 판본/정확 row다. 필요한 구간은 잘리지 않게 읽고 역사 후보 목록의 이름 수를 검증 완료율로 삼지 않는다. 새 대규모 목록/추론기/프레임워크를 만들지 않는다. 판정표의 모집단과 각 판정의 근거를 보조 스크립트로 대조해 자기 evidence에 출력한다. 원문을 실행했다거나 시험을 새로 통과했다고 쓰지 않는다.

모든 A와 findings를 report.json으로 작성하고 지정 Python으로 services/continuous-development/check.py report C:\\math C:\\math\\docs\\do-math\\continuous-development-2026-10-13 026 TASK 를 통과한다. 마지막 응답에 status와 report 경로를 알린다.
'''
policy='''## 목적과 역할

024 F2의 다섯 정책 이름을 정의 존재 확인에서 현재 동작의 한정 판정으로 옮긴다. conversation_loss_policy, disconnect_policy, model_policy, external_policy, adopt_default_review_policy의 문서상 주장을 실제 승인·저장·소비와 연결한다. 관련 정의와 원문 좌표는024 policy-name-decisions에 있다. 한정 질문의 답과 근거/정확 수리 후보를 반환해 다음 통합 work를 결정하게 한다. L01이나 정책 전체 재설계는 맡지 않는다.

## 완료 조건

### A1 원문과 판본·소유

025 검수판과 시작 SHA를 대조한다.024 다섯 이름의 기존 모든 occurrence를 현재 문장으로 연결하고 N01-020/218/230/268/273 중 해당 이름의 문장·예제만 판정 모집단으로 확정한다. 이름별 의미/정의/생산/저장/소비·승인 주체를 기록한다. model_policy 모듈 이름, profile lock 불일치 분류와 실제 설정 필드는 구별한다. 다른 N01 절의 전체 이름 검토로 확장하지 않는다.

### A2 현재 동작과 기존 검증의 대조

conversation attach의 generation·lease·명시 disconnect_policy 갱신/생략·대화 소실, pause와 continue_authorized의 차이 및 사용자 정지/HOLD/허가 만료·철회를 실제 consumer와 대조한다. 초기화 성공과 독립 운전의 승인 조건을 구별한다. external_policy의 disabled/explicit_grants와 실제 효과별 허가, adopt_default_review_policy의 현재 판본 결박·설정 hash/probe/adoption의 currentness, model_policy의 실제 역할/프로필 선택과 잠금 실패 분류를 현재 함수·정확 시험 단언에 연결한다. 기존 보고가 입증한 실행과 소스만 확인한 성질을 분리하고 필요한 원보고가 없으면 미관측을 남긴다.

### A3 처분 가능한 종료 결과

다섯 이름 전부에 유지/문구 교정/시험 공백/제품 반례/외부 결정 중 근거 있는 판정을 내린다. 이 분류는 제품 합격 상태가 아니라 후속 행동이다. 충분한 기존 근거는 현재 판본과 한정 재사용 조건을 적어 종결 후보로, 결함은 최소 반례·원문 기대·실제 분기·수정할 파일·필요 검사를 적어 단일 통합 work 후보로 반환한다. 전역 어휘 존재·표 형식만으로 통과시키지 않는다. 관련 PR/B slice는 이번에 다룬 hunk와 소비만 검토하고 다른 영역의 counts를 합산하지 않는다.

### A4 독립성과 보존

시작/끝 소스 전건 불변과 자기 자료의 원문 좌표를 확인한다. 다른 두 task와 미완성 자료·공유 실행 환경 의존이 없다. report의 findings는 G1/G2/G3에 연결하고 남은 N01/L01·최종 관문을 보존한다.

'''
write(RUN/'phases/026/tasks/policy-semantics/objective.md',policy+boundaries.replace('TASK','policy-semantics'))
for ident,pid,role in [('reference-names','N02','공통 실행·착수조건·모델예산·입력 소비·자기점검·지식·학술 참조 7문서'),('role-contract-names','N03','역할 계약 11문서')]:
 docs='\n'.join('- '+x for x in packets[pid]['document_partition'])
 specific=('기존 N02-002와 N02-014의 전문 단일 지급/재시도/개정 이름 판정은022~024 근거를 재사용한다. 모델과 실행예산의 능력 요구/예산, 입력 소비자·자기점검의 역할별 입력/출력, 학술 configured와 실제 완료 구별을 보존한다.' if pid=='N02' else
 '독립-운영의 installation_root 문장은008~009 성과를 재사용한다. 의도-해석의 import_unit/question_detail 산문 단수형을 실제 배열 원소 소유자로 구별하고 P06/P10은023 근거를 재사용한다. 역할 산출의 동일 이름도 stage·역할·공유 schema가 다르면 별도로 판정한다.')
 body=f'''## 목적과 역할

{pid}의 {role}에서 남은 단독/조합 이름·표·코드 예제를 현재 소유자와 계약에 연결한다. AST 반환 교체 P01~P11은025까지 검수됐으므로 재구현하지 않는다. 서로 독립적인 문서 이름 판정을 고정판에서 병렬로 완료하고, 필요한 공통 문서/helper 수리만 다음 work에 모으기 위한 조사다. 이번에 읽을 문서의 합집합은 다음과 같다.

{docs}

## 완료 조건

### A1 고정 모집단과 현재 원문

시작025 source-inspected SHA를 대조한다. followup-packets의 {pid} required_slices를 현재 제목/문장으로 연결해 위 문서 전부의 이름·표·코드펜스를 읽는다. 기존 lexical 후보는 찾아보기이며 고정 의미 분모가 아니다. 현 원문에서 추가/소멸한 이름과 코드펜스/산문 이름도 대조하고 문서별 누락 없이 판정 대상/기존 재사용/비코드 제외를 정한다. 문서의 모든 연구 절차를 재설계하거나 전 기능을 다시 감사하는 작업은 아니다.

### A2 실제 소유자와 문맥별 판정

이름을 실제 명령/인자/공유 schema·역할 산출·정책/등록부·파일명·산문 단수형 등 해당 문맥으로 연결한다. 같은 이름의 다른 역할 필드, 잘못된 조합/단축 명령을 전역 존재로 승인하지 않는다. schema가 표현하지 못하는 문서 주장은 직접 소비 함수와 해당 단언을 따라간다. {specific} 충분한 현재 근거는 재사용하고 부족한 축만 구체적 종료 질문으로 남긴다. policy-semantics가 맡은 다섯 정책의 의미는 별도 경계로 표시하며 그 결과를 기다리지 않는다. L01의 출력byte·실제 읽기 인증도 기존 외부 결정으로 유지한다.

### A3 유한한 판정과 수리 후보

문서별 이름/조합에 정의·실제 소비·현재 시험 또는 구체적인 비코드 제외 사유를 붙여 evidence의 판정표로 제출한다. 반복 이름은 동일 소유자/의미를 한 판정으로 묶되 원문 occurrence 좌표는 유지한다. 유지/교정/제거/추가 검증 여부와 이유를 구별한다. 문구 교정은 정확 위치와 제안 문장, 검사 공백은 최소 정상/반례와 독립 기대·수정 경로·공식 선택을 반환한다. 결함이 없으면 근거 있는 유지 판정을 반환하며 새 장치를 억지로 제안하지 않는다. 관련 PR24/B110~B114는 실제 다룬 slice만 대조한다. 이전 검수와 합집합/중복·남김을 설명해 다른 {('N01/N03' if pid=='N02' else 'N01/N02')} 전체 완료로 확대하지 않는다.

### A4 보존과 인도

시작/끝 소스 전건 불변을 확인하고 기존 원보고/근거를 다시 쓰지 않는다. 각 A의 판정·현재 근거·미검사를 report에 연결한다. 새 제품 실행 없이 확인한 정의/소비/시험 본문과 기존 실제 실행 row의 증언 범위를 구별한다. 최종 일반/freshT3/변이/G7/최종review를 닫지 않는다.

'''
 write(RUN/f'phases/026/tasks/{ident}/objective.md',body+boundaries.replace('TASK',ident))

base='run:phases/025/manager-evidence/'
summary='phase 025 document-trust의 A1~A5 complete를 검수했다. 시작2675파일은024 검수본과 같고 종료/현재 SHA 전건 일치 및 허용28변경(비캐시26·캐시2)을 확인했다. 정본/미러 동일185선택/고유row가 전부passed·exit0이며 각875Python/전후판본을 대조했다. 각122 trust 반환과 실제 설치 Job5개를 원JSONL에 연결해 null/분기별 부재/55변경의50목록·재결박을 검산했다. 부가 packaging 캡처는 각24오류로 미성공이며 unchanged review-stage 직접 단언의 통과와024 원자료 보존만 재사용한다. red3subTest·focus error1·초기 Lake 기대 failed1은 역사 실패로 보존했다. task252파일과024 원task352파일은 불변이다. 근거는 run:phases/025/manager-evidence/verification.json·return-check.json·review.md다. 지정 범위 완료이며 전체G 완료가 아니다.'
def add_section(text,section,paragraph):
 start=text.index('## '+section+' '); stop=text.find('\n## C',start+1)
 if stop<0: return text.rstrip()+'\n\n'+paragraph+'\n'
 return text[:stop].rstrip()+'\n\n'+paragraph+'\n'+text[stop:]
c=add_section(before['context.md'],'C2',summary)
old='phase 001~024의 task 세션은 종료됐다.025 document-trust 단일 work가 P08의 project/toolchain/environment_check와 N01-274/279/281의 직접 관련 문장을 통합한다. 공유 doc_code/engine_context·문서 순회·실 Lean/Lake·미러/캐시를 한 담당자가 소유한다. 기존 packet과 현 코드가 종료 질문을 제공하므로 별도 병렬 조사는 배정하지 않는다. runtime/runner/adapter·Job fixture·corpus·공유 설치/신뢰/연구는 고정하며 자기 전용 fixture에서 기존 실제 설치 검사를 순차 수행한다. jobs1·전체worker3 이하·동시에 한 묶음·소스 고정과 변경 영향에 따른 최종 선택을 유지한다. 정책 전체·다른N/L01과 최종 관문은 남는다.'
new='phase 001~025의 task 세션은 종료됐다.026은 policy-semantics(024 F2 다섯 정책), reference-names(N02 참조7문서), role-contract-names(N03 역할11문서)의 독립 work다. 전부 writes=[]이며 고정된025 소스·원문·기존 근거를 읽고 자기 report/evidence에만 쓴다. 제품 시험·미러 생성·공유 캐시·설치/OS 호출을 실행하지 않아 환경 충돌이 없다. 7문서는 현재810행, 11문서는1299행이며 문서의 이름/조합과 그 직접 소비로 범위를 한정한다. N01의 다른 이름·L01/최종 관문은 남는다. 조사 결과가 나온 뒤 필요한 공통 수정·미러·관련 회귀는 한 담당자가 통합한다. 공식 검사가 필요한 후속에는 jobs1·전체worker3 이하·한 묶음씩·소스 고정을 유지한다.'
assert old in c; c=c.replace(old,new)
c=add_section(c,'C8','025 gpt-6.1-sol/high 작업을 검수했고026 세 독립 work에도 같은 model/effort를 명시한다. manager와 제품 공급자 모델 설정은 변경하지 않는다.')
c=add_section(c,'C9','025 F2의 B113/B114 P08 AST 교체와 마지막 소비자가 사라진 producer_nodes/produced_object_schema/written_object_schema/consumed_object_schema 제거를 승인한다. 현재 호출부 부재·다른 기존 helper 함수 보존·실제 경계·존재7원보고 SHA를 대조했다. PR24 전체와 다른 hunk/역사counts의 새 성공은 아니다. 근거는 run:phases/025/manager-evidence/history-check.json·verification.json·review.md다.')
c=add_section(c,'C10','025 F1의 P08/TRUST 세 owner 및 N01-274/279/281 지정 문장을 닫는다. 실제 project/toolchain/environment_check의 null·변경목록 부재/제한·오류/재결박과 독립 입력 기대를 검수했다. P01~P11의 지정 AST 반환 교체는 끝났지만 전체24문서의 이름/의미 검증 완료는 아니다.025 F4의 부가 packaging raw 캡처는 bytes 직렬화 오류로 실패했으며 현재 전문1의 직접 단언과024의 불변 raw만 재사용한다. 후속 raw가 필요하면 JSON context/manifest와 원시 byte 파일을 별도로 보존한다.026은024 F2 정책 다섯 의미와 N02/N03의 고정 이름·조합 판정을 독립 수행하며, N01의 그 밖의 이름·L01 Q1/Q2와 원문byte 미충족을 보존한다. 근거는025 manager return-check.json·review.md와026 objectives다.')
c=add_section(c,'C11','025의 양쪽185passed는 부분 관련 실행이다. symlink 시험은 선택에 없고 기존1314 실제 반려 미검사는 유지한다. G4 기본전체·G5 freshT3·G6 전수변이·G7 최종판 연결·G8 최종review는 그대로 남는다.026의 읽기 판정으로 이 실행 관문을 대체하지 않는다.')
c=add_section(c,'C12','025 F3의 보존과 불변 하위 성질 재사용을 검수했다.024 기준139실호출입력·258고정경계·144corpus/150명시SHA/Gitraw-clean·host8/도구5·baseline910 및024원task352파일은 불변이다. 두 문서의 세 문단 변화는 미래 prompt/설치 문서 hash에 영향을 주며 과거 전체 설치/모델 독해의 실측으로 확대하지 않는다. 검수한26비캐시 제품/시험/문서/미러를 관리 커밋으로 마감한다.025원task252파일과26제품 원바이트는 manager-evidence/raw-evidence.zip에 보존하며 전건SHA와 선별추적범위는 run:phases/025/manager-evidence/preservation.json에 둔다. 압축만 추적하는 snapshot/관찰/scratch와 진행 로그·stage/commit 행정 수신은 로컬 보관으로 정리 때 사라질 수 있다. 압축은 복원 지시가 아니다.026배정·관리/기억 추가는 검수한 제품판본을 바꾸지 않는다.')
write(RUN/'context.md',c)
p=before['plan.md'].replace('## phase 001~024의 결과와 현재 상태','## phase 001~025의 결과와 현재 상태')
a=p.index('## 다음 phase: 025'); b=p.index('## 가까운 후속 배정과 선행 관계',a)
nextplan='''## 다음 phase: 026

gpt-6.1-sol/high의 고정판 독립 work 세 개를 배정한다. policy-semantics는024 F2의 다섯 정책 문장을 승인/저장/소비/기존 정확 단언과 대조한다. reference-names는 N02 참조7문서(현재810행), role-contract-names는 N03 역할11문서(현재1299행)의 단독/조합 이름·표·코드예제를 실제 역할별 소유자에 연결한다. 기존 P01~P11/PURE·지정 N 성과는 재사용하며 모든 연구 절차의 전수 재감사로 확장하지 않는다.

세 task는 writes=[]·자기 evidence만 사용하고 공식 제품 시험/미러/공유캐시/외부 호출을 실행하지 않는다. 동일025 소스가 고정돼 서로의 미완성 결과에 의존하지 않는다. 정책 담당은 N01의 해당 다섯 이름만 맡고 다른 두 담당은 그 의미/L01 외부 결정을 별도 경계로 표시한다. 알려진 결함 없이 새 공통 추론기나 수정부터 만들지 않고, 유지 가능한 부분을 닫고 실제 필요한 수리 경로/반례/검사를 반환한다. 그 결과를 다음 단일 통합 work에서 묶을지 manager가 판단한다. N01의 그 밖의 이름·L01 Q1/Q2/원문byte·기존symlink 미검사·최종 관문은 남는다.

'''
p=p[:a]+summary+'\n\n'+nextplan+p[b:]
oldstart=p.index('**024 manager의 묶음 결정:**'); oldend=p.index('\n\n',oldstart)
p=p[:oldstart]+'''**025 manager의 묶음 결정:** P08과 관련 N 문장을 검수해 AST 반환 교체를 마쳤다. 이제 남은 질문은 같은 helper 수정이 확정된 작업이 아니라 정책 동작/각 문맥의 이름 판정이다. 기존 packet의 세 고정 영역을 독립적으로 읽어 유지 가능한 부분을 닫고 정확 수리만 수집한다. 반복 회귀·미러·커밋을 문서마다 실행하지 않으며 후속 수정은 한 담당자가 통합한다. N01 다른 이름의 조사까지 무조건 한 세션에 넣지 않는다.''' +p[oldend:]
p=p.replace('025가P08/TRUST·같은owner의N문장을맡고024 F2정책전체·다른N은후속으로유지한다.','025 P08/TRUST·같은owner의N문장을검수했다.026은024 F2다섯정책과N02/N03이름을독립판정하고N01의다른이름은유지한다.')
p=p.replace('34 AST 구문지점의 제거 수로 진척을 세지 않고 마지막 소비자 뒤 helper를 정리한다.','025에서 마지막 AST 소비자와 네 추론 helper를 제거했다. 제거 수를 전체 문서 의미 완료율로 세지 않는다.')
write(RUN/'plan.md',p)
write(RUN/'seams.md',before['seams.md']+'\n025의 기존 project/toolchain/environment_check 경계 소비를 검수했다.026은 고정된 문서·현재 코드·기존 실행 근거를 독립 판정하며 제품 제공자/소비자나 새 인터페이스를 구현하지 않는다. 세 task의 writes/provides/uses는 비어 있고 S항목 개정은 없다. 새 수리가 필요하면 현재 정본과 최소 반례로 후속 배정에 반환한다.\n')
after={n:(RUN/n).read_text(encoding='utf-8') for n in before}
write(O/'common-docs.diff',''.join(''.join(difflib.unified_diff(before[n].splitlines(True),after[n].splitlines(True),fromfile=n+'.before',tofile=n)) for n in before))
save(O/'common-after-sha.json',{n:sha(RUN/n) for n in before})
save(O/'common-comparison.json',dict(changed=['C2','C5','C8','C9','C10','C11','C12'],unchanged=['C1','C3','C4','C6','C7'],
 removed_meaning='C5와plan의025 미래 배정을 검수 결과/026 고정판 독립 배정으로 교체했다. 기존 완료 기준·예외·미해결 외부 결정·역사실패는 삭제하지 않았다.',
 seams='제품 인터페이스/권한 의미 개정 없음.026 읽기 work 경계 설명만 추가했다.',next_tasks=[t['id'] for t in tasks]))
review='''# 025 manager 검수

document-trust report 전문과 objective A1~A5, 원근거/현재 소스를 대조해 complete를 지정 범위에서 승인한다. 형식 검사와 독립 검산은 verification.json에 있다. 시작2675파일은024 검수본과 같고 종료/현재가 전건 일치한다.28변경은 writes/report와 같고 비용캐시2를 제외한26제품·시험·문서·미러를 마감한다. runtime은 불변이다.

최종 정본/미러는 동일185선택/고유row 전부passed·실제exit0이다. 각875Python과 실행 전후 비캐시를 대조했다. 원JSONL의 각122 trust 반환(project40/toolchain2/environment80), 설치 Job5개의 실제 명령/종료와 승인된 해시를 확인했다. 실제 Lake 경로는 설치 lib/lean·src/lean/lake 및 전용 프로젝트 출력 경로의 독립 구성과 같고 non-Lake는 null이다. 환경 성공/재결박의 필드 부재, 입력 binding·변경55개의 앞50 및 초기 반려를 검산했다. 소스의 check_environment는 동일 조건에서 반환하며 baseline을 기록하지 않는다. 실제 기록 생산자를 쓰는 합성 host와 실 Lean/Lake/Job을 구별한다.

red3subTest, focus의73passed/1error, c의184passed/1failed는 보존하며 최종 exact ID의 passed에 대응했다. Lake 기대 수정은 설치 원문상 표준 경로 두 개의 누락 교정이다. 추가 prepare_role_input JSON 캡처 각24건은 raw bytes 때문에 실패했다. 새 전체 포장 원자료의 성공으로 세지 않는다. unchanged 현재 review-stage 시험의 전문1 직접 단언과024 원자료/producer 보존은 유효하므로 P08 완료를 막지 않는다. 이후 전체 포장 raw가 필요하면 JSON과 byte 파일을 따로 보존해야 한다.

B113/B114 P08 교체와 네 AST 추론 helper 제거는 마지막 소비자 부재, 다른 기존 helper 함수 본문 보존, 존재7원보고 SHA로 확인했다. 관련 PR24 slice만 승인하며 전체 PR24를 닫지 않는다. P01~P11의 지정 AST 반환 교체는 끝났지만 N 이름/정책 의미·L01/최종 관문은 남는다. 두 문서 세 문단은 null/분기별 부재·50목록/compact identity 설명만 명확히 하며 등록·활성화·컴파일·사람의 재기록 권한을 유지한다.

139실호출입력·258고정경계·144corpus/150명시SHA/Gitraw-clean·host8/도구5·baseline910은 불변이다. 원task252파일과024 원task352파일도 불변이다. 과거 실호출의 불변 하위 성질만 재사용하며 새 문서 독해/전체 설치 동등성을 주장하지 않는다. symlink는 이번 선택에 없어 기존1314 미검사를 유지한다.

026은 정책 다섯 의미, N02 참조7문서, N03 역할11문서의 이름/조합 판정을 고정판 독립 work로 배정한다. 모두 제품 쓰기·시험·미러/공유캐시 실행이 없어 충돌하지 않는다. 이미 검수한 경계를 재구현하지 않고 명확한 유지/교정/검사 공백을 반환한다. 다음 수정은 공유 helper와 미러/회귀를 한 담당자가 통합한다. N01의 다른 이름·L01의 외부 결정과 G4~G8 최종 관문은 보존한다. 개발 완료를 선언하지 않는다.

추적 진입점은 manager.json, verification.json, return-check.json, preservation.json과 raw-evidence.zip이다.252원task/26제품 바이트를 압축에 보존하고 선별 원경로를 직접 추적한다. 중복 snapshot/관찰/scratch 원경로·활성 로그와 stage/commit 수신은 로컬 보관이다. 압축은 복원 지시가 아니다.
'''
write(O/'review.md',review)
ev=[base+'verification.json',base+'review.md']
dispositions=[]
for ident,action,dest,reason in [
 ('F1','resolve',['run:context.md#C10'],'실제 반환/독립 기대/양쪽185passed로P08과지정세문장만종결한다.'),
 ('F2','resolve',['run:context.md#C9','run:context.md#C10'],'마지막호출부부재·나머지helper보존·역사hunk/7원보고를확인해한정교체/제거를승인한다.'),
 ('F3','carry',['run:context.md#C11','run:context.md#C12','run:plan.md'],'불변하위성질재사용과문서영향을보존하며symlink/L01/최종관문은계속후속책임이다.'),
 ('F4','resolve',['run:context.md#C10'],'부가packaging캡처실패를명시하고P08의온전한관찰·unchanged전문1직접단언·024raw보존으로한정완료를판정한다. 새전체캡처성공은주장하지않는다.')]:
 dispositions.append(dict(item='025/document-trust/'+ident,action=action,destination=dest,reason=reason,evidence=ev+[base+'return-check.json']))
updates=[]
reasons={'C2':'025의검수범위·실제counts/원관찰·실패와한계를추가한다.','C5':'종료된025배정을고정판독립026세work와환경비충돌로교체한다.','C8':'사용자지정모델을026세task에유지한다.','C9':'P08역사slice와네추론helper제거판정을추가하며PR24전체는유지한다.','C10':'P08종결·부가관찰한계·N/정책의다음범위를명시한다.','C11':'부분185passed와미실행최종관문/권한skip을구별한다.','C12':'불변하위재사용·26제품마감·252원task바이트보존범위를추가한다.'}
for cid,reason in reasons.items(): updates.append(dict(item=cid,action='amend',destination=['run:context.md#'+cid],reason=reason,evidence=ev+[base+'common-docs.diff']))
manager=dict(next='026',decision='025 document-trust A1~A5를 현재 소스·실제 원자료로 검수해 지정 complete를 승인한다. 양쪽185passed와 각122반환/5설치Job은 P08의 근거이며 부가 packaging24오류·기존symlink/L01/최종관문은 성공으로 바꾸지 않는다. 마지막 AST helper 제거는 소비자 부재 뒤 수행돼 승인한다.26비캐시 제품을 관리 마감한다.\n\n다음026은 정책 다섯 의미와 N02/N03 이름의 독립 판정이다. 현재7문서810행/11문서1299행의 고정 이름/조합과 직접소비만 맡겨 한 세션에 전체N01까지 밀어 넣지 않는다. 모두writes=[]이고 공식시험/미러/공유캐시를사용하지않아같은고정판에서독립진행한다. 검토된P01~P11성과를재사용하고필요수리만후속한담당자에게모아반복통합비용을줄인다. 이work는최종review가아니며G전체완료를선언하지않는다.',
 reports=[dict(task='document-trust',state='read',detail='report전문을읽고형식검사·현재2675파일·28허용변경·공식선택/row/exit·원JSONL/보존을검수했다. A1~A5complete는지정범위에서승인한다.',evidence=['run:phases/025/tasks/document-trust/report.json',base+'report-check.json']+ev)],
 dispositions=dispositions,context_updates=updates,plan_update='025 P08/TRUST 및 관련N지정문장을검수한결과를추가하고026정책·참조이름·역할이름의고정판독립work로다음배정을교체했다. N01다른이름/L01외부결정과G4~G8최종관문은유지한다. 기존유효이력·예외는common-docs.diff로보존을대조했다.',seam_updates=[],completion=None)
save(RUN/'phases/025/manager.pending.json',manager)
assert 'convention_version: 27' in (R/'기억/세칙.md').read_text(encoding='utf-8')
assert sorted((R/'기억/layer1').glob('M-*.md'))[-1].name=='M-0574.md'
write(R/'기억/layer1/M-0575.md','''---
id: M-0575
layer: 1
title: 신뢰 문서의 실제 반환 검수를 마치고 남은 이름 판정을 병렬 배정함
convention_version: 27
---

## 맥락

025 manager는 P08의 실제 trust 반환 검수와 다음 배정을 맡았다. 문서 작업을 번호마다 반복하지 말라는 사용자 지시에 따라 마지막 AST 소비가 끝난 뒤 작업 성격을 다시 구분했다. 공통 helper 수정이 필요한 단계는 한 담당자에게 모았고, 지금 남은 정책 의미와 서로 다른 문서의 이름 판정은 고정판을 읽는 독립 work로 배정했다.026의 세 task는 자기 evidence만 쓰며 공식 시험·미러·공유캐시를 실행하지 않는다. 수리 필요성이 확인되면 다음 담당자가 통합한다.

## 판단과 한계

실제 trust 원자료가 온전해도 더 넓게 시도한 포장 캡처는 실패할 수 있다. 이번 sys.monitoring의 prepare_role_input 반환에는 archive bytes가 있어 JSON 직렬화24건이 각 suite에서 실패했다. manager는 이를 새 전체 포장 근거로 승인하지 않았다. P08의122반환과5실설치Job, unchanged 전문1 직접 단언,024의 불변 raw를 각각 자기 성질의 근거로 사용했다. 관찰 범위의 공백과 제품 실패를 나눠 판정하는 데 필요한 좌표가 report에 있었으므로 같은185개 시험을 다시 실행할 이유는 없었다.

마지막 소비가 사라진 네 AST 추론 helper를 제거했지만, 이는 전체 문서 의미 검증의 종료가 아니다. 전역 이름 존재와 역할별 소유/소비도 다르므로 정책5개·공통참조7문서·역할계약11문서로 유한한 질문을 지정했다. N01의 다른 이름과 L01 외부 결정, 최종 관문은 유지한다. 거대한 packet을 처음에 통째로 출력해 절단이 발생했으며 뒤에는 필요한 키와 문서별 행수로 좁혔다. 후보 목록은 원문 판정의 진입점이다.

## 근거와 보존

추적 진입점은 docs/do-math/continuous-development-2026-10-13/phases/025/manager.json과 manager-evidence의 verification.json·return-check.json·review.md·preservation.json이다.26제품과252원task 바이트는 추적 raw-evidence.zip에 보존한다. 일부 snapshot/관찰/scratch 원경로와 활성로그·stage/commit행정수신은 로컬보관으로정리때사라질수있다. 압축은자동복원지시가아니다. 후속배정은phases/026/phase.json과각objective다. 제품전체완료나푸시는수행하지않았다.
''')
index=R/'기억/색인.md'; s=index.read_text(encoding='utf-8')
assert 'M-0575' not in s
write(index,s.replace('## layer-1\n','## layer-1\n\n- M-0575 [신뢰 문서의 실제 반환 검수를 마치고 남은 이름 판정을 병렬 배정함] -- P08/26제품 마감·추가 포장 관찰 한계,026 정책·참조·역할 이름의 고정판 독립 판정\n',1))
print('Prepared 026 three independent work tasks, common documents, pending manager and M-0575.')

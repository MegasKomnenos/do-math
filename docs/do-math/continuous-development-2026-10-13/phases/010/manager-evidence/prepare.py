"""Prepare the bounded work handoff, preserving old reports and product bytes."""
import difflib
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile

ROOT=Path('C:/math')
RUN=ROOT/'docs/do-math/continuous-development-2026-10-13'
OUT=Path(__file__).resolve().parent
NEXT=RUN/'phases/011'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='')
def write(p,s):p.write_text(s,encoding='utf-8',newline='')
V='run:phases/010/manager-evidence/verification.json'
R='run:phases/010/manager-evidence/review.md'
OBJ='run:phases/011/tasks/regression-reading/objective.md'
H='run:phases/010/tasks/host-smoke/'
L='run:phases/010/tasks/reading-limits/'
assert not (RUN/'phases/010/manager.json').exists()
for name in ('context.md','plan.md','seams.md'):
    before=OUT/(name+'.before')
    if not before.exists():before.write_bytes((RUN/name).read_bytes())

def amend(text,section,old,new):
    start=text.index('## '+section+' ')
    end=text.find('\n## ',start+1)
    if end<0:end=len(text)
    body=text[start:end]
    assert old in body,(section,old[:70])
    return text[:start]+body.replace(old,new,1)+text[end:]
def append(text,section,new):
    start=text.index('## '+section+' ')
    end=text.find('\n## ',start+1)
    if end<0:end=len(text)
    return text[:end].rstrip()+'\n\n'+new+'\n\n'+text[end:].lstrip('\n')

context=(OUT/'context.md.before').read_text(encoding='utf-8')
context=append(context,'C2','phase 010의 두 report는 manager 형식 검사를 통과했다. host-smoke는 A1/A2/A4 pass·A3 fail의 partial이며 reading-limits는 조사 A1~A3 complete다. 현재2644파일은 host 종료와 전건 일치하고 시작2640파일은009 종료와 같다. 허용14변경, 공식 실행의 선택/고유row/exit·전후소스와 정본/미러 각4묶음 OS 원자료를 대조했다. 최종 host 각3passed와 관련61건의59passed·1failed·1error를 구별한다. 시작 사본의 정확 두ID도 동일 실패다. 사본976파일 중975개 비캐시 파일만 시작 해시와 같고 비용 캐시1개는 현재 캐시 복사라는 manifest 예외를 적용한다. task의 “976파일 시작 동등” 표현은 이 범위로 정정한다. 읽기16페이지160행·꼬리80행을 남기는 중간 절단·합산 절단 기록과 고정 입력50개 및 CLI 바이너리2개를 대조했다. 조사 완료는13-C/L01 충족이 아니다. 근거는 run:phases/010/manager-evidence/verification.json·review.md와 두 원report이며 최종 G 완료가 아니다.')
start=context.index('phase 001~009는 종료됐고009의 문서4실패 해소를 검수했다.')
end=context.index('\n\ndo-math 시험 프로세스',start)
context=context[:start]+'phase 001~010의 세션은 종료됐다.010의 host 부분 성과와 읽기 조사 완료를 검수했으며 두 기존 회귀 문제와 읽기 문구 반례를011 regression-reading의 한정 work에 배정한다. 세 시험 파일·SKILL 읽기 문단·대응 미러·캐시를 한 task가 소유한다. 전건 smell/문서 검사는 상대 파일을 읽고 생성기는 정본 전체를 읽으므로 두 수리 task로 나누면 미완성 상태 의존이 생긴다. 이 phase는 단일 task가 jobs1·한 묶음씩 수행한다.010에서 성공한 OS 연쇄는 입력/경로 불변을 확인해 재사용한다. Lean·예약·학술의 실제 연쇄와 남은 문서/의미 질문은 현재 수리 결과 뒤 배정하며 공백을 조사용 빈 phase로 채우지 않는다.'+context[end:]
context=amend(context,'C8','010의 두 task도 gpt-6.1-sol/high로 배정한다.','010 두 task는 같은 모델로 수행됐고011 regression-reading도 gpt-6.1-sol/high다.010 host의partial과reading의조사complete를 각각 검수하며 제품 전체 합격과 구별한다.')
context=append(context,'C9','010에서 Job/pythonw의23cc4df3·c71053d6·46aaa333 도입 diff, 현재 소비자와 B117/B118의 존재하는6원보고를 확인했다. 초기 Job 보류/소유자 소실/자손 종료와 pythonw의 지급 console_python·정상/권한반려·형제 실행기 부재 명시 반려를 유지한다. 공유화한3개 boundary의21개 test method AST가 HEAD와 같고 새 T5는 실제 worker/Job·자손과pythonw 출력 연쇄를 추가했다. 이 PR02/PR11 지정 slice의 유지/공유화/추가 판단만 승인한다. 없는Temp 원보고의 counts와 다른 setup/저장/예약 성질은 새 성공에 합산하지 않는다. 근거는 run:phases/010/tasks/host-smoke/evidence/review.md·history-existing-reports.json 및 manager verification.json이다.')
old='L01은 실제 운전의 host/tool/version/read-call별 읽기·출력 한도와 그 측정 단위(byte 또는 token)가 미확정이다.'
start=context.index(old)
end=context.index('\n\n## C11',start)
context=context[:start]+'''L01/13-C의 읽기 한도 절은010 조사 뒤에도 미인증이다. 실제 개발 task의 Codex0.162.1 도구는 개별 명령과 합산에 별도의 token 예산을 적용한다. 비밀 없는 ASCII/Unicode 두80행fixture는400-token 출력에서 끝80행을 남기며 중간을 생략했고 명시10행씩16페이지는160행을 정확히 회수했다. 합산150-token 출력은 내부 두 결과가 온전해도 최종 수신을 잘랐다. 파일 해시·exit0·끝표지는 전문 수신의 증거가 아니며 수신은 독해/준수의 증명도 아니다. SKILL의 마지막 받은 부분 다음이라는 문구는 마지막 표시 꼬리로 읽힐 수 있어011 A3에 연속 접두/모든 공백/개별·합산 절단·긴 행의 부분 문자 처리를 명시하는 최소 수리를 배정한다. 문구 반례와 실제 운영자의 오류 발생을 구별한다.

설치 Claude2.1.289의 정적 Read는 기본25,000token, 전체 파일 입력262,144bytes와 세션 fileReadingLimits override를 구별한다. PARTIAL 접두/긴 행 일부·명시offset/limit 오류와 설명2,000행 대 실제limit 미지정을 확인했다. 이것은 실제 운전 세션의 효과값이나 Read 실행이 아니다. 최신allow_large 설명도 설치 판본에 소급하지 않는다. 입력 byte guard와 shell character 제한을 출력 byte 상한으로 바꾸지 않는다. 내부10역할의 문서·전체 prompt UTF-8/stdin 전달은 운전 도구 출력과 별개이며 기존 분석은 현재 코드/문서가 같은 성질만 재사용한다.

010 reading F4/Q1~Q2의 외부 결정은 남는다. 공급자별 실제 운영 host/CLI판본·model·Read 또는 shell·개별/합산 호출 설정을 특정하고, 원문의 UTF-8 출력 byte 기준을 유지할지 실제token/character와 전 구간 수신 기준으로 개정할지 결정해야 한다. manager는 기준 변경을 자의 승인하지 않았고 사용자에게 단위 선택을 상신했다. 답변 전에는 기존byte 요구와 미충족 판정을 유지한다. 현재 개발 host를 제품operator로 자동 지정하지 않으며 외부 결정과 독립적인011 수리를 계속한다. Claude 실제 Read 후속 검증은 해당 운전 프로필과 권한을 확정한 뒤 수행한다. B-20의 AI준수 한계는 유지한다. 구체적 선택지/잃는 보증은 run:phases/010/tasks/reading-limits/evidence/reading-boundaries.json·review.md, 검수는 run:phases/010/manager-evidence/verification.json·review.md다. 학술 외부 어휘는 별도 실제 응답 계약에서 확인한다. P02~P11/N01~N03의 다른 남김은 바꾸지 않았다.''' +context[end:]
start=context.index('010 host-smoke는 기존 실제 Job·pythonw boundary 경로를 확인해')
end=context.index('\n\n## C12',start)
context=context[:start]+'''010의 새 host T5는 실제 real_ports/ModelRunner/worker/Job·외부CLI 자손/collector와 pythonw→PowerShell→지급 제품 읽기를 실행해 정본3/미러3건이 모두passed였다. 외부 모델CLI만 결정적 로컬프로그램이며 유료 공급자 호출이나 실예약은0건이다. 커널PID/FILETIME·Job소유·정확exit7/stderr·명시취소/held handle 종료·빈Job·정상/반려JSON과exit0/1을 원자료에서 확인했다. 기존21개 boundary 단언도 유지됐다. 첫host 표본의turn.started 누락은 표본만 교정한 최종 통과로 해소했다.

관련61건 중59passed·1failed·1error는 아직 미해결이다. F1은 test_scheduling_call_jobs의 _job_run 필수clock/environment 누락과 실패dict를tuple로읽는KeyError로 실제취소를 실행하지 못한 시험이다. F2는 test_doc_code 한곳·test_knowledge_currentness 세곳의 unpinned_rejection이다.010 시작 사본에서 동일두ID의실패를 재현했으며 실제975비캐시파일만 시작과 같다.011 A1/A2/A4에 현재실포트 fixture·정확오류 단언·관련전건회귀를 배정하고runtime/규칙은 바꾸지 않는다. 새host 성공으로 이실패를 대체하지 않는다.010 A1/A2/A4는 보존하되A3는 실패 그대로다.

실제 OS예약등록/발화/해제, Lean/Mathlib, 학술MCP와 T4별도adapter분기는 후속책임이다.13-C/L01의조건은C10을 따른다. G4~G6/G8의최종전체관문은 아직 미수행이며 일부성공을 합산하지 않는다. 근거는 run:phases/010/manager-evidence/verification.json·review.md, 수리는 run:phases/011/tasks/regression-reading/objective.md다.''' +context[end:]
context=append(context,'C12','010 검수에서 runtime124·기존 공급자smoke입력3·양쪽corpus102경로가 시작과 같고102경로의Git raw/clean 동등성을 재확인했다. 기존 공급자 실호출의 승인된 성질과 역사실패는 유지한다. --check1307파일·skill-only verified와 실제판본을 대조했다.010의제품14변경(비용캐시2포함)은011 회귀수리·검수 뒤 마감하며 이번에는 제품을stage하지 않는다. 현재 제품원바이트와원OS/읽기근거는 manager-evidence/raw-evidence.zip 및 preservation.json에 결정화한다. 압축파일은자동복원지시가 아니다. 관리기록·선별원보고·011배정·기억만 커밋하며 원task report는 수정하지 않는다. 큰baseline사본과일부중복소스스냅샷의원경로는로컬보관이며 정리로 사라질 수 있다. 정확추적/보존범위는 run:phases/010/manager-evidence/preservation.json에 둔다.')
write(RUN/'context.md',context)

plan=(OUT/'plan.md.before').read_text(encoding='utf-8')
plan=plan.replace('## phase 001~009의 결과와 현재 상태','## phase 001~010의 결과와 현재 상태',1)
marker='최종 전체 관문은 아직 실행하지 않았다.'
plan=plan.replace(marker,'010의 host는 A1/A2/A4를 검수한 partial이며 관련61건의두기존회귀문제는011에배정했다. 읽기한도조사A1~A3는complete지만L01/13-C는미인증이며 문구반례를011에배정했다. '+marker,1)
start=plan.index('## 다음 phase: 010')
end=plan.index('## 가까운 후속 배정과 선행 관계',start)
plan=plan[:start]+'''## 다음 phase: 011

regression-reading 단일 work를 gpt-6.1-sol/high로 배정한다.010 host F1/F2의 실제취소fixture와 네정확음성단언, reading F2의 누락구간회수 문구를 수리한다. 세시험·SKILL문단·미러·비용캐시만 쓰며runtime/helper/검사규칙/원문요구는 바꾸지 않는다. 마지막에010의61개선택과해당문서/복구범위를 함께완결하고 미러관련검사·--check/skill-only를 확인한다. 이미 성공한host3/미러3은실행경로불변을확인해재사용한다.

수리를 둘로 나누면 전건smell/문서검사가 상대의미완성파일을 읽고 생성기/캐시도충돌하므로 한task로묶었다. 별도빈조사task를 병렬성을위해만들지 않는다. 정확한입력·쓰기·A·검사는 run:phases/011/phase.json 및 objective다.010의제품14변경은원바이트archive로보존하고011검수뒤같은변경단위로마감한다.

L01의Q1/Q2는외부결정으로남는다. 실제공급자별운전host/tool/판본/model/호출설정과출력byte기준유지또는도구단위개정을확정해야한다. 단위선택은사용자에게상신했고답변전에는원문byte기준과미충족을유지한다. 문구수리/시험수리는그답변과독립적이다.011A3의완료를읽기용량인증으로세지 않는다.

''' +plan[end:]
old='007 공급자 변경은 커밋됐고009의 정본110/미러89 전건 통과로008~009 문서·시험 변경28경로를 이번 관리 마감에 포함한다.009의 검수 근거는 manager-evidence/verification.json·review.md다.010에서 Job/pythonw와 L01을 독립 진행한다.'
new='007 공급자 변경과008~009 문서·시험28경로는009관리마감까지커밋됐다.010의host실경계와읽기조사를검수했으며011에서확인된두회귀문제와문구반례를수리한다.010제품은관련회귀완결뒤마감한다. 근거는010 manager-evidence/verification.json·review.md다.'
assert old in plan
plan=plan.replace(old,new,1)
old='| G7 Job/pythonw와 L01 |010 host-smoke가 실제 OS 작업자/출력/정리 연쇄를 T5에 연결하고 reading-limits가 현재 운전 읽기 계약의 한도·단위를 조사한다. | 두 task는 독립이다. 역할 stdin을 운전 출력 한도로 대체하지 않고 byte/token 근거 미상은 정확한 결정 질문으로 남긴다. |'
new='| G7 Job/pythonw 관련 회귀 |010 host정본3·미러3 성과를유지하고011A1/A2/A4에서call_jobs필수인자·네음성단언·관련전건회귀를완결한다. | 성공한OS성질과실패한기존검사를구별한다. 제품runtime은불변이다. |\n| G1/G3 읽기 문구와 L01 |011A3는연속접두/누락구간/개별·합산절단을명시한다. Q1/Q2의운전프로필·단위결정뒤실제읽기/한도검증을배정한다. | 현재조사complete는13-C인증이아니다. 원문byte기준은사용자답변전유지하며Claude실호출은미관측이다. |'
assert old in plan
plan=plan.replace(old,new,1).replace('|010 결과 뒤 실제 경계별 배정.', '|011 결과 뒤 실제 경계별 배정.',1)
write(RUN/'plan.md',plan)
seams=(OUT/'seams.md.before').read_text(encoding='utf-8')
seams+='\n010 host의기존runtime소비성과와reading조사를검수했다.011은현_job_run의필수clock/environment를기존fixture에전달하고지정음성단언·읽기문구만교정한다. 기존코드정본/실포트의입력·반환·오류의미는바꾸지않는다. 전건검사/미러/캐시소유를한task로모아제공자/소비자분리가없으며S항목·provides/uses는추가하지않는다. 읽기출력byte요구나운전host지정은이work의재량밖이다.\n'
write(RUN/'seams.md',seams)

(NEXT/'logs').mkdir(parents=True,exist_ok=True)
(NEXT/'tasks/regression-reading/evidence').mkdir(parents=True,exist_ok=True)
rels=['SKILL.md','scripts/tests/boundary/test_scheduling_call_jobs.py','scripts/tests/structure/test_doc_code.py','scripts/tests/sim/test_knowledge_currentness.py','scripts/tests/.timings.json']
inputs=['run:sources/user-decisions.md','run:sources/model-policy-2026-10-14.md','repo:.claude/skills/do-math/AGENTS.md',
    'repo:docs/do-math/시험-재편-2026-09-29/조사/결함-범주.md','repo:.claude/skills/do-math/scripts/tests/시험-지침.md',
    'repo:.claude/skills/do-math/scripts/이음새-정본.md','repo:.claude/skills/writing-skills/references/멀티런타임_동기화.md',
    H+'report.json',L+'report.json',H+'evidence/review.md',H+'evidence/related-results/report.json',H+'evidence/baseline-repro-02-results/report.json',
    H+'evidence/call-jobs-diagnosis.json',L+'evidence/reading-boundaries.json',L+'evidence/review.md',L+'evidence/fixture-verification.json',
    V,R,'run:phases/010/manager-evidence/source-inspected.json','run:phases/009/tasks/document-callable/report.json',
    'repo:.claude/skills/do-math/scripts/do_math/formal.py','repo:.claude/skills/do-math/scripts/do_math/parallel.py',
    'repo:.claude/skills/do-math/scripts/tests/support/doc_code.py','repo:.claude/skills/do-math/scripts/tests/support/smell_rules.py']
save(NEXT/'phase.json',{'kind':'work','purpose':'010에서 확인한 실제취소fixture·네음성단언과누락구간읽기문구를한정수리하고관련회귀/미러를완결한다. 공유검사와생성자원의충돌을피해단일task로소유한다.',
    'tasks':[{'id':'regression-reading','model':'gpt-6.1-sol','effort':'high','inputs':inputs,
    'writes':[tree+'/skills/do-math/'+p for tree in ('.claude','.agents') for p in rels],'provides':[],'uses':[]}]})

review='''# phase 010 manager 판단

host-smoke는partial, reading-limits는조사complete로검수했다. 두report의형식검사와원자료대조는report-checks.json·verification.json에있다. manager는제품코드/문서를수정하거나제품시험을재실행하지않았다.

현재2644파일이task종료와같고14변경은writes/report와정확히일치한다. 정본/미러host각3선택/3고유row/exit0, 관련61선택/59passed/1failed/1error/exit1, 첫host실패와후속수리, 시작사본의동일두실패를실제보고와process기록에서확인했다. 최종각867Python의전후/현재해시도맞는다. 기존3boundary21개test AST는HEAD와동일하다. 실제8개smoke.json에서PID/FILETIME·Job/자손소유·원stderr/반환·held handle종료·빈Job,pythonw JSON/exit0/1·PowerShell원관측을대조했다. 실제제품연쇄이되외부모델CLI는로컬대역이다. 공급자호출/OS예약/다른G7의성공이아니다.

F1은현재_job_run서명과취소시험call site에필수clock/environment가없는문제로확인했다. 인접publication실패시험은현재인자를전달한다. ModelCalls의실패dict에[-1]을적용한KeyError가실제Job실행실패를가린다. F2는전건smell원보고의네unpinned_rejection과현재AssertionError-only단언에대응한다. 008~009의관련선택에는이전건smell검사가없었으므로이전지정통과와상충하지않는다. 011은정확시험/반려원인을수리하고runtime·helper·규칙을변경하지않는다.

baseline-manifest의976파일중tests/.timings.json은현재비용캐시복사이며시작해시와다르다. 나머지975파일과시작해시는같다. 원report의976시작동등표현은이예외를붙여한정승인하고원보고는고치지않았다. manager첫검산은이캐시까지시작과같다고단언해멈췄고manifest의명시예외를적용한뒤통과했다. 초반키조회스크립트의list를dict로다룬AttributeError도읽기보조오류이며제품변경은없다.

읽기조사의16페이지는fixture의160행/순서/문자와같다.400-token결과는중간을생략하면서80행끝표지를남기고합산절단기록도별개다. 현SKILL문구/원문13-C/B-20과대조해문구반례를승인했다. 고정입력50개와설치바이너리2개해시,Claude정적Read의override/기본/선택호출코드snippet을실제binary근방에서대조했다.25,000token/262,144입력bytes는출력byte상한이아니다. 최신웹설명의allow_large는task가관측한당시판본차이기록으로만보존한다. manager가새웹검색이나Claude실제Read를수행했다고주장하지않는다.

F1/F3의관측은현재host/정적설치판본한정사실로종결하며F2문구는011A3에carry한다. F4는사용자에게단위선택을상신하고실제운전프로필/한도미인증을C10/plan에carry한다. 답변이없어원문byte기준을유지하며권한을추정해G를축소하지않는다. 011의세시험과문구수리는독립적으로가능하다. 전건문서/smell은상대파일을읽고미러/캐시도공유하므로두수리task로병렬화하지않는다.

runtime124·공급자입력3·corpus102경로불변과Git raw/clean을대조해F3의한정재사용을승인한다.010의제품은회귀수리뒤마감하고이번커밋은관리/선별원근거/원바이트archive/011/기억만담는다. G4~G8의전체완료는선언하지않는다. 공용문서diff는common-docs.diff다. G1~G8와C3/C4/C6/C7은바꾸지않고C2/C5/C8~C12의현재상태·선행관계만갱신했다. 기존조건/역사실패/모든미결범위를보존했고새S는없다.
'''
write(OUT/'review.md',review)
diff=''
for name in ('context.md','plan.md','seams.md'):
    old=(OUT/(name+'.before')).read_text(encoding='utf-8')
    new=(RUN/name).read_text(encoding='utf-8')
    diff+=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=name+'.before',tofile=name))
write(OUT/'common-docs.diff',diff)

dispositions=[]
def disposition(item,action,dest,reason,evidence):
    dispositions.append({'item':'010/'+item,'action':action,'destination':dest,'reason':reason,'evidence':evidence})
disposition('host-smoke/F1','carry',[OBJ+'#A1',OBJ+'#A4','run:context.md#C11'],'실제Job취소를실행하지못하는구fixture다. 현clock/environment전달과반환검사로수리하고정확ID/관련전건을확인한다.',[V,R,H+'evidence/call-jobs-diagnosis.json'])
disposition('host-smoke/F2','carry',[OBJ+'#A2',OBJ+'#A4','run:context.md#C11'],'원실패와현재네포괄음성단언이맞는다. 규칙/모집단을약화하지않고의도한반려원인에고정한다.',[V,R,H+'evidence/related-results/report.json'])
disposition('host-smoke/F3','resolve',['run:context.md#C11','run:context.md#C12'],'실제OS성질과runtime124/입력3/corpus102불변·raw/clean을확인해한정승인한다. 다른G7/전체관문완료가아니다.',[V,R])
disposition('reading-limits/F1','resolve',['run:context.md#C10'],'현재task의개별/합산token경계와160행회수만승인한다. 보편byte상한/제품operator/독해보증으로확대하지않는다.',[V,L+'evidence/fixture-verification.json',L+'evidence/fixture-aggregate-results.json'])
disposition('reading-limits/F2','carry',[OBJ+'#A3','run:context.md#C10'],'80행꼬리에서81행으로이어가면중간공백을놓친다. 연속접두와전구간/두출력계층을명시하는최소문구수리를배정한다.',[R,L+'evidence/fixture-capped-results.json','repo:.claude/skills/do-math/SKILL.md'])
disposition('reading-limits/F3','resolve',['run:context.md#C10'],'설치정적계약과바이너리판본만승인한다. 입력byteguard/기본token/override/최신문서차이를보존하고실제Claude호출미검증은F4후속에유지한다.',[V,L+'evidence/claude-read-binding.json',L+'evidence/reading-boundaries.json'])
disposition('reading-limits/F4','carry',['run:context.md#C10','run:plan.md'],'출력단위선택은사용자에게상신했다. 미지정실운전프로필과byte상한은유지된미충족조건이며답변전원문요구를개정하지않는다. 독립011수리는계속한다.',[L+'evidence/reading-boundaries.json',R,'run:sources/user-decisions.md'])
updates=[]
for c,reason in {
'C2':'010검수상태/현재해시/실행과조사의차이·캐시예외를추가하고역사판정을보존한다.',
'C5':'종료된010병렬배정을011단일수리소유로교체한다. 전건검사/미러/캐시의실제독립성제약과jobs1을명시한다.',
'C8':'010결과와011배정에도사용자지정gpt-6.1-sol/high를적용한다. manager정책은유지한다.',
'C9':'Job/pythonw지정도입diff/현재소비자/존재원보고의한정검토를추가한다. 다른PR과없는counts는닫지않는다.',
'C10':'L01조사예정을관측/정적계약/문구반례/외부단위결정으로갱신한다. byte요구·B-20한계·다른문서남김을보존한다.',
'C11':'010실연쇄성과와기존회귀실패를구분하고011A1/A2/A4에연결한다. 다른G7와최종관문을유지한다.',
'C12':'기존공급자/원바이트재사용과010제품커밋대기·archive/로컬근거의추적경계를추가한다.'}.items():
    updates.append({'item':c,'action':'amend','destination':['run:context.md#'+c],'reason':reason,'evidence':[V,R,'run:phases/010/manager-evidence/common-docs.diff']})
manager={'next':'011','decision':'010의host-smoke는A1/A2/A4성과를승인하고A3미충족의partial을유지한다. reading-limits는조사A1~A3complete이며L01/13-C는미인증이다. 현재2644소스/14변경·최종host정본3/미러3·관련61의59pass/1fail/1error와읽기160행/절단반례를원자료로확인했다. baseline976중975비캐시파일만시작동등이라는예외를명시하고원보고는보존했다.\n\n새host성공은기존취소/네음성단언문제를대체하지않는다.011에세시험·읽기문단의좁은수리와관련전건/미러검증을배정한다. 전건검사와생성기/캐시가상대미완성파일을소비하므로한task로묶었다. 전체관문이나새유료호출을현재부분회귀와섞지않는다.\n\n읽기단위개정은사용자상신후답변전기존byte기준/미충족을유지한다. 현재taskhost를제품operator로자동지정하지않는다. 독립수리는진행하며G1~G8은축소하지않았다.010제품은011검수뒤커밋하고이번에는관리/선별원근거/raw archive/011/기억만마감한다. review phase가아니고전체G도미충족이므로next:null을제출하지않는다.',
'reports':[{'task':'host-smoke','state':'read','detail':'report형식PASS. A1/A2/A4성과·A3실패의partial을검수했다. 캐시1개예외를제외한975시작동등으로한정하며011A1/A2/A4에복구배정한다.','evidence':[H+'report.json',V,R,OBJ]},
{'task':'reading-limits','state':'read','detail':'report형식PASS. 조사A1~A3complete이며13-C/L01충족은아니다. 문구반례는011A3,운전/단위결정은C10/plan으로인계한다.','evidence':[L+'report.json',V,R]}],
'dispositions':dispositions,'context_updates':updates,'plan_update':'010의실제성과와미충족을반영해011regression-reading을배정했다. 전건회귀/읽기문구의선행관계와공유검사/미러제약으로단일task를선택했다. 기존G4→G5→G6및나머지G7/최종review,미결문서/의미질문은유지한다. 외부Q1/Q2는상신/미인증이며현재수리와독립적이다.010제품커밋은011검수뒤로두고원바이트를보존한다.',
'seam_updates':[],'completion':None}
save(RUN/'phases/010/manager.pending.json',manager)

# Preserve exact original bytes in a compact archive; do not include 106 MiB baseline copies.
archived={}
for task in ('host-smoke','reading-limits'):
    for p in (RUN/'phases/010/tasks'/task).rglob('*'):
        if p.is_file() and not any(part in ('baseline-tree','baseline-tree-02','__pycache__') for part in p.parts):
            archived[p.relative_to(ROOT).as_posix()]=sha(p)
for p in read(OUT/'verification.json')['changes']:archived[p]=sha(ROOT/p)
archive=OUT/'raw-evidence.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
    for p in sorted(archived):z.write(ROOT/p,p)
with zipfile.ZipFile(archive) as z:
    assert all(hashlib.sha256(z.read(p)).hexdigest()==h for p,h in archived.items())
save(OUT/'preservation.json',{'archive':archive.relative_to(ROOT).as_posix(),'archive_sha256':sha(archive),'entries':archived,
    'products_pending_regression':read(OUT/'verification.json')['changes'],
    'local_only':'Full task directories remain local. baseline-tree and baseline-tree-02 are excluded from archive; baseline-manifest hashes, historical HEAD and raw reports remain. Some duplicated source snapshots are archived rather than individually tracked. Administrative stage/commit receipts remain local. No restoration or deletion is authorized by this archive.',
    'product_commit':'Defer 010 product paths until 011 regression completion. This commit includes only management, selected task originals, archive, 011 assignment and one memory node.'})
print(json.dumps({'next':'011','archive_files':len(archived),'archive_bytes':archive.stat().st_size,'manager':'pending','changes':'C2/C5/C8-C12, plan, seams explanatory text; no S changes'},ensure_ascii=False))

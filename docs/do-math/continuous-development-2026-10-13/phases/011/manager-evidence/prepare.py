from pathlib import Path
from difflib import unified_diff
import json
import re

REPO=Path('C:/math')
RUN=REPO/'docs/do-math/continuous-development-2026-10-13'
OUT=Path(__file__).resolve().parent
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
before={name:(RUN/name).read_text(encoding='utf-8-sig') for name in ('context.md','plan.md','seams.md')}
context=before['context.md']
summary='phase 011 regression-reading은 A1~A4 complete로 검수했다. report 검사 후 현재2644파일과 종료 해시 전건 일치, 시작과010 manager 판본 동일, 허용10변경(정본4·미러4·비용캐시2)을 확인했다. focused6·최종 정본136/미러136의 선택·고유row·passed·exit0와 각867 Python 및 실행 전후소스를 대조했다.010의 정확 error/failed 두ID는 새 passed에 대응하며 runtime/helper/규칙은 불변이다. 읽기 문구는14행 한 문단만 교정됐고 원fixture16페이지160행과 중간/합산 절단을 대조했다. runtime124·입력3·corpus102경로와 host8원자료의 한정 재사용, Git raw/clean 및 --check1307파일을 확인했다. manager 첫 diff 검산의 exit1은 파일 순서를 달리 이어붙인 관리 스크립트 문제였으며 순서만 고쳐 통과했다. 근거는 run:phases/011/manager-evidence/verification.json·review.md다. 전체 G나 L01 인증은 아니다.'
context=context.replace('## C3 현재 정본과 이력의 역할',summary+'\n\n## C3 현재 정본과 이력의 역할',1)
c5=context.index('## C5 '); c6=context.index('## C6 ')
old=context[c5:c6].split('\n\n')[1]
new='phase 001~011의 세션은 종료됐고011의 지정 회귀/문구 수리를 검수했다.012 lean-smoke는 기존 Lean/Mathlib 실연쇄·T5 최소 시험·실제 녹화/재생·미러를 한 task로 맡는다. corpus manifest·시험 전건 구조 검사·생성기와 비용 캐시를 공유하므로 다른 제품 수정/시험 task를 병행하지 않는다. jobs1·한 묶음씩 실행하고 기존 host/공급자는 불변 경로의 승인 성질을 재사용한다. 예약·학술·나머지 문서/의미 질문은 별도 후속 책임이다. 단일 외부 경계를 끝내는 작업으로 범위를 제한하며 독립성을 만들지 못한 빈 분석 task는 추가하지 않는다.'
context=context[:c5]+context[c5:c6].replace(old,new,1)+context[c6:]
context=context.replace('010 host의partial과reading의조사complete를 각각 검수하며 제품 전체 합격과 구별한다.', '010 host의partial과reading의조사complete를 각각 검수하며 제품 전체 합격과 구별한다.011의 A1~A4 complete를 검수했고012 lean-smoke도 gpt-6.1-sol/high로 배정한다.',1)
context=context.replace('SKILL의 마지막 받은 부분 다음이라는 문구는 마지막 표시 꼬리로 읽힐 수 있어011 A3에 연속 접두/모든 공백/개별·합산 절단·긴 행의 부분 문자 처리를 명시하는 최소 수리를 배정한다. 문구 반례와 실제 운영자의 오류 발생을 구별한다.', 'SKILL의 마지막 받은 부분 다음이라는 문구는 마지막 표시 꼬리로 읽힐 수 있었고011 A3에서14행 문단을 수리했다. 온전한 연속 접두 또는 명시 구간별 수신으로 모든 공백을 회수하고 개별·합산 절단 및 긴 행의 부분 문자를 구별한다. 기존 필수 순서·판본 재사용·내부 역할 경계는 유지됐다. 원fixture의 ASCII18~63/Unicode16~65 및 합산 누락에 새 절차를 대조해010 reading F2의 한정 문구 문제를 종결한다. 근거는 run:phases/011/tasks/regression-reading/evidence/changes.diff·reading-verification.json 및 manager 검수다. 문구 반례와 실제 운영자의 오류 발생을 구별하며 L01 인증은 아니다.',1)
context=context.replace('현재 개발 host를 제품operator로 자동 지정하지 않으며 외부 결정과 독립적인011 수리를 계속한다.', '현재 개발 host를 제품operator로 자동 지정하지 않는다. 외부 결정과 독립적인011 문구 수리는 완료했고012 Lean work를 계속한다.',1)
old='관련61건 중59passed·1failed·1error는 아직 미해결이다. F1은 test_scheduling_call_jobs의 _job_run 필수clock/environment 누락과 실패dict를tuple로읽는KeyError로 실제취소를 실행하지 못한 시험이다. F2는 test_doc_code 한곳·test_knowledge_currentness 세곳의 unpinned_rejection이다.010 시작 사본에서 동일두ID의실패를 재현했으며 실제975비캐시파일만 시작과 같다.011 A1/A2/A4에 현재실포트 fixture·정확오류 단언·관련전건회귀를 배정하고runtime/규칙은 바꾸지 않는다. 새host 성공으로 이실패를 대체하지 않는다.010 A1/A2/A4는 보존하되A3는 실패 그대로다.'
new='010 관련61건의59passed·1failed·1error는 역사 실패로 보존한다. F1은 _job_run의 필수clock/environment 누락으로 실제취소를 못 하고 실패dict의 tuple 인덱싱이 KeyError를 낸 시험이었다. F2는 test_doc_code 한곳·test_knowledge_currentness 세곳의 unpinned_rejection이었다.010 시작 사본의 동일두ID 재현은975비캐시파일 동등의 한계를 유지한다.011은 실제 real_ports 인자를 전달하고 owner thread 시작/판단·정확 stop tuple·한 번 수집/continuation·빈Job·추가collect0을 보강했다. 네 음성 단언은 원인별 owner/method·local_path·봉인 좌표 반려에 연결됐다. runtime/helper/규칙을 바꾸지 않고010 전체61개와 문서/복구75개를 합친 양쪽136건이 모두passed·exit0이어서010 F1/F2의 남김을 종결한다.010 A3 원보고는 fail 그대로이며 새 해소 근거는 run:phases/011/manager-evidence/verification.json·review.md다.'
assert old in context; context=context.replace(old,new,1)
context=context.replace('실제 OS예약등록/발화/해제, Lean/Mathlib, 학술MCP와 T4별도adapter분기는 후속책임이다.', '실제 OS예약등록/발화/해제, 학술MCP와 T4별도adapter분기는 후속책임이다. Lean/Mathlib는012 lean-smoke의 기존 실설치 대표 컴파일·실제 verifier 정상/오류·녹화/재생으로 배정한다. --version이나Python compiler 대역으로 성공을 대신하지 않으며 runtime/설치 변경이 필요하면 후속으로 반환한다.',1)
context=context.replace('수리는 run:phases/011/tasks/regression-reading/objective.md다.', '새 해소는011 report, 다음 실경계 책임은 run:phases/012/tasks/lean-smoke/objective.md다.',1)
context+='\n011 F3의 불변 근거를 검수해010 host의 정본3·미러3 성질과 기존 공급자 실호출을 한정 재사용한다. host8원자료의 SHA/판정, Python/pythonw SHA·판본과 PowerShell 당시 경로/판본의 한계를 유지하며 새 OS T5/유료호출은 없다. 현재 corpus102경로의 Git raw/clean을 재확인했고 manifest/녹화·속성·생성규칙은 불변이다.010~011의 검수된 제품·시험·문서·미러20경로를 같은 관리 커밋으로 마감하고 비용캐시2개는 제외한다. 원task report/evidence는 수정하지 않는다.011 원자료 전부와 현재 제품 원바이트는 raw-evidence.zip으로도 보존한다. 추적하는 선별 원경로와 압축 항목·SHA는 run:phases/011/manager-evidence/preservation.json에, 커밋 행정 수신은 로컬 commit.json에 둔다. 원경로 중 압축으로만 추적되는 scratch/중복 snapshot 및 행정 수신은 로컬 정리로 사라질 수 있다.012의 새 Lean 자료는 기존 공급자/host 성과를 재인증하는 작업이 아니며 G4~G6/G8과 나머지G7 책임을 유지한다.\n'
(RUN/'context.md').write_text(context,encoding='utf-8')

plan=before['plan.md'].replace('## phase 001~010의 결과와 현재 상태','## phase 001~011의 결과와 현재 상태',1)
plan=plan.replace('010의 host는 A1/A2/A4를 검수한 partial이며 관련61건의두기존회귀문제는011에배정했다. 읽기한도조사A1~A3는complete지만L01/13-C는미인증이며 문구반례를011에배정했다.', '010의 host는 A1/A2/A4를 검수한 partial이며 관련61건의 두 회귀 문제는011의 새 양쪽136건 전부 통과로 해소했다.011 A1~A4를 검수했고 읽기 문구 반례도 종결했다. 읽기한도조사 완료/문구 수리와 L01/13-C 인증은 구별하며 실제 운전 프로필·출력 단위 결정은 남는다.',1)
start=plan.index('## 다음 phase: 011'); end=plan.index('## 가까운 후속 배정',start)
plan=plan[:start]+'''## 다음 phase: 012

lean-smoke 단일 work를 gpt-6.1-sol/high로 배정한다. 현재 설치의 실제 정체와 `setup_lean.verify_environment`의 Mathlib 대표 컴파일, `formal.verify_lean`의 정상/오류를 T5 최소 선택에 연결한다. 실제 원출력·소스·판정의 새 Lean 녹화와 현재 parser 재생, 관련 회귀·지침·대응 미러를 완결한다. runtime/설치/신뢰 기록을 바꾸거나 다운로드하지 않는다. 그 경계의 결함/조건이 드러나면 원자료와 후속 범위를 반환한다.

corpus manifest·전건 구조 검사·공식 생성기·비용 캐시가 공유돼 한 task가 jobs1로 순차 소유한다. 다른 경계의 제품 task를 동시에 두면 상대의 미완성 상태를 읽게 되므로 다음 phase로 분리한다. 새 seam은 없으며 정확 입력·writes·A·검사는 run:phases/012/phase.json 및 objective다.010~011 제품20경로는 관련 회귀/미러 검수 뒤 현재 관리 마감에 포함한다.

L01의 Q1/Q2는 외부 결정으로 남는다. 실제 공급자별 운전 host/tool/판본/model/호출 설정과 출력 byte 기준 유지 또는 도구 단위 개정을 확정해야 한다. 이미 상신한 단위 선택의 답변이 없으므로 원문 byte 기준과 미충족을 유지한다.011의 문구 수리 완료는 읽기 용량 인증이 아니며012 Lean 작업은 이 답변과 독립적이다.

'''+plan[end:]
plan=plan.replace('010의host실경계와읽기조사를검수했으며011에서확인된두회귀문제와문구반례를수리한다.010제품은관련회귀완결뒤마감한다. 근거는010 manager-evidence/verification.json·review.md다.', '010의 host/읽기 조사를 검수했고011에서 두 회귀 문제와 문구 반례를 수리·검수했다.010~011 제품 단위를 마감하며012에서 Lean/Mathlib 실연쇄를 연결한다. 근거는011 manager-evidence/verification.json·review.md다.',1)
plan=plan.replace('| G7 Job/pythonw 관련 회귀 |010 host정본3·미러3 성과를유지하고011A1/A2/A4에서call_jobs필수인자·네음성단언·관련전건회귀를완결한다. | 성공한OS성질과실패한기존검사를구별한다. 제품runtime은불변이다. |','| G7 Job/pythonw 관련 회귀 |010 host정본3·미러3을 한정 재사용하고011의 실제 취소·네 음성 단언 및 양쪽136건 통과로 관련 남김을 닫았다. |010 실패 원보고는 보존한다. 이후 입력/경로 변경 시 재사용을 재판정한다. |',1)
plan=plan.replace('| G1/G3 읽기 문구와 L01 |011A3는연속접두/누락구간/개별·합산절단을명시한다. Q1/Q2의운전프로필·단위결정뒤실제읽기/한도검증을배정한다.', '| G1/G3 읽기 문구와 L01 |011A3의 연속 접두/누락 구간/개별·합산 절단 문구 수리는 종료됐다. Q1/Q2의 운전 프로필·단위 결정 뒤 실제 읽기/한도 검증을 배정한다.',1)
plan=plan.replace('| G7 Lean/예약/학술 | 실제 Lean/Mathlib, 시험 전용 예약 등록·발화·해제, 학술 list_sources를 기존 실제 경로로 각각 검증한다. |011 결과 뒤 실제 경계별 배정. Job/pythonw 성공이나 예약 cmdlet 대역의 결과로 대체하지 않는다. |','| G7 Lean/예약/학술 |012에서 실제 Lean/Mathlib 컴파일·verifier·녹화/재생을 맡는다. 시험 전용 예약 등록·발화·해제와 학술 list_sources는 각각 후속 실제 경계로 배정한다. | 공유 manifest/캐시·생성기 의존을 순차화한다. Job/pythonw 성공·예약 cmdlet 대역·도구 판본만으로 대신하지 않는다. |',1)
(RUN/'plan.md').write_text(plan,encoding='utf-8')
seams=before['seams.md']+'\n011의 기존 포트 fixture·정확 음성 단언·읽기 문구 수리를 검수했다.012는 현재 setup_lean.verify_environment/inspect_toolchain/verify_lean과 real_ports를 소비하는 Lean/Mathlib 최소 실연쇄다. 입력/반환/실패의 정본은 기존 함수·lean_evidence·trust_inventory이며 별도 형식 복제나 제품 계약 개정은 없다. 새 smoke/helper·녹화/재생과 미러를 한 task가 소유해 provides/uses는 빈 목록이고 S 항목은 추가하지 않는다. 설치/신뢰 상태 변경이나 runtime 수리가 필요하면 반례를 다음 배정으로 반환한다.\n'
(RUN/'seams.md').write_text(seams,encoding='utf-8')
diffs=[]
for name,old in before.items():
    diffs.extend(unified_diff(old.splitlines(keepends=True),(RUN/name).read_text(encoding='utf-8').splitlines(keepends=True),fromfile='before/'+name,tofile='after/'+name))
(OUT/'common-docs.diff').write_text(''.join(diffs),encoding='utf-8')

inputs=['run:sources/user-decisions.md','run:sources/model-policy-2026-10-14.md','repo:.claude/skills/do-math/AGENTS.md','repo:.claude/skills/do-math/scripts/tests/시험-지침.md','repo:.claude/skills/do-math/scripts/이음새-정본.md','repo:.claude/skills/writing-skills/references/멀티런타임_동기화.md','repo:docs/do-math/시험-재편-2026-09-29/설계.md','repo:docs/do-math/시험-재편-2026-09-29/조사/결함-범주.md','run:phases/001/tasks/gate-readiness/evidence/gate-readiness.json','run:phases/001/tasks/gate-readiness/evidence/environment.json','run:phases/001/tasks/closure-map/evidence/prior-review-state.json','repo:docs/do-math/시험-재편-2026-09-29/단계-전환표-2026-10-03.json','run:phases/011/tasks/regression-reading/report.json','run:phases/011/manager-evidence/verification.json','run:phases/011/manager-evidence/review.md','run:phases/011/manager-evidence/source-inspected.json']
inputs += ['repo:.claude/skills/do-math/scripts/'+p for p in ['setup_lean.py','do_math/formal.py','do_math/lean_evidence.py','do_math/trust_inventory.py','do_math/wiring.py','tests/boundary/test_setup_lean_compile.py','tests/boundary/test_knowledge_lean_verifier.py','tests/support/provider_inputs.py','tests/structure/test_corpus.py','tests/unit/test_corpus_replay.py','tests/contracts/test_doubles_follow_corpus.py','tests/corpus/manifest.json']]
paths=['scripts/tests/smoke/test_lean_live.py','scripts/tests/support/lean_live.py','scripts/tests/corpus/lean/','scripts/tests/corpus/manifest.json','scripts/tests/unit/test_corpus_replay.py','scripts/tests/시험-지침.md','scripts/tests/.timings.json']
writes=[tree+'/skills/do-math/'+p for tree in ('.claude','.agents') for p in paths]
phase={'kind':'work','purpose':'011의 관련 회귀 종료 뒤 현재 설치된 Lean/Mathlib 실연쇄를 T5와 실제 녹화·재생에 연결한다. 공유 corpus/생성기/캐시를 단일 task가 소유한다.','tasks':[{'id':'lean-smoke','model':'gpt-6.1-sol','effort':'high','inputs':inputs,'writes':writes,'provides':[],'uses':[]}]}
save(RUN/'phases/012/phase.json',phase)
(RUN/'phases/012/tasks/lean-smoke/evidence').mkdir(parents=True,exist_ok=True)
(RUN/'phases/012/logs').mkdir(exist_ok=True)

review='''# phase 011 관리 검수

regression-reading의 A1~A4 complete를 승인한다. report 형식 검사 후 현재2644파일/종료 해시와 파일 집합,010 manager/시작 해시의 동등성, 정확 허용10변경을 확인했다. focused6·정본136·미러136의 선택/고유row/전건passed/실제exit0 및 각867 Python 해시·전후 소스를 원자료에서 검산했다.010의61개와009의 관련75개가 현재136개에 빠짐없이 포함된다. task report나 과거 실패는 수정하지 않았다.

취소 fixture는 현 formal._job_run의 필수 실포트 인자를 전달한다. 실제 owner thread callback/판단, 명시 취소의 정확 tuple, 단일 collect/continuation, 빈Job와 추가collect0을 유지/보강했다. 원래 dict를 tuple로 인덱싱한 오류는 먼저 형식을 검사해 가려지지 않는다.010의 정확 error/failed 두ID가 새 row에서 passed다.

네 음성 단언의 기대는 owner/method 집합과 실제 source 소유 계약에서 나온다. 일반 continuation의 모든 봉인 좌표는 정상 source와 같고 local_path만 resume-history이므로 helper의 operational-review 접두 검사에서 반려된다. 정확 exception.args는 이 정상/교란 대조와 함께 읽어야 한다. checkpoint 교란은 다른 artifact_ref의 완전한 좌표 차이에 결속된다. helper/runtime/규칙/스캔 모집단은 불변이다.

SKILL 변경은14행 한 문단뿐이고 필수 문서 순서·판본 재사용·내부 역할은 보존됐다.010 원fixture16페이지160행, ASCII18~63/Unicode16~65의 실제 중간 누락과 합산 절단을 다시 대조했다. 온전한 접두 또는 명시 범위로 모든 공백을 회수하는 절차는 이 반례를 처리한다. L01/13-C 원문 output-byte 요구와 Q1/Q2 미정, AI 준수의 한계는 유지한다. 이번 조사/문구 수리가 용량 인증을 대신하지 않는다.

runtime124·공급자 입력3·corpus102경로와 host helper/시험/8원자료는 불변이다. 원자료 SHA/판정과 현재 Python/pythonw·PowerShell 실행 파일 SHA를 task 종료 조건에 대조했다. PowerShell의010 당시 SHA 부재는 경로/판본 기반 재사용의 한계로 유지한다. 새로운 OS T5·유료 모델 호출은 없다. 기존 승인 범위만 재사용하며 Git raw/clean102경로와 현재 공식 mirror --check1307파일을 재확인했다.

첫 manager 검산은 diff의 파일 순서를 task와 다르게 이어붙여 마지막 문자열 비교에서 exit1이 났다. 실제 내용/소스 문제는 없었고 task의 순서를 쓰도록 관리 스크립트만 교정한 뒤 전건 통과했다. 이 보조 검산 오류를 제품 실패나 task 수리로 세지 않는다.

012는 단일 Lean/Mathlib 실연쇄를 배정한다. 실제 대표 컴파일·verifier 정상/오류·원녹화/재생을 새 T5 선택에 연결하며 기존 제품/설치/신뢰 상태는 고치지 않는다. corpus manifest·전건 구조 검사·생성기/캐시를 공유하므로 다른 제품 task와 병행하지 않는다. 예약·학술·T4 adapter 보고·나머지 문서/의미 질문·G4~G6/G8은 유지한다. 최종 review 전이므로 개발 완료를 선언하지 않는다.

공용 변경은 common-docs.diff에 보존했다. C2에 검수 사실, C5에 자원 소유, C8에012 모델, C10에 문구 종결과 외부결정 유지, C11에 정확 두 회귀 종결/Lean 배정, C12에 재사용과20제품경로 마감을 반영했다. C/G/S 의미·완료 기준은 줄이지 않았다. seams에는 기존 API 소비/단일 소유 설명만 추가했고 새 S나 개정은 없다. 원자료 보존/정확 커밋 대상은 preservation.json, 커밋 행정 수신은 로컬 commit.json을 따른다.
'''
(OUT/'review.md').write_text(review,encoding='utf-8')
ev=['run:phases/011/manager-evidence/verification.json','run:phases/011/manager-evidence/review.md']
taskref='run:phases/011/tasks/regression-reading/report.json'
ctxchanges={
'C2':'011 A1~A4 검수와 현재/실행 소스·정확 이전 실패의 새 해소를 추가. 역사 partial과 전체 G 한계 보존.',
'C5':'011 종료 후012 단일 Lean work의 공유 manifest/검사/생성기/캐시 소유와 jobs1 순서를 지정. 다른 경계는 후속으로 분리.',
'C8':'011 complete 검수와012 gpt-6.1-sol/high를 추가. 기존 manager 설정과 모델 전환의 역사 조건 보존.',
'C10':'010 reading F2 문구 반례를011 원자료로 종결. 원문 byte 요구·Q1/Q2 미정·L01 미인증은 유지.',
'C11':'010 F1/F2를011 양쪽136건의 정확 passed ID로 해소.010 원fail 보존, Lean 실연쇄를012에 배정.',
'C12':'011 불변/원바이트/host 재사용을 추가하고010~011 제품20경로 마감을 지정. 캐시 제외·과거 원자료·다른 G 남김 유지.'}
manager={
'next':'012',
'decision':'011 regression-reading은 A1~A4 complete이며 검수 후 승인한다. 현재2644파일/종료 소스 및 시작/010판본, 허용10변경, focused6·정본/미러 각136 전건passed·exit0와 각각867 Python 해시를 원파일에서 대조했다.010의 정확 취소error/smellfailed는 새 동일ID의 통과로 해소됐다. 실제 포트/검사 규칙을 약화하지 않았고 네 반려 단언 및 읽기 문구는 지정 계약을 보존한다. 읽기 원자료의16페이지/중간·합산 절단을 대조했으나 L01/13-C의 운전프로필·출력단위 미정은 계속 남는다.\n\n011 F1/F2/F3의 지정 사실은 resolve하며 이전010의 관련 남김만 닫는다. runtime124·입력3·corpus102 및 host8원자료 불변에 따른 기존 승인 성질 재사용을 유지한다. PowerShell 역사 SHA 부재는 남겨 두며 새 실호출/전체 관문으로 확대하지 않는다. manager 첫 diff 비교 실패는 순서 불일치였고 관리 스크립트만 수정해 통과했다.\n\n다음012는 기존 Lean/Mathlib 설치를 실제 대표 컴파일·verifier·T5/녹화/재생에 연결하는 한정 work다. 공유 manifest/구조 검사/미러 생성/캐시 때문에 하나의 task로 순차 소유하며 다른 미완성 제품에 의존하지 않는다. 외부결정이 필요한 읽기 인증과 독립적이다. 예약/학술/T4보고 및 나머지 문서/의미 질문, G4~G6/G8이 남고 직전도 work이므로 종료 조건을 충족하지 않는다.010~011의 검수된20제품경로와 관리/기억을 정확 stage해 마감한다. 제품 코드는 manager가 수정하지 않았다.',
'reports':[{'task':'regression-reading','state':'read','detail':'report 전문과 A1~A4·10변경·3finding·10check를 읽고 형식 검사 및 현재 소스/실행 row/원자료를 대조했다. 지정 complete 승인.','evidence':[taskref,*ev,'run:phases/011/manager-evidence/report-check.stdout.log']}],
'dispositions':[
{'item':'011/regression-reading/F1','action':'resolve','destination':['run:context.md#C11','run:plan.md'],'reason':'010의 실제취소error와 전건smellfailed 두ID가 새 정본/미러136건에 포함돼 passed다. 실포트 fixture·네 원인 단언의 수리와 runtime/helper/규칙 불변을 대조했다. 역사010 A3 fail은 보존하고 그 남김만 닫는다.','evidence':ev+['run:phases/011/tasks/regression-reading/evidence/changes.diff']},
{'item':'011/regression-reading/F2','action':'resolve','destination':['run:context.md#C10','run:plan.md'],'reason':'14행 한 문단의 온전한 접두/명시구간·모든공백·개별/합산 절단 처리를 실제 두fixture16페이지에 대조했다. 문구 문제만 종결하며 기존 Q1/Q2와 output-byte 요구·L01 미인증은 유지한다.','evidence':ev+['run:phases/011/tasks/regression-reading/evidence/reading-verification.json']},
{'item':'011/regression-reading/F3','action':'resolve','destination':['run:context.md#C12','run:phases/012/tasks/lean-smoke/objective.md'],'reason':'불변 runtime/host/공급자 입력·원자료/도구 조건과 corpus102 Git raw/clean으로 기존 승인 성질의 한정 재사용을 확인했다. PowerShell 역사 SHA와 미수행 G의 한계를 보존한다. Lean은012로, 예약/학술/최종관문은 plan의 후속으로 남긴다.','evidence':ev+['run:phases/011/manager-evidence/git-clean-observation.json']}],
'context_updates':[{'item':k,'action':'amend','destination':['run:context.md#'+k],'reason':v,'evidence':ev+['run:phases/011/manager-evidence/common-docs.diff','run:phases/012/tasks/lean-smoke/objective.md']} for k,v in ctxchanges.items()],
'plan_update':'011의 두 회귀/읽기 문구 수리를 종료하고 다음012를 Lean/Mathlib 실연쇄·T5/녹화/재생 work로 교체했다.010~011 제품 단위 마감을 지정했다. 공유 manifest/캐시/전체 생성의 독립성 때문에 단일 task로 배정하고 나머지 실제 경계는 이후로 분리했다. L01 외부결정·나머지 문서/의미 질문·T4보고와 G4~G8 관문/최종review 순서는 보존했다. common-docs.diff에 기존 의미의 변경·유지를 대조했다.',
'seam_updates':[], 'completion':None}
save(RUN/'phases/011/manager.pending.json',manager)

assert re.search(r'^convention_version: 27$',(REPO/'기억/세칙.md').read_text(encoding='utf-8'),re.M)
node=REPO/'기억/layer1/M-0561.md'; assert not node.exists()
node.write_text('''---
id: M-0561
layer: 1
title: host 관련 회귀와 읽기 문구 수리를 검수하고 Lean 실연쇄를 배정함
convention_version: 27
---

## 맥락

010에서 새 host T5는 성공했지만 기존 관련 선택에는 취소 fixture 오류와 네 포괄적 음성 단언이 남았다.011은 현 real_ports의 필수 인자를 전달하고 단일 수집/종료 성질과 반려 원인을 보강했다. manager는 양쪽136건의 선택/고유row/실제exit와 현재2644파일·종료판본을 대조해 정확한 이전 실패 두ID의 해소를 승인했다. 새 host 성공으로 기존 실패를 덮지 않고 같은 ID의 새 근거로 닫은 단위다.010~011 제품20경로를 관련 회귀 검수 뒤 함께 마감한다.

## 판단의 조건

일반 continuation 반례의 오류 문구는 False is not true라서 문자열만으로 소유 경로를 식별할 수 없다. 이 시험은 정상 source와 봉인 좌표가 같고 local_path만 resume-history라는 사실을 먼저 확인한다. 그 입력 조건과 실제 helper의 검사 순서를 함께 읽어야 오류 단언의 의미가 정해진다. checker의 메시지를 새 제품 코드로 만들거나 helper를 고칠 필요는 없었다.

읽기 절차의 수리도 인증 범위를 구별했다.010 원자료는 끝80행을 남기며 중간을 생략했고, 명시16페이지는160행을 전부 수신했다.011은 온전한 접두 또는 명시구간별 수신으로 모든 공백을 회수하도록 문구를 바꿨다. 출력 byte 기준과 실제 operator 프로필을 결정하지 않았으므로 문구 수리를 L01 용량 인증으로 세지 않는다.012의 Lean/Mathlib 작업은 그 외부결정과 독립적으로 진행할 수 있다.

manager 첫 보조 검산은 동일 diff를 파일 순서만 다르게 연결해 문자열 비교에서 실패했다. 순서만 교정한 재검산은 통과했다. 산출물의 내용 차이와 검산 도구의 표현 차이를 원파일로 구별했으며 task 원보고는 고치지 않았다.

## 보존과 다음 책임

추적 진입점은 `docs/do-math/continuous-development-2026-10-13/phases/011/manager.json`, `manager-evidence/review.md`, `verification.json`, `preservation.json`과012 objective다. 원task 자료와 현재 제품 원바이트는 `raw-evidence.zip`에도 보존한다. 일부 scratch·중복 snapshot은 압축으로만 추적하고 원경로와 stage/commit 행정 수신은 로컬 보관이므로 정리로 사라질 수 있다. 압축은 자동 복원 지시가 아니다.

012는 기존 설치/신뢰 상태를 바꾸지 않고 실제 Mathlib 대표 컴파일과 verifier 정상/오류, T5·녹화/재생을 연결한다. corpus manifest·전건 구조검사·미러·비용캐시를 공유해 한 task가 소유한다. 예약/학술·문서/의미 질문·전체 일반/fresh T3/변이와 최종review는 남는다. 기존 공급자/host 성공은 입력·경로·도구 조건의 승인된 범위에서만 재사용한다.
''',encoding='utf-8')
index=REPO/'기억/색인.md'; text=index.read_text(encoding='utf-8')
line='- M-0561 [host 관련 회귀와 읽기 문구 수리를 검수하고 Lean 실연쇄를 배정함] -- 양쪽136건 통과·정확 두실패 종결, L01 미정 유지·010~011 제품20경로 마감\n'
pos=text.find('\n## layer-2')
text=text[:pos]+ '\n'+line+text[pos:] if pos>=0 else text.rstrip()+'\n'+line
index.write_text(text,encoding='utf-8')
print('Prepared context/plan/seams diff, 012 assignment, pending manager and M-0561.')

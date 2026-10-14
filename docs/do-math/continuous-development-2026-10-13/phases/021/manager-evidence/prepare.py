"""Prepare phase 021 management records and bounded phase 022 assignment."""
from pathlib import Path
import difflib
import hashlib
import json

R = Path('C:/math')
RUN = R / 'docs/do-math/continuous-development-2026-10-13'
O = Path(__file__).resolve().parent
P = RUN / 'phases/021'
NEXT = RUN / 'phases/022'

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p, text):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8', newline='\n')
def save(p, obj): put(p, json.dumps(obj, ensure_ascii=False, indent=2) + '\n')
def ref(name): return 'run:phases/021/manager-evidence/' + name

v = read(O/'verification.json')
assert v['current_equal_final'] and v['task_files_unchanged'] == 242
assert not NEXT.exists() and not (P/'manager.json').exists()
old = {n:(RUN/n).read_text(encoding='utf-8-sig') for n in ('context.md','plan.md','seams.md')}
save(O/'common-before-sha.json', {n:sha(RUN/n) for n in old})

put(O/'review.md', '''# phase 021 검수

document-review는 A1/A3/A4 pass, A2 fail의 partial로 검수한다. report 검사를 먼저 통과했고, 시작2675파일과020 manager 검수본, 종료와 현재2675파일의 전건 SHA를 대조했다. 변경28개는 정본13시험/helper·미러13·비용캐시2이며 report와 writes에 일치한다. 기존 canonical/repository/planning 및 작문 도구 변경은 task 시작에 이미 포함돼 있었고 이번 작업에 귀속하지 않는다.

최종 정본/미러의 같은270선택은 고유row 전건에 대응하며 각269passed·Windows1314 symlink1skip·실제exit0다. 각875 Python은 현재와 같고 검사한 tree의 비캐시 전후가 같다. red 한 method의 네 subTest 실패, focus와 corrected1~3의 fixture/defer 오류를 원보고대로 유지한다. 자리 입력 검사는 불완전 ReviewScene에서 공개 활성화된 Sim의 같은 이름 method로 이동했다. failure-mapping.json은 이 한 ID의 이동과 나머지 정확 ID의 최종 passed를 구별한다. 과거 실패를 같은 ID의 성공으로 잘못 소급하지 않는다.

F1은 실제 요구 미충족이다. CLI-실행-계약.md의 입력 크기 조정은 검토 계보 전문을 role_review.proposal에 한 번 제공한다고 정한다. proposal_probe.py는 기존 공식 시험을 실행하면서 prepare_role_input 반환 사건을 관찰하고 생산 함수를 바꾸지 않는다. manager는 보존된15반환을 재귀 비교해 첫14개는1개, answer/initial-0의 마지막은2개의 같은 전문 map임을 검산했다. 두 위치는 context.role_review.proposal과 context.role_review.self_messages[0].content다. 공식row의 passed/exit0와 추가 의미 단언의 exit1을 구별한다. context_for는 현재판본 proposal 메시지를 그대로 복사하고 _record_review_input은 그 전문을 원 transcript에 봉인한다. 후속 수리는 원 transcript를 지우지 않고 현재 입력의 중복과 실제 참조 복원을 함께 다뤄야 한다. manager가 새 제품 실행을 수행한 것은 아니다.

네 owner의 실제 반환/소유/바이트 결속 성과는 유지한다. helper의 context_for 비교는 실제 생산값과 최종 입력의 일치 증거이며 단일 지급 계약의 독립 기대값은 아니다. 바로 이 차이 때문에 공식green으로 A2를 닫지 않는다. 고정 질문의 id/digest/question·정확 source snapshot/ref와 inline/artifact 바이트는 원request/저장자료와 대조하고 다른 경로의 같은 바이트를 구별한다. 현재 diff, 실제 helper·복원 코드와 B113/B114의 도입 hunk, 존재7원보고 SHA를 확인했다. P05 지정 필드 결속과 P04의 필드/가시성 성과는 승인하되 P04 단일 지급·A2 및 PR24 전체는 미종결이다.

F3의 runtime/실호출139입력·고정runtime/T4 258경로·corpus144경로/150명시SHA/Git raw-clean·host8자료/도구5·baseline910/Gitblob을 독립 검산했다. 제품 문서도 불변이다. 기존 실호출의 승인 성질만 한정 재사용하며022의 runtime 변경은 영향을 별도로 판단한다. --check1336과 skill-only 원출력 및 exit를 확인했다. 원task242파일은 검산 전후 불변이다. F4의 권한skip은 통과나 실제 탈출 반려 증거가 아니며 G4에 유지한다.

022는 F1과 P07의 submission_check/repair, 관련 N01-237/N01-260/N02-002/N02-014 고정 절을 한 task로 묶는다. 모두 실제 제출·최종 입력과 doc_code/engine_context·직접 소비·문서 회귀를 공유한다. 두 runtime 파일은 F1 수리에만 허용하고 submission/repair runtime의 의미는 고정한다. 나머지 P06/P10은 거버넌스 입출력, P09/P11은 조건/대기, P08은 trust/formal의 유한한 후속 후보로 묶으며 정확 phase는 현재 결과 뒤 정한다. 각 후보의 관련 N 절은 동일 소비자와 함께 처리한다. 이번에 독립 조사 task를 추가하지 않는다. 기존 packet이 이미 종료 질문과 현재 생산자를 주며, 수정 중인 공통 helper를 읽는 조사는 독립 검증이 아니고 동결 사본을 추가할 만큼 새 질문도 없다. 한 담당자가 공유 수정 뒤 최종 관련 선택·미러를 통합한다.

021의26비캐시 제품파일 커밋은 F1 수리와 관련 검수 뒤로 보류한다. 현재 제품 바이트와 task 원근거는 raw-evidence.zip에 보존한다. 이번 커밋은 관리 판단·022 배정·선별 원근거·기억 하나만 담는다. L01 Q1/Q2와 원문byte 기준, G4~G6/G8 및 다른 의미/문서 미결은 그대로다. G1~G8나 seam의 기준을 낮추지 않았다.
''')

context = old['context.md']
def add_c(cid, text):
    global context
    start = context.index('## '+cid+' ')
    end = context.find('\n## C', start+1)
    if end < 0: end = len(context)
    context = context[:end].rstrip()+'\n\n'+text+'\n\n'+context[end:].lstrip()

add_c('C2', 'phase 021 document-review는 A1/A3/A4 pass·A2 fail의 partial로 검수했다. report 검사 뒤 시작2675파일과020 검수본 동일, 종료/현재 전건 SHA 일치, 허용28변경(정본13·미러13·비용캐시2)을 확인했다. 최종 양쪽 같은270선택/고유row의 각269passed·Windows1314 symlink1skip·exit0와 각875Python/전후판본을 대조했다. red4반례와 초기fixture/defer 오류는 역사 실패로 유지하며 자리 입력 검사 한ID의 unit→sim 이동을 구별했다. 실제최종포장15반환 중 answer/initial-0에 제안 전문2개(기대1)가 있어 공식green과 별개로 A2가 미충족이다. 원task242파일 불변과 보존 경계는 run:phases/021/manager-evidence/verification.json·proposal-check.json·failure-mapping.json·review.md에 있다. 제품 전체 합격이 아니다.')
a=context.index('phase 001~020의 task 세션은 종료됐다.')
b=context.index('\n\n', a)
context=context[:a]+'''phase 001~021의 task 세션은 종료됐다.022 review-delivery 단일 work가021 F1의 제안 전문 단일 지급 수리와 P07의 submission_check/repair, 관련 N01-237/N01-260/N02-002/N02-014 절을 함께 맡는다. doc_code/engine_context·실제 제출/최종 입력·공통 문서 순회와 미러를 공유해 한 담당자가 통합한다. 기존 packet 외에 새 독립 조사 질문이 없어 병렬 조사 task는 두지 않는다. runtime 쓰기는 F1의 review_cycle/review_engine 두 파일에 한정하며 다른 runtime/runner/adapter/Job fixture·corpus·기존 연구·실호출은 고정한다. jobs1·전체worker3 이하·한 묶음씩·검사 중 소스 고정을 유지한다. 남은 P06/P10, P09/P11, P08/TRUST는 소비자별 후속 후보이며 문서 번호마다 phase를 고정하지 않는다.'''+context[b:]
add_c('C8', '021의 gpt-6.1-sol/high 수행을 검수했다.022 review-delivery도 같은 사용자 지정 model/effort로 배정하며 manager 설정과 제품 공급자 호출 설정은 구별한다.')
add_c('C9', '021 F2의 B113 role_review/review_research와 B114 pending_findings/review_sources 반환 추정 교체를 승인한다. 실제 hunk·현재 소비와 존재7원보고 SHA를 대조했고 명시 owner/별칭/callable·다른 packet의 단언은 유지한다. helper의 생산값 비교는 전달 일치의 근거이며 전문 단일 지급의 독립 계약을 대신하지 않는다. F1 수리는 별도이며 PR24 전체·나머지 hunk는 미종결이다. 근거는 run:phases/021/manager-evidence/history-check.json·review.md와 원task binding-review.md다.')
add_c('C10', '021에서 P04/P05 네 owner의 실제 필드·최종 전달·고정 원자료 결속을 검수했다. P05 지정 바이트/소유 성과는 유지하지만 P04 제안 단일 지급은 미충족이다. 실제 answer/initial-0 입력의 role_review.proposal과 self_messages[0].content가 같은 전문이며 기대1/실제2다. context_for는 현재proposal 메시지를 전문으로 남기고 _record_review_input은 원메시지를 봉인한다.022가 원봉인·가시성·이전판본 복원·정확참조를 유지하며 이 중복을 수리하고 독립 단언을 제품회귀에 넣는다. 같은 제출/역할입력 경계의 P07 submission_check/repair와 N01-237/N01-260/N02-002/N02-014도 묶어 실제check·수리 원문·최종입력을 확인한다. 일반green으로 A2를 닫지 않는다. 후속 후보는 P06/P10 거버넌스 입출력, P09/P11 조건/대기, P08 trust/formal이며 각각 관련 N 절을 결합한다. 기존 충분한 P01~P03·P05를 새 반례 없이 다시 열지 않는다. L01 Q1/Q2·원문byte 요구와 나머지 의미/최종관문은 유지한다. 근거는 run:phases/021/manager-evidence/proposal-check.json·review.md 및 run:phases/022/tasks/review-delivery/objective.md다.')
add_c('C11', '021의 최종 양쪽270선택에서도 ContextStoreTests.test_outside_symlink_is_reported_when_supported가 Windows1314로 각1skip됐다. 실제탈출 반려는 미검사이며 G4에서 원문상 조건의 정당성을 판정한다. 일반green과 별개인 제안 전문중복은022 work에 넘겼다. 근거는021 manager verification.json·proposal-check.json이다.')
add_c('C12', '021 F3의 보존 사실과 승인 성질의 한정 재사용을 검수했다. runtime/실호출139입력·corpus144경로/150명시SHA/Git raw-clean·host8자료/도구5·baseline910/Gitblob·고정runtime/T4 258경로 및 제품문서는 불변이다.022의 review runtime 변경은 이 목록의 불변을 일괄 요구하지 않고 실제 영향과 필요한 대체 증거를 구별한다.021의26비캐시 제품경로 커밋은 F1 수리/검수 뒤로 보류한다. 원task242파일과26제품 원바이트를 raw-evidence.zip에 보존하고 전건SHA·선별추적범위는 run:phases/021/manager-evidence/preservation.json에 둔다. 이번 마감은 관리인계·원근거·022배정·기억만 포함한다. 압축만 추적하는 원경로와 stage/commit 행정수신은 로컬 보관으로 정리 때 사라질 수 있으며 압축은 복원 지시가 아니다.')
assert context.split('## C2 ')[0] == old['context.md'].split('## C2 ')[0]
put(RUN/'context.md',context)

plan=old['plan.md'].replace('## phase 001~020의 결과와 현재 상태','## phase 001~021의 결과와 현재 상태')
a=plan.index('## 다음 phase: 021'); b=plan.index('## 가까운 후속 배정',a)
plan=plan[:a]+'''021은 A1/A3/A4를 승인한 partial이다. 양쪽 같은270선택의269passed·권한1skip과 실제15반환을 검수했으나 answer/initial-0의 전문중복 기대1/실제2로 A2가 남는다. P05 필드/원자료 성과와 P04의 나머지는 유지한다.26비캐시 제품경로는 수리 뒤 검수까지 커밋을 보류하고 현재 바이트를 관리근거에 보존한다.

## 다음 phase: 022

gpt-6.1-sol/high의 review-delivery 단일 work에021 F1과 P07을 묶는다. review_cycle.context_for·review_engine의 준비/원메시지 봉인/복원에서 현재 제안의 단일 지급을 수리하고 실제최종입력에 독립 기대값1을 넣는다. 원메시지·이전판본·봉인전 동료 비노출·정확ref/물질화 실패는 유지한다. submission_check.passed와 repair.previous_output은 실제 check_submission·route_submission_return·최종 역할 입력에 연결한다. check의 pass/capture 가능·중앙접수/편입, 원문과 수리범위를 구별한다.

관련 N01-237 입력 크기 조정, N01-260 제출/보존/편입, N02-002 시작 입력, N02-014 최종응답/수리의 고정 절도 같은 소비자와 대조한다. 이미 검수된 owner는 기존 근거로 유지하고 남은 이름·조합만 판정한다. 공유 doc_code/engine_context·직접 소비·문서·미러·캐시를 한 담당자가 소유해 최종 회귀를 합친다. 제출/수리 runtime은 고정하며 runtime 쓰기는 F1 두 파일에 한정한다. jobs1·한 묶음씩이며 최종 동일 선택을 양쪽에서 완결한다. 전체T4/새실호출을 이유 없이 반복하지 않는다.

020의24비캐시 제품경로는 HEAD44f4bb4b에서 마감됐다.021 제품26경로의 인도는022 수리 뒤 판단한다.022의 허용 runtime 변경이 과거실호출/전체T4 근거에 미치는 영향을 따로 기록한다. L01의 Q1/Q2와 원문byte 미충족, 최종 전체일반/freshT3/전수변이·최종review는 유지한다.

'''+plan[b:]
marker='007 공급자 변경과008~009'
idx=plan.index(marker,plan.index('## 가까운 후속 배정'))
plan=plan[:idx]+'''**021 manager의 묶음 결정:** 즉시 배정은 F1+P07 및 위 네 N 절이다. 남은 가까운 후보는 P06/P10의 거버넌스 입출력, P09/P11의 조건/대기, P08의 trust/formal이며 각 관련 N 절을 같은 소유자에 결합한다. 이들은 미래 고정 phase표가 아니고022 결과로 다시 범위를 확인한다. doc_code/engine_context·전건 문서 순회·미러/캐시가 겹쳐 동시 구현하지 않는다. 고정 원문의 독립 조사 자체는 가능하지만 기존packet이 생산자와 종료 질문을 이미 제공하므로 이번에 추가 조사만 위한 task를 만들 실익이 없다. 새 장기 batching 감사 없이 현재 정의를 확인해 결정했다. 한 세션에 남은 전부를 밀어 넣지 않는다.

'''+plan[idx:]
plan=plan.replace('019 P02와020 P03을 닫았다.021이 P04/P05 검토 입력 네owner를 맡고 P06~P11·N01~N03의 다른 미결 절은 후속으로 남긴다.', '019 P02·020 P03 및021 P05 지정 결속을 검수했다.022가 P04 단일 지급 미충족과 P07·관련 네 N 절을 맡는다. P06/P10, P09/P11, P08/TRUST 및 N의 나머지는 후속 후보로 남긴다.')
plan=plan.replace('019~020 관련 양쪽의 Windows1314 skip','019~021 관련 양쪽의 Windows1314 skip')
put(RUN/'plan.md',plan)
put(RUN/'seams.md',old['seams.md'].rstrip()+'''\n\n021의 실제 검토 필드/고정원자료 결속을 검수했지만 현재 제안 단일 지급은 미충족이다.022는 기존 CLI-실행-계약의 한 번 지급 약속에 맞게 review_cycle.context_for와 review_engine의 준비/봉인/복원만 수리한다. 저장 원메시지·정확ref·판본/slot·가시성/복원오류 계약을 유지하며 반환의중복을 계약으로 승인하지 않는다. P07은 기존 submission.check_submission·RepairExecutionMixin.route_submission_return의 실제 반환/입력소비를 검사하고 pass/capture/접수/편입을 구별한다. 같은 task가 구현/직접소비/helper·미러를 맡고 별도 병렬 제공자/소비자가 없어 S항목·provides/uses는 추가하지 않는다. 새 공개 형식이나 권한 개정이 필요하면 근거를 반환한다.\n''')

base='.claude/skills/do-math/'
previous=read(P/'phase.json')['tasks'][0]
files=[p[len(base):] for p in previous['writes'] if p.startswith(base)]
files += ['scripts/do_math/review_cycle.py','scripts/do_math/review_engine.py',
 'scripts/tests/unit/test_review_transcript_contract.py','scripts/tests/unit/test_review_engine_transcripts.py',
 'scripts/tests/unit/test_review_engine_stages.py','scripts/tests/flows/test_review_owner_flows.py',
 'scripts/tests/unit/test_submission_checks.py','scripts/tests/unit/test_submission_check_invariants.py',
 'scripts/tests/sim/test_repair_routing.py']
files=list(dict.fromkeys(files))
assert all((R/base/f).is_file() for f in files)
writes=[prefix+f for prefix in (base,base.replace('.claude/','.agents/')) for f in files]
inputs=[
 'run:sources/user-decisions.md','run:sources/model-policy-2026-10-14.md','run:sources/document-batching-2026-10-14.md',
 'run:phases/001/tasks/document-closeout/evidence/followup-packets.json',
 'run:phases/001/tasks/document-closeout/evidence/binding-inventory.json',
 'run:phases/001/tasks/closure-map/evidence/prior-review-state.json',
 'run:phases/021/tasks/document-review/report.json','run:phases/021/tasks/document-review/evidence/binding-review.md',
 'run:phases/021/tasks/document-review/evidence/proposal_probe.py',
 'run:phases/021/tasks/document-review/evidence/proposal-observation.json',
 'run:phases/021/tasks/document-review/evidence/proposal-return-14.json',
 'run:phases/021/tasks/document-review/evidence/related-selection.json',
 'run:phases/021/tasks/document-review/evidence/preservation.json',
 ref('verification.json'),ref('proposal-check.json'),ref('review.md'),ref('source-inspected.json'),
 'repo:docs/do-math/시험-재편-2026-09-29/설계.md',
 'repo:docs/do-math/시험-재편-2026-09-29/조사/결함-범주.md',
 'repo:'+base+'AGENTS.md','repo:'+base+'scripts/tests/시험-지침.md','repo:'+base+'scripts/이음새-정본.md',
 'repo:.claude/skills/writing-skills/references/멀티런타임_동기화.md']
inputs += ['repo:'+base+f for f in ('scripts/do_math/review_cycle.py','scripts/do_math/review_engine.py',
 'scripts/do_math/repair_execution.py','scripts/do_math/submission.py','scripts/do_math/context_store.py',
 'scripts/tests/support/doc_code.py','scripts/tests/support/engine_context.py',
 'scripts/tests/unit/test_submission_checks.py','scripts/tests/sim/test_repair_routing.py',
 'references/CLI-실행-계약.md','references/공통-실행.md')]
save(NEXT/'phase.json',{'kind':'work',
 'purpose':'021의 실제 검토 입력 전문중복을 수리하고 같은 제출·최종입력 경계의 P07과 관련 네 문서 절을 통합 검증한다.',
 'tasks':[{'id':'review-delivery','model':'gpt-6.1-sol','effort':'high','inputs':inputs,'writes':writes,'provides':[],'uses':[]}]})
(NEXT/'logs').mkdir()
(NEXT/'tasks/review-delivery/evidence').mkdir(parents=True)
put(NEXT/'tasks/review-delivery/objective.md', '''## 목적과 역할

G1/G3의021 F1(검토 제안 전문중복)과 P07(submission_check/repair)를 한 세션에서 닫는다. 실제 제출·검토 자리·최종 역할 입력, doc_code/engine_context·문서 순회가 겹치므로 한 담당자가 수정 뒤 최종 회귀와 미러 생성을 통합한다. 사용자 document-batching 지시를 적용한 유한한 묶음이다. P06/P10·P09/P11·P08/TRUST·L01의 별도 질문까지 넓히지 않는다.

021은 partial이다. A1/A3/A4와 P05의 지정 바이트/소유 성과를 검수했지만 A2의 전문 단일 지급은 기대1/실제2다. 원probe에서 공식row는passed/exit0이고 추가 의미단언은exit1이다. 기존green을 합격으로 바꾸거나 count=2를 정상 기대값으로 삼지 않는다. 이번 runtime 쓰기는 이 반례 수리에만 허용한다.

## 완료 조건

### A1 정확한 반례와 현재 경계 확인

시작 skills/diff를021 manager source-inspected2675파일과 대조하고 이전부터 있던 dirty 변경을 자기 작업에 귀속하지 않는다. 원probe와 proposal-return-14의 실제 두map, CLI-실행-계약의 「입력 크기 조정」 한 번 지급 문장, context_for·_record_review_input·_prepare_review_context·최종prepare_role_input의 경계를 확인한다. 현재 소비자/공유expected seat view와 원message·manifest·판본/digest/ref를 함께 대조한다.

기존 단계 시험/관찰을 재사용해 수리 전 실제 최종반환에서 전문중복을 실패시키는 독립 단언을 제품회귀에 편입한다. 계약에서 기대값1을 얻고 context_for의 결과를 그대로 기대값으로 복제하지 않는다. 최상위proposal 부재 단언만으로 대신하지 않는다. 원021 report/evidence는 고치지 않고 새 출력에 재현한다.

### A2 단일 지급과 원봉인·복원·가시성 보존

현재제안 전문은 필요한 검토 입력에서 role_review.proposal에 한 번만 제공하고 누적self_messages 등의 다른 위치에 같은전문을 반복하지 않는다. 원 transcript/manifest는 정확바이트·원출처·순서와 판본을 보존한다. 현재/이전제안, tool/delivered_prompt와 자기메시지의 참조를 지급하면 실제물질화 파일·ref/hash/bytes를 통해 정확원문을 회수할 수 있어야 한다. 기록을 삭제하거나 숨겨서 사본수를1로 만들지 않는다.

scope/initial/organize/answer/judge, 같은자리 재개와 제안판본변경의 기존 경로에서 원담당·봉인전 동료판단 비노출·봉인결과·pending finding 정확ref·고정질문/원자료를 유지한다. 조건별 정상/반례·손상/부재의 좌표있는복원오류를 확인하고 실제최종포장과 공유seat view가 일치해야 한다. 021의 실제반환 관찰과 동일의미의 기대1 단언이 최종제품검사에서 통과해야 한다. 생산/포장/복원함수를 대역으로 교체하지 않는다.

### A3 P07의 실제 제출 검사와 반려 원문 결속

followup-packets의 P07을 현재 문서와 실제생산자에 연결한다. check_submission이 만든 submission_check.passed와 route_submission_return이 queue/wait/후속action에 넣은 repair.previous_output을 기존 unit.test_submission_checks 및 sim.test_repair_routing의 실제 경로에서 읽는다. 정상/실패/not_checked를 구별하고 check.passed·capture_eligible·delivery.state=accepted·편입의 의미를 혼합하지 않는다. 반려한 정확실행/후보의 원문과 후속수리범위·원담당을 유지하고 최종 역할입력 또는 정확참조파일까지 전달을 확인한다.

반환사본의 passed/previous_output 삭제·다른제출/다른check 차용·import_check.sha256와의 소유혼동을 반려한다. 이미 현재정본/실제시험이 충분하면 그 성질과 담당을 구체적으로 연결하고 중복 구현하지 않는다. doc_code의 result/retry AST 두결속을 실제반환/입력검사로 교체하며 다른owner·B130~B134·P01~P05의 유효단언을 유지한다. 일반순회 위임은 정확owner/담당/실제문서검사호출과 누락반례를 갖추고 범용추론기·전역등록부를 추가하지 않는다. B110~B114의 관련 hunk·현재소비·존재원보고만 확인하며 PR24 전체를 재감사하지 않는다.

### A4 관련 네 문서 절의 이름과 의미 판정

고정범위는 N01-237 「입력 크기 조정」, N01-260 「제출, 보존과 편입」, N02-002 「시작할 때 입력을 확인한다」, N02-014 「최종 응답을 전달하고 필요한 오류를 수리한다」다. packet의 역사행번호 대신 현재제목/본문으로 경계를 찾고 해당절의 이름·표·코드펜스/조합을 실제정의/계약에 연결한다. 이미 승인된 P01~P05/B130~B134 성질은 현재불변 근거로 재사용한다. 각미결 이름에는 실제소유자 또는 구체적 비코드/파일명 제외이유를 남기며 단순전역어휘 존재로 통과시키지 않는다. 새소유자의 실제검증이 필요해 현재scope 밖이면 정확이름·문장·남은질문을 finding으로 반환한다. 기존보증을 약화해 절완료로 쓰지 않는다. 네절 밖 N모집단의 완료를 주장하지 않는다.

### A5 통합 회귀와 인도·재사용 판정

최종동일 관련선택을 정본/미러에서 완결해 selected/고유row/실제exit·전후소스SHA를 보존한다. 원반례의green과 기존실패/소유/가시성단언을 유지한다. 조건부symlink skip은통과로세지않고G4에남긴다. 쓰기범위 안의공식미러생성·캐시동기화·--check·skill-only를완료한다.

021 preservation의139실호출입력/258고정runtime-T4목록 중 이번허용review두파일이 바뀌면 그영향을명시하고 불변으로거짓기록하지않는다. 공급자전송/worker·host/Lean/예약/학술의 승인성질을 실제호출경로·도구와 대조해 한정재사용하거나 정확대체검증을지정한다. corpus144경로/150명시SHA·host8자료/도구5·baseline910과 무관runtime/제품은보존한다. 문서수정의향후prompt영향도구별한다.021의26비캐시경로와이번수리를manager가함께마감할수있게 실제변경과판본을보고한다. 전체일반/freshT3/전수변이/최종review의성공으로확대하지않는다.

## 판단과 경계

runtime 수정은 review_cycle.py와 review_engine.py의 F1 단일지급·정확복원에 필요한 범위만 허용한다. 참조표현과 내부수리는 현재원문계약을 만족하는 범위에서 재량이다. API/권한/원schema/검토가시성·저장정확성·이전판본의연구의미를 약화하지 않는다. submission.py/repair_execution.py/core_engine/context_store와 다른runtime·runner·adapter·Jobfixture·corpus·설치신뢰/공유설정은 고정한다. 다른결함은 반례·필요파일·영향A를 반환한다. 기존 dirty canonical/repository/planning 변경은 보존한다. writes의 모든파일을 수정할 의무는 없다.

공통helper·직접소비·허용문서·미러/캐시를 한task가소유한다. jobs1·전체worker3이하·한묶음씩·검사중소스고정이다. parent TEMP/TMP/TMPDIR는 저장소밖 짧은전용경로이며 git rev-parse가상위저장소를찾지않는지확인한다. output/resource cwd도짧게한다. 시간은소프트기준이며 단언을약화하지않는다. 새유료/예약/학술실호출·기존연구운전/삭제·graphify갱신·Git stage/commit/reset/checkout/push는배정하지않는다.

## 검증 방법

cwd C:\\math, Python C:\\Users\\wogud\\AppData\\Local\\Programs\\Python\\Python312\\python.exe. 공식 run_tests.py에 -u -B --jobs 1 --output <자기 evidence의 짧은새경로>를사용한다. argv/cwd/환경·PID/시각/종료·stdout/stderr·소스전후를보존하고 진행result는 read_bytes_shared로읽는다.

1. A1의수리전반례와 A3의실제입력없는문서통과반례를 필요한좁은선택으로 확인한뒤수리한다. 021 probe는원위치에서재실행하지않고 새evidence/제품시험에관찰만옮긴다.
2. 021 related-selection의 기존관련선택을유지하고 unit.test_review_transcript_contract unit.test_review_engine_transcripts unit.test_review_engine_stages flows.test_review_owner_flows unit.test_submission_checks unit.test_submission_check_invariants sim.test_repair_routing을합친다. 중복ID를제거해최종정본/미러에서같은모집단으로한번씩완결한다. 실제변경으로필요한정확소비시험을추가할수있지만 무조건전체suite로넓히지않는다. source_ref물질화·원메시지/manifest·최종포장·제안판본변경의정상/오류가이선택에서확인되는지판단하고빠지면정확사례를보완한다.
3. 미러생성전에허용경로계획을확인하고공식생성기를사용한다. 마지막캐시동기화후 build_skill_mirrors.py --check와 probe_cli.py --skill-only를통과한다. 새변경/실패/판본무효화없이는성공검사를반복하지않는다. 새T5/전체T4·G4~G6최종관문은이번배정밖이다.
4. A1~A5·실제changes·원반례와최종단언·역사재사용조건·미검사와구체적후속책임을report에기록한다. 지정Python으로 services/continuous-development/check.py report C:\\math C:\\math\\docs\\do-math\\continuous-development-2026-10-13 022 review-delivery를통과한다. 마지막응답은상태와report경로다.
''')

diff=''.join(''.join(difflib.unified_diff(old[n].splitlines(True),(RUN/n).read_text(encoding='utf-8').splitlines(True),
 fromfile=n+' before 021 manager',tofile=n+' after 021 manager')) for n in old)
put(O/'common-docs.diff',diff)
save(O/'common-after-sha.json',{n:sha(RUN/n) for n in old})

manager={
 'next':'022',
 'decision':'''021을 partial로 검수한다. A1/A3/A4와 P05의 지정 성과는 승인하지만 A2의 현재제안 단일지급은 실제최종반환 기대1/실제2로 미충족이다. 공식 양쪽269passed/권한1skip·exit0는 이 반례를 해소하지 않는다. 보존된15반환/원probe와 현재 context_for·_record_review_input·물질화경로 및 원문을 대조했다. manager는 제품을 수정하지 않았다.

사용자의 document-batching 지시를 적용해022 한 task에 F1 runtime수리와 P07의 실제제출검사/수리원문, 관련 N01-237/N01-260/N02-002/N02-014 절을 결합한다. 같은 doc_code/engine_context·최종입력/제출소비·문서회귀/미러를 한 담당자가 통합한다. 남은 P06/P10, P09/P11, P08/TRUST는 소비자별 후속후보로 묶고 결과에 따라 확정한다. 기존packet이 이미 종료질문을 제공하므로 새독립조사만을위한task는만들지않는다. 수정중인helper를읽는동시조사는독립검증이아니다. 남은전부를한세션에넣거나문서번호마다phase를고정하지않는다.

시작/종료/현재2675파일, 허용28변경, 최종270선택의고유row/exit/875Python, 원task242파일불변과보존경계를확인했다. 초기fixture오류와검사한ID의unit→sim이동은역사대로남긴다. 네발견을각각처리하며 P04미충족·G4권한skip·L01외부결정/원문byte와다른최종G관문은유지한다.021제품26경로의커밋은F1수리/검수까지보류하고원바이트를보존한다.이번커밋은관리인계·원근거·022배정·기억하나다.020제품은9a2f34e9에마감됐다. next:null이나최종review를제출할근거는아직없다.''',
 'reports':[{'task':'document-review','state':'read','detail':'전문을 읽고 report 검사를 통과했다. partial/A2 fail을 유지하며 A1/A3/A4와 지정 실제결속만 승인한다. 새제품실행 없이 실제파일/보고/원반환/판본을 대조했다.',
             'evidence':['run:phases/021/tasks/document-review/report.json',ref('report-check.json'),ref('verification.json'),ref('proposal-check.json'),ref('review.md')]}],
 'dispositions':[
  {'item':'021/document-review/F1','action':'carry','destination':['run:context.md#C10','run:plan.md','run:phases/022/tasks/review-delivery/objective.md#A2'],
   'reason':'실제현재전문2개와기대1을확인했다. 원봉인/가시성/참조복원을보존하는runtime수리와독립제품단언을022에배정한다.',
   'evidence':[ref('proposal-check.json'),ref('review.md'),'repo:.claude/skills/do-math/scripts/do_math/review_cycle.py']},
  {'item':'021/document-review/F2','action':'resolve','destination':['run:context.md#C9','run:context.md#C10'],
   'reason':'실제결속교체를actualdiff/현재소비/존재7원보고SHA로승인한다. PR24전체와F1은종결하지않는다.',
   'evidence':[ref('history-check.json'),ref('review.md'),'run:phases/021/tasks/document-review/evidence/binding-review.md']},
  {'item':'021/document-review/F3','action':'resolve','destination':['run:context.md#C12'],
   'reason':'139입력·258고정경로·corpus144/150SHA/Gitbytes·host8/tools5·baseline910을독립검산했다. 한정재사용만승인하고022 runtime변경의영향은A5에서재판정한다.',
   'evidence':[ref('verification.json'),'run:phases/021/tasks/document-review/evidence/preservation.json','run:phases/022/tasks/review-delivery/objective.md#A5']},
  {'item':'021/document-review/F4','action':'carry','destination':['run:context.md#C11','run:plan.md'],
   'reason':'양쪽정확symlink행의1314 skip을확인했다. G4에서원문상권한조건정당성을판정하며실제탈출반려통과로세지않는다.',
   'evidence':[ref('verification.json'),'run:phases/021/tasks/document-review/evidence/c/report.json','run:phases/021/tasks/document-review/evidence/m/report.json']}],
 'context_updates':[],
 'plan_update':'021 partial와F1/skip을반영했다.022에F1+P07+관련네N절을통합하고공유helper/회귀/미러담당을단일화했다. 나머지는P06/P10·P09/P11·P08의소비자별후속후보로묶었다. 독립조사실익이없어추가task는두지않는다.021제품26경로마감은수리뒤로보류하고원바이트를보존한다. G1~G8·L01외부결정·최종관문과기존유효조건/근거는보존했다. common-docs.diff는운영자의기존batching지시가들어있던실제현재본과의편집차이다.',
 'seam_updates':[], 'completion':None}
for cid,reason in [
 ('C2','021검수판본/부분완료·실제중복과초기검사이동을추가했다. 과거기록은유지했다.'),
 ('C5','종료phase를021로갱신하고022묶음·공유파일/자원독립성판단을명시했다. 기존사용자batching원문과실행규율은보존했다.'),
 ('C8','022에도사용자지정task모델을적용했다.'),
 ('C9','B113/B114한정교체승인과생산값대조의한계를추가했다. PR24다른slice는유지했다.'),
 ('C10','P05성과와P04단일지급미충족을구분하고F1+P07/네N절및후속묶음을지정했다. L01와기존완료는유지했다.'),
 ('C11','021권한skip과F1후속을추가했다. 최종관문조건은변경하지않았다.'),
 ('C12','보존과 한정 재사용, 26개 제품 경로의 커밋 보류 및 원바이트 보존을 명시했다. 022 runtime 변경의 영향은 후속 작업에서 재판정한다.')]:
    manager['context_updates'].append({'item':cid,'action':'amend','destination':['run:context.md#'+cid],
      'reason':reason,'evidence':[ref('verification.json'),ref('review.md'),ref('common-docs.diff')]})
save(P/'manager.pending.json',manager)
print('Prepared 022 review-delivery; wrote review, current context/plan/seams diff, and manager.pending.json.')

"""Write the reviewed handoff and next bounded assignment, without product edits."""
import difflib
import hashlib
import json
from pathlib import Path

R = Path('C:/math'); RUN = R/'docs/do-math/continuous-development-2026-10-13'
O = Path(__file__).resolve().parent
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def text(p, value): p.write_text(value.rstrip()+'\n', encoding='utf-8', newline='\n')
def save(p, value): text(p, json.dumps(value, ensure_ascii=False, indent=2))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
assert not (RUN/'phases/022/manager.json').exists()
assert read(O/'verification.json')['proposal_requirement_satisfied']
before = {n:(RUN/n).read_text(encoding='utf-8-sig') for n in ('context.md','plan.md','seams.md')}
save(O/'common-before-sha.json', {n:sha(RUN/n) for n in before})

shared = ['scripts/tests/support/doc_code.py','scripts/tests/support/engine_context.py',
 'scripts/tests/structure/test_doc_code.py','scripts/tests/boundary/test_engine_cli.py',
 'scripts/tests/unit/test_engine_trace_report_corruption.py','scripts/tests/unit/test_role_input_packaging.py',
 'scripts/tests/unit/test_storage_record_queries.py','scripts/tests/unit/test_storage_report_projections.py',
 'scripts/tests/unit/test_submission_preview_commands.py','scripts/tests/sim/test_knowledge_project_identity.py',
 'scripts/tests/sim/test_role_input_context.py','scripts/tests/sim/test_submission_review_inputs.py',
 'scripts/tests/unit/test_submission_checks.py','scripts/tests/sim/test_repair_routing.py']
direct = ['unit/test_governance_imports.py','unit/test_governance_records.py','unit/test_academic_requirements.py',
 'sim/test_governance_interpretation.py','sim/test_governance_context.py','sim/test_academic_consumers.py',
 'sim/test_academic_assessment_flow.py','sim/test_academic_public_currentness.py','flows/test_academic_requirement_flows.py',
 'unit/test_governance_decision_basis.py','unit/test_knowledge_impact_review.py','unit/test_submission_extension_semantics.py',
 'unit/test_planning_revision_validation.py','sim/test_planning_revision_transitions.py','sim/test_planning_revision_obligations.py',
 'support/governance_cases.py','support/governance_sim.py','support/academic_scenes.py']
docs = ['references/입력-소비자.md','references/초기화-운전.md','references/CLI-실행-계약.md','references/공통-실행.md']
relative = shared + ['scripts/tests/'+p for p in direct] + docs + ['scripts/tests/.timings.json','scripts/tests/.timings-t3.json']
writes = [tree+'/skills/do-math/'+p for tree in ('.claude','.agents') for p in relative]
assert len(writes) == len(set(writes)) and all((R/p).is_file() for p in writes)
inputs = ['run:sources/user-decisions.md','run:sources/model-policy-2026-10-14.md',
 'run:sources/document-batching-2026-10-14.md',
 'run:phases/001/tasks/document-closeout/evidence/followup-packets.json',
 'run:phases/001/tasks/document-closeout/evidence/binding-inventory.json',
 'run:phases/001/tasks/closure-map/evidence/prior-review-state.json',
 'run:phases/022/tasks/review-delivery/report.json',
 'run:phases/022/tasks/review-delivery/evidence/binding-review.md',
 'run:phases/022/tasks/review-delivery/evidence/current-sections.json',
 'run:phases/022/tasks/review-delivery/evidence/section-name-decisions.json',
 'run:phases/022/tasks/review-delivery/evidence/related-selection.json',
 'run:phases/022/tasks/review-delivery/evidence/preservation.json',
 'run:phases/022/manager-evidence/verification.json','run:phases/022/manager-evidence/proposal-check.json',
 'run:phases/022/manager-evidence/review.md','run:phases/022/manager-evidence/source-inspected.json',
 'repo:docs/do-math/시험-재편-2026-09-29/설계.md','repo:docs/do-math/시험-재편-2026-09-29/조사/결함-범주.md',
 'repo:.claude/skills/do-math/AGENTS.md','repo:.claude/skills/do-math/scripts/tests/시험-지침.md',
 'repo:.claude/skills/do-math/scripts/이음새-정본.md',
 'repo:.claude/skills/writing-skills/references/멀티런타임_동기화.md']
inputs += ['repo:.claude/skills/do-math/'+p for p in docs]
inputs += ['repo:.claude/skills/do-math/scripts/'+p for p in (
 'do_math/governance.py','do_math/academic.py','do_math/submission.py','do_math/integration.py',
 'do_math/planning.py','do_math/governance_engine.py','tests/support/doc_code.py','tests/support/engine_context.py',
 'tests/unit/test_governance_imports.py','tests/unit/test_governance_records.py','tests/unit/test_academic_requirements.py')]
phase = dict(kind='work', purpose='P06의 실제 수입/독립 검사와 P10의 헌장·학술 상태 조회를 같은 helper/소비 경계에서 수리하고022 F5의 거버넌스·개정 이름을 한정 판정한다.',
 tasks=[dict(id='document-governance', model='gpt-6.1-sol', effort='high', inputs=inputs, writes=writes, provides=[], uses=[])])
next_root=RUN/'phases/023'
(next_root/'logs').mkdir(parents=True,exist_ok=True)
(next_root/'tasks/document-governance/evidence').mkdir(parents=True,exist_ok=True)
save(next_root/'phase.json', phase)

updates = {
'C2': 'phase 022 review-delivery는 A1~A5 complete로 검수했다. report 검사 뒤 시작2675파일과021 검수본 동일, 종료/현재 전건 SHA 일치와 허용30변경(비캐시28·비용캐시2)을 확인했다. 정본/미러 같은364선택·고유row의 각363passed·Windows1314 symlink1skip·실제exit0와 각875Python/전후판본을 대조했다. 기존270선택은 모두 유지됐고 red 전문2!=1·red-doc 두owner 무입력 통과 반례가 새 양쪽passed에 대응한다. 실제 최종반환 각80개를 원JSON에서 재귀 검산해 현재 전문1개를 확인했다. task355파일·021원task242파일은 검산 전후 불변이다. A4는247개 절별 이름/소유 판단과 남은 의미 질문의 반환이며 네 절 전체 의미 합격이 아니다. 근거는 run:phases/022/manager-evidence/verification.json·proposal-check.json·review.md다. 전체G 완료가 아니다.',
'C8': '022의 gpt-6.1-sol/high 수행을 검수했다.023 document-governance도 같은 사용자 지정 model/effort로 배정한다. manager 설정과 제품 공급자 실호출 설정은 구별한다.',
'C9': '022 F2의 B112 repair/B113 submission_check AST 추정 교체를 승인한다. 현재 실제 check/route·최종포장, 관련hunk와 존재7원보고 SHA를 대조했다. 필드/실행/후보/check/수리범위 손상 반례·명시owner/별칭/callable 및 다른packet 단언은 유지한다. P07의 한정slice만 닫으며 PR24 전체나 역사counts의 새 성공은 아니다. 근거는 run:phases/022/manager-evidence/history-check.json·review.md와 원task binding-review.md다.',
'C10': '022 F1의 최소 review_cycle.context_for 수리로021 F1/A2의 현재 제안 전문중복을 종결한다. 현재/이전proposal 원메시지를 기존정확source_ref로 지급하고 role_review.proposal의현재전문은1회로 유지한다. 원turns/manifest·봉인·가시성·정확복원은 보존하며 review_engine/context_store는 불변이다. P07 실제 check_submission/route_submission_return의 필드·원담당·후보/수리범위·최종입력 결속도 검수해 닫는다. import_check와 submission_check, pass/capture/접수/편입은 구별한다. 근거는 run:phases/022/manager-evidence/proposal-check.json·review.md와 원task binding-review.md다.\n\n022 F5는 미결로 유지한다. 네 N 절의247개 이름/소유 판정은 전체 의미 인증이 아니다.023의 P06/P10 묶음이 N02-014의 impact_set/previous_hashes/revision_requests/revision_resolutions를 현재소비·기존검사와 대조한다. N01-237의 input_overflow_retry_resolved/failed·question_links와 N02-002의 input_overflow_requests/input_overflow_resolutions는 P09/P11 후보의 현재성/사용자retry 질문으로 남기며, N01-260 scope/replay_safety/repair_target은 운영처분·종료/재개권한 질문으로 함께 보존한다. P08/TRUST·그 밖의 N·L01 Q1/Q2와 원문byte 미충족·다른 의미/최종관문은 그대로다. 정확문장은 run:phases/022/tasks/review-delivery/evidence/section-name-decisions.json이며 다음책임은 run:phases/023/tasks/document-governance/objective.md와 plan이다.',
'C11': '022 F4의 최종 양쪽364선택에서도 ContextStoreTests.test_outside_symlink_is_reported_when_supported는 Windows1314로 각1skip이다. 실제탈출 반려는 미검사이며 G4 최종기본전체에서 원문상 환경조건 정당성을 별도 판정한다. 새363passed에 포함하지 않는다. review_cycle runtime 변경 이후018 전체T4를 현재 전체판본 동등성으로 주장하지 않으며 영향받는 검토/포장/복원은022 새관련근거를 사용한다. G4~G6/G7 최종판연결/G8은 남는다.',
'C12': '022 F3의 재사용은 변경 영향을 반영해 한정 승인한다.139실호출입력 중 정본review_cycle1변경·138불변, 고정runtime/T4 258경로 중 양쪽review_cycle2변경·256불변이다. corpus144경로/150명시SHA/Git raw-clean·host8자료/도구5·baseline910원바이트/Gitblob은 현재와 같다. 새설치support.zip/tool_sha256와 향후검토prompt는 바뀌므로 과거전체설치/동결사본 동등성이나 모델독해를 주장하지 않는다. 공급자전송/worker·host/Lean/held예약/학술 최소호출의 불변 하위경계 성질만 재사용하고 영향받는 검토slice는022의 실제반환/복원/포장 회귀로 교체한다.\n\n021의 보류26경로와022의28비캐시 경로의 합집합36제품경로를 이번 관리마감에서 커밋한다. 원task355파일과36제품원바이트는 raw-evidence.zip으로 보존하며 전건SHA/선별추적범위는 run:phases/022/manager-evidence/preservation.json에 둔다.021의 과거바이트는 기존021 압축을 유지한다. 압축만 추적하는 중복snapshot/scratch 원경로와 stage/commit 행정수신은 로컬 보관으로 정리 때 사라질 수 있으며 압축은 복원 지시가 아니다.023배정/관리·기억 추가는 검수한 제품판본을 바꾸지 않는다.'}
context = before['context.md']
for cid,addition in updates.items():
    start=context.index('## '+cid+' ')
    end=context.find('\n## ',start+1)
    end=len(context) if end<0 else end
    context=context[:end].rstrip()+'\n\n'+addition+'\n\n'+context[end:]
old = 'phase 001~021의 task 세션은 종료됐다.022 review-delivery 단일 work가021 F1의 제안 전문 단일 지급 수리와 P07의 submission_check/repair, 관련 N01-237/N01-260/N02-002/N02-014 절을 함께 맡는다. doc_code/engine_context·실제 제출/최종 입력·공통 문서 순회와 미러를 공유해 한 담당자가 통합한다. 기존 packet 외에 새 독립 조사 질문이 없어 병렬 조사 task는 두지 않는다. runtime 쓰기는 F1의 review_cycle/review_engine 두 파일에 한정하며 다른 runtime/runner/adapter/Job fixture·corpus·기존 연구·실호출은 고정한다. jobs1·전체worker3 이하·한 묶음씩·검사 중 소스 고정을 유지한다. 남은 P06/P10, P09/P11, P08/TRUST는 소비자별 후속 후보이며 문서 번호마다 phase를 고정하지 않는다.'
new = 'phase 001~022의 task 세션은 종료됐다.023 document-governance 단일 work가 P06 import_payload/import_check와 P10 governance/academic_validation, 관련 수입승인·현재조회 문장과022 F5의 개정 네 이름을 함께 맡는다. 같은 doc_code/engine_context·공통 문서 순회·직접 소비·미러/캐시를 한 담당자가 통합한다. 기존packet이 생산자/종료질문을 제공하고 새 고정판 독립 조사 산출물이 필요하지 않아 병렬task는 두지 않는다. 제품runtime/runner/adapter/Job fixture·corpus·설치신뢰·기존 연구·실호출은 고정한다. jobs1·전체worker3 이하·한 묶음씩·검사 중 소스 고정을 유지한다. P09/P11·P08/TRUST와022 F5의 나머지는 구체적인 후속 질문으로 보존한다.'
assert old in context
context=context.replace(old,new)
text(RUN/'context.md',context)

plan=before['plan.md'].replace('## phase 001~021의 결과와 현재 상태','## phase 001~022의 결과와 현재 상태')
begin=plan.index('## 다음 phase: 022'); finish=plan.index('## 가까운 후속 배정과 선행 관계',begin)
plan=plan[:begin]+'''022 A1~A5를 검수했다. 전문중복의 독립 기대1을 실제반환 각80개에서 확인했고 P07 실제제출/반려/포장 결속을 승인했다. 양쪽동일364선택은363passed·권한1skip이며 이전270선택도 전부 유지됐다. 네절의 이름247개는 소유/정의 검토이고 다른packet 의미는 F5에 남는다.02126·02228 비캐시경로의 합36제품경로를 이번에 마감한다. 근거는022 manager verification.json·proposal-check.json·review.md다.

## 다음 phase: 023

gpt-6.1-sol/high document-governance 단일 work에 P06/P10 네owner를 묶는다. validate_import_units의 실제payload 소비와 check_import가 반환하는 bundle.check, governance_view의 유일한현재헌장과 academic_status의 조건별 결과를 문서에 연결한다. import_check.sha256와 submission_check.passed를 구별하고, 검사승인/사용자권한/실제적용·수학해결/학술후속완료의 차이를 유지한다. 관련 입력-소비자 서두/거버넌스절·초기화-운전6절·CLI의 수입승인/학술상태·공통-실행의 예정개정 절을 같은 경계에서 확인한다.

022 F5 중 N02-014의 impact_set/previous_hashes/revision_requests/revision_resolutions는 정확 문장·현재소비·기존검사로 충분성을 판정하고 빠진 축만 보완한다. runtime 수리가 필요하면 반례를 반환한다. 같은 doc_code/engine_context·문서순회·직접소비·미러/캐시를 한 담당자가 소유하므로 구현 병렬화는 하지 않는다. 기존packet과 현재코드가 종료질문을 제공해 추가조사task의 실익이 없다. 최종 관련 선택을 변경 영향으로 정하고 양쪽에서 동일선택을 완결한다. 이전364개에 계속 누적만 하는 고정명령을 만들지 않으며, 소유단언을 제외하려면 비소비 근거를 남긴다.

022의 runtime변경으로 과거전체설치/T4의 최종판동등성은 주장하지 않는다. 불변하위경계의 실호출 성질만 재사용하고 영향받은 검토slice는022의 새근거를 쓴다. L01 Q1/Q2·원문byte 미충족, G4권한skip·최종전체일반/freshT3/전수변이·G7최종판연결·최종review는 유지한다.

'''+plan[finish:]
oldstart=plan.index('**021 manager의 묶음 결정:**'); oldend=plan.index('\n\n',oldstart)
plan=plan[:oldstart]+'''**022 manager의 묶음 결정:** P06/P10을023에 함께 배정한다. 남은 P09/P11에는022 F5의 입력초과 해소/실패·question_links·요청/해결의 현재성과 사용자retry를 결합한다. N01-260의 scope/replay_safety/repair_target은 운영처분의 정확종료·재개권한 질문으로 그 후속범위에 유지한다. P08/TRUST와 다른 N은 별도후보다. 고정 phase표가 아니며023의 실제결과로 다시 정한다. 이미 검수한 P01~P05/P07은 새반례 없이 다시 열지 않는다.''' +plan[oldend:]
plan=plan.replace('019 P02·020 P03 및021 P05 지정 결속을 검수했다.022가 P04 단일 지급 미충족과 P07·관련 네 N 절을 맡는다. P06/P10, P09/P11, P08/TRUST 및 N의 나머지는 후속 후보로 남긴다.', '019 P02·020 P03·021 P05 및022 P04 단일지급/P07을 검수했다.023이 P06/P10과 관련문장·F5의 개정 네 이름을 맡는다. P09/P11·P08/TRUST 및 F5의 다른의미/N 나머지는 후속으로 유지한다.')
plan=plan.replace('019~021 관련 양쪽', '019~022 관련 양쪽')
text(RUN/'plan.md',plan)
text(RUN/'seams.md',before['seams.md']+'''\n022의 기존단일지급 약속 수리와 실제 제출/반려 경계 결속을 검수했다. 원봉인/참조/복원·권한 의미는 개정하지 않았다.023은 기존 governance.validate_import_units/prepare_import/check_import/governance_view 및 academic.academic_status와 현재 적용/포장 소비를 사용한다. P06은 소비입력과 반환bundle.check를 구별하고 P10은 조건별실제조회와 지급을 구별한다. 정본은 기존함수/공유schema이며 문서검사에 중복제품정의를 만들지 않는다. 같은task가 helper·직접소비·미러를 소유하고 제품계약을 개정하지 않아 S항목·provides/uses는 추가하지 않는다. runtime·권한의 변화가 필요하면 정확반례를 후속으로 반환한다.\n''')

review='''# 022 manager 검수

review-delivery A1~A5를 배정 범위에서 승인한다. 이 phase는 work이며 전체 개발 완료가 아니다. report 전문과 형식 검사를 읽고 현재2675소스·허용30변경·원task355파일의 불변, 원report 선택/고유row/실제exit·각875Python과 전후판본을 독립 검산했다. 정본/미러 각364선택은363passed·권한1skip이며021의270선택은 전부 포함된다. 원red의2!=1과 red-doc의 두 ValueError 미발생은 실제출력에 있고 같은ID가 최종양쪽passed다. 초기diff 작성exit1은 개행 실현 가정의 증거도우미 오류이며 원실패는 보존한다.

현재 review_cycle.context_for의 변경은 proposal 원메시지를 기존 source_ref로 지급하는 한 분기다. 원turns/manifest를 바꾸지 않고 기존 review_engine의 정확물질화·context_store의 authorized seat 검사를 소비한다. 실제최종반환 각80개를 원JSON에서 재귀검산해 context.role_review.proposal에만 전문1개임을 확인했다. 실제단계시험의 독립 count, reference 원바이트/SHA/크기/판본, 현재source 사본 재생성·변조의 정확 복원진단과 이전proposal 복원시험을 현재코드에서 대조했다.021 F1/A2를 이 새 근거로 닫는다.

P07은 실제 check_submission의 후보/context/schema/extensions 정규해시·실행/모드/check ID와 passed를, 실제 route의 queue/wait·후속포장에 previous_output/수리범위를 연결한다. 문서 helper는 실제반환을 읽으며 두 AST추정을 제거했다. 다른check/후보/실행·필드삭제/반전·수리범위 교란과 defer 담당누락을 반려한다. 독립검사 승인·후보봉인·중앙접수·편입의 의미는 별도다. 관련B112/B113 hunk와 존재7원보고 해시를 검산해 이slice만 승인한다.

A4는 현재네절의 이름/소유 판정 및 남은 의미를 정확반환하는 조건이다.247행을 전체의미 인증으로 읽지 않는다.022 F5의 개정 네 이름은023 P06/P10과 함께 현재소비·기존검사 충분성을 판정하고, input_overflow/question_links·운영 scope/replay_safety/repair_target은 P09/P11 후속범위로 유지한다. L01의 운전프로필/단위 외부결정과 원문byte 기준은 그대로다.

139실호출입력 중 review_cycle1개·고정runtime/T4 258 중 양쪽2개가 바뀌었음을 확인했다. 나머지입력·corpus144/명시SHA150/Git raw-clean·host8/도구5/baseline910은 불변이다. 새 support.zip/tool_sha256와 검토prompt에는 영향이 있으므로 과거설치 전체동등성·현재모델독해·전체T4 최종판 성공은 주장하지 않는다. 영향받는검토/포장/복원은 새관련검사로 대체하고 불변하위경계의 승인된실호출 성질만 재사용한다. symlink 실제탈출 반려미검사는G4에남긴다.

사용자의 공유수정지점별 batching 지시에 따라023은 네owner의 P06/P10과 직접관련문장을 한담당자에게 배정한다. 공통helper/전건문서순회·미러/캐시 때문에 동시구현은 독립적이지 않다. 기존packet이 이미 생산자/종료질문을 제공해 추가조사만위한 task를 만들지 않는다. runtime은고정한다. 전체일반/freshT3/전수변이·G7 최종판연결·최종review는후속이다.

관리편집의 의미: C2에022검수, C5에023소유/독립성, C8에동일모델, C9에P07한정이력, C10에021반례종결과F5분배, C11에skip/최종판한계, C12에재사용영향/36제품인도를반영했다. G1~G8·L01·기존유효조건과역사실패는보존했다. plan의즉시배정을023으로바꾸고후속질문을유지했으며seams에는현재코드정본의소비설명만추가했다. 새S/API개정은없다. common-docs.diff로변경전후를대조한다.

021보류26과022비캐시28의합집합36제품경로, 이번인계/근거·023배정·기억을같은관리커밋으로마감한다. task원자료와제품원바이트는압축해전건재독SHA를확인한다. 선별추적경로와로컬보관한계는preservation.json에있다. 원report/evidence는고치지않으며push하지않는다.
'''
text(O/'review.md',review)

base='run:phases/022/manager-evidence/'
ev=[base+'verification.json',base+'review.md']
taskref='run:phases/022/tasks/review-delivery/report.json'
objective='run:phases/023/tasks/document-governance/objective.md'
manager=dict(next='023',decision='022 A1~A5를 검수해021 F1/A2의 전문중복과 P07 지정남김을 닫는다. 공식green과 별개인 독립기대1을 원반환각80개에서 확인했고, 기존270선택을 포함한 양쪽364선택의363passed/권한1skip·현재판본을 대조했다. 네절의247이름은 소유판정이며 F5의 다른의미를 종결하지 않는다. F5 개정네이름과 P06/P10을 공유helper·직접소비·문서·미러 경계로 묶어023단일work에 배정하고 입력초과/운영처분·P09/P11·P08/L01을 후속으로 유지한다. 같은helper/캐시/미러를 수정하는 동시구현은 독립적이지 않고 기존packet 외 새조사질문도 없어 별도병렬task를 두지 않는다. runtime은고정하고 관련최종검사선택은 실제변경영향으로 통합한다. 022 runtime수리는 과거설치전체바이트와 최종T4 동등성을 바꾸므로 기존실호출은 불변하위성질에 한정하며 최종전체일반/freshT3/전수변이/G7판본연결/제품수정없는review는 남는다. work phase이고 모든G근거가 없으므로 next:null을 제출하지 않는다.021/022의36비캐시제품을 검수된 현재판본으로 정확마감하며 원자료를보존하고push하지않는다.',
 reports=[dict(task='review-delivery',state='read',detail='report전문을 읽고 형식검사를 통과했다. A1~A5를 배정범위로 승인하며 A4의 전체의미 미검사는F5와후속으로 유지한다. task355파일·현재2675소스·30허용변경과 선택/원반환/이력/보존경계를 직접검산했다.',evidence=[taskref,base+'report-check.json',*ev,base+'proposal-check.json'])],
 dispositions=[
 dict(item='022/review-delivery/F1',action='resolve',destination=['run:context.md#C10'],reason='원봉인/복원·가시성을 유지하는 최소runtime수리와 실제최종반환의독립기대1로021 F1/A2를종결한다. 두phase제품합집합36경로를마감한다.',evidence=[base+'proposal-check.json',*ev]),
 dict(item='022/review-delivery/F2',action='resolve',destination=['run:context.md#C9','run:context.md#C10'],reason='B112/B113관련hunk·존재7원보고SHA와 실제check/route소비를대조해P07한정교체를승인한다. PR24전체나다른packet은닫지않는다.',evidence=[base+'history-check.json',*ev]),
 dict(item='022/review-delivery/F3',action='carry',destination=['run:context.md#C12','run:plan.md',objective],reason='review_cycle수리와파생support.zip/prompt변경을보존한다. 불변하위경계승인성질만재사용하고최종전체일반/T3/변이/G7판본연결/review책임을유지한다.',evidence=ev+['run:phases/022/tasks/review-delivery/evidence/preservation.json']),
 dict(item='022/review-delivery/F4',action='carry',destination=['run:context.md#C11','run:plan.md'],reason='Windows1314조건의symlink탈출반려는미검사다. G4최종기본전체에서원문상조건정당성을판정하며통과로세지않는다.',evidence=ev),
 dict(item='022/review-delivery/F5',action='carry',destination=['run:context.md#C10','run:plan.md',objective+'#A4'],reason='현재이름소유와전체의미를구별한다. 개정네이름은023거버넌스소비와함께판정하고overflow/question_links와운영처분scope/replay_safety/repair_target은P09/P11후속질문으로유지한다.',evidence=['run:phases/022/tasks/review-delivery/evidence/section-name-decisions.json',*ev])],
 context_updates=[dict(item=cid,action='amend',destination=['run:context.md#'+cid],reason=reason,evidence=ev) for cid,reason in [
 ('C2','022의완료범위·원자료검산과A4한계를추가했다. 역사partial/실패는보존한다.'),
 ('C5','종료phase를022로갱신하고023단일소유/고정runtime·병렬비배정이유를반영했다.'),
 ('C8','023에도사용자지정gpt-6.1-sol/high를적용한다.'),
 ('C9','P07의B112/B113한정slice교체만승인하고다른PR미검토를보존했다.'),
 ('C10','021 F1/P04와P07을새근거로닫고F5의정확이름/의미후속책임을나눴다. 다른packet/L01은보존했다.'),
 ('C11','022권한skip과runtime변경뒤최종판한계를추가하고G4~G8관문을유지했다.'),
 ('C12','139/258중허용변경과파생설치영향에따라재사용을한정하고36제품및원근거인도범위를기록했다.')]],
 plan_update='즉시배정을022에서023 P06/P10 네owner·관련수입승인/현재조회문장·F5개정네이름으로바꿨다. 공유helper·직접소비·문서순회·미러/캐시를통합하며고정364누적선택대신변경영향과담당보존으로최종선택한다. overflow/운영처분·P09/P11/P08/L01·권한skip·최종전체관문과review는보존한다. 기존보고를고치거나G요구를줄이지않았다.',seam_updates=[],completion=None)
save(RUN/'phases/022/manager.pending.json',manager)

assert 'convention_version: 27' in (R/'기억/세칙.md').read_text(encoding='utf-8')
assert sorted((R/'기억/layer1').glob('M-*.md'))[-1].name == 'M-0571.md'
text(R/'기억/layer1/M-0572.md','''---
id: M-0572
layer: 1
title: 제안 단일 지급 수리를 검수하고 수입과 현재 조회 문서 작업을 결합함
convention_version: 27
---

## 맥락

021의 실제검토입력은 공식green이면서 현재제안 전문을두번지급했다.022는 원proposal메시지를지우지않고 기존정확source_ref로지급하는한분기로수리했다. manager는 보존된최종반환각80개를재귀검산해전문1개를확인했고원봉인·물질화·이전판본·가시성검사의현재소비를대조했다.021의보류26경로와022의28비캐시경로는합집합36개이며이검수후같이마감한다.

## 판단에 남길 조건

작은runtime변경도파생설치물의바이트를바꾼다. review_cycle은기존실호출139입력에포함되며설치support.zip에도들어간다. 따라서과거동결설치전체가같다고쓸수없다. 이번에는어느함수가달라졌는지와실제호출경로를대조해공급자전송/worker·host/Lean/held예약/학술최소호출의변하지않은성질만재사용한다. 영향받는검토입력/복원은새회귀로교체하며전체일반/T3/변이와최종T4판본연결을남긴다. 단일파일해시차이를모든실호출반복으로바꾸거나,하위성질불변을전체소스동등성으로바꾸지않는다.

네문서절의247개이름에소유자를연결했지만의미전체를검사한것은아니다.022는input_overflow와개정요청·영향계산·운영처분의별도질문을정확문장과함께반환했다. 다음023에는P06/P10의네owner와개정네이름만묶고,overflow/운영처분은P09/P11후속으로유지한다. 이름목록크기를의미완료율로읽지않는다. 공유helper·문서순회·미러/캐시를한담당자가통합하며,반복비용절감은기존검증의무를누락하는근거가아니다. 관련선택은이전364개에누적만하지않고실제소비/변경영향과제외근거로정하도록배정했다.

P07의check.passed·capture·중앙접수·편입은서로다른판정이다. 실제check와반려원문을각소유자의현재값·정확실행·후보해시·수리범위에묶어검사했고다른check/후보차용반례를보존했다. B112/B113관련slice만닫으며다른문서/PR·L01외부결정·최종관문은남는다.

추적진입점은docs/do-math/continuous-development-2026-10-13/phases/022/manager.json과manager-evidence/review.md·verification.json·proposal-check.json이다. 원task355파일과36제품바이트는raw-evidence.zip에보존하고전건SHA/선별추적범위는preservation.json에있다. 압축만추적하는snapshot/scratch의원경로와stage/commit행정수신은로컬보관이며정리때사라질수있다. 압축은복원지시가아니다. 사용자지시에따라push하지않는다.
''')
index=R/'기억/색인.md'; value=index.read_text(encoding='utf-8')
assert '- M-0572 ' not in value
value=value.replace('## layer-1\n','## layer-1\n\n- M-0572 [제안 단일 지급 수리를 검수하고 수입과 현재 조회 문서 작업을 결합함] -- 원반환160개·36제품 마감, 파생설치 영향과 이름/의미 구별·023 P06/P10 통합\n',1)
text(index,value)
diff=''.join(''.join(difflib.unified_diff(before[n].splitlines(True),(RUN/n).read_text(encoding='utf-8').splitlines(True),fromfile=n+' before 022 manager',tofile=n+' after 022 manager')) for n in before)
text(O/'common-docs.diff',diff)
save(O/'common-after-sha.json',{n:sha(RUN/n) for n in before})
print(json.dumps(dict(next='023',writes=len(writes),products=read(O/'verification.json')['products_to_commit'],memory='M-0572'),ensure_ascii=False))

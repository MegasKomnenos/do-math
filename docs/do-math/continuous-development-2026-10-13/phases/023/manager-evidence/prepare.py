"""Prepare management documents without changing product or completed assignments."""
import difflib
import hashlib
import json
from pathlib import Path

R=Path('C:/math'); RUN=R/'docs/do-math/continuous-development-2026-10-13'
O=Path(__file__).resolve().parent
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def text(p,s): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(s,encoding='utf-8',newline='\n')
def save(p,v): text(p,json.dumps(v,ensure_ascii=False,indent=2)+'\n')
assert not (RUN/'phases/023/manager.pending.json').exists()
assert not (RUN/'phases/024').exists()
v=read(O/'verification.json'); assert v['sources']==2675 and v['products_to_commit']==32
before={n:(RUN/n).read_text(encoding='utf-8') for n in ('context.md','plan.md','seams.md')}
save(O/'common-before-sha.json',{n:sha(RUN/n) for n in before})
for n,s in before.items(): text(O/(n+'.before'),s)
base='run:phases/023/manager-evidence/'
taskref='run:phases/023/tasks/document-governance/report.json'
objective='run:phases/024/tasks/document-waits/objective.md'

review='''# phase 023 재시작 검수

document-governance의 원 report를 전문으로 읽고 report 형식 검사를 통과했다. A1~A5를 지정 범위에서 승인한다. 현재 skills/diff 2675파일은 task 종료 판본과 같고, 시작 판본은022 manager 검수본과 같다. 34변경은 report와 writes에 전건 대응한다. 비용 캐시2개를 제외한32개는 시험·지원과 미러이며 제품 runtime·문서는 불변이다.

원 manager.log에는503 재접속 실패와 model capacity 오류가 있다. manager.json/pending과 manager-evidence는 없었다. 기존 phase/task를 재실행하지 않고 별도 manager 검수만 수행했다. 기존 로그의 SHA와 크기, 원task891파일의 SHA를 보존한다. 이번 실행 로그는 logs/manager-restart-001.log이며 실행 중인 로그를 덮어쓰지 않는다.

## 근거와 판정

최종 c2/m 각각460선택·고유row의459passed/Windows1314 symlink1skip·실제exit0, 각875Python과 실행 전후 판본을 원report/process/source에서 대조했다. red의네 실제값 부재 반례, focus의3실패와 c의observer3오류를 새 양쪽passed ID에 연결했다. c/c2 제품판본은 같고 오류 trace는 evidence observer의action.role 가정에서 발생했다. run_suite_initial.py와 원실패는 유지한다. 이 오류를 제품 실패나 소급성공으로 바꾸지 않는다.

manager 첫 검산은 오류문을 str(list)에서 찾아 문자열 표현의 따옴표 이스케이프 때문에 assertion으로 종료됐다. 원검산 스크립트 verify.initial.py를 보존하고 details 원문을 join해 검사했다. 실제 bundle.status와 내부 check.decision도 구별했다. task 파일과 제품을 수정하지 않은 관리 검산 교정이며 최종 verify.py는 통과했다.

P06/P10의네 owner를 실제값 필수로 바꾼 doc_code와 실제 수입/헌장/학술 소비 diff를 확인했다. kind가 없는 비어 있지 않은 payload와 유효한 빈payload, bundle과check·check hash와submission passed, 검사승인과사용자권한을 구별한다. 정확 원입력과별도승인 원문, 활성헌장/정책판본 및 학술 조건별 실제반환과최종입력을 확인한다. 조회 성공이나 AST 호출 존재가 지급/권한 전체를 입증한다는 주장은 하지 않는다.

저장된 원JSON에서 양쪽각151최종반환 중52제안반환을 재귀검산해 전문1개를 확인했다. 실제check각45개의bundle/check SHA와상태를 대조했으며 학술조회각517개의여섯 상태를 확인했다. 입력에독립적인 기대와손상반례는 해당현재시험이 맡고 관찰목록은 새 일반시험을 대신하지 않는다. 제외한이전8모듈의현재SHA와비소비 근거, 기존engine_context함수전부 및 doc_code의두수정함수 외 불변을 확인했다.

N02-014의impact_set/previous_hashes/revision_requests/revision_resolutions는 정확문장과실제consumer·기존검사·새두반례를 대조했다. 계산된영향·해시전건·요청즉시무변경·해결소유의한정판정만 승인한다. B111/B113 해당AST결속을 교체하고 B110~B114의7원보고 및 B119~B122의4원보고 SHA를 다시확인했다. PR24 전체와다른N 의미는 미종결이다.

runtime/실호출139입력·고정경계258경로·corpus144경로/150명시SHA와Git raw/clean·host8자료/도구5·baseline910원바이트/Gitblob 및022원task355파일은 불변이다. 공식생성과 --check/skill-only의완료출력 및현재동일판본을 확인했다.022 이전전체설치/T4판본의한계와모델독해 미검증은 유지하며 승인된불변하위성질만 재사용한다.

## 후속과 인도

024에는P09(change)와P11(plan_settle_wait)의공유doc_code/engine_context·직접조건/배정검사를 묶는다.022 F5의입력초과/질문현재성·사용자retry와운영처분의정확문장을 기존소비검사에 연결한다. 두owner와한정문장만 대상으로하며일반정책엔진이나전체운영재설계는배정하지않는다. 같은helper·문서순회·미러/검사를한담당자가소유한다. 기존packet/현재소스가종료질문을제공하므로독립조사task의이득이없다. 한세션의범위로고정하고새runtime결함은정확반례로반환한다.

원task891파일과32제품원바이트·이전manager.log를raw-evidence.zip에SHA검산해보존하고선별원경로를함께추적한다. 기존관리자료는삭제하지않는다. context/plan의변경차이를보존하며G1~G8과L01 Q1/Q2·원문byte미충족·권한skip·최종관문은유지한다. 형식handoff통과후manager.json을게시하고정확파일과M-0573노드를한커밋으로마감한다. 무관dirty/untracked·운영자변경은포함하지않고push하지않는다.
'''
text(O/'review.md',review)

ctx=before['context.md']
def append_section(value,cid,paragraph):
 marker='## '+cid+' '; start=value.index(marker); end=value.find('\n## C',start+len(marker))
 if end<0:return value.rstrip()+'\n\n'+paragraph+'\n'
 return value[:end].rstrip()+'\n\n'+paragraph+'\n\n'+value[end:]
updates={
'C2':'phase 023 document-governance는 A1~A5 complete로 검수했다. 재시작 manager가 report 검사 후 시작2675파일과022 검수본 동일, 종료/현재전건SHA일치 및허용34변경(비캐시32·비용캐시2)을 확인했다. 최종양쪽동일460선택/고유row의459passed·Windows1314 symlink1skip·실제exit0와각875Python/전후판본을 대조했다. 원반환각151개 중제안52개의전문1, check각45개/학술조회각517개를 검산했다. task891파일과022원task355파일은불변이다. red4subTest·focus3실패·observer3오류는역사실패로보존하며최종passed와연결했다. 근거는 run:phases/023/manager-evidence/verification.json·return-check.json·review.md다. 지정P06/P10과개정네이름의완료이며전체G완료가아니다.',
'C7':'023의원manager는503/model capacity오류로제출전에종료했다. 사용자의명시적재시작으로같은완료task를재실행하지않고원report/evidence와현재파일만검수했다. 이전manager.log는SHA와원바이트로보존했고기존pending/manager-evidence는없었다. 별도로그는run:phases/023/logs/manager-restart-001.log다. 모델정책을바꾸거나023task로되돌리지않으며024배정후관리마감을수행한다. 근거는 run:phases/023/manager-evidence/restart-state.json·review.md다.',
'C8':'023의gpt-6.1-sol/high수행을검수했다.024 document-waits에도같은model/effort를명시한다. 재시작manager는기존settings의gpt-6-astra/xhigh선택으로호출되며capacity오류를다른모델자동선택의근거로삼지않았다. 제품공급자실호출설정과구별한다.',
'C9':'023 F2의B111/P10과B113/P06 AST결속교체를승인한다. 실제hunk·현재소비와존재7원보고, B119~B122 PURE4원보고SHA 및기존helper/소유단언불변을대조했다. 관련slice만종결하며PR24전체·다른hunk·역사counts의새성공합산은하지않는다. 근거는 run:phases/023/manager-evidence/history-check.json·review.md와원task binding-review.md다.',
'C10':'023 F1의P06/P10지정남김을닫는다. 실제payload/check의원문·seal·독립execution과수신/적용, 유일헌장과별도승인원문·판본, 학술조건별조회와최종입력을검수했다. runtime/문서는불변이며검사승인/사용자권한/적용및수학해결/학술후속의구분을유지한다.023 F3는022 F5중개정네이름의정확문장만종결한다. 나머지input_overflow_retry_resolved/failed·question_links와input_overflow_requests/resolutions, scope/replay_safety/repair_target은024의P09/P11조건·대기·재시도묶음에현재소비/기존검사로한정배정한다. P08/TRUST·다른N/L01 Q1/Q2와원문byte미충족은유지한다. 근거는 run:phases/023/manager-evidence/review.md와 run:phases/024/tasks/document-waits/objective.md다.',
'C11':'023 F4의최종양쪽460선택에서도ContextStoreTests.test_outside_symlink_is_reported_when_supported는Windows1314로각1skip이다. 실제탈출반려는미검사이며G4최종기본전체에서원문상환경조건정당성을판정한다.459passed에포함하지않고G4~G6/G7최종판연결/G8은유지한다. 근거는 run:phases/023/manager-evidence/verification.json이다.',
'C12':'023 F5의보존과불변하위경계재사용을검수했다.022판본기준139실호출입력·258고정경계·144corpus/150명시SHA/Git raw-clean·host8/도구5·baseline910과원task355파일은불변이다. 과거전체설치/T4및모델독해의한계는유지한다. 검수된32비캐시시험/미러경로를이번관리커밋으로마감한다.023원task891파일·32제품원바이트·이전manager.log는raw-evidence.zip에보존하며전건SHA와선별추적범위는 run:phases/023/manager-evidence/preservation.json에둔다. 압축만추적하는반환/snapshot/scratch의원경로와진행중재시작로그·stage/commit행정수신은로컬보관으로정리때사라질수있으며압축은복원지시가아니다.024배정·관리/기억추가는제품판본을바꾸지않는다.'}
for cid,s in updates.items():ctx=append_section(ctx,cid,s)
old=next(p for p in ctx.split('\n\n') if p.startswith('phase 001~022의 task 세션은 종료됐다.'))
ctx=ctx.replace(old,'phase 001~023의 task 세션은 종료됐다.024 document-waits 단일 work가 P09 조건입력change와P11 plan_settle_wait를같은doc_code/engine_context·배정/문서검사경계에서통합한다.022 F5의입력초과/질문현재성·retry와운영처분의정확문장을기존소비검사에연결한다. 같은helper·문서순회·미러/캐시를한담당자가소유하며기존packet이종료질문을제공해별도병렬조사는두지않는다. runtime/runner/adapter·Job fixture·corpus·공유설치/연구·실호출은고정한다. jobs1·전체worker3이하·동시에한묶음·검사중소스고정을유지하고관련최종선택은실제변경영향으로정한다. P08/TRUST·그밖의N/L01과최종관문은남는다.',1)
text(RUN/'context.md',ctx)

plan=before['plan.md'].replace('## phase 001~022의 결과와 현재 상태','## phase 001~023의 결과와 현재 상태',1)
a=plan.index('## 다음 phase: 023'); b=plan.index('## 가까운 후속 배정과 선행 관계',a)
plan=plan[:a]+'''023의 A1~A5를 검수했다. P06/P10 네owner와개정네이름의지정범위를닫았으며정본/미러각460선택의459passed·권한1skip및실제반환을확인했다.34변경중32비캐시시험/미러경로를마감한다. 재시작은원task/로그를보존한manager검수이며task재실행이아니다. 근거는023 manager verification.json·return-check.json·review.md다.

## 다음 phase: 024

gpt-6.1-sol/high document-waits 단일work에P09(change)와P11(plan_settle_wait)를묶는다. evaluate_condition의실제사용자결정/현재성/자료형과_dispatchable의실제대기·해소를문서에연결한다. 조건입력의부재/null과반환형식을혼동하지않고plan_settle의대상·시각경계·명시요청/recovery우회·최초준비예외를기존시계주입검사로확인한다.

022 F5의정확문장인input_overflow_retry_resolved/failed·question_links, input_overflow_requests/resolutions와scope/replay_safety/repair_target을현재실제소비·기존검사에연결한다. 이미충분하면유지하고빠진축만허용시험에서보완한다. 범용정책추론이나제품runtime수리는배정하지않으며필요하면정확반례를반환한다. 공유doc_code/engine_context·문서순회·미러/캐시를한담당자가통합한다. 기존packet/현재코드가유한한종료질문을제공하므로독립조사task는추가하지않는다.

최종관련선택은변경영향과실제담당을기준으로정하고양쪽에서같은선택을완결한다.023의460건을기계적으로누적하지않는다. 기존P01~P07/P10·PURE의소유/오류/단일지급보증은유지하며제외에는비소비/판본근거를남긴다. P08/TRUST·다른N/L01 Q1/Q2·원문byte미충족·G4권한skip과최종전체일반/freshT3/전수변이/G7최종판연결/최종review는남는다.

'''+plan[b:]
start=plan.index('**022 manager의 묶음 결정:**'); end=plan.index('\n\n',start)
plan=plan[:start]+'''**023 manager의 묶음 결정:** P06/P10과개정네이름은검수해닫고P09/P11의조건·대기와022 F5의나머지정확문장소비를024에합친다. 공유helper의두owner교체와기존대기/재시도검사연결이라는한정범위다. 문서번호별phase반복·공유파일병렬수정을하지않는다. 이미검수한P01~P07/P10은새반례없이재개하지않으며P08/TRUST·다른N은후속후보다.024의실제결과로다음범위를정한다.'''+plan[end:]
plan=plan.replace('023이 P06/P10과 관련문장·F5의 개정 네 이름을 맡는다. P09/P11·P08/TRUST 및 F5의 다른의미/N 나머지는 후속으로 유지한다.','023 P06/P10과개정네이름을검수했다.024가P09/P11과F5의입력초과/운영처분정확문장을맡고P08/TRUST·다른N은후속으로유지한다.')
plan=plan.replace('019~022 관련 양쪽의 Windows1314 skip','019~023 관련 양쪽의 Windows1314 skip')
text(RUN/'plan.md',plan)
text(RUN/'seams.md',before['seams.md'].rstrip()+'''\n\n023의실제수입/헌장/학술소비를검수했다.024는기존planning.evaluate_condition/task_scope.decision_is_current와DispatchEngineMixin._plan_settle_waits/_dispatchable, input_overflow/운영처분의기존생산/소비경계를문서검사에연결한다. 입력/반환/권한/해소의정본은현재함수와공유schema이며문서용제품계약을복제하지않는다. 같은task가helper·직접소비·미러를소유하므로S항목·provides/uses는추가하지않는다. runtime계약변화가필요하면정확반례를후속으로반환한다.\n''')

common_consumers=['boundary/test_engine_cli.py','unit/test_engine_trace_report_corruption.py','unit/test_role_input_packaging.py','unit/test_storage_record_queries.py','unit/test_storage_report_projections.py','unit/test_submission_preview_commands.py','sim/test_knowledge_project_identity.py','sim/test_role_input_context.py','sim/test_submission_review_inputs.py','unit/test_submission_checks.py','sim/test_repair_routing.py']
specific=['unit/test_planning_conditions.py','unit/test_planning_condition_validation.py','sim/test_scheduling_session_slots.py','sim/test_engine_input_overflow.py','flows/test_engine_input_recovery.py','sim/test_scheduling_recovery_dispositions.py','unit/test_repair_execution.py','unit/test_submission_extension_semantics.py','unit/test_governance_question_contracts.py','unit/test_governance_questions.py','sim/test_governance_questions.py','flows/test_governance_question_flow.py']
supports=['support/doc_code.py','support/engine_context.py','structure/test_doc_code.py','support/engine_overflow.py','support/recovery_cases.py']
# Only existing support helpers are authorized; no guessed paths in the assignment.
supports=[p for p in supports if (R/'.claude/skills/do-math/scripts/tests'/p).exists()]
tests=list(dict.fromkeys(common_consumers+specific+supports))
assert all((R/'.claude/skills/do-math/scripts/tests'/p).exists() for p in tests)
docs=['references/과제-착수조건.md','references/CLI-실행-계약.md','references/공통-실행.md','references/초기화-운전.md','계약/운영-점검.md','계약/연구-계획.md']
assert all((R/'.claude/skills/do-math'/p).exists() for p in docs)
writes=[f'{tree}/skills/do-math/{p}' for tree in ('.claude','.agents') for p in
 [*('scripts/tests/'+p for p in tests),*docs,'scripts/tests/.timings.json','scripts/tests/.timings-t3.json']]
inputs=['run:sources/user-decisions.md','run:sources/model-policy-2026-10-14.md','run:sources/document-batching-2026-10-14.md',
 'run:phases/001/tasks/document-closeout/evidence/followup-packets.json','run:phases/001/tasks/document-closeout/evidence/binding-inventory.json',
 'run:phases/001/tasks/closure-map/evidence/prior-review-state.json',taskref,
 'run:phases/022/tasks/review-delivery/evidence/section-name-decisions.json','run:phases/022/tasks/review-delivery/evidence/current-sections.json',
 'run:phases/023/tasks/document-governance/evidence/binding-review.md','run:phases/023/tasks/document-governance/evidence/related-selection.json',
 'run:phases/023/tasks/document-governance/evidence/selection-decisions.json','run:phases/023/tasks/document-governance/evidence/preservation.json',
 base+'verification.json',base+'source-inspected.json',base+'return-check.json',base+'review.md',
 'repo:docs/do-math/시험-재편-2026-09-29/설계.md','repo:docs/do-math/시험-재편-2026-09-29/조사/결함-범주.md',
 'repo:.claude/skills/do-math/AGENTS.md','repo:.claude/skills/do-math/scripts/tests/시험-지침.md','repo:.claude/skills/do-math/scripts/이음새-정본.md',
 'repo:.claude/skills/writing-skills/references/멀티런타임_동기화.md']
inputs += ['repo:.claude/skills/do-math/'+p for p in docs]
inputs += ['repo:.claude/skills/do-math/scripts/do_math/'+p for p in ('planning.py','task_scope.py','dispatch_engine.py','input_overflow.py','operational_engine.py') if (R/'.claude/skills/do-math/scripts/do_math'/p).exists()]
inputs += ['repo:.claude/skills/do-math/scripts/tests/'+p for p in [*specific,'support/doc_code.py','support/engine_context.py']]
phase=RUN/'phases/024'; task=phase/'tasks/document-waits'
(task/'evidence').mkdir(parents=True); (phase/'logs').mkdir(); text(phase/'logs/.gitkeep','')
save(phase/'phase.json',dict(kind='work',purpose='P09/P11의조건입력과실제대기문서결속을통합하고022 F5의재시도/운영처분정확문장을같은기존소비검사에연결한다.',
 tasks=[dict(id='document-waits',model='gpt-6.1-sol',effort='high',inputs=inputs,writes=writes,provides=[],uses=[])]))
text(task/'objective.md','''## 목적과 역할

G1/G2/G3의문서P09(change)와P11(plan_settle_wait)를같은조건·배정경계에서닫는다.023의P06/P10은검수됐으며완료task를다시실행하지않는다. doc_code/engine_context·공통문서순회·직접소비·미러/관련검사를한담당자가통합한다.022 F5의남은정확문장만현재소비/기존검사와대조한다. 최종review가아닌한정work다.

## 완료 조건

### A1 현재 문장과 실제 경계

시작skills/diff를023 manager source-inspected2675파일과대조하고기존dirty를보존한다. P09/P11의역사좌표를현재제목/문장과정확owner에연결한다. 현재doc_code의change 소비AST와plan_settle_wait 반환AST가어떤성질을입증하지못하는지확인하고빠진경계에는수리전반례를남긴다. 실제입력/반환·공유계약·독립기대값을사용하며현재생산값의복사나AST모양을기대값으로삼지않는다. 충분한기존검사는정확ID·판본·보호성질로재사용한다.

### A2 P09의 실제 결정 소비

과제-착수조건의decision_value_is 문장을실제evaluate_condition과decision_is_current에연결한다. 현재유효결정/부재·무효결정, 과제범위일치/불일치, 값의자료형(예:true와1), change.value부재/null과전체change fallback을현입력계약에맞게구별한다. get으로읽는필드를필수출력으로잘못만들지않는다. 변경종류/대상/field가다른사례와basis/오류/ready-not_ready를기존시험에서확인하고빠진축만보완한다. 문서표·JSON예시와기존조건문법검사는유지한다. AST소비추출을실제입력문서검사또는기존공유계약으로교체하며실제평가기/현재성함수를대역으로가리지않는다.

### A3 P11의 실제 대기와 해소

CLI-실행-계약의plan_settle_seconds/dispatch_wait 및최초준비설명을실제_plan_settle_waits와_dispatchable·기존시계주입scene에연결한다. 계약검토유무/대기·실행상태의실제queue표현, 최초기준시각의유지, 제한전/동일시각/이후, requested_by/recovery우회, 해소뒤오래된dispatch_wait제거를확인한다. 모든후보를처음부터기다린다는잘못된해석과초기준비사건의소유/응답수락후소비를구별한다. 문서값없는통과·다른대기객체차용·필드삭제/변조반례를실제값과독립조건에연결한다. D-06의정확조건/예외표를남기되임의실시간timeout·일반정책추론기를만들지않는다.

### A4 관련 N 문장과 기존 변경의 한정 판정

022 section-name-decisions의N01-237 input_overflow_retry_resolved/failed·question_links, N02-002 input_overflow_requests/input_overflow_resolutions, N01-260 scope/replay_safety/repair_target의정확문장만현재소비·기존시험에연결한다. retry요청은질문해소가아니며실제재포장성공/다시실패와기존사용자해소/원artifact보존, 일반resume비해소·허용프로필/현재성/역할권한을구별한다. 운영retry는선행실행종료/봉인·같은활동/새작업공간·현재입력/프로필/권한/예산을확인하며설치repair의별도권한을우회하지않는다. 기존충분한검사는재구현하지않는다. 허용범위를넘는runtime결함은정확입력/기대/실제·필요파일·영향G를finding으로반환한다.

P11의5개lexical policy 후보는현재정의와문장별유지/해당소유자책임을기록하되이름존재를전체의미완료로바꾸지않는다. P09/P11에직접관련된B110~B114/D-06 hunk·현재소비·존재원보고만대조한다. P01~P07/P10·PURE의유효한성질과제안전문1/봉인복원을보존한다. P08/TRUST·다른N/L01·PR24전체는범위밖이다.

### A5 통합 회귀와 보존·인도

최종관련선택을실제변경영향과공통문서담당/직접소비로정하고정본/미러에서동일선택을완결한다. selected/고유row/exit·전후Python SHA를보존하며기존460건에계속누적하는고정선택을만들지않는다. 제외에는비소비/판본근거를남기고새위임은정확owner/실제문서검사담당·누락/오기반례를유지한다. 공식미러사전계획·생성·캐시동기화·--check·skill-only를완료한다.023기준runtime/실호출139입력·고정경계258·corpus144/명시SHA150/Git raw-clean·host8/도구5·baseline910및완료원task891파일은보존한다. 기존실호출은불변하위성질만재사용하고문서변경시미래prompt영향을명시한다. Windows1314 symlink skip·최종전체일반/freshT3/전수변이/G7최종판연결/최종review는남김으로구별한다.

## 판단과 경계

제품runtime·스키마·포트·runner/adapter·Job fixture·corpus·공유설치/신뢰·기존연구는고정한다. writes의문서/시험/지원만수리한다. 실제제품규칙과원문이충돌하면문장을약화하거나오류를정상으로바꾸지말고반례를반환한다. 기존AST helper는마지막다른소비자가남으면유지한다. 새범용추론기·전역등록부·중복제품schema를추가하지않는다.

한담당자가공유helper·직접소비·미러를소유한다. jobs1·전체worker3이하·동시에한묶음·검사중소스고정이다. parent TEMP/TMP/TMPDIR는저장소밖짧은전용경로를쓰고상위Git미발견/최종resource cwd를확인한다. 시간은소프트기준이다. 새유료/예약/학술실호출·기존연구재개/삭제·graphify갱신·Git stage/commit/reset/checkout/push는배정하지않는다. 지정경계를벗어난새개선은확장하지않고정확finding으로반환한다.

## 검증 방법

cwd C:\\math. Python C:\\Users\\wogud\\AppData\\Local\\Programs\\Python\\Python312\\python.exe. 공식run_tests.py에 -u -B --jobs 1 --output <자기evidence의새짧은경로>를사용한다. 원argv/cwd/환경·PID·시각·exit·stdout/stderr와소스전후를보존하고진행result는read_bytes_shared로읽는다.

직접관련진입점은unit.test_planning_conditions/condition_validation, sim.test_scheduling_session_slots, sim.test_engine_input_overflow, flows.test_engine_input_recovery, sim.test_scheduling_recovery_dispositions, unit.test_repair_execution과기존질문/제출확장검사다. 넓은모듈을무조건전부누적하지말고A별정확기존성질과변경영향을확인해선택한다. 공통doc_code/engine_context의문서담당은누락하지않는다. 성공한동일검사는새변경/실패/근거무효화이유없이반복하지않는다. 최종양쪽은같은선택과판본으로완결한다.

report에A1~A5·실제changes·모든finding·재사용/미검사범위를작성하고지정Python으로 services/continuous-development/check.py report C:\\math C:\\math\\docs\\do-math\\continuous-development-2026-10-13 024 document-waits 를통과한다. 마지막응답에상태와report경로를알린다.
''')

ev=[base+'verification.json',base+'review.md']
manager=dict(next='024',decision='사용자재시작요청에따라완료된023 task를재실행하지않고원report/evidence와현재파일을검수했다. 이전manager.log의503/capacity종료와제출부재를확인했고기존자료를보존했다. A1~A5를지정범위에서승인한다. 현재2675파일/허용34변경, 양쪽460선택의459passed·권한1skip, 실제최종반환/수입check와역사·보존경계를대조했다. P06/P10과022 F5중개정네이름만닫으며skip/다른의미/최종G는남는다. 다음024는P09/P11조건·대기와F5의입력초과/운영처분정확문장을공유helper·소비검사경계로묶는다. 같은doc_code/engine_context·미러/캐시와공식검사를한담당자가소유한다. 기존packet/현재소스가유한한종료질문을제공해별도독립조사의실익이없으며병렬구현은공유쓰기가충돌한다. task는gpt-6.1-sol/high로명시하고manager설정은유지한다. 이번은work검수이며G4~G8등이남아next:null을제출하지않는다. 원task891파일·32검수제품·이전로그를보존하고정확파일과하나의기억노드를커밋해관리마감하며push하지않는다.',
 reports=[dict(task='document-governance',state='read',detail='report전문을읽고형식검사및원자료/현재파일대조를통과했다. A1~A5의완료를승인하며전체N/PR24/최종G합격으로확대하지않는다. 초기task실패와manager검산문자열오류의원자료도보존한다.',evidence=[taskref,base+'report-check.json',*ev,base+'return-check.json'])],
 dispositions=[
 dict(item='023/document-governance/F1',action='resolve',destination=['run:context.md#C10'],reason='실제payload/check·현재헌장/학술조회/최종입력과손상반례를대조해P06/P10지정남김을종결한다. runtime/권한의미는불변이다.',evidence=[*ev,base+'return-check.json']),
 dict(item='023/document-governance/F2',action='resolve',destination=['run:context.md#C9'],reason='B111/B113관련hunk와7원보고·PURE4원보고SHA/기존단언불변을확인해한정교체를승인한다. 다른PR/slice는유지한다.',evidence=[*ev,base+'history-check.json']),
 dict(item='023/document-governance/F3',action='resolve',destination=['run:context.md#C10','run:plan.md',objective+'#A4'],reason='022 F5의개정네이름만현재소비/기존검사와새두반례로종결한다. 나머지입력초과/운영처분정확문장은024로넘기며다른N/P08/L01은유지한다.',evidence=[*ev,'run:phases/023/tasks/document-governance/evidence/section-name-decisions.json']),
 dict(item='023/document-governance/F4',action='carry',destination=['run:context.md#C11','run:plan.md'],reason='Windows1314조건으로실제symlink탈출반려는미검사다. G4최종기본전체에서원문상환경조건정당성을판정하며passed로세지않는다.',evidence=ev),
 dict(item='023/document-governance/F5',action='carry',destination=['run:context.md#C12','run:plan.md',objective+'#A5'],reason='현재불변경계의승인성질만재사용하며원바이트/정확32제품을관리마감한다. G4전체/G5freshT3/G6전수변이/G7최종판연결/G8review는별도후속책임이다.',evidence=[*ev,'run:phases/023/tasks/document-governance/evidence/preservation.json'])],
 context_updates=[dict(item=cid,action='amend',destination=['run:context.md#'+cid],reason=reason,evidence=ev) for cid,reason in [
 ('C2','023완료범위와현재소스/원결과대조를추가하고역사실패를유지했다.'),('C5','023종료및024공유수정묶음·단일담당/병렬비배정이유를반영했다.'),('C7','사용자승인재시작의실제상태와원로그/완료task보존·별도로그를추가했다.'),('C8','024에도지정task모델/effort를명시하고manager정책유지를기록했다.'),('C9','P06/P10의B111/B113한정교체와PURE근거보존을추가했다.'),('C10','P06/P10·개정네이름을닫고F5의정확나머지문장을024에연결했다. 다른N/L01은보존했다.'),('C11','023권한skip과G4최종환경판정책임을추가했다.'),('C12','불변경계재사용·원task/이전로그/32제품인도및로컬보관한계를기록했다.')]],
 plan_update='즉시배정을023에서024 P09/P11의두owner와022 F5의입력초과/운영처분정확문장으로전환했다. 공유helper·소비·문서순회·미러/검사를통합하고관련선택은변경영향으로정한다. P08/TRUST·다른N/L01·권한skip·전체관문/review는유지하며완료task를재실행하지않는다.',seam_updates=[],completion=None)
save(RUN/'phases/023/manager.pending.json',manager)
assert 'convention_version: 27' in (R/'기억/세칙.md').read_text(encoding='utf-8')
assert sorted((R/'기억/layer1').glob('M-*.md'))[-1].name=='M-0572.md'
text(R/'기억/layer1/M-0573.md','''---
id: M-0573
layer: 1
title: 중단된 manager를 복구해 수입과 현재 조회 검수를 마감함
convention_version: 27
---

## 맥락

023의 작업자는 완료했지만 manager가503/model capacity 오류로 제출 전에 종료됐다. 사용자는 완료 task를 다시 실행하지 말고 원보고·현재 파일을 대조하라고 지시했다. 재시작에서는 manager.json뿐 아니라 pending과 관리 자료의 실제 존재 여부를 확인했다. 이전 manager.log 외 관리 산출물은 없었으며 기존 로그와 원task891파일을 보존했다. 같은 phase를 실행기에 다시 주면 완료 작업과 로그를 덮을 수 있으므로 다음 phase는 새024로 배정했다.

## 판단에 남길 조건

023의 첫 통합 검사는 제품이 아니라 원반환 관찰자의 action.role 가정 때문에 세 오류가 났다. 실제 입력에는 그 키가 없는 유효한 경로가 있다. 작업자는 관찰자만 고쳐 현재 execution_profile.role을 읽었고, 제품/시험875개가 같은 c2/m의 각459통과와권한1skip을 새로 남겼다. manager는 원오류를 보존하며 두 판본과 정확 실패ID를 대조했다. 관찰자 오류를 제품 수리나 역사실패의 소급성공으로 기록하지 않는다. manager 자체 검산에서도 str(list)의따옴표표현을 원오류문으로 검색한 실수가 있었으며 원스크립트를남기고 실제details를join해교정했다.

P06/P10은 문서 필드의 AST 모양만 맞던 네 경계를 실제 입력·조회·최종 지급과 연결했다. import bundle과check, 독립검사승인과사용자권한, 최초원문과별도승인원문, 수학해결과학술후속을 구별한다. 개정네이름의 한정 판단은 닫지만 다른 N 문장 전체를 완료로 세지 않는다. 다음024는P09/P11과입력초과/운영처분의정확문장만같은helper·소비검사에묶는다. 문서번호마다 반복마감하는 대신 공유수정과최종관련검사를통합하며다른정책/신뢰의미까지한세션에확장하지않는다.

검수 진입점은 docs/do-math/continuous-development-2026-10-13/phases/023/manager.json과 manager-evidence/review.md·verification.json·return-check.json이다. 원task891파일·검수32제품원바이트·이전manager.log는 추적되는raw-evidence.zip과preservation.json에 보존한다. 압축만추적하는원반환/snapshot/scratch의원경로와재시작로그·행정수신은로컬보관으로정리때사라질수있다. 압축은복원지시가아니다. L01 외부결정과원문byte미충족·권한skip·전체일반/freshT3/전수변이/최종review는남고push하지않는다.
''')
index=R/'기억/색인.md'; s=index.read_text(encoding='utf-8'); assert '- M-0573 ' not in s
text(index,s.replace('## layer-1\n','## layer-1\n\n- M-0573 [중단된 manager를 복구해 수입과 현재 조회 검수를 마감함] -- 완료task/원로그 보존·32제품 검수, 관찰자 오류 구별과024 조건·대기 통합 배정\n',1))
text(O/'common-docs.diff',''.join(''.join(difflib.unified_diff(before[n].splitlines(True),(RUN/n).read_text(encoding='utf-8').splitlines(True),fromfile=n+' before 023 restart',tofile=n+' after 023 restart')) for n in before))
save(O/'common-after-sha.json',{n:sha(RUN/n) for n in before})
print(json.dumps(dict(next='024',writes=len(writes),products=32,memory='M-0573'),ensure_ascii=False))

"""Create manager review and next assignment; never modify product sources."""
from pathlib import Path
import difflib
import hashlib
import json
import subprocess

R=Path('C:/math'); RUN=R/'docs/do-math/continuous-development-2026-10-13'
O=Path(__file__).resolve().parent; E=RUN/'phases/020/tasks/document-tools/evidence'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,text): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(text,encoding='utf-8',newline='\n')
def save(p,obj): put(p,json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def ref(name): return 'run:phases/020/manager-evidence/'+name

v=read(O/'verification.json'); assert v['current_equal_final'] and v['task_files_unchanged']==171
history=[]
for entry in read(E/'history-verification.json'):
    for row in entry['reports']:
        assert sha(R/row['path'])==row['sha256']==row['expected_sha256']
        history.append({'id':entry['id'],'path':row['path'],'sha256':row['sha256']})
save(O/'history-check.json',{'reports':history,'count':len(history)})

review='''# phase 020 검수

P03의 지정 A1~A4를 승인한다. manager는 report 형식 검사 후 시작2675파일과019 검수본의 동일성, 종료와 현재의 전건 SHA, 허용26변경을 검산했다. 정본12·미러12·비용캐시2가 실제 changes와 writes에 대응한다. 최종 양쪽 같은200선택/고유row는 각199passed·Windows1314 symlink1skipped·exit0이며 각875Python과 실행 tree의 비캐시 전후 바이트가 같다. skip은 실제 탈출 반려 증거가 아니며 G4의 조건부 환경 판단에 남긴다.

현재 diff와 실제 생산/소비 코드를 대조했다. _context와 prepare_role_input/install_tools의 실제 산출에서 여섯 owner를 읽으며 goal_audit의 formal_verifier 참조는 정확 파일·SHA·크기를 확인한다. preview는 같은 formal_verifier의 하위 객체다. 설치 archive의 모든 member와 현재 source bytes, wrapper/command, schema/context, record_map 권한·snapshot과 limits를 대조한다. 수제 정상 입력으로 생산을 대신하지 않았다. configured·명령 지급은 모델/학술/Lean 실행 성공과 구별된다. 기존 console sibling 선택/부재 반려와 host/Lean의 승인된 실행 성질을 유지한다.

수리 전 여섯 subTest 반례와 초기 helper 정본 오류, maintenance를 map으로 가정한 실패를 보존했다. 각각의 정확 실패 ID는 최종 양쪽 passed에 대응한다. 실제 반환 후 필드 삭제·다른 명령/파일 차용·hash 변경·잘못된 archive와 일치 hash 쌍·참조 손상, 미설치 조건을 구별하는 단언을 확인했다. 일반 순회의 defer는 정확 owner에 한정되고 담당 method/문서 검사 호출의 존재 확인은 실제 결과 추론과 구별된다. P01/P02·B130~B134의 정상/반례와 기본 record_map 반환은 유지됐다.

B110~B114 actual diff와 현재 소비, 존재7원보고의 SHA를 대조해 P03 AST 조립 교체를 승인한다. 명시 owner·별칭·저장/입력 구별은 유지하며 다른 packet과 PR24 전체를 종결하지 않는다. runtime/실호출139입력·corpus144경로/150명시SHA·host8자료/도구5·baseline910/Git blob·고정runtime/T4 경계258개는 불변이다. 공식 생성/check1336·skill-only의 원출력/exit도 확인했다. 공통-실행 두 문장은 미래 일반 역할 prompt를 바꾸므로 과거 고정 smoke를 새 문서 읽기/준수 근거로 확대하지 않는다. 원task171파일은 검산 전후 불변이다.

021 document-review는 현재 doc_code에 남은 role_review/pending_findings와 review_research/review_sources 네 owner를 기존 context_for·검토 봉인/준비·고정 질문 물질화 시험에 연결한다. P04와 P05는 같은 DOC-RETURN-REVIEW 경계와 doc_code/defer 소비를 공유하고 기존 실제 시험이 있으므로 한 task에서 처리해 중복 문서 회귀/미러 생성을 줄인다. 두 제품 task로 나누면 검사 중 공유 helper와 미러/캐시가 변하므로 병렬 독립성이 없다. 서비스가 새 task 세션을 시작하며 manager가 제품을 수정하거나 직접 실행하지 않는다. L01 외부 결정·P06~P11/나머지N·남은 의미 검토와 최종 G4~G8은 유지한다.
'''
put(O/'review.md',review)

old={name:(RUN/name).read_text(encoding='utf-8-sig') for name in ('context.md','plan.md','seams.md')}
context=old['context.md']
def add_to_c(number,text):
    global context
    start=context.index('## '+number+' ')
    end=context.find('\n## C',start+1)
    if end<0: end=len(context)
    context=context[:end].rstrip()+'\n\n'+text+'\n\n'+context[end:].lstrip()
add_to_c('C2','phase 020 document-tools는 A1~A4 complete로 검수했다. 시작2675파일은019 검수본과 같고 종료/현재 전건 SHA가 일치한다. 허용26변경(정본12·미러12·비용캐시2), 최종 양쪽 동일200선택/고유row·199passed/1skipped/exit0와 각875Python 및 실행 전후를 대조했다. skip은 기존 symlink 권한1314이며 실제 탈출 반려 증거가 아니다. red6반례·초기helper 오류1·map 가정 실패1과 정확ID의 최종 해소를 확인했다. 원task171파일 불변과 실제 설치/참조/최종 입력 결속을 검수했으며 근거는 run:phases/020/manager-evidence/verification.json·review.md다. 지정 P03 완료이며 전체G 완료가 아니다.')
c5start=context.index('phase 001~019의 task 세션은 종료됐다.')
c5end=context.index('\n\n',c5start)
context=context[:c5start]+'phase 001~020의 task 세션은 종료됐다.021 document-review 단일 work가 P04 검토 자리와 P05 고정 질문/원자료의 네 owner를 실제 반환·봉인·물질화·최종 입력에 연결한다. 같은 DOC-RETURN-REVIEW 경계와 doc_code/defer 소비를 공유해 한 task로 묶으며 제품 task를 병행하지 않는다. P01~P03·B130~B134와 다른 owner를 유지하고 jobs1·전체worker3 이하·한 묶음씩을 따른다. runtime/runner/adapter/Job fixture·corpus·기존 연구와 실호출 입력은 고정한다. 범위 밖 결함은 반례로 반환하며 새 유료 공급자·예약·학술 호출은 배정하지 않는다.'+context[c5end:]
add_to_c('C8','020의 gpt-6.1-sol/high 수행을 검수했다.021 document-review도 같은 사용자 지정 model/effort로 배정하며 manager 설정·제품 공급자 실호출과 구별한다.')
add_to_c('C9','020은 B110~B114 중 P03 AST 조립을 실제 _context/설치/포장 검사로 교체한 판단을 승인했다. actual diff·현재 소비와 존재7원보고 SHA를 대조했고 기본 record_map 반환·명시 owner/별칭·저장/입력 구별을 유지한다. 역사 counts를 새 성공에 합산하지 않는다. PR24 전체와 P04~P11의 다른 slice는 미종결이다. 근거는 run:phases/020/tasks/document-tools/evidence/binding-review.md·history-verification.json 및 manager-evidence/history-check.json·review.md다.')
add_to_c('C10','020에서 P03 여섯 owner의 지정 남김을 닫았다. 실제 _context·build_profiles·prepare_role_input·install_tools 결과와 goal_audit 참조파일, 설치 wrapper/archive 전체member·schema/context·명령/해시/권한/limits를 대조했다. 미설치 preview·다른 명령/파일 차용·일치 hash의 잘못된 archive·참조 손상과 소유자별 defer 반례를 확인했다. 기본 record_map 및 P01/P02·B130~B134는 유지한다. scholarly.configured와 preview 지급을 실호출/검증 성공으로 읽지 않는다. 근거는020 manager verification.json·review.md와 원task binding-review.md다.021은 P04/P05의 role_review·pending_findings·review_research·review_sources만 맡는다. 이 네 owner는 같은 검토 입력 경계와 공통 문서 순회를 공유하므로 한 task에서 닫는다. L01 Q1/Q2와 원문byte 요구·미충족, P06~P11/TRUST·N의 다른 절·최종 관문은 그대로 남는다.')
add_to_c('C11','020의 최종 양쪽200선택에서도 기존 ContextStoreTests.test_outside_symlink_is_reported_when_supported가 Windows1314로 각1skip됐다. P03 필수 설치/입력 성질은 전부 실행됐지만 실제 symlink 탈출 반려는 미검사다. G4 최종 기본전체에서 원문상 환경조건의 정당성을 판정하며 skip을 통과로 세지 않는다. 근거는020 manager verification.json과 c/m 원report다.')
add_to_c('C12','020 F2의 보존과 한정 재사용을 검수했다. runtime/실호출139입력·corpus144경로/150명시SHA/Gitraw-clean·host8자료/도구5·baseline910/Gitblob·고정runtime/T4 258경로는 불변이다. preview 문서 두 문장은 미래 일반 역할 prompt에 반영되므로 과거 고정 smoke는 승인된 성질만 재사용한다. 검수한24비캐시 제품경로를 이번 관리 커밋으로 마감한다. 원task171파일과 제품원바이트는 manager-evidence/raw-evidence.zip에 보존하며 전건SHA·선별 추적범위는 run:phases/020/manager-evidence/preservation.json에 둔다. 압축만 추적하는 원경로와 stage/commit 행정 수신은 로컬 보관으로 정리 때 사라질 수 있다. 압축은 복원 지시가 아니다.021 배정·관리·기억 추가는 제품 검증 판본을 바꾸지 않는다.')
put(RUN/'context.md',context)

plan=old['plan.md'].replace('## phase 001~019의 결과와 현재 상태','## phase 001~020의 결과와 현재 상태')
a=plan.index('## 다음 phase: 020'); b=plan.index('## 가까운 후속 배정',a)
plan=plan[:a]+'''020 P03의 A1~A4를 검수했다. 실제 설치/최종 입력·양쪽 동일200선택의199passed/권한1skip 및875Python 판본을 확인했다. P03 지정 남김을 닫고 symlink 실제 반려 미검사는 G4에 유지한다.24비캐시 제품경로를 관리 마감한다. 근거는020 manager verification.json·review.md다.

## 다음 phase: 021

gpt-6.1-sol/high의 document-review 단일 work를 배정한다. P04의 role_review/pending_findings와 P05의 review_research/review_sources를 실제 context_for·검토 봉인/준비·고정 질문/원자료 물질화와 최종 입력에 연결한다. 같은 검토 입력 경계와 doc_code/defer 소비를 공유하므로 한 task가 네 owner를 맡아 중복 문서 회귀·미러 생성을 줄인다. 현재 단계별 blindness·정확 ref·고정 snapshot/바이트·실제 복원 오류를 유지한다.

공통 helper·직접 소비·문서·미러·캐시를 같은 task가 소유한다. jobs1·한 묶음씩이며 runtime·runner·adapter·Job fixture·corpus·실호출 입력은 고정한다. 최종 같은 관련 선택을 양쪽에서 완결하고 공식 생성/check/skill-only를 확인한다. P01~P03·B130~B134와 다른 owner의 정상/음성 단언을 보존한다. 새 실호출이나 전체T4 반복은 배정하지 않는다.

019의28비캐시 제품경로는 HEAD'''+v['head'][:8]+'''의 관리 커밋으로 마감됐다. 이번에는020의24비캐시 제품경로를 커밋한다. L01 Q1/Q2는 미정이며 원문byte 기준과 미충족을 유지한다. P06~P11/TRUST·N의 다른 절·남은 의미 질문, 전체일반/freshT3/전수변이·최종review는 후속 책임이다.

'''+plan[b:]
plan=plan.replace('019의 P02 네owner를 닫았다.020이 P03 실행 안내/지급 도구를 맡고 P04~P11·N01~N03의 다른 미결 절은 후속으로 남긴다.', '019 P02와020 P03을 닫았다.021이 P04/P05 검토 입력 네owner를 맡고 P06~P11·N01~N03의 다른 미결 절은 후속으로 남긴다.')
plan=plan.replace('019 관련 양쪽의 Windows1314 skip','019~020 관련 양쪽의 Windows1314 skip')
put(RUN/'plan.md',plan)
put(RUN/'seams.md',old['seams.md'].rstrip()+'''\n\n020의 P03 실제 설치/최종 입력 결속을 검수했다.021은 기존 review_cycle.context_for/accept_result·ReviewEngineMixin의 검토 준비/봉인/고정 조사/원자료 물질화 경계를 소비한다. stage별 가시성·정확 ref·proposal/request digest·고정 snapshot/복원 오류는 기존 코드/공유 계약이 정본이며 새 의미를 만들지 않는다. P04/P05 네 owner와 helper·직접 소비·미러를 한 task가 소유하므로 S항목·provides/uses는 추가하지 않는다. runtime나 권한 계약 개정은 범위 밖 반례로 반환한다.\n''')

base='.claude/skills/do-math/'
files=['scripts/tests/support/doc_code.py','scripts/tests/support/engine_context.py','scripts/tests/structure/test_doc_code.py',
 'scripts/tests/unit/test_review_cycle_stages.py','scripts/tests/unit/test_review_research_owner_contract.py',
 'scripts/tests/unit/test_review_research_slots.py','scripts/tests/sim/test_submission_review_inputs.py',
 'scripts/tests/sim/test_review_research_replay_evidence.py','scripts/tests/flows/test_review_research_flows.py',
 'scripts/tests/boundary/test_review_source_restoration.py','scripts/tests/support/review_inputs.py',
 'scripts/tests/support/review_research.py','scripts/tests/support/review_scene.py',
 'scripts/tests/sim/test_role_input_context.py','scripts/tests/unit/test_role_input_packaging.py',
 'scripts/tests/boundary/test_engine_cli.py','scripts/tests/unit/test_engine_trace_report_corruption.py',
 'scripts/tests/unit/test_storage_record_queries.py','scripts/tests/unit/test_storage_report_projections.py',
 'scripts/tests/unit/test_submission_preview_commands.py','scripts/tests/sim/test_knowledge_project_identity.py',
 'references/CLI-실행-계약.md','references/공통-실행.md','계약/동일성-검토.md','계약/보충-조사.md',
 'scripts/tests/.timings.json','scripts/tests/.timings-t3.json']
writes=[prefix+f for prefix in (base,base.replace('.claude/','.agents/')) for f in files]
assert all((R/p).exists() for p in writes)
inputs=['run:sources/user-decisions.md','run:sources/model-policy-2026-10-14.md',
 'run:phases/001/tasks/document-closeout/report.json',
 'run:phases/001/tasks/document-closeout/evidence/followup-packets.json',
 'run:phases/001/tasks/document-closeout/evidence/binding-inventory.json',
 'run:phases/001/tasks/closure-map/evidence/prior-review-state.json',
 'run:phases/020/tasks/document-tools/report.json','run:phases/020/tasks/document-tools/evidence/binding-review.md',
 'run:phases/020/tasks/document-tools/evidence/preservation.json',
 ref('verification.json'),ref('review.md'),ref('source-inspected.json'),
 'repo:docs/do-math/시험-재편-2026-09-29/설계.md','repo:docs/do-math/시험-재편-2026-09-29/조사/결함-범주.md',
 'repo:'+base+'AGENTS.md','repo:'+base+'scripts/tests/시험-지침.md','repo:'+base+'scripts/이음새-정본.md',
 'repo:.claude/skills/writing-skills/references/멀티런타임_동기화.md']
inputs+=['repo:'+base+f for f in ['references/CLI-실행-계약.md','references/공통-실행.md','계약/동일성-검토.md','계약/보충-조사.md',
 'scripts/do_math/review_cycle.py','scripts/do_math/review_engine.py','scripts/do_math/core_engine.py',
 'scripts/do_math/context_store.py','scripts/tests/support/doc_code.py','scripts/tests/support/engine_context.py',
 'scripts/tests/unit/test_review_cycle_stages.py','scripts/tests/unit/test_review_research_owner_contract.py',
 'scripts/tests/boundary/test_review_source_restoration.py','scripts/tests/sim/test_submission_review_inputs.py']]
P=RUN/'phases/021'; assert not P.exists()
(P/'logs').mkdir(parents=True); (P/'tasks/document-review/evidence').mkdir(parents=True)
save(P/'phase.json',{'kind':'work','purpose':'P04/P05 검토 자리·고정 질문과 원자료의 문서 필드를 실제 단계별 반환·봉인·물질화 입력에 연결한다.',
 'tasks':[{'id':'document-review','model':'gpt-6.1-sol','effort':'high','inputs':inputs,'writes':writes,'provides':[],'uses':[]}]})
objective='''## 목적과 역할

G1/G3의 DOC-RETURN-REVIEW 중 P04/P05 네 owner(role_review, pending_findings, review_research, review_sources)를 닫는다. 현재 doc_code는 context_for/_add_findings/_review_research_context의 AST와 물질화 함수의 소비 키, identity_basis/policy_ref의 수동 조립을 반환 증거로 사용한다. 이를 기존 실제 검토 단계·봉인·고정 질문/원자료 시험에 연결한다. 같은 helper/defer·최종 역할 입력을 공유하는 범위이므로 한 task가 두 packet을 함께 맡는다. 다른 owner나 전체 검토 체계 재설계로 범위를 늘리지 않는다.

020 P03은 검수됐고 양쪽200선택은199passed·기존 symlink권한1skip이다. P01~P03·B130~B134의 실제 생산/소비·설치와 정상/반례를 유지한다. 분석·AST 제거 수나 새 검사 수는 완료 기준이 아니다.

## 완료 조건

### A1 현재 문서와 실제 검토 입력의 경계 확정

시작 skills/diff를020 manager source-inspected2675파일과 대조하고 차이의 출처를 구별한다. followup-packets의 P04/P05와 결함-범주13-C의 지정 원문을 현재 문서 위치/별칭에 연결한다. role_review.proposal·pending_findings[].ref와 review_research.question/id/request_digest/proposal_digest/sources, 보충-조사의 sources=review_sources를 각각 실제 생산/최종 소비 객체에 대응시킨다. packet의 과거 행 번호는 현재 제목과 코드로 확인한다.

context_for 결과와 _prepare_review_context·_context·prepare_role_input의 최종 전달 관계, 비공개 동료 판단과 봉인 결과, 고정 조사 요청과 일반 research_sources를 구별한다. B110~B114의 이 네 owner 관련 actual diff·현재 소비·존재 원보고만 대조해 유지/교체/제거 판단을 남긴다. P01~P03의 완료와 PR24 다른 slice를 다시 전수 조사하지 않는다.

### A2 실제 반환과 최종 입력·원자료 바이트에 결속

기존 ReviewCycleTests의 scope/initial·organize/answer/judge 경로와 ReviewScene/ResearchOwnerContractTests·검토 입력 포장 시험을 재사용한다. 실제 context_for의 proposal·해당 조건에서 존재하는 identity_basis/policy_ref·pending_findings를 최종 role_review에 연결하고 proposal 전문 중복 방지·원래 blindness/봉인·정확 finding ref/answer 담당을 유지한다. 빈 pending_findings는 원소 ref 존재의 양성 증거가 아니므로 실제 열린 finding의 비어 있지 않은 표본을 포함한다.

실제 _review_research_context와 _materialize_research_sources에서 request의 id/digest/question/proposal_digest와 sources ref/local_path/SHA/bytes/snapshot을 대조한다. 일반 발행 뒤에도 고정 snapshot의 정확 바이트를 읽고 input/review-research 파일이 그 원자료에 대응함을 확인한다. inline과 artifact 조건, 최종 포장에서 참조가 되면 정확 파일을 읽는 책임을 명시한다. boundary.test_review_source_restoration의 실제 Git 정상/복원 실패를 포함해 실제 저장과 대역의 범위를 구별한다. 생산·포장·물질화 함수를 대역으로 가리거나 수제 정상 반환을 복제하지 않는다.

### A3 누락·교차 소유·단계 가시성과 실패 보존

수리 전 실제 문서 검사 공백의 red를 남기고 같은 성질의 green을 연결한다. 반환 후 사본에서 proposal/ref/question/digest/local_path 등 현재 문서가 요구하는 필드를 삭제하면 반려해야 한다. 다른 stage/slot/record의 finding ref, 일반 research_sources의 키·다른 원자료의 경로/같은 바이트 차용도 정확 소유 관계로 구별한다. 기존 동료 미봉인 판단 비노출·잘못된 proposal/request/원자료 바이트 반려·파일 부재/손상과 좌표 있는 ReviewRestorationError를 유지한다. 반환 사본 반례와 실제 제품의 손상 반려를 구별한다.

일반 순회가 실제 담당에 위임하면 네 owner별 담당 method와 실제 문서 검사 호출/실행을 명시하고 defer 오기·담당 누락·다른 owner 동시 건너뜀 반례를 유지한다. 마지막 소비가 없어진 해당 AST/소비키 조립만 제거하고 범용 추론기·전역 등록부는 추가하지 않는다. 빈 배열/조건부 부재는 양성 표본으로 쓰지 않는다. P01~P03·B130~B134 및 다른 owner의 음성 단언을 보존한다.

### A4 관련 회귀와 인도 근거

아래 관련 선택을 최종 정본/미러에서 같은 ID 집합으로 완결하고 선택/고유row/실제exit·실행 전후 판본을 남긴다. 허용 범위의 공식 생성·마지막 캐시 동기화·--check·skill-only를 통과한다. 조건부 환경 skip은 통과로 세지 않고 원인·영향 성질·G4 후속을 기록한다. 이 task 필수 성질 미실행은 해당 A의 pass가 아니다.

020 preservation의 runtime/실호출139입력·corpus144경로/150명시SHA·host8자료/도구5·baseline910 및 runtime/T4 고정 경계를 보존한다. 문서 수정의 미래 prompt 영향과 역사 고정 실호출의 한정 재사용을 구별한다. P06~P11/TRUST·N의 다른 절·L01 Q1/Q2와 G4~G6/G8은 후속 책임이다.

## 판단과 경계

writes의 지정 시험/helper·문서와 미러/캐시만 수정한다. 작은 공통 assertion과 시험 배치는 재량이며 모든 허용 파일을 수정할 의무는 없다. runtime/review_cycle/review_engine/core_engine/context_store·runner·adapter·Job fixture·corpus·설치 신뢰·공유 설정·공용 문서·기존 연구는 고정한다. 문서 검사 편의를 위해 제품 API·검토 가시성·권한·원 schema를 바꾸지 않는다. 범위 밖 결함은 최소 반례·필요 파일·영향 A와 다음 조치로 반환한다. 권한판단이나 L01 요구 개정은 이 task의 재량이 아니다.

전체worker3 이하·jobs1·한 묶음씩, 검사 중 소스 고정이다. parent TEMP/TMP/TMPDIR는 저장소 밖 짧은 전용 경로를 쓰고 git rev-parse가 상위 저장소를 찾지 않는지 확인한다. resource output과 최종cwd도 짧게 유지한다. 시간은 소프트 기준이며 단언을 약화하지 않는다. 새 유료 공급자·예약·학술 호출, 기존 연구 운전/삭제, graphify 갱신, Git stage/commit/reset/checkout/push는 배정하지 않는다.

## 검증 방법

cwd C:\\math, Python C:\\Users\\wogud\\AppData\\Local\\Programs\\Python\\Python312\\python.exe. 공식 run_tests.py에 -u -B·--jobs 1·--output <자기 evidence의 짧은 새 경로>를 사용한다. argv/cwd/환경·PID/시각·종료·stdout/stderr·소스 SHA를 보존하고 진행 result.json은 read_bytes_shared로 읽는다.

1. A1의 현재 생산/소비와 담당을 확인하고 A3 반례를 수리 전 실행한다. 기존 정상/오류 단언을 수정 전에 대조한다.
2. 직접 검토 경계는 unit.test_review_cycle_stages unit.test_review_research_owner_contract unit.test_review_research_slots sim.test_submission_review_inputs sim.test_review_research_replay_evidence flows.test_review_research_flows boundary.test_review_source_restoration이다. 정확 method와 경로를 현재 파일로 확인하며 새 장기 흐름을 만들기보다 기존 표본에 단언을 연결한다.
3. 공유 문서/입력 회귀는 structure.test_doc_code sim.test_role_input_context unit.test_submission_preview_commands sim.test_knowledge_project_identity unit.test_role_input_packaging unit.test_role_input_scoped_packaging unit.test_preflight unit.test_context_catalog sim.test_submission_receiver flows.test_submission_acceptance unit.test_storage_report_projections unit.test_engine_trace_report_corruption unit.test_storage_record_queries boundary.test_engine_cli sim.test_knowledge_currentness.RecoveryMaterialTests flows.test_knowledge_impact_retry.UnreadableBeforeReviewTests다. 2/3의 중복을 제거해 한 묶음 또는 순차 묶음으로 실행한다. 목록 밖 직접 소비 오류가 확인되면 정확ID를 추가 검증하고 writes 밖 수리는 manager에 반환한다.
4. 공식 생성 계획의 범위 확인 후 미러를 생성하고 미러 run_tests.py로 같은 최종 선택을 실행한다. 마지막 캐시 동기화 뒤 build_skill_mirrors.py --check와 probe_cli.py --skill-only를 통과한다. 성공 검사를 이유 없이 반복하지 않으며 전체일반/freshT3/전수변이·전체T4·새T5는 배정하지 않는다.
5. 지정 Python으로 services/continuous-development/check.py report C:\\math C:\\math\\docs\\do-math\\continuous-development-2026-10-13 021 document-review를 통과한다. report에 A1~A4·실제 changes·네 owner별 담당과 정상/반례·역사 근거 재사용·미검사 범위를 기록한다. 마지막 응답은 상태와 report 경로다.
'''
put(P/'tasks/document-review/objective.md',objective)

updates=[]
for item,reason in [('C2','020 지정완료와 실제 검산 범위·역사실패/skip을 추가했다.'),('C5','종료020 이후021의 네owner 단일소유·실행자원과 고정 경계를 지정했다.'),('C8','사용자 지정 gpt-6.1-sol/high를021에도 유지했다.'),('C9','B110~B114 P03 slice의 실제교체/유지 판단을 기록하고 PR24 전체 미종결을 보존했다.'),('C10','P03 여섯owner를 닫고 같은 검토 입력 경계의 P04/P05를021에 묶었다. 다른packet/L01 외부결정은 유지했다.'),('C11','020의 기존권한skip을 실제탈출 반려 미검사로 유지했다.'),('C12','불변 경계의 한정 재사용과24제품 마감·원바이트 보존/로컬 한계를 기록했다.')]:
    updates.append({'item':item,'action':'amend','destination':['run:context.md#'+item], 'reason':reason,'evidence':[ref('verification.json'),ref('review.md'),'run:phases/021/tasks/document-review/objective.md']})
manager={'next':'021','decision':'P03 document-tools의 A1~A4 complete를 승인한다. report 형식 검사를 통과했고 현재2675소스·허용26변경·공식 선택/row/실제exit·875Python 판본과 원바이트 보존을 직접 검산했다. 최종 양쪽200건은199passed/권한1skip이며 skip은 통과나 실제탈출 반려 근거가 아니다. red6반례와 두 초기오류의 정확ID 해소를 확인했다. 실제 설치/최종 입력과 지급 명령의 검사 범위를 승인하되 외부 호출 성공으로 확대하지 않는다.\n\n다음021 work는 P04/P05 네owner를 실제 단계별 검토/봉인·고정 질문/원자료 반환에 연결한다. 같은 doc_code/defer와 최종 입력 경계를 공유하며 기존 시험이 있으므로 한 task에서 처리한다. 두 task로 나누면 상대의 변경 중 helper·미러·캐시에 검증이 의존해 독립성이 없다. 지정24비캐시 제품과 관리기록·한 기억노드를 이번 커밋으로 마감한다. 기존 무관 변경은 포함하지 않는다.\n\n공용 G/권한/제품 seam은 바꾸지 않았다. L01의 운전프로필·출력단위 결정, P06~P11/TRUST·N의 다른 절·남은 의미 검토와 최종 전체일반/freshT3/전수변이·최종review가 남아 개발 완료 조건이 아니다. next:null을 제출하지 않는다.',
 'reports':[{'task':'document-tools','state':'read','detail':'report 전문과 A1~A4·모든 checks/findings를 읽고 형식검사를 통과했다. 171원파일 불변·2675현재소스/종료일치와 최종 양쪽 동일200선택/199passed·권한1skip/exit0를 검산해 지정완료를 승인한다. 초기실패와 미검사 한계는 보존한다.','evidence':['run:phases/020/tasks/document-tools/report.json',ref('report-check.json'),ref('verification.json'),ref('review.md')]}],
 'dispositions':[
 {'item':'020/document-tools/F1','action':'resolve','destination':['run:context.md#C9','run:context.md#C10'],'reason':'actual diff·현재 소비·7원보고 SHA와 실제 설치/문서 검사로 P03 slice 교체를 승인한다. 기본record_map·명시owner/별칭/다른packet 보존을 확인했고 PR24 전체로 확대하지 않는다.','evidence':[ref('history-check.json'),ref('review.md'),'run:phases/020/tasks/document-tools/evidence/B110-p03.diff']},
 {'item':'020/document-tools/F2','action':'resolve','destination':['run:context.md#C12'],'reason':'실호출/runtime·corpus·host·도구·baseline/T4 경계의 불변과 실제Gitclean을 검산했다. 승인된 고정입력 성질만 재사용하고 미래preview 문구의 읽기/준수는 주장하지 않는다.24비캐시제품 마감·압축원바이트 보존을 지정했다.','evidence':[ref('verification.json'),ref('review.md'),'run:phases/020/tasks/document-tools/evidence/preservation.json']},
 {'item':'020/document-tools/F3','action':'carry','destination':['run:context.md#C11','run:plan.md'],'reason':'양쪽 정확symlink ID가 Windows1314로skip이며 P03필수 성질은 전부 실행됐다. 권한/요구는 바꾸지 않고 G4 최종전체에서 원문상 환경조건과 실제반려 미검사를 별도판정한다.','evidence':[ref('verification.json'),'run:phases/020/tasks/document-tools/evidence/c/report.json','run:phases/020/tasks/document-tools/evidence/m/report.json']}],
 'context_updates':updates,'plan_update':'020 P03 지정남김을 닫고021 P04/P05 네owner를 한 task에 결합했다. 현재검토 경계/공통helper·미러·캐시 때문에 제품 병렬작업은 두지 않는다. 권한skip과 L01 외부결정·다른packet/의미질문·최종관문은 유지했다. 공용 diff에서 G1~G8 원문 불변과 기존 조건/이력 보존을 확인한다.','seam_updates':[],'completion':None}
save(RUN/'phases/020/manager.pending.json',manager)
diff=''
for name,before in old.items():
    after=(RUN/name).read_text(encoding='utf-8')
    if name=='context.md': assert before.split('## C2 ')[0]==after.split('## C2 ')[0]
    diff+=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile=name+' before 020',tofile=name+' after 020'))
put(O/'common-docs.diff',diff)
save(O/'common-before-sha.json',{n:hashlib.sha256(t.encode()).hexdigest() for n,t in old.items()})
print('Prepared review, current context/plan/seams, phase 021 and manager.pending.json.')

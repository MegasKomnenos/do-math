"""Prepare the manager's evidence disposition and the bounded next assignment."""
import difflib
import json
from pathlib import Path
import subprocess

R=Path('C:/math'); RUN=R/'docs/do-math/continuous-development-2026-10-13'
P=RUN/'phases/018'; O=P/'manager-evidence'; N=RUN/'phases/019'
def write(path,text): path.write_text(text,encoding='utf-8',newline='\n')
def save(path,value): write(path,json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def ref(path): return 'run:phases/018/manager-evidence/'+path
T='run:phases/018/tasks/job-cleanup/'
v=json.loads((O/'verification.json').read_text(encoding='utf-8'))
assert v['source_matches_task'] and all(x['exit_code']==0 for x in v['suites'])
assert not N.exists()
(N/'tasks/document-results/evidence').mkdir(parents=True)
(N/'logs').mkdir()

test_paths=['support/doc_code.py','support/engine_context.py','structure/test_doc_code.py',
 'sim/test_role_input_context.py','unit/test_context_catalog.py','sim/test_submission_receiver.py',
 'flows/test_submission_acceptance.py','flows/test_knowledge_impact_retry.py','boundary/test_engine_cli.py',
 'unit/test_storage_report_projections.py','unit/test_engine_trace_report_corruption.py',
 'unit/test_storage_record_queries.py','unit/test_role_input_packaging.py','unit/test_preflight.py',
 'sim/test_knowledge_currentness.py']
documents=['references/CLI-실행-계약.md','references/공통-실행.md','references/지식-저작과-재사용.md']
relative=['scripts/tests/'+p for p in test_paths]+documents+['scripts/tests/.timings.json','scripts/tests/.timings-t3.json']
writes=[tree+'/skills/do-math/'+p for tree in ('.claude','.agents') for p in relative]
assert all((R/p).is_file() for p in writes)
inputs=['run:sources/user-decisions.md','run:sources/model-policy-2026-10-14.md',
 'run:phases/001/tasks/document-closeout/report.json',
 'run:phases/001/tasks/document-closeout/evidence/followup-packets.json',
 'run:phases/001/tasks/document-closeout/evidence/binding-inventory.json',
 'run:phases/001/tasks/closure-map/evidence/prior-review-state.json',
 'run:phases/008/tasks/document-recovery/report.json',
 'run:phases/008/tasks/document-recovery/evidence/binding-review.md',
 'run:phases/009/manager-evidence/verification.json',
 'run:phases/018/manager-evidence/verification.json',
 'run:phases/018/manager-evidence/review.md',
 'run:phases/018/manager-evidence/source-inspected.json',
 'repo:docs/do-math/시험-재편-2026-09-29/설계.md',
 'repo:docs/do-math/시험-재편-2026-09-29/조사/결함-범주.md',
 'repo:.claude/skills/do-math/AGENTS.md',
 'repo:.claude/skills/do-math/scripts/tests/시험-지침.md',
 'repo:.claude/skills/do-math/scripts/이음새-정본.md',
 'repo:.claude/skills/writing-skills/references/멀티런타임_동기화.md']
inputs+=['repo:.claude/skills/do-math/'+p for p in documents]
inputs+=['repo:.claude/skills/do-math/scripts/'+p for p in ['do_math/context_store.py','do_math/core_engine.py',
 'do_math/contracts.py','tests/support/doc_code.py','tests/support/engine_context.py','tests/structure/test_doc_code.py',
 'tests/sim/test_role_input_context.py','tests/unit/test_context_catalog.py','tests/sim/test_submission_receiver.py',
 'tests/flows/test_submission_acceptance.py']]
save(N/'phase.json',{'kind':'work','purpose':'P02의 원자료·과제 결과·복원 파일 문서 결속을 실제 생산·저장·역할 입력과 연결하고 관련 회귀를 검증한다.',
 'tasks':[{'id':'document-results','model':'gpt-6.1-sol','effort':'high','inputs':inputs,'writes':writes,'provides':[],'uses':[]}]})
write(N/'tasks/document-results/objective.md','''## 목적과 역할

G1/G3의 문서 결속 중 phase 001 followup-packets의 P02를 닫는다. 원자료·과제 결과·복원 파일의 문서 필드가 실제 생산·저장·역할 입력을 검사하도록 기존 시험을 연결한다. 현재 doc_code.field_schemas는 source_ref, materialized_output_files, research_sources, results를 AST와 문자열 bindings로 구성한다. 이 추정만으로는 최종 입력의 누락·다른 실행의 파일 차용을 알 수 없다. 018에서 T4의 지정 오류는 양쪽 전체295passed로 종결됐으며 이 작업은 그 정본을 보존한다.

긴 JSON은 P02와 해당 소유자의 binding 항목만 선택한다. 원문은 결함-범주.md의13-C 및 P02가 가리키는1181/1184/1201/1600/1613행 주변을 현재 제목으로 확인한다. 역사 행 번호/AST 위치가 현재와 달라질 수 있다. P02의 소유자 네 개가 범위이며 현재341행의 review_sources는 별도 REVIEW 경계다. P01 운영/복구와 B132~B134·일반 재개의 완료 성질은 재사용한다.

## 완료 조건

### A1 문서·생산·소비와 기존 근거의 범위 확정

시작 skills/diff 해시를018 manager source-inspected2675파일과 대조하고 차이의 출처/영향을 기록한다. 기존 dirty·운영자 설정·관리 커밋을 제품 변화와 구별한다. P02의 source_ref, materialized_output_files, research_sources, results가 현재 세 문서에서 실제로 소비되는 위치·조건·별칭을 write_source_catalog, _preserve_outputs, _apply, _context, prepare_role_input 및 해당 시험에 연결한다. AST 전체를 조사하거나 다른 소유자를 이 작업으로 끌어오지 않는다.

저장된 output_files의 artifact 참조와 이번 workspace에 복원한 local_path, 수제 task.results fixture와 실제 _apply 생산 결과를 구별한다. 현 생산 출력의 보존 필터가 knowledge/relations/integration_bundles를 결과에 중복 저장하지 않는 성질을 실제 소비·기존 수신/acceptance 시험과 연결한다. 원래 문서 결속 B110~B114의 해당 P02 slice만 현재 diff/소비와001의 분석 근거로 유지·교체·제거 판단한다. PR24 전체나 없는 과거 원보고 counts를 검토 완료로 세지 않는다.

### A2 실제 반환·저장 파일을 사용하는 문서 결속

위 네 소유자의 AST/문자열 조립을 현재 실제 반환이나 이미 존재하는 공유 계약과 실제 경계 검사에 연결한다. 기존 ContextStoreTests·PackagedInputTests 및 실제 _apply를 지나는 수신/흐름 시험을 재사용한다. production 내부를 대역으로 가리거나 최종 반환을 손으로 베껴 정상 표본으로 만들지 않는다. 테스트 대역은 기존 외부 포트 경계에 둔다.

write_source_catalog의 실제 쓴 정규 JSON 바이트와 source_ref.path/sha256/bytes·total, _context의 sources/local_path, task.results의 report와 각 output_files/local_path를 해당 workspace·원artifact·snapshot·해시·크기에 결속한다. 큰 catalog의 source_ref와 목록/행의 참조를 실제 파일에서 회수해 검사하고, 일반 입력과 포장된 최종 입력의 조건을 구별한다. _apply의 보고/출력 보존과 독립 knowledge bundle 비중복 성질은 기존 sim.test_submission_receiver와 flows.test_submission_acceptance의600k 보고/파일·개정/재개 경로를 사용한다. 물질화만 확인한 수제 result로 실제 생산을 증명했다고 쓰지 않는다. 새 장기 엔진 시나리오를 중복 구축하지 않는다.

문서에서 결과를 읽는 권한과 과제 선택 모집단이 다르다는 의무, 과거 artifact와 local_path 구별, 읽기 실패를 빈 목록으로 바꾸지 않는 설명을 유지한다. 필요한 문장/별칭 교정만 허용된 세 문서에 반영한다. 현 runtime 계약을 문서 검사 편의를 위해 바꾸지 않는다.

### A3 누락·잘못된 소유자·빈 입력 반례와 담당 연결

실제 반환 후 사본 교란으로 report 또는 한 파일 local_path 삭제, 다른 실행/원자료의 local_path 차용, 잘못된 해시/크기, 문서 필드 오기·동명 다른 owner의 필드를 검사기가 거부함을 확인한다. 실제 제품의 손상 입력 반려는 정확 사유와 별도로 검증한다. 정상 빈 배열·조건부 부재는 계약대로 처리하되 원소의 필드 검증을 빈 배열 하나로 대신하지 않는다. 저장 execution에 local_path를 붙여 복원 경로를 대신하는 경우가 정상 증거로 들어가지 않아야 한다.

현재 공백을 드러내는 구체적 새 단언을 수리 전 실행해 red를 보존하고 같은 성질의 green을 연결한다. 이미 충분한 성질은 기존 근거를 재사용한다. field_schemas/scoped_field_issues의 일반 순회에서 실제 객체 담당에게 넘길 때 owner별 담당 시험과 문서 검사를 명시하고, 잘못된 defer 이름·누락된 담당·다른 owner의 동시 건너뜀을 거부한다. 기존 P01·B130~B134 등의 defer/음성 단언은 유지한다. 새 전역 등록부나 범용 AST 추론기를 요구하지 않는다. 마지막 소비자가 남은 AST helper는 유지하고, 이 작업 때문에 소비가 사라진 부분만 제거한다.

### A4 관련 회귀·미러·보존과 인계

아래 직접/공유 소비 검사를 최종 판본에서 완료하고 선택·고유 실제 row·exit·소스 전후를 보존한다. 공식 미러의 예상 변경이 writes 안인지 확인한 뒤 생성한다. 같은 관련 검사를 미러에서도 실행하고 --check 및 skill-only를 통과한다. 캐시는 성공의 근거가 아니다. runtime139입력·corpus144경로/150명시SHA·host8원자료/도구·과거baseline910과018 T4 제품 경계를 보존하고 기존 승인된 실호출의 재사용 영향을 판정한다. 문서 변경이 향후 역할 prompt 판본에 미치는 영향도 기록한다.

완료는 P02의 지정 문서 결속에 한정한다. P03 실행 안내/설치 도구, REVIEW/TRUST·나머지 P/N, L01 외부 결정과 G4~G6/G8은 남긴다. 전체 T4를 이번 문서 검사 변경만으로 반복할 의무는 없으며 runner/adapter/Job fixture는 수정하지 않는다. 범위 밖 runtime 결함이 발견되면 재현·필요 파일·영향 A와 후속 책임을 보고한다.

## 판단과 경계

writes는 doc_code·기존 engine_context helper, 직접 생산/수신 시험과 현재 문서 검사 소비자, 세 문서와 대응 미러/캐시다. 나열된 모든 파일을 고치라는 뜻은 아니며 소비자 변경은 이 네 owner의 실제 담당 연결에 한정한다. 테스트 helper의 작은 공통 함수와 구체적 배치는 재량이다. runtime/core_engine/context_store/contract·서버·공유 설정·runner·corpus·공용 context/plan·다른 phase·engine·기억을 고치지 않는다. 실제 인터페이스 개정이 필요하면 다음 manager에 정확히 반환한다.

공유 doc_code와 미러/캐시를 단일 task가 소유하므로 다른 제품 작업과 병행하지 않는다. 전체worker3 이하, jobs1, 한 묶음씩이며 검사 중 제품·시험 판본을 고정한다. parent TEMP/TMP/TMPDIR는 저장소 밖 짧은 전용 경로로 하고 resource output도 짧게 둔다. 시간 예산은 소프트 기준이고 yield/대기 만료는 시험 실패가 아니다. 새 유료 호출·예약 변경·학술 호출·설치 신뢰 변경·기존 연구 운전/삭제·graphify 갱신·Git stage/commit/reset/checkout/push는 수행하지 않는다.

## 검증 방법

cwd C:\\math, Python C:\\Users\\wogud\\AppData\\Local\\Programs\\Python\\Python312\\python.exe. 공식 .claude/skills/do-math/scripts/run_tests.py에 -u -B, --jobs 1, --output <자기 evidence의 짧은 새 경로>를 사용한다. argv/cwd/환경·PID/시작·종료·실제exit·stdout/stderr·판본을 보존한다. 진행 result.json은 do_math.file_io.read_bytes_shared로 읽는다.

1. A1의 현재 소비와 원문을 읽고 A3의 정확한 새 반례를 먼저 실행한다. 기존 전체 실패를 찾으려는 반복 실행은 하지 않는다.
2. 최종 정본의 structure.test_doc_code sim.test_role_input_context unit.test_context_catalog sim.test_submission_receiver flows.test_submission_acceptance를 실행한다. 현재 module/class/ID를 먼저 확인하고 실제 _apply/600k 보고/출력 재개 시험이 포함됐는지 기록한다.
3. 공유 문서 검사 회귀는 unit.test_role_input_packaging unit.test_role_input_scoped_packaging unit.test_preflight unit.test_storage_report_projections unit.test_engine_trace_report_corruption unit.test_storage_record_queries boundary.test_engine_cli 및 sim.test_knowledge_currentness.RecoveryMaterialTests flows.test_knowledge_impact_retry.UnreadableBeforeReviewTests를 포함한다. 현재 doc_code를 사용하는 다른 직접 시험이 확인되면 이번 영향이 있는 정확 ID만 추가한다. 2/3의 중복은 제거해 하나 또는 순차 묶음으로 실행할 수 있다.
4. 공식 미러 생성 뒤 .agents/skills/do-math/scripts/run_tests.py로 위 동일 선택을 검증한다. 성공 검사를 새 변경·실패 없이 반복하지 않는다. 마지막 캐시 동기화 후 build_skill_mirrors.py --check와 probe_cli.py --skill-only를 통과한다. 전체일반/freshT3/전수변이/T4 전체와 새 T5는 배정하지 않는다.
5. 지정 Python으로 services/continuous-development/check.py report C:\\math C:\\math\\docs\\do-math\\continuous-development-2026-10-13 019 document-results를 통과한다. report는 각 A, 실제 changes, 반례/정상과 유지한 성질, 미검사·후속 책임을 담고 마지막 응답에 상태와 report 경로를 반환한다.
''')

write(O/'review.md','''# phase 018 manager 검수

report 전문과 A1~A4를 읽고 공용 문서 편집 전에 check.py report를 통과했다. source-start2675개는017 manager 검수와 같고, 현재2675개는 task 종료와 전건 같다. 허용8변경은 fixture2·지침2·비용캐시4이며 report/writes에 대응한다. runtime/공급자·Lean·예약 입력139, corpus144/150SHA, host8원자료·도구, baseline910파일과 Git blob, index/pseudo/T3-store를 원자료와 대조했다.

현재 JobsContract._cleanup_job는 명시 terminate 뒤 root wait, 기존 cli_execution.termination_confirmed의 root signal·active0·빈PID를 확인하고 finally에서 close한다. 원문11shared test method와 runtime API는 유지했다. 실제 before2의 close 직후 wait258, 초기화된 live cwd의 WinError32와 종료 뒤 삭제 성공, after의 세 상태·각 signal0/빈Job/directory_removed를 읽었다. 두 오류 주입 사례는 본문 ValueError와 cleanup ObservationFault를 따로 기록하고 real/fake 핸들을 해제한다. 역사 race는 미재현이고017 오류 순간 상태는 없으며 bootstrap WinError5 원인도 미확인이다. 이 한계는 유지하고 현재 동기화 공백과 새 회귀 통과로 F1을 종결한다.

공식 exact1·정본관련27·미러관련27과 최종 정본/미러 T4 각각295개 선택·고유row·passed·실제exit0를 재대조했다. 양쪽 전체 --list와 실제 결과가 같고 Python875개가 현재와 일치한다. 각60worker의 요청/run_id/소스·공유 publication 검사·artifact SHA/원branch DB·부모 합집합 포함과 adapter5개 raw 재분석을 확인했다. 양쪽102/142는 정보이며 기능합격과 별도로 측정complete다.015의12미통과와017의 정확cleanup 오류는 새 전체에서 passed다. 기존 source-identical 환경7ID도 모두 선택에 포함돼 passed다. manager는 제품 시험을 다시 실행하지 않았다.

첫 manager 검산 exit1은 canonical exact/related 실행 뒤 아직 생성 전인 미러2파일까지 최종 동일성을 요구한 관리 스크립트 오류다. 원script는 verify-v1.py에 보존했다. 실제 검사한 tree의 동등성을 관련 실행별로 확인하고 최종 두 전체에는 양쪽 tree 불변을 요구하도록 교정해 exit0을 얻었다. 제품 판정이나 시험 근거를 고치지 않았다. task2463파일과 이전017 evidence5917파일은 검산 전후 불변이다.

018의 parent TEMP는 외부 전용 경로, git probe는128/빈stdout이며 resource output은c4/m4다.229자 cwd는 현 고정폭 구성으로 계산한 값이고017의241자 성공은 실제 관측이다. 이를 같은 종류의 관측으로 바꾸지 않는다. 두 실제 전체 실행의 설치probe 정상/반려 통과를 함께 사용한다. 지침2파일 추가는 허용 범위이며 기존22제품 중 나머지20파일은 불변이다. 원지침의 역편집은 시작SHA와 일치하나 사전 복사라고 주장하지 않는다.

F2의 지정 T4 남김과 F3의 보존 사실을 종결한다.015~016제품22경로와018fixture2경로, 합24경로는 관련 검수와 최종 T4 연결이 충분하므로 이번 관리 커밋에 포함한다. 비용캐시4·무관 dirty는 제외한다. 원task 자료와24제품 바이트는 raw-evidence.zip에 보존하고 추적/로컬 구분과 SHA는 preservation.json에 둔다. 새 커밋용 관리·기억만 추가하며 제품 바이트는 그대로다.

다음019는P02 네owner의 문서 결속을 실제 생산·저장·역할 입력으로 연결하는 단일 work다. 공유doc_code와 미러/캐시를 한 task가 소유하며, 독립된 무관 조사를 추가하지 않는다. L01 운전host·단위의 외부 결정은 답변 전 기존byte 요구/미충족으로 남긴다. P03/REVIEW/TRUST/다른 의미·문서와 G4~G6/G8 전체 관문도 유지한다. 직전 phase는 work이고 전체 기준 근거가 없으므로 종료하지 않는다.
''')

before={name:(RUN/name).read_text(encoding='utf-8-sig') for name in ('context.md','plan.md','seams.md')}
c=before['context.md']
def append_section(text,id,addition):
    start=text.index('## '+id+' '); end=text.find('\n## ',start+1)
    if end<0: return text.rstrip()+'\n\n'+addition+'\n'
    return text[:end].rstrip()+'\n\n'+addition+'\n'+text[end:]
c=append_section(c,'C2','phase 018 job-cleanup은 A1~A4 complete로 검수했다. report 검사 뒤 시작2675파일과017 검수본 동일, 현재와 종료 전건 일치, 허용8변경(정본fixture/지침2·미러2·비용캐시4)을 확인했다. 정확1·양쪽관련27·양쪽전체T4 각295선택/고유passed/exit0와 각875Python·각60worker 게시/원DB/adapter5개를 대조했다. 실제 close 직후 root wait258과 live cwd 잠금, 수리 뒤 suspended/resumed/자연종료3상태의 signal/빈Job/삭제 및 real/fake 오류 보존을 확인했다. 역사race 미재현·오류순간 미관측과 bootstrap WinError5 원인미확인은 유지한다. manager 첫 검산의exit1은 생성 전 미러까지 관련 정본 실행의 최종동등성을 요구한 관리 오류이며 검사한tree/최종전체 양쪽으로 구별해 exit0을 얻었다. task2463파일과017 evidence5917파일은 불변이다. 근거는 run:phases/018/manager-evidence/verification.json·review.md다. 지정 T4 완료이며 전체G 완료는 아니다.')
start=c.index('phase 001~017의 task 세션은 종료됐다.'); end=c.index('\n\n',start)
c=c[:start]+'''phase 001~018의 task 세션은 종료됐다.019 document-results 단일 work가 P02의 source_ref·materialized_output_files·research_sources·results를 실제 생산/저장/역할 입력 및 문서 검사로 연결한다. 공통 doc_code와 직접 소비 시험·미러·캐시를 같은 task가 수정·검증하므로 다른 제품 작업을 병행하지 않는다. 원래 P02의 한정 종료 질문과 현재 확인한 AST 결속을 처리하며 무관한 독립 조사로 범위를 늘리지 않는다. jobs1·전체worker3 이하·한 묶음씩을 유지한다. runtime/공유 인터페이스와018 T4 경계는 고정하고 범위 밖 결함은 반례로 반환한다. 새 유료 공급자·예약 변경·학술 호출·기존 연구 운전은 배정하지 않는다.'''+c[end:]
c=append_section(c,'C8','018의 gpt-6.1-sol/high 작업을 검수했다.019 document-results도 같은 사용자 지정 모델/effort로 배정하며 manager 설정·제품 공급자 실호출과 구별한다.')
c=append_section(c,'C9','018에서 116cff28/0b05e8ab/23cc4df3의 실제 Job 도입/포트/시험 이행 diff와 현재 JobsContract·WindowsJob·collector,010/016의 승인 근거를 대조했다. 기존 kill-on-close와 별도 종료 관측 의미는 유지하고 shared fixture가 종료를 기다리지 않던 소비만 교정한 판단을 승인한다. PR02의 이 Job slice만 닫으며 전체PR·다른hunk·부재 원보고 counts는 확대하지 않는다. 근거는 run:phases/018/tasks/job-cleanup/evidence/review.md·history-job-origin.stdout·history-job-port.stdout·history-job-migration.stdout 및 manager 검수다.')
c=append_section(c,'C10','018의 지정 T4 cleanup과 실제 전체 연결은 완료됐다.019는 외부 L01 결정과 독립적인 P02 네owner만 맡는다. source_ref의 실제 catalog bytes, _apply의 보고/산출 보존 및 _context/포장의 복원 local_path를 기존 생산/수신 시험에 연결한다. 수제task.results의 물질화와 실제 생산을 구별하며600k 보고/파일 재개와 독립bundle 비중복은 기존 흐름을 사용한다. 현재 doc_code의 review_sources와 P03 실행 안내/설치, 다른P/N은 이 배정 밖이다. runtime/문서 의미를 줄이거나 새 AST 추론기를 만들지 않는다. 근거는 run:phases/019/tasks/document-results/objective.md다.')
c=append_section(c,'C11','018에서017의 정확 cleanup 남김을 종결했다. 시험이 소유한 Job을 terminate·root wait·termination_confirmed로 확인한 뒤 finally에서 close하고 디렉터리를 정리한다. 현재 runtime API는 불변이다. 실제3상태와 오류2경로, exact1·양쪽관련27 및 새 양쪽전체T4 각295passed/exit0를 검수했다. 각60worker 측정complete·원branch DB/게시·부모합집합·adapter5개 정보102/142도 대조했다.015의12미통과와017환경7ID/cleanup1은 새 전체passed에 대응한다. 역사 실패·race 원인미확인·bootstrap WinError5 미확인과017 raw의 미러재사용 한계는 유지한다.229자cwd는 계산값이며241자 과거실측과 구별한다. 이번 전체T4를 G4 기본전체/G5 freshT3/G6 전수변이/G8 최종review로 대체하지 않는다. 근거는 run:phases/018/manager-evidence/verification.json·review.md다.')
c=append_section(c,'C12','018 F3의 보존과 한정 재사용을 검수했다. runtime139입력·corpus144경로/150명시SHA·host8원자료/도구·baseline910·index/pseudo/T3-store는 불변이다. 기존22제품 중 허용된 지침2에 단락을 추가했고 나머지20은 불변이며,017 companion 정의/원자료도 보존됐다. --check1336/skill-only와 실제 양쪽전체T4 성공을 확인해015~016제품22 및018fixture2, 합24비캐시 제품경로를 이번 관리 커밋으로 마감한다. 기존 실호출의 승인 성질만 재사용하며 새 호출은 없다. 원task 자료와24제품 바이트의 압축/전건SHA·선별 추적 경로는 run:phases/018/manager-evidence/preservation.json에 둔다. 압축만 추적하는 scratch/중복snapshot의 원경로와 stage/commit 행정 수신은 로컬 보관으로 정리 때 사라질 수 있다. 압축은 자동 복원 지시가 아니다.019 배정/관리·기억 추가는 검증한 제품 바이트를 바꾸지 않는다.')
write(RUN/'context.md',c)

p=before['plan.md'].replace('## phase 001~017의 결과와 현재 상태','## phase 001~018의 결과와 현재 상태',1)
p=p.replace('018은 cleanup 소비 수리와 새 전체 연결을 맡는다. 최종 전체 관문은 아직 실행하지 않았다.','018의 A1~A4도 검수했다. 종료확인 fixture 수리와 실제3상태/오류2경로, 정확1·양쪽관련27·양쪽전체T4 각295passed/exit0 및 각60worker 측정complete를 확인해 지정cleanup/T4 남김을 닫았다. 역사race와 bootstrap 원인미확인은 유지한다. 최종 전체일반/freshT3/전수변이 관문은 아직 실행하지 않았다.',1)
a=p.index('## 다음 phase: 018'); b=p.index('## 가까운 후속 배정과 선행 관계',a)
p=p[:a]+'''## 다음 phase: 019

gpt-6.1-sol/high의 document-results 단일 work를 배정한다. P02 네owner(source_ref, materialized_output_files, research_sources, results)의 실제 catalog·_apply 생산/보존·_context 복원·최종 포장과 문서 필드를 기존 시험에 연결한다. 현재 AST/문자열 bindings의 한정 범위를 교체하고 실제 파일 바이트·소유자·해시/크기·report 누락/다른local_path 반례를 확인한다. 수제task.results fixture는 물질화 근거로만 쓰고 생산/독립bundle 비중복과600k보고·파일 재개는 기존 수신/flow에 연결한다. P01과B130~B134를 재구현하지 않는다.

doc_code/helper와 현재 직접 소비자를 같은 task가 소유한다. 일반 문서 순회의 위임과 실제 owner 담당을 대응시키고 오기·잘못된 owner·다른 경계의 건너뜀을 반려한다. 관련 정본/미러 선택·고유row·실제exit·판본을 보존하고 공식 미러/check/skill-only로 인도한다. 기존 runtime·T4 runner/adapter/Job fixture·corpus·설치/연구는 고정한다. 제품 변경 task를 병행하면 공유doc_code·캐시/미러 판본을 독립 검증할 수 없어 단일로 둔다. 전체T4를 새로 반복하거나 새 실호출을 수행하지 않는다.

018의T4 전건 성공으로015~016제품22와018fixture2, 합24경로를 이번 관리 커밋으로 마감한다. 비용캐시4·무관dirty는 제외한다. L01 Q1/Q2의 운전 프로필·출력 단위는 계속 미정이며 원문byte 기준과 미충족을 유지한다. P03/REVIEW/TRUST·다른의미/문서와 전체일반/freshT3/전수변이·최종review는 별도 후속 책임이다.

'''+p[b:]
p=p.replace('전체T4는 정본 Job cleanup 오류가 남아018에 넘긴다.01512·01610비캐시 제품, 합22경로의 마감은018 수리·전체 연결 검수까지 대기한다. 근거는016 및017 manager-evidence/verification.json·review.md다.',
 '전체T4의 정본 Job cleanup 오류는018의 fixture수리와 양쪽295passed로 종결됐다.01512·01610·018fixture2의 합24비캐시 제품경로를018 관리커밋으로 마감한다. 근거는016~018 manager-evidence/verification.json·review.md다.')
p=p.replace('P02~P11·N01~N03의 미결 절만 실제 반환/공유 계약·기존 시험에 연결한다.', '019가 P02 네owner를 맡고 P03~P11·N01~N03의 다른 미결 절은 후속으로 남긴다. 실제 반환/공유 계약·기존 시험에 연결한다.')
p=p.replace('새 Job cleanup 한 오류는018에서 처리한다.', '새 Job cleanup 한 오류도018의 종료확인 수리와 양쪽전체295passed로 닫았다.')
p=p.replace('017 c4의294passed/1error와 m4의295passed·각60worker 측정complete를 검수했다.018이 정확cleanup 수리 뒤 양쪽 새전체를 완료하고 manager가22제품경로의마감을판단한다.', '018의 최종 정본/미러 각295passed/exit0·각60worker 측정complete를 검수해 지정 T4 연결을 닫았다. 기존22와018fixture2의 합24제품경로를 이번관리커밋에 포함한다.')
write(RUN/'plan.md',p)
write(RUN/'seams.md',before['seams.md'].rstrip()+'''\n\n018의 기존 Jobs API 소비와 최종 양쪽T4 연결을 검수했다.019는 기존 write_source_catalog·_preserve_outputs·_apply·_context·prepare_role_input의 생산/저장/복원을 실제 소비하는 문서 검사 수리다. 정본은 해당 함수·contracts/record schema이며 별도 제품 형식을 만들지 않는다. 같은task가 doc_code와 직접소비/helper·미러를 소유하고 독립 제공자/소비자로 나누지 않으므로 S항목·provides/uses는 추가하지 않는다. runtime/입출력 의미 개정이 필요하면 반례로 후속 판단에 반환한다.\n''')
diff=''
for name,old in before.items():
    now=(RUN/name).read_text(encoding='utf-8')
    if name=='context.md': assert old.split('## C2 ')[0]==now.split('## C2 ')[0]
    diff+=''.join(difflib.unified_diff(old.splitlines(True),now.splitlines(True),fromfile=name+' before 018',tofile=name+' after 018'))
write(O/'common-docs.diff',diff)

updates={
 'C2':'018의실제검수·부분범위와관리검산오류를추가하고역사결과를보존한다.',
 'C5':'다음단일work와공유helper/캐시/미러독립성조건을019기준으로교체한다.',
 'C8':'019에도사용자지정gpt-6.1-sol/high를명시한다.',
 'C9':'PR02의Job도입/포트/fixture종료소비slice만종결하고전체범위를유지한다.',
 'C10':'외부L01과독립인P02의네owner·실제생산/물질화구별및후속범위를명시한다.',
 'C11':'cleanup/T4지정남김을새전체근거로닫고역사미관측·최종G한계를유지한다.',
 'C12':'018보존검수·지침허용변화·24제품마감과압축/추적경계를추가한다.'}
save(P/'manager.pending.json',{
 'next':'019',
 'decision':'job-cleanup의 report 전문과 근거를 대조해 A1~A4 complete를 승인한다. 시작/현재2675파일과 허용8변경, 실제 Job 종료/빈Job/디렉터리 정리, 정확1·양쪽관련27·최종양쪽T4 각295passed/exit0와 각60worker 측정complete를 확인했다. close가 동기 종료가 아니라는 실제 관측과 현 API를 쓰는 fixture수리로017 cleanup 남김을 닫는다. 역사race 미재현·오류당시 상태 미관측 및 bootstrap WinError5 원인미확인은 그대로다. 측정102/142는정보이며기능합격과별도다. manager첫검산exit1은생성전미러를정본관련검사판본에잘못포함한관리오류로,검사tree와최종전체를구별해교정했다. 원task2463파일·이전017 evidence5917파일은불변이다.\n\n015~016제품22경로에018fixture2를더한24경로는관련검수/최종T4연결이충분해이번로컬관리커밋에포함한다.지침2는허용된추가이며나머지20은불변이다.비용캐시·무관dirty는제외한다.원자료압축·선별추적과한개의기억노드를함께보존한다.\n\n전체일반/freshT3/전수변이/최종review와남은문서·의미/L01은미완료다.다음019 work는P02네owner의AST문서결속을실제catalog/_apply/복원/포장과연결한다.기존수제result의물질화와실제생산을구별하고기존수신/600k flow를사용한다.공통doc_code/미러/캐시를독립검증해야하므로단일task로배정한다.L01의외부결정없이수행가능하며현재byte요구를바꾸지않는다.제품코드는manager가수정하지않고새phase배정만한다.',
 'reports':[{'task':'job-cleanup','state':'read','detail':'check.py report 통과 뒤 전체 report 및 원관측/코드/공식실행/판본을 대조했다. A1~A4 pass를 승인하고 F1~F3를 지정범위로 종결한다.',
 'evidence':[T+'report.json',ref('report-check.json'),ref('verification.json'),ref('review.md')]}],
 'dispositions':[
 {'item':'018/job-cleanup/F1','action':'resolve','destination':['run:context.md#C9','run:context.md#C11'],
 'reason':'현API의종료확인fixture와새실제3상태/오류2경로·회귀/전체통과를승인해cleanup남김을닫는다.역사race/빈도및bootstrap원인은미확인으로보존하며과거원보고를바꾸지않는다.',
 'evidence':[T+'evidence/job-observation-before2.json',T+'evidence/job-observation-after.json',T+'evidence/cleanup-faults.json',ref('verification.json')]},
 {'item':'018/job-cleanup/F2','action':'resolve','destination':['run:context.md#C11','run:plan.md'],
 'reason':'현재판본의양쪽295고유passed/exit0·worker게시/DB/adapter정보를원자료에서검수했다.지정T4미통과를종결하고다른G/문서/L01은남긴다.',
 'evidence':[ref('verification.json'),T+'evidence/c4/report.json',T+'evidence/m4/report.json']},
 {'item':'018/job-cleanup/F3','action':'resolve','destination':['run:context.md#C12','run:plan.md'],
 'reason':'139입력/144corpus/150SHA/host8/도구/baseline910/기존20제품/과거raw불변과허용지침2변화를검산했다.한정실호출재사용을유지하고검수된24제품경로를이번관리마감에포함한다.',
 'evidence':[ref('verification.json'),T+'evidence/preservation.json',ref('preservation.json')]}],
 'context_updates':[{'item':id,'action':'amend','destination':['run:context.md#'+id],
 'reason':reason,'evidence':[ref('common-docs.diff'),ref('verification.json'),'run:phases/019/tasks/document-results/objective.md']} for id,reason in updates.items()],
 'plan_update':'018의지정cleanup및T4전체연결을종결하고24비캐시제품의관리마감을기록했다.다음은019 document-results의P02실제생산/저장/문서결속이다.공통helper·미러/캐시를한task가소유한다.나머지의미/문서·L01외부결정과G4~G6/G8관문·최종review순서는유지한다.과거실패를소급삭제하지않았다.',
 'seam_updates':[],'completion':None})

# Recheck the current convention and node allocation at the point of writing.
assert 'convention_version: 27' in (R/'기억/세칙.md').read_text(encoding='utf-8')
assert sorted((R/'기억/layer1').glob('M-*.md'))[-1].name=='M-0567.md'
write(R/'기억/layer1/M-0568.md','''---
id: M-0568
layer: 1
title: Job 정리와 전체 T4 연결을 종결하고 결과 문서 결속을 배정함
convention_version: 27
---

## 맥락

phase017은 실제 비교와 미러 T4가 통과했지만 정본295건 중 하나가 TemporaryDirectory 정리에서 실패했다.018은 runtime close의 의미를 바꾸지 않고 시험 소유 Job의 종료 확인을 fixture에 추가했다. 새 manager가 실제 관측과 양쪽295passed, worker게시·분기DB·현재판본을 대조해 이 남김을 닫았다.015부터 대기한 제품22경로와이번fixture2를 같은관리커밋에 담는다. 전체일반/freshT3/전수변이와다른문서/의미·L01은남아있어개발완료는아니다.

## 판단에 남길 조건

close 직후 보존process handle의wait258은 핸들해제와종료완료가다른사건임을보였다.초기화된live cwd는WinError32였고명시종료/빈Job확인후삭제됐다.정확한과거race는재현되지않았고오류순간상태도없다.현재동기화공백의교정과새전체통과를승인하는데역사인과까지확정할필요는없었다.과거bootstrap WinError5 원인도미확인으로남긴다.

manager 첫검산은정본관련검사당시생성전미러까지최종판본과같아야한다고요구해exit1이었다.검사한tree의해시와미러생성후최종전체의양쪽해시를구별해관리검산을고쳤다.제품이나원시험결과를바꾸지않았다.이조건은앞선관련회귀를새판본증거로재사용할때어떤tree를실제로실행했는지확인할필요를구체화한다.

다음019는원자료/결과/복원파일의네owner를실제생산과문서검사에연결한다.수제task.results는물질화만보이므로_apply생산·독립bundle비중복은기존수신/600k흐름에연결하도록배정했다.서로다른증거의보증범위를맞추되동일장기시나리오를중복구축하지않는다.

근거의진입점은 docs/do-math/continuous-development-2026-10-13/phases/018/manager.json 및 manager-evidence/verification.json·review.md다.원task자료와24제품바이트는같은디렉터리 raw-evidence.zip에추적하며경로별SHA/선별추적범위는preservation.json에둔다.압축으로만보존하는scratch/중복snapshot의원경로와stage/commit행정수신은로컬보관이어서정리로사라질수있다.압축은자동복원지시가아니다.이전원report와역사실패는그대로유지했다.
''')
index=R/'기억/색인.md'; text=index.read_text(encoding='utf-8-sig')
write(index,text.replace('## layer-1\n','## layer-1\n\n- M-0568 [Job 정리와 전체 T4 연결을 종결하고 결과 문서 결속을 배정함] -- 종료확인·양쪽295건 검수와24제품마감, 역사인과 한계 유지·019 P02 생산/복원 연결\n',1))
print('Prepared 019/document-results, common-doc diff, manager.pending.json and M-0568.')

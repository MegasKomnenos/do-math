"""Write the phase 019 disposition and a bounded phase 020 assignment."""
import difflib
import json
from pathlib import Path
import subprocess
import sys

R=Path('C:/math'); RUN=R/'docs/do-math/continuous-development-2026-10-13'
P=RUN/'phases/019'; O=P/'manager-evidence'; N=RUN/'phases/020'
def write(p,s): p.write_text(s,encoding='utf-8',newline='\n')
def save(p,v): write(p,json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def ev(n): return 'run:phases/019/manager-evidence/'+n
T='run:phases/019/tasks/document-results/'
v=json.loads((O/'verification.json').read_text(encoding='utf-8'))
assert v['current_equal_final'] and not N.exists()
(N/'tasks/document-tools/evidence').mkdir(parents=True)
(N/'logs').mkdir()
before={name:(RUN/name).read_text(encoding='utf-8') for name in ('context.md','plan.md','seams.md')}
write(O/'writing-brief.md', '''# 작성 합의

압축 진술: phase 019의 P02 네 소유자 결속과 양쪽 186통과·1권한 skip을 검수해 지정 작업을 닫는다. 전체 완료와 symlink 검증을 주장하지 않고, 020에는 P03 실행 안내·지급 도구 여섯 소유자만 실제 최종 입력에 연결하도록 배정한다.

무거운 것: 실제 생산/저장/복원 및 파일 소유권이라는 검수 근거, 조건부 미검사와 최종 G의 유지, 후속 P03의 정확한 범위·완료 조건·검증 책임.
가벼운 것: 판본 수치와 원근거 좌표, 역사 검토의 한정 범위, 관리 커밋과 보존 경계. 원문 protocol의 형식은 그대로 따른다.
뺄 것: 수행 순서 일지, 무관 dirty의 세부 내용, 모든 과거 phase의 새 요약, 원문의 G를 낮추는 판단.

확정 사실은 manager-evidence/verification.json과 현재 소스 diff, task report 및 binding-review.md에 있다. 현재2675파일·변경30(비용캐시2)·각187고유ID/186passed/1skipped/exit0·runtime139/corpus144/150SHA/host8/tools5/baseline910 보존을 대조했다. Windows1314 skip은 원문 G4에 남기며 통과로 세지 않는다. P03은 현재 doc_code와 실제 install_tools/_context/prepare_role_input의 문서 결속 수리이며 runtime API 개정·새 실호출은 배정하지 않는다. 개발 모델은 gpt-6.1-sol/high다.

원고는 변경한 공용 문서 전체, 019 검수/manager 제출물, 020 phase/objective, 기억 노드와 필수 protocol을 한 파일로 묶는다. 실제 후속 세션이 입력 원자료를 읽는 절차는 유지하며 독해자에게 정답 합의를 전달하지 않는다. 불변의 G1~G8·사용자 지시와 protocol이 우선한다. 프로토콜 서식으로 표현한 acceptance/disposition은 독해의 합격 판정과 별개다.
''')
write(O/'writing-audience.md', '''# 독자 정보

독자는 C:\\math의 continuous-development 서비스를 이어받는 새 개발 AI와 검수 manager다. Python·시험·Git과 역할 분담을 이해하지만 이전 대화는 받지 않는다. 원고의 protocol·공용 현재본·phase/objective를 읽고 지정 inputs의 원자료를 회수해 작업한다. 사람도 검수 판단과 남은 책임을 읽을 수 있어야 한다.
''')
flow=R/'.claude/skills/write-for-reader/scripts/writing_flow.py'
cmd=[sys.executable,'-B',str(flow),'--session','continuous-phase019-manager','begin',
     '--draft',str(O/'handoff-draft.md'),'--brief',str(O/'writing-brief.md'),'--audience',str(O/'writing-audience.md')]
p=subprocess.run(cmd,cwd=R,capture_output=True)
save(O/'writing-begin.json',{'argv':cmd,'exit_code':p.returncode,'stdout':p.stdout.decode('utf-8',errors='replace'),'stderr':p.stderr.decode('utf-8',errors='replace')})
assert p.returncode==0,p.stderr

test_paths=['support/doc_code.py','support/engine_context.py','structure/test_doc_code.py',
 'sim/test_role_input_context.py','sim/test_knowledge_project_identity.py','unit/test_submission_preview_commands.py',
 'unit/test_role_input_packaging.py','unit/test_role_input_scoped_packaging.py','unit/test_preflight.py',
 'unit/test_context_catalog.py','sim/test_submission_receiver.py','flows/test_submission_acceptance.py',
 'flows/test_knowledge_impact_retry.py','boundary/test_engine_cli.py','unit/test_storage_report_projections.py',
 'unit/test_engine_trace_report_corruption.py','unit/test_storage_record_queries.py','sim/test_knowledge_currentness.py']
documents=['README.md','references/CLI-실행-계약.md','references/공통-실행.md','references/입력-소비자.md',
 'references/자기-점검.md','references/지식-저작과-재사용.md','계약/연구-수행.md','계약/유지보수.md']
relative=['scripts/tests/'+p for p in test_paths]+documents+['scripts/tests/.timings.json','scripts/tests/.timings-t3.json']
writes=[tree+'/skills/do-math/'+p for tree in ('.claude','.agents') for p in relative]
assert all((R/p).is_file() for p in writes)
inputs=['run:sources/user-decisions.md','run:sources/model-policy-2026-10-14.md',
 'run:phases/001/tasks/document-closeout/report.json',
 'run:phases/001/tasks/document-closeout/evidence/followup-packets.json',
 'run:phases/001/tasks/document-closeout/evidence/binding-inventory.json',
 'run:phases/001/tasks/closure-map/evidence/prior-review-state.json',
 T+'report.json',T+'evidence/binding-review.md',T+'evidence/preservation.json',
 ev('verification.json'),ev('review.md'),ev('source-inspected.json'),
 'run:phases/010/tasks/host-smoke/evidence/review.md',
 'run:phases/012/tasks/lean-smoke/evidence/review.md',
 'repo:docs/do-math/시험-재편-2026-09-29/설계.md',
 'repo:docs/do-math/시험-재편-2026-09-29/조사/결함-범주.md',
 'repo:.claude/skills/do-math/AGENTS.md',
 'repo:.claude/skills/do-math/scripts/tests/시험-지침.md',
 'repo:.claude/skills/do-math/scripts/이음새-정본.md',
 'repo:.claude/skills/writing-skills/references/멀티런타임_동기화.md']
inputs+=['repo:.claude/skills/do-math/'+p for p in documents]
inputs+=['repo:.claude/skills/do-math/scripts/'+p for p in ['do_math/context_store.py','do_math/core_engine.py',
 'do_math/submission.py','do_math/contracts.py','tests/support/doc_code.py','tests/support/engine_context.py',
 'tests/sim/test_role_input_context.py','tests/unit/test_submission_preview_commands.py','tests/sim/test_knowledge_project_identity.py']]
save(N/'phase.json',{'kind':'work','purpose':'P03 실행 안내와 지급 도구의 문서 필드를 실제 설치·최종 역할 입력에 연결한다.',
 'tasks':[{'id':'document-tools','model':'gpt-6.1-sol','effort':'high','inputs':inputs,'writes':writes,'provides':[],'uses':[]}]})
write(N/'tasks/document-tools/objective.md','''## 목적과 역할

G1/G3의 문서 결속 중 phase 001 followup-packets의 P03을 닫는다. 실행 안내와 지급 도구의 필드가 실제 설치 후 역할 입력을 검사하도록 기존 시험에 연결한다. 대상 소유자는 record_map의 read_tool, execution_window, scholarly, formal_verifier, preview, submission_contract다. record_map 기본 반환에 대한 기존 검증은 보존한다. 현재 doc_code의 AST 조립은 install_tools가 만든 파일과 최종 입력의 일치를 증명하지 못한다.

019의 P02는 검수됐고 양쪽187건 중186통과·기존 symlink 권한1skip이었다. 수리한 P01/P02·B130~B134의 실제 결과 검사를 유지한다. P03은 그 검사 기반을 공유하므로 한 task가 doc_code·직접 소비·미러를 소유한다. 실행 도구 설치와 포장을 확인하되 도구가 실제 모델·Lean·학술 호출에 성공했다는 별도 주장을 만들지 않는다.

## 완료 조건

### A1 현재 문서와 설치 전후 경계 확정

시작 skills/diff 해시를019 manager source-inspected2675파일과 대조하고 차이의 출처를 구별한다. P03의 현재 문서 위치·별칭·조건을 _context, prepare_role_input, record_map, install_tools의 실제 생산/소비에 연결한다. followup-packets의 역사 행 번호는 현재 제목과 코드로 확인한다. 결함-범주.md의13-C와 P03 지정 원문을 읽되 다른 packet으로 조사 범위를 늘리지 않는다.

execution_window의 경로 안내와 실제 동적 파일, scholarly.configured와 실제 도구 노출/호출, formal_verifier.preview의 지급 명령과 그 명령의 반환 JSON을 구별한다. B110~B114의 이 P03 slice만 actual diff·현재 소비·존재 원보고로 유지/교체/제거 판단한다. record_map 기본 반환과010 host·012 Lean의 승인된 성질은 재사용하고 PR24 전체를 완료로 올리지 않는다.

### A2 실제 설치와 최종 입력에 결속

기존 PreparedInputTests·RoleScopeContextTests·LeanPreviewTests·FormalInputManifestTests와 role packaging 시험을 사용해 대상 여섯 소유자를 실제 반환 또는 기존 공유 계약에 연결한다. install_tools가 쓴 input/tools의 세 wrapper·submission-support.zip, 제출 schema/context 파일과 실제 command/경로·tool_sha256·snapshot·권한 범위를 대조한다. 기존 archive/명령 실행 근거가 충분하면 재사용하고 새 장기 엔진 시나리오를 만들지 않는다.

_context의 실제 execution_window.self_check_directory와 고정 프로필에 따른 scholarly, 실제 formal_verifier, 설치 후 preview/record_map.read_tool/submission_contract 및 limits.checkpoint_bytes/max_artifact_bytes를 확인한다. 최종 fitted 입력에서 참조로 포장된 경우에는 정확한 참조 파일을 읽는다. 검사 정상 표본을 수동 복제하거나 제품 내부 생산/설치/포장을 대역으로 가리지 않는다. 외부 포트 대역과 실제 실행 근거의 범위는 구별한다. 기본 record_map 반환 검사를 유지하면서 read_tool AST만 실제 설치 결과에 연결한다.

문서의 기한·정지·종료 요청 의미, preview의 authoritative=false 및 중앙 재검사, scholarly 설정과 실제 성공의 차이, 콘솔 없는 실행기에서 지급하는 console Python 조건을 보존한다. 필요한 문장·별칭만 writes의 문서에 반영한다. runtime API와 입력/출력 의미를 문서 검사 편의로 바꾸지 않는다.

### A3 누락·다른 도구·조건부 부재와 실제 담당 검사

실제 반환 후 사본에서 self_check_directory, 지급 command, checkpoint_bytes, max_artifact_bytes를 각각 삭제해 문서 검사가 반려하는지 확인한다. 같은 command 필드라도 다른 지급 도구의 명령으로 바꾸거나 파일/해시를 차용하면 거부해야 한다. 설치된 정상 preview와 설치하지 않은 조건을 구별하고, 미설치 경로를 정상 필드 증거로 쓰지 않는다. windowless 실행기의 console sibling 정상 선택과 sibling 부재의 명시 반려·무부수효과는 현재 기존 시험에 연결한다. 고정 프로필 외 도구 override 반려와 실제 worker 미기동 단언을 보존한다.

새 단언이 드러내는 정확한 공백을 수리 전 실행해 red를 남기고 같은 성질의 green을 연결한다. 일반 문서 순회가 실제 입력 담당에게 위임하는 경우 소유자별 실제 문서 검사 위치를 명시한다. defer 오기·담당 누락·다른 소유자 동시 건너뜀 반례와 기존 P01/P02 등의 음성 단언을 유지한다. 범용 추론기·전역 등록부를 추가하지 않으며 이번 대상의 마지막 소비가 없어지는 AST 조립만 제거한다.

### A4 관련 회귀와 인도 근거

아래 최종 관련 선택을 정본과 미러에서 완결하고 선택/고유 row/실제 exit 및 실행 전후 소스를 보존한다. 허용 범위의 공식 미러 생성·마지막 캐시 동기화·--check·skill-only를 통과한다. 조건부 환경 skip은 통과로 세지 않고 원인·영향 성질·G4 후속 책임을 기록한다. P03 필수 성질 자체가 미실행이면 해당 A는 pass가 아니다.

019 preservation의 runtime/실호출139입력·corpus144경로/150명시SHA·host8원자료/도구5·과거baseline910·T4 고정 경계를 보존한다. 문서 수정이 향후 역할 prompt 판본에 미치는 영향과 기존 실호출의 한정 재사용을 구별한다. P04~P11·REVIEW/TRUST·나머지 P/N·L01과 G4~G6/G8은 후속 책임으로 남긴다.

## 판단과 경계

writes는 지정 시험/helper·문서 및 대응 미러/캐시다. 모두를 수정하라는 뜻은 아니다. helper의 작은 공통 함수와 구체적 시험 배치는 재량이다. runtime/core_engine/context_store/submission·runner·adapter·Job fixture·corpus·서버·설치 신뢰·공유 설정·공용 context/plan·다른 phase는 고정한다. 범위 밖 결함은 정확 재현, 필요한 파일, 영향 A와 후속 조치로 반환한다. 다른 owner의 AST가 남았다는 이유만으로 이번 범위를 늘리지 않는다.

전체 worker3 이하, jobs1, 한 묶음씩이며 검사 중 소스를 고정한다. parent TEMP/TMP/TMPDIR는 저장소 밖 짧은 전용 경로를 사용하고 output/resource cwd도 짧게 둔다. 시간 예산은 소프트 기준이다. 새 유료 공급자·예약·학술 호출, 설치 신뢰 변경, 기존 연구 운전/삭제, graphify 갱신, Git stage/commit/reset/checkout/push는 수행하지 않는다. 개발 작업은 gpt-6.1-sol/high이며 제품 실호출 설정과 다르다.

## 검증 방법

cwd C:\\math, Python C:\\Users\\wogud\\AppData\\Local\\Programs\\Python\\Python312\\python.exe. 공식 run_tests.py에 -u -B, --jobs 1, --output <자기 evidence의 짧은 새 경로>를 쓴다. argv/cwd/환경·PID/시각·종료·stdout/stderr·판본을 보존한다. 진행 result.json은 do_math.file_io.read_bytes_shared로 읽는다.

1. A1 경계를 확정하고 A3의 정확한 새 반례를 수리 전 실행한다.
2. 최종 정본에서 structure.test_doc_code sim.test_role_input_context unit.test_submission_preview_commands sim.test_knowledge_project_identity unit.test_role_input_packaging unit.test_role_input_scoped_packaging unit.test_preflight를 실행한다. 현재 class/method를 확인해 실제 설치와 최종 포장 경로의 포함을 기록한다.
3. 공유 helper와 문서 순회의 회귀에는 unit.test_context_catalog sim.test_submission_receiver flows.test_submission_acceptance unit.test_storage_report_projections unit.test_engine_trace_report_corruption unit.test_storage_record_queries boundary.test_engine_cli sim.test_knowledge_currentness.RecoveryMaterialTests flows.test_knowledge_impact_retry.UnreadableBeforeReviewTests를 포함한다. 2/3의 중복을 없애 한 묶음 또는 순차 묶음으로 실행한다. 목록 밖 직접 소비에서 이번 변경으로 오류가 확인되면 정확 ID를 검증에 추가하고 writes 밖 수정은 manager에 반환한다.
4. 공식 생성 계획이 writes 안인지 확인한 뒤 미러를 생성한다. 미러 run_tests.py로 같은 최종 선택을 실행하고 마지막 캐시 동기화 뒤 build_skill_mirrors.py --check와 probe_cli.py --skill-only를 통과한다. 새 변경·실패 없이 성공 검사를 반복하지 않는다. 전체일반/freshT3/전수변이·전체T4·새T5는 이번 배정에 없다.
5. 지정 Python으로 services/continuous-development/check.py report C:\\math C:\\math\\docs\\do-math\\continuous-development-2026-10-13 020 document-tools를 통과한다. report에 A1~A4, 실제 changes, 정상/반례·소유자별 책임, 역사 근거 재사용과 미검사 범위를 기록한다. 마지막 응답은 상태와 report 경로다.
''')

review='''# phase 019 검수

P02의 지정 A1~A4를 승인한다. manager는 원 report 형식 검사 뒤 현재2675파일·시작과018 판본 동일·허용30변경, 공식 선택/실제 row/exit와875개 Python 해시를 직접 검산했다. 정본과 미러의 동일187개 ID는 각각186passed·권한1314의 symlink1skipped·exit0이다. skip은 G4에서 원문 계약에 따른 조건부 미검사를 판정할 대상으로 유지한다. 개발 전체 완료는 아니다.

실제 코드 diff에서 source_ref의 catalog writer, results의 _apply 보존, _context의 원자료/과제 결과 물질화와 prepare_role_input을 확인했다. 새 helper는 저장 artifact와 이번 workspace의 task/execution별 local_path, snapshot 원바이트·SHA·크기를 대조한다. 동일 바이트의 다른 실행 경로도 반려한다. 수제 results는 복원만 증명하고 실제 생산·knowledge 별도 권위·독립 bundle 비중복은 기존 수신과600k 보고/파일 개정·재개 시험이 맡는다. 일반 defer의 담당 AST 검사는 실제 결과를 추론하는 데 쓰이지 않고 담당 method와 문서 검사 호출의 존재만 확인한다. 실제 실행 row와 구체적 단언을 함께 대조했다.

수리 전8개 owner/별칭 subTest의 red, 초기13error와 corrected23passed, 최종 양쪽의 정확 failed/error ID 해소를 원 row로 확인했다. 정상 빈 배열은 원소 필드 증거와 구별되고 실제 제품의 손상 hash 반려·read_source size/hash 사유는 반환 사본 교란과 별도다. P01·B130~B134 및 다른 owner의 실패 단언이 최종 선택에 남는다. B110~B114 중 P02 AST/문자열 조립만 교체한 처분을 승인하며 PR24·REVIEW/TRUST 전체는 종결하지 않는다.

runtime/실호출139입력·144corpus경로/150명시SHA·host8원자료/도구5·baseline910의 바이트/Git blob·T4 고정 경계가 보존됐다. 공식 생성·캐시 동기화·check와 skill-only의 실제 exit와 원출력을 확인했다. 두 문장은 앞으로 일반 역할 prompt에 들어가므로 과거 고정 smoke를 새 문서 읽기/AI준수의 근거로 사용하지 않는다. 원task181파일은 검산 전후 불변이며 이전 실패도 수정하지 않았다.

다음020은 P03의 실행 안내와 지급 도구를 실제 설치 후 최종 입력에 연결한다. 현재 doc_code의 해당 AST 조립과 install_tools/_context를 직접 확인해 한정 범위를 정했다. 공통 helper·문서 순회·미러·캐시가 겹쳐 다른 제품 작업과 병행하지 않는다. L01의 외부 결정과 독립적이며 새 실호출·전체T4 반복은 배정하지 않는다. G4 기본전체, G5 freshT3, G6 전수변이, 나머지 의미/문서 및 최종 review가 남아 next:null 조건은 충족하지 않는다.
'''
write(O/'review.md',review)

c=before['context.md']
summary='''phase 019 document-results는 A1~A4 complete로 검수했다. 시작2675파일은018 manager 판본과 같고 종료/현재 전건 해시가 일치한다. 허용30변경(정본14·미러14·비용캐시2)과 최종 양쪽 동일187선택/고유row·186passed/1skipped/exit0, 각875Python·실행 전후를 대조했다. skip은 기존 symlink 생성 권한1314이며 통과나 실제 탈출 반려 증거로 세지 않는다. 수리 전8반례의 red·초기13error·corrected23passed와 최종 정확ID 해소를 검수했다. 실제 생산/물질화·동일 바이트 다른 실행 경로 반례와 원task181파일 불변을 확인했다. 근거는 run:phases/019/manager-evidence/verification.json·review.md다. 지정 P02 완료이며 전체G 완료는 아니다.\n\n'''
c=c.replace('## C3 현재 정본과 이력의 역할',summary+'## C3 현재 정본과 이력의 역할',1)
a=c.index('phase 001~018의 task 세션은 종료됐다.'); b=c.index('\n\ndo-math 시험 프로세스',a)
c=c[:a]+'''phase 001~019의 task 세션은 종료됐다.020 document-tools 단일 work가 P03의 execution_window·scholarly·formal_verifier·preview·submission_contract와 record_map.read_tool을 실제 설치/최종 입력에 연결한다. 공통 doc_code·직접 소비·미러·캐시를 같은 task가 수정하므로 다른 제품 작업과 병행하지 않는다. record_map 기본 반환과 P01/P02·B130~B134를 유지하며 jobs1·전체worker3 이하·한 묶음씩을 따른다. runtime/runner/adapter/Job fixture·corpus·기존 연구와 실호출 입력은 고정하고 범위 밖 결함은 반례로 반환한다. 새 유료 공급자·예약·학술 호출은 배정하지 않는다.'''+c[b:]
c=c.replace('## C9 요구별 상태', '019의 gpt-6.1-sol/high 수행을 검수했다.020 document-tools에도 같은 사용자 지정 model/effort를 명시한다.\n\n## C9 요구별 상태',1)
c=c.replace('## C10 문서 결속', '''019는 B110~B114의 P02 slice를 actual diff·현재 소비와 존재하는7원보고에 대조했다. source_ref와 stored/restored/results의 AST 조립을 실제 생산/복원 검사로 교체하고 명시 owner·line-local 별칭·저장/입력 구별은 유지한 판단을 승인한다. review_sources와 PR24의 다른 hunk는 남긴다. 역사 counts를 현재 성공에 더하지 않는다. 근거는 run:phases/019/tasks/document-results/evidence/history-verification.json·binding-review.md 및 manager 검수다.

## C10 문서 결속''',1)
a=c.index('018의 지정 T4 cleanup과 실제 전체 연결은 완료됐다.019는'); b=c.index('\n\n## C11',a)
c=c[:a]+'''019에서 P02 네 소유자의 지정 남김을 닫았다. source_ref는 실제 catalog canonical bytes/total과 input/details snapshot에, research_sources·materialized_output_files·results는 실제 _apply 저장/보존과 _context·포장의 파일/소유자/바이트에 연결됐다. 실제 수신과600k 재개가 생산·비중복을 맡고 수제fixture는 물질화만 맡는다. 필드 누락·다른 실행의 동일바이트 경로·hash/size 교란, 실제 손상 반려, 소유자별 문서검사/defer 누락을 확인했다. P01/P02 및 B130~B134의 완료 성질은 유지한다. 근거는 run:phases/019/manager-evidence/review.md와 원task binding-review.md다.

020은 P03 여섯 소유자의 실행 안내/지급 도구 설치 후 최종 입력만 맡는다. 기본 record_map의 실제 반환은 유지하고 read_tool의 AST만 실제 설치로 연결한다. scholarly.configured는 호출 성공과 구별하고 preview 지급 명령은 반환 JSON과 다른 경계다. L01 외부 결정, REVIEW/TRUST·P04~P11·N의 다른 절과 최종 관문은 유지한다. 근거는 run:phases/020/tasks/document-tools/objective.md다.'''+c[b:]
c=c.replace('## C12 공급자 부분 성공', '''019의 관련 양쪽187건에는 기존 ContextStoreTests.test_outside_symlink_is_reported_when_supported가 Windows1314로 각1skip됐다. P02 지정 성질은 실행됐으나 실제 symlink 탈출 반려는 이번 환경에서 미검사다. G4 최종 기본전체에서 권한조건 skip의 원문상 정당성을 별도 판정하며 통과로 세지 않는다. 권한이나 완료 기준은 변경하지 않았다. 근거는019 manager verification.json과 최종 c/m 원report다.

## C12 공급자 부분 성공''',1)
c+='''
019 F3의 보존과 한정 재사용을 검수했다. runtime/실호출139입력·corpus144경로/150명시SHA·host8원자료/도구5·baseline910·T4 고정 경계는 불변이다. 문서두문장은 향후 일반 역할 prompt판본을 바꾸므로 역사 고정 smoke를 새 문서 읽기/준수의 실측으로 확대하지 않는다. 검수된 제품·시험·문서·미러28경로를 이번 관리 커밋으로 마감하고 비용캐시2는 제외한다. 원task181파일과 제품원바이트는 manager-evidence/raw-evidence.zip에 보존하며 전건SHA·선별 추적범위는 run:phases/019/manager-evidence/preservation.json에 둔다. 압축만 추적하는 원경로와 stage/commit 행정 수신은 로컬 보관으로 정리 때 사라질 수 있다. 압축은 자동 복원 지시가 아니다.020 배정·관리·기억 추가는 제품 검증 판본을 바꾸지 않는다.
'''
write(RUN/'context.md',c)
plan=before['plan.md'].replace('phase 001~018의 결과','phase 001~019의 결과',1)
plan=plan.replace('## 다음 phase: 019','''019 P02의 A1~A4를 검수했다. 실제 catalog/생산/저장/복원 결속과 양쪽187선택의186passed·권한1skip·exit0를 확인했다. P02 지정 남김을 닫고 symlink 실제 반려 미검사는 G4에 유지한다.28비캐시 제품경로를 관리 마감한다. 근거는019 manager verification.json·review.md다.

## 다음 phase: 020''',1)
a=plan.index('gpt-6.1-sol/high의 document-results'); b=plan.index('## 가까운 후속 배정',a)
plan=plan[:a]+'''gpt-6.1-sol/high의 document-tools 단일 work를 배정한다. P03의 execution_window·scholarly·formal_verifier·preview·submission_contract와 record_map.read_tool을 실제 _context·install_tools·prepare_role_input 결과와 설치 파일에 연결한다. 기본 record_map 실제 반환과 P01/P02·B130~B134를 유지하고 필드 누락/다른 명령 차용·조건부 미설치·console sibling 반려를 기존 준비/설치 시험에서 검증한다.

doc_code와 직접 소비/helper·문서·미러·캐시를 한 task가 소유한다. 공유 상태를 수정하는 제품 작업을 병행하지 않으며 jobs1·한 묶음씩 실행한다. runtime·runner·adapter·Job fixture·corpus·실호출 입력은 고정한다. 같은 최종 관련 선택을 양쪽에서 완결하고 공식 생성/check/skill-only를 확인한다. 새 실호출이나 전체T4 반복은 배정하지 않는다.

018의 제품24경로는 HEAD929fa4cc의 관리 커밋으로 마감됐다. 이번에는019의28비캐시 제품경로를 커밋한다. L01 Q1/Q2는 미정이며 원문byte 기준과 미충족을 유지한다. P04~P11·REVIEW/TRUST·N의 다른 절·남은 의미 질문, 전체일반/freshT3/전수변이·최종review는 별도 후속 책임이다.

'''+plan[b:]
plan=plan.replace('01512·01610·018fixture2의 합24비캐시 제품경로를018 관리커밋으로 마감한다.', '01512·01610·018fixture2의 합24비캐시 제품경로는018 관리커밋a29f3c6a로 마감됐다.')
plan=plan.replace('019가 P02 네owner를 맡고 P03~P11·N01~N03의 다른 미결 절은 후속으로 남긴다.', '019의 P02 네owner를 닫았다.020이 P03 실행 안내/지급 도구를 맡고 P04~P11·N01~N03의 다른 미결 절은 후속으로 남긴다.')
plan=plan.replace('기존22와018fixture2의 합24제품경로를 이번관리커밋에 포함한다.', '기존22와018fixture2의 합24제품경로는018 관리커밋a29f3c6a에 포함됐다.')
plan=plan.replace('| G1/G2 남은 의미 질문', '| G4 조건부 symlink 미검사 |019 관련 양쪽의 Windows1314 skip은 실제 탈출 반려를 입증하지 않았다. 최종 기본전체에서 원문상 환경조건을 판정하고 미검사를 명시한다. |권한이나 G4 기준을 자의 변경하지 않으며 skip을 통과로 세지 않는다. |\n| G1/G2 남은 의미 질문',1)
write(RUN/'plan.md',plan)
write(RUN/'seams.md',before['seams.md']+'''
019의 P02 실제 생산/저장/복원 문서 결속을 검수했다.020은 기존 _context·record_map·prepare_role_input·install_tools의 실행 안내와 지급 도구 경계를 소비한다. 명령/설치파일/오류/조건부 부재는 현 코드가 정본이고 문서 검사용 별도 schema를 제품 계약으로 만들지 않는다. 같은task가 helper와 직접 소비·미러를 소유하며 제품 인터페이스를 개정하지 않으므로 S항목·provides/uses는 추가하지 않는다. record_map 기본 반환, preview 지급과 실제 검증 결과의 차이, scholarly 설정과 실호출의 차이를 유지한다.
''')

assert 'convention_version: 27' in (R/'기억/세칙.md').read_text(encoding='utf-8')
assert sorted((R/'기억/layer1').glob('M-*.md'))[-1].name=='M-0568.md'
write(R/'기억/layer1/M-0569.md','''---
id: M-0569
layer: 1
title: 결과 문서 결속을 검수하고 실행 안내와 지급 도구를 배정함
convention_version: 27
---

## 맥락

phase 019는 P02의 원자료·과제 결과 필드를 AST 조립에서 실제 catalog·생산·저장·복원 검사로 바꿨다. manager는 현재2675파일과 양쪽187개 선택/실제 결과를 대조해 지정 A1~A4를 승인했다. 양쪽186passed와 기존 symlink 권한1314의1skip을 구별하며 전체 일반·freshT3·전수변이·나머지 의미/문서·최종review는 유지한다. 검수된28비캐시 제품경로를 마감하고020 P03을 배정한다.

## 판단에 남길 조건

동일 바이트의 다른 실행 경로를 차용한 반례는 파일 해시만으로 소유권을 증명할 수 없음을 구체화한다. 검사는 이번 workspace와 task/execution 좌표, 저장 artifact와 snapshot을 함께 대조한다. 수제 results의 복원과 실제 _apply의 생산/비중복은 서로 다른 시험이 맡고600k 보고·파일의 기존 개정/재개 흐름을 재사용했다. 일반 defer의 AST 검사는 담당 method와 문서 검사 호출의 존재만 확인하며 최종 결과 의미는 실제 실행 단언이 맡는다.

새로운 문서 문구는 미래 일반 역할 prompt를 바꾸지만 역사 고정 smoke 입력은 그대로다. 기존 실호출은 승인된 성질만 유지하고 새 문서의 읽기/준수 증거로 넓히지 않는다. 다음 P03도 지급 명령·설치파일·최종 입력 결속과 실제 외부 호출 성공을 구별하도록 배정했다. 공통 doc_code와 미러/캐시를 동시에 바꾸는 제품 task는 독립 검증이 어려워 하나로 묶었다.

원근거 진입점은 docs/do-math/continuous-development-2026-10-13/phases/019/manager.json과 manager-evidence/verification.json·review.md다. 원task181파일과28제품 바이트는 raw-evidence.zip에 추적하고 전건SHA·선별 추적경로는 preservation.json에 둔다. 압축만 추적하는 중복 snapshot 원경로 및 stage/commit 행정 수신은 로컬 보관으로 정리 때 사라질 수 있다. 압축은 복원 지시가 아니다. 원report와 역사 실패는 수정하지 않았다.
''')
index=R/'기억/색인.md'
write(index,index.read_text(encoding='utf-8').replace('## layer-1\n','## layer-1\n\n- M-0569 [결과 문서 결속을 검수하고 실행 안내와 지급 도구를 배정함] -- 실제 생산/복원·양쪽186통과1skip 검수, P02 종결·020 P03 최종 입력과 설치 연결\n',1))
updates=[]
reasons={'C2':'019의 지정 완료·판본/회귀와 미검사 범위를 추가했다.',
 'C5':'현재 단일 작업을020 P03으로 바꾸고 공유 helper/미러/실행 자원의 소유를 명시했다.',
 'C8':'사용자 지정 모델을020에도 적용했다.',
 'C9':'B110~B114의 P02 한정 처분을 추가하고 다른 slice를 보존했다.',
 'C10':'019의 예정 작업을 실제 완료와020의 한정 책임으로 교체했다. 기존 P/N/L01 조건은 보존했다.',
 'C11':'019 symlink 권한 skip을 G4의 별도 미검사 책임으로 추가했다.',
 'C12':'139입력 등 보존과 미래 prompt 영향,28제품 마감/원근거 보존 경계를 추가했다.'}
for cid,reason in reasons.items():
    updates.append({'item':cid,'action':'amend','destination':['run:context.md#'+cid],
                    'reason':reason,'evidence':[ev('verification.json'),ev('review.md'),'run:phases/020/tasks/document-tools/objective.md']})
manager={'next':'020','decision':'''019 document-results의 A1~A4를 검수해 P02 지정 남김을 닫는다. 원 report 형식, actual source diff, 현재2675파일·허용30변경과 양쪽 동일187ID의186passed/1skipped/exit0를 대조했다. 실제 catalog/생산/저장/복원 검사와 담당 위임, 초기 실패의 최종 해소를 확인했으며 수제fixture의 물질화와 _apply 생산 근거는 구별한다.

Windows1314 symlink skip은 실제 탈출 반려나 G4 통과로 세지 않는다. runtime139·corpus144/150SHA·host8/tools5·baseline910·T4 경계는 불변이고 두 문장 변경은 미래 역할 prompt에 영향을 준다. 이전 고정 smoke의 승인된 성질만 재사용하며 새 문서 준수의 실측으로 확대하지 않는다. 검수된28비캐시 제품경로를 관리 마감한다.

020은 P03 실행 안내와 지급 도구 여섯 소유자를 실제 설치 후 최종 입력에 연결하는 단일 work다. 현재 doc_code·install_tools·_context에서 경계를 확인했다. 공유 helper/미러/캐시·시험 판본이 겹쳐 다른 제품 task와 병렬화하지 않는다. L01 결정과 독립적인 작업이고 새 외부 호출/전체T4 반복은 필요하지 않다. 직전 phase가 work이며 다른 의미/문서와 G4~G6/G8이 남아 종료 조건은 충족하지 않는다.''',
 'reports':[{'task':'document-results','state':'read','detail':'report 형식 검사와 A1~A4의 원자료/현재 코드 대조를 통과했다. 지정 complete를 승인하고 symlink 조건부 미검사·최종 G의 남김은 유지한다.',
             'evidence':[T+'report.json',ev('report-check.json'),ev('verification.json'),ev('review.md')]}],
 'dispositions':[
 {'item':'019/document-results/F1','action':'resolve','destination':['run:context.md#C9','run:context.md#C10','run:plan.md'],
  'reason':'실제 생산/복원/문서 담당과 원결과를 검수해 P02 slice만 종결한다. PR24·다른 packet은 유지한다.',
  'evidence':[ev('verification.json'),ev('review.md'),T+'evidence/binding-review.md']},
 {'item':'019/document-results/F2','action':'carry','destination':['run:context.md#C11','run:plan.md','run:phases/020/tasks/document-tools/objective.md'],
  'reason':'P02 필수 성질은 실행됐으나 실제 symlink 탈출 반려는 권한1314로 미검사다. G4의 원문상 조건부 환경 판정에 남기며 통과나 권한 변경으로 처리하지 않는다.',
  'evidence':[ev('verification.json'),T+'evidence/c/report.json',T+'evidence/m/report.json']},
 {'item':'019/document-results/F3','action':'resolve','destination':['run:context.md#C12','run:plan.md'],
  'reason':'현재 바이트/Git clean·명시SHA·도구/원자료를 검수해 보존 사실을 승인한다. 기존 성질만 재사용하고 미래 prompt 영향과 최종 판본 관문은 유지한다.',
  'evidence':[ev('verification.json'),T+'evidence/preservation.json',ev('review.md')]}],
 'context_updates':updates,'plan_update':'019 P02를 지정 완료로 닫고020 P03 실행 안내/지급 도구를 단일 work로 배정했다. symlink 조건부 미검사를 G4에 명시하고018 제품마감을 실제 HEAD929fa4cc로 정정했다. 나머지 의미/문서·L01·전체일반/freshT3/전수변이·최종review의 선행 관계와 책임은 보존했다.',
 'seam_updates':[],'completion':None}
save(P/'manager.pending.json',manager)
diff=''.join(''.join(difflib.unified_diff(before[n].splitlines(True),(RUN/n).read_text(encoding='utf-8').splitlines(True),fromfile=n+' before 019',tofile=n+' after 019')) for n in before)
write(O/'common-docs.diff',diff)
assert before['context.md'].split('## C2 ')[0]==c.split('## C2 ')[0]
parts=[R/'services/continuous-development/protocol.md',RUN/'context.md',RUN/'plan.md',RUN/'seams.md',
       O/'review.md',P/'manager.pending.json',N/'phase.json',N/'tasks/document-tools/objective.md',R/'기억/layer1/M-0569.md']
write(O/'handoff-draft.md','\n\n'.join('# 파일: '+p.relative_to(R).as_posix()+'\n\n'+p.read_text(encoding='utf-8') for p in parts))
save(O/'draft-sources.json',{p.relative_to(R).as_posix():__import__('hashlib').sha256(p.read_bytes()).hexdigest() for p in parts})
print('Prepared 020/document-tools, amended context/plan/seams, 019 manager.pending and M-0569.')

"""Prepare reviewable manager records and the next bounded assignment."""
import difflib
import hashlib
import json
from pathlib import Path
import re

R=Path('C:/math'); RUN=R/'docs/do-math/continuous-development-2026-10-13'
O=Path(__file__).resolve().parent; E=RUN/'phases/024/tasks/document-waits/evidence'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def text(p,v): p.write_text(v,encoding='utf-8',newline='\n')
v=read(O/'verification.json')
assert v['products_to_commit']==28 and v['original_task_files_unchanged']==352
sections=read(E/'section-semantic-review.json')
old=read(RUN/'phases/022/tasks/review-delivery/evidence/section-name-decisions.json')
tested={r['id'] for group in read(E/'c2/report.json')['reports'] for r in group['rows'] if r['outcome']=='passed'}
for row in sections['exact_sentences']:
 assert sha(R/row['current_file'])==row['current_sha256']
 before=next(x for x in old if x['section']==row['section'] and x['token']==row['token'])
 assert before['sentences']==row['sentences']
 assert all(s in (R/row['current_file']).read_text(encoding='utf-8') for s in row['sentences'])
for row in sections['mapping'].values():
 for selector in row['tests']: assert any(i==selector or i.startswith(selector+'.') for i in tested),selector
policies=read(E/'policy-name-decisions.json')
for row in policies:
 for definition in row['definitions']:
  assert sha(R/definition['path'])==definition['sha256']
  for excerpt in definition['excerpts']:
   assert excerpt['text'] in (R/definition['path']).read_text(encoding='utf-8')
unique=set(s for row in sections['exact_sentences'] for s in row['sentences'])
assert len(unique)==4
save(O/'section-check.json',dict(name_rows=len(sections['exact_sentences']),unique_paragraphs=len(unique),policies=len(policies),
 current_sentences_equal=True,prior_sentences_equal=True,referenced_tests_present_and_passed=True,definition_excerpts_current=True,
 correction='Task wording eight sentences means eight name-indexed rows across four unique paragraphs; no full N-section or policy-semantic completion.'))
save(O/'manager-check-correction.json',dict(initial_exit_code=1,
 observed='FileNotFoundError at verify.py funcs(E/original/path): phase 024 has no original/helper copy.',
 correction='Read phase 023 raw-evidence.zip and require its helper SHA to equal phase 024 start.json. No task artifact or product changed.',
 initial_script='run:phases/024/manager-evidence/verify.initial.py',final_exit_code=0))

next_dir=RUN/'phases/025'; task_dir=next_dir/'tasks/document-trust'
assert not (next_dir/'phase.json').exists()
(task_dir/'evidence').mkdir(parents=True,exist_ok=True); (next_dir/'logs').mkdir(exist_ok=True)
text(next_dir/'logs/.gitkeep','')
tests=['boundary/test_engine_cli.py','unit/test_engine_trace_report_corruption.py','unit/test_role_input_packaging.py',
 'unit/test_storage_record_queries.py','unit/test_storage_report_projections.py','structure/test_doc_code.py',
 'support/doc_code.py','support/engine_context.py','support/trust_inputs.py',
 'sim/test_toolchain_tools.py','boundary/test_knowledge_lean_verifier.py','unit/test_trust_environment.py',
 'unit/test_toolchain_records.py','sim/test_trust_transition.py','sim/test_formal_wait_contract.py',
 'unit/test_knowledge_formal_runtime.py','boundary/test_knowledge_formal_consumer.py','boundary/test_knowledge_formal_runtime.py']
docs=['references/초기화-운전.md','references/초기화-효율과-정비.md','references/CLI-실행-계약.md']
sources=['formal.py','trust_validation.py','trust_inventory.py','trust_engine.py','formal_engine.py','formal_environment.py','project.py']
# Actual source names are resolved below; do not send invented input paths.
sources=[p for p in sources if (R/'.claude/skills/do-math/scripts/do_math'/p).is_file()]
inputs=['run:sources/user-decisions.md','run:sources/model-policy-2026-10-14.md','run:sources/document-batching-2026-10-14.md',
 'run:phases/001/tasks/document-closeout/evidence/followup-packets.json',
 'run:phases/001/tasks/document-closeout/evidence/binding-inventory.json',
 'run:phases/001/tasks/closure-map/evidence/prior-review-state.json',
 'run:phases/024/tasks/document-waits/report.json',
 'run:phases/024/tasks/document-waits/evidence/selection-decisions.json',
 'run:phases/024/tasks/document-waits/evidence/policy-name-decisions.json',
 'run:phases/024/tasks/document-waits/evidence/binding-review.md',
 'run:phases/024/tasks/document-waits/evidence/preservation.json',
 'run:phases/024/manager-evidence/verification.json','run:phases/024/manager-evidence/source-inspected.json',
 'run:phases/024/manager-evidence/return-check.json','run:phases/024/manager-evidence/review.md',
 'run:phases/012/tasks/lean-smoke/evidence/review.md','run:phases/016/tasks/t4-fixture-repair/report.json',
 'repo:docs/do-math/시험-재편-2026-09-29/설계.md','repo:docs/do-math/시험-재편-2026-09-29/조사/결함-범주.md',
 'repo:.claude/skills/do-math/AGENTS.md','repo:.claude/skills/do-math/scripts/tests/시험-지침.md',
 'repo:.claude/skills/do-math/scripts/이음새-정본.md','repo:.claude/skills/writing-skills/references/멀티런타임_동기화.md']
inputs += ['repo:.claude/skills/do-math/'+p for p in docs]
inputs += ['repo:.claude/skills/do-math/scripts/do_math/'+p for p in sources]
inputs += ['repo:.claude/skills/do-math/scripts/tests/'+p for p in tests]
writes=[tree+'/skills/do-math/'+p for tree in ('.claude','.agents')
 for p in docs+['scripts/tests/'+p for p in tests]+['scripts/tests/.timings.json','scripts/tests/.timings-t3.json']]
for ref in inputs:
 if ref=='run:phases/024/manager-evidence/review.md': continue  # Written below before handoff validation.
 prefix,path=ref.split(':',1); assert ((R if prefix=='repo' else RUN)/path).is_file(),ref
save(next_dir/'phase.json',dict(kind='work',purpose='P08의 실제 도구 사슬·프로젝트·환경 검사와 직접 연결된 N 문장을 한 문서 검사 변경으로 통합한다.',
 tasks=[dict(id='document-trust',model='gpt-6.1-sol',effort='high',inputs=inputs,writes=writes,provides=[],uses=[])]))
text(task_dir/'objective.md','''## 목적과 역할

G1/G2/G3의 남은 DOC-RETURN-TRUST/P08을 닫는다. project, toolchain, environment_check의 AST 조립을 현재 실제 반환과 직접 소비 검사에 연결한다. 같은 소유자를 설명하는 N01-274·N01-279·N01-281의 지정 문장을 함께 처리해 공통 helper·문서 순회·미러·회귀를 한 번 통합한다. 024의 P09/P11과 지정 재시도 문장은 검수됐으며 다시 구현하지 않는다. 최종 review가 아닌 한정 work다.

## 완료 조건

### A1 현재 문장과 경계·반례

시작 skills/diff를 024 manager source-inspected의 2675파일과 대조하고 기존 dirty를 보존한다. followup-packets P08의 세 원문 좌표를 현재 제목/문장으로 연결한다. field_schemas의 project/toolchain/environment_base 조립이 실제 값·null·분기별 부재를 입증하지 못하는 지점을 확인하고 수리 전 최소 반례를 보존한다. 기대값은 원문 계약과 독립 입력에서 얻으며 현재 생산값의 복사나 AST 모양을 의미 증거로 쓰지 않는다.

### A2 실제 project와 toolchain

현재 formal._project_identity/inspect_toolchain과 기존 실제 Git/파일·Lean/Lake 경계를 사용한다. non-Lake의 project=None과 Lake의 manifest_hashes/source_identity/search_paths를 구별한다. 프로젝트의 추적 트리·작업 트리 diff·미추적 입력, 입력 변경의 검색 경로 재관측, 동일 입력의 재사용 및 환경 변수 비상속을 기존 검사와 대조하고 빠진 축만 보완한다. 실제 실행파일/명령·version·hash·적재 검사기·.exe/.dll과 프로젝트 판본의 결속을 현재 toolchain_errors 및 직접 소비에 연결한다. 다른 객체의 동명 필드, 중첩 키 삭제/변조·소유자 차용을 반려한다. 실제 inspect 함수나 프로젝트 생산자를 대역으로 가리지 않는다. 외부 host 대역 시험과 실 Lean/Lake/Job 검사를 구별하고 실제 반환 표본을 보존한다. 공유 portable 설치·기록을 바꾸지 않고 자기 전용 프로젝트를 쓴다.

### A3 실제 환경 검사와 분기별 부재

check_environment가 실제 기록/판정 파일을 읽어 생산하는 verified, invalid, rebind를 문서와 연결한다. 성공·재결박에 changed_files가 없는 경우를 누락으로 만들지 않는다. 파일 추가/삭제/변경에 따른 changed_files·changed_file_count, 목록 50개 제한, 기록 부재/파손·identity 불일치·현재 기준 mismatch를 실제 소비와 원문 조건으로 구별한다. 오류 문자열을 모두 똑같은 invalid로 뭉개지 않는다. 기준을 자동 기록하지 않음, rebind의 이전/현재 결박과 recorded_at, 실패 시 컴파일 미시작·이전 환경 보존은 기존 담당 검사로 확인한다. trust_fixture는 실제 기록 생산자를 쓰되 host 대역과 실제 host 검증의 책임을 분리한다. 수제 문서용 schema나 필수 출력의 합집합으로 분기 차이를 감추지 않는다.

### A4 관련 문장과 기존 변경의 한정 처분

N01-274 「5. 툴체인 기록을 등록한다」 중 등록 요청/기록/현재 기준과 toolchain.project.search_paths 문단, N01-279 「지문 불일치와 재기록」 중 environment_check.changed_files·identity_errors 문단과 재결박 세 조건 문단, N01-281 「판정 파일, 판본 식별과 지문」 중 판본 식별/project.source_identity 문단을 같은 실제 소비·기존 시험에 연결한다. 기록 등록·활성화·컴파일·사람의 재기록 권한을 구별하고 전체 N 절·신뢰 전환 정책을 일괄 완료로 바꾸지 않는다. 문서가 현재 약속을 오해하게 하면 허용 문서의 해당 문장만 교정하고 의미/권한 변경은 정확 반례로 반환한다.

B110~B114 중 이 세 owner의 실제 도입 hunk·현재 소비·존재 원보고와 관련 PR24 slice를 대조한다. formal/Git의 B38 및 012/016 검수는 같은 성질·판본에서 재사용하고 없는 원보고 counts를 합산하지 않는다. 마지막 소비가 사라진 AST helper는 실제 호출부를 확인해 제거 여부를 판단하며 다른 소비자가 있으면 유지한다. 기존 P01~P07/P09~P11·PURE의 owner/오류/전문 단일 지급·봉인 복원은 보존한다. 024 F2의 정책 다섯 이름과 다른 N/L01의 미해결 의미는 이 범위에서 닫지 않는다.

### A5 통합 회귀와 보존·인도

공통 doc_code/engine_context의 실제 문서 순회 담당과 변경한 직접 소비를 기준으로 최종 선택을 정하고 정본/미러에서 같은 선택을 완결한다. 이전 254 또는 460개를 기계적으로 누적하지 않는다. 제외에는 비소비·판본·기존 보호성질 근거를 남긴다. 새 위임이 있으면 정확 owner와 실제 문서 검사 담당, 누락/오기·없는 메서드·다른 owner 비우회를 검사한다. selected/고유row/exit·전후 Python/문서 SHA와 실제 반환·오류 원자료를 보존한다.

공식 미러의 사전 영향 계획·생성·캐시 동기화·--check·skill-only를 완료한다. 024 기준 runtime/실호출139입력·고정258경계·corpus144/명시SHA150/Git raw-clean·host8/도구5·baseline910 및 완료 원task352파일은 보존한다. 문서 변화가 미래 prompt/설치 문서 해시에 미치는 영향과 과거 실호출의 불변 하위 성질 재사용을 구별한다. 실제 설치 읽기·컴파일이 필요한 검사는 허용하지만 공유 설치/신뢰 기준의 승인·수정이나 새 유료/예약/학술 호출은 배정하지 않는다. 권한1314 symlink 미검사, L01 Q1/Q2·원문 byte 요구와 최종 전체 관문은 그대로 남긴다.

## 판단과 경계

제품 runtime·schema·포트·runner/adapter·Job fixture·corpus·공유 설치와 기존 연구는 고정한다. writes의 문서/시험/지원만 수정한다. 원문과 실제 runtime이 충돌해 허용 범위를 넘어서는 수리가 필요하면 최소 입력·기대/실제·필요 파일·영향 G를 findings에 반환한다. 문서나 기대값을 약화해 통과시키지 않는다. 새 범용 추론기·등록부·중복 제품 schema를 추가하지 않는다.

한 담당자가 helper·직접 소비·미러/캐시를 소유한다. 다른 task의 미완성 결과나 동시 source 수정에 의존하지 않는다. 공식 검사는 jobs1·전체 worker3 이하·동시에 한 묶음이며 검사 중 소스를 고정한다. parent TEMP/TMP/TMPDIR는 저장소 밖의 짧은 전용 경로로 정하고 상위 Git 미발견을 확인한다. output도 짧게 정하며 실제 resource child cwd를 기록한다. 긴 경로 오류를 skip/무조건 retry로 처리하지 않는다. 시간은 소프트 기준이다. Git stage/commit/reset/checkout/push, graphify 갱신, 기존 연구 재개/삭제는 수행하지 않는다.

## 검증 방법

cwd C:\\math. Python C:\\Users\\wogud\\AppData\\Local\\Programs\\Python\\Python312\\python.exe. 공식 .claude/skills/do-math/scripts/run_tests.py에 -u -B --jobs 1 --output <자기 evidence의 새 짧은 경로>를 사용한다. 도구의 대기 만료는 시험 종료가 아니며 실제 PID·시각·exit·argv/cwd/환경·stdout/stderr를 보존한다. 진행 result는 read_bytes_shared로 읽는다.

직접 진입점은 unit.test_trust_environment, unit.test_toolchain_records, sim.test_toolchain_tools.HostIdentityTests, boundary.test_knowledge_lean_verifier의 ToolchainContractTests/LakeEnvironmentTests다. 신뢰 전환/형식 대기의 기존 소비는 sim.test_trust_transition, sim.test_formal_wait_contract와 지정 formal runtime/consumer에서 정확 성질을 선별한다. 정본/미러의 실제 설치 검사는 한 번씩 순차 수행하고 없는 설치·권한은 정확 미검사로 남긴다. 전체 Lean/T4나 전체 일반/T3/변이를 이번 좁은 문서 변경의 기본 회귀로 반복하지 않는다. 이미 통과한 같은 검사는 새 변경/실패/근거 무효화 없이 반복하지 않는다.

report의 A1~A5, 실제 changes와 모든 findings, 재사용/미검사를 작성하고 지정 Python으로 services/continuous-development/check.py report C:\\math C:\\math\\docs\\do-math\\continuous-development-2026-10-13 025 document-trust 를 통과한다. 마지막 응답에 status와 report 경로를 알린다.
''')

text(O/'review.md','''# 024 manager 검수

document-waits의 report 전문을 읽고 형식 검사 및 원근거 대조를 통과시켰다. A1~A5 complete를 지정 범위에서 승인한다. 시작 2675파일은 023 검수본과 같고 종료/현재 SHA가 전건 일치한다. 30변경은 writes/report와 같으며 28개 비캐시 제품·문서·시험·미러를 관리 마감한다. runtime은 바뀌지 않았다.

정본 c2와 미러 m의 동일254선택/고유row가 모두 passed·실제 exit0이고 각875 Python과 실행 전후 비캐시 파일이 같다. 원 관찰 각107개에서 계획 대기의 queue/시각/우회 조건을 독립 재계산했고 ready 결정의 정확 자료형/값을 확인했다. 각18개 최종 제안 입력을 재귀 검사해 전문1을 확인했다. 실제 입력/기대/현재성의 나머지 음성 사례는 현재 시험과 원 row를 함께 대조했다. 새 구조 위임은 owner/담당 호출 검증이며 의미는 실제 실행이 맡는다.

red 두 subTest, focus의2failed/1error, corrected의1failed, 관찰자 c의19error/25failed/62not_run은 역사 실패로 보존한다. 마지막 c2는 c와 제품875 Python/254선택이 같고 관찰자의 inspect.unwrap 교정 뒤 통과했다. 초기 실패의 정확 ID가 양쪽 최종 passed로 이어지는 것을 failure-mapping.json에 기록했다. 추가 resource1의 공식 통과/worker0과 원 audit의 두 cwd141자를 대조했다. 관리자 첫 검산은 존재하지 않는 original/helper 경로를 가정해 실패했으며, 023 압축의 실제 원바이트와 024 시작 SHA를 대조하도록 고쳤다. 제품이나 task 근거는 수정하지 않았다.

022 F5의 나머지 정확 문장을 현재 문서·소비·기존 검사와 대조해 종결한다. 원보고의 ‘8문장’은 이름별8항목이며 고유 문단은4개다. 이는 N01-237/260·N02-002 전체절의 의미 인증이 아니다. 024 F2의 정책 다섯 이름은 정의/소유를 확인해 유지하지만 전체 의미 질문은 context/plan에 carry한다. model_policy의 모듈 이름과 잠금 불일치 실패 분류도 구별한다.

B113의 P09/P11 AST만 실제 경계 검사로 교체한 판단과 D-06 초기 장벽 제거 유지 판단을 승인한다. 기존 helper의 다른 함수와 존재하는 B110~B114 원보고7개의 SHA를 대조했다. PR24 전체와 과거 counts를 새 성공으로 올리지 않는다. runtime/실호출139입력·고정258경계·144corpus/150명시SHA/Gitraw-clean·host8/도구5·baseline910·023원task891파일은 불변이다. 새 두 문서 문단의 미래 prompt/설치 해시 영향 때문에 과거 실호출은 불변 하위 성질만 재사용한다. 이번 선택에는 symlink 시험이 없고 기존1314 미검사는 남는다.

다음025는 P08의 project/toolchain/environment_check 및 같은 소유자의 N01-274/279/281 지정 문장을 한 work로 묶는다. 같은 helper·문서 순회·실 Lean/Lake·미러/캐시의 통합 담당이 필요하고 기존 packet이 종료 질문을 충분히 주므로 별도 병렬 조사를 만들지 않는다. 정책 전체·그 밖의 N/L01·G4~G8 최종 관문은 유지한다. 완료 선언은 하지 않는다.

추적 보존 진입점은 manager.json, verification.json, return-check.json, section-check.json, preservation.json과 raw-evidence.zip이다. task352파일과28제품 원바이트를 압축에 보존하며 선별 원경로만 직접 추적한다. 압축만 추적하는 snapshot/반환/scratch 원경로와 진행 로그·stage/commit 수신은 로컬 보관으로 정리 때 사라질 수 있다. 압축은 복원 지시가 아니다.
''')

before={n:(RUN/n).read_bytes() for n in ('context.md','plan.md','seams.md')}
for n,b in before.items(): (O/(n+'.before')).write_bytes(b)
c=before['context.md'].decode('utf-8')
def append_section(cid,paragraph):
 global c
 match=re.search(r'^## '+cid+r'\b.*?(?=^## C\d+\b|\Z)',c,re.M|re.S); assert match
 c=c[:match.end()]+paragraph+'\n\n'+c[match.end():]
append_section('C2','phase 024 document-waits의 A1~A5 complete를 검수했다. report 검사 뒤 시작2675파일과023 검수본 동일, 종료/현재 전건 SHA 일치와 허용30변경(비캐시28·비용캐시2)을 확인했다. 최종 정본/미러 동일254선택/고유row는 전부passed·exit0이며 각875Python과 전후판본을 대조했다. 실제 반환 각107개와 제안 입력 각18개의 전문1, resource 추가1건/worker0·실제cwd141자를 원자료에서 확인했다. red/focus/corrected/관찰자c의 실패는 최종 정확ID와 구별해 보존한다. 관리자의 초기 원본 경로 가정 오류도 기록하고023압축/024시작SHA 대조로 고쳤다. task352파일과023원task891파일은 불변이다. 근거는 run:phases/024/manager-evidence/verification.json·return-check.json·review.md다. 지정 범위 완료이며 전체G 완료가 아니다.')
old_par=next(p for p in c.split('\n\n') if p.startswith('phase 001~023의 task 세션'))
c=c.replace(old_par,'phase 001~024의 task 세션은 종료됐다.025 document-trust 단일 work가 P08의 project/toolchain/environment_check와 N01-274/279/281의 직접 관련 문장을 통합한다. 공유 doc_code/engine_context·문서 순회·실 Lean/Lake·미러/캐시를 한 담당자가 소유한다. 기존 packet과 현 코드가 종료 질문을 제공하므로 별도 병렬 조사는 배정하지 않는다. runtime/runner/adapter·Job fixture·corpus·공유 설치/신뢰/연구는 고정하며 자기 전용 fixture에서 기존 실제 설치 검사를 순차 수행한다. jobs1·전체worker3 이하·동시에 한 묶음·소스 고정과 변경 영향에 따른 최종 선택을 유지한다. 정책 전체·다른N/L01과 최종 관문은 남는다.')
append_section('C8','024의 gpt-6.1-sol/high 작업을 검수했고025 document-trust에도 같은 model/effort를 명시한다. manager 설정과 제품 공급자 실호출 모델은 구별한다.')
append_section('C9','024의 B113/P09·P11 AST 결속 교체와 D-06의 초기 준비 장벽 제거 유지 판단을 승인한다. 실제 hunk·현재 소비·존재7원보고 SHA와 기존 helper 함수 보존을 대조했다. 지정 slice만 닫으며 PR24 전체·다른hunk·역사counts의 새 성공 합산은 하지 않는다. 근거는 run:phases/024/manager-evidence/history-check.json·review.md와 원task binding-review.md다.')
append_section('C10','024 F1의 P09/P11 지정 남김을 닫는다. 실제 결정/자료형/현재성·queue 대기/정확 시각·우회/초기 사건 소유와 문서 반례를 검수했다.022 F5의 남은 재시도/운영처분 문장도 현재 소비에 연결해 종결한다. 정확히는 이름별8항목·고유4문단이며 N 세 절 전체의 인증은 아니다.024 F2의 conversation_loss_policy/disconnect_policy/model_policy/external_policy/adopt_default_review_policy는 정의·소유 확인으로 유지하되 의미 질문은 기존 담당 범위로 남긴다.025는 P08 세 owner와 N01-274/279/281의 같은 경계 문장을 맡는다. 다른 N·L01 Q1/Q2·원문byte 미충족은 그대로다. 근거는 run:phases/024/manager-evidence/section-check.json·review.md 및 run:phases/025/tasks/document-trust/objective.md다.')
append_section('C11','024 F3의 최종 양쪽254선택에는 symlink 시험이 없으며 기존 Windows1314 실제 탈출 반려 미검사는 해소되지 않았다. G4 기본전체에서 원문상 환경조건을 판정한다. 이번 부분 통과로 G4~G6·G7 최종판 연결·G8을 닫지 않는다. 근거는 run:phases/024/manager-evidence/verification.json이다.')
append_section('C12','024 F3의 보존과 불변 하위경계 재사용을 검수했다.023 기준139실호출입력·258고정경계·144corpus/150명시SHA/Git raw-clean·host8/도구5·baseline910과 원task891파일은 불변이다. 두 문서 문단은 미래 역할 prompt/설치 문서 hash를 바꾸므로 과거 전체 설치·모델 독해의 증거로 확대하지 않는다. 검수한28비캐시 제품/시험/문서/미러를 이번 관리 커밋으로 마감한다.024원task352파일·28제품 원바이트는 raw-evidence.zip에 보존하며 전건SHA와 선별추적범위는 run:phases/024/manager-evidence/preservation.json에 둔다. 압축만 추적하는 반환/snapshot/scratch의 원경로와 진행 로그·stage/commit 행정 수신은 로컬 보관으로 정리 때 사라질 수 있으며 압축은 복원 지시가 아니다.025배정·관리/기억 추가는 검증한 제품판본을 바꾸지 않는다.')
text(RUN/'context.md',c.rstrip()+'\n')
p=before['plan.md'].decode('utf-8').replace('## phase 001~023의 결과와 현재 상태','## phase 001~024의 결과와 현재 상태')
start=p.index('## 다음 phase: 024'); end=p.index('## 가까운 후속 배정과 선행 관계',start)
p=p[:start]+'''024 A1~A5를 검수했다. P09/P11과022 F5의 지정 나머지8이름/4문단을 닫았다. 양쪽 동일254선택 전부passed·각875Python·실제반환107/제안18의 전문1과 불변 경계를 확인했다.28비캐시경로를 마감한다. 정책 다섯 이름의 전체 의미, 다른N/L01·권한skip·최종관문은 남는다. 근거는024 manager verification.json·section-check.json·review.md다.

## 다음 phase: 025

gpt-6.1-sol/high document-trust 단일 work에 P08의 project/toolchain/environment_check와 N01-274/279/281의 직접 관련 문장을 묶는다. 실제 formal inspection/프로젝트/환경 검사와 기존 소비 회귀로 AST 조립을 교체한다. project=None, 분기별 changed_files 부재·실파일 변화, 재결박, 검색경로/판본의 독립 기대를 구별한다. 등록·활성화·컴파일·사람의 재기록 권한은 현재 계약대로 유지한다.

공유 helper·문서 순회·실 Lean/Lake·미러/캐시를 한 담당자가 통합한다. 기존 packet과 현재 코드가 한정 종료 질문을 주므로 독립 조사 task는 추가하지 않는다. 최종 관련 선택은 실제 소비/변경 영향으로 정하고 이전254/460개를 기계적으로 누적하지 않는다. runtime·공유 설치/신뢰는 고정한다. P01~P07/P09~P11·PURE와 기존 전문1/봉인복원은 보존한다. 024 F2 정책 전체·그 밖의 N/L01 Q1/Q2·원문byte 미충족·G4 권한skip 및 전체일반/freshT3/전수변이/G7 최종판연결/최종review는 후속 책임이다.

'''+p[end:]
old_par=next(x for x in p.split('\n\n') if x.startswith('**023 manager의 묶음 결정:**'))
p=p.replace(old_par,'**024 manager의 묶음 결정:** P09/P11과022 F5의 나머지 지정 문장을 검수해 닫고 P08과 같은 도구 사슬·신뢰 문장을025에 묶는다. 새 문서번호별 반복 배정이나 공유파일 병렬 수정은 하지 않는다. 마지막 문서 AST 소비가 실제 사라지는지도 같은 담당자가 판정한다.024 F2 정책 다섯 이름의 전체 의미와 다른 N은 기존 완료 범위를 뺀 정확 종료 질문으로 남긴다.025 결과 뒤 다음 범위를 정한다.')
p=p.replace('024가P09/P11과F5의입력초과/운영처분정확문장을맡고P08/TRUST·다른N은후속으로유지한다.','024 P09/P11과F5의입력초과/운영처분지정문장은검수했다.025가P08/TRUST·같은owner의N문장을맡고024 F2정책전체·다른N은후속으로유지한다.')
text(RUN/'plan.md',p)
s=before['seams.md'].decode('utf-8')+'\n024의 실제 조건/대기 문서 결속을 검수했다.025는 기존 formal._project_identity/inspect_toolchain 및 trust_validation.check_environment와 trust_inventory의 실제 생산/소비를 사용한다. project의 null, 환경 검사 분기별 부재·오류·재결박 및 등록/활성화/컴파일 권한은 현 함수·공유 schema가 정본이다. 같은 task가 helper·소비 시험·미러를 소유하고 제품 인터페이스를 개정하지 않으므로 S항목·provides/uses는 추가하지 않는다. runtime 수리가 필요하면 정확 반례를 반환한다.\n'
text(RUN/'seams.md',s)
save(O/'common-before-sha.json',{n:hashlib.sha256(b).hexdigest() for n,b in before.items()})
save(O/'common-after-sha.json',{n:sha(RUN/n) for n in before})
text(O/'common-docs.diff',''.join(''.join(difflib.unified_diff(b.decode('utf-8').splitlines(True),(RUN/n).read_text(encoding='utf-8').splitlines(True),fromfile=n+' before',tofile=n+' after')) for n,b in before.items()))

base='run:phases/024/manager-evidence/'
report_ref='run:phases/024/tasks/document-waits/report.json'
manager=dict(next='025',decision='024 document-waits의 A1~A5를 report 형식과 실제 코드/원출력/판본 대조로 승인한다. 양쪽254개 전부passed와 실제 반환·전문1을 확인했으며 초기 관찰자/fixture 실패는 역사 기록으로 유지한다. 022 F5의 나머지는 이름별8항목/고유4문단의 한정 소비 검증으로 종결하고 N 전체 의미와 구별한다.28비캐시 제품 변경을 관리 마감한다.\n\n다음025는 P08 세owner와 같은 신뢰/판본 문장을 단일 work로 통합한다. 공유 helper·직접소비·실 Lean/Lake·미러/캐시를 한 담당자가 소유하며 기존 packet이 종료 질문을 제공하므로 별도 병렬 조사 없이 반복 관리/회귀를 줄인다.024 F2 정책전체·다른N/L01·권한1314 미검사와 G4~G8 최종관문은 유지한다. 직전 phase는 work이고 전체 완료 근거가 없으므로 종료하지 않는다.',
 reports=[dict(task='document-waits',state='read',detail='전문을 읽고 report 검사를 통과했다. A1~A5 complete를 원근거로 검수했으며 task352파일과 이전891파일을 보존했다. 30변경/28비캐시, 양쪽254passed와 각875Python, actual107/제안18을 확인했다. 정확 범위와 원실패/문장 계수 정정은 review에 기록했다.',evidence=[report_ref,base+'report-check.json',base+'verification.json',base+'review.md'])],
 dispositions=[
 dict(item='024/document-waits/F1',action='resolve',destination=['run:context.md#C9','run:context.md#C10'],reason='P09/P11의 실제 입력·대기와022 F5 지정 문장 소비를 검수했다. 기존 helper/역사 slice를 보존하고28비캐시 변경을 마감한다. 전체PR/G완료가 아니다.',evidence=[base+'verification.json',base+'return-check.json',base+'history-check.json',base+'section-check.json',base+'review.md']),
 dict(item='024/document-waits/F2',action='carry',destination=['run:context.md#C10','run:plan.md'],reason='정책 다섯 이름의 정의/소유 유지 판단은 승인하되 전체 의미는 미검토다. 기존 남은 의미 질문에서 해당 소유자 범위를 유지하며025 신뢰검사로 이를 닫지 않는다.',evidence=['run:phases/024/tasks/document-waits/evidence/policy-name-decisions.json',base+'section-check.json',base+'review.md']),
 dict(item='024/document-waits/F3',action='carry',destination=['run:context.md#C11','run:context.md#C12','run:plan.md','run:phases/025/tasks/document-trust/objective.md'],reason='불변 경계와 녹화는 검산해 한정 재사용한다. 두 문서의 미래prompt/설치 영향, 기존symlink 미검사와 미실행 최종관문은 후속에 유지한다.',evidence=[base+'verification.json',base+'review.md']),
 dict(item='024/document-waits/F4',action='resolve',destination=['run:context.md#C2'],reason='초기 실패/미실행을 원자료로 보존했고 같은ID 최종passed 및 c/c2 동일제품판본을 대조했다. resource 후처리의 argv 가정 오류는 같은 raw로 해소했다. runtime 결함으로 재배정하지 않는다.',evidence=[base+'failure-mapping.json',base+'verification.json',base+'review.md'])],
 context_updates=[],plan_update='024 P09/P11·지정N 소비를 완료 상태로 반영하고025 P08/신뢰 문장 묶음을 배정했다. 기존 다음024 문단과023 묶음 판단만 현행화했고 과거 유효 근거·G1~G8·L01/정책/권한skip/최종관문은 보존했다. common-docs.diff로 전후를 대조했다.',seam_updates=[],completion=None)
reasons={'C2':'024 검수 결과·초기 실패와 관리자 경로 가정 교정을 추가했다. 기존 역사 결과는 보존한다.',
 'C5':'종료된024 대신025의 한정 통합 소유와 순차 검사 책임을 현행화했다.',
 'C8':'사용자 지정 모델을025에 그대로 적용했다.',
 'C9':'B113/P09·P11 및 D-06의 한정 처분을 추가하며PR24 전체 미완료를 유지한다.',
 'C10':'P09/P11과022 F5의 지정 남김을 닫고8이름/4문단으로 계수를 명확히 했다. 정책 다섯 이름·다른N/L01을 남기며025 책임을 명시했다.',
 'C11':'024에는symlink가선택되지않아기존미검사/최종관문이남음을명시했다.',
 'C12':'불변경계 재사용·두문서 미래영향과28제품/352원task의 인도 보존 범위를 추가했다.'}
for cid,reason in reasons.items(): manager['context_updates'].append(dict(item=cid,action='amend',destination=['run:context.md#'+cid],reason=reason,evidence=[base+'review.md',base+'verification.json',base+'common-docs.diff']))
save(RUN/'phases/024/manager.pending.json',manager)

# Reconfirm the convention immediately before writing the one memory node.
convention=(R/'기억/세칙.md').read_text(encoding='utf-8'); assert re.search(r'^convention_version: 27$',convention,re.M)
number=max(int(x.stem[2:]) for x in (R/'기억/layer1').glob('M-*.md'))+1
node=f'M-{number:04d}'; assert node=='M-0574'
text(R/'기억/layer1'/f'{node}.md','''---
id: M-0574
layer: 1
title: 조건과 대기 문서 결속을 검수하고 신뢰 경계 작업을 통합 배정함
convention_version: 27
---

## 맥락과 판단

024는 실제 조건입력과 queue 대기를 같은 문서 검사에 연결한 작업이다. manager는 보고의 complete를 전체 개발 완료로 바꾸지 않고 최종 양쪽254건, 현재2675파일, 실제반환 각107개와 제안 전문1을 대조했다. 다음025는 남은 project/toolchain/environment_check와 직접 관련된 세 N 절의 문장만 묶는다. 공유 helper와 실제 설치 검사·미러/캐시가 같은 담당자에게 있어야 하며, 기존 packet으로 종료 질문이 정해져 별도 조사를 병렬화할 실익은 없었다.

## 원근거를 해석할 때 유지할 차이

첫 c의 실패는 관찰자가 operation_trace 데코레이터를 실제 생산자로 오인한 결과였다. inspect.unwrap 교정 뒤 같은 제품875Python/254선택이 통과했고 원실패는 그대로 남는다. 관리 검산도 이전 task의 original 경로 관례를 이번 task에 가정해 FileNotFoundError가 났다. 023 압축의 helper 원바이트와024 시작SHA가 같은지 확인한 뒤 함수 보존을 대조했다. 두 오류 모두 제품이나 원task 파일을 바꾸는 이유가 아니었다.

원보고의 ‘정확8문장’은 실제로 이름별8항목이고 고유 문단은4개였다. 이 문단들의 소비 검증을 종결하되 N 세 절 전체를 인증하지 않는다. 정책 다섯 이름도 현 정의와 소유 확인까지이고 전체 의미는 계획에 남는다. 두 문서 문단을 바꿨으므로 과거 모델 호출이나 설치 전체판본의 동등성으로 확대하지 않고 불변 하위경계만 재사용한다.

진입점은 docs/do-math/continuous-development-2026-10-13/phases/024/manager.json과 manager-evidence/review.md·verification.json·section-check.json이다. task352파일과28제품 원바이트는 추적 raw-evidence.zip/preservation.json에 보존한다. 압축만 추적하는 반환/snapshot/scratch의 원경로와 진행 로그·행정 수신은 로컬 보관으로 정리 때 사라질 수 있다. 압축은 복원 지시가 아니다. L01 외부 결정·원문byte 요구, 기존1314 미검사, 최종 전체일반/freshT3/전수변이/연결/최종review는 남으며 push하지 않는다.
''')
idx=R/'기억/색인.md'; old_index=idx.read_text(encoding='utf-8')
text(idx,old_index.replace('## layer-1\n','## layer-1\n\n- M-0574 [조건과 대기 문서 결속을 검수하고 신뢰 경계 작업을 통합 배정함] -- 양쪽254건·실제반환 검수, 8이름/4문단 구별과025 P08·관련N 통합\n',1))
print(json.dumps(dict(next='025',task='document-trust',inputs=len(inputs),writes=len(writes),memory=node,name_rows=8,unique_paragraphs=4),ensure_ascii=False))

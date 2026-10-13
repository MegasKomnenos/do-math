"""Write the reviewed administrative handoff, without modifying product files."""
import difflib
import hashlib
import json
from pathlib import Path

ROOT = Path(r'C:\math')
RUN = ROOT / 'docs/do-math/continuous-development-2026-10-13'
OUT = Path(__file__).resolve().parent
NEXT = RUN / 'phases/008'

def put(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')

def data(path, value):
    put(path, json.dumps(value, ensure_ascii=False, indent=2) + '\n')

before = {name: (RUN / name).read_text(encoding='utf-8') for name in ('context.md', 'plan.md', 'seams.md')}
for name, text in before.items():
    backup = OUT / (name + '.before')
    if not backup.exists():
        put(backup, text)

context = before['context.md']
summary = ('phase 007 provider-consumers는 A1~A5 complete로 검수했다. manager가 8개 공식 실행의 선택/고유 row/실제 exit와 소스 전후를 대조했고 최종 직접 소비98·경계74·corpus14·미러59개가 모두 passed였다. 이전11실패와 pair 두 성공 분기의 공백은 해소됐다. 시작2640파일은006 종료와 같고 task의26변경은 모두 writes와 report에 일치한다. 검수 시 현재와 종료 해시의 차이는 모델 정책에 따른 운영자 작문 도구4파일뿐이며 do-math는 불변이다. runtime124·smoke입력3과102 corpus 경로의 raw/clean을 검산했다. 검수 HEAD는 61f9e06fc15fb49ef30bf7d93c83c92e275eebad이고 근거는 run:phases/007/manager-evidence/verification.json 및 review.md다. 이 지정 회귀의 완료를 전체 일반/T3/변이/G7/최종 review의 완료로 확대하지 않는다.')
context = context.replace('\n## C3 ', '\n' + summary + '\n\n## C3 ', 1)
old = context[context.index('phase 001의 독립 분석 세 task와'):context.index('\n\ndo-math 시험 프로세스')]
context = context.replace(old, 'phase 001의 독립 분석 세 task와 phase 002~007의 단일 work task는 종료됐다. 공급자 단위의 직접 소비 회귀는007에서 검수됐다. phase 008 document-recovery는 운영/복구 문서의 실제 반환 결속(P01)과 독립-운영.md의 확정된 설치 경로 설명(N03-003의 한 문장)을 한 task가 맡는다. 공유 doc_code와 그 소비 검사·공식 미러 생성이 얽혀 있어 같은 판본에서 병렬 수정·검사하지 않는다. 고정판의 독립 읽기 검토는 병렬화할 수 있으며, 후속 제품 작업도 파일과 시험/캐시 독립성을 먼저 확인한다.')
context = context.replace('현재는 phase 001 세 task와 phase 002~006 각 한 task의 report를 각각 새 manager가 검사했다.', '현재는 phase 001 세 task와 phase 002~007 각 한 task의 report를 각각 새 manager가 검사했다.')
context = context.replace('A3/A5를 007에 넘긴다. 이전 partial report 자체는 수정하지 않는다.', 'A3/A5의 직접 소비 남김은007의 새 근거로 해소됐다. phase 007은 A1~A5 complete로 검수했다. 이전 partial report 자체는 수정하지 않는다.')
context = context.replace('구체적 현재 조건은 C12에 둔다.', '구체적 현재 조건은 C12에 둔다.')
context = context.replace('실제 재현과 수리는 P01 책임으로 남는다.', '실제 재현과 수리는 phase 008 document-recovery의 P01 책임으로 배정한다.')
context = context.replace('N03의 해당 절에서 문서를 교정하며', 'phase 008에서 N03-003의 해당 문장을 교정하며')
context = context.replace('직접 소비 fixture·pair 공백의 007 수리 책임과 실호출 재사용 조건은 C12에 둔다.', '직접 소비 fixture·pair 공백은007에서 해소됐고 그 검수와 실호출 재사용 조건은 C12에 둔다.')
old = context[context.index('006 F2/F3와 A3/A5는 phase 007'):context.index('\n\n006 F4의 Claude 재사용')]
context = context.replace(old, '006 F2/F3와 A3/A5의 직접 소비 남김은007의 새 근거로 해소했다. consumers45건의11실패를 최종98개 묶음의 정확한 passed ID에 연결했다. pair는 실제 runner/worker/collector로 두 공급자의 성공·결박·불완전·정지8표본을 만들고 status/output/collection/error_kind/정확 오류·원자료 해시·종료를 검사한다. 수리 전 새 단언의 두 성공 subTest 실패와 수리 후 성공은 원보고로 보존한다. 단일 chunk의20관찰/한callback과 설치 복구 두 사례도 최종 묶음에서 통과했다. raw ingress의 첫97통과/1실패는 정상 후속 행 위치가 별도 final mismatch를 만들던 fixture 오류였다. 같은 stream의 정상 대조군을 completed로 확인하고 malformed만 주입하는42사례에서 공급자별 정확 collector 반려와 저장/재전달 무효과를 확인했다. 이를 제품 parser 수리나 실패 기대값 완화로 읽지 않는다. 근거는 run:phases/007/tasks/provider-consumers/report.json 및 manager-evidence/verification.json과 review.md다.')
old = context[context.index('직접 소비 회귀가 남아 공급자 제품 후보는 작업트리에 유지한다.'):]
context = context.replace(old, '007 검수로 공급자 단위의 관련 회귀가 완료돼003~007의 검수된 제품·시험·문서·미러124파일을 하나의 커밋 단위로 마감한다. 비용 캐시는 실행 부산물로 Git 대상에서 제외한다. 이전 archive는 각 당시 판본의 원바이트 근거로 유지하며 자동 복원 지시가 아니다. staged corpus102경로와 선별 원보고의 바이트를 Git blob으로 확인한 후 커밋한다. 관리 기록·008 배정·기억도 같은 인계에 포함한다. 운영자 모델 전환의 작문 도구·settings/start/README 변경은 제품 단위에 섞지 않으며 C8과 정책 원문은 현재 공용 맥락으로 보존한다. 실제 commit/stage 수신 기록과 정확 경로는 run:phases/007/manager-evidence/preservation.json 및 로컬 commit.json에 남긴다. 다른 G1~G8 의무, 문서/의미 질문, Job/pythonw·Lean/Mathlib·예약·학술·L01 및 최종 관문은 유지한다.\n')
put(RUN / 'context.md', context)

plan = before['plan.md'].replace('## phase 001~006의 결과와 현재 상태', '## phase 001~007의 결과와 현재 상태')
plan = plan.replace('직접 소비11실패와 pair의 성공 표본 공백 때문에 partial이며 phase 007에서 fixture와 분기 단언을 수리한다.', '직접 소비11실패와 pair의 성공 표본 공백 때문에 partial이었다. phase 007이 현 fixture와 실제 분기 단언을 수리했고 manager가 A1~A5를 검수했다.')
plan = plan.replace('직접 소비45개 중11실패와 pair의 두 성공 표본 공백은007 책임이다. 정적 추가 관찰인 chunk·cross_installation도 정확한 직접 소비 범위에 넣는다.', '당시 직접 소비45개 중11실패와 pair의 두 성공 표본 공백은007의 새 근거로 해소됐다. 역사 report는 그대로 유지한다.')
marker = '\n분류는 완료율이 아니다.'
plan = plan.replace(marker, '\n- 공급자 직접 소비 종료: run:phases/007/tasks/provider-consumers/report.json 및 manager-evidence/verification.json. task26변경·최종98/74/14/59선택의 고유 row/exit·이전11실패 해소와 pair red/green을 대조했다. raw 정상 대조와42malformed의 정확 오류도 승인했다. runtime124·smoke입력3·corpus는 불변이고 현재 차이4파일은 운영자의 모델 정책 변경이다. 제품124파일은 관리 마감의 정확 stage·바이트 검증 뒤 커밋한다.\n' + marker)
start, end = plan.index('## 다음 phase: 007'), plan.index('## 가까운 후속 배정과 선행 관계')
plan = plan[:start] + '''## 다음 phase: 008

단일 work task `document-recovery`가 P01의 운영/복구 실제 반환 결속을 닫고 N03-003의 확정된 설치 경로 설명을 교정한다. 운영-점검.md의 동명 result_source/checkpoint_source는 operational_evidence와 recovery_materials의 실제 객체를 구별해야 한다. 정상 파일·restoration_error·checkpoint_source=null·live에서 recovery_materials 부재를 문서 지시와 실제 반환/바이트 검사에 연결한다. B133의 일반 재개·반려·이전 파일 검사는 유지한다. 독립-운영.md의 LIVE_INSTALLATION_ROOT는 현재 manifest/snapshot_root에서 installation_root 인자를 전달하는 설명으로 고친다. N03 전체 이름 검토는 이번 범위가 아니다.

새 task는 C8에 따라 gpt-6.1-sol/high를 명시한다. 공유 doc_code와 직접 소비·미러 생성/비용 캐시를 한 task가 맡으므로 병렬 쓰기 작업으로 나누지 않는다. 한정된 기존 검사와 반례를 사용하며 제품 runtime은 고정한다. 정확한 A1~A5와 writes는 run:phases/008/tasks/document-recovery/objective.md 및 phase.json이다.

''' + plan[end:]
plan = plan.replace('007의 직접 소비·분기 회귀 결과를 검수해 공급자 단위의 관련 회귀 종료와 제품 커밋을 판단한다.', '007의 지정 관련 회귀를 검수했고 공급자 변경 단위를 커밋한다. 다음은008의 문서·실제 반환 연결을 검수하고 G7의 개별 실제 연쇄 배정을 정한다.')
plan = plan.replace('| G1/G2/G3 공급자 직접 소비 회귀 | phase 007이11실패와 성공 표본 공백을 현 외부 fixture·실제 분기 단언으로 해소하고 직접 소비/미러 검사를 완료한다. | 006의Codex 대표실호출·녹화와005의Git 수리는 검수됐다. runtime이 고정된 동안 그 성질을 재사용하고 역사 실패·Claude/background의 한정 재사용을 보존한다. |', '| G1/G2/G3 공급자 단위의 최종 판본 연결 | 007에서 관련 회귀를 종료했다. 이후 변경이 그 경계에 영향을 주면 필요한 근거만 교체하고 G4~G7 최종 관문에 연결한다. | 006 Codex 대표 호출·003 Claude 한정 재사용과 역사 실패를 유지한다. 중간 회귀 합산은 전체 성공이 아니다. |')
plan = plan.replace('| G1/G3 문서 P01 | operational_evidence', '| G1/G3 문서 P01 | phase 008이 operational_evidence')
plan = plan.replace('| G1/G8 문서 N03 확정 불일치 | 독립-운영.md', '| G1/G8 문서 N03 확정 불일치 | phase 008이 독립-운영.md')
put(RUN / 'plan.md', plan)

seams = before['seams.md'].replace('phase 002~006의 work는 종료됐다.', 'phase 002~007의 work는 종료됐다.')
start, end = seams.index('phase 007은 제품 runtime'), seams.index('\n\ncorpus 생성의 정본')
seams = seams[:start] + ('phase 007은 같은 경계의 fixture와 pair를 수리했고 manager가 지정 회귀를 검수했다. 제품 runtime은 불변이다. phase 008은 기존 _context 반환의 operational_evidence/recovery_materials를 문서와 실제 반환 검사로 연결한다. 일반 재개 restore_continuation과 동일한 필드명을 사용하더라도 다른 생산자다. 원자료의 정상/복원 오류/null/부재를 각 실제 객체에서 확인한다. 독립-운영의 설치 경로 설명도 현재 operator_bootstrap.main과 scheduled_operator.main 경계로 교정한다. 제품 계약 개정이나 새 task 사이 인터페이스가 없어 provides/uses는 빈 목록으로 유지하며 S 항목을 추가하지 않는다.') + seams[end:]
seams = seams.replace('007은 새 녹화를 만들지 않고 기존 양쪽 전건 경로/바이트·명시 SHA·Git raw/clean 및 미러 생성 일치를 확인한다.', '007은 새 녹화 없이 기존 양쪽 전건 경로/바이트·명시 SHA·Git raw/clean 및 미러 생성 일치를 확인했다. 008도 corpus를 수정하지 않으며 허용된 문서·시험 사본만 공식 생성한다.')
put(RUN / 'seams.md', seams)

suffixes = [
    '계약/운영-점검.md', '계약/독립-운영.md', 'references/CLI-실행-계약.md',
    'scripts/tests/support/doc_code.py', 'scripts/tests/support/engine_context.py',
    'scripts/tests/support/knowledge_currentness.py',
    'scripts/tests/structure/test_doc_code.py', 'scripts/tests/sim/test_role_input_context.py',
    'scripts/tests/sim/test_knowledge_currentness.py', 'scripts/tests/flows/test_knowledge_impact_retry.py',
    'scripts/tests/unit/test_role_input_packaging.py', 'scripts/tests/unit/test_role_input_scoped_packaging.py',
    'scripts/tests/unit/test_engine_trace_report_corruption.py', 'scripts/tests/unit/test_storage_record_queries.py',
    'scripts/tests/unit/test_storage_report_projections.py', 'scripts/tests/boundary/test_engine_cli.py',
    'scripts/tests/boundary/test_operator_bootstrap_info.py', 'scripts/tests/.timings.json',
]
inputs = ['run:sources/user-decisions.md', 'run:sources/model-policy-2026-10-14.md',
          'run:phases/001/tasks/document-closeout/report.json',
          'run:phases/001/tasks/document-closeout/evidence/followup-packets.json',
          'run:phases/001/tasks/document-closeout/evidence/binding-inventory.json',
          'run:phases/001/tasks/document-closeout/evidence/review-notes.md',
          'run:phases/007/manager-evidence/verification.json', 'run:phases/007/manager-evidence/review.md',
          'run:phases/007/tasks/provider-consumers/evidence/source-final.json',
          'repo:docs/do-math/시험-재편-2026-09-29/조사/결함-범주.md']
inputs += ['repo:.claude/skills/do-math/' + p for p in [
    'AGENTS.md', 'scripts/tests/시험-지침.md', 'scripts/이음새-정본.md',
    'scripts/do_math/core_engine.py', 'scripts/do_math/context_store.py', 'scripts/operator_bootstrap.py',
    'scripts/do_math/scheduled_operator.py', '계약/운영-점검.md', '계약/독립-운영.md',
    'references/CLI-실행-계약.md', 'scripts/tests/support/doc_code.py',
    'scripts/tests/structure/test_doc_code.py', 'scripts/tests/sim/test_role_input_context.py',
    'scripts/tests/sim/test_knowledge_currentness.py', 'scripts/tests/flows/test_knowledge_impact_retry.py',
    'scripts/tests/unit/test_role_input_packaging.py', 'scripts/tests/boundary/test_operator_bootstrap_info.py']]
phase = {'kind': 'work', 'purpose': '운영/복구 문서의 동명 필드를 실제 반환 객체·원바이트·부재/오류 조건에 결속하고, 확인된 설치 경로 설명을 현 구현으로 교정한다.',
         'tasks': [{'id': 'document-recovery', 'model': 'gpt-6.1-sol', 'effort': 'high', 'inputs': inputs,
                    'writes': [prefix + '/skills/do-math/' + suffix for prefix in ('.claude', '.agents') for suffix in suffixes],
                    'provides': [], 'uses': []}]}
data(NEXT / 'phase.json', phase)
(NEXT / 'logs').mkdir(parents=True, exist_ok=True)
(NEXT / 'tasks/document-recovery/evidence').mkdir(parents=True, exist_ok=True)
put(NEXT / 'tasks/document-recovery/objective.md', '''## 목적과 역할

운영 점검·종료 후 복구 문서가 가리키는 필드를 실제 역할 입력과 연결한다. 일반 재개 결과에도 result_source가 있지만 운영 진단의 recovery_materials.result_source와는 생산자가 다르다. 현재 doc_code는 일부를 AST 추출 또는 다른 동명 생산자로 확인하므로, 이름이 존재해도 실제 전달·복원 오류·부재를 놓칠 수 있다. phase 001 P01의 이 유한한 남김을 닫아 G1/G3의 문서 지시와 검출력을 개선한다. 함께 다룰 설치 설명은 N03-003의 LIVE_INSTALLATION_ROOT 한 문장이다.

상류 공급자 수리는007에서 지정 회귀를 완료했다. 그 runtime·corpus는 고정한다. 이번 task의 모델은 gpt-6.1-sol/high이며 제품 시험의 공급자 모델 선택과 구별한다. 공용 문서와 phase.json의 inputs를 읽고, 긴 JSON은 P01 및 N03의 LIVE_INSTALLATION_ROOT 항목을 선택한다. 원문 의무는 결함-범주.md의13-C 및 P01에 기록된1181/1184/1201/1600/1613행 주변을 현재 제목으로 확인한다. 기록된 행 번호는 찾기 좌표이며 현 원문을 우선한다.

## 완료 조건

### A1 현재 생산자·문서 소비와 보존 범위를 확정

시작 파일 해시와 Git 상태를 남기고007 source-final 및 manager 검수와 대조한다. C8에 기록된 운영자 작문 도구4파일 차이와 이후 manager의 공용 문서/기억·Git 변경을 제품 변화와 구별한다. 기존 dirty를 보존한다.

P01의 checkpoint_source, recovery_source, checkpoint_files, recovered_output_files, recovery_materials, operational_evidence를 문서별 실제 소비와 _context의 반환 객체에 대응시킨다. 일반 재개 restore_continuation의 result_source/rejected_response/previous_output_files는 별도 경계로 유지한다. 현재 doc_code의 해당 여섯 AST 추출 지점과 activity_continuations의 중첩 소비를 확인한다. 쓰이지 않는 이름이면 실제 소비 부재를 근거로 제거하고, 남은 소비가 있으면 그 경계를 보존한다. AST 호출 개수 감소를 의미 완료로 세지 않는다.

B132~B134의 manifest/prompt/documents/profile_selection와 B133 일반 재개 검사는 재구현하지 않는다. 바뀌는 doc_code를 import하는 현재6모듈과 새 소비를 찾아 검사 범위에 연결한다. 관찰·현재 처분·근거와 정확한 미결을 표 또는 짧은 기록에 남긴다.

### A2 운영·복구 지시를 실제 객체와 조건에 맞게 교정

운영-점검.md의 실행 중 증거는 operational_evidence.checkpoint_source/checkpoint_files로, 종료 후 진단은 recovery_materials.result_source/checkpoint_source/output_files로 소유자를 명시한다. 정상 파일의 local_path를 읽는 지시에는 그 필드가 존재하는 조건을 둔다. final_result_status=available만으로 복원 성공을 보증하지 않는지 현재 생산자와 대조한다. restoration_error가 있으면 원 artifact/snapshot/기대 해시·크기 및 관찰 오류를 진단 근거로 사용하고, 없는 local_path를 읽거나 검증되지 않은 바이트를 수학적 수락 근거로 쓰지 않는다. checkpoint_source=null과 live_review에서 recovery_materials 부재도 실제 조건대로 설명한다.

정상 결과·checkpoint_recovery·activity_result, 같은 원자료의 중복 계수 금지, 다른 실행의 live 공간으로 빈칸을 채우지 않는 기존 의무를 유지한다. CLI-실행-계약.md는 이 P01 문장과 필드 결속에 영향을 받는 절만 교정한다. 문서 의미를 시험 편의에 맞춰 줄이지 않는다.

### A3 실제 반환·파일과 반례가 문서 결속을 검증

기존 OperationalInputTests, RecoveryMaterialTests, UnreadableBeforeReviewTests 및 일반 재개 검사를 재사용한다. 실제 _context/입력 포장/저장·파일 생산을 유지하고 외부 포트에서만 대역을 둔다. 문서 검사기의 새 경계를 실제 반환 객체로 채워 검사한다. 현재 필드를 베낀 합성 표, 반환하지 않는 AST dict 또는 타 생산자의 동명 필드로 실제 결과 검사를 대체하지 않는다. AST helper 전체를 새 추론기로 확장하지 않는다.

정상 sealed checkpoint와 근거 파일의 local_path·바이트·sha256·bytes·snapshot, 종료 후 정상/복원 불가 자료, checkpoint_source=null, live에서 recovery_materials 부재, activity_continuations의 실제 문서 소비를 검사한다. 정상 객체 한 항목의 local_path 제거, 잘못된 해시/크기, 동명 운영/복구/일반 재개 소유자 교환이 해당 검사에서 실패해야 한다. 원제품 경로가 반려하는 입력은 정확한 반려 사유로 확인한다. 실제 반환을 얻은 뒤 그 사본을 교란하는 문서 검사 반례와 제품 경계의 손상 입력 검사를 구별한다.

현재 문서 결속 공백을 드러내는 새 단언을 수리 전에 실행해 red를 보존하고 수리 뒤 같은 성질의 통과를 연결한다. 전체 field_schemas/scoped_field_issues 검사는 실제 반환을 검증할 책임이 명시된 경계만 위임하며, 위임 목록 오기·누락·타 경계의 임의 통과를 거부한다. 정상/오류/null/부재를 필드 합집합 하나로 합쳐 누락을 숨기지 않는다.

### A4 설치 경로의 확정된 낡은 설명을 교정

독립-운영.md의 「설치본을 고정하고 live 수리 대상을 구별한다」 절에서 LIVE_INSTALLATION_ROOT 설명을 operator_bootstrap.main이 manifest의 installation_root 또는 snapshot_root를 scheduled_operator.main의 installation_root 인자로 전달하는 현 경계에 맞춘다. 고정 사본과 live 수리 대상 구별 및 manifest 검증의 한계를 유지한다. 기존 boundary.test_operator_bootstrap_info의 실제 실행을 근거로 연결한다. 옛 전역 이름을 제품에 추가하지 않는다. N03의 다른 절·문서 전체 이름 검토는 별도 남김이다.

### A5 관련 회귀·미러와 정확한 인계

아래 지정 검사를 최종 시험·문서 판본에서 완료하고 선택/고유 row/실제 종료·소스 전후 해시를 남긴다. 이전 반환 검사와 단언을 유지하며 실패·skip·미실행을 숨기지 않는다. 허용된 미러만 공식 생성하고 생성 계획·현재 dirty·실제 변경을 대조한다. 최종 --check와 --skill-only를 통과하고 runtime/corpus 불변을 확인한다. 제품 문서 변경은 후속 최종 판본 근거에 연결하되 공급자 runtime이 바뀐 것처럼 재호출하지 않는다.

report는 A1~A5, 실제 변경, red/green, 보존한 기존 성질, 미실행·권한 밖 발견과 다음 책임을 기록한다. 모든 A가 pass일 때만 complete다. 이번 완료는 P01 및 N03-003의 지정 문장에 한정되며 나머지 문서·G1~G8 전체나 최종 관문을 완료로 바꾸지 않는다.

## 판단과 경계

phase.json의 writes는 세 문서, doc_code와 기존 입력 helper, 명시한 직접 소비 시험 및 대응 미러/비용 캐시다. 여기에 파일이 나열됐어도 이번 경계와 무관한 성질을 바꿀 권한은 아니다. helper의 구체적 표현과 실제 반환을 연결하는 작은 공통 함수는 구현 재량이다. runtime/core_engine/context_store/bootstrap의 의미 수정은 쓰기 범위 밖이다.

제품 결함이나 추가 소비 범위가 확인되면 재현 근거와 영향 A를 fail/not_run으로 보고한다. 해결된 부분은 유지하고 다음 manager가 수리 범위를 배정하게 한다. 부분 완료를 피하려고 제품 검사를 완화하거나 새 문서 계약을 발명하지 않는다. 관할 밖 의무는 finding으로 반환한다.

검사 묶음은 순차 실행하고 worker 합계3 이하, 기본jobs1을 따른다. 검사 중 소스를 고정하며 시간은 소프트 기준이다. 실제 모델 호출·기존 연구 시작/재개/삭제·OS 예약 변경·graphify 갱신·Git stage/commit/reset/checkout/push는 이번 작업에 포함되지 않는다. manager와 서비스가 검수·커밋·다음 실행을 맡는다.

## 검증 방법

cwd는 C:\\math, Python은 C:\\Users\\wogud\\AppData\\Local\\Programs\\Python\\Python312\\python.exe다. 공식 명령은 이 Python으로 `-u -B .claude/skills/do-math/scripts/run_tests.py <선택> --jobs 1 --output <자기 evidence의 새 경로>`를 실행한다. argv/cwd/PID/시작·종료/stdout/stderr/exit와 소스 전후를 보존한다. 실행 중 result.json은 file_io.read_bytes_shared로 관찰한다.

1. A1 표와 원문을 바탕으로 A3 반례의 정확한 ID를 먼저 실행한다. 기존 전체 묶음의 실패를 보기 위한 무의미한 반복은 하지 않는다.
2. 최종 정본의 `structure.test_doc_code`, `sim.test_role_input_context.OperationalInputTests`, `sim.test_knowledge_currentness.RecoveryMaterialTests`, `flows.test_knowledge_impact_retry.UnreadableBeforeReviewTests`, `unit.test_role_input_packaging`, `unit.test_role_input_scoped_packaging`, `boundary.test_operator_bootstrap_info`를 한 묶음으로 실행한다. 정확한 클래스명은 시작 때 현재 코드로 확인한다.
3. 공유 doc_code 소비 회귀는 `unit.test_engine_trace_report_corruption unit.test_storage_record_queries unit.test_storage_report_projections boundary.test_engine_cli`로 실행한다. 앞 묶음의 doc_code 직접 소비와 함께 현재6모듈을 덮는다. 수정하거나 새로 보강한 시험이 이 선택 밖이면 그 정확한 ID를 추가하고 이유를 남긴다. 전체 일반/T3/변이 실행은 이번 배정이 아니다.
4. 공식 build_skill_mirrors.py의 생성 계획을 확인한 뒤 대응 파일을 생성한다. 미러의 `.agents/skills/do-math/scripts/run_tests.py`로 2번과3번 선택 중 이번에 수정한 시험 모듈, `structure.test_doc_code`, 두 운영/복구 클래스 및 bootstrap-info를 중복 없이 한 묶음에 넣어 실행한다. 미러 실행 후 비용 캐시만 공식 재동기화하고 `build_skill_mirrors.py --check`, `probe_cli.py --skill-only`를 확인한다.
5. `python -B services/continuous-development/check.py report C:\\math C:\\math\\docs\\do-math\\continuous-development-2026-10-13 008 document-recovery`를 통과한다. 마지막 응답에는 complete/partial/blocked와 자기 report.json 경로를 남긴다.
''')

put(OUT / 'review.md', '''# phase 007 manager 검수

provider-consumers의 A1~A5 complete를 승인한다. 형식 검사와 실제 판본·원검사 결과의 대조를 마쳤다. G4~G8 및 나머지 의미·문서 의무의 전체 완료는 아니다.

## 판본과 검증

시작2640파일은006 종료와 같고 task의26변경은 report 및 writes와 일치한다. 현재 종료 해시 차이4개는 sources/model-policy-2026-10-14.md에 명시된 작문 도구 정본/미러의 모델 기본값 변경이다. task에 귀속하지 않는다. do-math 종료 판본과 공식 최종 보고의 정본/미러 Python 각865개는 현재와 같다. 운영자가 바꾼 settings/start/README는 제품 커밋에서 제외한다.

manager가8개 공식 묶음의 선택/고유 row/counts/실제 exit와 명령별 전후 소스 해시를 대조했다. pair-red 1failed는 두 성공 subTest의 failed/output_validation을 드러낸 의도한 반례다. 첫 consumers의97passed/1failed는 역사 실패로 유지한다. 최종 consumers-final98·boundaries74·corpus14·mirror59는 각각 전건passed/exit0이며 검사 중 변화는 비용 캐시뿐이다. 새 테스트 전체를 다시 실행하지 않고 보존된 원보고와 소스를 대조했다. 관리 커밋 게이트에서는 생성기22개, 현재 --check1305파일과 skill-only verified를 별도로 확인했다.

## 의미 검수와 발견 처분

F1은 resolve다. 기존11실패의 ID를 최종 passed에 연결했다. provider_runs는 실제 worker CLI schema를 읽어 원/전송을 구분하고 explicit raw를 재작성하지 않는다. operator/probe/cross_installation, native storage와 chunk의 diff에서 nonce·파일·checkpoint·정확 오류·수치·원바이트·저장·단일 전달 단언이 유지됨을 확인했다. pair의8표본은 실제 runner/worker/collector를 지나며 성공 상태, 결박, 불완전, 정지를 각각 단언한다. 기존 저장 수신과 필드 역방향 검사를 유지했다.

F2는 resolve다. 원 consumers 실패와 raw-ingress-first.py, 최종 fixture 및 parser/collector의 반려 조건을 대조했다. 정상 final 바로 뒤 terminal을 요구하는 Codex 순서와 malformed에서 중단하는 공급자별 조건을 구별한다. 같은 생성기의 정상 대조2개가 completed이고42개 교란 입력의 정확 오류·원자료·저장/재전달 무효과가 확인된다. 제품 parser나 원실패 보고는 바뀌지 않았다.

F3는 한정 resolve다. runtime124·smoke입력3 및 현재 두 CLI 실행 파일 SHA가006 재사용 기록과 같다. 새 모델 호출은0이다.003 Claude의 역사 binary SHA 미기록과 background passed=false를 유지한다. corpus 각18항목/51파일/223685바이트/50명시SHA와102 Git raw/clean을 실제 바이트로 검산했다. 최종 전체 관문과 다른 G7 실연쇄는 plan에 계속 남긴다.

## 인도와 다음 책임

003~007의 검수된 공급자 제품·시험·문서·미러124파일을 커밋 후보로 골랐다. 기존 canonical/repository·planning 등 무관한 dirty와 운영자 모델 설정 변경은 제외한다. 최초 snapshot에 없거나 줄끝 때문에 비교되지 않은9파일은 현재 전체 Git diff가 보고된 Codex 전송 문장·corpus verbatim 규칙·생성기 반례와 일치하는지 직접 확인한다. 정확 stage 목록, 원보고/녹화 raw blob 대조를 관리 마감에서 보존한다. 최종 전건 검증 전의 중간 제품 커밋이며 최종 인도 합격은 아니다.

008은 P01 실제 반환 결속과 N03-003 한 문장 교정을 한 task에 배정한다. 현재 doc_code와 core_engine 원문에서 동명 객체·복원 오류/null/부재 조건을 확인했고 bootstrap 원문에서 installation_root 전달을 확인했다. 공유 helper·소비 검사·생성기 때문에 병렬 수정으로 나누지 않는다. task 모델은 사용자 지정 gpt-6.1-sol/high다. 다음 manager와 서비스 실행기의 설정은 C8을 따른다.

판정의 기계 근거는 verification.json, git-clean-observation.json, supplementary-checks.json 및 task의 원 report/evidence다. 공용 의미 갱신은 common-docs.diff와 manager.json에 연결한다. Git stage/commit 수신 기록은 로컬 commit.json에 남고, 선별 자료의 추적 범위는 preservation.json에 명시한다.
''')

assert 'convention_version: 27' in (ROOT / '기억/세칙.md').read_text(encoding='utf-8')
node = ROOT / '기억/layer1/M-0557.md'
assert not node.exists()
put(node, '''---
id: M-0557
layer: 1
title: 공급자 직접 소비 회귀를 검수하고 운영 복구 문서 결속을 배정함
convention_version: 27
---

## 맥락

phase 007은006의 Codex 전송 수리를 소비하는 시험만 바꾸었다. manager는 기존11실패와 실제 성공 표본의 검출 공백이 해소됐음을 원보고·현재 코드로 검수했다. 공급자 단위의 관련 회귀를 끝내003~007의 제품·시험·문서·미러를 함께 커밋한다. 전체 일반/T3/변이와 나머지 실제 연쇄는 아직 남는다.

## 판단의 근거

저장할 수 있는 결과를 만들었다는 사실은 성공 분기를 검사했다는 뜻이 아니었다. 새 pair 단언은 성공이라고 이름 붙인 두 표본이 output_validation 실패였음을 잡았고, 표본을 실제 collector 경로로 바꾼 뒤 통과했다. raw ingress에서는 잘못된 정상 후속 행 순서가 malformed 행과 무관한 final mismatch를 만들었다. 정상 대조와 정확 collector 사유를 함께 검증해 같은 failed 상태 안의 다른 원인을 구별했다. 원실패는 보존한다.

검수 중 task 종료 해시와 다른 네 파일은 운영자가 모델 기본값을 바꾼 작문 도구 정본/미러였다. 이를 작업자의 범위 위반이나 제품 회귀로 귀속하지 않았다. 사용자 지정 이후 새 task는 gpt-6.1-sol/high, manager는 gpt-6-astra/xhigh를 사용한다. 기존007 작업자의 모델 기록과 제품 실호출 모델은 소급 변경하지 않는다. 설정 변경 요청의 더 넓은 배경은 이 manager 대화로 확인할 수 없어 추측하지 않는다.

다음008은 운영/복구 문서의 같은 필드명을 실제 생산자에 연결한다. 일반 재개의 result_source로 운영 진단을 검증하지 않으며 오류/null/부재에서 실제 읽을 파일을 구별한다. 공유 doc_code와 그 소비를 한 task에 묶고 제품 runtime은 고정한다.

## 근거의 보존 범위

추적 진입점은 실행 기록의 phases/007/manager.json, manager-evidence/review.md·verification.json·preservation.json, task report 및 phases/008 배정이다. 원검사 report·stdout/stderr·시작/종료 소스와 필요한 명령별 판본은 추적한다. 재생성 가능한 작문 입력 묶음, 서비스 세션 로그와 독해 실행기의 원로그, Git stage/commit 수신 기록은 로컬 자료라 정리로 사라질 수 있다. 독해 결과·실행 metadata·대조와 입력 해시는 추적한다. 이전 공급자 원자료의 한계는 [[M-0553]]·[[M-0554]]·[[M-0555]]·[[M-0556]]을 유지한다.
''')
index = ROOT / '기억/색인.md'
put(index, index.read_text(encoding='utf-8').rstrip() + '\n- M-0557 [공급자 직접 소비 회귀를 검수하고 운영 복구 문서 결속을 배정함] -- 실제8분기·정상 대조/정확 반려 검수, 모델 운영자 변경 구별·008의 반환 소유자 교정\n')
diff = ''.join(''.join(difflib.unified_diff(before[name].splitlines(True), (RUN / name).read_text(encoding='utf-8').splitlines(True), fromfile=name + ':before', tofile=name + ':after')) for name in before)
put(OUT / 'common-docs.diff', diff)

reading_files = [ROOT / 'services/continuous-development/protocol.md', RUN / 'context.md', RUN / 'plan.md', RUN / 'seams.md', NEXT / 'phase.json', NEXT / 'tasks/document-recovery/objective.md', OUT / 'review.md', node]
put(OUT / 'handoff-reading.md', '\n\n'.join('# 입력 문서: ' + p.relative_to(ROOT).as_posix() + '\n\n' + p.read_text(encoding='utf-8') for p in reading_files))
data(OUT / 'reading-inputs.json', {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in reading_files})
print('Prepared phase 008, common documents, manager review and M-0557.')

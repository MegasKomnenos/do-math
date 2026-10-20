# 반려 원인의 필드 결박과 남은 구조 검사 묶음

사용자 목표는 잘못된 원인으로 실패한 시험이 성공으로 처리되지 않고, 실제 제품 경로를 가리지 않는 것이다. structure-fixes의 수용된 변경에서 시작한다. SESSION_JSON의 workspace·task.json과 inputs/context.md·plan.md·seams.md, managers/0027/review.md·source-review.json을 읽는다. 제품은 자기 workspace의 writes만 변경하고 공용 소스/다른 task 기록은 읽기 전용이다. do-math AGENTS.md와 시험 지침, 사용자 원문/묶음 지시/모델 지정을 적용한다.

## 한 작업에서 마칠 범위

1. manager F1: structure-fixes A07의 `sim/test_submission_review_inputs.py:test_review_stage_documents_reach_the_final_seat_input`은 identity_basis/policy_ref 누락을 모두 `^False != True$`로 받는다. 실제 `support/engine_context.py:assert_review_documents`의 role_review membership 비교에 누락된 필드의 정체성이 없다. helper의 정확한 필드 비교와 consumer의 반려 단언을 함께 연결한다. 실제 stage 정상 대조·지급/봉인 입력·기존 proposal/소유 좌표 검사와 단계 모집단을 보존한다. 하나의 필드 누락을 다른 필드 실패로 받아들이지 않는 최소 근거를 남긴다. 같은 helper의 가까운 진단만 보완하며 전체 문서 검사를 재설계하지 않는다.
2. manager F2: structure-fixes/evidence/smell-scope.json의 other_inherited 3건을 묶어 판정·수리한다. `unit/test_external_value_boundaries.py:test_extension_absence_null_and_empty_families_stay_distinct`의 UnicodeDecodeError는 실제 원 bytes·codec·위치/이유를 확인한다. `unit/test_null_boundary_consumers.py:test_console_discovery_failure_reports_null_reconciliation_command`의 cli.console_python 제품 patch는 실제 console 발견 실패를 만드는 외부 경계 입력으로 교체하면서 reconcile=null/원 scheduler 오류/발견 오류/exit/JSON 표현을 유지한다. `flows/test_submission_ingress_owner.py:test_workspace_roots_are_consumed_once_before_a_valid_maintenance_submission`의 broad_except는 실제 반려/재전달/뒤 정상 수락과 예외 전달을 읽고 필요 없는 wrapper를 줄이거나 정확한 책임을 드러낸다. 단순히 예외를 숨기거나 검사 필터/면제로 통과시키지 않는다. checker 오판이면 현재 목적·실제 반례를 입증하고 그 해석만 최소 수정할 수 있으나 새 예외 목록/이름 whitelist는 만들지 않는다.
3. 작은 공통 보완 F3: `references/입력-소비자.md`의 governance.apply_decision 생산자 표기를 기존 명시적 함수(...) 표기로 바꾸면 `support/doc_code.py:governance_field_issues`의 새 한국어 문구 전용 분기가 필요한지 재검토한다. 이 문서가 이전 writes 밖이었던 것은 제품 요구가 아니다. 명시 표기로 의미를 보존할 수 있으면 문서를 고치고 불필요한 분기와 그 분기를 요구하는 새 단언을 제거/교체한다. 기존 function_reference_issues의 실제 callable 대조와 설명 없는 필드·단독 이름·오타·별칭 반려는 유지한다. 새 문법이나 면제 registry를 추가하지 않는다.

`sim/test_role_input_context.py`의 9건은 실행 중 r31-fix의 소유다. 그 파일이나 r31-fix/r34-r36의 helper/runtime은 수정하지 않는다. structure-fixes의 원 report/판정표는 보존하고 후속 evidence에서 A07와 3건의 처분을 연결한다. 원35건을 새로 전부 실행하거나 문서 P01~P11을 다시 열지 않는다.

## 최소 확인과 인계

소스만으로 충분하면 정적으로 끝낸다. 실행은 공식 run_tests.py --jobs 1의 바뀐 성질과 helper의 직접 소비 ID만 선택한다. 정상 대조와 반려의 정확 원인을 함께 확인하고, 전체 smell의 정적 결과에서 다른 소유 9건과 자기 범위를 구분한다. 전체 일반/T3/변이/T4/T5·실제 Lean/모델/예약 호출은 하지 않는다. scope 밖 runtime 결함은 실제 입력·경계·영향과 필요한 파일을 보고한다.

공식 mirror build/check와 변경쌍 bytes를 확인하고 비용캐시는 증거 보존 후 own base로 복원한다. report에는 실제 변경·원인·선택/실제row·exit/판본·초기 실패/fixture 교정·소프트초과/미실행·남은 문제를 구분한다. check.py report C:/math/.async/dm structure-finish PASS 후 제출한다. 공용 context/plan/seams/queue/state·Git index·과거 원자료는 수정하지 않는다. G4~G8·다른 의미 질문·L01/Windows1314는 이 작업의 종료 조건이 아니다.

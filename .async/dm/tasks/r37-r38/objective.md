# 행동·과제·활동 대기의 실제 진입과 해소·표시

사용자 목표는 대기 상태가 실제 조건을 보존하고 올바른 담당자가 정확히 한 후속 행동으로 해소하며, 사람이 읽는 상태와 JSON이 그 사실을 정확히 보여 주는 것이다. 원래 R37/R38과 4-A·4-B·13-B의 이 범위를 현재 코드·원보고로 판정하고, 확인된 공백의 구현/시험 보완·필요한 최소 확인을 한 task에서 마친다. 선언표 존재만으로 의미 검증 완료를 주장하지 않는다.

SESSION_JSON의 workspace/task.json, inputs/context.md·plan.md·seams.md를 먼저 읽는다. C:/math의 원자료와 다른 task 기록은 읽기 전용이다. 자기 workspace의 writes에서만 수정하며 진행 중 사본은 읽지 않는다. 사용자 원문/묶음 지시/모델 지정과 스킬 AGENTS.md·시험 지침을 적용한다.

## 원문과 실제 모집단

closure-map/evidence/tracking-state.json의 R37/R38, requirement-state.json의 4-A/4-B/13-B, prior-review-state.json의 PR10 중 B28/B32/B78/B79를 읽는다. 결함-범주.md 557~566·1177~1180과 단계-전환표의 해당 original_requirement 및 current_work.wait_contract_integration/waiting_work_integration/impact_read_integration/activity_wait_integration/task_wait_projection_integration을 연결한다. 역사 22종은 출발 정보이며 현재 WAITING_ACTION_RULES/ACTIVITY_WAIT_RULES/REVIEW_WAIT_RULES와 실제 생성·갱신/해소 경로로 모집단을 확정한다. 과거 보고 경로가 없으면 부재를 기록하고 counts만으로 성공을 추정하지 않는다.

각 현행 kind에서 실제 생성자→저장/조건 전 유지→명시 해소자→조건 후 후속 1개/재전달 불변→JSON/사람 표시의 사유·담당자·좌표를 현재 정확한 단언과 연결한다. kind를 사후 주입한 constructor 시험과 실제 owner 전이 시험을 구별한다. 목록 값 일치·callable 존재·AST 등록은 행동 증거를 대신하지 않는다. 현재 task waiting/활동 waiting/검토 자리 대기는 서로 다른 의미와 저장 위치를 유지한다. 해소 조건이 성립하지 않은 입력과 성립한 입력, 무관 사건, 정확 대상/owner를 구별한다. 실제 저장/restart가 의미상 필요한 경우만 포함한다.

중심은 do_math/wait_rules.py의 waiting_action/update_waiting_action/activity_wait_record와 do_math/activities.py·reporting.py 및 실제 owner 소비자다. 기존 structure/test_action_wait_contract.py와 preparation/review/formal/authority/admission 선언 검사, unit/test_action_wait_contract.py·test_review_wait_contract.py·test_admission_wait_contract.py, sim의 preparation/formal/import/authority wait·storage status, flows의 impact/failed action/submission wait, support/wait_reporting.py를 먼저 대조한다. B28/B32의 실제 diff/현재 소비/정확 원보고와 B78/B79 원자료를 이 같은 범위에서 재사용·교정·추가 필요로 판정한다. PR10 전체나 R39~R43의 다른 대기/판정/반복 질문으로 확대하지 않는다.

## 쓰기와 병렬 경계

task.json writes가 정본이다. wait_rules/activities/reporting과 지정 직접 시험·wait_reporting helper·미러를 소유한다. r31-fix의 core_engine/decision_engine/task_scope/input_basis/record_schemas/역할 입력 시험, r34-r36의 planning/context_store/lifecycle/governance/formal/call_engine 및 규칙 차분 시험, structure-finish의 문서/helper/반려 시험은 읽기 전용이다. 해당 owner의 실제 결함이 필요하면 입력·사용 영향·정확 수정 경로를 보고하고 허용 범위의 수리까지 마친다. 읽기 전용 제품을 대역으로 교체하거나 새로운 호환 분기를 만들어 우회하지 않는다.

두 R 작업은 같은 kind/해소/표시 helper를 공유하므로 한 묶음이다. R38이 별도 R37 보고를 기다릴 필요는 없다. 이번 새 task는 현재 수용판을 읽으며 진행 중 두 task의 미완성 결과를 소비하지 않는다. 과거 task 개수나 매핑표를 완료율로 사용하지 않는다.

## 확인과 보고

기존 원보고/소스 대조로 충분한 성질은 재실행하지 않는다. 부족한 단언을 고쳤거나 실행 불확실성이 남으면 가장 작은 정상/조건 전후 입력으로 공식 run_tests.py --jobs 1의 해당 ID만 선택한다. 표를 채우기 위한 전 대기 흐름 반복 실행, 전체 일반/T3/변이/T4/T5·외부 모델/Lean/예약 호출은 하지 않는다. 외부 경계만 대역으로 두고 생산/해소/저장/표시 제품 경로와 독립 기대값을 유지한다.

evidence는 kind별 현재 경로/실제 단언·증거판본·충족 성질·구체적 남김을 담는다. 과거 수용된 r29-r30의 단위 실패/new execution_failure 대기와 r06/r12/r22의 저장·null·입장 의미를 보존한다. 현재 입력·권한·봉인·현재성 검사나 기존 규모/성질을 줄이지 않는다. mirror build/check 및 변경 bytes를 확인하고 비용캐시는 증거 보존 뒤 own base로 복원한다. report에 실제 선택/row·exit/SHA·fixture/초기 실패·소프트초과·미실행과 남은 질문을 구분하고 check.py report C:/math/.async/dm r37-r38 PASS로 마친다. 공용 문서/queue/state·Git index·과거 원자료를 수정하지 않는다. G4~G8·원요구/보존/P2 전체·L01/Windows1314는 열어 둔다.

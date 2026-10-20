# 역할 판정의 후속과 과제 대기 해소

사용자가 현재 과제가 왜 기다리는지, 무엇이 바뀌면 누가 이어가는지 알 수 있고 실제 조건 해소 뒤 정확한 후속으로 진행하게 한다. R41의 계약검토·운영점검·목표감사·평가 판정 공간과 r37-r38에서 남긴 같은 task/core owner의 대기를 한 작업에서 판정하고 필요한 구현·직접 시험·설명·미러를 마친다.

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md와 do-math AGENTS.md·시험-지침.md를 읽는다. 원문은 C:/math/docs/do-math/continuous-development-2026-10-13/sources/user-decisions.md·requirements-index.json, phases/001/tasks/closure-map/evidence/tracking-state.json의 R41 및 requirement-state의 4-A/4-B/13-B다. 시험-재편-2026-09-29/조사/결함-범주.md의 해당 절과 단계-전환표의 outcome_contract_integration(B33)·goal_academic_result_trigger_verification(B102)을 현행 코드·원보고와 대조한다. B33의 제출/복구 결과는 r40-r43에서 이미 다뤘으므로 역할 verdict와 혼동하거나 재실행하지 않는다.

## 맡은 유한 질문

1. contracts/planning/task_scope와 실제 core/decision/governance/revision 소비자에서 계약검토·운영점검·목표감사·평가의 현재 판정값을 확정한다. 각 실제 생산값의 저장 결과, 담당 해소자, 정확한 후속 또는 의도된 유지/종결과 공개 관측을 연결한다. 모든 verdict에 무조건 새 action을 강제하지 않는다. 실제 현재 의미에 맞는 단 하나의 후속 효과와 재전달 불변을 판단한다. 선언 enum·문자열 언급이나 합성 constructor만으로 실제 owner 전이를 증명하지 않는다.
2. tasks/r37-r38/evidence/wait-matrix.json과 review.md의 남김을 이어 과제에 저장되는 contract_review/contract_revision/assessment/assessment_input/research_followup 다섯 대기를 판정한다. planning.task_ready의 readiness 투영과 저장 task.waiting, action/activity 대기를 구별한다. 실제 producer→저장/restart→조건 전 유지→정확 해소/후속→사유·다음 소유자·좌표와 표시의 연결을 확인한다. 무관 사건/다른 대상·중복 요청은 원 대기·계수·원증거를 보존해야 한다. 기존 B28의 waiting 위임 결과가 원 assessment를 강제하지 않는 성질을 유지한다.
3. 같은 owner의 revision_dependency, input_overflow, machine_capacity를 기존 직접 시험에서 함께 판정한다. input_overflow의 원 입력·원 activity/프로필 선택·정확 해소와 task 없는 공개 표시, machine_capacity의 실제 입장 전후와 회계/다른 owner 보존을 확인한다. call_engine/model_runner/observation 계열은 진행 중 r47-r48의 소유이므로 읽기 전용이다. 현행 core의 producer/resolver를 검사하며 그 사본의 미완성 변경을 소비하지 않는다. user_resume/required_input은 공개 activities API와 현재 실제 caller 범위부터 판정하고, 없는 제품 경로를 지어내지 않는다.
4. r37-review가 확인한 작은 설명 불일치를 함께 정리한다. wait_rules.ACTIVITY_EXTRA_WAIT_RULES.review_resource_deferred의 조건 산문은 현재 _settle_review_resource_dispositions의 실제 제안 supersession/withdrawal·instance 종료 출구에 맞춘다. 현재 resource decision이 고정 scope를 재개한다는 없는 API를 추가하지 않는다. r37-review/evidence/review.md와 수용된 resource 직접 시험을 읽어 산문 정합만으로 충분하면 새 제품 시험을 늘리지 않는다. core admission condition.action_ids와 기존 정확 review 해소 연결도 제품 이음새 설명에 필요 범위만 반영한다.

## 구현과 확인 경계

task.json의 writes가 허용 범위다. 같은 task/core/planning owner의 실제 결함과 빠진 직접 단언을 함께 수리한다. 현재 r31-fix의 지급 source identity/currentness, r39-r42의 동일 clock pause, r37-review의 action_ids/회계, r39-report의 질문·반복·pause 표시를 보존한다. schema/기존 권한·봉인·현재성·반복 한도를 단언 통과를 위해 약화하지 않는다. 새 범용 대기 해석기·registry·호환 분기는 필요 근거 없이 만들지 않는다. reporting/helper를 바꿀 때 기존 공개 action/activity API를 보존한다.

R44~R46의 근거 민감도는 별도 고정 사본 조사다. 전체 5-A를 본 작업에 넣지 않는다. 새로 발견한 범위 밖 문제는 실제 입력·관측·필요 파일/심볼과 사용 영향으로 인계한다. r08 역사 A-02의 특정 review-cycle 종료와 task_ready 대상이 실제로 겹치면 함께 판단하되, 가상 삭제나 옛 API를 추가하지 않는다. 연결이 없으면 미확인으로 유지한다.

먼저 현재 단언·보존 원보고와 불변 정의를 읽고 충분한 성질은 재사용한다. 새 수리나 실제 공백만 공식 scripts/run_tests.py --jobs 1의 가장 작은 선택으로 확인한다. 외부 모델/Lean/예약·전체 일반/T3/변이/T4/T5는 실행하지 않는다. 같은 helper의 연관 확인을 묶고 성공한 동일 판본을 새 이유 없이 반복하지 않는다. 최초 실패·fixture 교정·정확 selected/실제 row·exit·판본·소프트 초과를 남기고 별도 실행을 단일 최종판 통과로 합산하지 않는다.

정본/미러를 공식 생성·check하고 timing cache는 관측 bytes를 evidence에 보존한 뒤 own base로 복원한다. report에는 역할별 유한 모집단/실제 소비, 다섯 과제 대기와 추가 대기의 완료·남김, 변경 이유와 확인 범위를 쓴다. check.py report C:/math/.async/dm r41 PASS 후 제출한다. 공용 source/문서/queue/state·다른 task·Git index·graphify·기존 연구 운전은 수정하지 않는다. 전체 R37/R38/PR10·G4~G8·L01/Windows1314의 완료로 확대하지 않는다.

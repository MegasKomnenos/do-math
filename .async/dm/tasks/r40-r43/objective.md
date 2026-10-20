# 공급자·설치 대기와 제출·복구·자기점검 계수

사용자 목표는 자원/환경/시각/설치수리 조건에 맞게 대기를 유지·해소하고, 실제 결과가 선언된 계수를 정확히 바꾸어 quota나 보류가 복구 기회를 소모하지 않게 하는 것이다. 원래 R40과 R43은 provider/repair의 실제 결과 소비를 공유하므로 함께 판정하고 필요한 수리·최소 확인까지 마친다.

SESSION_JSON의 workspace/task.json과 inputs/context.md·plan.md·seams.md를 먼저 읽는다. C:/math 원자료와 다른 task 기록은 읽기 전용이며 자기 workspace writes만 변경한다. do-math AGENTS.md·시험 지침, 사용자 원문/묶음 지시/모델 지정을 적용한다. r37-r38 수용판의 활동 조건 비교·표시/helper를 읽되 진행 중 r39-r42의 사본은 소비하지 않는다.

## 원문과 유한한 완료 질문

closure-map/evidence/tracking-state.json의 R40/R43, requirement-state.json의4-A/4-B/4-C/13-B를 읽는다. 결함-범주.md L557~572·1177~1180과 단계-전환표의 provider_population_integration/wait_contract_integration/outcome_contract_integration/self_check_progress_integration을 현재 정의와 대조한다. 역사 제출5·설치복구6·자기점검3은 출발 모집단이며 실제 생산자와 현행 정본으로 확정한다. 과거 counts나 이름 목록만으로 완료를 주장하지 않는다.

1. provider_wait/provider_engine/session_slots와 실제 scheduler의 공급자·자원·시각 gate를 연결한다. 조건 전/후·무관 사건·generation/owner·정확히 한 후속·재전달 불변과 status의 담당자/조건을 확인한다. 설치 repair 대기는 repair_execution/scheduled_operator의 실제 변경 조건·재시도 owner와 연결한다. r37 matrix에서 provider_admission, operational_repair, installation_repair_retry에 남긴 개별 owner/표시 질문을 이 범위에 포함한다. machine_capacity는 core owner의 다른 후속으로 남기고 공급자 실패와 혼동하지 않는다.
2. integration.SUBMISSION_OUTCOMES/submission_outcome → RepairExecutionMixin.route_submission_return, repair_execution.RECOVERY_OUTCOMES/runner_outcome/record_recovery_attempt/recovery_attempt_counts, control_protocol.SELF_CHECK_PROGRESS → observations.ObservationTracker.record_self_check_response의 실제 소비를 연결한다. 각 현행 결과에 선언된 reset/retain/increment/제외·정산·출구가 있는지 확인한다. quota·보류·미확인 종료와 실제 실패/보고를 구별하며 한도 뒤 사용자/운영/repair 출구와 중복 불변을 확인한다. r39-r42의 반복 다섯 계보는 이 작업의 계수와 다른 범위다.
3. 대기 관련 event kind의 실제 생산·수신을 현재 event/owner 경로와 연결한다. 이벤트 등록/순서 검사만으로 해소를 증명하지 않고, 위 두 항목의 사건이 실제 조건과 후속에 미치는 영향만 판정한다. 전 제품 이벤트 감사나 새로운 registry를 만들지 않는다.

기존 provider_wait_gates/provider_engine_admission/provider_quota_recovery, recovery_outcome_contract/output_repair_outcome_contract/self_check_progress_contract와 operator recovery 시험을 먼저 읽는다. 이미 충분한 단언·원보고는 재사용하고 부족한 실제 결과 경계만 수리한다. 원보고의 경로 부재/실패, 성질과 판본을 보존한다. 원 결과·봉인/영수증·해당 원owner/권한·종료/예약 정산·null 의미를 약화하지 않는다.

## 쓰기와 확인

provider_wait/provider_engine/session_slots, repair_execution/integration, scheduled_operator/scheduler, control_protocol/observations/events와 지정 직접 시험/전용 helper·미러가 허용 범위다. core/decision/lifecycle/revisions/planning/governance/schema 및 r37-review/edges의 owner 파일과 공통 wait_rules/activities/reporting/wait_reporting은 읽기 전용이다. 기존 API와 공개 owner를 사용하고 제품대역이나 임의 schema/호환 분기로 해결을 우회하지 않는다. 범위 밖 실제 수정이 필요하면 정확 입력·관측·파일/심볼을 보고한다.

정적 대조로 충분하면 실행하지 않는다. 바뀐 성질과 직접 소비의 최소 정상/반려·조건 전후만 공식 run_tests.py --jobs 1로 확인한다. 가상 clock/기존 외부 대역을 사용하고 실제 quota 획득을 위한 반복호출, 모델/Lean/OS예약 실호출·전체 일반/freshT3/변이/T4/T5는 하지 않는다. 동일 큰 규모/전체 provider 흐름을 반복하지 않는다. 정본·미러 build/check 및 bytes, 캐시 증거 보존 후 own base 복원을 확인한다.

report는 R40/R43·r37의 위 세 종류에 대해 충분한 기존 성질/수리/정확 남김과 근거판본을 구분하고 실제 선택/row·exit/SHA·초기 오류/소프트초과·미실행을 남긴다. check.py report C:/math/.async/dm r40-r43 PASS로 마친다. 공용 문서/queue/state·Git index·과거 원자료·graphify는 수정하지 않는다. 전체4-A/B/C·PR/K/P2·G4~G8·L01/Windows1314는 이 task ID의 완료와 구별한다.

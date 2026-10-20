# 복구·운영 처분·정비 차단·모델 위반의 저장 네 가족을 마친다

실제 생산값과 저장 수신 계약의 불일치가 시험을 빠져나가지 않도록 runtime.recoveries/operational_dispositions/maintenance_fence/model_policy_violation 네 가족의 생산·검증 게시·별도 decode·내용/필드 대응을 완성한다. 복구와 정비의 공통 core/provider/저장 경계를 한 task가 소유하고 필요한 구현·직접시험·설명·미러 수리를 함께 마친다. 단순 필드 목록이나 별도 읽기 조사로 끝내지 않는다.

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md, do-math AGENTS.md·시험-지침.md를 읽는다. 원요구는 C:/math/docs/do-math/continuous-development-2026-10-13/sources의 user-decisions.md·requirements-index.json·model-policy-2026-10-14.md·document-batching-2026-10-14.md, phases/001/tasks/closure-map/evidence/requirement-state.json의 R01/1-A·1-B/K-78, C:/math/docs/do-math/시험-재편-2026-09-29/설계.md 3.3/A20이다. C:/math/.async/dm/tasks/keep-storage/evidence/families.json의 root/family를 유지한다. managers/0057/review.md, 관련 r15-r16/r29-r30/r40-r43/r49-startup/execution-storage/storage-actions 수용 보고와 실제 소스·단언을 읽고 충분한 근거를 재사용한다. 공용 소스·다른 task·외부 원자료는 읽기 전용이다.

## 지정 질문과 완료 판단

1. `CoreEngineMixin._recover_disappeared`의 recoveries는 ID map이다. 실제 미종료 실행 ID·started_at, 각 처리의 dispositions 순서·값, finished_at의 게시를 연결한다. 미착수/예약보존, local termination 미확정, 실제 정산·보존 artifact·후속 owner의 기존 성질을 유지한다. `finished_at`은 그 복구 순회를 마쳤다는 기록이며 모든 remote 실행이 종료됐다는 뜻이 아니다. dispositions의 닫힌 중첩 필드까지 실제 writer/수신/내용을 대응하고 미생산 후보 `disposition`을 현재 코드로 판정한다. local 확인과 remote unknown, 미완료 예약을 임의 정산하지 않는다. 전체 운영 복구 여정을 다시 만들지 않고 기존 장면의 저장값을 재사용한다.
2. `CoreEngineMixin._apply_operational_disposition/_complete_operational_disposition/_run_pending_operational_repairs`와 `repair_execution`은 실제 검토 제안/발급 입력의 근거·현재성을 검사해 operational_dispositions를 쓴다. 리뷰 execution_id와 target_execution_id, 원 disposition 및 obligation IDs·시각·status, 조건부 result/error/question_id/applied_at의 정확 생산·소비를 연결한다. continue·종료대기·retry/resume·task 처분·repair의 실제 필요한 표본을 기존 scheduling/repair 시험에서 얻는다. 같은 제안의 저장 계약은 `operational_dispositions.validate_disposition`이 소비하는 현재 `contracts.disposition_schema`를 따른다. 열린 EVIDENCE 내부를 임의로 닫거나 무의미한 root 필드를 채우지 않는다. 원 owner/봉인 입력·현재 checkpoint·정산 전 비중복·후속 action 한 번 게시와 실제 파일 수리의 권한/판본 확인을 보존한다. 개별 충분한 근거와 이번 새 저장 확인을 구별한다.
3. `maintenance_gate.apply_control/settle`의 maintenance_fence는 닫힌 singleton이다. 공개 quiesce의 request_id/origin/text/created_at을 정확히 저장하고 draining→blocked/quiescent, 실제 pending_executions/held_reservations/settled_at을 원 실행·예약과 대조한다. 동일 fence ID·origin·종료 장벽을 확인한 release만 현재 singleton을 제거한다. operator가 user fence를 풀지 못하는 성질, user_pause 불변 및 unknown 실행/예약을 보존하는 기존 단언을 재사용한다. quiescent와 원격 종료 확정을 혼동하지 않는다. 공개 engine/검증 저장/재시작의 최소 연결을 확인한다.
4. `provider_engine.record_model_policy_violation`은 실제 `CallEngineMixin._receive_call`의 모델 불일치를 받아 execution_id/assigned_model/reported_models를 복사하고 종료되지 않은 연구를 paused로 둔다. model_policy_violation은 열린 EVIDENCE singleton이므로 빈 properties의 역방향을 완료로 세지 않는다. 독립 원결과/배정과 정확 내용·중첩 격리·paused/이미 종료 상태·검증 저장·cold load, 명시 resume 뒤 marker 제거를 현행 실제 경로와 충분한 기존 근거로 연결한다. 가상 모델 응답을 실제 외부 호출 성공으로 보고하지 않는다. r49-startup의 독립 설치 판본/원 provider 증거와 execution-storage의 소수 보존은 유지한다.
5. 네 가족 모두 실제 production→검증 Repository 게시→새 installed_contract 객체를 받은 ResearchRepository의 첫 load로 blob decode를 연결한다. map/singleton의 manifest·원내용·필드 부재·순서·필요 artifact·옛head를 확인한다. cached publication이나 helper 반환만으로 저장 성공을 대신하지 않는다. 닫힌 필수/선택/중첩 필드는 기존 `contracts.pairs.assert_pair`와 `storage_authority_pairs._named_fields`를 재사용하며 같은 알고리즘/registry를 새로 만들지 않는다. 실제 미생산 optional과 표본 미도달을 구별하고 필요한 정리는 생산·소비·schema·시험·설명·미러까지 함께 한다. 정상 값을 schema에 맞게 삭제/보충하거나 구판 alias/default/우회검증으로 통과시키지 않는다. 제거 슬롯·타입/참조/키 오류의 정확 반려·head불변과 미생산 optional 추가 반례는 남은 불확실성에 필요한 최소 범위만 확인한다.

## 실제 선행과 수정 소유

직접 선행은 storage-actions-fix 하나다. manager0060에서 storage-actions의 입력 소유권 수리는 부분 수용했지만 공용 _named_fields의 boolean schema 오류와 공통 _ACTION/queue/wait 전체 필드·내용 대응이 남았다. storage-actions-fix가 그 공용helper·core/중앙schema/저장·직접시험·공유설명을 마친 수용판을 받은 뒤 같은 파일의 수리를 맡는다. managers/0060/review.md와 storage-actions-fix/report.json을 함께 읽는다. 다른 무관한 작업의 종료는 필요 없다. 진행 중 배정이나 미수용 workspace를 바꾸거나 소비하지 않는다.

task.json.writes의 네 가족 제공자·관련 직접 소비·저장/중앙schema·시험/helper·설명·공식 미러만 수정한다. 넓은 파일 범위는 네 가족에 필요한 수리를 위한 것이며 scheduler/권한/예약 전체 재설계가 아니다. 공통 contracts.pairs와 선행 storage helper는 읽기 전용이다. 새 storage_recovery_pairs/test_storage_recovery_pairs는 여러 검사가 실제 공유할 장면이 있을 때만 사용한다. 실제 결함이 범위 밖이면 정확한 입력·실패·심볼/영향을 남기고 독립 범위는 마친다. tasks/외부operation/질문·history·다른 저장 가족 전체 대응은 범위 밖이다.

## 최소 확인과 인계

정적 코드와 원보고가 충분하면 실행하지 않는다. 필요한 변경만 자기 workspace의 공식 scripts/run_tests.py --jobs 1로 가장 작은 관련 선택을 확인한다. 각 task jobs1·전체상한3이다. 전체 일반/fresh T3/극단변이/T4/T5·실모델/HTTP/Lean/native Git/Job·설치/OS예약·대형 저장비용 실행은 맡지 않는다. 실제 engine/Repository/StateContract/수송과 외부 포트 대역을 구별한다.

원 네 행의 현재 shape/필드·writer/수신 심볼/소스 SHA·독립 기대값·정확 시험ID/원보고판본, 유지/수리/미해결 판단을 evidence에 남긴다. 선택·고유 실제row/counts·fixture_counts·실제 관측exit/source SHA/changed_during_run/소프트초과와 최초 실패·교정판을 보존하고 서로 다른 판본 성공을 합산하지 않는다. 모든 writer 분기 도달과 최종판은 fresh T3/최종관문에 남긴다.

비용캐시는 관측 bytes를 evidence에 보존한 뒤 own base로 복원한다. 공식 build_skill_mirrors.py 생성/check·writes와 report.json을 확인하고 `python C:/math/services/async-development/check.py report C:/math/.async/dm storage-recovery`를 통과시킨다. 공용 source/context/plan/seams/queue/state·다른 task·engine·Git index/commit·graphify·기존 연구는 수정하지 않는다. manager가 통합·수용한다. 원84의 나머지·관찰4/다른 원요구/K/P2·G4~G8·L01/Windows1314·최종review는 별도 남는다.

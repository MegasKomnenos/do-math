# 대화 임대·유실 세대·pause·가용성의 저장 계약 5가족을 마친다

사용자 목표는 실제 생산값과 저장 수신 계약의 어긋남이 시험을 빠져나가지 않게 만드는 것이다. 대화 연결과 유실에 따른 제어 상태를 같은 생산자·직접시험 묶음으로 판정하고 필요한 수리와 최소 확인까지 마친다. 가족마다 작은 task나 새 registry를 만들지 않는다.

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md, do-math AGENTS.md와 시험-지침.md를 읽는다. 원자료는 C:/math/docs/do-math/continuous-development-2026-10-13/sources의 user-decisions.md·requirements-index.json·model-policy-2026-10-14.md·document-batching-2026-10-14.md, phases/001/tasks/closure-map/evidence/requirement-state.json의 R01/1-A·1-B/K-78과 C:/math/docs/do-math/시험-재편-2026-09-29/설계.md 3.3/A20이다. C:/math/.async/dm/tasks/keep-storage/evidence/families.json의 원 root/family를 유지하며 storage-lifecycle의 수용 보고·근거와 managers/0051/review.md를 읽는다. 이 경로들은 읽기 전용 원자료다.

## 대상과 선행

대상은 research.conversation_loss_policy, runtime.conversations, runtime.lost_conversation_generations, runtime.user_pause, runtime.availability의 정확한 5가족이다. conversations는 닫힌 map record, lost_conversation_generations는 ID→NAT singleton이다. 나머지는 metadata이며 conversation_loss_policy는 TEXT, user_pause는 boolean/object, availability는 state 필수·reason/next_owner 선택의 닫힌 객체다. metadata라는 저장 모양을 scalar 타입이라고 오해하지 않는다.

storage-lifecycle만 선행이다. 수용된 실제 lifecycle 생산·검증 게시·새 contract reader decode 방법과 직접시험을 소비한다. execution-fields→storage-academic의 미수용 사본을 읽거나 종료를 기다리지 않는다. 두 작업이 소유한 core/call/governance/academic/repair_execution/scheduler/중앙 record_schemas와 정본 설명, 공통 pairs/storage_records는 읽기 전용이다. 이번 다섯 가족의 현재 스키마에는 수리를 전제할 근거가 아직 없다. 해당 경계에서 실제 결함을 찾으면 정확한 입력·원인·필요 파일을 남기고 자기 독립 범위를 마친다. 단순 읽기나 가상의 결함을 선행으로 추가하지 않는다.

clock_guard 객체·research.lifecycle 전체 역방향·events/pending_events/event_cursor·processed_controls/extended_controls·tasks/queue와 원84가족 중 다른 가족은 이 배정으로 닫지 않는다. 이들 기록을 생산 경로에서 함께 읽거나 저장한 사실과 해당 가족 전체의 완료는 구별한다.

## 판단과 구현

1. 현재 실제 생산자와 저장 소비자를 먼저 대응한다. LifecycleEngineMixin._conversation_control/_lose_conversation/_check_conversations/_conversation_live/_apply_extended_control/_resume_lifecycle/_activate_initialization/_refresh_readiness, InitializationEngineMixin._initialization_control, initialize_state와 Repository·설치 StateContract를 확인한다. availability의 core/call 쓰기와 user_pause의 다른 쓰기도 현재 source에서 읽어 분류한다. 과거 표의 references는 검색 후보이며 실제 root 생산 인증이 아니다. 최종 fresh T3가 소비할 정확 심볼·SHA·시험 ID/판본을 남긴다.
2. r49-startup의 실제 lease 만기/restart, r39-report의 명시 user pause/재개, r47-r48의 수신시각과 처리시각 구별, r39-r42의 clock pause 중복 방지 및 현재 lifecycle 직접시험의 충분한 성질을 원보고·현재 source와 대조해 먼저 재사용한다. 긴 활성화/승인/기동 시나리오를 새 helper마다 반복하지 않는다. 실제 생산→검증 저장→별도 decode·독립 내용 단언이 빠진 부분만 보완한다. 기존 helper와 원자료를 읽되 불변의 역사 성공을 현행 실행 횟수에 더하지 않는다.
3. conversations의 attach/heartbeat/explicit detach/lease expiry와 새 generation의 실제 record를 연결한다. caller ID·generation·정확 policy·lease_seconds·source_ref·attached_at/last_heartbeat_at/lease_expires_at/lost_at/loss_reason·status를 독립 입력/시각 기대값과 비교한다. heartbeat가 현재 connected 세대만 갱신하고, 만기/유실 뒤 같은 세대가 되살아나지 않으며 새 연결 후 resume이 가능한 의미를 보존한다. source_ref가 어느 신호를 가리키는지 실제 쓰기대로 판단한다. control_contracts의 공개 lease는 양의 정수다. private 함수의 int/float 허용만 보고 공개 입력 결함으로 단정하지 말고 실제 입구와 저장 경계를 확인한다. 부동소수 저장 허용·자동변환·구판 alias를 추가하지 않는다.
4. conversation_loss_policy는 초기 부재, 명시 adopt/attach의 pause·continue_authorized 생산, 실제 연결 상실의 소비를 구별한다. continue_authorized는 이미 유효한 권한으로 계속한다는 뜻이며 새 권한을 부여하지 않는다. lost_conversation_generations는 pause 정책에서 실제 잃은 세대를 ID에 보존하는 값이며 새 연결의 생존 판단과 연결한다. 빈 mapping.properties를 역방향 성공으로 세지 말고 독립 ID/정수값·새 세대·옛 head 불변을 검사한다. 다른 conversation ID와 중첩 실행의 session ID는 다른 계약이다.
5. 명시 사용자 pause의 실제 request_id/reason/created_at를 원 요청에 결박하고, 사용자 resume 뒤 제거·옛 head 보존·자동 resume으로 사용자 정지를 해제할 수 없는 기존 성질을 유지한다. user_pause의 허용 boolean과 실제 객체 작성자를 구별하고 열린 object에 임의의 닫힌 필드 의무를 새로 만들지 않는다. availability의 초기화 불충족 blocked/reason/next_owner, 실제 활성화 available, clock 차단 등의 현재 생산을 확인한다. 상태·사유·담당자 내용과 선택 필드 부재/제거를 검사하며 단순 dict가 저장됐다는 사실로 끝내지 않는다. runtime status나 clock_guard 가족 전체를 대신 검증한 것으로 쓰지 않는다.
6. 정상 표본은 실제 생산자→검증된 Repository initialize/save_with_state→새 installed_contract를 받은 reader의 첫 load로 이어진다. 실제 저장 경로는 각 metadata의 <root>/_state/metadata.json#/record/<name>, conversations의 map record, lost_conversation_generations의 singleton이다. 새 wrapper/registry는 필요 없다. conversations/availability의 required+optional 전체 필드와 실제 생산 필드의 역방향은 공통 contracts.pairs.assert_pair를 재사용한다. value·open mapping/object에는 명시적인 값 단언을 사용한다. 가족별 checker/validator와 검증 게시를 연결하되 같은 전체 상태 검증을 불필요하게 반복하지 않는다. 정상 변경 후 옛 head/원값, 정확 반려 대상·원인과 게시 전 head 불변을 보존한다. 비검증 publish는 필요한 손상 read 반례에만 쓴다.
7. 자기 writes 안의 실제 결함은 구현·소비 시험·공식 미러·최소 확인까지 한 번에 고친다. 기존 직접시험 보완을 우선하며 전용 storage_conversation_pairs/contract 모듈은 실제 공유가 필요할 때만 만든다. 단언 약화·정상 필드 삭제·사후 fixture 필드 보충으로 역방향을 통과시키지 않는다. 코드와 기존 근거로 충분한 경우 새 실행 없이 판정한다. 모든 쓰기분기 전건 도달을 측정하지 않았다면 완료라고 하지 않는다.

## 최소 확인과 제출

제품 수정은 자기 workspace의 task.json.writes에 한한다. 기존 수용된 metadata5·lifecycle8의 단언을 보존한다. 공식 scripts/run_tests.py --jobs 1로 남은 불확실성에 필요한 가장 작은 관련 ID만 실행한다. execution-fields→storage-academic과 본 task의 최대2개 동시 시험·각jobs1이며 전체 상한3을 지킨다. 전체 일반/fresh T3/전체변이/T4/T5·유료모델/HTTP/native Git/Lean/Job/설치/OS예약·대형 비용 실행은 하지 않는다. 실제 engine/Repository/StateContract와 Git/clock/host/Calls 대역을 구별한다.

5가족별 현재 shape·생산/수신·독립 입력축·필드/내용 단언·재사용 원보고/판본·수리 또는 정확 남김을 report/evidence에 남긴다. 최초 실패/fixture 오류·선택/고유 실제 row·counts·관측exit·source SHA·changed_during_run·소프트초과를 보존하며 서로 다른 판본의 성공을 합산하지 않는다. 필요한 확인 뒤 반복하지 않는다. 비용캐시는 관측을 evidence에 보존한 뒤 own base로 복원하고 공식 build_skill_mirrors.py 생성/check와 실제 쓰기 범위를 확인한다.

protocol 형식 report.json을 작성하고 `python C:/math/services/async-development/check.py report C:/math/.async/dm storage-conversation`을 통과시킨다. 공용 context/plan/seams/queue/state·다른task·engine·Git index/commit·graphify·기존 연구는 수정하지 않는다. manager가 통합·수용과 공용 설명을 맡는다. 다른 가족/원요구/K/P2·G4~G8·L01·Windows1314·최종review는 남는다.

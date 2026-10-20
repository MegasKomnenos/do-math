# 사건 게시·소비와 제어·편입 영수증의 저장 다섯 가족을 마친다

실제 생산값과 저장 수신 계약의 불일치가 시험을 빠져나가지 않도록 runtime.events/pending_events/event_cursor/control_receipts/integrations 다섯 가족의 생산·검증 게시·복원·내용/필드 대응을 완성하고 필요한 수리를 같은 task에서 마친다. 공통 core/Repository/중앙schema의 작은 보완을 가족마다 나누지 않는다.

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md, do-math AGENTS.md·시험-지침.md를 읽는다. 원요구는 C:/math/docs/do-math/continuous-development-2026-10-13/sources의 user-decisions.md·requirements-index.json·model-policy-2026-10-14.md·document-batching-2026-10-14.md, phases/001/tasks/closure-map/evidence/requirement-state.json의 R01/1-A·1-B/K-78 및 C:/math/docs/do-math/시험-재편-2026-09-29/설계.md 3.3/A20이다. C:/math/.async/dm/tasks/keep-storage/evidence/families.json의 root/family를 유지하고 managers/0054/review.md와 선행 두 task의 수용 보고·현행 소스를 읽는다. 공용 소스·외부 원자료·다른 task 기록은 읽기 전용이다.

## 실제 선행과 범위

execution-storage는 core_engine와 실행 입장/수신 및 해당 직접시험의 수용판을 제공한다. storage-control-state는 lifecycle/초기화·Repository/StateContract·중앙schema와 직접 저장/제어시험의 수용판을 제공한다. 두 배정의 파일을 이 작업에서도 필요한 수리까지 맡으므로 두 결과의 수용이 실제 선행이다. 수용된 파일을 시작 사본으로 받고 미완성 workspace를 소비하지 않는다. 다른 무관한 task의 종료는 필요 없다.

현재 다섯 가족의 구현·소비·직접시험·설명·공식 미러만 task.json.writes 안에서 수정한다. 넓은 이벤트 제공자 파일 목록은 관련 쓰기/소비 수리를 허용하기 위한 범위이며 다른 기능 전반을 재설계하라는 뜻이 아니다. 기존 실행92필드 정리·독립성, 학술 goal3필드 제거, 권한/지식의 현행 schema와 수명/시계/원문/제어 처리의 수용 성질을 유지한다. 계획의 다른20미배정 가족·관찰4·최종판 전체검증은 이 작업으로 종결하지 않는다.

## 판정할 내용

1. 현재 events는 ID 있는 list record, pending_events는 REFS singleton, event_cursor는 NAT metadata다. EventPublisher.assign_sequences_in_place는 Repository의 후보 runtime에 새 event_seq를 붙이고 cursor를 갱신한다. 이미 게시된 사건의 내용/순서/번호는 보존하며 pending은 아직 소비되지 않은 사건 ID다. 게시가 pending을 비우는 것으로 오인하지 않는다. 실제 LifecycleEngineMixin._lifecycle_event, planning.collect_due_events/record_due_events/schedule_reconsideration, core의 제어/제출·실패 경로와 다른 실제 event writer를 수신 required+optional에 연결한다. provider raw stream의 events나 임의 fixture를 runtime.events 생산자로 세지 않는다. 열린 basis/evidence도 원값/참조 내용은 독립적으로 검사하되 임의 닫힌 필드를 추가하지 않는다.
2. 수용된 원보고·현재 단언으로 충분한 event numbering/불변/참조/실패 성질은 재사용한다. 새 확인은 실제 생산 사건을 검증 Repository에 게시하고 별도로 설치한 계약을 가진 reader의 첫 load로 blobs를 decode하는 연결에 집중한다. 연속1..n/cursor=n, 순서·원내용·옛head, 게시 실패/CAS 재시도 때 caller 불변과 원 pending, 새 사건만 번호부여, 정확 참조/타입 반려를 보존한다. event_seq는 원 writer가 아니라 게시 경계의 정당한 추가필드라는 점을 표에 구별한다. scalar/ID배열의 빈 properties를 역방향 성공으로 세지 않는다.
3. _consume_action_events는 실제 입장한 action.event_refs만 pending에서 제거하고 history에 실행ID/시각을 남긴다. task_new_input의 request_id와 현재 newinput이 같을 때만 표지를 제거하며 나중 요청은 보존한다. 준비/예약 실패가 소비로 처리되지 않음과 재시작 뒤 비재생의 충분한 기존 근거를 재사용한다. 현재 pending 계약은 문자열 참조 배열인데 dict 항목 보존 분기가 남아 있다. 이 분기의 현재 소비 의미/생산 전제를 판정하고 불필요한 구판 허용이면 관련 수리와 확인을 묶는다. 가상 dict producer나 옛 API를 추가하지 않는다. history/tasks/queue 전체 가족은 범위 밖이다.
4. control_receipts는 _publish_control_request의 실제 실행/권한/시계·수송 요청을 받아 게시한 map이다. 같은 request_id·exact_content_hash의 재전달과 내용 충돌, accepted/rejected 및 preview처럼 저장하지 않는 반환을 구별한다. safe_request의 capability 제거와 나머지 원문/중첩 payload 보존, execution/kind/state/request_id/request_sha256/received_at/parent_snapshot, 실제 제출 분기가 더하는 필드를 현재 코드에 연결한다. 임의 정상 receipt를 조립하지 말고 기존 running_work/실제 수송·owner 경로를 재사용한다. 저장 CAS 완료가 영수증 승인의 기준이며 ack 유실 뒤 durable 재조회, feedback 재전달, 원문·head 불변과 정확 한 번의 적용 성질을 보존한다. grant_id/snapshot/publication_id/payload/transport_id 등 허용 optional의 실제 root 작성 여부를 판정하되 응답 projection이나 request 안 동명 필드와 혼동하지 않는다.
5. integrations는 integration.apply_bundles가 실제 허용된 bundle 적용 뒤 기록한 map이다. execution_id/payload_sha256/members/input_snapshot과 조건부 response_sha256를 실제 봉인 output·번들/입력에 연결하고 독립 직렬화/hash 및 정확 member 순서/집합 의미를 확인한다. 일치 재전달의 비중복/원 receipt 보존, 변경 payload 반려·실패 bundle의 미기록, 부분 수용 뒤 재시도와 현재 authority/impact 검사를 기존 충분한 근거부터 재사용한다. direct apply_bundles의 주입 domain callback과 실제 core 적용 경로를 구별한다. null input_snapshot의 현행 조건을 삭제하지 않는다. 실행 레코드의 폐기된 integration_id 슬롯을 복원하지 않는다.
6. 실제 수신 required+optional 및 닫힌 중첩 필드마다 생산·게시·내용 단언을 대응한다. 공통 contracts.pairs.assert_pair와 기존 _named_fields 등 실제 helper를 소비하고 같은 알고리즘·새 registry를 복제하지 않는다. 표본 공백과 실제 미생산 필드를 구별하고 불필요한 슬롯은 중앙schema·직접소비·시험·설명·미러까지 함께 제거한다. 정상 생산필드 삭제, 검증 우회, alias/default/자동변환으로 시험을 통과시키지 않는다. 같은 역방향에 미생산 optional 하나를 추가한 반례와 제거필드의 정확 게시 반려를 필요한 최소 범위로 확인한다.

## 최소 확인과 인계

기존 test_record_family_storage/test_engine_event_guards/test_engine_control_receipts/test_submission_integration_bundles와 관련 scheduling/planning/public receiver 시험을 먼저 읽는다. 긴 초기화/위임·승인·검토 여정을 필드별로 반복하지 않는다. 새 storage_event_pairs와 계약시험은 필요한 공유가 있을 때만 만들며 실제 producer 표본을 보관한다. 정적 분석과 유효 원보고가 충분하면 실행하지 않는다. 남은 불확실성은 자기 workspace의 공식 scripts/run_tests.py --jobs 1에서 가장 작은 관련 ID로 확인한다. 전체일반/fresh T3/전체변이/T4/T5·새 실제 모델/HTTP/Lean/Job/native Git/설치/OS예약·대형 저장 비용 실행은 하지 않는다.

실제 engine/검증 저장/봉인과 외부 Git/clock/host/compiler/model 포트 대역을 보고에서 구별한다. 최초 실패·fixture 오류/교정판, selected/실제 고유row/counts/fixture_counts/관측exit/source SHA/changed_during_run/소프트초과를 보존하고 서로 다른 판본 성공을 합산하지 않는다. 선행 두 task는 종료 뒤이므로 이 큐의 시험동시성은 본 task 하나며 이후 독립 배정도 전체 상한3·각jobs1을 지킨다. 비용캐시는 evidence 보존 뒤 own base로 복원하고 공식 build_skill_mirrors.py 생성/check와 쓰기 범위를 확인한다.

evidence에는 원 다섯 행의 현재 shape/정의·writer/수신 심볼·소스SHA·정확 시험ID/판본, 유지/수리/제거 이유와 남은 질문을 기록한다. 전체 쓰기지점/분기 도달은 최종 fresh T3에서 별도 판단한다. protocol 형식 report.json과 `python C:/math/services/async-development/check.py report C:/math/.async/dm storage-events`를 마친다. 공용 context/plan/seams/queue/state·다른task·engine·Git index/commit·graphify·기존 연구는 수정하지 않는다. manager가 통합·수용한다.

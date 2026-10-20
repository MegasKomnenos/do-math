# 목적과 완료할 결과

R08/2-A의 공개 제어와 제어 수송이 잘못된 입력을 자기 계약의 반려 형태로 처리하고, 같은 항목을 중복 적용하지 않으며, 뒤의 정상 제어를 실제 owner/store까지 진행시키는지 판단한다. 현재 정의·단언·유효한 원보고가 충분하면 유지하고, 빠진 입력/단언이나 실제 반려 결함만 같은 task에서 수리한다. 공개 action별·오류 종류별로 작업을 쪼개거나 등록표를 실행 증거로 취급하지 않는다.

## 입력과 수정 범위

SESSION_JSON의 workspace와 고정 inputs/context.md·plan.md·seams.md, task.json이 기준이다. 상대 제품 경로는 자기 workspace다. C:/math/docs/do-math/continuous-development-2026-10-13의 sources/user-decisions.md·requirements-index.json, phases/001/tasks/closure-map/evidence의 requirement-state.json[2-A]·tracking-state.json[R08]·prior-review-state.json[PR07]·evidence-catalog.json이 읽기 전용 원자료다. PR07은 B15 ingress_integration, B23 delivery_recovery_integration, B59 control_detail_integration의 해당 제어 slice만 연결한다. 실제 hunk→현재 caller/수신자→원보고의 정확 ID/판본을 확인하고 없는 Temp 원보고의 수치를 성공으로 합산하지 않는다. 원문의 repo:docs/...는 C:/math, run:은 위 continuous-development 루트다.

manager 0011이 r10의 관찰·공급자 입구 수리를 수용했다. 그 report/evidence와 manager review는 R10과 R08의 책임을 구분하는 입력이다. tracker receipt/event 양순서 성공을 서로 다른 control transport의 충돌/재전달 증거로 쓰지 않는다. r03-fix는 저장 schema/pairs, r14는 parallel/scheduler 진행성을 별도 사본에서 수행한다. 두 task의 중간 결과를 소비하거나 배정을 바꾸지 않는다. r08은 이 결과를 필요로 하지 않으므로 depends_on=[]이다.

수정 가능한 시험은 unit/test_ingress_rejection.py·test_engine_control_transport.py·test_engine_control_shapes.py, sim/test_ingress_consumption.py·test_engine_control_shapes.py·test_engine_controls.py·test_engine_control_receipts.py, flows/test_engine_nested_control_consumption.py와 task.json에 명시한 좁은 입력/fixture helper 및 미러다. 기존 support.ingress·engine_shapes·engine_nested_controls·engine_control을 우선 재사용한다. 새 support/control_ingress.py는 실제 중복을 줄일 필요가 있을 때만 만든다. support.ingress를 바꾸면 r10의 NOT_TEXTS와 기존 제출/native 소비 성질을 보존한다. 범위 밖 helper는 읽기 전용이다.

현재 외부 도달 입력으로 반려 계약을 깨는 결함을 관측한 경우에 한해 do_math/core_engine.py·control_transport.py·control_contracts.py·control_protocol.py와 미러의 해당 경로를 함께 수리할 수 있다. 일반 리팩터링이나 반려 정책 변경은 배정하지 않는다. core_engine의 관찰/제출 및 record schema, parallel/scheduler는 이 task의 수리 대상이 아니다. 범위 밖 제공자 수정이 필요하면 정확 입력·기대/실제·심볼·필요 쓰기를 보고하고 허용된 유효 결과를 마친다. 오류를 통째로 삼키거나 결함을 정상 기대값으로 바꾸지 않는다.

## 답할 질문

1. 현재 control_contracts.PAYLOADS와 configure 정본으로 공개 action 모집단을 확인한다. 원문의 역사적 14라는 수를 현재 등록부에 강제하지 않는다. validate_control_payload→engine.control/core_engine.submit_control→실제 inbox→ResearchEngine.process_controls/_apply_inbox, 별도의 ControlTransport.worker_submit/receive/pump/worker_receipt→_publish_control_request 경계를 구분한다. 공개 제출 전 ValueError와 owner가 저장한 반려/history/영수증은 서로 다른 관찰값이다.
2. 2-A의 세 입력 부류를 현재 필드/상태에 대응한다. 스키마의 비객체·None·0·잘못된 scalar/enum·실제 경로 필드, 형식 통과 뒤 적용 전제가 소실된 종결/삭제 대상, 동일 ID의 같은/다른 내용과 두 transport·양쪽 처리 순서를 다룬다. 실제 적용 전제 소실은 공개 전이 또는 현행 생산 경로로 도달시킨다. 임의 내부 del로 공개 도달을 주장하지 않는다. 등록표·unit 형식 전건·대표 owner 경로가 각각 입증하는 범위를 구별한다. 원문이 요구하지 않는 무한 입력/일정 전수 증명은 만들지 않는다.
3. 정확 반려 사유/구조, 실제 한 번 소비·원 bytes 보존·상태/예약/도메인 효과 불변, 재전달·receiver 재시작 뒤 불변, 뒤 정상 제어의 적용 및 durable reload를 현재 단언에 연결한다. 같은 receipt를 다시 돌려주는 것이 정상인 pump를 호출마다 빈 목록이어야 한다고 바꾸지 않는다. received·previewed·accepted·rejected·closed의 의미와 CAS 성공 전에 accepted가 게시되지 않는 계약을 보존한다. 정상 대조군으로 무관한 전제/fixture 실패를 배제한다.
4. 기존 tests/unit/test_engine_control_transport.py의 rewritten rejection/restart, 전송 간 ID 점유, 경쟁 payload, close와 도착 경합, 발급 self-check replay/충돌 및 sim/test_engine_control_receipts.py의 CAS/양순서 단언을 먼저 읽는다. 충분한 성질은 원보고·현재 판본을 연결해 재사용한다. 실제 결함이나 공백이 확인된 입력/단언만 보완하고 최소 공식 ID로 확인한다. 동시 실행 시험이 정확 양순서 강제를 입증하는지, 단순 존재/개수 단언이 정확 사유·내용까지 확인하는지 구별한다.
5. PR07의 해당 제어 slice와 관련 K/P2만 판정한다. R09의 제출 확장/참조, R10 관찰/provider의 이미 수용한 성질, 모든 action의 도메인 업무 의미, R14의 진행성 상한을 새로 종결하지 않는다. 미확인 축은 구체적인 입력·도달 전제·수신 위치와 함께 남기며, 충분한 기존 성질·수리 완료·정확 미결·최종 판본 대기를 구분한다.

## 확인과 제출

정적 분석으로 충분하면 실행을 추가하지 않는다. 수정한 기능에 실행이 필요하면 자기 workspace의 scripts/run_tests.py, jobs1로 최소 입력/공식 ID를 선택한다. 실제 transport·validator·owner·Repository를 대역으로 바꾸지 않는다. 기존 외부 Job/CLI/Git 포트 대역은 재사용한다. 새 실제 모델·Lean·예약·네트워크, 전체 일반/T3/변이/T4/T5는 배정하지 않는다. 충분한 검사를 새 이유 없이 반복하지 않으며 시간 기준은 soft다.

실행 중 소스를 고정하고 선택 ID·실제 row·exit·판본·실패·fixture 오류·미실행을 보존한다. 공유 helper/runtime 변경 시 실제 직접 소비자의 보존 성질을 읽고 남은 불확실성만 최소 확인한다. 서로 다른 판본의 성공을 단일 최종 전체 성공으로 합산하지 않는다. 정본/미러는 공식 build_skill_mirrors.py --target .agents로 함께 생성하고 --check --target .agents를 확인한다. 미러 byte 일치로 충분하면 시험을 반복하지 않는다. 비용 캐시 두 개는 evidence에 보존한 뒤 자기 base로 복원한다.

공용소스·공용 context/plan/seams/queue/state·engine·다른 task·과거 원자료·Git index를 수정하지 않으며 graphify도 갱신하지 않는다. report.json에는 실제 결과·판단 이유·검증 방법과 한계·변경·후속 판단을 남기고 python C:/math/services/async-development/check.py report C:/math/.async/dm r08의 PASS를 확인한다. G4~G8, L01 Q1/Q2·원문 UTF-8 byte, Windows1314 symlink 실반려 미검사는 유지한다.

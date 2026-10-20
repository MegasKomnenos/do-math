# 입력·자료와 보류된 확장 값의 실제 저장 계약을 마친다

사용자 목표는 실제 생산값이 검증 켜진 저장소를 통과하고, 수신 스키마에만 남은 필드나 내용 검사가 없는 저장 경로가 시험을 빠져나가지 않게 하는 것이다. research.sources, runtime.inputs, runtime.private_insights, runtime.pending_kind_checks 네 가족을 같은 core 입력/확장 생산자와 저장 수신 경계로 묶는다. 제품 결함과 필요한 직접시험·설명·공식미러를 한 task에서 마친다. 필드별 작은 후속 task로 나누지 않는다.

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md, do-math AGENTS.md·시험-지침.md를 읽는다. 원요구는 C:/math/docs/do-math/continuous-development-2026-10-13/sources의 user-decisions.md·requirements-index.json·model-policy-2026-10-14.md·document-batching-2026-10-14.md와 C:/math/docs/do-math/시험-재편-2026-09-29/설계.md 3.3/A20, phases/001/tasks/closure-map/evidence/requirement-state.json의 R01/1-A·1-B/K-78이다. 읽기 전용 근거는 C:/math/.async/dm/tasks/keep-storage/evidence/families.json, keep-inputs/r31-r33/r44-fix/storage-authority/storage-events/execution-storage의 보고·근거와 managers/0055/review.md다. 과거 원보고와 당시 판본을 보존한다.

## 지정 질문과 완료 판단

1. 현재 네 가족의 실제 생산자·수신 schema/checker·저장 위치·소비를 연결한다. sources와 inputs는 list item record, private_insights는 cycle ID→열린 항목 배열의 singleton, pending_kind_checks는 닫힌 item 배열 singleton이다. root의 빈 properties를 보고 역방향 의무가 없다고 판단하지 않는다. 열린 임의 내용에 허구의 닫힌 필드 목록을 만들지도 않는다. 현재 required/optional과 중첩 item의 필드를 공통 contracts.pairs.assert_pair로 실제 표본에 연결하고, 미생산 optional 추가가 같은 검사에서 실패하는지 최소 반례로 확인한다.
2. sources는 initialize_state의 초기 빈 목록, core_engine.initialize_instance의 실제 파일 추가와 CoreEngineMixin._apply_inbox의 source 신규/동일내용/변경을 원 독립 bytes·SHA·name·ID·path·revision·history·source_ref와 연결한다. 실제 source.bin/초기 artifact와 저장 record, 별도 reader의 decode와 옛head를 비교한다. Unicode/CRLF/비텍스트 자료의 현행 정규화 계약은 source_values/normalized_source_bytes의 정본을 소비한다. 같은 내용의 요청은 revision을 올리지 않으며 실제 변경은 기존 ID와 역사 내용, 과제/지식 현재성의 기존 의미를 보존한다. created_at 등 optional의 실제 writer 여부는 조사 질문이지 미리 확정한 제거 목록이 아니다.
3. inputs는 initialize_state의 최초 원문과 공개 input→실제 inbox 적용의 추가 입력을 사용한다. 원 text/config, ID/시각/accepted_order/origin/instance_id/sha256의 실제 생산 여부와 의미를 독립 입력·순서·해시에 대조한다. 수신 전 제어요청과 저장 inputs record를 혼동하지 않는다. 동일 재전달, 뒤 입력 및 재시작, 영구 close 반려의 원입력/옛head를 기존 근거에서 먼저 재사용한다. 비어 있는 optional 일치나 저장 직전 수동 필드 보충으로 역방향을 통과시키지 않는다. sources/inputs를 소비하는 원문 현재성·역할입력 근거는 보존한다.
4. private_insights는 실제 검토 실행의 research_insights 확장과 _apply_extensions를 통해 cycle별 보류를 생산하고 검증 저장/다른 reader로 적재한다. source_execution과 원 통찰 내용·순서·격리, 진행 중 비공개 유지와 completed/unresolved 후 원 작성자에 연결된 해제·삭제·발행/계획을 독립 기대값으로 확인한다. 기존 test_review_released_insights의 수동 보류 fixture는 그 국소 성질의 근거로 보존하되 실제 생산·저장의 대체로 쓰지 않는다. 현행 producer가 만들 수 없는 구판 전용 분기/fixture가 있으면 실제 호출·의미·기존 검사를 근거로 유지/제거를 판단한다. 과거 구현 호환성을 새 요구로 만들거나 원 작성자의 불량 항목을 다른 작성자에게 귀속시키지 않는다.
5. pending_kind_checks는 _propose_kind의 실제 제안·등록·검사 예약과 _apply_kind_definition_check의 approved/revision_required/unresolved 소비를 저장 전후에 연결한다. definition ID/hash, family/token/source_ref/actor_ref와 현재 정확 정의를 읽은 독립 checker를 유지한다. 같은 이름의 실행 필드와 pending item의 execution_id optional을 혼동하지 않는다. 다른 정의의 pending 항목은 유지하고 해당 항목만 해소되는지, 잘못된 정의/hash/독립성 입력이 상태와 head를 바꾸지 않는지 필요한 기존 근거를 재사용·보완한다. 종류 정의 가족 자체는 storage-authority의 수용 근거를 재사용한다.
6. 실제 생산 표본을 검증 게시한 뒤 새 installed_contract/ResearchRepository reader로 적재·decode하고 기존 공통 Pair에 전달한다. 원 artifact/참조/hash·옛head·재시작·정확 반려를 대상 의미에 맞게 연결한다. 닫힌 필드와 열린 내용/참조 검사는 별개다. 별도 registry/역방향 알고리즘, 모든 필드를 채운 거대 fixture, 시험 모듈 간 import, alias/default/검증 예외를 추가하지 않는다. 미생산 필드를 확인하면 schema·소비자·직접시험·정본설명·미러를 같은 변경에서 정리한다. 실제 쓰이지만 기존 표본에 없는 필드를 지워서 검사만 통과시키지 않는다.

## 선행과 수정 소유

직접 선행은 storage-events 하나다. 그 task는 core_engine/initialization/Repository/중앙schema/공유설명과 저장 직접시험을 소유하고, storage-control-state와 execution-storage 수용판을 간접 선행으로 소비한다. 본 task도 같은 제공자·schema의 수리가 필요할 수 있어 그 수용판에서 시작한다. 진행 중 storage-control-state와 대기 중 storage-events의 배정은 바꾸지 않으며 미수용 workspace를 소비하지 않는다. 공유 파일의 중복 수정 방지가 실제 선행 이유이며 무관한 task 종료를 기다리는 장벽은 아니다.

task.json의 명시된 core/초기화/종류·통찰/자료 제공자, 중앙schema·저장, 관련 단위/sim/flow/전용 계약시험·helper와 이음새 설명을 소유한다. 기존 source/input/현재성·kind·통찰 시험을 먼저 재사용하고 전용 helper는 실제 공통 장면이 필요할 때만 둔다. 공통 contracts.pairs와 다른 수용된 helper는 읽기 전용이다. writes 밖에서 실제 결함이 확인되면 정확한 최소 반례·필요한 경로·사용 영향만 보고한다.

## 필요한 확인과 인계

기존 원보고와 정적 판단으로 충분하면 실행하지 않는다. 보완한 실제 동작의 불확실성만 workspace의 공식 scripts/run_tests.py --jobs 1로 최소 관련 선택을 확인한다. 동시 공식시험 상한3, 본 task는1이다. 전체 일반/fresh T3/극단변이/T4/T5·유료 모델/HTTP/실Lean/native Job/설치/OS예약·대형 비용 실행은 배정하지 않는다. 실제 producer/검증/저장과 외부 포트 대역을 구별한다.

가족별 표에는 현재 schema 필드·생산 심볼/파일 SHA·수신/저장·독립 기대값·정확 시험ID/원보고판본·유지/수리/구체적 남김을 남긴다. 원문 요구/K-78에 연결하되 유한 표본을 모든 역할/선택값/쓰기분기 도달로 확대하지 않는다. 최초 실패/준비 오류·교정판, selected/고유 실제row/counts·실제 실행 로그의 exit·source SHA·changed_during_run·소프트초과를 보존한다. successful로 exit를 추정해 관측값이라고 쓰지 않는다. 별도판본 통과를 합산하지 않는다.

비용캐시는 관측을 evidence에 보존한 뒤 own base로 복원한다. 공식 build_skill_mirrors.py 생성/check와 writes를 확인하고 protocol 형식 report.json을 작성해 `python C:/math/services/async-development/check.py report C:/math/.async/dm storage-inputs`를 통과시킨다. 공용 source/context/plan/seams/queue/state·다른task·engine·Git index/commit·graphify·기존 연구는 수정하지 않는다. 다른16미배정 가족과 관찰4의 최종판·전쓰기분기 fresh T3·다른 원요구/K/P2·G4~G8·L01/Windows1314·최종review는 별도다.

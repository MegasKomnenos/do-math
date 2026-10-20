# 실행 저장의 남은 19필드와 전체 역방향 연결을 마친다

사용자 목표는 실제 생산값이 검증 켜진 저장소를 통과하고, 수신 스키마에만 남은 필드와 의미를 검사하지 않는 쓰기가 시험을 빠져나가지 않게 하는 것이다. execution-fields의 미생산10슬롯 제거·독립성 소비 수리·대표 저장 단언은 수용됐다. 현재 executions는 required8+optional84=92필드다. 남은19필드의 실제 생산→검증 저장→별도 load→독립 기대값 연결과 executions 전체 필드 역방향의 빠짐을 한 task에서 마친다. 이미 확인한73행을 처음부터 재조사하거나 필드마다 후속 task를 나누지 않는다.

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md, do-math AGENTS.md·시험-지침.md를 읽는다. 원요구는 C:/math/docs/do-math/continuous-development-2026-10-13/sources의 user-decisions.md·requirements-index.json·model-policy-2026-10-14.md·document-batching-2026-10-14.md와 C:/math/docs/do-math/시험-재편-2026-09-29/설계.md 3.3/A20, phases/001/tasks/closure-map/evidence/requirement-state.json의 R01/1-A·1-B/K-78이다. 직접 입력은 C:/math/.async/dm/tasks/execution-fields/report.json·evidence/judgment.md·execution-fields.json·verification.json, storage-execution의 보고·historical-rows.json과 managers/0052/review.md·verification-review.json이다. 원자료와 공용 소스는 읽기 전용이다.

## 범위와 완료 판단

1. 다음19개를 현재 producer와 의미별로 묶는다. 입력/근거5개는 academic_requirements_sha256/delegation_input_sha256/input_solution_basis/input_basis/additional_audit_input, 역할 결과/운영7개는 output/runner/operational_continuation/pending_operational_disposition/preserved_reason/failure/error_kind, 공급자 사용량4개는 usage_segments/model_usage_reported/usage_scope/reported_models, 관찰/정지3개는 observation_fact_sequence/observation_rules/stop_reason이다. 앞 task의 필드표는 정확 생산 심볼·SHA와 구체적인 남김을 제공한다. 이름 검색, 다른 record의 같은 필드, runner-only 성공, 저장 직전 fixture 보충, optional 부재 일치는 이 질문의 완료 근거가 아니다.
2. 기존 직접시험·원보고에서 이미 충분한 성질과 판본을 먼저 재사용한다. _prepare_call의 학술 요구/위임 입력 hash·research_plan의 현재 solution basis·kind 입력 basis, governance_engine._bind_governance_input의 비빈 추가감사 입력을 원 입력/봉인/독립 기대값에 연결한다. 학술6가족 자체의 역방향은 storage-academic 소유이며 여기서는 실행 최상위에 실제 작성되는 값과 저장 수신을 검사한다.
3. CoreEngineMixin._apply/_apply_operational_disposition의 운영 결과·continue/retry/resume/stop과 marker 제거, scheduled_operator.recovery의 runner status/evidence_ref 및 원 파일 내용, CallEngineMixin._receive_call의 늦은 결과 보존·실제 실패/error_kind를 검사한다. 필요할 때 가장 짧은 기존 실제 producer 장면에 저장/load 단언을 더한다. 별도 ledger나 supervision 응답의 같은 이름을 실행 저장값으로 대체하지 않는다. 원결과·불명 종료·예약/owner·한 번 정산·옛head를 보존한다.
4. 공급자 사용량은 기존 raw/명시 입력을 실제 parser→runner 분류→실행 수신/저장에 연결한다. 비빈 segments/model usage/scopes/reported model 값과 opaque decimal JSON 표현을 독립적으로 비교한다. 새 실모델 호출·합성raw의 녹화 승격은 하지 않는다. _observe_running의 fact sequence는 실제 사실과 수신 순서, _prepare_call의 observation_rules는 tracker 설정과 execution binding, _call_stop_requested의 stop_reason은 첫 기록과 뒤 요청에서의 보존을 정확히 확인한다. 전체 관찰여정을 다시 만들지 않는다.
5. 기존73행의 범위 한정 근거와 새19행을 현재92필드에 연결한다. 같은 실제 생산/저장 표본을 contracts.pairs.assert_pair의 필수+선택 역방향에 연결해 미생산 optional을 추가하면 빠짐이 실패로 드러나게 한다. 기존 stored_pair/ExecutionScene과 실제 단언을 재사용하고, 필요하면 같은 소유 helper로 옮겨 한 번 생산한 표본을 사용한다. 시험 모듈 사이 import나 별도 역방향 알고리즘·거대 registry·모든 필드를 한 객체에 채운 fixture를 만들지 않는다. 열린 evidence/map은 닫힌 필드 검사와 별개로 실제 내용·참조·해시를 검사한다. 모든 역할·선택값의 조합이나 모든 쓰기분기 도달을 새 유한 표본만으로 완료라고 하지 않는다.
6. 제거10필드의 정확 반려와 현재 정본 ended_at/execution_profile_ref/launch_ticket/capacity.process, continuation 독립성·fresh worker 요청, state/10·신뢰/권한 필드 정리와 기존 실제 저장 성질을 보존한다. 새로운 제품 결함이 확인되면 쓰기 범위의 제공자·직접시험·미러와 필요한 수리를 함께 마친다. 현재92라는 수를 유지하기 위해 잘못된 계약을 방치하지 않되 중앙schema 등의 다른 소유 경계가 정말 필요하면 정확한 최소 반례와 필요한 변경을 보고한다. 가상 의존성이나 구판 alias/default/검증 예외는 추가하지 않는다.

## 실제 선행과 소유

선행은 execution-fields 하나다. 현재 실제 실행 계약·저장 대표·필드별 남김을 소비하며 storage-execution/storage-authority는 간접 선행에 포함된다. storage-academic과 storage-conversation의 종료는 필요하지 않다. 두 task의 배정·workspace·미수용 결과는 바꾸거나 소비하지 않는다. 공유 소스는 각 task가 시작할 때 고정된 사본으로 읽는다.

본 task는 core/call/dispatch/provider/runner/scheduled_operator/repair 및 명시된 실행 직접시험·helper를 소유한다. 중앙schema, governance/governance_engine/academic/knowledge, lifecycle/initialization/Repository/StateContract, 공통 contracts.pairs와 제품 이음새 설명은 읽기 전용이다. 학술 task가 중앙schema/목표·학술 제공자·공유 설명을, 대화 task가 lifecycle/저장 기반과 직접시험을 소유한다. 따라서 현재 의미 있는 writes 교집합은 없고 비용캐시만 공유한다. 인터페이스 변경이 필요하면 정확한 정의/소비/의미를 report에 남겨 manager가 공용 설명과 후속 소유를 판단할 수 있게 한다.

## 필요한 확인과 인계

정적 판단과 정확 원보고로 충분하면 실행하지 않는다. 보완한 실제 동작의 불확실성만 자기 workspace 공식 scripts/run_tests.py --jobs 1의 가장 작은 관련 선택으로 확인한다. storage-academic/storage-conversation과 합쳐 최대3개 task·각jobs1이며 추가 병렬 시험은 하지 않는다. 전체 일반/fresh T3/극단변이/T4/T5·유료 모델/HTTP/실 Lean/native Job/설치/OS예약·대형 비용 실행은 배정하지 않는다. 실제 생산/검증/저장과 외부 포트 대역을 구별한다.

필드별 최종판은 기존102행의 제거10/유효92를 유지하며 실제 producer·receiver·내용 단언·정확 ID/원보고판본·유지/수리/남김을 갱신한다. 새 문서만으로 완료하지 않는다. 전 쓰기분기 fresh T3가 소비할 심볼·SHA·관련ID를 남기되 현재 부분실행을 전분기 도달0으로 보고하지 않는다. 최초 실패/fixture 오류·교정판, selected/고유 실제 row·counts·관측exit·source SHA·changed_during_run·소프트초과를 보존하고 별도판본 통과를 합산하지 않는다.

비용캐시는 관측값을 evidence에 보존한 뒤 own base로 복원한다. 공식 build_skill_mirrors.py 생성/check와 허용writes를 확인하고 protocol 형식 report.json을 작성해 `python C:/math/services/async-development/check.py report C:/math/.async/dm execution-storage`를 통과시킨다. 공용 source/context/plan/seams/queue/state·다른task·engine·Git index/commit·graphify·기존 연구는 수정하지 않는다. 다른29미배정 가족·관찰4의 최종판·다른 원요구/K/P2·G4~G8·L01/Windows1314·최종review는 남는다.

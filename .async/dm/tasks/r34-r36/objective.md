# R34~R36: 같은 판단을 하는 평가자들의 규칙 일치성

원래 3-C의 열한 규칙 쌍과 그 현재 직접 소비에서 평가자가 같은 판정 또는 선언된 함의를 만족하는지 판단한다. 기존 충분한 성질을 재사용하고 실제 공백의 수리·관련 확인을 한 task에서 마친다. 허가/프로필, 상태/분류, 입력/경계는 같은 structure.test_rule_consistency와 기존 유한 공간 시험을 소비하므로 따로 쪼개지 않는다. r31-fix 및 structure-fixes의 완료를 기다릴 선행은 없다.

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md, 스킬 AGENTS.md·시험-지침.md·이음새-정본.md를 읽는다. 원문은 C:/math/docs/do-math/시험-재편-2026-09-29/조사/결함-범주.md 3-C와 단계-전환표-2026-10-03.json이다. C:/math/docs/do-math/continuous-development-2026-10-13/phases/001/tasks/closure-map/evidence의 requirement-state 3-C, tracking-state R34/R35/R36, prior-review-state와 evidence-catalog의 B70~B73을 읽는다. 과거 run:은 그 continuous-development 루트다. 사용자 결정·모델/문서 묶음 지시를 유지한다.

## 끝낼 유한 질문

- R34: B-16(준비성/프로필), C-19(허가/정지), B-36(제한 복구). 난이도×중요도×허용 프로필 부분집합, 실제 역할×프로필 및 역할×grant 이름 집합의 작은 유한 공간과 초기화-운전 문서의 grant 예시를 기존 producer/실제 소비에 연결한다. ready이면 선택 가능, 배정 허가이면 해당 실행의 정지 사유가 아님이라는 함의를 실제 입력 조건과 함께 확인한다. 서로 다른 의미의 과거 grant와 현재 pinned grant를 섞지 않는다.
- R35: C-15(환경 분류), C-12(종결), D-02(철회), A-47(초과 적용). 실제 판정 정본과 모든 현재 직접 평가자의 값·선언된 함의가 일치하는지 확인한다. 환경 원인 반려의 환경 대기 분류, 종결 wrapper, 철회 우선순위/권한과 초과 처분의 실제 적용을 정적 등록표만으로 대체하지 않는다.
- R36: B-49(실행 경로), B-32(필수 입력), B-33(역할 관찰), C-13(표시한도와 비교). 경로 대소문자/PATHEXT·현재 공급자의 실제 정체성 소비, prepare_role_input→fit_context 필수/선택 분류, 현행 프로필의 관찰 모드/결속, 바이트 예산 전달과 기록을 확인한다. B72의 extra:task-input-supply는 원래 B-32가 아니라 추가 규칙이다. 원래 B-32 및 P2 B-32의 governance/action 필수·goal/policies 선택(각800/예산1200) 질문을 현행 계약에 맞춰 판정하고, 명시적으로 필수인 goal의 정상 overflow를 결함 기대값으로 바꾸지 않는다.

`structure.test_rule_consistency.RULES`의 현재 13행은 원래 열한 쌍과 추가 task-input-supply/5-A 및 관찰 하위규칙을 표시한다. 현재 정의·직접 호출은 원 코드로 확인하고, 새 이름의 의미상 사본은 이 열한 판단을 실제 소비하는 경계에 한정하여 찾는다. 모든 미래 복제 부재의 증명이나 전 제품 재감사를 새 종료조건으로 만들지 않는다. 선언표/AST 일치와 행동 차분은 서로 다른 근거다.

## 기존 근거와 수리

단계-전환표 current_work의 rule_consistency_integration(B70), authority_rule_consistency_integration(B71), input_observation_rule_integration(B72), original_rule_scope_correction_integration(B73)는 실제 tracked_report와 당시 소스 SHA를 제공한다. 각각 검증/2026-10-04-판정-규칙-세쌍, 허가-정지-차분, 참조-관찰-경로-규칙, 원문-규칙-정정 아래 report.json이다. 원 diff/현재 소비/정확 단언/해당 원보고를 대조해 유지·교정·추가 필요를 판단한다. 119/100/122/141 과거 counts를 현재 성공으로 합산하지 않는다. 원보고 부재나 판본 불일치는 정확한 한계로 남긴다.

r07/r18/r02/r04/r05 및 r06의 수용 성질, r09/r31-r33의 지급 참조와 양수신, r12-r13-fix의 위임 권한, r29-r30의 단위 실패 수리는 해당 불변 경계만 재사용한다. 제품 입력/권한/기초/반려를 낮추어 차분을 맞추지 않는다. 새로운 병렬 registry나 평가자 사본을 추가하기 전에 한 정본의 실제 소비로 줄일 수 있는지 판단한다. 발견한 직접 시험/helper 공백과 지정 범위의 실제 규칙 결함은 가까운 수리·미러·최소 확인을 함께 마친다.

## 소유·최소 검증·보고

task.json writes가 정본이다. 지정 규칙 runtime(model_policy/governance/lifecycle/planning/context_store/input_recovery/observations/file_io와 직접 call/formal 소비), 기존 차분 시험·필요한 한정 새 test_rule_consumer_differences 및 helper를 소유한다. core_engine/decision_engine/task_scope/input_basis/record_schemas·제출/역할 요구표·sim/test_role_input_context.py와 structure-fixes의 시험/문서/검사기는 읽기 전용이다. 이 파일들의 실제 결함을 확인하면 입력·심볼·영향·필요 수정 파일을 보고한다. r31-fix의 local_path currentness F4는 그 task가 소유하므로 여기서 고치거나 같은 실패를 재실행하지 않는다. D-02의 task_scope는 읽기·현재 시험으로 충분한지를 먼저 판단한다.

충분한 원코드/원보고 관계는 정적으로 끝낸다. 실제로 바꾼 동작과 직접 소비만 공식 run_tests.py --jobs 1의 작은 선택으로 확인하며, 유한 공간의 의미를 줄이거나 모든 역할 init을 반복하지 않는다. 전체 일반/T3/변이/T4/T5, 대형 fixture, 외부 모델/Lean/예약 호출은 수행하지 않는다. 모델 이름의 무한 분할이나 원문에 없는 입력 전건을 만들지 않는다.

공식 mirror build/check, 변경쌍 bytes와 비용캐시 own base 복원을 마친다. 보고에 원래 11쌍별 충분한 성질·입력축·실제 소비·원보고 판본·공백/수리/남김을 연결한다. 전체PR/K/P2 완료를 추정하지 않고 직접 교차하는 B70~B73/P2만 원ID로 처분한다. 선택·row·exit·source SHA, 초기 실패/fixture 오류·소프트 초과를 구분한다. `python C:/math/services/async-development/check.py report C:/math/.async/dm r34-r36` PASS를 확인한다. 공용 문서/queue/state·다른 task·Git index·graphify는 수정하지 않는다.

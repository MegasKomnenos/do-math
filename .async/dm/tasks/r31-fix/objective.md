# 지급된 자료 경로의 현재성 수리와 역할 입력 반려 단언 마감

사용자가 추가 자료를 등록하면 그 자료를 기다리던 실제 과제 판정이 다시 열려야 한다. r31-r33이 남긴 F4를 고치고, 같은 역할 입력 파일에 남은 구조 반려 단언 9건을 함께 마친다. r31-r33만 실제 선행이다. 구조 문서/검사기 작업과 규칙 일치성 작업은 독립이며 중간 workspace를 소비하지 않는다.

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md와 스킬 AGENTS.md·시험-지침.md를 읽는다. 공용 source와 다른 task 기록은 읽기 전용이며 자기 workspace의 writes만 수정한다. manager0026의 review.md·source-review.json, r31-r33의 report.json·evidence/judgment.md·contract-reach.md·related-final/report.json이 직접 입력이다. 원래 3-A의 자료 식별 형식과 기존 정상 기대값을 유지한다.

## 맡은 결과

1. `flows.test_submission_missing_input_aliases.MissingInputAliasTests.test_supplied_local_source_path_reopens_the_actual_plan`의 실제 실패를 해결한다. 공개 source 등록 → 실제 research_work 결과 → 지급 sources[].local_path를 missing_inputs로 쓴 계획의 중앙 수락까지는 성공한다. 같은 source 다음 판본 도착 뒤에도 current=true이고 basis의 해당 참조는 None이다. `core_engine._context`/`submission.reference_aliases`는 지급 local_path를 합법적 인용으로 제공하지만 `decision_engine._apply_task_plan` → `task_scope.apply_task_assessments/assessment_basis`는 local_path 없는 instance.sources를 조회한다. 이 경계가 사용한 고정 입력과 실제 source 정체성을 연결한다.
2. 원 제출 bytes/해시/receipt는 그대로 보존한다. 기존 이름, source:이름, ID, 게시 경로의 네 형식과 지급 local_path 모두 자료의 실제 도착/판본 변경을 따라야 한다. 무관 source는 current를 바꾸지 않고 결과 목록은 보존하며, 해당 source 변경 뒤 returned_task_ids가 다시 열려 정상 재계획을 진행해야 한다. 저장/restart에서도 같은 의미를 유지한다. locator 문자열을 임의 basename 추측이나 현재 순서만으로 다른 source에 결박하지 않는다. 원 지급 입력에서 얻을 수 있는 정체성을 사용하며, 새 자료가 아직 없는 정상 missing_inputs와 허위 참조·현재성 검사를 구별한다. 이미 존재하는 봉인 입력·기초 표현으로 충분한지 먼저 확인하고 새 저장 구조는 실제로 필요할 때만 쓴다.
3. `managers/0025/structure-scope.json.reserved_rows` 및 `managers/0026/source-review.json.remaining_role_input_smells`의 sim/test_role_input_context.py 9건을 판정·수리한다. r31-r33은 이 파일을 바꾸지 않아 9건이 남았다. 세 시험 메서드의 실제 파일/manifest/역할 입력 반려 원인을 읽고 정확한 사유를 단언한다. 예외형만 맞거나 무의미한 regex/예외 객체 접근만으로 검사를 피하지 않는다. 정상 대조와 원 입력축은 유지한다. 현재 checker가 오판한 경우에는 정확 근거를 보고하되 실행 중 structure-fixes의 smell_rules를 수정하지 않는다.

## 범위와 확인

task.json writes의 core_engine/decision_engine/task_scope/input_basis 및 필요한 assessment schema, 직접 시험/helper·미러를 소유한다. core_engine 변경은 지급 source 연결과 assessment 소비에 필요한 부분으로 한정하며 수용된 r29-r30의 제어/정비/native 수리를 보존한다. runtime의 다른 모듈과 r34-r36의 규칙/차분 시험, structure-fixes의 16시험·문서·검사기는 읽기 전용이다. 오래된 저장판의 호환층이나 데이터 마이그레이션을 만들지 않는다. 새 저장 필수 구조로 계약 설명이 바뀌어야 하는 경우 실제 변경과 필요한 문서 경계를 보고하며 현재 state/10을 근거 없이 올리지 않는다.

기존 실패 회귀와 정상 네 형식을 먼저 사용하고 새 저장/restart 또는 잘못된 결박 위험을 확인하는 가장 작은 입력만 보완한다. 29개 전체·10역할 전체·대형 입력을 이유 없이 반복하지 않는다. 반려 단언은 바뀐 세 메서드와 실제 관련 helper만 공식 run_tests.py --jobs 1로 확인한다. 정적 판정으로 충분한 항목은 실행하지 않는다. 전체 일반/T3/변이/T4/T5, 외부 모델/Lean/예약 실호출은 하지 않는다.

공식 mirror build/check와 변경쌍 bytes를 확인한다. 비용캐시는 원증거 보존 후 own base로 복원한다. report에는 F4와 9건 각각의 처분, 원값/현재성/재시작 근거, 실제 선택·고유 row·exit·소스 SHA, 실패/fixture 교정/소프트 초과를 기록한다. `python C:/math/services/async-development/check.py report C:/math/.async/dm r31-fix`를 통과한다. 공용 문서/queue/state·다른 task·Git index·graphify를 수정하지 않는다. 최종 통합판 관문·다른 K/P2·L01/Windows1314는 이번 완료와 구별한다.

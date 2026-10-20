# 구조 검사 잔여 반려 단언과 저장 계약 설명 정리

사용자가 원하는 결과는 잘못된 사유의 예외가 시험을 통과하지 않으며, 실제 제품 계약과 사용 설명이 일치하는 것이다. 기존 구조 실패를 새 검사 체계로 대체하지 않고 현재 실패 원인을 해결한다. r22-snapshots 수용판에서 시작하며 다른 실행 중 task의 결과는 필요하지 않다.

SESSION_JSON의 workspace, task.json, inputs/context.md·plan.md·seams.md를 먼저 읽는다. 공용 source와 다른 task의 기록은 읽기 전용이며 제품 변경은 자기 workspace의 writes에만 한다. 사용자 원문은 C:/math/docs/do-math/continuous-development-2026-10-13/sources/user-decisions.md·document-batching-2026-10-14.md·model-policy-2026-10-14.md다. 스킬 AGENTS.md와 scripts/tests/시험-지침.md, 설계.md 6.2를 적용한다.

## 맡은 두 결과

1. managers/0025/structure-scope.json의 assigned_rows 35건을 판정하고 필요한 반려 단언을 고친다. r14의 역사 44건에 해당하는 17파일을 현행 smell_rules로 정적 확인했으며 여전히 44건이다. 이 중 sim/test_role_input_context.py의 9건은 실행 중 r31-r33의 기존 소유이므로 쓰지 않는다. 본 작업의 직접 파일은 나머지 16개다. 각 finding의 test와 실제 생산·반려 경로를 읽고 잘못된 원인으로도 성공할 수 있는 단언을 정확 원인에 연결한다. 현재 근거로 이미 올바른 시험을 검사기가 오판한다면 그 사실을 입증해 검사기의 해당 해석만 교정할 수 있다.
2. r22-snapshots가 STATE_CONTRACT_ID를 do-math-state/10으로 바꿨지만 README.md 15행, references/CLI-실행-계약.md 5·58행에는 /9가 남았다. managers/0025/source-review.json의 F3와 payloads/state_contract 및 scripts/이음새-정본.md 7절을 읽어 현행 저장 계약 설명을 맞춘다. 역할 응답 do-math-cli/5와 저장 계약을 혼동하지 않는다. 같은 문서의 바로 관련 저장 표현 설명이 실제 snapshot codec과 충돌하면 같이 고친다. 기존 문서 P01~P11을 재감사하거나 옛 계약 호환층을 만들지 않는다.

## 반려 의미와 최소 확인

형식 오류, 권한·현재성 오류, 봉인 불일치, 외부 환경 실패를 실제 수신 경계와 원 입력에 대조한다. 예외 종류만 보거나 임의 문자열로 통과시키지 않는다. 같은 fixture를 정상 대조로 쓰며 반려를 만드는 입력과 distinct message/issue/coordinate의 관계를 확인한다. 반려 단언을 통과시키려고 runtime의 동작·검사·기존 입력축·기대값을 낮추지 않는다. 문서 반례가 helper의 AssertionError를 받는 시험이면 어느 문서/정의/불일치를 잡았는지 확인한다. 예외를 읽지 않고 ctx.exception만 접근하거나 .* 같은 무의미한 regex로 검사를 속이지 않는다.

구조44건 전체를 이번 완료 건수로 세지 않는다. assigned_rows별로 수리/기존 충분/검사기 오판 판정과 근거를 기록하고 reserved_rows 9건은 남김으로 구별한다. 본 작업이 실제 수정한 파일에서 가까운 동일 문제를 발견하면 함께 처리하되 전 제품 의미 감사나 모든 helper 재설계로 확대하지 않는다. support/smell_rules.py를 변경한다면 원래 반려 원인 확인의 목적을 유지하며 해당 false positive/false negative를 가르는 최소 회귀를 unit.test_smell_rules에 둔다. 면제 목록·test 이름 whitelist·검사 삭제는 수리로 인정하지 않는다.

실행보다 원 코드·원보고 대조로 충분한 것은 정적으로 끝낸다. 새 반려 단언이 실제 결과를 확인해야 할 때는 공식 run_tests.py --jobs 1의 해당 ID만 쓴다. 변경한 checker/문서 계약의 직접 소비만 필요한 만큼 포함한다. 전체 일반/T3/변이/T4/T5는 실행하지 않는다. structure.test_test_smells의 전체 결과가 읽기 전용 9건 때문에 실패하면 정확 scope를 보고하고 다른 task 파일을 고치거나 검사에서 제외하지 않는다. 파일별 정적 결과와 전체 결과를 구별한다. 실제 Lean 호출·예약·모델 호출은 새로 수행하지 않으며 boundary 파일은 필요한 경우 정적 원인 대조와 보존 원보고로 판단한다. 기존 환경 skip을 통과로 바꾸지 않는다.

## 쓰기와 제출

task.json writes가 정본이다. 지정 시험16개, 필요한 smell/doc 정본 helper와 직접 구조·단위 회귀, README/CLI 참조 및 미러를 소유한다. runtime 전체, engine_context와 role_input_requirements/제출 helper, r29-r30의 owner/CLI 시험, r31-r33의 역할 입력·광고/수신 파일은 읽기 전용이다. 실제 제품 결함이 드러나면 입력·정확 경계·사용 영향·필요한 수정 경로를 보고하고 가능한 수리를 마친다. 진행 중 사본은 읽지 않는다.

공식 mirror build/check를 마치고 변경쌍의 정확한 bytes를 확인한다. 비용캐시는 증거 보존 후 own base로 복원한다. report에는 두 결과의 상태, 35건의 현재 처분·9건의 별도 소유, 실제 선택/row·exit·판본 SHA, 초기 실패와 fixture 오류·소프트초과·미실행을 구별한다. check.py report C:/math/.async/dm structure-fixes PASS를 확인한다. 공용 context/plan/seams/queue/state, Git index, 과거 원자료를 수정하지 않는다. G4~G8·다른 의미 질문·L01·Windows1314의 완료를 주장하지 않는다.

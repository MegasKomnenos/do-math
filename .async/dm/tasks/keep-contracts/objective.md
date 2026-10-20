# 시험 계약의 정본 소비와 의미 있는 실패 보존

KEEP-TEST-CONTRACT의 K-51/64/65/69/71/74 여섯 질문을 현재 정의와 직접 소비 시험에 연결한다. 시험이 제품의 정본을 사용하고, 실제 성질을 확인하며, 잘못된 입력의 정확한 실패를 드러내는 상태가 목표다. 충분한 기존 결과는 재사용하고 확인된 공백의 수정·관련 최소 확인·미러를 한 task에서 마친다. 전 제품 시험을 다시 감사하거나 문체만 바꾸는 작업이 아니다.

SESSION_JSON/task.json과 inputs/context.md·plan.md·seams.md, do-math AGENTS.md와 시험-지침.md를 읽는다. 원자료 루트는 C:/math/docs/do-math/continuous-development-2026-10-13이다. sources/user-decisions.md·model-policy-2026-10-14.md·document-batching-2026-10-14.md·requirements-index.json 및 phases/001/tasks/closure-map/evidence/tracking-state.json의 KEEP-TEST-CONTRACT, requirement-state.json의 해당 여섯 K가 원문 연결이다. C:/math/docs/do-math/시험-재편-2026-09-29/조사/대역-사각지대.md와 단계-전환표-2026-10-03.json의 같은 ID를 확인한다. tests/migration/dispositions/kernel.knowledge.json의 where는 탐색 출발점이며 실제 현재 정의·단언으로 판단한다.

keep-inputs의 수용된 role_answers·직접 입력 시험, structure-finish의 필드별 반려 단언과 문서 소비, keep-isolation의 현재 시험 지침을 보존한다. 이 세 결과만 선행이다. 다른 실행 중 task의 사본을 소비하지 않는다. keep-storage와 keep-evidence가 같은 시점의 별도 사본에서 작업하며 그 배정·파일은 읽기 전용이다.

## 판정할 질문

1. **K-51: 제품 정본을 사용하는 fixture.** support.role_answers.review_items가 CONTRACT_REVIEW_ITEMS를, support.observation_inputs.observation_rule이 OPERATORS의 source/unit을, 실제 scheduling/model profile helper와 test_scheduling_parallel_engine이 현행 model_policy/execution_profiles의 목록·상수를 사용하는지 확인한다. 폐기 PROFILE_CONFIG 이름을 복원하지 않는다. 제품이 정의한 모집단과 시험이 독립적으로 정해야 하는 기대값을 구별한다. r07-fix의 소유권·r34-r36의 profile/grant 판정을 재사용하고, 기대값을 같은 피검사 함수로 다시 계산하는 순환 단언이나 이 작업에서 발견한 stale 복제만 직접 수리한다.
2. **K-64: 한 시험이 설명하는 성질.** support.smell_rules._test_issues와 structure.test_test_smells가 기계적으로 보장하는 범위와 사람의 의미 판단을 구별한다. no_assertion이 없다는 사실만으로 이름/한 성질 규칙을 증명하지 않는다. 위 정본 소비·음성 사유·시간·공유 계약의 직접 시험을 유한 모집단으로 삼아 이름과 실제 단언의 관계를 설명한다. 한 성질의 여러 입력축이나 실제 공개 여정의 관련 단언을 무조건 쪼개지 않는다. 실행 방법·개수·이름만 바꾸는 전수 재편이나 새 명명 검사기는 만들지 않는다.
3. **K-65: 조건 대기와 주입 시계.** 현재 smell_rules의 fixed_sleep 검사와 직접 반례, FakeClock.advance·engine_purpose.drive·run_tests.wait_for_worker 및 그 직접 소비를 대조한다. keep-templates의 현재 상태 선확인, keep-isolation의 실제 Job 정산, r47-r48/r49-startup의 시각 소비 근거를 재사용한다. 가상 시각/유한 owner-turn, 실제 조건 대기, 제품의 임대·기한과 폐기된 시험 wall timeout을 구별한다. 최신 사용자 정책상 공식 worker를 시간만으로 실패시키는 상한을 복원하지 않는다. 검사기의 일반적인 동적 Python 우회 완전성을 새 의무로 만들지 않고 현재 코드에서 실제 놓치는 입력만 판단한다.
4. **K-69: 공통 계약의 소유.** support/port_contracts/{jobs,calls,clock,host,http,scheduler,git_backend}.py와 실제 contracts/boundary 양측이 같은 정의를 소비하는지 확인한다. structure.test_ports의 importlib/inspect는 시험 모집단을 검사하는 코드다. 이것을 시험 실행 helper를 다른 test 모듈에서 가져오는 의존과 같은 것으로 취급하지 말고 목적·실제 정의 소유를 확인한다. 관련 모듈의 import/상속을 정적으로 읽고 기존 구조 검사·과거 이동 근거를 재사용한다. 현행 helper 중복·잘못된 소유가 있으면 수정하고, 근거 없이 모든 test 모듈의 동적 조회를 금지하는 규칙을 추가하지 않는다.
5. **K-71: 반려의 정확한 원인.** smell_rules의 unpinned_rejection이 실제로 검사하는 수준과 정확 reason/code/path를 단언하는 소비자의 수준을 구별한다. structure-finish의 A07 필드별 진단·원 bytes/codec/위치, r31-fix의 지급 자료 반려, keep-inputs의 경로/해시/길이·정확 receipt/의미 근거 반려를 재사용한다. keep-storage 소유 저장 시험은 읽기만 한다. 넓은 예외나 관계없는 필드 실패가 성공으로 통과하는 실제 공백을 발견하면 해당 직접 시험/helper를 함께 고친다. AST가 의미를 완전히 증명한다고 주장하거나 통과를 위해 검사기를 느슨하게 하지 않는다.
6. **K-74: 계약 변경을 소비한 대역.** ModelDouble의 호출별 Answer/실제 봉인·중앙 receipt, LeanDouble의 명시 입력 등록, 공통 port contract의 생산/소비 경계를 현재 코드와 이미 수용한 변경 근거에 연결한다. keep-inputs·keep-templates·keep-isolation 및 관련 r task의 전후 차이에서 어떤 계약이 바뀌고 어떤 대역/단언이 그것을 소비했는지 확인한다. 아직 실행 중인 keep-evidence/keep-storage의 결과를 추측하지 않는다. 이 질문의 현행 의미와 그 두 task가 소유한 구체적인 미결을 나누어 보고하며, 같은 합성 증거/저장 조사를 중복 수행하지 않는다.

각 K에 원문 성질, 현재 정의/정확 시험 메서드, 실제 확인과 원보고 판본, 충족한 범위와 구체적인 남김을 연결한다. 기존 전체 실패 보고 속 지정 passed와 현재 실행을 구별하고 Temp 원보고 부재를 성공으로 보충하지 않는다. 전체 G2/G3·다른 K/P2의 완료율을 추정하지 않는다.

## 수정 범위와 최소 확인

task.json의 smell 검사/helper·직접 시험, 정본 fixture/직접 소비, port 구조 조회와 시험 지침·미러가 수정 범위다. 필요한 새 소규모 fixture 계약 시험은 unit/test_fixture_contracts.py에 둘 수 있다. runtime, run_tests/test_categories, support/sim.py, fake clock/host/jobs, Lean/trust 합성 증거, 저장 repository/contract/helper·계약 pair는 읽기 전용이다. 공통 port 계약 정의와 양측 시험도 이번에는 읽기 전용이다. 실제 수정이 그 범위를 넘어야 하면 정확 원인·입력·심볼과 영향을 보고한다. 새 규칙/추상화/호환 wrapper를 기본 해법으로 선택하지 않는다.

충분한 성질은 정적 대조로 끝낸다. 변경으로 남은 불확실성만 workspace의 공식 run_tests.py --jobs 1에서 가장 작은 관련 선택으로 확인한다. 검증 중 소스를 고정하고 selected/실제 고유 row·exit·판본 SHA·fixture/초기 실패·실행 중 변경·소프트 초과와 이유를 보존한다. 실제 제품 코드·외부 대역·AST 검사 각각의 증명 범위를 구분한다. 전체 일반/T3/변이/T4/T5·실 공급자/Lean/HTTP/OS예약 호출을 실행하지 않는다. 비용캐시는 관측 bytes를 evidence에 보존한 뒤 own base로 복원하고 공식 mirror build/check를 한다. 무변경이라면 불필요한 실행·미러 생성을 하지 않는다.

report.json에는 여섯 유한 질문의 판정·수리·재사용·미결 및 공용 설명 인계를 적는다. 최종 통합판 증거, KEEP-REGRESSION-PROOF의 별도 네 질문, G4~G8·L01 Q1/Q2/UTF-8 byte·Windows1314는 별도로 남는다. check.py report C:/math/.async/dm keep-contracts PASS로 제출한다. 공용소스/공용문서·queue/state·다른 task·engine/Git index·graphify·기존 연구 운전은 수정하지 않는다.

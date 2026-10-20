# 시험 선택과 실행 결과가 원래 보호 성질을 보존하게 한다

사용자가 공식 실행기의 선택과 보고를 근거로 시험 완료 여부를 판단할 수 있어야 한다. KEEP-RUNNER-DISCOVERY와 KEEP-RUNNER-REPORT의 같은 run_tests.py owner를 한 작업으로 묶어, 충분한 기존 성질은 재사용하고 실제 공백이 있으면 구현·직접 시험·해당 설명·미러를 이 task에서 마친다. 최종 전체 시험을 실행하는 task는 아니다.

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md와 do-math AGENTS.md·시험-지침.md를 읽는다. 원자료 루트 C:/math/docs/do-math/continuous-development-2026-10-13의 sources/user-decisions.md·requirements-index.json, phases/001/tasks/closure-map/evidence/tracking-state.json의 KEEP-RUNNER-DISCOVERY/REPORT, requirement-state.json의 K-01~K-09·K-12·K-54·K-62·K-68, prior-review-state.json의 PR01 중 이 질문에 직접 연결된 slice를 읽는다. C:/math/docs/do-math/시험-재편-2026-09-29/조사/대역-사각지대.md의 해당 K 원문과 단계-전환표의 preservation 항목, 현행 tests/migration/dispositions/runner.json·kernel.knowledge.json을 대조한다. 이행 표의 actual_test_ids나 과거 passed 숫자는 현재 단언·원보고를 대신하지 않는다. 원보고 부재와 판본 차이는 그대로 남긴다.

## 유한한 질문과 완료 판단

1. K-01/02/03/04/05/68: 현재 run_tests.FOLDERS/TIERS, test_modules/discover/main이 실제 디스크 모집단·필수 패키지·폴더 밖 파일·수집 누락/유령·중복 ID·import 오류·한 개라도 모르는 위치 ID·빈 선택을 어떻게 처리하는지 현행 계약과 직접 단언에 연결한다. 유효한 폴더/모듈/클래스/메서드와 tier/match 선택도 보존한다. 원문 SHARDS는 폐기된 수동 등록 수단이다. 이를 되살리지 않으며 K-02의 알려진 구멍을 보존할 정상 기대값으로 삼지 않는다. 실제 디스크/loader 생산과 합성 ID 입력이 각각 무엇을 입증하는지 구별한다. 모듈 이름 규칙을 이유로 전체 제품 시험을 다시 명명하지 않는다.
2. K-06/07/08/12: 새거나 빈 output, 재사용 없는 일반 결과, class/module 준비 실패/skip의 fixture 행과 selected별 not_run, subTest 실패/skip의 부모 결과, 다음 시험이 시작되기 전 complete=False 실패 파일 게시와 최종 selected/실제 row/complete/successful/exit를 연결한다. 실패가 있는 표본은 의도한 반례이며 공식 부모 시험의 실패와 구별한다. 기존 TimedResult/_run_suite/_worker/main의 실제 소비를 검사한다. 시간 경과로 자동 종료하는 정책이나 결과 캐시를 추가하지 않는다. T3 측정 재사용은 일반 시험 결과 캐시와 다르며 이 task가 fresh T3를 실행할 이유가 아니다.
3. K-09/54/62: _edition의 실제 scripts Python bytes와 실행 전후 변경 검출, docs/pycache 제외, changed_during_run과 successful 반려, 미완결 결과를 성공으로 세지 않는 소비를 연결한다. 현재 official run_tests.py가 유일한 완료 근거라는 지침을 유지한다. 실행 중 자기 workspace를 편집하지 않는다. 변경 검출 시험은 기존 격리 fixture/주입 경계에서 구성하고 실제 실행 중인 source를 변경하여 증거를 무효화하지 않는다. 현행 비용 캐시와 T3 측정 store, 결과 재사용을 서로 혼동하지 않는다.

각 ID를 현행 정의·정확 시험 메서드·실제 단언·재사용하는 원보고/판본·충족 또는 구체적 남김에 연결한다. 충분하면 정적 확인으로 종료한다. 확인된 공백은 동일 task에서 기존 직접 시험에 단언을 더하고 필요한 실행기 수리를 한다. 단순 목록/AST 일치만으로 동작을 입증하지 않으며, 검사 대상인 discover/result 집계를 대역으로 지운 채 원하는 결론을 반환하지 않는다. 실행기 자체의 오류 입력을 주입하는 경계와 검사 대상의 대체를 구별한다. 새로운 일반 감사 체계나 registry를 만들지 않는다.

## 범위와 검증

쓰기 범위는 run_tests.py, unit/test_runner_regressions.py·test_runner_tiers.py, 필요한 공통 support/runner_contracts.py, tests/시험-지침.md 및 미러·비용 캐시다. isolation OS/Windows Job, branch_gate/selection/mutation/t3_store의 별도 전체 보존 질문과 최종 T3/변이·T4/T5는 읽기만 하며 확인된 범위 밖 결함은 정확 파일·입력·영향으로 인계한다. runtime core/lifecycle/knowledge/operator와 공유 이음새·README는 다른 task의 범위다. r44-fix나 r49-startup의 미완성 결과를 소비하지 않는다. 새 선행이 필요하지 않은 독립 파일 묶음이다.

기존 단언과 실제 원보고를 먼저 읽는다. 새 변경에 실행이 필요할 때만 공식 scripts/run_tests.py --jobs 1의 가장 작은 관련 선택으로 확인한다. 이미 충분한 같은 판본의 검증을 반복하지 않는다. 전체 일반/T3/변이/T4/T5, 외부 모델/Lean/OS 예약은 실행하지 않는다. 초기 실패·준비 오류·정확 selected/row·exit·source SHA·실행중 변경·소프트 초과와 한계를 남긴다. 별도 실행/판본을 단일 전체 통과로 합산하지 않는다. 정본/미러를 공식 생성·check하고 timing cache 관측 bytes를 evidence에 보존한 뒤 own base로 복원한다.

report.json에는 이 13개 K ID의 현재 처분, 유지·수리한 성질과 정확 남김을 적고 check.py report C:/math/.async/dm keep-runner PASS로 제출한다. 전체 G2/G3·PR01·G4~G8의 완료로 확대하지 않는다. 공용 source/문서/queue/state, 다른 task, engine, Git index, graphify와 기존 연구 운전은 수정하지 않는다.

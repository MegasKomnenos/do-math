# 회귀 증거의 보호 성질을 현재 실행기와 실제 보존 기록에서 판정한다

KEEP-REGRESSION-PROOF의 K-70/73/76/77은 재현·수리 무력화·증거 종류·고정 판본과 최초 실패 보존에 관한 사용자 요구다. 현재 실행기가 제공하는 보장과 실제 작업 기록이 입증하는 범위를 구별하여 이 네 ID의 남은 판단을 끝낸다. 이 task는 제품 수정과 새 시험 실행이 없는 한정 읽기 작업이다. 다른 세 작업이 공식 최소 시험을 진행하므로 독립된 원보고·소스 검토를 병행한다.

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md 및 do-math AGENTS.md를 읽는다. C:/math/docs/do-math/continuous-development-2026-10-13/sources의 user-decisions.md·model-policy-2026-10-14.md·document-batching-2026-10-14.md·requirements-index.json과 phases/001/tasks/closure-map/evidence/tracking-state.json의 KEEP-REGRESSION-PROOF, 단계-전환표-2026-10-03.json·대역-사각지대.md의 네 ID를 확인한다. 옛 기억/원문은 역사 위치이고 현재 실행 계약은 services/async-development/protocol.md·principles.md 및 현재 시험-지침.md다. 거대한 전문·원로그를 전수 출력하지 않는다.

## 확인할 네 질문

1. K-70: 현행 시험 지침의 재현/수리 절차와 수용된 keep-inputs의 source 반려·goal_audit 수리 전 red 및 수정 후 실제 row, legacy phase002 mutation-baseline의 red2/정상 대조·수리를 대조한다. 실패가 제품/검사 공백 때문인지 fixture/import 오류 때문인지 정확 입력·실패 단언·소스 판본에서 구별한다. 재현이 먼저 있었음을 기록이 확인하는 범위와 사후 추정만 가능한 범위를 나눈다.
2. K-73: tests/support/mutation.py의 validate_result/run/passed와 CLI/T3 소비, tests/unit/test_mutation.py 및 boundary/test_mutation_baseline.py의 해당 단언을 읽는다. legacy phase002 mutation-baseline의 실제 보존 probe/child/spec/result/정상 기준이 어느 수정의 무력화를 증명하는지 확인한다. 일반 극단 변이·수리 전 실패·특정 수리 무력화는 같은 근거가 아니다. 이미 수행된 유효 probe를 재사용하고, 없는 probe는 수행된 것처럼 쓰지 않는다. 현행 의미에 필요한 구체적 무력화 확인이 없다면 해당 함수/수리/시험 ID와 가장 작은 후속 입력을 남긴다. 모든 역사 수리를 새로 재실행하는 계획으로 확대하지 않는다.
3. K-76: 위 근거와 keep-isolation의 실제 폐기용 Python/Windows Job, keep-storage의 실제 Repository/StateContract 위 Git·Calls 일정 대역, keep-inputs의 모델 대역/설치 schema 파일 읽기를 비교한다. 원보고가 실제 외부 공급자·프로세스/파일·대역 상태·정적 독해를 구별하고 결과를 범위 밖으로 확대하지 않는지 판정한다. 원자료가 없거나 판본이 다르면 그 사실을 유지한다.
4. K-77: run_tests.main/_isolated의 source SHA/changed_during_run·출력 디렉터리 재사용 거부·selected/rows/counts/fixture_counts/complete/successful/exit 소비를 실제 정의와 keep-runner·keep-isolation의 정확 row에서 확인한다. keep-storage final-1의14pass/1fixture기대실패와 corrected-2의1pass 및 변경1파일/891SHA, keep-isolation의36pass/1실패와 교정1pass가 별도 판본으로 보존되는지도 확인한다. fixture 오류 수정 후 성공과 원 실패 삭제를 구별한다. 실행기 기능만으로 모든 기록 작성자의 준수를 자동 인증한다고 주장하지 않는다.

## 입력과 결과 경계

C:/math/.async/dm/tasks/{keep-runner,keep-isolation,keep-inputs,keep-storage}/report.json과 그 evidence의 정확 원보고·관련 정의만 읽는다. manager 검수는 managers/0036·0039·0041·0042의 review/source-review/verification-review를 안내로 쓰되 핵심 판단은 실제 원보고/현재 코드로 확인한다. legacy 입력은 C:/math/docs/do-math/continuous-development-2026-10-13/phases/002/tasks/mutation-baseline/report.json·evidence 및 phases/002/manager-evidence/verification.json이다. 현재 없는 Temp 경로는 부재로 남긴다. 원상태와 현행 정의의 차이를 확인할 때 과거 Git 조회는 git -C C:/math 읽기 전용으로 한정한다.

task writes=[]다. 제품/공용 문서/다른 task·원보고·queue/state·서비스·Git index·graphify를 수정하지 않는다. 새 공식 시험/변이/외부 호출을 실행하지 않으므로 동시 시험 슬롯을 쓰지 않는다. 진행 중 keep-evidence/keep-contracts/storage-knowledge의 미수용 결과를 소비하지 않는다. 이미 충분한 질문은 원자료 대조로 종료하고, 새 runtime/시험 결함을 실제로 발견했다면 입력·관측·파일/심볼과 관련 최소 수리를 report에 남긴다. 읽기만으로 확인할 수 없는 사항을 일반적인 추가 감사 권고로 늘리지 않는다.

task/evidence에 네 ID별 현재 제공·소비 심볼, 실제 원보고/row와 판본, 충족한 성질과 한계, 구체적 남김을 한정해 작성한다. G1~G3/다른 K·PR01 전체나 최종 G4~G8·전체 변이 성공으로 확대하지 않는다. report.json은 status·summary·changes=[]·verification·findings를 갖추고 check.py report C:/math/.async/dm keep-proof PASS로 제출한다. manager가 무변경 integrate 후 수용 여부를 결정한다.

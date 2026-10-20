# 목적과 완료할 결과

원문8-A와 R14의 진행성 질문을 현재 실제 owner 경로와 정확 단언에 연결하고, 빠진 입력/검사가 확인되면 같은 task에서 수리한다. 세 성질은 한 바퀴 관찰 적용량의 진입 적재분 한정, 관찰량과 독립적인 완료 회수 상한, 대기 제어의 한 owner 바퀴 내 처리다. 기존 모델/관찰/수송 검사를 재사용하며 requirement-state가 명시한 경쟁 관찰 부하 속 기계 완료 회수 공백도 함께 판단한다. 반환 뒤 정산 성공만으로 진행성을 입증하지 않는다.

## 입력과 현재 위치

SESSION_JSON의 workspace 및 고정 inputs/context.md·plan.md·seams.md와 task.json을 읽는다. C:/math/docs/do-math/continuous-development-2026-10-13/sources의 user-decisions.md·requirements-index.json·모델/묶음 지시와 phases/001/tasks/closure-map/evidence의 requirement-state.json 8-A, tracking-state.json R14/R15, prior-review-state.json PR11의 해당 B50/B34 slice, evidence-catalog.json의 scheduling_population_integration/return_settlement_integration이 원자료다. 과거 run:은 그 continuous-development 루트, repo:docs/...는 C:/math의 읽기 전용 자료다. 큰 JSON은 필요한 key만 읽는다. 원보고 부재를 과거 counts로 대신하지 않는다.

managers/0008/review.md·source-review.json과 tasks/r11/report.json·evidence/review.md는 수용된 종료 검사의 근거다. R11/2-C는 해결·최종 판본 대기이며 재검토할 새 반례가 없으면 되풀이하지 않는다. r03(신뢰/관찰 record)·r05(외부 값 경계)는 독립 진행 중이다. 중간 파일을 소비하거나 그 배정을 바꾸지 않는다.

## 종료할 질문

1. ModelCalls._apply_observations/pump/collect/wait와 scheduler._run_parallel의 controls·collect·wait 순서에서 실제 원천 전건을 확인한다. 기존 WAIT_SOURCES 이름표를 실행 증거로 쓰지 않는다. 함수 진입 제한과 owner 바퀴 전체 제한을 구별하고 실제 입력 생산/소비와 세 진행성 성질을 연결한다.
2. 기존 test_scheduling_close_progress의 느린 관찰(1/64/1024), 고정 시계의 끝없는 native stream·OBSERVATION_MODES, 두 완료 순서 시험이 어떤 입력과 상한을 입증하는지 판단한다. Future 완료→실제 결과 수신, queued control→processed receipt의 실제 사건 순서를 확인한다. 한 사건 처리 비용·배치 크기를 바꿔 상한을 느슨하게 만드는 방식으로 공백을 덮지 않는다. 기존 정확 단언과 충분한 원근거는 유지한다.
3. 형식·신뢰·외부 작업 등 현행 기계 호출은 어떤 같은 완료/관찰 경계를 공유하고 어디가 다른지 현재 호출자로 확인한다. 기존 machine pause·return matrix·external 시험은 실제 증명하는 성질만 재사용한다. 경쟁 관찰 부하 속 기계 완료 회수가 빠졌으면 기존 검증된 Sim·scheduling_machine/return_matrix·외부 포트 fixture로 최소 사건열과 정확 단언을 추가한다. 공유 경계 대표 하나로 충분한 경우 실제 공통 경로를 근거로 설명하고, 서로 다른 소비를 무근거로 합치지 않는다. R15/R16의 모든 종료 시점×역할 조합 정산 재감사로 확대하지 않는다.
4. 실제 engine/ModelCalls/runner/worker/collector/저장 검사를 유지한다. ObservedCalls·OwnerProbe는 실제 호출을 관찰하며 제품 메서드를 가짜로 치환하지 않는다. 외부 CLI/Lean/HTTP·시계·Calls 포트는 기존 계약 fixture를 사용한다. 가상 시계/차례 상한은 성질 또는 유한 실패를 탐지하기 위한 것이며 벽시계 timeout·시간 경과만으로 성공을 세지 않는다. 준비 실패는 runtime 반례와 구별한다.
5. 빠진 시험·가까운 helper 수리·미러·관련 최소 확인을 한 task에서 끝낸다. 실제 재현한 진행성 결함이면 배정된 parallel.py/scheduler.py 안에서 현행 계약을 유지하며 고친다. 불필요한 새 framework·등록부·실행 정책은 만들지 않는다. 범위 밖 수정이 필요하면 정확 입력·영향·필요한 파일을 보고하고 범위 안 결과를 완료한다. PR11의 해당 진행성/회수 slice와 직접 관련 K/P2 성질만 판단하고 다른 미결은 남긴다.

## 수정 범위

task.json의 writes가 권한 정본이다. 주 대상은 tests/flows/test_scheduling_close_progress.py이며 직접 관련 test_scheduling_close_settlement.py와 support/scheduling_return_observer.py·scheduling_machine.py·scheduling_parallel.py, 필요시 support/scheduling_progress.py를 함께 소유한다. 새 helper는 두 실제 소비자가 필요한 경우에만 만든다. runtime do_math/parallel.py·scheduler.py는 관측된 해당 결함 수리에 한해 수정한다. 각 정본의 .agents 미러도 같은 task가 생성한다. 다른 runtime·return matrix/external 시험·r11 종료 시험·r03/r05 경로는 읽기 전용이다. 공유 helper를 바꾸면 현재 직접 소비자의 관련 성질 보존을 정적으로 점검하고 남은 불확실성에 필요한 최소 검사만 추가한다.

## 최소 확인과 제출

먼저 현재 코드/원보고로 판단하고 충분하면 실행하지 않는다. 새 입력/단언이나 수리한 동작에만 자기 workspace의 공식 scripts/run_tests.py, jobs1로 가장 작은 관련 ID를 실행한다. 실패는 먼저 읽고 수정한 뒤 실패 ID만 확인한다. 시간 예산은 소프트하며 단언·실제 경로를 약화하지 않는다. 새 실제 모델/Job/Lean/설치/예약 호출과 전체 일반/T3/변이/T4/T5는 이 배정이 아니다.

실행 중 소스를 고정하고 선택·실제 row·exit·해시·최초 실패·한계를 evidence에 보존한다. 서로 다른 판본을 한 판본 전체 성공으로 합산하지 않는다. 공식 build_skill_mirrors.py --target .agents로 미러를 만들고 --check --target .agents 및 대응 바이트를 확인한다. 비용 캐시 두 개는 evidence 보존 후 자기 base로 복원한다. 같은 미러 시험을 불필요하게 반복하지 않는다.

evidence에는 원천/실제 생산·수신/세 성질/정확 시험·단언/판본·원보고/현재 판정·남김의 연결과 수리 이유를 남긴다. async report.json에는 실제 변경 전부와 직접 확인 범위·한계를 적고 python C:/math/services/async-development/check.py report C:/math/.async/dm r14의 PASS를 확인한다. 공용소스·engine 서비스·공용 문서/queue/state·다른 task·원자료·Git index를 수정하지 않고 graphify를 갱신하지 않는다. G4~G8·L01·Windows1314 symlink 미검사·다른 의미 미결은 유지한다.

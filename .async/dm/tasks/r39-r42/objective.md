# R39·R42: 수명·질문·반복 보류의 해소와 반복 계수

사용자가 정확한 해소 사건을 제공하면 해당 대기가 풀리고 필요한 후속 행동이 한 번만 생겨야 한다. 같은 사건의 재전달이나 무관한 변화는 다른 대기와 반복 이력을 건드리지 않아야 한다. 원래 R39의 수명·질문·반복 보류와 R42의 반복 계수를 함께 판정하고, 확인된 공백의 구현·시험 수리와 관련 확인을 이 task에서 마친다. R40·R41·R43은 이번 배정에 포함하지 않는다.

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md, 스킬 AGENTS.md·시험-지침.md·이음새-정본.md를 읽는다. 공용 소스와 다른 task 기록은 읽기 전용이며 자기 workspace의 writes만 수정한다. source_repo의 docs 원자료는 C:/math에서 읽는다. 과거 문서의 run:은 C:/math/docs/do-math/continuous-development-2026-10-13 기준이다. Git 원자료는 필요할 때 git -C C:/math의 읽기 명령으로 확인한다.

## 끝낼 질문과 원자료

원문은 docs/do-math/시험-재편-2026-09-29/조사/결함-범주.md의 4-A·4-B·4-C·13-B다. closure-map/evidence의 requirement-state, tracking-state R39/R42, prior-review-state와 evidence-catalog는 원 요구·보존·재검토의 연결을 제공한다. 단계-전환표-2026-10-03.json의 operational_question_integration(B27), repetition_population_integration(B42), lifecycle_restart_and_public_request_verification(B108)의 실제 도입 변경·원보고·현재 소비자를 대조한다. 과거 Temp 보고가 없으면 정확히 남기며 counts만으로 현재 성공을 만들지 않는다.

1. 현재 수명 상태, questions.QUESTION_OWNERS의 질문 소유자, 반복 보류의 실제 생산·해소 모집단을 확인한다. 선언·생산 지점·해소자·현재 시험을 연결하고 등록표만으로 실제 진입을 증명하지 않는다. 기존 전체 행동·활동/검토 대기 조사는 r37-r38 소유이므로 반복하지 않는다.
2. 각 맡은 종류의 실제 진입, 조건 전 유지, 정확 해소 사건 뒤 owner 한 바퀴의 변화와 후속 하나를 판단한다. 공개 결정, 요구 변경의 빈 집합, 정확한 질문/대상 범위, 한도 뒤 사용자 계속, 재전달·재시작을 해당 생산 경로의 의미에 맞게 연결한다. 수명 종결처럼 재개가 허용되지 않는 상태는 종결 자체가 출구인 계약과 구별한다. 없는 과거 API나 가상의 내부 삭제를 만들어 출구를 입증하지 않는다.
3. 반복 결과는 현재 task_contracts.REPETITION_OUTCOMES와 REPEAT_LINEAGES를 기준으로 실제 생산값을 양방향 대조한다. 원래 11결과와 현재 추가/폐기된 값이 있으면 원ID와 이유를 남긴다. revisions.record_repetition/record_execution_outcome의 reset·retain·increment와 diagnose, 무산출 계보·판본 계수·문턱·한도, 같은 event_ref 중복 불변, 정확한 공개 계속의 한 출구를 검사한다. 수락·부분수락·거부·전제변경·공급자한도·보류·판정불가를 이름이 비슷하다는 이유로 같은 계수로 합치지 않는다. 제출 수리/설치 복구/자기점검의 별도 계수 전체는 R43에 남긴다.
4. 이 범위의 실제 JSON·사람용 status에 사유·다음 소유자·제약 좌표가 연결되고, 과제 대상 없는 질문·수명/반복 보류도 보이는지 판단한다. 이미 충분한 실제 표시 시험은 그대로 재사용한다. support/wait_reporting.py와 reporting.py는 진행 중 r37-r38 소유이므로 읽기 전용이다. 새 표시 결함을 확인하면 정확한 생산 입력·누락 값·필요 수정 경로를 보고하고 임시 별도 표시기나 복제 helper를 만들지 않는다.

R04가 확인한 다섯 limit 키 소비와 기존 hold(2,2,user)는 부분 성질이다. R34/R35의 허가·종결·철회 규칙 재사용과 R39의 실제 공개 전이는 구별한다. r31-fix의 지급 자료 정체성 및 원 제출 보존, r29-r30의 실패 이력·비재생·native 재수신 수리를 유지한다. B27/B42/B108과 직접 교차하는 PR/K/P2만 판정하며 전체 요구 완료로 확대하지 않는다.

## 수정 범위와 병렬 경계

task.json writes가 정본이다. questions/question_engine/revisions/task_contracts 및 수명·공개 결정·실제 반복 생산자의 필요한 부분, 지정 직접 시험·helper와 미러를 소유한다. core_engine/decision_engine/governance_engine/planning_engine/retention 변경은 이번 질문·반복 전이에 실제로 필요한 부분으로 한정한다. r31-fix의 source 정체성 및 다른 수용 기능을 바꾸려면 새 반례와 관련 회귀를 함께 제시한다. schema 또는 문서 계약 변경이 실제로 필요하면 쓰기 범위의 정본과 미러를 함께 맞추고 옛 호환층을 남기지 않는다.

진행 중 structure-finish의 doc_code/engine_context/smell_rules와 지정 문서·시험, r37-r38의 wait_rules/activities/reporting/wait_reporting 및 지정 시험은 수정하지 않는다. 두 task의 미완성 workspace를 입력으로 쓰거나 종료를 기다리지 않는다. 공통 공급자/표시 경계에 실제 결함이 있으면 정확한 후속 입력으로 남긴다. 소유 밖 코드가 필요하다는 이유만으로 자기 범위에서 가능한 수리와 확인까지 중단하지 않는다.

## 최소 확인과 인계

현재 코드·정확한 기존 단언·원보고 판본으로 충분한 성질은 정적으로 끝낸다. 변경한 동작과 실제 관련 소비만 공식 scripts/run_tests.py --jobs 1의 작은 선택으로 확인한다. 한 조합을 보이기 위해 모든 역할 초기화나 큰 흐름을 반복하지 않는다. 전체 일반/T3/변이/T4/T5, 외부 모델/Lean/예약 호출은 이번 배정이 아니다. 실제 외부 경계 대역을 사용하고 제품 owner·판정기를 가리는 patch로 전이를 만들지 않는다.

공식 mirror build/check와 변경쌍 bytes를 확인한다. 비용캐시 변경의 원 bytes는 evidence에 보존하고 own base로 복원한다. report에는 종류·결과별 충분한 성질, 확인한 공백과 수리, 실제 생산/해소/계수/표시 근거, 정확한 미결을 연결한다. 선택/고유row/exit/source SHA, 초기 실패·fixture 교정·소프트 초과를 구별한다. `python C:/math/services/async-development/check.py report C:/math/.async/dm r39-r42`를 통과한다. 공용 문서/queue/state, 다른 task, Git index, graphify 및 기존 연구 운전은 수정하지 않는다. 최종 통합판 관문·L01/Windows1314는 별도로 남는다.

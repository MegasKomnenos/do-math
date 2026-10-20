# 형식검사·신뢰·외부 작업 대기의 실제 소유자 연결

목표는 형식검사와 외부 작업의 대기가 조건을 보존하고 정확한 소유자의 현재 입력으로 해소되며 저장/공개 표시가 일치하도록 하는 것이다. r37-r38의 matrix에서 남은 아래 여섯 종류만 현재 소스·기존 단언과 대조하고, 확인된 공백의 구현/시험 수리와 최소 확인을 한 작업에서 마친다.

SESSION_JSON의 workspace/task.json과 inputs/context.md·plan.md·seams.md, managers/0029/review.md, tasks/r37-r38/report.json·evidence/review.md·wait-matrix.json을 읽는다. do-math AGENTS.md·시험 지침과 사용자 원문/모델/묶음 지시를 적용한다. 자기 workspace writes만 수정하며 C:/math 원자료·다른 task 기록은 읽기 전용이다.

## 종료할 여섯 질문

- formal_environment/formal_stopped: test_formal_wait_contract의 기존 parked() 뒤 kind 사후주입은 해소자 시험이다. formal_engine의 실제 환경 변화/정지 생산자와 현재 정식 검사 흐름을 먼저 대조한다. 실제 생산된 wait에서 조건 전 유지, 정확 환경·정지 원인의 해소, 다른 owner 보존, 후속 하나와 공개 표시를 연결한다. 이미 실제 생산을 증명하는 다른 시험이 있으면 그 근거를 재사용한다. formal_authority의 수용된 실제 생산 회귀를 보존한다.
- environment_interrupted/trust_check_stopped: formal_engine._trust_activation_steps/_trust_check_steps와 기존 test_trust_transition의 공개 fence/재시도/같은 owner를 읽는다. 중단된 신뢰 작업의 원 계보·확인 근거·조건을 보존하고 정확 공개 재개와 표시를 연결한다. 조건과 현재성 검사를 제거해 대기를 없애지 않는다.
- external_reconciliation/external_followup: external_engine._external_execution_record/_external_control과 실제 학술 effect control 시험에서 unknown·failed/cancelled 결과의 의무를 구별한다. 전송 사실·원request/receipt·같은 grant·재조정 증거, 조건 전 재전송 금지와 정확 공개 출구·후속1개·재전달 불변·활동 표시를 대조한다. r06-edges/r15-r16의 null/종료/정산 근거는 재사용하며, unknown을 성공/실패로 임의 확정하지 않는다.

여섯 종류 모두 하나의 새 end-to-end 시험이 있어야 한다는 추가 의무는 없다. 기존 실제 producer·해소자·표시 단언이 합쳐 충분하면 소스/원보고의 정확 심볼로 판정한다. constructor/등록/이름 언급을 실제 행동 근거로 확대하지 않는다. 기존 원자료의 실패·부재는 유지한다.

## 구현과 다른 작업의 경계

formal_engine/trust_validation 및 external_engine/external/academic/academic_engine의 실제 해당 결함, 지정 직접 시험과 전용 helper·미러를 소유한다. 진행 중 r39-r42의 core/lifecycle/governance/revisions/planning, r37-review의 review 소유 파일, r40-r43의 provider/repair/scheduler/observations와 공통 wait_rules/activities/reporting/wait_reporting은 읽기 전용이다. 현재 wait_reporting helper로 공개 JSON·사람 출력/조회 독립성을 확인한다. 범위 밖의 실제 결함은 입력·영향·정확 파일/함수로 보고하고 제품대역이나 허용 파일의 임의 자동해소로 우회하지 않는다.

실행이 필요한 변경 성질만 공식 run_tests.py --jobs 1의 작은 ID 선택으로 확인한다. Lean·HTTP·OS Job 등 외부 경계는 기존 대역을 사용하며 실제 외부 모델/Lean/예약/학술 호출은 하지 않는다. 전체 일반/T3/변이/T4/T5와 전 대기 반복도 하지 않는다. 정본 미러 build/check·bytes를 확인하고 캐시는 증거 보존 뒤 own base로 복원한다. report에는 여섯 종류별 기존 성질/수리/정확 남김·근거판본·실제 선택/row·exit/SHA·초기 오류/소프트초과·미실행을 구분한다. check.py report C:/math/.async/dm r37-edges PASS로 마친다. 공용 문서/queue/state·Git index·과거 원자료·graphify는 수정하지 않는다. 전체 R37/R38·PR10/G4~G8·L01/Windows1314의 완료를 주장하지 않는다.

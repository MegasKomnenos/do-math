# 검토 재승인 직후의 정확한 활동 해소와 검토 소유자 대기

사용자가 정확한 검토 교체를 승인하면 그 자리의 행동·활동 대기가 함께 해소되고 후속 행동은 하나만 생겨야 한다. r37-r38의 실제 F2를 수리하고 같은 review owner의 restoration/resource 대기에서 남은 실제 진입·해소 근거를 함께 마친다. 전체 R37/R38을 다시 조사하지 않는다.

SESSION_JSON의 workspace/task.json과 inputs/context.md·plan.md·seams.md를 읽는다. products는 자기 writes 안에서만 수정한다. C:/math의 원자료와 다른 task 기록은 읽기 전용이다. do-math AGENTS.md·시험 지침, 사용자 원문/모델/묶음 지시를 적용한다. r39-r42가 core를 수정할 수 있으므로 그 수용판에서 시작하며 시작 후 다른 사본을 소비하지 않는다.

## 맡은 결과

1. tasks/r37-r38/evidence/review.md의 F2와 review-owner-red/report.json·reproduction.py를 읽는다. 실제 선행 owner가 있는 최종 red를 근거로 삼고, 초기 review-2/3 fixture 실패와 혼동하지 않는다. 현재 core_engine.CoreEngineMixin._register_execution의 admission condition 생산과 review_engine.ReviewEngineMixin._release_review_wait/_authorize_review_replacement의 exact cycle/stage/round/slot 소비를 함께 수리한다. 정확 재승인 직후, 다음 실행 등록 전에 activity ready·waiting 부재·공개 표시 부재를 확인한다. 기존 action wait 제거·후속1개·원owner/회계·재전달 불변을 보존한다. 다른 slot/cycle/owner나 조건 미충족의 활동을 해소하지 않는다. kind만 보고 자동 해소하거나 불필요한 schema/호환 분기를 만들지 않는다. 어떤 좌표를 생산/소비할지는 현재 계약과 가장 작은 구현으로 결정한다.
2. 같은 review owner의 review_input_restoration과 review_resource_deferred를 현재 실제 producer/정확 소비에 연결한다. r37 wait-matrix의 constructor 삽입과 review_resource 현재 제안/기존 제안 해소 공백이 대상이다. 기존 review owner·source restoration·resource evidence 시험과 원보고를 먼저 읽는다. 충분한 경로는 재실행하지 않고, 부족한 경우에만 실제 복원 실패/복원 성공 또는 현재 자원 처분을 사용해 조건 전 유지·정확 후속·사유/담당자/좌표를 보완한다. task_ready 대상의 특정 review-cycle 종료라는 r08 역사 A-02 질문이 이 실제 경로와 직접 겹치면 현재 생산자/대상 의미로 판정한다. 옛 API나 가상 내부 삭제를 추가하지 않는다.

core_engine/review_engine/review_cycle/review_policy와 지정 직접 시험/helper·미러가 범위다. core의 다른 수용 변경·권한/입력/봉인/현재성/반복/종료 의미는 유지한다. r37-edges의 formal_engine/external_engine, r40-r43의 provider/repair/observations/scheduler 및 공통 wait_rules/activities/reporting/wait_reporting은 읽기 전용이다. 별도 표시기를 만들지 않고 현재 helper를 사용한다. 제품 정본 설명이 필요하면 자기 변경 함수의 문서와 보고에 정확 계약을 쓰고 공용 이음새 정본의 변경 필요를 manager에게 연결한다.

## 확인과 반환

기존 근거로 충분한 성질은 정적으로 판정한다. 바뀐 F2의 정상/반려·다른owner 보존과 직접 소비만 공식 run_tests.py --jobs 1로 확인한다. 실제 외부 모델/Lean/예약·전체 일반/T3/변이/T4/T5는 실행하지 않는다. red의 ready 기대를 삭제하거나 다음 admission까지 기다려 결함을 숨기지 않는다. 정상 대조·무관 사건·재전달과 필요한 저장/restart를 같은 작은 확인에 포함한다.

정본·미러 생성/check 및 변경bytes를 확인하고 비용캐시는 증거 보존 뒤 own base로 복원한다. report에는 구현 판단, exact 선택/실제row·exit/판본, 초기 실패/fixture 교정·미실행, 원 F2와 나머지 두 종류의 처분을 남긴다. check.py report C:/math/.async/dm r37-review PASS 후 제출한다. 공용 문서/queue/state·Git index·과거 원자료는 수정하지 않는다. 과제5종·다른 대기·전체 PR10/G4~G8·L01/Windows1314를 이 배정으로 종결하지 않는다.

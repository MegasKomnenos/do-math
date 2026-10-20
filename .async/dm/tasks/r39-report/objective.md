# 질문·반복 보류·사용자 pause의 실제 상태 보고

사용자가 status만 읽어도 답해야 할 질문, 정확히 계속할 반복 보류, 유지 중인 pause의 이유와 원요청을 찾을 수 있게 한다. r39-r42가 남긴 F2 세 표시 결함을 같은 reporting 생산/소비 경계에서 고치고, 기존 실제 owner 시험·관련 문서·미러·최소 확인을 한 작업으로 마친다. R39 전이를 다시 조사하거나 전체 R37/R38/R41을 이 작업에 넣지 않는다.

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md와 do-math AGENTS.md·시험-지침.md를 읽는다. source_repo와 다른 task 기록은 읽기 전용이다. C:/math/docs/do-math/continuous-development-2026-10-13의 사용자 결정·모델·묶음 지시가 원자료이며 과거 run:은 그 경로 기준이다. 자기 workspace의 writes만 수정한다.

## 확인된 입력과 끝낼 결과

원문 의무는 시험-재편-2026-09-29/조사/결함-범주.md의 13-B와 R39 수명·질문·반복 보류다. tasks/r39-r42/evidence/judgment.md의 F2, status-observations.json의 human 인덱스 3/6/10 및 각각 직전 JSON 행, managers/0030/source-review.json·review.md를 읽는다. 관측은 실제 status_report와 render_human_report의 반환이다. 별도 제품 함수를 교체한 재현이 아니다. r37-r38 수용판은 활동 condition 표시가 추가됐지만 이 세 결함을 바꾸지 않았다.

1. 실제 maintenance의 봉인된 결과가 user/research/operations 세 질문을 만들 때 JSON question_links에 있는 본문·owner·사유·질문 ID·발생 원문/실행 좌표·대상과 미해소 대상을 사람이 읽는 보고에도 연결한다. 과제0이나 target_ids=[]라는 이유로 누락하지 않는다. 부분 답변은 남은 대상만 계속 열려 있음을 구별하고, resolved/superseded를 현재 답해야 할 질문으로 표시하지 않는다. 기존 question_view의 원문 복원을 소비하며 질문 문자열을 파싱하거나 본문을 별도 저장하지 않는다.
2. 실제 accepted empty preparation의 task0/active hold1을 JSON과 사람 보고에서 구조적으로 찾을 수 있게 한다. 정본 공급자는 revisions.active_repetition_holds(runtime)다. lineage/lineage_id·event_ref·count/limit·reason·next_owner·release_condition 등 실제 보류의 식별과 해소에 필요한 정보를 보존한다. tuple key를 그대로 JSON에 노출하거나 새 보류 registry를 만들지 않는다. active hold와 해소된 이력을 구별하고 공개 정확 continue·재전달·restart 뒤 현재 보류가 사라지는 것을 기존 owner 시험에 연결한다. 현재 primary_blocker 우선순위를 무조건 바꾸거나 과제 없는 준비가 전역 정지라는 새 의미를 만들지 않는다.
3. 실제 user pause의 reason과 request_id를 operating_summary의 해당 blocker 및 사람 출력에 연결한다. 현재 report의 최상위 user_pause에는 이미 원 request_id/created_at가 있다. 결함은 원자료 손실이 아니라 요약 blocker와 사람이 읽는 표시의 누락이다. 저장된 같은 사실을 사용하고 별도 제어를 생산하지 않는다. 명시 user resume 전후 및 operator의 해소 불가 계약은 보존한다.

JSON 필드·정렬·표시 형태는 현재 reporting 계약에 맞게 가장 작은 구현으로 선택하고 실제 의미를 관련 CLI 설명/이음새 정본에 함께 반영한다. report는 같은 snapshot을 투영하고 render_human_report는 전달받은 report만 읽는다. 표시를 위해 새로운 상태 변경·외부 조회·현재 시계 판단을 추가하지 않는다. 기존 공개 질문 목록, action/activity/dispatch 대기와 r37-r38의 condition 표시를 유지한다. 필드 추가의 문서/직접 소비 검사까지 같은 작업에 포함하고 구현 상수에서 기대 결과를 복제하지 않는다.

## 쓰기 경계와 필요한 확인

runtime 쓰기는 reporting.py다. r39-r42에서 수용된 세 sim 파일의 실제 생산→저장→status 지점에 누락값과 해소 후 단언을 붙이는 것이 출발점이다. 기존 unit/sim 보고 시험·wait_reporting helper·관련 설명의 정확 허용 목록은 task.json에 있다. helper의 기존 action/activity API는 다른 수용 시험도 소비하므로 보존한다. 별도 표시기·복제 helper나 세 가지 작은 task를 만들지 않는다.

questions/question_engine/revisions/lifecycle_engine/supervision/wait_rules/activities와 core/review/formal/external/provider/repair/scheduler/observations는 읽기 전용이다. r37-review·r37-edges·r40-r43의 미완성 사본을 입력으로 쓰거나 종료를 기다리지 않는다. 필요 범위 밖 결함은 실제 입력·관측·필요 파일/심볼로 인계하며, 표시를 맞추려고 이미 수용된 전이·권한·반복 계수를 바꾸지 않는다. r39-r42의 시계 회귀도 보존한다.

기존 근거로 충분한 성질은 정적으로 판정한다. 새 표시와 실제 직접 소비만 공식 scripts/run_tests.py --jobs 1의 작은 선택으로 확인한다. 실제 owner의 과제 없는 질문/보류, 부분 해소/정확 계속, pause/resume 상태를 기존 표본에서 재사용한다. 독립 JSON 값과 실제 human 문자열을 확인하며 단순 status 헤더 존재로 누락 검사를 대신하지 않는다. 반복 대형 초기화나 새 전체 흐름은 요구하지 않는다. 전체 일반/T3/변이/T4/T5·외부 모델/Lean/예약은 범위 밖이다.

공식 mirror build/check와 변경쌍 bytes를 확인하고 비용캐시는 원 bytes를 evidence에 보존한 뒤 own base로 복원한다. report에는 세 F2의 실제 해결·정확 선택/고유 결과/exit/source SHA·새 공개 필드와 의미·미확인 범위를 기록한다. 이전 실패와 소프트 비용을 보존하며 다른 실행을 단일 통합판 성공으로 합산하지 않는다. check.py report C:/math/.async/dm r39-report PASS 후 제출한다. 공용 문서/queue/state·다른 task·Git index·graphify·기존 연구 운전은 수정하지 않는다. 최종 G4~G8·L01·Windows1314 및 다른 의미 질문은 별도다.

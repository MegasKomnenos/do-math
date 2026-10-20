# manager 0019: 관찰 중 완료 회수 수리 수용

이번 inbox의 완료 사건 r14-fix를 검수했다. inbox 시작 당시 r06-domain·r06-edges·r22-storage는 실행 중이며 정의를 유지한다. 이후 완료 사건은 다음 manager가 처리한다. 기존 r12-r13-fix는 이번 수용으로 선행이 충족된다.

## 직접 확인과 수용

check.py report는 PASS다. inspect_result.py/source-review.json은 baseline/base/workspace의 실제12변경·미러6쌍·캐시복원, 직접 불변 소비16파일과 공식 보고/하위row/선택·SHA·exit를 대조했다. r14-fix.diff의 전 변경과 현재 runner/ModelCalls/ObservationBatch, core._observe_running/_apply_inbox 및 scheduler._run_parallel을 읽었다. workspaces.py integrate가12파일을 충돌 없이 반영했고 integration-check.json에서 공용 bytes와 제출판이 같음을 확인했다. manager 제품 시험 재실행은0이다.

runner는1MiB read의 원행을 최대4개씩 전달한다. 중간 part의 end_offset은 마지막 완전 행, 마지막 part는 read offset이고 received 시각·row bytes/offset/first_row를 보존한다. ends_read는 local metadata이며 실제 stream 끝과 함께 caught_up/tick을 결정한다. owner allowance가 있는 pump는 future마다1callback 후 제어 수신으로 돌아간다. collect는 진입 완료 집합을 고정하고 callback 중 새 완료가 생기면 현재 게시 후 양보한다. 자기 결과는 자기 관찰 전체 처리 후 받는다. 단일 반환 future만 남은 경우 같은 read의 진입 허용량 안에서만 part를 합쳐 불필요한 작은 게시를 줄인다. 새 큐/스레드나 미게시 candidate 재진입은 없다.

core/scheduler/관찰 tracker/record schema/제어 수송은 task base와 공용판에서 불변이다. 기존 게시 성공 뒤 tracker commit·실패 rollback과 r08 제어/r03-fix 저장 계약이 유지된다. 변경한 두 공급자 native 저장 시험은 실제 원 bytes/행 좌표·정확 receipt·caught_up/tick·fresh tracker 재전달과 저장값을 단언한다. Codex의 delimiter 없는 마지막 행과 Claude의 strict JSONL 경계를 구별한다.

red-atomic-fixed는 같은 native1/64/1024·사건0.25초에서64/1024의32/512초로 실패한다. red-collect와 red-owner-pump는 각1failed/exit1이다. 최초 red-atomic과 native-parts의 새 fixture 오류는 제품 반례와 구별했다. related-final과 green-owner-pump의 미완결/exit -1은 성공으로 세지 않는다. 각각 실제 worker 오류와 accepted 뒤 불필요한 게시 비용을 보고 중단한 기록이다.

progress-final은20선택/20고유passed·exit0·138.4초다. 이후 계약 read 경계 회귀1개를 추가한 related-final-2는16선택/16고유passed·exit0·152.9초이며 Python876 SHA가 제출판과 같다. 앞 판본과 유일한 Python 차이는 test_port_calls.py이고 복원된 원파일 SHA와 기존 함수 AST 전부가 동일함을 확인했다. 이를 단일 전체36passed로 합산하지 않는다. 두 최종 실행의 fixture_counts/changed_during_run은 비어 있다. 모델 회귀68.562초의 소프트60초 초과를 유지한다. cleanup 안전 탐지 여유만4096→32768로 바뀌었고 실제 성공 기준1초·owner≤1, 총입력·사건 비용·생산 loop는 유지됐다. 가상1초는 벽시계 SLA가 아니다.

공용판은 task 최종판과18 Python파일이 다르다. runtime 차이는 r09의 integration.inspect_bundles 문자열 guard뿐이고 그 실제 diff를 확인했다. 나머지는 수용된 cross/제출/규모/비용/null 시험·helper다. 직접16소비에는 차이가 없고 이번 결과를 통합판 전건 실행으로 확대하지 않는다. 0012의 구조44건·과거 Temp 부재, R15/R16·PR11의 다른 slice, G4~G8·L01·Windows1314 실반려 미검사는 남는다.

R14/8-A의 맡은 F3와 F1/F2 보존 회귀를 해결·최종 통합판 대기로 수용한다. 원래 진행성 질문을 R15/R16 전체 정산이나 동기 HTTP 전건으로 확대하지 않는다.

## 다음 배정

기존 r12-r13-fix의 내용/선행 정의를 유지하고 r14-fix를 accepted에 넣어 준비 상태로 만든다. 새 r15-r16은 같은 반환 matrix/정산 helper를 공유하는 원문8-B의 R15/R16을 한 작업으로 묶는다. r11의 실제 반환 전제와 이번 진행성 수용판만 선행이다. 반환 경로×종류×시점에서 실제 반환 시 미적용 완료·owner·종료/예약·결과 증거를 판단하고 부족한 직접 단언/수리를 함께 맡는다. 중간 collect가 다음 바퀴로 넘긴 관찰 부채와 run 반환 미적용 완료는 구별한다. 알려진 unknown 종료를 confirmed로 바꾸지 않는다.

실행 중 null/저장 및 준비된 위임의 제품 쓰기와 겹치지 않는다. core·external_engine/session_slots/model_call·schema·공용fixture는 읽기 전용이고 scheduler/parallel/call_engine/formal_engine 등 지정 runtime의 실제 반환 결함만 수리할 수 있다. 범위 밖 실제 결함은 정확 입력/심볼과 남김으로 연결한다. 기존 구조44건은 수정하는 가까운 발견만 함께 다루고 나머지 묶음은 소유권 정리 뒤 배정한다. 현재 독립 작업이 있어 active를 유지한다.

context/plan/seams와 새 objective를 먼저 갱신한다. assignment-review.json으로 기존 정의 유지·새 의미 쓰기 교집합0(복원할 캐시 제외)을 확인한다. queue.pending.json을 check.py queue로 검사한 뒤 그 원바이트를 queue.json으로 원자 교체하고 공용 변경을 마친다.

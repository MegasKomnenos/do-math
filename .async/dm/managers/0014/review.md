# manager 0014: 제어 반려 수용과 명시 null 후속

이번 inbox는 r08의 정상 종료를 알린다. r09·r12-r13은 시작 당시 실행 중이며 두 정의와 준비된 r14-fix의 기존 배정을 유지한다. 검토 중 새로 도착하는 완료 사건은 다음 manager의 입력이다.

## 수용한 결과와 근거

r08의 실제 변경16파일은 정본 runtime2·시험6 및 미러8이다. check.py report는 PASS다. base/workspace의 파일 집합과 SHA, 각 변경의 공용 시작판 일치, 미러8쌍, 검토한 changes.diff와 실제 diff의 일치를 직접 확인했다. runtime AST 변경은 submit_control·ControlTransport.worker_submit·_reject_delivery_file 세 함수뿐이며 다른 함수와 관련 불변16파일을 대조했다. workspaces.py integrate는 충돌 없이16파일을 반영했다. inspect_result.py와 source-review.json, tasks/r08/integration.json이 재검토 근거다.

worker_submit은 list/dict kind로 REQUEST_KINDS membership의 TypeError를 내던 경계를 문자열 검사 뒤 정확 ValueError로 반려한다. submit_control은 source locator가 빠진 경우와 host path resolve/read의 OSError·ValueError를 구별해 ValueError로 연결한다. 정상 source 정규화/내용·request identity는 기존 경로를 유지한다. _reject_delivery_file은 이미 inbox에서 발견한 파일명을 유효 worker request ID로 다시 검사해 pump를 중단하던 전제를 제거했다. path.stem은 손상 파일의 반려 좌표이며 실제 outbox의 정확 bytes/SHA 영수증과 다음 파일 처리가 유지된다. 공개 worker_submit/worker_receipt의 안전한 ID 검사는 바꾸지 않았다.

unit의 NOT_TEXTS 정상/반려 대조, source 입구의 no-inbox/no-state-change 및 뒤 정상 source 저장, 손상 파일명 뒤 정상 delivery와 fresh receiver를 검토했다. owner 반려 시험은 기존 action별14대표·손상 envelope7·중첩16입력에 정확 사유, processed/history의 추가1개, 원 bytes, 도메인/예약/실행 불변, 재시작과 뒤 정상 제어의 durable 결과를 연결한다. stale 시험은 내부 status 주입을 제거하고 공개 task_scope revise로 task_ready 전제를 없앤다. 공개 close 뒤 지연 input/maintenance 반려와 후속 configure 저장도 보존한다.

새 두 transport 시험은 같은 실행의 서로 다른 binding으로 A-first/B-first를 실제 receive 순서에서 강제한다. 첫 owner 반려·같은 요청 replay·다른 payload 충돌·fresh receiver의 정확 delivery_validation/SHA/bytes·각 sender의 원 receipt를 확인하며 publish1/save0과 head/runtime 불변을 단언한다. 뒤 정상 draft는 실제 owner/CAS/store의 publish2/save1·receipt1·execution stopping으로 이어진다. 한 endpoint의 동시 writer 시험이나 R10의 native/receipt 결속 양순서와 다른 질문이다. workspace draft_path의 정확 capture issue는 제어 경계에 한정하며 R09 확장/참조 전체를 대신하지 않는다.

## 확인 범위와 남김

원 red3선택/3error/exit1은 세 runtime 결함을 드러낸다. focused8passed/exit0과 related26passed/1error/exit1 뒤, 새 stale fixture의 deepcopy import 누락만 고친 stale-final1passed/exit0을 구별한다. 원보고 SHA와 선택/고유 실제 row, unit/sim/flows 하위 result.json을 직접 대조했다. 모든 실행 changed_during_run=[]이고 마지막 Python876 SHA는 제출판과 전건 같다. focused/related와 최종판의 유일 Python 차이는 test_engine_controls.py다. 다른 관련 성공은 불변 함수/직접 소비 범위로 재사용하며 단일 전체 성공으로 합산하지 않는다. 종료 코드는 task가 회수한 기록이며 manager가 제품 시험을 다시 실행하지 않았다.

task의 공식 미러 --check exit0/1337파일 드리프트0 기록과 실제 변경8쌍 byte 일치를 사용한다. build 종료 출력 미회수는 그대로 남긴다. 비용 캐시2개는 base로 복원됐고 공용 캐시를 덮지 않았다. B129 원보고 SHA·정확71관련 row·base/제출판 비교를 대조했다. 원보고 전체 successful=false와 과거 Temp 보고 부재를 유지하며 counts를 합산하지 않는다. PR07 B15/B23/B59는 task의 실제 hunk 연결과 현재 보존된 경로의 해당 제어 성질만 유지한다.

R08의 관측된 세 결함과 현재 유한 질문의 수리는 수용한다. 특정 역사 review-cycle 종료가 현행 supplemental_research/task_ready에 미치는 의미와 공개 execution/review/task 삭제 생산자는 확인되지 않았다. 그 축은 실제 생산자/대상 의미를 먼저 판정하고 내부 del이나 옛 API 복원으로 채우지 않는다. 다른 의미 작업에서 직접 다룰 전이와 함께 묶을 남김이며 이번 결과를 2-A 전체 완료로 바꾸지 않는다. r03-fix·r14가 반영된 공용판 전체에서 새 실행한 증거는 아니다. 전체 G4~G8·기타 K/P2·L01·Windows1314는 남는다.

## 다음 배정과 게시

r08 수용으로 기존 r14-fix의 r14/r08 선행이 충족된다. r14-fix는 관찰 처리 F3를 이어받으며 이번 제어 세 함수의 의미와 현재 저장 계약을 보존한다. 진행 중 r09·r12-r13의 배정/사본은 그대로다.

독립 r06은 원래1-C의 남은 명시 null 생산 필드→실제 모든 읽기 소비자 질문을 맡는다. r04/r05의 확인된 null slice와 r03-fix 저장 계약을 재사용하고 현재 실제 생산/읽기 근거로만 남은 공백을 좁힌다. 동일 key의 다른 객체, 명시 null과 부재, 실제 None 필드 생산과 지역 변수/기본값을 구별한다. AST/검색은 발견 보조이며 목록 자체를 실행 증거로 세지 않는다. 기존 producer/record storage와 전용 null 시험의 필요한 보완·미러·최소 확인을 한 작업에 묶고 PR06 B58의 해당 slice만 함께 판단한다.

r06의 runtime·공통helper는 읽기 전용이고 세 기존 작업의 의미 있는 writes와 겹치지 않는다. 따라서 depends_on=[]이다. 캐시는 각 base로 복원한다. 실제 runtime 결함은 생산자→소비자·재현·필요 쓰기를 정확히 남겨 소유 작업 뒤 수리로 연결한다. 새 영구 null registry나 전체 관문 반복을 만들지 않는다. 동시 runtime 변경이 null 증거의 직접 심볼을 바꾸면 이후 통합에서 그 영향만 대조한다. task 수나 병렬 인원 자체가 목적은 아니며 실행기는 max_workers=3의 빈 자리에서 준비된 작업을 시작한다.

context/plan/seams와 r06 objective를 먼저 갱신한다. r08을 accepted에 추가하고 r06을 넣은 queue.pending.json을 검사한 뒤 검사한 바로 그 파일을 queue.json으로 원자 교체한다. queue-check.json은 검사/게시할 판본과 문서 해시를 남긴다. 상태는 active이고 게시 후 이번 세션의 공용 변경을 끝낸다.

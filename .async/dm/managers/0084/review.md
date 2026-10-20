# manager0084: 캡처 게시 수리의 부분 수용과 남김 분할

inbox의 종료 결과는 g5-core-tail 하나이며 report 상태는 partial이다. 정본5파일 diff와 현재 생산/소비 계약, 원시험 자료를 읽고 workspaces.py integrate로 정본5·미러5, 총10파일을 충돌 없이 통합했다. 제품 변경은 task 산출물의 통합뿐이다. g23-handoff의 시작 정의/objective와 입력은 유지한다. 그 이후 도착한 완료 사건은 이번 수용에 끼워 넣지 않는다.

## 수용한 결과와 판단 이유

CoreEngineMixin._publish_control_request는 게시 실패 뒤 _reload도 실패하면 그 오류를 전파한다. 성공한 Git CAS의 응답만 유실됐는데 재조회까지 실패하는 경우를 최종 rejected로 확정하던 결함을 고쳤다. 재조회로 영수증이 없음을 실제 확인한 경우의 기존 rejected는 유지한다. self.head가 원 head이면 임시 instance/runtime을 복원하며, 새 durable head를 이미 채택했으면 이를 되돌리지 않는다. ControlTransport.receive의 publish 호출 뒤에만 _store가 있는 점과 pump가 GitStateStoreError를 최종 반려로 포장하지 않는 점을 확인했다. 실제 확인 범위는 시험의 Git 읽기 장애이며 모든 종류의 후속 예외/공개 owner 복구 완결을 인증하지 않는다.

_capture_native_submission은 재조회 finally에서 같은 원 head의 임시 후보를 복원한다. 기존에는 _reload 실패가 복원보다 먼저 전파돼 submission_receipt/intent와 stopping 전이가 원 head의 메모리에 남았다. 저장소 복구 후 prior receipt를 재사용하고 원 final bytes·submission_checked 1회를 유지하는 직접 단언을 확인했다. _save/_reload는 저장 결과를 채택한 뒤 _evaluate_stops를 호출하므로 head 전진 후의 예외 질문은 이번 수리만으로 해소했다고 하지 않는다.

외부 오류 주입은 tests/support/submission_scenes.lost_acknowledgment의 실제 backend.update_ref 수행 뒤 OSError와 backend.object_info의 GitBackendError다. 제품 publisher/Repository/validator를 대역으로 바꾸지 않았다. 원상태·수송영수증 부재·실제 durable accepted receipt·재접수 publication_id/head/무중복을 직접 검사한다. sim의 기존 자기점검 시험도 unreadable ref의 확정 반려 기대를 오류 전파/영수증 부재/원 tracker 유지·복구 뒤 동일 delivery 수용으로 교정했다.

추가 세 성질은 실제 inbox 파일 삭제 경쟁 뒤 다음 요청 진행/한 번 적용과 waiting owner wakeup, 관찰 의무 게시 뒤 종료 관측에서 worker-inbox 미전달이다. 마지막은 외부 ObservationBatch 종료 관측이며 실제 OS 자식 종료 시험은 아니다. 두 설명 파일은 이 미확정 게시/복원/원 영수증 재사용의 계약을 설명하며 미러5쌍의 bytes가 일치한다.

## 필요한 검수와 한계

verify.py의 결과는 verification-review.json이다. 원6실행의 report SHA·coverage SHA, 선택과 고유 실제행, counts·complete·successful·fixture/실행중변경·관측exit, 실행별 변경Python3파일의 보존SHA를 대조했다. 전체 과거 소스 재감사는 하지 않았다. 수정시험5본문과 기존회귀2본문의 동일 AST passing 연결을 확인했다(비용 docstring 제외). 검수 스크립트가 selected를 개수가 아닌 목록으로 읽도록 한 번 교정했으며 제품 시험 재실행은0이다.

capture-before=1failed, capture-after=2passed/1failed, capture-regression-before=1failed, capture-races-final=3passed, native-regression-before=1failed, native-final=2passed다. 앞 두 실행의 ref_oid fixture 오류는 제품 결함 재현으로 세지 않는다. object_info 교정 뒤 시작 제품의 explicit 실패는 GitStateStoreError 미전파이고, 아직 native를 수리하지 않은 판의 실패는 원상태 tuple 불일치다. 이 원실패와 수리 후 직접 단언을 각각 확인했다. 모든 실행은 complete=true·fixture/실행중변경0·부분gate/최상위passed/closing_eligible=false·관측exit1이며, 서로 다른 부분판을 전체성공으로 합산하지 않는다.

원58arc/63행 중 직접 해소2arc/3행을 같은 함수 AST와 raw 도달에 연결했다. 남김56arc/60행은 29함수의 원/제출좌표·보존 이유를 가진다. 이 수치는 역사 배정의 처분이며 최종 전체G5 gap 수가 아니다. 새 분기제거/제외는 없다. 실제 provider/Windows Job/Lean·전체G4/freshG5·변이·T4/T5를 이번 manager가 실행하지 않았다. 작업자의 cache 복원 보고는 실제 통합 변경이10경로뿐인 결과와 양립한다.

## 다음 배정과 실익

이전 core 남김 전체를 다시 한 세션에 맡기는 대신 같은 파일의 계약 질문을 세 묶음으로 줄였다. scope-partition.json에 남은116좌표가 정확히 한 번씩 배정됨을 기록했다. 각 task에서 관련 구현·필요 확인·설명/미러를 함께 마친다. 같은 core_engine.py와 직접 helper/설명의 결과를 다음 사본이 소비하므로 순차 배정한다. 독립 g23-handoff는 계속 병행한다.

- g5-core-edge: 입구·보존자료10arc/12행, 10함수. 영수증 ancestry·head 전진/재조회·원요청/target/response lineage·overflow 현재성·check 우선순위·파일/Git 경계. 선행 g5-core-tail.
- g5-core-apply: 제출·적용24arc/24행, 7함수. currentness·mixed/unrelated impact·무영향 mutation·private insight·preparation/revision/condition·fixed plan. 선행 g5-core-edge.
- g5-core-recover: 복구·정산22arc/24행, 12함수. 현재 위임 권한·reassessment/goal/native 복원·운영처분·수용 뒤 로컬 실패/정산·cleanup gate. 선행 g5-core-apply.

이 분할은 기능별 시험quota가 아니다. 실제 생산/참조/불변식으로 충분하면 정적 판단으로 끝내고 새 실행을 요구하지 않는다. 앞 task가 partial이어도 다음 task가 그 남김을 자동으로 완료/인수하지 않는다. 후속 manager가 실제 남김과 통합 영향에 따라 미시작 배정만 조정할 수 있다. 작은 경로별 별도 task와 소유자 탐색 감사는 추가하지 않았다.

최종 전체T4는 core 소비판의 추가 수리 가능성이 아직 남아 이번에는 반복 실행하지 않는다. boundary/test_engine_cli.py·test_engine_cli_advanced.py·test_review_git_read_fault.py 등이 실제 ResearchEngine/check/제어와 Git 읽기 경계를 소비한다. G4/G5/G6나 g23의 종료를 포괄 선행으로 삼지 않고 실제 core 소비판이 정해지면 T4를 바로 배정한다. 새 읽기 조사로 이를 지연시키지 않는다. G6는 최종 T3의 실제 함수/선택 색인을 소비한다.

사용자 storage-scope-direction-2026-10-15.md와 원설계3.3/A22를 적용했다. 구체적 두 게시 수리를 수용하며 공통codec·검증게시·기존업무 보장, cleanup 두 CAS·closed source·overflow retry·nested condition·assignment 수리는 관련 새 변경이 없으면 반복하지 않는다. 취소된 가족별 전필드 재입증2건은 유지하고 전가족/새reader/옛head quota·장기감사·동일 환경probe·반복 공급자 호출을 만들지 않는다. 원증거는 보존했다.

기존100정의·취소2건을 보존하고 accepted97, 새3개를 포함103정의·미해결4·active다. 동시 시험슬롯은 새core1, g23=0이며 max_workers10·gpt-6.1-sol/high를 유지한다. 환경6arc/10행, L01 Q1/Q2와 원UTF-8 bytes, 현지원 quota/복수result/동적schema 원자료, 최종G1~G8은 미완료다. 무응답/개발worker를 외부결정/실증으로 대신하지 않는다.

context/plan/seams·objective를 먼저 갱신하고 queue.pending.json을 check.py queue로 검사한다. 검사한 파일의 bytes를 확인해 queue.json으로 원자 교체하는 것을 마지막 공용 변경으로 한다.

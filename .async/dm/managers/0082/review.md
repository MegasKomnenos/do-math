# manager0082: core 부분 수용과 원의무 인계

이번 inbox의 g5-core-gaps(partial), g1-handoff(complete)를 검토했다. 종료 상태와 별도로 실제 정본 diff·현재 정의·원보고를 대조했다. workspaces.py integrate로 core20파일과 handoff files=[]를 충돌 없이 통합했다. 두 결과를 accepted에 넣으며 core의 미완료를 완료로 바꾸지 않는다. inbox.running의 g7-scheduler 정의와 objective는 보존한다.

## g5-core-gaps의 유효한 변경

정본 제품2(core_engine.py/integration.py), 시험5/helper1, 설명2와 공식미러10쌍이다. 모든 정본 diff를 읽고 다음 계약을 확인했다.

- integration.bundle_impact_request는 실제 보존 assignment별로 같은 assignment의 검토 집합을 제외해 요청을 계산하고 정확히 같은 결과만 채택한다. 후보가 없으면 제외 없이 새 요청을 만든다. 오래된 검토가 현재 영향에 들어올 때 새 검토가 자기 입력을 무효화하던 유한 domain graph 회귀를 수리했다. header 일치만으로 승인·제외하지 않고 기존 신원/고정입력/이전hash/독립성/봉인을 유지한다. 공개 owner에서 두 assignment가 생성되는 전체 흐름 인증은 아니다.
- _receive_submission의 수용 후 maintenance cleanup은 GitStateStoreError도 로컬 효과 실패로 처리한다. 최신 게시 상태를 읽고 동일 실행의 아직 게시하지 못한 maintenance_cleanup 삭제 사실만 보존해 retention.record_cleanup_interruption에 전달한다. accepted 응답·영수증·output_accepted와 완료 경로를 유지한다. archive/final CAS 두 외부 실패 위치의 직접 시험을 확인했고, 재적재 불능 Git 오류는 계속 전파된다. 자기 writer lock 아래 _maintenance_cleanup의 게시/삭제 순서와 retention의 history_start·completed_paths 소비를 읽었다.
- _resume_input_overflow_action의 live 중복 검사는 activities.wait_for의 전실행 종료 요구와 assign_execution의 waiting 거절로 줄였다. _resolve_input_overflow_question은 questions.link/close가 보장하는 닫힌 질문의 원해소를 보존한다. 정확 owner/wait/condition과 저장 enum은 유지한다. 두 전이 정본을 직접 읽었다.

source 개정 시 closed 과제 보존, 실제 read-log lock 파일 오류, 다른 host의 check, frozen review upkeep, nested condition 이름 결박, 잘못된 native final의 원결과와 재접수, goal/impact 봉인 손상의 원판정/원생산자 routing은 관련 시험의 직접 단언 범위로 수용한다. 실제 공급자/Windows Job/Lean이나 전체 관문 성공으로 확대하지 않는다.

## 실제 검수 범위와 한계

verify_results.py의 최종 성공 결과는 verification-review.json이다. manager 제품시험/실호출0이다. 원9실행의 report·관측exit·선택과 고유 실제행·fixture/실행중변경·변경 Python8파일의 보존 source SHA를 대조했다. 원coverage와 같은 함수 AST의 도달 연결, 제출 변경 시험본문12개의 동일 AST passing 기록, 미러10쌍을 확인했다. 전체 과거 파일 hash 감사는 하지 않았다. 검수 스크립트의 nested 함수명과 stage2 원문표현 처리 오류를 교정한 뒤 성공했으며 제품 오류나 시험 재실행으로 세지 않는다.

원순서의 결과는 regression-before=1failed, integration-after=4passed, core-boundaries-before=1passed/1failed/1error, cleanup-regression-before=1passed/1failed, core-boundaries-after=3passed/1error, core-contracts=3passed/1error, preserved-boundaries=5passed/1failed, cleanup-impact-final=1passed/1failed, cleanup-settlement=1passed다. 전부 complete=true·fixture/실행중변경0, 부분 gate/최상위passed/closing_eligible=false·관측exit1이다. 마지막 수정본문들의 passing 연결은 확인했으나 다른 부분판을 단일 최종 전체성공으로 합치지 않는다. 초기 fixture/기대값 오류와 두 제품수리의 원실패는 task judgment에 보존돼 있다.

원70arc/94행은 raw도달9arc/28행·제거3arc/3행·남김58arc/63행이다. 원/제출SHA와 좌표·관측을 대조했다. 남김은 core뿐이며 integration의 원 안정화 오류는 제거됐다. 이 수치는 과거 배정 좌표의 처분으로 현재 전체 G5 gap 수가 아니다. 권한/고정 입력·현재성·혼합 영향·운영 처분/복구·외부 오류 등은 g5-core-tail에 묶는다. 불가능한 상태 조립·좌표별 시험 quota나 자동 제외를 요구하지 않는다.

## g1-handoff와 최신 수용분

원문 stage1 19+stage2 11의 ID와 실제 원문 발췌30개, 수용 task63개의 report/review/integration 링크, 시작판 현행 정의93파일 SHA를 정적으로 대조했다. judgment와 행별 요구·한계·다음 조건을 읽고 제품 변경 없는 인계로 수용했다. 이는 G1 최종 인증이나 G2/G3/G8 완료가 아니다. 기존 의미 판단·codec·공통 저장 보장을 재감사하지 않았다.

인계의 고정 시작판은 manager0080이며 그 원문은 보존한다. 이번 core와 이미 수용한 G7 조사에 대한 현재 보충은 handoff-delta.json에 둔다. 영향 assignment·cleanup·overflow와 새 직접 단언을 관련 의무에 연결하고, 남은58/63 및 최종 관문/실환경을 유지한다. g7-boundary-scope의 옛 bootstrap 계약 보정은 manager0081 검토를 재사용한다. g7-scheduler가 처리하는 HOLD 이전 입구/예약 계약은 core 연구처리 수리의 선행을 요구하지 않는다.

## 후속과 저장범위 지시 적용

새 g5-core-tail은 같은 core 소유의 남김과 필요한 구현/검증/설명을 묶는다. 새 g23-handoff는 K61/P2 12와 PR25의 수용 근거·현행 정의·실제 남김을 연결하는 독립 읽기 작업이다. 매핑을 실제 검토로 간주하지 않으며 미검토 slice는 정확한 다음 판단으로 남긴다. core/예약의 미완성 제공자를 기다리지 않는다.

사용자 storage-scope-direction-2026-10-15.md와 A22를 적용했다. 구체적 계산·CAS 수리를 수용하고 공통codec/검증게시·기존 업무 보장은 재사용했다. 취소2건은 유지하고 전가족/전필드/새reader/옛head quota·반복quota호출·같은 환경probe·장기감사를 추가하지 않는다. 기존 산출물과 원실패는 보존한다.

기존98개 정의·취소2건을 보존하고 accepted95개, 새2개를 포함한100개 정의로 active를 유지한다. 새 core 정본76/미러76 허용경로와 running 예약의 교집합0, g23 writes=[]다. 시험슬롯 core1+예약1=2, g23=0, max_workers10·gpt-6.1-sol/high를 유지한다. G4/freshG5·G6와 최종T4/G7/G8은 실제 소비판 수용 후 연결한다. 환경6arc/10행·L01 Q1/Q2/원UTF-8 byte·현지원 quota/복수result/동적schema 원자료 공백은 미해결이며 이번 결과로 덮지 않는다. 무응답과 개발worker를 외부 결정/실증으로 대체하지 않는다.

공용 context/plan/seams와 objective·배정근거를 먼저 갱신한 뒤 queue.pending.json을 check.py queue로 검사하고, 검사한 bytes를 queue.json으로 원자 교체해 게시한다. 게시 후 공용 변경을 끝낸다.

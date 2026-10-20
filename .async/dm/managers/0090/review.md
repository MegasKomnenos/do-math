# manager0090 판단

이번 inbox의 g5-core-recover는 중복 완료 사건이고 g7-t4는 디스크 부족으로 중단된 작업이다. 새 제품 결과를 통합하거나 accepted에 추가하지 않는다. 기존 수용107건을 유지하고 g7-t4의 미실행 범위를 새 g7-t4r에 배정한다. 제품 코드 수정과 시험 실행은 하지 않았다.

## 사건과 확인 범위

g5-core-recover는 manager0089가14파일을 통합·수용하고 큐 게시와 최종 응답까지 마쳤다. 현재 accepted, task ID와14경로가 있는 integration.json, 0089 session.log의 PASS queue·os.replace 성공·최종 응답을 읽었다. 현재 queue.json SHA는0089 queue-check.json의 checked_sha256과 같다. sources/archive-resume-2026-10-16.md의 재전달 지시에 따라 수용된 제품 파일과 과거 실행을 다시 해시·검증하거나 integrate하지 않았다.

g7-t4의 session.log에는 첫 안내와 stdout 기록 중 디스크 공간 부족(os error112)만 있고 report.json이 없다. 공식 workspaces.changes로 baseline.json의2,773파일과 workspace를 대조한 변경 경로는0이다. 실행 자료·수리 결과가 없는 중단을 T4 완료나 무변경 review로 수용하지 않는다. 원 task 정의·objective·로그·사본은 보존하고 cancelled에 넣는다. sources/archive-resume의 새 ID 복구 지시와 protocol을 적용했다. 확인한 사실은 recovery-review.json에 남겼다.

inbox.running은 비어 있었으나 검토 중 state에서 pr-base-tests running과 pr-base-ports launch_failed를 확인했다. 후자는 Existing workspace or snapshot 오류로 pending에 들어온 새 사건이다. protocol3절에 따라 이 사건의 원자료·복구 판단은 다음 manager가 처리한다. 이 manager는 두 task의 정의/objective/입력을 바꾸거나 미완성 산출물을 소비하지 않았다. state.json도 편집하지 않았다.

## 다음 배정과 이유

새 g7-t4r는 g5-core-recover 수용판의 전체 T4·직접 결함 수리·최소 확인·설명/미러를 맡는다. 중단 task에서 소비할 결과가 없으므로 원래 배정 범위를 유지한다. 공유 전체관문 슬롯1·jobs1이며 독립 읽기 review는 슬롯0이다. 미시작 g45-final은 선행과 report/integration 입력을 g7-t4r로 바꿨다. 전체일반/freshT3의 같은 수리판 소비와 공유 자원 순서를 유지하며 역사 review 전체를 장벽으로 만들지 않는다.

새 서비스는 base 디렉터리를 만들지 않는다. 새 T4 objective와 미시작 G45 objective에 baseline.json/objects의 시작 bytes·부재, 공식 restore로 필요한 파일만 복원하는 방법을 명시했다. 예전 prepare.py와 과거 사본 경로는 그대로 실행할 전제가 아니라 보존된 참고다. 진행 중 review의 입력은 고정된 채 유지한다. 시작된 모든 queue 정의도 원래 spec과 같고, 변경한 기존 정의는 아직 시작하지 않은 g45-final 하나다.

새 기능이나 독립 제품 결함이 발견된 세션이 아니므로 재개 외 별도 task를 만들지 않는다. 저장범위/A22의 공통codec·기존 업무 성질 재사용을 유지하고 가족별quota·반복실호출·과거 증거 전수 재감사·장기감사를 배정하지 않았다. 이미 수용한 정산/권한 성질도 이번 중단 때문에 다시 확인하지 않는다. 114정의·accepted107·cancelled3·미해결4, active다. G1~G3 최종연결·최종G4/freshG5/G6/나머지G7/G8과 환경6arc/10행·L01 Q1/Q2/원UTF-8 bytes·현재 공급자 quota/복수result/역할동적schema 원자료 조건은 그대로 남고 Q3의 해결도 유지한다.

## 게시와 보존

공용 context/plan/seams와 objective를 먼저 갱신한 뒤 queue.pending-0090.json을 준비한다. check.py queue를 통과한 동일 파일만 queue.json으로 원자 교체하며 이것이 마지막 공용 변경이다. publication-plan.json은 정의 변화와 문서 SHA, queue-check.json은 실제 검사 결과와 게시할 파일 SHA를 기록한다. 수용·통합·종료 task의 정리는 manager 종료 뒤 실행기에 맡기고 미수용 원자료는 보존한다. 새 통합이 없으므로 별도 integration 기록을 만들지 않는다.

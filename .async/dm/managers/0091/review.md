# manager0091 판단

이번 inbox의 pr-base-ports는 기존 사본 충돌로 기동하지 못한 review다. 완료한 결과를 수용하는 사건이 아니므로 integrate나 accepted 추가는 없다. 원배정·objective/scope/inputs·base/workspace를 보존하고 이 ID를 cancelled에 넣으며, 같은 유한 질문을 새 pr-base-ports-r로 복구한다. 제품 수정과 제품시험은0회다.

## 사실과 판단 범위

inbox.completed는 launch_failed/returncode null과 `Existing workspace or snapshot: use a new task ID to recover it`를 보고한다. 현재 state도 같은 실패를 기록하고 worker PID가 없다. workspaces.py:_prepare의137~138행은 workspace/base/baseline 중 하나가 있으면 task.json·baseline.json 작성과 worker 기동 전에 거절한다. 실제 디렉터리에는 objective.md·scope.json·inputs와 base/workspace 각387파일만 있고 report.json·task.json·baseline.json·session.log·evidence·integration.json은 없다. 시작판이 완성됐거나 실제 변경이0이라고 파일 수로 판단하지 않는다. 공식 changes/integrate에 필요한 시작 목록과 task 정의도 없고, 읽기 review의 판단 산출물이 없으므로 수용할 결과가 없다. 디스크 중단 재개의 기존 기록 및 protocol의 새 ID 복구 절차를 적용한다. 상세 관측은 recovery-review.json에 보존했다.

이 판단은 새 사건의 파일 상태와 준비 guard에 한정한다. 기존 수용107건의 제품 bytes/실행을 다시 검사하지 않았으며 진행 중 task의 미완성 산출물은 소비하지 않았다. 원 pr-base-ports 디렉터리와 기록은 삭제하거나 고치지 않는다. state.json도 수정하지 않는다.

## 복구 배정과 남은 결과

pr-base-ports-r는 원0089 scope.json을 그대로 복사하고 기반1b의 외부 효과/포트 계약, 1c의 판정·효과 이동/절단의 남은 실제hunk 의미 판단을 맡는다. objective의 두 질문·직접 현재소비·수용 성질 재사용·원자료 한계·제품시험 금지와 새 전수감사 제외를 유지한다. 새 recovery 안내와 실제 task ID의 report 검사만 보완했다. 실제 선행은 수용된 g5-core-recover·pr-ports이며 writes=[]·시험슬롯0·gpt-6.1-sol/high다. 과거 코드가 필요할 때만 공식 restore로 필요한 경로를 별도 새 디렉터리에 복원하며 불완전 원 사본을 시작판으로 삼지 않는다.

inbox.running의 pr-base-tests·g7-t4r와 미시작 g45-final을 포함한 기존114개 정의는 모두 보존한다. 두 running task의 objective와 고정입력도 불변이다. 전체관문은 g7-t4r jobs1 다음 g45-final jobs3이며 독립 두 기반review는 시험슬롯0으로 병행한다. review를 전체관문 선행 장벽으로 추가하지 않는다. 판단 중 도착하는 새 완료사건은 다음 manager가 처리한다.

새 결함/기능 결과가 없는 기동 복구이므로 별도 제품work를 만들지 않는다. 저장범위/A22의 공통codec·기존업무 보장 재사용을 유지하며 가족별quota·반복실호출·과거시험 재감사·장기감사를 추가하지 않았다. 기존 목표·G1~G8 및 L01 Q1/Q2/원UTF-8 bytes·환경6arc/10행·현재 공급자 quota/복수result/역할동적schema 원자료의 남김은 그대로다. Q3 해결도 유지한다. 최종 stable T3/색인 뒤 G6, G1~G3의 최종연결과 나머지G7/G8은 기존 계획에 남는다. 115정의·accepted107·cancelled4·미해결4로 active다.

## 게시

공용 context/plan/seams와 새 objective/scope를 먼저 완성한다. queue.pending-0091.json에서 기존 정의 불변·신규 배정·수용/취소 및 의존관계를 check.py queue로 확인하고, 통과한 바로 그 파일만 queue.json으로 원자 교체한다. 이것이 마지막 공용 변경이다. publication-plan.json에는 전후 배정과 공용 문서/새입력 SHA를, queue-check.json에는 실제 검사 결과와 검사한 queue SHA를 남긴다. 수용·통합·종료 사본 정리는 manager 종료 뒤 실행기에 맡기고 미수용 원기록은 보존한다.

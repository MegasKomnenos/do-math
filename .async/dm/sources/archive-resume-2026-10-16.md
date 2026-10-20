# 새 서비스 코드로 사본 정리·재개

사용자가 2026-10-16 끝난 작업의 workspace/base 정리와 반복 비용 개선이 반영된 services/async-development를 사용해 기존 작업물을 정리하고 재실행하라고 지시했다.

10:31경 C: 여유0으로 상태 저장과 g7-t4 시작 로그 쓰기가 실패했다. state.json의 기존 running 표시는 stale이며 운영자가 runner21300/manager4612/worker21876이 존재하지 않음을 확인했다. manager0089는 g5-core-recover를 수용하고 큐를 실제 게시한 뒤 응답까지 마쳤다. 새 runner의 재개에서 이 이벤트가 다시 전달되더라도 기존accepted/integration/최종로그를 대조해 중복 통합·검증하지 않는다. g7-t4는 첫 인사 뒤 디스크 오류로 종료했고 report가 없다. 기존 로그와 미수용 사본을 보존하며 새 서비스의 interrupted 처리와 새task ID를 이용해 필요한 잔여만 배정한다. g45-final/pr-base-ports/pr-base-tests의 미시작 배정은 실제 선행을 확인해 이어간다.

## 보존·복원 규약

공식 workspaces.py cleanup-accepted를 사용해 수용·종료·통합된 작업만 보존 후 정리한다. baseline.json/result.json과 objects의 내용별 저장소가 두 판본을 보존하며 archive.json은 보고/통합기록의 해시를 연결한다. reports/evidence/session.log/objective/inputs와 미수용 작업은 보존한다. cleanup.json이 있는 작업의 과거 workspace/base 경로는 영구 입력이 아니다.

후속 task와 manager는 새 protocol/README/principles를 먼저 읽는다. 과거 입력이 workspace/base 절대경로를 참조하더라도 없는 디렉터리를 증거 소실로 단정하거나 전체 사본을 다시 만들지 않는다. 보존된 report/evidence/integration부터 읽고, 실제 과거 코드가 필요한 경우에만 공식 restore로 해당파일/디렉터리만 별도의 짧은 임시경로에 복원한다. 예: `python C:/math/services/async-development/workspaces.py restore C:/math/.async/dm TASK result NEW_DIRECTORY .claude/skills/do-math/scripts/do_math/core_engine.py`. baseline판은 result 대신 baseline을 사용한다. 관리 task의 base/workspace 원래위치에 복원하지 않는다. 새 task는 baseline.json+objects를 시작판으로 쓰고 base디렉터리가 없다.

## 다음 판단

원래 사용자 목표·G4~G8·모델(worker gpt-6.1-sol/high, manager gpt-6-astra/xhigh)·max_workers10과 저장 A22 범위 교정은 유지한다. 반복되는 전체검증·과거증거 재읽기를 절차상 이유로 추가하지 않는다. 최신 코드의 실제 보존·통합·정리 절차를 사용하고 원자료는 필요한 범위만 읽는다. 새 서비스 코드 변경은 운영자 준비이며 do-math 제품 결과로 귀속하지 않는다. 정리 결과와 공간은 runtime/cleanup-2026-10-16-*에 기록한다.

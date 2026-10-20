# do-math 비동기 개발 실행

## 2026-10-20 작업트리 정리와 보존 범위

현재 queue의 상태는 외부 조건 대기 `blocked`다. `managers/0108/review.md`와 `tasks/g8-review/report.json`이 최종 검토·제품 인도와 미충족 조건의 추적 진입점이다. 작업트리 정리·커밋은 개발 목표 완료나 서비스 재기동을 뜻하지 않는다.

Git에는 실행 설정·시작 스크립트·공용 맥락·계획·사용자 지시와 각 task의 objective/task/report/integration, manager의 review를 보존한다. `objects/`, task의 base/workspace 및 실행·복원 목록과 큰 evidence, session 로그, manager의 중간 자료는 로컬 보관한다. 과거에 이미 추적한 선별 evidence는 계속 추적한다. `.gitignore`는 이 구분을 구현하며 원자료를 삭제하지 않는다. Git clone만으로 로컬 실행을 그대로 재개하거나 과거 전체 파일을 restore할 수 있다는 뜻은 아니다. 다른 장치로 이관하려면 해당 실행 디렉터리의 objects·baseline/result/archive·evidence·state를 별도로 백업해야 한다.

보관 해시를 확인한 수용 task의 잔여 workspace/base만 삭제했다. 중단·취소됐지만 미수용인 작업의 사본은 검수되지 않은 내용이 있을 수 있어 유지한다. 정리 세부는 `sources/working-tree-cleanup-2026-10-20.json`에, 개별 삭제 경로·보관 근거는 로컬 `runtime/working-tree-cleanup-2026-10-20-deletions.json`에 있다.


서비스: `C:/math/services/async-development` · 공용소스: `C:/math` · 기록: `C:/math/.async/dm`.

2026-10-15 사용자가 기존 개발을 중지하고 async-development로 재개하라고 지시했다. 이전029 manager를 중지한 뒤 첫 async manager0001이 남은 이관 검수를 완료했다. 현재 소스와 원검사 판본을 대조해 지정 여덟 발견을 수용하고 r02/r07/r18의 독립 조사를 준비했다. 원task·원로그·draft를 보존했으며 완료된 task의 제품 검사는 다시 실행하지 않았다. 상세 인계는 context.md, plan.md, sources/migration.json과 sources/legacy 원문에 있다.

시작/중단 후 재개: `& C:/math/.async/dm/start.ps1`. 이 스크립트는 queue를 검사하고 공식 `services/async-development/run.py C:/math C:/math/.async/dm`을 숨긴 프로세스로 시작한다. 모델은 settings.json과 task 배정에 따르며 worker gpt-6.1-sol/high, manager gpt-6-astra/xhigh다. max_workers는10이다. 동일 기록의 중복 실행은 서비스 lock이 거부한다.

진행 정본은 state.json과 queue.json이다. 실제 manager는 managers/번호/session.log, worker는 tasks/ID/session.log에 기록된다. runtime/launch-*.json은 기동 이력이며 PID만으로 생존을 단정하지 않는다. 이전 continuous-development의 launch/model-change 상태는 과거 기록이다.

Git ceiling을 tasks 디렉터리로 두어 Git메타데이터 없는 workspace가 상위 공용 저장소를 자기 repo로 인식하지 않도록 한다. 과거 이력은 명시적으로 source_repo에서 읽고, 제품 검사는 workspace에서 한다. 독립 코드 사본 생성과 충돌 검사 통합은 서비스가 수행한다. large docs/evidence/toolchain은 snapshot에 넣지 않고 절대경로로 필요한 원문만 읽는다. 현재 snapshot은2681파일 약220MiB이며 task마다base와workspace가 만들어진다.

manager가실패하면서비스는기존worker종료뒤오류로멈추고사건을보존한다. 같은명령으로재개한다. 재개시살아있는세션을복제하지않으며 state를수기로고치거나기존task폴더를지워재실행하지않는다. 자세한규약은서비스README/protocol/principles를따른다.

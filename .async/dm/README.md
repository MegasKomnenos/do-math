# do-math 비동기 개발 실행

서비스: `C:/math/services/async-development` · 공용소스: `C:/math` · 기록: `C:/math/.async/dm`.

2026-10-15 사용자가 기존 개발을 중지하고 async-development로 재개하라고 지시했다. 이전029 manager를 중지한 뒤 첫 async manager0001이 남은 이관 검수를 완료했다. 현재 소스와 원검사 판본을 대조해 지정 여덟 발견을 수용하고 r02/r07/r18의 독립 조사를 준비했다. 원task·원로그·draft를 보존했으며 완료된 task의 제품 검사는 다시 실행하지 않았다. 상세 인계는 context.md, plan.md, sources/migration.json과 sources/legacy 원문에 있다.

시작/중단 후 재개: `& C:/math/.async/dm/start.ps1`. 이 스크립트는 queue를 검사하고 공식 `services/async-development/run.py C:/math C:/math/.async/dm`을 숨긴 프로세스로 시작한다. 모델은 settings.json과 task 배정에 따르며 worker gpt-6.1-sol/high, manager gpt-6-astra/xhigh다. max_workers는3이다. 동일 기록의 중복 실행은 서비스 lock이 거부한다.

진행 정본은 state.json과 queue.json이다. 실제 manager는 managers/번호/session.log, worker는 tasks/ID/session.log에 기록된다. runtime/launch-*.json은 기동 이력이며 PID만으로 생존을 단정하지 않는다. 이전 continuous-development의 launch/model-change 상태는 과거 기록이다.

Git ceiling을 tasks 디렉터리로 두어 Git메타데이터 없는 workspace가 상위 공용 저장소를 자기 repo로 인식하지 않도록 한다. 과거 이력은 명시적으로 source_repo에서 읽고, 제품 검사는 workspace에서 한다. 독립 코드 사본 생성과 충돌 검사 통합은 서비스가 수행한다. large docs/evidence/toolchain은 snapshot에 넣지 않고 절대경로로 필요한 원문만 읽는다. 현재 snapshot은2681파일 약220MiB이며 task마다base와workspace가 만들어진다.

manager가실패하면서비스는기존worker종료뒤오류로멈추고사건을보존한다. 같은명령으로재개한다. 재개시살아있는세션을복제하지않으며 state를수기로고치거나기존task폴더를지워재실행하지않는다. 자세한규약은서비스README/protocol/principles를따른다.

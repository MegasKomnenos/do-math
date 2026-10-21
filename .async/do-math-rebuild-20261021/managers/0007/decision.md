# manager 0007 판단

## 받은 결과와 수용

inbox의 완료 사건은 skill-entry 하나이며 실행 중 task는 없다. report.json, objective.md, verification.md를 읽고 새 SKILL.md 본문 및 base 대비 plan.md/RUNTIME.md diff를 검토했다. 사용자 원문의 목적·재량·독립 기동·운영 요구에서 제품 본문으로 누락을 대조하고, SKILL→RUNTIME/protocol/common→runner.py의 실제 정의로 동작을 대조했다.

SKILL에는 사용자가 정하는 목표·조건·허가와 AI의 방법 선택, 환경을 그대로 사용하는 설정, 인스턴스 자체 Git, init/start/status 및 새 PID·로그 확인 후 위치 반환, 공개 해설·검토·목표 판정 읽기가 있다. STOP·입력·공급자 한도·완료를 구분하며 개별 CLI 종료와 재기동 뒤 남은 산출 처리도 설명한다. 예시 경로·모델은 호스트의 보장값으로 고정하지 않는다. 이 내용을 runner의 initialize/load_settings/start/status/main, Runner.dispatch/enqueue/apply_output/ingest_inputs/tick/run과 대조했다. 새 형식·승인 단계·실행 코드 변경은 없다.

계획 문서 보완은 pending/assigned 요청의 task·origin·상태 읽기와 session_failed.session→sessions.request→requests.task/origin을 구체화한다. request:null인 실패 계획은 해당 input.json.task.events로 원 사건을 회수한다. Runner.dispatch의 계획 전용 RUNTIME/state 안내와 enqueue/apply_output의 키·필드에 맞는다. 검토 기동 입력에는 작성자 폴더·로그 경로를 추가하지 않는다. 이는 전달 경로 확인이며 OS 파일 읽기 격리의 보장이 아니다.

`python services/async-development/workspaces.py integrate C:/math C:/math/.async/do-math-rebuild-20261021 skill-entry`가 성공했다. SKILL.md, plan.md, RUNTIME.md 세 파일을 공용 소스에 반영했고 integration.json에 기록됐다. skill-entry를 수용한다.

## 확인의 한계와 다음 작업

이번 판단은 문서와 관련 구현의 정적 대조다. task가 보고한 링크·LF·명령 AST 확인과 report 검사를 반복하지 않았으며 실제 모델·Lean·독립 기동을 새로 실행하지 않았다. 실제 두 공급자의 파일 산출과 무인 완주는 아직 완료 근거가 없다.

기존 mixed-completion objective는 수용된 SKILL 진입부터 실제 Codex·Claude 혼합 인스턴스의 작은 Lean 목표 완주, 공개 해설·독립 검토·목표 achieved·Git 기록 확인과 직접 관련 결함 수정을 이미 포함한다. 배정과 objective를 그대로 유지한다. skill-entry 수용으로 이 task가 파견 가능해진다. 다른 독립 후속 기능은 없고 최종 review는 혼합 완주 및 필요한 수정을 수용한 뒤 준비한다.

공용 context.md/plan.md/seams.md를 현재 수용 상태와 읽기 경로로 갱신했다. queue는 accepted에 skill-entry만 추가한 임시 파일을 검사하고 원자 교체해 게시한다. 제품 코드를 manager가 직접 수정하거나 그래프 갱신·Codex 사본 복사를 수행하지 않았다.

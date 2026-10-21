# 사용자 대화의 do-math 진입점과 문서 연결

## 맡은 결과

개발 대화를 모르는 Claude Code·Codex 대화 세션이 SKILL.md를 읽고 새 연구를 준비해 독립 실행기를 띄운 뒤 사용자에게 위치를 전달하고 끝낼 수 있게 한다. 같은 진입점에서 진행 조회, 정지와 해제, 사용자 입력, 멈춘 세션 하나 종료, 실행기 재기동을 수행할 수 있어야 한다. 수용된 실행기와 작업맥락 문서의 작은 연결 보완도 이 task에서 함께 마친다.

`inputs/context.md`, `inputs/plan.md`, `inputs/seams.md`, task.json을 먼저 읽는다. 자기 workspace의 `.claude/skills/do-math/runner.py`, RUNTIME.md, CLI.md, protocol.md, common.md, plan.md, research.md, review.md와 check.py가 제품 근거다. 사용자 확정 요구는 `C:/math/.async/do-math-rebuild-20261021/user-messages.md`다. `tasks/session-contexts/verification.md`의 연결 조건은 위 records 아래에 있다. runner와 session-contexts가 수용된 뒤 시작하므로 실제 실행기 계약을 소비한다. 이전 do-math와 Git 이력은 설계 자료로 사용하지 않는다.

## 작성과 연결

1. `.claude/skills/do-math/SKILL.md`를 스킬 진입 문서로 작성한다. 스킬을 찾을 이름과 설명, 연구 목적·사용 시점, 사용자가 정할 목표·필수조건·허가와 AI가 정할 방법의 경계를 전달한다. 의미 있는 기본 선택을 스스로 할 수 있는 일에 별도 확인 단계를 만들지 않는다.
2. 실제 runner 명령과 입력 파일에 맞춘 새 연구 시작 경로를 제시한다. 목표·조건과 settings, 범주별 모델·노력과 공급자 접두, 실제 CLI 경로, Lean command/version_command/cwd/env, 자체 Git을 가진 인스턴스 위치를 연결한다. 예시와 실제 사용 경로를 구분하고 사용 가능한 설치를 그때 사용한다. 인스턴스 Git과 저장소 본체가 섞이지 않게 한다. 긴 설정 정의는 protocol·RUNTIME·CLI에 연결하되 사용자가 첫 연구를 시작하는 데 필요한 의미를 본문에서 생략하지 않는다.
3. Windows 무창 독립 기동/재기동의 실제 명령, PID와 새 기동 기록 확인, 인스턴스 위치를 반환하고 대화가 끝나는 순서를 안내한다. 기동 대화가 연구를 계속 기다려야 하는 운영으로 만들지 않는다. 종료된 실행기를 사람이 다시 띄우는 방식과 남은 세션 처리 의미를 설명한다.
4. 상태·공개 결과·독립 검토·목표 판정 읽기, STOP 설정/해제, 사용자 입력과 외부 입력 대기 해제, 멈춘 세션 하나의 식별·종료를 실제 명령 및 필요한 후속 행동으로 안내한다. STOP은 새 파견만 막고 개별 세션 종료와 다르다. 공급자 한도 대기의 해제 시각 또는 fallback, 완료 후 새 파견 중단과 기존 산출 처리 의미를 보존한다. 종료 방식에 관계없이 공식 재검사로 결과를 판단한다는 의미도 전달한다.
5. runner의 입력·기동 프롬프트에서 common/protocol/goal과 해당 범주 문서, 자기 세션 폴더·input.json·공식 검사 명령을 찾는 경로를 확인한다. 계획이 이미 게시한 미파견·실행 중 요청의 지시·대체 대상·상태 및 실패 session의 원 요청을 실제 상태/공개 계획에서 찾을 수 있는지 따라 읽는다. 원 요청 식별 의미는 계획 기록 ID+배열 이름+인덱스다. 검토자는 공개 knowledge와 target으로 판단하며 작성자 폴더·로그가 기동 입력에 포함되지 않아야 한다. 실제 코드가 제공하는 읽기 경로에 맞춰 common/plan/research/review/RUNTIME 문서의 필요한 문구·링크를 보완한다. 이 조건을 코드가 제공하지 않으면 정확한 파일·심볼과 영향·최소 수정안을 report에 남긴다.

## 범위와 확인

쓰기 범위는 SKILL.md 및 연결 보완에 필요한 common.md, plan.md, research.md, review.md, RUNTIME.md 여섯 파일이다. 이미 충분한 문서를 다시 쓰거나 새 규칙·스키마·승인 단계를 추가할 필요는 없다. 실행기·검사기·CLI 코드 변경, 그래프 갱신, `.agents/skills/do-math/` 복사는 이 task 범위 밖이다. 실제 혼합 모델 완주도 후속 task가 맡는다.

문서 확인은 SKILL 진입→설정·인스턴스→실제 기동·운영 명령→상태·공개 지식 경로로 읽고 runner의 argparse/관련 함수와 대조하면 충분하다. 작업맥락은 기동 입력→공통·범주 문서→task·지식·요청 상태→산출·공식 검사로 읽는다. 사용자 원문과 공용 context의 중요한 요구가 제품 본문에서 회수되는지 먼저 대조하고, 문서가 말하는 명령·필드·동작이 실제 구현과 맞는지 확인한다. 링크 존재만으로 내용 전달을 판정하지 않는다. 실행이 필요한 불확실성이 있으면 해당 명령의 가장 작은 확인만 하고 실제 모델을 기동하거나 기존 가짜 시험 전체를 반복할 필요는 없다.

report.json에는 제공한 읽기 경로, 수정 이유, 실제 확인과 미확인 범위, 실제 혼합 완주에 사용할 진입 명령 및 남은 결함을 기록한다. `python C:/math/services/async-development/check.py report C:/math/.async/do-math-rebuild-20261021 skill-entry`로 보고와 변경 범위를 검사한다.

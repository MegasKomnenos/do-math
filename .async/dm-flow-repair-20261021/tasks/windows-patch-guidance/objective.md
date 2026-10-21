# Windows 명령과 중복 패치 오류의 실제 작업자 안내 수리

context.md R6, R7.1의 관련 문서 수리와 필요한 확인을 한 작업에서 완료한다. `C:\math\.skill-workspace\parking-unimodality-20261021\audit\subcommand-failures.json`, shell-quoting-reproduction.json과 실패 실행의 실제 도구 요청/반환을 읽기 전용으로 대조한다. cmd 따옴표 실패 5건과 한 패치의 같은 파일 중복 대상 거부 2건의 실제 경계·사용 도구 계약을 확인한다. 다른 도구의 패치 문법을 이 오류의 계약처럼 추측하지 않는다.

정본 AGENTS.md, SKILL.md 역할 읽기 대응표와 `contracts.reading_map/prompt_documents`를 읽는다. `references/공통-실행.md`는 현행 common 지급 문서이므로 그 안의 실제 명령 작성 문맥에 명확한 예시를 넣는 것을 첫 선택으로 삼는다. 현재 이미 충분한 경로가 있으면 새 필수 문서/입력 필드를 추가하지 않는다. 관련 역할 계약의 일반 책임 개정은 후속 R1 구현이 맡으므로 이 작업은 공통 실행 안내에 집중한다.

PowerShell `Get-Content -LiteralPath '공백 있는 경로'`, 실행파일 호출 연산자 `&`, 공백 있는 실행파일/스크립트 경로의 분리된 인수, cmd가 실제 shell인 경우의 올바른 표기를 무해한 파일 읽기 또는 Python version 호출로 확인한다. PowerShell 문자열, cmd 문법, JSON의 wire escape를 섞지 않는다. 잘못된 `\"`를 shell 자체에 전달하는 형태와 올바른 도구 입력에서 JSON을 해석한 후 전달되는 실제 명령의 관계를 설명한다.

확인한 패치 도구의 실제 계약에 맞게 같은 파일 변경을 한 파일 작업과 여러 hunk로 합치는 예시, 거부 후 적용 여부를 확인하고 올바른 요청으로 다시 제출하는 수리 절차를 제공한다. 사용자 파일을 바꾸는 확인은 하지 않고 자기 task 전용 임시 파일만 쓴다. 이번 안내의 적절성을 확인하는 작은 파일 예시 외에 제품과 같은 시험을 새로 복제하지 않는다.

완료 근거에는 `prompt_documents` 또는 실제 역할 입력 생산자를 통해 역할에게 추가한 안내가 도달한다는 확인을 포함한다. 단지 문서 경로가 존재한다는 확인으로 대체하지 않는다. 무해한 shell 호출 명령·실제 출력·도구 계약 근거·확인하지 못한 경계를 task evidence와 `docs/do-math/flow-repair-20261021/windows-patch-guidance.md`에 남긴다. 모든 역할이 안내를 실제로 준수한다는 주장으로 확대하지 않는다.

허용된 정본 문서와 안내 관련 기존 구조/읽기 시험만 변경한다. 시험이 필요하면 한 프로세스의 관련 선택 범위로 끝낸다. 공식 writing-skills SKILL.md와 미러 생성기를 읽고 Codex 사본을 생성한다. 다른 스킬/.agents/diff는 변경 대상에 포함하지 않는다. report.json을 실제 변경과 맞추고 서비스 report 검사로 확인한다. 원 연구/HOLD/예약과 graphify는 변경하지 않는다.

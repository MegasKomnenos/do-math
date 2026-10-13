## 목적과 역할

G7의 공식 T5 진입점에 공급자 최소 실호출을 연결한다. phase 001에서 smoke/test_*.py가 0개이고 Codex 설치판 0.162.1과 녹화판 0.160.0이 다름을 확인했다. 기존 probe_cli의 protocol_probe는 파일·종료 경계의 유효한 부분 증거이지만 원문 설계 5.5의 실제 역할 schema 호출을 대신하지 않는다. 정상 기준 수리 phase 002 뒤, 문서 수리를 길게 진행하기 전에 실제 모델 접근·역할 스키마 수락·녹화의 조건을 확인한다.

이 task는 Codex/Claude 최소 스모크 구현, 실제 호출과 관련 말뭉치·재생·미러까지 맡는다. 제품 연구를 재개하거나 모델 답의 수학 품질을 평가하는 작업이 아니다. Job/pythonw 전용 연쇄, Lean/Mathlib, 예약 등록·발화·해제, 학술 MCP list_sources, 운전 문서 읽기 한도 L01은 후속 task다. 이번 T5 선택의 통과만으로 T5 전체 요구나 G7 전체를 완료로 표시하지 않는다.

선행 입력은 gate-readiness.json의 G7-T5/environment_readiness/corpus_reuse, population-and-corpus.json의 corpus와 실제 정본이다. 과거 재검토는 prior-review-state.json의 PR15 중 B86(provider_corpus_integration), B87(background_probe_contract)의 공급자 녹화·background slice만 이번 구현에 결합한다. 전체 PR15나 B89의 비공급자 경계를 선행 과제로 넓히지 않는다.

## 완료 조건

### A1 공식 T5에서 명시적인 공급자 최소 스모크를 실행

`scripts/tests/smoke/`에 공급자별 실제 시험을 두고 `run_tests.py --tier T5 --list`가 둘 다 선택함을 확인한다. 실제 `ModelRunner.run`과 `real_ports(environment=...)`의 작업자·Job·현재 provider adapter·현재 수신 parser를 사용한다. 제품 중간 경로를 scripted CLI, mock ModelRunner 또는 수동 보고 dict로 교체하지 않는다. 격리는 기존 `test_categories.test_group('resource')` 등 현 공식 규칙을 따른다.

시험의 역할 schema는 `contracts.action_schema({'role': 'maintenance'})`의 현재 실제 결과를 사용한다. 이 보통 maintenance 분기가 core_engine.CoreEngineMixin._response_schema에서 어떻게 반환되는지 원문과 대조하고 실제로 건넨 schema와 해시를 기록한다. integration_bundles 등 선택 필드를 포함한 schema를 공급자 수락을 위해 삭제·축소하지 않는다. 새로운 protocol_probe 복제품이나 독립 schema 사본을 만들지 않는다. 이 호출은 역할 schema의 대표 경계이며 연구 control_binding·중앙 제출·저장까지 수행했다고 보고하지 않는다.

모델·effort·호스트·CLI 경로와 판본을 실행 입력으로 명시하고, 현재 설치된 비밀 아닌 설정 필드/CLI 관찰로 선택 근거를 보존한다. 설치판·모델 ID를 이 문서의 역사 숫자로 고정하거나 임의 ID를 발명하지 않는다. 호출할 수 없는 모델·인증·구성이면 진단 가능한 실패로 남기며 빈 선택, skip, 자동 대역 전환을 통과로 쓰지 않는다. 설정 전달 방법은 구현자가 정하되 개인 절대 경로나 인증 값을 제품 시험/지침에 고정하지 않는다. 새 옵션 프레임워크 대신 작은 명시 입력과 기존 실행기를 사용한다.

### A2 두 공급자의 현재 실제 역할 호출과 파일·종료 증거

공급자별로 기본 1회씩 짧은 실제 호출을 수행한다. 새 시험 전용 scratch에서 nonce 파일 쓰기·다시 읽기와 유효한 checkpoint를 요청하고, 같은 호출이 maintenance schema의 유효한 structured output을 반환하도록 한다. 실제 반환·파일 내용·checkpoint 해석·native event·선택된 최종 응답과 local termination barrier를 함께 대조한다. 현재 `observations.read_checkpoint` 등 실제 소비 규칙을 사용하며 문자열 존재만으로 통과하지 않는다.

CLI 경로/판본, 설정한 model/effort와 보고된 model(제공되는 경우), prompt/schema hash, 시작·종료·PID/worker 원자료, raw stdout/stderr/final, 실제 파서 결과와 개별 판정을 보존한다. 과금·호출 횟수는 실제 시도 전부를 세고 준비 오류/실패도 버리지 않는다. 인증 토큰·키·전체 환경을 출력/커밋하지 않는다. 실제 역할 schema가 거부되거나 외부 조건이 없으면 A2는 fail 또는 not_run이고 status는 partial/blocked다. 독립적으로 가능한 구현·재생·근거 보존은 완료하고 필요한 외부 결정/제품 수리 위치를 finding으로 반환한다.

### A3 현 판본 녹화와 기존 재생 계약 연결

성공·실패를 구별한 현재 공급자 원출력을 tests/corpus의 해당 provider 디렉터리에 추가하고 manifest의 판본·일시·command·role·source·source_sha256·verdict·부속 recording 경로를 실제 바이트에 결속한다. 설치판이 같더라도 새 역할 schema 결과와 기존 protocol_probe의 성질을 구별한다. 과거 실패 녹화의 verdict를 성공으로 바꾸거나 역사 원바이트를 덮어쓰지 않는다. current command-surface 녹화는 실제 adapter가 선언한 version/help 관찰과 연결해 현재판으로 맞추고, 갱신 전후 형식 차이와 parser 지원 여부를 기록한다.

structure.test_corpus와 unit.test_corpus_replay의 전 항목 순회, contracts.test_doubles_follow_corpus의 실제 parser/대역 비교를 통과한다. 새 성공 응답의 최종 선택·구조가 현재 parser에서 동일하게 확인되는지 명시한다. fixture를 현재 실패에 맞춰 느슨하게 바꾸지 않는다. 5MB 말뭉치 상한과 기존 비공급자 항목을 유지한다. 큰 raw를 줄여야 하면 완전 원자료를 자기 evidence에 보존하고 발췌 좌표/해시/제외 범위를 명시한다. 절단된 stream으로 전체 종료 성공을 주장하지 않는다. 검사 중 corpus 정본을 수정하지 않고 녹화는 먼저 evidence에 받은 뒤 검사 사이에 승격한다.

### A4 Claude background와 관련 과거 변경의 한정 판정

기존 claude-background-completed-21289 원자료를 `probe_cli.background_completed_before_result`의 현재 identity(task_id/tool_use_id)·start/completion/result 순서와 대조한다. B87의 actual_wait_tool 과거 요구와 현재 native completion 계약을 구별하고 현재 파일·종료 근거까지 충분한지 판정한다. 충분하면 해당 성질만 재사용하고, 부족하면 A2와 합치거나 공급자당 1~2회 범위의 추가 실제 호출로 필요한 원자료를 얻는다. 사건 이름 존재만으로 성공 처리하지 않는다. timeout이나 별도 모델/agent를 도입하지 않는다.

PR15/B86/B87의 실제 도입 diff(필요하면 git log -S로 위치 확인), 현재 직접 소비자, 원보고를 읽어 유지/교정/미검토 범위를 보고한다. 없는 임시 원보고의 counts는 역사 주장으로 남기며 현재 작은 재현으로 대체한 성질을 구별한다. upstream 제품 결함이 이번 writes 밖이면 우회하거나 부수 수리하지 말고 정확한 다음 조치를 반환한다.

### A5 검증과 인도 범위 일치

최종 스모크 선택/실제 row/exit와 소스 불변을 보존하고, 관련 offline 재생 및 새 시험의 구조 검사를 완결한다. live 녹화를 위해 이미 수행한 유효한 실호출을 새 변경 없이 반복하지 않는다. 최종 live 이후 관련 제품·시험이 바뀌면 어느 근거가 무효화됐는지 판단하고 필요한 호출만 다시 수행한다. 단순 corpus 승격/문서 변경과 호출 경로 변경을 구별한다.

시험 지침에 실제 실행 입력·호출 비용·출력 위치·대표 역할 범위·미완료 외부 연쇄를 적는다. 정본/미러를 공식 생성기로 맞추고 `--check`와 `probe_cli.py --skill-only`를 통과한다. report는 A1~A5, 실제 호출 횟수·각 결과·남은 G7 조건과 다음 수리/외부 결정의 책임을 연결한다. 전체 일반/fresh T3/전체 함수 변이/T4 전체 및 G7 전체 완료를 주장하지 않는다.

## 판단과 경계

프로젝트 writes는 phase.json을 따른다. 이 phase는 smoke와 필요한 작은 시험 보조, 공급자 corpus/재생, 지침만 수정한다. ModelRunner/worker/adapter/parser/역할 schema 제품 코드는 읽어 사용하며 수정하지 않는다. 제품 결함이 발견되면 원자료와 실패 경로를 반환하고 manager가 별도 수리를 배정한다. probe_cli의 기존 files/background 함수를 재사용할 수 있지만 이번 작업을 위해 기존 제품 프로브의 의미를 바꾸지 않는다. 새 smoke에 중복된 프로세스 수명 관리나 schema 변환기를 만들지 않는다.

테스트 scratch는 자기 evidence 또는 공식 runner가 소유한 scratch 안에 둔다. 기존 연구 인스턴스의 시작·재개·삭제, OS 예약 변경, 패키지 설치/업데이트, 인증/전역 모델 설정 변경을 이 작업에 넣지 않는다. 필요한 기존 설정 읽기는 비밀 아닌 최소 필드만 추출한다. 현재 모델 접근이 불확실하면 가능한 조건을 확인하고 정확한 question/issue를 남긴다. 원문 요구를 축소해서 성공을 만들지 않는다.

검사 묶음은 순차, 합계 worker는 3 이하이며 실제 모델/자식 프로세스가 있으므로 이번 공식 실행은 `--jobs 1`이다. 모든 정상 기다림에는 timeout을 재도입하지 않는다. 관찰 도구의 yield와 실제 종료를 구별하고 긴 실행의 PID·시작·종료·중간 원자료를 자기 evidence에 남긴다. 실호출의 공급자당 1~2회는 정상 준비의 호출 범위다. 준비 오류/결함으로 더 필요하면 무한 재시도하지 말고 기존 실패와 정확한 재실행 필요를 보고한다.

정본은 .claude/skills/do-math이고 .agents 사본은 공식 생성물이다. 생성 전 영향 범위와 dirty 상태를 확인하고 허용 대응 파일 외의 drift를 덮어쓰지 않는다. tests/.timings.json 두 사본은 실행 보조 파일로 허용한다. .selection-index·pseudo_tested·engine·공용 문서·과거 task report/evidence는 수정하지 않는다. Git commit/reset/checkout/push와 graphify 갱신은 수행하지 않는다.

## 검증 방법

cwd는 `C:\math`, Python은 `C:\Users\wogud\AppData\Local\Programs\Python\Python312\python.exe`다. 최초/최종 입력 해시와 각 실행의 실제 argv·비밀 아닌 지정 환경·시각·PID·stdout/stderr·exit를 evidence에 보존한다. 각 재시도는 새 출력 디렉터리를 사용한다.

1. phase 001의 corpus/환경 관찰을 실제 현재 코드·파일과 대조한다. `--tier T5 --list`의 시작 시 빈 선택과 구현 후 선택을 확인하며 시작의 empty exit를 모델 실패로 세지 않는다. 실제 역할 schema와 선택한 모델의 근거를 먼저 확정한다.
2. 모델을 호출하지 않는 준비 검증과 필요한 작은 harness 입력 검증을 먼저 수행한다. live trial은 `& 'C:\Users\wogud\AppData\Local\Programs\Python\Python312\python.exe' -u -B .claude/skills/do-math/scripts/run_tests.py --tier T5 --jobs 1 --output docs/do-math/continuous-development-2026-10-13/phases/003/tasks/provider-smoke/evidence/live-01`로 수행한다. task가 문서화한 모델 입력을 같은 실행 환경에 지정한다. live 실행 중 corpus 파일은 쓰지 않는다.
3. 종료 후 selected와 실제 reports[].rows의 공급자별 대응, 성공·실패·skip·미실행·fixture 오류·termination을 확인한다. runner의 successful만으로 외부 성공을 선언하지 않는다. 성공/실패 raw를 보존하고 해당 provider 녹화를 승격한다. Claude background 재사용 판단 또는 필요한 추가 실제 호출도 같은 자료 좌표와 연결한다.
4. 승격한 최종 판본에서 공식 `run_tests.py structure.test_corpus unit.test_corpus_replay contracts.test_doubles_follow_corpus structure.test_test_smells --jobs 1 --output <새 evidence 경로>`를 수행한다. 새 offline 시험을 추가했다면 그 모듈도 포함한다. 관련 기존 parser/CLI 시험은 변경·실패 이유가 있을 때만 추가한다. 전체 T3나 전체 일반을 여기서 실행하지 않는다.
5. 영향이 허용 범위 안임을 확인하고 `build_skill_mirrors.py`, `build_skill_mirrors.py --check`, `probe_cli.py --skill-only`를 같은 Python으로 순차 실행한다. report를 작성하고 `services/continuous-development/check.py report C:\math C:\math\docs\do-math\continuous-development-2026-10-13 003 provider-smoke`를 통과한다. 외부 조건 때문에 일부 A가 충족되지 않으면 유효한 결과를 보존한 partial/blocked 제출로 종료한다.

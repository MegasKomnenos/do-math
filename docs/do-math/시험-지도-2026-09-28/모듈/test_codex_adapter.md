# test_codex_adapter

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_codex_adapter.py` (226행) |
| 클래스 / 테스트 | 1 / 15 |
| 시험 대상 제품 코드 | `do_math/codex_worker.py`의 `build_argv`, `load_request`, `run`, `sanitized_environment`, `main`; `do_math/claude_worker.py`의 직접 실행 머리; `do_math/cli_worker.py`의 `check_common_request`, `run_cli`, `allowed_environment`, `validate_max_runtime`; `do_math/codex_adapter.py`의 `_parse_jsonl`, `CodexExecAdapter.describe`, `LocalCLIAdapter.collect`, `start`, `CLIExecution`; `do_math/file_io.py`의 `strict_json_loads`; `do_math/windows_job.py`의 `JobInspection` |
| 사용하는 픽스처 모듈 | `provider_fixtures.FakeJob` |
| 격리 표지 | 없음 |
| 시작 상태 | 1단(작업자 요청 검사, 인자 빌더, 파서, 수집기 직접 호출). 두 시험은 실제 Python 자식 프로세스를 띄운다. 수집 시험은 `FakeJob`이 고정 Job 관찰을 돌려주고, 출력 파일은 임시 폴더에 직접 쓴다 |

## 목적

모듈 docstring은 없다. 시험 대상 `codex_adapter.py`의 docstring은 다음과 같다. "Local CLI adapters: the lifetime base every provider shares, and ``codex exec``." Codex CLI에는 문서화된 공급자 응답 식별자, 원격 취소, 호출별 사용량 표면이 없으므로 어댑터는 그것들을 알 수 없음으로 기록한다. `codex_worker.py`의 docstring은 "Execute one ``codex exec`` request without a shell or API-key fallback."이다. 이 모듈은 Codex 작업자와 공통 수집기 경계의 계약을 본다.

- 작업자는 셸 없이 문서화된 비대화형 플래그만으로 CLI를 부른다. 요청은 엄격히 검사하고, 로그인 상태만 남긴 환경을 쓰며, MCP는 scholarly만 명시한다.
- 명령 표면 점검은 작업자가 쓰는 플래그를 모두 요구한다.
- 작업자 모듈은 Job 안에서 직접 실행되는 루트로 import할 수 있어야 한다.
- JSONL 파서는 모호하거나 비유한인 사건으로 완료를 세우지 않는다.
- 수집기는 종료 장벽이 확인된 뒤에만 산출물을 읽고, 시작 때의 스냅숏 바이트를 쓴다.
- 시작은 이미 있는 출력 파일을 거부한다.

## 모듈 수준 요소

- 행 12 `SCRIPTS`: 스킬의 `scripts/` 폴더(`Path(__file__).resolve().parents[1]`).
- 행 13: `SCRIPTS`를 `sys.path` 앞에 넣는다. 조건 없이 넣으므로 이미 있어도 한 번 더 들어간다.
- 행 226: 직접 실행하면 `unittest.main()`을 부른다.

## CodexWorkerTests (행 20–223)

`unittest.TestCase`를 그대로 상속한다. 표지, 클래스 속성, 훅, 도우미가 없다.

### `test_build_argv_is_direct_cli_with_isolating_probe_flags` (행 21–32)
- 성질: Codex 작업자의 명령은 CLI를 직접 부르고, 사용자 설정·규칙·저장소 점검·프로젝트 문서를 무시하는 격리 플래그를 달며, 프롬프트를 표준 입력(`-`)으로 받는다.
- 준비: `windows_sandbox="unelevated"`를 포함한 완전한 요청 사전(`C:/Codex/codex.exe`, `gpt-x`, `high`, `read-only`, `never`).
- 실행: `codex_worker.build_argv(request)`.
- 단언: 앞 네 인자가 `["C:/Codex/codex.exe", "--ask-for-approval", "never", "exec"]`다. `--json`, `--ephemeral`, `--ignore-user-config`, `--ignore-rules`, `--skip-git-repo-check`, `project_doc_max_bytes=0`, `windows.sandbox="unelevated"`가 인자에 있다. 마지막 인자가 `"-"`다. 인자를 이어 붙인 소문자 문자열에 `shell`이 없다.
- 대역: 없음.
- 비고: 이름의 "probe"는 이 시험에서 직접 단언되지 않는다. `shell`이 없다는 단언은 셸 경유 실행 흔적이 인자에 없다는 뜻이다.

### `test_surface_requires_the_flags_used_by_the_worker` (행 34–48)
- 성질: 명령 표면 점검(`describe`)은 `exec --help` 출력에 작업자가 쓰는 플래그가 모두 있을 때만 검증됨으로 판정한다.
- 준비: 필요한 플래그 13개. `--json`, `--output-last-message`, `--model`, `--sandbox`, `--ephemeral`, `--ignore-user-config`, `--ignore-rules`, `--skip-git-repo-check`, `--output-schema`, `--config`, `--strict-config`, `--color`, `--cd`다. `subTest(missing=...)` 네 경우에서 빠뜨릴 플래그는 없음, `--strict-config`, `--color`, `--cd`다. 가짜 `subprocess.run` 결과 셋은 차례로 버전, `--help`(`--ask-for-approval`), `exec --help`(빠진 플래그를 뺀 나머지)다.
- 실행: `CodexExecAdapter("fixture-cli").describe()`.
- 단언: `description["verified"]`가 `missing is None`과 같다.
- 대역: `patch("do_math.codex_adapter.subprocess.run", side_effect=results)`, `patch.object(adapter, "capability_identity", return_value={"fixture": True})`.
- 비고: 제품의 플래그 목록은 `CodexExecAdapter.help_commands`(`codex_adapter.py` 321–324행)다. 시험은 이 목록을 import하지 않고 다시 적는다. 빠뜨림 경우는 셋만 고르며, 모두 `build_argv`가 실제로 쓰는 플래그다.

### `test_worker_does_not_accept_fake_argument_prefixes` (행 50–77)
- 성질: 작업자 요청은 임의의 명령 앞부분(`codex_argv`)을 받지 않는다. 정상 요청으로 실행하면 작업자는 셸 없이 자기가 만든 인자로 CLI를 띄우고, 프롬프트를 표준 입력으로 넘기며, API 키를 환경에서 빼고, 상태 파일에 종료 코드를 남긴다.
- 준비: 임시 폴더의 프롬프트 파일(`b"hello"`)과 완전한 요청(`codex_path=sys.executable`, `max_runtime_seconds=5`). 먼저 `codex_argv=[sys.executable, fake.py]`를 더한 요청 파일을 쓴다. 가짜 `Popen` 클래스 `Process`는 받은 명령, `env`, `shell`, 표준 입력을 `captured`에 기록하고 종료 코드 0을 낸다. 테스트 동안 `OPENAI_API_KEY="must-not-pass"`를 프로세스 환경에 넣고, `finally`에서 되돌린다.
- 실행: `codex_worker.run(request_path)`를 두 번 부른다. 한 번은 `codex_argv`가 있는 요청, 한 번은 정상 요청이다.
- 단언:
  - 첫 호출은 `ValueError`를 메시지 `"unknown worker request fields: codex_argv"`로 낸다.
  - 둘째 호출은 0을 돌려준다.
  - 기록된 명령이 `codex_worker.build_argv(request)`와 같다. `env`에 `OPENAI_API_KEY`가 없다. `shell`이 거짓이다. 표준 입력이 `b"hello"`다.
  - 상태 파일의 `cli_exit_code`가 0이다.
- 대역: `patch.object(cli_worker.subprocess, "Popen", Process)`. 프로세스 환경 변수를 직접 바꾸고 되돌린다.
- 비고: `run_cli`는 작업 공간 아래에 `.scratch/.execution-temp`를 만들어 `TEMP`/`TMP`로 준다. 시험은 이것을 단언하지 않는다.

### `test_sanitized_environment_removes_every_forced_api_route` (행 79–83)
- 성질: Codex 작업자의 환경 정리는 API 키, 접근 토큰, 기본 URL 같은 강제 API 경로를 모두 뺀다.
- 준비: `OPENAI_API_KEY`, `CODEX_API_KEY`, `CODEX_ACCESS_TOKEN`, `OPENAI_BASE_URL`, `PATH`가 든 사전.
- 실행: `codex_worker.sanitized_environment(...)`.
- 단언: 결과가 `{"PATH": "safe"}`와 같다.
- 대역: 없음.
- 비고: 제품은 허용 목록 방식이다(`cli_worker.ENV_ALLOWLIST`에 `CODEX_HOME` 추가). 따라서 이 네 이름뿐 아니라 목록에 없는 모든 이름이 빠진다.

### `test_invalid_timeout_duplicate_json_and_windows_sandbox_fail_before_start` (행 85–105)
- 성질: 요청 파일의 중복 키, 비유한 상수, 양수가 아닌 실행 한도, 알 수 없는 Windows 샌드박스 값은 모두 작업 시작 전 요청 검사에서 거부된다.
- 준비: 한 요청 파일 경로에 네 내용을 차례로 쓴다.
  1. `codex_path`가 중복된 JSON.
  2. `max_runtime_seconds=NaN`인 요청(`json.dumps`가 `NaN`으로 쓴다).
  3. `max_runtime_seconds=0`.
  4. `max_runtime_seconds=1`, `windows_sandbox="none"`.
- 실행: 각 내용으로 `codex_worker.load_request(path)`.
- 단언: 각각 `ValueError`의 메시지 조각이 `"duplicate"`, `"non-finite JSON constant"`, `"max_runtime"`, `"windows_sandbox"`다. 곧 거부 사유를 메시지로 고정한다.
- 대역: 없음.
- 비고: 주석(95행)은 요청 파일을 엄격히 파싱하므로 이름 붙은 비유한 상수가 필드 검사에 닿지 않는다고 설명한다. NaN은 `max_runtime_seconds` 검사 전에 `strict_json_loads`의 `"non-finite JSON constant: NaN"`으로 거부된다. 이름의 "before start"는 `start`를 부르지 않고 `load_request`만으로 거부된다는 뜻이다.

### `test_scholarly_is_the_only_explicit_mcp_and_uses_workspace_data_directory` (행 107–119)
- 성질: Codex 작업자가 명시하는 MCP 서버는 scholarly 하나이고, 그 데이터 폴더는 작업 공간 아래 `scholarly-data`다.
- 준비: `scholarly_server={"command": "python", "args": ["C:/server.py"]}`가 있는 요청.
- 실행: `codex_worker.build_argv(request)`. `--config` 다음 값만 모은다.
- 단언: `mcp_servers.scholarly.command="python"`이 있다. `mcp_servers.scholarly.args=` 값에 `"C:/server.py"`, `"--data-dir"`, `scholarly-data`가 들어 있다. `mcp_servers.`를 담은 값 가운데 `scholarly`가 없는 것은 없다.
- 대역: 없음.
- 비고: 요청에 `control_binding`이 없으므로 제어 서버 설정도 없다. 결합된 실행이라면 제어 MCP 서버(`CONTROL_SERVER`)가 추가되며, 이 시험은 그 경우를 보지 않는다. 이름의 "only explicit"는 결합이 없는 요청에 대한 것이다.

### `test_worker_remains_importable_as_its_direct_job_root` (행 121–125)
- 성질: `codex_worker.py`는 패키지 밖의 직접 스크립트로 실행되어도 import 오류 없이 사용법 안내까지 간다.
- 준비: 없음.
- 실행: 실제 자식 프로세스 `subprocess.run([sys.executable, codex_worker.__file__], capture_output=True, timeout=10)`. 인자가 없다.
- 단언: 표준 오류에 `b"No module named"`가 없고 `b"usage: codex_worker.py REQUEST.json"`이 있다.
- 대역: 없음.
- 비고: 실제 Python 자식 프로세스를 쓴다(시간 상한 10초). 시험-지침 4절 규칙 6은 인터프리터의 시작(import, `sys.path`)이 검사 대상이면 자식 프로세스를 유지하라고 한다. 이 시험이 그 경우다. 제품은 `do_math` 패키지 import가 실패하면 같은 폴더의 모듈로 되돌아간다(`codex_worker.py` 14–21행).

### `test_claude_worker_remains_importable_as_its_direct_job_root` (행 127–131)
- 성질: `claude_worker.py`도 직접 스크립트로 실행되어 import 오류 없이 사용법 안내까지 간다.
- 준비: 없음.
- 실행: 실제 자식 프로세스로 `claude_worker.__file__`을 인자 없이 실행한다(시간 상한 10초).
- 단언: 표준 오류에 `b"No module named"`가 없고 `b"usage: claude_worker.py REQUEST.json"`이 있다.
- 대역: 없음.
- 비고: 앞 시험과 대상 파일만 다르다. Claude 작업자의 되돌아가기 import는 `claude_worker.py` 12–19행이다.

### `test_unknown_worker_request_field_is_rejected` (행 133–143)
- 성질: 작업자 요청에 선언되지 않은 필드가 있으면 거부된다.
- 준비: 필수 필드를 모두 갖추고 알 수 없는 `file_system={}`을 더한 요청 파일.
- 실행: `codex_worker.load_request(path)`.
- 단언: `ValueError`를 메시지 조각 `"unknown worker request fields"`로 낸다.
- 대역: 없음.
- 비고: `test_worker_does_not_accept_fake_argument_prefixes`의 첫 단언과 같은 경로(`cli_worker.check_common_request`)다. 그쪽은 명령 앞부분 필드와 필드 이름까지, 이쪽은 다른 필드와 문구 앞부분만 본다.

### `test_jsonl_tail_and_missing_terminal_are_not_success` (행 145–149)
- 성질: 줄바꿈 없는 파싱 불가 꼬리가 있고 종료 사건이 없는 Codex 스트림은 성공이 아니다. 앞에서 읽은 스레드 ID는 남는다.
- 준비: `thread.started` 한 행과 꼬리 `not-json`.
- 실행: `_parse_jsonl(...)`.
- 단언: `thread_id`가 `"t"`, `turn_completed`가 거짓, `unparsed_tail_bytes`가 0보다 크다.
- 대역: 없음.

### `test_ambiguous_or_nonfinite_native_events_cannot_establish_completion` (행 151–171)
- 성질: 종료 사건 행에 중복 키나 비유한 수가 있으면 그 행은 파싱 불가로 처리되어 완료를 세우지 못한다. 유한한 소수는 받아들인다.
- 준비: 접두는 `thread.started`(`thread_id` `t`)와 `turn.started` 두 행이다. `subTest(terminal=...)` 여섯 종료 행을 붙인다.
  1. `type` 키가 중복된 `turn.failed`/`turn.completed`.
  2. `usage.tokens` 중복.
  3. `NaN`.
  4. `Infinity`.
  5. `-Infinity`.
  6. `1e999`.
- 실행: `_parse_jsonl(prefix + terminal)`. 이어서 `usage={"cost": 0.25}`인 정상 종료 행.
- 단언: 여섯 경우 모두 `parse_complete`와 `turn_completed`가 거짓이다. `parsed_bytes`는 접두 길이, `unparsed_tail_bytes`는 종료 행 길이다. `unknown_events[0].kind`는 `"invalid_jsonl"`이다. 정상 경우는 `parse_complete`와 `turn_completed`가 참이고 `usage`가 `[{"cost": 0.25}]`다.
- 대역: 없음.
- 비고: 1번은 종료 종류 자체가 모호한 경우다. 파서가 마지막 키로 조용히 해석하면 실패가 완료로 바뀔 수 있다. `parsed_bytes`와 `unparsed_tail_bytes`의 정확한 값은 파서가 잘못된 행에서 즉시 멈추고 그 앞까지만 소비함을 고정한다.

### `test_collect_rejects_malformed_tail_even_with_turn_completed` (행 173–185)
- 성질: 스트림에 `turn.completed`가 있어도 그 뒤에 파싱할 수 없는 꼬리가 있으면 수집은 불완전이다.
- 준비: 임시 폴더에 출력 파일 넷을 쓴다. `stdout`은 `{"type":"turn.completed"}\nbroken`, `stderr`는 빈 파일, `final`은 `b"final"`, 상태는 `{"state":"exited","cli_exit_code":0}`이다. `CLIExecution`은 요청 `b"{}"`, 프롬프트 `b"p"`와 그 SHA-256, 작업자 인자 `("worker",)`, 스키마 해시 `None`, 그리고 `FakeJob(JobInspection(0, (), True))`로 만든다. 이 Job 관찰은 종료 장벽이 확인된 상태다.
- 실행: `CodexExecAdapter(sys.executable).collect(execution)`.
- 단언: `result`가 `"incomplete"`이고 `reasons`에 `"jsonl_parse_incomplete"`가 있다.
- 대역: `FakeJob`(고정 `JobInspection`).
- 비고: `_parse_jsonl`은 잘못된 행에서 멈출 때 그때까지의 `turn_completed`(여기서는 참)를 돌려준다. 그래서 수집기가 `parse_complete`를 따로 보는지가 이 시험의 요점이다. 상태 파일에 해시가 없으므로 다른 사유(`worker_stdin_hash_mismatch` 등)도 함께 붙는다. 시험은 `assertIn`으로 한 사유만 본다.

### `test_collect_reports_start_snapshot_bytes_without_rereading_them` (행 187–201)
- 성질: 수집기는 원본 요청과 프롬프트를 파일에서 다시 읽지 않고, 시작 때 해시한 스냅숏 바이트와 기록된 해시를 그대로 보고한다.
- 준비: 앞 시험과 같은 구성이다. 다만 `stdout`은 빈 파일이다. 주석(194행)이 밝히듯 비공개 스냅숏 파일은 존재하지 않는다.
- 실행: `CodexExecAdapter(sys.executable).collect(execution)`.
- 단언: `source_request`가 `{"present": True, "bytes": 2, "sha256": execution.request_sha256, "raw": b"{}"}`와 같다. `source_prompt.sha256`이 `execution.prompt_sha256`이다.
- 대역: `FakeJob`.
- 비고: 제품은 `_artifact(raw, sha256)`에 시작 때의 해시를 넘겨 다시 계산하지 않는다(`codex_adapter.py` 280–281행). 빈 스트림이므로 수집 결과는 불완전이지만 시험은 그것을 보지 않는다.

### `test_timeout_with_descendant_still_in_job_cannot_collect_stale_files` (행 203–213)
- 성질: 작업자가 시간 초과로 끝났어도 Job 안에 후손 프로세스가 남아 있으면 수집기는 출력 파일을 읽지 않는다. 그 파일은 낡았을 수 있다.
- 준비: 출력 셋에 `b"old"`를 쓰고, 상태는 `{"state":"timeout","runner_stop_required":true}`로 둔다. Job 관찰은 `JobInspection(1, (99,), True)`다. 곧 루트는 신호를 받았지만 활성 프로세스 1개(pid 99)가 남아 있다.
- 실행: `collect(execution)`.
- 단언: `artifacts_read`가 거짓이고 `reasons`에 `"termination_barrier_unconfirmed"`가 있다.
- 대역: `FakeJob`.
- 비고: 제품은 장벽이 없으면 파일을 읽기 전에 돌아간다(`codex_adapter.py` 245–252행). 이 시험은 "루트 신호만으로는 부족하다"는 `wait_for_termination`의 docstring과 같은 규칙을 수집기 쪽에서 본다.

### `test_start_rejects_preexisting_output_before_creating_a_job` (행 215–223)
- 성질: 요청이 가리키는 출력 경로에 이미 파일이 있으면 `start`는 Job을 만들기 전에 거부한다.
- 준비: 프롬프트 파일과, 미리 `b"old"`를 쓴 `final` 파일. `final_path`가 그 파일을 가리키는 정상 요청(`codex_path=sys.executable`).
- 실행: `CodexExecAdapter(sys.executable).start(request_path, cwd=root, env={})`.
- 단언: `FileExistsError`가 난다(유형만 본다).
- 대역: 없음.
- 비고: 제품의 검사 순서는 요청 적재, 실행 파일 일치, 경로 구별, 출력 존재 순이다. 출력 존재 검사(`codex_adapter.py` 194–195행)는 스냅숏 폴더와 `WindowsJob` 생성보다 앞에 있다. 시험은 Job이 만들어지지 않았다는 것을 직접 단언하지 않는다. 예외가 그 앞에서 난다는 코드 순서로 보증된다. 작업 공간과 출력이 같은 임시 폴더에 있지만, 출력 존재 검사가 작업 공간 밖 검사(196–198행)보다 먼저라서 이 거부가 먼저 난다.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈:
  - `test_claude_adapter`는 같은 기반 `LocalCLIAdapter` 위의 Claude 어댑터와 작업자를 본다. 이 모듈에 있는 Claude 작업자의 직접 실행 시험은 두 작업자가 공유하는 직접 루트 규칙이라 여기 함께 있다.
  - `test_execution_profiles`는 능력 신원(`capability_identity`), 표면 증거와 Job 증거의 구별, 구조적 시작 실패를 본다. 이 모듈의 `describe` 시험은 그 표면 판정의 플래그 조건만 본다.
  - 실제 Windows Job의 생성과 종료 장벽은 `test_owned_job_children`이 실제 자식 프로세스로 본다. 이 모듈은 `FakeJob`으로 장벽 관찰만 흉내 낸다.
  - `test_model_runner`는 러너가 수집 결과를 판정하는 층을 본다. 이 모듈은 수집 결과를 만드는 층이다.
- 픽스처 의존: `FakeJob`의 소비자는 이 모듈과 `test_execution_profiles`다.
- 이 모듈에만 있는 도우미: 없다(지역 클래스 `Process`는 한 테스트 안에만 있다).

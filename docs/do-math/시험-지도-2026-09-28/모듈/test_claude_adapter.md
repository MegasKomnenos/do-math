# test_claude_adapter

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_claude_adapter.py` (240행) |
| 클래스 / 테스트 | 1 / 12 |
| 시험 대상 제품 코드 | `do_math/claude_adapter.py`의 `parse_jsonl`(= `claude_stream.parse_stream`), `ClaudePrintAdapter.parse_response`, `final_bytes`, `validate_final`, `ADAPTERS`; `do_math/claude_worker.py`의 `build_argv`, `sanitized_environment`; `do_math/codex_worker.py`의 `load_request`; `do_math/model_runner.py`의 `ModelRunner.run`(공급자 라우팅, 모델 잠금, `claude:` 접두 제거); `do_math/execution_profiles.py`의 `build_profiles`, `runner_tools`, `prepare_prompt`, `prompt_seal`, `profile_ref`; `do_math/configuration.py`의 `validate_config`; `do_math/model_policy.py`의 `selection`; `do_math/session_slots.py`의 `SessionSlots`; `do_math/observations.py`의 `ObservationTracker`; `do_math/contracts.py`의 `ROLES`, `schema_for`; `do_math/cli.py`의 `build_parser` |
| 사용하는 픽스처 모듈 | `provider_fixtures`의 `CLAUDE_INIT`, `CLAUDE_RESULT`, `claude_stream`, `Adapter`, `runner_with`; `research_fixtures`의 `observe`, `dispatched_launch` |
| 격리 표지 | 없음 |
| 시작 상태 | 1단이 대부분(파서, 작업자 인자 빌더, 설정 검증기, 선택기, CLI 파서 직접 호출). 라우팅과 잠금 시험은 실제 `ModelRunner`에 수집기 대역 `Adapter`를 끼운다. 슬롯 시험은 손으로 만든 사전 상태 위의 `SessionSlots`다 |

## 목적

모듈 docstring은 "Claude stream validation and routing at the same local execution boundary."이다. Claude는 Codex와 같은 지역 실행 경계(`LocalCLIAdapter`의 Windows Job 수명, 증거 수집)를 공유한다. `claude_adapter.py`의 docstring은 "Interpret native Claude events without treating exit zero as completion."이다. 이 모듈은 Claude가 그 경계에 들어올 때의 규칙을 본다. 스트림이 완료와 제출을 스스로 입증해야 한다. 최종 응답은 스트림에서 골라 보존된 바이트와 대조한다. 작업자는 로그인 상태와 표준 입력, 스키마, 설정된 MCP만 쓴다. 러너는 모델 이름으로 공급자를 고르고, 모델 잠금은 Claude 요청에만 전달한다. 혼합 모델 구성에서는 선택과 모델별 작업 슬롯이 기존 규칙을 따른다.

## 모듈 수준 요소

- 행 11: `sys.path.insert(0, str(Path(__file__).resolve().parents[1]))`로 `scripts/` 폴더를 경로 앞에 넣는 공통 머리다.
- `routed_requests(calls)` (행 21–39): 실제 `ModelRunner` 하나의 모든 공급자 칸(`codex`, `claude`)을 공급자별 `Adapter`(수집 결과 `output_collected`, 최종 `b"{}"`)로 바꾼다. 그 뒤 `(model, lock)` 쌍마다 새 임시 작업 공간에서 `run(model=..., output_schema={}, effort="low", timeout_seconds=1, claude_only_assigned_model=lock)`을 부른다. 호출 전에 각 대역의 `request` 속성을 지워, 이번 호출이 시작한 대역의 요청만 `(provider, request)`로 모은다. 한 러너를 여러 호출에 재사용하므로, 공유 러너가 호출 사이에 바뀌지 않는지도 이 도우미 위에서 확인된다. `test_model_lock_is_opt_in_and_reaches_only_claude`와 `test_router_dispatches_claude_and_codex_without_mutating_shared_runner`가 쓴다.
- 행 239–240: 직접 실행하면 `unittest.main()`을 부른다.

## ClaudeTests (행 42–236)

`unittest.TestCase`를 그대로 상속한다. 표지, 클래스 속성, 훅, 도우미 메서드가 없다.

### `test_claude_lock_in_pinned_profile_keeps_codex_request_valid` (행 43–66)
- 성질: 고정 프로필에 Claude 전용 모델 잠금이 켜져 있어도, 그 프로필이 Codex 모델을 쓰면 Codex 작업자 요청에는 잠금 필드가 들어가지 않고 요청이 유효하다.
- 준비: `DEFAULT_CONFIG`에 `claude_only_assigned_model=True`, `scholarly_enabled=False`를 둔 설정으로 `build_profiles`를 부르고, `maintenance` 역할 프로필 하나를 고른다. 기본 등급 모델은 모두 Codex 모델(`gpt-6-astra`, `gpt-5.6-sol`, `gpt-5.6-terra`)이다. codex 칸에 `Adapter`를 끼운 `runner_with`를 쓴다.
- 실행: `runner.run(model=profile["ai"]["model"], effort=profile["ai"]["effort"], prompt=prepare_prompt("fixture", profile), ..., timeout_seconds=1, execution_id="EX-codex-lock", profile=profile, launch_ticket=dispatched_launch(...), input_seal=prompt_seal(prompt))`. 이어서 증거 폴더의 요청을 실제 `codex_worker.load_request`로 읽는다.
- 단언: 프로필의 `ai.claude_only_assigned_model`이 참이다. Codex 요청에 `claude_only_assigned_model`이 없다. 요청의 `profile_ref`가 `profile_ref(profile)`과 같다. 결과 `status`가 `'completed'`다.
- 대역: `Adapter`, `runner_with`.
- 비고: 러너는 잠금이 참이고 요청에 `claude_path`가 있을 때만 잠금 필드를 싣는다(`model_runner.py` 113–114행). `codex_worker.load_request`는 알 수 없는 필드를 `"unknown worker request fields: "`로 거부하므로, 요청을 읽는 데 성공한 것 자체가 유효성 단언이다. `maintenance`는 작업 역할이 아니므로 `timeout_seconds=1`이 프로필의 호출 제한 안에 있어야 한다. 기본값 600초 안이다. `dispatched_launch`는 `launch.ticket`으로 티켓을 만들고, 이 함수는 `windows_job.owner_identity()`로 현재 프로세스의 Windows 신원을 읽는다. 러너의 `validate_start`도 그 신원을 다시 대조하므로, 이 시험은 Windows 호스트를 전제한다.

### `test_model_lock_is_opt_in_and_reaches_only_claude` (행 68–98)
- 성질: 모델 잠금은 기본으로 꺼져 있고 불리언만 받는다. 켜면 고정 프로필이 러너 도구로 전달하고, 러너는 Claude 요청에만 싣는다. Claude 작업자는 잠금이 있을 때만 모델 전환과 하위 에이전트 모델을 그 모델로 묶는 설정을 넣는다.
- 준비: 잠금을 켠 설정의 `maintenance` 프로필. 스키마 파일 `{"type":"object"}`을 쓴 임시 폴더. Claude 요청 사전(`claude.exe`, `claude-opus-5`, `high`).
- 실행:
  1. `runner_tools(profile)`을 부른다.
  2. `validate_config({"claude_only_assigned_model": "true"})`를 부른다.
  3. `routed_requests([("claude-opus-5", True), ("gpt-5.6-sol", True)])`를 부른다.
  4. `claude_worker.build_argv`를 잠금 없이 한 번, `request["claude_only_assigned_model"] = True` 뒤에 한 번 부른다.
- 단언:
  - `runner_tools(profile)["claude_only_assigned_model"]`이 참이고, `DEFAULT_CONFIG`의 값은 거짓이다.
  - 문자열 `"true"`는 `ValueError`를 낸다(유형만 본다).
  - 라우팅 결과는 `[("claude", "claude-opus-5", True), ("codex", "gpt-5.6-sol", None)]`이다.
  - 잠금이 없으면 `--settings` JSON에 `availableModels`가 없다.
  - 잠금이 있으면 `availableModels == ["claude-opus-5"]`, `fallbackModel == []`, `switchModelsOnFlag`가 거짓이다. `env`의 `CLAUDE_CODE_SUBAGENT_MODEL`과 `ANTHROPIC_DEFAULT_HAIKU_MODEL`이 `"claude-opus-5"`이고 `CLAUDE_CODE_SUBAGENT_MODEL_FORCE`가 `"1"`이다.
- 대역: `routed_requests` 안의 `Adapter`.
- 비고: 주석(72행)은 러너가 잠금을 현재 설정이 아니라 고정 판본에서 읽는다고 밝힌다. `routed_requests`는 프로필 없이 잠금을 인자로 주는 경로를 쓴다. 이 경로에서 러너는 인자를 그대로 쓴다.

### `test_role_schemas_reach_claude_without_unsupported_meta_schema` (행 100–117)
- 성질: 모든 역할의 출력 스키마는 `$schema`와 `x-contract-id`만 뺀 채 그대로 Claude의 `--json-schema`에 전달된다. 전달된 스키마는 Draft 7로 유효하고 빈 객체를 거부한다. 원래 스키마 파일은 바뀌지 않는다.
- 준비: `contracts.ROLES`의 역할마다 `subTest(role=role)`로 돈다. `schema_for(role)`을 JSON으로 써 둔 스키마 파일 하나를 쓴다.
- 실행: `claude_worker.build_argv({"claude_path": "claude.exe", "model": "claude-opus-5", "effort": "high", "cwd": d, "output_schema_path": ...})`. `--json-schema` 다음 인자를 JSON으로 읽는다.
- 단언: 전달값이 원본에서 `$schema`와 `x-contract-id`를 뺀 사전과 같다. `Draft7Validator.check_schema(sent)`가 통과한다. `Draft7Validator(sent).is_valid({})`가 거짓이다. 스키마 파일의 텍스트가 쓴 그대로다.
- 대역: 없음.
- 비고: 제품은 `$schema`가 2020-12 메타 스키마일 때만 그 키를 뺀다(`claude_worker.py` 67–68행). 이름의 "unsupported meta schema"는 공급자가 받지 않는 메타 스키마 선언을 가리킨다. Draft 7 검사를 하는 이유는 원문에 적혀 있지 않다.

### `test_claude_tools_and_messages_feed_progress_observation` (행 119–131)
- 성질: Claude의 `assistant` 사건 속 도구 호출과 텍스트, `user` 사건 속 도구 결과가 진행 관찰기의 대기 도구, 완료 호출, 관찰 사실로 들어간다.
- 준비: `ObservationTracker("one", Path(d), {"observation_mode": "periodic", "research_self_checks": False})`.
- 실행: `research_fixtures.observe(tracker, event)`로 두 사건을 차례로 관찰한다. 첫째는 텍스트 `"Checking the computation."`와 `tool_use`(`id` `tool-one`, `Bash`)를 담은 `assistant` 사건이다. 둘째는 `tool_use_id` `tool-one`의 `tool_result`를 담은 `user` 사건이다. `observe`는 각 사건을 1바이트 스트림 행으로 좌표를 붙여 넘긴다.
- 단언: 첫 관찰 뒤 `tracker.pending_tools`에 `tool-one`이 있다. 둘째 관찰 뒤 `completed_call_ids`가 `{"tool-one"}`이고 `pending_tools`가 비어 있다. 첫 관찰이 돌려준 사실 가운데 `kind == "observation_fact"`인 첫 행의 JSON에 텍스트 `"Checking the computation."`가 들어 있다.
- 대역: 없음.

### `test_profile_accepts_claude_provider` (행 133–139)
- 성질: 공개 CLI의 `profile` 명령은 `--provider claude`를 받는다.
- 준비: 없음.
- 실행: `build_parser().parse_args(["profile", "--provider", "claude"])`.
- 단언: `CliInputError`가 나면 그 메시지로 실패시킨다. `args.provider`가 `"claude"`다.
- 대역: 없음.
- 비고: `cli.py` 192행의 `choices=("codex", "claude")`, 기본값 `"codex"`를 고정한다. 명령 실행은 하지 않는다.

### `test_native_success_extracts_structured_output_and_usage` (행 141–147)
- 성질: 성공한 원생 스트림에서 구조화 출력과 사용량 행이 추출되고, 구간 안의 `rate_limit_event`는 완료를 깨지 않는다.
- 준비: `claude_stream(CLAUDE_INIT, {"type": "rate_limit_event"}, CLAUDE_RESULT)`. `CLAUDE_RESULT`는 세션 `session-one`, `structured_output={"ok": True}`, 사용량 입력 7·출력 3이다.
- 실행: `claude_adapter.parse_jsonl(...)`.
- 단언: `parse_complete`와 `turn_completed`가 참이다. `structured_output`이 `{"ok": True}`이고 `usage`가 `[CLAUDE_RESULT["usage"]]`다.
- 대역: 없음.

### `test_rate_notification_can_precede_init_but_work_cannot` (행 149–158)
- 성질: 같은 세션의 입장 알림(`rate_limit_event`)은 세션 시작 전에 와도 되지만, 작업 사건이나 다른 세션의 알림, 문자열이 아닌 세션 ID는 스트림을 불완전하게 만든다.
- 준비: `notification = {"type": "rate_limit_event", "session_id": "session-one"}`. 음성은 `subTest(events=...)` 세 경우다.
  1. `init` 앞의 `assistant`.
  2. 세션 `"other"`의 알림.
  3. 세션 ID가 정수 7인 `init`과 결과.
- 실행: `parse_jsonl(claude_stream(...))`.
- 단언: 알림이 앞선 정상 스트림은 `parse_complete`가 참이다. 세 음성 경우는 모두 거짓이다.
- 대역: 없음.
- 비고: 주석(151행)은 이 순서를 scholarly MCP 연결 중 Claude 2.1.274에서 관찰했다고 적는다. 제품의 오류는 차례로 `work_before_session_start`, `session_mismatch`, `invalid_session_start`다. 시험은 오류 이름을 단언하지 않는다.

### `test_final_is_selected_from_the_stream_and_preserved_bytes_must_match_it` (행 160–169)
- 성질: 최종 응답은 스트림이 고른 구조화 출력의 정해진 직렬화 바이트다. 보존된 최종 바이트는 그것과 정확히 같아야 하며, 의미가 같아도 바이트가 다르면 불일치다.
- 준비: `ClaudePrintAdapter("unused")`. 요청 `{"output_schema_path": "schema.json"}`으로 `claude_stream(CLAUDE_INIT, CLAUDE_RESULT)`를 파싱한다.
- 실행: `adapter.final_bytes(parsed)`와 `validate_final`. 이어서 `subTest(final=...)` 세 바이트열 `b'{"ok":1}'`, `b'{"ok":false,"ok":true}'`, `b'{"ok":true}'`로 `validate_final`을 부른다. 마지막으로 결과 없는 스트림(`CLAUDE_INIT`만)을 요청 `{}`로 파싱해 `final_bytes`를 부른다.
- 단언: `json.loads(final)`이 `CLAUDE_RESULT["structured_output"]`과 같다. 그 바이트로 `validate_final`이 `[]`다. 세 변형은 모두 참인 목록(불일치)이다. 결과 없는 스트림의 `final_bytes`는 `None`이다.
- 대역: 없음.
- 비고: 셋째 변형 `b'{"ok":true}'`는 의미가 같지만 불일치다. 제품의 `final_bytes`는 `json.dumps(..., ensure_ascii=False, allow_nan=False)`의 기본 구분자(`": "`)를 쓰므로 공백이 다르기 때문이다(`codex_adapter.py` 298–308행). 이 시험은 바이트 비교가 JSON 의미 비교가 아님을 고정한다.

### `test_error_truncation_duplicate_terminal_and_session_mismatch_fail` (행 171–181)
- 성질: 종료 없음, 중복 종료, 잘린 꼬리, 세션 불일치, 시작 없는 결과, 종료 뒤 작업은 모두 파싱을 불완전하게 만든다. 오류 결과는 턴 실패로 기록되고 완료가 아니다.
- 준비: `subTest(raw=...)` 여섯 경우.
  1. `CLAUDE_INIT`만.
  2. `CLAUDE_INIT, CLAUDE_RESULT, CLAUDE_RESULT`.
  3. `CLAUDE_INIT, CLAUDE_RESULT` 뒤에 `{"type":`.
  4. 세션이 `"another"`인 결과.
  5. `CLAUDE_RESULT`만.
  6. `CLAUDE_INIT, CLAUDE_RESULT` 뒤의 `assistant`.

  이어서 `subtype="error_max_turns"`, `is_error=True`인 결과.
- 실행: `parse_jsonl`.
- 단언: 여섯 경우 모두 `parse_complete`가 거짓이다. 오류 결과는 `turn_failed`가 참이고 `turn_completed`가 거짓이다.
- 대역: 없음.
- 비고: 이 시험과 `test_claude_stream`의 `test_later_failure_or_truncation_cannot_fall_back_to_old_success`는 겹치는 경우가 있다(종료 뒤 결과, 잘린 꼬리, 세션 불일치). 이 시험은 단일 구간 스트림에서 `parse_complete`를 보고, 그쪽은 다중 구간에서 `turn_completed`와 `structured_output`의 부재를 본다.

### `test_worker_uses_login_stdin_schema_and_only_configured_mcp` (행 183–204)
- 성질: Claude 작업자는 구독 로그인을 유지하는 print 모드로 실행하고, 스트림 JSON을 출력하며, 세션을 저장하지 않는다. MCP는 설정된 scholarly 서버만 엄격 모드로 쓰고, 그 데이터 폴더는 작업 공간 아래다. 환경은 API 키와 우회 경로를 뺀 허용 목록만 넘긴다.
- 준비: 스키마 파일과, `model="haiku"`, `effort="low"`, `scholarly_server={"command": "python", "args": [server.py 경로]}`인 요청.
- 실행: `claude_worker.build_argv(request)`, 이어서 `claude_worker.sanitized_environment({...})`.
- 단언:
  - 인자의 앞 둘이 `["claude.exe", "--print"]`다. `stream-json`이 있고 `--bare`는 없다. `--no-session-persistence`와 `--strict-mcp-config`가 있다.
  - `--mcp-config`의 `mcpServers` 키 집합이 `{"scholarly"}`이다. 그 `args`의 마지막 둘이 `["--data-dir", str(root / "scholarly-data")]`다.
  - 정리된 환경이 `{"PATH": "ok", "USERPROFILE": "login", "CLAUDE_CONFIG_DIR": "config"}`와 같다. 곧 `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, `CLAUDECODE`, `ANTHROPIC_BASE_URL`, `CLAUDE_CODE_USE_BEDROCK`이 빠진다.
- 대역: 없음.
- 비고: 제품 주석(`claude_worker.py` 57행)은 `--bare`가 OAuth 로그인을 끄므로 일부러 쓰지 않는다고 설명한다. 이름의 "stdin"은 이 시험에서 직접 단언되지 않는다. 표준 입력으로 프롬프트를 넘기는 것은 `cli_worker.run_cli`의 동작이다.

### `test_router_dispatches_claude_and_codex_without_mutating_shared_runner` (행 206–212)
- 성질: 한 러너가 모델 이름에 따라 Claude와 Codex 어댑터로 호출을 보내고, `claude:` 접두는 떼어 CLI에 넘기며, 이름 없는 `claude:`는 거부한다.
- 준비: 없음(도우미가 준비한다).
- 실행: `routed_requests([("claude:haiku", None), ("gpt-5.6-sol", None), ("claude-haiku-4-5-20251001", None)])`, 이어서 `routed_requests([("claude:", None)])`.
- 단언: 결과가 `[("claude", "haiku"), ("codex", "gpt-5.6-sol"), ("claude", "claude-haiku-4-5-20251001")]`다. 빈 이름은 `ValueError`를 메시지 조각 `"requires a Claude model name"`로 낸다.
- 대역: `routed_requests` 안의 `Adapter`.
- 비고: 주석(208행)은 각 호출이 자기 공급자의 어댑터에 닿고 Claude CLI는 `claude:` 없는 이름을 받는다고 밝힌다. "without mutating shared runner"는 같은 러너로 연이어 부른 세 호출이 각자의 공급자로 간다는 결과로만 확인된다. 러너의 `adapters`가 그대로라는 단언은 따로 없다.

### `test_mixed_models_use_existing_selection_and_per_model_work_slots` (행 214–236)
- 성질: 공급자가 섞인 등급 구성에서도 모델 선택은 기존 등급 규칙을 따르고, 작업 슬롯은 모델마다 따로 센다. 운영 역할은 작업 슬롯을 쓰지 않으며, 반환된 슬롯은 다시 쓸 수 있다.
- 준비: `tier_models`는 `high="claude:opus"`, `medium="gpt-5.6-sol"`, `low="claude:haiku"`이고, 세 모델의 작업 슬롯은 각각 1이다. `validate_config`로 통과를 확인한다. `state = {**build_profiles(config), "config": config}`, `runtime = {"executions": {}, "reservations": {}}` 위의 `SessionSlots`를 쓴다. 지역 함수 `acquire(eid, role, model)`은 그 역할과 모델의 프로필로 `slots.acquire`를 부른다.
- 실행: `selection`을 두 역할에 부르고, 지역 함수 `acquire`로 `one`, `two`, `three`, `four`를 차례로 입장시킨다. 이어서 `slots.release("one")` 뒤 `two`를 다시 입장시킨다.
- 단언: 단계별로 확인하는 결과는 다음과 같다.
  - `selection(config, {"role": "research_plan"}, {}, {})["model"]`이 `"claude:opus"`, `task_contract_review`가 `"gpt-5.6-sol"`이다. 기본 `role_tiers`의 high와 medium이다.
  - `one`(research_work, claude:opus)은 참이고, `two`(같은 모델)는 거짓이다. 슬롯이 1이기 때문이다.
  - `three`(research_plan, claude:opus)는 참이다. 운영 역할은 작업 슬롯을 예약하지 않는다(주석 232행).
  - `four`(research_work, gpt-5.6-sol)는 참이다. 모델이 다르면 슬롯도 따로다.
  - `slots.release("one")`이 참이고, 그 뒤 `two`가 참이다.
- 대역: 없음. `tempfile.TemporaryDirectory()`를 열지만 그 경로는 쓰이지 않는다.
- 비고: `release`가 참인 것은 발급된 티켓의 Job이 만들어진 적이 없어 비었다고 확인되기 때문이다. 이 확인은 패치 없이 실제 Windows API(`OpenProcess`, `OpenJobObjectW`)를 부르고, 입장 때의 티켓 발급도 `windows_job.owner_identity()`를 부르므로, 이 시험은 Windows 호스트를 전제한다. 처음 거절된 `two`는 등록되지 않았으므로 같은 ID로 다시 입장할 수 있다.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈:
  - `test_claude_stream`은 같은 파서의 다중 구간 규칙과 입장 거부 분류를 순수 함수로 본다. 이 모듈은 단일 구간 판정과 어댑터·작업자·러너 경계를 본다.
  - `test_codex_adapter`는 공통 기반 `LocalCLIAdapter`의 수명 처리와 Codex 작업자를 본다. `test_codex_adapter`의 `test_claude_worker_remains_importable_as_its_direct_job_root`는 Claude 작업자의 직접 실행 가능성을 본다.
  - `test_provider_final_contract`는 제어 결합이 있을 때 `--json-schema`가 빠지는 것과 텍스트 최종 응답의 바이트 대조를 본다.
  - `test_model_runner`는 공급자와 무관한 러너 수명을 본다. 이 모듈은 러너의 공급자 라우팅과 모델 잠금을 본다.
  - 모델별 슬롯 산술은 `test_budget`이 순수 함수로 보고, 이 모듈의 마지막 시험은 `SessionSlots` 층에서 본다. `test_configuration`은 단일 모델 구성에서 용량 제약과 프로필의 연결을 본다.
- 픽스처 의존: `CLAUDE_INIT`과 `CLAUDE_RESULT`의 소비자는 이 모듈과 `test_execution_profiles`다. `observe`는 `test_controls`, `test_currentness`, `test_design_walkthroughs`, `test_live_observation`, `test_observations`와 함께 쓴다.
- 이 모듈에만 있는 도우미: `routed_requests`.

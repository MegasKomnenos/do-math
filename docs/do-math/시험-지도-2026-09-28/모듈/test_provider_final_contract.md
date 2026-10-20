# test_provider_final_contract

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_provider_final_contract.py` (92행) |
| 클래스 / 테스트 | 1 / 3 |
| 시험 대상 제품 코드 | `do_math/model_runner.py`의 `ModelRunner.run`(비결합일 때만 스키마 파일을 쓰는 97–104행, 결합이면 `provider_evidence_only`로 돌려주는 260–263행), `verified_native_final`; `do_math/codex_worker.py`와 `do_math/claude_worker.py`의 `load_request`, `build_argv`; `do_math/control_transport.py`의 `ControlTransport.issue`; `do_math/execution_profiles.py`의 `build_profiles`, `prepare_prompt`, `prompt_seal`; `do_math/engine.py`의 `_collect_submitted_result`; `do_math/claude_stream.py`의 `parse_stream`; `do_math/claude_adapter.py`의 `ClaudePrintAdapter.parse_response`, `validate_final`(기반 `LocalCLIAdapter`) |
| 사용하는 픽스처 모듈 | `provider_fixtures`의 `Adapter`, `runner_with`, `PROFILE_CONFIG`; `research_fixtures`의 `dispatched_launch`, `bare_engine`(둘 다 테스트 안에서 늦게 import) |
| 격리 표지 | 없음 |
| 시작 상태 | 시험 1은 네 단 밖(실제 `ModelRunner`와 수집기 대역 `Adapter`, 실제 `ControlTransport` 파일). 시험 2는 저장소 없는 `bare_engine`. 시험 3은 1단(파서와 어댑터 메서드 직접 호출) |

## 목적

모듈 docstring은 "A central draft contract must not become a second provider-final contract."이다. 연구 실행은 제어 전송(`control_binding`)으로 중앙에 초안을 제출하고, 그 제출 스키마는 입력 묶음이 전달한다. 그래서 이런 실행에서는 공급자 CLI의 구조화 최종 응답 스키마(`--output-schema`, `--json-schema`)가 두 번째 계약이 되어서는 안 된다. 제품 좌표는 `model_runner.py`의 주석이다. "Unbound consumers use the structured final response, so only they hand the CLI a schema file. Research binds its full schema to the central draft submission instead; its input bundle preserves that schema." 이 모듈은 세 가지를 지킨다. 결합된 실행에는 CLI 스키마가 전달되지 않는다. 제출 없이 끝난 공급자 종료는 연구 결과가 아니다. Claude의 텍스트 최종 응답은 프로토콜 검사를 유지한 채 바이트까지 같아야 한다.

## 모듈 수준 요소

- 행 9: `sys.path.insert(0, str(Path(__file__).resolve().parents[1]))`로 `scripts/` 폴더를 경로 앞에 넣는 공통 머리다.
- 행 91–92: 직접 실행하면 `unittest.main()`을 부른다.

## ProviderFinalContractTests (행 16–88)

`unittest.TestCase`를 그대로 상속한다. 표지, 클래스 속성, 훅, 도우미가 없다.

### `test_bound_draft_schema_stays_local_and_unbound_final_keeps_its_schema` (행 17–61)
- 성질: 제어 전송에 결합된 실행은 작업자 요청과 CLI 인자에 출력 스키마를 싣지 않고 공급자 증거만 수집한다. 결합되지 않은 실행은 전체 출력 스키마를 스키마 파일과 CLI 플래그로 전달한다. 이 규칙은 두 공급자에 똑같이 적용된다.
- 준비: 출력 스키마는 `ids`(문자열 배열, `uniqueItems: True`)를 필수로 하는 닫힌 객체다. `subTest(provider=model, bound=bound)`로 네 경우를 돈다. 공급자는 `('codex', codex_worker, 'gpt-6-astra', '--output-schema')`와 `('claude', claude_worker, 'claude-opus-5', '--json-schema')` 둘이고, 각각 `bound`가 참·거짓인 경우를 본다. 경우마다 다음을 준비한다.
  - 임시 폴더 아래에 `workspace`를 만든다. `PROFILE_CONFIG` 사본의 세 등급을 모두 그 모델로, `session_limits`를 `{'work': {model: 3}}`로 둔다.
  - `build_profiles`에서 `research_work` 프로필 하나를 고른다. `prepare_prompt('Use the provided draft schema.', profile)`로 프롬프트를 만든다.
  - 결합 경우에는 `ControlTransport(root / 'transport').issue('EX-final', 'GR-final', workspace=workspace)`로 실제 결합을 발급한다. 비결합 경우는 `None`이다.
  - 수집기 대역 `Adapter`는 결과 `output_collected`를 돌려준다. 최종 바이트는 결합이면 JSON이 아닌 `b'Draft submitted.'`, 비결합이면 `b'{"ids":[]}'`다. 대역에는 공급자 이름을 주어 그 공급자의 실제 `worker_options`를 쓰게 한다. `runner_with(adapter, provider)`로 러너에 끼운다.
- 실행: `runner.run(prompt=..., input_seal=prompt_seal(prompt), output_schema=schema, ..., timeout_seconds=60, execution_id='EX-final', profile=profile, control_binding=binding, launch_ticket=dispatched_launch('EX-final', profile))`. 이어서 증거 폴더의 `request.json`을 그 공급자의 실제 `worker.load_request`로 읽고 `worker.build_argv(request)`로 CLI 인자를 만든다.
- 단언:
  - 요청에 `output_schema_path`가 있는지와 인자에 공급자 플래그가 있는지가 모두 `not bound`와 같다.
  - `evidence/output.schema.json`의 존재가 `not bound`와 같다. 비결합이면 그 파일 내용이 원래 스키마 전체와 같다(`uniqueItems` 포함).
  - 요청의 `control_binding`이 발급한 결합과 같다(비결합이면 `None`).
  - `status`가 `'completed'`다. 결합이면 `output`이 `None`이고 `collection`이 `'provider_evidence_only'`다.
- 대역: `Adapter`(스크립트된 수집 결과), `runner_with`. 작업자의 `load_request`와 `build_argv`, `ControlTransport`는 실제다. 프로세스는 시작하지 않는다.
- 비고: 주석(49–52행)은 이유를 밝힌다. CLI의 스키마 파일은 그것이 제약하는 비결합 최종 응답에만 있고, "the keyword rejected by the actual provider in REAL run009"를 포함한 전체 초안 스키마를 담는다는 것이다. 결합된 실행의 스키마는 입력 묶음을 거쳐 초안 제출에 닿는다. 결합 경우의 최종 바이트가 JSON이 아니어도 `completed`인 것은, 러너가 `control_binding`이 있으면 최종 응답을 파싱하거나 검증하지 않고 `provider_evidence_only`로 돌려주기 때문이다. `claude_worker.load_request`는 스키마 경로도 결합도 없는 요청을 `"an unbound Claude worker requires its structured final schema"`로 거부한다. 그래서 Claude 비결합 경우의 스키마 파일은 작업자 쪽에서도 필수다. `dispatched_launch`는 `launch.ticket`으로 티켓을 만들고, 이 함수는 `windows_job.owner_identity()`로 현재 프로세스의 Windows 신원을 읽는다. 러너의 `validate_start`도 그 신원을 다시 대조하므로, 이 시험은 Windows 호스트를 전제한다.

### `test_unsubmitted_provider_terminal_is_not_a_research_result` (행 63–70)
- 성질: 중앙 제출 의향 없이 공급자 증거만 남긴 종료는 연구 결과로 받아들여지지 않고 실행 실패가 된다.
- 준비: 인자 없는 `bare_engine()`. 결과 `{'status': 'completed', 'output': None, 'collection': 'provider_evidence_only'}`.
- 실행: `engine._collect_submitted_result({}, result, {}, {}, None)`. 실행 레코드가 빈 사전이라 `submission_intent`가 없다.
- 단언: 반환값의 `status`가 `'failed'`, `error_kind`가 `'execution_failure'`, `output`이 `None`이다.
- 대역: 없음(`bare_engine`의 저장소 대역은 이 경로에서 쓰이지 않는다).
- 비고: 제출 의향이 없고 수집이 `provider_evidence_only`이면, 제품은 `verified_native_final`로 원시 최종 응답을 다시 검증하려 한다(`engine.py` 2784–2805행). 결과에 `execution` 증거가 없으므로 `KeyError`가 `ValueError('native completion evidence is missing or malformed')`로 바뀌고, 이것이 `execution_failure`로 잡힌다. 오류 문구는 단언하지 않는다. 따라서 이 시험은 실패의 종류만 고정하고 거부 사유는 고정하지 않는다.

### `test_claude_text_terminal_retains_protocol_checks_and_exact_text` (행 72–88)
- 성질: 스키마 없는 Claude 실행은 텍스트 최종 응답을 받아들이되, 스트림 프로토콜 검사(세션 시작, 종료 사건, 완전한 행)를 그대로 유지하고, 최종 응답이 스트림이 고른 텍스트와 바이트 단위로 같기를 요구한다.
- 준비: 텍스트 `'Submitted Café.'`(결합 문자로 쓴 é). 사건은 둘이다. `system/init`(세션 `session`)과 `result/success`(`is_error=False`, 같은 세션, `result`는 그 텍스트, `num_turns=1`, `usage={}`). 각 사건을 `ensure_ascii=False`로 부호화하고 `\n`으로 끝낸다.
- 실행: `parse_stream(raw)`(기본값 `require_structured_output=True`), `ClaudePrintAdapter('fixture-cli').parse_response(raw, {})`, `adapter.validate_final`을 두 바이트열로, 그리고 `parse_response(raw + b'{', {})`.
- 단언:
  - 기본 `parse_stream`의 `parse_complete`는 거짓이다. 구조화 출력이 요구되는데 결과에 `structured_output`이 없어 `segment_submission_missing`이 기록되기 때문이다.
  - 요청에 `output_schema_path`가 없으므로 어댑터는 `require_structured_output=False`로 파싱한다. 그 결과의 `parse_complete`와 `turn_completed`가 참이고, `structured_output` 키는 없다.
  - `validate_final(parsed, text.encode('utf-8'))`는 `[]`다. 정규화 형태만 다른 `'Submitted Café.'`의 바이트는 `['final_response_mismatch']`다. 곧 유니코드 정규화를 하지 않는 정확한 바이트 비교다.
  - 끝에 줄바꿈 없는 `{`를 덧붙이면 `parse_complete`가 거짓이다(`incomplete_jsonl_line`).
- 대역: 없음. CLI 경로 `'fixture-cli'`는 이름일 뿐 실행되지 않는다.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈:
  - Claude 스트림 파서의 구간 선택, 사용량, 실패 규칙은 `test_claude_stream`과 `test_claude_adapter`가 자세히 본다. 이 모듈은 텍스트 최종 응답 경로와 바이트 비교만 본다.
  - 작업자 요청 필드와 인자 구성은 `test_codex_adapter`(Codex)와 `test_claude_adapter`의 `test_worker_uses_login_stdin_schema_and_only_configured_mcp`(Claude)가 본다.
  - `verified_native_final`이나 `_capture_native_submission`을 원문에서 부르는 시험 모듈은 `test_native_final_submission` 하나다. 증거를 갖춘 원생 최종 응답이 중앙 제출로 받아들여지는 경로는 그쪽 소관이다. `test_execution_profiles`의 `test_native_claude_report_reaches_normal_result_without_scope_expansion`은 결합 없는 러너 경로에서 Claude 수집 결과가 정상 결과가 되는 것만 본다.
  - 제어 전송의 발급과 결합 검증은 `test_control_transport`가 본다.
- 픽스처 의존: `Adapter`와 `runner_with`를 `test_model_runner` 등과 함께 쓴다. `PROFILE_CONFIG`의 소비자는 `test_execution_profiles`, `test_formal_runtime`, `test_host_resources`, `test_observations`, `test_provider_final_contract`, `test_supervisor_recovery`다. `dispatched_launch`는 발급된 실행 티켓의 `phase`를 `'dispatched'`로 바꾼 값이다.
- 이 모듈에만 있는 도우미: 없다.

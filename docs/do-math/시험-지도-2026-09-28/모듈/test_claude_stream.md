# test_claude_stream

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_claude_stream.py` (135행) |
| 클래스 / 테스트 | 1 / 8 |
| 시험 대상 제품 코드 | `do_math/claude_stream.py`의 `parse_stream`, `provider_limit`, `usage_total`; `do_math/claude_adapter.py`의 `ClaudePrintAdapter.validate_final`(기반 `LocalCLIAdapter.final_bytes`); `do_math/file_io.py`의 `strict_json_loads`; `do_math/payloads.py`의 `json_safe`; 스키마 `record_schemas.RECORDS['executions']` |
| 사용하는 픽스처 모듈 | `provider_fixtures.claude_stream`(이름 `stream`으로 import); `record_fixtures.surface_state`(테스트 안에서 늦게 import) |
| 격리 표지 | 없음 |
| 시작 상태 | 1단(파서와 분류기를 바이트 입력으로 직접 호출). 첫 시험만 `surface_state()`가 만든 합성 사전 상태를 스키마 검증의 대상으로 쓴다 |

## 목적

모듈 docstring은 "Invocation boundaries, continuation failures, and native quota evidence."이다. 시험 대상 `claude_stream.py`의 docstring에 따르면, 이 파서는 Claude 원생(native) 호출을 구간(segment)으로 나누어 읽는다. 지원하는 이어짐은 같은 세션의 task-notification 뿐이고, 사건과 제출 바이트의 권위는 원래 JSONL에 있다. 한 구간은 `system/init`에서 시작해 `result`로 끝난다. 파서는 마지막으로 유효한 제출(`structured_output`)을 고르고, 사용량은 구간 카운터의 합으로, 모델 사용 보고는 마지막 누적값으로 따로 집계한다. 이 모듈은 다음 경계를 본다. 구간 경계와 이어짐의 조건, 뒤 구간의 실패나 잘림이 앞의 성공으로 되돌아가지 못한다는 규칙, 엄격한 JSON, 원생 입장 거부만을 공급자 한도로 분류하는 규칙, 종료 뒤 정리 사건의 허용, 그리고 이 메타데이터가 실행 레코드 저장 계약에 맞는지.

## 모듈 수준 요소

- 행 8: `sys.path.insert(0, str(Path(__file__).resolve().parents[1]))`로 `scripts/` 폴더를 경로 앞에 넣는 공통 머리다.
- 행 14 `INIT`: 세션 `"one"`의 `system/init` 사건. 모든 시험에서 구간을 연다.
- 행 15–18 `RESULT`: 세션 `"one"`의 성공 결과. `num_turns=2`, `usage={"input_tokens": 3, "output_tokens": 7}`, `modelUsage={"claude-opus-5": {"outputTokens": 7}}`, `total_cost_usd=.1`, `structured_output={"summary": "computation pending"}`를 갖는다. 첫 구간의 정상 제출이다.
- 행 21–22 `notification(**changes)`: `RESULT`의 깊은 사본에 `origin={"kind": "task-notification"}`을 달고 `changes`를 덮어쓴 결과 사건. 제품이 둘째 구간부터 요구하는 이어짐 표지다. 여러 시험이 쓴다.
- 행 25–28 `noop()`: `num_turns=0`, 사용량 0/0이고 `structured_output`이 없는 task-notification 결과. 작업 없이 끝난 뒤 구간을 흉내 낸다.
- 행 134–135: 직접 실행하면 `unittest.main()`을 부른다.

## StreamTests (행 31–131)

`unittest.TestCase`를 그대로 상속한다. 표지, 클래스 속성, 훅, 도우미가 없다. 모든 입력은 `stream(*events)`(각 사건을 `json.dumps`하고 `\n`으로 끝낸 바이트)로 만든다.

### `test_native_usage_metadata_fits_the_execution_storage_contract` (행 32–53)
- 성질: 파서가 내는 사용량 메타데이터 네 필드는 실행 레코드 스키마에 맞고 JSON 왕복에서 보존되며, 스키마는 그 밖의 필드와 잘못된 모양을 거부한다.
- 준비: `parse_stream(stream(INIT, RESULT))`. `record_fixtures.surface_state()`가 주는 런타임의 실행 `EX-1`. `surface_state`는 거버넌스가 승인된 인스턴스와 기본 설정 프로필, 활동 `AC-1`에 배정된 `research_work` 실행 `EX-1`을 만든다.
- 실행: 파싱 결과에서 `usage_segments`, `model_usage_reported`, `usage_scope`, `reported_models`를 뽑아 `json_safe`로 투영하고, 실행 레코드에 합친다. 그 레코드를 `Draft202012Validator(RECORDS['executions'])`로 검증한다.
- 단언:
  - 파싱 결과의 `turn_completed`가 참이다.
  - 검증이 통과한다. `json.dumps`/`json.loads` 왕복 뒤 네 필드가 투영값과 같다.
  - 등록되지 않은 필드 `unregistered_provider_field`를 더하면 `ValidationError`가 난다.
  - `subTest(key=...)` 네 경우에서 모양이 틀린 값은 모두 `ValidationError`를 낸다. 경우는 `usage_segments={}`, `model_usage_reported=[]`, `usage_scope='unknown'`, `reported_models={}`다.
- 대역: 없음.
- 비고: 스키마 좌표는 `record_schemas/schemas.py` 308–313행이다. 음성 단언은 예외 유형만 보고 메시지는 보지 않는다.

### `test_three_segments_choose_correction_and_separate_usage_scopes` (행 55–69)
- 성질: 세 구간 스트림에서 마지막 구간의 정정 제출이 선택되고, 앞 제출은 대체된 것으로 남는다. 사용량은 구간 카운터의 합이고, 모델 사용 보고와 비용은 마지막 보고값이다. 최종 응답은 선택된 제출과 바이트가 같아야 한다.
- 준비: `corrected`는 `structured_output={"summary": "computation failed; not rerun"}`, `modelUsage` 출력 14, `total_cost_usd=.2`인 notification이다. 스트림은 일곱 행이다. `INIT`, `RESULT`(구간 0), `INIT`, `noop()`(구간 1), `INIT`, `{"type": "assistant", "session_id": "one"}`, `corrected`(구간 2).
- 실행: `parse_stream(...)`. 이어서 `ClaudePrintAdapter("unused").validate_final`을 두 바이트열로 부른다.
- 단언:
  - `turn_completed`가 참이다(실패 메시지는 파싱 결과 전체).
  - `structured_output`이 `corrected`의 것이고, `selected_result.result_line`이 7이며, `superseded_results`가 1개(구간 0의 제출)다.
  - `usage_total`이 `{"input_tokens": 6, "output_tokens": 14}`다. 3+0+3과 7+0+7의 합이며, 누적 `modelUsage`의 14를 더하지 않는다.
  - `model_usage_reported`가 `corrected["modelUsage"]`이고 `total_cost_usd`가 `.2`다.
  - `corrected` 제출의 `json.dumps` 바이트는 `validate_final`이 `[]`다. 옛 `RESULT` 제출의 바이트는 참인 목록(불일치)이다.
- 대역: 없음.
- 비고: 구간 1의 `noop()`는 작업 없는 무보고 이어짐이라 오류를 남기지 않고 선택도 바꾸지 않는다(`claude_stream.py` 155–158행). 구간 2의 `assistant` 사건은 그 구간을 작업 구간으로 만든다.

### `test_trailing_noop_retains_submission_but_new_work_requires_submission` (행 71–80)
- 성질: 제출 뒤 작업 없는 무보고 이어짐은 앞 제출을 유지하지만, 이어진 구간에 작업이 있거나 사용량이 0이 아니면 새 제출이 필요하다.
- 준비: 세 종류의 스트림을 만든다.
  1. `stream(INIT, RESULT, INIT, noop())`.
  2. `subTest(extra=...)`로 `INIT` 뒤, `noop()` 앞에 `{"type": "assistant"}`, `{"type": "user"}`, `{"type": "stream_event"}` 가운데 하나를 끼운다.
  3. 출력 토큰을 1로 바꾼 `noop()`를 쓴다.
- 실행: 각 스트림을 `parse_stream`으로 파싱한다. (2)는 `subTest(extra=...)` 안에서 파싱한다.
- 단언: (1)은 `turn_completed`가 참이고 `selected_result.segment`가 0이다. (2)의 세 경우와 (3)은 모두 `turn_completed`가 거짓이다.
- 대역: 없음.
- 비고: (2)와 (3)의 실패 원인은 제품의 `segment_submission_missing` 오류다. 시험은 `turn_completed`만 보므로 오류 이름은 고정하지 않는다. (2)에 끼운 사건들에는 `session_id`가 없다. 세션 목록은 `session_id`가 있는 사건만 모으므로 세션 불일치는 생기지 않는다.

### `test_later_failure_or_truncation_cannot_fall_back_to_old_success` (행 82–94)
- 성질: 첫 구간의 성공 뒤에 실패, 잘림, 형식 위반이 오면 옛 성공으로 되돌아가 완료를 선언하지 않는다.
- 준비: `bad`는 `subtype="error_during_execution"`, `is_error=True`인 notification이다. `subTest(raw=...)`로 일곱 경우를 본다.
  1. `INIT, RESULT, INIT, bad`: 뒤 구간의 실패.
  2. `INIT, RESULT, INIT`: 끝나지 않은 마지막 구간.
  3. `INIT, RESULT, INIT, notification()`에서 마지막 바이트(`\n`)를 뺀 것: 잘린 마지막 행.
  4. `INIT, RESULT` 뒤에 `{"type":`: 잘린 꼬리.
  5. `INIT, RESULT, RESULT`: init 없는 두 번째 종료.
  6. `INIT, RESULT, INIT, RESULT`: `origin` 없는 이어짐 결과.
  7. `INIT, RESULT`, 세션 `"other"`인 `INIT`, `notification()`: 다른 세션.
- 실행: 각 경우 `parse_stream(raw)`.
- 단언: 모든 경우 `turn_completed`가 거짓이고 결과에 `structured_output` 키가 없다.
- 대역: 없음.
- 비고: 제품의 오류 이름은 차례로 `turn_failed`(오류가 아니라 실패 표지), `terminal_missing`, `incomplete_jsonl_line`, `incomplete_jsonl_line`, `event_after_terminal_without_init`, `unsupported_continuation`, `session_mismatch`다. 시험은 이 이름들을 단언하지 않는다. `structured_output`이 없다는 단언은, 파서가 완료되지 않은 스트림에서는 선택한 제출을 결과에 싣지 않음(`claude_stream.py` 169–174행)을 고정한다.

### `test_duplicate_keys_nonfinite_and_overflow_are_invalid` (행 96–100)
- 성질: 중복 키, 이름 붙은 비유한 상수, 무한대로 넘치는 지수를 담은 행은 파싱을 불완전하게 만든다.
- 준비: `stream(INIT)` 뒤에 세 행 가운데 하나를 붙인다. `{"type":"result","type":"system"}`, `{"type":"result","usage":NaN}`, `{"type":"result","usage":1e999}`.
- 실행: `parse_stream(...)`.
- 단언: 각 경우 `parse_complete`가 거짓이다.
- 대역: 없음.
- 비고: `subTest` 없이 반복한다. 거부는 `file_io.strict_json_loads`(중복 키 훅, 상수 거부, `compact_json_bytes` 재검사)에서 일어나고 파서는 `invalid_jsonl`을 기록한다. 오류 이름은 단언하지 않는다.

### `test_only_native_admission_rejection_is_provider_failure` (행 102–116)
- 성질: 공급자 한도 실패는 마지막 원생 입장 사건이 `rejected`이고 턴이 완료되지 않은 경우에만 인정된다. 초과 사용 표지, 도구 결과 안의 "429" 문구, 완료된 턴은 한도 실패가 아니다.
- 준비: `failure`는 실패로 끝난 `RESULT` 변형이다. `status`가 `"allowed"`, `"allowed_warning"`, `"rejected"`인 `rate_limit_event`를 차례로 만든다. 각 사건에는 `overageStatus="rejected"`, `resetsAt=1789705200`, `rateLimitType="five_hour"`, `unifiedWindows.seven_day`(이용률 1.0, `resetsAt=1789729200`)가 있다.
- 실행: `provider_limit(parse_stream(stream(rate, INIT, failure)))`를 세 상태에 대해 부른다. 이어서 도구 결과 사건(`"429 rejected"` 내용)과 `failure`의 스트림, 그리고 `rate`(마지막 값 `rejected`)와 성공 `RESULT`의 스트림에 대해서도 부른다.
- 단언:
  - `rejected`이면 `retry_at`이 `"2026-09-18T11:00:00+00:00"`이고 `evidence_line`이 1이다.
  - `allowed`와 `allowed_warning`이면 `None`이다.
  - 도구 결과 경우와 성공 경우도 `None`이다.
- 대역: 없음.
- 비고: `retry_at`은 두 창의 재설정 시각 가운데 늦은 쪽인 7일 창의 1789729200(UTC 2026-09-18 11:00)이다. 5시간 창의 1789705200은 04:20이다. 7일 창은 이용률이 1 이상이라 창 목록에 들어간다(`claude_stream.py` 35–38행). `rate_limit_event`는 `init` 앞에 와도 오류가 되지 않는다(104–107행). `evidence_line` 1이 이 사실에 기댄다. 마지막 경우의 `rate`는 반복문에서 마지막으로 만든 `rejected` 사건이다.

### `test_all_reported_models_survive_last_segment_overwrite` (행 118–121)
- 성질: 뒤 구간의 `modelUsage`가 모델 사용 보고를 덮어써도, 보고된 모델 이름의 목록은 모든 구간의 합집합으로 남는다.
- 준비: 첫 결과는 `modelUsage`가 `other-model`인 `RESULT` 변형이다. 둘째 구간은 `claude-opus-5`를 보고하는 `notification()`이다.
- 실행: `parse_stream(stream(INIT, first, INIT, notification()))`.
- 단언: `reported_models`가 `["claude-opus-5", "other-model"]`(정렬)이다.
- 대역: 없음.
- 비고: 이 목록은 러너가 모델 잠금(`claude_only_assigned_model`)을 판정하는 입력이다(`model_runner.py`의 `reported_models` 검사). 시험은 그 연결을 단언하지 않는다.

### `test_native_terminal_cleanup_preserves_partial_submission_and_stop_evidence` (행 123–131)
- 성질: 최종 결과 뒤에 오는 배경 작업 정리 사건(빈 작업 목록, `killed` 갱신, `stopped` 알림)은 완료를 깨지 않고 정리 증거로 보존된다. 다른 상태의 알림은 종료 뒤의 새 사건으로 거부된다.
- 준비: 정리 사건 셋은 `background_tasks_changed`(`tasks=[]`), `task_updated`(`patch.status="killed"`), `task_notification`(`status="stopped"`)이다.
- 실행: `parse_stream(stream(INIT, RESULT, *events))`. 이어서 마지막 알림의 `status`를 `"failed"`와 `"completed"`로 바꾼 스트림을 각각 파싱한다.
- 단언: 첫 스트림은 `turn_completed`가 참이고 `post_result_events`가 3개다. 두 변형은 `turn_completed`가 거짓이다.
- 대역: 없음.
- 비고: 제품 주석(`claude_stream.py` 109–110행)은 Claude 2.1.276이 최종 결과 뒤에 남은 배경 작업의 종료를 보고하며, 이것은 다른 모델 턴이 아니라 정리라고 설명한다. 이름의 "preserves partial submission"은 정리 사건이 붙어도 선택된 제출이 유지된다는 뜻이다. 시험은 그것을 `turn_completed`로만 확인하고 `structured_output`의 값은 보지 않는다.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈:
  - `test_claude_adapter`는 같은 파서를 단일 구간 판정(`claude_adapter.parse_jsonl`)과 어댑터 경계(`ClaudePrintAdapter.parse_response`, `final_bytes`, `validate_final`의 보존 바이트 대조)에서 보고, 작업자 인자와 러너 라우팅도 본다. `ClaudePrintAdapter.collect`는 부르지 않는다. 이 모듈은 파서의 구간 규칙을 순수 함수로 본다.
  - `test_provider_final_contract`의 `test_claude_text_terminal_retains_protocol_checks_and_exact_text`는 스키마 없는 텍스트 최종 응답 경로(`require_structured_output=False`)를 본다. 이 모듈은 모두 기본값(구조화 출력 요구)으로 파싱한다.
  - 공급자 한도가 실행 대기로 이어지는 흐름은 `test_execution_lifecycle`의 `ProviderAdmissionTests`와 `test_execution_profiles`의 `test_provider_wait_is_canonical_and_serializes_retry_probe`가 본다.
- 픽스처 의존: `claude_stream`의 소비자는 `test_claude_adapter`, `test_claude_stream`, `test_execution_profiles`다. 이 모듈은 `provider_fixtures`의 `CLAUDE_INIT`/`CLAUDE_RESULT` 대신 자기 `INIT`/`RESULT`를 둔다. 세션 이름(`"one"`)과 사용량, `modelUsage`, 비용이 다르다. `record_fixtures.surface_state`는 이 모듈에서 저장 스키마 검증의 바탕 레코드로만 쓰인다.
- 이 모듈에만 있는 도우미: `notification`, `noop`.

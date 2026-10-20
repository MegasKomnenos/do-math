# test_model_runner

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_model_runner.py` (127행) |
| 클래스 / 테스트 | 2 / 10 |
| 시험 대상 제품 코드 | `do_math/model_runner.py`의 `ModelRunner.run`(35–280행); 그 안에서 부르는 `codex_adapter._provider_observation`, `observation_transport.decode_observation_row`, `ObservationBatch`, `cli_worker.validate_max_runtime` |
| 사용하는 픽스처 모듈 | `provider_fixtures`의 `Adapter`, `runner_with` |
| 격리 표지 | 없음 |
| 시작 상태 | 네 단 밖. 실제 `ModelRunner`에 스크립트된 수집기 대역 `Adapter`(또는 그 하위 클래스)를 끼우고 임시 폴더를 작업 공간과 증거 폴더로 쓴다. 프로세스와 모델은 시작하지 않는다 |

## 목적

모듈 docstring은 없다. 시험 대상 `do_math/model_runner.py`의 docstring은 "Evidence-producing CLI runners sharing validation and local lifetime handling."이다. `ModelRunner.run`은 요청 파일을 쓰고, 공급자 어댑터로 작업을 시작한다(`start`). 이어서 시작 기록(`on_started`) 뒤에 재개하고(`resume`), 종료를 폴링하면서 표준 출력을 관찰 묶음으로 전달한다(`on_observation`). 정지 요청이나 마감이 오면 멈추고(`stop`), 끝나면 수집 결과(`collect`)를 스키마로 검증해 결과 사전을 만든다. 이 모듈은 두 무리의 성질을 본다. `Tests`는 결과 판정(스키마 통과만 `completed`, 불완전 수집은 실패), 시작 콜백 실패와 시작 전 정지 때 재개하지 않는다는 규칙, 그리고 요청 파일의 내용을 본다. `WithoutDeadlineTests`는 마감 없는 실행의 수명(정상 반환까지 계속, 정지는 따름, 유한 마감은 여전히 정지)과 관찰 스트림 전달의 바이트 정확성을 본다.

## 모듈 수준 요소

- 행 4: `sys.path.insert(0, str(Path(__file__).resolve().parents[1]))`로 `scripts/` 폴더를 경로 앞에 넣는 공통 머리다.
- 행 5: `import do_math.model_runner as runner`. `WithoutDeadlineTests`가 `runner.time`의 `monotonic`과 `sleep`을 `patch.object`로 바꿀 때 이 이름을 쓴다.
- 행 127: 직접 실행하면 `unittest.main()`을 부른다.

## Tests (행 9–43)

`unittest.TestCase`를 그대로 상속한다. 표지, 클래스 속성, 훅이 없다. 원문은 한 칸 들여쓰기를 쓴다.

- `run_with(self, collected)` (행 10–13): 임시 폴더 아래에 작업 공간 `ws`를 만들고, 증거 폴더 `e`는 만들지 않은 채 경로로만 준다. 제품이 증거 폴더가 새것이기를 요구하기 때문이다(`evidence_dir must be new`). 수집 결과가 `collected`인 `Adapter`를 `runner_with`로 codex 칸에 끼운 `ModelRunner`에서 `run`을 부른다. 인자는 `prompt='x'`, `output_schema={'type':'object','required':['x']}`, `model='m'`, `effort='low'`, `timeout_seconds=1`이다. 모델 이름 `'m'`은 `provider_for`에서 `claude:`나 `claude-`로 시작하지 않으므로 codex 공급자로 간다. 프로필과 실행 ID는 주지 않는다. 결과 사전을 돌려준다.

대역 `Adapter`(`provider_fixtures.py`)의 동작은 다음과 같다. `start`는 요청 파일을 읽어 `request`에 두고 고정 핸들 `Execution`(pid 7의 `Job`)을 돌려준다. `resume`은 `resumed=True`를, `stop`은 `stopped=True`를 기록한다. `wait_for_termination`은 언제나 `True`를 돌려준다. `collect`는 스크립트한 결과에 `codex_adapter._provider_observation`으로 계산한 `provider_observation`을 붙인다.

### `test_completed_only_after_schema` (행 14–18)
- 성질: 수집된 최종 응답이 출력 스키마를 통과해야 결과가 `completed`이고, 사용량은 공급자 관찰의 마지막 보고 행에서 온다.
- 준비: `run_with({'result': 'output_collected', 'final': {'raw': b'{"x":1}'}, 'jsonl': {'usage': [{'input_tokens': 1}]}})`.
- 실행: `ModelRunner.run`(도우미를 거쳐).
- 단언: `status`가 `'completed'`이고 `usage`가 `{'input_tokens': 1}`이다.
- 대역: `Adapter`, `runner_with`.
- 비고: 주석(15행)은 수집기의 파싱 결과가 보고마다 사용량 행 하나를 나열한다고 설명하며 `codex_adapter._parse_jsonl`을 가리킨다. `_provider_observation`은 `usage_total`이 없으면 `usage` 목록의 마지막 행을 쓴다(`codex_adapter.py` 347행).

### `test_invalid_output_keeps_parsed_value_and_actionable_schema_error` (행 19–24)
- 성질: 스키마를 어긴 최종 응답은 실패로 끝나지만, 파싱한 값을 결과에 남기고, 어긴 속성을 가리키는 오류를 준다.
- 준비: `run_with({'result': 'output_collected', 'final': {'raw': b'{}'}, 'jsonl': {'usage': {}}})`. 필수 속성 `x`가 없다.
- 실행: `ModelRunner.run`.
- 단언: `status`가 `'failed'`, `error_kind`가 `'output_validation'`, `output`이 `{}`이다. `error` 문자열에 `'x'`가 들어 있다.
- 대역: `Adapter`, `runner_with`.
- 비고: 제품은 스키마 검사 전에 `result["output"] = output`을 먼저 넣고, 검증 오류는 `"output" + 경로 + ": " + 메시지`로 만든다(`model_runner.py` 266–275행). 오류 문구는 `'x'`의 포함만 보므로 느슨하게 고정된다. jsonschema 메시지 `'x' is a required property`가 이 조건을 채운다.

### `test_incomplete_fails` (행 25–27)
- 성질: 수집이 `output_collected`가 아니면 결과는 실패다.
- 준비: `run_with({'result': 'incomplete', 'reasons': ['tail'], 'jsonl': {}})`.
- 실행: `ModelRunner.run`.
- 단언: `status`가 `'failed'`다.
- 대역: `Adapter`, `runner_with`.
- 비고: 제품은 이때 `error`를 이유 목록을 이어 붙인 `"tail"`로 둔다. 대역의 `provider_failure`가 `None`이므로 `error_kind`는 `execution_failure`로 남는다. 두 값 모두 단언하지 않는다.

### `test_callback_failure_does_not_resume` (행 28–33)
- 성질: 시작 기록 콜백 `on_started`가 실패하면 러너는 작업을 멈추고 예외를 다시 던지며, 중단 상태로 시작된 루트 프로세스를 재개하지 않는다.
- 준비: 도우미를 쓰지 않고 직접 준비한다. 스크립트 결과가 빈 사전인 `Adapter({})`와 `runner_with(a)`. `on_started`는 호출되면 생성기 식 `(_ for _ in ()).throw(RuntimeError())`로 `RuntimeError`를 던지는 람다다. `output_schema={}`.
- 실행: `r.run(..., on_started=...)`.
- 단언: `RuntimeError`가 전파된다(유형만 본다). `a.stopped`가 참이다. `a.resumed`가 없거나 거짓이다(실패 메시지 `'a failed start record must not resume the root'`).
- 대역: `Adapter`, `runner_with`.
- 비고: 제품의 `try` 블록에서 `on_started(started)`는 `adapter.resume(execution)`보다 앞에 있다. 예외가 나면 `except`가 `stop`과 종료 대기를 거쳐 다시 던진다(`model_runner.py` 197–230행). 대역의 `collect`는 불리지 않는다.

### `test_pre_start_stop_does_not_resume` (행 34–38)
- 성질: 시작 직후 정지 요청이 이미 서 있으면 러너는 재개하지 않고 멈춘 뒤 `stopped` 결과를 돌려준다.
- 준비: `Adapter({'result': 'incomplete', 'jsonl': {}})`, `runner_with(a)`, `should_stop=lambda: True`.
- 실행: `r.run(...)`.
- 단언: `status`가 `'stopped'`이고, `a.stopped`가 참이며, `a.resumed`가 없거나 거짓이다.
- 대역: `Adapter`, `runner_with`.
- 비고: 제품은 이 경로에서도 `collect`를 불러 `provider_observation`을 결과에 싣고, `error`를 `"stop requested before resume"`으로 둔다. 둘 다 단언하지 않는다.

### `test_scholarly_server_is_written_to_the_immutable_worker_request` (행 39–43)
- 성질: 러너에 준 scholarly 서버 설정은 작업자 요청 파일에 그대로 기록된다.
- 준비: `Adapter({'result': 'output_collected', 'final': {'raw': b'{}'}, 'jsonl': {'usage': {}}})`. `output_schema={'type': 'object'}`, `scholarly_server={'command': 'python', 'args': ['C:/server.py']}`.
- 실행: `r.run(...)`. 대역의 `start`가 요청 파일 `request.json`을 읽어 `a.request`에 둔다.
- 단언: `a.request['scholarly_server']`가 준 값과 같다.
- 대역: `Adapter`, `runner_with`.
- 비고: 이 경로는 고정 프로필 없이 러너 인자로 서버를 준다. 제품은 고정 프로필이 있으면 이 인자를 거부하고 프로필의 `ai.scholarly_server`를 쓴다(`model_runner.py` 70–73행). 그 경로는 이 시험 밖이다. 이름의 "immutable"은 작업자가 시작 뒤 읽는 요청 파일에 값이 기록된다는 뜻이다. 파일이 이후 바뀌지 않는다는 것을 단언하지는 않는다.

## WithoutDeadlineTests (행 44–124)

`unittest.TestCase`를 그대로 상속한다. 표지, 클래스 속성, 훅이 없다.

- `run_observed(self, *, timeout=None, stop=False)` (행 45–62): 가짜 단조 시계 `clock=[0.0]`을 둔다. 지역 대역 클래스 `LiveAdapter(Adapter)`는 `wait_for_termination`이 불릴 때마다 `polls`를 1 늘리고 시계를 10,000초 앞당긴다. 그리고 `stopped`이거나 `polls >= 9`일 때 `True`를 돌려준다. 이 대역을 수집 결과 `output_collected`(최종 `b'{}'`)와 함께 `runner_with`로 끼운다. `runner.time.monotonic`을 가짜 시계로, `runner.time.sleep`을 아무것도 하지 않는 대역으로 `patch.object`한다. 그 위에서 `run`을 `timeout_seconds=timeout`, `should_stop=lambda: stop and adapter.polls >= 4`로 부른다. 작업 공간은 임시 폴더 자체이고 증거 폴더는 그 아래 `evidence`다. `(result, adapter)`를 돌려준다.

### `test_observation_burst_preserves_order_and_split_utf8_tail` (행 64–108)
- 성질: 한 번의 읽기 한도(1 MiB)를 넘는 관찰 폭주도 행 순서와 바이트 좌표를 잃지 않고 전달된다. UTF-8 문자가 두 쓰기 사이에서 잘려도 온전한 행으로 복원된다. 끝에 줄바꿈이 없는 마지막 행은 작업이 끝난 뒤에 전달된다.
- 준비:
  - `expected`는 `{"type": "item.updated", "index": i, "text": "x"*960}` 2,000행(약 2 MB)이다. `last`는 `index` 2000에 텍스트 `"가"`인 행이다.
  - 첫 쓰기 `first`는 `expected` 각 행을 `\r\n`으로 끝낸 것, 빈 줄 `\r\n` 하나, 그리고 `last`의 UTF-8 부호화를 `"가"`의 첫 바이트 바로 뒤에서 자른 앞부분이다.
  - 두 번째 쓰기 `second`는 `last`의 나머지, `\r\n`, 파싱할 수 없는 행 `not-json\r\n`, 줄바꿈 없는 조각 `{"type":`이다.
  - 지역 대역 `BurstAdapter(Adapter)`의 `wait_for_termination`은 첫 폴링에서 요청의 `stdout_path`에 `first`를 쓰고, 두 번째 폴링에서 `second`를 덧붙인다. 네 번째 폴링부터 `True`를 돌려준다.
  - `runner.time.sleep`을 대역으로 바꾼다. 단조 시계는 바꾸지 않는다.
- 실행: `worker.run(prompt="fixture", ..., model="fixture", timeout_seconds=None, on_observation=observed.append)`. 러너는 폴링 사이에 `observe()`로 최대 1 MiB씩 읽는다. 작업이 끝나면 남은 바이트를 모두 읽고, 버퍼에 남은 미종결 행을 `observe(final=True)`로 전달한다.
- 단언:
  - `status`가 `'completed'`다.
  - 모든 묶음의 `events` 가운데 `item.updated` 행이 `[*expected, last]`와 순서까지 같다. `last`의 `"가"`가 온전히 복원되었다는 뜻이다.
  - `unparsed_observation` 행은 정확히 둘이다. 바이트 수는 `len(b"not-json\r")`와 `len(b'{"type":')`다. `decode_observation_row`는 끝의 `\n`만 떼고 센다. 주석(97행)은 작업이 끝난 뒤 러너가 줄바꿈 없는 마지막 행도 전달한다고 말한다.
  - 마지막 묶음의 `end_offset`이 `len(first) + len(second)`다.
  - 모든 묶음의 `rows`를 이으면 원 바이트에서 빈 줄 하나를 뺀 것(`(first + second).replace(b"\r\n\r\n", b"\r\n")`)과 같다. 빈 행은 행으로 세지 않는다.
  - 행 번호 `batch.first_row + i`가 0부터 끊김 없이 이어진다.
  - 모든 묶음에서 `offsets[i]`의 바이트 범위가 `rows[i]`와 정확히 같다.
- 대역: `BurstAdapter`(스크립트된 표준 출력 쓰기), `patch.object(runner.time, "sleep")`.
- 비고: 제품 `observe`는 한 번에 `1024 * 1024`바이트를 읽는다(`model_runner.py` 165행). 따라서 2 MB 넘는 첫 쓰기는 루프 안의 읽기와 종료 뒤 드레인 루프(`offset < stdout_path.stat().st_size`) 여러 번에 걸쳐 전달되며, 이 시험은 그 이음매에서 행이 섞이지 않음을 본다. 공개 경로도 엔진도 없다.

### `test_long_running_work_keeps_running_until_its_normal_return` (행 110–114)
- 성질: 마감 없는 작업은 가짜 시계로 아주 오래(폴링당 10,000초) 지나도 멈춰지지 않고 정상 반환까지 간다.
- 준비: `run_observed()`(마감 없음, 정지 없음).
- 실행: `ModelRunner.run`이 아홉 번째 폴링까지 돈다.
- 단언: `status`가 `'completed'`이고, `adapter.stopped`가 거짓이며, 요청의 `max_runtime_seconds`가 `None`이다.
- 대역: `LiveAdapter`, 단조 시계와 `sleep` 패치.
- 비고: 작업자 요청의 `max_runtime_seconds`가 `None`이라는 단언은, 러너뿐 아니라 작업자 쪽에도 실행 시간 한도가 넘어가지 않음을 고정한다.

### `test_work_without_a_deadline_still_obeys_stop` (행 116–119)
- 성질: 마감이 없어도 정지 요청은 따른다.
- 준비: `run_observed(stop=True)`. 정지 판단은 폴링이 네 번 이상일 때 참이 된다. 따라서 시작 전 정지 점검(폴링 0)은 통과하고 재개 뒤에 멈춘다.
- 실행: `ModelRunner.run`.
- 단언: `status`가 `'stopped'`이고 `adapter.stopped`가 참이다.
- 대역: `LiveAdapter`, 시계와 `sleep` 패치.
- 비고: 수집 결과는 `output_collected`지만 `stopped` 판정이 우선한다(`model_runner.py` 249–251행). 따라서 정상 출력이 있어도 결과가 `completed`로 바뀌지 않는다는 것도 함께 확인된다.

### `test_a_finite_call_deadline_still_stops_the_runner` (행 121–124)
- 성질: 유한한 호출 마감을 주면 러너는 마감에 이르러 작업을 멈춘다.
- 준비: `run_observed(timeout=1)`. 재개 시각의 가짜 시계에 1초를 더한 것이 마감이다. 첫 폴링에서 시계가 10,000초 앞당겨진다.
- 실행: `ModelRunner.run`.
- 단언: `status`가 `'stopped'`이고 `adapter.stopped`가 참이다.
- 대역: `LiveAdapter`, 시계와 `sleep` 패치.
- 비고: 세 테스트는 같은 도우미를 쓰며 인자만 다르다. 셋째 테스트의 정지 원인은 정지 요청이 아니라 마감이다(`stop=False`).

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈:
  - `test_execution_profiles`는 고정 프로필을 준 `ModelRunner.run`의 경로를 본다. 요청 고정, 입력 봉인 대조, 프로필 도구, 구조적 시작 실패 증거가 여기에 든다. 이 모듈은 프로필 없는 경로만 쓴다.
  - `test_provider_final_contract`는 같은 `Adapter`와 `runner_with`로 제어 결합(`control_binding`)이 있을 때 스키마 파일을 쓰지 않는 경로를 본다.
  - `test_live_observation`(docstring "Live observation of running executions: collected events, self-check obligations and observation rules.")도 `Adapter`와 `runner_with`를 쓴다. 이 모듈의 폭주 시험은 관찰 묶음을 만드는 러너 쪽을 본다.
  - 마감 없는 실행 창의 공개(`execution_window.publish`에 마감 `None`)와 마감 예고는 `test_execution_window`가 순수 함수로 본다. 고정 프로필에서 작업 역할만 `timeout_seconds=None`을 받는다는 러너 규칙은 `test_execution_profiles`의 `test_work_has_no_deadline_and_operations_keep_their_call_window`가 본다. 엔진이 작업 역할에 `call_deadline=None`을 주는 분기(`engine.py` 3250–3251행)는 이 모듈도 그 두 모듈도 직접 단언하지 않는다. 이 모듈은 러너가 `timeout_seconds=None`을 받았을 때의 동작만 본다.
- 픽스처 의존: `Adapter`와 `runner_with`의 소비자는 `test_claude_adapter`, `test_execution_profiles`, `test_live_observation`, `test_model_runner`, `test_provider_final_contract`, `test_role_input`이다(`consumers.json`).
- 이 모듈에만 있는 도우미: `Tests.run_with`, `WithoutDeadlineTests.run_observed`, 지역 대역 `LiveAdapter`와 `BurstAdapter`.

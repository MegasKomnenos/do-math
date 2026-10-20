# provider_fixtures

| 항목 | 값 |
|---|---|
| 원문 | `.claude/skills/do-math/scripts/tests/provider_fixtures.py` (236행) |
| 정의 수 | 함수 11, 클래스 5(`Job`, `Execution`, `Adapter`, `FakeJob`, `HTTPFixtureHandler`), 상수 5(`CLAUDE_INIT`, `CLAUDE_RESULT`, `PROVIDER_MODEL`, `PROVIDER_LIMIT_FAILURE`, `PROFILE_CONFIG`) |
| 이 모듈을 쓰는 시험 모듈 | 22개(`consumers.json` 기준). 다른 픽스처 모듈은 이 모듈을 import하지 않는다 |
| 이 모듈이 부르는 다른 픽스처 | `research_fixtures.current_state`(`provider_repository` 안에서 지연 import) |

## 목적

모듈 docstring(행 1–27)은 이 모듈을 "공급자(provider), 호스트 프로세스, 외부 서비스의 경계에 선 대역"이라고 규정한다. 이 모듈에는 모델, Lean 컴파일러, 네트워크 서비스를 스스로 띄우는 정의가 하나도 없다. 대역 하나하나는 제품이 프로세스 바깥의 무언가에 닿는 자리에 선다. docstring은 대역을 여섯 영역으로 나눈다.

- 모델 러너: `Adapter`와 `mock_adapter`, 프로세스 핸들 `Job`·`Execution`, 그리고 `FakeJob`.
- Claude 스트림: `claude_stream`, `CLAUDE_INIT`, `CLAUDE_RESULT`.
- 세션 슬롯 위의 공급자 한도: `provider_repository`, `admit`, `report`, `finish`, `transact`, `instant`.
- 실행 프로필: `PROFILE_CONFIG`와 `host_capacity_fixture`.
- Lean: `actual_command`.
- HTTP: `HTTPFixtureHandler`.

대역마다 제품이 그대로 남기는 부분이 뚜렷하다. `Adapter`는 공급자의 실제 `worker_options`와 실제 `_provider_observation` 계산을 쓴다. `runner_with`는 실제 `ModelRunner`를 만든다. `admit`·`report`·`finish`는 실제 `SessionSlots`, `execution_lifecycle`, `activities` 함수를 부른다. `host_capacity_fixture`는 실제 `execution_profiles`와 `governance.preserve_source`로 제약과 프로필을 만든다. 대역이 바꾸는 것은 외부 프로세스의 출현(시작, 대기, 수집)과 공급자가 보고하는 원자료뿐이다.

## 구성

| 무리 | 정의 | 부르는 것 |
|---|---|---|
| 모델 러너 대역 | `Job`, `Execution`, `Adapter`, `mock_adapter`, `runner_with`, `FakeJob` | `Adapter.__init__`와 `mock_adapter` → `do_math.claude_adapter.provider_adapter(provider, 'fake').worker_options`; `Adapter.start` → `Execution`(→ `Job`); `Adapter.collect` → `do_math.codex_adapter._provider_observation`; `runner_with` → `do_math.model_runner.ModelRunner` |
| Claude 스트림 | `claude_stream`, `CLAUDE_INIT`, `CLAUDE_RESULT` | `json.dumps`만 쓴다 |
| 공급자 한도와 세션 슬롯 | `PROVIDER_MODEL`, `PROVIDER_LIMIT_FAILURE`, `instant`, `provider_repository`, `admit`, `report`, `finish`, `transact` | `provider_repository` → `research_fixtures.current_state`, `execution_profiles.build_profiles`, `ResearchRepository.initialize`; `admit` → `instant`, `execution_lifecycle.create_execution`, `SessionSlots.acquire`, `activities.open_activity`·`assign_execution`; `report` → `SessionSlots.provider_result_from_run`; `finish` → `instant`, `SessionSlots.release`, `execution_lifecycle.transition_execution`, `activities.finish_activity`; `transact` → `ResearchRepository.writer_lock`·`load`·`save_with_state`, `SessionSlots` |
| 실행 프로필 | `PROFILE_CONFIG`, `host_capacity_fixture` | `host_capacity_fixture` → `PROFILE_CONFIG`, `execution_profiles.build_profiles`·`host_constraint`·`with_host_resources`, `governance.preserve_source`, `platform.node` |
| Lean | `actual_command` | `do_math.formal.portable_bin`, `toolchain_root` |
| HTTP | `HTTPFixtureHandler` | `http.server.BaseHTTPRequestHandler` |

`admit`, `report`, `finish`의 첫 인자는 모두 `SessionSlots`다. 시험은 이 셋을 보통 `transact(repository, lambda slots, instance, runtime: ...)`의 `operation`으로 넘긴다. 그러면 한 연산이 writer lock 아래에서 적재, 적용, 저장을 한 번에 치른다.

## 모델 러너 대역

### `Job` (행 44–50)
- 종류: 대역(프로세스 핸들).
- 하는 일과 반환값: Windows Job 핸들을 흉내 낸다. 클래스 속성 `pid = 7`, `creation_filetime = 9`는 프로세스 식별값이다. 제품이 핸들에서 읽는 식별자에 고정값을 준다.
- 메서드:
  - `terminate` (행 48): `self.terminated = True`를 기록한다. 실제 프로세스를 끝내지 않는다.
  - `close` (행 50): `self.closed = True`를 기록한다.
- 부작용: 없음. 대역 안의 검사도 없다.
- 의존: 없음.
- 소비자: 모듈 안에서만 사용. `Execution.job`의 값으로 한 번 만들어지며(행 54), `Adapter.start`가 돌려주는 `Execution`을 거쳐 제품의 러너에 닿는다. `consumers.json`에 항목이 없다.
- 비고: 인스턴스가 `Execution`의 클래스 속성이므로 모든 `Execution()`이 같은 `Job` 객체를 공유한다. 따라서 한 시험에서 `terminate`나 `close`가 남긴 `terminated`·`closed` 속성은 같은 프로세스의 다른 시험에서도 보인다.

### `Execution` (행 53–55)
- 종류: 대역(실행 핸들).
- 하는 일과 반환값: `Adapter.start`가 돌려주는 실행 핸들이다. 클래스 속성 `job = Job()`과 `request_sha256 = "a"`만 가진다. 메서드는 없다.
- 부작용: 없음.
- 의존: `Job`.
- 소비자: 모듈 안에서만 사용. 호출자는 `Adapter.start`(행 67)다. `consumers.json`에 항목이 없다.

### `Adapter` (행 58–80)
- 종류: 대역(공급자 수집기, scripted collector).
- 하는 일과 반환값: 실제 `ModelRunner`의 어댑터 자리에 들어가, 미리 준 결과를 수집 결과로 돌려준다. docstring은 "worker request 필드는 그 공급자의 실제 것"이라고 밝힌다. 제품 그대로인 부분은 두 가지다. 하나는 `worker_options`로, 공급자 어댑터가 실제로 만든다. 다른 하나는 `provider_observation`으로, 실제 codex 어댑터의 함수가 계산한다. 바뀌는 부분은 프로세스 시작, 재개, 종료 대기, 정지, 수집 원자료다.
- 메서드:
  - `__init__` (행 60–63): `result`(수집 결과 사전)와 `provider`(기본 `'codex'`)를 받는다. `done=False`, `stopped=False`로 시작하고, `do_math.claude_adapter.provider_adapter(provider, 'fake').worker_options`를 `self.worker_options`에 담는다. `provider_adapter`는 알려지지 않은 공급자에 `ValueError("unsupported profile provider")`를 던지므로, 공급자 이름이 틀리면 생성 단계에서 실패한다.
  - `start` (행 65–67): 첫 위치 인자를 요청 파일 경로로 보고 `read_text(encoding='utf-8')`로 읽어 JSON으로 풀어 `self.request`에 담는다. 그다음 `Execution()`을 돌려준다. 첫 인자가 경로가 아니거나 JSON이 아니면 예외가 난다. 이것이 이 대역의 유일한 입력 검사이고, 제품이 실제로 봉인된 요청 파일을 썼는지를 간접적으로 확인한다.
  - `resume` (행 69): `self.resumed = True`를 기록한다.
  - `wait_for_termination` (행 71): `self.done = True`를 기록하고 `True`를 돌려준다. 곧 종료 대기가 언제나 즉시 성공한다.
  - `stop` (행 73): `self.stopped = True`를 기록한다.
  - `collect` (행 75–78): `{'provider_observation': _provider_observation(self.request, self.result.get('jsonl', {}), None), **self.result}`를 돌려준다. 주석(행 76)은 "실제 수집기는 모든 결과에 공급자 사실을 싣는다. 그와 같이 도출한다"고 설명한다. `start`가 먼저 불리지 않았으면 `self.request`가 없어 `AttributeError`가 난다. `self.result`에 `provider_observation` 키가 있으면 그것이 계산값을 덮어쓴다.
  - `provider_failure` (행 80): 언제나 `None`을 돌려준다. 곧 공급자 한도 실패를 보고하지 않는다.
- 부작용: 요청 파일을 읽을 뿐 쓰지 않는다. 프로세스를 만들지 않는다.
- 의존: `do_math.claude_adapter.provider_adapter`, `do_math.codex_adapter._provider_observation`, `Execution`.
- 소비자: `test_claude_adapter`, `test_execution_profiles`, `test_live_observation`, `test_model_runner`, `test_provider_final_contract`, `test_role_input`.

### `mock_adapter(provider='codex')` (행 83–87)
- 종류: 대역(`unittest.mock.Mock`).
- 하는 일과 반환값: `worker_options` 하나만 실제 공급자 어댑터에서 가져온 `Mock`을 돌려준다. 나머지 속성과 메서드는 모두 `Mock`의 자동 속성이다. 호출 기록을 단언하려는 시험에 쓴다.
- 부작용: 없음.
- 의존: `do_math.claude_adapter.provider_adapter`.
- 소비자: `test_execution_profiles`.

### `runner_with(adapter, provider='codex')` (행 90–93)
- 종류: 함수.
- 하는 일과 반환값: 제품 `do_math.model_runner.ModelRunner()`를 만들고 `adapters[provider]`를 `adapter`로 바꿔 돌려준다. 러너의 나머지 동작(요청 구성, 수집 판정, 관측)은 제품 그대로다.
- 부작용: 없음.
- 의존: `do_math.model_runner.ModelRunner`.
- 소비자: `test_claude_adapter`, `test_execution_profiles`, `test_live_observation`, `test_model_runner`, `test_provider_final_contract`, `test_role_input`.

### `FakeJob` (행 96–100)
- 종류: 대역(Job 관측).
- 하는 일과 반환값: docstring은 "`inspect`가 `state`를 보고하는 job"이다. 생성 때 받은 값을 그대로 돌려준다.
- 메서드:
  - `__init__` (행 98): `state`를 저장한다.
  - `inspect` (행 100): 저장한 `state`를 돌려준다. 검사는 없다.
- 부작용: 없음.
- 의존: 없음.
- 소비자: `test_codex_adapter`, `test_execution_profiles`.
- 비고: 모듈 docstring(행 9–10)은 "고정된 `JobInspection`으로 답한다"고 쓴다. 코드는 형을 검사하지 않고 생성 때 받은 값을 그대로 돌려준다. 소비자는 모두 `JobInspection`을 넘기므로 docstring은 실제 사용과 맞는다(`test_codex_adapter` 행 182, 197, 210, `test_execution_profiles` 행 796).

## Claude 스트림

### `claude_stream(*events)` (행 103–104)
- 종류: 함수.
- 하는 일과 반환값: 사건 사전들을 각각 `json.dumps(...).encode() + b"\n"`으로 바꿔 이어 붙인 `bytes`(JSONL)를 돌려준다. Claude CLI의 stdout 원자료 자리에 쓴다.
- 부작용: 없음.
- 의존: 없음.
- 소비자: `test_claude_adapter`, `test_claude_stream`, `test_execution_profiles`.

- `CLAUDE_INIT` (행 107): 성공한 실행의 첫 행. `type="system"`, `subtype="init"`, `session_id="session-one"`. 소비자: `test_claude_adapter`, `test_execution_profiles`.
- `CLAUDE_RESULT` (행 108–110): 성공한 실행의 마지막 행. `type="result"`, `subtype="success"`, `is_error=False`, 같은 `session_id`, `structured_output={"ok": True}`, `usage={"input_tokens": 7, "output_tokens": 3}`. 소비자: `test_claude_adapter`, `test_execution_profiles`.

## 공급자 한도와 세션 슬롯

- `PROVIDER_MODEL` (행 113): `"claude-opus-5"`. `provider_repository`가 세 등급(`low`, `medium`, `high`) 모두에 이 모델을 배정하고 `work` 세션 한도를 이 모델에 3으로 둔다. 소비자: `test_provider_wait`.
- `PROVIDER_LIMIT_FAILURE` (행 114–115): 공급자 한도 실패 기록. `kind="provider_limit"`, `provider="claude"`, `retry_at=None`, `evidence_ref="synthetic-provider-limit.json"`, `limit_windows=[]`. `report(..., failure=PROVIDER_LIMIT_FAILURE)`로 넘긴다. 소비자: `test_provider_recovery`, `test_provider_wait`.

### `instant(seconds)` (행 118–119)
- 종류: 함수.
- 하는 일과 반환값: 에포크 초를 UTC `datetime`으로 바꿔 ISO 문자열로 돌려준다. 기록이 쓰는 시각 형식에 맞추는 변환이다.
- 부작용: 없음.
- 의존: 없음.
- 소비자: `test_provider_wait`. 모듈 안에서는 `admit`과 `finish`가 쓴다.

### `provider_repository(root)` (행 122–134)
- 종류: 함수(Git 저장소 시작 상태).
- 하는 일과 반환값: `root`의 Git 저장소에 준비된(ready) 인스턴스 하나를 초기화하고 그 `ResearchRepository`를 돌려준다. 설정은 `DEFAULT_CONFIG` 사본에 `scholarly_enabled=False`, 세 등급 모두 `PROVIDER_MODEL`, `session_limits={"work": {PROVIDER_MODEL: 3}}`(작업 슬롯 3개)를 더한 것이다. 인스턴스는 `research_fixtures.current_state`에 `id`(새 `RI` ID), `workspace`, `config`, `build_profiles(config)`의 결과를 더한다. 런타임은 `status="ready"`와 빈 `executions`, `activities`, `reservations`, `provider_waits`다.
- 부작용: `ResearchRepository(root, iid).initialize(instance, runtime)`가 `root`에 상태를 커밋한다. `root`는 이미 Git 저장소여야 한다(docstring). 이 함수는 저장소를 만들지 않는다.
- 의존: `research_fixtures.current_state`, `do_math.repository.new_id`, `ResearchRepository`, `build_profiles`.
- 시작 상태의 단: 네 단 밖. 공개 `initialize`를 거치지 않고, 최소 상태 계약을 통과하는 합성 상태를 실제 Git 저장소에 직접 게시한다.
- 소비자: `test_provider_recovery`, `test_provider_wait`.

### `admit(slots, instance, runtime, identifier, role="research_work", current=100)` (행 137–150)
- 종류: 함수.
- 하는 일과 반환값: 실행 하나를 등록하고 입장시킨다. docstring은 "작업 역할(모델 슬롯) 또는 maintenance 같은 운영 역할(슬롯 없음)을 입장시킨다"고 밝힌다. `role`의 마지막 프로필 참조(`role_profile_refs[role][-1]`)로 프로필을 고르고, 활동 ID `"AY-" + identifier`로 AI 실행을 만든다(`create_execution`, `created_at=instant(current)`). 이어 `execution["role"] = role`을 적고 `slots.acquire(...)`를 부른다. 슬롯을 얻지 못하면 `False`를 돌려주고 활동을 열지 않는다. 얻으면 활동을 열고(`open_activity`) 실행을 배정한(`assign_execution`) 뒤 `True`를 돌려준다.
- 부작용: `slots`와 `runtime`을 제자리에서 바꾼다. 저장은 하지 않는다(`transact`가 저장한다).
- 의존: `instant`, `execution_lifecycle.create_execution`, `profile_ref`, `SessionSlots.acquire`, `activities.open_activity`, `activities.assign_execution`.
- 소비자: `test_provider_recovery`, `test_provider_wait`.

### `report(slots, instance, identifier, current, failure=None, **config)` (행 153–158)
- 종류: 함수.
- 하는 일과 반환값: 합성 러너 결과를 적용한다. `failure`가 있으면 `{"status": "failed", "error_kind": "provider_limit", "failure": failure}`를, 없으면 `{"status": "completed"}`를 만든다. 이것을 `slots.provider_result_from_run(identifier, result, {**instance["config"], **config}, current_time=current)`에 넘기고 그 반환값을 돌려준다. `config` 키워드는 재시도 간격 같은 설정을 이 호출에서만 덮어쓴다.
- 부작용: `slots`가 가리키는 런타임을 바꾼다.
- 의존: `SessionSlots.provider_result_from_run`.
- 소비자: `test_provider_recovery`, `test_provider_wait`.

### `finish(slots, runtime, identifier, current, *, close_activity=True)` (행 161–172)
- 종류: 함수.
- 하는 일과 반환값: 실행을 해제하고 끝낸다. `slots.release(identifier)`가 거짓이면 `AssertionError("test execution without an acknowledged process did not settle")`를 던진다. 이것이 대역 안의 검사다. 해제에 성공하면 실행을 `stopping`, 이어서 `ended`로 전이시킨다. `ended`의 `outcome`은 `"start_failed"`, `disposition`은 `{"kind": "synthetic_provider_observation"}`이다. `close_activity`가 참이면 소유 활동을 `finish_activity`로 닫는다. 이때 `unresolved`에 "No model process was started in this allocator fixture"를 남긴다. 반환값은 없다.
- 부작용: `runtime`과 `slots`를 바꾼다.
- 의존: `instant`, `SessionSlots.release`, `execution_lifecycle.transition_execution`, `activities.finish_activity`.
- 소비자: `test_provider_recovery`, `test_provider_wait`.

### `transact(repository, operation)` (행 175–181)
- 종류: 함수.
- 하는 일과 반환값: `repository.writer_lock()` 아래에서 `load()`로 머리·인스턴스·런타임을 읽고 `SessionSlots(runtime, instance)`를 만든다. 그다음 `operation(slots, instance, runtime)`을 부르고 `save_with_state(head, instance, runtime)`로 저장한 뒤 `operation`의 반환값을 돌려준다.
- 부작용: 실제 파일 잠금과 Git 커밋. 저장 결과의 새 머리는 버린다(`[0]`을 읽기만 한다).
- 의존: `ResearchRepository.writer_lock`, `load`, `save_with_state`, `SessionSlots`.
- 소비자: `test_provider_wait`.

## 실행 프로필

- `PROFILE_CONFIG` (행 184–193): `build_profiles`에 넘길 완결된 프로필 설정. `tier_models`, `role_tiers`, `session_limits`는 `model_policy.MODELS`, `ROLE_TIERS`, `LIMITS`의 사본이다. 그 밖의 값은 다음과 같다: `effort="medium"`, `max_input_bytes=500000`, `call_timeout_seconds=600`, `operator_timeout_seconds=5400`, `operator_effort="high"`, `observation_mode="event_driven"`, `observation_interval_seconds=300`, `finish_notice_seconds=60`, `scholarly_enabled=True`, `scholarly_server=None`, `claude_only_assigned_model=False`, `provider_retry_initial_seconds=300`, `provider_retry_max_seconds=7200`. 소비자: `test_execution_profiles`, `test_formal_runtime`, `test_host_resources`, `test_observations`, `test_provider_final_contract`, `test_supervisor_recovery`.

### `host_capacity_fixture()` (행 196–219)
- 종류: 함수.
- 하는 일과 반환값: `(instance, selected, constraint)`를 돌려준다. `instance`는 `build_profiles(PROFILE_CONFIG)`의 결과에 다음을 더한 것이다. 먼저 사용자 출처의 `governance_sources` 하나(`GS-host-test`, 한도 문구를 담은 임시 승인)를 둔다. 다음으로 호스트 제약 `constraint`를 만든다. 제약의 `host_id`는 `platform.node()`, 한도는 jobs 4·메모리 512 MiB·CPU 8000 basis points, 제어 예비분은 jobs 1·128 MiB·2000이다. 이 제약을 `capacity_constraints`에 넣고 `host_capacity_ref`로 가리킨다. `selected`는 `research_work`, `recovery`, `formal_check` 세 역할마다 원래 프로필을 `with_host_resources`로 바꾼 새 판이다. 새 판은 jobs 1·128 MiB·CPU 2000을 예약한다. 새 판은 `execution_profiles`에도 추가되며, 원래 판은 그대로 남는다.
- 부작용: 없음(순수 계산).
- 의존: `PROFILE_CONFIG`, `execution_profiles.build_profiles`, `host_constraint`, `with_host_resources`, `governance.preserve_source`, `platform.node`.
- 시작 상태의 단: 1단(순수 사전).
- 소비자: `test_formal_runtime`, `test_host_resources`, `test_machine_scheduling`, `test_session_scheduler`.

## Lean

### `actual_command()` (행 222–224)
- 종류: 함수.
- 하는 일과 반환값: 실제 Lean 컴파일러 명령을 원소 하나짜리 목록으로 돌려준다. 환경 변수 `DO_MATH_KNOWLEDGE_TEST_LEAN`이 있으면 그 값을 쓰고, 없으면 `portable_bin(toolchain_root()) / 'lean.exe'`를 쓴다. 주석(행 223)은 "명시적인 휴대용 컴파일러 범위이며 Mathlib 준비 상태는 따로 검사한다"고 밝힌다.
- 부작용: 없음. 명령을 실행하지 않는다.
- 의존: `do_math.formal.portable_bin`, `toolchain_root`.
- 소비자: `test_formal`, `test_formal_runtime`, `test_knowledge_import_engine`, `test_knowledge_storage`, `test_lean_preview`.
- 비고: 모듈 docstring(행 24–25)에 따르면 이 명령은 `lean` 표지를 단 시험만 부른다. 그 시험들은 실제 Lean을 실행한다.

## HTTP

### `HTTPFixtureHandler` (행 227–236)
- 종류: 대역(HTTP 서버 처리기). `BaseHTTPRequestHandler`를 상속한다.
- 하는 일과 반환값: docstring은 "POST는 201 `ok`로 답하고, GET은 다른 출처로 리다이렉트한다"이다. 외부 효과(external effect)를 전송하는 제품 경로가 실제 HTTP 소켓을 거치게 하는 로컬 서버의 처리기다.
- 메서드:
  - `do_POST` (행 229–231): `Content-Length`(없으면 0)만큼 본문을 읽어 버리고 201과 `Content-Length: 2`, 본문 `b'ok'`로 답한다. 요청 본문은 검사하지 않는다.
  - `do_GET` (행 233–234): 302와 `Location: http://evil/`, `Content-Length: 0`으로 답한다. 곧 허가된 출처 밖으로 향하는 리다이렉트를 돌려준다.
  - `log_message` (행 236): 아무것도 하지 않는다. 서버 로그가 시험 출력에 섞이지 않게 한다.
- 부작용: 처리기 자체는 소켓 응답만 쓴다. 서버를 띄우는 것은 소비 시험이다.
- 의존: `http.server.BaseHTTPRequestHandler`.
- 소비자: `test_external`, `test_lifecycle_engine`.
- 비고: 소비 시험은 실제 로컬 소켓을 연다. `test_external`은 `setUp`(행 42)에서 `HTTPServer(('127.0.0.1', 0), HTTPFixtureHandler)`를 데몬 스레드로 띄우고 `tearDown`에서 내린다. `test_lifecycle_engine`(행 134, 1034)은 이 처리기를 상속한 `Handler`로 `do_POST`를 덮어 호출 횟수를 센다.

## 관계

- 다른 픽스처 모듈과의 의존: 이 모듈이 부르는 픽스처는 `research_fixtures.current_state` 하나다(`provider_repository`). 다른 픽스처 모듈은 이 모듈을 import하지 않는다. 그래서 이 모듈은 픽스처 의존 그래프의 잎에 가깝다.
- 시작 상태 체계에서의 자리: 이 모듈은 `research_fixtures` docstring의 네 단 체계 밖에 있다. 대부분의 정의는 1단 시험(어댑터, 러너, 프로필 산술, 스트림 파싱)에 입력과 대역을 준다. `provider_repository`와 `transact`는 합성 상태를 실제 Git 저장소에 게시하는 별도 경로다. 공급자 한도와 세션 슬롯 시험은 이 경로 위에서 템플릿이나 공개 활성화 없이 돈다.
- 외부 자원의 경계: 모델 프로세스는 `Adapter`와 `mock_adapter`가, Windows Job 관측은 `FakeJob`이, 원격 공급자 한도 실패는 `PROVIDER_LIMIT_FAILURE`와 `report`가 대신한다. 실제 외부 자원을 쓰는 정의는 둘이다. `actual_command`는 실제 Lean(`lean` 표지 시험)에 쓰이고, `HTTPFixtureHandler`는 실제 로컬 HTTP 소켓에 쓰인다.

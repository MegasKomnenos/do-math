# test_lifecycle_gates

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_lifecycle_gates.py` (201행) |
| 클래스 / 테스트 | 4 / 15 |
| 시험 대상 제품 코드 | `do_math/initialization.py`의 `initialize_state`, `activation_requirements`, `capability_requirements`; `do_math/record_schemas.py`의 `validate_lifecycle`; `do_math/lifecycle_engine.py`의 `_clock_guard`, `_require_action_clock`, `_apply_extended_control`, `_resume_lifecycle`, `_pause_lifecycle`, `_conversation_control`, `_lose_conversation`, `_conversation_live`, `_record_readiness`, `_activate_initialization`; `do_math/formal_engine.py`의 `_formal_environment` |
| 사용하는 픽스처 모듈 | `research_fixtures`: `bare_engine`, `FixtureAdapter`; `engine_fixtures`: `FakeEngine` |
| 격리 표지 | 없음 |
| 시작 상태 | 대부분 1단(`initialize_state`의 순수 결과, 또는 그 결과를 얹은 `bare_engine`). 한 시험은 메모리 엔진 대역 `FakeEngine`으로 활성화까지 몬다 |

## 목적

모듈 docstring은 "Instance lifecycle gates: activation requirements and capability evidence, lifecycle transitions, the clock guard and the conversation lease."다. 인스턴스 수명주기의 관문 넷을 검사한다.

1. 활성화 요건과 능력 증거. 초기화는 빠진 요건을 기록만 하고 아무것도 배정하지 않는다. 능력은 프로필의 참/거짓 표기가 아니라 관찰된 증거로만 인정한다.
2. 수명주기 전이. 멈춤과 재개는 이전 수명주기 상태로 돌아간다. 대화 소실로 멈춘 뒤에는 새 연결 세대가 있어야 재개한다.
3. 시계 관문. 저장된 UTC 최고 수위보다 이른 시각, 실시간 UTC의 역행, 단조 시계와 UTC의 어긋남은 새 권한을 막는다. 시계 분해능 안의 양자화는 역행으로 보지 않는다.
4. 대화 임대. 독립 운영 정책에서는 대화 임대가 없어도 살아 있다고 본다.

제품 좌표로, `_clock_guard`(lifecycle_engine.py 행 71–107)의 docstring은 "A retained regression blocks authority until a verified re-observation."이다. `capability_requirements`(initialization.py 행 26–55)의 docstring은 "Use exact profile/host/implementation evidence, never profile booleans."다. `activation_requirements`(행 189 이하)의 docstring은 "Evaluate current evidence; none of these checks creates authority."다.

## 모듈 수준 요소

- 행 9 `SCRIPTS`: 스킬의 `scripts/` 폴더. 행 10에서 `sys.path` 앞에 넣는다.
- `fixture_engine()` (행 21–28): `bare_engine(head="snapshot-fixture")`에 시계 대역을 붙인다. `current_time`은 2026-09-20 00:00 UTC다. `lifecycle_clock`은 `current_time`의 ISO 문자열을, `lifecycle_monotonic`은 항상 `0.0`을 돌려준다. 상태는 `initialize_state(instance_id='RI-fixture', goal='G', workspace=<임시 폴더>, config={}, source_input='original request', created_at=<current_time>)`로 만든다. 따라서 저장된 UTC 최고 수위는 `current_time`과 같다. 시험은 `current_time`을 바꾸어 UTC 시계를 움직인다. 사용처는 `ActivationGateTests`의 두 시험, `LifecycleTransitionTests.engine`, `ClockResolutionTests`의 세 시험이다.
- 행 200–201: 직접 실행하면 `unittest.main()`을 부른다.

## ActivationGateTests (행 31–96)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다.

### `test_initialization_persists_missing_activation_requirements_without_dispatch` (행 32–43)
- 성질: 초기화 직후의 상태는 `initializing`이고, 대기열이 비어 있으며, 가용성이 `blocked`다. 빠진 활성화 요건에 거버넌스와 신뢰 환경이 들어 있다.
- 준비: `initialize_state(instance_id="RI-test", goal="Prove a theorem", workspace=<임시 폴더>/do-math-lifecycle-test, config={}, source_input="original user request")`.
- 실행: `activation_requirements(instance, runtime)`.
- 단언: `instance["lifecycle"]["state"] == "initializing"`, `runtime["status"] == "initializing"`, `runtime["queue"] == []`다. `missing`에 `"governance"`와 `"trust_environment"`가 있다. `runtime["availability"]["state"] == "blocked"`다.
- 대역: 없음.
- 비고: 이름의 "persists"는 초기화가 만든 상태 사전에 빠진 요건과 차단이 담겨 있다는 뜻으로 읽힌다. 저장소 게시는 하지 않는다. `missing`의 다른 항목(설정, 대화 정책, 외부 정책, 독립 의도 등)은 단언하지 않는다.

### `test_formal_use_cannot_register_or_activate_an_environment` (행 45–52)
- 성질: 형식 사용 입장(`_formal_environment`)은 승인된 활성 환경이 없으면 거부하고, 그 과정에서 환경을 등록하거나 활성화하지 않는다.
- 준비: `fixture_engine()`. 신뢰 환경이 하나도 없다.
- 실행: `engine._formal_environment()`.
- 단언: `ValueError`의 메시지가 정규식 `'approved'`에 맞는다. 제품 메시지는 `'approved fixed trust environment required: ...'`다(`require_active_environment`). 호출 뒤 `active_trust_environment`가 `None`이고 `trust_environments`가 빈 사전이다.
- 대역: 시계 대역(`fixture_engine`).
- 비고: 시계가 사용 가능하므로 `_require_action_clock`은 통과하고, 거부 사유는 환경 부재로 고정된다.

### `test_clock_regression_blocks_new_lifecycle_action_without_rewriting_time` (행 54–62)
- 성질: 현재 UTC가 저장된 최고 수위보다 이르면 시계 관문은 사용 불가를 알리고, 저장된 최고 수위를 고쳐 쓰지 않는다.
- 준비: `fixture_engine()`의 `last_observed_utc`를 현재보다 1분 뒤인 `"2026-09-20T00:01:00+00:00"`으로 바꾼다.
- 실행: `engine._clock_guard()`.
- 단언: `usable`이 거짓이고 `reason == "persisted_utc_regression"`이다. `last_observed_utc`가 그대로다.
- 대역: 시계 대역.
- 비고: 이름은 "새 수명주기 행동을 막는다"고 말하지만, 행동 호출은 하지 않고 관문의 반환만 본다. 행동 차단은 `LifecycleTransitionTests.test_clock_failure_precedes_grant_application`이 확인한다.

### `test_capability_gate_reports_missing_evidence_instead_of_assuming_support` (행 64–76)
- 성질: 저장된 프로필에 능력을 참으로 적어 두어도 관찰 증거가 없으면 능력 관문은 충족되지 않는다. 필요한 능력 전부를 빠진 것으로 보고하며, 참조 오류로 끝나지 않는다.
- 준비: `build_profiles(DEFAULT_CONFIG)`에서 `actor_kind == "ai"`인 첫 프로필을 고르고, `capabilities`에 `required_capabilities`의 모든 이름을 `True`로 적는다. 원문 주석(행 69)은 "A boolean claim on the stored profile is not observed capability evidence."라고 밝힌다.
- 실행: `capability_requirements(instance, profile_ref(profile), current_identity={"host": "fixture"})`.
- 단언: 결과에 `reason` 키가 없다(주석: 유효하지 않은 참조로 끝난 것이 아니라 증거로 판단됨). `missing`이 정렬된 `required_capabilities`와 같다. `satisfied`가 거짓이다.
- 대역: 없음. `current_identity`를 인자로 주어 어댑터 관찰을 부르지 않는다.

### `test_activation_requires_recorded_evidence_then_opens_the_correct_first_action` (행 78–87)
- 성질: 활성화 관문은 증거가 기록되기 전에는 활성화하지 않는다. 채택 절차를 거치면 수명주기가 `active`가 되고 가용성이 열린다.
- 준비: 임시 폴더 위의 `FakeEngine(root)`. 어댑터 관찰은 `FixtureAdapter`로 바꾼다.
- 실행: `engine._activate_initialization()`, 이어서 `engine.activate()`. `FakeEngine.activate`는 초기 허가와 연구 허가, 헌장, AI 프로필별 능력 증거, 초기화 채택 결정, 합성 신뢰 환경 `base`의 등록과 전환, 의도 해석 두 실행을 차례로 적용한다.
- 단언: 첫 호출의 반환에서 `activated`가 거짓이다. `activate()` 뒤 `lifecycle.state == 'active'`이고 `runtime['availability'] == {'state': 'available'}`다.
- 대역: `FakeEngine`(메모리 상태 위의 제품 엔진. 저장은 사본 기록), `patch('do_math.initialization.adapter_for', return_value=FixtureAdapter())`.
- 비고: 이름은 "올바른 첫 행동을 연다"고 말하지만, 단언은 수명주기 상태와 가용성만 본다. 대기열의 첫 행동은 확인하지 않는다. 게다가 `FakeEngine.activate`는 `_complete_initial_intent`와 `_activate_initialization`을 부른 뒤 마지막에 `runtime['queue']`와 `runtime['pending_events']`를 비운다(engine_fixtures.py 행 174–177). 그래서 이 시험의 끝 상태에는 활성화가 연 첫 행동이 남아 있지 않다.

### `test_lifecycle_rules_reject_a_state_without_its_utc_high_water` (행 89–96)
- 성질: 수명주기 규칙은 UTC 최고 수위가 없는 상태를 거부한다.
- 준비: `initialize_state(instance_id="RI-check", ...)`.
- 실행: `validate_lifecycle(instance, runtime)`을 한 번 부르고(통과), `runtime`에서 `last_observed_utc`를 뺀 뒤 다시 부른다.
- 단언: 두 번째 호출이 `ValueError`를 던지고, 메시지가 `"high-water"`에 맞는다.
- 대역: 없음.

## LifecycleTransitionTests (행 99–151)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅이 없다. 도우미 하나를 둔다.

- `engine()` (행 100–106): `fixture_engine()`을 받아 상태를 `initialize_state(instance_id='RI-test', goal='G', ..., source_input='original', created_at=<current_time>)`로 다시 만들고, `lifecycle_monotonic`을 `0.0`으로 다시 둔다. 모든 시험이 이 엔진에서 시작한다. `fixture_engine`이 이미 같은 방식으로 상태와 단조 시계를 두므로, 달라지는 것은 인스턴스 ID와 원래 입력 문자열뿐이다.

### `test_initialization_does_not_create_implicit_grants` (행 108–110)
- 성질: 초기화는 암묵적 허가를 만들지 않는다.
- 준비: `self.engine()`.
- 실행: 없음(상태만 읽는다).
- 단언: `instance.get('grants') == {}`.
- 대역: 시계 대역.

### `test_pause_resume_returns_to_initialization_and_requires_new_generation` (행 112–126)
- 성질: 초기화 중에 멈췄다가 재개하면 `initializing`으로 돌아간다. 멈춤을 두 번 해도 돌아갈 상태가 덮어쓰이지 않는다. 대화 소실 정책이 `pause`일 때 대화를 잃으면, 새 연결 세대가 붙기 전에는 재개가 거부된다.
- 준비: `self.engine()`.
- 실행: (1) `pause-1` 적용. (2) `pause-2`와 `resume-1` 적용. (3) `conversation_loss_policy='pause'`로 두고, `_conversation_control`로 대화 `chat` 세대 1을 임대 60초로 붙인 뒤 `_lose_conversation`으로 잃는다. (4) `resume-2` 적용. (5) 세대 2로 다시 붙이고 `resume-3` 적용.
- 단언: (1) 뒤 `runtime['resume_lifecycle'] == 'initializing'`. (2) 뒤 `status == 'initializing'`. (4)는 `ValueError`(메시지 정규식 `'conversation'`)로 거부된다. 제품 메시지는 `'conversation pause requires a live new connection generation'`이다. (5) 뒤 `status == 'initializing'`.
- 대역: 시계 대역.
- 비고: 멈춤이 이미 `paused`이면 `resume_lifecycle`을 덮어쓰지 않는 제품 규칙(`_pause_lifecycle` 행 131–132)은, 두 번 멈춘 뒤의 재개 결과로 간접 확인된다. `_conversation_live`는 연결 행의 세대가 `lost_conversation_generations`의 값보다 커야 살아 있다고 본다.

### `test_clock_failure_precedes_grant_application` (행 128–135)
- 성질: 시계가 쓸 수 없는 상태면 허가 결정은 적용되기 전에 거부되고, 허가 목록이 바뀌지 않는다.
- 준비: `self.engine()`의 `last_observed_utc`를 하루 뒤(`'2026-09-21T00:00:00+00:00'`)로 둔다. 허가 목록 사본을 떠 둔다.
- 실행: `_apply_extended_control`로 `decision` 제어 `grant-1`(로컬 허가, 역할 `maintenance`)을 적용한다.
- 단언: `ValueError`의 메시지가 `'clock'`에 맞는다. 제품 메시지는 `'clock prevents new authority: persisted_utc_regression'`이다. 허가 목록이 사본과 같다.
- 대역: 시계 대역.

### `test_derived_readiness_not_written_to_runtime` (행 137–141)
- 성질: 과제 준비도는 파생값이며, 런타임 상태에 기록되지 않고 프로세스 지역의 `_task_readiness`에만 남는다.
- 준비: `self.engine()`.
- 실행: `engine._record_readiness('T', {'state': 'ready', 'basis': [], 'errors': []}, 'now')`.
- 단언: `runtime`에 `task_readiness` 키가 없다. `engine._task_readiness['T']['state'] == 'ready'`.
- 대역: 시계 대역.

### `test_live_monotonic_regression_blocks_before_catching_persisted_high_water` (행 143–151)
- 성질: 단조 시계로 잰 경과보다 UTC가 덜 흘렀으면, 현재 UTC가 저장된 최고 수위를 넘더라도 `live_monotonic_regression`으로 막는다. 같은 시계 조건에서 다음 권한 행동도 거부된다.
- 준비: `self.engine()`의 단조 시계를 목록 `tick=[0.0]`으로 바꾼다.
- 실행: (1) `_clock_guard()`로 기준점을 잡는다. (2) 단조 시계를 2.0초, UTC를 1초 앞당기고 `_clock_guard()`를 다시 부른다. (3) `decision` 제어 `UI-rejected`(`change.kind='grant'`)를 적용한다.
- 단언: (1)은 `usable`이 참이다. (2)의 `reason == 'live_monotonic_regression'`이다. (3)은 `ValueError`(`'clock'`)로 거부된다.
- 대역: 단조 시계와 UTC 시계 대역. `time.get_clock_info`는 실제 값이다.
- 비고: 제품은 첫 호출에서 `(now, after, wall_radius, mono_radius)` 기준점을 저장한다. 다음 호출에서 단조 경과의 하한만큼 UTC가 흘렀어야 한다고 보고, 모자라면 이 사유를 낸다. 실패는 `_clock_failure`에 남아 이후 호출에서 되돌아온다(행 97–105). 다만 (3)의 호출에서도 단조 시계 2.0초와 UTC +1초가 그대로이고 기준점도 첫 호출의 것이므로, 제품은 같은 사유를 다시 계산해도 거부한다. 따라서 (3)의 단언은 실패의 유지와 재계산을 구별하지 않는다. 이름의 "before catching persisted high-water"는 UTC가 저장된 수위보다 앞서 있어서 `persisted_utc_regression`에는 걸리지 않는 상황을 가리킨다.

## ClockResolutionTests (행 154–191)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다. 세 시험 모두 `fixture_engine()`에서 시작한다.

### `test_actual_host_samples_do_not_report_quantization_as_regression` (행 155–167)
- 성질: 실제 호스트의 UTC 시계와 단조 시계를 빠르게 반복해 표본해도, 시계 분해능 때문에 생기는 양자화가 역행으로 보고되지 않는다.
- 준비: `lifecycle_clock`을 실제 `datetime.now(timezone.utc)`로, `lifecycle_monotonic`을 실제 `time.monotonic`으로 바꾼다. 저장된 최고 수위는 지금보다 1초 앞의 시각으로 둔다.
- 실행: `_clock_guard()`를 200번 부르고, 호출 사이마다 `time.sleep(.002)`를 둔다.
- 단언: 매 호출의 `usable`이 참이다. 실패하면 회차, 결과, 지금까지의 표본 목록을 메시지로 보인다.
- 대역: 없음(실제 시계).
- 비고: 실제 호스트 시계를 쓰는 표본 시험이다. `time.sleep(.002)`로 200회 대기하므로 Windows의 대기 분해능에 따라 수백 밀리초에서 수 초가 걸릴 수 있다. `시험-지침.md` 4절 규칙 5는 다른 스레드나 프로세스의 결과를 기다리는 고정 대기를 금한다. 이 시험의 대기는 결과를 기다리는 것이 아니라 표본 간격을 만드는 것이지만, 표본의 시간 분포는 기계 부하에 따라 달라진다.

### `test_windows_quantization_interval_is_not_a_regression` (행 169–179)
- 성질: 단조 시계가 한 양자(15.625ms)만큼 뛰는 동안 UTC가 3ms만 흘러도 역행이 아니다.
- 준비: 단조 시계를 `10., 10., 10.015625, 10.015625`를 차례로 내는 반복자로 바꾼다. `do_math.lifecycle_engine.time.get_clock_info`가 분해능 `.015625`를 돌려주게 패치한다. 이 패치는 UTC 시계와 단조 시계 모두에 적용된다.
- 실행: `_clock_guard()`로 기준점을 잡고, UTC를 3ms 앞당긴 뒤 다시 부른다.
- 단언: 두 호출 모두 `usable`이 참이다.
- 대역: 단조 시계 대역, `patch('do_math.lifecycle_engine.time.get_clock_info', return_value=SimpleNamespace(resolution=.015625))`.
- 비고: 제품은 경과 하한을 `before - mono_radius - (anchor 단조 + anchor mono_radius)`로 계산해 0 아래면 0으로 둔다. 양쪽에 분해능 하나씩을 빼므로, 한 양자의 뜀은 요구 경과 0으로 흡수된다.

### `test_direct_utc_regressions_have_no_quantization_tolerance` (행 181–191)
- 성질: 실시간 UTC가 직전 관측보다 뒤로 가면, 1마이크로초라도 허용 오차 없이 `live_utc_regression`이다.
- 준비: `subTest`로 두 경우. 역행량은 `timedelta(microseconds=1)`과 `timedelta(seconds=60)`이다. 각 경우 새 `fixture_engine()`의 UTC를 120초 앞당긴다.
- 실행: `_clock_guard()`로 기준점을 잡고, UTC를 역행량만큼 되돌린 뒤 다시 부른다.
- 단언: 첫 호출은 `usable`이 참이다. 둘째 호출은 `usable`이 거짓이고 `reason == 'live_utc_regression'`이다.
- 대역: 시계 대역(단조 시계는 0.0 고정).
- 비고: 되돌린 시각도 저장된 최고 수위보다는 뒤이므로 `persisted_utc_regression`이 아니라 기준점과의 비교(`now < anchor[0]`)에서 걸린다.

## ConversationLeaseTests (행 194–197)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다.

### `test_independent_operation_does_not_require_a_conversation_lease` (행 195–197)
- 성질: 대화 소실 정책이 `continue_authorized`이면 연결된 대화가 하나도 없어도 대화가 살아 있다고 본다.
- 준비: `bare_engine({'conversation_loss_policy': 'continue_authorized'}, {'conversations': {}})`.
- 실행: `engine._conversation_live()`.
- 단언: 반환값이 참이다.
- 대역: 없음.

## 관계

- 수명주기 엔진의 넓은 경로(공개 초기화와 활성화, 제어 수신, 재개 뒤의 배정)는 `lifecycle` 조각의 `test_lifecycle_engine`, `test_controls`, `test_engine` 등이 다룬다. 이 모듈은 관문 함수 단위의 규칙에 집중한다.
- 능력 증거의 생산(어댑터 관찰과 `capability_evidence` 기록)은 `test_execution_profiles`, `test_initialization_probe_batch` 등이 다룬다. 여기서는 증거가 없을 때의 판정만 본다.
- 픽스처 의존은 다음과 같다. `research_fixtures.bare_engine`(모듈 함수 `fixture_engine`과 대화 임대 시험), `engine_fixtures.FakeEngine`과 `research_fixtures.FixtureAdapter`(활성화 시험 하나).
- 이 모듈에만 있는 도우미는 `fixture_engine`과 `LifecycleTransitionTests.engine`이다.

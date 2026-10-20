# test_observation_admission

| 항목 | 값 |
|---|---|
| 조각 | `lifecycle` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_observation_admission.py` (146행) |
| 클래스 / 테스트 | 2 / 8 |
| 시험 대상 제품 코드 | `do_math/initialization.py`의 `initialize_state`, `activation_requirements`; `do_math/initialization_engine.py`의 `_initialization_control`(채택 연산); `do_math/observations.py`의 `observation_settings_errors`, `tracker_config`; `do_math/execution_profiles.py`의 `build_profiles`; `do_math/planning_engine.py`의 `_retry_observation_configuration`; `do_math/engine.py`의 `control`, `ResearchEngine`(`status`, `process_controls`, `control_result`, `_execution_profile`); `do_math/repository.py`의 `exact_content_hash` |
| 사용하는 픽스처 모듈 | `engine_fixtures`(`FakeEngine`); `research_fixtures`(`FixtureAdapter`, `new_instance`) |
| 격리 표지 | 없음 |
| 시작 상태 | 1단(`initialize_state`, `build_profiles`, 관찰 설정 검사기 직접 호출) 3개. 메모리 엔진 대역 `FakeEngine` 4개(활성화 전 3개, `activate()` 뒤 1개). 4단(공개 `initialize`) 1개 |

## 목적

모듈 docstring은 "기본 초기 구성(bootstrap)과 변경 불가 프로필의 입장을 픽스처 기본값 없이" 시험한다고 밝힌다. 실행 프로필은 관찰 설정 두 값을 담는다. 하나는 도구 검토 창 `tool_review_window_seconds`이고, 다른 하나는 자기 점검 응답 창 `self_check_response_window_seconds`다. 제품 기본 설정(`DEFAULT_CONFIG`)은 두 값을 정하지 않는다. `research_fixtures.activate`의 주석도 "제품에는 의도적으로 암묵적 기본값이 없다"고 적는다.

이 모듈은 대부분의 픽스처가 넣어 주는 그 두 값을 빼고 시작한다. 그 상태에서 다음을 확인한다.

- 활성화 조건이 빠진 설정을 정확히 보고한다.
- 설정 채택이 준비되지 않은 프로필을 거부한다.
- 창 값의 형식이 검증된다.
- 설정이 갖춰진 뒤 관찰 설정 대기를 풀 때, 검토 행동은 새 프로필에 다시 결박되지만 과제에 고정된 프로필은 다시 준비된다.

## 모듈 수준 요소

- 행 8: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 넣는다.
- 행 145–146: 직접 실행하면 `unittest.main()`.

## ObservationAdmissionTests (행 17–102)

`unittest.TestCase`를 상속한다. 설정 훅과 도우미가 없다.

### `test_default_bootstrap_reports_exact_missing_settings_before_activation` (행 18–32)
- 성질: 기본 설정으로 초기화한 인스턴스는 활성화 조건 보고에서 빠진 관찰 설정을 정확히 두 창 필드로 짚고, 별도 프로필 목록을 요구하지 않는다. 관찰 설정 말고 다른 활성화 조건도 빠져 있을 수 있으며, 시험은 그것을 보지 않는다.
- 준비: 1단. `initialize_state(instance_id='RI-default', config=deepcopy(DEFAULT_CONFIG), source_input='Original request')`에 `build_profiles`를 더한다.
- 실행: `activation_requirements(instance, runtime)`.
- 단언:
  - `satisfied`가 거짓이다.
  - `missing`에 `profiles`가 없고 `observation_configuration`이 있다. 주석은 현재 역할 프로필이 곧 채택 판본이라 별도 목록이 필요 없다고 적는다.
  - `observation_errors`의 필드 집합이 정확히 두 창 이름이고, 모든 오류의 `profile_id`가 인스턴스 프로필이다.
  - 오류 역할에 `intent_interpretation`이 없고 `research_work`가 있다.
  - 원 입력 텍스트가 `'Original request'`다.
- 대역: 없음.

### `test_adopting_a_configuration_whose_role_profiles_lack_settings_is_rejected` (행 34–42)
- 성질: 역할 프로필에 관찰 설정이 빠진 설정은 채택할 수 없고, 채택 기록이 남지 않는다.
- 준비: `FakeEngine(root)`. `FakeEngine`은 기본적으로 두 창 값을 넣으므로, 인스턴스 설정을 `DEFAULT_CONFIG` 사본으로 되돌리고 그 설정으로 `build_profiles`를 다시 적용한다.
- 실행: `_initialization_control({'config_sha256': exact_content_hash(config)}, 'UI-settings')`.
- 단언: `ValueError`의 메시지가 정규식 `'observation_configuration.*research_work'`에 맞는다. `lifecycle.adoption`에 `config_sha256`이 없다.
- 대역: `FakeEngine`.

### `test_adoption_of_a_configuration_other_than_the_current_one_is_rejected` (행 44–49)
- 성질: 현재 설정이 아닌 설정 해시의 채택은 거부된다.
- 준비: `FakeEngine(root)`(창 값을 갖춘 설정).
- 실행: `_initialization_control({'config_sha256': '0'*64}, 'UI-stale')`.
- 단언: `ValueError`(메시지 `'config_sha256'`). 채택 기록에 `config_sha256`이 없다.
- 대역: `FakeEngine`.

### `test_adoption_takes_no_profile_list` (행 51–56)
- 성질: 채택 요청은 프로필 목록을 받지 않는다.
- 준비: `FakeEngine(root)`와 `research_work`의 첫 프로필 참조.
- 실행: `_initialization_control({'profile_refs': [reference]}, 'UI-profiles')`.
- 단언: `ValueError`(메시지 `'profile_refs'`).
- 대역: `FakeEngine`.

### `test_configured_settings_do_not_require_task_rules_until_execution` (행 58–67)
- 성질: 창 값이 설정된 프로필은 관찰 설정 오류가 없다. 과제 규칙은 설정 단계가 아니라 추적기를 만드는 실행 단계에서야 요구되며, 그 요구는 `research_work`에만 있다.
- 준비: 1단. 두 창 값(60, 5)을 더한 설정의 `build_profiles`.
- 실행: 모든 프로필에 `observation_settings_errors(profile)`와 `tracker_config(profile)`.
- 단언: 모든 프로필의 설정 오류가 `[]`다. `research_work`는 `tracker_config`가 `ValueError`(메시지 `'rules'`)이고, 다른 역할은 예외 없이 통과한다.
- 대역: 없음.

### `test_nonpositive_boolean_and_fractional_millisecond_values_are_rejected` (행 69–76)
- 성질: 도구 검토 창 값으로 없음, 0, 음수, 불리언, 밀리초보다 작은 소수 문자열, `NaN`은 거부된다.
- 준비: 1단. 기본 설정 `research_work` 프로필.
- 실행: `subTest`로 값 `None`, `0`, `-1`, `True`, `'0.0001'`, `'NaN'`마다 `observation.settings`에 그 값과 응답 창 5를 넣고 `observation_settings_errors(profile)`.
- 단언: 오류 필드 목록이 정확히 `['tool_review_window_seconds']`다(응답 창 5는 통과한다).
- 대역: 없음.
- 비고: `subTest` 케이스는 여섯 값이다. 반복 사이에 같은 프로필 사전을 바꿔 쓴다.

### `test_active_wait_rebinds_review_but_reprepares_a_tasks_fixed_profile` (행 78–102)
- 성질: 관찰 설정 대기를 다시 볼 때, 계약 검토 행동은 대기에서 풀려 현재 프로필로 다시 결박되고, 옛 프로필에 고정된 과제의 작업 행동은 대기에 남는다. 그 대신 과제를 다시 준비하는 행동이 큐에 들어가며 과제의 고정 프로필은 바뀌지 않는다.
- 준비:
  - `adapter_for`를 `FixtureAdapter`로 패치한 `FakeEngine`에 `activate()`를 부른다.
  - `_execution_profile`을 `FakeEngine`의 재정의 대신 제품 `ResearchEngine._execution_profile`로 되돌린다(`MethodType`).
  - 창 값이 없는 기본 설정의 옛 프로필(`build_profiles(DEFAULT_CONFIG)`)을 인스턴스 프로필에 더한다.
  - 미승인 과제 `TK-old`의 `profile_refs`를 옛 `research_work` 참조로 두고 사본을 뜬다.
  - 대기 두 개를 둔다. `AC-review`는 옛 `task_contract_review`의 두 번째 참조를 고정한 계약 검토이고, `AC-work`는 과제 작업이다. 둘 다 종류가 `observation_configuration`이다.
- 실행: `_retry_observation_configuration()`.
- 단언: `AC-review`가 대기에서 빠진다. `AC-work`는 대기에 남는다. 과제의 `profile_refs`가 사본과 같다. 큐에 대상이 그 과제인 `research_preparation` 행동이 있다.
- 대역: `FixtureAdapter`, `FakeEngine`(단 `_execution_profile`은 제품 메서드).
- 비고:
  - 이름의 "rebinds review"에 대응하는 단언은 검토 행동이 대기에서 빠진다는 것뿐이다. 다시 결박된 프로필 참조 값은 보지 않는다.
  - 제품 `_retry_observation_configuration`(`planning_engine.py` 행 40)은 과제 연구 생산 역할에 대해, 현재 역할 프로필이 모두 설정 오류가 없고 학술 요구 과제가 아니면 그 과제의 `research_preparation`을 큐에 넣는다.

## PublicObservationAdmissionTests (행 105–142)

`unittest.TestCase`를 상속한다. 설정 훅과 도우미가 없다.

### `test_public_default_init_rejects_unready_adoption_then_adopts_the_configured_one` (행 106–142)
- 성질: 기본값으로 공개 초기화한 인스턴스에서는 관찰 창 없이 채택 결정을 보내면 두 창 이름을 사유로 거부되고 `initializing`에 머문다. 공개 `configure`로 창을 정하면 새 프로필 판본과 새 설정 해시가 생기고, 그 해시의 채택은 받아들여진다. 옛 판본과 원 입력은 보존되고 실행은 생기지 않는다.
- 준비: 4단. `new_instance(repository, goal='Preserve this original', config={'scholarly_enabled': False, 'operator_enabled': False, 'lean_command': ['test-lean']})`. `research_work`의 옛 프로필 참조를 사본으로 둔다.
- 실행:
  1. `status()['config_sha256']`을 읽는다. 주석은 운전자가 점검한 설정의 해시를 `status`에서 읽는다고 적는다.
  2. 그 해시로 채택 `decision` 제어를 보내고 `process_controls`.
  3. 공개 `configure`로 두 창(60, 5)을 정하고 `process_controls`.
  4. 새 `status()['config_sha256']`로 채택 제어를 다시 보내고 `process_controls`.
- 단언:
  - 첫 요청의 `rejected_user_control` 기록 사유가 `tool_review_window_seconds`와 `self_check_response_window_seconds`를 모두 담고, 수명 상태가 `initializing`이다.
  - 설정 뒤 `research_work` 프로필 참조가 옛 것과 다르고 설정 해시도 달라진다.
  - 두 번째 요청 ID는 첫 것과 다르고, 그 결과 `effect`가 `applied`다.
  - 채택된 `config_sha256`이 현재 설정의 `exact_content_hash`와 같다.
  - 옛 프로필 ID가 여전히 인스턴스 프로필에 있고, 원 입력 텍스트가 보존되며, `executions`가 `{}`다.
- 대역: 없음.
- 비고: 실제 Git 저장소를 쓴다. 거부 사유는 메시지 조각(두 필드 이름)으로 고정된다.

## 관계

- **다른 층의 같은 기능.** 관찰 설정을 실행 시점에 추적기로 바꾸는 규칙(`tracker_config`, 과제 규칙 결박)은 `test_live_observation`의 `RuleBindingTests`와 `TaskObservationRoleTests`가 본다. 관찰 설정 검사 전반은 `test_observations`가 맡는다. `_initialization_control`의 `probe` 연산은 `test_initialization_probe_batch`가 본다. 활성화 조건 보고의 공개 판본(`missing` 목록과 사용자 차단)은 `test_engine.EngineTests.test_initialization_reports_missing_values_without_model_dispatch`가 본다.
- **픽스처 의존.** `engine_fixtures.FakeEngine`은 기본적으로 창 값 60, 5를 넣는다. 그래서 이 모듈은 그 값을 덮어써 "픽스처 기본값 없이"를 재현한다. 그 밖에 `research_fixtures.FixtureAdapter`와 `new_instance`를 쓴다.
- **이 모듈에만 있는 도우미.** 없다.
- **겹치거나 보완하는 시험.** 창이 빠진 설정의 채택 거부는 메모리(`test_adopting_a_configuration_whose_role_profiles_lack_settings_is_rejected`)와 공개 제어(`test_public_default_init_rejects_unready_adoption_then_adopts_the_configured_one`) 두 층에서 본다. 설정 해시 불일치 거부는 메모리 시험 `test_adoption_of_a_configuration_other_than_the_current_one_is_rejected`만 본다. 공개 시험은 두 번 모두 그 시점의 현재 설정 해시를 보내며, 첫 거부의 사유는 해시 불일치가 아니라 빠진 창이다.

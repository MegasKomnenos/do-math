# test_initialization_probe_batch

| 항목 | 값 |
|---|---|
| 조각 | `lifecycle` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_initialization_probe_batch.py` (139행) |
| 클래스 / 테스트 | 2 / 8 |
| 시험 대상 제품 코드 | `do_math/initialization_engine.py`의 `_initialization_control`(능력 관측 `probe` 연산); `do_math/initialization.py`의 `_capability_batch_requirements`, `capability_requirements`, `observed_profile_refs`, `adapter_for`; `do_math/execution_profiles.py`의 `build_profiles`, `profile_ref`; `do_math/engine.py`의 `control`, `ResearchEngine.process_controls`, `control_result` |
| 사용하는 픽스처 모듈 | `research_fixtures`(`FixtureAdapter`, `bare_engine`); `state_fixtures`(`start_active_copy`) |
| 격리 표지 | 없음 |
| 시작 상태 | `ProbeBatchTests`는 `bare_engine` 메모리 엔진(초기화 중 수명과 기본 설정의 프로필만 가진 인스턴스, 저장 대역). `ActiveProbePublicTests`는 2단(`start_active_copy`가 `state_fixtures.active_instance`를 `ACTIVE_CONFIG`로 복원) |

## 목적

모듈 docstring은 없다. 이 모듈은 초기화 결정 제어의 `probe` 연산을 검사한다. 이 연산은 실행 프로필마다 호스트 CLI를 관측해 능력 증거(`capability_evidence`)를 만든다. 제품 `_initialization_control`의 docstring은 "기존 결정 제어가 설정을 채택하거나 관측한 CLI 증거를 갱신한다"고 설명한다(`initialization_engine.py` 행 21–22). `_capability_batch_requirements`의 docstring은 "이 검사에서 공급자마다 한 번 관측하고, 정확한 프로필 각각을 검증한다"고 설명한다(`initialization.py` 행 58–59). 이 모듈은 다음을 검사한다.

- 묶음 관측은 현재 공급자 식별을 한 번만 읽어 재사용하고, 식별이 바뀌면 다시 읽는다.
- 증거는 프로필과 관측 범위를 보존한다.
- 잘못된 참조는 관측 전에 거부된다.
- 중간 실패는 부분 증거를 남기지 않는다.
- 활성 상태의 관측은 계약을 다시 채택하지 않는다.
- 참조 없는 관측은 현재 설정 해시를 요구하고 현재 AI 역할 프로필 전부를 관측한다.
- 공개 경로에서는 사용자만 정확한 활성 프로필을 갱신할 수 있다.

## 모듈 수준 요소

- 행 7: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 넣는다.
- 모듈 수준 함수·상수·`__main__` 블록이 없다. 파일을 직접 실행해도 시험이 시작되지 않는다.

## ProbeBatchTests (행 13–107)

`unittest.TestCase`를 상속한다.

- `setUp` (행 14–17): `DEFAULT_CONFIG` 사본으로 `build_profiles`를 만들고, 수명 `{"state": "initializing"}`, 설정, 프로필을 가진 인스턴스로 `bare_engine`을 만든다. `self.profiles`는 `actor_kind == "ai"`인 프로필 가운데 처음 두 개다.

모든 시험의 시작 상태는 이 메모리 엔진이며, `do_math.initialization.adapter_for`를 시험마다 따로 패치한다.

### `test_activation_batch_reuses_only_the_current_provider_observation` (행 19–43)
- 성질: 활성화 묶음 검사는 공급자 식별을 한 번만 관측해 현재 증거를 재사용하고, 식별이 바뀌면 다시 관측해 옛 증거를 쓰지 않으며, 해시가 다른 프로필 참조는 충족시키지 않는다.
- 준비: 두 프로필의 참조. `Mock` 어댑터의 `describe`는 식별 `{'host': 'fixture'}`, 검증됨, 범위 `cli_command_surface_only`, 지원 `jsonl`·`model`·`structured_output`를 돌려주고, `capability_identity`는 같은 식별을 돌려준다.
- 실행: 어댑터를 패치한 채 `_initialization_control({'operation': 'probe', 'profile_refs': references}, 'source')`. 같은 시각 `at`으로 참조마다 `capability_requirements(..., current_identity=identity, at=at)`를 기대값으로 계산하고, `_capability_batch_requirements(instance, references, at=at)`를 부른다. 식별을 `{'host': 'changed'}`로 바꿔 다시 부른다. 마지막 참조의 `sha256`을 0으로 바꿔 부른다.
- 단언: 묶음 결과가 개별 계산 목록과 같다. `capability_identity` 호출이 1번이고 모든 행이 `evidence_refs`를 가진다. 식별이 바뀐 뒤 호출 수가 2가 되고, 모든 행이 충족되지 않으며 `evidence_refs`가 비어 있다. 해시를 바꾼 참조는 충족되지 않는다.
- 대역: `Mock` 어댑터(`adapter_for` 패치).

### `test_batch_preserves_each_profile_and_observed_capability_scope` (행 45–55)
- 성질: 묶음 관측은 프로필마다 증거 행을 만들고, 관측된 기능은 `supported`로, 관측 범위 밖의 기능은 `unknown`으로 기록한다.
- 준비: `FixtureAdapter`를 상속해 `describe`가 범위 `cli_command_surface_only`와 지원 `{'jsonl': True, 'local_job': True}`를 돌려주는 어댑터.
- 실행: 두 프로필 참조로 `probe`.
- 단언: 증거 행의 프로필 ID 집합이 두 프로필의 ID 집합과 같다. 모든 행에서 `capabilities.jsonl.status`가 `supported`이고 `capabilities.local_job.status`가 `unknown`이다.
- 대역: `FixtureAdapter` 하위 클래스.
- 비고: 어댑터가 `local_job: True`를 보고해도 범위가 CLI 명령면이므로 로컬 Job 기능은 `unknown`으로 남는다. 이 해석은 단언된 값에서 읽은 것이며, 원문에 설명 주석은 없다.

### `test_invalid_reference_is_rejected_before_probing_or_mutating_evidence` (행 57–63)
- 성질: 없는 프로필을 가리키는 참조가 섞인 관측 요청은 어댑터를 부르기 전에 거부되고 증거를 바꾸지 않는다.
- 준비: 첫 프로필 참조와 ID `missing`인 참조.
- 실행: `adapter_for`를 `MagicMock`으로 패치하고 `probe`.
- 단언: `ValueError`(유형만). `adapter_for`가 불리지 않았다. `capability_evidence`가 비어 있다.
- 대역: `adapter_for` 패치.

### `test_failed_later_observation_does_not_publish_partial_evidence` (행 65–72)
- 성질: 묶음 관측 도중 뒤쪽 관측이 실패하면 앞쪽 관측의 증거도 남기지 않는다.
- 준비: 첫 호출에는 식별만 돌려주는 어댑터, 둘째 호출에는 `RuntimeError("probe failed")`를 내는 `side_effect`.
- 실행: 두 프로필 참조로 `probe`.
- 단언: `RuntimeError`(메시지 `"probe failed"`). `capability_evidence`가 비어 있다.
- 대역: `adapter_for` 패치(`side_effect` 목록).

### `test_active_probe_refreshes_observation_without_adopting_contract` (행 74–88)
- 성질: 활성 상태의 관측은 능력 증거만 갱신하고 인스턴스의 다른 부분을 바꾸지 않으며, 활성 계약을 대체하는 채택·통치 연산은 거부된다.
- 준비: 수명을 `{"state": "active", "adoption": {"config_sha256": "saved"}}`로 두고 인스턴스 사본을 뜬다. `jsonl`만 지원하는 어댑터.
- 실행: 단일 `profile_ref`로 `probe`. 이어서 `subTest`로 `adopt`, `governance` 연산을 각각 부른다.
- 단언: 증거가 생긴다. `capability_evidence`를 뺀 인스턴스가 사본과 같다. 두 연산은 각각 `ValueError`(메시지 `"active contract"`)다.
- 대역: `FixtureAdapter` 하위 클래스.
- 비고: `subTest` 케이스는 `adopt`, `governance`다. 제품 메시지는 `'initialization adoption cannot replace an active contract'`다(`initialization_engine.py` 행 29).

### `test_probe_without_named_editions_observes_every_current_ai_role_profile` (행 90–99)
- 성질: 프로필 참조 없이 현재 설정 해시만 준 관측은 현재 역할 프로필 가운데 AI 프로필 전부를 관측한다.
- 준비: 연산 `probe`와 `config_sha256 = exact_content_hash(instance["config"])`.
- 실행: `FixtureAdapter`를 패치하고 `_initialization_control(change, "source")`.
- 단언: 증거 행의 프로필 ID 집합이 `observed_profile_refs(instance)` 가운데 `actor_kind == "ai"`인 것의 ID 집합과 같다.
- 대역: `FixtureAdapter`.

### `test_probe_without_named_editions_must_name_the_current_configuration` (행 101–107)
- 성질: 프로필 참조 없는 관측은 현재 설정 해시를 요구하며, 없거나 다르면 관측 전에 거부된다.
- 준비: 두 요청. 연산만 있는 것과 `config_sha256`이 0인 것.
- 실행: `adapter_for`를 패치하고 `subTest`로 각각 `_initialization_control`.
- 단언: 각각 `ValueError`(메시지 `"config_sha256"`). `adapter_for`가 불리지 않았다. 증거가 비어 있다.
- 대역: `adapter_for` 패치.
- 비고: `subTest` 케이스는 두 요청이다.

## ActiveProbePublicTests (행 110–139)

`unittest.TestCase`를 상속한다.

- `setUp` (행 111–113): `state_fixtures.start_active_copy(self)`. 능력 관측을 `FixtureAdapter`로 바꾸고(`enterContext`), `restore_template(active_instance, config=ACTIVE_CONFIG)` 사본의 `root`, `repo`, `identifier`를 시험에 준다.

### `test_user_refreshes_exact_active_profile_and_other_authority_is_rejected` (행 115–139)
- 성질: 활성 인스턴스에서 사용자는 공개 결정 제어로 정확한 활성 프로필의 능력 증거를 갱신할 수 있고, 운전자 출처나 해시가 틀린 참조의 요청은 증거와 수명 기록을 바꾸지 않고 거부된다.
- 준비: 2단. 복원한 저장소 위의 엔진. 상태가 `active`임을 확인하고 수명 사본을 뜬다. `maintenance` 역할의 첫 프로필 참조로 `probe` 결정 설정을 만든다.
- 실행: `origin="operator"`로 공개 `control`. 사용자 출처 `control`과 `process_controls`. `sha256`을 0으로 바꾼 설정으로 `control`과 `process_controls`. 끝으로 `store.load()`.
- 단언: 운전자 출처는 `ValueError`(메시지 `"operator controls are limited"`)로 즉시 거부된다. 사용자 요청은 `control_result(...)["effect"]`가 `applied`이고, 수명 기록이 사본과 같으며, 증거 행 가운데 그 참조를 가진 것이 있다. 해시가 틀린 요청은 `effect`가 `rejected`이고, 증거와 수명 기록이 앞 값 그대로다. 게시된 인스턴스의 증거가 메모리 값과 같다.
- 대역: `FixtureAdapter`(`start_active_copy`).
- 비고: 운전자 출처 거부는 `control` 호출 단계에서 일어나며, 제품 메시지는 `"operator controls are limited to ..."`다(`engine.py` 행 260). 실제 Git 저장소 사본을 쓴다.

## 관계

- **다른 층의 같은 기능.** 공개 활성화 경로 전체에서 현재 설정 해시를 지정한 관측이 한 번 돈다(`research_fixtures.activate`의 `probe` 결정). 그 끝단 연결은 `test_engine.EngineTests.test_public_initialization_reaches_active_with_distinct_interpretation`이 지킨다. 능력 증거의 판정은 `test_lifecycle_engine`의 `test_capability_evidence_rejects_changed_host_or_forged_record`와 `test_negative_job_is_not_cleared_by_later_help_probe`가 본다. `_initialization_control`의 채택 연산은 `test_observation_admission`이 본다. 별도 관측 명령 `probe_cli`의 인자 검사는 `test_probe_cli`가 맡는다(그 모듈 docstring: "probe_cli argument checks which never call a model").
- **픽스처 의존.** `research_fixtures.bare_engine`(저장소 없는 엔진), `FixtureAdapter`(합성 관측, 범위 `synthetic_test_evidence_not_host_verification`), `state_fixtures.start_active_copy`(2단).
- **이 모듈에만 있는 도우미.** 없다. 각 시험이 `FixtureAdapter` 하위 클래스를 지역으로 정의한다.
- **겹치거나 보완하는 시험.** `test_invalid_reference_is_rejected_before_probing_or_mutating_evidence`와 `test_probe_without_named_editions_must_name_the_current_configuration`은 관측 전 거부를 두 입력 결함(없는 참조, 틀린 설정 해시)으로 나눠 본다. `test_active_probe_refreshes_observation_without_adopting_contract`(메모리)와 `ActiveProbePublicTests`(공개 제어와 게시)는 활성 상태 관측을 두 층에서 본다.

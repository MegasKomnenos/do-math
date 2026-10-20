# test_configuration

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_configuration.py` (55행) |
| 클래스 / 테스트 | 1 / 3 |
| 시험 대상 제품 코드 | `do_math/configuration.py`의 `DEFAULT_CONFIG`, `validate_config`; `do_math/engine.py`의 `initialize`; `do_math/execution_profiles.py`의 `build_profiles`, `WORK_ROLES`; 문서 `references/CLI-실행-계약.md`의 설정 목록 |
| 사용하는 픽스처 모듈 | 없음 |
| 격리 표지 | 없음 |
| 시작 상태 | 1단(검증기와 프로필 빌더 직접 호출, 계약 문서 읽기). 둘째 시험은 4단 공개 경로 `initialize`의 입구에서 거부되는 것만 본다 |

## 목적

모듈 docstring은 "Public configuration has one current execution model."이다. 설정 절은 닫혀 있어 선언되지 않은 키를 받지 않는다. 기본 입력 한도는 코드와 문서가 같은 값을 말한다. 모델 선택(`tier_models`)과 동시 실행 용량(`session_limits.work`)은 같은 모델 이름으로 이어져 하나의 현행 실행 모델을 이룬다. 이 모듈은 이 세 가지를 지킨다. 제품 좌표는 `do_math/configuration.py`의 `validate_config`(38행 이하)다. 이 함수는 먼저 스키마 속성에 없는 키를 `"configuration has fields outside the stored configuration section: "`으로 거부하고, 이어서 기본값과 합친 설정을 `config_schema()`로 검사해 `"config/<경로>: <jsonschema 메시지>"`를 낸다. 모델 사이의 규칙은 `model_policy.validate_policy`가 맡는다. 모델 선택과 용량의 연결은 `do_math/execution_profiles.py`의 `build_profiles`(206행 이하)에 있다.

## 모듈 수준 요소

- 행 9: `sys.path.insert(0, str(Path(__file__).resolve().parents[1]))`로 `scripts/` 폴더를 경로 앞에 넣는 공통 머리다. `SCRIPTS` 이름은 두지 않는다.
- 행 54–55: 직접 실행하면 `unittest.main()`을 부른다.

## ConfigurationTests (행 15–51)

`unittest.TestCase`를 그대로 상속한다. 표지, 클래스 속성, 설정 훅, 도우미가 없다.

### `test_default_input_limit_is_two_million_bytes_in_code_and_config_list` (행 16–20)
- 성질: 기본 입력 한도 `max_input_bytes`는 코드의 기본 설정과 설정 목록 문서 양쪽에서 2,000,000바이트다.
- 준비: 스킬 폴더의 `references/CLI-실행-계약.md`를 UTF-8로 읽는다. 경로는 `Path(__file__).resolve().parents[2]`에서 만든다.
- 실행: 문서에서 정규식 `^\| \`max_input_bytes\` \| (\d+) \|`로 표의 행을 찾는다(다중 행 모드). 한 개만 있어야 하도록 `documented, =`로 언팩한다.
- 단언: `(DEFAULT_CONFIG['max_input_bytes'], int(documented))`가 `(2_000_000, 2_000_000)`과 같다. 두 값이 서로 같다는 것만이 아니라 둘 다 이 숫자라는 것까지 고정한다. 문서에 해당 행이 없거나 둘 이상이면 언팩에서 `ValueError`로 실패한다.
- 대역: 없음.
- 비고: 주석(17행)은 이 값이 사용자의 결정이며 "the config list is the one document that states defaults"라고 이유를 적는다. 문서의 해당 행은 `CLI-실행-계약.md` 166행 `| \`max_input_bytes\` | 2000000 | 양의 정수 |`다. 시험-지침 4절 규칙 7은 제품 정의를 import해 쓰라고 하지만, 이 시험은 값 자체가 사용자 결정이므로 숫자를 직접 적는다.

### `test_configuration_outside_the_current_contract_is_rejected_before_creating_an_instance` (행 22–32)
- 성질: 현행 설정 계약 밖의 설정은 인스턴스와 작업 공간을 만들기 전에 `ValueError`로 거부된다.
- 준비: `subTest(patch=...)` 세 경우. 경우마다 새 `TemporaryDirectory`를 쓰고, `config={'scholarly_enabled': False, **patch}`를 만든다. `scholarly_enabled=False`는 scholarly 서버 해석(`initialize`의 158–159행)을 건너뛰게 한다.
  1. `{'invented_setting': 1}`: 선언되지 않은 키.
  2. `{'allowed_axioms': ['propext']}`: 현행 설정 절에 없는 키.
  3. `{'session_limits': None}`: 선언된 키지만 타입이 틀린 값.
- 실행: 공개 `initialize(root / 'repository', goal='P', workspace=root / 'workspace', config=...)`.
- 단언: 각 경우 `ValueError`의 메시지가 정규식으로 맞는다. (1)은 `'outside the stored configuration section: invented_setting'`, (2)는 `'outside the stored configuration section: allowed_axioms'`, (3)은 `'config/session_limits: None is not of type'`이다. 곧 거부 사유를 메시지까지 고정한다. 앞의 둘은 미지 키 검사의 문구와 키 이름을, 셋째는 스키마 검사의 경로 접두와 jsonschema 타입 오류 문구를 본다. 세 경우 모두 호출 뒤 `root / 'workspace'`가 없다.
- 대역: 없음.
- 비고: 제품 `initialize`는 `validate_config(settings)`(157행)를 `workspace.mkdir`(163행)보다 먼저 부른다. 작업 공간이 없다는 단언이 이 순서를 고정한다. `root / 'repository'`가 생기지 않았다는 것은 단언하지 않는다. 주석(23행)은 "The configuration section is closed: an undeclared key names no setting, and a declared one needs its type."이다.

### `test_model_selection_and_capacity_share_the_current_tier_configuration` (행 34–51)
- 성질: 세 등급이 한 모델을 가리키면 동시 실행 제약은 그 모델의 제약 하나뿐이고, 모든 AI 프로필이 그 모델을 쓰며, 작업 역할만 그 제약을 참조한다. 퇴역한 `operations` 용량 절은 거부된다.
- 준비: `DEFAULT_CONFIG`의 깊은 사본에 `tier_models`를 `low`·`medium`·`high` 모두 `'fixture-model'`로, `session_limits`를 `{'work': {'fixture-model': 2}}`로, `scholarly_enabled`를 `False`로 둔다.
- 실행: `validate_config(config)`로 통과를 확인하고 `build_profiles(config)`를 부른다. 이어서 `session_limits`에 `'operations': {'fixture-model': 1}`을 더한 사본 `retired`로 `validate_config`를 부른다.
- 단언:
  - `profiles['capacity_constraints']`의 값이 정확히 하나다(언팩). 그 제약의 `(kind, model, work_slots)`가 `('concurrency', 'fixture-model', 2)`다.
  - `actor_kind == 'ai'`인 모든 프로필의 `ai.model`이 `'fixture-model'`이다.
  - 그 모든 프로필에서 `ai.capacity_refs`는 역할이 `WORK_ROLES`에 들면 `[제약 id]`, 아니면 `[]`다. 운영 AI 역할은 모델 슬롯을 예약하지 않는다는 제품 규칙(`execution_profiles.py` 17–18행 주석)을 확인한다.
  - `retired`는 `ValueError`를 낸다. 메시지는 보지 않으므로 거부 사유는 고정되지 않는다.
- 대역: 없음.
- 비고: `retired`를 거부하는 것은 스키마다. `session_limits`는 `obj({"work": ...}, ("work",))`로 선언되어(`record_schemas/__init__.py` 165행) `additionalProperties: False`이므로, 실제 메시지는 `config/session_limits: Additional properties are not allowed ('operations' was unexpected)`다. 이 메시지는 시험이 아니라 제품 코드를 읽어 확인했다. `host_resources`가 없으므로 호스트 제약은 생기지 않는다. 제약이 하나뿐이라는 단언은 이 사실에도 기댄다.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈:
  - `build_profiles`가 만든 프로필의 고정·선택·재결합은 `test_execution_profiles`가 폭넓게 검사한다. 이 모듈은 설정에서 프로필로 가는 용량 연결 하나만 본다.
  - 모델별 동시 실행 슬롯 배정은 `test_claude_adapter`의 `test_mixed_models_use_existing_selection_and_per_model_work_slots`가 `SessionSlots`로 검사한다.
  - 호스트 자원 설정(`host_resources`)의 교차 규칙은 `test_host_resources`가 맡는다. 이 모듈은 그 경로를 지나지 않는다.
  - 원문에 `validate_config` 또는 `DEFAULT_CONFIG`가 나오는 파일은 시험 모듈 35개와 픽스처 모듈 5개, 모두 40개다. 대부분은 설정을 입력으로 쓴다.
- 문서 대조: 첫 시험은 스킬 문서 `references/CLI-실행-계약.md`의 표 한 행을 읽어 제품 기본값과 대조한다.
- 픽스처 모듈을 쓰지 않는다.

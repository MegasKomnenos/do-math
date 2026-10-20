# test_json_digests

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_json_digests.py` (90행) |
| 클래스 / 테스트 | 1 / 6 |
| 시험 대상 제품 코드 | `do_math/repository.py`의 `exact_content_hash`(그 안의 `canonical_json`, `validate_storage_value`); `do_math/file_io.py`의 `json_digest`(그 안의 `compact_json_bytes`); `do_math/observations.py`의 비공개 함수 `_raw_json`; `do_math/academic.py`의 `requirement_record`, `solution_basis`; `do_math/external.py`의 `prepare_operation`, `request_binding_current` |
| 사용하는 픽스처 모듈 | 없음 |
| 격리 표지 | 없음 |
| 시작 상태 | 1단(순수 함수 직접 호출) |

## 목적

모듈 docstring(1–9행)은 이 모듈이 "두 JSON 다이제스트 소유자와 각자가 식별하는 값"을 다룬다고 밝힌다. 상태 안의 값은 저장 값 영역을 검사하는 `repository.exact_content_hash`로 식별한다. 상태 밖의 JSON(전송 파일, 제공자 값)은 `file_io.json_digest`로 식별한다. 저장된 기록과 관측 피드백이 이 다이제스트를 싣고 다니므로, 각 공식을 값 영역 위의 고정 다이제스트로 못박는다. 그래서 구분자, 키 순서, 이스케이프, 인코딩 가운데 하나라도 바뀌면 이 모듈이 실패한다. 곧 이 모듈은 특성화 시험(characterization test)이다. 기대값은 계산 규칙이 아니라 현재 공식이 낸 16진 다이제스트 문자열 그대로다.

세 공식의 제품 좌표는 다음과 같다.
- `canonical_json`(`repository.py` 214–219행): `validate_storage_value`를 통과한 값만 받는다. `ensure_ascii=False`, `sort_keys=True`, `indent=2`, `allow_nan=False`로 직렬화하고 끝에 줄바꿈을 붙여 UTF-8로 인코딩한다. `exact_content_hash`(222–224행)는 그 SHA-256이다. `validate_storage_value`(722행~)는 부동소수(`"JSON floating-point numbers are not permitted"`), 안전 정수 범위 밖의 정수, 서로게이트 코드 포인트, 문자열이 아닌 키를 거부한다.
- `compact_json_bytes`(`file_io.py` 194–201행): 구분자 `(",", ":")`, 키 정렬, `ensure_ascii=False`, `allow_nan=False`. `json_digest`(204–206행)는 그 SHA-256이다. 부동소수를 허용한다.
- `_raw_json`(`observations.py` 95–98행): `json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True)`. 기본 구분자(`", "`, `": "`)를 쓰며, 관측 규칙 다이제스트(479행, 823행)와 제공자 응답 지문에 쓰인다. 원문 주석은 "Provider payloads can contain fractional metrics."라고 이유를 밝힌다.

## 모듈 수준 요소

- 행 15: `sys.path.insert(0, ...parents[1])`로 `scripts/`를 경로 맨 앞에 넣는다(중복 확인 없음).
- 행 16–19: 시험 대상 import. `_raw_json`은 밑줄 붙은 비공개 이름을 직접 import한다.
- `STATE_DIGESTS` (행 24): 상태 트리 값과 기대 다이제스트의 쌍 다섯 개. 주석(22–23행)은 "두 Unicode 정규형의 문자열, 이스케이프, 중첩, 빈 값, 안전 정수 경계"를 담는다고 말한다. 첫 값 `"é and é stay distinct"`의 두 é는 원문 바이트로 보면 하나는 U+00E9(조합형), 하나는 `e`+U+0301(분해형)이다. 나머지는 한글·한자·수학 기호(U+1D53D)와 따옴표·역슬래시·개행·탭 이스케이프, 빈 리스트·객체가 섞인 중첩 구조, 빈 객체·빈 리스트·빈 문자열·`None`, 그리고 `[-(2**53-1), 0, 2**53-1, True]`이다. `test_state_value_digests_stay_fixed`가 쓴다.
- `JSON_DIGESTS` (행 35): 상태 밖 값 두 개. `0.1`, `1e-07`, `1.5e300`, `-0.0`이 든 객체와, 원주율·`2.5`·`[1, 1.0]`이 든 리스트다. 주석은 "상태 트리 밖의 값은 분수 수를 가질 수 있다"고 말한다. `test_json_digests_stay_fixed`가 쓴다.
- `RULE_DIGESTS` (행 42): 관측 규칙 모양의 값 세 개. 비ASCII `id`(`"régle"`)와 `required_evidence: ["証拠"]`를 가진 규칙 하나, 빈 리스트, 중첩 객체다. 주석은 "관측 규칙과 제공자 페이로드는 원 JSON 텍스트를 유지한다"고 말한다. `test_observation_rule_digests_stay_fixed`가 쓴다.
- 행 89–90: 직접 실행하면 `unittest.main()`으로 돈다.

## DigestCharacterizationTests (행 51–86)

`unittest.TestCase`를 상속한다. 표지, 클래스 속성, 설정·정리 훅, 도우미가 없다.

### `test_state_value_digests_stay_fixed` (행 52–55)
- 성질: 상태 값의 식별 공식(`canonical_json`의 SHA-256)이 바뀌지 않는다. 두 Unicode 정규형은 서로 다른 다이제스트로 남는다.
- 준비: `STATE_DIGESTS` 다섯 쌍.
- 실행: 값마다 `exact_content_hash(value)`.
- 단언: 결과가 고정된 64자리 다이제스트 문자열과 같다.
- 대역: 없음.
- 비고: `subTest(value=...)` 케이스 다섯 개. 정규형의 구별은 기대 다이제스트에 담겨 있을 뿐이다. 조합형만 든 문자열과 비교하는 단언은 따로 없다.

### `test_json_digests_stay_fixed` (행 57–60)
- 성질: 상태 밖 JSON의 식별 공식(`compact_json_bytes`의 SHA-256)이 바뀌지 않으며, 부동소수와 음의 0을 받는다.
- 준비: `JSON_DIGESTS` 두 쌍.
- 실행: 값마다 `json_digest(value)`.
- 단언: 결과가 고정 다이제스트와 같다.
- 대역: 없음.
- 비고: `subTest` 케이스 두 개.

### `test_observation_rule_digests_stay_fixed` (행 62–65)
- 성질: 관측 규칙과 제공자 값의 원 JSON 텍스트 공식(`_raw_json`)이 바뀌지 않는다.
- 준비: `RULE_DIGESTS` 세 쌍.
- 실행: 값마다 `hashlib.sha256(_raw_json(value).encode()).hexdigest()`. 제품의 `rules_digest` 계산(`observations.py` 479행)과 같은 식을 시험 안에서 다시 적는다.
- 단언: 결과가 고정 다이제스트와 같다.
- 대역: 없음.
- 비고: `subTest` 케이스 세 개.

### `test_state_value_identity_refuses_values_outside_the_storage_domain` (행 67–70)
- 성질: 상태 값 식별은 저장 값 영역 밖의 값, 곧 부동소수와 NaN을 거부한다.
- 준비: `{"limit": 0.5}`, `[1.0]`, `{"value": float("nan")}`.
- 실행: 각각 `exact_content_hash(value)`.
- 단언: 모두 `ValueError`를 낸다. 예외 유형만 보고 메시지는 보지 않는다. 제품에서는 셋 모두 `validate_storage_value`의 `"JSON floating-point numbers are not permitted"`에 걸린다.
- 대역: 없음.
- 비고: `subTest` 케이스 세 개. 안전 정수 범위를 넘는 정수와 서로게이트 문자열 거부는 이 모듈에서 보지 않는다.

### `test_stored_academic_and_external_identities_use_the_state_value_digest` (행 72–81)
- 성질: 저장되는 학술 요구 기록, 해답 근거, 외부 작업의 요청 식별자는 모두 상태 값 다이제스트(`exact_content_hash`)로 계산된다.
- 준비: 요구 하나(`id "R"`, `scope "S"`, `assessor "research_plan"`, `criteria ["C"]`), 기록 `{"id": "K-1", "claim": "é"}`, 요청 `{"method": "GET", "url": "https://example.invalid/a"}`.
- 실행: `academic.requirement_record([...])`, `academic.solution_basis("goal", [record])`, `external.prepare_operation(request, "G-1", "S-1")`, `external.request_binding_current(operation)`.
- 단언: `requirements["sha256"]`이 `exact_content_hash({"items": requirements["items"]})`와 같다. `basis["records"]`가 `[{"id": "K-1", "sha256": exact_content_hash(record)}]`다. `operation["request_sha256"]`이 `exact_content_hash(operation["request"])`와 같다. `request_binding_current(operation)`이 참이다.
- 대역: 없음.

### `test_json_digest_refuses_non_finite_numbers` (행 83–86)
- 성질: 상태 밖 다이제스트도 유한하지 않은 수(NaN, 양·음의 무한대, 넘쳐서 무한대가 된 `1e999`)는 거부한다.
- 준비: `float("nan")`, `float("inf")`, `float("-inf")`, `float("1e999")`를 `{"value": ...}`에 담는다.
- 실행: `json_digest(...)`.
- 단언: 모두 `ValueError`를 낸다(유형만). 제품에서는 `allow_nan=False`가 막는다.
- 대역: 없음.
- 비고: `subTest` 케이스 네 개.

## 관계

- `exact_content_hash`는 이 모듈 밖에서도 많은 시험 모듈이 기대값을 계산하는 데 쓴다(`test_family_records`, `test_knowledge`, `test_knowledge_storage`, `test_reassessment`, `test_external`, `test_governance` 등). 그 모듈들은 공식이 무엇이든 제품과 시험이 같은 함수를 쓰므로 공식 변경을 잡지 못한다. 공식 자체를 고정 값으로 못박는 곳은 이 모듈뿐이다.
- `json_digest`와 같은 파일의 원자적 쓰기·지문 캐시는 `test_file_io`가 다룬다.
- 관측 규칙 다이제스트가 실제 관측 흐름에서 쓰이는 방식은 `test_observations` 등 관측 쪽 모듈이 검사한다. 이 모듈은 `_raw_json`의 출력 바이트만 고정한다.
- 픽스처 모듈을 쓰지 않는다. 도우미도 없다.

# test_state_contract

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_state_contract.py` (135행) |
| 클래스 / 테스트 | 4 / 7 |
| 시험 대상 제품 코드 | `do_math/state_contract.py`의 `StateContract`(`register_family`, `family`, `families`, `manifest`, `validate`), `default_state_contract`, `RegisteredFamily.references`; `do_math/record_schemas`의 `install`; `do_math/repository.py`의 `ResearchRepository`(`initialize`, `load`, `save_with_state`); 준비용 `execution_profiles.build_profiles`·`bind_execution`, `activities.open_activity`, `knowledge_io.ensure_ontology`, `model_policy.LIMITS`·`MODELS` |
| 사용하는 픽스처 모듈 | `research_fixtures`: `current_state`, `git_init`, `installed_contract`, `with_validator` |
| 격리 표지 | 없음 |
| 시작 상태 | 6개는 1단(계약 객체와 순수 검증 직접 호출). `test_registered_validator_enforces_current_rules` 하나는 `git_init` 저장소에 최소 상태를 직접 `initialize`한다(네 단 밖: 저장소 계층 직접 초기화) |

## 목적

모듈 docstring은 "설치된 상태 계약: 가족 등록, 등록된 검증기, 그리고 적재와 발행에서 적용되는 레코드 검사"를 다룬다고 밝힌다. `StateContract`는 레코드 가족마다 스키마, 레코드 검증기, 참조 규칙을 담는다. 제품 docstring(`state_contract.py` 행 40–45)에 따르면 가족은 계약을 만드는 동안(`record_schemas.install`)에만 등록되고 첫 사용 뒤에는 등록되지 않는다. 검증된 읽기가 계약 객체별로 캐시되고 목록(manifest) 해시가 한 번만 계산되기 때문이다. 이 모듈은 다섯 계약을 검사한다. 공유 계약은 하나이고 시험은 자기 계약을 따로 만든다. 등록은 한 번뿐이고 스키마 사본을 지킨다. 내장 스키마는 모두 유효한 JSON Schema다. 목록 해시는 등록 전까지 한 번만 계산된다. 적재와 발행은 등록된 검증기와 실행·활동 관계 규칙을 적용한다.

## 모듈 수준 요소

- 행 10: 스킬의 `scripts/` 폴더를 확인 없이 `sys.path` 맨 앞에 넣는다.
- `RECORD` (행 15–16): 최소 레코드 스키마. `id`(문자열)만 허용하고 필수로 하며 `additionalProperties=False`다. 제품의 `register_family`는 map·list 가족의 스키마가 알 수 없는 필드를 거부할 것을 요구한다(`"record schema must reject unknown fields"`). 이 상수는 그 조건을 만족하는 가장 작은 스키마다. `SchemaRegistrationTests`와 `ManifestMemoTests`가 쓴다.
- 행 134–135: 직접 실행하면 `unittest.main()`으로 이 모듈의 시험을 돈다.

## SchemaRegistrationTests (행 19–50)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다.

### `test_repositories_share_one_installed_contract_and_tests_build_their_own` (행 20–26)
- 성질: `default_state_contract()`는 프로세스에 하나뿐인 공유 객체이고, 시험이 자기 계약에 등록한 가족은 공유 계약에 새지 않는다.
- 준비: 공유 계약과, `installed_contract()`로 만든 새 계약.
- 실행: 새 계약에 `register_family("research", "fixture_record", schema=RECORD)`.
- 단언: `default_state_contract()`를 다시 부르면 같은 객체(`assertIs`)가 나온다. 공유 계약의 `family("research", "fixture_record")`는 `None`이다. 두 계약의 `_families` 키 차집합이 `{("research", "fixture_record")}` 하나다. 곧 `installed_contract`는 공유 계약과 같은 가족을 설치한다.
- 대역: 없음.

### `test_a_family_is_registered_once_and_keeps_its_own_schema_copy` (행 28–41)
- 성질: 가족은 한 번만 등록되고, 등록된 스키마는 호출자의 스키마를 나중에 바꿔도 영향받지 않는 사본이다.
- 준비: 빈 `StateContract()`와 `RECORD`와 같은 모양의 새 스키마 사전.
- 실행: `register_family("research", "sample", schema=schema)` 뒤 호출자 사본의 `id` 타입을 `"not-a-json-schema-type"`으로 망가뜨린다. 등록된 스키마로 `Draft202012Validator`를 만들어 검증한다. 같은 이름을 다시 등록한다. 설치 계약의 기존 가족 `sources`를 `shape="list"`, 검증기 람다로 다시 등록한다.
- 단언: 등록된 스키마는 `{"id": "valid"}`를 받아들이고 `{"id": 123}`에는 `jsonschema.ValidationError`를 낸다. 곧 망가뜨리기 전의 사본이다(제품 `register_family`의 `deepcopy`). 두 재등록은 모두 `ValueError`를 정규식 `"already registered"`로 던진다. 둘째 재등록은 모양과 검증기가 달라도 이름이 같으면 거부된다는 것을 보인다.
- 대역: 없음.

### `test_every_built_in_family_schema_is_a_valid_json_schema` (행 43–50)
- 성질: 설치된 모든 가족 스키마는 유효한 JSON Schema(Draft 2020-12)다.
- 준비: `default_state_contract().families()`.
- 실행: 가족마다 `jsonschema.Draft202012Validator.check_schema(family.schema)`.
- 단언: 가족 수가 50보다 크고, 모든 스키마가 `check_schema`를 통과한다(예외가 없음).
- 대역: 없음.
- 비고: `subTest(family=family.name)`로 가족마다 나눈다. 행 44의 주석은 "내장 스키마는 프로세스 시작 때 다시 검사되지 않는다. 이 시험이 그 검사다"라고 밝힌다. 곧 이 시험이 내장 스키마 유효성의 유일한 확인 장치다.

## ManifestMemoTests (행 53–66)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다.

### `test_manifest_is_computed_once_until_a_registration` (행 54–66)
- 성질: 계약의 목록 해시는 한 번 계산되어 재사용되고, 새 등록만이 그것을 다시 계산하게 한다.
- 준비: 공유 계약의 목록 `installed`와 새 설치 계약 `contract`.
- 실행: `json.dumps`를 `wraps`로 감싼 `patch.object(json, "dumps", ...)` 안에서 `contract.manifest()`를 두 번 부른다. 이어서 `memo_fixture` 가족을 등록하고 목록을 다시 부른다.
- 단언: 두 번의 결과가 같고, 그동안 `json.dumps` 호출이 정확히 1회다. 등록 뒤 목록의 `sha256`이 첫 값과 다르다. 패치 밖에서, 첫 목록은 공유 계약의 목록과 같고, 공유 계약의 목록은 이 과정 뒤에도 그대로다.
- 대역: `patch.object(json, "dumps", wraps=json.dumps)`. 실제 직렬화를 하면서 호출 수를 센다. 제품의 `manifest`는 `file_io.json_digest`를 거쳐 `json.dumps`를 부른다.

## RegisteredValidatorTests (행 69–91)

`unittest.TestCase`를 그대로 상속한다. 클래스 몸체 첫머리에 빈 줄 두 개(행 70–71)가 있고, 표지, 속성, 훅, 도우미가 없다.

### `test_registered_validator_enforces_current_rules` (행 72–91)
- 성질: 등록된 레코드 검증기는 발행할 때 현재 규칙을 적용하며, 거부된 발행은 저장된 상태를 바꾸지 않는다.
- 준비: 임시 폴더를 `git_init`하고, `new_id('RI')`로 뽑은 인스턴스를 기본 계약의 `ResearchRepository`로 `initialize`한다. 상태는 `current_state`에 원천 레코드 하나(`SO-input`, `path="original.txt"`, `sha256="a"*64`)를 담은 `sources` 목록을 더한 것이다. 이어서 `sources` 가족의 검증기를 `check_source`로 바꾼 계약을 만든다. `check_source`는 `path`가 `original.txt`가 아니면 `ValueError('repaired source rule')`를 던진다. 교체에는 `with_validator(installed_contract(), 'research', 'sources', check_source)`를 쓴다. 그 계약으로 같은 저장소와 인스턴스를 다시 연다.
- 실행: 새 계약으로 `load(head)`. 원천의 `path`를 `unexpected.txt`로 바꾸고 `save_with_state(head, instance, runtime)`.
- 단언: 적재한 머리가 `head`다. 이미 저장된 레코드는 새 규칙을 통과하므로 적재가 성공한다. 발행은 `ValueError`를 정규식 `'repaired source rule'`로 던진다. 곧 거부 사유가 등록된 검증기에서 나온 것으로 고정된다. 뒤이어 머리를 생략한 `load()`로 읽은 원천의 `path`는 여전히 `original.txt`다.
- 대역: `check_source` 검증기(가족 검증기 교체). `with_validator`는 계약의 `_families` 항목을 `dataclasses.replace`로 바꾸고 `_manifest`를 `None`으로 되돌린다.
- 비고: 실제 Git 저장소를 쓴다.

## StateContractValidationTests (행 94–131)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다.

### `test_installed_receipt_family_checks_execution_ref` (행 95–99)
- 성질: 설치된 `runtime/integrations` 가족은 레코드의 `execution_id`를 `executions` 가족에 대한 참조로 선언한다.
- 준비: 공유 계약의 `family("runtime", "integrations")`.
- 실행: `family.references({"execution_id": "EX-1"})`.
- 단언: 가족이 존재하고, 참조 집합이 `{("EX-1", "executions")}`다.
- 대역: 없음.
- 비고: 이름의 "receipt"는 `integrations` 가족을 가리킨다. 단언은 참조 선언만 보고, 없는 실행을 가리킬 때 적재가 실패하는지는 보지 않는다.

### `test_invalid_execution_and_activity_are_rejected_by_the_state_contract` (행 101–131)
- 성질: 계약 검증은 실행의 닫힌 상태 값과, 실행과 소유 활동의 짝을 강제한다.
- 준비: 실제 도메인 생산자로 유효한 상태를 만든다. `execution_profiles.build_profiles`에 모델 정책 `LIMITS`·`MODELS`, `observation_mode="event_driven"`, `max_input_bytes=500000`, effort `medium`, operator effort `high`, operator 제한 시간 600초, scholarly 사용, `claude_only_assigned_model=False`를 준다. 그 결과 가운데 `role_profile_refs`를 뺀 가족과 `object_format="sha1"`, 빈 `knowledge`·`expositions`를 `current_state`의 instance에 더한다. `knowledge_io.ensure_ontology`로 온톨로지를 채운다. `activities.open_activity`로 `research_work` 활동 `AT-1`을 연다. `research_work` 역할 프로필에 `bind_execution`한 실행 `EX-1`(`status="running"`)을 넣고, 활동의 `assigned_execution_ids`를 `["EX-1"]`로 둔다.
- 실행: `default_state_contract().validate(instance, runtime)`. 이어서 실행 상태를 `"teleporting"`으로 바꾼 사본과, 활동의 배정 목록을 비운 사본을 각각 검증한다.
- 단언: 원래 상태는 예외 없이 통과한다. 상태 값을 바꾼 사본은 `ValueError`를 정규식 `"executions/EX-1/status"`로 던진다. 곧 사유가 그 필드 경로로 고정된다. 배정을 비운 사본은 `ValueError`를 `"EX-1: execution has no matching activity"`로 던진다.
- 대역: 없음.
- 비고: 행 102–103의 주석은 이렇게 밝힌다. "검사(inspection)는 적재된 상태만 받는다. 적재가 실행 상태와 활동 소유를 검증하므로, 그것들이 거부되는 곳은 계약이다." `test_state_checks`가 같은 종류의 변형을 적재 단계 거부로 확인하는 것과 짝을 이룬다.

## 관계

- `test_state_checks`는 적재된 상태에 대한 점검(`state_checks`)과, 적재에서 거부되는 변형(`assertRejectedAtLoad`)을 검사한다. 이 모듈의 마지막 테스트는 그 거부가 계약 검증에서 나온다는 것을 계약 층에서 확인한다.
- `test_repository`는 이 계약을 쓰는 저장소의 검증된 읽기 재사용(`ValidatedReadReuseTests`, 계약 객체별 캐시)과, 부모와 같은 레코드의 검사 생략을 검사한다. 이 모듈의 제품 docstring이 말하는 "계약 객체별 캐시" 규칙이 그쪽의 전제다.
- `test_unicode_flow`는 `installed_contract()`에 시험용 가족 `unicode_fixture`를 등록해 쓴다. `test_repository`는 `installed_contract()`를 가족 등록 없이 쓴다. 하나는 공유 계약과 다른 계약 객체로 적재하는 데 쓰고(`test_one_head_is_validated_once_across_repository_objects`), 다른 하나는 `with_validator`로 `governance_sources` 검증기를 바꾸는 데 쓴다(`test_unchanged_records_skip_record_local_and_immutable_hash_checks`). 이 모듈의 첫 테스트는 시험이 자기 계약에 등록한 가족이 공유 계약에 새지 않음을 보인다.
- 픽스처 의존: `research_fixtures.current_state`, `git_init`, `installed_contract`, `with_validator`.
- 이 모듈에만 있는 도우미는 없다.

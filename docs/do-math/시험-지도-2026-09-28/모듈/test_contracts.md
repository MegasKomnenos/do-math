# test_contracts

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_contracts.py` (200행) |
| 클래스 / 테스트 | 1 / 16 |
| 시험 대상 제품 코드 | `do_math/contracts.py`의 `ROLES`, `schema_for`, `action_schema`, `with_integration_schema`, `schema_reference`, `identify_schema`, `disposition_schema`, `TASK_CANDIDATE`, `MANIFEST_SCHEMA`, `reading_map`, `prompt_documents`, `render_prompt`; `do_math/submission.py`의 `extension_schema`; `do_math/review_cycle.py`의 `stage_schema`, `research_schema`, `research_request_schema`; `do_math/governance.py`의 `interpretation_schema`; `do_math/integration.py`의 `impact_review_response_schema`; `do_math/record_schemas/__init__.py`의 `config_schema`; `do_math/scheduled_operator.py`의 `repair_report_schema` |
| 사용하는 픽스처 모듈 | `research_fixtures`: `review_items`. `record_fixtures`: `two_observation_output` |
| 격리 표지 | 없음 |
| 시작 상태 | 1단(스키마 생성기와 검증기를 직접 호출). `test_role_document_missing_fails`만 임시 스킬 루트를 만든다 |

## 목적

모듈 docstring은 없다. 이 모듈은 `contracts.py`가 정의하는 역할 응답 계약(`do-math-cli/5`)을 검사한다. 대상은 스키마의 형태, 닫힘, 식별, 그리고 역할 문서 읽기와 프롬프트 조립이다. 검사는 일곱 무리로 나뉜다.
1. 확장 스키마(`extension_schema`)의 필수 필드: 지식 변경의 `impact_set`, 학술 해소의 `evidence_refs`.
2. 스키마 식별: 변형마다 다른 `$id`, 봉투 적용의 멱등성.
3. 공유 참조 모양: 실행 프로필 참조가 `id`, `revision`, `sha256`의 봉인 형태인지.
4. 스키마 생성기의 독립 사본성과 모든 역할 스키마의 닫힘.
5. 역할별 판정 값의 열거.
6. 읽기 지도와 프롬프트 조립.
7. 개별 역할 스키마의 필드 구성: 연구 계획의 필수 필드, 과제 후보의 완료 의무와 범위, 운영 점검의 처분, 의도 해석의 봉투, 검토 범위 평가의 초기 좌석, 통합 묶음 선언의 선택성.

`contracts.py` 모듈 docstring의 첫 줄은 "Role prompt and output schemas for the CLI adapters of every provider."이고, 이어지는 문단이 "The ``do-math-cli/5`` output schemas describe newly requested CLI responses."라고 말한다.

## 모듈 수준 요소

- 행 11: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리다.
- 행 12–15: `contracts` 모듈, `ROLES`, `reading_map`, `prompt_documents`, `render_prompt`, `schema_for`와 픽스처 `review_items`, `two_observation_output`을 import한다. `jsonschema`는 행 9에서 import한다.
- 행 199–200: 직접 실행하면 `unittest.main()`으로 이 모듈의 시험을 돈다.

## ContractTests (행 18–196)

`unittest.TestCase`를 그대로 상속한다. 표지, 설정 훅, 클래스 도우미가 없다. 두 테스트는 테스트 안에 지역 함수(`containers`, `objects`)를 둔다.

### `test_knowledge_change_requires_a_declared_impact_set` (행 19–27)
- 성질: 연구 수행의 확장 문서에서 지식 변경(`knowledge_changes`) 행은 `impact_set`을 반드시 선언해야 한다.
- 준비: `submission.extension_schema({"role": "research_work"})`와 변경 행 하나. 행은 `id='KN-source'`, `changes.statement='Corrected'`, `reason`, `impact_set=['TK-consumer']`를 갖는다.
- 실행: `jsonschema.validate`로 행을 담은 확장을 검증하고, `impact_set`을 뺀 행으로 다시 검증한다.
- 단언: 첫 검증은 통과하고, 둘째는 `jsonschema.ValidationError`를 던진다. 예외 유형만 본다. 제품 스키마의 필수 목록은 `["id", "changes", "reason", "impact_set"]`이다.
- 대역: 없음.

### `test_exact_schema_identity_distinguishes_variants_and_is_idempotent` (행 29–34)
- 성질: 같은 역할이라도 변형된 스키마는 다른 식별자를 갖고, 봉투 적용은 멱등이다.
- 준비: 연구 준비의 두 행동 스키마. 보통 `action_schema({"role": "research_preparation"})`와 평가용 `action_schema({"role": "research_preparation", "assessment_targets": []})`다. 평가용은 `model_policy.preparation_only`가 참이 되어 `candidates.maxItems=0`인 변형이다.
- 실행: 두 스키마의 `$id`를 비교한다. `with_integration_schema(ordinary)`를 적용해 원본과 비교한다. 두 스키마의 `schema_reference`를 비교한다.
- 단언: 두 `$id`가 다르다. `identify_schema`는 `$id`를 뺀 정준 내용의 SHA-256으로 URI를 만든다. `with_integration_schema(ordinary)`는 `ordinary`와 같다. `schema_reference`(가족, `$id`, 전체 해시)도 서로 다르다.
- 대역: 없음.

### `test_profile_references_use_the_sealed_provider_identity` (행 36–45)
- 성질: 과제 후보의 `profile_refs` 항목과 검토 범위 평가의 `selected_profile_ref`는 같은 봉인 프로필 참조 모양(`id`, `revision`, `sha256`)만 받는다.
- 준비: 참조 `{"id": "EP-test", "revision": 1, "sha256": "a"*64}`. 모양 둘은 `contracts.TASK_CANDIDATE`의 `profile_refs.items`와 `review_cycle.stage_schema("scope")`의 `scope_assessment.properties.selected_profile_ref`다.
- 실행: 모양마다 `Draft202012Validator(shape).is_valid`를 부른다.
- 단언: 올바른 참조는 유효하다. 무효 셋은 모두 무효다: 문자열 `"EP-test"`, `version` 필드를 쓴 객체, `sha256='wrong'`인 객체. 제품 `PROFILE_REF`는 닫힌 객체이고 `revision`은 1 이상의 정수, `sha256`은 `SHA256_SCHEMA`다.
- 대역: 없음.

### `test_academic_resolution_carries_real_evidence_references` (행 47–52)
- 성질: 연구 계획의 학술 해소(`academic_resolutions`) 행은 증거 참조를 반드시 담는다.
- 준비: `extension_schema({"role": "research_plan"})`의 `academic_resolutions.items` 모양과 행 `{"id": "ER-1", "decision": "resolved", "evidence": "Exact assessment", "evidence_refs": ["EX-evidence"]}`.
- 실행: 행과, `evidence_refs`를 뺀 행을 각각 검증한다.
- 단언: 원 행은 유효하고, 뺀 행은 무효다. 제품 모양은 `evidence_refs`에 `minItems: 1`, `uniqueItems: True`를 둔다.
- 대역: 없음.

### `test_schema_builders_return_copies_that_share_no_node` (행 54–97)
- 성질: 스키마 생성기의 결과는 모듈 전역과 컨테이너를 공유하지 않고, 결과 안에서도 같은 컨테이너가 두 번 나오지 않는다. 그래서 호출자가 노드를 제자리에서 바꿔도 다른 필드나 나중에 만든 스키마가 바뀌지 않는다(docstring).
- 준비: 지역 함수 `containers(value)`는 사전과 목록 노드를 모두 모은다. 영향 검토 요청 `request`를 만든다: `integration_id='IN-1'`, 해시 자리 값들, `plans.scope.digest`. 생성 결과는 다음을 모은다.
  - 모든 `ROLES`의 `schema_for`
  - 네 역할의 `action_schema`: `research_preparation`, `research_work`, `maintenance`, `intent_interpretation`
  - `disposition_schema()`
  - `extension_schema({"role": "research_work", "review_cycle_id": "RC-1"})`
  - `integration.impact_review_response_schema(request)`
  - 다섯 단계의 `review_cycle.stage_schema`: `scope`, `initial`, `organize`, `answer`, `judge`
  - `research_schema()`, `research_request_schema()`
  - 두 단계의 `governance.interpretation_schema`: `interpret`, `check`
  - `record_schemas.config_schema()`
  - `scheduled_operator.repair_report_schema(diagnosed=True)`
- 실행: `sys.modules`에서 `do_math`와 `do_math.*` 모듈의 모든 전역 값에 든 컨테이너 `id` 집합을 만든다. 생성 결과마다 컨테이너 `id` 목록을 만든다.
- 단언: 결과마다 `id` 목록에 중복이 없다(메시지 "a node appears twice in the result"). 결과의 `id` 집합과 전역 `id` 집합의 교집합이 비어 있다(메시지 "the result holds a module-global node").
- 대역: 없음.
- 비고: `subTest(builder=name)`의 케이스는 위 생성 결과의 이름 전부다. 역할 수를 `ROLES`에서 가져오므로 역할이 늘면 케이스도 는다. 전역 검사는 그 시점에 적재된 `do_math` 모듈만 본다.

### `test_every_role_has_closed_schema` (행 99–116)
- 성질: 모든 역할 스키마에서, 어떤 깊이든 `properties`를 선언한 객체는 선언하지 않은 필드를 거부한다(docstring).
- 준비: 지역 생성기 `objects(node, path)`가 `properties`를 가진 모든 사전과 그 경로를 낸다.
- 실행: `ROLES`의 역할마다 `schema_for(role)`을 훑는다.
- 단언: 모든 객체의 `additionalProperties`가 `False` 자체다(`assertIs`). 스키마의 `required`에 `summary`, `used_sources`, `questions`가 들어 있다. `Draft202012Validator.check_schema`가 통과한다.
- 대역: 없음.
- 비고: `subTest(path=path)`의 케이스는 역할별 경로 전부다.

### `test_invalid_decisions_fail` (행 118–134)
- 성질: 판정 역할 넷의 판정 값은 열거된 값만 받는다.
- 준비: 공통 기반은 `summary`, `used_sources`, `questions`와 통합 묶음 `IN-review` 하나다. 역할별 필드는 다음과 같다.
  - `task_contract_review`: `review_items(["TK-1"], next_owner="research_preparation")`. 모든 계약 항목을 승인한다.
  - `identity_review`: `decision='match'`.
  - `goal_audit`: `decision='satisfied'`.
  - `operational_review`: `disposition.kind='continue'`와 `basis_refs`, `next_owner`, `reason`, `next_review=None`.
- 실행: 역할마다 `Draft202012Validator(schema_for(role))`로 원 값을 검증한다. 이어서 판정 값을 `"invalid"`로 바꾸어 다시 검증한다. 바꾸는 자리는 역할마다 다르다: 계약 검토는 `item_reviews[0].decision`, 운영 점검은 `disposition.kind`, 나머지는 `decision`이다.
- 단언: 원 값은 유효하고, 바꾼 값은 무효다. 실패 메시지는 역할 이름이다.
- 대역: 없음.

### `test_role_document_missing_fails` (행 136–145)
- 성질: 읽기 지도가 선언한 역할 계약 문서가 없으면 문서 적재가 실패한다.
- 준비: 임시 스킬 루트를 만든다. 빈 `계약/` 폴더를 두고, 실제 설치본의 `SKILL.md`와 `references/` 전체를 복사하며, `GLOSSARY.md`는 `"x"`로 쓴다.
- 실행: `prompt_documents("research_work", skill_root=root)`.
- 단언: `FileNotFoundError`가 난다. 예외 유형만 본다. `계약/` 아래 문서가 없으므로, 읽기 지도의 `research_work` 행이 선언한 `계약/연구-수행.md`를 읽을 때 난다.
- 대역: 없음.

### `test_prompt_contains_actual_documents_context_and_schema` (행 147–154)
- 성질: 렌더된 프롬프트는 실제 문서, 정준 맥락, 출력 스키마, 전달 규칙을 담는다.
- 준비: 실제 설치본. 맥락은 `{"z": 1, "a": "입력"}`이다.
- 실행: `render_prompt("research_work", context)`.
- 단언: 프롬프트가 여섯 조각을 포함한다.
  - 문서 머리 `DOCUMENT SKILL.md`, `DOCUMENT GLOSSARY.md`, `DOCUMENT 계약/연구-수행.md`.
  - 키가 정렬되고 공백이 없으며 한글이 이스케이프되지 않은 맥락 `{"a":"입력","z":1}`. 제품은 `sort_keys=True`, `ensure_ascii=False`, 구분자 `(",", ":")`를 쓴다.
  - 스키마의 계약 ID `"do-math-cli/5"`.
  - 문구 "without Markdown or text outside JSON".
- 대역: 없음.

### `test_declared_role_documents_are_complete` (행 156–157)
- 성질: 실제 `SKILL.md`의 읽기 지도는 모든 역할에 문서를 배정한다.
- 준비: 실제 설치본.
- 실행: `reading_map()`.
- 단언: 결과의 키 집합이 `set(ROLES)`와 같다.
- 대역: 없음.

### `test_plan_assessment_fields_are_required` (행 159–163)
- 성질: 연구 계획 응답은 처분, 준비 요청, 목표 감사 여부, 과제 평가를 반드시 담고, 과제 평가 행의 필수 필드는 정해진 다섯 개다.
- 준비: `schema_for("research_plan")`.
- 실행: 스키마를 읽는다.
- 단언: `required`에 `dispositions`, `preparation_requests`, `goal_audit`, `task_assessments`가 있다. `task_assessments.items.required`의 집합이 `{"task_id", "decision", "reason", "item_dispositions", "unresolved"}`와 같다.
- 대역: 없음.

### `test_structured_task_candidate_has_one_completion_authority` (행 165–168)
- 성질: 과제 후보는 구조화된 완료 의무와 객체 범위를 갖는다.
- 준비: `schema_for("research_preparation")`의 `candidates.items.properties`.
- 실행: 스키마를 읽는다.
- 단언: `completion_obligations` 속성이 있다. `scope.type`이 `"object"`다.
- 대역: 없음.
- 비고: 이름의 "one completion authority"(완료 권한이 하나뿐)는 직접 단언하지 않는다. 다른 완료 필드가 없음을 보지 않고, `completion_obligations`의 존재와 `scope`의 객체 형식만 확인한다.

### `test_operational_response_uses_six_dispositions` (행 170–172)
- 성질: 운영 점검 응답에는 처분(`disposition`) 속성이 있다.
- 준비: `schema_for("operational_review")["properties"]`.
- 실행: 스키마를 읽는다.
- 단언: `disposition` 키가 있다.
- 대역: 없음.
- 비고: 이름은 여섯 처분을 말하지만, 단언은 `disposition` 속성의 존재만 확인한다. 처분 종류의 수는 보지 않는다. 제품 `disposition_schema`의 변형은 실제로 여섯이다: `continue`, `repair`, `resume`, `retry`, `task_disposition`, `user_decision`.

### `test_specialized_role_schema_uses_same_envelope` (행 174–180)
- 성질: 전문 역할(의도 해석의 `check` 단계) 스키마도 일반 역할과 같은 봉투를 쓴다.
- 준비: `action_schema({"role": "intent_interpretation", "stage": "check"})`와 `governance.interpretation_schema("check")`.
- 실행: 두 스키마의 속성을 비교한다.
- 단언: 해석 스키마의 속성이 모두 행동 스키마에 있다. 행동 스키마의 속성에 `integration_bundles`가 있다. `required`에는 `integration_bundles`가 없다. 제품 `with_integration_schema`는 `integration_bundles`와 `repair_responses`를 더하고 `integration_bundles`를 필수 목록에서 뺀다.
- 대역: 없음.

### `test_scope_planning_schema_reaches_domain_scope_validator` (행 182–186)
- 성질: 검토 범위 단계 스키마는 범위 평가와 그 초기 좌석(`initial_slots`)을 담는다.
- 준비: `review_cycle.stage_schema("scope")["properties"]`.
- 실행: 스키마를 읽는다.
- 단언: `scope_assessment`가 있고, 그 속성에 `initial_slots`가 있다.
- 대역: 없음.
- 비고: 이름은 "domain scope validator"에 이른다고 말하지만 단언은 스키마 속성의 존재만 본다. 스키마가 실제로 범위 검증기에 도달하는지는 `test_review_scope_wire`의 `test_one_real_response_contract_reaches_the_consumer`가 본다.

### `test_manifest_is_optional_but_explicit_declarations_remain_typed` (행 188–196)
- 성질: 통합 묶음 선언(`integration_bundles`)은 생략할 수 있지만, 적었다면 형식을 지켜야 한다.
- 준비: `schema_for("research_work")`와 `two_observation_output()`에서 `integration_bundles`를 뺀 출력. 그 출력은 관찰 지식 두 개를 담은 연구 수행 출력이다.
- 실행: 뺀 출력을 검증하고, 이어서 `integration_bundles`를 `None`, `[]`, `[{}]`로 둔 출력을 각각 검증한다.
- 단언: `required`에 `integration_bundles`가 없다. 뺀 출력의 오류 목록은 `[]`다. 세 값은 모두 오류가 하나 이상이다. 제품 `MANIFEST_SCHEMA`는 `minItems: 1`인 배열이고, 항목은 `BUNDLE_SCHEMA`다.
- 대역: 없음.
- 비고: `subTest(value=...)`의 세 케이스는 `None`, `[]`, `[{}]`다.

## 관계

- 같은 제품 기능의 다른 층: 읽기 지도와 프롬프트 조립은 `test_reading_map`이 순서와 바이트 보존까지 더 자세히 본다. 두 모듈 모두 누락 문서의 `FileNotFoundError`를 확인한다(`test_role_document_missing_fails`, `test_reading_map.test_missing_required_reference_is_not_silently_omitted`). 통합 묶음의 기본 분할과 적용은 `test_integration_bundles`가 본다. 검토 범위 스키마의 소비는 `test_review_scope_wire`와 `test_review_policy`가 본다. 영향 검토 응답 스키마는 `test_impact_review`의 `test_designated_review_has_producible_closed_schema_and_exact_scope`가 더 자세히 본다.
- 픽스처 의존: `research_fixtures.review_items`(모든 계약 항목을 같은 판정으로 검토한 출력), `record_fixtures.two_observation_output`(관찰 지식 둘과 묶음 둘을 가진 연구 수행 출력).
- 이 모듈에만 있는 도우미: 테스트 안의 지역 함수 `containers`, `objects`.
- 겹치거나 보완하는 시험: 닫힌 스키마 검사(`test_every_role_has_closed_schema`)와 노드 비공유 검사(`test_schema_builders_return_copies_that_share_no_node`)는 서로 다른 생성기 집합을 본다. 앞의 것은 `schema_for`의 역할 스키마만 보고, 뒤의 것은 단계, 확장, 설정, 수리 보고 스키마까지 넓게 본다.

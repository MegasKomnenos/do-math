# test_integration_bundles

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_integration_bundles.py` (279행) |
| 클래스 / 테스트 | 2 / 18 |
| 시험 대상 제품 코드 | `do_math/integration.py`의 `inspect_bundles`, `split_bundles`, `apply_bundles`, `preview_bundles`, `member_values`, `protocol_output`, `split_research`, `mutation_members`; `do_math/submission.py`의 `payload_issues`; `do_math/contracts.py`의 `schema_for`; 첫 적용 테스트에서 `do_math/repository.py`의 `ResearchRepository`(`initialize`, `validate_candidate`, `save_validated`, `load`), `do_math/knowledge_io.py`의 `import_candidate`, `ensure_ontology`, `do_math/execution_profiles.py`의 `build_profiles`, `bind_execution`, `do_math/activities.py`의 `open_activity` |
| 사용하는 픽스처 모듈 | `record_fixtures`: `observation_knowledge`, `research_work_context`, `two_observation_output`. `research_fixtures`: `git_init`, `current_state` |
| 격리 표지 | 없음 |
| 시작 상태 | 대부분 1단(`integration` 함수에 사전 출력과 맥락, 콜백 람다를 넘김). `test_bundle_receipt_and_records_share_real_git_publication`만 네 단 밖으로, `git_init`으로 만든 실제 Git 저장소에 `current_state` 최소 상태를 직접 발행한다 |

## 목적

모듈 docstring은 이 모듈이 통합 묶음(integration bundle)을 시험한다고 밝힌다. 생산자 응답이 묶음으로 어떻게 나뉘고, 검사되고, 미리보기되고, 적용되는지를 본다. 적용은 설치된 `integration` 모듈을 거치며, 대상은 메모리 상태나 실제 Git 상태다. 영수증, 재시도, 부분 수용은 각 적용이 남긴 상태에서 단언한다. `integration.py`의 docstring은 "Atomic response bundles. No mathematical independence is certified."로 시작한다. 이어서 도메인 변경, 현재성과 권한 확인, Git CAS 발행은 명시적 콜백이며, 실패한 발행은 결코 수용을 돌려주지 않는다고 밝힌다.

이 모듈이 다루는 규칙은 다섯 무리다.
- 기본 묶음: 선언이 없으면 응답 전체가 결정적인 묶음 하나가 된다.
- 명시 선언이 필요한 경우: 개정과 부분 수용 재시도.
- 구조 검사: 구성원, 단일 묶음, 참조 폐포, 변경 루트.
- 적용 순서: 현재성 → 적용 → 후보 검증 → 발행.
- 영수증: 멱등 재생, 실패 묶음만의 재시도, 발행 실패의 비수용.

## 모듈 수준 요소

- 행 12: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리다.
- 행 13–16: `contracts`, `integration`, `submission`, `exact_content_hash`와 픽스처 `observation_knowledge`, `research_work_context`, `two_observation_output`, `git_init`을 import한다.
- 행 278–279: 직접 실행하면 `unittest.main()`으로 이 모듈의 시험을 돈다.

픽스처의 공통 입력은 둘이다. `two_observation_output()`은 관찰 지식 `A`, `B`를 가진 연구 수행 출력이다. 명시 묶음 둘을 갖는데, `IN-A`는 `output`과 `output/knowledge/0`을, `IN-B`는 `output/knowledge/1`을 구성원으로 둔다. `research_work_context()`는 역할 `research_work`(대상 `TK-1`), 스냅숏 `fixed`, 관찰 종류 정의를 가진 맥락이다. 연구 수행은 `split_research`가 참이므로 지식과 관계 행이 독립 구성원이 된다.

## DefaultBundleTests (행 19–63)

`unittest.TestCase`를 그대로 상속하고 표지와 도우미 메서드가 없다.

`setUp` (행 20–27)은 세 가지를 둔다.
- `self.api`: `integration` 모듈.
- `self.context`: `research_work_context()`에 세 필드를 더한 맥락. `execution_id='EX-default'`, 행동 `AC-default`(역할 `research_work`, `grant_id='GR-default'`), `grants=[{"id": "GR-default"}]`이다.
- `self.output`: `integration_bundles`를 뺀 `two_observation_output()`.

### `test_missing_manifest_is_one_deterministic_unit_without_editing_original` (행 29–42)
- 성질: 묶음 선언이 없는 응답은 결정적인 기본 묶음 하나가 된다. 원 응답은 바뀌지 않고, 묶음 ID는 응답 값과 실행이 바뀌면 달라진다.
- 준비: `setUp`의 출력과 맥락. 비교용 `deepcopy`를 떠 둔다.
- 실행: `inspect_bundles(output, {}, context)`와 `split_bundles(...)`. 같은 입력의 깊은 사본으로 한 번 더 나눈다. `report`를 바꾼 출력, `execution_id='EX-other'`인 맥락으로도 각각 나눈다.
- 단언:
  - 검사 결과가 `[]`다.
  - 묶음이 1개이고, 구성원 집합이 `{"output", "output/knowledge/0", "output/knowledge/1"}`이다.
  - `authority_refs`가 `["GR-default"]`, `impact_set`이 `[]`다.
  - 원 출력이 사본과 같다.
  - 깊은 사본의 분할 결과가 같다.
  - `report`를 바꾸거나 실행을 바꾸면 `integration_id`가 달라진다.
- 대역: 없음.
- 비고: 제품 `protocol_output`은 실행 ID, 스냅숏, 행동, 선언, 구성원 값의 해시로 `IN-<hash>`를 만든다. 권한 참조는 행동의 `grant_id`와 제어 결합의 `grant_id`에서 가져온다.

### `test_revision_and_partial_acceptance_still_require_explicit_declarations` (행 44–54)
- 성질: 기존 객체의 개정이나 부분 수용 뒤의 재시도에는 기본 묶음을 쓸 수 없다. 명시 선언이 필요하다.
- 준비: 선언 없는 출력에 대한 다섯 경우를 둔다.
  1. 맥락에 `accepted_integration_ids=['IN-earlier']`.
  2. 맥락에 `accepted_response`.
  3. 행동에 `revision_targets=['TK-old']`.
  4. 확장에 `knowledge_changes=[{"id": "KN-old"}]`.
  5. 확장에 `task_dispositions=[{"task_id": "TK-old"}]`.
  여섯째로 출력 `{"candidates": [{"revises_task_id": "TK-old"}]}`를 둔다.
- 실행: 각 경우에 `inspect_bundles`.
- 단언: 여섯 경우 모두 결과가 비어 있지 않다. 거부 사유는 고정하지 않는다. 제품은 "revisions and partially accepted retries require explicit integration_bundles"를 `integration.manifest` 문제로 낸다.
- 대역: 없음.
- 비고: `subTest(extensions=..., context=...)`의 다섯 케이스는 위 1–5다. 여섯째는 `subTest` 밖에서 확인한다.

### `test_explicit_split_stays_split_and_orphan_impact_fails_structurally` (행 56–63)
- 성질: 명시적으로 나눈 묶음은 그대로 나뉜다. 기존 객체를 변경하지 않는 묶음이 영향 집합을 선언하면 구조 오류다.
- 준비: 명시 묶음 둘을 가진 `two_observation_output()`.
- 실행: `split_bundles`와 `inspect_bundles`를 부른다. 이어서 `IN-A`의 `impact_set`을 `["read-source"]`로 바꾸고 다시 검사한다.
- 단언: 분할 결과가 2개이고, 첫 검사는 `[]`다. 두 번째 검사에는 `rule_id == "integration.mutation_root"`이고 `integration_id == "IN-A"`인 문제가 있다(제품 "bundle declares impact without an existing mutation root"). 검사 뒤에도 출력의 `impact_set`은 `["read-source"]` 그대로다.
- 대역: 없음.

## BundleApplicationTests (행 66–275)

`unittest.TestCase`를 그대로 상속하고 훅과 도우미가 없다. 대부분의 테스트는 `apply_bundles`나 `preview_bundles`에 콜백 네 개를 람다로 넘긴다: `apply_bundle`, `validate_current`, `validate_candidate`, `publish`. 그리고 결과 사전(`instance`, `runtime`, `bundles`, `issues`, `retry_bundle_ids`, `status`)을 단언한다.

### `test_bundle_receipt_and_records_share_real_git_publication` (행 67–137)
- 성질: 묶음의 영수증과 레코드는 같은 Git 발행(커밋)에 함께 실린다. 한 묶음이 실패하면 다른 묶음만 발행된 부분 수용이 되고, 실패 묶음만 다시 보내 완성할 수 있다. 미리보기는 저장소도 입력도 바꾸지 않는다.
- 준비: 네 단 밖.
  1. 임시 폴더에 `git_init`을 하고 `ResearchRepository(root, "RI-01ARZ3NDEKTSV4RRFFQ69G5FAV")`를 만든다.
  2. `build_profiles`에 명시 설정을 넘겨 프로필 상태를 만든다. 설정은 모델 한도, 관찰 방식 `event_driven`, 입력 상한 500000 등이다.
  3. `current_state`로 빈 지식과 해설, 프로필을 가진 상태를 만들고 `ensure_ontology`를 적용한다.
  4. 활동 `AT-1`을 열고, 연구 수행 프로필에 묶인 실행 중 실행 `EX-1`을 배정한 뒤 `initialize`로 첫 head를 발행한다.
  콜백은 셋이다. `apply`는 묶음의 지식을 `knowledge_io.import_candidate`로 후보로 들여온다. `validate`는 `repo.validate_candidate(i, r, head)`를 부른다. `publish`는 `repo.save_validated(head, validated)`로 발행하고 `head`를 갱신한다.
- 실행: 세 번 부른다.
  1. `preview_bundles`로 두 묶음을 미리보기한다.
  2. 지식 `B`의 `kind`를 `"undefined_kind"`로 바꾼 출력을 `apply_bundles`로 적용한다.
  3. 저장소를 `load`해 `IN-A` 영수증을 읽고, `B`만 가진 재시도 출력(묶음 `IN-B`)을 적용한다. 재시도 맥락에는 `accepted_response`로 영수증의 ID와 `response_sha256`을 싣는다.
- 단언:
  - 미리보기 `status`는 `"accepted"`다. 호출 전후의 `(instance, runtime)`이 같고, `head`가 저장소의 현재 head와 같다. 곧 발행하지 않았다.
  - 첫 적용의 `status`는 `"partial"`이고, `retry_bundle_ids`는 `["IN-B"]`다. 적재한 지식 제목은 `{"A"}`다.
  - 재시도 `status`는 `"accepted"`다. 저장소 head가 마지막으로 발행한 `head`와 같다. 지식 제목은 `{"A", "B"}`, 영수증 키는 `{"IN-A", "IN-B"}`다.
  - `git rev-parse <head>^`로 얻은 부모 커밋에는 지식 `{"A"}`와 영수증 `{"IN-A"}`만 있다. 영수증과 레코드가 같은 커밋에 함께 실렸다는 뜻이다.
- 대역: 없음. 실제 Git 저장소를 쓰고, 콜백은 제품 함수를 부르는 얇은 람다다.
- 비고: 실제 외부 자원으로 `subprocess.check_output(["git", "-C", ..., "rev-parse", head + "^"])` Git 자식 프로세스를 직접 부른다. `ResearchRepository`의 쓰기와 읽기도 `git_store`를 통해 Git 자식 프로세스를 쓴다.

### `test_local_schema_failure_does_not_block_valid_bundle` (행 139–149)
- 성질: 한 묶음의 스키마 오류는 그 묶음에만 붙고, 유효한 다른 묶음의 적용을 막지 않는다.
- 준비: `two_observation_output()`에서 지식 `B`의 `statement`를 지운다.
- 실행: `submission.payload_issues(output, schema_for("research_work"), research_work_context(), {}, 임시폴더)`로 문제를 얻는다. 그 문제를 `submission_issues`로 넘겨 `apply_bundles`를 부른다. 적용 콜백은 인스턴스에 묶음 ID를 기록한다.
- 단언: 문제들의 `integration_id` 집합이 `{"IN-B"}`다. 결과 인스턴스가 `{"IN-A": True}`다.
- 대역: 콜백 람다(적용 기록, 나머지는 무동작).

### `test_structural_failure_never_crashes_on_wrong_record_type` (행 151–155)
- 성질: 레코드 자리에 잘못된 유형(`None`)이 있어도 구조 검사는 예외 없이 목록을 돌려준다.
- 준비: 지식 `A`를 `None`으로 바꾼 출력.
- 실행: `inspect_bundles(output, {}, research_work_context())`.
- 단언: 결과가 `list`다. 내용은 단언하지 않는다.
- 대역: 없음.

### `test_structural_top_level_failure_returns_without_candidate_application` (행 157–167)
- 성질: 응답이나 확장의 최상위 모양이 잘못되면, 콜백을 하나도 부르지 않고 입력 상태 그대로 반려한다.
- 준비: 세 경우. 출력 `None`, 출력 `[]`, 확장 `[]`(출력은 정상).
- 실행: `apply_bundles({"original": True}, {}, ...)`. 네 콜백은 모두 호출되면 `self.fail`로 시험을 실패시킨다.
- 단언: `status`는 `"returned"`이고, `issues`는 비어 있지 않으며, `instance`는 `{"original": True}`다.
- 대역: `self.fail`을 부르는 콜백 넷(호출 금지 감시).
- 비고: `subTest(output=유형이름, extensions=유형이름)`의 세 케이스는 `NoneType/dict`, `list/dict`, `dict/list`다. 제품은 전역 문제(`integration_id` 없음)가 있으면 적용에 들어가지 않는다.

### `test_proposed_kind_and_consumer_must_share_bundle` (행 169–175)
- 성질: 새로 제안한 지식 종류와 그 종류를 쓰는 레코드는 같은 묶음에 있어야 한다.
- 준비: 지식 `A`의 `kind`를 `"experiment"`로 바꾼다. 종류 정의 `experiment`를 확장 `kind_definitions/0`으로 두고, 그 구성원을 `IN-B`에 넣는다.
- 실행: `inspect_bundles(output, extensions, research_work_context())`.
- 단언: 문제의 `rule_id` 집합에 `"integration.reference_closure"`가 있다. 제품은 레코드의 `kind`를 참조로 보고, 새 식별자(종류 `token`)를 가진 묶음과 다르면 "merge bundles referencing new object"를 낸다.
- 대역: 없음.

### `test_preview_applies_candidate_without_publishing_or_mutating_input` (행 177–184)
- 성질: 미리보기는 같은 후보 경로를 돌되 발행하지 않고 입력을 바꾸지 않는다.
- 준비: 빈 인스턴스 `original`.
- 실행: `preview_bundles(original, {}, two_observation_output(), {}, research_work_context(), ...)`. 적용 콜백은 묶음 ID를 기록한다.
- 단언: `original`이 `{}` 그대로다. 결과 인스턴스는 `{"IN-A": True, "IN-B": True}`이고, `mode`는 `"preview"`다.
- 대역: 콜백 람다.
- 비고: 제품 `preview_bundles`는 `publish`를 무동작으로 둔 `apply_bundles`이며, 수용된 묶음의 상태를 `preview_passed`로 바꾼다.

### `test_missing_member_is_rejected` (행 186–190)
- 성질: 묶음은 존재하지 않는 구성원을 가리킬 수 없다.
- 준비: `IN-B`의 구성원을 `["output/relations/0"]`로 바꾼다. 관계 행은 없다.
- 실행: `inspect_bundles`.
- 단언: `rule_id` 집합에 `"integration.members"`가 있다. 제품은 알 수 없는 구성원("unknown or multiply assigned member")과 배정되지 않은 `output/knowledge/1`("mutation has no declared integration bundle")을 같은 규칙으로 낸다.
- 대역: 없음.

### `test_cross_bundle_new_reference_requires_merge` (행 192–196)
- 성질: 다른 묶음에서 새로 만드는 객체를 참조하는 레코드는 그 묶음과 합쳐야 한다.
- 준비: 지식 `B`의 `dependencies`를 `["A"]`로 둔다. `A`는 `IN-A`의 새 레코드 제목이다.
- 실행: `inspect_bundles`.
- 단언: `rule_id` 집합에 `"integration.reference_closure"`가 있다.
- 대역: 없음.

### `test_metadata_cannot_split_from_its_new_record` (행 198–202)
- 성질: 새 레코드의 메타데이터는 그 레코드와 다른 묶음에 있을 수 없다.
- 준비: 확장 `knowledge_metadata=[{"title": "A"}]`를 두고, 그 구성원을 `IN-B`에 넣는다.
- 실행: `inspect_bundles`.
- 단언: `rule_id` 집합에 `"integration.reference_closure"`가 있다. 제품은 `knowledge_metadata` 행의 `title`을 참조로 더한다.
- 대역: 없음.

### `test_plan_is_one_bundle` (행 204–209)
- 성질: 연구 계획 응답은 묶음 하나여야 한다.
- 준비: 맥락의 역할을 `research_plan`으로 바꾼다. 출력은 묶음 둘을 가진 `two_observation_output()`이다.
- 실행: `inspect_bundles`.
- 단언: `rule_id` 집합에 `"integration.single_bundle"`이 있다. 제품 문구는 "this role response and all extensions are one judgment"다.
- 대역: 없음.
- 비고: 계획 역할에서는 `split_research`가 거짓이라 지식 행이 독립 구성원이 아니므로, 구성원 문제도 함께 날 수 있다. 테스트는 `single_bundle`의 존재만 본다.

### `test_failed_candidate_does_not_undo_other_bundle` (행 211–228)
- 성질: 후보 검증에서 한 묶음이 실패해도 앞서 수용된 묶음은 되돌려지지 않는다. 실패는 재시도 목록과 전체 문제 목록에 남는다.
- 준비: 인스턴스 `{"knowledge": {}}`. 적용 콜백은 지식을 제목으로 넣는다. 후보 검증 콜백은 인스턴스에 `B`가 있으면 `ValueError("B rejected")`를 던진다. 발행 콜백은 인스턴스 사본을 기록한다.
- 실행: `apply_bundles(original, {}, two_observation_output(), {}, research_work_context(), ...)`.
- 단언: 묶음 상태가 `["accepted", "returned"]`다. 결과 인스턴스의 지식 키는 `{"A"}`다. 원 인스턴스는 `{"knowledge": {}}` 그대로다. 발행은 1회다. `retry_bundle_ids`에 `"IN-B"`가 있다. 둘째 묶음의 `issues`가 결과 전체의 `issues`와 같다. 곧 후보 단계에서 처음 발견된 실패가 전체 목록에 보존된다(제품 주석 "Preserve failures first discovered during candidate validation/publication").
- 대역: 콜백 람다.

### `test_receipt_is_published_with_state_and_replay_has_no_effect` (행 230–240)
- 성질: 영수증은 상태와 함께 발행되고, 같은 응답을 다시 적용하면 아무 효과가 없다.
- 준비: 적용 콜백은 묶음 ID를 `calls`에 기록한다. 발행 콜백은 런타임 사본을 `published`에 기록한다.
- 실행: 빈 상태에 두 묶음을 적용하고, 그 결과 상태에 같은 출력을 다시 적용한다.
- 단언: 첫 발행 런타임의 `integrations`에 `"IN-A"`가 있다. 두 번째 적용 뒤에도 `calls`는 2개다. 두 번째 결과의 모든 묶음 상태가 `"already_accepted"`다. 제품은 영수증의 `payload_sha256`이 같으면 적용을 건너뛴다.
- 대역: 콜백 람다.

### `test_retry_only_failed_bundle_does_not_repeat_response_finalization` (행 242–254)
- 성질: 실패한 묶음만 다시 보낼 때, 이미 수용된 응답 본문은 다시 확정되지 않는다.
- 준비: 원 출력의 `output` 구성원 값 `base`를 `member_values`로 얻는다. 출력을 지식 `B`와 묶음 `IN-B`(구성원 `output/knowledge/0`)만 남기도록 줄인다. 맥락의 `accepted_response`에는 `IN-A`와 `exact_content_hash(base)`를 싣는다.
- 실행: `inspect_bundles`를 부르고, 이어서 `apply_bundles(..., execution_id="EX-2")`를 부른다. 적용 콜백은 묶음의 `owns_response`를 기록한다.
- 단언: 검사 결과가 `[]`다. 응답 본문 `output`은 이미 소유된 것으로 인정된다. 결과 `status`는 `"accepted"`이고, `calls`는 `[False]`다.
- 대역: 콜백 람다.

### `test_current_authority_failure_precedes_mutation` (행 256–264)
- 성질: 현재성이나 권한 검사가 실패하면 적용과 발행 전에 멈춘다.
- 준비: `validate_current`가 `ValueError("authority revoked")`를 던진다. 적용과 발행 콜백은 호출되면 `calls`에 기록한다.
- 실행: `apply_bundles`.
- 단언: `calls`가 `[]`다. `retry_bundle_ids`가 `["IN-A", "IN-B"]`다.
- 대역: 콜백 람다.

### `test_publish_failure_does_not_claim_acceptance` (행 266–275)
- 성질: 발행(CAS)이 실패하면 어떤 묶음도 수용으로 보고되지 않고, 작업 상태도 바뀌지 않는다.
- 준비: 발행 콜백이 `ValueError("CAS conflict")`를 던진다. 적용 콜백은 후보 인스턴스에 `changed=True`를 둔다.
- 실행: `apply_bundles({}, {}, two_observation_output(), ...)`.
- 단언: 결과 인스턴스는 `{}`이고, 런타임에 `integrations`가 없다(거짓값). 모든 묶음 상태가 `"returned"`이고 전체 `status`도 `"returned"`다.
- 대역: 콜백 람다.
- 비고: 제품은 발행 단계에서 실패하면 남은 묶음을 모두 `integration.publication`("reload current snapshot before retry")으로 반려하고 반복을 멈춘다.

## 관계

- 같은 제품 기능의 다른 층: 묶음 선언의 스키마(`MANIFEST_SCHEMA`, 선택 필드)는 `test_contracts.test_manifest_is_optional_but_explicit_declarations_remain_typed`가 본다. 지식 변경 묶음의 영향 검토와 그 단일 적용은 `test_impact_review`가 본다. 제출 검사가 묶음 문제를 어떻게 싣는지는 `test_submission_checks`의 `SubmissionShapeTests`와 여러 경계 테스트가 본다. 엔진의 수령 경로에서 묶음을 적용하는 흐름은 제출 흐름 모듈들이 다룬다.
- 픽스처 의존: `record_fixtures`의 `two_observation_output`, `observation_knowledge`, `research_work_context`와 `research_fixtures`의 `git_init`, `current_state`.
- 이 모듈에만 있는 도우미: 없다. 콜백은 모두 테스트 안의 람다나 지역 함수다.
- 겹치거나 보완하는 시험: 참조 폐포 규칙은 세 테스트가 서로 다른 참조 원천으로 본다. 종류 정의는 `test_proposed_kind_and_consumer_must_share_bundle`, 의존 필드는 `test_cross_bundle_new_reference_requires_merge`, 메타데이터 제목은 `test_metadata_cannot_split_from_its_new_record`가 맡는다. 적용 단계별 실패는 네 테스트가 나누어 본다. 제출 문제는 `test_local_schema_failure_does_not_block_valid_bundle`, 현재성은 `test_current_authority_failure_precedes_mutation`, 후보 검증은 `test_failed_candidate_does_not_undo_other_bundle`, 발행은 `test_publish_failure_does_not_claim_acceptance`가 맡는다.

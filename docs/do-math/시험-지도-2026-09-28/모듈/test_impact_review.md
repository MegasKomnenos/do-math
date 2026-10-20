# test_impact_review

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_impact_review.py` (678행) |
| 클래스 / 테스트 | 3 / 13 |
| 시험 대상 제품 코드 | `do_math/integration.py`의 `bundle_impact_request`, `impact_review_response_schema`, `validate_impact_review_response`, `require_bundle_impact_review`(내부 `_reviewed_impact_request`), `apply_reviewed_knowledge_changes`, `ImpactReviewRequired`, `split_bundles`, `member_values`, `apply_bundles`; `do_math/knowledge.py`의 `plan_impact`, `apply_reviewed_impacts`, `replace_knowledge`, `content_hash`; `do_math/submission.py`의 `extension_schema`, `install_tools`, `producer_check`, `seal_submission`, `read_sealed_submission`, `issued_input`; `do_math/contracts.py`의 `action_schema`, `schema_for`; `do_math/engine.py`의 `ResearchEngine._retry_impact_reviews`; `do_math/git_store.py`의 `GitStateStore`; `do_math/repository.py`의 `ResearchRepository` |
| 사용하는 픽스처 모듈 | `review_fixtures`: `ImpactReviewHarness`. `research_fixtures`: `bare_engine`, `git_init`, `current_state`. `record_fixtures`: `research_work_context` |
| 격리 표지 | 없음 |
| 시작 상태 | `ImpactBundleTests`, `ImpactReviewTests`: 네 단 밖. `ImpactReviewHarness`가 메모리 상태에 관찰 지식 셋과 영향 검토를 기다리는 묶음 `IN-held`를 만든다. 일부 테스트는 그 위에 `git_init`으로 실제 Git 저장소를 만들어 봉인된 검토를 발행한다. `ImpactReviewRetryTests`: 네 단 밖의 `bare_engine`(저장소 없는 엔진)에 자동 명세 저장소 대역을 붙인다 |

## 목적

모듈 docstring은 이 모듈이 지식 영향 검토(knowledge-impact review)를 시험한다고 밝힌다. 대상은 변경에 대한 지정 검토, 그 봉인 증거, 그리고 검토된 묶음의 단일 적용이다. 생산자가 기존 지식을 고치는 묶음(`knowledge_changes`)을 내면, `bundle_impact_request`가 영향 계획을 만든다. 계획은 묶음 전체의 계획 하나와 변경 좌표마다 계획 하나로 이루어진다. 제품 docstring은 이 함수를 "Bind the unchanged held payload to each actual domain plan separately."라고 설명한다.

`knowledge.plan_impact`는 기계가 계산한 폐포(computed closure)와 생산자가 선언한 영향을 비교한다. 선언이 폐포를 넘거나 해석할 수 없는 참조가 있을 때만 독립 검토가 필요하다. 그러면 묶음은 대기하고, 지정된 유지보수 실행(`stage='impact_review'`)이 검토를 맡는다. 그 검토가 봉인되고 영수증과 함께 발행된 뒤에야 `apply_reviewed_knowledge_changes`가 계획을 한 번 적용하고 대체 후보를 만든다(docstring "Apply the reviewed S0 plans once, then create every replacement candidate.").

이 모듈은 이 경로의 다섯 가지를 검사한다: 계획 산출, 검토 응답의 형식, 대기 처분, 봉인 증거에 대한 해석기의 검증, 실제 Git 위의 재시도와 멱등 적용.

## 모듈 수준 요소

- 행 14: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리다.
- 행 15–23: `exact_content_hash`, `contracts`, `engine`(별칭 `engine_module`), `integration`, `knowledge_io`, `repository`, `submission`, `GitStateStore`, `content_hash`, `canonical_json`과 픽스처 `bare_engine`, `git_init`, `ImpactReviewHarness`, `research_work_context`를 import한다.
- 행 677–678: 직접 실행하면 `unittest.main()`으로 이 모듈의 시험을 돈다.

기반 하네스 `review_fixtures.ImpactReviewHarness`의 `setUp`은 다음을 만든다.
- `self.api`: `integration` 모듈.
- `self.instance`, `self.runtime`: `knowledge_io.import_candidate`로 관찰 지식 `A`, `B`, `C`를 후보로 들여온 상태. ID는 `self.ids`에 둔다. 런타임에는 실행 중인 생산자 `EX-producer`(`input_snapshot='fixed-input'`)가 있다.
- `self.output`, `self.extensions`: 지식이 없는 연구 수행 출력과, `A`와 `C`를 고치는 `knowledge_changes` 둘. 각 변경의 `impact_set`은 `[B]`다.
- `self.bundle`: 묶음 `IN-held`. 구성원은 `output`과 두 변경 좌표이고, `impact_set=[B]`, `previous_hashes`에 `A`, `C`의 내용 해시를 둔다.

하네스 메서드는 셋이다.
- `request()`: 이 묶음의 영향 검토 요청.
- `review_output(request)`: 모든 계획을 승인하는 독립 검토 출력. 각 결정의 `affected_ids`는 계산 영향과 선언 영향의 합집합이다. 통합 묶음 `IN-review`를 갖는다.
- `seal_review_fixture(execution, output, fixed, workspace)`: 제품의 중앙 포착으로 검토를 봉인한다. `install_tools`, `seal_submission`, `bare_engine()._stage_submission_capture`를 거친 뒤 실행을 `ended`/`output_accepted`로 전이하고, 발행할 artifact를 돌려준다.

`B`는 `A`나 `C`에 의존하지 않으므로, 선언된 `B`는 계산 폐포 밖의 추가 선언이다. 그래서 하네스의 묶음은 독립 검토를 요구한다.

## ImpactBundleTests (행 26–388)

기반 클래스는 `review_fixtures.ImpactReviewHarness`(그 기반은 `unittest.TestCase`)다. 클래스 표지와 속성은 없다. 도우미 메서드는 둘이다.

- `_request()` (행 27–34): `integration.bundle_impact_request(self.instance, self.runtime, self.bundle, producer_execution_id="EX-producer", input_snapshot="fixed-input")`.
- `_seal_review(request)` (행 36–65): 요청을 승인하는 검토를 봉인해 실제 Git에 발행하고, 검토 소비자에게 넘길 키워드 인자를 돌려준다(docstring). 과정은 다섯 단계다.
  1. `enterContext(tempfile.TemporaryDirectory())`로 임시 폴더를 만든다.
  2. 검토 행동 `AC-review`(역할 `maintenance`, 단계 `impact_review`, `input_basis.impact_review=request`)와 고정 맥락을 만들고, 검토 출력의 묶음을 나눈다.
  3. 런타임에 실행 중인 검토 실행 `EX-review`(입력 묶음 `BA-review-input`)와 영수증 `IN-review`를 기록한다.
  4. `seal_review_fixture`로 artifact를 얻는다.
  5. `GitStateStore(git_init(root / "repository"), ...)`에 세 가지를 발행한다: `research/fixture.json`, 고정 맥락, 봉인 artifact.
  반환값은 `producer_execution_id`, `input_snapshot`, `review_execution_id`, 발행 head `snapshot`, 저장소에서 바이트를 읽는 `read_artifact`다.

### `test_coupled_changes_use_the_single_reviewed_s0_plan` (행 67–119)
- 성질: 서로 의존하는 두 지식을 한 묶음에서 함께 고치면, 검토된 하나의 계획 집합이 한 번 적용된다. 재평가 기록과 후속 계획은 각각 하나만 생긴다.
- 준비: `B`(`dependent`)의 `dependencies`를 `[A]`(`first`)로 바꾸고 `ensure_ontology`를 다시 적용한다. 대기열을 비운다. 변경 둘을 둔다. `dependent`는 영향 없음, `first`는 영향 `[dependent]`다. 묶음의 `impact_set`을 `[dependent]`로, `previous_hashes`를 두 대상의 현재 해시로 두고 다시 나눈다. 적용 전 상태의 정준 JSON을 떠 둔다. `_request()`와 `_seal_review(request)`로 봉인된 승인을 준비한다.
- 실행: `apply_reviewed_knowledge_changes(self.instance, self.runtime, self.bundle, actor_ref="EX-producer", **args)`.
- 단언:
  - 입력 인스턴스의 정준 JSON이 적용 전과 같고, 돌려받은 런타임은 적용 전과 다르다.
  - 결과 지식 가운데 `supersedes`가 있는 행의 대상 집합이 `{dependent, first}`다.
  - 런타임 이력의 `knowledge_reassessment_required` 행이 1개다.
  - 대기열에서 역할이 `research_plan`이고 `affected_ids`가 있는 후속이 1개이며, 그 `affected_ids`에 `dependent`가 있다.
- 대역: 없음. 검토는 제품의 중앙 포착으로 봉인하고, 실제 Git에 발행한다.
- 비고: 실제 외부 자원으로 `GitStateStore`의 Git 자식 프로세스를 쓴다. 이름의 "S0 plan"은 제품 `knowledge.apply_reviewed_impacts`의 docstring "Apply one already-current S0 decision set without recomputing an S1 plan."의 용어다.

### `test_bundle_level_reviewed_effect_is_applied_once` (행 121–169)
- 성질: 묶음 수준에서 선언한 영향(외부 과제)은 검토된 뒤 한 번만 적용된다.
- 준비: 런타임에 열린 과제 `TK-external-premise`를 둔다. 과제의 평가는 `current=True`다. 대기열을 비운다. 확장은 `A`를 고치는 변경 하나(영향 없음)다. 묶음 `IN-whole-only`는 `output`과 그 변경을 구성원으로 두고, `impact_set=[task_id]`와 `A`의 이전 해시를 갖는다. 다시 나누고 `_seal_review`로 승인을 준비한다.
- 실행: `apply_reviewed_knowledge_changes(...)`.
- 단언: 결과 런타임에서 과제의 `assessment.current`가 거짓이다. `knowledge_reassessment_required` 이력 행이 1개다.
- 대역: 없음.
- 비고: 실제 Git 자식 프로세스를 쓴다.

### `test_ordinary_execution_source_dependency_still_propagates` (행 171–195)
- 성질: 지식을 출처로 쓴 보통 실행은 영향 폐포에 든다. 다른 배정을 검토한 영향 검토 실행도 마찬가지다.
- 준비: 런타임에 끝난 실행 둘을 둔다. 연구 수행 `EX-consumer`는 `used_sources=[A]`다. 유지보수 영향 검토 `EX-other-review`는 다른 배정(`IN-other`)을 검토했고 `used_sources=[A]`다.
- 실행: `knowledge.plan_impact(self.instance, self.runtime, [A], [])`.
- 단언: `computed_impact`에 `EX-consumer`와 `EX-other-review`가 모두 있다.
- 대역: 없음.
- 비고: 제품 `bundle_impact_request`는 같은 요청 머리를 가진 검토 실행만 계산에서 뺀다(`excluded_dependents`). 다른 배정의 검토는 이 테스트처럼 보통 실행과 같이 전파된다.

### `test_only_an_impact_beyond_the_computed_closure_needs_independent_review` (행 197–215)
- 성질: 계산 폐포의 일부를 선언하지 않은 것은 독립 검토를 부르지 않는다. 폐포 밖의 레코드를 선언하면 독립 검토가 필요하다.
- 준비: `A`를 출처로 쓴 실행 `EX-consumer`를 둔다.
- 실행: `plan_impact(..., [A], [])`와 `plan_impact(..., [A], [B])`.
- 단언: 첫 계획의 `missing_declarations`에 `EX-consumer`가 있고, `requires_independent_review`는 거짓이다. 둘째 계획의 `extra_declarations`에 `B`가 있고, `requires_independent_review`는 참이다.
- 대역: 없음.
- 비고: 행 207–212의 주석이 이유를 적는다. 기계는 계산 폐포를 적용하고 승인은 그 폐포를 덮어야 하므로, 일부를 빠뜨린 선언은 아무것도 바꾸지 않는다. 폐포가 닿지 않는 레코드를 정지시키는 것은 생산자 자신의 판단이다. 제품 `plan_impact`의 주석도 같은 내용이다.

### `test_explicit_replacement_ids_support_forward_sibling_dependencies` (행 217–272)
- 성질: 생산자가 대체 ID(`replacement_id`)를 명시하면, 한 변경이 같은 묶음에서 뒤에 만들어질 형제의 대체 ID에 의존할 수 있다.
- 준비: 새 ID 둘 `KN-01ARZ3NDEKTSV4RRFFQ69G5FAA`(`new_first`), `...FAB`(`new_dependent`). 변경 둘을 둔다. `dependent`의 대체는 `dependencies=[new_first]`이고, `first`의 대체는 요약만 바꾼다. 둘 다 영향은 없다. 묶음 `IN-explicit-ids`와 이전 해시를 두고 다시 나눈다. 적용 전 상태의 정준 JSON을 떠 둔다.
- 실행: 검토 인자 없이 `apply_reviewed_knowledge_changes(..., actor_ref="EX-producer", producer_execution_id="EX-producer", input_snapshot="fixed-input")`.
- 단언: `new_dependent`의 `dependencies`는 `[new_first]`다. `new_first.supersedes`는 `first`이고, `new_dependent.supersedes`는 `dependent`다. 입력 인스턴스와 런타임은 바뀌지 않았고, 돌려받은 런타임은 달라졌다.
- 대역: 없음.
- 비고: 선언 영향이 없어 어느 계획도 독립 검토를 요구하지 않으므로, 검토 없이 적용된다(`_reviewed_impact_request`가 빈 확인을 돌려준다). 제품은 대체 ID 전체를 `reserved_dependency_ids`로 넘겨 앞선 변경이 뒤의 대체 ID를 참조할 수 있게 한다.

### `test_replacement_id_schema_and_global_uniqueness_are_enforced` (행 274–388)
- 성질: 대체 ID는 확장 스키마를 통과하고 설치된 생산자 검사에서도 받아들여진다. 한 묶음 안에서 같은 대체 ID를 두 번 쓰거나 이미 있는 레코드 ID를 대체 ID로 쓰면 적용이 거부되고 상태는 바뀌지 않는다.
- 준비: 대체 ID `KN-01ARZ3NDEKTSV4RRFFQ69G5FAC`를 가진 `A`의 변경 행 `row`를 만든다. 형제 행 `sibling`은 `B`를 고치며, 대체 ID는 `...FAD`이고 `dependencies=[row의 대체 ID]`다. 생산자 출력의 묶음 `IN-producer-explicit-ids`는 변경 둘과 `revision_resolutions` 둘을 구성원으로 둔다. 행동에는 `revision_targets`로 두 대상을 두고, 맥락에는 `execution_id='EX-producer'`와 `knowledge_catalog`를 둔다.
- 실행: 네 단계로 진행한다.
  1. `extension_schema({"role": "research_work"})`로 `row`를 검증한다.
  2. 임시 작업 공간에 `install_tools`로 검사 도구를 설치하고, 초안(`.scratch/draft.json`)과 `activity-extensions.json`을 쓴 뒤 `submission.producer_check(workspace, draft)`를 부른다.
  3. 지역 도우미 `bundle_for(rows)`로 묶음 `IN-id-rejection`을 만든다. 같은 대체 ID를 두 행(대상 `A`와 `B`)이 쓰는 `duplicate`를 적용한다.
  4. 대체 ID를 기존 ID `C`로 둔 `reused`를 적용한다.
- 단언: 스키마 오류는 `[]`다. 생산자 검사의 `passed`가 참이다(실패 메시지는 `issues`). 3과 4는 각각 `ValueError`이고 메시지가 `"already exists"`에 맞는다. 행 367의 주석은 `import_candidate`가 두 번째 사용을 거부한다고 밝힌다. 끝으로 인스턴스와 런타임의 정준 JSON이 원래와 같다.
- 대역: 없음.
- 비고: 지역 도우미 `bundle_for(rows)`는 행 수에 맞춘 구성원과 이전 해시로 묶음을 만들고 첫 분할 결과를 돌려준다.

## ImpactReviewRetryTests (행 391–411)

`unittest.TestCase`를 그대로 상속하고 훅과 도우미가 없다.

### `test_sealed_bytes_are_read_only_after_every_requested_review_ended` (행 392–411)
- 성질: 영향 검토를 기다리는 제출의 봉인 바이트는, 요청한 검토가 모두 끝나기 전에는 읽지 않는다.
- 준비: `bare_engine({}, head='a'*40)`. 런타임은 `status='ready'`, 생산자 실행 `EX-producer`, 대기 행동 `A-1`이다. `A-1`은 종류 `impact_review`이고 `review_requests={'IN-1': request}`다. `_hold_unreadable_impact_submission`은 자동 명세 대역으로 바꾼다. `engine.store`는 `ResearchRepository`의 자동 명세 인스턴스이고, `git_dir`는 임의의 `git-<uuid>`다.
- 실행: `engine_module.submission.read_sealed_submission`을 `SealedSubmissionError('unreadable fixture')`를 던지도록 패치한다. `_retry_impact_reviews()`를 부른다. 이어서 같은 요청을 배정받아 끝난(`output_accepted`) 검토 실행 `EX-review`를 더하고 다시 부른다.
- 단언: 첫 호출 뒤 읽기 대역이 불리지 않았다(`assert_not_called`). 둘째 호출 뒤에는 정확히 한 번 불렸다. 보류 대역 `_hold_unreadable_impact_submission`도 정확히 한 번 불렸다.
- 대역: `create_autospec`의 `_hold_unreadable_impact_submission`과 `ResearchRepository` 인스턴스, `patch.object(engine_module.submission, 'read_sealed_submission', side_effect=...)`.
- 비고: 행 403의 주석은 "Control processing retries every waiting item; a pending review reads nothing."이라고 밝힌다. 제품 `_retry_impact_reviews`의 주석은 "Sealed bytes are read only once every requested review has ended."다.

## ImpactReviewTests (행 414–674)

기반 클래스는 `review_fixtures.ImpactReviewHarness`다. 클래스 표지, 속성, 도우미 메서드는 없다. 하네스의 `request()`, `review_output()`, `seal_review_fixture()`를 쓴다.

### `test_request_cannot_relabel_the_original_producer_snapshot` (행 415–418)
- 성질: 영향 검토 요청은 생산자의 원래 입력 스냅숏과 다른 스냅숏으로 만들 수 없다.
- 준비: 하네스 상태. 생산자의 `input_snapshot`은 `fixed-input`이다.
- 실행: `bundle_impact_request(..., input_snapshot="other-input")`.
- 단언: `ValueError`다. 예외 유형만 본다. 제품 문구는 "impact request snapshot differs from its original producer input"이다.
- 대역: 없음.

### `test_designated_review_has_producible_closed_schema_and_exact_scope` (행 420–451)
- 성질: 지정 검토의 응답 스키마는 생산자가 실제로 만들 수 있고, 배정된 범위마다 정확히 한 번의 결정을 요구한다. 설치된 생산자 검사도 같은 규칙을 적용한다.
- 준비: 하네스의 요청과 검토 출력. 행동은 `{"role": "maintenance", "stage": "impact_review", "input_basis": {"impact_review": request}}`다.
- 실행: 네 단계로 진행한다.
  1. `contracts.action_schema(action)`로 출력을 검증하고 `validate_impact_review_response(request, output)`를 부른다.
  2. 결정 하나를 뺀 출력, 두 번째 결정의 `plan_digest`를 묶음 계획 digest로 바꾼 출력을 각각 검증한다.
  3. 임시 작업 공간에 `install_tools`로 도구를 설치하고, 초안으로 `producer_check`를 부른다.
  4. 첫 결정을 세 번 반복한 출력으로 `producer_check`를 다시 부른다.
- 단언:
  - 스키마 오류는 `[]`다.
  - 요청의 `plans`는 3개다(묶음 하나와 변경 좌표 둘).
  - 묶음 계획과 첫 변경 좌표 계획의 `digest`가 다르다.
  - 2의 두 경우는 각각 `ValueError`다(예외 유형만 본다).
  - 3의 `passed`는 참이다.
  - 4의 `passed`는 거짓이다(실패 메시지 "Installed producer must reject duplicate scope judgments").
- 대역: 없음.
- 비고: 제품 `impact_review_response_schema`는 범위마다 `scope`와 `plan_digest`를 상수로 고정한 대안을 `oneOf`로 둔다. `plan_decisions`의 `minItems`와 `maxItems`는 대안 수와 같다. `validate_impact_review_response`는 범위 집합이 정확히 한 번씩 덮이는지와 승인의 `affected_ids`가 합집합과 같은지를 더 본다.

### `test_review_required_is_a_waiting_disposition_not_a_producer_retry` (행 453–460)
- 성질: 독립 검토가 필요한 묶음은 생산자 재시도가 아니라, 요청을 실은 영향 검토 대기로 반려된다.
- 준비: 하네스 상태.
- 실행: `apply_bundles(...)`를 부른다. `validate_current`는 검토 인자 없이 `require_bundle_impact_review`를 부른다. 적용, 후보 검증, 발행 콜백은 호출되면 `self.fail`한다.
- 단언: 첫 묶음 결과의 `next_owner`가 `"impact_review"`이고, `impact_review_request`가 `self.request()`와 같다.
- 대역: `self.fail` 콜백(호출 금지 감시).
- 비고: 제품은 `ImpactReviewRequired`(메시지 "designated independent impact review required")를 던지고, `apply_bundles`가 이 예외를 잡아 요청을 결과에 싣는다.

### `test_review_evidence_does_not_change_the_mathematical_impact_plan` (행 462–468)
- 성질: 검토 실행을 기록해도, 그 검토가 배정받은 영향 계획은 바뀌지 않는다.
- 준비: 요청 `before`를 만든다. 검토 출력의 `used_sources=[A]`로 두고, 이 요청을 배정받아 끝난 검토 실행 `EX-review`를 런타임에 더한다.
- 실행: `self.request()`를 다시 만든다.
- 단언: 새 요청이 `before`와 같다(실패 메시지 "Recording the review must not invalidate its own assigned impact plan").
- 대역: 없음.
- 비고: 제품 `bundle_impact_request`는 요청 머리가 같은 검토 실행을 계산에서 빼고, 제외 집합이 안정될 때까지 반복한다. 검토가 `A`를 출처로 썼어도 자기 계획에 들어가지 않는다.

### `test_review_resolver_uses_actual_git_bytes_and_scoped_receipt` (행 470–563)
- 성질: 검토 해석기는 런타임의 사본이 아니라 실제 Git의 봉인 바이트와 범위가 맞는 영수증으로 승인을 확인한다. 조건이 하나라도 어긋나면 런타임을 바꾸지 않고 거부한다. 합법적으로 제출된 부정 판단은 증거일 뿐 변경 허가가 아니다.
- 준비: `_seal_review`와 같은 방식으로 준비한다. 검토 실행과 영수증 `IN-review`를 기록한다. 임시 폴더에 `git_init`과 `GitStateStore`를 만든다. `seal_review_fixture`로 artifact를 얻어 고정 맥락과 함께 발행하고, 해석기 인자 `args`를 만든다.
- 실행과 단언: 다섯 단계로 진행한다.
  1. `require_bundle_impact_review(..., **args)`의 확인 키 집합이 요청 `plans`의 키 집합과 같다. `apply_reviewed_knowledge_changes`의 결과에서 `supersedes` 대상은 `{A, C}`다. 그 결과를 Git에 발행하고 다시 읽으면 같다.
  2. 재시도 실행 `EX-retry`가 `continuation_of='EX-producer'`이면 `receiving_execution_id="EX-retry"`로도 같은 확인을 얻는다. `continuation_of`를 지우면 `ValueError`다(제품 "impact approval cannot transfer to an unrelated receiving execution").
  3. 런타임의 검토 출력 `summary`를 바꾼 사본으로도 같은 확인을 얻는다. 해석기는 런타임 사본이 아니라 봉인 바이트를 읽는다.
  4. 일곱 부정 경우를 `subTest(case=...)`로 확인한다.
     - `same_producer`: 검토 실행을 생산자로 둔다.
     - `other_bundle`: 묶음 ID를 바꾼다.
     - `stale`: `B`의 요약을 바꾼다. 메시지 `"current assignment"`(제품 "impact review is not the accepted designated current assignment").
     - `unsealed`: 영수증을 비운다.
     - `tampered_output`: `read_artifact`가 출력 참조 경로에서 바뀐 출력을 돌려주게 한다. 메시지 `"sealed output_ref hash differs"`(제품 `read_sealed_submission`의 "execution ...: sealed output_ref hash differs at ...").
     - `shared_conversation`: 생산자와 검토자에 같은 `conversation_id`를 둔다.
     - `machine`: 검토자의 `actor_kind`를 `machine`으로 둔다.
     각각 `ValueError`이고, `stale`과 `tampered_output`은 메시지 조각까지 고정한다. 나머지는 빈 정규식이라 유형만 본다. 모든 경우에 검사 뒤 런타임의 정준 JSON이 검사 전과 같다(행 535의 주석 "A rejected review leaves the runtime it was checked against unchanged.").
  5. 첫 결정을 `reject`와 `unresolved`로 바꾼 부정 검토를 만든다. 이 응답은 `validate_impact_review_response`를 통과한다. 각각 별도 실행과 입력 묶음으로 봉인해 발행하고 영수증을 그 검토로 바꾼다. 해석기는 `ValueError`를 던지고 메시지가 `"did not approve"`에 맞는다(제품 "independent impact review did not approve every assigned scope").
- 단언: 위 다섯 단계에 단계별로 적었다. 요약하면 셋이다. 봉인 바이트와 영수증이 맞으면 모든 계획의 확인을 돌려준다. 어긋난 증거는 런타임을 바꾸지 않고 `ValueError`로 거부된다. 부정 결정은 "did not approve"로 거부된다.
- 대역: `tampered_output` 경우의 `read_artifact` 람다(바이트 변조).
- 비고: 실제 Git 자식 프로세스(`GitStateStore`)를 쓴다. `subTest`는 일곱 부정 경우와 두 부정 결정(`reject`, `unresolved`)이다.

### `test_sealed_review_allows_real_domain_git_retry_and_rejects_wrong_evidence` (행 565–674)
- 성질: 실제 `ResearchRepository` 위에서 봉인된 영향 검토를 발행하고 수용하면, 보류된 생산자 묶음이 그 검토로 적용된다. 잘못된 증거는 거부되고, 이미 수용된 묶음의 재생은 아무것도 다시 하지 않는다.
- 준비: 네 단 밖.
  1. 임시 폴더에 `git_init`을 하고, `build_profiles`로 명시 설정의 프로필을 만들어 인스턴스에 더한다.
  2. 지역 도우미 `execution(identifier, role, action)`로 활동을 열고, 프로필에 묶인 실행 중 실행을 만든다. 생산자 `EX-producer`를 만든다.
  3. `current_state`로 생명주기 관문을 통과하는 상태를 만든다(행 589의 주석). `ResearchRepository`에 `initialize`하고, 생산자의 `input_snapshot`을 그 head로 둔다.
  4. 요청과 검토 실행 `EX-review`를 만든다. 고정 맥락에는 스냅숏, 지식 목록, 종류 정의를 둔다. 검토 출력의 `used_sources`를 `[A, C]`로 둔다.
  5. 유지보수 스키마에 `impact_review` 응답 스키마를 필수로 더하고, `install_tools`와 `seal_submission`으로 봉인한다. 봉인의 `passed`가 참임을 먼저 확인한다.
  6. 검토 실행에 입력 묶음, 출력 참조, 출력, 입력 스냅숏을 기록하고, 고정 맥락과 봉인 artifact를 `save_with_state`로 발행한다.
- 실행: 세 번의 적용을 차례로 한다.
  - 검토 응답 적용: `apply_bundles`에 적용 콜백 `accept_review`를 넘긴다. 이 콜백은 응답을 검증하고, `record_submission_intent`로 제출 의도와 제어(`CT-review`)를 기록한 뒤, 검토 실행을 `ended`/`output_accepted`로 전이한다. `validate_current`는 응답 검증이고, 후보 검증과 발행은 실제 저장소를 쓴다.
  - 생산자 묶음 적용: 적재한 상태에서 `require_bundle_impact_review`로 확인을 얻는다. 네 부정 경우를 확인한 뒤, `apply_bundles`에 적용 콜백 `apply_changes`(내부에서 `apply_reviewed_knowledge_changes`)와 `validate_current=require_bundle_impact_review`를 넘긴다.
  - 재생: 적재한 상태로 같은 묶음을 다시 적용한다. 적용, 현재성, 발행 콜백은 호출되면 `self.fail`한다.
- 단언:
  - 검토 응답 적용의 `status`는 `"accepted"`다.
  - 확인 키 집합이 요청 `plans`의 키 집합과 같다.
  - 네 부정 경우(`same_producer`, `other_bundle`, `stale`, `unsealed`)는 각각 `ValueError`다. 예외 유형만 본다.
  - 생산자 묶음 적용의 `status`는 `"accepted"`이고, 적재한 지식의 `supersedes` 대상은 `{A, C}`다.
  - 재생 결과 첫 묶음 상태는 `"already_accepted"`이고, 저장소 head는 재생 전과 같다.
- 대역: 없음. 실제 `ResearchRepository`와 Git 자식 프로세스를 쓴다. 콜백은 제품 함수를 부르는 지역 함수다.
- 비고: `subTest(case=...)`의 네 케이스는 위와 같다. 지역 도우미는 `execution`, `publish`, `validate`, `accept_review`, `apply_changes`다.

## 관계

- 같은 제품 기능의 다른 층: 묶음의 일반 분할과 적용 규칙은 `test_integration_bundles`가 본다. 확장 스키마의 `knowledge_changes.impact_set` 필수 여부는 `test_contracts.test_knowledge_change_requires_a_declared_impact_set`이 본다. 봉인과 생산자 검사의 일반 규칙은 `test_submission_checks`가 본다. 목표 완료 정산에서 영향 검토 대기 행동을 보존하는 것은 `test_completion_settlement.test_completion_records_input_and_held_submission_before_finishing_activities`가 본다.
- 픽스처 의존: `review_fixtures.ImpactReviewHarness`(상태, 묶음, 요청, 검토 출력, 봉인 도우미). `research_fixtures`의 `bare_engine`, `git_init`, `current_state`. `record_fixtures.research_work_context`. 하네스는 내부에서 `record_fixtures`의 `observation_knowledge`, `two_observation_output`을 쓴다.
- 이 모듈에만 있는 도우미: `ImpactBundleTests._request`, `ImpactBundleTests._seal_review`, 테스트 안의 지역 함수 `bundle_for`, `execution`, `publish`, `validate`, `accept_review`, `apply_changes`.
- 겹치거나 보완하는 시험: 봉인 검토의 부정 경우는 두 층에서 겹친다. `test_review_resolver_uses_actual_git_bytes_and_scoped_receipt`는 `GitStateStore` 위에서 일곱 경우와 메시지를 보고, `test_sealed_review_allows_real_domain_git_retry_and_rejects_wrong_evidence`는 실제 `ResearchRepository` 위에서 그 가운데 네 경우를 유형만으로 본다. 영향 계획의 독립 검토 조건은 `test_only_an_impact_beyond_the_computed_closure_needs_independent_review`가 순수 계획 수준에서 본다.

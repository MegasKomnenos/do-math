# test_contract_checks

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_contract_checks.py` (141행) |
| 클래스 / 테스트 | 1 / 11 |
| 시험 대상 제품 코드 | `do_math/submission.py`의 `payload_issues`(연구 준비 역할의 `contract_checks` 확장 검사 분기, 행 782–804와 `task_conditions` 검사 행 884–901), `contract_check_errors`(행 364–399); `do_math/planning.py`의 `revision_requested`, `action_write_ids`; `do_math/task_contracts.py`의 `prepared_dependencies` |
| 사용하는 픽스처 모듈 | `research_fixtures`: `candidate`. `record_fixtures`: `contract_check`, `preparation_context`, `preparation_issues`(내부에서 `runner_fixtures.common`, `runner_fixtures.rating`, `research_fixtures.supply_observation_rules`를 쓴다) |
| 격리 표지 | 없음 |
| 시작 상태 | 1단(검증기 `payload_issues`를 사전 맥락과 임시 작업 공간 위에서 직접 호출) |

## 목적

모듈 docstring은 이 모듈이 연구 준비(`research_preparation`)의 생산자 쪽 계약 자기 점검을 시험한다고 밝힌다. 검사하는 규칙은 계약 검토 가운데 입력 상태가 결정하는 부분이다. 인용한 과제나 지식 레코드는 존재해야 한다. 인용한 형제(sibling) 계약에서 가져온 경계는 현재 개정판에서 읽어야 하고, 아직 개정 중인 형제에 조용히 의존해서는 안 된다. docstring은 이 규칙이 "2026-09-19 parking run"에서 왔다고 밝힌다. 기호 충돌과 빠진 결과 분기는 저자와 독립 계약 검토의 판단이지, 여기서 검사하는 선언이 아니라고도 적는다. 제품의 `contract_check_errors` docstring도 같은 경계를 말한다("Symbol meanings and outcome branches stay with the author's self-review and the independent contract review; no declaration of them is compared here."). 모든 테스트는 `record_fixtures.preparation_issues`로 준비 출력 하나를 만든다. 그 출력을 `payload_issues`에 넣고, 돌아온 문제 목록의 JSON 텍스트에 특정 조각이 들어 있는지 확인한다.

## 모듈 수준 요소

- 행 16: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리다.
- 행 17–18: 픽스처 `candidate`, `contract_check`, `preparation_context`, `preparation_issues`를 import한다.
- 행 140–141: 직접 실행하면 `unittest.main()`으로 이 모듈의 시험을 돈다.

## ContractCheckTests (행 21–137)

`unittest.TestCase`를 그대로 상속하고 표지가 없다.

`setUp` (행 22–27)은 임시 작업 공간 폴더를 만들고 정리를 등록한다. 맥락과 입력은 셋이다.
- `self.context`: `preparation_context()`. 행동 `AC-this`(역할 `research_preparation`), `budget_unit='concurrent_sessions'`이고, `tasks`, `knowledge_catalog`, `kind_definitions`, `sources`가 비어 있다.
- `self.item`: `candidate("one")`. 제목 `one`, 자연수 영 덧셈 질문, 빈 `dependencies`의 비형식 후보다.
- `self.conditions`: `[]`.

도우미 메서드는 둘이다.
- `issues(*entries, candidates=None)` (행 29–31): `preparation_issues`를 부른다. 인자는 자기 점검 항목 `entries`, 후보 목록(기본 `[self.item]`), 맥락, 작업 공간, `conditions`다. 결과는 문제 목록의 JSON 텍스트다. 정상일 때는 `"[]"`이다. `preparation_issues`는 후보마다 모델 평가 하나(`rating`), 자기 점검 `contract_checks`, 과제 조건 `task_conditions`, 픽스처의 관찰 규칙을 확장에 싣고, 이것들을 통합 묶음 `IN-check` 하나로 묶는다.
- `sibling(**changes)` (행 33–36): 맥락의 `tasks`를 형제 과제 하나로 바꾼다. 형제는 `candidate("window")`에 `id='TK-window'`, `revision=2`, `status='planned'`와 `changes`를 덮은 것이다. 이어서 후보의 `scope.included`를 "Rows below the window of TK-window; the threshold is tau."로 바꿔 형제를 인용하게 한다.

### `test_every_candidate_needs_exactly_one_self_check` (행 38–42)
- 성질: 후보마다 자기 점검 항목이 정확히 하나여야 한다.
- 준비: `setUp`의 후보 `one`.
- 실행: `issues()`를 네 가지로 부른다: 항목 없음, `contract_check()` 하나, 같은 항목 둘, `contract_check()`와 `contract_check("foreign")`.
- 단언: 항목이 없으면 결과 텍스트에 `"one"`이 들어 있다. 제품의 적용 범위 문구가 빠진 제목 목록을 싣는다("missing" 뒤의 JSON 배열). 하나일 때는 `"[]"`이다. 중복일 때와 없는 후보(`foreign`)를 가리킬 때는 `"[]"`가 아니다. 뒤의 두 경우는 거부 사유를 고정하지 않고, 문제가 있다는 사실만 본다.
- 대역: 없음.

### `test_self_check_declares_only_sibling_boundaries` (행 44–56)
- 성질: 자기 점검은 형제 경계만 선언한다. 기호 의미나 결과 분기를 선언하는 필드는 받지 않는다.
- 준비: 후보의 `question`을 "With T the threshold, expand C = T - Q + L where T is the first term"으로 바꿔 기호 `T`가 두 뜻으로 쓰이게 한다. 맥락에 활성 과제 `TK-exact`(개정 1)를 두고, 조건 `{"task_title": "one", "dependencies": ["TK-exact"]}`를 둔다. 이 의존은 어떤 결과 분기에서도 이름이 불리지 않는다.
- 실행: `issues(contract_check())`를 부른다. 이어서 두 필드를 하나씩 더한 `contract_check(**{field: value})`로 다시 부른다. 두 필드는 `symbols`(`T` = threshold)와 `outcome_branches`(`TK-exact holds`/`fails`)다.
- 단언: 기본 항목은 `"[]"`다. 기호 이중 의미와 이름 없는 의존은 이 검사의 대상이 아니다. 두 필드를 더한 항목은 각각 결과 텍스트에 그 필드 이름을 포함한다. 확장 스키마의 `contract_checks` 행은 `task_title`과 `sibling_boundaries`만 선언하는 닫힌 객체이므로, 선언되지 않은 필드가 스키마 오류로 보고된다.
- 대역: 없음.
- 비고: `subTest(field=...)`의 두 케이스는 `symbols`, `outcome_branches`다. 행 45–46의 주석은 이 두 판단이 저자와 계약 검토의 몫이라는 것을 밝힌다.

### `test_a_cited_sibling_contract_is_declared_at_its_current_revision` (행 58–63)
- 성질: 인용한 형제 계약은 경계를 선언해야 하고, 그 경계는 형제의 현재 개정판에서 읽은 것이어야 한다.
- 준비: `sibling()`. 형제 `TK-window`의 개정은 2다.
- 실행: 세 번 부른다. 경계 없는 `contract_check()`, 개정 1을 적은 경계, 개정 2를 적은 경계. 경계는 `k <= tau - 3`, `independent_of_next_revision=True`다.
- 단언: 경계가 없으면 결과에 `"TK-window"`가 있다(제품 문구 "cited sibling contract has no declared boundary: TK-window"). 개정 1이면 `"revision"`이 있다(문구 "sibling boundary was not read from the current revision 2 of TK-window"). 개정 2면 `"[]"`다.
- 대역: 없음.

### `test_sibling_boundary_is_read_from_the_checker_task_not_its_detail_copy` (행 65–84)
- 성질: 형제의 현재 개정은 검사기 맥락의 `tasks` 행에서 읽는다. 프롬프트에 주는 상세 사본은 읽지 않는다.
- 준비: `sibling(status='completed')`. 형제 행을 JSON으로 직렬화한 바이트 `raw`를 만들고, 작업 공간의 `input/details/sibling.json`에는 `raw + b' '`를 쓴다. 우발적으로 바뀐 상세 사본을 흉내 낸 것이다. 맥락에 `snapshot='fixed-input'`을 둔다. `task_catalog`에는 형제의 ID, 제목, 개정, 상태와 `source_ref`를 둔다. `source_ref`는 그 파일 경로, 스냅숏, 그리고 원래 `raw`의 SHA-256과 길이를 가리킨다.
- 실행: 경계 개정 2(현재)와 개정 1로 각각 `issues`를 부른다.
- 단언: 개정 2는 `'[]'`다. 상세 사본이 목록과 맞지 않아도 문제가 되지 않는다. 개정 1은 `'revision'`을 포함한다.
- 대역: 없음.
- 비고: 행 66–67의 주석과 제품 행 792–793의 주석이 같은 이유를 적는다. 검사기 맥락은 비교 모집단 밖의 완료된 형제까지 모든 현재 과제를 담는다(`context_store.prepare_role_input`). 형제 상태를 `completed`로 둔 것은 이 조건을 재현하기 위해서다.

### `test_primary_and_extension_dependencies_both_wait_for_a_sibling_under_revision` (행 86–97)
- 성질: 개정 중인 형제에 기대는 경계는 형제를 의존으로 기다리면 허용된다. 의존은 후보 본문의 `dependencies`로 적어도 되고, 확장 `task_conditions`의 의존으로 적어도 된다.
- 준비: `sibling(revision_requested={"revision": 2, ...})`로 현재 개정에 대한 개정 요청을 둔다. 경계는 개정 2, `k <= T - s`, `independent_of_next_revision=False`다.
- 실행: 네 조합마다 후보의 `dependencies`(`['TK-window']` 또는 `[]`)와 `self.conditions`(형제 의존 조건 또는 `[]`)를 두고 `issues`를 부른다.
- 단언: 둘 가운데 하나라도 있으면 `'[]'`다. 둘 다 없으면 `'under revision'`을 포함한다. 제품은 `prepared_dependencies`로 두 의존을 합친다(docstring "An extension adds prerequisites; omitted fields never erase the contract.").
- 대역: 없음.
- 비고: `subTest(primary=..., extension=...)`의 네 케이스는 `(False, False)`, `(True, False)`, `(False, True)`, `(True, True)`다.

### `test_revision_condition_is_matched_by_existing_id` (행 99–107)
- 성질: 기존 과제를 개정하는 후보에는, 과제 ID(`task_id`)로 지정한 과제 조건도 대응된다.
- 준비: 개정 요청이 있는 형제를 둔다. 후보는 `revises_task_id='TK-one'`이다. 맥락 `tasks`에 계획 상태의 `TK-one`(개정 1)을 더한다. 경계는 개정 2, 독립 아님이다.
- 실행: 조건 없이 한 번 부른다. 이어서 `self.conditions = [{'task_id': 'TK-one', 'dependencies': ['TK-window']}]`로 두고 다시 부른다.
- 단언: 첫 결과는 `'under revision'`을 포함하고, 둘째 결과는 포함하지 않는다. 제품은 조건을 `task_title`이 후보 제목과 같거나, `task_id`가 후보의 `revises_task_id`와 같은 행으로 찾는다.
- 대역: 없음.
- 비고: 행 105의 주석대로, 이 개정 픽스처는 무관한 문제도 함께 만든다. 그래서 둘째 단언은 `'[]'`가 아니라 `'under revision'`의 부재만 본다.

### `test_title_and_revision_id_cannot_supply_two_conditions_for_one_candidate` (행 109–113)
- 성질: 한 후보에 대해 제목으로 한 조건과 개정 대상 ID로 한 조건을 동시에 줄 수 없다.
- 준비: 후보는 `revises_task_id='TK-old'`이고, 맥락 `tasks`는 계획 상태의 `TK-old` 하나다. 조건은 `{'task_title': 'one'}`과 `{'task_id': 'TK-old'}` 둘이다.
- 실행: `issues(contract_check())`.
- 단언: 결과에 `'must not repeat'`가 있다. 제품 문구는 "task conditions must not repeat a target"이다. 제품은 개정 대상 ID를 그 후보의 제목으로 바꿔 대상 목록을 만들므로(행 889–891의 주석 "A title and the ID it revises identify the same prepared target."), 두 조건이 같은 대상으로 겹친다.
- 대역: 없음.
- 비고: 이 테스트는 계약 자기 점검(`contract_checks`)이 아니라 과제 조건(`task_conditions`)의 중복 규칙을 검사한다.

### `test_a_boundary_may_not_silently_depend_on_a_sibling_under_revision` (행 115–122)
- 성질: 개정 중인 형제에 대한 경계는 셋 가운데 하나를 해야 한다. 다음 개정이 움직일 수 없는 경계라고 밝히거나, 형제를 의존으로 기다리거나, 둘 다 하지 않으면 거부된다.
- 준비: 형제는 `status='waiting'`이고 개정 요청(출처 `AC-revise`)이 있다. 맥락의 `pending_revisions`에는 `AC-revise`가 `TK-window`를 개정 대상으로 두고 대기열에 있다. 경계는 개정 2, `k <= T - s`, 독립 아님이다.
- 실행: 세 번 부른다. (1) 그 경계. (2) 경계를 `k <= tau - 3`, `independent_of_next_revision=True`로 바꾼 것. (3) 원 경계에 형제 의존 조건을 더한 것.
- 단언: (1)은 `"under revision"`을 포함한다. 제품 문구는 "sibling contract is under revision: state a boundary that its next revision cannot move, or wait for it through task_conditions dependencies"다. (2)와 (3)은 `"[]"`다.
- 대역: 없음.

### `test_a_pending_revision_of_the_sibling_counts_as_under_revision` (행 124–128)
- 성질: 형제에 개정 요청이 없어도, 다른 행동이 형제를 개정 대상으로 대기 중이면 형제는 개정 중으로 본다.
- 준비: `sibling()`(개정 요청 없음). `pending_revisions`에는 `AC-other`가 `TK-window`를 `revision_targets`로 두고 대기열에 있다. 경계는 독립 아님이다.
- 실행: `issues(contract_check(sibling_boundaries=[entry]))`.
- 단언: `"under revision"`을 포함한다. 제품은 현재 행동(`AC-this`)과 다른 대기 개정의 쓰기 대상(`planning.action_write_ids`)을 `revising` 집합으로 모은다.
- 대역: 없음.

### `test_a_revision_request_on_the_sibling_counts_as_under_revision` (행 130–133)
- 성질: 대기 개정 행동이 없어도, 형제의 현재 개정에 개정 요청이 있으면 형제는 개정 중으로 본다.
- 준비: `sibling(revision_requested={"revision": 2, ...})`. `pending_revisions`는 없다. 경계는 독립 아님이다.
- 실행: `issues(contract_check(sibling_boundaries=[entry]))`.
- 단언: `"under revision"`을 포함한다. 제품 `planning.revision_requested`는 요청의 `revision`이 과제의 현재 `revision`과 같을 때 참이다.
- 대역: 없음.

### `test_a_cited_record_must_exist` (행 135–137)
- 성질: 후보 본문이 인용한 레코드 ID는 입력이나 그 `record_index`에 있어야 한다.
- 준비: 후보의 `scope.included`를 "Apply KN-missing to the given inputs."로 바꾼다.
- 실행: `issues(contract_check())`.
- 단언: 결과에 `"KN-missing"`이 있다. 제품은 본문(제목, 질문, 범위, 기대 출력, 의무와 진척 기준의 주장)에서 `TK-`/`KN-` 형식의 ID를 정규식 `RECORD_ID`로 찾는다. 알려진 ID가 아니면 "cited record is neither in the supplied input nor in its record_index: KN-missing"을 낸다.
- 대역: 없음.

## 관계

- 같은 제품 기능의 다른 층: 이 모듈은 생산자가 제출 전에 받는 검사(`payload_issues`)만 본다. 독립 계약 검토(`task_contract_review`)의 판정 형식은 `test_contracts`의 `test_invalid_decisions_fail`이 다룬다. 과제 계약 자체의 구조는 `test_task_contracts`가 다룬다. 제출 검사의 다른 규칙과 미리보기, 봉인은 `test_submission_checks`가 본다.
- 픽스처 의존: `research_fixtures.candidate`, `record_fixtures`의 `contract_check`, `preparation_context`, `preparation_issues`. `preparation_issues`를 통해 `runner_fixtures`의 `common`, `rating`과 `research_fixtures.supply_observation_rules`에도 간접적으로 의존한다.
- 이 모듈에만 있는 도우미: `ContractCheckTests.issues`, `ContractCheckTests.sibling`.
- 겹치거나 보완하는 시험: "개정 중"을 만드는 두 원인을 따로 검사한다. 개정 요청은 `test_a_revision_request_on_the_sibling_counts_as_under_revision`이, 대기 개정 행동은 `test_a_pending_revision_of_the_sibling_counts_as_under_revision`이 본다. `test_a_boundary_may_not_silently_depend_on_a_sibling_under_revision`은 둘이 함께 있을 때 허용되는 두 해소 방식을 본다. 의존을 적는 두 위치는 `test_primary_and_extension_dependencies_both_wait_for_a_sibling_under_revision`이 본다.

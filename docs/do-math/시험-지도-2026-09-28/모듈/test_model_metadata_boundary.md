# test_model_metadata_boundary

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_model_metadata_boundary.py` (141행) |
| 클래스 / 테스트 | 1 / 6 |
| 시험 대상 제품 코드 | `do_math/planning_engine.py`의 `PlanningEngineMixin._apply_model_metadata`, `_ensure_model_assessments`; `do_math/model_policy.py`의 `validate_assessments`, `selection`, `assessment_basis`, `LIMITS`; `do_math/execution_profiles.py`의 `select_profile`, `build_profiles`, `profile_ref`; `do_math/contracts.py`의 `task_candidate_record`; `do_math/planning.py`의 `contract_hash`, `revision_requested` |
| 사용하는 픽스처 모듈 | `engine_fixtures.routing_engine`; `research_fixtures`의 `bare_engine`, `candidate`, `disposition`, `prepared_rule_conditions`; `record_fixtures.approved_task`; `runner_fixtures.rating`(뒤의 셋은 테스트 안에서 늦게 import) |
| 격리 표지 | 없음 |
| 시작 상태 | 네 단 밖(시험 1, 2, 5는 `routing_engine`, 시험 6은 `bare_engine` 위의 손으로 쓴 상태). 시험 3과 4는 1단(계약 생성기와 선택기 직접 호출) |

## 목적

모듈 docstring은 없다. 이 모듈은 모델 메타데이터의 경계를 본다. 모델 메타데이터란 과제의 난이도·중요도 평가(`model_assessment`), 역할별 모델 선택, 형식 과제의 신뢰 환경 결합을 말한다. 세 가지 성질이 있다.

- 이 메타데이터는 모델이 작성한 전송 형태(wire), 곧 계획의 처분(`dispositions`)과 준비의 후보(`candidates`)를 바꾸지 않는다. 대신 실행 레코드의 `model_decisions`나 수신자 쪽 계약 필드에 따로 기록된다. 제품 주석은 `planning_engine.py` 29–30행의 "Keep the authored wire candidate unchanged."다.
- 평가의 범위 규칙이 있다. `validate_assessments`의 docstring은 준비가 후보나 배정 과제를 정확히 한 번씩 평가한다고 말한다. 또 계획은 선택한 과제를 저장된 평가를 바꾸거나 없는 평가를 채울 때만 평가한다고 말한다.
- 계약 검토가 거부한 뒤 새로 준비된 평가는, 이미 처리된 거부 때문에 지워지지 않는다.

## 모듈 수준 요소

- 행 6: `sys.path.insert(0, str(Path(__file__).resolve().parents[1]))`로 `scripts/` 폴더를 경로 앞에 넣는 공통 머리다.
- 행 141: 직접 실행하면 `unittest.main()`을 부른다.

## ModelMetadataBoundaryTests (행 14–138)

`unittest.TestCase`를 그대로 상속한다. 표지, 클래스 속성, 훅, 도우미 메서드가 없다. `routing_engine()`은 `bare_engine(store=NoRepository())` 위에 거버넌스가 시작된 최소 인스턴스와 빈 런타임(`tasks`, `executions`, `queue` 등)을 붙인 엔진이다. `_bind_revision_action`, `_cancel_selected_revision_targets`, `_record_output_questions` 세 메서드는 `create_autospec` 대역으로 바뀌어 있다(`engine_fixtures.py` 369–382행).

### `test_plan_receiver_records_model_decisions_without_changing_the_authored_dispositions` (행 15–33)
- 성질: 계획 수신자는 선택된 과제의 모델 평가를 실행의 `model_decisions`에 기록하되, 모델이 작성한 처분 목록은 바꾸지 않는다. 평가가 필요한 선택 과제를 빠뜨리거나 선택되지 않은 과제를 평가하면 거부한다.
- 준비: `routing_engine()`의 설정을 `DEFAULT_CONFIG` 사본으로 둔다. 처분은 `TK-selected`(선택)와 `TK-waiting`(`kind='not_selected'`)이고, 런타임에 과제는 없다. 평가 `rating`은 난이도 low, 중요도 medium이다. 실행 `EX-plan`의 `extensions.model_assessments`에 `TK-selected`의 평가 하나를 둔다.
- 실행: `engine._apply_model_metadata({'role': 'research_plan'}, output, 'EX-plan')`를 세 번 부른다. 평가 목록은 차례로 `TK-selected` 하나, 빈 목록, `TK-selected`와 `TK-waiting` 둘이다.
- 단언: 첫 호출 뒤 `model_decisions`가 `{'TK-selected': rating}`이고, `output`이 호출 전 사본과 같다. 둘째 호출은 `ValueError`(정규식 `'missing'`), 셋째 호출은 `ValueError`(정규식 `'unexpected'`)다.
- 대역: `routing_engine`의 autospec 대역 셋(이 경로에서는 불리지 않는다).
- 비고: 제품의 커버리지 오류 메시지는 `"model assessment coverage: " + json.dumps({"missing": [...], "unexpected": [...]})`이다(`model_policy.py` 80–83행). 두 키가 언제나 함께 실리므로, 정규식 `'missing'`과 `'unexpected'`는 어느 쪽 위반이든 맞는다. 곧 이 두 단언은 커버리지 오류가 났다는 것만 고정하고, 빠뜨림인지 초과인지는 가르지 않는다. 실제로는 둘째 호출이 빠뜨림(`missing: ["TK-selected"]`), 셋째 호출이 초과(`unexpected: ["TK-waiting"]`)다.

### `test_plan_rates_a_selected_task_only_to_change_or_supply_its_stored_assessment` (행 35–56)
- 성질: 계획은 저장된 평가가 없는 선택 과제는 반드시 평가하고, 저장된 평가가 있는 선택 과제는 바꿀 때만 평가할 수 있다. 선택되지 않은 과제는 평가할 수 없고, 같은 과제를 두 번 평가할 수 없다.
- 준비: 런타임 과제는 둘이다. `TK-kept`는 저장된 평가 `stored`가 있고, `TK-unrated`는 평가가 없다. 처분은 두 과제의 선택과 `TK-waiting`의 비선택이다. 지역 함수 `apply(rows)`는 `EX-plan`의 평가 목록을 `rows`로 바꿔 `_apply_model_metadata`를 부르고 `model_decisions`를 돌려준다. `changed`는 난이도와 중요도 모두 high인 평가다.
- 실행: 지역 함수 `apply`로 평가 목록 다섯 가지를 차례로 적용한다. 각 적용은 `_apply_model_metadata({'role': 'research_plan'}, output, 'EX-plan')` 호출이다.
- 단언: 단계별로 확인하는 결과는 다음과 같다.
  - `[TK-unrated: stored]`는 `{'TK-unrated': stored}`다. 저장된 평가가 있는 `TK-kept`는 평가하지 않아도 된다.
  - `[TK-kept: changed, TK-unrated: stored]`는 두 평가를 모두 기록한다. 저장된 평가를 바꾸는 것은 허용된다.
  - `[TK-kept: changed]`는 `ValueError`(`'missing'`)다. `TK-unrated`가 빠졌다.
  - `[TK-unrated, TK-waiting]`은 `ValueError`(`'unexpected'`)다.
  - `TK-unrated`를 두 번 평가하면 `ValueError`(`'duplicate'`)다.
- 대역: `routing_engine`의 autospec 대역(불리지 않는다).
- 비고: 앞 시험과 같이 `'missing'`과 `'unexpected'`는 위반의 종류를 가르지 못한다. `'duplicate'`는 커버리지 검사 전에 나는 별도 메시지 `"duplicate model assessment: TK-unrated"`로 고정된다(`model_policy.py` 53–54행). 이름의 "only to change"는 저장된 평가와 같은 값을 다시 내는 경우를 따로 막는다는 뜻으로 읽힐 수 있다. 그러나 제품은 선택된 과제의 재평가를 값과 무관하게 허용하며(`allowed = selected_task_ids`), 이 시험도 같은 값의 재평가를 거부하는지는 보지 않는다.

### `test_formal_contract_binds_the_supplied_environment_without_changing_wire` (행 58–66)
- 성질: 형식 과제의 계약을 만들 때 수신자가 준 신뢰 환경이 계약에 결합되고, 입력 후보는 바뀌지 않는다. 형식 과제가 아니면 신뢰 환경을 결합하지 않는다.
- 준비: `candidate('formal work', formal=True)`와 그 깊은 사본.
- 실행: `task_candidate_record(item, task_id='TK-one', trust_environment_id='TE-author')`. 이어서 `work_class`를 `'nonformal'`로 바꾼 후보로 `task_id='TK-other'` 호출.
- 단언: 첫 계약의 `trust_environment_id`가 `'TE-author'`이고, 후보가 사본과 같다. 둘째 계약에는 `trust_environment_id`가 없다.
- 대역: 없음.
- 비고: 제품은 `candidate['work_class'] == 'formal'`이고 환경이 주어질 때만 결합한다(`contracts.py` 71–72행). 후보는 `copy.deepcopy`로 복사되어 계약이 된다.

### `test_task_work_allowlist_does_not_block_the_independent_contract_reviewer` (행 68–88)
- 성질: 과제의 프로필 허용 목록은 그 과제의 연구 작업에만 적용되고, 독립 계약 검토자는 자기 역할의 채택 프로필을 쓴다. 허용 목록이 비면 연구 작업의 선택이 거부된다.
- 준비: `DEFAULT_CONFIG` 사본으로 `build_profiles`를 부른다. `research_work`의 low 등급 프로필 `work`를 고른다. 과제 `TK-one`은 `profile_refs=[profile_ref(work)]`이고 평가는 low/low다.
- 실행: `model_policy.selection(config, {'role': 'task_contract_review', 'target': 'TK-one'}, tasks, {}, instance=instance)`, 같은 과제에 대한 `research_work` 선택, 그리고 `profile_refs=[]`로 바꾼 뒤의 `research_work` 선택.
- 단언:
  - 검토자 선택의 프로필은 역할이 `'task_contract_review'`이고, 등급이 `config['role_tiers']['task_contract_review']`와 같다. 과제 평가 low가 역할 하한 medium보다 낮으므로 하한이 이긴다.
  - 작업 선택의 `profile_ref`는 `profile_ref(work)`다.
  - 빈 허용 목록의 작업 선택은 `ValueError`를 메시지 조각 `'permitted role/model edition'`으로 낸다.
- 대역: 없음.
- 비고: 제품 주석(`model_policy.py` 146–148행)은 과제의 허용 목록이 그 과제의 작업 시도를 다스리고, 검토자와 다른 판단 역할은 자기 역할 프로필을 쓰되 과제의 난이도·중요도 요구는 물려받는다고 설명한다. 거부 메시지는 `select_profile`의 `"profile selection must resolve to exactly one permitted role/model edition"`이다.

### `test_assessment_is_preserved_without_changing_the_candidate_wire_shape` (행 90–107)
- 성질: 준비 역할의 평가는 후보 제목으로 식별되어 `model_decisions`에 기록된다. 후보 목록 자체는 바뀌지 않으며, 계약은 평가 필드 없이 후보에서 만들어진다.
- 준비: `routing_engine()`, 기본 설정. `candidate('bounded observation')`의 `profile_refs`를 기본 설정의 `research_work` 프로필 하나로 채운다. `output={'candidates': [item]}`과 그 사본. 실행 `EX-prepare`에는 `task_title`로 식별한 평가 하나를 둔다.
- 실행: `engine._apply_model_metadata({'role': 'research_preparation'}, output, 'EX-prepare')`, 이어서 `task_candidate_record(output['candidates'][0], task_id='TK-test')`.
- 단언: `output`이 사본과 같다. `model_decisions`가 `{item['title']: rating}`이다. 계약의 `title`이 후보 제목이다.
- 대역: `routing_engine`의 autospec 대역(불리지 않는다).
- 비고: 이름의 "without changing the candidate wire shape"는 `output`의 불변으로 확인된다. 계약에 평가가 들어가지 않는다는 것은 단언하지 않는다. 제품 주석은 평가를 과제 레코드에 설치하는 일이 과제 생성자의 호출자 몫이라고 한다.

### `test_processed_rejection_cannot_erase_a_fresh_equal_or_changed_assessment` (행 109–138)
- 성질: 계약 검토의 거부로 한 번 지워진 평가를 준비가 새로 채우면, 그 새 평가는 값이 옛것과 같든 다르든 이미 처리된 거부 때문에 다시 지워지지 않는다. 대기 중인 새 검토도 큐에서 빠지지 않는다. 새로운 비승인 검토가 오면 그때는 지워진다.
- 준비: `subTest(unchanged=...)` 두 경우(거짓, 참). 경우마다 다음을 준비한다.
  - `record_fixtures.approved_task()`로 승인된 과제, 인스턴스, 런타임을 받는다.
  - `prepared_rule_conditions([task['id']])`로 초기 관찰 규칙을 붙인다.
  - 인스턴스 설정을 `{'session_limits': deepcopy(LIMITS)}`로 둔다.
  - 과제를 학술 요구 `R`에 속하게 하고, 현재 개정에 대한 수정 요청(`source='REJECT'`)과 평가 `rating()`을 준다.
  - 그 시점의 `assessment_basis(task)`에 `decision='revision_required'`, `execution_id='REJECT'`인 검토 하나를 둔다.
  - 이 상태의 `bare_engine(instance, runtime)`으로 `_ensure_model_assessments()`를 한 번 불러 거부를 처리한다.
- 실행:
  1. 새 평가를 넣는다. 같은 경우는 `rating()`, 다른 경우는 중요도만 `'high'`로 바꾼 평가다. 관찰 규칙도 다시 넣는다. 큐를 `[{'id': 'NEW-REVIEW', 'role': 'task_contract_review', 'target': 과제}]`로 둔다.
  2. `_ensure_model_assessments()`를 세 번 부른다.
  3. 현재 기준으로 `decision='unresolved'`, `execution_id='REJECT-NEW'`인 검토를 더하고 한 번 더 부른다.
- 단언: 2 뒤에 `model_assessment`가 새 평가와 같다. `model_assessment_history`는 1개(첫 거부 처리 때의 것)다. 큐의 ID 목록은 `['NEW-REVIEW']`뿐이다. 3 뒤에는 `model_assessment`가 없고, 이력이 2개다.
- 대역: 없음(`bare_engine`의 메모리 저장소 대역은 이 경로에서 쓰이지 않는다).
- 비고: 두 경우가 보존되는 경로는 서로 다르다.
  - `assessment_basis`는 `contract_hash`를 쓰고, 계약 필드 `CONTRACT_FIELDS`에는 `model_assessment`와 `initial_observation_rules`가 들어 있다(`planning.py` 23–27행). 따라서 같은 평가와 같은 규칙을 다시 넣으면 기준이 옛 거부 검토와 다시 맞는다. 이때는 그 검토가 이미 소비되었다는 표시, 곧 `observation_rule_history`의 `contract_review_execution == 'REJECT'`가 재삭제를 막는다(`planning_engine.py` 117–122행). 제품 주석은 "A fresh assessment may legitimately keep the same value."다.
  - 다른 평가는 기준이 달라져 옛 검토와 맞지 않으므로 처음부터 건너뛴다.

  세 번 반복은 처리가 멱등임을 확인한다. 첫 처리 뒤 제품이 큐에 넣은 `research_preparation` 요청은 시험이 큐를 덮어써서 지운다. 따라서 큐 단언은 새 요청이 다시 생기지 않고 `NEW-REVIEW`가 지워지지 않음을 본다.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈:
  - 모델 평가가 엔진 경로에서 준비되고 검토되는 흐름은 `test_model_assessment_flow`가 본다. 그 모듈은 `purpose_fixtures.assessment_preparation_instance`의 유일한 소비자이고, 자기 빌드 `rejected_assessment_instance`를 둔다. 이 모듈은 수신 함수 하나씩을 손으로 만든 상태에서 본다.
  - 역할별 모델 선택과 프로필 고정은 `test_execution_profiles`의 `test_selection_is_pinned_and_contract_allowlist_is_enforced`와 `test_explicit_old_edition_uses_its_model_but_preserves_floor_and_allowlist`가 본다. 이 모듈의 넷째 시험은 허용 목록이 검토자에게 미치지 않는다는 한 점만 본다.
  - `test_claude_adapter`의 `test_mixed_models_use_existing_selection_and_per_model_work_slots`도 `selection`을 부르지만 인스턴스 없이 모델만 본다.
- 픽스처 의존: `routing_engine`(engine_fixtures), `bare_engine`, `candidate`, `disposition`, `prepared_rule_conditions`(research_fixtures), `approved_task`(record_fixtures), `rating`(runner_fixtures). 픽스처 모듈 넷(`engine_fixtures`, `research_fixtures`, `record_fixtures`, `runner_fixtures`)을 쓴다.
- 이 모듈에만 있는 도우미: 없다(지역 함수 `apply`는 둘째 테스트 안에만 있다).

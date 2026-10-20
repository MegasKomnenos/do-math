# test_academic_preparation

| 항목 | 값 |
|---|---|
| 조각 | `academic` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_academic_preparation.py` (173행) |
| 클래스 / 테스트 | 2 / 8 |
| 시험 대상 제품 코드 | `do_math/submission.py`의 `payload_issues`; `do_math/contracts.py`의 `action_schema`; `do_math/model_policy.py`의 `assessment_basis`; `do_math/planning.py`의 `action_read_ids`, `revision_waits`; `do_math/revision_engine.py`의 `RevisionEngineMixin._retire_closed_revision_targets`(11행); `do_math/planning_engine.py`의 `_ensure_model_assessments`(104행), `_finish_assessment_preparation`(171행), `_apply_model_metadata`(12행; "preparation target has a live execution", "task edition changed"); `do_math/engine.py`의 `run`, `_activity_for_action`; `do_math/lifecycle_engine.py`의 `_refresh_readiness`; `do_math/activities.py`의 `wait_for` |
| 사용하는 픽스처 모듈 | `purpose_fixtures`(`ActivatedPurposeHarness`, `PurposeRunner`, `prepared_assessment_engine`); `research_fixtures`(`candidate`, `prepared_rule_conditions`, `seal_response`); `runner_fixtures`(`common`, `rating`) |
| 격리 표지 | 없음 |
| 시작 상태 | `RuleSubmissionTests`는 1단(검증기와 순수 함수 직접 호출, 임시 작업공간). `RulePreparationFlowTests`는 2단 위의 공유 빌드 `purpose_fixtures.assessment_preparation_instance` |

## 목적

모듈 docstring(행 1)은 "배정된 관찰 준비: 생산자 범위와 엔진 전이"를 시험한다고 밝힌다. 여기서 관찰 준비(observation preparation)는 이미 있는 과제에 관찰 규칙(`observation_rules`)을 채우도록 준비 역할에 배정한 행동이다. 그 행동은 `observation_rule_targets`를 갖는다. 모델 평가 배정(`assessment_targets`)과 한 행동에 묶일 수 있다.

이 모듈은 두 층을 본다. 첫째 층은 생산자 제출 검사(`payload_issues`)가 강제하는 규칙이다. 배정된 대상을 정확히 덮어야 하고, 유보(deferral)는 명시적이고 완전하며 배타적이어야 하고, 대상 밖 편집이나 옛 판본은 거부된다. 둘째 층은 엔진 전이다. 결합 준비가 사용자 계약 조항을 보존한 채 새 판본과 새 계약 검토를 게시하는지 본다. 유보가 관련 입력이 바뀔 때까지 기다리는지 본다. 수신기가 실행 중이거나 바뀐 대상을 바꾸지 않고 거부하는지 본다.

## 모듈 수준 요소

- 행 8: `scripts/`를 `sys.path` 앞에 넣는 공통 머리.
- 행 172–173: 직접 실행하면 `unittest.main()`.

모듈 함수와 상수는 없다.

## RuleSubmissionTests (행 19–87)

- 기반 클래스: `unittest.TestCase`. 표지·속성이 없다.
- `setUp` (행 20–28): 임시 폴더를 작업공간으로 두고 정리 훅을 건다. 과제 `TK-one`은 `candidate('one')`에 `revision=1`, `status='planned'`를 붙인 것이다. 행동 `AC-rules`는 `research_preparation`이고 `observation_rule_targets={'TK-one': assessment_basis(task)}`를 갖는다. 문맥은 `budget_unit='concurrent_sessions'`, 과제 목록, 빈 지식 목록·종류 정의·원천이다. 1단 시작 상태다.
- 도우미 `issues(extensions, candidates=None)` (행 30–35): 준비 출력(`common('research_preparation')`에 `candidates`)을 만든다. `extensions`를 `activity-extensions.json`에 쓰고 `seal_response`로 통합 묶음을 봉인한 뒤 `payload_issues(output, action_schema(action), context, extensions, workspace)`를 돌려준다. 빈 목록이면 통과다.

### `test_rules_only_and_combined_preparation_cover_exact_assignments` (행 37–42)
- 성질: 규칙만 배정된 준비는 대상의 규칙 조건으로 통과한다. 모델 평가까지 배정된 결합 준비는 평가도 내야 통과한다.
- 준비: `setUp`. 확장 `task_conditions=prepared_rule_conditions(['TK-one'])`.
- 실행: 그대로 검사한다. 행동에 `assessment_targets`를 더해 같은 확장으로 검사하고, `model_assessments=[rating(task_id='TK-one')]`를 더해 다시 검사한다.
- 단언: 첫째 `[]`, 둘째 비어 있지 않음, 셋째 `[]`.
- 대역: 없음.
- 비고: 이슈 내용은 보지 않고 있다·없다만 본다.

### `test_deferral_is_explicit_complete_and_exclusive` (행 44–51)
- 성질: 규칙 준비를 미루려면 대상마다 명시적 유보를 한 번씩 내야 한다. 같은 대상에 유보와 규칙을 함께 낼 수 없다.
- 준비: `setUp`. 유보 행은 `task_id='TK-one'`, 사유, `missing_inputs=['source:paper']`, `next_owner='research_preparation'`이다.
- 실행: 네 확장으로 `issues`. 빈 확장, 유보 하나, 같은 유보 둘, 유보와 규칙 조건이다.
- 단언: 빈 확장은 이슈가 있다(묵시적 생략 금지). 유보 하나는 `[]`다. 중복은 이슈가 있다. 유보와 규칙을 함께 내도 이슈가 있다.
- 대역: 없음.

### `test_unauthorized_contract_edits_foreign_targets_and_stale_editions_fail` (행 53–60)
- 성질: 규칙 준비는 규칙 밖의 계약 필드를 고칠 수 없다. 배정되지 않은 대상을 다룰 수 없고, 새 후보를 낼 수 없으며, 옛 판본을 대상으로 할 수 없다.
- 준비: `setUp`. 올바른 규칙 조건 `good`.
- 실행: `good[0]`에 `dependencies`, `task_title`, `completion_obligations`를 하나씩 더해 검사한다. 다른 대상 `TK-other`의 조건, `good`에 새 후보 `candidate('new')`, 과제 `revision`을 올린 뒤의 `good`도 검사한다.
- 단언: 여섯 경우 모두 이슈가 있다.
- 대역: 없음.
- 비고: 루프로 도는 세 필드 경우에 `subTest`를 쓰지 않는다. 이슈 내용은 고정하지 않는다.

### `test_assigned_rules_are_declared_writes_and_keep_other_readers_out` (행 62–71)
- 성질: 배정된 규칙 준비는 그 대상에 대한 선언된 쓰기다. 그래서 준비가 도는 동안 같은 대상의 계약 검토는 기다린다. 대상의 작업이 도는 동안에는 준비가 기다린다.
- 준비: `setUp`. 런타임에 과제, 큐에 행동, 실행 중인 `EX-rules`를 둔다.
- 실행: `action_read_ids(action, instance, runtime)`와 `revision_waits(검토 행동, ...)`를 부른다. 이어 실행을 대상의 작업 `EX-work`로 바꾸고 `revision_waits(action, ...)`를 부른다.
- 단언: 읽기 ID에 `'TK-one'`이 있다. 검토 대기가 비어 있지 않다. 작업이 도는 동안 준비 대기가 비어 있지 않다.
- 대역: 없음.
- 비고: 이름의 "declared writes"는 `action_read_ids`에 대상이 포함되는지로 확인한다. 대기 내용은 보지 않고 비어 있지 않은지만 본다.

### `test_terminal_targets_retire_without_erasing_other_preparation_obligations` (행 73–87)
- 성질: 종결된 대상은 규칙 준비 행동에서 빠지지만, 다른 대상의 의무는 남는다. 모든 대상이 종결되면 행동이 큐에서 빠진다.
- 준비: `setUp`. 행동 사본에 대상 `TK-two`를 더한다. `TK-one`은 `closed`, `TK-two`는 `planned`다. `SimpleNamespace(runtime=..., _remove_action=...)` 호스트를 둔다.
- 실행: `RevisionEngineMixin._retire_closed_revision_targets(host)`. `TK-two`를 `completed`로 바꾸고 다시 부른다.
- 단언: 첫 호출 뒤 대상 키가 `{'TK-two'}`이고 큐가 `[action]`이다. 둘째 호출 뒤 큐가 비어 있다.
- 대역: `SimpleNamespace` 호스트. 엔진 없이 믹스인 메서드를 직접 부른다.

## RulePreparationFlowTests (행 90–169)

- 기반 클래스: `ActivatedPurposeHarness`(`setUp`의 `install_adapter_fixture`). 표지·속성이 없다.
- 도우미 `prepare()` (행 91–98): `purpose_fixtures.prepared_assessment_engine(self)`를 부른다. 이것은 `assessment_preparation_instance`를 `ASSESSMENT_CONFIG`로 복원하고 `PurposeRunner`를 단다. 그 빌드(`purpose_fixtures` 573–602행)의 상태는 다음과 같다. 2단 합성 활성 상태에 공개 헌장 결정으로 요구 `r`을 승인했다. 학술 과제 `TK-academic-1`과 `TK-academic-2`를 넣고, 계약 검토 대신 평가 전용 준비 하나가 게시되어 있다. 이 도우미는 큐를 비우고 모든 과제의 `initial_observation_rules`를 비운 뒤 `_refresh_readiness()`와 `_save()`를 부른다. 그 결과 관찰 규칙과 모델 평가가 모두 없는 두 과제를 대상으로 한 결합 준비가 큐에 선다.

### `test_combined_preparation_preserves_user_terms_and_publishes_fresh_review` (행 100–128)
- 성질: 결합 준비(규칙과 모델 평가)는 사용자 계약 조항을 바꾸지 않은 채 규칙과 평가를 채운다. 새 판본마다 계약 검토를 하나씩 게시한다. 규칙을 기다리던 실패 행동의 대기를 풀고 활동을 끝낸다. 연구 주기는 올리지 않는다.
- 준비: `prepare()`. 큐에서 규칙 대상을 가진 행동을 찾아, `assessment_targets`와 `observation_rule_targets`의 키가 같음을 단언한다. 실패 행동 `AC-old-rules`(`research_work`)의 활동을 `_activity_for_action`으로 잡는다. `activities.wait_for(... reason='missing rules', condition={'kind': 'observation_rules'}, next_owner='research_preparation')`로 대기시키고, `waiting_actions`에도 넣고 저장한다.
- 실행: `PurposeRunner()`로 `run(max_steps=1)`. 픽스처는 `assessment_targets`에 평가를 쓰고 `observation_rule_targets`에 `prepared_rule_conditions`를 쓴다(`purpose_fixtures` 190–216행).
- 단언:
  - 실패 행동이 대기에 없고, 그 활동이 `finished`다.
  - 과제마다 `question`, `scope`, `expected`, `completion_obligations`, `academic_requirement_id`, `authority_refs`가 이전과 같다. `revision`은 1 올랐다. `initial_observation_rules`와 `model_assessment`가 비어 있지 않다.
  - 그 과제 대상 `task_contract_review`가 정확히 1개이고, 그 `contract_basis.revision`이 새 판본이다.
  - `runtime['cycles'] == 0`이다.
  - 이력에 `observation_rules_resolved`가 있다.
- 대역: `PurposeRunner`(실제 Windows Job), `FixtureAdapter`.

### `test_assessed_task_rule_deferral_waits_for_relevant_new_input` (행 130–152)
- 성질: 이미 평가된 과제의 규칙 준비를 유보하면 그 행동은 기다린다. 관련 없는 원천이 추가돼도 다시 열리지 않고, 유보가 요구한 원천(`source:paper`)이 생겨야 다시 준비가 큐에 선다.
- 준비: `prepare()`. 과제마다 `rating(task_id=...)`에서 `task_id`를 뺀 모델 평가를 넣고 큐를 비운 뒤 `_ensure_model_assessments()`를 부른다. 새 행동은 규칙 대상만 있고 `assessment_targets`가 없다. 종료된 준비 실행 `EX-deferred`에 모든 대상의 규칙 유보(`missing_inputs=['source:paper']`)를 둔다.
- 실행:
  1. `_finish_assessment_preparation(action, 'EX-deferred')`.
  2. 큐를 비우고 `_ensure_model_assessments()`.
  3. 원천 `unrelated`를 추가하고 `_ensure_model_assessments()`.
  4. 원천 `paper`를 추가하고 `_ensure_model_assessments()`.
- 단언: 새 행동에 `assessment_targets`가 없다. 유보 뒤와 무관 원천 뒤에는 규칙 대상 행동이 큐에 없다. `paper` 원천 뒤에는 원 행동이 대기에 없고, 규칙 대상 행동이 큐에 있다.
- 대역: 없음(러너 불리지 않음).

### `test_receiver_rejects_a_live_or_changed_target_without_mutating_it` (행 154–169)
- 성질: 수신기는 결합 준비의 결과를 적용할 때, 대상 과제에 실행 중인 작업이 있거나 판본이 바뀌었으면 과제를 바꾸지 않고 거부한다.
- 준비: `prepare()`. 규칙 행동과 그 첫 대상을 고른다. 종료된 실행 `EX-prepare`에 규칙 조건과 모델 평가 확장을 둔다. 대상에 실행 중 작업 `EX-live`를 두고 과제 사본을 뜬다.
- 실행: `_apply_model_metadata(action, {'candidates': []}, 'EX-prepare')`를 부른다. `EX-live`를 지우고 대상 `revision`을 올린 뒤 다시 부른다.
- 단언: 첫 호출은 `ValueError`, 메시지가 `'live execution'`에 맞는다(제품 "preparation target has a live execution: <id>"). 과제가 사본과 같다. 둘째 호출은 `ValueError`, 메시지가 `'edition changed'`에 맞는다(제품 "... task edition changed: <id>").
- 대역: 없음.
- 비고: 둘째 거부 뒤의 불변은 단언하지 않는다.

## 관계

- 같은 제품 기능의 다른 층:
  - 모델 평가 배정의 제출 규칙과 엔진 전이는 `test_model_assessment_flow`가 같은 빌드(`assessment_preparation_instance`)로 본다.
  - 관찰 규칙 자체(문턱, 반복, 자기 점검)는 `test_currentness`의 규칙 시험과 `lifecycle` 조각의 관찰 모듈이 본다.
  - 학술 과제의 생성은 `test_academic_engine`이 본다.
- 픽스처 의존: `purpose_fixtures.prepared_assessment_engine`(두 모듈이 공유; `consumers.json`), `research_fixtures.prepared_rule_conditions`(규칙 응답 픽스처), `seal_response`, `candidate`, `runner_fixtures.rating`/`common`.
- 이 모듈에만 있는 도우미: `RuleSubmissionTests.issues`, `RulePreparationFlowTests.prepare`.
- 겹치거나 보완하는 시험:
  - `RuleSubmissionTests`는 `test_model_assessment_flow.AssessmentSubmissionTests`와 같은 방식이다. 곧 `seal_response` 뒤 `payload_issues`로 이슈 유무를 본다. 이쪽은 규칙 배정을, 저쪽은 평가 배정을 본다.
  - 유보 대기 규칙은 이 모듈의 `test_assessed_task_rule_deferral_...`(규칙 유보, 원천 추가)와 `test_model_assessment_flow`의 유보 시험들(평가 유보, 입력 변경)이 나눠 본다.

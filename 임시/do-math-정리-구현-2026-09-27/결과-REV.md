# 결과-REV: 제출·검토·계약 그룹

## 1. 브랜치, 커밋, 바꾼 파일

- 브랜치: `c-rev` (worktree `C:/math-worktrees/c-rev`, 기준 `c-int`의 `78f00bb`)
- 마지막 커밋: `39e179a` (26개 파일, +541 −476)
- 경로는 모두 `.claude/skills/do-math/scripts/` 기준이다.

**제품 (11)**: `do_math/` 아래 `contracts.py`, `governance.py`, `input_basis.py`, `integration.py`, `reporting.py`, `review_cycle.py`, `review_engine.py`, `review_policy.py`, `submission.py`, `task_contracts.py`, `task_scope.py`

**시험 (14)**: `tests/` 아래 `research_fixtures.py`, `test_approved_five_repairs.py`, `test_connection_repairs.py`, `test_performance_repairs.py`, `test_redesign_ENGINE.py`, `test_redesign_GOVERNANCE.py`, `test_redesign_REVIEWS.py`, `test_redesign_SURFACE.py`, `test_redesign_TASKS.py`, `test_repair_plan.py`, `test_review_engine.py`, `test_review_research.py`, `test_review_scope_wire.py`, `test_submission_flow.py`

**문서 (1)**: `이음새-정본.md`(6절 표에 새 정본 행 추가, `derived_bundles`·`issued_input` 행 보충)

## 2. ID별 처분

- **REV-01: 구현함.** `submission._payload_issues`의 scope 특례를 지우고 `stage != "scope"` 조건을 뺐다. scope 결과도 `review_cycle.validate_visible_output` → `_validate_content`를 지나므로, 생산자 검사가 수신과 같게 `scope_complete=true`와 빈 `questions`를 요구한다. 문서 문장은 4절에 적었다.
- **REV-02: 구현함.** `defer_for_research(cycle, action, output, requests, execution_id, sources, *, limit, ...)`가 요청별 원천 행을 받아 `request_digest`를 `research_request_digest` 하나로 한 번 계산하고 `source_records`도 함께 기록한다. 엔진의 덮어쓰기 대입(옛 1116-1119행)과 봉인 재구성의 둘째 대조 분기, `generated.update(...)`를 지웠다. enqueue 루프는 남겼다.
- **REV-03: 구현함.** `_start_identity_review`가 지식 항목의 `scope_assessment`·`owner_activity_id`·`producer_execution_ids`와 설정의 `review_scope_assessment`를 읽지 않는다. 단계적 검토의 `producer_execution_ids` 읽기도 지웠다. 호출자가 없어진 `start_review`의 `owner_activity_id` 인자를 지우고 시작값을 None으로 고정했다. 엔진이 여는 모든 검토는 scope 단계에서 시작한다.
- **REV-04: 구현함.** 세 가지를 바꿨다.
  - `_admit_review_execution`은 이미 입장한 실행을 만나면 입장 결박만 대조하고 `already_admitted`를 먼저 돌려준다.
  - 수락과 보류는 새 `_checked_review_result`(현재성·독립성·입력 기반) 한 번을 거친다. `_record_review_input`은 확인이 끝난 cycle을 인자로 받는다.
  - 재심사는 독립성을 다시 걷지 않는다. `validate_review_execution`을 독립성과 `validate_review_binding`(배정·입력·프로필 결박)으로 나눠 결박만 부른다.

  문맥 준비는 `_prepare_review_context`가 확인한 cycle을 `_build_review_context`에 넘기고, 스키마를 모듈 함수 `_seat_schema(cycle, action)`로 만든다. 그래서 `_review_cycle`은 한 번만 실행된다.
- **REV-05: 구현함.** `governance.execution_lineage(runtime, execution_id, fields, *, revisit_error=None)`를 두고 세 소비자가 순회를 공유한다. 각 소비자의 판정은 그대로다.
  - `validate_independent_execution`: `continuation_of`만 따라가고, 순환·작성자·없는 행을 거부한다.
  - `validate_review_independence`: 두 필드를 따라가고, 작성자·없는 행·다른 자리 문맥을 거부한다.
  - `_qualified_assessment_defect`: 없는 행에서 None을 돌려준다.

  `_qualified_assessment_defect`의 작성자 집합(`previous_reviews` 작성자 제외)은 사용자 판단 거리이므로 바꾸지 않았다.
- **REV-07: 구현함.** `_prepare_review_context`의 오류 문구 표지 분기(`except ValueError`)를 지웠다.
- **REV-08: 구현함.** `_build_review_context`는 참조 메시지를 `compact_json_bytes(cycle['turns'][slot][index])` 한 줄로 직렬화한다. 재해시·길이 대조와 `KeyError`/`IndexError` 분기를 지웠다. 물질화 경로의 불일치 분기는 남겼다.
- **REV-10: 구현함.** `assessment_basis`와 `assessment_current`가 `records=` 색인을 받는다. `refresh_task_assessments`는 판정이 있는 첫 과제에서 색인을 한 번 만든다. 판정이 없으면 만들지 않으므로 호출 비용이 늘지 않는다. `apply_task_assessments`는 이미 만든 색인을 마지막 `assessment_basis`에도 넘긴다. `planning`의 호출부는 기본값(None)으로 그대로 동작한다.
- **REV-11: 구현함.** `review_policy.SCOPE_ASSESSMENT`(와 `OVERFLOW_DISPOSITIONS`)가 scope 평가의 유일한 모양이다. `stage_schema('scope')`는 이것을 싣는다. `validate_scope_assessment`는 기존 정본 `state_contract.validate_record`로 모양을 한 번 보고, 의미 조건만 남긴다. 의미 조건은 정책 일치, 관점 포괄, 최소 자리, 자리 ID 중복·예약 충돌, 한도 상·하한, 넘침 처분이다. 공백 문자열은 이제 wire와 같이 거부된다. 반환값은 입력의 깊은 사본이다.
- **REV-12: 구현함.** `contracts._object`를 `contracts.closed_object(properties, required=None)`로 공개했다. `submission._object`, `review_cycle._object`, `integration`의 지역 `obj`를 지우고 모두 이것을 쓴다. `review_policy`도 같은 이름을 쓴다.
- **REV-13: 구현함.** `review_cycle.proposal_value(proposal, reference)`를 두고, `classify_research_source`와 `submission._validate_reference`가 부른다.
- **REV-14: 구현함.** `review_cycle.inline_source_row(reference, value)`(생성)와 `inline_source_bytes(source, *, error=...)`(대조)를 두었다. 세 곳이 쓴다: 엔진 `_research_source_spec`, `_materialize_research_sources`, 봉인 재구성. 재구성의 오류 문구 `supplemental source bytes changed`는 `error=` 인자로 유지했다.
- **REV-15: 구현함.** `submission`에 `CHECK_SUBJECT_FIELDS`, `NOT_MACHINE_CHECKED`, `_check_subject`, `_failed_check(mode, context, raw, error, phase, execution_id)`를 두었다. `check_submission`, `_producer_check`, `seal_submission`, 설치 계약의 `not_checked`가 이것을 쓴다. 생산자 기록의 `check_subject`에도 `revision_targets`가 들어간다. 설치 계약 목록에는 빠져 있던 `kind_semantic_approval`이 들어간다. 미리보기 계약의 별개 목록(`future_application_currentness`)은 건드리지 않았다.
- **REV-16: 구현함.** `validate_plan_dispositions`에서 스키마가 이미 강제하는 형태 검사를 지웠다: `dispositions` 존재, 행 dict·`task_id` 문자열, `kind` 열거, `reason`·`next_owner` 텍스트, 평가의 `decision` 열거. `apply_task_assessments`에서는 중복 평가와 `decision` 열거 검사를 지웠다. 의미 검사는 남겼다. 모집단 일치, 선택 시 `expected_research_change`, revisit 해석, `not_assessable`의 missing_inputs, 병렬 참조, 평가 모집단이 그것이다.
- **REV-20: 구현함.** `task_contracts.readiness_for_task`를 지웠다. `reporting.py`와 시험은 `planning.task_ready`를 직접 부른다.
- **REV-21: 구현함.** 네 곳을 `match_profile_ref`로 바꿨다: `review_cycle.validate_review_binding`, `validate_resource_disposition`, `review_engine._reconcile_review_host_profiles`, `submission`의 후보 관찰 프로필 검사.
- **REV-22: 구현함.** 엔진 두 곳이 `config['review_research_limit']`를 읽고, `defer_for_research`의 `limit` 기본값을 없앴다. 봉쇄 재구성은 `instance`가 없으면 `ValueError('review closure replay requires its governing configuration')`로 거부하고, 있으면 `instance['config']['review_research_limit']`를 읽는다. 검증이 든 시험(`test_connection_repairs.py:139,189`, `test_redesign_REVIEWS.py:351-387`)은 봉쇄 경로에 닿지 않는다. 봉쇄 시험은 이미 instance를 넘긴다.
- **REV-24: 구현함.** `issued_input`의 메모 키를 `artifact_key`와 같은 규칙(`git_dir is not None`이면 `str(git_dir)`)으로 맞췄다. `_publish_assessment_reassessment`의 `getattr` 둘을 직접 속성 접근으로 바꿨다. 공용 표지 `'fixture-git'`을 쓰던 시험 5곳은 `'git-' + uuid4().hex`로 바꿨다. `FakeEngine.store`는 `git_dir=None`과 읽으면 `FileNotFoundError`를 내는 `read`를 가진 대역으로 바꿨다. 메모 자체는 유지했다.
- **REV-26: 구현함.** `contracts.py` 모듈 설명을 "Role prompt and output schemas for the CLI adapters of every provider."로 고쳤다.
- **TSB-11: 구현함(통합표의 정정안).** 제품의 `item.get('scope_assessment', config.get('review_scope_assessment'))` 식 전체를 지웠다(REV-03). `FakeEngine` 설정에서 계약 밖 키 `objection_round_limit`, `review_policy`, `review_scope_assessment`를 지우고 `review_research_limit`을 더했다. 지식의 `required_reviews`도 지웠다. 저장 왕복 시험이 키를 떼는 5행이 사라졌다. 미리 정한 범위가 필요한 시험은 새 시험 도우미 `research_fixtures.start_scoped_review`를 쓴다. 이 도우미는 엔진이 연 검토 주기의 scope 필드를 순수 `start_review(..., scope_assessment=...)` 경로로 구성한다. `FakeEngine.start`는 이 도우미를 감싼다.
- **HIS-18: 구현함.** `submission.payload_issues`가 `integration.derived_bundles`를 한 번 계산해 `inspect_bundles`·`split_bundles`에 `derived=`로 넘긴다. `integration._split_research`는 공개 이름 `split_research`로 바꿨다. 호출 세 곳(`payload_issues`, `capture_eligible`, `captured_check`)이 이 이름을 쓴다.
- **커널 후속 1(상태 값 digest): 구현함.** 상태에 저장되고 다시 대조되는 검토 값을 `exact_content_hash`로 옮겼다. 대상은 `review_cycle`의 `proposal_digest`(생성·`_check_proposal`), 발견 키(`_add_findings`, `_organize`, `validate_visible_output`), 대체 입력의 `sealed_input_sha256`(생성·재구성 대조), `input_basis`의 `review_input_basis.sha256`이다. 조사 `request_digest`는 REV-02로 이미 `exact_content_hash` 하나다. 판본은 올리지 않았다.

  남긴 `json_digest`는 둘이다. 하나는 `review_engine`의 `event_sha256`이다. 공급자 이벤트(소수를 담을 수 있음)의 식별이고 다시 대조되지 않는다. 다른 하나는 `validate_transcript`의 진단값 `observed_sha256`이다. 전사 manifest 행의 바이트 규칙 `sha256(compact_json_bytes(message))`과 비교할 관측값이라 같은 규칙을 써야 한다.
- **커널 후속 2(`decision_is_current`): 구현함.** 결정 스키마(`record_schemas/schemas.py:437-444`)에 없는 필드를 읽는 조건을 지웠다. `expires_at`, `valid_from`, `source_basis`와, 같은 이유로 도달하지 않는 `goal_revision`·`policy_revision` 대조다. 7절에 적었다.

처분별 건수: 구현함 23(담당 ID 21, 커널 후속 2), 구현하지 않음 0, 조건 불성립 0, 끝내지 못함 0.

## 3. 새 공유 정의와 위치, 지운 공개 이름

새로 만들었거나 공개한 정의는 모두 `이음새-정본.md` 6절 표에 올렸다.

| 이름 | 위치 | 담는 규칙 |
|---|---|---|
| `closed_object(properties, required=None)` | `contracts.py` | 닫힌 wire 객체 스키마(옛 `contracts._object`의 공개 이름) |
| `SCOPE_ASSESSMENT`, `OVERFLOW_DISPOSITIONS` | `review_policy.py` | scope 평가의 모양과 넘침 처분 어휘 |
| `execution_lineage(runtime, execution_id, fields, *, revisit_error=None)` | `governance.py` | 실행 계보 순회 |
| `validate_review_binding` | `review_cycle.py` | 검토 실행의 배정·입력·프로필 결박(독립성과 분리). 표에는 `validate_review_independence`와 한 행 |
| `proposal_value(proposal, reference)` | `review_cycle.py` | 제안 좌표의 값 |
| `inline_source_row`, `inline_source_bytes` | `review_cycle.py` | 인라인 조사 원천 행의 생성·대조 |
| `split_research(context)` | `integration.py` | 과제 연구 응답의 독립 묶음 여부(옛 `_split_research`) |

모듈 안에서만 쓰는 새 이름은 표에 올리지 않았다: `submission.CHECK_SUBJECT_FIELDS`, `NOT_MACHINE_CHECKED`, `_check_subject`, `_failed_check`, `review_engine._seat_schema`, `ReviewEngineMixin._checked_review_result`. 시험 도우미 `tests/research_fixtures.start_scoped_review`와 `test_review_engine.FakeEngine.start`도 새로 두었다.

지운 이름은 다음과 같다.
- 공개 이름: `task_contracts.readiness_for_task`, `start_review`의 `owner_activity_id` 인자, `defer_for_research`의 `limit` 기본값
- 비공개 이름: `contracts._object`, `submission._object`, `review_cycle._object`, `integration._split_research`, `review_policy._OVERFLOW_DISPOSITIONS`(공개 `OVERFLOW_DISPOSITIONS`로 바뀜)

## 4. 필요한 문서 변경

- **`계약/동일성-검토.md` 「범위 계획 단계」 절**(REV-01): 첫 문단 끝에 다음 문장을 더한다. "범위 계획 결과의 `scope_complete`는 `true`, `questions`는 빈 배열이어야 한다. 둘 중 하나라도 어기면 제출 검사와 수락이 모두 반려한다."
- 그 밖의 스킬 문서와 `AGENTS.md`에 바꿀 곳은 없다. `review_scope_assessment`, `readiness_for_task`, `_split_research`, 기계 검사의 `not_checked`·`check_subject` 목록을 적은 문서는 grep으로 찾지 못했다(`.agents/` 사본 제외).

## 5. 실행한 시험

모든 실행은 `scripts/run_tests.py`로 하나씩 돌렸다. 실제 Lean이 필요한 시험에는 `DO_MATH_KNOWLEDGE_TEST_LEAN`을 주었다.

- **기준(변경 전, `78f00bb`)**: `test_review_engine test_review_cycle test_review_research test_review_scope_wire test_redesign_REVIEWS test_task_scope test_submission_flow test_submission_tools test_submission_boundaries test_connection_repairs test_redesign_TASKS test_contracts`. 결과는 통과 260, 실패 0, 오류 0이다(630초).
- **편집 확인 1**: `test_review_cycle test_review_scope_wire test_redesign_REVIEWS test_redesign_GOVERNANCE.ExecutionLineageTests test_contracts test_review_research.PureResearchTests`. 결과는 통과 67, 오류 1이다. 오류는 `test_redesign_REVIEWS.ReassessmentGitTests.test_actual_split_state_suspend_review_save_reload_and_next_owner`였다. 시험이 `config = {}`로 계약 밖의 빈 설정을 만들어 `review_research_limit`이 없었기 때문이다(REV-22). 시험 설정에 그 키를 주도록 고친 뒤 그 시험만 다시 돌려 통과 1을 얻었다.
- **편집 확인 2**: `test_review_engine test_review_research test_connection_repairs.ReviewScopeBudgetTests test_redesign_TASKS test_task_scope`. 결과는 통과 124, 실패 0, 오류 0이다.
- **인계 확인(커밋 직전 코드)**: 결과는 통과 269, 실패 0, 오류 0이다(614초). 대상은 다음과 같다.
  - 모듈 13개: `test_contracts test_review_cycle test_review_engine test_review_research test_review_scope_wire test_redesign_REVIEWS test_redesign_TASKS test_task_scope test_submission_flow test_submission_tools test_submission_boundaries test_reporting test_impact_bundle`
  - 고친 시험 ID 11개
    - `test_connection_repairs.ReviewScopeBudgetTests`
    - `test_redesign_GOVERNANCE.ExecutionLineageTests`
    - `test_redesign_GOVERNANCE.AuditRepairTests.test_actual_engine_delegation_control_to_independent_judgments_effect_and_receipt`
    - `test_redesign_ENGINE.ImpactReviewRouting.test_unresolved_review_remains_held_and_has_one_final_rejected_receipt`
    - `test_redesign_ENGINE.ReceiptAndQuotaConnections.test_task_receipt_occurs_once_after_the_complete_bundle_result`
    - `test_redesign_ENGINE.DelegationConnections.test_actual_blind_judgments_apply_the_approved_review_recovery`
    - `test_redesign_SURFACE.SurfaceRedesignTests.test_engine_review_context_reaches_role_input_with_bound_identity_and_policy`
    - `test_approved_five_repairs.WaitOwnershipTests`의 `test_new_user_wait_survives_successful_response`와 `test_resolved_publication_and_impact_waits_are_removed`
    - `test_performance_repairs.ImpactReviewRetryTests.test_sealed_bytes_are_read_only_after_every_requested_review_ended`
    - `test_repair_plan.GoalAuditFlowRepairTests.test_recovery_confirms_termination_before_using_original_seal_without_recollection`
- **소비자 쪽 기계 확인**: 바꾼 `.py` 파일을 모두 `py_compile`했다. `tests/`의 `test_*.py` 135개를 모두 `importlib`로 적재했고 실패는 0이다. 옛 이름 grep(`_split_research`, `readiness_for_task`, `review_scope_assessment`, `objection_round_limit`, `required_reviews`, 영역 안 `resolve_profile`)에서 남은 참조는 `knowledge.py:87`의 필드 이름 목록뿐이다(8절).
- 변경 전부터 실패하던 시험은 없다.
- 돌리지 않은 관련 시험: 인계 확인 범위 밖의 소비자 모듈은 시험 지침 2절에 따라 통합 확인에 맡겼다. 예를 들어 `governance`·`integration`·`contracts`를 쓰는 다른 모든 모듈이 여기에 든다.

## 6. 기능이나 시험 범위가 바뀐 것

- **scope 결과의 생산자 검사(REV-01)**
  - 이유: 생산자 검사가 수신 조건 일부를 빠뜨렸다.
  - 잃는 것: 없음.
  - 얻는 것: `scope_complete=false`나 남은 질문이 있는 scope 결과가 적용 단계가 아니라 생산자 검사에서 `output` 경로로 반려된다.
  - 시험: `test_review_scope_wire`의 시험을 `test_submission_checks_scope_with_the_conditions_the_review_accepts`로 바꿨다. 실제 검토 주기의 `context_for` 입력에서 세 경우가 생산자 검사와 `accept_result` 양쪽에서 반려됨을 단언한다. 고치기 전 코드에서 이 시험이 실패하는지는 돌려 보지 않았다. 옛 경로가 두 조건을 실행하지 않았다는 사실은 원문으로 확인했다.
- **scope 모양 검사(REV-11)**
  - 이유: 모양 정의가 두 벌이었다.
  - 잃는 것: 수기 검사의 오류 문구. 이제 `scope_assessment/<경로>: <jsonschema 문구>`다.
  - 얻는 것: 공백 문자열이 wire와 같이 거부된다. 새 시험 `test_scope_assessment_rejects_a_blank_text_as_the_scope_wire_does`가 이를 단언한다.
- **검토 시작 상태(REV-03, TSB-11)**
  - 이유: 제품이 시험 전용 키를 읽었다.
  - 잃는 것: 운전에서 닿지 않던 경로뿐이다.
  - 얻는 것: 엔진이 늘 scope 단계에서 연다. `test_redesign_REVIEWS.test_engine_freezes_adopted_policy_and_scope_at_cycle_opening`은 지식 항목의 owner 주입을 단언하던 시험이었다. 이것을 `test_engine_freezes_adopted_policy_and_opens_every_review_at_its_scope_stage`로 바꿨다. 새 시험은 채택 정책 고정, `phase='scope'`, 평가·owner None, scope 행동만 대기함을 단언한다.
- **결정 현재성(커널 후속 2)**
  - 이유: 결정 스키마에 없는 필드를 읽는 조건이었다.
  - 잃는 것: 저장될 수 없는 결정의 만료·시작·원천·거버넌스 판본 대조.
  - 시험: `test_redesign_TASKS.test_bare_unrelated_expired_or_changed_authority_cannot_transfer`에서 결정에 `expires_at`을 넣는 subTest 하나를 지웠다. 시험 이름은 `test_bare_unrelated_or_changed_authority_cannot_transfer`가 되었다.
- **봉쇄 재구성(REV-22)**
  - 이유: 설정 기본값의 사본을 지웠다.
  - 잃는 것: instance 없이 봉쇄 검토를 재구성하는 호출. 이제 거부된다. 제품 호출부는 모두 instance를 넘긴다.
- **계획 형태 오류(REV-16)**
  - 잃는 것: 스키마를 거치지 않은 직접 호출에서 형태 오류가 `ValueError` 문구로 나오지 않는다. 대신 `KeyError`나 `TypeError`가 난다.
  - 제품 경로: 세 경로 모두 스키마 검사를 먼저 거친다. 생산자 검사, 봉인 적용, 운영 점검이다. 생산자 검사의 `check()`는 두 예외를 모두 이슈로 기록한다.
- **기계 검사 기록(REV-15)**
  - 바뀐 것: 읽기·해석 실패 기록과 설치 계약의 `not_checked`에 `kind_semantic_approval`이 들어간다. 생산자 기록의 `check_subject`에 `revision_targets`가 들어가 생산자 check ID가 바뀐다. 결정 1에 따라 호환은 두지 않았다.
- **상태 값 식별(커널 후속 1)**
  - 바뀐 것: `proposal_digest`, 발견 키, `sealed_input_sha256`, `review_input_basis.sha256`의 값이 바뀐다. `do-math-state/7` 안이고 현재 인스턴스는 없다.
- **시험 대역**
  - `FakeEngine.store`가 None에서 대역 객체로 바뀌었다(REV-24).
  - `'fixture-git'` 표지 5곳이 시험마다 고유한 표지로 바뀌었다. 새 메모 규칙에서 시험 사이로 메모가 새지 않게 하려는 것이다.
  - 새 시험을 둘 더했다. `test_submission_flow.test_issued_input_is_read_once_per_repository_identity_and_returned_as_copies`는 문자열 표지도 한 번만 읽고 사본을 돌려주며 None은 메모하지 않음을 단언한다. `test_redesign_GOVERNANCE.ExecutionLineageTests.test_one_lineage_walk_keeps_each_consumers_judgment`는 공유 순회 위에서 세 소비자의 판정이 그대로임을 단언한다.

## 7. 막힌 지점, 접근을 바꾼 지점, 예상과 달랐던 결과

- **REV-11 모양 검사의 도구**: 처음에는 `review_cycle._check_schema`를 `review_policy`로 옮겨 공유하려 했다. 그런데 같은 규칙("첫 스키마 위반을 `<라벨>/<경로>: <메시지>`로 낸다")의 정본 `state_contract.validate_record`가 이미 있었다. 새 공개 이름을 만드는 대신 그것을 썼다(`_SCOPE_CHECKER`는 모듈 적재 때 한 번 만든다).
- **REV-04의 재심사 결박 확인**: 독립성 재검사를 빼는 선택 인자를 두지 않았다. `validate_review_execution`을 독립성과 `validate_review_binding` 둘로 나눴고, 봉인 재구성은 둘 다, 수락은 결박만 부른다.
- **REV-05의 순환 판정**: `validate_independent_execution`은 계보 순환을 거부하고 리뷰 순회는 순환을 건너뛴다. 이 차이를 보존하려고 공유 순회에 `revisit_error` 인자를 두었다.
- **REV-10의 색인 시점**: 처음에는 `refresh_task_assessments` 첫머리에서 색인을 만들었다. 그러면 판정이 하나도 없는 갱신에서도 색인을 만들어 소유 루프마다 비용이 는다. 그래서 판정이 있는 첫 과제에서 만들도록 바꿨다. 기록 ID 중복의 `ValueError`도 전과 같이 판정을 확인할 때에만 난다.
- **커널 후속 2의 범위**: 파견문은 `expires_at`·`valid_from`·`source_basis` 셋을 들었다. 같은 함수의 `goal_revision`·`policy_revision` 대조도 결정 스키마(`schemas.py:437-444`, 닫힌 `record()`)에 없는 필드라 도달하지 않는다. 같은 이유로 함께 지웠다(`task_scope.py`).
- **편집 도구**: 한국어 주석이 든 셸 heredoc 편집이 `bash -c`의 따옴표 해석 오류로 실패했다. 이후 편집 스크립트를 파일로 써서 실행했다. 그 실패로 바뀐 파일은 없다.
- **남은 관찰(REV 영역, 담당 ID 밖)**: `_retry_review_restoration`은 `_review_cycle`을 부른 뒤 `_prepare_review_context`를 불러 한 번 더 확인한다.

## 8. 다른 그룹 범위에서 발견한 문제

- **RES — `planning.py:639-641`, `:694`**: `task_ready`가 의존 과제마다 `task_scope.assessment_current`를 부른다. 호출자는 이미 `records` 색인을 가지고 있으므로 `records=records`로 넘기면 과제마다 색인을 다시 만들지 않는다(REV-10이 연 인자).
- **RES/STO — `knowledge.py:87`**: `_DECISION_BOOKKEEPING`에 저장 지식 스키마에 없는 필드 `producer_execution_ids`, `required_reviews`가 이름으로 남아 있다. 동작에는 영향이 없다.
- **ENG — `engine.py:3201`**: 실행 시작 때 `_record_review_input(action, execution_id)`는 이제 입장 기록을 먼저 대조하고 `already_admitted`로 돌아온다. 입장 시점의 독립성·입력 기반 재확인은 수락 때(`_checked_review_result`) 하고, 문맥 준비 때에는 `_build_review_context`가 입력 기반을 확인한다. 엔진 쪽 코드는 바꿀 필요가 없다. 흐름만 알린다.

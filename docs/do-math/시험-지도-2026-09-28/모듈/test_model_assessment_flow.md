# test_model_assessment_flow

| 항목 | 값 |
|---|---|
| 조각 | `academic` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_model_assessment_flow.py` (448행) |
| 클래스 / 테스트 | 4 / 22 (시험 없는 러너 대역 `RejectingRunner` 포함) |
| 시험 대상 제품 코드 | `do_math/submission.py`의 `payload_issues`; `do_math/contracts.py`의 `schema_for`; `do_math/planning.py`의 `contract_hash`; `do_math/model_policy.py`의 `MODELS`, 모델 평가 범위 규칙("model assessment coverage", 82행); `do_math/planning_engine.py`의 `_ensure_model_assessments`, `_assessment_input_version`; `do_math/engine.py`의 `run`, `_enqueue`, `_response_schema`, `_resolve_failed_actions`(2898행), `_check_installation`, `process_controls`; `do_math/lifecycle_engine.py`의 `_refresh_readiness`; `do_math/scheduler.py`의 `_select_model`, `_schedule_reconsideration`; 설치된 제출 검사 명령(`submission_contract.command`) |
| 사용하는 픽스처 모듈 | `purpose_fixtures`(`ActivatedPurposeHarness`, `PurposeRunner`, `ASSESSMENT_CONFIG`, `assessment_preparation_instance`, `prepared_assessment_engine`, `solved_instance`, `SOLVED_REQUIREMENT_CRITERIA`); `research_fixtures`(`restore_template`, `local_job_runner`, `producer_result`, `contract_review`, `prepared_rule_conditions`, `seal_response`, `supply_observation_rules`, `candidate`); `runner_fixtures`(`common`, `context_from`, `rating`, `contract_checks`) |
| 격리 표지 | 없음 |
| 시작 상태 | `AssessmentSubmissionTests`는 1단(검증기 직접 호출). `AssessmentFlowTests`는 2단 위의 공유 빌드 `assessment_preparation_instance`(8개), 2단 `make_active`(1개), 3단 위의 `solved_instance`(1개). `RejectedAcademicAssessmentTests`는 그 공유 빌드 위에 쌓은 모듈 빌드 `rejected_assessment_instance` |

## 목적

모듈 docstring(행 1–7)은 "평가 완전성과 준비에서 검토까지의 실제 상태 전이"를 시험한다고 밝힌다. 모델 응답은 명시적 픽스처이고, 엔진, 제출 검사기, 스냅숏, 설치된 생산자 명령이 실제로 돈다. 모델 판단의 질은 시험하지 않는다. 시작 상태는 프로세스당 한 번 만든 템플릿의 복사본이다.

여기서 모델 평가(model assessment)는 과제마다 난도(difficulty)와 중요도(importance)와 사유를 적은 레코드다. 스케줄러가 이것으로 모델 등급을 고른다(`test_session_scheduler` 참조). 이 모듈이 지키는 계약은 다섯이다.

1. 준비 제출은 새 후보와 개정 후보 모두에 정확히 하나씩 평가를 내야 한다.
2. 평가 전용(assessment-only) 준비는 계약을 만들거나 고칠 수 없다.
3. 평가가 빠진 학술 과제는 계약 검토 전에 평가 전용 준비 하나로 모인다.
4. 유보된 평가 요청은 입력이 바뀔 때까지 기다린다.
5. 계약 검토가 평가를 이유로 계약을 반려하면, 옛 평가는 이력에 남고 평가 전용 재요청이 생긴다. 새 평가는 바뀌었든 같든 새 독립 검토를 받는다.

## 모듈 수준 요소

- 행 18: `scripts/`를 `sys.path` 앞에 넣는 공통 머리.
- `candidate(title="one")` (행 32–34): `research_fixtures.candidate(title)`를 지역 import해 돌려준다. 제목 기본값만 다른 얇은 감싸기다. 이 모듈의 제출 시험과 흐름 시험이 쓴다.
- `rejected_assessment_instance(root, shared, *, config, decision)` (행 125–145): `restore_template` 빌드. docstring은 이것을 "독립 계약 검토가 반려한, 평가된 학술 과제 하나"라 부른다. 순서는 다음과 같다.
  1. `assessment_preparation_instance`에서 출발해 `TK-academic-2`를 지운다.
  2. `TK-academic-1`에 `rating()`을 모델 평가로 넣는다.
  3. 큐를 비우고 원본 사본을 뜬 뒤 그 과제의 `task_contract_review`를 넣고 저장한다.
  4. `RejectingRunner(decision)`로 `run(max_steps=1)`. 실제 Job과 제출 경로로 반려 검토를 돈다.

  `{'instance_id', 'task_id', 'original', 'rejected_id'}`를 돌려준다. `rejected_id`는 마지막 검토의 실행 ID다. `research_fixtures` docstring의 "What to use"는 이 빌드를 이 모듈 전용으로 적는다. `RejectedAcademicAssessmentTests.rejected_engine`이 쓴다.
- 행 447–448: 직접 실행하면 `unittest.main()`.

## AssessmentSubmissionTests (행 37–107)

- 기반 클래스: `unittest.TestCase`. 표지·속성이 없다. 1단이다.
- `setUp` (행 38–44): 임시 작업공간을 둔다. 문맥은 `action={'role': 'research_preparation'}`, `budget_unit='concurrent_sessions'`, 빈 과제·지식·종류·원천이다. 기본 출력은 후보 `one`, `two`다.
- 도우미 `issues(extensions)` (행 46–57): 확장 사본을 만든다. 행동에 `assessment_targets`가 없으면 `supply_observation_rules`로 후보의 관찰 규칙 조건을 채워, 규칙 결손이 평가 판정을 가리지 않게 한다. 확장을 파일로 쓰고, 문맥 과제마다 `content_sha256`을 `exact_content_hash`로 채운다. `seal_response` 뒤 `payload_issues(output, schema_for('research_preparation'), context, extensions, workspace)`를 돌려준다.

### `test_missing_candidate_assessments_are_rejected_with_missing_titles` (행 59–62)
- 성질: 평가가 빠진 후보가 있으면 제출이 거부되고, 이슈가 빠진 후보 제목을 댄다.
- 준비: `setUp`. 평가는 `one`만 있다.
- 실행: `issues({'model_assessments': [rating(task_title='one')]})`.
- 단언: 이슈가 있다(메시지 "a candidate without an assessment must not pass"). 직렬화한 이슈에 `'two'`가 있다.
- 대역: 없음.
- 비고: `issues`는 `contract_checks`를 채우지 않는다. 그래서 두 이슈가 함께 나온다. 하나는 평가 범위 이슈 `"model assessment coverage: {\"missing\": [\"two\"], ...}"`다. 다른 하나는 계약 자기 점검 범위 이슈 `contract_check.coverage`(`"... missing [\"one\", \"two\"]"`, `submission.py` 783–789행)다. 두 번째 이슈의 메시지에도 `two`가 들어 있다. 따라서 이슈 유무 단언과 `'two'` 단언은 평가 범위 규칙이 없어도 성립하며, 거부 사유를 평가 누락으로 고정하지 않는다.

### `test_missing_family_cannot_bypass_the_completeness_check` (행 64–65)
- 성질: `model_assessments` 가족 자체를 빼도 완전성 검사를 피할 수 없다.
- 준비: `setUp`.
- 실행: `issues({})`.
- 단언: 이슈가 있다.
- 대역: 없음.
- 비고: 이 확장에는 `contract_checks`도 없다. 그래서 평가 범위 이슈 옆에 계약 자기 점검 범위 이슈 `contract_check.coverage`가 함께 나온다. 이슈 유무만 보는 단언은 거부 사유를 평가 누락으로 고정하지 않는다.

### `test_exact_coverage_is_accepted_and_duplicates_and_foreign_targets_are_rejected` (행 67–73)
- 성질: 후보마다 평가 하나를 정확히 내면 통과한다. 중복 평가나 없는 후보의 평가는 거부된다.
- 준비: `setUp`.
- 실행: `one`, `two` 평가와 `contract_checks(candidates)`로 검사한다. 이어 `('one','one')`, `('one','foreign')`으로 검사한다.
- 단언: 첫째 `[]`, 나머지는 이슈가 있다.
- 대역: 없음.
- 비고: `subTest(titles=...)` 2건. 정확 범위 경우에는 `contract_checks`를 함께 넣고, 거부 경우에는 넣지 않는다. 그래서 거부 두 건의 이슈에는 평가 범위 이슈(`submission.activity-extensions.json.model_assessments`)와 계약 자기 점검 범위 이슈(`contract_check.coverage`, `submission.py` 783–789행)가 함께 나온다. `contract_checks`를 넣으면 평가 범위 이슈만 남는다. 단언은 이슈 유무만 보므로, 평가 규칙이 없어져도 두 거부 건은 계약 자기 점검 이슈만으로 통과한다. 곧 평가 규칙 때문에 거부되었는지를 고정하지 않는다.

### `test_revised_candidate_also_needs_a_new_assessment` (행 75–81)
- 성질: 기존 과제를 개정하는 후보도 새 평가가 필요하다. 옛 판본의 평가가 새 후보를 암묵적으로 채우지 않는다.
- 준비: 과제 `TK-old`(`revision=1`, `waiting`, 평가 있음)를 문맥에 넣는다. 행동에 `revision_targets`(판본과 `contract_hash`)를 두고, 후보를 `revises_task_id='TK-old'`로 바꾼다.
- 실행: `issues({})`.
- 단언: 직렬화한 이슈에 `'model_assessments'`가 있다(메시지는 옛 평가가 새 후보를 채우면 안 된다는 것).
- 대역: 없음.

### `test_empty_preparation_requires_no_candidate_assessments` (행 83–85)
- 성질: 후보 없는 준비는 평가를 요구하지 않는다.
- 준비: 후보를 비운다.
- 실행: `issues({})`.
- 단언: `[]`.
- 대역: 없음.

### `test_assessment_only_payload_cannot_edit_contracts_or_use_other_extensions` (행 87–98)
- 성질: 평가 전용 준비는 배정된 대상의 평가만 낼 수 있다. 후보를 내거나, 다른 확장(과제 처분)을 쓰거나, 배정되지 않은 대상을 평가할 수 없다.
- 준비: 과제 `TK-one`(`waiting`)을 문맥에 넣고, 행동에 `assessment_targets`(판본과 계약 해시)를 둔다. 후보는 비운다.
- 실행: 네 경우를 검사한다. 올바른 평가, 올바른 평가와 후보 하나, 올바른 평가와 `task_dispositions`(withdraw), 다른 대상 `TK-other`의 평가다.
- 단언: 첫째 `[]`, 나머지 셋은 이슈가 있다.
- 대역: 없음.

### `test_assessment_only_deferrals_must_cover_targets_without_overlap` (행 100–107)
- 성질: 평가 전용 준비에서 평가와 평가 유보(`model_assessment_deferrals`)는 배정 대상을 겹침 없이 모두 덮어야 한다.
- 준비: 행동의 `assessment_targets`는 `TK-one`, `TK-two`(빈 기준)다. 후보는 비운다.
- 실행: 세 경우를 검사한다. `TK-one` 평가와 `TK-two` 유보, `TK-one` 평가만, 두 평가와 `TK-two` 유보다.
- 단언: 첫째 `[]`, 둘째 이슈(누락), 셋째 이슈(겹침).
- 대역: 없음.

## RejectingRunner (행 110–122)

- 종류: 시험이 없는 러너 대역 클래스. 기반 클래스 없음.
- docstring: 모든 항목 결정이 `decision`인 독립 계약 검토자.
- `__init__(decision)` (행 113–114): 결정을 저장한다.
- `run(**arguments)` (행 117–122): `local_job_runner`로 감싸 실제 Windows Job을 띄운다. `on_started`를 부른 뒤 프롬프트 문맥을 `context_from`으로 읽는다. `contract_review(context, decision=..., findings=['model_assessment.reason: explain the impact on later verification.'])`를 `producer_result`로 제출한다.
- 사용처: `rejected_assessment_instance` 빌드와 `RejectedAcademicAssessmentTests.rejected_engine`.

## AssessmentFlowTests (행 148–343)

- 기반 클래스: `ActivatedPurposeHarness`. 표지·속성이 없다.
- 도우미 `prepare_engine()` (행 149–150): `prepared_assessment_engine(self)`. `assessment_preparation_instance`(`ASSESSMENT_CONFIG`)의 복사본에 `PurposeRunner`를 단다. 그 빌드의 상태는 다음과 같다(`purpose_fixtures` 573–602행).
  - 2단 합성 활성 상태다.
  - 공개 헌장 결정이 요구 `r`(범위 `solution`, 기준 `Explain the supplied argument`, 평가자 `research_plan`)을 승인했다.
  - `TK-academic-1`, `TK-academic-2`를 `planned` 상태로 직접 넣었다. 요구 해시, 관찰 규칙, 프로필, 권한은 있고 모델 평가는 없다.
  - 각 과제의 계약 검토를 넣은 뒤 `_refresh_readiness()`와 `_save()`를 불렀다. 그래서 게시 상태에서는 검토들이 평가 전용 준비 하나로 대체되어 있다.
- 이 클래스의 `prepare_engine`은 `RejectedAcademicAssessmentTests`가 클래스 속성으로 가져가고, 두 시험 메서드는 그 클래스에서 다시 불린다(아래 참조).

### `test_missing_academic_assessments_are_batched_before_any_contract_review` (행 152–164)
- 성질: 평가가 빠진 학술 과제들은 계약 검토 전에 평가 전용 준비 하나로 묶인다. 그 준비는 high 모델로 돈다. 다시 판정해도 중복되지 않는다.
- 준비: `prepare_engine()`, `_refresh_readiness()`.
- 실행: 큐 조사, `_select_model(action)`, 다시 `_refresh_readiness()`.
- 단언: 큐에 `task_contract_review`가 없다. `assessment_targets`를 가진 행동이 1개이고 역할이 `research_preparation`이며, 대상 집합이 모든 과제다. 선택 모델이 `MODELS['high']`다. 재판정 뒤에도 그 행동이 1개다.
- 대역: 없음(러너 불리지 않음).

### `test_assessment_only_run_preserves_user_contract_and_unblocks_independent_review` (행 166–200)
- 성질: 평가 전용 실행은 모델 평가만 더하고 사용자 계약의 다른 필드를 바꾸지 않는다. 그 뒤 과제마다 독립 계약 검토가 medium 등급으로 열린다. 연구 주기는 오르지 않는다.
- 준비: `prepare_engine()`. 과제 사본을 뜬다. 지역 러너 `Runner`의 동작은 다음과 같다.
  1. 문맥을 기록하고, 배정 대상마다 `rating(task_id=...)`를 확장에 쓴 뒤 `seal_response`한다.
  2. 초안을 `.scratch/submission.json`에 쓴다.
  3. 문맥의 설치된 제출 검사 명령(`submission_contract.command` + `--output <draft>`)을 `subprocess.run(..., timeout=30)`으로 실제 실행한다.
  4. 종료 코드가 0이 아니면 `AssertionError`를 낸다. 0이면 `producer_result`로 제출한다.
- 실행: `run(max_steps=1)`, `_refresh_readiness()`.
- 단언: 러너 호출이 1번이고 문맥에 `assessment_targets`가 있다. 과제마다 `model_assessment == rating()`이고, 나머지 필드가 사본과 같다. 검토 대상 집합이 모든 과제이고 모두 `medium` 등급이다. `cycles == 0`이다(메시지: 평가 완료는 새 준비 주기가 아니다).
- 대역: `Runner`(실제 Windows Job).
- 비고: 설치된 생산자 명령을 실제 자식 프로세스로 돌리는 시험이다. docstring이 "installed producer command"를 검사 대상으로 드는 근거다.

### `test_assessment_request_does_not_absorb_an_ordinary_preparation` (행 202–207)
- 성질: 평가 전용 요청은 일반 연구 준비 요청을 흡수하지 않는다.
- 준비: `prepare_engine()`, `_refresh_readiness()`.
- 실행: `_enqueue('research_preparation', reason='Explore a separate research direction')`.
- 단언: `research_preparation` 행동이 2개다.
- 대역: 없음.

### `test_assessment_only_schema_makes_contract_creation_impossible` (행 209–214)
- 성질: 평가 전용 행동의 응답 스키마는 후보 수를 0으로 막아 계약 생성을 스키마에서 불가능하게 한다.
- 준비: `prepare_engine()`, `_refresh_readiness()`.
- 실행: `_response_schema(action)`.
- 단언: `properties.candidates.maxItems == 0`이다.
- 대역: 없음.

### `test_saved_deferral_with_sources_does_not_retry_without_input_change` (행 216–230)
- 성질: 원천이 있는 상태에서 저장된 평가 유보는 입력 판본이 바뀌지 않으면 다시 시도되지 않는다. 원천 내용이 바뀌면 대기가 풀리고 재요청된다.
- 준비: `prepare_engine()`. 원천 `paper.txt`(sha `a`×64)를 두고 `_refresh_readiness()`. 평가 행동을 큐에서 빼서, `kind='model_assessment_input'`, `input_version=_assessment_input_version()`인 대기로 옮긴다.
- 실행: `_ensure_model_assessments()`, 원천 sha를 `b`×64로 바꾼 뒤 `_ensure_model_assessments()`.
- 단언: 첫 호출 뒤 대기에 남고 평가 행동이 큐에 없다. 원천 변경 뒤 대기에서 빠지고 평가 행동이 큐에 있다.
- 대역: 없음.

### `test_completed_normal_preparation_does_not_resolve_a_failed_assessment_request` (행 232–238)
- 성질: 일반 준비가 끝났다고 해서 실패한 평가 요청이 해소되지는 않는다.
- 준비: `prepare_engine()`, `_refresh_readiness()`. 평가 행동을 `kind='output_validation'` 대기로 둔다.
- 실행: `_resolve_failed_actions({'role': 'research_preparation'}, 'EX-normal')`.
- 단언: 그 행동이 대기에 남는다.
- 대역: 없음.

### `test_deferred_assessment_waits_for_input_and_can_resume_without_stale_question` (행 240–274)
- 성질: 평가를 유보한 실행은 질문을 하나 남기고 기다린다. 판정을 거듭해도 재요청하지 않는다. 사용자 입력이 오면 질문이 사라지고 평가 요청이 다시 선다.
- 준비: `prepare_engine()`. 큐를 정렬해 평가·규칙 대상 행동을 앞에 두고 저장한다. 주석(행 243–244)은 반려 계약 픽스처에는 정당한 계획도 큐에 있을 수 있으므로, 배정된 준비를 먼저 판정하려는 것이라고 적는다. 지역 러너 `DeferringRunner`는 모든 평가 대상에 `model_assessment_deferrals`를, 규칙 대상이 있으면 `observation_rule_deferrals`(`missing_inputs=['user_input']`, `next_owner='user'`)를 쓰고 빈 준비를 제출한다.
- 실행: `run(max_steps=1)`, `_refresh_readiness()` 세 번, 공개 `input` 제어, `process_controls()`, `_refresh_readiness()`.
- 단언: 대기가 1개이고, 그 `question`이 런타임 질문에 있다. 세 번의 재판정 동안 평가 행동이 큐에 없다. 입력 뒤 질문이 사라지고 평가 행동이 큐에 있다.
- 대역: `DeferringRunner`(실제 Windows Job).
- 비고: 주석(행 272)은 마지막 `_refresh_readiness()`를 "다음 스케줄러 통과가 바뀐 입력을 조정한다"는 뜻으로 부른다. `RejectedAcademicAssessmentTests.test_repair_deferral_preserves_obligation_until_resume`이 이 메서드를 반려 상태 엔진으로 다시 부른다.

### `test_late_assessment_cannot_change_a_revised_user_contract` (행 276–314)
- 성질: 평가 실행 도중 사용자가 계약을 개정하면, 늦게 도착한 평가는 개정된 계약에 적용되지 않는다. 결과는 보존되고 평가 요청이 다시 선다.
- 준비: `prepare_engine()`, 큐 정렬, 저장. 두 스레드 이벤트 `revise`와 `revised`를 둔다. `_check_installation`을 감싸서, `revise`가 켜졌는데 아직 개정 전이면 소유자 스레드에서 첫 대상 과제의 `revision`을 올리고 `scope`를 바꿔 저장한 뒤 `revised`를 켠다. 주석(행 280–281)은 엔진 상태가 소유자 스레드에 갇혀 있으므로 계산 스레드는 요청하고 기다리기만 한다고 적는다. 지역 러너 `RevisingRunner`는 평가(와 규칙 조건)를 쓰고 `revise`를 켠 뒤 `revised`를 최대 30초 기다려 제출한다.
- 실행: `patch.object(engine, '_check_installation', side_effect=...)` 아래 `run(max_steps=1)`.
- 단언:
  - 평가 실행의 `outcome == 'execution_incomplete'`다.
  - `result_disposition.kind == 'preserved_after_target_change'`다.
  - 어떤 과제에도 `model_assessment`가 없다.
  - 평가 행동이 큐에 있다.
- 대역: `RevisingRunner`(실제 Windows Job), `_check_installation` 패치(소유자 통과에 끼어드는 지점).
- 비고: `RejectedAcademicAssessmentTests.test_late_repair_cannot_overwrite_a_changed_user_contract`가 이 메서드를 다시 부른다.

### `test_receiver_parks_incomplete_new_candidate_assessments_without_creating_tasks` (행 316–330)
- 성질: 수신기는 평가가 빠진 새 후보를 받으면 과제를 만들지 않고 행동을 대기시킨다(수리 한도 0).
- 준비: 2단 `make_active(**fixture_config(scholarly_enabled=False, operator_enabled=False, max_output_repairs=0))`. 큐를 비우고 준비 하나를 넣는다. 지역 러너 `MissingRunner`는 평가 없이 후보 하나를 제출한다.
- 실행: `run(max_steps=1)`.
- 단언: 과제가 `{}`이다. 대기 사유 중 `'model assessment coverage'`를 담은 것이 있다(제품 `model_policy.py` 82행의 `ValueError("model assessment coverage: ...")`).
- 대역: `MissingRunner`(실제 Windows Job). `producer_result`는 확장을 쓰지 않으므로 평가와 관찰 규칙이 모두 빠진 제출이다.

### `test_real_academic_generation_enters_assessment_preparation_before_contract_review` (행 332–343)
- 성질: 실제 해결 경로로 생성된 학술 과제는 계약 검토 전에 평가 준비의 대상이 된다.
- 준비: 3단 위 빌드 `restore_template(solved_instance, criteria=SOLVED_REQUIREMENT_CRITERIA)`. 요구 `writeup`을 승인한 뒤 `drive_to`로 해결까지 몬 상태다(조건 `mathematically_solved`, 상한 45). 주석(행 334)이 이 사실을 적는다.
- 실행: `process_controls()`, `_refresh_readiness()`.
- 단언: 학술 과제가 있다. 그 ID들이 큐 행동의 `assessment_targets` 합집합에 포함된다. 학술 과제 대상 `task_contract_review`가 큐에 없다.
- 대역: `PurposeRunner`(불리지 않음). 빌드 안에서는 `AcademicRunner`와 `formal_fixture`다.

## RejectedAcademicAssessmentTests (행 346–444)

- 기반 클래스: `ActivatedPurposeHarness`. 표지가 없다.
- 클래스 속성 `prepare_engine = AssessmentFlowTests.prepare_engine` (행 347): 흐름 클래스의 도우미를 빌려 둔다. 두 재사용 시험이 `patch.object(self, 'prepare_engine', return_value=engine)`으로 이것을 반려 상태 엔진으로 바꾼다.
- 도우미 `rejected_engine(decision='revision_required')` (행 349–353): `restore_template(rejected_assessment_instance, config=ASSESSMENT_CONFIG, decision=decision)`의 복사본에 `RejectingRunner(decision)`를 단다. `self.rejected_id`를 두고 `(engine, task_id, original)`을 돌려준다.

### `test_rejected_rating_is_preserved_and_replaced_by_assessment_only_request` (행 355–370)
- 성질: 계약 검토가 평가를 이유로 반려하면, 과제의 현재 평가는 지워지고 이력에 반려 검토 실행과 함께 보존된다. 현재 계약 해시로 평가 전용 재요청이 하나 생긴다. 계약의 다른 필드는 그대로다. 재판정해도 이력이나 검토가 늘지 않는다.
- 준비: `rejected_engine()`.
- 실행: 상태 조사, `_refresh_readiness()` 세 번.
- 단언:
  - 과제에 `model_assessment`가 없다.
  - `model_assessment_history[0].assessment`가 원본 평가이고, `contract_review_execution`이 `rejected_id`다.
  - `research_preparation` 요청이 1개이고, 그 `assessment_targets[tid].contract_sha256 == contract_hash(task)`다.
  - `model_assessment`, `reviews`, `status`, `initial_observation_rules`를 뺀 원본 필드가 모두 같다.
  - 재판정 뒤 이력 길이가 1이고, `task_contract_review`가 없다.
- 대역: 없음(러너 불리지 않음).

### `test_repaired_and_unchanged_ratings_both_receive_fresh_independent_review` (행 372–425)
- 성질: 반려 뒤 다시 낸 평가는 바뀐 것이든(importance high) 같은 것이든 새 독립 계약 검토를 받는다. 새 평가에 맞는 모델 등급이 쓰이고, 승인 뒤 과제는 준비 완료가 된다.
- 준비: `subTest(unchanged=False/True)`마다 `rejected_engine`을 새로 연다. 결정은 `unchanged`면 `'unresolved'`, 아니면 `'revision_required'`다. `_schedule_reconsideration`을 `None`을 돌려주는 autospec으로 막는다. 주석: 일반 사용자 결정 계획은 다른 시험이 본다. 큐를 평가 행동과 계약 검토만 남기고 저장한다. 지역 러너 `Runner`는 두 역할에 답한다.
  - 준비면 입력을 점검한다. 문맥의 대상에 `tid`가 있고, 공급된 과제의 마지막 검토가 `rejected_id`이며, 평가 이력 첫 항목이 `rating()`이어야 한다. 그다음 선택한 평가와 규칙 조건을 쓰고 빈 준비를 제출한다.
  - 준비가 아니면 역할이 `task_contract_review`임을 단언하고 `contract_review(context)`로 승인한다.
- 실행: `run(max_steps=1)`로 준비를 돌린다. 검토 모델을 확인한 뒤 `run(max_steps=1)`로 검토를 돌린다.
- 단언:
  - 준비 뒤 과제에 `model_assessment`가 있다. 실패하면 최근 실행과 대기를 메시지로 싣는다. 그 값은 선택한 평가다.
  - 큐의 검토 선택 등급이 unchanged면 `medium`, 아니면 `high`다.
  - 러너가 받은 역할 순서가 `['research_preparation','task_contract_review']`다.
  - 과제는 `planned`이고, `_task_readiness[tid].state == 'ready'`다.
  - `revision_history[-1].reviews`가 1개이고, `reviews`가 2개이며, 마지막 결정이 `approved`다.
  - `cycles == 0`이다.
  - `model_assessment`, `reviews`, `status`, `revision`을 뺀 원본 필드가 같다.
- 대역: `Runner`(실제 Windows Job), `_schedule_reconsideration` autospec.
- 비고: `subTest` 2건. 러너 안의 `self.assert*`는 러너 스레드에서 실패하면 호출 실패로 드러난다.

### `test_preexisting_rejection_enters_repair_on_refresh` (행 427–434)
- 성질: 이미 저장된 반려 상태를 새 엔진이 열어 준비 여부를 판정하면 평가 수리(평가 전용 요청)로 들어간다.
- 준비: `rejected_engine()` 뒤 같은 저장소·인스턴스로 새 `ResearchEngine`을 연다(재시작 모사).
- 실행: `_refresh_readiness()`.
- 단언: 과제에 `model_assessment`가 없다. 그 과제를 `assessment_targets`에 가진 행동이 큐에 있다. 이력의 `contract_review_execution`이 `rejected_id`다.
- 대역: `RejectingRunner`(불리지 않음).

### `test_repair_deferral_preserves_obligation_until_resume` (행 436–439)
- 성질: 반려 뒤의 평가 수리 요청도 유보되면 질문을 남기고 입력이 올 때까지 의무를 보존한다. 입력이 오면 다시 선다.
- 준비: `rejected_engine()`. `patch.object(self, 'prepare_engine', return_value=engine)`.
- 실행: `AssessmentFlowTests.test_deferred_assessment_waits_for_input_and_can_resume_without_stale_question(self)`를 이 인스턴스로 부른다.
- 단언: 재사용한 메서드의 단언 전부(위 절 참조). 이번 시작 상태는 반려된 단일 과제다.
- 대역: `prepare_engine` 인스턴스 패치, 재사용 메서드의 `DeferringRunner`.

### `test_late_repair_cannot_overwrite_a_changed_user_contract` (행 441–444)
- 성질: 반려 뒤의 평가 수리도 도중에 사용자 계약이 개정되면 적용되지 않고 보존된다.
- 준비: `rejected_engine()`, `prepare_engine` 인스턴스 패치.
- 실행: `AssessmentFlowTests.test_late_assessment_cannot_change_a_revised_user_contract(self)`를 이 인스턴스로 부른다.
- 단언: 재사용한 메서드의 단언 전부.
- 대역: `prepare_engine` 인스턴스 패치, 재사용 메서드의 `RevisingRunner`와 `_check_installation` 패치.
- 비고: 시험-지침 4절 규칙 1("같은 성질이면 단언을 더한다")과 규칙 10(도우미를 다른 모듈에서 import하지 않음)은 모듈 사이의 일이다. 이 두 시험은 같은 모듈 안에서 다른 클래스의 시험 메서드를 직접 재사용한다.

## 관계

- 같은 제품 기능의 다른 층:
  - 모델 평가가 선택 모델로 흘러가는 경로는 `test_session_scheduler`의 `test_model_assessments_flow_from_preparation_through_review_and_planning_to_execution`과 `test_selected_task_without_a_plan_assessment_...`가 본다.
  - 관찰 규칙 배정은 `test_academic_preparation`이 본다.
  - 학술 과제 생성과 완료는 `test_academic_engine`이 본다.
  - 준비 제출 검사는 `test_submission_checks`(`foundation` 조각)와 `review` 조각의 `test_submission_boundaries`에 인접한다.
- 픽스처 의존:
  - `purpose_fixtures.assessment_preparation_instance`/`prepared_assessment_engine`/`ASSESSMENT_CONFIG`를 쓴다. `ASSESSMENT_CONFIG`와 빌드 자체는 이 모듈만 쓰고, `prepared_assessment_engine`은 `test_academic_preparation`과 공유한다(`consumers.json`).
  - `solved_instance`, `SOLVED_REQUIREMENT_CRITERIA`는 `test_academic_engine`과 공유한다.
  - `runner_fixtures.rating`, `research_fixtures.contract_review`(결정·발견 인자), `prepared_rule_conditions`, `supply_observation_rules`에도 기댄다.
- 이 모듈에만 있는 도우미: `candidate`, `rejected_assessment_instance`, `RejectingRunner`, `AssessmentSubmissionTests.issues`, `AssessmentFlowTests.prepare_engine`, `RejectedAcademicAssessmentTests.rejected_engine`. 지역 러너 `Runner`(두 번), `DeferringRunner`, `RevisingRunner`, `MissingRunner`도 이 모듈에만 있다.
- 겹치거나 보완하는 시험:
  - 유보와 늦은 적용 두 규칙을 첫 평가 요청(`AssessmentFlowTests`)과 반려 뒤 수리 요청(`RejectedAcademicAssessmentTests`)에서 같은 메서드로 두 번 검사한다.
  - 제출 층(`AssessmentSubmissionTests`)과 엔진 층(`AssessmentFlowTests`)이 같은 평가 범위 규칙을 두 층에서 본다. 엔진 층의 `test_receiver_parks_...`가 제출 층의 누락 거부와 짝이다.

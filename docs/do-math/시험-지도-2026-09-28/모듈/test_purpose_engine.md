# test_purpose_engine

| 항목 | 값 |
|---|---|
| 조각 | `research` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_purpose_engine.py` (377행) |
| 클래스 / 테스트 | 3 / 19 |
| 시험 대상 제품 코드 | `do_math/engine.py`의 `ResearchEngine.run`, `process_controls`, `status`, `_governance`; `do_math/governance_engine.py`의 `_governance_schema`; 공개 `control`(`decision`, `input`, `knowledge`, `trust`, `pause`); `do_math/knowledge.py`의 `plan_impact`, `revision_roots`; `do_math/knowledge_records.py`의 `usable_links`; `do_math/context_store.py`의 `prepare_role_input`; `do_math/model_policy.py`의 `validate_assessments`; `do_math/submission.py`의 `extension_schema`; `do_math/execution_profiles.py`의 `build_profiles`, `resolve_profile`; `do_math/repository.py`의 `ResearchRepository.load` |
| 사용하는 픽스처 모듈 | `purpose_fixtures`(`PurposeRunner`, `PurposeHarness`, `ActivatedPurposeHarness`, `candidate`, `parse_context`, `EXPLANATION`, `NEW_GOAL`, `solved_instance`); `research_fixtures`(`bare_engine`, `planning_model_assessments`, `charter_change`, `policy_change`, `disposition`, `seal_response`, `bind_candidates`, `restore_template`, `send_control`, `trust_fixture`); `record_fixtures`(`surface_state`); `state_fixtures`(`active_instance`, `ACTIVE_LEAN_COMMAND`) |
| 격리 표지 | 없음 |
| 시작 상태 | `PurposeFixtureContractTests`는 1단 6개와 2단 1개(`test_restored_template_...`). `PurposeEngineTests`는 3단 10개(`make` → `activated_instance`)와 2단 1개(`make_active`). `SolvedPurposeTests`는 3단 위의 `solved_instance` 빌드 |

## 목적

모듈 docstring(행 1–5)은 이 모듈을 "명시적으로 스크립트된 의미를 가진 실제 엔진의 목적 수준 시험"이라 부른다. 러너와 컴파일러는 대역이고, 목적 시험마다 스키마·CAS·불변 산출물을 설치한 임시 실제 Git 저장소를 쓴다. 어느 범주도 실제 모델이나 실제 Lean의 정확도를 입증하지 않는다고 못박는다.

이 모듈의 중심은 `purpose_fixtures`의 목적 시나리오다. `PurposeRunner`(`purpose_fixtures` 112–343행)는 역할마다 실제 입력을 읽고 응답한다. 기본 시나리오 `direct`의 흐름은 다음과 같다. 준비가 형식 과제 `A`(`SOURCE`)를 제안한다. 계약 검토는 승인하고, 작업은 `theorem()`을 돌려준다. 동일성 검토는 일치로 끝난다. 인증된 결과가 생기면 목표 감사가 만족을 낸다. `scenario` 인자로 변형을 고른다. `dependency`는 `B`를 `A`보다 먼저 푼다. `dispute`는 한 번 철회되는 이의를 낸다. `currentness`는 결과를 쓰는 하류 과제를 둔다. `catalog`는 긴 보고서를 낸다. `observation` 인자는 첫 작업 호출의 실시간 관찰을 몬다(`continue`, `stop`, `external_pause`).

목적 시험은 `PurposeHarness.drive(engine, predicate=None, limit=45)`로 엔진을 한 단계씩 몬다(`purpose_fixtures` 359–368행). 조건 함수를 주지 않으면 `goal_status == 'mathematically_solved'`까지 몬다. 조건이 참이 되기 전에 런타임이 `paused`, `closed`, `waiting`이 되면 상태·질문·큐·실행 요약과 함께 실패한다. 상한 안에 끝나지 않아도 실패한다. 이 모듈의 첫 클래스는 그 시나리오 픽스처 자체의 계약을 제품 스키마와 제품 함수에 대조한다. 둘째 클래스는 시나리오로 공개 엔진을 몬다. 셋째 클래스는 공개 초기화·활성화부터 해결까지 몬 상태를 읽는다.

## 모듈 수준 요소

- 행 18: `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리.
- 행 376–377: 직접 실행하면 `unittest.main(verbosity=2)`.

모듈 함수와 상수는 없다.

## PurposeFixtureContractTests (행 26–117)

- 기반 클래스: `unittest.TestCase`. 표지·속성·도우미·훅이 없다.
- 목적: 목적 시나리오 픽스처가 제품의 계약을 거짓으로 만족시키지 않는지 검사한다. 픽스처의 응답을 제품 스키마와 제품 검증기에 직접 넣는다.

### `test_goal_fixture_declares_the_empty_additional_audit_population` (행 27–37)
- 성질: `PurposeRunner`의 목표 감사 응답은 추가 감사 모집단이 비었음을 명시하고, 제품의 거버넌스 응답 스키마를 통과한다.
- 준비: 1단. `bare_engine({'governance': {}})`. 문맥은 `additional_audit_input=[]`이고, 적격 지식 `KN-goal` 하나가 `links`와 `decision='match'` 평가를 가진다.
- 실행: `PurposeRunner().answer('goal_audit', context, None)`, `seal_response`(임시 폴더), `jsonschema.validate(output, engine._governance_schema(action, schema_for('goal_audit')))`.
- 단언: 스키마 검증이 예외 없이 통과한다. `output['additional_audits'] == []`다.
- 대역: 없음(픽스처 자체가 검사 대상이다).

### `test_candidate_fixture_chooses_declared_current_profile_editions` (행 39–50)
- 성질: `bind_candidates`는 문맥에 이전 판본과 현재 판본의 프로필이 섞여 있어도, 현재 `role_profile_refs`가 선언한 `research_work` 판본만 후보에 묶는다.
- 준비: 1단. `build_profiles(DEFAULT_CONFIG)`(이전)와, `tool_review_window_seconds`·`self_check_response_window_seconds`를 바꾼 `build_profiles`(현재)의 프로필을 합친 문맥.
- 실행: `candidate(...)` 하나에 `bind_candidates(output, context)`.
- 단언: 후보의 `profile_refs`가 현재 `role_profile_refs['research_work']`와 같다.
- 대역: 없음.

### `test_fixture_reads_returned_report_from_the_actual_supplied_task_source` (행 52–68)
- 성질: 제품이 계획 입력을 맞출 때 과제의 `results`를 인라인 문맥에서 빼고 원천 파일로 옮긴다. 픽스처의 `parse_context`는 그 원천 파일에서 원래 결과를 그대로 복원해 읽는다.
- 준비: 1단 순수 함수 호출. `record_fixtures.surface_state()`에 `waiting` 상태 과제 `TK-returned`와 보고서 결과 하나를 넣는다.
- 실행: 임시 작업공간에 `context_store.prepare_role_input(..., role='research_plan', ...)`, 이어서 `parse_context(fitted['prompt'], workspace)`.
- 단언: 맞춘 문맥의 첫 과제에 `results` 키가 없다. 픽스처가 읽은 문맥의 `results`는 원 런타임의 결과와 같다.
- 대역: 없음.

### `test_completed_comparison_population_can_request_audit_from_the_supplied_usable_goal_result` (행 70–80)
- 성질: 계획 픽스처는 공급된 지식 목록에 쓸 수 있는(usable) 목표 결과가 있을 때만 목표 감사를 요청한다. 준비 픽스처는 목표 결과가 이미 있으면 쓸 수 있든 없든 새 후보를 내지 않는다.
- 준비: 1단. 과제가 없고 `Natural zero identity` 지식 하나만 있는 문맥.
- 실행: `PurposeRunner().answer('research_plan', ...)`를 `usable_as_k` 참·거짓으로 한 번씩 부르고, `answer('research_preparation', ...)`을 두 값으로 부른다.
- 단언: 계획의 `goal_audit`가 참이면 참, 거짓이면 거짓이다. 준비의 `candidates`는 두 경우 모두 `[]`이다.
- 대역: 없음.

### `test_plan_fixture_assesses_exactly_the_selected_task_population` (행 82–96)
- 성질: `planning_model_assessments`는 선택된(selected) 과제만 평가하고, 공급된 모델 평가의 난도·중요도를 옮긴다. 결과는 제품 확장 스키마와 제품 평가 검증을 통과한다.
- 준비: 1단. 선택 `TK-selected`(high/medium)와 비선택 `TK-deferred`(`kind='not_selected'`).
- 실행: `planning_model_assessments`, `jsonschema.validate(extensions, submission.extension_schema(action))`, `model_policy.validate_assessments(action, output, extensions, tasks)`.
- 단언: 검증된 평가의 키 집합이 `{'TK-selected'}`이고, 난도 `'high'`, 중요도 `'medium'`이다.
- 대역: 없음.

### `test_restored_template_is_an_independent_copy_of_the_published_state` (행 98–112)
- 성질: `restore_template`는 게시된 상태를 바이트 그대로 복사하고, 부를 때마다 이전 복사본을 대체한다. 복사본에서 한 변경은 다음 복사본에 남지 않는다. 제어 수신함도 비어 있다.
- 준비: 2단. `restore_template(active_instance, config=PurposeHarness.fixture_config())`.
- 실행: `ResearchRepository(...).load()`로 머리·인스턴스·런타임을 읽는다. 공개 `control(..., 'pause')`를 보내고 새 `ResearchEngine(...).process_controls()`로 적용한다. 같은 인자로 `restore_template`를 다시 부른다.
- 단언: 인스턴스의 `workspace`가 `root / 'work-0'`이다. 일시 정지 뒤 머리가 달라진다. 재호출 결과가 `(root, instance_id)`로 같다. 다시 읽은 `(head, instance, runtime)`이 처음과 같다. `work-0/control/<id>/*.json`이 없다.
- 대역: `PurposeRunner`(불리지 않음).
- 비고: 검사 대상은 제품이 아니라 `research_fixtures.restore_template`의 복사 규칙이다. `research_fixtures` docstring의 "Rules of a copy"가 말하는 성질이다.

### `test_plan_fixture_does_not_invent_a_missing_selected_task_assessment` (행 114–117)
- 성질: 계획 픽스처는 선택된 과제에 공급된 모델 평가가 없으면 평가를 지어내지 않고 실패한다.
- 준비: 1단. 모델 평가 없는 과제 `TK-missing`을 선택한 출력.
- 실행: `planning_model_assessments(output, {'tasks': [...]})`.
- 단언: `AssertionError`가 메시지 조각 `'without its supplied model assessment'`와 함께 난다.
- 대역: 없음.

## PurposeEngineTests (행 120–346)

- 기반 클래스: `ActivatedPurposeHarness`. 이 하네스의 `setUp`이 `install_adapter_fixture`를 건다. `make(scenario, observation=..., **config)`는 `activated_instance`(`goal=GOAL`, `fixture_config(**config)`, `external_policy='disabled'`)의 복사본에 `PurposeRunner(scenario, observation=...)`를 단 엔진을 준다. `observation`이 `continue`나 `stop`이면 `tool_review_window_seconds` 기본값을 1로 둔다. `fixture_config`의 기본값은 다음과 같다: `reviewers=2`, `goal_auditors=2`, `review_rounds=2`, `plan_settle_seconds=1`, `max_input_bytes=2_000_000`, `lean_command=['test-double']`, `tool_review_window_seconds=60`, `self_check_response_window_seconds=5`, `scholarly_enabled=False`, `operator_enabled=False`.
- 클래스 표지·속성·도우미: 없음.
- 공통 대역: `PurposeRunner`가 역할 응답을 낸다. 호출마다 `local_job_runner`가 실제 Windows Job 자식(`python -c "import time; time.sleep(600)"`)을 띄우고 호출이 끝나면 종료한다. 제출은 실제 제어 전송(`submit_intent`)을 거친다. 컴파일러는 `formal_fixture`(`SOURCE`/`add_zero_fixture`만 허용), 어댑터는 `FixtureAdapter`다. 저장은 실제 Git 저장소이고 git 자식 프로세스를 쓴다.

### `test_task_dependency_extension_blocks_A_until_B_completed_then_solves_goal` (행 121–130)
- 성질: 준비 확장이 선언한 과제 의존은 `A`의 작업을 `B`가 완료로 평가될 때까지 막는다. 그 뒤 목표가 해결된다.
- 준비: 3단, 시나리오 `dependency`. 준비 픽스처는 `activity-extensions.json`에 `A`의 `occurrence_condition`(B 완료)과 `dependencies=['B']`를 쓰고, 후보 `A`(형식)와 `B`(비형식)를 낸다.
- 실행: `self.drive(engine)`. 조건 함수는 기본(수학적 해결), 상한은 45다. 목표 감사까지 몬다.
- 단언:
  - `runner.work_order == ['B', 'A']`다. 픽스처도 `A` 작업 시작 때 `B`가 완료가 아니면 `AssertionError`를 낸다(`purpose_fixtures` 276–278행).
  - `A`의 `dependencies`가 `[B의 id]`이다.
  - `A`의 `occurrence_condition`을 직렬화한 문자열에 `"task_id": "B"`가 없다. 제목이 ID로 바뀌었다.
  - 모든 과제가 완료다.
  - `status()['knowledge']['K'] == 1`이다.
  - `formal_check` 역할 실행이 있다.
- 대역: 공통 대역.

### `test_objection_judgment_answer_and_final_approval_use_real_engine` (행 132–152)
- 성질: 동일성 검토에서 이의 제기, 쟁점 정리, 답변(철회), 판정이 실제 엔진의 단계 순서로 진행된다. 최종 일치 평가만 목표 감사에 전달된다.
- 준비: 3단, 시나리오 `dispute`, `review_rounds=3`. 초기 슬롯 `initial-0`이 영역 불일치 이의를 내고, 답변 단계에서 철회한다.
- 실행: `self.drive(engine)`. 기본 조건(해결), 상한 45로 목표 감사까지 몬다. 주석(행 137–138)은 목표 감사 픽스처가 "철회된 이의 뒤에 최종 일치 평가만 받는지" 검사하므로 끝까지 몬다고 적는다(`purpose_fixtures` 316–319행의 점검).
- 단언:
  - 동일성 검토 호출의 단계 목록이 정확히 `['scope','initial','initial','organize','judge','judge','judge','answer','judge','judge','judge']`다.
  - 8번째(색인 7) 호출의 슬롯이 `'initial-0'`이다.
  - 3번째 호출이 받은 `completed_results` 키가 `{'scope:1:scope'}`다.
  - 6번째 호출의 `completed_results`에 `judge` 단계가 없다.
  - 결과 지식의 `usable_links`가 비어 있지 않다. 그 평가의 `decision == 'match'`이고 `execution_ids`는 3개다.
  - 검토 주기의 `(decision, round) == ('match', 2)`다.
- 대역: 공통 대역.
- 비고: 주석(행 134–135)은 라운드 상한을 3으로 두었으므로 2라운드에서 닫힌 주기는 상한이 아니라 확인된 철회로 닫혔다고 설명한다.

### `test_policy_control_invalidates_old_contract_approval_before_work` (행 154–174)
- 성질: 공개 정책 결정이 정책 개정을 올리면 옛 정책 아래의 계약 승인은 무효가 되어 과제가 준비 완료에서 빠진다. 작업은 새 정책 개정으로 다시 승인된 뒤, 새 개정을 거버넌스 입력으로 받는다.
- 준비: 3단, `direct`.
- 실행: 첫 `drive`는 "`reviews`가 있는 과제가 생긴다"까지 몬다(상한 45). 공개 `control(..., 'decision', config={'change': policy_change(...)})`와 `process_controls()`를 부른다. 둘째 `drive`는 "`research_work` 호출의 `governance.policy_revision`이 새 개정이다"까지 몬다.
- 단언:
  - 첫 검토의 `policy_revision`이 이전 개정과 같다.
  - 제어 뒤 개정이 달라지고, `_task_readiness[task].state == 'not_ready'`다.
  - 과제 `reviews` 중 새 개정이면서 `approved`인 것이 있다.
  - 새 개정의 작업 호출 문맥이 새 개정을 담는다. 이 단언은 조건 함수와 같은 내용을 한 번 더 본다.
  - `research_work` 실행 중 `output_accepted`인 것이 있다.
- 대역: 공통 대역.

### `test_user_input_is_independently_checked_without_becoming_goal_authority` (행 176–193)
- 성질: 사용자 입력은 해석 실행과 다른 실행이 독립적으로 검사한다. 모델이 검사로 승인해도 입력이 목표 권한이 되지는 않는다. 별도의 정확한 공개 결정만 새 목표를 채택하고, 이전 헌장(charter)을 대체된 것으로 보존한다.
- 준비: 3단, `direct`. 헌장 사본을 떠 둔다.
- 실행: 공개 `control(..., 'input', text=NEW_GOAL)`. `drive`는 "`source.text == NEW_GOAL`이고 `check`가 있는 해석 묶음이 생긴다"까지 몬다. 이어 `send_control(engine, 'decision', config={'change': charter_change(goal=NEW_GOAL, ...)})`을 보낸다.
- 단언:
  - 묶음의 `execution_id`와 `check.execution_id`가 다르다.
  - `check.decision == 'approved'`다.
  - 결정 전에는 헌장이 그대로다.
  - `waiting_actions` 중 `kind == 'import_application_authority'`인 것이 있다.
  - 결정 뒤 `_governance()['goal'] == NEW_GOAL`이다.
  - 이전 헌장 레코드의 `status == 'superseded'`다.
- 대역: 공통 대역. `PurposeRunner`의 해석 응답은 입력이 `NEW_GOAL`이면 헌장 개정 제안 레코드 `CH-proposed-new-goal`을 가져오기 단위에 싣는다(`purpose_fixtures` 324–332행).

### `test_knowledge_currentness_loss_and_revision_recover_through_fresh_review` (행 195–241)
- 성질: 인증된 지식을 공개 제어로 무효화하면 목표가 미해결이 되고, 그 지식을 쓴 하류 완료 과제는 평가만 비현행이 된다. 결과는 보존된다. 지식을 개정하면 새 검토 주기로 대체 지식이 쓸 수 있게 되어 목표가 다시 해결된다. 이때 하류 과제는 다시 작업하지 않고 이전 동일성 평가는 바뀌지 않는다.
- 준비: 3단, 시나리오 `currentness`. 해결 뒤 계획이 하류 과제를 요청하고(`purpose_fixtures` 266–268행), 준비가 인증 결과를 참조하는 비형식 과제 `Dependent`를 낸다.
- 실행: 첫 `drive`는 "`Dependent` 과제가 완료다"까지 몬다(상한 45). `send_control(knowledge, invalidate, declared_impact=plan_impact(...)['computed_impact'])`를 보낸다. 이어 `send_control(knowledge, revise, changes={'explanation': ...}, declared_impact=plan_impact(revision_roots(...)))`를 보낸다. 둘째 `drive`는 기본 조건(해결)에 상한 55다.
- 단언:
  - 무효화 직후 `goal_status == 'unsolved'`다.
  - 하류 과제는 `completed`를 유지하고 `assessment.current`가 거짓이다. `use_history` 사유에 `'disputed'`가 있다.
  - 현행 목표 판정이 없다.
  - 개정 뒤 대체 지식의 `usable_links`가 비어 있지 않다.
  - 새 `review_cycle_id`는 이전과 다르고, 이전 주기는 런타임에 남는다.
  - 원 지식의 `lifecycle == 'superseded'`다.
  - 이전의 모든 동일성 평가가 그대로다.
  - 하류 과제는 완료이고 평가가 비현행이며, 결과가 무효화 전 사본과 같다.
  - `work_order`의 `'Dependent'` 횟수가 늘지 않는다.
  - 마지막 목표 판정은 `current`가 참이거나 그 키가 없다(`get('current', True)`).
- 대역: 공통 대역.
- 비고: 목표 판정이 단언 대상이므로 둘째 구동은 목표 감사까지 몬다. 상한 55는 이 시험에만 쓴다.

### `test_live_continue_preserves_checkpoint_and_reserves_no_work_slot` (행 243–263)
- 성질: 실시간 관찰 중 운영 검토가 `continue` 처분을 내면 작업자의 체크포인트가 보존된다. 실시간 운영 검토는 모델 작업 슬롯을 예약하지 않는다.
- 준비: 3단, `observation='continue'`(`tool_review_window_seconds=1`). 첫 작업 호출에서 픽스처가 다음 순서로 움직인다(`purpose_fixtures` 135–174행).
  1. `argument.txt`와 `checkpoint.json`을 쓴다.
  2. 관찰 배치를 보내고 도구 시작 사건을 보낸다.
  3. 1.05초 기다린 뒤 빈 틱을 보낸다.
  4. 운영 검토의 `continue` 피드백 파일이 생길 때까지 0.5초마다 틱을 보내며 폴링한다(상한 120초).
- 실행: `drive`는 "`continue` 처분이 있고 그 대상 실행이 `runtime['checkpoints']`에 있다"까지 몬다(상한 45). 주석(행 246)은 두 레코드 묶음이 첫 레코드와 함께 처음 나타난다고 설명한다.
- 단언:
  - `live` 표지 운영 검토 실행이 정확히 1개다.
  - 부모 작업자 프로필의 `ai.capacity_refs`는 비어 있지 않고, 실시간 검토 프로필의 것은 `[]`이다.
  - 검토 `outcome == 'output_accepted'`다.
  - 검토 실행을 소유자로 하는 `unit == 'execution'` 예약이 없다.
  - 부모 체크포인트의 `kind == 'worker_checkpoint'`다.
  - 부모를 대상으로 한 `continue` 처분이 있다.
- 대역: 공통 대역. 관찰은 `observation_batch`로 실제 배치 형식을 만든다.
- 비고: 고정 대기 `time.sleep(1.05)`와 0.05초 폴링이 픽스처 안에 있다. 시험-지침 4절 규칙 5와 달리 고정 대기를 쓰는 지점이다. 관찰 창 1초를 넘기기 위한 것으로 보이지만 원문 주석은 없다.

### `test_operating_review_runs_even_when_the_worker_used_the_last_work_call` (행 265–277)
- 성질: 이름은 작업자가 마지막 작업 호출을 써도 운영 검토가 돈다는 성질을 말한다. 주석이 말하는 근거는 운영 검토가 작업 슬롯을 쥐지 않는다는 것이다.
- 준비: 3단, `observation='continue'`.
- 실행: `drive`는 "`research_work` 실행 중 `output_accepted`가 있다"까지 몬다(상한 45).
- 단언: `WORK_ROLES` 역할 실행이 2개, 운영 검토 실행이 1개다. 운영 검토의 `outcome == 'output_accepted'`이고, 프로필의 `capacity_refs`가 `[]`이다.
- 대역: 공통 대역.
- 비고: 작업 슬롯이 실제로 다 찬 상태는 만들지 않는다. `fixture_config`는 `session_limits`를 바꾸지 않으므로 기본 한도(모델마다 3)가 그대로다. 두 작업 역할 실행은 `task_contract_review`와 `research_work`다(`WORK_ROLES`). 그래서 이름의 "마지막 작업 호출" 조건은 코드로 재현되지 않는다. 슬롯 비의존성은 프로필의 `capacity_refs`가 비었다는 단언으로만 확인된다. 이 단언은 앞 시험의 것과 겹친다.

### `test_large_history_uses_exact_context_source_files_without_losing_work` (행 279–299)
- 성질: 18만 바이트를 넘는 보고서를 가진 과제가 계획 입력에 들어가면, 그 상세는 해시와 크기가 일치하는 원천 파일(`input/details/tasks/`)로 공급된다. 작업은 잃지 않는다.
- 준비: 3단, 시나리오 `catalog`. 작업 보고서에 문장 하나를 6000번 덧붙인다.
- 실행: `drive`는 "`research_plan` 호출 문맥의 과제 중 첫 결과 보고서가 180000자를 넘는 것이 있다"까지 몬다(상한 45).
- 단언:
  - 수용된 계획 실행의 `input_manifest.detail_sources` 중 경로가 `input/details/tasks/`로 시작하고 180000바이트를 넘는 항목이 있다.
  - 각 항목을 저장소에서 읽으면 sha256과 길이가 일치한다.
  - `work_order == ['A']`다.
  - 계획 문맥 중 큰 보고서를 담은 것이 있다. 조건 함수와 같은 내용이다.
- 대역: 공통 대역. 문맥은 `parse_context`가 원천 파일에서 복원한다.
- 비고: 주석(행 284–285)은 비교 모집단은 그대로 두고, 큰 레코드 상세는 선택적 전체 필드 축약과 무관하게 정확한 원천이 된다고 적는다.

### `test_live_retry_stops_the_attempt_and_keeps_partial_artifacts_without_publishing_a_theorem` (행 301–309)
- 성질: 실시간 운영 검토가 `retry`를 처분하면 진행 중인 시도를 멈추고, 부분 산출물을 보존한 채 이어 가기 행동을 넣는다. 정리는 게시하지 않는다.
- 준비: 3단, `observation='stop'`. 픽스처의 운영 검토가 `retry`를 내고, 작업 픽스처는 `await_stop`과 `stop-request.json`을 확인한 뒤 `status='stopped'`로 돌아간다.
- 실행: `drive`는 "`stop_requested == 'operational_retry'`이면서 `ended`인 실행이 있다"까지 몬다(상한 45).
- 단언:
  - 작업자의 `outcome == 'execution_incomplete'`, `stop_requested == 'operational_retry'`다.
  - 큐에 `continuation_of == 작업자 id`인 행동이 있다.
  - `output_files`에 `argument.txt`가 있다.
  - `instance['knowledge']`가 비어 있다.
- 대역: 공통 대역.

### `test_external_user_pause_is_processed_during_running_work` (행 311–319)
- 성질: 작업이 도는 동안 도착한 외부 사용자 일시 정지를 처리한다. 작업은 취소되고 체크포인트는 보존되며 지식은 게시되지 않는다.
- 준비: 3단, `observation='external_pause'`. 픽스처는 첫 관찰 배치 뒤 `pause_sender`(하네스 `_engine`이 공개 `control(..., 'pause')`로 묶음)를 부른다. 이어 정지 판정을 기다려 `stopped`로 돌아간다.
- 실행: `drive`는 "`runtime.status == 'paused'`"까지 몬다(상한 45). 조건 함수를 먼저 보므로 `paused`가 실패로 처리되지 않는다.
- 단언:
  - 상태가 `paused`다.
  - 작업자 `outcome == 'cancelled'`, 체크포인트 종류는 `worker_checkpoint`다.
  - 이력에 `kind == 'user_control'`이면서 `request.action == 'pause'`인 행이 있다.
  - 지식이 비어 있다.
- 대역: 공통 대역.

### `test_environment_revalidation_does_not_clear_independent_meaning_dispute` (행 321–346)
- 성질: 신뢰 환경을 무효화했다가 새 환경으로 재검증해도, 따로 제기된 의미 분쟁은 풀리지 않는다. 지식 무효화 뒤 사라진 사용 가능 연결은 되살아나지 않고, 동일성 평가는 그대로다.
- 준비: 2단. `make_active(**fixture_config(plan_settle_seconds=1, lean_command=list(ACTIVE_LEAN_COMMAND)))`. 주석(행 325)은 이 규칙이 초기화 뒤에 시작되므로 공개 활성화는 따로 시험한다고 적는다.
- 실행:
  1. 첫 `drive`는 "`usable_links`가 있는 지식이 생긴다"까지 몬다(상한 45).
  2. 공개 `trust` 무효화 제어를 보내고 `process_controls()`로 적용한다.
  3. `send_control(knowledge, invalidate)`를 보낸다.
  4. `send_control(trust, trust_fixture(root/'replacement-environment', lean_command))`로 새 환경을 등록한다.
  5. `send_control(trust, transition)`을 보낸다.
  6. 둘째 `drive`는 "`active_trust_environment`가 새 환경"까지 몬다.
- 단언: 지식 무효화 직후 `usable_links == []`이다. 전환 뒤에도 동일성 평가가 무효화 직전 사본과 같고, `usable_links == []`, `goal_status == 'unsolved'`다.
- 대역: 공통 대역. `trust_fixture`가 합성 설치와 공유 도구 모음 기록을 만든다.
- 비고: 이 클래스에서 2단 `make_active`를 쓰는 유일한 시험이다.

## SolvedPurposeTests (행 349–373)

- 기반 클래스: `unittest.TestCase`(하네스가 아니다).
- docstring: 공개 초기화·활성화를 목표까지 몬 상태를 프로세스당 한 번 만들고, 그 상태와 빌드가 돌려준 사실을 읽는다고 밝힌다. `research_fixtures` docstring은 이 빌드를 "공개 경로를 유지해야 하는 전용 종단 연결" 중 하나로 든다.
- 클래스 표지·속성·도우미·훅: 없음.

### `test_public_activation_reaches_the_solution_with_archived_role_inputs` (행 357–373)
- 성질: 공개 초기화부터 해결까지 모든 실행이 수용되거나 검증되어 끝난다. 역할 입력을 가진 실행은 보관된 프롬프트와 그 다이제스트를 입력 목록(manifest)에 이름으로 싣는다.
- 준비: 3단 위의 빌드 `restore_template(solved_instance, criteria=None)`. 빌드는 `activated_instance`에서 `AcademicRunner`와 `formal_fixture`로 엔진을 만든다. `do_math.initialization.adapter_for`를 `FixtureAdapter`로 패치한 채 `drive_to`를 부른다. 조건은 `goal_status == 'mathematically_solved'`, 상한은 45다. 반환은 `{'instance_id', 'head', 'work_order'}`다.
- 실행: `ResearchRepository(...).load()`와 `store.read`.
- 단언:
  - `goal_status == 'mathematically_solved'`다.
  - 게시된 머리가 빌드가 돌려준 `head`와 같다.
  - 모든 실행의 `outcome`이 `output_accepted` 또는 `verified`다.
  - `input_bundle`이 있는 실행마다 `input_manifest.prompt.artifact_ref == runtime/artifacts/<bundle>/input.txt`이고, 그 바이트의 sha256이 기록과 같다.
  - `work_order == ['A']`다.
- 대역: 빌드 안의 `AcademicRunner`(학술 과제가 없으면 `PurposeRunner`와 같게 답함), `formal_fixture`, `FixtureAdapter`. 시험 본문은 대역을 쓰지 않는다.
- 비고: 빌드는 같은 프로세스에서 이 템플릿을 처음 요구하는 시험 안에서 돈다. `test_currentness`, `test_academic_engine`, `test_model_assessment_flow`도 `solved_instance` 템플릿을 쓴다. `test_currentness`는 이 시험과 같은 `criteria=None` 판을 쓴다. `test_academic_engine`은 `criteria=None` 판과 `SOLVED_REQUIREMENT_CRITERIA` 판을 모두 쓰고, `test_model_assessment_flow`는 `SOLVED_REQUIREMENT_CRITERIA` 판만 쓴다.

## 관계

- 같은 제품 기능의 다른 층:
  - 동일성 검토의 단계 계약은 `review` 조각의 `test_review_engine`, `test_review_research`가 층별로 본다.
  - 지식 무효화·개정의 영향 계산은 `test_currentness`와 `knowledge` 관련 모듈이 본다.
  - 실시간 관찰·운영 검토는 `test_live_observation`과 `test_research_recovery`가 본다.
  - 모델 평가 흐름은 `test_model_assessment_flow`, `test_session_scheduler`가 본다.
  - 공개 초기화에서 해결까지의 종단 연결은 이 모듈의 `SolvedPurposeTests`와 `test_engine.PublicGitFlow`가 나눠 맡는다(`research_fixtures` docstring).
- 픽스처 의존: `purpose_fixtures`의 시나리오 전체(`PurposeRunner`의 다섯 시나리오와 세 관찰 모드, `ActivatedPurposeHarness.make`/`make_active`, `solved_instance`)와 `research_fixtures`의 응답 조각(`disposition`, `planning_model_assessments`, `seal_response`, `bind_candidates`, `charter_change`, `policy_change`, `trust_fixture`)에 기댄다.
- 이 모듈에만 있는 도우미: 없다. 이 모듈은 픽스처를 그대로 쓴다.
- 겹치거나 보완하는 시험:
  - `PurposeFixtureContractTests`는 다른 목적 시험들이 믿는 픽스처 응답이 제품 계약과 맞는지 먼저 고정한다. 곧 픽스처의 시험이다.
  - `test_live_continue_...`와 `test_operating_review_runs_...`는 같은 관찰 모드로 운영 검토 프로필의 `capacity_refs == []`를 함께 단언한다.

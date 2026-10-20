# test_research_recovery

| 항목 | 값 |
|---|---|
| 조각 | `research` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_research_recovery.py` (973행) |
| 클래스 / 테스트 | 12 / 48 (시험 없는 하네스 `RecoveryHarness` 포함) |
| 시험 대상 제품 코드 | `do_math/engine.py`의 `ResearchEngine.run`, `process_controls`, `_inbox`, `status`, `_context`, `_apply`, `_planning_history`, `_register_execution`, `_governance`, `_complete_operational_disposition`(3988행), `_apply_operational_disposition`(3946행), `_run_pending_operational_repairs`(4067행), `_continue_initial_execution`(2436행), `_input_artifacts`; `do_math/repair_execution.py`의 `route_failed_action`, `route_submission_return`, `apply_initial_diagnosis`, `continue_initial_retries`, `pending_installation_repair`, `resume_installation_repair`; `do_math/operational_dispositions.py`의 `reconcile_recovery`; `do_math/activities.py`의 `successor_state`, `validate_activities`; `do_math/record_schemas`의 `RECORDS`, `RUNTIME_FIELDS`; 공개 `control` |
| 사용하는 픽스처 모듈 | `purpose_fixtures`(`ActivatedPurposeHarness`, `PurposeRunner`, `candidate`, `common`, `formal_fixture`, `requirement`); `research_fixtures`(`restore_template`, `local_job_runner`, `producer_result`, `await_stop`, `bare_engine`, `charter_change`, `disposition`, `send_control`); `state_fixtures`(`active_instance`, `active_repository`); `engine_fixtures`(`context_engine`, `initial_failure_engine`, `package`, `routing_engine`, `start_repair_host`); `record_fixtures`(`surface_state`, `transfer_assessment`, `apply_assessment`) |
| 격리 표지 | 없음 |
| 시작 상태 | 2단과 그 위의 모듈 전용 빌드 세 개(`reviewed_task`, `parked_failed_plan`, `paused_limited_recovery`)가 하네스 계열 23개를 맡고, `RecoveryStorageConnectionTests` 1개도 2단(`active_repository`)이다. 1단 순수 함수 시험(`RecoveryOwnershipTests` 등)이 있다. 메모리 엔진 대역(`routing_engine`, `initial_failure_engine`, `context_engine`)과 실제 Git 위의 bare 엔진(`start_repair_host`)도 쓴다 |

## 목적

모듈 docstring(행 1–3)은 연구 작업의 복구를 시험한다고 밝힌다. 대상은 계약 교체, 재시도, 진단, 운영 처분, 수리다. Git 기반 시험은 임시 저장소를 쓰고, 나머지는 메모리 엔진에서 돈다. 이 모듈이 지키는 계약의 축은 다섯이다.

1. 실패한 출력은 보존되고 재생되지 않는다. 독립 작업은 막지 않는다.
2. 재시도는 새 입력으로 같은 활동을 잇고, 원 실패 기록은 그대로 둔다.
3. 제어는 벽시계나 무작위 ID가 아니라 수용 순서(`accepted_order`)로 처리된다.
4. 운영자(operator)는 사용자 정지를 풀거나 수학적·외부 제어를 만들 수 없다.
5. 초기 해석 실패의 진단 재시도는 원 입력과 권한과 종료 증거를 우회하지 않으며, 한 번으로 한정된다.

## 모듈 수준 요소

- 행 14: `scripts/`를 `sys.path` 앞에 넣는 공통 머리.
- `empty_plan(**changes)` (행 27–29): `common(...)`의 중립 필드 위에 빈 `dispositions`, `preparation_requests`, `goal_audit=False`, `task_assessments`를 둔 계획 출력. `changes`로 필드를 덮는다. `parked_failed_plan`과 여러 `InvalidPlan`·`ValidPlan` 지역 러너가 쓴다.
- `purpose_engine(root, instance_id)` (행 32–33): 복사본 위에 `PurposeRunner`와 `formal_fixture`를 단 `ResearchEngine`. 모듈 빌드 세 곳이 쓴다.
- `reviewed_task(root, shared, *, config)` (행 36–49): `restore_template` 빌드. `active_instance`에서 `purpose_engine`을 `run(max_steps=1)`로 최대 45번 몬다. 멈춤 조건은 "`_task_readiness`에 `ready`가 있고 큐에 `research_plan`이 있다"이다. 런타임이 `paused`/`closed`/`waiting`이 되거나 상한을 넘으면 상태와 큐를 담은 `AssertionError`를 낸다. 실제 준비와 실제 계약 검토로 준비 완료가 된 과제 하나와, 그것이 연 계획이 큐에 있는 상태다. `RecoveryHarness.reviewed`가 쓴다.
- `parked_failed_plan(root, shared, *, config)` (행 52–75): `restore_template` 빌드. `active_instance`에서 공개 `configure`로 `max_output_repairs=0`을 둔다. 지역 러너 `InvalidPlan`은 없는 과제 `TK-completed`를 선택한 계획을 `producer_result`로 제출한다. 큐를 `AC-failed` 계획 하나로 바꾸고 `run(max_steps=1)` 한 번을 돈다. 실행이 `execution_incomplete`가 아니거나 `AC-failed`가 `waiting_actions`에 없으면 실패한다. `{'instance_id', 'failed': 실행 레코드}`를 돌려준다. `RecoveryHarness.failed_plan`이 쓴다.
- `paused_limited_recovery(root, shared, *, config)` (행 78–100): `restore_template` 빌드. 큐를 비우고 유지보수 행동 `AC-limited`를 넣는다. 공개 `pause`를 보내고, 공개 `decision`으로 `limited_recovery` 변경을 승인한다. 이 변경은 `action_id`, 연구 권한 `grant_id`, `_select_model`의 `profile_ref`, 목적·절차를 담고, `expires_at`은 빌드 시각에서 5분 뒤다. 인스턴스 ID를 돌려준다. `LimitedRecoveryCallTests`가 쓴다.
- `AT` (행 648): 고정 시각 문자열 `'2026-09-22T00:00:00+00:00'`. `RecoveryBoundaryTests.test_retry_keeps_pending_bundles_and_never_restores_old_input`의 활동·실행 시각에 쓴다.
- 행 972–973: 직접 실행하면 `unittest.main(verbosity=2)`.

`research_fixtures` docstring의 "What to use"는 `reviewed_task`, `parked_failed_plan`, `paused_limited_recovery`를 이 모듈 전용 빌드로 적는다.

## RecoveryStorageConnectionTests (행 103–125)

- 기반 클래스: `unittest.TestCase`. 표지·속성·도우미·훅이 없다.

### `test_operational_retry_producer_survives_actual_git_storage` (행 104–125)
- 성질: 운영 재시도 처분이 만든 이어 가기 행동과 그 복구 표지는, 실제 Git 저장·재적재를 거쳐도 그대로 남는다. 원 실행의 결과(`start_failed`)도 보존된다.
- 준비: 2단(`state_fixtures.active_repository()`). 행동 `AC-rejected`(`research_plan`)는 `_action_lifecycle_gate`를 통과시켜 둔다. 그다음 실행 `EX-rejected`를 `starting`으로 등록하고, `stopping`을 거쳐 `ended`(`outcome='start_failed'`)로 전이한다.
- 실행: 이미 결정된 처분 `OD-fixture`(`kind='retry'`)로 `engine._complete_operational_disposition`, `_save()`, 새 `ResearchEngine`으로 재적재.
- 단언: 재적재한 큐에 `continuation_of == EX-rejected`인 행동이 있다. 그 `recovery.execution_id`가 원 실행이고 `recovery.disposition_id == 'OD-fixture'`다. 원 실행의 `outcome == 'start_failed'`다.
- 대역: 없음. 주석(행 115–116)은 시험이 이미 결정된 운영 판정만 공급하고, 실제 재시도 생산자와 타입 있는 Git 저장·재적재가 검사 대상이라고 적는다.

## RecoveryHarness (행 128–141)

- 기반 클래스: `ActivatedPurposeHarness`. 시험이 없는 공유 하네스로, `ResearchRecoveryTests`와 `RecoveryRoutingTests`가 상속한다.
- 도우미 메서드:
  - `reviewed()` (행 129–132): `restore_template(reviewed_task, config=fixture_config(max_output_repairs=0))`의 복사본과 `PurposeRunner`.
  - `failed_plan()` (행 134–138): `parked_failed_plan`(`fixture_config()`) 복사본의 `(engine, failed)`.
  - `active(**config)` (행 140–141): `make_active(**fixture_config(**config))`, 곧 2단 합성 활성 상태에 목적 시나리오 설정을 준 것.

## ResearchRecoveryTests (행 144–236)

- 기반 클래스: `RecoveryHarness`. 표지·속성·훅이 없다.

### `test_revised_contract_replaces_obsolete_criteria_and_preserves_history` (행 146–176)
- 성질: 계약 검토를 받은 과제를 준비가 개정하면 새 완료 의무로 대체된다. 옛 의무는 개정 이력에 남는다. 이전 검토는 비워지고, 개정 번호가 오르며, 상태는 `planned`로 돌아간다.
- 준비: `reviewed()`(2단 위 `reviewed_task`). 제안은 `candidate('A', revises=old id)`의 첫 완료 의무 `claim`과 `scope`를 바꾼 것이다. 지역 러너 `RevisionRunner(PurposeRunner)`는 준비에서만 이 제안을 낸다. 큐를 비우고 `AC-revision` 준비를 넣는다.
- 실행: `engine.run(max_steps=1)`.
- 단언:
  - 개정 실행의 `outcome == 'output_accepted'`다. 실패하면 오류·통합 결과·대기를 메시지로 싣는다.
  - 현재 `completion_obligations`가 제안과 같다.
  - `revision_history[-1].completion_obligations`가 옛 의무와 같다.
  - `reviews == []`, `revision == 옛 + 1`, `status == 'planned'`다.
  - `_governance()['goal_revision'] == 1`이다.
- 대역: `RevisionRunner`(실제 Windows Job, `local_job_runner`는 `PurposeRunner.run`에 붙어 있음).

### `test_plan_rejection_names_missing_unexpected_and_duplicate_ids` (행 178–195)
- 성질: 모집단이 틀린 계획의 반려 사유는 빠진 준비 완료 ID, 예상치 못한 ID, 중복 ID를 모두 이름으로 댄다.
- 준비: `reviewed()`. `_refresh_readiness()`로 준비 완료 ID를 얻고, 큐를 계획 하나로 줄인다. 지역 러너 `InvalidPlan`은 `TK-absent`를 두 번(사유만 다름) 선택한 계획을 제출한다.
- 실행: `run(max_steps=1)`.
- 단언: `waiting_actions`를 JSON으로 직렬화한 문자열에 `'missing'`, 준비 완료 ID, `'unexpected'`, `'TK-absent'`, `'duplicate'`가 모두 있다.
- 대역: `InvalidPlan`(실제 Windows Job).
- 비고: 메시지 조각만 보고 이슈 구조는 보지 않는다.

### `test_plan_input_always_has_authoritative_ready_ids` (행 197–204)
- 성질: 계획 입력 문맥은 준비 완료 과제가 없어도 권위 있는 `ready_task_ids`를 늘 싣는다.
- 준비: `reviewed()`. 유일한 과제를 `completed`로 바꾸고 `_refresh_readiness()`를 부른다.
- 실행: `engine._context({'role': 'research_plan'}, root/'plan-input')`.
- 단언: `ready_task_ids == []`(키가 있고 빈 목록), `task_readiness[tid].state == 'not_ready'`다.
- 대역: 없음(러너 불리지 않음).

### `test_exhausted_output_repair_does_not_stop_unrelated_work` (행 206–226)
- 성질: 출력 수리 한도가 소진된 실패 계획은 대기로 빠진다. 인스턴스를 멈추지 않고 독립 행동은 큐에 남는다.
- 준비: 2단 `active(max_output_repairs=0)`. 큐는 `AC-bad-plan`(계획)과 `AC-independent`(준비)다. 지역 러너 `InvalidPlan`은 `producer_result`를 거치지 않고 잘못된 계획을 직접 돌려준다. 주석(행 212–213)은 유효 생산자 도우미가 반환 전에 예외를 내기 때문이라고 적는다.
- 실행: `run(max_steps=1)`.
- 단언: 상태가 `ready`다. `AC-independent`가 큐에 있다. `AC-bad-plan`이 `waiting_actions`에 있고, 그 `kind == 'output_validation'`이며 `execution_id`가 있다.
- 대역: `InvalidPlan`(실제 Windows Job).

### `test_resume_keeps_failed_output_out_of_execution_queue` (행 228–236)
- 성질: 일시 정지 뒤 재개해도 반려된 출력의 행동은 대기에 남고 실행 큐로 돌아오지 않는다.
- 준비: `failed_plan()`(`parked_failed_plan` 복사본).
- 실행: `send_control(pause)`, `_enqueue('research_preparation', requested_by='UC-fixture')`, `_save()`, `send_control(resume)`.
- 단언: 실패 행동 ID가 큐에 없고 `waiting_actions`에 있다. 큐에 `research_preparation`이 있다.
- 대역: 없음.

## RecoveryRoutingTests (행 239–492)

- 기반 클래스: `RecoveryHarness`. 표지·속성·훅이 없다.
- 도우미 메서드 `diagnose(engine, failed, kind='retry')` (행 310–330): 실패 실행에 대한 운영 진단을 한 번 돌린다. 제안은 `kind`, `basis_refs=[failed id]`, `next_owner='research_plan'`이다. `retry`면 `scope`와 `replay_safety`를 싣고, `repair`면 `repair_target=failed['id']`, `meaning_preserving=True`, `verification`을 싣는다. 지역 러너 `DiagnosisRunner`는 이 제안을 `producer_result`로 제출한다. 큐 맨 앞에 `AC-diagnose`(`operational_review`, 실패 실행 대상)를 넣고 `run(max_steps=1)`을 부른 뒤 원래 러너를 되돌린다.

### `test_controls_with_identical_wall_time_preserve_acceptance_order` (행 240–250)
- 성질: 벽시계 시각이 같은 두 제어는 ID 순서가 아니라 수용 순서대로 처리된다.
- 준비: 2단 `active()`. `do_math.engine.new_id`는 역순 ID 두 개를 내고, `do_math.engine.now`는 같은 시각을 낸다.
- 실행: 공개 `conversation` 제어 `attach`(`disconnect_policy='pause'`, 임대 60초)를 보낸 뒤 `detach`를 보낸다. 이어 `_inbox()`를 읽고 `process_controls()`를 부른다.
- 단언: 수신함의 `operation` 순서가 `['attach','detach']`다. 처리 뒤 상태는 `paused`다. 분리가 대화 상실을 낳아 정지한다.
- 대역: `do_math.engine.new_id`, `do_math.engine.now`의 `mock.patch`.

### `test_control_processing_uses_acceptance_time_not_random_id_order` (행 252–263)
- 성질: 제어는 무작위 ID 순서가 아니라 수용 시각 순서로 처리되고, 수용 번호는 1씩 오른다.
- 준비: 2단. `new_id`는 역순 ID를, `now`는 마이크로초 차이의 두 시각을 낸다.
- 실행: `pause`('first') 뒤 `resume`('second'), `_inbox()`, `process_controls()`.
- 단언: 수신함 행동 순서가 `['pause','resume']`이고, `accepted_order` 차이가 1이다. 처리 뒤 상태는 `ready`다.
- 대역: 같은 두 패치.

### `test_controls_preserve_acceptance_order_when_wall_clock_moves_back` (행 265–273)
- 성질: 벽시계가 뒤로 가도 수용 순서가 유지된다.
- 준비: 2단. `now`가 01:00:01 다음에 01:00:00을 낸다.
- 실행: `pause` 뒤 `resume`, `_inbox()`, `process_controls()`.
- 단언: 수신함 순서가 `['pause','resume']`이고, 처리 뒤 `ready`다.
- 대역: `do_math.engine.now` 패치.

### `test_concurrent_controls_receive_distinct_durable_order` (행 275–284)
- 성질: 동시에 들어온 제어들은 서로 다르고 연속된 수용 번호를 받는다.
- 준비: 2단.
- 실행: `ThreadPoolExecutor(max_workers=4)`로 `pause` 제어 4개를 동시에 보내고 `_inbox()`를 읽는다.
- 단언: 요청 ID가 4개로 모두 다르다. 수용 번호를 정렬하면 첫 번호부터 연속된 4개다.
- 대역: 없음(실제 스레드 동시성).

### `test_preparation_cannot_replace_a_user_academic_requirement_contract` (행 286–308)
- 성질: 준비 역할은 사용자가 정한 학술 요구 계약 과제를 개정 후보로 대체할 수 없다.
- 준비: 2단. `patch.object(engine, '_solution_basis', return_value={'goal_ref': 'synthetic-solution', 'records': []})`를 `enterContext`로 건다. `goal_status='mathematically_solved'`로 두고 저장한다. 공개 `decision`으로 `academic_requirements=[requirement([...])]`를 승인한 뒤 `_ensure_academic_followup()`와 `_save()`로 학술 과제를 만든다. 주석(행 289–290)은 이 시험이 저술 권한만 보므로 해결 전제는 합성이라고 적는다.
- 실행: 종료된 준비 실행 `EX-replacement`를 넣는다. 그 실행으로 `engine._apply({'role': 'research_preparation'}, {'candidates': [candidate('Replacement', revises=task id)]}, 'EX-replacement')`를 부른다.
- 단언: `ValueError`의 메시지가 정규식 `'academic'`에 맞는다. 과제가 사본과 같다.
- 대역: `_solution_basis` 패치.
- 비고: 해당 제품 거부는 `engine.py` 3674–3675행의 "user-defined academic contracts require an academic_requirements decision"이다. 시험은 `'academic'` 조각만 고정한다.

### `test_output_failure_opens_diagnosis_without_replaying_rejected_plan` (행 332–345)
- 성질: 수리 한도가 없을 때 출력 검증에 실패한 계획은 운영 진단을 열고, 반려된 계획 행동을 다시 큐에 넣지 않는다.
- 준비: 2단 `active(max_output_repairs=0)`. 큐는 `AC-invalid` 하나이고, 지역 러너 `InvalidPlan`은 `TK-absent` 선택 계획을 `producer_result`로 제출한다.
- 실행: `run(max_steps=1)`.
- 단언: 큐에 `operational_review`가 있고 `AC-invalid`는 없다.
- 대역: `InvalidPlan`(실제 Windows Job).

### `test_diagnosed_plan_retry_uses_fresh_input_and_preserves_failure_and_independent_work` (행 347–368)
- 성질: 진단이 재시도를 처분하면 같은 행동 ID·같은 활동의 이어 가기가 생긴다. 이어 가기는 새 입력을 쓰고, 수리 표지가 없으며, 원 실패 기록과 독립 작업은 보존된다.
- 준비: `failed_plan()`. 큐를 `AC-independent`(준비) 하나로 둔다. 실패 실행의 사본을 떠 둔다.
- 실행: `diagnose(engine, failed)`(`retry`). 이어 이어 가기 행동에 대해 `_context(action, root/'fresh-plan')`를 부른다.
- 단언:
  - `continuation_of == failed id`인 행동이 정확히 1개다.
  - 그 행동의 역할은 `research_plan`이고, `id`는 원 행동 ID와 같으며, `repair`와 `repair_attempt` 키가 없다.
  - 문맥은 `ready_task_ids == []`이고, `previous_execution`의 `id`와 `outcome`(`execution_incomplete`)이 원 실행을 가리키며, `snapshot == engine.head`다.
  - `recovery.execution_id`가 원 실행이다.
  - `AC-independent`가 큐에 있다.
  - 원 실행 레코드가 사본과 같다.
  - 질문이 없다.
- 대역: `DiagnosisRunner`(실제 Windows Job).

### `test_successful_fresh_plan_resolves_parked_failure_without_deleting_history` (행 370–394)
- 성질: 새 계획이 확장 `action_resolutions`로 대기 중인 실패 행동을 명시적으로 해소하면 대기가 풀리고 활동이 끝난다. 원 실행의 결과는 지워지지 않는다.
- 준비: `failed_plan()`. 지역 러너 `ValidPlan`은 `action_resolutions`(`AC-failed`, `evidence_execution_id='current'`)를 확장에 쓰고 빈 계획을 제출한다. 큐는 `AC-fresh` 하나다.
- 실행: `run(max_steps=1)`, 이어 `store.load()`.
- 단언:
  - `AC-failed`가 대기에 없다.
  - 원 실행의 `outcome == 'execution_incomplete'`가 유지된다.
  - 이력에 `kind == 'failed_action_explicitly_resolved'` 행이 있다.
  - 원 실행의 활동은 `status == 'finished'`이고, `waiting` 키가 없으며, `unresolved == []`다. `result_refs`에 해소 실행이 있고, `followups[0].resolved_by`가 그것과 같다.
  - 저장된 활동이 메모리의 활동과 같다.
- 대역: `ValidPlan`(실제 Windows Job).

### `test_diagnosis_wait_does_not_block_independent_actions` (행 396–401)
- 성질: 운영 진단이 대기를 낳아도 독립 행동은 막히지 않는다.
- 준비: `failed_plan()`. 큐는 `AC-other`(준비) 하나다.
- 실행: `diagnose(engine, failed, kind='repair')`.
- 단언: 상태가 `ready`이고, 큐 맨 앞이 `AC-other`다.
- 대역: `DiagnosisRunner`.
- 비고: `repair` 제안의 `repair_target`은 `failed['id']`(실행 ID)다. 제품의 처분 스키마는 `repair_target`에 패턴 `^installation:`을 요구하므로(`contracts.py` 191행), 이 진단 출력은 수용될 수 없다. 제출 경로를 따라가면 다음과 같다. `DiagnosisRunner`는 `producer_result`로 `submit_intent`를 보낸다. 엔진의 중앙 수령은 `submission.seal_submission`에서 `check_submission`과 `payload_issues`를 거친다. 그 검사가 `output/disposition`에 `schema.anyOf` 이슈를 낸다. `operational_review`는 분할 연구가 아니므로(`integration.split_research`가 거짓) `capture_eligible`이 거짓이 된다. 그래서 `_stage_submission_capture`는 수령을 `rejected`('candidate validation failed')로 기록한다. 그러면 `research_fixtures.submit_intent`가 `AssertionError`를 내고, 호출은 실패 결과(`parallel.failed_result`)로 끝난다. 같은 모듈의 `OperationalRepairCandidateTests`도 이런 대상이 `'repair/repair_target'`로 거부됨을 단언한다. 이 시험은 그 뒤의 `status == 'ready'`와 큐 머리 `AC-other`만 본다. 따라서 수용된 repair 처분이 독립 행동을 막지 않는지는 검사하지 않고, 실패한 진단 호출 뒤의 상태만 확인한다.

### `test_operator_resume_cannot_release_a_user_pause` (행 403–414)
- 성질: 운영자 출처의 재개는 사용자 정지를 풀지 못하고, 사용자 출처의 재개만 푼다.
- 준비: 2단.
- 실행: `pause`('Wait for my decision.'), `process_controls()`, `resume`(`origin='operator'`), 처리, `resume`(`origin='user'`), 처리.
- 단언: 정지 뒤 `status()['user_pause']['reason']`이 정지 문구와 같다. 운영자 재개 뒤에도 `paused`다. 사용자 재개 뒤 `ready`이고 `user_pause`가 `None`이다.
- 대역: 없음.

### `test_scholarly_configuration_reaches_the_actual_runner_call` (행 416–433)
- 성질: 학술 검색 서버 설정은 고정된 프로필(`profile.ai.scholarly_server`)로만 러너 호출에 도달하고, 별도 `scholarly_server` 인자는 넘어가지 않는다.
- 준비: 2단 `active(scholarly_enabled=True, scholarly_server={'command': sys.executable, 'args': [scholarly-fixture-server.py 경로]})`. 주석(행 417)은 절대 경로로만 검증되고 서버는 돌지 않는다고 적는다.
- 실행: 지역 러너 `CapturingRunner`가 `(kwargs.get('scholarly_server'), kwargs['profile']['ai']['scholarly_server'])`를 기록하고 빈 준비를 제출한다. `run(max_steps=1)`.
- 단언: 기록이 `[(None, 설정의 scholarly_server)]`이고, 설정값이 준 `server`와 같다.
- 대역: `CapturingRunner`(실제 Windows Job).
- 비고: 주석(행 424–425)은 `ModelRunner.run`이 프로필 옆의 별도 인자를 거부한다고 설명한다.

### `test_rejected_history_keeps_original_output_out_of_inline_action` (행 435–447)
- 성질: 계획 이력은 반려된 원 출력(`repair.previous_output`)을 인라인 행동에 싣지 않는다. 원 행동은 별도 원천 파일로 공급한다.
- 준비: `failed_plan()`. 실패 실행의 `action.repair`에 `previous_output`을 넣는다.
- 실행: `engine._planning_history('research_plan', workspace)`.
- 단언: 그 실행의 이력 행에서 `action.repair`에 `previous_output`이 없다. `action_source.local_path`의 JSON이 원 `action` 전체(`previous_output` 포함)와 같다.
- 대역: 없음.

### `test_status_failure_summary_does_not_repeat_rejected_output` (행 449–454)
- 성질: 상태 요약의 실패 대기 항목은 반려된 출력을 반복하지 않고 실행 ID로 가리킨다.
- 준비: `failed_plan()`, `_save()`.
- 실행: `engine.status()['waiting_actions']['AC-failed']`.
- 단언: 직렬화 문자열에 `'previous_output'`이 없다. `execution_id`가 런타임 실행에 있다.
- 대역: 없음.

### `test_operator_cannot_create_mathematical_or_external_controls` (행 456–460)
- 성질: 운영자 출처로는 수학적·외부 효과를 낳는 제어를 만들 수 없다.
- 준비: 2단.
- 실행: `decision`, `input`, `conversation`, `close`, `external`, `trust`, `knowledge` 일곱 행동마다 `control(..., origin='operator', text=...)`를 부른다.
- 단언: 모두 `ValueError`(유형만 본다).
- 대역: 없음.
- 비고: `subTest(action=...)` 7건. 메시지를 보지 않으므로 거부 사유는 고정하지 않는다.

### `test_conditional_hold_release_preserves_a_different_user_pause` (행 463–470)
- 성질: 기대 정지 사유를 조건으로 건 재개는 사유가 다른 사용자 정지를 풀지 않는다.
- 준비: 2단.
- 실행: `pause`('A newer independent user pause.'), `resume`(`config={'expected_user_pause_reason': '... HOLD old-hold'}`), `process_controls()`.
- 단언: 상태가 `paused`이고, `runtime['user_pause']['reason']`이 새 정지 문구다.
- 대역: 없음.

### `test_conditional_hold_release_handles_a_pause_still_in_the_inbox` (행 472–479)
- 성질: 조건부 재개는 아직 수신함에 있는(처리 전) 같은 사유의 정지도 올바르게 푼다.
- 준비: 2단.
- 실행: 같은 사유 `'User requested scheduled operator HOLD pending-hold'`로 `pause`와 조건부 `resume`을 연달아 보낸 뒤 한 번에 처리.
- 단언: 상태가 `ready`이고 `user_pause`가 `None`이다.
- 대역: 없음.

### `test_operator_respects_explicit_pause_on_conversation_loss` (행 481–492)
- 성질: 대화 상실로 생긴 명시적 정지(`disconnect_policy='pause'`)는 운영자 재개로 풀리지 않는다.
- 준비: 2단.
- 실행: `attach`, `detach`, 처리, `resume`(`origin='operator'`), 처리.
- 단언: 두 처리 뒤 모두 `paused`다.
- 대역: 없음.

## LimitedRecoveryCallTests (행 494–528)

- 기반 클래스: `ActivatedPurposeHarness`. 표지·속성·도우미·훅이 없다.

### `test_actual_ai_call_keeps_pause_and_honors_a_new_stop` (행 495–528)
- 성질: 승인된 제한 복구의 실제 AI 호출은 사용자 정지 상태에서도 돈다. 그 동안 정지는 유지된다. 새 정지가 오면 그 호출도 멈춘다.
- 준비: 2단 위 빌드 `paused_limited_recovery`(`fixture_config()`)를 `subTest`마다 새로 복원한다.
- 실행: 지역 러너 `Runner`가 호출 안에서 다음을 확인한다: 런타임과 수명 주기가 모두 `paused`이고 `should_stop()`이 거짓이다. `stop_again`이 참이면 새 `pause` 제어를 보내고 `await_stop`으로 정지 판정을 기다린 뒤 `status='stopped'`를 돌려준다. 거짓이면 유지보수 보고를 `producer_result`로 제출한다. `run(max_steps=1)`.
- 단언: 호출은 1번이다. 실행 `outcome`은 `stop_again`이면 `cancelled`, 아니면 `output_accepted`다. 두 경우 모두 런타임과 수명 주기가 `paused`이고 `user_pause`가 남는다.
- 대역: `Runner`(실제 Windows Job). `await_stop`은 상한 60초로 폴링한다.
- 비고: `subTest(stop_again=False/True)` 2건. 빌드의 복구 결정은 빌드 시각에서 5분 뒤 만료되므로, 같은 프로세스에서 빌드 뒤 5분 넘게 지나 이 템플릿을 쓰면 전제가 달라진다(`research_fixtures` docstring의 시간 규칙 참조).

## InitialDiagnosisTests (행 531–568)

- 기반 클래스: `unittest.TestCase`. 표지·속성·도우미·훅이 없다.

### `test_exhausted_initial_repairs_have_a_reachable_diagnostic_owner` (행 532–540)
- 성질: 초기화 중 해석 실행의 출력 수리가 소진되면 유지보수 진단이 그 실행을 대상으로 요청된다.
- 준비: 1단에 가까운 bare 엔진. `bare_engine({'lifecycle': {'state': 'initializing'}, 'config': {'max_output_repairs': 1}}, ...)`이고, `_enqueue`는 호출을 기록하는 autospec 대역이다.
- 실행: `route_submission_return(action(repair_attempt=1), {...빈 반려...}, 'EX-bad', None)`.
- 단언: 첫 `_enqueue` 위치 인자가 `('maintenance', 'EX-bad')`이고, 키워드 `initial_submission_diagnosis`가 참이다.
- 대역: `_enqueue`의 `create_autospec`.

### `test_diagnosis_and_bound_rules_fit_the_persisted_contract` (행 542–549)
- 성질: 진단 행동과 진단 재시도 행동이 저장 스키마에 맞고, 실행 레코드 스키마에 `observation_rules` 필드가 있다.
- 준비: 1단.
- 실행: `jsonschema.Draft202012Validator(RECORDS['queue']).validate(...)`를 두 행동에 부른다.
- 단언: 예외가 없다. `RECORDS['executions']['properties']`에 `'observation_rules'`가 있다.
- 대역: 없음.

### `test_diagnosis_retry_preserves_the_original_and_is_bounded` (행 551–568)
- 성질: 초기 진단의 재시도는 원 입력·원 활동을 잇는 행동으로 한 번만 생긴다. 그 재시도가 다시 반려되면 더는 큐에 넣지 않는다.
- 준비: 메모리 대역 `initial_failure_engine(root, 'output_validation')`. 이 픽스처는 `FakeEngine` 시드로 초기 해석 실패 `EX-bad`와 대기를 만들고, 저장소는 `create_autospec(ResearchRepository)`다. `_save`도 autospec 대역이다.
- 실행: `apply_initial_diagnosis(diagnostic, {'decision': 'retry', ...}, 'EX-diagnosis')`. 진단 실행을 `ended`/`output_accepted`로 넣고 `continue_initial_retries()`를 부른다. 뽑은 재시도로 `route_submission_return(...)`을 부른다.
- 단언: 진단 적용 직후 큐가 비어 있다. 재시도 행동의 `target == 'UI-original'`, `owner_activity_id == 'AY-original'`, `diagnosis_attempt == 1`이다. 재반려 뒤 큐가 비어 있다.
- 대역: `initial_failure_engine`, `_save` autospec.

## RetryEffectTests (행 571–583)

- 기반 클래스: `unittest.TestCase`. 표지·속성·도우미·훅이 없다.

### `test_retry_waits_for_unknown_effect_from_an_ancestor` (행 572–583)
- 성질: 재시도 대상의 조상 실행이 결과를 알 수 없는(unknown) 외부 효과를 남겼으면, 재시도는 그 효과를 대조하기 전에는 적용되지 않는다.
- 준비: 메모리 대역 `routing_engine()`. `EX-later`가 `EX-original`을 잇고, 외부 작업 `EO-one`은 `status='unknown'`이며 생산자가 `EX-original`이다.
- 실행: `_complete_operational_disposition({'target_execution_id': 'EX-later', 'disposition': {'kind': 'retry'}})`.
- 단언: `ValueError`의 메시지가 정규식 `'reconciliation'`에 맞는다(제품 문구 "recovery requires reconciliation of unknown external effects", `engine.py` 4021행). 큐가 비어 있다.
- 대역: `routing_engine`.

## RecoveryOwnershipTests (행 586–645)

- 기반 클래스: `unittest.TestCase`. 표지·속성·훅이 없다. 1단 순수 함수 시험이다.
- 도우미 메서드:
  - `runtime(status='running', *, successor=True)` (행 587–594): 활동 `AY-one`의 끝난 실행 `EX-old`(`research_plan`, `error='returned'`)를 둔다. `successor`가 참이면 같은 활동에서 `EX-old`를 잇는 `EX-new`(지정 `status`)를 더한다.
  - `record(kind='retry')` (행 596–598): 적용된(`applied`) 처분 `OD-one`, 대상 `EX-old`.

### `test_live_and_ended_successors_supersede_old_retry_and_resume` (행 600–609)
- 성질: 같은 활동에 이어 가기 실행이 이미 있으면 그것이 살아 있든 끝났든, 옛 `retry`/`resume` 처분은 대체(superseded)된다. 새 행동은 넣지 않고 원 오류는 보존한다.
- 준비: `runtime(status)`와 `record(kind)`.
- 실행: `operational_dispositions.reconcile_recovery(runtime, record)`.
- 단언: 반환 `True`, `record.status == 'superseded'`, 큐가 비어 있음, `EX-old.error == 'returned'`.
- 대역: 없음.
- 비고: `subTest(kind, status)` 6건. `kind`는 `retry`/`resume`, `status`는 `starting`/`running`/`ended`다.

### `test_unrelated_success_cannot_supersede_failure` (행 611–615)
- 성질: 다른 활동의 성공 실행은 실패를 대체하지 못한다.
- 준비: `runtime('ended')`에서 `EX-new`의 활동을 `AY-other`로 바꾼다.
- 실행: `activities.successor_state(runtime, 'EX-old')`, `reconcile_recovery`.
- 단언: 앞의 것은 `None`, 뒤의 것은 `False`.
- 대역: 없음.

### `test_queued_continuation_already_owns_recovery` (행 617–622)
- 성질: 이어 가기 행동이 이미 큐에 있으면 그것이 복구를 소유한 것으로 보고 상태를 바꾸지 않는다.
- 준비: 후속 실행 없이 큐에 `continuation_of='EX-old'` 행동.
- 실행: `reconcile_recovery`.
- 단언: 반환 `True`이고, 런타임이 사본과 같다.
- 대역: 없음.

### `test_task_continuation_does_not_discharge_a_separate_installation_defect` (행 624–631)
- 성질: 과제의 이어 가기 실행이 있다고 해서 따로 남은 설치 결함 수리 대기가 해소되지는 않는다.
- 준비: `runtime()`에 다른 활동 실행 `EX-other`를 더한다. 처분 둘은 모두 `installation_repair_pending`이다. `OD-one`은 `EX-old`, `OD-other`는 `EX-other` 대상이다.
- 실행: `repair_execution.pending_installation_repair(runtime)`, `reconcile_recovery(runtime, old)`.
- 단언: 대기 수리가 `old`이고, 조정은 `False`다.
- 대역: 없음.

### `test_successful_installation_repair_preserves_the_existing_continuation` (행 633–640)
- 성질: 설치 수리가 성공하면 이미 살아 있는 이어 가기를 보존하고 새 행동을 넣지 않는다.
- 준비: `runtime()`(살아 있는 `EX-new`)과 `installation_repair_pending` 처분.
- 실행: `repair_execution.resume_installation_repair(runtime, record, repaired_by='EX-repair', at=...)`.
- 단언: 반환 `None`, 큐가 비어 있음, `record.status == 'applied'`, `result.installation_repair.successor.live_execution_ids == ['EX-new']`.
- 대역: 없음.

### `test_already_applied_retry_keeps_its_receipt` (행 642–645)
- 성질: 이미 적용되어 이어 가기 영수(`continuation_action_id`)를 가진 재시도는 다시 조정되지 않는다.
- 준비: `record()`에 `result.continuation_action_id='AC-one'`.
- 실행: `reconcile_recovery(self.runtime(), record)`.
- 단언: `False`, `record.status == 'applied'`.
- 대역: 없음.

## RecoveryBoundaryTests (행 651–860)

- 기반 클래스: `unittest.TestCase`. 표지·속성·도우미·훅이 없다.

### `test_restart_finishes_an_accepted_retry_after_target_termination_once` (행 652–673)
- 성질: 대상 종료를 기다리던(`awaiting_termination`) 수용된 재시도는 재시작 뒤 인스턴스가 `ready`가 되면 정확히 한 번 끝난다. 이어 가기 행동이 하나 생기고, 처분은 `applied`가 되며, 대상의 대기 표지는 지워진다.
- 준비: `engine_fixtures.start_repair_host(self)`. 실제 Git 저장소(`git_init`) 위의 bare 엔진이고, 끝난 `EX-target`과 `EX-review`, 대기 처분 `OD-repair`를 가진다. 대상에서 `input_bundle`을 빼고 `pending_operational_disposition='OD-repair'`를 둔다. 처분은 `awaiting_termination`인 `retry`로 바꾸고, 런타임을 `paused`로 저장한다(주석: 대상이 끝난 뒤의 중단을 재적재 상태로 모사).
- 실행: 호스트의 `_complete_operational_disposition`을 제품 메서드로 다시 묶는다. `ResearchEngine._run_pending_operational_repairs(host)`를 `paused`에서 한 번 부르고, `ready`로 저장한 뒤 두 번 부른다.
- 단언: `paused`일 때는 큐가 비어 있다. 저장본 큐는 1개, 처분 `status == 'applied'`이고, 대상에 `pending_operational_disposition`이 없다.
- 대역: 없음(실제 Git, git 자식 프로세스).

### `test_initial_diagnosis_receives_the_original_role_contract_bytes` (행 675–704)
- 성질: 초기 제출 진단의 입력은 실패한 해석 실행이 받았던 원래 역할 계약 바이트(프롬프트, 스키마, 고정 문맥)를 그대로 받는다.
- 준비: `initial_failure_engine(root)`. `surface_state()`의 `governance`와 `governance_sources`를 옮긴다. `EX-bad`에 `input_bundle='BA-original'`과, 프롬프트를 가리키는 `input_manifest`를 둔다. 저장소 `read`/`read_many`는 원본 세 파일 사전에서 읽는다. `_documents`, `_preparation_checkpoint`, `_session_slots`, `_academic_status`를 대역으로 둔다.
- 실행: `_context({'role': 'maintenance', 'target': 'EX-bad', 'initial_submission_diagnosis': True}, workspace)`.
- 단언: `initial_submission_diagnosis.materials`의 `artifact_ref` 집합이 원본 세 경로와 같다. 각 로컬 파일 바이트가 원본과 같고 sha256이 기록과 같다.
- 대역: 저장소 autospec의 `side_effect`, `create_autospec` 메서드 대역들.

### `test_initial_diagnosis_receives_the_failed_checkpoint_evidence_files` (행 706–727)
- 성질: 초기 진단 입력은 실패한 실행의 체크포인트와 그 증거 파일을 싣는다.
- 준비: 앞 시험과 같은 엔진 구성. `checkpoints['EX-bad']`에 증거 파일 `notes.txt`(참조 `runtime/artifacts/BA-checkpoint/evidence/notes.txt`)를 둔다.
- 실행: 같은 `_context` 호출.
- 단언: 그 참조의 자료 행 로컬 파일이 증거 바이트와 같다.
- 대역: 앞 시험과 같다.
- 비고: 주석(행 707)이 계약 근거를 적는다. `계약/유지보수.md` 42행과 `공통-실행.md` 49행이 "진단은 체크포인트와 그 증거를 읽는다"고 정한다.

### `test_retry_queue_and_disposition_publish_together_and_replay_is_noop` (행 729–750)
- 성질: 재시도의 이어 가기 행동과 처분 상태는 같은 게시에서 함께 나타난다. 같은 처분을 다시 적용해도 아무 일도 없고, 작업공간의 손상 파일은 건드리지 않는다.
- 준비: `start_repair_host(self)`. 대상의 `input_bundle`을 빼고(주석: 큐와 CAS 게시만 떼어 봄), 처분을 `pending` `retry`로 두고 저장한다.
- 실행: `ResearchEngine._complete_operational_disposition(host, record)`, 저장소 재적재, `_save()`, 재적재, 같은 처분으로 다시 호출.
- 단언:
  - 첫 호출 직후 저장본 큐는 비어 있다. 아직 게시 전이다.
  - 저장 뒤 머리가 바뀌고, 처분은 `applied`이며, `result.continuation_action_id`가 저장본 큐 첫 행동 ID와 같다.
  - 재적용 뒤 큐 길이가 1이다.
  - 손상 파일 내용이 `b'damaged'` 그대로다.
- 대역: 없음(실제 Git).

### `test_initial_failure_kinds_and_stages_reach_one_authorized_followup` (행 752–782)
- 성질: 초기 해석 실패의 모든 종류와 단계는 유지보수 진단 하나로 이어진다. 그 진단의 재시도는 원 단계·원 활동·원 실행을 잇고, 불변 입력을 바꾸지 않으며, 한 번으로 한정된다.
- 준비: `subTest`마다 `initial_failure_engine(root, kind, stage)`.
- 실행:
  1. `route_failed_action(action, 'EX-bad', ...)`로 진단 행동을 뽑는다.
  2. 진단 행동을 `_action_lifecycle_gate`에 통과시킨다.
  3. 실행 중인 진단 실행으로 `apply_initial_diagnosis(... 'retry' ...)`를 부른다.
  4. `_save`를 autospec으로 바꾸고 진단을 `ended`로 둔 뒤 `continue_initial_retries()`를 부른다.
  5. 재시도의 반려를 `route_submission_return`으로 보낸다.
- 단언:
  - 진단 역할은 `maintenance`다.
  - 진단 적용 직후 큐가 비어 있다(메시지: 후보 적용은 네이티브 복구를 게시하지 않음).
  - 재시도의 `stage`는 원 단계이고, `owner_activity_id == 'AY-original'`, `continuation_of == 'EX-bad'`, `diagnosis_attempt == 1`이다.
  - 불변 입력이 사본과 같다.
  - `output_validation`이면 `repair.retry_bundle_ids == ['IN-pending']`다.
  - 재반려 뒤 큐가 비어 있다.
- 대역: `initial_failure_engine`, `_save` autospec.
- 비고: `subTest(kind, stage)` 6건. `kind`는 `output_validation`/`execution_failure`/`submission_failure`, `stage`는 `interpret`/`check`다.

### `test_failed_diagnosed_retry_is_recorded_once_and_remains_storable` (행 784–801)
- 성질: 진단된 재시도를 만들 수 없으면 그 오류를 대기에 한 번만 기록하고 저장 스키마를 지킨다. 권한 취소가 그런 경우다.
- 준비: `initial_failure_engine(root)`. 진단을 적용하고 진단 실행을 `ended`로 둔다. 권한 `GR-init`을 `revoked`로 바꾸고 `_save`를 autospec으로 둔다.
- 실행: `continue_initial_retries()`를 두 번.
- 단언: 대기의 `diagnosis`에 `retry_error`가 있다. 큐가 비어 있다. `_save.assert_called_once()`다. `RUNTIME_FIELDS['waiting_actions']` 스키마로 대기를 검증하면 통과한다.
- 대역: `initial_failure_engine`, `_save` autospec.

### `test_initial_diagnosis_does_not_bypass_termination_source_or_authority` (행 803–816)
- 성질: 진단 재시도는 세 경우에 거부된다. 원 실행의 로컬 종료가 확인되지 않은 경우, 원 입력 원천이 바뀐 경우, 권한이 취소된 경우다.
- 준비: `subTest(changed=termination/source/grant)`마다 `initial_failure_engine`의 한 조건을 바꾼다. `capacity.local_termination='unknown'`, `inputs[0].text='changed'`, `GR-init` 취소다.
- 실행: `engine._continue_initial_execution(wait, request_id='EX-diagnosis', diagnosis={...retry...})`.
- 단언: `ValueError`(유형만), 큐가 비어 있다.
- 대역: `initial_failure_engine`.
- 비고: `subTest` 3건. 메시지를 보지 않으므로 세 거부의 사유를 구분해 고정하지 않는다.

### `test_retry_keeps_pending_bundles_and_never_restores_old_input` (행 819–860)
- 성질: 운영 재시도는 남은 반려 묶음(`retry_bundle_ids`)을 이어받는다. 옛 입력 작업공간을 복원하지 않고 새 작업공간에 새 입력을 만든다. 같은 처분의 재적용은 무효과다.
- 준비: 메모리 대역 `context_engine()`(실제 문맥 생산자, 저장소 autospec).
  1. `package(engine, root, 'research_work')`로 역할 입력을 만든다.
  2. `_input_artifacts('BA-plan', ...)`로 그 산출물을 만들어 저장소 `read`에 연결한다.
  3. 활동 `AY-work`와 실행 `EX-work`를 만들어 `ended`(`execution_incomplete`)까지 전이한다.
  4. 활동을 대기로 두고, `waiting_actions['AC-work']`에 `repair.retry_bundle_ids=['IN-left']`를 둔다.
  5. 처분 `OD-retry`(`pending` `retry`)를 넣는다.
  6. 옛 작업공간의 `input/submission/context.json`을 `b'damaged'`로 덮는다.
- 실행: `_complete_operational_disposition(record)`를 두 번, 이어 `_context(retry, root/'next', execution_id='EX-next')`.
- 단언:
  - 손상 파일이 그대로다(재시도 전후 두 번 확인).
  - 큐가 1개이고, 그 `repair.retry_bundle_ids == ['IN-left']`다.
  - `record.result.continuation_action_id`가 그 행동이다.
  - `AC-work`가 대기에 없다.
  - 새 문맥의 `previous_execution.id == 'EX-work'`이고, 새 작업공간에 `input/implementation/SKILL.md`가 있다.
- 대역: `context_engine`의 autospec 대역들.

## ExecutionConnections (행 863–894)

- 기반 클래스: `unittest.TestCase`. 표지·속성·도우미·훅이 없다.

### `test_retry_retains_activity_with_explicit_parent_and_profile` (행 864–881)
- 성질: 명시적 `continuation_of`를 가진 재시도 실행은 원 실행과 같은 활동·같은 실행 프로필을 쓰고, 활동 레코드를 하나로 유지한다.
- 준비: `routing_engine()`에 `DEFAULT_CONFIG`와 `build_profiles`. `_select_model`은 중간 등급 모델을 돌려주는 autospec이다.
- 실행: `_register_execution`으로 `EX-first` 등록 뒤 `ended`/`execution_incomplete`로 바꾸고, `continuation_of`를 단 행동으로 `EX-second`를 등록한다.
- 단언: 두 실행의 `owner_activity_id`가 같다. `second.continuation_of == 'EX-first'`다. `execution_profile_ref`가 같다. 활동이 1개이고 `activities.validate_activities(runtime) == []`다.
- 대역: `_select_model` autospec.

### `test_missing_explicit_continuation_does_not_infer_from_same_target` (행 883–894)
- 성질: 명시적 이어 가기가 없으면, 같은 대상을 다룬 이전 실행이 있어도 이어 가기로 추론하지 않는다.
- 준비: `routing_engine()`과 같은 대상 `KN-one`의 끝난 `formal_check` 실행 `EX-unrelated`(활동 `AY-unrelated`).
- 실행: 같은 대상의 새 `formal_check` 행동으로 `_register_execution`.
- 단언: `continuation_of`가 `None`이고, 활동이 `AY-unrelated`가 아니며, 행에 `model` 키가 없다(기계 역할).
- 대역: 없음.

## FinalBoundaryConnections (행 897–953)

- 기반 클래스: `unittest.TestCase`. 표지·속성·도우미·훅이 없다.

### `test_operational_completion_and_transfer_use_real_task_domain_validation` (행 898–924)
- 성질: 운영 검토의 과제 처분(`task_disposition`, `closed`)은 실제 과제 영역 검증을 거친다. 근거 결정이 현행이 아니면 거부되고, 현행이면 과제를 닫으면서 의무를 이전(transfer)한다.
- 준비: `record_fixtures.transfer_assessment()`의 상태에서 평가를 `closed`로, 의무 판정자를 `operational_review`로 바꾼다. 결정 `DC-1`의 `contract_sha256`을 현재 계약 해시로 맞추고, `EX-plan`을 빼고 `EX-work`와 `EX-review`를 넣는다. `routing_engine()`에 이 상태를 싣고, 저장소 `view`는 입력 스냅숏 사본을 돌려준다. `_evaluation_context`는 대역이다.
- 실행: `DC-1.source_sha256`을 `'b'*64`로 바꾼 상태로 `_complete_operational_disposition`, 상태를 되돌린 뒤 다시 호출.
- 단언: 첫 호출은 `ValueError`이고 메시지가 `'current'`에 맞는다. 이때 `TK-1`은 `closed`가 아니다. 둘째 호출 뒤 `TK-1`이 `closed`이고, `TK-2`의 마지막 의무 ID가 `'OB-inherited'`이며, `TK-2.reviews == []`다.
- 대역: 저장소 autospec, `_evaluation_context` autospec.

### `test_paused_initialization_reads_original_input_but_active_corruption_fails` (행 926–936)
- 성질: 초기화 도중 멈춘 인스턴스의 거버넌스 보기는 원 입력의 목표를 읽는다. 활성 인스턴스에 헌장이 없으면 손상으로 실패한다.
- 준비: `routing_engine()`에 `lifecycle={'state': 'paused', 'input_id': 'UC-one', ...}`, `resume_lifecycle='initializing'`, 원 입력의 `goal`을 둔다.
- 실행: `_governance()`를 세 번 부른다. 빈 거버넌스, 정책만 있는 거버넌스, 수명 주기를 `active`로 바꾼 뒤다.
- 단언: 앞 두 번은 `goal == 'Original goal'`이다. 첫 번은 `status == 'unadopted_input'`이다. 셋째는 `ValueError`이고 메시지가 `'charter'`에 맞는다.
- 대역: 없음.

### `test_operational_task_disposition_uses_authoritative_item_assessment` (행 938–953)
- 성질: 운영 처분으로 과제를 완료할 때는 검토 실행 출력의 과제 평가를 권위 있는 입력으로 `apply_task_assessments`에 넘긴다.
- 준비: `routing_engine()`에 `TK-one`(`active`), `EX-work`, `EX-review`(출력에 평가 하나)를 둔다. 저장소 `view`와 `_evaluation_context`(`{'snapshot': 'current'}`)는 대역이다.
- 실행: `do_math.engine.task_scope.apply_task_assessments`를 완료된 런타임을 돌려주는 대역으로 패치하고 `_complete_operational_disposition`.
- 단언: 패치된 함수의 셋째 위치 인자가 `[assessment]`, `execution_id == 'EX-review'`, `evaluation_context == {'snapshot': 'current'}`다. 과제가 `completed`다.
- 대역: `mock.patch('do_math.engine.task_scope.apply_task_assessments')`, 저장소 autospec, `_evaluation_context` autospec.

## OperationalRepairCandidateTests (행 956–969)

- 기반 클래스: `unittest.TestCase`. 표지·속성·도우미·훅이 없다.

### `test_operational_repair_candidate_never_mutates_files_or_publishes` (행 957–969)
- 성질: 설치 파일이 아닌 대상을 고치려는 운영 수리 후보는 스키마에서 거부된다. 파일을 바꾸거나 게시하지 않는다.
- 준비: `routing_engine()`, `_save` autospec, 끝난 `EX-target`. 제안은 `kind='repair'`, `repair_target='input/catalog/task.json'`이다.
- 실행: `type(engine).complete_repair`를 패치하고 `_apply_operational_disposition({'target': 'EX-target'}, proposal, 'EX-review')`.
- 단언: `ValueError`의 메시지가 `'repair/repair_target'`에 맞는다. `complete_repair`가 불리지 않았다. `_save`가 불리지 않았다. `operational_dispositions`가 비어 있다. 큐가 비어 있다.
- 대역: `patch.object(type(engine), 'complete_repair')`, `_save` autospec.
- 비고: 주석(행 963)은 처분 스키마가 `installation:` 수리 대상만 받는다고 적는다(`contracts.py` 191행의 패턴 `^installation:`).

## 관계

- 같은 제품 기능의 다른 층:
  - 운영 처분·설치 수리는 `test_repair_execution`, `test_diagnosed_installation_recovery`, `test_supervisor_recovery`가 다른 층에서 본다. `test_repair_execution`과 `test_supervisor_recovery`는 `foundation` 조각이고, `test_diagnosed_installation_recovery`는 `host` 조각이다.
  - 현행성 반려와 새로 고침은 `test_currentness`가 본다.
  - 제어 수신함·수용 순서는 `test_controls`, `test_control_shapes`(`lifecycle` 조각)와 겹친다.
- 픽스처 의존:
  - 하네스 계열은 `ActivatedPurposeHarness.make_active`(2단) 위에 모듈 빌드를 쌓는다.
  - 메모리 대역은 `engine_fixtures`의 `routing_engine`, `initial_failure_engine`, `context_engine`/`package`를 쓴다.
  - 실제 Git bare 엔진은 `start_repair_host`를 쓴다.
  - 기록 상태는 `record_fixtures`의 `surface_state`, `transfer_assessment`를 쓴다.
- 이 모듈에만 있는 도우미: `empty_plan`, `purpose_engine`, 세 빌드(`reviewed_task`, `parked_failed_plan`, `paused_limited_recovery`), `RecoveryHarness`의 세 메서드, `RecoveryRoutingTests.diagnose`, `RecoveryOwnershipTests`의 `runtime`/`record`. 지역 러너 `InvalidPlan`(여러 번), `RevisionRunner`, `DiagnosisRunner`, `ValidPlan`, `CapturingRunner`, `Runner`도 이 모듈에만 있다.
- 겹치거나 보완하는 시험:
  - 제어 순서 네 시험은 동일 시각, 마이크로초 차이, 역행 시계, 스레드 동시성으로 수용 순서 규칙을 넷으로 나눈다.
  - 운영자 권한 네 시험은 사용자 정지를 풀려는 재개, 금지된 제어 생성, 조건부 재개 둘, 대화 상실 정지를 다룬다.
  - 초기 진단은 `InitialDiagnosisTests`(라우팅과 스키마)와 `RecoveryBoundaryTests`(입력 자료, 종류·단계 조합, 저장, 우회 금지)가 나눠 맡는다.
  - `test_diagnosis_wait_...`의 `repair` 제안과 `OperationalRepairCandidateTests`는 같은 스키마 패턴의 양쪽에 선다. 뒤쪽은 거부를 단언하고, 앞쪽은 거부 여부를 보지 않는다.

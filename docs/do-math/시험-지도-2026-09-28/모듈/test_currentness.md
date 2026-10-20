# test_currentness

| 항목 | 값 |
|---|---|
| 조각 | `research` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_currentness.py` (474행) |
| 클래스 / 테스트 | 4 / 13 |
| 시험 대상 제품 코드 | `do_math/engine.py`의 `ResearchEngine.process_controls`(`source`·`conversation` 제어), `_receive_submission`(현행성 반려와 refresh 경로), `_context`(`recovery_materials`), `_recover_disappeared`, `_register_execution`; `do_math/lifecycle_engine.py`의 `_check_conversations`; `do_math/knowledge_engine.py`의 `_invalidate_goal_currentness`; `do_math/knowledge.py`의 `capture_basis`, `validate_basis`; `do_math/observations.py`의 `ObservationTracker`, `validate_rules`; `do_math/planning.py`의 `task_ready`; `do_math/operational_dispositions.py`의 `basis_premise_changes` |
| 사용하는 픽스처 모듈 | `purpose_fixtures`(`ActivatedPurposeHarness`, `PurposeRunner`, `common`, `CURRENTNESS_CONFIG`, `formal_fixture`, `drive_to`, `solved_instance`); `research_fixtures`(`restore_template`, `local_job_runner`, `producer_result`, `read_fixture_context`, `await_control`, `send_control`, `observe`, `write_checkpoint`, `candidate`, `contract_review`, `dispatched_launch`, `sealed_maintenance_submission`); `state_fixtures`(`active_instance`); `engine_fixtures`(`routing_engine`) |
| 격리 표지 | 없음(`test_group` 없음) |
| 시작 상태 | 대부분 2단(`make` → `make_active`, 곧 `state_fixtures.active_instance` 복사본). 계획 인용 두 시험은 2단 위에 쌓은 모듈 전용 빌드 `plan_ready_instance`. `SolvedStateCurrentnessTests`는 3단(`activated_instance`, 그 위의 `solved_instance`). 나머지 두 클래스는 1단과 메모리 엔진 대역(`routing_engine`) |

## 목적

모듈 docstring(행 1–6)은 원천·과제·지식이 바뀔 때 연구 상태의 현행성(currentness)을 시험한다고 밝히고, 대상을 차례로 든다. 원천 교체, 바뀐 과제를 인용한 계획, 중단된 작업을 그 검토에 복원하는 일, 적용 전에 교체된 운영 증거, 실시간 관찰 규칙, 대화 보호(conversation guard), 목표 의존이다. 핵심 규칙은 마지막 문장이다. 전제가 바뀌었다는 이유만으로 돌아온 제출은 수리(repair)가 아니라 새로 고침(refresh)으로 다시 보낸다. 모델 응답은 모두 픽스처다.

이 규칙의 제품 좌표는 두 곳이다. 하나는 `ResearchEngine._receive_submission`(`engine.py` 2223행)이 `integration.currentness` 사유로 돌아온 묶음을 `error_kind='currentness_changed'`로 기록하고 `refresh` 표지를 단 새 행동을 넣는 경로다. 다른 하나는 운영 처분의 근거 인용을 가르는 `operational_dispositions.basis_premise_changes`(59–69행)다. 이 함수는 입력 시점에 허용되었다가 적용 시점에 사라진 인용만 "바뀐 전제"로 인정하고, 그 사유 문자열에 `"was admissible at input; replaced before application"`을 담는다.

## 모듈 수준 요소

- 행 17: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리. 직접 실행이나 `unittest discover`에서도 `do_math`를 import하게 한다.
- `plan_ready_instance(root, shared, *, config)` (행 30–43): 이 모듈 전용 `restore_template` 빌드. `state_fixtures.active_instance`로 합성 활성 상태를 만든 뒤 `PurposeRunner`와 `formal_fixture`를 단 엔진을 `purpose_fixtures.drive_to`로 몬다. 조건 함수는 "큐 맨 앞이 `research_plan`이고 `_task_readiness`가 비어 있지 않으며 그 안에 `state == 'ready'`인 과제가 있다"이고, 단계 상한은 `drive_to`의 기본값 45다. 곧 준비와 계약 검토(요청되면 모델 평가 포함)가 끝나 계획이 과제 하나를 결정하려고 큐 머리에 선 상태다. 인스턴스 ID를 돌려준다. docstring은 `_task_readiness`가 프로세스 지역 상태라 복사본에 없으므로 시험이 먼저 `_refresh_readiness()`를 불러야 한다고 적는다. 사용처는 `CurrentnessTests._plan_citing_task_while` 하나이고, `research_fixtures` docstring의 "What to use" 목록도 이 빌드를 `test_currentness` 전용으로 적는다.
- 행 474: 직접 실행하면 `unittest.main()`으로 이 모듈의 시험을 돈다.

## CurrentnessTests (행 46–351)

- 기반 클래스: `purpose_fixtures.ActivatedPurposeHarness`(→ `PurposeHarness` → `unittest.TestCase`). 하네스의 `setUp`이 `install_adapter_fixture`로 `do_math.initialization.adapter_for`를 `FixtureAdapter`로 바꾸고, `_engine`이 `self.repo`와 `ResearchEngine(..., formal_verifier=formal_fixture)`를 만든다.
- 클래스 표지·클래스 속성: 없음.
- 시작 상태: 클래스 훅은 없고 도우미가 만든다.
- 도우미 메서드:
  - `make(**config)` (행 47–48): 하네스의 `make`를 덮어써서 `make_active(**{**CURRENTNESS_CONFIG, **config})`를 부른다. 곧 2단 `active_instance` 복사본이다. `CURRENTNESS_CONFIG`(`purpose_fixtures` 404–406행)는 `max_input_bytes=2_000_000`, `tool_review_window_seconds=60`, `self_check_response_window_seconds=5`, `scholarly_enabled=False`, `operator_enabled=False`이며, `fixture_config`의 심사자 수나 `lean_command`는 넣지 않는다. 반환은 `(engine, PurposeRunner())`다.
  - `_plan_citing_task_while(change)` (행 132–156): `plan_ready_instance` 복사본을 열고 `_refresh_readiness()`를 부른 뒤, 큐 머리가 `research_plan`임을 단언하고 준비 완료(ready) 과제 하나를 고른다. 러너의 `answer`를 감싸 계획 응답의 `used_sources`에 그 과제 ID를 덧붙인다. 그다음 `engine._receive_submission`을 `patch.object`로 감싼다. 계획의 제출을 받기 직전, 소유자 스레드에서 `change(task)`로 과제를 바꾸고 `_save()`로 게시한다. 주석(행 145–147)은 이것이 "계획의 입력이 고정된 뒤, 제출을 받기 전에 소유자가 게시한 상태 변경"이고, 소유자 스레드에서 적용해 작업자·소유자 경합을 없앤다고 설명한다. `engine.run(max_steps=1)` 한 번 뒤 `(engine, task_id, 마지막 research_plan 실행)`을 돌려준다.
  - `_review_after_checkpoint_replacement(disposition)` (행 222–266): docstring대로 실패한 시도의 운영 검토를 돌리되, 검토 입력이 고정된 뒤 대상의 체크포인트를 교체한다. 첫 러너 `FailingRunner`는 `research_preparation` 호출에서 `checkpoint.json`만 쓰고 `status='failed'`를 돌려준다. 이어 `cited`에 그 실행의 체크포인트 `artifact_ref`를 담는다. 둘째 러너 `ReviewRunner`는 입력 문맥의 `admissible_basis_refs`에 `cited`가 없으면 `AssertionError`를 던진다(픽스처 점검). 그다음 `disposition(failed, cited)`를 처분으로 제출한다. `_receive_submission`은 패치로 감싸서, `operational_review`를 받기 직전에 체크포인트를 `ARTIFACT_ROOT + new_id('BA') + '/checkpoint.json'`의 새 경로로 옮겨 저장한다. 바이트는 같고 참조만 바뀐다. 반환은 `(engine, failed, cited, review 실행)`이다.

### `test_same_source_is_idempotent_changed_source_preserves_completed_task_history` (행 50–98)
- 성질: 같은 원천을 다시 등록하면 아무것도 바뀌지 않는다. 내용이 바뀐 원천은 새 개정이 되고, 그 원천을 읽은 완료 과제는 완료 상태와 평가 내용을 유지한 채 평가만 비현행이 된다. 그 과제에 의존하는 과제는 준비 완료에서 밀려난다.
- 준비: 2단(`make()`). 복사본 루트에 `source.txt`('old')를 쓴다.
- 실행: 공개 `control(..., 'source', config={'path': ...})`와 `process_controls()`를 두 번 부른다. 이어 러너의 `answer`를 감싸 준비 후보마다 `inputs`에 `'source:source.txt'`를 넣는다. `self.drive`의 조건 함수는 "완료된 과제가 하나라도 있다"이고, 단계 상한은 기본값 45다. 그다음 하류 과제 `TK-downstream`을 직접 만든다. `candidate('Downstream')`에 의존 `[task id]`를 주고, `seal_contract_review`로 봉인한 계약 승인을 붙인다. 원천을 'new'로 바꿔 다시 `source` 제어를 보낸다.
- 단언: 두 번째 등록 뒤에도 `instance['sources'][0]`이 첫 등록 사본과 같다(멱등). 원천 교체 전에는 하류 과제가 `task_ready(...)['state'] == 'ready'`다. 이 판정은 `goal_status`를 `'unsolved'`로 바꾼 인스턴스 사본으로 한다. 교체 뒤 완료 과제는 다음을 만족한다.
  - `status`가 여전히 `'completed'`다.
  - `assessment.decision`과 `item_dispositions`가 보존된다.
  - `assessment.current`가 거짓이다.
  - `invalidated_reason`에 소문자 `'source content changed'`가 있다.

  원천의 `revision`은 2다. 하류 과제는 `'not_ready'`이고 첫 오류에 `'blocked dependencies'`가 있다. `engine.check()`의 오류 중 완료 과제 ID로 시작하는 것이 없다.
- 대역: `PurposeRunner`(`answer` 감싸기). 호출마다 `local_job_runner`가 실제 Windows Job 자식을 띄운다. 컴파일러 대역은 `formal_fixture`, 어댑터 대역은 `FixtureAdapter`다.
- 비고: 하류 과제는 공개 경로로 만든 것이 아니다. 시험은 이 레코드를 `engine.runtime['tasks']`에 넣지도 않는다. 지역 사전으로 만들어 `task_ready(downstream, ...)`에 직접 넘길 뿐이다(행 73–81, 95). 주석(행 76)은 저장 레코드에는 후보의 `revises_task_id`를 두지 않으므로 뺀다고 적는다. 실제 외부 자원은 Git 자식 프로세스와 Windows Job이다.

### `test_graceful_output_on_changed_source_is_preserved_but_not_accepted` (행 100–130)
- 성질: 실행 도중 입력 원천이 바뀌면, 정상 종료한 출력이라도 받아들이지 않고 보존한다. 그 반려는 출력 수리 한도가 0이어도 한 번 새로 고침된다.
- 준비: 2단(`make(max_output_repairs=0)`). `basis.txt`('old')를 원천으로 등록한다.
- 실행: 지역 러너 `ChangingRunner`(`local_job_runner`)를 쓴다. 이 러너는 호출 중에 원천을 'new'로 바꾸고, 공개 `source` 제어를 보낸 뒤 `await_control`로 소유자 루프가 그 제어를 적용할 때까지 기다린다. 그다음 `partial.txt`를 쓰고, `used_sources=['basis.txt']`에 후보 없는 준비 출력을 `producer_result`로 제출한다. 엔진은 `engine.run(max_steps=1)`로 한 번 돈다.
- 단언: `research_preparation` 실행의 `outcome == 'execution_incomplete'`, `error_kind == 'currentness_changed'`다. `integration_result.issues`에 `rule_id == 'integration.currentness'`이면서 메시지에 `'source'`가 있는 행이 있다. `runtime['cycles'] == 0`이다. 큐에서 `refresh.execution_id`가 그 실행인 행동이 정확히 1개이고, 거기에 `repair` 키가 없다. 원 행동 ID가 `waiting_actions`에 없다. `output_files`의 `partial.txt`를 저장소에서 읽으면 `b'The old input was read.'`다.
- 대역: `ChangingRunner`(스크립트 러너, 실제 Windows Job). `await_control`은 상한 60초로 폴링한다.
- 비고: 주석(행 124)은 "출력 수리를 허용하지 않아도 바뀐 전제는 한 번 새로 고친다"고 적는다. 러너 스레드와 소유자 루프가 실제로 동시에 도는 시험이다.

### `test_cited_task_lifecycle_change_during_plan_does_not_reject_the_plan` (행 158–166)
- 성질: 계획이 인용한 과제에 수명 주기 정보만 바뀌었으면 계획을 반려하지 않는다.
- 준비: `_plan_citing_task_while` 절 참조(`plan_ready_instance`, 2단 위의 빌드). 바꾸는 필드는 `deferred_reason`과 `reviews`(항목 `{'note': 'concurrent'}` 추가)다.
- 실행: 도우미 안의 `engine.run(max_steps=1)`.
- 단언: 계획 실행의 `outcome == 'output_accepted'`다. 봉인된 출력(`submission_intent.output_ref`)의 `used_sources`에 과제 ID가 있다. `integration_result.status == 'accepted'`다. 과제 `status == 'active'`이고, 큐에 그 과제를 대상으로 한 `research_work`가 있다.
- 대역: `PurposeRunner`(응답 감싸기), `_receive_submission`의 `patch.object`.

### `test_cited_task_contract_change_during_plan_rejects_the_plan` (행 168–176)
- 성질: 계획이 인용한 과제의 계약 내용이 바뀌면 계획을 현행성 사유로 반려하고 작업을 넣지 않는다.
- 준비: `_plan_citing_task_while` 절 참조. 바꾸는 것은 `scope.included`에 `'A revised domain'`을 더하는 계약 변경이다.
- 실행: 도우미 안의 `engine.run(max_steps=1)`.
- 단언: `outcome == 'execution_incomplete'`, `error_kind == 'currentness_changed'`다. 이슈 중에 `rule_id == 'integration.currentness'`이고 메시지에 과제 ID와 `'contract_sha256'`이 모두 있는 행이 있다. 그 과제를 대상으로 한 `research_work`가 큐에 없다.
- 대역: 앞 시험과 같다.
- 비고: 앞 시험과 짝을 이룬다. 둘의 차이는 바뀐 필드가 계약 해시에 드는지뿐이다.

### `test_failed_execution_materials_are_restored_for_its_operational_review` (행 178–220)
- 성질: 실패한 실행의 결과원, 체크포인트, 출력 파일이 그 운영 검토의 입력 작업공간에 해시·크기·저장 바이트가 일치하도록 복원된다. 별도로 보존된 활동 결과가 있으면 결과원으로 그것을 쓴다.
- 준비: 2단(`make()`). 지역 러너 `FailingRunner`는 `partial.txt`와 `checkpoint.json`(`progress_state='blocked'`)을 쓰고 `status='failed'`로 끝난다.
- 실행: `engine.run(max_steps=1)`로 준비 실행을 실패시킨다. 큐의 `operational_review` 행동에 대해 `engine._context(review, 새 작업공간)`을 부른다. 이어 실행의 `result_ref`를 `runtime/artifacts/BA-activity-result/diagnostic.json`으로 바꾸고, 그 바이트와 함께 `_save`한 뒤 `_context`를 다시 부른다.
- 단언: `recovery_materials`가 다음을 만족한다.
  - `execution_id`가 실패 실행이다.
  - `(result_kind, final_result_status) == ('execution_result', 'available')`이다.
  - `checkpoint`가 `operational_evidence.checkpoint`와 같고, 그 `sha256`이 `runtime['checkpoints'][id]`와 같다.
  - `checkpoint` 안에 `checkpoint` 키가 없다(본문 중첩 금지).

  `result_source`, `checkpoint_source`, 각 `output_files`마다 로컬 파일의 sha256·바이트 수·저장소 판독(`snapshot` 기준)이 일치한다. 복원된 `partial.txt`의 내용은 `b'Reusable partial result.'`다. 두 번째 문맥에서는 결과원 파일 내용이 새 활동 결과 바이트와 같고, 결과원과 체크포인트원의 `local_path`가 다르다.
- 대역: `FailingRunner`(실제 Windows Job).

### `test_operational_basis_replaced_after_input_is_refreshed_without_output_repair` (행 268–278)
- 성질: 운영 검토가 입력 시점에 허용된 체크포인트를 인용했는데 적용 전에 그 체크포인트가 교체되었으면, 제출은 생산자 오류가 아니라 바뀐 전제로 새로 고침된다.
- 준비: `_review_after_checkpoint_replacement` 절 참조. 처분은 `kind='continue'`, `basis_refs=[target, checkpoint]`, `next_owner='engine'`이다.
- 실행: 도우미 안의 두 `run(max_steps=1)`.
- 단언: 검토 실행의 `error_kind == 'currentness_changed'`다. `currentness_changes` 중 사유에 인용 참조와 `'admissible at input'`이 모두 있는 행이 있다. 이 문구는 `basis_premise_changes`의 사유 문자열에서 온다. 대상 실행에 대한 `operational_review` 후속 행동이 정확히 하나이고, 그 `refresh.execution_id`가 검토 실행이다. 그 행동에 `repair` 키가 없다(메시지: "A changed premise does not spend an output repair"). 원 행동이 `waiting_actions`에 없다.
- 대역: `FailingRunner`, `ReviewRunner`(둘 다 실제 Windows Job), `_receive_submission` 패치.

### `test_replaced_operational_basis_with_another_application_error_stays_a_producer_repair` (행 280–290)
- 성질: 체크포인트가 교체되었더라도 적용 오류가 따로 있으면 그 제출은 생산자 수리로 간다. 바뀐 전제가 다른 결함을 가리지 않는다.
- 준비: 같은 도우미. 처분은 `kind='repair'`, `repair_target='installation:missing.py'`(존재하지 않는 설치 파일), `meaning_preserving=True`다.
- 실행: 도우미 안의 두 `run(max_steps=1)`.
- 단언: `error_kind == 'output_contract'`다. 이슈 메시지 중 `'installation repair target'`을 담은 것이 있다. 제품 `repair_execution.py` 64행의 "installation repair target must name an existing file inside the installed skill"에 대응한다. 후속 `operational_review`가 하나이고 그 `repair.execution_id`가 검토 실행이다. 그 행동에 `refresh` 키가 없다.
- 대역: 앞 시험과 같다.
- 비고: 앞 시험과 짝이다. 전제 변화와 다른 적용 오류가 함께 있을 때 수리 쪽이 이긴다는 경계를 고정한다.

### `test_recovery_captures_parent_and_inline_child_without_losing_action` (행 292–329)
- 성질: 사라진 실행을 복구할 때 부모와 인라인 자식이 모두 끝나고 출력이 보존된다. 부모의 행동은 버려지지 않고 대기로 옮겨지며, 부모의 운영 검토가 큐에 들어간다.
- 준비: 2단(`make()`). 부모 `EX-parent`(행동 `AC-fixture`, `research_preparation`)와 인라인 자식 `EX-inline`(`operational_review`, 부모 대상)을 `_register_execution`으로 `running` 등록한다. 각 실행에 다음을 붙인다.
  - `dispatched_launch`로 만든 발사 표.
  - 입장한 발사를 흉내 낸 `capacity`(`process.job_name`, `local_termination='unknown'`).
  - 작업공간의 `partial.txt`(내용은 실행 ID).

  `runtime`을 `status='running'`, `queue=[action]`으로 두고 저장한다.
- 실행: `windows_job.named_job_empty`와 `windows_job.owner_ended`를 `True`로 패치하고, `store.writer_lock()` 안에서 `engine._recover_disappeared()`를 부른다. 이어 `{'role': 'operational_review', 'target': 'EX-parent'}`의 `_context`를 만든다.
- 단언:
  - 끝나지 않은 실행이 없고 `runtime['recoveries']`가 비어 있지 않다.
  - `waiting_actions['AC-fixture'].execution_id == 'EX-parent'`다.
  - 큐에 `EX-parent` 대상 `operational_review`가 있다.
  - 두 실행 모두 `status == 'ended'`이고, 첫 출력 파일을 저장소에서 읽으면 실행 ID 바이트다.
  - 검토 문맥의 `recovery_materials`는 `result_kind='checkpoint_recovery'`, `final_result_status='not_produced'`이고, `result_source`와 `checkpoint_source`가 같으며, 그 로컬 파일이 존재한다.
- 대역: `do_math.windows_job.named_job_empty`와 `do_math.windows_job.owner_ended`의 `mock.patch`. 주석(행 309–310)은 이 픽스처가 프로세스를 띄우지 않았으므로 종료 관찰을 명시적으로 주며, 알 수 없는 실제 프로세스는 해제되지 않아야 한다고 적는다.

### `test_live_rules_repeat_exact_thresholds_and_preserve_last_valid_update` (행 331–351)
- 성질: 카운터 관찰 규칙은 문턱(threshold)과 반복 간격(repeat interval)의 정확한 경계마다 자기 점검을 한 번 요구한다. 같은 카운터에서는 다시 요구하지 않는다. 불리언 문턱은 규칙 검증에서 거부된다.
- 준비: 1단. 임시 폴더 하나와 규칙 `steps`를 쓴다. 규칙은 `counter_gte`, `attempts` 카운터, 문턱 2, 반복 간격 2, 필요 증거 `EV-iteration`이다. `ObservationTracker('EX', folder, {...}, clock=lambda: clock[0])`로 시계를 주입한다(값 0 고정).
- 실행: `write_checkpoint`로 카운터를 2 → 2(주장만 다름) → 4로 바꾸면서, 매번 `observe(tracker, {'type': 'tick'})`를 부른다. 이어 `validate_rules`에 `threshold: True`인 규칙을 넣는다.
- 단언: 첫 틱의 `self_check_due` 행 `due[0].boundary == 2`다. 같은 카운터의 둘째 틱에는 `self_check_due`가 없다. 카운터 4의 틱에서는 `boundary == 4`다. `tracker.rules`가 입력 규칙과 같다. `validate_rules`가 `ValueError`를 던진다(유형만 보고 메시지는 보지 않는다).
- 대역: 시계 주입(`clock` 리스트). 엔진은 없다.
- 비고: 이 클래스의 다른 시험과 달리 하네스 상태를 쓰지 않는 순수 단위 시험이다. 이름의 "preserve last valid update"는, 시험이 추적기에 새 규칙 갱신을 시도하지 않으므로 코드로는 확인되지 않는다. 단언은 추적기의 규칙이 처음 준 값과 같다는 것과 불리언 문턱이 검증에서 거부된다는 것뿐이다.

## SolvedStateCurrentnessTests (행 354–411)

- 기반 클래스: `ActivatedPurposeHarness`.
- docstring: 두 시험이 모두 템플릿 복사본에서 출발한다고 적는다. 하나는 공개 활성화이고, 다른 하나는 그 뒤의 실제 해결이다.
- 클래스 표지·속성·도우미: 없음.

### `test_live_conversation_guard_expires_without_new_scheduler_activity` (행 357–377)
- 성질: 대화 보호의 임대(lease)가 만료되면 스케줄러 활동이 없어도 대화 상실로 판정한다. 연결 정책 `pause`에 따라 인스턴스를 멈추고, 실행 중인 실행에 정지를 요청한다. 이 판정은 한 번만 기록된다.
- 준비: 3단(`make()` → `activated_instance`, `goal=GOAL`, `fixture_config()`). `send_control`로 `conversation` 제어(`attach`, `id='C'`, 세대 1, `lease_seconds=3600`, `disconnect_policy='pause'`)를 보낸다. 큐의 `research_preparation` 행동으로 `running` 실행을 등록한다.
- 실행: `engine.lifecycle_clock`을 임대 만료 시각 1초 뒤로 고정한다. `lifecycle_monotonic`은 0.0으로 두고 `_clock_anchor=None`으로 두 시계를 한 기준점에 맞춘다. 그다음 `_check_conversations()`를 두 번 부른다.
- 단언: 첫 호출은 `True`다. `runtime['status'] == 'paused'`이고 실행의 `stop_requested == 'conversation_lost'`다. 대화의 `last_heartbeat_at`은 이전과 같다. 이 판정은 심장박동을 만들어 내지 않는다. 둘째 호출은 `False`다. `conversation_lost` 사건은 1개다.
- 대역: 시계 주입(`lifecycle_clock`, `lifecycle_monotonic`). 러너는 불리지 않는다.
- 비고: docstring은 "the real solution" 템플릿도 언급하지만, 이 시험은 공개 활성화 템플릿만 쓴다. 제품 판정은 `lifecycle_engine.py` 510–517행이다.

### `test_goal_dependency_detects_changed_relation_endpoint_even_when_proof_record_is_unchanged` (행 379–411)
- 성질: 목표 판정이 전제로 쓴 관계 끝점(endpoint)의 해설이 바뀌면, 증명 레코드가 그대로여도 목표 판정은 비현행이 된다. 목표는 미해결로, 런타임은 `ready`로 돌아간다. 비현행이 된 판정도 저장 계약을 통과한다.
- 준비: 3단 위의 빌드. `restore_template(solved_instance, criteria=None)`은 공개 활성화를 `drive_to`(조건: `goal_status == 'mathematically_solved'`, 상한 45)로 해결까지 몬 상태다. `import_candidate`로 `question` 종류의 끝점 둘('left endpoint', 'right endpoint')을 지식에 넣는다. `capture_basis`로 기반 세 개를 잡는다. 증명만, 끝점과 그 해설, 그리고 둘 다다. 셋째를 마지막 목표 판정의 `record_basis`로 덮어쓴다. 그다음 오른쪽 끝점 해설의 첫 항목 텍스트를 바꾼다.
- 실행: `validate_basis`를 두 기반에 대해 부르고, `engine._invalidate_goal_currentness()`를 부른다.
- 단언:
  - 증명 기반은 `valid`, 끝점 기반은 `valid`가 아니다.
  - 판정의 `current`가 거짓이다.
  - `state_contract.default_state_contract().family('research', 'goal_judgments').checker`로 `validate_record`가 판정을 통과시킨다(예외 없음).
  - `goal_status == 'unsolved'`, `runtime['status'] == 'ready'`다.
- 대역: 없음. 해결 상태는 `PurposeRunner`와 `formal_fixture`로 만든 템플릿이다.
- 비고: 끝점 두 개를 목표 판정의 기반에 넣는 일은 시험이 직접 한다. 주석(행 396)은 "목표 평가자가 두 끝점을 명시적으로 전제로 썼다"는 상황을 만든다고 적는다.

## OperationalBasisPremiseTests (행 414–422)

- 기반 클래스: `unittest.TestCase`. 표지·속성·도우미·훅이 없다.

### `test_only_evidence_admitted_at_input_can_become_a_changed_premise` (행 415–422)
- 성질: 인용 중 입력 시점에 허용되었다가 지금 사라진 것만 바뀐 전제다. 입력에 없던 것을 인용했으면 전제 변화가 아니라 생산자 오류로 남는다.
- 준비: 1단. `at_input=['EX-target','BA-old']`, `current=['EX-target','BA-new']`.
- 실행: `operational_dispositions.basis_premise_changes`를 세 번 부른다.
- 단언: 첫째, `basis_refs=['EX-target','BA-old']`이면 결과 ID가 `['BA-old']`다. 둘째, `['BA-old','OF-never-supplied']`이면 입력에 없던 인용이 섞여 `[]`이다. 메시지는 "A citation outside the input stays a producer error"다. 셋째, `['EX-target']`이면 `[]`이다.
- 대역: 없음.

## CurrentnessReturnRoutingTests (행 425–471)

- 기반 클래스: `unittest.TestCase`. 표지·속성·도우미·훅이 없다.

### `test_currentness_return_beside_an_accepted_bundle_is_refreshed_not_repaired` (행 426–471)
- 성질: 분할 응답에서 한 묶음은 수용되고 다른 묶음이 바뀐 전제로 돌아온 경우(결과 `status='partial'`)를 다룬다. 수신기는 상태값이 아니라 반려 이슈의 종류로 경로를 정하므로, 이 제출을 수리하지 않고 새로 고친다. 일반 과제 영수 기록도 다시 하지 않는다.
- 준비: 네 단 밖, 메모리 엔진 대역 `routing_engine()`이다. `sealed_maintenance_submission`이 임시 작업공간에 실제 중앙 봉인 바이트를 만든다. 제출 의도에 `extensions_ref`와 `check_ref`를 붙인다. `store`는 `create_autospec(ResearchRepository)`이고, `read`는 봉인 산출물 사전에서 읽는다. `git_dir`은 무작위 문자열, `head`는 `'fixture-snapshot'`이다. 실행 `EX-work`는 `status='stopping'`이고 `submission_receipt`가 수용된 상태다.
- 실행: `_apply_submission_bundles`를 autospec 대역으로 바꾼다. 이 대역은 `status='partial'`, `retry_bundle_ids=['IN-two']`와 두 묶음을 돌려준다. `IN-one`은 수용, `IN-two`는 `integration.currentness` 이슈로 반려되고 `next_owner='producer'`다. `_record_task_receipt`도 autospec 대역이다. 그 상태에서 `engine._receive_submission(action, {}, 'EX-work', context, schema, workspace)`를 부른다.
- 단언: 실행의 `error_kind == 'currentness_changed'`다. `currentness_changes`의 `integration_id` 목록이 `['IN-two']`다. 큐는 행동 하나이고, 그 `refresh.execution_id == 'EX-work'`이며 `repair` 키가 없다. 원 행동 ID가 `waiting_actions`에 없다. `_record_task_receipt.assert_not_called()`다.
- 대역: `create_autospec(ResearchRepository, instance=True)`, `_apply_submission_bundles`와 `_record_task_receipt`의 autospec 대역.
- 비고: 긴 주석(행 427–430)이 설계 의도를 밝힌다. `partial`은 일부 묶음이 수용되었다는 뜻일 뿐이고 새로 고침과 수리 사이에서 같으므로, 수신기는 `integration.failure_kind`로 반려 이슈를 보고 경로를 정한다.

## 관계

- 같은 제품 기능의 다른 층:
  - 원천 등록 제어와 현행성 반려: 공개 흐름 쪽은 `test_purpose_engine`의 `test_knowledge_currentness_loss_and_revision_recover_through_fresh_review`가 지식 무효화·개정을 끝까지 몰아 본다.
  - 운영 처분의 수리·재시도 경로: `test_research_recovery`가 넓게 다룬다.
  - 관찰 규칙과 자기 점검: `test_live_observation`, `test_observation_admission`(`lifecycle` 조각)에서 다른 층으로 다룬다.
- 픽스처 의존: `ActivatedPurposeHarness.make_active`(2단)와 `make`(3단)를 쓴다. `purpose_fixtures.solved_instance`와 `drive_to`, `research_fixtures`의 러너 도우미(`local_job_runner`, `producer_result`, `read_fixture_context`, `await_control`), 관찰 도우미(`observe`, `write_checkpoint`), `engine_fixtures.routing_engine`에도 기댄다. `CURRENTNESS_CONFIG`는 이 모듈과 `test_checkpoint_persistence`만 쓴다(`consumers.json`).
- 이 모듈에만 있는 도우미: `plan_ready_instance`, `_plan_citing_task_while`, `_review_after_checkpoint_replacement`. 지역 러너 `ChangingRunner`, `FailingRunner`(두 번), `ReviewRunner`도 이 모듈에만 있다.
- 겹치거나 보완하는 시험:
  - 새로 고침이냐 수리냐의 경로 선택을 세 층에서 본다. 공개 엔진 층(`test_graceful_output_...`), 운영 검토 층(`test_operational_basis_replaced_...` / `test_replaced_operational_basis_...` 짝), 수신기 단위 층(`test_currentness_return_beside_...`)이다.
  - 전제 판정의 순수 함수는 `OperationalBasisPremiseTests`가 따로 고정한다.
  - 계획 인용 두 시험은 같은 도우미로 수명 주기 변경과 계약 변경을 나눈다.

# test_repetition

| 항목 | 값 |
|---|---|
| 조각 | `review` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_repetition.py` (321행) |
| 클래스 / 테스트 | 2 / 10 |
| 시험 대상 제품 코드 | `do_math/revisions.py`의 `bind_repetition_bases`, `record_execution_outcome`, `record_repetition`, `record_import_rework`, `import_rework`, `action_repetition_waits`, `action_scope`, `repetition_hold`; `do_math/task_contracts.py`의 `repetition_lineages`; `do_math/governance.py`의 `apply_decision`(`repetition_continue`); `do_math/planning.py`의 `exhaustion_state`, `schedule_reconsideration`, `governance_revisions`; `do_math/contracts.py`의 `action_schema`; `do_math/submission.py`의 `_payload_issues`, `install_tools`; `do_math/integration.py`의 `failure_kind`, `issue`; `do_math/activities.py`의 `continue_activity`, `wait_for`; `do_math/engine.py`의 `_register_execution`, `_collect_submitted_result`, `_receive_submission`, `_complete_operational_disposition`, `process_controls`, `control` |
| 사용하는 픽스처 모듈 | `engine_fixtures`(`routing_engine`, `intent_import`, `intent_verdict`, `native_result`); `purpose_fixtures`(`ActivatedPurposeHarness`); `research_fixtures`(`candidate`); `runner_fixtures`(`ScriptedRunner`) |
| 격리 표지 | 없음(`test_group` 미사용) |
| 시작 상태 | `RepetitionLineageTests`: 메모리 엔진 `routing_engine` 또는 1단(사전 입력과 순수 함수). `RepetitionEngineTests`: 2단(`ActivatedPurposeHarness.make_active`) |

## 목적

모듈 docstring은 반복 계보(repetition lineages)를 시험한다고 밝힌다. 곧 반복되는 생성, 재작업, 수신자 실패를 어떻게 세고, 붙잡아 두고(hold), 풀어 주는지를 본다. 제품 좌표는 `do_math.revisions`다. docstring은 또 모델 답은 픽스처이고, 영수증 적용, 활동 전이, 대기열 후속은 제품의 것이라고 밝힌다.

계보는 행동의 `repetition_bases`에 묶인 키로 식별된다. 이 모듈이 다루는 계보는 넷이다. `exhaustion_empty`는 후보 없는 준비의 반복, `import_rework`는 입력 해석의 재작성, `selection_failure`는 계획 수신 실패, `contract_revision`은 계약 개정이다. 반복 수가 구성의 한도에 이르면 사용자 소유의 보류(`repetition_hold`)가 생긴다. 행동은 `action_repetition_waits`가 비지 않는 동안 기다린다. 사용자 결정 `repetition_continue`가 정확한 보류를 풀면 계보 수가 0이 된다.

## 모듈 수준 요소

- 행 15: `sys.path.insert(0, ...)`로 스킬의 `scripts/` 폴더를 경로 앞에 넣는 공통 머리다.
- 행 16–22: 제품과 픽스처 import. 모듈 함수, 상수, `setUpModule`은 없다.
- 행 320–321: 직접 실행하면 `unittest.main()`을 부른다.

## RepetitionLineageTests (행 25–144)

`unittest.TestCase`를 상속하고 표지, 속성, 훅, 도우미가 없다. 각 테스트가 스스로 상태를 만든다. `routing_engine()`은 `bare_engine` 위에 거버넌스를 시작한 인스턴스(`RI-test`)와 빈 런타임을 둔 메모리 엔진이다. 저장소는 `NoRepository`이고, `_bind_revision_action`, `_cancel_selected_revision_targets`, `_record_output_questions`는 autospec 대역이다.

### `test_continue_after_successful_empty_preparation_creates_its_missing_request` (행 26–45)
- 성질: 성공했지만 후보가 없던 준비가 한도에 걸려 보류되었을 때, 계속 결정은 대기열에 없던 허용 행동을 새로 만든다. 그 행동은 기다리지 않는다.
- 준비: `routing_engine()`, `exhaustion_empty_limit=1`, 사용자 출처 `UI-source`. 행동 `AC-original`(`research_preparation`)에 `bind_repetition_bases`로 계보 키를 묶는다. 수락된 실행 `EX-empty`를 두고 `record_execution_outcome(..., {'summary': 'No candidate'}, 'EX-empty', accepted=True)`로 빈 결과를 기록한다. 허용 행동 `AC-next`(같은 `exhaustion_empty` 키)와 결정 `repetition_continue`(`hold_event_ref='EX-empty'`)를 만든다.
- 실행: `governance.apply_decision(instance, runtime, change, source_ref='UI-source')`.
- 단언: 반환된 런타임의 대기열 ID 목록이 `['AC-next']`다. 그 행동에 대해 `action_repetition_waits`가 거짓이다. `action_scope(queue[0])`이 허용 행동과 같다.
- 대역: `routing_engine`의 autospec 대역 셋.

### `test_supplement_does_not_increment_or_reset_empty_generation` (행 47–67)
- 성질: 보충 준비(평가 대상이나 관측 규칙 대상을 가진 준비)는 빈 생성 계보를 늘리지도 초기화하지도 않는다. 보충 준비는 `repetition_bases`에 `exhaustion_empty` 키가 묶여 있어도 그 보류로는 기다리지 않고, 관측 규칙 대상 과제의 `contract_revision` 보류로 기다린다(제품 `revisions.action_repetition_waits`가 `model_policy.preparation_only` 행동의 `exhaustion_empty` 키를 빼고 대상마다 계보를 더한다).
- 준비: 1단 사전 입력(`instance={'id': 'RI', 'config': {}}`와 빈 런타임). `record_repetition`으로 `exhaustion_empty`/`basis` 반복 하나를 기록하고 이력 사본을 떠 둔다.
- 실행: `assessment_targets`와 `observation_rule_targets` 각각을 가진 준비 행동으로 `record_execution_outcome(..., accepted=True)`. 이어 이력에 보류 둘을 직접 더하면서 `action_repetition_waits`를 두 번 부른다. 하나는 `exhaustion_empty`/`basis`(소유자 사용자), 다른 하나는 과제 `TK`에 대한 `contract_revision`이다.
- 단언: 보충 두 번 뒤 이력이 사본과 같다. `repetition_bases={'exhaustion_empty': 'basis'}`이고 `observation_rule_targets={}`인 행동은 보류가 있어도 기다리지 않는다. `observation_rule_targets={'TK': {}}`로 바꾸면 기다림 목록의 계보가 `['contract_revision']` 하나다.
- 대역: 없음.
- 비고: 두 번째 단언은 보충 행동이 `exhaustion_empty` 보류로는 기다리지 않는다는 것을 보인다. 이름의 "초기화하지 않는다"는 이력 불변으로 확인된다.

### `test_real_intent_rework_producer_keeps_original_lineage` (행 69–96)
- 성질: 실제 입력 해석 재작업의 생산자는 원래 계보를 이어받는다. 같은 재작업을 두 번 기록해도 한 번만 센다. 검사 단계와 무관한 대상의 행동은 그 계보에 걸리지 않는다.
- 준비: `routing_engine()`. `intent_import(engine)`으로 입력 `UC-input`의 해석 하나를 만들고 검사 행동을 받는다. `_apply(check_action, intent_verdict(bundle, 'revision_required', False), 'EX-check')`로 재작업을 요구한다. 대기열의 `stage='interpret'` 재작업 행동에 계보를 묶고, 실행 `EX-rework`를 둔다.
- 실행: `record_import_rework`를 두 번 부르고 `repetition_lineages`를 읽는다. `repetition_bases`를 뺀 재시도 행동 `AC-next`(`previous_import_id='IM-next'`)에 다시 `bind_repetition_bases`를 한다. 검사 행동 `{..., 'stage': 'check', 'continuation_of': 'EX-check'}`을 만든다. `import_rework_limit=1`로 두고 두 번째 재작성 반복을 `record_repetition`으로 기록한다. 대상을 `UC-unrelated`로 바꾼 행동에도 계보를 묶는다.
- 단언: `import_rework` 수가 1이다. 재시도 행동의 `repetition_bases`가 원래 재작업의 것과 같다. `import_rework(runtime, check)`가 거짓이다. 한도 도달 뒤 재작업 사본(`later`)은 기다리고, 검사 행동은 기다리지 않으며, 무관한 대상의 행동도 기다리지 않는다.
- 대역: `routing_engine`의 autospec 대역 셋. `intent_import`와 `intent_verdict`는 스크립트된 해석·검사 출력이다.

### `test_receiver_failure_categories_count_once_and_success_ends_streak` (행 98–115)
- 성질: 수신자 실패 가운데 선택 실패로 분류되는 것만 계획 계보를 늘리고, 같은 실행은 한 번만 센다. 다른 종류의 실패는 세지 않으며, 성공 하나가 연속 실패를 끝낸다.
- 준비: 1단 사전 입력. `research_plan` 행동(`selection_failure` 키 `basis`).
- 실행: 규칙 `schema.required`, `submission.parse`, `integration.application` 각각으로 `integration.failure_kind([integration.issue(rule, 'output', ...)])`를 실행의 `error_kind`로 두고, `record_execution_outcome(..., accepted=False)`를 두 번씩 부른다. 이어 `error_kind`가 `currentness_changed`, `publication_failure`, `input_failure`인 실행을 한 번씩 기록한다. 끝으로 수락된 `EX-good`을 기록한다.
- 단언: 첫 묶음 뒤 `selection_failure` 수가 3이다(실행마다 두 번 기록해도 한 번). 둘째 묶음 뒤에도 3이다. 성공 뒤 0이다.
- 대역: 없음.
- 비고: 이슈 메시지는 `'message deliberately contains no classification hints'`다. 분류가 메시지가 아니라 규칙 ID로 이루어져야 함을 전제한다.

### `test_generation_time_uses_fixed_machine_observation_and_excludes_supplement` (행 117–130)
- 성질: 빈 생성의 재생성 시각(`regenerate_after`)은 필수 필드이고, 기계 관측 시각보다 엄격히 뒤인 시간대 있는 시각이어야 한다. 보충 준비의 스키마에는 그 필드가 없다.
- 준비: 1단. `research_preparation` 행동의 `contracts.action_schema`, `assessment_targets`를 가진 보충 행동의 스키마, `observed_at='2026-09-23T00:00:00Z'`인 문맥, 후보 없는 출력.
- 실행: 임시 폴더에서 세 시각으로 `submission._payload_issues`를 부른다.
- 단언: 기본 스키마의 `required`에 `regenerate_after`가 있다. 보충 스키마의 `properties`에는 없다. `rule_id='submission.regeneration_time'` 문제는 관측보다 한 시간 뒤(`2026-09-23T01:00:00Z`)에는 없고, 한 시간 앞(`2026-09-22T23:00:00Z`)과 시간대 없는 시각(`2026-09-23T01:00:00`)에는 있다.
- 대역: 없음.
- 비고: 제품 규칙은 `revisions.regeneration_time_valid`의 docstring "A regeneration time must be a zoned time strictly after the machine observation."이다.

### `test_generation_time_is_checked_only_when_no_candidate_is_proposed` (행 132–144)
- 성질: 재생성 시각은 후보를 하나도 내지 않을 때만 검사된다.
- 준비: 1단. `research_fixtures.candidate('one')`을 함수 안에서 import해 후보 하나를 가진 출력과 빈 출력을 만든다.
- 실행: `(후보 있음, 시각 None)`, `(후보 있음, 관측보다 앞선 시각)`, `(빈 출력, 시각 None)` 세 경우로 `_payload_issues`.
- 단언: `path='output/regenerate_after'` 문제는 앞의 두 경우에 없고, 빈 출력에서 시각이 `None`일 때만 있다.
- 대역: 없음.

## RepetitionEngineTests (행 147–317)

기반은 `purpose_fixtures.ActivatedPurposeHarness`다. 그 `setUp`이 `adapter_for`를 `FixtureAdapter`로 패치한다. 네 테스트는 `self.make_active(**config)`로 시작한다. 이는 `restore_template(state_fixtures.active_instance, config=...)`의 사본(2단)으로, 실제 Git 저장소 위에 새 `ResearchEngine`을 만든다(`self.repo`, `self.root`가 설정된다). 클래스 표지와 속성은 없다.

- `seed_plan(engine)` (행 148–158): 대기열을 비우고 `research_plan`을 넣는다. 그 행동으로 실행을 `_register_execution`하고, `end_preparation(..., stage='context', cancelled=False)`로 준비 단계에서 실패로 끝낸다. 행동을 대기열에서 빼고, 소유 활동을 `activities.wait_for(..., next_owner='operational_review')`로 대기시킨다. 그 실행을 돌려준다. 운영 검토를 기다리는 "원래 실패한 계획"의 상태다.

### `test_empty_preparation_preserves_machine_time_and_opens_one_due_regeneration` (행 160–181)
- 성질: 후보 없는 준비는 기계 관측 시각을 영수증에 보존한다. 재생성 시각 전에는 재생성 가드로 멈추고, 그 시각에는 재고를 두 번 예약해도 준비를 하나만 연다.
- 준비: 2단 사본. `runner_fixtures.ScriptedRunner`를 함수 안에서 import한다. 대기열을 비우고 `research_preparation`을 넣은 뒤 `ScriptedRunner(preparation_candidates=[])`를 러너로 두고 저장한다.
- 실행: `engine.run(max_steps=1)`. 이어 런타임 사본에 대해 재생성 시각 1초 전의 `planning.exhaustion_state`와, 그 시각의 `planning.schedule_reconsideration` 두 번을 부른다.
- 단언: 이력의 `task_repetition`/`exhaustion_empty` 영수증이 가리키는 실행의 `outcome`이 `'output_accepted'`다. 영수증 `observed_at`이 실행의 `observed_at`과 같다. 1초 전 상태의 `reasons`가 `['regeneration_guard']`다. 두 번 예약한 뒤 `research_preparation`이 1개다.
- 대역: `ScriptedRunner`.
- 비고: `ScriptedRunner.run`은 `local_job_runner`로 감싸져 실제 Windows Job 안에서 `python -c "import time; time.sleep(600)"` 자식 프로세스를 띄웠다가 끝낸다. 실제 Git 저장소를 쓴다.

### `test_native_plan_failures_reach_receiver_counter_through_preserved_bytes` (행 183–232)
- 성질: 제공자가 낸 원 바이트의 계획 실패(구문, 스키마, 계약)는 보존된 바이트를 거쳐 수신자에 이르고, 각각 선택 실패 계보를 하나씩 늘린다. 한도에 이르면 사용자 소유의 보류가 생긴다.
- 준비: `make_active(selection_failure_limit=3)`, 대기열 비우기.
- 실행: 세 원 바이트에 대해 같은 절차(1–4)를 되풀이한다.
  1. `research_plan` 행동의 생애 주기 관문(`_action_lifecycle_gate`)을 통과시키고 `running` 실행을 등록한다.
  2. 실행에 권한, 입력 스냅숏, 입력 묶음, 봉인 프롬프트 목록(`input.txt`의 해시와 크기)을 채운다. `planning.governance_revisions`와 `capture_decision_basis`의 결정 기반도 채운다.
  3. 작업 폴더에서 `_context`와 `_response_schema`를 만들고 `submission.install_tools`를 한다. 문맥, 스키마, 프롬프트를 `_save`로 산출물로 저장한다.
  4. `native_result(execution, context, raw, workspace)`로 원 바이트의 제공자 결과를 만들고 `_collect_submitted_result`를 거친다. 실행을 `stopping`으로 전이한 뒤 `_receive_submission`을 부른다.

  반복이 끝난 뒤 한 번, 마지막 영수증의 `lineage_id`로 `revisions.repetition_hold`를 읽고 `_save()`를 부른다(행 230–232).
- 단언: 각 결과에 `rejected_submission`이 있다. 실행의 `error_kind`가 각각 `'output_parse'`(`b'{broken'`), `'output_schema'`(필드 누락), `'output_contract'`(없는 과제 `TK-missing`에 대한 처분)다. `selection_failure` 영수증 수와 계보 수가 반복마다 `index + 1`이고, 마지막 영수증 `outcome`이 `'rejected'`다. 끝의 보류 `owner`가 `'user'`다.
- 대역: `engine_fixtures.native_result`(제공자 프로토콜 대역; docstring은 "실제 Job 적용 범위는 따로 연결된 시험"이라고 밝힌다).
- 비고: 행 203 주석은 역할 입력 목록이 아래에서 저장하는 보존 프롬프트를 가리킨다고 밝힌다. 마지막 `engine._save()`에는 단언이 없고, 저장이 예외 없이 끝나는 것만 암묵적으로 확인한다. 실제 Git 저장소를 쓴다.

### `test_public_continue_releases_exact_hold_and_replay_is_idempotent` (행 234–256)
- 성질: 공개 제어로 보낸 계속 결정은 정확한 보류를 풀고 계보 수를 0으로 되돌린다. 같은 결정의 재생은 멱등이고, 이미 풀린 보류를 가리키는 새 결정은 거부된다.
- 준비: `make_active(selection_failure_limit=1)`, `seed_plan`. `activities.continue_activity`로 원래 실행의 계속 행동을 얻고, 그 `selection_failure` 계보에 `rejected` 반복을 `record_repetition`으로 기록한다. 보류를 읽고 저장한다.
- 실행: `control(self.repo, instance_id, 'decision', config={'change': change}, text=...)`, `engine.process_controls()`. 이어 저장된 결정의 `source_ref`로 같은 변경을 `governance.apply_decision`에 다시 넣고, `decision_id`만 바꾼 변경도 넣는다.
- 단언: 기록 직후 보류 `owner`가 `'user'`이고 행동이 기다린다. 제어 처리 뒤 행동이 기다리지 않고 계보 수가 0이다. 재생의 `history`가 엔진 런타임의 `history`와 같다. 새 결정은 `ValueError`(`'current repetition hold'`; 제품 `revisions.py`의 `'continuation must name the current repetition hold'`)다.
- 대역: 없음(공개 `control`과 실제 저장소).
- 비고: 실제 Git 저장소와 공개 제어 수신함을 쓴다.

### `test_operational_retry_is_idempotent_and_waits_for_user_at_the_limit` (행 258–317)
- 성질: 한도에 이른 계보에서 운영 검토가 재시도를 결정하면, 재시도 행동은 원래 행동 ID로 한 번만 대기열에 오르고 사용자를 기다린다. 이 대기는 재시작 뒤에도 유지된다. 사용자의 계속 결정 뒤에야 원래 실행을 잇는 후속 실행이 등록되며, 별도의 수리 승인 이력은 생기지 않는다.
- 준비: `make_active(selection_failure_limit=1)`, `seed_plan`, 원래 실행의 계보에 `rejected` 반복 기록. 운영 검토 행동을 관문에 통과시키고 `running` 실행으로 등록한다. 결정 기반과 봉인 프롬프트를 채우는 방식은 `test_native_plan_failures_reach_receiver_counter_through_preserved_bytes`와 같다(행 275–276 주석: 소유자의 쓰기 전 검사가 보존 프롬프트의 존재를 요구한다). 재시도 처분(`kind='retry'`, `next_owner='research_plan'`)을 담은 출력을 `native_result`로 만든다.
- 실행: `_collect_submitted_result`, `stopping` 전이, `_receive_submission`. 이어 새 `ResearchEngine(self.repo, ...)`로 재적재하고, `_complete_operational_disposition(record)`를 한 번 더 부른다. 공개 `control`로 계속 결정을 보내 `process_controls()`를 부르고, 재시도 행동으로 `_register_execution`한다.
- 단언:
  - 수집 결과 `status`가 `'completed'`이고, 수신 결과 `status`가 `'accepted'`다.
  - 운영 처분 기록이 `'applied'`다. `continuation_of`가 원래 실행인 재시도 행동의 `id`가 원래 행동 ID이고, 그 행동이 기다린다.
  - 재적재한 엔진에서도 같은 행동이 기다린다.
  - 처분 완료를 다시 불러도 그 행동은 대기열에 1개뿐이다.
  - 계속 결정 뒤 행동이 기다리지 않는다.
  - 후속 실행의 `continuation_of`가 원래 실행이고, `action.id`가 원래 행동 ID다.
  - 이력에 `kind='repetition_repair_authorized'`가 없다.
- 대역: `native_result`.
- 비고: 실제 Git 저장소, 공개 제어, 재시작 적재를 쓴다.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈: `test_task_contracts`는 계보 수(`repetition_lineages`)를 본다. `test_revision_obligations`는 과제 쪽 엔진 믹스인이 위임과 재시도를 거쳐 개정 소유를 유지하는지 본다(모듈 docstring). `test_planning`은 소진 판정(`exhaustion_state`)과 재고 예약(`schedule_reconsideration`)을 본다. `test_governance`와 `test_governance_engine`은 결정 적용 일반을 본다(`intent_import`는 이 모듈과 `test_governance_engine`만 쓴다). `test_submission_flow`와 `test_native_final_submission`은 `native_result`로 제공자 원 바이트의 수신 경로를 본다.
- 픽스처 의존: `engine_fixtures`의 `routing_engine`, `intent_import`, `intent_verdict`, `native_result`, `purpose_fixtures.ActivatedPurposeHarness`(2단), `runner_fixtures.ScriptedRunner`, `research_fixtures.candidate`. `native_result`, `ScriptedRunner`, `candidate`는 함수 안에서 import하고, 나머지는 모듈 머리(행 21–22)에서 import한다.
- 이 모듈에만 있는 도우미: `RepetitionEngineTests.seed_plan`. 모듈 함수는 없다.
- 겹치거나 보완하는 시험: 계속 결정은 1단에 가까운 메모리 엔진(`test_continue_after_successful_empty_preparation_creates_its_missing_request`)과 2단 공개 제어(`test_public_continue_releases_exact_hold_and_replay_is_idempotent`, `test_operational_retry_is_idempotent_and_waits_for_user_at_the_limit`)에서 본다. 선택 실패 계수는 순수 입력(`test_receiver_failure_categories_count_once_and_success_ends_streak`)과 실제 수신 경로(`test_native_plan_failures_reach_receiver_counter_through_preserved_bytes`)에서 본다. 재생성 시각은 스키마 수준(두 1단 시험)과 실제 실행(`test_empty_preparation_preserves_machine_time_and_opens_one_due_regeneration`)에서 본다.

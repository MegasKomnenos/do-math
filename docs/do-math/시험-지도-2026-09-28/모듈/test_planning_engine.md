# test_planning_engine

| 항목 | 값 |
|---|---|
| 조각 | `lifecycle` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_planning_engine.py` (232행) |
| 클래스 / 테스트 | 5 / 10 |
| 시험 대상 제품 코드 | 계획을 적용하는 `ResearchEngine`의 메서드 `_refresh_readiness`, `_apply_task_plan`, `_select_model`, `_apply_extensions`, `_apply`, `_evaluation_context`; `do_math/planning.py`의 `task_ready`, `contract_hash`, `evaluate_condition`; `do_math/model_policy.py`의 `work_profile_selection`, `LIMITS`; `do_math/configuration.py`의 `validate_config`; `do_math/session_slots.py`의 `SessionSlots`; `do_math/task_contracts.py`의 `returned_task_ids`; `do_math/revisions.py`의 `capture_targets`; `do_math/initialization.py`의 `governance_working_view` |
| 사용하는 픽스처 모듈 | `engine_fixtures`: `FakeEngine`, `context_engine`, `reassessment_engine`, `routing_engine`; `record_fixtures`: `approved_task`, `approve_task`, `task_disposition`; `research_fixtures`: `FixtureAdapter`, `candidate` |
| 격리 표지 | 없음 |
| 시작 상태 | 모두 메모리 엔진 대역이다. `WorkProfileAdmissionTests`는 활성화한 `FakeEngine`, `PlanningConnections`는 `context_engine`(첫 시험)과 `reassessment_engine`(`FakeEngine` 위, 나머지 셋), `KindSemanticConnections`·`DuplicateRevisionConnections`·`EvaluationConnections`의 둘째 시험은 `routing_engine`. `EvaluationConnections`의 첫 시험만 1단(검증기 직접 호출) |

## 목적

모듈 docstring은 "계획의 엔진 쪽"을 시험한다고 밝히며 네 무리를 든다. 계획과 과제 평가의 적용, 준비 상태 갱신(readiness refresh)과 그 후속, 그리고 계획이 평가하는 조건이다.

계획은 연구 계획(`research_plan`) 실행이 과제마다 처분(disposition)과 모델 평가(난도·중요도)를 내는 것이다. 엔진은 그 결과로 작업 행동을 대기열에 넣고, 작업 행동의 모델 등급을 평가에서 고르며(`_select_model`), 과제 계약과 검토는 바꾸지 않는다. 준비 상태 갱신(`_refresh_readiness`)은 과제마다 실행 가능 여부를 계산하고, 평가의 근거(원천 등)가 바뀌면 평가를 낡은 것으로 표시해 재평가 계획을 요청한다. 이 모듈은 그 밖에 작업 프로필이 과제의 모델 평가를 감당하는지의 수락 규칙, 새 종류 정의(kind definition)의 독립 검사, 결과물 조건의 스냅숏 판독, 같은 과제를 대체하는 후보의 중복 거부를 검사한다.

## 모듈 수준 요소

- 행 10: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 조건 없이 넣는다.
- 행 11–15: 제품 `execution_profiles`, `model_policy`, `planning`, `governance_working_view`, `ResearchRepository`와 픽스처 `context_engine`, `FakeEngine`, `reassessment_engine`, `routing_engine`, `FixtureAdapter`를 가져온다.
- 행 231–232: 직접 실행하면 `unittest.main()`.

모듈 함수와 모듈 상수는 없다.

## WorkProfileAdmissionTests (행 18–54)

`unittest.TestCase`를 그대로 상속한다. 표지·훅·도우미·클래스 속성이 없다. 두 시험 모두 임시 디렉터리 위에 `FakeEngine`을 만들고, `do_math.initialization.adapter_for`를 `FixtureAdapter`로 패치한 채 `engine.activate()`로 활성화한다. `FakeEngine`은 제품 엔진을 메모리 상태 위에 올린 대역으로, `activate`가 허가 `GR-init`·`GR-research`, 헌장 `CH-test`, 능력 증거, 초기화 채택 결정, 합성 신뢰 환경, 의도 해석 가져오기를 차례로 적용해 활성 상태를 만든다. `engine.task(approved=False)`는 과제 `T1`(비형식, 기본 프로필은 `research_work`의 `high` 등급)을 런타임에 넣고, `engine.approve(task)`는 계약 검토를 봉인한다.

### `test_policy_change_reprepares_an_unstarted_incompatible_contract` (행 19–33)
- 성질: 설정 변경으로 역할의 최저 등급이 올라가 아직 시작하지 않은 과제의 허용 프로필이 부족해지면, 그 과제는 준비되지 않은 상태가 되고 계약 검토가 아니라 연구 준비(재작성)로 돌아간다.
- 준비: 활성화한 `FakeEngine`. 과제 `T1`의 모델 평가를 `low`/`low`/`'local'`로, 허용 프로필을 `research_work`의 `low` 등급 프로필 하나로 두고 승인한다. 이어 `config['role_tiers']['research_work'] = 'high'`로 바꾼다.
- 실행: `engine._refresh_readiness()`.
- 단언: `_task_readiness['T1'].state == 'not_ready'`. 대기열에 `research_preparation`이고 `target == 'T1'`인 행동이 있다. `task_contract_review`이고 `target == 'T1'`인 행동은 없다.
- 대역: `FakeEngine`, `adapter_for` 패치.

### `test_reviewed_contract_cannot_be_ready_with_an_inadequate_allowed_profile` (행 35–54)
- 성질: 검토를 마친 계약이라도 허용 프로필이 과제의 모델 평가(중요도 `high`)를 감당하지 못하면 준비되지 않고, 감당하는 프로필로 바꾸면 준비되며 작업 프로필 선택이 그 프로필을 고른다.
- 준비: 활성화한 `FakeEngine`. 과제의 모델 평가를 `low`/`high`/`'goal-critical'`로, 허용 프로필을 `low` 등급 하나로 두고 승인한다.
- 실행: `planning.task_ready(task, governance_working_view(instance), runtime)`. 이어 허용 프로필을 `high` 등급 하나로 바꿔 다시 승인하고 `task_ready`와 `model_policy.work_profile_selection(config, task, instance)`.
- 단언: 처음은 `state == 'not_ready'`이고 첫 오류에 `'work profile requirement'`가 있다(메시지 조각 고정). 바꾼 뒤 `state == 'ready'`이고, 선택된 `profile_ref`가 과제의 첫 프로필 참조다.
- 대역: `FakeEngine`, `adapter_for` 패치.

## PlanningConnections (행 57–142)

`unittest.TestCase`를 그대로 상속한다. 표지·훅·도우미·클래스 속성이 없다. 첫 시험은 `engine_fixtures.context_engine`(실제 문맥 생산자를 유지하고 저장소와 무관한 호스트 관찰을 대역으로 바꾼 `bare_engine`)을 쓴다. 나머지 셋은 `engine_fixtures.reassessment_engine(directory)`를 쓴다. 이 픽스처는 `record_fixtures.transfer_assessment()`의 평가를 `incomplete`로 바꿔(의무 `OB-1`이 누락 입력 `SO-new`를 기다린다고 표시) 적용한 뒤 그 상태를 `FakeEngine`에 실은 것이다. 과제 `TK-1`은 없는 입력 `SO-new`를 기다리고, 대기열에는 다른 행동 `AC-other`(`research_preparation`)가 하나 있다.

### `test_plan_assessment_reaches_assignment_without_changing_contract` (행 58–95)
- 성질: 계획 실행의 모델 평가는 작업 행동의 모델 선택에 전달되지만 과제 계약과 검토를 바꾸지 않으며, 행동에 실린 평가는 원본과 분리된 사본이고, 선택된 등급은 세션 슬롯이 없다고 해서 낮아지지 않는다.
- 준비: `record_fixtures.approved_task()`의 상태로 `context_engine`을 만든다. 세션 한도를 `model_policy.LIMITS` 사본으로 두되 `high` 등급 모델의 작업 슬롯을 0으로, `role_tiers.research_work`를 `'low'`로 두고 `build_profiles`로 프로필을 다시 만든다. 과제의 허용 프로필을 `research_work`의 역할 프로필 참조 전부로, 모델 평가를 `low`/`low`로 두고 `approve_task`로 승인한다. 과제의 깊은 사본 `before`를 떠 둔다. 계획 실행 `EX-plan`(종료)에 `model_decisions = {과제: high/high/'New plan needs stronger reasoning'}`를 둔다.
- 실행: `engine._apply_task_plan({'dispositions': [task_disposition(과제)], 'task_assessments': []}, 'EX-plan', 과제 사본, [과제])`. 대기열의 `research_work` 행동으로 `_select_model(action)`. 이어 `SessionSlots(runtime, instance).acquire('EX-no-slot', profile=..., execution=...)`(선택된 프로필로 만든 `starting` 실행), 그리고 `_select_model`을 다시.
- 단언: 선택된 `tier == 'high'`, `model`이 `tier_models['high']`. 행동의 `model_assessment`가 계획의 평가와 같다. 과제의 `contract_hash`와 `reviews`가 `before`와 같다. 원본 평가 사전의 `reason`을 바꿔도 행동의 평가는 바뀌지 않는다(사본). 슬롯 획득은 `False`(슬롯 0), 그래도 다시 고른 등급은 `'high'`다.
- 대역: `context_engine`의 대역.
- 비고: 이름은 "assignment"까지 닿는다고 말한다. 시험은 실제 실행 시작이 아니라 모델 선택과 슬롯 획득 실패까지만 본다. `record_fixtures.task_disposition(과제)`는 `kind='selected'`, `next_owner='research_work'`인 처분이다.

### `test_readiness_refresh_requests_reassessment_while_other_work_remains` (행 97–111)
- 성질: 기다리던 입력이 생기면 준비 상태 갱신이 과제 평가를 낡은 것으로 표시하고 재평가 계획을 한 번만 요청하며(다른 작업이 대기열에 남아 있어도), 과제의 결과는 그대로다.
- 준비: `reassessment_engine(directory)`에 원천 `SO-new`를 더한다. 과제 결과의 사본을 떠 둔다.
- 실행: `_refresh_readiness()`를 두 번.
- 단언: 첫 갱신 뒤 `TK-1.assessment.current`가 거짓, `research_plan` 행동이 하나이고 그 `reason`에 `'TK-1'`이 있다. `task_contracts.returned_task_ids(tasks) == ['TK-1']`. 둘째 갱신 뒤에도 `research_plan` 행동이 하나다. 결과가 원래와 같다.
- 대역: `FakeEngine`(`reassessment_engine` 안).
- 비고: "다른 작업이 남아 있는 동안"은 픽스처의 `AC-other`가 대기열에 있는 상태를 가리킨다. 시험은 `AC-other`에 대해 단언하지 않는다.

### `test_live_work_defers_reassessment_until_end_and_unrelated_changes_do_not_reopen` (행 113–127)
- 성질: 무관한 원천의 추가는 평가를 다시 열지 않고, 과제에 대한 실행이 살아 있는 동안에는 관련 입력이 생겨도 재평가를 미루며, 실행이 끝나면 재평가를 요청한다.
- 준비: `reassessment_engine(directory)`.
- 실행: (1) 무관한 원천 `SO-other`를 더하고 갱신. (2) `TK-1`을 대상으로 한 실행 `EX-live`(`running`)를 넣고, 원천 `SO-new`를 더하고 갱신. (3) `EX-live`의 `status`를 `ended`로 바꾸고 갱신.
- 단언: (1) 뒤 평가가 여전히 `current`. (2) 뒤 대기열에 `research_plan`이 없다. (3) 뒤 평가가 낡음, `research_plan` 행동이 하나.
- 대역: `FakeEngine`(`reassessment_engine` 안).

### `test_terminal_history_remains_closed_when_assessment_evidence_changes` (행 129–142)
- 성질: 이미 닫힌 과제는 평가 근거가 바뀌어도 닫힌 채로 결과를 유지하며, 평가를 낡은 것으로 표시하는 사건 하나와 그 사건을 가리키는 후속 행동만 생긴다.
- 준비: `reassessment_engine(directory)`에서 `TK-1.status = 'closed'`. 결과 사본을 떠 둔다. 원천 `SO-new`를 더한다.
- 실행: `_refresh_readiness()`.
- 단언: 과제 `status == 'closed'`, 결과가 원래와 같다, 평가가 낡음. `events`에서 `kind == 'task_assessment_invalidated'`인 사건이 하나이고, 대기열에 그 사건 ID를 `event_refs`에 담은 행동이 있다.
- 대역: `FakeEngine`(`reassessment_engine` 안).
- 비고: 후속 행동의 역할은 고정하지 않는다.

## KindSemanticConnections (행 145–173)

`unittest.TestCase`를 그대로 상속한다. 표지·훅·도우미·클래스 속성이 없다.

### `test_proposed_kind_is_checked_by_a_separate_execution_before_activation` (행 146–173)
- 성질: 작업 실행이 제안한 새 종류 정의는 후보로 들어가 독립 검사 행동을 하나 만들고, 제안한 실행 자신은 그 검사를 적용할 수 없으며, 별도 실행의 승인이 정의를 활성으로 만든다.
- 준비: `routing_engine()`에 빈 원천과 빈 `kind_definitions`. 작성 실행 `EX-author`(`research_work`, 종료)의 확장에 정의 `{family: 'knowledge', token: 'method_note', meaning: ..., constraints: {mathematical_claim: False}}`. `_apply_queue_plan`과 `_apply_academic_resolutions`를 `create_autospec` 대역으로 바꾼다.
- 실행: `engine._apply_extensions({'role': 'research_work'}, 'EX-author')`. 생긴 검사 행동과 정의 해시로 승인 출력(`kind_definition_check.decision='approved'`)을 만들고, 검사 실행 `EX-check`(`maintenance`, `running`, `input_basis.kind_definition`에 정의 ID와 해시)를 등록한다. 그 출력을 `_apply(action, output, 'EX-author')`와 `_apply(action, output, 'EX-check')`로 적용한다.
- 단언: 확장 적용 뒤 그 정의 ID를 가리키는 검사 행동이 하나이고 정의의 `status == 'candidate'`. 작성 실행으로의 적용은 `ValueError`이고 메시지가 정규식 `'independent|author'`에 맞는다. 검사 실행으로의 적용 뒤 정의의 `status == 'active'`, `checked_by == 'EX-check'`, `check.decision == 'approved'`, `pending_kind_checks == []`.
- 대역: `routing_engine`의 대역, `_apply_queue_plan`·`_apply_academic_resolutions` 대역.

## EvaluationConnections (행 176–198)

`unittest.TestCase`를 그대로 상속한다. 표지·훅·도우미·클래스 속성이 없다.

### `test_declared_observation_and_repetition_values_can_be_adopted` (행 177–181)
- 성질: 관찰 창과 반복 한도에 대한 선언 값은 설정으로 채택할 수 있다.
- 준비: 1단. `tool_review_window_seconds=20`, `self_check_response_window_seconds=30`, 그리고 `import_rework_limit`, `selection_failure_limit`, `exhaustion_empty_limit`, `proposal_version_limit`, `contract_revision_limit`를 모두 3으로 둔 설정.
- 실행: `configuration.validate_config(설정)`.
- 단언: 명시적 단언이 없다. 예외 없이 끝나는 것이 통과 조건이다.
- 대역: 없음.
- 비고: 이 시험은 "계획이 평가하는 조건"과 직접 이어지지 않는 설정 검증이다. 제품 `validate_config`(`configuration.py` 행 38)는 반환값이 없고(`-> None`) 거부할 때만 `ValueError`를 던지는 검증기다. 따라서 이 시험이 보이는 것은 그 값들이 검증에서 거부되지 않는다는 것뿐이며, 이름의 "adopted"가 뜻하는 실제 채택, 곧 `configure` 제어로 인스턴스 설정에 들어가는 경로는 지나지 않는다.

### `test_artifact_condition_reads_exact_snapshot_and_validates_bytes` (행 183–198)
- 성질: 결과물 유효 조건(`artifact_valid`)은 참조가 가리키는 정확한 스냅숏에서 바이트를 읽고, 해시가 맞더라도 JSON이 깨졌으면 평가 오류다.
- 준비: `routing_engine()`, `head = 'a'*40`, 저장소를 `ResearchRepository`의 `create_autospec` 인스턴스로 바꾸고 `read`가 `b'{"proof": true}'`를 돌려주게 한다. 참조는 경로 `runtime/artifacts/BA-test/evidence.json`, 스냅숏 `'b'*40`(현재 헤드와 다르다), 그 바이트의 SHA-256.
- 실행: `planning.evaluate_condition({'op': 'artifact_valid', 'artifact_ref': ref}, instance, runtime, evaluation_context=engine._evaluation_context())`. 이어 `read`가 깨진 JSON `b'{"valid":true'`을 돌려주게 하고 해시를 그에 맞춘 뒤 다시.
- 단언: 첫 결과 `state == 'ready'`이고 `store.read`가 `(경로, 'b'*40)`으로 정확히 한 번 불렸다(현재 헤드가 아니라 참조의 스냅숏). 둘째 결과 `state == 'evaluation_error'`.
- 대역: `ResearchRepository` 대역.

## DuplicateRevisionConnections (행 201–228)

`unittest.TestCase`를 그대로 상속한다. 표지·훅·도우미·클래스 속성이 없다.

### `test_same_task_replacements_are_rejected_before_any_receiver_mutation` (행 202–228)
- 성질: 한 연구 준비 출력이 같은 과제를 대체하는 후보를 둘 이상 내면, 수신자는 상태를 조금도 바꾸기 전에 거부한다.
- 준비: `record_fixtures.approved_task()`의 상태에 설정 `{'lean_command': ['unused-fixture'], 'scholarly_enabled': False}`와 빈 지식을 두고, 런타임에 `cycles=0`, 빈 `waiting_actions`. 이 상태를 `routing_engine()`에 싣고 `_evaluation_context`를 빈 사전 대역으로 바꾼다. 행동 `AC-revise`(`research_preparation`, `revision_targets = revisions.capture_targets(instance, runtime, [과제])`). 실행 `EX-revise`(종료). `research_fixtures.candidate(title, revises=과제)`로 후보 `First`, `Second`를 만들고 둘 다 과제의 프로필·권한을 복사하며 첫 완료 의무의 주장을 제목으로 둔다. 상태의 깊은 사본 `before`.
- 실행: `engine._apply(action, {'summary': ..., 'questions': [], 'used_sources': [], 'candidates': 후보 둘}, 'EX-revise')`.
- 단언: `ValueError`를 메시지 조각 `'one replacement candidate'`로 던진다. 엔진의 인스턴스·런타임이 `before`와 같다. `_record_output_questions` 대역이 정확히 한 번 불렸다.
- 대역: `routing_engine`의 대역(`_record_output_questions` 등), `_evaluation_context` 대역.
- 비고: `_record_output_questions`는 `routing_engine`이 `create_autospec`으로 바꿔 둔 메서드라 상태를 바꾸지 않는다. 시험은 거부 전에 이 호출이 한 번 일어났음을 고정한다. 이름의 "before any receiver mutation"은 상태 비교로 확인되며, 이 호출은 대역이므로 그 비교에 영향을 주지 않는다.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈: 계획의 순수 규칙(`planning.task_ready`, 계약 해시, 조건 평가)은 이름이 같은 제품 모듈의 시험 `test_planning`이, 세션 슬롯은 `test_session_scheduler`가 다룬다. `model_policy`의 이름을 단 시험 모듈은 없다. 입력 초과로 붙잡힌 행동의 계획자 선택은 `test_input_recovery`가 다룬다. 이 모듈은 엔진이 그 규칙들을 적용하는 연결을 본다.
- 픽스처 의존: `engine_fixtures.FakeEngine`(`WorkProfileAdmissionTests`), `context_engine`(`test_plan_assessment_reaches_assignment_without_changing_contract`), `reassessment_engine`(재평가 세 시험), `routing_engine`(`KindSemanticConnections`, `EvaluationConnections`, `DuplicateRevisionConnections`); `record_fixtures.approved_task`, `approve_task`, `task_disposition`; `research_fixtures.FixtureAdapter`(활성화 중 어댑터), `candidate`.
- 이 모듈에만 있는 도우미: 없다. 모든 준비가 시험 본문과 픽스처에 있다.
- 겹침과 보완: 작업 프로필의 적합성은 설정 변경 뒤의 갱신(`test_policy_change_reprepares_an_unstarted_incompatible_contract`)과 순수 판정(`test_reviewed_contract_cannot_be_ready_with_an_inadequate_allowed_profile`)이 짝을 이룬다. 재평가는 세 시험이 새 입력, 살아 있는 실행, 닫힌 과제라는 세 상황으로 나눠 본다.

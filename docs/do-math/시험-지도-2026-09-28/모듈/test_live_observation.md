# test_live_observation

| 항목 | 값 |
|---|---|
| 조각 | `lifecycle` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_live_observation.py` (588행) |
| 클래스 / 테스트 | 6 / 21 |
| 시험 대상 제품 코드 | `do_math/observations.py`의 `ObservationTracker`(`observe`, `issue_self_check`, `record_delivery`, `obligations`, `self_check_call_ids`, `boundary_call_ids`, `counters`, `rules`), `bind_task_rules`, `task_rules_from_execution`, `validate_execution_rules`, `observation_rule_contract`, `evaluate_rules`, `tracker_config`; `do_math/observation_transport.py`의 `ObservationBatch`; `do_math/engine.py`의 `ResearchEngine`(`_observe_running`, `_call_steps`, `_record_review_observation`); `do_math/control_transport.py`의 `ControlTransport`(`issue`, `request_self_check`, `worker_self_check`); `do_math/parallel.py`의 `ModelCalls`; `do_math/model_runner.py`의 `ModelRunner.run`; `do_math/codex_adapter.py`의 `CodexExecAdapter`, `CLIExecution`; `do_math/windows_job.py`의 `WindowsJob`; `do_math/record_schemas.py`의 `RECORDS` |
| 사용하는 픽스처 모듈 | `engine_fixtures`(`routing_engine`); `provider_fixtures`(`Adapter`, `runner_with`); `research_fixtures`(`acknowledge`, `Clock`, `observation_batch`, `observe`, `write_checkpoint`, `observation_rule`, `candidate`, `supply_observation_rules` 패치 대상); `record_fixtures`(`contract_check`, `preparation_context`, `preparation_issues`); 실행기 모듈 `test_categories`(`test_group`) |
| 격리 표지 | `NativeBatchTests`에 `test_group('resource')` |
| 시작 상태 | 1단(관찰 규칙 함수와 `ObservationTracker`에 설정 가능한 시계 `Clock` 주입) 다수. 소유자 경로는 `engine_fixtures.routing_engine` 메모리 엔진에 `_controls`, `_check_conversations`, `_save` 등을 `create_autospec` 대역으로 둔다. 실제 Windows Job 자식 프로세스 1개, 실제 스레드 기반 `ModelCalls` 1개 |

## 목적

모듈 docstring은 "실행 중인 실행의 실시간 관찰: 수집된 사건, 자기 점검 의무, 관찰 규칙"을 시험한다고 밝힌다. 또한 "공급자 스트림과 모델 답은 픽스처이고, 관찰 추적기와 그 전송, 관찰을 적용하는 소유자와 그 게시는 제품의 것"이라고 적는다.

실행 중인 작업자의 공급자 스트림(Codex JSONL 사건, Claude `assistant`/`user` 메시지)은 러너가 `ObservationBatch`로 묶어 소유자에게 넘긴다. 소유자 `_observe_running`은 그 배치를 `ObservationTracker`에 먹여 관찰 사실(`observation_facts`), 체크포인트, 자기 점검 의무를 만들고 한 트랜잭션으로 게시한다. 이 모듈은 다음을 검사한다.

- 과제 관찰 규칙을 실행에 결박하는 규칙.
- 자기 점검 요청의 전달, 수신 확인(ack), 놓침(missed) 판정.
- 체크포인트 증거 포획.
- 배치 하나가 소유자 트랜잭션 하나라는 규칙.
- 실패한 게시가 추적기와 상태를 되돌리는 원자성.
- 한가한 관찰이 상태를 복사하거나 게시하지 않는다는 규칙.
- 검토 대화 행의 순서.
- 역할별 관찰 계약.

## 모듈 수준 요소

- 행 16: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 넣는다.
- 행 24: 실행기 `test_categories`에서 `test_group`을 import한다. `NativeBatchTests`의 격리 표지에 쓴다.
- 행 587–588: 직접 실행하면 `unittest.main()`.

자주 쓰는 픽스처는 다음과 같다.

- `research_fixtures.Clock`: 호출하면 `value`를 돌려주는 설정 가능한 시계.
- `observation_rule()`: 체크포인트 카운터 `attempts`가 2 이상이면 자기 점검을 요구하는 규칙 `R-1`.
- `write_checkpoint(workspace, counters=...)`: 유효한 작업자 체크포인트를 쓴다.
- `observe(tracker, event)`: 추적기 시계로 받은 다음 1바이트 스트림 행으로 사건을 관찰시킨다.
- `acknowledge(tracker, obligation_id)`: 자기 점검 요청을 발급·전달하고 작업자의 성공 폴링을 관찰시켜, 이후의 연구 행동이 요청 위반이 되게 한다.
- `observation_batch(events, ...)`: 연속 JSON 행으로 된 러너 배치.

## RuleBindingTests (행 27–94)

`unittest.TestCase`를 상속한다. 설정 훅과 도우미가 없다. 과제 관찰 규칙은 대상 ID 자리에 `$execution`을 쓰고, 실행을 시작할 때 실제 실행 ID로 결박된다.

### `test_producer_reports_missing_initial_rules_before_contract_review` (행 28–35)
- 성질: 준비 출력이 후보 과제의 초기 관찰 규칙을 선언하지 않으면, 생산자 쪽 수신자가 계약 검토 전에 그 누락을 쟁점으로 보고한다.
- 준비: 1단. `research_fixtures.supply_observation_rules`를 아무것도 하지 않는 함수로 패치한다. `preparation_issues`는 호출 시점에 이 함수를 읽어 확장에 규칙을 넣으므로, 패치하면 규칙이 빠진다.
- 실행: `preparation_issues([contract_check()], candidates=[candidate('one')], context=preparation_context(), workspace=...)`.
- 단언: 쟁점 JSON 텍스트가 `'initial_observation_rules'`를 담는다.
- 대역: `supply_observation_rules` 패치.

### `test_foreign_execution_is_not_silently_rebound` (행 37–42)
- 성질: 이미 다른 실행(`EX-foreign`)에 결박된 규칙은 새 실행으로 조용히 다시 결박되지도, 과제 규칙으로 되돌려지지도 않는다.
- 준비: 1단. 대상 `EX-foreign`인 `checkpoint_count_gte` 규칙.
- 실행: `observations.bind_task_rules(rules, 'EX-new')`, `observations.task_rules_from_execution(rules, 'EX-new')`.
- 단언: 둘 다 `ValueError`(유형만).
- 대역: 없음.

### `test_one_task_rule_can_start_two_distinct_executions` (행 44–59)
- 성질: 과제 규칙 하나로 서로 다른 두 실행을 시작할 수 있고, 각 추적기는 자기 실행 ID로 결박된 규칙을 가지며, 원래 과제 규칙은 바뀌지 않는다.
- 준비: 1단. 두 창을 넣은 설정의 `research_work` 프로필. 대상 `$execution`인 `checkpoint_count_gte` 규칙(임계 2).
- 실행: `bind_task_rules`가 호출 가능한지 먼저 확인한다. 실행 `EX-first`, `EX-second`마다 결박하고, `tracker_config(profile, initial_self_check_rules=bound)`와 `ObservationTracker(eid, dir, config)`를 만든다.
- 단언: `bind_task_rules`가 호출 가능하다(메시지: 추적기 입장 전에 실행 결박이 필요하다). 각 추적기 첫 규칙의 대상 ID가 그 실행 ID다. 원 규칙의 대상 ID는 `$execution` 그대로다.
- 대역: 없음.

### `test_checkpoint_iterations_bind_and_round_trip_for_each_execution` (행 62–85)
- 성질: 체크포인트 반복 횟수 규칙은 실행마다 결박되어 검증을 통과하고 도래를 평가하며, 과제 규칙으로 정확히 되돌아가고, 다른 실행에 결박된 사본은 결박·되돌림·검증에서 모두 거부된다.
- 준비: 1단. 대상 `$execution`, 근거 `checkpoint`, 임계 10, 반복 간격 10인 `iteration_gte` 규칙 `iteration-review`.
- 실행: 실행 `EX-first`, `EX-retry`마다 `bind_task_rules`, `validate_execution_rules(bound, bindings=observation_rule_contract(), execution_id=eid)`, `evaluate_rules(bound, {'iterations': {eid: 10}})`, `task_rules_from_execution(bound, eid)`를 부른다. 대상을 `EX-foreign`으로 바꾼 사본으로 세 함수를 다시 부른다.
- 단언: 결박 대상이 실행 ID다. 도래 규칙 ID 목록이 `['iteration-review']`다. 되돌린 규칙이 원 템플릿과 같다. 바꾼 사본은 세 호출 모두 `ValueError`다. 템플릿 대상은 끝까지 `$execution`이다.
- 대역: 없음.

### `test_iterations_have_only_the_checkpoint_source` (행 87–94)
- 성질: 반복 횟수 규칙의 근거는 체크포인트뿐이며, 실행 사건을 근거로 한 반복 규칙은 입장하지 못한다.
- 준비: 1단. 근거 `execution_events`인 `iteration_gte` 규칙.
- 실행: `bind_task_rules(rules, 'EX-new')`.
- 단언: `ValueError`(메시지 `'basis'`).
- 대역: 없음.
- 비고: 주석은 공급자 사건에는 반복 횟수가 없다고 설명한다.

## ObservationCollectionTests (행 97–358)

`unittest.TestCase`를 상속한다. 설정 훅과 도우미가 없다. 소유자 경로를 보는 시험은 `routing_engine()`에 `_controls`, `_check_conversations`(거짓 반환), `_save`를 `create_autospec` 대역으로 두고, `running` 상태의 실행 `EX-one`을 넣는다.

### `test_owner_distinguishes_preview_and_boundary_from_self_check` (행 98–134)
- 성질: 자기 점검 요청을 받은 뒤, 소유자는 작업자의 제출 미리보기(submission preview)만 응답 전 연구 행동으로 보고 요청을 놓침으로 표시한다. 안전 경계(safety boundary) 제출은 경계 호출로, 자기 점검 호출은 자기 점검 호출로 따로 기록한다.
- 준비: 1단 추적기와 메모리 엔진. 두 공급자(`codex`, `claude`)와 세 종류(`submission_preview`, `safety_boundary`, `self_check`)의 조합마다 `subTest`로 새 임시 디렉터리를 쓴다. 추적기는 `observation_rule()`, 창 60·5, `Clock()`으로 만든다. 체크포인트 카운터 `attempts=2`로 `tick`을 관찰해 `self_check_due` 의무를 얻고, `acknowledge`로 전달과 폴링을 관찰시킨다. 호출 사건 `CALL`의 도구는 `self_check`면 `control_self_check`(인자 `self_check_id`), 아니면 `control_submit`(인자 `request_id='NEXT'`, `kind`, 페이로드)이다. Codex는 `item.started`의 `mcp_tool_call`로, Claude는 `mcp__execution_control__<tool>` 이름의 `tool_use`로 표현한다. 엔진에는 `_enqueue`와 `_review_observation_source`(없음 반환)도 대역으로 둔다.
- 실행: `_observe_running('EX-one', tracker, observation_batch([event], ..., start=추적기의 마지막 끝 오프셋))`.
- 단언: 의무의 `missed_reason`이 `submission_preview`일 때만 `'research_action_before_response'`이고 나머지는 `None`이다. `CALL`이 `self_check_call_ids`에 있는 것은 `self_check`일 때뿐이고, `boundary_call_ids`에 있는 것은 `safety_boundary`일 때뿐이다.
- 대역: `create_autospec` 대역 다섯 개(`_controls`, `_check_conversations`, `_save`, `_enqueue`, `_review_observation_source`), `Clock`.
- 비고: `subTest` 케이스는 공급자 2 × 종류 3 = 6개다. 시험 안에서 `create_autospec`과 `routing_engine`을 다시 import하는데, 둘 다 모듈 머리에서 이미 import한 이름이다.

### `test_self_check_is_discoverable_inside_the_assigned_workspace` (행 136–148)
- 성질: 자기 점검 요청은 배정된 작업공간 안의 알려진 경로에 놓여 작업자가 ID로 찾을 수 있고, 작업자 조회가 같은 요청을 돌려준다.
- 준비: 1단. 실제 `ControlTransport(root/'transport')`와 작업공간. `issue('EX-one', 'GR-one', workspace=...)`로 결박을 발급한다.
- 실행: `request_self_check(binding, request={'self_check_id': 'SC-one', ...})`, `worker_self_check(binding, self_check_id='SC-one')`.
- 단언: `workspace/.control/self-checks/SC-one.json`이 파일이다(메시지: ID가 필요한 폴링에는 허용된 작업공간 안의 찾을 수 있는 요청이 필요하다). 그 JSON이 요청과 같다. 작업자 조회도 요청과 같다.
- 대역: 없음. 실제 파일 전송을 쓴다.

### `test_native_poll_ack_requires_the_exact_successful_returned_request` (행 150–181)
- 성질: 작업자의 자기 점검 폴링은 정확히 발급된 요청을 성공적으로 돌려받았을 때만 수신 확인으로 인정되며, 그 뒤의 새 명령만 놓침이 된다.
- 준비: 1단. 변형 `ok`, `started`, `failed`, `wrong_payload`, `error_result`, `claude`마다 `subTest`로 새 추적기와 `self_check_due` 의무를 만든다. `issue_self_check`로 받은 봉투 사본을 두고 `record_delivery(..., source_offset=100)`를 기록한다. `wrong_payload`는 봉투의 `rule_revision`을 1 올린다. 폴링 사건 항목은 `control_self_check` 호출이다. 상태는 `failed` 변형만 `failed`이고 나머지는 `completed`이며, 결과 텍스트는 봉투 JSON이고, `isError`는 `error_result` 변형만 참이다. 원천 좌표는 오프셋 100–150이다.
- 실행: `claude` 변형은 `tool_use`를 먼저 관찰하고 봉투를 담은 `tool_result`를 관찰한다. 나머지는 `started` 변형이면 `item.started`, 아니면 `item.completed`로 관찰한다(모두 `evaluate=False`). 이어서 오프셋 150–200의 새 `command_execution` 시작을 관찰한다.
- 단언: 새 명령 관찰 결과에 `self_check_missed`가 있는 것은 `ok`와 `claude`일 때뿐이다.
- 대역: `Clock`.
- 비고: `subTest` 케이스는 여섯 변형이다. 원문 주석은 폴링이 추적기가 발급하고 해시한 바로 그 요청 객체를 돌려준다고 적는다.

### `test_native_command_after_delivery_without_ack_is_only_missing_response_evidence` (행 183–205)
- 성질: 전달 뒤 수신 확인 없이 관찰된 명령은 놓침으로 판정되지 않고, 응답 기한이 지나야 기한 경과로 보고된다.
- 준비: 1단. `Clock`을 단 추적기, `self_check_due` 의무, 발급과 오프셋 100 전달.
- 실행: 오프셋 200–300의 `command_execution` 시작 관찰. 시계 2에서 그 명령의 완료 관찰. 시계 7에서 `tick` 관찰.
- 단언: 명령 시작 관찰 결과에 `self_check_missed`가 없다(메시지: 전달 뒤의 게시가 이 자기 점검의 수신을 입증하지 않는다). `tick` 결과에 사유 `response_deadline_passed`인 행이 있다.
- 대역: `Clock`.
- 비고: 주석은 실행 중 명령이 1초부터 2초까지 기한을 붙잡아, 기한이 6초 뒤에 지난다고 설명한다. 응답 창은 5초다. 단언은 시계 7에서 기한 경과만 확인하고 시계 5와 6 사이를 보지 않는다. 그래서 명령이 기한을 늦추는지는 이 시험이 판별하지 못한다. 늦춤이 없어도 기한은 5초에 지나므로 시계 7의 단언은 똑같이 성립한다.

### `test_checkpoint_capture_preserves_its_evidence_before_live_file_changes` (행 207–232)
- 성질: 소유자가 관찰 중 포획한 체크포인트 증거는 포획 뒤 작업공간 파일이 바뀌어도 게시되는 산출물에서 원래 바이트를 유지한다.
- 준비: 메모리 엔진(`max_artifact_bytes=4096`). 임시 작업공간에 `proof.lean`(`b'exact submitted source'`)과 그것을 증거로 가리키는 체크포인트. `deadline_only` 추적기와 빈 `ObservationBatch`.
- 실행: `_observe_running('EX-one', tracker, batch)`. 이어서 `proof.lean`을 `b'changed later'`로 바꾼다.
- 단언: 런타임 체크포인트의 `evidence_files`가 1개다. `_save` 대역이 받은 첫 인자(산출물 사전)에서 그 증거 파일 산출물이 원래 바이트다.
- 대역: `create_autospec` 대역 세 개, `Clock`.
- 비고: `test_checkpoint_persistence`가 같은 성질을 순수 함수와 실제 게시 층에서 본다.

### `test_rejected_input_of_a_deadline_only_execution_is_recorded_without_a_review` (행 234–252)
- 성질: `deadline_only` 실행에 다른 실행의 사건이 들어오면 거부 사실만 기록하고, 후속 조치나 운영 검토를 열지 않는다.
- 준비: 메모리 엔진에 `maintenance` 역할 실행 `EX-one`. `deadline_only` 추적기.
- 실행: `execution_id='EX-other'`를 가진 `turn.started` 사건 배치로 `_observe_running`.
- 단언: 관찰 사실 가운데 종류 `observation_input_rejected`인 것이 1개이고 `followup` 키가 없다. 큐에 `operational_review`가 없다.
- 대역: `create_autospec` 대역 세 개, `Clock`.
- 비고: 주석은 `deadline_only` 실행이 재귀 검토를 열지 않으므로 거부된 입력에 후속이 없다고 설명한다.

### `test_returned_result_is_collected_before_unrelated_observation_callbacks` (행 254–281)
- 성질: 모델 호출 수집은 이미 돌아온 결과를 다른 실행의 관찰 콜백보다 먼저 연속에 전달한다.
- 준비: 실제 `ModelCalls()`. 결과를 받으면 `order`에 `'result'`를 적는 연속 생성기. 첫 호출 `EX-ready`는 곧바로 끝나는 함수로 시작해 `result(timeout=5)`로 끝남을 기다린다. 둘째 호출 `EX-live`는 `on_observation`을 불러 `order`에 `'observation'`을 적게 한 뒤 `threading.Event`를 최대 5초 기다린다.
- 실행: 둘째 호출의 `future.observations`가 생길 때까지 10밀리초 간격으로 폴링한다(상한 5초). 이어서 `calls.collect()`.
- 단언: `collect()`가 1을 돌려준다. `order`가 `['result', 'observation']`이다. 끝에 이벤트를 풀고 `close()`한다.
- 대역: 없음. 실제 스레드를 쓴다.
- 비고: 폴링 상한 5초, 이벤트 대기 상한 5초.

### `test_buffered_command_before_delivery_is_not_a_new_action_violation` (행 283–310)
- 성질: 자기 점검 전달 이전 스트림 위치의 명령은, 전달 뒤에 관찰되더라도 새 행동 위반이 아니다. 수신 확인 뒤, 전달보다 뒤 위치에 있는 새 명령만 놓침이 된다.
- 준비: 1단. `self_check_due` 의무, 발급한 봉투, 오프셋 100 전달.
- 실행: 오프셋 0–80의 옛 명령 시작 관찰. 80–160에 걸친 부분 기록 명령 관찰. 100–160의 성공 폴링 관찰. 160–200의 새 명령 시작 관찰(모두 `evaluate=False`).
- 단언: 옛 명령과 부분 기록 명령의 관찰 결과에는 `self_check_missed`가 없다. 부분 기록 명령의 메시지는 "부분적으로 쓰인 옛 사건의 시작은 전달보다 앞선다"이다. 새 명령 관찰 결과에는 `self_check_missed`가 있다.
- 대역: `Clock`.
- 비고: 제품의 놓침 판정(`observations.py` 행 576–578)에는 두 조건이 모두 필요하다. 하나는 수신 확인이 있는 것이고, 다른 하나는 사건의 스트림 시작 오프셋이 전달 오프셋과 수신 확인 오프셋 가운데 큰 값 이상인 것이다. 원문 메시지는 부분 기록 명령이 위반이 아닌 이유를 시작 오프셋 80이 전달 오프셋 100보다 앞서는 데서 찾는다. 그러나 옛 명령과 부분 기록 명령은 모두 폴링(수신 확인)보다 먼저 관찰되므로, 수신 확인 조건만으로도 놓침이 되지 않는다. 따라서 이 시험은 오프셋 조건을 따로 떼어 판별하지 못한다.

### `test_terminated_stream_replay_preserves_events_without_live_reviews` (행 312–336)
- 성질: 이미 끝난 스트림을 다시 먹이면 사건은 관찰 사실로 보존되지만, 실시간 운영 검토나 의무는 만들지 않고 게시는 한 번이다.
- 준비: 메모리 엔진. 관찰 간격 300초의 `periodic` 추적기. 시계를 900으로 둔다. 사건 두 개(`turn.started`, 옛 명령 시작)와 그 오프셋·행 바이트로 만든 `ObservationBatch`의 종료 판정 함수가 참을 돌려준다.
- 실행: `_observe_running('EX-one', tracker, batch)`.
- 단언: 큐에 `operational_review`가 없다. 관찰 사실이 2개다. `_save` 호출이 1번이다. 추적기 `obligations`가 비어 있다.
- 대역: `create_autospec` 대역 세 개, `Clock`.

### `test_one_native_chunk_is_one_owner_transaction` (행 338–358)
- 성질: 공급자 스트림에 한 번에 버퍼된 사건 20개는 관찰 콜백 한 번, 곧 소유자 트랜잭션 하나로 전달된다.
- 준비: `provider_fixtures.Adapter`를 상속한 `Burst`. `wait_for_termination`의 첫 폴링에서 요청의 `stdout_path`에 `agent_message` 사건 20개를 한 번에 쓰고, 두 번째 폴링에서 끝났다고 답한다. `do_math.model_runner.time.sleep`을 패치해 대기를 없앤다. `runner_with(Burst({...'result': 'output_collected'...}))`.
- 실행: `runner.run(prompt='fixture', ..., on_observation=delivered.append)`.
- 단언: 결과 `status`가 `completed`다. `delivered`가 1개다(메시지: 버퍼된 스트림 조각 하나에 상태 트랜잭션 20개가 필요하면 안 된다). 그 배치의 `events`가 20개 사건과 같다.
- 대역: `Burst` 수집기 대역, `time.sleep` 패치.

## NativeBatchTests (행 362–422)

`unittest.TestCase`를 상속한다. 클래스 데코레이터 `@test_group('resource')`가 붙어 있어 `run_tests.py`가 격리된 Windows Job 작업자 프로세스에서 제한 시간과 함께 돌린다(`시험-지침.md` 1절, 4절 규칙 6). 설정 훅과 도우미가 없다.

### `test_real_job_completion_is_observed_before_delayed_batch_application` (행 363–422)
- 성질: 실제 Job이 끝난 뒤에 관찰 배치가 늦게 적용되어도 모든 사건이 스키마에 맞는 관찰 사실로 보존되고, 종료 장벽이 확인되며, 끝난 실행에 실시간 운영 검토가 열리지 않는다.
- 준비:
  - `CodexExecAdapter`를 상속한 `LocalStream`을 둔다. 그 `start`는 요청 파일에서 프롬프트·스키마·출력 경로를 읽는다. 스키마를 작업 폴더에 복사하고, 상태(`exited`, 종료 코드 0, 요청·표준입력·스키마 해시)와 사건 네 개(`thread.started`, `turn.started`, 최종 `agent_message` `{"ok":true}`, `turn.completed`)를 준비한다.
  - 실제 `WindowsJob`으로 `python -B -c` 스크립트를 띄워 stdout·stderr·최종·상태 파일을 쓰게 하고, 그 Job을 담은 `CLIExecution`을 돌려준다.
  - 메모리 엔진에는 `running` 실행 `EX-real`과 `create_autospec` 대역 세 개를 둔다.
  - 관찰 간격 1초의 `periodic` 추적기를 쓰고, `last_review`를 600초 앞당겨 검토 주기가 이미 지난 상태로 만든다.
  - 관찰 콜백 `delayed(batch)`는 `batch.is_terminated()`가 참이 될 때까지 10밀리초 간격으로 폴링하고(상한 10초), 참임을 단언한 뒤 `_observe_running`을 부른다.
- 실행: `runner_with(LocalStream('local-fixture')).run(prompt=..., output_schema={'type': 'object'}, timeout_seconds=15, on_observation=delayed)`.
- 단언: 결과 `status`가 `completed`(실패 시 `error`를 싣는다)이고 `output`이 `{'ok': True}`다. `execution.collect.termination_barrier.confirmed`가 참이다. 큐에 `operational_review`가 없다. 관찰 사실이 4개이고 각각 `RECORDS['observation_facts']` 스키마(`Draft202012Validator`)를 통과한다.
- 대역: `LocalStream`(모델 없는 로컬 스트림, 프롬프트 `'Local stream fixture, no model.'`), `create_autospec` 대역 세 개.
- 비고: 실제 외부 자원은 Windows Job과 Python 자식 프로세스다. 격리 표지는 `resource`다. 폴링 상한은 10초이고 러너 시간 상한은 15초다.

## ObservationTransactions (행 425–496)

`unittest.TestCase`를 상속한다. 설정 훅과 도우미가 없다. 세 시험 모두 `routing_engine` 메모리 엔진, `observation_rule()` 추적기, `Clock`을 쓴다.

### `test_failed_observation_publication_does_not_advance_the_tracker` (행 426–447)
- 성질: 관찰 게시가 실패하면 추적기 카운터도 엔진 상태도 앞으로 가지 않고 자기 점검 요청도 보내지 않으며, 다음 게시가 성공하면 그때 한 번 반영된다.
- 준비: 메모리 엔진에 실행 `EX-one`, `_transport`는 `Mock`, `_transport_bindings`에 `EX-one`을 둔다. 상태 사본. `_save`를 `ValueError("CAS failure")`로 대역화한다. 체크포인트 카운터 `attempts=2`.
- 실행: 빈 배치로 `_observe_running`을 부른다. `side_effect`를 해제하고 다시 부른다.
- 단언: 첫 호출은 `ValueError`(메시지 `"CAS"`)이고, 그 뒤 추적기 `counters`가 `{}`이며 상태가 사본과 같고 `request_self_check`가 불리지 않았다. 둘째 호출 뒤 `counters`가 `{"attempts": 2}`이고 `self_check_obligations`가 비어 있지 않으며 `request_self_check`가 정확히 한 번 불렸다.
- 대역: `_controls`, `_check_conversations`, `_save` 대역, `_transport` `Mock`.

### `test_failed_observation_rolls_back_to_the_published_state_without_copying_it_first` (행 449–475)
- 성질: 관찰 게시가 실패하면 엔진은 저장소에 게시된 상태로 되돌아가며, 그 되돌림을 위해 미리 런타임 사본을 뜨지 않는다.
- 준비: 게시 상태를 들고 있는 지역 저장 대역 `PublishedStore`(`git_dir=None`, `published_state`, `load`). 메모리 엔진의 저장소를 그것으로 바꾸고 상태 사본을 뜬다. `_save`는 `CAS failure` 대역이다.
- 실행: `do_math.engine.deepcopy`를 `wraps`로 감시하며 `_observe_running`.
- 단언: `ValueError`(`"CAS"`)가 난다. `deepcopy` 호출 인자 가운데 사본 객체이거나 사본과 같은 값이 없다(미리 복사하지 않았다). 런타임이 사본과 같다. 추적기 `counters`가 `{}`다.
- 대역: `PublishedStore`, `_save` 대역, `deepcopy` 감시.

### `test_idle_observation_tick_neither_copies_nor_publishes_the_runtime` (행 477–496)
- 성질: 새 것이 없는 관찰 틱은 런타임을 복사하지도 게시하지도 않는다.
- 준비: 메모리 엔진과 `_save` 대역.
- 실행: 빈 배치로 `_observe_running`을 부르고(주석: 첫 틱은 아직 측정되지 않은 규칙 신호를 보고한다), 대역을 초기화하고 사본을 뜬 뒤, `deepcopy` 감시 아래 다시 부른다.
- 단언: 첫 틱에서 `_save`가 정확히 한 번 불린다. 둘째 틱에서는 `_save`가 불리지 않고, `deepcopy`의 인자로 런타임 객체 자체가 쓰이지 않으며, 런타임이 사본과 같다.
- 대역: `_save` 대역, `deepcopy` 감시.

## ReviewDialogueObservationTests (행 499–536)

`unittest.TestCase`를 상속한다. 설정 훅과 도우미가 없다.

### `test_review_public_dialogue_keeps_raw_row_order_and_retries_after_failed_cas` (행 500–536)
- 성질: 검토 실행의 공개 대화 행은 원 행 바이트와 스트림 행 번호를 그대로 기록하고, 게시가 실패하면 같은 행을 다시 적용할 수 있으며, 작업이 끝난 뒤 전달되는 마지막 미종결 행은 다음 번호를 받는다.
- 준비:
  - 메모리 엔진에 `_record_review_observation`을 대역으로 두고, 검토 주기 `RC-one`의 `identity_review` 실행 `EX-review`를 넣는다.
  - 인스턴스 작업공간을 임시 디렉터리로 두고 `runs/EX-review/evidence/stdout.jsonl`에 빈 줄, 한 행, 줄바꿈 없는 꼬리 행을 쓴다.
  - 지역 함수 `batch(event, start, raw, first_row)`는 정확한 행 바이트와 행 번호로 `ObservationBatch`를 만든다.
  - `deadline_only`, `research_self_checks=False` 추적기를 쓰고, `_save`는 `CAS failed` 대역이다.
- 실행: 첫 행 배치(시작 1, 행 번호 0)로 `_observe_running`을 부르면 실패한다. 대역을 해제하고 같은 배치로 다시 부른다. 이어서 꼬리 행 배치(시작 `1 + len(row)`, 행 번호 1)로 부른다.
- 단언: 첫 호출은 `ValueError`(`"CAS"`)다. 재시도 뒤 `_record_review_observation`의 마지막 호출 인자가 `("EX-review", event)`이고 `event_index`가 0이며, `_save`가 받은 산출물의 그 `artifact_ref` 바이트가 원 행 바이트다. 꼬리 행 뒤 호출 인자가 `("EX-review", tail)`이고 `event_index`가 1이며, 산출물 바이트가 줄바꿈 없는 꼬리 바이트다.
- 대역: `_controls`, `_check_conversations`, `_record_review_observation`, `_save` 대역.
- 비고: 주석은 Job이 끝난 뒤 러너가 미종결 마지막 행을 다음 번호로 전달한다고 설명한다.

## TaskObservationRoleTests (행 539–584)

`unittest.TestCase`를 상속한다. 설정 훅과 도우미가 없다.

### `test_task_rules_follow_the_selected_roles_observation_contract` (행 540–584)
- 성질: 과제 실행을 시작할 때 과제의 초기 관찰 규칙은 선택된 역할의 관찰 계약을 따른다. `research_work`는 자기 점검 규칙을 실행 ID에 결박해 받고, `supplemental_research`는 받지 않으며, 과제의 규칙 원본은 바뀌지 않는다.
- 준비: 두 창을 넣은 설정의 프로필과 대상 `$execution`인 `checkpoint_count_gte` 규칙. `subTest`로 역할 `research_work`, `supplemental_research`마다 다음을 준비한다.
  - 새 `routing_engine`의 head와 설정을 정하고, 과제 `TK-one`에 그 규칙을 초기 관찰 규칙으로 둔다.
  - 배정 전 단계 대역을 둔다. `_check_installation`(참), `_clock_guard`(사용 가능), `_evaluation_context`, `_action_lifecycle_gate`, `_revision_dispatch_waits`(`[]`), `_selected_action_current`(참), `_obsolete_action_reason`(없음), `_execution_profile`(그 역할 프로필), `_activity_for_action`.
  - `_register_execution`은 지역 예외 `BeforeInput`을 던지게 해 입력 준비 전에 멈춘다.
  - `do_math.engine.tracker_config`를 `wraps`로 감시하고, `governance.authorize`(허용, `GR-one`)와 `planning.task_ready`(`ready`)를 패치한다.
- 실행: `next(engine._call_steps({'id': 'AC-one', 'role': role, 'target': 'TK-one'}))`.
- 단언: `BeforeInput`이 난다. 등록하려던 실행 ID와 감시된 `tracker_config`의 `initial_self_check_rules` 인자로 추적기를 다시 만들어 본다. `research_self_checks`와 `rules`의 유무가 모두 `role == "research_work"`와 같다. 규칙이 있으면 첫 규칙의 대상 ID가 그 실행 ID다. 과제의 `initial_observation_rules`가 원 규칙 그대로다.
- 대역: 위의 `create_autospec` 대역 열 개, `tracker_config` 감시, `authorize`와 `task_ready` 패치, `BeforeInput` 예외.
- 비고: `subTest` 케이스는 두 역할이다.

## 관계

- **다른 층의 같은 기능.** 추적기와 관찰 규칙의 세부 산술은 `test_observations`가 맡는다. 체크포인트 포획의 순수 함수와 게시 층은 `test_checkpoint_persistence`가 본다. 관찰 설정(두 창 값)의 입장은 `test_observation_admission`이 본다. `ControlTransport` 전반은 `test_control_transport`, 공급자 스트림 파싱은 이름으로 보아 `test_claude_stream`과 `test_codex_adapter`의 영역이다. `test_engine.PublicGitFlow`는 공개 흐름에서 `self_check` 도구가 `research_work` 결박에만 있다는 것을 확인해, 이 모듈의 역할별 관찰 계약과 맞물린다.
- **픽스처 의존.** `engine_fixtures.routing_engine`(소유자 경로의 메모리 엔진), `research_fixtures`의 관찰 도우미(`Clock`, `observation_rule`, `observe`, `acknowledge`, `write_checkpoint`, `observation_batch`), `provider_fixtures.Adapter`와 `runner_with`(러너와 수집기 대역), `record_fixtures`의 준비 수신자 도우미.
- **이 모듈에만 있는 도우미.** 모듈 함수는 없다. 시험 안의 지역 클래스 `Burst`, `LocalStream`, `PublishedStore`, `BeforeInput`과 지역 함수 `delayed`, `batch`가 있다.
- **겹치거나 보완하는 시험.**
  - 자기 점검 수신 확인과 놓침 판정은 세 시험이 나눠 본다. 폴링 성공 조건은 `test_native_poll_ack_requires_the_exact_successful_returned_request`, 확인 없는 명령은 `test_native_command_after_delivery_without_ack_is_only_missing_response_evidence`, 전달 전 위치의 명령은 `test_buffered_command_before_delivery_is_not_a_new_action_violation`이다.
  - 게시 원자성은 추적기 불전진(`test_failed_observation_publication_does_not_advance_the_tracker`), 복사 없는 되돌림(`test_failed_observation_rolls_back_to_the_published_state_without_copying_it_first`), 검토 행 재시도(`test_review_public_dialogue_keeps_raw_row_order_and_retries_after_failed_cas`)로 나뉜다.
  - "끝난 실행에는 실시간 검토가 없다"는 성질은 재생 스트림(`test_terminated_stream_replay_preserves_events_without_live_reviews`)과 실제 Job(`test_real_job_completion_is_observed_before_delayed_batch_application`)의 두 층에서 본다.

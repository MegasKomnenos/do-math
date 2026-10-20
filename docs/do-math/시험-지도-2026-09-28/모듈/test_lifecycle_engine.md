# test_lifecycle_engine

| 항목 | 값 |
|---|---|
| 조각 | `lifecycle` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_lifecycle_engine.py` (1103행) |
| 클래스 / 테스트 | 5 / 73 |
| 시험 대상 제품 코드 | `do_math/engine.py`의 `ResearchEngine`(수명 제어 `_apply_extended_control`, `_pause_lifecycle`, `_resume_lifecycle`, `_action_lifecycle_gate`, `_clock_guard`, `_require_action_clock`, `_lifecycle_event`, `_refresh_readiness`, `_consume_action_events`, `_check_conversations`, `_trust_control`, `_run_trust_check`, `_formal_environment`, `_process_machine_action`, `_run_external_action`, `_run_parallel`, `_check_limited_recovery`, `_limited_recovery_allowed`, `_execution_stop_requested`, `_capability_requirements`, `_session_resources`, `_queue_initial_intent`, `_retry_input_overflow_action`, `_complete_initial_intent`, `process_controls`, `control_result`), `read_record`; `do_math/scheduler.py`의 `_dispatchable`; `do_math/initialization.py`의 `initialize_state`, `original_input_bytes`, `capability_requirements`; `do_math/execution_profiles.py`(`build_profiles`, `profile_ref`, `capability_evidence`, `structural_failure_evidence`); `do_math/record_schemas.py`의 `RECORDS`, `RECORD_RULES`, `validate_lifecycle`; `do_math/external.py`·`external_engine.py`; `do_math/trust_inventory.py`; `do_math/knowledge.py`의 `plan_impact`, `capture_basis`; `do_math/academic.py`의 `current_requirements`, `solution_basis`; `do_math/governance.py`의 `validate_grant_source`; `setup_lean.rerecord` |
| 사용하는 픽스처 모듈 | `engine_fixtures`(`FakeEngine`, `initialized`, `initialized_instance`, `PublicInitializationRunner`); `research_fixtures`(`FixtureAdapter`, `IDENTITY`, `restore_template`, `send_control`, `activate`, `install_adapter_fixture`, `trust_fixture`, `fixture_setup_lean`); `state_fixtures`(`owner_calls`, `active_instance`); `provider_fixtures`(`HTTPFixtureHandler`) |
| 격리 표지 | 없음 |
| 시작 상태 | 대부분 메모리 엔진 대역 `FakeEngine`(`activate()`로 채택 결정까지 적용한 활성 상태). `PublicLifecycleTests`는 `engine_fixtures.initialized_instance` 템플릿(공개 `initialize`만), 4단 공개 초기화·활성화, 2단 `active_instance`를 섞는다. `PersistedConnections`는 4단. 1단 순수 함수 호출이 몇 개 있다 |

## 목적

모듈 docstring은 "기능 판본 5(Feature-five)의 수명 주기 통합 시험이며 CLI·Lean 관측은 명시적 대역"이라고 밝힌다. "기능 판본 5"는 이 docstring이 처음 들어온 커밋 `7d2597e`("do-math 기능 판본 5…")의 판본이며, 당시 인스턴스는 `feature_version` 5를 기록했다. 인스턴스 수명은 `initializing → active ⇄ paused → closed` 사이를 오가고, 그 전이를 공개 제어(`control` → `process_controls`)와 확장 제어(`_apply_extended_control`)가 일으킨다. 이 모듈은 다음을 검사한다.

- 수명 상태와 정지·재개·종결의 규칙, 영구 종결 표지.
- 시계 관문. UTC 수위(watermark)는 되돌아갈 수 없고, 시계 역행은 권한 판정보다 앞선다.
- 초기 권한과 연구 권한의 분리, 채택된 권한 가운데 유일하게 적격인 것의 선택.
- 사건(event)의 게시와 소비, 파생 준비도(readiness).
- 대화 연결(conversation)의 세대와 끊김 정책.
- 신뢰 환경의 등록, 전환, 재검사, 활성화.
- 제한 복구(limited recovery).
- 외부 HTTP 효과의 준비·전송·미확정·조정·재시도.
- 능력 증거의 판정.

대부분의 시험은 `FakeEngine`, 곧 제품 `ResearchEngine`을 메모리 상태와 저장 대역 위에 올린 엔진을 쓴다. 따라서 상태 전이 규칙은 실제 코드로 돌지만 Git 게시는 일어나지 않는다. 공개 경로와 Git 재적재가 대상인 시험만 `PublicLifecycleTests`와 `PersistedConnections`에 모여 있다.

## 모듈 수준 요소

- 행 11: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 넣는다.
- `run_machine(engine, role)` (행 22–25): 큐에서 `role`의 기계 행동 하나를 `state_fixtures.owner_calls(engine)` 블록 안에서 `engine.machine(role)`으로 처리한다. `owner_calls`는 블록을 나갈 때 시작된 호출의 콜백과 제어 전송 요청을 처리하고 연속(continuation)을 한 번 재개해, 스케줄러가 하는 일을 재현한다. 처리한 행동을 돌려준다. 신뢰 검사·활성화 시험 다수가 쓴다.
- 행 1103: 직접 실행하면 `unittest.main()`.

## PublicLifecycleTests (행 28–181)

`unittest.TestCase`를 상속한다. 설정 훅이 없다.

- `initializing()` (행 29–34): `restore_template(initialized_instance, goal='Preserve this original input', config={'scholarly_enabled': False})`로 공개 `initialize`만 돈 템플릿 사본을 받아 `(저장소 경로, 인스턴스 ID)`를 돌려준다. 활성화는 되어 있지 않다.

### `test_public_utc_watermark_is_published_only_with_normal_change` (행 36–62)
- 성질: 관측한 UTC 수위는 시계 관측만으로는 커밋을 만들지 않고 일반 변경과 함께 게시되며, 재시작한 엔진은 게시된 수위보다 이른 시계를 거부하고, 나중에 거부된 표본이 앞서 신뢰한 표본을 취소하지 않는다.
- 준비: `initializing()` 사본 위의 엔진. 먼저 `_save()`로 일반 파생 필드를 확정한다.
- 실행: `lifecycle_clock`을 2시간 뒤로, `lifecycle_monotonic`을 0으로 두고 `_require_action_clock()`, `_save()`. 제목을 바꿔 `_save()`. 재시작 엔진에 게시 수위보다 1마이크로초 이른 시계를 주고 `_clock_guard()`. 원 엔진에 +1시간 시계로 `_require_action_clock()`을 부른 뒤, +30분 시계로 `_clock_guard()`, `_pause_lifecycle('clock_regression')`, `_save()`.
- 단언: 시계 관측 뒤의 저장에서는 head가 그대로다(메시지 "clock observation alone created a commit"). 일반 변경 저장 뒤 `last_observed_utc`가 관측 시각이다. 재시작 엔진의 `_clock_guard()["reason"]`이 `persisted_utc_regression`이다. +30분 표본의 `usable`이 거짓이다. 정지 후 게시된 `last_observed_utc`가 +1시간 표본(`trusted`)이다.
- 대역: 시계 주입(`lifecycle_clock`, `lifecycle_monotonic`).
- 비고: 템플릿은 공개 `initialize`만 돈 상태다. 실제 Git 저장소 사본을 쓴다.

### `test_public_unicode_original_survives_restart` (행 64–70)
- 성질: 결합 문자를 담은 원 입력은 재시작 뒤에도 원래 UTF-8 바이트 그대로 복원된다.
- 준비: 4단. `initialized(root, goal='Café', ...)`.
- 실행: 새 `ResearchEngine`으로 다시 열어 `original_input_bytes(lifecycle.immutable_input)`.
- 단언: 반환이 `'Café'.encode()`와 같다.
- 대역: 없음.
- 비고: 같은 성질의 메모리 판본이 `LifecycleBoundaryTests.test_original_unicode_bytes_survive_canonical_roundtrip`이다.

### `test_public_initializing_pause_resume_preserves_source_and_missing` (행 72–95)
- 성질: 초기화 중 정지·재개는 `initializing`으로 돌아가고, 입력과 빠진 활성화 조건을 보존하며, 종결 뒤의 정지·재개는 거부된다.
- 준비: `initializing()` 사본. 런타임 `inputs` 사본을 떠 둔다.
- 실행: `send_control(engine, 'pause')`, `send_control(engine, 'resume')`, 재적재, `send_control(resumed, 'close')`, 이어서 공개 `control`로 `pause`와 `resume`을 각각 보내고 `process_controls`.
- 단언: 정지 직후 `resume_lifecycle`이 `initializing`이다. 재적재한 엔진의 수명 상태가 `initializing`이고, `inputs`가 사본과 같으며, `activation.missing`이 `independent_intent`를 담고, `availability`에 `missing` 키가 없다. 종결 뒤 `permanently_closed`가 참이다. 뒤이은 `pause`와 `resume` 요청은 각각 `control_result(...)["effect"]`가 `rejected`다. 다시 적재한 엔진의 상태가 `closed`이고 `permanently_closed`가 참이다.
- 대역: 없음.
- 비고: 주석은 재개 뒤의 같은 정지가 새 요청이라고 적는다.

### `test_public_call_mode_init_activate_pause_resume_and_persistence` (행 97–124)
- 성질: 호출 방식의 공개 초기화와 활성화가 `active`에 이르며, 그 뒤 `run(until_active=True)`은 아무것도 더 하지 않고, 정지·재개와 재적재 뒤에도 `active`와 파생값 비저장이 유지된다.
- 준비: 4단. `install_adapter_fixture`, `do_math.windows_job.named_job_empty`를 참으로 패치, `initialized(root, goal='Prove n + 0 = n', lean_command=['synthetic-lean'])`, `PublicInitializationRunner`를 단 엔진.
- 실행: `activate(engine, root, initialization_runner=engine.runner)`, `run(until_active=True)`, `send_control` 정지·재개, 재적재.
- 단언: 활성화 뒤 상태 `active`, `intent_imports`가 1개, `active_trust_environment`가 있다. 두 번째 `run(until_active=True)` 뒤 실행 ID 집합과 큐가 그대로다. 정지 뒤 `resume_lifecycle`이 `active`이고 재개 뒤 `active`다. 재적재한 엔진이 `active`이고 런타임에 `task_readiness`가 없으며 수명 기록에 `initial_request`가 없다.
- 대역: `FixtureAdapter`, `PublicInitializationRunner`(해석 역할만 답하는 합성 작성자·검사자, 실제 생산자·수신자 경로), `named_job_empty` 패치.
- 비고: 주석은 공개 초기화와 활성화가 이 시험의 대상이라 공개 경로를 유지한다고 적는다. `PublicInitializationRunner`는 로컬 Job을 띄우지 않고 Job 이름만 보고하므로 `named_job_empty` 패치가 종료 확인을 대신한다.

### `test_public_external_once_credential_resume_persists_attempts` (행 126–181)
- 성질: 자격 증명이 없어 멈춘 일회성 HTTP 효과는 공개 재요청과 재적재를 거쳐 새 시도로 이어지고, 원 시도의 기록은 바뀌지 않으며 두 시도는 같은 활동과 계보(`continuation_of`)로 묶인다.
- 준비: 2단. `restore_template(active_instance, config={'scholarly_enabled': False, 'lean_command': ['synthetic-lean']})`. 실제 루프백 `HTTPServer`를 데몬 스레드에서 돌리고, `HTTPFixtureHandler`를 상속한 `Handler`가 POST 수를 센다. `send_control`로 `reuse='once'`, 허용 origin·메서드·경로 접두 `/effect`, `credential_env={'X-Test': 'LIFECYCLE_AUDIT_TEST_TOKEN'}`인 HTTP 권한 `GR-public-http`를 적용하고, `external` 제어로 조작 `OP-public`을 준비한다.
- 실행: 환경변수를 지운 채 `_process_machine_action(action)`. 재적재 엔진에서 같은 설정을 `request_id='UC-public-external-credential-resume'`로 다시 보내고, 토큰을 넣은 환경에서 `_process_machine_action`. 다시 재적재해 읽는다.
- 단언: 첫 시도의 실행이 `ended`이고 POST 수가 0이다. 재시도 뒤 POST 수가 1이고 조작 상태가 `confirmed`이며 `waiting_reason`이 없다. `id`, `request_sha256`, `idempotency_key`가 첫 시도 때와 같다. 첫 실행 기록이 그대로 보존된다. 새 실행의 `continuation_of`가 첫 실행이고 `owner_activity_id`가 같으며, `submission_receipt.kind`가 `machine_output`, `outcome`이 `output_accepted`다. 두 실행의 전이 시각이 정렬되어 있다.
- 대역: `FixtureAdapter`, `patch.dict(os.environ)`.
- 비고: 주석은 대상이 공개 제어와 Git 재적재가 두 시도를 기록하는 방식이지 활성화가 아니므로 검증된 활성 상태에서 시작한다고 적는다. 실제 외부 자원은 루프백 HTTP 서버(127.0.0.1, 임의 포트)다.

## LifecycleTests (행 184–612)

`unittest.TestCase`를 상속한다. 표지는 없다.

- `setUp` (행 185–189): 임시 디렉터리를 만들고 `do_math.initialization.adapter_for`를 `FixtureAdapter()`로 패치한 뒤, `FakeEngine(temp)`을 만들어 `activate()`를 부른다. `FakeEngine.activate`는 다음을 차례로 적용한다. 초기 권한 `GR-init`, 연구 권한 `GR-research`, 헌장 `CH-test`, AI 프로필마다 `FixtureAdapter` 관측으로 만든 능력 증거, 채택 결정(`external_policy='explicit_grants'`, 기본 검토 정책, 대화 끊김 정책 `continue_authorized`), 기준 신뢰 환경 `base`의 등록과 전환. 이어서 작성자 `EX-interpret`와 검사자 `EX-check`의 해석을 `governance.prepare_import`, `check_import`, `apply_import`로 적용하고 `_complete_initial_intent`와 `_activate_initialization`을 부른 뒤 큐와 대기 이벤트를 비운다. 시계는 고정된 `current_time`이고 `_save`는 사본을 `saves`에 쌓는다.
- `transition()` (행 335–338): 지식 `K1`, `K2`를 만들고 새 신뢰 환경 `next`를 등록해 전환 제어를 보낸다. `(옛 환경, 새 환경, 전환 ID)`를 돌려준다.
- `olean(environment_id)` (행 385–386): 그 환경 툴체인 실행 파일의 두 단계 위 폴더 아래 `lib/lean/Init/Prelude.olean` 경로.
- `http(url)` (행 493–500): 그 origin만 허용하는 재사용 HTTP 권한 `GR-http`를 주고, 확장 제어 `external`로 조작 `EO-test`(`POST`, 본문 `test`)를 준비해 그 조작 기록을 돌려준다.

별도 언급이 없으면 각 시험의 준비는 이 `setUp`의 활성 `FakeEngine`이다.

### `test_controls_reach_active_and_separate_initial_authority` (행 190–196)
- 성질: 제어만으로 활성 상태에 이르고, 초기 권한은 활성 뒤 해석 역할에 쓸 수 없으며, 채택한 초기 프로필 참조는 실제 프로필로 해석된다.
- 준비: 클래스 절.
- 실행: `_action_lifecycle_gate({'role': 'intent_interpretation', 'grant_id': 'GR-init'})`, `ResearchEngine._execution_profile(e, {..., 'profile_ref': chosen})`.
- 단언: 상태 `active`, 권한 집합이 `{'GR-init', 'GR-research'}`다. 관문 호출은 `ValueError`(유형만)다. 해석된 프로필의 참조가 `adoption.initial_profile_ref`와 같다.
- 대역: `FakeEngine`, `FixtureAdapter`.

### `test_review_currentness_and_no_persisted_readiness` (행 197–214)
- 성질: 승인되지 않은 과제에는 계약 검토 요청이 하나만 생기고, 승인 뒤 준비도가 `ready`가 되어 스키마에 맞는 `task_became_ready` 사건이 나며, 정책이 바뀌면 준비도가 `not_ready`로 돌아간다. 준비도는 저장되지 않는다.
- 준비: 클래스 절에 미승인 과제 `T1`.
- 실행: `_refresh_readiness()` 두 번, `approve`, 큐 비우고 다시 계산, 확장 제어 `decision`으로 새 정책 `PO-new`, 다시 계산.
- 단언: 큐의 `task_contract_review`가 1개다. 승인 뒤 준비도 `ready`. 사건 `task_became_ready`가 `RECORDS['events']` 스키마(`Draft202012Validator`)를 통과하고 그 `basis.records`가 준비도의 `basis`와 같다. 과제 상태는 `planned`이고 런타임에 `task_readiness`가 없다. 정책 추가 뒤 준비도가 `not_ready`다. 모든 사건이 스키마를 통과한다.
- 대역: `FakeEngine`.

### `test_rejected_current_review_not_repeated` (행 215–217)
- 성질: 현재 판본에 대한 거부된 계약 검토는 다시 요청되지 않는다.
- 준비: 미승인 과제를 `rejected`로 판정한다.
- 실행: `_refresh_readiness()`.
- 단언: 큐에 `task_contract_review`가 없다.
- 대역: `FakeEngine`.

### `test_missing_input_and_bad_condition_distinct` (행 218–221)
- 성질: 없는 입력에 걸린 과제와 지원되지 않는 발생 조건을 가진 과제는 서로 다른 준비도 상태를 받는다.
- 준비: 입력 `absent`를 요구하는 과제 `T1`, 조건 `{'op': 'unsupported'}`의 과제 `T2`.
- 실행: `_refresh_readiness()`.
- 단언: 앞 과제가 `not_ready`, 뒤 과제가 `evaluation_error`다.
- 대역: `FakeEngine`.

### `test_completed_removes_readiness_projection` (행 222–224)
- 성질: 완료된 과제는 준비도 투영에서 빠진다.
- 준비: 과제 하나. 준비도를 계산한 뒤 상태를 `completed`로 바꾼다.
- 실행: `_refresh_readiness()`.
- 단언: `_task_readiness`에 그 과제가 없다.
- 대역: `FakeEngine`.

### `test_pause_returns_to_original_phase_and_preserves_events` (행 225–229)
- 성질: 정지 중에도 대기 사건은 보존되고, 거듭된 정지 뒤 재개하면 원래 단계(`active`)로 돌아간다.
- 준비: 사건 `user_input_available` 하나.
- 실행: 확장 제어 `pause`, `_refresh_readiness()`, 요청 ID `UI-again`의 `pause`, `resume`.
- 단언: 정지 중 그 사건이 `pending_events`에 있다. 재개 뒤 상태가 `active`다.
- 대역: `FakeEngine`.

### `test_published_event_is_not_mutated_when_assigned` (행 230–242)
- 성질: 게시된 사건은 행동에 배정되거나 소비되어도 그 기록이 바뀌지 않으며, 소비는 해당 사건만 대기에서 뺀다.
- 준비: `event_seq=1`을 붙인 사건과 그 사본.
- 실행: `_refresh_readiness()`, 둘째 사건 생성, `ResearchEngine._consume_action_events(e, {'event_refs': [event id]}, 'EX-accepted-plan')`.
- 단언: 계산 뒤 사건 기록이 사본과 같고, 대기 사건에 있으며, 어떤 큐 행동의 `event_refs`에 들어 있다. 소비 뒤 첫 사건은 대기에서 빠지고 둘째는 남으며, 첫 사건 기록은 여전히 사본과 같다.
- 대역: `FakeEngine`.

### `test_one_input_request_is_one_event_and_its_consumption_keeps_a_later_request` (행 243–256)
- 성질: 과제의 새 입력 요청 하나는 시간이 지나도 사건 하나이고, 그 사건을 소비해도 그 사이 생긴 나중 요청은 남는다.
- 준비: 과제 `T1`의 `newinput='RQ-one'`.
- 실행: 계산, 시계 +5초, 다시 계산. `newinput`을 `RQ-two`로 바꾸고 첫 사건 소비, 계산, 둘째 사건 소비.
- 단언: `task_new_input` 사건의 `request_id` 목록이 `['RQ-one']`이고 대기 목록에 한 번만 있다. 첫 소비 뒤 `newinput`이 `RQ-two`로 남는다. 둘째 소비 뒤 `newinput` 키가 없다.
- 대역: `FakeEngine`, 시계(`current_time`).

### `test_empty_queue_prepares_from_goal_exhaustion_regardless_of_cycle_count` (행 257–263)
- 성질: 큐가 비면 순환 횟수와 무관하게 목표 소진 근거를 담은 연구 준비가 생긴다.
- 준비: `cycles=1000`.
- 실행: `_refresh_readiness()`.
- 단언: `research_preparation` 행동이 있고 `exhaustion_basis`를 가지며 그 `exhausted`가 참이다.
- 대역: `FakeEngine`.

### `test_conversation_requires_new_live_generation` (행 264–270)
- 성질: 끊김 정책 `pause`인 대화가 임대 만료로 끊기면, 새 세대로 다시 붙기 전에는 재개도 옛 세대의 심박도 거부된다.
- 준비: 대화 `chat`을 세대 1, 임대 10초, 끊김 정책 `pause`로 붙인다.
- 실행: 시계 +11초, `_check_conversations()`, `resume`, 세대 1 `heartbeat`, 세대 2 `attach`, `resume`.
- 단언: 끊긴 뒤 `resume`과 세대 1 심박은 각각 `ValueError`다. 세대 2로 붙인 뒤 재개하면 상태가 `active`다.
- 대역: `FakeEngine`, 시계.

### `test_continue_alias_is_rejected_without_changing_conversation` (행 271–277)
- 성질: 끊김 정책 별칭 `continue`는 거부되고 상태를 바꾸지 않는다.
- 준비: 상태 사본.
- 실행: `disconnect_policy='continue'`인 `attach`.
- 단언: `ValueError`(메시지 `'conversation loss policy'`). 상태가 사본과 같다.
- 대역: `FakeEngine`.

### `test_continue_policy_does_not_pause` (행 279–283)
- 성질: 끊김 정책 `continue_authorized`인 대화가 끊기면 대화만 `lost`가 되고 인스턴스는 멈추지 않는다.
- 준비: 임대 1초로 붙인 대화.
- 실행: 시계 +2초, `_check_conversations()`.
- 단언: 대화 상태가 `lost`, 수명 상태가 `active`다.
- 대역: `FakeEngine`, 시계.

### `test_control_replay_and_atomic_rejection` (행 284–289)
- 성질: 같은 요청 ID와 같은 내용의 제어 재전송은 무효과이고, 같은 ID에 다른 내용은 상태를 바꾸지 않고 거부된다.
- 준비: 요청 ID `UI-fixed`로 대화를 붙인 뒤의 상태 사본.
- 실행: 같은 요청 재전송, 세대만 2로 바꾼 같은 ID 요청.
- 단언: 재전송 뒤 상태가 사본과 같다. 다른 내용은 `ValueError`이고 상태가 여전히 사본과 같다.
- 대역: `FakeEngine`.

### `test_empty_trust_activation_records_profile_bound_machine_execution` (행 290–300)
- 성질: 검사할 형식 결과가 없는 신뢰 전환의 활성화도 프로필에 결박된 기계 실행으로 기록된다.
- 준비: 지식 없이 새 환경 `empty-transition`을 등록하고 전환 제어를 보낸다.
- 실행: `run_machine(e, 'trust_activate')`.
- 단언: `trust_activate` 실행이 정확히 1개이고, `ended`, `output_accepted`, 수신증 종류 `machine_output`, `execution_profile_ref`를 가진다. 소유 활동이 `finished`다.
- 대역: `FakeEngine`, `trust_fixture` 합성 툴체인.

### `test_trust_transition_uses_current_storage_contract` (행 302–308)
- 성질: 신뢰 전환 기록은 현재 저장 스키마를 따른다.
- 준비: 새 환경 `schema-transition`의 전환 제어.
- 실행: 마지막 전환 기록을 `jsonschema.validate(..., RECORDS['trust_transitions'])`.
- 단언: 검증 예외가 없다.
- 대역: `FakeEngine`.

### `test_initial_grant_does_not_queue_research_before_activation` (행 311–316)
- 성질: 활성화 전 초기 권한을 주어도 연구 행동이 큐에 들어가지 않는다.
- 준비: `setUp`의 엔진과 별개로 활성화하지 않은 새 `FakeEngine`.
- 실행: `grant('GR-initial', True)`.
- 단언: 권한이 생기고 큐가 `[]`다.
- 대역: `FakeEngine`.

### `test_initial_intent_receipt_cannot_replace_import_evidence` (행 318–328)
- 성질: 초기 의도의 완료는 가져오기(import) 묶음의 검사 해시, 적용 상태, 원문이 모두 맞아야 하며, 하나라도 바뀌면 거부된다.
- 준비: 원 `intent_imports` 사본.
- 실행: `subTest`로 `field` ∈ {`check`, `application`, `source`}마다 사본을 되돌리고 각각 `check.bundle_sha256='0'*64`, `application.status='awaiting_decision'`, `source.text='different original'`로 바꾼 뒤 `_complete_initial_intent(input_id)`.
- 단언: 세 경우 모두 `ValueError`(유형만)다.
- 대역: `FakeEngine`.
- 비고: `subTest` 케이스는 세 필드다.

### `test_formal_requires_preapproved_environment` (행 330–334)
- 성질: 형식 검사 환경은 미리 승인된 활성 신뢰 환경뿐이다.
- 준비: 클래스 절.
- 실행: `_formal_environment()`. 이어서 `active_trust_environment=None`으로 둔 뒤 다시 부른다.
- 단언: 반환 환경의 ID가 활성 환경과 같다. 비운 뒤에는 `ValueError`다.
- 대역: `FakeEngine`.

### `test_full_transition_preserves_old_formal_records_and_full_command` (행 339–350)
- 성질: 신뢰 전환은 모든 대상의 재검사가 끝나야 새 환경을 활성화하고, 옛 형식 결과를 바꾸지 않으며, 검증기는 등록된 전체 명령으로 불린다.
- 준비: `transition()`. 형식 결과 사본.
- 실행: `_formal_environment()`, `trust_check` 두 번, `trust_activate`.
- 단언: 전환 중 `_formal_environment()`는 `ValueError`다. 첫 검사 뒤에는 활성 환경이 옛 것이고 활성화 뒤에는 새 것이다. 옛 형식 결과가 모두 그대로다. 모든 검증기 호출의 `lean_command`가 `expected_toolchain.configured_command`와 같다. 모든 실행이 `execution_profile_ref`와 `owner_activity_id`를 가지며, `trust_check` 실행은 `output_accepted`이고 수신증 종류가 `machine_output`이다.
- 대역: `FakeEngine.verify`(합성 형식 검증).

### `test_trust_recheck_needs_no_grant_naming_the_trust_roles` (행 351–360)
- 성질: 신뢰 재검사와 활성화는 신뢰 역할을 이름으로 담은 권한이 없어도, 사용자의 전환 제어를 권한으로 삼아 진행된다.
- 준비: 모든 권한의 `roles`에서 `trust_check`와 `trust_activate`를 뺀 뒤 `transition()`.
- 실행: `trust_check` 두 번, `trust_activate`.
- 단언: 상태가 `active`이고 활성 환경이 새 것이다.
- 대역: `FakeEngine`.
- 비고: 주석은 문서화된 연구 권한이 연구 역할과 `formal_check`만 담는다고 하며 `초기화-운전` 3절을 가리킨다(`references/초기화-운전.md`).

### `test_partial_failure_cannot_activate` (행 361–366)
- 성질: 재검사 하나라도 실패하면 전환은 활성화되지 않는다.
- 준비: `transition()`. 검증기 동작을 `{'status': 'failed'}`로 둔다.
- 실행: `trust_check` 두 번, `trust_activate`.
- 단언: 활성 환경이 옛 것이고 전환 상태가 `failed`다.
- 대역: `formal_behavior`.

### `test_wrong_compiler_is_rejected` (행 367–370)
- 성질: 다른 툴체인 해시를 보고한 검증 결과는 거부된다.
- 준비: `transition()`. 검증 결과의 `toolchain`만 `{'sha256': 'wrong'}`으로 바꾸는 동작.
- 실행: `trust_check` 한 번.
- 단언: 전환 결과 `K1`의 상태가 `rejected`다.
- 대역: `formal_behavior`.

### `test_changed_semantics_requires_independent_review` (행 371–380)
- 성질: 선언의 의미(타입)가 바뀐 재검사 결과는 전환을 활성화하지 않고 독립 검토를 연다.
- 준비: `transition()`. 모든 선언의 `declaration_evidence`를 `{'type': 'changed'}`로 바꾸는 동작.
- 실행: `trust_check` 두 번, `trust_activate`.
- 단언: 활성 환경이 옛 것이고 전환 상태가 `ready`이며, 그 전환 ID를 가진 검토 주기가 2개다. 이 수는 `transition()`이 만든 지식 `K1`, `K2`의 수와 같지만, 지식 수 자체는 단언하지 않는다.
- 대역: `formal_behavior`.

### `test_completed_target_not_repeated_on_recovery` (행 381–384)
- 성질: 이미 끝난 재검사 대상은 복구 때 다시 컴파일되지 않는다.
- 준비: `transition()` 뒤 `trust_check` 한 번.
- 실행: 같은 행동으로 `_run_trust_check(a)`를 직접 다시 부른 뒤 `trust_check`, `trust_activate`.
- 단언: 직접 재호출 뒤 검증기 호출 수가 그대로다. 끝에 새 환경이 활성이다.
- 대역: `FakeEngine.verify`.

### `test_changed_olean_blocks_trust_check_before_compiling` (행 387–396)
- 성질: 새 환경의 `.olean` 파일이 바뀌면 재검사는 컴파일 전에 신뢰 환경 오류로 실패한다.
- 준비: `transition()` 뒤 새 환경의 `Prelude.olean` 바이트를 바꾼다.
- 실행: `trust_check`.
- 단언: 결과 상태 `failed`, `error_kind` `trust_environment`, 사유에 `'olean fingerprint differs'`, `environment_check.changed_files`가 `['toolchain/lib/lean/Init/Prelude.olean']`이다. 검증기가 한 번도 불리지 않았다.
- 대역: `trust_fixture` 합성 툴체인 파일(실제 파일 시스템).

### `test_registration_reads_the_shared_record_without_scanning_files` (행 397–413)
- 성질: 신뢰 환경 등록은 공유 툴체인 기록을 읽을 뿐 파일을 훑거나 해시하지 않으며, 같은 기록으로 두 번 등록할 수 있고, 결박이나 공리 목록이 다르면 거부된다.
- 준비: 새 `trust_fixture(root/'shared', ...)` 요청.
- 실행: `trust_inventory.observe_fingerprint`와 `content_hashes`를 호출 금지로 패치하고 `_trust_control`을 두 번. 결박 지문을 0으로 바꾼 요청, 공리 하나를 중복한 요청.
- 단언: 같은 툴체인의 환경이 2개이고 각각 `toolchain_record`와 런타임 결박이 요청과 같다. 지문을 바꾼 요청은 `ValueError`(`'differs from its toolchain record'`)다. 공리 중복은 `ValueError`(`'foundation axiom profile differs'`)이고 환경 목록이 그대로다.
- 대역: 두 호출 금지 패치.

### `test_rerecorded_baseline_is_followed_once_with_an_event` (행 414–432)
- 성질: 재기록된 툴체인 기준(baseline)은 재검사가 한 번 따라가 결박을 갱신하고 사건 하나를 남기며, 활성화는 상태와 검증 수신증만 더한다.
- 준비: `transition()`. 새 환경의 `.olean` 수정 시각을 1초 늦추고, `fixture_setup_lean` 안에서 `setup_lean.rerecord`로 기록을 다시 만든다.
- 실행: `trust_check` 두 번, `trust_activate`.
- 단언: 새 환경이 활성이고 결박이 재기록 결박과 같다. `trust_environment_rebound` 사건이 정확히 1개이고 `(previous, current)`가 (옛 결박, 새 결박)이다. 활성 환경에서 `validation_receipt`를 빼고 `status`를 `registered`로 둔 것이 원래 환경 기록과 같다. 수신증의 `binding`이 새 결박이다.
- 대역: `fixture_setup_lean`(호스트 관측을 합성 툴체인으로 대체한 `setup_lean`).
- 비고: 실제 파일 시스템의 수정 시각과 재기록을 쓴다.

### `test_clock_regression_precedes_authority` (행 433–438)
- 성질: 시계 역행은 권한 판정보다 먼저 거부된다.
- 준비: `last_observed_utc`를 현재보다 1초 뒤로 둔다.
- 실행: `grant('GR-bad')`, `_action_lifecycle_gate({'role': 'external_action'})`.
- 단언: 둘 다 `ValueError`(메시지 `'clock'`). 권한이 그대로다.
- 대역: `FakeEngine`.

### `test_dispatch_uses_current_task_predicate` (행 440–451)
- 성질: 과제 작업의 배정 가능성은 현재 과제의 준비 조건으로 판정하며, 과제 상태나 저장된 준비도 값을 믿지 않는다.
- 준비: 과제 `T1`과 행동 `AC-work`. `_revision_dispatch_waits`(`[]`), `_selected_action_current`(참), `_provider_status`(빈 공급자)를 `autospec`으로 패치한다.
- 실행: `_dispatchable(a)` 세 번. 처음, 입력 `absent`를 더한 뒤, 입력을 비우고 과제 `status='ready'`와 가짜 `task_readiness`를 넣은 뒤.
- 단언: 처음은 참이고 입력을 더하면 거짓이다. 세 번째도 거짓이며, 행동의 `dispatch_wait.kind`가 `task_readiness`다.
- 대역: 세 가지 `patch.object`.
- 비고: 세 번째 경우가 거짓인 이유는 이 시험이 단언하지 않는다. 과제 상태를 `ready`로 바꾼 것이 현재 조건 평가에서 준비되지 않은 상태로 판정된다는 사실만 확인한다.

### `test_task_artifact_context_reaches_refresh_and_dispatch` (행 453–471)
- 성질: 산출물 유효성 조건을 가진 과제는 준비도 계산과 배정 판정 모두에서 실제 산출물 읽기 문맥을 받는다.
- 준비: 저장소를 `create_autospec(ResearchRepository, instance=True)`로 바꾸고 `read`가 `{"valid":true}` 바이트를 돌려주게 한다. 조건 `artifact_valid`(스냅숏 `sealed-evidence`, 경로와 SHA-256)인 과제를 승인한다.
- 실행: `_refresh_readiness()`. 앞 시험과 같은 세 패치를 두고 `_dispatchable(a)`.
- 단언: 준비도가 `ready`다. 배정이 참이다. `_selected_action_current`가 받은 `evaluation_context`의 `validate_artifact`가 호출 가능하고, `read_artifact(path, 'sealed-evidence')`가 원 바이트를 돌려준다. 저장소 `read`의 모든 호출 인자가 `(path, 'sealed-evidence')`다.
- 대역: 저장소 자동 사양 대역, 세 가지 `patch.object`.

### `test_stop_and_resume_trust_check_preserves_attempt_lineage` (행 473–483)
- 성질: 정지로 중단된 신뢰 재검사는 결과를 남기지 않고, 재개 뒤 다음 시도는 같은 활동에서 앞 시도의 계보를 잇는다.
- 준비: `transition()`. 검증기 동작이 `_pause_lifecycle('test_pause')`를 부르고 `{'status': 'stopped'}`를 돌려준다.
- 실행: `trust_check`. 동작을 해제하고 `resume`, 다시 `trust_check`.
- 단언: 첫 시도가 `ended`이고 전환 결과에 `K1`이 없다. 두 번째 시도의 `owner_activity_id`가 같고 `continuation_of`가 첫 시도다.
- 대역: `formal_behavior`.

### `test_assigned_events_survive_and_live_input_is_not_changed` (행 485–491)
- 성질: 실행 중인 계획이 입력으로 가진 행동은 새 사건이 와도 바뀌지 않고, 두 사건 모두 대기로 남는다.
- 준비: 사건 하나와 계산으로 생긴 계획 행동, 그 행동을 입력으로 가진 `running` 실행 `EX-live`.
- 실행: 둘째 사건 생성, `_refresh_readiness()`.
- 단언: 원 계획 행동이 사본과 같다. 두 사건 ID가 모두 대기 사건에 있다.
- 대역: `FakeEngine`.

### `test_real_loopback_unknown_reconcile_and_retry_share_activity` (행 502–533)
- 성질: 응답이 불확실한 HTTP 효과는 `unknown`이 되고, 구조화된 증거로 조정하기 전에는 재시도할 수 없으며, 조정 뒤 재시도는 같은 활동에서 계보를 잇는다.
- 준비: 모든 POST에 503과 본문 `uncertain`을 답하는 실제 루프백 `HTTPServer`. `http(url)`로 조작 준비.
- 실행: `machine('external_action')`. 재시도 제어, 문자열 증거의 조정 제어, 구조화 증거(`evidence_ref`, 조작 ID, 요청 해시, 멱등 키, `fact='effect_absent'`, 관측 시각)의 조정 제어, 재시도 제어, 다시 `machine`.
- 단언: 첫 전송 뒤 `http_status` 503, 상태 `unknown`, `succeeded`가 `None`이다. 조정 전 재시도와 문자열 증거 조정은 각각 `ValueError`다. 재시도 뒤 조작 상태가 `prepared`이고 `handling`과 `reconciliation` 키가 없다. 그 기록이 `RECORD_RULES['external_operations']`를 통과한다. 두 번째 전송 뒤 서버 POST 수가 2이고, 두 실행이 같은 `owner_activity_id`와 `continuation_of` 계보를 가진다.
- 대역: 없음(실제 HTTP).
- 비고: 실제 외부 자원은 루프백 HTTP 서버다. 주석은 새 시도가 조정된 시도가 아니므로 처리 기록은 조정과 함께 간다고 적는다.

### `test_revocation_before_transport_cancels` (행 535–541)
- 성질: 전송 전에 권한이 철회되면 조작이 취소되고 전송이 일어나지 않는다.
- 준비: `http('http://127.0.0.1:1/effect')`.
- 실행: 확장 제어 `revoke`, `_run_external_action(...)`.
- 단언: 조작 상태가 `cancelled`이고 `do_math.external._http`가 불리지 않는다.
- 대역: `_http` 패치.

### `test_prepare_replay_preserves_unknown_ledger` (행 543–548)
- 성질: 이미 전송되어 `unknown`인 조작에 같은 준비 제어를 다시 보내도 장부가 바뀌지 않는다.
- 준비: 조작을 `status='unknown'`, `transmitted=True`로 바꾼 사본.
- 실행: 같은 요청의 `prepare` 제어.
- 단언: 조작 기록이 사본과 같다.
- 대역: `FakeEngine`.

### `test_capability_evidence_rejects_changed_host_or_forged_record` (행 550–556)
- 성질: 능력 증거는 호스트 식별이 바뀌거나 증거 기록의 식별이 위조되면 충족되지 않는다.
- 준비: 해석 역할의 프로필 참조.
- 실행: `_capability_requirements(ref)`를 세 번. 그대로, `FixtureAdapter.capability_identity`를 `{'host': 'different'}`로 패치해서, 모든 증거의 `identity`를 `{'forged': True}`로 바꿔서.
- 단언: 처음만 `satisfied`가 참이고 나머지 둘은 거짓이다.
- 대역: `capability_identity` 패치.

### `test_changed_fixed_source_never_activates_transition` (행 558–563)
- 성질: 고정된 형식 원문이 바뀌면 전환은 활성화되지 않는다.
- 준비: `transition()` 뒤 `K1` 형식 결과의 `lean_code`에 주석 한 줄을 덧붙인다.
- 실행: `trust_check` 두 번.
- 단언: 활성 환경이 옛 것이다.
- 대역: `FakeEngine.verify`.

### `test_http_success_finishes_activity_without_changing_effect_fact` (행 565–574)
- 성질: 성공한 HTTP 전송은 조작을 `confirmed`로, 실행을 `output_accepted`로 끝내고 활동을 마친다.
- 준비: `http(...)`.
- 실행: `_http`가 `{'http_status': 201, 'body': b'created'}`를 돌려주도록 패치하고 `machine('external_action')`.
- 단언: 조작 `confirmed`, `succeeded is True`, 활동 `finished`, 실행 `output_accepted`, 수신증 종류 `machine_output`.
- 대역: `_http` 패치.
- 비고: 이름의 "효과 사실을 바꾸지 않는다"는 부분에 대응하는 별도 단언은 없다.

### `test_authority_revoked_at_send_gate_prevents_transport` (행 576–585)
- 성질: 전송 단계 바로 앞의 관문에서 권한 철회가 적용되면 전송하지 않고 취소한다.
- 준비: `http(...)`. `_apply_inbox`를 `create_autospec`으로 바꿔 네 번째 호출에서 권한 상태를 `revoked`로 만든다(주석: 외부 정지 판정은 전송 단계마다 먼저 받은 편지함을 적용한다).
- 실행: `_http`를 패치하고 `machine('external_action')`.
- 단언: `_http`가 불리지 않고 조작 상태가 `cancelled`다.
- 대역: `_apply_inbox` 대역, `_http` 패치.

### `test_failure_before_any_send_step_is_an_untransmitted_cancellation` (행 587–594)
- 성질: 전송 단계 전에 실패하면 조작은 미전송 취소로 기록된다.
- 준비: `http(...)`.
- 실행: `do_math.external_engine.execute_operation`을 `ValueError('grant is inactive')`로 패치하고 `machine('external_action')`.
- 단언: 저장 대역에서 다시 읽은 조작의 `(status, transmitted, succeeded)`가 `('cancelled', False, False)`이고 `RECORD_RULES['external_operations']`를 통과한다.
- 대역: `execute_operation` 패치.

### `test_session_capacity_reads_git_reservations_not_sqlite` (행 596–600)
- 성질: 세션 용량은 상태의 예약에서 계산되고 SQLite 슬롯 폴더를 쓰지 않는다.
- 준비: 클래스 절.
- 실행: `_session_resources()`.
- 단언: 결과가 비어 있지 않고, 모든 행의 키 집합이 `{'limit', 'used', 'execution_ids', 'available'}`이며, `root/'session-slots'`가 없다.
- 대역: `FakeEngine`.
- 비고: 이름은 "Git 예약"을 말하지만 `FakeEngine`은 Git을 쓰지 않는다. 단언은 결과 모양과 옛 슬롯 폴더의 부재만 본다.

### `test_invalidated_split_knowledge_invalidates_dependent_goal` (행 602–612)
- 성질: 목표 판정이 의존하는 지식을 무효화하면 목표가 미해결로 돌아가고 그 판정은 현재가 아니게 된다.
- 준비: 지식 `K1`, `goal_status='mathematically_solved'`, `K1`에 의존하는 현재 목표 판정 `G1`(`capture_basis`).
- 실행: `plan_impact`로 영향을 계산하고, 확장 제어 `knowledge`로 `invalidate`와 선언 영향을 보낸다.
- 단언: `goal_status`가 `unsolved`, `G1.current`가 거짓이다.
- 대역: `FakeEngine`.

## LifecycleBoundaryTests (행 614–833)

`unittest.TestCase`를 상속한다. 클래스 docstring은 "메모리 엔진 위의 시계, 신뢰, 제한 복구, 종결 경계"라고 밝힌다. 설정 훅이 없어 시험마다 `FakeEngine`을 직접 만들며, 필요한 시험만 `adapter_for` 패치와 `activate()`를 부른다.

### `test_event_uses_the_clock_sample_that_passed_the_guard` (행 617–625)
- 성질: 사건의 시각은 시계 관문을 통과한 그 표본이며, 뒤에 읽은 다른 표본이 아니다.
- 준비: 활성화하지 않은 `FakeEngine`. 시계가 차례로 +2초, +1초를 돌려준다.
- 실행: `_lifecycle_event('test_clock_observation', schedule=False)`.
- 단언: 사건 `at`과 `last_observed_utc`가 +2초 표본이다.
- 대역: 시계 반복자.

### `test_scheduler_scopes_maintenance_dispatch_with_executor_double` (행 627–655)
- 성질: 정지 중 스케줄러는 승인된 제한 복구 행동 하나만 배정하고, 일반 연구 행동은 남기며 정지를 유지한다.
- 준비: 활성화 뒤 정지. 대상 `RI-test` 한정의 일회성 정비 권한 `GR-repair`. 큐는 `AC-repair`(정비)와 `AC-general`(준비). `limited_recovery` 결정(목적, 절차, 5분 만료).
- 실행: `_call_steps`를 실행기 대역으로 바꾼다. 이 대역은 관문을 통과시키고 실행 `EX-repair`를 등록해 기록한 뒤 `execution_incomplete`로 끝내고 큐에서 뺀다. `_check_installation`, `_provider_status`, `_selected_action_current`, `_revision_dispatch_waits`도 `create_autospec` 대역으로 두고 `_run_parallel(max_steps=1)`.
- 단언: 배정된 역할 목록이 `['maintenance']`, 상태 `paused`, 큐 첫 행동이 `AC-general`이다.
- 대역: `_call_steps` 실행기 대역과 네 가지 자동 사양 대역.

### `test_wrong_pinned_trust_command_ends_attempt_without_verifier` (행 657–671)
- 성질: 옛 프로필(다른 신뢰 명령)을 고정한 신뢰 검사 시도는 검증기를 부르지 않고 미완으로 끝난다.
- 준비: 활성화, 지식 `K1`, 현재 `trust_check` 프로필 참조, 새 환경 `next`의 전환. 큐의 `trust_check` 행동에 옛 참조를 고정한다.
- 실행: `owner_calls` 안에서 `_process_machine_action(action)`.
- 단언: 검증기 호출이 없다. 실행이 `ended`, `execution_incomplete`이고 끝나지 않은 실행이 없다.
- 대역: `FakeEngine`.

### `test_terminal_marker_cannot_have_live_projection` (행 673–681)
- 성질: 영구 종결 표지가 있는 인스턴스의 런타임 상태는 `closed`여야 한다.
- 준비: 활성화하지 않은 엔진에 `permanently_closed=True`.
- 실행: `validate_lifecycle`을 두 번(상태를 `closed`로 바꾸기 전과 뒤).
- 단언: 앞은 `ValueError`(`'permanently closed'`), 뒤는 통과한다.
- 대역: 없음.

### `test_scheduler_runs_only_approved_machine_recovery_and_stays_paused` (행 683–707)
- 성질: 정지 중에도 승인된 기계 복구(빈 전환의 활성화)는 실제로 돌아 새 환경을 활성화하되, 인스턴스는 정지로 남고 일반 행동은 큐에 남는다.
- 준비: 활성화, 새 환경 `repair`의 전환, 정지, `trust_activate` 한정 일회성 권한, 그 행동의 `limited_recovery` 결정. 큐 앞에 `AC-general`을 끼운다. `_check_installation`, `_selected_action_current`, `_revision_dispatch_waits`는 대역.
- 실행: `_run_parallel(max_steps=1)`.
- 단언: 활성 환경이 `repair`, 런타임과 수명 상태 모두 `paused`, 큐에 `AC-general`이 있다. 마지막 `trust_activate` 실행이 `ended`이고 수신증 상태가 `accepted`다.
- 대역: 세 가지 자동 사양 대역.

### `test_changed_transition_opens_real_review_without_live_publication` (행 709–728)
- 성질: 의미가 바뀐 재검사는 실제 검토 주기와 그 행동을 열지만, 지식과 형식 결과 계열은 바꾸지 않는다.
- 준비: 활성화, `K1`, 새 환경 `next`. 전환 전 인스턴스 사본.
- 실행: 전환 제어, 선언 타입을 `'Changed proposition'`으로 바꾸는 동작, `trust_check`, `trust_activate`.
- 단언: 전환 상태 `ready`, 그 전환의 검토 주기가 1개이고 그 주기를 가리키는 큐 행동이 있다. `knowledge`, `formal_results`, `identity_assessments`, `assessment_uses` 네 계열이 사본과 같다.
- 대역: `formal_behavior`.
- 비고: `LifecycleTests.test_changed_semantics_requires_independent_review`는 지식이 둘이고 검토 주기 수 2를 본다. 이 시험은 지식이 하나이고, 게시되는 지식 계열이 바뀌지 않음을 본다.

### `test_trust_verifier_uses_registered_command_without_deadline` (행 730–743)
- 성질: 신뢰 검증기는 등록된 명령으로 불리고 시간 상한 인자를 받지 않는다.
- 준비: 활성화, `K1`, 새 환경. 그 명령으로 만든 `trust_check` 프로필을 역할 참조로 둔다.
- 실행: 전환 제어, `trust_check`.
- 단언: 검증기 호출이 1번이고 `timeout_seconds` 키가 없으며 `lean_command`가 등록 명령이다.
- 대역: `FakeEngine.verify`.

### `test_paused_recovery_is_exact_authorized_and_revocable` (행 745–771)
- 성질: 정지 중 제한 복구는 결정이 가리킨 정확한 행동에만 허용되고, 새 비상 정지나 새 정지가 오면 철회된다.
- 준비: 활성화 뒤 정지. 대상·목적 한정 일회성 정비 권한과 행동 `AC-repair`, 그 `limited_recovery` 결정.
- 실행: `_check_limited_recovery`, `_action_lifecycle_gate`, `_limited_recovery_allowed`, `_execution_stop_requested`. `stop_requested`를 `new_emergency_stop`으로 바꿨다가 되돌리고, 대상 `RI-other` 행동과 `research_preparation` 행동으로 관문을 부르고, `_pause_lifecycle('new_pause')`.
- 단언: 처음에는 허용이 참이고 정지 요청이 거짓이며 상태가 `paused`다. 비상 정지 중에는 허용이 거짓이다. 다른 대상과 다른 역할은 `ValueError`다. 새 정지 뒤 허용이 거짓, 정지 요청이 참이다.
- 대역: `FakeEngine`.

### `test_limited_recovery_refuses_unbound_requests_and_surfaces_check_defects` (행 773–781)
- 성질: 제한 복구에 결박되지 않은 요청은 검사 없이 거부되고, 결박된 요청의 검사 결함은 삼키지 않고 드러난다.
- 준비: 활성화하지 않은 엔진.
- 실행: `_check_limited_recovery`를 호출 금지로 패치하고 결박 없는 `AC-plain`으로 `_limited_recovery_allowed`. 이어서 `KeyError('defect')`를 던지게 패치하고 `repair.limited_recovery`를 가진 `AC-bound`로 호출.
- 단언: 앞은 거짓이다. 뒤는 `KeyError`가 전파된다.
- 대역: `_check_limited_recovery` 패치 두 번.

### `test_closed_pause_cannot_reopen` (행 783–792)
- 성질: 종결된 인스턴스는 정지로도 재개로도 다시 열리지 않는다.
- 준비: 상태를 `closed`로 둔 엔진과 상태 사본.
- 실행: `_pause_lifecycle('user_pause')`, `_resume_lifecycle({'origin': 'user'})`.
- 단언: 둘 다 `ValueError`이고, 정지 시도 뒤 상태가 사본과 같다.
- 대역: 없음.

### `test_close_control_seals_terminal_marker` (행 794–802)
- 성질: 종결 제어는 영구 종결 표지를 세우고 큐를 비우며, 그 뒤 정지·재개를 거부한다.
- 준비: 활성화하지 않은 엔진.
- 실행: 확장 제어 `close`, `pause`, `resume`.
- 단언: `close`의 반환이 참이고, `permanently_closed` 참, 상태 `closed`, 큐 `[]`다. 뒤의 두 제어는 `ValueError`다.
- 대역: 없음.

### `test_original_unicode_bytes_survive_canonical_roundtrip` (행 804–818)
- 성질: 원 입력은 정규 JSON 왕복 뒤에도 원래 바이트로 복원되고, 원문이 바뀌면 해시 불일치로 거부된다.
- 준비: 1단. `initialize_state(..., goal='Café', source_input='Café')`.
- 실행: `json.loads(canonical_json(instance))`, `original_input_bytes`.
- 단언: 복원 바이트가 원문 UTF-8과 같고, `text`가 원문이며, 런타임 첫 입력의 `sha256`이 원 입력의 것과 같다. `text='wrong'`으로 바꾸면 `ValueError`다.
- 대역: 없음.

### `test_negative_job_is_not_cleared_by_later_help_probe` (행 820–833)
- 성질: 실제 실행이 남긴 구조적 실패 증거(원자적 로컬 Job 불가)는 나중의 도움말 관측이 긍정해도 지워지지 않는다.
- 준비: 정비 프로필의 `structural_failure_evidence`(실행 `EX-failed`)와 1초 뒤의 `capability_evidence`(`FixtureAdapter` 관측).
- 실행: 2초 뒤 시각으로 `capability_requirements(..., current_identity=IDENTITY)`.
- 단언: `satisfied`가 거짓이고 `missing`이 `atomic_local_job`을 담는다.
- 대역: `FixtureAdapter().describe()`.

## GrantAndExternalEffectTests (행 835–1078)

`unittest.TestCase`를 상속한다. 클래스 docstring은 "권한의 채택과 선택, 초기 큐, 외부 HTTP 효과와 그 제어"라고 밝힌다.

- 클래스 속성 `setUp = LifecycleTests.setUp` (행 838): 설정 훅을 공유한다. 따라서 시작 상태는 `LifecycleTests` 절과 같은 활성 `FakeEngine`이다.
- `prepare_http(*, once=False, credentials=False, scope=None, origin='http://127.0.0.1:1')` (행 963–972): HTTP 권한 `GR-http-audit`(`reuse`는 `once` 또는 `reusable`, 허용 경로 접두 `/effect`)를 결정 제어로 적용하고, 필요하면 `credential_env`와 범위 필드를 더한다. 조작 `OP-audit` 준비 제어의 설정을 돌려주되 보내지는 않는다.

### `test_machine_records_use_registered_schema_and_existing_source_provenance` (행 840–866)
- 성질: 외부 조작과 기계 실행(외부 효과·신뢰 활성화·신뢰 검사)의 기록은 등록된 스키마를 통과하고, 원천 참조가 실제 통치 원문을 가리킨다.
- 준비: 클래스 절. `prepare_http()` 설정을 제어로 보낸다.
- 실행: 조작과 준비 사건 검사, `_http`를 201로 패치한 `machine('external_action')`, 새 환경 `audit-schema`의 전환과 `trust_activate`, `LifecycleTests.transition(self)`, `trust_check` 두 번.
- 단언: 조작 기록이 스키마 오류 없이 통과한다(`iter_errors` 목록이 `[]`). `external_operation_prepared` 사건의 `source_ref`가 `governance_sources`에 있다. 전송 뒤 조작 기록도 통과한다. 세 역할의 모든 실행이 `executions` 스키마를 통과하고 `action.source_ref`를 가지며, 신뢰 역할은 `result_ref`가 수신증의 `evidence_ref`와 같다.
- 대역: `_http` 패치.
- 비고: `LifecycleTests.transition`을 다른 클래스의 인스턴스로 호출한다.

### `test_ambiguous_adopted_grants_are_not_selected_by_order` (행 868–877)
- 성질: 채택된 연구 권한 가운데 적격이 둘 이상이면 순서로 고르지 않고 거부하며, 명시한 권한은 받아들인다.
- 준비: 권한 `GR-other`를 더하고 채택 목록을 `['GR-other', 'GR-research']`로 둔다.
- 실행: 권한 없는 준비 행동으로 관문 호출. `grant_id='GR-research'`를 명시한 행동으로 호출.
- 단언: 앞은 `ValueError`(`'ambiguous'`)이고 행동에 `grant_id`가 붙지 않는다. 뒤는 통과하고 `grant_id`가 그대로다.
- 대역: `FakeEngine`.

### `test_initial_queue_does_not_manufacture_explicit_grant_choice` (행 879–892)
- 성질: 초기 해석 큐는 초기 권한을 임의로 골라 붙이지 않고, 적격 초기 권한이 하나일 때만 관문이 그것을 고른다.
- 준비: 초기 권한 `GR-init-other`를 더하고, 수명을 `initializing`으로 되돌려 `intent_check`를 지우고, 초기 권한 목록을 둘로 둔다. 큐를 비운다.
- 실행: `_queue_initial_intent()`, 관문 호출, 목록을 `['GR-init']`로 줄인 뒤 관문 호출.
- 단언: 해석 행동에 `grant_id`가 없다. 앞 관문은 `ValueError`(`'ambiguous'`)다. 뒤 관문 뒤 `grant_id`가 `GR-init`이다.
- 대역: `FakeEngine`.

### `test_initial_queue_treats_held_input_overflow_as_the_same_request` (행 894–906)
- 성질: 입력 초과로 보류된 초기 해석 요청이 있으면 초기 큐는 새 행동 ID로 다시 만들지 않는다.
- 준비: 수명 `initializing`, 보류 행동 `AC-held-overflow`(종류 `input_overflow`)를 `waiting_actions`에 둔다. 큐를 비운다.
- 실행: `_queue_initial_intent()`.
- 단언: 큐가 `[]`다.
- 대역: `FakeEngine`.

### `test_retry_reuses_the_exact_held_action_and_current_authority` (행 908–934)
- 성질: 입력 초과 대기의 재시도는 보류된 정확한 행동(같은 ID, 활동, 프로필)을 다시 큐에 넣고, 막고 있던 질문은 열어 둔 채이며, 종결된 인스턴스에서는 거부된다.
- 준비: 준비 행동을 관문에 통과시켜 활동을 얻고, 활동을 `input_overflow` 조건으로 대기시키고, 차단 질문을 연결한 뒤, 보류 행동을 `waiting_actions`에 둔다.
- 실행: `ResearchEngine._retry_input_overflow_action(e, {'id': 'UC-retry', 'config': {'retry_action': ...}})`. 상태를 `closed`로 바꾸고 다시 부른다.
- 단언: 재시도 행동의 `id`, `owner_activity_id`, `profile_ref`가 원래 것이다. 활동이 `ready`이고 대기에서 빠졌다. 질문 상태는 `open`이다(메시지: 요청은 이제 입력이 들어간다는 증명이 아니다). 종결 뒤 호출은 `ValueError`(`'closed/completed'`)다.
- 대역: `FakeEngine`.

### `test_adoption_preserves_approved_grants_and_disjoint_initial_scope` (행 936–951)
- 성질: 채택은 승인된 권한 기록(`initialization_only` 포함)을 그대로 보존하고, 초기 권한과 연구 권한이 같은 권한이면 거부한다.
- 준비: 클래스 절 엔진, 그리고 별도의 새 `FakeEngine`에 초기 권한 `GR-narrow`.
- 실행: 권한마다 `validate_grant_source`. 초기 권한으로 해석 관문 호출. 새 엔진에서 초기·연구 목록이 모두 `GR-narrow`인 `adopt` 결정.
- 단언: 권한의 `initialization_only`가 결정에 적힌 값과 같고 원천 검증을 통과한다. 해석 관문은 `ValueError`다. 같은 권한 채택은 `ValueError`(`'distinct grants'`)이고 권한 목록이 그대로다.
- 대역: `FakeEngine`.

### `test_unique_eligible_grant_within_adoption_and_explicit_denial` (행 953–961)
- 성질: 채택된 권한 가운데 행동에 적격인 것이 하나뿐이면 그것이 선택되고, 부적격 권한을 명시하면 거부된다.
- 준비: `GR-other`의 `included_targets`를 `['different']`로 좁히고 채택 목록을 둘로 둔다.
- 실행: 권한 없는 준비 행동으로 관문, `GR-other`를 명시한 행동으로 관문.
- 단언: 앞은 `grant_id`가 `GR-research`가 된다. 뒤는 `ValueError`다.
- 대역: `FakeEngine`.

### `test_scoped_http_control_preserves_exact_envelope` (행 974–987)
- 성질: 범위가 있는 HTTP 권한 아래 준비된 조작은 대상·목적·주체·실행 종류를 그대로 보존하고, 다른 목적의 준비는 거부된다.
- 준비: `prepare_http(scope=...)`(대상 `TARGET`, 목적 `publish`, 주체 `publisher`, 실행 종류 `machine`).
- 실행: 네 필드를 더한 준비 제어, `_http` 201 패치로 `machine`, 목적만 `different`로 바꾼 준비 제어.
- 단언: 조작의 네 필드가 보낸 값과 같다. 전송이 1번이다. 목적을 바꾼 제어는 `ValueError`다.
- 대역: `_http` 패치.

### `test_once_http_first_send_and_distinct_request` (행 989–995)
- 성질: 일회성 HTTP 권한은 첫 전송을 허용하고, 다른 조작 ID의 두 번째 준비는 거부한다.
- 준비: `prepare_http(once=True)`.
- 실행: 준비 제어, `_http` 201 패치로 `machine`, ID `OP-other`의 준비 제어.
- 단언: 전송 1번, 상태 `confirmed`, 두 번째 준비 `ValueError`.
- 대역: `_http` 패치.

### `test_once_unknown_send_cannot_be_replayed_without_evidence` (행 997–1009)
- 성질: 일회성 조작의 전송 결과가 불확실하면 증거 없이 재시도나 재실행할 수 없다.
- 준비: `prepare_http(once=True)`와 준비 제어.
- 실행: `_http`를 `TimeoutError`로 패치하고 `machine`. 재시도 제어. `_http` 패치 아래 `_run_external_action(action)`.
- 단언: 첫 전송 1번 뒤 상태 `unknown`. 재시도 `ValueError`. 직접 재실행은 `_http`를 부르지 않고 조작의 `execution_id`가 그대로다.
- 대역: `_http` 패치 두 번.

### `test_academic_control_binds_current_real_prerequisite` (행 1011–1028)
- 성질: 학술 전제를 요구하는 HTTP 권한 아래의 조작은 현재 풀이 근거가 있을 때만 준비되고 그 근거와 요구 해시에 결박되며, 전송 전 근거가 사라지면 전송하지 않고 취소된다.
- 준비: `prepare_http(scope={'requires_academic': True})`. `_solution_basis`를 대역으로 바꿔 `goal_status`가 `mathematically_solved`일 때만 형식 결과로 `solution_basis`를 만들게 한다.
- 실행: 근거 없이 준비 제어. 지식 `K-academic`을 만들고 목표를 풀린 상태로 둔 뒤 준비 제어. 목표를 `unsolved`로 돌리고 `_http` 패치 아래 `machine`.
- 단언: 첫 준비는 `ValueError`다. 두 번째 뒤 조작의 `academic_basis`가 `{'solution_basis': basis, 'requirements_sha256': current_requirements(...)['sha256']}`와 같다. 전송은 불리지 않고 상태가 `cancelled`다.
- 대역: `_solution_basis` 대역(주석: 상류 증명 결과는 합성이고 결박과 학술 전제 소비자는 실제), `_http` 패치.

### `test_credential_resume_has_new_attempt_receipt_and_cleared_wait` (행 1030–1078)
- 성질: 자격 증명 부재로 멈춘 조작의 재개는 새 시도와 새 수신증을 만들고 대기를 지우며, 두 시도의 전이 순서는 인과적으로 이어지고 모든 시각이 UTC다.
- 준비: 클래스 절. 실제 루프백 서버와 POST 수를 세는 `HTTPFixtureHandler` 하위 클래스. `prepare_http(credentials=True, origin=...)`. 시계를 실제 호스트 시계로 되돌린다(`lifecycle_clock=None`, `lifecycle_monotonic=time.monotonic`, `_clock_anchor=None`, 주석: 고정 픽스처 시각을 쓰지 않는다).
- 실행: 준비 제어. 환경변수를 지우고 `_http` 패치 아래 `machine`. 같은 준비 제어를 다시 보내고 토큰을 넣은 환경에서 `machine`.
- 단언: 첫 시도에서 전송이 없고 실행이 `ended`다. 재개 뒤 POST 수 1, 조작의 `execution_id`가 새 실행이다. 첫 실행 기록이 그대로이고, 새 실행의 `continuation_of`와 `owner_activity_id`가 이어지며, `output_accepted`와 수신증 종류 `machine_output`를 가진다. 조작에 `waiting_reason`이 없고 `id`, `request_sha256`, `idempotency_key`가 그대로다. 두 실행 모두 첫 전이가 `queued`에서 시작하고 마지막 전이가 `ended`로 끝나며, 인접 전이의 `to`와 `from`이 이어지고, 모든 `at`의 UTC 오프셋이 0이며, `ended_at`이 마지막 전이 시각이다.
- 대역: 첫 시도의 `_http` 패치, `patch.dict(os.environ)`.
- 비고: 실제 외부 자원: 루프백 HTTP 서버. `PublicLifecycleTests.test_public_external_once_credential_resume_persists_attempts`가 같은 흐름을 Git 재적재와 공개 제어로 본다. 이 시험은 메모리 엔진에서 전이 순서와 시각 형식까지 본다.

## PersistedConnections (행 1081–1100)

`unittest.TestCase`를 상속한다. 설정 훅과 도우미가 없다.

### `test_new_instance_is_v5_initializing_without_implicit_authority` (행 1082–1100)
- 성질: 새 인스턴스는 `initializing` 상태로 게시되고, 암묵적 권한과 큐 행동이 없으며, 레코드 조회는 게시된 바이트에 맞는 증거를 돌려주고, 첫 실행은 모델을 부르지 않는다.
- 준비: 4단. `initialized(root/"repo", goal="Prove the stated goal", ...)`.
- 실행: `ResearchRepository.load`, 첫 실행 프로필에 대한 `read_record(..., snapshot=head)`와 그 경로의 `read`, `Mock` 러너를 단 엔진의 `run(max_steps=1)`.
- 단언: 게시된 상태가 `initializing`, 큐 `[]`, 권한 `{}`다. 조회 결과의 `sha256`과 `bytes`가 읽은 바이트의 해시·길이와 같고 `snapshot`이 head다. 실행 뒤 상태가 `initializing`이고 `runner.run`이 불리지 않았다.
- 대역: `Mock` 러너.
- 비고: 이름의 "v5"는 저장 계약 판본이 아니라 기능 판본 5다. 이 시험을 들여온 커밋 `7d2597e`의 원형은 `instance["feature_version"] == 5`를 단언했다. 현재 원문에는 그 단언이 없어서 이름의 "v5"에 대응하는 단언이 없고, 판본 번호를 확인하지 않는다.

## 관계

- **다른 층의 같은 기능.**
  - 활성화 관문은 `test_lifecycle_gates`, 신뢰 전환은 `test_trust_continuation`, 외부 효과는 `test_external`과 `test_external_operations`, 권한과 통치 결정은 `test_governance`와 `test_governance_engine`이 따로 검사한다. 이 목록은 모듈 이름으로 고른 것이다.
  - 초기 의도의 완료 증거는 `test_initial_intent_connection`이 순수 함수(`initial_intent_evidence`)로 검사한다. 이 모듈의 `test_initial_intent_receipt_cannot_replace_import_evidence`는 엔진 쪽(`_complete_initial_intent`)을 본다.
  - 입력 초과 재시도 `_retry_input_overflow_action`은 `test_initial_intent_connection.InitialFailureRetryTests`도 공개 제어 경로로 검사한다.
- **픽스처 의존.** `engine_fixtures.FakeEngine`이 중심이다. 그 `activate`, `grant`, `environment`, `knowledge`, `task`, `approve`, `machine`, `verify`, `formal_behavior`, `formal_calls`, `current_time`을 쓴다. `state_fixtures.owner_calls`는 기계 행동의 호출 수명을 재현한다. `research_fixtures.trust_fixture`와 `fixture_setup_lean`은 합성 툴체인, `provider_fixtures.HTTPFixtureHandler`는 201 응답 서버다. 공개 경로 시험은 `initialized`, `initialized_instance`, `active_instance`, `activate`, `PublicInitializationRunner`를 쓴다.
- **이 모듈에만 있는 도우미.** `run_machine`, `PublicLifecycleTests.initializing`, `LifecycleTests.transition`, `olean`, `http`, `GrantAndExternalEffectTests.prepare_http`.
- **겹치거나 보완하는 시험.**
  - 유니코드 원 입력은 공개 재적재(`test_public_unicode_original_survives_restart`)와 정규 JSON 왕복(`test_original_unicode_bytes_survive_canonical_roundtrip`)의 두 층에서 본다.
  - 자격 증명 재개는 공개 판본과 메모리 판본이 한 쌍이다.
  - 의미 변경 전환은 `test_changed_semantics_requires_independent_review`(검토 주기 수)와 `test_changed_transition_opens_real_review_without_live_publication`(게시 계열 불변)이 나눠 본다.
  - 정지 중 제한 복구는 정비 배정 범위(`test_scheduler_scopes_maintenance_dispatch_with_executor_double`), 실제 기계 복구(`test_scheduler_runs_only_approved_machine_recovery_and_stays_paused`), 허가와 철회(`test_paused_recovery_is_exact_authorized_and_revocable`), 결박 없는 요청(`test_limited_recovery_refuses_unbound_requests_and_surfaces_check_defects`)으로 나뉜다.

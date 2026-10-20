# test_family_records

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_family_records.py` (1260행) |
| 클래스 / 테스트 | 2 / 75 |
| 시험 대상 제품 코드 | `do_math/repository.py`의 `ResearchRepository`(`initialize`, `load`, `load_records`, `save_with_state`, `validate_candidate`, `read_record`, `read`, `list_files`, `_store.publish`, `_store.read_snapshot`, `contract`), `canonical_json`, `exact_content_hash`, `_encode_cursor`, `_decode_cursor`; `do_math/events.py`의 `EventPublisher.assign_sequences_in_place`, `check_sequence`; `do_math/git_store.py`의 `GitStateStoreConflict`; `do_math/state_contract.py`의 `default_state_contract`와 `StateContract.register_family`; `do_math/record_schemas`의 `RECORDS`. 저장 대상 기록을 만드는 생산자는 다음과 같다. `knowledge_io`(`import_candidate`, `import_relation`, `ensure_ontology`), `knowledge_records.create_candidate`, `knowledge`(`validate_basis`, `capture_basis`, `begin_transition`, `record_transition_result`, `activate_transition`, `assess_use`), `contracts`(`task_candidate_record`, `TASK_CANDIDATE`, `prompt_metrics`, `schema_for`), `planning.contract_hash`, `governance`(`preserve_source`, `apply_decision`, `governance_view`, `validate_grant_source`), `execution_profiles`(`build_profiles`, `host_constraint`, `resolve_profile`, `with_host_resources`, `seal_profile`, `profile_ref`, `HOST_ROLES`), `session_slots.SessionSlots`, `execution_lifecycle`(`create_execution`, `transition_execution`, `record_submission_intent`, `begin_preparation`, `end_preparation`), `activities.assign_execution`, `execution_window.publish`, `observations`(`preserve_checkpoint`, `ObservationTracker`), `context_store.fit_context`, `external`(`prepare_operation`, `execute_operation`, `reconcile_operation`, `prepare_retry`), `model_policy.selection`, `academic.record_resolution`, `questions.link`, `revisions.bind_repetition_bases`, `initialization`(`initialize_state`, `original_input_bytes`), `submission`(`extension_schema`, `payload_issues`), `review_policy.build_review_policy`, `trust_validation`(`check_environment`, `environment_errors`), `engine`(`initialize`, `ResearchEngine`, `_apply_task_plan`, `_start_staged_identity_review`, `_finish_trust_transition`, `_save`) |
| 사용하는 픽스처 모듈 | `research_fixtures`: `current_state`, `git_init`, `governance_start`, `installed_contract`, `with_validator`, 함수 안에서 `candidate`, `approved_governance`, `charter`, `sealed_maintenance_submission`, `bare_engine`, `disposition`, `send_control`, `trust_fixture`. `record_fixtures`: `execution_state`, 함수 안에서 `two_observation_output`, `research_work_context`. `review_fixtures`: `reviewed_candidate`, 함수 안에서 `deferred_research_cycle`, `ImpactReviewHarness`. `knowledge_fixtures`: 함수 안에서 `knowledge_candidate`, `formal_evidence`. `engine_fixtures`: 함수 안에서 `FakeEngine` |
| 격리 표지 | 없음 |
| 시작 상태 | `FamilyRecordStorageTests`: `setUp`이 시험마다 임시 폴더에 실제 Git 저장소와 기본 계약의 `ResearchRepository`를 만든다. 기록은 대부분 1단식으로 메모리에서 조립한다(`current_state`, `execution_state` 등). 세 시험은 4단(공개 `initialize`와 제어)이다. `ProducerStorageContractTests`: 1단 |

## 목적

모듈 docstring은 이 모듈의 계약을 한 문장으로 말한다. 상태는 기록 가족(record family) 파일로 저장되고, 기록은 Git 저장을 거쳐도 형식과 닫힌 모양(closed)을 유지하며, 읽기(load)는 계약에 등록되지 않은 것을 거부한다. 제품 쪽 정본은 `ResearchRepository`의 docstring "Read and publish the record-family files of the installed state contract through one Git CAS."(`repository.py` 228행)다.

시험은 네 무리로 나뉜다.
1. 저장 계층 일반. 가족 파일 배치(`research/<가족>/<ID>.json`, `runtime/events/...`, `_state/metadata.json`, `_state/manifest.json`), 닫힌 스키마, 전역 ID 유일성, 참조 무결성, 등록되지 않은 가족·필드 거부, 계약 판본과 객체 형식 강제, 변경 없는 저장의 무쓰기, CAS 경합과 호출자 불변을 본다.
2. 공개 사건 번호(`event_seq`). 공개 경계에서 연속 번호를 매기고, 이미 공개한 사건의 내용·번호·존재를 바꾸지 못하며, 번호는 정확한 정수다.
3. 생산자 왕복. 각 제품 생산자가 실제로 만든 기록이 저장·재적재 뒤에도 같다. 한 필드를 망가뜨리면 저장 계약이 그 영역의 사유로 거부한다. 대상은 과제, 거버넌스, 호스트 예약, 실행 창, 체크포인트, 제출 권한 회수, 영향 검토 요청, 입력 준비, 외부 작업, 모델 선택, 학술 해결, 질문, 관계, 초기화, 신뢰 환경, 검토 주기, 연속 판정 등이다. 이 무리가 가장 크다.
4. Unicode 정확성. 분해형 결합 부호(`é`), 켈빈 기호(`K`), CRLF가 과제 설명, 경로 지정자, 거버넌스 원문, 등록 가족 페이로드, 조회 커서에서 그대로 보존된다.

## 모듈 수준 요소

- 행 16: `sys.path.insert(0, ...parents[1])`로 `scripts/`를 경로 앞에 넣는다(중복 확인 없음).
- 행 5–25: import. `subprocess`는 두 시험이 `git`을 직접 부르는 데 쓴다. `jsonschema`는 스키마 조각을 직접 검사하는 데 쓴다. `contracts`와 `knowledge_io`는 `ProducerStorageContractTests`가 쓴다.
- `INSTANCE_ID` (행 28): `"RI-01ARZ3NDEKTSV4RRFFQ69G5FAV"`. 기본 저장소와 여러 시험의 인스턴스 ID다. 계약을 따로 둔 두 번째 저장소는 마지막 글자만 다른 `"RI-01ARZ3NDEKTSV4RRFFQ69G5FAW"`를 쓴다(원문에 직접 적는다).
- 행 1259–1260: 직접 실행하면 `unittest.main()`.

## FamilyRecordStorageTests (행 31–1222)

`unittest.TestCase`를 상속한다. 클래스 표지와 클래스 속성이 없다. 설정 훅은 클래스 본문 중간(행 573)에 있지만 모든 시험 메서드에 적용된다.

- `setUp` (행 573–578): `tempfile.TemporaryDirectory()`를 `self.temporary`에 둔다. 그 아래 `repository/` 폴더를 만들어 `self.repository_path`에 두고 `git_init`으로 빈 저장소를 만든다. 기본 계약의 `self.repository = ResearchRepository(repository_path, INSTANCE_ID)`를 둔다. 저장소 생성자는 `git rev-parse`를 자식 프로세스로 부르므로, 이 클래스의 모든 시험이 실제 Git 자식 프로세스를 쓴다.
- `tearDown` (행 580–581): `self.temporary.cleanup()`.
- `task_with_reference_locators()` (행 59–72): `reference_fixture_instance()`의 `research_work` 프로필과 `research_fixtures.candidate('Reference locator fixture')`로 과제 후보를 만든다. `inputs=['source:NatAddZero.lean', 'tool:lean']`, `basis_refs=['context:goal', 'context:policy', 'tool:lean']`, `profile_refs`, `authority_refs=['GR-reference']`를 넣는다. `contracts.task_candidate_record(wire, task_id='TK-reference-locators')`로 저장형 과제를 만들고, `revises_task_id`를 지우고, `status='planned'`로 둔다.
- `reference_fixture_instance()` (행 74–84): `DEFAULT_CONFIG`에 `lean_command=['fixture-lean']`, `scholarly_enabled=False`를 둔 설정으로 프로필을 만든다. 보존 원문 `GS-reference`를 가진 거버넌스 시작 상태를 `current_state`로 감싼다. `apply_decision`으로 `research_work` 역할의 local grant `GR-reference`를 적용한다.
- `_approved_governance()` (행 863–868): `charter('CH-1', rationale='Study P', desired_result='Proof', ...)`를 `approved_governance({'id': INSTANCE_ID}, ..., source=('GS-1', 'Study P'), approval_id='DC-1')`로 채택한 인스턴스를 `current_state`로 감싸 돌려준다.

아래 항목의 "준비"에 적지 않은 한, 시작 상태는 `setUp`의 빈 Git 저장소와 기본 계약 저장소다. 음성 단언은 대부분 `validate_candidate`, `save_with_state`, `load`가 `ValueError`를 내는지 보고, 정규식이 있으면 함께 적는다.

### `test_relation_claim_endpoint_basis_survives_storage_and_remains_typed` (행 32–58)
- 성질: 관계 주장 기록의 끝점 기준(`relation_endpoint_basis`)은 Git 왕복 뒤에도 같고 여전히 유효하다. 저장 계약은 잘못된 모양의 기준을 이 필드 이름으로 거부한다.
- 준비: `current_state()`에 비형식 후보 두 개(`source`, `target`)를 가져오고, `formally_implies` 관계 주장을 가진 후보 `relation proof`를 가져온다.
- 실행: `initialize`, `load(head)`, `knowledge.validate_basis`. 잘못된 기준 셋으로 `validate_candidate(changed, running, head)`를 부른다. 셋은 `{}`, `sha256='bad'`인 행, `status`가 빠진 행이다.
- 단언: 다시 읽은 기준이 저장 전과 같고 유효하다. 잘못된 셋 모두 `ValueError`를 메시지 `"relation_endpoint_basis"`로 낸다.
- 대역: 없음.
- 비고: `subTest(invalid=...)` 세 개. `test_knowledge_io.test_relation_claim_endpoint_basis_matches_the_storage_contract`의 스키마 검사를 실제 저장 경로로 옮긴 짝이다.

### `test_wire_task_description_survives_storage_and_binds_contract` (행 86–109)
- 성질: 과제 후보의 설명(`description`)은 결합 부호와 CRLF까지 그대로 저장되고 과제 계약 해시에 묶인다. 빈 값이나 문자열이 아닌 설명은 저장 계약이 거부한다.
- 준비: `task_with_reference_locators()`에서 `TASK_CANDIDATE` 속성만 골라 wire를 만든다. `description='Exact task explanation é\r\n'`, `revises_task_id=None`을 넣어 `task_candidate_record`로 다시 만든다. `planning.contract_hash(task)`를 떠 둔다.
- 실행: `reference_fixture_instance()`와 이 과제를 가진 런타임으로 `initialize`, `load`. 이어 잘못된 설명 넷으로 `validate_candidate`.
- 단언: 저장된 설명이 입력과 같고 계약 해시가 같다. 설명만 바꾼 사본의 해시는 다르다. `''`, `'   '`, `3`, `None`은 모두 `ValueError`(유형만)다.
- 대역: 없음.
- 비고: `subTest(description=...)` 네 개.

### `test_task_input_and_basis_locators_survive_actual_git_storage` (행 111–119)
- 성질: 과제의 입력·근거 지정자와 참조 필드가 Git 왕복 뒤에도 같다.
- 준비: `task_with_reference_locators()`. `basis_refs`에 `'context:goal'`, `inputs`에 `'source:NatAddZero.lean'`이 있는지 먼저 확인한다.
- 실행: `initialize`, `load`.
- 단언: `inputs`, `basis_refs`, `reuse`, `dependencies`, `authority_refs`, `profile_refs`가 저장 전과 같다.
- 대역: 없음.

### `test_task_source_path_locators_keep_exact_unicode_in_git` (행 121–130)
- 성질: 과제의 출처 경로 지정자는 Unicode를 정확히 유지한다.
- 준비: 지정자 목록 `['source:é.lean', 'input/sources/K.lean', 'runtime/artifacts/BA-source/report.md', 'context:policy', 'tool:lean']`을 `inputs`와 `basis_refs`에 둔다.
- 실행: `initialize`, `load`.
- 단언: 두 필드가 목록 그대로다.
- 대역: 없음.

### `test_task_locator_storage_does_not_widen_record_or_profile_authority` (행 132–143)
- 성질: 지정자 문자열(`context:goal`)은 기록·프로필·권한을 가리키는 필드에는 들어갈 수 없다. 지정자 허용은 입력·근거 필드에 한정된다.
- 준비: 입력과 근거를 비운 과제를 저장하고 다시 읽는다.
- 실행: `reuse`, `dependencies`, `authority_refs`, `profile_refs` 각각을 `['context:goal']`로 바꿔 `validate_candidate`.
- 단언: 각각 `ValueError`를 그 필드 이름을 담은 메시지로 낸다(`assertRaisesRegex(ValueError, field)`).
- 대역: 없음.
- 비고: `subTest(field=...)` 네 개.

### `test_final_goal_assessment_keeps_its_recorded_group_key_in_git` (행 145–148)
- 성질: 최종 목표 평가의 묶음 열쇠(`goal_assessment_basis`)가 Git 왕복 뒤에도 같다.
- 준비: `current_state({'goal_assessment_basis': 'a'*64})`.
- 실행: `initialize`, `load`.
- 단언: 인스턴스의 `goal_assessment_basis`가 `'a'*64`다.
- 대역: 없음.

### `test_scoped_review_research_request_survives_action_storage` (행 150–159)
- 성질: 검토 보충 조사 행동의 요청 ID(콜론을 포함하는 범위 ID)가 대기열 저장을 거쳐도 그대로다.
- 준비: `review_fixtures.deferred_research_cycle()`의 첫 조사 요청 ID로 `supplemental_research` 행동(`slot='research-'+ID`, `stage='investigating'`)을 만든다. ID에 `':'`이 있는지 확인한다.
- 실행: 대기열에 이 행동을 둔 런타임으로 `initialize`, `load`.
- 단언: 요청 ID에 `':'`이 있고, 다시 읽은 대기열이 `[action]`과 같다.
- 대역: 없음.

### `test_lossless_query_cursor_retains_exact_search_text` (행 161–164)
- 성질: 조회 커서의 부호화·복호화는 검색 문자열의 결합 부호까지 손실 없이 되돌린다.
- 준비: 커서 `{'snapshot': 'a'*40, 'prefix': 'research/', 'text': 'é', 'last_path': 'research/a.json'}`.
- 실행: 비공개 함수 `_decode_cursor(_encode_cursor(cursor))`.
- 단언: 원래 커서와 같다.
- 대역: 없음.
- 비고: 1단. 저장소를 쓰지 않는다(`setUp`의 저장소는 만들어진다).

### `test_plain_exact_json_rejects_invalid_stored_records_on_git_read` (행 166–182)
- 성질: 저장소에 직접 써 넣은 잘못된 기록(미등록 필드, 틀린 형식)은 읽기에서 거부된다. 읽기 경로도 닫힌 스키마를 검사한다.
- 준비: `installed_contract()`에 연구 가족 `exact_negative`를 닫힌 스키마로 등록한다. 스키마는 `id`와 `payload.text` 문자열만 허용한다. 이 계약으로 `self.repository`를 새로 만들고, `payload.text='é'`인 `EN-1`을 저장한다.
- 실행: `read_record('EN-1', head)`의 바이트를 읽고, 페이로드를 `{'text': 'valid string', 'unknown': 'forbidden'}` 또는 `{'text': 3}`로 바꾼다. 이를 `self.repository._store.publish(head, {path: canonical_json(broken)})`로 검증 없이 공개한 뒤 `load(head)`를 부른다.
- 단언: 두 경우 모두 `ValueError`(유형만).
- 대역: 없음. 저장소의 비공개 `_store.publish`로 검증을 우회해 쓴다.
- 비고: `subTest(payload=...)` 두 개.

### `test_exact_singleton_root_is_typed_without_wrapper_autodetection` (행 184–195)
- 성질: 단일(singleton) 가족의 루트 값은 등록된 모양으로 형식이 정해진다. 파일 속 감싸개(wrapper)를 추측해 풀지 않고, 기록 좌표는 `/record`다.
- 준비: 런타임 단일 가족 `exact_history`를 배열 스키마(`value` 문자열 객체), `identity=False`로 등록한 계약과 저장소를 만든다. 값은 `[{'value': 'é\r\n'}]`이다.
- 실행: `initialize`, `load`, `load_records(head)[3]`에서 이 가족의 서술자를 찾는다.
- 단언: 다시 읽은 값이 입력과 같고, 서술자의 `json_pointer`가 `'/record'`다.
- 대역: 없음.

### `test_registered_exact_payload_keeps_closed_logical_validation_and_file_coordinates` (행 197–222)
- 성질: 등록 가족의 정확한 페이로드는 논리 검증(닫힌 스키마)을 유지하고, 파일 좌표(경로, 바이트 해시, `json_pointer`)와 논리 기록이 일치한다. 같은 상태를 다시 저장하면 새 커밋을 만들지 않는다. 검증은 호출자의 후보를 바꾸지 않는다.
- 준비: 연구 가족 `exact_fixture`를 등록한다. 스키마는 `id`, `machine` 문자열, 문자열 값만 받는 `payload`다. 기록은 `{'id': 'EF-1', 'machine': 'é', 'payload': {'K': 'é\r\n', 'K': 'é'}}`다.
- 실행: `validate_candidate`, `initialize`, `load`, `read_record`, `read(path)`, 같은 상태로 `save_with_state`. 끝으로 페이로드 `K`를 정수 7로 바꿔 `validate_candidate`.
- 단언: 검증 뒤 원래 기록의 `machine`이 `'é'` 그대로다(주석 "pure candidate"). 검증 결과의 `machine`도 같다. 다시 읽은 페이로드와 파일 속 `record.payload`가 입력과 같다. 서술자의 `sha256`이 `bytes`의 SHA-256과 같고, `json_pointer`가 `'/record'`, `record`가 읽은 기록과 같다. 같은 상태 저장이 같은 `head`를 돌려준다. 정수 페이로드는 `ValueError`다.
- 대역: 없음.

### `test_governance_original_text_survives_lossless_git_and_immutable_check` (행 224–234)
- 성질: 거버넌스 보존 원문은 결합 부호와 CRLF까지 Git에 그대로 저장된다. 정규형만 다른 원문으로 바꿔 저장하려 하면 불변 규칙이 거부한다.
- 준비: `preserve_source('GS-exact', 'Prove that "é" contains two Unicode code points.\r\n', origin='user')`.
- 실행: `initialize`, `load`. 이어 원문의 `é`을 `é`로 바꿔 다시 `preserve_source`한 값으로 교체하고 `save_with_state`를 부른다.
- 단언: 다시 읽은 원문 기록이 같다. 교체 저장은 `ValueError`를 메시지 `"immutable"`로 낸다.
- 대역: 없음.

### `test_actual_host_profile_reservation_round_trip_and_authority_refs` (행 236–277)
- 성질: 실제 호스트 제약, 호스트 자원 프로필, 슬롯 예약이 Git 왕복을 거친다. 제약 값 변조, 다른 호스트를 가리키는 프로필, 근거 원문 누락은 저장 계약이 거부한다.
- 준비: `execution_state()`에 보존 원문 `GS-host`를 둔다. `host_constraint(host_id=platform.node(), limits={jobs 3, memory 4096, cpu 8000}, control_reserve={1, 1024, 1000}, authority_refs=[GS-host])`를 용량 제약과 `host_capacity_ref`로 넣는다. `EX-1`의 프로필에 `with_host_resources`로 요구 `{1, 1024, 1000}`을 더한 프로필을 추가한다. 이 프로필로 기계 실행 `EX-host`를 만들어 활동 `AT-1`에 배정한다. `SessionSlots(runtime, instance).acquire('EX-host', ..., current_time=100)`이 참인지 확인한다.
- 실행: `initialize`, `load`. 변조 셋으로 `validate_candidate`. 셋은 제약 `memory_bytes`에 1을 더한 것, `other-host`를 가리키도록 다시 봉인한 프로필을 넣은 것, `governance_sources`를 비운 것이다.
- 단언: 예약 획득이 참이다. 다시 읽은 `EX-host`의 `capacity.provider`가 `None`이다. 예약 단위 집합이 `{jobs, memory_bytes, cpu_rate_basis_points}`다. 변조 셋 모두 `ValueError`를 메시지 `"host|authority"`로 낸다.
- 대역: 없음. 호스트 ID는 실제 `platform.node()`다.

### `test_adopted_host_authoring_retains_shared_constraint_pointer` (행 279–302)
- 성질: 설정의 호스트 자원 정책으로 채택한 프로필은 공유 제약을 가리키는 `host_capacity_ref`를 유지한다. 없는 제약을 가리키면 거부된다.
- 준비: `execution_state()`에 원문 `GS-host-config`와 호스트 제약을 둔다. `config.host_resources`에 제약과 `HOST_ROLES`별 요구를 두고, `build_profiles`로 채택한 프로필·제약·`role_profile_refs`·`host_capacity_ref`를 넣는다.
- 실행: `initialize`, `load`. 이어 `host_capacity_ref='CP-absent'`로 `validate_candidate`.
- 단언: 다시 읽은 `host_capacity_ref`가 제약 ID이고, `config.host_resources`가 같다. 없는 참조는 `ValueError`(유형만)다.
- 대역: 없음.

### `test_cleanup_scope_preserves_exact_user_request_and_execution_references` (행 304–321)
- 성질: 정리(cleanup) 유지보수 행동은 정확한 사용자 요청과 실행 참조에 묶여 저장된다. 참조나 요청 근거가 어긋나면 거부된다.
- 준비: `execution_state()`의 대기열에 `maintenance` 행동(`requested_by='UC-cleanup'`, `cleanup_execution_ids=['EX-1']`)을 둔다. 이력에는 같은 사용자 제어 요청을 둔다.
- 실행: `initialize`, `load`. 변조 넷으로 `validate_candidate`. 넷은 없는 실행 `EX-absent`, 요청 설정의 실행 목록 비우기, 요청 `origin='engine'`, 행동 역할 `research_work`다.
- 단언: 다시 읽은 행동이 같다. 넷 모두 `ValueError`를 메시지 `"cleanup"`으로 낸다.
- 대역: 없음.

### `test_failed_execution_wait_preserves_actual_failure_and_snapshot` (행 323–333)
- 성질: 실행 실패로 생긴 대기 기록은 실패 종류와 입력 스냅숏을 그대로 저장한다. 없는 실행을 가리키면 거부된다.
- 준비: `execution_state()`의 `waiting_actions`에 `formal_check` 행동을 둔다. 대기 기록은 `kind`와 `failure_kind`가 `execution_failure`이고 `reason=None`, `execution_id='EX-1'`, `input_snapshot='a'*40`이다.
- 실행: `initialize`, `load`. 이어 `execution_id='EX-missing'`으로 `validate_candidate`.
- 단언: 다시 읽은 `waiting_actions`가 같다. 변조는 `ValueError`를 메시지 `"waiting action reference"`로 낸다.
- 대역: 없음.

### `test_actual_execution_window_preserves_integer_measurement_and_owner` (행 335–355)
- 성질: 실제 실행 창 기록은 정수 밀리초 측정과 소유 실행을 저장한다. 다른 실행을 가리키도록 바꾸면 거부된다.
- 준비: `execution_window.publish(work, 'EX-1', 12.75, config, clock=lambda: 12.0)`로 창을 만들어 `EX-1`에 붙인다. 실행을 `starting` → `running`으로 옮기고, `stop_reason='submission_intent'`를 달아 `stopping`으로 옮긴다. 원문 주석은 엔진의 `should_stop` 콜백이 쓰는 값과 같으며, 수명 소유자가 실행 상태와 정지 단계 축을 따로 관리한다고 밝힌다.
- 실행: `initialize`, `load`. 이어 창의 `execution_id='EX-other'`로 `validate_candidate`.
- 단언: `remaining_ms_at_start`가 750이다(12.75 − 12.0 초). 변조는 `ValueError`를 메시지 `"execution window"`로 낸다.
- 대역: 시계를 `lambda: 12.0`으로 주입한다.

### `test_checkpoint_observation_evidence_uses_actual_same_cas_bytes` (행 357–382)
- 성질: 체크포인트의 관측 증거는 같은 CAS 공개에 실린 산출물 바이트로 뒷받침되어야 한다. 크기, 누락 목록, 최종 관측 해시가 어긋나면 거부된다.
- 준비: `execution_state()`를 저장한다. `preserve_checkpoint(없는 폴더, artifact_prefix=..., max_bytes=4096)`로 빈 체크포인트를 만든다. 관측 출처 하나(`events.jsonl`, 바이트 `{"type":"public_message","message":"observed"}\n`)를 적고 `observation_evidence_complete=True`로 둔다.
- 실행: 산출물 없이 `validate_candidate`를 부른다. 이어 `artifacts={reference: raw}`로 `save_with_state`, `load`. 변조 셋으로 `validate_candidate`를 부른다. 셋은 출처 `bytes`에 1을 더한 것, `observation_evidence_omitted`에 행을 넣은 것, `final_observation`의 출처 해시를 0으로 바꾼 것이다.
- 단언: 산출물 없는 검증은 `ValueError`를 메시지 `"artifact evidence"`로 낸다. 다시 읽은 체크포인트가 같다. 변조 셋 모두 `ValueError`(유형만)다.
- 대역: 없음.

### `test_actual_submission_authority_revocation_round_trip` (행 384–405)
- 성질: 제출 의도를 기록하면 실행의 권한 회수(`authority_revocation`)가 제출 영수증에 묶여 저장된다. 영수증 ID, 상태, 종류가 어긋나면 거부된다.
- 준비: `execution_state('maintenance')`를 저장한다. `sealed_maintenance_submission(workspace, 'EX-1')`로 실제 중앙 봉인 바이트와 의도를 만든다. 실행을 `running`으로 옮기고 `record_submission_intent`로 영수증 `CT-submit`(`submit_intent`, `accepted`)을 기록한다.
- 실행: 산출물과 함께 `save_with_state`, `load`. 변조 셋으로 `validate_candidate`. 셋은 회수의 `receipt_id='CT-other'`, 영수증 `state='rejected'`, 영수증 `kind='self_check'`다.
- 단언: 다시 읽은 `authority_revocation.receipt_id`가 `'CT-submit'`이다. 변조 셋 모두 `ValueError`를 메시지 `"revocation"`으로 낸다.
- 대역: 없음.

### `test_actual_impact_request_has_closed_nested_plan_schema` (행 407–430)
- 성질: 영향 검토 요청을 담은 행동은 대기열 스키마를 통과하고 Git 왕복을 거친다. 중첩된 계획의 해시가 변조되면 저장 계약이, 미등록 키가 더해지면 스키마가 거부한다.
- 준비: `ImpactReviewHarness()`를 만들어 `setUp()`을 직접 부른다. 그 `request()`로 `maintenance` 행동(`stage='impact_review'`, `input_basis.impact_review`)을 만든다. `execution_state('research_work')`에 하네스 인스턴스를 합치고, 실행 `EX-1`을 `EX-producer`로 이름 바꿔 활동에 배정한다. 대기열에 행동을 둔다.
- 실행: `Draft202012Validator(RECORDS['queue']).validate(action)`, `initialize`, `load`. 계획 `bundle`의 `digest`를 0으로 바꿔 `validate_candidate`를 부른다. 원래 행동의 계획에 `unregistered=True`를 더해 스키마 검사를 한다.
- 단언: 처음 스키마 검사가 통과한다. 해시 변조는 `ValueError`를 메시지 `"plan hash"`로 낸다. 미등록 키는 예외(`Exception`)를 낸다.
- 대역: 없음.

### `test_actual_input_preparation_begin_and_cancel_round_trip` (행 432–446)
- 성질: 입력 준비의 시작과 취소가 저장·재적재를 거쳐 실행 결과 `cancelled`와 사유로 남는다. 준비 기록에 미등록 키를 더하면 거부된다.
- 준비: `execution_state()`의 `EX-1`에 `begin_preparation`을 적용한다.
- 실행: `initialize`, `load`. `end_preparation(..., stage='packing', reason='input overflow', cancelled=True)`, `save_with_state`, `load`. 이어 `input_preparation.unregistered=True`로 `validate_candidate`.
- 단언: 저장된 `outcome`이 `'cancelled'`, `input_preparation.reason`이 `'input overflow'`다. 미등록 키는 `ValueError`다.
- 대역: 없음.

### `test_task_input_invalidation_keeps_request_and_reason` (행 448–456)
- 성질: 과제 스키마에서 대기 중인 입력 신호(`newinput`)는 입력 요청 ID 문자열이고, 판정 무효 사유(`invalidated_reason`)는 문자열이다.
- 준비: `RECORDS['tasks']['properties']`.
- 실행: `newinput` 스키마로 `'UC-source'`를, `assessment.invalidated_reason` 스키마로 사유 문자열을 검사한다. `newinput`에 `False`, `True`, `3`을 넣어 검사한다.
- 단언: 문자열 둘은 통과하고, 세 값은 예외를 낸다.
- 대역: 없음.
- 비고: 1단 스키마 검사다. 이름은 "keeps"라고 말하지만 저장 왕복은 없다. 원문 주석은 "The pending input signal is the input request's ID; consumption removes it."다.

### `test_actual_input_metrics_overflow_and_validity_basis_round_trip` (행 458–476)
- 성질: 실행의 입력 측정값, 빈 유효성 기준, 입력 넘침 기록이 저장·재적재를 거친다. 넘침 기록에 미등록 키를 더하면 거부된다.
- 준비: `EX-1`에 `prompt_metrics('prompt', {'required': 'body'}, {}, [])`와 `capture_basis(instance, runtime, [])`를 붙인다. `fit_context({'required': 'body'*50}, max_bytes=10, ...)`로 넘침을 만들어 `research_plan` 행동의 `input_overflow`에 둔다.
- 실행: `initialize`, `load`. 이어 넘침 기록에 `unregistered=True`를 더해 `validate_candidate`.
- 단언: 다시 읽은 `validity_basis`가 `[]`이고 넘침 기록이 같다. 미등록 키는 `ValueError`다.
- 대역: 없음.

### `test_scoped_external_operation_keeps_actual_producer_fields` (행 478–486)
- 성질: 범위 필드(`target_id`, `purpose`, `subject`, `actor_kind`)를 가진 외부 작업 기록이 저장 스키마를 통과하고, 미등록 범위 필드는 거부된다.
- 준비: `prepare_operation({'method': 'POST', 'url': 'https://example.test/action'}, 'GR-1', 'SO-1', target_id='TK-1', purpose='publish', subject='result', actor_kind='ai')`.
- 실행: `RECORDS['external_operations']` 스키마로 검사한다. 이어 `unregistered_scope=True`를 더해 검사한다.
- 단언: 원래 행은 통과하고, 더한 행은 예외를 낸다.
- 대역: 없음.
- 비고: 1단 스키마 검사. 저장 왕복은 없다.

### `test_queue_preserves_actual_model_selection_producer` (행 488–499)
- 성질: 모델 정책이 만든 행동의 모델 선택 기록이 저장·재적재를 거친다. 선택된 프로필 해시가 틀리면 거부된다.
- 준비: `execution_state('research_plan')`의 대기열에 `research_plan` 행동을 두고 `model_policy.selection(config, action, {}, {}, instance=instance)`를 붙인다.
- 실행: `initialize`, `load`. 이어 `model_selection.profile_ref.sha256`을 0으로 바꿔 `validate_candidate`.
- 단언: 다시 읽은 `model_selection`이 같다. 변조는 `ValueError`다.
- 대역: 없음.

### `test_actual_external_uncertainty_reconciliation_and_retry_round_trip` (행 501–534)
- 성질: 외부 작업이 불확실 상태(`unknown`)가 되고, 효과 부재가 확인되어 `failed`로 조정되고, 재시도가 준비되는 매 단계가 저장·재적재를 거친다. 재시도 기록에 이전 결과가 남는다.
- 준비: `_approved_governance()`에 http grant `GR-http`(`https://example.test`, `POST`, `/`)를 적용한다. 대기 행동에 ID가 없으면 채운다. 원문 주석은 도메인 요청이 수명 적용 경계에서 영속 ID를 얻으며, 이 외부 원장 픽스처가 그 ID를 대신 준다고 설명한다. `prepare_operation`으로 작업을 만들어 저장한다. 지역 함수 `persist(row)`는 행을 런타임에 넣고 `save_with_state`한 뒤, 다시 읽은 행이 같은지 확인한다.
- 실행: `external.execute_operation(operation, grant, persist=persist, transport=lambda *_: {'http_status': 503, 'body': b'uncertain'}, runtime=runtime)`. 이어 `reconcile_operation(unknown, proof, 'failed', source='user', effect_absent=True)`와 `persist`, `prepare_retry(absent, {...'kind': 'effect_absent'...}, source='user')`와 `persist`를 부른다.
- 단언: 실행 결과 `status`가 `'unknown'`이다. `persist`가 매번 왕복 일치를 확인한다. 마지막으로 읽은 작업의 `previous_outcome`이 `'failed'`다.
- 대역: 네트워크 대신 `transport` 람다(503 응답)를 쓴다. 효과 부재 증명은 합성이다.

### `test_actual_plan_disposition_and_repetition_request_round_trip` (행 536–551)
- 성질: 계획 역할의 처분(`not_selected`)과 준비 요청이 엔진 적용을 거쳐 과제의 선택 처분과 대기 행동으로 저장된다. 생산 실행 ID가 남는다.
- 준비: `execution_state('research_plan')`에 `planned` 과제 `TK-1`을 둔다. `bare_engine(instance, runtime)`를 만든다. 출력은 `disposition(TK-1, kind='not_selected')`(재방문 시각과 불확실성 포함)와 `preparation_requests=['Refine the contract']`다.
- 실행: `engine._apply_task_plan(output, 'EX-1', tasks 사본, [TK-1])`, `initialize`, `load`.
- 단언: 과제의 `selection_disposition.execution_id`가 `'EX-1'`이고, 대기열 첫 행동의 `requested_by`가 `'EX-1'`이다.
- 대역: `bare_engine`(메모리 상태 엔진, `StateStore` 대역).

### `test_configure_preserves_selected_profile_edition_not_all_historical_editions` (행 553–571)
- 성질: 설정을 바꿔 새 프로필 판을 채택해도, 실행이 가리키는 옛 판은 보존되고 역할별 선택 참조(`role_profile_refs`)는 새 판을 가리킨다. 선택 참조의 해시가 틀리면 거부된다.
- 준비: `execution_state()`의 `call_timeout_seconds`를 1 올리고, `build_profiles`의 새 판을 프로필·제약·선택 참조에 반영한다. 옛 실행의 프로필 참조를 떠 둔다.
- 실행: `validate_candidate`, `initialize`, `load`. 이어 첫 역할 선택 참조의 `sha256`을 0으로 바꿔 `validate_candidate`.
- 단언: 검증 결과의 `role_profile_refs`가 새 판이고, 옛 프로필 ID가 `execution_profiles`에 남는다. 다시 읽은 선택 참조가 새 판이다. 변조는 `ValueError`다.
- 대역: 없음.

### `test_state_persists_as_family_files_and_reconstructs_views` (행 583–597)
- 성질: 상태는 가족별 파일로 저장되고, 읽을 때 보기로 다시 조립된다. 한 덩어리의 `instance.json`이나 `state.json`은 없다. 공개 사건은 번호를 받는다.
- 준비: `current_state`에 출처 `SO-01`과 사건 `EV-01`을 둔다.
- 실행: `initialize`, `load`, `list_files('research/')`와 `list_files('runtime/')`.
- 단언: 다시 읽은 `sources`가 같고, 사건의 `event_seq`가 1이다. 파일 목록에 `research/sources/SO-01.json`과 `runtime/events/EV-01.json`이 있고, `research/instance.json`과 `runtime/state.json`은 없다.
- 대역: 없음.

### `test_save_rejects_global_identifier_collision_and_missing_reference` (행 599–617)
- 성질: 기록 ID는 가족을 넘어 전역에서 유일해야 한다. 등록 가족이 선언한 참조는 실재 기록을 가리켜야 한다.
- 준비: 출처 `SO-01`을 저장한다. 두 번째 경우를 위해 런타임 가족 `links`(참조 함수 `lambda record: [record['target_id']]`)를 등록한 계약과 다른 인스턴스 ID의 저장소를 만든다.
- 실행: 사건 ID를 `SO-01`로 둔 런타임으로 `save_with_state`. 이어 `target_id='missing'`인 링크로 새 저장소의 `initialize`.
- 단언: 첫째는 `ValueError`를 메시지 `"globally unique"`로, 둘째는 `"unknown record"`로 낸다.
- 대역: 없음.

### `test_public_events_receive_contiguous_sequence_at_publish_boundary` (행 619–627)
- 성질: 공개 경계에서 사건은 1부터 연속 번호를 받고 커서가 마지막 번호를 가리킨다. 사건 가족은 기록 목록이며 사상(map)은 거부된다.
- 준비: 사건 두 행.
- 실행: `validate_candidate`. 이어 같은 사건을 ID 사상으로 둔 상태로 `validate_candidate`.
- 단언: `event_seq`가 `[1, 2]`, `event_cursor`가 2다. 사상은 `ValueError`를 메시지 `"record list"`로 낸다.
- 대역: 없음.
- 비고: 저장소에 공개하지 않는 순수 검증이다.

### `test_republication_keeps_prior_event_sequence_and_only_numbers_new_events` (행 629–634)
- 성질: 다시 공개할 때 이미 공개한 사건의 번호는 유지하고 새 사건에만 번호를 매긴다.
- 준비: 공개된 `EV-01`(`event_seq=1`)과 새 `EV-02`.
- 실행: `EventPublisher.assign_sequences_in_place(runtime, published_events=previous)`.
- 단언: 번호가 `[1, 2]`다.
- 대역: 없음.
- 비고: 1단.

### `test_published_event_numbers_require_exact_integers_in_every_position` (행 636–643)
- 성질: 공개된 사건 번호는 모든 위치에서 정확한 양의 정수여야 한다.
- 준비: 첫 사건 번호를 `True`, `1.0`, `None`, `"1"`, `0`, `-1` 가운데 하나로 두고 둘째를 2로 둔다.
- 실행: `check_sequence(rows)`.
- 단언: 모두 `ValueError`를 메시지 `"published event sequence is not contiguous"`로 낸다.
- 대역: 없음.
- 비고: `subTest(number=...)` 여섯 개. 원문 주석은 "check_sequence is the published numbering rule; reading a snapshot applies it."다.

### `test_current_event_numbers_require_exact_integers` (행 645–651)
- 성질: 공개 전 현재 사건의 번호도 정확한 정수여야 한다. 공개 이력이 있든 없든 같다.
- 준비: 같은 여섯 값 × 공개 이력 없음·있음(`EV-01`, 1).
- 실행: `EventPublisher.assign_sequences_in_place`.
- 단언: 모두 `ValueError`를 메시지 `"invalid event sequence"`로 낸다.
- 대역: 없음.
- 비고: `subTest(number=..., published=...)` 열두 개.

### `test_event_publication_preserves_history_and_rejects_unbacked_sequence` (행 653–661)
- 성질: 공개된 사건은 지울 수 없고 내용과 번호도 바꿀 수 없다. 공개 이력 없이 임의 번호를 가진 사건은 받지 않는다.
- 준비: 공개된 `EV-01`.
- 실행: 빈 목록, 종류를 바꾼 사본, 번호를 2로 바꾼 사본 각각으로 `assign_sequences_in_place`. 이어 이력 없이 `event_seq=8`인 사건으로 부른다.
- 단언: 각각 `ValueError`를 `"cannot be removed"`, `"content cannot be rewritten"`, `"sequence cannot be rewritten"`, `"contiguous"`로 낸다.
- 대역: 없음.
- 비고: `subTest(message=...)` 세 개.

### `test_unknown_family_and_malformed_map_do_not_become_singletons` (행 663–666)
- 성질: 등록되지 않은 가족이나 키와 ID가 다른 사상은 단일 가족으로 둔갑하지 않고 거부된다.
- 준비: `{'unregistered_records': {}}`, `{'knowledge': {'KN-1': {'id': 'KN-2'}}}`.
- 실행: 각각 `initialize`.
- 단언: 모두 `ValueError`(유형만).
- 대역: 없음.
- 비고: `subTest(state=...)` 두 개.

### `test_list_record_validation_cannot_be_bypassed` (행 668–671)
- 성질: 목록 가족(관계)의 기록 검증은 건너뛸 수 없다.
- 준비: 끝점이 없는 `supports` 관계 하나.
- 실행: `initialize`.
- 단언: `ValueError`(유형만).
- 대역: 없음.

### `test_save_and_cas_failure_do_not_mutate_caller` (행 673–679)
- 성질: 공개가 CAS 경합으로 실패해도 호출자의 상태는 바뀌지 않는다.
- 준비: 사건 하나를 가진 상태와 그 사본.
- 실행: `patch.object(self.repository._store, 'publish', side_effect=GitStateStoreConflict('race'))` 아래에서 `initialize`.
- 단언: `GitStateStoreConflict`가 나고, 상태가 사본과 같다. 번호 매기기 같은 변경이 호출자에게 새지 않는다.
- 대역: `_store.publish`를 경합 예외로 패치한다.

### `test_published_event_content_is_immutable_and_retry_uses_parent` (행 681–687)
- 성질: 공개된 사건의 내용을 바꿔 저장할 수 없다.
- 준비: 사건 하나를 저장하고 다시 읽는다.
- 실행: 사건 `kind`를 `'rewritten'`으로 바꿔 `save_with_state`.
- 단언: `ValueError`를 메시지 `"content cannot be rewritten"`으로 낸다.
- 대역: 없음.
- 비고: 이름의 "retry uses parent"는 이 시험에서 단언하지 않는다. 부모 기준 재시도는 `test_real_event_storage_retry_removal_and_order`와 `test_real_stale_cas_retry_keeps_pending_obligations_and_caller`가 본다.

### `test_real_event_storage_retry_removal_and_order` (행 689–709)
- 성질: 실제 저장에서 경합 실패는 호출자를 바꾸지 않고, 같은 상태로 다시 시도하면 성공한다. 번호가 이어지고, 같은 상태 재저장은 사건을 바꾸지 않는다. 사건의 순서를 뒤집거나 지우면 거부된다.
- 준비: 사건 `EV-1`을 저장하고 다시 읽은 뒤 `EV-2`를 더하고 사본을 떠 둔다.
- 실행:
  1. `publish`를 `GitStateStoreConflict('late race')`로 패치하고 `save_with_state`한다.
  2. 패치 없이 다시 저장하고 읽는다.
  3. 같은 상태로 한 번 더 저장한다.
  4. 사건 순서를 뒤집어 저장한다.
  5. 사건을 비워 저장한다.
- 단언: 1은 `GitStateStoreConflict`를 내고 상태가 사본과 같다. 2 뒤 번호가 `[1, 2]`다. 3 뒤 사건이 같다. 4는 `ValueError`(`"published event sequence is not contiguous"`)다. 5는 `ValueError`(`"removed"`)다.
- 대역: 1단계의 `_store.publish` 패치.

### `test_empty_family_and_list_order_round_trip_and_runtime_oid` (행 711–722)
- 성질: 빈 가족(빈 사상, 빈 목록)이 왕복을 거쳐 보존되고, 목록 가족의 순서도 보존된다. 런타임만 바뀐 저장은 `research` 트리의 객체 ID를 바꾸지 않는다.
- 준비: `knowledge={}`, `sources=[]`, `events=[]`인 상태를 저장한다. 이어 사건 `EV-Z`, `EV-A`를 이 순서로 넣는다.
- 실행: `save_with_state`. `subprocess.run(['git', '-C', 저장소, 'rev-parse', commit + ':research'])`로 두 커밋의 `research` 트리 OID를 읽는다. `load`.
- 단언: 두 트리 OID가 같다. 다시 읽은 `knowledge`가 `{}`, `sources`가 `[]`이고, 사건 ID 순서가 `['EV-Z', 'EV-A']`다.
- 대역: 없음.
- 비고: 제품 경로 밖에서 `git` 자식 프로세스를 직접 부른다.

### `test_exact_record_evidence_and_corrupt_record_rejected_on_load` (행 724–735)
- 성질: 기록 서술자의 바이트와 해시는 저장 파일과 정확히 같다. 파일에 미등록 권한 필드를 끼워 넣으면 읽기가 거부한다.
- 준비: 출처 `SO-1`을 저장한다.
- 실행: `read_record`, `read(path)`. 이어 기록에 `unknown_authority=True`를 더해 `_store.publish`로 쓰고 `load(bad)`.
- 단언: 읽은 바이트가 서술자 `bytes`와 같고, 그 SHA-256이 서술자 `sha256`과 같다. 변조 읽기는 `ValueError`를 메시지 `"Additional properties"`로 낸다.
- 대역: 없음.

### `test_pure_validation_rejects_duplicate_list_ids_and_unknown_record_fields` (행 737–742)
- 성질: 순수 검증은 목록 가족의 중복 ID와 미등록 필드를 거부하고, 저장소에 아무것도 쓰지 않는다.
- 준비: 같은 출처 행 두 개, 그리고 `mystery=True`를 더한 행.
- 실행: 각각 `validate_candidate`.
- 단언: 모두 `ValueError`(유형만)다. 이후 `_store.read_snapshot().head`가 `None`이다.
- 대역: 없음.
- 비고: `subTest(rows=...)` 두 개.

### `test_storage_object_format_and_contract_versions_are_enforced` (행 744–759)
- 성질: 저장된 객체 형식과 다른 `object_format`으로는 저장할 수 없다. 계약 판본(`contract_id`)이 다른 매니페스트는 읽기가 거부한다. 같은 판본이면 매니페스트의 계약 해시만 달라도 현재 값과 배치로 다시 검사해 읽는다.
- 준비: 빈 상태를 저장하고 다시 읽는다.
- 실행: `object_format='sha256'`으로 `save_with_state`. 이어 `research/_state/manifest.json`의 `contract.sha256`을 0으로 바꿔 공개하고 `load`한다. 다시 `contract.contract_id='unsupported'`로 바꿔 공개하고 `load`한다.
- 단언: 첫째는 `ValueError`(`"object_format"`)다. 계약 해시만 바꾼 읽기는 성공한다(주석 "Same edition is checked against current values and layout."). 판본을 바꾼 읽기는 `ValueError`(`"contract/schema"`)다.
- 대역: 없음.

### `test_pending_event_references_remain_unconsumed_after_publication` (행 761–768)
- 성질: 대기 사건 참조(`pending_events`)는 공개 뒤에도 소비되지 않고 남는다. 없는 사건을 가리키면 거부된다.
- 준비: 사건 `EV-1`과 `pending_events=['EV-1']`.
- 실행: `initialize`, `load`. 이어 `['EV-missing']`으로 `save_with_state`.
- 단언: 다시 읽은 `pending_events`가 `['EV-1']`이다. 변조는 `ValueError`(유형만)다.
- 대역: 없음.

### `test_load_rejects_removed_required_contract_field` (행 770–778)
- 성질: 런타임 매니페스트에서 필수 컨테이너 항목을 지우면 읽기가 거부한다.
- 준비: 빈 상태를 저장한다.
- 실행: `runtime/_state/manifest.json`의 `containers.status`를 지워 공개하고 `load`.
- 단언: `ValueError`를 메시지 `"status"`로 낸다.
- 대역: 없음.

### `test_current_lifecycle_empty_families_are_registered` (행 780–783)
- 성질: 현재 수명 주기의 런타임 가족 다섯(`trust_transitions`, `conversations`, `checkpoints`, `observations`, `extended_controls`)은 등록되어 있어 빈 사상으로 받아들여진다.
- 준비: 다섯 가족을 `{}`로 둔 런타임.
- 실행: `validate_candidate`.
- 단언: 검증 결과의 다섯 가족이 모두 `{}`다.
- 대역: 없음.

### `test_academic_resolution_accepts_only_resolved_sealed_artifact_evidence` (행 785–809)
- 성질: 학술 이의 해결 기록은 같은 공개에 실린 산출물 증거가 있을 때만 받아들여진다. 증거 해시를 바꾸고 기록 해시를 다시 맞춰도 거부된다.
- 준비: `execution_state('research_plan')`에 `_approved_governance()`를 합친다. 실행에 `input_solution_basis`를 두고 외부 이의 `RJ-1`을 둔다. 저장한 뒤 `academic.record_resolution(..., {'id': 'RJ-1', 'decision': 'resolved', 'evidence_refs': [path]}, execution_id='EX-1', resolve_evidence=...)`로 해결을 기록한다. 증거는 `b"preserved answer"`다.
- 실행: 산출물 없이 `validate_candidate`, 산출물과 함께 `save_with_state`, `load`. 이어 `evidence_hashes[path]`를 0으로 바꾸고 행 `sha256`을 다시 계산해 `validate_candidate`.
- 단언: 산출물 없는 검증은 `ValueError`(`"artifact evidence"`)다. 다시 읽은 `evidence_hashes[path]`가 바이트의 SHA-256이다. 변조는 `ValueError`(`"artifact evidence"`)다.
- 대역: `resolve_evidence` 람다가 증거 바이트를 공급한다.

### `test_academic_assessment_binds_declared_task_assessment_hash` (행 811–821)
- 성질: 학술 평가 행은 선언한 과제 평가 해시(`task_assessment_sha256`)를 SHA-256 모양으로 묶는다.
- 준비: 런타임 `academic_assessments` 가족 스키마와 행 하나.
- 실행: `jsonschema.validate([row], schema)`. 이어 해시를 `'not-a-hash'`로 바꿔 다시 검사한다.
- 단언: 첫 검사는 통과하고, 둘째는 `jsonschema.ValidationError`를 낸다.
- 대역: 없음.
- 비고: 스키마 검사만 한다.

### `test_task_dependencies_resolve_tasks_or_existing_knowledge` (행 823–839)
- 성질: 과제의 의존은 실재하는 과제나 지식을 가리켜야 한다.
- 준비: 온톨로지를 설치한 상태에 `create_candidate`로 관찰 기록을 만든다. 그 ID에 의존하는 완전한 과제 `TK-1`을 둔다.
- 실행: `validate_candidate`. 이어 의존을 `['K-missing']`으로 바꿔 다시 부른다.
- 단언: 첫째는 통과하고, 둘째는 `ValueError`(`"unknown record"`)다.
- 대역: 없음.

### `test_actual_profiles_activities_and_observation_producers` (행 841–861)
- 성질: 관측 추적기의 사실 기록과 역할별 프로필 선택이 저장·재적재를 거친다. 선택 참조는 `id`, `revision`, `sha256`만 가진다. 실행의 프로필 해시나 관측 사실의 사건 해시가 틀리면 거부된다.
- 준비: `execution_state()`와 `ObservationTracker('EX-1', 저장소, {'observation_mode': 'deadline_only'}, clock=lambda: 1.25)`의 `fact('observation_fact', {'type': 'provider_report', 'cost': 0.125}, 1.5)`.
- 실행: `initialize`, `load`, `list_files('research/')`, `load_records(head)[3]`. 이어 변조 둘로 `validate_candidate`를 부른다. 하나는 실행의 `execution_profile_ref.sha256`, 하나는 사실의 `event_sha256`을 0으로 바꾼 것이다.
- 단언: 사실이 같고, `role_profile_refs`가 같다. 파일 `research/role_profile_refs/state.json`이 있다. 선택 기록의 모든 참조 키가 `{'id', 'revision', 'sha256'}`이다. 두 변조는 각각 `ValueError`(`"profile"`, `"event.*hash"`)다.
- 대역: 시계 주입(`lambda: 1.25`).

### `test_governance_actual_approval_and_semantics` (행 870–878)
- 성질: 승인된 거버넌스 헌장은 저장·재적재 뒤 같은 목표를 보이고, 승인된 제안과 다른 내용으로 바꾸면 거부된다.
- 준비: `_approved_governance()`를 저장하고 다시 읽는다.
- 실행: `governance_view(instance)`. 이어 `CH-1`의 `content.goal`을 `'Something else'`로 바꿔 `validate_candidate`.
- 단언: 목표가 `'Prove P'`다(픽스처 헌장의 값). 변조는 `ValueError`(`"approved proposal"`)다.
- 대역: 없음.

### `test_registration_requires_closed_schema_once_and_runs_the_owner_checker` (행 880–892)
- 성질: 가족 등록은 닫힌 스키마를 요구하고 한 번만 할 수 있다. 등록된 소유자 검사기는 검증에서 실제로 불린다.
- 준비: `installed_contract()`.
- 실행: 스키마 `None`과 열린 `{'type': 'object'}`로 `register_family('runtime', 'unknown', ...)`을 부른다. 이미 있는 `sources`를 다시 등록한다. `with_validator(contract, 'research', 'sources', reject)`로 검사기를 `ValueError('owner checker invoked')`를 던지는 함수로 바꾸고, 그 계약의 저장소로 `validate_candidate`를 부른다.
- 단언: 두 스키마는 `ValueError`, 재등록은 `ValueError`(`"already registered"`), 검증은 `ValueError`(`"owner checker invoked"`)다.
- 대역: `with_validator`로 바꾼 소유자 검사기.

### `test_real_stale_cas_retry_keeps_pending_obligations_and_caller` (행 894–910)
- 성질: 두 작성자가 같은 부모에서 저장하면 늦은 쪽은 실제 CAS 경합으로 실패하고 호출자는 바뀌지 않는다. 새 부모에서 다시 적용하면 번호가 이어지고 대기 의무가 보존된다.
- 준비: 사건 `EV-1`과 `pending_events=['EV-1']`을 저장한다. 다시 읽은 런타임을 `winner`와 `loser` 둘로 나눈다.
- 실행: `winner`에 `EV-2`를 더해 저장한다. `loser`에 `EV-3`을 더해 옛 `head`로 저장한다. 이긴 커밋을 다시 읽어 `EV-3`을 더해 저장한다.
- 단언: 늦은 저장이 `GitStateStoreConflict`를 내고 `(instance, loser)`가 사본과 같다. 최종 사건 번호가 `[1, 2, 3]`이고 `pending_events`가 `['EV-1']`이다.
- 대역: 없음(실제 CAS 경합).

### `test_family_round_trip_on_sha256_repository` (행 912–919)
- 성질: SHA-256 객체 형식의 Git 저장소에서도 가족 왕복이 되고, 헤드는 64자리이며, 상태의 `object_format`이 `sha256`이다.
- 준비: 임시 폴더에 `git init -q --object-format=sha256`을 자식 프로세스로 돌려 저장소를 만든다.
- 실행: 그 저장소의 `ResearchRepository(path, INSTANCE_ID)`로 `initialize`, `load`.
- 단언: 헤드 길이가 64이고 `object_format`이 `'sha256'`이다.
- 대역: 없음.
- 비고: `git_init`이 아니라 `subprocess.run`으로 실제 `git init`을 부른다. 객체 형식 선택이 검사 대상이기 때문이다.

### `test_identity_bearing_singleton_and_nonexecution_question` (행 921–932)
- 성질: ID를 가진 단일 가족 기록은 `research/<가족>/<ID>.json`에 저장된다. 실행에서 나오지 않은 질문(`origin_execution_id=None`)도 저장된다.
- 준비: 연구 단일 가족 `singleton_proof`(`id`, `claim`)를 등록한 계약과 저장소를 만든다. 질문 `QU-1`은 `origin_field='input_overflow/AC-1'`이고 대상은 `SP-1`이다.
- 실행: `initialize`, `read_record('SP-1')`, `load`.
- 단언: 경로가 `research/singleton_proof/SP-1.json`이고, 다시 읽은 질문의 `origin_execution_id`가 `None`이다.
- 대역: 없음.

### `test_question_target_can_be_a_preserved_waiting_action_coordinate` (행 934–943)
- 성질: 열린 질문의 대상은 보존된 대기 행동의 좌표일 수 있다. 없는 행동을 가리키면 거부된다.
- 준비: 대기 행동 `AC-1`(`reason='input_overflow'`, `question_id='QU-1'`)과 그것을 대상으로 한 열린 질문.
- 실행: `validate_candidate`. 이어 대상을 `AC-absent`로 바꿔 다시 부른다.
- 단언: 첫째는 통과하고, 둘째는 `ValueError`(`"question target"`)다.
- 대역: 없음.

### `test_resolved_question_preserves_a_historical_action_coordinate` (행 945–951)
- 성질: 해결된 질문은 이미 없어진 역사적 행동 좌표를 대상으로 유지할 수 있다.
- 준비: 대기 행동이 없고, `target_ids=['AC-finished']`, `status='resolved'`, `blocks=True`인 질문.
- 실행: `validate_candidate`.
- 단언: 예외 없이 통과한다.
- 대역: 없음.

### `test_grant_question_kind_survives_storage` (행 953–962)
- 성질: grant가 필요한 외부 요청의 질문 표지(`question_kind='grant'`)가 저장·재적재를 거친다.
- 준비: `execution_state('research_work')`에 `questions.link(...)`로 질문을 만들고 `question_kind='grant'`를 단다. 원문 주석은 엔진이 grant를 이름 대지 않은 외부 요청의 사용자 질문에 이 표지를 달며(`engine._apply_extensions`), 상태 질문 보기가 그 표지를 읽는다고 설명한다.
- 실행: `initialize`, `load`.
- 단언: 다시 읽은 질문의 `question_kind`가 `'grant'`다.
- 대역: 없음.

### `test_relation_schema_and_domain_kind_evidence_are_both_enforced` (행 964–976)
- 성질: 관계 기록은 저장 스키마와 도메인 종류 규칙을 모두 거친다. 증거를 요구하는 종류에서 증거를 빼면 도메인 사유로 거부된다.
- 준비: 온톨로지 설치 뒤 관찰 기록 둘을 만들고 `import_relation`으로 `supports` 관계(`evidence='input'`)를 만든다.
- 실행: `initialize`, `load`, `read_record(relation_id)`. 이어 `evidence`를 지워 `validate_candidate`.
- 단언: 기록의 가족이 `'relations'`다. 변조는 `ValueError`(`"evidence_required"`)다.
- 대역: 없음.

### `test_installed_initialization_and_knowledge_producers_round_trip` (행 978–992)
- 성질: 설치 초기화 생산자(`initialize_state`)의 상태와 지식 후보 생산자의 기록이 저장·재적재를 거친다. 해설 참조가 없는 기록을 가리키면 거부된다.
- 준비: `initialize_state(instance_id=INSTANCE_ID, goal='question', workspace=저장소, config={}, source_input='question')`, `ensure_ontology`, `create_candidate`(관찰).
- 실행: `initialize`, `load`, `read_record(kid)`. 이어 `exposition_id='XP-absent'`로 `save_with_state`.
- 단언: 다시 읽은 기록이 같고 가족이 `'knowledge'`다. 변조는 `ValueError`(`"unknown record"`)다.
- 대역: 없음.

### `test_complete_lifecycle_candidate_uses_installed_current_state_gate` (행 994–1000)
- 성질: 초기화 상태는 설치된 현재 상태 관문을 통과하고, 발명한 런타임 상태 값은 거부된다.
- 준비: `initialize_state(..., goal='P', source_input='P')`.
- 실행: `validate_candidate`. 이어 `runtime['status']='invented_status'`로 다시 부른다.
- 단언: 첫째는 통과하고, 둘째는 `ValueError`(`"runtime/status"`)다.
- 대역: 없음.

### `test_original_input_bytes_are_the_exact_working_text` (행 1002–1011)
- 성질: 보존된 원래 입력의 바이트는 작업 텍스트의 UTF-8 바이트와 정확히 같다. 해시가 틀리면 거부된다.
- 준비: `source_input='é original input'`로 초기화한다.
- 실행: `original_input_bytes(instance['lifecycle']['immutable_input'])`. 이어 `sha256`을 0으로 바꿔 `validate_candidate`.
- 단언: 바이트가 `source.encode('utf-8')`이고, `immutable_input`이 `{'text', 'sha256', 'bytes'}` 세 값과 정확히 같다. 변조는 `ValueError`다.
- 대역: 없음.

### `test_initial_input_and_loaded_pending_event_references_are_checked` (행 1013–1027)
- 성질: 초기 상태의 입력 참조와, 읽어 들인 대기 사건 참조는 실재 기록을 가리켜야 한다.
- 준비: 초기화 상태에서 `runtime['inputs']`를 비운다. 별도로 사건 `EV-1`과 대기 참조를 저장한다.
- 실행: `validate_candidate`. 이어 `runtime/pending_events/state.json`의 `record`를 `['EV-unknown']`으로 바꿔 공개하고 `load`.
- 단언: 둘 다 `ValueError`(`"unknown record"`)다.
- 대역: 없음.

### `test_public_initialize_control_and_source_bound_grant_round_trip` (행 1029–1049)
- 성질: 공개 초기화와 사용자 제어로 만든 grant는 보존 원문에 묶여 저장된다. 승인 범위 밖으로 넓히면 거부된다. 이어지는 사용자 요청은 요청자를 가진 행동으로 저장된다.
- 준비: 4단. 저장소에서 공개 `initialize(goal='Preserve original request', config={'scholarly_enabled': False})`를 돌리고 `ResearchEngine`을 연다.
- 실행: `send_control(engine, 'decision', ...)`로 `maintenance` local grant `GR-test`(`subjects=['maintenance']` 등)를 적용한다. 엔진을 다시 연 뒤 `validate_grant_source`를 부르고, `subjects`에 `'unapproved publication'`을 더해 `store.validate_candidate`를 부른다. 끝으로 `send_control(reloaded, 'request', text='Inspect this run', config={'role': 'maintenance'})`와 `store.load()`.
- 단언: `validate_grant_source`가 통과하고 `subjects`가 `['maintenance']`다. 확장은 `ValueError`(`"approved scope"`)다. 다시 읽은 대기열에 `requested_by`를 가진 행동이 있다.
- 대역: 없음.
- 비고: 공개 경로와 실제 Git 자식 프로세스를 쓴다. `send_control`은 제어가 거부되면 실패로 처리한다.

### `test_public_initial_grant_adoption_preserves_exact_approved_scope` (행 1051–1069)
- 성질: 초기화 결정으로 채택한 초기 grant는 승인된 범위 그대로 저장된다. 채택 표지를 임의로 더하면 거부된다.
- 준비: 4단. 공개 초기화 뒤 `intent_interpretation` local grant `GR-initial`(하루 뒤 만료)을 결정으로 적용하고 사본을 떠 둔다.
- 실행: `send_control(engine, 'decision', config={'change': {'kind': 'initialization', 'initial_grant_ids': ['GR-initial']}})`, `store.load()`. 이어 `initialization_only=True`를 더해 `store.validate_candidate`.
- 단언: 다시 읽은 grant가 사본과 같다. 변조는 `ValueError`다.
- 대역: 없음.
- 비고: 만료 시각은 실제 현재 시각(`datetime.now(timezone.utc)`)에서 계산한다.

### `test_public_trust_owner_flow_round_trip_requires_the_current_record_shape` (행 1071–1102)
- 성질: 공개 신뢰 등록과 전환의 소유자 흐름이 만든 환경·바인딩·검증 영수증이 저장·재적재를 거친다. 매니페스트나 도구 모음 기록의 모양이 현재 계약과 다르면 거부되고, 바인딩이 빠져도 거부된다.
- 준비: 4단. 공개 초기화 뒤 `trust_fixture(저장소, ['synthetic-lean'])`로 합성 설치를 만든다. 원문 주석은 "Real files/owner flow, synthetic toolchain bytes: this is not Lean evidence."다.
- 실행:
  1. `send_control(engine, 'trust', config=config)`로 등록한다. 마지막 환경의 `environment_errors`와 바인딩을 확인한다.
  2. `send_control(engine, 'trust', config={'operation': 'transition', 'env_id': eid})`로 전환을 연다.
  3. `check_environment(environment, binding)`의 결과로 `engine._finish_trust_transition(마지막 전환, check)`을 부르고 `engine._save()`, `store.load()`한다.
  4. 두 변조로 검증한다. 하나는 `manifest={'files': []}`, 하나는 상대 경로의 `toolchain_record`다.
  5. 바인딩을 지운 런타임으로 검증한다.
- 단언: 등록 뒤 `environment_errors`가 `[]`이고 바인딩이 요청의 `binding`과 같다. 검사 결과가 `('verified', binding['fingerprint_sha256'])`이다. 다시 읽은 활성 환경이 `eid`이고, 바인딩과 `validation_receipt`가 같다. 두 변조는 `ValueError`(`"trust|additional"`)다. 바인딩 누락은 `ValueError`(`"trust binding"`)다.
- 대역: 합성 도구 모음 파일. `mock` 대역은 없다.
- 비고: `subTest(field=...)` 두 개.

### `test_actual_repetition_binding_is_a_closed_queue_contract` (행 1104–1113)
- 성질: 반복 기준 결속(`repetition_bases`)은 대기열의 닫힌 계약이다. 발명한 계보 키는 거부된다.
- 준비: `research_plan` 행동 하나에 `revisions.bind_repetition_bases`를 적용한다.
- 실행: `initialize`, `load`. 이어 `repetition_bases.invented_lineage='a'*64`로 `validate_candidate`.
- 단언: 다시 읽은 `repetition_bases`가 같다. 변조는 `ValueError`다.
- 대역: 없음.

### `test_actual_uncertainty_text_and_object_preserve_wire_meaning` (행 1115–1126)
- 성질: 제출 확장 스키마가 받는 불확실성 평가(문자열, 객체)는 가져오기와 저장 검증을 거쳐 같은 의미로 보존된다.
- 준비: `submission.extension_schema({'role': 'research_work'})`.
- 실행: 값 `'Not a proof'`와 `{'claim': 'Not a proof', 'scope': 'finite search only'}`마다 확장 `knowledge_metadata`를 스키마로 검사한다. 이어 관찰 후보를 `import_candidate`로 가져오고 `validate_candidate`한다.
- 단언: 스키마 검사가 통과하고, 검증 결과 기록의 `uncertainty_assessment`가 값과 같다.
- 대역: 없음.
- 비고: 저장소에 공개하지 않는다. 거부 쪽은 `ProducerStorageContractTests`가 본다.

### `test_scalar_metadata_is_one_closed_record_per_root` (행 1128–1137)
- 성질: 스칼라 메타데이터(제목, 생성 시각, 상태, 주기 수)는 루트마다 닫힌 기록 하나(`_state/metadata.json`)로 저장된다. 필드별 파일로 흩어지지 않는다.
- 준비: 인스턴스에 `id`, `title`, `created_at`, 런타임에 `status='ready'`, `cycles=0`.
- 실행: `initialize`, `list_files('research/')`, `load`, `load_records(head)[3]`.
- 단언: `research/_state/metadata.json`이 있고 `research/title/state.json`은 없다. 제목이 `'Title'`이다. `metadata` 가족 서술자가 2개(두 루트)이고, 각각 `sha256`이 바이트의 SHA-256과 같다.
- 대역: 없음.

### `test_actual_review_cycle_and_identity_producer_round_trip` (행 1139–1149)
- 성질: 실제 검토 주기와 그 판정 생산자의 기록이 저장·재적재를 거친다. 판정이 가리키는 주기를 지우면 거부된다.
- 준비: `review_fixtures.reviewed_candidate(저장소)`. 봉인 동일성 검토 한 번을 거친 저장형 후보이며, 검증하지 않았으므로 범위가 미해결로 남는다(픽스처 docstring).
- 실행: `initialize`, `load`. 이어 `review_cycles={}`로 `validate_candidate`.
- 단언: 판정의 `review_cycle_id`가 `'RC-1'`이고 주기의 `sealed`가 같다. 변조는 `ValueError`(`"unknown record"`)다.
- 대역: 없음.

### `test_staged_review_producer_keeps_transient_candidate_and_real_transition` (행 1151–1177)
- 성질: 전환의 단계 동일성 검토 생산자는 형식 결과를 바꾸지 않고, 임시 후보(`staged_candidate`)와 실제 전환 ID를 주기에 저장한다. 전환 기준이 변조되면 거부된다.
- 준비: `reviewed_candidate(저장소, verified=True)`. `engine_fixtures.FakeEngine(저장소).environment('synthetic-staged')`로 두 번째 합성 환경을 만들어 환경과 바인딩을 복사한다. 검토 정책(`build_review_policy(reviewer_count=1, max_rounds=1)`)을 두고, 전환을 시작해 `formal_evidence(instance, kid, eid)`로 결과를 기록한다. `bare_engine(instance, runtime, head='a'*40)`를 만든다.
- 실행: `owner._start_staged_identity_review(transition_id, kid)`, `initialize`, `load`. 이어 주기의 `staged_candidate.transition_basis`를 0으로 바꿔 `validate_candidate`.
- 단언: 다시 읽은 `formal_results`가 시작 전과 같다. 주기의 `transition_id`가 전환 ID다. 변조는 `ValueError`(`"staged review"`)다.
- 대역: `FakeEngine`(합성 환경 생성용), `bare_engine`.

### `test_verified_identity_and_environment_continuity_round_trip` (행 1179–1206)
- 성질: 검증된 판정은 저장·재적재 뒤에도 사용 가능하다. 환경 전환의 연속 판정은 동등 비교와 함께 저장된다. 비교 결과나 검토 주기 참조를 바꾸면 거부된다.
- 준비: `reviewed_candidate(저장소, verified=True)`를 저장하고 다시 읽는다.
- 실행: `assess_use`를 부른다. `FakeEngine`으로 `synthetic-next` 환경을 만들어 복사하고, 전환을 시작·기록·활성화한 뒤 `status='active'`로 저장·재적재한다. 연속 판정의 두 변조로 `validate_candidate`를 부른다. 하나는 `continuity_comparison.equivalent=False`, 하나는 `review_cycle_id='RC-missing'`이다.
- 단언: 재적재 뒤 사용 가능하다(실패 메시지로 결과를 붙인다). `previous_assessment_id == aid`인 연속 판정의 `continuity_comparison.equivalent`가 참이다. 두 변조 모두 `ValueError`(유형만)다.
- 대역: `FakeEngine`(합성 환경 생성용).

### `test_unchanged_many_record_save_does_not_rewrite_blobs` (행 1208–1222)
- 성질: 기록이 많아도 바뀌지 않은 상태의 저장은 블롭을 하나도 쓰지 않고 같은 헤드를 돌려준다. 스칼라 하나만 바뀌면 쓰는 블롭이 둘 이하다.
- 준비: 출처 64개를 저장하고 다시 읽는다.
- 실행: `_store.publish`를 `wraps`로 감싸 같은 상태를 저장한다. 이어 `runtime['status']='ready'`로 바꿔 다시 저장한다.
- 단언: 첫 저장의 헤드가 같고, `publish` 호출들의 둘째 인자(변경 사상) 길이 합이 0이다. 둘째 저장의 헤드는 다르고 길이 합이 2 이하다.
- 대역: `_store.publish`의 `wraps` 대역(호출 기록만).
- 비고: 원문 주석은 "Every blob a publication writes is one of the changes handed to it."이다.

## ProducerStorageContractTests (행 1225–1256)

`unittest.TestCase`를 상속한다. 표지, 클래스 속성, 설정·정리 훅, 도우미가 없다. 저장소를 쓰지 않는 1단이다.

### `test_accepted_uncertainty_metadata_matches_registered_storage_shape` (행 1226–1256)
- 성질: 불확실성 평가의 받아들임 여부는 세 층에서 같다. 세 층은 생산자 제출 스키마(wire), 제출 검사(`payload_issues`), 가져오기(`import_candidate`)다. 받아들여진 값은 등록 저장 스키마도 통과한다.
- 준비: `submission.extension_schema({'role': 'research_work'})`, 등록된 `research/knowledge` 스키마, `record_fixtures.two_observation_output()`를 쓴다. 출력 첫 편입 묶음의 구성원에 `'activity-extensions.json/knowledge_metadata/0'`을 더한다. 작업 공간은 `self.enterContext(tempfile.TemporaryDirectory())`다.
- 실행: 값 `'Not a proof'`, `{'claim': ..., 'scope': ...}`, `None`, `[]`, `7`, `False`마다 다음을 한다. 확장 `{'knowledge_metadata': [{'title': 'A', 'uncertainty_assessment': value}]}`을 wire 스키마로 검사한다. `submission.payload_issues(output, contracts.schema_for('research_work'), research_work_context(), extension, workspace)`를 부른다. 첫 관찰 후보에 값을 넣어 `import_candidate`를 부른다.
- 단언: 값이 문자열이나 객체인지(`valid`)와 wire 스키마 오류 없음이 일치한다. `payload_issues`가 비었는지도 `valid`와 일치한다. 무효 값이면 `rule_id == 'schema.type'`이고 경로가 `/uncertainty_assessment`로 끝나는 문제가 있고, 가져오기가 `ValueError`(`"uncertainty_assessment"`)를 낸다. 유효 값이면 가져온 기록이 등록 스키마를 통과하고 값이 그대로다.
- 대역: 없음.
- 비고: `subTest(value=...)` 여섯 개. `test_knowledge_io.test_uncertainty_metadata_matches_storage_types_at_import`가 가져오기와 저장 스키마의 대응만 보는 데 비해, 이 시험은 생산자 wire와 제출 검사까지 넓힌다.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈:
  - `test_knowledge_io`, `test_knowledge`, `test_knowledge_storage`, `test_reassessment`는 지식 가족의 도메인 규칙과 왕복을 본다. 이 모듈은 저장 계약 쪽에서 관계 기준, 불확실성, 관계 증거, 연속 판정, 단계 검토를 확인한다.
  - 사건 번호, CAS, 매니페스트는 저장 계층(`test_git_store` 등)과 겹칠 수 있다. 이 모듈은 가족 파일 저장소(`ResearchRepository`)를 통해 본다.
  - 호스트 예약(`test_budget`, `test_host_resources`), 외부 작업(`test_external`), 거버넌스(`test_governance`), 실행 창, 체크포인트, 관측의 도메인 동작은 각 모듈이 다룬다. 이 모듈은 그 생산물이 저장 계약을 통과하고 변조가 거부되는지만 본다.
- 픽스처 의존: `research_fixtures`의 13개 기호, `record_fixtures`의 3개, `review_fixtures`의 3개, `knowledge_fixtures`의 2개, `engine_fixtures.FakeEngine`(`consumers.json`). `installed_contract`와 `with_validator`는 시험이 소유한 계약에 가족을 더하거나 검사기를 바꾸는 도구다. 이 모듈만의 것은 아니다. `consumers.json`에 따르면 `installed_contract`는 이 모듈과 `test_payloads`, `test_repository`, `test_state_contract`, `test_unicode_flow`가, `with_validator`는 이 모듈과 `test_repository`, `test_state_contract`가 쓴다.
- 이 모듈에만 있는 도우미: `task_with_reference_locators`, `reference_fixture_instance`, `_approved_governance`, 상수 `INSTANCE_ID`.
- 실제 외부 자원: 모든 `FamilyRecordStorageTests` 시험의 Git 자식 프로세스. `subprocess`로 `git`을 직접 부르는 시험은 `test_empty_family_and_list_order_round_trip_and_runtime_oid`, `test_family_round_trip_on_sha256_repository` 두 개다. 호스트 이름(`platform.node()`)과 현재 시각을 쓰는 시험이 있다.

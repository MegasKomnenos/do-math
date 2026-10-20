# test_governance_engine

| 항목 | 값 |
|---|---|
| 조각 | `lifecycle` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_governance_engine.py` (633행) |
| 클래스 / 테스트 | 5 / 31 |
| 시험 대상 제품 코드 | `do_math/governance_engine.py`의 엔진 혼합 메서드 `_governance_control`, `_apply_governance_intent`, `_apply_governance_goal_audit`, `_governance_context`, `_governance_schema`, `_bind_governance_input`, `_governance_input_source`, `_configure_candidate`, `governance_owner_handlers`; `do_math/governance.py`의 `validate_import_units`, `_import_basis`, `preserve_source`, `import_input_source`, `prepare_import`, `check_import`, `import_approval_draft`, `apply_import_control`, `initialize_governance`, `evaluate_goal_audits`, `governance_view`; `do_math/academic.py`의 `apply_goal_assurance`; `do_math/engine.py`의 `control`, `ResearchEngine`(`process_controls`, `control_result`, `_controls`, `_apply`, `_context`, `_response_schema`, `_recover_disappeared`, `_retry_submission_publications`); `do_math/repository.py`의 `exact_content_hash`; `do_math/cli.py`의 `main`(한 시나리오) |
| 사용하는 픽스처 모듈 | `engine_fixtures`: `governance_host`, `goal_audit_host`, `intent_import`, `intent_verdict`, `routing_engine`; `record_fixtures`: `checked_import`, `audited_governance`, `task_contract`; `research_fixtures`: `governance_start`, `new_instance`, `charter`, `dispatched_launch`, `trust_environment`, `trust_fixture` |
| 격리 표지 | 없음 |
| 시작 상태 | `CentralGovernanceTests`: 1단(거버넌스 순수 함수)과 `bare_engine` 위의 조립 상태(`governance_host`, `goal_audit_host`). `PublicGitGovernanceTests`: 새 임시 Git 저장소에 공개 `initialize`만 돈 상태(`new_instance`, 활성화 없음). `ApprovalDraftTests`: 1단(`checked_import`의 사전 상태). `IntentConnections`: `routing_engine` 위의 `intent_import`. `GovernanceOwnerConnections`: `routing_engine`에 `governance_host`의 상태를 옮겨 실은 것 |

## 목적

모듈 docstring은 "중앙 거버넌스 훅"을 시험하며 "Git 시험은 조립(assembly)과 실제 배선(live wiring)을 구별한다"고 밝힌다. 곧 `CentralGovernanceTests`는 메모리 상태에 조립한 엔진으로 규칙 하나씩을 보고, `PublicGitGovernanceTests`는 같은 규칙이 실제 Git 저장소, 공개 `control`, 엔진 재적재를 지나서도 성립하는지 본다.

시험 대상은 세 흐름이다.

1. 의도 가져오기(intent import): 사용자 입력을 해석한 AI 출력(`import_units`)을 봉인 묶음으로 만들고(`prepare_import`), 독립 검사 실행이 그것을 승인하며(`check_import`), 사용자가 봉인된 묶음과 검사의 해시를 그대로 가리키는 나중 승인(`import_approval`)을 보내면 적용된다(`_governance_control`, `apply_import_control`). 승인은 해석한 원 공개 입력, 결정의 원천, 묶음·검사의 해시, 단위별 내용 해시를 모두 다시 확인한다. 전제가 바뀌었으면 적용하지 않고 재작성 행동(`previous_import_id`)을 대기열에 넣는다.
2. 설정 변경: 가져오기 경로의 설정 변경이 공개 `configure`와 같은 프로필·용량 전이를 쓰고, 운영자 출처는 자원 설정을 바꿀 수 없다.
3. 목표 감사: 추가 감사(`additional_audit`) 기록이 감사 실행의 문맥·스키마·입력 결속으로 전달되고, 감사 결과의 판정 사상(`verdict_mapping`)이 목표 판정에 저장되며, 잘못되거나 낡은 감사 결과는 판정을 덧붙이기 전에 거부된다.

여러 시험이 유니코드 결합 문자 `é`(두 코드 포인트)과 합성 문자 `é`를 대비시켜, 원문이 NFC로 정규화되지 않고 코드 포인트 그대로 보존·비교된다는 계약을 확인한다.

## 모듈 수준 요소

- 행 8: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 조건 없이 넣는다.
- 행 9–12: 제품 `ResearchEngine`, `exact_content_hash`와 픽스처 `goal_audit_host`, `governance_host`, `intent_import`, `intent_verdict`, `routing_engine`, `governance_start`, `new_instance`를 가져온다. 나머지 픽스처와 제품 모듈은 시험 안에서 지역 import한다.
- 행 633: 직접 실행하면 `unittest.main()`.

모듈 함수와 모듈 상수는 없다.

## CentralGovernanceTests (행 15–288)

`unittest.TestCase`를 그대로 상속한다. 표지·설정 훅·도우미·클래스 속성이 없다. 많은 시험이 `engine_fixtures.governance_host()`로 시작한다. 이 픽스처는 `record_fixtures.checked_import()`의 상태(헌장 `CH1`이 승인된 인스턴스에서, 입력 `IN`을 해석해 `CH1`을 대체하는 `CH2`(목표 `'Prove Q'`)를 제안하는 묶음을 만들고 실행 `E2`가 승인 검사를 마친 상태, 그리고 `CHECK` 행동이 `import_application_authority` 대기인 상태)를 `bare_engine`에 싣는다. 사용자의 나중 승인 `request`(ID `LATER`)를 공개 결정 모양 `{'config': {'change': {...}}}`으로 감싸 돌려준다. `_complete_initial_intent`와 `_activate_initialization`은 `create_autospec` 대역으로 바꿔, 호출되면 `completed_input`과 `activation_attempted` 속성을 기록만 한다. 설정은 `DEFAULT_CONFIG`에 `scholarly_enabled=False`다. `goal_audit_host()`는 그 위에 `record_fixtures.audited_governance()`(추가 감사 `AU`: 범위 `['P']`, 필요 입력 `['CH1']`, 사상 `pass→satisfied`, `partial→not_satisfied`, `unknown→unresolved`)를 싣고, `_goal_basis_key`를 `'B'`로 고정한 뒤 감사 실행 `AUDITOR`의 입력을 결속하고, "목표는 충족했지만 추가 감사 `AU`는 부분"인 출력을 돌려준다.

### `test_import_unit_target_matches_each_governance_consumer` (행 16–37)
- 성질: 가져오기 단위의 `owner_ref`는 그 단위의 페이로드가 가리키는 대상과 일치해야 하며, 이 규칙이 거버넌스 소비자 종류마다 성립한다.
- 준비: 1단. `preserve_source('GS-target', 'Use the named target.', origin='user')`. 인스턴스 `{'id': 'RI-test'}`, 빈 런타임.
- 실행: 다섯 `subTest` 케이스마다 단위 하나짜리 출력으로 `validate_import_units`를 세 번 부른다. 원래 대상, `owner_ref='different-target'`, 그리고 페이로드를 `{}`로 비운 경우.
- 단언: 첫 호출은 통과한다. 둘째는 `ValueError`를 메시지 조각 `'owner coordinate'`로 던진다. 셋째(대상을 말하지 않는 빈 페이로드)는 다시 통과한다.
- 대역: 없음.
- 비고: `subTest` 케이스(`kind`, 대상, 페이로드)는 `grant`/`GR-one`(`grant.id`), `delegation`/`DG-one`(`delegation.id`), `revoke`/`GR-one`(`grant_id`), `task_scope`/`TK-one`(`task_id`), `question_answer`/`QU-one`(`resolves_questions=['QU-one', 'QU-two']`)이다. 마지막 케이스에서 대상은 `resolves_questions` 목록에 들어 있기만 하면 된다. 제품 `validate_import_units`(`governance.py` 행 880–883)는 `owner_ref`가 그 목록에 포함되는지를 본다. 시험의 대상 `QU-one`이 목록의 첫 원소이므로, 이 시험은 포함 규칙과 첫 원소 일치 규칙을 구별하지 않는다.

### `test_import_basis_tracks_replaced_grant_but_not_unrelated_grants` (행 39–52)
- 성질: 가져오기의 전제(basis) 해시는 묶음이 대체하는 허가의 변경에는 반응하고, 무관한 허가의 변경에는 반응하지 않는다.
- 준비: 1단. 활성 허가 `GR-old`, `GR-other`(둘 다 역할 `maintenance`)를 가진 인스턴스. 출력은 `GR-old`를 대체하는 새 허가 `GR-new`의 단위 하나.
- 실행: `gov._import_basis(instance, {}, output)`를 원 상태, `GR-other`에 역할을 더한 상태, `GR-old`에 역할을 더한 상태에서 부른다.
- 단언: 무관한 변경의 전제는 원래와 같고, 대체 대상 변경의 전제는 원래와 다르다.
- 대역: 없음.
- 비고: 비공개 함수 `_import_basis`를 직접 부른다.

### `test_exact_later_control_applies_once_and_queues_followup` (행 54–63)
- 성질: 봉인된 검사와 정확히 일치하는 나중 승인은 한 번 적용되고, 같은 승인을 다시 보내도 효과가 겹치지 않으며, 적용이 후속 연구 준비를 대기열에 넣는다.
- 준비: `governance_host()`.
- 실행: `h._governance_control(request)`를 두 번.
- 단언: 첫 호출은 참을 돌려주고 `governance['CH2']['content']['goal'] == 'Prove Q'`. 둘째 호출도 참이며 대기열이 첫 호출 직후와 같다. 대기열에 `role == 'research_preparation'`이고 `reason`에 `'checked user information'`이 든 행동이 있다.
- 대역: `governance_host`의 대역(`bare_engine`, 초기 의도 완료·활성화 기록 대역).
- 비고: 주석(행 61)은 제품 대기열이 이 후속을 이미 있는 준비 요청에 합친다고 적는다.

### `test_initial_later_control_completes_initialization_without_new_check` (행 65–71)
- 성질: 가져오기가 인스턴스의 초기 입력을 해석한 것이면, 나중 승인의 적용이 초기화를 완료하고 활성화를 시도하며, 새 의도 해석 검사를 만들지 않는다.
- 준비: `governance_host()`에서 `instance['lifecycle'] = {'input_id': bundle['input_ref']}`로 묶음의 입력을 초기 입력으로 만든다.
- 실행: `h._governance_control(request)`.
- 단언: `h.completed_input == bundle['input_ref']`, `h.activation_attempted`가 참, 대기열에 `intent_interpretation` 행동이 없다.
- 대역: `governance_host`의 대역. 완료와 활성화는 실제로 수행되지 않고 기록만 된다.

### `test_stale_approval_rejects_and_routes_to_reauthor` (행 73–78)
- 성질: 승인이 기대는 결정의 원천 해시가 바뀌었으면 승인은 거부되고, 가져오기는 재작성으로 돌아간다.
- 준비: `governance_host()`에서 `instance['decisions']['D']['source_sha256']`를 `'0'*64`로 바꾼다.
- 실행: `h._governance_control(request)`.
- 단언: `ValueError`(유형만). `CH2`가 거버넌스에 없다. 대기열에 `previous_import_id == bundle['id']`인 행동이 있다.
- 대역: `governance_host`의 대역.

### `test_corrected_exact_approval_cancels_unstarted_recheck_of_same_seal` (행 80–87)
- 성질: 봉인 해시가 틀린 승인이 재작성 행동을 대기열에 넣었더라도, 이어서 정확한 승인이 오면 같은 봉인에 대한 아직 시작하지 않은 재작성 행동이 취소된다.
- 준비: `governance_host()`. `check_sha256`만 `'0'*64`로 바꾼 사본 `wrong`.
- 실행: `_governance_control(wrong)`, 이어 `_governance_control(request)`.
- 단언: 첫 호출은 `ValueError`이고 대기열에 `previous_import_id == bundle['id']`인 행동이 있다. 둘째 호출 뒤 그런 `intent_interpretation` 행동이 없다.
- 대역: `governance_host`의 대역.

### `test_original_changed_before_later_approval_is_not_applied` (행 89–94)
- 성질: 가져오기가 해석한 원 공개 입력이 승인 전에 바뀌었으면 승인은 적용되지 않는다.
- 준비: `governance_host()`에서 `runtime['inputs']`를 같은 ID(`bundle['input_ref']`)에 다른 텍스트 `'A different user original'`을 담은 입력으로 바꾼다.
- 실행: `_governance_control(request)`.
- 단언: `ValueError`를 메시지 조각 `'original public input changed'`로 던진다. `CH2`가 없다.
- 대역: `governance_host`의 대역.
- 비고: 주석(행 90): 승인은 가져오기가 해석한 공개 입력(`input_ref`)을 다시 확인한다.

### `test_failed_initial_followup_does_not_publish_partial_control_effect` (행 96–103)
- 성질: 초기 입력의 승인을 적용하다 초기 의도 완료 단계가 실패하면, 거버넌스 변경도 가져오기의 적용 기록도 남지 않는다(부분 효과 없음).
- 준비: `governance_host()`, 초기 입력 설정은 `test_initial_later_control_completes_initialization_without_new_check`와 같다. `_complete_initial_intent`를 `ValueError('missing initial evidence')`를 던지는 함수로 바꾼다.
- 실행: `_governance_control(request)`.
- 단언: `ValueError`(유형만). `CH2`가 없고, `runtime['intent_imports'][bundle['id']]`에 `application` 키가 없다.
- 대역: `governance_host`의 대역과, 실패하는 `_complete_initial_intent`.

### `test_import_configuration_uses_same_profile_and_slot_transition` (행 105–133)
- 성질: 의도 가져오기로 승인된 설정 변경은 공개 `configure`와 똑같은 설정·실행 프로필·용량 제약·역할 프로필 참조·예약 전이를 만든다.
- 준비: `governance_host()`. 임시 디렉터리를 작업공간으로, 예약을 빈 사전으로 둔다. 패치는 `DEFAULT_CONFIG['session_limits']`의 사본. 기준값은 `h._configure_candidate(instance, runtime, {'action': 'configure', 'origin': 'user', 'config': patch})`의 결과 `(public_i, public_r)`다.
- 실행: 입력 `CONF`('Adopt these exact concurrent capacities')를 더하고 `import_input_source`로 원천을 얻는다. `owner_kind='configuration'` 단위 하나로 `prepare_import`(작성 실행 `AUTHOR`, `governance_owner_handlers()`)를 하고, 검사 실행 `CHECK`를 등록해 `check_import`(승인)를 한다. `import_approval` 요청 `CONF-APPROVE`를 `_governance_control`로 적용한다.
- 단언: 인스턴스의 `config`, `execution_profiles`, `capacity_constraints`, `role_profile_refs`가 `public_i`와 같고, `runtime['reservations']`가 `public_r['reservations']`와 같다.
- 대역: `governance_host`의 대역.

### `test_configuration_rejects_operator_resources` (행 135–143)
- 성질: 운영자 출처의 `configure`는 자원 설정(세션 한도)을 바꿀 수 없고, 거부된 시도는 인스턴스를 바꾸지 않는다.
- 준비: `governance_host()`. `session_limits.work`의 모든 모델 한도를 1씩 늘린 값.
- 실행: `_governance_control({'action': 'configure', 'origin': 'operator', 'config': {'session_limits': limits}})`.
- 단언: `ValueError`를 메시지 조각 `'resource settings require a user decision'`으로 던진다. 인스턴스가 호출 전 깊은 사본과 같다.
- 대역: `governance_host`의 대역.

### `test_intent_input_tasks_carry_the_contract_hash_a_scope_decision_binds` (행 145–159)
- 성질: 의도 해석 실행의 문맥에 실린 과제는 범위 결정이 결속할 계약 해시(`planning.contract_hash`)를 담는다.
- 준비: `governance_host()`. 초기 입력 `RAW`('Waive the first obligation.')와 그 불변 입력 기록을 둔다. 과제는 `record_fixtures.task_contract()`(`TK-1`)이며, 문맥에는 거짓 `content_sha256 = 'c'*64`를 덧붙여 넘긴다.
- 실행: `h._governance_context({'role': 'intent_interpretation', 'target': 'RAW'}, {'tasks': [...]})`.
- 단언: 문맥의 첫 과제 `contract_sha256`이 `contract_hash(task)`와 같다.
- 대역: `governance_host`의 대역.
- 비고: 주석(행 146–147)이 근거를 적는다. `입력-소비자.md`의 `task_scope`는 공급된 과제 판본과 해시를 쓰고, 적용(`governance.apply_decision`)은 그 해시를 `planning.contract_hash`와 비교한다. 거짓 `content_sha256`을 넣는 것은 문맥이 그 값을 쓰지 않고 계약 해시를 새로 계산함을 보이려는 설정으로 읽힌다.

### `test_nfd_original_reaches_actual_context_and_coverage` (행 161–180)
- 성질: NFD(결합 문자) 원문은 해석 실행의 문맥과 원천 해시에 코드 포인트 그대로 전달되고, 가져오기 단위의 원문 범위는 NFC 길이가 아니라 실제 코드 포인트 길이로 검사된다.
- 준비: `governance_host()`. `text = 'Prove that é has two code points.'`와 그 불변 입력 기록.
- 실행: `_governance_context(...)`, `_governance_input_source('RAW')`, 원문 전체 범위 단위로 `prepare_import`, 이어 범위 끝을 NFC 문자열의 길이로 바꾼 `prepare_import`.
- 단언: 문맥 `user_request.text`가 원문과 같다. 원천의 `sha256`이 원문 UTF-8 바이트의 해시다. 첫 `prepare_import`는 통과하고, NFC 길이의 범위는 `ValueError`(유형만).
- 대역: `governance_host`의 대역.

### `test_audit_context_schema_binding_and_rejected_missing_results` (행 182–195)
- 성질: 추가 감사 기록은 목표 감사 실행의 문맥과 응답 스키마에 들어가고, 결속된 감사 실행이 감사 결과를 빠뜨리면 평가가 거부된다.
- 준비: `governance_host()` 위에 `audited_governance()`의 상태를 싣는다.
- 실행: `_governance_context({'role': 'goal_audit'}, {})`, `_governance_schema(action, 빈 객체 스키마)`, `_bind_governance_input(action, execution, context)`로 실행 `AUDITOR`를 결속하고 등록한 뒤 `evaluate_goal_audits(instance, runtime, 'AUDITOR', [])`.
- 단언: 문맥 `additional_audit_input[0].audit.id == 'AU'`. 스키마의 `required`에 `additional_audits`가 있다. 빈 결과의 평가는 `ValueError`(유형만).
- 대역: `governance_host`의 대역.

### `test_original_literal_changes_are_not_equal_approval_hashes` (행 197–199)
- 성질: 승인 해시(`exact_content_hash`)는 NFD와 NFC처럼 정규화로 같아지는 문자열을 다른 내용으로 본다.
- 준비: 1단.
- 실행: `exact_content_hash({'statement': 'é has two codepoints'})`와 `é` 판본.
- 단언: 두 해시가 다르다.
- 대역: 없음.

### `test_import_source_and_public_input_have_distinct_global_identity` (행 201–209)
- 성질: 가져오기가 보존하는 원천 기록은 공개 입력과 다른 전역 ID를 갖되, 입력을 `input_ref`로 가리키고 같은 내용 해시를 갖는다.
- 준비: `governance_host()`. 묶음의 원천과 같은 ID·텍스트·출처의 공개 입력을 `runtime['inputs']`에 둔다.
- 실행: `_apply_governance_intent({'id': 'AC-NEW', 'role': 'intent_interpretation', 'target': source['id']}, bundle['output'], 'AUTHOR')`.
- 단언: 새 묶음의 `input_ref`가 입력 ID이고, `source.id`는 그와 다르며, `source.sha256`은 같다.
- 대역: `governance_host`의 대역.

### `test_actual_goal_consumer_stores_mapping_not_generic_satisfied` (행 211–221)
- 성질: 실제 목표 감사 소비자는 추가 감사의 판정 사상(부분 → 불충족)을 판정에 저장하고, 일반 판정 `satisfied`만으로 인스턴스를 완료하거나 최종 보증을 허락하지 않는다.
- 준비: `goal_audit_host()`.
- 실행: `h._apply_governance_goal_audit(action, output, 'AUDITOR')`, 이어 `apply_goal_assurance(instance, decision='mathematically_solved', basis='B', judgments=[judgment], runtime=runtime)`.
- 단언: 판정 `decision == 'satisfied'`, `additional_audits[0].decision == 'not_satisfied'`. 런타임 `status`가 `'completed'`가 아니다. `goal_judgments == [judgment]`. 최종 보증은 `ValueError`(유형만).
- 대역: `goal_audit_host`의 대역(`_goal_basis_key` 고정 포함).

### `test_actual_goal_consumer_rejects_missing_wrong_and_stale_audit_before_append` (행 223–232)
- 성질: 목표 감사 결과에 추가 감사가 없거나, 입력 해시·평가자가 틀리거나, 감사가 기대는 헌장이 바뀌었으면 판정을 덧붙이기 전에 거부된다.
- 준비: `subTest`마다 새 `goal_audit_host()`에 변형 하나를 가한다.
- 실행: `_apply_governance_goal_audit(action, output, 'AUDITOR')`.
- 단언: `ValueError`(유형만). `goal_judgments == []`.
- 대역: `goal_audit_host`의 대역.
- 비고: `subTest` 케이스 `mutation`은 넷이다. `'missing'`: `additional_audits`를 뺀다. `'wrong_hash'`: 입력 해시를 `{'CH1': '0'*64}`로. `'wrong_assessor'`: 평가자를 `'producer-claim'`으로. `'stale'`: 헌장 `CH1`의 목표 끝에 `' changed'`를 붙인다.

### `test_goal_consumer_and_final_assurance_with_explicit_formal_double` (행 234–271)
- 성질: 형식 증명의 가용성만 대역으로 두면, 추가 감사가 `pass`일 때 목표 판정이 최종 보증으로 이어져 목표가 `mathematically_solved`가 되고 학술 후속이 요청되며, `partial`일 때는 그렇지 않다. 어느 경우든 판정의 `record_basis`는 기록 스키마를 지키고 이전 판정은 보존된다.
- 준비: `subTest`마다 새 `goal_audit_host()`. 지식 `K`와 형식 결과 `FR`을 두고, 이전 판정 `GJ-old`(`not_satisfied`, `current=False`)를 덧붙인다. `trust_fixture(tmp, ['synthetic-audit-lean'])`와 `trust_environment(..., environment_id='TE-audit')`로 합성 신뢰 환경을 활성으로 둔다. `_ensure_academic_followup`을 호출되면 `academic_followup=True`를 기록하는 `create_autospec` 대역으로 바꾼다. 감사 결과의 `verdict`를 케이스 값으로 둔다.
- 실행: `patch('do_math.knowledge.assess_use', return_value={'valid': True})`, `patch('do_math.knowledge_records.usable_links', return_value=[{'formal_result_id': 'FR', 'assessment_id': 'AS'}])`, `patch('do_math.knowledge_records.formal_usable', return_value=True)` 아래에서 `_apply_governance_goal_audit`.
- 단언: 마지막 판정의 `record_basis`가 비어 있지 않고 `RECORDS['goal_judgments']['properties']['record_basis']` 스키마를 `jsonschema.validate`로 통과한다. `goal_status == 'mathematically_solved'` 여부가 기대값과 같다. `academic_followup` 기록 여부가 기대값과 같다. 첫 판정이 `GJ-old`와 같고 판정이 모두 둘이다.
- 대역: 위 세 `patch`, `_ensure_academic_followup` 대역, `goal_audit_host`의 대역.
- 비고: `subTest` 케이스는 `('partial', False)`, `('pass', True)`다. 주석(행 256–257)이 범위를 밝힌다: 증명 가용성만 대역이고, 사상·판정·최종 보증은 실제 제품 소비자다.

### `test_raw_initial_charter_compares_lossless_input_not_nfc_projection` (행 273–288)
- 성질: 초기 거버넌스는 헌장 원천을 불변 입력의 무손실 원문과 비교하며, NFC 투영과는 다르다고 본다.
- 준비: 1단. `text = 'é has two codepoints'`와 그 불변 입력을 가진 `governance_start(...)` 인스턴스. `preserve_source('S', text, origin='user')`, `research_fixtures.charter()`(`CH1`), 그 해시를 담은 승인 `D`.
- 실행: `initialize_governance(instance, source, approval, [record])`, 이어 NFC 텍스트로 만든 원천으로 같은 호출.
- 단언: 첫 결과의 `governance_sources['S'].text`가 원문과 같다. 둘째는 `ValueError`를 메시지 조각 `'initial charter source differs'`로 던진다.
- 대역: 없음.

## PublicGitGovernanceTests (행 291–561)

`unittest.TestCase`를 그대로 상속한다. 표지·설정 훅·클래스 속성은 없다. 시험마다 `tempfile.TemporaryDirectory()`를 저장소 루트로 쓰고 `initialized`로 새 인스턴스를 만든다. 시작 상태는 새 Git 저장소에서 공개 `initialize`만 돈 것이다(4단의 공개 경로 가운데 초기화까지이고 활성화는 하지 않는다). 모든 상태가 실제 Git 저장소에 저장되며, 시험은 `ResearchEngine(root, iid)`로 엔진을 다시 적재해 저장 뒤의 상태를 본다.

- `initialized(root, goal='User approves P')` (행 292–294): `research_fixtures.new_instance(root, goal=goal, workspace=root/'work', config={'scholarly_enabled': False})`로 저장소를 만들고 공개 `initialize`를 한 뒤 `ResearchEngine(root, instance_id)`를 돌려준다. `new_instance`는 `git_init`(프로세스당 한 번 만든 빈 `.git` 복사)을 쓴다.
- `execution_fixture(engine, eid, role, target=None)` (행 296–305): 모델 공급자 없이 실행 기록 하나와 그 소유 활동 `ACT-<eid>`를 런타임에 직접 넣는다. 활동은 `status='ready'`, 실행은 `status='queued'`, `actor_kind='ai'`, 역할의 첫 프로필 참조, 행동 `AC-<eid>`를 갖는다.
- `run_sealed_import_case(scenario)` (행 342–437): 세 시험이 공유하는 시나리오. `scenario`는 `'exact'`, `'changed_premise'`, `'configuration'`이다. 단계는 다음과 같다.
  1. 공개 `control`로 초기 거버넌스 결정(`charter()`, 요청 ID `adopt-charter`)을 보내고 `process_controls`로 적용한다. 효과가 `applied`임을 단언한다.
  2. 공개 입력 `input-Q`를 보낸다. 텍스트는 설정 시나리오에서 `'Set call timeout to 901 seconds'`, 나머지는 `'Change the goal to Q'`.
  3. `execution_fixture`로 작성 실행 `AUTHOR`와 검사 실행 `CHECKER`를 만든다. 주석(행 358–359): 공급자 없는 실행 기록이 실제 정체·프로필·활동 관계를 유지하며, 공급자 성공이나 형식 증명은 단언하지 않는다.
  4. 출력은 `CH2`(목표 `'Prove Q'`, `CH1` 대체)를 제안하는 헌장 단위 하나다. 설정 시나리오에서는 `owner_kind='configuration'`, 페이로드 `{'call_timeout_seconds': 901}`로 바꾸고, 기대값으로 `_configure_candidate`의 결과 인스턴스를 계산해 둔다.
  5. `_apply_governance_intent`로 작성 단계를, 검사 실행에 묶음 해시를 적은 뒤 `stage='check'` 행동으로 검사 단계(승인)를 적용하고 `_save()`한다. 엔진을 다시 적재해 봉인된 검사를 `sealed`로 떠 두고, 승인 사양 `spec`(`import_approval`, 묶음·검사 해시, 단위 해시)을 만든다.
  6. `changed_premise`: 새 추가 감사 `AU-LATER`를 공개 결정으로 채택(효과 `applied`)해 전제를 바꾼 뒤, 옛 `spec`의 승인 `stale-premise-approval`을 보낸다. 효과가 `rejected`이고, 재적재한 상태에 `CH2`가 없으며, 봉인이 `sealed`와 같고, 대기열에 `previous_import_id == bundle['id']`인 행동이 있음을 단언하고 끝난다.
  7. 나머지: `check_sha256`만 틀린 승인 `wrong-approval`을 보내 효과 `rejected`를 단언하고, 같은 요청을 다시 보내 재생 영수증의 `snapshot`이 원래 거부의 것과 같음을 단언한다. 이어 `spec`을 들여쓰기 2의 JSON으로 쓰고 줄바꿈을 CRLF로 바꾼 파일을 만들어 `cli.main(['decision', ..., '--file', ..., '--request-id', 'approve-Q'])`를 프로세스 안에서 부른다. 반환 0, 효과 `applied`를 단언한다. 재적재한 상태의 `governance_sources` 가운데 텍스트가 CRLF 원문과 정확히 같은 것이 있음을 단언한다. 설정 시나리오는 `config`, `role_profile_refs`, `execution_profiles`, `capacity_constraints`가 기대 인스턴스와 같음을, 나머지는 `governance_view(...)['goal'] == 'Prove Q'`임을 단언한다. 봉인이 `sealed`와 같고, 재작성 행동이 없으며, 같은 요청 ID로 다시 보낸 `control`의 `snapshot`이 CLI 결과의 것과 같음을 단언한다.

### `test_public_configure_preserves_original_result_after_other_control_and_reload` (행 307–331)
- 성질: 공개 `configure`의 영수증은 다른 설정 제어와 엔진 재적재 뒤에도 원래 결과를 재생하고, 운영자 출처의 자원 설정과 같은 요청 ID에 다른 내용을 실은 요청은 수락 단계에서 거부된다.
- 준비: `initialized(root)`. 지역 함수 `capacity(count)`는 `session_limits.work`의 모든 모델 한도를 `count`로 둔 설정 패치를 만든다.
- 실행: 공개 `control`로 `configure`(한도 12, `request_id='configure-first'`)를 보내 적용하고 `control_result`로 결과를 읽는다. 한도 14의 `configure-second`를 적용한다. 엔진을 새로 적재한다. `configure-first`를 같은 내용으로 다시 보낸다. 이어 운영자 출처 한도 15, 그리고 `configure-first` ID에 한도 16을 보낸다.
- 단언: 첫 결과는 `effect == 'applied'`이고 한도가 12다. 재전송 영수증의 `snapshot`과 한도가 첫 결과와 같다(12). 재적재된 엔진의 현재 설정은 한도 14다. 운영자 출처와 내용이 바뀐 재사용 ID는 모두 `ValueError`(유형만).
- 대역: 없음. 실제 Git 저장소.

### `test_git_sealed_import_later_control_and_restart` (행 333–334)
- 성질: 봉인된 헌장 가져오기는 틀린 봉인 참조를 거부(재생 가능)한 뒤, CRLF 원문 그대로의 정확한 나중 승인으로 적용되고, 엔진 재적재 뒤에도 봉인·원문·재생 영수증이 보존된다.
- 준비: 클래스 절의 `run_sealed_import_case` 참조.
- 실행: `run_sealed_import_case('exact')`.
- 단언: 클래스 절의 7단계 가운데 헌장 분기(`goal == 'Prove Q'`).
- 대역: 없음. 실제 Git 저장소와 프로세스 안의 `cli.main`.

### `test_git_changed_premise_rejects_later_approval_and_preserves_seal` (행 336–337)
- 성질: 검사 뒤 전제(추가 감사 기록)가 바뀌면 옛 전제의 승인은 거부되고, 봉인은 그대로 남으며 재작성이 대기열에 들어간다.
- 준비: 클래스 절의 `run_sealed_import_case` 참조.
- 실행: `run_sealed_import_case('changed_premise')`.
- 단언: 클래스 절의 6단계.
- 대역: 없음. 실제 Git 저장소.

### `test_git_configuration_import_uses_public_transition_and_profiles` (행 339–340)
- 성질: 설정 변경 가져오기의 승인은 공개 `configure`와 같은 설정·프로필·용량 전이를 만들고 Git 재적재 뒤에도 유지된다.
- 준비: 클래스 절의 `run_sealed_import_case` 참조.
- 실행: `run_sealed_import_case('configuration')`.
- 단언: 클래스 절의 7단계 가운데 설정 분기(네 필드가 `_configure_candidate`의 기대 인스턴스와 같음).
- 대역: 없음. 실제 Git 저장소와 프로세스 안의 `cli.main`.
- 비고: `CentralGovernanceTests.test_import_configuration_uses_same_profile_and_slot_transition`의 Git 판본이다. 그쪽은 세션 한도와 예약을, 이쪽은 `call_timeout_seconds`를 바꾼다.

### `test_public_audit_contract_and_actual_goal_judgment_survive_git_reload` (행 439–535)
- 성질: 공개 결정으로 채택한 추가 감사가 목표 감사 실행의 문맥·스키마·결속으로 이어지고, 실제 목표 판정이 Git에 저장된다. 판정 공개 직후 실행 마무리 전에 충돌한 상태에서도, 복구가 봉인된 제출을 다시 공개해 실행을 `output_accepted`로 끝내되 판정과 사건을 중복하지 않는다.
- 준비: `initialized(root)`. 공개 결정으로 헌장(`charter`)과 추가 감사 `AU`(사상 `pass→satisfied`, `partial→not_satisfied`)를 채택한다(`audit` 효과 `applied` 단언). 목표 감사 행동 `AC-AUDITOR`(`basis = engine._goal_basis_key()`, `slot=0`, `required=1`)와 `execution_fixture`로 만든 실행 `AUDITOR`.
- 실행과 단언: 여러 단계로 나뉜다.
  1. `engine._context(action, workspace, execution_id='AUDITOR')`의 `additional_audit_input[0].audit.id == 'AU'`, `_response_schema(action)['required']`에 `additional_audits`가 있다. `_bind_governance_input`으로 결속한다.
  2. 출력은 `decision='satisfied'`와 `AU`의 `verdict='partial'`이다. 추가 감사가 빈 목록인 출력과 `verdict='invented'`인 출력을 `engine._apply`에 넣으면 각각 `ValueError`이고 `goal_judgments`가 빈 채로 남는다. 이어 올바른 출력을 `_apply`한다.
  3. 주석(행 474–475): 판정·영수증 공개 직후, 원 실행의 마지막 `output_accepted` 처리 전의 충돌을 보존한다. 이를 위해 출력에 통합 묶음 `IN-audit`를 더하고 `integration.split_bundles`로 첫 묶음을 얻어 `runtime['integrations']`에 넣는다. 실행을 `transition_execution(..., 'ended', outcome='start_failed', reason='crash fixture before finalization')`으로 끝내고, `dispatched_launch`에 `phase='finished'`를 얹은 실행 요청표, 확인된 로컬 종료, 입력 묶음·스냅숏·결과 참조를 채운다. 결과물 사전에 결과·문맥·스키마를 `canonical_json`으로 담는다. `submission.check_submission(..., mode='receiver', execution_id='AUDITOR', tool_sha256='a'*64)`의 `passed`가 참임을 단언한다. 출력·확장·검사를 결과물로 쓰고 그 해시를 `submission_intent`에 적은 뒤, 수락된 `submission_receipt`를 만든다. `read_sealed_submission`으로 봉인 읽기가 통과함을 확인하고 `engine._save(artifacts)`로 저장한다.
  4. 재적재한 엔진에서 첫 판정의 `additional_audits[0].decision == 'not_satisfied'`, 런타임 `status != 'completed'`, 실행의 `additional_audit_input`이 문맥의 것과 같다. 판정과 사건 목록, 결과 참조를 떠 둔다.
  5. `writer_lock()` 안에서 `_recover_disappeared()`를 부른 뒤 `waiting_actions[action['id']].kind == 'submission_publication'`을 단언하고, `_retry_submission_publications()`를 부른다.
  6. 다시 적재한 최종 상태에서 실행 `outcome == 'output_accepted'`, 활동 `ACT-AUDITOR`의 `status == 'finished'`, 결과 참조 불변, `goal_judgments`와 `events`가 4의 사본과 같고, 대기에 그 행동이 없다.
- 단언: 위 단계에 적은 것을 요약하면 다음과 같다. 문맥·스키마에 감사 `AU`가 실린다. 빈 감사 결과와 사상에 없는 판정(`invented`)은 `ValueError`(유형만)이고 판정을 덧붙이지 않는다. 제출 검사가 통과한다. 재적재 뒤 감사 판정이 `not_satisfied`로 사상되어 있고 인스턴스가 완료되지 않는다. 복구가 `submission_publication` 대기를 만들고, 재공개 뒤 실행이 `output_accepted`, 활동이 `finished`이며 판정·사건·결과 참조가 복구 전과 같다.
- 대역: 없음. 실제 Git 저장소. 실행 기록과 제출 결과물은 공급자 없이 손으로 조립한다.
- 비고: 이 모듈에서 가장 긴 시나리오다. 판정과 사건이 복구 뒤에도 같다는 단언이 "중복 없음"의 근거다.

### `test_exact_initial_input_context_survives_actual_git_restart` (행 537–546)
- 성질: 결합 문자를 담은 초기 목표는 Git 재적재 뒤에도 해석 실행 문맥의 사용자 요청과 원 원천에 코드 포인트 그대로 전달된다.
- 준비: `initialized(root, goal='Prove that é contains two Unicode codepoints.')`.
- 실행: 엔진을 새로 적재하고 `_governance_context({'role': 'intent_interpretation', 'target': 초기 입력 ID}, {})`.
- 단언: 문맥의 `user_request.text`와 `original_source.text`가 원문과 같다.
- 대역: 없음. 실제 Git 저장소.

### `test_exact_public_input_and_replay_preserve_codepoints_after_git_restart` (행 548–561)
- 성질: 공개 입력의 결합 문자는 Git 재적재 뒤의 문맥에 그대로 남고, 같은 요청 ID로 NFC 판본을 보내면 다른 내용으로 거부된다.
- 준비: `initialized(root)`.
- 실행: 공개 `control(root, iid, 'input', text='é is a two-codepoint literal', request_id='literal-input')`, `process_controls`, 엔진 재적재 뒤 `_governance_context(..., target='literal-input')`, 이어 같은 ID로 `é` 판본의 `control`.
- 단언: 문맥의 `original_source.text`와 `user_request.text`가 원문과 같다. NFC 판본은 `ValueError`(유형만).
- 대역: 없음. 실제 Git 저장소.

## ApprovalDraftTests (행 564–578)

`unittest.TestCase`를 그대로 상속한다. 표지·훅·도우미·클래스 속성이 없다.

### `test_exact_draft_reaches_existing_consumer_without_mutating_source_state` (행 565–578)
- 성질: `import_approval_draft`는 원 상태를 바꾸지 않고 기존 적용 소비자가 받는 것과 같은 승인 초안을 만들며, 검사가 범위를 다 다루지 않았으면 초안을 거부한다.
- 준비: 1단. `record_fixtures.checked_import()`의 `(instance, runtime, bundle, request)`와 그 깊은 사본.
- 실행: `governance.import_approval_draft(instance, runtime, bundle['id'])`, 그 초안으로 `apply_import_control(instance, runtime, {**request, 'config': draft})`, 이어 검사의 `scope_complete`를 거짓으로 바꾼 런타임 사본으로 다시 초안.
- 단언: 초안이 `request['config']`와 같다. 원 상태가 사본과 같다. 적용 영수증 `status == 'applied'`. 범위 미완의 초안은 `ValueError`(유형만).
- 대역: 없음.

## IntentConnections (행 581–609)

`unittest.TestCase`를 그대로 상속한다. 표지·훅·도우미·클래스 속성이 없다. 모든 시험이 `routing_engine()`(메모리 상태의 `bare_engine`, 저장소 대역 `NoRepository`, `_bind_revision_action`·`_cancel_selected_revision_targets`·`_record_output_questions`를 `create_autospec` 대역으로 바꾼 엔진)에 `engine_fixtures.intent_import`로 입력 `UC-input`('Keep the original purpose.')의 해석을 작성한다. `intent_import`는 작성 행동(`lineage_id='AC-root'`)을 `_apply`로 적용하고, 검사 실행 `EX-check`를 등록한 뒤, 대기열의 첫 행동(검사 행동)을 꺼내고 대기열을 비워 `(bundle, action)`을 돌려준다. `clarification=True`이면 해석이 차단 질문 `Q-one`을 묻는다. `intent_verdict(bundle, decision, complete)`는 독립 검사의 출력이며 승인이 아니면 발견 사항 `'Missing second clause'` 하나를 담는다.

### `test_clarification_still_receives_independent_check` (행 582–588)
- 성질: 해석이 명확화 질문을 물어도 그 질문을 기록하기 전에 독립 검사를 받는다.
- 준비: `routing_engine()`과 `intent_import(engine, clarification=True)`.
- 실행: 준비 안의 작성 단계 `_apply`가 곧 실행이다.
- 단언: 돌아온 행동의 `stage == 'check'`, `import_id == bundle['id']`. `question_links == []`. `_record_output_questions` 대역이 불리지 않았다.
- 대역: `routing_engine`의 대역.

### `test_failed_check_returns_to_authoring_with_findings` (행 590–599)
- 성질: 독립 검사가 수정 필요로 판정하면 가져오기는 발견 사항을 들고 같은 계보의 작성 단계로 돌아가며 질문을 만들지 않는다.
- 준비: `routing_engine()`과 `intent_import(engine)`.
- 실행: `engine._apply(action, intent_verdict(bundle, 'revision_required', False), 'EX-check')`.
- 단언: 대기열 첫 행동의 `stage == 'interpret'`, `lineage_id == 'AC-root'`, `previous_import_id == bundle['id']`, `intent_repair.findings == ['Missing second clause']`. `questions == []`.
- 대역: `routing_engine`의 대역.

### `test_check_cannot_apply_unresolved_proposed_changes` (행 601–609)
- 성질: 독립 검사가 승인해도 차단 질문이 풀리지 않은 제안 변경은 적용되지 않고 결정을 기다리며, 연구 준비도 대기열에 들어가지 않는다.
- 준비: `routing_engine()`과 `intent_import(engine, clarification=True, payload={'kind': 'charter', 'record': {'id': 'CH-one'}})`.
- 실행: `engine._apply(action, intent_verdict(bundle), 'EX-check')`(승인).
- 단언: 거버넌스에 `CH-one`이 없다. 가져오기의 `application.status == 'awaiting_decision'`. `question_links`가 하나다. 대기열에 `research_preparation`이 없다.
- 대역: `routing_engine`의 대역.

## GovernanceOwnerConnections (행 612–630)

`unittest.TestCase`를 그대로 상속한다. 표지·훅·도우미·클래스 속성이 없다.

### `test_control_applies_actual_checked_import_and_records_one_public_result` (행 613–630)
- 성질: 엔진의 제어 처리 루프(`_controls`)는 받은 편지함의 승인 요청을 실제 가져오기 적용으로 보내고, 공개 결과를 정확히 하나 기록하며, 한 번 저장한다.
- 준비: `governance_host()`의 상태를 `routing_engine()`에 옮겨 싣고, 런타임을 `status='ready'`, 빈 `history`, 빈 `processed_controls`로 둔다. 상태가 없는 실행은 `ended`로 채운다. `head = 'fixed-parent'`.
- 실행: `_inbox`가 `[request]`를 돌려주게 하고 `engine._controls()`.
- 단언: `CH2`의 목표가 `'Prove Q'`. 가져오기의 `application.status == 'applied'`. `history`에서 `kind == 'user_control'` 항목이 하나. `_save`가 정확히 한 번 불렸다. `_apply_extended_control`이 불리지 않았다.
- 대역: `create_autospec`으로 바꾼 `_inbox`(요청 반환), `_save`, `False`를 돌려주는 `_review_recovery_control`, `_knowledge_io_control`, `_academic_control`, `_apply_extended_control`, 그리고 아무것도 하지 않는 `_schedule_operational_reviews`, `_retry_submission_publications`, `_retry_impact_reviews`, `_run_pending_operational_repairs`.
- 비고: 다른 제어 처리기가 모두 `False`를 돌려주게 해, 승인 요청이 거버넌스 경로로만 처리됨을 격리해 본다.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈: 초기 의도 해석과 활성화의 공개 연결은 `test_initial_intent_connection`이, 헌장·정책·허가 결정의 CLI 경로는 `test_cli_advanced`가 다룬다. 계약 해시(`planning.contract_hash`)와 과제 범위 결정은 계획 모듈(`test_planning_engine` 등)과 이어진다. 목표 감사와 최종 보증은 목적 시나리오 모듈(`test_purpose_engine`)이 끝까지 몰아 확인하고, 이 모듈은 소비자 하나씩을 조립 상태에서 본다.
- 픽스처 의존: `engine_fixtures.governance_host`·`goal_audit_host`(대부분의 `CentralGovernanceTests`와 `GovernanceOwnerConnections`), `intent_import`·`intent_verdict`·`routing_engine`(`IntentConnections`); `record_fixtures.checked_import`(`ApprovalDraftTests`, 그리고 `governance_host` 안), `audited_governance`, `task_contract`; `research_fixtures.new_instance`(`PublicGitGovernanceTests.initialized`), `governance_start`, `charter`, `dispatched_launch`, `trust_fixture`, `trust_environment`.
- 이 모듈에만 있는 도우미: `PublicGitGovernanceTests`의 `initialized`, `execution_fixture`, `run_sealed_import_case`.
- 겹침과 보완: 같은 규칙이 두 층에서 짝을 이룬다. 정확한 나중 승인의 적용(`test_exact_later_control_applies_once_and_queues_followup` ↔ `test_git_sealed_import_later_control_and_restart`), 전제 변경의 거부(`test_stale_approval_rejects_and_routes_to_reauthor` ↔ `test_git_changed_premise_rejects_later_approval_and_preserves_seal`), 설정 가져오기(`test_import_configuration_uses_same_profile_and_slot_transition` ↔ `test_git_configuration_import_uses_public_transition_and_profiles`), 목표 감사(`test_audit_context_schema_binding_and_rejected_missing_results`·`test_actual_goal_consumer_stores_mapping_not_generic_satisfied` ↔ `test_public_audit_contract_and_actual_goal_judgment_survive_git_reload`), 코드 포인트 보존(`test_nfd_original_reaches_actual_context_and_coverage` ↔ 두 Git 재적재 시험).

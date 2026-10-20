# test_state_checks

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_state_checks.py` (432행) |
| 클래스 / 테스트 | 3 / 23 |
| 시험 대상 제품 코드 | `do_math/state_checks.py`의 `inspect_state`; `do_math/state_contract.py`의 `default_state_contract().validate`; `do_math/context_store.py`의 `prefetch_artifacts`; `do_math/engine.py`의 `ResearchEngine._inspect_before_write`, `check`; 준비에 쓰는 도메인 생산자 `knowledge_records.create_candidate`, `knowledge.begin_transition`·`record_transition_result`·`activate_transition`, `external.prepare_operation`·`execute_operation`, `execution_profiles.build_profiles`·`capability_evidence`·`profile_ref`; `record_schemas.RECORDS`·`REFERENCES`; `git_store.GitStateStoreError` |
| 사용하는 픽스처 모듈 | `research_fixtures`: `bare_engine`, `current_state`, `supply_observation_rules`; `record_fixtures`: `surface_state`, `task_contract`; `knowledge_fixtures`: `verified_knowledge` |
| 격리 표지 | 없음 |
| 시작 상태 | 거의 모두 1단. 도메인 생산자가 만든 사전 상태(`surface_state` 등)를 `inspect_state`나 계약 `validate`에 직접 준다. `test_engine_entry_checks_presence_and_length_while_check_compares_bytes` 하나는 `bare_engine`과 `ResearchRepository` 대역으로 엔진 입구를 부른다 |

## 목적

모듈 docstring은 "실제 도메인 생산자가 만든 레코드와 적대적 변형에 대한 저장 상태 점검"이라고 밝힌다. 클래스 `StateCheckTests`의 docstring(행 57)은 이 모듈의 핵심 분업을 밝힌다. "`inspect_state`는 적재된 상태를 받는다. 적재가 검사하는 조건은 적재에서 단언한다." 그래서 이 모듈의 변형 시험은 두 갈래로 나뉜다. 저장 계약이 막는 변형(실행 상태 값, 참조, 원천 서술, 버전 등)은 `assertRejectedAtLoad`로 계약 검증에서 거부됨을 단언한다. 적재를 통과한 상태에서만 드러나는 조건(완료의 의무 처분, 목표 감사의 현재성, 보충 조사의 연결, 예약의 실행 쪽 소유 등)은 `inspect_state`의 영역별 발견(finding)으로 단언한다. 나머지 두 클래스는 산출물 바이트 검사의 배치 읽기(`BatchedInspectionTests`)와 점검 영역의 결과 규약(`CheckAreaTests`)을 검사한다.

## 모듈 수준 요소

- 행 8: 스킬의 `scripts/` 폴더를 확인 없이 `sys.path` 맨 앞에 넣는다.
- `storage_state(refs)` (행 19–21): 원천이 없는 instance와, 실행 `EX-1` 하나의 `output_files`가 `refs`인 runtime의 쌍. `BatchedInspectionTests`의 `inspect` 도우미와 `test_engine_entry_checks_presence_and_length_while_check_compares_bytes`가 쓴다.
- `artifact(path, raw, **changes)` (행 24–26): 산출물 참조 행. `artifact_ref=path`, `raw`의 SHA-256과 길이에 `changes`를 덧씌운다. `BatchedInspectionTests`의 모든 테스트와 `archived_role_input`이 쓴다.
- `archived_role_input(bundle, snapshot, files)` (행 29–47): `runtime/artifacts/<bundle>/` 아래에 한 번 보관된 유지보수(`maintenance`) 역할 입력의 목록(manifest). 프롬프트는 `input.txt`(`b'exact prompt'`)다. 직접 입력 네 개는 `input/catalog/<키>.json`(`b'{}\n'`)이고, 키는 `snapshot`, `governance`, `execution_profile`, `action`이다. 문서 두 개는 `input/implementation/SKILL.md`와 `GLOSSARY.md`다. 출력 계약은 `do-math-cli/5`이고 참조는 비어 있다. 각 행의 바이트는 `files`에 기록된다. docstring과 행 37의 주석은 문서 행이 자기 `path` 필드를 가지므로 보관 위치는 다른 이름(`artifact_ref`)으로 적는다고 밝힌다. `test_engine_entry_checks_presence_and_length_while_check_compares_bytes`만 쓴다.
- `at_load(instance, runtime)` (행 50–53): 도메인이 만든 상태를 저장소가 검증하는 모양으로 바꾼다. runtime에서 `status`를 빼고, instance에 `object_format='sha1'`을 더해 `current_state`로 감싼다(docstring: "객체 형식과 현재 생애주기 관문"). `StateCheckTests.assertRejectedAtLoad`와 두 테스트가 직접 쓴다.
- 행 431–432: 직접 실행하면 `unittest.main(verbosity=2)`로 이 모듈의 시험을 돈다.

## StateCheckTests (행 56–282)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 설정 훅이 없다. 도우미 셋이 있다.

- `assertRejectedAtLoad(instance, runtime, pattern)` (행 59–62): `at_load`로 바꾼 상태를 `default_state_contract().validate`에 주고, `ValueError`가 정규식 `pattern`으로 나는지 단언한다.
- `area(instance, runtime, name)` (행 76–77): `inspect_state(instance, runtime, requested_areas=[name])`의 결과.
- `assertError(instance, runtime, text, area)` (행 79–81): 그 영역 결과의 `findings` 가운데 메시지에 `text`가 든 행이 있는지 단언한다. 실패하면 발견 목록을 메시지로 보인다.

도우미 정의가 첫 테스트 뒤(행 76–81)에 놓여 있다.

### `test_valid_rule_payload_is_not_an_error_list` (행 64–74)
- 성질: 유효한 관찰 규칙은 자기 점검 정지 영역에서 오류로 보고되지 않고, 규칙 값이 잘못되면 그 영역의 발견이 된다.
- 준비: `surface_state()`. `supply_observation_rules([{'title': 'fixture'}], extensions)`가 만든 과제 조건의 `observation_rules`를 실행 `EX-1`과 `runtime['task_observation_rules']['TK-fixture']`에 복사한다.
- 실행: `area(..., 'self_check_stop')`. 첫 규칙의 `threshold`를 0으로 바꾼 뒤 같은 영역을 다시 점검한다.
- 단언: 처음에는 영역 `status`가 `healthy`다. 바꾼 뒤에는 메시지에 `'positive integer'`가 든 발견이 있다.
- 대역: 없음.
- 비고: 이름은 "유효한 규칙 값은 오류 목록이 아니다"라고 말한다. 단언은 건강 상태와, 잘못된 값의 발견 메시지 조각을 본다.

### `test_domain_created_activity_execution_profiles_are_clean` (행 83–91)
- 성질: 도메인 생산자가 만든 활동·실행·프로필 상태는 계약 검증을 통과하고, 과제·활동·실행 영역 점검에서 건강하며, 점검은 상태를 바꾸지 않는다.
- 준비: `surface_state()`.
- 실행: `default_state_contract().validate(*at_load(...))`, `area(..., 'tasks_activities_executions')`를 두 번.
- 단언: 계약 검증이 예외 없이 끝난다. 영역 `status`가 `healthy`다. 첫 영역의 `checked_invariants[0]`이 `'load-time state contract validation'`이다. 곧 점검 결과가 이 영역의 첫 불변식을 적재 단계의 계약 검증으로 밝힌다. 두 번째 점검 뒤 runtime이 사본과 같다.
- 대역: 없음.

### `test_execution_state_lineage_profile_and_activity_mutations` (행 93–113)
- 성질: 실행의 상태 값, 계보(이어받기), 프로필 결속, 활동 소유를 망가뜨린 상태는 적재에서 거부된다.
- 준비: 경우마다 새 `surface_state()`의 실행 `EX-1`을 바꾼다.
- 실행: 경우마다 `assertRejectedAtLoad`(`at_load`로 바꾼 상태의 `default_state_contract().validate`)를 부른다. 다섯 경우는 실행 상태 값, 소유 활동, 이어받기 대상, 프로필 참조 ID, 프로필 내용을 하나씩 바꾼 것이다.
- 단언: `assertRejectedAtLoad`로 다섯 경우를 확인한다. `status='teleporting'`은 `'runtime/executions/EX-1/status'`로 거부된다. `owner_activity_id='absent'`는 `'executions references unknown record: absent'`로 거부된다. `continuation_of='EX-missing'`은 `'executions references unknown record: EX-missing'`으로 거부된다. `execution_profile_ref.id='EP-missing'`은 `'profile reference is absent or stale'`로 거부된다. 마지막으로 첫 실행 프로필의 `role`을 `'changed'`로 바꾸면 `'execution profile content differs from its immutable identity'`로 거부된다. 모든 경우에 거부 사유가 메시지 조각으로 고정된다.
- 대역: 없음.
- 비고: 앞의 세 경우와 프로필 참조 경우는 `subTest(field=...)` 4건으로 나뉜다. 프로필 내용 변경은 `subTest` 밖에서 확인한다. 행 94–95의 주석은 "실행 상태, 계보, 프로필 결속, 활동 소유는 적재 시점의 상태 계약 조건이고, 점검이 되풀이하지 않는다"고 밝힌다.

### `test_separated_knowledge_and_source_mutations` (행 115–135)
- 성질: 분리 저장된 지식 레코드의 참조, 원천 서술, 형식 결과의 게시 상태는 적재에서 검사된다.
- 준비: `surface_state()`에 `knowledge_records.create_candidate`로 정리(theorem) 후보 `P`를 만든다. 후보는 Lean 코드 `theorem p : True := True.intro`, 선언 이름 `['p']`를 가진다.
- 실행: `area(..., 'mathematical_effect')`로 대조군을 점검한 뒤, 세 종류의 변형(해설 참조, 원천 서술 두 필드, 형식 결과 게시 상태)마다 `assertRejectedAtLoad`를 부른다.
- 단언: 먼저 `mathematical_effect` 영역이 `healthy`다(대조군). 지식 레코드의 `exposition_id`를 `'missing'`으로 바꾼 사본은 `'knowledge references unknown record: missing'`으로 거부된다. 원천 하나(`SO-1`)의 `sha256`을 `'bad'`로, 또는 `bytes`를 -1로 바꾼 두 경우는 `'research/sources/None/' + 필드`로 거부된다. 그 지식의 형식 결과를 `publication_state='accepted'`, `formal_use='active'`로 바꾸면 `'published formal result requires verification evidence'`로 거부된다.
- 대역: 없음.
- 비고: 원천 변형은 `subTest(source_field=...)` 2건이다. 원천 거부 메시지의 경로에 `None`이 들어가는 것은 목록 가족(`sources`)의 행이 경로 안에서 ID 대신 `None`으로 표시된다는 뜻이다. 테스트는 이 표기까지 고정한다. 행 122와 132의 주석은 지식 참조와 원천 서술이 적재 조건이고, 검증 없이 게시된 형식 결과는 적재되지 않는다고 밝힌다.

### `test_formal_results_left_under_a_superseded_environment_are_not_findings` (행 137–153)
- 성질: 신뢰 환경 전환 뒤 대체된 환경 아래 남은, 여전히 승인·활성인 옛 형식 결과는 수학적 효과 영역의 발견이 아니다.
- 준비: `knowledge_fixtures.verified_knowledge()`가 준 검증된 지식과 그 형식 결과(`old`). 새 환경 `TE-next`(registered, 도구 모음 `next`)를 더한다. 옛 검증을 복사해 도구 모음만 `next`로 바꾼 결과를 만든다. `knowledge.begin_transition`, `record_transition_result`, `activate_transition`으로 전환을 끝낸다.
- 실행: `area(..., 'mathematical_effect')`.
- 단언: 옛 환경 `TE-test`의 상태가 `superseded`이고, 옛 형식 결과의 `formal_use`가 여전히 `active`다(준비가 의도한 상태인지 확인). 영역 `status`가 `healthy`다.
- 대역: 없음.
- 비고: 행 138–139의 주석은 "신뢰 전환은 대상마다 새 형식 결과를 주고, 옛 결과는 승인·활성인 채로 대체된 환경 아래 남긴다"고 밝힌다. 이 상태가 오탐되지 않음을 고정하는 회귀 시험이다.

### `test_completion_requires_all_obligations_and_authoritative_waiver` (행 155–174)
- 성질: 완료된 과제는 모든 의무를 처분한 평가를 가져야 하고, 면제(waived) 처분은 유효한 권한을 가리켜야 한다.
- 준비: `surface_state()`와 `record_fixtures.task_contract()`. 과제를 `completed`로 두고, `research_work` 프로필의 `profile_ref`를 단다. 평가는 `OB-1`만 `fulfilled`(증거 `EV-1`)로 처분하고 `unresolved`는 비운다.
- 실행: (1) 빈 `authority_refs`를 단 과제로 `assertRejectedAtLoad`. (2) 평가를 뺀 과제로 `assertError(..., 'tasks_activities_executions')`. (3) 평가를 되돌리고 면제 처분을 더해 같은 영역으로 `assertError`.
- 단언: (1) 과제의 `authority_refs`를 빈 목록으로 바꿔 runtime 사본에 넣으면 적재에서 `'every obligation'`으로 거부된다. 거부 사유는 `task_contract()`의 둘째 의무 `OB-2`에 처분도 미결 점검도 없다는 것이다(`task_contracts.py`의 `"every obligation requires a disposition or unresolved inspection"`). (2) 평가를 뺀 완료 과제는 `tasks_activities_executions` 영역에 `'assessment decision'` 발견을 낸다. (3) 평가를 되돌리고 `OB-2`를 `waived`(권한 `'missing'`, 증거 없음)로 더하면 같은 영역에 `'authority'` 발견을 낸다.
- 대역: 없음.
- 비고: 행 164와 168의 주석은 분업을 밝힌다. "적재는 기록된 모든 평가의 처분을 검사한다." "평가 없는 완료 과제는 점검 자신의 발견이다." (3)은 `OB-1`만 처분된 평가에 `OB-2`의 면제 행을 더한 것이다. 그래서 두 의무가 모두 처분되어 (1)의 의무 처분 규칙은 충족된다. 이 단계는 `inspect_state`만 부르므로 적재 검증을 거치지 않는다.

### `test_solved_goal_requires_current_complete_audits` (행 176–183)
- 성질: 수학적으로 해결된 목표는 현재(current)이고 범위가 완전한 합의 감사를 요구한다.
- 준비: `surface_state()`에 `goal_status='mathematically_solved'`, `goal_assessment_basis='GB'`를 두고, 목표 판정 `GJ-1` 하나를 넣는다. 이 판정은 기준 `GB`, 필요 수 1, 슬롯 `one`, 결정 `satisfied`, `scope_complete=True`다.
- 실행: `area(..., 'mathematical_effect')`. 판정에 `current=False`를 더한 뒤 다시 점검한다.
- 단언: 처음에는 `healthy`다. 바꾼 뒤에는 `'current agreeing audits'`가 든 발견이 있다.
- 대역: 없음.
- 비고: 이름의 "complete"(`scope_complete`)를 바꾸는 경우는 단언하지 않는다.

### `test_supplement_request_must_match_pending_review_owner` (행 185–191)
- 성질: 대기열의 보충 조사 행동은 대기 중인 검토 조사 요청의 요청 슬롯과 이어져 있어야 한다.
- 준비: `surface_state()`. 검토 주기 `RC`(working, 지식 `KN`)에 대기 중인 조사 요청 `RQ`를 둔다. 요청의 행동 슬롯은 `initial-0`이다. 대기열에는 `supplemental_research` 행동을 넣는다. 이 행동은 `RC`와 `RQ`를 가리키지만 `requesting_slot='wrong'`이다.
- 실행: `assertError(..., 'preparation_selection')`.
- 단언: `'queued investigation is not linked'`가 든 발견이 있다.
- 대역: 없음.
- 비고: 올바른 슬롯의 대조군은 없다.

### `test_external_error_http_remains_unknown_and_reconciliation_is_distinct` (행 193–219)
- 성질: 외부 요청이 HTTP 오류로 끝나면 결과는 모름(`unknown`)으로 남고, 성공 여부·조정(reconciled)·취소의 모순된 조합은 적재에서 거부된다.
- 준비: `surface_state()`. `external.prepare_operation`으로 `POST https://example.test/` 작업 `OP`를 준비하고 `producer_executions=['EX-1']`을 단다.
- 실행: `external.prepare_operation`, `jsonschema.validate`(설치 스키마), `REFERENCES['external_operations']`, `external.execute_operation`(전송·저장 람다), `area(..., 'tasks_activities_executions')`, 그리고 세 가지 모순 조합마다 `assertRejectedAtLoad`.
- 단언: 작업이 설치 스키마 `RECORDS['external_operations']`를 통과한다. `REFERENCES['external_operations']`가 `('EX-1', 'executions')`를 낸다. `producer_executions=[1]`이면 `jsonschema.ValidationError`가 난다. 이어서 `external.execute_operation`을 부른다. 권한(grant)은 활성 `GR`이고 출처·메서드·경로 접두사를 허용한다. 전송 함수는 `{'http_status': 500, 'body': b'uncertain'}`을 돌려주고, `persist`는 행을 그대로 돌려준다. 실행 뒤 작업 `status`가 `unknown`이다. runtime에 넣은 뒤 `tasks_activities_executions` 영역은 `healthy`다. `succeeded=False`는 `'definitive success'`로 거부된다. `succeeded=None`과 `handling='reconciled'`는 `'reconciled handling'`으로 거부된다. `handling`을 빼고 `status='cancelled'`로 두면 `'confirmed untransmitted'`로 거부된다.
- 대역: 전송 람다와 `persist` 람다. 행 203의 주석은 이것이 "지어낸 성공 영수증이 아니라 실제 도메인 전송 응답"이라고 밝힌다.
- 비고: 행 211의 주석은 "작업 레코드 하나가 이 사실들을 정하므로 저장 계약이 이것들을 거부한다"고 밝힌다. 네트워크는 쓰지 않는다.

### `test_capability_evidence_id_must_match_its_content_at_load` (행 221–232)
- 성질: 능력 증거(capability evidence)의 ID는 그 내용의 해시와 같아야 하며, 적재가 이것을 확인한다.
- 준비: 기본 설정에서 scholarly를 끈 `build_profiles`의 첫 프로필로 `capability_evidence`를 만든다. 신원은 `{'host': 'fixture'}`, 검증됨, `jsonl` 지원, 관찰 시각은 2026-01-01이다. 그 행을 instance에 넣는다.
- 실행: `default_state_contract().validate(*at_load(instance, {}))`. 행의 `identity`를 `{'host': 'forged'}`로 바꾼 뒤 `assertRejectedAtLoad`.
- 단언: 처음에는 통과한다. 바꾼 뒤에는 `'capability evidence ID differs from its content'`로 거부된다.
- 대역: 없음.
- 비고: 행 222의 주석은 "읽는 쪽은 저장된 ID를 다시 해시하지 않고 쓴다. 바뀐 행은 여기서 대신 거부된다"고 밝힌다.

### `test_execution_outcome_is_a_closed_value_at_load` (행 234–237)
- 성질: 실행의 결과(`outcome`)는 닫힌 값 집합에 속해야 하며 적재에서 검사된다.
- 준비: `surface_state()`의 실행을 `status='ended'`, `ended_at`, `outcome='finished'`로 바꾼다.
- 실행: `assertRejectedAtLoad`.
- 단언: 정규식 `'outcome'`으로 거부된다. 메시지 조각이 필드 이름뿐이라 거부 사유를 느슨하게 고정한다.
- 대역: 없음.

### `test_reservation_requires_balanced_settlement_and_existing_owner` (행 239–260)
- 성질: 예약 행은 정산이 예약량과 맞아야 하고, 음수가 아니며, 있는 제약과 소유자를 가리켜야 한다. 실행 쪽 예약 참조가 소유자에게 돌아가는지는 점검이 본다.
- 준비: `surface_state()`의 첫 용량 제약을 쓰는 정산된 예약 `R`이다. 단위는 `session`이고, 예약 1, 소비 확인 1, 반환 0이다. 소유자는 실행 `EX-1`이고 증거는 `EV-1`이다.
- 실행: 네 변형마다 `runtime['reservations']`를 바꾸고 `assertRejectedAtLoad`를 부른다. 이어서 소유자를 `EX-other`로 둔 예약과 실행 쪽 예약 참조로 `assertError(..., 'tasks_activities_executions')`.
- 단언: 네 변형이 적재에서 거부된다. 소비 0과 빈 증거는 `'settled reservation must account for reserved exactly'`로 거부된다. `reserved=-1`은 `'reserved'`로 거부된다. `constraint_id='CC-missing'`은 `'reservations references unknown record: CC-missing'`으로 거부된다. `owner_id='EX-missing'`은 `'reservations references unknown record: EX-missing'`으로 거부된다. 이어서 소유자를 `EX-1`이 아닌 ID `EX-other`로 두고, 실행 `EX-1`의 `capacity.reservation_ids=['R']`로 두면 `tasks_activities_executions` 영역에 `'execution reservation does not resolve to its owner'` 발견이 난다.
- 대역: 없음.
- 비고: 네 변형은 `subTest(change=...)` 4건이다. 행 240–241의 주석은 "예약 회계와 참조는 적재 조건이고, 입장(admission)은 그것을 통과한 예약만 읽는다(`budget.plan_reservations`)"고 밝힌다. 행 256의 주석은 점검이 실행 쪽 소유 확인을 유지한다고 밝힌다. `EX-other`는 `surface_state`에 없는 실행이다. 마지막 단계는 적재를 거치지 않고 점검만 부른다.

### `test_requested_area_never_reuses_other_domain_findings` (행 262–271)
- 성질: 요청한 점검 영역은 다른 영역의 발견을 가져오지 않고, 점검하지 않은 영역은 건강이 아니라 미완(`incomplete`)이다.
- 준비: `surface_state()`의 실행에 원장 행이 없는 예약 참조 `R-missing`을 둔다.
- 실행: `tasks_activities_executions`, `governance_trust`, `start_import_input` 영역을 각각 점검한다.
- 단언: 첫 영역에 `'execution reservation does not resolve to its owner'` 발견이 있다. `governance_trust`는 `healthy`다. `start_import_input`은 `status='incomplete'`이고, 첫 영역의 `not_checked`가 참 값이다.
- 대역: 없음.
- 비고: `start_import_input`이 미완인 이유는 `surface_state`의 AI 실행 `EX-1`이 빈 목록 `input_manifest=[]`를 가지기 때문이다. 제품 `state_checks.py`(행 317–319)는 `direct`를 가진 사전이 아닌 역할 입력 목록을 "점검하지 못함"(`omitted`)으로 적는다. 단언은 미완 표지만 확인한다.

### `test_unknown_version_and_old_state_are_not_new_contract_success` (행 273–282)
- 성질: 알 수 없는 기능 버전과 옛 생애주기의 상태는 새 계약의 성공으로 적재되지 않는다.
- 준비: `surface_state()`.
- 실행: instance 버전 변형과 runtime 버전 변형에 `assertRejectedAtLoad`를 부르고, 새 상태를 `at_load` 없이 `default_state_contract().validate({**instance, 'object_format': 'sha1'}, runtime)`에 준다.
- 단언: instance에 `feature_version=99`를 두면 `'research/feature_version'`으로 거부된다. runtime에도 같은 값을 두면 `'feature_version'`으로 거부된다. 새 `surface_state()`를 `at_load` 없이(runtime의 `status`를 남기고 생애주기를 덧씌우지 않은 채) 객체 형식만 더해 검증하면 `ValueError`가 정규식 `'^runtime/status/'`로 난다.
- 대역: 없음.
- 비고: 행 274의 주석은 "버전과 생애주기는 적재 조건이고, 점검은 적재된 상태만 받는다"고 밝힌다. 두 번째 단언은 instance의 변형을 되돌리지 않은 채 runtime에도 버전을 둔다. 그래서 거부가 runtime 쪽에서 났는지는 가리지 않는다.

## BatchedInspectionTests (행 285–388)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 설정 훅이 없다.

- `inspect(refs, single, batch=None)` (행 286–288): `storage_state(refs)`로 `inspect_state`를 부른다. 영역은 `record_storage`이고, `read_artifact=single`, `read_artifacts=batch`다.

### `test_batch_keeps_each_reference_check_and_binary_bytes` (행 290–303)
- 성질: 배치 읽기를 쓰는 점검은 개별 읽기와 같은 결과를 내고, 참조마다의 검사와 이진 바이트를 보존하며, 파일을 다시 읽지 않는다.
- 준비: 산출물 두 개. `empty`는 빈 바이트이고, `raw`는 `b'\x00\xff\r\nblob missing\n'`이다. 참조는 두 파일의 올바른 행에, `empty` 경로를 가리키지만 `sha256='0'*64`인 셋째 행을 더한 것이다.
- 실행: 개별 읽기(`files.__getitem__`)만으로 점검한 기대 결과와, 배치 읽기 대역을 준 점검 결과를 비교한다.
- 단언: 두 결과가 같다. 기대 결과의 `status`가 `blocked`다(셋째 행의 해시 불일치). 영역의 `checked_invariants`에 `'artifact bytes'`가 한 번만 나온다. 배치는 `list(files)`로 정확히 한 번 불렸다. 경로 중복을 없애고 순서를 지킨 목록이다. 개별 읽기 대역은 불리지 않았다.
- 대역: `single = Mock(side_effect=AssertionError('normal batch must not read files again'))`, 사전 조회 `batch` `Mock`.
- 비고: 행 300의 주석은 영역이 확인한 참조 수와 상관없이 불변식 이름을 한 번만 적는다고 밝힌다. 바이트 `b'\r\n'`과 `b'blob missing'`은 줄바꿈 변환이나 Git 출력 해석이 끼면 드러나도록 고른 값으로 보인다. 원문에 그 이유를 밝힌 주석은 없다.

### `test_failed_batch_preserves_individual_error_order_and_scope` (행 305–321)
- 성질: 배치 읽기가 통째로 실패하면 개별 읽기로 돌아가, 오류의 순서와 범위가 개별 읽기만 쓴 경우와 같다.
- 준비: `bad`(저장 `b'changed'`, 참조 해시는 `b'original'`), `good`, 파일이 없는 `missing`. 개별 읽기 함수는 없는 경로에 `FileNotFoundError('missing fixture: ...')`를 던진다.
- 실행: 개별 읽기만 쓴 기대 결과와, `GitStateStoreError('one requested blob is missing')`를 던지는 배치 대역을 준 결과를 비교한다.
- 단언: 두 결과가 같다. 개별 읽기 대역이 받은 경로 순서가 `paths`(bad, good, missing)다. 발견의 상태 목록이 `['blocked', 'incomplete']`다. 해시 불일치는 막힘이고, 없는 파일은 미완이다.
- 대역: `Mock(side_effect=read)` 개별 읽기, `Mock(side_effect=GitStateStoreError(...))` 배치.
- 비고: 제품 `prefetch_artifacts` docstring은 "통째로 실패한 배치는 호출자의 기존 경로로 개별 읽혀, 오류의 순서와 범위가 국소적으로 남는다"고 밝힌다.

### `test_next_inspection_reads_fresh_bytes` (행 323–331)
- 성질: 배치로 읽은 바이트는 그 점검에만 속하고, 다음 점검은 새로 읽는다.
- 준비: 산출물 하나(`b'original'`)와 그 참조.
- 실행: 배치 대역으로 점검한 뒤 저장 바이트를 `b'changed'`로 바꾸고 다시 점검한다.
- 단언: 첫 점검은 `healthy`, 둘째 점검은 `blocked`이고, 배치가 두 번 불렸다.
- 대역: 사전 조회 `batch` `Mock`.

### `test_empty_or_unavailable_batch_needs_no_new_reader_contract` (행 333–343)
- 성질: 읽을 경로가 없거나 배치 읽기 함수가 없으면 원래 개별 읽기 함수를 그대로 쓰고, 배치가 빠뜨린 경로는 그 경로만의 오류가 된다.
- 준비: `b'single'`을 돌려주는 개별 대역과 `{}`를 돌려주는 배치 대역.
- 실행: `prefetch_artifacts([], single, batch)`, `prefetch_artifacts(['one'], single)`, `prefetch_artifacts(['one'], single, batch)`의 읽기 함수로 `'one'`과 `'another'`를 읽는다.
- 단언: 앞의 두 호출은 `single` 객체 자신을 돌려준다(`assertIs`). 빈 경로 목록에서는 배치가 불리지 않는다. 셋째의 읽기 함수는 `'one'`에 `ValueError`를 `'artifact is missing: one'`으로 던진다. 요청하지 않은 `'another'`에는 개별 읽기의 `b'single'`을 돌려준다.
- 대역: 두 `Mock`.
- 비고: 행 340의 주석은 "배치는 스냅숏에 없는 요청 경로를 결과에서 뺀다"고 밝힌다.

### `test_engine_entry_checks_presence_and_length_while_check_compares_bytes` (행 345–388)
- 성질: 엔진 입구의 쓰기 전 점검(`_inspect_before_write`)은 산출물의 존재와 길이만 한 번에 확인하고 바이트를 읽지 않는다. 바이트 비교는 `check`의 몫이며, 두 경로 모두 처음 관찰한 스냅숏을 유지한다.
- 준비: 머리 `'a'*40`. 출력 산출물 `BA-output/result.bin`(`b'\x00\xff'`)을 `storage_state`의 출력 파일로 둔다. 실행에 `input_bundle='BA-input'`과 `archived_role_input('BA-input', head, files)`의 입력 목록을 단다. 엔진은 `bare_engine(..., head=head, store=create_autospec(ResearchRepository, instance=True))`다. 저장소 대역의 `load`는 그 상태를 돌려주고, `read`는 부르면 `AssertionError('normal inspection must use batch reads')`를 던진다. `read_many`는 `batch`이고 `blob_sizes`는 `sizes`다. 둘 다 받은 `(snapshot, missing)`이 `(head, 'omit')`인지 단언하고, 스냅숏에 있는 경로만 돌려준다. `batch`는 부를 때 `engine.head`를 `'b'*40`으로 바꾼다. 행 360의 주석대로, 뒤따르는 콜백이 관찰한 스냅숏을 유지하는지 보기 위해서다.
- 실행: `engine._inspect_before_write()`와 `engine.check(requested_areas=['start_import_input'])`를 네 단계로 번갈아 부른다. (1) 원래 상태. (2) 같은 길이로 바꾼 프롬프트. (3) 지운 프롬프트. (4) 짧아진 출력 산출물. 단계 사이에 `engine.head`를 `head`로 되돌린다.
- 단언: (1) `_inspect_before_write()`. 행 370의 주석대로 run·controls 입구는 산출물 바이트를 읽지 않으므로 `read_many` 호출 수가 0이다. `check(requested_areas=['start_import_input'])['passed']`가 참이다. (2) 머리를 되돌리고 입력 프롬프트를 같은 길이의 `b'exact prompX'`로 바꾼다. `_inspect_before_write()`는 통과한다. `check`는 `passed=False`이고, 발견 메시지에 `'EX-1: input artifact bytes differ: prompt'`가 있다. (3) 입력 프롬프트를 지우면 `_inspect_before_write()`가 `ValueError`를 `'current input artifact is missing: EX-1'`로 던진다. (4) 출력 산출물을 `b'\x00'`로 줄이면 `ValueError`를 `'repaired before publication'`으로 던진다. 끝으로 `read`는 한 번도 불리지 않았다.
- 대역: `bare_engine`, `create_autospec(repository.ResearchRepository, instance=True)`, 지역 함수 `batch`와 `sizes`.
- 비고: (4)는 입력 프롬프트가 지워진 채로 진행한다. 그래도 출력 길이 불일치가 `record_storage` 점검에서 먼저 걸려 `"current state evidence must be repaired before publication: ..."`가 난다(제품 `_inspect_before_write` 행 4179–4183). 제품 docstring은 "존재와 저장 길이만 본다. `check`가 전체 바이트를 비교한다"고 밝힌다. 행 376의 주석은 `start_import_input` 영역이 프롬프트를 포함한 보관 역할 입력을 모두 비교한다고 밝힌다.

## CheckAreaTests (행 391–428)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다.

### `test_cleanup_aborted_attempt_is_not_healthy` (행 392–398)
- 성질: 중단된 정리 시도의 이력이 있으면 기록 저장 영역은 건강하지 않다.
- 준비: `surface_state()`의 `history`를 `maintenance_cleanup_failed` 항목 하나로 바꾼다. 이 항목은 `runs/EX-1`을 대상으로 하고, 완료 경로가 없으며, 사유는 `'root inaccessible'`, 다음 소유자는 `maintenance`다.
- 실행: `inspect_state(..., requested_areas=['record_storage'])`.
- 단언: `status`가 `degraded`다.
- 대역: 없음.

### `test_cleanup_history_is_the_degraded_source` (행 400–410)
- 성질: 정리 이력의 가장 최근 결과가 저하의 원천이며, 뒤이은 성공한 정리가 그것을 해소한다.
- 준비: `surface_state()`의 `history`에 저하된 `maintenance_cleanup` 결과를 더한다. 실패 행은 `runs/EX-1`, `'locked'`, 다음 소유자 `maintenance`다.
- 실행: 기록 저장 영역 점검. 이어서 `runs/EX-1`을 지운 건강한 정리 결과를 더하고 다시 점검한다.
- 단언: 처음에는 `degraded`이고, 발견 가운데 문자열로 바꿨을 때 `'runs/EX-1'`을 담은 행이 있다. 성공 결과를 더한 뒤에는 `healthy`다.
- 대역: 없음.

### `test_area_errors_are_not_copied_to_unrelated_areas` (행 412–415)
- 성질: 한 영역의 오류는 함께 요청한 다른 영역의 발견으로 복사되지 않는다.
- 준비: 이름 없는 원천 하나(`sha256`만 있음)를 가진 instance와, 빈 활동·실행·과제의 runtime.
- 실행: `requested_areas=['record_storage', 'tasks_activities_executions']`로 점검.
- 단언: `record_storage` 영역에 `'source[0]: missing name'` 발견이 있다. `tasks_activities_executions` 영역에는 `'source[0]'`을 담은 발견이 없다.
- 대역: 없음.

### `test_requested_check_areas_distinguish_unchecked_from_healthy` (행 417–428)
- 성질: 점검한 영역과 점검하지 못한 영역은 결과에서 구별되며, 알 수 없는 영역은 미완으로 보고되고 운영자에게 넘겨진다.
- 준비: 빈 원천·지식·신뢰 환경의 instance와, `status='ready'`인 빈 runtime.
- 실행: `record_storage` 영역 점검, 그리고 알 수 없는 영역 `not_an_area` 점검.
- 단언: 앞의 결과는 `status='healthy'`, `not_checked=[]`, 첫 영역 이름 `record_storage`다. 뒤의 결과는 `status='incomplete'`, `not_checked=['not_an_area']`이고, `areas`가 정확히 `[{"name": "not_an_area", "status": "incomplete", "checked": False, "findings": 1}]`이며, 첫 발견의 `next_owner`가 `operator`다.
- 대역: 없음.

## 관계

- 적재 거부의 정본인 계약 검증은 `test_state_contract`(`test_invalid_execution_and_activity_are_rejected_by_the_state_contract`)가 계약 층에서 검사한다. 이 모듈의 `assertRejectedAtLoad` 시험들은 같은 계약을 여러 도메인의 변형에 적용한다.
- 상태 보고(`snapshot_report`)가 이 점검을 부르는 경로와, 보고 쪽의 길이만 보는 산출물 확인은 `test_reporting`이 검사한다. 이 모듈의 마지막 `BatchedInspectionTests` 테스트는 같은 "길이는 입구, 바이트는 check" 분업을 엔진 입구에서 확인한다.
- 정리 규칙 자체는 `test_retention`이 검사한다. `CheckAreaTests`의 두 정리 테스트는 그 이력이 점검 결과로 어떻게 읽히는지만 본다.
- 예약 산술은 `test_budget`이, 외부 작업의 실행 경로는 `test_external_operations`와 `test_external`이, 신뢰 전환은 `test_knowledge` 계열이 맡는다. 이 모듈은 그 결과 상태의 적재·점검 규칙만 본다.
- 픽스처 의존: `research_fixtures.bare_engine`, `current_state`, `supply_observation_rules`; `record_fixtures.surface_state`, `task_contract`; `knowledge_fixtures.verified_knowledge`.
- 이 모듈에만 있는 도우미: 모듈 함수 `storage_state`, `artifact`, `archived_role_input`, `at_load`와, 클래스 도우미 `assertRejectedAtLoad`, `area`, `assertError`, `inspect`.

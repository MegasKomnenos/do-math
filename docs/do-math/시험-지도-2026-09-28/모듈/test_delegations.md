# test_delegations

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_delegations.py` (311행) |
| 클래스 / 테스트 | 3 / 11 |
| 시험 대상 제품 코드 | `do_math/delegations.py`의 `case_basis_reference_ids`, `prepare_application`, `record_judgment`, `judgment_input`, `authorize_delegated_case`, `apply_application`, 간접으로 `_basis`, `_checked`, `_check_judgment`, `validate_delegation`; `do_math/governance.py`의 `apply_decision`(`grant`, `delegation`), `preserve_source`, `authorize_review_replacement`; `do_math/engine.py`의 `ResearchEngine._review_recovery_control`, `_apply_delegation_judgment`; `do_math/review_engine.py`의 `_record_review_recovery`; `do_math/activities.py`의 `open_activity`, `assign_execution`; `do_math/execution_lifecycle.py`의 `create_execution`; `do_math/execution_profiles.py`의 `profile_ref`; `do_math/repository.py`의 `ResearchRepository` |
| 사용하는 픽스처 모듈 | `research_fixtures`(`new_instance`), `record_fixtures`(`domain_governance`), `review_fixtures`(함수 안에서 import하는 `ReviewFakeEngine`, `grant_replacement`) |
| 격리 표지 | 없음 |
| 시작 상태 | 대부분 1단(사전 상태에 순수 함수). `test_structured_reference_survives_git_and_stales_when_its_record_changes`는 4단(`new_instance`로 공개 `initialize`, 실제 Git 저장소). `test_actual_engine_delegation_control_to_independent_judgments_effect_and_receipt`는 `review_fixtures.ReviewFakeEngine`(저장소 없는 실제 엔진 하위 클래스) |

## 목적

모듈 docstring은 "위임된 결정: 한 사례에 대한 독립 판단들, 저장된 사례 참조, 교체 권한의 재사용"을 시험한다고 밝힌다.

위임(delegation)은 사용자가 한 번 내린 원 결정(`original_decision_id`)을 명시된 범위(`included_targets`, 외부 효과, 자원 한도, 만료) 안에서 같은 종류의 새 사례에 다시 쓰게 하는 기록이다. 제품은 사례 하나를 적용하기 전에 `prepare_application`으로 사례와 원 결정·위임·승인·대상 기록을 묶은 근거(basis)를 만들고 그 해시(`input_sha256`)를 봉인한다. 그다음 서로 다른 두 실행(`interpret` 단계와 `check` 단계, 둘 다 `intent_interpretation` 역할)이 같은 봉인 입력만 받아 "범위 안(`within_scope`)"인지 판단한다. 두 판단이 모두 범위 안이고 근거가 여전히 현재일 때만 `authorize_delegated_case`가 허용하고 `apply_application`이 효과를 적용한다. 효과는 권한 가족(결정, 허가, 위임, 거버넌스, 거버넌스 원천)을 바꿀 수 없다.

이 모듈은 다음을 본다.

- 사례의 근거 참조 모양은 닫혀 있고, 저장소를 왕복해도 유지되며, 참조 기록이 바뀌면 적용 근거가 낡는다.
- 두 독립 판단이 같은 현재 사례에 있어야 적용되고, 적용은 한 번이며, 위임이 철회되면 적용할 수 없다.
- 위임 승인은 실제 위임 내용을 묶어야 한다.
- 호출자가 주장한 독립 표지는 실제 판단 실행을 대신하지 못한다.
- 판단 입력의 해시는 전체 문맥이 아니라 사례 해시다.
- 위임 효과는 보존된 권한 원천을 고칠 수 없다.
- 엔진의 검토 복구 제어가 두 판단 작업을 만들고, 판단 적용과 교체 실행까지 이어진다.
- 검토 교체는 일반 기계 허가로도 되며, 위임 사례를 쓸 때는 사례·주기·효과가 다시 확인되고, 만료되거나 검사 판단이 없으면 재사용이 거부된다.

## 모듈 수준 요소

- 행 11: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리.
- `replacement_case()` (행 25–48): docstring은 "`K`의 검토를 대체하는 위임 검토 교체로, 아직 적용되지 않은 것"이다. `domain_governance()`에 지식 `K`(개정 1)와 검토 주기 `RC`(대상 `K`, 개정 1)를 둔다. 교체 작업 `ACTION`은 `identity_review` 역할, 목적 `record_replacement`, 주기 `RC`, 단계 `initial`, 슬롯 `R1`, 회차 0, `replacement_for=0`, 연속성 단절 원인 `permanent_loss`다. `gov.apply_decision`으로 지역 허가 `G`(역할 `identity_review`, 재사용 가능, 대상 `K`, 목적 `record_replacement`)를 채택한다. 사용자 원 결정 `ORIGINAL`(`review_replacement`)을 두고, `apply_decision`으로 위임 `DG`(결정 종류 `review_replacement`, 대상 `K`, 만료 2099년)를 채택한다. 사례 `CASE`는 작업의 여섯 필드를 효과로 갖고 근거 참조가 `['RC']`다. `(instance, runtime, action, case)`를 돌려준다. 함수 안에서 `delegations`를 `d`로 import하지만 쓰지 않는다. `checked_replacement_case`와 두 시험(`test_delegation_uses_case_hash_not_full_context_hash`, `test_general_machine_grant_does_not_require_new_semantic_delegation`)이 직접 쓴다.
- `checked_replacement_case()` (행 51–60): docstring은 "두 독립 판단이 모두 범위 안이라고 본 위임 적용을 가진 `replacement_case`"다. `prepare_application`으로 적용을 만들고, 실행 `INTERPRET`와 `CHECK`(둘 다 `intent_interpretation`, 봉인 입력 해시를 가짐)를 두어 각 단계의 `within_scope` 판단을 `record_judgment`로 기록한다. 사례에 `application_id`를 더해 돌려준다. 세 시험이 쓴다.
- 행 310–311: 직접 실행하면 `unittest.main()`.

## DelegationStorageTests (행 63–149)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다.

### `test_structured_case_reference_is_closed` (행 64–66)
- 성질: 사례의 근거 참조는 기록 ID 문자열이나 정확히 `{'id': ID}`인 객체만 받는다.
- 준비: `{"id": "SO-one", "sha256": "not-a-binding"}` 객체 하나를 근거 참조로 가진 사례.
- 실행: `case_basis_reference_ids(...)`.
- 단언: `ValueError`이고 메시지가 `"case basis reference"`에 맞는다. 제품 메시지는 `"case basis reference must be a record ID or an exact {'id': ID} object"`다.
- 대역: 없음.

### `test_structured_reference_survives_git_and_stales_when_its_record_changes` (행 68–149)
- 성질: 객체 모양(`{'id': ...}`)의 근거 참조를 가진 위임 적용은 Git 저장소에 저장·재적재된 뒤에도 허용되고, 참조한 원천 기록이 바뀌면 "낡음"으로 거부된다.
- 준비: 임시 폴더에 원천 파일 `source.txt`를 쓰고, `new_instance`로 Git 저장소를 만들어 공개 `initialize`를 돈다(원천 하나, `scholarly_enabled`·`operator_enabled` 끔, `lean_command=["fixture-lean"]`). `ResearchRepository`로 적재한다. 사용자 원천 `GS-delegation`을 보존하고, `apply_decision`으로 원 결정 `DC-original`의 지역 허가 `GR-original`(역할 `maintenance`)과 위임 `DG-source`(결정 종류 `grant`, 대상은 원천 ID, 만료 없음)를 채택한다. 사례 `CASE-source`의 근거 참조는 `[{"id": source_id}]`다.
- 실행:
  1. `prepare_application`으로 적용을 만들고 `save_with_state`와 `load`로 왕복한다.
  2. `intent_interpretation` 실행 프로필을 찾아, 두 단계(`interpret`, `check`)마다 활동(`delegation_judgment`)을 열고, `execution_lifecycle.create_execution`으로 실행을 만들어 역할과 봉인 입력 해시를 달고, 활동에 배정한 뒤 `record_judgment`로 `within_scope` 판단을 기록한다. 다시 저장·적재한다.
  3. `authorize_delegated_case(instance, "DG-source", {"application_id": ...}, runtime=runtime)`.
  4. 원천의 `revision`을 2로 바꾸고 저장·적재한 뒤 다시 허가를 묻는다.
- 단언: (3)의 `allowed`가 참(실패 메시지로 결과 전체). (4)의 `allowed`가 거짓이고 `reason`이 정확히 `"delegation application stale"`이다.
- 대역: 없음.
- 비고: 실제 외부 자원으로 Git 자식 프로세스를 쓰고, 공개 초기화를 처음부터 돈다. 원천 파일 바이트는 바꾸지 않고 저장된 원천 기록의 `revision`만 바꾼다.

## DelegationJudgmentTests (행 152–281)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다.

### `test_delegation_requires_two_real_judgments_on_same_current_case` (행 153–178)
- 성질: 두 실제 판단이 같은 현재 사례에 있으면 효과가 적용되고, 적용은 권한 기록을 만들지 않으며, 다시 적용해도 효과가 반복되지 않고, 위임이 철회되면 적용할 수 없다.
- 준비: `domain_governance()`에 사용자 원 결정 `ORIGINAL`과 위임 `DG`(대상 `T`)를 직접 넣는다. 위임의 `decision_id`를 `"D"`로 두었다가 바로 `"DD"`로 바꾸고, 위임 내용을 그대로 담은 사용자 결정 `DD`를 둔다. 과제 `T`(`waiting`). 사례 `CASE`의 효과는 `{"replace_slot": "R"}`이다.
- 실행: `prepare_application`, 두 실행 `E1`(`interpret`)·`E2`(`check`)의 `within_scope` 판단 기록, 과제를 `ready`로 바꾸고 상태에 `replacement`를 적는 효과 함수로 `apply_application`. 결과 상태로, 부르면 시험을 실패시키는 효과 함수와 함께 다시 적용. 위임 `status`를 `"revoked"`로 바꾸고 원래 상태로 적용.
- 단언: 적용 뒤 상태의 `replacement`가 `{"replace_slot": "R"}`, 결과 인스턴스의 `decisions`에 적용 ID가 없다. 재적용의 상태가 첫 적용 상태와 같다. 철회 뒤 적용은 `ValueError`(유형만).
- 대역: 효과 함수(`effect`, `self.fail`을 부르는 람다).
- 비고: 재적용은 제품이 영수증을 보고 효과 함수를 부르지 않고 돌아가므로 `self.fail`이 불리지 않는다. 철회 뒤 거부는 제품의 `validate_delegation`의 `"delegation inactive"` 경로다.

### `test_delegation_approval_must_bind_the_actual_delegation` (행 180–186)
- 성질: 위임의 승인 결정이 그 위임 내용을 묶지 않으면 적용을 준비할 수 없다.
- 준비: `domain_governance()`에 원 결정 `ORIG`(`custom_case`)와 위임 `DG`를 넣는다. 위임의 `decision_id`는 `"D"`로, 이것은 도메인 거버넌스의 헌장 승인 결정이지 위임 결정이 아니다.
- 실행: `prepare_application(i, {"tasks": {"T": {"id": "T"}}}, "DG", case)`.
- 단언: `ValueError`(유형만).
- 대역: 없음.
- 비고: 제품의 `_basis`에는 승인 관련 거부가 둘 있다(`"delegation has no current user approval"`, `"approval does not bind the exact delegated scope"`). 이 시험은 어느 쪽에서 거부되는지 고정하지 않는다.

### `test_case_delegation_requires_explicit_scope_and_independent_check` (행 188–206)
- 성질: 호출자가 사례에 붙인 `independent=True` 표지는 실제 판단 실행을 대신하지 못한다.
- 준비: 활성 위임 `DG`(결정 종류 `task_scope`, 대상 `T`)만 가진 인스턴스.
- 실행: `authorize_delegated_case`를 두 번. 사례에 `check={"decision": "match", "scope_complete": True, "independent": True}`를 붙인 경우와 `independent: False`인 경우.
- 단언: 두 결과 모두 `allowed`가 거짓이다.
- 대역: 없음.
- 비고: 주석은 "호출자의 `independent=True` 표지는 어느 실제 실행도 해결하지 않는다"고 적는다. 두 사례 모두 `application_id`가 없어 제품의 `_checked`가 `"application not found"`로 거부하므로, 두 결과의 거부 사유는 같다. 이름의 "explicit scope"에 해당하는 범위 판정은 이 시험에서 따로 드러나지 않는다.

### `test_delegation_uses_case_hash_not_full_context_hash` (행 208–224)
- 성질: 판단 실행의 입력 일치는 전체 역할 문맥의 해시가 아니라 봉인된 사례 입력 해시로 판정되고, 적용 영수증은 사례 효과를 담으며 허가를 바꾸지 않고, 재적용은 같은 영수증을 돌려준다. 검사 실행의 역할이 바뀌면 허가가 거부된다.
- 준비: `replacement_case()`로 적용을 만들고, 실행 `AUTHOR`와 `CHECKER`에 서로 다른 전체 문맥 해시(`input_manifest.prompt.sha256`)와 같은 `delegation_input_sha256`을 주어 판단을 기록한다.
- 실행: 검토 주기에 효과를 적는 효과 함수로 `apply_application`, 같은 결과로 다시 적용, 이어서 `CHECKER`의 역할을 `research_work`로 바꾸고 `authorize_delegated_case`.
- 단언: 영수증의 `effect`가 사례의 `effect`와 같다. 결과 인스턴스의 `grants`가 원래와 같다. 재적용의 영수증이 첫 영수증과 같다. 역할 변경 뒤 `allowed`가 거짓이다.
- 대역: 효과 함수.
- 비고: 제품의 `_judgment_input_hash`는 실행의 `delegation_input_sha256`만 읽는다(주석: 엔진은 전체 역할 문맥을 사례와 따로 봉인한다). 역할 변경은 `_check_judgment`의 `"judgment execution must bind blind shared input"`에서 거부된다.

### `test_delegated_effect_cannot_rewrite_preserved_authority_source` (행 226–231)
- 성질: 위임 효과가 권한 원천(`governance_sources`)에 새 행을 더하면 적용이 거부된다.
- 준비: `checked_replacement_case()`.
- 실행: 인스턴스의 `governance_sources`에 위조 원천 `NEW`를 더하는 효과 함수로 `apply_application`.
- 단언: `ValueError`(유형만). 제품 메시지는 `"delegated application cannot alter authority"`다.
- 대역: 효과 함수.

### `test_actual_engine_delegation_control_to_independent_judgments_effect_and_receipt` (행 233–281)
- 성질: 엔진의 검토 복구 제어는 위임 사례에 대해 두 독립 판단 작업을 큐에 넣고, 두 작업은 같은 입력을 받으며, 두 판단이 적용되면 권한 기록은 바뀌지 않은 채 교체 검토가 큐에 들어가고, 그 교체가 실행되어 지식이 사용 가능해지고 교체 영수증이 남는다.
- 준비: 임시 폴더에 `ReviewFakeEngine(root)`를 만든다. 이 대역 엔진은 검증된 형식 증거를 가진 정리 `K1`과 검토 정책을 갖고 저장소 없이 돈다. `grant_replacement(engine)`로 교체 허가 `GR-review`를 채택하고, `engine.start('K1')`로 검토를 연다. 대기 중인 검토 작업을 복사해 `engine._record_review_recovery(action, ValueError('permanent_loss'), retryable=False)`로 영구 손실을 기록한다. 사용자 원 결정 `ORIGINAL`과 위임 `DG`(대상 `K1`)를 채택한다. 작업의 주기·단계·슬롯·회차와 `replacement_for=0`, `permanent_loss`로 효과를 만들고, 근거 참조가 검토 주기 ID인 사례를 만든다. 유지보수 역할의 사용자 제어 요청 `REQUEST`(`review_replacement`에 작업, 허가, 위임, 사례)를 이력에 `user_control`로 남긴다.
- 실행:
  1. `ResearchEngine._review_recovery_control(engine, request)`.
  2. 큐에서 `delegation_application_id`를 가진 두 작업을 찾고, `delegations.judgment_input`으로 공유 입력을 얻는다. 권한 가족(`decisions`, `grants`, `delegations`)의 사본을 뜬다.
  3. 두 작업마다 끝난 `intent_interpretation` 실행(`DG-0`, `DG-1`)을 두고 `ResearchEngine._apply_delegation_judgment(engine, stage, {'delegation_judgment': ...}, eid)`로 `within_scope` 판단을 적용한다.
  4. 교체 작업(`replacement_for`가 있는 작업)을 큐 맨 앞으로 옮기고 `engine.execute(record_first=True)`, 이어서 `engine.execute()`.
- 단언: (1)이 참. 판단 작업이 2개. 각 작업 앞에서 `judgment_input`이 처음 얻은 값과 같다. 적용 기록의 판단 키가 `{'interpret', 'check'}`, 적용 효과가 만든 효과와 같다. 권한 가족이 사본과 같다. (4) 뒤 `engine.usable()`이 참이고, 검토 주기의 `replacement_receipts`가 참(비어 있지 않음)이다.
- 대역: `review_fixtures.ReviewFakeEngine`(저장소 없는 실제 엔진, `_save`는 대역, 검토자 응답을 스크립트로 적용). 실행 기록은 손으로 넣는다.
- 비고: 실행의 `input_sha256`에 `'full-context-' + eid`를 주어, 전체 문맥 해시가 실행마다 달라도 판단이 받아들여짐을 앞 시험과 같은 방식으로 확인한다.

## ReplacementAuthorityTests (행 284–307)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다.

### `test_general_machine_grant_does_not_require_new_semantic_delegation` (행 285–291)
- 성질: 검토 교체는 일반 기계 허가만으로 허용되며, 허가의 보존 원천이 바뀌거나 허가가 만료되면 거부된다.
- 준비: `replacement_case()`.
- 실행: `gov.authorize_review_replacement(i, rt, action)`. 원천 `S`의 문장 끝에 `'!'`를 붙인 사본으로 다시. 허가 `G`의 `expires_at`을 2000년으로 바꾸고 다시.
- 단언: 처음은 `allowed`가 참, 나머지 둘은 거짓이다.
- 대역: 없음.
- 비고: 제품은 위임 ID가 없으면 `authority_mode="machine_grant"`로 허용한다. 원천 변경은 `validate_grant_source`, 만료는 `authorize`에서 거부된다.

### `test_real_checked_case_resolves_knowledge_and_rechecks_cycle_and_exact_effect` (행 293–300)
- 성질: 검사를 마친 위임 사례로 교체를 허용하되, 효과가 검사된 사례와 다르거나 검토 주기가 바뀌면 거부한다.
- 준비: `checked_replacement_case()`.
- 실행: `authorize_review_replacement(i, rt, action, delegation_id='DG', case=case)`. 효과의 `slot`을 `'OTHER'`로 바꾼 위조 사례로 `delegations.authorize_delegated_case`. 검토 주기 `RC`의 `revision`을 2로 바꾸고 원 사례로 다시 `authorize_review_replacement`.
- 단언: 처음은 참, 위조는 거짓, 주기 변경 뒤는 거짓이다.
- 대역: 없음.
- 비고: 위조 사례는 제품의 `"requested case differs from independently checked effect"`, 주기 변경은 근거 해시가 달라져 `"delegation application stale"`에 해당한다. 이 시험은 사유를 고정하지 않는다.

### `test_expired_or_missing_independent_check_denies_semantic_reuse` (행 302–307)
- 성질: 위임이 만료된 시각이거나 검사 판단이 없으면 위임 사례 재사용이 거부된다.
- 준비: `checked_replacement_case()`.
- 실행: `at='2100-01-01T00:00:00Z'`로 `authorize_review_replacement`. 적용 기록에서 `check` 판단을 지우고 다시.
- 단언: 두 결과 모두 `allowed`가 거짓이다.
- 대역: 없음.
- 비고: 위임 만료는 2099년이므로 2100년 시각에 `"delegation expired"`로 거부된다. 판단 삭제는 `"two independent judgments required"`에 해당한다.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈: 검토 교체와 복구의 엔진 경로는 `review_fixtures`를 쓰는 검토 계열 모듈이 본다. `test_governance`는 결정 종류 목록에 `delegation`이 들어 있음만 확인하고(`IntentImportTests.test_intent_input_exposes_actual_consumers_and_exact_source`), 위임 기록의 채택·적용은 이 모듈이 맡는다.
- 픽스처 의존: `research_fixtures.new_instance`, `record_fixtures.domain_governance`, `review_fixtures.ReviewFakeEngine`, `grant_replacement`.
- 이 모듈에만 있는 도우미: 모듈 함수 `replacement_case`, `checked_replacement_case`.
- 겹치거나 보완하는 시험: 판단 입력이 사례 해시라는 성질은 `test_delegation_uses_case_hash_not_full_context_hash`(도메인 함수)와 `test_actual_engine_delegation_control_to_independent_judgments_effect_and_receipt`(엔진 믹스인)가 두 층에서 본다. 위임 사례의 낡음은 저장소 왕복(원천 개정)과 도메인 상태(검토 주기 개정)의 두 경로로 본다.

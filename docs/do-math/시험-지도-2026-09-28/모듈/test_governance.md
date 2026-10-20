# test_governance

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_governance.py` (564행) |
| 클래스 / 테스트 | 5 / 41 |
| 시험 대상 제품 코드 | `do_math/governance.py`의 `initialize_governance`, `governance_view`, `validate_governance_state`, `apply_decision`, `authorize`, `grant_scope_reason`, `preserve_source`, `evaluate_additional_audit`, `import_input_source`, `validate_import_units`, `prepare_import`, `check_import`, `current_import`, `apply_import`, `apply_import_control`, `interpretation_schema`, `execution_lineage`, `validate_independent_execution`, `import_owner_handlers`, `register_import_owner`, `register_configuration_owner`, `GOVERNANCE_KINDS`; `do_math/governance_engine.py`의 `GovernanceEngineMixin._governance_context`, `governance_owner_handlers`, `_apply_governance_intent`, `_resume_import_question_waits`; `do_math/initialization_engine.py`의 `InitializationEngineMixin._queue_initial_intent`; `do_math/initialization.py`의 `initial_intent_evidence`, `grant_current`; `do_math/control_contracts.py`의 `validate_decision_shape`; `do_math/review_cycle.py`의 `validate_review_independence`; `do_math/submission.py`의 `_intent_import_issues`; `do_math/questions.py`의 `user_waits` |
| 사용하는 픽스처 모듈 | `research_fixtures`(`charter`, `governance_start`), `record_fixtures`(`checked_import`, `domain_governance`, `governance_import`, 함수 안에서 import하는 `applied_initial_intent`), `engine_fixtures`(함수 안에서 import하는 `governance_host`) |
| 격리 표지 | 없음 |
| 시작 상태 | 대부분 1단(`record_fixtures`의 사전 기록에 순수 도메인 함수). `IntentImportTests`의 세 시험은 `engine_fixtures.governance_host`의 `bare_engine` 엔진 객체에서 거버넌스 믹스인 메서드를 직접 부른다. 두 시험은 스킬 폴더의 실제 문서 파일을 읽는다 |

## 목적

모듈 docstring은 "거버넌스 기록: 헌장(charter)과 정책, 들여온 사용자 의도, 허가(grant), 승인, 등록된 주인"을 다루며 "이 시험들은 제공자의 능력이 아니라 사실과 권한 경계를 명세한다"고 밝힌다.

do-math의 거버넌스는 연구의 권위를 사용자의 보존된 원문에 묶는다. 헌장, 정책, 연구 맥락, 추가 감사는 사용자의 원천 문장(`governance_sources`)과 그 해시를 묶은 사용자 결정(`decisions`)으로만 채택되고, 저장된 내용이 승인된 제안과 달라지면 상태 검증이 실패한다. 사용자의 자연어 입력은 의도 가져오기(intent import)로 거버넌스에 들어온다. 작성 실행이 원문을 빈틈없는 의미 단위(`import_units`, 원문 좌표로 덮음)로 나누어 봉인하고(`prepare_import`), 독립된 검사 실행이 같은 봉인을 검사하며(`check_import`), 적용(`apply_import`, `apply_import_control`)은 검사가 승인이고 전제가 현재이며, 권한을 바꾸는 단위는 사용자가 그 정확한 변경을 승인했을 때만 이루어진다. 허가는 역할·대상·주체·실행 종류·목적·재사용 규칙으로 실행을 허락하고, `authorize`는 겹치는 허가 가운데 하나를 임의로 고르지 않는다.

이 모듈은 이 체계의 도메인 규칙을 가장 넓게 모은 곳이다. 다섯 클래스가 다루는 주제는 다음과 같다.

- `DomainGovernanceTests`: 헌장·정책·맥락·추가 감사의 채택, 초기화의 원문 결속, 가져오기의 좌표·검사·재작성·현재성·적용, 허가의 판정과 교체.
- `ImportApprovalTests`: 검사를 마친 가져오기에 대한 사용자의 나중 승인.
- `ExecutionLineageTests`: 실행 계보를 따라 독립성을 판정하는 규칙.
- `RegisteredOwnerTests`: 기록 종류마다 등록된 주인(owner)을 통한 적용.
- `IntentImportTests`: 초기 의도 가져오기와 질문, 그리고 문서 계약.

## 모듈 수준 요소

- 행 12: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리.
- 행 563–564: 직접 실행하면 `unittest.main(verbosity=2)`.

## 공통 픽스처

여러 시험이 `record_fixtures`의 세 도우미에서 시작한다.

- `domain_governance()`: 인스턴스 `I`. 사용자가 원천 `S`("User approves P")에서 결정 `D`로 헌장 `CH1`(목표 "Prove P")을 채택한 상태다.
- `governance_import()`: `(instance, runtime, source, output)`. 공개 입력 `IN`("A choice", 8자)을 의미 단위 `U` 하나(좌표 0–8, 주인 `charter`/`CH1`, 빈 페이로드)로 해석하고, 선택 질문 `Q`(비차단, 대상 `I`) 하나를 묻는 출력이다.
- `checked_import(kind='charter', handlers=None, payload=None)`: `(instance, runtime, bundle, request)`. 위 출력을 헌장 `CH2`(목표 "Prove Q", `CH1`을 대체)를 제안하도록 바꾸어 `E1`이 작성하고 `E2`가 승인 검사한 묶음과, 사용자가 나중에 그 정확한 변경을 승인하는 요청 `LATER`다. 런타임에는 검사 작업 `CHECK`가 `import_application_authority`로 대기한다.

## DomainGovernanceTests (행 24–277)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다. 모두 1단이다.

### `test_initialized_charter_is_single_authority_and_binds_approved_original` (행 25–33)
- 성질: 초기화된 인스턴스의 목표는 헌장 하나에만 있고 헌장은 승인 결정을 가리키며, 승인된 원문과 다른 원천으로는 초기화할 수 없다.
- 준비: `domain_governance()`. 원천 `S`의 사본을 떠 문장 끝에 `"!"`를 붙인다.
- 실행: `gov.governance_view(i)`, 이어서 바뀐 원천과 원래 결정 `D`, `charter()`로 `gov.initialize_governance(governance_start({"id": "I"}), ...)`.
- 단언: 인스턴스 최상위에 `"goal"`, `"policies"` 키가 없다. 보기의 `goal`이 `"Prove P"`, `CH1`의 `approval_ref`가 `"D"`다. 재초기화는 `ValueError`(유형만).
- 대역: 없음.

### `test_policy_coexists_and_only_explicit_supersession_retires_old_rule` (행 35–46)
- 성질: 정책은 여럿이 공존하고, 명시적 대체(`supersedes`)만 옛 규칙을 물린다. 구조화된 기록 없이 문장만으로 정책을 바꿀 수 없다.
- 준비: `domain_governance()`와 빈 런타임.
- 실행: 정책 `P1`, `P2`, `P3`(`P3`는 `P1`을 대체)를 차례로 `apply_decision`으로 채택한다. 이어서 `{"kind": "policy", "text": "replace all"}` 결정.
- 단언: 보기의 `policy_records` ID 집합이 `{"P2", "P3"}`, `P1`의 `status`가 `"superseded"`. 문장 결정은 `ValueError`(유형만). 제품에서 해당 경로는 `"governance decision requires a structured governance record"`다.
- 대역: 없음.

### `test_context_and_audit_require_owned_meaning_and_exact_verdict_mapping` (행 48–61)
- 성질: 연구 맥락과 추가 감사를 채택할 수 있고, 추가 감사의 판정 대응표는 지원되는 결정 값만 가질 수 있다.
- 준비: `domain_governance()`. 연구 맥락 `CX`(용어 `P`와 정의·경계), 추가 감사 `AU`(범위 `P`, 필수 입력 `CH1`, 감사자 `goal_audit`, 대응 `pass→satisfied`, `fail→not_satisfied`, `unknown→unresolved`).
- 실행: 둘을 `apply_decision`으로 채택한다. 이어서 감사 ID를 `AU2`로, `pass` 대응을 `"unsupported_assurance"`로 바꾸어 채택한다.
- 단언: 보기의 `additional_audits` 첫 행 ID가 `"AU"`. `AU2`는 `ValueError`(유형만).
- 대역: 없음.
- 비고: 이름의 "owned meaning"(맥락 용어의 주인)은 성공 경로 하나로만 드러나고, 맥락 용어의 거부 경로는 이 시험에 없다.

### `test_import_holes_and_self_check_are_rejected_and_questions_still_checked` (행 63–75)
- 성질: 원문 좌표에 빈틈이 있는 해석은 봉인되지 않고, 작성자 자신은 검사자가 될 수 없으며, 독립 검사를 거친 해석은 적용되고, 비차단 질문은 적용 뒤에도 작업을 막지 않는다.
- 준비: `governance_import()`. 단위 좌표의 끝을 7로 줄인 사본.
- 실행: 사본으로 `prepare_import` 시도, 원 출력으로 `prepare_import`, 실행 `E2`(봉인 해시를 가진 `intent_interpretation`)를 둔다. 승인 검사를 `E1`로 `check_import` 시도, `E2`로 `check_import`, `apply_import`, 연구 준비 작업에 `questions.user_waits`.
- 단언: 빈틈 사본은 `ValueError`. `E1` 검사는 `ValueError`. 적용 결과의 `status`가 `"applied"`. 대기가 거짓. 거부는 유형만 본다.
- 대역: 없음.
- 비고: 제품의 `check_import`는 실행 결속 검사보다 먼저 `validate_independent_execution(runtime, execution_id, [작성 실행 ID])`를 부른다. `E1`은 작성 실행 ID이면서 런타임 실행에도 없으므로 이 첫 검사가 `"independent checker execution required"`로 거부한다. 이름의 "self check"는 작성 실행 ID를 검사에 쓰는 경우를 가리킨다.

### `test_import_reauthor_requires_current_failed_parent_and_repair_coordinates` (행 77–88)
- 성질: 검사에서 수정 요구를 받은 가져오기의 재작성은 수리 기록(이전 해시, 바뀐 단위, 조치)을 요구하고, 수리 기록을 갖춘 새 묶음은 이전 묶음을 부모로 가리키며, 수정 요구를 받은 원래 묶음은 적용할 수 없다.
- 준비: `governance_import()`로 봉인한 묶음 `b`를 `E2`가 `revision_required`(발견 사항 "Question incomplete")로 검사한다.
- 실행: 수리 기록 없이 `previous_id=b["id"]`로 `prepare_import` 시도. 출력에 수리 기록(`changed_unit_ids=["U"]`)을 달고 질문 선택지를 하나 더한 뒤 다시. 끝으로 `apply_import(i, rt, b["id"])`.
- 단언: 첫 시도는 `ValueError`. 새 묶음의 `previous_id`가 `b`의 ID. 원 묶음 적용은 `ValueError`. 거부는 유형만.
- 대역: 없음.
- 비고: 제품의 `prepare_import`는 단위마다 단위 자체와 그 단위가 참조하는 질문 상세·질문 문장을 묶어 비교하므로(`unit_basis`), 질문 `Q`의 선택지를 늘리면 `Q`를 참조하는 `U`가 실제로 바뀐 단위가 된다. 그래서 `changed_unit_ids=["U"]`가 맞는 수리 좌표가 된다. 제품의 수리 좌표 검사(`"repair coordinates do not match actual changed units"`)는 `test_import_repair_cannot_claim_unchanged_units_were_changed`가 음성으로 본다.

### `test_import_currentness_binds_actual_structured_task_contract` (행 90–99)
- 성질: 해석이 인용한 과제의 계약 내용이 바뀌면, 개정 번호가 같아도 검사가 거부된다.
- 준비: `governance_import()`에 과제 `T`(개정 1, 질문 "Original task")를 두고 출력의 `used_sources`를 `['T']`로 한다. 작성 실행 `AUTHOR`로 봉인하고 검사 실행 `CHECK`를 둔다. 이어서 `T`의 질문만 바꾼다.
- 실행: `check_import(..., execution_id='CHECK')`.
- 단언: `ValueError`(유형만).
- 대역: 없음.
- 비고: 제품의 `check_import`는 `current_import`로 봉인 당시의 근거를 다시 계산하므로 `"import authority or affected targets changed"` 경로에 해당한다.

### `test_unapproved_or_stale_import_cannot_change_charter` (행 101–119)
- 성질: 헌장을 바꾸는 가져오기는 의미 검사만으로 적용되지 않고 사용자의 정확한 변경 승인이 필요하며, 적용은 반복해도 같은 결과를 내고, 권한 전제가 바뀌면 거부된다.
- 준비: `governance_import()`의 단위를 헌장 `CH2`(목표 "Prove Q", `CH1` 대체)를 제안하도록 바꾸고 질문을 없앤다. 봉인하고 `E2`가 승인 검사한다.
- 실행: 승인 없이 `apply_import`. 단위 `U`에 대한 사용자 승인(원천 ID·해시, 페이로드 해시)을 주어 `apply_import`. 같은 승인으로 결과 상태에 다시 적용. 결정 `D`의 `source_sha256`을 0으로 바꾼 사본으로 적용.
- 단언: 승인 없는 적용은 `ValueError`. 승인 적용 뒤 보기의 `goal`이 `"Prove Q"`, 사건 `status`가 `"applied"`. 재적용의 사건과 상태가 첫 적용과 같다. 낡은 사본의 적용은 `ValueError`. 거부는 유형만.
- 대역: 없음.
- 비고: 제품에서 승인 없는 적용은 `"semantic check is not user approval of the exact change"` 경로다.

### `test_explicit_once_grant_and_exclusions_use_existing_execution_ledger` (행 121–127)
- 성질: 일회성 허가는 실행 장부에 이미 쓰인 다른 사례가 있으면 다시 허락하지 않고, 제외 대상은 허락하지 않는다.
- 준비: 활성 지역 허가 `G`(역할·주체 `research_work`, `excluded_targets=["B"]`, `reuse="once"`)만 가진 인스턴스. 런타임에는 작업 `A1`을 이 허가로 실행한 `E`가 있다.
- 실행: 작업 `A2`(대상 `A`)를 그 런타임으로, 작업 `A1`(대상 `B`)을 빈 런타임으로 `gov.authorize`.
- 단언: 두 결과 모두 `allowed`가 거짓이다. 사유는 고정하지 않는다.
- 대역: 없음.

### `test_grant_decision_shape_names_no_resource_limit` (행 129–135)
- 성질: 허가 결정의 모양에는 자원 한도 필드가 없다.
- 준비: 주석은 "허가에 적힌 한도를 강제하는 예약 주인이 없고, 저장된 허가에도 그런 필드가 없다"고 적는다. 지역 허가 명세에 `resource_limits`를 `{}` 또는 `{"jobs": 1}`로 단다.
- 실행: `control_contracts.validate_decision_shape({"kind": "grant", "grant": ...})`.
- 단언: 두 경우 모두 `ValueError`이고 메시지가 `"change/grant: invalid additionalProperties"`에 맞는다.
- 대역: 없음.
- 비고: `subTest(limits=...)` 두 경우.

### `test_initialization_cannot_rebind_another_immutable_original` (행 137–142)
- 성질: 초기화는 인스턴스의 불변 원 입력과 다른 원천으로 거버넌스를 묶을 수 없다.
- 준비: 원천 `S`("P")와 그것에 맞는 승인, `charter()`. 인스턴스의 `lifecycle.immutable_input`은 다른 문장 `"Q"`다.
- 실행: `gov.initialize_governance(...)`.
- 단언: `ValueError`(유형만). 제품의 `"initial charter source differs from initialization immutable input"` 경로다.
- 대역: 없음.

### `test_stored_governance_content_must_still_match_approved_proposal` (행 144–146)
- 성질: 저장된 거버넌스 내용이 승인된 제안과 달라지면 상태 검증이 실패한다.
- 준비: `domain_governance()`에서 `CH1`의 목표를 `"Unapproved Q"`로 바꾼다.
- 실행: `gov.validate_governance_state(i)`.
- 단언: `ValueError`(유형만). 제품의 `"governance content differs from approved proposal"` 경로다.
- 대역: 없음.

### `test_import_check_must_resolve_a_real_execution_and_bound_input` (행 148–153)
- 성질: 가져오기 검사는 실제 실행이어야 하고 그 실행이 봉인된 입력에 묶여 있어야 한다.
- 준비: `governance_import()`로 봉인한 묶음.
- 실행: 런타임에 없는 실행 `FAKE`로 `check_import`.
- 단언: `ValueError`(유형만).
- 대역: 없음.
- 비고: `FAKE`는 런타임에 없으므로 제품의 첫 검사 `validate_independent_execution`이 `"independent checker execution required"`로 거부한다. 이름의 "bound input"에 해당하는 결속 검사(`"checker execution must bind exact preserved import input"`), 곧 실재하는 실행이 봉인 해시를 갖지 않은 경우는 이 시험이 만들지 않는다.

### `test_import_reapplication_is_idempotent` (행 155–164)
- 성질: 이미 적용한 가져오기를 다시 적용하면 같은 결과를 내고 질문 연결을 더 만들지 않는다.
- 준비: `governance_import()`를 봉인하고 `E2`로 승인 검사한다.
- 실행: `apply_import` 두 번.
- 단언: 두 번째 결과가 첫 결과와 같고, 질문 연결 수가 같다.
- 대역: 없음.

### `test_additional_audit_consumes_exact_required_inputs_and_mapping` (행 166–174)
- 성질: 추가 감사 판정은 승인된 필수 입력 전부의 현재 해시를 요구하고, 승인된 대응표로 결정을 매긴다. 판정을 매겨도 목표 상태는 바뀌지 않는다.
- 준비: `domain_governance()`에 추가 감사 `AU`(필수 입력 `CH1`)를 채택한다.
- 실행: 빈 `input_hashes`로 `gov.evaluate_additional_audit(i, "AU", "pass", assessor="goal_audit", ...)`, 이어서 `CH1`의 해시를 주어 다시.
- 단언: 첫 호출은 `ValueError`(유형만). 둘째 결과의 `decision`이 `"satisfied"`. 인스턴스의 `goal_status`가 `"unsolved"`.
- 대역: 없음.

### `test_grant_replacement_revokes_the_replaced_grant_and_stops_its_consumers` (행 176–185)
- 성질: 허가를 교체하면 옛 허가가 교체 사건으로 철회되고, 그 허가로 돌던 실행에 정지가 요청된다.
- 준비: `domain_governance()`에 지역 허가 `G`(만료 2099-01-01)를 채택하고, 이 허가로 `running`인 실행 `E`를 둔다.
- 실행: `G2`(만료 2099-01-02)를 `replaces=["G"]`로 채택하는 `apply_decision`.
- 단언: `G`의 `status`가 `"revoked"`, `revoked_by`가 교체 사건 ID, `E`의 `stop_requested`가 `"grant_revoked"`.
- 대역: 없음.

### `test_local_execution_kind_is_not_ignored` (행 187–190)
- 성질: 지역 허가의 `execution_kinds` 제한도 판정에 쓰인다.
- 준비: `execution_kinds=["machine"]`인 재사용 가능 지역 허가.
- 실행: `actor_kind="ai"`인 연구 작업으로 `gov.authorize`.
- 단언: `allowed`가 거짓.
- 대역: 없음.

### `test_import_repair_cannot_claim_unchanged_units_were_changed` (행 192–197)
- 성질: 재작성의 수리 기록은 실제로 바뀌지 않은 단위를 바뀌었다고 주장할 수 없다.
- 준비: `governance_import()`를 봉인하고 `revision_required`로 검사한다. 출력은 그대로 두고 수리 기록에 `changed_unit_ids=["U"]`를 적는다.
- 실행: `previous_id`로 `prepare_import`.
- 단언: `ValueError`(유형만). 제품의 `"repair coordinates do not match actual changed units"` 경로다.
- 대역: 없음.

### `test_initial_original_and_later_explicit_approval_remain_distinct` (행 199–207)
- 성질: 초기화에서 원 입력 원천과 그것을 승인한 원천은 따로 보존되고, 헌장은 원 입력을, 결정은 승인 원천을 가리킨다.
- 준비: 원 입력 원천 `ORIG`("Research P")와 승인 원천 `APPROVAL`. 승인 `D`는 승인 원천과 원 입력 원천을 모두 해시로 묶는다. 인스턴스의 불변 입력은 `ORIG`의 문장·해시·바이트 수다.
- 실행: `gov.initialize_governance(..., approval_source=approval_source)`, 이어서 `validate_governance_state`.
- 단언: `CH1`의 `source_ref`가 `"ORIG"`, 결정 `D`의 `source_ref`가 `"APPROVAL"`. 상태 검증이 예외 없이 끝난다.
- 대역: 없음.

### `test_resumed_author_session_is_not_an_independent_import_check` (행 209–213)
- 성질: 작성 실행을 이어받은(`continuation_of`) 실행은 독립 검사자가 아니다.
- 준비: `governance_import()`를 `E1`으로 봉인하고, 봉인 해시를 가진 `E2`에 `continuation_of="E1"`을 단다.
- 실행: `E2`로 `check_import`.
- 단언: `ValueError`(유형만). 제품의 `validate_independent_execution`이 `"checker resumes an author lineage"`로 거부하는 경로다.
- 대역: 없음.

### `test_intent_schema_covers_the_actual_check_and_repair_contract` (행 215–223)
- 성질: 해석 단계와 검사 단계의 출력 스키마는 실제 출력 모양을 받아들이고, 검사 결정에 정의되지 않은 값을 거부한다.
- 준비: `governance_import()`의 출력에 `summary`, `used_sources`를 더한다. 검사 출력(요약, 인용, 질문, 봉인 해시, `approved`, 범위 완결, 단위·질문 ID, 빈 발견).
- 실행: `jsonschema.validate`를 `interpretation_schema("interpret")`와 `interpretation_schema("check")`에 대해, 이어서 `decision="match"`인 검사 출력으로.
- 단언: 앞의 두 검증은 예외 없이 끝나고, 마지막은 `jsonschema.ValidationError`.
- 대역: 없음.
- 비고: 이름의 "repair contract"에 해당하는 수리 필드는 이 시험의 출력에 없다.

### `test_question_coordinates_must_reciprocate_unit_question_references` (행 225–230)
- 성질: 질문의 원천 단위 목록과 단위의 질문 참조는 서로 맞아야 한다.
- 준비: 단위 `U`의 좌표를 0–4로 줄이고 4–8을 덮는 단위 `V`(질문 참조 없음)를 더한다. 질문 `Q`의 `source_unit_ids`를 `["V"]`로 바꾼다. `U`는 여전히 `Q`를 참조한다.
- 실행: `prepare_import`.
- 단언: `ValueError`(유형만). 제품의 `"question coordinates contradict unit ownership"` 경로다.
- 대역: 없음.

### `test_advisory_question_does_not_leave_import_waiting_for_a_decision` (행 232–247)
- 성질: 비차단 질문만 있는 가져오기는 적용되고 질문은 열린 채 남으며, 차단 질문이 있으면 적용이 사용자 결정 대기로 멈추고 작업이 막힌다.
- 준비: 두 번 `governance_import()`에서 시작한다. 두 번째는 질문을 `blocks=True`로 바꾼다. 각각 봉인하고 `E2`로 승인 검사한다.
- 실행: 각각 `apply_import`, 두 번째 뒤 연구 준비 작업에 `user_waits`.
- 단언: 첫째 `status`가 `"applied"`이고 첫 질문 연결이 `"open"`. 둘째 `status`가 `"awaiting_decision"`이고 대기가 참.
- 대역: 없음.

### `test_overlapping_grants_are_not_selected_by_identifier_order` (행 249–259)
- 성질: 같은 작업에 맞는 허가가 둘 이상이면 ID 순서로 하나를 고르지 않고 거부한다.
- 준비: `governance_start`로 빈 거버넌스 가족을 가진 인스턴스와 사용자 원천. 재사용 가능 지역 허가 `A`, `B`(둘 다 `research_work`)를 채택한다.
- 실행: 작업 `AC`(`research_work`, `ai`)로 `authorize`.
- 단언: `allowed`가 거짓이고 `reason`이 정확히 `"ambiguous current grants"`.
- 대역: 없음.

### `test_import_schema_requires_coordinate_covered_meaning_units` (행 261–265)
- 성질: 해석 단계 스키마는 의미 단위의 필수 필드를 정확한 목록으로 요구한다.
- 준비: 없음.
- 실행: `interpretation_schema("interpret")`.
- 단언: `properties`에 `import_units`가 있고, 항목의 `required`가 `unit_id`, `source_range`, `interpretation`, `owner_kind`, `owner_ref`, `payload`, `decision_refs`, `question_refs` 순서의 목록과 같다.
- 대역: 없음.

### `test_once_http_operation_and_its_execution_share_logical_case` (행 267–277)
- 성질: 일회성 허가에서 외부 연산과 그 연산을 수행하는 실행은 같은 논리 사례로 세어지고, 다른 사례나 두 번째 연산은 허가를 다시 쓸 수 없다.
- 준비: 일회성 허가 `G`. 외부 연산 `OP`. 작업 `AC-OP`(`external_action`, 대상 `OP`)와 그 실행 `EX`.
- 실행: `gov.grant_scope_reason`을 네 번. 작업 `AC-OP`, 연산 자체를 가리키는 `{'id': 'OP', 'role': 'external_operation'}`, 다른 작업 `{'id': 'OTHER', 'case_id': 'OP'}`, 그리고 두 번째 연산 `SECOND`를 더한 뒤 작업 `AC-OP`.
- 단언: 앞의 둘은 `None`, 뒤의 둘은 `None`이 아니다.
- 대역: 없음.

## ImportApprovalTests (행 280–320)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다. 모두 `checked_import()`에서 시작하는 1단이다.

### `test_later_exact_approval_resumes_apply_without_rechecking` (행 281–290)
- 성질: 사용자의 나중 승인은 검사를 다시 하지 않고 적용을 이어가며, 대기 중인 검사 작업을 풀고, 같은 승인을 반복해도 결과가 같다.
- 준비: `checked_import()`. 봉인된 검사 기록의 사본.
- 실행: `gov.apply_import_control(i, rt, request)` 두 번.
- 단언: 보기의 `goal`이 `"Prove Q"`, 결과 `status`가 `"applied"`. 검사 기록이 사본과 같다. `waiting_actions`에 `CHECK`가 없다. 두 번째 호출의 세 반환값이 첫 번째와 같다.
- 대역: 없음.

### `test_later_approval_rejects_changed_seal_and_changed_premise` (행 292–298)
- 성질: 나중 승인은 검사 봉인 해시가 다르거나 권한 전제가 바뀌면 거부되고, 거부될 때 승인 원천을 남기지 않는다.
- 준비: `checked_import()`. 요청의 `check_sha256`을 `'wrong'`으로 바꾼 사본.
- 실행: 사본으로 `apply_import_control`. 결정 `D`의 `source_sha256`을 0으로 바꾸고 원 요청으로.
- 단언: 두 호출 모두 `ValueError`(유형만). 인스턴스의 `governance_sources`에 `LATER`가 없다.
- 대역: 없음.

### `test_import_application_receipt_binds_approval_and_rejects_tampering` (행 300–306)
- 성질: 적용 영수증은 승인 원천과 검사 봉인을 묶고, 영수증이 바뀌면 다시 적용할 때 거부된다.
- 준비: `checked_import()`를 `apply_import_control`로 적용한다.
- 실행: 영수증 확인 뒤 런타임 적용 기록의 `applied_units`를 `[]`로 바꾸고 다시 `apply_import_control`.
- 단언: 영수증의 `approvals['U']['source_ref']`가 `'LATER'`, `check_sha256`이 묶음의 검사 해시와 같다. 재적용은 `ValueError`(유형만). 제품의 `"sealed import application receipt changed"` 경로다.
- 대역: 없음.

### `test_changed_premise_reopens_checked_import_without_fabricated_text_change` (행 308–320)
- 성질: 전제가 바뀌지 않았으면 바뀐 단위 없는 재작성은 거부되고, 전제가 바뀌었으면 같은 문장으로 가져오기를 다시 열 수 있으며, 새 묶음은 검사 전 상태이고 옛 검사 기록은 보존된다.
- 준비: `checked_import()`. 묶음 출력 사본에 바뀐 단위 없는 수리 기록(`changed_unit_ids=[]`, 조치 "Re-evaluate the changed governing premise")을 단다.
- 실행: `previous_id`로 `prepare_import`. 결정 `D`의 `source_sha256`을 0으로 바꾸고 다시.
- 단언: 첫 호출은 `ValueError`(유형만. 제품 메시지 `"unchanged import resumes application; it does not need a new check"`). 다시 연 묶음의 `status`가 `'checking'`, `basis_sha256`이 원 묶음과 다르다. 원 묶음의 검사 기록이 그대로이고, 새 묶음에 `check` 키가 없다.
- 대역: 없음.

## ExecutionLineageTests (행 323–348)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다.

### `test_one_lineage_walk_keeps_each_consumers_judgment` (행 324–348)
- 성질: 실행 계보를 걷는 한 함수가 이어받기(`continuation_of`)와 문맥 원천(`context_origin`)을 따라가고, 소비자마다 다른 판단을 유지한다. 검사자 독립성은 이어받기만 따라가고, 검토 독립성은 문맥 원천도 따라간다. 순환과 해결되지 않는 계보는 거부된다.
- 준비: 실행 일곱 개. `EX-context`는 문맥 원천이 `EX-author`, `EX-check`는 `EX-context`를 이어받는다. `EX-loop-a`와 `EX-loop-b`는 서로를 이어받는다. `EX-lost`는 없는 `EX-missing`을 이어받고, `EX-orphan`은 없는 `EX-missing`을 문맥 원천으로 가진다.
- 실행: `governance.execution_lineage(runtime, 'EX-check')`, `execution_lineage(runtime, 'EX-lost')`, `validate_independent_execution`를 `EX-check`·`EX-loop-a`·`EX-lost`에 대해(작성자 `EX-author`), `review_cycle.validate_review_independence`를 `EX-check`(작성자를 제안 생산자로 가진 주기)와 `EX-orphan`(빈 제안)에 대해.
- 단언: `EX-check`의 계보 ID가 `['EX-check', 'EX-context', 'EX-author']`. `EX-lost` 계보의 마지막이 `('EX-missing', None)`. `EX-check`의 검사자 독립성은 예외 없이 통과한다. 검토 독립성은 `'original author context'`에 맞는 `ValueError`. `EX-loop-a`는 `'resumes an author lineage'`, `EX-lost`는 `'continuation lineage does not resolve'`, `EX-orphan`의 검토 독립성은 `'review context lineage does not resolve'`에 맞는 `ValueError`.
- 대역: 없음.
- 비고: 주석은 "검사자 독립성은 이어받기만 따른다. 검토는 문맥 원천도 따른다"고 적는다. `EX-loop-a`의 계보는 `EX-loop-b`를 거쳐 다시 `EX-loop-a`로 돌아온다. 제품의 `validate_independent_execution`은 `execution_lineage`에 `revisit_error="checker resumes an author lineage"`를 주므로, 작성자가 계보에 없어도 순환 자체가 같은 문구로 거부된다.

## RegisteredOwnerTests (행 351–391)

`unittest.TestCase`를 그대로 상속한다. 클래스 docstring은 "각 기록 종류에 등록된 주인을 통해 적용되는 거버넌스 변경"이다. 표지, 속성, 훅, 도우미가 없다.

### `test_configuration_adapter_uses_actual_config_validator` (행 354–365)
- 성질: 설정 가져오기의 주인은 제품의 실제 설정 검증기를 쓰므로, 잘못된 설정 패치는 봉인 단계에서 거부된다.
- 준비: `gov.import_owner_handlers()`에 `register_configuration_owner(handlers, apply=install)`로 설정 주인을 등록한다. `governance_import()`의 인스턴스 설정을 `DEFAULT_CONFIG` 사본으로 두고, 단위를 주인 `configuration`, 대상 `I`, 페이로드 `{'kind': 'configuration', 'config': {'call_timeout_seconds': 0}}`로 바꾼다.
- 실행: `prepare_import(..., owner_handlers=handlers)`.
- 단언: `ValueError`(유형만).
- 대역: 적용 콜백 `install`(호출되지 않는다).

### `test_registered_owner_applies_existing_knowledge_consumer` (행 367–378)
- 성질: `research_record`와 `evidence` 주인은 기존 지식 소비자로 적용되어 후보 지식을 만들고, 연구 계획을 큐에 넣으며, 형식 결과를 만들지 않는다.
- 준비: 새 `KN` ID를 가진 관찰 후보. 주인마다 `checked_import(kind=owner, payload={'kind': owner, 'record': candidate})`.
- 실행: `apply_import_control(i, rt, request)`.
- 단언: 후보 ID가 인스턴스 `knowledge`에 있고, 큐에 `research_plan` 작업이 있으며, 영수증의 `applied_units`가 `['U']`, 지식의 `formal_result_id`가 `None`이다.
- 대역: 없음.
- 비고: `subTest(owner=...)` 두 경우.

### `test_registered_configuration_reuses_owner_callback_and_currentness` (행 380–391)
- 성질: 등록된 주인의 적용 콜백과 현재성 함수가 가져오기에 쓰이므로, 주인이 보는 전제(설정)가 검토 중에 바뀌면 적용이 거부된다.
- 준비: `register_import_owner(handlers, 'configuration', apply=install, validate=..., basis=lambda i, rt, unit: i.get('config'))`. 이 주인으로 `checked_import`(페이로드 `{'model': 'approved'}`).
- 실행: `apply_import_control(..., owner_handlers=handlers)`. 이어서 원 인스턴스의 설정을 `{'model': 'changed during review'}`로 바꾸고 다시.
- 단언: 첫 결과의 `config['model']`이 `'approved'`. 둘째는 `ValueError`(유형만).
- 대역: 주인 콜백 셋(`install`, 검증 람다, 근거 람다).

## IntentImportTests (행 394–560)

`unittest.TestCase`를 그대로 상속한다. 클래스 docstring은 "거버넌스에 들여온 사용자 의도: 그 입력, 주인, 질문, 허가"다. 표지, 속성, 훅, 도우미가 없다.

### `test_intent_input_exposes_actual_consumers_and_exact_source` (행 397–409)
- 성질: 의도 해석 역할의 입력은 정확한 원문, 모든 가져오기 소비자, 현재 거버넌스 기록을 담고, 각 소비자의 페이로드 계약 문서는 그 주인 종류를 실제로 언급한다.
- 준비: `engine_fixtures.governance_host()`의 엔진. 이 픽스처는 `checked_import()` 상태를 `bare_engine`에 싣고 `_complete_initial_intent`와 `_activate_initialization`을 대역으로 바꾼다. 런타임 입력을 결합 문자가 든 `'é has two code points'`로 둔다.
- 실행: `host._governance_context({'role': 'intent_interpretation', 'target': 'UI-exact'}, {})`.
- 단언: 문맥의 `user_request['text']`와 `original_source['text']`가 같다. 소비자의 `owner_kind` 집합이 `gov.GOVERNANCE_KINDS`와 `{'grant', 'revoke', 'delegation', 'question_answer', 'task_scope'}`와 `host.governance_owner_handlers()`의 키를 합친 것과 같다. `governance_records`가 인스턴스 거버넌스 값 목록과 같다. 소비자마다 스킬 폴더 기준 `payload_contract['document']` 파일을 읽어 그 본문에 `owner_kind`가 들어 있다.
- 대역: `governance_host`가 붙인 두 `create_autospec` 대역.
- 비고: 실제 스킬 문서 파일을 읽는다. 결합 문자 입력은 원문 보존(정규화하지 않음)을 드러내는 입력이지만, 시험은 두 문맥 필드가 같은지만 비교한다.

### `test_initial_configuration_keeps_its_owner_through_completion` (행 411–443)
- 성질: 초기 입력에 대한 설정 가져오기는 설정 주인을 거쳐 적용되고, 초기 의도 증거는 그 가져오기의 작성 실행을 가리킨다.
- 준비: `record_fixtures.applied_initial_intent('Use this exact configuration')`로 공개 `initialize_state`에서 초기 해석이 적용된 인스턴스를 만든다. 설정을 `DEFAULT_CONFIG`(학술 검색 끔)로 둔다. 초기 입력 원천을 읽고, 인스턴스를 깊게 복사해 설정을 고치는 주인 `configure`를 등록한다. 원문 전체를 덮는 단위 `U`(주인 `configuration`, 페이로드 `{'effort': 'high'}`)의 출력을 만든다.
- 실행: 작성 실행 `EX-config-author`로 `prepare_import`, 검사 실행 `EX-config-check`로 `check_import`, 사용자 요청 `APPROVAL-config`로 `apply_import_control`, 이어서 `initial_intent_evidence(instance, runtime, owner_handlers=handlers)`.
- 단언: 인스턴스 설정의 `effort`가 `'high'`. 증거의 `interpretation_execution_id`가 `'EX-config-author'`.
- 대역: 주인 콜백 `configure`.

### `test_initial_advisory_question_does_not_become_a_blocking_gate` (행 445–466)
- 성질: 초기 입력의 재해석에 비차단 질문이 있어도 가져오기는 적용되고, 초기 의도 증거는 새 해석을 가리키며, 질문은 열린 채 남는다.
- 준비: `applied_initial_intent('Prove the stated goal')`의 원 가져오기 출력 사본에 비차단 질문 `Q-advice`(대상 인스턴스, 선택지 없음)를 더하고, 단위의 질문 참조를 맞춘다.
- 실행: 작성 실행 `EX-advice`로 `prepare_import`, `EX-advice-check`로 `check_import`, `apply_import`, `initial_intent_evidence`.
- 단언: 영수증 `status`가 `'applied'`. 증거의 `interpretation_execution_id`가 `'EX-advice'`. 마지막 질문 연결의 `status`가 `'open'`.
- 대역: 없음.

### `test_unrelated_progress_preserves_checked_import_but_relevant_changes_do_not` (행 468–477)
- 성질: 가져오기와 무관한 진행(다른 과제, 다른 결정)은 검사된 가져오기를 무효로 하지 않고, 관련 권한 전제의 변경은 무효로 한다.
- 준비: `checked_import()`에 무관한 과제 `TK-other`와 무관한 결정 `DC-other`를 더한다.
- 실행: `apply_import_control`. 이어서 결정 `D`의 `source_sha256`을 0으로 바꾸고 다시.
- 단언: 첫 영수증 `status`가 `'applied'`, 목표가 `'Prove Q'`. 둘째는 `ValueError`(유형만).
- 대역: 없음.

### `test_initial_blocking_question_waits_and_answer_reopens_original_once` (행 479–523)
- 성질: 초기 입력 해석에 차단 질문이 있으면 가져오기는 사용자 결정을 기다리고, 그동안 초기 해석 작업이 다시 큐에 들어가지 않으며, 사용자가 답하면 원 입력의 재해석이 이전 가져오기를 부모로 정확히 한 번 큐에 들어간다.
- 준비: `governance_host()`. 인스턴스 수명 주기를 초기화 중으로, 입력 `UI-original`("Which domain?")의 불변 입력과 채택 기록(초기 프로필 `P`, 초기 허가 `GR-initial`)으로 둔다. `GR-initial`은 `intent_interpretation` 역할이다. 큐와 대기 작업을 비운다. 해석 작업 `AC-interpret`과 그 끝난 실행 `AUTHOR`를 둔다. 출력은 차단 질문 `Q-domain`과 그것을 참조하는 단위 `U`다.
- 실행:
  1. `host._apply_governance_intent(action, output, 'AUTHOR')`로 묶음을 만들고 큐에 들어간 검사 작업을 꺼낸다. 끝난 검사 실행 `CHECK`를 두고 승인 검사를 `_apply_governance_intent`로 적용한다.
  2. `_capability_requirements`를 만족을 돌려주는 `create_autospec` 대역으로, `_lifecycle_now`를 실제 현재 시각을 돌려주는 대역으로 바꾼다. `do_math.initialization.grant_current`를 참으로 패치하고 `InitializationEngineMixin._queue_initial_intent(host)`를 세 번 부른다.
  3. 마지막 질문 연결을 `apply_decision`의 `question_answer`("Natural numbers")로 푼다. `host._resume_import_question_waits()`를 두 번 부른다.
- 단언: (1) 뒤 `waiting_actions`가 1개. (2) 뒤 큐가 `[]`. (3) 뒤 큐가 1개이고 그 작업의 `previous_import_id`가 묶음 ID, `target`이 `'UI-original'`이며, `waiting_actions`가 `{}`.
- 대역: `governance_host`의 대역, `_capability_requirements`와 `_lifecycle_now`의 `create_autospec` 대역, `grant_current`의 `patch`.
- 비고: (2)에서 제품의 `_queue_initial_intent`는 같은 입력에 `awaiting_decision` 상태의 가져오기가 있으면 큐에 넣지 않는다. (3)의 두 번째 재개 호출은 대기 항목이 이미 지워져 아무것도 더하지 않으므로, "once"가 확인된다.

### `test_question_references_are_stable_ids_at_both_boundaries` (행 525–540)
- 성질: 단위의 질문 참조는 수신 쪽(`validate_import_units`)과 생산 쪽(`submission._intent_import_issues`) 모두에서 안정된 질문 ID여야 하고, 출력 포인터 모양은 거부된다.
- 준비: `domain_governance()`, 원천 `SOURCE`("Which domain?"), 차단 질문 `Q-domain`과 그것을 참조하는 단위 `U`의 출력. 생산 쪽 문맥은 사용자 요청 문장, 원천, 인스턴스 ID다.
- 실행: `gov.validate_import_units(instance, {}, source, output)`, `_intent_import_issues(output, context)`. 이어서 단위의 질문 참조를 `'output/questions/0'`으로 바꾸고 다시 `_intent_import_issues`.
- 단언: 수신 검사는 예외 없이 끝나고, 생산 쪽 문제는 `[]`. 포인터 모양으로는 문제가 참(비어 있지 않음).
- 대역: 없음.
- 비고: 주석은 "생산자는 자기 고정 입력에 같은 검사를 돌린다"고 적는다.

### `test_interpretation_binds_referenced_source_alias` (행 542–549)
- 성질: 해석이 원천 별칭(`source:table.txt`)으로 인용한 원천의 내용이 바뀌면 가져오기가 현재가 아니게 된다.
- 준비: `governance_import()`의 인스턴스에 원천 `SO-table`(`table.txt`)을 두고 출력의 `used_sources`를 `['source:table.txt']`로 한다. `AUTHOR`로 봉인한다. 이어서 원천의 `sha256`을 바꾼다.
- 실행: `gov.current_import(instance, runtime, bundle['id'])`.
- 단언: `ValueError`이고 메시지가 `'targets changed'`에 맞는다. 제품 메시지는 `"import authority or affected targets changed"`다.
- 대역: 없음.

### `test_documented_research_grant_permits_formal_check` (행 551–560)
- 성질: 운영 문서 `references/초기화-운전.md`에 예시된 연구 허가 `GR-research-01`은 형식 검사(`formal_check`) 역할을 실제로 허락한다.
- 준비: 스킬 폴더의 `references/초기화-운전.md`를 읽어 `json` 코드 블록 가운데 `"id": "GR-research-01"`을 담은 블록의 `grant`를 꺼낸다. 주석은 "문서의 만료는 운영자가 승인된 기간으로 바꾸는 자리표시자"라고 적는다. 허가를 `status='active'`, 만료 `2026-09-23T00:00:00+00:00`으로 채운다.
- 실행: `gov.authorize({'grants': {...}}, {'role': 'formal_check'}, at='2026-09-22T00:00:00+00:00')`.
- 단언: 문서의 `expires_at`이 `'<'`로 시작한다(실패 메시지로 그 값). `allowed`가 참.
- 대역: 없음.
- 비고: 실제 스킬 문서 파일을 읽으므로, 문서의 예시가 제품 허가 규칙과 어긋나면 이 시험이 실패한다.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈: 거버넌스 제어를 엔진과 공개 경로에서 돌리는 것은 `test_governance_engine`, `test_initial_intent_connection`, `test_lifecycle_gates` 등이다. 허가 결정은 이 밖에 `test_external_operations`, `test_delegations`, `test_control_shapes`, `test_family_records`, `test_cli`, `test_engine` 등에서도 채택된다. 추가 감사의 소비는 `test_goal_audit`, 질문의 경로와 해결은 `test_questions`가 더 자세히 본다.
- 픽스처 의존: `record_fixtures`의 `domain_governance`, `governance_import`, `checked_import`, `applied_initial_intent`; `research_fixtures`의 `charter`, `governance_start`; `engine_fixtures.governance_host`.
- 이 모듈에만 있는 도우미: 없다. 시험 안에서 주인 콜백(`install`, `configure`)을 정의한다.
- 겹치거나 보완하는 시험: 가져오기의 재적용 멱등성은 `test_import_reapplication_is_idempotent`(검사만 받은 적용)와 `test_unapproved_or_stale_import_cannot_change_charter`(사용자 승인 적용), `test_later_exact_approval_resumes_apply_without_rechecking`(나중 승인 제어)이 세 경로에서 본다. 권한 전제(결정 `D`의 원천 해시)를 0으로 바꾸는 시험은 `DomainGovernanceTests`, `ImportApprovalTests`, `IntentImportTests`에 걸쳐 넷이다. 그 가운데 `test_unapproved_or_stale_import_cannot_change_charter`, `test_later_approval_rejects_changed_seal_and_changed_premise`, `test_unrelated_progress_preserves_checked_import_but_relevant_changes_do_not` 셋은 그 변경으로 적용이 거부됨을 보고, `test_changed_premise_reopens_checked_import_without_fabricated_text_change`는 같은 변경으로 가져오기를 다시 여는 경로를 본다.

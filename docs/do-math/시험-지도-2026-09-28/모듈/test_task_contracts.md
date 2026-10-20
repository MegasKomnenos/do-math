# test_task_contracts

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_task_contracts.py` (899행) |
| 클래스 / 테스트 | 9 / 61 |
| 시험 대상 제품 코드 | `do_math/task_contracts.py`의 `validate_task_contract`, `validate_item_dispositions`, `remaining_obligations`, `returned_task_ids`, `repetition_lineages`, `prepared_dependencies`, `REPEAT_LINEAGES`; `do_math/contracts.py`의 `TASK_CANDIDATE`, `task_candidate_record`; `do_math/planning.py`의 `task_ready`, `contract_review_current`, `review_basis_key`, `seal_contract_review`, `validate_plan_submission`, `ready_task_ids`, `evaluate_condition`, `capture_task_basis`, `action_read_ids`, `contract_hash`, `exhaustion_state`, `collect_due_events`, `record_due_events`, `schedule_reconsideration`, `governance_revisions`; `do_math/task_scope.py`의 `apply_task_assessments`, `assessment_current`, `refresh_task_assessments`, `validate_withdrawal_scope`; `do_math/revisions.py`의 `bind_repetition_bases`, `record_import_rework`, `record_execution_outcome`, `record_repetition`, `action_repetition_waits`, `repetition_hold`; `do_math/governance.py`의 `apply_decision`, `governance_view`; `do_math/execution_profiles.py`의 `profile_ref`, `build_profiles`, `resolve_profile`, `select_profile`; `do_math/decision_engine.py`의 `_validate_decision_acceptance`; `do_math/engine.py`의 `ResearchEngine._apply`; `do_math/submission.py`의 `_explicit_reference_fields`; `do_math/state_contract.py`의 `default_state_contract`; `do_math/repository.py`의 `ResearchRepository`; `do_math/knowledge.py`의 `capture_basis` |
| 사용하는 픽스처 모듈 | `research_fixtures`(`bare_engine`, `candidate`, `git_init`, `review_items`, 함수 안에서 import하는 `current_state`, `charter`), `record_fixtures`(`apply_assessment`, `approve_task`, `approved_task`, `domain_governance`, `task_contract`, `task_disposition`, `transfer_assessment`, `specialist_assessment`) |
| 격리 표지 | 없음 |
| 시작 상태 | 대부분 1단(`record_fixtures`의 사전 기록에 순수 함수). `TaskContractStorageTests`는 실제 Git 저장소(`git_init`과 `ResearchRepository`)에 설치된 스키마로 저장·재적재한다. 엔진 수신 경로를 보는 시험은 `bare_engine`으로 만든 실제 엔진 객체의 메서드를 직접 부른다 |

## 목적

모듈 docstring은 "과제 계약: 의무와 처분, 파생된 착수 가능성, 의존, 평가, 반복 계열"을 시험한다고 밝힌다.

과제 계약은 연구 준비가 제안하고 독립 계약 검토가 승인하는 작업 단위다. 계약에는 질문, 범위, 기대 산출, 진척 기준, 완료 의무(`completion_obligations`, 의무마다 ID·주장·판정자·요구 증거), 입력, 재사용, 의존, 발생 조건, 실행 프로필 참조, 권한 참조가 있다. 과제가 결과를 돌려주면 연구 계획이 평가(`task_assessments`)로 의무마다 처분(`fulfilled`, `transferred`, `waived`, `open`)이나 미결(`unresolved`)을 매기고, `task_scope.apply_task_assessments`가 이를 적용해 과제를 `completed`, `closed`, 대기 가운데 하나로 옮긴다. 의무의 이전(transfer)과 면제(waive)는 현재의 사용자 과제 범위 결정(`task_scope` 결정)이 있어야 한다. 착수 가능성은 저장하지 않고 매번 계약 검토·입력·권한·프로필·조건·대기에서 파생한다. 반복 계열(repetition lineage)은 같은 의미의 시도가 몇 번 되풀이되었는지 다섯 계열(`import_rework`, `selection_failure`, `exhaustion_empty`, `proposal_version`, `contract_revision`)로 세고, 설정 한도에 닿으면 사용자 보류를 건다.

아홉 클래스가 다루는 주제는 다음과 같다.

- `TaskContractReviewTests`: 계약 모양과 계약 검토의 현재성, 이전 의무의 완료 금지.
- `TaskContractStorageTests`: 설치된 스키마와 Git을 거친 저장·재적재와 엔진 수신.
- `TransferredContractRevisionTests`: 이전받은 의무의 보존.
- `TaskContractsTest`: 의무 처분의 규칙, 파생 착수 가능성, 계획 제출 검사, 조건.
- `TaskReadinessTests`: 착수 가능성을 막는 실제 전제 변경들, 연구 소진 판정.
- `AssessmentApplicationTests`: 평가 적용과 이전·면제·미결·전문 판정.
- `RepetitionLineageTests`: 반복 계열의 기록과 한도.
- `PreparationReceiptClassificationTests`: 연구 준비 영수증의 분류.
- `TaskDependencyTests`: 준비된 과제의 의존 보존.

## 모듈 수준 요소

- 행 6: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리.
- 행 898–899: 직접 실행하면 `unittest.main(verbosity=2)`.

## 공통 픽스처

- `task_contract()`: 계획된 계약 `TK-1`. 의무 `OB-1`(증거 `EV-1` 요구)과 `OB-2`(요구 증거 없음), 판정자는 모두 `task_assessor`다.
- `approved_task()`: `(task, instance, runtime)`. `task_contract`를 비형식 과제로 바꾸어 원천 `SO-1`을 입력으로 읽게 하고, 연구 작업 AI 프로필 하나와 지역 허가 `GR-1`(재사용 가능, 과제 `TK-1`만)을 둔 인스턴스 `IN-1`, 그리고 승인된 계약 검토(`approve_task`)를 갖는다.
- `transfer_assessment()`: `(instance, runtime, assessment)`. `approved_task`의 `TK-1`이 결과 `EV-1`을 돌려받아 대기 중이고, 수신 과제 `TK-2`(계획됨)가 있으며, 사용자 결정 `DC-1`이 `OB-2`를 `TK-2`로 이전한다. 평가는 `OB-1`을 `EV-1`로 충족하고 `OB-2`를 `DC-1` 권한으로 `TK-2`의 `OB-inherited`로 이전해 `TK-1`을 `closed`로 끝낸다. 의무의 판정자는 `research_plan`으로 바뀌어 있다. `apply_assessment(i, r, a)`는 이 평가를 계획 실행 `EX-plan`으로 `apply_task_assessments`에 넘긴다.
- `specialist_assessment(judge='identity_review')`: `transfer_assessment` 위에 검증된 정리(`knowledge_fixtures.verified_knowledge`)를 `TK-1`에 두고, 의무를 판정자 `judge`의 인증 의무 `OB-certification` 하나로 바꾼 뒤, 평가가 그 판정의 기록(신원 평가 ID나 형식 결과 ID)을 증거로 인용해 완료를 선언하게 한다.

## TaskContractReviewTests (행 19–145)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다. 모두 1단이다.

### `test_wire_profile_reference_remains_identical_in_stored_contract` (행 20–37)
- 성질: 제안 후보(wire)의 프로필 참조는 저장된 계약에서 그대로 유지되고, ID와 개정은 엔진이 붙이는 것이라 후보에 들어가면 스키마가 거부하며, ID 없는 후보는 저장 계약 검증을 통과하지 못한다.
- 준비: `approved_task()`의 인스턴스에서 첫 실행 프로필의 `profile_ref`를 `research_fixtures.candidate()`에 넣는다.
- 실행: `Draft202012Validator(contracts.TASK_CANDIDATE).validate(wire)`. 후보에서 `revises_task_id`를 빼고 `id='TK-wire'`, `revision=1`을 더해 `task_contracts.validate_task_contract`. 후보에 `id`나 `revision`을 더한 두 변형의 스키마 오류를 모은다. 원 후보로 `validate_task_contract`.
- 단언: 후보 검증과 저장 계약 검증이 예외 없이 끝나고, 저장 계약의 `profile_refs`가 후보와 같다. 두 변형은 스키마 오류가 하나 이상 있다. 원 후보의 저장 검증은 `ValueError`(유형만).
- 대역: 없음.
- 비고: 주석은 "할당은 wire 생산자가 아니라 엔진의 몫"이라고 적는다.

### `test_raw_governance_review_is_current_in_raw_and_projected_consumers` (행 39–50)
- 성질: 계약 검토는 거버넌스 보기의 목표·정책 개정을 기록하고, 원 인스턴스와 그 보기를 펼친 인스턴스 양쪽에서 현재이며 과제가 착수 가능하다. 인스턴스 최상위에는 개정 필드가 생기지 않는다.
- 준비: `approved_task()`를 `approve_task`로 한 번 더 승인하고 마지막 검토를 읽는다.
- 실행: `governance_view(instance)`와, 원 인스턴스·보기를 합친 인스턴스 두 형태에서 `contract_review_current`와 `task_ready`.
- 단언: 검토의 `goal_revision`·`policy_revision`이 보기와 같다. 두 형태 모두 검토가 유효하고 상태가 `'ready'`다. 인스턴스에 `goal_revision` 키가 없다.
- 대역: 없음.

### `test_transfer_cannot_complete_original_obligations` (행 52–60)
- 성질: 의무를 이전한 평가는 원 과제를 `completed`로 끝낼 수 없고, 이 규칙은 평가 적용과 계획 제출 검사 모두에서 같다.
- 준비: `transfer_assessment()`의 평가 결정을 `'completed'`로 바꾼다. 상태의 사본을 뜬다.
- 실행: `apply_assessment`, 이어서 `planning.validate_plan_submission({'dispositions': [], 'task_assessments': [assessment]}, tasks, [])`.
- 단언: 두 호출 모두 `ValueError`이고 메시지가 정규식 `'completed.*transferred'`에 맞는다. 적용 거부 뒤 상태가 사본과 같다.
- 대역: 없음.

### `test_review_ignores_flat_projection_and_rejects_real_governance_changes` (행 62–74)
- 성질: 계약 검토의 현재성은 인스턴스에 덧붙인 가짜 개정 필드를 무시하고, 실제 거버넌스 변경(새 정책 채택)에 반응한다.
- 준비: `approved_task()`의 마지막 검토 사본. 인스턴스에 `goal_revision=999`, `policy_revision='fake'`를 덧붙인 사본.
- 실행: 가짜 사본으로 `contract_review_current`. `review_basis_key`를 뜬다. 새 정책 `POL-new`를 `apply_decision`으로 채택하고 다시 `contract_review_current`와 `review_basis_key`.
- 단언: 가짜 사본에서 유효. 정책 채택 뒤 무효이고 검토 근거 키가 바뀐다.
- 대역: 없음.

### `test_actual_charter_replacement_invalidates_review_without_top_level_fields` (행 76–87)
- 성질: 실제 헌장 교체는 최상위 개정 필드 없이도 계약 검토를 무효로 하고 과제를 착수 불가로 만든다.
- 준비: `approved_task()`의 검토 사본. 헌장 `CH2`("Prove the stronger Q", 개정 2, `CH1` 대체).
- 실행: `apply_decision`으로 `CH2` 채택, `contract_review_current`, `task_ready`.
- 단언: 갱신된 인스턴스에 `goal_revision` 키가 없고, 검토가 무효이며, 상태가 `'not_ready'`다.
- 대역: 없음.

### `test_closed_transfer_never_satisfies_a_completion_dependency` (행 89–100)
- 성질: 의무를 이전해 `closed`로 끝난 과제는 그것을 완료 의존으로 가진 과제의 의존을 만족시키지 않는다.
- 준비: `transfer_assessment()`를 적용한다. `TK-2`를 복사해 `TK-1`에 의존하는 `TK-consumer`를 만들고, 허가 `GR-1`의 과제 목록에 더한 뒤 승인한다.
- 실행: `task_ready(consumer, ...)`.
- 단언: 상태가 `'not_ready'`이고 첫 오류에 `'blocked dependencies'`가 든다.
- 대역: 없음.

### `test_terminal_disposition_consistency_is_checked_by_shared_validator` (행 102–112)
- 성질: 종결 평가에 열린 의무가 섞이면 공유 검증기가 거부하고, 저장된 과제 상태와 평가 결정이 어긋나면 평가가 현재가 아니다.
- 준비: `transfer_assessment()`. 평가 사본의 첫 처분을 `open`으로 바꾼다.
- 실행: 사본으로 `task_contracts.validate_item_dispositions`. 원 평가를 적용한 뒤 `TK-1`의 `status`를 `'completed'`로 바꾸고 `task_scope.assessment_current`.
- 단언: 검증은 `ValueError`이고 메시지가 `'open obligations'`에 맞는다. `assessment_current`가 거짓.
- 대역: 없음.

### `test_profile_ref_shape_and_exact_resolution_are_both_required` (행 114–127)
- 성질: 프로필 참조는 모양(ID·정수 개정·SHA-256)이 맞고 중복이 없어야 하며, 모양이 맞아도 현재 프로필 판본에 정확히 해석되지 않으면 과제가 착수 불가다.
- 준비: `approved_task()`.
- 실행: 참조를 ID 문자열만, `revision=True`, `sha256='invalid'`로 바꾼 세 변형과 참조를 두 번 넣은 변형을 `validate_task_contract`. 이어서 `revision=2`와 `sha256='b'*64`인 두 변형을 과제로 저장·승인하고 `task_ready`.
- 단언: 모양 변형 넷은 모두 `ValueError`(유형만). 해석 불가 변형 둘은 `'not_ready'`.
- 대역: 없음.

### `test_repetition_basis_changes_with_actual_policy_not_flat_projection` (행 129–139)
- 성질: 반복 계열의 근거는 실제 정책 변경에 따라 달라진다.
- 준비: `approved_task()`의 인스턴스와 런타임. 연구 준비 작업 사전.
- 실행: `revisions.bind_repetition_bases`로 근거를 붙인다. 새 정책을 채택한 뒤 새 작업에 다시 붙인다.
- 단언: 두 작업의 `repetition_bases`가 다르다.
- 대역: 없음.
- 비고: 이름의 "not flat projection"에 해당하는 가짜 최상위 필드 대조는 이 시험에 없다.

### `test_common_reference_closure_does_not_split_grant_reuse_string` (행 141–145)
- 성질: 과제 근거의 공통 참조 폐포는 허가의 `reuse` 문자열을 글자로 쪼개 참조로 삼지 않고, 작업의 읽기 대상에는 프로필 ID가 들어간다.
- 준비: `approved_task()`.
- 실행: `planning.capture_task_basis`, `planning.action_read_ids({'target': 'TK-1'}, ...)`.
- 단언: 근거의 `common`에 `'r'`이 없다. 읽기 대상에 첫 프로필 참조의 ID가 있다.
- 대역: 없음.
- 비고: `'r'`은 `'reusable'`의 첫 글자로, 문자열을 반복 가능한 목록처럼 펼치는 결함을 겨냥한 단언이다.

## TaskContractStorageTests (행 148–321)

`unittest.TestCase`를 그대로 상속한다. 클래스 docstring은 "실제 설치 스키마와 Git. 사용자 결정과 AI 판단은 합성"이다. 표지와 속성이 없다.

- `setUp` (행 150–165): 접두 `tasks-audit1-`의 임시 폴더를 만들고 `addCleanup`으로 지운다. `git_init(root)`로 빈 Git 저장소를 만들고 `ResearchRepository(root, 'RI-01ARZ3NDEKTSV4RRFFQ69G5FAV')`를 둔다. `research_fixtures.current_state`로 수명 주기 검사를 통과하는 최소 상태를 만들되, 인스턴스에는 `domain_governance()`, `DEFAULT_CONFIG` 사본, `build_profiles(DEFAULT_CONFIG)`가 만든 실행 프로필을 싣고 런타임은 `ready`로 둔다. 수명 주기를 `active`로 바꾼다(주석: 저장 상태는 현재 수명 주기 관문을 통과해야 하고, 이 과제들은 활성 인스턴스에 속한다).
- `execution(identifier, role)` (행 167–181): 역할의 프로필을 찾아 활동을 열고, `create_execution`으로 실행을 만들어 역할을 달고 배정한 뒤 `starting`, `running`으로 전이시킨다.
- `candidate(identifier)` (행 183–196): 고급(`high`) 연구 작업 프로필과 권한 `GR-audit`을 단 후보를 `contracts.task_candidate_record`로 저장 계약으로 바꾸고, `revises_task_id`를 뺀 뒤(주석: 전송 대상이지 저장 계약의 권한이 아님) `planned`, 빈 결과·검토로 런타임에 둔다. `(task, wire)`를 돌려준다.
- `grant()` (행 198–201): 지역 허가 `GR-audit`(역할 `research_work`, 재사용 가능)을 원천 `S`로 채택한다.
- `review(identifier)` (행 203–208): 검토 실행 `EX-review-<ID>`를 만들고 `review_items(['S'])`로 승인 검토를 `seal_contract_review`로 봉인해 과제에 둔다.

### `test_candidate_review_profile_selection_and_governance_survive_git_reload` (행 210–249)
- 성질: 후보·검토·프로필 선택·거버넌스 개정은 Git 저장·재적재 뒤에도 유지되고, 잘못된 프로필 참조는 저장이 거부되며, 수신자의 결정 수용 검사는 저장된 거버넌스를 읽어 정책 변경 뒤 현재성 변경을 알린다.
- 준비: `setUp`, `grant()`, `candidate('TK-stored')`, `review(...)`. `self.store.initialize`로 첫 판을 만들고 적재한다.
- 실행:
  1. 저장된 과제로 `resolve_profile`, 작업 `AC-dispatch`로 `select_profile`, `task_ready(..., action=action, include_scheduling_waits=False)`.
  2. 런타임 사본의 프로필 개정을 1 올려 `save_with_state` 시도, 이어서 `load()`.
  3. `bare_engine(instance, runtime, store=self.store)`로 수신 엔진을 만들고, 입력 스냅숏·계약 해시·거버넌스 개정을 담은 영수증으로 `receiver._validate_decision_acceptance(review_action, output, receipt, {})`.
  4. 새 정책을 채택해 저장·적재하고 같은 호출을 되풀이한 뒤 `contract_review_current`.
- 단언: 저장된 `profile_refs`가 후보와 같다. 인스턴스에 `goal_revision`, `policy_revision` 키가 없고, 검토의 두 개정이 거버넌스 보기와 같다. `select_profile`의 ID가 해석된 프로필과 같고 상태가 `'ready'`. (2)는 `ValueError`이고 저장소 머리가 그대로다. (3)은 예외 없이 끝난다. (4)는 `input_basis.CurrentnessChanged`를 던지고, 검토가 무효다.
- 대역: 없음. 실제 Git 자식 프로세스와 설치된 상태 스키마를 쓴다.
- 비고: 주석은 "영수증 현재성은 검토·배정과 같은 저장된 거버넌스를 읽는다"고 적는다.

### `test_transfer_closes_without_completion_and_recipient_obligation_survives_reload` (행 251–286)
- 성질: 사용자 결정에 따른 의무 이전은 원 과제를 완료 없이 닫고, 수신 과제의 새 의무는 저장·재적재 뒤에도 남는다. 저장 검증과 평가 현재성 모두 이전을 완료로 바꿔 적는 것을 거부하고, 수신 과제의 완료 평가는 모든 의무를 덮어야 한다.
- 준비: `setUp`, `grant()`, 과제 `TK-source`와 `TK-target`, 계획 실행 `EX-plan`. `TK-source`를 결과를 가진 대기 상태로 두고, `apply_decision`으로 첫 의무를 `TK-target`으로 옮기는 `task_scope` 결정을 채택한다. 첫 판을 만들고 적재한다.
- 실행: 결정 권한을 인용한 `closed` 평가를 `task_scope.apply_task_assessments(..., execution_id='EX-plan', input_tasks=...)`로 적용하고 저장·적재한다. 이어서 원 과제의 상태와 평가 결정을 `completed`로 바꾼 사본으로 `save_with_state`를 시도하고, 그 사본의 `assessment_current`를 본다. 끝으로 수신 과제의 첫 의무만 처분한 `completed` 평가로 `validate_item_dispositions(..., require_complete=True)`.
- 단언: 원 과제 `status`가 `'closed'`, 수신 과제 `revision`이 2, 원 과제의 평가가 현재, 수신 과제 마지막 의무 ID가 `'OB-inherited'`. 변조 저장은 `'completed.*transferred'`에 맞는 `ValueError`이고, 변조 사본의 평가는 현재가 아니며, 머리가 그대로다. 마지막 검증은 `'every obligation'`에 맞는 `ValueError`.
- 대역: 없음. 실제 Git을 쓴다.
- 비고: 주석은 "저장 상태도 완료 소비자도 이전을 충족으로 바꿔 적을 수 없다"고 적는다.

### `test_actual_engine_candidate_and_review_receiver_round_trip` (행 288–321)
- 성질: 실제 엔진 수신 경로로 들어온 후보는 개정 1의 과제가 되고, 계약 검토가 적용되며, 저장·재적재 뒤에도 검토가 현재이고 과제가 착수 가능하다.
- 준비: `setUp`, `grant()`, 빈 지식·원천, 실행 `EX-author`(연구 준비)와 `EX-review`(계약 검토). `bare_engine(..., store=self.store)`를 만들고 `store.initialize`로 머리를 둔다. 고급 프로필과 `GR-audit`을 단 후보를 스키마로 검증한다. `engine._issued_input`을 `({'available_input_refs': [], 'supplied_record_ids': []}, None)`을 돌려주는 `create_autospec` 대역으로 바꾼다(주석: 이 수신 입력에 ID·개정이나 승인 근거를 끼워 넣지 않는다. 작성자의 발행 입력이 인용 가능한 과제 입력을 정한다).
- 실행: `engine._apply({'role': 'research_preparation'}, {'candidates': [wire]}, 'EX-author', owns_response=False)`, 이어서 `review_items(['S'])` 출력으로 `engine._apply({'role': 'task_contract_review', 'target': ...}, ..., 'EX-review', owns_response=False)`. 저장·적재한다.
- 단언: 적용 직후 과제 `revision`이 1이고 `profile_refs`가 후보와 같다. 재적재 뒤 마지막 검토가 유효하고 상태가 `'ready'`.
- 대역: `_issued_input`의 `create_autospec` 대역.

## TransferredContractRevisionTests (행 324–352)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다.

### `test_replacement_preserves_inherited_obligation_and_machine_provenance` (행 325–352)
- 성질: 이전받은 의무를 가진 과제를 교체하는 후보는 이전 의무 기록과 상속 의무를 그대로 보존해야 하고, 교체된 과제는 AI 철회 대상이 아니며, 상속 의무를 빼거나 바꾸는 후보는 거부되고 원 과제는 바뀌지 않는다.
- 준비: `transfer_assessment()`를 적용해 수신 과제 `TK-2`(상속 의무 포함)를 얻는다. `candidate('Revised recipient', revises='TK-2')`에 수신 과제의 의무를 복사하고 첫 의무의 주장만 바꾼다.
- 실행: `task_candidate_record(proposal, task_id='TK-2', previous=recipient)`. 그 결과를 `planned`로 두고 `validate_withdrawal_scope`. 이어서 마지막 의무를 빼거나 `id`·`claim`·`judges`·`evidence_required`를 바꾼 다섯 변형으로 `task_candidate_record`.
- 단언: 교체 기록의 `transferred_obligations`가 수신 과제와 같되 같은 객체가 아니다(`assertIsNot`). 마지막 의무가 같다. 철회 검사는 `'protected obligations'`에 맞는 `ValueError`. 다섯 변형은 모두 `'preserve transferred obligations'`에 맞는 `ValueError`이고, 매번 수신 과제가 사본과 같다.
- 대역: 없음.
- 비고: `subTest(field=...)` 다섯 경우. 이름의 "machine provenance"는 `transferred_obligations` 기록의 보존을 가리킨다.

## TaskContractsTest (행 355–454)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다. 모두 1단이다.

### `test_contract_has_stable_obligations_and_completion_requires_every_disposition` (행 356–364)
- 성질: 계약은 안정된 의무 ID를 갖고, 모든 의무에 처분이 있으면 남은 의무가 없다.
- 준비: `task_contract()`와, `OB-1`을 `EV-1`로 충족하고 `OB-2`를 `TK-2`의 `OB-9`로 이전(권한 `GR-1`)하는 평가.
- 실행: `validate_task_contract`, `validate_item_dispositions`, `remaining_obligations`.
- 단언: 두 검증이 예외 없이 끝나고 남은 의무가 `[]`.
- 대역: 없음.
- 비고: 이 순수 검증은 이전 권한 `GR-1`이 실제 사용자 결정인지 보지 않는다. 권한의 실재는 평가 적용(`AssessmentApplicationTests`)에서 본다.

### `test_unresolved_inspection_is_not_a_false_or_open_disposition` (행 366–372)
- 성질: 미결 항목은 거짓 처분이나 열린 처분이 아니므로 완결 요구 검증을 통과하지 못하고, 남은 의무로 센다.
- 준비: `OB-1`을 미결(누락 입력 `EV-1`, 다음 주인 `AC-recover`)로, `OB-2`를 충족으로 둔 평가.
- 실행: `validate_item_dispositions(..., require_complete=True)`, `remaining_obligations`.
- 단언: 검증은 `'unresolved'`에 맞는 `ValueError`. 남은 의무가 `["OB-1"]`.
- 대역: 없음.

### `test_waiver_and_transfer_need_authoritative_links` (행 374–386)
- 성질: 이름은 면제와 이전 처분에 권한 연결이 필요하다고 말한다. 실제로 단언되는 것은 세 입력이 `ValueError`로 거부된다는 사실뿐이다(비고 참조).
- 준비: `task_contract()`.
- 실행: 권한 없는 면제 행, `evidence_refs`와 대상 의무 ID가 모두 없는 이전 행을 각각 `OB-1` 하나만 처분한 평가로 검증하고, 이어서 권한 `GR-unrelated`를 단 `OB-1`의 면제 행 하나로 검증한다.
- 단언: 세 경우 모두 `ValueError`(유형만).
- 대역: 없음.
- 비고: `subTest(row=...)` 두 경우와 별도 단언 하나. 제품 경로에서 첫 행은 `"waived obligation needs authority_ref"`로 거부된다. 둘째 행은 대상 의무 ID 검사(`"transferred obligation needs authority and target obligation"`)에 닿기 전에 `_row_by_obligation`의 `"item disposition requires evidence_refs"`에서 거부된다. 셋째 입력은 `OB-2`에 처분이 없어 `"every obligation requires a disposition or unresolved inspection"`에서 거부된다. `validate_item_dispositions`는 `authority_ref`가 어떤 기록인지 확인하지 않으므로, 셋째 단언은 무관한 권한의 거부를 검사하지 않는다. 권한의 실재는 평가 적용(`AssessmentApplicationTests`)에서 본다.

### `test_readiness_is_derived_not_a_saved_task_state` (행 388–393)
- 성질: 착수 가능성은 파생 값이고, 판정이 런타임에 상태를 저장하지 않는다.
- 준비: `approved_task()`와 런타임 사본.
- 실행: `task_ready`.
- 단언: 상태가 `"ready"`이고 런타임이 사본과 같다.
- 대역: 없음.

### `test_repetition_lineages_keep_ai_repair_distinct_from_user_authority` (행 395–401)
- 성질: 다섯 반복 계열이 각각 세어지고, AI 소유 영수증은 AI 소유로 남는다.
- 준비: `REPEAT_LINEAGES`마다 과제 `TK-1`의 `revised`·`ai` 영수증 하나씩을 가진 이력.
- 실행: `task_contracts.repetition_lineages(runtime, "TK-1")`.
- 단언: 키 집합이 다섯 계열 이름과 같고, 모든 행의 `owner`가 `"ai"`, `count`가 1이다.
- 대역: 없음.

### `test_planning_routes_tasks_to_derived_readiness_and_item_plan_checks` (행 403–413)
- 성질: 계획은 파생 착수 가능성으로 준비된 과제를 고르고, 계획 제출 검사는 준비된 과제의 누락·예상 밖 과제·중복 처분을 한 메시지에 모두 보고한다.
- 준비: `approved_task()`.
- 실행: `task_ready`, `planning.ready_task_ids(runtime, instance)`, `TK-1`의 `not_selected` 처분으로 `validate_plan_submission`. 이어서 없는 `TK-absent`의 처분 두 개로 `validate_plan_submission`.
- 단언: 상태가 `"ready"`, 준비 목록이 `["TK-1"]`, 첫 제출 검사가 예외 없이 끝난다. 둘째는 `ValueError`이고 메시지에 `"missing=['TK-1']"`, `"unexpected=['TK-absent']"`, `"duplicate=['TK-absent']"`가 모두 들어 있다.
- 대역: 없음.

### `test_family_qualified_condition_does_not_read_a_same_id_from_another_family` (행 415–420)
- 성질: 가족을 지정한 조건은 같은 ID의 다른 가족 기록을 읽지 않고, 두 가족에 같은 ID가 있으면 판정 오류를 낸다.
- 준비: 지식 `X`와 과제 `X`가 함께 있는 상태.
- 실행: 지식 `X`의 수명 주기가 `active`인지 보는 조건 판정.
- 단언: 상태가 `"evaluation_error"`이고 첫 오류에 `'duplicate'`가 든다.
- 대역: 없음.
- 비고: `test_planning`의 `ConditionIndexTests.test_compound_condition_scans_one_population_and_rechecks_the_next_evaluation`에도 같은 ID 중복 오류 단언이 있다.

### `test_decision_and_artifact_conditions_preserve_effect_and_validity` (행 422–437)
- 성질: 결정 값 조건은 결정 원천이 바뀌면 착수 불가가 되고, 산출물 조건은 나중 스냅숏에서도 유효하며 바이트가 바뀌면 판정 오류가 된다.
- 준비: `approved_task()`의 인스턴스에 사용자 결정 `DC-1`(원천 `SO-1`, 해시 `'a'*64`, 변경 값 `continue`)을 둔다. 산출물 참조(스냅숏 `SN-1`, `runtime/artifacts/BA-1/proof.txt`, 바이트의 해시)와 읽기·검증 람다를 가진 판정 문맥.
- 실행: 결정 조건을 빈 런타임으로 판정, 결정의 원천 해시를 `'b'*64`로 바꾸고 런타임으로 판정. 산출물 조건을 판정, 문맥 스냅숏을 바꾸고 판정, 읽기가 `b'corrupt'`를 돌려주게 하고 판정.
- 단언: `"ready"`, `'not_ready'`, `'ready'`, `'ready'`, `'evaluation_error'`.
- 대역: 판정 문맥의 읽기·검증 람다.
- 비고: 문맥에 `git_dir`가 없다. `test_planning`의 `ArtifactConditionTests`가 저장소 유무에 따른 읽기·검증 캐시를 따로 본다.

### `test_prose_requirement_does_not_require_a_future_id_equal_to_the_description` (행 439–454)
- 성질: 의무의 산문 증거 요구(`evidence_requirements`)는 그 문장과 같은 ID의 증거를 요구하지 않지만, ID 목록 요구(`evidence_required`)는 그 ID를 증거로 요구한다. 산문 요구는 제출의 명시 참조 필드가 아니다.
- 준비: `candidate()`의 첫 의무에 산문 요구를 달고 `contracts.task_candidate_record(wire, task_id='TK-new')`로 계약을 만든 뒤 `revises_task_id`를 뺀다(주석: 엔진은 wire 전용 개정 포인터 없이 계약을 저장한다). 평가는 새로 만든 실행 `EX-newly-created`를 증거로 의무를 충족한다.
- 실행: `validate_item_dispositions`. 의무의 `evidence_required`를 `['KN-required-existing']`로 두고 다시. 증거에 그 ID를 더하고 다시. 끝으로 `submission._explicit_reference_fields(wire)`.
- 단언: 첫 검증 통과, 둘째는 `'required evidence'`에 맞는 `ValueError`, 셋째 통과. 명시 참조 필드 경로 가운데 `'evidence_requirements'`를 담은 것이 없다.
- 대역: 없음.

## TaskReadinessTests (행 457–538)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다. 모두 1단이다.

### `test_review_cannot_be_replaced_by_an_unsubstantiated_summary` (행 458–460)
- 성질: 항목별 검토가 없는 계약 검토는 승인으로 인정되지 않는다.
- 준비: `approved_task()`의 첫 검토에서 `item_reviews`를 비운다.
- 실행: `task_ready`.
- 단언: 상태가 `'ready'`가 아니다.
- 대역: 없음.

### `test_each_actual_premise_change_blocks_an_otherwise_ready_task` (행 462–474)
- 성질: 착수 가능한 과제는 실제 전제 가운데 어느 하나가 바뀌어도 착수 불가가 된다.
- 준비: 변형마다 새 `approved_task()`. 변형은 여덟 가지다. (1) 검토의 `inputs_current=False`. (2) 원천 목록 비우기. (3) 원천 해시 변경. (4) 허가 `GR-1` 철회. (5) 실행 프로필 비우기. (6) 현재 개정(1)에 대한 개정 요청 `revision_requested`. (7) `TK-1`을 막는 열린 사용자 차단 질문. (8) `TK-1`을 개정 대상으로 한 연구 준비 작업을 큐에 넣기.
- 실행: 변형 전후 `task_ready`.
- 단언: 변형 전은 `'ready'`, 변형 뒤는 `'not_ready'`.
- 대역: 없음.
- 비고: `subTest(mutate=...)` 여덟 경우.

### `test_missing_input_cannot_be_approved_into_existence` (행 476–478)
- 성질: 없는 입력은 검토 승인으로 존재하게 되지 않는다.
- 준비: `approved_task()`의 입력에 `SO-absent`를 더하고 다시 승인한다.
- 실행: `task_ready`.
- 단언: 첫 오류에 `'missing inputs'`가 든다.
- 대역: 없음.

### `test_profile_edition_and_fixed_trust_must_still_apply` (행 480–489)
- 성질: 배정할 작업의 프로필 판본과 과제에 고정된 신뢰 환경이 여전히 적용되어야 착수 가능하다.
- 준비: `approved_task()`를 형식 과제(`trust_environment_id='TE-1'`)로 바꾸고 활성 신뢰 환경 `TE-1`을 둔 뒤 다시 승인한다. 첫 프로필 참조를 가진 작업 `AC-work`.
- 실행: `task_ready(..., action=action)`, 작업의 프로필 개정을 1 올리고 다시, 활성 신뢰 환경을 `TE-2`로 바꾸고 `action` 없이 다시.
- 단언: `'ready'`, `'not_ready'`, `'not_ready'`.
- 대역: 없음.

### `test_split_knowledge_evidence_is_part_of_review_currentness` (행 491–499)
- 성질: 입력 지식이 참조하는 해설 기록의 내용은 계약 검토의 현재성에 들어간다.
- 준비: `approved_task()`에 지식 `KN-1`(해설 `XP-1`, 형식 결과 `FR-1`)과 그 두 기록을 두고, 입력에 `KN-1`을 더해 다시 승인한다.
- 실행: `task_ready`, 해설 `XP-1`의 항목을 바꾸고 다시.
- 단언: `'ready'`, `'not_ready'`.
- 대역: 없음.
- 비고: 지식 기록 자체는 바꾸지 않고, 지식이 가리키는 별도 해설 기록만 바꾼다.

### `test_external_wait_and_formal_work_are_not_research_exhaustion` (행 501–505)
- 성질: 외부 사건을 기다리는 과제나 큐의 형식 검사 작업이 있으면 연구가 소진된 것이 아니다.
- 준비: `approved_task()`의 과제를 외부 사건 대기로 둔다. 이어서 과제를 모두 지우고 큐에 형식 검사 작업을 둔다.
- 실행: 두 상태에서 `planning.exhaustion_state`.
- 단언: 두 번 모두 `exhausted`가 거짓.
- 대역: 없음.

### `test_empty_queue_is_not_exhaustion_when_work_is_running` (행 507–509)
- 성질: 큐가 비어도 실행 중인 연구 작업이 있으면 소진이 아니다.
- 준비: 과제·큐가 비고 실행 `EX-live`(`research_work`, `running`)만 있는 런타임.
- 실행: `exhaustion_state({'goal_status': 'unresolved'}, runtime)`.
- 단언: `exhausted`가 거짓.
- 대역: 없음.

### `test_stale_approval_and_absent_input` (행 511–516)
- 성질: 입력이 낡았다고 표시된 승인과 없는 입력을 가진 과제는 착수 가능하지 않다.
- 준비: `task_contract()`의 입력을 `['missing-input']`, 검토를 `inputs_current=False`인 승인 하나로 둔다.
- 실행: `task_ready(value, {}, {'tasks': {...}})`.
- 단언: 상태가 `'ready'`가 아니다.
- 대역: 없음.
- 비고: 두 결함을 함께 넣으므로 어느 쪽이 착수 불가를 만드는지는 가리지 않는다.

### `test_missing_returned_work_cannot_be_silently_omitted` (행 518–521)
- 성질: 결과를 돌려받아 대기 중인 과제는 계획 제출에서 빠질 수 없다.
- 준비: `task_contract()`를 결과 `EV-return`을 가진 `waiting`으로 둔다.
- 실행: 빈 처분·평가와 빈 준비 목록으로 `validate_plan_submission`.
- 단언: `ValueError`(유형만).
- 대역: 없음.
- 비고: 제품의 `validate_plan_submission`은 준비 목록과 `returned_task_ids`의 합집합을 비교 대상으로 삼는다.

### `test_open_obligation_does_not_require_evidence_of_fulfilment` (행 523–527)
- 성질: 열린 처분은 충족 증거를 요구하지 않는다.
- 준비: `task_contract()`와 두 의무를 모두 `open`, 빈 증거로 둔 평가.
- 실행: `validate_item_dispositions`.
- 단언: 명시 단언 없이, 예외 없이 끝나는 것으로 통과한다.
- 대역: 없음.

### `test_new_contract_fields_are_in_approval_digest` (행 529–533)
- 성질: 의무의 주장 문장은 계약 해시에 들어간다.
- 준비: `task_contract()`와 첫 의무의 주장만 바꾼 사본.
- 실행: 두 `contract_hash`.
- 단언: 두 해시가 다르다.
- 대역: 없음.
- 비고: 함수 안에서 `deepcopy`를 다시 import한다. `test_planning`의 `test_contract_hash_only_changes_for_contract_fields`가 계약 필드(질문)와 장부 필드를 대조한다.

### `test_artifact_metadata_is_not_evidence_of_readable_bytes` (행 535–538)
- 성질: 인스턴스에 적힌 산출물 메타데이터(`valid=True`)는 읽을 수 있는 바이트의 증거가 아니다.
- 준비: 산출물 참조를 문자열 `'AR-1'`로 준 조건과, `artifacts` 가족에 `AR-1`(유효 표지, 해시)을 둔 인스턴스.
- 실행: `evaluate_condition`.
- 단언: 상태가 `'evaluation_error'`.
- 대역: 없음.
- 비고: 제품의 `validate_condition`은 `artifact_ref`가 `snapshot`·`path`·`sha256`을 가진 사전이 아니면 `"artifact_ref requires snapshot, path, sha256"`로 거부한다. 이 입력은 그 모양 규칙에서 오류가 되며, 인스턴스의 메타데이터를 읽는 경로까지 가지 않는다.

## AssessmentApplicationTests (행 541–696)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다. 모두 1단이다.

### `test_transfer_binds_receiving_contract_and_blocks_incomplete_recipient_completion` (행 542–557)
- 성질: 의무 이전을 적용하면 입력은 바뀌지 않고, 원 과제는 닫히며, 수신 과제는 개정이 올라 검토가 비워지고 원 의무의 주장을 그대로 가진 상속 의무를 얻는다. 수신 과제의 완료 평가가 상속 의무를 처분하지 않으면 거부된다.
- 준비: `transfer_assessment()`와 런타임 사본.
- 실행: `apply_assessment`. 이어서 수신 과제에 결과 `EV-1`을 두고, `OB-1`·`OB-2`만 충족한 `completed` 평가를 적용한다.
- 단언: 입력 런타임이 사본과 같다. `TK-1`의 `status`가 `'closed'`. `TK-2`의 `revision`이 2, `reviews`가 `[]`, 마지막 의무 ID가 `'OB-inherited'`이고 주장이 원 `TK-1`의 둘째 의무 주장과 같다. 불완전 평가는 `'every obligation'`에 맞는 `ValueError`.
- 대역: 없음.

### `test_bare_unrelated_or_changed_authority_cannot_transfer` (행 559–569)
- 성질: 의무 이전은 현재의, 이 과제·수신자·계약 판본에 맞는 사용자 결정 없이는 적용되지 않고, 거부될 때 상태가 바뀌지 않는다.
- 준비: 변형마다 새 `transfer_assessment()`. 변형은 다섯 가지다. (1) 결정 모두 삭제. (2) 결정의 수신 과제를 `TK-other`로. (3) 결정의 계약 개정을 2로. (4) 결정의 원천 해시 변경. (5) 이전 처분의 권한을 허가 `GR-1`로.
- 실행: 변형 뒤 상태 사본을 뜨고 `apply_assessment`.
- 단언: 모두 `ValueError`(유형만)이고 상태가 사본과 같다.
- 대역: 없음.
- 비고: `subTest(mutation=...)` 다섯 경우. 제품의 `task_scope.validate_disposition_authority`가 이 권한 검사를 맡는다.

### `test_changed_decision_source_invalidates_scope_assessment_and_decision_condition` (행 571–586)
- 성질: 과제 범위 결정의 원천이 바뀌면, 그 결정에 기댄 평가는 현재가 아니게 되고 결정 값 조건도 착수 불가가 된다. 이미 닫힌 과제의 상태는 바뀌지 않는다.
- 준비: `transfer_assessment()`의 결정 `DC-1` 변경에 `value='continue'`를 더하고 평가를 적용한다. 결정 값 조건과, 과제 ID를 담은 판정 문맥.
- 실행: `assessment_current`, 조건 판정. 결정의 원천 해시를 바꾸고 다시 둘.
- 단언: 앞은 참과 `'ready'`, 뒤는 거짓과 `'not_ready'`. 원 과제 `status`가 `'closed'` 그대로다.
- 대역: 없음.

### `test_waiver_is_a_scope_decision_not_missing_evidence` (행 588–594)
- 성질: 면제는 증거 누락이 아니라 범위 결정이므로, 현재 사용자 결정의 면제 처분이 있으면 과제가 완료되고 다른 과제는 바뀌지 않는다.
- 준비: `transfer_assessment()`의 둘째 처분을 `DC-1` 권한의 `waived`로 바꾸고 결정을 `completed`로, 결정 `DC-1`의 처분을 `waive`로 바꾼다.
- 실행: `apply_assessment`.
- 단언: `TK-1`의 `status`가 `'completed'`, `TK-2`의 `revision`이 1 그대로다.
- 대역: 없음.

### `test_unresolved_inspection_preserves_missing_input_and_owner` (행 596–603)
- 성질: 미완 평가의 미결 항목은 누락 입력과 다음 주인을 과제 대기에 남기고, 과제를 결과 반환 목록에 다시 올리지 않는다.
- 준비: `transfer_assessment()`의 결정을 `incomplete`로, `OB-1`의 처분을 빼고 미결(누락 `EV-1`, 다음 주인 `research_work`)로 둔다.
- 실행: `apply_assessment`, `task_contracts.returned_task_ids`.
- 단언: `TK-1`의 `waiting['target_refs']`가 `['EV-1']`, `waiting['next_owner']`가 `'research_work'`, 반환 목록이 `[]`.
- 대역: 없음.

### `test_missing_assessment_input_arrival_reopens_assessment_without_new_work` (행 605–623)
- 성질: 미결 평가가 기다리던 입력이 도착하면 새 작업 없이 평가만 다시 열리고(과제가 결과 반환 목록에 오른다), 무관한 원천의 도착은 평가를 다시 열지 않으며, 과제의 결과는 그대로다. 누락 입력은 원천 ID, 파일 이름, `source:` 별칭, 원천 경로 어느 형태로 적어도 된다.
- 준비: 네 참조 형태(`SO-new`, `new.txt`, `source:new.txt`, `sources/new.txt`)마다 `transfer_assessment()`를 미완 평가로 바꾸어 그 참조를 누락 입력으로 둔 뒤 적용한다. 결과 사본을 뜬다.
- 실행: `returned_task_ids`. 무관한 원천 `SO-other`를 더하고 `task_scope.refresh_task_assessments`. 원천 `SO-new`(`new.txt`, `sources/new.txt`)를 더하고 다시.
- 단언: 처음 반환 목록이 거짓. 무관한 원천 뒤 새로 고침 결과가 `[]`이고 평가 `current`가 참. 새 원천 뒤 결과가 `['TK-1']`, 반환 목록이 `['TK-1']`, 결과가 사본과 같다.
- 대역: 없음.
- 비고: `subTest(reference=...)` 네 경우.

### `test_plan_covers_every_ready_and_returned_task_and_rejects_double_disposition` (행 625–633)
- 성질: 계획 제출은 준비된 과제와 결과가 돌아온 과제를 모두 다뤄야 하고, 한 과제에 처분을 두 번 주거나 처분과 평가를 함께 줄 수 없다.
- 준비: `transfer_assessment()`.
- 실행: 평가 `a` 하나만 담은 계획을 빈 준비 목록으로 검증한다. 이어서 네 경우를 검증한다. (1) 빈 계획, 준비 없음. (2) 평가만, 준비 `['TK-2']`. (3) `TK-2` 처분 두 개와 평가, 준비 `['TK-2']`. (4) `TK-1` 처분과 평가, 준비 `['TK-1']`.
- 단언: 첫 검증은 예외 없이 끝나고, 네 경우는 모두 `ValueError`(유형만).
- 대역: 없음.
- 비고: (1)은 결과가 돌아온 `TK-1`의 평가가 빠진 경우다. 네 경우는 `subTest` 없이 한 반복문에서 단언한다.

### `test_incomplete_open_work_is_available_for_a_later_continuation_plan` (행 635–642)
- 성질: 의무가 열린 채 미완으로 평가된 과제는 뒤의 계속 계획에서 다시 착수 가능하고, 연구 계획이 큐에 들어간다.
- 준비: `transfer_assessment()`의 `TK-1`을 평가 대기로 두고 다시 승인한다. 평가를 두 의무 모두 `open`인 `incomplete`로 바꾼다.
- 실행: `apply_assessment`, `task_ready`.
- 단언: 상태가 `'ready'`이고 큐에 `research_plan` 작업이 있다.
- 대역: 없음.

### `test_nonselection_revisit_is_an_actual_machine_event` (행 644–648)
- 성질: 선택되지 않은 과제의 재방문 시각은 실제 기계 사건이 된다.
- 준비: `approved_task()`의 과제에 계획 실행 `EX-plan`의 `not_selected` 처분을 달고 재방문 시각을 `2026-09-20T00:00:00Z`로 둔다.
- 실행: `planning.collect_due_events(..., '2026-09-20T00:00:01Z')`.
- 단언: 사건 가운데 종류가 `task_revisit_due`이고 대상이 `TK-1`인 것이 있다.
- 대역: 없음.

### `test_planner_can_aggregate_the_tasks_current_specialist_receipt` (행 650–655)
- 성질: 연구 계획은 과제에 대한 현재의 전문 판정 영수증(신원 검토나 형식 검사)을 모아 과제를 완료할 수 있다.
- 준비: 판정자 `identity_review`와 `formal_check`마다 `specialist_assessment(judge)`.
- 실행: `apply_assessment`.
- 단언: `TK-1`의 `status`가 `'completed'`.
- 대역: 없음.
- 비고: `subTest(judge=...)` 두 경우. 증거는 신원 검토면 신원 평가 ID, 형식 검사면 형식 결과 ID다.

### `test_foreign_stale_or_cycle_only_receipt_does_not_authorize_completion` (행 657–667)
- 성질: 다른 과제의 지식, 사용이 정지된 평가, 검토 주기 ID만의 인용, 바뀐 해설은 완료 근거가 되지 못한다.
- 준비: 변형마다 새 `specialist_assessment()`. (1) 지식의 `task_id`를 `TK-other`로. (2) 모든 평가 사용을 `suspended`로. (3) 증거를 검토 주기 ID `RC-fixture`로. (4) 해설 첫 항목 문장 변경.
- 실행: `apply_assessment`.
- 단언: 모두 `ValueError`(유형만).
- 대역: 없음.
- 비고: `subTest(mutation=...)` 네 경우.

### `test_unresolved_has_one_owner_and_can_be_reassessed_after_evidence_arrives` (행 669–681)
- 성질: 미결 의무는 주인이 하나이며 같은 의무에 처분을 겹칠 수 없고, 평가 입력 대기에 있던 과제는 뒤에 완료 평가를 받을 수 있다.
- 준비: `specialist_assessment()`. 미완 사본은 인증 의무를 미결(누락 `IA-needed`, 다음 주인 `identity_review`)로 둔다. 중복 사본은 여기에 같은 의무의 `open` 처분을 더한다.
- 실행: 미완 사본 적용, 중복 사본 적용, 이어서 미완 적용 결과 상태에 원 완료 평가를 적용.
- 단언: 미완 적용 뒤 대기 `kind`가 `'assessment_input'`. 중복은 `'undisposed'`에 맞는 `ValueError`. 마지막 적용 뒤 `status`가 `'completed'`.
- 대역: 없음.

### `test_goal_judgment_must_cover_this_tasks_result_and_remain_current` (행 683–696)
- 성질: 목표 감사 판정은 이 과제의 결과를 의존으로 덮고 현재일 때만 의무의 판정 근거가 된다.
- 준비: `specialist_assessment('goal_audit')`. 만족·범위 완결·현재인 목표 판정 `GJ-proof`(의존 `kid`, `knowledge.capture_basis`로 뜬 기록 근거, 현재 거버넌스 개정)를 두고, 평가 증거를 `GJ-proof`로 바꾼다.
- 실행: `apply_assessment`. 판정의 `current`를 거짓으로 바꾸고 다시.
- 단언: 앞은 `'completed'`, 뒤는 `ValueError`(유형만).
- 대역: 없음.

## RepetitionLineageTests (행 699–834)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다. 모두 1단이다.

### `test_real_receipts_produce_all_five_lineages_and_initial_versions` (행 700–719)
- 성질: 실제 실행 결과 영수증이 다섯 반복 계열 모두에 사건을 남기고, 제안 판본은 대체 계보의 뿌리로 세며, 빈 연구 결과가 없으면 소진 계열 수는 0이다.
- 준비: `approved_task()`의 과제 생산 실행을 `EX-prep`으로 두고, 지식 `KN-first`(생산 `EX-work`)와 그것을 대체한 `KN-next`(생산 `EX-revise`)를 둔다.
- 실행: 다섯 실행마다 끝난 실행 기록을 두고 `revisions.bind_repetition_bases`, `record_import_rework`, `record_execution_outcome`을 차례로 부른다. 실행은 연구 준비 `EX-prep`(수용), 연구 계획 `EX-plan`(거부), 의도 해석 재작성 `EX-import`(`previous_import_id='IM-1'`, 수용), 연구 작업 `EX-work`와 `EX-revise`(수용)다. 끝으로 `task_contracts.repetition_lineages(r)`.
- 단언: 모든 계열 행의 `events`가 참. `proposal_version`의 `by_lineage`가 `{'KN-first': 2}`. `contract_revision`의 `count`가 1, `exhaustion_empty`의 `count`가 0.
- 대역: 없음.

### `test_a_technical_retry_does_not_reset_the_configured_user_limit` (행 721–734)
- 성질: 설정 한도에 닿은 반복 보류는 운영 진단의 기술적 재시도 처분으로 풀리지 않고, 계열 수와 사용자 주인을 유지한다.
- 준비: `selection_failure_limit=1`. `record_repetition`으로 `selection_failure/population`에 `rejected` 하나를 기록한다. 재시도 작업 `AC-retry`(`EX-bad`를 잇고 같은 반복 근거).
- 실행: `action_repetition_waits`. 운영 검토 실행 `EX-op`과, `EX-bad`를 재시도하라는 적용된 운영 처분 `OD-1`을 둔 뒤 다시. `repetition_lineages`, `repetition_hold`.
- 단언: 두 번 모두 대기가 참, 계열 수가 1, 보류의 `owner`가 `'user'`.
- 대역: 없음.

### `test_new_request_ids_do_not_reset_semantic_lineage` (행 736–744)
- 성질: 작업 ID가 달라도 같은 의미의 계획이면 반복 근거가 같고, 원천이 바뀌면 근거가 달라진다.
- 준비: `approved_task()`. 연구 계획 작업 `AC-1`, `AC-2`.
- 실행: 둘에 `bind_repetition_bases`. 원천 해시를 바꾸고 `AC-3`에 붙인다.
- 단언: `AC-1`과 `AC-2`의 근거가 같고, `AC-1`과 `AC-3`은 다르다.
- 대역: 없음.

### `test_one_case_grant_is_available_before_reservation_but_not_after_other_use` (행 746–750)
- 성질: 일회성 허가는 쓰이기 전에는 과제를 착수 가능하게 하지만, 다른 작업이 그 허가를 쓴 뒤에는 그렇지 않다.
- 준비: `approved_task()`의 `GR-1`을 `once`로 바꾸고 다시 승인한다.
- 실행: `task_ready`. 다른 작업 `AC-other`로 `GR-1`을 쓴 끝난 실행 `EX-used`를 두고 다시.
- 단언: `'ready'`, `'not_ready'`.
- 대역: 없음.
- 비고: 클래스 주제(반복 계열)와 다른 허가 규칙 시험이 이 클래스에 있다.

### `test_one_regeneration_diagnosis_waits_for_a_new_basis_after_its_attempt` (행 752–769)
- 성질: 빈 연구 결과에 대한 재생성 진단(연구 계획)은 근거 하나에 한 번만 시도되고, 새 근거(원천 도착)가 생기면 새 진단이 다른 소진 사건으로 큐에 들어간다. 시도의 성공 여부와 무관하다.
- 준비: 결과 `output_accepted`와 `execution_incomplete`마다, 목표 미해결 인스턴스와 `exhaustion_empty/basis-one`의 `empty` 영수증 하나를 가진 활성 런타임.
- 실행: `planning.schedule_reconsideration(now=...00Z)`로 큐의 작업을 꺼낸다. 그 작업의 끝난 실행 `EX-plan`을 둔 뒤 `...01Z`에 다시. 원천 `SO-new`를 더하고 `...02Z`에 다시.
- 단언: 꺼낸 작업의 역할이 `'research_plan'`. 둘째 뒤 큐가 `[]`. 셋째 뒤 큐가 1개이고 그 `exhaustion_event_ref`가 꺼낸 작업과 다르다.
- 대역: 없음.
- 비고: `subTest(outcome=...)` 두 경우.

### `test_empty_regeneration_cannot_immediately_repeat_and_periodic_is_independent` (행 771–791)
- 성질: 연구 소진 사건은 관찰 시각과 빈 재생성 시각을 가진 저장 가능한 사건이고, 빈 결과 영수증 직후에는 연구 준비가 즉시 반복되지 않으며, 주기 재검토는 이와 독립으로 연구 준비를 만든다.
- 준비: `DEFAULT_CONFIG` 설정의 목표 미해결 인스턴스와 빈 활성 런타임.
- 실행: `schedule_reconsideration(now='...00Z')`로 소진 사건을 얻고 `default_state_contract().family('runtime', 'events').schema`로 검증한다. 큐를 비우고 `record_repetition`으로 `exhaustion_empty/basis-1`의 `empty` 영수증을 기록한 뒤 `...01Z`에 일정 계획. 다음 재검토 시각을 `...02Z`로 두고 `...03Z`에 `record_due_events`와 일정 계획.
- 단언: 소진 사건의 `observed_at`이 `'2026-09-20T00:00:00Z'`, `regenerate_after`가 `None`, 스키마 검증이 예외 없이 끝난다. `...01Z` 뒤 큐에 연구 준비가 없다. `...03Z` 뒤 큐에 연구 준비가 있다.
- 대역: 없음.

### `test_repetition_threshold_counts_validation_failures_once_per_execution` (행 793–806)
- 성질: 출력 검증 실패는 실행 하나에 한 번만 세어 반복 한도를 채우고, 한도는 그 근거에만 보류를 건다.
- 준비: `selection_failure_limit=2`. 반복 근거 `population-1`의 연구 계획 작업.
- 실행: 두 실행(`output_validation`, `output_schema` 실패)마다 `record_execution_outcome(..., accepted=False)`를 두 번씩 부르고 계열 수를 읽는다. 끝으로 두 근거의 보류를 본다.
- 단언: 계열 수가 실행마다 1, 2. `population-1`에는 보류가 있고 `population-2`에는 없다.
- 대역: 없음.

### `test_technical_plan_failures_do_not_count_and_acceptance_ends_the_sequence` (행 808–824)
- 성질: 현재성 변경, 출판 실패, 입력 실패 같은 기술적 실패는 선택 실패로 세지 않고, 출력 검증 실패는 세며, 수용된 결과는 연속을 끝낸다.
- 준비: 반복 근거 `population-1`의 연구 계획 작업.
- 실행: 세 기술 실패 실행, 출력 검증 실패 실행, 수용 실행마다 `record_execution_outcome`.
- 단언: 기술 실패 뒤 계열 수 0, 검증 실패 뒤 1, 수용 뒤 0.
- 대역: 없음.

### `test_repetition_receipt_produces_followup_once` (행 826–834)
- 성질: 같은 반복 영수증을 두 번 기록해도 이력 행과 후속 운영 검토 작업은 하나이고, 한도가 없으면 질문이 생기지 않는다.
- 준비: 빈 이력·큐·질문 연결.
- 실행: 같은 인자로 `record_repetition`을 두 번(`selection_failure/IN-1`, `EX-failed`, `rejected`).
- 단언: 이력 1행, 큐 1개, 큐의 역할이 `'operational_review'`, 질문 연결이 비었다.
- 대역: 없음.

## PreparationReceiptClassificationTests (행 836–866)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다.

### `test_rejected_preparation_does_not_count_as_an_empty_research_result` (행 837–855)
- 성질: 거부된 연구 준비(출력 검증 실패, 현재성 변경, 출력 계약 실패)는 빈 연구 결과로 세지 않아 영수증·후속·대기를 만들지 않고, 수용된 빈 준비는 세어 한도에 닿으면 보류를 건다.
- 준비: 실패 종류마다 `exhaustion_empty_limit=1` 인스턴스, 반복 근거 `same-input`의 연구 준비 작업, 실패 실행 `EX-failed`.
- 실행: 재생성 시각을 단 출력으로 `record_execution_outcome(..., accepted=False)`. 이어서 빈 준비 실행 `EX-empty`를 `accepted=True`로 기록.
- 단언: 거부 뒤 이력과 큐가 `[]`이고 대기가 거짓. 수용 뒤 `exhaustion_empty` 수가 1이고 보류가 있다.
- 대역: 없음.
- 비고: `subTest(failure=...)` 세 경우.

### `test_partially_accepted_contract_still_records_its_real_production` (행 857–866)
- 성질: 출력이 거부되었어도 그 실행이 실제로 만든 계약이 남아 있으면 영수증은 빈 결과가 아니라 계약 보존으로 기록되고, 계약 개정 계열이 센다.
- 준비: `approved_task()`의 과제 생산 실행을 `EX-partial`로 두고 그 실행을 둔다.
- 실행: 반복 근거 `same-input`의 연구 준비 작업으로 `record_execution_outcome(..., accepted=False)`.
- 단언: `exhaustion_empty` 영수증의 결과 목록이 `['contracts_preserved']`. `contract_revision` 수가 1.
- 대역: 없음.

## TaskDependencyTests (행 869–895)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다.

### `test_primary_and_extension_dependencies_are_preserved` (행 870–874)
- 성질: 준비된 과제의 의존은 후보의 의존과 확장 조건의 의존을 합치고, 확장이 의존을 생략해도 후보 의존을 지우지 않으며, 제목으로 적은 새 과제는 ID로 바뀐다.
- 준비: 의존 `TK-existing`을 가진 후보.
- 실행: `task_contracts.prepared_dependencies(candidate, {'observation_rules': []})`, `prepared_dependencies(candidate, {'dependencies': ['new task', 'TK-existing']}, {'new task': 'TK-new'})`.
- 단언: `['TK-existing']`, `['TK-existing', 'TK-new']`.
- 대역: 없음.

### `test_engine_preserves_primary_dependency_when_extension_only_sets_condition` (행 876–895)
- 성질: 엔진의 준비 출력 적용은 확장이 발생 조건만 줄 때도 후보의 의존을 보존하고, 의존을 발생 조건에 반영한다.
- 준비: `approved_task()`의 과제 `TK-1`을 선행 과제로 두고, 제목 `Followup` 후보에 그 프로필 참조와 의존 `TK-1`을 준다(주석: 작성자는 받은 작업 프로필을 묶는다, `research_fixtures.bind_candidates`). 끝난 준비 실행 `EX-prepare`의 확장에 `Followup`의 `always` 조건을 둔다. `bare_engine`의 `_record_output_questions`, `_evaluation_context`, `_issued_input`, `_governance`를 `create_autospec` 대역으로 바꾼다(`_governance`는 제품 `governance_view`를 부른다).
- 실행: `ResearchEngine._apply(host, {'role': 'research_preparation'}, {'candidates': [proposal]}, 'EX-prepare')`.
- 단언: 새 과제의 `dependencies`가 `['TK-1']`이고, `occurrence_condition['args'][1]['task_id']`가 `'TK-1'`이다.
- 대역: 네 메서드의 `create_autospec` 대역.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈: 착수 가능성과 조건은 `test_planning`이, 계약 검토 현재성과 결정 근거는 `test_decision_basis`가, 과제 철회는 `test_task_scope`가, 반복 보류 질문은 `test_questions`의 `RepetitionQuestionTests`가, 평가 근거의 관계 경유 판정은 `test_relation_dependencies`가 본다. 평가 적용의 엔진·목적 시나리오 경로는 `test_task_completion`, `test_model_assessment_flow` 등이 본다.
- 픽스처 의존: `record_fixtures`의 과제 계약 계열 도우미 전부(`task_contract`, `approved_task`, `approve_task`, `task_disposition`, `transfer_assessment`, `apply_assessment`, `specialist_assessment`, `domain_governance`); `research_fixtures`의 `bare_engine`, `candidate`, `git_init`, `review_items`, `current_state`, `charter`.
- 이 모듈에만 있는 도우미: `TaskContractStorageTests`의 `setUp`, `execution`, `candidate`, `grant`, `review`.
- 겹치거나 보완하는 시험: 이전을 완료로 바꿔 적는 것의 금지는 `test_transfer_cannot_complete_original_obligations`(평가 적용과 계획 제출)와 `test_transfer_closes_without_completion_and_recipient_obligation_survives_reload`(저장 검증)가 두 층에서 본다. 계약 해시의 범위는 이 모듈의 `test_new_contract_fields_are_in_approval_digest`와 `test_planning`의 `test_contract_hash_only_changes_for_contract_fields`가 나누어 본다. 같은 ID의 가족 중복 오류는 이 모듈과 `test_planning`에 각각 한 번씩 있다.

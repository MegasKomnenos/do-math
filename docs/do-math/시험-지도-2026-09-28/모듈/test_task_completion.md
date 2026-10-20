# test_task_completion

| 항목 | 값 |
|---|---|
| 조각 | `lifecycle` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_task_completion.py` (166행) |
| 클래스 / 테스트 | 3 / 10 |
| 시험 대상 제품 코드 | `do_math/task_scope.py`의 `apply_task_dispositions`(내부의 `_validate`, `validate_withdrawal_scope`), `validate_withdrawal_record`, `assessment_basis`, `assessment_current`, `apply_task_assessments`(내부의 `designated_judgment`); `do_math/planning.py`의 `contract_hash`; `do_math/repository.py`의 `exact_content_hash` |
| 사용하는 픽스처 모듈 | `record_fixtures`: `apply_assessment`, `completed_with_knowledge`, `specialist_assessment`(모듈 수준 import), `withdraw_prepared`, `withdrawable_task`, `transfer_assessment`(함수 안 import) |
| 격리 표지 | 없음 |
| 시작 상태 | 1단(순수 함수 직접 호출). 입력은 모두 `record_fixtures`가 만드는 사전 기록이다 |

## 목적

모듈 docstring은 "과제 완료, 이전(transfer), 철회(withdrawal)(`do_math.task_scope`)"를 시험한다고 밝힌다. 세 물음을 다룬다. 어떤 제출 증거가 완료 평가(completion assessment)를 현행으로 유지하는가. 평가가 의무를 다른 과제에 어떻게 넘기는가. 철회는 무엇을 보존하는가. docstring은 이 모두가 "기록 픽스처 위의 순수 함수"라고 적는다.

제품 좌표는 다음과 같다. `apply_task_dispositions`(`task_scope.py` 78행)는 연구 계획이 AI가 준비한 과제를 철회하는 경로다. 입력 스냅숏과 계약 해시를 대조하고(`_validate`), 철회 범위 규칙(`validate_withdrawal_scope`)을 거친 뒤 과제를 `closed`로 바꾸고 `scope_disposition`을 남긴다. `validate_withdrawal_record`(135행)는 그 기록이 "실제 미완료 평가를 보존하고 결코 충족으로 바꾸지 않는다"는 docstring을 검사한다. `assessment_current`(281행)는 저장된 평가의 계약 해시, 결과 해시, 증거 기반(`assessment_basis`)과 전문 판정 지원이 아직 맞는지 판정한다. `apply_task_assessments`(376행)는 평가 전체를 사본에 적용하며, 이전 받는 과제(recipient)의 의무까지 고친다.

## 모듈 수준 요소

- 행 12: `sys.path.insert(0, ...)`로 `scripts/` 폴더를 경로 맨 앞에 넣는 공통 머리.
- 행 13–15: `planning`, `task_scope`, `exact_content_hash`와 `record_fixtures`의 `apply_assessment`, `completed_with_knowledge`, `specialist_assessment`를 import한다.
- 행 165–166: 직접 실행하면 `unittest.main()`을 부른다.

## PartialWithdrawalTests (행 18–77)

`unittest.TestCase`를 그대로 상속하고 표지와 설정 훅이 없다. 도우미 메서드 하나가 "부분 결과가 있고 미완료 평가가 붙은 과제"를 만든다.

- `fixture()` (행 33–46): `record_fixtures.withdrawable_task()`의 인스턴스와 런타임을 받는다. 그 과제 `TK-AI`는 `task_contract()`에 기반한 개정 3, `planned` 상태의 준비 산출 과제이고 의무 `OB-1`, `OB-2`를 갖는다. 도우미는 과제를 `status='waiting'`, `results=[{'execution_id': 'EX-work', 'outcome': 'partial'}]`로 바꾼다. 그 위에 `decision='incomplete'`, 모든 의무를 `kind='open'`으로 둔 `item_dispositions`, `execution_id='EX-plan'`인 평가를 만든다. 평가에는 저장 시 수신자가 붙이는 필드(주석: `apply_task_assessments`)인 `contract_sha256=planning.contract_hash(task)`, `results_sha256=exact_content_hash(task['results'])`, `current=True`, `basis=task_scope.assessment_basis(...)`를 붙인다. 반환값은 `(instance, runtime, {task_id: 과제 사본})`이고 셋째 값이 입력 스냅숏이 된다.

### `test_current_unperformed_withdrawal_preserves_results_and_residual_scope` (행 19–31)
- 성질: 수행된 적 없는 과제의 철회 기록은 평가 해시가 없고, 결과 해시와 남은 의무 목록 가운데 하나라도 빠지면 철회 기록 검사에 걸린다.
- 준비: `withdrawable_task()`의 런타임과 스냅숏(결과 없음). 함수 안에서 `withdraw_prepared`, `withdrawable_task`를 import한다.
- 실행: `withdraw_prepared(runtime, snapshot)`(곧 `apply_task_dispositions`로 `TK-AI` 철회, 실행 `EX-plan`)를 부르고, 결과 과제에 `validate_withdrawal_record`를 부른다. 이어 `subTest`마다 `scope_disposition`에서 키 하나를 지운 사본으로 다시 검사한다.
- 단언: 원래 기록은 검사를 통과하고, `scope_disposition['assessment_sha256']`이 `None`이다. `results_sha256`을 지우거나 `remaining_obligation_ids`를 지우면 `ValueError`가 난다. 예외 유형만 보고 메시지는 고정하지 않는다.
- 대역: 없음.
- 비고: `subTest(missing=...)` 두 경우는 `results_sha256`, `remaining_obligation_ids`다. 제품에서는 각각 `'withdrawal results changed'`, `'withdrawal residual scope differs'`로 거부된다.

### `test_assessed_partial_work_closes_without_becoming_complete` (행 48–61)
- 성질: 현행 미완료 평가가 붙은 부분 결과 과제를 철회하면 과제는 `closed`가 되지만 완료되지 않고, 결과와 평가 이력과 남은 의무가 보존된다.
- 준비: `fixture()`.
- 실행: `apply_task_dispositions(instance, runtime, [{'task_id': 'TK-AI', 'disposition': 'withdraw', 'reason': ...}], execution_id='EX-next-plan', input_tasks=snapshot)`. 이어 결과 과제에 `validate_withdrawal_record`를 부르고, `remaining_obligation_ids`를 빈 목록으로 바꿔 다시 부른다.
- 단언: 상태가 `'closed'`다. `results`가 스냅숏의 결과와 같다. 과제에 `assessment` 키가 없고, `assessment_history[-1]`이 스냅숏의 평가와 같다. `scope_disposition['remaining_obligation_ids']`가 `['OB-1', 'OB-2']`다. 원래 기록은 검사를 통과하고, 남은 의무를 비운 기록은 `ValueError`로 거부된다(유형만 확인).
- 대역: 없음.

### `test_unassessed_new_results_and_protected_scope_are_not_withdrawable` (행 63–77)
- 성질: 평가되지 않은 새 결과, 현행이 아닌 평가, 사용자 요구 의무, 이전 받은 의무는 각각 자기 철회 규칙으로 철회를 막는다.
- 준비: `subTest`마다 새 `fixture()`. 런타임의 `TK-AI`를 한 가지씩 바꾼다. `new_result`는 결과 `{'execution_id': 'EX-new'}`를 덧붙이고, `stale_assessment`는 평가의 `current`를 `False`로 바꾸고, `user_required`와 `transferred_obligations`는 그 키를 `True`로 둔다. 입력 스냅숏은 바꾸지 않는다.
- 실행: `apply_task_dispositions(..., execution_id='EX-next', input_tasks=snapshot)`로 철회를 요청한다.
- 단언: 각 경우가 메시지 조각으로 고정된 `ValueError`를 낸다. `new_result`와 `stale_assessment`는 `'current item dispositions'`, `user_required`와 `transferred_obligations`는 `'protected obligations'`다.
- 대역: 없음.
- 비고: 원문 주석(64행)은 "각 변경은 저장 기록의 스키마가 아니라 자기 철회 규칙으로 거부된다"고 적는다. 메시지를 고정하므로 스냅숏 불일치 같은 다른 사유로 거부되면 실패한다. 제품에서 두 메시지는 `validate_withdrawal_scope`(`task_scope.py` 65·71행)가 낸다.

## CompletionBasisTests (행 80–138)

`unittest.TestCase`를 그대로 상속하고 표지·훅·도우미가 없다. 대부분의 시험이 `record_fixtures.completed_with_knowledge()`에서 시작한다. 이 픽스처는 `transfer_assessment()`의 평가를 `decision='completed'`로 바꾸고, 모든 의무를 `KN-proof`와 요구 증거로 충족시킨 뒤, 지식 `KN-proof`(형식 결과 `FR-proof`, 해설 `XP-proof`를 가리킨다)와 형식 결과 `FR-proof`(`formal_use='suspended'`, `publication_state='candidate'`)를 두고 `apply_assessment`로 평가를 적용한다. 반환은 `(instance, runtime)`이고 `TK-1`에 현행 평가가 붙어 있다.

### `test_submission_completion_survives_later_formal_verification_and_review_id` (행 81–89)
- 성질: 제출 뒤의 형식 검증 결과 기록과 검토 주기 ID 변경은 바뀌지 않은 제출 증거에 기반한 완료 평가를 무효로 만들지 않는다.
- 준비: `completed_with_knowledge()`.
- 실행: `assessment_current(task, instance, runtime)`를 부른 뒤, `FR-proof`에 `publication_state='accepted'`, `formal_use='active'`, `verification={'status': 'verified'}`를 넣고 `KN-proof`의 `review_cycle_id`를 `'RC-new'`로 바꿔 다시 부른다.
- 단언: 두 번 모두 `True`다. 둘째 단언의 메시지는 "Post-submission bookkeeping must not invalidate unchanged submitted evidence"다.
- 대역: 없음.
- 비고: 제품 `assessment_basis`는 지식 인용으로 닿은 형식 결과에서 `lean_code`, `declaration_names` 등 제출 수학 필드만 해시하고, 지식 기록에서 `review_cycle_id`를 뺀다(`task_scope.py` 269–276행).

### `test_actual_submitted_source_change_still_invalidates_completion` (행 91–94)
- 성질: 제출된 Lean 원문이 실제로 바뀌면 완료 평가는 현행이 아니다.
- 준비: `completed_with_knowledge()`.
- 실행: `FR-proof.lean_code`를 `'different source'`로 바꾸고 `assessment_current`를 부른다.
- 단언: `False`다.
- 대역: 없음.
- 비고: 바로 앞 시험과 짝을 이룬다. 앞 시험은 해시에서 빠지는 필드를, 이 시험은 해시에 남는 필드를 바꾼다.

### `test_relation_endpoint_contents_remain_part_of_completion_evidence` (행 96–106)
- 성질: 증거 지식이 관계 주장을 가지면 그 양 끝 지식의 해설 내용도 완료 증거 기반에 들어가, 끝점 내용이 바뀌면 평가가 현행이 아니게 된다.
- 준비: `completed_with_knowledge()` 위에 `KN-proof.relation_claim={'source': 'KN-source', 'target': 'KN-target'}`를 두고, `KN-source`, `KN-target` 지식과 해설 `XP-source`, `XP-target`(항목 텍스트는 각각 이름)을 추가한다. 평가의 `basis`를 `assessment_basis`로 다시 계산해 새 상태를 기준선으로 삼는다.
- 실행: `XP-source`의 첫 항목 텍스트를 `'different endpoint'`로 바꾸고 `assessment_current`를 부른다.
- 단언: `False`다.
- 대역: 없음.

### `test_new_identity_assessment_does_not_change_submission_content_basis` (행 108–112)
- 성질: 제출 뒤에 같은 형식 결과·해설에 대한 새 동일성 평가가 생겨도 제출 내용 기반은 바뀌지 않는다.
- 준비: `completed_with_knowledge()` 위에 동일성 평가 `IA-later`(`formal_result_id='FR-proof'`, `exposition_id='XP-proof'`, `decision='match'`)를 추가한다.
- 실행: `assessment_current`.
- 단언: `True`다.
- 대역: 없음.
- 비고: 제품 `assessment_basis`는 지식이 엄격 인용(strict) 대상일 때만 같은 형식 결과·해설의 동일성 평가를 기반에 더한다(`task_scope.py` 248–250행). 이 시험의 `KN-proof`는 평가가 직접 인용한 지식일 뿐 엄격 대상이 아니다.

### `test_specialist_support_still_requires_its_current_trust_and_use` (행 114–126)
- 성질: 전문 판정(형식 검사 또는 동일성 검토)으로 충족된 의무는 그 판정의 신뢰 환경과 사용 상태가 현행일 때만 완료로 유지된다.
- 준비: `subTest(judge=...)`마다 `specialist_assessment(judge)`. 이 픽스처는 `knowledge_fixtures.verified_knowledge()`의 검증된 지식을 `TK-1`에 묶고, 의무를 `OB-certification` 하나(판정자 `judge`)로 바꾸며, 증거로 형식 결과 ID(`formal_check`) 또는 동일성 평가 ID(`identity_review`)를 인용한 완료 평가를 만든다. 이어 `apply_assessment`로 적용한다.
- 실행: `assessment_current`를 부르고, `formal_check`이면 `active_trust_environment`를 `'TE-other'`로, `identity_review`이면 모든 `assessment_uses`의 `status`를 `'suspended'`로 바꿔 다시 부른다.
- 단언: 바꾸기 전 `True`, 바꾼 뒤 `False`다.
- 대역: 없음.
- 비고: `subTest` 두 경우는 `formal_check`, `identity_review`다.

### `test_specialist_dependency_use_is_not_reduced_to_submission_content` (행 128–138)
- 성질: 형식 검사로 충족된 의무에서는 형식 결과가 의존하는 지식의 사용 상태도 완료 증거에 들어가며, 제출 내용 해시로 축소되지 않는다.
- 준비: `specialist_assessment('formal_check')` 위에 형식 결과의 `dependencies=['KN-dependency']`를 두고, `KN-dependency` 지식과 형식 결과 `FR-dependency`(`formal_use='active'`)를 추가한다. 그다음 `apply_assessment`로 평가를 적용한다.
- 실행: `FR-dependency.formal_use`를 `'suspended'`로 바꾸고 `assessment_current`를 부른다.
- 단언: `False`다.
- 대역: 없음.
- 비고: 첫 시험과 대조된다. 지식 인용으로 닿은 형식 결과는 제출 필드만 해시하지만, 평가가 형식 결과를 직접 인용하면 그 결과는 엄격 대상이 되어 전체 기록과 의존 기록이 기반에 들어간다(`task_scope.py` 210–211행의 엄격 대상 규칙과 273–274행의 주석 "Explicit FR citations still bind the full record").

## TransferReferenceTests (행 141–162)

`unittest.TestCase`를 그대로 상속하고 표지·훅·도우미가 없다.

### `test_transfer_recipient_is_bound_to_the_fixed_input_population` (행 142–162)
- 성질: 의무 이전의 수신 과제는 평가 실행의 고정 입력에 들어 있어야 하고, 입력 이후 개정·종결되었거나 살아 있는 실행을 가지면 이전이 거부된다.
- 준비: 함수 안에서 `transfer_assessment`와 `apply_task_assessments`를 import한다. `transfer_assessment()`는 승인된 과제 `TK-1`(결과 `EV-1`, 상태 `waiting`)과 수신 과제 `TK-2`(계획 상태, 결과 없음), `OB-2`를 `TK-2`로 이전하는 사용자 결정 `DC-1`, 그리고 `OB-1` 충족·`OB-2` 이전(대상 의무 `OB-inherited`)의 평가를 만든다. 런타임 과제의 `deepcopy`를 `original`로 떠 둔다.
- 실행: 다섯 번 부른다. (1) 원 런타임과 `input_tasks=original`로 `apply_task_assessments`. (2)–(4) 런타임 사본을 한 가지씩 바꾼 뒤 같은 입력으로 부른다. 바꾸는 것은 `TK-2.revision=2`, `TK-2.status='closed'`, 그리고 `TK-2`를 대상으로 하는 `running` 실행 `EX-peer` 추가다. (5) 원 런타임에 `input_tasks={'TK-1': original['TK-1']}`(수신 과제가 빠진 입력)로 부른다.
- 단언: (1)의 결과에서 `TK-2`의 마지막 `completion_obligations` 항목 ID가 `'OB-inherited'`다. (2)–(4)는 `ValueError`를 낸다(유형만 확인). (5)는 메시지 조각 `'recipient'`로 고정된 `ValueError`를 낸다.
- 대역: 없음.
- 비고: 원문 주석(143–144행)은 "계획의 고정 입력은 준비된 모집단 밖의 수신 과제를 포함해 모든 현행 과제를 담으므로(`context_store.prepare_role_input`), 수신 과제는 그 입력에 묶인다"고 적는다. (2)의 개정 변경은 계약 해시를 바꿔 `'transfer recipient must be bound to the current input'`에, (3)은 `'transfer requires a distinct unfinished recipient ...'`에, (4)는 `'transfer recipient has a live execution'`에 걸린다. 다만 시험은 이 세 메시지를 구분하지 않는다.

## 관계

- 같은 제품 기능의 다른 층: `test_task_scope`(foundation 조각, docstring "AI가 준비한 과제의 자율 철회 회귀 검사")가 철회를 따로 다룬다. `assessment_current`는 `test_review_engine`, `test_task_contracts`에서도, `apply_task_assessments`는 `test_academic`, `test_academic_engine`, `test_research_recovery`, `test_task_contracts`에서도 쓰인다. `apply_task_dispositions`는 `test_design_walkthroughs`에도 나온다. `validate_withdrawal_record`를 부르는 시험 모듈은 이 모듈 하나다.
- 픽스처 의존: `record_fixtures`의 과제 계약 무리(`task_contract` → `approved_task` → `transfer_assessment` → `completed_with_knowledge`/`specialist_assessment`, 그리고 `withdrawable_task`/`withdraw_prepared`)에 전부 기대며, `specialist_assessment`를 거쳐 `knowledge_fixtures.verified_knowledge`에도 간접 의존한다.
- 이 모듈에만 있는 도우미: `PartialWithdrawalTests.fixture`(현행 미완료 평가가 붙은 부분 결과 과제).
- 겹침과 보완: `CompletionBasisTests`의 여섯 시험은 `assessment_basis`의 포함·제외 규칙을 짝으로 찌른다. 해시에서 빠지는 것(검증 결과·검토 주기 ID, 새 동일성 평가)과 남는 것(Lean 원문, 관계 끝점 해설, 전문 판정의 신뢰·사용 상태, 직접 인용한 형식 결과의 의존)이 한 모듈 안에서 대조된다.

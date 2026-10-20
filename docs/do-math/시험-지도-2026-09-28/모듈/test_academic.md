# test_academic

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_academic.py` (309행) |
| 클래스 / 테스트 | 3 / 17 |
| 시험 대상 제품 코드 | `do_math/academic.py`의 `academic_status`, `assess`, `current_requirements`, `effect_receipts`, `record_resolution`, `requirement_record`, `solution_basis`, `unresolved_rejections`, `external_prerequisite`, `bind_external_prerequisite`, 간접으로 `current_solution_basis`, `criterion_obligations`; `do_math/academic_engine.py`의 `AcademicEngineMixin._ensure_academic_followup`, `_record_academic_assessment`, `_academic_status`, `_solution_basis`; `do_math/planning_engine.py`의 `_finish_assessment_preparation`; `do_math/engine.py`의 `ResearchEngine._apply_plan`, `_remove_action`; `do_math/task_scope.py`의 `apply_task_assessments`; `do_math/task_contracts.py`의 `validate_task_contract`; `do_math/planning.py`의 `seal_contract_review`, `task_ready`, `ready_task_ids`, `contract_hash`; `do_math/governance.py`의 `apply_decision`(`task_scope`, `charter`); `do_math/external.py`의 `prepare_operation`; `do_math/execution_profiles.py`의 `build_profiles`; `do_math/knowledge.py`의 `capture_basis` |
| 사용하는 픽스처 모듈 | `record_fixtures`(`domain_governance`), `research_fixtures`(`approved_governance`, `bare_engine`, `charter`, `disposition`, `review_items`, 함수 안에서 import하는 `prepared_rule_conditions`) |
| 격리 표지 | 없음 |
| 시작 상태 | `Tests`와 `AcademicGovernanceTests`의 대부분은 1단(사전 상태에 순수 함수). `AcademicConsumerTests`와 `test_academic_basis_rejects_a_stale_judgment_dependency`는 `bare_engine`으로 만든 실제 엔진 객체에 사전 상태를 싣고 학술 믹스인 메서드를 직접 부른다 |

## 목적

이 모듈에는 docstring이 없다. 시험들이 가리키는 계약은 학술 요건(academic requirement)이다. 헌장은 수학적 해결 뒤에 따로 만족시켜야 할 학술 요건(예: 원고 준비)을 담을 수 있다. 요건은 ID, 범위, 판정자(`research_plan`), 기준 목록(`criteria`), 선택적 필수 입력과 외부 효과를 가진다. 목표가 `mathematically_solved`가 되면 엔진의 `_ensure_academic_followup`이 요건마다 과제 계약 하나를 만들고, 기준 하나를 완료 의무 하나로 옮긴다(`criterion_obligations`). 이 과제가 일반 과제처럼 검토·배정·작업·평가를 거치고, 적용된 과제 평가를 `_record_academic_assessment`가 학술 평가로 기록한다. `academic_status`는 현재 해결 근거(`solution_basis`)와 현재 요건 해시에 맞는 만족 평가, 필요한 외부 효과 영수증, 미해결 외부 거절 여부를 모아 학술 상태(`not_applicable`, `pending`, `active`, `externally_rejected`, `completed` 등)를 낸다.

세 클래스가 다루는 주제는 다음과 같다.

- `Tests`: 요건·평가·거절 해결·외부 효과 영수증의 순수 규칙.
- `AcademicConsumerTests`: 학술 요건을 과제로 만드는 생산자와, 그것을 소비하는 과제 체계(검토, 착수, 계획, 평가)의 실제 연결.
- `AcademicGovernanceTests`: 거절 해결의 증거 현재성, 외부 요청의 해결 근거 결속, 목표 판정 의존의 현재성.

## 모듈 수준 요소

- 행 7: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리.
- 행 308–309: 직접 실행하면 `unittest.main()`.

## Tests (행 16–80)

`unittest.TestCase`를 그대로 상속한다. 표지와 속성이 없다.

- `setUp` (행 17–23): 요건 `paper`(범위 `solution`, 기준 `['draft']`, 판정자 `research_plan`)를 `self.requirement`로 둔다. 인스턴스는 `goal_status='mathematically_solved'`이고 활성 헌장 `CH`(개정 1, 목표 `P`, 학술 요건 `[paper]`)를 가진다. `solution_basis('goal', [{'id': 'K', 'value': 1}])`를 `self.basis`로, 빈 과제·학술 평가·외부 거절을 가진 런타임을 둔다.

### `test_requirements_follow_the_charter_edition` (행 25–30)
- 성질: 학술 요건은 현재 헌장 판본을 따르므로, 헌장 개정과 기준이 바뀌면 요건 해시가 바뀐다. 평가가 없으면 상태는 `pending`이다.
- 준비: `setUp`. 헌장 개정을 2로, 기준을 `['publish']`로 바꾼 사본.
- 실행: `academic_status`, 두 인스턴스의 `current_requirements`.
- 단언: 상태가 `'pending'`. 두 요건 해시가 다르다.
- 대역: 없음.

### `test_assessment_covers_exact_criteria_but_does_not_replace_task_evidence` (행 32–40)
- 성질: 학술 평가는 요건의 기준을 정확히 덮어야 하고, 평가 기록 하나만으로는 학술 상태가 완료되지 않는다.
- 준비: `setUp`과 현재 요건.
- 실행: 기준 `draft`를 만족으로 적은 `assess('paper', basis, requirements, 'satisfied', ...)`를 런타임에 넣고 `academic_status`. 이어서 요건에 없는 기준 `publish`로 `assess`.
- 단언: 상태가 `'pending'` 그대로. 없는 기준의 평가는 `ValueError`(유형만).
- 대역: 없음.
- 비고: 제품의 `academic_status`는 판정자와 평가의 현재성(`assessment_current`)까지 보므로, 과제와 실행에 묶이지 않은 평가는 완료 근거가 되지 않는다. 시험은 결과 상태만 단언한다.

### `test_rejection_needs_a_structured_current_resolution` (행 42–54)
- 성질: 외부 거절은 봉인된 해결 기록으로만 풀린다. `resolved=True` 표지나 손으로 쓴 해결 행으로는 풀리지 않는다.
- 준비: `setUp`의 런타임에 거절 `RJ`(현재 해결 근거, `resolved=True`, 묶이지 않은 산문 증거)를 둔다.
- 실행: `academic_status`. 봉인 해시 없이 손으로 쓴 해결 행을 `academic_resolution_records`에 둔 사본으로 `academic_status`. 이어서 연구 계획 실행 `E`(입력 해결 근거)와 증거 실행 `EX-evidence`를 두고 `record_resolution(..., {'id': 'RJ', 'decision': 'resolved', ..., 'evidence_refs': ['EX-evidence']}, execution_id='E')` 뒤 `academic_status`.
- 단언: 처음 두 상태는 `'externally_rejected'`, 마지막은 `'pending'`.
- 대역: 없음.
- 비고: 주석은 "봉인된 거절과 증거 해시가 없는 손으로 쓴 해결 행은 아무것도 풀지 않는다"고 적는다.

### `test_invalid_requirement_shapes_are_rejected` (행 56–61)
- 성질: 잘못된 요건 모양은 요건 기록 생성에서 거부된다.
- 준비: 네 요건. (1) ID만 있음. (2) 빈 기준과 다른 판정자. (3) 중복 필수 입력. (4) 같은 ID의 외부 효과 둘.
- 실행: 각각 `requirement_record([value])`.
- 단언: 모두 `ValueError`(유형만).
- 대역: 없음.
- 비고: `subTest(value=...)` 네 경우.

### `test_unsolved_not_applicable` (행 63–66)
- 성질: 목표가 수학적으로 해결되지 않았으면 학술 요건은 해당 없음이다.
- 준비: `setUp`의 목표 상태를 `'unsolved'`로.
- 실행: `academic_status`.
- 단언: 결과가 정확히 `{'status': 'not_applicable', 'reason': 'goal not mathematically solved'}`.
- 대역: 없음.

### `test_effect_receipts_require_the_exact_successful_operation` (행 68–80)
- 성질: 요건의 외부 효과는 그 과제·요건·요건 해시·해결 근거·효과 ID에 정확히 묶이고 성공으로 확인된 외부 연산만 영수증으로 인정한다.
- 준비: 필수 입력 `context:goal`과 외부 효과 `submit`(허가 `G`)을 가진 요건 기록.
- 실행: 연산 없이 `effect_receipts(requirement, task_id='T', ...)`. 이어서 확인·성공이고 학술 결속(`task_id='T'`, 요건 `paper`, 요건 해시, 해결 근거, 효과 `submit`)을 가진 연산 `OP`를 두고 다시. `succeeded`를 거짓으로 바꾸고 다시.
- 단언: 첫 값 `[0]`이 거짓, 참, 거짓.
- 대역: 없음.

## AcademicConsumerTests (행 83–267)

`unittest.TestCase`를 그대로 상속한다. 클래스 docstring은 "실제 학술 생산자와 TASKS 소비자. 수학적 증거는 합성"이다. 표지, 속성, 설정 훅이 없다. 네 도우미 메서드가 층층이 시작 상태를 쌓는다.

- `host()` (행 86–112): `bare_engine()`을 만들고 `_solution_basis`(엔진의 `basis` 사본을 돌려줌), `_academic_evidence`(`None`), `_lifecycle_now`(`2026-09-20T00:00:00Z`)를 `create_autospec` 대역으로 바꾼다. 인스턴스는 `approved_governance`로 학술 요건 `AR`(범위 "Prepare a manuscript", 판정자 `research_plan`, 기준 "Explain the proof"와 "Discuss the limitations")을 가진 헌장을 원천 `S`에서 채택한 것이다. 설정은 `DEFAULT_CONFIG`에 도구 검토 창 60초와 자기 점검 응답 창 5초를 더한 것이고, `build_profiles`로 만든 프로필과 연구 작업 역할 프로필 참조(주석: 초기화처럼 모든 연구 작업 등급 판본을 채택한다. 평가되지 않은 작업 과제는 고급 등급을 요구한다)를 둔다. 목표는 해결됨, 지역 허가 `G`(연구 작업, 재사용 가능)가 있다. 해결 근거는 원천 `S`를 기록으로 가진 `solution_basis('synthetic-current-goal', ...)`이다.
- `generated()` (행 114–116): `host()`에서 `_ensure_academic_followup()`을 불러 학술 과제를 만들고 `(h, task)`를 돌려준다.
- `reviewed()` (행 118–129): `generated()`에서 관찰 규칙 대상 준비 작업을 큐에서 찾아, 끝난 준비 실행 `PREP`의 확장에 `prepared_rule_conditions([task_id])`를 두고 `_finish_assessment_preparation(action, 'PREP')`와 `_remove_action(action)`을 부른다. 이어서 `review_items([task_id], next_owner='research_preparation')`을 `seal_contract_review`로 봉인해 과제 검토에 더한다.
- `assessed(*, kind='fulfilled', decision='completed')` (행 131–143): `reviewed()`에서 과제에 결과(실행 `WORK`)를 두고, 끝난 작업 실행 `WORK`와 해결 근거를 입력으로 가진 계획 실행 `PLAN`을 둔다. 모든 의무에 `kind` 처분(증거 `WORK`)을 준 `decision` 평가를 `apply_task_assessments(..., execution_id='PLAN', ...)`로 적용하고 `(h, task, assessment)`를 돌려준다.

### `test_actual_constructor_review_and_ready_population_use_the_task_contract` (행 145–158)
- 성질: 학술 요건 생산자가 만든 과제는 일반 과제 계약 검증을 통과하고, 기준마다 의무 하나를 가지며, 역할 프로필과 허가와 해결 근거 기록을 입력으로 담고, 검토 뒤 착수 가능하다. 생산자를 다시 불러도 과제가 늘지 않는다.
- 준비: `reviewed()`.
- 실행: `validate_task_contract`, `task_ready`, `ready_task_ids`, 다시 `_ensure_academic_followup`.
- 단언: 의무 주장 목록이 두 기준과 같다. `profile_refs`가 인스턴스의 연구 작업 역할 프로필 참조와 같고, `authority_refs`가 `['G']`, 해결 근거 기록 ID가 `inputs`의 부분집합, `completion_criteria` 키가 없다. 상태가 `'ready'`, 준비 목록이 `[task_id]`. 생산자 재호출 뒤 과제가 1개.
- 대역: `host()`의 세 `create_autospec` 대역.

### `test_actual_assessment_consumer_uses_item_dispositions_and_current_evidence` (행 160–168)
- 성질: 학술 평가는 적용된 과제 평가의 항목 처분에서 만들어지고, 같은 평가를 두 번 기록해도 하나이며, 증거 실행이 바뀌면 학술 완료가 무효가 되고 다시 기록할 수 없다.
- 준비: `assessed()`.
- 실행: `_record_academic_assessment(task, assessment, 'PLAN')`, `_academic_status()`, 다시 기록. 작업 실행 `WORK`에 `changed_evidence=True`를 달고 `_academic_status()`와 다시 기록.
- 단언: 상태가 `'completed'`. 학술 평가가 1개. 증거 변경 뒤 상태가 `'completed'`가 아니고, 기록은 `ValueError`(유형만).
- 대역: `host()`의 대역.
- 비고: 증거 실행 기록에 필드를 하나 더해 증거 내용을 바꾼다. 제품의 `_record_academic_assessment`는 적용된 과제 평가가 현재가 아니면 `"academic result requires the current applied independent TASKS assessment"`로 거부하지만, 시험은 예외 유형만 보므로 어느 검사에서 거부되는지는 고정하지 않는다.

### `test_open_disposition_keeps_followup_in_same_task_contract` (행 170–176)
- 성질: 의무가 열린 미완 평가는 같은 과제를 대기로 두고 학술 평가를 불만족으로 기록하며, 생산자는 새 과제를 만들지 않는다.
- 준비: `assessed(kind='open', decision='incomplete')`.
- 실행: `_record_academic_assessment`, `_ensure_academic_followup`.
- 단언: 과제 `status`가 `'waiting'`, 첫 학술 평가의 `decision`이 `'not_satisfied'`, 과제가 1개.
- 대역: `host()`의 대역.

### `test_engine_plan_dispatch_consumes_generated_contract_and_applied_assessment` (행 178–210)
- 성질: 엔진의 계획 적용은 생성된 학술 과제를 선택해 작업을 큐에 넣고, 돌아온 결과의 완료 평가를 적용해 과제·학술 상태·인스턴스 상태를 완료로 만든다.
- 준비: `reviewed()`. 선택 계획 실행 `SELECT`(입력 스냅숏 `before-work`, 입력 묶음 `BA-select`). 상태 사본 `first`. 저장소를 `create_autospec(ResearchRepository, instance=True)`로 바꾸고, `view`가 스냅숏과 `first` 사본을, `read`가 스냅숏·과제 목록·준비 목록 `[tid]`의 JSON을 돌려주게 한다. 머리를 `before-work`로, `_evaluation_context`를 스냅숏만 담은 사전을 돌려주는 대역으로 둔다.
- 실행:
  1. `ResearchEngine._apply_plan(h, {'dispositions': [선택 처분], 'task_assessments': [], 'goal_audit': False}, 'SELECT')`.
  2. 과제에 결과를 두고 작업 실행 `WORK`와 계획 실행 `PLAN`(스냅숏 `after-work`, 묶음 `BA-returned`, 해결 근거)을 둔다. 상태 사본 `returned`로 저장소 대역을 다시 만들고(준비 목록 `[]`) 머리를 `after-work`로 둔다. 모든 의무 충족의 완료 평가로 `_apply_plan(h, {..., 'task_assessments': [assessment]}, 'PLAN')`.
- 단언: (1) 뒤 과제 `status`가 `'active'`이고 큐에 그 과제의 `research_work` 작업이 있다. (2) 뒤 과제 `status`가 `'completed'`, `_academic_status()['status']`가 `'completed'`, 런타임 `status`가 `'completed'`.
- 대역: 저장소의 `create_autospec` 대역 두 벌과 `view`·`read` 부수 효과, `_evaluation_context` 대역, `host()`의 대역.

### `test_unapplied_or_different_assessment_cannot_certify_academic_success` (행 212–217)
- 성질: 적용된 과제 평가와 다른 평가나, 적용 기록이 없는 과제로는 학술 성공을 기록할 수 없다.
- 준비: `assessed()`. 첫 처분의 증거를 `'not-in-input'`으로 바꾼 위조 사본.
- 실행: 위조로 `_record_academic_assessment`. 과제에서 `assessment`를 빼고 원 평가로 다시.
- 단언: 두 호출 모두 `ValueError`(유형만).
- 대역: `host()`의 대역.

### `test_scope_waiver_records_authority_without_applying_a_second_task_lifecycle` (행 219–237)
- 성질: 사용자의 과제 범위 면제 결정은 과제 자체를 바꾸지 않고 권한만 기록하며, 그 권한으로 모든 의무를 면제해 닫은 학술 과제는 학술 완료가 되지 않는다.
- 준비: `generated()`. 과제에 결과를 두고, 모든 의무를 면제하는 `task_scope` 결정(`WAIVER`, 현재 개정과 계약 해시)을 만든다. 과제 사본을 뜬다.
- 실행: `gov.apply_decision(..., change, source_ref='S')`. 계획 실행 `PLAN`을 두고 모든 의무를 결정 권한으로 `waived` 처분한 `closed` 평가를 `apply_task_assessments`로 적용한 뒤 `_record_academic_assessment`와 `_academic_status`.
- 단언: 결정 적용 뒤 과제가 사본과 같다. 학술 상태가 `'completed'`가 아니다.
- 대역: `host()`의 대역.

### `test_task_scope_transfer_decision_changes_no_task_and_requires_the_current_contract` (행 239–249)
- 성질: 과제 범위 이전 결정은 과제를 바꾸지 않고, 현재 계약 해시에 묶여야 한다.
- 준비: `generated()`의 과제를 복제한 수신 과제 `RECIPIENT`. 첫 의무를 `RECIPIENT`로 옮기는 `task_scope` 결정.
- 실행: `gov.apply_decision`. 계약 해시를 `'stale'`로 바꾸고 다시.
- 단언: 적용 뒤 과제 집합이 원래와 같다. 낡은 해시는 `ValueError`(유형만).
- 대역: `host()`의 대역.

### `test_academic_only_charter_change_preserves_math_fact_and_replaces_requirement_task` (행 251–267)
- 성질: 학술 요건만 바꾸는 헌장 교체는 수학적 해결 사실을 유지하고 옛 학술 과제를 닫아 새 요건의 과제로 바꾼다. 목표를 바꾸는 헌장 교체는 해결 사실을 되돌린다.
- 준비: `generated()`. 요건 `AR`의 기준을 `['Revised manuscript']`로 바꾼 헌장 `CH2`(`CH1` 대체).
- 실행: `apply_decision`으로 `CH2` 채택, `_ensure_academic_followup`. 이어서 목표 "Prove Q"의 헌장 `CH3`(`CH2` 대체) 채택.
- 단언: `CH2` 뒤 `goal_status`가 `'mathematically_solved'`, 옛 과제가 `'closed'`, 닫히지 않은 과제가 1개이고 첫 의무 주장이 `'Revised manuscript'`. `CH3` 뒤 `goal_status`가 `'unsolved'`.
- 대역: `host()`의 대역.

## AcademicGovernanceTests (행 270–305)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다.

### `test_resolution_is_current_only_while_its_real_evidence_is_unchanged` (행 271–288)
- 성질: 외부 거절의 해결은 증거 산출물을 실제로 읽을 수 있을 때만 기록되고, 그 바이트가 바뀌면 거절이 다시 미해결이 된다.
- 준비: `domain_governance()`를 해결됨으로 두고, 해결 근거 `solution_basis("CH1", [{"id": "K"}])`, 거절 `RJ`, 연구 계획 실행 `E`. 산출물 경로 `runtime/artifacts/BA-response/response.md`와 그 바이트를 담은 사전 `stored`(주석: 산출물 증거는 상태 기록 가족이 아니며, 엔진이 저장된 바이트에서 해석한다, `academic_engine._academic_evidence`).
- 실행: 증거 해석기 없이 `academic.record_resolution`. `resolve_evidence=stored.get`으로 다시. `unresolved_rejections`. 바이트를 `b"changed"`로 바꾸고 `unresolved_rejections`.
- 단언: 해석기 없는 기록은 `ValueError`(유형만). 해결 뒤 미해결 목록이 `[]`. 바이트 변경 뒤 1개.
- 대역: `stored.get`을 증거 해석기로 쓴다.

### `test_generic_academic_request_must_bind_the_solution_it_relied_on` (행 290–299)
- 성질: 학술 전용 허가 아래의 외부 요청은 기댄 해결 근거에 묶여야 학술 선행 조건을 만족하고, 다른 해결 근거에서는 만족하지 않는다.
- 준비: 해결된 `domain_governance()`, 해결 근거, 학술 전용 허가 `G`, `prepare_operation`으로 만든 `POST` 연산.
- 실행: `academic.external_prerequisite`, `bind_external_prerequisite`로 묶은 뒤 다시, 이어서 다른 근거(`CH2`)로.
- 단언: 거짓, 참, 거짓.
- 대역: 없음.

### `test_academic_basis_rejects_a_stale_judgment_dependency` (행 301–305)
- 성질: 목표 판정의 의존 기록 내용이 바뀌면 현재 해결 근거를 만들 수 없다.
- 준비: `bare_engine()`에 해결된 인스턴스(지식 `K`의 `text='new'`, 평가 근거 `B`)와, 옛 내용(`text='old'`)으로 뜬 `capture_basis`를 기록 근거로 가진 현재 목표 판정을 둔다.
- 실행: `h._solution_basis()`.
- 단언: `None`.
- 대역: 없음.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈: 학술 요건의 엔진 구동 경로는 `test_academic_engine`, `test_academic_preparation`, `test_model_assessment_flow`가 `academic` 조각에서 본다. 과제 평가 적용의 일반 규칙은 `test_task_contracts`, 외부 연산의 전송 규칙은 `test_external_operations`가 본다.
- 픽스처 의존: `record_fixtures.domain_governance`; `research_fixtures`의 `approved_governance`, `bare_engine`, `charter`, `disposition`, `review_items`, `prepared_rule_conditions`.
- 이 모듈에만 있는 도우미: `Tests.setUp`, `AcademicConsumerTests`의 `host`, `generated`, `reviewed`, `assessed`.
- 겹치거나 보완하는 시험: 거절 해결은 `Tests.test_rejection_needs_a_structured_current_resolution`(실행 증거)과 `AcademicGovernanceTests.test_resolution_is_current_only_while_its_real_evidence_is_unchanged`(산출물 바이트 증거)가 두 증거 형태로 본다. 외부 효과는 영수증 쪽(`test_effect_receipts_require_the_exact_successful_operation`)과 요청 결속 쪽(`test_generic_academic_request_must_bind_the_solution_it_relied_on`)으로 나뉜다.

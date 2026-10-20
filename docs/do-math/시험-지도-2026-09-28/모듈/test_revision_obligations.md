# test_revision_obligations

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_revision_obligations.py` (139행) |
| 클래스 / 테스트 | 1 / 7 |
| 시험 대상 제품 코드 | `do_math/revision_engine.py`의 `RevisionEngineMixin._retire_closed_revision_targets`, `_selected_action_current`, `_reconcile_revision_delegations`, `_apply_revision_followup`, 간접으로 `_bind_revision_action`; `do_math/engine.py`의 `ResearchEngine._enqueue`, `_remove_action`, `_apply`, `_governance`; `do_math/decision_engine.py`의 `DecisionEngineMixin._apply_task_plan`; `do_math/planning.py`의 `revision_waits`, `pending_revisions`, `revision_cycles`, `task_ready`; `do_math/revisions.py`의 `capture_targets`, `submission_errors`; `do_math/governance.py`의 `governance_view` |
| 사용하는 픽스처 모듈 | `research_fixtures`(`bare_engine`, 함수 안에서 import하는 `contract_review`), `record_fixtures`(`approved_task`, `task_disposition`) |
| 격리 표지 | 없음 |
| 시작 상태 | `FakeEngine`이 아닌 실제 `ResearchEngine` 객체를 `bare_engine`으로 저장소 없이 만들고, `approved_task()`의 합성 사전 상태를 싣는다. 엔진 루프는 돌리지 않고 믹스인 메서드를 직접 부른다. 네 단 가운데 1단에 가깝지만 제품 엔진 객체의 메서드를 쓴다는 점이 다르다 |

## 목적

모듈 docstring은 "실제 TASKS 믹스인이 위임과 재시도를 거치면서도 개정(revision) 소유권을 유지한다"고 밝히고, "하네스는 픽스처 상태만 공급하며 제공자나 Git 동작을 끝단 결과로 흉내 내지 않는다. 중앙 배정·직렬화는 MAIN 회귀 시험의 몫이다"라고 덧붙인다.

개정 의무는 이렇게 흐른다. 기존 기록(과제나 지식)을 고치려는 작업은 `revision_targets`에 대상과 그 시점의 기준(`revisions.capture_targets`)을 선언한다. 작업이 끝나면 `_apply_revision_followup`이 대상마다 제출된 처분(`revised`, `unchanged`, `delegated`, `deferred`)을 읽고, 해결되지 않은 대상이 있으면 그 작업을 `waiting_actions`의 `revision_dependency` 항목으로 남긴다. `delegated` 처분은 준비된 지식 개정 과제에 의무를 넘기며, 그 과제의 작업이 `revised`로 끝나면 부모 의무가 풀린다. 이 모듈은 이 소유권 흐름의 일곱 성질을 본다.

1. 닫힌 대상만 개정 목록에서 빠지고, 다른 대상과 병합된 새 요청은 남는다.
2. 개정은 그 대상을 읽는 소비자만 막고 독립 작업은 겹칠 수 있다.
3. 위임된 과제의 검토와 작업은 자기 의무 때문에 막히지 않는다.
4. 유지보수(`maintenance`)는 대기 중인 개정과 순환을 읽을 수 있다.
5. 위임받은 과제가 닫히면 의무는 부모로 돌아와 새 준비자에게 넘어간다.
6. 계획 선택과 배정 직전 검사는 실제 현재 입력을 쓴다.
7. 개정 제출은 대상을 빠뜨리거나 필수 수리를 `unchanged`로 취소할 수 없다.

## 모듈 수준 요소

- 행 11: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리.
- `owner_harness()` (행 17–20): `record_fixtures.approved_task()`의 과제 `TK-1`, 인스턴스, 런타임에 빈 `waiting_actions`를 더하고 `bare_engine(instance, runtime)`으로 감싼 엔진을 돌려준다. 모든 시험과 `delegated`가 쓴다.
- `enqueue(h, role, target=None, **fields)` (행 23–26): docstring은 "제품을 통해 큐에 넣고, 그것이 더하거나 병합한 행을 돌려준다". `h._enqueue`를 부른 뒤 큐를 뒤에서부터 훑어 같은 `role`과 `target`의 첫 행을 돌려준다. 네 시험과 `delegated`가 쓴다.
- 행 139: 직접 실행하면 `unittest.main(verbosity=2)`.

## RevisionObligationTests (행 29–136)

`unittest.TestCase`를 그대로 상속한다. 클래스 표지, 클래스 속성, 설정 훅이 없다. 준비는 각 시험이 `owner_harness()`나 `delegated()`로 한다.

- `delegated()` (행 56–63): 위임이 성립한 상태를 만든다. 지식 `KN-source`(개정 1)를 두고, `research_preparation` 부모 작업을 `KN-source`를 필수(`required=True`)로 선언해 큐에 넣는다. 과제 `TK-1`을 제목 `'Correct source'`, 생산 실행 `EX-prep`, `knowledge_revision_targets=['KN-source']`로 바꾼다. 끝난 실행 `EX-prep`의 확장에 `KN-source`를 `delegated`(과제 제목 `'Correct source'`)로 처분한 행을 둔다. `h._apply_revision_followup(parent, ..., 'EX-prep')`로 후속 처리를 적용하고 `h._remove_action(parent)`로 부모를 큐에서 뺀다. `(h, parent)`를 돌려준다. 세 시험이 쓴다.

### `test_closed_target_does_not_erase_other_targets_or_merged_new_request` (행 30–40)
- 성질: 개정 대상 가운데 닫힌 것만 개정 목록에서 빠지고, 병합으로 대상 없는 요청(`unbound_request`)을 떠안은 행은 대상이 모두 빠져도 큐에 남는다. 대상도 없고 병합 표지도 없으면 큐에서 빠진다.
- 준비: `owner_harness()`에 `TK-1`의 사본 `TK-2`를 더한다. `enqueue`로 `research_preparation` 작업 `a`를 `TK-1`, `TK-2` 두 대상으로 넣는다.
- 실행: (1) `TK-1`을 `closed`로 바꾸고 `h._retire_closed_revision_targets()`. (2) `a['unbound_request']=True`, `TK-2`를 `closed`로 바꾸고 다시 부른다. (3) `a['revision_targets']={'TK-2': {}}`, `unbound_request=False`로 바꾸고 다시 부른다.
- 단언: (1) 뒤 `a`의 개정 대상 키 집합이 `{'TK-2'}`. (2) 뒤 큐가 `[a]`이고 `a['revision_targets']`가 `{}`. (3) 뒤 큐가 빈 목록.
- 대역: 없음.
- 비고: `unbound_request`는 제품의 `_enqueue`가 개정 대상 없는 요청을 대상 있는 행에 병합할 때 다는 표지다(`engine.py` `_enqueue`의 주석 "A request without revision targets must outlive the retirement of merged targets."). 이 시험은 그 표지를 직접 켜고 끈다.

### `test_revision_blocks_consumer_but_independent_work_can_overlap` (행 42–54)
- 성질: 과제 개정 작업이 대기 중이면 그 과제를 입력으로 읽는 작업은 기다리지만 무관한 작업은 기다리지 않고, 개정 작업은 실행 중인 소비자가 끝날 때까지만 기다린다.
- 준비: `owner_harness()`의 `TK-1`을 `a`로, `TK-1`을 입력으로 읽는 사본 `TK-B`, 독립 사본 `TK-C`를 만든다(둘 다 `reviews=[]`). `enqueue(h, 'research_preparation', 'TK-1')`로 개정 작업 `writer`를 넣는다. 제품의 `_bind_revision_action`이 이 작업에 `TK-1`을 개정 대상으로 붙인다.
- 실행: 소비자 작업 `AC-B`(`research_work`, `TK-B`)와 독립 작업 `AC-C`(`research_work`, `TK-C`)에 `planning.revision_waits`. 이어서 `AC-B`를 실행 `EX-reader`로 `running`에 두고 `writer`를 판정, 그 실행을 `ended`로 바꾸고 다시 판정.
- 단언: `AC-B`의 대기가 참, `AC-C`의 대기는 `[]`. 소비자가 실행 중이면 `writer`의 대기가 참, 끝나면 `[]`.
- 대역: 없음.

### `test_delegated_work_and_review_do_not_block_on_own_obligation` (행 65–80)
- 성질: 위임받은 과제의 계약 검토와 작업은 자신이 떠안은 개정 의무 때문에 막히지 않고, 그 작업이 대상을 `revised`로 끝내면 부모의 의무가 풀리며 과제는 평가 대기로 간다.
- 준비: `delegated()`. 부모 작업의 `waiting_actions` 항목을 `entry`로 읽는다.
- 실행: 검토 작업 `AC-review`(`task_contract_review`, `TK-1`)에 `revision_waits`. `enqueue(h, 'research_work', 'TK-1')`로 작업을 넣고 `revision_waits`. 끝난 실행 `EX-work`의 확장에 `knowledge_changes=[{'id': 'KN-source'}]`와 `KN-source`의 `revised` 처분을 두고, `KN-source`의 개정을 2로 올린 뒤 `h._apply_revision_followup(work, {'summary': 'correction', 'outcome': 'submitted'}, 'EX-work')`.
- 단언: `entry['delegated_targets']`가 `{'KN-source': 'TK-1'}`. 검토의 대기가 `[]`. 작업의 `revision_targets`에 `KN-source`가 있고(과제의 `knowledge_revision_targets`에서 붙음) 대기가 `[]`. 후속 처리 뒤 부모 ID가 `waiting_actions`에서 사라지고, `TK-1`의 `status`가 `'waiting'`, `waiting['next_owner']`가 `'research_plan'`이다.
- 대역: 없음.

### `test_maintenance_can_read_pending_revisions_and_cycles` (행 82–87)
- 성질: 유지보수 작업은 개정 대기에 막히지 않고, 대기 중인 개정 목록과 개정 순환을 읽을 수 있다.
- 준비: `delegated()`.
- 실행: 유지보수 작업 `AC-check`(`maintenance`, 대상 `KN-source`)에 `revision_waits`, 이어서 `planning.pending_revisions(h.runtime)`, `planning.revision_cycles(h.instance, h.runtime)`.
- 단언: 대기가 `[]`. 대기 개정 목록을 `(state, 개정 대상 키 집합)`으로 옮긴 결과가 `[('waiting', {'KN-source'})]`. 순환이 `[]`.
- 대역: 없음.
- 비고: 제품의 `revision_waits`는 `operational_review`, `intent_interpretation`, `maintenance` 역할에 늘 빈 목록을 돌려준다. 이 시험은 그 가운데 `maintenance` 하나를 본다.

### `test_closed_delegate_keeps_obligation_for_new_preparer` (행 89–100)
- 성질: 위임받은 과제가 닫히면 그 과제에 딸린 실패 작업은 물러나고, 개정 의무는 부모에게 위임 표지 없이 남아 새 준비 작업이 그 의무를 이어받는다.
- 준비: `delegated()` 뒤 `TK-1`을 `closed`로, 큐를 비운다. `waiting_actions`에 실패 대기 `failed-child`(`execution_failure`, `research_work`, 대상 `TK-1`, 개정 대상 `KN-source`)를 넣는다.
- 실행: `h._retire_closed_revision_targets()`와 `h._reconcile_revision_delegations()`. 이어서 `enqueue`로 `KN-source`를 대상으로 하는 새 `research_preparation` 작업 `new`를 넣고 `revision_waits`, `revision_cycles`.
- 단언: `failed-child`가 `waiting_actions`에서 사라진다. 부모 항목의 개정 대상 키 집합이 `{'KN-source'}`이고 `delegated_targets`가 거짓(빈 사전). `new['revision_parent_ids']`에 부모 ID가 있다. `new`의 대기가 `[]`, 순환이 `[]`.
- 대역: 없음.
- 비고: `revision_parent_ids`는 제품의 `_bind_revision_action`이 대기 중인 `revision_dependency` 항목과 개정 대상을 공유하는 준비 작업에 붙인다. `_reconcile_revision_delegations`가 연구 계획 작업을 큐에 넣는 부수 효과는 단언하지 않는다.

### `test_plan_selection_and_predispatch_use_actual_current_input` (행 102–126)
- 성질: 계획이 선택한 작업은 배정 직전에 현재 입력으로 다시 판정되어, 원천이 바뀌면 물러나고 연구 계획이 다시 큐에 들어간다. 이어서, 계약 검토의 적용은 검토가 만든 대기만 지우고 다른 종류의 대기는 보존한다.
- 준비: `owner_harness()`에 끝난 계획 실행 `EX-plan`을 둔다. 계획 출력은 `task_disposition('TK-1')` 하나의 선택 처분이다.
- 실행:
  1. `h._apply_task_plan(plan, 'EX-plan', deepcopy(tasks), ['TK-1'])`로 `research_work` 작업을 큐에 넣고 `h._selected_action_current(action)`.
  2. 인스턴스 원천 `SO-1`의 `sha256`을 `'b'*64`로 바꾸고 다시 `_selected_action_current`.
  3. `h._governance`를 `create_autospec(h._governance, side_effect=lambda: governance_view(h.instance))`로 바꾼다. `contract_review({'task': task})`로 만든 승인 검토를 `ResearchEngine._apply(h, review_action, ..., 'EX-fresh-review', owns_response=False)`로 적용하고 `task_ready`.
  4. `task['waiting']`을 `{'kind': 'external_event', 'next_owner': 'user'}`로 두고 다른 검토(`EX-other-review`)를 같은 방식으로 적용한 뒤 `task_ready`.
- 단언: (1) 참. (2) 거짓이고, 큐에 `research_work`가 없고 `research_plan`이 있다. (3) 과제에 `waiting` 키가 없고 `task_ready(...)['state']`가 `'ready'`. (4) `waiting`이 설정한 사전 그대로이고 상태가 `'not_ready'`.
- 대역: `h._governance`를 감싼 `create_autospec` 대역(부수 효과로 제품 `governance_view`를 부른다).
- 비고: 이름은 계획 선택과 배정 직전 검사를 말하지만, (3)(4)는 계약 검토 적용이 외부 사건 대기를 지우지 않는다는 다른 성질을 단언한다. (2)에서 물러난 과제의 `waiting` 기록(`contract_review` 종류)과 이력 행 `obsolete_selection`은 단언하지 않는다.

### `test_revision_cannot_omit_target_or_cancel_required_repair_as_unchanged` (행 128–136)
- 성질: 개정 대상을 선언한 작업의 제출은 대상의 처분을 빠뜨릴 수 없고, 필수 개정을 `unchanged`로 취소할 수 없으며, 대응하는 개정 후보와 `revised` 처분을 갖추면 오류가 없다.
- 준비: `owner_harness()`의 `TK-1`과, `TK-1`을 필수 개정 대상으로 선언한 `research_preparation` 작업. 문맥은 `{'action': action, 'tasks': [task]}`.
- 실행: `revisions.submission_errors`를 세 번. (1) 빈 출력·빈 확장. (2) `TK-1`을 `unchanged`로 처분한 확장. (3) 처분을 `revised`로 바꾸고 출력에 `revises_task_id='TK-1'`인 후보를 둔다.
- 단언: (1)과 (2)는 오류 목록이 참(비어 있지 않음), (3)은 `[]`. 오류의 경로나 메시지는 고정하지 않는다. 제품에서 (1)은 `"resolve each declared target exactly once, ..."`, (2)는 `"a required revision or rejected contract cannot be cancelled as unchanged"`에 해당하는 경로다.
- 대역: 없음.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈: `revision_waits`와 `capture_targets`는 `test_relation_dependencies`(관계의 간접 끝점), `test_decision_basis`, `test_academic_preparation`, `test_planning_engine`에서도 불린다. 모듈 docstring이 가리키는 중앙 배정·직렬화 경로는 엔진 구동 시험의 몫이다.
- 픽스처 의존: `research_fixtures.bare_engine`, `contract_review`; `record_fixtures.approved_task`, `task_disposition`.
- 이 모듈에만 있는 도우미: 모듈 함수 `owner_harness`, `enqueue`, 클래스 도우미 `delegated`.
- 겹치거나 보완하는 시험: 개정 제출 검사는 이 모듈의 마지막 시험이 순수 함수로, 개정 소유권의 흐름은 나머지 시험이 엔진 믹스인으로 본다.

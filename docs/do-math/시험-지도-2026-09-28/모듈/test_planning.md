# test_planning

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_planning.py` (367행) |
| 클래스 / 테스트 | 6 / 21 |
| 시험 대상 제품 코드 | `do_math/planning.py`의 `validate_condition`, `evaluate_condition`, `record_index`, `governance_revisions`, `task_ready`, `capture_task_basis`, `contract_hash`, `revision_requested`, `revision_required`, `collect_due_events`, `record_due_events`, `schedule_reconsideration`, 상수 `CONDITION_FIELDS`, `RECORD_FAMILIES`, `EXPOSED_FIELDS`; `do_math/initialization.py`의 `governance_working_view`; `do_math/model_policy.py`의 `preparation_only`; `do_math/task_scope.py`의 `designated_judgment`; `do_math/activities.py`의 `open_activity`; `do_math/knowledge_records.py`의 `record_identity_assessment`, `identity_basis`, `create_candidate`; `do_math/knowledge.py`의 `assess_use`; `do_math/git_store.py`의 `ARTIFACT_ROOT` |
| 사용하는 픽스처 모듈 | `record_fixtures`(`approved_task`, `approve_task`, 함수 안에서 import하는 `domain_governance`, `governance_import`), `knowledge_fixtures`(함수 안에서 import하는 `verified_knowledge`) |
| 격리 표지 | 없음 |
| 시작 상태 | 모두 1단. 사전 상태에 순수 함수를 부른다. 두 시험은 스킬 폴더의 실제 문서 `references/과제-착수조건.md`를 읽는다 |

## 목적

모듈 docstring은 "계획: 조건, 착수 가능성(readiness), 계획 입력. 저장된 준비 상태 픽스처 없음"이라고 밝힌다.

do-math의 과제는 발생 조건(`occurrence_condition`)이라는 기계 판정 조건을 갖는다. 조건은 `op`로 시작하는 작은 문법(`always`, `all`, `any`, `not`, `record_exists`, `record_field_equals`, `record_lifecycle_is`, `relation_exists`, `artifact_valid` 등)이며, 기록 가족(`RECORD_FAMILIES`)과 가족마다 노출된 필드(`EXPOSED_FIELDS`)만 읽을 수 있다. `planning.evaluate_condition`은 조건을 `ready`, `not_ready`, `evaluation_error` 가운데 하나로 판정하고, 판정이 기댄 기록마다 해시를 담은 근거(`basis`)를 돌려준다. `planning.task_ready`는 과제의 계약 검토, 입력, 조건, 대기를 모아 과제가 지금 착수 가능한지 판정한다. 계획 입력 쪽에서는 주기적 재검토 시각과 새 입력 요청이 사건(`events`)으로 기록되고 연구 준비 작업으로 이어진다.

이 모듈은 다음을 본다.

- 조건의 판정과 근거, 잘못된 조건의 오류 상태, 노출 필드 제한, 산출물 경로 문법.
- 조건이 한 번의 기록 색인만 훑고, 산출물 조건은 읽기와 검증을 캐시한다.
- 착수 가능성 판정이 검토·조건을 다시 보고, 입력을 바꾸지 않으며, 두 인스턴스 형태에서 같은 값을 낸다.
- 계약 해시가 계약 필드에만 반응한다.
- 과거 목표 판정이 바뀐 거버넌스나 원천을 덮어쓰지 못한다.
- 주기 사건과 새 입력 사건이 한 번만 기록되고, 준비 전용 작업이 주기 탐색을 가로채지 않는다.
- 문서 `과제-착수조건.md`의 예시와 표가 제품 문법과 맞는다.

## 모듈 수준 요소

- 행 9: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리.
- 행 367: 직접 실행하면 `unittest.main(verbosity=2)`.

## ActivityConditionTests (행 14–29)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다.

### `test_activity_kind_uses_the_stored_activity_contract` (행 15–29)
- 성질: 활동 기록의 `activity_kind`는 조건에서 읽을 수 있고, 노출되지 않은 필드는 조건 검증에서 거부된다.
- 준비: `activities.open_activity`로 활동 `AT-kind`(`research_work`)를 연 런타임. 조건은 런타임 공간 `activity` 가족의 `AT-kind`에서 포인터 `/activity_kind`가 `'research_work'`와 같은지 본다.
- 실행: `planning.validate_condition(condition)`, 이어서 `evaluate_condition`을 원 조건, 값 `'maintenance'`, 없는 기록 `AT-missing`으로. 끝으로 포인터 `/role`로 `validate_condition`.
- 단언: 검증이 예외 없이 끝나고, 세 판정이 `'ready'`, `'not_ready'`, `'not_ready'`다. 포인터 `/role`은 `ValueError`이고 메시지가 `'exposed machine field'`에 맞는다.
- 대역: 없음.

## PlanningTests (행 30–184)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성이 없다.

- `setUp` (행 31–33): `record_fixtures.approved_task()`로 과제 `TK-1`, 인스턴스 `IN-1`, 런타임을 받는다. 과제는 원천 `SO-1`을 입력으로 읽는 비형식 과제이고 계약 검토가 승인되어 있다. 인스턴스에 지식 `K`(`lifecycle='active'`, `kind='lemma'`)를 둔다.
- `condition(op='record_exists', **changes)` (행 35–36): 연구 공간 `knowledge` 가족의 `K`를 가리키는 조건 사전을 만든다.

### `test_conditions_and_errors_preserve_basis` (행 38–53)
- 성질: 조건 판정은 입력을 바꾸지 않고 기댄 기록마다 근거를 남기며, 기록 내용이 바뀌면 근거 해시가 바뀐다. 알 수 없는 연산, 노출되지 않은 포인터, 하위 조건의 오류는 `evaluation_error`가 되고, 없는 기록은 부재 질의 근거와 함께 `not_ready`가 된다.
- 준비: `setUp`. `K`가 있고 `/kind`가 `'lemma'`인지 보는 `all` 조건.
- 실행: 판정, `K`의 `kind`를 `'theorem'`으로 바꾼 뒤 판정, 단순 존재 조건 판정. 세 잘못된 조건(`{'op': 'unknown'}`, 포인터 `/question`, `any` 안의 알 수 없는 연산) 판정. 지식을 모두 지운 뒤 존재 조건 판정.
- 단언: 첫 판정이 `'ready'`이고 근거가 2개이며 인스턴스가 사본과 같다. 종류 변경 뒤 `'not_ready'`. 존재 조건의 근거 해시가 첫 판정의 첫 근거 해시와 다르다. 잘못된 셋은 모두 `'evaluation_error'`. 지식 삭제 뒤 `'not_ready'`이고 첫 근거에 `'absencequery'` 키가 있다.
- 대역: 없음.

### `test_instance_conditions_and_bases_read_one_projection_of_either_instance_form` (행 55–68)
- 성질: 인스턴스 가족을 읽는 조건과 과제 근거는 인스턴스의 투영(projection)만 읽으므로, 전체 인스턴스와 거버넌스 작업 보기에서 같은 값을 내고, 인스턴스의 다른 연구 기록이 바뀌어도 근거가 같다.
- 준비: `setUp`. 과제 조건을 인스턴스 `/goal_revision`이 현재 목표 개정과 같은지로 두고 `approve_task`로 다시 승인한다. `initialization.governance_working_view(instance)`로 보기를 만든다.
- 실행: 두 형태로 `task_ready`와 `planning.capture_task_basis`. 지식 `K`의 종류를 바꾸고 전체 인스턴스로 다시 근거를 뜬다.
- 단언: `task_ready`의 상태가 `'ready'`이고 두 형태의 결과가 같다. 두 형태의 근거가 같다. 지식 변경 뒤 근거가 같다.
- 대역: 없음.
- 비고: 주석은 "인스턴스 기록은 전체 연구 상태가 아니라 그 투영"이라고 적는다.

### `test_artifact_condition_grammar_is_the_reader_prefix_and_state_segments` (행 70–78)
- 성질: 산출물 조건의 경로는 산출물 뿌리(`ARTIFACT_ROOT`) 아래의 안전한 경로 조각이어야 한다.
- 준비: 스냅숏과 `b'x'`의 해시를 가진 참조.
- 실행: `ARTIFACT_ROOT + 'BA-1/proof.txt'`로 `validate_condition`. 이어서 다섯 경로 `out/proof.txt`, `...BA-1/../proof.txt`, `...BA-1/con.txt`, `...BA-1/a:b.txt`, `ARTIFACT_ROOT` 자체로 검증.
- 단언: 첫 검증은 예외 없이 끝나고, 다섯 경로는 모두 `ValueError`(유형만).
- 대역: 없음.
- 비고: `subTest(path=...)` 다섯 경우. 제품의 `validate_condition`은 경로가 `ARTIFACT_ROOT` 아래의 보관 산출물이어야 한다고 보고(`"artifact path must name an archived artifact under ..."`), 나머지 조각마다 상태 경로 규칙 `check_path_segment`를 적용한다(주석 "each segment follows the state path rule"). 뿌리 밖 경로(`out/proof.txt`)는 앞 규칙에 걸린다. 뿌리 자체(`runtime/artifacts/`)는 접두 검사를 통과하지만 `/`로 나눈 마지막 빈 조각이 조각 규칙에 걸리고, 상위 경로 조각(`..`)·`con`·콜론도 조각 규칙에 걸린다. 시험은 어느 규칙에서 거부되는지 고정하지 않는다.

### `test_task_ready_rechecks_reviews_inputs_and_conditions` (행 80–86)
- 성질: 착수 가능성 판정은 계약 검토의 현재성과 발생 조건을 매번 다시 본다.
- 준비: `setUp`.
- 실행: `task_ready`. 첫 검토의 `revision`을 2로 바꾸고 다시. 조건을 `K`의 수명 주기가 `'withdrawn'`인지로 바꾸고 `approve_task`로 다시 승인한 뒤 다시.
- 단언: `'ready'`, `'not_ready'`, `'not_ready'`.
- 대역: 없음.
- 비고: 이름은 "inputs"도 말하지만 이 시험은 입력을 바꾸지 않는다. 없는 입력의 경우는 `ReadinessCopyTests.test_borrowed_inputs_and_copied_results_match_prior_evaluation`의 `missing` 경우가 다룬다.

### `test_contract_hash_only_changes_for_contract_fields` (행 88–93)
- 성질: 계약 해시는 상태·대기·이력 같은 장부 필드에 반응하지 않고 계약 필드에만 반응한다.
- 준비: `setUp`의 과제와 그 `contract_hash`.
- 실행: `status`, `waiting`, `history`를 바꾸고 해시, 이어서 `question`을 바꾸고 해시.
- 단언: 앞은 기준과 같고, 뒤는 다르다.
- 대역: 없음.

### `test_a_revision_request_of_an_earlier_revision_is_already_answered` (행 95–101)
- 성질: 이전 개정에 대한 개정 요청은 이미 응답된 것으로 보고, 현재 개정에 대한 요청만 개정 요구가 된다.
- 준비: 개정 2이고 `revision_requested={'revision': 1, ...}`인 과제 사전.
- 실행: `planning.revision_requested`, `revision_required`. 요청 개정을 2로 바꾸고 다시.
- 단언: 처음 둘은 거짓, 뒤의 둘은 참.
- 대역: 없음.

### `test_periodic_exploration_is_not_consumed_by_preparation_only` (행 103–130)
- 성질: 준비 전용 연구 준비 작업(평가 대상이나 관찰 규칙 대상만 가진 보충 작업)은 주기적 재검토 사건을 흡수하지 않고, 사건은 별도의 일반 연구 준비 작업 하나로 이어지며, 같은 사건으로 작업이 두 번 생기지 않는다.
- 준비: 두 필드(`assessment_targets`, `observation_rule_targets`)마다 `setUp` 런타임의 사본에 보충 작업 `AC-supplement`(그 필드에 과제 개정과 계약 해시)을 큐에 두고, 다음 재검토 시각을 `2026-09-24T00:00:00Z`로 둔다.
- 실행: `planning.record_due_events(..., '2026-09-25T00:00:00Z')`와 `planning.schedule_reconsideration(..., now=...)`. 이어서 1초 뒤 시각으로 두 호출을 반복한다.
- 단언: 보충 작업이 사본과 같다. 큐의 연구 준비 작업 가운데 `preparation_only`가 거짓인 것이 정확히 1개이고, 그 `event_refs`가 `research_reconsider_due` 사건 ID 목록과 같으며 `periodic_reconsideration`이 참이다. 어떤 사건에도 `assigned_to` 키가 없다. 1초 뒤 반복 뒤 큐 길이가 2다.
- 대역: 없음.
- 비고: `subTest(field=...)` 두 경우. 주석은 "배정은 요청의 `event_refs`에 있고, 출판된 사건에는 표지가 없다"고 적는다.

### `test_due_events_are_unique_and_paused_preserves_pending` (행 132–141)
- 성질: 만기 사건은 ID가 겹치지 않고, 인스턴스가 멈춘(`paused`) 동안 기록된 사건은 대기 사건 목록에 보존되며, 같은 시각에 다시 기록하면 새 사건이 없다.
- 준비: `setUp`의 런타임에 다음 재검토 시각 `2026-01-01`, 과제에 새 입력 요청 `newinput='RQ-source'`.
- 실행: `planning.collect_due_events(..., '2026-01-02T00:00:00Z')`. 런타임을 `paused`로 두고 `record_due_events`를 같은 시각으로 두 번.
- 단언: 수집한 사건 종류를 정렬하면 `['research_reconsider_due', 'task_new_input']`이고 ID가 모두 다르다. 첫 기록 뒤 `pending_events`가 기록된 사건 ID 목록과 같다. 둘째 기록은 `[]`.
- 대역: 없음.

### `test_one_input_request_is_one_event_across_observations_and_scheduling` (행 143–154)
- 성질: 새 입력 요청 하나는 관찰(사건 기록)과 일정 계획을 거쳐도 사건 하나이고, 새 요청이 오면 새 사건이 생긴다.
- 준비: `setUp`의 과제에 `newinput='RQ-source'`.
- 실행: `record_due_events`를 `00:00:00`과 `00:00:05`에. `schedule_reconsideration(now='...00:00:05Z')`. 과제의 요청을 `RQ-later`로 바꾸고 `00:00:09`에 기록.
- 단언: 첫 기록이 `[('task_new_input', 'RQ-source')]`, 둘째는 `[]`. 일정 계획 뒤 `task_new_input` 사건이 첫 사건 하나뿐이고 `pending_events`에 그 ID가 한 번 있다. 마지막 기록의 요청 ID 목록이 `['RQ-later']`.
- 대역: 없음.

### `test_source_arrival_and_trust_transition_are_machine_conditions` (행 156–165)
- 성질: 원천의 도착과 신뢰 환경의 상태 전이는 기계 조건으로 판정된다.
- 준비: 원천 `SO-new` 존재와 신뢰 환경 `TE-1`의 수명 주기가 `active`인지를 함께 보는 `all` 조건.
- 실행: 판정. 원천과 활성 신뢰 환경을 더하고 판정. 신뢰 환경을 `invalid`로 바꾸고 판정.
- 단언: `'not_ready'`, `'ready'`, `'not_ready'`.
- 대역: 없음.

### `test_relation_condition_rechecks_its_proof_after_import` (행 167–184)
- 성질: 관계 존재 조건은 관계가 인용한 형식 결과의 현재 사용 가능성을 다시 확인한다.
- 준비: `knowledge_fixtures.verified_knowledge()`로 검증된 정리 `kid`와 그 형식 결과 `fid`, 해설 `xid`를 얻는다. 해설에 관계 주장(`formally_implies`, 자기 자신)을 달고 `record_identity_assessment`로 새 신원 평가를 기록한다. 관계 `RL-1`(`formally_implies`, 형식 결과와 평가 인용)을 둔다.
- 실행: `{'op': 'relation_exists', 'subkind': 'formally_implies', 'from_id': kid, 'to_id': kid}` 판정. 형식 결과의 `formal_use`를 `'suspended'`로 바꾸고 판정.
- 단언: 처음은 `'ready'`(실패 메시지로 판정 전체). 뒤는 `'ready'`가 아니다.
- 대역: 없음.
- 비고: 함수 안에서 `knowledge_io`를 import하지만 쓰지 않는다. 이름의 "after import"는 원문의 동작과 대응하는 호출이 없다.

## ConditionIndexTests (행 188–209)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다.

### `test_compound_condition_scans_one_population_and_rechecks_the_next_evaluation` (행 189–209)
- 성질: 여러 하위 조건을 가진 복합 조건은 기록 색인을 한 번만 만들고, 다음 판정에서는 새로 만든다. 같은 ID가 두 가족에 있으면 오류이고, 가족이 다른 기록을 가리키면 오류다.
- 준비: 지식 200개를 가진 인스턴스와, 그 가운데 50개의 존재를 보는 `all` 조건.
- 실행: `patch.object(planning, 'record_index', wraps=planning.record_index)`로 호출 수를 세며 판정. `K0`을 지우고 판정. 런타임에 같은 ID의 과제 `K1`을 두고 판정. 런타임 `task` 가족에서 `K1`을 찾는 조건을 빈 런타임으로 판정.
- 단언: 색인 호출 수가 1, 상태가 `'ready'`, 근거가 50개. 삭제 뒤 `'not_ready'`. 중복 ID는 `'evaluation_error'`이고 첫 오류에 `'duplicate'`가 든다. 다른 가족 조건은 `'evaluation_error'`이고 첫 오류에 `'another family'`가 든다.
- 대역: `record_index`를 감싸 호출을 세는 `patch.object`(원 함수를 그대로 부른다).

## ArtifactConditionTests (행 212–239)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다.

### `test_artifact_condition_reads_and_validates_a_sealed_artifact_once` (행 213–225)
- 성질: 저장소가 있는 판정 문맥에서 봉인된 산출물 조건은 산출물을 한 번 읽고 한 번 검증한 뒤 결과를 재사용한다.
- 준비: 바이트 `{"result": true}`와 그 해시를 가진 산출물 참조. 판정 문맥에 읽기 `Mock`(바이트 반환), 검증 `Mock`(참 반환), `uuid`로 만든 고유 `git_dir`, 시각을 둔다.
- 실행: `evaluate_condition({'op': 'artifact_valid', ...}, {}, {}, evaluation_context=context)`를 세 번.
- 단언: 세 번 모두 `'ready'`이고 읽기·검증 호출 수가 `(1, 1)`이다.
- 대역: `unittest.mock.Mock` 둘.

### `test_artifact_verdict_belongs_to_its_validator_and_needs_no_repository` (행 227–239)
- 성질: 산출물 판정은 검증기에 속하므로 검증기가 다르면 판정이 다르고, 저장소가 없어도(`git_dir=None`) 판정할 수 있다. 이때 바이트는 매번 대조하지만 검증기별 판정은 한 번만 계산한다.
- 준비: 읽기 `Mock`, 받아들이는 검증 `accept`와 거부하는 검증 `reject`.
- 실행: `accept`, `reject`, `accept`, `reject` 순서로 각각 `git_dir=None` 문맥에서 판정.
- 단언: 상태가 차례로 `'ready'`, `'evaluation_error'`, `'ready'`, `'evaluation_error'`. 호출 수가 읽기 4, `accept` 1, `reject` 1.
- 대역: `Mock` 셋.
- 비고: 주석은 "저장소가 없으면 바이트를 매번 대조하고, 판정은 각각 한 번 계산된다"고 적는다.

## ReadinessCopyTests (행 242–286)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다.

### `test_historical_judgment_cannot_override_changed_governance_or_sources` (행 243–262)
- 성질: 과거의 목표 판정은 원천이나 거버넌스 개정이 바뀐 뒤에는 과제 의무의 지정 판정으로 쓰일 수 없다.
- 준비: `domain_governance()`에 원천 하나와 과제 `TK-one`의 지식 `KN-one`을 둔다. 목표 판정 `GJ-one`은 만족, 현재, 의존 `KN-one`, 현재 거버넌스 개정, 현재 원천 근거를 가진다. `do_math.knowledge_records.usable_links`를 평가 하나를 돌려주도록 패치한다. 내부 함수 `judge()`는 판정자 `goal_audit`인 의무와 증거 `GJ-one`으로 `task_scope.designated_judgment`를 부른다.
- 실행: `judge()`. 원천 해시를 바꾸고 `judge()`. 원천을 되돌리고 판정의 `goal_revision`을 `'old-edition'`으로 바꾸고 `judge()`.
- 단언: 처음은 `'GJ-one'`, 나머지 둘은 `None`.
- 대역: `usable_links`의 `patch`.
- 비고: 함수 안에서 `governance_import`를 import하지만 쓰지 않는다. 클래스 이름의 "Copy"와 달리 이 시험은 복사를 다루지 않는다.

### `test_borrowed_inputs_and_copied_results_match_prior_evaluation` (행 264–286)
- 성질: `task_ready`는 인자를 바꾸지 않고, 사본으로 판정한 결과와 원본으로 판정한 결과가 같으며, 반환된 대기 목록을 고쳐도 과제의 대기 기록이 바뀌지 않는다.
- 준비: 네 시나리오마다 `approved_task()`의 깊은 사본. `waiting`은 외부 사건 대기를 달고, `missing`은 없는 입력 `SO-missing`을 더하고, `invalid`는 알 수 없는 조건 연산을 준다. `ready`는 그대로다.
- 실행: 인자의 깊은 사본으로 `task_ready`를 한 번, 원 인자로 한 번 부르고 결과를 깊게 복사한다. `waiting`이면 결과의 첫 대기 사유를 고친다.
- 단언: 두 결과가 같다. 인자가 호출 전 사본과 같다. `waiting`이면 과제의 `waiting`이 결과의 `waits`에 있고, 결과를 고쳐도 과제 대기의 `reason`이 `'wait'` 그대로다.
- 대역: 없음.
- 비고: `subTest(scenario=...)` 네 경우. 결과를 `deepcopy`한 뒤 고치므로, 마지막 단언은 반환값이 입력과 객체를 공유하는지를 직접 검사하지는 않는다.

## ReadinessConditionTests (행 289–364)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다.

### `test_required_certification_condition_tracks_current_identity_effect` (행 290–300)
- 성질: 지식의 `/usable_as_k` 조건은 신원 평가 사용의 현재 효력을 따르고, 값은 불리언이어야 한다.
- 준비: `verified_knowledge()`의 정리 `kid`. 조건은 `usable_as_k`가 참인지 본다.
- 실행: 판정, 모든 평가 사용을 `suspended`로 바꾸고 판정, 값을 1로 바꾸어 `validate_condition`.
- 단언: `'ready'`, `'not_ready'`, 그리고 `ValueError`(유형만).
- 대역: 없음.

### `test_documented_readiness_examples_match_the_live_grammar` (행 302–311)
- 성질: 문서 `references/과제-착수조건.md`의 JSON 예시는 모두 현재 조건 문법을 통과한다.
- 준비: 스킬 폴더의 문서를 읽어 `json` 코드 블록을 정규식으로 모은다.
- 실행: 블록마다 JSON을 읽어, `op`가 있으면 그 자체를, 없으면 `task_conditions`의 각 `occurrence_condition`을 `validate_condition`.
- 단언: 블록이 2개 이상이고 모든 검증이 예외 없이 끝난다.
- 대역: 없음.
- 비고: 실제 문서 파일을 읽는다.

### `test_readiness_document_tables_match_the_condition_grammar` (행 313–344)
- 성질: docstring은 "연산, 기록 가족과 그 공간, 포인터가 `planning`과 일치한다"고 말한다. 문서의 표와 문장이 제품의 `CONDITION_FIELDS`, `RECORD_FAMILIES`, `EXPOSED_FIELDS`와 같다.
- 준비: 문서의 Markdown 표를 첫 칸 머리 이름으로 모은다. 머리가 `` `op` ``인 표에서 연산과 필드를, "현재 기록 가족은 ... 이다." 문장에서 가족 목록을, "...의 space는 `runtime`" 문장에서 런타임 가족을, 머리가 `기록 가족`인 표에서 가족별 포인터를 읽는다.
- 실행: 문서 파싱과 비교.
- 단언: 문서의 연산 집합이 `CONDITION_FIELDS`의 키와 같고, 연산마다 제품 필드가 문서 필드의 부분집합이다(실패 메시지로 연산 이름). 문서 가족 집합이 `RECORD_FAMILIES`의 키와 같다. 런타임 가족과 나머지(연구 가족)가 제품의 공간 구분과 같다. 가족별 포인터 집합이 `EXPOSED_FIELDS`와 같다.
- 대역: 없음.
- 비고: 실제 문서 파일을 읽는다. 문서의 표 머리나 문장 형태가 바뀌면 파싱이 실패한다.

### `test_nonformal_research_reuse_is_ready_but_not_certified` (행 346–364)
- 성질: 비형식 연구 지식을 재사용하는 과제는, 그 지식이 형식 인증 기준(`assess_use`)으로는 유효하지 않아도 착수 가능하다. 지식이 철회되거나 사용이 정지되면 착수 불가가 된다.
- 준비: `approved_task()`에 활성 종류 정의 `KD-observation`을 두고 `create_candidate`로 관찰 지식 `KN-computation`을 만든다. 과제의 `reuse`를 그 지식으로 두고 다시 승인한다.
- 실행: `assess_use`, `task_ready`. 이어서 `lifecycle='withdrawn'`, `use_suspended=True`, `kind_use_suspended=True` 각각을 사본에 적용하고 다시 승인한 뒤 `task_ready`.
- 단언: `assess_use(...)['valid']`가 거짓, 착수 상태가 `'ready'`. 세 변경은 모두 `'not_ready'`(실패 메시지로 필드 이름).
- 대역: 없음.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈: `test_planning_engine`(계획의 엔진 경로), `test_task_contracts`(`TaskReadinessTests`에서 착수 가능성과 의존), `test_decision_basis`(계약 검토 현재성과 개정 대기), `test_revision_obligations`(배정 직전의 현재 입력 재판정). 조건 문법의 문서 대조는 이 모듈에만 있다.
- 픽스처 의존: `record_fixtures`의 `approved_task`, `approve_task`, `domain_governance`(그리고 쓰이지 않는 `governance_import` import); `knowledge_fixtures.verified_knowledge`.
- 이 모듈에만 있는 도우미: `PlanningTests.setUp`, `condition`, 시험 안의 내부 함수 `judge`.
- 겹치거나 보완하는 시험: 산출물 조건은 경로 문법(`PlanningTests`)과 읽기·검증 캐시(`ArtifactConditionTests`)로 나누어 본다. 형식 결과의 사용 정지가 조건에 반영되는 성질은 관계 조건(`test_relation_condition_rechecks_its_proof_after_import`)과 `usable_as_k` 조건(`test_required_certification_condition_tracks_current_identity_effect`)이 두 경로에서 본다.

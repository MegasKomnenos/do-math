# test_decision_basis

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_decision_basis.py` (211행) |
| 클래스 / 테스트 | 1 / 13 |
| 시험 대상 제품 코드 | `do_math/input_basis.py`의 `capture_decision_basis`, `decision_basis_changes`; `do_math/integration.py`의 `apply_bundles`; `do_math/decision_engine.py`의 `DecisionEngineMixin._apply_action_resolutions`, `_refresh_changed_decision`; `do_math/engine.py`의 `ResearchEngine._submission_repair_context`; `do_math/planning.py`의 `seal_contract_review`, `contract_review_current`, `revision_waits`, `revision_cycles`; `do_math/revisions.py`의 `capture_targets`, `submission_errors`, `dependency_cycles`; `do_math/knowledge_records.py`의 `create_candidate`; 간접으로 `do_math/submission.py`의 `action_resolution_errors` |
| 사용하는 픽스처 모듈 | `research_fixtures`(`approved_governance`, `bare_engine`, `candidate`, `contract_review`, `charter_record`) |
| 격리 표지 | 없음 |
| 시작 상태 | 1단(사전 상태에 순수 함수)과, `bare_engine`으로 만든 실제 엔진 객체에 최소 사전 상태를 싣고 결정 믹스인 메서드를 직접 부르는 방식이 섞여 있다. 저장소·Git·엔진 루프는 쓰지 않는다 |

## 목적

이 모듈에는 docstring이 없다. 모듈 이름과 시험이 가리키는 계약은 결정 근거(decision basis)다. AI의 판단(계획, 검토, 개정 등)은 그 판단이 기댄 기록의 상태를 근거로 봉인하고, 적용 직전에 근거가 여전히 현재인지 다시 확인한다. 제품의 `input_basis.capture_decision_basis`는 과제의 계약 해시와 결과 접두 해시, 지식의 내용 해시와 사용 상태를 모으고, `decision_basis_changes`는 그 가운데 바뀐 필드를 보고한다. 이 모듈은 다음을 본다.

- 무엇이 내용 변경이고 무엇이 장부(bookkeeping) 변경인가. 과제의 상태·검토·보류 사유와 뒤에 붙은 결과는 장부이고, 계약 변경·결과의 수정과 삭제·지식 해설의 교체는 내용 변경이다.
- 계약 검토 승인은 외부 전제(입력 과제)의 내용이 바뀌면 무효가 된다.
- 실패한 작업을 현재 판단으로 해결하는 선언(`action_resolutions`)은 검증된 묶음과 함께만 커밋되고 같은 판단 범위여야 한다.
- 개정 대기의 규칙: 대기 중인 개정은 의존자만 막고, 시작하지 않은 개정자끼리는 오래된 것부터 빠지며, 실패한 개정자는 진단을 막지 않는다.
- 개정 제출은 선언된 대상마다 명시 처분을 요구하고, 같은 과제의 교체 후보는 하나뿐이다.
- 전제 변경으로 새로 고친 작업은 새로 고쳐진 실행을 잇는다.

## 모듈 수준 요소

- 행 6: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리.
- 행 210–211: 직접 실행하면 `unittest.main()`.

## BasisTests (행 13–207)

`unittest.TestCase`를 그대로 상속한다. 클래스 표지, 클래스 속성, 도우미 메서드가 없다.

- `setUp` (행 77–83): 두 시험 뒤에 정의되어 있지만 클래스의 모든 시험 앞에 돈다. 주석은 "명시적 합성 승인은 이 도메인 수준 시험의 입력이다. 엔진 수명 주기나 활성화 증거는 주입하지 않는다"고 적는다. `charter_record("Preserve approved task premises")`를 `approved_governance`로 채택한 인스턴스(원천 `UI-basis-fixture`, 승인 `DC-basis-fixture`, 빈 `knowledge`·`sources`)를 `self.instance`로 둔다. `self.runtime`에는 과제 `A` 하나가 있다. `A`는 `candidate("A")`에 `id="A"`, `revision=1`, `question="original"`, `status="planned"`, 결과 `[{"report": "first"}]`, 빈 `inputs`를 준 것이다. 빈 큐·실행·대기 작업도 둔다. 앞의 두 시험(`test_current_resolution_*`)과 `test_premise_refresh_of_an_output_repair_continues_the_refreshed_execution`은 이 상태를 쓰지 않고 자기 엔진을 만든다.

### `test_current_resolution_commits_only_with_its_complete_bundle` (행 14–47)
- 성질: 현재 실행이 자기 판단으로 실패 작업을 해결하는 선언은 그 실행의 통합 묶음이 검증과 출판을 모두 통과해야만 커밋되고, 뒤 단계가 실패하면 입력 상태는 그대로이며, 같은 묶음을 다시 적용해도 이력이 늘지 않는다.
- 준비: `bare_engine()`. 연구 계획 작업 `AC-current`(대상 `A`)와 빈 판단을 담은 계획 출력. 문맥은 실행 `EX-current`와 40자 스냅숏. 해결 선언은 실패 작업 `AC-failed`를 `evidence_execution_id='current'`로 해결한다. 런타임에는 `AC-failed`의 `execution_failure` 대기(같은 역할·대상)와, 확장에 이 선언을 담은 실행 `EX-current`가 있다. 내부 함수 `apply`는 후보 상태를 엔진에 싣고 `owner._apply_action_resolutions('EX-current', accepting_current=True)`를 부른다. 내부 함수 `run`은 `integration.apply_bundles`에 `apply_bundle=apply`, 항상 통과하는 `validate_current`, 인자로 받은 `validate_candidate`와 `publish`를 넘긴다.
- 실행: `run`을 네 번. (1) 후보 검증이 `ValueError('later candidate failure')`를 던진다. (2) 출판이 `OSError('Git publication failed')`를 던진다. (3) 모두 통과. (4) (3)의 결과 런타임으로 다시 모두 통과.
- 단언: (1)(2)의 `status`가 `'returned'`이고 그때마다 입력 런타임이 적용 전 사본과 같다. (3)의 `status`가 `'accepted'`, 결과 런타임의 `waiting_actions`가 `{}`, 이력이 1행이다. (4)의 결과 이력이 (3)과 같다.
- 대역: 콜백 람다들(`validate_current`, `validate_candidate`, `publish`). 예외는 생성기 식 `(_ for _ in ()).throw(...)`로 던진다.
- 비고: (4)에서 제품의 `apply_bundles`는 같은 통합 ID와 같은 내용 해시의 영수증을 보고 그 묶음을 `already_accepted`로 건너뛴다. 이 시험은 이력이 같다는 결과만 단언한다.

### `test_current_resolution_requires_its_validated_bundle_and_same_scope` (행 49–75)
- 성질: 해결 선언의 증거 실행은 받아들여진 실행이거나, 적용 중인 현재 실행이어야 하고, 실패 작업과 같은 판단 범위(같은 대상 등)여야 한다. 거부되면 상태가 바뀌지 않는다.
- 준비: 네 경우마다 `bare_engine({})`에 `AC-failed`의 `execution_failure` 대기(연구 계획, 대상 `A`), 확장에 선언을 담은 `EX-current`(대상은 경우마다 다름), 받아들여지지 않은 `EX-other`(대상 `A`)를 둔다.
- 실행: `owner._apply_action_resolutions('EX-current', accepting_current=...)`. 네 경우는 (현재 적용 여부, 증거, `EX-current`의 대상, 허용)이 `(False, 'current', 'A', 거부)`, `(True, 'current', 'A', 허용)`, `(True, 'current', 'B', 거부)`, `(True, 'EX-other', 'A', 거부)`다.
- 단언: 허용이면 `waiting_actions`가 `{}`이고 첫 이력 행의 `resolved_by`가 `'EX-current'`다. 거부면 `ValueError`이고 메시지가 `'same judgment scope'`에 맞으며, 런타임이 사본과 같다.
- 대역: 없음.
- 비고: `subTest(accepting=..., evidence=..., target=...)` 네 경우. 주석은 "받아들여지지 않은 증거와 다른 대상 모두 같은 범위 규칙에서 실패한다"고 적는다. 제품 메시지는 받아들여지지 않은 증거의 경우 `"resolution evidence must be an accepted execution of the same judgment scope"`, 대상이 다른 경우 `submission.action_resolution_errors`의 `"resolution evidence must be an execution of the same judgment scope as the failed action"`이다. 정규식은 두 메시지에 모두 맞는다.

### `test_task_bookkeeping_and_appended_results_are_not_content_changes` (행 85–94)
- 성질: 과제의 상태·검토·보류 사유 변경과 결과 추가는 결정 근거의 변경이 아니고, 이미 있던 결과의 수정은 변경이다.
- 준비: `setUp`의 상태. `capture_decision_basis(instance, runtime, ["A"])`로 근거를 뜬다.
- 실행: `A`를 `active`로, 승인 검토와 `deferred_reason="later"`를 더하고 결과 하나를 덧붙인 뒤 `decision_basis_changes`. `status="completed"`로 바꾸고 다시. 첫 결과의 `report`를 `"changed"`로 바꾸고 다시.
- 단언: 앞의 두 번은 `[]`. 마지막은 첫 변경 행의 `field`가 `"results_sha256"`다.
- 대역: 없음.
- 비고: 제품은 근거를 뜰 때의 결과 개수만큼의 접두를 해시하므로, 뒤에 붙은 결과는 변경으로 보지 않는다.

### `test_task_contract_change_and_result_removal_are_detected` (행 96–99)
- 성질: 과제 계약의 변경과 결과의 삭제는 결정 근거의 변경으로 탐지된다.
- 준비: `setUp`의 상태와 `A`의 근거.
- 실행: `A`의 `question`을 `"different"`로, `results`를 `[]`로 바꾸고 `decision_basis_changes`.
- 단언: 변경 행의 `field` 집합이 `{"contract_sha256", "results_sha256"}`이다.
- 대역: 없음.

### `test_split_knowledge_bookkeeping_is_stable_but_authored_reference_change_is_detected` (행 101–111)
- 성질: 지식 기록의 검토 장부(검토 주기 ID, 이력)는 근거를 바꾸지 않고, 작성된 참조(해설 ID)의 교체는 내용 해시 변경으로 탐지된다.
- 준비: `setUp`의 상태에 `create_candidate`로 관찰 후보 `K`를 만든다(원천 `explicit-fixture`, 행위자 `fixture-producer`). 그 근거를 뜬다.
- 실행: 기록에 `review_cycle_id="RC-new"`와 행정 이력 한 행을 달고 `decision_basis_changes`. 이어서 `exposition_id`를 `'XP-replaced'`로 바꾸고 다시.
- 단언: 첫 결과가 `[]`. 둘째 결과의 `field` 집합에 `'content_sha256'`이 있다.
- 대역: 없음.
- 비고: 이름의 "split knowledge"가 무엇을 가리키는지 밝힌 주석은 원문에 없다. 시험이 바꾸는 필드는 `review_cycle_id`, `history`, `exposition_id` 셋이다.

### `test_a_previous_approval_is_invalid_after_its_external_premise_changes` (행 113–122)
- 성질: 과제 계약 검토 승인은 그 과제가 입력으로 읽는 다른 과제의 내용이 바뀌면 무효가 되고, 그 과제의 장부 변경으로는 무효가 되지 않는다.
- 준비: `setUp`의 상태에 `A`를 입력으로 읽는 과제 `B`를 더한다. `planning.seal_contract_review(task, contract_review({"task": task}), ..., execution_id="EX-independent-review")`로 승인 검토를 봉인한다.
- 실행: `planning.contract_review_current(review, task, instance, runtime)`를 세 번. 처음, `A`에 `deferred_reason="bookkeeping"`을 단 뒤, `A`의 `question`을 `"new premise"`로 바꾼 뒤.
- 단언: 앞의 두 번은 `["valid"]`가 참, 마지막은 거짓이다.
- 대역: 없음.

### `test_pending_revision_blocks_dependents_but_not_independent_or_delegated_work` (행 124–134)
- 성질: 큐에 있는 개정은 개정 대상을 읽는 과제의 작업만 막고, 독립 과제의 작업과, 그 개정을 스스로 위임받은 과제의 검토는 막지 않는다.
- 준비: `setUp`의 상태에 `A`를 읽는 `B`, 입력 없는 `C`를 더한다. `A`를 개정 대상으로 한 준비 작업 `write`를 큐에 둔다.
- 실행: `B-work`와 `C-work`(둘 다 `research_work`)에 `planning.revision_waits`. 이어서 후보 지식 `K`, `K`를 입력과 지식 개정 대상으로 갖고 `revision_request_action_id="write-K"`인 과제 `D`, `K`를 개정 대상으로 한 준비 작업 `write-K`를 더하고 `D-review`(`task_contract_review`, 대상 `D`)를 판정한다.
- 단언: `B-work`의 대기가 참, `C-work`는 거짓, `D-review`는 거짓이다.
- 대역: 없음.
- 비고: 제품의 `revision_waits`는 작업 대상 과제의 `revision_request_action_id`를 소유자로 보고, 소유자의 개정 대상 가운데 그 과제가 떠안은 것을 겹침에서 뺀다.

### `test_unstarted_writers_reading_each_others_targets_drain_oldest_first` (행 136–153)
- 성질: 서로의 대상을 읽는 시작 전 개정자들은 ID가 오래된 것부터 빠져 교착이 없고, 실행 중인 개정자가 생기면 두 방향 대기가 생겨도 대기 순환은 없다.
- 준비: `setUp`의 상태에서 `A`와 `B`가 서로를 입력으로 읽게 한다. 개정자 셋: `AC-1`(대상 `A`), `AC-2`(대상 `B`), `AC-3`(대상 `A`와 `B`). 큐 순서는 `[AC-2, AC-3, AC-1]`이다.
- 실행: 각 개정자에 `revision_waits`, `planning.revision_cycles`, `A-work`(`research_work`, 대상 `A`)에 `revision_waits`. 이어서 `AC-2`를 실행 `E`로 `running`에 두고 `AC-1`을 다시 판정하고 순환을 본다.
- 단언: `AC-1`의 대기가 `[]`. `AC-2`의 대기 작업 ID가 `["AC-1"]`. `AC-3`의 대기 작업 ID를 정렬하면 `["AC-1", "AC-2"]`. 순환이 `[]`. `A-work`의 대기가 참. `AC-2`가 실행 중이면 `AC-1`의 대기 가운데 작업 대기의 ID가 `["AC-2"]`, 실행 대기의 ID가 `["E"]`이고, 순환은 여전히 `[]`이다.
- 대역: 없음.
- 비고: 큐 순서와 무관하게 ID 순서(`AC-1` < `AC-2` < `AC-3`)가 대기 방향을 정한다. 제품 주석("Unstarted writers drain oldest first. A declared writer waits only for older ones, so writers reading each other's targets cannot deadlock.")과 시험 주석("실행 중인 개정자는 아무것도 기다리지 않으므로 두 개정자의 상호 읽기는 대기 순환을 만들지 않는다")이 같은 규칙을 말한다.

### `test_writer_drains_a_running_plan_but_failed_writer_does_not_block_diagnosis` (행 155–161)
- 성질: 개정자는 실행 중인 연구 계획이 끝날 때까지 기다리지만, 실패해 대기 중인 개정자는 다음 연구 계획을 막지 않는다.
- 준비: `setUp`의 상태에 `A`를 개정 대상으로 한 준비 작업 `write`와, 실행 중인 연구 계획 실행 `E`.
- 실행: `write`에 `revision_waits`. `E`를 끝내고 `write`를 `execution_failure` 대기로 둔 뒤 `next-plan`(`research_plan`)에 `revision_waits`.
- 단언: 앞은 참, 뒤는 거짓이다.
- 대역: 없음.
- 비고: 제품 주석은 "진단과 계획이 실패한 개정을 풀 수 있다. 새 전역 계획은 살아 있는 개정자만 막는다"고 적는다.

### `test_declared_revision_requires_an_explicit_resolution` (행 163–169)
- 성질: 필수로 선언된 개정 대상은 명시 처분이 있어야 하고, `unchanged`로 취소할 수 없으며, `deferred`는 받아들여진다.
- 준비: `A`를 개정 1·필수로 선언한 준비 작업 문맥.
- 실행: `revisions.submission_errors({"candidates": []}, ...)`를 세 확장으로. 빈 확장, `A`를 `unchanged`로 처분한 확장, `deferred`로 바꾼 확장.
- 단언: 앞의 두 번은 오류가 참(비어 있지 않음), 마지막은 `[]`. 메시지는 고정하지 않는다.
- 대역: 없음.
- 비고: `test_revision_obligations`의 `test_revision_cannot_omit_target_or_cancel_required_repair_as_unchanged`와 겹친다. 그 시험은 허용 경로로 `revised`와 교체 후보를, 이 시험은 `deferred`를 본다.

### `test_dependency_cycles_are_reported_with_the_actual_edges` (행 171–172)
- 성질: 과제 의존 순환은 실제 간선 순서로 보고된다.
- 준비: `A`→`B`, `B`→`A`로 의존하는 두 과제 사전.
- 실행: `revisions.dependency_cycles(...)`.
- 단언: 결과가 `[["A", "B", "A"]]`이다.
- 대역: 없음.
- 비고: `setUp`의 상태는 쓰지 않는다.

### `test_revision_response_rejects_distinct_titles_for_the_same_existing_task` (행 174–184)
- 성질: 한 응답에서 같은 기존 과제를 고치는 후보는 제목이 달라도 하나뿐이어야 한다.
- 준비: `A`를 개정 대상으로 선언한 문맥과 `A`의 `revised` 처분. 출력에는 `A`를 고치는 후보 `First`, `Second` 둘.
- 실행: `revisions.submission_errors(output, extension, context)`, 이어서 `Second`의 `revises_task_id`를 `None`으로 바꾸고 다시.
- 단언: 첫 결과에 메시지에 `"one replacement candidate"`가 든 오류가 있다(실패 메시지로 오류 목록을 보인다). 둘째 결과는 `[]`.
- 대역: 없음.

### `test_premise_refresh_of_an_output_repair_continues_the_refreshed_execution` (행 186–207)
- 성질: 출력 수리 작업이 전제 변경으로 새로 고쳐지면, 새 작업은 수리 원본이 아니라 새로 고쳐진 실행을 잇고, 옛 제출 문제를 물려받지 않으며, 그 실행 계보에서 받아들여진 응답을 물려받는다.
- 준비: 주석은 "`EX-second`는 `EX-first`의 출력 수리이며, 다른 묶음이 바뀐 전제로 돌아오기 전에 응답 묶음이 받아들여졌다. 새로 고침은 `EX-second`를 잇는다"고 적는다. 수리 기록(`EX-first`, 옛 문제 `IS-old`)을 가진 보충 연구 작업 `AC-repair`(`continuation_of='EX-first'`, `repair_attempt=1`). 받아들여진 통합 영수증 `IN-report`(`EX-second`, 응답 해시 `'a'*64`). 이 상태로 `bare_engine`을 만든다.
- 실행: `owner._refresh_changed_decision(action, 'EX-second', [{'field': 'integration_currentness'}])`, 큐의 첫 작업을 새 작업으로 읽고 `owner._submission_repair_context({}, refreshed)`.
- 단언: 새 작업의 `refresh['execution_id']`와 `continuation_of`가 모두 `'EX-second'`이고 `repair` 키가 없다. 문맥의 `submission_failures`가 `[]`, `accepted_integration_ids`가 `['IN-report']`, `accepted_response`가 `{'integration_id': 'IN-report', 'response_sha256': 'a'*64}`이다.
- 대역: 없음.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈: `revision_waits`, `capture_targets`, `submission_errors`는 `test_revision_obligations`와 겹친다. `revision_waits`의 관계 경유 판정은 `test_relation_dependencies`가 본다. 계약 검토의 현재성은 `test_planning`과 `test_task_contracts`도 다룬다.
- 픽스처 의존: `research_fixtures`의 `approved_governance`, `charter_record`, `candidate`, `contract_review`, `bare_engine`.
- 이 모듈에만 있는 도우미: `BasisTests.setUp`, 첫 시험 안의 내부 함수 `apply`와 `run`.
- 겹치거나 보완하는 시험: 해결 선언은 첫 시험이 통합 묶음 경로로, 둘째 시험이 믹스인 직접 호출로 본다. 결정 근거의 현재성은 과제(두 시험), 지식(한 시험), 계약 검토(한 시험)로 나누어 본다.

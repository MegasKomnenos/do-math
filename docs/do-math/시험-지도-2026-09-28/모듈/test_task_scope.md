# test_task_scope

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_task_scope.py` (190행) |
| 클래스 / 테스트 | 3 / 8 |
| 시험 대상 제품 코드 | `do_math/task_scope.py`의 `apply_task_dispositions`(안에서 `_validate`), `validate_withdrawal_scope`; `do_math/engine.py`의 `ResearchEngine._apply_extensions`; `do_math/submission.py`의 `payload_issues`; `do_math/planning.py`의 `contract_hash`; `do_math/knowledge.py`의 `revision_roots`, `plan_impact`, `revise_knowledge`, `assess_use`; `do_math/knowledge_io.py`의 `import_candidate`; `do_math/knowledge_records.py`의 `proposal_view` |
| 사용하는 픽스처 모듈 | `record_fixtures`(`task_contract`, `withdrawable_task`, `withdraw_prepared`), `research_fixtures`(`bare_engine`, 함수 안에서 import하는 `seal_response`), `runner_fixtures`(함수 안에서 import하는 `common`) |
| 격리 표지 | 없음 |
| 시작 상태 | 대부분 1단(사전 상태에 순수 함수). `EngineIntegrationTest`는 `bare_engine`으로 만든 실제 엔진 객체에 저장소 대역을 붙인다. 제출 검사 시험은 임시 작업 폴더에 확장 파일을 쓴다 |

## 목적

모듈 docstring은 "AI가 준비한 과제의 자율 철회(withdrawal)에 대한 회귀 시험"이라고 밝힌다. 연구 준비(`research_preparation`)나 연구 계획(`research_plan`) 실행은 확장 `task_dispositions`에 `withdraw` 처분을 제출해, AI가 준비한 과제를 사용자 결정 없이 닫을 수 있다. 제품의 `task_scope.apply_task_dispositions`는 docstring에서 "스냅숏과 출처 검증 뒤에 철회 요청을 적용한다. 목표, 정책, 허가, 학술 요건, 사용자 과제 범위 기록은 바꿀 수 없다"고 밝힌다. 이 모듈은 다음을 본다.

- 철회는 계약을 보존하고 과제를 `closed`로 바꾸며, 시작 전 작업만 취소한다.
- 철회를 허가한 실행 하나만 "살아 있는 실행" 검사에서 빠진다.
- 스냅숏이 바뀌었거나, 사용자·학술 과제이거나, 살아 있는 실행이 있거나, 이미 끝난 과제는 철회할 수 없다. 종결 평가도 철회로 이어질 수 없다.
- 제출 검사는 `withdraw`가 아닌 처분과 중복 대상을 거부한다.
- 부분 결과가 있는 과제는 항목별 처분 없이 철회할 수 없고, 거부되면 결과를 보존한다.
- 엔진의 확장 적용 경로가 철회를 실제로 적용한다.

마지막 클래스 `SourceCorrectionTest`는 철회와 다른 주제로, 같은 원천 바이트에서 잘못 읽은 지식을 개정하는 경로를 본다.

## 모듈 수준 요소

- 행 7–8: 시험 폴더(`tests/`)와 스킬의 `scripts/` 폴더를 차례로 `sys.path` 앞에 넣는다. 다른 모듈과 달리 시험 폴더를 명시적으로 넣는 줄이 하나 더 있다.
- 행 189–190: 직접 실행하면 `unittest.main(verbosity=2)`.

## EngineIntegrationTest (행 15–42)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다.

### `test_engine_applies_task_disposition_extension` (행 16–42)
- 성질: docstring은 "계획 확장이 적격한 과제를 `task_scope`를 통해 닫는다"고 말한다. 엔진의 `_apply_extensions`는 계획 실행의 `task_dispositions`를 실행 입력 스냅숏의 과제와 대조해 적용한다.
- 준비: `bare_engine()`으로 만든 엔진에 빈 인스턴스와 런타임을 싣는다. 과제는 `task_contract()`를 `TK-AI`, `producer_execution='EX-prep'`, 빈 결과·검토로 바꾼 것이다. 끝난 준비 실행 `EX-prep`을 둔다. `engine.head='fixed-input'`. 저장소를 `create_autospec(ResearchRepository, instance=True)`로 바꾸고, `store.view`의 부수 효과가 `('fixed-input', {}, deepcopy(engine.runtime))`를 돌려주게 한다(주석: 엔진은 계획자의 고정 입력 스냅숏을 복사 없이 `ResearchRepository.view`로 읽는다). 끝난 계획 실행 `EX-plan`의 `input_snapshot`을 머리로 두고, 확장에 `TK-AI`의 `withdraw` 처분을 둔다.
- 실행: `engine._apply_extensions({"role": "research_plan"}, "EX-plan")`.
- 단언: 엔진 런타임에서 `TK-AI`의 `status`가 `"closed"`다.
- 대역: `ResearchRepository`의 `create_autospec` 대역과 `view`의 부수 효과.
- 비고: `view`의 부수 효과는 호출 시점의 `engine.runtime` 사본을 돌려주므로 입력 스냅숏과 현재 런타임이 같다.

## TaskScopeTests (행 45–148)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 클래스 도우미가 없다. 대부분의 시험은 `record_fixtures.withdrawable_task()`에서 시작한다. 이 픽스처는 `(instance, runtime, input_tasks)`를 돌려준다. 과제 `TK-AI`(개정 3, `planned`, 생산 실행 `EX-prep`, 승인 검토 하나), 그것에 의존하는 `TK-dependent`(`waiting`), 끝난 준비 실행 `EX-prep`, 큐의 `AC-review`(대상 `TK-AI`)와 `AC-other`(대상 없음), 대기 작업 `AC-work`(대상 `TK-AI`)가 있다. `withdraw_prepared(runtime, snapshot)`은 `apply_task_dispositions({}, runtime, [TK-AI withdraw], execution_id="EX-plan", input_tasks=snapshot)`이다.

### `test_withdrawal_preserves_contract_and_cancels_only_prestart_actions` (행 46–62)
- 성질: 철회는 과제를 닫되 계약·검토를 보존하고, 철회 기록에 이전 개정·계약 해시·취소된 큐와 대기 작업을 남기며, 의존 과제를 건드리지 않고 입력 런타임을 바꾸지 않는다.
- 준비: `withdrawable_task()`.
- 실행: `withdraw_prepared(runtime, snapshot)`.
- 단언: 바뀐 런타임에서 `TK-AI`의 `status`가 `"closed"`, `completion_obligations`가 스냅숏과 같고, `reviews`가 `[{"decision": "approved"}]`, `assessment` 키가 없다. `scope_disposition`의 `actor_execution`이 `"EX-plan"`, `previous_revision`이 3, `previous_contract_sha256`이 스냅숏 과제의 `contract_hash`, `cancelled_queue_actions`와 `cancelled_waiting_actions`가 참(비어 있지 않음)이다. 바뀐 런타임에 `task_readiness` 키가 없고, `TK-dependent`는 `"waiting"` 그대로다. 입력 런타임의 `TK-AI`는 여전히 `"planned"`다.
- 대역: 없음.
- 비고: 이름의 "only prestart actions"에 대해 이 시험은 취소 목록이 비어 있지 않음만 본다. 대상 없는 `AC-other`가 큐에 남는다는 사실이나 취소 목록의 정확한 내용은 단언하지 않는다. `task_readiness`는 입력 런타임에도 없으므로 그 단언은 함수가 그 키를 새로 만들지 않음을 본다.

### `test_selected_unstarted_withdrawal_excludes_only_its_authorizing_execution` (행 64–77)
- 성질: 살아 있는 실행 검사에서 제외되는 것은 철회를 제출한 실행(ID가 `execution_id`이고 계획 역할인 것) 하나뿐이다.
- 준비: `withdrawable_task()`에서 `TK-AI`를 `active`로 바꾸고, `EX-plan`을 `research_preparation` 역할, `stopping` 상태, 대상 `TK-AI`인 실행으로 둔다.
- 실행: (1) `withdraw_prepared`. (2) `EX-plan`을 복제한 `EX-other`를 더하고 다시 부른다. (3) `EX-other`를 지우고 `EX-plan`의 역할을 `research_work`로 바꾸고 다시 부른다.
- 단언: (1) `TK-AI`가 `closed`가 된다. (2)와 (3)은 `ValueError`이고 메시지가 정규식 `'live execution'`에 맞는다.
- 대역: 없음.
- 비고: (3)은 ID가 같아도 역할이 계획 역할(`execution_profiles.PLANNING_ROLES`: `research_preparation`, `research_plan`)이 아니면 제외되지 않음을 보인다. `stopping` 상태도 끝나지 않은 실행으로 센다.

### `test_terminal_assessment_cannot_withdraw_even_without_results` (행 79–85)
- 성질: 결과가 없는 과제라도 제안된 평가가 종결(`completed`, `closed`)이면 철회 범위 검사가 거부한다.
- 준비: `withdrawable_task()`.
- 실행: 두 결정마다 `task_scope.validate_withdrawal_scope(task, snapshot_task, proposed_assessment={'decision': decision})`.
- 단언: `ValueError`이고 메시지가 `'terminal'`에 맞는다. 제품 메시지는 `"withdrawal cannot follow a terminal task assessment"`다.
- 대역: 없음.
- 비고: `subTest(decision=...)` 두 경우.

### `test_rejects_changed_snapshot_user_or_academic_task_and_live_or_terminal_task` (행 87–101)
- 성질: 스냅숏 이후 계약이 바뀐 과제, 준비 실행이 만들지 않은 과제, 학술 요건 과제, 살아 있는 실행이 있는 과제, 이미 끝난 과제는 철회되지 않는다.
- 준비: 변형마다 새 `withdrawable_task()`에 변형 하나를 적용한다. 변형은 일곱 가지다. (1) 스냅숏 과제의 `question`을 `"new"`로. (2) `producer_execution`을 없는 실행 `EX-user`로. (3) `academic_requirement_id="writeup"`. (4) `research_work` 실행 `EX`가 `TK-AI`를 대상으로 `running`. (5) `task_contract_review` 실행이 같은 조건으로 `running`. (6) 과제 `status="completed"`. (7) `status="closed"`.
- 실행: 변형마다 `withdraw_prepared(runtime, snapshot)`.
- 단언: 모두 `ValueError`. 예외 유형만 보고 메시지는 고정하지 않는다. 제품 경로에서는 (1)(3) `"task contract changed since the execution input snapshot"`, (2) `"task is not attributable to a research preparation execution"`, (4)(5) `"task has a live execution"`, (6)(7) `"withdrawal requires an unfinished task"`가 해당한다.
- 대역: 없음.
- 비고: `subTest(mutation=...)` 일곱 경우. 이름의 "user ... task"는 (2)의 `producer_execution="EX-user"` 변형이다. 이 실행은 런타임에 없으므로 "준비 실행에 귀속되지 않음"으로 거부된다. `user_required` 필드로 사용자 과제를 표시하는 경로는 쓰지 않는다. (3)은 이름의 "academic task"를 가리키지만, `academic_requirement_id`가 `planning.CONTRACT_FIELDS`에 들어 있어 런타임 과제에만 이 필드를 더하면 계약 해시가 스냅숏과 달라진다. 그래서 `_validate`의 첫 검사인 스냅숏 대조에서 거부되고, `validate_withdrawal_scope`의 보호 의무 분기(`"protected obligations require authoritative item dispositions"`)에는 닿지 않는다. 이 모듈의 어느 시험도 그 분기를 고정하지 않는다.

### `test_submission_rejects_nonwithdraw_and_duplicate_requests` (행 103–133)
- 성질: docstring은 "봉인된 확장 스키마와 제출 검사가 처분의 모양과 대상의 구별을 맡는다"고 말한다. 제출 단계에서 `withdraw`가 아닌 처분과 같은 대상의 중복 처분이 거부된다.
- 준비: `task_contract()`를 `TK-AI`(`planned`, `EX-prep`, 빈 결과·검토)로 바꾼 과제. 고정 입력 문맥에는 이 과제를 `content_sha256`(`knowledge.content_hash`)과 함께 둔다(주석: 처분은 기존 과제를 고치므로, 엔진의 과제 보기처럼 고정 입력이 과제와 그 내용 해시를 공급한다). 내부 함수 `issues(dispositions)`는 임시 폴더에 `activity-extensions.json`을 `canonical_json`으로 쓰고, `runner_fixtures.common("research_preparation")` 출력에 `research_fixtures.seal_response`로 봉인 좌표를 단 뒤 `payload_issues(output, schema_for("research_preparation"), context, extensions, workspace)`를 돌려준다.
- 실행: `issues`를 두 번. (1) `disposition="revise"` 하나. (2) 같은 `TK-AI`의 `withdraw` 두 개.
- 단언: (1)의 오류 가운데 경로가 `activity-extensions.json/task_dispositions/0/disposition`인 것이 있다. (2)의 오류 가운데 경로가 `activity-extensions.json/task_dispositions`이고 메시지에 `"distinct targets"`가 든 것이 있다.
- 대역: 없음. 실제 파일 시스템의 임시 폴더를 쓴다.
- 비고: (1)은 스키마 검사, (2)는 `submission.py`의 "entries must identify distinct targets" 검사에서 난다.

### `test_partial_work_requires_item_disposition_and_preserves_results_on_rejection` (행 135–148)
- 성질: 부분 결과가 돌아온 과제는 항목별 처분 없이 철회할 수 없고, 거부되면 과제와 실행 기록이 바뀌지 않는다.
- 준비: `withdrawable_task()`에서 `TK-AI`를 `waiting`, 결과 `R-partial`(`outcome="partial"`)로 바꾸고, 끝난 작업 실행 `EX-work`(`outcome="output_accepted"`)를 둔다. 스냅숏의 `TK-AI`도 `waiting`으로 맞춘다.
- 실행: `withdraw_prepared(runtime, snapshot)`.
- 단언: `ValueError`이고 메시지가 `'item dispositions'`에 맞는다. 이어서 입력 런타임의 과제 `status`가 `"waiting"`, `results`가 원래 목록, `EX-work`의 `outcome`이 `"output_accepted"`다.
- 대역: 없음.
- 비고: 과제에 평가가 없으므로 `validate_withdrawal_scope`의 `"performed obligations need current item dispositions for all returned work"`에서 거부된다. 결과 보존은 `apply_task_dispositions`가 입력의 깊은 사본에서 일하기 때문이다.

## SourceCorrectionTest (행 151–186)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다.

### `test_same_source_bytes_can_revise_a_misread_claim_and_suspend_dependents` (행 152–186)
- 성질: docstring은 "바로잡은 읽기는 지식을 바꾸지 불변 원천 바이트를 바꾸지 않는다"고 말한다. 같은 원천에서 잘못 읽은 주장을 개정하면 옛 지식은 대체되고 새 지식이 생기며, 그 위에 선 의존 지식은 사용할 수 없게 되고 재평가 요구가 이력에 남는다.
- 준비: `SimpleNamespace`로 만든 상태 그릇 `engine`(실제 엔진이 아니다)에 원천 `SO-paper`(`sha256`은 `'a'*64`)를 둔다. 두 후보 `KN-reading`(진술 "The paper prints m/n.")과 그것에 의존하는 `KN-dependent`를 `knowledge_io.import_candidate`로 `observation` 종류로 들인다. 후보 사전의 `statement`, `explanation`, `summary`, `lean_code`, `declaration_names`, `dependencies`만 넘기고, 의존은 앞서 받은 ID로 바꾼다.
- 실행: `knowledge.revision_roots`로 뿌리를 구하고 `plan_impact(..., roots, [])`로 영향을 계산한 뒤, `knowledge.revise_knowledge(..., changes, reason=..., actor_ref='EX-correction', declared_impact=impact['computed_impact'])`로 진술을 "The paper prints n/m."으로 바꾼다.
- 단언: 원천의 `sha256`이 여전히 `'a'*64`. 옛 지식의 `lifecycle`이 `'superseded'`이고 `proposal_view`의 진술이 옛 문장이다. `supersedes`가 옛 ID인 새 지식의 진술이 새 문장이다. 의존 지식에 `knowledge.assess_use(...)['valid']`가 거짓이다. 이력의 첫 `knowledge_reassessment_required` 행의 `affected_ids`에 의존 지식 ID가 있다.
- 대역: 없음. 엔진 대신 `SimpleNamespace` 그릇을 쓴다.
- 비고: 후보 사전에 적힌 `id`, `revision`, `status`, `reviews`, `source_basis` 필드는 `import_candidate`에 넘기지 않으므로 시험 결과에 영향이 없다. 이 클래스는 과제 철회와 무관한 지식 개정 경로를 본다.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈: 원문에 `task_dispositions`가 나오는 시험 모듈은 이 모듈 밖에 `test_task_completion`, `test_integration_bundles`, `test_model_assessment_flow`, `test_design_walkthroughs`가 있다. `withdrawable_task` 픽스처는 이 모듈과 `test_task_completion`이 함께 쓴다. 과제 평가와 항목별 처분(`apply_task_assessments`)은 `test_task_contracts`가 본다. 지식 개정(`revise_knowledge`)은 `test_knowledge`, `test_knowledge_io`, `test_knowledge_storage`, `test_submission_boundaries`, `test_design_walkthroughs`에서도 불린다.
- 픽스처 의존: `record_fixtures.withdrawable_task`, `withdraw_prepared`, `task_contract`; `research_fixtures.bare_engine`, `seal_response`; `runner_fixtures.common`.
- 이 모듈에만 있는 도우미: 시험 안의 내부 함수 `issues`(행 120–126)뿐이다.
- 겹치거나 보완하는 시험: 철회의 허용 조건은 이 모듈이 순수 함수로, 엔진 경로 연결은 `EngineIntegrationTest` 하나가 본다.

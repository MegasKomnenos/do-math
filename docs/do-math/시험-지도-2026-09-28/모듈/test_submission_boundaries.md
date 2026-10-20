# test_submission_boundaries

| 항목 | 값 |
|---|---|
| 조각 | `review` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_submission_boundaries.py` (445행) |
| 클래스 / 테스트 | 3 / 11 (`BoundaryFixture`는 테스트 없는 하네스) |
| 시험 대상 제품 코드 | `do_math/engine.py`의 `ResearchEngine.run`, `process_controls`, `_refresh_readiness`, `_enqueue`, `control`(모듈 함수); 받아들임 경계에서 도는 `_receive_submission`과 `_apply_submission_bundles`(간접); `do_math/context_store.py`의 `fit_context`; `do_math/knowledge.py`의 `assess_use`, `revise_knowledge`, `plan_impact`, `revision_roots`; `do_math/knowledge_records.py`의 `create_candidate`; `do_math/planning.py`의 `contract_hash` |
| 사용하는 픽스처 모듈 | `purpose_fixtures`(`ActivatedPurposeHarness`, `PurposeRunner`, `CheckedRunner`, `parse_context`, `formal_fixture`, `candidate`), `runner_fixtures`(`common`, `contract_checks`, `formal_ok`), `research_fixtures`(`FixtureAdapter`, `await_control`, `restore_template`, `candidate`, `contract_review`, `disposition`, `assessment`, `supply_observation_rules`), `state_fixtures`(`ACTIVE_LEAN_COMMAND`, `active_instance`) |
| 격리 표지 | 없음 |
| 시작 상태 | `AcceptanceTests` 7개 가운데 6개는 2단 위의 더 깊은 빌드(이 모듈의 `prepared_tasks`)에서, 1개는 2단(`make_active`)에서 시작한다. `HistoricalInputTests` 4개는 1단이다 |

## 목적

모듈 docstring은 이 모듈이 "증거 받아들임과 경계 있는 실패 복구의 회귀 계약"이라고 밝힌다. 이어서 스케줄러, Git 스냅숏, Git 예약은 실제이고, 모델 응답만 스크립트한다고 설명한다. 그렇게 해야 본래 비결정적인 실패 순서를 재현할 수 있기 때문이다.

`AcceptanceTests`는 실제 엔진 구동에서 다섯 계약을 본다.

- 실행이 입력으로 읽은 지식이나 원천이 실행 도중 바뀌면, 그 결과는 현행성 변경으로 받아들여지지 않는다(읽은 스냅숏에 결속된다).
- 한 요청의 실패는 독립 작업자를 멈추지 않는다.
- 실행 실패는 진단 전에 대기로 멈춘다.
- 같은 초과 크기 계약은 저절로 다시 큐에 오르지 않는다.
- 큰 보고는 개정과 재개를 거쳐도 살아남는다.

`HistoricalInputTests`는 순수 함수 `fit_context`와 지식 레코드 함수로 두 가지를 본다. 하나는 큰 이력 입력이 정확한 참조로 읽힐 수 있으면서 현행 계약을 부풀리지 않는다는 것이다. 다른 하나는 보존된 이력이 현행 지식 의존을 되살리지 않는다는 것이다.

## 모듈 수준 요소

- 행 13: 스킬의 `scripts/` 폴더를 `sys.path` 맨 앞에 조건 없이 넣는 공통 경로 머리다.
- 행 14: `purpose_fixtures`를 `purpose`라는 이름으로 import한다.
- 행 6–26: import 목록이다. 상수와 `setUpModule`은 없다.
- `prepared_tasks(root, shared, *, config, count)` (행 29–59): `restore_template`의 빌드 함수다.
  - docstring은 검증된 활성 상태에 비형식 과제 `count`개(`"0"`, `"1"`, ...)를 두고, 각 과제를 실제로 준비하고 계약 검토하고 계획이 선택하게 하여, `research_work` 행동 `count`개가 큐에 오른 상태라고 밝힌다. 준비와 승인은 실제 적용이며, 준비 완료 플래그를 주입하지 않는다.
  - 구현 순서는 다음과 같다.
    1. `PurposeRunner()`의 `answer`를 감싼다. `research_preparation`이면 `research_fixtures.candidate(str(i), formal=False)` 후보 `count`개를 낸다. 확장 파일에는 `contract_checks`(`runner_fixtures`)와 `model_assessments`(난도 high, 중요도 medium)를 쓴다.
    2. `state_fixtures.active_instance(root, shared, config=config)`로 2단 상태를 만든다.
    3. 그 위에 `ResearchEngine(..., runner=runner, formal_verifier=purpose.formal_fixture)`를 연다.
    4. `do_math.initialization.adapter_for`를 `FixtureAdapter`로 패치한 채 `run(max_steps=1)`을 최대 45번 돌린다. 대기열의 `research_work` 수가 `count`가 되면 멈춘다. 끝내 이르지 못하면 `AssertionError("The prepared tasks were not queued for work: ...")`를 던진다.
    5. 끝나지 않은 실행이 있으면 `AssertionError`를 던진다.
    6. 인스턴스 ID를 돌려준다.
  - 사용처는 `BoundaryFixture.engine`이다. `research_fixtures` docstring의 "What to use"는 이 빌드를 `test_submission_boundaries` 전용으로 적는다.
- `note(title="Computation", **changes)` (행 80–83): 비형식 관찰 지식 후보 사전을 만든다. `kind="observation"`, `statement="The result is one."`이고, Lean 코드와 선언과 의존은 비었다. `changes`로 덮어쓴다. `test_newly_reported_knowledge_dependencies_bind_the_read_snapshot`, `test_identity_review_ignores_unrelated_source_change_but_checks_required_source`, `test_changed_prerequisite_task_assessment_invalidates_its_running_consumer`, `test_preserved_history_does_not_recreate_current_knowledge_dependencies`가 쓴다.
- `returned(role, **changes)` (행 86–90): 스크립트 러너의 완료 결과를 만든다. 출력은 `runner_fixtures.common(role)`의 역할별 중립 필드다. `research_work`이면 `outcome="submitted"`, `report`, `checkpoint="Ready."`를 더하고, `changes`로 덮어쓴다. 반환값은 `{"status": "completed", "output": ..., "usage": {}, "error": None}`다. `AcceptanceTests`의 러너들이 쓴다.
- 행 444–445: 직접 실행하면 `unittest.main(verbosity=2)`를 돈다.

## BoundaryFixture (행 62–77)

- 기반: `purpose.ActivatedPurposeHarness`. 테스트가 없는 하네스이고, `AcceptanceTests.setUp`이 인스턴스로 만들어 쓴다. 표지와 클래스 속성은 없다.
- 설정 훅은 재정의하지 않는다. 기반의 `setUp`이 `install_adapter_fixture`로 어댑터를 `FixtureAdapter`로 바꾼다.
- 도우미 `engine(runner, count=1, **configuration)` (행 63–77)은 다음 순서로 엔진을 준비한다.
  1. 설정은 `fixture_config(max_output_repairs=0, **configuration)`이다. 주석(행 64–69)은 두 가지를 설명한다. 공개 초기화와 준비 사슬은 따로 검사되므로, 여기서는 실제로 준비하고 검토한 과제를 가진 검증된 활성 상태의 사본에서 시작한다. 또 현행성 경우들이 반려된 제출의 재시도가 없기를 요구하므로 `max_output_repairs=0`을 두며, 다른 경우는 반려에 이르지 않으므로 한 값으로 시작 상태를 공유한다.
  2. `count`가 참이면 `restore_template(prepared_tasks, config=config, count=count)`의 사본에 `PurposeRunner()`를 단 엔진을 연다. `count=0`이면 `make_active(**config)`(2단)를 쓴다.
  3. 엔진의 러너를 `CheckedRunner(runner)`로 바꾼다.

  `CheckedRunner`는 모델 응답만 스크립트하고, 생산자 검사와 실제 제어 전송 제출을 그대로 쓴다. `local_job_runner`로 호출마다 실제 Windows Job 자식 하나를 띄운다.

## AcceptanceTests (행 93–373)

- 기반: `unittest.TestCase`. 하네스를 상속하지 않고 합성으로 쓴다. 표지와 클래스 속성은 없다.
- `setUp` (행 94–97)은 `BoundaryFixture()`를 만들고 그 `setUp()`을 직접 불러 어댑터 패치를 시작한다. 패치 해제는 `addCleanup(self.fixture.doCleanups)`로 이 테스트의 정리에 잇는다.
- 클래스 도우미 메서드는 없다. 모든 테스트가 `self.fixture.engine(...)`으로 엔진을 얻고, 제어는 `control(self.fixture.repo, ...)`로 보낸다.
- 준비의 단: `count`가 1 이상이면 2단 위의 더 깊은 빌드(`prepared_tasks`)이고, `count=0`이면 2단이다. 설정 인자가 다르면(`max_input_bytes` 등) `restore_template`은 다른 템플릿을 한 번 더 빌드한다.

### `test_newly_reported_knowledge_dependencies_bind_the_read_snapshot` (행 99–128)
- 성질: 실행이 입력으로 받은 지식을 실행 도중 사용자가 개정하면, 결과는 받아들여지지 않고 현행성 변경으로 반려된다. 그 지식을 새로 보고한 방식(근거, 의존, 입력 파일 경로)과 관계없이 그렇다.
- 준비: `prepared_tasks` 빌드(`count=1`). `control(..., "knowledge", config={"operation": "import", "candidate": note()})`와 `process_controls()`로 관찰 지식을 들여온다. 대기열을 `research_work` 행동만 남기고 저장한다. 스크립트 `Runner.run`은 다음을 한다.
  1. `on_started({"pid": 1})`를 부른다.
  2. 작업 공간의 `input/knowledge/<kid>.json`을 읽어 `statement`가 `"The result is one."`임을 단언한다. 입력이 개정 전 판임을 확인하는 것이다.
  3. `control(..., "knowledge", config={"operation": "revise", ..., "changes": {"statement": "The result is two."}})`를 보내고 `await_control`로 적용을 기다린다.
  4. 선언 방식에 따라 `used_sources`나 `dependencies`에 그 지식을 넣은 연구 작업 출력을 돌려준다. 지식으로는 `note("Derived", ...)`를 더한다.
- 실행: `engine.run(max_steps=1)`.
- 단언:
  - 연구 작업 실행의 `outcome`이 `"execution_incomplete"`이고, `error_kind`가 `'currentness_changed'`다.
  - `integration_result.issues`에 `rule_id == 'integration.currentness'`가 있다. 규칙 ID로 사유를 고정한다.
  - 제목이 `"Derived"`인 지식이 없다.
- 대역: `CheckedRunner`, 스크립트 `Runner`, `local_job_runner`(실제 Windows Job).
- 비고:
  - `subTest(declaration=...)` 세 경우는 다음과 같다.
    - `used_sources`: 근거에 지식 ID를 넣는다.
    - `dependencies`: 새 지식의 의존에 넣는다.
    - `knowledge_path`: 근거에 `input/knowledge/<kid>.json` 경로를 넣는다.
  - 경우마다 새 템플릿 사본을 연다.
  - `await_control`의 상한은 60초다.

### `test_identity_review_ignores_unrelated_source_change_but_checks_required_source` (행 130–175)
- 성질: 식별 검토 도중 원천이 바뀌어도, 그 원천이 검토 대상 지식에 필요한 원천이 아니면 검토 결과를 받아들인다. 필요한 원천이면 받아들이지 않는다.
- 준비: 2단. `engine(Runner(), count=0, lean_command=list(ACTIVE_LEAN_COMMAND))`로 연다. 주석대로 형식 검사에는 활성 환경의 구성 명령이 필요하다. `formal_verifier`는 `runner_fixtures.formal_ok`로 바꾼다.
  - 원천 파일은 엔진 루트 밖의 별도 임시 폴더에 둔다(`required.txt` 또는 `unrelated.txt`, 내용 `"original"`). 주석대로 엔진마다 앞 사본을 바꾸기 때문이다.
  - `control(..., "source", ...)`로 원천을 공급한다. 형식 정리 지식 `note("Formal claim", kind="theorem", lean_code="theorem t : True := by trivial", declaration_names=["t"], source_refs=...)`를 들여온다. `source_refs`는 필요한 경우에만 그 원천 이름이다.
  - `engine._enqueue('formal_check', kid)`로 형식 검사를 큐에 올린다.
  - 스크립트 `Runner.run`은 다음을 한다.
    1. `on_started`를 부른다.
    2. 원천 파일을 `"corrected"`로 바꾸고 `control(..., "source", ...)`로 다시 공급한 뒤 `await_control`로 기다린다.
    3. `identity_review` 결과를 돌려준다. `proposal_digest`는 문맥의 `role_review`에서 가져오고, `used_sources=["proposal:statement"]`, `decision="match"`, `scope_complete=True`다.
- 실행: 최대 25번 되풀이한다. 매번 대기열을 그 지식을 대상으로 한 `formal_check`와 `identity_review`만 남기고 저장한 뒤 `run(max_steps=1)`을 돌린다. `stage == 'initial'`인 식별 검토 실행이 끝나면 멈춘다. 끝내 끝나지 않으면 실행, 대기열, 검토 주기를 담아 `self.fail`한다.
- 단언: 끝난 초기 식별 검토 실행의 `outcome`이 필요한 원천이면 `"execution_incomplete"`, 무관한 원천이면 `"output_accepted"`다.
- 대역: `CheckedRunner`, 스크립트 `Runner`, `formal_ok`(컴파일러 대역), `local_job_runner`(실제 Windows Job). 범위 단계의 식별 검토는 `CheckedRunner`가 `scope_response`로 대신 답한다.
- 비고: `subTest(required=...)` 두 경우는 `False`와 `True`다. 단계 상한은 25다.

### `test_changed_prerequisite_task_assessment_invalidates_its_running_consumer` (행 177–236)
- 성질: 선행 과제의 완료 판정은 그것이 근거로 삼은 지식이 개정되면 현행성을 잃는다. 그 선행 과제를 소비하던 실행 중인 후행 작업은 받아들여지지 않는다.
- 준비: `prepared_tasks` 빌드(`count=2`). 관찰 지식 하나를 들여온다. 과제를 제목순으로 정렬해, 제목이 `"0"`인 것을 선행으로, `"1"`인 것을 후행으로 둔다. 대기열을 선행 과제를 대상으로 한 행동만 남긴다. 스크립트 `Runner.run`은 역할에 따라 답한다.
  - `task_contract_review`: `research_fixtures.contract_review(context)`로 승인한다.
  - `research_plan`: 선행 과제에 `assessment(...)`로 완료 판정을 내린다. 준비 완료 과제 전부에는 `not_selected` 처분을 준다.
  - 선행 과제의 `research_work`: `used_sources=[kid]`로 답한다.
  - 후행 과제의 `research_work`: 먼저 `plan_impact(...)['computed_impact']`를 선언한 개정 제어로 지식의 `statement`를 바꾸고, `await_control`로 기다린다. 그 개정이 실제로 받아들여졌는지를 확인한다. 곧 `history`에 `kind == "user_control"`이고 요청 ID가 같은 행이 있어야 한다. 그다음 `used_sources=[prerequisite_id]`로 답한다.
- 실행: 네 단계를 차례로 밟는다.
  1. 선행 작업을 `run(max_steps=1)`으로 돌린다.
  2. 대기열을 `research_plan` 행동 하나로 두고 `run(1)`을 돌린다.
  3. 후행 과제를 `dependencies=[prerequisite_id]`, `reviews=[]`, `planned`, 개정 번호 +1로 바꾼다. 대기열을 그 과제의 `task_contract_review` 하나로 두고 `run(1)`을 돌린다.
  4. 대기열을 후행 과제의 `research_work` 하나로 두고 `run(1)`을 돌린다.

  대기열 행동의 ID는 `repository.new_id("AC")`로 만든다.
- 단언:
  - 1단계 뒤 선행 과제에 결과가 있다.
  - 2단계 뒤 선행 과제의 `status`가 `"completed"`다.
  - 3단계 뒤 후행 과제에 검토가 있다.
  - 4단계 뒤 선행 과제의 `assessment.current`가 거짓이고, 후행 실행의 `outcome`이 `"execution_incomplete"`다.
- 대역: `CheckedRunner`, 스크립트 `Runner`, `local_job_runner`(실제 Windows Job).
- 비고: 대기열과 과제 레코드를 테스트가 직접 고쳐 단계를 고른다.

### `test_failed_request_does_not_stop_a_running_independent_worker` (행 238–276)
- 성질: 한 요청이 실패해도 동시에 도는 독립 작업자는 멈추지 않는다. 인스턴스는 일시정지되지 않으며, 독립 작업자의 결과와 출력 파일은 받아들여진다. 뒤에 재개 제어가 와도 실패한 요청은 저절로 다시 큐에 오르지 않는다.
- 준비: `prepared_tasks` 빌드(`count=2`). 스크립트 `Runner.run`은 역할과 과제에 따라 답한다.
  - 연구 작업이 아닌 역할(실패 진단)은 즉시 실패한다. 주석대로 진단은 시험 대상이 아니다.
  - 과제 `"0"`의 작업은 동료 시작 신호(`threading.Event`)를 최대 10초 기다린 뒤 실패한다.
  - 과제 `"1"`의 작업은 두 일을 한다. `result.txt`를 쓰고 시작 신호를 보낸 뒤, 2초 동안 0.02초 간격으로 `should_stop()`을 폴링한다. 정지를 보면 `observed["stopped"]`를 참으로 하고 `stopped`를 돌려주며, 보지 못하면 완료를 돌려준다.
- 실행: `engine.run(max_steps=2)`. 이어서 `control(..., "resume", origin="operator")`를 보내고 `process_controls()`로 적용한다.
- 단언:
  - 독립 작업자가 정지를 보지 않았다(메시지 "one failed request revoked an independent worker").
  - 런타임 `status`가 `"paused"`가 아니다. 실패한 행동 ID가 `waiting_actions`에 있다.
  - 동료 실행의 `outcome`이 `"output_accepted"`이고, `output_files`에 `path == "result.txt"`가 있다.
  - 재개 뒤 실패한 행동 ID가 대기열에 없다.
- 대역: `CheckedRunner`, 스크립트 `Runner`, `local_job_runner`(실제 Windows Job).
- 비고: 스레드 신호와 폴링을 쓴다. 신호 대기 상한은 10초, 정지 폴링은 2초 동안 0.02초 간격이다.

### `test_execution_failure_is_parked_before_diagnosis` (행 278–288)
- 성질: 실행이 실패하면 그 행동은 대기열에서 빠져 `execution_failure` 대기로 멈추고, 진단을 위한 운영 검토가 큐에 오른다.
- 준비: `prepared_tasks` 빌드(`count=1`). `Runner`는 `"local execution failure"`로 실패한다. 대기열 첫 행동의 ID를 잡는다.
- 실행: `engine.run(max_steps=1)`.
- 단언: 그 ID가 대기열에 없다. `waiting_actions[ID].kind`가 `"execution_failure"`다. 대기열에 `operational_review`가 있다.
- 대역: `CheckedRunner`, 스크립트 `Runner`, `local_job_runner`(실제 Windows Job).

### `test_same_oversized_contract_is_not_automatically_requeued` (행 290–310)
- 성질: 입력 한도를 넘는 같은 계약은 입력 초과로 한 번 기록된다. 모델을 시작하지 않으며, 준비 완료 여부를 여러 번 다시 계산해도 저절로 다시 큐에 오르지 않는다.
- 준비: `prepared_tasks` 빌드(`count=1`, `max_input_bytes=500000`). 설정이 다르므로 다른 템플릿이다. 과제의 `question`을 60만 자 `"q"`로 바꾸고, `status="planned"`, `reviews=[]`로 둔다. 대기열을 비우고 저장한다. `Runner.run`은 불리면 `AssertionError("oversized contract must not start a model")`를 던진다.
- 실행: `engine.run(max_steps=1)`, 이어서 `engine._refresh_readiness()`를 세 번 부른다.
- 단언:
  - `input_overflows` 가운데 행동 역할이 `task_contract_review`인 행이 정확히 1개다.
  - 그 과제의 `task_contract_review` 실행 가운데 `input_preparation.reason == 'input overflow'`인 것이 정확히 1개이고, 그 실행에 `started_at`이 없다.
  - 대기열에 그 과제의 `task_contract_review`가 없다.
- 대역: `CheckedRunner`와 호출되면 실패하는 `Runner`. 모델 호출이 없으므로 `local_job_runner`는 돌지 않는다.

### `test_large_accepted_report_survives_revision_review_and_resumed_work` (행 312–373)
- 성질: 60만 자 보고를 가진 부분 결과는 받아들여진 뒤, 계획의 개정 요청, 과제 개정, 계약 재검토를 거쳐 재개된 작업에 그대로 전달된다. 그 결과가 남긴 증거 파일도 재개된 작업 공간에서 읽힌다. 입력 초과는 생기지 않는다.
- 준비: `prepared_tasks` 빌드(`count=1`). 스크립트 `Runner.run`은 호출된 역할을 기록하고 역할마다 답한다.
  - 첫 `research_work`: `evidence.txt`에 `b"preserved partial evidence"`를 쓰고, `outcome="partial"`, `report="p"*600000`, 남은 일 하나로 답한다.
  - 둘째 `research_work`: 과제의 첫 결과 보고가 60만 자 원문과 같음을 단언한다. 또 문맥의 과제 결과 `output_files`에서 `evidence.txt` 행을 찾아, 작업 공간의 `local_path`가 원래 바이트임을 단언한다. 그 뒤 완료로 답한다.
  - `research_plan`: 반환된 과제에 `incomplete` 판정을 내린다. 완료 의무마다 `open` 처분을 준다. 확장에는 `model_assessments`와, 개정 번호 1인 과제의 `revision_requests`를 쓴다. 준비 완료 과제는 선택한다.
  - `research_preparation`: 그 과제를 개정하는 비형식 후보(`purpose.candidate(..., revises=task_id)`)를 낸다. 확장에는 `model_assessments`, `contract_checks`, `revision_resolutions`(`disposition="revised"`)를 쓰고, `supply_observation_rules`로 관찰 규칙을 더한다.
  - `task_contract_review`: `contract_review(context)`로 승인한다.
  - 그 밖의 역할: `AssertionError("unexpected role: ...")`를 던진다.
- 실행: `engine.run(max_steps=1)`을 최대 12번 돌리며, 작업 호출이 두 번이 되면 멈춘다.
- 단언:
  - 작업 호출이 정확히 두 번이다. 실패하면 실행, 대기, 대기열을 진단으로 보여 준다.
  - 둘째 호출의 과제 개정 번호가 첫째보다 크다. 역할 기록에 `task_contract_review`가 있다.
  - `input_overflows`가 비었다.
  - 연구 작업 실행의 결과가 `["output_accepted", "output_accepted"]`다.
- 대역: `CheckedRunner`, 스크립트 `Runner`, `local_job_runner`(실제 Windows Job).
- 비고: 스크립트 러너 안의 단언(보고 원문, 증거 파일 바이트)도 검사의 일부다. 그래서 두 번째 작업 호출까지 몬다.

## HistoricalInputTests (행 376–441)

- 기반: `unittest.TestCase`. 표지, 훅, 도우미, 클래스 속성은 없다. 모든 테스트가 1단이다. `fit_context`와 `knowledge_records`, `knowledge` 함수를 직접 부르고, 임시 폴더를 작업 공간으로 쓴다.

### `test_large_checkpoint_and_operational_evidence_use_exact_readable_references` (행 377–397)
- 성질: 60만 자 체크포인트를 담은 재개 체크포인트, 복구 자료, 운영 검토 입력(검토 대상 실행과 관찰)은 입력 한도를 넘으면 작업 공간 파일로 옮겨진다. 옮겨진 파일은 원래 값을 정확히 담는다.
- 준비: 1단. 체크포인트는 `current_claim`이 60만 자인 사전이다. 문맥은 `{"goal": "g", "action": {"role": "operational_review"}}`에 경우별 키를 더한 것이다.
- 실행: `fit_context(original, max_bytes=20000, workspace=..., mandatory_keys=["goal", "action", *required])`.
- 단언: `overflow.kind`가 `"input_overflow"`다. `result["context"]`가 원래 문맥과 같다. 더한 키마다 목록에서 `key`가 같은 행을 찾아, 그 `path`의 파일 JSON이 원래 값과 같다.
- 대역: 없음.
- 비고: `subTest(fields=list(additions))` 세 경우는 다음과 같다.
  - `resume_checkpoint`(`kind="worker_checkpoint"`).
  - `recovery_materials`.
  - `execution_to_review`와 `observation`. 이 경우는 두 키를 필수 키로도 지정한다.

### `test_large_repair_action_and_previous_execution_remain_readable_by_reference` (행 399–413)
- 성질: 60만 자 이전 출력을 담은 수리 행동은 입력 한도를 넘어도 현행 문맥에서 ID와 역할을 유지하고, 원래 행동 전체가 참조 파일로 읽힌다.
- 준비: 1단. 행동은 `AC-repair`(research_preparation, `repair_attempt=1`)이고, `repair.previous_output.summary`가 60만 자다. 문맥에는 `previous_execution`(같은 행동을 담음)도 둔다.
- 실행: `fit_context(context, max_bytes=20000, workspace=..., mandatory_keys=["goal", "action"])`.
- 단언: `overflow.kind`가 `"input_overflow"`다. 현행 문맥 `action`의 `id`와 `role`이 원래 값과 같다. 목록의 `key == "action"` 행의 파일 JSON이 원래 행동과 같다.
- 대역: 없음.
- 비고: 이름은 "이전 실행"도 참조로 읽힌다고 말하지만, 단언은 `action` 참조만 확인한다. `previous_execution` 키가 어떻게 되는지는 단언하지 않는다.

### `test_preserved_history_does_not_recreate_current_knowledge_dependencies` (행 415–425)
- 성질: 지식 레코드의 보존 이력 필드 안에 다른 지식을 가리키는 `dependencies`가 있어도, 그것은 현행 의존이 아니다. 가리켜진 지식이 개정되어도 사용 중단이나 사용 판정 변화가 생기지 않는다.
- 준비: 1단. 이력 키마다 `knowledge_records.create_candidate`로 `KN-A`(`note()`)와 `KN-B`(`note("Independent")`)를 만든다. `KN-B`는 그 키에 `[{"dependencies": ["KN-A"]}]`를 담는다. `assess_use(KN-B)`를 떠 둔다.
- 실행: `revise_knowledge(instance, {}, "KN-A", {"statement": "corrected"}, reason="correction", actor_ref="user")`.
- 단언: 바뀐 `KN-B`에 `use_suspended`가 없거나 거짓이다. `assess_use` 결과가 개정 전과 같다.
- 대역: 없음.
- 비고: `subTest(key=...)` 일곱 경우는 `history`, `use_history`, `review_history`, `revision_history`, `assessment_history`, `governance_history`, `previous_initial_reviews`다.

### `test_large_task_history_is_readable_without_inflating_the_current_contract` (행 427–441)
- 성질: 60만 자 결과와 개정 이력을 가진 과제는 입력 한도를 넘어도 현행 계약(질문, 완료 의무, 계약 해시)을 그대로 유지한다. 과제 전체는 참조 파일로 읽힌다.
- 준비: 1단. 과제는 `research_fixtures.candidate("Current contract")`에 `id="TK-A"`, `revision=2`, 60만 자 결과, 60만 자 결과를 담은 `revision_history`를 더한 것이다.
- 실행: `fit_context(context, max_bytes=20000, workspace=..., mandatory_keys=["goal", "action", "task"])`. 문맥의 행동 역할은 `task_contract_review`다.
- 단언: `overflow.kind`가 `"input_overflow"`다. 현행 `task`의 `question`과 `completion_obligations`가 원래와 같고, `planning.contract_hash`도 같다. 목록의 `key == "task"` 행의 파일 JSON이 원래 과제와 같다.
- 대역: 없음.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈:
  - 입력 초과(`fit_context`)의 일반 규칙은 `test_context_store`와 `test_role_input`이 본다. 이 모듈은 이력성 큰 입력이 현행 계약을 부풀리지 않는지만 본다. `fit_context`는 `test_design_walkthroughs`, `test_family_records`, `test_submission_tools`도 쓴다.
  - 현행성 변경에 따른 반려는 `test_currentness`가 넓게 본다. 이 모듈의 현행성 경우는 스크립트 러너 안에서 실제 제어를 보내 경쟁을 재현한다는 점이 다르다.
  - 실행 실패 뒤 대기와 운영 검토는 `test_submission_tools`의 `ReviewFailureTests`와 `test_unsealed_invalid_runner_output_is_preserved_for_operational_review`가 다른 실패 종류로 본다.
- 픽스처 의존:
  - `AcceptanceTests`는 모두 `BoundaryFixture.engine`을 거친다. 이 도우미는 `purpose_fixtures.ActivatedPurposeHarness`(`make_active`, `_engine`, `fixture_config`)와 `research_fixtures.restore_template`, 모듈 빌드 `prepared_tasks`를 쓴다.
  - 러너는 `purpose_fixtures.CheckedRunner`다. `CheckedRunner`를 쓰는 모듈은 이 모듈과 `test_submission_tools` 둘뿐이다.
  - 응답 조각은 `runner_fixtures.common`, `contract_checks`와 `research_fixtures.contract_review`, `disposition`, `assessment`, `supply_observation_rules`다.
  - 형식 검사 대역은 `purpose.formal_fixture`(빌드)와 `runner_fixtures.formal_ok`(원천 경우)다.
- 이 모듈에만 있는 도우미: 모듈 함수 `prepared_tasks`, `note`, `returned`와 하네스 클래스 `BoundaryFixture`(도우미 `engine`). `prepared_tasks`는 `research_fixtures` docstring의 "What to use"에 이 모듈 전용 빌드로 등록되어 있다.
- 겹치거나 보완하는 시험:
  - `test_newly_reported_knowledge_dependencies_bind_the_read_snapshot`과 `test_changed_prerequisite_task_assessment_invalidates_its_running_consumer`는 둘 다 실행 도중의 지식 개정이 결과를 무효로 함을 본다. 앞의 것은 실행이 직접 읽은 지식을, 뒤의 것은 선행 과제 판정을 거친 간접 의존을 다룬다.
  - `test_identity_review_ignores_unrelated_source_change_but_checks_required_source`는 같은 원천 변경을 두 경우로 나누어 받아들임과 거부의 경계를 한 테스트에서 본다.
  - `test_preserved_history_does_not_recreate_current_knowledge_dependencies`는 순수 함수로 "이력은 현행 의존이 아니다"를 보고, `test_large_task_history_is_readable_without_inflating_the_current_contract`는 입력 준비에서 "이력은 현행 계약이 아니다"를 본다.

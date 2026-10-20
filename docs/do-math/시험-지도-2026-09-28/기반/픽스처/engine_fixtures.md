# engine_fixtures

| 항목 | 값 |
|---|---|
| 원문 | `.claude/skills/do-math/scripts/tests/engine_fixtures.py` (813행) |
| 정의 수 | 함수 29, 클래스 3(`FakeEngine`, `PublicInitializationRunner`, `NoRepository`), 상수 3(`SCRIPTS`, `QUERY_INSTANCE_ID`, `EVIDENCE_TIME`) |
| 이 모듈을 쓰는 시험 모듈 | 33개(`consumers.json` 기준). 픽스처 모듈 가운데에서는 `state_fixtures`와 `review_fixtures`가 `FakeEngine`을 쓴다 |
| 이 모듈이 부르는 다른 픽스처 | `research_fixtures`(`FixtureAdapter`, `StateStore`, `approved_governance`, `bare_engine`, `charter`, `governance_start`, `review_items`, `trust_fixture`, `trust_environment`, `intent_response`, `seal_response`, `dispatched_launch`, `current_state`, `git_init`), `record_fixtures`(`surface_state`, `apply_assessment`, `transfer_assessment`, `checked_import`, `audited_governance`), `knowledge_fixtures`(`formal_result`, `knowledge_candidate`), `state_fixtures.start_active_copy` |

## 목적

모듈 docstring(행 1–38)은 이 모듈을 "엔진 대역과, 시험들이 공유하는 엔진 시작 상태"라고 소개한다. 여기에 나오는 엔진은 모두 제품 `ResearchEngine`이다. 대역은 엔진 클래스를 새로 쓰지 않는다. 엔진이 붙는 상태와 저장소를 바꾸거나, 엔진 메서드 몇 개를 덮어쓴다. docstring은 엔진을 두 종류로 나눈다.

- 메모리 엔진(in-memory engine)은 건네받은 상태를 들고 Git에는 아무것도 게시하지 않는다. `FakeEngine`, `formal_check_engine`, `routing_engine`, `context_engine`, `initial_failure_engine`, `reassessment_engine`, `governance_host`, `goal_audit_host`, `evidence_engine`이 여기에 속한다. 그리고 이 엔진들을 움직이는 도우미가 따른다: `approve_contract`, `formal_verification`, `intent_import`, `intent_verdict`, `package`, `reviewed_task`, `apply_plan`, `accept_knowledge`, `audit_goal`.
- Git 기반 시작 상태(Git-backed start state)는 `unittest.TestCase`에 속성을 준다. `start_submission_history`, `submit_history`, `start_native_final`, `start_query_repository`, `start_repair_host`가 여기에 속한다. 공개 `initialize`만 돌리는 `initialized`와 템플릿 빌드 `initialized_instance`, 그 해석 역할에 답하는 `PublicInitializationRunner`도 같은 무리다.

`native_result`는 등록된 실행에 대해 공급자가 내놓는 네이티브 최종 출력을 러너가 보고하는 모양으로 만든다. 프로세스는 만들지 않는다.

## 구성

| 무리 | 정의 | 부르는 것 |
|---|---|---|
| 메모리 엔진의 핵심 | `approve_contract`, `formal_verification`, `FakeEngine`, `formal_check_engine` | `FakeEngine.__init__` → `research_fixtures.StateStore`, `initialization.initialize_state`, `build_profiles`; `FakeEngine.approve` → `approve_contract` → `research_fixtures.review_items`, `planning.seal_contract_review`, `governance_working_view`; `FakeEngine.verify`·`knowledge` → `formal_verification` → `knowledge_fixtures.formal_result`; `FakeEngine.activate` → `grant`, `control`, `environment`, `research_fixtures.charter`·`FixtureAdapter`·`intent_response`, `governance.import_input_source`·`prepare_import`·`check_import`·`apply_import`, 엔진의 `_activate_initialization`; `formal_check_engine` → `FakeEngine.activate`, `kr.create_candidate` |
| 공개 초기화 | `initialized`, `initialized_instance`, `PublicInitializationRunner` | `initialized` → `engine.initialize`, `research_fixtures.git_init`; `initialized_instance` → `initialized`; `PublicInitializationRunner.run` → `research_fixtures.intent_response`·`seal_response`, `submission.request_control`, `ControlTransport.wait_receipt` |
| 역할 입력 | `context_engine`, `package` | `context_engine` → `record_fixtures.surface_state`, `research_fixtures.bare_engine`, `contracts.prompt_documents`; `package` → 엔진의 `_context`, `context_store.prepare_role_input` |
| 응답 경로와 해석 | `NoRepository`, `routing_engine`, `intent_import`, `intent_verdict` | `routing_engine` → `bare_engine`, `NoRepository`, `governance_start`; `intent_import` → 엔진의 `_apply` |
| 회복·계획·거버넌스 상태 | `initial_failure_engine`, `reassessment_engine`, `governance_host`, `goal_audit_host` | `initial_failure_engine` → `FakeEngine`, `bare_engine`, `model_policy.selection`, `activities`, `execution_lifecycle`, `research_fixtures.dispatched_launch`; `reassessment_engine` → `record_fixtures.transfer_assessment`·`apply_assessment`, `FakeEngine`; `governance_host` → `record_fixtures.checked_import`, `bare_engine`; `goal_audit_host` → `governance_host`, `record_fixtures.audited_governance`, 엔진의 `_bind_governance_input`·`_governance_context` |
| Git 기반 시작 상태 | `start_submission_history`, `submit_history`, `start_native_final`, `start_repair_host`, `QUERY_INSTANCE_ID`, `start_query_repository` | `start_submission_history` → `state_fixtures.start_active_copy`, `ResearchEngine`, `submission.install_tools`, `ControlTransport`, `research_fixtures.seal_response`; `start_native_final` → `start_submission_history`, `input_basis.capture_decision_basis`; `start_repair_host` → `git_init`, `bare_engine`, `current_state`, `ResearchRepository`; `start_query_repository` → `engine.initialize`, `knowledge_io.import_candidate`·`import_relation` |
| 네이티브 최종 출력 | `native_result` | `codex_adapter._artifact`, `launch.ticket` |
| 증거 흐름(설계 워크스루) | `SCRIPTS`, `EVIDENCE_TIME`, `input_snapshot_store`, `evidence_engine`, `evidence_task`, `reviewed_task`, `plan_output`, `apply_plan`, `truth_candidate`, `accept_knowledge`, `audit_goal` | `evidence_engine` → `bare_engine`, `governance_start`, `approved_governance`, `charter`, `governance_working_view`, `build_profiles`, `contracts.all_prompt_documents`, `input_snapshot_store`; `reviewed_task` → `evidence_task`, `review_items`, `planning.seal_contract_review`; `apply_plan` → `input_snapshot_store`, 엔진의 `_apply`; `accept_knowledge` → `truth_candidate` → `knowledge_fixtures.knowledge_candidate`, `knowledge_io.import_candidate`, `research_fixtures.trust_fixture`·`trust_environment`, `knowledge_fixtures.formal_result`, `kr.record_formal_result`·`record_identity_assessment`; `audit_goal` → 엔진의 `_goal_basis_key`·`_bind_governance_input`·`_governance_context`·`_apply` |

## 모듈 수준 이름

- `SCRIPTS` (행 60): `Path(__file__).resolve().parents[1]`, 곧 스킬의 `scripts/` 폴더다. 이 모듈 안에서는 `evidence_engine`이 인스턴스의 `workspace`로 쓴다(행 717). `consumers.json`에 항목이 없다.
- `QUERY_INSTANCE_ID` (행 602): `"RI-00000000000000000000000000"`. `start_query_repository`가 공개 `initialize`에 넘기는 고정 인스턴스 ID다. 소비자: `test_control_shapes`, `test_query_records`.
- `EVIDENCE_TIME` (행 682): `'2026-09-20T00:00:00+00:00'`. `evidence_engine`의 `last_observed_utc`와 `lifecycle_clock`이 이 시각을 돌려준다. 소비자: `test_design_walkthroughs`.

## 메모리 엔진의 핵심

### `approve_contract(instance, runtime, task, decision='approved')` (행 63–66)
- 종류: 함수.
- 하는 일과 반환값: `task`의 계약 검토 하나를 봉인해 `task['reviews']`를 그 한 건으로 바꾼다. 검토 출력은 `review_items(['context:goal'], decision=decision)`이다. 이를 `planning.seal_contract_review(task, output, governance_working_view(instance), runtime, execution_id='EX-review')`로 봉인한다. docstring은 "`FakeEngine.approve`가 하는 것과 같이"라고 밝히며, `FakeEngine` 밖의 기록에도 같은 봉인을 줄 때 쓴다. 반환값은 없다.
- 부작용: `task`를 제자리에서 바꾼다.
- 의존: `research_fixtures.review_items`, `planning.seal_contract_review`, `initialization.governance_working_view`.
- 소비자: `test_submission_flow`. 모듈 안에서는 `FakeEngine.approve`가 부른다.

### `formal_verification(source, declarations, chain)` (행 69–73)
- 종류: 대역(컴파일러).
- 하는 일과 반환값: docstring은 "`FakeEngine`의 컴파일러 대역: 모든 선언이 `Eq Nat 1 1`로 검증되고 의존이 없다"이다. `knowledge_fixtures.formal_result(source, declarations, chain, closure=(), dependency_evidence=(), declaration_evidence=('Eq Nat 1 1', None), allowed_axioms=sorted(AXIOMS))`를 돌려준다. 원문과 선언을 검사하지 않으므로 어떤 입력도 `verified`가 된다.
- 부작용: 없음.
- 의존: `knowledge_fixtures.formal_result`, `trust_validation.AXIOMS`.
- 소비자: `test_formal_engine`, `test_review_engine`. 모듈 안에서는 `FakeEngine.verification`의 값이다.

### `FakeEngine` (행 76–210)
- 종류: 대역(메모리 엔진). 제품 `ResearchEngine`을 상속한다.
- 하는 일과 반환값: docstring은 "메모리 상태 위의 제품 엔진이며, 저장은 사본을 기록한다"이다. 저장소는 메모리 `StateStore` 대역이다. docstring은 "거부된 확장 제어는 그것을 거쳐 현재 머리에 거부된 요청을 보존한다"고 덧붙인다. 제품 그대로인 부분은 제어 적용(`_apply_extended_control`), 신뢰 등록과 전이, 해석 준비·검사·적용, 초기화 활성화, 기계 행동 처리, 지식 기록이다. 바뀌는 부분은 넷이다. `_execution_profile`은 모델 선택을 생략한다. `_controls`는 아무것도 하지 않는다. `_save`는 사본만 기록한다. `_ensure_model_assessments`는 빈 집합을 돌려준다. 여기에 시험용 편의 메서드가 더해진다.
- 클래스 속성: `verification = staticmethod(formal_verification)` (행 178). `verify`와 `knowledge`가 쓰는 컴파일러 대역이다. 하위 클래스나 인스턴스에서 바꿀 수 있다.
- 메서드:
  - `__init__` (행 82–97): `ResearchEngine.__init__`을 부르지 않는다. `_init_process_state()` 뒤에 다음을 둔다: `store=StateStore(self)`, `runner=None`, `root`, 현재 UTC 시각 `current_time`, 그 시각을 돌려주는 `lifecycle_clock`, 0을 돌려주는 `lifecycle_monotonic`. 설정은 `DEFAULT_CONFIG` 사본에 `tool_review_window_seconds=60`, `self_check_response_window_seconds=5`, 호출자의 `config`, 그리고 강제 `research_reconsider_seconds=60`을 더한 것이다. `initialize_state`로 인스턴스 `RI-test`(목표 'Prove the target', 원 입력 'Original user request')를 만들고 `build_profiles(config)`를 얹는다. 런타임에 `cycles=0`, `waiting_actions={}`를 둔다. 끝으로 `head='fixture-head'`, `saves=[]`, `formal_calls=[]`, `formal_behavior=None`, `formal_verifier=self.verify`를 둔다.
  - `_execution_profile` (행 98–107): 제품 판(엔진의 `_select_model`과 `select_profile`)을 대신한다. 우선순위는 다음과 같다. 행동의 대상 과제에 `profile_refs`가 있고 행동에 `profile_ref`가 없으면 과제의 첫 참조를 쓴다. 그렇지 않으면 행동의 `profile_ref`를 쓰고, 그것도 없으면 `role_profile_refs[role][0]`을 쓴다. 고른 프로필의 참조와 `actor_kind`를 행동에 적는다. 이 점은 주석(행 99)이 밝히듯 제품과 같다. 모델 선택 기록(`model_selection`)은 남기지 않는다. 참조가 해석되지 않으면 `resolve_profile`의 예외가 그대로 난다.
  - `_controls` (행 108): 아무것도 하지 않는다. 제품 판은 받은 편지함(inbox) 적용과 주기적 정비(upkeep)를 한다. 이 대역에서 제어는 `control`로만 들어온다.
  - `_save` (행 109–110): `saves`에 인스턴스, 런타임, 산출물의 깊은 사본을 덧붙이기만 한다. 제품 판이 하는 변경 없음 판정, 시계 기준점 반영, `store.save_with_state` 호출, 정지 평가는 하지 않는다. 그래서 `head`는 바뀌지 않는다.
  - `_ensure_model_assessments` (행 111): 빈 집합을 돌려준다. 제품 판(`planning_engine.py` 행 104–169)은 계약 검토 전에 준비를 요청한다. 대상은 모델 평가(`model_assessment`)가 없는 비종결 과제 전부와, 유효한 초기 관찰 규칙이 없는 학술 과제(`academic_requirement_id`)다. 제품 판은 그 과제들의 대기 중인 `task_contract_review`를 큐에서 빼고, 평가·규칙 준비를 맡기는 `research_preparation` 행동을 큐에 넣은 뒤, 해당 과제 ID 집합을 돌려준다. 준비성 갱신은 이 집합의 과제를 `not_ready`로 둔다(`lifecycle_engine.py` 행 581–590). 이 대역 아래에서는 이런 준비 요청이 생기지 않고, 어떤 과제도 이 이유로 `not_ready`가 되지 않는다.
  - `control` (행 112–114): `{'id': request_id 또는 'UI-'+확장 제어 수, 'action', 'config'}`를 제품의 `_apply_extended_control`에 넘기고 그 결과를 돌려준다.
  - `grant` (행 115–118): `decision` 제어로 grant `identifier`를 적용한다. `http`가 있으면 그 사전을 grant로 쓴다. 없으면 `kind='local'`, `reuse='reusable'`, 만료 하루 뒤로 두고, 역할은 `initial`이면 `['intent_interpretation']`, 아니면 `TASK_WORK_ROLES | OPERATING_ROLES` 전체를 정렬한 것이다.
  - `environment` (행 119–136): 차례는 다음과 같다.
    1. `research_fixtures.trust_fixture(root/name, ['synthetic-lean', name])`로 합성 도구 사슬을 만든다.
    2. 제품의 `_trust_control`로 등록하고, 그 도구 사슬을 가진 환경 ID를 찾는다. 찾지 못하면 `StopIteration`이 난다.
    3. 주석(행 125)대로 그 도구 사슬의 `configured_command`로 만든 `trust_check` 프로필 판을 명시적으로 설치한다.
    4. `active`면 `transition` 신뢰 제어를 보낸다. 이어 `check_environment`의 실제 검사 결과로 `_finish_trust_transition`을 마친다.
    5. 환경 ID를 돌려준다.
  - `activate` (행 137–177): docstring은 "채택 결정(adoption decision)을 거쳐 활성화한다. `review_policy`가 None이면 기본 정책을 채택한다"이다. 차례는 다음과 같다.
    1. grant 둘을 준다: `GR-init`(초기)과 `GR-research`.
    2. 헌장 `CH-test`를 초기화 거버넌스 제어로 넣는다.
    3. AI 프로필마다 `FixtureAdapter().describe()`로 능력 증거를 만들어 `capability_evidence`에 넣는다.
    4. 초기화 채택 결정을 보낸다. 결정은 다음을 싣는다: 설정 해시, 현재 거버넌스 채택, `continue_authorized`, `external_policy`, 검토 정책 또는 기본 정책 채택, 초기·연구 grant ID.
    5. `environment('base', True)`로 신뢰 환경을 활성화한다.
    6. 원 입력의 해석을 제품 함수로 돈다. `import_input_source` 뒤에 작성 실행 `EX-interpret`를 등록하고 `research_fixtures.intent_response`로 답을 만들어 `prepare_import`를 부른다. 이어 검사 실행 `EX-check`를 등록하고 같은 방식으로 판정을 만들어 `check_import`, `apply_import`를 부른다.
    7. 두 실행을 `execution_incomplete`로 끝낸다(`disposition={'kind': 'test_fixture'}`).
    8. `_complete_initial_intent`와 `_activate_initialization`을 부른다.
    9. 큐와 대기 사건을 비운다.
    대역 안의 검사는 둘이다. `_activate_initialization()`의 결과가 `activated`가 아니면 그 결과를 담은 `AssertionError`를 던진다. `intent_response`의 검사 단계는 해석이 원문을 그대로 이어 붙인 것이 아니면 `AssertionError`를 던진다. 호출자는 `do_math.initialization.adapter_for`를 `FixtureAdapter`로 바꿔 두어야 한다(`formal_check_engine`, `state_fixtures.active_instance`가 그렇게 한다).
  - `verify` (행 179–182): 호출 인자를 `formal_calls`에 기록한다. `formal_behavior`가 있으면 그것에 인자를 넘긴 결과를, 없으면 `verification(source, declarations, expected_toolchain)`을 돌려준다. 엔진의 `formal_verifier`로 걸려 있으므로 제품의 형식 검사가 이 메서드를 부른다.
  - `knowledge` (행 183–192): 지식 `kid`를 만든다. 원문은 `theorem <kid 소문자> : 1 = 1 := rfl`, 종류 `lemma`, 의존은 `dependencies`다. 차례는 네 단계다. 후보를 만든다(`kr.create_candidate`). `verification`의 결과를 기록한다(`record_formal_result`, 기본값은 활성 신뢰 환경). `match` 동일성 평가를 `review-policy` 정책으로 기록한다. 기록된 지식 사전을 돌려준다.
  - `task` (행 193–205): 과제 `task_id`(기본 `T1`)를 `planned` 상태로 `runtime['tasks']`에 넣는다. 과제는 비형식(`nonformal`)이다. 진행 기준 `PG-<id>`와 완료 의무 `OB-<id>`(판정자 `task_assessor`) 하나씩을 가진다. 프로필은 `research_work`의 `high` 등급 프로필이고, 권한은 `GR-research`, 근거는 `context:goal`이다. `condition`과 `inputs`로 발생 조건과 입력을 바꾼다. `approved`면 `approve`로 계약 검토를 봉인한다. 과제 사전을 돌려준다.
  - `approve` (행 206–207): `approve_contract(self.instance, self.runtime, t, decision)`을 부른다.
  - `machine` (행 208–210): 큐에서 `role`의 첫 행동을 찾아 제품의 `_process_machine_action`으로 처리하고 그 행동을 돌려준다. 없으면 `StopIteration`이 난다.
- 부작용: `environment`는 `root` 아래에 합성 도구 사슬과 기록 파일을 만든다. 그 밖에는 메모리 상태만 바꾼다. Git도 프로세스도 쓰지 않는다.
- 의존: `research_fixtures.StateStore`·`FixtureAdapter`·`charter`·`trust_fixture`·`intent_response`, `approve_contract`, `formal_verification`, `initialization.initialize_state`, `execution_profiles`, `governance`, `trust_validation.check_environment`, `kr`.
- 시작 상태의 단: 네 단 밖(메모리 엔진 대역). 동시에 2단의 재료다. `state_fixtures.active_instance`가 이 엔진의 `activate`로 합성 활성 상태를 조립한다.
- 소비자: `review_fixtures`, `state_fixtures`, `test_family_records`, `test_initial_intent_connection`, `test_lifecycle_engine`, `test_lifecycle_gates`, `test_machine_parallel`, `test_observation_admission`, `test_planning_engine`, `test_role_input`, `test_session_scheduler`. 모듈 안에서는 `formal_check_engine`, `initial_failure_engine`, `reassessment_engine`이 쓴다.

### `formal_check_engine(test)` (행 213–238)
- 종류: 함수(메모리 엔진 시작 상태).
- 하는 일과 반환값: 후보 `K1`과 그 큐에 들어간 `formal_check`를 가진 `FakeEngine`을 `(engine, action)`으로 돌려준다. 차례는 다음과 같다.
  1. `do_math.initialization.adapter_for`를 `FixtureAdapter()`로 패치한다.
  2. 임시 디렉터리 위에 `FakeEngine`을 만들어 `activate()`한다.
  3. 후보 `K1`(`theorem k1 : 1 = 1 := rfl`)을 만든다.
  4. docstring대로, 활성 신뢰 환경의 `configured_command`로 프로필 판을 다시 만든다. 그 판의 실행 프로필을 더하고 `formal_check` 역할 참조를 교체한다.
  5. 큐를 `[{'id': 'AC-formal', 'role': 'formal_check', 'target': 'K1'}]` 하나로 둔다.
- 부작용: `mock.patch('do_math.initialization.adapter_for')`를 시작하고 `test.addCleanup`으로 멈춘다. 임시 디렉터리도 정리를 등록한다.
- 의존: `FakeEngine`, `research_fixtures.FixtureAdapter`, `kr.create_candidate`, 엔진의 `_formal_environment`, `build_profiles`.
- 시작 상태의 단: 네 단 밖(메모리 엔진 대역).
- 소비자: `test_formal_engine`, `test_review_engine`.

## 공개 초기화

### `initialized(repository, *, goal, **options)` (행 241–249)
- 종류: 함수(공개 경로).
- 하는 일과 반환값: `research_fixtures.git_init(repository)`로 새 Git 저장소를 만들고 공개 `do_math.engine.initialize`로 인스턴스 하나를 만든 뒤 그 ID를 돌려준다. `workspace`의 기본값은 `repository / 'work'`이고, 나머지 `options`는 `initialize`로 넘어간다.
- 부작용: 실제 Git 저장소와 초기 커밋, 작업 공간 디렉터리.
- 의존: `do_math.engine.initialize`, `research_fixtures.git_init`.
- 시작 상태의 단: 4단(공개 초기화를 직접 돈다).
- 소비자: `test_controls`, `test_engine`, `test_lifecycle_engine`. 모듈 안에서는 `initialized_instance`가 부른다.

### `initialized_instance(root, shared, *, goal, config)` (행 252–257)
- 종류: 템플릿 빌드(`research_fixtures.restore_template`).
- 하는 일과 반환값: docstring은 "공개 `initialize`만 돌리는 빌드이며 인스턴스 ID를 돌려준다"이다. 저장소는 `root / 'repository'`, 작업 공간은 `root / 'work-0'`이다. `shared`는 쓰지 않는다.
- 부작용: `initialized`와 같다. `restore_template`이 프로세스당 한 번 만들고 이후에는 바이트 사본을 준다.
- 의존: `initialized`.
- 시작 상태의 단: `restore_template`로 복원하는 공개 초기화 결과. 네 단 가운데 어느 것과도 같지 않다. 활성화 전의 `initializing` 상태를 담으며, `research_fixtures` docstring의 "What to use" 목록(행 63–64)에 올라 있다.
- 소비자: `test_controls`, `test_lifecycle_engine`, `test_session_scheduler`.

### `PublicInitializationRunner` (행 260–278)
- 종류: 대역(모델 러너).
- 하는 일과 반환값: docstring은 "합성된 독립 작성자·검사자 출력, 실제 생산자·수신자 경로"이다. 공개 활성화의 두 해석 실행(작성과 검사)에 답한다. 답의 내용만 합성이고, 제출은 실제 제어 전송(control transport)을 거친다.
- 메서드:
  - `run` (행 262–278): 차례는 다음과 같다.
    1. `workspace/input/submission/context.json`을 읽는다.
    2. 행동 역할이 `intent_interpretation`이 아니면 `AssertionError('No research is authorized by the initialization fixture')`를 던진다. 이것이 대역 안의 검사다.
    3. `on_started({'job_name': launch_ticket['job_name']})`로 시작을 알린다.
    4. `intent_response(context)`를 `seal_response`로 봉인해 `draft.json`에 쓴다.
    5. `submission.request_control(..., kind='submit_intent', wait_seconds=0, binding=control_binding)`로 제출 의사를 보낸다.
    6. `ControlTransport.wait_receipt(binding, request_id, 60)`로 소유자 루프가 받을 때까지 최대 60초 기다린다. 주석(행 274–275)은 "submit_intent는 이후의 연구 권한을 닫으며, 그것이 세운 플래그는 예상된 장벽"이라고 밝힌다.
    7. `{'status': 'completed', 'output': output, 'usage': {}, 'error': None}`을 돌려준다.
    `intent_response`의 검사 단계는 해석 단위를 이어 붙인 것이 원문과 다르면 `AssertionError`를 던진다.
- 부작용: 작업 공간에 `draft.json`을 쓰고 제어 전송 요청을 남긴다. 실제 프로세스는 만들지 않는다. `on_started`에 프로세스 식별 없이 `job_name`만 넘긴다.
- 의존: `research_fixtures.intent_response`·`seal_response`, `submission.request_control`, `ControlTransport.wait_receipt`, `canonical_json`.
- 소비자: `test_initial_intent_connection`, `test_lifecycle_engine`.
- 비고: 메서드 안에서 `json`, `submission`, `canonical_json`을 다시 import한다(행 263–265). 모두 모듈 머리(행 42, 48, 54)에서 이미 import한 이름이다.

## 역할 입력

### `context_engine(instance=None, runtime=None)` (행 280–303)
- 종류: 대역(메모리 엔진).
- 하는 일과 반환값: docstring은 "실제 맥락 생산자는 유지하고, 관련 없는 호스트 관측은 바꾼다"이다. 차례는 다음과 같다.
  1. `record_fixtures.surface_state()`의 상태에서 시작한다. 인스턴스에 빈 관계, `goal_status='unresolved'`, 활성 생명주기를 둔다. 런타임에 빈 입력, 질문, 실행을 둔다.
  2. `instance`가 있으면 그것을 덮어쓴다. 실행 프로필만은 합친다.
  3. `runtime`이 있으면 그것을 덮어쓴다.
  4. `bare_engine(..., head='a'*40, store=create_autospec(ResearchRepository, instance=True))`로 엔진을 만든다.
  5. 저장소의 `read_many`를 `read`의 반복으로 바꾼다. `read` 자체는 autospec이 돌려주는 대역 값이다.
  6. `_documents`에 `research_preparation`, `research_plan`, `research_work`의 실제 프롬프트 문서를 둔다.
  7. 엔진 메서드 일곱 개를 autospec으로 바꾼다. `_preparation_checkpoint`는 `None`, `_academic_status`는 `{}`, `_planning_history`는 `[]`, `_ensure_academic_followup`과 `_record_academic_assessment`는 `None`을 돌려준다. `_session_slots`는 자동 대역이다. `_execution_profile`은 `ValueError('no compiler launched in input test')`를 던진다. 제품 `_context`는 활성 신뢰 환경이 있을 때만 `formal_check` 미리보기 프로필을 고르려고 이 메서드를 부르고, `ValueError`를 잡아 미리보기를 비운다(`engine.py` 행 1719–1724). 따라서 이 대역은 역할 입력 준비를 실패시키지 않는다. 활성 환경이 주어지면 맥락의 `formal_verifier`에서 `command`와 `expected_toolchain`이 `None`이 된다. 기본 상태인 `surface_state`에는 신뢰 환경이 없으므로 이 호출은 일어나지 않는다.
- 부작용: 없음(저장소도 autospec).
- 의존: `record_fixtures.surface_state`, `research_fixtures.bare_engine`, `contracts.prompt_documents`, `ResearchRepository`(autospec).
- 시작 상태의 단: 네 단 밖(메모리 엔진 대역).
- 소비자: `test_context_store`, `test_input_recovery`, `test_planning_engine`, `test_question_flow`, `test_research_recovery`, `test_role_input`, `test_submission_flow`.

### `package(engine, root, role='research_plan', target=None)` (행 306–316)
- 종류: 함수.
- 하는 일과 반환값: 역할 입력 하나를 실제로 준비한다. 행동 `{'id': 'AC-plan', 'role': role}`(대상이 있으면 `target` 포함)으로 제품의 `_context(action, root, execution_id='EX-plan')`를 부른다. 그 역할의 첫 프로필로 `context_store.prepare_role_input`을 부르는데, 인자는 `snapshot=engine.head`, `workspace=root`, `activity_id='AC-1'`, `install_submission_tools=True`, `artifact_prefix='runtime/artifacts/BA-plan'`이다. 그다음 `root/input/submission/context.json`을 `submission.load_json`으로 읽는다. `(result, fixed)`를 돌려준다.
- 부작용: `root` 아래에 역할 입력 파일과 제출 도구를 쓴다.
- 의존: 엔진의 `_context`, `context_store.prepare_role_input`, `submission.load_json`.
- 소비자: `test_input_recovery`, `test_research_recovery`, `test_role_input`.

## 회복·계획·거버넌스 상태

### `initial_failure_engine(root, kind='execution_failure', stage='interpret')` (행 319–355)
- 종류: 함수(메모리 엔진 시작 상태).
- 하는 일과 반환값: 실패한 초기 해석이 maintenance를 기다리는 엔진을 `(engine, action, wait)`로 돌려준다. 시각은 모두 `2026-09-22T00:00:00+00:00`이다. 차례는 다음과 같다.
  1. 씨앗 `FakeEngine`에 초기 grant `GR-init`을 주고 역할에 `maintenance`를 더한다.
  2. `model_policy.selection`으로 `intent_interpretation` 프로필을 고른다.
  3. 생명주기에 입력 `UI-original`과 채택 정보(초기 grant, 초기 프로필 참조)를 적는다.
  4. 씨앗 상태로 `bare_engine`을 만든다. 저장소는 `ResearchRepository` autospec이고, 시계는 씨앗의 것을 옮긴다.
  5. 활동 `AY-original`을 연다.
  6. 실행 `EX-bad`를 만든다. 발사 표(`dispatched_launch`, 단계 `finished`)와 로컬 종료 확인을 붙인다. `starting` → `stopping` → `ended`(`execution_incomplete`)로 전이시킨다.
  7. 활동을 `kind` 사유로 maintenance 대기에 둔다.
  8. `kind == 'output_validation'`이면 행동에 수리 시도 2와 재시도 묶음 `IN-pending`을 적는다.
  9. 큐를 비우고 `waiting_actions`에 대기 기록을 둔다.
- 부작용: 없음(메모리 상태). `FakeEngine(root)`는 파일을 만들지 않는다.
- 의존: `FakeEngine`, `bare_engine`, `model_policy.selection`, `execution_profiles`, `activities`, `execution_lifecycle`, `research_fixtures.dispatched_launch`.
- 시작 상태의 단: 네 단 밖(메모리 엔진 대역).
- 소비자: `test_research_recovery`.

### `NoRepository` (행 357–366)
- 종류: 대역(저장소).
- 하는 일과 반환값: docstring은 "메모리 엔진의 저장소: Git 디렉터리가 없고 읽을 것도 없다"이다. 클래스 속성 `git_dir = None`이다.
- 메서드:
  - `read` (행 361–363): 언제나 `AssertionError("an in-memory engine has no stored artifact: " + path)`를 던진다. 주석은 "엔진은 이 판독기를 소비자에게 넘긴다. 이것으로 읽는 것은 시험 결함"이라고 밝힌다.
  - `published_state` (행 365–366): 언제나 `None`을 돌려준다. 주석은 "게시된 것이 없으므로 엔진의 상태는 결코 변경 없음이 아니다"라고 밝힌다.
- 부작용: 없음.
- 의존: 없음.
- 소비자: 모듈 안에서만 사용. `routing_engine`(행 372)이 쓴다. `consumers.json`에 항목이 없다.
- 비고: `research_fixtures.StateStore`와 달리 `load`와 `save_with_state`가 없다. `published_state`가 `None`이므로 제품 `_save`의 변경 없음 판정(`_unchanged`)은 언제나 거짓이 된다. 그래서 이 저장소를 가진 엔진이 `_save`에서 게시(`store.save_with_state`)에 이르면 실패한다.

### `routing_engine()` (행 369–382)
- 종류: 대역(메모리 엔진).
- 하는 일과 반환값: 응답 경로(response routing)용 빈 엔진이다. `bare_engine(store=NoRepository())` 위에 인스턴스와 런타임을 둔다. 인스턴스는 `governance_start`로 만든 `RI-test`로, 빈 지식·관계, `goal_status='unresolved'`, 설정 `goal_auditors=2`와 `DEFAULT_CONFIG`의 `max_artifact_bytes`를 가진다. 런타임은 빈 `tasks`, `activities`, `executions`, `queue`, `questions`, `question_links`, `history`, `inputs`, `interpretations`와 `status='ready'`다. 주석(행 370–371)은 "모든 적재된 엔진은 저장소와 산출물 한도를 가지며, 소비자는 대체값 없이 `store.git_dir`와 `config['max_artifact_bytes']`를 읽는다"고 밝힌다. `_bind_revision_action`, `_cancel_selected_revision_targets`, `_record_output_questions` 셋은 autospec 대역으로 바꾼다. 이 셋의 호출 기록을 시험이 읽을 수 있다.
- 부작용: 없음.
- 의존: `research_fixtures.bare_engine`·`governance_start`, `NoRepository`.
- 시작 상태의 단: 네 단 밖(메모리 엔진 대역).
- 소비자: `test_controls`, `test_currentness`, `test_engine`, `test_formal_engine`, `test_governance_engine`, `test_live_observation`, `test_model_metadata_boundary`, `test_planning_engine`, `test_repetition`, `test_research_recovery`, `test_review_engine`, `test_role_input`, `test_session_scheduler`, `test_submission_flow`.

### `intent_import(engine, *, clarification=False, payload=None)` (행 384–411)
- 종류: 함수.
- 하는 일과 반환값: docstring은 "`routing_engine`에서 입력 `UC-input`의 해석 하나를 작성하고 `(bundle, check action)`을 돌려준다"이다. 차례는 다음과 같다.
  1. 입력 "Keep the original purpose."를 둔다.
  2. 해석 단위 `IU-one` 하나로 원문 전체를 덮는 출력을 만든다. 단위의 소유자는 헌장 `CH-one`이고, `payload`는 호출자가 준다.
  3. `clarification`이면 차단 질문 `Q-one`("Which scope?")을 붙인다.
  4. 작성 실행 `EX-author`를 등록하고 제품의 `_apply`로 적용한다. 그 뒤 실행을 `ended`로 둔다.
  5. 생긴 첫 해석 묶음에 대해 검사 실행 `EX-check`를 `ended`로 둔다. 이 실행은 묶음의 `sha256`을 가진다.
  6. 큐 첫 행동의 사본을 떼고 큐를 비운다.
- 부작용: 엔진 상태만 바꾼다.
- 의존: 엔진의 `_apply`.
- 소비자: `test_governance_engine`, `test_repetition`.

### `intent_verdict(bundle, decision="approved", complete=True)` (행 414–419)
- 종류: 함수.
- 하는 일과 반환값: docstring은 "`bundle`에 대한 독립 검사의 출력이며, approved가 아닌 결정은 발견 하나를 단다"이다. 출력은 `bundle_sha256`, `unit_ids=['IU-one']`, 묶음의 질문 ID들, `scope_complete=complete`를 싣는다. 발견은 approved면 비어 있고, 아니면 "Missing second clause" 하나다.
- 부작용: 없음.
- 의존: 없음.
- 소비자: `test_governance_engine`, `test_repetition`.

### `reassessment_engine(directory)` (행 422–434)
- 종류: 함수(메모리 엔진 시작 상태).
- 하는 일과 반환값: docstring은 "불완전한 평가 뒤 과제 `TK-1`이 누락 입력 `SO-new`를 기다리는 `FakeEngine`"이다. 차례는 다음과 같다.
  1. `record_fixtures.transfer_assessment()`의 평가를 `incomplete`로 바꾼다. 첫 처분을 빼고, 미해결 `OB-1`에 누락 입력 `SO-new`와 다음 소유자 `research_work`를 둔다.
  2. `apply_assessment`로 적용한다.
  3. 새 `FakeEngine`을 활성 상태로 둔다. 그 인스턴스에 결과 인스턴스를 얹되 생명주기와 설정은 빼고, 런타임은 결과 런타임으로 갱신한다.
  4. 큐를 `[{'id': 'AC-other', 'role': 'research_preparation'}]`로 둔다.
- 부작용: 없음.
- 의존: `record_fixtures.transfer_assessment`·`apply_assessment`, `FakeEngine`.
- 시작 상태의 단: 네 단 밖(메모리 엔진 대역).
- 소비자: `test_planning_engine`, `test_session_scheduler`.

### `governance_host()` (행 437–457)
- 종류: 함수(메모리 엔진 시작 상태).
- 하는 일과 반환값: docstring은 "`record_fixtures.checked_import`의 상태를 가진 빈 엔진 `(engine, bundle, request)`"이다. `request`는 사용자가 나중에 보내는 정확한 승인을 공개 결정 모양(`config={'change': ...}`)으로 감싼 것이다. 초기 의도 완료와 활성화는 "기록하되 수행하지 않는다". 그래서 `_complete_initial_intent`는 `completed_input` 속성을, `_activate_initialization`은 `activation_attempted=True`를 세우는 autospec으로 바뀐다. 런타임에 빈 `events`·`pending_events`를 두고, 실행마다 `status`의 기본값을 `queued`로 둔다. 설정은 `DEFAULT_CONFIG`에 `scholarly_enabled=False`를 얹는다. 주석(행 456)은 "설정 추가는 이 헌장 가져오기의 전제가 아니다"라고 밝힌다.
- 부작용: 없음. 저장소는 `bare_engine`의 기본 `StateStore`다.
- 의존: `record_fixtures.checked_import`, `research_fixtures.bare_engine`.
- 시작 상태의 단: 네 단 밖(메모리 엔진 대역).
- 소비자: `test_execution_profiles`, `test_goal_audit`, `test_governance`, `test_governance_engine`. 모듈 안에서는 `goal_audit_host`가 부른다.
- 비고: 함수 안에서 `create_autospec`을 다시 import한다(행 443). 모듈 머리(행 45)에서 이미 import한 이름이다.

### `goal_audit_host()` (행 460–481)
- 종류: 함수(메모리 엔진 시작 상태).
- 하는 일과 반환값: docstring은 "`record_fixtures.audited_governance` 위의 `governance_host`인 `(engine, action, output)`"이다. 차례는 다음과 같다.
  1. `governance_host()`의 엔진 상태를 `audited_governance()`로 바꾼다. 지식과 목표 판정은 비우고, 관측 시각은 2020년으로 둔다.
  2. `_goal_basis_key`를 `'B'`를 돌려주는 autospec으로 바꾼다.
  3. 목표 감사 행동(`basis='B'`, 슬롯 0, 필요 1)에 대해 실행 `AUDITOR`를 만든다. 제품의 `_bind_governance_input`으로 거버넌스 입력을 묶는다.
  4. `output`을 만든다. 일반 목표 판정은 `satisfied`이지만, 추가 감사 `AU`의 판정은 `partial`이다. 이 추가 감사 행은 실행이 받은 입력 해시를 그대로 싣는다.
- 부작용: 없음.
- 의존: `governance_host`, `record_fixtures.audited_governance`, 엔진의 `_bind_governance_input`·`_governance_context`.
- 시작 상태의 단: 네 단 밖(메모리 엔진 대역).
- 소비자: `test_goal_audit`, `test_governance_engine`.
- 비고: 함수 안에서 `create_autospec`을 다시 import한다(행 465).

## Git 기반 시작 상태

### `start_submission_history(test)` (행 484–527)
- 종류: 함수(Git 기반 시작 상태).
- 하는 일과 반환값: docstring은 "검증된 활성 상태의 사본 위에서 실행 중인 maintenance 실행을 `test`에 준다"이다. 차례는 다음과 같다.
  1. `state_fixtures.start_active_copy(test)`를 부른다. 이 함수는 `root`, `repo`, `identifier`를 두고, 시험이 끝날 때까지 어댑터 관측을 `FixtureAdapter`로 바꿔 둔다.
  2. 실제 `ResearchEngine(test.repo, test.identifier)`를 연다.
  3. maintenance 행동 `AC-history`를 생명주기 게이트(`_action_lifecycle_gate`)에 통과시킨다. 게이트가 행동에 `grant_id`를 적는다.
  4. 실행 `EX-history`를 `running`으로 등록한다.
  5. 실행에 grant, 입력 묶음 `BA-history-input`, 입력 스냅숏, 입력 목록을 적는다. 입력 목록에는 합성 프롬프트의 경로·해시·크기가 들어간다. 여기에 `governance_revisions`를 더한다.
  6. 작업 공간 `runs/EX-history/workspace`를 만든다.
  7. 맥락을 만든다. 행동, 실행 ID, 스냅숏, 빈 목록들, 행동의 grant 사본이 들어간다.
  8. maintenance 스키마로 제출 도구를 설치한다(한도 1 MiB).
  9. `_save`로 프롬프트, 맥락, 스키마를 봉인 산출물로 게시한다.
  10. `delivery` 폴더에 `ControlTransport`를 만들고 `EX-history`의 바인딩을 발급한다.
  11. 유효한 `output`(비ASCII 문자 `é`를 담은 요약)을 `seal_response`로 봉인한다.
  시험에는 `engine`, `workspace`, `context`, `schema`, `transport`, `binding`, `output`이 생긴다. 모델과 Lean은 부르지 않는다.
- 부작용: 실제 Git 커밋(`_save`), 작업 공간 파일, 제어 전송 디렉터리.
- 의존: `state_fixtures.start_active_copy`, `ResearchEngine`, `contracts.schema_for`, `submission.install_tools`, `ControlTransport`, `planning.governance_revisions`, `research_fixtures.seal_response`, `canonical_json`.
- 시작 상태의 단: 2단(`state_fixtures.active_instance` 템플릿 사본) 위에 실행 하나를 더한 것.
- 소비자: `test_controls`, `test_submission_flow`. 모듈 안에서는 `start_native_final`이 부른다.

### `submit_history(test, request_id, raw)` (행 530–535)
- 종류: 함수.
- 하는 일과 반환값: docstring은 "`raw`를 `EX-history`의 제출 의사 `request_id`로 전달하고 `(request, receipt)`를 돌려준다"이다. `raw`를 `draft.json`에 쓰고, 바인딩에 `request_id`, `kind='submit_intent'`, `payload={'draft_path': 'draft.json'}`를 얹은 요청을 만든다. 이 요청을 `test.transport.receive(request, publish=test.engine._publish_control_request)`로 받게 한다.
- 부작용: 작업 공간 파일과 실제 게시(수신 경로가 게시하면).
- 의존: `ControlTransport.receive`, 엔진의 `_publish_control_request`.
- 소비자: `test_native_final_submission`, `test_submission_flow`.

### `start_native_final(test)` (행 538–543)
- 종류: 함수(Git 기반 시작 상태).
- 하는 일과 반환값: docstring은 "실행이 결정 근거(decision basis)도 기록하는 `start_submission_history`이며, 네이티브 최종 출력이 이를 요구한다"이다. `start_submission_history(test)` 뒤에 `EX-history`의 `decision_basis`를 `capture_decision_basis(instance, runtime, [])`로 채운다. 메모리 안에서만 바꾸고 저장은 하지 않는다.
- 부작용: `start_submission_history`와 같다.
- 의존: `start_submission_history`, `input_basis.capture_decision_basis`.
- 시작 상태의 단: 2단 위의 확장.
- 소비자: `test_native_final_submission`.

### `start_repair_host(test)` (행 546–599)
- 종류: 함수(Git 기반 시작 상태).
- 하는 일과 반환값: docstring은 "실제 저장소 위에 대기 중인 운영 재시도(operational retry) 하나를 가진 빈 엔진을 `test`에 준다"이다. 시각은 모두 `2026-09-20T00:00:00Z`다. 차례는 다음과 같다.
  1. 임시 디렉터리(`test.enterContext`로 정리)에 `git_init`으로 저장소를 만든다.
  2. `ResearchRepository(repo, "RI-01ARZ3NDEKTSV4RRFFQ69G5FAV")`를 저장소로 가진 `bare_engine`을 `test.host`로 둔다.
  3. `current_state`로 상태를 만든다. `DEFAULT_CONFIG` 프로필 가운데 `research_work`와 `operational_review` 프로필만 두고, 용량 제약을 함께 둔다.
  4. 실행 `EX-target`(`research_work`)과 `EX-review`(`operational_review`)를 각자의 활동에 배정하고 `ended`/`cancelled`로 끝낸다.
  5. 대상 실행에 입력 묶음 `BA-target`과 목록을 적는다. 목록의 `catalog`에는 `input/catalog/tasks.json`의 해시·크기가 들어간다.
  6. 작업 공간 사본(`destination`)에는 `b"damaged"`를 쓴다.
  7. 운영 처분 `OD-repair`를 `pending`으로 둔다. 종류는 `retry`, 다음 소유자는 `engine`, 사유는 "Use a fresh workspace for the unfinished activity"다.
  8. `store.initialize`로 게시한다.
  9. `_save`로 봉인 입력 원본(`source`, 내용 `raw`)과 `manifest.json`을 게시한다.
  시험에는 `host`, `raw`, `digest`, `relative`, `source`, `destination`, `record`가 생긴다.
- 부작용: 실제 Git 저장소와 커밋 둘, 작업 공간의 손상된 파일.
- 의존: `research_fixtures.current_state`·`git_init`·`bare_engine`, `ResearchRepository`, `build_profiles`, `activities`, `execution_lifecycle`, `canonical_json`.
- 시작 상태의 단: 네 단 밖(합성 상태를 실제 Git 저장소에 직접 게시).
- 소비자: `test_repair_execution`, `test_research_recovery`.

### `start_query_repository(test)` (행 605–642)
- 종류: 함수(Git 기반 시작 상태).
- 하는 일과 반환값: docstring은 "`test`에 지식 기록 둘과 관계 하나를 가진 게시된 인스턴스 `QUERY_INSTANCE_ID`를 준다"이다. 차례는 다음과 같다.
  1. 임시 디렉터리(`enterContext`)에 `git_init`으로 저장소를 만든다.
  2. 공개 `initialize`를 `instance_id=QUERY_INSTANCE_ID`, 설정 `operator_enabled=False`, `scholarly_enabled=False`로 부른다.
  3. 초기 머리를 다시 적재한다. 적재한 머리가 초기 머리와 다르면 `AssertionError('The initialized head did not load as itself')`를 던진다. 이것이 대역 안의 검사다.
  4. `import_candidate`로 정의 "One"(요약 alpha)과 정리 "Two"(요약 beta)를 가져온다.
  5. `import_relation`으로 "One supports Two" 관계를 만든다.
  6. `save_with_state`로 게시한다(`old_head`).
  7. `runtime/artifacts/query-fixture/a.txt`(`needle alpha`)와 `b.txt`(`needle beta`)를 더해 한 번 더 게시한다(`file_head`).
  시험에는 `root`, `git`, `workspace`, `repository`, `initial_head`, `kids`, `relation_id`, `old_head`, `file_head`가 생긴다.
- 부작용: 실제 Git 저장소와 초기화 커밋 뒤 커밋 둘.
- 의존: `do_math.engine.initialize`, `knowledge_io.import_candidate`·`import_relation`, `ResearchRepository`, `research_fixtures.git_init`.
- 시작 상태의 단: 4단(공개 `initialize`)에 도메인 함수로 기록을 더한 것. 활성화는 하지 않는다.
- 소비자: `test_control_shapes`, `test_query_records`, `test_relation_dependencies`.
- 비고: 함수 안에서 `tempfile`과 `ResearchRepository`를 다시 import한다(행 613, 616). 모듈 머리에서 이미 import한 이름이다.

## 네이티브 최종 출력

### `native_result(execution, context, raw, workspace)` (행 644–680)
- 종류: 대역(러너 결과).
- 하는 일과 반환값: docstring은 "순수 프로토콜 픽스처이며, 실제 Job 범위는 별도의 연결 시험이 맡는다"이다. 등록된 실행에 대해 codex 러너가 보고하는 결과를 만든다. 결과는 `status='completed'`, `output=None`, `collection='provider_evidence_only'`와 `execution.started`·`execution.collect`를 싣는다. 만드는 과정은 다음과 같다.
  1. 실행에 발사 표(`launch.ticket`, 단계 `finished`)를 적는다.
  2. codex 요청(작업 디렉터리, `codex_path='fixture-cli'`, 제어 바인딩)을 만들고 그 해시로 프로세스 식별을 만든다. 식별값은 `pid=123`과 고정 `creation_filetime`이다.
  3. 입력 목록의 `prompt`에 봉인 프롬프트 `b'exact sealed prompt'`의 해시·크기를 적는다. 주석(행 658)은 "역할 입력 목록은 공급자가 받은 봉인 프롬프트의 해시를 싣는다"고 밝힌다.
  4. 실행의 `capacity`에 로컬 종료 확인과 프로세스 식별을 적는다.
  5. codex JSONL 스트림을 만든다: `thread.started`, `turn.started`, `raw`를 본문으로 한 `agent_message` 항목 완료, `turn.completed`.
  6. 수집 결과를 만든다. 요청, 프롬프트, stdout, stderr, 최종 출력의 산출물(`_artifact`)을 담는다. 작업자 상태는 종료 코드 0이며 요청·stdin 해시를 가진다. 종료 장벽은 확인됨, 활성 프로세스 0이다.
- 부작용: `execution`을 제자리에서 바꾼다(`launch_ticket`, `input_manifest`, `capacity`). 프로세스는 만들지 않는다.
- 의존: `codex_adapter._artifact`, `launch.ticket`.
- 소비자: `test_native_final_submission`, `test_repetition`, `test_submission_flow`.
- 비고: 인자 `context`는 함수 본문에서 쓰이지 않는다.

## 증거 흐름

### `input_snapshot_store(instance, runtime)` (행 685–709)
- 종류: 대역(저장소, `ResearchRepository` autospec).
- 하는 일과 반환값: docstring은 "고정된 입력 스냅숏 `'input-snapshot'` 하나를 가진 저장소 대역"이다. `(instance, runtime)`의 깊은 사본을 붙든다. 메서드는 다음과 같이 답한다.
  - `load`와 `view`는 스냅숏이 `'input-snapshot'`일 때만 `(snapshot, instance 사본, runtime 사본)`을 돌려준다. 다른 값이면 `ValueError('unexpected snapshot')`를 던진다.
  - `read`는 경로가 `/input/submission/context.json`으로 끝날 때만 보관된 역할 맥락을 돌려준다. 맥락은 스냅숏, 과제 목록, `planning.ready_task_ids`를 담은 JSON 바이트다. 다른 경로는 `ValueError('fixture has no archived artifact: ...')`를 던진다.
  - `git_dir = None`이므로 프로세스 캐시가 읽기를 기록하지 않는다.
  docstring은 "저장의 경계일 뿐 도메인 전이가 아니다"라고 밝힌다.
- 부작용: 없음.
- 의존: `ResearchRepository`(autospec), `planning.ready_task_ids`.
- 소비자: 모듈 안에서만 사용. `evidence_engine`(행 737)과 `apply_plan`(행 769)이 부른다. `consumers.json`에 항목이 없다.

### `evidence_engine(goal='Establish P', *, academic_requirements=None)` (행 712–738)
- 종류: 대역(메모리 엔진).
- 하는 일과 반환값: 활성 인스턴스 `RI-evidence`를 가진 엔진을 돌려준다. 차례는 다음과 같다.
  1. `bare_engine()`에 `governance_start`로 인스턴스를 만든다. 인스턴스는 활성 생명주기, 빈 출처·지식·관계·결정, `DEFAULT_CONFIG`, 작업 공간 `SCRIPTS`를 가진다. grant는 `GR-evidence` 하나로, 역할은 `research_work`와 `supplemental_research`다.
  2. 헌장 `CH-fixture`를 `approved_governance`로 채택한다. 목표는 `goal`, 학술 요구는 `academic_requirements`다. 사용자 출처는 `US-fixture`, 승인은 `DC-fixture`다.
  3. 주석(행 725)대로 엔진이 현재 쓰는 읽기 투영(`governance_working_view`)을 인스턴스로 삼는다. 이 투영은 저장되지 않는다.
  4. 목표 상태를 미해결로 되돌리고 프로필을 얹는다.
  5. 런타임은 빈 가족들, `status='ready'`, `last_observed_utc=EVIDENCE_TIME`이다.
  6. `head='input-snapshot'`으로 두고, 시계를 `EVIDENCE_TIME`에, 단조 시계를 0에 고정한다.
  7. `_documents`에 모든 역할의 실제 프롬프트 문서를 둔다.
  8. 저장소를 `input_snapshot_store(instance, runtime)`로 둔다.
- 부작용: 없음.
- 의존: `research_fixtures.bare_engine`·`governance_start`·`approved_governance`·`charter`, `initialization.governance_working_view`, `build_profiles`, `contracts.all_prompt_documents`, `input_snapshot_store`, `SCRIPTS`, `EVIDENCE_TIME`.
- 시작 상태의 단: 네 단 밖(메모리 엔진 대역).
- 소비자: `test_design_walkthroughs`.
- 비고: 저장소 사본은 만들 때의 상태를 붙든다. 그 뒤 상태를 바꾸고 입력 스냅숏에서 읽으려면 `apply_plan`처럼 저장소를 다시 만들어야 한다.

### `evidence_task(identifier='TK-1')` (행 741–751)
- 종류: 함수.
- 하는 일과 반환값: `planned` 과제 사전을 돌려준다. 질문은 'Does P hold?'다. 진행 기준은 `PC-1` 하나다. 완료 의무는 둘로, `OB-proof`(증거 `EV-proof`)와 `OB-scope`(증거 `EV-scope`)이며 판정자는 모두 `research_plan`이다. 권한은 `GR-evidence`, 생산 실행은 `EX-preparation`이다.
- 부작용: 없음.
- 의존: 없음.
- 소비자: `test_design_walkthroughs`. 모듈 안에서는 `reviewed_task`가 부른다.

### `reviewed_task(e, identifier='TK-1', **changes)` (행 754–761)
- 종류: 함수.
- 하는 일과 반환값: `evidence_task`에 `changes`를 얹고, 프로필 참조를 `research_work`·`supplemental_research`의 모든 프로필로 둔다. 과제를 `e.runtime['tasks']`에 넣는다. `review_items([identifier])`의 계약 검토를 `planning.seal_contract_review`로 봉인한다(실행 `EX-review-<id>`). 과제를 돌려준다.
- 부작용: 엔진 런타임을 바꾼다.
- 의존: `evidence_task`, `research_fixtures.review_items`, `planning.seal_contract_review`.
- 소비자: `test_design_walkthroughs`, `test_stop_flags`.

### `plan_output(**changes)` (행 764–765)
- 종류: 함수.
- 하는 일과 반환값: 빈 연구 계획 출력(`dispositions`, `task_assessments`, `preparation_requests`는 빈 목록, `goal_audit=False`)에 `changes`를 얹어 돌려준다.
- 부작용: 없음.
- 의존: 없음.
- 소비자: `test_design_walkthroughs`.

### `apply_plan(e, plan, execution_id='EX-plan')` (행 768–772)
- 종류: 함수.
- 하는 일과 반환값: 현재 상태로 `input_snapshot_store`를 다시 만든다. `research_plan` 실행 `execution_id`를 `ended`로 등록한다(입력 스냅숏 `input-snapshot`, 묶음 `BA-plan`). 제품의 `_apply`로 `plan`을 적용한다. 반환값은 없다.
- 부작용: 엔진 상태와 저장소 대역을 바꾼다.
- 의존: `input_snapshot_store`, 엔진의 `_apply`.
- 소비자: `test_design_walkthroughs`.

### `truth_candidate(statement='True', source='theorem truth : True := True.intro', **changes)` (행 775–779)
- 종류: 함수.
- 하는 일과 반환값: docstring은 "모든 해설 필드에 `statement`를 적고 `source`로 증명한 `knowledge_candidate`"이다. 제목, 명제, 설명, 요약이 모두 `statement`이다.
- 부작용: 없음.
- 의존: `knowledge_fixtures.knowledge_candidate`.
- 소비자: `test_design_walkthroughs`. 모듈 안에서는 `accept_knowledge`의 기본값이다.

### `accept_knowledge(e, proposed=None)` (행 782–801)
- 종류: 함수.
- 하는 일과 반환값: docstring은 "Lean과 동일성 응답만 픽스처이고, 가져오기·바인딩·사용 게이트는 실제로 돈다"이다. 차례는 다음과 같다.
  1. `proposed`(기본 `truth_candidate()`)를 `knowledge_io.import_candidate`로 가져온다.
  2. 엔진에 처음 붙는 임시 디렉터리에 합성 신뢰 환경 `TE-fixture`를 만들어 활성 환경으로 둔다. 호출할 때마다 새 환경으로 교체된다.
  3. 선언 `['truth']`에 대한 검증 결과를 `formal_result`로 만들어 기록한다(`record_formal_result`).
  4. `match` 동일성 평가를 `policy:fixture`로 기록한다.
  5. `(kid, aid)`를 돌려준다.
- 부작용: `e._trust_fixture_directory`에 `tempfile.TemporaryDirectory()`를 붙이고 그 아래에 합성 도구 사슬을 만든다. 명시적 정리는 등록하지 않는다.
- 의존: `truth_candidate`, `knowledge_io.import_candidate`, `research_fixtures.trust_fixture`·`trust_environment`, `knowledge_fixtures.formal_result`, `kr.record_formal_result`·`record_identity_assessment`.
- 소비자: `test_design_walkthroughs`.
- 비고: 형식 결과의 선언 목록은 `proposed`의 `declaration_names`와 관계없이 `['truth']`로 고정되어 있다(행 794). 선언 증거의 형(type)은 `proposed['statement']`다.

### `audit_goal(e, kid, decision='satisfied')` (행 804–813)
- 종류: 함수.
- 하는 일과 반환값: 목표 감사 두 슬롯(0과 1)을 적용한다. 슬롯마다 차례는 셋이다. 먼저 `goal_audit` 실행 `EX-goal-<slot>-<판정 수>`를 `ended`로 등록한다. 다음으로 제품의 `_bind_governance_input`으로 거버넌스 입력을 묶는다. 끝으로 `_apply`로 판정을 적용한다. 판정은 `decision`, 범위 완결, `used_sources=[kid]`이고, 행동은 `basis=_goal_basis_key()`, `required=2`다. 반환값은 없다.
- 부작용: 엔진 상태를 바꾼다.
- 의존: 엔진의 `_goal_basis_key`·`_bind_governance_input`·`_governance_context`·`_apply`.
- 소비자: `test_design_walkthroughs`.

## 관계

- 다른 픽스처 모듈과의 의존: 이 모듈은 `research_fixtures`의 기반 도구를 가장 많이 쓴다. 메모리 저장소 `StateStore`, `bare_engine`, 합성 신뢰 환경, 해석 응답, 봉인, `git_init`, `current_state`가 모두 그쪽에서 온다. 도메인 기록은 `record_fixtures`, 지식 기록은 `knowledge_fixtures`에서 오고, 2단 사본은 `state_fixtures.start_active_copy`에서 온다. 반대로 `state_fixtures.active_instance`는 `FakeEngine.activate`로 2단 템플릿을 조립하고, `review_fixtures.reviewed_candidate`는 `FakeEngine.environment`를 쓴다. 따라서 `FakeEngine`은 합성 활성 상태 체계 전체의 밑바탕이다.
- 시작 상태 체계에서의 자리: 이 모듈의 정의 대부분은 네 단 밖의 메모리 엔진 대역이다. 엔진은 제품이되 저장소와 일부 메서드가 대역이다. Git 기반 시작 상태는 셋으로 갈린다. 2단 위에 쌓은 것(`start_submission_history`, `start_native_final`), 공개 `initialize` 위에 쌓은 것(`start_query_repository`, `initialized`, `initialized_instance`), 합성 상태를 직접 게시한 것(`start_repair_host`)이다.
- 저장소 대역 셋의 차이: `research_fixtures.StateStore`(`FakeEngine`과 `bare_engine`의 기본값)는 적재와 게시를 흉내 내고 읽기를 막는다. `NoRepository`(`routing_engine`)는 읽기를 막고 게시가 없다. `input_snapshot_store`(`evidence_engine`)는 스냅숏 하나의 적재와 봉인 맥락 하나의 읽기만 허용한다. `context_engine`과 `initial_failure_engine`은 `ResearchRepository` autospec을 저장소로 쓴다.

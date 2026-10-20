# research_fixtures

| 항목 | 값 |
|---|---|
| 원문 | `.claude/skills/do-math/scripts/tests/research_fixtures.py` (1,129행) |
| 정의 수 | 모듈 함수 54, 클래스 4(`StateStore`, `Clock`, `FixtureAdapter`, `_Template`), 모듈 수준 대입 5(`IDENTITY`, `FIXTURE_CAPABILITIES`, `SYNTHETIC_TOOLCHAIN_FILES`, `_EMPTY_GIT_DIR`, `_TEMPLATES`) |
| 이 모듈을 쓰는 시험 모듈 | 85개(`consumers.json` 기준). 이 밖에 픽스처 모듈 8개(`engine_fixtures`, `knowledge_fixtures`, `provider_fixtures`, `purpose_fixtures`, `record_fixtures`, `review_fixtures`, `runner_fixtures`, `state_fixtures`)가 이 모듈을 import한다 |
| 모듈 수준 import | 제품 `do_math.contracts`(`CONTRACT_REVIEW_ITEMS`, `ROLES`), `do_math.control_transport.ControlTransport`, `do_math.execution_profiles.profile_ref`, `do_math.file_io.sha256_file`, `do_math.repository.canonical_json`, `do_math.trust_validation.AXIOMS`. 나머지 제품·픽스처 import는 함수 안에서 늦게 한다 |

## 목적

모듈 docstring(행 1–163)은 이 모듈을 "합성 입력, 프로세스 도우미, 공유 시작 상태"의 모듈이라고 부른다. 첫 문단(행 3–5)은 경계를 긋는다. 모든 권한과 영속화는 여전히 엔진을 거치고, 여기의 어댑터 사실과 Lean 사실은 합성 시험 증거일 뿐이다. 그래서 이 모듈의 값은 호스트 능력, 실제 컴파일러 결과, 실제 사용자의 승인을 입증하지 않는다.

docstring은 네 가지를 정한다.

1. **픽스처 모듈 체계(행 7–34).** 시험 모듈은 픽스처를 이 아홉 픽스처 모듈에서만 가져오고, 다른 시험 모듈에서는 가져오지 않는다. 한 시험 모듈만 쓰는 픽스처는 그 모듈의 모듈 함수로 남는다. 두 번째 모듈이 쓰게 되면 영역에 맞는 픽스처 모듈로 옮긴다. 이 모듈은 여러 영역이 함께 쓰는 입력을 맡는다. 과제 후보, 검토 출력, 헌장과 그 승인, 신뢰 환경, 관찰 규칙, 시계와 배치가 여기에 든다. 프로세스 안의 `git_init`·`run_cli`·`cli_result`, 공개 활성화 `activate`, 역할 도달 판정 `role_reach`, 공유 시작 상태도 이 모듈에 있다.
2. **공유 시작 상태(행 36–95).** 공개 경로로 활성 인스턴스를 만드는 일(`activate`: 여러 제어와 해석 실행 두 번)은 수십 초가 걸린다. Git이나 CLI 자식 프로세스 하나도 눈에 띄는 비용이다. 그래서 그 경로 뒤를 검사하는 시험은 프로세스당 한 번 만든 상태의 사본에서 시작한다. `restore_template`가 그 입구다. 공유 빌드 목록과 한 모듈 전용 빌드 목록도 여기에 적혀 있다.
3. **사본의 규칙(행 97–116)과 빌드 작성법(행 118–132).** 이 두 절은 아래 `restore_template`와 `_Template` 절에서 구현과 대조한다.
4. **공개 경로와 자식 프로세스를 유지할 때(행 134–153), 시나리오를 일찍 멈출 때(행 155–163).** 자식 프로세스를 유지해야 하는 경우는 프로세스 자체가 검사 대상일 때다. 셸이 보는 종료 코드, 표준 입출력 인코딩, `pythonw`, Windows Job, 다른 프로세스의 소유자 식별, 백그라운드 프로세스, 인터프리터 시동이 여기에 해당한다. 같은 프로세스 안에서 다른 기술자가 잡은 잠금도 프로세스 사이처럼 충돌하므로(`file_io.os_lock`), 잠금 경합만을 이유로 자식 프로세스를 쓸 필요는 없다.

`시험-지침.md` 4절 규칙 3은 시작 상태를 네 단으로 나눈다. 1단은 순수 함수 직접 호출, 2단은 `state_fixtures.active_instance`, 3단은 이 모듈의 `activated_instance`와 그 위의 빌드, 4단은 공개 경로다. 규칙 3은 각 도우미의 인자와 복원 규칙의 정본으로 이 docstring을 가리킨다. 규칙 6은 `git init` 대신 `git_init`을, CLI 자식 프로세스 대신 `run_cli`를 쓰라고 정한다. 이 모듈은 3단 빌드와 두 프로세스 대체물, 그리고 2단과 3단이 쓰는 템플릿 기계 `restore_template`를 제공한다.

## 구성

정의는 여덟 무리로 나뉜다. 제목의 순서는 무리 순서이고, 무리 안에서는 원문 순서를 따른다. 화살표(→)는 "부른다"를 뜻한다.

1. **메모리 엔진과 최소 상태.** `bare_engine` → `StateStore`, 제품 `ResearchEngine._init_process_state`. `current_state`, `governance_start`, `installed_contract` → 제품 `record_schemas.install`, `with_validator`. `new_instance` → `git_init`, 제품 `engine.initialize`.
2. **역할 입출력(스크립트 역할이 쓰는 응답 조각).** `read_fixture_context` → 제품 `context_store.read_source`. `role_reach` → 제품 `GitStateStore`, 실제 자식 프로세스 `read_input.py`. 이 무리에는 `candidate`, `bind_candidates`, `review_items`, `contract_review`, `scope_response`, `disposition`, `planning_model_assessments`, `assessment`, `intent_response`도 속한다. `seal_response` → 제품 `integration.mutation_members`, `model_policy.preparation_only`. `supply_observation_rules` → `observation_rule`이고, `prepared_rule_conditions` → `supply_observation_rules`다.
3. **관찰 추적기 입력.** `Clock`, `observation_rule`, `self_check_response`, `write_checkpoint`, `observe`, `acknowledge` → `observe`, `observation_batch` → 제품 `ObservationBatch`.
4. **실행과 제출 수송.** `local_job_runner` → 제품 `WindowsJob`. `dispatched_launch` → 제품 `launch.ticket`. `submit_intent` → 제품 `submission.request_control`, `ControlTransport.wait_receipt`. `await_control`, `await_stop`. `producer_result` → `read_fixture_context`, `bind_candidates`, `seal_response`, `submit_intent`. `sealed_maintenance_submission` → 제품 `submission.install_tools`·`seal_submission`, 그리고 `seal_response`.
5. **어댑터와 신뢰 환경.** `FixtureAdapter`(기본값 `FIXTURE_CAPABILITIES`, 식별 `IDENTITY`). `install_adapter_fixture` → `FixtureAdapter`. `fixture_setup_lean` → `validation_fixture`. `validation_fixture` → 제품 `trust_inventory.validation_program`. `trust_fixture` → `SYNTHETIC_TOOLCHAIN_FILES`, `validation_fixture`, 제품 `trust_inventory`. `trust_environment`.
6. **거버넌스와 공개 제어.** `send_control` → 제품 `engine.control`, `process_controls`. `charter_change`, `policy_change`, `charter`, `charter_record` → `charter`. `approved_governance` → `governance_start`, 제품 `governance.preserve_source`·`initialize_governance`.
7. **공개 활성화, 프로세스 대체물, 템플릿.** `activate` → `send_control`, `charter_record`, `trust_fixture`, 제품 `engine.control`·`model_policy.selection`·`ResearchEngine.run`. `activated_instance` → `git_init`, `FixtureAdapter`, `activate`, `_no_formal_check`, `runner_fixtures.ScriptedRunner`, 제품 `initialize`. `git_init` → `_EMPTY_GIT_DIR`, 실제 `git init` 한 번. `run_cli` → 제품 `cli.main`. `cli_result` → `run_cli`. `restore_template` → `_TEMPLATES`, `_Template` → `remove_tree`.
8. **식별 검토.** `scope_assessment`, `start_scoped_review` → 제품 `review_cycle.start_review`, `input_basis.capture_review_input_basis`, 엔진의 `_start_identity_review`·`_queue_identity_actions`.

모듈 사이에는 순환 import가 하나 있다. `runner_fixtures`는 모듈 머리(행 30–32)에서 이 모듈의 함수 열두 개를 import한다. 이 모듈은 `activated_instance` 안에서만 `from runner_fixtures import ScriptedRunner`를 늦게 한다(행 932). 그래서 순환은 import 시점에 걸리지 않는다.

## 1. 메모리 엔진과 최소 상태

### `bare_engine(instance=None, runtime=None, *, head="fixture-head", store=None, runner=None, formal_verifier=None)` (행 192–208)
- 종류: 대역(저장소 없는 실제 엔진 객체).
- 하는 일과 반환값: `object.__new__(ResearchEngine)`로 `__init__`를 건너뛰어 저장소를 읽지 않은 엔진을 만든다. 이어서 제품의 `_init_process_state()`를 불러 로드된 엔진과 같은 프로세스 지역 소유자 상태 속성을 모두 갖추게 한다(docstring 행 196–197). `instance`, `runtime`, `head`, `runner`, `formal_verifier`를 인자 그대로 붙이고, `store`가 없으면 이 모듈의 `StateStore(engine)`를 붙인다. 반환값은 그 엔진이다.
- 부작용: 없다. 디스크와 Git을 건드리지 않는다. docstring(행 197–199)이 짚는 점이 있다. `_save`는 상태를 `store.published_state(head)`와 비교한다. 그런데 `StateStore`는 어떤 헤드에도 `None`을 돌려주므로, 첫 `_save`는 언제나 `store`로 게시된다.
- 의존: `StateStore`, 제품 `do_math.engine.ResearchEngine`.
- 시작 상태의 단: 네 단 밖의 "메모리 엔진"이다. 1단처럼 저장소는 없지만 엔진 메서드를 그대로 부를 수 있다.
- 소비자: `engine_fixtures`, `knowledge_fixtures`, `review_fixtures`, `test_academic`, `test_completion_settlement`, `test_decision_basis`, `test_environment_validation`, `test_execution_lifecycle`, `test_family_records`, `test_goal_audit`, `test_host_resources`, `test_impact_review`, `test_initialization_probe_batch`, `test_input_recovery`, `test_installation_discovery`, `test_knowledge_import_engine`, `test_knowledge_storage`, `test_lifecycle_gates`, `test_machine_scheduling`, `test_model_metadata_boundary`, `test_observations`, `test_provider_final_contract`, `test_provider_recovery`, `test_provider_wait`, `test_purpose_engine`, `test_question_flow`, `test_questions`, `test_repair_execution`, `test_reporting`, `test_repository`, `test_research_recovery`, `test_review_engine`, `test_review_scope_wire`, `test_revision_obligations`, `test_state_checks`, `test_submission_flow`, `test_task_contracts`, `test_task_scope`, `test_trust_continuation`.

### `current_state(instance=None, runtime=None)` (행 211–225)
- 종류: 함수(최소 상태 레코드).
- 하는 일과 반환값: 현재 상태 계약이 받는 가장 작은 `(instance, runtime)` 쌍을 돌려준다. 원본 입력 바이트는 `b"fixture input"`이다. `instance`의 `lifecycle`은 `state="initializing"`, `input_id="UI-fixture"`, `immutable_input`(본문, SHA-256, 바이트 수)을 갖는다. `runtime`은 `status="initializing"`, `last_observed_utc="2026-01-01T00:00:00+00:00"`, 입력 행 하나(`UI-fixture`, 같은 본문과 해시, `config={"goal": "fixture"}`, `created_at`)를 갖는다. 호출자의 사전은 얕게 덮어쓴다(`{**기본, **호출자}`). 그래서 호출자가 `lifecycle`을 주면 기본 `lifecycle`은 통째로 대체된다.
- 부작용: 없다.
- 의존: 없다(`hashlib`만 쓴다). docstring은 이 모양의 근거로 제품 `record_schemas.validate_lifecycle`을 든다(행 214–216).
- 시작 상태의 단: 1단.
- 소비자: `engine_fixtures`, `provider_fixtures`, `record_fixtures`, `review_fixtures`, `test_cli_surface`, `test_design_walkthroughs`, `test_engine`, `test_execution_lifecycle`, `test_family_records`, `test_host_resources`, `test_impact_review`, `test_integration_bundles`, `test_knowledge`, `test_knowledge_io`, `test_knowledge_storage`, `test_observations`, `test_payloads`, `test_repository`, `test_retention`, `test_review_engine`, `test_session_scheduler`, `test_state_checks`, `test_state_contract`, `test_supervisor_recovery`, `test_task_contracts`, `test_unicode_flow`.

### `governance_start(instance=None)` (행 228–234)
- 종류: 함수.
- 하는 일과 반환값: 빈 거버넌스 가족 네 개(`governance`, `governance_sources`, `decisions`, `grants`)를 가진 사전에 `instance`를 덮어 돌려준다. docstring(행 229–233)에 따르면 이 네 가족은 제품 `initialization.initialize_state`가 모든 인스턴스에 주는 것이다. 작은 인스턴스로 거버넌스 함수를 부르는 도메인 시험은 함수가 이 가족을 만들어 주리라 기대하지 않고 여기서 시작한다. `instance`에 같은 키가 있으면 `instance`의 값이 이긴다.
- 부작용: 없다.
- 의존: 없다.
- 시작 상태의 단: 1단.
- 소비자: `engine_fixtures`, `review_fixtures`, `test_context_store`, `test_engine`, `test_external_operations`, `test_family_records`, `test_governance`, `test_governance_engine`, `test_role_input`. 모듈 안에서는 `approved_governance`가 부른다.

### `installed_contract()` (행 237–247)
- 종류: 함수.
- 하는 일과 반환값: 새 `StateContract()`를 만들고 제품 `record_schemas.install`로 설치된 가족을 모두 등록해 돌려준다. docstring(행 238–241)에 따르면 저장소들은 가족이 늘지 않는 `default_state_contract()`를 공유한다. 그래서 가족을 더하려는 시험은 자기 계약을 따로 가져야 한다.
- 부작용: 없다.
- 의존: 제품 `do_math.record_schemas.install`, `do_math.state_contract.StateContract`.
- 시작 상태의 단: 1단.
- 소비자: `test_family_records`, `test_payloads`, `test_repository`, `test_state_contract`, `test_unicode_flow`.

### `with_validator(contract, root, name, validator)` (행 250–255)
- 종류: 함수.
- 하는 일과 반환값: 시험이 소유한 `contract`의 가족 `(root, name)` 하나의 레코드 검증기를 `validator`로 바꾼다. 구현은 `dataclasses.replace(contract.family(root, name), validator=validator)`를 비공개 사전 `contract._families[root, name]`에 다시 넣고, 캐시된 매니페스트를 `contract._manifest = None`으로 무효화한다. 반환값은 같은 `contract`다.
- 부작용: 인자 `contract`를 제자리에서 바꾼다. 제품의 비공개 속성(`_families`, `_manifest`)에 직접 쓴다.
- 의존: 제품 `StateContract.family`.
- 시작 상태의 단: 1단.
- 소비자: `test_family_records`, `test_repository`, `test_state_contract`.

### `StateStore` (행 258–288)
- 종류: 대역(메모리 엔진의 게시 헤드).
- 하는 일: docstring(행 259–267)에 따르면 메모리 엔진이 닿는 저장소 호출만 구현한다. 다른 저장소 사용은 저장소가 없을 때처럼 실패한다(속성 부재로 `AttributeError`).
- 클래스 속성 `git_dir` (행 269): `None`이다. Git 디렉터리가 없으므로 어떤 프로세스 캐시도 이 저장소의 읽기를 기록하지 않는다(docstring 행 266–267).
- `__init__` (행 271–273): `engine`을 붙잡고, 게시 기록 목록 `published`를 빈 목록으로 둔다.
- `published_state` (행 275–276): 어떤 헤드에도 `None`을 돌려준다. 캐시된 상태가 없으므로 엔진의 `_save`는 언제나 게시로 간다.
- `load` (행 278–279): `(engine.head, deepcopy(engine.instance), deepcopy(engine.runtime))`를 돌려준다. 곧 엔진의 현재 메모리 상태를 그 헤드의 게시 상태로 읽는다. `snapshot` 인자는 무시한다.
- `read` (행 281–283): 언제나 `AssertionError("an in-memory engine double stores no artifact: " + path)`를 던진다. 주석(행 282)에 따르면 엔진은 이 읽기 함수를 소비자에게 넘기는데, 여기에는 저장된 산출물이 없다.
- `save_with_state` (행 285–288): 후보 상태를 깊은 사본으로 `published`에 덧붙인다(`instance`, `runtime`, `artifacts`의 얕은 사전 사본). 반환값은 새 헤드 문자열 `f"{expected_head}+{len(published)}"`와 두 상태의 깊은 사본이다. `retain` 인자는 무시한다. 헤드 경합은 검사하지 않는다.
- 부작용: 메모리 안의 `published` 목록만 바꾼다.
- 의존: 없다.
- 소비자: `engine_fixtures`(`FakeEngine.__init__`이 붙인다). 모듈 안에서는 `bare_engine`이 기본 저장소로 쓴다.

### `new_instance(repository, *, goal, workspace=None, **options)` (행 291–301)
- 종류: 함수(공개 초기화).
- 하는 일과 반환값: `git_init(repository)`로 빈 Git 저장소를 만들고, 제품 `do_math.engine.initialize(repository, goal=goal, workspace=..., **options)`를 부른다. 작업 공간 기본값은 `repository / "work"`다. 반환값은 결과의 `instance_id`다.
- 부작용: `repository`에 `.git`을 복사해 만든다(`git_init` 참조). 제품 초기화가 첫 상태를 Git에 게시하고 작업 공간을 만든다.
- 의존: `git_init`, 제품 `initialize`.
- 시작 상태의 단: 4단의 앞부분이다. 공개 초기화만 돌고 활성화는 하지 않는다.
- 소비자: `test_context_store`, `test_controls`, `test_delegations`, `test_governance_engine`, `test_host_resources`, `test_initial_intent_connection`, `test_knowledge_import_engine`, `test_observation_admission`.

## 2. 역할 입출력

### `read_fixture_context(prompt, workspace)` (행 304–325)
- 종류: 함수.
- 하는 일과 반환값: 스크립트 역할에게 보인 것과 같은 로컬 원천을 읽는다(docstring 행 305). 먼저 프롬프트에서 표지 `--- CANONICAL INPUT CONTEXT ---\n`와 `\n--- OUTPUT JSON SCHEMA ---` 사이의 JSON을 파싱한다. 원천 참조는 안쪽 함수 `read`가 읽는다. `read`는 제품 `context_store.read_source(workspace, reference, limit=max(1, reference['bytes']))`를 부른다. 상태가 `ok`가 아니거나 잘렸으면(`truncated`) `AssertionError('Supplied context source could not be read exactly: ...')`를 던진다. 읽은 바이트는 JSON으로 풀고, `json_pointer`가 있으면 그 토큰을 따라 내려간다. 목록에서는 토큰을 정수 색인으로 쓴다. 치환은 세 가지다.
  - 최상위 항목 가운데 `source_ref.path`를 가진 사전은 읽은 내용으로 통째로 바꾼다.
  - `tasks`의 각 과제에 `source_ref`가 있으면, 과제 사전에 읽은 내용을 병합한 새 사전으로 그 과제를 바꾼다.
  - 과제의 `results`, `reviews`, `revision_history`, `assessment_history`는 `<필드>_source`가 있으면 그 참조를 읽어 채운다.

  반환값은 원천이 풀린 입력 문맥 사전이다.
- 부작용: 없다(읽기만 한다).
- 의존: 제품 `do_math.context_store.read_source`.
- 소비자: `purpose_fixtures`, `runner_fixtures`(`context_from`), `test_currentness`. 모듈 안에서는 `producer_result`가 부른다.

### `role_reach(prompt, workspace, secret)` (행 328–356)
- 종류: 함수(도달 판정기).
- 하는 일과 반환값: 준비된 역할 입력에서 `secret`이 역할에게 닿는 경로를 모두 찾는다. docstring(행 331–336)에 따르면 역할이 읽는 것은 셋이다. 렌더링된 프롬프트, 작업 공간 파일(고정 입력), 설치된 읽기 도구로 `record_map`이 허용하는 입력 스냅숏이다. 절차는 다음과 같다.
  1. 프롬프트에 `secret`이 있으면 `reached`에 `"prompt"`를 넣는다.
  2. 작업 공간의 모든 파일 가운데 바이트로 `secret`을 품은 파일의 상대 POSIX 경로를 정렬해 더한다.
  3. `input/submission/context.json`의 `record_store`(저장소 경로, 인스턴스 ID)로 제품 `GitStateStore`를 열고, `snapshot`의 트리 경로를 모두 `read_many`로 읽는다. `secret`을 품은 경로의 목록이 `held`다.
  4. 요청 인자를 만든다. `record_index`에 나오는 모든 ID에 `--id <ID>`를, `held`의 각 경로에 `--path <경로>`를 붙인다.
  5. 요청이 있으면 실제 자식 프로세스 `sys.executable -B input/tools/read_input.py ...`를 작업 공간에서 돌린다(`capture_output=True`, `timeout=120`). 역할이 도구를 돌리는 방식 그대로다. 출력의 `records` 행 가운데 `status == "ok"`이고 JSON 직렬화에 `secret`이 든 행마다 `"read_input.py " + row["request"]`를 `reached`에 더한다.

  반환값은 `(reached, held)`다. docstring에 따르면 `held`가 비었다는 것은 스냅숏이 비밀을 품은 적이 없다는 뜻이므로, 그때의 `reached`는 아무것도 입증하지 않는다.
- 부작용: 실제 Python 자식 프로세스 하나를 띄운다(설치된 읽기 도구 실행). 파일에는 쓰지 않는다.
- 의존: 제품 `do_math.git_store.GitStateStore`(`tree_paths`, `read_many`), 작업 공간에 설치된 `input/tools/read_input.py`.
- 소비자: `test_review_research`, `test_role_input`.

### `candidate(title="task", *, formal=False, revises=None, refs=None)` (행 359–370)
- 종류: 함수(준비 역할 출력의 과제 후보 한 행).
- 하는 일과 반환값: 과제 후보 사전을 돌려준다. 필드는 다음과 같다.
  - `revises_task_id=revises`, `title`
  - 질문 "Can the stated natural-number identity be established?"
  - 범위: 포함 "Natural numbers and addition of zero", 제외 "Other domains"
  - 기대 출력과 연구 변화
  - 진행 기준 `PC-argument` 하나
  - 완료 의무 `OB-argument` 하나(`judges=["research_plan"]`, 필요 증거 없음)
  - `inputs`와 `reuse`는 둘 다 `list(refs or [])`, `dependencies`·`profile_refs`·`authority_refs`·`basis_refs`는 빈 목록
  - `work_class`는 `formal`이 참이면 `"formal"`, 아니면 `"nonformal"`
- 부작용: 없다.
- 의존: 없다.
- 소비자: `purpose_fixtures`, `runner_fixtures`, `test_academic_preparation`, `test_context_store`, `test_contract_checks`, `test_currentness`, `test_decision_basis`, `test_engine`, `test_family_records`, `test_host_resources`, `test_live_observation`, `test_model_assessment_flow`, `test_model_metadata_boundary`, `test_planning_engine`, `test_repetition`, `test_role_input`, `test_session_scheduler`, `test_submission_boundaries`, `test_submission_checks`, `test_submission_flow`, `test_submission_tools`, `test_task_contracts`.

### `bind_candidates(output, context)` (행 373–381)
- 종류: 함수.
- 하는 일과 반환값: 저자에게 실제로 공급된 작업 프로필과 현재 권한만 후보에 묶는다(docstring 행 374). `output["candidates"]`의 각 행이 대상이다.
  - `profile_refs`에는 `context["execution_profiles"]` 가운데 역할이 `research_work`인 프로필의 참조(`profile_ref`)를 넣는다. `context["role_profile_refs"]["research_work"]`가 있으면 그 목록에 든 것만 넣는다.
  - `authority_refs`에는 `context["grants"]` 가운데 `status == "active"`이고 역할에 `research_work`가 든 권한의 ID를 넣는다.

  반환값은 없다(`None`). `output`을 제자리에서 바꾼다.
- 부작용: 인자 사전 변경.
- 의존: 제품 `execution_profiles.profile_ref`.
- 소비자: `purpose_fixtures`, `runner_fixtures`, `test_purpose_engine`. 모듈 안에서는 `producer_result`가 부른다.

### `review_items(evidence_refs, *, decision="approved", next_owner="research_plan", findings=())` (행 384–389)
- 종류: 함수(과제 계약 검토 출력).
- 하는 일과 반환값: 제품 `contracts.CONTRACT_REVIEW_ITEMS`의 모든 항목을 똑같이 판정한 `{"item_reviews": [...]}`를 돌려준다. 각 행의 필드는 `decision`, `evidence_refs`(인자의 목록 사본), `findings`, `next_owner`, `missing_inputs`다. `missing_inputs`는 `decision == "unresolved"`일 때만 `["Contract clarification"]`이다. 검토 항목 목록을 시험에 다시 적지 않고 제품 상수에서 가져오는 것은 `시험-지침.md` 4절 규칙 7을 따른 것이다.
- 부작용: 없다.
- 의존: 제품 `CONTRACT_REVIEW_ITEMS`.
- 소비자: `engine_fixtures`, `record_fixtures`, `test_academic`, `test_contracts`, `test_submission_checks`, `test_task_contracts`. 모듈 안에서는 `contract_review`가 부른다.

### `contract_review(context, *, decision="approved", findings=())` (행 392–396)
- 종류: 함수(스크립트 역할 `task_contract_review`의 응답).
- 하는 일과 반환값: `context["task"]`에 `completion_obligations`와 `scope`가 모두 있어야 한다. 하나라도 비었으면 `AssertionError("The review fixture requires the actual structured contract")`를 던진다. 곧 검토 대역이 실제 구조화된 계약을 받았는지 스스로 검사한다. 통과하면 `review_items([task["id"]], decision=..., next_owner="research_preparation", findings=...)`를 돌려준다.
- 부작용: 없다.
- 의존: `review_items`.
- 소비자: `purpose_fixtures`, `runner_fixtures`, `test_currentness`, `test_decision_basis`, `test_engine`, `test_model_assessment_flow`, `test_revision_obligations`, `test_session_scheduler`, `test_submission_boundaries`.

### `scope_response(context)` (행 399–415)
- 종류: 함수(식별 검토 범위 단계의 응답).
- 하는 일과 반환값: `context["role_review"]`와 그 안의 `review_policy`를 읽는다. 관점 목록은 정책의 `required_perspectives`에서 시작한다. `minimum_initial_slots`에 모자라면 "Statement and proof"와 "Explanation and domain"을 차례로 채운다. 그래도 모자라면 `AssertionError("The explicit fixture only defines two independent perspectives")`를 던진다. 반환값의 필드는 다음과 같다.
  - `proposal_digest`: 검토 문맥의 값 그대로
  - `scope_complete=True`
  - `scope_assessment`
    - `assessment_id`: `"fixture-full-scope"`
    - `policy_id`
    - `required_perspectives`: 정책의 목록 사본
    - `initial_slots`: ID는 `initial-<i>`, 관점은 위 목록, `required_source_refs=["proposal"]`
    - `selected_profile_ref`: `context["execution_profile"]`의 참조
    - `activity_execution_limit`, `overflow_disposition`: 정책에서 가져온다
- 부작용: 없다.
- 의존: 제품 `profile_ref`.
- 소비자: `purpose_fixtures`, `runner_fixtures`(식별 검토 `scope` 단계에서 늦게 import), `test_review_scope_wire`.

### `disposition(task_id, *, kind="selected")` (행 418–422)
- 종류: 함수(계획 역할 처분 한 행).
- 하는 일과 반환값: `task_id`, `kind`, 고정된 `reason`·`uncertainty`·`expected_research_change`를 담은 처분 행을 돌려준다. `parallel_task_ids`와 `missing_inputs`는 빈 목록이고, `revisit`은 `{"event_refs": [], "at": None}`이다. `next_owner`는 `kind`와 관계없이 `"research_work"`다. 이 점이 `record_fixtures.task_disposition`과 다르다. 그 함수는 `kind`에 따라 `next_owner`와 `missing_inputs`를 바꾼다.
- 부작용: 없다.
- 의존: 없다.
- 소비자: `purpose_fixtures`, `runner_fixtures`, `test_academic`, `test_family_records`, `test_model_metadata_boundary`, `test_purpose_engine`, `test_research_recovery`, `test_submission_boundaries`, `test_submission_tools`.

### `planning_model_assessments(output, context)` (행 425–437)
- 종류: 함수(계획 역할의 모델 재평가 확장 행).
- 하는 일과 반환값: `output["dispositions"]` 가운데 `kind == "selected"`인 과제마다 문맥 `tasks`에서 그 과제의 `model_assessment`를 찾는다. 과제가 문맥에 없거나 평가가 공급되지 않았으면 `AssertionError('The planning fixture cannot assess a selected task without its supplied model assessment')`를 던진다. 있으면 `difficulty`와 `importance`를 그대로 옮기고 고정 `reason`을 붙인 행을 만든다. 반환값은 그 행들의 목록이다.
- 부작용: 없다.
- 의존: 없다.
- 소비자: `purpose_fixtures`, `runner_fixtures`, `test_engine`, `test_purpose_engine`.

### `supply_observation_rules(candidates, extensions)` (행 478–489)
- 종류: 함수(준비 역할의 활동 확장).
- 하는 일과 반환값: 후보가 없으면 아무것도 하지 않는다. 있으면 `extensions["task_conditions"]`(없으면 만든다)에서 후보 제목과 `task_title`이 같은 행을 찾고, 없으면 새 행을 더한다. 그 행에 `observation_rules`가 아직 없을 때만 규칙 하나를 넣는다. 규칙은 `observation_rule(threshold=10, id='fixture-attempts', required_evidence=['checkpoint.json'])`, 곧 체크포인트 카운터 `attempts`가 10 이상인지 보는 규칙이다. 반환값은 없다. docstring(행 479)은 이를 "스크립트 짧은 과제를 위한 명시적 체크포인트 카운터 정책"이라 부른다.
- 부작용: `extensions`를 제자리에서 바꾼다.
- 의존: `observation_rule`.
- 소비자: `purpose_fixtures`, `record_fixtures`, `runner_fixtures`, `test_input_recovery`, `test_model_assessment_flow`, `test_state_checks`, `test_submission_boundaries`. 모듈 안에서는 `prepared_rule_conditions`가 부른다.

### `prepared_rule_conditions(task_ids)` (행 544–549)
- 종류: 함수.
- 하는 일과 반환값: 기존 과제에 관찰 규칙을 준비하도록 배정된 준비 역할의 응답 조각이다(docstring 행 545). 각 ID를 `{'title': ID}` 후보로 보아 `supply_observation_rules`를 돌린다. 반환값은 `[{'task_id': ID, 'observation_rules': [...]}]` 목록이다.
- 부작용: 없다.
- 의존: `supply_observation_rules`.
- 소비자: `purpose_fixtures`, `runner_fixtures`, `test_academic`, `test_academic_preparation`, `test_model_assessment_flow`, `test_model_metadata_boundary`, `test_stop_flags`.

### `assessment(task)` (행 552–559)
- 종류: 함수(계획 역할의 과제 평가 한 행).
- 하는 일과 반환값: `task["results"]`가 비었거나 보고서(`report`)가 빈 행이 있으면 `AssertionError("Completion fixture requires a supplied nonempty report")`를 던진다. 통과하면 `decision="completed"`인 평가를 돌려준다. 이 평가는 각 완료 의무를 `fulfilled`로 처분하고, 증거는 모든 결과 행의 `execution_id`다. `unresolved`는 빈 목록이다.
- 부작용: 없다.
- 의존: 없다.
- 소비자: `purpose_fixtures`, `runner_fixtures`, `state_fixtures`, `test_academic_engine`, `test_context_store`, `test_engine`, `test_submission_boundaries`.

### `intent_response(context)` (행 562–579)
- 종류: 함수(의도 해석 역할의 두 단계 응답).
- 하는 일과 반환값: 단계는 `context["action"]["stage"]`로 고르고, 기본값은 `interpret`이다.
  - **`interpret` 단계:** 사용자 요청 원문 전체를 하나의 가져오기 단위 `IU-original`로 해석한다. 단위의 원천 범위는 `0`부터 본문 길이까지이고, 해석 문자열은 본문 그대로다. `owner_kind="charter"`, `owner_ref`는 현재 헌장 ID, `payload={}`이며, 질문은 없다.
  - **확인 단계:** `context["interpretation_to_check"]` 묶음의 단위 해석을 이어 붙인 문자열이 원천 본문과 같아야 한다. 다르면 `AssertionError("This fixture only approves verbatim, complete interpretation")`를 던진다. 같으면 `decision="approved"`, `scope_complete=True`와 함께 묶음 해시, 단위 ID들, 질문 ID들, 빈 `findings`를 돌려준다.
- 부작용: 없다.
- 의존: 없다.
- 소비자: `engine_fixtures`(`FakeEngine.activate`), `purpose_fixtures`, `runner_fixtures`, `test_engine`.

### `seal_response(output, context, workspace)` (행 582–612)
- 종류: 함수(생산자 통합 묶음 선언).
- 하는 일과 반환값: 생산자가 자기 출력과 확장의 실제 좌표를 결합 단위 하나로 선언한다(docstring 행 583). 절차는 다음과 같다.
  1. 구성원 목록을 `["output"]`로 시작한다.
  2. 역할이 `research_preparation`일 때, 제품 `model_policy.preparation_only(action)`가 거짓이고 문맥에 `observed_at`이 있으면 `output`의 `regenerate_after`를 관찰 시각에서 한 시간 뒤로 채운다. 값이 이미 있으면 두는 `setdefault`다.
  3. 역할이 `research_work`나 `supplemental_research`이고 행동에 `review_cycle_id`가 없으면 `output/knowledge/<i>`와 `output/relations/<i>`를 구성원에 더한다.
  4. 작업 공간의 `activity-extensions.json`이 있으면 읽어서 `activity-extensions.json/<가족>/<i>`를 모두 더한다.
  5. 묶음 ID를 정한다. 값은 `"IN-"`에 `canonical_json({"action", "output", "extensions"})`의 SHA-256 앞 24자를 붙인 것이다.
  6. 제품 `integration.mutation_members(output, extensions)`가 내는 변경 대상 ID마다 이전 해시를 구한다. 대상은 문맥의 `tasks`나 `knowledge_catalog`에 보이고 `content_sha256`을 가진 레코드여야 한다. 아니면 `AssertionError("The fixture cannot revise a record absent from its fixed input: ...")`를 던진다.
  7. `output["integration_bundles"]`를 묶음 하나로 덮어쓴다. 그 묶음의 `impact_set`과 `authority_refs`는 빈 목록이고, `previous_hashes`는 6에서 구한 사전이다.

  반환값은 바뀐 `output`이다.
- 부작용: `output`을 제자리에서 바꾼다. 확장 파일은 읽기만 한다.
- 의존: 제품 `integration.mutation_members`, `model_policy.preparation_only`, `repository.canonical_json`.
- 소비자: `engine_fixtures`, `purpose_fixtures`, `runner_fixtures`, `test_academic_preparation`, `test_engine`, `test_input_recovery`, `test_model_assessment_flow`, `test_purpose_engine`, `test_role_input`, `test_submission_flow`, `test_submission_tools`, `test_task_scope`. 모듈 안에서는 `producer_result`와 `sealed_maintenance_submission`이 부른다.

## 3. 관찰 추적기 입력

### `Clock` (행 440–443)
- 종류: 대역(설정 가능한 시계).
- 하는 일: `ObservationTracker`의 `clock` 인자(제품 기본값 `time.monotonic`) 자리에 주입하는 설정 가능한 시계다. 호출하면 `value`를 돌려준다(docstring 행 441). 값은 시험이 정하므로 단조 증가를 보장하지 않는다.
- `__init__` (행 442): `value`를 `0`으로 둔다.
- `__call__` (행 443): 현재 `value`를 돌려준다. 시험은 `value`를 직접 바꿔 시간을 진행시킨다.
- 부작용: 없다.
- 의존: 없다.
- 소비자: `test_controls`, `test_design_walkthroughs`, `test_live_observation`, `test_observations`.

### `observation_rule(operator="counter_gte", subject_kind="counter", subject_id="attempts", threshold=2, **changes)` (행 446–460)
- 종류: 함수(관찰 규칙 한 행).
- 하는 일과 반환값: 규칙 `R-1`을 돌려준다. 주체는 `{"kind": subject_kind, "id": subject_id}`, 임계값은 `threshold`, 필요 증거는 `["EV-1"]`이다. `basis`의 `source`와 `unit`은 제품 `observations.OPERATORS[operator]`에서 가져온다. 그래서 연산자의 근거 원천과 단위를 시험이 다시 적지 않는다. `changes`는 필드를 덮거나 더한다. docstring 행 449–451은 `id`, `required_evidence`, `basis`, `repeat_interval`을 예로 든다.
- 부작용: 없다.
- 의존: 제품 `do_math.observations.OPERATORS`.
- 소비자: `test_controls`, `test_design_walkthroughs`, `test_execution_profiles`, `test_live_observation`, `test_observations`. 모듈 안에서는 `supply_observation_rules`가 부른다.

### `self_check_response(obligation, status="normal", evidence=None)` (행 463–475)
- 종류: 함수(작업자의 자기 점검 응답).
- 하는 일과 반환값: 전달된 자기 점검 의무에 대한 작업자의 답을 만든다. 의무의 `id`, `execution_id`, `rule_revision`을 옮기고 고정된 `progress`, `attempts`, `next_method`를 붙인다. `obligation["due"]`의 각 규칙에 결과 행 하나를 준다. 결과 행의 필드는 다음과 같다.
  - `status`: 인자 값
  - `evidence_refs`: `evidence`가 주어지면 그 값, 아니면 규칙의 `required_evidence`
  - `missing_evidence_refs`: `status == "indeterminate"`일 때만 규칙의 필요 증거
  - `reason`: `"artifact comparison"`
- 부작용: 없다.
- 의존: 없다.
- 소비자: `test_controls`, `test_observations`.

### `write_checkpoint(workspace, *, counters=None, iteration=None, claim="fixture progress")` (행 492–500)
- 종류: 함수.
- 하는 일과 반환값: 유효한 작업자 체크포인트를 `workspace/checkpoint.json`에 쓴다. 기본 필드는 `current_claim`, `evidence_paths`, `attempts`, `remaining_work`, `next_step="continue"`, `progress_state="working"`이다. `counters`와 `iteration`은 주어진 경우에만 더한다. docstring(행 493)에 따르면 추적기는 카운터와 반복 횟수를 이 파일에서만 읽는다. 반환값은 없다.
- 부작용: 파일 하나를 쓴다.
- 의존: 없다.
- 소비자: `test_controls`, `test_currentness`, `test_design_walkthroughs`, `test_live_observation`, `test_observations`.

### `observe(tracker, event, **options)` (행 503–513)
- 종류: 함수.
- 하는 일과 반환값: `event`를 다음 1바이트짜리 스트림 행으로 보고 `tracker.observe(event, source=..., **options)`를 부른다. 원천 좌표는 다음과 같다.
  - `stream="stdout.jsonl"`
  - `start_offset`: 직전 `tracker.observation_source`의 `end_offset`, 없으면 0
  - `end_offset`: `start_offset + 1`
  - `received_at`: 현재 UTC 시각
  - `received_monotonic`: `tracker.clock()`

  docstring(행 506–507)에 따르면 러너는 모든 행을 스트림 좌표와 함께 전달한다(`ObservationBatch.source`). 이 함수는 스트림 파일 없이 단위 시험에 같은 좌표를 준다. 반환값은 추적기의 반환값이다.
- 부작용: 추적기 상태 변경(제품 동작).
- 의존: 제품 `ObservationTracker.observe`.
- 소비자: `test_claude_adapter`, `test_controls`, `test_currentness`, `test_design_walkthroughs`, `test_live_observation`, `test_observations`. 모듈 안에서는 `acknowledge`가 부른다.

### `acknowledge(tracker, obligation_id)` (행 516–529)
- 종류: 함수.
- 하는 일과 반환값: 열린 자기 점검 요청을 전달하고, 작업자가 그 요청을 성공적으로 폴링했음을 관찰시킨다. 절차는 다음과 같다.
  1. `tracker.issue_self_check(obligation_id)`로 요청을 받는다.
  2. `tracker.record_delivery(obligation_id, source_offset=...)`로 전달을 기록한다. 오프셋은 직전 원천의 끝, 없으면 0이다.
  3. 폴링 사건을 만든다. `item.completed` 유형이고, 항목은 `mcp_tool_call`이다. 항목 ID는 `poll-<ID>`, 서버는 제품 `CONTROL_SERVER`, 도구는 `SELF_CHECK_TOOL`, 인자는 `self_check_id`이며, 결과 본문은 요청의 JSON이다.
  4. 그 사건을 `observe(..., evaluate=False)`로 관찰한다.
  5. 끝으로 맨 `assert`로 의무의 `acknowledged_call_id`가 `poll-<ID>`인지 확인한다.

  docstring(행 519)에 따르면, 이 뒤에 추적기가 연구 행동을 관찰하면 그 행동은 열린 요청을 위반한다. 반환값은 없다.
- 부작용: 추적기 상태 변경.
- 의존: `observe`, 제품 `control_transport.CONTROL_SERVER`·`SELF_CHECK_TOOL`.
- 소비자: `test_live_observation`, `test_observations`.

### `observation_batch(events=(), *, received_monotonic, stream_path, start=0, terminated=False)` (행 532–541)
- 종류: 함수.
- 하는 일과 반환값: 러너가 한 번 읽은 배치를 흉내 낸다. 각 사건을 `json.dumps(event)`에 줄바꿈을 붙인 바이트 행으로 만들고, `start`부터 연속된 `(시작, 끝)` 오프셋을 매긴다. 이것으로 제품 `ObservationBatch`를 만들어 돌려준다. 필드 값은 다음과 같다.
  - `events`, `offsets`, `rows`: 위에서 만든 값
  - `first_row=0`
  - `received_at`: 현재 UTC
  - `received_monotonic`: 인자 값
  - `end_offset`: 마지막 위치
  - `stream_path`: `Path(stream_path)`
  - `is_terminated`: `terminated`를 돌려주는 람다
- 부작용: 없다. 스트림 파일은 쓰지 않는다.
- 의존: 제품 `do_math.observation_transport.ObservationBatch`.
- 소비자: `purpose_fixtures`, `test_live_observation`, `test_observations`, `test_session_scheduler`.

## 4. 실행과 제출 수송

### `local_job_runner(method)` (행 615–645)
- 종류: 대역 장치(러너 메서드 데코레이터).
- 하는 일과 반환값: 스크립트 모델 호출에 실제 로컬 프로세스 수명을 준다. 그 수명에는 상한이 있다(docstring 행 616). 데코레이터는 `functools.wraps`로 감싼 `run(self, **arguments)`를 돌려준다.
  - **중첩 방지:** 받은 `on_started` 콜백에 속성 `fixture_job`이 참이면, 그 콜백은 바깥 래퍼의 `started`다. 잡은 그 `started`가 불릴 때 바깥 래퍼가 만들므로, 안쪽 래퍼는 잡을 만들지 않고 원 메서드를 그대로 부른다.
  - **대체 콜백:** 그렇지 않으면 `started(_reported_identity=None)`를 만들어 `on_started` 자리에 넣고 원 메서드를 부른다. 원 메서드가 넘기는 식별 인자는 쓰지 않는다. 원 메서드가 이 콜백을 부르면 다음이 일어난다.
    1. 제품 `WindowsJob`으로 `[sys.executable, "-c", "import time; time.sleep(600)"]`를 띄운다. 작업 디렉터리는 인자의 `workspace`, 잡 이름은 `launch_ticket['job_name']`이다. 제품 docstring에 따르면 `WindowsJob`은 멈춘 채 만들어진 루트 프로세스 하나를 kill-on-close 잡에 원자적으로 넣은 것이다.
    2. 제품 `process_identity(job)`에 `job_name`을 더해 원래 콜백을 부른다.
    3. `job.resume()`으로 루트를 시작한다.

    콜백이 두 번 불리면 `AssertionError("A scripted call must start exactly once")`를 던진다.
  - **정리:** `finally`에서 잡이 만들어졌으면 `terminate()`한 뒤 10초 안에 끝나지 않거나 `inspect().active_processes`가 남으면 `AssertionError("The fixture child did not terminate")`를 던진다. 어느 경우든 `job.close()`한다.
- 부작용: 원 메서드가 콜백을 부른 호출마다 실제 Python 자식 프로세스 하나를 실제 Windows Job 안에서 띄우고 끝낸다. 그 자식은 `time.sleep(600)`만 하고, 응답을 만드는 일은 시험 프로세스 안의 원 메서드가 한다. 엔진은 이 프로세스의 식별을 실제 실행의 식별로 기록한다.
- 의존: 제품 `do_math.windows_job.WindowsJob`, `process_identity`.
- 소비자: `purpose_fixtures`, `runner_fixtures`(`ScriptedRunner.run`에 붙는다), `test_checkpoint_persistence`, `test_currentness`, `test_engine`, `test_input_recovery`, `test_model_assessment_flow`, `test_provider_recovery`, `test_question_flow`, `test_research_recovery`, `test_review_research`, `test_session_scheduler`, `test_submission_tools`.

### `dispatched_launch(execution_id, profile)` (행 648–653)
- 종류: 함수.
- 하는 일과 반환값: 제품 `launch.ticket(execution_id, profile)`로 실행 표를 만들고 `phase`를 `'dispatched'`로 바꿔 돌려준다. docstring(행 649)은 이것을 "네이티브 경계 픽스처가 쓰는 현재의 명시적 러너 계약"이라 부른다.
- 부작용: 없다.
- 의존: 제품 `do_math.launch.ticket`.
- 소비자: `engine_fixtures`, `knowledge_fixtures`, `test_checkpoint_persistence`, `test_claude_adapter`, `test_currentness`, `test_execution_profiles`, `test_goal_audit`, `test_governance_engine`, `test_host_resources`, `test_provider_final_contract`, `test_reporting`, `test_role_input`.

### `submit_intent(binding, workspace, output)` (행 656–666)
- 종류: 함수(작업자의 제출 의도 송신).
- 하는 일과 반환값: `binding`이 `None`이면 `AssertionError("The engine must supply its real control transport")`를 던진다. 곧 엔진이 실제 제어 수송을 넘겼는지 검사한다. 그다음 `output`을 `canonical_json`으로 `workspace/output.json`에 쓰고, 제품 `submission.request_control(workspace, "output.json", kind="submit_intent", wait_seconds=0, binding=binding)`로 요청을 보낸다. 이어서 `ControlTransport.wait_receipt(binding, request_id, 60)`로 영수증을 최대 60초 기다린다. 주석(행 663)에 따르면 소유자 루프가 매 회차 수송 요청을 받고, 작업자는 기다리기만 한다. 영수증이 없거나 `state`가 `accepted`가 아니면 `AssertionError("Submission intent did not receive engine acceptance: ...")`를 던진다. 반환값은 없다.
- 부작용: 파일 `output.json`을 쓰고, 실제 제어 수송 요청을 하나 만든다.
- 의존: 제품 `do_math.submission.request_control`, `ControlTransport.wait_receipt`.
- 소비자: `purpose_fixtures`, `runner_fixtures`. 모듈 안에서는 `producer_result`가 부른다.

### `await_control(engine, request, timeout=60)` (행 669–676)
- 종류: 함수(폴링 대기).
- 하는 일과 반환값: 실행 중인 소유자 루프가 큐에 든 공개 제어를 적용할 때까지 기다린다. `request["request_id"]`가 `engine.runtime["processed_controls"]`에 들어올 때까지 0.01초 간격으로 폴링한다. `timeout`초를 넘기면 `AssertionError("The owner loop did not apply control ...")`를 던진다. 반환값은 없다. `시험-지침.md` 4절 규칙 5(고정 대기 대신 조건 폴링과 상한)의 도우미다.
- 부작용: 없다.
- 의존: 없다.
- 소비자: `test_currentness`, `test_submission_boundaries`, `test_submission_tools`.

### `await_stop(should_stop, timeout=60)` (행 679–687)
- 종류: 함수(폴링 대기).
- 하는 일과 반환값: `should_stop()`이 참이 될 때까지 0.01초 간격으로 폴링한다. 참이 되면 `True`를 돌려준다. `timeout`초를 넘기면 예외 없이 `False`를 돌려준다. 이 점이 `await_control`과 다르다. 단언은 호출자가 한다.
- 부작용: 없다.
- 의존: 없다.
- 소비자: `purpose_fixtures`, `test_formal_engine`, `test_machine_parallel`, `test_research_recovery`, `test_submission_tools`.

### `producer_result(result, arguments)` (행 690–697)
- 종류: 함수.
- 하는 일과 반환값: 시나리오가 명시한 응답에 생산자 수송과 봉투 사실만 더한다(docstring 행 691). `result["status"] == "completed"`이고 `output`이 사전일 때만 다음을 한다.
  1. `read_fixture_context(arguments["prompt"], arguments["workspace"])`로 문맥을 읽는다.
  2. `bind_candidates`로 후보를 묶는다.
  3. `seal_response`로 통합 묶음을 선언한다.
  4. `submit_intent(arguments.get("control_binding"), ...)`로 제출 의도를 보낸다.

  반환값은 같은 `result`다. `ScriptedRunner`의 생산자 경로에서 응답 생성만 빼낸 형태이며, 시험이 직접 만든 응답에 쓴다.
- 부작용: `submit_intent`의 부작용(파일, 제어 요청).
- 의존: `read_fixture_context`, `bind_candidates`, `seal_response`, `submit_intent`.
- 소비자: `test_currentness`, `test_input_recovery`, `test_model_assessment_flow`, `test_provider_recovery`, `test_question_flow`, `test_research_recovery`, `test_session_scheduler`.

### `sealed_maintenance_submission(workspace, execution_id)` (행 1076–1096)
- 종류: 함수(실제 중앙 봉인 바이트).
- 하는 일과 반환값: 수명 주기와 저장 시험이 단언할 실제 봉인 바이트를 만든다(docstring 행 1077). 절차는 다음과 같다.
  1. 작업 공간을 만든다.
  2. `maintenance` 역할의 최소 문맥을 만든다. 행동은 `AC-fixture`, 스냅숏은 `fixture-input`이고, 목록들은 비어 있다.
  3. 제품 `contracts.schema_for('maintenance')`로 스키마를 받는다.
  4. `submission.install_tools(workspace, context, schema, None)`로 제출 도구를 설치한다.
  5. 최소 유지 보수 출력을 만들고 `seal_response`로 묶음을 선언한 뒤 `draft.json`에 쓴다.
  6. `submission.seal_submission(... max_artifact_bytes=1024*1024)`로 봉인한다. 통과하지 못하면 `AssertionError(sealed['check']['issues'])`를 던진다.

  반환값은 쌍이다. 첫째는 봉인 의도에 `output_ref='runtime/artifacts/BA-fixture-submission/output.json'`을 더한 사전이고, 둘째는 같은 접두를 붙인 산출물 경로에서 바이트로 가는 사전이다.
- 부작용: 작업 공간에 도구와 초안, 봉인 산출물을 쓴다.
- 의존: `seal_response`, 제품 `contracts.schema_for`, `submission.install_tools`, `submission.seal_submission`.
- 소비자: `test_currentness`, `test_execution_lifecycle`, `test_family_records`, `test_submission_flow`.

## 5. 어댑터와 신뢰 환경

### `FixtureAdapter` (행 703–717)
- 종류: 대역(`LocalCLIAdapter` 탐침 표면의 합성 관찰 대역, docstring 행 704).
- 하는 일: 초기화의 능력 탐침이 부르는 어댑터 표면을 합성 값으로 답한다. 메서드는 아래와 같다.
- `__init__` (행 705–706): 능력 사전 `capabilities`를 사본으로 둔다. 기본값은 `FIXTURE_CAPABILITIES`다.
- `capability_identity` (행 708–709): `IDENTITY`의 깊은 사본을 돌려준다.
- `observation_key` (행 711): `('fixture',)`를 돌려준다.
- `describe` (행 713–717): 탐침 결과를 돌려준다. 필드는 `identity`(`IDENTITY` 사본), `verified=True`, `scope="synthetic_test_evidence_not_host_verification"`, `supported`(능력 사본), `unknown=[]`, `version_sha256="a"*64`, `exec_help_sha256="b"*64`다. `scope` 문자열은 이 증거가 호스트 검증이 아님을 기록한다.
- 부작용: 없다. 실제 CLI를 부르지 않는다.
- 의존: `IDENTITY`, `FIXTURE_CAPABILITIES`.
- 소비자: `engine_fixtures`, `purpose_fixtures`, `state_fixtures`, `test_engine`, `test_initialization_probe_batch`, `test_input_recovery`, `test_lifecycle_engine`, `test_lifecycle_gates`, `test_machine_parallel`, `test_observation_admission`, `test_planning_engine`, `test_role_input`, `test_session_scheduler`, `test_stop_flags`, `test_submission_boundaries`, `test_trust_continuation`. 모듈 안에서는 `install_adapter_fixture`와 `activated_instance`가 쓴다.

### `install_adapter_fixture(test_case)` (행 720–726)
- 종류: 함수(패치 설치).
- 하는 일과 반환값: `do_math.initialization.adapter_for`를 패치해 어떤 프로필에도 새 `FixtureAdapter()`를 돌려주게 한다(`side_effect`). 패치를 시작하고 `test_case.addCleanup`으로 해제를 등록한다. docstring(행 721)에 따르면 외부 관찰만 바꾸고, 증거 해싱과 능력 관문은 그대로 둔다. 반환값은 없다.
- 부작용: 시험이 끝날 때까지 유지되는 `mock.patch` 하나.
- 의존: `FixtureAdapter`.
- 소비자: `purpose_fixtures`, `test_controls`, `test_engine`, `test_initial_intent_connection`, `test_lifecycle_engine`, `test_provider_recovery`, `test_session_scheduler`.

### `fixture_setup_lean(toolchain, smoke, *, validation=True)` (행 730–742)
- 종류: 함수(`@contextmanager` 패치 문맥).
- 하는 일과 반환값: 호스트 관찰을 합성 도구 사슬로 바꾼 상태로 `setup_lean`을 쓰게 한다. `validation_fixture(toolchain, smoke)`로 검증 결과를 만든다. `validation=False`이면 그 결과를 `status='failed'`, `exit_code=1`로 바꾼다. 블록 동안 세 곳을 패치한다.
  - `setup_lean.observe_identity`: `deepcopy(toolchain)`을 돌려준다.
  - `setup_lean.verify_environment`: 위 결과를 돌려준다.
  - `do_math.file_io.RACY_NS`: `0`으로 둔다.

  docstring(행 733–734)에 따르면 합성 파일은 방금 만들어진 것이라 경합 창(racy window)을 닫아야 한다. 닫지 않으면 기록이 지문이 가라앉기를 기다린다. `yield`하는 값은 없다.
- 부작용: 블록 동안 세 패치.
- 의존: `validation_fixture`, 스크립트 모듈 `setup_lean`.
- 소비자: `test_environment_validation`, `test_lifecycle_engine`, `test_machine_parallel`, `test_submission_flow`.

### `validation_fixture(toolchain, source)` (행 745–753)
- 종류: 대역(명시적 컴파일러 대역).
- 하는 일과 반환값: docstring(행 746)은 이 기록을 네이티브 검증으로 내세우지 말라고 한다. 제품 `trust_inventory.validation_program(toolchain)`에서 검증 프로그램 본문과 범위를 받아, 검증 성공 기록을 돌려준다. 필드는 다음과 같다.
  - `status='verified'`, `scope`
  - `source`: `source`의 절대 경로
  - `source_text`, `source_sha256`
  - `command`: 설정 명령에 원천 경로를 붙인 것
  - `exit_code=0`, `stdout='synthetic external compiler result'`, `stderr=''`
  - 고정 시각 `2026-09-20T00:00:00Z`–`00:00:01Z`

  원천 파일은 쓰지 않고 경로만 해석한다.
- 부작용: 없다.
- 의존: 제품 `do_math.trust_inventory.validation_program`.
- 소비자: `knowledge_fixtures`(`formal_boundary_engine`), `test_environment_validation`. 모듈 안에서는 `fixture_setup_lean`과 `trust_fixture`가 부른다.

### `trust_fixture(root, command)` (행 759–786)
- 종류: 함수(합성 설치, 공유 도구 사슬 기록, 등록 요청).
- 하는 일과 반환값: 호출마다 `root` 아래에 `tempfile.mkdtemp(prefix='synthetic-trust-')`로 새 디렉터리를 만든다. 곧 호출마다 자기 디렉터리와 기록을 가진다(docstring 행 763). 그 안에서 다음을 한다.
  1. `toolchain/` 아래에 `SYNTHETIC_TOOLCHAIN_FILES` 네 파일을 쓴다. 각 내용은 `"CORE_TESTS synthetic <상대경로> for <명령>"`이다.
  2. 도구 사슬 사전을 만든다. 필드는 다음과 같다.
     - `executable`: `lean.exe` 경로, `sha256`: 그 해시
     - `version`: `"Lean test 4.32.0"`, `version_exit=0`
     - `configured_command`: `command`
     - `verifier_sha256`, `verifier_path`: 실제 제품 `formal.py`
     - `executables`: `lean.exe`와 `lake.exe`의 해시
     - `project=None`

     검사기 식별을 실제 `formal.py`로 두는 것은 게시 관문이 일관된 식별을 다시 계산하게 하려는 것이다(docstring 행 762–763).
  3. 제품 `trust_inventory`의 `observe_fingerprint`, `content_hashes`, `new_baseline`(`validation_fixture` 결과를 포함), `new_record`로 기록을 만들고, `write_record`로 `records/<기록ID>.json`에 쓴다.

  반환값은 등록 요청 사전이다. 필드는 `operation="register"`, `toolchain`, `allowed_axioms=sorted(AXIOMS)`, `toolchain_record`(경로와 ID), `binding`(`trust_inventory.binding(record)`)이다.
- 부작용: 합성 도구 사슬 파일 네 개와 기록 파일 하나를 디스크에 쓴다. 기록은 이 파일들의 stat 지문을 담는다. 그래서 템플릿 빌드에서는 이 함수의 `root`로 `shared`를 준다(`restore_template` 절 참조).
- 의존: `SYNTHETIC_TOOLCHAIN_FILES`, `validation_fixture`, 제품 `formal`, `trust_inventory`, `file_io.sha256_file`, `trust_validation.AXIOMS`.
- 소비자: `engine_fixtures`, `knowledge_fixtures`, `review_fixtures`, `test_control_shapes`, `test_environment_validation`, `test_family_records`, `test_formal`, `test_formal_engine`, `test_governance_engine`, `test_knowledge`, `test_lifecycle_engine`, `test_purpose_engine`, `test_review_engine`, `test_trust_continuation`. 모듈 안에서는 `activate`가 부른다.

### `trust_environment(request, *, environment_id='TE-fixture', status='active', source_ref='fixture:trust')` (행 789–798)
- 종류: 함수.
- 하는 일과 반환값: 등록 요청 `request`를 등록했을 때 생기는 인스턴스 기록과 런타임 결속을 쌍으로 돌려준다. 기록은 `{id, status, toolchain, allowed_axioms, source_ref, toolchain_record}`이고, 결속은 `request['binding']`의 깊은 사본이다. docstring(행 792–793)에 따르면 기록은 `instance['trust_environments']`에, 결속은 `runtime['trust_bindings']`에 같은 ID로 넣는다.
- 부작용: 없다.
- 의존: 없다.
- 소비자: `engine_fixtures`, `knowledge_fixtures`, `review_fixtures`, `test_control_shapes`, `test_environment_validation`, `test_formal`, `test_formal_engine`, `test_governance_engine`, `test_knowledge`, `test_review_engine`, `test_trust_continuation`.

## 6. 거버넌스와 공개 제어

### `send_control(engine, action, **kwargs)` (행 801–809)
- 종류: 함수(공개 제어 한 건).
- 하는 일과 반환값: 다음 순서로 공개 제어 한 건을 적용한다.
  1. 제품 공개 함수 `do_math.engine.control(engine.store.repository, engine.instance["id"], action, **kwargs)`로 제어 요청을 저장소의 제어 수신함에 넣는다.
  2. `engine.process_controls()`로 적용한다.
  3. 런타임 `history`에서 `kind == "rejected_user_control"`이고 요청 ID가 같은 항목을 찾는다. 있으면 `AssertionError("Public fixture control was rejected: ...")`를 던진다.

  반환값은 제어 요청 사전이다.
- 부작용: 실제 저장소에 제어 요청을 쓰고, 엔진이 새 상태를 게시한다.
- 의존: 제품 `engine.control`, `ResearchEngine.process_controls`. 엔진이 실제 저장소(`store.repository`)를 가져야 한다.
- 소비자: `purpose_fixtures`, `test_academic_engine`, `test_currentness`, `test_engine`, `test_family_records`, `test_formal_engine`, `test_lifecycle_engine`, `test_provider_recovery`, `test_purpose_engine`, `test_research_recovery`, `test_review_research`, `test_session_scheduler`. 모듈 안에서는 `activate`가 부른다.

### `charter_change(engine, **content_changes)` (행 812–818)
- 종류: 함수.
- 하는 일과 반환값: 엔진의 실제 현재 헌장(`engine._governance()["charter"]`)에 대한 변경 제안을 만든다. 새 기록의 ID는 `new_id("CH")`, 개정 번호는 현재 개정 + 1, `supersedes=[현재 ID]`다. 내용은 현재 내용의 깊은 사본에 `content_changes`를 덮은 것이다. 반환값은 `{"kind": "charter", "record": ...}`다. docstring(행 813)에 따르면 승인은 공개 경로에 남는다. 이 함수는 제안만 만든다.
- 부작용: 없다.
- 의존: 제품 `repository.new_id`, 엔진의 `_governance`.
- 소비자: `purpose_fixtures`, `test_academic_engine`, `test_engine`, `test_purpose_engine`, `test_research_recovery`, `test_stop_flags`.

### `policy_change(engine, text)` (행 821–826)
- 종류: 함수.
- 하는 일과 반환값: 정책 기록 제안 `{"kind": "policy", "record": ...}`를 돌려준다. 기록의 필드는 다음과 같다.
  - `id`: `new_id("PO")`, 개정 1, `supersedes=[]`
  - `content.rule_id`: `"fixture-domain"`
  - `text`: 인자 값
  - `scope`: 현재 목표 하나
  - `reason_refs`: 현재 헌장 ID
  - `audit_refs`: 빈 목록
- 부작용: 없다.
- 의존: 제품 `new_id`, 엔진의 `_governance`.
- 소비자: `test_purpose_engine`, `test_stop_flags`.

### `charter(identifier="CH1", goal="Prove P", **content)` (행 829–836)
- 종류: 함수(헌장 기록).
- 하는 일과 반환값: 개정 1의 헌장 기록을 돌려준다. `content`의 필드는 다음과 같다.
  - `rationale`: "Research P"
  - `goal`
  - `desired_result`: "A proof"
  - `success_criteria`: `["P proved"]`
  - `partial_success_criteria`
  - `included_scope`: `["P"]`
  - `excluded_scope`, `preferences`, `academic_requirements`, `stop_conditions`: 빈 목록
  - `priorities`
  - `evidence_boundary`
  - `decision_authority`: `"user"`

  `content` 인자는 이 필드를 덮는다. docstring(행 830)에 따르면 이 함수는 승인을 주지 않는다.
- 부작용: 없다.
- 의존: 없다.
- 소비자: `engine_fixtures`, `record_fixtures`, `test_academic`, `test_family_records`, `test_governance`, `test_governance_engine`, `test_review_engine`, `test_task_contracts`. 모듈 안에서는 `charter_record`가 부른다.

### `charter_record(goal)` (행 839–844)
- 종류: 함수.
- 하는 일과 반환값: `charter("CH-fixture", goal, ...)`로 합성 시나리오용 헌장을 만든다. 성공 기준은 `[goal]`, 포함 범위는 `[goal]`, 부분 성공 기준은 "Record an explicit unresolved obligation"이다. 증거 경계는 "Synthetic model and compiler inputs in a temporary repository"다. 승인은 주지 않는다.
- 부작용: 없다.
- 의존: `charter`.
- 소비자: `test_decision_basis`, `test_initial_intent_connection`. 모듈 안에서는 `activate`가 부른다.

### `approved_governance(instance, records, *, source=("S", "User approves P"), approval_id="D")` (행 847–860)
- 종류: 함수.
- 하는 일과 반환값: `records`를 명시적 합성 사용자 승인 하나로 채택한 인스턴스를 돌려준다. 절차는 다음과 같다.
  1. 제품 `governance.preserve_source(*source, origin="user")`로 사용자 원문을 보존한다.
  2. 승인 `{id: approval_id, actor: "user", source_ref, source_sha256, record_hashes}`를 만든다. `record_hashes`는 기록마다 `exact_content_hash`를 넣은 사전이다. docstring(행 851–852)에 따르면 이 모양은 제품 `governance.initialize_governance`가 요구하는 것이다.
  3. `governance.initialize_governance(governance_start(instance), preserved, approval, records)`의 결과를 돌려준다.
- 부작용: 없다(순수 함수 조합).
- 의존: `governance_start`, 제품 `governance.preserve_source`·`initialize_governance`, `repository.exact_content_hash`.
- 시작 상태의 단: 1단.
- 소비자: `engine_fixtures`, `record_fixtures`, `test_academic`, `test_decision_basis`, `test_family_records`.

## 7. 공개 활성화, 프로세스 대체물, 템플릿

### `activate(engine, root, *, initialization_runner, external_policy="disabled", review_policy=None)` (행 863–918)
- 종류: 함수(공개 활성화 구동).
- 하는 일과 반환값: 공개 제어와 실제 해석 실행 두 번으로 활성화를 채운다. docstring(행 864–867)에 따르면 픽스처는 합성 승인, 신뢰, 능력 관찰만 공급하고, 수명 주기 변경과 활성화 관문은 엔진이 적용한다. 순서는 다음과 같다.
  1. **관찰 창 설정.** `tool_review_window_seconds=60`, `self_check_response_window_seconds=5` 가운데 설정에 없는 키가 있으면 `send_control(engine, "configure", ...)`로 먼저 넣는다. 주석(행 870–871)에 따르면 제품에는 의도적으로 암묵 기본값이 없어서, 프로필을 채택하기 전에 픽스처가 명시적으로 승인한다.
  2. **사전 계산.** 만료 시각을 지금부터 하루 뒤로 잡는다. 설정 해시 `config_sha256`을 구한다. 제품 `model_policy.selection`으로 `intent_interpretation` 역할의 초기 프로필 참조를 구하고, 원본 입력 본문으로 `charter_record`를 만든다.
  3. **다섯 제어를 한꺼번에 넣고 적용.** 제어 다섯 개를 제품 `control`로 큐에 넣는다. 본문은 모두 "Synthetic CORE_TESTS input; not actual host verification or user approval"이다.
     1. 헌장 채택 결정(`initialization`/`governance`)
     2. 해석용 권한 `GR-initial-fixture`(역할 `intent_interpretation`)
     3. 연구용 권한 `GR-research-fixture`(역할 `ROLES`에 `formal_check`를 더한 것)
     4. 탐침 결정(`initialization`/`probe`, 설정 해시)
     5. `trust` 제어(`trust_fixture(root, config["lean_command"])`)

     두 권한은 모두 `local`, `reusable`이고 위 만료 시각을 쓴다. 넣은 뒤 `process_controls()`를 한 번 부른다. 거부된 제어가 하나라도 있으면 `AssertionError("Initialization controls rejected: ...")`를 던진다.
  4. **신뢰 전환.** 첫 신뢰 환경으로 `trust`/`transition`을 `send_control`한다.
  5. **채택 결정.** 초기화 채택 결정을 `send_control`한다. 필드는 다음과 같다.
     - `config_sha256`
     - `adopt_current_governance=True`
     - `conversation_loss_policy="continue_authorized"`
     - `external_policy`
     - 검토 정책: `review_policy`가 없으면 `adopt_default_review_policy=True`
     - `initial_profile_ref`
     - `initial_grant_ids`, `research_grant_ids`
  6. **해석 실행.** 엔진의 러너를 `initialization_runner`로 바꾸고 `engine.run(until_active=True)`를 돈다. 이때 실제 해석 실행 두 번(해석과 확인)이 이 러너로 돈다. 끝나고 `lifecycle.state`가 `active`가 아니면 `AssertionError("Public initialization did not reach active: ...")`를 던진다. 메시지에는 `activation`, `status`, 최근 `history` 세 개가 담긴다. `finally`에서 원래 러너를 되돌린다.

  반환값은 같은 `engine`이다.
- 부작용: `root` 아래에 `trust_fixture`의 합성 도구 사슬을 만든다. 저장소에 제어 요청과 게시 상태가 쌓인다. 러너가 해석 실행을 돈다(`ScriptedRunner`이면 실제 Windows Job 자식 프로세스).
- 의존: `send_control`, `charter_record`, `trust_fixture`, 제품 `engine.control`, `repository.exact_content_hash`, `model_policy.selection`, `contracts.ROLES`, `ResearchEngine.process_controls`·`run`.
- 시작 상태의 단: 4단(공개 경로). 3단 빌드 `activated_instance`의 본체다.
- 소비자: `test_engine`, `test_lifecycle_engine`. 모듈 안에서는 `activated_instance`가 부른다.

### `_no_formal_check(**arguments)` (행 921–922)
- 종류: 대역(금지된 형식 검사기).
- 하는 일과 반환값: 불리면 언제나 `AssertionError('Public activation ran a formal check; a template build supplies no verifier')`를 던진다. 템플릿 빌드 동안 활성화가 형식 검사를 부르지 않음을 고정한다.
- 부작용: 없다.
- 의존: 없다.
- 소비자: 모듈 안에서만 사용한다. `activated_instance`가 엔진의 `formal_verifier`로 준다.

### `activated_instance(root, shared, *, goal, config, external_policy='disabled', review_policy=None)` (행 925–939)
- 종류: 템플릿 빌드(`restore_template`에 넘긴다).
- 하는 일과 반환값: 공개 `initialize`와 `activate`를 돈다. 절차는 다음과 같다.
  1. `git_init(root / 'repository')`로 저장소를 만든다.
  2. `do_math.initialization.adapter_for`를 `FixtureAdapter`를 돌려주는 패치로 덮는다. 이 패치 안에서 3–5를 한다.
  3. 제품 `initialize(repository, goal=goal, workspace=root / 'work-0', config=config)`를 부른다.
  4. `ResearchEngine(repository, instance_id, runner=ScriptedRunner(), formal_verifier=_no_formal_check)`로 엔진을 만든다.
  5. `activate(engine, shared, initialization_runner=ScriptedRunner(), ...)`를 부른다. 신뢰 도구 사슬의 위치로 `shared`를 넘긴다.

  반환값은 인스턴스 ID다. docstring(행 927–929)에 따르면 도구 사슬을 `shared`에 두는 까닭은 복원된 사본이 그 지문을 유지하게 하려는 것이다. 이 빌드의 `external_policy` 기본값은 `'disabled'`이고, `state_fixtures.active_instance`의 기본값은 `'explicit_grants'`다.
- 부작용: `root/repository`에 Git 저장소와 활성 상태까지의 게시 이력이 생긴다. `root/work-0`에는 작업 공간, 실행 산출물 `runs/`, 제어 수신함이 생긴다. `shared` 아래에는 합성 도구 사슬과 그 기록이 생긴다. `ScriptedRunner.run`은 `local_job_runner`로 감싸여 있으므로 해석 실행 두 번이 각각 실제 Windows Job 자식 프로세스를 띄운다.
- 의존: `git_init`, `FixtureAdapter`, `activate`, `_no_formal_check`, `runner_fixtures.ScriptedRunner`(늦은 import), 제품 `initialize`, `ResearchEngine`.
- 시작 상태의 단: 3단 템플릿이다. 모듈 docstring(행 60–62)에 따르면 이 빌드는 첫 연구 단계 전의 게시 상태를 만든다.
- 소비자: `purpose_fixtures`, `test_session_scheduler`.

### `git_init(path)` (행 945–960)
- 종류: 함수(자식 프로세스 대체물).
- 하는 일과 반환값: `path`를 새 빈 Git 저장소로 만든다. 결과는 `git init -q <path>`와 같다(docstring 행 946). 구현 수준의 동작은 다음과 같다.
  1. **프로세스당 한 번의 실제 `git init`.** 모듈 전역 목록 `_EMPTY_GIT_DIR`가 비어 있으면 `tempfile.mkdtemp(prefix='do-math-empty-git-')`로 모형 디렉터리를 만든다. 그 디렉터리를 `atexit.register(shutil.rmtree, model, True)`로 종료 시 지우도록 등록하고, 실제 자식 프로세스 `subprocess.run(['git', 'init', '-q', model], check=True)`를 한 번 돈다. 그 뒤 `model/.git` 경로를 목록에 넣는다. `git`이 0이 아닌 코드로 끝나면 `CalledProcessError`가, 실행 파일이 없으면 `FileNotFoundError`가 호출한 시험으로 전파된다. 어느 경우든 목록은 비어 있으므로, 다음 호출이 다시 시도한다.
  2. **호출마다 복사.** `path.mkdir(parents=True, exist_ok=True)`로 대상 디렉터리를 만들고 `shutil.copytree(_EMPTY_GIT_DIR[0], path / '.git')`로 모형의 `.git`을 복사한다. docstring(행 948–949)에 따르면 이 `.git`은 자기 경로를 담지 않으므로 다른 위치에 복사해도 유효하다. 대상에 `.git`이 이미 있으면 `copytree`가 `FileExistsError`를 던진다. 반면 `git init`은 기존 저장소를 다시 초기화한다. 이것이 원문에서 읽히는 원본과의 차이 하나다.

  반환값은 `Path(path)`다.
- 부작용: 첫 호출에서 실제 `git` 자식 프로세스 하나와 임시 모형 디렉터리를 만든다. 호출마다 `path/.git`을 복사한다.
- 의존: `_EMPTY_GIT_DIR`, 외부 `git` 실행 파일(첫 호출만).
- 소비자: `engine_fixtures`, `review_fixtures`, `state_fixtures`, `test_cli`, `test_cli_surface`, `test_design_walkthroughs`, `test_engine`, `test_execution_lifecycle`, `test_family_records`, `test_formal_input_manifest`, `test_git_store`, `test_host_resources`, `test_impact_review`, `test_initial_intent_connection`, `test_integration_bundles`, `test_knowledge`, `test_machine_parallel`, `test_observations`, `test_operator`, `test_payloads`, `test_preflight`, `test_provider_recovery`, `test_provider_wait`, `test_reporting`, `test_repository`, `test_retention`, `test_review_engine`, `test_role_input`, `test_session_scheduler`, `test_state_contract`, `test_submission_checks`, `test_submission_flow`, `test_submission_tools`, `test_supervisor_recovery`, `test_task_contracts`, `test_unicode_flow`. 모듈 안에서는 `new_instance`와 `activated_instance`가 부른다.

### `run_cli(*arguments, cwd=None)` (행 963–991)
- 종류: 함수(자식 프로세스 대체물).
- 하는 일과 반환값: CLI의 `main`을 이 프로세스 안에서 돌린다. 결과는 `python do_math.py *arguments`와 같은 모양이다(docstring 행 964). 구현 수준의 동작은 다음과 같다.
  1. 인자를 모두 `os.fspath`로 문자열화한다. 그래서 `Path`를 넘겨도 된다.
  2. 표준 출력과 표준 오류를 받을 `io.StringIO` 두 개를 만든다.
  3. 현재 작업 디렉터리를 기억하고, `cwd`가 주어지면 `os.chdir(cwd)`한다.
  4. `redirect_stdout`·`redirect_stderr` 안에서 제품 `do_math.cli.main(arguments)`를 부른다. 반환값이 종료 코드다.
  5. `main`이 `SystemExit`를 던지면 인터프리터처럼 해석한다(주석 행 985). 코드가 `None`이면 0, 정수면 그 값이다. 다른 값이면 그 값을 표준 오류에 출력하고 1이다.
  6. `finally`에서 작업 디렉터리를 되돌린다.

  반환값은 `subprocess.CompletedProcess(['do_math.py', *arguments], 코드, stdout 문자열, stderr 문자열)`이다.

  docstring(행 968–969)은 대체의 한계를 밝힌다. 프로세스에 관한 것은 하나도 검사되지 않는다. 스트림 인코딩, 인터프리터 시동, 프로세스 전역 상태는 시험 프로세스의 것이 그대로 남는다. `SystemExit`가 아닌 예외는 잡지 않으므로 호출한 시험으로 그대로 전파된다. 자식 프로세스였다면 종료 코드 1과 트레이스백 출력이 되었을 것이다. `os.chdir`는 프로세스 전역이므로 호출 동안 다른 스레드의 상대 경로 해석에도 영향을 준다.
- 부작용: 호출 동안 작업 디렉터리 변경과 표준 스트림 재지정. CLI가 하는 저장소 쓰기.
- 의존: 제품 `do_math.cli.main`.
- 소비자: `test_cli`, `test_cli_advanced`, `test_controls`, `test_input_recovery`. 모듈 안에서는 `cli_result`가 부른다.

### `cli_result(root, *arguments)` (행 994–1002)
- 종류: 함수.
- 하는 일과 반환값: `run_cli(*arguments, cwd=root)`를 돈다. 두 층의 성공을 요구한다.
  - 프로세스 층: `returncode`가 0이 아니면 표준 출력과 오류를 이은 문자열로 `AssertionError`를 던진다.
  - 봉투 층: 표준 출력을 JSON 봉투로 읽고, 봉투의 `exit_code`가 0이 아니면 봉투를 담아 `AssertionError`를 던진다.

  반환값은 봉투의 `result`다.
- 부작용: `run_cli`와 같다.
- 의존: `run_cli`.
- 소비자: `test_controls`, `test_input_recovery`.

### `remove_tree(path)` (행 1005–1010)
- 종류: 함수.
- 하는 일과 반환값: 디렉터리 트리를 지운다. Git이 쓰는 읽기 전용 객체 파일이 있으면 `shutil.rmtree(path, onexc=...)` 콜백이 그 파일을 `os.chmod(target, stat.S_IWRITE)`로 쓰기 가능하게 바꾸고 같은 삭제 함수를 다시 부른다. 반환값은 없다. `onexc` 인자는 Python 3.12부터 있다.
- 부작용: 파일 삭제.
- 의존: 없다.
- 소비자: 모듈 안에서만 사용한다. `_Template.restore`와 `_Template.remove`가 부른다.

### `_Template` (행 1013–1037)
- 종류: 클래스(템플릿 하나의 저장소).
- 하는 일: 빌드한 트리 하나, 손대지 않은 그 사본, 그리고 사본을 복원하는 고정 경로를 담는다(docstring 행 1014).
- `__init__` (행 1016–1024): 다음 순서로 템플릿을 만든다.
  1. `tempfile.mkdtemp(prefix='do-math-template-')`의 절대 경로를 `base`로 잡는다.
  2. 곧바로 `atexit.register(self.remove)`로 프로세스 종료 시 삭제를 등록한다. 등록이 빌드보다 앞서므로, 빌드가 실패해도 `base`는 종료 때 지워진다.
  3. `live`, `pristine`, `shared`를 `base` 아래의 세 경로로 정한다. `live`와 `shared`만 만든다.
  4. `build(live, shared, **parameters)`를 부르고 그 반환값을 `value`에 둔다.
  5. `shutil.copytree(live, pristine, symlinks=True)`로 빌드 직후의 트리를 보존한다.
  6. `used = False`로 둔다.
- `restore` (행 1026–1031): `used`가 참이면 `remove_tree(live)`로 앞 사본을 지우고 `copytree(pristine, live, symlinks=True)`로 새 사본을 만든다. 거짓이면 빌드가 남긴 `live`를 그대로 준다. 이때 `live`의 바이트는 방금 떠 둔 `pristine`과 같다. 어느 경우든 `used = True`로 두고 `(live, deepcopy(value))`를 돌려준다.
- `remove` (행 1033–1037): `remove_tree(base)`를 부르되 `OSError`는 삼킨다. 종료 시 정리가 실패해도 프로세스 종료를 막지 않는다.
- 부작용: 임시 디렉터리 셋(`live`, `pristine`, `shared`)과 `atexit` 등록 하나.
- 의존: `remove_tree`.
- 소비자: 모듈 안에서만 사용한다. `restore_template`가 만든다.

### `restore_template(build, **parameters)` (행 1043–1073)
- 종류: 함수(공유 시작 상태의 입구).
- 하는 일과 반환값: `(root, value)`를 돌려준다. 이 모듈에서 가장 중요한 함수이므로 복원 규칙을 구현 수준에서 적는다.
  1. **열쇠 계산(행 1060–1065).** 먼저 `inspect.signature(build).bind(None, None, **parameters)`로 매개변수를 빌드 서명에 묶는다. 앞의 두 `None`은 `root`와 `shared` 자리다. 이어서 `apply_defaults()`로 기본값을 채우고, 앞의 두 인자를 뺀 나머지를 매개변수 사전으로 삼는다. 주석(행 1061)에 따르면 기본값을 열쇠에 넣는 까닭은 기본값을 생략한 호출과 명시한 호출이 같은 템플릿을 가리키게 하려는 것이다. 열쇠는 `(build.__module__, build.__qualname__, json.dumps(parameters, sort_keys=True))`다. 서명에 맞지 않는 매개변수는 `bind`에서 `TypeError`를 낸다. JSON이 아닌 값은 `json.dumps`에서 `TypeError`를 낸다. 둘 다 등록 전에 나므로 템플릿 표에 흔적을 남기지 않는다. docstring(행 1057–1058)은 매개변수가 JSON 값이어야 하고, `build`의 이름과 함께 템플릿을 고른다고 적는다.
  2. **프로세스당 한 번의 빌드(행 1066–1070).** 모듈 전역 사전 `_TEMPLATES`에서 열쇠를 찾는다. 없으면 먼저 `_TEMPLATES[key] = 'failed'`를 적고, 그다음 `_Template(build, parameters)`를 만들어 같은 열쇠에 덮어쓴다. `_Template.__init__`이 빌드를 부르므로, 빌드는 그 템플릿을 처음 요청한 시험 안에서 돈다. 표가 프로세스 메모리에만 있으므로, 템플릿은 한 프로세스 안에서만 살고 디스크에서 다시 쓰이지 않는다(모듈 docstring 행 111–114). docstring은 그 까닭으로 템플릿이 설치 판, 빌드 하루 뒤의 권한 만료, 시계 최고 수위를 싣는다는 점을 든다.
  3. **실패한 빌드의 전파(행 1068–1072).** 빌드가 예외를 던지면 `_Template` 생성이 끝나지 않아 표에는 `'failed'`가 남는다. 그 예외는 처음 요청한 시험으로 그대로 전파된다. 같은 열쇠를 다시 요청하면 빌드를 재시도하지 않는다. 대신 `AssertionError('This template failed to build earlier in this process: ' + repr(key))`를 던진다. 주석(행 1068)에 따르면 재시도하면 뒤의 모든 시험이 그 비용을 되풀이하기 때문이다. 결과적으로 한 프로세스에서 한 빌드의 실패는 원인 예외 한 번과 그 뒤 요청마다의 `AssertionError`로 나타난다(모듈 docstring 행 115–116).
  4. **복원(행 1073).** 템플릿의 `restore()`를 부른다. 첫 호출은 빌드가 남긴 `live`를 그대로 받고, 이후 호출은 `pristine`에서 새로 복사한 `live`를 받는다. `value`는 빌드 반환값의 깊은 사본이다.

  복원 규칙과 그 근거는 다음과 같다.
  - **같은 절대 경로.** 한 템플릿의 모든 사본은 같은 경로 `base/live`에 놓인다. 빌드도 바로 그 경로를 `root`로 받아 돌았다. 그래서 상태에 기록된 절대 경로(저장소 `root/repository`, 작업 공간 `root/work-0`)와 그 경로를 포함한 해시가 사본에서도 참이다(docstring 행 1052–1053, 모듈 docstring 행 99–100). 대가도 있다. 호출이 앞 사본을 지우고 새 사본으로 바꾸므로, 시험은 다음 사본을 요청하기 전에 앞 엔진을 끝내야 한다. 시험이 사본 저장소에 인스턴스를 더하는 것은 허용된다(모듈 docstring 행 101–102). 앞 사본의 파일을 잡은 핸들이 남아 있으면 `remove_tree`가 실패할 수 있다. `onexc` 콜백은 권한만 바꿔 다시 시도하므로, 그래도 지워지지 않으면 오류가 전파된다.
  - **정확한 바이트.** `copytree`는 빌드가 남긴 파일을 모두 복사한다. Git 객체와 참조, `runs/` 산출물, 제어 수신함이 여기에 든다. 기호 링크는 링크로 복사한다(`symlinks=True`). 그래서 사본은 제품이 게시한 그대로의 상태다.
  - **`shared` 폴더.** `shared`는 `base/shared`에 한 번 만들어지고, 복사되거나 비워지지 않는다. 템플릿이 사는 동안 그대로 남고, 종료 시 `base`와 함께 지워진다. docstring(행 1055–1058, 모듈 docstring 행 120–124)에 따르면 이 폴더에는 제품이 읽기만 하고 쓰지 않으면서 상태가 그 stat 지문을 기록하는 파일만 둔다. 두 조건을 모두 갖춘 파일이어야 한다. `trust_fixture`의 도구 사슬과 기록이 그 예다. 이런 파일을 `live`에 두면 복사할 때마다 생성 시각이 바뀌어 지문이 어긋난다. 빌드 뒤에는 `shared`를 읽기만 해야 한다.
  - **프로세스 지역 상태 제외.** 사본은 디스크 바이트만 담는다. 엔진 객체의 프로세스 지역 상태는 담지 않는다. 예를 들어 `run` 전의 `_task_readiness`나 `lifecycle_clock` 패치는 새 엔진에 다시 설정해야 한다(모듈 docstring 행 107–110).
  - **설정은 매개변수로.** 설정을 뒤늦게 `configure` 제어로 바꾸지 말고 매개변수로 넘겨야 한다. 뒤늦은 제어는 새 능력 증거가 필요한 새 프로필 판을 만들기 때문이다(모듈 docstring 행 103–106).
- 부작용: 첫 호출에서 빌드 실행과 임시 디렉터리 생성. 이후 호출마다 `live` 삭제와 재복사.
- 의존: `_TEMPLATES`, `_Template`, `remove_tree`(간접).
- 시작 상태의 단: 2단과 3단의 공통 기계다. 2단은 `state_fixtures.active_instance`와 그 위에 쌓은 빌드를 넘긴다. `purpose_fixtures.purpose_state`·`assessment_preparation_instance`와 시험 모듈 전용 빌드 대부분이 여기에 든다. 3단은 `activated_instance`와 그 위에 쌓은 빌드를 넘긴다. `purpose_fixtures.solved_instance`와 `test_session_scheduler.ready_work`(`public=True`)가 여기에 든다. `engine_fixtures.initialized_instance`, `test_cli.cli_instance`, `test_cli_advanced.created_instance`처럼 공개 초기화만 도는 빌드도 이 기계를 쓴다.
- 소비자: `purpose_fixtures`, `state_fixtures`, `test_academic_engine`, `test_cli`, `test_cli_advanced`, `test_controls`, `test_currentness`, `test_engine`, `test_input_recovery`, `test_lifecycle_engine`, `test_model_assessment_flow`, `test_provider_recovery`, `test_purpose_engine`, `test_research_recovery`, `test_session_scheduler`, `test_stop_flags`, `test_submission_boundaries`.

## 8. 식별 검토

### `scope_assessment(policy, slots)` (행 1099–1105)
- 종류: 함수.
- 하는 일과 반환값: 픽스처 검토자가 작성한 전체 제안 범위 평가를 돌려준다(docstring 행 1100). 필드는 다음과 같다.
  - `assessment_id`: `"fixture-full-proposal-scope"`
  - `policy_id`, `required_perspectives`: 정책의 값. 목록은 복사하지 않고 같은 객체를 쓴다.
  - `initial_slots`: `slots`의 각 이름을 ID와 관점으로 삼고, `required_source_refs=["proposal"]`을 붙인다.
  - `selected_profile_ref=None`
  - `activity_execution_limit`, `overflow_disposition`: 정책의 값

  `scope_response`와 달리 역할 문맥 없이 정책과 칸 이름만으로 만든다.
- 부작용: 없다.
- 의존: 없다.
- 소비자: `review_fixtures`, `test_review_engine`.

### `start_scoped_review(engine, knowledge_id, assessment, previous_cycle_id=None)` (행 1108–1129)
- 종류: 함수.
- 하는 일과 반환값: 범위 단계가 이미 `assessment`로 정해진 검토 주기를 연다. docstring(행 1111–1114)에 따르면 엔진은 모든 검토를 범위 단계에서 연다. 그래서 뒤 단계를 검사하는 시험은 범위 실행을 돌리지 않는다. 대신 연 주기에 순수 `start_review(..., scope_assessment=...)` 경로가 주는 범위를 준다. 봉인 재생이 하는 방식과 같다. 절차는 다음과 같다.
  1. 엔진의 `_start_identity_review(knowledge_id, previous_cycle_id)`로 주기를 연다.
  2. 제품 `review_cycle.start_review`에 주기의 제안, 요청 검토자 칸, 판정자 칸, 최대 회차, 앞 주기, 정책, `scope_assessment`를 넘긴다.
  3. 결과의 `scope_assessment`, `reviewer_slots`, `activity_execution_limit`, `required_source_refs`, `phase`를 주기에 옮긴다.
  4. `capture_review_input_basis(cycle)`로 검토 입력 기반을 다시 잡는다.
  5. 런타임 큐에서 이 주기의 행동을 모두 뺀다.
  6. `_queue_identity_actions(knowledge_id, cycle_id)`로 다음 단계 행동을 다시 넣는다.

  반환값은 주기 ID다.
- 부작용: 엔진 런타임(주기, 큐)을 제자리에서 바꾼다. 저장하지는 않는다.
- 의존: 제품 `review_cycle.start_review`, `input_basis.capture_review_input_basis`, 엔진의 `_start_identity_review`·`_queue_identity_actions`.
- 소비자: `review_fixtures`, `test_review_engine`.

## 상수와 모듈 수준 이름

- `IDENTITY` (행 188): `{"host": "CORE_TESTS synthetic host", "implementation": "CORE_TESTS synthetic adapter"}`. 합성 어댑터의 능력 식별이며, `FixtureAdapter.capability_identity`와 `describe`가 사본을 돌려준다. 소비자: `test_lifecycle_engine`.
- `FIXTURE_CAPABILITIES` (행 700): `{"jsonl": True, "model": True, "structured_output": True}`. `FixtureAdapter`의 기본 능력이다. 모듈 안에서만 사용한다.
- `SYNTHETIC_TOOLCHAIN_FILES` (행 756): `('bin/lean.exe', 'bin/lake.exe', 'bin/libleanshared.dll', 'lib/lean/Init/Prelude.olean')`. `trust_fixture`가 도구 사슬 디렉터리에 만드는 파일 목록이다. 모듈 안에서만 사용한다.
- `_EMPTY_GIT_DIR` (행 942): 빈 목록으로 시작하는 프로세스 캐시다. `git_init`의 첫 호출이 모형 저장소의 `.git` 경로 하나를 넣는다. 모듈 안에서만 사용한다.
- `_TEMPLATES` (행 1040): 빈 사전으로 시작하는 템플릿 표다. 열쇠는 `(모듈, 한정 이름, 정렬된 매개변수 JSON)`이고, 값은 `_Template` 또는 문자열 `'failed'`다. `restore_template`만 읽고 쓴다.

## 관계

**다른 픽스처 모듈과의 의존.** 이 모듈은 픽스처 체계의 뿌리다. `consumers.json`에 따르면 나머지 픽스처 모듈 여덟이 모두 이 모듈을 import한다.
- `state_fixtures`: `git_init`, `FixtureAdapter`, `restore_template`, `assessment`
- `engine_fixtures`: `bare_engine`, `StateStore`, `trust_fixture`, `intent_response`, `charter` 등
- `runner_fixtures`: 역할 응답 조각 열두 개
- `record_fixtures`: `approved_governance`, `charter`, `current_state`, `review_items`, `supply_observation_rules`
- `knowledge_fixtures`: `bare_engine`, `trust_environment`, `trust_fixture`, `validation_fixture`, `dispatched_launch`
- `review_fixtures`, `purpose_fixtures`, `provider_fixtures`

반대 방향의 의존은 하나뿐이다. `activated_instance`가 `runner_fixtures.ScriptedRunner`를 함수 안에서 늦게 import한다. 이 모듈은 다른 픽스처 모듈을 모듈 머리에서 import하지 않는다.

**시작 상태 체계에서 맡는 자리.** `시험-지침.md` 4절 규칙 3의 네 단 가운데 이 모듈이 맡는 몫은 네 가지다.
- 1단이 쓰는 최소 레코드(`current_state`, `governance_start`, `approved_governance`, `charter`)와 메모리 엔진 `bare_engine`
- 2단과 3단이 공유하는 템플릿 기계 `restore_template`
- 3단의 기본 빌드 `activated_instance`
- 4단의 공개 활성화 본체 `activate`

2단 빌드 `state_fixtures.active_instance`는 이 모듈의 `restore_template`, `git_init`, `FixtureAdapter` 위에 선다. 더 깊은 빌드는 모듈 docstring(행 124–126)대로 준비된 빌드를 자기 `root`에서 부른 뒤 스크립트 러너로 엔진을 더 몰고 간다. 바탕 빌드와 러너는 빌드마다 다르다. `purpose_fixtures.solved_instance`는 `activated_instance` 위에서 `AcademicRunner`를 쓴다. `purpose_fixtures.purpose_state`는 2단 `state_fixtures.active_instance` 위에서 `PurposeRunner`를 쓴다. `assessment_preparation_instance`와 시험 모듈 전용 빌드 대부분도 `active_instance` 위에 선다. `git_init`과 `run_cli`는 `시험-지침.md` 4절 규칙 6이 지정한 자식 프로세스 대체물이다. 이 모듈의 코드가 직접 띄우는 실제 자식 프로세스는 세 곳이다.
- `git_init`의 첫 `git init`
- `role_reach`의 `read_input.py`
- `local_job_runner`의 Windows Job 속 `sleep` 프로세스

이와 별개로, 이 모듈이 부르는 제품 저장소 코드는 Git 자식 프로세스를 계속 띄운다. 제품 `GitStateStore._git`이 Git 명령마다(`git_store.py` 행 540) `subprocess.run`을 부르기 때문이다. 그래서 `new_instance`·`activated_instance`의 공개 초기화와 게시, `role_reach`의 스냅숏 읽기, `send_control`의 제어 적용은 모두 Git 자식 프로세스를 쓴다. `git_init`이 없애는 것은 호출마다 띄웠을 `git init` 자식 프로세스뿐이다.

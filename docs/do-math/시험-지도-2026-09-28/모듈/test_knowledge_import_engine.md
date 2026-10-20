# test_knowledge_import_engine

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_knowledge_import_engine.py` (341행) |
| 클래스 / 테스트 | 3 / 15 |
| 시험 대상 제품 코드 | `do_math/engine.py`의 `ResearchEngine`(`process_controls`, `_knowledge_io_control`, `_apply_kind_definition_check`, `_context`, `_save`, `store`), 모듈 함수 `control`, `query_records`; `do_math/knowledge_engine.py`의 `_knowledge_control`; `do_math/formal_engine.py`의 `_formal`; `do_math/review_engine.py`의 `_start_identity_review`; `do_math/formal.py`의 `verify_lean`, `_job_run`(대역·감시 대상); `do_math/trust_validation.py`의 `require_active_environment`, `EnvironmentUnavailable`; `do_math/knowledge.py`의 `assess_use`, `revision_roots`; `do_math/knowledge_records.py`의 `proposal_view`, `usable_links`, `validate_knowledge_records`; `do_math/review_policy.py`의 `build_review_policy`; `do_math/activities.py`, `do_math/execution_lifecycle.py`의 실행 기록 함수 |
| 사용하는 픽스처 모듈 | `knowledge_fixtures`: `formal_boundary_engine`, `impact_declaration`, `knowledge_candidate`, `knowledge_graph`. `research_fixtures`: `bare_engine`, `new_instance`. `state_fixtures`: `owner_calls`. `provider_fixtures`: `actual_command`. `record_fixtures`: `execution_state`(함수 안 import). `test_categories.test_group`(별칭 `category`) |
| 격리 표지 | `PortableFormalBoundaryTests` 클래스에 `@category('lean')` |
| 시작 상태 | `KnowledgeImportTests`: 4단(시험마다 공개 `initialize`를 실제 Git 저장소에서 돈다. 활성화는 하지 않는다). `FormalBoundaryTests`: 메모리 엔진 `bare_engine`에 자동 사양 대역을 입힌 `formal_boundary_engine`이나 `knowledge_graph()` 상태. `PortableFormalBoundaryTests`: 같은 메모리 엔진에 실제 설치 Lean을 연결한다 |

## 목적

모듈 docstring(1–5행)은 두 대상을 밝힌다. 하나는 실제 Git 가져오기, 다른 하나는 명시적 호스트 대역을 둔 중앙 형식 경계다. `PortableFormalBoundaryTests`는 설치된 Lean을 돌리고, 권한·시계·저장·컴파일러 아닌 빌드 증명은 합성이다. 전체 Mathlib 빌드는 주장하지 않는다.

세 클래스가 층을 나눈다.
- `KnowledgeImportTests`는 사용자 제어 `knowledge`(`operation`: `import`, `register-kind`)가 엔진의 제어 처리(`process_controls` → `_knowledge_io_control`, `engine.py` 1410–1433행)를 거친다. 그 결과가 분리 가족 파일로 Git에 저장되고, 조회(`query_records`)와 작업자 카탈로그(`_context`)에 도달하는지 본다.
- `FormalBoundaryTests`는 중앙 형식 검사 소비자 `_formal`(`formal_engine.py` 309행~)의 경계를 본다. 사전 승인 도구 모음 전달, 동일성 검토 시작 실패의 대기 기록, 설치 파일 지문 변경 시 차단이 대상이다. 개정 제어(`_knowledge_control`)와 동일성 검토 시작(`_start_identity_review`)도 여기서 본다.
- `PortableFormalBoundaryTests`는 같은 경계를 실제 Lean 컴파일로 본다. 정확한 원문과 선언 이름의 전달, 컴파일 뒤 식별 변경과 환경 변경의 포착, 버전 관측 재사용, 승인과 다른 실행 파일의 거부가 대상이다.

## 모듈 수준 요소

- 행 6–21: import. 경로 머리가 없으므로 `scripts/`와 `tests/`가 이미 경로에 있어야 한다. 행 20의 `hashlib`은 본문에서 쓰이지 않는다.
- 행 341: 직접 실행하면 `unittest.main(verbosity=2)`.

## KnowledgeImportTests (행 24–117)

`unittest.TestCase`를 상속한다. 클래스 표지와 클래스 속성이 없다.

- `setUp` (행 25–31): 임시 폴더를 만들고 `addCleanup`으로 정리를 건다. `research_fixtures.new_instance(repo, goal='Knowledge integration test fixture', workspace=repo/'work', config={'scholarly_enabled': False})`로 저장소를 만들고 공개 `initialize`를 돈다. 그 인스턴스를 연 `ResearchEngine(repo, instance_id)`를 `self.engine`에 둔다. 시작 상태는 4단이다(공개 초기화만, 활성화 없음). `new_instance`의 `git_init`과 제품의 Git 저장은 실제 Git 자식 프로세스를 쓴다.
- `send(**config)` (행 33–35): `engine.control(repo, instance_id, 'knowledge', config=config)`로 제어를 수신함에 넣고 `self.engine.process_controls()`로 처리한다.

### `test_import_is_persisted_as_families_and_query_has_snapshot_evidence` (행 37–58)
- 성질: 사용자 가져오기는 사용할 수 없는 후보로 분리 가족 파일에 저장되고 형식 검사를 대기열에 넣는다. Lean 원문의 정확한 바이트와 선언 이름이 Git 왕복 뒤에도 그대로다. 조회 결과는 저장 스냅숏과 파일 경로·해시를 증거로 싣는다.
- 준비: 클래스 절의 `setUp`. 후보의 `lean_code`는 `'theorem K : True := True.intro\r\ntheorem K : True := True.intro\n-- é\n'`다. 켈빈 기호(U+212A)와 라틴 `K`, CRLF, 결합 부호를 섞었다. `declaration_names`는 `['K', 'K']`다.
- 실행: `send(operation='import', candidate=data)`, `e.store.load()`, `kr.proposal_view(loaded, kid)`, `query_records(repo, instance_id, kind='knowledge')`, `e.store.read_record(kid, head)`.
- 단언: 가져온 기록이 사용 불가이고 `formal`과 `reviews` 키가 없다. 대기열에 이 기록을 대상으로 한 `formal_check`가 있다. 다시 읽은 `formal_results`와 `expositions`가 엔진 상태와 같다. 복원한 `lean_code`의 UTF-8 바이트와 `declaration_names`가 입력과 같다. 조회 행의 `snapshot`이 `head`이고, `path`와 `sha256`이 `read_record`의 값과 같다.
- 대역: 없음.
- 비고: 실제 Git 자식 프로세스.

### `test_duplicate_import_does_not_replace_saved_record` (행 60–68)
- 성질: 같은 ID로 두 번째 가져오기를 보내면 저장된 기록은 바뀌지 않고, 제어는 거부 이력으로 남는다.
- 준비: `setUp`. 미리 만든 ID `kid`.
- 실행: `send(operation='import', candidate=knowledge_candidate(id=kid))`, 이어 `summary='Changed'`로 같은 ID를 한 번 더 보낸다.
- 단언: 기록이 첫 가져오기 직후 사본과 같고, 지식 기록 수가 1이다. 런타임 `history`에 `kind == 'rejected_user_control'`인 행이 있다(실패 메시지로 이력 전체를 붙인다).
- 대역: 없음.
- 비고: 도메인의 거부(`import_candidate`의 "record ID already exists")가 엔진에서 예외 대신 거부 이력으로 바뀌는지 본다. 거부 사유 문자열은 단언하지 않는다.

### `test_ended_instance_refuses_knowledge_imports` (행 70–79)
- 성질: 완료되었거나 닫힌 인스턴스는 지식 가져오기 제어를 받지 않고, 상태와 지식 가족을 바꾸지 않는다.
- 준비: `setUp`. 런타임 `status`를 `'completed'`, `'closed'`로 차례로 바꾼다.
- 실행: 제어 처리 경로를 건너뛰고 `e._knowledge_io_control({'action': 'knowledge', 'id': new_id('UC'), 'config': {'operation': 'import', 'candidate': ...}})`를 직접 부른다.
- 단언: `ValueError`를 메시지 `'closed/completed'`로 낸다(`assertRaisesRegex`). 제품 메시지는 `"closed/completed instance cannot apply knowledge controls"`다. `status`가 그대로이고 `knowledge`가 `{}`다.
- 대역: 없음.
- 비고: `subTest(status=...)` 두 개.

### `test_custom_kind_reaches_worker_catalog_only_after_check_and_activation` (행 81–117)
- 성질: 사용자가 제안한 지식 종류는 독립 실행의 검사 판정을 중앙이 소비해 활성화한 뒤에만 작업자 입력의 카탈로그에 나타나고, 그 상태는 저장·재적재 뒤에도 유지된다.
- 준비: `setUp`. 정의 `computational_lemma`(`constraints={}`)를 `send(operation='register-kind', ...)`로 보낸다. 지역 함수 `kinds()`는 `engine._context({'role': 'research_preparation'}, repo/new_id('EX'))`로 매번 새 입력 작업 공간을 만들고 `kind_definitions.knowledge`의 토큰을 돌려준다. 주석은 "Each actual invocation receives a new immutable input workspace."다.
- 실행:
  1. 등록 직후 `kinds()`를 부른다.
  2. 대기열에서 `kind_definition_id`를 가진 행동(등록이 넣은 검사 행동)을 찾는다.
  3. `maintenance` 프로필로 활동을 열고 실행 기록을 만든다. 입력 기준은 `{'kind_definition': {'id', 'sha256'}}`이고 역할은 `maintenance`다. 실행을 `starting`, `running`으로 옮긴다.
  4. 합성 판정 `{'decision': 'approved', 'findings': [], ...}`로 `engine._apply_kind_definition_check(action, verdict, eid)`를 부른다.
  5. 제출 영수증을 붙이고 `stopping`, `ended(output_accepted)`로 옮긴다.
  6. `writer_lock` 아래에서 `_save()`하고 `store.load()`로 다시 읽은 뒤 `kinds()`를 다시 부른다.
- 단언: 등록 직후 토큰이 카탈로그에 없고, 재적재 뒤에는 있다.
- 대역: AI 판정은 합성 사전이다. `mock` 대역은 없다.
- 비고: 원문 주석은 "Only the central consumer of an independent check activates a kind. Use a separate v5 execution and a synthetic AI verdict."다. 제품의 `_apply_kind_definition_check`(`engine.py` 3917행~)는 `governance.validate_independent_execution`으로 검사 실행이 제안자와 다른지 확인한다. 또 정의의 해시와 실행 입력 기준이 일치해야 한다. 실제 Git 자식 프로세스를 쓴다.

## FormalBoundaryTests (행 120–211)

`unittest.TestCase`를 상속한다. 표지, 클래스 속성, 설정·정리 훅, 도우미가 없다. 앞의 세 시험은 `knowledge_fixtures.formal_boundary_engine(Path(d))`에서 시작한다. 이 빌드가 만드는 상태는 다음과 같다.
- `bare_engine()` 메모리 엔진에 `trust_fixture`로 만든 합성 설치를 둔다. 그 위에 `TE-old` 신뢰 환경과 바인딩을 채택하고, 검증하지 않은 후보 하나(`kid`)를 넣는다.
- 설정 `lean_command`는 일부러 승인되지 않은 `['unapproved-config-command']`로 둔다.
- `_save`, `_controls`, `_execution_profile`, `_settle_activity`, `_remove_action`, `_start_identity_review`, `_action_lifecycle_gate`, `_require_action_clock`, `_enqueue`, `_session_slots`, `_activity_for_action`, `_check_conversations`, `_register_execution`, `_machine_started`를 `create_autospec` 대역으로 바꾼다.
- `formal_verifier`는 `formal_evidence`를 돌려주는 `Mock`이다.

세 시험은 모두 `do_math.engine.governance.authorize`를 `{'allowed': True, 'grant_id': 'GR-fixture'}`로 패치하고, `state_fixtures.owner_calls(e)` 블록 안에서 `e._formal({'id': ..., 'role': 'formal_check', 'target': kid})`를 부른다. 블록을 나올 때 시작된 호출을 모두 거둬들인다. 네 단 가운데 어디에도 들지 않는 시작 상태, 곧 메모리 엔진과 자동 사양 대역이다.

### `test_formal_consumer_passes_runtime_and_preapproved_toolchain` (행 121–134)
- 성질: 중앙 형식 소비자는 설정 명령이 아니라 사전 승인된 환경의 도구 모음을 검증기에 넘긴다. 결과를 수리하되 동일성 판정 전까지 지식을 사용 가능으로 올리지 않는다. 동일성 검토를 시작하고 실행을 정상 종료한다.
- 준비: 클래스 절의 `formal_boundary_engine`.
- 실행: `authorize` 패치와 `owner_calls` 아래에서 `e._formal(...)`.
- 단언: `formal_verifier` 호출의 `expected_toolchain` 키워드가 `TE-old`의 `toolchain`과 같다. 형식 결과의 `publication_state`가 `'accepted'`이고 지식은 사용 불가다. `_start_identity_review`가 `kid`로 한 번 불린다. 실행 기록이 `status='ended'`, `outcome='output_accepted'`, `submission_receipt.state='accepted'`다.
- 대역: 빌드의 자동 사양 대역과 `Mock` 검증기, `governance.authorize` 패치.

### `test_review_start_failure_produces_a_storable_wait_after_formal_acceptance` (행 136–163)
- 성질: 형식 결과를 수리한 뒤 동일성 검토 시작이 실패하면, 형식 결과와 실행 종료는 유지된다. 그리고 저장 계약을 통과하는 대기 기록(다음 소유자 `review_policy`)이 남는다.
- 준비: `formal_boundary_engine`. `_start_identity_review`의 `side_effect`를 `ValueError('adopted review policy is required before review admission')`로 둔다.
- 실행: `e._formal(action)`. 이어 대기 기록을 저장 계약으로 검사한다. `record_fixtures.execution_state()`의 구조적으로 완전한 실행 상태(`object_format='sha1'`)를 가져와, 그 실행 `EX-1`의 ID를 실제 실행 ID로 바꾸고 활동의 `assigned_execution_ids`를 맞춘다. 거기에 엔진의 `waiting_actions`를 복사해 `default_state_contract().validate(instance, runtime)`를 부른다.
- 단언: 대기 기록의 ID가 원래 행동 ID와 다르다. 대기 행동의 역할은 `'identity_review'`, 대상은 `kid`다. `next_owner`는 `'review_policy'`이고 `reason`에 `'adopted review policy'`가 있다. 대기 기록이 가리키는 실행이 `('ended', 'output_accepted')`다. 형식 결과는 `accepted`다. 저장 계약 검사가 예외 없이 끝난다.
- 대역: 빌드의 대역과 `_start_identity_review`의 `side_effect`.
- 비고: 원문 주석은 "Use a structurally complete execution fixture for the stored reference; the waiting record itself comes unchanged from the actual producer."다. 대기 기록은 실제 생산자의 것을 그대로 쓰고, 주변 실행 기록만 픽스처에서 빌린다.

### `test_changed_olean_blocks_even_fake_verifier` (행 165–180)
- 성질: 승인된 설치의 `.olean` 파일이 바뀌면 검증기가 대역이어도 형식 검사가 시작되지 않는다. 실행은 미완 종료되고 신뢰 관리 쪽 대기가 남는다.
- 준비: `formal_boundary_engine`. `TE-old` 도구 모음 실행 파일의 두 단계 위 폴더에서 `lib/lean/Init/Prelude.olean`을 `'changed'`로 덮어쓴다. 이 파일은 `trust_fixture`가 만든 합성 설치의 것이다.
- 실행: `e._formal(...)`.
- 단언: `formal_verifier`가 불리지 않는다. 실행이 `('ended', 'execution_incomplete')`다. 대기 기록의 `next_owner`가 `'trust_governance'`이고, `reason`에 `'olean fingerprint differs'`가 있으며, `detail.environment_id`가 `'TE-old'`다. `_enqueue`가 불리지 않는다.
- 대역: 빌드의 대역.
- 비고: 제품 문구는 `trust_validation.py` 166행의 `'olean fingerprint differs from the bound toolchain baseline; '`다.

### `test_revision_consumer_passes_declared_scope_and_queues_replacement` (행 182–196)
- 성질: 엔진의 지식 개정 제어는 선언 영향을 받아 개정을 적용하고, 대체 기록의 동일성 검토를 대기열에 넣는다. 대체 기록은 판정 전까지 사용할 수 없고, 결과 상태는 지식 가족 규칙을 지킨다.
- 준비: `bare_engine()`에 `knowledge_graph()` 상태를 싣고, 런타임에 `review_cycles={}`, `executions={}`를 더한다. `_lifecycle_event`와 `_enqueue`를 `create_autospec` 대역으로 바꾼다. 선언 영향은 `impact_declaration(..., k.revision_roots(instance, a))`다.
- 실행: `e._knowledge_control({'operation': 'revise', 'id': a, 'changes': {'summary': 'Clarified summary'}, 'reason': 'clarify', 'declared_impact': impact}, 'UC-fixture')`.
- 단언: 대체 기록의 `usable_links`가 비어 있다. 런타임 대기열에 대체 기록을 대상으로 한 `identity_review`가 있다. `kr.validate_knowledge_records(e.instance)`가 예외 없이 끝난다.
- 대역: `_lifecycle_event`, `_enqueue`의 자동 사양 대역.
- 비고: 이름은 "declared scope를 넘긴다"고 말하지만, 선언 영향이 `revise_knowledge`에 전달되었는지는 직접 단언하지 않는다. 결과 상태만 본다. 대체 기록의 `identity_review`는 `_enqueue`가 아니라 도메인 `replace_knowledge`가 런타임 대기열에 직접 넣는다. 그래서 `_enqueue` 대역과 무관하게 보인다.

### `test_review_starts_from_split_proposal_without_nested_authorities` (행 198–211)
- 성질: 동일성 검토는 분리 가족에서 조립한 제안에서 시작한다. 제안은 원래 Lean 원문과 진술을 담는다.
- 준비: `bare_engine()`에 `knowledge_graph()` 상태를 싣는다. 설정 `{'reviewers': 2, 'review_rounds': 1}`과 `build_review_policy(reviewer_count=2, max_rounds=1)`, 빈 `review_cycles`, `head='fixture-snapshot'`을 둔다. `_enqueue`는 자동 사양 대역이다.
- 실행: `e._start_identity_review(a)`.
- 단언: 새 주기의 `proposal.lean_code`와 `proposal.statement`가 `knowledge_candidate()`의 값과 같다. `validate_knowledge_records`가 통과한다.
- 대역: `_enqueue` 대역.
- 비고: 이름의 "without nested authorities"(제안 안에 형식 결과나 판정 기록이 중첩되지 않음)는 직접 단언하지 않는다. 제안의 두 필드 값만 본다.

## PortableFormalBoundaryTests (행 215–338)

`unittest.TestCase`를 상속하고, 클래스 표지 `@category('lean')`를 단다. `run_tests.py`가 Windows Job 격리 프로세스에서 클래스 단위로 돌린다.

- `setUpClass` (행 217–224): `provider_fixtures.actual_command()`가 가리키는 Lean 실행 파일이 없으면 `unittest.SkipTest('portable Lean is not installed')`를 던진다. 경로는 `DO_MATH_KNOWLEDGE_TEST_LEAN`이나 `portable_bin(toolchain_root())/'lean.exe'`다. 있으면 `formal.verify_lean(source=knowledge_candidate()['lean_code'], declarations=['truth'], ..., lean_command=actual_command())`로 기준 결과 `cls.baseline`을 만들고, `verified`가 아니면 `AssertionError`를 던진다. 기준 결과의 `toolchain`이 이후 승인 도구 모음으로 쓰인다.
- `run_formal(root, change=None, toolchain=None)` (행 226–241): `formal_boundary_engine(root, toolchain or baseline['toolchain'])`으로 실제 설치를 채택한 엔진을 만든다. `formal_verifier`를 `Mock(side_effect=verify)`로 바꾸는데, `verify`는 실제 `formal.verify_lean`을 부르고 `verified`인지 확인한 뒤 결과를 `observed`에 넣는다. `change`가 있으면 컴파일 직후 `change(e)`를 부른다. `authorize` 패치와 `owner_calls` 아래에서 `_formal`을 부른 뒤, `_save` 대역의 모든 호출에서 첫 인자 사전을 모아 경로가 `'/formal.json'`으로 끝나는 산출물을 JSON으로 읽는다. `(e, kid, observed, result)`를 돌려준다.

### `test_actual_approved_command_seals_result_and_ends_execution` (행 243–256)
- 성질: 승인된 실제 명령으로 컴파일하면 결과가 승인 도구 모음으로 봉인되고, 실행이 정상 종료되며, 동일성 검토와 활동 정산이 한 번씩 일어난다.
- 준비: `run_formal(Path(d))`.
- 실행: `run_formal` 안의 `_formal`.
- 단언: 형식 결과가 `accepted`이고 `verification.toolchain`이 `TE-old`의 도구 모음과 같다. 산출물 `formal.json`의 `status`가 `'verified'`다. 검증 호출이 1회다. `dependency_closure.truth`에 `'True.intro'`가 있다. 실행이 `('ended', 'output_accepted')`이고 끝나지 않은 실행이 없다. `_start_identity_review`가 `kid`로, `_settle_activity`가 실행 ID로 각각 한 번 불린다.
- 대역: 빌드의 자동 사양 대역, `Mock`으로 감싼 실제 검증기, `authorize` 패치.
- 비고: 실제 Lean 컴파일(Windows Job).

### `test_actual_exact_source_and_compiler_names_reach_authoritative_consumer_and_artifact` (행 258–282)
- 성질: 비ASCII 선언 이름과 CRLF, 결합 부호가 든 원문이 바이트 그대로 컴파일러에 전달된다. 컴파일러가 낸 선언 이름과 증거가 권위 기록과 산출물에 그대로 남는다.
- 준비: `formal_boundary_engine(Path(d), baseline['toolchain'])`. 형식 결과 기록의 원문을 `'theorem K (Ω : True) : True := Ω\r\ntheorem K : True := True.intro\n-- é\n'`로 바꾼다. 이름은 켈빈 기호 선언과 `K`, 매개변수로 옴 기호(U+2126)를 쓴다. `declaration_names`는 `['K', 'K']`다. `verify`는 받은 `source`의 UTF-8 바이트와 `declarations`가 정확히 같은지 확인한 뒤 실제 `verify_lean`을 부른다.
- 실행: `authorize` 패치와 `owner_calls` 아래에서 `_formal`.
- 단언: `verify` 안에서 원문 바이트와 선언 목록이 일치한다. 형식 결과가 `accepted`이고 `verification.declarations`가 `names`, `declaration_evidence`가 관측 결과와 같다. `_save`로 넘어간 `formal.json`이 관측 결과 전체와 같다.
- 대역: `run_formal`과 같은 구성을 시험 안에서 직접 만든다.
- 비고: 실제 Lean 컴파일.

### `test_identity_change_after_actual_compile_is_caught_at_publication` (행 284–302)
- 성질: 컴파일 뒤 승인된 검사기 파일이 바뀌면, 이미 얻은 형식 결과는 수리되지만 현재 식별을 다시 확인하는 활성 환경 검사가 변경을 잡는다.
- 준비: 제품 `do_math` 패키지 폴더를 임시 폴더의 `checked-checker/scripts/do_math`로 복사한다(`__pycache__` 제외). 도구 모음의 `verifier_path`를 복사본의 `formal.py`로 바꾼다. `change(e)`는 검사기 경로가 작업 공간 안에 있는지 확인한 뒤 파일을 `'changed after actual compilation'`으로 덮어쓴다. 원문 주석은 "A copied checker is the one identity file this test may change."다.
- 실행: `run_formal(Path(d), change, toolchain)`, 이어 `require_active_environment(e.instance, e.runtime, current_identity=True)`.
- 단언: 관측 결과와 산출물이 모두 `verified`이고 형식 결과는 `accepted`다. 주석은 "Nothing is re-observed after compiling; the formal result itself is accepted."다. 환경 검사는 `EnvironmentUnavailable`을 내고, 메시지에 `'approved toolchain file changed: ' + 검사기 경로`가 있다.
- 대역: `run_formal`의 구성.
- 비고: 실제 Lean 컴파일. 제품 문구는 `formal.py` 448행이다.

### `test_current_environment_change_after_actual_compile_prevents_publication` (행 304–314)
- 성질: 컴파일 도중 현재 신뢰 환경 기록이 바뀌면 결과를 공개하지 않고, 실행은 미완 종료된다.
- 준비: `change(e)`는 `TE-old`의 `source_ref`를 `'different-current-approval'`로 바꾼다.
- 실행: `run_formal(Path(d), change)`.
- 단언: 관측 결과는 `verified`다. 산출물 결과는 `status='stopped'`, `reason='trust_environment_changed'`다. 형식 결과의 `verification`이 `{}`로 남는다. 실행이 `('ended', 'execution_incomplete')`다.
- 대역: `run_formal`의 구성.
- 비고: 실제 Lean 컴파일.

### `test_actual_compile_reuses_pinned_version_observation_without_reprobing` (행 316–328)
- 성질: 승인에 고정된 버전 관측을 재사용하므로 `--version`을 다시 묻지 않고, 실행 파일 식별로 컴파일러를 묶는다.
- 준비: 기준 도구 모음 사본의 `version`을 `'pinned approval observation'`으로 바꾼다. 원문 주석은 "Version text is a pinned observation; executable identities, rather than a second process's display string, bind the approved compiler."다.
- 실행: `do_math.formal._job_run`을 `wraps`로 감싼 채 `formal.verify_lean(..., expected_toolchain=approved)`.
- 단언: `status`가 `'verified'`이고 결과의 `toolchain`이 `approved`와 같다. `_job_run` 호출이 1회이고, 그 첫 인자에 `'--version'`이 없다. `dependency_closure.truth`에 `'True.intro'`가 있다.
- 대역: `_job_run`의 `wraps` 대역(호출 기록만).
- 비고: 실제 Lean 컴파일. 엔진을 쓰지 않는다.

### `test_actual_executable_identity_different_from_approved_input_is_rejected` (행 330–338)
- 성질: 실제 실행 파일의 해시가 승인 입력과 다르면 실행 전에 거부한다.
- 준비: 기준 도구 모음 사본의 `sha256`을 `'0'*64`로 바꾼다.
- 실행: `formal.verify_lean(..., expected_toolchain=approved)`.
- 단언: `status='rejected'`, `reason='approved toolchain changed before execution'`, `command`가 `None`이다.
- 대역: 없음.
- 비고: 실제 Lean 설치 파일을 해시하지만 컴파일은 하지 않는다. 클래스 표지 때문에 격리 프로세스에서 돈다.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈:
  - `test_knowledge_io`와 `test_knowledge`는 가져오기, 종류 수명, 개정, 전환 장벽을 도메인 함수 층(1단)에서 본다. 이 모듈은 그 함수들이 엔진 제어와 중앙 형식 소비자에 어떻게 이어지는지 본다.
  - `test_knowledge.KnowledgeRecordTests.test_changed_approved_toolchain_rejects_before_source_execution`은 승인 도구 모음 변경 거부를 `sys.executable`과 합성 파일로 보고, 이 모듈의 `test_actual_executable_identity_different_from_approved_input_is_rejected`는 실제 Lean으로 본다.
  - `test_knowledge_storage`도 `formal_boundary_engine`을 쓰는 실제 Lean 개정·전환 시험을 가진다(`ExactSourceTests`).
  - `test_formal`은 `verify_lean` 자체를 다룬다.
- 픽스처 의존: `knowledge_fixtures.formal_boundary_engine`은 이 모듈과 `test_knowledge_storage`만 쓴다. `provider_fixtures.actual_command`, `state_fixtures.owner_calls`, `research_fixtures.new_instance`와 `bare_engine`, `record_fixtures.execution_state`.
- 이 모듈에만 있는 도우미: `KnowledgeImportTests.send`, `PortableFormalBoundaryTests.run_formal`.
- 실제 외부 자원: Git 자식 프로세스(`KnowledgeImportTests` 전부), 설치 Lean과 Windows Job(`PortableFormalBoundaryTests` 전부).

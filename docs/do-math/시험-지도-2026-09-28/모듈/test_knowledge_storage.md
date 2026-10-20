# test_knowledge_storage

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_knowledge_storage.py` (312행) |
| 클래스 / 테스트 | 2 / 12 |
| 시험 대상 제품 코드 | `do_math/repository.py`의 `ResearchRepository`(`initialize`, `save_with_state`, `load`, `validate_candidate`, `read_record`, `read`), `exact_content_hash`; `do_math/knowledge.py`의 `capture_basis`, `validate_basis`, `plan_impact`, `content_hash`, `revision_roots`, `revise_knowledge`, `begin_transition`, `record_transition_result`, `activate_transition`, `assess_use`; `do_math/knowledge_records.py`의 `proposal_view`, `identity_basis`, `formal_usable`, `usable_links`, `set_assessment_use`, `record_formal_result`; `do_math/knowledge_io.py`의 `import_candidate`; `do_math/engine.py`의 `_apply_bundle_candidate`; `do_math/context_store.py`의 `write_source_catalog`; `do_math/formal.py`의 `verify_lean` |
| 사용하는 픽스처 모듈 | `review_fixtures.KnowledgeRoundtripHarness`(두 클래스의 기반). `knowledge_fixtures`: `formal_boundary_engine`, `knowledge_candidate`. 함수 안 import로 `research_fixtures`의 `bare_engine`, `current_state`와 `provider_fixtures.actual_command`. `test_categories.test_group`(별칭 `category`) |
| 격리 표지 | `ExactSourceTests`의 두 메서드에 `@category('lean')` |
| 시작 상태 | 하네스 `setUp`이 매 시험 실제 Git 저장소(`git_init`)와 합성 신뢰 환경 위에 검증된 미검토 정리 하나를 준비한다. 도메인 상태는 1단식으로 메모리에서 만들고, 저장만 실제 Git으로 한다. 템플릿은 쓰지 않는다 |

## 목적

모듈 docstring은 이 모듈이 실제 Git 저장을 거친 지식 기록을 다룬다고 밝힌다. 대상은 공유 형식 결과, 정확한 원문과 컴파일러 텍스트, 개정 왕복이다. 공통 기반인 `KnowledgeRoundtripHarness`(`review_fixtures.py` 387–469행)의 docstring은 준비 상태를 "실제 Git 저장소에 있는, 검증되었지만 아직 검토되지 않은 정리와 도메인이 만든 봉인 검토"로 설명한다.

이 모듈이 지키는 계약은 세 갈래다.
1. 분리 가족 기록(형식 결과, 해설, 판정, 사용, 전환)은 Git 저장과 재적재를 거쳐도 값과 판정 효력이 그대로다. 저장 계약은 전환 대상의 해설 연결이 어긋나거나 빠진 것을 거부한다.
2. Unicode 정규형 차이(`é`과 `é`, 켈빈 기호 `K`와 `K`)와 CRLF는 원문 바이트, 기준 해시, 동일성 기준, 저장 파일에서 모두 구별되어 보존된다. 합성 동일성 검토 영수증이 바뀐 표현을 덮을 수 없다.
3. 중앙의 설명 개정은 형식 결과를 재사용하고, 대체 기록의 동일성 검토만 대기열에 넣는다. 실제 Lean 컴파일 결과도 개정과 전환을 거쳐 정확히 보존된다.

## 모듈 수준 요소

- 행 7: `sys.path.insert(0, ...parents[1])`로 `scripts/`를 경로 앞에 넣는다(중복 확인 없음).
- 행 8–14: import. `hashlib`은 원문 해시를 다시 계산하는 데 쓴다.
- 행 311–312: 직접 실행하면 `unittest.main()`.

## KnowledgeRoundtripTests (행 17–161)

기반 클래스는 `review_fixtures.KnowledgeRoundtripHarness`(그 기반은 `unittest.TestCase`)이고, 클래스 docstring은 "Actual Git roundtrips with domain-produced sealed, synthetic reviews."다. 클래스 표지와 클래스 속성이 없다.

하네스가 만드는 시작 상태와 도구는 다음과 같다(모두 상속).
- `setUp`: 임시 폴더를 `git_init`으로 저장소로 만들고 `self.root`에 둔다. `self.repo = ResearchRepository(root, new_id('RI'))`를 만든다. `trust_fixture(root, ['synthetic-lean'])`와 `trust_environment(..., environment_id='TE-test', source_ref='synthetic:approval')`로 합성 설치의 환경과 바인딩을 만든다. `verified_knowledge(environment, binding=binding, identity=False)`로 판정 없는 검증 기록 `self.kid`를 만든 뒤, `current_state`로 수명 규칙을 맞춘다. `lean_command=['synthetic-lean']`인 `identity_review` 프로필(`self.profile`)과 용량 제약을 상태에 넣는다.
- `cycle(decision='match', proposal=None)`: 순수 검토 주기(`scoped_start`, `start_review`, `next_actions`, `accept_result`)를 끝까지 돌린다. 각 단계 출력은 `review_stage_output`으로 만들고, `mismatch`나 `unresolved`를 요청하면 초기 단계 출력을 그에 맞게 바꾼다. 단계마다 실행 기록을 만들어 `ended(output_accepted)`까지 옮긴다. 결정이 요청과 같은지 확인한 뒤 주기를 `runtime['review_cycles']`에 넣는다.
- `assessment(decision='match')`: `cycle`의 결과로 `identity_assessment`를 만들어 `record_identity_assessment`로 봉인하고 판정 ID를 돌려준다.
- `roundtrip()`: 처음이면 `repo.initialize`, 이후에는 `repo.save_with_state(self.head, ...)`로 공개한 뒤 `repo.load()`로 `head`, `state`, `runtime`을 다시 읽는다.

모든 시험은 실제 Git 자식 프로세스를 쓴다. `setUp`의 저장소와 `roundtrip`의 저장이 해당한다. 검토 판정은 합성이다.

### `test_shared_formal_result_continuity_round_trips_for_each_exposition` (행 19–69)
- 성질: 한 형식 결과를 공유하는 두 해설은 신뢰 환경 전환을 두 번 거쳐도 각자 연속 판정을 이어받아 사용 가능하다. 모든 단계의 상태가 Git 왕복을 통과한다. 저장 계약은 전환 대상의 해설 ID가 어긋나거나 빠진 런타임을 거부한다.
- 준비: 하네스 상태. 첫 기록의 판정을 `assessment()`로 봉인한다. 같은 형식 결과를 `formal_result_ref`로 재사용하고 제목과 설명만 다른 둘째 후보를 가져와(`actor_ref='second-author'`), `self.kid`를 둘째로 바꾸고 판정을 봉인한다. 한 번 `roundtrip()`한다.
- 실행: 환경 `TE-next`, `TE-third` 각각에 대해 차례로 다음을 한다.
  1. 현재 활성 환경을 복사해 `registered` 환경을 만들고 같은 바인딩을 복사한다. 주석은 "Registering the same shared toolchain record again binds the same baseline."이다.
  2. `begin_transition`을 부른다.
  3. 대상마다 기존 검증에 새 도구 모음만 바꾼 결과를 `record_transition_result`로 넣는다.
  4. 전환을 런타임 `trust_transitions`에 넣고 `roundtrip()`한다.
  5. 저장된 전환으로 `activate_transition`을 부르고 `status='active'`로 둔 뒤 다시 `roundtrip()`한다.
  6. 저장 계약 검사를 두 번 한다. 한 번은 첫 대상의 `exposition_id`를 둘째 것으로 바꾼 런타임 사본, 한 번은 첫 대상의 `exposition_id`를 지운 사본으로 `self.repo.validate_candidate`를 부른다.
- 단언: 첫 왕복 뒤 둘째 기록의 `formal_result_id`가 공유 ID다. 전환마다 대상 ID가 두 기록이고, 각 대상의 `exposition_id`가 기록의 현재 해설과 같다. 활성화 뒤 기록마다 `previous_assessment_id`가 직전 판정인 새 판정이 있다. 그 판정의 해설은 `supersedes`로 직전 판정의 해설을 가리키고, 기록은 `usable_links`가 비어 있지 않다. 어긋난 사본과 빠진 사본은 둘 다 `ValueError`(유형만)다.
- 대역: 없음(검토 판정은 합성).
- 비고: 한 시험 안에서 저장소 공개가 다섯 번 일어난다. 연속 판정의 사슬(`previous_assessment_id`)을 두 번의 전환에 걸쳐 따라간다.

### `test_unicode_currentness_and_impact_survive_actual_storage` (행 71–82)
- 성질: 분해형 Unicode 제목을 가진 기록의 기준과 영향 계획이 Git 왕복 뒤에도 그대로다. 내용 해시는 두 정규형을 구별하고, 의미가 바뀌면 기준이 무효가 된다.
- 준비: 판정을 봉인하고 제목을 `'Café'`(분해형)로 바꾼다. `capture_basis([kid])`와 `plan_impact([kid], [])`를 떠 둔다.
- 실행: `roundtrip()`, 이어 기준 검증과 계획 재계산. 끝으로 제목을 `'Changed meaning'`으로 바꿔 기준을 다시 검증한다.
- 단언: 왕복 뒤 제목이 `'Café'` 그대로다. 기준이 유효하다. 계획이 왕복 전과 같다. `knowledge.content_hash({'title': 'Café'})`와 `{'title': 'Café'}`의 값이 다르다. 제목 변경 뒤 기준이 무효다.
- 대역: 없음.

### `test_raw_lean_source_hash_and_record_basis_preserve_unicode_distinctions` (행 84–92)
- 성질: Lean 원문의 해시와 형식 결과 기록의 기준은 Unicode 정규형 차이를 구별한다. 원문이 정규형만 바뀌어도 기준이 무효가 되고 형식 결과를 쓸 수 없게 된다.
- 준비: 형식 결과의 `lean_code` 앞에 `'-- Café\n'`을 붙이고, `verification.source_sha256`을 새 원문의 SHA-256으로 맞춘다.
- 실행: `kr.formal_usable`, `capture_basis([formal id])`. 이어 원문의 `'Café'`을 `'Café'`로 바꾸고 `validate_basis`와 `formal_usable`을 다시 부른다.
- 단언: 처음 `formal_usable`이 참이다. 바꾼 뒤 기준이 무효이고 `formal_usable`이 거짓이다.
- 대역: 없음.
- 비고: 이 시험은 `roundtrip()`을 부르지 않는다. 하네스의 Git 저장소는 만들어지지만 저장 왕복은 없다.

### `test_current_mismatch_has_active_effect_without_positive_knowledge` (행 94–103)
- 성질: 현재 기준의 `mismatch` 판정은 활성 효력을 가진다(사용 가능한 판정). 그래도 지식을 사용 가능하게 만들지는 않는다. 정지와 재활성을 거쳐도 봉인 판정은 바뀌지 않는다.
- 준비: `assessment('mismatch')`로 불일치 판정을 봉인하고 `roundtrip()`한다. 주석은 "Baseline must pass sealed-review and storage validation."이다. 판정 사본을 떠 둔다.
- 실행: `set_assessment_use`로 `suspended`를 거쳐 `active`로 되돌리고 `roundtrip()`한다.
- 단언: 판정이 사본과 같다. `knowledge.assess_use(판정, state)['valid']`가 참이다. 지식의 `usable_links`가 `[]`다.
- 대역: 없음.

### `test_central_explanation_revision_reuses_formal_and_schedules_only_replacement` (행 105–161)
- 성질: 연구 실행의 확장 묶음에 담긴 설명 개정을 중앙이 적용하면 다음이 성립한다. 형식 결과를 재사용하고, 옛 기록의 형식 검사와 동일성 검토 대기를 거두며, 무관한 대기와 기존 이력은 보존하고, 대체 기록의 동일성 검토 하나만 대기열에 넣는다. 결과는 저장 계약을 통과한다.
- 준비:
  1. 판정을 봉인하고 `roundtrip()`한다. 원래 형식 결과를 복사해 둔다.
  2. 변경은 `{'summary': 'Clearer summary of the unchanged formal proposition'}`이고, 영향은 `revision_roots`로 계산한 `computed_impact`다.
  3. `research_work` 프로필을 상태에 넣고 활동을 연 뒤 실행 기록을 만든다. 실행의 확장은 `knowledge_changes`(`id`, `changes`, `impact_set`, `reason`)이고, 실행을 `running`까지 옮긴다.
  4. 대기열에 옛 기록을 대상으로 한 `formal_check`(낡은 대기)와 `research_work`(보존될 대기)를 넣는다. 이력 사본을 떠 둔다.
  5. `bare_engine(state, runtime, head=self.head, store=self.repo)`로 실제 저장소를 쓰는 메모리 엔진을 만든다. `_enqueue`와 `_invalidate_goal_currentness`는 `create_autospec` 대역으로 바꾼다. 주석은 각각 "Unrelated planner wake-up; domain follow-up remains real.", "Goal consensus is another owner's consumer."다.
  6. 실행의 `input_snapshot`을 `head`로 두고, 편입 묶음을 만든다. 묶음에는 `integration_id`, `payload_sha256`, `members=['activity-extensions.json/knowledge_changes/0']`, `extensions`, `output={}`, `owns_response=False`, `impact_set`, `previous_hashes`가 들어간다.
- 실행: `engine._apply_bundle_candidate(state, runtime, bundle, action=action, execution_id=eid, extensions=...)`, 이어 `roundtrip()`.
- 단언: `supersedes`가 옛 기록인 대체 기록이 정확히 하나다. 그 `formal_result_id`가 원래 ID이고, 원래 형식 결과가 사본과 같다. 옛 기록을 대상으로 한 `formal_check`와 `identity_review`가 대기열에 없다. 보존 대기가 대기열에 남아 있다. 이전 이력이 앞부분에 그대로 있다. 대체 기록을 대상으로 한 대기 역할이 `['identity_review']`다. 마지막 `roundtrip()`이 예외 없이 끝난다.
- 대역: `_enqueue`, `_invalidate_goal_currentness`의 자동 사양 대역.
- 비고: 원문 주석(143–144행)은 "Candidate application now owns knowledge revisions; extension-only bundles do not own the separate research response/task disposition."이다. 시작 상태는 실제 Git 저장소에 연결한 `bare_engine`이며 네 단 가운데 어디에도 들지 않는다.

## ExactSourceTests (행 164–308)

기반 클래스는 `KnowledgeRoundtripHarness`이고, 하네스의 `setUp`, `cycle`, `assessment`, `roundtrip`을 그대로 쓴다(위 절 참고). 클래스 표지와 클래스 속성이 없다. 실제 Lean 시험 두 개에만 메서드 표지 `@category('lean')`가 붙는다.

- `_actual_lean_revision_transition(persist)` (행 251–308): 두 `lean` 시험이 공유하는 시나리오다. 인자 `persist`는 각 단계 뒤에 부를 저장 함수다. Git 변형은 `self.roundtrip`을, 도메인 변형은 아무것도 하지 않는 `lambda: None`을 넘긴다. 순서는 다음과 같다.
  1. 원문 `'theorem K (Ω : True) : True := Ω\r\ntheorem K : True := True.intro\n-- é\n'`과 이름 `['K', 'K']`를 실제 `verify_lean`(명령 `actual_command()`, 작업 공간 `self.root`)으로 컴파일해 `verified`인지 확인한다.
  2. 그 도구 모음으로 `formal_boundary_engine(self.root, observed['toolchain'])`을 만들어 새 `self.kid`를 얻는다. 주석은 "Installed compiler; authority adoption and noncompiler clean-build evidence are the same explicit synthetic fixtures as the central boundary tests."다.
  3. 엔진 상태와 하네스의 프로필·용량 제약으로 `current_state`를 다시 만든다. 형식 결과의 원문과 이름을 위 값으로 바꾸고 `persist()`한다. 주석은 "The Git case checks candidate transport before compilation."이다.
  4. `proposal_view`의 원문 바이트가 입력과 같은지 확인한다.
  5. 그 원문과 이름으로 `expected_toolchain`을 준 `verify_lean`을 다시 돌려 `verified`를 확인하고, `record_formal_result(..., 'TE-old')`로 수리한다. 형식 결과를 복사한 뒤 `persist()`한다. 형식 결과가 사본과 같고 `source_sha256`이 원문의 SHA-256인지 확인한다.
  6. 요약만 바꾸는 `revise_knowledge`(선언 영향은 계산된 영향)를 적용하고 대체 기록으로 `self.kid`를 옮긴 뒤 `persist()`한다. 대체 기록이 같은 형식 결과를 쓰고, 형식 결과가 사본과 같으며, 요약이 바뀌었는지 확인한다.
  7. `TE-old`를 복사한 `TE-next`(`registered`, `source_ref='synthetic:next-adoption'`)와 같은 바인딩을 둔다. `begin_transition`을 부르고 관측 결과를 `record_transition_result`로 넣은 뒤, 런타임 `trust_transitions`에 두고 `persist()`한다. 저장된 전환 결과의 `declaration_evidence`가 관측값과 같은지 확인한다.
  8. `activate_transition` 뒤 `status='active'`로 두고 `persist()`한다. 새 형식 결과의 원문 바이트, 이름, `declaration_evidence`가 입력·관측과 같은지, 옛 형식 결과가 사본과 같은지, 새 형식 결과가 `formal_usable`인지 확인한다.

### `test_actual_git_candidate_preserves_exact_source_and_declaration_names` (행 165–182)
- 성질: 켈빈 기호 선언, 결합 부호, CRLF가 든 후보를 Git에 저장하고 다시 읽어도 원문 바이트와 선언 이름이 그대로다. 기준과 영향 계획이 유지되고, 저장 파일의 물리 바이트가 기록된 해시와 맞는다.
- 준비: 하네스 상태에 원문 `'theorem K : True := True.intro\n-- é\r\n'`, 이름 `['K']`인 후보를 가져온다. 형식 결과와 해설의 `capture_basis`, 그리고 형식 결과를 뿌리로 한 `computed_impact`를 떠 둔다.
- 실행: `roundtrip()`, `proposal_view`, `validate_basis`, `plan_impact`, `self.repo.read_record(formal id, head)`, `self.repo.read(path, head)`.
- 단언: 제안 보기의 원문 UTF-8 바이트가 입력과 같다. 이름이 `['K']`다. 기준이 유효하다. 영향이 왕복 전과 같다. 저장 기록의 `lean_code` 바이트가 입력과 같다. 물리 파일 바이트의 SHA-256이 `read_record`의 `sha256`과 같다.
- 대역: 없음.

### `test_identity_basis_distinguishes_exact_exposition_and_compiler_expressions` (행 184–194)
- 성질: 동일성 기준은 해설 텍스트와 컴파일러 선언 증거의 Unicode 정규형 차이를 모두 구별한다.
- 준비: 하네스 상태의 형식 결과와 해설.
- 실행: 해설 첫 항목을 `'Expression é'`과 `'Expression é'`로 바꿔 가며 `kr.identity_basis`를 부른다. 이어 `verification.declaration_evidence.truth.type`을 같은 두 형태로 바꿔 가며 다시 부른다.
- 단언: 두 경우 모두 두 기준이 서로 다르다.
- 대역: 없음.
- 비고: `roundtrip()`을 부르지 않는다.

### `test_synthetic_transition_review_cannot_cover_a_changed_unicode_expression` (행 196–214)
- 성질: 전환 결과의 선언 증거가 바뀌었을 때, 결과에 붙인 합성 동일성 검토 영수증으로는 활성화할 수 없다. 봉인된 단계 검토 런타임이 필요하며, 상태는 바뀌지 않는다.
- 준비: `TE-test`를 복사한 `TE-next`(`registered`)로 전환을 시작한다. 결과의 `declaration_evidence.truth.type`을 `'Exact expression K'`로 바꾸고, `identity_review={'decision': 'match', 'result_digest': ..., 'review_ref': 'synthetic:eligible-review', 'policy_ref': 'synthetic:frozen-policy'}`를 붙인다. 상태 사본을 떠 둔다.
- 실행: `record_transition_result`와 `activate_transition`. 이어 표현을 `'Exact expression K'`로 바꿔 반복한다.
- 단언: 두 활성화 모두 `ValueError`를 메시지 `'sealed staged identity review runtime'`으로 낸다(`assertRaisesRegex`). 두 번 모두 상태가 사본과 같다.
- 대역: 없음.
- 비고: 제품에서는 `compare_formal_results`가 `declaration_evidence` 변경을 보고하고 `runtime`이 없어 거부된다. 원래 증거(`'True'`)와 비교하면 두 번째 표현도 바뀐 것이다. 따라서 두 번째 반복은 켈빈 기호를 라틴 `K`로 바꾼 표현도 같은 이유로 막힌다는 것을 보인다. `roundtrip()`은 부르지 않는다.

### `test_actual_git_preserves_exact_compiler_result_and_mathematical_exposition` (행 216–228)
- 성질: 결합 부호와 CRLF가 든 원문, 선언 증거, 선언 서명, 해설 텍스트가 Git 왕복 뒤에도 기록 그대로이고, 형식 결과가 계속 사용 가능하다.
- 준비: 형식 결과 원문 끝에 `'\n-- é\r\n'`을 붙이고 `source_sha256`을 다시 계산한다. `declaration_evidence.truth.type`과 `declaration_signatures.truth`를 `'String.literal "é"'`로 둔다. 해설 첫 항목을 `'Exact mathematical expression é'`로 둔다. 두 기록을 복사해 둔다.
- 실행: `roundtrip()`.
- 단언: 다시 읽은 형식 결과와 해설이 사본과 같고, `formal_usable`이 참이다.
- 대역: 없음.

### `test_source_catalog_delivers_exact_proposal_text_and_compiler_keys` (행 230–241)
- 성질: 역할 입력의 출처 카탈로그는 제안 보기를 정확한 바이트로 파일에 쓰고, 그 해시를 행에 기록한다. 비ASCII 선언 서명 키도 보존된다.
- 준비: 형식 결과 원문 끝에 `'\n-- é\r\n'`을 붙이고, `declaration_signatures={'K': 'first', 'K': 'second'}`를 둔다. `proposal_view`를 만든다.
- 실행: `write_source_catalog({'proposal': proposal}, self.root)`.
- 단언: 카탈로그 `entries.proposal`의 파일 바이트 SHA-256이 행의 `sha256`과 같고, 그 JSON이 제안 보기와 같다.
- 대역: 없음.
- 비고: Git 왕복은 없다. 하네스 저장소 폴더를 작업 공간으로 쓴다.

### `test_actual_lean_git_revision_and_transition_preserve_exact_inputs_and_evidence` (행 244–245)
- 성질: 실제 Lean 컴파일 결과가 Git 저장을 거친 개정과 전환에서도 정확한 원문, 이름, 선언 증거를 보존한다.
- 준비: 하네스 상태. 시나리오는 클래스 절의 `_actual_lean_revision_transition`이다.
- 실행: `self._actual_lean_revision_transition(self.roundtrip)`. 각 단계 뒤에 실제 Git 왕복을 한다.
- 단언: 도우미 안의 단언 전부(클래스 절의 1–8단계).
- 대역: `formal_boundary_engine`의 엔진은 도메인 상태를 만드는 데만 쓰고, `_formal`은 부르지 않는다. 컴파일은 실제 `verify_lean`이다.
- 비고: `@category('lean')`. 실제 Lean 컴파일(Windows Job)과 Git 자식 프로세스를 쓴다. `PortableFormalBoundaryTests`와 달리 설치 Lean이 없을 때 건너뛰는 장치가 없다. Lean이 없으면 첫 `verify_lean`의 `status` 단언에서 실패한다.

### `test_actual_lean_domain_revision_and_transition_preserve_exact_inputs_and_evidence` (행 248–249)
- 성질: 같은 성질을 저장 없이 도메인 층에서만 확인한다.
- 준비: 하네스 상태. 시나리오는 `_actual_lean_revision_transition`이다.
- 실행: `self._actual_lean_revision_transition(lambda: None)`.
- 단언: 도우미 안의 단언 전부.
- 대역: 위와 같다.
- 비고: `@category('lean')`. Git 변형과의 차이는 `persist`가 아무것도 하지 않는다는 것뿐이다. 두 시험의 결과를 비교하면 실패가 저장에서 나는지 도메인에서 나는지 가를 수 있다. 하네스 `setUp`은 여전히 Git 저장소를 만든다. 설치 Lean이 없을 때 건너뛰는 장치가 없는 점은 Git 변형과 같다.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈:
  - `test_knowledge`와 `test_knowledge_io`는 같은 도메인 함수를 저장 없이 본다. 이 모듈은 Git 왕복을 더한다.
  - `test_reassessment`는 같은 하네스(`KnowledgeRoundtripHarness`)를 기반으로 재평가를 본다(`DomainReassessmentTests`, `ReassessmentGitTests`).
  - `test_knowledge_import_engine.PortableFormalBoundaryTests`는 `formal_boundary_engine`과 실제 Lean으로 중앙 형식 소비자 `_formal`을 본다. 이 모듈의 실제 Lean 시험은 `_formal`을 거치지 않고, 도메인 수리·개정·전환과 저장을 본다.
  - `test_family_records`는 가족 파일 저장 계약 일반을 본다.
- 픽스처 의존: `review_fixtures.KnowledgeRoundtripHarness`(이 모듈과 `test_reassessment`가 쓴다), `knowledge_fixtures.formal_boundary_engine`, `knowledge_candidate`, `research_fixtures.bare_engine`, `current_state`, `provider_fixtures.actual_command`.
- 이 모듈에만 있는 도우미: `ExactSourceTests._actual_lean_revision_transition`.
- 실제 외부 자원: 모든 시험의 Git 저장소 준비. 실제 저장 왕복은 `roundtrip()`을 부르는 시험에서만 일어난다. 설치 Lean과 Windows Job은 `lean` 표지 시험 두 개가 쓴다.

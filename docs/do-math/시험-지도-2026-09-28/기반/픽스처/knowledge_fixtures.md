# knowledge_fixtures

| 항목 | 값 |
|---|---|
| 원문 | `.claude/skills/do-math/scripts/tests/knowledge_fixtures.py` (189행) |
| 정의 수 | 모듈 함수 10, 클래스 0, 모듈 수준 상수 0 |
| 이 모듈을 쓰는 시험 모듈 | 10개(`consumers.json` 기준). 이 밖에 픽스처 모듈 `engine_fixtures`, `record_fixtures`, `review_fixtures`, `runner_fixtures`가 이 모듈을 쓴다 |
| 모듈 수준 import | `copy.deepcopy`, `pathlib.Path`, 제품 `do_math.knowledge`(`k`)·`knowledge_io`(`io`)·`knowledge_records`(`kr`), `formal.lean_source_sha256`, `repository.exact_content_hash`·`new_id` |

## 목적

모듈 docstring(행 1–30)은 이 모듈을 "지식 후보, 그 합성 형식 증거, 작은 지식 상태"의 모듈이라고 부른다. docstring이 세우는 경계는 두 가지다(행 3–4).
- 여기의 컴파일러 결과는 명시적 대역(`formal_result`)이며, Lean을 실행한 결과가 아니다.
- 식별 평가는 검토를 거치지 않고 직접 기록한다.

이 모듈의 정의는 세 겹이다.
- 가장 작은 조각: 정리 후보 하나(`knowledge_candidate`)와 검증된 컴파일러 결과 하나(`formal_result`)
- 조각을 제품의 지식 기록 함수(`knowledge_io.import_candidate`, `knowledge_records.record_formal_result`·`record_identity_assessment`, `knowledge.revise_knowledge`)에 통과시켜 만든 작은 지식 상태: `add_knowledge`, `knowledge_graph`, `verified_knowledge`
- 형식 검사의 중앙 실행 경계를 시험하기 위한 메모리 엔진: `formal_boundary_engine`

## 구성

화살표(→)는 "부른다"를 뜻한다.

1. **조각.**
   - `knowledge_candidate`
   - `formal_result` → 제품 `lean_source_sha256`, `exact_content_hash`
   - `formal_evidence` → `formal_result`
2. **지식 상태.**
   - `seal_knowledge` → `formal_evidence`, 제품 `kr.record_formal_result`·`identity_basis`·`record_identity_assessment`
   - `add_knowledge` → `knowledge_candidate`, `seal_knowledge`, 제품 `io.import_candidate`
   - `knowledge_graph` → `add_knowledge`, 제품 `new_id`
   - `verified_knowledge` → `knowledge_candidate`, `formal_result`, 제품 `io.import_candidate`, `kr.record_formal_result`·`record_identity_assessment`
3. **개정과 영향.**
   - `impact_declaration` → 제품 `k.plan_impact`
   - `revise_knowledge` → `impact_declaration`, 제품 `k.revision_roots`·`k.revise_knowledge`
4. **형식 경계 엔진.**
   - `formal_boundary_engine` → `research_fixtures.bare_engine`·`trust_fixture`·`trust_environment`·`validation_fixture`·`dispatched_launch`, `add_knowledge`, `formal_evidence`
   - 제품: `trust_validation.environment_errors`, `trust_inventory`, `activities.open_activity`, `execution_profiles.build_profiles`, `session_slots.SessionSlots`
   - `unittest.mock`: `Mock`, `create_autospec`

## 1. 조각

### `knowledge_candidate(**changes)` (행 40–45)
- 종류: 함수(레코드).
- 하는 일과 반환값: 정리 후보 "Truth"를 돌려준다. 필드는 다음과 같다.
  - `kind='theorem'`, `title='Truth'`, `statement='True'`
  - `explanation='Truth holds'`, `summary='Truth'`
  - `lean_code='theorem truth : True := True.intro'`
  - `declaration_names=['truth']`, `dependencies=[]`

  `changes`는 이 필드들을 덮는다(docstring 행 6–7).
- 부작용: 없다.
- 의존: 없다.
- 시작 상태의 단: 1단.
- 소비자: `engine_fixtures`, `review_fixtures`, `test_family_records`, `test_knowledge`, `test_knowledge_import_engine`, `test_knowledge_io`, `test_knowledge_storage`, `test_submission_flow`. 모듈 안에서는 `add_knowledge`와 `verified_knowledge`가 부른다.

### `formal_result(source, declarations, toolchain, *, closure=('True', 'True.intro'), dependency_evidence=('fixture-type', 'fixture-value'), declaration_evidence=('fixture-type', 'fixture-proof'), **extra)` (행 48–59)
- 종류: 대역(검증된 컴파일러 결과).
- 하는 일과 반환값: `source`에 대한 검증된 컴파일러 결과 사전을 돌려준다. 필드는 다음과 같다.
  - `status='verified'`
  - `source_sha256`: 제품 `lean_source_sha256(source)`
  - `declarations`: 목록 사본
  - `toolchain`: 깊은 사본
  - `extra`의 필드
  - `axioms`: 선언마다 빈 목록
  - `dependency_closure`: 선언마다 `list(closure)`
  - `dependency_evidence`: 폐포의 각 이름을 열쇠로 하고, 짝지은 `dependency_evidence` 문자열의 `exact_content_hash`를 값으로 한다. 짝짓기는 `zip`이므로 짧은 쪽에서 끊긴다.
  - `declaration_evidence`: 선언마다 `{'type': declaration_evidence[0], 'value': declaration_evidence[1]}`

  docstring(행 51–53)에 따르면 `extra`는 `allowed_axioms` 같은 필드를 더한다. `dependency_evidence`는 폐포 본문들의 이름표이고, 결과에는 그 해시가 저장된다.
- 부작용: 없다. Lean을 부르지 않는다.
- 의존: 제품 `formal.lean_source_sha256`, `repository.exact_content_hash`.
- 시작 상태의 단: 1단.
- 소비자: `engine_fixtures`, `runner_fixtures`(`formal_ok`). 모듈 안에서는 `formal_evidence`와 `verified_knowledge`가 부른다.

### `formal_evidence(state, kid, env='TE-old')` (행 62–65)
- 종류: 함수.
- 하는 일과 반환값: `state`에 저장된 `kid`의 형식 기록을 찾는다(`state['formal_results'][knowledge[kid]['formal_result_id']]`). 그 기록의 `lean_code`와 `declaration_names`, 그리고 신뢰 환경 `env`의 `toolchain`으로 `formal_result`를 만들어 돌려준다. 폐포와 증거는 기본값을 쓴다.
- 부작용: 없다.
- 의존: `formal_result`.
- 시작 상태의 단: 1단.
- 소비자: `review_fixtures`, `test_family_records`, `test_knowledge`, `test_knowledge_io`. 모듈 안에서는 `seal_knowledge`와 `formal_boundary_engine`이 부른다.

## 2. 지식 상태

### `seal_knowledge(state, runtime, kid, env='TE-old')` (행 68–71)
- 종류: 함수.
- 하는 일과 반환값: 두 기록을 차례로 남긴다.
  1. 제품 `kr.record_formal_result(state, kid, formal_evidence(state, kid, env), env, runtime=runtime)`로 형식 증거를 기록한다.
  2. 제품 `kr.record_identity_assessment(state, kid, {'decision': 'match', 'basis': kr.identity_basis(state, kid)}, 'policy:fixture', runtime=runtime)`로 일치 판정 식별 평가를 기록한다. 검토 주기는 거치지 않는다.

  반환값은 `(state, 평가 ID)`다(docstring 행 13–14).
- 부작용: 없다(제품 기록 함수의 반환 상태를 쓴다).
- 의존: `formal_evidence`, 제품 `knowledge_records.record_formal_result`·`identity_basis`·`record_identity_assessment`.
- 시작 상태의 단: 1단.
- 소비자: `test_knowledge`. 모듈 안에서는 `add_knowledge`가 부른다.

### `add_knowledge(state, runtime, *, verified=True, **changes)` (행 74–79)
- 종류: 함수.
- 하는 일과 반환값: 제품 `io.import_candidate(state, runtime, knowledge_candidate(**changes), source_ref='fixture', actor_ref='producer')`로 후보를 가져온다. `verified`가 참이면 `seal_knowledge`로 봉인한다. 반환값은 `(state, runtime, kid, 평가 ID)`이고, `verified=False`이면 평가 ID는 `None`이다. 봉인은 기본 신뢰 환경 `TE-old`를 쓰므로, `verified=True`인 호출은 상태에 `trust_environments['TE-old']`가 있어야 한다.
- 부작용: 없다.
- 의존: `knowledge_candidate`, `seal_knowledge`, 제품 `knowledge_io.import_candidate`.
- 시작 상태의 단: 1단.
- 소비자: `test_knowledge`, `test_knowledge_io`. 모듈 안에서는 `knowledge_graph`와 `formal_boundary_engine`(`verified=False`)이 부른다.

### `knowledge_graph()` (행 82–96)
- 종류: 함수(레코드).
- 하는 일과 반환값: 봉인된 지식 기록 셋이 서로 엮인 작은 그래프를 만든다(docstring 행 17–19). 절차는 다음과 같다.
  1. 활성 신뢰 환경 `TE-old`를 둔다. 필드는 다음과 같다.
     - `toolchain`: `{'version': 'fixture-old'}`
     - `allowed_axioms`: 빈 목록
     - `source_ref`: `fixture:trust`
     - `toolchain_record`: ID는 `'TC-' + '0'*64`, 경로는 `Path.cwd()/records/<ID>.json`. 이 경로에 실제 파일은 만들지 않는다.
  2. 런타임을 최소 모양(`tasks`, `queue`, `history`)으로 둔다.
  3. `add_knowledge`로 `a`, `b`(`dependencies=[a]`), `c`를 차례로 가져와 봉인한다.
  4. `new_id`로 관계 ID(`RL`), 목표 판정 ID(`GJ`), 과제 ID 둘(`TK`)을 만든다.
  5. 관계, 판정, 과제를 둔다.
     - 관계: `a`→`c`, `active`
     - 현재 목표 판정: `used_sources=[b]`
     - 완료 과제 `task`: 입력 `[b]`, 현재 완료 평가
     - 완료 과제 `unrelated`: 입력 `[c]`, 평가 없음

  반환값은 `(state, runtime, ids)`다. `ids`는 `a`, `b`, `c`, 세 평가 ID `aa`, `ba`, `ca`, `relation`, `goal`, `task`, `unrelated`를 담는 사전이다.
- 부작용: 없다.
- 의존: `add_knowledge`, 제품 `new_id`.
- 시작 상태의 단: 1단.
- 소비자: `test_knowledge`, `test_knowledge_import_engine`, `test_knowledge_io`.

### `verified_knowledge(environment=None, *, binding=None, identity=True, check=None)` (행 110–127)
- 종류: 함수(레코드).
- 하는 일과 반환값: 후보 "Truth"를 신뢰 환경 `TE-test` 아래에서 검증한다. `identity=False`가 아니면 일치로 평가된 상태까지 만든다(docstring 행 22–25). 절차는 다음과 같다.
  1. 빈 상태 `{}`, `{}`에 `io.import_candidate(..., source_ref="source", actor_ref="producer")`로 `knowledge_candidate()`를 가져온다.
  2. 활성 신뢰 환경 `TE-test`를 둔다(`toolchain={"version": "test-fixture"}`, `allowed_axioms=[]`). `environment`가 주어지면 `TE-test` 자리의 기록을 그 깊은 사본으로 바꾼다. `binding`이 주어지면 `runtime['trust_bindings']`를 `{'TE-test': 사본}`으로 둔다.
  3. `formal_result(lean_code, ["truth"], TE-test의 도구 사슬, ...)`로 검증 결과를 만든다. 인자는 `dependency_evidence=('fixture-type', 'fixture-constructor')`, `declaration_evidence=('True', 'True.intro')`이고, `check`의 필드를 더한다. docstring(행 24–25)에 따르면 `check`는 저장되는 중앙 검사의 필드, 예를 들어 원시 출력을 더한다. 이 결과를 `kr.record_formal_result(..., "TE-test", runtime=runtime)`로 기록한다.
  4. `identity=False`이면 `(state, runtime, kid, None)`을 돌려준다.
  5. 아니면 `kr.record_identity_assessment`로 평가를 기록한다. 평가는 `{"decision": "match", "basis": identity_basis, "review_cycle_id": "RC-fixture"}`이고 정책은 `"policy:1"`이다. 반환값은 `(state, runtime, kid, 평가 ID)`다.

  `seal_knowledge`와 다른 점은 다섯이다.
  - 신뢰 환경 이름이 `TE-test`다.
  - 의존 증거 이름표가 `('fixture-type', 'fixture-constructor')`다. `seal_knowledge`가 쓰는 `formal_evidence`는 기본값 `('fixture-type', 'fixture-value')`를 쓴다.
  - 선언 증거가 `('True', 'True.intro')`다. 기본값은 `('fixture-type', 'fixture-proof')`다.
  - 평가에 `review_cycle_id`가 붙는다.
  - 정책 이름이 `policy:1`이다.
- 부작용: 없다.
- 의존: `knowledge_candidate`, `formal_result`, 제품 `knowledge_io.import_candidate`, `knowledge_records.record_formal_result`·`identity_basis`·`record_identity_assessment`.
- 시작 상태의 단: 1단.
- 소비자: `record_fixtures`(`specialist_assessment`), `review_fixtures`, `test_context_store`, `test_knowledge`, `test_planning`, `test_role_input`, `test_state_checks`.

## 3. 개정과 영향

### `impact_declaration(state, runtime, roots)` (행 99–101)
- 종류: 함수.
- 하는 일과 반환값: 제품 `k.plan_impact(state, runtime, roots, [])`의 `computed_impact`를 돌려준다. 이것은 생산자가 선언하는 완전한 계산된 영향이다(docstring 행 20–21). 주석(행 100)에 따르면 완전한 생산자 선언을 모형화한 것이고, 그 국소성은 시험이 따로 단언한다.
- 부작용: 없다.
- 의존: 제품 `knowledge.plan_impact`.
- 시작 상태의 단: 1단.
- 소비자: `test_knowledge`, `test_knowledge_import_engine`. 모듈 안에서는 `revise_knowledge`가 부른다.

### `revise_knowledge(state, runtime, kid, changes=None)` (행 104–107)
- 종류: 함수.
- 하는 일과 반환값: 제품 `k.revise_knowledge`의 결과를 돌려준다. 인자는 다음과 같다.
  - `changes`: 기본값 `{'statement': 'Revised statement'}`
  - `reason='correction'`, `actor_ref='author'`
  - `declared_impact`: `impact_declaration(state, runtime, k.revision_roots(state, kid))`

  곧 개정 뿌리에서 계산한 영향 전체를 선언으로 넘겨 기록 하나를 개정한다.
- 부작용: 없다.
- 의존: `impact_declaration`, 제품 `knowledge.revision_roots`·`revise_knowledge`.
- 시작 상태의 단: 1단.
- 소비자: `test_knowledge`, `test_knowledge_io`.

## 4. 형식 경계 엔진

### `formal_boundary_engine(workspace, toolchain=None)` (행 130–189)
- 종류: 대역(형식 검사 중앙 실행 경계를 위한 메모리 엔진 하네스).
- 하는 일과 반환값: `(engine, kid)`를 돌려준다. `engine`은 신뢰 환경 `TE-old`를 채택한 메모리 엔진이다. `TE-old`의 도구 사슬은 `toolchain`이 주어지면 설치된 실제 도구 사슬이고, 아니면 합성 도구 사슬이다. 엔진은 미검증 후보 `kid` 하나를 갖는다. 형식 검사 주변의 수락, 저장, 검토 시작은 autospec 대역으로 바뀌어 있다(docstring 행 26–30). 절차는 다음과 같다.
  1. **엔진.** `research_fixtures.bare_engine()`으로 저장소 없는 엔진을 만든다. 저장소는 메모리 `StateStore`다.
  2. **신뢰 요청.** `trust_fixture(workspace, 명령)`으로 합성 설치와 기록을 `workspace` 아래에 만든다. 명령은 `toolchain`의 `configured_command`, 없으면 `['fixture']`다.
  3. **실제 도구 사슬(선택).** `toolchain`이 주어지면 주석(행 138–139)대로 실제 설치를 쓴다. 그 식별의 사본으로 제품 `trust_inventory.new_record`를 만든다. 기준선은 실제 `observe_fingerprint(identity)`, 빈 내용 해시 `{'files': {}, 'sha256': exact_content_hash({})}`, `validation_fixture(identity, workspace/'smoke.lean')`로 구성한다. 주석에 따르면 내용 기준선은 대역이며, `--rerecord`와 `--check-contents`만 그것을 읽는다. 이 기록을 `workspace/records/<ID>.json`에 쓰고, 요청의 `toolchain`, `toolchain_record`, `binding`을 이 기록의 것으로 바꾼다.
  4. **신뢰 환경 검증.** `trust_environment(request, environment_id='TE-old', source_ref='synthetic:test-adoption')`로 기록과 결속을 얻는다. 제품 `trust_validation.environment_errors(trust, binding)`가 오류를 내면 `AssertionError('The synthetic trust environment does not validate: ...')`를 던진다.
  5. **상태.** 인스턴스를 `{'active_trust_environment': 'TE-old', 'trust_environments': {...}}`로, 런타임을 최소 모양으로 두고, `add_knowledge(..., verified=False)`로 미검증 후보를 넣는다. 이어서 다음을 설정한다.
     - `instance['workspace']`: `str(workspace)`
     - `instance['config']`: `{'lean_command': ['unapproved-config-command']}`. 주석(행 156)에 따르면 의도적으로 다른 값이다. 중앙 실행이 설정 명령이 아니라 승인된 명령을 써야 함을 시험하기 위해서다.
     - 런타임: `status='ready'`, 빈 `executions`·`activities`·`trust_transitions`, `trust_bindings={'TE-old': binding}`
     - `engine.head`: `'fixture-snapshot'`
  6. **autospec 대역 아홉.** 엔진 메서드 `_save`, `_controls`, `_execution_profile`, `_settle_activity`, `_remove_action`, `_start_identity_review`, `_action_lifecycle_gate`, `_require_action_clock`, `_enqueue`를 `create_autospec`으로 바꾼다. 원 서명은 지키지만 동작은 하지 않는다.
  7. **실행 프로필.** `_execution_profile`의 반환값을 `formal_check` 역할 프로필로 정한다. 이 프로필은 `build_profiles({**DEFAULT_CONFIG, 'lean_command': 신뢰 환경의 설정 명령})`으로 만든다.
  8. **세션 슬롯.** `_session_slots`를 autospec으로 바꾼다. 반환값은 `SessionSlots` 인스턴스 모양의 autospec이다. 주석(행 168–169)에 따르면 등록은 여기서 호스트 대역이고 실제 공유 예약은 없으며, 컴파일러 자식 프로세스는 `PortableFormalBoundaryTests`에서 실제로 남는다.
  9. **활동.** 제품 `activities.open_activity`로 활동 `AT-fixture`(`formal_check`, 입력 `[kid]`)를 열고, `_activity_for_action`이 이 활동을 돌려주게 한다. `_check_conversations`는 `False`를 돌려준다.
  10. **실행 등록.** `_register_execution`을 autospec으로 바꾸고 `side_effect`로 안쪽 함수 `register(action, row, *, profile=None)`를 준다. `register`는 행에 `research_fixtures.dispatched_launch(row['id'], 형식 검사 프로필)` 실행 표, `action`, `activity_id='AT-fixture'`를 붙이고, 런타임 `executions`에 넣은 뒤 행을 돌려준다.
  11. **기계 시작.** `_machine_started`를 autospec으로 바꾸고 `side_effect`로 `started(execution_id, identity)`를 준다. `started`는 대역 `_save()`를 부른다. 주석(행 183–184)에 따르면 이 픽스처는 수락과 저장을 대체하지만 컴파일러 잡은 실제다. 그래서 멈춘 채 시작한 잡의 시작 확인도 같은 합성 소유자를 거친다.
  12. **검증기.** `engine.formal_verifier`를 `Mock(return_value=formal_evidence(engine.instance, kid))`로 둔다. 증거는 `TE-old` 도구 사슬 아래의 검증 결과다.
- 부작용: `workspace` 아래에 `trust_fixture`의 합성 도구 사슬 디렉터리와 기록 파일이 생긴다. `toolchain`이 주어지면 `workspace/records/`에 실제 도구 사슬의 기록 파일이 하나 더 생긴다. 엔진 메서드 열두 개(6의 아홉, `_session_slots`, `_activity_for_action`, `_check_conversations`)와 `_register_execution`, `_machine_started`를 인스턴스 속성으로 덮는다. 저장소나 Git은 쓰지 않는다.
- 의존: `research_fixtures.bare_engine`·`trust_fixture`·`trust_environment`·`validation_fixture`·`dispatched_launch`, `add_knowledge`, `formal_evidence`, 제품 `trust_validation.environment_errors`, `trust_inventory`, `activities.open_activity`, `configuration.DEFAULT_CONFIG`, `execution_profiles.build_profiles`, `session_slots.SessionSlots`, `repository.exact_content_hash`.
- 시작 상태의 단: 네 단 밖의 메모리 엔진 대역이다. `toolchain`을 주면 실제 설치된 Lean의 식별을 쓴다.
- 소비자: `test_knowledge_import_engine`, `test_knowledge_storage`.

## 관계

**다른 픽스처 모듈과의 의존.** 이 모듈은 모듈 머리에서 제품 모듈만 import한다. `research_fixtures`(`bare_engine`, `trust_environment`, `trust_fixture`, `validation_fixture`, `dispatched_launch`)는 `formal_boundary_engine` 안에서만 늦게 import한다. 반대 방향으로는 네 픽스처 모듈이 이 모듈을 쓴다.
- `runner_fixtures.formal_ok`: 컴파일러 대역의 결과를 `formal_result`로 만든다.
- `record_fixtures.specialist_assessment`: `verified_knowledge`를 쓴다.
- `engine_fixtures`: `knowledge_candidate`, `formal_result`를 쓴다.
- `review_fixtures`: `knowledge_candidate`, `formal_evidence`, `verified_knowledge`를 쓴다.

다른 픽스처 모듈의 컴파일러 대역도 이 모듈의 `formal_result`로 형식 결과를 만든다. `runner_fixtures.formal_ok`와 `engine_fixtures.formal_verification`(`FakeEngine`의 컴파일러 대역)이 그렇다. 다만 이 모듈이 합성 형식 결과의 유일한 원천은 아니다. `review_fixtures`(행 106–109)는 옛 모양 지식 기록 `K1`의 `formal` 필드를 복사한 뒤 `dependency_closure`, `dependency_evidence`, `declaration_evidence`를 손으로 채워 `record_formal_result`에 넘긴다. 형식 결과의 모양이 바뀌면 그 자리도 함께 고쳐야 한다.

**시작 상태 체계에서 맡는 자리.** `formal_boundary_engine`을 뺀 아홉 정의는 `시험-지침.md` 4절 규칙 3의 1단에 속한다. 저장소 없이 제품의 지식 기록 함수에 넘길 상태를 만든다. `formal_boundary_engine`은 `research_fixtures.bare_engine` 위의 메모리 엔진으로, 형식 검사의 중앙 실행 경계만 실제로 두고 나머지 엔진 협력자를 autospec 대역으로 둘러싼 하네스다.

# test_knowledge

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_knowledge.py` (721행) |
| 클래스 / 테스트 | 2 / 57 |
| 시험 대상 제품 코드 | `do_math/knowledge.py`의 `capture_basis`, `validate_basis`, `assess_use`, `assess_research_use`, `decision_reference`, `plan_impact`, `apply_impact`, `propagate`, `revise_knowledge`, `invalidate_knowledge`, `suspend_for_source_change`, `begin_transition`, `record_transition_result`, `activate_transition`, `invalidate_environment`, `validate_changes`, `AUTHORED_FIELDS`; `do_math/knowledge_records.py`의 `create_candidate`, `record_formal_result`, `record_identity_assessment`, `set_assessment_use`, `identity_basis`, `proposal_view`, `reader_view`, `knowledge_view`; `do_math/knowledge_io.py`의 `import_candidate`, `ensure_ontology`, `catalog_definitions`, `register_kind_definition`, `check_kind_definition`, `activate_kind_definition`, `withdraw_kind_definition`, `validate_relation`, `BUILTIN_DEFINITIONS`; `do_math/formal.py`의 `verify_lean`, `portable_bin`, `toolchain_root`; `do_math/repository.py`의 `ResearchRepository`; `do_math/state_contract.py`의 `default_state_contract`, `validate_record`; `do_math/record_schemas.py`의 `RECORDS` |
| 사용하는 픽스처 모듈 | `knowledge_fixtures`: `add_knowledge`, `formal_evidence`, `impact_declaration`, `knowledge_graph`, `revise_knowledge`, `seal_knowledge`, `knowledge_candidate`, `verified_knowledge`. `research_fixtures`: `git_init`, 함수 안에서 `trust_environment`, `trust_fixture`, `current_state`. `review_fixtures`: 함수 안에서 `scoped_start`. `test_categories.test_group`(별칭 `category`) |
| 격리 표지 | `KnowledgeRecordTests.test_installed_lean_extracts_transitive_constants`에 `@category('lean')` |
| 시작 상태 | 대부분 1단(도메인 함수 직접 호출). 시작 상태는 `knowledge_graph()`나 `verified_knowledge()`의 메모리 상태다. 실제 Lean을 부르는 시험 1개, 실제 Git 저장소를 쓰는 시험 1개, 실제 파일과 `sys.executable`로 승인 도구 모음을 흉내 내는 시험 1개가 있다 |

## 목적

모듈 docstring은 이 모듈이 지식 기록의 다섯 영역, 곧 현재성, 영향, 개정, 종류, 신뢰 환경을 다룬다고 밝힌다. 또 도메인 픽스처의 커널 증거는 시험 대역이며, `lean` 표지가 붙은 시험만 설치된 컴파일러를 돌린다고 말한다. 제품 쪽 정본은 `knowledge.py`의 docstring(1–5행) "This module records and propagates semantic state. It does not run formal tools, enforce OS isolation, or infer mathematical equivalence."와 `knowledge_records.py`의 "Separate knowledge authorities and derived, never-persisted K/proposal views."다.

두 클래스는 대략 다음처럼 나뉜다. `KnowledgeTests`는 세 기록 그래프(`knowledge_graph`) 위에서 개정, 철회, 영향 전파, 출처 현재성, 신뢰 환경 전환과 복구를 본다. `KnowledgeRecordTests`는 한 기록(`verified_knowledge`)이나 작은 수작업 상태 위에서 권위 가족의 분리, 종류 정의, 형식 증거의 모양(의존 본문 해시표), 전환 경계, 영향 계획의 불변성, 저장 왕복을 본다.

주요 제품 규칙은 다음과 같다.
- 지식의 사용 가능성(K)은 저장 필드가 아니라 전제에서 유도된다. `usable_links`(`knowledge_records.py`)는 기록 전제(`record_premises_current`: 활성 수명, 활성 종류, 현재 출처, 사용 가능한 의존, 관계 끝점 기준)와 `formal_usable`, `match` 판정, 판정 기준(`identity_premise`) 일치, 활성 사용 기록을 모두 요구한다.
- 영향 계획(`plan_impact`, `knowledge.py` 228–266행)은 참조 필드를 따라 닫힘을 계산한다. `dependencies`, `formal_result_refs`, `assessment_refs` 등은 엄격(strict) 필드이고, `inputs`, `used_sources`, `origin_refs` 등은 관대(lenient) 필드다. 관대 필드는 알려진 ID이거나 `KN-` 형식일 때만 참조로 센다. `history` 같은 이력 키는 건너뛴다.
- 적용(`_apply_impact_effects`)은 판정을 고치지 않는다("Sealed judgment is immutable."). 대신 형식 결과의 `formal_use`를 `suspended`로(뿌리가 모두 판정이나 판정 사용 기록이면 형식 결과는 건드리지 않는다), 판정의 사용 기록을 `suspended`로, 과제의 `input_current`와 판정 `current`를 거짓으로, 관계를 `suspended`로, 목표 판정의 `current`를 거짓으로 바꾼다. 과제 수명은 건드리지 않는다.
- 신뢰 환경 전환은 옛 형식 결과와 판정을 그대로 두고, 새 형식 결과·해설·연속 판정을 새 ID로 만든다(`activate_transition`).

## 모듈 수준 요소

- 행 11: `sys.path.insert(0, ...parents[1])`로 `scripts/`를 경로 앞에 넣는다(중복 확인 없음).
- 행 12–19: 제품과 픽스처 import. `knowledge`와 별칭 `k`가 같은 모듈이다. `test_categories.test_group`은 `category`라는 이름으로 들여온다.
- `withdraw(state, runtime, kid)` (행 22–24): `k.invalidate_knowledge`를 `reason='false'`, `actor_ref='reviewer'`로 부른다. 선언 영향으로는 `impact_declaration(state, runtime, [kid])`, 곧 계산된 영향 전체를 넘긴다. 철회를 쓰는 `KnowledgeTests`의 시험 여러 개가 쓴다.
- `transition(state)` (행 27–31): 상태 사본에 `status='registered'`, `toolchain={'version': 'fixture-new'}`인 환경 `TE-new`를 더하고 `k.begin_transition(state, 'TE-new')`를 부른다. `(state, env, transition)`을 돌려준다. 전환 시험들이 쓴다.
- `finish_transition(state, env, tr)` (행 34–37): 전환의 모든 대상에 새 환경 도구 모음으로 만든 `formal_evidence`를 결과로 기록한 뒤 `k.activate_transition(state, tr)`을 부른다. `runtime`은 넘기지 않으므로 증거가 달라 동일성 검토가 필요한 대상이 있으면 거부된다.
- 행 721: 직접 실행하면 `unittest.main(verbosity=2)`.

## KnowledgeTests (행 40–336)

`unittest.TestCase`를 상속한다. 표지, 클래스 속성, 설정·정리 훅, 도우미 메서드가 없다. 거의 모든 시험이 `knowledge_graph()`에서 시작한다. 이 상태의 신뢰 환경은 `TE-old`(활성, `toolchain={'version': 'fixture-old'}`)다. 기록은 셋이다. `a`, `a`에 의존하는 `b`, 그리고 `c`이며, 각각 판정 `aa`, `ba`, `ca`로 봉인되어 있다. 여기에 관계 `a→c`, `b`를 쓰는 현재 목표 판정 하나, `b`를 입력으로 하고 판정이 현재인 완료 과제 `task`, `c`를 입력으로 하는 완료 과제 `unrelated`가 있다. 시작 상태는 1단이다.

### `test_explanation_revision_reuses_only_current_formal_evidence` (행 41–71)
- 성질: 설명만 바꾸는 개정은 옛 형식 결과가 현재 사용 가능할 때만 그것을 재사용한다. 그렇지 않으면 새 형식 후보를 만들어 형식 검사를 다시 받는다. 어느 경우든 옛 형식 결과는 바뀌지 않고, 옛 기록의 형식 검사 대기는 남지 않는다.
- 준비: 형식 결과 상태 네 가지마다 `TE-old`만 있는 상태에 `add_knowledge(verified=False)`로 후보를 넣는다. `candidate`는 증거를 기록하지 않는다. `rejected`는 `formal_evidence`의 `status`를 `failed`로 바꿔 기록한다. `suspended`는 검증 증거를 기록한 뒤 `formal_use='suspended'`로 바꾼다. `verified`는 검증 증거를 그대로 기록한다.
- 실행: 픽스처 `revise_knowledge(ins, run, kid, {'summary': 'Corrected summary'})`.
- 단언: 대체 기록의 `formal_result_id`가 옛 ID와 같은지 여부가 `status == 'verified'`와 일치한다. 옛 형식 결과가 개정 전 사본과 같다. 대체 기록을 대상으로 하는 대기 행동이 정확히 하나이고, 그 역할은 재사용이면 `identity_review`, 아니면 `formal_check`이다. 옛 `kid`를 대상으로 하는 `formal_check`는 없다. 재사용이 아니면 새 형식 결과의 `verification`은 `{}`, `publication_state`는 `'candidate'`다.
- 대역: 없음.
- 비고: `subTest(status=...)` 네 개. 제품 근거는 `replace_knowledge`의 주석 "Reuse unchanged formal evidence only while it is currently usable."이다.

### `test_nonformal_explanation_revision_still_returns_to_planning` (행 73–80)
- 성질: Lean 원문이 없는 기록을 개정하면 형식 결과 없이 연구 계획으로 돌아간다.
- 준비: 빈 상태에 `add_knowledge(verified=False, lean_code='', declaration_names=[])`.
- 실행: 픽스처 `revise_knowledge(..., {'summary': 'Corrected observation'})`.
- 단언: 대체 기록의 `formal_result_id`가 `None`이고, 대체 기록을 대상으로 하는 대기 역할이 `['research_plan']`이다.
- 대역: 없음.

### `test_candidate_dependency_not_promoted_by_prerequisite_reverification` (행 81–87)
- 성질: 의존 기록의 판정 사용이 정지된 기록은 선행 기록이 개정되어 다시 봉인되어도 사용 가능으로 올라가지 않는다.
- 준비: `knowledge_graph()`에서 `b`의 판정 `ba`의 사용을 `set_assessment_use(..., 'suspended', 'requires review', 'reviewer')`로 정지한다.
- 실행: 선행 기록 `a`를 개정하고(`revise_knowledge`), 대체 기록을 `seal_knowledge`로 형식 결과와 `match` 판정까지 봉인한다.
- 단언: `k.assess_use(b)['valid']`가 거짓이다.
- 대역: 없음.
- 비고: 단언은 결과 하나만 본다. `b`가 무효인 이유는 셋이 겹친다. 첫째는 `b`의 판정 사용이 정지된 것이다. 둘째는 `a` 개정의 영향 적용(`_apply_impact_effects`)이 `b`의 형식 결과 `formal_use`를 `suspended`로 바꾼 것이다. 같은 준비의 `test_revision_preserves_history_and_only_actual_dependencies_change`가 이 효과를 단언한다. 셋째는 `b`가 여전히 옛 `a`(이제 `superseded`)에 의존한다는 것이다(`record_premises_current`가 의존의 `usable_links`를 요구한다). 어느 이유 때문인지는 가르지 않으므로, 판정 사용 정지가 없어도 이 단언은 통과한다.

### `test_revision_preserves_history_and_only_actual_dependencies_change` (행 89–111)
- 성질: 개정은 새 개정 번호의 대체 기록을 만들고, 판정과 형식 결과의 검증 내용을 보존한다. 실제로 의존하는 기록과 과제, 목표 판정만 현재성을 잃고, 관계로만 이어진 기록과 무관한 과제는 그대로다.
- 준비: `knowledge_graph()`.
- 실행: 픽스처 `revise_knowledge(ins, run, ids['a'])`(기본 변경은 `statement`를 `'Revised statement'`로).
- 단언:
  - 대체 기록의 `revision`이 옛 개정 번호 + 1이다.
  - `identity_assessments`가 같고, `formal_results`의 ID 집합과 각 `verification`이 같다.
  - `b`의 형식 결과 `formal_use`가 `'suspended'`다.
  - 옛 상태의 `proposal_view(a)['statement']`가 `'True'`다.
  - 새 상태에서 `a`의 `lifecycle`이 `'superseded'`다.
  - `b`는 사용 불가, `c`는 사용 가능하다.
  - `task`의 `assessment.current`가 거짓이고, `unrelated` 과제는 원래 그대로다.
  - 목표 판정의 `current`가 거짓이다.
  - 대기열에 대체 기록을 대상으로 한 `identity_review`(`reason='correction'`)가 있다.
  - 모든 대기 행동의 `id`와 `lineage_id`가 같고 ID가 중복되지 않는다.
- 대역: 없음.

### `test_task_dependencies_are_strong_reassessment_edges` (행 113–118)
- 성질: 과제의 `dependencies` 필드는 강한 재평가 간선이다. 거기서 가리킨 지식이 바뀌면 과제의 입력 현재성이 사라지지만, 과제 상태는 바뀌지 않는다.
- 준비: `task`의 `inputs`를 비우고 `dependencies=[b]`로 둔다.
- 실행: 픽스처 `revise_knowledge(ins, run, a)`.
- 단언: `task`의 `input_current`가 거짓이고 `status`는 `'completed'`다.
- 대역: 없음.
- 비고: 제품에서 `dependencies`는 `planning.READ_REFERENCE_FIELDS`의 엄격 필드다(`"dependencies": "strict"`).

### `test_terminal_history_and_unfinished_lifecycle_are_preserved` (행 120–132)
- 성질: 철회가 과제에 전파되어도 과제 상태(완료, 종결, 계획)는 그대로이고, 입력 현재성과 종결 판정의 현재성만 사라지며, 범위 처분은 보존된다.
- 준비: `knowledge_graph()`에 과제 두 개를 더한다. `closed`는 `status='closed'`, 입력 `b`, `scope_disposition={'kind': 'withdraw', 'reason': 'user withdrawal'}`, `assessment={'decision': 'closed', 'current': True}`다. `planned`는 `status='planned'`, 입력 `b`다.
- 실행: 모듈 함수 `withdraw(ins, run, a)`.
- 단언: `task`, `closed`, `planned`의 상태가 각각 `completed`, `closed`, `planned`로 남고, 셋 모두 `input_current`가 거짓이다. `closed`의 `scope_disposition`이 같고, `assessment`는 `{'decision': 'closed', 'current': False}`다.
- 대역: 없음.

### `test_invalidation_preserves_record_and_relation_neighbor` (행 134–141)
- 성질: 기록을 철회하면 그 기록은 `withdrawn`이 되고, 관계로 이어진 이웃 기록은 바뀌지 않은 채 사용 가능으로 남으며, 관계만 정지된다.
- 준비: `knowledge_graph()`.
- 실행: `withdraw(ins, run, a)`.
- 단언: `a`의 `lifecycle`이 `'withdrawn'`이다. `c` 기록이 원래와 같고 사용 가능하다. `relations[0]`의 `status`가 `'suspended'`다. `unrelated` 과제는 그대로다.
- 대역: 없음.

### `test_withdrawn_record_retires_its_pending_checks` (행 143–149)
- 성질: 철회된 기록을 대상으로 한 형식 검사, 동일성 검토, 검토 보충 조사 대기는 사라지고, 그 밖의 대기는 남는다.
- 준비: `a`를 대상으로 한 대기 행동 넷. 역할은 `formal_check`, `identity_review`, `supplemental_research`(`review_cycle_id='RC-review'`), `maintenance`다.
- 실행: `withdraw(ins, run, a)`.
- 단언: `a`를 대상으로 남은 역할 목록이 `['maintenance']`다.
- 대역: 없음.
- 비고: 제품 규칙은 `knowledge._without_checks`다. 검토 보충 조사 여부는 `execution_profiles.review_research`(역할 `supplemental_research`이고 `review_cycle_id`가 있음)로 가른다.

### `test_basis_hash_covers_exact_family_record` (행 151–158)
- 성질: 기준 해시는 가족 기록의 정확한 내용을 덮는다. 해설 항목 하나가 바뀌면 기준이 `hash_changed`를 보고하고, 그 해설을 쓰는 지식은 사용할 수 없게 된다.
- 준비: `a`, `a`의 해설 `xid`, `task`로 기준을 잡는다(`k.capture_basis`).
- 실행: `k.validate_basis`, 해설 `items[0].text`를 `'changed'`로 바꾼 뒤 다시 `validate_basis`, `k.assess_use(a)`.
- 단언: 처음 기준은 유효하다. 변경 뒤 사유에 `'hash_changed:' + xid`가 있다. `a`는 사용 불가다.
- 대역: 없음.

### `test_source_locators_are_not_missing_record_ids` (행 160–165)
- 성질: 출처 위치 지정자(문자열 경로나 경로 객체)는 없는 기록 ID로 취급되지 않는다. 반면 없는 `KN-` ID에 대한 의존은 미해결 참조로 드러난다.
- 준비: `b.origin_refs`를 `['proposal:1', 'input/knowledge/KN-X.json', {'path': 'catalog.json', 'sha256': '0'}]`로 둔다.
- 실행: `k.plan_impact(ins, run, [b], [])`. 이어 `b.dependencies`에 `'KN-MISSING'`을 더해 다시 부른다.
- 단언: 처음 `unresolved_refs`가 `[]`이고, 둘째에는 `'KN-MISSING'`이 있다.
- 대역: 없음.
- 비고: 제품에서 `origin_refs`는 관대 필드다. 문자열은 `^KN-...$`에 온전히 맞거나 알려진 ID일 때만 참조로 센다. 식별 키가 없는 객체는 관대 필드에서 건너뛴다(`_field_refs`).

### `test_system_propagation_applies_computed_impact_and_names_unresolved_refs` (행 167–175)
- 성질: 시스템이 관측한 실패의 전파(`propagate`)는 계산된 영향을 호출자의 사본에 그대로 적용하고, 기준 밖 참조를 사유에 적는다.
- 준비: `c.used_sources=[a]`, `c.dependencies`에 `'KN-MISSING'`을 더한다.
- 실행: `k.propagate(ins, run, [a], 'trust environment invalidated')`. 반환값 없이 제자리에서 바뀐다.
- 단언: `run['history'][-1]`의 `kind`가 `'knowledge_reassessment_required'`이고, `affected_ids`에 `c`가 있으며, `reason`에 `'KN-MISSING'`이 있다.
- 대역: 없음.
- 비고: 제품 근거는 `propagate`의 주석이다. 시스템 관측 실패에는 선언을 검토받을 생산자가 없으므로 계산된 영향을 늘 적용하고, 기준 밖 참조를 사유에 적는다.

### `test_known_source_propagates_but_locator_does_not` (행 177–182)
- 성질: `used_sources`에 섞인 위치 지정자는 무시되고, 알려진 기록 ID는 영향을 전한다.
- 준비: `c.used_sources=['proposal:1', 'input/knowledge/KN-X.json', a]`.
- 실행: `k.plan_impact(ins, run, [a], [])`.
- 단언: `computed_impact`에 `c`가 있고, `unresolved_refs`에 `'input/knowledge/KN-X.json'`이 없다.
- 대역: 없음.

### `test_source_currentness_and_reassessment_preserve_judgment` (행 184–196)
- 성질: 출처가 바뀌면 지식은 즉시 사용 불가가 된다. 출처 변경에 따른 정지는 봉인 판정을 고치지 않는다. 바이트를 되돌리면 정지하지 않은 상태는 다시 사용 가능해지지만, 정지를 적용한 상태는 계속 사용 불가다.
- 준비: `sources=[{'name': 'paper', 'sha256': 'old', ...}]`를 둔 그래프에 `add_knowledge(source_refs=['paper'])`로 봉인된 기록 `kid`와 판정 `aid`를 더한다. 판정 사본을 떠 둔다.
- 실행: `sha256`을 `'new'`로 바꾸고 `k.suspend_for_source_change(..., source_name='paper', reason='source changed', actor_ref='user')`를 부른 뒤, 두 상태 모두 `'old'`로 되돌린다.
- 단언: 처음 사용 가능, 출처 변경 뒤 사용 불가다. 정지 뒤 판정이 사본과 같다. 되돌린 뒤 원 상태는 사용 가능, 정지 상태는 사용 불가다.
- 대역: 없음.

### `test_partial_failure_keeps_old_environment` (행 198–203)
- 성질: 전환 대상 가운데 하나가 실패하면 활성화가 거부되고 옛 환경이 활성으로 남는다.
- 준비: 모듈 함수 `transition(ins)`로 `TE-new` 전환을 시작하고, `a`에 `{'status': 'failed'}` 결과만 기록한다.
- 실행: `k.activate_transition(ins, tr)`.
- 단언: `ValueError`가 난다(유형만). `active_trust_environment`가 `'TE-old'`다.
- 대역: 없음.
- 비고: 결과가 기록되지 않은 대상도 있어 제품의 "all transition targets must be verified" 조건에 걸린다. 실패 하나만의 효과는 다음 시험이 가른다.

### `test_one_failure_in_complete_multi_target_batch_preserves_every_original_record` (행 205–215)
- 성질: 모든 대상의 결과가 모인 묶음에서도 하나가 실패하면 활성화가 거부되고, 상태는 조금도 바뀌지 않는다.
- 준비: 모든 대상에 새 환경 증거를 기록한 뒤, 둘째 대상의 결과를 `{'status': 'failed'}`로 덮어쓴다. 상태 사본을 떠 둔다.
- 실행: `k.activate_transition(ins, tr)`.
- 단언: `ValueError`를 메시지 `'all transition targets'`로 낸다(`assertRaisesRegex`). 상태가 사본과 같다.
- 대역: 없음.

### `test_unknown_environment_rejected` (행 217–220)
- 성질: 없는 환경으로 전환을 시작하거나 없는 환경을 무효화할 수 없다.
- 준비: `knowledge_graph()`.
- 실행: `k.begin_transition(ins, 'TE-missing')`, `k.invalidate_environment(ins, run, 'TE-missing', 'bad')`.
- 단언: 둘 다 `ValueError`(유형만).
- 대역: 없음.

### `test_complete_transition_preserves_old_evidence_and_changes_links` (행 222–232)
- 성질: 완료된 전환은 새 환경을 활성화하고 옛 환경을 `superseded`로 돌린다. 옛 형식 결과와 판정은 그대로 두고, 기록마다 새 형식 결과로 연결을 바꿔 사용 가능성을 유지한다.
- 준비: `transition(ins)`.
- 실행: 모듈 함수 `finish_transition`.
- 단언: `active_trust_environment`가 `TE-new`이고 `TE-old`의 `status`가 `'superseded'`다. 옛 형식 결과와 판정이 모두 원래와 같다. `a`, `b`, `c`가 사용 가능하고, 각 `formal_result_id`가 옛 값과 다르다.
- 대역: 없음.

### `test_invalidated_environment_recovery_rechecks_all_accepted_results` (행 234–247)
- 성질: 무효화된 환경은 스키마에 맞는 무효 기록으로 남는다. 복구 전환은 수리된 모든 결과를 다시 검사 대상으로 삼고, 다시 검사된 기록을 사용 가능으로 되돌린다. 무효 환경은 무효로 남는다.
- 준비: `k.invalidate_environment(ins, run, 'TE-old', 'kernel defect')`.
- 실행: `jsonschema.validate(TE-old, RECORDS['trust_environments'])`, `transition(stopped)`, `finish_transition`.
- 단언: 무효 기록이 스키마를 통과하고 `invalidated_reason`이 `'kernel defect'`, `active_trust_environment`가 `None`이다. 전환 대상 ID가 `{a, b, c}`이고 모두 `previous_environment_ids == ['TE-old']`다. 복구 뒤 `TE-old`의 `status`는 `'invalid'`이고 `a`, `b`, `c`가 사용 가능하다.
- 대역: 없음.
- 비고: 사용 가능성 회복은 무효화 때 사용 기록에 남긴 `environment_revalidation`을 `activate_transition`이 복구 가능으로 인정하기 때문이다.

### `test_recovery_does_not_promote_unchecked_or_withdrawn` (행 249–259)
- 성질: 복구 전환은 검사받지 않은 후보와 철회된 기록을 대상으로 삼지 않고, 사용 가능으로 올리지도 않는다.
- 준비: 봉인하지 않은 후보 `pending`을 더하고, `c`를 철회하고, `TE-old`를 무효화한다.
- 실행: `transition`, `finish_transition`.
- 단언: 대상에 `pending`과 `c`가 없다. 복구 뒤 `pending`은 사용 불가, `c`의 `lifecycle`은 `'withdrawn'`이다.
- 대역: 없음.

### `test_recovery_preserves_later_semantic_suspension` (행 261–268)
- 성질: 환경 무효화 뒤에 따로 내려진 의미 정지는 환경 복구로 풀리지 않는다.
- 준비: `TE-old` 무효화 뒤 `aa`의 사용을 `'meaning challenged'`로 정지한다. `set_assessment_use`는 `environment_revalidation` 표지를 지운다.
- 실행: `transition`, `finish_transition`.
- 단언: `a`는 사용 불가, `c`는 사용 가능하다.
- 대역: 없음.

### `test_environment_recovery_cannot_clear_a_later_source_reassessment` (행 270–282)
- 성질: 환경 복구는 그 뒤에 생긴 출처 재평가 의무를 지우지 못한다. 출처 바이트를 되돌려도 마찬가지다.
- 준비: 출처 `paper`를 가진 봉인 기록 `kid`를 더한다. `TE-old`를 무효화한 뒤 출처를 `'new'`로 바꾸고 `suspend_for_source_change`를 적용한다. 그 뒤 출처를 `'old'`로 되돌린다.
- 실행: `transition`, `finish_transition`.
- 단언: `kid`가 사용 불가다.
- 대역: 없음.
- 비고: 원문 주석은 "Restoring bytes resolves currentness, not the separate review obligation."이다.

### `test_recovery_preserves_dependency_on_withdrawn_knowledge` (행 284–291)
- 성질: 복구 전환 뒤에도 철회된 기록에 의존하는 기록은 사용할 수 없다.
- 준비: `a`를 철회한 뒤 `TE-old`를 무효화한다.
- 실행: `transition`, `finish_transition`.
- 단언: `b`가 사용 불가이고 `a`의 `lifecycle`이 `'withdrawn'`이다.
- 대역: 없음.

### `test_history_is_not_a_current_dependency` (행 293–297)
- 성질: 이력에 남은 옛 의존은 현재 의존이 아니므로 영향이 전파되지 않는다.
- 준비: `b.history=[{'previous': {'dependencies': [c]}}]`.
- 실행: 픽스처 `revise_knowledge(ins, run, c)`.
- 단언: `b`가 사용 가능하다.
- 대역: 없음.
- 비고: 제품은 `_HISTORY_KEYS`의 키를 참조 수집에서 건너뛴다.

### `test_fresh_plan_is_applied_without_recomputing_the_closure` (행 299–305)
- 성질: 방금 계산한 계획을 적용할 때 닫힘을 다시 계산하지 않는다.
- 준비: `knowledge_graph()`.
- 실행: `patch.object(k, 'plan_impact', wraps=k.plan_impact)` 아래에서 `withdraw(ins, run, a)`.
- 단언: `plan_impact` 호출이 정확히 2회다. 주석은 이를 "생산자 선언 하나(`impact_declaration`)와 `invalidate_knowledge` 안의 계획 하나"로 설명한다. `a`의 `lifecycle`이 `'withdrawn'`이다.
- 대역: `do_math.knowledge.plan_impact`를 감싼 대역(`wraps`). 호출 수만 세고 동작은 원래대로다.

### `test_observed_propagation_plans_twice_and_applies_to_the_callers_copy` (행 307–314)
- 성질: 관측 전파는 미리보기와 계획으로 두 번만 계산하고, 적용 때 다시 계산하지 않으며, 호출자가 넘긴 원래 런타임은 바꾸지 않는다.
- 준비: `knowledge_graph()`.
- 실행: 같은 `wraps` 대역 아래에서 `k.invalidate_environment(ins, run, 'TE-old', 'environment defect')`.
- 단언: 호출이 2회다. 반환 런타임의 마지막 이력 `kind`가 `'knowledge_reassessment_required'`다. 원래 `run['history']`에는 그 종류가 없다.
- 대역: `plan_impact`의 `wraps` 대역.

### `test_research_reuse_keeps_dependency_and_source_currentness` (행 316–328)
- 성질: 연구 수준 재사용(`assess_research_use`)도 의존 기록의 출처 현재성을 따라간다.
- 준비: 출처 `data`(`sha256='a'*64`)와 활성 종류 `KD`를 둔 상태에 `create_candidate`를 직접 불러 `KN-parent`(출처 기준 `data`)와 그에 의존하는 `KN-child`를 만든다.
- 실행: `assess_research_use(child)`. 이어 출처 해시를 `'b'*64`로 바꾸고 다시 부른다.
- 단언: 처음 유효, 변경 뒤 무효다.
- 대역: 없음.
- 비고: `import_candidate`의 검사를 거치지 않고 `create_candidate`로 저장 모양만 만든다.

### `test_knowledge_input_exposes_exact_formal_and_identity_records` (행 330–336)
- 성질: 지식 입력의 독자 보기(`reader_view`)는 기록의 정확한 형식 결과, 판정, 판정 사용을 함께 싣는다.
- 준비: `verified_knowledge()`.
- 실행: `reader_view(instance, kid)`.
- 단언: `view['formal_result']['id'] == view['formal_result_id']`, `identity_assessments[0]['id'] == aid`, `assessment_uses[0]['assessment_id'] == aid`.
- 대역: 없음.

## KnowledgeRecordTests (행 339–718)

`unittest.TestCase`를 상속한다. 클래스 표지, 클래스 속성, 설정·정리 훅, 도우미 메서드가 없다. 표지는 첫 시험 메서드에만 붙는다. 많은 시험이 `verified_knowledge()`에서 시작한다. 이 상태에는 후보 "Truth"(`theorem truth : True := True.intro`)가 있고, 활성 환경 `TE-test`(`toolchain={'version': 'test-fixture'}`)에서 합성 검증을 받았으며, `policy:1`의 `match` 판정(`review_cycle_id='RC-fixture'`)이 봉인되어 있다.

### `test_installed_lean_extracts_transitive_constants` (행 341–353)
- 성질: 설치된 Lean으로 검증하면 선언의 의존 닫힘에 간접 상수까지 들어가고, 선언 증거가 남는다.
- 준비: 명령은 환경변수 `DO_MATH_KNOWLEDGE_TEST_LEAN`이 있으면 그 값을, 없으면 `portable_bin(toolchain_root()) / "lean.exe"`를 쓴다. 파일이 없으면 `skipTest("installed Lean is unavailable")`. 소스는 `base`, `base`를 쓰는 `mid`, `mid = base`를 증명하는 `leaf` 세 선언이다.
- 실행: 임시 폴더를 작업 공간으로 `verify_lean(source=..., declarations=['leaf'], workspace=..., lean_command=command)`. 주석은 "실제 로컬 Job 전송을 통해 설치 컴파일러를 쓴다"고 밝힌다.
- 단언: `status`가 `'verified'`다(실패 메시지로 결과 전체를 붙인다). `dependency_closure`가 있고 `leaf`의 닫힘에 `base`와 `mid`가 모두 있다. `declaration_evidence`에 `leaf`가 있다.
- 대역: 없음.
- 비고: `@category('lean')`이므로 `run_tests.py`가 Windows Job 격리 프로세스에서 돌린다. 실제 Lean 자식 프로세스를 쓴다. 설치 Lean이 없으면 건너뛴다.

### `test_import_separates_formal_and_exposition_authority` (행 355–361)
- 성질: 가져온 지식 기록은 Lean 원문과 형식 증거를 직접 담지 않고, 별도 형식 결과와 해설 기록을 ID로 가리킨다.
- 준비: 빈 상태.
- 실행: `knowledge_io.import_candidate({}, {}, knowledge_candidate(), ...)`.
- 단언: 기록에 `lean_code`와 `formal`이 없다. `formal_result_id`가 `formal_results`에, `exposition_id`가 `expositions`에 있다.
- 대역: 없음.

### `test_installed_relation_kinds_are_active_from_installation` (행 363–372)
- 성질: 설치 관계 종류는 설치 순간부터 활성이고 설치 표지(`builtin`)를 가지며, 같은 토큰을 다시 정의할 수 없다.
- 준비: `knowledge_io.ensure_ontology({})`.
- 실행: `catalog_definitions(state)['relations']`, 그리고 `supports` 정의의 네 필드로 `register_kind_definition`.
- 단언: 카탈로그 토큰 집합이 `BUILTIN_DEFINITIONS`의 관계 토큰 집합과 같다. 모두 `status='active'`이고 `builtin`이 참이다. 재등록은 `ValueError`를 메시지 `"already defined"`로 낸다.
- 대역: 없음.

### `test_kind_registration_requires_explicit_check_and_activation` (행 374–378)
- 성질: 새 종류를 등록하면 `candidate` 상태로 시작한다.
- 준비: 정의 `bounded_result`(`constraints={}`).
- 실행: `register_kind_definition`.
- 단언: 저장된 정의의 `status`가 `'candidate'`다.
- 대역: 없음.
- 비고: 이름은 "검사와 활성화를 요구한다"고 말하지만 단언은 등록 직후 상태만 본다. 검사 전 활성화 거부는 `test_kind_constraints_and_withdrawal`과 `test_knowledge_io.test_unknown_kind_requires_candidate_check_and_activation`이 본다.

### `test_kind_definitions_use_record_ids_and_allow_explicit_replacement` (행 380–388)
- 성질: 종류 정의는 레코드 ID를 키로 저장된다. 철회된 설치 종류는 새 정의로 명시적으로 대체할 수 있고, 대체 정의는 옛 정의를 가리킨다.
- 준비: `ensure_ontology({})`.
- 실행: `withdraw_kind_definition(state, {}, 'knowledge', 'theorem', ...)`, 이어 같은 토큰으로 `register_kind_definition`.
- 단언: 모든 사전 키가 값의 `id`와 같다. 새 `candidate` 정의의 `supersedes`가 `kind_definitions`에 있는 ID다.
- 대역: 없음.

### `test_impact_planning_does_not_mutate_and_includes_relations` (행 390–396)
- 성질: 영향 계획은 입력을 바꾸지 않고, 관계 기록도 영향에 넣는다.
- 준비: 수작업 상태. `KN-a` 하나와 자기 자신을 잇는 관계 `RL-a`.
- 실행: `knowledge.plan_impact(state, {}, ['KN-a'], ['RL-a'])`.
- 단언: 상태가 사본과 같고, `computed_impact`에 `RL-a`가 있다.
- 대역: 없음.

### `test_explanation_revision_preserves_formal_evidence_and_old_judgment` (행 398–413)
- 성질: 설명 개정은 형식 결과와 옛 판정을 그대로 두고, 옛 판정의 사용과 옛 해설만 물린다. 대체 기록은 새 판정 전까지 사용할 수 없다.
- 준비: `verified_knowledge()`. 선언 영향은 판정 `aid`와 그 사용 기록 ID다.
- 실행: `knowledge.revise_knowledge(state, runtime, kid, {'summary': 'Revised summary'}, reason='clarify', actor_ref='author', declared_impact=declared)`.
- 단언: `formal_results`가 사본과 같다. 판정 `aid`가 원래와 같다. 옛 기록은 `superseded`이고 대체 기록은 정확히 하나이며 사용 불가다. 옛 판정의 사용 `status`가 `'suspended'`다. 옛 해설의 `lifecycle`이 `'superseded'`다.
- 대역: 없음.

### `test_decision_reference_reports_actual_split_environment` (행 415–417)
- 성질: 결정 참조는 분리된 형식 결과가 가진 실제 신뢰 환경 ID를 보고한다.
- 준비: `verified_knowledge()`.
- 실행: `knowledge.decision_reference(record, state)`.
- 단언: `trust_environment_id`가 `'TE-test'`다.
- 대역: 없음.

### `test_revision_reuses_candidate_kind_and_dependency_validation` (행 419–424)
- 성질: 개정도 후보 가져오기의 종류 검사와 의존 검사를 그대로 거친다.
- 준비: `verified_knowledge()`와 판정·사용 선언.
- 실행: `{'kind': 'unregistered_kind'}`와 `{'dependencies': ['KN-missing']}` 각각으로 `knowledge.revise_knowledge`.
- 단언: 둘 다 `ValueError`(유형만).
- 대역: 없음.
- 비고: `subTest(changes=...)` 두 개.

### `test_revision_changes_name_only_authored_fields` (행 426–434)
- 성질: 개정 변경은 저작 필드만 이름 댈 수 있다.
- 준비: `knowledge.AUTHORED_FIELDS` 전체, 그리고 저작 필드가 아닌 `id`, `status`, `formal`, `verified_at`, `identity_assessment`, `producer_execution_ids`, `unknown_field`.
- 실행: 필드마다 `knowledge.validate_changes({field: 'value'})`.
- 단언: 저작 필드는 예외가 없고, 나머지는 `ValueError`(유형만)를 낸다.
- 대역: 없음.
- 비고: 저작 필드마다 하나, 비저작 필드마다 하나씩 `subTest`를 둔다. 원문 주석은 "The producer check and the application share this one rule."이다.

### `test_common_execution_names_exactly_the_authored_fields` (행 436–442)
- 성질: 역할 문서 「공통 실행」이 개정 작성자에게 주는 필드 목록은 `validate_changes`가 받는 닫힌 집합과 정확히 같다.
- 준비: 스킬의 `references/공통-실행.md` 전문.
- 실행: 정규식 ``r'`changes`의 키는 저작 필드 (.+?) 가운데서만 고른다'``로 문장을 찾고, 그 안의 역따옴표 이름을 뽑는다.
- 단언: 문장이 있고(`assertIsNotNone`), 뽑은 이름 집합이 `knowledge.AUTHORED_FIELDS`와 같다.
- 대역: 없음.
- 비고: 문서와 코드의 대조 시험이다. 해당 문장은 `references/공통-실행.md` 356행에 있고, 그 문장은 "이 목록의 정본은 `knowledge.AUTHORED_FIELDS`다"라고 이어진다.

### `test_import_captures_required_source_and_rejects_unknown_source` (행 444–449)
- 성질: 가져오기는 없는 출처 참조를 거부하고, 있는 출처의 해시를 기록의 출처 기준으로 잡는다.
- 준비: `sources=[{'name': 'paper', ..., 'sha256': 'original'}]`.
- 실행: `source_refs=['absent']`, 그리고 `['paper']`로 `import_candidate`.
- 단언: 첫째는 `ValueError`다(유형만. 제품 메시지 `"required source does not exist"`). 둘째 기록의 `source_basis[0].sha256`이 `'original'`이다.
- 대역: 없음.

### `test_assessment_suspension_is_local_and_reversible` (행 451–459)
- 성질: 판정 사용의 정지는 판정 기록을 바꾸지 않고 그 지식만 사용 불가로 만들며, 형식 결과의 유효성에는 영향이 없고, 다시 활성으로 되돌릴 수 있다.
- 준비: `verified_knowledge()`와 판정 가족 사본.
- 실행: `kr.set_assessment_use(state, aid, 'suspended', 'review defect', 'reviewer')`, 이어 `'active'`로 복원.
- 단언: 정지 뒤 판정 가족이 사본과 같다. 지식은 사용 불가지만 `kr.knowledge_view(suspended)[0]['formal_valid']`는 참이다. 복원 뒤 다시 사용 가능하다.
- 대역: 없음.

### `test_independent_expositions_share_one_formal_result` (행 461–473)
- 성질: 독립된 두 해설은 한 형식 결과를 공유할 수 있다. 각 해설의 판정 사용은 서로 독립이다.
- 준비: `verified_knowledge()`. 둘째 후보는 `formal_result_ref=fid`와 다른 `explanation`을 가진다.
- 실행: `import_candidate`(`actor_ref='other-author'`), 둘째 기록의 `match` 판정 봉인, 첫 판정 사용 정지.
- 단언: `formal_results`가 하나뿐이다. 가져온 뒤 대기 마지막 역할이 `'identity_review'`다. 형식 결과를 재사용하므로 형식 검사를 건너뛴다. 정지 뒤 첫 기록은 사용 불가, 둘째 기록은 사용 가능하다.
- 대역: 없음.

### `test_mathematical_relation_consumes_separate_result_and_assessment` (행 475–485)
- 성질: 수학 관계는 분리된 형식 결과와 판정을 소비하며, 판정 사용이 정지되면 관계가 무효가 된다.
- 준비: `verified_knowledge()`의 형식 결과와 판정에 관계 주장 `formally_implies(kid→kid, 'reflexive implication')`를 직접 써 넣는다.
- 실행: 관계 `{**claim, formal_result_refs: [fid], assessment_refs: [aid], evidence_refs: [kid]}`로 `validate_relation`, 판정 사용 정지 뒤 다시 부른다.
- 단언: 처음 유효, 정지 뒤 무효다.
- 대역: 없음.
- 비고: 관계 주장을 가져오기 경로가 아니라 기록에 직접 써서 만든다. 가져오기 경로를 통한 결속은 다음 시험이 본다.

### `test_relation_claim_is_bound_through_import_and_identity` (행 487–500)
- 성질: 관계 주장은 가져오기와 동일성 판정을 거쳐 결속된다. 끝점 기록이 바뀌면 관계가 무효가 된다.
- 준비: `verified_knowledge()`. 관계 주장 `formally_implies(kid→kid, 'reflexive')`를 가진 후보를 가져와 `proof`로 둔다. `kid`의 검증 내용을 복사해 `proof`의 형식 결과로 기록한다(원문이 같으므로 통과). `match` 판정을 봉인한다.
- 실행: 관계 검증, `kid`의 `title`을 `'changed endpoint'`로 바꾼 뒤 재검증.
- 단언: 처음 유효, 변경 뒤 무효다.
- 대역: 없음.

### `test_trust_transition_uses_split_results_and_compares_evidence` (행 502–519)
- 성질: 신뢰 전환은 분리된 형식 결과에서 대상을 만들고 커널 증거를 싣는다. 증거가 같으면 옛 판정을 보존한 채 활성화한다. 의존 본문 증거가 달라지면 동일성 검토 없이는 활성화할 수 없다.
- 준비: `verified_knowledge()`에 `TE-next`(`registered`, `toolchain={'version': 'next'}`)를 더한다.
- 실행: `begin_transition`, 기존 검증 내용에 `id=kid`, `toolchain={'version': 'next'}`만 바꾼 결과로 `record_transition_result`와 `activate_transition`. 이어 결과의 `dependency_evidence['True']`를 `exact_content_hash('changed-type')`로 바꿔 새 전환으로 반복한다.
- 단언: 대상이 1개이고 `dependency_closure`와 `axioms`를 가진다. 활성화 뒤 활성 환경이 `TE-next`이고 `kid`가 사용 가능하며, 판정 `aid`가 원래와 같다. 증거를 바꾼 둘째 활성화는 `ValueError`다(유형만).
- 대역: 없음.
- 비고: 둘째 거부는 제품에서 `compare_formal_results`가 `changed`를 보고해 `requires_identity_review`가 참이 되는데, `runtime`이 없어 "transition requires its sealed staged identity review runtime"으로 막히는 경로다. 시험은 메시지를 고정하지 않는다.

### `test_identity_review_cannot_replace_missing_new_kernel_evidence` (행 521–531)
- 성질: 새 커널 증거가 빠진 전환 결과는 동일성 검토 영수증을 붙여도 활성화할 수 없다.
- 준비: `TE-next` 전환. 결과에서 `dependency_closure`를 빼고 `identity_review={'decision': 'match', ...}`를 붙인다.
- 실행: `record_transition_result`, `activate_transition`.
- 단언: `ValueError`(유형만).
- 대역: 없음.
- 비고: 제품에서는 `validate_formal_evidence`가 `"verification evidence incomplete: dependency_closure"`로 먼저 막는다. 동일성 검토 확인보다 앞선 단계다.

### `test_rejects_unapproved_environment_and_replayed_identity_basis` (행 533–541)
- 성질: 현재 기준과 다른 기준(재생된 옛 기준)의 판정은 봉인되지 않는다. 활성이 아닌 환경에서는 형식 결과를 기록할 수 없다.
- 준비: `verified_knowledge()`. 판정 기준 `{'formal': 'old', 'exposition': 'old'}`.
- 실행: `kr.record_identity_assessment`. 이어 `TE-test`의 `status`를 `'registered'`로 바꾸고 기존 검증 내용으로 `kr.record_formal_result`.
- 단언: 둘 다 `ValueError`(유형만).
- 대역: 없음.

### `test_storage_registration_roundtrip_uses_split_family_files` (행 543–598)
- 성질: 실제 신뢰 환경 등록 자료와 실제 검토 주기에서 나온 판정을 가진 분리 가족 상태가 실제 Git 저장소에 저장되었다가 그대로 읽혀 나오고, 읽은 상태에서도 지식이 사용 가능하다.
- 준비: 임시 폴더에 `trust_fixture(Path(directory), ['synthetic-lean'])`로 합성 설치와 도구 모음 기록을 만들고, `trust_environment(..., environment_id='TE-test', source_ref='synthetic:approval')`로 환경과 바인딩을 만든다. `environment_errors`가 `[]`이고 `check_environment`의 `status`가 `'verified'`인지 먼저 확인한다. `verified_knowledge(environment, binding=binding, identity=False)`로 판정 없는 검증 기록을 만든다. `build_profiles(DEFAULT_CONFIG)`의 `identity_review` 프로필과 용량 제약을 넣고 활동을 연다. `scoped_start(proposal_view + revision 1, reviewers=2)`로 검토 주기를 시작한다. 두 번 반복하며 `next_actions`로 행동을 얻고 `match` 출력을 `accept_result`로 넣는다. 매번 실행 기록을 만들어 `starting` → `running` → 제출 영수증 → `stopping` → `ended(output_accepted)`로 옮긴다. 주기가 `completed`가 되면 ID, 지식 ID, 동일성 기준, 정책을 붙인다. `identity_assessment(cycle, ...)`로 판정을 만들어 봉인한다. 끝으로 `git_init(directory)`, `current_state(state, runtime)`로 수명 규칙을 맞춘다.
- 실행: `ResearchRepository(Path(directory), new_id('RI'), contract=default_state_contract())`의 `initialize(state, runtime)`와 `load()`.
- 단언: 준비 중 세 점검(`environment_errors == []`, `check_environment(...)['status'] == 'verified'`, 주기 `status == 'completed'`)을 확인한다. 읽은 `formal_results`와 `identity_assessments`가 저장 전과 같고, 읽은 상태에서 `kid`가 사용 가능하다.
- 대역: 컴파일러·검토자·승인 증거는 합성이다(원문 주석 "Real Git and domain validators; compiler/reviewer/approval evidence is synthetic."). `mock` 대역은 없다.
- 비고: 실제 Git 자식 프로세스를 쓴다. `ResearchRepository`의 `GitStateStore`가 `subprocess.run`으로 `git`을 부른다. 시작 상태 단으로는 1단 도메인 준비 위에 실제 Git 저장소를 얹은 것이다.

### `test_import_rejects_malformed_registry_id` (행 600–602)
- 성질: 정규 `KN-` ULID가 아닌 지식 ID는 거부된다.
- 준비: `knowledge_candidate(id='KN-not-a-ulid')`.
- 실행: `import_candidate`.
- 단언: `ValueError`(유형만. 제품 메시지 `"knowledge ID must be a canonical KN-prefixed ULID"`).
- 대역: 없음.

### `test_formal_verification_requires_dependency_body_evidence` (행 604–611)
- 성질: 의존 본문 증거(`dependency_evidence`)가 없는 검증은 기록되지 않는다.
- 준비: 새로 가져온 후보. `verified_knowledge()`에서 신뢰 환경과 검증 내용을 빌려 오고, 검증에서 `dependency_evidence`를 뺀다.
- 실행: `kr.record_formal_result(state, kid, verification, 'TE-test', runtime=runtime)`.
- 단언: `ValueError`(유형만. 제품 메시지 `"dependency body evidence differs from the closure"`).
- 대역: 없음.

### `test_dependency_body_evidence_is_one_hash_table_over_the_declared_closures` (행 613–626)
- 성질: 의존 본문 증거는 선언한 닫힘의 상수마다 SHA-256 하나를 둔 평평한 표다. 선언별로 중첩되거나, 빠진 상수가 있거나, 해시 모양이 아닌 값이 있으면 거부된다.
- 준비: 앞 시험과 같다. `truth`의 닫힘에 속한 상수마다 `exact_content_hash(name)`를 둔 표를 만든다.
- 실행: 올바른 표로 `record_formal_result`. 이어 잘못된 표 셋으로 반복한다. 셋은 `{'truth': table}`(중첩), 마지막 상수를 뺀 표, 첫 상수를 `'not-a-hash'`로 바꾼 표다.
- 단언: 받은 형식 결과의 `verification.dependency_evidence`가 표와 같다. 잘못된 셋은 모두 `ValueError`(유형만).
- 대역: 없음.
- 비고: `subTest(invalid=...)` 세 개.

### `test_transition_targets_store_the_dependency_hash_table` (행 628–638)
- 성질: 전환 대상은 의존 본문 증거를 평평한 해시표로 저장하고, 저장 계약의 런타임 `trust_transitions` 검사기가 중첩 형태를 거부한다.
- 준비: `verified_knowledge()`에 `TE-next`를 더하고 `begin_transition`.
- 실행: `default_state_contract().family('runtime', 'trust_transitions').checker`로 `validate_record(checker, transition, 'transition')`. 이어 첫 대상의 표를 `{'truth': 표}`로 중첩한 사본으로 반복한다.
- 단언: 원래 전환은 통과하고, 중첩 사본은 `ValueError`(유형만).
- 대역: 없음.

### `test_changed_approved_toolchain_rejects_before_source_execution` (행 640–661)
- 성질: 승인 뒤 실행 파일 바이트가 바뀌면 소스를 실행하기 전에 거부한다.
- 준비: 승인 도구 모음 사전의 기본값은 `sys.executable`과 그 해시, `formal.py`의 해시와 경로다. 임시 폴더에 `lean.exe`를 `b"approved executable bytes"`로 쓰고, 그 경로와 해시로 `executable`, `sha256`, `configured_command`, `executables`를 갱신한다. 그 뒤 파일을 `b"changed executable bytes"`로 덮어쓴다.
- 실행: `do_math.formal._job_run` 대역 아래에서 `verify_lean(source=knowledge_candidate()['lean_code'], declarations=['truth'], ..., lean_command=command, expected_toolchain=approved)`.
- 단언: `status`가 `'rejected'`, `reason`이 `'approved toolchain changed before execution'`이다. `_job_run`이 불리지 않는다(`assert_not_called`).
- 대역: `do_math.formal._job_run`을 `side_effect=AssertionError('changed executable must not start')`로 패치한다.
- 비고: `lean` 표지가 없다. 실제 Lean을 부르지 않고, 실제 파일 해시 비교만 한다.

### `test_publication_reads_runtime_transition_barrier` (행 663–670)
- 성질: 신뢰 전환이 검사 중이면 형식 결과 기록과 `match` 판정 봉인이 모두 기다린다.
- 준비: `verified_knowledge()`의 런타임에 `trust_transitions={'TR-test': {'status': 'checking'}}`.
- 실행: `kr.record_formal_result`, `kr.record_identity_assessment(... 'match' ...)`.
- 단언: 둘 다 `ValueError`(유형만). 제품 메시지는 각각 `"formal publication waits for the trust transition"`, `"identity publication waits for the trust transition"`이다.
- 대역: 없음.

### `test_impact_mismatch_and_staleness_reject_without_mutation` (행 672–685)
- 성질: 계산된 닫힘을 넘는 선언은 독립 확인 없이 적용되지 않고 상태를 바꾸지 않는다. 계산 뒤 상태가 바뀐 낡은 계획도 적용되지 않는다.
- 준비: 수작업 상태. `KN-a`, `KN-b`, 자기 관계 `RL-a`.
- 실행: 선언 `['RL-a', 'KN-b']`로 계획해 `apply_impact`. 이어 선언 `['RL-a']`로 계획한 뒤 관계 `target`을 `'KN-changed'`로 바꾸고 `apply_impact`.
- 단언: 둘 다 `ValueError`(유형만). 첫 경우 뒤 상태가 사본과 같다.
- 대역: 없음.
- 비고: 원문 주석은 "A declared record beyond the computed closure needs an independent confirmation."이다. 제품 메시지는 각각 `"impact requires independent scope and disposition confirmation"`, `"impact plan is stale or altered"`다.

### `test_impact_tracks_origin_refs_and_missing_split_refs` (행 687–692)
- 성질: 영향은 `origin_refs`의 알려진 ID를 따라가고, 엄격 필드의 없는 분리 기록 참조를 미해결로 보고한다.
- 준비: `KN-b`가 `origin_refs=['KN-a']`, `formal_result_refs=['FR-missing']`를 가진다.
- 실행: `plan_impact(state, {}, ['KN-a'], ['KN-b'])`.
- 단언: `computed_impact`에 `KN-b`, `unresolved_refs`에 `FR-missing`이 있다.
- 대역: 없음.

### `test_impact_preserves_terminal_task_and_suspends_its_judgment` (행 694–702)
- 성질: 영향 적용은 완료 과제의 상태를 보존하고 그 판정과 목표 판정의 현재성만 거둔다.
- 준비: `KN-a`, 그것을 쓰는 목표 판정 `GJ-a`, 입력 `KN-a`인 완료 과제 `TK-a`(`assessment.current=True`).
- 실행: 선언 `['TK-a', 'GJ-a']`로 `plan_impact`를 만들고 `apply_impact(..., reason='premise changed')`.
- 단언: `TK-a.status`가 `'completed'`, `assessment.current`가 거짓, `goal_judgments[0].current`가 거짓이다.
- 대역: 없음.

### `test_kind_constraints_and_withdrawal` (행 704–718)
- 성질: 종류 정의의 제약(허용 인식 상태, 필수 필드)은 가져오기에 적용된다. 검사 전 활성화는 거부된다. 종류를 철회하면 그 종류를 쓰는 기록이 종류 사용 정지 표지를 받는다.
- 준비: `bounded_result` 정의. 제약은 `allowed_epistemic_statuses=['tentative']`, `required_fields=['confirmed_scope']`다.
- 실행: 등록, 검사 전 `activate_kind_definition`, 검사와 활성화를 거친다. 그 뒤 제약을 채우지 않은 후보, `epistemic_status='tentative'`와 `confirmed_scope='finite case'`를 채운 후보를 차례로 가져온다. 마지막으로 `withdraw_kind_definition`.
- 단언: 검사 전 활성화와 제약 미충족 가져오기는 `ValueError`(유형만)다. 제약을 채운 가져오기는 통과한다. 철회 뒤 기록의 `kind_use_suspended`가 참이다.
- 대역: 없음.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈:
  - `test_knowledge_io`는 가져오기, 종류 수명, 관계 검증의 계약을 같은 1단 도메인 층에서 본다. 종류 등록과 활성화 순서, 개정의 새 ID와 형식 재사용은 두 모듈이 모두 다룬다(`test_kind_constraints_and_withdrawal`, `test_unknown_kind_requires_candidate_check_and_activation` 등).
  - `test_knowledge_storage`와 `test_reassessment`는 같은 도메인 함수를 실제 Git 왕복(`KnowledgeRoundtripHarness`)으로 본다.
  - `test_knowledge_import_engine`은 엔진의 형식 경계(`FormalBoundaryTests`, `PortableFormalBoundaryTests`)에서 `record_formal_result`와 전환 장벽이 실행 흐름에 어떻게 이어지는지 본다.
  - `test_family_records`는 `formal_results`, `identity_assessments`, `trust_transitions` 등 가족 파일의 저장 계약을 본다.
- 픽스처 의존: `knowledge_fixtures`의 여덟 기호와 `research_fixtures`의 `git_init`, `trust_environment`, `trust_fixture`, `current_state`, 그리고 `review_fixtures.scoped_start`. `consumers.json`에 따르면 `verified_knowledge`는 이 모듈을 포함한 시험 모듈 5개(`test_context_store`, `test_knowledge`, `test_planning`, `test_role_input`, `test_state_checks`)와 픽스처 모듈 2개(`record_fixtures`, `review_fixtures`)가 쓰고, `seal_knowledge`는 이 모듈만 쓴다.
- 이 모듈에만 있는 도우미: 모듈 함수 `withdraw`, `transition`, `finish_transition`.
- 실제 외부 자원: 설치 Lean(`test_installed_lean_extracts_transitive_constants`, 격리 `lean`), Git 자식 프로세스(`test_storage_registration_roundtrip_uses_split_family_files`), 문서 파일 읽기(`test_common_execution_names_exactly_the_authored_fields`).

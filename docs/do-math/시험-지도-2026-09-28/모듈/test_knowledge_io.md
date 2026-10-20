# test_knowledge_io

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_knowledge_io.py` (201행) |
| 클래스 / 테스트 | 1 / 12 |
| 시험 대상 제품 코드 | `do_math/knowledge_io.py`의 `import_candidate`, `register_kind_definition`, `check_kind_definition`, `activate_kind_definition`, `withdraw_kind_definition`, `catalog_definitions`, `validate_relation`, `import_relation`, `BUILTIN_DEFINITIONS`; `do_math/knowledge_records.py`의 `usable_links`, `proposal_view`, `record_formal_result`, `record_identity_assessment`, `identity_basis`; `do_math/knowledge.py`의 `capture_basis`, `validate_basis`, `assess_use`, 그리고 픽스처를 거친 `revise_knowledge`; `do_math/state_contract.py`의 `default_state_contract` |
| 사용하는 픽스처 모듈 | `knowledge_fixtures`: `add_knowledge`, `knowledge_candidate`, `knowledge_graph`, `revise_knowledge`, `formal_evidence`(함수 안 import). `research_fixtures`: `current_state`(함수 안 import) |
| 격리 표지 | 없음 |
| 시작 상태 | 1단(순수 도메인 함수 직접 호출). 빈 사전이나 `knowledge_fixtures.knowledge_graph()`의 메모리 상태에서 시작한다. 저장소·엔진·프로세스는 쓰지 않는다 |

## 목적

모듈 docstring은 "v5 권위 가족을 쓰는 저작 가져오기와 온톨로지 계약"을 다룬다고 밝힌다. 여기서 "권위 가족"은 지식 하나를 나눠 담는 다섯 가족이다. 곧 `knowledge`, `formal_results`, `expositions`, `identity_assessments`, `assessment_uses`이며, 정의는 `knowledge_records.FAMILIES`에 있다. 시험 대상은 다음 네 계약이다.

1. 후보 가져오기(`import_candidate`, `knowledge_io.py` 240–320행). 가져온 후보는 사용할 수 없는 상태로 시작하고 형식 검사를 대기열에 넣는다. 같은 ID로 다시 가져올 수 없다. 의존은 실재해야 한다. 저작 출처(`origin_refs`)와 생산 실행(`producer_execution`)을 구별한다. `uncertainty_assessment`의 형식은 저장 스키마와 같다.
2. 종류 정의의 수명 주기. 새 종류 토큰은 `candidate` → `checked` → `active` 순서를 거쳐야 쓸 수 있다(`register_kind_definition`·`check_kind_definition`·`activate_kind_definition`, 111–170행). 설치 종류(`BUILTIN_DEFINITIONS`, 35–70행)는 처음부터 `active`다. 카탈로그는 `active` 정의만 보인다(`catalog_definitions`, 103–108행).
3. 관계 검증(`validate_relation`, 328–378행). 연구 관계(`supports`, `analogous_to` 등)와 수학 관계(`formally_implies` 등, `mathematical_claim=True`)를 구별한다. 수학 관계는 같은 관계 주장을 확정하는 `match` 판정과 사용 가능한 형식 결과를 요구한다.
4. 관계 가져오기(`import_relation`, 381–406행). 같은 ID로 다시 가져오면 개정 번호를 올리고 이전 판을 `history`에 남긴다.

## 모듈 수준 요소

- 행 2–6: import. 경로 머리(`sys.path` 조작)가 없으므로 `run_tests.py`나 `unittest discover -s scripts/tests`처럼 `scripts/`와 `tests/`가 이미 경로에 있을 때만 import된다.
- 행 201: 직접 실행하면 `unittest.main(verbosity=2)`.

## KnowledgeIoTests (행 9–198)

`unittest.TestCase`를 상속한다. 표지, 클래스 속성, 설정·정리 훅, 도우미가 없다. 여러 시험이 `knowledge_graph()`에서 시작한다. 이 상태에는 봉인된 기록 `a`, `b`(`a`에 의존), `c`와 관계 `a→c`, `b`를 쓰는 현재 목표 판정, `b`와 `c`를 입력으로 쓰는 완료 과제가 있다. 신뢰 환경 `TE-old`가 활성이다. 합성 형식 증거(`formal_result`)는 Lean 실행이 아닌 대역이다.

### `test_uncertainty_metadata_matches_storage_types_at_import` (행 10–21)
- 성질: `uncertainty_assessment`는 가져올 때 저장 스키마와 같은 형식, 곧 문자열이나 객체만 받는다.
- 준비: 빈 상태. 받을 값은 `'Not a proof'`와 `{'claim': 'Not a proof', 'scope': 'finite search only'}`이고, 거부할 값은 `None`, `[]`, `7`, `False`다.
- 실행: 값마다 `io.import_candidate({}, {}, knowledge_candidate(uncertainty_assessment=value), source_ref='s', actor_ref='u')`.
- 단언: 받는 값은 기록의 `uncertainty_assessment`에 그대로 저장되고, 설치 저장 계약의 `research/knowledge` 가족 스키마를 `jsonschema.Draft202012Validator`로 검사하면 오류 목록이 비어 있다. 거부 값은 모두 `ValueError`를 낸다(유형만). 제품 메시지는 `"uncertainty_assessment must be text or an object"`다.
- 대역: 없음.
- 비고: `subTest(accepted=...)` 두 개, `subTest(rejected=...)` 네 개. 가져오기 검사와 저장 스키마가 같은 형식을 말하는지 대조하는 시험이다. `test_family_records.ProducerStorageContractTests`가 같은 성질을 생산자 쪽에서 본다.

### `test_candidate_import_is_not_usable_and_queues_formal_check` (행 22–45)
- 성질: 가져온 후보는 활성 기록이지만 사용할 수 없고, 형식 결과는 후보 상태로 비어 있으며, 형식 검사가 대기열에 오른다. 사용자 가져오기는 생산 실행을 남기지 않고 행위자를 출처에 더한다. 실재 실행이 가져오면 세 저작 기록에 그 실행을 생산자로 남긴다. 입력 상태는 바뀌지 않는다.
- 준비: 빈 `before` 사전과 빈 런타임.
- 실행: `import_candidate(before, {}, knowledge_candidate(), source_ref='source', actor_ref='user')`. 이어 런타임에 `executions: {'EX-author': ...}`를 두고 `actor_ref='EX-author'`로 한 번 더 부른다.
- 단언:
  - 지식 기록의 `lifecycle`이 `'active'`이고 `formal`, `reviews`, `statement` 키가 없다. 진술은 해설 가족으로 분리된다.
  - 형식 결과의 `publication_state`는 `'candidate'`, `verification`은 `{}`이다.
  - `kr.usable_links`가 `[]`이다.
  - 기록의 `origin_refs`에 `'source'`가 있다.
  - 지식, 해설, 형식 결과 세 기록 모두 `producer_execution`이 없고 `origin_refs`에 `'user'`가 있다.
  - 대기열 마지막 행동의 역할이 `'formal_check'`이다.
  - `before`가 여전히 `{}`이다.
  - 둘째 호출에서는 세 기록 모두 `producer_execution == 'EX-author'`이다.
- 대역: 없음.
- 비고: 제품 근거는 `import_candidate` 안의 주석(301–302행) "User/import provenance is not an execution identity. Review author exclusion links must resolve to real executions in this instance."다.

### `test_same_id_import_rejected_explicit_revision_preserves_old_authorities` (행 47–59)
- 성질: 이미 있는 ID로는 다시 가져올 수 없다. 명시적 개정은 새 ID의 대체 기록을 만들고, 옛 형식 결과를 재사용하며, 옛 판정과 옛 해설을 그대로 둔다.
- 준비: `knowledge_graph()`, 대상은 `ids['a']`.
- 실행: `knowledge_candidate(id=kid)`로 `import_candidate`를 부르고, `revise_knowledge(ins, run, kid, {'statement': 'Rephrased True'})`(픽스처: 계산된 영향을 선언으로 붙여 `knowledge.revise_knowledge`를 부른다)를 부른다.
- 단언:
  - 같은 ID 가져오기는 `ValueError`를 낸다(유형만. 제품 메시지는 `"record ID already exists; revisions require a new ID"`).
  - `supersedes == kid`인 대체 기록의 ID가 `kid`와 다르다.
  - 대체 기록의 `formal_result_id`가 옛 기록의 것과 같다. Lean 코드가 바뀌지 않았으므로 재사용한다.
  - `identity_assessments`가 개정 전과 같아 새 판정이 생기지 않는다.
  - `kr.proposal_view(changed, kid)['statement']`가 `'True'`이므로 옛 해설이 보존된다.
  - 대체 기록의 `usable_links`가 `[]`이다. 새 해설에는 아직 판정이 없다.
  - 대기열 마지막 역할이 `'identity_review'`다.
- 대역: 없음.

### `test_unknown_kind_requires_candidate_check_and_activation` (행 61–71)
- 성질: 설치되지 않은 지식 종류는 등록, 독립 검사, 활성화를 모두 거친 뒤에만 쓸 수 있고, 검사 전 활성화는 거부된다.
- 준비: 정의 `family='knowledge'`, `token='computational_lemma'`, `constraints={}`.
- 실행: 다섯 단계를 차례로 밟는다. (1) 등록 전에 `import_candidate`를 부른다. (2) `register_kind_definition` 뒤 다시 가져온다. (3) 검사 전에 `activate_kind_definition`을 부른다. (4) `check_kind_definition` 뒤 다시 가져온다. (5) `activate_kind_definition` 뒤 가져온다.
- 단언: (1) `ValueError`다. 제품 메시지는 `"unknown knowledge kind: computational_lemma"`다. (2) 상태가 `candidate`이므로 `ValueError`다. (3) `ValueError`다. 제품 메시지는 `"kind definition must be checked before activation"`이다. (4) 상태가 `checked`여도 `ValueError`다. (5) 가져온 기록의 `kind`가 그 토큰이다.
- 대역: 없음.
- 비고: 음성 단언은 모두 예외 유형만 확인하고 메시지는 보지 않는다.

### `test_relation_claim_endpoint_basis_matches_the_storage_contract` (행 73–103)
- 성질: 관계 주장을 담은 후보는 두 끝점의 기준(`relation_endpoint_basis`)을 `capture_basis`의 결과 그대로 저장한다. 그 상태는 설치 저장 계약을 통과한다. 저장 스키마는 기준 행의 모양을 닫힌 형태로 강제한다.
- 준비: `research_fixtures.current_state({'object_format': 'sha1'})`로 저장 계약이 받는 최소 상태를 만든다. 비형식 후보 두 개(`lean_code=''`, `declaration_names=[]`, 제목 `'Source endpoint'`, `'Target endpoint'`)를 가져와 끝점으로 둔다.
- 실행: 관계 주장 `formally_implies`(`confirmed_scope='True implies True'`)을 담은 후보를 가져오고, `knowledge.capture_basis(ins, run, endpoints)`로 기대값을 만든다. `contract.validate(ins, run)`과 `knowledge.validate_basis`를 부른다. 스키마에는 잘못된 기준 넷을 넣어 `jsonschema.validate`를 부른다.
- 단언: 저장된 `relation_endpoint_basis`가 기대값과 같다. `contract.validate`가 예외 없이 끝난다. `validate_basis(...)['valid']`가 참이다. 잘못된 기준 네 가지 모두 `jsonschema.ValidationError`를 낸다. 넷은 빈 객체 `{}`(목록 아님), `sha256='not-a-hash'`인 행, `status`가 빠진 행, 등록되지 않은 필드 `unregistered`를 더한 행이다.
- 대역: 없음.
- 비고: `subTest(basis=...)` 네 개.

### `test_missing_dependency_is_rejected_without_mutation` (행 105–110)
- 성질: 없는 기록에 의존하는 후보는 거부되고 입력 상태는 바뀌지 않는다.
- 준비: `knowledge_graph()`와 그 `deepcopy`.
- 실행: `dependencies=[new_id('KN')]`인 후보로 `import_candidate`.
- 단언: `ValueError`(유형만. 제품 메시지 `"candidate dependencies do not exist: "`)가 나고, 상태가 사본과 같다.
- 대역: 없음.

### `test_research_analogy_is_distinct_from_mathematical_connection` (행 112–118)
- 성질: 연구 유비 관계는 증거만으로 유효하며 `research_connection` 권위로 저장된다. 같은 끝점과 증거라도 수학 관계 종류로는 유효하지 않다.
- 준비: `knowledge_graph()`와 관계 `analogous_to`(`a→b`, `evidence='Same recurrence shape'`).
- 실행: `validate_relation`, `import_relation`, 종류를 `formally_implies`로 바꾼 `validate_relation`.
- 단언: 첫 검증이 유효하다. 저장된 관계의 `authority`가 `'research_connection'`이다. 수학 종류 검증은 `valid`가 거짓이다.
- 대역: 없음.

### `test_mathematical_relation_requires_match_in_addition_to_active_use` (행 120–148)
- 성질: 수학 관계는 활성 사용을 가진 판정만으로는 성립하지 않는다. 같은 관계 주장을 확정하는 `match` 판정을 직접 가리켜야 한다.
- 준비: 판정값 `"mismatch"`와 `"unresolved"` 각각에 대해 새 `knowledge_graph()`를 만든다. 관계 주장 `formally_implies(a→b)`을 담은 후보를 `add_knowledge(verified=False, ...)`로 가져와 `proof`로 둔다. `kr.record_formal_result(..., formal_evidence(ins, proof), "TE-old")`로 형식 결과를 수리하고, 음성 판정(`policy:fixture`)을 봉인한다.
- 실행: 관계 `{**claim, evidence: 'proof', formal_result_refs: [proof의 형식 결과], assessment_refs: [negative]}`를 `validate_relation`에 넣는다. 이어 `match` 판정을 봉인하고 같은 관계를 다시 검증한다. 마지막으로 `assessment_refs`를 `[positive]`로 바꿔 검증한다.
- 단언:
  - 음성 판정에 `knowledge.assess_use`를 적용하면 `valid`가 참이다. 음성 판정도 활성 사용이 있으면 "사용 가능"하다는 전제를 먼저 고정한다.
  - 첫 검증은 무효이고, 사유 가운데 하나가 `"formal_result_does_not_establish_this_relation:"`로 시작한다.
  - `match` 봉인 뒤에도 음성 판정을 가리키는 관계는 무효이고, 사유에 `"assessment_not_effective:" + negative`가 있다.
  - `positive`를 가리키면 유효하다.
- 대역: 없음.
- 비고: `subTest(decision=...)` 두 개. 사유 문자열까지 고정하는 음성 시험이다.

### `test_mathematical_relation_requires_exact_formal_identity_and_current_endpoints` (행 150–163)
- 성질: 수학 관계는 그 관계 주장을 담은 기록의 형식 결과와 판정만 받는다. 끝점 기록이 바뀌면 더는 유효하지 않다.
- 준비: `knowledge_graph()`와 관계 주장 `formally_implies(a→b)`.
- 실행: (1) 관계 주장 없는 기록 `a`의 형식 결과와 판정 `aa`로 검증한다. (2) `add_knowledge(..., relation_claim=claim)`으로 증명 기록을 만든 뒤 그 형식 결과와 판정으로 검증하고 `import_relation`을 부른다. (3) 판정만 `aa`로 바꿔 검증한다. (4) 끝점 `b`의 `title`을 `'Changed endpoint'`로 직접 바꾼 뒤 검증한다.
- 단언: (1) 무효다. (2) 유효하고, 저장된 관계의 `authority`가 `'mathematical_connection'`이다. (3) 무효다. (4) 무효다.
- 대역: 없음.
- 비고: (4)의 무효 사유는 단언하지 않는다. 제품 경로에서는 증명 기록의 `relation_endpoint_basis`가 더는 `validate_basis`를 통과하지 않는다. 그래서 `record_premises_current`와 `assessment_current`가 거짓이 되고, 판정이 확정 판정 목록에서 빠진다.

### `test_relation_revision_keeps_id_and_history` (행 165–173)
- 성질: 같은 ID로 관계를 다시 가져오면 ID는 유지되고 개정 번호가 오르며 이전 판이 이력에 남는다.
- 준비: `knowledge_graph()`와 관계 `supports(a→b)`, `id=new_id('RL')`, `evidence='e1'`.
- 실행: `import_relation`을 `source_ref='s1'`로 부르고, `evidence='e2'`로 바꿔 `source_ref='s2'`로 다시 부른다.
- 단언: 두 번째 반환 ID가 첫 ID와 같다. 저장 행의 `revision`이 2이고, `history[-1]['evidence']`가 `'e1'`이다.
- 대역: 없음.

### `test_catalog_exposes_only_active_definitions` (행 175–188)
- 성질: 역할에 보이는 카탈로그는 `active` 정의만 담는다. 새 관계 종류는 독립 검사와 활성화를 거친 뒤에야 나타나고, 철회되면 사라진다.
- 준비: `BUILTIN_DEFINITIONS`의 관계 토큰 정렬 목록(`installed`). 새 정의 `translates_to`(`constraints={'requires_evidence': True}`)를 빈 상태에 등록한다.
- 실행: 등록 뒤, `check_kind_definition` 뒤, `activate_kind_definition` 뒤, `withdraw_kind_definition` 뒤마다 `catalog_definitions(ins)['relations']`의 토큰을 읽는다.
- 단언: 등록 뒤와 검사 뒤에는 `installed`와 같다. 활성 뒤에는 `installed`에 `'translates_to'`를 더한 정렬 목록이다. 철회 뒤에는 다시 `installed`다. 등록 뒤 지식 카탈로그에 `theorem` 토큰이 있다.
- 대역: 없음.
- 비고: 원문 주석은 "A new relation kind still passes an independent check before any use."다.

### `test_installed_relation_kinds_are_usable_without_activation` (행 190–198)
- 성질: 설치 관계 종류는 따로 활성화하지 않아도 쓸 수 있다. 설치 수학 종류도 활성이지만 증거 요구는 그대로 적용된다.
- 준비: `knowledge_graph()`와 관계 `supports(a→b)`.
- 실행: 그대로, 그리고 종류를 `formally_implies`로 바꿔 `validate_relation`.
- 단언: `supports`는 유효하다. `formally_implies`는 무효이고, 사유에 `'formal_result_refs_required'`와 `'assessment_refs_required'`가 모두 있다.
- 대역: 없음.
- 비고: 원문 주석은 "An installed mathematical kind is active too; its evidence requirement still applies."다.

## 관계

- 같은 도메인 함수를 다른 층에서 검사하는 모듈:
  - `test_knowledge`는 현재성, 영향, 개정, 종류 제약, 신뢰 환경 전환을 도메인에서 본다. `test_kind_registration_requires_explicit_check_and_activation` 등 종류 등록 시험 일부가 이 모듈의 `test_unknown_kind_requires_candidate_check_and_activation`과 겹친다.
  - `test_knowledge_import_engine`은 엔진 제어 `knowledge`(`operation='import'`, `'register-kind'`)로 들어온 가져오기와 사용자 종류 정의가 실제 Git에 저장되고 작업자 카탈로그에 도달하는 과정을 본다.
  - `test_knowledge_storage`는 실제 Git 저장을 거친 왕복을 본다.
  - `test_family_records.test_relation_claim_endpoint_basis_survives_storage_and_remains_typed`는 이 모듈의 `test_relation_claim_endpoint_basis_matches_the_storage_contract`를 실제 Git 저장으로 확장한다.
- 픽스처 의존: `knowledge_fixtures`의 `knowledge_candidate`, `knowledge_graph`, `add_knowledge`, `revise_knowledge`, `formal_evidence`, 그리고 `research_fixtures.current_state`.
- 이 모듈에만 있는 도우미는 없다.

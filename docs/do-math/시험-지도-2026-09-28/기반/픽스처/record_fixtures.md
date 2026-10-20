# record_fixtures

| 항목 | 값 |
|---|---|
| 원문 | `.claude/skills/do-math/scripts/tests/record_fixtures.py` (393행) |
| 정의 수 | 모듈 함수 25, 클래스 0, 모듈 수준 상수 0 |
| 이 모듈을 쓰는 시험 모듈 | 39개(`consumers.json` 기준). 이 밖에 픽스처 모듈 `engine_fixtures`, `review_fixtures`가 이 모듈을 쓴다 |
| 모듈 수준 import | `copy.deepcopy`, 제품 `do_math.governance`(`gov`)·`do_math.planning`·`repository.exact_content_hash`, `research_fixtures`의 `approved_governance`, `charter`, `current_state`, `review_items` |

## 목적

모듈 docstring(행 1–62)은 이 모듈을 "순수 도메인 함수 시험을 위한 레코드" 모듈이라고 부른다. 영역은 거버넌스, 과제 계약, 제출이다. docstring이 세우는 경계는 두 가지다(행 3–5).
- 모든 함수는 새로운 평범한 레코드(사전)를 돌려주고, 저장소를 열거나 엔진을 돌리지 않는다.
- 레코드는 명시적 합성 승인과 증거를 싣는다. 실제 사용자 결정이나 모델 판단은 싣지 않는다.

그래서 이 모듈의 모든 정의는 `시험-지침.md` 4절 규칙 3의 1단(순수 함수나 검증기 직접 호출)에 속한다. 레코드를 만드는 과정에서는 제품의 순수 함수를 실제로 부른다. `governance.prepare_import`·`check_import`·`apply_import`, `planning.seal_contract_review`, `task_scope.apply_task_assessments` 등이 그런 함수다. 그래서 결과 레코드는 제품 규칙을 통과한 모양이다.

docstring은 정의를 세 절로 나눈다.
- 거버넌스(행 7–24)
- 과제 계약(행 26–50)
- 제출과 표면(행 52–62)

## 구성

화살표(→)는 "부른다"를 뜻한다.

1. **거버넌스.**
   - `domain_governance` → `research_fixtures.approved_governance`·`charter`
   - `governance_import` → `domain_governance`, 제품 `gov.import_input_source`
   - `checked_import` → `governance_import`, `charter`, 제품 `gov.prepare_import`·`check_import`, `exact_content_hash`
   - `audited_governance` → `domain_governance`, 제품 `gov.apply_decision`
   - `applied_initial_intent` → 제품 `initialization.initialize_state`, `approved_governance`, `charter`, 제품 `gov.import_input_source`·`prepare_import`·`check_import`·`apply_import`
2. **과제 계약.**
   - `task_contract`
   - `approved_task` → `task_contract`, `domain_governance`, `approve_task`, 제품 `configuration.DEFAULT_CONFIG`, `execution_profiles.seal_profile`·`profile_ref`·`BOUNDARY`, `observations.observation_rule_contract`
   - `approve_task` → `research_fixtures.review_items`, 제품 `planning.seal_contract_review`
   - `task_disposition`
   - `transfer_assessment` → `approved_task`, 제품 `planning.contract_hash`
   - `apply_assessment` → 제품 `task_scope.apply_task_assessments`
   - `completed_with_knowledge` → `transfer_assessment`, `apply_assessment`
   - `specialist_assessment` → `transfer_assessment`, `knowledge_fixtures.verified_knowledge`
   - `withdrawable_task` → `task_contract`
   - `withdraw_prepared` → 제품 `task_scope.apply_task_dispositions`
   - `installation_repair_state` → 제품 `activities.open_activity`
3. **준비 자기 점검.**
   - `contract_check`
   - `preparation_context`
   - `preparation_issues` → `research_fixtures.supply_observation_rules`, `runner_fixtures.common`·`rating`, 제품 `contracts.schema_for`·`submission.payload_issues`
4. **제출과 표면.**
   - `execution_state` → `research_fixtures.current_state`, 제품 `build_profiles`·`profile_ref`·`open_activity`·`assign_execution`·`create_execution`
   - `two_observation_output` → `observation_knowledge`
   - `observation_knowledge`
   - `research_work_context`
   - `surface_state` → `approved_governance`, `charter`, 제품 `execution_profiles`·`activities`·`execution_lifecycle`
   - `stored_surface_state` → `surface_state`, `current_state`

## 1. 거버넌스

### `domain_governance()` (행 71–72)
- 종류: 함수(레코드).
- 하는 일과 반환값: `approved_governance({"id": "I"}, [charter()])`를 돌려준다. 결과는 인스턴스 `I`이고, 헌장 `CH1`(목표 "Prove P")을 원천 `S`("User approves P")에서 온 결정 `D`로 채택했다(docstring 행 9–11).
- 부작용: 없다.
- 의존: `research_fixtures.approved_governance`, `research_fixtures.charter`.
- 시작 상태의 단: 1단.
- 소비자: `test_academic`, `test_delegations`, `test_goal_audit`, `test_governance`, `test_observations`, `test_planning`, `test_questions`, `test_task_contracts`. 모듈 안에서는 `governance_import`, `audited_governance`, `approved_task`가 부른다.

### `governance_import()` (행 75–85)
- 종류: 함수(레코드).
- 하는 일과 반환값: 공개 입력 `IN`을 단위 하나 `U`로 해석한 가져오기 출력을 만든다. 이 해석은 선택 질문 하나 `Q`를 묻는다(docstring 행 12–14). 만드는 것은 다음과 같다.
  - **인스턴스:** `domain_governance()`
  - **런타임:** `tasks`, `executions`, `queue`가 비어 있고 `status="ready"`이며, 입력 행 `{"id": "IN", "text": "A choice", "origin": "user"}` 하나를 갖는다.
  - **원천:** 제품 `gov.import_input_source(i, rt, "IN")`로 얻는다.
  - **단위 `U`:** 원천 범위는 0–8, 곧 "A choice" 전체다. 해석은 "Ask a choice"이고 `owner_kind="charter"`, `owner_ref="CH1"`, `payload={}`, `decision_refs=["D"]`, `question_refs=["Q"]`다.
  - **질문:** `questions=["Which scope?"]`와 `question_details` 한 행을 싣는다. 그 행은 `id="Q"`, `target_ids=["I"]`, `blocks=False`, 선택지 "Keep"/"No change", `source_unit_ids=["U"]`를 갖는다.

  반환값은 `(instance, runtime, source, output)`다.
- 부작용: 없다.
- 의존: `domain_governance`, 제품 `governance.import_input_source`.
- 시작 상태의 단: 1단.
- 소비자: `test_governance`, `test_observations`, `test_planning`. 모듈 안에서는 `checked_import`가 부른다.

### `checked_import(kind='charter', handlers=None, payload=None)` (행 88–105)
- 종류: 함수(레코드).
- 하는 일과 반환값: `governance_import`의 해석을 `payload`를 제안하도록 바꾼다. 그 제안을 독립 확인하고, 사용자의 나중 정확 승인 `request`를 기다리는 상태로 만든다(docstring 행 15–19). 절차는 다음과 같다.
  1. `payload` 기본값은 `{'kind': kind, 'record': 헌장 CH2}`다. `CH2`는 목표 "Prove Q"이고 `supersedes=['CH1']`이다. `kind`를 바꾸고 `payload`를 주지 않으면 기록은 여전히 헌장 `CH2`이고 `kind`만 바뀐다.
  2. 출력의 질문을 비운다. 단위를 `owner_kind=kind`, `owner_ref=payload['record']['id']`(없으면 `'I'`), `payload`, `question_refs=[]`로 고친다. `decision_refs=["D"]`는 남는다.
  3. 제품 `gov.prepare_import(..., execution_id='E1', input_ref="IN", owner_handlers=handlers)`로 묶음을 만든다.
  4. 런타임 실행 `E2`(역할 `intent_interpretation`, `intent_import_sha256`은 묶음 해시)를 등록한다. 작성 실행 `E1`은 런타임에 등록하지 않는다.
  5. 제품 `gov.check_import`로 확인 판정을 적용한다. 판정은 `approved`, `scope_complete=True`, `unit_ids=['U']`, 질문과 발견은 비어 있으며, `execution_id='E2'`와 같은 `owner_handlers`를 쓴다.
  6. 승인 요청 `request`를 만든다. ID는 `'LATER'`, 행동은 `decision`, 출처는 `user`다. 설정은 `kind='import_approval'`이고, 묶음 ID, 묶음 해시, 확인 해시(`bundle['check']['sha256']`), 단위 해시(`{'U': exact_content_hash(payload)}`)를 담는다.
  7. 런타임 `waiting_actions['CHECK']`에 `kind='import_application_authority'` 대기를 넣는다. 대기 행동은 `{'id': 'CHECK', 'role': 'intent_interpretation', 'stage': 'check'}`다.

  반환값은 `(instance, runtime, bundle, request)`다. 요청은 만들기만 하고 적용하지 않는다.
- 부작용: 없다.
- 의존: `governance_import`, `research_fixtures.charter`, 제품 `gov.prepare_import`·`check_import`, `exact_content_hash`.
- 시작 상태의 단: 1단.
- 소비자: `engine_fixtures`, `test_control_shapes`, `test_governance`, `test_governance_engine`.

### `audited_governance()` (행 108–114)
- 종류: 함수(레코드).
- 하는 일과 반환값: `domain_governance()`와 최소 런타임(`status='ready'`)으로 시작한다. 여기에 추가 감사 기록 `AU`를 제품 `gov.apply_decision(i, rt, {'kind': 'additional_audit', 'record': audit}, source_ref='S')`로 적용한다. `AU`의 필드는 다음과 같다.
  - `kind='additional_audit'`, 개정 1
  - 범위 `['P']`, 필요 입력 `['CH1']`
  - 평가자 `goal_audit`
  - 판정 사상: `pass`→`satisfied`, `partial`→`not_satisfied`, `unknown`→`unresolved`

  반환값은 `(instance, runtime)`다. docstring(행 20–21)은 이것을 "`CH1`에 대한 활성 추가 목표 감사 `AU`"라고 부른다.
- 부작용: 없다.
- 의존: `domain_governance`, 제품 `gov.apply_decision`.
- 시작 상태의 단: 1단.
- 소비자: `engine_fixtures`, `test_control_shapes`, `test_goal_audit`, `test_governance_engine`.

### `applied_initial_intent(text)` (행 117–141)
- 종류: 함수(레코드).
- 하는 일과 반환값: 새로 초기화한 인스턴스를 만든다. 그 원본 입력 `text`를 해석하고 확인해 채택된 헌장에 적용한다(docstring 행 22–24). 절차는 다음과 같다.
  1. 제품 `initialization.initialize_state(instance_id='RI-case', goal=text, workspace=시스템 임시 디렉터리, config={}, source_input=text)`로 상태를 만든다.
  2. `approved_governance`로 헌장 `CH1`을 원천 `('GS-adoption', text)`와 승인 `DC-adopt`로 채택한다.
  3. 수명 주기의 `input_id`로 `gov.import_input_source`를 불러 원천을 얻는다.
  4. 원문 전체를 단위 `IU-goal` 하나로 해석한 출력을 만든다.
  5. 실행 `EX-author`를 등록하고 `gov.prepare_import`로 묶음을 만든다.
  6. 실행 `EX-check`를 등록하고 `gov.check_import`로 승인 판정을 적용한다.
  7. `gov.apply_import`로 적용한다.
  8. 영수증 `status`가 `'applied'`가 아니거나 원천 ID가 입력 ID와 같으면 `AssertionError('The initial interpretation was not applied from its own input source: ...')`를 던진다. 곧 해석이 입력 자체가 아니라 그 입력에서 보존한 자기 원천으로 적용됐는지 스스로 검사한다.

  반환값은 `(instance, runtime, 묶음 ID)`다.
- 부작용: 없다. 작업 공간은 경로 값으로만 넘긴다.
- 의존: `research_fixtures.approved_governance`·`charter`, 제품 `initialization.initialize_state`, `gov.import_input_source`·`prepare_import`·`check_import`·`apply_import`.
- 시작 상태의 단: 1단.
- 소비자: `test_governance`, `test_initial_intent_connection`.

## 2. 과제 계약

### `task_contract()` (행 144–156)
- 종류: 함수(레코드).
- 하는 일과 반환값: 계획된 계약 `TK-1`을 돌려준다(개정 1, `status="planned"`). 필드는 다음과 같다.
  - 질문: "What follows?"
  - 범위: 포함 "derive result", 제외 "publish"
  - 기대 출력: "proof sketch"
  - 진행 기준: `PG-1`(증거 `EV-1`)
  - 완료 의무 둘: `OB-1`("provide the proof sketch", 판정자 `task_assessor`, 증거 `EV-1`), `OB-2`("preserve the excluded publication boundary", 판정자 `task_assessor`, 증거 없음)
  - `occurrence_condition={"op": "always"}`
  - 프로필 참조: `PF-1`(개정 1, 해시 `"a"*64`)
  - 권한 참조: `GR-1`, 근거 참조: `KN-1`
- 부작용: 없다.
- 의존: 없다.
- 시작 상태의 단: 1단.
- 소비자: `test_context_store`, `test_governance_engine`, `test_input_recovery`, `test_role_input`, `test_state_checks`, `test_task_contracts`, `test_task_scope`. 모듈 안에서는 `approved_task`와 `withdrawable_task`가 부른다.

### `approved_task()` (행 159–180)
- 종류: 함수(레코드).
- 하는 일과 반환값: `task_contract`를 `domain_governance`의 비형식 과제로 만든다. 원천 `SO-1` 하나, 작업 프로필과 권한 하나씩, 승인된 계약 검토를 갖춘다(docstring 행 30–32). 만드는 것은 다음과 같다.
  - **설정:** `DEFAULT_CONFIG`의 깊은 사본이다. `tier_models`는 세 등급 모두 `fixture-model`이고, `session_limits={'work': {'fixture-model': 3}}`이다.
  - **프로필:** 제품 `seal_profile`로 봉인한 `research_work` AI 프로필이다. 모델 `fixture-model`, 등급과 노력은 `high`, 경계는 `BOUNDARY`, 관찰은 `event_driven`과 `observation_rule_contract()`다. 용량 참조는 `'CP-' + exact_content_hash({'model': 'fixture-model', 'work': 3})` 하나다. 주석(행 165)에 따르면 작업 역할의 AI 프로필은 모델의 작업 슬롯을 예약한다.
  - **과제:** `task_contract()`에 `work_class='nonformal'`, `basis_refs=['SO-1']`, `profile_refs=[프로필 참조]`, `inputs=['SO-1']`, `results=[]`, `producer_execution='EX-author'`를 덮는다.
  - **인스턴스:** `domain_governance()`에 `id='IN-1'`, 원천 `SO-1`, 프로필, 설정, 권한 `GR-1`을 더한다. `GR-1`은 `local`, `active`, 행위자 `ai`, 역할 `research_work`, 과제 `TK-1`, `reusable`이며, 유효 기간 제한이 없다.
  - **런타임:** `status='active'`이고 `tasks={'TK-1': 과제}`이며, 나머지 목록은 비어 있다.
  - 끝으로 `approve_task(과제, 인스턴스, 런타임)`로 검토를 붙인다.

  반환값은 `(task, instance, runtime)`다. 런타임의 `TK-1`과 반환된 `task`는 같은 객체다.
- 부작용: 없다.
- 의존: `task_contract`, `domain_governance`, `approve_task`, 제품 `DEFAULT_CONFIG`, `seal_profile`, `profile_ref`, `BOUNDARY`, `observation_rule_contract`, `exact_content_hash`.
- 시작 상태의 단: 1단.
- 소비자: `test_input_recovery`, `test_model_metadata_boundary`, `test_planning`, `test_planning_engine`, `test_relation_dependencies`, `test_reporting`, `test_revision_obligations`, `test_role_input`, `test_task_contracts`. 모듈 안에서는 `transfer_assessment`가 부른다.

### `approve_task(value, instance, runtime)` (행 183–185)
- 종류: 함수.
- 하는 일과 반환값: `research_fixtures.review_items(['SO-1'])`로 모든 항목을 승인한 검토 출력을 만든다. 이것을 제품 `planning.seal_contract_review(value, output, instance, runtime, execution_id='EX-review')`로 봉인하고, `value['reviews']`를 그 한 행으로 덮는다. 반환값은 없다.
- 부작용: 인자 `value`를 제자리에서 바꾼다.
- 의존: `research_fixtures.review_items`, 제품 `planning.seal_contract_review`.
- 시작 상태의 단: 1단.
- 소비자: `test_input_recovery`, `test_planning`, `test_planning_engine`, `test_relation_dependencies`, `test_role_input`, `test_task_contracts`. 모듈 안에서는 `approved_task`가 부른다.

### `task_disposition(identifier, kind='selected')` (행 188–192)
- 종류: 함수(레코드).
- 하는 일과 반환값: 계획 처분 한 행을 돌려준다. `reason`, `uncertainty`, `expected_research_change`는 고정 문구이고, `revisit`은 `{'event_refs': ['EV-next'], 'at': None}`이다. 두 필드는 `kind`에 따라 달라진다.
  - `missing_inputs`: `kind == 'not_assessable'`일 때만 `['SO-missing']`이다.
  - `next_owner`: `kind == 'selected'`이면 `'research_work'`, 아니면 `'research_plan'`이다.

  `research_fixtures.disposition`은 `kind`와 관계없이 `research_work`를 준다. 이 점이 그 함수와 다르다.
- 부작용: 없다.
- 의존: 없다.
- 시작 상태의 단: 1단.
- 소비자: `test_context_store`, `test_planning_engine`, `test_revision_obligations`, `test_role_input`, `test_task_contracts`.

### `transfer_assessment()` (행 195–209)
- 종류: 함수(레코드).
- 하는 일과 반환값: `approved_task`의 과제가 `EV-1`과 함께 반환된 상태를 만든다. 사용자 결정 `DC-1`이 `OB-2`를 `TK-2`로 이관하고, 계획 평가가 그 이관으로 `TK-1`을 닫는다(docstring 행 34–37). 절차는 다음과 같다.
  1. `TK-1`의 모든 의무 판정자를 `['research_plan']`으로 바꾼다. `status='waiting'`으로 두고, 결과를 `[{'id': 'EV-1', 'execution_id': 'EX-work'}]`로 둔다.
  2. 그 깊은 사본으로 `TK-2`를 만든다(결과·검토 없음, `planned`).
  3. 실행 `EX-plan`(`research_plan`, `ended`)을 등록한다.
  4. `instance['decisions']`를 `DC-1` 하나만 가진 사전으로 **통째로 바꾼다**. 그래서 `domain_governance`가 남긴 결정 `D`는 이 사전에서 사라진다. `DC-1`의 필드는 다음과 같다.
     - 행위자 `user`, 원천 `SO-1`
     - 변경: `task_scope`/`transfer`
     - 대상: `TK-1` 개정 1, 계약 해시 `planning.contract_hash(t)`
     - 이관: 의무 `['OB-2']`를 `TK-2`로
  5. 평가를 만든다. `decision='closed'`이고, `OB-1`은 `fulfilled`(`EV-1`)다. `OB-2`는 `transferred`이며 `authority_ref='DC-1'`, `target_task_id='TK-2'`, `target_obligation_id='OB-inherited'`를 갖는다.

  반환값은 `(instance, runtime, assessment)`다. 평가는 적용하지 않고 만들기만 한다.
- 부작용: 없다.
- 의존: `approved_task`, 제품 `planning.contract_hash`.
- 시작 상태의 단: 1단.
- 소비자: `engine_fixtures`, `test_research_recovery`, `test_task_completion`, `test_task_contracts`. 모듈 안에서는 `completed_with_knowledge`와 `specialist_assessment`가 부른다.

### `apply_assessment(i, r, a)` (행 212–214)
- 종류: 함수.
- 하는 일과 반환값: 제품 `task_scope.apply_task_assessments(i, r, [a], execution_id='EX-plan', input_tasks=deepcopy(r['tasks']))`의 결과, 곧 새 `(instance, runtime)`을 돌려준다. docstring(행 37)에 따르면 평가를 계획 실행 `EX-plan`으로서 적용한다. 입력 과제 스냅숏은 적용 직전 런타임 과제의 깊은 사본이다.
- 부작용: 없다(제품 함수가 사본 위에서 적용한다).
- 의존: 제품 `task_scope.apply_task_assessments`.
- 시작 상태의 단: 1단.
- 소비자: `engine_fixtures`, `test_research_recovery`, `test_task_completion`, `test_task_contracts`. 모듈 안에서는 `completed_with_knowledge`가 부른다.

### `completed_with_knowledge()` (행 217–231)
- 종류: 함수(레코드).
- 하는 일과 반환값: `transfer_assessment`에서 시작해 평가를 `completed`로 바꾼다. `TK-1`의 각 의무는 `fulfilled`로 처분하고, 증거는 `['KN-proof', *의무의 필요 증거]`다. 인스턴스에는 다음 지식 가족을 더한다.
  - `knowledge`: 후보 정리 `KN-proof`(`active`, 형식 결과 `FR-proof`, 해설 `XP-proof`)
  - `formal_results`: `FR-proof`(`publication_state='candidate'`, `formal_use='suspended'`)
  - `expositions`: `XP-proof`
  - `identity_assessments`, `assessment_uses`: 빈 사전

  반환값은 `apply_assessment(...)`의 결과 `(instance, runtime)`다. docstring(행 38–39)은 이것을 "후보 정리 `KN-proof`를 인용한 완료 평가 뒤"라고 부른다.
- 부작용: 없다.
- 의존: `transfer_assessment`, `apply_assessment`.
- 시작 상태의 단: 1단.
- 소비자: `test_relation_dependencies`, `test_task_completion`.

### `specialist_assessment(judge='identity_review')` (행 234–246)
- 종류: 함수(레코드).
- 하는 일과 반환값: `transfer_assessment`의 과제가 의무 하나만 갖도록 바꾼다. 그 의무는 `judge`가 판정하고, 증거로 검증된 정리(`knowledge_fixtures.verified_knowledge`)를 인용한다(docstring 행 40–42). 절차는 다음과 같다.
  1. `verified_knowledge()`의 상태를 인스턴스에 병합한다. 병합은 얕은 `update`다.
  2. 그 지식의 `task_id`를 `TK-1`로 둔다.
  3. `TK-1`의 의무를 `OB-certification` 하나로 바꾼다. 판정자는 `[judge]`, 필요 증거는 없다.
  4. 평가를 `completed`로 바꾸고 `OB-certification`을 `fulfilled`로 처분한다. 인용하는 증거는 `judge`에 따라 다르다. `judge == 'identity_review'`이면 식별 평가 ID이고, 아니면 그 지식의 `formal_result_id`다.

  반환값은 다섯 값 `(instance, runtime, assessment, 지식 ID, 식별 평가 ID)`다.
- 부작용: 없다.
- 의존: `transfer_assessment`, `knowledge_fixtures.verified_knowledge`(늦은 import).
- 시작 상태의 단: 1단.
- 소비자: `test_relation_dependencies`, `test_role_input`, `test_task_completion`, `test_task_contracts`.

### `withdrawable_task()` (행 249–261)
- 종류: 함수(레코드).
- 하는 일과 반환값: AI가 준비한 승인 과제 `TK-AI`를 만든다. 이 과제에는 의존 과제, 큐에 든 검토, 대기 중인 작업 행동이 딸린다(docstring 행 43–45). 만드는 것은 다음과 같다.
  - **`TK-AI`:** `task_contract()`에 `title="AI proposal"`, `revision=3`, `status="planned"`, `producer_execution="EX-prep"`, `reviews=[{"decision": "approved"}]`, 빈 결과를 덮는다.
  - **런타임:** 과제 두 개를 둔다. 하나는 `TK-AI`의 사본이고, 다른 하나는 `TK-AI`에 의존하는 `waiting` 과제 `TK-dependent`다. 실행 `EX-prep`(`research_preparation`, `ended`)도 둔다.
  - **큐:** `AC-review`(`task_contract_review`, 대상 `TK-AI`)와 `AC-other`(`research_plan`)가 들어 있다.
  - **대기 행동:** `AC-work`(`research_work`, 대상 `TK-AI`)가 있다.

  반환값은 `({}, runtime, {'TK-AI': 과제의 깊은 사본})`이다. 첫 값은 빈 인스턴스이고, 셋째는 입력 과제 스냅숏이다.
- 부작용: 없다.
- 의존: `task_contract`.
- 시작 상태의 단: 1단.
- 소비자: `test_task_completion`, `test_task_scope`.

### `withdraw_prepared(runtime, snapshot)` (행 264–268)
- 종류: 함수.
- 하는 일과 반환값: 제품 `task_scope.apply_task_dispositions({}, runtime, [...], execution_id="EX-plan", input_tasks=snapshot)`의 결과를 돌려준다. 처분은 `{"task_id": "TK-AI", "disposition": "withdraw", "reason": "The prepared task is superseded by a narrower current direction."}` 하나다. 결과는 새 `(instance, runtime)`이다. 인스턴스 인자는 언제나 빈 사전이다.
- 부작용: 없다.
- 의존: 제품 `task_scope.apply_task_dispositions`.
- 시작 상태의 단: 1단.
- 소비자: `test_task_completion`, `test_task_scope`.

### `installation_repair_state()` (행 271–296)
- 종류: 함수(레코드).
- 하는 일과 반환값: 실패한 계획 실행 하나가 수락된 설치 수리 진단을 기다리며 붙들린 상태를 만든다(docstring 행 46–47). 시각은 모두 `2026-09-22T00:00:00+00:00`이다. 만드는 것은 다음과 같다.
  - **활동:** 제품 `activities.open_activity`로 활동 `AY-work`(`research_plan`, 소유 `AC-work`)를 연다.
  - **실패 실행 `EX-failed`:** `research_plan`, `ended`이고, 오류는 "receiver contract conflict"다. 행동 `AC-work`를 싣고, 결과 참조는 `runtime/artifacts/failure/result.json`이다.
  - **활동 대기:** 활동에 이 실행을 배정하고 `waiting`으로 바꾼다. 대기 조건은 `{'error': 'receiver'}`, 다음 소유자는 `operations`다.
  - **진단 실행 `EX-diagnosis`:** `operational_review`, `ended`, `output_accepted`이고, 대상은 `EX-failed`다.
  - **운영 처분 `OD-repair`:** `status='installation_repair_pending'`이다. 처분 필드는 다음과 같다.
    - `kind='repair'`
    - `repair_target='installation:scripts/do_math/task_scope.py'`
    - `meaning_preserving=True`
    - 검증 문구
    - `next_owner='installation_recovery'`

    결과에는 `installation_repair`(설치 해시 `'a'*64`, 증거는 실패 결과 경로)를 싣는다.
  - **대기 행동 `AC-work`:** `kind='output_validation'`, 사유 "failed again"이다. 원 행동에 `repair_attempt=2`와 `repair`(실행 `EX-failed`, 오류 메시지 "actual error")를 더한다.

  반환값은 `(runtime, record)`다. 인스턴스는 돌려주지 않는다.
- 부작용: 없다.
- 의존: 제품 `activities.open_activity`.
- 시작 상태의 단: 1단.
- 소비자: `test_diagnosed_installation_recovery`, `test_repair_execution`.

## 3. 준비 자기 점검

### `contract_check(title="one", **changes)` (행 299–300)
- 종류: 함수(레코드).
- 하는 일과 반환값: 준비 자기 점검 한 행 `{"task_title": title, "sibling_boundaries": [], **changes}`를 돌려준다. `runner_fixtures.contract_checks`의 행과 같은 모양이며, 한 행씩 필드를 바꿀 수 있다.
- 부작용: 없다.
- 의존: 없다.
- 시작 상태의 단: 1단.
- 소비자: `test_context_store`, `test_contract_checks`, `test_live_observation`.

### `preparation_context()` (행 303–306)
- 종류: 함수(레코드).
- 하는 일과 반환값: 모델을 평가하는 준비의 고정 입력을 돌려준다(docstring 행 304). 행동은 `{"id": "AC-this", "role": "research_preparation"}`이고 `budget_unit="concurrent_sessions"`다. `tasks`, `knowledge_catalog`, `sources`는 빈 목록, `kind_definitions`는 빈 사전이다.
- 부작용: 없다.
- 의존: 없다.
- 시작 상태의 단: 1단.
- 소비자: `test_contract_checks`, `test_live_observation`.

### `preparation_issues(entries, *, candidates, context, workspace, conditions=None)` (행 309–331)
- 종류: 함수(수신 검사 호출).
- 하는 일과 반환값: `candidates`를 제안하는 준비 출력에 대해 수신자가 내는 문제 목록을 JSON 문자열로 돌려준다(docstring 행 310–315). 절차는 다음과 같다.
  1. 출력은 `runner_fixtures.common("research_preparation")`에 `candidates`를 덮은 것이다.
  2. 확장에는 후보마다 `rating(task_title=제목)` 모델 평가를 넣고, `contract_checks`에 `entries`를 넣는다. `conditions`가 주어지면 `task_conditions`로 넣는다.
  3. `research_fixtures.supply_observation_rules`로 후보마다 관찰 규칙을 더한다. docstring(행 313–315)에 따르면 이 함수는 호출 시점에 읽히며, 자기 행을 `conditions`에 직접 더한다. `conditions`가 비어 있지 않으면 `task_conditions`는 호출자가 넘긴 목록 객체 자체다. 그래서 두 가지 변경이 호출자에게 그대로 남는다. 후보 제목과 같은 `task_title` 행이 없으면 새 행이 호출자의 목록에 더해진다. 그런 행이 있고 `observation_rules`가 없으면 호출자의 그 행 사전에 규칙이 더해진다.
  4. 통합 묶음 `IN-check` 하나에 `output`과 확장의 모든 좌표를 구성원으로 담는다. 영향 집합과 권한 참조는 비어 있고, `previous_hashes`는 없다.
  5. 제품 `submission.payload_issues(output, schema_for("research_preparation"), context, extensions, workspace)`의 결과를 `json.dumps(..., ensure_ascii=False)`로 돌려준다.

  모듈 docstring(행 49)의 예시 `context=preparation_context()`는 호출 예다. 서명에서 `context`는 기본값 없는 필수 키워드 인자다.
- 부작용: 호출자의 `conditions` 목록과 그 행을 바꿀 수 있다(3 참조). 수신 검사가 `workspace`를 읽는다.
- 의존: `research_fixtures.supply_observation_rules`, `runner_fixtures.common`·`rating`, 제품 `contracts.schema_for`, `submission.payload_issues`.
- 시작 상태의 단: 1단(수신 검증기 직접 호출).
- 소비자: `test_contract_checks`, `test_live_observation`.

## 4. 제출과 표면

### `execution_state(role="formal_check")` (행 334–347)
- 종류: 함수(레코드).
- 하는 일과 반환값: 저장 수명 주기 관문을 통과하는 `(instance, runtime)`을 돌려준다. 기본 프로필과, 활동 `AT-1` 안의 `role` 실행 `EX-1` 하나를 갖는다(docstring 행 335). 절차는 다음과 같다.
  1. `current_state`에 `DEFAULT_CONFIG` 사본과 `build_profiles(DEFAULT_CONFIG)`의 가족을 넘기고, 런타임에 `executions={}`를 넘긴다.
  2. 역할이 `role`인 프로필을 고른다.
  3. 활동 `AT-1`을 연다. 활동 종류는 `role`과 관계없이 `formal_check`이고, 소유는 `engine`이다.
  4. 제품 `create_execution`으로 `EX-1`을 만든다. 행위자 종류는 프로필의 것이고, `input_manifest={}`, 시각은 `2026-09-20T00:00:00Z`다.
  5. `role`을 붙여 `assign_execution`으로 배정한다.
- 부작용: 없다.
- 의존: `research_fixtures.current_state`, 제품 `DEFAULT_CONFIG`, `build_profiles`, `profile_ref`, `open_activity`, `assign_execution`, `create_execution`.
- 시작 상태의 단: 1단.
- 소비자: `review_fixtures`, `test_family_records`, `test_knowledge_import_engine`.

### `two_observation_output()` (행 350–355)
- 종류: 함수(레코드).
- 하는 일과 반환값: 독립 관찰 두 개(`observation_knowledge("A")`, `("B")`)를 가진 `research_work` 출력을 돌려준다. `outcome="submitted"`다. 두 관찰은 통합 묶음 두 개에 나뉜다.
  - `IN-A`: 구성원 `output`, `output/knowledge/0`
  - `IN-B`: 구성원 `output/knowledge/1`

  두 묶음 모두 영향 집합과 권한 참조가 비어 있다.
- 부작용: 없다.
- 의존: `observation_knowledge`.
- 시작 상태의 단: 1단.
- 소비자: `review_fixtures`, `test_contracts`, `test_family_records`, `test_integration_bundles`, `test_submission_checks`, `test_submission_flow`.

### `observation_knowledge(title)` (행 358–360)
- 종류: 함수(레코드).
- 하는 일과 반환값: `kind="observation"`인 지식 한 행을 돌려준다. 제목, 진술, 설명, 요약이 모두 `title`이다. `lean_code`는 빈 문자열이고, `declaration_names`와 `dependencies`는 빈 목록이다.
- 부작용: 없다.
- 의존: 없다.
- 시작 상태의 단: 1단.
- 소비자: `review_fixtures`, `test_integration_bundles`. 모듈 안에서는 `two_observation_output`이 부른다.

### `research_work_context()` (행 363–366)
- 종류: 함수(레코드).
- 하는 일과 반환값: `two_observation_output`에 맞는 고정 입력 문맥을 돌려준다. 행동은 `research_work`이고 대상은 `TK-1`, 스냅숏은 `"fixed"`다. 종류 정의에서 지식 종류는 `observation` 하나이고 관계 종류는 없다. 목록들(`knowledge_catalog`, `tasks`, `sources`, `grants`)은 비어 있다.
- 부작용: 없다.
- 의존: 없다.
- 시작 상태의 단: 1단.
- 소비자: `review_fixtures`, `test_family_records`, `test_impact_review`, `test_integration_bundles`, `test_submission_checks`, `test_submission_flow`.

### `surface_state()` (행 369–386)
- 종류: 함수(레코드).
- 하는 일과 반환값: docstring의 "Submissions and surfaces" 절(행 52–62)이 말하는 표면 상태 `(instance, runtime)`을 돌려준다. 만드는 것은 다음과 같다.
  - **인스턴스:** `IN-1`이다. `approved_governance`로 헌장 `CH-1`(`evidence_boundary='Proof'`)을 원천 `GS-1`, 승인 `DC-1`로 채택한다. 설정은 `DEFAULT_CONFIG` 사본이고, 지식 관련 가족은 비어 있다. `build_profiles`의 기본 프로필을 더한다.
  - **런타임:** `status='active'`이고 나머지 가족은 비어 있다.
  - **활동과 실행:** 활동 `AC-1`(종류 `research`, 소유 `IN-1`)을 연다. `research_work` 프로필로 실행 `EX-1`(`actor_kind='ai'`, `input_manifest=[]`)을 만들어 역할을 붙이고 배정한다.

  모듈 docstring(행 60–61)은 `EX-1`을 "실행 중인(running)" 실행이라고 부른다. 그러나 제품 `create_execution`은 상태를 `"queued"`로 만들고(`execution_lifecycle.py`), 이 함수는 상태를 바꾸지 않는다. 그래서 실제 `EX-1`의 상태는 `queued`다.
- 부작용: 없다.
- 의존: `research_fixtures.approved_governance`·`charter`, 제품 `DEFAULT_CONFIG`, `execution_profiles.build_profiles`·`profile_ref`, `activities.open_activity`·`assign_execution`, `execution_lifecycle.create_execution`.
- 시작 상태의 단: 1단.
- 소비자: `engine_fixtures`, `test_claude_stream`, `test_cli_advanced`, `test_context_store`, `test_execution_profiles`, `test_formal_input_manifest`, `test_purpose_engine`, `test_reporting`, `test_research_recovery`, `test_role_input`, `test_state_checks`. 모듈 안에서는 `stored_surface_state`가 부른다.

### `stored_surface_state()` (행 389–393)
- 종류: 함수(레코드).
- 하는 일과 반환값: `surface_state()`의 런타임에서 `status`를 지운 뒤 `current_state(instance, runtime)`에 넘긴다. docstring(행 390)에 따르면 결과는 모든 저장 상태처럼 현재 수명 주기 관문 아래에 있다. 병합의 결과는 다음과 같다.
  - 인스턴스는 `current_state`의 기본 `lifecycle`(`state="initializing"`, 입력 `UI-fixture`)을 받는다.
  - 런타임은 기본 `status="initializing"`, `last_observed_utc`, 입력 목록을 받는다.

  그래서 `surface_state`의 `status='active'`는 `initializing`으로 바뀐다.
- 부작용: 없다.
- 의존: `surface_state`, `research_fixtures.current_state`.
- 시작 상태의 단: 1단.
- 소비자: `test_reporting`.

## 관계

**다른 픽스처 모듈과의 의존.** 이 모듈이 기대는 픽스처는 세 모듈이다.
- `research_fixtures`: `approved_governance`, `charter`, `current_state`, `review_items`(모듈 머리), `supply_observation_rules`(늦은 import)
- `runner_fixtures`: `common`, `rating`
- `knowledge_fixtures`: `verified_knowledge`

반대 방향으로는 `engine_fixtures`와 `review_fixtures`가 이 모듈의 레코드를 가져가 메모리 엔진이나 검토 하네스의 시작 상태로 쓴다. `engine_fixtures`는 `checked_import`, `audited_governance`, `transfer_assessment`, `apply_assessment`, `surface_state`를 쓴다. `review_fixtures`는 `execution_state`, `two_observation_output`, `observation_knowledge`, `research_work_context`를 쓴다.

**시작 상태 체계에서 맡는 자리.** 이 모듈 전체가 `시험-지침.md` 4절 규칙 3의 1단을 맡는다. 저장소, 엔진, 프로세스 없이 순수 도메인 함수에 넘길 사전을 만든다. 레코드를 손으로 적지 않고 제품의 순수 함수(거버넌스 가져오기·확인·적용, 계약 검토 봉인, 과제 평가 적용)를 실제로 거쳐 만든다. 그래서 결과가 제품 규칙이 받아들이는 모양임이 만들 때 이미 확인된다. `applied_initial_intent`의 적용 검사처럼 픽스처가 스스로 확인하는 경우도 있다.

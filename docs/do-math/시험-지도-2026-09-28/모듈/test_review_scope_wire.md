# test_review_scope_wire

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_review_scope_wire.py` (165행) |
| 클래스 / 테스트 | 2 / 6 |
| 시험 대상 제품 코드 | `do_math/review_cycle.py`의 `stage_schema`, `review_action`, `start_review`, `next_actions`, `context_for`, `accept_result`, `validate_visible_output`(내부 `_validate_content`); `do_math/review_policy.py`의 `build_review_policy`, `validate_scope_assessment`, `minimum_scope_executions`; `do_math/contracts.py`의 `with_integration_schema`; `do_math/submission.py`의 `_payload_issues`; `do_math/record_schemas/schemas.py`의 `RECORDS['sources']`, `RUNTIME_FIELDS['review_inputs']`(패키지 `do_math.record_schemas`가 다시 내보낸다); `do_math/review_engine.py`의 `_start_identity_review`; `do_math/execution_profiles.py`의 `build_profiles` |
| 사용하는 픽스처 모듈 | `research_fixtures`: `bare_engine`, `scope_response` |
| 격리 표지 | 없음 |
| 시작 상태 | `ScopeWireTests`: 1단(스키마, 검증기, 검토 주기 순수 함수를 직접 호출). `ExpandedScopeRevisionTests`: 1단의 검토 주기 함수로 이전 주기를 만들고, 네 단 밖의 `bare_engine`(저장소 없는 엔진)에서 `_start_identity_review`를 부른다 |

## 목적

모듈 docstring은 "범위(scope) 응답은 설치된 전송 스키마(wire)와 검토 소비자를 모두 만족해야 한다"라고 밝힌다. 동일성 검토의 첫 단계인 범위 좌석은 모델에게 두 겹의 스키마를 준다. 안쪽은 `review_cycle.stage_schema("scope")`이고 거기에 제안 digest를 `enum`으로 묶는다. 바깥은 `contracts.with_integration_schema`의 통합 봉투다. 모델의 응답은 이 전송 스키마를 통과한 뒤, 검토 소비자(`accept_result`)의 의미 검사(`review_policy.validate_scope_assessment`)도 통과해야 한다. 이 모듈은 한 응답이 두 층을 함께 통과함을 보인다. 또 제출 검사(`_payload_issues`)가 소비자와 같은 조건으로 거부하고 같은 조건으로 받아들이는지 확인한다. 끝으로 검토 저장과 행동 투영의 모양 두 가지, 그리고 확장된 범위를 개정할 때 이전 좌석을 유지하는 규칙을 검사한다.

## 모듈 수준 요소

- 행 9: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리다.
- 행 10–12: `contracts`, `execution_profiles`, `review_cycle`, `review_policy`, `DEFAULT_CONFIG`와 픽스처 `bare_engine`, `scope_response`를 import한다.
- 행 164–165: 직접 실행하면 `unittest.main()`으로 이 모듈의 시험을 돈다.

## ScopeWireTests (행 15–105)

`unittest.TestCase`를 그대로 상속하고 표지와 도우미 메서드가 없다.

`setUp` (행 43–56)은 원문에서 앞의 두 테스트 뒤에 정의되어 있지만, 클래스의 모든 테스트 앞에서 돈다. 만드는 것은 셋이다.
- `self.policy`: `build_review_policy(None, reviewer_count=2, max_rounds=2)`로 만든 기본 정책. ID는 `review-policy-v5-default`, 필수 관점 없음, 최소 초기 좌석 2, 판정 좌석 셋, 회차 상한 2다. 활동 실행 상한은 제품 식 `count + rounds * (count + len(judges) + 1)`에 따라 14다.
- `self.response`: 범위 응답. `summary`, 빈 `used_sources`와 `questions`에, `scope_response`가 만든 필드를 더한다. `scope_response`에는 정책, 제안 digest `fixture-proposal`, 그리고 `build_profiles(deepcopy(DEFAULT_CONFIG))`에서 고른 `identity_review` 역할 프로필을 넘긴다. 이 픽스처는 필수 관점이 없는 정책에 대해 관점 둘("Statement and proof", "Explanation and domain")로 초기 좌석 `initial-0`, `initial-1`을 채운다. 좌석마다 `required_source_refs=['proposal']`이다. 여기에 `selected_profile_ref`, 정책의 실행 상한과 초과 처분, `scope_complete=True`가 붙는다. 마지막으로 통합 묶음 `IN-scope`를 더한다.
- `self.wire`: 설치된 전송 스키마. `stage_schema("scope")`의 `proposal_digest`에 `enum: ["fixture-proposal"]`을 더하고, `with_integration_schema`로 감싼다. 행 52–53의 주석은 이것이 엔진의 `_response_schema`가 검토 좌석에 만드는 스키마와 같다고 밝힌다(`_review_schema`가 살아 있는 제안 digest를 묶고, 그 뒤 통합 봉투를 씌운다).

### `test_review_storage_keeps_local_source_alias_without_widening_source_records` (행 16–27)
- 성질: 검토 입력 기록(`review_inputs`)은 출처의 작업 공간 사본 경로(`local_path`)를 보존하지만, 출처 레코드 스키마는 그 필드를 받도록 넓어지지 않는다.
- 준비: 출처 레코드 `SO-input`(`notes.txt`, `sources/notes.txt`, 해시, 3바이트). 여기에 `local_path='input/sources/0000-notes.txt'`를 더한 `supplied`를 만든다. 준비된 검토 입력 `prepared`에는 제안 digest, 빈 제안과 요청, 좌석 `scope`, 작업 공간, `supplied_sources=[supplied]`, 출처 스냅숏이 들어 있다.
- 실행: `RECORDS['sources']`로 원 출처를 검증한다. `RUNTIME_FIELDS['review_inputs']`로 `{'RC-fixture:scope:1:scope': prepared}`를 검증한다. `RECORDS['sources']`로 `supplied`를 검증한다.
- 단언: 앞의 두 검증은 통과하고, 셋째는 `jsonschema.ValidationError`를 던진다. 예외 유형만 본다.
- 대역: 없음.
- 비고: 이 테스트는 `setUp`의 값을 쓰지 않는다. `prepared`는 `review_engine`이 검토 맥락을 만들 때 `runtime['review_inputs']`에 남기는 행(`review_engine.py` 행 646–653)의 필수 필드 여덟 개를 갖는다. 제품 행에 더 있는 `restored_messages`는 빠져 있는데, 스키마(`record_schemas/schemas.py` 행 702–705)는 그 필드를 선택으로 둔다.

### `test_review_action_keeps_replacement_authority_only_for_a_replacement` (행 29–41)
- 성질: 검토 좌석의 행동 투영(`review_action`)은 보통 좌석에서 실행의 권한 필드를 떼어 내고, 대체(replacement) 좌석에서만 대체 권한 필드를 유지한다.
- 준비: 실행 행동 `AC-execution`. 역할 `identity_review`, 단계와 좌석 `scope`, 회차 1, `grant_id='GR-running'`, `actor_kind='ai'`다. 대체 행동은 여기에 다섯 필드를 더한다: `replacement_for='initial-0'`, `grant_sha256`, `continuity_broken=True`, `purpose`, `continuity_break_cause`.
- 실행: 두 행동에 각각 `review_cycle.review_action`을 부른다.
- 단언: 보통 행동의 투영은 정확히 `{'stage': 'scope', 'slot': 'scope', 'round': 1}`이다. 대체 행동의 투영은 여덟 필드(`id`, `replacement_for`, `grant_id`, `grant_sha256`, `continuity_broken`, `actor_kind`, `purpose`, `continuity_break_cause`)가 원 값과 같다. 제품 docstring은 "Separate a review seat from the enclosing execution's authority fields."다.
- 대역: 없음.
- 비고: 이 테스트도 `setUp`의 값을 쓰지 않는다.

### `test_one_real_response_contract_reaches_the_consumer` (행 58–62)
- 성질: 전송 스키마를 통과한 범위 응답 하나가 봉투를 뺀 뒤 단계 스키마와 정책의 의미 검사도 통과한다.
- 준비: `setUp`의 `self.response`, `self.wire`, `self.policy`.
- 실행: 전송 스키마로 응답을 검증한다. `integration_bundles`를 뺀 `body`를 `stage_schema("scope")`로 검증한다. `validate_scope_assessment(body["scope_assessment"], self.policy)`를 부른다.
- 단언: 세 단계 모두 예외 없이 끝난다. 명시적 `assert` 없이 예외 부재로 단언한다.
- 대역: 없음.

### `test_submission_checks_scope_with_the_conditions_the_review_accepts` (행 64–94)
- 성질: 제출 검사는 범위 응답을 검토 소비자와 같은 조건으로 판정한다. 다른 정책의 평가는 둘 다 거부한다. 정직한 부분 읽기와 열린 질문은 둘 다 받아들이고, 그 내용이 봉인된 범위 결과로 모든 초기 좌석에 전달된다.
- 준비: `start_review({'revision': 1}, 2, max_rounds=2, policy=self.policy)`로 주기를 시작한다. `execution_accounting.executions_used`를 `['EX-scope']`로 둔다. 첫 행동(범위 좌석)을 얻어, `review_cycle_id='RC-fixture'`와 `role_review=context_for(cycle, action)`을 담은 맥락을 만든다. 전송 스키마는 이 주기의 실제 `proposal_digest`로 다시 묶는다. 응답은 `self.response`에 그 digest를 넣은 사본이다.
- 실행과 단언: 다섯 단계를 차례로 밟는다.
  1. `submission._payload_issues(response, wire, context, {}, 임시폴더)`의 결과가 `[]`다.
  2. `scope_assessment.policy_id`를 `'RP-other'`로 바꾼 응답의 문제 목록은 경로가 `['output']` 하나다. 문구는 고정하지 않는다. 제품의 제출 검사는 `identity_review` 행동에 대해 경로 `output`에서 `review_cycle.validate_visible_output`을 부르고(`submission.py` 행 988–990), 그 안의 `validate_scope_assessment`가 "scope assessment belongs to another review policy"로 거부한다.
  3. 같은 응답(봉투 제외)을 `accept_result(cycle, action, ..., 'EX-scope-result')`에 넣으면 `ValueError`가 난다.
  4. `scope_complete=False`와 `questions=['Which domain is intended?']`로 바꾼 응답의 제출 문제는 `[]`다.
  5. 4의 응답을 `accept_result`로 받아들이고, 다음 초기 행동의 `context_for(...)['completed_results']['scope:1:scope']`를 읽는다. 봉인된 출력의 `questions`가 `['Which domain is intended?']`이고, `scope_complete`는 `False` 자체다(`assertIs`).
- 단언: 위 다섯 단계에 단계별로 적었다. 요약하면 셋이다. 정상 응답은 제출 문제가 없다. 다른 정책의 평가는 제출 검사(경로 `output`)와 `accept_result` 모두에서 거부된다. 부분 읽기와 질문은 두 층 모두 받아들이고 봉인 결과에 보존된다.
- 대역: 없음.
- 비고: 행 85–86의 주석은 "정직한 부분 읽기와 열린 질문은 거부가 아니라 보고되며, 봉인된 범위 결과가 둘을 모든 초기 좌석에 싣는다"라고 밝힌다. `executions_used`를 1로 두면 `validate_scope_assessment`의 최소 실행 수 계산(`minimum_scope_executions`)에 이미 쓴 시도 1이 더해진다. 이 테스트에서 그 효과를 따로 단언하지는 않는다.

### `test_wire_rejects_missing_proposal_binding_and_invalid_scope_details` (행 96–105)
- 성질: 전송 스키마는 제안 digest 묶음이나 범위 완결 표시가 빠진 응답, 그리고 불완전한 범위 평가를 거부한다.
- 준비: `setUp`의 응답 사본.
- 실행: `proposal_digest`를 뺀 응답, `scope_complete`를 뺀 응답, `scope_assessment`를 `{"policy_id": self.policy["id"]}`만으로 바꾼 응답을 차례로 전송 스키마로 검증한다.
- 단언: 세 경우 모두 `jsonschema.ValidationError`를 던진다. 예외 유형만 본다.
- 대역: 없음.

## ExpandedScopeRevisionTests (행 108–163)

`unittest.TestCase`를 그대로 상속하고 훅과 도우미가 없다.

### `test_revision_retains_all_prior_slots_above_the_policy_minimum` (행 109–163)
- 성질: 정책 최소(2)보다 많은 좌석(3)으로 확장된 이전 검토를 개정하면, 새 검토는 이전 좌석을 모두 유지할 좌석으로 요청하고 범위 단계부터 다시 시작한다. 새 범위 평가가 유지할 좌석을 빼면 제출 검사와 수용 모두에서 거부된다.
- 준비:
  1. 기본 정책(`reviewer_count=2`, `max_rounds=2`)과 좌석 셋 `initial-0`, `initial-1`, `specialist`를 둔 범위 평가 `SA-expanded`를 만든다. 실행 상한은 정책 상한 14와 같다.
  2. `start_review({'id': 'KN-old', 'revision': 1}, 2, policy=policy, scope_assessment=scope)`로 이전 주기를 시작한다.
  3. 다음 행동마다 `decision='match'`, `scope_complete=True`인 결과를 `accept_result`로 넣어, 행동이 없을 때까지 진행한다.
  4. 이전 주기에 `id='RC-old'`, `knowledge_id='KN-old'`를 둔다.
  5. `bare_engine`으로 엔진을 만든다. 인스턴스는 `KN-new`(`supersedes='KN-old'`), 빈 설정, 정책을 갖고, 런타임은 `review_cycles={'RC-old': 이전 주기}`, head는 `fixed-input`이다.
- 실행:
  - 엔진 메서드 셋을 `create_autospec` 대역으로 바꾼다. `_settle_review_resource_dispositions`는 `None`을 돌려준다. `_review_publication_premises`는 `{}`를 돌려준다. `_queue_identity_actions`는 `(kid, cid)`를 `queued`에 기록한다.
  - `do_math.review_engine._proposal`(반환 `{'id': 'KN-new', 'revision': 2}`)과 `do_math.review_engine.kr.identity_basis`(반환 `{}`)를 패치한 채 `owner._start_identity_review('KN-new', previous_cycle_id='RC-old')`를 부른다.
  - 새 주기의 범위 행동과 그 가시 맥락(`context_for`)을 얻는다. 마지막 좌석을 뺀 범위 평가 `SA-next`로 `validate_visible_output`과 `accept_result`를 부른다.
- 단언:
  - 새 주기의 `retained_reviewer_slots`와 `requested_reviewer_slots`가 모두 세 좌석 목록이다.
  - `phase='scope'`, `results={}`, `decision is None`이다.
  - `previous_reviews[-1].decision`이 `'match'`다.
  - `queued`가 `[('KN-new', cid)]`다.
  - 가시 맥락의 `retained_reviewer_slots`가 세 좌석이다. `previous_reviews[-1].proposal`은 이전 주기의 `proposal`과 같다.
  - 좌석을 뺀 평가는 `validate_visible_output`과 `accept_result` 모두에서 `ValueError`를 던지고, 메시지가 정규식 `'retained logical slots'`에 맞는다. 제품 문구는 "new scope assessment cannot remove retained logical slots"다(`review_cycle._validate_content`).
- 대역: `create_autospec`으로 만든 엔진 메서드 대역 셋, `patch('do_math.review_engine._proposal', ...)`, `patch('do_math.review_engine.kr.identity_basis', ...)`, `bare_engine`의 메모리 상태 저장소 대역.
- 비고: 행 149–150의 주석은 범위 좌석이 유지할 좌석과 새 개정이 대체하는 제안을 받으므로, 공유 제출 검사가 중앙 수령 전에 좌석 제거를 거부한다고 밝힌다. 제품 `_start_identity_review`는 이전 주기에 `reviewer_slots`가 있으면 그 목록을 새 주기의 검토자 좌석으로 넘긴다.

## 관계

- 같은 제품 기능의 다른 층: 범위 평가의 의미 규칙(필수 관점, 예약 좌석 이름, 공백 텍스트, 최소 실행 수)은 `test_review_policy`가 검사한다. 이 모듈은 전송 스키마, 제출 검사, 소비자의 일치를 본다. 범위 단계 스키마에 `scope_assessment.initial_slots`가 있는지는 `test_contracts.test_scope_planning_schema_reaches_domain_scope_validator`가 본다. 검토 주기의 전체 단계 진행은 `test_review_cycle`이 본다.
- 픽스처 의존: `research_fixtures.scope_response`(정책의 최소 좌석을 채우는 범위 응답 본문), `research_fixtures.bare_engine`.
- 이 모듈에만 있는 도우미: 없다. `setUp`의 전송 스키마 구성이 이 모듈 고유의 준비다.
- 겹치거나 보완하는 시험: `test_review_policy.test_scope_assessment_rejects_a_blank_text_as_the_scope_wire_does`는 이름대로 전송 스키마와 같은 공백 거부를 의미 검사 쪽에서 확인한다. 이 모듈의 `test_submission_checks_scope_with_the_conditions_the_review_accepts`는 반대로 제출 검사가 소비자와 같은 조건을 쓰는지 확인한다.

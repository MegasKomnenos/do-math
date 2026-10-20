# test_review_policy

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_review_policy.py` (232행) |
| 클래스 / 테스트 | 1 / 12 |
| 시험 대상 제품 코드 | `do_math/review_policy.py`의 `build_review_policy`, `validate_scope_assessment`, `minimum_scope_executions`; `do_math/review_cycle.py`의 `start_review`, `next_actions`, `accept_result`, `context_for`, `record_recovery_event`, `authorize_record_replacement`; `do_math/input_basis.py`의 `capture_review_input_basis`, `review_input_basis_changes`; `do_math/review_engine.py`의 `_start_identity_review`, `_prepare_review_context`, `_record_review_recovery`; 계약 문서 `계약/동일성-검토.md` |
| 사용하는 픽스처 모듈 | `review_fixtures`: `ReviewFakeEngine`, `grant_replacement` |
| 격리 표지 | 없음 |
| 시작 상태 | 대부분 1단(정책과 검토 주기 순수 함수를 직접 호출). 엔진을 쓰는 세 테스트(`test_permanent_restoration_loss_blocks_its_slot_until_a_current_grant_authorizes_a_replacement`의 권한 부분, `test_engine_freezes_adopted_policy_and_opens_every_review_at_its_scope_stage`, `test_engine_returns_a_structured_slot_recovery_instead_of_reraising_restore_failure`)는 네 단 밖의 `review_fixtures.ReviewFakeEngine`(저장소 없는 제품 엔진 하위 클래스)을 쓴다 |

## 목적

모듈 docstring은 이 모듈이 검토 정책과 범위를 시험한다고 밝힌다. 대상은 범위 단계, 필수 관점과 좌석, 그리고 각 검토 단계가 고정되는 입력이다. `review_policy.py`의 docstring은 "Versioned policy and independent scope contracts for identity review."이다. 동일성 검토는 독립 범위 단계로 시작한다. 범위 평가(`scope_assessment`)는 정책 아래에서 필수 관점, 초기 좌석, 선택 프로필, 활동 실행 상한을 정한다. 정해진 값은 주기에 고정되고, 입력 기준(`review_input_basis`)으로 봉인되어 이후의 변화를 감지하게 한다. 이 모듈은 여섯 가지를 검사한다.
1. 범위 단계에서 초기 검토, 조직, 판정으로 이어지는 진행.
2. 범위 평가의 의미 규칙: 관점 누락, 예약 좌석 이름, 공백 텍스트, 추가 관점.
3. 영구 복원 손실 뒤의 좌석 차단과 권한 있는 대체.
4. 입력 기준의 변화 감지.
5. 엔진이 채택 정책을 고정하는지와 복원 실패를 구조화된 회복으로 돌려주는지.
6. 계약 문서의 최소 실행 수 공식과 코드의 일치.

## 모듈 수준 요소

- 행 8: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리다.
- 행 10–14: 검토 주기 함수, 정책 함수, 입력 기준 함수와 픽스처 `ReviewFakeEngine`, `grant_replacement`를 import한다.
- `policy()` (행 17–26): `build_review_policy`에 명시 정책을 넘겨 검증된 사본을 돌려준다. ID `RP-identity-v5`, 필수 관점 `formal`과 `semantic`, 최소 초기 좌석 2, 판정 좌석 `judge-0`–`judge-2`, 회차 상한 2, 활동 실행 상한 12, 초과 처분 `unresolved`다. `test_scope_execution_minimum_in_the_review_contract_matches_the_policy`를 뺀 모든 테스트가 쓴다.
- `assessment()` (행 29–41): 이 정책에 맞는 범위 평가 `SA-1`. 필수 관점 두 개를 그대로 두고, 초기 좌석 둘(`initial-formal`/`formal`, `initial-semantic`/`semantic`)은 모두 `required_source_refs=['proposal']`이다. 선택 프로필은 `EP-review` 개정 1, 실행 상한 12, 초과 처분 `unresolved`다. 대부분의 테스트가 쓴다. 이 평가의 최소 실행 수는 `minimum_scope_executions(2, 2, 0)` = 2 + 1 + 2 + 6 = 11이므로 상한 12를 넘지 않는다.
- 행 231–232: 직접 실행하면 `unittest.main()`으로 이 모듈의 시험을 돈다.

## ReviewScopeTests (행 44–228)

`unittest.TestCase`를 그대로 상속하고 표지, 설정 훅, 클래스 도우미가 없다. 엔진을 쓰는 두 테스트는 테스트 안에서 `self.directory`에 임시 폴더를 두고 `addCleanup`으로 정리한다.

### `test_missing_scope_opens_an_independent_scope_action_before_initial_reviews` (행 45–55)
- 성질: 범위 평가 없이 시작한 검토는 초기 검토보다 앞서 독립된 범위 행동 하나를 연다. 범위 결과를 받으면 평가가 정한 초기 좌석으로 넘어간다.
- 준비: `start_review({"revision": "r1"}, reviewers=2, policy=policy())`.
- 실행: `next_actions(cycle)`로 범위 행동을 얻고, `assessment()`를 담은 범위 결과를 `accept_result(..., "scope-execution")`로 넣는다.
- 단언: 시작 주기의 `phase`가 `"scope"`다. 행동 목록이 정확히 `[{"stage": "scope", "slot": "scope", "round": 1}]`이다. 수용 뒤 `phase`는 `"initial"`이다. 다음 행동 좌석이 `["initial-formal", "initial-semantic"]`이다.
- 대역: 없음.

### `test_scope_then_initial_organization_and_independent_judgment_use_only_sealed_stages` (행 57–94)
- 성질: 범위, 초기 검토, 조직, 판정의 네 단계가 차례로 진행되고, 판정 좌석은 봉인된 이전 단계 결과를 받는다. 모든 이의가 승인되면 주기는 불일치로 완료된다.
- 준비: 정책으로 시작해 범위 결과를 넣는다.
- 실행: 네 단계를 차례로 밟는다.
  1. 초기 좌석마다 발견 하나(`<slot>-finding`, 증거 `proposal`)와 `decision='mismatch'`를 넣는다.
  2. 조직 행동에서 발견마다 별도 쟁점(`issue-<slot>`)을 만들고, 답변 좌석을 그 발견의 좌석으로 둔다.
  3. 판정 행동들을 얻어 각 맥락의 `completed_results`를 확인한다.
  4. 판정 좌석마다 모든 쟁점을 `approved`로 판정하고 `decision='mismatch'`를 넣는다.
- 단언: 조직 행동의 `stage`가 `"organize"`다. 판정 행동들의 단계 집합이 `{"judge"}`다. 모든 판정 행동의 `context_for(...)["completed_results"]`가 비어 있지 않다. 마지막 `(status, decision)`이 `("completed", "mismatch")`다.
- 대역: 없음.
- 비고: 이름의 "use only sealed stages"는 판정 맥락에 완료 결과가 있다는 것만으로 확인한다. 봉인되지 않은 값이 없다는 음성 단언은 하지 않는다.

### `test_scope_assessment_freezes_required_slots_profile_and_activity_budget` (행 96–103)
- 성질: 범위 평가를 주고 시작한 주기는 평가의 좌석, 정책, 선택 프로필, 활동 실행 상한, 필수 출처를 고정하고 곧바로 초기 좌석을 연다.
- 준비: `start_review(..., policy=policy(), scope_assessment=assessment())`.
- 실행: 주기 필드와 `next_actions`를 읽는다.
- 단언: 여섯 값을 확인한다.
  - `reviewer_slots`가 `["initial-formal", "initial-semantic"]`이다.
  - `review_policy.id`가 `"RP-identity-v5"`다.
  - `scope_assessment.selected_profile_ref.id`가 `"EP-review"`다.
  - `activity_execution_limit`이 12다.
  - `required_source_refs`가 `["proposal"]`이다.
  - 다음 행동의 좌석 집합이 두 초기 좌석이다.
- 대역: 없음.

### `test_scope_assessment_rejects_missing_required_perspective` (행 105–109)
- 성질: 범위 평가는 정책의 필수 관점을 빠뜨릴 수 없다.
- 준비: `assessment()`의 `required_perspectives`를 `["formal"]`로 줄인다.
- 실행: `validate_scope_assessment(invalid, policy())`.
- 단언: `ValueError`이고 메시지가 정규식 `"required perspective"`에 맞는다. 제품 문구는 "scope assessment omits a required perspective"다.
- 대역: 없음.

### `test_executed_scope_cannot_merge_initial_and_private_judge_slots` (행 111–121)
- 성질: 실행된 범위 결과는 초기 좌석에 범위, 조직, 판정 좌석의 이름을 쓸 수 없다. 독립 역할 좌석을 합치면 안 된다.
- 준비: 새 주기마다 `assessment()`의 첫 초기 좌석 ID를 예약 이름으로 바꾼다.
- 실행: 범위 행동에 그 평가를 담은 결과를 `accept_result`로 넣는다.
- 단언: `ValueError`이고 메시지가 정규식 `'role slot'`에 맞는다. 제품 문구는 "scope assessment reuses an independent role slot"이다.
- 대역: 없음.
- 비고: `subTest(slot=...)`의 세 케이스는 `'scope'`, `'organize'`, `'judge-0'`이다. 수용 경로(`accept_result`)를 거치므로, 직접 검증이 아니라 실행된 범위 결과로 확인한다.

### `test_scope_assessment_rejects_a_blank_text_as_the_scope_wire_does` (행 123–127)
- 성질: 의미 검사는 전송 스키마와 같이 공백만 있는 텍스트를 거부하고, 문제 좌표를 알려 준다.
- 준비: 첫 초기 좌석의 `perspective`를 `'   '`로 바꾼다.
- 실행: `validate_scope_assessment(invalid, policy())`.
- 단언: `ValueError`이고 메시지가 좌표 `'scope_assessment/initial_slots/0/perspective'`를 포함한다(정규식). 제품은 공유 모양 `SCOPE_ASSESSMENT`를 `validate_record(_SCOPE_CHECKER, assessment, "scope_assessment")`로 먼저 검사한다. 행 15–16의 제품 주석은 범위 단계의 전송 스키마가 같은 모양을 싣는다고 밝힌다.
- 대역: 없음.

### `test_scope_added_expertise_requires_an_actual_assigned_slot` (행 129–133)
- 성질: 범위 평가가 필수 관점을 더하면, 그 관점을 맡은 초기 좌석이 실제로 있어야 한다.
- 준비: `assessment()`의 `required_perspectives`에 `'number theory'`를 더한다. 좌석은 그대로 둔다.
- 실행: `validate_scope_assessment(invalid, policy())`.
- 단언: `ValueError`이고 메시지가 정규식 `'required perspective'`에 맞는다. 제품 문구는 "scope assessment has no slot for a required perspective"다.
- 대역: 없음.
- 비고: 이 테스트와 `test_scope_assessment_rejects_missing_required_perspective`는 같은 정규식을 쓴다. 두 제품 문구 모두 그 조각을 담으므로, 어느 거부 사유인지는 정규식만으로 구별되지 않는다.

### `test_permanent_restoration_loss_blocks_its_slot_until_a_current_grant_authorizes_a_replacement` (행 135–174)
- 성질: 재시도 가능한 복원 실패는 좌석을 그대로 둔다. 영구 손실은 그 좌석을 연속성 단절로 막고, 현재 부여(grant)가 권한을 줄 때만 기록 기반 대체를 허용한다. 대체 결과는 입력 매니페스트가 단절과 권한을 밝혀야 받아들여진다.
- 준비: 범위 평가를 주고 시작한 주기와 첫 초기 행동 `action`.
- 실행과 단언: 다섯 단계로 진행한다.
  1. `record_recovery_event(cycle, action, {"reason": "source_read_error", "retryable": True, ...})`. 결과 `status`는 `"working"`이고, 다음 행동이 원래 두 행동 `[action, next_actions(cycle)[1]]`과 같다.
  2. 이어서 `reason='permanent_loss'`, `retryable=False`로 기록한다. `(status, decision)`은 `("working", None)`이다. 마지막 `continuity_events`의 `reason`이 `"permanent_loss"`이고 `continuity_broken`이 참이다. 다음 행동 좌석은 `["initial-semantic"]`뿐이다. 막힌 좌석이 빠진다.
  3. 주기에 `id='RC-test'`, `knowledge_id='K1'`을 두고 런타임을 만든다. `authorize_record_replacement(permanent, action, {"grants": {}}, runtime=runtime)`의 `disposition`이 `"authorization_denied"`다.
  4. 임시 폴더에 `ReviewFakeEngine`을 만들고 `grant_replacement(engine)`로 부여 `GR-review`를 적용한다. 이 부여는 `identity_review` 역할, 대상 `K1`, 목적 `record_replacement`의 지역 부여다. 그 인스턴스로 `authorize_record_replacement(..., grant_id="GR-review")`를 부르면 `disposition`이 `"replacement_ready"`다. 대체 행동의 `continuity_broken`이 참이고, 대체 맥락의 `replacement.grant_id`가 `"GR-review"`다.
  5. 대체 결과를 입력 매니페스트 없이 `accept_result`에 넣으면 `ValueError`이고 메시지가 `"continuity break"`에 맞는다. 제품 문구는 "replacement input manifest omits its continuity break"다. 매니페스트 `{"replacement_for", "grant_id": "GR-review", "grant_sha256"}`를 주면 받아들여지고, 마지막 `replacement_receipts`의 `execution_id`가 `"replacement-run"`이다.
- 단언: 위 다섯 단계에 단계별로 적었다. 요약하면 넷이다. 재시도 가능 실패는 좌석을 유지한다. 영구 손실은 좌석을 막는다. 부여가 없으면 `authorization_denied`, 부여가 있으면 `replacement_ready`다. 대체 결과는 단절과 권한을 밝힌 매니페스트로만 받아들여진다.
- 대역: `review_fixtures.ReviewFakeEngine`(부여 결정을 적용할 인스턴스를 만드는 데만 쓴다).
- 비고: 엔진은 `with tempfile.TemporaryDirectory()` 블록 안에서 만들고, 그 뒤에는 `engine.instance`만 쓴다.

### `test_review_input_basis_detects_policy_scope_and_profile_drift` (행 176–182)
- 성질: 검토 입력 기준은 선택 프로필의 변화를 `selected_profile_ref` 필드의 변화로 정확히 보고한다.
- 준비: 범위 평가를 주고 시작한 주기와 `capture_review_input_basis(cycle)`.
- 실행: 같은 주기로 `review_input_basis_changes`를 부른다. 이어서 `scope_assessment.selected_profile_ref.revision`을 2로 바꾼 사본으로 다시 부른다.
- 단언: 같은 주기는 `[]`다. 바꾼 사본의 첫 변화 `field`는 `"selected_profile_ref"`다.
- 대역: 없음.
- 비고: 이름은 정책, 범위, 프로필의 변화를 말하지만 단언은 프로필 변화 하나만 본다. 제품은 `review_policy`, `scope_assessment`, `owner_activity_id`, `activity_execution_limit`, `identity_basis`, `policy_ref`, `publication_premises`를 고정한다.

### `test_engine_freezes_adopted_policy_and_opens_every_review_at_its_scope_stage` (행 184–194)
- 성질: 엔진이 여는 동일성 검토는 인스턴스가 채택한 정책을 주기와 입력 기준에 고정하고, 범위 단계에서 시작한다.
- 준비: `ReviewFakeEngine`을 만든다. 이 엔진은 후보 정리 `K1`, 검증된 형식 증거, 합성 신뢰 환경을 갖는다. 인스턴스의 `review_policy`를 `policy()`로 바꾼다.
- 실행: `engine._start_identity_review("K1")`.
- 단언: 주기의 `review_policy`가 `policy()`와 같다. `(phase, scope_assessment, owner_activity_id)`가 `("scope", None, None)`이다. `review_input_basis.values.review_policy`가 `policy()`와 같다. 대기열 행동의 `(stage, slot)` 목록이 `[("scope", "scope")]`이다.
- 대역: `ReviewFakeEngine`. 그 `_save`는 자동 명세 대역이고, 저장소 읽기는 `FileNotFoundError`를 던지는 `_no_artifacts`다.

### `test_engine_returns_a_structured_slot_recovery_instead_of_reraising_restore_failure` (행 196–211)
- 성질: 좌석의 대화 기록 복원이 실패하면, 엔진은 예외를 다시 던지지 않고 구조화된 회복 처분을 돌려준다. 주기는 계속 작업 중으로 남는다.
- 준비: `ReviewFakeEngine`에 `policy()`를 채택하고, `engine.start("K1", scope=assessment())`로 초기 좌석부터 시작한다. 대기열의 첫 `identity_review` 행동의 좌석에 대화 기록 하나(`message_id='lost'`)를 두고, 그 전사 매니페스트 행의 `sha256`을 `"wrong"`으로 둔다.
- 실행: 임시 작업 공간으로 `engine._prepare_review_context(action, workspace)`.
- 단언: 반환 `disposition`이 `"recovery_recorded"`이고, `recovery.disposition`이 `"replacement_authorization_required"`다. `recovery.recovery_event.retryable`은 거짓이다. 주기 `status`는 `"working"`이다.
- 대역: `ReviewFakeEngine`.
- 비고: 제품 `_prepare_review_context`의 docstring은 "A failed reconstruction is already durable state, not an exception that should escape and be retried as though nothing had been recorded."라고 밝힌다. 복원 오류(`ReviewRestorationError`)는 `_record_review_recovery`로 기록되고, 재시도 불가이면 다음 소유자가 `governance`가 된다.

### `test_scope_execution_minimum_in_the_review_contract_matches_the_policy` (행 213–228)
- 성질: 동일성 검토 계약 문서에 적힌 최소 실행 수 공식(한 회차 `U+N+4`, 두 회차 이상 `U+2N+7`)은 검사 코드가 실제로 쓰는 함수와 같다(docstring).
- 준비: 실제 설치본의 `계약/동일성-검토.md`를 읽는다.
- 실행: 정규식으로 두 문장을 찾는다. `'한 회차의 하한은 U+<계수>N+<상수>'`와 `'두 회차 이상의 하한은 U+<계수>N+<상수>'`다. 계수가 비어 있으면 1로 읽는다. 회차 상한 `(1,)`과 `(2, 3, 5)`, 이미 쓴 시도 `0`과 `2`, 좌석 수 `1`과 `3`의 모든 조합에 대해 `minimum_scope_executions(slots, round_limit, used)`를 계산한다.
- 단언: 두 문장이 모두 발견된다(`assertIsNotNone`, 메시지는 문장 머리). 모든 조합에서 함수 값이 `used + 계수*slots + 상수`와 같다. 실패 메시지는 `(round_limit, used, slots)`다.
- 대역: 없음.
- 비고: 제품 식은 `executions_used + initial_slots + 1 + (3 if round_limit == 1 else initial_slots + 6)`이다. 곧 한 회차는 U+N+4, 그 밖은 U+2N+7이다. 이 테스트는 문서와 코드가 어긋나면 실패하는 문서-코드 일치 감시다.

## 관계

- 같은 제품 기능의 다른 층: 범위 응답의 전송 스키마와 제출 검사, 확장된 범위의 개정은 `test_review_scope_wire`가 본다. 검토 주기 전체의 단계 규칙(만장일치, 차단, 회차 상한, 전사 복원)은 `test_review_cycle`이 본다. 엔진 층의 동일성 검토 흐름은 `test_review_engine`이 넓게 다룬다.
- 픽스처 의존: `review_fixtures.ReviewFakeEngine`, `review_fixtures.grant_replacement`. `ReviewFakeEngine`은 내부에서 `research_fixtures.trust_fixture`, `trust_environment`로 합성 신뢰 환경을 만든다.
- 이 모듈에만 있는 도우미: 모듈 함수 `policy()`, `assessment()`.
- 겹치거나 보완하는 시험: 범위 평가의 예약 좌석 이름은 이 모듈이 수용 경로에서 본다. `start_review`에 직접 넘긴 좌석의 중복, 판정 좌석과의 이름 충돌, 판정자 수는 `test_review_cycle.test_allocation_duplicates_and_judge_count`가 본다. 복원 실패는 이 모듈이 엔진 처분을 보고, `test_review_cycle.test_transcript_restore_reference_and_integrity`가 주기 층의 복원 무결성을 본다.

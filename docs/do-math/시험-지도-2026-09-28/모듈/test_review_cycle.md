# test_review_cycle

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_review_cycle.py` (381행) |
| 클래스 / 테스트 | 2 / 24 |
| 시험 대상 제품 코드 | `do_math/review_cycle.py`의 `start_review`, `next_actions`, `stage_schema`, `accept_result`(내부 `_validate_content`, 입력 매니페스트 검사), `context_for`, `record_turn`, `validate_transcript`, `ReviewRestorationError`, `validate_review_independence`, `defer_for_research`, `accept_research_result`, `record_recovery_event`, `validate_sealed_review`; `do_math/review_engine.py`의 `_authorize_review_replacement`; `do_math/execution_profiles.py`의 `build_profiles`, `profile_ref` |
| 사용하는 픽스처 모듈 | `review_fixtures`: `scoped_start`, `review_stage_output`, `deferred_research_cycle`, `research_answer`, `ReviewFakeEngine`, `grant_replacement` |
| 격리 표지 | 없음 |
| 시작 상태 | 1단(검토 주기 순수 함수에 사전 상태를 넘김). 예외로 `SealedReplayTests.test_authorized_replacement_keeps_full_authority_and_sealed_input`은 네 단 밖의 `review_fixtures.ReviewFakeEngine`(저장소 없는 제품 엔진 하위 클래스)을 쓴다 |

## 목적

모듈 docstring은 없다. 이 모듈은 동일성 검토의 유한 주기(`review_cycle`)를 순수 함수 수준에서 검사한다. 주기는 다섯 단계로 흐른다: 범위(scope), 초기 검토(initial), 조직(organize), 답변(answer), 판정(judge). 초기 검토자들은 서로의 결과를 보지 않고 판정한다. 모두 일치(`match`)하면 끝나고, 불일치 발견이 있으면 조직자가 쟁점을 만든다. 판정자 셋이 쟁점을 판정하며, 기각된 쟁점은 원래 좌석의 답변으로 돌아가 회차 상한까지 반복된다. `start_review`의 docstring은 "The engine always opens at the scope stage. A given scope_assessment is the replay of an accepted scope (validate_sealed_review) or a test's start state."라고 밝힌다. 그래서 이 모듈의 대부분은 `scoped_start`로 범위가 이미 정해진 주기에서 시작한다.

`ReviewCycleTests`는 주기의 단계 규칙을 검사한다. 대상은 만장일치, 순수성, 초기 차단과 비공개, 조직자의 위조 방지, 판정 집계, 회차 상한, 답변과 분할, 개정 재시작, 독립성, 전사 복원, 입력 매니페스트다. `SealedReplayTests`는 끝난 검토를 봉인된 증거로 다시 재생하는 `validate_sealed_review`를 검사한다. 대상은 조사 예산 종료, 권한 있는 대체, 이전 검토의 보존, 고정 조사 결과의 재생이다.

## 모듈 수준 요소

- 행 7: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리다.
- 행 8–10: `review_cycle`의 `start_review`, `next_actions`, `stage_schema`, `accept_result`, `context_for`, `record_turn`, `validate_review_independence`와 `review_fixtures`의 `deferred_research_cycle`, `grant_replacement`, `research_answer`, `review_stage_output`, `ReviewFakeEngine`, `scoped_start`를 import한다.
- 행 380–381: 직접 실행하면 `unittest.main()`으로 이 모듈의 시험을 돈다.

## ReviewCycleTests (행 13–276)

`unittest.TestCase`를 그대로 상속하고 표지와 설정 훅이 없다. 원문에서 첫 테스트가 도우미보다 앞에 놓여 있다. 도우미 메서드는 넷이다.

- `start(**kw)` (행 20–21): `scoped_start`로 범위가 정해진 주기를 연다. 제안은 `{'revision': 'r1', 'proof': 'original', 'producer_execution_ids': ['author']}`이고 검토자는 2명이다. `scoped_start`는 좌석 `initial-0`, `initial-1`, 판정 좌석 `judge-0`–`judge-2`, 회차 상한(기본 3), 정책 `test-policy-v5`와 그 범위 평가를 만든 뒤 `start_review`를 부른다. `kw`는 `max_rounds` 등을 넘긴다.
- `submit(cycle, **changes)` (행 23–25): 다음 행동 하나에 `review_stage_output`의 기본 출력(바뀐 필드 포함)을 실행 ID `e-<결과 수>`로 `accept_result`에 넣는다. 기본 출력은 단계별로 다르다: 초기는 일치, 조직은 대기 발견마다 쟁점 하나, 답변은 모든 이의 유지, 판정은 모든 쟁점 승인과 불일치다.
- `disputed(**kw)` (행 27–31): 쟁점 하나가 판정을 기다리는 주기를 만든다. 첫 초기 검토는 발견 `f1`("Quantifier is reversed")로 불일치를 내고, 둘째는 일치를 낸다. 조직자는 그 발견을 쟁점 `i0`으로 만든다.
- `judges(cycle, vote='approved', decision='mismatch', extra=None)` (행 33–39): 판정자 셋이 차례로 모든 쟁점에 같은 표(`vote`)를 던지게 한다. `extra`가 있으면 그 필드를 더한다.

### `test_incomplete_transcript_manifest_is_a_local_restoration_error` (행 14–18)
- 성질: 좌석 전사의 매니페스트 행이 불완전하면, 그 좌석의 맥락 복원은 전사 복원 오류로 실패한다.
- 준비: `start()` 뒤 `record_turn`으로 `initial-0`에 메시지 하나를 기록하고, 그 매니페스트 첫 행에서 `sha256`을 뺀다.
- 실행: 첫 대기 행동에 대해 `context_for`를 부른다.
- 단언: `ValueError`이고 메시지가 정규식 `'transcript'`에 맞는다. 제품 `validate_transcript`는 이 경우 "transcript restoration manifest is incomplete"(`cause_kind='invalid_manifest'`)로 `ReviewRestorationError`를 던진다.
- 대역: 없음.
- 비고: 이름은 "local restoration error"를 말하지만, 단언은 `ValueError`와 메시지 조각만 본다. `ReviewRestorationError`는 `ValueError`의 하위 클래스이며, 그 유형은 단언하지 않는다.

### `test_initial_unanimity_and_purity` (행 41–51)
- 성질: 초기 검토자 둘이 모두 일치하면 주기가 일치로 완료된다. `accept_result`는 입력 주기를 바꾸지 않고 JSON으로 왕복 가능한 새 주기를 돌려준다.
- 준비: `start()`와 그 `deepcopy`.
- 실행: 일치 결과를 한 번 넣어 `partial`을 얻고, 한 번 더 넣어 `done`을 얻는다.
- 단언: 원 주기는 사본과 같다(순수성). `partial.phase`는 `'initial'`이고 대기 행동은 1개다. `done`의 `(status, decision)`은 `('completed', 'match')`이고 대기 행동은 `[]`다. `json.loads(json.dumps(done))`이 `done`과 같다.
- 대역: 없음.

### `test_initial_barrier_and_blindness` (행 53–59)
- 성질: 초기 검토는 서로 차단된다. 한 검토자의 불일치 발견은 다른 초기 검토자의 맥락에 보이지 않는다.
- 준비: `start()` 뒤 첫 초기 검토가 발견 `'secret finding'`으로 불일치를 낸다.
- 실행: 남은 초기 행동의 `context_for`.
- 단언: 맥락의 `completed_results`, `issues`, `pending_findings`가 모두 비어 있고, 맥락 JSON에 `'secret finding'`이 없다.
- 대역: 없음.

### `test_scope_false_match_rejected_and_incomplete_not_reviewed` (행 61–68)
- 성질: 범위를 다 읽지 못한 검토는 일치를 낼 수 없고, 불완전 판정은 조직이나 판정으로 넘어가지 않고 미해결로 끝난다.
- 준비: `start()`.
- 실행: `scope_complete=False`인 일치 결과를 넣는다. 이어서 `decision='unresolved'`, `scope_complete=False`인 결과와 기본 일치 결과를 차례로 넣는다.
- 단언: 첫 제출은 `ValueError`이고 메시지가 `'complete scope'`에 맞는다(제품 "match requires complete scope"). 끝난 주기의 `status`는 `'unresolved'`이고 대기 행동은 `[]`다.
- 대역: 없음.

### `test_organizer_omission_forgery_and_owner_checks` (행 70–85)
- 성질: 조직자는 대기 중인 발견을 빠뜨리거나, 위조하거나, 중복시키거나, 답변 좌석을 원 소유자가 아닌 좌석으로 바꿀 수 없다. 두 초기 검토자가 같은 지역 ID를 써도 두 쟁점으로 구별된다.
- 준비: `start()` 뒤 두 초기 검토가 모두 불일치를 낸다. 발견은 같은 지역 ID `f1`로 서로 다른 내용이다. 유효한 조직 출력은 `review_stage_output(cycle, 'organize')`로 만든다.
- 실행: 네 변조를 각각 `accept_result(..., 'org')`에 넣는다.
  - `omit`: 마지막 쟁점을 뺀다.
  - `forge`: 첫 쟁점의 발견 참조 `id`를 `'fabricated'`로 바꾼다.
  - `duplicate`: 첫 쟁점을 복제한다.
  - `owner`: 첫 쟁점의 `answer_role_slot_id`를 `'initial-1'`로 바꾼다.
  마지막으로 유효 출력을 넣는다.
- 단언: 네 변조는 모두 `ValueError`다. 예외 유형만 보고 메시지는 고정하지 않는다. 유효 출력 뒤 `phase`는 `'judge'`이고 쟁점은 2개다.
- 대역: 없음.
- 비고: `subTest(mutate=...)`의 네 케이스는 `omit`, `forge`, `duplicate`, `owner`다.

### `test_approved_objection_closes_mismatch` (행 87–90)
- 성질: 판정자 셋이 모두 승인한 이의는 주기를 불일치로 닫는다.
- 준비: `disputed()`.
- 실행: `judges(...)`(모두 승인, 불일치).
- 단언: `(status, decision)`이 `('completed', 'mismatch')`이고, 쟁점 `i0`의 `status`가 `'approved'`다.
- 대역: 없음.

### `test_rejection_returns_to_original_slot_and_same_judges` (행 92–103)
- 성질: 기각된 이의는 다음 회차에 원래 발견을 낸 좌석의 답변으로 돌아가고, 답변 뒤에는 같은 판정자 셋이 새 판본을 판정한다.
- 준비: `disputed(max_rounds=2)` 뒤 판정자 셋이 모두 기각한다(판정은 `match`).
- 실행: 답변 행동의 맥락을 읽는다. 답변 `withdraw`(쟁점 `i0`)를 넣는다. 판정자 셋이 다시 기각한다.
- 단언:
  - 다음 행동이 정확히 `[{'stage': 'answer', 'slot': 'initial-0', 'round': 2}]`다.
  - 답변 맥락의 완료 결과 가운데 판정 단계가 3개다.
  - `self_messages`에 `role='assistant'`인 메시지가 있다. 좌석 자신의 이전 대화가 복원된다.
  - 답변 뒤 `phase`는 `'judge'`이고, 판정 좌석은 `['judge-0', 'judge-1', 'judge-2']`이며, 쟁점 `i0`의 `version`은 2다.
  - 재판정 뒤 `decision`은 `'match'`다.
- 대역: 없음.

### `test_partial_judges_never_aggregate_or_leak` (행 105–113)
- 성질: 판정자 일부만 판정한 상태에서는 집계되지 않고, 다른 판정자의 표가 새지 않는다. 빈 판정은 거부된다.
- 준비: `disputed()` 뒤 판정자 한 명이 판정한다.
- 실행: 다음 판정 행동의 맥락을 읽고, `issue_verdicts=[]`인 판정을 넣는다.
- 단언: `status`는 `'working'`이다. 맥락의 완료 결과에 판정 단계가 없다. 쟁점 `i0`의 `verdicts`는 `[]`다. 빈 판정은 `ValueError`다. 예외 유형만 본다.
- 대역: 없음.

### `test_judge_new_findings_get_organizer_assignment_and_answer` (행 115–129)
- 성질: 판정자가 낸 새 발견은 판정 회차가 끝난 뒤 다음 회차의 조직자에게 배정되고, 답변을 거쳐 판정된다.
- 준비: `disputed(max_rounds=2)`.
- 실행: 여러 단계를 차례로 밟는다.
  1. 첫 판정자가 새 발견 `j1`을 내고, 나머지 두 판정자가 판정한다.
  2. 조직 맥락의 첫 대기 발견 참조 `source`를 읽는다.
  3. 조직, 답변을 넣는다.
  4. 판정자 셋이 승인한다.
- 단언:
  - 첫 판정 직후 주기의 `pending_findings`는 `[]`다. 회차가 끝나기 전에는 드러나지 않는다.
  - 세 판정 뒤 `(phase, round)`는 `('organize', 2)`다.
  - `source`의 `(stage, slot)`은 `('judge', 'judge-0')`이다.
  - 조직 뒤 다음 행동은 `[{'stage': 'answer', 'slot': 'initial-0', 'round': 2}]`다. 픽스처 조직자는 판정 단계 발견을 `initial-0`에 배정한다.
  - 최종 `decision`은 `'mismatch'`이고, 쟁점 `i1`의 첫 발견 참조가 `source`와 같다.
- 대역: 없음.

### `test_round_limit_split_votes_unresolved_and_last_rejection` (행 131–141)
- 성질: 회차 상한에 이른 판정에서 표가 갈리면 주기는 미해결로 끝나고 후속을 남긴다. 마지막 회차에서 모두 기각하면 일치로 끝난다.
- 준비: 두 개의 `disputed(max_rounds=1)`.
- 실행: 첫 주기에서는 판정자가 차례로 승인, 기각(`match`), 승인을 던진다. 둘째 주기에서는 셋 모두 기각한다.
- 단언: 첫 주기의 `decision`은 `'unresolved'`, 대기 행동은 `[]`이고 `followup`이 참이다. 둘째 주기의 `decision`은 `'match'`, `round`는 1이다.
- 대역: 없음.

### `test_new_finding_at_cap_cannot_be_approved` (행 143–149)
- 성질: 회차 상한에서 판정자가 낸 새 발견은 판정받을 수 없으므로, 주기는 미해결로 끝나고 발견은 대기로 남는다.
- 준비: `disputed(max_rounds=1)`.
- 실행: 첫 판정자가 새 발견 `new`를 내고, 나머지 두 판정자가 판정한다.
- 단언: `decision`은 `'unresolved'`이고, `pending_findings`가 비어 있지 않다.
- 대역: 없음.

### `test_answer_new_findings_and_split_reach_fresh_judgment` (행 151–169)
- 성질: 답변이 이의를 분할(`split`)하려면 파생 발견이 둘 이상이어야 한다. 분할과 독립 발견은 새 쟁점이 되어 같은 좌석에 배정되고, 이전 회차의 표로는 이번 회차를 채울 수 없다.
- 준비: `disputed(max_rounds=2)` 뒤 판정자 셋이 기각한다. 답변은 쟁점 `i0`의 `split`이다. 발견 셋을 준비한다: 부모가 `i0`인 `child1`, `child2`와 부모 없는 `independent`.
- 실행: 발견 하나(`child1`)만 붙인 답변을 넣는다. 이어서 셋을 모두 붙인 답변을 넣는다. 끝으로 판정자 셋이 승인한다.
- 단언:
  - 첫 답변은 `ValueError`이고 메시지가 `'split must identify'`에 맞는다(제품 "split must identify at least two derived findings").
  - 둘째 답변 뒤 `phase`는 `'judge'`이고 쟁점은 4개다. `parent_issue_ids == ['i0']`인 쟁점이 2개이고, 둘 다 `answer_role_slot_id`가 `'initial-0'`이다.
  - 대기 행동은 3개(판정자 셋)다. 행 165의 주석은 "Prior-round votes cannot satisfy this round, including unchanged issues."라고 밝힌다.
  - 승인 뒤 `decision`은 `'mismatch'`이고, 쟁점 `i0`의 `verdicts`는 2개다.
- 대역: 없음.

### `test_answer_batch_hides_peer_results_and_covers_assignments` (행 171–185)
- 성질: 답변은 자기에게 배정된 쟁점을 모두 한 번씩 다뤄야 하고, 같은 회차의 다른 답변자 결과를 보지 못한다.
- 준비: `start(max_rounds=2)` 뒤 두 초기 검토가 각각 발견 `f0`, `f1`로 불일치를 낸다. 조직을 넣고, 판정자 셋이 기각한다.
- 실행: 빈 `answers=[]`를 넣는다. 첫 답변을 기본 출력으로 넣고 둘째 답변 행동의 맥락을 읽는다. 둘째 답변을 넣는다.
- 단언: 빈 답변은 `ValueError`이고 메시지가 `'every assigned issue'`에 맞는다(제품 "answer must cover every assigned issue exactly once"). 둘째 답변자의 맥락에는 답변 단계 결과가 없고, 쟁점 `i0`의 `answer`는 `None`이다. 둘째 답변 뒤 `phase`는 `'judge'`이고 모든 쟁점에 `answer`가 있다.
- 대역: 없음.

### `test_round_three_reuses_slots_without_execution_keys_colliding` (행 187–196)
- 성질: 세 회차에 걸쳐 같은 좌석을 다시 써도 결과 키가 충돌하지 않는다.
- 준비: `disputed(max_rounds=3)`.
- 실행: 반복 변수 `round_number`가 2와 3일 때마다, 판정자 셋이 `unresolved`를 던져 현재 회차(1회차, 이어서 2회차)의 판정을 마치고, 다음 회차의 답변을 넣는다. 마지막으로 3회차의 판정자 셋이 다시 `unresolved`를 던진다. 판정은 모두 세 회차다.
- 단언: 1회차와 2회차의 판정 뒤 `(phase, round)`가 각각 `('answer', 2)`, `('answer', 3)`이다. 최종 `status`는 `'unresolved'`, `round`는 3이다. `results`는 14개다: 초기 2, 조직 1, 판정 3, 그리고 두 회차의 답변 1과 판정 3.
- 대역: 없음.

### `test_allocation_duplicates_and_judge_count` (행 198–201)
- 성질: 좌석 배정은 중복 좌석, 판정 좌석과 겹치는 검토 좌석, 셋이 아닌 판정자 수를 거부한다.
- 준비: 네 조합. `(['x', 'x'], 3)`, `(['judge-0'], 3)`, `(2, 4)`, `(2, 2)`.
- 실행: `start_review({'revision': 'r1'}, reviewers, judges)`.
- 단언: 모두 `ValueError`다. 예외 유형만 본다. 제품은 판정자가 셋이 아니면 "exactly three judges and a positive round limit are required"를 내고, 좌석 이름이 겹치면 `_unique`의 중복 오류를 낸다.
- 대역: 없음.
- 비고: `subTest(reviewers=..., judges=...)`의 네 케이스는 위와 같다.

### `test_revision_full_restart_and_old_output_blocked` (행 203–216)
- 성질: 새 개정의 검토는 결정 없이 처음부터 다시 시작하되 좌석과 대화를 물려받는다. 옛 제안에 대한 결과는 받지 않는다. 좌석을 줄이거나 같은 개정으로 다시 여는 것은 거부된다.
- 준비: `start()`로 두 초기 일치를 넣어 완료된 `old`를 만든다. `scoped_start({'revision': 'r2', 'proof': 'changed'}, reviewers=2, previous=old)`로 새 주기를 연다.
- 실행: 새 주기의 필드를 읽는다. `old`에 대한 초기 출력을 새 주기의 행동에 `accept_result`로 넣는다. `reviewers=1`인 개정과 같은 개정 `r1`로 각각 `scoped_start`를 부른다.
- 단언: 새 주기는 `status='working'`, `decision=None`이고 대기 행동이 2개다. `reviewer_slots`와 `turns`가 `old`와 같다. 옛 출력은 `ValueError`이고 메시지가 `'another proposal'`에 맞는다(제품 "result belongs to another proposal"). 뒤의 두 `scoped_start`는 `ValueError`다. 예외 유형만 본다. 제품 `start_review`는 같은 개정이면 "new review requires a new proposal revision"을, 이전 좌석을 포함하지 않는 범위면 "existing logical slots must be retained"를 낸다.
- 대역: 없음.

### `test_proposal_mutation_and_execution_identity` (행 218–234)
- 성질: 검토자는 제안의 저자이거나 저자의 맥락을 이어받은 실행일 수 없다. 한 실행 ID는 결과 하나에만 쓸 수 있다. 봉인된 제안이 바뀌면 주기가 진행되지 않는다.
- 준비: `start()`와 첫 행동. 런타임의 실행은 넷이다: `author`, `fresh`, `continuation_of='author'`인 `resumed`, `context_origin=['author']`인 `inherited`.
- 실행: 네 실행 각각에 대해 `validate_review_independence(cycle, runtime, eid, action)`를 부른다. 이어서 첫 결과를 `e-0`으로 넣고, 같은 ID `e-0`으로 다음 행동의 결과를 다시 넣는다. 끝으로 원 주기의 `proposal.proof`를 `'mutated'`로 바꾸고 `next_actions`를 부른다.
- 단언: `fresh`는 통과한다. `author`, `resumed`, `inherited`는 각각 `ValueError`다. 같은 실행 ID의 재사용은 `ValueError`다. 제안을 바꾼 뒤의 `next_actions`는 `ValueError`다. 모두 예외 유형만 본다.
- 대역: 없음.
- 비고: `subTest(execution_id=...)`의 세 케이스는 `author`, `resumed`, `inherited`다. 행 220–221의 주석은 저자 여부와 이어받은 저자 맥락을 입장과 수용이 `accept_result` 전에 함께 돌리는 하나의 계보 검사가 판단한다고 밝힌다. 제품 `validate_review_independence`는 이어받기와 맥락 출처를 추이적으로 따라간다.

### `test_transcript_restore_reference_and_integrity` (행 236–256)
- 성질: 좌석 전사 기록은 멱등이다. 개정 검토에서 복원된 맥락은 도구 출력 본문과 옛 제안 전문 대신 참조를 싣고 검토자의 결론은 싣는다. 복원 맥락은 주기와 분리된 사본이다. 전사 바이트가 바뀌면 복원이 실패한다.
- 준비: `start()`에 네 메시지를 `record_turn(cycle, 'initial-0', messages)`로 기록한다. 네 메시지는 시스템 규칙, 옛 제안 전문(`kind='proposal'`), 큰 도구 출력(`call='read'`), 조수의 사실 진술("Fact from source at line 3")이다. 같은 기록을 한 번 더 한다.
- 실행: 두 초기 일치로 주기를 끝내고, `scoped_start({'revision': 'r2'}, reviewers=2, previous=cycle)`로 복원 주기를 연다. 첫 행동의 `context_for`를 읽는다. 이어서 맥락의 제안 개정을 바꾸고, 복원 주기의 첫 전사 메시지 내용을 `'corrupt'`로 바꾼 뒤 다시 `context_for`를 부른다.
- 단언:
  - 두 번째 `record_turn`의 결과가 첫 결과와 같다.
  - 맥락의 `source_refs`는 2개다.
  - 맥락 JSON에 `'large exact source body'`와 `'old full proposal'`이 없고, `'Fact from source at line 3'`은 있다.
  - 복원 주기의 `turns['initial-0'][2].content`는 여전히 원 본문이다.
  - 맥락의 제안을 바꿔도 복원 주기의 `revision`은 `'r2'`다.
  - 손상 뒤의 `context_for`는 `ValueError`이고 메시지가 `'bytes changed'`에 맞는다(제품 "transcript bytes changed", `cause_kind='content_mismatch'`).
- 대역: 없음.

### `test_manifest_peer_and_judge_origin_checks` (행 258–270)
- 성질: 입력 매니페스트는 객체여야 한다. 봉인되지 않은 동료 결과를 볼 수 없고, 판정자는 초기 검토나 조직자 맥락을 이어받을 수 없으며, 한 논리 좌석은 다른 좌석의 대화를 이어받을 수 없다.
- 준비: 검사마다 새 주기를 만든다.
- 실행: 네 경우를 `accept_result`에 넣는다.
  1. 매니페스트 `[]`.
  2. 첫 초기 결과(`e-0`) 뒤 둘째 초기 결과에 `visible_execution_ids=['e-0']`.
  3. `disputed()`의 첫 판정에 `continuation_of='e-0'`.
  4. 첫 판정(`e-3`)을 넣은 뒤 다음 판정에 `continuation_of='e-3'`.
- 단언: 각각 `ValueError`이고 메시지가 차례로 `'input manifest must be an object'`, `'unsealed peer'`, `'judge cannot inherit'`, `"another slot's conversation"`에 맞는다. 제품 문구는 "input contains unsealed peer results", "judge cannot inherit initial-review or organizer context", "a logical slot cannot inherit another slot's conversation"이다.
- 대역: 없음.

### `test_stage_schema_is_specific` (행 272–276)
- 성질: 단계 스키마는 단계마다 다르다.
- 준비: 없음.
- 실행: `stage_schema`를 `initial`, `judge`, `organize`, `invented`로 부른다.
- 단언: `initial`의 `required`에 `findings`가 있다. `judge`의 `required`에 `issue_verdicts`가 있다. `organize`의 `properties`에 `decision`이 없다. `invented`는 `ValueError`다(제품 "unknown review stage").
- 대역: 없음.

## SealedReplayTests (행 279–377)

`unittest.TestCase`를 그대로 상속하고 훅과 도우미가 없다. 각 테스트는 필요한 제품 함수를 테스트 안에서 import한다. 네 테스트 모두 끝난 검토를 봉인된 증거로 재생하는 `validate_sealed_review`를 검사한다.

### `test_budget_closed_investigation_is_verified_unresolved_not_an_unfinished_vote` (행 280–302)
- 성질: 조사 예산이 0이라 닫힌 조사 요청은 끝나지 않은 표가 아니라 검증된 미해결로 재생된다. 이 판단은 그 검토를 지배한 설정에 묶인다.
- 준비: `scoped_start({'revision': 1}, reviewers=2)`에서 정책과 범위 평가를 가져와 `start_review`로 주기 `RC-cap`을 연다. 첫 행동의 미해결 출력(`scope_complete=False`)과 조사 요청 하나(`Which domain is intended?`)로 `defer_for_research(..., 'requester', [[]], limit=0)`를 부른다. 런타임에는 끝난 요청자 실행을 둔다. 설정은 `DEFAULT_CONFIG`에서 `review_research_limit`만 0으로 바꾸고, `build_profiles`로 프로필을 만든다. 요청자 실행에는 `actor_kind='ai'`와 `identity_review` 프로필 참조를 단다.
- 실행: `validate_sealed_review(cycle, runtime, instance=instance)`. 이어서 설정의 `review_research_limit`를 3으로 바꾸고 다시 부른다.
- 단언: 첫 결과의 `(status, decision)`은 `('unresolved', 'unresolved')`다. 둘째는 `ValueError`이고 메시지가 정규식 `'closure|limit'`에 맞는다. 제품에는 "review closure limit no longer matches its governing configuration"이 있다.
- 대역: 없음.

### `test_authorized_replacement_keeps_full_authority_and_sealed_input` (행 304–323)
- 성질: 권한을 받아 대체한 좌석의 검토는 봉인 입력의 해시를 영수증에 담고, 재생할 때 그 해시가 맞아야 한다.
- 준비: 임시 폴더에 `ReviewFakeEngine`을 만들고 `grant_replacement`로 부여 `GR-review`를 적용한다. `engine.start('K1')`로 초기 좌석부터 검토를 연다. 대기 행동의 `(stage, slot, round)`에 재시도 불가 복원 사건(`lost exact public transcript`)을 `record_recovery_event`로 기록한다.
- 실행: `engine._authorize_review_replacement(action, grant_id='GR-review')`로 대체를 허가한다. 대기열에 `identity_review` 행동이 없을 때까지 `engine.execute()`를 반복한다. 이어서 `validate_sealed_review`를 부른다. 첫 대체 영수증의 `authorization.sealed_input_sha256`을 `'changed'`로 바꾸고 다시 부른다.
- 단언: 첫 대체 영수증의 `authorization`에 `sealed_input_sha256`이 있다. 재생 결과의 `decision`은 `'match'`다. 해시를 바꾼 뒤에는 `ValueError`이고 메시지가 `'sealed input changed'`에 맞는다(제품 "replacement sealed input changed").
- 대역: `ReviewFakeEngine`(저장소 없음, `_save`는 자동 명세 대역). `execute`는 픽스처 검토자로 답한다: 범위 평가 생성, 초기 일치, 조직, 판정 기각, 답변 철회.

### `test_previous_review_must_resolve_to_its_actual_preserved_cycle` (행 325–351)
- 성질: 개정 검토를 재생하려면 이전 검토가 실제로 보존된 주기 하나로 해석되어야 한다. 봉인 결과와 다른 결론은 거부된다.
- 준비: 개정 1과 2의 두 주기 `cycle-1`, `cycle-2`를 차례로 만든다. 둘째는 첫째를 `previous`로 둔다. 각 주기는 `scoped_start`에서 정책과 범위를 가져와 `start_review`로 연다. 대기 행동마다 `review_stage_output`의 기본 출력을 실행 ID `<cid>:<slot>`으로 넣고, 그 실행을 런타임에 끝난 실행으로 기록한다. 두 주기를 `runtime['review_cycles']`에 보존한다.
- 실행: `validate_sealed_review(cycle, runtime)`. 첫 결과의 `stage`를 `'judge'`로 바꾼 사본을 재생한다. 끝으로 `cycle-1`을 보존 목록에서 지우고 원 주기를 재생한다.
- 단언: 첫 재생의 `decision`은 `'match'`다. 위조 사본은 `ValueError`이고 메시지가 `'sealed evidence'`에 맞는다(제품 "review conclusion differs from sealed evidence"). `cycle-1`을 지운 뒤에는 `ValueError`이고 메시지가 `'preserved cycle'`에 맞는다(제품 "previous review does not resolve to one preserved cycle").
- 대역: 없음.

### `test_fixed_private_research_is_replayed_before_requesters_final_vote` (행 353–377)
- 성질: 요청자의 최종 표보다 먼저 수행된 고정 비공개 조사 결과는 재생에서도 실제로 수용된 실행의 출력과 일치해야 한다.
- 준비: `deferred_research_cycle()`로 첫 초기 검토가 조사 요청 하나 때문에 미뤄진 주기와 그 행동을 얻고, `id='RC-research'`를 둔다. 첫 전사 메시지에서 잠정 결과를, `research`에서 요청 ID를 읽고, `research_answer(cycle)`로 조사자의 답을 만든다. 런타임에는 요청자 실행(출력은 잠정 결과)과 조사자 실행(`supplemental_research`, 출력은 답)을 끝난 실행으로 둔다.
- 실행: `accept_research_result(cycle, rid, answer, 'investigator')`를 부른다. 이어서 대기 행동마다 기본 출력을 좌석 이름을 실행 ID로 넣는다. `validate_sealed_review`를 부른다. 끝으로 조사자 출력의 `request_digest`를 `'forged'`로 바꾸고 다시 부른다.
- 단언: 재생 `decision`은 `'match'`다. 위조 뒤에는 `ValueError`이고 메시지가 `'actual accepted execution'`에 맞는다(제품 "review result is not bound to its actual accepted execution").
- 대역: 없음.

## 관계

- 같은 제품 기능의 다른 층: 범위 단계와 정책 규칙은 `test_review_policy`가, 범위 응답의 전송 스키마와 제출 검사는 `test_review_scope_wire`가 본다. 엔진 층의 동일성 검토(입장, 적용, 저장)는 `test_review_engine`이 넓게 다룬다. 이 모듈은 주기 함수의 규칙과 봉인 재생에 집중한다.
- 픽스처 의존: `review_fixtures`의 `scoped_start`, `review_stage_output`, `deferred_research_cycle`, `research_answer`, `ReviewFakeEngine`, `grant_replacement`. `ReviewFakeEngine`은 내부에서 `research_fixtures`의 `governance_start`, `start_scoped_review`, `trust_fixture`, `trust_environment`를 쓴다.
- 이 모듈에만 있는 도우미: `ReviewCycleTests`의 `start`, `submit`, `disputed`, `judges`.
- 겹치거나 보완하는 시험: 대체 좌석의 흐름은 `test_review_policy.test_permanent_restoration_loss_blocks_its_slot_until_a_current_grant_authorizes_a_replacement`(주기 함수 수준)와 이 모듈의 `test_authorized_replacement_keeps_full_authority_and_sealed_input`(엔진 실행과 재생)이 나누어 본다. 전사 복원 실패는 이 모듈의 두 테스트가 주기 층의 오류를 보고, `test_review_policy.test_engine_returns_a_structured_slot_recovery_instead_of_reraising_restore_failure`가 엔진의 처분을 본다.

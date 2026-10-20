# test_completion_settlement

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_completion_settlement.py` (147행) |
| 클래스 / 테스트 | 2 / 6 |
| 시험 대상 제품 코드 | `do_math/academic_engine.py`의 `AcademicEngineMixin._settle_goal_completion`, `_ensure_academic_followup`; `do_math/engine.py`의 `ResearchEngine._settle_activity`, `_retry_submission_publications`; `do_math/activities.py`의 `open_activity`, `finish_activity`; `do_math/retention.py`의 `record_cleanup_interruption`, `pending_cleanup_failures` |
| 사용하는 픽스처 모듈 | `research_fixtures`: `bare_engine` |
| 격리 표지 | 없음 |
| 시작 상태 | `CompletionSettlementTests`: 네 단 밖. `research_fixtures.bare_engine()`이 저장소를 적재하지 않고 만든 엔진 객체에 손으로 쓴 최소 `instance`와 `runtime`을 얹는다. `CleanupInterruptionTests`: 1단(`retention`의 순수 함수에 사전 `runtime`을 넘김) |

## 목적

모듈 docstring은 "완료는 실행되지 않은 의무를 보존하되 그 성공을 주장하지 않는다"라고 밝힌다. 목표가 완료되면 `_settle_goal_completion`(docstring "Close dispatch obligations with evidence, without claiming task success.")이 두 곳의 행동을 거둔다. 하나는 대기열(`queue`)의 아직 보내지 않은 행동이고, 다른 하나는 대기 행동(`waiting_actions`)이다. 각 행동은 `goal_completion_superseded_action` 이력으로 남고, 소유 활동에는 `reason='goal_completed_before_dispatch'`인 미해결 의무와 `next_owner='user'`인 후속으로 붙는다. 활동은 그 시도가 모두 끝난 뒤에야 마감된다(`activities.finish_activity`는 살아 있는 실행이 있으면 거부한다). 이 모듈은 완료 정산이 같은 규칙으로 여러 경로에서 도는지 확인한다. 경로는 네 가지다: 목표 완료 직후, 살아 있는 시도가 끝난 뒤의 활동 정산, 학술 요구 후속, 지연된 제출 발행 재시도. 둘째 클래스는 유지보수 정리(`retention`)가 중단되었을 때, 이미 지운 경로를 다시 실패로 열지 않는지를 본다.

## 모듈 수준 요소

- 행 8: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리다.
- 행 10–12: `do_math`의 `activities`, `retention`, `ResearchRepository`(자동 명세 대역의 원형)와 픽스처 `bare_engine`을 import한다.
- 행 146–147: 직접 실행하면 `unittest.main()`으로 이 모듈의 시험을 돈다.

## CompletionSettlementTests (행 15–122)

`unittest.TestCase`를 그대로 상속하고 표지와 설정 훅이 없다. 각 테스트는 도우미로 새 엔진을 만든다.

- `engine()` (행 16–25): `bare_engine()`으로 저장소 없는 엔진을 만든다. `instance`는 `{'id': 'RI-test', 'knowledge': {}}`이다. `runtime`은 `status='completed'`이고 `queue`, `waiting_actions`, `activities`, `executions`, `tasks`, `questions`, `history`가 비어 있다. 이어서 `activities.open_activity`로 연구 활동 세 개를 연다. 세 활동은 `AC-input`, `AC-review`, `AC-producer`이고, 모두 소유자 `RI-test`, 입력 없음, 개설 시각 `2026-09-24T00:00:00+00:00`이며 상태는 `ready`다. `bare_engine`은 저장소가 없을 때 메모리 `StateStore` 대역을 붙인다(`research_fixtures` 행 194–201, `bare_engine`의 docstring).

### `test_completion_records_input_and_held_submission_before_finishing_activities` (행 27–51)
- 성질: 목표 완료 정산은 대기열의 행동과 대기 중인 봉인 제출을 모두 이력으로 보존한 뒤에야 소유 활동을 마감한다. 늦게 들어온 사용자 입력은 질문으로 알리며, 정산을 다시 해도 상태가 바뀌지 않는다.
- 준비: `engine()`에 세 행동을 둔다.
  - 대기열 행동 `A-input`: 역할 `intent_interpretation`, 대상 `UI-late`, 소유 `AC-input`.
  - 대기열 행동 `A-review`: 역할 `maintenance`, 단계 `impact_review`, 대상 `EX-producer`, 소유 `AC-review`.
  - 대기 행동 `A-producer`: 역할 `research_work`, 소유 `AC-producer`. 종류 `impact_review`이고 `execution_id='EX-producer'`, `review_requests={'IB-one': {'payload_sha256': 'sealed'}}`를 갖는다. 이 대기 행을 `held`로 보관해 두고, 그 사본을 `waiting_actions`에 넣는다.
- 실행: `engine._settle_goal_completion()`을 부르고, 상태를 `deepcopy`한 뒤 한 번 더 부른다.
- 단언:
  - `queue`는 `[]`, `waiting_actions`는 `{}`이다.
  - 이력 행들의 `action.id` 집합이 `{'A-input', 'A-review', 'A-producer'}`다.
  - `A-producer` 이력의 `waiting`이 원래 `held`와 같다. 봉인 제출의 대기 정보가 온전히 보존된다.
  - `questions` 가운데 `'UI-late'`를 포함하는 것이 있다. 제품은 `intent_interpretation` 행동에 대해 "Goal completed before input ... was interpreted" 질문을 더한다.
  - 세 활동 모두 `status='finished'`이고 `unresolved`가 비어 있지 않으며, 마지막 `followups`의 `next_owner`가 `'user'`다.
  - 두 번째 호출 뒤의 `runtime`이 호출 전 사본과 같다. 거둘 행동이 없으면 제품이 곧바로 돌아온다.
- 대역: `bare_engine`의 메모리 상태 저장소 대역(호출되지 않음).
- 비고: 이름의 "before finishing activities"는 순서를 직접 단언하지 않는다. 결과 상태에 이력과 미해결 의무가 함께 남아 있는지만 확인한다.

### `test_live_activity_finishes_only_after_its_attempt_and_keeps_undispatched_work` (행 53–70)
- 성질: 살아 있는 실행이 있는 활동은 완료 정산에서 마감되지 않는다. 그 실행이 끝난 뒤의 활동 정산에서 마감되며, 보내지 못한 행동은 미해결 의무로 남는다.
- 준비: `engine()`의 `AC-input`을 `status='working'`, `assigned_execution_ids=['EX-live']`로 바꾼다. 실행 `EX-live`는 `status='running'`, `outcome=None`이다. 대기열에는 같은 활동이 소유한 행동 `A-later`(역할 `research_work`)를 둔다.
- 실행: `_settle_goal_completion()`을 부른다. 이어서 실행을 `status='ended'`, `outcome='output_accepted'`로 바꾸고, `_settle_review_resource_dispositions`를 아무 일도 하지 않는 자동 명세 대역으로 바꾼 뒤 `_settle_activity('EX-live')`를 부른다.
- 단언: 완료 정산 직후 활동 상태는 여전히 `'working'`이다. 활동 정산 뒤에는 `'finished'`다. 마지막 `unresolved` 항목의 `action_id`는 `'A-later'`이고, 마지막 `followups`의 `next_owner`는 `'user'`다. 제품의 `_settle_activity`는 `reason='goal_completed_before_dispatch'`인 의무를 `preserved`로 골라 마감에 싣는다.
- 대역: `create_autospec(engine._settle_review_resource_dispositions, side_effect=lambda: None)`.

### `test_academic_completion_uses_the_same_settlement` (행 72–81)
- 성질: 학술 요구 후속 경로에서 목표가 완료로 판정되어도 같은 완료 정산이 돈다.
- 준비: `engine()`의 대기열에 `A-input`(역할 `intent_interpretation`, 대상 `UI-late`, 소유 `AC-input`)을 둔다. `_solution_basis`는 `{'records': []}`를 돌려주고, `_academic_status`는 `{'status': 'not_applicable'}`을 돌려주는 자동 명세 대역으로 바꾼다.
- 실행: `do_math.academic.current_requirements`를 `{'sha256': 'current', 'items': []}`로 패치하고 `engine._ensure_academic_followup()`을 부른다.
- 단언: `AC-input`의 상태가 `'finished'`다. 이력 첫 행의 `action.id`가 `'A-input'`이다. 제품은 학술 상태가 `completed`나 `not_applicable`이면 `runtime['status']='completed'`로 두고 `_settle_goal_completion()`을 부른다.
- 대역: `create_autospec`으로 만든 `_solution_basis`와 `_academic_status` 대역, `patch('do_math.academic.current_requirements', ...)`.

### `test_delayed_publication_settles_each_role_and_preserves_pending_followups` (행 83–122)
- 성질: 지연된 제출 발행을 재시도해 받아들이면, 역할과 관계없이 소유 활동이 정산된다. 받는 도중 새 후속 행동이 생기면 활동은 마감되지 않고 작업 상태로 남는다.
- 준비: 역할 네 개와 후속 유무 두 가지의 조합마다 새 `engine()`을 만든다.
  - `instance['workspace']`는 `'unused'`, `runtime['status']`는 `'ready'`다.
  - 행동 `A-publication`은 소유 `AC-producer`다.
  - 실행 `EX-publication`은 `status='stopping'`, `input_bundle='BA-input'`, `result_ref='runtime/artifacts/BA-result/result.json'`이다.
  - `AC-producer`는 `working`이고 그 실행을 배정받았다.
  - 대기 행동은 종류 `submission_publication`이다.
  - `engine.head`는 `'snapshot'`이다.
- 실행: 대역 네 개를 둔다.
  - `engine.store`: `create_autospec(ResearchRepository, instance=True)`. `read`가 `b'{}'`를 돌려준다.
  - `engine._save`: 자동 명세 대역.
  - `_settle_review_resource_dispositions`: 아무 일도 하지 않는 대역.
  - `_receive_submission`: 부수효과 `receive`. `engine.runtime`을 `deepcopy`로 교체하고, 실행을 `ended`/`output_accepted`로 바꾸며, 대기 행동을 지운다. `followup`이 참이면 같은 활동 소유의 `A-next`를 대기열에 더한다.
  그다음 `engine._retry_submission_publications()`를 부른다.
- 단언: 교체된 `runtime`의 `AC-producer` 상태가 후속이 있으면 `'working'`, 없으면 `'finished'`다. `result_refs`는 `[execution['result_ref']]`이고, `unresolved`는 `[]`다. `_receive_submission`과 `_save`가 각각 정확히 한 번 불렸다. 제품의 `_settle_activity`는 같은 활동 소유의 대기열 행동이 있으면 `result_refs`만 갱신하고 돌아온다. 그래서 후속이 있을 때에도 `result_refs`가 채워진다.
- 대역: `create_autospec(ResearchRepository, instance=True)`, `create_autospec(engine._save)`, `create_autospec(engine._settle_review_resource_dispositions, side_effect=...)`, `create_autospec(engine._receive_submission, side_effect=receive)`.
- 비고: `subTest(role=..., followup=...)`의 여덟 케이스는 역할 `maintenance`, `identity_review`, `research_work`, `goal_audit`과 `followup` `False`/`True`의 조합이다. `receive`가 `runtime` 객체를 교체하므로, 재시도 뒤의 정산이 교체된 상태를 읽는다는 사실도 함께 확인된다. `store.read`의 `b'{}'`는 `_issued_input`이 `submission.issued_input`으로 발급 입력을 읽을 때 쓰인다.

## CleanupInterruptionTests (행 125–143)

`unittest.TestCase`를 그대로 상속하고 훅과 도우미가 없다. 두 테스트 모두 1단이다.

### `test_later_exact_deletion_resolves_an_interrupted_attempt` (행 126–135)
- 성질: 중단된 정리 시도가 남긴 경로 실패는 다른 경로의 성공적 삭제로는 풀리지 않고, 그 경로를 정확히 지운 뒤의 정리 기록으로만 풀린다.
- 준비: `runtime = {'history': []}`.
- 실행: 먼저 `record_cleanup_interruption(runtime, ['EX-one'], 'EX-maint', 'inaccessible', history_start=0)`을 부른다. 그다음 `EX-next`의 정리 기록을 두 번 덧붙인다. 첫 기록은 `deleted=['runs/other']`, 둘째 기록은 `deleted=['runs/EX-one']`이다. 각 단계마다 `pending_cleanup_failures(runtime)`를 부른다.
- 단언: 처음 미결 목록의 첫 행 `path`는 `'runs/EX-one'`이다. 무관한 삭제 뒤에도 미결은 1건이다. 정확한 삭제 뒤에는 `[]`이다. 제품 docstring "An unrelated healthy attempt does not clear an older failure. Only deletion of that exact path establishes cleanup completion"이 이 성질을 말한다.
- 대역: 없음.

### `test_failed_final_save_does_not_reopen_already_deleted_paths` (행 137–143)
- 성질: 정리 시도가 끝의 저장에서 실패해도, 그 시도 안에서 이미 지운 경로는 미결 실패로 다시 열리지 않는다.
- 준비: 이력에 `EX-maint`의 정리 기록 하나(`deleted=['runs/EX-one']`)가 있는 `runtime`.
- 실행: `record_cleanup_interruption(runtime, ['EX-one', 'EX-two'], 'EX-maint', 'save interrupted', history_start=0)` 뒤 `pending_cleanup_failures(runtime)`.
- 단언: 미결 경로 목록이 `['runs/EX-two']`다. 마지막 이력 행의 `completed_paths`가 `['runs/EX-one']`이다. 제품은 `history_start` 이후 같은 `execution_id`의 정리 기록에서 삭제된 경로를 모아, 실패 기록의 `paths`에서 빼고 `completed_paths`에 적는다(docstring "Name unfinished paths without undoing deletions recorded in this attempt.").
- 대역: 없음.

## 관계

- 같은 제품 기능의 다른 층: `_settle_goal_completion`은 `academic_engine`(학술 후속)과 `governance_engine`(행 427)의 두 호출처에서 불린다. 목표 감사 경로에서 완료에 이르는 공개 흐름은 `test_goal_audit`, `test_governance_engine`, `test_purpose_engine`이 넓게 다룬다. `activities.py`의 이름을 딴 시험 모듈은 없다. `finish_activity`를 직접 부르는 시험은 `test_engine`과 `test_execution_lifecycle`에 있다. 유지보수 정리의 실행 경로는 `test_retention`이 본다.
- 픽스처 의존: `research_fixtures.bare_engine` 하나.
- 이 모듈에만 있는 도우미: `CompletionSettlementTests.engine`.
- 겹치거나 보완하는 시험: 첫 테스트는 모든 활동의 시도가 없어 즉시 마감되는 경우를, 둘째 테스트는 살아 있는 시도가 있어 마감이 활동 정산으로 미뤄지는 경우를 본다. 셋째와 넷째는 같은 정산이 다른 진입점(학술 후속, 발행 재시도)에서도 도는지 확인한다.

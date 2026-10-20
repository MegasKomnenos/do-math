# test_review_engine

| 항목 | 값 |
|---|---|
| 조각 | `review` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_review_engine.py` (1405행) |
| 클래스 / 테스트 | 9 / 58 |
| 시험 대상 제품 코드 | `do_math/review_engine.py`의 `ReviewEngineMixin`(`_start_identity_review`, `_start_staged_identity_review`, `_completed_staged_identity_review`, `_admit_review_execution`, `_request_review_resource_disposition`, `_settle_review_resource_dispositions`, `_review_cycle`, `_review_schema`, `_prepare_review_context`, `_build_review_context`, `_record_review_recovery`, `_authorize_review_replacement`, `_retry_review_restoration`, `_record_review_input`, `_record_review_prompt`, `_record_review_observation`, `_apply_identity_review`, `_adopted_review_policy`); `do_math/engine.py`의 `_register_execution`, `_settle_activity`, `_review_recovery_control`, `_apply_delegation_judgment`, `_hold_impact_reviews`, `_retry_impact_reviews`, `_apply_bundle_candidate`, `_apply_extensions`, `_call_steps`, `control`; `do_math/review_cycle.py`(`record_turn`, `validate_transcript`, `validate_sealed_review`, `resource_disposition`, `validate_resource_disposition`, `context_for`, `next_actions`, `start_review`); `do_math/review_policy.py`(`minimum_scope_executions`, `validate_scope_assessment`, `build_review_policy`); `do_math/knowledge.py`(`begin_transition`, `record_transition_result`, `activate_transition`, `assess_use`, `capture_basis`); `do_math/knowledge_records.py`(`usable_links`, `identity_basis`, `proposal_view`, `record_formal_result`, `formal_usable`, `assessment_current`); `do_math/repository.py`의 `ResearchRepository`; `do_math/cli.py`의 `build_parser`, `execute` |
| 사용하는 픽스처 모듈 | `review_fixtures`(`ReviewFakeEngine`, `grant_replacement`, `ReassessmentHarness`, `ImpactReviewHarness`); `research_fixtures`(`bare_engine`, `current_state`, `git_init`, `scope_assessment`, `start_scoped_review`, `trust_environment`, `trust_fixture`, `charter`); `engine_fixtures`(`formal_check_engine`, `formal_verification`, `routing_engine`); `purpose_fixtures`(`ActivatedPurposeHarness`, `theorem`); `state_fixtures`(`owner_calls`, `start_active_copy`, `start_model_call`) |
| 격리 표지 | 없음(`test_group` 미사용) |
| 시작 상태 | 대부분 메모리 엔진 대역 `ReviewFakeEngine`(제품 `ResearchEngine` 하위 클래스, 저장소 없음). 그 밖에 `routing_engine`·`bare_engine`(메모리 엔진), `formal_check_engine`(`FakeEngine`), 1단(순수 검토 주기·정책 함수), 2단(`ActivatedPurposeHarness.make_active`, `start_active_copy`) |

## 목적

모듈 docstring은 "엔진 안의 동일성 검토"를 시험한다고 밝히고 그 영역을 일곱으로 든다. 주기(cycles), 범위 예산(scope budgets), 준비 실패(preparation failures), 입력 초과(input overflow), 영향 검토(impact reviews), 재평가(reassessment), 위임(delegation)이다. 순수 검토 주기(`do_math/review_cycle.py`)의 단계 전이는 `test_review_cycle`이 따로 검사하고, 이 모듈은 그 주기를 엔진이 소유할 때 생기는 계약을 본다. 그 계약은 다음과 같다.

- 채택된 검토 정책과 공표 전제가 주기를 열 때 봉인되고, 그 뒤에 바뀌면 거부된다.
- 칸마다 시도를 입장시킬 때 실행 예산을 센다.
- 제공자가 준 공개 사건만 그 칸의 대화로 복원한다.
- 입력 복원이 실패하면 칸 단위로 복구 기록을 남기고, 사용자 권한으로 교체한다.
- 신뢰 환경 전환 중의 단계적 검토가 전환 활성화로 소비된다.
- 자원이 바닥나면 판정을 지어내지 않고 계획으로 되돌린다.

엔진 쪽 구현의 좌표는 `do_math/review_engine.py`의 `ReviewEngineMixin`이다. 그 docstring은 "소유 엔진이 주기, 지식, 대기열의 변경을 실행 결과와 함께 원자적으로 저장한다"고 밝히고, `_record_review_input`은 실행 시작 시에도 불려 실패한 시도가 실제로 전달된 입력을 보존한다고 적는다.

## 모듈 수준 요소

- 행 14: `sys.path.insert(0, ...)`로 스킬의 `scripts/` 폴더를 경로 앞에 넣는다. `run_tests.py` 밖에서 직접 실행하거나 `unittest discover`로 돌려도 `do_math`를 import할 수 있게 하는 공통 머리다.
- 행 15–26: 제품 모듈과 픽스처 기호의 import. 모듈 함수, 상수, `setUpModule`은 없다.
- 행 1404–1405: 직접 실행하면 `unittest.main()`을 부른다.

## ReviewEngineTests (행 29–947)

`unittest.TestCase`를 상속하고 표지가 없다. 클래스 속성도 없다.

- `setUp` (행 30–33): 임시 폴더를 만들고 정리를 등록한 뒤 `self.engine = ReviewFakeEngine(self.temp.name)`을 둔다. `ReviewFakeEngine`은 검증된 형식 증거와 검토 정책 `fixture-review-policy-v5`(초기 칸 최소 2, 판정 칸 `judge-0..2`, `round_limit=2`, `activity_execution_limit=24`, `overflow_disposition='unresolved'`)를 가진 정리 후보 `K1` 하나를 담은 제품 엔진이다. 저장소가 없고, `_save`는 autospec 대역이며, 저장소 읽기는 `FileNotFoundError`를 낸다. 신뢰 환경 `TE-review`는 `trust_fixture`가 임시 폴더 아래에 만든 합성 도구 모음이다. 이 클래스의 모든 테스트는 이 상태에서 시작한다. `engine.start()`는 `start_scoped_review`로 범위 단계를 이미 정한 주기를 열어 초기 칸 두 개(`initial-0`, `initial-1`)부터 시작한다. `_start_identity_review`를 직접 부르면 범위(`scope`) 단계부터 시작한다. `engine.execute(changes)`는 대기 중인 첫 검토 행동을 검토자로서 답한다. 초기 칸은 `match`, 조직자는 발견 사항마다 쟁점을 만들고, 판정자는 모든 쟁점을 기각하며, 답변자는 이의를 철회한다. 그 답을 제품의 입장(`_admit_review_execution`)과 적용(`_apply_identity_review`) 경로로 넣는다.
- `staged_transition` (행 275–286): 등록 상태의 신뢰 환경 `TE-next`(도구 모음 `new-toolchain`)를 더하고, `knowledge.begin_transition`으로 전환을 연다. `K1`의 검증 결과를 새 도구 모음으로 바꾸고 선언 증거 값을 `'staged verified proof'`로 바꾼 사본을 `record_transition_result`로 기록한다. 그 전환을 `runtime['trust_transitions']`에 두고 ID를 돌려준다.
- `_staged_activation_git_round_trip(*, followup_transition)` (행 365–513): 두 Git 왕복 테스트가 공유하는 시나리오 본체다. 아래 해당 테스트 항목에서 풀어 쓴다.
- `open_dispute` (행 776–783): 범위를 정한 주기를 열고 `initial-0`이 발견 사항 `f`와 함께 `mismatch`를 내게 한다. 이어 `initial-1`을 답하고, 대기 행동이 `organize`임을 단언한 뒤 조직 단계를 실행해 쟁점 `issue-0`을 만든다. 주기 ID를 돌려준다. 뒤에 남는 행동은 판정자 세 칸이다.

### `test_adopted_instance_policy_is_the_only_opening_and_publication_policy` (행 35–49)
- 성질: 주기를 열 때와 공표할 때 쓰는 정책은 인스턴스에 채택된 `review_policy` 하나뿐이고, 열린 뒤 그 정책이 바뀌면 검토를 이어 가거나 다시 열 수 없다.
- 준비: `setUp`의 `ReviewFakeEngine`. 채택 정책을 `id='ADOPTED'`, `minimum_initial_slots=3`, `required_perspectives=['formal','semantic','scope']`, `activity_execution_limit=18`로 바꾼 사본으로 교체한다.
- 실행: `_start_identity_review('K1')`로 연 뒤, 대기 행동에 `_prepare_review_context`를 부른다. 정책의 `activity_execution_limit`을 19로 바꾸고 `_review_cycle(pending)`과 `_start_identity_review('K1')`을 다시 부른다.
- 단언: 주기의 `review_policy`와 준비된 문맥의 `review_policy`가 채택 정책과 같다. 정책을 바꾼 뒤의 두 호출은 모두 `ValueError`를 메시지 조각 `'publication premises'`로 던진다. 제품 메시지는 `_review_cycle`의 `'review publication premises changed: formal, exposition, trust or policy'`다. 재시작 호출도 같은 사유로 거부되는 것은 `_start_identity_review`가 이미 열린 주기를 다시 쓸 때 `_review_cycle`을 거치기 때문이다.
- 대역: 없음(`setUp`의 엔진 대역 외).

### `test_kernel_evidence_outside_the_reviewed_projection_still_binds_publication` (행 51–59)
- 성질: 검토 제안(projection)에 드러나지 않는 커널 증거도 공표 전제에 묶여 있어, 그것이 바뀌면 검토가 공표되지 않는다.
- 준비: `setUp`의 엔진에서 `_start_identity_review('K1')`. 주기에 봉인된 `proposal`의 사본을 떠 둔다. 이어 형식 결과의 `verification.declaration_evidence.sample.value`를 `'another proof term'`으로 바꾼다.
- 실행: `review_cycle.review_proposal(instance, 'K1')`, `_review_cycle(pending)`.
- 단언: 변경 뒤에도 `review_proposal`의 결과가 봉인된 제안과 같다. 곧 이 증거는 제안 밖에 있다. 그런데도 `_review_cycle`은 `ValueError`(`'publication premises'`)를 던진다. 공표 전제에 든 `identity_basis`가 형식 결과의 `verification` 전체를 해시로 묶기 때문이다(`knowledge_records.identity_premise`).
- 대역: 없음.

### `test_v5_missing_adopted_policy_does_not_use_config_default` (행 61–65)
- 성질: 채택된 검토 정책이 없으면 구성 기본값으로 대신하지 않고 검토를 열지 않는다.
- 준비: 인스턴스에서 `review_policy`를 지운다.
- 실행: `_start_identity_review('K1')`.
- 단언: `ValueError`를 메시지 조각 `'adopted review policy'`로 던진다(제품 `_adopted_review_policy`의 `'adopted review policy is required before review admission'`).
- 대역: 없음.

### `test_admission_counts_failed_and_retried_executions_before_results` (행 67–84)
- 성질: 실행 예산은 결과가 아니라 입장한 시도를 센다. 실패한 시도와 재시도도 모두 세고, 같은 시도를 두 번 입장시켜도 한 번만 센다.
- 준비: 한도를 `review_policy.minimum_scope_executions(2, 2)`(= 11)로 두고, 정책과 범위 평가 모두에 그 한도를 넣어 `engine.start`로 연다.
- 실행: `attempt-1`부터 `attempt-11`까지 각 시도에 대해 `_admit_review_execution(action, execution)`을 두 번 부르고, 시도를 `ended`로 바꿔 실행 기록에 넣는다. 마지막으로 `attempt-extra`를 입장시킨다.
- 단언: 각 시도의 첫 호출은 `'admitted'`, 두 번째는 `'already_admitted'`다. 12번째 시도는 `'review_budget_exhausted'`다. 주기의 `execution_accounting.executions_used`는 11개 시도 ID 목록과 정확히 같고, `results`는 빈 사전이다. 결과가 하나도 없어도 예산이 바닥난다는 뜻이다.
- 대역: 없음.

### `test_optional_research_cannot_consume_mandatory_followup_reservations` (행 86–95)
- 성질: 선택적 보충 조사는 필수 후속 단계(초기, 조직, 답변, 판정)를 위해 예약된 실행 칸을 쓸 수 없다.
- 준비: 한도 12로 연 주기. 대기 행동을 `role='supplemental_research'`, `stage='investigating'`, `research_request_id='R'`로 바꾼 행동을 만든다.
- 실행: `_admit_review_execution(action, {'id': 'optional', ...})`.
- 단언: `disposition`이 `'review_followup_reserved'`다. 반환된 `reserved_execution_slots`의 단계 집합이 `{'initial','organize','answer','judge'}`를 포함한다. `executions_used`는 빈 목록이다(거부된 시도는 세지 않는다).
- 대역: 없음.

### `test_admission_cannot_reseal_changed_policy_or_scope` (행 97–104)
- 성질: 입장은 바뀐 정책이나 범위를 새로 봉인하지 않고 거부한다.
- 준비: `engine.start('K1')` 뒤 주기의 `activity_execution_limit`을 1 늘린다.
- 실행: `_admit_review_execution(pending, {'id': 'stale', ...})`.
- 단언: `ValueError`(`'review inputs changed'`; 제품 메시지 `'review inputs changed before admission: ...'`). `executions_used`는 빈 목록이다.
- 대역: 없음.

### `test_actual_prompt_and_public_provider_events_restore_only_to_their_slot` (행 106–133)
- 성질: 실제로 전달된 프롬프트와 제공자의 공개 사건은 그 칸의 대화로만 복원된다. 추론(reasoning) 사건은 저장되지 않고, 다른 칸에는 보이지 않는다.
- 준비: `engine.start('K1')`. 대기 행동을 가진 실행 `PUBLIC`을 둔다. 사건 셋을 준비한다. `reasoning` 항목(`'HIDDEN'`), `agent_message`(`'PUBLIC EXPLANATION'`), `command_execution`(`aggregated_output='EXACT TOOL OUTPUT'`)이다.
- 실행: `_record_review_prompt('PUBLIC', prompt, artifact_ref=...)`. 이어 각 사건을 같은 `event_index`로 `_record_review_observation`에 두 번씩 넣는다. 자기 칸과 동료 칸에 `_prepare_review_context`를 부른다.
- 단언: 그 칸의 대화(`turns`)는 3개다(전달 프롬프트, 공개 메시지, 도구 결과). 같은 사건을 다시 넣어도 늘지 않고, reasoning은 들어가지 않는다. `turns` 어디에도 `'HIDDEN'`이 없다. 자기 문맥에는 `'PUBLIC EXPLANATION'`이 있고, 물질화된 원천 파일 가운데 하나는 프롬프트 전문을, 다른 하나는 `'EXACT TOOL OUTPUT'`을 담는다. 동료 칸의 문맥에는 `'PUBLIC EXPLANATION'`이 없고 `source_refs`가 빈 목록이다.
- 대역: 없음.

### `test_observed_public_events_reject_out_of_order_append_but_allow_exact_replay` (행 135–143)
- 성질: 같은 사건의 정확한 재생은 허용되지만, 이미 기록한 것보다 앞선 순번의 새 사건은 거부된다.
- 준비: 대기 행동을 가진 실행 `ORDER`와 `public_message` 사건 하나.
- 실행: `event_index=3`으로 두 번 기록한 뒤 `event_index=1`로 기록한다.
- 단언: 앞의 두 호출은 통과한다. 세 번째는 `ValueError`(`'out of order'`; 제품 메시지 `'observed public review event arrived out of order'`)다.
- 대역: 없음.

### `test_public_provider_numbers_survive_storage_and_slot_restoration` (행 145–184)
- 성질: 정수 전용 상태에 넣을 수 없는 제공자 숫자(소수, 2^53)는 정확한 JSON 텍스트로 보존되어, 저장 왕복과 칸 복원을 거쳐도 값이 같다.
- 준비: 실행 `NUMBERS`. 값 `0.25`와 `2 ** 53` 각각에 대해 사건 넷을 만든다. `assistant` 텍스트(사용량에 값), `mcp_tool_call`(인자와 결과에 값), `assistant`의 `tool_use` 블록(입력에 값), `public_message`의 도구 메시지(`arguments`에 값)다. 모두 8개이고, 원본 사본을 떠 둔다.
- 실행: 각 사건을 같은 순번으로 두 번 기록한다. 주기를 `canonical_json`으로 직렬화했다가 되읽어 교체한다. 이어 `validate_transcript(cycle, slot)`과 `_prepare_review_context`를 부른다.
- 단언: 입력 사건 목록이 원본과 같다(제품이 입력을 바꾸지 않는다). 검증된 대화는 8개다. 각 값 묶음의 첫 대화 내용은 `'Observed value'`다. 둘째의 JSON 내용 `result.estimate`, 셋째의 `input.threshold`, 넷째의 `arguments.threshold`가 원래 값과 같다. 복원 문맥의 `self_messages`도 8개다. 각 원천 파일의 SHA-256이 참조의 `sha256`과 같고, 그 JSON이 해당 순번의 대화와 같다.
- 대역: 없음.
- 비고: 제품 근거는 `_record_review_observation`의 주석 "Provider JSON numbers remain exact text outside integer-only state."다.

### `test_restore_diagnostics_keep_exact_coordinate_hashes_and_verified_prefix` (행 186–206)
- 성질: 복원 중 내용 불일치가 나면, 복구 사건은 정확한 좌표, 기대·관측 해시, 검증된 앞부분을 보존한다. 재시도해도 같은 사건을 중복 기록하지 않는다.
- 준비: `record_turn`으로 칸에 대화 둘을 기록하고, 둘째의 기대 해시를 떠 둔다. 그 뒤 둘째 내용을 `'changed second'`로 바꾼다.
- 실행: `_prepare_review_context`를 같은 작업 폴더로 두 번 부른다.
- 단언: 복구 사건의 `cause_kind`는 `'content_mismatch'`다. `coordinate`는 `{'slot': ..., 'index': 1}`이다. `expected_sha256`은 떠 둔 해시이고 `observed_sha256`과 다르다. `preserved_range.verified_indices`는 `[0]`이다. `retryable`은 `False`다. `continuity_broken`은 `False`다(행 203 주석: 불일치는 원본 사본이 모두 사라졌다는 증거가 아니다). 두 번째 호출의 사건이 첫 번째와 같고, `recovery_events`는 1개다.
- 대역: 없음.

### `test_tampered_materialized_source_records_the_exact_file_hashes` (행 208–220)
- 성질: 작업 폴더에 물질화된 원천 파일이 바뀌면, 복구 사건은 기대 해시, 실제 파일의 해시, 파일 경로를 기록한다.
- 준비: 칸에 도구 대화 하나를 기록하고, 문맥을 한 번 준비해 원천 파일을 만든다. 그 파일을 `b'changed file'`로 덮어쓴다.
- 실행: 같은 작업 폴더로 `_prepare_review_context`를 다시 부른다.
- 단언: `expected_sha256`은 참조의 `sha256`이다. `observed_sha256`은 `b'changed file'`의 SHA-256이다. `coordinate.path`는 파일의 절대 경로 문자열이다.
- 대역: 없음.
- 비고: 제품은 이 경우 `cause_kind='materialized_content_mismatch'`를 쓰지만(`_build_review_context`), 이 시험은 `cause_kind`를 단언하지 않는다.

### `test_temporary_io_failure_preserves_reason_and_can_be_retried` (행 222–232)
- 성질: 일시적 입출력 실패(`EAGAIN`)는 재시도 가능한 복구로 기록되고, 원인 문구와 경로를 보존한다.
- 준비: `engine.start('K1')`.
- 실행: `_build_review_context`를 `OSError(errno.EAGAIN, 'sharing temporarily unavailable', 'source.json')`을 던지게 패치하고 `_prepare_review_context`를 부른다.
- 단언: 복구 사건의 `retryable`이 `True`다. `reason`이 `'sharing temporarily unavailable'`을 담는다. `coordinate.path`가 `'source.json'`이다.
- 대역: `patch.object(engine, '_build_review_context', side_effect=OSError(...))`.
- 비고: 이름의 "재시도될 수 있다"는 `retryable` 표지로 확인한다. 제품 `_record_review_recovery`는 이 표지가 참이면 처분을 `'slot_restore_retry'`, 다음 소유자를 `'review_recovery'`로 정한다. 이 시험은 실제 재시도(`_retry_review_restoration`)를 부르지 않는다. 재시도의 성공은 `test_restored_exact_bytes_release_the_held_slot_without_a_replacement`와 `test_review_materialization_failure_ends_preparation_and_saves_recovery`가 본다. `errno`와 `patch`를 함수 안에서 다시 import한다(모듈 머리에도 있다).

### `test_central_replacement_control_releases_wait_and_queues_next_execution` (행 234–256)
- 성질: 중앙 제어(`_review_recovery_control`)로 교체를 요청하면, 그 칸의 대기가 풀리고 활동이 다시 준비되며, 같은 활동이 소유한 교체 행동이 대기열에 오른다.
- 준비: `grant_replacement(engine)`으로 `K1` 검토의 기록 기반 교체 권한 `GR-review`를 준다. 연 주기의 대기 행동 사본에 `id='AC-held'`, `owner_activity_id='AY-held'`를 준다. 문맥을 한 번 준비한 뒤 `ValueError('permanent_loss')`를 재시도 불가 복구로 기록한다. `activities.open_activity`로 `AY-held`를 열고, `wait_for`로 `review_input_restoration` 대기에 둔다. `waiting_actions`에 같은 대기를 넣고 대기열을 비운다.
- 실행: `ResearchEngine._review_recovery_control(engine, {'action': 'request', 'config': {'role': 'maintenance', 'review_replacement': {'action': action, 'grant_id': 'GR-review'}}})`.
- 단언: 반환값이 참이다. `waiting_actions`에서 `AC-held`가 사라진다. 활동 `AY-held`의 상태가 `'ready'`다. 대기열에 `replacement_for`가 있는 행동이 있고, 그 `owner_activity_id`가 `'AY-held'`다. 그 행동의 문맥 준비 결과는 `'ready'`다.
- 대역: 없음.

### `test_restored_exact_bytes_release_the_held_slot_without_a_replacement` (행 258–273)
- 성질: 원래 바이트가 복구되면 교체 없이 멈춘 칸이 풀리고, 연속성 파손 사건도 남지 않는다.
- 준비: 정상 대화 하나를 기록한 주기(`good`)를 두고, 그 내용을 `'corrupt'`로 바꾼다. 준비가 복구를 기록하게 한 뒤 `waiting_actions`에 대기를 넣고 대기열을 비운다. 이어 `turns`를 정상 사본으로 되돌린다.
- 실행: `_retry_review_restoration(action, root/'restored', at='now')`.
- 단언: `disposition`이 `'review_resumed'`다. `waiting_actions`가 빈 사전이다. 대기열이 비어 있지 않다. 주기의 `continuity_events`가 빈 목록이다.
- 대역: 없음.

### `test_staged_candidate_uses_the_same_scope_cycle_without_publication` (행 288–304)
- 성질: 신뢰 환경 전환 중의 단계적(staged) 후보도 같은 범위 단계 주기로 검토되지만, 검토 결과를 인스턴스에 공표하지 않는다. 완료 영수증은 전환 기반에 묶인다.
- 준비: `staged_transition()`. 인스턴스의 사본을 떠 둔다.
- 실행: `_start_staged_identity_review(transition_id, 'K1')`. 이어 `execute()`를 세 번(범위, 초기 칸 둘) 부르고 `_completed_staged_identity_review`를 부른다. 전환 결과의 선언 증거 값을 `'changed'`로 바꾼 뒤 다시 부른다.
- 단언: 첫 대기 행동의 단계가 `'scope'`다. 주기 제안의 `formal.toolchain`이 `TE-next`의 도구 모음이다. 세 번 실행한 뒤에도 인스턴스가 사본과 같다. 영수증의 `decision`은 `'match'`, `review_cycle_id`는 주기 ID, `transition_basis`는 주기 `staged_candidate`의 `transition_basis`다. 변경 뒤 호출은 `ValueError`(`'staged'`; 제품 `_review_cycle`의 `'staged review candidate changed'`)다.
- 대역: 없음.

### `test_completed_staged_review_is_consumed_by_transition_activation` (행 306–333)
- 성질: 완료된 단계적 검토 영수증은 전환 활성화가 소비한다. 활성화는 새 형식 결과·해설·평가와 그 사용 기록을 만들고, 원래 인스턴스는 바꾸지 않는다.
- 준비: `staged_transition()`, 단계적 검토 완주(`execute` 세 번), 영수증. 전환 사본의 `results.K1.identity_review`에 영수증을 넣는다.
- 실행: `knowledge.activate_transition(engine.instance, candidate, runtime=engine.runtime)`.
- 단언: 결과의 `active_trust_environment`가 전환의 `to_environment`다. `K1`의 `formal_result_id`와 `exposition_id`가 이전과 다르고, 새 기록의 `supersedes`가 각각 이전 ID다. `review_cycle_id`가 주기인 평가의 `execution_ids`가 영수증의 것과 같고, 그 평가의 `formal_result_id`와 `exposition_id`가 새 ID다. 그 평가를 가리키는 `status='active'` 사용 기록이 있다. `engine.instance`는 떠 둔 사본과 같다.
- 대역: 없음.

### `test_staged_activation_rejects_tampered_receipt_and_stale_policy` (행 335–363)
- 성질: 변조된 영수증, 다른 전환·대상의 영수증, 낡은 정책 아래의 활성화는 거부되고 상태를 바꾸지 않는다.
- 준비: 단계적 검토 완주와 영수증.
- 실행: 세 경우를 `activate_transition`에 넣는다. (1) `proposal_digest`를 `'0'*64`로 바꾼 영수증. (2) `subTest(field=...)`로 `transition_id='TR-another'`, `knowledge_id='K-another'`를 넣은 영수증. (3) 인스턴스 사본의 `review_policy.round_limit`을 1 늘린 상태.
- 단언: (1)은 `ValueError`(`'receipt'`; 제품 `knowledge.py`의 `'staged identity review receipt is stale, altered, or not a complete match'`). (2)는 `ValueError`(`'receipt|another transition target'`). (3)은 `ValueError`(`'publication premises'`). 각 경우 뒤에 인스턴스가 호출 전 사본과 같다.
- 대역: 없음.
- 비고: `subTest` 케이스는 `transition_id`, `knowledge_id` 둘이다.

### `test_staged_activation_git_round_trip_preserves_old_and_loads_new_records` (행 515–516)
- 성질: 단계적 검토로 활성화한 상태를 실제 Git 저장소에 저장했다 되읽으면, 옛 형식 결과와 평가는 두 판본 모두에 그대로 남고, 새 기록은 전환에 묶인 채 적재된다.
- 준비: `_staged_activation_git_round_trip(followup_transition=False)`. 도우미는 다음을 한다. `trust_fixture`로 `old-lean`과 `next-lean` 합성 도구 모음을 임시 폴더에 만든다. `trust_environment`로 옛 환경 `TE-review`(활성)와 새 환경 `TE-next`(등록)를 만들고, `K1`의 검증 결과를 옛 도구 모음에 맞춘다. 전환, 단계적 검토 완주(`execute` 세 번), 영수증, `activate_transition`을 차례로 거친다. 이어 `git_init`으로 `round-trip-repository`를 만들고 `ResearchRepository(path, 'RI-000...')`를 연다. `current_state()`의 생애 주기 필드를 붙여 저장 계약을 통과하는 전후 상태를 만든다. 이때 활동 `AY-fixture` 기록을 만들고, 실행 기록의 시각·입력 목록·제출 영수증을 채운다. 주기의 `producer_execution_ids`와 입력 결합 해시를 정규화한다. `capacity_constraints`를 넣고 `role_profile_refs`를 뺀다. 전환 상태를 `active`로 하고 `trust_activate` 대기 행동을 지운다.
- 실행: `repository.initialize(before)`, 이어 `save_with_state(first, after)`. 저장 중 `repository_module.exact_content_hash`를 `wraps` 패치로 감싸, `transition_id`와 `from_environment`를 가진 사전에 대한 호출(`transition_hashes`)을 모은다. 두 판본을 새 `ResearchRepository`로 `load`한다.
- 단언: 두 번째 저장에서 전환 해시 호출이 있다(부모에 없던 단계적 검토는 전환을 해시로 묶는다, 행 442 주석). `before`의 `formal_results`와 `identity_assessments`의 모든 기록이 옛 판본과 새 판본에 그대로 있다. 새 판본의 현재 형식 결과의 `transition_id`가 전환 ID다. 해설의 `formal_result_id`가 현재 형식 결과다. 주기의 평가가 현재 형식 결과·해설을 가리킨다. 그 평가의 사용 기록이 있다.
- 대역: `patch.object(repository_module, 'exact_content_hash', wraps=...)`(호출 관측용, 동작은 원래 함수).
- 비고: 실제 Git 저장소를 쓰고, `ResearchRepository`의 저장·적재는 `do_math/git_store.py`를 거쳐 `git` 자식 프로세스를 부른다. `git_init`은 프로세스마다 한 번 `git init`을 돌린 모형 `.git`을 복사한다.

### `test_staged_assessment_survives_a_second_transition_and_git_round_trip` (행 518–519)
- 성질: 단계적 검토로 만든 평가와 기록은 두 번째 신뢰 전환 뒤에도 바이트 그대로 남되 현재성을 잃는다. 두 번째 전환의 저장은 이미 끝난 단계적 검토의 전환 해시를 다시 계산하지 않는다.
- 준비: `_staged_activation_git_round_trip(followup_transition=True)`. 앞 테스트의 모든 단계와 단언을 거친 뒤 이어서 진행한다. 첫 전환의 형식 결과·해설·평가 사본을 떠 둔다. `final-lean` 도구 모음으로 `TE-final`(등록)을 만들고, 두 번째 전환을 열어 결과를 기록한 뒤 `activate_transition`한다.
- 실행: 두 번째 활성 상태를 `save_with_state(second, ...)`로 저장하고(`transition_hashes`로 관측) 다시 적재한다.
- 단언: 두 번째 활성 직후 첫 전환의 형식 결과·해설·평가가 사본과 같다. 주기 `staged_candidate.target_environment.status`는 `'registered'`다. `TE-next`의 상태는 `'superseded'`다. 봉인된 검증에 `trust_environment_digest`가 없고, `toolchain`이 검토 당시 환경의 도구 모음과 같다(행 493 주석: 봉인 결과는 가변 환경 기록의 해시가 아니라 도구 모음 정체성을 묶는다). `kr.formal_usable`과 `kr.assessment_current`는 거짓이고, `kr.usable_links(..., 'K1')`은 참이다. 세 번째 저장의 전환 해시 호출 목록은 빈 목록이다(행 501 주석). 적재한 판본에서도 세 기록이 사본과 같고, 평가는 현재가 아니며, `K1`은 사용 가능하다.
- 대역: 앞 테스트와 같은 `wraps` 패치.
- 비고: 실제 Git 자식 프로세스를 쓴다. 앞 테스트의 모든 단언을 함께 수행하므로, 앞 테스트가 깨지면 이 테스트도 깨진다.

### `test_split_proposal_binds_real_formal_exposition_and_current_basis` (행 521–531)
- 성질: 분리 저장된 지식에서도 검토 제안은 실제 형식 결과와 해설, 현재 동일성 기반에 묶인다. 지식 기록 자체에는 형식·검토 필드가 없다.
- 준비: `K1` 기록의 사본을 떠 둔 뒤 `engine.start('K1')`.
- 실행: 없음(주기 필드를 읽는다).
- 단언: 주기 제안의 `lean_code`가 `kr.proposal_view`의 것과 같다. `identity_basis`가 `kr.identity_basis`와 같다. 제안의 `formal_result_id`와 `exposition_id`가 지식 기록의 것과 같다. 지식 기록에 `formal`, `lean_code`, `reviews`, `status`, `identity_assessment`가 없다.
- 대역: 없음.

### `test_corrupt_slot_can_be_replaced_from_verified_records_under_real_user_grant` (행 533–555)
- 성질: 손상된 칸은 실제 사용자 권한 아래 검증된 기록에서 교체된다. 교체 칸의 문맥에는 보존된 대화만 들어가고, 손상 내용과 동료의 비공개 검토는 들어가지 않는다.
- 준비: `grant_replacement`. 칸 대화 둘(`'preserved visible conversation'`, `'lost exact body'`)을 기록하고, 둘째를 `'CORRUPTED'`로 바꾼다. `permanent_loss`를 재시도 불가 복구로 기록한다.
- 실행: `_authorize_review_replacement(action, grant_id='GR-review')`. 이어 동료 칸(`initial-1`)을 요약 `'PRIVATE-PEER-REVIEW'`로 실행하고, 교체 행동의 문맥을 준비한 뒤 교체 칸을 실행한다.
- 단언: 권한 처분이 `'replacement_ready'`다. 교체 문맥의 준비 결과가 `'ready'`이고, `'preserved visible conversation'`을 담으며, `'CORRUPTED'`와 `'PRIVATE-PEER-REVIEW'`를 담지 않는다. 실행 뒤 `usable()`이 참이고 주기에 `replacement_receipts`가 있다.
- 대역: 없음.

### `test_replacement_rejects_forged_grant_source_and_revocation_before_input` (행 557–572)
- 성질: 권한의 출처 문서가 위조되었거나, 권한이 입력 전에 철회되면 교체가 거부된다.
- 준비: `grant_replacement`, 복구 기록. 거버넌스 출처 `SOURCE-review`의 `text` 끝에 `' forged'`를 붙인다.
- 실행: `_authorize_review_replacement`, 출처 복원 뒤 다시 `_authorize_review_replacement`, 권한 `GR-review`를 `revoked`로 바꾼 뒤 교체 행동에 `_prepare_review_context`.
- 단언: 첫 처분은 `'authorization_denied'`, 복원 뒤는 `'replacement_ready'`, 철회 뒤 준비 결과는 `'authorization_denied'`다.
- 대역: 없음.

### `test_approved_replacement_omits_malformed_manifest_without_rethrowing` (행 574–593)
- 성질: 대화 목록(manifest) 행이 망가진 칸은 예외를 다시 던지지 않고 복구를 기록한다. 승인된 교체는 검증할 수 없는 내용을 빼고 진행한다.
- 준비: `grant_replacement`. 칸에 대화 `'UNVERIFIABLE'` 하나를 기록하고 그 `transcript_manifest` 행을 `None`으로 바꾼다.
- 실행: `_prepare_review_context`, `_authorize_review_replacement`, 교체 문맥 준비, `execute()` 두 번.
- 단언: 첫 준비 결과가 `'recovery_recorded'`(예외가 아니라 처분)다. 권한 처분은 `'replacement_ready'`다. 교체 준비는 `'ready'`이고 `'UNVERIFIABLE'`을 담지 않는다. 끝에 `usable()`이 참이다.
- 대역: 없음.

### `test_checked_delegation_replacement_survives_its_own_recorded_input` (행 595–631)
- 성질: 위임으로 승인된 교체는, 교체 칸이 자기 입력을 기록한 뒤에도(같은 입력을 두 번 기록해도) 위임 권한 결합을 유지하고 봉인 검토를 통과한다.
- 준비: `grant_replacement`, 복구 기록. 사용자 결정 `ORIGINAL`(`kind='review_replacement'`)을 둔다. `governance.apply_decision`으로 위임 `DG`를 적용한다. 칸 좌표와 `continuity_break_cause='permanent_loss'`를 담은 효과로 사례 `CASE`를 만든다. `delegations.prepare_application`으로 적용 기록을 만들고, `INTERPRET`와 `CHECK` 두 실행의 판단(`within_scope`)을 `record_judgment`로 기록한다.
- 실행: `_authorize_review_replacement(action, grant_id='GR-review', delegation_id='DG', case=case)`. 교체 행동을 대기열 맨 앞으로 옮긴 뒤 `execute(record_first=True)`와 `execute()`를 부른다.
- 단언: 처분이 `'replacement_ready'`다. 끝에 `usable()`이 참이다. `review_cycle.validate_sealed_review(cycle, runtime, instance=...)`의 `decision`이 `'match'`다.
- 대역: 없음.
- 비고: `record_first=True`는 적용 전에 `_record_review_input`을 두 번 부른다(`ReviewFakeEngine.execute`). 결합 비교는 `delegation_authority` 키를 뺀 나머지로 한다(`_record_review_input`).

### `test_replacement_unresolved_question_keeps_organizer_finding_coordinates` (행 633–644)
- 성질: 교체 칸이 질문과 함께 `unresolved`를 내면, 주기는 조직 단계로 가고 이어 판정 단계로 간다.
- 준비: `grant_replacement`, 복구 기록, 교체 승인.
- 실행: 동료 칸 `execute()`. 이어 교체 칸을 `decision='unresolved'`, `questions=['Exact domain still disputed']`로 실행하고, 조직 단계를 실행한다.
- 단언: 교체 칸 실행 뒤 대기 단계가 `'organize'`, 조직 뒤 대기 단계가 `'judge'`다.
- 대역: 없음.
- 비고: 이름은 조직자 발견 사항의 좌표 보존을 말하지만, 단언은 단계 전이(`organize` → `judge`)만 확인한다. 쟁점이나 발견 사항의 좌표는 읽지 않는다.

### `test_actual_profile_and_restored_input_remain_bound_to_the_logical_slot` (행 646–664)
- 성질: 실제 실행 프로필과 복원된 입력은 논리 칸에 묶이고, 다음 개정판 검토에서 같은 칸의 프로필이 바뀌면 거부된다.
- 준비: `engine.start('K1')`, `engine.profile`을 `{'id': 'EP-review', 'revision': 1, 'sha256': 'a'*64}`로 둔다.
- 실행: `execute()` 두 번으로 첫 주기를 끝낸다. `revise()`로 `K2`를 만들고 `start(kid, previous_cycle_id=cid)` 뒤 `execute()`를 한다. 프로필을 `EP-other`로 바꾸고 다시 `execute()`한다.
- 단언: 첫 주기의 `slot_profiles['initial-0']`과 `input_bindings['ex-1'].profile_ref`가 그 프로필이다. 새 주기에서 실행의 입력 결합 `restored_messages`가 문맥의 `self_messages`와 같고 비어 있지 않다. 프로필을 바꾼 실행은 `ValueError`(`'profile'`; 제품 `'logical review slot profile changed'`)다.
- 대역: 없음.

### `test_runtime_trust_barrier_leaves_final_slot_pending_for_retry` (행 666–677)
- 성질: 신뢰 전환이 진행 중이면 마지막 칸의 결과 적용이 거부되고, 주기는 입장 회계를 빼면 적용 전 그대로 남아 재시도할 수 있다.
- 준비: `engine.start('K1')`, `execute()` 한 번. 주기 사본을 떠 두고 `runtime['trust_transitions'] = {'TR': {'status': 'ready'}}`를 둔다.
- 실행: `execute()`.
- 단언: `ValueError`(`'trust transition'`; 제품 `knowledge_records.py`의 `'identity publication waits for the trust transition'`). 주기가 `execution_accounting`을 뺀 모든 키에서 사본과 같다. `executions_used`는 `['ex-1', 'ex-2']`다(입장한 시도는 적용이 되돌려져도 세어진다).
- 대역: 없음.

### `test_initial_match_activates_only_after_all_slots` (행 679–698)
- 성질: 초기 `match`는 모든 칸이 끝난 뒤에만 지식을 사용 가능하게 한다. 주기 시작은 멱등이고, 스키마는 제안 요약값에 묶인다.
- 준비: `engine.start('K1')`.
- 실행: `_start_identity_review('K1')` 재호출, `_review_schema(pending)`, `execute()` 두 번.
- 단언: 시작 직후 사용 불가이고 대기열에 2개가 있다. 재호출이 같은 주기 ID를 돌려주고 대기열은 여전히 2개다. 스키마의 `proposal_digest.enum`이 주기의 요약값 하나다. 첫 실행 뒤 `identity_assessments`가 비어 있다. 두 번째 실행의 문맥 `completed_results`가 빈 사전이다(동료 결과를 보지 않는다). 그 뒤 사용 가능하다. 평가의 `decision`은 `'match'`이고 `execution_ids`는 2개다. 지식 기록에 `identity_assessment`가 없다. 대기열 첫 행동의 역할은 `research_plan`이다. 런타임이 JSON 왕복에서 같다.
- 대역: 없음.

### `test_v5_scope_execution_selects_initial_slots_before_the_initial_phase` (행 700–709)
- 성질: 범위 단계 실행이 초기 칸을 고른 뒤에야 초기 단계가 시작된다.
- 준비: `_start_identity_review('K1')`(범위 단계부터).
- 실행: `execute()` 한 번(범위 답: `generated-scope`, 칸 `initial-0`, `initial-1`).
- 단언: 실행 전 대기 단계가 `'scope'`다. 실행 뒤 주기 `phase`가 `'initial'`이다. `review_input_basis.values.scope_assessment.assessment_id`가 `'generated-scope'`다. 대기열의 검토 칸 집합이 `{'initial-0','initial-1'}`이다.
- 대역: 없음.

### `test_scope_admission_propagates_actual_activity_and_selected_profile_to_initial_actions` (행 711–727)
- 성질: 범위 단계의 실제 소유 활동과 범위 평가가 고른 프로필이 초기 단계 행동에 전파된다.
- 준비: 범위 단계부터 연 주기. 대기 행동의 `owner_activity_id`를 `'AY-actual'`로 바꾼다. `selected_profile_ref`를 `EP-fixed`로 둔 범위 평가를 만든다.
- 실행: `execute({'scope_assessment': scope})`.
- 단언: 주기의 `owner_activity_id`가 `'AY-actual'`이다. 대기열의 모든 `identity_review` 행동이 `owner_activity_id='AY-actual'`과 `profile_ref=selected`를 갖는다.
- 대역: 없음.

### `test_scope_to_answer_and_judgment_publishes_the_same_links_consumed_by_goal_audit` (행 729–774)
- 성질: 범위부터 답변과 판정까지 완주한 검토가 공표한 링크는, 목표 감사가 소비하는 링크와 같다. 그 평가의 사용이 정지되면 목표 기반 키가 바뀌고 사용 판정이 무효가 된다.
- 준비: 범위 단계부터 주기를 연다. 이어 차례로 실행한다. 범위, `initial-0` 불일치(발견 사항 `f`), `initial-1`, 조직, 판정 셋, 원래 칸의 이의 철회 답변, 2라운드 판정 셋이다.
- 실행: 공표 뒤 `bare_engine(engine.instance, engine.runtime)`으로 감사 엔진을 만든다(같은 객체를 공유한다). `goal_judgments`와 `tasks`를 비운다. `charter('CH-goal-fixture', ...)`와 사용자 출처로 `governance.initialize_governance`를 한다. `_render_prompt`와 `_record_output_questions`를 autospec 대역으로 바꾸고 `goal_auditors=2`를 둔다. `_goal_basis_key()`를 떠 두고, 실행 `AUDIT`의 거버넌스 입력을 `_bind_governance_input`으로 묶은 뒤 `_apply`로 `goal_audit` 결과(`satisfied`, `used_sources=['K1']`)를 적용한다. 끝으로 `kr.set_assessment_use(..., 'suspended', ...)`를 부른다.
- 단언: `usable_links(K1)[0]`의 `assessment_id`가 평가 ID다. `kr.knowledge_view`의 첫 행 `links`가 그 링크 하나다. `knowledge.assess_use`가 유효하다. 평가의 `policy_ref`가 주기의 것과 같다. 목표 판정의 `formal_result_refs`가 링크의 `formal_result_id` 하나다. `record_basis`가 `knowledge.capture_basis(..., ['K1'])`와 같다. 감사 뒤 평가 객체가 같은 객체(`assertIs`)다. 사용 정지 뒤 `_goal_basis_key()`가 떠 둔 값과 다르고, `assess_use`가 무효다.
- 대역: `create_autospec(audit._render_prompt, return_value='fixed goal-audit instructions')`, `create_autospec(audit._record_output_questions)`.

### `test_complete_rejected_objection_round_trip` (행 785–798)
- 성질: 기각된 이의는 원래 칸의 답변과 2라운드 판정을 거쳐 한 바퀴 돌고, 끝에 같은 주기의 `match` 평가를 현재 기반으로 공표한다.
- 준비: `open_dispute()`.
- 실행: 판정 셋(모두 기각), 원래 칸 답변(`record_first=True`), 2라운드 판정 셋.
- 단언: 판정 뒤 대기 행동이 `('answer', 'initial-0')`이다. 답변 문맥의 `completed_results` 가운데 `judge` 단계가 3개다. 답변 뒤 대기 행동의 `round`가 2다. 끝에 사용 가능하다. 평가의 `review_cycle_id`는 주기 ID이고, `execution_ids`는 3개이며, `basis`는 현재 `identity_basis`다.
- 대역: 없음.

### `test_mismatch_and_round_limit_return_precise_followup` (행 800–818)
- 성질: 확정된 불일치와 라운드 한도 도달은 각각 정확한 후속 계획 입력을 대기열에 남긴다.
- 준비: `open_dispute()`.
- 실행: (1) 판정 셋이 모두 `issue-0`을 `approved`로, `decision='mismatch'`로 답한다. (2) `ReviewFakeEngine(temp, rounds=1)`로 새 엔진을 만들고 `open_dispute()` 뒤 판정 셋이 `unresolved`로 답한다.
- 단언: (1) 평가 `decision`이 `'mismatch'`이고 사용 불가다. 대기열의 `research_plan` 행동의 `identity_review`에 `cycle_id`가 주기 ID이고, `issues`에 `'issue-0'`이 있으며, `actual_scope`가 참이고, `effective`가 거짓이다. (2) 평가 `decision`이 `'unresolved'`이고, 계획 행동의 `identity_review.remaining_questions`가 참이다.
- 대역: 없음.
- 비고: (2)는 `self.engine`을 새 엔진으로 교체해 `open_dispute`를 재사용한다.

### `test_new_revision_restarts_all_slots_and_retains_own_conversation` (행 820–840)
- 성질: 새 개정판은 모든 칸을 다시 시작하되 칸 구성과 각 칸의 대화를 이어받는다. 이전 개정판의 평가는 바뀌지 않는다.
- 준비: 첫 주기를 `execute()` 두 번으로 끝내고, 주기와 평가의 사본을 떠 둔다.
- 실행: `revise()`로 `K2`, `start(kid, previous_cycle_id=first_id)`, `execute()` 두 번.
- 단언: 새 주기의 `revision`이 다르다. `reviewer_slots`와 `turns`가 첫 주기와 같다. 시작 직후 `K2`는 사용 불가다. 첫 실행의 문맥에 `self_messages`와 `source_refs`가 있다. 끝에 `K2` 평가의 주기 ID가 새 주기이고 사용 가능하다. `K1`의 평가는 사본과 같다.
- 대역: 없음.

### `test_source_recovery_has_exact_bytes_hash_and_relative_path` (행 842–861)
- 성질: 칸에 복원되는 원천은 정확한 바이트와 해시를 가진 파일로 상대 경로에 놓이고, 문맥 본문에는 원천 내용이 인라인되지 않는다. 다시 준비해도 대화가 늘지 않는다.
- 준비: `initial-0`에 도구 대화 하나(`'Original source at line 12: quantifier'`, `call='read'`, `message_id='source-1'`)를 기록한다.
- 실행: `_prepare_review_context`를 같은 작업 폴더로 두 번 부른다.
- 단언: 참조 파일이 존재하고, SHA-256이 참조 `sha256`과 같으며, JSON이 원래 대화와 같다. `local_path`는 절대 경로가 아니다. 문맥 JSON에 원천 내용 문자열이 없다. `self_messages[0].content.source_ref.local_path`가 참조의 `local_path`다. 두 번째 준비 뒤에도 `initial-0` 대화는 1개다.
- 대역: 없음.

### `test_final_match_does_not_override_suspension_or_formal_change` (행 863–878)
- 성질: 마지막 칸이 `match`를 내도, 그 사이 형식 결과 정지, 원천 해시 변경, 환경 무효화, 신뢰 전환, 정책 변경이 있으면 평가를 공표하지 않는다.
- 준비: `subTest(failure=...)`마다 새 `ReviewFakeEngine`, `start`, `execute()` 한 번. 그 뒤 실패 종류에 따라 상태를 바꾼다.
- 실행: 두 번째 `execute()`.
- 단언: `ValueError`가 난다(유형만 확인하고 메시지는 보지 않는다). `identity_assessments`가 빈 사전이고 사용 불가다.
- 대역: 없음.
- 비고: `subTest` 케이스는 다섯이다. `suspended`(형식 결과 `formal_use`), `source_hash`(`verification.source_sha256`), `environment`(`TE-review` 상태 `invalid`), `trust_transition`(런타임에 `checking` 전환), `policy`(`activity_execution_limit` +1).

### `test_input_delta_is_not_a_recursive_transcript_copy` (행 880–894)
- 성질: 칸마다 기록되는 입력은 새 요청분(delta)이고, 복원된 대화나 제안 전체를 재귀적으로 복사하지 않는다.
- 준비: `open_dispute()`.
- 실행: 판정 셋, 답변 하나, 판정 셋을 모두 `record_first=True`로 실행한다.
- 단언: 모든 칸의 대화 수 합이 `3 * len(cycle['results'])`다. `kind='review_request'`인 대화의 `content`에 `self_messages`와 `proposal`이 없다. 모든 `message_id`가 서로 다르다.
- 대역: 없음.
- 비고: 제품 근거는 `_build_review_context`의 주석 "Appending the complete rendered prompt here would recursively duplicate old messages."다.

### `test_fresh_exact_formal_check_preserves_eligibility` (행 896–905)
- 성질: 같은 검증 내용으로 형식 검사를 새로 기록해도 검토 자격은 유지되고, 평가는 새 기반으로 공표된다.
- 준비: `start`, `execute()` 한 번. 현재 검증을 복사해 `kr.record_formal_result`로 다시 기록한다.
- 실행: `execute()`.
- 단언: 사용 가능하다. 평가 `basis`가 현재 `identity_basis`다.
- 대역: 없음.

### `test_environment_transition_during_review_invalidates_old_environment_use` (행 907–915)
- 성질: 검토 도중 활성 신뢰 환경이 바뀌면 옛 환경 위의 검토는 공표되지 않는다.
- 준비: `start`, `execute()` 한 번. 활성 환경을 `'TE-new'`로, `TE-review`를 `superseded`로 바꾼다.
- 실행: `execute()`.
- 단언: `ValueError`(`'premises changed'`; 제품 `_review_cycle`의 공표 전제 메시지). 사용 불가다.
- 대역: 없음.

### `test_new_judge_finding_is_assigned_answered_and_fully_judged` (행 917–930)
- 성질: 판정자가 새로 낸 발견 사항도 쟁점으로 조직되고, 답변 칸에 배정되며, 모든 판정자에게 판정된다.
- 준비: `open_dispute()`.
- 실행: `judge-0`이 새 발견 사항 `new-source`와 함께 `mismatch`를 내고, 나머지 판정 둘, 조직, 답변, 판정 셋을 실행한다.
- 단언: 판정 셋 뒤 대기 단계가 `'organize'`다. 조직 문맥의 `pending_findings[0].ref.slot`이 `'judge-0'`이다. 조직 뒤 대기 단계가 `'answer'`다. 답변 문맥의 `answer_requests` 집합이 `{'issue-0','issue-1'}`이다. 끝에 사용 가능하다.
- 대역: 없음.

### `test_mutated_proposal_and_old_action_are_rejected` (행 932–947)
- 성질: 검토 중 제안이 바뀌거나, 지난 행동으로 스키마를 요청하면 거부된다.
- 준비: 연 주기의 대기 행동 사본(`old_action`). 형식 결과의 `lean_code` 끝에 주석 한 줄을 붙인다.
- 실행: `_review_schema(old_action)`. 원복 뒤 `execute()` 두 번으로 주기를 끝내고, `revise`와 새 주기 시작 뒤 `_review_schema(old_action)`을 부른다.
- 단언: 첫 호출은 `ValueError`(`'sealed mathematical proposal'`), 마지막 호출은 `ValueError`(`'not pending'`; 제품 `'review action is not pending'`)다.
- 대역: 없음.

## ReleasedInsightTests (행 950–970)

`unittest.TestCase`를 상속하고 표지, 속성, 훅, 도우미가 없다.

### `test_released_incidental_insights_plan_only_preserved_items` (행 951–970)
- 성질: 검토가 끝나 풀려난 부수 통찰(private insights)은 등록된 종류만 지식으로 보존되고, 그것들만 증거로 하는 계획 하나를 연다.
- 준비: `valid`가 참과 거짓인 두 반복. 각 반복에서 `routing_engine()`을 만들고 `knowledge_io.ensure_ontology`로 온톨로지를 채운다. `_apply_queue_plan`과 `_apply_academic_resolutions`를 autospec 대역으로 바꾼다. 실행 `EX-old`와 `EX-current`, 완료된 주기 `RC`, 그리고 `EX-old`에서 온 통찰 셋을 `private_insights['RC']`에 둔다. 통찰의 종류는 `'question'`(유효) 또는 `'unregistered'`다.
- 실행: `_apply_extensions({'role': 'identity_review', 'review_cycle_id': 'RC'}, 'EX-current')`.
- 단언: 대기열의 `research_plan` 수가 `int(valid)`다. 유효하면 그 계획의 `evidence_refs` 집합이 인스턴스 지식 ID 집합과 같고 3개다. 무효하면 지식이 빈 사전이다.
- 대역: `create_autospec(engine._apply_queue_plan)`, `create_autospec(engine._apply_academic_resolutions)`. `routing_engine` 자체도 `_bind_revision_action`, `_cancel_selected_revision_targets`, `_record_output_questions`를 autospec으로 바꾼다.
- 비고: 반복은 `subTest` 없이 `for` 문으로 돈다. 첫 반복이 실패하면 둘째는 실행되지 않는다.

## ReviewPreparationFailureTests (행 973–1051)

기반은 `purpose_fixtures.ActivatedPurposeHarness`다. 그 `setUp`이 `install_adapter_fixture`로 `do_math.initialization.adapter_for`를 `FixtureAdapter`로 패치한다. 두 테스트는 `self.make_active()`로 시작한다. 이는 `restore_template(state_fixtures.active_instance, config={})`의 사본(2단)이고, 실제 Git 저장소 위에 `ResearchEngine`을 새로 만든다. 러너는 `PurposeRunner()`, 형식 검증기는 `formal_fixture`다. 클래스 표지, 속성, 도우미는 없다.

### `test_failed_review_slot_keeps_its_live_sibling_running` (행 974–1020)
- 성질: 한 초기 칸의 입력 물질화가 실패해도, 이미 실행 중인 형제 칸은 멈추지 않고 결과를 낸다. 실패한 칸만 복원 대기로 간다.
- 준비: 2단 사본. 대기열을 비우고 `_knowledge_io_control`로 `theorem()` 후보를 가져온다. `owner_calls` 안에서 `_formal`로 형식 검사를 끝낸다. `_start_identity_review`로 범위 행동을 열고, `owner_calls` 안에서 `start_model_call`로 범위 호출을 끝낸다. 대기열을 검토 행동만 남긴다. 러너의 `answer`를 감싸 `initial-0`은 `threading.Event` `release`를 최대 60초 기다리게 한다. `_prepare_review_context`를 감싸 `initial-1`일 때만 두 가지를 한다. 먼저 `initial-0` 실행이 아직 끝나지 않았는지를 `observed`에 적는다. 그다음 `Path.mkdir`를 `review-sources` 경로에서 `OSError(EBUSY, ...)`를 던지게 패치한 채 원래 준비를 부르고, 끝에 `release`를 세운다.
- 실행: 감싼 준비 함수로 `patch.object(engine, '_prepare_review_context', side_effect=prepare_slot)`를 두고 `engine._save()`, `engine.run(max_steps=2)`.
- 단언: `observed`가 `[True]`다(`initial-1` 준비는 `initial-0`이 살아 있는 동안 한 번 일어났다). `initial-0` 실행의 `outcome`이 `'output_accepted'`다. `initial-1`의 대기 항목 `kind`가 `'review_input_restoration'`이다.
- 대역: `patch.object(engine, '_prepare_review_context', ...)`, 준비 안의 `patch.object(Path, 'mkdir', busy)`, 러너 `answer` 교체. 러너는 `PurposeRunner`다.
- 비고: `PurposeRunner.run`은 `research_fixtures.local_job_runner`로 감싸져 있어, 호출마다 실제 Windows Job 안에서 `python -c "import time; time.sleep(600)"` 자식 프로세스를 띄웠다가 끝낸다. 범위 호출과 `initial-0` 호출이 이에 해당한다. `release.wait(60)`은 스레드 사이 대기의 시간 상한이다. 실제 Git 저장소를 쓴다.

### `test_review_materialization_failure_ends_preparation_and_saves_recovery` (행 1022–1051)
- 성질: 검토 입력의 물질화가 실패하면 그 시도는 준비 단계에서 끝나고, 복원 대기가 저장된다. 재시도가 성공하면 대기가 풀린다.
- 준비: 앞 테스트와 같이 후보 가져오기와 형식 검사를 거쳐 `_start_identity_review`로 연다. 첫 검토 행동(범위)을 고른다.
- 실행: `Path.mkdir`를 `review-sources` 경로에서 `OSError(EBUSY, 'Regression source materialization busy')`로 패치하고, `owner_calls` 안에서 `start_model_call(engine, action)`을 부른다. 이어 `engine.store.load()`를 하고 `_retry_review_restoration(wait['action'], root/'restored', at=now())`를 부른다.
- 단언: 이 행동의 시도가 1개이고 상태가 `'ended'`다. `waiting_actions[action.id]`의 `kind`가 `'review_input_restoration'`이고 `next_owner`가 `'review_recovery'`다(`EBUSY`는 재시도 가능). 저장소에서 적재한 런타임의 같은 대기가 메모리의 것과 같다. 재시도의 처분이 `'review_resumed'`이고, 대기가 사라진다.
- 대역: `patch.object(Path, 'mkdir', unavailable)`.
- 비고: 준비가 실패하므로 러너는 불리지 않는다. 실제 Git 저장소를 쓴다.

## ReviewScopeBudgetTests (행 1054–1137)

`unittest.TestCase`를 상속하고 표지, 속성, 훅, 도우미가 없다. 엔진을 쓰는 두 테스트는 `engine_fixtures.formal_check_engine(self)`로 시작한다. 이는 활성화된 `FakeEngine`(메모리 엔진 대역)에 후보 `K1`과 형식 검사 행동을 둔 상태이고, `adapter_for` 패치와 임시 폴더 정리를 `self`에 등록한다. 나머지 둘은 1단이다.

### `test_exhaustion_drains_only_owned_attempts_before_publishing_followup` (행 1055–1089)
- 성질: 예산이 바닥나면 그 검토가 소유한 시도만 멈추게 하고, 그 시도들이 모두 끝난 뒤에야 후속 계획을 공표한다. 무관한 실행은 건드리지 않는다.
- 준비: `formal_check_engine`, `engine.knowledge('K2')`. 채택 정책의 한도를 `minimum_scope_executions(2, round_limit)`로 두고 `_adopted_review_policy`를 그 사본을 돌려주는 autospec으로 바꾼다. `start_scoped_review(engine, 'K2', scope_assessment(policy, ['one','two']))`로 연다. 한도만큼 `_register_execution`으로 시도를 등록하고, 마지막을 뺀 시도는 `end_preparation(..., cancelled=True)`로 끝낸다. 마지막 시도는 `starting`, `running`으로 전이한다. 무관한 `maintenance` 실행 `EX-unrelated`를 등록한다.
- 실행: 한도를 넘는 `EX-denied` 등록, 마지막 시도를 `stopping`과 `ended`(`execution_incomplete`)로 전이, `_settle_activity(last)`.
- 단언: 초과 등록은 `None`이다. 그때 `review_cycle.resource_disposition(cycle).state`가 `'draining'`이다. 마지막 시도에 `stop_requested='review_resource_disposition'`이 있고, 무관한 실행에는 없다. 아직 `research_plan`이 없다. 정산 뒤 주기 `status`가 `'unresolved'`이고, 소유 활동이 `'finished'`이며, 무관한 실행은 여전히 `'running'`이다. `research_plan`이 정확히 1개다. `validate_sealed_review`의 `decision`이 `'unresolved'`다.
- 대역: `create_autospec(engine._adopted_review_policy, side_effect=...)`. 시계는 `FakeEngine.current_time`을 쓴다.

### `test_floor_counts_scope_and_mandatory_followup` (행 1092–1102)
- 성질: 범위 평가의 실행 한도 하한은 이미 쓴 시도와 필수 후속 경로를 모두 센다.
- 준비: 1단. `subTest(rounds=...)`마다 `build_review_policy(None, reviewer_count=3, max_rounds=rounds)`와 칸 셋의 `scope_assessment`.
- 실행: `validate_scope_assessment(scope, policy, executions_used=1)`를 한도 `required - 1`과 `required`로 부른다.
- 단언: `required - 1`은 `ValueError`(`'at least'`; 제품 `'scope activity execution limit requires at least ... attempts including ... already used'`). `required`는 통과하고 반환 평가의 `activity_execution_limit`이 `required`다.
- 대역: 없음.
- 비고: `subTest` 케이스는 `(1, 8)`, `(2, 14)`, `(4, 14)`다. 제품 식 `minimum_scope_executions`는 `used + slots + 1 + (3 if round_limit == 1 else slots + 6)`이므로, 칸 3·사용 1에서 1라운드는 8이고 2라운드 이상은 14다.

### `test_scope_context_exposes_actual_attempt_usage` (행 1104–1109)
- 성질: 범위 단계 문맥은 실제로 쓴 시도 수와 그에 따른 최소 한도를 보여 준다.
- 준비: 1단. `review_cycle.start_review({'revision': 1}, 2)`, `executions_used=['EX-first','EX-retry']`.
- 실행: `context_for(cycle, next_actions(cycle)[0])`.
- 단언: `scope_executions_used`가 2, `minimum_scope_execution_limit`이 13이다.
- 대역: 없음.

### `test_unaffordable_scope_returns_to_plan_without_fabricating_a_judgment` (행 1111–1137)
- 성질: 범위 단계조차 감당할 수 없는 예산이면 시도를 등록하지 않고, 판정을 지어내지 않은 채 계획으로 돌아간다. `defer` 처분이면 주기를 얼린 채 둔다.
- 준비: `subTest(disposition=...)`마다 `formal_check_engine`, `K2`. 정책 한도 1과 해당 `overflow_disposition`을 autospec 대역으로 준다. `_start_identity_review('K2')`(범위 단계부터).
- 실행: `_register_execution(action, {'id': 'EX-unstarted', ...})`, 이어 `_settle_review_resource_dispositions()`.
- 단언: 등록 결과가 `None`이고 실행 기록에 없다. `validate_resource_disposition`의 `state`는 `unresolved`일 때 `'ended'`, `defer`일 때 `'deferred'`다. `identity_assessments`가 이전과 같다. `research_plan`이 1개이고 `evidence_refs`에 주기 ID가 있다. `next_actions(cycle)`이 빈 목록이다. 다시 정산해도 계획은 1개다. `unresolved`일 때 봉인 검토의 `decision`이 `'unresolved'`다.
- 대역: `create_autospec(engine._adopted_review_policy, side_effect=...)`.
- 비고: `subTest` 케이스는 `unresolved`, `defer` 둘이다.

## ReviewInputOverflowTests (행 1140–1189)

`unittest.TestCase`를 상속한다. 표지, 속성, 도우미는 없다.

- `setUp` (행 1141–1142): `state_fixtures.start_active_copy(self)`. `restore_template(active_instance, config=ACTIVE_CONFIG)`의 사본(2단)을 받아 `root`, `repo`, `identifier`를 두고, 시험 동안 `adapter_for`를 `FixtureAdapter`로 패치한다.

### `test_actual_proposal_overflow_ends_preparation_and_reaches_plan_input` (행 1144–1189)
- 성질: 실제 제안이 입력 한도를 넘으면 검토 준비는 포장 단계에서 끝나고, 자원 처분(`review_input_overflow`)으로 주기를 닫는다. 그 주기는 다음 계획의 입력으로 원천과 함께 전달되며, 재시작 뒤에도 유지된다.
- 준비: 2단 사본 위에 `ResearchEngine(self.repo, self.identifier)`. 설명을 `max_input_bytes`보다 길게 만든 후보 `KN-overflow`를 `create_candidate`로 만든다. `formal_verification` 대역 결과를 `record_formal_result`로 기록하고 저장한다. `_start_identity_review`로 연다.
- 실행: `next(engine._call_steps(action))`. 이어 계획 행동의 `_context`와 `context_store.prepare_role_input(..., role='research_plan', ...)`을 부르고, 새 `ResearchEngine`으로 다시 적재한다.
- 단언: `_call_steps`가 인자를 내지 않고 `StopIteration`으로 끝난다(러너를 부르지 않는다). 자원 처분의 `reason`이 `'review_input_overflow'`다. 해당 실행은 `('ended', 'packing')`이고 `capacity.process`가 없다. 입력 목록의 `direct` 항목이 모두 저장소에서 읽힌다. 차단 질문 링크가 없다. 계획 입력의 `validation_context.review_followups[0].id`가 주기 ID다. 그 `source_ref.path` 파일의 `proposal_digest`와 `history`가 주기와 같다. `supplied_record_ids`에 주기 ID가 있다. 재시작한 엔진에서 주기 상태가 `'unresolved'`다.
- 대역: `engine_fixtures.formal_verification`(컴파일러 결과 대역). `adapter_for` 패치.
- 비고: 실제 Git 저장소를 쓴다. `json`을 함수 안에서 다시 import한다.

## ImpactReviewRouting (행 1192–1268)

`unittest.TestCase`를 상속하고 표지, 속성, 훅이 없다.

- `fixture` (행 1193–1206): `review_fixtures.ImpactReviewHarness`를 인스턴스로 만들어 `setUp()`을 직접 부른다. 이 하네스는 관측 지식 A·B·C, 실행 중인 생산자 `EX-producer`, A와 C를 고치고 B를 영향 집합으로 선언한 분할 묶음 `IN-held`를 만든다. 행 1194 주석은 "대체 적용 엔진이 아니라 소유자의 실제 도메인 픽스처를 재사용한다"고 밝힌다. 이 상태를 `routing_engine()`에 옮기고 `head='current'`, `workspace='unused'`로 둔다. 생산자를 `research_work` 행동 `AC-held`의 `execution_incomplete`로 끝난 실행으로 바꾼다. 하네스의 영향 검토 요청을 `next_owner='impact_review'`로 담은 수신 결과를 `_hold_impact_reviews`에 넘긴다. `(engine, source, action, request, received)`를 돌려준다.

### `test_exact_request_waits_for_accepted_review_without_new_producer` (행 1208–1231)
- 성질: 보류된 묶음은 정확한 요청에 대한 검토가 수락될 때까지 기다리고, 수락되면 새 생산자 없이 보존된 생산자 결과를 다시 받는다.
- 준비: `fixture()`. 생산자 출력의 사본을 떠 둔다.
- 실행: `_hold_impact_reviews`를 한 번 더 부른다. `_receive_submission`, `_save`, `_settle_activity`를 autospec으로 바꾸고 `_retry_impact_reviews()`를 부른다. 이어 수락된 검토 실행 `EX-review`(하네스의 `review_output`)를 넣고, 저장소를 autospec `ResearchRepository`로(`read`는 `b"{}"`) 바꾼 뒤 다시 부른다.
- 단언: 두 번 보류해도 `impact_review` 행동이 1개다. 그 `input_basis.impact_review`가 요청과 같고 `continuation_of`가 없다. 검토 전 재시도는 `_receive_submission`을 부르지 않는다. 검토 뒤 재시도는 셋째 인자 `'EX-producer'`, `preserved=True`로 부른다. `waiting_actions['AC-held'].review_execution_ids`가 `{'IN-held': 'EX-review'}`다. 생산자 출력은 사본과 같다.
- 대역: `create_autospec`으로 바꾼 `_receive_submission`, `_save`, `_settle_activity`; `patch("do_math.engine.submission.read_sealed_submission", side_effect=...)`(실행의 `output`을 돌려준다); `create_autospec(ResearchRepository, instance=True)`.

### `test_shared_candidate_applies_actual_domain_revision_without_mutating_preview_source` (행 1233–1252)
- 성질: 미리보기와 수신자가 함께 쓰는 도메인 콜백 `_apply_bundle_candidate`는 후보 사본에 실제 개정을 적용하고, 원래 상태는 바꾸지 않는다.
- 준비: `fixture()`. 묶음 사본의 `owns_response`를 거짓으로 하고, 변경마다 `knowledge.revision_roots`와 `plan_impact`로 영향 집합을 다시 계산해 넣는다. 원래 인스턴스의 `canonical_json`을 떠 둔다.
- 실행: 인스턴스·런타임의 깊은 사본에 `_apply_bundle_candidate(candidate, running, bundle, action=..., execution_id='EX-producer', extensions=...)`.
- 단언: 원래 인스턴스의 직렬화가 같다. 후보 지식 가운데 `supersedes`가 있는 행의 대상 집합이 `{A, C}`다. 사본 대기열에 `reason='knowledge currentness changed'` 행이 없다.
- 대역: 없음(행 1244–1245 주석: 저장소·CAS는 따로 시험한다).

### `test_unresolved_review_remains_held_and_has_one_final_rejected_receipt` (행 1254–1268)
- 성질: 영향 검토가 `unresolved`면 묶음은 보류된 채 남고, 거부된 최종 과제 영수증은 두 번 재시도해도 한 번만 기록된다.
- 준비: `fixture()`. 첫 계획 결정을 `unresolved`로 바꾼 검토 출력으로 수락된 `EX-review`를 둔다.
- 실행: `_record_task_receipt`, `_save`, `_receive_submission`을 autospec으로 바꾸고, 저장소를 `git_dir`이 무작위 문자열인 autospec으로 둔 뒤 `_retry_impact_reviews()`를 두 번 부른다.
- 단언: `_receive_submission`은 불리지 않는다. `_record_task_receipt`는 정확히 한 번 `accepted=False`로 불린다. 대기 항목 `kind`가 `'impact_review_blocked'`다. `impact_review` 행동은 여전히 1개다.
- 대역: 위 autospec 셋, `read_sealed_submission` 패치, autospec 저장소.

## AssessmentReassessmentConnections (행 1271–1342)

`unittest.TestCase`를 상속하고 표지, 속성, 훅이 없다.

- `fixture` (행 1272–1276): `review_fixtures.ReassessmentHarness`를 만들어 `setUp()`을 부르고 `self.addCleanup(owner.doCleanups)`을 등록한다. 하네스는 `ReviewFakeEngine`에서 `K1` 검토를 끝까지 돌려 평가를 만들어 둔 상태다. `request(evidence)`는 공개 재평가 요청, `defect()`는 초기 칸 하나의 문맥에 저자 실행을 섞어 넣은 결함 증거, `use()`는 그 평가의 사용 기록, `complete(decision)`은 대기 중인 검토 행동을 모두 인자 `decision`(기본 `'match'`)의 결론이 나도록 답한다. 런타임 상태를 `'ready'`로 둔다.

### `test_central_control_consumes_qualified_evidence_and_retains_bounded_followup` (행 1278–1298)
- 성질: 자격 있는 결함 증거는 중앙 제어가 소비해 재평가를 연다. 재평가가 `unresolved`로 끝나면 활동이 끝나고, 계획 소유의 제한된 후속이 남는다. 새 평가는 공표되지 않는다.
- 준비: `fixture()`.
- 실행: `ResearchEngine._review_recovery_control(engine, {'config': {'role': 'identity_review', 'assessment_reassessment': owner.request(owner.defect())}, ...})`. `owner.complete('unresolved')`를 부르고, 소유 활동의 실행들을 `assign_execution`으로 붙인 뒤 `ResearchEngine._settle_activity(engine, 마지막 실행)`을 부른다.
- 단언: 반환이 참이다. 이력 마지막 결과의 `disposition`이 `'reassessment_opened'`다. 평가 사용 상태가 `'suspended'`다. 활동 상태가 `'finished'`이고, `unresolved[0].next_owner`가 `'research_plan'`이며, `followups[0].revisit_conditions`가 참이다. `identity_assessments`는 1개(원래 평가)뿐이다.
- 대역: 없음.
- 비고: 행 1288–1289 주석은 하네스가 만든 실행을 제품 활동 API로 붙인 뒤 중앙 종료 훅을 부른다고 밝힌다.

### `test_cli_report_reaches_qualified_reassessment_and_replay_is_idempotent` (행 1300–1319)
- 성질: CLI의 `--assessment-reassessment-file` 보고는 자격 있는 재평가에 이르고, 같은 보고를 다시 보내면 이미 열린 재평가를 가리킨다.
- 준비: `fixture()`. 결함 증거로 만든 요청을 파일에 쓴다. `cli.build_parser().parse_args(['request', '--repository', ..., '--instance', 'RI-test', '--assessment-reassessment-file', path])`.
- 실행: `do_math.cli._control`을 `consume`으로 패치하고 `cli.execute(args)`를 두 번 부른다. `consume`은 받은 `text`가 `config['assessment_reassessment']`와 같은지 단언하고, `_review_recovery_control`을 부른 뒤 이력의 결과를 돌려준다.
- 단언: 종료 코드가 0이다. 첫 결과는 `'reassessment_opened'`, 둘째는 `'already_open'`이다. 두 결과의 `review_cycle_id`가 같다. 사용 상태가 `'suspended'`다.
- 대역: `patch("do_math.cli._control", side_effect=consume)`.

### `test_ordinary_report_cannot_suspend_and_closed_control_cannot_open_review` (행 1321–1330)
- 성질: 자격 없는 일반 보고는 평가를 정지시키지 않는다. 닫힌 인스턴스는 재평가를 열 수 없다.
- 준비: `fixture()`. 증거 `{'kind': 'report', 'text': 'Maybe wrong'}`의 요청.
- 실행: `_review_recovery_control`. 이어 런타임 상태를 `'closed'`로 바꾸고 다시 부른다.
- 단언: 첫 결과의 `disposition`이 `'report_only'`이고, 사용 상태가 `'active'`다. 닫힌 뒤 호출은 `ValueError`(`'closed/completed'`; 제품 `'closed/completed instance cannot start an assessment reassessment'`)다.
- 대역: 없음.

### `test_public_admission_binds_original_assessment_hash` (행 1332–1342)
- 성질: 공개 제어 입장은 원래 평가의 해시를 묶으며, 해시가 다르면 거부한다.
- 준비: `fixture()`. 작업 폴더를 하네스 폴더로 두고, `load`가 엔진 상태를 돌려주는 autospec 저장소를 만든다.
- 실행: `do_math.engine.ResearchRepository`를 그 저장소로 패치하고 `control(path, 'RI-test', 'request', config=config)`를 부른다. 이어 `assessment_sha256`을 `'0'*64`로 바꾼 설정으로 다시 부른다.
- 단언: 첫 결과의 `accepted`가 참이다. 둘째는 `ValueError`(`'original judgment'`; 제품 `engine.py`의 `'assessment reassessment must identify the current original judgment'`)다.
- 대역: `create_autospec(ResearchRepository, instance=True)`, `patch("do_math.engine.ResearchRepository", return_value=store)`.

## DelegationConnections (행 1345–1381)

`unittest.TestCase`를 상속하고 표지, 속성, 훅, 도우미가 없다.

### `test_actual_blind_judgments_apply_the_approved_review_recovery` (행 1346–1381)
- 성질: 위임에 기댄 검토 복구 요청은 서로의 판정을 보지 않는 두 판단(해석, 검사)을 대기열에 올린다. 두 판단이 모두 `within_scope`면 적용 기록이 `applied`가 되고 교체 행동이 대기열에 오른다.
- 준비: 임시 폴더의 `ReviewFakeEngine`, `grant_replacement`, 연 주기의 첫 칸에 `permanent_loss` 복구 기록. 사용자 결정 `ORIGINAL`과 위임 `DG`를 `governance.apply_decision`으로 적용한다. 칸 좌표를 담은 효과와 사례 `CASE`를 만든다(`basis_refs=[{'id': cid}]`). `maintenance` 역할의 `review_replacement` 요청(`grant_id`, `delegation_id`, `case`)을 만든다.
- 실행: `ResearchEngine._review_recovery_control`과 `_apply_delegation_judgment`을 `MethodType`으로 엔진에 묶어 요청을 처리한다. 이력에 `user_control` 항목을 더한 뒤, 대기열의 판단 행동 둘마다 실행 기록(프롬프트 해시와 `delegation_input_sha256`)을 두고 `_apply_delegation_judgment`로 `within_scope` 판단을 적용한다.
- 단언: 제어 반환이 참이다. `delegation_application_id`를 가진 대기 행동이 2개다. 적용 기록의 `application.status`가 `'applied'`다. 대기열에 `replacement_for == 0`인 행동이 있다.
- 대역: 없음.
- 비고: 이름의 "blind"(두 판단이 서로의 판정을 받지 않음)는 제품 `engine.py`의 `_review_recovery_control` 주석 "neither receives the other verdict"가 말하는 성질이지만, 이 시험은 판단의 입력을 읽지 않는다. 단언은 판단 행동 수, 적용 상태, 교체 행동만 본다. `ReviewFakeEngine`은 `_review_recovery_control`과 `_apply_delegation_judgment`를 재정의하지 않으므로(`review_fixtures.py` 행 52–188), `MethodType`으로 다시 묶는 두 줄은 동작을 바꾸지 않는다. `ReviewFakeEngine`, `grant_replacement`, `governance`를 함수 안에서 다시 import한다(모듈 머리에도 있다).

## ReviewAttemptAdmissionTests (행 1384–1401)

`unittest.TestCase`를 상속하고 표지, 속성, 훅, 도우미가 없다.

### `test_every_review_owned_attempt_uses_owner_admission_before_registration` (행 1385–1401)
- 성질: 검토 주기가 소유한 모든 시도(보충 조사 포함)는 등록 전에 소유자 입장을 거친다. 입장이 거부되면 실행을 등록하지 않고 그 검토의 자원 처분을 요청한다.
- 준비: `routing_engine()`. `_execution_profile`을 `supplemental_research` 기본 프로필을 돌려주는 autospec으로 바꾼다. `_admit_review_execution`은 `{'disposition': 'review_followup_reserved'}`를 돌려주는 autospec으로, `_request_review_resource_disposition`은 autospec으로 바꾼다. 행동 `{'id': 'AC-review', 'role': 'supplemental_research', 'owner_review_cycle_id': 'RC-one'}`을 대기열에 둔다.
- 실행: `_register_execution(action, {'id': 'EX-attempt', ...})`.
- 단언: 반환값이 `None`이다. 입장 대역이 받은 실행의 `actor_kind`가 `'ai'`이고 `execution_profile_ref`가 그 프로필의 참조다. `EX-attempt`는 실행 기록에 없다. 자원 처분 요청이 `(action, 'review_followup_reserved', {'disposition': 'review_followup_reserved'})`로 정확히 한 번 불린다.
- 대역: 위 autospec 셋.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈:
  - `test_review_cycle`은 순수 검토 주기(`review_cycle.py`)의 단계 전이, 발견·쟁점·판정 규칙을 1단에서 본다. 이 모듈은 그 주기를 엔진이 소유할 때의 입장, 복원, 공표를 본다.
  - `test_review_policy`와 `test_review_scope_wire`는 정책과 범위 평가를 본다. 이 모듈의 `ReviewScopeBudgetTests` 가운데 두 테스트도 1단 정책 함수를 직접 부른다.
  - `test_reassessment`는 재평가의 도메인 규칙을 `ReassessmentHarness`로 본다. 이 모듈의 `AssessmentReassessmentConnections`는 그 하네스를 중앙 제어, CLI, 공개 `control`에 연결한다.
  - `test_impact_review`는 영향 검토 요청과 판정의 도메인을 `ImpactReviewHarness`로 본다. 이 모듈의 `ImpactReviewRouting`은 엔진의 보류·재시도 경로를 본다.
  - `test_delegations`는 위임 적용의 도메인을 본다.
  - `test_review_research`는 검토 중 보충 조사를 같은 `ReviewFakeEngine`과 목적 시나리오로 본다.
  - `test_knowledge`는 신뢰 환경 전환과 복구를, `test_trust_continuation`은 전환의 연속성을 본다.
- 픽스처 의존: `review_fixtures`의 `ReviewFakeEngine`(`ReviewEngineTests`, `DelegationConnections`), `grant_replacement`, `ReassessmentHarness`, `ImpactReviewHarness`. `research_fixtures.start_scoped_review`는 이 모듈과 `review_fixtures`만 쓴다(`consumers.json`). `engine_fixtures.formal_check_engine`은 이 모듈과 `test_formal_engine`이 쓴다. `ReviewPreparationFailureTests`만 `ActivatedPurposeHarness`(2단)를, `ReviewInputOverflowTests`만 `start_active_copy`(2단)를 쓴다.
- 이 모듈에만 있는 도우미: `ReviewEngineTests`의 `staged_transition`, `_staged_activation_git_round_trip`, `open_dispute`, 그리고 `ImpactReviewRouting.fixture`와 `AssessmentReassessmentConnections.fixture`. 모듈 함수는 없다.
- 겹치거나 보완하는 시험: 입장 회계는 세 곳에서 본다. `test_admission_counts_failed_and_retried_executions_before_results`(도메인 수준 입장), `test_exhaustion_drains_only_owned_attempts_before_publishing_followup`(엔진 등록 경로의 소진), `test_every_review_owned_attempt_uses_owner_admission_before_registration`(등록 전 입장 호출)이다. 교체 흐름은 사용자 권한(`test_corrupt_slot_...`, `test_replacement_rejects_...`, `test_approved_replacement_...`)과 위임(`test_checked_delegation_replacement_...`, `DelegationConnections`)으로 나뉜다. 입력 복원 실패는 도메인(`test_restore_diagnostics_...`, `test_tampered_...`, `test_temporary_io_failure_...`)과 2단 엔진(`ReviewPreparationFailureTests`)에서 겹친다.

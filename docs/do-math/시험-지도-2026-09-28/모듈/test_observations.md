# test_observations

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_observations.py` (863행) |
| 클래스 / 테스트 | 4 / 61 |
| 시험 대상 제품 코드 | `do_math/observations.py`: `ObservationTracker`(관찰, 자기 점검 의무와 응답, 제어 결박, 마감 붙잡기, 규칙 교체), `read_checkpoint`, `checkpoint_value`, `preserve_checkpoint`, `persistent_record`, `request_checkpoint`, `write_checkpoint_reminder`, `validate_rules`, `evaluate_rules`, `observation_rule_contract`, `tracker_config`, `self_check_feedback`, `self_check_request`, `worker_feedback`, `OPERATORS`, `WORKER_FEEDBACK_FIELDS`, `CHECKPOINT_SCHEMA`. 이 밖에 `do_math/operational_dispositions.py`의 `validate_disposition`, `worker_feedback`; `do_math/execution_profiles.py`의 `seal_profile`, `build_profiles`, `profile_ref`, `BOUNDARY`; `do_math/submission.py`의 `_captured_checkpoint`, `_workspace_checks`; `do_math/context_store.py`의 `collect_outputs`; `do_math/state_contract.py`의 `default_state_contract`, `validate_record`; 엔진의 `_observe_running` |
| 사용하는 픽스처 모듈 | `research_fixtures`: `acknowledge`, `Clock`, `git_init`, `observation_batch`, `observation_rule`, `observe`, `self_check_response`, `write_checkpoint`, `bare_engine`, `current_state`; `provider_fixtures`: `PROFILE_CONFIG`; `record_fixtures`: `domain_governance`(그리고 쓰이지 않는 `governance_import`) |
| 격리 표지 | 없음 |
| 시작 상태 | 대부분 1단. 임시 작업 공간 위의 `ObservationTracker`에 합성 시계(`Clock`)와 합성 이벤트를 넣는다. 한 시험은 `bare_engine`, 한 시험은 실제 Git 저장소 게시와 재적재를 쓴다 |

## 목적

모듈 docstring은 다음과 같다. "Observation of executions: rules and trackers, self-check obligations and their control-bound responses, and the profile signal contract." 연구 실행 하나를 관찰하는 `ObservationTracker`와 그 주변 계약을 검사한다. 넷으로 나뉜다.

1. `Tests`: 체크포인트 읽기와 보존, 도구 검토 창과 주기·명시 검토, 최대 간격 자기 점검, 응답 검사와 후속, 규칙 제안의 경로, 카운터의 단조성, 알림, 마감 붙잡기, 작업자 피드백 필드, 문서화된 연산자 표.
2. `SelfCheckControlBindingTests`: 자기 점검 응답이 제어 요청(control request)과 수령증(receipt)에 결박되어야 연구 행동이 아닌 것으로 인정된다는 규칙.
3. `ExecutionObservationProfileTests`: 프로필의 신호 종류 계약(`rule_bindings`)과 실행별 카운터 이름의 결박, 저장 뒤 재적재.
4. `ObservationRuleTests`: 규칙 검증과 평가, 응답 마감과 그 붙잡기, 정수 저장, 규칙 이름 변경과 경계 소비, 프로필 입장, 처분 검증.

제품의 연산자 표 `OPERATORS`(observations.py 행 27–34)는 연산자 여섯 개를 둔다. `counter_gte`, `iteration_gte`, `checkpoint_count_gte`(출처 `checkpoint`), `tool_call_completed`(`adapter_calls`), `safe_boundary_recorded`(`control_receipts`), `wall_time_reached`(`clock`, 단위 `UTC`)다. 주석은 "The one operator table"이라고 밝힌다. 카운터와 반복 수는 작업자가 쓴 `checkpoint.json`에서만 관찰된다. 스킬 문서 `references/공통-실행.md`의 연산자 표(행 197 부근)가 규칙 작성자용 사본이며, 그 정본이 `observations.OPERATORS`라고 같은 문서 행 204가 밝힌다.

공통 픽스처의 역할은 다음과 같다(`research_fixtures`).
- `observation_rule(...)`은 규칙 `R-1`을 만든다. 기본값은 카운터 `attempts`를 체크포인트에서 세는 `counter_gte`, 문턱 2, 필수 증거 `["EV-1"]`이다.
- `write_checkpoint`는 유효한 체크포인트를 쓴다.
- `observe`는 추적기의 다음 한 바이트 스트림 좌표로 이벤트를 관찰한다.
- `self_check_response`는 의무의 모든 규칙에 같은 상태를 준 응답을 만든다.
- `acknowledge`는 자기 점검 요청을 발급하고 전달을 기록한 뒤, 작업자의 폴링 호출을 관찰한다.
- `Clock`은 `value`를 돌려주는 설정 가능한 시계다.

## 모듈 수준 요소

- 행 2: `from __future__ import annotations`. 행 12: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 넣는다.
- `profile(bindings)` (행 21–25): `seal_profile`로 합성 AI 프로필을 봉인한다. 역할은 `research_work`, 모델 `test`, 용량 참조 `CP-test`, 관찰 모드 `event_driven`이다. 설정은 도구 검토 60초, 응답 창 5초, 관찰 간격 300초이고, `rule_bindings=bindings`다. `SelfCheckControlBindingTests`의 두 시험이 쓴다.
- `counter_rule(*, source="checkpoint")` (행 28–30): `observation_rule(id="SC-attempts", basis={"source": source, "unit": "count"}, required_evidence=["checkpoint.json"])`. `ExecutionObservationProfileTests`가 쓴다. `source`를 바꾸어 위조 출처를 만든다.
- 행 863: 직접 실행하면 `unittest.main(verbosity=2)`를 부른다.

## Tests (행 33–443)

`unittest.TestCase`를 그대로 상속한다. 표지와 클래스 속성이 없다.

- `setUp` (행 34–39): 임시 폴더 `self.ws`와 `Clock()`을 만든다. 설정 `self.config`는 `observation_rules=[observation_rule(repeat_interval=2)]`, 응답 창 5초, 도구 검토 창 60초, 관찰 간격 300초다. 추적기 `self.t = ObservationTracker("E", self.ws, self.config, clock=self.clock)`를 둔다. 모드는 기본값 `event_driven`이고, 규칙 개정은 0에서 시작한다.
- `tearDown` (행 41): 임시 폴더를 정리한다.
- `assert_persisted_notice(record)` (행 43–47): 상태 계약의 `runtime`/`observations` 가족 스키마로 `{execution_id: persistent_record(record)}`를 `jsonschema.validate`한다. 추적기가 낸 알림이 그대로 저장될 수 있음을 확인한다.
- `write(**changes)` (행 49–52): 작업 공간에 체크포인트를 쓴다. 기본 필드는 `current_claim="c"`, 빈 `evidence_paths`·`attempts`·`remaining_work`, `next_step="n"`, `progress_state="working"`이다.
- `due()` (행 54–57): 체크포인트에 `counters={"attempts": 2}`를 쓰고 `tick`을 관찰해 `self_check_due` 행을 돌려준다. 주석은 "Counters reach the tracker only through the worker's checkpoint."다.

### `test_repeated_checkpoint_reads_reuse_schema_but_recheck_value_and_evidence` (행 59–75)
- 성질: 체크포인트를 반복해 읽을 때 스키마 자체의 검증은 다시 하지 않지만, 값과 증거 파일의 존재는 매번 다시 확인한다.
- 준비: 기본 체크포인트. `CHECKPOINT_SCHEMA`의 검증기 클래스의 `check_schema`를 호출 수를 세는 래퍼로 바꾼다.
- 실행: `read_checkpoint`를 20번 부른다. 이어서 네 경우에 부른다. `progress_state="invented"`, 없는 증거 `proof.txt`, 증거 파일 생성 뒤, 증거 파일 삭제 뒤다.
- 단언: 20번 모두 `valid`다. 이어서 `invalid`, `invalid`, `valid`, `invalid` 순이다. `check_schema` 호출 수가 1 이하다.
- 대역: `patch.object(validator, "check_schema", wraps=...)`.
- 비고: 제품은 모듈 적재 때 검증기 `_CHECKPOINT_VALIDATOR`를 한 번 만든다(행 78). 그래서 이 구간의 호출 수는 0이다.

### `test_live_polling_rereads_the_checkpoint_only_after_a_change` (행 77–95)
- 성질: 실시간 폴링은 유효하게 읽은 체크포인트의 지문이 그대로면 다시 읽지 않는다. 유효하지 않은 읽기는 기억하지 않는다. 명시된 증거가 나중에 생길 수 있기 때문이다.
- 준비: 증거 `proof.txt`를 명시한 체크포인트(파일은 아직 없음). `file_io.RACY_NS`를 0으로 둔다(주석: 새 파일의 생성 시각은 나이를 먹일 수 없으므로 지난 지문을 모두 안정된 것으로 취급).
- 실행: `self.t._changed_checkpoint()`를 차례로 부른다. 처음, 증거 파일 생성 뒤, 다시 한 번이다. 그 뒤 체크포인트를 `next_step="later"`로 다시 쓰고 수정 시각을 1초 뒤로 옮긴 다음 한 번 더 부른다.
- 단언: 결과가 `invalid`, `valid`, `unchanged` 순이고, 이때까지 `read_checkpoint` 호출 수가 2다. 재작성 뒤 결과가 `valid`이고 호출 수가 3이다.
- 대역: `patch.object(file_io, "RACY_NS", 0)`, `patch.object(observations, "read_checkpoint", wraps=...)`.
- 비고: 제품 docstring(행 800–805)은 "Only a valid read is remembered: an invalid one can become valid when its named evidence appears, so it is read again."이다.

### `test_duplicate_checkpoint_keys_are_invalid_live_and_at_final_capture` (행 97–114)
- 성질: JSON 키가 중복된 체크포인트는 실시간 읽기와 최종 포착 모두에서 유효하지 않다. 최종 보존은 이전의 유효한 체크포인트를 유지하고 새 산출물을 만들지 않는다.
- 준비: `current_claim="last valid"`, `counters={"attempts": 1}`인 체크포인트를 쓰고, `preserve_checkpoint(..., artifact_prefix="runtime/artifacts/prior")`로 이전 보존을 만든다. 원래 바이트에서 두 변형을 만든다. 하나는 `current_claim` 키가 두 번 나오고, 다른 하나는 `attempts` 키가 두 번 나온다.
- 실행: 변형마다 체크포인트 파일에 쓰고 `read_checkpoint`, `submission._captured_checkpoint({"checkpoint.json": malformed})`, `preserve_checkpoint(..., previous=prior, artifact_prefix="runtime/artifacts/final")`을 부른다.
- 단언: 앞의 둘이 `invalid`다. 보존 결과의 `sha256`이 이전 보존의 값과 같고, `final_observation.checkpoint_status == "invalid"`이며, 산출물 사전이 비어 있다.
- 대역: 없음.
- 비고: 중복 키가 뒤의 값으로 조용히 덮이지 않도록, 제품은 엄격한 JSON 적재(`strict_json_loads`)를 쓴다(`checkpoint_value`, 행 399–408). 실시간 추적기, 수신자 포착 검사, 산출물 형식 검사가 이 한 규칙을 공유한다.

### `test_checkpoint_rejects_numbers_outside_the_storage_value_domain` (행 116–128)
- 성질: 체크포인트의 수는 저장 값 영역 안의 정수여야 한다. 실수 표기의 정수와 2^53 이상은 거부된다. 유효한 정수는 저장 기록에 그대로 남는다.
- 준비: `subTest`로 세 경우. `iteration=1.0`, `counters={"attempts": 2.0}`, `iteration=2**53`.
- 실행: 각 경우 `read_checkpoint`. 이어서 `iteration=1`, `counters={"attempts": 2}`로 읽고 `persistent_record(checkpoint, artifact_ref=...)`.
- 단언: 세 경우 모두 `invalid`다. 유효한 경우 `valid`이고, 저장 기록의 `value.iteration == 1`, `value.counters == {"attempts": 2}`다.
- 대역: 없음.

### `test_checkpoint_requires_available_preserved_evidence_paths` (행 130–138)
- 성질: 체크포인트가 명시한 증거 경로는 실제 파일이어야 하고, 보존에서 제외되는 경로(`.scratch/`)는 증거가 될 수 없다.
- 준비: `evidence_paths=["proof.txt"]`인 체크포인트.
- 실행: `read_checkpoint`를 세 번 부른다. 파일 없음, `proof.txt` 생성 뒤, `.scratch/proof.txt`를 만들고 증거 경로를 그것으로 바꾼 뒤다.
- 단언: `invalid`, `valid`, `invalid` 순이다.
- 대역: 없음.
- 비고: 제품 메시지는 `"checkpoint evidence is unavailable or excluded from preservation: ..."`다(행 424–428). 이 시험은 상태만 보고 메시지는 보지 않는다.

### `test_checkpoint_is_refused_through_a_workspace_reparse_point` (행 140–160)
- 성질: 체크포인트는 다른 작업 공간 파일과 같은 경로 규칙(`context_store.safe_path`)을 따른다. 경로에 정션이 있으면, 그 정션이 작업 공간 안으로 되돌아가더라도 거부된다.
- 준비: `ws/real/checkpoint.json`에 유효한 체크포인트를 쓴다. Windows에서는 `cmd.exe /d /c mklink /J <link> <real>`로 정션을 만들고 반환 코드 0을 단언한다. 그 밖의 OS에서는 디렉터리 심볼릭 링크를 만든다.
- 실행: `read_checkpoint(real)`와 `read_checkpoint(link)`.
- 단언: 앞은 `valid`, 뒤는 `invalid`이고, 뒤의 `error`가 정규식 `"reparse|symlink"`에 맞는다.
- 대역: 없음.
- 비고: 정션을 만들기 위해 실제 자식 프로세스 `cmd.exe`를 실행한다. `finally`에서 링크만 지운다(Windows는 `os.rmdir`). 주석(행 160)은 "Only the link, not its target."이다.

### `test_invalid_partial_missing_checkpoint_and_stop_request` (행 162–169)
- 성질: 체크포인트가 없으면 `missing`, 디코딩할 수 없거나 필수 필드가 빠졌으면 `invalid`다. 정지 요청은 새 연구를 시작하지 말라는 지시를 담아 제어 폴더에 파일로 남는다.
- 준비: 빈 작업 공간.
- 실행: `read_checkpoint`. 이어서 `b'\xff'`와 `b'{"current_claim":"partial"}'`을 차례로 쓰고 읽는다. `request_checkpoint(self.ws, "stop", immediate=True, deadline="2026-01-01T00:00:00Z")`.
- 단언: 처음은 `missing`이고, 두 경우는 `invalid`다. 요청의 `instruction`에 `"Do not start new research"`가 있다. `.control/stop-request.json`이 파일로 존재한다.
- 대역: 없음.

### `test_transport_ping_and_idle_do_not_create_math_failure_or_review` (행 171–175)
- 성질: 전송 수준의 이벤트(tick, ping, 수신 바이트)와 유휴 시간은 수학적 실패나 검토를 만들지 않는다.
- 준비: 시계 200초. 최대 자기 점검 간격(300초)은 아직 닿지 않았다.
- 실행: `{"type": "tick"}`, `{"type": "ping"}`, `{"type": "transport_bytes_received", "bytes": 100}`을 차례로 관찰한다.
- 단언: 어떤 행도 종류에 `"review"`를 담지 않고, `self_check_due`도 아니다.
- 대역: 합성 시계.

### `test_frozen_window_ignores_worker_timeout_and_mutated_input_config` (행 177–187)
- 성질: 도구 검토 창은 추적기를 만들 때 고정된다. 호출자가 설정 사전을 나중에 바꾸거나, 작업자의 도구 입력이 시간 제한이나 창 값을 주어도 따르지 않는다.
- 준비: 추적기를 만든 뒤 `self.config`의 `tool_review_window_seconds`를 1로, 모드를 `periodic`으로 바꾼다.
- 실행: `timeout: 1`과 `observation_review_window_seconds: 1`을 입력에 가진 `Bash` 도구 호출(`id="C"`)을 관찰한다. 시계 2초에서 tick, 60초에서 tick, 다시 tick.
- 단언: 2초의 결과가 빈 목록이다. 60초의 `tool_review_due` 행들의 `window_ms`가 `[60000]`이고, 그 행이 저장 스키마를 통과한다. 마지막 tick은 빈 목록이다(한 호출에 한 번만 검토).
- 대역: 합성 시계.
- 비고: 추적기는 생성자에서 설정을 `deepcopy`한다(행 460).

### `test_adapter_completion_matches_exact_call_and_duplicate_start_cannot_delay` (행 189–198)
- 성질: 도구 호출의 완료는 정확히 같은 호출 ID로만 짝지어지고, 같은 호출의 중복 시작 이벤트는 검토 시각을 늦추지 못한다.
- 준비: 기본 추적기.
- 실행: 0초에 `command_execution` `C` 시작, 50초에 같은 시작 재관찰, `OTHER` 완료 관찰. 60초에 tick. 이어서 Claude 모양의 `tool_result`(`tool_use_id="C"`) 관찰.
- 단언: 60초의 `tool_review_due` 호출 ID 목록이 `["C"]`다(0초 기준 60초 창). `completed_call_ids == {"C", "OTHER"}`, `pending_tools == {}`다.
- 대역: 합성 시계.

### `test_periodic_and_explicit_reviews_have_independent_bases` (행 200–209)
- 성질: 주기 검토와 명시 예약 검토는 서로 다른 기준으로 도래하며, 같은 시점에 둘 다 나올 수 있다. 각각 한 번만 나온다.
- 준비: `periodic` 모드, 관찰 간격 3초의 추적기 `P`. `schedule_review("RECHECK", at="2026-09-20T10:00:00Z", reason=..., basis_ref="DISP-1")`.
- 실행: 시계 3초에서, `observations.now`를 `"2026-09-20T10:00:00+00:00"`로 패치한 채 tick을 두 번 관찰한다.
- 단언: 첫 결과의 종류 집합이 `{"periodic_review_due", "explicit_review_due"}`이고, 모든 행이 저장 스키마를 통과한다. 두 번째 결과는 빈 목록이다.
- 대역: 합성 시계, `patch.object(observations, "now", ...)`.

### `test_deadline_only_never_opens_recursive_review` (행 211–217)
- 성질: `deadline_only` 모드의 추적기는 도구 검토도 주기 검토도 열지 않고, 명시 검토 예약도 거부한다.
- 준비: `deadline_only` 모드, 관찰 간격 1초, 도구 검토 창 1초의 추적기 `D`.
- 실행: 호출 `C` 시작을 관찰하고, 시계 100초에서 tick. `schedule_review(...)`.
- 단언: tick 결과가 빈 목록이다. `schedule_review`는 `ValueError`다(메시지는 보지 않는다).
- 대역: 합성 시계.
- 비고: 이름의 "recursive review"는, 이 모드가 운영 점검 같은 검토 실행 자신을 관찰할 때 다시 검토를 열지 않는다는 뜻으로 읽힌다. 시험은 검토 행이 나오지 않는다는 것만 본다.

### `test_maximum_interval_opens_self_check_and_valid_response_reanchors` (행 219–233)
- 성질: 조건이 도래하지 않아도 최대 간격이 지나면 자기 점검 의무가 열린다. 유효한 응답은 다음 최대 간격의 기준을 응답 시각으로 옮긴다. 같은 응답의 재제출은 거부되고 기준을 바꾸지 않는다.
- 준비: 기본 추적기. 체크포인트는 없다.
- 실행: 시계 300초에서 tick. 다시 tick. 시계 301초에서 `self_check_response(obligation)`을 기록하고, 같은 응답을 한 번 더 기록한다.
- 단언: 300초 결과 가운데 `observation_unavailable` 행은 저장 스키마를 통과한다. `self_check_due`의 첫 규칙 ID가 `"@maximum_interval"`이다. 두 번째 tick은 빈 목록이다. 첫 응답 결과의 `next_self_check_offset_ms == 601000`이다(301초 + 300초). 재제출의 `kind == "self_check_rejected"`이고, 추적기의 `next_self_check_offset_ms`가 여전히 601000이다.
- 대역: 합성 시계.

### `test_missed_self_check_notification_matches_persisted_contract` (행 235–240)
- 성질: 응답 창이 지나면 자기 점검 미응답 알림이 나오고, 그 알림은 저장 계약을 통과한다.
- 준비: `self.due()`로 의무를 연다(응답 창 5초).
- 실행: 시계 6초에서 tick.
- 단언: `self_check_missed` 행의 `obligation_id`가 의무 ID이고, 저장 스키마를 통과한다.
- 대역: 합성 시계.

### `test_response_coverage_identity_revision_and_current_evidence` (행 242–249)
- 성질: 자기 점검 응답은 실행 ID, 규칙 개정, 모든 도래 규칙의 결과, 의무 ID가 맞아야 하고, 인용한 증거가 현재 가용해야 한다. 거부된 응답은 의무를 닫지 않는다.
- 준비: `self.due()`.
- 실행: 네 변형 응답을 기록한다. `execution_id="OTHER"`, `rule_revision=99`, `rule_results=[]`, `obligation_id=[]`다. 이어서 정상 응답을 가용 증거 빈 집합으로 기록한다.
- 단언: 네 변형 모두 `self_check_rejected`다(사유는 보지 않는다). 마지막 결과의 `errors`에 `"evidence_not_current"`가 있다. 의무의 `status == "open"`이다.
- 대역: 합성 시계.

### `test_normal_defect_indeterminate_followups` (행 251–260)
- 성질: 자기 점검 응답의 상태에 따라 후속이 정해진다. `normal`이면 계속하고, `defect`와 `indeterminate`면 운영 점검을 연다.
- 준비: 체크포인트 `attempts=2`. `subTest`마다 이름이 상태인 새 추적기를 같은 설정으로 만든다.
- 실행: tick으로 의무를 열고, 해당 상태의 응답을 기록한다. `indeterminate`는 증거를 빈 목록으로 주고, 필수 증거를 누락 증거로 싣는다.
- 단언: 결과의 `kind == "self_check_received"`이고, `followup.kind`가 `continue`, `operational_review_due`, `operational_review_due` 순이다.
- 대역: 합성 시계.

### `test_a_rules_file_in_the_workspace_is_not_a_replacement_path` (행 262–271)
- 성질: 작업 공간의 규칙 파일은 관찰 규칙을 바꾸지 않고 알림도 만들지 않는다. 규칙을 바꾸는 경로는 자기 점검 응답의 `rule_proposal` 하나뿐이다.
- 준비: `observation-rules.json`에 유효한 모양의 제안(`current_revision=0`, 규칙 `R-new`)을 쓴다.
- 실행: tick.
- 단언: 결과에 `observation_rules_rejected`가 없다. 규칙이 설정과 같고, 개정이 0이며, `next_self_check_offset_ms`가 300000이다.
- 대역: 합성 시계.
- 비고: 원문 주석(행 263–264)이 규칙을 밝힌다: "Only a self-check response's rule_proposal replaces rules; a workspace file is ordinary output that neither replaces them nor draws a notice."

### `test_valid_response_accepts_rules_but_bad_proposal_keeps_previous` (행 273–280)
- 성질: 유효한 자기 점검 응답에 실린 제안이 낡은 개정을 가리키면, 응답은 받아들여지고 제안만 거부되며 이전 규칙이 유지된다.
- 준비: `self.due()`. 응답에 `rule_proposal={"current_revision": 99, ...}`를 싣는다.
- 실행: 응답을 기록한다.
- 단언: `kind == "self_check_received"`, `rule_update.kind == "observation_rules_rejected"`, 규칙 개정이 0이다.
- 대역: 합성 시계.

### `test_rule_proposal_travels_in_the_response_and_a_rules_file_is_not_checked` (행 282–299)
- 성질: 규칙 제안은 응답 안에서만 효력을 가진다. 작업 공간의 `observation-rules.json`은 어떤 모양이든 규칙 의미가 없으므로, 실시간 검사도 포착된 제출 검사도 그 파일을 검사하지 않는다.
- 준비: `self.due()`. 이름을 바꾼 규칙(`renamed`, 반복 2)의 제안.
- 실행: 제안을 실은 응답을 기록한다. 이어서 세 모양을 차례로 파일에 쓴다. 제안 전체, 규칙 목록만, `current_revision=-1`인 제안이다. 각 모양마다 `submission._workspace_checks(context, ws, candidate=...)`를 두 번 부른다. 한 번은 `candidate=None`(실시간)이고, 한 번은 `collect_outputs(ws)`(포착)다.
- 단언: 규칙 갱신이 `observation_rules_accepted`다. 여섯 검사 모두 `issues == []`다. 끝에 규칙 개정이 1이다.
- 대역: 합성 시계. 문맥은 `{"submission_contract": {"limits": {"max_artifact_bytes": 100000}}}`다.

### `test_tracker_records_leave_through_the_storage_check` (행 301–312)
- 성질: 추적기가 엔진에 넘기는 기록(응답 기록, 저장용 의무)은 저장 관문의 검사기를 통과한다. 저장 계약에 없는 필드가 의무에 끼면 저장용 사본을 만들 때 거부된다.
- 준비: `self.due()`. 규칙 제안을 실은 응답.
- 실행: 응답을 기록한다. `validate_record(default_state_contract().family("runtime", "self_check_responses").checker, record, "response")`. `stored_obligations()`. 의무에 `bookkeeping=[]`를 더한 뒤 다시 `stored_obligations()`.
- 단언: 검사기가 예외 없이 통과한다. `stored_obligations()`가 `obligations`와 같다. 필드를 더한 뒤에는 `ValueError`(메시지 `"bookkeeping"`)다.
- 대역: 합성 시계.
- 비고: docstring은 "The tracker runs the storage gate's own checker on what ENGINE saves (이음새-정본.md §6)."이다.

### `test_malformed_rule_proposal_does_not_reject_valid_self_check` (행 314–319)
- 성질: 형식이 틀린 규칙 제안(정수가 아닌 문턱 1.5)은 제안만 거부되고, 유효한 자기 점검 응답은 받아들여진다.
- 준비: `self.due()`. `threshold=1.5`인 규칙의 제안.
- 실행: 응답을 기록한다.
- 단언: `kind == "self_check_received"`, `rule_update.kind == "observation_rules_rejected"`.
- 대역: 합성 시계.

### `test_invalid_checkpoint_counters_do_not_partially_advance` (행 321–328)
- 성질: 한 체크포인트의 카운터 가운데 하나라도 줄면 그 체크포인트의 카운터는 하나도 반영되지 않는다.
- 준비: `counters={"attempts": 1, "branches": 5}`를 쓰고 tick한다.
- 실행: `counters={"attempts": 2, "branches": 4}`를 쓰고 tick한다.
- 단언: 결과에 `checkpoint_observation_rejected`가 있다. 카운터가 `{"attempts": 1, "branches": 5}` 그대로다. 의무가 없다. 카운터가 반영되지 않았으므로 `attempts`가 문턱 2에 닿지 않은 것이다.
- 대역: 합성 시계.
- 비고: 제품 `_merge_monotonic`(행 533–543)은 모든 값을 먼저 검사한 뒤 한 번에 갱신하며, 메시지는 `"checkpoint counters cannot decrease"`다.

### `test_provider_event_counters_are_not_observation_signals` (행 330–335)
- 성질: 제공자 이벤트에 실린 카운터, 반복 수, 활성 시간은 관찰 신호가 아니다.
- 준비: 기본 추적기.
- 실행: `counters`, `iterations`, `active_duration_ms`, `id`를 가진 tick 이벤트를 관찰한다.
- 단언: 추적기의 `counters`와 `iterations`가 비어 있고, `self_check_due`가 없다.
- 대역: 합성 시계.

### `test_no_progress_limit_keeps_count_across_rule_replacement` (행 337–349)
- 성질: 연속 무진전 횟수는 규칙을 교체해도 초기화되지 않는다. 한도에 닿으면 반복 무진전 후속이 나오고, 운영 점검 확인이 횟수를 0으로 되돌린다.
- 준비: `no_progress_limit=2`인 추적기.
- 실행: 카운터 2와 4에서 각각 의무를 열고 `progress="no_progress"` 응답을 기록한다. 첫 응답에는 규칙 이름을 `R-new`로 바꾸는 제안을 싣는다. 이어서 `tracker.acknowledge_review(observation_refs=[result["id"]])`.
- 단언: 각 결과의 `no_progress_count`가 1, 2다. 마지막 결과의 `followup.trigger == "repeated_no_progress"`다. 확인 뒤 `no_progress_count == 0`이다.
- 대역: 합성 시계.

### `test_actual_checkpoint_counters_and_iterations_repeat_without_recounting_bytes` (행 351–360)
- 성질: 반복 규칙은 실제 체크포인트의 카운터가 다음 경계에 닿을 때마다 다시 도래한다. 반복 수는 실행 ID를 키로 기록된다. 이미 본 체크포인트 바이트는 다시 세지 않는다.
- 준비: `counters={"attempts": 2}`, `iteration=3`.
- 실행: tick, tick. `attempts=4`, `iteration=4`로 바꾸고 tick. 처음 내용(`attempts=2`, `iteration=3`)으로 되돌리고 tick.
- 단언: 첫 tick에 `self_check_due`가 있고, `iterations == {"E": 3}`이며, 둘째 tick은 빈 목록이다. 셋째 tick에 `self_check_due`가 있다(반복 간격 2). 마지막에 `checkpoint_count == 2`다.
- 대역: 합성 시계.
- 비고: 제품은 본 체크포인트의 SHA-256을 `seen_checkpoints`에 기억한다(행 975–976). 그래서 처음과 같은 바이트는 세지도 병합하지도 않는다.

### `test_self_check_calls_and_checkpoints_do_not_trigger_themselves` (행 362–374)
- 성질: 자기 점검 제어 호출은 완료된 연구 호출로 세지 않는다. 자기 점검 계보로 등록된 체크포인트는 체크포인트 수에 들지 않는다.
- 준비: `self.due()`로 연 의무를 `answered`로 둔다.
- 실행: `execution_control`/`control_self_check` MCP 호출 완료(`SC-CALL`)를 `evaluate=False`로 관찰한다. 체크포인트를 새로 쓰고, 그 SHA-256을 `register_self_check_checkpoint`로 등록한 뒤 tick한다.
- 단언: `SC-CALL`이 `completed_call_ids`에 없다. 체크포인트 수가 등록 전과 같다.
- 대역: 합성 시계.

### `test_reminder_is_once_and_does_not_replace_existing_feedback` (행 376–380)
- 성질: 체크포인트 알림 파일은 한 번만 쓰이고, 이미 있는 피드백을 덮어쓰지 않는다.
- 준비: 빈 작업 공간.
- 실행: `write_checkpoint_reminder(self.ws)`를 두 번 부른다.
- 단언: 처음은 참, 둘째는 거짓이다. `.control/observation-feedback.json`의 `reason`에 `"current_claim"`이 있다.
- 대역: 없음.
- 비고: 이름의 "does not replace existing feedback"은 두 번째 호출이 거짓을 돌려준다는 단언으로만 확인된다. 다른 피드백이 먼저 있는 경우는 시험하지 않는다.

### `test_missing_checkpoint_reminder_only_for_checkpointing_roles` (행 382–387)
- 성질: 체크포인트 알림은 체크포인트를 쓰는 역할(`checkpoint_expected=True`)에만, 그리고 한 번만 도래한다.
- 준비: `checkpoint_expected=True`인 추적기 `W`와 기본 추적기. 시계 300초.
- 실행: `W`에서 tick 두 번, 기본 추적기에서 tick 한 번.
- 단언: `W`의 첫 tick에만 `checkpoint_reminder_due`가 있다. 기본 추적기에는 없다.
- 대역: 합성 시계.

### `test_engine_answers_reminder_without_opening_model_review` (행 389–408)
- 성질: 엔진은 체크포인트 알림 도래를 기계적으로 처리한다. 작업 공간에 알림 파일을 쓰고, 모델 검토 행동은 대기열에 넣지 않는다.
- 준비: `ws/runs/E/workspace`를 만든다. `bare_engine({"workspace": ws}, {"status": "running", "executions": {"E": {}}})`의 `_controls`, `_check_conversations`, `_save`, `_unchanged`, `_publish_observation`, `_review_observation_source`를 `create_autospec` 대역으로 바꾼다. `_enqueue`는 호출을 목록에 기록한다. 추적기의 `observe`는 `[{"kind": "checkpoint_reminder_due", "execution_id": "E"}]`를 돌려주는 람다로 바꾼다(주석: 이 시험은 추적기 시각이 아니라 엔진의 알림 처리를 본다).
- 실행: `engine._observe_running("E", tracker, observation_batch(received_monotonic=..., stream_path=<workspace>/stdout.jsonl))`.
- 단언: `<workspace>/.control/observation-feedback.json`이 있다. `_enqueue` 호출 기록이 비어 있다.
- 대역: 위의 `create_autospec` 대역들, 추적기 메서드 대체, `observation_batch`(빈 이벤트 묶음).

### `test_obligation_opened_during_a_research_call_is_held_until_the_call_ends` (행 410–422)
- 성질: 연구 호출이 도는 중에 열린 의무의 마감은 호출이 끝날 때까지 붙잡힌다. 호출이 끝나면 붙잡힌 시간만큼 마감이 늘어나며, 응답 전에 안전 경계가 필요 없다.
- 준비: 호출 `C` 시작을 관찰한 뒤 `self.due()`.
- 실행: 시계 30초에서 tick. 호출 `C` 완료를 관찰. 응답을 기록한다.
- 단언: 의무를 연 직후 `(deadline_offset_ms, deadline_held_offset_ms) == (5000, 0)`다. 30초 tick에 `self_check_missed`가 없다. 완료 뒤 `deadline_offset_ms == 35000`이고 붙잡기 키가 없다. 응답이 `self_check_received`다(실패 시 `errors`를 보인다).
- 대역: 합성 시계.
- 비고: 제품 `_hold_deadlines`(행 762–777)의 docstring은 "A worker busy in a tool call cannot read or answer the request, so the time a hold lasts is added to the deadline."이다.

### `test_feedback_producers_share_the_public_field_set` (행 424–432)
- 성질: 작업자에게 가는 피드백은 공개 필드 집합만 쓴다. 비공개 필드는 거부된다. 자기 점검 요청은 의무에서 파생된 정본 모양과 같다. 전달 좌표는 음수일 수 없다.
- 준비: `self.due()`.
- 실행: `observations.worker_feedback({"kind": "x", "diagnostic": "private"})`, `self_check_feedback(obligation)`, `issue_self_check(obligation_id)`, `record_delivery(obligation_id, source_offset=-1)`.
- 단언: 첫 호출은 `ValueError`(메시지 `"private or unknown"`)다. 피드백의 키가 `WORKER_FEEDBACK_FIELDS`의 부분집합이다. 발급한 요청이 `self_check_request(<현재 의무>)`와 같다. 음수 좌표는 `ValueError`(메시지 `"nonnegative"`)다.
- 대역: 합성 시계.

### `test_explicit_null_repeat_is_not_a_positive_repeat_interval` (행 434–435)
- 성질: 명시적 `repeat_interval=None`은 양의 반복 간격이 아니므로 규칙 검증에서 거부된다.
- 준비: `observation_rule(repeat_interval=None)`.
- 실행: `observations.validate_rules([...])`.
- 단언: `ValueError`다(메시지는 보지 않는다).
- 대역: 없음.

### `test_documented_operator_table_is_the_operator_table` (행 437–443)
- 성질: 스킬 문서 `references/공통-실행.md`의 연산자 표는 `observations.OPERATORS`와 정확히 같다.
- 준비: 스킬 폴더(`tests/`의 두 단계 위)의 `references/공통-실행.md`를 읽는다.
- 실행: 정규식 ``^\| `(\w+)` \| `(\w+)` \| `(\w+)`, `(\w+)` \|$``로 행을 뽑아 `{operator: {subject_kind, unit, source}}`를 만든다.
- 단언: 그 사전이 `observations.OPERATORS`와 같다.
- 대역: 없음.
- 비고: docstring은 "「공통 실행」's operator table is the rule authors' copy of observations.OPERATORS."다. 문서 행의 셋째 칸은 `` `출처`, `단위` `` 순서로 적힌다(문서 행 197 `| `counter_gte` | `counter` | `checkpoint`, `count` |`). 문서와 제품의 표가 어긋나면 이 시험이 잡는다.

## SelfCheckControlBindingTests (행 446–532)

`unittest.TestCase`를 그대로 상속한다. 표지와 속성이 없다.

- `setUp` (행 447–450): 임시 작업 공간 `self.ws`와 `Clock()`을 만든다.
- `tearDown` (행 451): 임시 폴더를 정리한다.
- `tracker()` (행 453–455): `ObservationTracker("EX-1", self.ws, {observation_rules: [observation_rule()], tool_review_window_seconds: 60, self_check_response_window_seconds: 5}, clock=self.clock)`.
- `submission(tracker)` (행 457–467): 체크포인트 `attempts=2`로 의무를 연다. `acknowledge(tracker, id)`로 요청을 발급하고 전달한 뒤 작업자의 폴링을 관찰한다. 주석은 "The worker has polled the delivered request: a research action from here misses it."이다. 그 뒤 세 값을 돌려준다.
  - 정상 응답 `response`.
  - 제어 요청 `request`. `request_id="self-check-<의무 ID>"`, `execution_id="EX-1"`, `kind="self_check_response"`, `payload={self_check_id, response}`다.
  - 어댑터 이벤트 `event`. `item.started`의 `mcp_tool_call`이며, `id="CALL-SC"`, `server="execution_control"`, `tool="control_self_check"`, 인자는 의무 ID와 응답이다.

### `test_real_control_submission_is_not_research_action` (행 469–478)
- 성질: 신뢰된 제어 서버의 자기 점검 제출 호출은 연구 행동이 아니므로 열린 요청의 미응답을 일으키지 않는다. 수령증에 결박된 응답은 받아들여진다.
- 준비: `self.submission(tracker)`.
- 실행: 이벤트를 관찰한다. `bind_control_request(request, receipt_id="CT-1")`. 응답을 `receipt_id="CT-1"`로 기록한다.
- 단언: 관찰 결과에 `self_check_missed`가 없다. 응답이 `self_check_received`다. `CALL-SC`가 `self_check_call_ids`에 있다. `control_requests[request_id].receipt_id == "CT-1"`이다.
- 대역: 합성 시계.

### `test_receipt_before_adapter_event_and_claude_shape` (행 480–487)
- 성질: 수령증 결박이 어댑터 이벤트보다 먼저 와도 되고, Claude 모양의 도구 사용 이벤트(`mcp__execution_control__control_self_check`)도 같은 제어 호출로 인정된다.
- 준비: `self.submission(tracker)`.
- 실행: 먼저 `bind_control_request(request, receipt_id="CT-1")`. 이어서 `assistant` 메시지의 `tool_use`(같은 호출 ID, 이름 `mcp__execution_control__control_self_check`, 같은 인자)를 관찰한다. 응답을 수령증과 함께 기록한다.
- 단언: 응답이 `self_check_received`다.
- 대역: 합성 시계.

### `test_unbound_or_different_control_request_cannot_acknowledge_response` (행 489–497)
- 성질: 수령증에 결박되지 않은 응답은 확인되지 않은 제어 요청으로 거부된다. 제출된 응답과 다른 내용의 제어 요청은 결박할 수 없다.
- 준비: `self.submission(tracker)`. 이벤트를 관찰한다.
- 실행: 수령증 없이 응답을 기록한다. 요청 사본의 `payload.response.next_method`를 `"different"`로 바꾸고 `bind_control_request(altered, receipt_id="CT-2")`.
- 단언: 첫 결과의 `errors`에 `"control_request_unconfirmed"`가 있다. 결박은 `ValueError`다(메시지는 보지 않는다).
- 대역: 합성 시계.

### `test_other_control_submit_and_wrong_server_remain_research_actions` (행 499–506)
- 성질: 자기 점검 응답이 아닌 제어 제출(`control_submit`의 `submission_preview`)과 신뢰되지 않은 서버의 호출은 연구 행동으로 보며, 열린 요청을 놓친 것이 된다.
- 준비: 두 경우마다 새 추적기에 `self.submission`. (1) 서버를 `"untrusted"`로 바꾼다. (2) 도구를 `control_submit`, 인자를 `{"request_id": "P", "kind": "submission_preview", "payload": {}}`로 바꾼다.
- 실행: 바꾼 이벤트를 관찰한다.
- 단언: 두 경우 모두 결과에 `self_check_missed`가 있다.
- 대역: 합성 시계.
- 비고: `subTest`가 아닌 반복문이다. 실패 메시지는 어느 경우인지 밝히지 않는다.

### `test_missing_profile_observability_contract_is_not_support` (행 508–509)
- 성질: 신호 종류 계약(`rule_bindings`)이 빈 프로필은 관찰을 지원하지 않으므로 추적기 설정을 만들 수 없다.
- 준비: `profile([])`.
- 실행: `tracker_config(profile([]), initial_self_check_rules=[observation_rule()])`.
- 단언: `ValueError`다(메시지는 보지 않는다).
- 대역: 없음.

### `test_checkpoint_counter_rule_ignores_counters_from_another_source` (행 511–520)
- 성질: 체크포인트 출처로 결박된 카운터 규칙은 다른 출처(제공자 이벤트)의 카운터를 무시하고, 실제 체크포인트의 카운터로만 도래한다.
- 준비: `basis={"source": "checkpoint", "unit": "count"}`인 규칙과, 그 규칙의 연산자·대상 종류·기반으로 만든 결박 하나. `tracker_config(profile([binding]), initial_self_check_rules=[rule])`로 추적기를 만든다.
- 실행: `counters={"attempts": 2}`를 실은 tick 이벤트를 관찰한다. 같은 카운터의 체크포인트를 쓰고 tick한다.
- 단언: 첫 결과에 `self_check_due`가 없고, 둘째 결과에 있다.
- 대역: 합성 시계.
- 비고: 시험 안에 `import json`이 다시 있다(모듈 머리와 중복). 이 시험 뒤 원문 행 521–524는 빈 줄이다.

### `test_receipt_cannot_be_reused_for_a_different_response_body` (행 525–532)
- 성질: 한 수령증은 그 제어 요청이 실은 응답 본문에만 쓸 수 있다. 본문이 다른 응답에 같은 수령증을 대면 거부된다.
- 준비: `self.submission(tracker)`. 이벤트 관찰, `CT-1` 결박.
- 실행: `next_method`만 바꾼 응답을 `receipt_id="CT-1"`로 기록한다.
- 단언: `errors`에 `"control_response_mismatch"`가 있다.
- 대역: 합성 시계.

## ExecutionObservationProfileTests (행 535–618)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅이 없다.

- `research_profile()` (행 536–539): `build_profiles({**PROFILE_CONFIG, tool_review_window_seconds: 60, self_check_response_window_seconds: 5})`에서 `research_work` 프로필을 고른다. `PROFILE_CONFIG`는 `provider_fixtures`의 프로필 설정이다.

### `test_checkpoint_counter_name_is_bound_by_the_execution_not_the_profile` (행 541–552)
- 성질: 프로필은 신호 종류만 정하고 카운터 이름은 정하지 않는다. 실행이 받은 규칙의 카운터 이름(`attempts`)은 그 실행의 체크포인트로 관찰된다.
- 준비: `tracker_config(profile, initial_self_check_rules=[counter_rule()])`. 임시 작업 공간에 `counters={"attempts": 2}`인 체크포인트.
- 실행: `ObservationTracker("EX-local", workspace, config)`에서 tick을 관찰한다. 시계 인자가 없으므로 실제 `time.monotonic`을 쓴다.
- 단언: 결과에 `self_check_due`가 있다.
- 대역: 없음.
- 비고: 제품 `observation_rule_contract`의 docstring(행 53–59)은 "Counter names are local to a particular execution and are checked against that execution's snapshot, rather than being guessed while a reusable profile is authored."이다.

### `test_new_execution_gets_its_observation_interval_before_missing_signal_review` (행 554–569)
- 성질: 새 실행은 첫 관찰 간격이 끝날 때까지 신호 미측정을 진단하지 않는다. 간격이 끝나도 신호가 없으면 그 규칙에 대한 미측정 진단과 운영 점검 후속이 나오고, 카운터를 0으로 만들지 않는다.
- 준비: 위와 같은 설정. 시계는 목록 `elapsed`를 읽는 람다다. 체크포인트는 없다.
- 실행: 경과 0초와 `observation_interval_seconds - 0.1`초에서 tick. 이어서 정확히 간격에서 tick.
- 단언: 앞의 두 tick에는 `observation_unavailable`이 없고 `attempts`가 카운터에 없다. 간격의 tick에는 `observation_unavailable`이 있고, 그 `rule_ids == ["SC-attempts"]`, `followup.kind == "operational_review_due"`다. `attempts`가 여전히 카운터에 없다.
- 대역: 시계 람다.
- 비고: `references/공통-실행.md` 행 204는 "첫 tick에 이름이 아직 나타나지 않았다는 이유만으로 값을 0으로 만들거나 운영 AI를 부르지 않는다"고 적는다.

### `test_shared_contract_rejects_forged_source_and_other_execution_subject` (행 571–589)
- 성질: 공유 신호 계약은 위조된 출처의 규칙을 받지 않는다. 다른 실행을 대상으로 한 규칙은 추적기를 만들 때 거부된다. 나중의 규칙 교체도 같은 계약을 따르며, 거부되면 기존 규칙이 유지된다.
- 준비: `research_profile()`. 다른 실행 대상 규칙 `SC-other`(`checkpoint_count_gte`, 대상 `{"kind": "checkpoint", "id": "EX-other"}`).
- 실행: `counter_rule(source="invented")`로 `tracker_config`. `SC-other`로 `tracker_config`를 만든 뒤 `ObservationTracker("EX-local", ...)`. `counter_rule()`로 정상 추적기를 만든다. `tracker._replace_rules({"current_revision": 0, "reason": "change", "rules": [SC-other]})`.
- 단언: 첫 호출은 `ValueError`(메시지 `"basis"`)다. `SC-other` 추적기 생성은 `ValueError`(메시지 `"different execution"`)다. 정상 추적기의 규칙이 `[admitted]`다. 교체 결과가 `observation_rules_rejected`이고, 규칙이 여전히 `[admitted]`다.
- 대역: 없음.
- 비고: `SC-other`의 `tracker_config`는 예외 없이 끝난다. 실행 결박 대상의 검사는 실행 ID를 아는 추적기 생성자에서 일어난다(observations.py 행 476–478).

### `test_git_reload_preserves_the_sealed_shared_contract_before_tracker_admission` (행 591–618)
- 성질: Git에 저장했다가 다시 읽은 프로필도 봉인된 신호 종류 계약과 참조 정체성을 보존한다. 그 프로필로 만든 추적기는 실행별 카운터 규칙을 받아들여 체크포인트로 도래시킨다.
- 준비: 임시 폴더에 `git_init`으로 저장소를 만들고 `ResearchRepository(root, "RI-01ARZ3NDEKTSV4RRFFQ69G5FAV")`를 연다. 설정은 기본 설정에 두 창을 더한 것이다. `current_state({**domain_governance(), "config": ..., **build_profiles(...)}, {"status": "ready", ...})`로 현행 계약에 맞는 상태를 만든다.
- 실행: `store.initialize`로 게시하고 `store.load(head)`로 다시 읽는다. 읽은 `research_work` 프로필로 `tracker_config`를 만든다. 작업 공간에 체크포인트(`attempts=2`)를 쓰고, 추적기를 만들어 tick을 관찰한다.
- 단언: 읽은 프로필의 `observation.rule_bindings`가 `observation_rule_contract()`와 같다. `profile_ref(profile)["id"]`가 프로필 `id`와 같다. tick 결과에 `self_check_due`가 있다.
- 대역: 없음. 저장소는 실제 Git이다.
- 비고: 행 594에서 `record_fixtures`의 `domain_governance`와 `governance_import`를 import하지만, `governance_import`는 이 시험에서 쓰이지 않는다. 추적기는 실제 `time.monotonic`을 쓴다.

## ObservationRuleTests (행 621–860)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅이 없다.

- `tracker(workspace, clock, **extra)` (행 670–673): `ObservationTracker("EX-1", workspace, {observation_rules: [observation_rule()], tool_review_window_seconds: 60, self_check_response_window_seconds: 5, **extra}, clock=clock)`. 원문에서 세 번째 시험과 네 번째 시험 사이에 정의되어 있다. 이 도우미의 추적기에는 관찰 간격이 없다.

### `test_rules_bind_operator_subject_unit_and_evidence` (행 622–633)
- 성질: 규칙은 연산자의 출처와 단위를 기반으로 정확히 가져야 한다. 지원되지 않는 연산자, 한 번뿐인 연산자에 1이 아닌 문턱, 빈 규칙 목록은 거부된다.
- 준비: `observation_rule(repeat_interval=2)`.
- 실행: `validate_rules`를 여섯 번 부른다. 정상, 기반 `{"source": "x"}`, 기반 `{"source": "checkpoint", "unit": "milliseconds"}`, 연산자 `tool_results_gte`, `observation_rule("tool_call_completed", "tool_call", "CALL-1", 2)`, 빈 목록이다.
- 단언: 정상은 `[accepted]`를 돌려준다. 두 기반은 `ValueError`(`"basis"`, `subTest`)다. 이어서 `"unsupported"`, `"one-time"`, `"nonempty"`가 나온다.
- 대역: 없음.

### `test_rule_evaluation_preserves_multiple_boundaries_and_unknowns` (행 635–643)
- 성질: 규칙 평가는 여러 규칙의 경계를 각각 보고한다. 반복 규칙은 현재 값 아래의 가장 큰 경계를 쓴다. 관찰되지 않은 대상은 0으로 바꾸지 않고 도래시키지 않는다.
- 준비: 두 규칙. 하나는 `counter_gte` `attempts` 문턱 2, 반복 2이고, 다른 하나는 `tool_call_completed` `CALL-1` 문턱 1(`R-2`)이다.
- 실행: 스냅숏 `{"counters": {"attempts": 5}, "completed_call_ids": ["CALL-1"]}`로 `evaluate_rules`. 대상이 `missing`인 규칙을 빈 카운터로 평가한다.
- 단언: 첫 결과의 `(rule_id, boundary)`가 `[("R-1", 4), ("R-2", 1)]`이다. 둘째 결과가 빈 목록이다.
- 대역: 없음.
- 비고: 주석(행 640–641)은 규칙 ID 중복이 무효이므로, 부재가 0으로 바뀌지 않음을 보이려고 독립된 미지 규칙을 쓴다고 밝힌다.

### `test_tracker_creates_self_check_and_call_specific_review_facts` (행 645–668)
- 성질: 추적기가 연 의무는 설정의 규칙 개정을 싣는다. 작업자 피드백은 규칙의 기반 같은 내부 필드를 싣지 않는다. 도구 검토는 호출별로, 작업자가 준 창이 아니라 고정된 창으로 도래한다.
- 준비: `self_check_revision=3`인 추적기와 체크포인트(`attempts=2`).
- 실행: tick으로 의무를 열고 응답을 기록한다. `self_check_feedback(obligation)`. `observation_review_window_seconds: 3`을 입력에 가진 `Bash` 호출 `CALL-1`을 관찰한다. 시계 3초와 60초에서 tick.
- 단언: 의무의 `rule_revision == 3`이다. 응답이 `self_check_received`다. 피드백의 `obligation_id`가 의무 ID이고, `due[0]`에 `basis`가 없다. 3초에는 `tool_review_due`가 없고, 60초에는 `call_id == "CALL-1"`인 `tool_review_due`가 있다.
- 대역: 합성 시계.

### `test_three_reported_counterexamples` (행 675–687)
- 성질: 보고된 반례 세 가지를 고정한다. (1) 필수 증거가 아닌 증거만 인용한 응답은 거부된다. (2) 작업자의 도구 입력이 준 짧은 창(`timeout: 1`, `observation_review_window_seconds: 1`)으로 도구 검토가 앞당겨지지 않는다. (3) `wall_time_reached` 규칙은 관찰 시각이 문턱과 정확히 같을 때 도래한다.
- 준비: `self.tracker(...)`, 체크포인트(`attempts=2`).
- 실행: (1) `evidence=["unrelated"]`인 응답을 가용 증거 `{"unrelated"}`로 기록한다. (2) 도구 호출 `C`를 관찰하고 시계 2초에서 tick. (3) `observation_rule("wall_time_reached", "clock", "UTC", "2026-09-20T10:00:00Z", basis={"source": "clock", "unit": "UTC"})`를 `validate_rules`한 뒤 `{"observed_at": "2026-09-20T10:00:00+00:00"}`로 `evaluate_rules`.
- 단언: (1) `self_check_rejected`다. (2) `tool_review_due`가 없다. (3) 도래 목록의 길이가 1이다.
- 대역: 합성 시계.
- 비고: 이름은 성질이 아니라 계기("보고된 반례 셋")를 말한다. `시험-지침.md` 4절 규칙 9는 계기로 시험 이름을 짓지 않도록 정한다. 세 성질은 서로 독립이며, 규칙 2의 "시험 하나는 성질 하나"와도 어긋난다.

### `test_response_deadline_is_current_and_rejection_reaches_worker` (행 689–699)
- 성질: 응답 창이 지난 뒤의 응답은 마감 경과로 거부되고, 거부는 운영 점검 후속을 가진다.
- 준비: `self.tracker(...)`, 체크포인트, tick으로 의무를 연다.
- 실행: 시계 6초에서 응답을 기록한다.
- 단언: `kind == "self_check_rejected"`, `errors`에 `"response_deadline_passed"`, `followup.kind == "operational_review_due"`.
- 대역: 합성 시계.
- 비고: 이름의 "rejection reaches worker"는 작업자 피드백 전달을 말하지만, 단언은 후속 종류만 본다.

### `test_call_reported_at_a_safe_boundary_stops_holding_the_deadline` (행 701–714)
- 성질: 안전 경계에서 보고된 호출은 더 이상 마감을 붙잡지 않는다. 경계 기록 시각까지 붙잡힌 시간만 마감에 더해진다.
- 준비: 호출 `C` 시작 뒤 의무를 연다(0초, 마감 5000, 붙잡기 0).
- 실행: 9초에 `record_safe_boundary("CT-1", call_ids=["C"])`. 14초에 응답을 기록한다.
- 단언: 의무를 연 직후 `(5000, 0)`이다. 경계 뒤 `deadline_offset_ms == 14000`이다. 14초의 응답이 `self_check_received`다.
- 대역: 합성 시계.

### `test_deadline_held_by_a_call_running_at_opening_passes_after_the_call_ends` (행 716–730)
- 성질: 의무가 열릴 때 돌던 호출이 붙잡은 마감은 호출이 끝나면 다시 흐르고, 늘어난 마감이 지나면 응답이 거부된다.
- 준비: 호출 `C` 시작 뒤 의무를 연다(붙잡기 0).
- 실행: 9초에 호출 `C` 완료를 관찰한다. 15초에 응답을 기록한다.
- 단언: 붙잡기 값이 0이다. 완료 뒤 마감이 14000이다. 15초의 응답은 `self_check_rejected`이고 `errors`에 `"response_deadline_passed"`가 있다.
- 대역: 합성 시계.

### `test_research_calls_before_the_response_hold_its_deadline_until_all_of_them_end` (행 732–760)
- 성질: 의무가 열린 뒤 시작된 연구 호출들은 모두 끝날 때까지 마감을 붙잡는다. 겹친 호출 가운데 하나가 끝나도 풀리지 않는다. 풀린 뒤 새 호출은 다시 붙잡는다.
- 준비: 체크포인트로 0초에 의무를 연다(마감 5000). 지역 람다 `start`, `end`, `missed`를 둔다.
- 실행: 1초에 `A` 시작, 3초에 `B` 시작, 20초에 `A` 완료, 30초에 `B` 완료, 31초에 `C` 시작, 40초에 `C` 완료, 43초에 응답.
- 단언: `A` 완료와 `B` 완료에서 미응답이 없다(첫 메시지: "a nested call still running holds the deadline"). `B` 완료 뒤 마감이 34000(5000 + 30000 − 1000)이고 붙잡기 키가 없다. `C` 완료에서 미응답이 없고, 마감이 43000(34000 + 40000 − 31000)이다. 43초의 응답이 `self_check_received`다.
- 대역: 합성 시계.

### `test_research_call_after_the_deadline_does_not_hold_it` (행 762–770)
- 성질: 마감이 지난 뒤 시작된 연구 호출은 마감을 붙잡지 않는다.
- 준비: 체크포인트로 의무를 연다.
- 실행: 6초에 호출 `late` 시작을 관찰한다.
- 단언: 관찰 결과에 `reason == "response_deadline_passed"`인 행이 있다.
- 대역: 합성 시계.
- 비고: 제품 `_hold_deadlines`는 `offset <= deadline`일 때만 붙잡는다(행 773).

### `test_integer_persistence_keeps_raw_adapter_payload_as_text` (행 772–782)
- 성질: 관찰 사실은 정수 밀리초 오프셋으로 저장되고, 어댑터 원본 이벤트는 실수를 포함해도 JSON 텍스트로 보존되어 정규 JSON으로 직렬화된다.
- 준비: `self.tracker(...)`. 시계 0.125초.
- 실행: `{"type": "result", "duration": 0.25}`를 관찰하고 `observation_fact` 행을 `canonical_json`한다.
- 단언: 직렬화가 예외 없이 끝난다. `monotonic_offset_ms == 125`다. `event_json`을 다시 읽은 `duration`이 0.25다.
- 대역: 합성 시계.

### `test_rule_identity_change_does_not_reconsume_boundary` (행 784–789)
- 성질: 규칙 ID만 바꾼 같은 규칙은 이미 소비한 경계를 다시 도래시키지 않는다.
- 준비: 기본 규칙과 스냅숏 `attempts=2`.
- 실행: `evaluate_rules`. 결과의 `boundary_key`로 소비 사전을 만든다. ID가 `RENAMED`인 규칙을 같은 스냅숏과 소비 사전으로 평가한다.
- 단언: 첫 결과에 `boundary_key`가 있다. 둘째 결과가 빈 목록이다.
- 대역: 없음.
- 비고: 경계 키는 규칙 ID가 아니라 연산자, 대상, 기반(시각 규칙은 문턱도)에서 계산된다(`_boundary_key`, 행 310–315). 주석은 "IDs and revisions name presentations, not new occurrences of an event."다.

### `test_missing_checkpoint_counter_is_reported_not_zero_or_wall_time` (행 791–800)
- 성질: 필요한 카운터가 체크포인트에 없으면 미측정으로 보고하고, 0이나 경과 시간으로 대신하지 않는다.
- 준비: `self.tracker(...)`. 체크포인트는 없다.
- 실행: 100초에서 tick.
- 단언: `observation_unavailable` 행의 `rule_ids == ["R-1"]`, `followup.kind == "operational_review_due"`다. `self_check_due`가 없다.
- 대역: 합성 시계.
- 비고: 이 추적기에는 관찰 간격 설정이 없다. 간격이 없으면 제품은 첫 관찰부터 측정 시한이 된 것으로 본다(행 993–994). 따라서 시계 100초라는 값은 이 결과에 필요하지 않다. 첫 관찰 간격까지 유예하는 규칙은 `ExecutionObservationProfileTests.test_new_execution_gets_its_observation_interval_before_missing_signal_review`가 검사한다.

### `test_profile_admission_requires_frozen_windows` (행 802–815)
- 성질: 관찰 창 설정이 없는 프로필로는 추적기 설정을 만들 수 없다. 창을 가진 프로필의 설정은 창 값과 프로필 참조를 고정한다.
- 준비: `settings={}`인 합성 AI 프로필 본문(`rule_bindings`는 `observation_rule_contract()`).
- 실행: `seal_profile(body)`로 `tracker_config`. 세 창을 넣고 다시 봉인해 `tracker_config`.
- 단언: 첫 호출은 `ValueError`(정규식 `"window|interval"`)다. 둘째 설정의 `tool_review_window_seconds == 60`이고, `observation_profile_ref.revision == 1`이다.
- 대역: 없음.
- 비고: 시험 안에서 `observation_rule_contract`, `tracker_config`, `seal_profile`, `BOUNDARY`를 다시 import한다(모듈 머리와 중복). 행 812는 `rule_bindings`에 이미 가진 값과 같은 값을 다시 대입한다.

### `test_indeterminate_operator_input_is_not_silently_skipped` (행 817–819)
- 성질: 연산자 입력이 정수가 아니면(2.5) 규칙을 조용히 건너뛰지 않고 오류를 낸다.
- 준비: 기본 규칙.
- 실행: `evaluate_rules([rule], {"counters": {"attempts": 2.5}})`.
- 단언: `ValueError`(메시지 `"observation"`)다.
- 대역: 없음.

### `test_checkpoint_record_requires_preserved_original_artifact` (행 821–834)
- 성질: 체크포인트의 저장 기록은 원본 산출물 참조를 요구하고, 원본 바이트(`raw`)는 기록에 싣지 않는다.
- 준비: 임시 작업 공간의 유효한 체크포인트를 읽어 `kind="checkpoint"`를 붙인다.
- 실행: `persistent_record(checkpoint)`, `persistent_record(checkpoint, artifact_ref="ART-1")`, `canonical_json(preserved)`.
- 단언: 첫 호출은 `ValueError`(메시지 `"artifact"`)다. 둘째 결과에 `raw`가 없고 `artifact_ref == "ART-1"`이다. 직렬화가 예외 없이 끝난다.
- 대역: 없음.
- 비고: 시험 안에서 `observations`를 다시 import한다(모듈 머리와 중복).

### `test_maximum_interval_keeps_distinct_ids_for_every_due_rule` (행 836–852)
- 성질: 작업자 규칙의 ID가 최대 간격 합성 규칙의 이름과 겹쳐도, 한 의무의 모든 도래 규칙은 서로 다른 ID를 가진다. 그 의무에 대한 응답은 받아들여진다.
- 준비: ID가 `@maximum_interval`, `@maximum_interval:1`인 두 규칙과 관찰 간격 10초의 추적기.
- 실행: 10초에서 체크포인트(`attempts=2`)를 쓰고 tick. 응답을 기록한다.
- 단언: 도래 규칙 ID가 셋이고 서로 다르며, 두 작업자 규칙 ID를 모두 포함한다. 응답이 `self_check_received`다.
- 대역: 합성 시계.
- 비고: 셋째 ID는 최대 간격 합성 규칙이 충돌을 피해 받은 ID다. 이 시험은 그 구체적 값을 단언하지 않는다.

### `test_dispositions_are_validated_before_engine_application` (행 854–860)
- 성질: 운영 처분은 엔진 적용 전에 스키마로 검증되고, 작업자에게는 공개 필드(`kind`, `reason`, `next_owner`)만 간다. 알려지지 않은 비공개 필드는 거부된다.
- 준비: `resume` 처분(`basis_refs`, `checkpoint_ref`, `scope` 포함).
- 실행: `validate_disposition(disposition)`, `worker_feedback(disposition)`(`operational_dispositions`의 함수), 비공개 필드 `private_diagnostic`을 더한 처분의 `validate_disposition`.
- 단언: 검증 결과가 입력과 같다. 작업자 피드백이 `{"kind": "resume", "reason": ..., "next_owner": "engine"}`이다. 비공개 필드는 `ValueError`(메시지 `"Additional properties are not allowed"`)다.
- 대역: 없음.
- 비고: 이 모듈이 import한 `worker_feedback`은 `operational_dispositions.worker_feedback`이다(행 17). `Tests.test_feedback_producers_share_the_public_field_set`이 부르는 `observations.worker_feedback`과는 다른 함수다.

## 관계

- 실시간 관찰 경로(러너의 스트림 묶음이 엔진의 `_observe_running`을 거쳐 추적기와 알림 게시로 가는 흐름)는 `lifecycle` 조각의 `test_live_observation`, `test_observation_admission`이 엔진 수준에서 검사한다. 이 모듈은 그 가운데 추적기 규칙과 엔진의 알림 처리 하나만 본다.
- 자기 점검 제어 호출의 전송 층(제어 서버, 요청과 수령증 발급)은 `test_control_transport`와 `lifecycle` 조각의 `test_controls`가 다룬다. 이 모듈의 `SelfCheckControlBindingTests`는 추적기 쪽의 결박 규칙을 본다.
- 프로필의 신호 계약과 봉인은 `test_execution_profiles`가, 체크포인트의 영속 저장은 `lifecycle` 조각의 `test_checkpoint_persistence`가 넓게 검사한다.
- 관찰 창의 채택 경고(창이 대표 컴파일보다 짧음)는 `test_environment_validation.ObservationWindowWarningTests`가 검사한다. 그 경고가 응답 창을 대상에서 빼는 근거가 이 모듈의 마감 붙잡기 시험들이다.
- `test_design_walkthroughs`의 w08, w10이 같은 추적기를 통합 경로에서 재생한다.
- 픽스처 의존은 다음과 같다(`consumers.json`). 관찰 도우미(`Clock`, `observe`, `write_checkpoint`, `observation_rule`)는 `test_live_observation`, `test_controls`, `test_design_walkthroughs` 등과 공유한다. `acknowledge`는 이 모듈과 `test_live_observation`이 쓴다. `self_check_response`는 이 모듈과 `test_controls`가 쓴다. `provider_fixtures.PROFILE_CONFIG`와 `record_fixtures.domain_governance`는 여러 모듈이 공유한다.
- 이 모듈에만 있는 도우미는 모듈 함수 `profile`, `counter_rule`과 클래스 도우미 `assert_persisted_notice`, `write`, `due`, `tracker`, `submission`, `research_profile`이다.

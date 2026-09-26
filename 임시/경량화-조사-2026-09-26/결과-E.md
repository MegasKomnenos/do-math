# 결과 — 그룹 E: 외부 프로세스·제어·관찰

이 문서는 do-math 경량화 2라운드 그룹 E의 반환이다. 설계 `docs/do-math/경량화-설계-2026-09-26.md` 6절의 다섯 항목을 순서대로 적고, 이음새 계약 10절의 `이음새 요청`과 `추가한 이름`을 끝에 덧붙인다.

- 처분: 완료. 4.6절 표의 ID를 모두 구현했다. 구현하지 않은 ID는 없다.
- 브랜치·커밋: worktree `C:/math-worktrees/r2-e`, 브랜치 `r2-e`, 커밋 `c2d45a7`(기준 `24682fd`, 커널 병합 뒤).
- 변경 범위: 제품 15개 파일, 시험 21개 파일. 스킬 문서와 `.agents` 미러는 고치지 않았다(3절).
- 좌표: 경로는 `C:/math-worktrees/r2-e/.claude/skills/do-math/scripts/` 기준이다. `do_math/`는 제품, `tests/`는 시험이다.
- 검증: 시험을 실행하지 않았다(설계 3.3). 바꾼 파일 36개를 모두 `python -m py_compile`로 확인했다. 이와 별도로, 3.3절이 허용한 문법 확인을 넘는 확인을 한 번 했다. `engine`·`cli`·`model_runner`·`claude_adapter`·`observations`·`control_contracts`를 import하는 `python -c` 명령이며, 순환 import가 없음을 확인했다. 이 명령은 파일을 바꾸지 않았고 시험 결과를 대신하지 않으므로, 통합자가 따로 처리할 것은 없다.

## 통합자가 먼저 알아야 할 계약 변경

다음 여섯 가지는 다른 그룹의 시험 대역과 스킬 문서가 옛 계약을 가정하면 통합 뒤 깨지는 지점이다. 각 항목의 구현 세부는 1절의 해당 ID에 있다.

1. **관찰 규칙 계약(결정 3, IO-03·IO-13).** 출처 `execution_events`·`adapter_active_intervals`와 연산자 `event_recorded`·`active_duration_gte`가 사라졌다. 연산자 표 `observations.OPERATORS`에서 연산자마다 출처가 하나뿐이므로, `validate_rules`는 규칙의 `basis`가 그 연산자의 `{source, unit}`과 정확히 같아야 받는다. 따라서 카운터와 반복 수는 작업자의 `checkpoint.json`으로만 tracker에 들어간다. 공급자 사건의 최상위 `counters`·`iterations`·`active_duration_ms`·`id`는 이제 읽지 않는다. 시험에서 `tracker.observe({"type": "tick", "counters": ...})`로 자기 점검을 열던 곳은 모두 checkpoint를 쓰도록 고쳤다. 다른 그룹이 새로 쓰는 시험도 이 방식을 따라야 한다(`tests/research_fixtures.write_checkpoint`).
2. **Claude final의 출처(IO-05).** Claude worker는 더 이상 stdout을 해석하지 않고 `final.txt`를 쓰지 않는다. Claude 요청에는 `final_path`가 없고, 있으면 worker가 미지 필드로 거부한다. 수집기가 stream이 선택한 응답에서 final 바이트를 한 번 도출한다. Codex는 CLI가 쓴 `final.txt`를 그대로 쓰되, 일반 수집(`collect`)이 이제 그 바이트를 종료 직전 `agent_message` 본문과 대조한다. 이 대조는 전에는 `verified_native_final`에만 있었다.
3. **자기 점검 전달(IO-02·IO-04·IO-12).** 요청 객체는 `observations.self_check_request` 하나로 만들고, tracker가 해시한 그 객체를 transport가 그대로 쓴다. API가 `tracker.issue_self_check(id)` → `transport.request_self_check(binding, request=...)` → `tracker.record_delivery(id, source_offset=...)`로 바뀌었다. 형식이 틀린 응답은 이제 반려 기록과 운영 점검이 아니라 MCP 도구 오류(-32602)가 되며, inbox에 아무것도 쓰지 않는다. MCP `control_submit`의 `kind` enum은 `self_check_response`를 포함한다.
4. **관찰 묶음과 검토 행 번호(IO-01·ENG-09).** `ObservationBatch`에 `rows`(공백이 아닌 행마다 원 바이트 하나; 빈 행은 싣지 않음. 해석하지 못한 행도 `unparsed_observation` 사건이 되므로 `rows[i]`와 `events[i]`는 늘 같은 행이다)와 `first_row`(묶음 첫 행의 stream 행 번호, 공백이 아닌 행만 셈)가 더해져 위치 인자 순서가 바뀌었다. 엔진은 stdout을 다시 읽지 않는다. `_drain_review_observations`와 `_review_event_cursors`는 지웠고, 종료 뒤 줄바꿈으로 끝나지 않은 마지막 행은 러너가 직접 묶음으로 보낸다.
5. **러너 인자(ENG-07·RUN-24).** 엔진은 러너와 형식 검증기에 모든 인자를 조건 없이 넘긴다(`inspect.signature` 분기 4곳 삭제). 엔진은 `scholarly_server`·`claude_only_assigned_model`을 더 이상 넘기지 않는다. 러너는 고정 프로필이 있으면 두 값을 프로필에서만 읽는다. 두 인자의 기본값은 `None`이며, 프로필과 함께 둘 중 하나라도 `None`이 아닌 값을 받으면 `ValueError`를 낸다.
6. **능력 식별과 transport 동작(IO-08·IO-19).** `capability_identity`의 모양이 `{cli_path, cli_sha256, module_sha256: {모듈: 해시}, host}`로 바뀌었으므로, 적용 뒤 첫 확인에서 기존 능력 증거가 한 번 무효가 된다(조사 파일이 예고한 차이). `ControlTransport.pump`는 열린 전송의 inbox만 읽는다.

가장 큰 미확인 위험은 2번의 Codex 대조다. 정상 Codex 실행에서 `--output-last-message`의 바이트가 종료 직전 `agent_message`의 `text`와 항상 같은지 실측하지 않았다. 다르면 모든 Codex 일반 실행이 `final_response_mismatch`로 실패한다(4절).

## 1. ID별 처분

모두 **구현함**이다. 조사 제안과 다르게 구현한 부분은 해당 행에 적고 이유는 5절에 모았다.

| ID | 구현 내용 |
|---|---|
| 결정 3 (IO-03) | `observations.py`에서 두 출처와 두 연산자, `_ingest_event`의 사건 카운터·반복·활성 시간·사건 ID 분기, `active_*`·`event_ids`·`checkpoint_counters`·`checkpoint_iterations` 상태, `_snapshot`의 `by_source`를 지웠다. `observation_unavailable`은 checkpoint 카운터·반복이 측정되지 않았을 때만 생긴다. 연구 수행 프로필의 `rule_bindings`는 6개 조합으로 줄었다. |
| IO-13 | `OPERATORS = {연산자: {subject_kind, unit, source}}` 표 하나에서 계약 목록(`observation_rule_contract`), 연산자 검사, 단위·출처 검사를 모두 얻는다. `OBSERVATION_OPERATORS`, `_OPERATOR_SUBJECTS`, `OBSERVATION_SOURCES`는 사용처가 이 모듈뿐이어서 파생 이름을 남기지 않고 지웠다. `validate_observation_rule_contract`는 계약 목록의 원소 검사가 되었다. 문서 표는 문서 단계로 넘긴다(3절). |
| IO-01, ENG-09 | 행 해석 규칙은 `observation_transport.decode_observation_row` 하나다. 러너가 이 함수로 행을 해석하고 `rows`·`first_row`를 싣는다. `engine._review_observation_source(execution_id, batch, index)`는 `batch.rows[index]`와 `batch.first_row + index`를 쓴다. 파일 재독해, 사건 대조, 커서와 그 복원을 지웠다. |
| IO-07, ENG-11 | 원자료 정규화 검사는 `control_contracts.normalized_source_bytes` 하나다. 엔진 `control`은 경로 형태를 `normalized_source`로 정규화한 뒤 이 함수로 자기 확인하고, `_controls`는 inbox 사본에 같은 함수를 적용한다. `control_request_id`는 `cli`에서 `control_contracts`로 옮겨 역방향 의존 `engine → cli`가 사라졌다. 요청 ID 형식은 `control_contracts.REQUEST_ID_PATTERN` 하나를 CLI 요청 스키마와 엔진(`validate_request_id`)이 함께 쓴다. `cli._control`은 정규화·상호 배제 검사·ID 계산을 하지 않고, 엔진이 돌려준 `request_id`를 쓴다. |
| IO-02 | 5절의 이유로 조사 제안의 대안(전달 기록과 오프셋 기록 분리)을 택했다. `issue_self_check`가 응답 기한을 정하고 요청 객체를 만들어 해시한 뒤 돌려준다. 엔진은 그 객체를 전송하고, 전송 뒤 한 번 잰 `stream_size()`를 `record_delivery`에 넘긴다. 전송 전 오프셋 측정과 덮어쓰기는 사라졌다. |
| IO-04 | 스키마 `SELF_CHECK_RESPONSE_SCHEMA`를 `control_transport.py`로 옮겼고, `observations`는 그것을 import한다. 생산자 쪽에서는 `ControlTransport.worker_submit`이 `kind=self_check_response`일 때 이 스키마로 검사한다. 두 MCP 도구(`control_self_check`, `control_submit`)가 이 함수를 지나므로 둘 다 막힌다. 같은 스키마를 `control_self_check`의 `inputSchema.properties.response`로 공개했다. 검사에는 `jsonschema`를 함수 안에서 불러온다. 수신 검사는 그대로다. |
| IO-05 | 어댑터 기반에 `final_bytes(parsed)`(stream이 선택한 `final_text` 또는 `structured_output`의 바이트)와 `final_from_stream` 속성을 두었다. Claude는 `final_from_stream = True`로 수집기가 도출하고, Codex는 CLI 파일을 쓴다. `validate_final`은 기반에 하나이며 `final == final_bytes(parsed)`를 요구한다. Codex 해석기는 종료 직전 사건이 `agent_message`일 때만 `final_text`를 싣는다. 그렇지 않으면 `final_bytes`가 `None`이므로, `final.txt`가 있어도 `collect`는 사유 `final_response_mismatch`를 다른 실패 사유와 함께 기록한다(`final.txt`가 없으면 `final_message_missing`). `verified_native_final`의 공급자 분기와 stdout 재해석을 지웠다. |
| IO-06 | `codex_worker.py`에 `check_common_request`, `validate_max_runtime`, `run_cli`, `STATUS_BINDING_KEYS`를 두었다. 두 worker는 argv 구성, 공급자별 필드 검사, 환경 허용 목록만 가진다. `max_runtime_seconds` 규칙은 러너도 `validate_max_runtime`을 쓰므로 사본이 1개가 되었다. 예외 처리는 Claude 쪽(`Exception`, `error` 문구 기록)으로 맞췄다. `_REMOVED_ENV`와 `codex_argv` 분기를 지웠다. `collect`는 `STATUS_BINDING_KEYS`를 import한다. Claude worker는 `ControlTransport`를 `control_transport`에서 직접 가져온다. 공통 모듈의 이름은 바꾸지 않았다. |
| IO-08 | 어댑터 클래스 속성 `identity_modules`에 식별할 모듈 이름을 두었다. Codex는 `codex_worker`, `control_transport`, `file_io`, `windows_job`, `scholarly`, `codex_adapter`다. Claude는 여기에 `claude_worker`, `claude_adapter`, `claude_stream`을 더한다. 식별은 `module_sha256`에 모듈별 `cached_sha256`을 담는다. |
| IO-11 | `control_transport.BINDING_FIELDS`와 `ControlTransport.validate_binding(binding, *, execution_id, cwd=None)`을 두었다. `codex_worker.validate_execution_binding`은 바인딩 부분을 이 메서드에 맡긴다. `mcp_server_config`, MCP 진입 `main`, `worker_submit`이 이 상수를 쓴다. |
| IO-12 | `control_transport.py`에 서버 이름 `CONTROL_SERVER`, 도구 이름 셋, 요청 종류 상수와 `REQUEST_KINDS`·`SUBMISSION_KINDS`, `self_check_request_id`를 두었다. 두 worker, `observations`, `submission.request_control`이 이것을 쓴다. tracker의 `control_server_name` 설정 키는 설정하는 곳이 없어 지웠다. MCP `control_submit` enum은 `sorted(REQUEST_KINDS)`다. |
| IO-14 | `record_self_check_response`에서 도달 불가능한 네 분기(`rule_results_missing`, `invalid_rule_result`, `invalid_rule_status`, `invalid_rule_evidence`)를 지웠다. 규칙 포괄과 증거 대조는 남겼다. |
| IO-15 | `collect`는 장벽이 확인되지 않은 분기에서도 `provider_observation`을 돌려준다(`codex_adapter._provider_observation` 하나가 만든다). 러너는 그 값만 쓴다. 한도 분류는 어댑터 메서드 `provider_failure(parsed)`이며, Claude는 `provider_limit`을 부르고 기반은 `None`이다. |
| IO-16 | `claude_adapter.py`의 `ADAPTERS`(각 어댑터의 `provider` 속성이 키), `provider_adapter(provider, cli_path=None)`, `request_provider(request)`가 정본이다. `initialization.adapter_for(profile)`, `cli`의 `profile` 명령, 두 러너 생성자, `verified_native_final`이 이것을 쓴다. |
| IO-17 | `LocalCLIAdapter`에서 Codex 전용 내용을 `CodexExecAdapter`로 옮겼다. `describe`는 기반에 하나이며 공급자는 `help_commands`(인자와 필수 플래그 쌍; Codex의 `--ask-for-approval`은 전역 help의 필수 플래그), `surface_capabilities`, `unknown_capabilities`만 준다. 파싱 훅은 `parse_response(raw, request)` 하나다. `parse_output`, `inspect`, `reported_evidence`를 지웠다. `describe` 결과에 두 공급자 모두 `provider`가 들어간다. |
| IO-18 | `cli.RESPONSE_FIELDS`를 `_emit`과 `describe_commands`가 함께 쓰므로 `--describe`에 `response_contract`가 나온다. `inspection_exit_codes`는 `state_checks.inspection_exit_code`를 네 상태에 적용해 만든다. `_json_arguments`의 도달 불가 검사 두 개를 지웠다. 계약 문서 48행은 문서 단계로 넘긴다. |
| IO-19 | `ControlTransport`가 열린 전송 ID 집합을 가진다. 생성 때 `binding.json`이 있고 상태가 열린 전송으로 채우고, `issue`에서 더하고, `close`에서 뺀다. 상태 파일이 없거나 JSON으로 읽을 수 없는 전송도 열린 것으로 넣는다. 전에는 모든 inbox를 읽었으므로 이런 전송의 전달도 수신 단계에서 판정되어 거부 영수증을 받았는데, 이 동작을 유지하기 위해서다. `close`는 상태를 쓴 뒤 그 전송의 inbox를 한 번 pump해 경합 전달에 `closed` 영수증을 준다. `_receipt`의 전역 glob은 바꾸지 않았다. |
| IO-21 | 엔진 발행자의 `inflight_calls` 재검사를 지웠다. 관찰 코드의 같은 조건은 보존 판정대로 두었다. |
| IO-22 | `observations.WORKER_FEEDBACK_FIELDS`와 `worker_feedback(feedback)`을 두었다. 규칙 파일 반려, 응답 반려, `self_check_feedback`, `operational_dispositions.worker_feedback`이 이 함수로 만들고, 규칙 교체는 이 집합으로 투영한다. 게시 함수의 검사도 같은 함수를 쓴다. |
| ENG-07, RUN-24 | `engine._runner_tools`와 러너의 비교 분기를 지웠다. 러너 인자 `on_observation`은 무조건 넘긴다. 형식 검증기에는 `launch_ticket`·`should_stop`·`allowed_axioms`를 무조건 넘긴다(`engine.py`, `lifecycle_engine.py`). `engine.py`의 `import inspect`는 쓰는 곳이 없어 지웠다. `execution_profiles.runner_tools`는 엔진의 역할 입력 문맥이 쓰므로 남겼다. |

## 2. 만든 공유 정의

설계 2절의 커널에는 이 정의들이 없었다. 정정된 계약에 따라 그 개념을 소유한 그룹 E 모듈에 하나씩 만들었다.

| 정의 | 위치 | 규칙 |
|---|---|---|
| `decode_observation_row(raw)`, `ObservationBatch.rows`·`first_row` | `do_math/observation_transport.py` | stdout 한 행의 해석과 행 바이트·번호 |
| `CONTROL_SERVER`, `SUBMIT_TOOL`·`RECEIPT_TOOL`·`SELF_CHECK_TOOL`, 요청 종류 상수, `REQUEST_KINDS`, `SUBMISSION_KINDS`, `self_check_request_id` | `do_math/control_transport.py` | 제어 어휘 |
| `BINDING_FIELDS`, `ControlTransport.validate_binding` | `do_math/control_transport.py` | 제어 바인딩 모양 |
| `SELF_CHECK_RESPONSE_SCHEMA`, `self_check_response_errors` | `do_math/control_transport.py` | 자기 점검 응답 모양(생산자·수신자 공용) |
| `OPERATORS`, `WORKER_FEEDBACK_FIELDS`, `worker_feedback`, `self_check_request` | `do_math/observations.py` | 관찰 연산자 표, 작업자 피드백 공개 필드, 자기 점검 요청 객체 |
| `REQUEST_ID_PATTERN`, `validate_request_id`, `control_request_id`, `SOURCE_FIELDS`, `normalized_source`, `normalized_source_bytes` | `do_math/control_contracts.py` | 요청 ID, 원자료 정규형 |
| `STATUS_BINDING_KEYS`, `COMMON_REQUIRED`, `COMMON_OPTIONAL`, `check_common_request`, `validate_max_runtime`, `run_cli` | `do_math/codex_worker.py` | worker 공통 요청 검사와 실행 골격 |
| `ADAPTERS`, `provider_adapter`, `request_provider` | `do_math/claude_adapter.py` | 공급자와 어댑터 대응 |
| `LocalCLIAdapter.final_bytes`·`validate_final`·`provider_failure`, 속성 `identity_modules`·`help_commands`·`final_from_stream` | `do_math/codex_adapter.py` | 어댑터 기반의 공급자 훅 |

Job 안 직접 적재 경로는 유지했다. `codex_worker`·`claude_worker`는 새 이름을 `control_transport`와 서로에게서 가져오며, 둘 다 기존 `try: from do_math... except ModuleNotFoundError: from 형제 모듈` 형태를 쓴다. `control_transport`가 새로 쓰는 제3자 모듈은 함수 안에서 불러오는 `jsonschema`뿐이다. MCP 서버 프로세스의 `submit_draft` 경로는 전부터 `jsonschema`를 불러왔다. 직접 적재는 시험으로 확인하지 않았다(4절).

## 3. 필요한 문서 변경

- `references/공통-실행.md`
  - 130–139행 관찰 연산자 표: `event_recorded`, `active_duration_gte` 행을 지운다. `counter_gte`·`iteration_gte`의 출처를 `checkpoint`만으로 줄인다. 규칙의 `basis`는 표의 `{source, unit}`과 정확히 같아야 한다고 적는다. 표를 `observations.OPERATORS`를 가리키는 문장으로 바꾸거나, 코드 표와 대조하는 시험을 함께 둔다(IO-13 제안).
  - 145행: 실행 결박 조건을 "`subject.kind=checkpoint` 또는 `operator=iteration_gte`"로 고치고, `execution_events` 출처의 반복 대상 이름 문장을 지운다.
  - 167행: 응답 형식은 `control_self_check` 도구 입력 스키마로 공개되며, 형식이 틀리면 도구 오류로 즉시 돌아와 고쳐 다시 보낸다고 적는다. `control_submit`으로도 `self_check_response`를 보낼 수 있다.
- `references/CLI-실행-계약.md`
  - 48행: `--request-id`를 받는 제어 열거에 `quiesce`, `release-quiesce`를 더하거나 `--describe` 결과를 가리키는 문장으로 바꾼다.
  - `--describe`의 `response_fields`에 `response_contract`가 포함된다.
  - 911행 부근(Claude): "보존한 최종 파일"은 worker가 쓴 파일이 아니라 수집기가 stream에서 도출해 보존한 final 바이트다. Claude worker 요청에는 `final_path`가 없다.
  - Codex 수집 설명: 일반 수집이 `final.txt`를 종료 직전 `agent_message`와 대조한다.
  - 능력 식별 설명이 있으면 모양(`module_sha256`)과 식별 모듈 목록을 적는다. `describe` 결과의 `reported_evidence`가 사라지고 `provider`가 두 공급자에 생긴다.
- `docs/do-math/검사-경량화-이음새-계약.md` 2.1절: "worker 능력 식별의 파일 범위가 `control_transport`와 `file_io`"를 어댑터별 `identity_modules`로 바꾼다. 2절의 새 정의를 이음새 표로 옮긴다(통합자 몫).
- `.agents/skills/do-math/` 미러: 문서 단계의 미러 재생성이 반영한다.

## 4. 고친 시험 파일과 확인하지 못한 위험

### 고친 시험 파일

- 관찰 계약(카운터를 checkpoint로): `research_fixtures.py`(`write_checkpoint` 추가), `test_observations.py`, `test_redesign_OBSERVATION.py`(`rule()`의 basis를 `OPERATORS`에서 얻음), `test_observation_audit1.py`, `test_execution_observation_profile.py`, `test_approved_five_repairs.py`, `test_currentness_recovery.py`, `test_document_followup.py`, `test_redesign_EVIDENCE_walkthroughs.py`, `test_redesign_ENGINE.py`, `test_research_reliability.py`.
- 관찰 묶음 위치 인자: `test_checkpoint_persistence.py`, `test_research_reliability.py`, `test_redesign_ENGINE.py`(검토 대화 시험을 묶음으로 다시 씀).
- 자기 점검 API: `test_research_reliability.py`, `test_control_transport_io.py`, `test_redesign_ACTIVITIES.py`, `test_redesign_PROFILES.py`(유효한 응답으로 바꾸고, 틀린 응답이 도구 오류가 되는지와 도구 스키마 공개를 확인).
- Claude final·worker 요청: `test_claude_adapter.py`, `test_provider_final_contract.py`(`final_response_mismatch`), `test_worker_temporary_outputs.py`, `test_redesign_PROFILES.py`.
- 러너 인자: `test_redesign_ENGINE.py`(`_runner_tools` 시험을 러너 시험으로 교체), `test_claude_adapter.py`, `test_model_runner.py`(대역 `collect`가 `provider_observation`을 만들고 `provider_failure`를 가짐; 종료 뒤 마지막 행 전달과 행 번호·오프셋 단언 추가).
- 그 밖: `test_codex_adapter.py`(`codex_argv` 거부 문구), `test_cli.py`(`--describe`의 응답 필드가 실제 봉투와 같은지), `test_redesign_PROFILES.py`(능력 식별 모듈 목록).
- 새 시험: 닫힌 전송을 pump하지 않고 `close`가 경합 전달에 영수증을 주는지, 피드백 생산자의 공개 필드, 공급자 사건 카운터를 읽지 않음, checkpoint 카운터의 부분 전진 없음, 사건 출처 반복 규칙 거부, 러너가 프로필과 함께 준 도구 인자를 거부함, Claude final 도출과 바이트 대조.

### 확인하지 못한 위험

- **Codex final 대조(IO-05).** 정상 Codex 실행에서 `final.txt`가 종료 직전 `agent_message`의 `text`와 같은 바이트인지 실측하지 않았다. `--output-schema`를 쓰는 비결합 실행에서도 같아야 한다. 다르면 Codex 일반 실행이 모두 실패한다. 통합 시험 전에 실제 Codex 실행 하나로 확인할 것을 권한다.
- **직접 적재.** `codex_worker`·`claude_worker`·`control_transport`의 패키지 없는 적재와 MCP 서버 기동을 실행하지 않았다. `test_worker_remains_importable_as_its_direct_job_root`와 MCP를 띄우는 시험(`test_redesign_PROFILES`, `test_control_preview`, `test_redesign_ACTIVITIES`)이 덮는다.
- **종료 뒤 마지막 행.** 이제 검토 실행만이 아니라 모든 실행의 tracker가 줄바꿈 없는 마지막 행을 `live=False` 관찰 사실로 받는다. 저장되는 관찰 사실이 실행마다 하나 늘 수 있다.
- **pump 범위.** 한 `ControlTransport` 인스턴스는 자기 생성 뒤 다른 인스턴스가 `issue`한 전송을 읽지 않는다. 운영 코드는 엔진마다 인스턴스 하나지만, 시험 가운데 이 순서에 의존하는 것이 있는지 전수로 확인하지 않았다.
- **dict 사건 경로.** `_observe_running`은 시험 대역의 dict 사건을 여전히 받지만, dict 사건에는 행 바이트가 없어 검토 대화를 기록하지 않는다. 이 경로를 쓰는 운영 코드는 없다. 대역을 모두 묶음으로 바꾸면 이 경로를 지울 수 있다.
- **줄바꿈.** 시험 파일 일부를 스크립트로 고치면서 작업 트리 사본이 CRLF가 되었다. 커밋된 blob은 `.gitattributes`(`eol=lf`)에 따라 정규화되었고, 커밋 diff는 실제 변경 줄만 담는다(`git show --stat HEAD`: 36개 파일, 927줄 추가, 882줄 삭제).

## 5. 전제가 틀렸거나 계획을 바꾼 지점

- **IO-01 drain의 대상.** 조사가 미확인으로 남긴 `_drain_review_observations`의 처리 행은 줄바꿈으로 끝나지 않은 마지막 행이었다. 옛 시험(`AuditConsumerConnections`)이 그 행을 덧붙인 뒤 drain하는 것으로 확인했다. 러너 묶음의 `end_offset`은 버퍼에 남은 부분 행까지 포함하므로, 조사 제안대로 "마지막 batch의 end_offset부터" 읽을 수 없었다. 그래서 종료 뒤 러너가 그 행을 한 번 더 묶음으로 보내게 하고 drain을 지웠다(4절의 세 번째 위험).
- **검토 행 번호.** 행 번호는 러너가 세는 공백 아닌 행의 번호(`first_row + index`)다. 전에는 엔진 커서가 빈 행도 셌다. 번호가 상태 없이 정해지므로 CAS 실패 뒤 재시도에서도 같은 번호가 나온다. 저장 필드 이름 `event_index`는 바꾸지 않았다.
- **IO-02 전달 순서.** 조사의 첫 제안(전송 뒤 `record_delivery` 한 번)은 요청 payload가 `record_delivery`가 정하는 `deadline_offset_ms`를 담는다는 점과 충돌한다. 전송 뒤에 기한을 정하면 작업자가 옛 기한을 받는다. 그래서 조사가 적은 대안대로 기한·요청 생성(`issue_self_check`)과 오프셋 기록(`record_delivery`)을 나눴다.
- **IO-13 출처 검사.** 연산자마다 출처가 하나가 되었으므로 `validate_rules`가 `basis.source`까지 검사한다. 조사 제안은 단위 규칙만 적었다. 전에는 프로필 결박이 없는 tracker가 임의 출처를 받았다.
- **IO-16 `initialization.adapter_for`.** 프로필을 받는 이 함수는 남기고 본문만 `provider_adapter`로 바꿨다. 시험 약 30곳이 이 이름을 patch하기 때문이다.
- **RUN-24 프로필과 인자.** 러너가 프로필 값으로 조용히 덮어쓰지 않고, 프로필과 함께 준 도구 인자를 거부한다. AGENTS.md의 "무시되는 설정을 남기지 않는다"를 따랐다. 프로필 없는 호출(`probe_cli.py`)은 두 인자를 그대로 쓴다.
- **IO-05 Claude 비교.** 전에는 final 파일을 의미 비교(`canonical_json`)했지만, 이제 도출한 바이트와 같은지 비교한다. 직렬화는 변경 전 Claude worker가 `final.txt`를 쓸 때 쓰던 `json.dumps(..., ensure_ascii=False, allow_nan=False)` 그대로이므로 final artifact 바이트는 전과 같다.
- **IO-06 문자열 검사.** 공통 검사는 Claude worker의 규칙(비공백, NUL 없음)을 쓰므로 Codex 요청의 문자열 필드도 공백만인 값을 거부한다. Codex의 `sandbox`는 필수 필드로 옮겼다(전에는 선택 목록에 있으면서 없으면 거부됐다).
- **IO-07 오류 봉투.** `engine.control`이 ID 계산 전에 예외를 내면 CLI 오류 봉투의 `request_id`가 `UC-…` 대신 `QR-…`다(조사가 예고한 미세 변경).
- **IO-19 close의 예외.** `close`의 pump는 inbox 파일마다 `ValueError`를 삼킨다. 이미 영수증을 받은 요청 ID의 inbox 파일이 다른 내용으로 바뀌어 있으면 `_reject_delivery_file`이 "different content" 오류를 내는데, 이 오류가 실행 종료 절차를 멈추지 않게 하기 위해서다. 이때 그 요청 ID의 outbox에는 먼저 쓴 영수증이 그대로 남고, 바뀐 파일에는 새 영수증을 쓰지 않는다.
- **다른 그룹과 겹치는 줄.** `model_runner.py` 63–65행의 `budget_kind == "operations"` 검사는 결정 4(그룹 A) 소관이라 건드리지 않았다. 바로 아래 66–72행을 RUN-24로 고쳤으므로 병합 때 인접 충돌이 날 수 있다. `cli.py`의 `timeline --include-operator`(OPS-06, 그룹 F)도 건드리지 않았다. `operational_dispositions.py`(그룹 C)와 `lifecycle_engine.py`(그룹 A), `submission.py`(그룹 C)에는 각각 한두 줄만 고쳤다.
- **`probe_codex.py`.** 지운 `adapter.inspect`를 부르므로 그룹 F가 삭제하기 전까지 이 스크립트는 동작하지 않는다(설계 4.6이 허용).

## 이음새 요청

- 2절의 공유 정의를 이음새 계약 표로 옮길지, 특히 제어 어휘·바인딩·응답 스키마를 `control_transport`에 둔 배치(worker가 직접 적재하는 모듈이라서)를 통합자가 확정한다.
- `ObservationBatch`의 필드가 늘었으므로 다른 그룹이 새로 만드는 시험 대역은 `rows`·`first_row`를 채워야 한다.

## 추가한 이름

- 공개 함수·상수: 2절 표 전부. 그 밖에 `ObservationTracker.issue_self_check`.
- 바뀐 서명: `ObservationTracker.record_delivery(obligation_id, *, source_offset)`(요청을 만들지 않음), `ControlTransport.request_self_check(binding, *, request)`, `engine._review_observation_source(execution_id, batch, index)`, `CodexModelRunner.worker_options(evidence_dir)`, 러너 `claude_only_assigned_model` 기본값 `None`.
- 지운 이름: `cli.control_request_id`, `engine._runner_tools`, `engine._drain_review_observations`, `LocalCLIAdapter.inspect`·`parse_output`, `observations.OBSERVATION_OPERATORS`·`OBSERVATION_SOURCES`·`_OPERATOR_SUBJECTS`, `codex_worker._REMOVED_ENV`·`_write_status`, `codex_adapter._paths`.
- 새 수집 사유 문자열: `final_response_mismatch`(`final_text_mismatch`, `structured_output_*` 대체).
- 새 시험 도우미: `tests/research_fixtures.write_checkpoint`.
- 설정 키, 사건 종류, 상태 필드, CLI 인자는 추가하지 않았다. 저장 모양이 바뀐 것은 자기 점검 의무의 `snapshot`(`by_source`·`event_ids`·`active_duration_ms` 없음)과 프로필 `rule_bindings`(6개 조합)이다.

# do-math 경량화 조사: 영역 IO (외부 모델 프로세스, CLI 제어, 관찰 전송)

이 문서는 `기준.md`의 산출 형식에 따른 IO 영역의 조사 결과다. 모든 좌표는 2026-09-26 작업 트리(HEAD `8d2ffd0`, 작업 트리 변경 없음)의 현재 원문이다. 경로의 기준 위치는 `C:/math/.claude/skills/do-math/`다. `scripts/do_math/`는 `do_math/`로, `scripts/tests/`는 `tests/`로 줄여 쓴다.

후보는 무게 순서로 배열했다. 앞의 네 후보(IO-01~IO-04)가 이 영역의 중심이다. 모두 관찰 전달 이음새에 있다. IO-01과 IO-02에서는 두 곳이 같은 값을 따로 만든 뒤 서로 대조하며, 값이 어긋나면 판정이 조용히 멈춘다. IO-03과 IO-04에서는 작업자가 합법적인 규칙을 고르거나 응답 형식을 실수하면 그 결과가 운영 AI 실행으로 이어진다. 나머지 후보는 같은 지식을 여러 곳에 적은 곳을 하나로 합치는 정리다. 대부분 동작을 보존하며, 동작이 바뀌는 후보는 각 후보의 `동작` 필드에 적었다.

## 1. 읽은 범위

전문을 읽은 파일은 다음과 같다.

| 파일 | 행 수 |
|---|---|
| `do_math/claude_adapter.py` | 62 |
| `do_math/claude_stream.py` | 192 |
| `do_math/claude_worker.py` | 135 |
| `do_math/codex_adapter.py` | 316 |
| `do_math/codex_worker.py` | 208 |
| `do_math/cli.py` | 726 |
| `do_math/control_contracts.py` | 140 |
| `do_math/control_transport.py` | 515 |
| `do_math/observation_transport.py` | 26 |
| `do_math/observations.py` | 1250 |
| `references/CLI-실행-계약.md` | 965 |
| `do_math/model_runner.py`(이음새의 소비자) | 383 |
| `C:/math/임시/경량화-조사-2026-09-26/기준.md` | 120 |
| `C:/math/docs/do-math/검사-경량화-이음새-계약.md` | 159 |

일부만 읽은 파일은 다음과 같다. 모두 이음새를 따라가며 판정에 필요한 범위만 읽었다.

| 파일 | 읽은 행 |
|---|---|
| `do_math/engine.py` | 89-212, 333-420, 935-960, 1240-1410, 2860-3040, 3615-3632, 3700-3716 |
| `do_math/execution_profiles.py` | 325-400(그 밖에 grep으로 30-33, 80-83, 210) |
| `do_math/initialization.py` | 27-95 |
| `do_math/submission.py` | 1535-1609 |
| `do_math/operational_dispositions.py` | 95-115 |
| `do_math/scheduled_operator.py` | 525-540 |
| `do_math/state_checks.py` | 106-111 |
| `do_math/file_io.py` | 1-30, 97-111, 146-154 |
| `do_math/repository.py` | 548-562 |
| `do_math/provider_wait.py` | 6-8 |
| `do_math/record_schemas/domains.py` | 307-316 |
| `references/공통-실행.md` | 110-160 |
| `tests/test_observations.py` | 325-345 |
| `tests/test_redesign_ENGINE.py` | 440-510 |
| `tests/test_codex_adapter.py` | 83-88 |
| `tests/test_cli.py` | 140-160 |
| `tests/test_claude_stream.py` | 1-34 |
| `기억/layer3/L-0020.md` | grep으로 관련 행만 |

## 2. 후보

#### IO-01: 관찰 행을 model_runner와 engine이 각자 다시 읽고 해석한 뒤 서로 대조한다

- 유형: 이음새중복
- 위치: `do_math/model_runner.py:149-178`, `do_math/observation_transport.py:7-26`, `do_math/engine.py:2880-2905`, `do_math/engine.py:2907-2927`, `do_math/engine.py:2943`, `do_math/engine.py:2951-2956`, `do_math/engine.py:3014`
- 현상: stdout JSONL 한 행을 관찰 사건으로 바꾸는 규칙이 세 곳에 있다. 규칙의 내용은 다음과 같다. 행은 `\n`으로 나누고 빈 행은 건너뛴다. `json.loads`에 실패하면 `{"type":"unparsed_observation","bytes":<행 길이>}`로 대체한다.
  - `model_runner.observe`(`model_runner.py:161-173`)는 1 MiB 단위로 읽은 바이트를 나누고 해석한다. 그 결과를 `ObservationBatch(events, offsets, ...)`로 넘긴다. batch는 행마다 `(시작, 끝)` 오프셋을 싣지만 원 행 바이트는 싣지 않는다(`observation_transport.py:9-15`).
  - identity_review 실행이면 `engine._review_observation_source`(`engine.py:2880-2905`)가 같은 `stdout.jsonl`을 사건마다 다시 연다. 자기 커서 `_review_event_cursors`에서 `readline`하고 같은 규칙으로 다시 해석한다. 그 결과가 batch의 사건과 다르면 `ValueError("review observation differs from its actual provider row")`를 낸다(`engine.py:2902-2903`).
  - `engine._drain_review_observations`(`engine.py:2907-2927`)는 같은 읽기·해석을 세 번째로 구현한다.
  - 커서 상태는 저장 실패 때 되돌리기 위해 별도로 복사된다(`engine.py:2943`, `engine.py:3014`).

  세 사본은 지금은 같은 결과를 낸다. 한 사본의 대체 규칙이나 빈 행 처리를 바꾸면 identity_review 관찰 전체가 예외로 멈추고, 그 결함을 막는 공유 정의는 없다.
- 제안: 정본은 `observation_transport.py`에 둔다. 이 모듈은 이미 두 끝점이 함께 import한다.
  1. `decode_observation_row(raw: bytes) -> dict` 하나를 정의하고 `model_runner.observe`가 그것을 쓴다.
  2. `ObservationBatch`에 `rows: list[bytes]` 필드를 더한다. 값은 각 사건의 원 행 바이트(`\n` 포함)이며 `offsets`와 같은 순서다.
  3. `engine._review_observation_source`는 파일을 다시 열지 않는다. artifact 원문으로 `batch.rows[index]`를 쓰고, 행 번호는 실행별 정수 계수기 하나로 센다. 사건 대조와 `_review_event_cursors`의 파일 오프셋은 사라진다.
  4. `_drain_review_observations`가 계속 필요하면 마지막 batch의 `end_offset`부터 읽고 같은 해석 함수를 쓰게 한다. 이 경로가 실제로 처리하는 행이 무엇인지는 미확인이다. `model_runner.py:210-214`는 종료 뒤 완전한 행을 이미 모두 batch로 보낸다. 따라서 drain이 처리하는 행은 `\n`으로 끝나지 않은 마지막 행뿐일 가능성이 있다.
- 동작: 보존. artifact에 저장되는 바이트는 `model_runner`가 같은 파일에서 읽은 바이트다. 사건 순서와 행 번호도 같다.
- 실익: identity_review 사건마다 발생하던 파일 open·seek·readline 1회가 사라진다(추정: 사건 수만큼의 파일 호출). `engine.py`에서 약 35행, 커서 상태와 그 복원이 줄어든다. 두 해석의 불일치로 관찰이 멈추는 실패 경로가 없어진다.
- 위험과 보호: 행 번호(`event_index`)의 계산이 바뀌면 검토 대화 기록의 순서 대조가 깨질 수 있다. `tests/test_redesign_ENGINE.py`의 `test_review_public_dialogue_keeps_raw_row_order_and_retries_after_failed_cas`와 `tests/test_research_reliability.py`의 `test_one_native_chunk_is_one_owner_transaction`, `test_terminated_stream_replay_preserves_events_without_live_reviews`가 덮는다.
- 확신: 높음. 세 사본과 대조 예외를 원문에서 확인했다. drain 경로의 필요성만 미확인이다.
- 다른 영역: `engine.py`(엔진 영역), `model_runner.py`.

#### IO-02: 자기 점검 요청 객체를 transport와 tracker가 따로 만들고 해시로 대조한다

- 유형: 이음새중복
- 위치: `do_math/control_transport.py:241-265`, `do_math/observations.py:641-651`, `do_math/observations.py:733-754`, `do_math/observations.py:626-639`, `do_math/engine.py:3018-3028`
- 현상: 작업자에게 전달하는 자기 점검 요청은 `{"self_check_id", "execution_id", "payload"}` 객체다. 이 객체를 두 곳이 독립적으로 만든다.
  - `ControlTransport.request_self_check`(`control_transport.py:250-251`)가 객체를 만들어 `worker-inbox/`에 쓰고, 그 객체를 반환한다. 엔진은 반환값을 버린다(`engine.py:3024-3025`).
  - `ObservationTracker.record_delivery`(`observations.py:649-651`)는 같은 모양의 `issued`를 다시 만든다. `payload`는 `self_check_feedback(obligation)`을 다시 계산한 값이다. 이 객체의 `_raw_json` 해시를 `delivered_request_sha256`으로 저장한다.
  - `_acknowledge_poll`(`observations.py:750-752`)은 작업자가 `control_self_check`로 읽어 간 결과를 이 해시와 대조한다. 다르면 아무 기록 없이 반환한다.
  - `_start_call`(`observations.py:634-639`)은 인지 오프셋(`acknowledged_source_offset`)이 있어야 "응답 전 연구 행동"을 판정한다.

  따라서 두 생성 코드 가운데 하나에 필드를 더하거나 payload 계산을 바꾸면 인지 확인이 조용히 영구 실패한다. 그 결과 응답 전 행동 위반은 더 이상 판정되지 않는다. 이 상태를 드러내는 오류나 사건도 없다.

  같은 자리에서 전달 오프셋도 두 번 잰다. `engine.py:3022`는 전송 전 `batch.stream_size()`를 `record_delivery`에 넘긴다. `engine.py:3027`은 전송 뒤 다시 잰 값으로 `delivered_source_offset`을 덮어쓴다. 최종 값은 전송 뒤 값이다. 응답 기한의 기준 시각(`observations.py:647-648`)은 전송 전에 정해진다.
- 제안: 정본은 `observations.py`의 새 함수 `self_check_request(obligation) -> dict`다. 이 함수가 요청 객체를 한 번 만든다.
  - `record_delivery(obligation_id, *, source_offset, request)`는 받은 `request`를 해시만 한다.
  - `ControlTransport.request_self_check(binding, *, request)`는 받은 객체의 키 집합과 `execution_id`를 검사하고 쓴다.
  - 엔진은 같은 객체 하나를 두 호출에 넘긴다.
  - 오프셋은 전송 뒤 한 번만 재서 `record_delivery`에 넘기고 `engine.py:3027`의 덮어쓰기를 지운다.
- 동작: 요청 객체의 통합은 보존이다. 오프셋 단일화는 변경(미세)이다. `record_delivery`를 전송 뒤에 부르면 응답 기한의 기준 시각이 파일 쓰기에 걸린 시간만큼 늦어진다. 이것을 피하려면 `record_delivery`를 전송 전에 그대로 두고, 오프셋 기록만 전송 뒤의 별도 호출로 분리한다.
- 실익: 요청 객체의 생성 1곳, `self_check_feedback` 중복 계산 1회, `stream_size` 호출 1회가 줄어든다. 인지 확인이 소리 없이 멈추는 실패 경로가 사라진다.
- 위험과 보호: 해시 입력이 바뀌면 기존 인지 판정 시험이 깨진다. 덮는 시험은 `tests/test_research_reliability.py`의 `test_native_poll_ack_requires_the_exact_successful_returned_request`, `test_native_command_after_delivery_without_ack_is_only_missing_response_evidence`, `test_buffered_command_before_delivery_is_not_a_new_action_violation`이다.
- 확신: 높음. 두 생성 지점, 무기록 반환, 반환값을 버리는 호출을 원문에서 확인했다.
- 다른 영역: `engine.py`(엔진 영역).

#### IO-03: 프로필이 실제로 생산되지 않는 관찰 신호를 광고하고, 작업자가 그 신호를 쓰면 운영 점검이 열린다

- 유형: 불필요기능(문제 발생 여지 포함)
- 위치: `do_math/observations.py:33-39`, `do_math/observations.py:42-56`, `do_math/observations.py:587-607`, `do_math/observations.py:1059-1078`, `do_math/execution_profiles.py:210`, `do_math/engine.py:2957`, `do_math/engine.py:2962`, `do_math/engine.py:3000-3006`, `references/공통-실행.md:130-139`
- 현상: `observation_rule_contract()`의 docstring은 이 함수가 "실제로 생산되는 신호 종류"를 돌려준다고 적는다(`observations.py:43`). 연구 수행 프로필은 이 목록 전체를 `rule_bindings`로 받는다(`execution_profiles.py:210`). 그러나 두 출처는 운영 코드에 생산자가 없다.
  - `adapter_active_intervals`(`active_duration_gte`): 활성 시간은 사건의 `active_duration_ms` 필드나 `research_activity_started`·`research_activity_finished` 사건으로만 쌓인다(`observations.py:595-607`). `research_activity_`로 grep하면 `observations.py:603`, `observations.py:606`과 `tests/test_observations.py:333-338`만 나온다. do-math가 만든 이 사건 이름을 Codex나 Claude CLI가 낼 수는 없다.
  - `execution_events`의 `counter_gte`·`iteration_gte`: 값은 사건 최상위의 `counters`·`iterations` 필드에서만 온다(`observations.py:593-594`).
  - 운영 코드에서 tracker에 사건을 넣는 곳은 두 곳이다. 하나는 공급자 stdout 행이고(`engine.py:2957`, `model_runner.py:161-173`), 다른 하나는 엔진이 만든 `{'type':'tick'}`이다(`engine.py:2962`). grep `\.observe(` 결과는 이 두 곳뿐이다. 최상위 `counters`나 `active_duration_ms`를 담은 공급자 사건은 확인되지 않았다. 이 필드들은 시험에서만 쓰인다.

  작업자가 문서 표(`공통-실행.md:130-139`)를 보고 이런 규칙을 쓰면 신호는 끝내 측정되지 않는다. 첫 관찰 구간이 지나면 `observation_unavailable`이 발생하고, 그 사건은 `operational_review_due` 후속을 단다(`observations.py:1076-1078`). 엔진은 이 후속으로 운영 점검 실행을 큐에 넣는다(`engine.py:3000-3006`). 작업자의 합법적 선택 하나가 모델 실행 한 건을 낳는다.
- 제안: 정본인 `OBSERVATION_SOURCES`에서 생산자 없는 조합을 뺀다. 대상은 `adapter_active_intervals` 전체, `execution_events`의 `counter_gte`·`iteration_gte`다. `_ingest_event`의 대응 분기(`observations.py:593-607`)와 `_snapshot`의 해당 `by_source` 항목도 뺀다. 문서 표 `공통-실행.md:130-139`도 같은 목록으로 줄인다. `event_recorded`는 사건 최상위 `id`에서만 값을 얻는다(`observations.py:602`). 두 CLI의 사건에 최상위 `id`가 있는지는 확인하지 못했다. 이 연산자는 실측 뒤 같은 처분을 정한다. 생산자를 새로 구현해 광고를 참으로 만드는 선택지도 있다. 두 선택지 가운데 어느 쪽을 택할지는 사용자 결정이다.
- 동작: 변경. 연구 수행 프로필의 `rule_bindings`가 줄어든다. 이 신호를 쓰는 작업자 규칙은 수신 때 "등록되지 않은 관찰 대상"으로 반려된다. 이미 저장된 인스턴스의 프로필에 뺀 조합이 있으면 `validate_observation_rule_contract`(`execution_profiles.py:80-83`에서 호출)가 거부할 수 있다. 저장 인스턴스를 어떻게 다룰지 함께 정해야 한다.
- 실익: 측정될 수 없는 규칙이 운영 점검 실행을 여는 경로가 사라진다. 한 건마다 모델 실행 1회가 줄어든다(추정. 발생 빈도는 미측정). 그 밖에 코드 약 20행, 문서 표 3행이 줄어든다.
- 위험과 보호: 활성 시간 누적 시험 `tests/test_observations.py`의 `test_active_duration_counts_only_observed_progress_intervals`, `tests/test_redesign_OBSERVATION.py`의 `test_missing_active_measurement_is_reported_not_zero_or_wall_time`, `tests/test_execution_observation_profile.py`의 프로필 결박 시험이 바뀌거나 삭제된다. 저장 프로필의 호환을 덮는 시험은 없다.
- 확신: `adapter_active_intervals`는 높음이다. 운영 코드에 생산자가 없음을 grep 전수로 확인했다. `execution_events`의 카운터는 중간이다. 공급자 사건 형식을 실측하지 않았다.
- 다른 영역: `execution_profiles.py`, `references/공통-실행.md`, 역할 계약(규칙 작성 지침).

#### IO-04: 자기 점검 응답의 형식 검사가 수신자에만 있고, 형식 반려가 운영 점검 실행으로 이어진다

- 유형: 생산자자기확인부재
- 위치: `do_math/observations.py:77-92`, `do_math/observations.py:929-934`, `do_math/observations.py:987-992`, `do_math/control_transport.py:450-451`, `do_math/control_transport.py:316-326`, `do_math/control_transport.py:487-488`, `do_math/engine.py:1354-1357`, `references/공통-실행.md:167`
- 현상: 자기 점검 응답의 스키마 `SELF_CHECK_RESPONSE_SCHEMA`는 수신 함수 `record_self_check_response`(`observations.py:931`)에서만 쓰인다. 작업자가 응답을 보내는 도구 `control_self_check`의 `inputSchema`는 `response`를 `{"type":"object"}`로만 선언한다(`control_transport.py:450-451`). `worker_self_check`(`control_transport.py:316-326`)는 응답을 검사하지 않고 inbox에 쓴다. 작업자가 받는 형식 설명은 산문뿐이다(`공통-실행.md:167`). 스키마 위반 응답은 `self_check_rejected`로 기록되고 `operational_review_due` 후속을 단다(`observations.py:987-990`). 엔진은 그 후속으로 운영 점검 실행을 큐에 넣는다(`engine.py:1354-1357`). 필드 이름 하나를 틀린 응답이 모델 실행 한 건이 된다. 작업자 쪽에는 제출 전에 이 오류를 알 방법이 없다.
- 제안: 검사 정본은 `SELF_CHECK_RESPONSE_SCHEMA` 하나로 유지하고, 생산자 쪽 두 지점에서 같은 스키마를 쓴다.
  1. `_mcp_server`의 `control_self_check` 처리(`control_transport.py:487-488`)에서 `response`가 있으면 이 스키마로 먼저 검사한다. 위반이면 도구 오류(`-32602`)로 즉시 돌려준다. `submit_draft`처럼 필요할 때만 `do_math` 패키지를 불러오면 된다(`control_transport.py:470-474`의 선례).
  2. 같은 스키마를 도구의 `inputSchema.properties.response`에 넣어 모델에게 공개한다.

  수신 검사는 그대로 둔다. 작업자는 신뢰 경계 밖에 있기 때문이다. 기한, 증거 현재성, 규칙 포괄 같은 상태 의존 검사는 수신자에만 남는다.
- 동작: 변경. 형식이 틀린 응답은 기록된 반려와 운영 점검 대신 도구 호출 오류가 된다. 작업자는 같은 호출을 고쳐 다시 보낸다.
- 실익: 형식 오류 한 건마다 운영 점검 모델 실행 1회와 반려 기록·피드백 게시가 줄어든다(추정. 빈도는 미측정).
- 위험과 보호: MCP 서버가 Windows Job 안에서 스크립트로 직접 실행되므로 패키지 import 경로가 깨질 수 있다. 직접 실행 import를 덮는 선례 시험은 `tests/test_codex_adapter.py`의 `test_worker_remains_importable_as_its_direct_job_root`다. MCP 도구의 스키마 검사 자체를 덮는 시험은 없다.
- 확신: 중간. 수신 전용 검사와 운영 점검 연결은 원문으로 확인했다. 도구 inputSchema를 CLI가 실제로 강제하는지는 확인하지 않았다.
- 다른 영역: `engine.py`, `references/공통-실행.md`.

#### IO-05: 최종 응답의 선택과 대조를 공급자마다 다른 층이 맡는다

- 유형: 이음새중복
- 위치: `do_math/claude_worker.py:119-125`, `do_math/claude_adapter.py:46-62`, `do_math/codex_adapter.py:302-306`, `do_math/model_runner.py:369-380`
- 현상: "최종 응답 바이트가 native stream의 완결 응답과 같다"는 조건이 공급자마다 다른 층에 있다.
  - Claude: worker가 Job 안에서 stdout 전체를 `parse_stream`으로 해석한다. 선택된 `structured_output`을 `json.dumps(..., ensure_ascii=False, allow_nan=False)`로 직렬화해 `final.txt`에 쓴다(`claude_worker.py:120-124`). 수집기는 같은 stdout을 다시 해석하고, 파일 바이트를 `canonical_json` 비교로 대조한다(`claude_adapter.py:49-62`). 한 조건을 두 직렬화 규칙이 맞물려야 통과시킨다.
  - Codex: `final.txt`는 CLI의 `--output-last-message`가 쓴다. 기본 `validate_final`은 늘 `[]`를 반환한다(`codex_adapter.py:305-306`). 따라서 일반 수집(`collect`)은 이 파일을 stream과 대조하지 않는다. 같은 대조("마지막 앞 사건이 `agent_message`이고 그 text 바이트가 final과 같다")는 저장된 증거를 재검증하는 `verified_native_final`에만 있다(`model_runner.py:371-377`). 이 함수는 stdout을 `json.loads`로 한 번 더 해석한다.

  한 실행의 stdout 전체는 worker, collect, `verified_native_final`에서 최대 세 번 해석된다.
- 제안: 정본은 어댑터의 `validate_final(parsed, final)` 하나다.
  - Codex의 `agent_message` 대조를 `model_runner.py:371-377`에서 `CodexExecAdapter.validate_final`로 옮긴다. `verified_native_final`의 공급자 분기는 사라진다.
  - Claude는 worker가 final을 만들지 않고, 수집기가 `parse_response` 결과에서 final 바이트를 한 번 도출한다. `LocalCLIAdapter.collect`에 `final_bytes(parsed, file_raw)` 훅을 두어 Codex는 파일을, Claude는 도출값을 쓴다. 그러면 Claude worker의 `claude_stream` import와 `claude_adapter.validate_final`의 직렬화 대조가 사라진다.
- 동작: 변경. Codex의 일반 수집에 대조가 새로 생겨 조건이 엄격해진다. Claude는 `final.txt`를 worker가 쓰지 않는다. 증거 디렉터리의 파일 목록이 바뀌며, 수집 결과의 `final` artifact 바이트는 같다.
- 실익: 실행마다 stdout 전체 해석 1회가 줄어든다(Claude worker). 코드 약 25행이 줄고, 직렬화 규칙 두 개의 일치를 요구하는 이음새가 사라진다.
- 위험과 보호: Codex 일반 실행에서 `agent_message`가 마지막 앞 사건이 아닌 정상 stream이 있으면 새로 실패하게 된다. `verified_native_final`이 같은 가정을 이미 쓰지만, 일반 수집에 대한 실측은 없다. 덮는 시험은 `tests/test_native_final_submission.py`의 `test_verified_native_stream_retains_exact_bytes_and_serialized_evidence`, `test_status_alone_bad_stream_changed_request_and_unconfirmed_barrier_rejected`, `tests/test_provider_final_contract.py`의 `test_claude_text_terminal_retains_protocol_checks_and_exact_text`, `tests/test_claude_adapter.py`의 `test_final_output_comparison_preserves_json_types_and_rejects_duplicates`다.
- 확신: 중간. 조건의 위치와 반복 해석은 원문으로 확인했다. Codex 일반 stream의 마지막 사건 구조는 실측하지 않았다.
- 다른 영역: `model_runner.py`.

#### IO-06: 두 worker가 요청 검사와 프로세스 실행 골격을 각자 구현한다

- 유형: 이음새중복(죽은코드 포함)
- 위치: `do_math/codex_worker.py:23-39`, `do_math/codex_worker.py:91-128`, `do_math/codex_worker.py:164-197`, `do_math/claude_worker.py:12-53`, `do_math/claude_worker.py:89-129`, `do_math/codex_adapter.py:265-275`, `do_math/model_runner.py:50-53`
- 현상: 두 worker의 `run()`은 거의 같은 순서로 같은 일을 한다(`codex_worker.py:164-197`, `claude_worker.py:89-129`).
  1. argv·요청·stdin·스키마 해시로 status를 만들고 `execution_id`·`profile_ref`를 복사한다.
  2. 환경을 정리하고 `.scratch/.execution-temp`를 TEMP로 지정한다.
  3. `Popen`과 `communicate(timeout)`으로 실행하고, 시간 초과면 kill한다.
  4. status를 기록한다.

  차이 가운데 CLI 동작에서 오지 않는 것이 있다. Codex는 `BaseException`을 잡고 오류 문구를 남기지 않는다. Claude는 `Exception`을 잡고 `error`를 남긴다. `load_request`의 공통 검사도 두 벌이다. 필드 집합, NUL 없는 문자열, `max_runtime_seconds`, `scholarly_server`, 바인딩 검사가 그것이다(`codex_worker.py:91-128`, `claude_worker.py:27-53`). `max_runtime_seconds` 규칙은 `model_runner.py:50-53`에 세 번째 사본이 있다.

  status 필드의 이음새도 흩어져 있다. 생산자인 두 worker가 `("execution_id", "profile_ref")`를 각자 적고(`codex_worker.py:178`, `claude_worker.py:99`), 소비자인 `collect`가 같은 튜플을 다시 적는다(`codex_adapter.py:273`). status 상태 문자열 `exited`·`timeout`도 양쪽에 따로 적혀 있다. Claude worker는 공통 조각을 `codex_worker`에서 import한다(`claude_worker.py:13`). 그 가운데 `ControlTransport`는 `codex_worker`를 거친 재수출이다.

  죽은 코드도 둘 있다.
  - `_REMOVED_ENV`(`codex_worker.py:23-27`)는 `_ENV_ALLOWLIST`(`codex_worker.py:31-33`)와 교집합이 없다. 그래서 `sanitized_environment`의 `not in _REMOVED_ENV` 조건(`codex_worker.py:39`)은 늘 참이다.
  - `codex_argv` 금지 검사(`codex_worker.py:102-103`)는 바로 아래의 미지 필드 검사(`codex_worker.py:104-106`)가 같은 입력을 이미 거부한다.

  "control 바인딩이 없으면 출력 스키마가 필요하다"는 조건은 Claude worker에만 있다(`claude_worker.py:35-36`). 이 조건이 CLI 동작 차이에서 오는지는 확인되지 않았다.
- 제안: 정본은 `codex_worker.py`에 두는 공통 함수 `run_cli(request_path, request, command, *, environment, finalize=None)`와 `check_common_request(request, required, optional)`다. 이 파일은 두 worker가 이미 공유하는 모듈이며, Job 안에서 직접 import할 수 있다. 공급자 worker는 argv 구성, 공급자별 필드 검사(effort 집합, sandbox, `claude_only_assigned_model`)와 환경 허용 목록만 가진다. status의 결박 키 튜플은 공통 모듈의 상수 하나로 두고 `collect`가 import한다. `_REMOVED_ENV`와 `codex_argv` 분기를 지운다. 공통 모듈의 이름을 중립적으로 바꿀지는 통합자가 정한다. 새 모듈을 만들면 IO-08의 식별 범위에 넣어야 한다.
- 동작: 보존. 예외 처리를 한쪽으로 맞추면 Codex worker 오류 기록에 `error` 문구가 생기는 변경이 있다. 어느 쪽에 맞출지는 통합자가 정한다.
- 실익: 약 45행이 줄어든다. 요청 필드 규칙의 사본이 3개에서 1개로 준다.
- 위험과 보호: Job 직접 실행 import 경로. `tests/test_codex_adapter.py`의 `test_worker_remains_importable_as_its_direct_job_root`, `test_unknown_worker_request_field_is_rejected`, `test_invalid_timeout_duplicate_json_and_windows_sandbox_fail_before_start`, `test_sanitized_environment_removes_every_forced_api_route`와 `tests/test_claude_adapter.py`의 `test_worker_uses_login_stdin_schema_and_only_configured_mcp`가 덮는다.
- 확신: 높음. 두 골격과 죽은 조건을 원문에서 대조했다.
- 다른 영역: `model_runner.py`.

#### IO-07: 제어 요청 ID와 source 정규화를 CLI와 엔진이 각자 계산한다

- 유형: 이음새중복
- 위치: `do_math/cli.py:227-259`, `do_math/cli.py:551-562`, `do_math/cli.py:569-575`, `do_math/engine.py:333-371`
- 현상: CLI의 `_control`은 source 파일을 읽어 base64·SHA-256·크기로 정규화한다(`cli.py:232-236`). 이어서 `control_request_id`로 요청 ID를 계산해 늘 `request_id=`로 엔진에 넘긴다(`cli.py:237-242`). 엔진의 `control`은 그 정규화된 source를 받으면 다음을 반복한다(`engine.py:352-366`).
  1. base64를 디코드한다.
  2. 해시와 크기를 다시 대조한다.
  3. 같은 값을 다시 인코딩하고 다시 해시한다.

  엔진에는 CLI 정규화와 같은 일을 하는 경로 분기(`engine.py:359-362`)와, `request_id`가 없을 때 같은 `control_request_id`를 부르는 분기(`engine.py:368-371`)도 있다. 엔진은 이 함수를 `cli`에서 import한다(`engine.py:369`). 방향이 뒤집힌 의존이다. `request_id`와 `idempotency_key`의 상호 배제 검사는 `cli.py:229-230`과 `engine.py:348-349`에 둘 다 있다. `request_id` 형식 규칙(1~128자, ASCII 영숫자·`-`·`_`)은 JSON 요청 스키마(`cli.py:574`)와 엔진 코드(`engine.py:343-345`)에 각각 적혀 있다. CLI 경로에서 source 파일 하나는 base64 인코딩 2회, SHA-256 3회를 거친다.
- 제안: 요청 ID와 source 정규화의 정본은 엔진 쪽 `control`이다. `control_request_id`는 `engine.py`(또는 `control_contracts.py`)로 옮긴다. `cli._control`은 `config={"path", "name"}`, `request_id=explicit`, `idempotency_key=key`를 그대로 넘기고, 반환의 `request_id`를 `args._resolved_request_id`로 쓴다. CLI의 정규화, 상호 배제 검사, ID 계산을 지운다. 형식 규칙은 한 정규식 상수로 두고 스키마와 엔진이 함께 참조한다.
- 동작: 대체로 보존. 요청 ID와 적용 결과는 같다. `engine.control`이 ID 계산 전에 예외를 내면 오류 봉투의 `request_id`가 `UC-…` 대신 `QR-…`가 된다. 오류 봉투의 식별자만 바뀌는 미세 변경이다.
- 실익: CLI에서 약 12행이 줄고, source 제어마다 파일 전체 인코딩 1회와 해시 2회가 줄어든다. 역방향 의존 `engine → cli`가 사라진다.
- 위험과 보호: 재전송 재생(replayed)의 요청 ID 동일성. `tests/test_cli.py`, `tests/test_redesign_ENGINE.py`, `tests/test_redesign_STORAGE.py`의 idempotency 관련 시험이 덮는다(파일 단위로 grep 확인. 개별 시험명은 확인하지 않았다).
- 확신: 높음. 두 계산 경로와 import 방향을 원문에서 확인했다.
- 다른 영역: `engine.py`(엔진 영역).

#### IO-08: 능력 식별의 파일 범위가 worker가 실제로 실행하는 모듈을 덮지 않는다

- 유형: 기타(식별 범위 누락, 문제 발생 여지)
- 위치: `do_math/codex_adapter.py:124-139`, `do_math/claude_worker.py:12-19`, `do_math/codex_worker.py:13-20`, `do_math/claude_adapter.py:15`, `do_math/initialization.py:46-50`
- 현상: `capability_identity`는 다음 파일의 해시로 구현을 식별한다(`codex_adapter.py:131-137`): CLI 실행 파일, worker 파일 하나, `windows_job`, `control_transport`, `file_io`, `codex_adapter`, 공급자 어댑터 파일. 능력 증거는 이 식별이 현재 값과 정확히 같을 때만 재사용된다(`initialization.py:48`).
  - Claude worker는 `codex_worker`(요청 바인딩 검사, status 기록), `claude_stream`(final 선택), `scholarly`를 import해 실행한다(`claude_worker.py:13-19`). 이 셋은 식별에 없다.
  - Codex worker도 `scholarly`를 import한다(`codex_worker.py:14`).
  - Claude 수집기가 쓰는 `claude_stream`(`claude_adapter.py:15`)도 식별에 없다.

  그래서 이 모듈들이 바뀌어도 식별이 같아 기존 능력 증거가 그대로 재사용된다.
- 제안: 식별 파일 목록을 어댑터 클래스 속성 하나(`identity_modules`)로 두고, worker가 실제로 import하는 모듈을 모두 넣는다. Claude는 `claude_worker`, `codex_worker`, `claude_stream`, `scholarly`를 넣고, Codex는 `codex_worker`, `scholarly`를 넣는다. IO-06으로 공통 모듈이 생기면 그 모듈도 넣는다.
- 동작: 변경. 식별 dict가 바뀌므로, 적용 뒤 첫 확인에서 기존 능력 증거가 한 번 무효가 되고 재관찰이 필요하다.
- 실익: 구현이 바뀌었는데도 옛 증거를 쓰는 경로가 사라진다. 추가 비용은 식별 계산마다 `cached_sha256` 2~4회이며, 지문이 같으면 캐시에 적중한다.
- 위험과 보호: 식별 모양을 가정하는 시험. `tests/test_redesign_PROFILES.py`의 `test_capability_identity_has_host_worker_and_cli_hashes`가 덮는다.
- 확신: 중간. 누락 자체는 원문으로 확인했다. 이음새 계약 2.1절은 "worker 능력 식별의 파일 범위가 control_transport와 file_io"라고 적는다. 이 범위가 의도적으로 좁힌 것인지는 확인하지 못했다.
- 다른 영역: `initialization.py`, `docs/do-math/검사-경량화-이음새-계약.md` 2.1절.

#### IO-09: 엄격 JSON 해석 훅이 네 벌 있다

- 유형: 이음새중복
- 위치: `do_math/codex_worker.py:42-48`, `do_math/claude_stream.py:18-28`, `do_math/cli.py:33-39`, `do_math/repository.py:551-561`, `do_math/codex_adapter.py:77-80`, `do_math/claude_stream.py:93-96`, `do_math/claude_adapter.py:57`
- 현상: "중복 키 거부" 훅이 네 곳에 같은 본문으로 있다. `codex_worker._pairs`, `claude_stream._pairs`, `cli._pairs`, `repository._unique_pairs`다. "비유한 상수 거부"도 `claude_stream._constant`와 `repository._reject_constant` 두 벌이다. 지수 넘침(`1e999`) 거부는 한 곳이 `json.dumps(allow_nan=False)`(`codex_adapter.py:80`), 다른 곳이 `json_digest`(`claude_stream.py:96`)로 한다. `claude_adapter.validate_final`은 `claude_worker._pairs`를 쓰는데, 이 이름은 `codex_worker`에서 재수출된 것이다(`claude_adapter.py:57`).
- 제안: 정본은 `file_io.py`의 `unique_pairs`, `reject_constant`, `strict_json_loads(raw)`다. `strict_json_loads`는 두 훅과 넘침 검사를 함께 적용한다. `file_io`는 이미 Job 안에서 직접 적재되는 커널이다(이음새 계약 2.1). `repository`는 이 두 이름을 재수출하고, 나머지 사본은 지운다. `cli._pairs`는 `CliInputError` 대신 `ValueError`를 내게 된다. `cli.main`은 `ValueError`도 `input_error`, 종료 코드 2로 처리하므로(`cli.py:710-712`) 관찰 결과는 같다.
- 동작: 보존.
- 실익: 약 25행이 줄고, 해석 규칙의 사본이 5개에서 1개로 준다.
- 위험과 보호: `tests/test_claude_stream.py`의 `test_duplicate_keys_nonfinite_and_overflow_are_invalid`, `tests/test_codex_adapter.py`의 `test_ambiguous_or_nonfinite_native_events_cannot_establish_completion`이 덮는다.
- 확신: 높음.
- 다른 영역: `repository.py`, `payloads.py`, `submission.py`, `model_runner.py`(모두 `repository._unique_pairs` 사용자).

#### IO-10: 압축 정렬 JSON 직렬화와 원자 게시가 커널 밖에 다시 구현돼 있다

- 유형: 이음새중복
- 위치: `do_math/file_io.py:102-111`, `do_math/file_io.py:146-153`, `do_math/control_transport.py:36-38`, `do_math/control_transport.py:58-64`, `do_math/codex_worker.py:159-161`, `do_math/codex_adapter.py:198`
- 현상: `json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))`의 UTF-8 바이트가 네 곳에 따로 적혀 있다. `file_io.json_digest` 내부, `control_transport._canonical`, `codex_worker._write_status`, `codex_adapter.start`의 스냅샷이다. `control_transport._atomic_json`(`control_transport.py:58-64`)은 `file_io.write_bytes_atomic`(`file_io.py:102-111`)과 한 줄씩 같다. 부모 생성, 같은 prefix·suffix의 임시 파일, `atomic_replace`까지 같다. 전송 영수증의 `request_sha256`은 `json_digest`로 계산되고, 파일 본문은 `_canonical`로 쓰인다. 지금은 두 규칙이 같지만, 같게 유지하라고 묶는 정의는 없다.
- 제안: `file_io.compact_json_bytes(value)`(`allow_nan=False`)를 정본으로 두고 `json_digest = sha256(compact_json_bytes(value))`로 바꾼다. `_canonical`, `_write_status`, 스냅샷 직렬화는 이 함수를 쓴다. `_atomic_json(path, value)`는 `write_bytes_atomic(path, compact_json_bytes(value))`로 바꾼다.
- 동작: 보존(유효한 입력에서). NaN이 든 worker 요청을 스냅샷할 때 지금은 통과하지만 제안 뒤에는 오류가 된다. 이 입력은 `load_request`의 정상 경로에서 만들어지지 않는다.
- 실익: 약 12행이 줄고, 직렬화 규칙 사본이 4개에서 1개로 준다.
- 위험과 보호: `tests/test_control_transport_io.py` 전체, `tests/test_codex_adapter.py`의 `test_collect_reports_start_snapshot_bytes_without_rereading_them`이 덮는다.
- 확신: 높음.
- 다른 영역: 없음.

#### IO-11: 제어 바인딩의 필드 목록과 검사가 네 곳에 있다

- 유형: 이음새중복
- 위치: `do_math/control_transport.py:118-134`, `do_math/control_transport.py:136-149`, `do_math/control_transport.py:280`, `do_math/control_transport.py:501-511`, `do_math/codex_worker.py:51-88`, `do_math/model_runner.py:78-81`
- 현상: 바인딩 필드 `endpoint, transport_id, capability, execution_id, grant_id`(선택 `workspace`) 목록이 여러 곳에 따로 적혀 있다.
  - `issue`가 이 필드로 바인딩을 만든다(`control_transport.py:122-128`).
  - `mcp_server_config`(`control_transport.py:138`)와 MCP 진입 `main`(`control_transport.py:505`)이 목록을 각자 적는다.
  - `worker_submit`이 부분 목록을 적는다(`control_transport.py:280`).
  - 바인딩 모양의 검사는 소유 모듈이 아닌 `codex_worker.validate_execution_binding`(`codex_worker.py:71-88`)에 있고, `model_runner`가 그 함수를 빌려 쓴다(`model_runner.py:79`).
- 제안: 정본은 `control_transport.py`의 `BINDING_FIELDS` 상수와 `ControlTransport.validate_binding(binding, *, execution_id, cwd=None)`이다. `validate_execution_binding`은 바인딩 부분을 이 메서드에 맡긴다. `mcp_server_config`와 `main`은 상수로 인자를 만든다.
- 동작: 보존.
- 실익: 필드 목록 사본이 4개에서 1개로 줄고, 약 10행이 준다.
- 위험과 보호: `tests/test_control_transport_io.py`, `tests/test_codex_adapter.py`의 `test_build_argv_is_direct_cli_with_isolating_probe_flags`, `tests/test_claude_adapter.py`의 `test_worker_uses_login_stdin_schema_and_only_configured_mcp`가 덮는다.
- 확신: 높음.
- 다른 영역: `model_runner.py`.

#### IO-12: 제어 도구 어휘를 transport, worker, 관찰 코드가 문자열로 각자 적는다

- 유형: 이음새중복
- 위치: `do_math/control_transport.py:27`, `do_math/control_transport.py:324`, `do_math/control_transport.py:443-452`, `do_math/claude_worker.py:67`, `do_math/codex_worker.py:146-147`, `do_math/observations.py:551`, `do_math/observations.py:670-707`, `do_math/submission.py:1547`
- 현상: 다음 이름들을 생산자(transport, worker)와 소비자(관찰 코드)가 각자 문자열로 적는다.
  - MCP 서버 이름 `execution_control`: `claude_worker.py:67`, `codex_worker.py:146-147`, `observations.py:551`.
  - 도구 이름 `control_submit`·`control_receipt`·`control_self_check`: 정의는 `control_transport.py:443-452`, 해석은 `observations.py:676-707`.
  - 자기 점검 응답 요청 ID 접두 `self-check-`: 생성은 `control_transport.py:324`, 역산은 `observations.py:699`.
  - 요청 종류 문자열: `_REQUEST_KINDS`(`control_transport.py:27`), MCP 스키마의 enum(`control_transport.py:447`), `submission.py:1547`, `observations.py:676`·`observations.py:700`.

  어휘가 이미 어긋난 곳이 하나 있다. MCP `control_submit`의 enum은 `self_check_response`를 공개하지 않는다(`control_transport.py:447`). 그러나 transport는 이 종류를 받고, 관찰 코드는 `control_submit`으로 온 `self_check_response`를 처리한다(`observations.py:700`).
- 제안: 정본은 `control_transport.py`의 상수들이다. 서버 이름, 도구 이름, 요청 종류, `self_check_request_id(self_check_id)` 함수를 여기에 둔다. 두 worker와 `observations.py`, `submission.py`가 이것을 import한다. `control_transport`는 두 worker가 이미 import하고, `observations`는 패키지 안에서 import할 수 있다. MCP enum은 `_REQUEST_KINDS`에서 만든다. `self_check_response`를 enum에 공개할지, 관찰 분기를 지울지는 통합자가 정한다.
- 동작: 보존. enum을 넓히면 모델에게 공개되는 도구 설명이 바뀐다.
- 실익: 문자열 사본 약 15개가 상수 참조로 바뀐다. 어휘가 어긋나면 관찰이 조용히 빗나가는 위험이 줄어든다.
- 위험과 보호: `tests/test_research_reliability.py`의 `test_owner_distinguishes_preview_and_boundary_from_self_check`, `tests/test_redesign_ENGINE.py`의 `test_safety_boundary_updates_obligation_only_after_publication`이 덮는다.
- 확신: 높음.
- 다른 영역: `submission.py`.

#### IO-13: 관찰 연산자 표가 코드 안에 세 가지 모양으로 적혀 있다

- 유형: 이음새중복
- 위치: `do_math/observations.py:21-39`, `do_math/observations.py:42-56`, `do_math/observations.py:303-319`, `do_math/observations.py:331-361`, `references/공통-실행.md:130-139`
- 현상: 연산자마다 대상 종류, 단위, 출처가 있다. 이 한 표를 코드가 여러 번 표현한다.
  - `OBSERVATION_OPERATORS`(`observations.py:21-24`)는 `_OPERATOR_SUBJECTS`(`observations.py:25-30`)의 키 집합과 같다.
  - "연산자 → 단위" 규칙은 세 번 적혀 있다. `observation_rule_contract`(`observations.py:52-53`), `validate_observation_rule_contract`(`observations.py:349-350`), `validate_rules`의 부정형 검사(`observations.py:305`, `observations.py:316-319`)다.
  - `validate_observation_rule_contract`는 목록을 한 조각씩 다시 검사한다. 이 검사는 `normalized in observation_rule_contract()`와 같은 뜻이다.
  - 문서 표 `공통-실행.md:130-139`가 같은 표를 한 번 더 적는다.
- 제안: 정본은 `OPERATORS = {operator: {"subject_kind", "unit", "sources"}}` 표 하나다. `OBSERVATION_OPERATORS`, `_OPERATOR_SUBJECTS`, `OBSERVATION_SOURCES`, 단위 규칙을 이 표에서 파생한다. `validate_observation_rule_contract`의 조건은 계약 목록의 원소 검사로 바꾼다. 문서 표는 정본을 가리키거나, 시험으로 코드 표와 대조한다. IO-03을 채택하면 이 표에서 조합을 빼는 것으로 끝난다.
- 동작: 보존.
- 실익: 약 20행이 줄고, 같은 규칙의 사본이 4개에서 1개로 준다.
- 위험과 보호: `tests/test_redesign_OBSERVATION.py`의 `test_rules_bind_operator_subject_unit_and_evidence`, `tests/test_execution_observation_profile.py`, `tests/test_redesign_PROFILES.py`가 덮는다.
- 확신: 높음.
- 다른 영역: `references/공통-실행.md`.

#### IO-14: 자기 점검 응답 수신에서 스키마 뒤의 수동 재검사에 도달할 수 없다

- 유형: 죽은코드
- 위치: `do_math/observations.py:929-934`, `do_math/observations.py:954-971`
- 현상: `record_self_check_response`는 먼저 `SELF_CHECK_RESPONSE_SCHEMA`로 검사한다. 실패하면 `invalid_response_schema`를 기록하고, 그 뒤 검사는 `if not errors:` 안에서만 실행된다. 스키마를 통과한 입력에서는 다음 조건이 모두 성립한다(`observations.py:79-89`).
  - `rule_results`는 비어 있지 않은 배열이다.
  - 각 행은 정확히 다섯 키를 가진 객체다(`additionalProperties: false`와 `required`).
  - `status`는 세 값 가운데 하나다.
  - 두 참조 목록은 비어 있지 않은 문자열의 배열이다.
  - `reason`은 비어 있지 않은 문자열이다.

  따라서 `rule_results_missing`(`observations.py:957`), `invalid_rule_result`(`observations.py:962-963`), `invalid_rule_status`(`observations.py:964-965`), `invalid_rule_evidence`(`observations.py:968-971`) 분기에는 도달할 수 없다. grep `invalid_rule_|rule_coverage_mismatch`로 `tests/`를 찾으면 결과가 없다. 이 분기들을 기대하는 시험도 없다.
- 제안: 네 분기를 지운다. 규칙 포괄(`rule_coverage_mismatch`)과 증거 대조 검사는 남긴다.
- 동작: 보존.
- 실익: 약 10행이 줄어든다.
- 위험과 보호: `tests/test_redesign_OBSERVATION.py`의 `test_response_deadline_is_current_and_rejection_reaches_worker`가 수신 경로를 덮는다.
- 확신: 높음. 스키마 조건과 분기 조건을 한 줄씩 대조했다.
- 다른 영역: 없음.

#### IO-15: provider_observation과 사용량 선택식이 수집기와 runner에 두 벌 있다

- 유형: 이음새중복
- 위치: `do_math/codex_adapter.py:293-300`, `do_math/model_runner.py:225-240`, `do_math/model_runner.py:249`, `do_math/claude_stream.py:42-63`
- 현상: 사용량 선택식 `usage_total`, 없으면 마지막 `usage`는 두 곳에 있다(`codex_adapter.py:296`, `model_runner.py:226-227`). `provider_observation` 객체도 두 곳에서 만든다. `collect`는 장벽이 확인된 분기에서만 만들고(`codex_adapter.py:293-300`), `model_runner`는 그것이 없을 때 같은 키의 대체 객체를 만든다(`model_runner.py:233-237`). 공급자 한도 분류 `provider_limit`은 Claude 전용 함수다. 그런데 `model_runner`가 공급자와 무관하게 부른다(`model_runner.py:249`). Codex 해석 결과에는 `rate_limits`가 없어서 늘 `None`이 된다.
- 제안: `collect`가 두 분기 모두에서 `provider_observation`을 돌려주게 하고, `model_runner`는 그 값만 쓴다. 공급자 한도 분류는 어댑터 메서드 `provider_failure(parsed)`로 옮긴다. Claude는 `provider_limit`을 부르고, Codex는 `None`을 돌려준다.
- 동작: 보존.
- 실익: 약 10행이 줄어든다. 사용량 선택 규칙이 한 곳에만 남는다.
- 위험과 보호: `tests/test_claude_stream.py`의 `test_only_native_admission_rejection_is_provider_failure`, `tests/test_provider_wait.py`, `tests/test_redesign_PROFILES.py`가 덮는다.
- 확신: 높음.
- 다른 영역: `model_runner.py`.

#### IO-16: 공급자에서 어댑터로의 대응이 네 곳에 있다

- 유형: 이음새중복
- 위치: `do_math/initialization.py:27-35`, `do_math/cli.py:454-466`, `do_math/model_runner.py:26-29`, `do_math/model_runner.py:277-285`, `do_math/model_runner.py:369`, `do_math/provider_wait.py:6-7`
- 현상: 공급자 이름에서 어댑터 클래스와 기본 실행 파일(`shutil.which(name) or name`)을 고르는 규칙이 네 곳에 따로 있다. `initialization.adapter_for`, `cli`의 `profile` 명령, 두 `ModelRunner`의 생성자, `verified_native_final`이다. `verified_native_final`은 요청의 `claude_path` 키 존재로 공급자를 다시 추론한다. 모델 이름에서 공급자를 정하는 규칙은 `provider_wait.provider_for` 한 곳에 있다.
- 제안: 정본은 `claude_adapter.py`(또는 새 소형 표)의 `ADAPTERS = {"codex": (CodexExecAdapter, "codex"), "claude": (ClaudePrintAdapter, "claude")}`와 `adapter_for(provider, path=None)`다. 네 곳은 모두 이것을 부른다. `verified_native_final`은 요청의 실행 파일 키로 공급자를 고르는 일을 한 함수에 맡긴다.
- 동작: 보존.
- 실익: 약 15행이 준다. 세 번째 공급자를 추가할 때 고칠 곳이 네 곳에서 한 곳으로 준다.
- 위험과 보호: `tests/test_claude_adapter.py`의 `test_router_dispatches_claude_and_codex_without_mutating_shared_runner`, `test_profile_accepts_claude_provider`가 덮는다.
- 확신: 높음.
- 다른 영역: `initialization.py`, `model_runner.py`.

#### IO-17: 공유 어댑터 기반 클래스가 Codex 전용 내용을 담고, 파싱 훅이 둘이다

- 유형: 복잡성
- 위치: `do_math/codex_adapter.py:113-171`, `do_math/codex_adapter.py:211-217`, `do_math/codex_adapter.py:302-310`, `do_math/claude_adapter.py:18-47`
- 현상: `LocalCLIAdapter`("공유 기반")는 Codex의 worker 모듈, 실행 파일 키, JSONL 해석기, `describe`를 기본값으로 갖는다(`codex_adapter.py:116-118`, `codex_adapter.py:147-171`). `CodexExecAdapter`는 빈 하위 클래스다(`codex_adapter.py:309-310`). 두 `describe`는 `--version`·`--help` 실행과 필수 플래그 대조, 같은 모양의 반환을 각자 구현한다(`claude_adapter.py:23-44`, `codex_adapter.py:147-171`). 파싱 훅도 둘이다. `parse_output`은 정적 속성이고 `parse_response(raw, request)`는 메서드이며, Claude는 둘 다 재정의한다. `parse_output`은 `inspect`(`codex_adapter.py:216`)와 기본 `parse_response`에서만 쓰인다. `inspect`는 운영 코드가 부르지 않고 `probe_codex.py:79`, `probe_codex.py:85`만 부른다. `describe`의 `reported_evidence`(`claude_adapter.py:42`)는 grep 결과 읽는 곳이 없다.
- 제안:
  1. Codex 전용 속성과 `describe`의 자료 부분을 `CodexExecAdapter`로 옮긴다.
  2. `describe`는 기반 클래스에 한 번 구현한다. 공급자는 `help_commands`와 `required_flags`만 준다. Codex의 `--ask-for-approval` 조건은 "전역 help의 필수 플래그"로 표현한다.
  3. 파싱 훅은 `parse_response(raw, request)` 하나로 두고, `inspect`는 `parse_response(raw, {})`를 부른다.
  4. `reported_evidence`를 지운다.
- 동작: 보존. `describe` 결과에서 `reported_evidence`가 빠진다. 소비자 `capability_evidence`(`execution_profiles.py:355-380`)는 이 필드를 읽지 않는다.
- 실익: 약 20행이 줄고 재정의 지점이 준다.
- 위험과 보호: `tests/test_codex_adapter.py`의 `test_surface_requires_the_flags_used_by_the_worker`, `tests/test_claude_adapter.py`의 `test_profile_accepts_claude_provider`, `probe_codex.py`가 덮는다.
- 확신: 높음.
- 다른 영역: `probe_codex.py`.

#### IO-18: CLI `--describe`의 계약 표가 실제 정의와 따로 적혀 이미 어긋났다

- 유형: 이음새중복(죽은코드 포함)
- 위치: `do_math/cli.py:614-619`, `do_math/cli.py:670-676`, `do_math/cli.py:636-644`, `do_math/state_checks.py:106-110`, `references/CLI-실행-계약.md:32`, `references/CLI-실행-계약.md:48`
- 현상: `describe_commands`의 `response_fields`는 `['schema_version','request_id','command','exit_code','result OR error']`다(`cli.py:616`). 실제 봉투 `_emit`은 `response_contract` 필드를 더 낸다(`cli.py:674`). 계약 문서(`CLI-실행-계약.md:32`)와 README도 이 필드를 적는다. `--describe`만 실제와 다르다. `inspection_exit_codes`(`cli.py:617`)는 `state_checks.inspection_exit_code`(`state_checks.py:106-110`)의 규칙을 손으로 다시 적은 것이다. 계약 문서 48행은 `--request-id`를 받는 제어를 열거하는데, 코드가 받는 `quiesce`·`release-quiesce`(`cli.py:121-126`)가 빠져 있다.

  `_json_arguments`에는 도달할 수 없는 검사가 둘 있다. 요청 스키마가 이미 `caller`의 enum을 강제하므로 `cli.py:639-640`의 재검사는 도달할 수 없다. `command`도 스키마 enum으로 검사되고, `describe_commands`가 모르는 명령이면 예외를 낸다. 그래서 `cli.py:629-630`도 도달할 수 없다.
- 제안: 봉투 필드 목록을 모듈 상수 하나로 두고 `_emit`과 `describe_commands`가 함께 쓴다. `inspection_exit_codes`는 `inspection_exit_code`를 네 상태에 적용해 만든다. 계약 문서 48행의 열거는 `--describe`의 결과를 가리키는 문장으로 바꾸거나 두 명령을 더한다. 도달 불가 검사 두 개를 지운다.
- 동작: 변경. `--describe` 출력에 `response_contract`가 더해진다. 나머지는 보존이다.
- 실익: 발견 계약과 실제 봉투의 불일치가 사라진다. 약 6행이 준다.
- 위험과 보호: `tests/test_cli.py`의 `--describe` 호출(145행 부근, 시험명 미확인)이 덮는다. 필드 목록을 단언하는 시험은 없다.
- 확신: 높음. 불일치는 원문의 사실이다.
- 다른 영역: `state_checks.py`, `README.md`.

#### IO-19: 제어 전송의 pump가 닫힌 전송까지 매번 전수 조회한다

- 유형: 운영비용
- 위치: `do_math/control_transport.py:194-225`, `do_math/control_transport.py:400-408`, `do_math/engine.py:943-947`, `do_math/engine.py:606`
- 현상: 엔진의 `_controls`는 run 루프마다 `self._transport.pump(...)`를 부른다(`engine.py:946-947`). `pump`는 `root.glob("*/inbox/*.json")`으로 인스턴스의 모든 전송 디렉터리를 훑는다. 캐시된 최종 영수증도 매번 `file_fingerprint`로 stat한다(`control_transport.py:201-211`). 전송은 실행마다 하나씩 생긴다. 닫혀도(`close`, `engine.py:839` 외 6곳) 디렉터리와 inbox 파일은 지워지지 않는다(grep `execution-control|_transport.close`). 따라서 pump 한 번의 비용은 인스턴스가 지금까지 받은 제어 요청의 총수에 비례해 커진다. 메모리에 없는 영수증을 찾는 `_receipt`도 `root.glob("*/outbox/<id>.json")`로 전체를 훑는다(`control_transport.py:407`).
- 제안: 전송 객체가 연 전송 ID 집합을 메모리에 둔다. `issue`에서 넣고 `close`에서 뺀다. `pump`는 이 집합의 `inbox`만 읽는다. 재시작 뒤의 복구는 `state.json`이 `open`인 전송만 집합에 넣는다. 닫힌 전송의 inbox에 새 파일이 생기는 경로는 `worker_submit`이 상태를 먼저 확인하므로(`control_transport.py:276-279`) 경합뿐이다. 이 경합 파일은 닫는 시점에 한 번 pump해 영수증을 쓴다.
- 동작: 변경(경계 사례). 닫힌 뒤 경합으로 도착한 전달은 닫기 직전의 마지막 pump까지만 영수증을 받는다.
- 실익: pump마다 stat 수가 "누적 요청 수"에서 "열린 전송의 요청 수"로 준다. 측정값은 없다. 추정 근거는 실행 수 × 실행당 요청 수이며, 수백 실행 인스턴스에서 루프마다 수백~수천 stat이다.
- 위험과 보호: `tests/test_control_transport_io.py`의 `test_final_delivery_is_not_reread_until_its_fingerprint_changes`, `test_concurrent_real_files_do_not_reproduce_old_permission_error`가 덮는다. 직전 라운드의 pump 캐시(지문 기반)는 바꾸지 않는다.
- 확신: 중간. 누적 구조는 원문으로 확인했다. 실제 루프 빈도와 파일 수는 측정하지 않았다.
- 다른 영역: `engine.py`.

#### IO-20: control_contracts의 설정 모양과 엔진의 설정 검사가 같은 키·자료형을 두 번 적는다

- 유형: 이음새중복
- 위치: `do_math/control_contracts.py:65-77`, `do_math/engine.py:89-107`, `do_math/engine.py:163-205`
- 현상: `CONFIG_PATCH`는 설정 키마다 자료형을 적는다(`control_contracts.py:65-77`). 엔진은 `DEFAULT_CONFIG`·`OPTIONAL_CONFIG`로 키 집합을 다시 적는다(`engine.py:89-107`, `engine.py:167`). `validate_config`는 같은 자료형 조건을 다시 검사한다. 불리언 세 키(`engine.py:175-177`), 양의 정수 목록(`engine.py:182-190`), `lean_command` 배열(`engine.py:195-198`), `allowed_axioms` 배열(`engine.py:201-202`)이다. 읽기 전용 확인 결과 지금은 두 키 집합이 같다. 사용한 명령은 `python -c "from do_math import engine, control_contracts as c; ..."`였고, 결과는 `patch-only [] / engine-only []`였다. 새 키를 한쪽에만 더하면 모양 검사 없이 통과하거나(`CONFIG_PATCH`에는 `additionalProperties: false`가 없다) 엔진이 거부한다.
- 제안: 정본은 설정 키 표 하나(`키 → (기본값, 자료형 조각, 선택 여부)`)다. `CONFIG_PATCH`의 `properties`, `DEFAULT_CONFIG`, `OPTIONAL_CONFIG`를 이 표에서 파생한다. `validate_config`는 자료형을 모양 검사에 맡기고, 양수 범위, 열거, 교차 조건만 남긴다. 표의 위치(엔진 또는 `control_contracts`)는 설정 영역과 함께 정한다.
- 동작: 보존.
- 실익: 약 20행이 줄고, 키 목록 사본이 2개에서 1개로 준다.
- 위험과 보호: `tests/test_control_shapes.py`의 `test_shape_check_preserves_partial_configuration_and_nullable_candidate_fields`, `test_initialization_checks_the_boolean_flags_its_owner_actually_consumes`가 덮는다.
- 확신: 중간. 중복은 확실하다. 이 표가 설정 영역 조사와 겹치는지는 통합자가 판정해야 한다.
- 다른 영역: `engine.py`(설정 영역).

#### IO-21: 안전 경계의 `inflight_calls` 조건을 엔진이 같은 프로세스에서 다시 검사한다

- 유형: 수신재검사중복
- 위치: `do_math/control_transport.py:342-343`, `do_math/engine.py:1321-1324`, `do_math/engine.py:947`, `do_math/engine.py:3618`
- 현상: `ControlTransport._validate_request`가 `safety_boundary`의 `inflight_calls is not False`를 거부한다(`control_transport.py:342-343`). 그 직후 같은 프로세스에서 `deepcopy`한 요청으로 엔진 발행자가 불린다(`control_transport.py:169`, `control_transport.py:179`). 엔진은 같은 조건을 다시 검사한다(`engine.py:1323-1324`). 운영 코드에서 발행자는 `pump`를 통해서만 불린다(`engine.py:947`, `engine.py:3618`). 두 검사 사이에 디스크 왕복, 다른 스레드, 재시작은 없다. `tests/test_redesign_ENGINE.py`(455-506행)는 발행자를 직접 부르지만 모두 `inflight_calls: False`를 넣는다.
- 제안: 엔진의 재검사(`engine.py:1323-1324`)를 지운다. 관찰 코드의 같은 조건(`observations.py:680`)은 수신 전에 호출을 분류하는 다른 목적이므로 둔다(보존 판정 참조).
- 동작: 보존.
- 실익: 2행이 준다. 실익이 작으므로 다른 엔진 정리와 묶을 때만 올릴 만하다.
- 위험과 보호: `tests/test_redesign_ENGINE.py`의 `test_safety_boundary_updates_obligation_only_after_publication`이 덮는다.
- 확신: 높음.
- 다른 영역: `engine.py`.

#### IO-22: 작업자 피드백의 공개 필드 허용 목록을 게시 함수가 손으로 유지한다

- 유형: 이음새중복(문제 발생 여지)
- 위치: `do_math/observations.py:1180-1194`, `do_math/observations.py:864-870`, `do_math/observations.py:882-888`, `do_math/observations.py:991-992`, `do_math/observations.py:1160-1170`, `do_math/operational_dispositions.py:99-102`, `do_math/engine.py:1359`, `do_math/engine.py:1380-1385`, `do_math/control_transport.py:213-220`
- 현상: `publish_worker_feedback`는 허용 필드 집합을 손으로 적고, 그 밖의 필드가 있으면 `ValueError`를 낸다(`observations.py:1186-1190`). 피드백을 만드는 곳은 다섯이다. 규칙 파일 반려(`observations.py:867-869`), 규칙 교체(`observations.py:888`), 응답 반려(`observations.py:991-992`), `self_check_feedback`(`observations.py:1166-1170`), `operational_dispositions.worker_feedback`(`operational_dispositions.py:99-102`)다. 지금 허용 집합은 다섯 생산자의 키 합집합과 같다. 생산자가 필드를 하나 더하면 게시가 실패한다.

  제어 영수증 경로에서는 이 실패가 모순된 기록을 남긴다. 게시는 상태 저장(`engine.py:1359`) 뒤에 일어나고, 엔진은 `OSError`만 잡는다(`engine.py:1383-1385`). 따라서 `ValueError`는 `pump`까지 전파된다. `pump`는 그 전달을 `delivery_validation` 거부 영수증으로 기록한다(`control_transport.py:219-220`, `control_transport.py:383-398`). 결과적으로 엔진 상태는 수락, 전송 영수증은 거부가 된다. 이 경로는 가정한 변경에서만 열리며 지금은 발생하지 않는다.
- 제안: 공개 필드 집합을 상수 `WORKER_FEEDBACK_FIELDS`로 두고, 각 생산자가 피드백을 만들 때 같은 상수로 투영하거나 검사한다(생산자 자기 확인). 게시 함수의 검사는 남긴다.
- 동작: 보존.
- 실익: 생산자 변경이 저장 뒤 모순 기록으로 번지는 경로가 사라진다. 행 수는 거의 같다.
- 위험과 보호: `tests/test_redesign_OBSERVATION.py`의 `test_invalid_rules_feedback_preserves_previous_revision`, `test_response_deadline_is_current_and_rejection_reaches_worker`가 덮는다.
- 확신: 낮음. 지금은 발생하지 않는 경로다. 실익은 향후 변경의 안전에 있다.
- 다른 영역: `operational_dispositions.py`, `engine.py`.

## 3. 보존 판정

| 위치 | 겉보기 문제 | 유지 이유 |
|---|---|---|
| `do_math/codex_worker.py:131-156`, `do_math/claude_worker.py:56-86` | 두 argv 구성이 비슷한 일을 한다 | 플래그, MCP 설정 방식(`--config mcp_servers.*` 대 `--mcp-config` JSON), 권한 모드가 두 CLI의 실제 인터페이스 차이다 |
| `do_math/claude_worker.py:80-85` | 출력 스키마를 복사해 `$schema`·`x-contract-id`를 지운다 | Claude CLI가 두 주석을 거부했다는 실측(`기억/layer3/L-0020.md:98`)에서 온 CLI 차이다. 중앙 검사는 원본을 쓴다 |
| `do_math/codex_worker.py:28`, `do_math/claude_worker.py:41`, `do_math/engine.py:171-179` | effort 허용 집합이 여러 벌 있다 | 인스턴스 설정 값과 각 CLI가 받는 값은 서로 다른 집합이다(`CLI-실행-계약.md:194`) |
| `do_math/codex_worker.py:31-39`, `do_math/claude_worker.py:22-24` | 환경 허용 목록이 두 벌 있다 | 공급자별 로그인 상태 변수(`CODEX_HOME` 대 `CLAUDE_CONFIG_DIR` 등)가 다르다. 공통 부분은 이미 하나의 상수를 쓴다(`_REMOVED_ENV`는 IO-06) |
| `do_math/codex_adapter.py:61-110`, `do_math/claude_stream.py:66-192` | JSONL 해석기가 두 개다 | 사건 어휘, 생명주기 순서, 구간·세션·사용량 의미가 두 CLI에서 다르다. 공유할 조각(엄격 JSON 해석)만 IO-09로 합친다 |
| `do_math/observations.py:609-624`, `do_math/observations.py:659-673` | 도구 호출 추적이 공급자별 사건 구조로 분기한다 | `item.*`와 `mcp_tool_call`(Codex), `assistant`·`user`의 `tool_use`·`tool_result`와 `mcp__<server>__<tool>` 이름(Claude)은 CLI 출력 형식의 차이다 |
| `do_math/claude_stream.py:111-112`, `do_math/observations.py:612-615` | 백그라운드 task 사건 이름이 두 모듈에 있다 | 한 곳은 구간 판정용 보존이고, 다른 곳은 호출 수명 추적이다. 소비 목적이 달라 한 정의로 묶으면 두 변경 이유가 결합된다 |
| `do_math/claude_stream.py:42-63`의 Claude 전용 공급자 한도 해석 | Codex에 대응 코드가 없다 | Codex 경로에는 해석할 한도 사건이 없다. 호출 위치만 IO-15에서 옮긴다 |
| `do_math/model_runner.py:305-383`(`verified_native_final`) | `collect`가 이미 검사한 status·해시·장벽을 다시 검사한다 | 입력이 저장된 증거(디스크·Git 기록)이므로 신뢰 경계 밖이다(`기준.md` 40행) |
| `do_math/codex_worker.py:91`, `do_math/claude_worker.py:27`의 Job 안 `load_request` | `adapter.start`가 같은 함수로 이미 검사했다 | 검사 사이에 파일 스냅샷과 별도 프로세스 경계가 있다. 같은 함수를 공유하므로 이음새 중복은 아니다 |
| `do_math/codex_adapter.py:202`와 `do_math/codex_worker.py:179`의 이중 환경 정리 | 같은 정리를 두 번 한다 | Job 생성 시점과 CLI 자식 생성 시점의 프로세스 경계다 |
| `do_math/observations.py:111-114`의 `_raw_json` 해시 | `json_digest`와 바이트가 다르다 | 저장·대조되는 값이라 이음새 계약 2.1이 변종으로 유지를 정했다 |
| `do_math/observations.py:676-687`의 `inflight_calls is False` | transport 검사(IO-21)와 같은 조건이다 | 수신 전에 관찰된 호출을 경계 호출로 분류하는 목적이다. 거부 검사가 아니다 |
| `do_math/model_runner.py:168-171`의 관대한 관찰 해석 | 엄격 해석기(IO-09)와 규칙이 다르다 | 관찰은 행 하나의 실패로 멈추면 안 된다. 권위 판정은 `collect`의 엄격 해석이 맡는다 |
| `do_math/control_transport.py:67-86`(`_create_json_once`) | `write_bytes_atomic`와 비슷하다 | 대상 이름을 선점하는 `os.link` 의미가 다르다. 덮어쓰는 원자 게시와 합치면 안 된다 |
| `do_math/engine.py:199-200`, `do_math/observations.py:493-494`, `do_math/record_schemas/domains.py:312`의 관찰 모드 열거 | 값 목록이 셋이다 | 인스턴스 설정(`event_driven`, `periodic`)과 프로필·tracker(`deadline_only` 포함)는 다른 개념이다 |
| `do_math/control_contracts.py:130-140`(`validate_control_payload`) | 공개 제어(`engine.py:338`)와 inbox 소비(`engine.py:951-952`)에서 두 번 부른다 | 같은 함수를 공유하고, inbox 파일이라는 디스크 경계를 사이에 둔다. 기준 문서의 원칙에 맞는 구조다 |

## 4. 후보 없음

다음 주제는 전문을 읽었고 후보가 없었다.

- `do_math/claude_stream.py`의 구간 선택 논리(`parse_stream`의 init·result 구간, 알림 후속, 종료 뒤 정리 사건): 계약 문서 911행, 954행과 일치한다. 공급자 고유 규칙이다.
- `do_math/codex_adapter.py`의 `start`, `stop`, `wait_for_termination`, `collect`의 장벽·스냅샷 검사.
- `do_math/control_transport.py`의 `receive`, `_store`, `_reject_unvalidated`, `_reject_delivery_file`, `worker_submit`, `wait_receipt`의 영수증 규칙과 파일 이름 안전 검사.
- `do_math/cli.py`의 `build_parser`, `execute`의 명령별 분기(IO-07, IO-18 제외), `_human_status`.
- `do_math/observations.py`의 `evaluate_rules`, `validate_rules`의 비단위 조건, 규칙 결박(`bind_task_rules`, `task_rules_from_execution`, `validate_rule_preparation`), `read_checkpoint`, `preserve_checkpoint`, `capture_checkpoint_files`, `request_checkpoint`, `write_checkpoint_reminder`.
- `do_math/control_contracts.py`의 `CONFIG_PATCH`를 뺀 제어 payload 모양(IO-20 제외).

## 5. 미완료

없음. 다만 추정으로 남긴 값이 있다. IO-03과 IO-04의 발생 빈도, IO-19의 파일 수와 루프 빈도, IO-05의 Codex 일반 stream 끝 사건 구조는 측정하거나 실측하지 않았다. 각 후보의 `실익`과 `확신`에 그 사실을 적었다.

## 6. 작업 중 사건

- 예상과 다른 결과가 셋이었다.
  - 관찰 신호 `adapter_active_intervals`의 생산자가 운영 코드에 없었다(IO-03). 시험만 `research_activity_*` 사건을 넣는다.
  - `--describe`의 `response_fields`가 실제 봉투와 이미 어긋나 있었다(IO-18).
  - Claude worker가 import하는 모듈 셋이 능력 식별 밖에 있었다(IO-08).
- 동작 확인을 위해 읽기 전용 파이썬 명령을 한 번 실행했다(IO-20). 명령은 `python -c "from do_math import engine, control_contracts as c; p=set(c.CONFIG_PATCH['properties']); d=set(engine.DEFAULT_CONFIG)|set(engine.OPTIONAL_CONFIG)|{'host_resources'}; ..."`이고 결과는 `patch-only [] / engine-only [] / optional [8개]`였다.
- IO-01의 `_drain_review_observations`가 실제로 처리하는 행의 종류는 정적 독해만으로 확정하지 못했다. 해당 후보에 미확인으로 적었다.
- 저장소 작문 규범(write-for-reader)의 독해 검토는 합의·독자 파일과 상태 파일을 요구한다. `기준.md`는 산출 파일 하나 외의 저장소 쓰기를 금지한다. 두 요구를 모두 지키려고 합의·독자·상태 파일을 저장소 밖 임시 폴더(`%TEMP%/io-writing`)에 두었다.

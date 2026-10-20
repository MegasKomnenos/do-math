# test_operation_trace

| 항목 | 값 |
|---|---|
| 조각 | `lifecycle` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_operation_trace.py` (101행) |
| 클래스 / 테스트 | 1 / 5 |
| 시험 대상 제품 코드 | `do_math/operation_trace.py`의 `OperationTrace`(`emit`, `close`, `_write_pending`, `_write_live`, `_failed`), `tracing`, `phase`, `workspace_operation`, `child_environment`, `progress`, `phase_rows`(내부의 `trace_rows`), `LIVE_INTERVAL` |
| 사용하는 픽스처 모듈 | 없음 |
| 격리 표지 | 없음 |
| 시작 상태 | 1단(제품 클래스·함수 직접 호출). 저장소·엔진은 없고, 매 시험이 `tempfile.TemporaryDirectory()`에 추적 파일을 실제로 쓴다 |

## 목적

모듈 docstring은 "작업 추적: 단계 행, 실시간 스냅숏, 원격 측정 실패(`do_math.operation_trace`)"를 시험한다고 밝힌다. 제품 모듈의 docstring은 이 추적이 "제한된 운영 원격 측정일 뿐 허가나 수학적 판정이 아니다"라고 정한다(`operation_trace.py` 1행). `OperationTrace`는 작업 하나의 추가 전용 추적 파일(`<id>.jsonl`)과, 활성 구간을 담아 `LIVE_INTERVAL`(1.0초)마다 많아야 한 번 다시 쓰는 실시간 스냅숏(`live/<id>.json`)을 관리한다. 클래스 docstring(22–29행)은 세 가지를 약속한다. 구간 안의 뒤 행은 대기 타이머 하나가 쓰므로 스냅숏이 `LIVE_INTERVAL`보다 더 뒤처지지 않는다. `close`는 둘을 모두 비우고 멈춘다. 닫힌 뒤에 도착한 행은 추적 파일에 붙지만 스냅숏을 다시 쓰지 않는다. 이 모듈은 그 약속과 함께 실패 기록이 예외 문구를 새지 않는 것, 부모 작업 식별자가 자식에게 건너가는 것, 단계 행이 중첩·미완결 작업을 보존하는 것을 검사한다.

## 모듈 수준 요소

- 행 10: `sys.path.insert(0, ...)`로 `scripts/` 폴더를 경로 맨 앞에 넣는다. `do_math` 패키지를 import하기 위한 공통 머리다.
- 행 11: `LIVE_INTERVAL`, `OperationTrace`, `phase`, `phase_rows`, `progress`, `tracing`을 모듈 수준에서 import한다.
- 행 100–101: 직접 실행하면 `unittest.main()`을 부른다.

## OperationTraceTests (행 14–97)

`unittest.TestCase`를 그대로 상속한다. 표지, 클래스 속성, 설정 훅, 도우미가 없다. 모든 시험이 자기 임시 폴더를 만든다.

### `test_telemetry_failure_identifies_operation_without_leaking_exception_text` (행 15–27)
- 성질: 실시간 스냅숏 교체가 실패하면 실패한 조작의 이름과 errno만 남기고 예외 메시지는 원격 측정 기록에 복사하지 않으며, 추적 파일 쓰기는 계속된다.
- 준비: 임시 폴더 위의 `OperationTrace`. 함수 안에서 `OperationTrace`를 다시 import하지만 모듈 수준 import와 같은 이름이다.
- 실행: `atomic_replace`를 `PermissionError(13, 'private request value')`로 실패하게 한 채 `emit({'event': 'started', 'span_id': 'span', 'phase': 'unit'})`를 부른다. 첫 행이므로 `live_written=-inf`에서 곧바로 `_write_live`가 돌고 `replace_live` 단계에서 실패한다. 이어서 `close()`를 부르고 `progress(directory)`를 읽는다.
- 단언: `emit`이 `RuntimeWarning`을 낸다(`assertWarns`). `progress(...)['telemetry_errors'][0]`의 `operation`이 `'replace_live'`, `errno`가 13이다. 그 기록 전체를 JSON으로 직렬화해도 `'private request value'`가 들어 있지 않다. `sink.path`(추적 파일)가 실제 파일로 남아 있다.
- 대역: `mock.patch('do_math.operation_trace.atomic_replace', side_effect=PermissionError(...))`.
- 비고: 실패 기록은 `_failed`가 `errors/<id>.json`에 쓰고 `progress`가 그 폴더를 읽는다. 제품 주석(125–126행)은 "예외 메시지, 원시 argv, 요청은 원격 측정에 복사하지 않는다"고 적는다.

### `test_launcher_trace_correlation_is_separate_from_child_authority` (행 29–40)
- 성질: 실행기 작업의 추적 식별자는 자식 프로세스 환경변수 `DO_MATH_PARENT_OPERATION_ID`로 건너가고, 자식의 단계 행은 그 값을 `parent_operation_id`로 기록한다.
- 준비: 임시 폴더. `@workspace_operation('launcher')`로 감싼 지역 함수 `launcher(workspace)`가 `child_environment()['DO_MATH_PARENT_OPERATION_ID']`를 반환한다.
- 실행: `launcher(directory)`로 부모 식별자를 얻는다. 이 호출은 `directory/operations` 아래에 추적을 연다. 이어 `patch.dict('os.environ', {'DO_MATH_PARENT_OPERATION_ID': parent})` 안에서 `tracing(directory)`와 `phase('child')`를 연다. 새 `OperationTrace`는 생성 시 이 환경변수를 읽는다. 마지막으로 `phase_rows(directory)`를 읽는다.
- 단언: `phase == 'child'`인 행의 `parent_operation_id`가 `parent`와 같다.
- 대역: `patch.dict('os.environ', ...)`로 자식 프로세스의 환경을 흉내 낸다. 실제 자식 프로세스는 없다.
- 비고: 이름은 상관 식별자가 자식의 권한과 "분리된다"고 말한다. 단언은 상관 식별자가 전달된다는 것만 확인하며, 권한이 건너가지 않는다는 것은 단언하지 않는다. 분리의 근거는 제품 `child_environment`의 docstring("Only a trace correlation crosses the process boundary, never authority", 228행)이다. 부모 추적은 `directory/operations`에, 자식 추적은 `directory`에 쓰이므로 `phase_rows(directory)`는 자식 행만 읽는다.

### `test_live_snapshot_is_throttled_but_never_more_than_one_interval_behind` (행 42–58)
- 성질: 한 구간 안의 여러 행은 대기 쓰기 하나로 합쳐지되, 그 대기 쓰기는 한 구간 안에 반드시 일어나 최신 상태를 싣고, 닫으면 타이머가 사라지며 추적 파일에는 모든 행이 남는다.
- 준비: 임시 폴더 위의 `OperationTrace`. 실시간 스냅숏의 교체마다 원본 JSON을 `writes`에 모은 뒤 실제로 `Path.replace`를 하는 대역을 `atomic_replace`에 건다.
- 실행: 서로 다른 `span_id`(`s0`–`s19`)로 `started` 행 20개를 곧바로 `emit`한다. 이후 `5 * LIVE_INTERVAL` 상한 안에서 0.02초 간격으로 `writes`가 둘이 될 때까지 폴링한다. 이어 `s0`의 `completed` 행을 `emit`하고 `close()`한다.
- 단언: 20행 직후 `writes`는 정확히 1개다(메시지 "rows inside one interval share one pending write"). 첫 행은 곧바로 쓰이고 나머지 19행은 타이머 하나를 기다린다. 폴링 뒤 마지막 스냅숏의 `active_spans`는 20개다. 닫은 뒤 `sink.timer`는 `None`이고, 추적 파일은 21줄이다.
- 대역: `atomic_replace`를 기록 후 실제 교체하는 함수로 바꾼다.
- 비고: 실제 `threading.Timer`가 발화하기를 기다린다. 폴링 상한은 `5 * LIVE_INTERVAL`(5초)이다. 21번째 `completed` 행은 닫기 직전에 온 행이므로 대기 쓰기가 예약될 수 있지만, `close`가 그것을 취소한다. 단언은 타이머가 없다는 것까지만 본다.

### `test_a_timer_that_fires_after_close_does_not_recreate_the_removed_snapshot` (행 60–71)
- 성질: `close`와 경합해 이미 발화한 타이머나 닫힌 뒤 도착한 행은 지워진 실시간 스냅숏을 되살리지 않고, 닫힌 뒤의 행도 추적 파일에는 붙는다.
- 준비: 임시 폴더 위의 `OperationTrace`에 `a`, `b` 두 `started` 행을 `emit`한다. 두 번째 행은 구간 안이므로 타이머를 예약한다.
- 실행: `close()` 뒤 `sink.live.unlink()`로 스냅숏을 지운다. 이미 발화해 잠금을 기다리던 타이머를 흉내 내어 `sink._write_pending()`을 직접 부른다(주석). 이어 `a`의 `completed` 행을 `emit`한다.
- 단언: 두 번째 `emit` 직후 `sink.timer`가 `None`이 아니다(메시지 "the second row inside the interval is pending"). 끝에서 `sink.live`가 존재하지 않고, 추적 파일은 3줄이다.
- 대역: 없음. 타이머 경합은 비공개 메서드 `_write_pending`의 직접 호출로 재현한다.
- 비고: 제품의 대응은 `_write_pending`의 `if not self.closed and self.pending is not None` 검사(94행)와 `emit`의 닫힌 뒤 분기(53–59행)다.

### `test_phase_timings_preserve_overlap_and_incomplete_work` (행 73–97)
- 성질: 중첩된 단계는 부모-자식 관계와 겹치는 경과 시간을 보존하고, 끝나지 않은 부모 구간은 실시간 스냅숏에 남으며, 끝난 뒤 스냅숏은 비고, 끊긴 추적 줄은 끝난 시각을 지어내지 않고 건너뛴다.
- 준비: 임시 폴더.
- 실행: `tracing(directory)` 안에서 `phase('parent')`와 그 안의 `phase('child')`를 연다. 자식 안에서 `counters.update(completed_files=2, read_bytes=20)`를 부른다. 자식이 끝난 뒤 부모 안에서 `progress(directory)['rows']`를 `5 * LIVE_INTERVAL` 상한 안에서 0.02초 간격으로 폴링해, 첫 행의 `active_spans` 단계 이름이 `['parent']`가 될 때를 기다린다. 추적을 닫은 뒤 `phase_rows(directory)`를 읽고, 끝으로 `interrupted.jsonl`에 `{"event": "started"}` 줄과 해독할 수 없는 바이트 `\xff` 줄을 써서 다시 읽는다.
- 단언: 폴링 결과가 `['parent']`다. 단계 행은 2개다. 자식 행의 `parent_span_id`가 부모 행의 `span_id`와 같다. 자식 행의 `trace_write_errors`가 0이다. 부모 `elapsed_ns`가 자식 `elapsed_ns` 이상이다. 추적이 닫힌 뒤 `progress(...)['rows']`는 빈 목록이다(`tracing`이 스냅숏을 지운다). 끊긴 파일을 더한 뒤에도 단계 행은 2개다.
- 대역: 없음.
- 비고: 원문 주석(79행)은 "스냅숏은 `LIVE_INTERVAL`만큼 뒤처질 수 있으므로 상한을 두고 폴링한다"고 적는다. 끊긴 파일의 첫 줄은 `span_id`가 없어 `phase_rows`의 필드 검사에서 빠지고, 둘째 줄은 해독 실패로 `incomplete_trace` 행이 되어 역시 빠진다. 제품 주석(267행)은 "끊긴 추가는 모르는 것이지 지어낸 종료 시각이 아니다"라고 적는다. 카운터 값(`completed_files`, `read_bytes`)이 단계 행에 실린다는 것은 단언하지 않는다.

## 관계

- 시험 모듈 가운데 `operation_trace`를 이름으로 부르는 것은 이 모듈 하나다. 제품에서는 아홉 모듈이 이 모듈을 쓴다. `engine.py`(`engine_operation`, `tracing`, `phase`, `measured`, `progress`), `scheduled_operator.py`(`workspace_operation`, `child_environment`), `reporting.py`(`phase_rows`), `parallel.py`와 `repository.py`(`phase`), 그리고 `codex_adapter.py`, `context_store.py`, `git_store.py`, `model_runner.py`, `repository.py`의 `measured` 장식자다. 그 연결을 다른 시험 모듈이 직접 단언하지는 않는다.
- 픽스처 모듈을 쓰지 않는다. 모든 준비는 임시 폴더와 `mock.patch`로 끝난다.
- 두 시험(`test_live_snapshot_...`, `test_phase_timings_...`)은 실제 `threading.Timer` 발화를 상한 있는 폴링으로 기다린다. `시험-지침.md` 4절 규칙 5가 요구하는 "조건 폴링과 상한" 형식이다.
- `test_live_snapshot_...`과 `test_a_timer_...`은 스로틀의 두 끝을 나눠 본다. 앞의 것은 대기 쓰기가 반드시 일어나 최신 상태를 싣는다는 쪽을, 뒤의 것은 닫힌 뒤에는 대기 쓰기가 아무것도 되살리지 않는다는 쪽을 본다.

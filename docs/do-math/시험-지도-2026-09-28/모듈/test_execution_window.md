# test_execution_window

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_execution_window.py` (56행) |
| 클래스 / 테스트 | 1 / 3 |
| 시험 대상 제품 코드 | `do_math/execution_window.py`의 `publish`, `request_finish`, `notice_seconds`; `do_math/repository.py`의 `canonical_json` |
| 사용하는 픽스처 모듈 | 없음 |
| 격리 표지 | 없음 |
| 시작 상태 | 1단(순수 함수와 파일 쓰기 함수를 임시 폴더 위에서 직접 호출). 시계는 람다로 주입한다 |

## 목적

모듈 docstring은 없다. 시험 대상 `do_math/execution_window.py`의 모듈 docstring은 "Monotonic execution deadlines with UTC descriptions and a non-revoking notice."이다. 이 모듈은 실행 하나의 호출 마감을 단조 시계로 계산해 UTC 시각으로 `.control/execution-window.json`에 공개하고(`publish`), 마감 직전에 권한을 거두지 않는 마감 예고 `.control/finish-request.json`을 한 번만 쓴다(`request_finish`). 예고 시간은 `notice_seconds`가 `min(finish_notice_seconds, call_timeout_seconds / 10)`로 정한다. 제품 docstring이 말하듯 마감은 운영 호출에만 있다. 엔진은 `WORK_ROLES`에 속한 역할의 `call_deadline`을 `None`으로 둔다(`do_math/engine.py` 3248–3251행의 주석 "Only operational AI roles have a per-call execution deadline."). 이 모듈은 세 성질을 지킨다. 예고는 권한을 거두지 않고 정확히 한 번 난다. 마감이 없는 작업에는 예고가 없다. 공개 값은 정수 밀리초로 저장 계약에 맞는다.

## 모듈 수준 요소

- 행 8: `sys.path.insert(0, str(Path(__file__).resolve().parents[1]))`로 `scripts/` 폴더를 경로 앞에 넣는다. 파일을 직접 실행하거나 `unittest discover`로 돌려도 `do_math`를 import할 수 있게 하는 공통 머리다. 이 모듈은 `SCRIPTS` 이름을 두지 않는다.
- 행 55–56: 직접 실행하면 `unittest.main()`을 부른다.

## WindowTests (행 12–52)

`unittest.TestCase`를 그대로 상속한다. 표지, 클래스 속성, 설정 훅, 도우미가 없다. 각 테스트는 `tempfile.TemporaryDirectory()`를 작업 공간 `root`로 쓴다.

### `test_actual_remaining_time_and_notice_do_not_revoke_authority` (행 13–30)
- 성질: 공개한 실행 창은 실제 남은 시간을 UTC로 기술하고, 마감 예고는 예고 구간에 처음 들어선 때 한 번만 쓰이며 권한을 거두지 않는다.
- 준비: `config = {"call_timeout_seconds": 30, "finish_notice_seconds": 60}`. 임시 폴더를 작업 공간으로 쓴다.
- 실행: 먼저 `notice_seconds(config)`를 부른다. 이어서 `publish(root, "E", 130, config, clock=lambda: 110, wall_clock=datetime(2026, 9, 19, tzinfo=timezone.utc))`를 부른다. 마지막으로 `request_finish(root, 130, config, clock=...)`를 시계 126, 127, 128로 세 번 부른다.
- 단언:
  - `notice_seconds`는 3이다. `min(60, 30/10)`이므로 호출 제한의 10분의 1이 설정값 60보다 먼저 걸린다.
  - `publish`의 반환값은 다음과 같다. `remaining_ms_at_start`는 20000(130−110초), `deadline_source`는 `"operational_call"`, `effective_deadline_at`은 `"2026-09-19T00:00:20+00:00"`, `finish_notice_at`은 `"2026-09-19T00:00:17+00:00"`(마감 3초 전)이다. 남은 시간은 주입한 단조 시계로 계산하고, UTC 시각은 주입한 벽시계에 더해 얻는다.
  - `request_finish`는 시계 126에서 `False`다(남은 4초가 예고 3초보다 크다). 127에서 `True`다(남은 3초가 3초를 넘지 않는다). 128에서 다시 `False`다(예고 파일이 이미 있다). 곧 예고는 경계에서 포함적으로 나고 한 번만 쓰인다.
  - 작업 공간 루트에는 `stop-request.json`도 `finish-request.json`도 생기지 않는다. `.control/execution-window.json`은 파일로 있고, `.control/finish-request.json`의 `revokes_authority`는 `False`다.
- 대역: 시계 주입(`clock` 람다와 고정 `wall_clock`).
- 비고: 루트에 `stop-request.json`이 없다는 단언은, 예고가 정지 요청으로 쓰이지 않는다는 뜻으로 읽힌다. 예고 파일의 `kind`(`"finish_notice"`)와 `instruction` 문구는 단언하지 않는다.

### `test_work_without_deadline_has_no_finish_notice_after_long_elapsed_time` (행 33–43)
- 성질: 마감이 없는 실행(작업 역할)은 공개 창에 마감·잔여 시간·예고 시각이 모두 없고, 아무리 오래 지나도 예고가 쓰이지 않는다.
- 준비: 앞 시험과 같은 `config`. 임시 폴더.
- 실행: `publish(root, "E", None, config)`, 이어서 `request_finish(root, None, config, clock=lambda: 1000000)`.
- 단언: 반환값의 `effective_deadline_at`, `remaining_ms_at_start`, `finish_notice_at`이 모두 `None`이고 `deadline_source`는 `"none"`이다. `request_finish`는 `False`이고 `.control/finish-request.json`이 없다.
- 대역: 시계 주입(`request_finish`의 `clock`). `publish`는 마감이 `None`이면 시계를 읽지 않으므로 기본값을 쓴다.
- 비고: 반환값의 `effective_notice_ms`(제품은 0으로 둔다)와 창 파일의 존재는 이 시험에서 단언하지 않는다.

### `test_fractional_clock_is_serialized_as_integer_milliseconds` (행 45–52)
- 성질: 단조 시계와 마감이 소수초여도 공개 값은 정수 밀리초로 계산되어 저장 계약의 정규 JSON으로 부호화된다.
- 준비: `config = {"call_timeout_seconds": 3, "finish_notice_seconds": 1}`. 임시 폴더. `canonical_json`은 테스트 안에서 `do_math.repository`로부터 늦게 import한다.
- 실행: `publish(Path(directory), "E", 3.375, config, clock=lambda: 1.125)`, 이어서 `canonical_json(value)`.
- 단언: `remaining_ms_at_start`가 2250이고(3.375−1.125초), `effective_notice_ms`가 300이다(`min(1, 3/10)`초). `canonical_json(value)`가 예외 없이 끝난다. `canonical_json`은 `validate_storage_value`로 부동소수를 `"JSON floating-point numbers are not permitted"`로 거부하므로(`do_math/repository.py` 763–764행), 이 호출의 성공은 공개 값에 float가 하나도 없다는 단언이다.
- 대역: 시계 주입(`clock` 람다). `wall_clock`은 주지 않으므로 실제 현재 UTC가 쓰이지만 그 시각은 단언하지 않는다.
- 비고: 제품은 `Decimal(str(...))`로 빼고 곱해 이진 부동소수 오차 없이 정수로 자른다(`execution_window.py` 29, 36행). 시험의 값 3.375, 1.125, 0.3은 이 경로에서 정확히 떨어지는 값이다.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈:
  - `test_family_records.py`의 `test_actual_execution_window_preserves_integer_measurement_and_owner`(335행 부근)는 `publish`의 결과를 런타임 실행 레코드의 `execution_window`에 넣고 저장·재적재한 뒤 `remaining_ms_at_start`가 정수로 보존되는지 본다. 이 모듈의 세 번째 시험이 부호화 가능성만 보는 것을 저장 왕복까지 넓힌다.
  - `test_stop_flags.py`는 엔진 구동 중 `.control/finish-request.json`이 생기는 것을 단언한다(250행). 이 모듈이 순수 함수로 본 예고가 엔진의 `should_stop` 경로(`engine.py` 3284행의 `execution_window.request_finish` 호출)에서 실제로 쓰이는지를 그쪽이 본다.
  - 작업 역할에 마감이 없다는 규칙은 러너 층에서 검사된다. `test_execution_profiles`의 `test_work_has_no_deadline_and_operations_keep_their_call_window`는 고정 프로필로 부른 러너가 `research_work`에는 `timeout_seconds=None`을 받아 작업자 요청의 `max_runtime_seconds`를 `None`으로 두고, `operational_review`에는 `None`이나 호출 제한 초과를 거부함을 본다. `test_model_runner`의 `WithoutDeadlineTests`는 러너가 `timeout_seconds=None`으로 불렸을 때 정상 반환까지 계속 돌고 정지는 따름을 본다. 엔진이 `WORK_ROLES`에 `call_deadline=None`을 주는 분기(`engine.py` 3250–3251행) 자체를 단언하는 시험은 이 두 모듈에 없다.
- 저장 스키마: 공개 값의 여섯 키는 `do_math/record_schemas/schemas.py`의 `execution_window` 객체 스키마(322–325행)가 요구하는 필드와 같다. 이 모듈은 스키마 검증을 직접 하지 않는다.
- 픽스처 모듈을 쓰지 않으므로 다른 모듈과 공유하는 준비 코드가 없다.

# test_operator

| 항목 | 값 |
|---|---|
| 조각 | `host` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_operator.py` (393행) |
| 클래스 / 테스트 | 2 / 22 |
| 시험 대상 제품 코드 | `do_math/scheduled_operator.py`의 `task_names`(행 107–110), `schedule`(행 113–163), `hold`, `release`, `run_engine`(행 247–285), `engine_start_guard`(행 298–332), `check`(행 375–431), `wake`, `reconcile_wake`, `supervision_block`, `LIVE_INSTALLATION_ROOT`; `do_math/cli.py`의 `build_parser`, `execute`(`init`, `configure`, `operator release`), `_emit`(행 586–592), `_schedule_failure`(행 262–272); `do_math/planning.py`의 `research_wake_reasons`, `collect_due_events`; 스크립트 `operator_bootstrap.py` |
| 사용하는 픽스처 모듈 | `research_fixtures.git_init` |
| 격리 표지 | 없음 |
| 시작 상태 | 대부분 네 단 밖의 직접 호출. `read_status`, `subprocess.run`, `schedule`, `ResearchRepository`, `ModelRunner`, `recovery` 등을 패치해 운영자의 판단만 본다. 두 시험은 `git_init`한 저장소에서 공개 `cli.execute('init')`를 도는 4단이고, 한 시험은 설치 사본을 실제 자식 프로세스로 실행한다. `WakeTests`의 두 시험은 순수 함수를 부르는 1단이다 |

## 목적

모듈 docstring은 "Windows 등록 없이 하는 일반 예약 운영자 경계 검사"라고 밝힌다. 예약 운영자(`scheduled_operator`)는 인스턴스마다 저장소 경로에 묶인 예약 작업(운영자, 엔진, 깨우기)을 두고, 모델을 부르지 않는 감독(`check`)으로 엔진 상태 한 장을 읽어 엔진을 깨울지, 복구를 열지, 기다릴지를 정한다(`check` docstring "Model-free supervision"). HOLD 표지는 로컬 표지일 뿐 연구 상태를 바꾸지 않고(`hold` docstring), 엔진 시작은 HOLD·일시정지·모델 정책·설치 수리 등 막는 요인이 없을 때만 한다(`engine_start_guard`). 이 모듈은 작업 이름, 예약 어댑터 인자, HOLD, 엔진 시작 조건, 관찰 모드(`probe`)의 무부작용, 엔진 import 실패의 보존과 복구 진입, 쓰기 잠금 경합의 비복구 처리, 설치 수리 시 감독자 즉시 요청, 초기화·구성 뒤 예약 등록 실패의 보고와 조정 명령, 깨우기 이유 계산의 읽기 전용성을 검사한다.

## 모듈 수준 요소

- `SCRIPTS` (행 16): 스킬의 `scripts/` 폴더. 행 17–18이 `sys.path`에 없을 때만 앞에 넣는다. 행 187의 시험이 `SCRIPTS.parent`(스킬 폴더)를 복사하는 기준으로도 쓴다.
- 행 20–24: `scheduled_operator`를 `operator`로, `cli`, `git_init`, `deepcopy`, `planning`을 import한다.
- `AT` (행 319): 시각 `2026-09-22T00:00:00+00:00`. `WakeTests`의 두 시험이 기한 시각으로 쓴다.
- 행 392–393: 직접 실행하면 `unittest.main(verbosity=2)`.

## OperatorTests (행 27–316)

`unittest.TestCase`를 그대로 상속하고 표지가 없다.

- `setUp` (행 28–35): 임시 폴더 아래 `repository`와 `workspace` 폴더를 만들고, 인스턴스 ID를 `RI-00000000000000000000000000`으로 둔다. 저장소는 Git 저장소가 아니다(필요한 시험만 `git_init`한다).
- `tearDown` (행 37–38): 임시 폴더를 정리한다.
- `_config(value)` (행 313–316): `value`를 `config.json`으로 쓰고 경로를 돌려준다. `init` 시험의 `--config-file`에 쓴다.

### `test_task_names_are_repository_scoped_and_stable` (행 40–47)
- 성질: 예약 작업 이름은 같은 저장소·인스턴스에 대해 늘 같고, 저장소가 다르면 달라진다.
- 준비: 1단. `setUp`의 경로.
- 실행: `task_names`를 같은 인자로 두 번, 다른 저장소로 한 번.
- 단언: 첫 두 결과가 같다. 다른 저장소의 `operator` 이름이 다르다. `operator` 이름에 `Operator`, `engine` 이름에 `Engine`이 들어 있다.
- 대역: 없음.

### `test_schedule_request_passes_only_generic_instance_coordinates` (행 49–65)
- 성질: 예약 등록 요청은 PowerShell 어댑터에 동작, 저장소, 작업 공간, 인스턴스 같은 일반 좌표만 넘기고 그 JSON 결과를 돌려준다.
- 준비: 받은 명령을 기록하고 `{"operator":"ready"}`를 돌려주는 `runner` 대역.
- 실행: `operator.schedule('install', ..., interval_seconds=7200, operator_timeout_seconds=5400, runner=runner)`.
- 단언: 결과의 `operator`가 `ready`다. 명령이 한 번 불렸고, 인자에 `install`, 저장소의 resolve 경로, 작업 공간의 resolve 경로, 인스턴스 ID가 있다.
- 대역: `runner` 주입.
- 비고: 이름의 "only"(그것만 넘김)는 단언하지 않는다. 시험은 좌표가 들어 있음만 확인한다.

### `test_hold_and_release_do_not_resume_or_edit_research_state` (행 67–73)
- 성질: HOLD와 해제는 작업 공간의 운영자 표지 파일만 다룬다.
- 준비: `setUp`의 작업 공간.
- 실행: `operator.hold(workspace, reason='user requested stop')`, `operator.release(workspace)`.
- 단언: HOLD 뒤 `operator/HOLD.json`이 있다. 해제 결과의 `released.id`가 HOLD의 `id`와 같고, `HOLD.json`이 없어지고 `operator/release.json`이 생겼다.
- 대역: 없음.
- 비고: 이름의 "재개하거나 연구 상태를 고치지 않음"은 저장소에 아무것도 없는 상태에서 호출이 성공한다는 점으로만 간접 확인된다.

### `test_engine_does_not_start_for_hold_or_any_pause` (행 75–97)
- 성질: 엔진은 막는 요인이 없을 때만 시작되고, HOLD나 사용자 일시정지가 있으면 자식 프로세스를 띄우지 않는다.
- 준비: 상태 `{"status": "ready", "user_pause": False}`.
- 실행: 아래 번호 단계에 적은 호출을 차례로 한다.
- 단언: 각 단계의 단언은 아래 번호 단계에 함께 적는다. 단계 목록:
  1. `read_status`가 `ready`, `waiting`을 차례로 돌려주고 `subprocess.run`이 성공하는 대역 아래 `run_engine`. 결과가 `completed`, `before`가 첫 상태, `after.status`가 `waiting`이다.
  2. `hold` 뒤 `run_engine`의 결과가 `held`이고 `subprocess.run`이 불리지 않았다.
  3. HOLD 파일을 지우고 `read_status`가 `{"status": "paused", "user_pause": True}`일 때 결과가 `paused`이고 자식 실행이 없다.
  4. 1단계에서 기록한 명령에 `run`이 있다.
- 대역: `operator.read_status`, `operator.subprocess.run` 패치.

### `test_probe_observes_without_starting_a_model_or_engine` (행 99–112)
- 성질: 관찰 모드의 감독은 상태를 보고하고 엔진 시작 가능성만 판단하며, 모델·예약·복구를 부르지 않는다.
- 준비: 상태 `{"status": "ready", "user_pause": None}`. `ResearchRepository`, `ModelRunner`, `schedule`, `recovery`를 패치한다.
- 실행: `operator.check(..., probe=True)`.
- 단언: 결과가 정확히 `{"outcome": "observed", "status": 상태, "model_called": False, "engine_start": {"outcome": "startable", "before": 상태}}`다. `ModelRunner`, `schedule`, `recovery`가 불리지 않았다.
- 대역: 다섯 패치.

### `test_automatic_and_user_pause_do_not_trigger_external_recovery` (행 114–127)
- 성질: 자동 일시정지든 사용자 일시정지든 감독은 복구나 모델이나 예약을 부르지 않고 일시정지를 보고한다.
- 준비: 두 `subTest(pause=...)`: `user_pause`가 `None`(자동)과 `{"reason": "user stop"}`(사용자). 상태의 `status`는 둘 다 `paused`.
- 실행: `operator.check(...)`(관찰 모드 아님).
- 단언: `outcome`이 `paused`이고 `ModelRunner`, `schedule`, `recovery`가 불리지 않았다.
- 대역: `read_status`, `ResearchRepository`, `ModelRunner`, `schedule`, `recovery` 패치.

### `test_engine_import_failure_is_preserved_before_recovery` (행 129–142)
- 성질: 엔진을 import조차 못 하면 실패를 파일로 보존한 뒤 복구에 넘기고, 관찰 모드에서는 보존만 하고 복구하지 않는다.
- 준비: `read_status`가 `SyntaxError('engine broken')`를 던지게 하고 `recovery`를 `{"outcome": "fixture-recovered"}`로 패치한다.
- 실행: `check(...)`, 이어 새 패치 아래 `check(..., probe=True)`.
- 단언: 첫 결과가 `fixture-recovered`다. 복구에 넘긴 `failure`의 `error_type`이 `SyntaxError`, `kind`가 `engine_unavailable`이고, `operator/engine-failure.json`의 내용이 그 `failure`와 같다. 관찰 모드 결과의 `outcome`이 `recovery_required`이고 복구가 불리지 않았다.
- 대역: `read_status`, `recovery` 패치.

### `test_engine_child_targets_live_installation_from_frozen_supervisor` (행 144–152)
- 성질: 동결된 감독자가 띄우는 엔진 자식은 현재 살아 있는 설치의 진입점을 가리킨다.
- 준비: `LIVE_INSTALLATION_ROOT`를 임시 경로 `live-installation`으로 패치(`create=True`)하고, `read_status`와 `subprocess.run`을 성공으로 패치한다.
- 실행: `run_engine`.
- 단언: 결과가 `completed`이고, 자식 명령의 둘째 인자가 `live/scripts/do_math.py`다.
- 대역: 세 패치.

### `test_contended_writer_lock_is_recorded_without_opening_recovery` (행 154–171)
- 성질: 엔진이 쓰기 잠금 경합(재시도 가능한 도구 오류)으로 끝나면 설치 실패가 아니라 `engine_busy`로 기록되고, 다음 감독은 복구를 열지 않고 엔진을 다시 요청한다.
- 준비: 종료 코드 5와 `error.kind='tool_error'`, `message='writer lock is busy'`, `retryable=True`를 담은 표준 출력.
- 실행: 아래 번호 단계에 적은 호출을 차례로 한다.
- 단언: 각 단계의 단언은 아래 번호 단계에 함께 적는다. 단계 목록:
  1. 그 결과를 돌려주는 `subprocess.run` 아래 `run_engine`. 결과와 `operator/latest-engine.json`의 `outcome`이 모두 `engine_busy`다.
  2. `read_status`(빈 제공자 대기 포함), `ResearchRepository`, `reconcile_wake`(`not_needed`), `schedule`(`engine.state='Ready'`), `recovery`를 패치하고 `check`. 결과가 `engine_requested`이고 복구가 불리지 않았다.
- 대역: 패치들.
- 비고: 제품 `_retryable_tool_error`(docstring "A busy writer lock or lost CAS is contention, not an installation failure")가 판정한다. `check`는 기록된 엔진 결과(`latest-engine.json`) 가운데 `outcome`이 `engine_failed`인 것에만 복구를 연다(행 413–419). 이와 별도로 상태 읽기 실패(행 382–391)와 설치 수리 대기(행 403–409)도 복구를 연다.

### `test_accepted_installation_repair_requests_supervisor_without_periodic_delay` (행 173–182)
- 성질: 엔진 실행 뒤 상태에 받아들여진 설치 수리가 있으면, 다음 정기 감독을 기다리지 않고 운영자 작업을 즉시 요청한다.
- 준비: `read_status`가 `ready`, 그다음 `installation_repair`가 있는 `waiting`을 돌려준다. `subprocess.run`은 성공, `schedule`은 `{'operator': {'state': 'Running'}}`.
- 실행: `run_engine`.
- 단언: `schedule`의 첫 위치 인자가 `start-operator`이고 결과에 `supervisor_request`가 있다.
- 대역: 세 패치.

### `test_real_probe_persists_failure_when_engine_has_syntax_error` (행 184–197)
- 성질: 실제 부트스트랩 진입점은 엔진 원문에 문법 오류가 있어도 시작되어, 관찰 모드에서 실패를 보고하고 보존한다.
- 준비: 스킬 폴더 전체를 `isolated-skill`로 복사하고(`__pycache__`, `*.pyc`, `.lake` 제외) `scripts/do_math/engine.py`를 `broken engine syntax !!!`로 덮어쓴다.
- 실행: `subprocess.run([sys.executable, isolated/scripts/operator_bootstrap.py, 'check', '--repository', ..., '--instance', ..., '--workspace', ..., '--probe'], timeout=30, creationflags=CREATE_NO_WINDOW)`.
- 단언: 종료 코드가 0이다(실패 시 stderr). 표준 출력 JSON의 `error_type`이 `SyntaxError`, `outcome`이 `recovery_required`이고, `operator/engine-failure.json`의 내용과 같다.
- 대역: 없음.
- 비고: 실제 자식 Python 프로세스와 스킬 폴더 전체 복사를 쓴다. 표지가 없다. 부트스트랩이 손상된 공유 모듈과 독립적으로 도는 성질은 `test_operator_bootstrap`이 더 자세히 본다.

### `test_init_keeps_created_instance_when_schedule_registration_fails` (행 199–212)
- 성질: 초기화가 인스턴스를 만든 뒤 예약 등록이 실패해도 만든 인스턴스는 남고, 결과는 실패와 조정 명령을 보고하며 종료 코드 5를 준다.
- 준비: 4단. `git_init(self.repository)`와 `scholarly_enabled=False` 설정 파일. `cli.build_parser().parse_args(('init', ...))`.
- 실행: `cli.scheduled_operator.schedule`을 `RuntimeError('scheduler unavailable')`로 패치하고 `cli.execute(arguments)`.
- 단언: 종료 코드가 5, 결과에 `instance_id`가 있고, `operator_schedule.status`가 `failed`이며, `reconcile`에 `operator install`, `--repository`, 저장소 경로가 들어 있다.
- 대역: `schedule` 패치.
- 비고: 공개 초기화를 실제 Git 저장소 위에서 돈다.

### `test_new_instance_installs_the_operator_every_two_hours_by_default` (행 214–225)
- 성질: 새 인스턴스는 기본으로 운영자를 두 시간(7200초) 간격으로 설치한다.
- 준비: 4단. 앞 시험과 같은 `init` 인자.
- 실행: `schedule`을 `{"operator": "ready"}`로 패치하고 `cli.execute`.
- 단언: 종료 코드 0, `schedule`의 위치 인자가 `("install",)`, `interval_seconds`가 7200, 결과의 `operator_schedule`이 `{"operator": "ready"}`다.
- 대역: `schedule` 패치.

### `test_cli_emits_byte_bearing_operator_receipt_as_json` (행 227–231)
- 성질: 바이트를 담은 운영자 영수증도 CLI는 JSON으로 내보내며 바이트는 base64로 싣는다.
- 준비: 1단.
- 실행: 표준 출력을 가로채고 `cli._emit({"raw": b"preserved bytes"}, command="operator check", request_id="QR-receipt")`.
- 단언: 출력 JSON의 `result.raw.base64`가 `cHJlc2VydmVkIGJ5dGVz`다.
- 대역: `redirect_stdout`.

### `test_release_submits_a_conditional_resume_even_before_hold_pause_is_applied` (행 233–244)
- 성질: 운영자 해제는 HOLD로 인한 일시정지가 아직 적용되지 않았어도 조건부 재개 제어를 제출한다.
- 준비: `operator release` 인자. `cli._operator_workspace`(작업 공간), `operator.release`(`{'released': {'id': 'pending-hold'}}`), `operator.read_status`(`user_pause=None`), `cli._control`(`{'effect': 'pending engine processing'}`)을 패치한다.
- 실행: `cli.execute(args)`.
- 단언: `_control`이 한 번 불렸고 `config`가 정확히 `{'expected_user_pause_reason': 'User requested scheduled operator HOLD pending-hold'}`다. `(종료 코드, result.resume.effect)`가 `(0, 'pending engine processing')`다.
- 대역: 네 패치.

### `test_completed_instance_is_observed_without_starting_an_operator_model` (행 246–255)
- 성질: 완료된 인스턴스는 운영자 모델을 시작하지 않고 완료로 관찰된다.
- 준비: 상태 `{"status": "completed", "user_pause": None, "snapshot": "finished"}`.
- 실행: `check(...)`.
- 단언: `outcome`이 `completed`, `status`가 그 상태와 같고, `ModelRunner`가 불리지 않았다.
- 대역: `read_status`, `ModelRunner`, `ResearchRepository` 패치.

### `test_saved_results_survive_schedule_process_start_errors` (행 257–284)
- 성질: `init`과 `configure`가 저장을 마친 뒤 예약 프로세스를 시작하지 못해도(`OSError`, `SubprocessError`) 저장 결과는 응답에 그대로 남고, 예약 실패가 따로 보고된다.
- 준비: `init`·`configure` × `OSError('scheduler executable unavailable')`·`subprocess.SubprocessError('scheduler process failed')`의 네 `subTest`. 명령별로 저장된 결과 사전(`init`: `instance_id`, `snapshot`, `status`; `configure`: `effect`, `request_id`, `snapshot`, `config`)을 둔다.
- 실행: `cli._require_git`, `cli.initialize`, `cli._control`, `cli._json_file`, `cli.ResearchRepository`를 패치하고 `cli._reconcile_operator`가 그 예외를 던지게 한 뒤 `cli.execute(args)`.
- 단언: 종료 코드 5, 결과의 저장 키들이 저장 결과와 같고, `operator_schedule.status`가 `failed`, `operator_schedule.error`가 예외 문자열이다.
- 대역: 여섯 패치.

### `test_schedule_reconcile_preserves_entrypoint_paths_and_disable_direction` (행 286–300)
- 성질: 예약 실패의 조정 명령은 PowerShell 따옴표 규칙으로 해석기·진입점·저장소·인스턴스 경로를 보존하고, 운영자가 꺼져 있으면 설치가 아니라 제거 방향을 적는다.
- 준비: 작은따옴표가 든 저장소 경로 `research owner's repository`. 두 `subTest(enabled=...)`.
- 실행: `cli._schedule_failure({'config': {'operator_enabled': enabled}}, RuntimeError('failed'), repository, instance)`.
- 단언: 명령이 `& '<sys.executable>' `로 시작하고, `do_math.py` 진입점의 따옴표 경로를 담으며, ` operator install `(켜짐) 또는 ` operator uninstall `(꺼짐)을 담고, `--repository '<resolve 경로>'`를 담으며, `--instance '<ID>'`로 끝난다. 종료 코드가 5다. 따옴표 함수는 작은따옴표를 두 개로 겹친다.
- 대역: 없음.

### `test_schedule_reconcile_uses_the_console_interpreter_when_run_windowless` (행 302–311)
- 성질: 창 없는 `pythonw.exe`로 돌 때도 조정 명령은 같은 폴더의 콘솔 `python.exe`를 쓴다.
- 준비: 빈 `python.exe`, `pythonw.exe`를 둔 임시 `Python` 폴더.
- 실행: `sys.executable`을 `pythonw.exe`로 패치하고 `cli._schedule_failure(...)`.
- 단언: `reconcile`이 `& '<임시 python.exe>' `로 시작한다.
- 대역: `sys.executable` 패치.

## WakeTests (행 322–389)

`unittest.TestCase`를 그대로 상속한다. 표지·훅·도우미가 없다.

### `test_supervisor_requests_once_and_probe_reports_the_same_reason` (행 323–344)
- 성질: 연구 재고 기한이 되어 기다리는 엔진에 대해, 관찰 모드는 같은 이유를 보고만 하고, 감독은 엔진을 한 번만 요청하며 이미 도는 엔진은 다시 요청하지 않는다.
- 준비: 상태 `{'status': 'waiting', 'research_wake_reasons': [{'kind': 'research_reconsider_due'}], 'operator_enabled': True, 'provider_waits': {'providers': {}}}`. `schedule` 대역은 `start-engine`이면 실행 중 표시를 켜고, 그 밖에는 엔진 상태를 `Running` 또는 `Ready`로 돌려준다. `reconcile_wake`는 `not_needed`.
- 실행: `check(..., probe=True)`, `check(...)` 두 번.
- 단언: 관찰 결과의 `engine_start.reason`이 `research reconsideration due`이고 `schedule`이 불리지 않았다. 첫 감독이 `engine_requested`, 둘째가 `engine_running`이다. `start-engine` 호출이 모두 합쳐 1번이다.
- 대역: `read_status`, `reconcile_wake`, `schedule` 패치.
- 비고: 주석(행 324)은 "감독은 이 엔진 상태 하나로 판단하며 저장소 상태를 적재하지 않는다"고 밝힌다. `ResearchRepository`를 패치하지 않아도 되는 이유다.

### `test_stopped_waiting_engine_wakes_on_due_research_without_mutating_state` (행 346–369)
- 성질: 멈춰 기다리는 엔진은 연구 재고 기한이 되면 깨울 이유를 얻되 그 계산은 상태를 바꾸지 않으며, 엔진 시작 판정은 모델 정책·사용자 일시정지·HOLD를 차례로 거부 사유로 보고한다.
- 준비: 1단. 활성 인스턴스와 `next_research_reconsider_at=AT`인 `waiting` 런타임, 그 사본.
- 실행: 아래 번호 단계에 적은 호출을 차례로 한다.
- 단언: 각 단계의 단언은 아래 번호 단계에 함께 적는다. 단계 목록:
  1. `research_wake_reasons(..., now='2026-09-21T00:00:00Z')`가 빈 목록이다.
  2. `now=AT`이면 첫 이유의 `kind`가 `research_reconsider_due`이고 런타임이 사본과 같다.
  3. 그 이유를 담은 상태로 `read_status`를 패치하고 `engine_start_guard`가 `startable`이다.
  4. `model_policy_violation`을 더하면 결과가 정확히 `{'outcome': 'model_policy_waiting', 'before': status}`다(주석 행 362: 모든 거부는 판단한 상태를 같은 키로 보고한다).
  5. 그것을 지우고 `user_pause`를 두면 `paused`다.
  6. `hold` 뒤 `held`다.
- 대역: `read_status` 패치.

### `test_regeneration_and_task_timers_are_read_only_and_not_duplicated` (행 371–389)
- 성질: 과제 재방문 기한과 반복 재생성 기한은 깨울 이유가 되되, 이미 사건으로 기록된 기한은 다시 이유가 되지 않고, 사용자를 막는 질문이 열려 있으면 이유가 없다.
- 준비: 1단. 과제 `TK-wait`의 선택 처분이 `AT`에 재방문하는 `not_selected`인 런타임.
- 실행: 아래 번호 단계에 적은 호출을 차례로 한다.
- 단언: 각 단계의 단언은 아래 번호 단계에 함께 적는다. 단계 목록:
  1. `collect_due_events(instance, runtime, AT)`로 기한 사건을 얻는다. `research_wake_reasons(now=AT)`의 첫 이유가 `task_revisit_due`다.
  2. 그 사건을 `runtime['events']`에 두면 이유가 빈 목록이다(중복 없음).
  3. 과제와 대기열을 비우고 `regenerate_after=AT`인 반복 이력을 두고 `do_math.revisions.repetition_hold`를 거짓으로 패치하면, 기한 전에는 빈 목록, `AT`에는 정확히 `[{'kind': 'research_regeneration_due'}]`다.
  4. 인스턴스 ID를 두고 사용자 소유의 막는 질문 `QU-user`(열림, 대상 `RI-wait`)를 더하면 `AT`에도 빈 목록이다.
- 대역: `repetition_hold` 패치.
- 비고: 이름의 "read-only"는 이 시험에서 단언하지 않는다(런타임 불변 단언은 앞 시험에 있다).

## 관계

- 같은 제품 기능을 다른 층에서 보는 모듈: `test_diagnosed_installation_recovery`는 `recovery` 자체를, `test_operator_bootstrap`은 부트스트랩의 동결 코드 검증을, `test_schedule_lifetime`과 `test_schedule_pythonw`는 실제 Windows 작업 스케줄러 등록을, `test_provider_wait`는 제공자 대기와 깨우기를, `test_cli`·`test_cli_advanced`(`lifecycle` 조각)는 CLI 일반 경로를, `test_supervisor_recovery`는 감독 복구 규칙을 본다.
- 픽스처 의존: `research_fixtures.git_init` 하나(`init` 두 시험).
- 이 모듈에만 있는 도우미: `OperatorTests._config`.
- 반복 기법: `read_status`를 패치해 엔진 상태 한 장을 주고 운영자의 판정만 본다. 모델·예약·복구가 불리지 않았음을 `assert_not_called`로 확인한다.
- 실제 외부 자원: 행 184의 시험만 실제 자식 Python을 띄운다. 행 199, 214의 시험은 실제 Git 저장소 위에서 공개 초기화를 돈다.

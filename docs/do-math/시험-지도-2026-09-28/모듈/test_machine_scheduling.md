# test_machine_scheduling

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_machine_scheduling.py` (99행) |
| 클래스 / 테스트 | 2 / 4 |
| 시험 대상 제품 코드 | `do_math/scheduler.py`의 `_plan_settle_waits`, `_dispatchable`, `_admissible`; `do_math/decision_engine.py`의 `_decision_references`(→ `planning.action_read_ids`); `do_math/session_slots.py`의 `SessionSlots.acquire`, `release`, `admission_check`; `do_math/execution_profiles.py`의 `with_host_resources`, `resolve_profile`, `profile_ref`; `do_math/parallel.py`의 `ModelCalls`; 스키마 `record_schemas.RECORDS['queue']` |
| 사용하는 픽스처 모듈 | `research_fixtures.bare_engine`; `provider_fixtures.host_capacity_fixture` |
| 격리 표지 | 없음 |
| 시작 상태 | 네 단 밖. 저장소를 적재하지 않은 `bare_engine` 위의 손으로 쓴 사전 상태(시험 1–3). 시험 4는 실제 스레드 하나를 쓰는 `ModelCalls`를 직접 부른다 |

## 목적

모듈 docstring은 "Host-capacity scheduling with real reservation arithmetic."이다. 이어서 범위를 밝힌다. 수명 주기와 입력 현행성의 술어는 명시적 전제로 고정하며(`create_autospec`으로 대체), 이 모듈은 권한이나 프로세스 종료를 검증한다고 주장하지 않는다. 곧 이 모듈은 스케줄러의 배정 가능성 판단(`ResearchEngine._dispatchable`, `do_math/scheduler.py` 218행 이하)이 호스트 용량을 실제 예약 산술(`SessionSlots._admission` → `budget.plan_reservations`)로 판정하되 준비 판단만으로는 아무것도 예약하지 않는다는 것을 본다. 계획 정착 대기의 저장 형태, 운영 검토의 결정 참조, 모델 호출 병렬 실행기의 콜백 전달도 함께 본다.

## 모듈 수준 요소

- 행 13: `sys.path.insert(0, str(Path(__file__).resolve().parents[1]))`로 `scripts/` 폴더를 경로 앞에 넣는 공통 머리다. `provider_fixtures`와 `research_fixtures`는 시험 폴더에서 import된다. 직접 실행하면 파이썬이 스크립트 폴더를 경로에 넣고, discover에서는 `-s scripts/tests`가 넣는다.
- 행 99: 직접 실행하면 `unittest.main()`을 부른다.

## MachineSchedulingTests (행 21–72)

`unittest.TestCase`를 그대로 상속한다. 표지, 클래스 속성, 설정 훅, 도우미가 없다. 각 테스트가 `bare_engine(instance, runtime)`으로 저장소 없는 엔진을 만든다. `bare_engine`은 `object.__new__(ResearchEngine)`에 `_init_process_state()`만 돌리고 상태를 붙이며, `store`를 주지 않으면 메모리 안의 `StateStore` 대역을 쓴다(`research_fixtures.py` 192–208행). 이 모듈의 테스트는 `_save`를 부르지 않는다.

### `test_plan_settle_action_survives_the_persisted_queue_contract` (행 22–30)
- 성질: 계획 정착 대기가 연구 계획 요청에 기록한 필드는 저장되는 큐 레코드 스키마를 통과한다.
- 준비: `instance = {'config': {'plan_settle_seconds': 300}}`, `runtime = {'queue': [{'role': 'task_contract_review'}]}`인 `bare_engine`. 요청 `action = {'id': new_id('AC'), 'role': 'research_plan'}`. `RECORDS`, `new_id`, `Draft202012Validator`는 테스트 안에서 늦게 import한다.
- 실행: `scheduler._plan_settle_waits(action)`, 이어서 `Draft202012Validator(RECORDS['queue']).validate(action)`.
- 단언: `_plan_settle_waits`가 `True`다. 큐에 계약 검토(`task_contract_review`)가 있고, 방금 정한 `settle_started_at`에서 300초가 지나지 않았기 때문이다. 대기가 붙은 요청이 큐 스키마 검증을 예외 없이 통과한다. `action['dispatch_wait']['since']`가 `action['settle_started_at']`과 같다.
- 대역: 없음. 시계는 실제 현재 시각을 쓴다(`governance.timestamp()`).
- 비고: 제품 docstring은 "Approvals arriving minutes apart are decided by one plan; a slow review delays it only up to the limit."이다. 이 시험은 대기의 시작만 보고, 한도 경과 뒤 대기가 풀리는 경로는 보지 않는다. `dispatch_wait`의 `kind`(`"plan_settle"`)와 `limit_seconds`는 스키마 통과로만 간접 확인된다.

### `test_operational_review_of_targetless_preparation_has_only_real_references` (행 32–38)
- 성질: 대상이 없는 준비 실행을 운영 검토할 때 결정 참조에는 실제로 있는 식별자만 들어간다.
- 준비: `runtime`에 과제는 없다. 실행 `EX-preparation`의 `action`은 `{'role': 'research_preparation'}`뿐이라 `target`이 없고, `decision_basis.records`에 `KN-basis` 하나가 있다. 인스턴스는 빈 사전이다.
- 실행: `engine._decision_references({'role': 'operational_review', 'target': 'EX-preparation'})`.
- 단언: 결과가 `['EX-preparation', 'KN-basis']`와 같다.
- 대역: 없음.
- 비고: `planning.action_read_ids`(100행 이하)는 운영 검토의 부모 실행에서 `decision_basis`의 레코드와 부모 행동의 `target`을 시드로 더한다. 이때 부모의 `target`이 `None`이면 더하지 않는다(108–110행). 이름의 "only real references"는 `None` 같은 가짜 참조가 목록에 섞이지 않는다는 뜻이다. 섞이면 결과가 달라지거나 `sorted`가 `None`과 문자열을 비교하다 실패한다.

### `test_blocked_machine_does_not_hide_a_smaller_ready_machine` (행 40–72)
- 성질: 호스트 용량이 모자라 대기하는 큰 기계 요청이 뒤에 있는 작은 기계 요청의 배정을 막지 않는다. 준비 판단은 예약도 실행도 만들지 않는다. 용량이 풀리면 큰 요청이 배정 가능해지고 대기 표시가 지워진다.
- 준비:
  - `host_capacity_fixture()`가 `(instance, selected, constraint)`를 준다. 호스트 제약의 한도는 jobs 4, 512 MiB, CPU 8000이고, 제어 예비분은 jobs 1, 128 MiB, CPU 2000이다. 따라서 실행에 빌려줄 수 있는 양은 jobs 3, 384 MiB, CPU 6000이다. `selected`의 `research_work`, `recovery`, `formal_check` 프로필은 각각 1 job, 128 MiB, CPU 2000을 요구한다.
  - `with_host_resources`로 두 프로필을 새로 만든다. `big`은 `formal_check`에 1 job, 384 MiB, CPU 6000을 요구한다. `small`은 원래의 `trust_check` 프로필에 1 job, 128 MiB, CPU 2000을 요구한다. 둘 다 인스턴스의 `execution_profiles`에 등록한다.
  - 빈 `runtime`(`tasks`, `executions`, `reservations`) 위의 `SessionSlots`로 `EX-held`(역할 `research_work`, 상태 `queued`)를 `selected['research_work']` 프로필에 `acquire`한다. 반환값 `True`를 단언한다. 이 예약이 1 job, 128 MiB, CPU 2000을 차지하므로 남는 양은 2 jobs, 256 MiB, CPU 4000이다.
  - 큐는 `AC-big`(`formal_check`, `big`의 `profile_ref`)과 `AC-small`(`trust_check`, `small`의 `profile_ref`)의 순서다.
- 실행: `choose`는 큐를 앞에서부터 보며 `scheduler._dispatchable(a)`가 참인 첫 요청을 고른다. 이것을 한 번 부르고, `slots.release('EX-held', reason='fixture: no process was created')` 뒤에 다시 부른다.
- 단언:
  - 첫 `choose()`는 `AC-small`을 고른다. `runtime`이 호출 전의 깊은 사본과 같다(실패 메시지 `'readiness must not reserve or create an execution'`). `AC-big`의 `dispatch_wait.kind`는 `'host_capacity'`다.
  - `release`가 `True`다.
  - 두 번째 `choose()`는 `AC-big`을 고른다. `AC-big`에 `dispatch_wait`가 더는 없다. `runtime`이 release 직후의 사본과 같다.
- 대역: `create_autospec`으로 엔진 인스턴스의 다섯 메서드를 바꾼다.
  - `_execution_profile`: 요청의 `profile_ref`로 `profiles.resolve_profile`을 부른다.
  - `_action_lifecycle_gate`: 수명 주기 판단 없이 `_execution_profile(action)`을 돌려준다.
  - `_revision_dispatch_waits`: `[]`.
  - `_selected_action_current`: `True`.
  - `_evaluation_context`: `{}`.

  모듈 docstring이 말하는 "explicit preconditions"가 이 대역들이다. 용량 판정(`_admissible` → `SessionSlots(observer=True).admission_check`)은 대역 없이 실제 산술로 돈다.
- 비고: 두 번째 배정에서 `big`의 요구 384 MiB와 CPU 6000은 가용량과 정확히 같다. 따라서 이 시험은 경계값에서 입장이 허용됨도 함께 고정한다. `formal_check`와 `trust_check`는 둘 다 `LEAN_ROLES`이지만, 살아 있는 실행 `EX-held`가 `research_work`이므로 `formal_execution` 대기(한 번에 Lean 실행 하나)는 걸리지 않는다. `release`가 참인 것은 발급된 티켓의 Job이 한 번도 만들어지지 않아 비어 있다고 확인되기 때문이다(`session_slots.py` 235행 이하, 증거 종류 `never_resumed`). 이 확인은 패치 없이 실제 Windows API를 부른다. `launch.termination_confirmed`가 `owner_ended`(`OpenProcess`)와 `named_job_empty`(`OpenJobObjectW`)를 쓴다. 입장 때 발급하는 티켓도 `windows_job.owner_identity()`로 현재 프로세스의 신원을 읽으며, Windows가 아니면 `WindowsJobUnsupportedError`를 던진다. 따라서 이 시험은 Windows 호스트를 전제한다. 이름이 말하는 "hide"는 큐의 순서상 앞선 대기 요청이 뒤 요청의 선택을 가리지 않는다는 뜻이다.

## ModelCallTests (행 75–96)

`unittest.TestCase`를 그대로 상속한다. 표지, 클래스 속성, 훅, 도우미가 없다.

### `test_parallel_call_carries_a_distinct_execution_id` (행 76–96)
- 성질: `ModelCalls`는 실행 ID를 단 호출을 별도 스레드에서 돌리면서, 러너의 `on_started` 콜백을 소유자 스레드의 `collect`로 전달하고, 끝난 호출의 결과를 그 호출을 낸 생성기에 되돌린다.
- 준비: 지역 클래스 `Runner`의 `run(**arguments)`는 `arguments["on_started"]({"pid": 7})`을 부르고 `{"status": "completed"}`를 반환한다. 생성기 `operation`은 `{"on_started": ...}`(받은 값을 `events`에 붙인다)를 내보낸 뒤, 되돌려 받은 결과를 `events`에 붙인다. `next(generator)`로 인자를 꺼낸다.
- 실행: `calls.start_call(generator, Runner().run, arguments, execution_id="EX-1")`. 이어서 `calls.collect()`가 참(끝난 호출 수 ≥ 1)이 될 때까지 폴링한다. 끝나면 `finally`에서 `calls.close()`.
- 단언: 폴링 중 10초 상한을 넘으면 `assertLess`가 실패한다. 실패 메시지에는 대기 중인 콜백 수(`calls.events.qsize()`)를 싣는다. 최종적으로 `events`가 `[{"pid": 7}, {"status": "completed"}]`와 같다. 곧 시작 콜백이 결과보다 먼저, 정확히 한 번씩 전달된다.
- 대역: 러너 대역(지역 클래스 `Runner`)과 생성기. 실제 스레드(`Thread(name="do-math-call")`)가 돈다.
- 비고: 이름은 "carries a distinct execution id"를 말하지만, 단언은 `execution_id`를 직접 보지 않고 콜백과 결과의 전달 순서만 확인한다. ID는 `start_call`의 입력 검증(비어 있지 않은 문자열, 같은 ID의 활성 호출 중복 거부, `parallel.py` 64–68행)을 지날 뿐이다. 폴링은 `time.sleep(.01)` 간격, 상한 10초다. 콜백은 러너 스레드에서 `Future`로 막혀 있다가 `collect` 끝의 `pump()`가 소유자 스레드에서 실행해야 풀리므로, 이 시험은 콜백 왕복이 교착 없이 끝남도 보증한다.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈:
  - `_dispatchable`은 `test_session_scheduler`, `test_engine`, `test_lifecycle_engine`, `test_repair_execution`, `test_design_walkthroughs`와 `state_fixtures`에도 나온다. 수명 주기와 현행성 술어를 실제로 돌리는 배정 판단은 그쪽 모듈이 맡는다.
  - 호스트 용량 산술 자체(`plan_reservations`의 예비분과 거부 메시지)는 `test_budget`이 순수 함수로 본다. 호스트 제약의 채택과 검증은 `test_host_resources`가 본다.
  - `ModelCalls`는 `test_machine_parallel`, `test_live_observation`, `test_stop_flags`, `test_repair_execution`과 `state_fixtures`에도 나온다. `test_machine_parallel`의 docstring은 "Owner-thread machine continuations, scheduler progress, and real Job barriers."로, 소유자 스레드의 기계 후속 처리를 실제 Job과 함께 본다.
  - `action_read_ids` 또는 `_decision_references`는 이 모듈 밖에서 `test_academic_preparation`, `test_repetition`, `test_task_contracts`에 나온다.
- 픽스처 의존: `host_capacity_fixture`의 소비자는 `test_formal_runtime`, `test_host_resources`, `test_machine_scheduling`, `test_session_scheduler`다(`consumers.json`). `bare_engine`은 30개가 넘는 모듈이 쓴다.
- 이 모듈에만 있는 도우미: 없다(지역 `Runner` 클래스와 `choose` 람다는 테스트 안에만 있다).

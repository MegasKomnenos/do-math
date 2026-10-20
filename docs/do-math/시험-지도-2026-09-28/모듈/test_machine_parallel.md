# test_machine_parallel

| 항목 | 값 |
|---|---|
| 조각 | `host` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_machine_parallel.py` (611행) |
| 클래스 / 테스트 | 3 / 22 (시험 클래스 2개와 엔진 대역 클래스 `Host` 1개. 시험은 `MachineSchedulerTests` 11개, `CallManagerTests` 11개) |
| 시험 대상 제품 코드 | `do_math/scheduler.py`의 `_run_parallel`(행 277 이하, 소유자 스레드 반복); `do_math/parallel.py`의 `ModelCalls`(`start_call`, `collect`, `judge`, `pump`, `wait`, `close`, `threads`, `futures`, `events`); 엔진의 `_formal`, `_resume_formal_waits`, `_end_machine_execution`, `_register_execution`, `_session_slots`, `_settle_activity`; `do_math/session_slots.SessionSlots.acquire`; `do_math/formal._job_run`; `do_math/windows_job.named_job_empty`; `do_math/git_store.GitStateStore`; 스크립트 `setup_lean.rerecord` |
| 사용하는 픽스처 모듈 | `engine_fixtures.FakeEngine`(그리고 그 `verification`=`formal_verification`, `knowledge`, `environment`, `control`); `research_fixtures.FixtureAdapter`, `await_stop`, `git_init`, 함수 안에서 `fixture_setup_lean`; `state_fixtures.owner_calls`; `test_categories.test_group` |
| 격리 표지 | `CallManagerTests`의 세 메서드에 `test_group('resource')`: `test_close_sets_every_stop_flag_and_fails_pending_start_callbacks`, `test_failed_start_publication_never_resumes_the_real_job`, `test_real_job_cancellation_uses_owner_judgment_and_collects_once`. 뒤의 둘에는 메서드 단위 `unittest.skipUnless(os.name == 'nt', 'Windows Job required')`도 붙는다. 클래스 표지 없음 |
| 시작 상태 | `MachineSchedulerTests`: 메모리 엔진 대역 `FakeEngine`을 상속한 `Host`를 `setUp`에서 활성화한 상태(2단에 가까운 합성 활성 상태를 테스트마다 새로 조립). 한 시험은 실제 Git 저장소를 붙인다. `CallManagerTests`: `ModelCalls`를 직접 부르는 스레드 수준 시험(1단에 준함)과 실제 Windows Job 두 시험 |

## 목적

모듈 docstring은 "소유자 스레드의 기계 연속(continuation), 스케줄러 진행, 실제 Job 장벽"이라고 밝힌다. do-math 엔진은 모든 상태 변경을 소유자 스레드 하나에서 하고, 모델 호출과 기계 계산(형식 검사, 신뢰 검사)은 `ModelCalls`가 관리하는 작업 스레드에서 돈다. 계산은 정지 깃발을 읽기만 하고, 깃발은 소유자가 게시된 상태를 보고 판단해 세운다(`scheduler.py` 주석 "Calculations only read stop flags"). 시작 콜백과 관찰은 소유자에게 대기열로 전달되고, 반환은 소유자가 수집해 연속을 재개한다. 이 모듈은 두 층을 본다. `MachineSchedulerTests`는 엔진 수준에서 긴 형식 검사가 AI 호출 수집을 막지 않는지, 일시정지·권한 철회 뒤 늦게 온 성공이 거부되는지, 환경 변경 시 재기록까지 기다리는지, 결과가 실제 Git 묶음에 게시되는지, 소유자 예외와 게시 실패에서 결과와 용량이 보존·정리되는지를 본다. `CallManagerTests`는 `ModelCalls` 자체의 스레드 수거, 정지 깃발 판단, 관찰 전달, 실제 Job 취소를 본다.

## 모듈 수준 요소

- 행 13: `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리.
- 행 14–22: `ResearchEngine`, `ModelCalls`, `transition_execution`, `ResearchRepository`, `new_id`, `knowledge_records`, `FakeEngine`, `FixtureAdapter`, `await_stop`, `git_init`, `owner_calls`, `test_group`을 import한다. `test_group`을 원래 이름으로 모듈에 두지만 unittest는 `TestCase` 하위 클래스만 모으므로 시험으로 수집되지 않는다.
- 행 610–611: 직접 실행하면 `unittest.main()`.

## Host (행 25–84)

`engine_fixtures.FakeEngine`(제품 `ResearchEngine` 위에 메모리 상태를 얹은 대역)을 상속한 엔진 대역이다. 시험 클래스가 아니다.

- 클래스 속성 `_execution_profile`(행 26): `FakeEngine`의 프로필 선택 대신 제품 `ResearchEngine._execution_profile`을 그대로 쓴다.
- `__init__(root)` (행 28–41): 현재 스레드를 `owner_thread`로 기억하고 `FakeEngine`을 초기화한 뒤 `activate()`로 활성화한다. 활성 신뢰 환경의 `configured_command`를 `config['lean_command']`로 두고 `build_profiles`로 기계 역할 프로필을 다시 지어 `execution_profiles`와 `role_profile_refs`에 더한다. `ai_finished` 이벤트, 가짜 시계값 `tick=0.`, 빈 `control_action`, `identity_reviews` 목록, 항상 `completed`를 돌려주는 `runner`를 둔다.
- `storage_double()` (행 43–46): `store`를 `ResearchRepository`의 `create_autospec` 대역으로 바꾸고, `load`가 마지막 저장본의 사본을 돌려주게 한다. 저장 실패 뒤의 "지속된" 상태를 읽기 위해 쓴다.
- `_save(artifacts=None)` (행 48–53): 소유자 스레드가 아니면 `AssertionError('engine mutation escaped the owner thread')`. 저장을 기록하고 헤드를 `fixture-head-<저장 수>`로 옮긴 뒤 `_evaluate_stops()`를 부른다(주석: 실제 게시 지점은 저장마다 정지를 판단한다).
- `_controls()` (행 55–58): `_calls`가 있으면 `pump()`하고 `control_action()`을 부른다. 시험이 소유자 반복의 제어 단계에 끼어드는 자리다.
- `_check_installation` (행 60, 항상 참), `_refresh_readiness` (행 61, 아무것도 안 함), `_settle_activity` (행 62, 아무것도 안 함), `_start_identity_review` (행 63, 지식 ID를 `identity_reviews`에 쌓음): 시험과 무관한 엔진 단계를 막는 대역.
- `_call_steps(action)` (행 65–77): AI 호출 경로의 대역. 주석(행 66–67)은 "모델 응답만 합성이다. 입장·수집·반환은 스케줄러의 실제 예약 구현을 쓴다"고 밝힌다. 제품 프로필로 실행을 등록하고 `_session_slots().acquire`를 단언한 뒤 `running`으로 전이하고, `yield {'execution_id': eid}`로 호출 결과를 받는다. 결과가 `completed`임을 단언하고 기계 실행 종료(`execution_incomplete`, `synthetic_AI_return`), 요청 제거, `ai_finished.set()`을 한다.
- `candidate(kid)` (행 79–84): `knowledge_records.create_candidate`로 `theorem fixture : 1 = 1 := rfl`을 담은 지식 후보를 만들고, 그 후보를 대상으로 하는 `formal_check` 요청을 돌려준다.

## MachineSchedulerTests (행 87–320)

`unittest.TestCase`를 그대로 상속하고 표지가 없다.

- `setUp` (행 88–94): 임시 폴더(`addCleanup`), `do_math.initialization.adapter_for`를 `FixtureAdapter()`로, `do_math.windows_job.named_job_empty`를 `True`로 패치하고(`enterContext`), `Host(임시 폴더)`를 만든 뒤 `do_math.scheduler.time.monotonic`을 `host.tick`을 읽는 함수로 패치한다(시계 주입).
- `run_case(*, trust=False, cancel=False, stops=None)` (행 96–150): 긴 기계 계산 하나와 AI 호출 하나를 함께 돌리는 시나리오 하네스.
  - 준비: `trust`이면 지식 `K1`과 새 신뢰 환경 `next`를 만들고 `trust` 제어(`transition`)로 생긴 `trust_check` 요청을 쓰고, 아니면 `candidate('K1')`의 `formal_check` 요청을 쓴다. 둘째 기계 요청 `candidate('K2')`를 더해 대기열을 `[기계 요청, maintenance AI 요청, 둘째 기계 요청]`으로 둔다.
  - 제어 대역 `control`: AI가 끝났고 검증기가 들어온 뒤 한 번만, 가짜 시계를 `100000.`초로 뛰게 하고, `cancel == 'revoke'`면 모든 허가를 `revoked`로, `cancel`이 참이면 런타임과 생애주기를 `paused`로 바꾼 뒤 `_save()`로 게시한다(주석: 제어는 게시되어야 효력이 있다).
  - 검증기 대역 `verify`: 들어오면 표시하고 `on_started`에 Job 이름을 넘긴다. 최대 500번(0.01초 간격) 정지 깃발을 읽으며 AI 완료를 기다린다. AI가 끝나면 제어 적용을 최대 5초 기다리고(`the owner loop did not apply the control`), 그 시점의 `should_stop()`을 `observed`에 기록한 뒤 늦은 성공(`host.verification(...)`)을 돌려준다(주석 행 130: 현재성이 판단하도록 일부러 늦은 성공을 돌려준다). AI가 끝나지 않으면 `AssertionError('AI completion was blocked by the formal verifier')`.
  - 실행: `host._run_parallel(max_steps=2)`.
  - 단언: `ai_finished`가 참. `observed == [stops]`(기본값은 `bool(cancel)`; 실패 시 저장된 `formal.json`·`trust-result.json` 산출물과 대기 행동을 보여 줌). 기계 실행(`formal_check`·`trust_check`)이 정확히 1개(`the second Lean request must stay unstarted`)이고 `ended`이며 `capacity.local_termination`이 `confirmed`. `maintenance` 실행의 `local_termination`도 `confirmed`. `stops`이면 기계 실행의 `outcome`이 `execution_incomplete`이고 신원 검토가 시작되지 않았다.
  - 반환: `host`.

### `test_formal_allows_ai_collection_after_long_elapsed_time` (행 152–153)
- 성질: 형식 검사가 오래(가짜 시계로 10만 초) 도는 동안에도 AI 호출은 수집되어 끝나고, 정지 사유가 없으면 검사의 늦은 성공이 정지되지 않는다.
- 준비: `setUp`의 `Host`. `run_case()` 기본값(형식 검사, 취소 없음).
- 실행: `run_case`의 `_run_parallel(max_steps=2)`.
- 단언: `run_case`의 공통 단언과 `observed == [False]`.
- 대역: `run_case`의 검증기·제어 대역, `setUp`의 패치.
- 비고: 스레드 대기 상한은 검증기의 500×0.01초 반복과 5초 제어 대기다.

### `test_environment_failure_waits_for_rerecord_before_compiler_retry` (행 155–195)
- 성질: 신뢰 도구 모음 파일의 메타데이터가 바뀌면 형식 검사는 컴파일러를 부르지 않고 신뢰 거버넌스의 재기록을 기다리며, 재기록 뒤에야 같은 요청이 계보를 이어 재개되어 결과가 받아들여지고, 결속 변경이 사건으로 남는다.
- 준비: `candidate('K-env')` 요청만 대기열에 둔다. 활성 신뢰 환경의 결속 사본을 떠 두고, 도구 모음 실행 파일 기준 `lib/lean/Init/Prelude.olean`의 수정 시각을 1초 늘린다(주석: 예를 들어 캐시 재다운로드). 검증기를 `Mock()`으로 둔다.
- 실행: 아래 번호 단계에 적은 호출을 차례로 한다.
- 단언: 각 단계의 단언은 아래 번호 단계에 함께 적는다. 단계 목록:
  1. `owner_calls(host)` 안에서 `host._formal(action)`. 검증기가 불리지 않았다. 대기 행동의 `kind`가 `formal_environment`, `next_owner`가 `trust_governance`다. 대기 실행 ID를 `previous`로 둔다.
  2. `_resume_formal_waits()`를 불러도 여전히 대기 중이다.
  3. `fixture_setup_lean(toolchain, smoke.lean)` 안에서 `setup_lean.rerecord(['unused'], 기록 폴더, 증거 폴더, None)`로 재기록한다.
  4. `_resume_formal_waits()` 뒤 대기열의 같은 ID 요청이 `continuation_of == previous`이고 대기 행동에서 빠졌다.
  5. 검증기를 합성 성공을 돌려주는 함수로 바꾸고 `owner_calls` 안에서 `_formal(successor)`. `continuation_of == previous`인 새 실행의 `outcome`이 `output_accepted`다.
  6. 런타임의 신뢰 결속이 재기록 결과의 결속과 같고, `trust_environment_rebound` 사건이 정확히 하나이며 `(previous, current)`가 `(옛 결속, 새 결속)`이다.
- 대역: `Mock` 검증기, 합성 검증기, `fixture_setup_lean`(호스트 관찰을 픽스처 도구 모음으로 바꾼 `setup_lean`), `owner_calls`.
- 비고: 도구 모음 파일은 `trust_fixture`가 만든 합성 파일이다. 실제 Lean은 쓰지 않는다. 함수 안에서 `os`, `setup_lean`, `Mock`을 import한다.

### `test_formal_user_stop_rejects_a_late_verified_result` (행 197–198)
- 성질: 형식 검사 중 사용자 일시정지가 게시되면 계산의 정지 깃발이 서고, 그 뒤 늦게 돌아온 검증 성공은 받아들여지지 않는다.
- 준비: `run_case(cancel=True)`.
- 실행: `run_case`.
- 단언: 공통 단언과 `observed == [True]`, 기계 실행 `outcome == 'execution_incomplete'`, 신원 검토 없음.
- 대역: `run_case`와 같다.

### `test_trust_check_allows_ai_collection_after_long_elapsed_time` (행 200–201)
- 성질: 신뢰 검사(`trust_check`)도 오래 도는 동안 AI 수집을 막지 않고, 정지 사유가 없으면 정지되지 않는다.
- 준비: `run_case(trust=True)`. 지식 `K1`과 신뢰 환경 전환 요청을 만든다.
- 실행: `run_case`.
- 단언: 공통 단언과 `observed == [False]`.
- 대역: `run_case`와 같다.

### `test_trust_check_user_stop_rejects_a_late_verified_result` (행 203–204)
- 성질: 신뢰 검사 중 사용자 일시정지가 게시되면 늦은 성공이 거부된다.
- 준비: `run_case(trust=True, cancel=True)`.
- 실행: `run_case`.
- 단언: 공통 단언과 `observed == [True]`, `outcome == 'execution_incomplete'`, 신원 검토 없음.
- 대역: `run_case`와 같다.

### `test_revoked_authority_rejects_both_kinds_of_formal_result` (행 206–207)
- 성질: 형식 검사 중 연구 허가가 철회되면 정지 깃발이 서고 늦은 결과가 거부된다.
- 준비: `run_case(cancel='revoke')`. 형식 검사 경우만 돈다.
- 실행: `run_case`.
- 단언: 공통 단언과 `observed == [True]`, `outcome == 'execution_incomplete'`, 신원 검토 없음.
- 대역: `run_case`와 같다.
- 비고: 이름은 "두 종류의 형식 결과"를 말하지만 이 시험은 `formal_check` 한 종류만 돌린다. 신뢰 검사 쪽 철회는 다음 시험이 반대 결론(정지하지 않음)으로 다룬다.

### `test_revoking_research_grants_does_not_stop_a_trust_check` (행 209–211)
- 성질: 연구 허가를 철회해도 신뢰 검사는 멈추지 않는다. 신뢰 검사의 권한은 허가가 아니라 승인된 전환이기 때문이다.
- 준비: `run_case(trust=True, cancel='revoke', stops=False)`.
- 실행: `run_case`.
- 단언: 공통 단언과 `observed == [False]`.
- 대역: `run_case`와 같다.
- 비고: 주석(행 210)은 "디스패치는 신뢰 검사를 허가 없이 입장시키며, 승인된 전환이 그 권한이다"라고 밝힌다.

### `test_machine_artifacts_publish_to_real_immutable_git_bundles` (행 213–240)
- 성질: 형식 검사와 신뢰 검사의 원 결과와 판정 결과는 실제 Git에 서로 다른 불변 묶음으로 게시된다.
- 준비: 두 `subTest(trust=...)`. 각각 새 `Host`를 만들고 `git_init`한 저장소에 `GitStateStore`를 열어 빈 상태를 첫 게시한다. `host._save`를 `create_autospec` 대역으로 감싸, 산출물이 있으면 실제로 `store.publish`하고 원래 `_save`를 부른 뒤 인스턴스와 런타임을 깊은 복사로 바꾼다(주석: `ResearchRepository.save_with_state`는 새로 정규화한 뿌리를 돌려준다).
- 실행: `run_case(trust=trust)`.
- 단언: 기계 실행의 `raw_result_ref`와 `result_ref`의 셋째 경로 조각(묶음 ID)이 다르다. 두 참조를 헤드에서 읽은 바이트에 `verified`가 들어 있다. `outcome`이 `output_accepted`다.
- 대역: `_save` 감싸기(실제 Git 게시 추가). 그 밖은 `run_case`와 같다.
- 비고: 실제 Git 자식 프로세스를 쓴다. 함수 안의 `import subprocess`는 쓰이지 않는다.

### `test_stop_request_reaches_the_calculation_within_one_owner_pass` (행 242–269)
- 성질: 일시정지의 게시 자체가 계산의 정지 깃발을 세우고, 계산은 소유자 반복 한 바퀴 안에 그 정지를 본다.
- 준비: `candidate('K1')` 요청 하나. 제어 대역은 바퀴 수를 세고, 계산이 시작된 뒤 처음 한 번 일시정지를 게시하며 그 바퀴 번호와 게시 직후의 깃발 값을 기록한다. 검증기 대역은 시작을 알리고 `await_stop(should_stop, timeout=30)`으로 정지를 기다린 뒤(못 보면 `AssertionError('the stop never reached the calculation')`) 그때의 바퀴 번호를 기록하고 `stopped`를 돌려준다.
- 실행: `_run_parallel(max_steps=1)`.
- 단언: 게시 직후 깃발이 참이다(`the publication itself sets the flag`). 관찰 바퀴 − 게시 바퀴 ≤ 1(`the calculation stops within one owner pass`). 형식 실행의 `result_disposition.stop_reasons`가 `['instance_paused']`다.
- 대역: 제어·검증기 대역, `setUp`의 패치.
- 비고: 폴링 상한은 `await_stop`의 30초다.

### `test_owner_exception_stops_worker_preserves_result_and_reconciles_capacity` (행 271–301)
- 성질: 소유자 반복이 예외로 끝나도 작업자 계산은 정지되고, 그 결과 증거가 보존되며, 실행은 종료되고 용량은 종료 확인과 함께 정리되고, 요청은 실행 실패 대기와 운영 검토로 넘어간다.
- 준비: `candidate('K1')` 요청, `storage_double()`, `_settle_activity`를 제품 `ResearchEngine._settle_activity`로 되돌린다. 검증기는 시작을 알리고 정지를 기다린 뒤 `stdout=b'preserved evidence\xff'`, `usage={'cost_usd': 0.25}`인 `stopped` 결과를 돌려준다. 제어 대역은 어떤 실행에 `capacity.process`가 생기면 `RuntimeError('injected owner failure')`를 던진다.
- 실행: `_run_parallel(max_steps=1)`.
- 단언: `RuntimeError`(`injected owner failure`)가 올라온다. 형식 실행이 `ended`이고 `local_termination`이 `confirmed`이며 신원 검토가 없다. 마지막 저장 산출물 `result_ref`의 JSON에서 `stdout.base64`를 풀면 원래 바이트이고, `usage.cost_usd`가 `{'reported_decimal': '0.25'}`다(소수를 정수 전용 상태에 반올림하지 않음). 대기 행동의 `kind`가 `execution_failure`이고, 그 요청은 대기열에 없으며, 그 실행을 대상으로 하는 `operational_review` 요청이 대기열에 있다. 소유 활동의 `status`가 `waiting`이다.
- 대역: `storage_double`, 제어·검증기 대역.

### `test_publication_failure_keeps_local_result_and_durable_unsettled_record` (행 303–320)
- 성질: 결과 게시가 실패하면 지속 상태에는 끝나지 않고 종료 확인도 없는 실행 기록이 남고, 반환된 결과는 로컬 복구 파일로 보존된다.
- 준비: `candidate('K1')` 요청, `storage_double()`, `failed` 결과를 즉시 돌려주는 검증기. `_save`를 감싸 산출물이 있는 저장에서 `OSError('injected result storage failure')`를 던진다.
- 실행: `_run_parallel(max_steps=1)`.
- 단언: `OSError`(정규식 `result storage failure`)가 올라온다. `store.load()`로 읽은 지속 상태의 형식 실행이 `ended`가 아니고 `local_termination`이 `confirmed`가 아니다. 작업 공간의 `execution-recovery/<실행 ID>/returned-result.json`에 `retained compiler evidence`가 있다.
- 대역: `storage_double`, `_save` 감싸기, 검증기 람다.

## CallManagerTests (행 323–607)

`unittest.TestCase`를 그대로 상속한다. 클래스 표지·훅·도우미가 없다. 각 시험이 `ModelCalls()`를 직접 만들고 끝에 `close()`한다. 연속은 한 번 `yield`해 결과를 받는 생성기이며, `next()`로 준비한 뒤 `start_call(generator, 함수, 인자, execution_id=...)`에 넘긴다.

### `test_collection_releases_finished_threads_but_retains_a_live_call` (행 324–361)
- 성질: 수집은 끝난 호출의 스레드와 미래(future)를 풀어 주고 살아 있는 호출은 남기며, 닫으면 남은 호출도 수집된다.
- 준비: 이벤트를 기다리는 살아 있는 호출 `EX-live` 하나.
- 실행: 16번 반복해 값을 바로 돌려주는 호출을 시작하고, 결과(5초 상한)와 스레드 종료를 기다린 뒤 `collect()`한다. 끝으로 이벤트를 풀고 `close()`, `collect()`를 두 번.
- 단언: 매 반복에서 미래의 결과가 그 번호이고, 스레드가 끝났으며, `collect()`가 1이고, `threads`가 살아 있는 스레드 하나뿐이고 `futures`가 1개다. 연속이 받은 값이 0–15다. 닫은 뒤 첫 `collect()`가 1, 둘째가 0이고, 받은 값 끝에 `released`가 붙으며, `threads`와 `futures`가 비었다.
- 대역: 없음.

### `test_admission_transition_preserves_native_utc_precision` (행 363–381)
- 성질: 입장 전이의 시각은 네이티브 UTC 마이크로초 정밀도를 그대로 유지한다.
- 준비: 1단. `2026-09-23T00:00:00.997259+00:00` 시각을 돌려주는 `datetime` 하위 클래스 `Clock`. `DEFAULT_CONFIG` 프로필의 `formal_check` 실행 `EX-precision`.
- 실행: `patch('datetime.datetime', Clock)`과 `do_math.session_slots.time.time`을 그 시각보다 1마이크로초 앞선 값으로 패치하고 `SessionSlots(runtime, instance).acquire(...)`.
- 단언: 입장이 참이고, 실행의 마지막 전이 `at`이 `instant.isoformat()`과 같다.
- 대역: `datetime.datetime`, `session_slots.time.time` 패치(시계 주입).
- 비고: `time.time()`으로 다시 계산했다면 1마이크로초 어긋났을 값을 거부하는 구성이다.

### `test_close_sets_every_stop_flag_and_fails_pending_start_callbacks` (행 384–406)
- 성질: 닫기는 모든 호출의 정지 깃발을 세우고, 소유자의 답을 기다리던 시작 콜백은 실패로 끝낸다.
- 준비: 정지 깃발을 기다리는 호출 `EX-one`(계산 측 `should_stop`은 늘 거짓인 인자를 받지만 `ModelCalls`가 깃발로 감싼다)과, `on_started({})`를 부르는 호출 `EX-two`(시험의 `on_started`는 불리면 `self.fail('must not run')`).
- 실행: 최대 3초 동안 `events.qsize()`가 1이 될 때까지 폴링하고 `close()`, `collect()` 두 번.
- 단언: 사건 대기열 크기가 1이다(`only the start callback waits for the owner`). `collect()`가 2, 이어서 0이다. 연속이 받은 값에 `{'stopped': True}`가 있고 `status == 'failed'`인 결과가 있다. 살아 있는 스레드가 없다.
- 대역: 없음.
- 비고: 메서드 표지 `test_group('resource')`. 실제 프로세스는 쓰지 않고 스레드 수명만 다룬다.

### `test_owner_wait_wakes_on_a_returned_call_not_its_bound` (행 408–423)
- 성질: 소유자의 대기는 호출이 돌아오면 상한 전에 깨고, 기다릴 호출이 없으면 상한만큼 쉰다.
- 준비: 이벤트를 최대 5초 기다리는 호출 `EX-wake`.
- 실행: `wait(0)`, 이벤트 해제, `wait(30)`의 소요 시간 측정, `collect()`, `wait(.2)`의 소요 시간 측정.
- 단언: `wait(30)`이 5초 안에 끝난다(`a returned call wakes the owner`). `wait(.2)`가 0.15초 이상 걸린다(`nothing pending: the bound paces the owner`).
- 대역: 없음.

### `test_stop_flag_reads_never_wait_for_the_owner` (행 425–443)
- 성질: 계산의 정지 깃발 읽기는 소유자를 기다리지 않으며, 판단 함수는 시작할 때 소유자 쪽에서 한 번만 돈다.
- 준비: 판단 함수는 `judged`에 `'judged'`를 더하고 거짓을 돌려준다. 계산은 `should_stop()`을 1000번 읽고 결과와 걸린 시간을 돌려준다. 소유자는 그동안 `pump`하지 않는다(주석 행 436).
- 실행: `start_call`, 미래의 결과(5초 상한).
- 단언: `stopped`가 거짓, 걸린 시간이 1초 미만, `judged == ['judged']`(메시지 `the judgment runs on the owner, once at start`).
- 대역: 없음.

### `test_owner_judgment_sets_the_flag_once_and_stops_the_calculation` (행 445–471)
- 성질: 소유자의 판단이 정지 사유를 보면 깃발을 한 번 세워 계산을 멈추고, 세워진 깃발은 다시 판단하지 않는다.
- 준비: 판단 함수는 소유자 스레드에서 도는지 단언하고, `reasons`가 비었는지를 기록·반환한다. 계산은 깃발을 기다린다.
- 실행: `start_call`(시작 시 판단 1회), `judge()`, 사유 `paused` 추가, `judge()` 두 번, 최대 5초 동안 `collect()` 반복.
- 단언: 첫 `judge()` 뒤 `future.stop`이 서지 않았다. 연속이 `{'status': 'stopped'}`를 받았다. 판단 기록이 `[False, False, True]`다(시작, 첫 `judge`, 사유 뒤 `judge`; 셋째 `judge`는 판단하지 않음).
- 대역: 없음.

### `test_failed_judgment_fails_only_its_own_call` (행 473–497)
- 성질: 정지 판단이 예외를 내면 소유자는 예외를 올리지 않고 그 호출만 실패로 끝내며, 계산이 돌려준 증거는 남는다.
- 준비: 판단 함수는 `state['fail']`이 참이면 `KeyError('missing record')`를 던진다. 계산은 깃발을 기다렸다가 `{'status': 'stopped', 'evidence': 'kept'}`를 돌려준다.
- 실행: `start_call`, `state['fail'] = True`, `judge()`, 최대 5초 동안 `collect()` 반복.
- 단언: 연속이 받은 결과의 `status`가 `failed`, `evidence`가 `kept`, `error`에 `stop judgment failed: KeyError`가 있다.
- 대역: 없음.

### `test_observations_queue_without_waiting_and_apply_before_collection` (행 499–533)
- 성질: 계산의 관찰은 소유자 왕복 없이 대기열에 쌓이고, 소유자가 수집할 때 결과보다 먼저 적용되며, 적용에 실패한 관찰은 그 호출의 오류 콜백으로 보고된다.
- 준비: `ModelCalls(on_observation_error=...)`. 관찰 적용 함수는 `'bad'`에 `ValueError('unapplied observation')`를 던진다.
- 실행: 관찰 `one`, `two`를 내고 끝나는 호출. 결과를 기다린 뒤 `collect()`. 이어 `'bad'`를 내고 깃발을 기다리는 둘째 호출을 시작하고 최대 5초 동안 `collect()` 반복.
- 단언: 첫 결과 직후 적용 목록이 비었다(`nothing is applied until the owner pumps`). `collect()`가 1이고 순서가 `applied one`, `applied two`, `collected {'status': 'completed'}`다. 오류 콜백 기록이 `[('EX-failed-observation', 'unapplied observation')]`이고, 마지막 순서 항목이 `collected {'status': 'stopped'}`다.
- 대역: 없음.
- 비고: 둘째 호출이 정지로 끝난다는 것은 관찰 적용 실패가 그 호출의 정지 깃발을 세운다는 뜻이다(시험은 결과만 단언한다).

### `test_one_pump_applies_only_the_rows_queued_before_it` (행 535–564)
- 성질: 한 번의 `pump`는 그 시점까지 쌓인 관찰만 적용한다. 적용 중에 새로 생긴 관찰은 다음 바퀴로 미룬다.
- 준비: 계산은 관찰 0, 1을 내고 이벤트를 기다린다. 적용 함수는 해제 전이고 값이 50 미만이면 적용하면서 `값+2`를 새로 낸다.
- 실행: 관찰 2개가 쌓일 때까지 최대 5초 폴링, `pump()`, 이벤트 해제, 결과 대기, `collect()`.
- 단언: 첫 `pump` 뒤 적용 목록이 `[0, 1]`이고 미래의 남은 관찰 인자가 `[(2,), (3,)]`이다. `collect()`가 1이고 최종 적용 목록이 `[0, 1, 2, 3, ('collected', {'status': 'completed'})]`다.
- 대역: 없음.
- 비고: 주석(행 536–537)은 "적용보다 빨리 만들어 내는 호출이 소유자를 한 `pump` 안에 붙잡아 디스패치·검토·제어를 막아서는 안 된다"고 밝힌다.

### `test_failed_start_publication_never_resumes_the_real_job` (행 568–578)
- 성질: 시작 신원의 게시가 실패하면 실제 Job의 루트는 재개되지 않는다.
- 준비: 표지 파일 `must-not-run`을 만드는 Python 명령. `on_started`는 표지 파일이 없음을 단언하고 `OSError('simulated publication failure')`를 던진다.
- 실행: `formal._job_run(command, root, on_started=reject)`.
- 단언: `OSError`(정규식 `publication`)가 올라오고, 끝난 뒤에도 표지 파일이 없다.
- 대역: 없음.
- 비고: 메서드 표지 `test_group('resource')`와 `unittest.skipUnless(os.name == 'nt', 'Windows Job required')`. 실제 Windows Job(일시정지 루트)을 쓴다.

### `test_real_job_cancellation_uses_owner_judgment_and_collects_once` (행 582–607)
- 성질: 실제 Job을 `ModelCalls`로 돌릴 때 시작 콜백은 소유자 스레드에서 돌고, 소유자 판단으로 정지되면 Job이 비워지며 결과는 한 번만 수집된다.
- 준비: 30초 자는 Python 명령. `on_started`는 소유자 스레드임을 단언하고 신원을 기록한다. `should_stop`은 시작 기록이 있으면 참이다.
- 실행: `start_call(generator, _job_run, {...}, execution_id='EX-real')`. 최대 15초 동안 `collect()`, `judge()`를 반복한다.
- 단언: 미래가 모두 수집되었다. 연속이 받은 결과가 하나이고 그 마지막 원소(`stopped`)가 참이다. `named_job_empty(시작 신원의 job_name)`이 참이다. 이후 `collect()`가 0이다.
- 대역: 없음.
- 비고: 메서드 표지 `test_group('resource')`와 `unittest.skipUnless(os.name == 'nt', 'Windows Job required')`. 실제 Windows Job, 작업자, Python 자식 프로세스를 쓴다.

## 관계

- 같은 제품 기능을 다른 층에서 보는 모듈: `test_session_scheduler`(`research` 조각)는 배정 규칙을, `test_machine_scheduling`(`foundation`)은 기계 역할의 입장 규칙을, `test_stop_flags`(`lifecycle`)는 정지 깃발 판단을, `test_formal`·`test_formal_runtime`은 `_job_run`을, `test_host_resources`는 호스트 예약을, `test_trust_continuation`은 신뢰 결속의 재기록을 본다.
- 픽스처 의존: `engine_fixtures.FakeEngine`이 `Host`의 바탕이다. `research_fixtures`의 `FixtureAdapter`(능력 관찰 대역), `await_stop`, `git_init`, `fixture_setup_lean`; `state_fixtures.owner_calls`.
- 이 모듈에만 있는 도우미: 엔진 대역 `Host`와 시나리오 하네스 `run_case`.
- 겹침과 보완: 형식·신뢰 검사 × 취소 없음·일시정지·철회의 여섯 조합을 `run_case`를 쓰는 여섯 시험(행 152, 197, 200, 203, 206, 209)이 나눠 본다. 그 가운데 늦은 성공을 거부하는 것은 세 시험(행 197, 203, 206)이고, 신뢰 검사의 허가 철회(행 209)는 정지하지 않는 쪽을 고정한다. 실제 Job 취소는 `ModelCalls` 수준(행 582)과 `_job_run` 수준(`test_formal`의 행 132)에서 따로 확인된다.
- 격리 표지: 실제 Job을 쓰는 두 시험과 스레드 수명을 다루는 한 시험에 `resource`가 있다. 실제 Git 게시 시험(행 213)과 나머지 스레드 시험에는 표지가 없다.

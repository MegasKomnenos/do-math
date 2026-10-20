# test_session_scheduler

| 항목 | 값 |
|---|---|
| 조각 | `research` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_session_scheduler.py` (953행) |
| 클래스 / 테스트 | 13 / 41 (시험 없는 러너 대역 `ConcurrentRunner` 포함) |
| 시험 대상 제품 코드 | `do_math/session_slots.py`의 `SessionSlots`(`acquire`, `release`, `snapshot`, `started`, `admission_wait`); `do_math/model_policy.py`의 `MODELS`, `LIMITS`, `assessment_tier`, `selection`, `validate_policy`; `do_math/configuration.py`의 `DEFAULT_CONFIG`, `validate_config`; `do_math/execution_profiles.py`의 `build_profiles`, `apply_editions`, `capability_evidence`, `WORK_ROLES`; `do_math/scheduler.py`의 `_scan_due`, `_publish_observation`, `_dispatchable`, `_select_model`, `_local_call_returned`, `OWNER_RESCAN_SECONDS`; `do_math/engine.py`의 `run`, `check`, `_register_execution`, `_machine_started`, `_enqueue`; `do_math/lifecycle_engine.py`의 `_refresh_readiness`; `do_math/planning_engine.py`의 `_apply_queue_plan`; `do_math/provider_engine.py`의 `_provider_admit`, `_session_slots`; `do_math/execution_lifecycle.py`의 `release_or_hold`; `do_math/scheduled_operator.py`의 `check`, `recovery`; `do_math/repository.py`의 `writer_lock`; `do_math/windows_job.py`의 `WindowsJob`, `named_job_empty`; 공개 `initialize`, `control` |
| 사용하는 픽스처 모듈 | `purpose_fixtures`(`ActivatedPurposeHarness`); `research_fixtures`(`restore_template`, `candidate`, `contract_review`, `current_state`, `git_init`, `install_adapter_fixture`, `local_job_runner`, `observation_batch`, `producer_result`, `send_control`, `FixtureAdapter`, `activated_instance`); `runner_fixtures`(`ScriptedRunner`, `common`, `context_from`); `state_fixtures`(`start_active_copy`, `active_instance`, `ACTIVE_LEAN_COMMAND`); `engine_fixtures`(`initialized_instance`, `reassessment_engine`, `routing_engine`, `FakeEngine`); `provider_fixtures`(`host_capacity_fixture`) |
| 격리 표지 | 없음(`test_group` 없음). `test_slot_waits_for_actual_named_job_termination`에 `skipUnless(os.name == 'nt')` |
| 시작 상태 | 1단 순수 함수(`SessionPolicyTests`). 2단(`OwnerRescanTests`, `PlanAfterPreparationTests`, `DuplicateContractReviewTests`, `PlanSettleTests`, `RunWithoutDeadlineTests`, `ResearchAdmissionTests`, `MaintenanceFenceRunTests`). 모듈 빌드 `ready_work`는 기본은 2단 위, `public=True`면 3단 위에 쌓는다(`ParallelEngineTests`). 공개 `initialize`만 복원한 템플릿(`SlotTests`). 메모리 엔진 대역 `FakeEngine`·`reassessment_engine`·`routing_engine`(`SchedulingResponsibilityTests`, `MachineAdmissionConnections`) |

## 목적

모듈 docstring(행 1)은 스케줄링을 시험한다고 밝힌다. 대상은 세션 슬롯과 공급자 입장, 계획이 열리거나 기다리는 때, 호출 제한 시간, 기계 예약이다. 이 모듈이 지키는 계약은 크게 여섯이다.

1. 모델 작업은 모델별 세션 한도가 정한 슬롯을 차지하고, 운영 역할은 슬롯을 차지하지 않는다.
2. 슬롯의 입장·해제는 Git 쓰기 잠금을 가진 소유자만 하고, 관찰자는 읽기만 한다.
3. 모델 등급은 난도와 중요도 중 큰 쪽으로 정하고, 역할 하한과 평가 없음(high)의 규칙을 따른다.
4. 계획은 결정할 것이 있을 때만 열리고, 가까운 계약 검토 승인들을 한 번의 결정에 모으려고 정해진 시간만큼 기다린다(plan settle).
5. 작업 역할 호출에는 시간 상한이 없고, 비작업 역할 호출에는 프로필의 상한 이하가 걸린다.
6. 기계 역할(`formal_check`)은 호스트 예약을 시작 전에 잡고, 종료가 불확실하면 용량을 붙든다.

`시험-지침.md` 4절 규칙 9는 `do_math/scheduler.py`의 배정 규칙 시험을 이 모듈에 둔다고 예로 든다.

## 모듈 수준 요소

- 행 17: `scripts/`를 `sys.path` 앞에 넣는 공통 머리.
- `ready_work(root, shared, *, count, public, config)` (행 34–82): `restore_template` 빌드. docstring은 이것을 "실제 계획이 선택해 작업을 큐에 넣은 준비 완료 과제 `count`개"라고 부른다.
  - 기본(`public=False`)은 `active_instance`(`lean_command=ACTIVE_LEAN_COMMAND`)에서 실제 준비를 돈다. 계약 승인은 `seal_contract_review`로 봉인한다.
  - `public=True`면 `activated_instance`(`goal='bounded research'`, `lean_command=['test-lean']`)에서 준비 뒤 실제 검토를 `run(max_steps=count)`로 돈다. docstring은 공개 활성화를 유지하는 이유를 적는다. 합성 초기화 실행에 대한 `check()`는 역할 입력을 검사하지 않았다고 보고하고, 활성화는 큐 사건을 남긴다. 그 결과에 의존하는 시험은 공개 상태가 필요하다.
  - 두 경우 모두 기본 설정에 `operator_enabled=False`, `scholarly_enabled=False`를 둔다.
  - `count=0`이면 활성화가 남긴 큐 그대로 인스턴스 ID를 돌려준다.
  - `count`가 양수면 러너는 `ScriptedRunner(preparation_candidates=[candidate('0'), ...], model_rating=high/medium)`이다. 과제 수와 모든 과제의 `ready`를 확인하고, 큐의 `task_contract_review`를 지운 뒤 `run(max_steps=1)`로 실제 계획을 돈다. 끝에서 큐가 정확히 과제마다 `research_work` 하나인지, `pending_events == []`인지 확인한다. 아니면 `AssertionError`를 낸다.
  - `FixtureAdapter` 패치 아래서 돈다. `ParallelEngineTests.engine`이 쓴다.
- 행 952–953: 직접 실행하면 `unittest.main(verbosity=2)`.

`research_fixtures` docstring의 "What to use"는 `ready_work`를 이 모듈 전용 빌드로 적는다.

## ConcurrentRunner (행 85–124)

- 종류: 시험이 없는 러너 대역 클래스. 기반 클래스 없음.
- `__init__(expected=3, release=None)` (행 86–95): 기대 동시 호출 수, 해제 이벤트, 잠금, 현재·최대 동시 수(`active`, `peak`), 받은 모델 목록, 작업공간 목록, 시작 조건 변수 `started`와 `started_count`를 둔다.
- `run(...)` (행 98–124): `local_job_runner`로 감싸 호출마다 실제 Windows Job 자식을 띄운다. 들어오면 `active`를 올리고 `peak`, 모델, 작업공간을 기록한다. `active == expected`가 되면 해제 이벤트를 켠다. `on_started()` 뒤 `started_count`를 올리고 알린다. 해제될 때까지 0.01초 간격으로 기다리는데, `should_stop()`이 참이면 `stopped`로 돌아가고 120초를 넘기면 "independent model calls did not overlap" `AssertionError`를 낸다. 해제되면 작업공간에 `same-name.txt`(내용은 행동 대상)를 쓰고, `research_work` 제출을 `producer_result`로 보낸다.
- 사용처: `ParallelEngineTests`의 여러 시험. 하위 클래스 `ObservedRunner`가 한 번 있다.

## SessionPolicyTests (행 127–199)

- 기반 클래스: `unittest.TestCase`. 표지·속성·도우미·훅이 없다. 모두 1단이다.

### `test_old_profile_cannot_bypass_a_new_zero_capacity_limit` (행 128–158)
- 성질: 한도가 0으로 바뀐 뒤에는 옛 프로필 판본으로도 슬롯을 얻을 수 없다. 한도가 다시 오르면 입장은 현재 판본의 용량 제약에 예약된다.
- 준비: 1단. `DEFAULT_CONFIG` 사본과 `build_profiles`로 인스턴스를 만든다. 옛 high 등급 `research_work` 프로필을 잡아 두고 `SessionSlots(runtime, instance)`를 만든다.
- 실행: 설정의 high 모델 한도를 0으로 바꾸고 `apply_editions`, 옛 프로필로 `slots.acquire`. 한도를 1로 올려 `apply_editions` 뒤 다시 `acquire`.
- 단언: 첫 입장은 `False`다. `admission_wait.kind == 'capacity'`, `next_owner == 'user'`, 예약이 비어 있다. 둘째 입장은 `True`이고, 예약의 `constraint_id`가 현재 high 판본의 `capacity_refs[0]`이다.
- 대역: 없음.

### `test_defaults_and_max_of_difficulty_and_importance` (행 160–170)
- 성질: 기본 모델·한도 표가 정해진 값이다. 평가 등급은 난도와 중요도 중 큰 쪽이다. 모델 선택은 한도가 0이어도 평가 등급의 모델을 고른다.
- 준비: 1단.
- 실행: `MODELS`, `LIMITS`, `DEFAULT_CONFIG` 비교, `assessment_tier`, 한도 0 설정의 `selection`.
- 단언:
  - `MODELS == {'high': 'gpt-6-astra', 'medium': 'gpt-5.6-sol', 'low': 'gpt-5.6-terra'}`다.
  - `LIMITS == {'work': 각 모델 3}`이다.
  - `DEFAULT_CONFIG`의 `tier_models`와 `session_limits`가 `(MODELS, LIMITS)`다.
  - low/high 평가의 등급이 `'high'`다.
  - high 평가의 선택 모델이 `MODELS['high']`다.
- 대역: 없음.
- 비고: 제품 상수값을 시험에 적어 둔 드문 경우다. 시험-지침 규칙 7은 제품 정의를 import하라고 하지만, 이 시험은 기본값 자체를 계약으로 고정한다.

### `test_model_names_extend_without_closed_catalogue` (행 172–176)
- 성질: 모델 이름은 닫힌 목록이 아니다. 설정한 새 이름과 그 한도를 정책이 받아들인다.
- 준비: 1단. high 모델을 `'configured-future-model'`로 바꾸고 그 한도를 2로 둔다.
- 실행: `validate_policy(config)`.
- 단언: 예외가 없다.
- 대역: 없음.

### `test_bad_capacity_and_missing_tier_model_are_rejected` (행 178–191)
- 성질: 잘못된 한도 값은 설정 스키마가, 빈 모델 이름과 빠진 등급 모델은 정책이 거부한다.
- 준비: 1단.
- 실행: high 한도를 `-1`, `True`, `None`, `1.5`로 바꿔 `validate_config`. 공백 이름 `' '` 한도를 넣어 `validate_policy`. 등급 `low`/`medium`/`high`를 하나씩 지워 `validate_policy`.
- 단언: 앞 넷은 `ValueError`이고 메시지가 `'config/session_limits/work'`에 맞는다. 나머지는 `ValueError`(유형만)다.
- 대역: 없음.
- 비고: 주석(행 180)은 용량 범위는 설정 스키마의, 필드 간 규칙은 정책의 몫이라고 적는다. `subTest`는 쓰지 않고 루프로 돈다.

### `test_role_floor_raises_low_assessment_and_unassessed_work_uses_high` (행 193–199)
- 성질: 역할 하한은 낮은 평가를 끌어올린다(`task_contract_review`는 최소 medium). 평가 없는 작업은 high를 쓴다.
- 준비: 1단.
- 실행: low/low 평가의 `task_contract_review` 선택과, 평가 없는 `research_work` 선택.
- 단언: 앞은 `('medium', MODELS['medium'])`, 뒤는 `('high', MODELS['high'])`다.
- 대역: 없음.

## OwnerRescanTests (행 202–218)

- 기반 클래스: `unittest.TestCase`. 표지·속성·도우미·훅이 없다.

### `test_owner_rejudges_after_a_state_change_or_its_time_bound_but_not_after_an_observation` (행 203–218)
- 성질: 소유자 루프는 게시된 상태가 바뀌었거나 재검사 주기(`OWNER_RESCAN_SECONDS`, 1.0초)가 지났을 때만 준비 여부와 배정을 다시 판정한다. 관찰만 게시한 것은 재판정을 부르지 않는다.
- 준비: 2단(`restore_template(state_fixtures.active_instance, config={})`).
- 실행: `do_math.scheduler.time.monotonic`을 100.0으로 고정한다. `_scan_due()`를 부르고, 이력 추가 뒤 `_publish_observation()`, 다른 이력 추가, 시계를 `100 + OWNER_RESCAN_SECONDS`로 옮기며 `_scan_due()`를 차례로 부른다.
- 단언: 첫 호출 `True`, 곧바로 `False`(메시지 "an unchanged state was judged again"). 관찰 게시 뒤 `False`(메시지 "an observation publication made the owner judge again"). 상태 변경 뒤 `True`, 다시 `False`. 주기 경과 뒤 `True`.
- 대역: `do_math.scheduler.time.monotonic` 패치(시계 주입).
- 비고: 제품 판정은 `scheduler.py` 56–71행이다.

## SlotTests (행 221–358)

- 기반 클래스: `unittest.TestCase`.
- docstring: "Git 쓰기 소유자가 입장을 소유하고, 관찰자는 예약을 조정하지 않는다."
- 클래스 표지·속성: 없음.
- `setUp` (행 223–228): 모델마다 한도 1을 둔다. `restore_template(initialized_instance, goal='Reservation boundary fixture', config={'operator_enabled': True, 'scholarly_enabled': False, 'session_limits': ...})`로 공개 `initialize`만 한 상태를 복원한다. 네 단 밖의 템플릿이다. `self.repo`, `self.workspace`(`work-0`), `self.engine`(`ScriptedRunner`)을 둔다.
- 도우미:
  - `slots(*, observer=False)` (행 230–233): 엔진 런타임·인스턴스 위의 `SessionSlots`.
  - `reserve(eid, *, operational=False)` (행 235–254): docstring대로 작업 역할(슬롯을 쥠)이나 운영 역할(슬롯을 쥐지 않음)을 입장시킨다. 작업은 `task_contract_review`, 운영은 `research_plan`의 high 모델 프로필이다. 활동을 열고 실행을 만들어 `starting`으로 전이한 뒤 `slots().acquire(...)`를 부른다. `(accepted, execution)`을 돌려준다.

### `test_work_slot_operational_admission_and_reusable_slots_are_published_together` (행 256–271)
- 성질: 작업 슬롯 입장, 슬롯 없이 들어가는 운영 입장, 해제 뒤 재사용이 모두 같은 게시 상태에 기록된다. 예약 소유자는 모두 실제 실행이다.
- 준비: `setUp` 절 참조.
- 실행: `writer_lock()` 안에서 `reserve('EX-work')`, `reserve('EX-blocked')`, `reserve('EX-operation', operational=True)`, `_save()`, `store.load()`, `release('EX-work')`, `reserve('EX-next')`, `_save()`.
- 단언:
  - 입장 결과가 차례로 참, 거짓(한도 1), 참이다.
  - 저장 머리가 엔진 머리와 같다.
  - 예약이 비어 있지 않고, `EX-operation` 소유의 `unit == 'execution'` 예약이 없다.
  - 모든 예약 소유자가 저장된 실행에 있다.
  - 해제는 참이고, 재입장도 참이다.
  - 작업공간에 `*.sqlite*` 파일이 없다.
- 대역: 없음(실제 Git).
- 비고: 마지막 단언은 예약 장부가 별도 DB가 아니라 게시 상태에 있음을 확인한다.

### `test_saved_reservations_survive_reopen_until_explicit_release` (행 273–284)
- 성질: 저장된 예약은 엔진을 다시 열어도 남고, 명시적으로 해제할 때까지 슬롯을 차지한다.
- 준비: `setUp`.
- 실행: 잠금 안에서 `reserve('EX-held')`와 저장, 새 `ResearchEngine`으로 재적재, 관찰자 `snapshot()`, 잠금 안에서 해제와 저장, 다시 `snapshot()`.
- 단언: 재적재한 예약이 사본과 같다. 관찰자 스냅숏의 high `used`가 1이었다가 해제 뒤 0이다.
- 대역: 없음.

### `test_distinct_instances_have_distinct_reservation_ledgers` (행 286–300)
- 성질: 같은 저장소의 서로 다른 인스턴스는 예약 장부를 공유하지 않는다.
- 준비: `setUp`. 첫 인스턴스에 `EX-first-instance`를 예약한다.
- 실행: 공개 `initialize(self.repo, goal='Separate reservation ledger', workspace=root/'other-work', config=...)`로 둘째 인스턴스를 만들고, 두 관찰자 스냅숏을 읽는다.
- 단언: 인스턴스 ID가 다르다. 둘째 인스턴스의 `used`는 0, 첫째는 1이다. 둘째 저장본의 `reservations`가 `{}`이다.
- 대역: 없음. 공개 `initialize`를 실제로 한 번 더 부른다(4단 경로 일부).

### `test_observer_cannot_acquire_or_reconcile_an_unknown_lifetime` (행 302–311)
- 성질: 관찰자 슬롯은 읽기 전용이다. 해제하려 하면 거부되고, 스냅숏은 런타임을 바꾸지 않는다.
- 준비: `setUp`. `EX-held` 예약과 저장, 런타임 사본.
- 실행: `slots(observer=True).release('EX-held')`, `snapshot()`.
- 단언: `ValueError`의 메시지가 `'read-only'`에 맞는다. 런타임이 사본과 같다.
- 대역: 없음.
- 비고: 이름은 "acquire or reconcile"을 말하지만 코드는 관찰자의 `release`와 `snapshot`만 부른다. `acquire` 거부는 직접 단언하지 않는다.

### `test_two_processes_cannot_both_own_the_git_writer` (행 313–326)
- 성질: 한 프로세스가 Git 쓰기 잠금을 쥐고 있으면 다른 프로세스는 그 잠금을 얻지 못한다.
- 준비: `setUp`.
- 실행: 부모가 `writer_lock()`을 쥔 채 `subprocess.run([sys.executable, '-c', program, ...], timeout=30)`으로 자식 파이썬을 띄운다. 자식은 같은 저장소·인스턴스의 `writer_lock()`을 시도해 성공하면 `acquired`를, 실패하면 예외 유형 이름을 출력한다.
- 단언: 자식 종료 코드 0, 출력에 `'LockError'`가 있고 `'acquired'`가 없다.
- 대역: 없음.
- 비고: 실제 자식 프로세스를 쓴다(제한 시간 30초). 시험-지침 규칙 6과 `research_fixtures` docstring은 같은 프로세스 안의 잠금 경합으로 충분하면 자식이 필요 없다고 하지만, 이 시험은 "두 프로세스"를 성질로 삼는다.

### `test_slot_waits_for_actual_named_job_termination` (행 329–345)
- 성질: 슬롯은 이름 붙은 실제 Windows Job이 비기 전에는 해제되지 않고, 종료가 확인된 뒤에야 해제된다.
- 준비: `setUp`. 잠금 안에서 `reserve('EX-job')`를 하고, 그 실행의 `launch_ticket.job_name`을 이름으로 쓴다.
- 실행: `WindowsJob([python, -c, sleep 30], name=...)`을 만든다. `slots().started('EX-job', {'pid', 'job_name'}, at=now())`, 저장, `job.resume()`, `release`, `job.terminate()`, `job.wait(10)`, `named_job_empty`, `release`, 저장.
- 단언: 종료 전 해제는 `False`다. 종료 뒤 `wait`가 참, `named_job_empty`가 참이고, 해제가 참이다.
- 대역: 없음.
- 비고: `@unittest.skipUnless(os.name == 'nt', 'requires a Windows Job')`. 실제 Windows Job과 파이썬 자식을 쓴다. 행 332의 `name = 'Local\\DoMath-test-' + uuid.uuid4().hex`는 행 335에서 바로 덮어써지므로 쓰이지 않는 대입이다. 모듈의 `uuid` import는 이 줄에서만 쓰인다.

### `test_regular_supervision_observes_without_creating_an_ai_execution` (행 347–353)
- 성질: 정기 감독(`scheduled_operator.check`, probe)은 관찰만 하고 AI 실행을 만들지 않는다.
- 준비: `setUp`(`operator_enabled=True`).
- 실행: `scheduled_operator.ModelRunner`를 부르면 `AssertionError`를 내는 패치를 건다. 그 상태로 `scheduled_operator.check(repo, id, workspace, probe=True)`.
- 단언: `outcome == 'observed'`, `model_called`가 거짓, 저장본 실행이 `{}`이다.
- 대역: `patch.object(scheduled_operator, 'ModelRunner', side_effect=AssertionError(...))`.

### `test_recovery_requires_actual_failure_evidence` (행 355–358)
- 성질: 운영자 복구는 실제 실패 증거 없이는 시작하지 않는다.
- 준비: `setUp`.
- 실행: `scheduled_operator.recovery(repo, id, workspace, failure={})`.
- 단언: `ValueError`의 메시지가 `'failure evidence'`에 맞는다(제품 "recovery requires preserved engine failure evidence", `scheduled_operator.py` 455행).
- 대역: 없음.

## ParallelEngineTests (행 361–640)

- 기반 클래스: `unittest.TestCase`. 표지·속성이 없다.
- `setUp` (행 362–363): `install_adapter_fixture(self)`.
- 도우미:
  - `engine(runner, count=3, *, public=False, **config)` (행 365–369): docstring대로 `ready_work` 복사본에 `runner`를 단 엔진. `config`에 한도 등이 들어간다. `self.root`와 `self.repo`를 둔다.
  - `configure_limits(engine, limits)` (행 371–377): `send_control(configure, session_limits)`, 이어서 AI 프로필 참조 전체로 `decision`의 `initialization`/`probe` 변경을 보낸다. 새 한도 판본에 필요한 능력 증거를 다시 얻기 위해서다.
- 공통 비고: 러너 호출은 `local_job_runner`로 실제 Windows Job을 띄운다. 여러 호출이 실제 스레드로 겹친다.

### `test_three_calls_overlap_and_apply_serially_to_distinct_workspaces` (행 379–401)
- 성질: 독립 작업 호출 세 개가 동시에 돌고, 각자 다른 작업공간을 쓴다. 적용은 소유자 스레드에서 차례로 한다. 끝난 상태는 `check()`를 통과한다.
- 준비: `ready_work(count=3, public=True)`. 주석: `check()`를 판정하므로 공개 상태가 필요하다. `ConcurrentRunner()`(기대 3). `_save`를 autospec으로 감싸 매번 호출 스레드가 주 스레드인지 단언한다.
- 실행: `engine.run(max_steps=3)`.
- 단언:
  - `peak == 3`, 작업공간이 3개로 모두 다르다.
  - 받은 모델이 high 3번이고, `same-name.txt` 내용이 3가지다.
  - 수용된 `research_work`가 3개다.
  - 반환 상태의 `budget[high].used == 0`이다.
  - `check()`의 `errors == []`, `inspection.not_checked == []`, `inspection.findings == []`, `passed`가 참이다.
- 대역: `ConcurrentRunner`, `_save` autospec(스레드 확인).

### `test_unavailable_assigned_model_waits_without_spending_other_model_slots` (행 403–414)
- 성질: 배정된 모델에 한도가 없으면 작업은 다른 모델 슬롯을 쓰지 않고 용량 대기에 든다. 한도가 생기면 그 모델로 돈다.
- 준비: `ready_work(count=1)`, high 한도 0. `ConcurrentRunner(expected=1)`.
- 실행: `run(max_steps=1)`, `configure_limits(high=1)`, `run(max_steps=1)`.
- 단언: 첫 상태가 `capacity_waiting`이고, 받은 모델이 없으며, 대기의 `model_selection.model`이 high다. 한도 복구 뒤 받은 모델이 `[high]`다.
- 대역: `ConcurrentRunner`.

### `test_blocked_high_priority_work_does_not_block_independent_low_model_work` (행 416–438)
- 성질: high 모델 작업이 한도로 막혀도 독립된 low 모델 작업은 돈다.
- 준비: `ready_work(count=2)`, high 한도 0. 두 번째 과제의 `model_assessment`를 low/low로 바꾼다.
- 실행:
  1. 큐를 비우고 그 과제의 `task_contract_review`를 넣은 뒤 `ScriptedRunner`로 `run(1)`. 실제 검토를 다시 돈다.
  2. 원 큐의 high 작업을 앞에 되붙이고 `run(1)`. 실제 계획이 새 판정으로 다시 선택한다.
  3. 러너를 `ConcurrentRunner(expected=1)`로 바꾸고 `run(1)`.
- 단언: `ConcurrentRunner`가 받은 모델이 `[MODELS['low']]`이고, high 과제 대상 행동이 큐에 남는다.
- 대역: `ScriptedRunner`, `ConcurrentRunner`.
- 비고: 주석(행 430–431)은 바뀐 계약이 선택을 잃고, 실제 계획이 새 판단으로 다시 선택한다고 설명한다.

### `test_pause_reaches_all_parallel_calls_and_releases_their_slots` (행 441–459)
- 성질: 병렬 호출 세 개가 돌 때 일시 정지를 보내면 모든 호출에 닿는다. 슬롯은 모두 풀리고 인스턴스는 멈춘다.
- 준비: `ready_work(count=3)`, `ConcurrentRunner(expected=99)`. 스스로 해제되지 않게 기대 수를 크게 둔다.
- 실행: 별도 스레드 `controller`가 `started_count == 3`을 최대 120초 기다린 뒤 공개 `pause`를 보낸다. 주 스레드는 `run(max_steps=3)`, 끝나면 `controller.join(20)`.
- 단언: 제어 스레드가 끝났다. 상태 `paused`, `active_executions == []`, high `used == 0`, `research_work` 실행이 3개다.
- 대역: `ConcurrentRunner`(`should_stop` 폴링으로 `stopped` 반환).
- 비고: 조건 변수 대기 상한 120초, join 상한 20초.

### `test_live_operations_can_run_when_work_is_full_and_step_limit_is_reached` (행 461–514)
- 성질: 작업 슬롯이 다 차고 단계 상한에 닿아도, 실시간 운영 검토는 슬롯 없이 돈다.
- 준비: `ready_work(count=3, public=True, observation_mode='periodic', observation_interval_seconds=1)`. 주석: 결과가 합성 활성 상태와 달라 공개 상태를 유지한다. 지역 하위 러너 `ObservedRunner(ConcurrentRunner)`는 두 갈래로 답한다.
  - 운영 검토 호출이면 `continue` 처분을 `producer_result`로 제출한 뒤 해제 이벤트를 켠다. 주석(행 472–473)은 먼저 해제하면 대상이 끝나 검토가 쓸모없어진다고 설명한다.
  - 작업 호출이면 해제될 때까지 1초마다 빈 관찰 배치를 보낸다. 실제 러너의 유휴 주기를 흉내 낸 것이다. 120초 상한이 있다.
- 실행: `run(max_steps=3)`.
- 단언: 운영 검토 실행이 있다. 그 실행을 소유자로 하는 `unit == 'execution'` 예약이 없다(메시지: 운영 역할은 슬롯 없이 돈다). 그 `model`이 high다. 이어서 두 갈래 중 하나를 확인한다. `result_disposition.kind`가 `'preserved_after_target_change'`이면 대상 실행이 `ended`인지 보고, 아니면 `outcome == 'output_accepted'`인지 본다.
- 대역: `ObservedRunner`(실제 Windows Job), `observation_batch`.
- 비고: 마지막 단언은 경합 결과 두 가지를 모두 합격으로 받는다. 대상 종료 뒤 수거된 결과는 적용하지 않고 보존한다(주석 행 510). 0.1초 폴링.

### `test_planner_queue_order_cancels_only_unstarted_requests_and_preserves_obligations` (행 516–529)
- 성질: 계획의 큐 재배열(`queued_requests`)은 유지할 요청을 정한 순서로 두고, 취소한 요청만 뺀다. 취소된 과제는 `planned`로 돌아가고 완료 의무는 보존된다.
- 준비: `ready_work(count=3)`, `_refresh_readiness()`. 끝난 실행 `EX-plan`의 확장에 셋째 유지, 첫째 유지, 둘째 취소를 둔다.
- 실행: `engine._apply_queue_plan('EX-plan')`.
- 단언: 큐 ID가 `[third, first]` 순이다. 둘째 대상 과제의 `status == 'planned'`이고, 의무 ID가 `['OB-argument']`다.
- 대역: 없음(러너 불리지 않음).

### `test_model_assessments_flow_from_preparation_through_review_and_planning_to_execution` (행 531–552)
- 성질: 준비가 낸 모델 평가가 검토와 계획을 거쳐 작업 실행의 모델 선택까지 그대로 흐른다. 그 상태는 제출 검사와 점검을 통과한다.
- 준비: `ready_work(count=0, public=True)`. 공개 활성화 상태 그대로이고, 러너는 `ScriptedRunner(model_rating=low/low)`다.
- 실행: 최대 12번 `run(max_steps=1)`. 멈춤 조건은 "`research_work` 실행이 `ended`다". 주석(행 535–536)은 모든 단언이 첫 작업 실행과 그때까지의 제출만 읽으므로 그 뒤의 계획·목표 감사·재준비는 필요 없다고 적는다.
- 단언:
  - 첫 과제의 `model_assessment`가 준 평가다.
  - 첫 작업의 `model`이 low이고, `model_selection.assessment`가 준 평가다.
  - `check()`의 `errors == []`, `submission_checks.status == 'verified'`, `inspection.not_checked == []`, `inspection.status == 'healthy'`다.
- 대역: `ScriptedRunner`.
- 비고: 루프가 12번 안에 조건에 닿지 않아도 루프 자체는 실패하지 않는다. 그 경우 `work` 목록 단언에서 드러난다.

### `test_selected_task_without_a_plan_assessment_runs_at_its_reviewed_assessment` (행 554–569)
- 성질: 계획이 선택한 과제를 다시 평가하지 않으면, 작업은 검토된 과제 레코드의 모델 평가로 돈다.
- 준비: `ready_work(count=0, public=True)`, `ScriptedRunner(model_rating=low/low, plan_assessments=False)`.
- 실행: 최대 12번 `run(max_steps=1)`. 멈춤 조건은 "`research_work` 실행이 있다"다.
- 단언: 계획 실행이 있고 첫 계획의 `model_decisions == {}`다. 작업 실행이 있다. 없으면 대기 사유를 메시지로 싣는다. 첫 작업의 `model`이 low이고 `model_selection.assessment`가 준 평가다.
- 대역: `ScriptedRunner`.
- 비고: docstring은 "공유 템플릿 뒤 약 14초. 수령·계획 적용·배정이 각각 평가 없는 선택을 판정한다"고 적는다. 시험-지침 4절 규칙 8의 10초 목표를 넘는 이유를 밝힌 것이다.

### `test_failed_live_review_stops_its_parent_and_preserves_independent_work` (행 571–600)
- 성질: 실시간 운영 검토가 실패하면 그 부모 작업만 멈춘다. 독립된 다른 작업은 끝나 수용되고, 인스턴스는 멈추지 않는다.
- 준비: `ready_work(count=2, observation_mode='periodic', observation_interval_seconds=1)`. 지역 러너 `Runner`는 세 가지로 답한다.
  - 운영 검토면 이벤트를 켜고 `failed`로 돌아간다.
  - 과제 `'0'`의 작업이면 빈 관찰 배치를 계속 보낸다(검토 유발).
  - 다른 작업이면 검토 실패 이벤트 뒤 제출한다.

  작업 쪽 대기는 20초를 넘기면 `AssertionError`를 낸다.
- 실행: `run(max_steps=2)`.
- 단언: 수용된 작업이 정확히 1개이고, 상태가 `paused`가 아니다.
- 대역: `Runner`(실제 Windows Job), `observation_batch`.
- 비고: 부모가 실제로 멈췄다는 사실은 러너가 `should_stop()`에서 `stopped`로 돌아가는 경로로만 나타난다. 부모의 결과를 직접 단언하지는 않는다.

### `test_user_requests_and_intent_join_existing_operating_queue_in_order` (행 602–610)
- 성질: 사용자 요청과 입력 해석은 이미 있는 운영 큐 뒤에 도착 순서대로 붙는다.
- 준비: `ready_work(count=0)`. 2단 상태 그대로다.
- 실행: `_enqueue('maintenance')`와 저장, 공개 `request`(`research_preparation`), 공개 `input`, `process_controls()`.
- 단언: 큐 역할이 `['maintenance','research_preparation','intent_interpretation']`이다.
- 대역: `ConcurrentRunner`(불리지 않음).

### `test_output_repair_keeps_the_original_operating_queue_position` (행 612–640)
- 성질: 출력 수리로 다시 넣는 행동은 원래 운영 큐 위치를 지킨다.
- 준비: `ready_work(count=0, public=True)`. 주석: 활성화가 남긴 큐 사건이 이 규칙과 만난다. 지역 러너 `InvalidPreparation`은 `candidates`를 뺀 준비 출력을 돌려준다(스키마 위반). 큐는 `AC-older`(유지보수)와 `AC-preparation`(활성화 준비의 `event_refs` 승계)이다. `_dispatchable`은 유지보수를 배정하지 않도록 감싼다. 주석: 운영 역할은 모델 슬롯이 없으므로 배정 검사로 기다리게 한다.
- 실행: `run(max_steps=1)`.
- 단언: 러너가 받은 역할이 `['research_preparation']`이다. 큐 ID가 `['AC-older','AC-preparation']` 순이다. 둘째의 `repair_attempt == 1`이다.
- 대역: `InvalidPreparation`(실제 Windows Job), `_dispatchable`의 `create_autospec` 감싸기.

## ResearchAdmissionTests (행 643–684)

- 기반 클래스: `unittest.TestCase`. 표지·속성·도우미·훅이 없다.

### `test_public_task_flow_keeps_observation_and_state_contracts_consistent` (행 644–684)
- 성질: 공개 과제 흐름(준비, 검토, 계획, 작업)에서 공급자 입장은 매번 받아들여진다. 작업 실행은 관찰 규칙을 갖고, 점검은 오류 없이 끝난다.
- 준비: 2단(`start_active_copy(self)`), `ScriptedRunner`. 역할 문서 `_documents`의 본문을 합성 문자열과 그 해시로 바꾼다. 주석: 스케줄러·저장 통합 시험이지 역할 산문 해석 시험이 아니다. `_configure_candidate`로 창·자기 점검 시간과 `plan_settle_seconds=1`을 적용한다. AI 프로필마다 `capability_evidence(..., FixtureAdapter().describe(), ...)`를 넣고, 준비를 넣고 저장한다. `_provider_admit`은 결과가 참인지 매번 단언하도록 감싼다.
- 실행: `run(max_steps=8)`. 주석: 준비 완료 사건이 계획을 하나 더 열 수 있으므로 단계는 네 연구 단계가 아니라 행동 수다.
- 단언:
  - 작업 실행이 있고 첫 작업의 `observation_rules`가 비어 있지 않다.
  - `check()`의 `errors == []`다.
  - `inspection.status == 'incomplete'`다. 주석: 합성 초기 해석은 입력 목록이 없다.
  - 발견 메시지 집합이 `{'EX-check: role input manifest not examined', 'EX-interpret: role input manifest not examined'}`다.
- 대역: `ScriptedRunner`, `_provider_admit` autospec 감싸기, `FixtureAdapter`(`start_active_copy`가 패치).

## PlanAfterPreparationTests (행 687–725)

- 기반 클래스: `ActivatedPurposeHarness`. 표지·속성이 없다.
- 도우미:
  - `prepare(candidates, *, ready_candidate=False)` (행 688–709): 2단 `make_active(**fixture_config(scholarly_enabled=False, operator_enabled=False))`에서 시작한다. 큐가 비고 대기 사건이 없음을 단언한다. 주석: 공개 활성화는 계획이 먼저 소비해야 할 재고려 사건을 남기므로 합성 상태를 쓴다. `ready_candidate`가 참이면 먼저 `ScriptedRunner(preparation_candidates=[candidate('deferred')])`로 준비를 넣고 `run(max_steps=2)`를 돌려 준비 완료 과제를 만든다. 그다음 큐를 비우고 준비 하나를 넣어 `ScriptedRunner(preparation_candidates=candidates)`로 `run(max_steps=1)`을 돈다.
  - `plans(engine)` (행 711–712): 큐의 `research_plan` 행동 목록.

### `test_new_contracts_awaiting_review_do_not_open_a_plan_with_nothing_to_decide` (행 714–717)
- 성질: 새 계약이 검토를 기다리기만 하고 결정할 준비 완료 과제가 없으면, 준비는 계획을 열지 않는다.
- 준비: `prepare([candidate('one')])`.
- 실행: 도우미 안의 `run(max_steps=1)`.
- 단언: 큐에 `task_contract_review`가 있고 계획은 없다.
- 대역: `ScriptedRunner`.

### `test_preparation_still_opens_a_plan_when_a_ready_task_awaits_a_decision` (행 719–721)
- 성질: 결정을 기다리는 준비 완료 과제가 있으면 준비는 계획을 연다.
- 준비: `prepare([candidate('one')], ready_candidate=True)`.
- 실행: 같은 도우미.
- 단언: 계획이 정확히 1개다.
- 대역: `ScriptedRunner`.

### `test_preparation_without_any_pending_review_still_opens_a_plan` (행 723–725)
- 성질: 후보 없이 끝난 준비(대기 검토 없음)도 계획을 연다.
- 준비: `prepare([])`.
- 실행: 같은 도우미.
- 단언: 계획이 정확히 1개다.
- 대역: `ScriptedRunner`.

## DuplicateContractReviewTests (행 728–745)

- 기반 클래스: `ActivatedPurposeHarness`. 표지·속성·도우미가 없다.

### `test_a_running_review_of_the_same_contract_is_not_doubled_when_its_outside_premises_move` (행 729–745)
- 성질: 같은 계약의 검토가 이미 실행 중이면, 준비 여부를 다시 판정해도 검토를 하나 더 넣지 않는다.
- 준비: 2단 `make_active(...)`, `ScriptedRunner(preparation_candidates=[candidate('window')])`로 준비 `run(1)`. 큐의 검토 행동으로 `running` 실행을 등록한다.
- 실행: `_refresh_readiness()`.
- 단언: 큐의 `task_contract_review` ID가 원래 하나뿐이다. 메시지는 "끝난 검토 자신의 현행성 검사가 다른 검토가 필요한지 정한다"이다.
- 대역: `ScriptedRunner`.
- 비고: 이름의 "outside premises move"에 해당하는 전제 변경은 코드에서 따로 만들지 않는다. 실행 중 검토가 있는 상태에서 준비 판정을 다시 부르는 것만 한다.

## PlanSettleTests (행 748–774)

- 기반 클래스: `ActivatedPurposeHarness`. 표지·속성이 없다.
- `setUp` (행 749–752): 하네스 `setUp` 뒤 2단 `make_active(scholarly_enabled=False, operator_enabled=False)`를 둔다. `fixture_config`를 쓰지 않으므로 `plan_settle_seconds`는 제품 기본 300이다. 큐를 비운다.
- 도우미 `queue(plan, review=True)` (행 754–756): 큐를 계획 하나로 두고, `review`가 참이면 `AC-review`(`task_contract_review`, `TK-x`)를 덧붙인다.

### `test_a_plan_waits_for_pending_contract_reviews_so_nearby_approvals_share_one_decision` (행 758–763)
- 성질: 대기 중인 계약 검토가 있으면 계획은 정착(settle) 대기에 들어간다. 검토가 없으면 배정 가능하다.
- 준비: `setUp`, `queue(plan)`.
- 실행: `_dispatchable(plan)`, 검토 없이 다시.
- 단언: 첫 판정 `False`, `dispatch_wait.kind == 'plan_settle'`. 둘째 판정 `True`.
- 대역: 없음.

### `test_the_settle_wait_ends_at_its_configured_limit` (행 765–770)
- 성질: 정착 대기는 설정 한도(300초)를 넘으면 끝난다.
- 준비: `setUp`. `settle_started_at`을 실제 현재 시각에서 301초 전으로 둔 계획과 대기 검토.
- 실행: `_dispatchable(plan)`.
- 단언: 설정값이 300이다. 판정이 `True`다(메시지: 느린 검토가 첫 준비 완료 과제를 오래 붙들면 안 된다).
- 대역: 없음.
- 비고: 시계를 주입하지 않고 `datetime.now(timezone.utc)`를 쓴다. 301초 여유는 1초라서 느린 환경에서도 방향은 같다.

### `test_an_explicitly_requested_plan_does_not_settle` (행 772–774)
- 성질: 사용자가 명시적으로 요청한 계획(`requested_by`)은 정착 대기를 하지 않는다.
- 준비: `setUp`, `requested_by='UC-user'`인 계획과 대기 검토.
- 실행: `_dispatchable(plan)`.
- 단언: `True`.
- 대역: 없음.

## RunWithoutDeadlineTests (행 777–809)

- 기반 클래스: `ActivatedPurposeHarness`. 표지·속성·도우미가 없다.

### `test_elapsed_time_does_not_block_the_next_execution_and_work_calls_have_no_timeout` (행 778–809)
- 성질: 경과 시간은 다음 실행을 막지 않는다. 작업 역할 호출은 시간 상한이 없고(`None`), 비작업 역할 호출은 프로필 창의 `call_timeout_seconds` 이하 양수 상한을 받는다.
- 준비: 2단 `make_active(...)`, 큐를 비우고 준비 하나. 지역 러너 `Runner`는 `ScriptedRunner(preparation_candidates=[candidate('deadline regression')])`에 위임하고, 호출마다 가짜 시계를 10000초 앞당긴다.
- 실행: `scheduler.time`과 `engine.time`을 `SimpleNamespace(monotonic=실제 + offset, sleep=time.sleep)`로 패치하고 `run(max_steps=2)`.
- 단언: 호출이 2번이다. `WORK_ROLES` 여부 집합이 `{True, False}`다(준비와 계약 검토). 작업 역할 호출의 `timeout_seconds`는 `None`이다. 비작업 역할은 `0 < timeout_seconds <= profile.window.call_timeout_seconds`다. 상태가 `paused`가 아니다.
- 대역: `do_math.scheduler.time`, `do_math.engine.time` 모듈 패치(시계 주입), 위임 러너.

## SchedulingResponsibilityTests (행 812–855)

- 기반 클래스: `unittest.TestCase`. 표지·속성·도우미·훅이 없다. 메모리 엔진 대역(`FakeEngine` 계열)을 쓴다.

### `test_terminal_stale_assessment_gets_one_followup_without_reopening` (행 813–824)
- 성질: 종결된 과제의 평가가 비현행이 되면 후속 사건이 한 번만 생기고 큐에 걸린다. 과제는 다시 열리지 않는다.
- 준비: `engine_fixtures.reassessment_engine(directory)`. `TK-1`을 `closed`로 두고 평가를 `current=False`, `invalidated_reason='source corrected'`로 바꾼다.
- 실행: `_refresh_readiness()` 두 번.
- 단언: 상태는 `closed` 그대로다. `task_assessment_invalidated` 사건이 1개이고 대상이 `TK-1`이다. 그 사건 ID를 `event_refs`에 가진 큐 행동이 있다.
- 대역: `reassessment_engine`(`FakeEngine`).

### `test_initial_preparation_owns_initial_events_until_accepted` (행 826–839)
- 성질: 초기화 활성화가 만든 첫 준비는 초기 사건들을 소유한다. 준비가 수용되기 전에는 그 사건으로 계획을 열지 않는다. 배정은 소비가 아니다.
- 준비: `FakeEngine(directory)`와 `activate()`. 상태를 `initializing`으로 되돌리고, `_lifecycle_event('trust_environment_activated')`, `_activate_initialization()`을 부른다. `adapter_for`는 `FixtureAdapter`로 패치한다.
- 실행: 첫 준비 행동을 찾고 `_refresh_readiness()`.
- 단언: 준비의 `event_refs` 집합이 `pending_events`와 같다. 계획이 없다. `pending_events`가 비어 있지 않다(메시지 "Assignment is not consumption").
- 대역: `FakeEngine`, `adapter_for` 패치.

### `test_normal_dispatch_occupancy_does_not_request_a_new_plan` (행 841–855)
- 성질: 과제가 평소대로 작업에 배정되어 점유 중이면 새 계획을 요청하지 않는다. 점유 중에 실제 권한이 사라지면 계획이 필요하다.
- 준비: `FakeEngine`, `activate()`, `task()`, `_refresh_readiness()`. 큐를 그 과제의 `research_work` 하나로, `pending_events`를 빈 목록으로 둔다.
- 실행: `_refresh_readiness()`, 권한 `GR-research`를 `revoked`로 바꾼 뒤 `_refresh_readiness()`.
- 단언: 처음엔 계획이 없고 `_task_readiness[task].dispatch_occupied`가 참이다. 권한 취소 뒤에는 계획이 있다(메시지 "Actual authority loss during occupancy still needs planning").
- 대역: `FakeEngine`, `adapter_for` 패치.

## MachineAdmissionConnections (행 858–935)

- 기반 클래스: `unittest.TestCase`. 표지·속성이 없다.
- 도우미 `fixture()` (행 859–866): `provider_fixtures.host_capacity_fixture()`의 인스턴스를 `routing_engine()`에 싣는다. 호스트 제약은 jobs 4, 메모리 512 MiB, CPU 8000bp이고, 예비분은 jobs 1, 128 MiB, 2000bp다. `formal_check` 프로필은 jobs 1, 128 MiB, 2000bp를 요구한다. `_execution_profile`은 그 프로필을, `_admit_review_execution`은 `{'disposition': 'not_applicable'}`을 돌려주는 autospec이다. `_save`도 autospec이다.

### `test_common_machine_admission_reserves_before_start_and_refuses_without_execution` (행 868–885)
- 성질: 기계 역할 입장은 시작 전에 호스트 예약을 잡는다. 용량이 모자라면 실행을 만들지 않고 활동을 대기로 둔다. 시작 실패로 해제되면 다시 입장할 수 있다.
- 준비: `fixture()`.
- 실행: 같은 대상의 `formal_check` 세 개를 `_register_execution`으로 등록한다. 넷째 `AC-refused`는 큐에 넣고 등록을 시도한다. `_local_call_returned('EX-machine-0', {'launch_not_created': True})` 뒤 `_session_slots().release('EX-machine-0', reason=...)`, 재등록.
- 단언:
  - 세 실행이 모두 `starting`이고, 예약 ID가 3개씩이며, `capacity.provider`가 `None`이다.
  - 넷째 등록은 `None`이고, 실행이 없으며, 그 활동이 `waiting`이다.
  - 예약이 모두 9개다.
  - 해제가 참이고, 재등록 실행이 `starting`이다.
- 대역: `fixture()`의 autospec 대역들.
- 비고: 가용 jobs는 4 − 예비 1 = 3이므로 넷째가 거부된다. 예약 9개는 실행 3개 × 단위 3개(jobs, memory_bytes, cpu_rate_basis_points)다.

### `test_machine_callback_seals_process_before_resume_and_keeps_uncertain_capacity` (행 887–904)
- 성질: 기계 시작 콜백은 프로세스 식별을 기록하고 실행을 `running`으로 바꾼 뒤 한 번 게시한다(재개 전 봉인). 로컬 Job 종료가 확인되지 않으면 용량과 출력을 붙든다.
- 준비: `fixture()`, 실행 `EX-one` 등록. 식별은 `job_name`, `pid=17`, `creation_filetime`이다. `_save`의 `side_effect`는 게시 순간에 `capacity.process`가 식별과 같고 `status`가 `running`인지 단언한다.
- 실행: `_machine_started('EX-one', identity)`. 이어 `named_job_empty=False` 패치 아래 `release_or_hold(execution, _session_slots(), at=...)`.
- 단언: `_save.assert_called_once()`다. `release_or_hold`가 `False`이고, 실행이 `stopping`이다. `error`가 정확히 "Local Job termination is unconfirmed; capacity and output remain held for recovery."다. 정산된(`settled`) 예약이 없다.
- 대역: `_save` side_effect 단언, `do_math.windows_job.named_job_empty` 패치.

### `test_actual_git_snapshot_binds_machine_reservations_and_start_identity` (행 906–935)
- 성질: 기계 입장과 시작 식별은 실제 스키마와 Git CAS로 게시된다. 입장 스냅숏에는 `starting` 실행과 호스트 예약 3개가 있고, 시작 뒤 스냅숏에는 프로세스 식별과 `running`이 있다.
- 준비: 임시 폴더에 `git_init(root/'repo')`. `host_capacity_fixture`와 `current_state`로 인스턴스·런타임을 만들어 `routing_engine()`에 싣는다. `formal_check` 역할 프로필 참조를 그 프로필로 맞춘다. 실제 `ResearchRepository`로 저장소를 바꾸고 `initialize`한다.
- 실행: `writer_lock()` 안에서 `_register_execution`, `_save()`, 입장 머리로 `load`, `_machine_started`, 새 머리로 `load`.
- 단언: 입장 스냅숏의 실행이 `starting`이고 예약이 3개다. 시작 뒤 머리는 입장 머리와 다르고, 그 스냅숏의 `capacity.process`가 식별과 같으며 `status`가 `running`이다.
- 대역: Job 식별은 대역(주석 행 928–929). 저장은 실제 Git이다.

## MaintenanceFenceRunTests (행 938–949)

- 기반 클래스: `unittest.TestCase`. 표지·속성·도우미·훅이 없다.

### `test_run_that_starts_under_a_maintenance_fence_returns_without_an_execution` (행 939–949)
- 성질: 유지보수 울타리(maintenance fence)가 `quiescent`인 상태에서 시작한 `run`은 실행을 만들지 않고 돌아온다.
- 준비: 2단(`start_active_copy(self)`). 공개 `quiesce` 제어를 보내고 새 엔진으로 `process_controls()`를 부른다.
- 실행: `run(max_steps=1)`.
- 단언: 처리 뒤와 실행 뒤 모두 `maintenance_fence.state == 'quiescent'`다. 실행 목록이 처리 뒤 사본과 같다.
- 대역: 없음.
- 비고: 주석(행 940)은 소유자 루프가 첫 통과에서 멈춤 검사보다 먼저 울타리를 만난다고 적는다.

## 관계

- 같은 제품 기능의 다른 층:
  - 예약 산술은 `test_budget`이 1단으로 본다.
  - 호스트 자원과 기계 병렬은 `test_host_resources`, `test_machine_parallel`, `test_windows_job`(`host` 조각)이 본다.
  - 공급자 대기는 `test_provider_wait`가, 운영자는 `test_operator`가 본다.
  - 모델 평가 흐름은 `test_model_assessment_flow`가 본다.
  - 제어 순서는 `test_research_recovery`가 본다.
- 픽스처 의존: `runner_fixtures.ScriptedRunner`가 이 모듈의 주 러너다. 목적 시나리오 러너 `PurposeRunner`는 쓰지 않고, `ActivatedPurposeHarness`는 `make_active`만 쓴다. `engine_fixtures`의 `initialized_instance`, `reassessment_engine`, `routing_engine`, `FakeEngine`, `provider_fixtures.host_capacity_fixture`, `research_fixtures`의 `activated_instance`/`active_instance` 기반 빌드에 기댄다.
- 이 모듈에만 있는 도우미: `ready_work`, `ConcurrentRunner`(와 지역 하위 클래스 `ObservedRunner`), `SlotTests.reserve`/`slots`, `ParallelEngineTests.engine`/`configure_limits`, `PlanAfterPreparationTests.prepare`/`plans`, `PlanSettleTests.queue`, `MachineAdmissionConnections.fixture`.
- 겹치거나 보완하는 시험:
  - 운영 역할이 작업 슬롯을 쥐지 않는다는 성질을 세 곳이 확인한다. `SlotTests`의 첫 시험(단위), `test_live_operations_...`(병렬 엔진), `test_purpose_engine`의 실시간 관찰 두 시험(목적 시나리오)이다.
  - 계획 개폐 규칙은 `PlanAfterPreparationTests`(열 때)와 `PlanSettleTests`(기다릴 때)가 나눠 맡는다.
  - 기계 입장은 메모리 층 두 시험과 실제 Git 층 한 시험으로 나뉜다.

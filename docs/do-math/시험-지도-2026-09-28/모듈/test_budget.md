# test_budget

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_budget.py` (97행) |
| 클래스 / 테스트 | 1 / 5 |
| 시험 대상 제품 코드 | `do_math/budget.py`의 `plan_reservations`, `settle_reservation`, `BudgetConflict`, `BudgetInputError`; `do_math/session_slots.py`의 `held_reservations` |
| 사용하는 픽스처 모듈 | 없음 |
| 격리 표지 | 없음 |
| 시작 상태 | 1단(순수 함수 직접 호출). 저장소·엔진·프로세스를 쓰지 않는다 |

## 목적

모듈 docstring은 "한 실행의 고정된 프로필이 요구하는 예약 산술"을 시험한다고 밝힌다. 시험 대상인 `plan_reservations`는 실행 하나가 프로필에 따라 잡아야 할 예약 행(held reservation) 전부를 한 번에 계산하고, 용량이 하나라도 모자라면 아무 행도 만들지 않고 `BudgetConflict`를 던진다. `settle_reservation`은 잡힌 예약 하나를 실제 증거와 함께 정확히 한 번 정산한다. 이 모듈은 두 함수의 원자성, 입력 불변, 두 종류의 용량(동시 실행 슬롯과 호스트 자원) 판정, 정산의 전량·일회성 규칙을 검사한다. 두 함수는 저장소를 모르는 순수 함수이므로 모든 시험이 사전(dict) 입력만으로 끝난다.

## 모듈 수준 요소

- 행 11–13: `SCRIPTS`(스킬의 `scripts/` 폴더)를 `sys.path` 앞에 넣는다. `run_tests.py` 밖에서 이 파일을 직접 실행하거나 `unittest discover -s scripts/tests`로 돌려도 `do_math` 패키지를 import할 수 있게 하는 공통 머리다.
- 행 23 `RESERVE`: 호스트 제약의 `control_reserve` 기본값. 세 단위(`jobs`, `memory_bytes`, `cpu_rate_basis_points`) 모두 0이다. 제어기 예비분이 없는 상태를 기준선으로 두고, 예비분의 효과는 이 값을 바꾼 시험에서만 본다.
- 행 96–97: 직접 실행하면 `unittest.main(verbosity=2)`로 이 모듈의 시험을 돈다.

## BudgetTests (행 26–93)

`unittest.TestCase`를 그대로 상속하고 표지·설정 훅이 없다. 두 도우미 메서드가 입력을 만든다.

- `constraints(*, work_slots=1, max_jobs=1, memory_bytes=100, reserve=None)` (행 27–34): 채택된 제약 두 개를 ID로 묶은 사전. `exec`는 `kind="concurrency"`, `accounting_unit="execution"`, `work_slots` 슬롯이다. `host`는 `kind="host"`로 `max_jobs`, `memory_bytes`, `cpu_rate_basis_points=10000`과 `control_reserve`(기본 `RESERVE` 사본)를 갖는다.
- `profile(*, host_memory=50)` (행 36–43): AI 실행 프로필 `EP-1`(개정 1, `sha256`은 `"0"*64`). `ai.capacity_refs=["exec"]`로 동시 실행 슬롯 하나를, `host_resources`로 `host` 제약에 `jobs=1`, `memory_bytes=host_memory`, `cpu_rate_basis_points=5000`을 요구한다.

### `test_one_profile_reserves_its_work_slot_and_host_demands_atomically` (행 45–57)
- 성질: 프로필 하나는 동시 실행 슬롯 하나와 호스트 요구 세 단위를 한꺼번에 예약하고, 입력 제약을 바꾸지 않으며, 슬롯이 이미 차 있으면 다음 실행을 거부한다.
- 준비: `max_jobs=2`, `memory_bytes=200`인 제약과 기본 프로필. 비교용으로 제약의 `deepcopy`를 떠 둔다.
- 실행: `plan_reservations([], constraints, profile, owner_id="EX-1")`, 이어서 그 결과를 `held`로 넘긴 `owner_id="EX-2"` 호출.
- 단언: 반환 행의 `(constraint_id, unit, reserved)` 집합이 `exec/execution/1`과 `host`의 `cpu_rate_basis_points/5000`, `jobs/1`, `memory_bytes/50` 넷과 같다. 모든 행이 `state="held"`, `owner_id="EX-1"`이고 `authority_refs`가 프로필의 `id`·`revision`·`sha256` 하나를 가리킨다. 호출 뒤 제약이 사본과 같다(입력 불변). 두 번째 호출은 `BudgetConflict`를 메시지 `"concurrency capacity unavailable: exec"`로 던진다. 호스트 용량은 두 번째 실행을 받을 만큼 넉넉하므로 거부 사유는 슬롯에 고정된다.
- 대역: 없음.

### `test_a_profile_without_capacities_reserves_nothing` (행 59–61)
- 성질: AI 용량 참조도 호스트 요구도 없는 프로필은 아무것도 예약하지 않는다.
- 준비: `actor_kind="machine"`이고 `ai`·`host_resources`가 없는 프로필 `EP-2`.
- 실행: `plan_reservations([], constraints(), profile, owner_id="EX-1")`.
- 단언: 반환값이 빈 튜플 `()`이다.
- 대역: 없음.

### `test_host_capacity_is_checked_separately_and_keeps_the_control_reserve` (행 63–68)
- 성질: 호스트 자원은 동시 실행 슬롯과 따로 판정되고, 제약의 `control_reserve`만큼은 실행에 빌려주지 않는다.
- 준비: 두 경우. (1) 기본 제약(`memory_bytes=100`, 예비분 0)에 `host_memory=101`인 프로필. (2) `memory_bytes` 예비분 60을 둔 제약에 기본 프로필(요구 50).
- 실행: 두 경우 모두 빈 `held`로 `plan_reservations`.
- 단언: 두 경우 모두 `BudgetConflict`를 메시지 `"host capacity unavailable: host/memory_bytes"`로 던진다. (2)는 요구 50이 전체 용량 100보다 작아도 가용량 100−60=40을 넘어 거부되므로, 예비분이 가용량에서 빠진다는 제품 규칙(`budget.py`의 "The controller's reserve is never lent to an admitted child Job.")을 확인한다.
- 대역: 없음.

### `test_returned_slot_is_reusable_but_held_slot_remains_occupied` (행 70–81)
- 성질: 정산으로 반환된 예약은 슬롯을 비우고, 아직 `held`인 예약은 슬롯을 계속 차지한다.
- 준비: 같은 `exec` 슬롯에 대한 두 예약 행. `RR-returned`는 `state="settled"`, `returned=1`, 증거 `local_job_empty`다. `RR-held`는 그것을 바탕으로 `state="held"`, `returned=0`, `reobserve.on="local_termination_barrier"`로 바꾼 행이다. 두 행을 `runtime["reservations"]`에 담는다.
- 실행: `session_slots.held_reservations(runtime)`, 빈 `held`의 `plan_reservations`, `held_reservations(runtime)`을 `held`로 넘긴 `plan_reservations`.
- 단언: `held_reservations`는 `[RR-held]`만 돌려준다. 빈 `held`로는 4행이 예약된다. 실제 `held` 목록을 넘기면 `BudgetConflict`(`"concurrency capacity unavailable: exec"`)가 난다. 반환된 행이 슬롯을 점유하지 않는다는 사실은 `held_reservations`가 그 행을 걸러낸다는 단언으로 확인된다.
- 대역: 없음.

### `test_settlement_is_exactly_once_and_requires_full_accounting` (행 83–93)
- 성질: 정산은 예약량 전부를 한 번에 설명해야 하고, 원 행을 바꾸지 않으며, 이미 정산한 행은 다시 정산할 수 없다.
- 준비: 기본 제약·프로필로 예약한 행 가운데 `exec` 행 하나.
- 실행: `settle_reservation`을 세 번 부른다. 소비 0·반환 0, 소비 0·반환 1, 정산 결과에 대한 소비 0·반환 1. 증거는 매번 `[{"receipt": "x"}]`.
- 단언: 첫 호출은 `BudgetInputError`를 메시지 조각 `"every reserved unit exactly once"`로 던진다. 둘째 호출의 결과는 `state="settled"`이고 `reobserve` 키가 없으며, 원 행의 `state`는 여전히 `"held"`다(사본 반환). 셋째 호출은 `BudgetInputError`(`"only a held reservation"`)로 거부된다.
- 대역: 없음.
- 비고: 제품의 세 번째 거부 사유인 "증거 없는 정산"(`"settlement requires actual evidence_refs"`)과 음수 입력 거부(`_nonnegative`)는 이 모듈에서 단언하지 않는다.

## 관계

- 이 모듈은 예약 산술만 본다. 예약 행이 실행의 입장·종료 경로에서 런타임 상태(`runtime["reservations"]`)에 기록되고 정산되는 과정은 `test_host_resources`, `test_execution_profiles`, `test_machine_scheduling`, `test_execution_lifecycle` 등이 검사한다. 원문에 `reservation`이 나오는 시험 모듈은 이 모듈을 포함해 26개다.
- `session_slots.held_reservations`는 슬롯 계산의 입력을 고르는 함수다. 여기서는 `plan_reservations`에 넘길 `held` 목록의 생산자로만 쓰인다.
- 픽스처 모듈을 쓰지 않으므로 다른 모듈과 공유하는 준비 코드가 없다.

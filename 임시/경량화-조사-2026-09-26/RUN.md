# RUN 영역 조사 결과: 실행 수명과 예산

실행 한 건은 네 경로를 거친다. 엔진 AI 경로, 기계 경로(신뢰 검사·활성화·외부 행동), 형식 검사 경로, 설치 복구 경로다. 이 네 경로에서 시작 콜백, 슬롯 반환과 종료 전이, 공급자 결과 반영, 정산 완료 판정이 각자 따로 구현되어 있다. 이 구현들을 `session_slots`·`launch`·`execution_lifecycle`의 공유 함수로 합치는 것이 이 영역에서 가장 큰 경량화다(RUN-01~06).

같은 규칙을 여러 곳에 쓴 결과는 이미 어긋남으로 나타났다. 정산 판정 하나는 예약 기록에 없는 필드를 읽는다(RUN-05). 상태 표시가 보여 주는 빈 슬롯과 실제 배정 판정이 다르다(RUN-07). 역할 출력 스키마와 수신 검사기가 서로 다른 값을 받아들인다(RUN-19). 상태 검사 하나는 제품 코드가 쓰지 않는 경로를 읽어서 아무것도 검사하지 않는다(RUN-20). 동작을 바꾸는 후보는 RUN-07, RUN-09, RUN-19, RUN-20의 넷이며, 사용자 결정이 필요하다.

좌표는 2026-09-26 main(`8d2ffd0`) 작업 트리를 기준으로 한다. 경로 약칭은 다음과 같다.

- `do_math/`: `C:/math/.claude/skills/do-math/scripts/do_math/`
- `tests/`: `C:/math/.claude/skills/do-math/scripts/tests/`
- `references/`, `SKILL.md`, `README.md`: `C:/math/.claude/skills/do-math/` 아래

## 1. 읽은 범위

전문을 읽은 파일은 다음과 같다(행 수).

- `do_math/lifecycle_engine.py` 1511
- `do_math/execution_lifecycle.py` 203
- `do_math/execution_window.py` 50
- `do_math/execution_profiles.py` 381
- `do_math/session_slots.py` 358
- `do_math/budget.py` 367
- `do_math/model_policy.py` 151
- `do_math/model_runner.py` 383
- `do_math/provider_engine.py` 173
- `do_math/provider_wait.py` 58
- `do_math/repair_execution.py` 220
- `do_math/operational_dispositions.py` 123
- `do_math/maintenance_gate.py` 49
- `do_math/launch.py` 63
- `do_math/windows_job.py` 622
- `references/모델과-실행예산.md` 121
- `C:/math/임시/경량화-조사-2026-09-26/기준.md` 120
- `C:/math/docs/do-math/검사-경량화-이음새-계약.md` 159

이음새를 따라 일부만 읽은 파일과 행 범위는 다음과 같다.

- `do_math/engine.py`: 88-240, 592-605, 628-645, 700-745, 878-912, 1538-1582, 1668-1780, 2620-2636, 3495-3660, 3036-3050, 4345-4362, 4640-4676
- `do_math/scheduled_operator.py`: 251-310, 372-612
- `do_math/scheduler.py`: 14-40, 120-145, 190-268, 505-640
- `do_math/governance_engine.py`: 40-80, 110-119, 360-390
- `do_math/state_checks.py`: 340-375, 480-490
- `do_math/record_schemas/domains.py`: 262-273, 455-461
- `do_math/record_schemas/__init__.py`: 225-232, 352-362
- `do_math/contracts.py`: 25-31, 120-121, 150-172
- `do_math/reporting.py`: 40-80
- `do_math/activities.py`: 195-210
- `do_math/decision_engine.py`: 45-58
- `do_math/review_engine.py`: 376-386
- `README.md`, `SKILL.md`, `references/CLI-실행-계약.md`: 수치 grep 결과 행만
- `tests/test_session_scheduler.py`: 100-112

## 2. 후보

### 실행 수명의 이음새 (무거운 묶음)

#### RUN-01: 종료 시 슬롯 반환과 반환 실패 처리가 네 곳에 따로 구현되어 있다
- 유형: 이음새중복
- 위치: `do_math/lifecycle_engine.py:1118-1122`(`_end_machine_execution`), `do_math/engine.py:3633-3643`(AI 경로), `do_math/engine.py:4651-4655`(형식 검사 경로), `do_math/scheduled_operator.py:570-583`(설치 복구 경로). 반환 자체의 정본은 `do_math/session_slots.py:257-291`(`release`)이다.
- 현상: 네 곳이 같은 순서를 각자 구현한다. `release`를 부르고, 실패하면 실행을 `stopping`(`terminating`)으로 옮기고, 오류 문구를 남기고, 산출을 보존한 채 멈춘다. 문구도 복제되어 있다. `"Machine capacity and result remain held until local Job termination is confirmed."`가 `lifecycle_engine.py:1121`과 `engine.py:4654`에 똑같이 있다. 형식 검사 경로(`engine.py:4651-4675`)는 기계 실행 종료를 위해 이미 있는 `_end_machine_execution`을 쓰지 않고 같은 전이를 다시 적는다. 설치 복구 경로는 반환 실패 시에도 `stopping` 전이를 먼저 하고, 성공한 때만 `ended`로 간다(`scheduled_operator.py:578-583`).
- 제안: `execution_lifecycle.py`에 `release_or_hold(execution, slots, *, at, reason) -> bool`을 둔다. 이 함수는 반환을 시도하고, 실패하면 `stopping`/`terminating` 전이와 오류 기록을 한 번에 한다. 네 끝점은 이 함수를 부르고, 경로별 산출 보존만 각자 한다. 형식 검사 경로는 `_end_machine_execution`을 재사용한다. 발사표 phase 갱신(RUN-04)도 이 함수의 앞에 둘 수 있다.
- 동작: 보존
- 실익: 추정 25~35행 감소. 반환 실패 처리의 정본이 하나가 되어, 이후 반환 조건이 바뀌어도 네 곳을 함께 고칠 필요가 없다.
- 위험과 보호: 경로마다 반환 실패 뒤의 저장 시점이 다르다. AI 경로는 `_publish_provider_result`로 저장하고 형식 검사 경로는 `_save`로 저장한다. 공유 함수는 저장하지 않고 호출자가 저장해야 한다. 보호 테스트: `tests/test_session_scheduler.py`의 `test_slot_waits_for_actual_named_job_termination`, `test_pause_reaches_all_parallel_calls_and_releases_their_slots`, `tests/test_provider_wait.py`의 `test_probe_is_reconciled_only_after_confirmed_local_termination`
- 확신: 높음. 네 곳의 원문 순서와 문구를 직접 대조했다.
- 다른 영역: `scheduled_operator.py`(운영 영역), `engine.py`

#### RUN-02: 시작 콜백(슬롯에 프로세스 기록 → running 전이 → 저장)이 세 곳에 있다
- 유형: 이음새중복
- 위치: `do_math/engine.py:735-742`(`_machine_started`), `do_math/engine.py:3546-3552`(AI 경로의 `started`), `do_math/scheduled_operator.py:504-508`(설치 복구의 `on_started`). 공통 정본 후보는 `do_math/session_slots.py:240-255`(`started`)다.
- 현상: 세 콜백이 모두 `slots.started(eid, identity)`를 부르고, `transition_execution(..., "running")`을 하고, 저장한다. 엔진 두 곳은 `process=json_safe(identity)`와 `started_at`도 기록하고, 복구 경로는 기록하지 않는다. 그래서 같은 사실(Job이 시작됨)이 경로에 따라 다른 필드 집합으로 남는다.
- 제안: `SessionSlots.started`가 running 전이와 시작 시각 기록까지 맡게 한다. 인자로 `at`을 받는다. 세 콜백에는 경로별 부가 기록(AI의 `execution_window` 게시)과 저장만 남긴다.
- 동작: 보존. 관찰되는 판정과 보장은 같다. 저장 기록에서는 설치 복구 실행에도 `started_at`이 추가된다. 실행의 `started_at`을 읽는 코드는 없다(grep `started_at`: 쓰는 곳 `engine.py:742`, `:3552`와 스키마뿐).
- 실익: 추정 10행 감소. 시작 사실의 기록 형식이 경로와 무관하게 하나가 된다.
- 위험과 보호: `started`는 `launch.validate`로 발사표를 검증한다(`session_slots.py:245-248`). 전이를 합칠 때 이 검증의 순서를 바꾸지 않는다. 보호 테스트: `tests/test_redesign_ENGINE.py`(기계 Job 시작), `tests/test_host_resources.py`
- 확신: 높음
- 다른 영역: `scheduled_operator.py`

#### RUN-03: Job 프로세스 식별이 `capacity.process`와 `execution.process`에 이중으로 저장된다
- 유형: 파생상태
- 위치: 쓰는 곳은 `do_math/session_slots.py:255`(`capacity["process"]`), `do_math/engine.py:742`와 `:3552`(`execution["process"]`)다. 읽는 곳은 `do_math/session_slots.py:266`, `do_math/provider_engine.py:50`, `do_math/model_runner.py:343`과 `:362`, `do_math/activities.py:204`, `do_math/execution_lifecycle.py:152`, `do_math/engine.py:4402`다. 스키마는 `do_math/record_schemas/domains.py:271`과 `do_math/record_schemas/schemas.py:113`이다.
- 현상: 같은 `identity`를 한 콜백 안에서 두 위치에 쓴다. 한쪽은 `deepcopy`로, 다른 쪽은 `json_safe`로 쓴다. 슬롯 반환은 `capacity.process`를 읽고, 원천 최종 산출 검증은 `execution.process`를 읽는다. 설치 복구 경로는 `capacity.process`만 쓰므로 두 위치의 내용이 경로에 따라 다르다. `provider_engine.py:49-58`의 `capacity`가 없는 분기는 `execution.process`를 읽는데, `capacity`가 없는 실행에 `process`가 기록되는 경로는 찾지 못했다(RUN-21 참조).
- 제안: 한 위치를 정본으로 정한다. 반환 장벽이 쓰는 `capacity.process`를 정본으로 권한다. 나머지 읽는 곳은 그 위치를 읽게 하고 `execution.process` 쓰기를 없앤다. RUN-02와 함께 적용하면 쓰는 곳은 `SessionSlots.started` 하나가 된다.
- 동작: 보존. 저장 기록의 모양은 바뀐다.
- 실익: 동기화 대상 필드 하나 제거. 읽는 곳 7곳이 같은 위치를 본다.
- 위험과 보호: 판본 5에서 이미 저장된 실행 기록은 `execution.process`만 갖고 있을 수 있다. 읽는 곳이 옛 기록을 다루어야 하는지 확인한 뒤 적용한다. `model_runner.verified_native_final`의 식별 비교(`model_runner.py:356-366`)는 정수와 십진 문자열을 모두 받으므로, 정본 위치를 바꾸어도 표현 차이로 깨지지 않는다. 보호 테스트: `tests/test_redesign_ENGINE.py`, `tests/test_currentness_recovery.py`
- 확신: 중간. 옛 기록의 존재 여부를 확인하지 않았다.
- 다른 영역: `record_schemas`(상태 영역), `activities.py`

#### RUN-04: 발사표 phase 전이가 여섯 곳의 문자열 대입으로 흩어져 있다
- 유형: 이음새중복
- 위치: `reserved`는 `do_math/launch.py:12`에서 쓴다. `dispatched`는 `do_math/engine.py:726`, `:3534`, `do_math/scheduled_operator.py:502`에서 쓴다. `finished`/`not_started`는 `do_math/scheduler.py:27`, `do_math/lifecycle_engine.py:1116-1117`, `do_math/scheduled_operator.py:572-573`에서 쓴다. 해석하는 곳은 `do_math/launch.py:21`, `:44`, `:57-63`이다.
- 현상: `launch.py`는 phase 값을 검증하고 해석하지만 전이 함수는 없다. 호출자들이 `ticket['phase'] = ...`를 직접 쓴다. `'not_started' if result.get('launch_not_created') is True else 'finished'`라는 같은 규칙이 `scheduler.py:27`과 `scheduled_operator.py:572-573`에 두 번 적혀 있다. 반면 `lifecycle_engine.py:1116-1117`은 `not_started`가 아니면 `finished`로 덮는 다른 식을 쓴다.
- 제안: `launch.py`에 `mark_dispatched(ticket)`와 `mark_returned(ticket, result)`를 둔다. `mark_returned`는 허용 전이(`reserved`/`dispatched` → `finished`/`not_started`)만 받는다. 여섯 곳의 대입을 이 둘로 바꾼다.
- 동작: 보존
- 실익: phase 문자열 리터럴이 `launch.py` 한 모듈에 모인다. 반환 장벽(`termination_confirmed`)이 해석하는 값과 쓰는 값의 정본이 같아진다.
- 위험과 보호: `lifecycle_engine.py:1116`은 `not_started`를 보존하는 조건이 다르다. 합칠 때 이 조건을 인자로 받아 보존한다. 보호 테스트: `tests/test_session_scheduler.py`의 `test_slot_waits_for_actual_named_job_termination`
- 확신: 높음
- 다른 영역: `scheduler.py`, `scheduled_operator.py`

#### RUN-05: "예약이 정산되었는가" 판정이 열 곳 넘게 각자 표현되고, 그중 하나는 없는 필드를 읽는다
- 유형: 이음새중복
- 위치:
  - 실행별 held 예약 판정: `do_math/activities.py:202-203`, `do_math/decision_engine.py:51-53`, `do_math/engine.py:1676-1677`, `do_math/engine.py:2632-2633`, `do_math/governance_engine.py:366-367`, `:386-387`, `do_math/review_engine.py:382-383`
  - 인스턴스 정지 판정(끝나지 않은 실행 없음 + held 예약 없음): `do_math/lifecycle_engine.py:171-173`, `do_math/maintenance_gate.py:45-47`, `do_math/governance_engine.py:57-59`
  - 없는 필드를 읽는 판정: `do_math/engine.py:1697-1698`
  - 정본 쓰기: `do_math/session_slots.py:280-286`(`release`가 예약을 `settled`로 바꾸고 `local_termination='confirmed'`를 함께 기록)
- 현상: 예약 기록의 상태 필드는 `state`이고, 값은 `held`/`settled`다(`do_math/budget.py:271`, `:327`). 그런데 `engine.py:1697-1698`의 복구 판정은 `row.get("status") != "released"`로 거른다. 예약에는 `status` 필드가 없으므로 이 식은 소유 예약 전부를 참으로 센다. 지금은 `queued` 실행이 예약을 가질 수 없다. `acquire`가 예약 발행과 `starting` 전이를 한 후보 안에서 같이 하기 때문이다(`session_slots.py:216-231`). 그래서 이 오류는 결과를 바꾸지 않는다. 하지만 같은 판정을 문자열로 반복한 결과 어긋남이 이미 생겼다는 증거다.

  또 `local_termination == 'confirmed'`와 "held 예약 없음"은 같은 사실이다. `settle_reservation`의 유일한 호출자가 `release`이고, `release`가 두 기록을 함께 쓰기 때문이다(`session_slots.py:283-286`, grep `settle_reservation`). 그런데 `engine.py:1675-1677`과 `:2631-2633`은 두 조건을 모두 검사한다.
- 제안: `session_slots.py`에 다음 두 함수를 둔다.
  - `held_reservations(runtime, owner_ids=None) -> list`
  - `quiescence(runtime) -> {'pending_executions': [...], 'held_reservations': [...]}`

  모든 끝점이 이 두 함수를 쓴다. `engine.py:1697`은 `held_reservations(runtime, [eid])`로 바꾼다. 이중 조건은 하나로 줄인다. 정본은 예약 원장이 권장되며, `local_termination`은 표시용으로만 둔다.
- 동작: 보존. `engine.py:1697`은 도달 가능한 상태에서 결과가 같다.
- 실익: 추정 20행 감소. 예약 상태 문자열(`'held'`)이 8개 모듈에서 1개 모듈로 줄어든다. 잘못된 필드 이름 같은 결함이 다시 생길 경로가 없어진다.
- 위험과 보호: `governance_engine.py:57-59`는 프로세스 내부 플래그(`_executor_running`, `_live_execution_ids`)도 함께 본다. 그 부분은 호출자에 남긴다. 보호 테스트: `tests/test_initialization_efficiency.py`의 `test_quiescence_does_not_release_unknown_execution_or_user_pause`, `test_public_maintenance_fence_survives_restart_and_preserves_user_pause`, `tests/test_redesign_ACTIVITIES.py`의 `test_queued_recovery_does_not_discard_a_held_reservation`
- 확신: 높음. 검색식은 `grep -rn "'held'\|\"held\"" do_math | grep state`와 `grep -rn "local_termination" do_math`다.
- 다른 영역: `activities.py`, `decision_engine.py`, `governance_engine.py`, `review_engine.py`, `engine.py`

#### RUN-06: 공급자 결과 반영과 모델 잠금 위반 기록이 엔진과 설치 복구에 각자 있다
- 유형: 이음새중복
- 위치: 공급자 결과는 `do_math/provider_engine.py:108-116`(`_provider_outcome`)와 `do_math/scheduled_operator.py:527-533`에 있다. 모델 잠금 위반은 `do_math/provider_engine.py:11-15`(`_pause_for_model_policy`)와 `do_math/scheduled_operator.py:541-545`에 있다.
- 현상: 러너 결과에서 공급자 게이트 입력을 만드는 규칙이 두 곳에 글자 그대로 복제되어 있다. 규칙은 세 가지다. `error_kind == "provider_limit"`일 때만 `failure`를 넘긴다. `status == "completed" or turn_failed or turn_completed`면 응답을 관찰한 것으로 본다. 설정의 재시도 간격 두 값을 넘긴다. 모델 잠금 위반 기록 `{"execution_id", "assigned_model", "reported_models"}`와 `status="paused"` 전이도 두 곳에 있다. 엔진 쪽은 `closed`/`completed`이면 `paused`로 바꾸지 않는데, 설치 복구 쪽은 이 조건이 없다.
- 제안: `SessionSlots.provider_result_from_run(execution_id, result, config)`를 정본으로 둔다. 이 함수는 러너 결과를 받아 `failure`와 `response_observed`를 스스로 추출한다. provider는 `execution.capacity.provider`에서 읽는다(RUN-13 참조). 모델 잠금 위반 기록은 `provider_engine`의 함수를 모듈 함수 `record_model_policy_violation(runtime, eid, model, result)`로 꺼내 두 곳이 같이 쓴다.
- 동작: 보존. 설치 복구 경로는 이미 `status in {paused, closed, completed}`에서 진입하지 않으므로(`scheduled_operator.py:395`) 조건 차이가 결과를 바꾸지 않는다.
- 실익: 추정 12행 감소. "응답 관찰"의 정의가 하나가 된다. 공급자 게이트가 `checking`에서 `available`로 가는 판정이 이 정의에 달려 있으므로, 두 경로가 다르게 판정할 여지가 없어진다.
- 위험과 보호: 보호 테스트: `tests/test_provider_wait.py`의 `test_late_success_does_not_release_a_newer_rejection`, `test_probe_is_reconciled_only_after_confirmed_local_termination`, `tests/test_diagnosed_installation_recovery.py`
- 확신: 높음
- 다른 영역: `scheduled_operator.py`

### 슬롯·예산 계산

#### RUN-07: 슬롯 사용량 계산이 세 곳에 있고, 상태 표시와 배정 판정이 다른 답을 낸다
- 유형: 이음새중복, 문제 발생 여지
- 위치:
  - 배정 판정: `do_math/budget.py:278-292`(`_check_concurrency`, `total_slots` 포함)와 `do_math/session_slots.py:140-189`(옛 판본 예약을 현재 제약으로 재기준화)
  - 상태 표시: `do_math/session_slots.py:339-358`(`snapshot`, `total_slots` 없음)
  - 상태 검사: `do_math/state_checks.py:357-371`
  - 제약 저작: `do_math/execution_profiles.py:193-196`(`total_slots = work + operations`)
  - 문서: `references/모델과-실행예산.md:23`, `:109`
- 현상: 세 계산이 서로 다른 식을 쓴다.
  - 배정 판정은 제약 ID로 재기준화한 뒤 `reserved - returned`를 풀별과 전체로 합산한다.
  - 상태 표시는 `held` 행의 `reserved`를 모델 이름으로 묶어 풀별로만 합산한다.
  - 상태 검사는 재기준화 없이 제약 ID별로 합산한다.

  `total_slots`는 저작 시 늘 `work + operations`다. 그래서 두 풀이 모두 한도 안에 있으면 전체 검사는 결과를 바꾸지 않는다. 하지만 한 풀의 한도를 현재 점유보다 낮추면 결과가 달라진다. 실측 조건은 `work_slots=3`, `operations_slots=1`, `total_slots=4`이고, 운영 예약 3건과 작업 예약 1건이 보유 중이다. 이때 작업 요청 1건은 `BudgetConflict`로 거부된다(아래 명령). 같은 상태에서 `snapshot`은 작업 풀을 `limit 3, used 1, available 2`로 표시한다(`session_slots.py:347`, `:357`). 사용자는 작업 슬롯이 비어 있다고 보지만 배정은 대기한다. 이 결과는 문서 `:23`의 "운영과 작업은 모델이 같아도 별도 용량이다. 작업에 남은 운영 슬롯을 자동으로 빌려 주거나 그 반대로 처리하지 않는다"와도 어긋난다. 운영 풀의 초과 점유가 작업 풀 용량을 잠식하기 때문이다. 다만 `:109`의 "한도를 현재 점유보다 낮추면 해당 모델의 새 배정을 기다리게 한다"는 모델 전체의 대기로도 읽힌다.

  실측 명령은 `python -c` 한 줄로, `plan_reservations`에 위 제약과 예약 4건을 넣고 작업 요청 1건을 계산했다. 출력은 `conflict concurrency capacity unavailable: C`였다.
- 제안: 두 단계로 나눈다.
  1. (동작 보존) `budget.py`에 `outstanding(reservations, constraints, *, model, budget_kind=None)` 하나를 두고 배정·표시·상태 검사가 모두 이 함수를 쓴다. 옛 판본 예약의 재기준화(`session_slots.py:140-189`)는 동시성 예약을 같은 모델 이름끼리, 호스트 예약을 같은 `host_id`끼리 묶어 합산하는 것과 결과가 같다. 따라서 합산 키를 제약 ID 대신 동시성 예약은 모델 이름, 호스트 예약은 `host_id`로 바꾸면 재기준화 코드 약 30행이 사라진다.
  2. (사용자 결정) `total_slots`의 의미를 정한다. 선택지는 둘이다.
     - (a) 문서 `:23`을 따라 전체 검사를 없애고 풀별 검사만 둔다.
     - (b) 전체 검사를 유지하고, 문서와 `snapshot`에 "한 풀의 초과 점유가 다른 풀을 막을 수 있다"를 반영한다.
- 동작: 1은 보존, 2는 변경. (a)를 택하면 한도를 낮춘 뒤의 작업·운영 배정이 서로 막지 않는다. (b)를 택하면 표시가 바뀐다.
- 실익: 추정 40~50행 감소(재기준화, 표시 합산, 상태 검사 합산). 표시와 판정의 불일치가 사라진다.
- 위험과 보호: 재기준화 보호 테스트는 `tests/test_session_scheduler.py`의 `test_old_profile_cannot_bypass_a_new_zero_capacity_limit`이다. 풀 분리 보호 테스트는 `tests/test_budget.py`의 `test_shared_profile_refs_reserve_atomically_and_separate_work_from_operations`와 `tests/test_session_scheduler.py`의 `test_shared_capacity_separate_pools_and_reusable_slots_are_published_together`다. 한도를 낮춘 뒤 다른 풀이 막히는지를 고정한 테스트는 없음.
- 확신: 1은 높음, 2의 결함 판정은 중간. 문서 `:109`의 의도를 확정할 수 없다.
- 다른 영역: `state_checks.py`(상태 영역), `references/모델과-실행예산.md`(문서 영역)

#### RUN-13: 배정 사전 확인(`admission_check`)이 실제 배정을 가짜 원장에서 통째로 재실행하고, 배정 인자가 고정 프로필과 중복된다
- 유형: 운영비용, 복잡성
- 위치: `do_math/session_slots.py:66-82`(`admission_check`), `:99-238`(`acquire`), `:116-130`(인자 동일성 검사), `:218-219`(발사표 생성). 호출하는 곳은 `do_math/scheduler.py:525`, `:541`(대기 요청마다, 주인 루프 `OWNER_POLL_SECONDS=0.25` 한 바퀴마다)이다. 중복 인자를 넘기는 곳은 `do_math/provider_engine.py:94-95`, `do_math/engine.py:717`, `do_math/scheduled_operator.py:498`이다.
- 현상: `admission_check`는 원장 사본과 가짜 실행을 만들어 `acquire`를 그대로 실행한다. 그래서 순수 계산에 필요 없는 부수 작업이 매번 일어난다.
  - `launch.ticket`: `uuid4`, 그리고 `windows_job.owner_identity`의 Win32 호출 `GetProcessTimes`와 `ProcessIdToSessionId`
  - `bind_execution`
  - `transition_execution`
  - `deepcopy`

  실측값은 빈 원장에서 호출 한 번에 1.3ms(`research_plan` 프로필)~3.9ms(`research_work` 프로필)이고, 그 안에서 `validate_profile`(내용 해시 재계산)을 5번 부른다. 또 `acquire(execution_id, pool, model, provider=...)`의 `pool`·`model`·`provider`는 고정 프로필에서 바로 얻을 수 있는 값이다. `acquire`는 이 인자들을 프로필과 비교해 다르면 예외를 내는 일만 한다(`:116-117`, `:127-130`).
- 제안: `acquire`를 둘로 나눈다. 순수 계산 `_admission(profile, current_time) -> (plan | wait)`은 공급자 게이트, 제약 결정, `plan_reservations`까지 맡는다. 그 결과를 원장에 쓰는 부분이 나머지다. `admission_check`는 순수 계산만 부른다. `acquire`의 `pool`·`model`·`provider` 인자는 없애고 프로필에서 읽는다. `provider_result`의 `provider` 인자도 `execution.capacity.provider`와 같은지 비교만 하므로(`:300-301`) 같이 없앤다.
- 동작: 보존
- 실익: 측정값으로 대기 요청 하나가 주인 루프 한 바퀴마다 1.3~3.9ms를 쓰고, 추정으로 부수 작업을 빼면 그 대부분이 사라진다. Win32 호출 2회와 `uuid4`도 매 확인마다 없어진다. 인자 동일성 검사 약 8행과 그 호출부 인자도 사라진다.
- 위험과 보호: 문서가 요구하는 "사전 확인 뒤 최신 상태 재검사"는 `acquire`가 순수 계산을 다시 부르는 구조로 유지된다(보존 판정 1 참조). 보호 테스트: `tests/test_session_scheduler.py`의 `test_unavailable_assigned_model_waits_without_spending_other_model_slots`, `test_blocked_high_priority_work_does_not_block_independent_low_model_work`
- 확신: 높음
- 다른 영역: `scheduler.py`, `scheduled_operator.py`

#### RUN-14: `budget.py`의 재실행(replay) 분기와 상수 입력 검사는 운영 경로에서 도달하지 않는다
- 유형: 죽은코드, 불필요기능
- 위치: `do_math/budget.py:30-31`, `:79-87`(예약 재실행), `:141-144`(정산 재실행), `:181-194`(요청 상수 검사). 유일한 운영 호출자는 `do_math/session_slots.py:197-203`, `:283-284`다.
- 현상: 운영 경로에서 `plan_reservations`와 `settle_reservation`을 부르는 곳은 `session_slots` 하나뿐이다(grep `plan_reservations\|settle_reservation`, 나머지 호출은 `tests/test_budget.py`).
  - 예약 ID는 실행 ID에서 만든다(`session_slots.py:190-196`). 그리고 `acquire`는 `capacity`가 이미 있는 실행을 거부한다(`:120-123`). 그래서 같은 ID로 다시 예약하는 재실행 분기에 도달하지 않는다.
  - `release`는 이미 `confirmed`이면 일찍 돌아간다(`:264-265`). 그래서 정산 재실행 분기에도 도달하지 않는다.
  - 요청의 `owner_kind="execution"`, `purpose="normal"`, `reobserve`는 호출자가 상수로 넣는다(`session_slots.py:197-199`). `budget.py:181-189`는 이 상수를 다시 검사한다.
- 제안: `BudgetReplayConflict`, `ReservationPlan.replayed`, `SettlementPlan.replayed`, 재실행 분기, 상수 검사를 지운다. 이미 보유한 예약 기록의 검증(`_validate_existing_records`)은 이번 조사에서 판정하지 않았다. 상태 검사(`state_checks.py:349-350`)가 모든 적재에서 실행되는지 확인하지 않았기 때문이다.
- 동작: 보존
- 실익: 추정 25행 감소. 제거되는 테스트는 `tests/test_budget.py`의 `test_exact_request_replays_but_changed_request_with_same_id_is_rejected` 하나이고, `test_settlement_is_exactly_once_and_requires_full_accounting`의 재실행 단언 일부도 제거된다.
- 위험과 보호: 향후 재예약이 필요한 경로(예: 예약만 먼저 발행하는 설계)를 도입하면 다시 필요하다. 보호 테스트: `tests/test_budget.py` 전체
- 확신: 높음
- 다른 영역: 없음

#### RUN-15: `SessionSlots.configure`는 유일한 호출자가 방금 한 일을 다시 한다
- 유형: 이음새중복, 운영비용
- 위치: `do_math/session_slots.py:84-97`(`configure`)과 `do_math/governance_engine.py:64-73`(유일한 운영 호출자)이다. 관련 호출은 `do_math/engine.py:220-222`(`validate_config`의 `build_profiles`)와 `do_math/governance_engine.py:49`, `:60`(`validate_config` 2회)이다.
- 현상: `governance_engine`은 `build_profiles(candidate)`의 결과로 `execution_profiles`, `capacity_constraints`, `role_profile_refs`, `host_capacity_ref`를 반영한다(`:64-72`). 바로 다음 줄(`:73`)에서 `configure`가 같은 설정으로 `build_profiles`를 다시 부르고 같은 네 필드를 다시 반영한다(`session_slots.py:87-97`). `configure`의 호스트 제약 검사(`:88-89`)는 이미 갱신된 `host_capacity_ref`와 비교하므로 늘 통과한다. `host_resources`가 있으면 `validate_config`도 `build_profiles`를 부르므로(`engine.py:220-222`), 설정 변경 한 번에 전체 판본 생성이 최대 4번 일어난다. 전체 판본 생성 1회의 실측값은 38ms다.
- 제안: `SessionSlots.configure`와 `governance_engine.py:73`의 호출을 지운다. 판본 반영은 `governance_engine`에만 둔다. `initialize`(`engine.py:233-235`)도 같은 반영(`instance.update(profiles)`)을 하므로, `apply_editions(instance, editions)` 하나로 두 곳을 합친다.
- 동작: 보존
- 실익: 약 14행 감소. 설정 변경마다 `build_profiles` 1회(실측 38ms)가 줄어든다.
- 위험과 보호: 테스트 4곳이 `configure`를 직접 부른다(`tests/test_host_resources.py:218`, `tests/test_redesign_PROFILES.py:290`, `tests/test_session_scheduler.py:85`, `:95`). 이 테스트들은 공개 설정 경로로 옮겨야 한다.
- 확신: 높음
- 다른 영역: `governance_engine.py`

#### RUN-16: 모델 선택이 채택된 역할 프로필 목록을 설정에서 매번 다시 만든다
- 유형: 이음새중복, 운영비용
- 위치: 다시 만드는 곳은 `do_math/model_policy.py:137-141`이다. 저장된 채택 목록(`instance["role_profile_refs"]`)을 쓰는 곳은 `do_math/engine.py:637`, `do_math/scheduler.py:256`, `do_math/scheduled_operator.py:430`이다. 호출 빈도가 높은 곳은 `do_math/lifecycle_engine.py:964`(준비 상태 갱신 때 과제마다), `do_math/scheduler.py:212`(배정 때마다)다.
- 현상: 같은 개념(현재 채택된 역할 판본)을 두 원천에서 얻는다. `selection`은 `build_profiles(config, roles={role})`로 다시 만들고, 엔진의 `_execution_profile`은 저장된 `role_profile_refs`를 쓴다. 두 값은 설정과 판본을 같은 전이에서 저장하므로(`governance_engine.py:64-72`) 정상 상태에서 같다. 하지만 설치 갱신으로 판본 본문(예: 관찰 규칙 계약)이 바뀌면 다시 만든 ID가 등록 목록에 없어 `select_profile`이 실패한다. 반면 엔진 경로는 저장 목록으로 계속 동작한다. 역할 하나를 다시 만드는 데 3.3ms(`research_plan`)~6.8ms(`research_work`)가 든다(실측).
- 제안: `selection`이 `profiles`와 함께 채택 목록을 받아 `role_profile_refs[role]`을 쓰게 한다. 호출자는 `instance`에서 두 값을 같이 넘긴다.
- 동작: 보존. 정상 상태에서 결과가 같다. 판본 본문이 바뀐 설치 갱신 직후에는 저장 목록 기준으로 선택하게 된다.
- 실익: 선택 한 번당 3~7ms, 준비 상태 갱신에서는 대상 과제 수에 비례해 절약된다(추정). 채택 판본의 정본이 하나가 된다.
- 위험과 보호: 보호 테스트: `tests/test_session_scheduler.py`의 `test_role_floor_raises_low_assessment_and_unassessed_work_uses_high`, `test_model_assessments_flow_from_preparation_through_review_and_planning_to_execution`
- 확신: 중간. 설치 갱신 직후의 두 원천 차이는 코드 읽기로 추론했고 재현하지 않았다.
- 다른 영역: `context_store.py`, `decision_engine.py`, `input_recovery.py`, `cli.py`(같은 `selection`의 호출자)

### 공급자 대기와 재시도

#### RUN-08: 공급자 게이트의 개폐 판정이 세 가지 식으로 적혀 있다
- 유형: 이음새중복
- 위치: `do_math/session_slots.py:132`(배정 차단: `checking or waiting and retry_at > now`), `:334`(`due`: `waiting and retry_at <= now`), `do_math/provider_engine.py:165`(재큐: `available or due`), `do_math/scheduled_operator.py:267-270`(기동: `any due`)
- 현상: 세 식은 지금 서로 여집합으로 맞물린다. 하지만 게이트 상태가 하나 늘거나 `checking`의 만료 규칙이 생기면 네 곳을 함께 고쳐야 한다.
- 제안: `provider_wait.py`에 `gate_open(row, now) -> bool`을 둔다. `provider_snapshot`은 `due` 대신 또는 함께 `open`을 게시한다. 네 곳은 그 값을 읽는다.
- 동작: 보존
- 실익: 판정 정본 하나. 약 5행 감소.
- 위험과 보호: 보호 테스트: `tests/test_provider_wait.py`의 `test_restriction_blocks_both_pools_and_survives_another_owner`, `test_two_real_processes_admit_one_probe`
- 확신: 높음
- 다른 영역: `scheduled_operator.py`

#### RUN-09: 공급자 한도 대기에 두 경로가 있다
- 유형: 복잡성(같은 일을 하는 두 경로)
- 위치: 경로 A(실행 뒤 한도 실패)는 `do_math/provider_engine.py:138-151`(`_hold_provider_action`: `waiting_actions`에 보관)과 `:153-173`(`_retry_provider_actions`: 게이트가 열리면 재큐)이고, 호출은 `do_math/engine.py:1642`, `do_math/scheduler.py:598`이다. 경로 B(시작 전 게이트 닫힘)는 `do_math/session_slots.py:131-137`과 `do_math/scheduler.py:525-545`(대기열에 `dispatch_wait.kind='provider_limit'`로 남기고 매 바퀴 재확인)다. 외부 기동 판정은 `do_math/scheduled_operator.py:268-271`이다.
- 현상: 같은 사실(이 공급자의 게이트가 열릴 때까지 기다림)을 두 기록 방식으로 다룬다. A는 `waiting_actions`(`failure_kind='provider_limit'`)와 전용 재큐 함수를 쓴다. B는 대기열에 요청을 남겨 두고 배정 사전 확인이 게이트를 본다. 외부 기동 판정도 두 기록을 모두 확인해야 한다(`pending_actions or failure_kind == 'provider_limit'`).
- 제안: 한도 실패 뒤의 요청도 B처럼 대기열에 되돌린다. 이때 `continuation_of`, `recovery`, 그리고 `dispatch_wait`(게이트 정보)를 붙인다. `_retry_provider_actions`와 `waiting_actions`의 `provider_limit` 종류를 없앤다.
- 동작: 변경. 상태 표시에서 한도 대기 요청이 `waiting_actions` 항목 대신 대기열 요청의 `dispatch_wait`(`kind='provider_limit'`)로 보인다. 인스턴스 상태 값은 지금과 같이 `waiting`이 된다. 대기열이 배정 불가 요청만 가질 때 `scheduler.py:634-639`는 모든 대기가 `capacity`/`host_capacity`인 경우에만 `capacity_waiting`을, 그 밖에는 `waiting`을 쓰기 때문이다. 운영 점검 AI의 입력이 `waiting_actions`를 읽는지는 미확인이며, 읽는다면 입력이 달라진다.
- 실익: 추정 30행 감소(`_hold_provider_action`, `_retry_provider_actions`, 기동 판정의 한 갈래). 대기 경로가 하나가 된다.
- 위험과 보호: 실패 실행의 계보(`continuation_of`)와 활동 대기(`wait_for`)를 옮겨야 한다. 보호 테스트: `tests/test_redesign_ACTIVITIES.py`의 `test_provider_mixin_records_structured_waits_on_admission_and_failure`, `tests/test_six_connections.py`(공급자 결과 게시)
- 확신: 낮음. 상태 표시와 운영 점검 입력의 하류 영향을 전수 확인하지 않았다.
- 다른 영역: `scheduled_operator.py`, `reporting.py`, 운영 점검 역할 입력(`context_store.py`)

#### RUN-10: `activity_wait` 필드는 계산해 저장하지만 읽는 곳이 없다
- 유형: 파생상태, 불필요기능
- 위치: 쓰는 곳은 `do_math/provider_engine.py:99-103`, `:144-149`이고, 생성 함수는 `do_math/provider_wait.py:33-58`(`provider_wait_disposition`), 스키마는 `do_math/record_schemas/domains.py:459-460`이다.
- 현상: `dispatch_wait`와 `waiting_actions` 항목에는 이미 게이트의 `retry_at`이 들어 있다. `activity_wait`는 같은 `retry_at`을 `retry_time`으로 다시 계산한 사본이다. 미래 시각이면 그대로 돌려주므로 같은 값이 된다. 여기에 `retry_at_timestamp`와 `attempt`가 더해진다. 배정 경로는 `attempts=1`을 상수로 넣으므로(`provider_engine.py:100`) `attempt`는 실제 시도 횟수와 무관하다. 제품 코드에서 `activity_wait`를 읽는 곳은 없다(grep `activity_wait`: 쓰는 곳 두 곳, 스키마, 테스트 2파일).
- 제안: `provider_wait_disposition`과 `activity_wait` 쓰기를 지운다. 스키마 항목은 판본 5에 이미 저장된 기록이 통과하도록 남기거나 선택 필드로 둔다.
- 동작: 보존. 저장 기록에서 필드 하나가 빠진다.
- 실익: 약 35행 감소(함수 26행, 호출부 약 10행). 틀린 `attempt` 값이 기록되지 않는다.
- 위험과 보호: 테스트 단언을 고쳐야 한다. `tests/test_provider_wait.py`의 `test_engine_provider_wait_disposition_survives_real_git_storage`(`:150-152`), `test_empty_nonmapping_failure_is_rejected`, `tests/test_redesign_ACTIVITIES.py`의 `test_provider_wait_is_a_wait_record_not_a_capacity_claim`, `test_provider_mixin_records_structured_waits_on_admission_and_failure`(`:247`, `:251`)
- 확신: 높음
- 다른 영역: `record_schemas`

#### RUN-11: 재시도 간격과 마무리 예고의 기본값이 함수 기본 인자에 복제되어 있다
- 유형: 이음새중복
- 위치: 정본은 `do_math/engine.py:105-106`(`DEFAULT_CONFIG`: 300, 7200, 60)이다. 복제는 `do_math/session_slots.py:294`(300, 7200), `do_math/provider_wait.py:26`, `:34`(300, 7200), `do_math/execution_window.py:14`(60)에 있다.
- 현상: 운영 호출자는 모두 설정값을 명시해 넘긴다. `provider_engine.py:102-103`, `:115`, `:148-149`와 `scheduled_operator.py:532-533`이 그렇다. 함수 기본값을 쓰는 곳은 테스트뿐이다(`tests/test_provider_wait.py:130`, `:167`, `:176-177`, `tests/test_redesign_PROFILES.py:580`, `:590`, `tests/test_six_connections.py:362`). 설정 기본값을 바꾸면 테스트가 옛 값으로 계속 통과한다.
- 제안: 기본 인자를 없애 필수 키워드로 만든다. `notice_seconds`는 `config["finish_notice_seconds"]`를 읽는다. 엔진이 넘기는 `config`는 인스턴스 설정과 프로필 설정의 합이므로(`engine.py:3271`) 키가 있다. 테스트는 `DEFAULT_CONFIG`를 넘긴다.
- 동작: 보존
- 실익: 수치 사본 7개 제거.
- 위험과 보호: 테스트 호출 약 8곳을 수정해야 한다. `tests/test_execution_window.py`의 설정 픽스처에 `finish_notice_seconds`가 있는지 확인해야 한다.
- 확신: 높음
- 다른 영역: 없음

#### RUN-12: 모델·슬롯·재시도 기본값이 문서 네 곳에 다시 적혀 있고 대조 장치가 없다
- 유형: 이음새중복(코드 상수와 문서)
- 위치:
  - 코드: `do_math/model_policy.py:7-16`(`MODELS`, `LIMITS`, `ROLE_TIERS`), `do_math/engine.py:90-91`, `:104-106`
  - 문서: `references/모델과-실행예산.md:13-19`(표), `:39`(역할 하한), `:115`(`claude_only_assigned_model` 기본 false), `:119`(300/7200), `SKILL.md:45`, `README.md:95`, `:105-108`, `references/CLI-실행-계약.md:177`, `:200-203`, `:952`(60)
  - 테스트: `tests/test_session_scheduler.py:105-108`(코드 값을 리터럴로 고정)
- 현상: 이번 조사 시점에는 문서와 코드의 값이 모두 일치한다. 하지만 같은 값이 코드 1곳, 테스트 1곳, 문서 5개 파일 9곳에 따로 적혀 있다. 문서를 읽어 코드와 대조하는 테스트는 없다(grep `모델과-실행예산\|gpt-6-astra\|7200` in `tests/`: `test_reading_map.py`는 문서 경로만 본다).
- 제안: 사용자 결정 사항이다. 가벼운 순서로 세 가지가 있다.
  - (a) 수치 정본 문서를 `references/모델과-실행예산.md` 하나로 정하고, `SKILL.md`·`README.md`·`CLI-실행-계약.md`는 수치 대신 링크만 둔다. 설정 예시 블록은 남긴다.
  - (b) (a)에 더해, 그 문서의 표·재시도 문장을 파싱해 `model_policy`·`DEFAULT_CONFIG`와 비교하는 테스트 하나를 둔다.
  - (c) 현상을 유지한다.
- 동작: 보존
- 실익: (a)로 문서 사본이 9곳에서 약 4곳으로 준다. (b)로 어긋남을 테스트가 잡는다.
- 위험과 보호: `SKILL.md`의 요약은 AI가 첫 적재에서 읽는 정보다. 수치를 빼면 독자가 링크를 따라가야 한다. 보호 테스트는 없음.
- 확신: 중간. 이 중복을 줄일지는 문서의 독자 설계에 달렸다.
- 다른 영역: 문서 영역

### 구조 정리

#### RUN-17: 배정 대기 종류(`dispatch_wait.kind`)의 어휘가 다섯 모듈에 리터럴로 흩어져 있다
- 유형: 이음새중복
- 위치: 생산하는 곳은 `do_math/session_slots.py:134`, `:166`, `:205-207`(`provider_limit`, `capacity`, `host_capacity`, `resource_unclassified`)이다. 소비하는 곳은 `do_math/reporting.py:74-75`, `do_math/scheduler.py:636`, `do_math/engine.py:1578`, `do_math/governance_engine.py:115-116`이다.
- 현상: 소비자마다 다른 부분집합을 적는다. 자원 대기로 보는 집합은 `reporting`이 4종, `governance_engine`이 3종, `scheduler`와 `engine`이 2종이다. 각 부분집합의 뜻(표시할 대기, 설정 변경 뒤 풀어 줄 대기, `capacity_waiting` 상태를 만드는 대기)은 코드에 이름으로 드러나지 않는다.
- 제안: `session_slots.py`에 의미별 상수를 둔다. 예를 들어 `RESOURCE_WAITS = {'capacity', 'host_capacity', 'resource_unclassified'}`, `SLOT_WAITS = {'capacity', 'host_capacity'}`다. 소비자는 이 상수를 가져다 쓴다.
- 동작: 보존
- 실익: 새 대기 종류를 추가할 때 고칠 곳이 한 곳이 된다.
- 위험과 보호: 보호 테스트: `tests/test_session_scheduler.py`의 `test_live_operations_can_run_when_work_is_full_and_step_limit_is_reached`
- 확신: 높음
- 다른 영역: `reporting.py`, `governance_engine.py`, `scheduler.py`

#### RUN-18: `SessionSlots` 캐시(`self._slots`)에 세 가지 신선도 정책이 공존한다
- 유형: 복잡성, 문제 발생 여지
- 위치: `do_math/provider_engine.py:65-76`(런타임 동일성 검사 뒤 재사용), `:78-84`(동일성 검사 없이 재사용), `do_math/engine.py:909-911`, `:1542-1544`(저장·적재 뒤 재결합), `do_math/scheduler.py:198-200`(검사 없이 재사용), `:548`, `:660`(설정·해제)
- 현상: `SessionSlots`는 `runtime`과 `instance`를 감싸는 얇은 뷰다. 가진 상태는 직전 배정의 `admission_wait` 하나이고, 이 값은 같은 호출 안에서만 읽힌다. 그런데 엔진은 이 뷰를 캐시하고, 신선도를 곳마다 다르게 관리한다. `_provider_slots`는 동일성을 검사하고, `_provider_status`와 `_session_resources`는 검사하지 않는다. 대신 `_save`와 `status`가 수동으로 재결합한다. 다른 적재 지점(`scheduler.py:122`의 오류 경로 재적재, `lifecycle_engine.py:596`의 거부 후보 보존)에서는 재결합이 없다. 그래서 그 뒤의 `_provider_status`가 옛 `provider_waits`를 읽을 수 있다.
- 제안: 캐시를 없애고 사용할 때마다 `SessionSlots(self.runtime, self.instance)`를 만든다. 재결합 코드(`engine.py:909-911`, `:1542-1544`)와 동일성 검사를 지운다.
- 동작: 보존
- 실익: 약 15행 감소. 옛 원장을 읽을 경로가 사라진다.
- 위험과 보호: 테스트 8개 파일이 `engine._slots`에 가짜 객체나 실제 뷰를 주입한다(grep `\._slots\b` in `tests/`). 예를 들어 `tests/test_redesign_ACTIVITIES.py:236`은 가짜 `Slots()`를 넣는다. 이런 주입은 생성 함수를 바꿔치는 방식으로 옮겨야 한다.
- 확신: 중간. 옛 원장 읽기가 실제로 잘못된 판정으로 이어지는 경우는 재현하지 않았다.
- 다른 영역: 테스트 영역

#### RUN-19: 운영 처분의 구조 규칙이 JSON 스키마와 수신 검사기에 따로 적혀 있고, 이미 다르다
- 유형: 이음새중복, 생산자자기확인부재
- 위치: 생산자 스키마는 `do_math/contracts.py:159-171`(`disposition_schema`, docstring: "Field names match operational_dispositions.validate_disposition")다. 수신 검사기는 `do_math/operational_dispositions.py:13-67`(`_REQUIRED`, `validate_disposition`)이다. 수신 검사기를 쓰는 곳은 `do_math/submission.py:729-732`, `do_math/engine.py:4353`, `do_math/state_checks.py:486-488`, `do_math/record_schemas/__init__.py:359`, `do_math/repair_execution.py:215`이다.
- 현상: 필드 집합, 비지 않은 문자열, `basis_refs`의 중복 금지, `task_state` 열거, `next_review` 형태가 두 곳에 두 번 표현되어 있다. 이미 두 가지가 다르다.
  - 공백만 있는 문자열: 스키마는 `TEXT = {"minLength": 1, "pattern": "\\S"}`(`contracts.py:120`)로 거부하고, 검사기는 `not disposition[key]`만 보므로 수락한다. 실측으로 `next_owner=' '`인 처분은 `validate_disposition` 수락, `jsonschema.validate(d, disposition_schema())` 거부였다.
  - `repair_target`의 `installation:` 접두: 검사기만 요구한다(`operational_dispositions.py:49-50`). 그래서 생산자(운영 점검 AI)는 스키마로 이 조건을 미리 알 수 없고, 제출 뒤 반려를 받는다.
- 제안: `validate_disposition`을 `jsonschema.validate(disposition, disposition_schema())`와 스키마로 표현할 수 없는 의미 검사로 바꾼다. `_REQUIRED`와 필드별 수동 검사는 지운다. `repair_target`에는 스키마에 `"pattern": "^installation:"`을 넣어 생산자가 제출 전에 같은 조건을 알게 한다.
- 동작: 변경. 공백만 있는 문자열을 가진 처분이 수신에서 거부된다. 판본 5에 이미 저장된 처분 가운데 이런 값이 있으면 상태 검사(`state_checks.py:488`, `record_schemas/__init__.py:359`)가 실패하게 된다.
- 실익: 약 30행 감소. 생산자와 수신자가 같은 조건을 쓴다.
- 위험과 보호: 보호 테스트: `tests/test_redesign_OBSERVATION.py`의 `test_dispositions_are_validated_before_engine_application`
- 확신: 높음(차이는 실측). 저장된 처분에 공백 값이 있는지는 미확인이다.
- 다른 영역: `contracts.py`(계약·스키마 영역), `state_checks.py`, `record_schemas`

#### RUN-20: 상태 검사가 실행의 예약 목록을 제품 코드가 쓰지 않는 경로에서 읽고, 실행 슬롯 스키마에 쓰이지 않는 필드 7개가 있다
- 유형: 수신검사부재, 죽은코드
- 위치: `do_math/state_checks.py:345-348`, `do_math/session_slots.py:228-229`(실제 경로 `capacity.reservation_ids`), `do_math/record_schemas/schemas.py:115`, `do_math/record_schemas/domains.py:268-271`
- 현상: `state_checks`는 `execution.get('reservation_ids', [])`를 읽는다. 제품 코드는 예약 목록을 `execution['capacity']['reservation_ids']`에만 쓴다(grep `reservation_ids`). 그래서 "실행의 예약이 그 실행을 소유자로 가리키는가" 검사는 늘 빈 목록을 돌고 아무것도 검사하지 않는다. 또 `capacity` 스키마는 `acquired_at`, `released_at`, `profile_ref`, `model`, `budget_kind`, `release_evidence`, `state`를 허용한다. 하지만 `capacity`를 만드는 곳은 `session_slots.py:228` 하나이고, 거기서 쓰는 키는 `reservation_ids`, `provider`, `process`, `local_termination` 넷뿐이다(grep `acquired_at\|release_evidence`: 스키마 밖 0건).
- 제안: 검사 경로를 `execution.get('capacity', {}).get('reservation_ids', [])`로 고친다. 스키마의 top-level `reservation_ids`와 `capacity`의 미사용 7필드는 판본 5 저장 기록에 그 필드가 없음을 확인한 뒤 지운다.
- 동작: 변경. 검사가 실제로 작동하므로, 지금까지 드러나지 않은 불일치가 있으면 상태 검사가 결함을 보고하게 된다.
- 실익: 죽은 검사가 살아난다. 스키마 약 8개 항목이 줄어든다.
- 위험과 보호: 테스트 픽스처가 top-level `reservation_ids`를 쓰는지 확인해야 한다(미확인). 이 검사 경로를 덮는 테스트는 없음.
- 확신: 높음
- 다른 영역: `state_checks.py`, `record_schemas`(상태 영역)

#### RUN-21: 복구 시 "끝나지 않은 실행을 종료 장벽까지 몰아가는" 전이 해석이 두 층에 있고, 쓰이지 않는 관찰 종류가 남아 있다
- 유형: 이음새중복, 죽은코드
- 위치: `do_math/engine.py:1711-1715`(상태에서 초기 관찰 종류로), `do_math/provider_engine.py:31-44`(`_settle_recovered_execution`의 상태별 전이), `do_math/execution_lifecycle.py:163-203`(`recover_execution`), `do_math/provider_engine.py:49-58`(`capacity` 없는 분기)
- 현상: 엔진 복구는 먼저 상태를 관찰 종류로 바꾸어 `recover_execution`을 부른다. `starting`은 `start_unknown`, `running`은 `previous_engine_lost`, 체크포인트 중이면 `engine_restarted`, 그 밖은 `termination_barrier_pending`이 된다. 이어서 `_settle_recovered_execution`이 상태를 다시 보고 같은 목표(`stopping`/`terminating`을 거쳐 `ended`)로 전이한다. 같은 상태→전이 해석이 두 번 있다.

  `recover_execution`의 관찰 종류 가운데 두 개는 운영 경로에서 쓰이지 않는다. `no_substantive_action`(`:179-183`)은 테스트 2파일에서만 쓰이고, `checkpoint_deadline_elapsed`(`:190`)는 어디서도 쓰이지 않는다(grep 결과: 운영 0건). `_settle_recovered_execution`의 `local_termination_observed` 분기(`provider_engine.py:58`)가 읽는 필드는 제품 코드 어디에서도 쓰지 않는다(grep: 이 줄 1건). `activities.requeue_recovered_execution`(`activities.py:198`)도 운영 호출자가 없다(grep: 운영 0건, `tests/test_redesign_ACTIVITIES.py`만).
- 제안: `execution_lifecycle.py`에 `drive_to_termination(execution, *, at, reason)` 하나를 두고 두 층이 쓴다. 쓰이지 않는 관찰 종류 두 개, `local_termination_observed` 분기, `requeue_recovered_execution`을 지운다.
- 동작: 보존
- 실익: 추정 30행 감소.
- 위험과 보호: 복구 처분 문자열(`recovery_disposition`)을 `do_math/retention.py:174`가 읽는다. 남기는 관찰 종류의 처분 값은 바꾸지 않는다. 보호 테스트: `tests/test_redesign_ACTIVITIES.py`의 `test_recovery_changes_only_the_observed_execution`, `test_03_real_recovery_record_completion_round_trip`, `tests/test_currentness_recovery.py`
- 확신: 중간. `capacity` 없는 실행이 운영 경로에 없다는 판단은 `_register_execution`의 기계 배정(`engine.py:715-727`)과 AI 배정을 읽어 내렸다.
- 다른 영역: `activities.py`, `retention.py`

#### RUN-22: `lifecycle_engine.py` 안에서 종결 판정과 정지 표시가 반복되고, 없는 실행 상태 `'finished'`를 비교한다
- 유형: 복잡성, 죽은코드
- 위치:
  - 종결 판정 `status in {'closed','completed'} or permanently_closed`: `do_math/lifecycle_engine.py:115`, `:138`, `:165`, `:348`, `:499-500`, `:513`, `:904`
  - 정지 표시 반복문: `:124-126`, `:525-526`, `:875-877`
  - `'finished'`: `:125`, `:876`
- 현상: 같은 두 조건식이 7번 적혀 있다. 끝나지 않은 실행에 `stop_requested`를 붙이는 반복문은 3번 적혀 있다. 그중 두 곳은 `status not in {'ended', 'finished'}`로 비교하는데, 실행 상태에 `finished`는 없다(`execution_lifecycle.py:8`). `finished`는 활동의 상태다(`planning.py:349`).
- 제안: `_instance_closed()`와 `_request_stop_all(reason)` 두 메서드로 모은다. `'finished'`는 지운다.
- 동작: 보존
- 실익: 약 12행 감소.
- 위험과 보호: 보호 테스트: `tests/test_lifecycle_engine.py`
- 확신: 높음
- 다른 영역: 없음

#### RUN-23: 슬롯 반환이 같은 Job의 비었는지를 두 번 조회한다
- 유형: 운영비용
- 위치: `do_math/session_slots.py:268-275`, `do_math/launch.py:61-62`
- 현상: `release`는 `launch.termination_confirmed(ticket)`를 부른다. 이 함수는 `native_job`이면 `windows_job.named_job_empty(ticket['job_name'])`로 확인한다. `release`는 이어서 `identity`가 있으면 `named_job_empty(identity["job_name"])`를 다시 부른다. `started`가 `identity.job_name == ticket.job_name`을 보장하므로(`session_slots.py:247`) 같은 Job을 두 번 연다. `identity`가 있으면 발사표는 `native_job`이고 phase가 `not_started`일 수 없다. `not_started`는 Job 생성 전에 실패한 경우에만 쓰기 때문이다(`model_runner.py:117-126`, `scheduler.py:27`).
- 제안: 두 번째 조회(`:271-275`)를 지운다.
- 동작: 보존
- 실익: 반환마다 `OpenJobObjectW`와 `QueryInformationJobObject`가 1회씩 줄어든다. 5행 감소.
- 위험과 보호: 보호 테스트: `tests/test_session_scheduler.py`의 `test_slot_waits_for_actual_named_job_termination`
- 확신: 높음
- 다른 영역: 없음

#### RUN-24: 러너에 고정 프로필과 중복된 값을 넘기고, 제품 코드가 가짜 러너의 시그니처에 맞춰 인자를 고른다
- 유형: 이음새중복, 복잡성
- 위치: `do_math/engine.py:3038-3045`(`_runner_tools`), `do_math/execution_profiles.py:315-317`(`runner_tools`), `do_math/model_runner.py:68-71`(러너가 프로필 값으로 덮어씀), `inspect.signature` 분기(`do_math/engine.py:3039`, `:3606`, `:4625`, `do_math/lifecycle_engine.py:1392-1396`)
- 현상: 엔진은 `scholarly_server`와 `claude_only_assigned_model`을 프로필에서 꺼내 러너에 넘긴다. 러너는 프로필이 있으면 넘겨받은 값을 프로필과 비교한 뒤 프로필 값으로 덮어쓴다. 설치 복구 경로는 이 값을 넘기지 않고도 같은 결과를 얻는다(`scheduled_operator.py:512-517`). 또 엔진은 러너와 형식 검증기의 시그니처를 `inspect.signature`로 조사해 인자를 넣을지 정한다. 실제 러너(`model_runner.py:37-47`)와 검증기는 모든 인자를 받으므로, 이 분기는 좁은 시그니처의 테스트 가짜만을 위한 것이다.
- 제안: `_runner_tools`와 러너 쪽 비교를 지우고, 러너가 프로필에서 읽게 한다. `inspect.signature` 분기 4곳을 지우고, 테스트 가짜가 `**kwargs`를 받게 한다.
- 동작: 보존
- 실익: 약 25행 감소.
- 위험과 보호: `tests/test_redesign_ENGINE.py`의 `test_runner_tools_consume_the_selected_edition`, `tests/test_claude_adapter.py:69`가 `_runner_tools`를 직접 부른다. 가짜 러너·검증기를 쓰는 테스트 전반을 수정해야 한다.
- 확신: 중간. 가짜 시그니처를 고쳐야 할 테스트 수를 세지 않았다.
- 다른 영역: 테스트 영역

#### RUN-25: 역할 집합이 여러 모듈에 리터럴로 복제되어 있다
- 유형: 이음새중복
- 위치: `MACHINE_ROLES`는 `do_math/execution_profiles.py:18`과 `do_math/scheduler.py:12`에 두 번 정의되어 있다. 호스트 상한이 없는 Lean 역할 `{'formal_check','trust_check','trust_activate'}`은 `do_math/execution_profiles.py:23`의 차집합과 `do_math/session_slots.py:112`의 리터럴로 두 번 있다. Lean 명령 역할 `{'formal_check','trust_check'}`은 `do_math/launch.py:8`, `do_math/execution_profiles.py:70-71`, `:199`, `:216`, `do_math/scheduler.py:520`, `do_math/engine.py:1738`에 있다.
- 현상: 기계 역할 하나를 추가하거나 Lean 역할의 호스트 정책을 바꾸면 여러 모듈을 함께 고쳐야 한다.
- 제안: `execution_profiles.py`에 `LEAN_ROLES`와 `UNCAPPED_ROLES`를 두고, 모든 곳이 이 상수와 `MACHINE_ROLES`를 가져다 쓴다.
- 동작: 보존
- 실익: 리터럴 사본 9곳 제거.
- 위험과 보호: 보호 테스트: `tests/test_host_resources.py`
- 확신: 높음
- 다른 영역: `scheduler.py`, `launch.py`, `engine.py`

#### RUN-26: `windows_job.py`가 FILETIME 합성을 세 번 쓴다
- 유형: 복잡성
- 위치: `do_math/windows_job.py:459`, `:595`, `:617`
- 현상: `(dwHighDateTime << 32) | dwLowDateTime`을 세 곳에 쓴다. 두 곳은 문자열로, 한 곳은 정수로 쓴다. 발사표의 소유자 동일성 비교(`owner_ended`)는 이 세 결과가 같은 표현일 때만 맞는다.
- 제안: `_filetime(ft) -> int` 하나를 두고, 문자열화는 호출자가 한다.
- 동작: 보존
- 실익: 3행 감소. 동일성 비교의 표현이 한 함수에서 나온다.
- 위험과 보호: 보호 테스트: `tests/test_session_scheduler.py`의 `test_slot_waits_for_actual_named_job_termination`, `owner_ended`를 쓰는 테스트 4파일
- 확신: 높음
- 다른 영역: 없음

## 3. 보존 판정

1. **배정 사전 확인과 실제 배정의 이중 계산**(`do_math/session_slots.py:66-82`, `:99-238`). 겉보기에는 같은 계산을 두 번 한다. 하지만 사전 확인은 쓰기 잠금 없이 대기 사유를 표시하는 용도이고, 실제 배정은 잠금 아래 최신 원장에서 다시 검사해야 한다(`references/모델과-실행예산.md:5`). 따라서 두 번의 계산은 유지한다. 구현의 중복만 RUN-13으로 줄인다.
2. **러너의 입력 봉인 검사**(`do_math/model_runner.py:72-75`). 프롬프트 바이트와 봉인 해시를 러너가 다시 대조한다. 봉인은 엔진의 입력 적재기가 만들고, 러너는 실제로 전송할 바이트를 가진 쪽이다. 두 쪽 사이에 입력 조립(`prepare_prompt`)이 있으므로 이 대조는 수신 검사로 유지한다. RUN-24의 인자 정리와는 별개다.
3. **원천 최종 산출의 재검증**(`do_math/model_runner.py:305-383`). 수집 결과, 시작 기록, 작업자 상태를 여러 번 대조한다. 입력이 어댑터와 디스크에서 온 증거(신뢰 경계 밖)이므로 유지한다.
4. **운영 처분의 적용 시점 재검증**(`do_math/engine.py:4353-4358`). 제출 검사(`do_math/submission.py:729-732`)에서 한 검사를 적용 때 다시 한다. 하지만 `admissible_basis_refs`는 적용 시점의 런타임에서 다시 계산되고, 제출과 적용 사이에 저장·재적재가 있다. 따라서 유지한다.
5. **`windows_job.validate_resource_limits`와 `execution_profiles._host_amounts`**(`do_math/windows_job.py:29-37`, `do_math/execution_profiles.py:100-107`). 두 함수 모두 CPU 상한 10000과 양수 조건을 본다. 하지만 앞의 것은 OS가 받을 수 있는 값(`size_t` 범위)을 확인하고, 뒤의 것은 승인된 정책 형식(세 단위, `jobs=1`)을 확인한다. 둘은 다른 지식을 표현하므로 합치지 않는다.
6. **발사표의 소유자 식별과 이름 있는 Job의 이중 증거**(`do_math/launch.py:49-63`). 소유 프로세스의 종료와 Job이 비었다는 사실을 둘 다 확인한다. 두 증거가 각각 다른 실패(소유자 소실, 자식 잔존)를 막으므로 유지한다. 같은 Job을 두 번 조회하는 부분만 RUN-23으로 줄인다.
7. **공급자 게이트의 `checking` 소유권**(`do_math/session_slots.py:232-233`, `:287-290`, `:318-324`). 한 실행만 재관찰을 소유하고, 로컬 반환은 공급자 회복의 증거로 삼지 않는다. 문서(`references/모델과-실행예산.md:117`)가 요구하는 동작이므로 유지한다.

## 4. 후보 없음

- `do_math/execution_window.py`: RUN-11의 기본값 60 외에 후보 없음.
- `do_math/maintenance_gate.py`: RUN-05의 정지 판정 외에 후보 없음.
- `do_math/repair_execution.py`: 출력 수리 횟수 제한, 초기화 진단 경로, 설치 수리 경로를 읽었다. 이 영역의 세 주제에 해당하는 후보 없음.
- `do_math/model_policy.py`: RUN-16 외에 후보 없음. `validate_assessments`는 이미 생산자와 수신자가 공유하는 검사 함수다.
- 실행 창의 마감 기록과 마무리 요청(`execution_window.publish`, `request_finish`): 후보 없음.

## 5. 미완료

없음.

## 6. 작업 중 사건

- 슬롯 표시와 배정의 불일치(RUN-07)는 코드를 읽어 의심했고, `budget.plan_reservations`에 한 줄 입력을 넣어 거부를 실측했다. 같은 상태의 `snapshot` 값은 코드(`session_slots.py:347`, `:357`)에서 계산했으며 실행하지 않았다.
- 비용 수치는 모두 이 기계에서 `python -c`로 20~200회 반복한 평균이다. `build_profiles` 전체 38ms, 역할 하나 3.3~6.8ms, `admission_check` 1.3~3.9ms, `validate_profile` 0.2~0.46ms를 얻었다. 저장소 상태는 바꾸지 않았다.
- `engine.py:1697`의 `status`/`released` 비교(RUN-05)와 `state_checks.py:345`의 경로(RUN-20)는 예상하지 못한 어긋남이었다. 두 곳 모두 결과가 드러나지 않는 형태여서 테스트로 잡히지 않았다.
- 설치 복구 경로(`scheduled_operator.recovery`, 372-612행)는 맡은 모듈이 아니다. 하지만 실행 수명 전체를 엔진과 별도로 다시 구현하고 있어서, RUN-01·02·04·06의 끝점으로 포함했다.

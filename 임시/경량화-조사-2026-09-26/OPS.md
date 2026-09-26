# OPS 영역 경량화 조사: 운영, 거버넌스, 초기화, 보조 스크립트

기준 문서: `C:/math/임시/경량화-조사-2026-09-26/기준.md`. 모든 좌표는 2026-09-26 작업 트리(HEAD `8d2ffd0`, 작업 트리 clean)의 현재 원문 행 번호다. 경로는 `C:/math/.claude/skills/do-math/`를 기준으로 한 상대 경로로 적고, 스킬 밖의 파일은 절대 경로로 적는다.

통합자가 먼저 알아야 할 결론은 셋이다.

1. 운영 영역에서 가장 무거운 이음새는 "예약 감독이 엔진을 시작하지 않거나 복구를 열지 않을 조건"이다. 같은 상태(HOLD, 사용자 정지, 정비 fence, 종결·완료, 모델 정책 위반, 대화 소실, 설치 수리 대기, 운영 활성 여부)를 일곱 곳이 각자 다른 구성으로 해석한다. 실제 불일치도 확인했다. 엔진 쪽 wake 재조정(`provider_engine.py:131-133`)은 정비 fence를 받지 못한다(OPS-01).
2. 파견문의 "예약 작업의 등록·조회·제거가 PowerShell과 Python 양쪽에 따로 구현"이라는 전제는 현재 코드에서 성립하지 않는다. 예약 작업을 다루는 코드는 `scripts/operator_schedule.ps1` 하나이고, Python(`scheduled_operator.schedule`)은 그 어댑터를 호출해 JSON을 해석할 뿐이다. 양쪽에 겹치는 것은 동작 이름 집합, 간격 검증, 기본값, 스크립트 경로 전달 같은 인자 계약이다(OPS-04).
3. 죽었거나 같은 일을 하는 경로가 있다. `timeline --include-operator`는 커밋 ded5952 이후 생산자가 없는 경로를 읽는다(OPS-06). `probe_codex.py`는 `probe_cli.py`와 같은 일을 제품이 쓰지 않는 샌드박스 구성으로 한다(OPS-15). bootstrap의 해시 도우미 둘은 `file_io` 정본과 바이트가 같다(OPS-05, 읽기 전용 확인). 검증된 적재 직후에는 같은 사전 검사가 다시 돈다(OPS-07).

## 1. 읽은 범위

### 전문을 읽은 파일

| 파일 | 행 수 |
|---|---|
| `C:/math/임시/경량화-조사-2026-09-26/기준.md` | 120 |
| `C:/math/docs/do-math/검사-경량화-이음새-계약.md` | 159 |
| `C:/math/기억/layer3/L-0020.md` | 146 |
| `scripts/do_math/scheduled_operator.py` | 635 |
| `scripts/do_math/governance.py` | 1172 |
| `scripts/do_math/governance_engine.py` | 451 |
| `scripts/do_math/preflight.py` | 153 |
| `scripts/do_math/initialization.py` | 266 |
| `scripts/do_math/reporting.py` | 270 |
| `scripts/do_math.py` | 7 |
| `scripts/operator_bootstrap.py` | 187 |
| `scripts/operator_schedule.ps1` | 87 |
| `scripts/check_coverage.py` | 357 |
| `scripts/test_categories.py` | 34 |
| `scripts/probe_cli.py` | 141 |
| `scripts/probe_codex.py` | 182 |
| `scripts/probe_native_isolation.py` | 339 |
| `SKILL.md` | 173 |
| `README.md` | 565 |
| `AGENTS.md` | 11 |
| `references/초기화-운전.md` | 345 |
| `references/초기화-효율과-정비.md` | 153 |
| `계약/독립-운영.md` | 65 |
| `계약/운영-점검.md` | 95 |
| `계약/유지보수.md` | 138 |
| `계약/목표-감사.md` | 49 |
| `계약/의도-해석.md` | 77 |
| `scripts/tests/test_probe_codex.py` | 44 |

### 이음새 판정을 위해 일부만 읽은 파일

| 파일 | 읽은 행 |
|---|---|
| `scripts/do_math/engine.py` | 55-110, 168-192, 330-392, 574-590, 592-650, 1538-1600, 3630-3646, 3775-3790, 4750-4792 |
| `scripts/do_math/cli.py` | 262-300, 340-356, 440-520 |
| `scripts/do_math/provider_engine.py` | 105-175 |
| `scripts/do_math/lifecycle_engine.py` | 30-60, 165-185, 585-605 |
| `scripts/do_math/repository.py` | 103-225 |
| `scripts/do_math/state_contract.py` | 170-200 |
| `scripts/do_math/record_schemas/__init__.py` | 138-160, 195-240 |
| `scripts/do_math/record_schemas/schemas.py` | 218-240 |
| `scripts/do_math/record_schemas/domains.py` | 80-100 |
| `scripts/do_math/repair_execution.py` | 102-135 |
| `scripts/do_math/file_io.py` | 146-153 |
| `scripts/do_math/provider_wait.py` | 10-20 |
| `scripts/do_math/codex_adapter.py` | 124-153 |
| `scripts/do_math/codex_worker.py` | 29-30, 104-155(grep 행) |
| `scripts/do_math/model_runner.py` | 33-34 |
| `scripts/do_math/model_policy.py` | 7-16 |
| `scripts/do_math/control_contracts.py` | 40-60, 106-140 |
| `scripts/do_math/contracts.py` | 310-335 |
| `references/CLI-실행-계약.md` | 186-203(grep 행) |
| `scripts/tests/test_preflight.py` | 1-64 |
| `scripts/tests/test_reporting.py` | 145-171 |
| `scripts/tests/test_operator.py` | 시험 이름 목록(38-284) |
| `scripts/tests/test_operator_bootstrap.py` | 시험 이름 목록 |

## 2. 후보

#### OPS-01: 예약 감독의 정지·시작 조건을 한 판정 함수로 모은다
- 유형: 이음새중복
- 위치:
  - `scripts/do_math/scheduled_operator.py:223-227` (`run_engine`의 감독 요청 조건)
  - `scripts/do_math/scheduled_operator.py:251-278` (`engine_start_guard`)
  - `scripts/do_math/scheduled_operator.py:285-286`, `291` (`reconcile_wake`의 held 판정과 운영 활성 여부)
  - `scripts/do_math/scheduled_operator.py:336-343` (`check`)
  - `scripts/do_math/scheduled_operator.py:393-397`, `562-563` (`recovery`의 잠금 안 재확인)
  - `scripts/do_math/provider_engine.py:126-135` (엔진 쪽 `_schedule_provider_wake`)
  - `scripts/do_math/reporting.py:108-133` (`operating_summary.primary_blocker`)
  - `scripts/do_math/engine.py:1587-1590` (`status`의 `user_pause`·`conversation_lost`·`model_policy_violation` 투영)
- 현상: 여러 지점이 같은 상태를 각자 다른 구성으로 해석한다.

  | 지점 | HOLD | user_pause | status | maintenance_fence | model_policy | conversation_lost | operator_enabled |
  |---|---|---|---|---|---|---|---|
  | `run_engine` 223-227 | 파일 | ○ | {paused, closed, completed} | ○ | × | × | `operating_summary.supervision.configured_enabled is True` |
  | `engine_start_guard` 253-266 | 파일 | ○ | `paused`, 이후 {ready, running, capacity_waiting} 밖이면 비시작 | ○ | ○ | `status['conversation_lost']` | × |
  | `reconcile_wake` 285-291 | 파일 | ○ | {paused, closed, completed} | ○(인자에 있을 때만) | × | × | `config.get(..., True)` |
  | `check` 336-343 | 파일(322) | ○ | {paused, closed, completed} | ×(뒤의 guard가 봄) | ○ | 원시 상태에서 다시 도출(342) | `config.get(..., True)` |
  | `recovery` 393-397 | 파일 | ○ | {paused, closed, completed} | ○ | × | × | `config.get(..., True)` |
  | `_schedule_provider_wake` 131-133 | (reconcile 안) | ○ | runtime status | **전달 안 함** | × | × | `config.get(...)` |

  확인한 불일치는 셋이다.
  - 엔진 쪽 `_schedule_provider_wake`는 `reconcile_wake`에 `{"user_pause", "status"}`만 담은 합성 상태를 넘긴다(`provider_engine.py:131-133`). 그래서 정비 fence 중에도 엔진이 공급자 wake 예약을 등록할 수 있다. 감독 쪽 `check`는 같은 함수에 fence가 들어 있는 전체 status를 넘기므로 예약을 취소한다. 두 경로가 같은 예약을 서로 반대로 조정할 수 있다. 등록된 wake가 실행되어도 `wake()`의 `engine_start_guard`가 fence를 보고 막으므로(257-258) 연구가 잘못 시작되지는 않는다. 남는 비용은 헛된 예약과 PowerShell 호출이다.
  - 대화 소실 정지는 `engine.status`가 이미 `conversation_lost`로 투영한다(`engine.py:1588-1589`). 그런데 `check`는 따로 적재한 원시 상태에서 같은 식을 다시 계산한다(`scheduled_operator.py:342`).
  - 운영 활성 여부는 한 곳이 표시용 투영의 `configured_enabled is True`로, 세 곳이 `config.get("operator_enabled", True)`로 읽는다. `validate_config`가 이 키를 불리언으로 강제하므로(`engine.py:175-177`) 현재 값은 갈리지 않는다. 다만 기본값 규칙이 두 벌이다.
- 제안: `scheduled_operator.py`에 순수 함수 `supervision_block(facts, workspace) -> dict | None` 하나를 두고, 고정된 우선순위로 첫 차단 사유(`held`, `maintenance_waiting`, `model_policy_waiting`, `paused`/`closed`/`completed`, `user_paused`(대화 소실), `installation_repair_waiting`, `disabled`)를 돌려주게 한다. 입력 `facts`는 `engine.status`의 필드 부분집합이다(`user_pause`, `status`, `maintenance_fence`, `model_policy_violation`, `conversation_lost`, `installation_repair`, 운영 활성 여부). 엔진 쪽 `_schedule_provider_wake`는 합성 dict 대신 같은 필드를 채우는 도우미를 쓴다. 이 도우미는 `reporting.operating_summary` 옆에 `supervision_facts(instance, runtime)`로 두고, `engine.status`도 같은 도우미로 해당 필드를 만든다. 각 지점의 처리는 다음과 같다.
  - `engine_start_guard`는 차단 사유가 없을 때만 공급자 재관찰·연구 재검토 분기를 평가한다.
  - `reconcile_wake`, `recovery`의 두 재확인, `run_engine`의 감독 요청은 같은 함수를 호출한다. `recovery`는 잠금 안에서 방금 적재한 상태로 `facts`를 만든다.
  - `reporting.operating_summary.primary_blocker`는 HOLD 파일을 보지 않는 저장 상태 투영이다. 같은 우선순위 표를 공유하되 HOLD 항목만 빠지게 한다. 표시 계약(`README.md:239`)은 바꾸지 않는다.
- 동작: 변경. 엔진 쪽 공급자 wake 재조정이 정비 fence를 보게 되어, fence 중에는 wake 예약을 등록하지 않고 취소한다. `check`의 반환 `outcome` 문자열은 지점마다 조금씩 다른데(예: 대화 소실이 `check`에서는 `user_paused`, guard에서도 `user_paused`, 종결은 `check`에서 `closed`, guard에서 `not_started`), 통일하면 일부 반환 값이 바뀐다. 기존 값을 유지하려면 함수가 사유 코드를 돌려주고 각 지점이 지금의 outcome 문자열로 사상하면 된다.
- 실익: 판정 코드 약 35행이 한 함수로 줄고, 정지 조건을 새로 추가할 때 고칠 곳이 일곱에서 하나로 준다(추정, 위 좌표의 행 수 합산). 엔진·감독 사이의 fence 불일치 경로가 사라진다.
- 위험과 보호: 우선순위를 바꾸면 반환 outcome이 바뀐다. 덮는 시험은 `scripts/tests/test_operator.py`의 `test_engine_does_not_start_for_hold_or_any_pause`, `test_automatic_and_user_pause_do_not_trigger_external_recovery`, `test_completed_instance_is_observed_without_starting_an_operator_model`, `test_accepted_installation_repair_requests_supervisor_without_periodic_delay`이다. `reconcile_wake`는 `test_six_connections.py`, `test_static_review_repairs.py`, `test_walkthrough_contract_repairs.py`, `test_initialization_efficiency.py`, `test_redesign_PROFILES.py`가 참조한다(grep `reconcile_wake|engine_start_guard`). fence 중 엔진 쪽 wake 재조정을 덮는 시험은 없음.
- 확신: 높음. 불일치는 원문 행으로 확인했고, 합칠 대상은 모두 "감독이 시작·복구를 보류할 조건"이라는 같은 지식이다.
- 다른 영역: `engine.py`(status 투영), `provider_engine.py`(공급자 wake), `reporting.py`(운영 요약). 엔진·공급자 영역 조사자와 겹칠 수 있다.

#### OPS-02: `check` 한 번에 상태를 두 번 적재하고 예약 상태를 두 번 조회하는 것을 없앤다
- 유형: 운영비용
- 위치: `scripts/do_math/scheduled_operator.py:325`(`read_status`), `334`(`ResearchRepository(...).load()`), `299`(`reconcile_wake`의 `schedule("status")`), `365`(`check`의 `schedule("status")`)
- 현상: `check`는 `read_status`로 `ResearchEngine`을 만들어 status를 얻는다(내부에서 적재 두 번과 `inspect_state` 수행). 그 뒤 설정과 원시 runtime을 얻으려고 저장소를 다시 적재한다(334). 두 적재는 서로 다른 시점의 head일 수 있다. 판정 일부는 앞의 status로, 일부(`conversation_lost` 342, 설치 수리 345)는 뒤의 상태로 한다. 공급자 대기가 있으면 `reconcile_wake`가 PowerShell `status`를 한 번 부르고(299), guard가 시작 가능이면 `check`가 같은 조회를 다시 부른다(365).
- 제안: `check`가 status 하나만 쓰게 한다. 운영 활성 여부는 `status['operating_summary']['supervision']['configured_enabled']`(`reporting.py:141`)에서 읽는다. 설치 수리는 `status['installation_repair']`에서 읽고, 복구에 넘길 `installation_failure`만 `recovery` 안의 잠금 적재에서 계산한다. `recovery`는 이미 잠금 안에서 적재하고 진단을 다시 대조한다(`scheduled_operator.py:391`, `400-403`). `reconcile_wake`는 조회한 예약 상태를 반환값에 담고, `check`는 그 값이 있으면 재조회하지 않는다.
- 동작: 보존. 한 점검 안의 판단이 한 snapshot에 근거하게 된다.
- 실익: 공급자 대기 중인 점검마다 PowerShell 프로세스 하나(측정값 1.18-1.42초, 아래 명령)가 줄고, 상태 적재·deepcopy가 한 번 준다. 측정 명령: `powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Get-ScheduledTask -TaskName DoMath-Nonexistent-zzz -ErrorAction SilentlyContinue | Out-Null"`을 세 번 실행한 시간 `[1.42, 1.18, 1.38]`초. 어댑터의 `status`는 작업 세 개를 조회하므로 실제 비용은 이보다 크거나 같다(추정).
- 위험과 보호: 설치 수리 판정 위치를 옮기면 `probe` 반환 형태(`installation_repair_pending`, 349)가 바뀔 수 있다. 덮는 시험은 `test_operator.py`의 `test_probe_observes_without_starting_a_model_or_engine`, `test_real_probe_persists_failure_when_engine_has_syntax_error`, `test_diagnosed_installation_recovery.py`다.
- 확신: 높음. 적재와 조회의 중복이 행 단위로 확인된다.
- 다른 영역: 없음.

#### OPS-03: 엔진이 실행 결과마다 부르는 wake 재조정이 상태를 다시 적재하지 않게 한다
- 유형: 운영비용
- 위치: `scripts/do_math/provider_engine.py:118-135`, `scripts/do_math/scheduled_operator.py:287-289`, 호출 지점 `scripts/do_math/engine.py:3643`, `3787`
- 현상: 엔진은 실행 결과를 처리할 때마다 `_publish_provider_result`로 저장한 뒤 `_schedule_provider_wake`를 부른다(`engine.py:3787`). 운영이 활성이면(기본값 활성) `reconcile_wake`가 `ResearchRepository(repository, instance).load()`로 방금 저장한 상태 전체를 다시 적재한다(287). 검증된 읽기 캐시에 적중하지만 `load`는 instance·runtime 전체를 deepcopy한다(`repository.py:208-211`). 엔진은 같은 상태를 이미 메모리에 가지고 있다.
- 제안: `reconcile_wake(..., state=None, runtime=None)`로 호출자가 가진 상태를 받게 하고, 엔진은 `self.instance`, `self.runtime`을 넘긴다. 감독 쪽은 지금처럼 인자 없이 호출한다. OPS-01과 함께 하면 `status` 인자도 `supervision_facts`로 바뀐다.
- 동작: 보존. 엔진은 저장 직후 호출하므로 메모리 상태와 저장 head가 같다(`provider_engine.py:120-122`).
- 실익: 실행 결과 하나마다 상태 전체 deepcopy 한 번이 준다. 크기는 인스턴스에 따라 다르다. 실측은 하지 못했다(6절). 공급자 대기가 없으면 PowerShell 호출은 원래 없으므로 이 후보는 적재 비용만 줄인다.
- 위험과 보호: `SessionSlots(runtime, state, observer=True)`가 인자를 변경하지 않는지 확인해야 한다. 덮는 시험은 위 OPS-01의 `reconcile_wake` 참조 시험들이다.
- 확신: 중간. 중복은 확실하지만 절감량은 측정하지 못했다.
- 다른 영역: `provider_engine.py`, `engine.py`

#### OPS-04: 예약 어댑터의 인자 계약을 한쪽에만 둔다
- 유형: 이음새중복
- 위치:
  - 동작 이름 집합: `scripts/do_math/scheduled_operator.py:120`, `scripts/operator_schedule.ps1:2`
  - 간격 검증: `scheduled_operator.py:122-123`, `operator_schedule.ps1:13-14`, `scripts/do_math/engine.py:184-190`
  - 기본값 7200·5400: `scheduled_operator.py:113-114`, `engine.py:101-102`
  - 스크립트 경로 전달: `scheduled_operator.py:35`, `135`, `operator_schedule.ps1:8`, `20`, `40-41`, `49`
  - wake 취소 절차: `scheduled_operator.py:292-294`, `scripts/do_math/cli.py:489-491`
  - wake 표지 경로 리터럴: `scheduled_operator.py:283`, `cli.py:491`
  - HOLD 정지 사유 문자열: `cli.py:487`, `cli.py:497`
- 현상: 등록·조회·제거·시작은 PowerShell 한 곳에만 구현되어 있다. 전수 검색 `schtasks|ScheduledTask|Register-Scheduled|Unregister-Scheduled|operator_schedule|task_names\(|scheduled_operator\.schedule` 결과가 이를 뒷받침한다. 이음새에서 겹치는 부분은 다음과 같다.
  - 동작 이름 7개가 Python 집합과 PowerShell `ValidateSet`에 따로 적혀 있다.
  - `-IntervalSeconds`와 `-OperatorTimeoutSeconds`는 `install`에서만 쓰이는데 모든 동작에 필수다. 그래서 Python `schedule()`이 기본값 7200·5400을 가지고, CLI는 `status`·`start`에도 설정을 적재해 넘긴다(`cli.py:470-480`). 이 기본값은 `DEFAULT_CONFIG`의 복제이지만 `install` 외에는 쓰이지 않는다.
  - `-Entrypoint`로 `do_math.py` 경로를 넘기지만 PowerShell은 그 부모 디렉터리에서 `operator_bootstrap.py`를 찾는 데만 쓴다(20, 40). 이 디렉터리는 스크립트 자신의 위치 `$PSScriptRoot`와 같다. `SCHEDULE_SCRIPT`와 `ENTRYPOINT`는 둘 다 `SCRIPTS` 아래에 있다(`scheduled_operator.py:35-36`).
  - `operator hold`가 wake를 취소하는 코드(`cli.py:489-491`)가 `reconcile_wake`의 취소(292-294)를 표지 경로 리터럴까지 복제한다.
  - HOLD 정지 사유 `"User requested scheduled operator HOLD " + id`가 두 번 조립되고, 엔진은 이 문자열을 `expected_user_pause_reason`과 비교한다.
- 제안:
  - PowerShell의 간격·기한 인자를 비필수로 바꾸고 `install`에서만 존재를 검사한다. Python은 `install`에만 값을 넘기고 `schedule()`의 기본값 7200·5400을 없앤다. 간격의 양수 검증은 `validate_config` 한 곳에 둔다.
  - PowerShell이 `$PSScriptRoot`로 bootstrap을 찾게 하고 `-Entrypoint` 인자와 `ENTRYPOINT` 상수를 없앤다. `install`의 `$Entrypoint` 재대입(49)은 지역 변수 `$frozenBootstrap`으로 바꾼다.
  - 동작 이름 집합은 PowerShell `ValidateSet`을 정본으로 두고, Python 쪽 검사는 오류 메시지를 위한 것이면 모듈 상수 하나로 둔다.
  - `scheduled_operator.cancel_wake(repository, instance, workspace)`를 두어 `reconcile_wake`와 CLI `hold`가 함께 쓴다. `scheduled_operator.hold_pause_reason(hold_id)`를 두어 CLI의 두 조립을 대체한다.
- 동작: 보존. 예약 작업의 이름, 트리거, 실행 제한, 반환 JSON은 바뀌지 않는다.
- 실익: 인자 7개 중 2개가 조건부가 되고 1개가 사라진다. CLI의 `status`·`start`·`start-operator`가 설정 적재를 하지 않게 된다(`cli.py:470-471`). 중복 리터럴 4곳이 사라진다.
- 위험과 보호: 시험이 어댑터를 `-Entrypoint`와 함께 직접 호출한다(`scripts/tests/test_schedule_pythonw.py:30`). `test_operator.py`의 `test_schedule_request_passes_only_generic_instance_coordinates`, `test_schedule_reconcile_preserves_entrypoint_paths_and_disable_direction`, `test_new_instance_installs_the_operator_every_two_hours_by_default`도 인자 목록을 단언하므로 함께 고쳐야 한다. frozen 감독이 부르는 `schedule-wake`는 snapshot 안의 어댑터를 쓰므로 `$PSScriptRoot`도 snapshot을 가리킨다. 이 점은 `test_operator.py::test_engine_child_targets_live_installation_from_frozen_supervisor`가 덮지 않으므로 새 시험이 필요하다(없음).
- 확신: 높음. 인자 사용처를 원문 전 행으로 확인했다.
- 다른 영역: `cli.py`(operator 명령)

#### OPS-05: bootstrap의 해시 도우미를 `file_io` 정본으로 바꾼다
- 유형: 이음새중복
- 위치: `scripts/operator_bootstrap.py:21-23`(`_digest`), `49-50`(`_source_files`), `53-58`(`_file_io`), `88`, `C:/math/docs/do-math/검사-경량화-이음새-계약.md:75`
- 현상: 이음새 계약 2.1절은 bootstrap의 `_digest`를 보존한 이유를 "설계상 `do_math`를 import하지 않는다"로 적었다(계약 75행). 그러나 직전 라운드 이후 bootstrap은 `verify_snapshot`에서 `do_math.file_io`를 import한다(`operator_bootstrap.py:53-58`, `88`). `freeze`도 마지막에 `verify_snapshot`을 부르므로 live 설치의 `file_io`를 import한다(154). 그러니 보존 근거가 더는 성립하지 않는다. 두 도우미가 정본과 같은 값을 내는지 읽기 전용으로 확인했다.
  ```
  python -c "import sys;sys.path.insert(0,'.');import operator_bootstrap as b; from do_math.file_io import json_digest, sha256_file; ... print(b._digest(basis)==json_digest(basis)); print(all(sha256_file(p)==files[n] ...))"
  → True 116 / True
  ```
  (작업 디렉터리 `scripts/`. `basis`는 현재 설치 116개 파일의 실제 manifest 기초값이다.) `_digest`는 `json_digest`와 `allow_nan`만 다르고, manifest에는 부동소수가 없다.
- 제안: `_digest`를 `file_io.json_digest`로, `_source_files`의 `hashlib.sha256(path.read_bytes())`를 `file_io.sha256_file`로 바꾼다. `freeze`는 시작할 때 `_file_io()`를 한 번 부른다. 이음새 계약 2.1절의 보존 목록에서 `operator_bootstrap` 항목을 지운다.
- 동작: 보존. snapshot 디렉터리 이름(`snapshot_sha256`)과 manifest 해시가 바이트 단위로 같으므로 기존 bootstrap 사본도 그대로 검증된다.
- 실익: 해시 도우미 2개(약 6행)와 `hashlib` import가 사라진다. 계약 문서의 낡은 예외 하나가 정리된다.
- 위험과 보호: `freeze`가 live `file_io`를 더 일찍 import하게 된다. live 설치가 `file_io`조차 import하지 못하는 경우에는 freeze가 지금보다 앞 단계에서 실패하지만, 지금도 154행에서 같은 import로 실패한다. 덮는 시험은 `scripts/tests/test_operator_bootstrap.py`의 네 시험과 `test_operator.py::test_real_probe_persists_failure_when_engine_has_syntax_error`다.
- 확신: 높음. 바이트 동일성을 실측했다.
- 다른 영역: 이음새 계약 문서(통합자 소유)

#### OPS-06: 생산자가 없는 `timeline --include-operator` 경로를 제거한다
- 유형: 죽은코드
- 위치: `scripts/do_math/reporting.py:209`, `235-248`, `scripts/do_math/cli.py:110`, `296`, `README.md:517`, `references/CLI-실행-계약.md:958`, `scripts/tests/test_reporting.py:152-171`
- 현상: `include_operator`는 `<workspace>/operator/runs/*/result.json`을 읽는다(`reporting.py:236`). 이 경로를 쓰는 제품 코드는 없다. 전수 검색 `operator/runs|"runs"|'runs'` 결과 제품 코드의 해당 경로는 이 읽기 한 곳뿐이다. 시험(`test_reporting.py:160`)이 파일을 손으로 만들어 넣는다. 생산자는 커밋 ded5952("do-math 검증 1라운드로 계약 불일치와 미사용 경로를 정리")에서 `scheduled_operator.py`의 `run_directory = _operator_dir(workspace) / "runs" / ...`가 삭제될 때 사라졌다(`git log -S'/ "runs"' -- scripts/do_math/scheduled_operator.py`). 읽는 필드(`result.assigned_model`, `model_selection`, `ended_at`)도 폐기된 모델 호출 운영자의 기록 형식이다. 현재 모델을 부르는 운영 경로는 설치 복구 하나이고, 그 실행은 `role="recovery"` 실행 기록으로 연구 상태에 들어간다(`scheduled_operator.py:489-495`). 그래서 `timeline`의 `internal_execution` 행으로 이미 나온다.
- 제안: `timeline`의 `include_operator` 인자와 235-248행, CLI 플래그(`cli.py:110`, `296`), README 517행, CLI 실행 계약 958행의 사용법 표기, 시험 `test_local_operator_evidence_has_its_own_hash_and_count_unit`을 삭제한다. 운영 로그를 보는 경로는 `--include-operations`(`reporting.py:249-255`)가 남는다.
- 동작: 변경. 공개 CLI 플래그 하나가 사라진다. 실제 인스턴스에서는 이 플래그가 항상 0행을 돌려주었으므로 관찰되는 데이터는 바뀌지 않는다.
- 실익: 제품 코드 약 16행, 시험 20행, 문서 한 문장이 준다. "현재 로컬 운영 로그도 포함한다"는 README의 틀린 약속이 사라진다.
- 위험과 보호: 외부 스크립트가 이 플래그를 쓰면 argparse 오류가 난다. 저장소 전체 grep `include-operator|include_operator` 결과 사용처는 위 좌표뿐이다.
- 확신: 높음. 생산자 삭제 커밋을 확인했다.
- 다른 영역: `cli.py`, `README.md`

#### OPS-07: 검증된 적재 직후 같은 사전 검사를 다시 돌리지 않는다
- 유형: 수신재검사중복
- 위치: `scripts/do_math/record_schemas/__init__.py:218-222`(검증된 읽기 안의 `inspect_current_state`), `scripts/do_math/repository.py:185`(`contract.validate` 호출), `scripts/do_math/engine.py:599`(`__init__`), `engine.py:387`(`control`), `scripts/do_math/preflight.py:72-73`(`inspect_persisted_state`), `engine.py:4787`(`check`)
- 현상: `ResearchRepository._read_documents`는 `contract.validate`를 거치고, 그 안의 `validate_semantics`가 `inspect_current_state`를 실행한다(`record_schemas/__init__.py:218-222`). 그런데 적재 직후 같은 값에 같은 함수를 다시 부르는 곳이 넷이다.
  - `ResearchEngine.__init__`: `store.load()` 바로 뒤(599)
  - `control`: `store.load()` 뒤(387)
  - `inspect_persisted_state`: `_read_documents` 바로 뒤(73)
  - `ResearchEngine.check`: `store.load(snapshot)` 뒤(4787)

  네 곳 모두 같은 프로세스이고, 적재와 재검사 사이에 값을 바꾸는 경로가 없다. 예외는 `validate_semantics`가 `if "lifecycle" in instance`일 때만 검사한다는 점이다(218). lifecycle 기록군은 선택적 singleton으로 등록되므로(`record_schemas/__init__.py:143-160`) lifecycle이 없는 상태는 검증된 읽기를 통과한다. 지금은 뒤의 재검사가 그런 상태를 거부한다. `test_reporting.py:156-158`처럼 lifecycle 없는 최소 상태를 저장하는 시험이 이 조건 분기에 기대고 있다.
- 제안: `validate_semantics`의 `if "lifecycle" in instance` 조건을 없애 `inspect_current_state`를 무조건 실행한다. 그 뒤 위 네 재검사를 삭제한다. `_inspect_before_write`(`engine.py:4758`)는 메모리에서 바뀐 상태를 검사하므로 유지한다. `AGENTS.md:7`("구형 fixture나 인터페이스를 살리려고 제품 코드에 예외를 넣지 않는다")에 따라 lifecycle 없는 시험 상태는 현행 `initialize_state`로 만들게 고친다.
- 동작: 변경(비정상 상태만). lifecycle 없는 상태가 엔진 생성 단계가 아니라 적재 단계에서 거부된다. 정상 v5 상태의 동작은 같다.
- 실익: 재검사 호출 4개와 `_require_current_contract`의 호출부가 준다. 검사 한 번은 dict 조회와 과제 전수 순회라 시간 절감은 작다(추정). 주된 실익은 "적재된 상태는 이미 사전 검사를 통과했다"는 불변식이 한 곳에 서는 것이다.
- 위험과 보호: lifecycle 없는 상태를 쓰는 시험이 몇 개인지는 미확인이다. 전수 grep이 필요하지만 fixture 구성이 다양해 이번 조사에서 세지 못했다. 덮는 시험은 `scripts/tests/test_preflight.py`의 `test_good_head_preserves_rejected_raw_not_candidate_state`, `test_damaged_head_is_not_rewritten_even_to_preserve_candidate`와 `test_redesign_ENGINE.py`의 `_require_current_contract` 패치 시험(651, 692, 1258행)이다. 뒤의 패치 시험은 함수 삭제에 맞춰 고쳐야 한다.
- 확신: 중간. 중복은 확실하지만 시험 fixture의 파급 범위를 세지 못했다.
- 다른 영역: `engine.py`, `record_schemas/`(상태 저장 영역)

#### OPS-08: 설치 판본 식별의 파일 집합 정의를 하나로 모은다
- 유형: 이음새중복
- 위치:
  - `scripts/do_math/repair_execution.py:102-109`(`installation_sha256`: 트리 전체의 `.py`·`.md`·`.ps1`·`requirements.txt`, `scripts/tests` 포함, `__pycache__`만 제외)
  - `scripts/operator_bootstrap.py:35-46`(`_source_paths`: 트리 전체, `scripts/tests`·`__pycache__`·`.git`·`.lake`·`.pyc`·bootstrap 표지 제외)
  - `scripts/do_math/engine.py:622-628`(`_installation_manifest`: `do_math/*.py`, 역할 읽기 문서, 추가 3개 파일)
  - `scripts/do_math/preflight.py:107-108`(설치 검사 대상 추가 문서 5개)
  - `scripts/tests/test_preflight.py:58-59`(위 5개 목록의 시험 사본)
- 현상: "설치된 스킬의 판본"을 네 곳이 서로 다른 파일 집합으로 정의한다. 같은 개념은 둘이다.
  - 복구 식별(`repair_execution`)과 bootstrap 사본(`operator_bootstrap`)은 모두 "설치 스킬 전체"를 뜻한다. 그러나 앞의 것은 시험 파일을 포함하고 `examples/*.json`을 뺀다. 뒤의 것은 그 반대다. 그 결과 시험 파일만 고쳐도 복구 식별이 바뀐다. 복구의 "같은 실패·같은 설치 판본은 한 번만" 규칙(`scheduled_operator.py:422-427`)이 시험 편집만으로 다시 열린다.
  - 추가 운영 문서 목록은 두 벌이다(`preflight.py:107-108`의 5개와 `engine.py:626`의 3개). 시험은 앞의 목록을 손으로 복제한다(`test_preflight.py:58-59`).
- 제안: `repair_execution.py`나 `file_io.py`에 `installation_files(root) -> dict[relpath, Path]`를 두어 bootstrap의 현재 규칙(시험·캐시·VCS·빌드 산출·bootstrap 표지 제외)을 정본으로 삼는다. `repair_execution.installation_sha256`과 `operator_bootstrap._source_paths`는 이 함수를 쓴다. bootstrap은 `do_math`를 import하므로(OPS-05) 가능하다. 운영 문서 목록은 `contracts.py`에 `OPERATING_DOCUMENTS` 상수 하나로 두고 `preflight`, `engine._installation_manifest`, 시험이 함께 읽는다. 엔진 manifest의 좁은 범위(역할이 받는 문서와 엔진 코드)는 다른 개념이므로 유지한다(3절).
- 동작: 변경. 시험 파일만 바뀐 경우 복구 식별이 바뀌지 않아 같은 실패의 자동 복구가 다시 열리지 않는다. `examples/*.json` 변경은 복구 식별을 바꾼다.
- 실익: 파일 집합 규칙 두 벌이 하나로 줄고, 문서 목록 복제 셋(제품 둘, 시험 하나)이 상수 하나로 준다.
- 위험과 보호: 복구 AI가 회귀 시험만 추가하고 "repaired"를 보고하는 경우의 재시도 규칙이 달라진다. 이 경우를 다루는 계약은 `계약/독립-운영.md:27`, `61`("같은 오류와 설치 판본으로 수리를 반복하지 않는다")이다. 덮는 시험은 `test_repair_execution.py`, `test_walkthrough_contract_repairs.py`(grep `installation_sha256`)와 `test_preflight.py`의 `PreflightTests`다.
- 확신: 중간. 두 집합이 같은 개념이라는 판단은 두 함수의 docstring("Identity of the whole installed skill", "Freeze ... installed supervisor")에 근거한다. 시험 포함 여부가 의도였다는 기록은 찾지 못했다.
- 다른 영역: `repair_execution.py`, `engine.py`, `contracts.py`

#### OPS-09: grant의 시간 효력 규칙과 정규화 규칙을 한 곳에 둔다
- 유형: 이음새중복
- 위치:
  - 시간 효력: `scripts/do_math/governance.py:381-382`(`_grant_scope_reason`), `governance.py:514`(`expire_grants`), `scripts/do_math/initialization.py:233-234`(`grant_current`)
  - 정규화: `governance.py:568-573`(생산: `apply_decision`), `governance.py:453-458`(수신: `validate_grant_source`)
- 현상: "grant는 `expires_at <= now`면 만료, `valid_from > now`면 아직 효력 없음"이라는 규칙이 세 곳에 따로 있다. 경계 부등호는 지금 세 곳 모두 일치한다. 또 새 grant를 저장할 때 채우는 기본값(`status="active"`, `reuse="once"`, 목록 필드 다섯 개의 빈 배열, `created_at`, `source_ref`, `decision_id`)을 생산자(568-573)가 적용한다. 수신자(453-458)는 결정 기록에서 같은 기본값을 다시 조립해 저장된 grant와 비교한다. 한쪽 기본값만 바뀌면 모든 기존 grant가 "grant differs from the actual approved scope"로 거부된다.
- 제안: `governance.py`에 `grant_time_reason(grant, now) -> str | None`과 `normalized_grant(spec, *, gid, when, source_ref, decision_id) -> dict`를 둔다. `_grant_scope_reason`, `expire_grants`, `initialization.grant_current`는 앞의 함수를 쓴다. `apply_decision`의 grant 분기와 `validate_grant_source`는 뒤의 함수를 쓴다. 이렇게 하면 생산자와 수신자가 같은 정규화 함수로 같은 값을 만든다.
- 동작: 보존.
- 실익: 같은 규칙의 재기술 세 곳과 두 곳이 각각 하나로 준다(약 15행).
- 위험과 보호: `validate_grant_source`는 결정 기록의 `change.grant`에서, `apply_decision`은 요청 spec에서 시작한다. `expires_at` 처리(`approved.get("expires_at")`와 `spec.get("expires_at")`)가 같은지 합칠 때 확인해야 한다. 덮는 시험은 `test_redesign_GOVERNANCE.py`, `test_lifecycle_engine.py`, `test_redesign_STORAGE.py`, `test_walkthrough_repairs.py`(grep `grant_current|_grant_scope_reason|expire_grants|validate_grant_source`)다.
- 확신: 높음.
- 다른 영역: `record_schemas/__init__.py`의 grant 검사가 `validate_grant_source`를 부르는지는 미확인이다(240행 이후를 읽지 않았다).

#### OPS-10: `governance.py` 안의 같은 리터럴과 로컬 해시 재구현을 정리한다
- 유형: 복잡성
- 위치:
  - 결정 소유자 종류 집합 `GOVERNANCE_KINDS | {"grant", "revoke", "delegation", "question_answer", "task_scope"}`: `scripts/do_math/governance.py:742`, `757`, `759`, `854`, `998`
  - 의도 해석 검사의 판정 어휘: `governance.py:1014`(수신 검사 집합), `governance.py:1162`(출력 스키마 enum), `계약/의도-해석.md:52`
  - `exact_content_hash` 재구현: `scripts/do_math/governance_engine.py:22-23`
- 현상: 기본 결정 종류 다섯 개를 담은 집합 리터럴이 한 모듈에 다섯 번 나온다. 판정 어휘 세 개는 스키마 enum과 수신 검사에 따로 적혀 있다. `bind_host_configuration`은 `hashlib.sha256(canonical_json(...))`를 직접 계산하는데, 이는 `repository.exact_content_hash`의 정의(`repository.py:112-114`)와 같다.
- 제안: `DECISION_OWNER_KINDS = GOVERNANCE_KINDS | {...}`와 `INTERPRETATION_DECISIONS = ("approved", "revision_required", "unresolved")`를 모듈 상수로 두고 모든 사용처가 참조한다. 수신 검사는 신뢰 경계 밖 모델 출력을 받으므로 유지하되 스키마와 같은 상수를 쓴다. `governance_engine.py:22-23`은 `exact_content_hash({'host_resources': host})`로 바꾼다. 결과 식별자는 바이트가 같아 바뀌지 않는다.
- 동작: 보존.
- 실익: 리터럴 7곳이 상수 2개로 줄고 해시 재구현 1곳이 사라진다.
- 위험과 보호: 없음에 가깝다. 덮는 시험은 `test_redesign_GOVERNANCE.py`, `test_knowledge_import_engine.py`다.
- 확신: 높음.
- 다른 영역: 없음.

#### OPS-11: `status --snapshot`과 라이브 `status`의 목표 도출을 하나로 한다
- 유형: 이음새중복
- 위치: `scripts/do_math/reporting.py:163-164`(`snapshot_report`), `scripts/do_math/engine.py:574-586`(`_governance`), `engine.py:1555`(`status`의 `goal`), `scripts/do_math/cli.py:344-352`
- 현상: CLI `status`는 snapshot을 지정하지 않으면 `engine.status`를, 지정하면 `reporting.snapshot_report`를 쓴다(`cli.py:346-349`). 라이브 쪽은 `engine._governance()`로 목표를 얻는다. 이 함수는 초기화 중이라 활성 헌장이 없으면 최초 입력의 목표로 대체한다(577-583). snapshot 쪽은 `governance_view(instance).get('goal') if instance.get('governance') else instance.get('goal')`이다. 그런데 v5 상태에는 최상위 `goal`이 있을 수 없다. `validate_governance_state`가 이를 "parallel governance authority"로 거부한다(`governance.py:162-163`). 그래서 대체 분기는 항상 `None`이다. 결과적으로 초기화 중인 인스턴스는 라이브 `status`에서는 목표가 보이고 `status --snapshot <head>`에서는 `goal: unknown`으로 보인다.
- 제안: `engine._governance`의 본문을 인스턴스·runtime만 받는 순수 함수(예: `initialization.governance_or_initial_view(instance, runtime)`)로 옮긴다. `engine._governance`와 `snapshot_report`가 이 함수를 쓰고, `reporting.py:164`의 `instance.get('goal')` 분기는 삭제한다.
- 동작: 변경. 초기화 중 인스턴스의 `status --snapshot` 출력에 최초 입력 목표가 나타난다.
- 실익: 죽은 호환 분기 하나가 사라지고, 같은 snapshot에 대한 두 조회 경로의 불일치 하나가 해소된다.
- 위험과 보호: 덮는 시험은 `test_redesign_SURFACE.py`(217, 452행 부근)와 `test_reporting.py`의 `snapshot_report` 시험이다. 초기화 중 snapshot 목표를 단언하는 시험은 없음.
- 확신: 높음.
- 다른 영역: `engine.py`

#### OPS-12: import 승인 적용 전의 원문 재대조 중복을 없앤다
- 유형: 수신재검사중복
- 위치: `scripts/do_math/governance_engine.py:227-230`, `scripts/do_math/governance.py:986-987`(`_current_import`), `governance.py:1120`(`apply_import_control`이 `_current_import` 호출)
- 현상: `_governance_control`은 `apply_import_control`을 부르기 직전에 `_governance_input_source(input_id) != bundle['source']`를 검사한다(227-230). `apply_import_control`은 곧바로 `_current_import`를 부르고, `_current_import`는 같은 함수 `import_input_source`로 같은 비교를 한다(986-987). 두 검사 사이에 상태를 바꾸는 코드는 없다. 실패하면 두 검사 모두 `ValueError`를 내고, 같은 `except`(234-237)가 상태 복원과 재저작 요청을 처리한다. 엔진이 만드는 묶음은 항상 `input_ref`를 가지므로(`governance_engine.py:254-255`가 `input_ref=target` 전달), `input_ref`가 없는 경우를 위한 엔진 쪽 대체(`bundle['source']['id']`)는 도달하지 않는다.
- 제안: `governance_engine.py:227-230`의 사전 검사를 삭제한다.
- 동작: 보존. 거부 메시지만 "original source changed before later approval"에서 "original public input changed"로 바뀐다.
- 실익: 원문 복원(초기 입력이면 `original_input_bytes` 재검증 포함) 한 번과 4행이 준다.
- 위험과 보호: 오류 메시지를 단언하는 시험이 있으면 고쳐야 한다. 존재 여부는 미확인이다(grep하지 않았다).
- 확신: 중간. 제거 가능성은 확실하지만 메시지 의존 시험을 확인하지 않았다.
- 다른 영역: 없음.

#### OPS-13: 시각 해석 함수를 하나로 모은다
- 유형: 이음새중복
- 위치: `scripts/do_math/governance.py:332-338`(datetime 반환, 시간대 필수), `scripts/do_math/provider_wait.py:10-19`(float 초 반환, 시간대 없으면 None), `scripts/do_math/preflight.py:54-60`(UTC 오프셋 0 요구), 영역 밖의 `external.py:21`, `delegations.py:11`, `planning.py:664`, `observations.py:243`
- 현상: ISO 시각 문자열을 `Z` 치환 후 `datetime.fromisoformat`으로 해석하는 규칙이 일곱 곳에 있다. 같은 이름 `timestamp`인 두 함수(`governance.timestamp`, `provider_wait.timestamp`)는 반환 형식과 실패 처리가 다르다. `initialization.py:11`은 앞의 것을, `reporting.py:11`·`scheduled_operator.py:27`은 뒤의 것을 import한다. 이름이 같아 import 출처를 바꾸면 조용히 형식이 바뀐다.
- 제안: `file_io.py` 옆의 작은 모듈이나 `provider_wait.py`에 `parse_utc(value) -> datetime`(시간대 필수, UTC 변환, 실패 시 ValueError) 하나를 두고, 다른 형식은 그 위의 얇은 변환(`to_seconds`, `require_utc_offset`)으로 둔다. `governance.timestamp`와 `provider_wait.timestamp`는 서로 다른 이름으로 바꾼다.
- 동작: 보존. 각 호출처의 반환 형식과 실패 처리를 유지하는 변환을 둔다.
- 실익: 파싱 규칙 일곱 벌이 하나로 준다. 동명이형 함수의 혼동 위험이 사라진다.
- 위험과 보호: 호출처가 많아 영역 밖 수정이 크다. 덮는 시험은 `test_preflight.py::test_malformed_or_naive_high_water_is_rejected` 등 분산되어 있다.
- 확신: 중간. OPS 영역 안의 세 곳은 확인했고, 영역 밖 네 곳은 grep 행만 봤다.
- 다른 영역: `external.py`, `delegations.py`, `planning.py`, `observations.py`

#### OPS-14: 문서가 따로 적은 운영 기본값과 명령을 정본 한 곳에 두고 나머지는 가리키게 한다
- 유형: 이음새중복
- 위치:
  - 감독 주기 7200초·2시간: `SKILL.md:43`, `README.md:95`, `README.md:168`, `계약/독립-운영.md:13`, `references/CLI-실행-계약.md:187` ↔ `scripts/do_math/engine.py:101`, `scripts/do_math/scheduled_operator.py:113`
  - 복구 기한 여유 300초와 연구 예약의 무제한 `PT0S`: `README.md:461` ↔ `scripts/operator_schedule.ps1:51-52`
  - 기본 모델·슬롯: `SKILL.md:45`, `README.md:95`, `README.md:103-113`, `references/CLI-실행-계약.md:200-203`, `references/모델과-실행예산.md:15` ↔ `scripts/do_math/model_policy.py:7-9`
  - `plan_settle_seconds` 300: `SKILL.md:87`, `references/CLI-실행-계약.md:186` ↔ `engine.py:98`
  - 연구 예약 작업의 명령행: `README.md:185` ↔ `scheduled_operator.py:209-210`
  - 운영 기록 경로와 outcome 값: `README.md:187` ↔ `scheduled_operator.py:201`, `206`, `218-220`
- 현상: `references/CLI-실행-계약.md:186-187`이 설정 기본값 목록을 가지고 있다. 그런데 같은 값을 네 문서가 다시 적는다. 코드가 바뀌면 문서 다섯 곳을 함께 고쳐야 한다. 이 일치를 확인하는 시험은 없음(grep `2시간|7200|operator_interval_seconds` 결과 시험은 코드 인자만 단언한다).
- 제안: 수치 기본값은 `references/CLI-실행-계약.md`의 설정 목록 한 곳에 둔다. `SKILL.md`, `README.md`, `계약/독립-운영.md`는 "기본 주기는 CLI 실행 계약의 설정 목록을 따른다"처럼 가리킨다. 문서 수를 줄이지 않고 값을 남겨야 한다면, `DEFAULT_CONFIG`와 `model_policy`를 읽어 위 문서의 해당 문구를 대조하는 문서 정합 시험 하나를 추가한다. 명령행과 기록 경로(README 185, 187)는 운전자가 호스트 프로세스를 대조하는 데 쓰는 관찰 계약이므로 문서에 남기고, 같은 시험의 대상에 넣는다.
- 동작: 보존.
- 실익: 값 하나가 바뀔 때 고칠 문서가 다섯에서 하나로 준다(가리키기 방식). 또는 불일치가 시험으로 드러난다(시험 방식).
- 위험과 보호: `SKILL.md`는 역할 공통 문서이므로(`SKILL.md:162`) 문면이 바뀌면 역할 입력과 엔진의 설치 manifest가 바뀐다. 실행 중 인스턴스는 설치 문서 변경으로 정지할 수 있다(`README.md:294`). 덮는 시험은 없음.
- 확신: 높음(중복 사실). 두 방식 가운데 무엇을 고를지는 사용자 결정이다.
- 다른 영역: 모델·예산 영역(`model_policy.py`, `references/모델과-실행예산.md`), 문서 영역

#### OPS-15: `probe_codex.py`를 제거한다
- 유형: 불필요기능
- 위치: `scripts/probe_codex.py`(전체 182행), `scripts/tests/test_probe_codex.py:27-40`, 비교 대상 `scripts/probe_cli.py:58-133`, `scripts/do_math/model_runner.py:33-34`
- 현상: `probe_codex.py`는 Codex 어댑터를 저수준으로 직접 몰아 text·structured·tool·cancel 사례를 실행한다. 샌드박스는 `read-only`나 `workspace-write`이고 기본 `windows_sandbox`는 `elevated`다(`probe_codex.py:62-63`, `134`). 제품 실행은 `danger-full-access`와 `unelevated`를 쓴다(`model_runner.py:33-34`). elevated 구성은 실제 연구 실행에서 오류 1223을 냈다는 기록이 있다(`C:/math/기억/layer3/L-0020.md:88`). 제품이 실제로 쓰는 `ModelRunner` 경로의 Codex 대표 실호출은 `probe_cli.py --provider codex`가 이미 제공한다(`probe_cli.py:107-111`, `README.md:553`). `probe_codex.py`는 스킬 문서 어디에도 나오지 않고, 시험 하나(`test_missing_cli_preserves_failed_report_and_runs_no_cases`)만 이 스크립트를 실행한다.
- 제안: `scripts/probe_codex.py`와 `test_probe_codex.py`의 해당 시험을 삭제한다. 같은 파일의 `probe_cli` 시험은 남긴다.
- 동작: 변경(개발 도구). 사용자·운영자·AI 역할이 관찰하는 제품 동작은 바뀌지 않는다.
- 실익: 스크립트 182행과 시험 14행이 준다. bootstrap이 설치마다 복사·해시하는 파일이 하나 준다.
- 위험과 보호: `docs/do-math/boundary-repairs-2026-09-25/*.json` 같은 과거 증거의 파일 목록에 이름이 남아 있으나, 이 목록은 당시 snapshot의 기록이라 영향이 없다.
- 확신: 높음.
- 다른 영역: 없음.

#### OPS-16: `probe_native_isolation.py`를 스킬 밖 증거 도구로 옮기거나 제거한다
- 유형: 불필요기능
- 위치: `scripts/probe_native_isolation.py`(전체 339행), `scripts/tests/test_native_probe.py:7`, `scripts/tests/test_standalone.py:15-28`
- 현상: 이 스크립트는 "elevated Windows sandbox read-root isolation"을 재현한다(1행, 128행 `windows.sandbox="elevated"`). 제품은 이 구성을 쓰지 않고(`model_runner.py:33-34`), 기록상 elevated 구성은 읽기 격리가 성립하지 않았다(`L-0020.md:87`). 스킬 문서에는 언급이 없다. 시험 둘이 이 모듈의 보조 함수와 `--help` 동작만 검사한다.
- 제안: 사용자가 격리 재검토 가능성을 보존하려면 `C:/math/docs/do-math/` 아래의 증거 도구로 옮긴다. 그렇지 않으면 삭제한다. 어느 쪽이든 두 시험의 해당 부분을 함께 옮기거나 삭제한다.
- 동작: 변경(개발 도구).
- 실익: 스킬 배포 단위에서 339행이 빠지고, bootstrap 사본의 파일이 하나 준다.
- 위험과 보호: 향후 샌드박스 격리를 다시 평가할 재현 도구를 잃을 수 있다. 덮는 시험은 위 둘이다.
- 확신: 낮음. 이 도구를 보존할 가치는 사용자의 향후 계획에 달려 있다.
- 다른 영역: 없음.

## 3. 보존 판정

| 위치 | 겉보기 문제 | 유지 이유 |
|---|---|---|
| `scheduled_operator.py:197`, `313`, `362`, `cli.py:476-477` | `engine_start_guard`가 CLI, 감독, wake, 엔진 작업에서 반복 실행된다 | 각 실행이 다른 프로세스이고 사이에 시간이 흐른다. 예약 작업이 실제로 실행될 때의 상태를 다시 봐야 한다(TOCTOU). |
| `scheduled_operator.py:555-561` | 복구 뒤 `probe_cli.py --skill-only`를 subprocess로 실행한다. 같은 `inspect_bundle`을 프로세스 안에서 부를 수 있어 보인다 | frozen 감독 프로세스는 옛 코드를 import한 상태다. 새 프로세스로 live 설치를 import해야 수리된 코드가 적재되는지 확인된다. |
| `scheduled_operator.py:416-421`, `449-450` | 같은 실패에 대해 digest 두 개(`failure_identity`, `owner.failure_sha256`)를 다른 직렬화로 만든다 | 둘 다 저장되어 다시 대조된다. 이음새 계약 2.1절이 이미 보존으로 판정했다(계약 73행). |
| `engine.py:622-628` | 설치 manifest가 OPS-08의 전체 설치 집합보다 좁다 | 역할이 받는 문서와 엔진 코드만 보는 "실행 중 판본" 개념이다. 넓히면 README 같은 운전자 문서 변경에도 실행 중 연구가 정지한다. |
| `scripts/check_coverage.py` | 스킬 밖 `docs/do-math/`의 추적 문서를 검사하는 도구가 스킬 배포 단위 안에 있다 | `archive` 시험 그룹이 현재 판본에서 이 검사로 과거 증거의 무결성을 확인한다. 읽기 전용 실행 결과 오류 0건이다(`check_coverage.validate(...)` → `0 []`). 옮기면 시험 import 경로만 바뀌고 실익이 작다. |
| `governance_engine.py:261-264` | `check_import` 전에 원문 변화를 먼저 검사해 OPS-12와 같아 보인다 | 이 검사는 실패 시 재저작 요청을 먼저 큐에 넣는다. `check_import` 안의 같은 검사는 요청을 넣지 않으므로 결과가 다르다. |
| `governance_engine.py:49`, `61` | `validate_config`를 두 번 부른다 | 두 호출 사이에 `bind_host_configuration`이 `host_resources.constraint`를 다시 만든다(51). 뒤의 호출은 바뀐 값을 검사한다. |
| `governance.py:1014-1021`와 `interpretation_schema` | 출력 스키마와 수신 검사가 같은 조건을 두 번 표현한다 | 생산자가 모델 응답이므로 신뢰 경계 밖이다(기준 문서 원칙). 어휘 상수의 공유만 OPS-10에서 다룬다. |
| `operator_bootstrap.py:120`, `139`, `154` | 최초 freeze가 설치 트리 116개 파일(2,958,065바이트)을 네 번 해시한다 | 설치 명령에서만 실행되고 전체 약 12MB 해시라 비용이 작다(추정). 복사 전후 동일성 확인이 목적이다. |

## 4. 후보 없음

- `scripts/do_math.py`: CLI 진입점 7행이다.
- `scripts/test_categories.py`: `UNIT_MODULES` 목록의 모든 이름이 실제 시험 파일과 일치한다(읽기 전용 확인 `missing []`). 장식자와 모듈 목록은 기본값과 예외라는 서로 다른 역할이다.
- `scripts/do_math/initialization.py`의 능력 증거 경로(`capability_requirements`, `_capability_batch_requirements`): `capability_identity`는 `cached_sha256`로 계산되어 반복 호출 비용이 작다(`codex_adapter.py:124-136`). 복구의 두 번 호출(`scheduled_operator.py:435-444`)도 문제가 아니다.
- `계약/운영-점검.md`, `계약/유지보수.md`, `계약/목표-감사.md`: 코드 상수나 명령을 따로 적는 곳이 없다. 설치 수리 대상 접두어 `installation:`은 `repair_execution.py:133`과 일치한다.
- `references/초기화-운전.md`, `references/초기화-효율과-정비.md`: 초기화 grant 조건(`초기화-운전.md:116`)이 `initialization.py:14`, `227-228`과 일치한다. 신뢰 환경 부분은 직전 라운드(G1) 소유라 조사하지 않았다.
- 초기화 단계와 사전 검사의 중복(파견문의 셋째 관점): `activation_requirements`(`initialization.py:139-220`)와 `inspect_current_state`(`preflight.py:29-63`)는 검사 항목이 겹치지 않는다. 앞의 것은 채택·권한·능력·용량 관문이고, 뒤의 것은 판본·lifecycle·상태 값의 구조 검사다. 실제 중복은 사전 검사 자체의 재실행이며 OPS-07에서 다룬다.

## 5. 미완료

- OPS-07: lifecycle 없는 최소 상태를 저장하는 시험의 수를 세지 못했다. fixture 구성이 다양해 전수 grep 식을 확정하지 못했다.
- OPS-09: `record_schemas/__init__.py` 240행 이후의 grant 검사가 `validate_grant_source`를 쓰는지 확인하지 않았다.
- OPS-12: 거부 메시지를 단언하는 시험의 존재를 grep하지 않았다.
- OPS-03: 상태 재적재 비용을 측정하지 못했다(6절).

## 6. 작업 중 사건

- 파견문은 "예약 작업의 등록·조회·제거가 PowerShell과 Python 양쪽에 따로 구현된 곳"을 볼 대상으로 들었다. 전수 검색 결과 이 전제는 성립하지 않았다. 조사 대상을 두 언어 사이의 인자 계약 중복으로 바꾸었다(OPS-04).
- OPS-03의 비용을 재려고 `C:/math/.skill-workspace/nat-add-zero-fresh-20260926/repo`(인스턴스 `RI-01M3CN7251W9XX24TVMH4SZSDV`)를 읽기 전용으로 적재했다. 현행 계약 검증이 `execution_profiles/.../machine`의 구판 필드(`tool_manifest`, `tool_manifest_scope`)를 거부해 적재하지 못했다. `AGENTS.md:6`에 따라 구판 인스턴스는 호환 대상이 아니므로 결함으로 다루지 않았다. 대신 절감량을 추정으로 적었다.
- `write-for-reader` 스킬의 별도 독해 절차는 합의·독자 파일과 `.codex/writing-flow/` 상태 파일을 요구한다. 기준 문서의 "산출 파일 하나만 쓴다"는 금지와 충돌하므로 실행하지 않았다. 스킬의 품질 규칙과, `경중_배분.md`가 독해 없는 글에 허용하는 대조(가장 긴 대목과 경중 선언의 대조)만 적용했다.
- graphify는 사용하지 않았다. 읽을 파일이 파견문에 명시되어 있어 원문을 직접 읽었다.

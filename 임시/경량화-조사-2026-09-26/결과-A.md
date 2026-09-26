# 결과-A: 실행 수명·예산·공급자 대기·예약 감독

이 문서는 do-math 경량화 2라운드 그룹 A의 반환이다. 설계 `docs/do-math/경량화-설계-2026-09-26.md` 6절의 다섯 항목을 순서대로 적는다. 1절에서 표의 ID마다 처분을 확인할 수 있다. 2절에는 이 그룹이 만든 공유 정의와 위치를 적었고, 통합자는 이를 보고 이음새 계약에 올릴지 정한다. 3절은 문서 단계에 넘길 변경 목록이다. 결정 4 착수 전에 한 운영 역할 동시 실행 확인은 0절에 따로 적었다. 통합자 지시에 따라 이 확인은 보고용이며, 결정 4는 조건 없이 구현했다.

- worktree `C:/math-worktrees/r2-a`, 브랜치 `r2-a`, 커밋 `6b0bac2`(기준 `24682fd`, 커널 병합 뒤).
- 변경 범위: 제품 `scripts/do_math/` 35개 파일, `scripts/operator_schedule.ps1`, `examples/claude-codex-sessions.json`, 시험 52개 파일. 합계 89개 파일, 1400줄 추가, 1419줄 삭제.
- 좌표는 따로 적지 않으면 `C:/math-worktrees/r2-a/.claude/skills/do-math/scripts/` 기준이고, 행 번호는 커밋 `6b0bac2`의 것이다.
- 시험은 실행하지 않았다(설계 3.3). 바꾼 Python 파일 87개는 모두 `python -m py_compile`을 통과했다.

## 0. 운영 역할의 동시 실행 상한 확인(결정 4, 보고만)

1.3절이 예상한 두 제한 가운데 하나는 코드에 있고, 하나는 성립하지 않는다.

- **있는 제한.** 계획과 준비는 역할마다 한 번에 하나만 실행된다(`do_math/scheduler.py:494`). 같은 역할·대상·단계의 요청은 대기열에서 병합된다(`do_math/engine.py`의 `_enqueue` 비교 키). 라이브 운영 점검은 대상 실행마다 하나다(`scheduler.py:491`의 identity 키).
- **성립하지 않는 제한.** 운영 점검 수가 실행 중인 작업 수를 넘지 않는다는 제한은 없다. 결정 4 뒤에는 모델 슬롯도, 기본 설정의 호스트 한도(`host_resources` 없음)도 아래 세 경로를 막지 않는다.
  1. `intent_interpretation`은 사용자 입력마다 하나씩 대기열에 들어간다(`engine.py:967`). 대상이 입력 ID라서 서로 병합되지 않는다. 입력 N개는 N개가 동시에 실행된다.
  2. `maintenance`는 한 출력의 `kind_definitions` 항목마다 하나씩 들어간다(`engine.py:4197`). 이 배열에는 `maxItems`가 없다(`submission.py:209`). 영향 검토 요청마다 들어가는 경로도 있다(`engine.py:1138`).
  3. 라이브가 아닌 `operational_review`는 실패한 계보마다 하나씩 들어간다(`repair_execution.py:22`, `decision_engine.py:204`). 실패한 작업이 쌓이면 실행 중인 작업 수와 무관하게 늘어난다.
- 전에는 운영 풀의 모델별 운영 슬롯(기본 3)이 이 셋의 상한이었다. 지금은 사용자 입력 수, 한 출력의 제안 수, 실패 수만이 상한이다. 결정 4에 상한이 필요한지는 통합자와 사용자의 판단으로 넘긴다.

## 1. ID별 처분

4.2절 표의 모든 ID와 추가 배정을 처리했다. 부분 구현은 RUN-05와 RUN-21 두 건이다. 둘 다 남은 범위가 그룹 D 소유의 함수(`activities.requeue_recovered_execution`, RES-14로 삭제 예정)에 있어서 손대지 않았다. 설계의 "현재 원문에 맞는 방법으로 같은 결과" 원칙에 따라 조사 제안과 다르게 구현한 곳은 각 행과 5절에 적었다.

| ID | 처분 | 내용 |
|---|---|---|
| 결정 4 | 구현함 | 아래 네 부분으로 나누어 적는다. |
| 결정 4 (1) 예산 구조 | | `model_policy.LIMITS`와 설정 `session_limits`는 `{"work": {...}}` 하나다. 동시성 제약 행은 `{model, accounting_unit, work_slots, scope}`이고 `operations_slots`·`total_slots`가 없다(`execution_profiles.py:198-204`). `budget._check_concurrency`는 제약마다 `work_slots` 하나만 본다. |
| 결정 4 (2) 운영 역할 | | 작업 역할의 AI 프로필만 `ai.capacity_refs`를 가진다. 운영 AI 역할은 `[]`이고, `validate_profile`이 이 불변식을 검사한다(`execution_profiles.py:82-83`). 운영 역할은 `acquire`에서 모델 예약 없이 바로 배정된다. 호스트 한도가 있으면 호스트 예약은 유지된다. 기계 역할은 전과 같다. |
| 결정 4 (3) `budget_kind` 제거 | | 프로필, 실행, action, 예약 기록, 대기 기록, grant, 외부 작업 기록에서 `budget_kind`를 없앴다. 스키마도 같이 바꿨다(`record_schemas/schemas.py`, `domains.py`). 이 값에 달린 분기는 역할 기준으로 바꾸거나 지웠다. 관찰 모드와 운영 호출 기한·마무리 예고는 `role in WORK_ROLES`로 판정한다(`execution_profiles.py:84-85`, `engine.py` `_call_steps`, `model_runner.py:66`). grant의 "resource pool outside grant"는 지웠다(`governance.py`, 그룹 F 파일에서 한 줄). 초기 grant의 `budget_kind == "operations"` 요구도 지웠다(`initialization.py:216-217`, 그룹 F 파일에서 한 줄). |
| 결정 4 (4) 운영 풀 전용 코드 제거 | | 활성화 요구 `operations_capacity`와 `initialization.operations_capacity_available`을 지웠다(그룹 F 파일). 상태 검사는 제약마다 `work_slots` 초과만 본다(`state_checks.py:352-360`, 그룹 B 파일에서 최소 변경). 예시 설정 `examples/claude-codex-sessions.json`의 `operations` 맵을 지웠다. |
| STO-11, ENG-12, IO-20 | 구현함 | 설정 절의 정본은 `record_schemas.config_schema()`다(`record_schemas/__init__.py:155-190`). 키, 형, 범위, 열거를 여기에 모았다: 양의 정수 키 `POSITIVE_SETTINGS`, 노력 값 `EFFORTS`, `session_limits`는 `work`만. 파생은 셋이다. ① 저장 스키마는 `install()`이 이 함수를 쓴다. ② configure 제어 모양은 `control_contracts._configure_validator()`(`control_contracts.py:76`)가 키마다 JSON 형만 남겨 만들고 `additionalProperties: false`를 둔다. ③ `engine.validate_config`(`engine.py:160`)는 모르는 키를 거부하고, 호스트 절을 뺀 전체 설정을 정본 스키마로 검사한 뒤 교차 조건만 직접 본다. 교차 조건은 모델 정책, 재시도 최대 ≥ 초기, `lean_command`의 NUL, 호스트, scholarly다. `CONFIG_PATCH`와 `OPTIONAL_CONFIG`는 지웠다. 결정 4로 사라진 `operations` 키도 뺐다. |
| RUN-01 | 구현함 | `execution_lifecycle.release_or_hold(execution, slots, *, at)`(`execution_lifecycle.py:174`)가 반환과 반환 실패 처리를 한 번에 한다. 반환 실패 처리는 stopping/terminating 전이와 오류 기록이다. 네 끝점이 이 함수를 쓴다: AI(`engine.py` `_call_steps`), 형식 검사(`engine.py` `_formal_steps`), 기계(`lifecycle_engine.py:1113`), 설치 복구(`scheduled_operator.py` `recovery`). 오류 문구는 하나로 통일했다. 이미 있는 오류는 덮지 않는다(5절). |
| RUN-02 | 구현함 | `SessionSlots.started(execution_id, identity, *, at)`(`session_slots.py:221`)가 발사표 검증, `capacity.process` 기록, running 전이, `started_at`을 맡는다. 세 콜백(`_machine_started`, AI `started`, 복구 `on_started`)에는 경로별 부가 기록과 저장만 남았다. |
| RUN-03 | 구현함 | 실행 레코드의 `process` 쓰기와 스키마 항목을 지웠다. 정본은 `capacity.process`다. 읽는 곳을 옮겼다: `model_runner.verified_native_final`(그룹 E 파일, 두 줄), `end_preparation`, `engine.py`의 재개 검사, `provider_engine`. `activities.py:204`는 5절 참조. |
| RUN-04 | 구현함 | `launch.mark_dispatched`, `launch.mark_returned(ticket, result=None)`(`launch.py:44-65`)를 두고 여섯 대입을 바꿨다. `mark_returned`는 이미 끝난 phase를 그대로 둔다. 기계 종료의 "not_started 보존" 조건은 `result=None`일 때의 규칙으로 흡수했다. |
| RUN-05 | 부분 구현 | `session_slots.held_reservations(runtime, owner_ids=None)`와 `quiescence(runtime)`(`session_slots.py:25-35`)를 두었다. `decision_engine`, `governance_engine`(두 곳과 호스트 변경 조건), `review_engine`, `lifecycle_engine`(recovery_checked), `maintenance_gate`, `engine`이 이를 쓴다. `engine.py`의 없는 필드 비교(`status != "released"`)는 `held_reservations`로 고쳤다. 이중 조건은 `local_termination == "confirmed"` 하나로 줄였다(5절: 조사 제안과 방향이 반대). 남은 곳은 `activities.py:202-204` 한 곳이다. |
| RUN-06 | 구현함 | `SessionSlots.provider_result_from_run(execution_id, result, config)`(`session_slots.py:272`)가 러너 결과에서 failure와 응답 관찰을 꺼낸다. provider는 `capacity.provider`에서 읽는다. 모델 잠금 위반은 모듈 함수 `provider_engine.record_model_policy_violation`(`provider_engine.py:8`)으로 꺼냈다. 엔진과 설치 복구가 둘 다 이것을 쓴다. |
| RUN-07 | 결정 4로 대체 | 운영 풀과 `total_slots`가 사라져 표시와 배정의 불일치 원인이 없어졌다. 표시(`snapshot`)는 모델별 작업 슬롯 표 하나를 돌려준다. |
| RUN-08 | 구현함 | `provider_wait.gate_open(row, now)`(`provider_wait.py:35`)가 정본이다. 배정 사전 확인(`SessionSlots.provider_wait`), 스냅숏의 `open`(전의 `due` 대체), 감독의 재관찰 기동이 이것을 쓴다. 재큐 쪽 판정은 RUN-09로 없어졌다. |
| RUN-09 | 구현함 | 한도 실패 뒤의 요청은 `_requeue_provider_action`(`provider_engine.py:92`)이 대기열에 되돌린다. 이때 `recovery`와 `dispatch_wait`(게이트 정보)를 붙이고, 활동은 `wait_for("provider admission deferred")`로 둔다. `_hold_provider_action`, `_retry_provider_actions`, `waiting_actions`의 provider_limit 항목과 그 스키마 필드(`provider`, `generation`, `retry_at`)를 지웠다. 감독 기동 판정은 대기열 요청의 공급자 게이트가 열렸는지를 본다(`scheduled_operator.py:299`). 역할 입력에서 읽는 곳의 확인 결과는 5절에 적었다. |
| RUN-10 | 구현함 | `provider_wait_disposition`과 `activity_wait` 쓰기, 스키마 항목을 지웠다. |
| RUN-11 | 구현함 | `retry_time`, `provider_result_from_run`(설정에서 읽음), `execution_window.notice_seconds`(`config["finish_notice_seconds"]`)의 기본값 사본을 없앴다. |
| RUN-13 | 구현함 | 수용 계산은 순수 함수 `SessionSlots._admission(profile, execution_id, current)`(`session_slots.py:74`)다. `admission_check`는 이것만 부르므로 uuid, Win32 호출, 전이, 가짜 실행이 없다. `acquire(execution_id, *, profile, execution, current_time=None)`는 같은 계산을 잠금 아래 다시 하고 기록한다. `pool`·`model`·`provider` 인자와 동일성 검사, `provider_result`의 provider 인자를 없앴다. 단일 풀 구조를 전제로 한다. |
| RUN-14 | 구현함 | `BudgetReplayConflict`, `ReservationPlan`, `SettlementPlan`, `canonical_record_bytes`, 재실행 분기, 요청 상수 검사를 지웠다. `plan_reservations`는 레코드 tuple을, `settle_reservation`은 레코드를 돌려준다. 이미 있는 ID와 held가 아닌 예약의 정산은 `BudgetInputError`다. K-제품 이음새 요청의 `budget.canonical_record_bytes` 사본도 이로써 없어졌다. |
| RUN-15 | 구현함 | `SessionSlots.configure`와 그 호출을 지웠다. 판본 반영은 `execution_profiles.apply_editions(instance, editions)`(`execution_profiles.py:252`) 하나이고, `initialize`와 `_configure_candidate`가 함께 쓴다. |
| RUN-16 | 구현함 | `model_policy.selection(..., *, instance=None)`(`model_policy.py:102`)은 기본 배정에 `instance["role_profile_refs"]`를 쓰고 판본을 다시 만들지 않는다. `work_profile_selection`의 셋째 인자도 인스턴스다. 호출부 10곳을 바꿨다(cli, context_store, decision_engine, input_recovery, lifecycle_engine, scheduler, planning, engine). |
| RUN-17 | 구현함 | `session_slots.py:16-22`에 `PROVIDER_WAIT`, `SLOT_WAITS`, `RESOURCE_WAITS`, `ADMISSION_WAITS`를 두었다. `reporting`, `governance_engine`, `scheduler`, `engine`이 이 상수를 쓴다. |
| RUN-18 | 구현함 | 엔진의 `_slots` 캐시, 재결합 코드, 동일성 검사를 지웠다. `_session_slots()`(`provider_engine.py:17`)가 매번 새 뷰를 만든다. |
| RUN-19 | 해당 없음(그룹 C) | 표에 없음. |
| RUN-21 | 부분 구현 | `execution_lifecycle.drive_to_termination`(`execution_lifecycle.py:163`)을 두고 `recover_execution`과 `_settle_recovered_execution`이 함께 쓴다. 쓰이지 않는 관찰 종류 `no_substantive_action`·`checkpoint_deadline_elapsed`와 `local_termination_observed` 분기를 지웠다. capacity가 없는 실행은 종료 장벽이 없으므로 False다. 남은 곳은 `activities.requeue_recovered_execution` 한 곳이다(그룹 D의 RES-14 소관이라 두었다). |
| RUN-22 | 구현함 | `_instance_closed()`, `_request_stop_all(reason)`(`lifecycle_engine.py:114-123`)로 일곱 판정과 세 반복문을 모았다. 없는 실행 상태 `'finished'` 비교가 사라졌다. |
| RUN-23 | 구현함 | `release`의 두 번째 `named_job_empty` 조회를 지웠다. |
| RUN-26 | 구현함 | `windows_job._filetime(value)`(`windows_job.py:582`)를 세 곳이 쓴다. |
| ENG-05 | 구현함 | 손 쓰기 12곳, `_save`의 재계산, 저장 필드 `active_execution(s)`, 스키마 항목, 참조 함수를 모두 지웠다. `status()`가 두 값을 실행 목록에서 계산한다. |
| ENG-06 | 구현함 | `ResearchEngine._call`과 `_run_machine_steps`의 동기 분기, `_local_call_returned` 이중 호출을 지웠다. lifecycle 기계 continuation의 `if self._calls is not None` 조건도 지웠다. 실패 결과는 `parallel.failed_result(error)`(`parallel.py:19`) 하나다. 시험용 도우미 `state_fixtures.owner_calls`, `start_model_call`을 두었다. |
| ENG-15 | 구현함 | `engine._preserve_outputs(execution_id, workspace, bundle, *, max_bytes, evidence_dir=None)`(`engine.py:1079`)를 정상 종료와 소실 복구가 함께 쓴다. 복구 경로도 이제 `output-manifest.json`·`omitted.json`을 보존하고, 체크포인트 참조의 중복 쓰기가 없어졌다. |
| ENG-21 | 구현함 | 수용 판정 블록을 `scheduler._admissible(action, profile)`(`scheduler.py:516`)로 모았다. 지역 import와 무효 분기(프로필은 한 번 계산)를 지웠다. `ModelCalls.start` 포장을 지웠고 이벤트 튜플은 3원소가 되었다. |
| OPS-01 | 구현함 | 감독 판정 정본은 `scheduled_operator.supervision_block(facts)`와 우선순위 표 `SUPERVISION_BLOCKS`다. 표는 `held, disabled, user_pause, maintenance, model_policy, paused, closed, completed, conversation_lost, installation_repair` 순서다. 사실은 `supervision_facts(instance, runtime)`(`scheduled_operator.py:179-201`)가 만든다. 각 지점은 사유 코드를 전의 outcome 문자열로 바꾼다: `run_engine`, `engine_start_guard`, `reconcile_wake`, `check`, `recovery`, `reporting.operating_summary`, 엔진 `status()`, 엔진 `_schedule_provider_wake`. 엔진 쪽 wake 재조정이 정비 fence를 보게 되었다(승인된 동작 변경). 위치 선택과 우선순위 차이는 5절. |
| OPS-02 | 구현함 | `check`는 status 하나로 판정하고 저장소를 다시 적재하지 않는다. 운영 활성 여부와 설치 수리는 status의 감독 사실에서 읽는다. 비-probe 설치 수리는 `recovery(repository, instance, workspace)`가 잠금 안에서 failure를 만든다. probe만 status의 snapshot을 적재해 failure를 계산한다(반환 모양 유지). `reconcile_wake`가 조회한 예약 상태는 `observed`로 돌려받아 재조회하지 않는다. |
| OPS-03 | 구현함 | `reconcile_wake(repository, instance, workspace, *, facts, providers)`는 호출자의 감독 사실과 provider 스냅숏을 받고 저장소를 적재하지 않는다. 엔진은 메모리 상태를 넘긴다. |
| OPS-04 | 구현함 | PowerShell 어댑터가 `$PSScriptRoot`로 부트스트랩을 찾는다. `-Entrypoint`와 `ENTRYPOINT`를 지웠고, install의 재대입은 `$frozenBootstrap`이다. 간격·기한 인자는 선택 인자이고 install에서만 넘기고 검사한다. Python `schedule()`의 기본값 7200·5400과 간격 검증을 지웠다. 동작 이름은 `SCHEDULE_ACTIONS` 상수다. `cancel_wake`, `hold_pause_reason`을 두어 CLI의 복제를 대체했다. CLI는 install에서만 설정을 읽는다. |
| 추가 배정: 방어 getattr 5곳 | 구현함 | `engine.py`의 `_clock_anchor`·`_stop_deadlines`, `lifecycle_engine.py:83`, `scheduler.py:54`·`66`을 직접 접근으로 바꿨다. 같은 이유로 남아 있던 `engine.py`의 `hasattr(self, "_trackers")`와 `scheduler.py`의 `hasattr(self, '_live_execution_ids')`도 지웠다. 후자는 ENG-06의 동기 분기와 함께 없어졌다. |

## 2. 만든 공유 정의와 위치

커널 표에 없던 공유 정의를 그룹 A 소유 모듈에 하나씩 만들었다(정정된 계약 (2)). 이름과 위치는 아래와 같다.

| 정의 | 위치 | 규칙 |
|---|---|---|
| `held_reservations(runtime, owner_ids=None)`, `quiescence(runtime)` | `session_slots.py:25-35` | 보유 중인 예약, 정지 판정(미종료 실행·보유 예약) |
| `PROVIDER_WAIT`, `SLOT_WAITS`, `RESOURCE_WAITS`, `ADMISSION_WAITS` | `session_slots.py:16-22` | 배정 대기 종류의 의미별 집합 |
| `SessionSlots.provider_wait`, `_admission`, `provider_result_from_run`, `started(..., at)` | `session_slots.py` | 공급자 대기 기록, 순수 수용 계산, 러너 결과 반영, 시작 기록 |
| `gate_open(row, now)` | `provider_wait.py:35` | 공급자 게이트 개폐 |
| `mark_dispatched`, `mark_returned` | `launch.py:44-65` | 발사표 phase 전이 |
| `drive_to_termination`, `release_or_hold` | `execution_lifecycle.py:163-186` | 종료 장벽까지 전이, 반환 또는 보류 |
| `apply_editions(instance, editions)` | `execution_profiles.py:252` | 판본 채택 |
| `failed_result(error)` | `parallel.py:19` | 계산 예외의 결과 모양 |
| `record_model_policy_violation(...)` | `provider_engine.py:8` | 모델 잠금 위반 기록과 정지 |
| `supervision_facts`, `supervision_block`, `SUPERVISION_BLOCKS`, `cancel_wake`, `hold_pause_reason`, `SCHEDULE_ACTIONS` | `scheduled_operator.py:37-201` | 감독 판정과 예약 어댑터 계약 |
| `config_schema()`, `EFFORTS`, `POSITIVE_SETTINGS` | `record_schemas/__init__.py:155-190` | 설정 절 정본 |
| 엔진 메서드 `_session_slots`, `_requeue_provider_action`, `_preserve_outputs`, `_admissible`, `_instance_closed`, `_request_stop_all` | 각 믹스인 | 모듈 내부 정의 |
| `_filetime` | `windows_job.py:582` | 모듈 내부 |
| 시험 도우미 `owner_calls`, `start_model_call` | `tests/state_fixtures.py` | 동기 경로를 대신하는 ModelCalls 실행 |

**이음새 요청**

- `supervision_facts`는 조사 제안의 `reporting` 대신 `scheduled_operator`에 두었다(5절). 이음새 계약에 올릴 때 위치를 확인한다.
- `config_schema()`는 설계 2절 표의 "저장 스키마의 설정 절"이다. 이음새 계약 표의 해당 행에 이 이름을 적는다.

**추가·변경한 이름**

- status 키 `operator_enabled`를 더했다(감독 사실).
- 제거한 status 키는 둘이다. `waiting_actions` 항목의 `retry_at`, 그리고 `status()["budget"]`의 풀 계층이다. `budget`은 이제 모델별 표 하나다.
- 저장 필드를 제거했다: `active_execution`, `active_executions`, 실행의 `process`와 `budget_kind`, 예약·프로필·grant·외부 작업의 `budget_kind`, 제약의 `operations_slots`·`total_slots`, 대기 기록의 `activity_wait`·`provider`·`generation`·`retry_at`.
- 설정 키는 추가하지 않았다. `session_limits.operations`를 제거했다.

## 3. 필요한 문서 변경

문서 단계가 반영한다. 스킬 문서는 고치지 않았다. 좌표는 `C:/math-worktrees/r2-a/.claude/skills/do-math/` 기준이다.

- **결정 4(단일 작업 풀)**
  - `SKILL.md:45`: "각 모델에 운영 슬롯 3개와 작업 슬롯 3개"를 작업 슬롯만으로 고친다. 운영 역할은 슬롯 없이 역할 등급 모델로 바로 배정한다.
  - `README.md:93-117`: 설정 예시의 `operations` 맵과 "운영 슬롯" 서술(115, 117행)을 고친다.
  - `references/CLI-실행-계약.md:177, 187, 201-203, 212, 216, 243, 909`
    - `session_limits`는 `work`만 둔다.
    - 복구 AI는 운영 슬롯을 쓰지 않는다.
    - status `budget`은 모델별 표 하나다. `execution_attempts`는 역할로 센다.
    - `run`의 "독립된 운영 슬롯" 서술을 고친다.
  - `references/모델과-실행예산.md:11, 23, 95, 109, 117`
    - 운영·작업 별도 용량 서술을 단일 작업 풀로 바꾼다.
    - 운영 역할은 예약 없이 배정된다.
    - 0절의 상한 부재를 적을지는 판단이 필요하다.
  - `references/초기화-운전.md:130`: 초기 grant 예시의 `"budget_kind": "operations"`를 지운다. grant는 이 필드를 받지 않는다.
  - `계약/독립-운영.md:59`: "운영 슬롯 반환"을 "로컬 실행 종료 확인"으로 고친다.
  - 활성화 요구 목록에서 `operations_capacity`를 뺀다(초기화 문서에 있다면).
- **RUN-09(공급자 한도 대기)**: `모델과-실행예산.md:117`과 공급자 한도를 서술하는 곳을 고친다. 한도에 걸린 요청은 `waiting_actions`가 아니라 대기열 요청의 `dispatch_wait`(kind `provider_limit`)로 보인다. status의 `waiting_actions`에는 `retry_at`이 없다. provider 스냅숏 행은 `due` 대신 `open`을 가진다.
- **ENG-05**: `CLI-실행-계약.md:216` 부근. `active_execution(s)`는 저장 필드가 아니라 status 계산값이다.
- **OPS-01**: `README.md:239` 부근의 `primary_blocker` 서술은 그대로 두어도 된다. 우선순위는 user_pause, maintenance_fence, model_policy, paused, installation_repair로 전과 같다. 종결·완료 상태에서는 설치 수리를 차단 사유로 내지 않는다.
- **OPS-04**: 운영 예약 어댑터를 서술하는 곳에 적는다. 어댑터는 자기 옆의 `operator_bootstrap.py`를 쓰고, 간격·기한 인자는 install에만 넘긴다.
- **설정 절(STO-11 등)**: `CLI-실행-계약.md:212`. 설정 오류 문구가 `config/<키>: <jsonschema 메시지>` 형식으로 바뀌었다. 양의 정수 범위를 저장 설정도 강제한다.
- **역할 입력**: `resources`는 모델별 표 하나다. `profile_selection.allowed_profiles`에 `budget_kind`가 없다. 연구 계획 역할 문서가 풀 계층을 가정하면 고친다.
- **이음새 계약** `docs/do-math/검사-경량화-이음새-계약.md`: 2절 표를 통합자가 옮길 때 이 문서 2절의 정의를 더한다.

## 4. 고친 시험 파일과 확인하지 못한 위험

시험 52개 파일을 새 계약에 맞췄다. 공용 픽스처는 내가 고쳤다. 나머지 시험 파일은 서로 겹치지 않는 일곱 묶음으로 나눠 작업자에게 맡겼다(`gp-opus-medium`). 입력은 변경 목록 `C:/math-worktrees/reports/r2-a/시험-변경목록.md`다. 셋째 묶음은 도중에 API 오류로 멈췄고, 남은 다섯 파일은 내가 마쳤다.

- **공용 픽스처**
  - `tests/research_fixtures.py`: `selection(instance=)`, 초기 grant의 `budget_kind`를 제거했다.
  - `tests/state_fixtures.py`: `active_execution`을 제거하고 `owner_calls`·`start_model_call`을 추가했다.
  - `tests/test_lifecycle_engine.py`의 `FakeEngine.grant`: `budget_kind`를 제거했다.
  - `tests/test_model_metadata_boundary.py`: 배정 밖에서 찾아 고쳤다.
- **고친 시험 파일**
  - test_approved_five_repairs, test_budget, test_checkpoint_persistence, test_claude_adapter, test_connection_repairs, test_controls, test_current_contract, test_currentness_recovery, test_delegation_storage, test_diagnosed_installation_recovery
  - test_efficiency, test_engine, test_execution_window, test_formal_runtime, test_governance_engine, test_host_resources, test_initial_intent_connection, test_initialization_review_repairs, test_input_recovery, test_knowledge_import_engine
  - test_lifecycle_engine, test_machine_parallel, test_machine_scheduling, test_native_final_submission, test_observation_audit1, test_operator, test_provider_recovery, test_provider_wait, test_purpose_engine, test_redesign_ACTIVITIES
  - test_redesign_ENGINE, test_redesign_GOVERNANCE, test_redesign_OBSERVATION, test_redesign_PROFILES, test_redesign_STORAGE, test_redesign_TASKS, test_repair_plan, test_reporting, test_review_engine, test_review_research
  - test_review_scope_wire, test_run_feedback, test_schedule_pythonw, test_session_scheduler, test_six_connections, test_state_checks, test_static_review_repairs, test_stop_flags, test_walkthrough_contract_repairs, test_walkthrough_followup
- **지운 시험**. 폐기된 기능만 검사하던 것이다.
  - `test_provider_wait.test_empty_nonmapping_failure_is_rejected`: `provider_wait_disposition`이 폐기되었다.
  - `test_host_resources.test_session_reconfiguration_cannot_silently_remove_host_approval`: `SessionSlots.configure`가 폐기되었다. 이 보호를 엔진 수준 시험으로 다시 만들지는 통합 단계에서 정한다.
  - `test_session_scheduler.test_failed_work_waits_for_diagnosis_when_its_operating_model_is_full`: 운영 풀이 폐기되었다.
  - `test_redesign_ACTIVITIES.test_starting_no_substantive_action_has_a_legal_terminal_path`: 관찰 종류가 폐기되었다.
  - `test_governance_engine`의 실행 중 모드 전환 부분.
  - `test_redesign_GOVERNANCE`의 grant 풀 범위 부분.
  - 그 밖에 풀 관련 단언은 새 계약의 같은 뜻(운영 실행에 execution 단위 예약이 없음, 작업 프로필만 `capacity_refs`를 가짐)으로 옮겼다.

**확인하지 못한 위험**. 실행하지 않았으므로 모두 미확인이다.

1. **동기 경로 제거로 바뀐 시험.** 형식 검사·신뢰 검사·AI 호출을 직접 부르던 시험은 `owner_calls` 안에서 ModelCalls로 돈다. 계산이 이제 작업 스레드에서 돈다. 계산 안에서 엔진 상태를 바꾸던 대역(`test_lifecycle_engine`의 `formal_behavior=stop`, `test_knowledge_import_engine`의 `change`)은 작업 스레드에서 상태를 바꾼다. 소유자는 그동안 기다리기만 하지만 경합 여지가 있다. `test_connection_repairs`는 제어를 소유자 쪽에서 적용하도록 옮겼다.
2. **capacity 없는 실행.** `_settle_recovered_execution`이 capacity 없는 실행에 False를 돌려준다. 그래서 최상위 `process`만 가진 합성 실행으로 복구를 검사하던 시험에는 capacity 레코드를 넣었다(`test_checkpoint_persistence`, `test_currentness_recovery`, `test_repair_plan`). 다른 시험에 같은 전제가 숨어 있으면 복구가 "reservation settlement not confirmed"로 멈춘다.
3. **운영 활성 여부의 기본값.** `supervision_facts`는 `operator_enabled`가 없으면 비활성으로 본다. 전의 `check`·`recovery`는 없으면 활성으로 봤다. 저장 설정에는 항상 이 키가 있다. 손으로 만든 시험 상태에는 키를 넣었다.
4. **감독 우선순위 변경.** 공존 조합에서 일부 outcome 문자열이 바뀐다(5절). 이런 조합을 단언하는 시험은 찾지 못했다.
5. **설정 오류 문구.** 설정 오류 문구가 jsonschema 메시지로 바뀌었다. 문구를 단언하는 시험은 찾지 못했다.
6. **작업자가 확신이 낮다고 적은 수정.**
   - `test_repair_plan`: 설정 변경 시험의 대기 요청 역할을 goal_audit으로 바꿨다.
   - `test_redesign_TASKS`: 가짜 `capacity_refs` ID를 쓴다.
   - `test_provider_wait`: 새 저장 시험이 `time.time`을 전역 패치한다.
   - `test_session_scheduler`: 출력 수리 대기열 시험이 `_dispatchable` 대역을 쓴다.
   - `test_redesign_PROFILES`: 감독 시험이 `repository.assert_not_called()`로 추가 적재 없음을 단언한다.

## 5. 전제가 틀렸거나 계획을 바꾼 지점

1. **결정 4의 진행.** 처음 파견문과 설계 1.3절에 따라 상한 없는 경로(0절)를 찾았을 때는 예산 변경을 미루려 했다. 그 뒤 통합자가 정정했다. 결정 4는 조건 없이 구현하고, 상한 확인은 보고만 한다. 구현 전에 정정되었으므로 되돌린 코드는 없다.
2. **`budget_kind`는 필드 전체를 지웠다.** 설계는 "운영 값과 그 분기"의 제거를 요구했다. 남는 값이 "work" 하나뿐이면 필드는 정보를 담지 않는다. 그래서 필드를 지우고, 슬롯 예약 여부는 `ai.capacity_refs`로, 역할 구분은 `WORK_ROLES`로 표현했다. 운영 호출 기한과 마무리 예고는 예산이 아니라 역할의 책임이므로 동작을 유지했다.
3. **운영 역할의 모델 선택은 바꾸지 않았다.** 1.3절은 "모델은 역할별로 미리 지정된 등급(`ROLE_TIERS`)으로 정한다"고 적었다. 나는 이 문장을 슬롯 없이도 모델이 정해지는 방식의 서술로 읽었다. 그래서 지금의 규칙을 유지했다: 설정 `role_tiers`가 `ROLE_TIERS`를 덮고, 과제 평가가 등급을 올린다. 평가로 올리는 것까지 막으려는 뜻이면 `model_policy.selection`을 추가로 바꿔야 한다.
4. **RUN-05의 이중 조건은 조사 제안과 반대로 줄였다.**
   - 조사 제안: 예약 원장을 정본으로 두고 `local_termination`은 표시용으로 남긴다.
   - 결정 4 뒤의 사정: 운영 역할 실행은 모델 예약이 없고, 호스트 한도가 없으면 예약이 하나도 없다. 그런 실행은 "보유 예약 없음"이 종료 전부터 참이 된다.
   - 그래서 종료 확인의 정본은 `capacity.local_termination`이다. `release`가 모든 예약을 정산한 뒤에만 이 값을 confirmed로 쓰므로, 두 조건이 함께 있던 곳은 이 하나로 줄였다(`engine.py` 목표 감사 복원, 초기 재시도).
5. **`release_or_hold`는 이미 있는 오류를 덮지 않는다.** 설치 복구는 전에 반환 실패 시 러너 오류를 그대로 두었다. 나머지 세 경로는 반환 실패 시 오류가 없던 상태다. 그래서 오류가 비어 있을 때만 보류 문구를 쓰게 해 네 경로의 결과를 보존했다.
6. **RUN-09의 계보.** 조사 제안은 되돌린 요청에 `continuation_of`를 붙이는 것이었다. 전의 재큐(`_retry_provider_actions`)는 `recovery.execution_id`만 붙였다. `continuation_of`는 실행 계보와 형식 검사의 선행 입력 대조에 쓰이므로, 전과 같은 `recovery`만 붙였다.
7. **RUN-09: 역할 입력이 `waiting_actions`를 읽는지.** 읽는다.
   - 운영 점검 입력은 `blocked_actions`에서 대상 실행의 대기 항목만 읽는다(`engine.py:2050`). 연구 준비·계획과 정비 입력은 전체 `blocked_actions`를 읽는다(`engine.py:2058`, `2088`). 연구 준비·계획 입력의 `ongoing_work`도 대기 항목을 읽는다(`context_store.py:492`).
   - 한도 대기 요청은 이제 이 목록에 없다. 대신 대기열에 있으므로 연구 계획 입력의 `queued_work`(`engine.py:1828`)에 작업 역할 요청으로 나타난다. 계획이 이 요청을 취소하거나 재배치할 수 있게 되었다.
   - 한도 실패에는 원래 운영 점검이 붙지 않았으므로 운영 점검 입력의 변화는 사실상 없다.
8. **ENG-15의 범위.** 조사 제목은 세 경로(정상 종료, 소실 복구, 소유자 오류 중단)를 들었다. 하지만 소유자 오류 중단(`_abort_parallel_calls`)은 작업 공간 파일을 모으지 않고 반환 결과만 보존한다. 제안도 두 경로의 공유를 말했다. 그래서 두 경로에만 적용했다. 복구 경로가 산출 manifest를 보존하는 것은 조사가 "선택 사항, 동작 변경"으로 적은 것을 택한 결과다.
9. **OPS-01의 위치와 우선순위.**
   - 위치: 조사는 `supervision_facts`를 `reporting`에 두자고 했다. 감독 복구 경로는 엔진 import가 깨진 상태에서도 돌아야 하는데, `reporting`은 `state_checks`·`academic`을 끌어온다. 그래서 두 함수를 `scheduled_operator`에 두고, `reporting`과 엔진은 필요한 자리에서 import한다.
   - 우선순위: 지점마다 달랐던 차단 순서를 하나로 정했다. `reporting`의 표시 순서(user_pause, fence, model_policy, paused, 설치 수리)를 보존하는 순서다.
   - 그 결과 공존 조합에서 바뀌는 반환은 넷이다.
     - guard: user_pause와 fence가 함께 있으면 paused를 낸다(전: maintenance_waiting).
     - guard: 종결 상태의 대화 소실·설치 수리는 not_started다.
     - check: 모델 정책 위반은 model_policy_waiting이다(전에는 paused가 먼저 잡혔다). fence는 check에서 바로 maintenance_waiting으로 끝난다(전에는 복구나 guard에서 held나 maintenance_waiting).
     - reconcile_wake: 비활성과 사용자 정지가 함께 있으면 held가 아니라 not_needed를 낸다(둘 다 예약을 취소한다).
   - guard는 명시적 엔진 시작이 운영 활성 여부와 무관하던 동작을 유지하려고 disabled를 보지 않는다.
10. **RUN-07 상태 검사.** 결정 4로 대체되어 구현하지 않았다. 참고로 조사 1단계 제안 가운데 상태 검사까지 모델 기준 합산으로 바꾸는 부분은 성립하지 않는다. 한도를 점유보다 낮추면 새 판본 제약에 옛 예약이 합산되어, 정상 상태를 결함으로 보고하게 된다. 상태 검사는 제약 ID별 합산으로 두었다.
11. **다른 그룹 파일의 변경.** 모두 결정 4나 내 항목의 호출부 최소 변경이다.
    - 그룹 B: `state_checks`, `record_schemas`(설정 절 외), 실행 스키마의 `process`·`budget_kind`, 대기 기록 필드. `record_schemas/domains.py:268`의 capacity `budget_kind` 한 항목은 그룹 B의 RUN-20(미사용 필드 7개 제거)과 겹친다.
    - 그룹 C: `review_cycle`, `review_engine`, `decision_engine`, `context_store`.
    - 그룹 D: `planning` 한 줄, `external`, `input_recovery`.
    - 그룹 E: `model_runner` 두 곳, `cli`.
    - 그룹 F: `governance`, `initialization`, `reporting`. 통합자가 지시한 세 곳과 `reporting`의 OPS-01·RUN-17 부분이다.
12. **커밋 절차.** 저장소 규칙은 커밋마다 `commit-harness`로 기억 노드를 결정화하라고 한다. 파견문은 worktree 안의 파일만 고치고 트레일러 없는 한 줄로 커밋하라고 명시했다. 병렬 그룹의 기억 결정화는 통합 단계 몫이라고 보고 파견문을 따랐다.

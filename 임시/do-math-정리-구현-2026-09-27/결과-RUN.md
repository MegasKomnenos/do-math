# 결과 — RUN(실행 수명·예산·예약) 그룹

기준은 worktree `C:/math-worktrees/c-run`의 브랜치 `c-run`이다. 이 브랜치는 `c-int`의 `78f00bb`에서 시작했다. 경로는 따로 적지 않으면 `.claude/skills/do-math/scripts/` 기준 상대 경로다. 행 번호는 마지막 커밋 `45fee5e`의 원문 좌표다.

## 1. 브랜치, 커밋, 바꾼 파일

- 브랜치: `c-run`(시작: `78f00bb`)
- 커밋: `5dc45b6` "RUN-01~17, HIS-14, HIS-20", `45fee5e` "RUN-18 재배치와 이음새 정본"(마지막)
- 제품(36, 새 모듈 5 포함):
  - 새 모듈: `do_math/planning_engine.py`, `do_math/initialization_engine.py`, `do_math/knowledge_engine.py`, `do_math/external_engine.py`, `do_math/formal_engine.py`
  - 수정: `academic_engine.py`, `budget.py`, `cli.py`, `context_store.py`, `engine.py`, `execution_lifecycle.py`, `execution_profiles.py`, `file_io.py`, `governance_engine.py`, `initialization.py`, `input_recovery.py`, `launch.py`, `lifecycle_engine.py`, `maintenance_gate.py`, `model_policy.py`, `model_runner.py`, `parallel.py`, `payloads.py`, `planning.py`, `preflight.py`, `provider_engine.py`, `record_schemas/__init__.py`, `record_schemas/schemas.py`, `retention.py`, `review_cycle.py`, `review_engine.py`, `scheduled_operator.py`, `scheduler.py`, `session_slots.py`, `state_checks.py`, `submission.py`(모두 `do_math/` 아래)
- 시험(11): `tests/test_budget.py`, `tests/test_control_shapes.py`, `tests/test_lifecycle_engine.py`, `tests/test_machine_parallel.py`, `tests/test_machine_scheduling.py`, `tests/test_redesign_ACTIVITIES.py`, `tests/test_redesign_ENGINE.py`, `tests/test_redesign_PROFILES.py`, `tests/test_session_scheduler.py`, `tests/test_state_checks.py`, `tests/test_walkthrough_repairs.py`
- 문서(1): `이음새-정본.md`(6절 표의 행 넷을 고치고 한 행을 더함, 3절). `operator_schedule.ps1`은 바꿀 필요가 없었다(RUN-12). 스킬 문서와 `AGENTS.md`는 고치지 않았다.

## 2. ID별 처분

담당 20건 모두 `구현함`이다. 측정 조건부 항목 둘(RUN-01, HIS-20)은 측정으로 실익을 확인한 뒤 구현했다. 측정 명령과 값은 이 절 끝에 있다.

| ID | 처분 | 내용과 좌표 |
|---|---|---|
| RUN-01 | 구현함 | 소유 루프는 준비 상태 갱신과 배정 스캔을 한 바퀴마다 하지 않고, `_scan_due`(`scheduler.py:55-62`)가 참일 때만 한다. 참이 되는 경우는 셋이다. 그 실행의 첫 바퀴, 마지막 판정 뒤 게시 head가 바뀐 경우, 마지막 판정에서 `OWNER_RESCAN_SECONDS`(1초, `scheduler.py:27`)가 지난 경우다. 관찰 적용의 게시는 head를 바꿔도 판정을 다시 부르지 않는다(`_publish_observation`, `scheduler.py:64-69`, 엔진 `_observe_running`이 씀). idle `--watch`의 0.2초 리터럴 둘은 `OWNER_POLL_SECONDS`로 합쳤다. 시각 조건의 다음 도래 시점은 계산하지 않고, 시간만으로 도래하는 전이는 최대 1초 늦는 상한으로 대신했다(7절). |
| RUN-02 | 구현함 | `_schedule_reconsideration`(`scheduler.py:161-195`)은 런타임을 복사하지 않고 제자리에서 `status`와 사건 배정 주석을 바꾼 뒤 `try/finally`로 되돌린다. 되돌림은 사건마다 원래의 `assigned_to`·`assigned_at` 값만 보관해 복원한다. |
| RUN-03 | 구현함 | `_action_lifecycle_gate`는 고른 프로필을 반환하고(`lifecycle_engine.py:205-265`), 같은 값을 다시 적던 `action.update(profile_ref=…, actor_kind=…)`를 지웠다. `_dispatchable`은 반환된 프로필을 `_admissible`에 넘기고, `_select_model`의 재대입과 `_execution_profile` 재호출 두 곳을 지웠다(`scheduler.py:234-285`). 기계 경로는 `_process_machine_action`의 관문 하나를 시작 직전 관문으로 남기고 `_run_external_action`·`_trust_check_steps` 첫머리의 관문을 지웠다. |
| RUN-04 | 구현함 | `profile_ref`는 세 키만 꺼낸다. `with_host_resources`, `job_resource_limits`, `runtime_config`, `machine_invocation`, `runner_tools`, `boundary_prompt`의 `validate_profile`을 지웠다. `select_profile`은 참조를 `match_profile_ref`로 확인하고 저장 프로필을 복사 없이 비교·반환한다(`execution_profiles.py:287-302`). 같은 이유로 저장 프로필을 재해시하던 `context_store.prepare_role_input`의 검사, `context_store`의 대안 프로필 검사, `planning.task_ready`의 검사도 지웠다. 검증은 `seal_profile`과 저장 관문에 남는다. |
| RUN-05 | 구현함 | `budget.plan_reservations(held, constraints, profile, *, owner_id)`가 프로필에서 요구를 직접 만들고 보유 예약만 센다(`budget.py:35-84`). 요청 조립(`session_slots`), 요청 검사(`_request_parts`의 확인부, `_snapshot_parts`, `_constraints`), 제어 예비량 재검사, `_validate_existing_records`를 지웠다. `_admission`은 보유 예약만 복사해 재기준화한다(`session_slots.py:79-162`). `settle_reservation`은 보유 기록 하나를 받는다. `budget.py`는 301행에서 146행이 되었다. |
| RUN-06 | 구현함 | `recover_execution(execution, *, at)`는 상태로 처분을 정하고 관찰 종류 어휘와 불일치 분기를 지웠다(`execution_lifecycle.py:196-218`). 장벽 확인 뒤 종료는 `end_recovered`(`:221-225`)로 두었다. `recovery_disposition`은 `ended` 전이에서 지운다(`:90-92`). 소비자 없는 `execution["recovery"]` 기록과 그 스키마 키, 대기열 단계 복구의 `retain_for_recheck` 설정, 정리 보호 사유가 된 `retention.py`의 `recovery_disposition` 조건을 지웠다(`retention.py:268-269`). |
| RUN-07 | 구현함 | `session_slots.local_termination_confirmed(execution)`(`session_slots.py:31-33`)을 두고 판정식 사본 8곳(`engine.py` 5, `execution_lifecycle.py` 1, `maintenance_gate.py` 1, `model_runner.py` 1)이 부르게 했다. |
| RUN-08 | 구현함 | `_reconsider_interval`과 `_plan_settle_waits`는 설정을 직접 색인한다. `_reconsider_interval`의 형 검사, `validate_policy`의 `session_limits` 모양·정수 검사, `build_profiles`의 형 검사 둘을 지웠다. `validate_policy`에는 모델 이름 공백 금지와 등급 모델 포함 조건만 남았다(`model_policy.py:92-94`). |
| RUN-09 | 구현함 | `lifecycle_clock = None`, `lifecycle_monotonic = time.monotonic`을 `_init_process_state`(`engine.py:446-447`)에서 초기화하고 `lifecycle_engine.py`의 두 `getattr`을 직접 접근으로 바꿨다. 같은 성질인 `parallel.py`의 `getattr(future, "execution_id", None)`과 `getattr(future, "judge_error", None)`도 `start_call`의 초기화와 직접 접근으로 바꿨다. ENG가 처리한 좌표는 다시 다루지 않았다. |
| RUN-10 | 구현함 | `_knowledge_control`(현재 `knowledge_engine.py`)의 대기열 거르기를 분기 뒤 한 번으로 옮기고 도달하지 않는 `else`를 지웠다. |
| RUN-11 | 구현함 | `scheduled_operator.py`의 `__package__` 채우기 분기와 `if __name__ == "__main__"`을 지웠다. 적재 경로는 `operator_bootstrap.py`의 모듈 적재 하나다. |
| RUN-12 | 구현함 | `SCHEDULE_ACTIONS`와 사전 거부를 지웠다. 동작 목록은 `operator_schedule.ps1`의 `ValidateSet` 하나이며, 목록 밖 동작은 어댑터가 0이 아닌 종료로 거부하고 `schedule`이 `RuntimeError`로 올린다. 이음새 정본 6절의 해당 행을 이 규칙으로 고쳤다. |
| RUN-13 | 구현함 | 바이트 증거 모양을 `file_io.bytes_evidence(raw)`(`file_io.py:207-212`)로 옮기고 `payloads.json_safe`와 `scheduled_operator._json`이 부른다. 엔진의 옛 사본은 이미 커널 단계에서 `payloads.json_safe`로 옮겨져 있었다(7절). |
| RUN-14 | 구현함 | 설치 복구 역할의 모델 등급 키를 `recovery` 하나로 통일했다: `model_policy.ROLE_TIERS`, `execution_profiles.PROFILE_ROLES`(치환 제거), `scheduled_operator`의 `selection(config, {"role": "recovery"}, …)`, `preflight`의 스키마 표 키. 설정 키 `role_tiers.independent_operator`는 이제 거부된다. 문서 두 곳은 4절에 적었다. |
| RUN-15 | 구현함 | `_limited_recovery_allowed`는 제한 복구 결박이 없으면 먼저 `False`를 돌려주고, `ValueError`만 거부로 받는다(`lifecycle_engine.py:349-357`). 재현 시험을 더했다(5절). |
| RUN-16 | 구현함 | `parallel.py`의 "As before" 경위 주석과 `provider_engine._provider_admit`의 옛 구현 언급을 현재 규칙으로 고쳤다. `_session_slots`·`_provider_status`의 가드를 지웠다. 저장 관문이 `role_profile_refs`(모든 역할 필수)와 그 참조 대상 프로필·제약을 강제하므로 적재된 인스턴스에는 두 키가 늘 있고, `provider_snapshot`은 런타임만 읽는다. |
| RUN-17 | 구현함 | `launch.termination_confirmed`의 `validate`를 지웠고, `SessionSlots.started`는 발사표의 종류와 Job 이름만 대조한다. |
| RUN-18 | 구현함 | 아래 표대로 옮겼다. 두 파일은 한 클래스의 믹스인이므로 동작은 바뀌지 않는다. `scheduler.py`는 630행에서 402행, `lifecycle_engine.py`는 1699행에서 782행이 되었다. |
| HIS-14 | 구현함 | `resolve_profile` 호출 30곳을 감사했다. 반환값을 고치거나 밖으로 내보내 뒤에서 고쳐질 수 있는 곳은 역할 입력 문맥에 프로필을 싣는 `engine.py:1731` 하나였고, 그곳만 `resolve_profile`(사본)을 쓴다. 나머지 29곳(17개 모듈)과 `select_profile` 내부는 읽기만 하므로 `match_profile_ref`로 옮겼다. `select_profile`이 돌려준 저장 프로필의 소비자(등록, 관문, 발사표, 러너, 추적 설정, 역할 입력, 예약)도 읽기만 함을 확인했다. 역할 입력은 `deepcopy(profile)`을 싣는다(`context_store.py:459`). |
| HIS-20 | 구현함 | 관찰 적용의 되돌림용 런타임 전체 사본을, 메모리 상태가 이 head의 게시 상태와 같을 때는 만들지 않는다(`engine.py:2673`). 실패하면 게시 상태를 적재해 되돌린다. 게시하지 않은 소유자 변경이 있을 때만 전과 같이 사본을 만든다. 통합표의 "관찰이 고치는 하위 키로 한정" 대신 이 방법을 쓴 이유는 7절에 있다. 재현 시험을 더했다. |

RUN-18의 재배치는 다음과 같다. 새 믹스인은 `ResearchEngine`의 기반 클래스에 더했다(`engine.py:409`).

| 새 모듈과 믹스인 | 옮긴 메서드 | 원래 파일 |
|---|---|---|
| `planning_engine.py` `PlanningEngineMixin` | `_apply_model_metadata`, `_assessment_input_version`, `_retry_observation_configuration`, `_resolve_task_observation_waits`, `_rule_deferral_inputs`, `_ensure_model_assessments`, `_finish_assessment_preparation`, `_apply_queue_plan` | `scheduler.py` |
| `initialization_engine.py` `InitializationEngineMixin` | `_initialization_control`, `_queue_initial_intent`, `_complete_initial_intent` | `lifecycle_engine.py` |
| `knowledge_engine.py` `KnowledgeEngineMixin` | `_invalidate_goal_currentness`, `_knowledge_control` | `lifecycle_engine.py` |
| `external_engine.py` `ExternalEngineMixin` | `_external_control`, `_external_prerequisite`, `_validate_external`, `_external_execution_record`, `_run_external_action` | `lifecycle_engine.py` |
| `formal_engine.py` `FormalEngineMixin` | `_trust_control`, `_formal_environment`, `_apply_trust_rebind`, `_resume_environment_waits`, `_run_trust_activation`, `_record_machine_continuation`, `_trust_activation_steps`, `_run_trust_check`, `_trust_check_steps`, `_formal`, `_formal_steps`, `_finish_trust_transition`, 모듈 함수 `_toolchain_matches` | `lifecycle_engine.py` |

`scheduler.py`에는 소유 루프, 배정 판정, `_select_model`, `_plan_settle_waits`, 재고려 예약, 판정 주기가 남는다. `lifecycle_engine.py`에는 시계 관문, 일시정지·재개·종료, 초기화 활성 전이(`_activate_initialization`), 배정 관문, 제한 복구, 확장 제어의 적용과 분배, 대화 임대, 준비 상태 갱신, 기계 실행의 공통 골격(`_release_machine_execution`, `_end_machine_execution`, `_lean_machine_call`, `_preserve_machine_return`, `_process_machine_action`)이 남는다. 통합표 정정대로 `_select_model`, `_plan_settle_waits`, `_end_machine_execution`, `_process_machine_action`은 옮기지 않았다. 옮긴 메서드 이름을 믹스인 클래스로 직접 부르던 시험 두 곳(`test_control_shapes.py:173`, `test_walkthrough_repairs.py:136`)은 새 클래스를 가리키게 고쳤다. 메서드 이름 충돌은 MRO 전수 검사에서 0건이었다.

영역 밖 관찰 세 건의 처분:

- **`mark_returned` 중복 호출**: 고치지 않았다. 두 호출은 서로 다른 경로를 맡는다. `_local_call_returned`(`scheduler.py:31-37`)는 `ModelCalls`로 돈 모든 호출의 반환을 결과와 함께 표시하며, 결과의 `launch_not_created` 영수증이 `not_started`를 정한다(`launch.py:52-63`). `_release_machine_execution`(`lifecycle_engine.py:707-713`)의 표시는 호출이 없던 기계 실행을 맡는다. 시작 전에 정지된 형식·신뢰 검사와 소유 스레드에서 동기로 도는 외부 작업이 여기에 든다. 중복은 두 경로가 겹치는 경우(호출이 돈 형식·신뢰 검사와 신뢰 활성)의 두 번째 표시이며, `mark_returned`는 이미 반환된 phase를 바꾸지 않는다. 앞쪽을 지우면 AI 호출의 시작 실패 영수증을 잃고, 뒤쪽을 지우면 ENG가 확인한 대로 시작 전 정지 검사가 종료 장벽에 보류된다(결과-ENG 5절).
- **`"source":"git_runtime"`**: 스킬 폴더, `AGENTS.md`, `docs/`를 전수 검색했다. 제품 소비자는 0건이고, 이 값을 단언하던 시험 한 줄(`test_redesign_ACTIVITIES.py`)과 역사 자료(`docs/do-math/initialization-repairs-20260925.json`, `test-cost-inventory-2026-09-24.csv`)만 있었다. 필드와 시험의 단언을 지웠다. 함께 사라진 `"uninitialized_feature_5_runtime"` 표지도 소비자가 없었다.
- **`budget.py` 비공개 이름**: `state_checks.py`와 `record_schemas/__init__.py`가 공개 이름 `outstanding_sum`, `validate_reservation`을 import한다.

측정(모델 호출 없음, 저장소·픽스처 변경 없음). 스크립트는 `C:/Users/wogud/AppData/Local/Temp/c-run-measure/`의 `measure.py`, `prof_run.py`, `his20.py`다. 각 스크립트는 `restore_template(test_session_scheduler.ready_work, count=6, public=False, config={})`로 준비 과제 6개와 대기 작업 요청 6개가 있는 상태를 임시 폴더에 복원한다. 값은 30회(큰 런타임은 10회) 중앙값이며, 다른 그룹의 시험이 동시에 도는 기계에서 쟀다.

| 측정 | 변경 전 | 변경 후 |
|---|---|---|
| `_refresh_readiness` 한 번 | 99.9ms | 60.0ms(RUN-03·04·05 뒤) |
| 대기 요청 6개의 `_dispatchable` 스캔 한 번 | 191.5ms | 132.8ms(RUN-03·04·05 뒤) |
| 판정을 건너뛴 바퀴의 `_scan_due` 확인 | 없음(매 바퀴 위 두 항목, 약 190ms) | 0.21ms |
| 무변경 `_save` | 0.26ms | 0.49ms |
| `deepcopy(runtime)`, 런타임 172KB | 5.3~6.4ms | 관찰 되돌림에서 만들지 않음 |
| `deepcopy(runtime)`, 실행 200개·history 2,000행을 더한 10.9MB | 346~618ms | 관찰 되돌림에서 만들지 않음 |
| 게시 상태와의 동등 비교(`_unchanged`와 같은 비교), 10.9MB | — | 13.4ms |

RUN-01의 실익 판정: 변경 전 한 바퀴의 준비 상태 갱신과 배정 스캔은 약 290ms였다. idle `--watch`는 이것을 0.2초마다, 호출이 돌 때는 관찰 한 건(제품 러너는 호출마다 약 1초 주기)마다 반복했으므로 소유 루프 시간의 대부분을 차지할 수 있었다. HIS-20의 실익 판정: 관찰 게시마다 드는 되돌림 사본은 10.9MB 런타임에서 한 건에 0.35~0.6초로, 제품의 관찰 주기(1초)에 견줄 크기다. 비교로 바꾸면 13ms다. 게시(`save_with_state`) 안의 복사 두 번은 사용자 결정(안 C 보류)에 따라 건드리지 않았다.

## 3. 새 공유 정의와 지운 공개 이름

`이음새-정본.md` 6절에 올린 새 공유 정의와 고친 행은 다음과 같다.

| 정본 | 위치 | 쓰는 곳 |
|---|---|---|
| `local_termination_confirmed(execution)`(`held_reservations`·`quiescence` 행에 더함) | `session_slots.py` | `engine.py`, `execution_lifecycle.py`, `maintenance_gate.py`, `model_runner.py` |
| `plan_reservations(held, constraints, profile, *, owner_id)`, `settle_reservation(record, …)`, `validate_reservation(record)`, `outstanding_sum(records, constraint_id, unit)`(새 행) | `budget.py` | `session_slots.py`, `state_checks.py`, `record_schemas/__init__.py` |
| `bytes_evidence(raw)`(새 행) | `file_io.py` | `payloads.json_safe`, `scheduled_operator._json`(모양 소비자 `model_runner`) |
| `profile_ref`, `select_profile`(`match_profile_ref` 행에 더함, 복사 규칙 명시) | `execution_profiles.py` | 프로필 선택·조회 전부 |
| `recover_execution`, `end_recovered`(`drive_to_termination` 행에 더함) | `execution_lifecycle.py` | `engine._recover_disappeared`, `provider_engine._settle_recovered_execution` |
| `SCHEDULE_ACTIONS` 삭제, 동작 목록은 `operator_schedule.ps1`의 `ValidateSet` | `scheduled_operator.py` 행 | — |

모듈 안에서만 쓰는 새 이름은 표에 올리지 않았다: `scheduler.OWNER_RESCAN_SECONDS`, `SchedulerMixin._scan_due`·`_publish_observation`, 새 믹스인 다섯(`engine.py`만 import).

지운 이름: `budget._snapshot_parts`, `_constraints`, `_request_parts`, `_new_record`, `_check_concurrency`, `_check_host`, `_validate_existing_records`, `_outstanding_sum`, `_outstanding`, `_string_set`, `_validate_reservation`(공개 이름으로 바꿈), `scheduled_operator.SCHEDULE_ACTIONS`, 설정 키 `role_tiers.independent_operator`와 `model_policy.ROLE_TIERS["independent_operator"]`, 복구 관찰 어휘(`start_unknown`, `previous_engine_lost`, `engine_restarted`, `termination_barrier_pending`, `termination_barrier_confirmed`, `no_execution_or_reservation` 전달), 실행 필드 `recovery`, `recovery_disposition` 값 `retain_for_recheck`·`continue_non_execution_followup`, 공급자 상태 필드 `source`. `recover_execution`은 `observation` 인자를 잃었다. 옛 이름 grep(`SCHEDULE_ACTIONS`, `_outstanding_sum`, `_validate_reservation`, `_validate_existing_records`, `independent_operator`, `uninitialized_feature_5`, `git_runtime`, `termination_barrier_confirmed`, `retain_for_recheck`)은 스킬 폴더와 `AGENTS.md`의 `.py`·`.md`·`.ps1`·`.json`에서 아래 4절의 문서 두 곳과 이름만 겹치는 시험 이름 두 개(`test_preflight`의 독립 운영 문서 시험, `test_redesign_ACTIVITIES`의 기존 시험 이름) 외에 0건이다.

## 4. 필요한 문서 변경

| 문서와 절 | 바꿀 내용 |
|---|---|
| `README.md:458` | `role_tiers.independent_operator`를 `role_tiers.recovery`로 바꾼다. |
| `references/CLI-실행-계약.md:230` | 같은 설정 키를 `role_tiers.recovery`로 바꾼다. |
| `references/CLI-실행-계약.md`의 status·`provider_waits` 설명(:993 부근) | 바꿀 필요 없음. 문서는 `source` 필드를 적지 않는다. |
| (선택) 소유 루프의 반응 시간을 적는 문서가 있다면 | 시간만으로 도래하는 전이(시각 조건, grant 만료, 계획 정착, 공급자 재시도)와 관찰이 연 live 운영 점검은 최대 1초(`OWNER_RESCAN_SECONDS`) 늦게 판정된다. `README.md`와 `references/`에서 소유 루프 주기를 적은 문장은 찾지 못했다. |

## 5. 실행한 시험

모두 `.claude/skills/do-math`에서 `python scripts/run_tests.py …`로 돌렸다. Lean이 필요한 실행에는 `DO_MATH_KNOWLEDGE_TEST_LEAN=C:/math/.skill-workspace/do-math-toolchains/lean-4.32.0/lean-4.32.0-windows/bin/lean.exe`를 주었다. 한 번에 한 프로세스만 띄웠다.

| 실행 | 대상 | 결과 |
|---|---|---|
| 편집 확인 1 | `test_budget test_machine_scheduling test_redesign_ACTIVITIES test_redesign_PROFILES test_launch_recovery test_host_resources` | 91 통과, 실패 2 → 수리 |
| 편집 확인 2 | `test_lifecycle_engine test_session_scheduler test_stop_flags test_machine_parallel test_redesign_ENGINE.ObservationTransactions test_state_checks test_preflight test_provider_wait test_provider_recovery test_redesign_LIFECYCLE test_controls test_research_recovery test_trust_continuation test_file_io test_operator` | 214 통과, 실패 12, 오류 7 → 수리 |
| 편집 확인 3 | 2의 실패·오류가 난 클래스(`test_machine_parallel.MachineSchedulerTests`, `test_lifecycle_engine.AuditRepairTests`, `…LifecycleTests`, `test_redesign_ENGINE.ObservationTransactions`, `test_session_scheduler.SessionPolicyTests`) | 70 통과 |
| 편집 확인 4 | `test_session_scheduler.OwnerRescanTests`(새 시험) | 1 통과 |
| 인계 확인(RUN-18 재배치 뒤) | `test_academic_engine test_budget test_cli test_context_store test_engine test_file_io test_governance_engine test_lifecycle_engine test_model_runner test_planning test_preflight test_review_cycle test_review_engine test_state_checks test_launch_recovery test_provider_wait test_provider_recovery test_session_scheduler test_machine_parallel test_machine_scheduling test_operator test_redesign_ACTIVITIES test_redesign_ENGINE test_redesign_PROFILES test_control_shapes test_walkthrough_repairs test_stop_flags test_controls test_research_recovery test_trust_continuation test_redesign_LIFECYCLE test_external test_formal_runtime test_input_recovery` | 585 통과, 건너뜀 1, 실패 1 |

실패·오류의 원인과 처리:

- 편집 확인 1의 실패 2건. `test_redesign_PROFILES.ProfileTests.test_admission_probe_preserves_history_and_provider_gate_across_capacity_editions`의 마지막 블록은 저장된 예약을 `reserved=-1`로 망가뜨린 뒤 배정 확인이 거부하기를 기대했다. RUN-05로 배정은 저장 관문을 통과한 예약만 읽으므로, 그 성질을 저장 관문 시험(`test_state_checks.…test_reservation_requires_balanced_settlement_and_existing_owner`)의 부분 사례 `{'reserved': -1}`로 옮기고 이 블록을 지웠다. `test_supervisor_has_engine_independent_launcher`는 RUN-11로 지운 경로 직접 실행만 검사해 지웠다. 엔진과 무관한 감독 기동은 `test_operator_bootstrap`이 엔진을 깨뜨린 복사본에서 검사한다.
- 편집 확인 2의 실패·오류 19건은 네 원인이다. (1) 시험 대역 `FakeEngine._execution_profile`이 고른 프로필의 참조를 행동에 기록하지 않았다. 제품 `_execution_profile`은 기록하며, RUN-03 전에는 관문의 중복 `update`가 이 차이를 가렸다. 대역이 제품 계약대로 기록하게 고쳤다(`profile_ref` KeyError 4건, 외부 작업 시험 6건). (2) `test_machine_parallel`의 `Host` 대역은 게시해도 head가 그대로여서, RUN-01의 판정 규칙에서 두 번째 배정이 일어나지 않았다(7건). 대역의 `_save`가 head를 옮기게 고쳤다. (3) `test_redesign_ENGINE.NoRepository`에 `published_state`가 없어 HIS-20의 동등 비교가 실패했다(2건). "게시한 것이 없다"는 뜻으로 `None`을 돌려주게 더했다. (4) `test_session_scheduler.…test_bad_capacity_and_missing_tier_model_are_rejected`는 `validate_policy`를 직접 불러 스키마가 맡는 범위 검사를 기대했다(1건). 범위 사례를 설정 경계 `validate_config`의 스키마 오류로 단언하고, `validate_policy`에는 남은 모델 이름 공백 금지 사례를 단언하게 고쳤다.
- 인계 확인의 실패 1건 `test_walkthrough_repairs.WalkthroughRepairs.test_readiness_document_tables_match_the_condition_grammar`는 변경 전부터 실패하던 시험이다. `후속-배정.md`의 KS 행이 "과제-착수조건의 /value·/lifecycle 포인터 삭제 전까지 실패"로 DOC 그룹에 배정했다. 건너뜀 1건은 심볼릭 링크 권한(WinError 1314)이다.

새 시험 3건과 수정 전 코드에서의 실패:

- `test_lifecycle_engine.…test_limited_recovery_refuses_unbound_requests_and_surfaces_check_defects`: 옛 코드는 결박 없는 요청에도 `_check_limited_recovery`를 부르고 `KeyError`를 `False`로 삼키므로 두 단언이 모두 실패한다(코드로 확인).
- `test_redesign_ENGINE.ObservationTransactions.test_failed_observation_rolls_back_to_the_published_state_without_copying_it_first`: 옛 코드는 `deepcopy(self.runtime)`을 부르므로 복사 단언이 실패한다(코드로 확인).
- `test_session_scheduler.OwnerRescanTests.test_owner_rejudges_after_a_state_change_or_its_time_bound_but_not_after_an_observation`: 옛 코드에는 `_scan_due`가 없다.

기계적 확인: `do_math/*.py`와 `record_schemas/*.py` 전부 `py_compile` 통과, `scripts/tests`의 `test_*.py` 135개 모두 `importlib.import_module` 성공, 3절의 옛 이름 grep, 새 믹스인의 메서드 이름 충돌 0건, 바꾼 모듈의 사용하지 않는 import 0건(AST 검사).

돌리지 않은 관련 시험과 이유(시험 지침 2절에 따라 통합 확인에 맡김):

- 프로필 조회·선택의 소비자 모듈(`test_redesign_SURFACE`, `test_submission_*`, `test_initialization_*`, `test_academic*`, `test_review_*` 외 다수): 반환값은 같고 사본 대신 저장 객체를 받는다. 소비자가 고치지 않음을 코드로 감사했다(HIS-14).
- status 출력의 소비자(`test_reporting` 외): `provider_waits`에서 `source` 필드만 사라졌다. 이 필드를 단언하는 시험은 고친 한 줄 외에 0건이다.
- `retention` 정리 시험(`test_redesign_STORAGE` 외): 지운 조건은 종료된 실행에서만 참이 될 수 있었고, 이제 종료 전이가 그 값을 지운다.
- 소유 루프를 전 구간 모는 시험 모듈 다수(`test_purpose_engine`, `test_redesign_EVIDENCE*` 외): RUN-01의 판정 주기가 이들의 진행을 바꿀 수 있는지는 통합 확인에서 드러난다. 판정은 게시 head가 바뀌면 곧바로 다시 일어나므로, 제품 엔진 위의 시험에서는 이전과 같은 바퀴에서 배정이 일어날 것으로 본다. 게시해도 head를 바꾸지 않는 시험 대역을 쓰는 모듈이 더 있으면 같은 수리(대역이 head를 옮기게)가 필요하다.

## 6. 기능이나 시험 범위가 바뀐 것

| 대상 | 이유 | 잃는 것 | 얻는 것 |
|---|---|---|---|
| 소유 루프의 판정 주기 | RUN-01 | 시간만으로 도래하는 전이와 관찰이 연 live 운영 점검이 최대 1초 늦게 판정된다. idle 대기가 0.2초에서 0.25초가 된다 | 상태가 그대로인 바퀴는 판정 없이 0.2ms에 지난다. 새 프로세스 지역 상태 둘(`_scan_head`, `_scan_at`): 게시 head 이동(관찰 게시 제외)이나 1초 경과로 무효가 되고, 실행마다 첫 바퀴에서 초기화되며, 복구 규칙은 필요 없다 |
| 관찰 실패의 되돌림 | HIS-20 | 없음(게시하지 않은 변경이 있으면 전과 같이 사본) | 관찰 게시마다 런타임 전체 사본 1회 |
| 예산 계산 | RUN-05 | 배정 때 저장 예약 원장 전체의 재검증, `budget` 단위의 잘못된 요청·기존 예약 ID·미지원 제약 종류 거부 시험 2건(`test_existing_reservation_id_is_rejected`, `test_unsupported_constraint_kind_is_rejected`). 요청은 함수 안에서 프로필로 만들고, 실행 ID의 단일 사용은 `SessionSlots.acquire`가 지킨다 | 배정 계산이 보유 예약 수에 비례한다. 저장 관문 시험에 음수 예약 사례 하나가 더해졌다 |
| 프로필 접근 | RUN-04, HIS-14 | 저장·봉인되지 않은 프로필을 접근자에 넘기면 더는 거부되지 않는다(호출자 전수 확인에서 그런 곳은 없다). `select_profile`이 저장 객체를 돌려준다 | 선택·배정·시작·문맥 구성마다의 재해시와 사본 |
| 복구 처분 | RUN-06 | 종료된 실행이 `recovery_disposition`으로 정리에서 영구히 빠지던 보호, 실행의 `recovery` 관찰 이력(소비자 없음) | 종료된 실행의 정리 보호는 대기·복구·활동 의무라는 현행 사유만 따른다 |
| 설정 키 | RUN-14 | `role_tiers.independent_operator` | `role_tiers.recovery`(프로필 역할 이름과 같음) |
| 예약 어댑터 동작 검사 | RUN-12 | 목록 밖 동작의 Python 사전 거부(`ValueError`) | 동작 목록 하나. 목록 밖 동작은 PowerShell을 한 번 띄운 뒤 `RuntimeError` |
| 감독 모듈 직접 실행 | RUN-11 | `python scheduled_operator.py`와 그 시험 1건 | 적재 경로 하나(`operator_bootstrap.py`) |
| 제한 복구 판정 | RUN-15 | 없음 | 판정 안의 `KeyError`·`TypeError`·`IndexError` 결함이 "허용 안 됨"으로 숨지 않고 드러난다 |
| 기계 경로의 관문 | RUN-03 | `_run_external_action`·`_trust_check_steps`가 스스로 관문을 통과하던 자기완결성. 직접 부르는 호출자는 `_process_machine_action`처럼 관문을 먼저 통과시켜야 한다 | 같은 시작의 관문 2회 |
| status의 `provider_waits` | 영역 밖 관찰 | `source` 필드 | 없음 |
| 발사표 재검증 | RUN-17 | 반환·시작 때의 발사표 모양 재검사 | 반복 확인 1회 |
| 시험 대역 | RUN-01·03, HIS-20 | 없음 | `FakeEngine._execution_profile`이 제품처럼 참조를 기록하고, `Host._save`가 head를 옮기며, `NoRepository`가 `published_state`를 가진다 |

## 7. 막힌 지점, 접근을 바꾼 지점, 예상과 달랐던 결과

- **RUN-01의 판정 규칙.** 통합표 (a)안은 "시각 조건이 도래한 바퀴"에 판정하라고 했다. 과제 조건은 조건 문법으로 `now`를 임의로 쓸 수 있어 다음 도래 시점을 모두 계산할 수 없다. 그래서 도래 시점 계산 대신 1초 상한을 두었다. 상태 변화 신호는 게시 head로 잡았다. 관찰 적용은 대부분 게시하므로 head만 보면 (a)안의 "관찰만 도착해 깬 바퀴"도 판정이 다시 돈다. 그래서 관찰 게시만 판정을 무효로 하지 않게 했다. 관찰은 live 운영 점검을 대기열에 넣을 수 있으며, 그 배정은 최대 1초 늦는다.
- **RUN-01에서 드러난 시험 대역.** head를 옮기지 않는 `Host` 대역과 참조를 기록하지 않는 `FakeEngine` 대역이 제품 계약과 달랐다. 제품에 대역용 신호(직전 바퀴의 배정·수거 여부)를 더하는 대신 대역을 제품 계약에 맞췄다.
- **RUN-01 측정에서 예상과 달랐던 것.** 한 바퀴 비용은 예상보다 컸다(6개 과제에서 약 290ms). 프로필 재해시(RUN-04)와 중복 선택(RUN-03)을 지운 뒤에도 남는 큰 항목은 담당 ID 밖이다: `model_policy.assessment_tier`가 호출마다 `jsonschema.validate`로 메타스키마까지 검사하고(과제마다 바퀴당 두 번), 배정 스캔의 `capability_requirements`가 요청마다 `adapter_for`로 CLI 경로를 찾는다(8절).
- **HIS-20의 방법.** 통합표는 되돌림 사본을 관찰이 고치는 하위 키로 한정하라고 했다. 관찰 적용은 `_record_review_observation`과 `_enqueue`를 거쳐 검토 주기와 대기열 등 여러 키를 고칠 수 있어, 키를 열거하면 빠진 키가 되돌려지지 않는 위험(통합표 비용 칸)이 남는다. 관찰은 게시 직후의 상태에서 시작하는 것이 보통이므로(`_settle_stops`가 먼저 게시), 그 경우 게시 상태 자체를 되돌림으로 삼으면 키를 열거하지 않고 같은 결과를 낸다. 게시하지 않은 변경이 있으면 전과 같이 사본을 만든다. `save_with_state`가 돌려주는 상태는 캐시와 분리된 사본이라(`repository.py:463`) 동등 비교가 유효하다.
- **RUN-13의 좌표.** 엔진의 옛 사본(`engine.py:122-125`)은 커널 단계에서 `payloads.json_safe`로 이미 옮겨져 있었다. 두 사본은 `payloads.json_safe`와 `scheduled_operator._json`이었고, 통합표대로 `file_io`로 옮겼다.
- **RUN-06의 범위.** 대기열 단계 복구가 `recover_execution`으로 `retain_for_recheck`를 기록한 직후 `end_preparation`으로 끝내던 경로는, 종료 전이가 그 값을 지우므로 기록 자체가 무의미해져 호출을 지웠다. 그러자 `retention.py`의 `recovery_disposition` 조건은 종료된 실행에서 참이 될 수 없어 지웠다(STO 파일의 한 줄).
- **RUN-18의 배치.** 통합표는 "각 도메인 engine mixin"을 목적지로 들었으나 지식·신뢰·외부·계획 흐름을 받을 기존 믹스인이 없었다. 기존 믹스인(다른 그룹이 병렬로 고치는 파일)에 코드를 더하는 대신 새 모듈 다섯을 만들어 병합 충돌을 피했다. 형식 검사는 ENG-08이 신뢰 검사 옆에 둔 구조를 따라 신뢰 흐름과 함께 `formal_engine`으로 옮겼다. 대화 임대와 초기화 활성 전이는 수명 상태를 바꾸는 규칙이라 `lifecycle_engine`에 남겼다.
- **RUN-04의 범위.** 통합표 좌표 밖에서 저장 프로필을 재해시하던 곳 셋(`context_store.py` 2, `planning.py` 1)을 같은 결과(검증은 봉인과 저장 관문 두 곳)를 위해 함께 지웠다.
- **작문 절차.** 이 파일에는 `write-for-reader`의 `명료한_산문.md`, `AI_프롬프트.md`, `에이전트_채널.md`를 적용했다. `writing_flow.py`의 별도 독해는 실행하지 않았다.

## 8. 다른 그룹 범위에서 발견한 문제

- **담당 ID 없음(RUN 영역 파일, 측정된 최대 비용)**: `model_policy.assessment_tier`(`model_policy.py:24-29`)가 호출마다 `jsonschema.validate`를 불러 메타스키마 검사(`check_schema`)까지 한다. 준비 상태 갱신과 배정 스캔에서 과제마다 여러 번 불린다. 모듈 수준 검사기 하나로 바꾸면 줄어든다.
- **OPS**: `initialization.capability_requirements`(`initialization.py:30-38`)가 배정 판정마다 `adapter_for(profile).capability_identity()`를 부르고, `claude_adapter.provider_adapter`가 그때마다 `shutil.which`로 CLI를 찾는다. 역량 증거 행 재해시(RUN 검토 5절의 `initialization.py:43` 관찰)와 같은 경로다.
- **STO**: `retention.py:269`가 읽는 실행 필드 `recovery_pending`, `checkpoint_required`는 제품에 생산자가 없다. `save_with_state`는 게시 한 번에 상태를 두 번 복사한다(`repository.py:365-366`, `:463`). 사용자 결정(안 C 보류)과 인접한다.
- **RES**: `planning.py:834`의 `instance.get('config',{}).get('research_reconsider_seconds')`는 RUN-08과 같은 기본값 접근이다.
- **TSB**: `tests/test_redesign_ENGINE.py:377`, `:407`, `:1700`의 `_action_lifecycle_gate` 대역은 이제 관문을 부르지 않는 `_call_steps`·`_formal`을 부르는 시험에 남아 효과가 없다. `FakeEngine`(`tests/test_lifecycle_engine.py:19`)은 게시해도 head를 옮기지 않으므로, 이 대역으로 소유 루프를 여러 번 배정까지 모는 시험은 RUN-01 뒤 `Host`처럼 head를 옮겨야 한다.
- **ENG·RUN 경계(작음)**: 신뢰 검사·신뢰 활성·외부 작업의 `_register_execution`은 여전히 등록 안에서 프로필을 다시 고른다. RUN-04 뒤 이 선택은 참조 비교뿐이라 비용이 작아 관문의 프로필을 기계 단계 생성기로 넘기지 않았다.

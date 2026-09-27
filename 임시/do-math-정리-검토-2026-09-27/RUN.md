# RUN 영역 정리 검토: 실행 수명·예산·예약

좌표는 따로 적지 않으면 `C:/math/.claude/skills/do-math/` 기준 상대 경로이고, 행 번호는 main `9b434f4` 작업 트리의 것이다.

## 1. 읽은 범위

전문을 읽은 파일(행 수는 `wc -l`):

- 영역 파일 15개(`scripts/do_math/`): `lifecycle_engine.py` 1477, `session_slots.py` 344, `budget.py` 302, `launch.py` 88, `execution_lifecycle.py` 233, `execution_window.py` 49, `provider_engine.py` 109, `provider_wait.py` 41, `model_policy.py` 157, `execution_profiles.py` 418, `windows_job.py` 627, `scheduler.py` 630, `parallel.py` 218, `maintenance_gate.py` 48, `scheduled_operator.py` 701
- 공통 계약과 필수 문서: `C:/math/임시/do-math-정리-검토-2026-09-27/기준.md` 238, `AGENTS.md` 11, `C:/math/docs/do-math/검사-경량화-이음새-계약.md` 245
- 과거 경량화 자료: `C:/math/임시/경량화-조사-2026-09-26/RUN.md` 424, `결과-A.md` 195, `결과-병합A.md` 93, `C:/math/임시/시험-경량화-2026-09-26/작업자-노드/W-debt-M-0351.md` 37
- 커밋 diff: `8d2ffd0`의 영역 파일 변경 전체(6개 파일), `9b434f4`의 `parallel.py` 변경 전체

일부만 읽은 것(이음새를 따라간 범위):

- `379a171`: 영역 파일 15개의 `--stat`, `launch.py`·`execution_window.py`·`windows_job.py` hunk 전체, 나머지 12개 파일은 추가된 주석·docstring 행만. 나머지 변경 내용은 `결과-A.md`·`결과-병합A.md`와 현재 원문으로 대조했다.
- `fe59ca0`(경량화 이전): `provider_engine.py` 20-70, `execution_lifecycle.py`·`retention.py`의 `recovery_disposition` 행
- `scripts/do_math/engine.py`: 97-125, 205-257, 352-362, 520-545, 577-592, 626-666, 1636-1700, 1870-1895, 3355-3470, 4239-4251, 4375-4440
- `scripts/do_math/record_schemas/__init__.py` 100-125, 140-185; `record_schemas/schemas.py` 23-50, 400-412
- `scripts/do_math/planning.py` 774-819; `retention.py` 236-252; `state_checks.py` 250-267; `initialization.py` 31-56; `governance_engine.py` 42-75; `model_runner.py` 288-300; `claude_adapter.py` 50-55
- `scripts/operator_bootstrap.py`(grep 행: 106, 118, 144, 169-172), `scripts/operator_schedule.ps1` 2행, `scripts/tests/test_background_processes.py` 85-110
- `C:/math/기억/색인.md` layer-3 절, 기억 노드 M-0348~M-0350은 RUN 관련 행 grep 결과만

파견문이 정했는데 읽지 못한 파일은 없다. 모든 종류를 검토했다.

## 2. 영역 판정

RUN 영역은 2라운드가 실행 수명의 이음새(반환 또는 보류, 시작 기록, 발사표 전이, 보유 예약·정지 판정, 공급자 게이트, 대기 종류)를 공유 함수로 모은 덕분에 방향성 1·2와 대체로 맞는다. 남은 불일치는 대부분 한 가지 성질로 묶인다. 같은 호출 안에서 방금 만든 값이나 저장 관문을 이미 통과한 값을 다시 검사하거나 다시 계산하는 곳이 배정 경로에 겹겹이 남아 있다. 저장된 프로필을 접근할 때마다 재해시하고(RUN-04), `budget.py`가 같은 호출에서 만든 요청과 전체 예약 원장을 배정마다 검증하며(RUN-05), 한 요청의 배정 판정이 프로필을 두 번 고르고 수명 관문을 두세 번 통과한다(RUN-03). 가장 큰 개선 여지는 소유 루프다. 관찰 한 건이 루프를 깨울 때마다 준비 상태 전체 갱신, 런타임 전체 깊은 복사, 대기열 전 요청의 배정 판정을 다시 하며, M-0351이 남긴 "관찰 하나의 소유 루프 비용이 도착 간격보다 크다"는 공백이 여기서 열려 있다(RUN-01, RUN-02). 이 둘을 정리하면 배정 경로는 "저장 관문에서 한 번 검증, 상태 판본이 바뀌거나 시각 조건이 도래할 때만 재평가"라는 하나의 규칙으로 설명할 수 있다.

검토했고 없음: 문서, 결함, 비대, 낡음

## 3. 후보

#### RUN-01 소유 루프가 관찰 한 건마다 준비 상태 전체와 대기열 전체의 배정을 다시 계산한다
- 검토: 2
- 종류: 공백
- 좌표: `scripts/do_math/scheduler.py:521-614`(특히 569, 584-585, 578, 614), `scripts/do_math/parallel.py:53-60`, `scripts/do_math/lifecycle_engine.py:882-1066`
- 현상: `_run_parallel`의 한 바퀴는 `_settle_stops`(내부 `_save`), `_controls`, `collect`, `_check_installation`, `_refresh_readiness`, `_resume_environment_waits`, 대기열 앞에서부터 `_dispatchable` 평가를 차례로 한다. 호출이 도는 동안 바퀴는 `ModelCalls.wait(OWNER_POLL_SECONDS)`에서 깨어나는데, `_observed`는 관찰 행을 붙일 때마다 `wake.set()`을 한다(`parallel.py:58-59`). 그래서 관찰 한 건이 바퀴 한 번을 통째로 돌린다. `_refresh_readiness`는 매 바퀴 과제마다 `work_profile_selection`, `capture_task_basis`, `contract_review_current`, `task_ready`를 계산하고 `apply_event_schedule`, `_schedule_reconsideration`(RUN-02의 런타임 깊은 복사)을 부른다. 이어 `_dispatchable`이 같은 바퀴에서 작업 요청의 `task_ready`를 한 번 더 계산한다(`scheduler.py:474-477`). 호출이 없는 `--watch` 대기에서는 `time.sleep(.2)` 뒤 같은 전체 바퀴와 `_save()`를 초당 5회 반복한다(`scheduler.py:573-579`, `606-614`). 정기 감독의 엔진 실행은 `--watch`로 뜬다(`scheduled_operator.py:263-264`).
- 근거: M-0351 「작업 너머 시사점」은 "관찰 하나당 소유 루프 비용이 부하 아래 관찰 도착 간격보다 크다. 호출 여럿이 출력을 흘리면 소진을 한정해도 적용 대기 관찰이 쌓인다"고 적고 미해결로 남겼다. `9b434f4`는 소진 한정(`parallel.py:130-134`)만 넣었다. `8d2ffd0` 이전에는 루프가 0.02초 폴링이었고(`8d2ffd0` diff의 `time.sleep(.02)` 삭제), 사건 기반 대기로 바뀌면서 관찰이 곧 바퀴 기동이 됐다. 멈춤 판정은 이미 "head 이동 또는 시각 조건 도래 때만" 규칙을 쓴다(`scheduler.py:28-42`, `51-67`). 준비 상태와 배정 판정에는 같은 규칙이 없다. 이 판정은 코드 경로로 확인했고, 바퀴 비용은 측정하지 않았다.
- 제안: 먼저 `operation_trace.phase`로 한 바퀴의 구간별 시간(`_refresh_readiness`, 배정 스캔, `_save`)을 실제 호출 부하에서 잰다. 그 결과에 따라 둘 중 하나를 고른다. (a) 관찰 행만 도착해 깬 바퀴는 `pump`와 멈춤 판정만 하고, 준비 상태 갱신과 배정 스캔은 head가 바뀌었거나 시각 조건(과제 조건의 `now`, `plan_settle_seconds`, 공급자 `retry_at`, grant 만료)이 도래한 바퀴에서만 한다. (b) 준비 상태 갱신만 head 변화나 일정 간격에 묶는다. 대기용 0.2초 리터럴은 `OWNER_POLL_SECONDS` 하나로 합친다.
- 실익: 관찰이 많은 호출 여럿이 동시에 돌 때 적용 대기 관찰의 누적과 소유 루프 지연(배정·live 점검·제어 응답)이 줄어든다. idle `--watch`의 초당 5회 전체 재계산이 없어진다.
- 비용과 위험: 새 프로세스 지역 상태(마지막 스캔 head, 다음 시각 조건 시점)와 그 무효화 규칙이 생긴다. 과제 조건처럼 시각에 의존하는 준비 판정의 다음 도래 시점을 모두 계산하지 못하면 시각 기반 전이가 늦어진다. 방향성 8에 따라 이 상태를 비용으로 센다. 측정 없이 채택하지 않는다.
- 기능·커버리지 영향: 있음(시각 조건 도래 전까지 준비 상태 표시가 갱신되지 않을 수 있다)
- 사용자 결정 관련: 없음
- 확신도: 추정(실제 호출 부하에서 바퀴 구간별 시간을 측정하면 확정된다)

#### RUN-02 `_schedule_reconsideration`이 매 바퀴 런타임 전체를 깊은 복사한다
- 검토: 1
- 종류: 비용
- 좌표: `scripts/do_math/scheduler.py:135-169`, 호출 `scripts/do_math/lifecycle_engine.py:1028`
- 현상: `_schedule_reconsideration`은 `candidate = deepcopy(self.runtime)`로 런타임 전체(실행과 전이 이력, 사건, history, 과제, 예약 원장)를 복사한다. 복사의 용도는 두 가지 임시 변경뿐이다. `status`를 `'active'`로 바꾸는 것과 사건에 `assigned_to`를 붙이는 것이다. 호출 뒤 둘 다 되돌리고(161-167), 결과 `candidate`를 조건 없이 채택한다(168). 되돌림에 필요한 원래 사건은 146행이 따로 복사해 둔다. 따라서 전체 복사는 채택될 객체를 새로 만드는 일만 한다.
- 근거: `planning.schedule_reconsideration`(`planning.py:774-819`)은 `events`, `pending_events`, `queue`와 대기열 요청만 바꾼다. 호출 경로는 `_refresh_readiness`(1028행)이고, RUN-01에 따라 매 바퀴 실행된다. 예외가 나도 안전하다. 소유 루프 예외는 `_abort_parallel_calls`가 `_reload()`로 메모리 상태를 버리고(`scheduler.py:105`), 제어 적용 예외는 `before_instance`·`before_runtime`으로 되돌린다(`lifecycle_engine.py:537`, `584`).
- 제안: 제자리에서 `status`를 바꾸고 사건 주석을 붙인 뒤 `try/finally`로 되돌린다. 전체 `deepcopy`와 `self.runtime = candidate`를 지운다.
- 실익: 매 바퀴 런타임 크기에 비례하는 깊은 복사 1회가 없어진다. 런타임은 실행 이력과 예약 원장이 계속 쌓이므로 연구가 길어질수록 절감이 커진다. 코드는 1-2행 준다.
- 비용과 위험: 파일 하나만 바뀐다. 새 상태, 수명, 복구 규칙은 없다. `try/finally`가 없으면 예외 때 `status='active'`가 메모리에 남는다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인(복사의 용도와 채택 경로는 원문으로 확인했다. 절감 시간의 크기는 측정하지 않았다.)

#### RUN-03 한 요청의 배정 판정이 프로필을 두 번 고르고, 기계 요청은 수명 관문을 같은 호출 사슬에서 세 번 통과한다
- 검토: 1
- 종류: 비용
- 좌표: `scripts/do_math/scheduler.py:462`, `502`, `506-507`, `512`; `scripts/do_math/lifecycle_engine.py:348-350`, `1160`, `1251`, `1314`; `scripts/do_math/engine.py:588-591`
- 현상: `_dispatchable`은 먼저 `_action_lifecycle_gate`를 부른다(462). 관문은 `self._execution_profile(action)`으로 프로필을 고르고(348), `action.update(profile_ref=profile_ref(profile), actor_kind=...)`를 한다(350). 그런데 `_execution_profile`이 이미 같은 두 필드와 `model_selection`을 기록했다(`engine.py:588-591`). `_dispatchable`은 이어 `_select_model`로 방금 기록된 `model_selection`의 사본을 받아 같은 값을 다시 쓰고(506-507), `_admissible(action, self._execution_profile(action))`로 프로필을 다시 고른다(502, 512). 기계 요청은 `_dispatchable`의 관문(462) 뒤 `_process_machine_action`의 관문(1160)을 지나고, 그 직후 `_run_external_action`의 첫 행(1251)이나 `_trust_check_steps`의 첫 행(1314)에서 관문을 또 통과한다. 1160과 1251·1314 사이에는 분기 호출 말고 문장이 없다.
- 근거: 관문 한 번은 시계 확인, `select_profile`(허용 참조마다 `resolve_profile`과 `profile_ref` 재해시), `authorize`를 한다. 프로필 재해시 한 번은 이 기계에서 0.126ms(`research_plan` high, 1418바이트)~0.286ms(`research_work` high, 2115바이트)였다(아래 명령). 검색 `_action_lifecycle_gate\(`의 제품 일치는 12건이고, 그중 이 후보와 관련된 것은 4건(`scheduler.py:462`, `lifecycle_engine.py:1160`, `1251`, `1314`)이다. 나머지는 `engine.py`와 `_trust_activation_steps`의 결과 뒤 재확인(1220)이다.
  - 측정: `python -c` 한 줄로 `build_profiles(DEFAULT_CONFIG, roles={'research_work','research_plan'})`의 프로필에 `validate_profile`을 200회 반복했다. 저장소는 바꾸지 않았다.
- 제안: `_action_lifecycle_gate`가 고른 프로필을 반환하게 하고, `_dispatchable`은 그 프로필을 `_admissible`에 넘긴다. 350행의 중복 `update`와 506-507행을 지운다. 기계 경로는 `_process_machine_action`의 관문(1160)을 시작 직전 관문으로 남기고 1251·1314를 지운다. `_trust_activation_steps`는 시작 때 관문이 없으므로 1160이 필요하다.
- 실익: AI 요청의 배정 판정 한 번에서 `select_profile` 1회(허용 참조 수 + 2회 재해시)가 준다. 기계 요청의 시작 한 번에서 관문 2회가 준다. 판정은 RUN-01에 따라 매 바퀴 대기 요청마다 반복되므로 절감도 곱해진다. 코드 약 5행이 준다.
- 비용과 위험: 두 파일이 바뀐다. 남는 관문(1160)이 여전히 시작 직전의 마지막 확인이므로 방향성 12항의 재확인은 약해지지 않는다. `_run_external_action`·`_run_trust_check`를 관문 없이 직접 부르는 시험(`scripts/tests/test_lifecycle_engine.py:529`, `677`, `1122`)이 안쪽 관문에 기대는지 확인해야 한다.
- 기능·커버리지 영향: 없음(시험 호출 방식은 바뀔 수 있다)
- 사용자 결정 관련: 없음
- 확신도: 확인(중복 호출은 원문으로 확인했다. 위 세 시험의 영향은 추정이며, 해당 시험을 읽으면 확정된다.)

#### RUN-04 저장된 프로필을 접근할 때마다 재해시한다
- 검토: 1
- 종류: 불일관
- 좌표: `scripts/do_math/execution_profiles.py:56-58`(`profile_ref`), `151`, `164`, `294`, `298`, `303`, `310`, `320`, `334`, `353`, `389`, `399`; `scripts/do_math/session_slots.py:70`, `84`, `91`, `123`, `156`, `169`
- 현상: `profile_ref`, `job_resource_limits`, `runtime_config`, `runner_tools`, `boundary_prompt`, `machine_invocation`, `with_host_resources`는 매번 `validate_profile`을 불러 본문을 `exact_content_hash`로 다시 해시한다. `select_profile`은 허용 참조마다 `profile_ref(resolve_profile(...))`를 만들고(294), 후보마다 `profile_ref(p)`를 다시 계산한다(303). 한 번의 배정 계산(`_admission`)에서도 `profile_ref` 3회와 `job_resource_limits` 1회가 재해시한다.
- 근거: 저장된 프로필은 적재 때 저장 관문의 가족 검증기로 `validate_profile`을 이미 통과한다(`record_schemas/__init__.py:105`, `109`). 새 판본은 `seal_profile`이 생성 직후 검증한다(`execution_profiles.py:52`). 2라운드가 정한 `match_profile_ref`의 규칙은 "Stored profiles passed validate_profile when saved or sealed, so the profile is neither hashed again nor copied"다(`execution_profiles.py:273-284`, 이음새 계약 11절). 위 접근자들은 이 규칙과 어긋난다. 방향성 6의 "같은 사실의 반복 확인"에 해당한다. 비용은 RUN-03의 측정값(재해시 1회 0.126~0.286ms)이다. `profile_ref(` 호출은 제품 16개 모듈에 40행이 있다(검색 `profile_ref\(`).
- 제안: `profile_ref`는 세 키만 꺼내고 검증하지 않는다. 나머지 접근자의 `validate_profile` 호출을 지운다. `select_profile`은 참조를 `match_profile_ref`로 확인하고 참조끼리 비교한다. 검증은 `seal_profile`과 저장 관문 두 곳에 남긴다.
- 실익: 배정 판정·시작·문맥 구성마다 수 회의 재해시가 없어진다. 저장 프로필에 대한 규칙이 `match_profile_ref`와 하나로 맞는다. `execution_profiles.py`에서 약 8행이 준다.
- 비용과 위험: `profile_ref` 호출 40행 가운데 봉인·저장을 거치지 않은 dict를 넘기는 곳이 있으면 검증이 빠진다. `context_store.py:676`과 `planning.py:648`은 후보 프로필을 직접 검증하므로 영향이 없다. 나머지 호출자를 전수로 확인해야 한다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 추정(`profile_ref` 호출 40행이 모두 봉인되었거나 저장된 프로필을 넘기는지 확인하면 확정된다)

#### RUN-05 `budget.py`가 같은 호출에서 만든 요청과 저장 관문을 통과한 원장 전체를 배정마다 다시 검사한다
- 검토: 1
- 종류: 이음새
- 좌표: `scripts/do_math/session_slots.py:100-160`; `scripts/do_math/budget.py:47-59`, `91`, `111-133`, `136-199`, `241-249`, `256-258`
- 현상: `_admission`은 프로필의 `capacity_refs`와 고정된 `host_resources.demands`로 요구(demand)와 요청을 만든다(`session_slots.py:146-157`). `plan_reservations`는 같은 프로필을 받아, 요구가 프로필 참조와 정확히 일치하는지, 호스트 요구가 고정 값과 같은지, 단위가 `accounting_unit`과 같은지를 다시 확인한다(`budget.py:142-192`). "프로필 하나가 요구하는 예약"이라는 같은 지식이 생산과 확인 두 곳에 있다. 또 `plan_reservations`는 매번 원장의 모든 예약을 `_validate_existing_records`로 검증하고(50행), `_admission`은 모든 예약을 복사해 재기준화한다(101행, 135-145행). 제어 예비량 검사(`budget.py:243-249`)는 `_admission`이 직전에 부른 `validate_host_constraint`(132행)가 같은 조건을 확인한다(`execution_profiles.py:126-131`).
- 근거: `plan_reservations`와 `settle_reservation`의 제품 호출자는 `session_slots.py` 하나다(검색 `plan_reservations\|settle_reservation`: 제품 일치 4건, 관련 4건, 시험은 `scripts/tests/test_budget.py` 1파일). 저장된 예약은 적재 때 `budget._validate_reservation`이 가족 검증기로 검증한다(`record_schemas/__init__.py:106`, `109`; 스키마 `record_schemas/schemas.py:403-408`). 예약은 지워지지 않는다(검색 `reservations.*pop(\|del .*reservations`: 0건). 정산은 늘 `returned=reserved`이므로(`session_slots.py:262-263`) 정산된 행의 미결 양은 0이다. 따라서 배정 계산 한 번의 비용이 지금까지 만든 예약 전체에 비례한다. 예약 계산은 대기 요청마다 매 바퀴 반복된다(`scheduler.py:514-519`).
- 제안: `plan_reservations(reservations, constraints, profile, *, owner_id)`가 프로필에서 요구를 직접 만든다(정의 하나). `session_slots.py`의 요구·요청 조립, `budget.py`의 요청 검사(`_request_parts`의 확인부, `_snapshot_parts`, `_constraints`), 제어 예비량 재검사, `_validate_existing_records` 호출을 지운다. 합산은 `held_reservations`의 행만 대상으로 한다. `_validate_reservation`은 저장 관문의 가족 검증기로 남긴다. 재기준화(135-145)는 보유 행만 복사해 적용한다.
- 실익: `budget.py` 302행 가운데 약 80~100행이 준다(추정). 배정 계산 비용이 전체 예약 수에서 보유 예약 수로 준다. 요구 규칙의 사본 하나가 없어진다.
- 비용과 위험: `budget.py`의 API가 바뀐다. `test_budget.py`의 입력 검증 시험은 지우거나 저장 관문 시험으로 옮긴다. `state_checks.py:257`과 `record_schemas/__init__.py:106`이 private 이름(`_outstanding_sum`, `_validate_reservation`)을 import하므로 공개 이름으로 바꾸는 편이 낫다. 새 상태, 수명, 복구 규칙은 없다.
- 기능·커버리지 영향: 있음(`budget.py` 단위의 잘못된 요청 거부 시험이 사라진다. 요청이 같은 함수 안에서 만들어지므로 제품 동작은 같다.)
- 사용자 결정 관련: 없음
- 확신도: 확인(중복과 호출자는 전수 검색으로 확인했다. 줄어드는 행 수는 추정이다.)

#### RUN-06 복구 관찰 종류는 유일한 생산자가 상태에서 파생하고, `recovery_disposition`은 실행이 끝나도 지워지지 않는다
- 검토: 1
- 종류: 파생상태
- 좌표: `scripts/do_math/execution_lifecycle.py:198-233`; `scripts/do_math/engine.py:1645-1662`; `scripts/do_math/provider_engine.py:36-40`; `scripts/do_math/retention.py:245`; `scripts/do_math/record_schemas/schemas.py:267`
- 현상: 엔진 복구는 실행 상태에서 관찰 종류를 만든다(`starting`→`start_unknown`, `running`→`previous_engine_lost`, 체크포인트 중→`engine_restarted`, 그 밖→`termination_barrier_pending`, `engine.py:1658-1662`). `recover_execution`은 그 종류와 상태의 짝을 다시 확인해 전이와 `recovery_disposition`을 정한다. 짝이 맞지 않을 때의 `ValueError`(231-232행)는 제품에서 도달하지 않는다. 관찰은 `execution["recovery"]`에 쌓이지만(211행) 제품에서 읽는 곳이 없다. `recovery_disposition`은 네 곳에서 쓰고(`execution_lifecycle.py:213-230`, `engine.py:1648`), 이후 실행이 `ended`로 전이해도 지워지지 않는다. `retention.py:245`는 이 값이 `preserve_space_and_reservations`, `reconcile_local_and_remote`, `retain_for_recheck`이면 실행을 `recovery_pending`으로 보고 정리에서 뺀다.
- 근거: 관찰 문자열 검색(`start_unknown|previous_engine_lost|termination_barrier_confirmed|queued_reservation_requires_reconciliation`)의 제품 일치는 `engine.py` 3건과 `provider_engine.py` 1건뿐이고 모두 같은 프로세스에서 상태로부터 만든다. 실행의 `recovery` 필드를 읽는 제품 코드는 없다(검색 `get\(['"]recovery['"]`: 4건, 모두 요청·대기의 `recovery`이며 관련 0건). `recovery_disposition`을 지우는 코드는 없다(검색 결과 쓰기 7건, 읽기 1건). 예를 들어 대기열 단계에서 사라진 실행은 `retain_for_recheck`를 받은 직후 `cancelled`로 끝나고(`engine.py:1650-1653`), 이 값은 그대로 남아 정리 보호 사유가 된다. 이 동작은 `fe59ca0`에도 있었으므로 세 경량화가 들여온 것은 아니다.
- 제안: `recover_execution(execution, *, at)`가 상태에서 직접 처분을 정하게 하고, 관찰 종류 어휘와 불일치 분기를 지운다. 장벽 확인 뒤 종료는 별도 함수로 둔다. `recovery_disposition`의 수명은 방향성 10에 따라 `ended` 전이에서 정한다(지우거나 종결 처분으로 바꾼다). `execution["recovery"]` 기록을 지울지는 소비자 부재를 근거로 판단한다.
- 실익: 약 15행 감소, 생산자 하나뿐인 어휘 하나 제거. 끝난 실행의 작업 공간이 이유 없이 정리에서 영구히 빠지는 여지가 없어진다.
- 비용과 위험: `execution_lifecycle.py`, `engine.py`, `provider_engine.py`, `scripts/tests/test_redesign_ACTIVITIES.py:123`, `127`이 바뀐다. `reconcile_local_and_remote`가 원격 종료 미확인 때문에 종료 뒤에도 보존을 의도한 값이라면 그 값만 남겨야 한다.
- 기능·커버리지 영향: 있음(끝난 실행이 정리 대상이 될 수 있다)
- 사용자 결정 관련: 없음
- 확신도: 추정(관찰 종류의 중복은 확인했다. `recovery_disposition`이 종료 뒤에도 남는 것이 의도인지는 설계 원문으로 확인해야 한다.)

#### RUN-07 "로컬 종료 확인" 판정식이 여덟 곳에 사본으로 있다
- 검토: 1
- 종류: 이음새
- 좌표: `scripts/do_math/engine.py:1626`, `1633`, `2535`, `4000`, `4152`; `scripts/do_math/execution_lifecycle.py:120`; `scripts/do_math/maintenance_gate.py:42`; `scripts/do_math/model_runner.py:321`; 생산 `scripts/do_math/session_slots.py:248`, `265`
- 현상: `execution.get('capacity', {}).get('local_termination') == 'confirmed'`(또는 `!=`)가 네 모듈 여덟 곳에 그대로 적혀 있다.
- 근거: 검색 `local_termination.*confirmed`의 제품 일치는 21건이고, 그중 판정식 사본은 위 8건이다. 나머지는 생산, 스키마, 다른 필드다. 2라운드는 `local_termination`을 종료 확인의 정본으로 정했다(결과-A 5절 4). 같은 이음새의 `held_reservations`·`quiescence`는 이미 `session_slots.py`에 정본이 있다.
- 제안: `session_slots.local_termination_confirmed(execution)`을 두고 여덟 곳이 부르게 한다. 이음새 계약 11절 표의 `held_reservations`·`quiescence` 행에 더한다.
- 실익: 판정 정본 하나. `capacity`가 없는 실행을 어떻게 볼지 같은 규칙이 바뀌면 한 곳만 고친다.
- 비용과 위험: 네 파일의 한 행씩 바뀐다. 새 상태는 없다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### RUN-08 설정 기본값과 형·범위 검사의 사본이 설정 절 정본 밖에 남아 있다
- 검토: 1
- 종류: 이음새
- 좌표: `scripts/do_math/lifecycle_engine.py:26-30`; `scripts/do_math/scheduler.py:448`; `scripts/do_math/model_policy.py:91-97`; `scripts/do_math/execution_profiles.py:182-184`, `198-200`
- 현상: `_reconsider_interval`은 `config.get('research_reconsider_seconds', 86400)`로 기본값을 다시 적고 양의 정수인지 검사한다. `_plan_settle_waits`는 `get("plan_settle_seconds", 300)`로 기본값을 다시 적는다. `validate_policy`는 `session_limits`가 `{"work"}` 하나인지, 값이 음이 아닌 정수인지 검사한다. `build_profiles`는 `session_limits`가 dict인지, 값이 음이 아닌 정수인지 다시 검사한다.
- 근거: 기본값의 정본은 `DEFAULT_CONFIG`(`engine.py:104`, `106`)이고, 형·범위의 정본은 `config_schema()`다(`record_schemas/__init__.py:150-151`의 `POSITIVE_SETTINGS`, 170행의 닫힌 `session_limits`). 이음새 계약 11절은 "저장 스키마, configure 제어 모양, engine.validate_config가 모두 이것에서 파생한다"고 정한다. 저장 설정은 늘 `DEFAULT_CONFIG`에 덧씌워 만든다(`engine.py:241-242`, `governance_engine.py:47`). `validate_policy`와 `build_profiles`의 모든 제품 호출자는 먼저 `validate_config`를 거친다(`engine.py:216-220`, `229`, `243`, `257`, `358-359`; `governance_engine.py:48`, `58`, `61`). 2라운드는 같은 성격의 재시도·마무리 예고 기본값을 없앴다(결과-A RUN-11).
- 제안: 두 기본값 사본을 직접 색인(`config["..."]`)으로 바꾸고 `_reconsider_interval`의 형 검사를 지운다. `validate_policy`에서는 스키마가 이미 강제하는 두 조건을 지우고, 모델 이름의 공백 금지와 등급 모델 포함 조건만 남긴다. `build_profiles`의 형 검사 두 곳을 지운다.
- 실익: 수치 사본 2개와 형 검사 사본 3곳 제거(약 10행). 설정 기본값을 바꿀 때 옛 값이 코드에 남지 않는다.
- 비용과 위험: 세 파일이 바뀐다. `planning.py:824`의 같은 키 `.get`은 RES 영역이다(5절).
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### RUN-09 방어 getattr·hasattr와 시험 전용 시계 훅이 남아 있다
- 검토: 1
- 종류: 불일관
- 좌표: `scripts/do_math/lifecycle_engine.py:39`, `57`, `89`, `172`, `341`, `725`, `730`, `732`, `811`, `813`; `scripts/do_math/scheduler.py:46`; 초기화 블록 `scripts/do_math/engine.py:520-534`
- 현상: 늘 정의된 메서드를 기본값 있는 getattr·hasattr로 읽는다. `_governance_owner_handlers`(172, 341; 정의 `governance_engine.py:111`), `_solution_basis`(730, 811; 정의 `academic_engine.py:96`), `_academic_evidence`(732, 813; 정의 `academic_engine.py:93`)가 그렇다. 초기화되지 않는 프로세스 지역 속성도 getattr로 읽는다. `_clock_failure`(89), `_external_preparation_binding`(725), `_goal_basis_memo`(`scheduler.py:46`)가 그렇다. `lifecycle_clock`(39)과 `lifecycle_monotonic`(57)은 제품이 설정하는 곳이 없고 시험만 설정한다.
- 근거: `ResearchEngine`은 이 mixin들을 모두 상속한다(`engine.py:499`). 시험의 `FakeEngine`도 `ResearchEngine`의 하위 클래스다(`scripts/tests/test_lifecycle_engine.py:19`). 검색 결과 `lifecycle_clock`은 제품 설정 0건·시험 7파일, `lifecycle_monotonic`은 제품 설정 0건·시험 5파일이다. 2라운드는 같은 이유의 방어 getattr 5곳과 hasattr 2곳을 직접 접근으로 바꿨다(결과-A 1절 "추가 배정"). `engine.py:520-534`에는 프로세스 지역 상태를 모으는 블록이 이미 있다.
- 제안: 초기화 블록에 `_clock_failure = None`, `_goal_basis_memo = None`, `_external_preparation_binding = None`, `lifecycle_clock = None`, `lifecycle_monotonic = time.monotonic`을 두고 직접 접근한다. 늘 정의된 세 메서드의 fallback을 지운다.
- 실익: getattr·hasattr 11곳 제거. 엔진의 프로세스 지역 상태 목록이 한 곳에 모인다.
- 비용과 위험: 두 파일과 초기화 블록이 바뀐다. 시험은 지금처럼 속성을 대입하면 된다. `engine.py`의 같은 성격 행은 5절에 적었다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### RUN-10 `_knowledge_control`의 대기열 거르기 중복과 도달하지 않는 else
- 검토: 1
- 종류: 미사용
- 좌표: `scripts/do_math/lifecycle_engine.py:614-649`
- 현상: 616-617행이 `operation`을 `revise`·`invalidate`로 제한한 뒤, 634-647행의 if/elif는 같은 대기열 거르기 두 행을 각 분기에 반복하고(638-639, 644-645), else(646-647)는 도달하지 않는다.
- 근거: 원문. 호출자는 `_apply_extended_control`(563행)과 `scripts/tests/test_control_shapes.py:183`이다.
- 제안: 거르기를 분기 뒤로 한 번 옮기고 else를 지운다.
- 실익: 약 5행 감소.
- 비용과 위험: 없음.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### RUN-11 `scheduled_operator.py`의 직접 실행 분기는 쓰이지 않는다
- 검토: 1
- 종류: 미사용
- 좌표: `scripts/do_math/scheduled_operator.py:20-22`, `700-701`
- 현상: 파일을 경로로 직접 실행할 때 `__package__`를 채우는 분기와 `if __name__ == "__main__"`이 있다.
- 근거: 정기 감독은 `operator_bootstrap.py`가 `from do_math import scheduled_operator`로 적재해 `main(args)`을 부른다(`scripts/operator_bootstrap.py:169-172`). 검색 `scheduled_operator.py`의 일치는 파일 존재 확인(`operator_bootstrap.py:106`)과 AST 검사 시험(`scripts/tests/test_background_processes.py:98`) 2건이고, 경로 실행은 0건이다. 검색 `-m do_math\|do_math\.scheduled_operator\b`(시험 제외)도 0건이다. 분기는 `7d2597e`(판본 5)에서 들어왔고, 이후 frozen bootstrap이 적재 경로를 대신했다.
- 제안: 두 블록과 주석을 지운다.
- 실익: 5행 감소. 모듈 적재 경로가 하나로 설명된다.
- 비용과 위험: 없음.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### RUN-12 예약 어댑터 동작 목록이 Python과 PowerShell에 따로 있다
- 검토: 1
- 종류: 이음새
- 좌표: `scripts/do_math/scheduled_operator.py:36-38`, `130-131`; `scripts/operator_schedule.ps1:2`
- 현상: `SCHEDULE_ACTIONS` 튜플과 어댑터의 `ValidateSet`이 같은 일곱 이름을 따로 적는다. 36행 주석은 ValidateSet이 목록이라고 밝힌다.
- 근거: 둘을 비교하는 시험은 없다(검색 `SCHEDULE_ACTIONS\|ValidateSet`: 정의 파일 밖 0건). CLI는 이 상수를 쓰지 않고 자기 모드 목록을 둔다(`cli.py:210`, `447-448`). 따라서 상수는 `schedule()`의 사전 거부 한 곳에서만 쓰인다.
- 제안: 튜플과 사전 거부를 지우고 어댑터의 ValidateSet 거부(0이 아닌 종료 → `RuntimeError`)에 맡긴다. 또는 ValidateSet을 파싱해 비교하는 시험 하나를 둔다. 앞쪽이 정의 하나에 맞는다.
- 실익: 동작 목록 사본 하나 제거(약 3행).
- 비용과 위험: 잘못된 동작 이름이 PowerShell을 한 번 띄운 뒤 실패한다. 호출자는 모두 코드 안의 상수를 넘긴다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### RUN-13 bytes를 증거 JSON으로 바꾸는 규칙이 두 곳에 있다
- 검토: 1
- 종류: 이음새
- 좌표: `scripts/do_math/scheduled_operator.py:87-91`; `scripts/do_math/engine.py:122-125`
- 현상: 두 곳이 bytes를 `{"sha256", "text"(utf-8 replace), "base64"}`로 같은 모양으로 바꾼다.
- 근거: 검색 `b64encode`의 제품 일치 7건 가운데 이 모양은 두 곳이다. `scheduled_operator`는 엔진 import가 깨져도 돌아야 하므로 `engine`을 import하지 못한다(모듈 docstring, 결과-A 5절 9).
- 제안: 규칙을 worker·감독 경로가 함께 쓰는 `file_io.py`로 옮기고 두 곳이 부른다.
- 실익: 규칙 사본 하나 제거(약 5행).
- 비용과 위험: 세 파일이 바뀐다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### RUN-14 설치 복구 AI 역할이 두 이름을 가진다
- 검토: 1
- 종류: 불일관
- 좌표: `scripts/do_math/model_policy.py:16`; `scripts/do_math/execution_profiles.py:29`, `231`, `237-238`; `scripts/do_math/scheduled_operator.py:507-509`; `scripts/do_math/preflight.py:123`; `README.md:458`; `references/CLI-실행-계약.md:230`
- 현상: 프로필·실행의 역할 이름은 `recovery`인데, 모델 등급 키는 `independent_operator`다. 그래서 `PROFILE_ROLES`는 `set(ROLE_TIERS) - {"independent_operator"} | ... | {"recovery"}`로 이름을 바꿔 끼우고, 복구는 `selection(config, {"role": "independent_operator"})`로 모델을 고른 뒤 `select_profile(..., {"role": "recovery"}, ...)`로 프로필을 고른다.
- 근거: 검색 `independent_operator`의 일치는 제품 4행과 문서 2행이다.
- 제안: 한 이름(`recovery`)으로 통일한다. 설정 키 `role_tiers.independent_operator`와 두 문서, 응답 스키마 키(`preflight.py:123`)를 같은 변경에서 바꾼다.
- 실익: 이름 치환 하나와 역할 집합의 예외 처리 제거. 설정·문서·코드가 같은 이름을 쓴다.
- 비용과 위험: 사용자에게 보이는 설정 키가 바뀐다. 현행 계약 하나 원칙에 따라 별칭을 두지 않는다.
- 기능·커버리지 영향: 있음(설정 키 이름)
- 사용자 결정 관련: 없음
- 확신도: 확인

#### RUN-15 `_limited_recovery_allowed`가 KeyError·TypeError·IndexError를 거부로 삼킨다
- 검토: 1
- 종류: 기타(원인을 확인하지 않고 예외를 삼키는 코드이며, 세 경량화 이전부터 있어 검토 2의 임시방편에 넣지 않았다)
- 좌표: `scripts/do_math/lifecycle_engine.py:445-490`; 호출 `scripts/do_math/scheduler.py:544-545`, `scripts/do_math/lifecycle_engine.py:352`, `498-499`
- 현상: `_check_limited_recovery`의 모든 `KeyError`, `TypeError`, `IndexError`를 `False`로 바꾼다. 이 함수는 정지 중 매 바퀴 대기열 요청마다, 그리고 멈춤 판정마다 불린다.
- 근거: 제한 복구 승인이 없는 일반 요청은 453-456행의 `ValueError`로 거부되므로 세 예외가 필요하지 않다. 세 예외는 `authorize`·`resolve_profile`·`_capability_requirements` 안의 프로그래밍 결함도 "허용 안 됨"으로 바꾼다.
- 제안: 바인딩이 없으면 먼저 `False`를 돌려주고, `ValueError`만 거부로 받는다.
- 실익: 제한 복구 판정의 결함이 조용히 "허용 안 됨"으로 바뀌지 않는다.
- 비용과 위험: 지금 세 예외로만 거부되는 정상 경로가 있으면 오류가 난다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 추정(세 예외가 정상 경로에서 나는 곳이 없음을 `authorize`와 확장 제어 기록의 결측 경우까지 확인하면 확정된다)

#### RUN-16 작업 경위를 설명하는 주석과 도달 여부가 불명한 가드
- 검토: 2
- 종류: 잔재
- 좌표: `scripts/do_math/parallel.py:112`; `scripts/do_math/provider_engine.py:54-58`, `19-20`, `49-50`
- 현상: `parallel.py:112`의 "As before, a failing judgment fails its own call"은 `8d2ffd0`가 멈춤 판정을 소유 스레드로 옮길 때 붙인 경위 주석이다(`8d2ffd0` diff). `provider_engine.py:57-58`의 "deliberately has no legacy model-only or SQLite admission path"는 없어진 옛 구현을 가리킨다. `_session_slots`와 `_provider_status`는 인스턴스에 `execution_profiles`·`capacity_constraints`가 없을 때를 다룬다.
- 근거: 초기화는 늘 판본을 만들어 두 키를 채운다(`engine.py:257`, `execution_profiles.py:252-261`).
- 제안: 두 주석을 현재 규칙만 말하게 고친다(예: "A failing judgment fails its own call, not the owner."). 두 가드는 도달 경로를 확인한 뒤 지운다.
- 실익: 경위 주석 2개 제거, 가드가 도달하지 않으면 약 4행 감소.
- 비용과 위험: 없음.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 추정(주석은 확인했다. 가드는 초기화 전 `status()` 경로와 시험의 가짜 엔진이 두 키 없이 들어오는지 확인하면 확정된다.)

#### RUN-17 저장 관문을 통과한 발사표를 다시 검증한다
- 검토: 1
- 종류: 비용
- 좌표: `scripts/do_math/launch.py:75`; `scripts/do_math/session_slots.py:228`
- 현상: `termination_confirmed`와 `SessionSlots.started`가 저장되었거나 방금 만든 발사표의 모양 전체를 `validate`로 다시 검사한다.
- 근거: 저장 관문이 적재 때 `validate_launch`로 발사표를 검사한다(`record_schemas/__init__.py:243`). 발사표는 `acquire` 안에서 `ticket()`이 만든다(`session_slots.py:204`). `started`의 Job 이름·종류 대조(229-230행)는 다른 지식이므로 남는다.
- 제안: 두 호출에서 `validate`를 지우고, `started`는 종류와 Job 이름만 대조한다.
- 실익: 반환·시작마다 반복 확인 1회 제거, 2행 감소. 효과는 작다.
- 비용과 위험: 없음.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### RUN-18 `scheduler.py`와 `lifecycle_engine.py`가 실행 수명과 무관한 흐름을 함께 가진다
- 검토: 1
- 종류: 경계
- 좌표: `scripts/do_math/scheduler.py:181-457`; `scripts/do_math/lifecycle_engine.py:194-343`, `614-866`, `1068-1477`
- 현상: `scheduler.py`는 소유 루프와 배정 판정 외에 모델 평가·관찰 규칙 준비 흐름(`_apply_model_metadata`, `_ensure_model_assessments`, `_finish_assessment_preparation`, `_rule_deferral_inputs`, `_retry_observation_configuration`, `_resolve_task_observation_waits`)과 계획의 대기열 재배치(`_apply_queue_plan`)를 가진다. `lifecycle_engine.py`는 시계 관문·일시정지·배정 관문 외에 초기화 채택, 지식·신뢰·외부·대화 제어, 신뢰 검사·활성화·외부 행동 실행을 가진다.
- 근거: 두 파일은 한 클래스의 mixin이므로 옮겨도 동작과 행 수는 바뀌지 않는다. 바뀌는 것은 응집도다. 지금은 모델 평가 규칙이 바뀔 때도, 신뢰 전환 규칙이 바뀔 때도 RUN 영역 파일이 바뀐다.
- 제안: 준비·평가 흐름은 `planning`·`task_scope` 쪽 mixin으로, 신뢰·외부·지식 제어는 각 도메인의 engine mixin으로 옮긴다. 우선순위는 낮다.
- 실익: 실행 수명 파일이 실행 수명의 이유로만 바뀐다. 행 수 절감은 없다.
- 비용과 위험: 파일 이동이 크고, 병렬 작업과 충돌하기 쉽다. 새 상태는 없다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인(책임 혼재는 원문으로 확인했다. 실익은 구조적이다.)

## 4. 보존 판정

- `scripts/do_math/session_slots.py:85-91`: 프로필이 인스턴스의 현재 채택 호스트 제약을 가리키는지 보는 검사다. 형식 재검사가 아니라 현재성 검사이므로 유지한다.
- `scripts/do_math/session_slots.py:174-219`: 사전 확인과 실제 배정의 이중 계산이다. 쓰기 잠금 아래 최신 원장으로 다시 계산해야 하므로 유지한다(2라운드 RUN 보존 판정 1과 같다).
- `scripts/do_math/scheduler.py:44-49`(`_goal_basis_key_at_head`): head를 키로 한 메모다. 멈춤 판정은 `_save` 뒤(`_evaluate_stops`)나 `_save` 직후(`_settle_stops`)에만 돌므로 메모리 상태가 게시 상태와 같고, 방향성 9의 조건을 만족한다. 초기화하지 않은 getattr만 RUN-09로 정리한다.
- `scripts/do_math/scheduled_operator.py:495-500`, `528-529`: 기본 구분자로 만든 실패 digest 두 곳이다. 저장되고 다시 대조되므로 규칙을 바꾸지 않는다(이음새 계약 2.1절).
- `scripts/do_math/lifecycle_engine.py:1099-1113`, `scripts/do_math/engine.py:4391-4414`, `scripts/do_math/engine.py:3445-3483`, `scripts/do_math/scheduled_operator.py:636-649`: 반환 뒤 종료 전이의 네 사본처럼 보인다. 그러나 경로마다 "반환 확인 전에는 결과를 기록하지 않는다"는 순서 사이에 서로 다른 수신 기록(형식 결과 기록, 제출 수집, 복구 보고 영수증)이 끼어 있고, 공유할 수 있는 것은 전이 두 행뿐이다. 감독 경로는 엔진 import 없이 돌아야 한다. 합치지 않는다.
- `scripts/do_math/provider_engine.py:84-90`: 예약 wake 조정의 `except Exception`이다. 실패를 `provider_wake`에 기록하고 wake는 보조 수단이므로 조용히 삼키는 코드가 아니다.
- `scripts/do_math/parallel.py:130-145`: `9b434f4`의 소진 한정이다. 반환된 호출은 행을 더 붙이지 않으므로 `collect`가 모두 적용한다. 유지한다.
- `scripts/do_math/model_policy.py:95-99`의 모델 이름 공백 금지와 등급 모델 포함 조건: 스키마가 표현하지 않는 교차 조건이므로 RUN-08 뒤에도 남긴다.
- `scripts/do_math/budget.py:261-277`(`_validate_reservation`): 저장 관문의 가족 검증기이므로 RUN-05 뒤에도 남긴다.
- 운영 역할 동시 실행의 상한 부재(결과-A 0절의 세 경로): 결정 4에서 사용자가 상한을 두지 않기로 했다. 그 뒤 새로 드러난 사실은 찾지 못했다.
- `scripts/do_math/windows_job.py:29-37`과 `execution_profiles.py:109-116`, `launch.py:74-88`의 이중 증거, `session_slots.py:213-215`·`266-269`의 게이트 `checking` 소유권: 2라운드 RUN 보존 판정 5·6·7의 근거가 현재 원문에서도 성립한다.

## 5. 영역 밖 관찰

- ENG `scripts/do_math/engine.py:629`: `_register_execution`이 `_dispatchable` 직후 같은 요청의 프로필을 다시 고른다(RUN-03과 같은 성질).
- ENG `scripts/do_math/engine.py:3057`, `4301`: AI·형식 검사 시작 때 같은 바퀴의 `_dispatchable` 관문을 다시 통과한다. 시작 직전 확인으로 둘 곳 하나를 정하면 된다.
- ENG `scripts/do_math/engine.py:3665`, `4053`, `4244`: `_external_preparation_binding`, `_goal_audit_contract`의 방어 getattr(RUN-09와 같은 성질).
- ENG/OPS `scripts/do_math/engine.py:358-359`, `scripts/do_math/governance_engine.py:48`, `58`, `61`: 설정 변경 한 번에 `validate_config`와 `build_profiles`가 여러 번 불린다(`host_resources`가 있으면 `validate_config` 안에서도 한 번 더 부른다).
- RES `scripts/do_math/planning.py:824`: `research_reconsider_seconds`의 `.get` 사본(RUN-08과 같은 성질).
- STO `scripts/do_math/retention.py:245`: 종료된 실행의 `recovery_disposition`을 보호 사유로 읽는다(RUN-06의 소비자).
- STO `scripts/do_math/state_checks.py:257`, `scripts/do_math/record_schemas/__init__.py:106`: `budget.py`의 private 이름을 import한다.
- OPS `scripts/do_math/initialization.py:43`: `capability_requirements`가 배정 판정마다 저장된 역량 증거 행을 재해시한다(RUN-04와 같은 성질, 매 바퀴 반복).

## 6. 작업 기록

- `379a171`의 영역 파일 diff는 세 파일만 hunk 전체를 읽고 나머지는 추가 주석 행과 결과 문서로 대조했다. 현재 원문을 전문으로 읽었으므로 후보 판정에는 영향이 없다고 판단했다.
- 예상과 달랐던 결과가 둘 있다. 첫째, `recovery_disposition`이 종료 뒤에도 남아 정리 보호 사유가 되는 동작은 세 경량화 이전(`fe59ca0`)부터 있었다(RUN-06). 둘째, `8d2ffd0`가 폴링을 사건 기반 대기로 바꾸면서 관찰 한 건이 곧 소유 루프 한 바퀴가 됐다. M-0351의 미해결 비용은 여기서 나온다(RUN-01).
- 측정은 프로필 재해시 한 가지만 했다. 소유 루프 한 바퀴의 비용과 런타임 깊은 복사 비용은 실제 인스턴스가 필요해 측정하지 못했다(RUN-01, RUN-02는 원문 판정이다).
- write-for-reader 스킬의 별도 독해(`writing_flow.py read`)는 실행하지 않았다. 산출 형식은 기준 8절이 정했고, 이 산출은 통합자가 원문으로 다시 확인한다.

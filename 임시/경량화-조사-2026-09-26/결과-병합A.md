# 결과-병합A: r2-int에 그룹 A 병합

이 문서는 통합 단계에서 브랜치 `r2-a`(그룹 A, 커밋 `6b0bac2`)를 `r2-int`(그룹 B·F·D·E·C 병합 상태, 커밋 `74d3221`)에 합친 기록이다. 1절은 충돌 파일마다 두 쪽의 의도와 합친 방법을 적는다. 2절은 병합 뒤 양방향 이름 정리의 결과, 3절은 확인 결과, 4절은 이 병합이 남긴 판단과 위험이다.

- worktree `C:/math-worktrees/r2-int`, 브랜치 `r2-int`, 병합 커밋 `5169fa0`(부모 `74d3221`, `6b0bac2`)
- 좌표는 따로 적지 않으면 `C:/math-worktrees/r2-int/.claude/skills/do-math/scripts/` 기준이다.
- 병합은 취소하지 않고, 멈춘 상태에서 diff3 형태로 충돌을 다시 펼쳐(`git checkout --conflict=diff3`) 기준(`24682fd`)과 대조하며 풀었다.
- 시험은 실행하지 않았다(사용자 결정). 줄 끝은 LF 그대로다(바꾼 파일 모두 CRLF 0개를 확인했다).

## 1. 파일별 해결

충돌은 제품 7개 파일(수정/삭제 충돌인 `domains.py`까지 8개)과 시험 6개 파일에 있었다. 어느 파일도 한쪽을 통째로 택하지 않았다. 기준 대비 양쪽이 각각 무엇을 지웠고 무엇을 더했는지 나누어 본 뒤, 두 변경을 모두 적용한 형태로 다시 썼다.

### 1.1 제품 모듈

| 파일 | HEAD 쪽 의도 | r2-a 쪽 의도 | 해결 |
|---|---|---|---|
| `do_math/control_contracts.py` (import 1곳) | E(IO-07): `base64`·`binascii`·`hashlib`·`re` import 추가(원자료 정규화, 요청 ID 검사) | A(STO-11): `functools.cache` import 추가(`_configure_validator`) | 두 import 묶음을 모두 둔다. |
| `do_math/engine.py` (5곳) | ① B(STO-01): `inspect_current_state` import 삭제 ② B(STO-20): `_saved_state`·`_state_signature` 삭제, `_reload` 도입 ③ B(STO-08): 실행의 `input_sha256` 필드 삭제 ④ E(ENG-07·RUN-24): `_runner_tools`·`inspect.signature` 분기를 지우고 `on_observation`을 무조건 넘김 | ① `launch`, `record_model_policy_violation`, `supervision_facts`, `SLOT_WAITS`·`held_reservations` import 추가 ② RUN-18: `_slots` 캐시 재결합 코드 삭제 ③ 결정 4: 실행의 `budget_kind` 삭제 ④ 추가 배정: `getattr(self, "_stop_deadlines", {})`를 직접 접근으로 | ① A의 import 네 줄을 두고 `inspect_current_state` 줄은 뺐다. ② `_save` 끝은 `self._evaluate_stops()`만 남는다(`_saved_state`도, `_slots` 재결합도 없음). ③ `status()`는 `self._reload(snapshot)` 한 줄이다. ④ 실행 레코드 생성에서 `budget_kind`와 `input_sha256`을 모두 뺐다. ⑤ 러너 인자는 E의 형태(`on_observation=` 직접 전달)에 `deadlines = self._stop_deadlines`를 붙였다. |
| `do_math/lifecycle_engine.py` (1곳) | C(ENG-03): `_run_external_action`의 `available_input_refs` 덧붙이기 네 줄 삭제 | A(ENG-05): `active_execution` 손 쓰기(`else:` 분기) 삭제 | 두 삭제를 모두 적용했다. 해당 위치에는 아무 줄도 남지 않는다. |
| `do_math/model_runner.py` (1곳) | B(STO-08): 입력 대조를 `execution['input_manifest']['prompt']['sha256']`로 | A(RUN-03): 요청 해시 대조를 `capacity.process`(`published`)로 | `published.get('request_sha256')`와 `input_manifest.prompt.sha256` 대조를 함께 둔다. 과제 설명이 예고한 E(RUN-24)와 A(`budget_kind` → `role not in WORK_ROLES`)의 인접 변경은 git이 충돌 없이 합쳤다. 병합 결과에 두 변경이 모두 있는 것을 원문으로 확인했다(63–72행: 역할 기준 기한 검사, 프로필 고정 시 `scholarly_server`·`claude_only_assigned_model` 명시 인자 거부). |
| `do_math/scheduler.py` (1곳) | A(RUN-09): `_retry_provider_actions()` 호출 삭제 | C(ENG-04): `instance["available_input_refs"]` 저장 한 줄 삭제 | 두 삭제를 모두 적용했다. 소유 루프는 `_refresh_readiness()`로 바로 이어진다. |
| `do_math/record_schemas/__init__.py` (1곳과 import) | B(STO-12): `task_readiness` 파생 가족 등록 삭제. B(STO-15): `from .schemas import *` 대신 명시 import | A(STO-11): 설정 절을 `config_schema()`·`EFFORTS`·`POSITIVE_SETTINGS`로 옮기고 `session_limits`를 `work`만으로 | A의 `config_schema()` 구조를 두고 `task_readiness` 등록은 뺐다. `config_schema()`가 쓰는 `enum`이 B의 명시 import에 없어서 import 목록에 `enum`을 더했다. 그 밖의 A 변경(`active_execution(s)` 참조 함수 삭제, 동시성 제약 검사를 `model`·`work_slots`·`accounting_unit`만으로)은 충돌 없이 들어왔다. |
| `do_math/record_schemas/schemas.py` (4곳) | B(STO-02·STO-15·ENG-20·STO-08): 열거값을 상수에서 만들고, `domains.py`의 수정을 최종형으로 합치고, `engine_sha256`·`input_sha256`을 지우고, 실행 프로필·용량 제약의 세부 모양을 정의 | 결정 4: 실행·실행 프로필(필수 목록)·용량 제약·grant에서 `budget_kind`를 빼고, 용량 제약에서 `operations_slots`·`total_slots`를 뺌 | 네 곳 모두 HEAD의 정의를 바탕으로 A가 지운 필드만 뺐다. 실행: `budget_kind` 삭제(`engine_sha256`·`input_sha256`은 HEAD대로 없음). 실행 프로필: 필수 목록에서 `budget_kind` 삭제(HEAD의 `observation`·`window`·`input`·`ai` 세부 모양은 유지). 용량 제약: `operations_slots`·`total_slots`와 `domains.py`에서 들어온 `budget_kind`를 삭제(`host_id`·`control_reserve`·`authority_refs`는 유지). grant: HEAD의 `expired` 상태를 두고 `budget_kind`만 삭제. |
| `do_math/record_schemas/domains.py` (수정/삭제) | B(STO-15): 파일 삭제, 모든 수정을 `schemas.py`로 이동 | A: 이 파일의 `extend()`에서 결정 4·RUN-09 관련 정의를 수정 | 파일은 삭제 상태로 두고(`git rm`), A의 수정을 `schemas.py`의 대응 정의에 옮겨 적용했다. 내용은 1.2절. |

### 1.2 `domains.py`에서 옮긴 그룹 A 변경

A의 `domains.py` diff(`git diff 24682fd r2-a -- …/domains.py`)는 다섯 곳이다. 각각을 `schemas.py`의 대응 정의에 다음과 같이 적용했다.

1. **외부 작업**(`RECORDS["external_operations"]`): `"budget_kind": enum("work", "operations")`를 지웠다. `producer_executions` 뒤에는 `actor_kind`가 바로 온다.
2. **용량 제약의 `budget_kind`**(`RECORDS["capacity_constraints"]["properties"]["budget_kind"]` 삭제): 1.1절 표의 용량 제약 충돌 해결에 포함했다.
3. **실행의 `capacity`**(A는 `budget_kind: TEXT` 한 항목을 삭제): B의 RUN-20이 같은 정의에서 미사용 7필드를 이미 지웠고, 그 7필드에 `budget_kind`가 들어 있다. 그래서 두 변경을 합친 결과는 B의 네 키 `{provider, reservation_ids, process, local_termination}`와 같다. A의 생산자(`session_slots.py:209-210`)와 A가 고친 시험(`test_checkpoint_persistence`, `test_currentness_recovery`, `test_redesign_ACTIVITIES`)이 정확히 이 네 키를 쓰는 것을 확인했다.
4. **행동 스키마**(`_ACTION`, A는 `action["properties"].update`에서 `budget_kind` 삭제): `_ACTION`의 `"budget_kind": enum("work", "operations")`를 지웠다.
5. **대기 기록**(`waiting_actions`, A는 `extend()`의 덮어쓰기에서 `provider`·`generation`·`retry_at`·`activity_wait`를 삭제): `provider`, `generation`, `activity_wait`를 지웠다. `retry_at`은 A의 실제 효과에 맞췄다. 기준 커밋의 `schemas.py`에는 대기 기록의 `"retry_at": TEXT`가 따로 있었고, A는 그 줄을 두고 `domains.py`의 덮어쓰기(`nullable({"anyOf": [TEXT, NAT]})`)만 지웠다. 그래서 A 브랜치의 유효 스키마는 `"retry_at": TEXT`였다. B가 두 정의를 합칠 때 덮어쓰기 쪽을 남겼으므로, 합친 정의를 `"retry_at": TEXT`로 되돌렸다(4절 1).

A가 `schemas.py`에서 직접 고친 나머지 항목(실행 최상위 `process` 삭제, 예약의 `budget_kind` 삭제, 런타임 `active_execution(s)` 삭제)은 충돌 없이 합쳐졌다. 병합 결과에 이 이름들이 남지 않은 것을 grep으로 확인했다.

### 1.3 시험

| 파일 | HEAD 쪽 | r2-a 쪽 | 해결 |
|---|---|---|---|
| `tests/test_lifecycle_engine.py` (import) | B: `StateStore` import 추가 | A: `from state_fixtures import owner_calls` 추가 | 둘 다 둔다. |
| `tests/test_machine_parallel.py` (대역) | C: `_available_inputs` 대역 삭제 | A: `_retry_provider_actions` 대역 삭제 | 두 대역을 모두 지웠다. 두 메서드는 이제 소유 루프가 부르지 않는다. |
| `tests/test_native_final_submission.py` (고유 결과 픽스처) | B: `input_sha256` 대신 `input_manifest.prompt`에 봉인 digest를 넣음 | A: 프로세스 식별을 `capacity.process`로 옮김 | B의 manifest 설정과 A의 `capacity = {'local_termination': 'confirmed', 'process': {...}}`를 함께 둔다. 최상위 `execution['process']`와 `input_sha256`은 모두 없다. |
| `tests/test_redesign_ENGINE.py` (import) | B·E: `current_state`, `write_checkpoint` import | A: `owner_calls` import | 둘 다 둔다. |
| `tests/test_redesign_PROFILES.py` (설치 복구 시험의 상태) | B: 최소 상태를 `current_state(...)`로 바꿈(수명 주기 관문) | A: 설정에 `operator_enabled: True`를 더함(감독 사실의 기본값이 비활성) | `current_state`를 쓰되 `"config": {**CONFIG, "operator_enabled": True}`로 두었다. |
| `tests/test_state_checks.py` (예약 검사) | B: 예약 결함을 적재 거부 단언으로 옮기고 소유자 검사를 따로 둠 | A: 예약 픽스처에서 `budget_kind` 삭제 | B의 시험 구조를 두고 `balanced` 예약에서 `budget_kind`를 뺐다. 예약 스키마에 이 필드가 없으므로, 남기면 적재 거부의 원인이 달라진다. |

## 2. 이름 정리

### 2.1 그룹 A 코드가 HEAD 쪽의 옛 이름을 부르는 곳

A 브랜치가 더한 줄 전체(`git diff -U0 24682fd r2-a`의 `+` 줄)와 병합 결과의 제품·시험 코드 전체에서 아래 이름을 찾았다. 충돌 해결로 없앤 세 곳 말고 고칠 곳은 없었다.

- `planning._records`(→ `planning.record_index`): 없음. A가 고친 호출부는 `selection(..., instance=)` 쪽이고, 색인 함수는 부르지 않는다.
- `_verify_current_head`: 없음.
- 실행의 `input_sha256`: 충돌 해결로 두 곳을 없앴다(`engine.py` 실행 레코드 생성, `model_runner.verified_native_final`). 남은 `input_sha256`은 모두 위임 판정 기록(`delegations`, `delegation_applications`, `delegation_input_sha256`)의 다른 개념이다.
- `available_input_refs` 저장 필드: 충돌 해결로 두 곳을 없앴다(`lifecycle_engine._run_external_action`, `scheduler` 소유 루프). 남은 사용처는 모두 역할 입력 문맥의 키(`context["available_input_refs"]`)이거나 `task_contracts.available_input_refs` 함수다.
- `domains` 모듈 import: 없음. 병합 결과에 `domains.py`가 없고, import 확인도 통과했다.
- 그 밖에 HEAD 쪽이 지우거나 바꾼 이름도 A가 더한 줄에서 찾았으나 없었다: `_state_signature`, `_saved_state`, `_require_current_contract`, `engine._records`, `ENGINE_SHA256`·`engine_sha256`, `inspect_persisted_state`, `inspect_current_state`의 엔진 import, `task_readiness` 가족, 실행 최상위 `reservation_ids`, `_runner_tools`, `_drain_review_observations`, `_review_event_cursors`, `cli.control_request_id`, `OBSERVATION_OPERATORS`·`OBSERVATION_SOURCES`, `academic._evidence`, `formal._ident`, `knowledge._records`, `delegated_to_task_id`, `resolution_evidence`, `include_operator`, `probe_codex`.
- 추가 수정 하나: `record_schemas/__init__.py`의 명시 import에 `enum`을 더했다. A의 `config_schema()`는 B 이전의 `import *`로 `enum`을 얻었기 때문이다.
- 역방향 호출 확인: A가 바꾼 `model_policy.selection(..., *, instance=)`와 `work_profile_selection(config, task, instance)`의 호출부 11곳(cli, context_store, decision_engine, input_recovery, lifecycle_engine 3곳, scheduler 2곳, engine, planning)이 병합 뒤에도 새 서명을 쓴다. `SessionSlots.acquire`의 호출부 3곳(engine, provider_engine, scheduled_operator)도 `pool` 인자 없이 부른다.

### 2.2 HEAD 쪽 코드가 그룹 A가 지운 이름을 부르는 곳

찾은 이름은 `budget_kind`, `operations_slots`, `total_slots`, `session_limits`의 `operations`, `operations_capacity`, `active_execution(s)` 저장 필드, `_slots` 캐시, `SessionSlots.configure`, `_hold_provider_action`, `_retry_provider_actions`, `provider_wait_disposition`, `activity_wait`, `BudgetReplayConflict`·`ReservationPlan`·`SettlementPlan`·`canonical_record_bytes`, `CONFIG_PATCH`·`OPTIONAL_CONFIG`, `no_substantive_action`·`checkpoint_deadline_elapsed`·`local_termination_observed`, 실행 최상위 `process`다.

- 충돌 해결로 없앤 곳: `schemas.py`의 `budget_kind` 6곳(실행, 실행 프로필 필수 목록, 용량 제약, grant, `_ACTION`, 외부 작업)과 `operations_slots`·`total_slots`, `engine.py`의 `_slots` 재결합 두 곳, `scheduler.py`의 `_retry_provider_actions()`, `test_machine_parallel.py`의 대역, `test_state_checks.py`의 `budget_kind`, `test_native_final_submission.py`의 `execution['process']`.
- 충돌 밖에서 고친 곳 하나: `tests/test_provider_final_contract.py:31`. 설정을 `session_limits={pool: {model: 3} for pool in ('work', 'operations')}`로 만들고 있었다. A 브랜치에도 같은 줄이 남아 있었다(A가 고친 52개 파일 밖). 결정 4에 맞춰 `session_limits={'work': {model: 3}}`로 고쳤다.
- 고치지 않은 남은 일치 항목과 그 이유는 다음과 같다.
  - `engine.py:1433`, `1450`의 `active_execution(s)`는 A(ENG-05)가 만든 `status()` 계산값이다. 저장 필드가 아니다.
  - `tests/test_session_scheduler.py:418`의 `state["active_executions"]`도 이 status 값을 읽는다.
  - `tests/test_current_contract.py:43`은 `operations`가 든 `session_limits`를 거부하는지 확인하는 A의 시험이다.
  - `scheduler._local_call_returned`는 A가 이중 호출만 지운 메서드이고, 이름은 그대로 쓰인다.
  - 그 밖의 `"operations"`는 모두 별개 개념이다. 질문·대기의 `next_owner`, 작업 공간의 `operations` 추적 디렉터리, `session_slots`의 대기 분류 소유자가 여기에 속한다.

## 3. 확인 결과

- **문법.** 바꾼 14개 파일에 `python -m py_compile`을 실행했고 모두 통과했다. 제품 7개(`control_contracts`, `engine`, `lifecycle_engine`, `model_runner`, `record_schemas/__init__`, `record_schemas/schemas`, `scheduler`)와 시험 7개(충돌 6개와 `test_provider_final_contract`)다.
- **import.** `python -c "import sys; sys.path.insert(0, r'C:/math-worktrees/r2-int/.claude/skills/do-math/scripts'); import do_math.engine, do_math.cli, do_math.scheduled_operator"`를 실행했고 오류 없이 통과했다(`IMPORT_OK`). 고친 import 오류는 없다. `enum` 누락은 이 확인 전에 원문 대조로 찾아 고쳤다. `config_schema()`는 설치 시점에 불리므로 import만으로는 드러나지 않는 오류였다.
- **충돌 표지.** `scripts/` 아래 `.py` 파일에 `<<<<<<<`·`>>>>>>>`가 남지 않았다. `git diff --name-only --diff-filter=U`는 비어 있는 상태에서 커밋했다.
- **줄 끝.** 바꾼 14개 파일 모두 CRLF 0개, LF만 있다.

## 4. 남은 판단과 위험

시험을 실행하지 않았으므로 아래는 모두 미확인이다.

1. **대기 기록의 `retry_at`.** 결과-A는 대기 기록의 `retry_at` 스키마 필드를 지웠다고 적었다. 하지만 A 브랜치의 실제 유효 스키마는 기준 `schemas.py`의 `"retry_at": TEXT`를 그대로 가졌다. 이 병합은 A의 실제 효과(`TEXT`)를 따랐다. 대기 기록에 `retry_at`을 쓰는 생산 코드는 찾지 못했다. 읽는 곳은 `reporting.py:103`의 `next_observation_at` 하나다. 필드를 완전히 지울지는 통합자가 정한다. 지운다면 `reporting.py:103`도 함께 정리해야 한다.
2. **B의 수명 주기 관문과 A의 시험.** B(STO-01)부터 모든 적재가 수명 주기 관문을 검사한다. A가 고친 시험 가운데 `{"feature_version": 5}` 같은 최소 상태를 저장하는 곳이 있으면 적재 단계에서 실패한다. 충돌이 난 `test_redesign_PROFILES` 한 곳은 `current_state`로 맞췄다. 충돌 없이 합쳐진 A의 시험은 전수로 대조하지 않았다.
3. **E의 관찰 계약과 A의 시험.** A의 `owner_calls`·`start_model_call` 도우미가 E가 바꾼 `ObservationBatch`(`rows`·`first_row`)나 checkpoint 기반 카운터 계약과 부딪치는지는 확인하지 않았다.
4. **ModelCalls 이벤트 모양.** A(ENG-21)가 이벤트 튜플을 3원소로 바꿨다. 다른 그룹이 새로 쓴 시험이 옛 4원소 모양을 가정하는지 전수로 찾지 않았다.
5. **결정 4의 운영 역할 상한.** 결과-A 0절이 보고한 세 경로, 곧 `intent_interpretation`, `maintenance`, 라이브가 아닌 `operational_review`의 상한 부재는 이 병합과 무관하게 그대로다.

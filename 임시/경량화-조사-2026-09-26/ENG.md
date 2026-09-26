# ENG — 엔진 핵심 영역 경량화 조사

조사 대상은 `engine.py`, `scheduler.py`, `parallel.py`와 `references/공통-실행.md`의 대응이다. 모든 좌표는 2026-09-26 작업 트리(HEAD `8d2ffd0`) 기준이며, 경로 앞부분 `C:/math/.claude/skills/do-math/`는 `DM/`로 줄여 적는다. 저장소 파일은 하나도 수정하지 않았고 테스트는 실행하지 않았다.

## 1. 읽은 범위

전문을 읽은 파일은 다음과 같다.

- `C:/math/임시/경량화-조사-2026-09-26/기준.md` (121행)
- `C:/math/docs/do-math/검사-경량화-이음새-계약.md` (160행)
- `DM/scripts/do_math/engine.py` (4,817행)
- `DM/scripts/do_math/scheduler.py` (660행)
- `DM/scripts/do_math/parallel.py` (214행)
- `DM/references/공통-실행.md` (345행)
- `C:/math/기억/layer3/L-0020.md` (147행). 작업 기억 참조 규칙에 따라 읽었다.

이음새를 따라가며 일부만 읽은 파일과 범위는 다음과 같다.

| 파일 | 읽은 범위 |
|---|---|
| `DM/scripts/do_math/context_store.py` | 375-714, 785-797 |
| `DM/scripts/do_math/repository.py` | 73-79, 159-165, 200-259, 276-321, 365-395 |
| `DM/scripts/do_math/control_contracts.py` | 60-140 |
| `DM/scripts/do_math/planning.py` | 176-180, 220-233, 254-256, 331-361, 369-389, 531-573 |
| `DM/scripts/do_math/submission.py` | 442-490, 625-667 |
| `DM/scripts/do_math/lifecycle_engine.py` | 888-918, 1140-1210, 1325-1340 |
| `DM/scripts/do_math/state_checks.py` | 235-255 |
| `DM/scripts/do_math/git_store.py` | 265-305 |
| `DM/scripts/do_math/session_slots.py` | 10-45 |
| `DM/scripts/do_math/file_io.py` | 함수 목록, 100-112 |
| `DM/scripts/do_math/trust_inventory.py` | 205-235 |
| `DM/scripts/do_math/trust_validation.py` | 150-176 |
| `DM/scripts/do_math/formal.py` | 154-176, 423-426 |
| `DM/scripts/do_math/model_runner.py` | 37-45, 150-185, 295-303 |
| `DM/scripts/do_math/observation_transport.py` | 1-27 |
| `DM/scripts/do_math/governance_engine.py` | 133-163 |
| `DM/scripts/do_math/initialization.py` | 93-96 |
| `DM/scripts/do_math/task_contracts.py` | 251-276 |
| `DM/scripts/do_math/record_schemas/schemas.py` | 100-112 |
| `DM/scripts/do_math/relation_refs.py` | 1-16 |
| `C:/math/기억/색인.md` | layer-3 절과 layer-1 목록(5-38) |

그 밖에 테스트 파일은 가짜 객체 시그니처와 관련 테스트 이름을 grep 결과 줄로만 확인했다.

## 2. 후보

#### ENG-01: 역할 집합 `MACHINE_ROLES`·`WORK_ROLES`가 두 모듈에 같은 값으로 따로 정의돼 있다
- 유형: 이음새중복
- 위치:
  - `DM/scripts/do_math/scheduler.py:12-13`
  - `DM/scripts/do_math/execution_profiles.py:17-18`
  - `DM/scripts/do_math/engine.py:49`(`scheduler`에서 `WORK_ROLES` import)
  - `DM/scripts/do_math/engine.py:633`(`execution_profiles.MACHINE_ROLES` 사용)
  - `DM/scripts/do_math/governance.py:18`(이름은 같고 값은 다른 `WORK_ROLES`)
- 현상:
  - `scheduler.py:12-13`과 `execution_profiles.py:17-18`에 두 집합이 글자 그대로 같게 정의돼 있다.
  - 엔진은 `WORK_ROLES`를 scheduler에서, `MACHINE_ROLES`를 execution_profiles에서 가져온다. scheduler 자신은 자기 사본을 쓴다(`scheduler.py:519`).
  - `governance.py:18`의 `WORK_ROLES`에는 `formal_check`가 더 들어 있다. 이름이 같지만 뜻이 다른 개념이다.
  - 검색식: `grep -rn "MACHINE_ROLES\s*=\|WORK_ROLES\s*=" do_math`
- 제안:
  - 정본은 `execution_profiles.py:17-18`로 둔다. `scheduler.py:12-13`을 지우고 `from .execution_profiles import MACHINE_ROLES, WORK_ROLES`로 바꾼다.
  - `engine.py:49`는 execution_profiles에서 import한다.
  - `governance.WORK_ROLES`는 합치지 않고, 뜻에 맞는 이름(예: `AUTHORIZED_WORK_ROLES`)으로 바꾸는 것을 governance 소유자에게 제안한다.
- 동작: 보존
- 실익:
  - 중복 정의 2행이 줄어든다.
  - 역할 추가 때 한쪽만 고쳐 스케줄러의 기계 역할 판정(`scheduler.py:519`)과 프로필 선택(`engine.py:633`)이 갈라지는 경로가 없어진다.
- 위험과 보호:
  - import 순환의 위험이 있다. scheduler는 이미 `model_policy`, `session_slots`를 import하므로 execution_profiles를 import해도 순환이 새로 생기는지 확인해야 한다(미확인).
  - 덮는 테스트는 `tests/test_lifecycle_engine.py`(두 이름을 참조)다.
- 확신: 높음 — 두 정의의 문자열이 같고 사용처가 grep으로 전수 확인된다.
- 다른 영역: `execution_profiles.py`, `governance.py`

#### ENG-02: 과제 입력의 "사용 가능" 판정이 세 곳에서 서로 다른 규칙으로 구현돼 있어, 생산자 검사를 통과한 후보를 엔진이 반려할 수 있다
- 유형: 이음새중복(생산자 자기확인과 수신 판정의 불일치)
- 위치:
  - 제출 검사(생산자 도구와 수신 구조 검사가 공유): `DM/scripts/do_math/submission.py:625`(`known = _reference_ids(context)`), `:641`, `:666-667`
  - 엔진 적용: `DM/scripts/do_math/engine.py:4082-4090`(`available = set(self._available_inputs())`), `:2581-2592`
  - 착수 판정: `DM/scripts/do_math/planning.py:568-573`
- 현상: 세 곳이 허용하는 참조의 범위가 다르다.
  - **제출 검사**는 `available_input_refs`, `_reference_ids(context)`, 같은 응답의 새 과제 제목을 허용한다. `_reference_ids`는 결정·허가·실행·사건·외부 작업·질문·사용자 입력·거버넌스 기록 ID까지 모은다(`submission.py:442-476`).
  - **엔진 `_apply`**는 적용 시점에 새로 계산한 `_available_inputs()`만 허용한다(`engine.py:4088-4090`). 이 목록에 들어가는 것은 SKILL.md, GLOSSARY.md, context 두 개, 조건부 tool 두 개, 지식·과제 ID, 원자료 별칭뿐이다.
  - **`task_ready`**는 `planning.RECORD_FAMILIES`의 모든 기록과 `available_input_refs`를 허용한다(`planning.py:569-573`). 이 기록에는 결정, 허가, 거버넌스, 외부 작업이 포함된다.

  그 결과가 이렇다. 후보 준비가 `inputs`에 결정 ID나 허가 ID를 쓰면 `check_submission.py`는 통과시키고, 착수 판정도 그 입력을 받아들인다. 그런데 엔진 적용은 `task inputs must copy available source refs`로 그 묶음을 반려하고, 수리 회차가 열린다. 또 `tool:lean`의 존재 여부가 입력 시점(`available_input_refs`)과 적용 시점(`_lean_discovered`)에서 따로 판정된다. 공통-실행.md:43은 "사용할 ID가 `available_input_refs`나 제공된 기록에 정확히 존재하는가"를 기준으로 적고 있다.
- 제안:
  - `planning.py`(또는 `task_contracts.py`)에 `task_input_errors(refs, instance, runtime, *, available, new_titles=())` 하나를 둔다.
  - 제출 검사(`submission.py:666-667`), 엔진 적용(`engine.py:4088-4090`), 착수 판정(`planning.py:568-573`)이 모두 이 함수를 부른다.
  - 허용 집합을 셋 중 어느 것으로 할지는 사용자 결정이다. 기본안은 공통-실행.md:43의 문언대로 "지급된 `available_input_refs` 또는 기록 가족에 실재하는 ID"다.
  - 엔진 적용은 새로 계산한 목록 대신, 실행이 받은 고정 입력(`input/submission/context.json`의 `available_input_refs`)을 쓴다.
- 동작: 변경 — 허용 집합이 하나로 정해지므로, 지금 셋 중 한쪽만 허용하는 참조(결정·허가·거버넌스 ID 등)의 수락 여부가 바뀐다.
- 실익:
  - 규칙 구현 3개가 1개로 준다.
  - 생산자 검사를 통과한 후보가 적용에서 반려돼 생기는 수리 실행 1회가 사라진다. 모델 호출 1회와 검토 비용이 해당한다(추정).
  - Lean 발견 여부의 시점 차이 경로도 사라진다.
- 위험과 보호:
  - 허용 집합이 넓어지면 착수 판정이 기록의 판본 변화를 감시해야 할 대상이 늘어난다. `capture_task_basis`의 대상 가족을 함께 확인해야 한다.
  - `unknown task inputs`, `task inputs must copy`를 직접 단언하는 테스트는 찾지 못했다. 그러므로 보호하는 테스트는 `없음`이다. 검색식: `grep -ln "unknown task inputs\|task inputs must copy" tests/*.py`
- 확신: 중간 — 세 규칙의 차이는 원문으로 확인했지만, 실제 운전에서 이 반려가 일어났는지는 확인하지 않았다.
- 다른 영역: `submission.py`, `planning.py`, 계약 문서 `계약/후보-준비.md`

#### ENG-03: 외부 작업 확정 때 `available_input_refs`에 덧붙인 ID가 다음 소유 루프에서 덮어써진다
- 유형: 죽은코드(덮어써지는 쓰기)
- 위치:
  - 쓰기: `DM/scripts/do_math/lifecycle_engine.py:1174-1177`
  - 덮어쓰기: `DM/scripts/do_math/scheduler.py:597`, `DM/scripts/do_math/engine.py:3334`
  - 계산: `DM/scripts/do_math/engine.py:2581-2592`
- 현상:
  - `_run_external_action` 경로는 확정된 외부 작업의 ID를 `instance["available_input_refs"]`에 덧붙인다.
  - 그러나 소유 루프는 매 회차(`scheduler.py:597`)와 매 실행 준비(`engine.py:3334`)에서 이 필드를 `_available_inputs()`로 통째로 다시 쓴다. 이 계산은 외부 작업 ID를 넣지 않는다(`engine.py:2582-2592`).
  - 따라서 덧붙인 ID는 한 번 게시된 뒤 다음 회차에 사라진다.
  - 한편 착수 판정은 외부 작업을 기록 가족으로 이미 인정한다(`planning.py:340`, `:570`). 이 덧붙이기가 유지돼야 효력이 생기는 소비자는 확인되지 않았다.
  - 검색식: `grep -rn "available_input_refs" do_math/*.py`
- 제안: 둘 중 하나를 사용자가 고른다.
  - (a) 의도가 "확정된 외부 작업을 입력으로 쓸 수 있게 한다"이면 `_available_inputs()`에 `status=='confirmed' and succeeded` 외부 작업을 넣고 `lifecycle_engine.py:1174-1177`을 지운다.
  - (b) 의도가 없으면 그 네 줄만 지운다.
- 동작: 보존((b)의 경우. 다음 회차에 사라지던 일시적 값만 없어진다). (a)는 변경이다.
- 실익:
  - 4행이 줄어든다.
  - 같은 필드에 규칙이 다른 두 작성자가 있어서 생기는 혼동이 사라진다.
  - 덧붙임과 재계산으로 게시가 한 번 더 일어나는 경우도 없어진다(추정).
- 위험과 보호:
  - `record_schemas/__init__.py:577`은 이 목록을 질문 대상의 허용 집합에 쓴다. 덧붙인 직후에 게시되는 질문 경로가 있는지 확인해야 한다(미확인).
  - 덮는 테스트는 `없음`이다(`grep -rn "available_input_refs" tests/*.py`는 fixture 1줄만 찾았다).
- 확신: 높음 — 덮어쓰기 경로를 원문으로 확인했다.
- 다른 영역: `lifecycle_engine.py`, `record_schemas`

#### ENG-04: `available_input_refs`는 호스트 상태에 의존하는 파생값인데 연구 상태에 저장된다
- 유형: 파생상태
- 위치:
  - `DM/scripts/do_math/engine.py:2573-2592`, `:3334`
  - `DM/scripts/do_math/scheduler.py:597`
  - `DM/scripts/do_math/record_schemas/domains.py:238`
  - 소비자: `DM/scripts/do_math/planning.py:229`, `:570`, `DM/scripts/do_math/submission.py:482`, `:641`, `DM/scripts/do_math/questions.py:66`
- 현상:
  - 이 목록은 지식·과제·원자료 ID와, 호스트에서 Lean이 발견됐는지(`_lean_discovered`, 1초 주기로 파일 시스템을 조회)로 계산된다.
  - 그런데 `instance`에 저장되어 게시된다. 따라서 Lean 설치 상태가 바뀌면 연구 상태의 새 판본이 게시된다.
  - 소비자 가운데 일부(`planning.task_ready`)는 저장된 값을, 일부(`engine._apply`)는 새로 계산한 값을 읽는다(ENG-02).
- 제안:
  - 저장을 멈추고, 필요한 곳에서 계산하게 한다.
  - 역할 입력에는 `_context`가 계산해 `available_input_refs`로 지급하고(engine 1886), 착수 판정에는 인자로 넘긴다.
  - 스키마 필드는 do-math-state/5의 기존 상태 호환을 위해 선택 필드로 남긴다.
- 동작: 변경 — 저장 상태에서 필드가 빠지고, Lean 설치 변화가 상태 게시를 유발하지 않는다.
- 실익:
  - 소유 루프 회차마다 하던 목록 재계산과 상태 비교 입력이 사라진다.
  - 호스트 변화로 생기는 커밋이 사라진다.
  - 저장값과 계산값이 어긋나는 경로가 없어진다.
- 위험과 보호:
  - 질문 대상 검증(`record_schemas/__init__.py:577`)은 상태만 받으므로, 인자를 추가해야 한다.
  - 덮는 테스트는 `tests/test_efficiency.py::test_readiness_is_derived_and_changes_with_contract_review_evidence`로 간접적이다.
- 확신: 중간 — 소비자는 전수 확인했지만, 저장 필드를 제거하는 것은 저장 계약 변경이다.
- 다른 영역: `planning.py`, `record_schemas`, `questions.py`, `submission.py`

#### ENG-05: `runtime.active_execution(s)`는 `_save`가 매번 다시 계산하는 파생값인데, 12곳에서 손으로 쓰고 있다. 또 묶음 게시 경로는 이 값을 다시 계산하지 않는다
- 유형: 파생상태
- 위치:
  - 재계산: `DM/scripts/do_math/engine.py:879-881`
  - 손 쓰기: `DM/scripts/do_math/engine.py:3527`, `:3713`, `:4599`, `:4678-4679`, `DM/scripts/do_math/lifecycle_engine.py:1158-1159`, `:1173`, `:1226`, `:1265`, `:1358`, `:1436-1437`
  - 재계산 없는 게시: `DM/scripts/do_math/engine.py:2355-2363`(`publish`가 `store.save_with_state`를 직접 부른다)
  - 소비자: `DM/scripts/do_math/engine.py:1556`(status가 저장된 `active_execution`을 읽는다). `:1575`의 status는 `active_executions`를 저장값 대신 새로 계산한다.
- 현상:
  - `_save`는 게시 직전에 두 필드를 실행 상태에서 다시 계산한다. 그래서 그 앞의 손 쓰기는 게시 전에 덮어써진다. 엔진 쪽 네 곳은 뒤따르는 `_save`를 원문으로 확인했다(3527→3538, 3713→3715, 4599→4600, 4678→4700).
  - 여러 실행이 병렬이면 `live[0]`이 선택되므로, 손으로 쓴 ID가 남는다는 보장도 없다.
  - 반면 `_apply_submission_bundles`의 게시는 재계산을 거치지 않는다.
  - 코드 소비자는 status 한 곳이다. 문서는 status의 `active_executions`만 설명한다(`references/CLI-실행-계약.md:216`).
  - 검색식: `grep -rn "active_execution\b\|active_executions" do_math/*.py`
- 제안:
  - (1) 손 쓰기 12곳을 지운다.
  - (2) status는 두 값을 모두 실행 목록에서 계산한다.
  - (3) 저장 필드를 없애는 것(스키마 `record_schemas/schemas.py:233`, `__init__.py:136`, `:155-157`)은 저장 계약 변경이므로 별도로 결정한다.
- 동작: 보존((1)(2)). (3)은 변경이다.
- 실익:
  - 12곳의 쓰기와 조건 판정 약 16행이 줄어든다.
  - 파생값이 게시 경로에 따라 달라지는 경로가 사라진다.
- 위험과 보호:
  - lifecycle 쪽 여섯 곳 뒤에 `_save`가 오는지는 원문으로 모두 확인하지 않았다.
  - 저장된 `active_execution`을 단언하는 테스트가 있다: `tests/test_engine.py`, `test_controls.py`, `test_lifecycle_engine.py` 등 6개 파일(`grep -rln "active_execution" tests`). 재계산값이 같으면 통과한다.
- 확신: 중간 — 엔진 쪽은 높고, lifecycle 쪽 후속 저장은 미확인이다.
- 다른 영역: `lifecycle_engine.py`, `record_schemas`

#### ENG-06: 모델·기계 호출에 동기 경로와 병렬 경로가 공존하며, 동기 경로는 테스트만 쓴다
- 유형: 복잡성(같은 일을 하는 두 경로)
- 위치:
  - 동기 경로: `DM/scripts/do_math/engine.py:3190-3204`(`_call`), `DM/scripts/do_math/scheduler.py:89-100`(`_run_machine_steps`의 `_calls` 부재 분기)
  - 병렬 경로: `DM/scripts/do_math/scheduler.py:622-628`, `:86-88`, `DM/scripts/do_math/parallel.py:161-196`
  - 이중 호출: `DM/scripts/do_math/parallel.py:182-183` + `DM/scripts/do_math/engine.py:3615`
  - 실패 형태: `DM/scripts/do_math/engine.py:3199`, `DM/scripts/do_math/parallel.py:176-177`, `DM/scripts/do_math/scheduler.py:92`, `:113`
- 현상:
  - 운영 호출은 모두 `_run_parallel`에서 `_calls`가 설정된 상태로 들어온다. `_formal`·`_process_machine_action`의 운영 호출자는 `scheduler.py:618-619`뿐이다.
  - 그런데도 `_call`과 `_run_machine_steps`의 동기 분기가 남아 있다. `_call`의 호출자는 `tests/test_walkthrough_followup.py:229`, `:444`뿐이다. 동기 기계 분기는 `tests/test_connection_repairs.py`, `tests/test_knowledge_import_engine.py`의 직접 `_formal` 호출이 사용한다.
  - 두 경로가 공존하면서 생긴 결과가 둘 있다.
    - **이중 호출.** `_call_steps`가 반환 직후 `_local_call_returned`를 직접 부른다(engine 3615). 이것은 동기 경로를 위한 호출이다. 운영의 병렬 경로에서는 `ModelCalls.collect`가 `on_returned`로 같은 함수를 먼저 부르므로, 이 함수가 두 번 실행된다.
    - **실패 형태의 차이.** 계산 함수가 예외를 내면 병렬 경로는 `{"status":"failed","output":None,"usage":{},"error":...}`를 만든다. 동기 기계 경로와 `_abort_parallel_calls`는 `{'status':'failed','reason':...}`를 만든다. 그래서 형식 검사 예외의 보존 증거(`formal.json`) 형태가 어느 경로였는지에 따라 달라진다.
- 제안:
  - `_call`과 `_run_machine_steps`의 동기 분기를 제품 코드에서 지운다.
  - 테스트에는 `ModelCalls`를 한 번 돌리는 도우미를 둔다. `tests/state_fixtures.py`에 `start_call` → `wait` → `collect`를 수행하는 함수를 추가하는 방식이다.
  - `engine.py:3615`을 지운다.
  - 실패 결과는 `parallel.py`의 함수 하나(`failed_result(error)`)로 만든다. `scheduler.py:113`도 그 함수를 쓴다.
- 동작: 보존 — 운영 경로의 관찰 결과는 같다. 실패 형태는 지금 운영 경로의 형태로 통일한다.
- 실익:
  - 제품 코드 약 30행이 줄어든다.
  - 호출 반환 처리가 한 경로가 된다.
  - 테스트가 운영과 다른 경로를 검증하는 사각지대가 사라진다.
- 위험과 보호:
  - 직접 `_formal`·`_call`을 부르는 테스트 약 12곳을 도우미로 옮겨야 한다.
  - 덮는 테스트는 `tests/test_machine_parallel.py`(`test_stop_request_reaches_the_calculation_within_one_owner_pass`, `test_owner_exception_stops_worker_preserves_result_and_reconciles_capacity`, `test_failed_judgment_fails_only_its_own_call`)와 `tests/test_stop_flags.py`다.
- 확신: 높음 — 운영 호출자를 grep으로 전수 확인했다(`grep -rn "\._call(\|\._formal(\|_run_machine_steps(" do_math tests`).
- 다른 영역: `lifecycle_engine.py`(기계 단계 생성기), 테스트

#### ENG-07: 호출 대상 시그니처를 조사해 인자를 넣거나 빼는 우회 계층이 있다
- 유형: 불필요기능
- 위치:
  - `DM/scripts/do_math/engine.py:3038-3045`(`_runner_tools`), `:3606-3608`(`on_observation`), `:4625-4632`(`launch_ticket`, `should_stop`, `allowed_axioms`)
  - `DM/scripts/do_math/lifecycle_engine.py:1392-1395`
- 현상:
  - 운영 호출 대상은 이 인자들을 모두 받는다.
    - `ModelRunner.run(*, model, **options)`(`model_runner.py:295`)은 가변 키워드를 받는다.
    - `verify_lean`(`formal.py:423-426`)은 `launch_ticket`, `should_stop`, `allowed_axioms`를 선언한다.
    - `verify_formal`(`trust_validation.py:150`)은 나머지 인자를 그대로 넘긴다.
  - 테스트 가짜 객체도 모두 받는다. 확인한 것은 `formal_ok`(`tests/test_engine.py:148-149`), `formal_fixture`(`tests/test_purpose_engine.py:59-60`), `**kwargs` 람다·함수, `Mock`이다. 러너 가짜 13개도 `**kwargs`를 가진다.
  - 따라서 조사 분기는 언제나 참이다.
  - 그런데 이 분기는 조용한 약화 경로를 연다. `allowed_axioms`를 받지 않는 검증기가 주어지면, 환경의 허용 공리 대신 `verify_lean`의 기본값 `AXIOMS`로 검사된다.
- 제안: 조사를 지우고 인자를 무조건 넘긴다. 받지 못하는 호출 대상은 `TypeError`로 즉시 실패하게 한다.
- 동작: 보존
- 실익:
  - 약 20행과 `inspect` import가 줄어든다.
  - 호출마다 하던 시그니처 조사가 사라진다.
  - 허용 공리가 누락될 수 있는 경로가 제거된다.
- 위험과 보호:
  - 이 인자를 받지 않는 외부 러너가 있으면 깨진다. 저장소 안에는 없다.
  - 덮는 테스트는 `tests/test_machine_parallel.py`, `tests/test_engine.py`(러너 가짜가 해당 인자를 받는다)다.
- 확신: 높음 — 운영과 테스트의 호출 대상을 모두 확인했다.
- 다른 영역: `lifecycle_engine.py`

#### ENG-08: 실행의 고정 입력(`context.json`, `schema.json`) 경로와 읽기가 엔진 9곳과 다른 모듈 2곳에 흩어져 있다
- 유형: 이음새중복, 운영비용
- 위치:
  - 쓰기: `DM/scripts/do_math/engine.py:842-865`(`_input_artifacts`가 `{bundle}/schema.json`과 작업 공간의 `input/submission/*`를 보존)
  - 엔진 읽기: `DM/scripts/do_math/engine.py:1105-1106`, `:1239-1240`, `:1297-1298`, `:1412`, `:2403-2404`, `:2690-2691`, `:2735-2736`, `:3133-3134`, `:4511-4512`
  - 다른 모듈 읽기: `DM/scripts/do_math/submission.py:102`, `DM/scripts/do_math/integration.py:207`
- 현상:
  - `"runtime/artifacts/" + input_bundle + "/input/submission/context.json"`과 `"/schema.json"`의 조립, 그리고 `submission.load_json(self.store.read(...))`가 곳곳에서 반복된다.
  - 매 `submit_intent`(1297), `self_check_response`의 증거 목록(1412), 미리보기(2403)마다 이 파일이 Git에서 다시 읽히고 다시 해석된다.
  - `context.json`은 전체 검증 문맥이다. 계획 역할에서는 과제 전건이 들어간다.
  - 입력 묶음은 불변이다(이음새 계약 S3, `git_store.py`의 번들 불변 검사).
  - 검색식: `grep -rn "input/submission/context.json" do_math/*.py`
- 제안:
  - `submission.py`에 `issued_input(read_artifact, execution, snapshot) -> (context, schema)`를 둔다. 경로 규칙은 이 함수와 `_input_artifacts`의 쓰기 두 곳만 안다.
  - 해석 결과는 `(git_dir, input_bundle)` 키로 프로세스 안에서 메모한다. 호출자가 값을 고칠 수 있으면 사본을 돌려준다.
  - 엔진 9곳, `submission.py:102`, `integration.py:207`이 이 함수를 쓴다.
- 동작: 보존
- 실익:
  - 경로 문자열 조립 약 20행이 줄어든다.
  - 제출·자기 점검·미리보기 요청마다 Git blob 읽기 2회와 JSON 해석 2회가 첫 회 이후 0회가 된다(추정. 크기는 계획 문맥에서 수백 KB).
- 위험과 보호:
  - 메모의 수명은 프로세스이고 키는 불변 번들이므로 무효화 규칙이 필요 없다. 이것은 S3의 전제를 따르는 판단이다.
  - 덮는 테스트는 `tests/test_submission_flow.py`, `tests/test_native_final_submission.py`, `tests/test_impact_bundle.py`(context.json 경로 사용)다.
- 확신: 높음 — 중복 자체는 확실하다. 메모의 실익은 추정이다.
- 다른 영역: `submission.py`, `integration.py`

#### ENG-09: 공급자 stdout JSONL을 사건으로 바꾸는 규칙이 생산자와 엔진에 따로 있고, 엔진은 같은 파일을 다시 읽어 대조한다
- 유형: 이음새중복, 운영비용
- 위치:
  - 생산자: `DM/scripts/do_math/model_runner.py:161-172`
  - 엔진 재독해: `DM/scripts/do_math/engine.py:2880-2905`(`_review_observation_source`), `:2907-2927`(`_drain_review_observations`), `:2943`, `:2955-2956`, `:3014`(`_review_event_cursors`)
  - 묶음의 좌표: `DM/scripts/do_math/observation_transport.py:8-20`(`offsets`)
- 현상:
  - `model_runner`는 줄을 나누고, 빈 줄을 건너뛰고, 해석에 실패하면 `unparsed_observation`으로 바꾼다. 그리고 각 사건의 정확한 바이트 좌표 `(start, end)`를 `ObservationBatch.offsets`에 싣는다.
  - 동일성 검토의 관찰 보존은 이 좌표를 쓰지 않는다. 엔진이 자기 커서로 같은 파일을 처음부터 다시 줄 단위로 읽고, 같은 해석 규칙을 다시 구현해 `decoded != event`로 대조한다(2898-2903).
  - 두 규칙 중 하나만 바뀌면 대조가 실패한다. 그러면 관찰 적용이 실패로 처리되어 실행이 정지된다(`scheduler.py:70-74`).
  - 종료 뒤의 `_drain_review_observations`도 같은 규칙을 세 번째로 구현한다.
  - 검색식: `grep -rn "unparsed_observation" do_math/*.py`
- 제안:
  - 줄 분리와 해석 규칙을 `observation_transport.py`의 함수 하나(`read_batch(path, offset)`)로 옮긴다. `model_runner`와 종료 뒤 배수 처리가 그 함수로 묶음을 만든다.
  - `_review_observation_source`는 `batch.offsets[index]`로 정확한 바이트 `[start, end)`를 한 번 읽어 보존한다.
  - 엔진의 커서 상태, 재해석, 대조를 지운다.
- 동작: 보존 — 보존되는 원 바이트와 사건은 같다.
- 실익:
  - 약 45행과 엔진의 파일 커서 상태가 줄어든다.
  - 관찰 사건마다 하던 파일 재독해와 재해석이 사라진다(동일성 검토 실행 한정).
  - 규칙이 어긋나 실행이 정지되는 경로가 제거된다.
- 위험과 보호:
  - 묶음 없는 dict 사건 경로(`_drain_review_observations`)를 묶음으로 바꿔야 한다.
  - 덮는 테스트는 `tests/test_review_engine.py::test_actual_prompt_and_public_provider_events_restore_only_to_their_slot`, `tests/test_redesign_ENGINE.py`(provider-event 관련)다.
- 확신: 중간 — 종료 뒤 배수 처리가 묶음 수집 뒤에도 필요한지는 확인하지 않았다.
- 다른 영역: `model_runner.py`, `observation_transport.py`

#### ENG-10: OS 파일 잠금 구현이 세 벌이다
- 유형: 이음새중복
- 위치:
  - `DM/scripts/do_math/engine.py:272-306`(`_control_acceptance_lock`, 대기형)
  - `DM/scripts/do_math/git_store.py:269-303`(`writer_lock`, 비대기형)
  - `DM/scripts/do_math/session_slots.py:14-41`(`_lock`/`_unlock`, 비대기형)
  - 원자 쓰기: `DM/scripts/do_math/engine.py:322-329`와 `DM/scripts/do_math/file_io.py:102-111`(`write_bytes_atomic`)
- 현상:
  - 세 곳이 각자 `msvcrt.locking`/`fcntl.flock` 분기, 0바이트 파일 보정, 해제를 구현한다.
  - 엔진판은 잠금 파일을 만들 때 임시 파일과 `os.link`를 쓰는 추가 절차(277-287)를 갖는다. git_store는 같은 목적을 `os.open(..., O_CREAT)` 한 줄로 해결한다.
  - `_next_control_order`는 임시 파일, fsync, `atomic_replace`를 손으로 조합한다. `file_io.write_bytes_atomic`과의 차이는 fsync 하나다.
  - 검색식: `grep -rn "msvcrt.locking\|fcntl.flock" do_math/*.py`
- 제안:
  - `file_io.py`에 `os_lock(path, *, blocking)` 컨텍스트 관리자 하나를 둔다. 세 곳이 이것을 쓴다.
  - `write_bytes_atomic`에 `fsync` 선택 인자를 두고, `_next_control_order`가 이것을 쓴다.
- 동작: 보존
- 실익:
  - 약 50행이 줄어든다.
  - 잠금 규칙을 고칠 때 세 곳을 함께 고쳐야 하는 부담이 사라진다.
- 위험과 보호:
  - git_store는 워커 쪽 적재 제약이 없는 모듈이지만, `file_io`는 워커 Job 안에서도 적재된다(이음새 계약 2.1). 따라서 새 함수는 표준 라이브러리만 써야 한다.
  - 덮는 테스트는 `tests/test_research_recovery.py::test_controls_with_identical_wall_time_preserve_acceptance_order`와 같은 파일의 접수 순서 테스트들이다.
- 확신: 높음 — 중복은 원문으로 확인했다. 실익은 작다.
- 다른 영역: `git_store.py`, `session_slots.py`, `file_io.py`

#### ENG-11: 원자료 제어의 정규화 검사가 생산자(`control`)와 수신자(`_controls`)에 서로 다른 코드로 있다
- 유형: 이음새중복
- 위치:
  - `DM/scripts/do_math/engine.py:350-366`
  - `DM/scripts/do_math/engine.py:956-966`
  - 모양 스키마: `DM/scripts/do_math/control_contracts.py:103`
- 현상:
  - CLI의 `control()`은 원자료를 정규형 `{name, body_base64, sha256, bytes}`로 만들고 해시와 크기를 확인한다.
  - 소유 엔진은 inbox 파일을 읽어 같은 조건(키 집합의 일치, base64 해독, 해시와 크기의 일치)을 다른 문장으로 다시 검사한다.
  - inbox는 디스크 기록이므로 신뢰 경계 밖이다. 수신 검사는 보존해야 한다(기준 문서 「검사의 정의와 실행 위치 원칙」 셋째 항목).
- 제안:
  - `control_contracts.py`에 `normalized_source_bytes(spec) -> bytes`를 둔다. 이 함수는 조건이 틀리면 `ValueError`를 낸다.
  - `control()`은 정규형을 만든 뒤 이 함수로 자기 확인을 하고, `_controls`는 이 함수로 수락 여부를 판정한다.
- 동작: 보존
- 실익: 조건 표현이 2벌에서 1벌로 준다(약 10행). 한쪽만 바뀌어 CLI가 받은 요청을 엔진이 반려하는 경로가 사라진다.
- 위험과 보호: 덮는 테스트는 `tests/test_redesign_ENGINE.py::test_normalized_source_has_one_identity_and_rejects_wrong_bytes`와 `tests/test_cli.py`(원자료 제어)다.
- 확신: 높음
- 다른 영역: `control_contracts.py`

#### ENG-12: 설정 키의 형식 규칙이 네 곳에 적혀 있다
- 유형: 이음새중복
- 위치:
  - `DM/scripts/do_math/engine.py:89-107`(`DEFAULT_CONFIG`)
  - `DM/scripts/do_math/engine.py:133-134`(`OPTIONAL_CONFIG`)
  - `DM/scripts/do_math/engine.py:173-192`(`validate_config`의 effort 값 집합, 불리언 목록, 양의 정수 목록)
  - `DM/scripts/do_math/control_contracts.py:65-77`(`CONFIG_PATCH`의 정수·불리언 키 목록)
  - 문서: `DM/references/CLI-실행-계약.md:206` 부근
- 현상:
  - 같은 키 집합과 형식이 기본값 표, 선택 키 표, 엔진 검사 목록, 제어 스키마 목록에 따로 적혀 있다. 지금은 서로 일치한다.
  - 키를 추가하면 네 곳을 모두 고쳐야 한다. 한 곳을 빠뜨리면 `configure` 제어가 스키마에서 반려되거나, 엔진 검사를 우회한다.
- 제안:
  - `control_contracts.py`에 표 하나를 둔다. 각 키의 종류(양의 정수, 0 이상 정수, 불리언, effort 값 등)와 선택 여부를 적는다.
  - `CONFIG_PATCH`와 `validate_config`의 반복문을 이 표에서 만든다.
  - `DEFAULT_CONFIG`는 값만 가진다.
  - 워커 모듈의 effort 집합(`codex_worker.py:28`, `claude_worker.py:41`)은 보존 판정(3절)에 둔다.
- 동작: 보존
- 실익: 키 목록 3벌이 1벌로 준다(약 20행). 설정 키를 추가할 때 어긋날 수 있는 곳이 3곳 줄어든다.
- 위험과 보호: 덮는 테스트는 `tests/test_current_contract.py::test_retired_configuration_is_rejected_before_creating_an_instance`, `tests/test_redesign_PROFILES.py`, `tests/test_redesign_ENGINE.py`(`validate_config` 사용)다.
- 확신: 높음
- 다른 영역: `control_contracts.py`, `references/CLI-실행-계약.md`

#### ENG-13: 기록 ID의 전역 유일성 검사가 서로 다른 범위로 세 번 구현돼 있다
- 유형: 이음새중복(수신 검사와 게시 전 검사의 범위 차이)
- 위치:
  - `DM/scripts/do_math/engine.py:453-489`(`_records`. 유일한 호출자는 `:2293`)
  - `DM/scripts/do_math/planning.py:369-382`(`RECORD_FAMILIES`의 부분집합, `:331-341`)
  - `DM/scripts/do_math/state_checks.py:238-248`(모든 가족을 범용으로 순회)
  - 소비: `DM/scripts/do_math/engine.py:4761`(`_inspect_before_write`는 `record_storage` 영역을 실행 쓰기 전에 요구한다)
- 현상:
  - 엔진판은 가족 목록을 손으로 적는다. 질문, 예약, 운영 처분, 관찰 등이 여기 들어 있다.
  - planning판은 다른 목록을 쓴다. 거버넌스와 목표 판정은 들어 있고 질문과 예약은 빠져 있다.
  - state_checks판은 두 루트의 모든 가족을 순회한다.
  - 묶음 후보의 게시 전 검사는 엔진판뿐이다. 저장소 `validate_candidate`에는 ID 중복 검사가 없다(`grep -n "duplicate\|collision" repository.py`).
  - 그 결과, 엔진판이 보지 않는 가족 사이의 ID 충돌은 게시된다. 그리고 다음 `run`의 `_inspect_before_write`가 그 상태를 차단한다.
- 제안:
  - `state_checks.py`의 순회를 공개 함수 `record_id_collisions(instance, runtime)`로 꺼낸다.
  - `_validate_bundle_candidate`(`engine.py:2293`)가 이 함수를 쓴다. `engine._records`는 지운다.
  - planning판은 조회용 색인이므로 남기되, 충돌 판정은 같은 함수에 맡긴다.
- 동작: 변경 — 지금은 게시된 뒤 다음 실행에서 차단되는 충돌이 게시 전에 반려된다.
- 실익:
  - 엔진 37행과 가족 목록 1벌이 줄어든다.
  - "게시는 됐는데 실행기가 멈추는" 경로가 제거된다.
- 위험과 보호:
  - state_checks판은 `id`를 가진 모든 행을 센다. 지금 게시되는 정상 상태 중에 이 규칙에 걸리는 것이 있는지는 확인하지 않았다. 그러나 `_inspect_before_write`가 이미 같은 규칙을 요구하므로, 정상 운전 상태는 통과할 것으로 추정한다.
  - `record ID collision`을 단언하는 테스트는 찾지 못했다. 보호하는 테스트는 `없음`이다.
- 확신: 중간
- 다른 영역: `state_checks.py`, `planning.py`

#### ENG-14: 상태 재적재 절차가 7곳에 흩어져 있고, 그중 2곳은 무변경 기준을 갱신하지 않는다
- 유형: 복잡성, 운영비용
- 위치:
  - `DM/scripts/do_math/engine.py:1529-1532`, `:1620-1623`, `:2372-2377`, `:2556-2558`
  - `DM/scripts/do_math/scheduler.py:122-124`
  - 갱신 누락: `DM/scripts/do_math/engine.py:1365-1369`, `:3156-3158`
  - 이중 무변경 판정: `DM/scripts/do_math/engine.py:1535-1537`
- 현상:
  - 재적재는 세 단계로 이뤄진다. `self.head, self.instance, self.runtime = self.store.load()`, `self._saved_state = self._state_signature()`, `self._evaluate_stops()`.
  - 이 세 줄이 곳곳에서 손으로 반복된다. 게시 확인을 잃은 뒤 복구하는 두 곳(1365-1369, 3156-3158)은 `_saved_state`를 갱신하지 않는다.
  - `_state_signature`는 `(self.head, ...)`를 포함한다. 그래서 다음 `_save`는 아무 변화가 없어도 서명 불일치로 판정한다. 그 결과 전체 후보 검증을 수행하고 `updated_at`만 바뀐 커밋을 게시한다.
  - `process_controls`는 `_controls()` 뒤에 게시된 상태를 다시 적재하고 깊은 비교를 한다(1535-1537). `_save` 자체가 이미 서명으로 무변경을 판정하므로 두 번째 판정이다.
- 제안:
  - `_reload(head=None)` 도우미 하나로 7곳을 바꾼다.
  - `process_controls`의 적재·비교는 `self._save()` 한 줄로 바꾼다.
- 동작: 보존 — 불필요한 커밋 1건이 사라진다. 게시되는 내용의 보장은 같다.
- 실익:
  - 약 20행이 줄어든다.
  - 게시 확인을 잃은 복구 뒤의 불필요한 후보 검증 1회와 커밋 1개가 사라진다.
  - 제어 처리마다 하던 상태 전체 deepcopy와 깊은 비교 1회가 사라진다.
- 위험과 보호:
  - `_save`의 사전 정규화(879-894)가 `process_controls`에서 더 일찍 게시될 수 있다.
  - 덮는 테스트는 `tests/test_native_final_submission.py::test_lost_cas_acknowledgment_resolves_one_native_capture`, `tests/test_controls.py`다.
- 확신: 높음 — 누락을 원문으로 확인했다.
- 다른 영역: 없음

#### ENG-15: 실행 산출의 보존 조립이 정상 종료, 실행기 소실 복구, 소유자 오류 중단의 세 경로에 따로 있다
- 유형: 이음새중복
- 위치:
  - `DM/scripts/do_math/engine.py:3659-3692`(정상 종료)
  - `DM/scripts/do_math/engine.py:1736-1765`(소실 복구)
  - `DM/scripts/do_math/scheduler.py:107-152`(`_abort_parallel_calls`)
- 현상:
  - 작업 공간 파일과 `.control` 파일을 수집하고 `files/`, `control/` 참조를 만든다. 각 파일의 sha256과 크기 행을 만들고, 체크포인트를 보존한다. 이 절차가 두 곳에 거의 같게 쓰여 있다.
  - 복구 경로에는 `output-manifest.json`, `omitted.json`, 공급자 증거 보존이 없다.
  - 복구 경로는 1751과 1764에서 같은 체크포인트 참조를 두 번 쓴다.
- 제안:
  - `_preserve_outputs(execution_id, workspace, bundle, *, max_bytes, evidence_dir=None)`가 `(artifacts, output_files, checkpoint, complete)`를 돌려주게 한다. 두 경로가 이것을 쓴다.
  - 복구 경로에도 산출 manifest를 남길지는 선택 사항이다. 남기면 동작 변경이다.
- 동작: 보존(도우미화만 할 경우)
- 실익:
  - 약 30행이 줄어든다.
  - 보존 규칙(수집 제외, 한도)을 바꿀 때 두 경로가 어긋나는 일이 사라진다.
- 위험과 보호: 덮는 테스트는 `tests/test_checkpoint_persistence.py`, `tests/test_machine_parallel.py::test_owner_exception_stops_worker_preserves_result_and_reconciles_capacity`, `tests/test_research_recovery.py`다.
- 확신: 높음
- 다른 영역: 없음

#### ENG-16: 역할별 문맥이 `engine._context`와 `context_store.prepare_role_input` 두 단계에서 만들어지며, 엔진이 만든 값 일부가 버려지거나 다시 계산된다
- 유형: 이음새중복, 운영비용
- 위치:
  - `config`: `DM/scripts/do_math/engine.py:2150` → `DM/scripts/do_math/context_store.py:447-449`
  - `pending_revisions`: `DM/scripts/do_math/engine.py:2152` → `DM/scripts/do_math/context_store.py:544-554`
  - `ready_task_ids`: `DM/scripts/do_math/engine.py:2151`(`planning.py:254-256`)과 `:1881-1882`
  - `resources`: `DM/scripts/do_math/engine.py:1887`, `:2149`
  - 분기 정리: `DM/scripts/do_math/engine.py:1892-1897`, `:1966-1970`
  - deepcopy: `DM/scripts/do_math/governance_engine.py:134`, `DM/scripts/do_math/context_store.py:425`, `:597`
- 현상: 두 단계가 같은 값을 따로 다루면서 다음 낭비가 생긴다.
  - (a) 엔진은 계획·준비에 설정 전체를 deepcopy해 `config`로 넣는다. `prepare_role_input`은 이것을 버리고 `instance['config']`에서 `configuration_source`를 새로 만든다.
  - (b) 엔진은 계획·준비에 `pending_revisions`를 계산한다. 후보 준비에서는 `prepare_role_input`이 같은 함수로 다시 계산해 덮어쓴다.
  - (c) 계획·준비의 `ready_task_ids`는 모든 과제에 `task_ready`를 다시 실행한다(`planning.ready_task_ids`). 그런데 같은 함수 안에서 같은 `evaluation_context`로 `task_readiness`가 모든 과제에 이미 계산돼 있다. 두 계산 사이에 상태를 바꾸는 호출은 없다.
  - (d) `_session_resources()`가 계획·준비에서 두 번 호출된다.
  - (e) 같은 조건의 `if` 블록이 나란히 두 번 있다(research_plan 1892/1895, identity_review 1968/1970).
  - (f) `_governance_context`가 완성된 문맥 전체를 deepcopy한다. `prepare_role_input`이 곧바로 다시 deepcopy하고(425), 검증 문맥을 위해 한 번 더 한다(597). 역할마다 문맥 전체가 세 번 복사된다.
- 제안:
  - (a) `engine.py:2150`을 지우고, `context_store.py:447`의 조건을 역할 집합만으로 한다.
  - (b) 후보 준비의 `pending_revisions`는 한 곳에서 계산한다. 엔진 쪽 2152를 계획에만 남기거나, 둘 다 `prepare_role_input`으로 옮긴다.
  - (c) `ready_task_ids = sorted(t for t, r in task_readiness.items() if r["state"] == "ready")`로 바꾼다.
  - (d)(e)는 합친다.
  - (f) `_governance_context`의 deepcopy를 지운다. `prepare_role_input` 첫 줄이 이미 입력을 복사한다.
- 동작: 보존
- 실익:
  - 계획 입력 준비 1회당 `task_ready` 호출이 2N에서 N으로 준다(N은 과제 수).
  - 후보 준비 1회당 `pending_revisions` 계산 1회, 설정 deepcopy 1회, 문맥 전체 deepcopy 1회가 줄어든다(추정. 측정하지 않음).
- 위험과 보호:
  - (f)는 문맥 안의 실상태 참조가 복사 없이 `prepare_role_input`까지 가게 만든다. 해당 참조는 `relations`, `user_inputs`, `external_operations` 등(1874-1885)이다. 그 사이의 변경 호출은 `context["control_binding"]` 대입뿐이다(3362).
  - 덮는 테스트는 `tests/test_purpose_engine.py`, `tests/test_redesign_EVIDENCE.py`, `tests/test_preparation_cache.py`(`ready_task_ids`, 계획 입력)다.
- 확신: 높음 — (a)~(e)는 원문으로 확인했다. (f)는 중간이다.
- 다른 영역: `context_store.py`, `governance_engine.py`

#### ENG-17: 역할 입력에 소비자가 없는 필드와 같은 대상을 두 번 투영한 필드가 있다
- 유형: 불필요기능, 운영비용(프롬프트 크기)
- 위치:
  - `repetition_lineages`: `DM/scripts/do_math/engine.py:1954`(`task_contracts.py:251-276`)
  - `execution_limits`: `DM/scripts/do_math/engine.py:1898-1899`, `:1959`
  - `blocked_actions` 대 `ongoing_work`의 대기 절반: `DM/scripts/do_math/engine.py:2124-2127`, `:2154-2157` 대 `DM/scripts/do_math/context_store.py:514-522`
  - `ongoing_preparation` 대 `ongoing_work`의 실행 절반: `DM/scripts/do_math/engine.py:2159-2169` 대 `DM/scripts/do_math/context_store.py:504-513`
  - `task_readiness` 전 역할 지급: `DM/scripts/do_math/engine.py:1881-1882`
  - 직접 입력 표: `DM/scripts/do_math/context_store.py:382-391`
- 현상: L-0020은 "역할 계약에 필드명이 없다는 것만으로는 미사용의 근거가 되지 못한다"고 경고한다. 그래서 문서와 코드 소비자를 모두 대조했다.
  - (a) **소비자가 없는 필드.** `repetition_lineages`와 `execution_limits`는 역할 계약, references, SKILL.md, GLOSSARY.md 어디에도 이름이 없다. `submission.py`를 포함한 코드 어디에서도 읽지 않는다. 검색식: `grep -rl` 문서, `grep -n "[\"']repetition_lineages[\"']\|[\"']execution_limits[\"']" *.py`.
    - `repetition_lineages`는 반복 계보마다 `task_repetition` 이력 행 전체의 사본을 싣는다(`task_contracts.py:273-274`). 그래서 연구가 진행될수록 모든 역할의 입력이 커진다.
    - 운영 점검 계약이 읽는 것은 `repetition_holds`(1955, `계약/운영-점검.md:79`)다.
  - (b) **대기 행동의 이중 투영.** 후보 준비의 직접 입력에는 `blocked_actions`와 `ongoing_work`가 모두 들어 있다. 두 목록 모두 `waiting_actions` 전건을 거의 같은 필드로 투영한다. 공통-실행.md:27은 `blocked_actions`를 "아직 해소하지 못한 행동별 실패 요지"라고 설명하지만, 코드는 실패로 거르지 않고 전건을 담는다.
  - (c) **준비 실행의 이중 투영.** 계획의 직접 입력에는 `ongoing_preparation`과 `ongoing_work`가 모두 있다. 둘 다 미종결 후보 준비 실행을 싣는다.
  - (d) **`task_readiness`의 전 역할 지급.** 모든 과제의 `task_readiness`는 모든 역할의 입력 준비에서 계산된다. 이것을 명시한 계약은 `계약/연구-계획.md`, `계약/연구-수행.md`, `references/CLI-실행-계약.md`다.
- 제안:
  - (a) 두 필드를 문맥에서 뺀다.
  - (b) `blocked_actions`는 `submission.py`의 `action_resolutions` 검사가 소비하므로 남긴다. `ongoing_work`는 대기 절반 대신 `blocked_actions`의 `action_id`를 참조하게 한다. 또는 `blocked_actions`를 문서대로 실패 종류로 거른다.
  - (c) `ongoing_preparation`의 추가 필드(`revision_targets`, 판본, 평가 대상)를 `ongoing_work`의 준비 실행 행에 싣고 `ongoing_preparation`을 없앤다. 공통-실행.md:29, :31을 함께 고친다.
  - (d) `task_readiness`는 계획·연구 수행·보충 조사에만 계산해 준다.
  - 각 항목은 채택 여부를 따로 정할 수 있다.
- 동작: 변경 — 역할 프롬프트의 내용이 줄거나 합쳐진다. (b)(c)는 계약 문서의 문장도 바뀐다.
- 실익:
  - 모든 역할 입력에서 반복 이력 사본과 실행 한도가 빠진다. 크기는 이력에 비례하며 측정하지 않았다.
  - 준비·계획 입력에서 대기 행동과 준비 실행이 한 번씩만 실린다.
  - 계획·수행이 아닌 역할의 입력 준비마다 `task_ready` N회가 사라진다(추정).
- 위험과 보호:
  - 모델이 이 필드를 실제로 읽고 있었는지는 문서 대조만으로 증명할 수 없다.
  - (d)는 `task_readiness`를 언급하는 계약이 있는 역할을 빠짐없이 골라야 한다.
  - 필드 부재를 단언하는 테스트는 없다. 덮는 테스트는 `tests/test_redesign_SURFACE.py`, `tests/test_purpose_engine.py`(역할 입력)이며 간접적이다.
- 확신: 중간 — 소비자 부재는 grep으로 확인했다. 모델 쪽 효과는 미확인이다.
- 다른 영역: `context_store.py`, `DM/references/공통-실행.md`, `DM/계약/연구-계획.md`, `DM/계약/후보-준비.md`

#### ENG-18: 과거 입력 snapshot을 읽기만 하려고 상태 전체를 deepcopy해 여러 번 적재한다
- 유형: 운영비용
- 위치:
  - `DM/scripts/do_math/engine.py:2266`, `:3857`, `:3936`, `:4019`, `:4452`, `:4510`
  - `DM/scripts/do_math/scheduler.py:434`
  - 적재 구현: `DM/scripts/do_math/repository.py:208-211`
- 현상:
  - `store.load(snapshot)`은 캐시된 문서를 매번 deepcopy해 돌려준다.
  - 연구 계획의 수락 한 번에 같은 `input_snapshot`을 여러 번 적재한다. 적재 지점은 `_validate_bundle_current`(2266, 묶음마다), `_apply_plan`(4510), `_apply_extensions`의 과제 철회(3857), `_apply_queue_plan`(scheduler 434)이다.
  - 모든 호출자는 `tasks`, `active_trust_environment`, `executions`와 queue 같은 일부만 읽고 고치지 않는다.
- 제안:
  - 저장소에 읽기 전용 조회 `store.view(snapshot)`를 둔다. 이 조회는 복사하지 않은 캐시 문서를 돌려주고, 호출자는 고치지 않는다는 규약을 따른다.
  - 위 7곳이 이 조회를 쓴다.
- 동작: 보존
- 실익: 계획 수락 1회당 상태 전체 deepcopy 3~4회(묶음 수에 따라 더)가 줄어든다. 크기와 시간은 추정이며 측정하지 않았다.
- 위험과 보호:
  - 호출자가 반환값을 고치면 공유 캐시가 오염된다. `apply_task_dispositions`, `task_scope.apply_task_assessments`가 `input_tasks`를 고치지 않는지 확인해야 한다(미확인).
  - 덮는 테스트는 `tests/test_redesign_TASKS.py`, `tests/test_purpose_engine.py`(계획 수락)다.
- 확신: 중간
- 다른 영역: `repository.py`(상태 저장소 소유자), `task_scope.py`

#### ENG-19: 한 실행의 프롬프트와 역할 문서가 두 묶음에 두 번 보존되고, 프롬프트 해시도 두 곳에 기록된다
- 유형: 이음새중복, 파생상태
- 위치:
  - 엔진 사본: `DM/scripts/do_math/engine.py:842-851`(`{input_bundle}/input.txt`, `{input_bundle}/input/implementation/*`)
  - manifest 사본: `DM/scripts/do_math/context_store.py:704-708`(`{execution_id}/input/documents/{i}.txt`, `{execution_id}/input/prompt.txt`)
  - 해시: `DM/scripts/do_math/engine.py:3480`(`input_sha256`)과 `DM/scripts/do_math/context_store.py:687`(`manifest.prompt.sha256`), 문서 해시 재계산 `DM/scripts/do_math/context_store.py:685-686`
  - 검사: `DM/scripts/do_math/engine.py:4766-4776`, `:4788-4795`와 `DM/scripts/do_math/context_store.py:785-797`
  - 문서: `DM/references/공통-실행.md:15`
- 현상:
  - 같은 프롬프트 바이트와 같은 역할 문서가 입력 묶음과 manifest 접두어 양쪽에 저장된다.
  - `input_sha256`은 `manifest.prompt.sha256`과 같은 값이다.
  - 엔진은 문서의 `sha256`을 이미 갖고 있다(1794). 그런데 context_store는 실행마다 모든 역할 문서를 다시 해시한다.
  - 검사도 두 갈래다. `check`/`_inspect_before_write`는 `input.txt`를 보고, `verify_manifest_artifacts`는 manifest 사본을 본다.
  - Git은 같은 blob을 한 번만 저장하므로 저장 공간의 비용은 작다. 늘어나는 것은 트리 항목, 게시 때의 해시, 검사 경로다.
- 제안:
  - manifest 사본만 남긴다.
  - `input_sha256`은 `manifest.prompt.sha256`에서 가져오거나 필드를 없앤다.
  - `check`는 manifest 검사를 쓴다.
  - context_store는 `doc['sha256']`을 재사용한다.
  - 공통-실행.md:15의 "사본으로도 저장" 문장을 고친다.
- 동작: 변경 — 입력 묶음의 저장 배치와 문서 설명이 바뀐다.
- 실익:
  - 실행 1회당 artifact 항목 약 (문서 수+1)개가 줄고, 역할 문서 전체의 SHA-256 1회가 줄어든다.
  - 입력 무결성 검사가 한 갈래가 된다.
- 위험과 보호:
  - `input.txt`와 `input_sha256`의 소비자가 여럿이다: `model_runner.py:343`, `review_cycle.py:228`, `engine.py:3537`, `:2140`.
  - 덮는 테스트는 `tests/test_formal_input_manifest.py`, `tests/test_redesign_STORAGE.py`, `tests/test_performance_repairs.py`(input.txt 사용)다.
- 확신: 중간 — 중복은 확실하다. 소비자 이전의 범위가 넓다.
- 다른 영역: `context_store.py`, `model_runner.py`, `review_cycle.py`, `references/공통-실행.md`

#### ENG-20: `engine_sha256`은 기록만 되고 읽히지 않으며, 엔진 파일 하나만 식별한다
- 유형: 불필요기능
- 위치:
  - `DM/scripts/do_math/engine.py:88`, `:2466`, `:3483`, `:4591`
  - `DM/scripts/do_math/record_schemas/schemas.py:108`
  - 설치본 식별: `DM/scripts/do_math/engine.py:616-629`, `:1624-1629`
- 현상:
  - 모듈을 적재할 때 `engine.py`를 읽어 해시하고, 모든 AI·형식 실행에 `engine_sha256`으로 기록한다.
  - 이 필드를 읽는 코드는 없다. 검색식: `grep -rn "engine_sha256" --include=*.py .`
  - 설치본 전체의 식별은 `runtime.installation`과 `implementation_history`가 이미 기록한다.
  - `:2466`의 `ENGINE_SHA256` 대체값은 `submission_contract`가 없는 문맥에서만 쓰인다. 그런데 실행 준비는 늘 `install_submission_tools=True`로 이 항목을 만든다(`engine.py:3370`, `context_store.py:617-622`).
- 제안:
  - 새 실행에 `engine_sha256` 기록을 멈춘다. 스키마 필드는 기존 상태 호환을 위해 선택으로 남긴다.
  - `:2466`의 대체값은 지운다. 필요하면 `KeyError`로 실패하게 한다.
  - 식별이 필요하면 실행에 `installation.sha256`을 기록한다.
- 동작: 변경 — 새 실행 기록에서 필드가 빠진다.
- 실익:
  - 모듈을 적재할 때 약 200KB 해시 1회가 사라진다.
  - 의미가 좁은 식별자가 사라진다.
- 위험과 보호: `engine_sha256`을 단언하는 테스트는 찾지 못했다. 보호하는 테스트는 `없음`이다.
- 확신: 중간 — 코드 소비자 부재는 확인했다. 외부 분석 도구가 읽는지는 미확인이다.
- 다른 영역: `record_schemas`

#### ENG-21: 스케줄러와 병렬 호출기의 국소 중복과 죽은 인자
- 유형: 복잡성, 죽은코드
- 위치:
  - `DM/scripts/do_math/scheduler.py:519-528`과 `:539-544`(같은 수용 판정 블록), `:523`, `:539`(이미 `:10`에서 import한 `SessionSlots`를 다시 import), `:534`, `:540`(프로필 계산 분기)
  - `DM/scripts/do_math/parallel.py:57-58`(`start` 포장, 유일 호출자 `scheduler.py:628`), `:41`, `:149`, `:209`(이벤트 튜플의 항상 `None`인 넷째 원소)
- 현상:
  - `_dispatchable`에서 기계 역할과 AI 역할의 끝부분이 같은 `SessionSlots(... observer=True).admission_check(profile)` 블록을 반복한다.
  - 534행의 `profile_ref`가 있으면 `None`으로 둔다. 그러나 540행이 결국 다시 계산하므로, 이 조건 분기는 효과가 없다.
  - `ModelCalls.start`는 `runner.run`을 넘기는 한 줄짜리 포장이다.
- 제안:
  - 수용 판정을 도우미 하나로 만든다.
  - 지역 import를 지운다.
  - 프로필은 한 번 계산한다.
  - `start`를 지우고 호출자가 `start_call(generator, self.runner.run, ...)`을 부르게 한다.
  - 튜플을 3원소로 줄인다.
- 동작: 보존
- 실익: 약 15행이 줄어든다.
- 위험과 보호: 덮는 테스트는 `tests/test_machine_parallel.py`(`test_close_sets_every_stop_flag_and_fails_pending_start_callbacks`, `test_observations_queue_without_waiting_and_apply_before_collection`)다.
- 확신: 높음
- 다른 영역: 없음

#### ENG-22: 엔진 안의 한 곳짜리 포장 함수와 반복 투영
- 유형: 복잡성
- 위치:
  - `_read_extensions`: `DM/scripts/do_math/engine.py:2877-2878`(유일 호출자 `:2457`)
  - 사용자 제어 요청 찾기(4곳): `:257-259`, `:1489-1490`, `:2097-2098`, `:4186-4187`
  - 미종결 실행의 action ID 집합(6곳 이상): `:1893`, `:3802`, `:4094`, `DM/scripts/do_math/scheduler.py:313`, `:435-437`, `DM/scripts/do_math/lifecycle_engine.py:914-915`
  - `lambda snapshot, path: self.store.read(path, snapshot)`(7곳): `:1207`, `:1216`, `:1663`, `:1941`, `:2256`, `:2313`, `:2453`
  - 형식 검사: `:4638`과 `:4648`(같은 `reference`를 두 번 대입), `:4642`와 `:4655`/`:4700`(같은 `proposal.lean`을 두 묶음에 저장)
- 현상:
  - `_read_extensions`는 `submission.read_extensions`를 그대로 넘긴다. 테스트에서 이 함수를 교체하는 곳도 없다(`grep -rn "_read_extensions"`).
  - 나머지는 같은 식이 곳곳에서 반복된다.
- 제안:
  - `_read_extensions`를 지운다.
  - `_user_control_request(request_id)`, `_live_action_ids()`, `_read_at`(바운드 메서드) 도우미를 둔다.
  - 형식 검사 원문은 원 반환 묶음 한 곳에만 저장한다.
- 동작: 보존
- 실익: 약 25행이 줄어든다.
- 위험과 보호: 덮는 테스트는 `tests/test_connection_repairs.py`, `tests/test_knowledge_import_engine.py`(형식 검사 경로)다.
- 확신: 높음
- 다른 영역: `lifecycle_engine.py`(live ID 집합)

#### ENG-23: 보존 정리의 참조 추출 규칙이 retention 모듈이 아니라 엔진에 있다
- 유형: 이음새중복(규칙의 소유 위치)
- 위치:
  - `DM/scripts/do_math/engine.py:4197-4241`(`_retention_state`)
  - 소비자: `DM/scripts/do_math/retention.py:132-143`, `:221-239`
  - 비교: `DM/scripts/do_math/relation_refs.py:4-16`
- 현상:
  - 어느 필드가 참조인지(`reference_keys` 19개와 예외 규칙)를 엔진이 정의한다. 이 결과를 쓰는 곳은 retention의 폐포 계산뿐이다.
  - 관계 참조의 정본인 `relation_refs.py`는 `formal_result_refs`, `assessment_refs`를 참조로 본다. 엔진의 목록에는 이 둘이 없다.
  - 다만 연구 루트의 기록은 모두 보호 대상이므로(4236-4237), 이 누락이 실제 삭제로 이어지는지는 확인되지 않았다.
- 제안:
  - 참조 추출(`references`)과 기록 색인 구성을 `retention.py`의 `retention_inputs(instance, runtime, rows)`로 옮긴다.
  - 관계 참조는 `relation_refs`를 재사용한다.
  - 엔진은 범위 확인(`_cleanup_scope`)과 호출만 한다.
- 동작: 보존
- 실익:
  - 엔진 약 40행이 retention으로 옮겨진다.
  - 참조 필드 목록이 관계 정본과 어긋나는 경로가 줄어든다.
- 위험과 보호: 덮는 테스트는 `tests/test_redesign_STORAGE.py::test_cleanup_scope_preserves_exact_user_request_and_execution_references`, `tests/test_completion_settlement.py`다.
- 확신: 중간
- 다른 영역: `retention.py`, `relation_refs.py`

#### ENG-24: 착수 가능 판정이 같은 소유 루프 안에서 서로 다른 입력 투영으로 반복된다
- 유형: 운영비용, 기타(같은 판정의 두 입력)
- 위치:
  - `DM/scripts/do_math/scheduler.py:491-501`(`governance_working_view(self.instance)` 사용)
  - `DM/scripts/do_math/engine.py:3313-3315`, `:1050`, `:1881`(원 `self.instance` 사용)
  - `DM/scripts/do_math/planning.py:176-180`(`governance_revisions`는 호출자의 투영을 쓰지 않는다)
  - 소유 루프 주기: `DM/scripts/do_math/scheduler.py:18`, `:614-615`
- 현상:
  - `_dispatchable`은 대기열의 연구 수행 요청마다 `task_ready`를 실행한다. 소유 루프는 최대 0.25초 간격으로 돈다. 따라서 준비되지 않은 요청이 대기열 앞쪽에 남아 있으면 회차마다 같은 판정이 되풀이된다.
  - 같은 술어를 스케줄러는 거버넌스 투영을 덧씌운 인스턴스로, 엔진은 원 인스턴스로 부른다.
  - `task_ready`가 목표·정책 판본을 `governance_view`로 직접 읽는 것은 확인했다(`planning.py:176-180`). 그러나 투영의 다른 필드(`goal`, `policies`)에 의존하는 하위 호출이 있는지는 확인하지 않았다.
- 제안:
  - (1) 두 호출이 같은 입력을 쓰도록 통일한다. 투영이 필요 없으면 원 인스턴스를 쓴다.
  - (2) 시간 조건이 없는 판정 결과를 `(head, task_id, action_id)`로 메모하는 방안을 검토한다. 이 메모는 이음새 계약 S4의 head 키 메모 규칙을 따른다.
  - 단, 판정은 `lifecycle_now`에 의존할 수 있으므로 (2)는 측정 뒤에 결정한다.
- 동작: 보존((1)이 동등함이 확인될 경우)
- 실익: 대기 중 소유 루프의 CPU가 줄어든다. 측정하지 않은 추정이다.
- 위험과 보호: 덮는 테스트는 `tests/test_efficiency.py::test_readiness_is_derived_and_changes_with_contract_review_evidence`다.
- 확신: 낮음 — 입력 투영의 동등성과 실제 비용을 확인하지 않았다.
- 다른 영역: `planning.py`, `lifecycle_engine.py`(`_refresh_readiness`)

## 3. 보존 판정

- **`_controls`의 원자료 재검사** (`DM/scripts/do_math/engine.py:956-966`)
  - 겉보기 문제: CLI가 이미 검사한 조건을 엔진이 다시 검사한다.
  - 유지 이유: inbox는 디스크에 있는 기존 기록이라 신뢰 경계 밖이다. 코드만 ENG-11로 합치고 검사는 남긴다.
- **실행 준비 직후 작업 공간의 `context.json`을 다시 읽는 처리** (`DM/scripts/do_math/engine.py:3374`)
  - 겉보기 문제: `fitted["validation_context"]`가 메모리에 있는데 디스크에서 다시 읽는다.
  - 유지 이유: 작업자가 읽는 바이트와 엔진이 이후 판단에 쓰는 문맥의 동일성을 보장한다. 이것은 판정한 입력과 게시한 입력의 동일성에 해당한다.
- **native 포착 때 고정 입력과의 대조** (`DM/scripts/do_math/engine.py:3132-3136`)
  - 겉보기 문제: 같은 프로세스가 준 문맥을 다시 비교한다.
  - 유지 이유: 수신 검사가 실제로 발급한 입력에 대해 이루어졌음을 보장한다. ENG-08의 도우미로 읽기만 합친다.
- **워커 모듈의 effort 값 집합** (`DM/scripts/do_math/codex_worker.py:28`, `DM/scripts/do_math/claude_worker.py:41`)
  - 겉보기 문제: 엔진의 집합(`engine.py:173`, `:178`)과 중복이다.
  - 유지 이유: 워커는 패키지 없이 Job 안에서 적재된다(이음새 계약 2.1). 또 Claude 집합은 공급자별로 실제로 다르다. 엔진 쪽 두 집합만 ENG-12에서 합친다.
- **`governance.WORK_ROLES`** (`DM/scripts/do_math/governance.py:18`)
  - 겉보기 문제: scheduler의 `WORK_ROLES`와 이름이 같다.
  - 유지 이유: `formal_check`를 포함하는 다른 개념이다. 합치면 무관한 두 개념이 한 정의에 묶인다. 이름만 바꾼다(ENG-01).
- **`blocked_actions` 자체** (`DM/scripts/do_math/engine.py:2116-2127`, `:2154-2157`)
  - 겉보기 문제: `ongoing_work`와 겹친다(ENG-17).
  - 유지 이유: `submission.py`의 `action_resolutions` 검사가 이 목록을 수신 판정에 쓴다. 겹치는 쪽을 줄이되 이 목록은 남긴다.
- **`ModelCalls`의 호출별 스레드** (`DM/scripts/do_math/parallel.py:60-95`)
  - 겉보기 문제: 표준 `ThreadPoolExecutor`로 바꿀 수 있어 보인다.
  - 유지 이유: 호출별 정지 플래그, 소유 스레드의 콜백 왕복, 관찰 큐가 필요하다. 동시성의 상한은 세션 슬롯이 정하므로 고정 크기 풀은 호출을 줄 세워 의미를 바꾼다.
- **게시 확인을 잃은 뒤 저장 상태에서 영수증을 찾는 복구** (`DM/scripts/do_math/engine.py:1360-1375`, `:3155-3166`)
  - 겉보기 문제: 두 곳에 비슷한 예외 처리가 있다.
  - 유지 이유: 커밋은 됐으나 확인을 잃은 경우를 해소하는 필수 보장이다. 재적재 부분만 ENG-14로 합친다.
- **`_sealed_bytes`, `_state_signature`, `_check_installation`/`_installation_manifest`, `_goal_basis_key_at_head`, 정지 판정 콜백(`should_stop`, `stop`)**
  - 겉보기 문제: 반복 해시, 반복 판정.
  - 유지 이유: 직전 라운드(8d2ffd0)가 다룬 결과 캐시, 재해시, 상태 검증, 취소 콜백의 구현이다. 기준 문서가 재제안을 금지한다. 이음새 중복은 새로 발견되지 않았다.

## 4. 후보 없음

- `parallel.py`의 `judge`, `pump`, `collect`, `close` 흐름(ENG-06, ENG-21을 제외한 부분). 소유 스레드 직렬화의 불변식을 지키는 최소 구성으로 판단했다.
- `query_records`, `read_record`, `_record_evidence`, `_query_record`(`engine.py:492-567`). 커서와 증거 형식이 한 곳에 있다.
- `_enqueue`의 병합 규칙(`engine.py:3794-3847`). L-0020이 기록한 병합 결함들의 수리 결과이며, 비교 키는 `_dispatchable`의 식별 키(`scheduler.py:510`)와 목적이 다르다.
- `_apply`의 역할 분기(`engine.py:4000-4181`), `_complete_operational_disposition`(`engine.py:4385-4464`), `_submission_check_summary`(`engine.py:4712-4751`), `check`(`engine.py:4778-4817`).
- `scheduler.py`의 `_schedule_reconsideration`, `_ensure_model_assessments`, `_finish_assessment_preparation`, `_apply_queue_plan`(ENG-18의 적재를 제외한 부분).

## 5. 미완료

- 모든 실익은 추정이다. 테스트와 측정은 기준 문서의 금지에 따라 실행하지 않았다.
- ENG-05에서 lifecycle_engine의 여섯 손 쓰기 각각 뒤에 `_save`가 오는지 원문으로 확인하지 않았다.
- ENG-09에서 종료 뒤 `_drain_review_observations`가 묶음 수집 뒤에도 필요한지 확인하지 않았다.
- ENG-18에서 `apply_task_dispositions`, `apply_task_assessments`가 입력 과제를 고치지 않는지 확인하지 않았다.
- ENG-24에서 `governance_working_view` 투영과 원 인스턴스의 판정 동등성, 그리고 소유 루프의 실제 판정 비용을 확인하지 않았다.
- 믹스인 모듈(`review_engine.py`, `lifecycle_engine.py`, `governance_engine.py`, `provider_engine.py`, `decision_engine.py`, `revision_engine.py`, `question_engine.py`, `academic_engine.py`)은 다른 영역이다. 엔진 이음새가 닿는 줄만 읽었다. 그 모듈들이 `_context`에 더하는 역할별 입력(`_prepare_review_context`, `_review_research_context` 등)과 역할 계약의 대응은 검사하지 않았다.

## 6. 작업 중 사건

- `references/공통-실행.md`는 첫 읽기에서 219행까지만 표시돼, 나머지(220-345)를 이어서 읽었다.
- 러너 가짜 객체의 `**kwargs` 유무를 처음에는 한 줄 grep으로 셌고, 2개가 없다는 잘못된 결과를 얻었다. 여러 줄에 걸친 시그니처를 원문으로 확인해 13개 모두 가변 키워드를 가진다고 정정했다(ENG-07).
- ENG-03은 처음에는 `available_input_refs`의 파생 저장(ENG-04)만 볼 생각이었다. 작성자를 전수로 찾다가 lifecycle_engine의 덧붙이기가 덮어써진다는 사실을 발견했다.
- ENG-02는 `_apply`의 입력 검사를 따라가다가 제출 검사와 착수 판정의 규칙을 대조하면서 발견했다. 예상과 달리 엔진 적용이 셋 가운데 가장 좁은 규칙이었다.

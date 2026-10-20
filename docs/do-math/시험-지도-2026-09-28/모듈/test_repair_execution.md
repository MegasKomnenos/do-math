# test_repair_execution

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_repair_execution.py` (212행) |
| 클래스 / 테스트 | 3 / 11 |
| 시험 대상 제품 코드 | `do_math/repair_execution.py`의 `installation_sha256`, `pending_installation_repair`, `installation_failure`, `resume_installation_repair`, `RepairExecutionMixin.route_submission_return`, `route_failed_action`, `complete_repair`, `request_installation_repair`; `do_math/engine.py`의 `ResearchEngine._complete_operational_disposition`; `do_math/operational_dispositions.py`의 `reconcile_recovery`; `do_math/scheduler.py`의 `_run_parallel`; `do_math/scheduled_operator.py`의 `engine_start_guard`, `check`, `hold` |
| 사용하는 픽스처 모듈 | `engine_fixtures`: `start_repair_host`; `record_fixtures`: `installation_repair_state`; `research_fixtures`: `bare_engine` |
| 격리 표지 | 없음 |
| 시작 상태 | `RepairExecutionTests`는 실제 Git 저장소 위의 `bare_engine`(`start_repair_host`). 나머지는 1단(순수 함수나 손으로 만든 런타임 사전, 대역으로 둘러싼 `bare_engine`) |

## 목적

모듈 docstring은 "Repair execution: the installation repair handoff and its routing, and retries of ended attempts over real Git."이다. 제품 `repair_execution.py`의 docstring은 "Preserve failed submissions and route accepted installation repairs."다. 이 모듈은 수리 실행의 세 부분을 검사한다.

1. 끝난 시도의 운영 재시도와 설치 수리 인계(`RepairExecutionTests`). 실제 Git 저장소에 게시하고 다시 읽는다.
2. 설치 정체성(`InstallationIdentityTests`). 설치된 스킬 전체를 해시하되 시험 폴더는 뺀다.
3. 설치 수리의 경로 배정(`InstallationRepairRoutingTests`). 생산자 수리 한도를 넘은 제출 반환은 진단을 한 번 연다. 설치 수리 요청은 받아들여진 진단을 요구한다. 설치 수리가 걸려 있는 동안 스케줄러는 새 일을 배정하지 않고 엔진 시작도 막는다. 감독자는 진단을 읽기만 하는 탐침과 실제 회복 경로를 구별한다. 수리 뒤의 재개는 거부된 최신 묶음과 수리 횟수를 이어받는다.

## 모듈 수준 요소

- 행 9: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 넣는다.
- 행 17 `AT`: `"2026-09-20T00:00:00Z"`. 첫 시험에서 새 실행 `EX-next`의 생성 시각으로 쓴다.
- 행 211–212: 직접 실행하면 `unittest.main()`을 부른다.

## RepairExecutionTests (행 20–60)

`unittest.TestCase`를 그대로 상속한다. 표지와 클래스 속성이 없다.

- `setUp` (행 39–40): 두 시험 메서드 사이에 정의되어 있다. `engine_fixtures.start_repair_host(self)`를 부른다. 이 픽스처는 임시 폴더에 `git_init`으로 실제 Git 저장소를 만들고, 그 위의 `ResearchRepository`를 저장소로 가진 `bare_engine`을 `self.host`로 둔다. 상태는 `current_state`에 `research_work`, `operational_review` 두 역할의 프로필만 둔 것이다. `EX-target`(research_work, 활동 `AY-target`)과 `EX-review`(operational_review, 활동 `AY-review`)는 모두 `cancelled`로 끝나 있다. 검토의 처분 `OD-repair`는 `kind="retry"`, `status="pending"`으로 대상의 미완 활동을 새 작업 공간에서 다시 시도하자는 것이다. 대상의 봉인 입력은 묶음 `BA-target` 아래 `input/catalog/tasks.json`에 있다(`self.source`). 작업 공간의 사본 `self.destination`은 `b"damaged"`로 손상되어 있다. 픽스처는 저장소를 초기화하고, 봉인 입력과 manifest를 함께 게시한다.

### `test_operational_retry_of_an_ended_attempt_keeps_its_registered_successor` (행 21–37)
- 성질: 끝난 시도에 이미 등록된 후속 실행이 있으면, 운영 재시도 처분은 새 후속을 만들지 않고 `superseded`로 정산된다. 그 결과와 후속의 계보가 저장소에 남는다.
- 준비: `setUp`의 저장소 상태. `execution_lifecycle.create_execution`으로 `EX-next`를 만든다. 소유 활동은 `EX-target`과 같고, `created_at=AT`, `role`과 `action`은 대상의 것을 따르며, `continuation_of='EX-target'`다. `activities.assign_execution`으로 활동에 배정하고 `host._save()`로 게시한다.
- 실행: `ResearchEngine._complete_operational_disposition(host, record)`(`record`는 `OD-repair`). 이어서 `host._save()`와 `host.store.load()`.
- 단언: 반환 기록의 `status == 'superseded'`다. 대기열이 비어 있다. 저장소에서 다시 읽은 `operational_dispositions['OD-repair']['status'] == 'superseded'`이고, `executions['EX-next']['continuation_of'] == 'EX-target'`이다.
- 대역: 없음. 저장소는 실제 Git이다.
- 비고: 제품의 `reconcile_recovery`(operational_dispositions.py 행 81–99)가 처리한다. docstring은 "Settle an obsolete recovery proposal without duplicating its successor."다.

### `test_installation_repair_handoff_preserves_failure_and_is_idempotent` (행 42–60)
- 성질: 받아들여진 `repair` 처분은 설치 수리 대기(`installation_repair_pending`)로 인계되고, 새 행동을 대기열에 넣거나 작업 공간을 고치지 않는다. 같은 기록으로 다시 부르면 같은 결과를 돌려주고 새로 게시하지 않는다.
- 준비: `setUp`의 상태에서 `EX-target`에 `error="Installed receiver rejected valid output"`와 `result_ref=self.source`를 둔다. `OD-repair`를 `status="repair_required"`로 바꾸고, 처분을 `kind="repair"`, `repair_target="installation:scripts/do_math/engine.py"`, `meaning_preserving=True`, `next_owner="installation_recovery"`로 바꾼다. 그 뒤 `host._save()`.
- 실행: `repair_execution.installation_sha256`을 `"a" * 64`로 패치하고 `_complete_operational_disposition`을 부른다. 제품은 `complete_repair`에서 `request_installation_repair`로 간다. 대상 파일이 실제 설치본에 있는지를 `validate_installation_target`로 확인하고, 상태와 `installation_repair` 결박(해시, 증거 참조)을 기록한 뒤 저장한다. 이어서 반환된 결과 기록을 인자로 한 번 더 부른다.
- 단언: 첫 결과의 `status == "installation_repair_pending"`이다. 대기열이 비어 있다. `self.destination`의 바이트가 여전히 `b"damaged"`다. 두 번째 호출의 반환이 첫 결과와 같고, `host.head`가 바뀌지 않았다.
- 대역: `patch.object(repair_execution, "installation_sha256", return_value="a" * 64)`.
- 비고: 이름의 "preserves failure"는 작업 공간과 대기열이 그대로라는 단언으로 읽힌다. 대상 실행의 `error`와 `result_ref`가 결과에 증거 참조로 실렸는지는 단언하지 않는다. 수리 대상 경로 검사는 실제 설치본(`scripts/do_math/engine.py`)의 존재에 기대므로, 그 파일 이름이 바뀌면 이 시험이 깨진다.

## InstallationIdentityTests (행 63–75)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다.

### `test_identity_covers_the_installed_skill_but_not_its_tests` (행 64–75)
- 성질: 설치 정체성은 설치된 스킬의 모든 파일을 덮되, `scripts/tests` 아래의 시험 파일은 뺀다.
- 준비: 임시 루트에 `scripts/do_math/a.py`, `scripts/tests/test_a.py`, `examples/case.json`을 `'one'`으로 쓴다.
- 실행: `repair_execution.installation_sha256(root)`를 세 번 부른다. 처음, `test_a.py`를 `'two'`로 바꾼 뒤, `examples/case.json`을 `'two'`로 바꾼 뒤.
- 단언: 시험 파일만 바꾼 뒤의 해시는 처음과 같다. `examples/case.json`을 바꾼 뒤에는 다르다.
- 대역: 없음.
- 비고: 원문 주석(행 71)이 이유를 밝힌다: "A regression test alone does not reopen the same failure's automatic repair." 제외 규칙은 `file_io.installation_files`(file_io.py 행 378–392)에 있고, `__pycache__`, `.git`, `.lake`, `.pyc`도 뺀다. 이 시험은 그 가운데 `scripts/tests`만 확인한다.

## InstallationRepairRoutingTests (행 78–208)

클래스 docstring은 "Installation repair: routing a receiver defect to diagnosis, the repair request, and the work around it."이다. `unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다. 여러 시험이 `record_fixtures.installation_repair_state()`로 시작한다. 이 픽스처는 `(runtime, record)`를 돌려준다. 런타임에는 다음이 들어 있다.
- 활동 `AY-work`(research_plan, `waiting`).
- 오류 `'receiver contract conflict'`로 끝난 실행 `EX-failed`(research_plan).
- `output_accepted`로 끝난 진단 실행 `EX-diagnosis`(operational_review, 대상 `EX-failed`).
- 처분 `OD-repair`. `status='installation_repair_pending'`이고, `repair_target='installation:scripts/do_math/task_scope.py'`이며, 결박 `installation_sha256='a'*64`와 증거 참조를 가진다.
- `AC-work`의 대기 행. `repair_attempt=2`이고, `repair.execution_id='EX-failed'`다.

### `test_repeated_submission_return_stops_producer_and_opens_one_diagnosis` (행 81–102)
- 성질: 생산자 수리 한도 안의 제출 반환은 재시도로 다시 대기열에 넣는다. 한도를 넘으면 생산자를 멈추고 운영 진단을 한 번 연다. 진단 자신의 실패는 다시 진단을 열지 않는다. 한도가 0이면 첫 반환부터 대기로 간다.
- 준비: `bare_engine({'config': {'max_output_repairs': 1}}, {'queue': [], 'waiting_actions': {}})`. `_enqueue`는 호출을 목록 `opened`에 기록하는 `create_autospec` 대역이다. 생산자 행동은 `AC-producer`(research_plan)다. 수신 결과 `received`는 `retry_bundle_ids=['IN-failed']`, `bundles=[]`, `issues=[{'rule_id': 'application'}]`다.
- 실행: (1) `route_submission_return(action, received, 'EX-first', {'summary': 'preserved'})`. (2) 대기열에서 꺼낸 재시도 행동으로 `'EX-second'` 반환. (3) 역할만 `operational_review`로 바꾼 재시도로 `'EX-op'` 반환. (4) `max_output_repairs=0`으로 바꾸고 새 행동 `AC-zero`로 `'EX-zero'` 반환.
- 단언: (1) 뒤 꺼낸 재시도의 `repair_attempt == 1`. (2) 뒤 대기열이 비어 있고, `opened[0][0] == ('operational_review', 'EX-second')`다. `waiting_actions['AC-producer']`의 `action.repair.execution_id == 'EX-second'`이고, `detail.issues`가 `received['issues']`와 같다. (3) 뒤 `opened`의 길이가 여전히 1이다. 원문 주석(행 96)은 "Failed diagnostic output itself cannot open recursive diagnostics forever."라고 밝힌다. (4) 뒤 대기열이 비어 있고 `AC-zero`가 대기 행에 있다.
- 대역: `create_autospec(engine._enqueue, side_effect=...)`.
- 비고: (4)에서도 `route_failed_action`이 진단을 열어 `opened`가 2가 되지만, 이 시험은 그 수를 단언하지 않는다. 인스턴스에 `lifecycle`이 없으므로 제품은 초기화 분기(`maintenance`)가 아니라 `operational_review` 분기를 탄다.

### `test_installation_request_requires_accepted_diagnosis_and_keeps_stable_identity` (행 104–114)
- 성질: 설치 수리 요청의 실패 정체성은 받아들여진 진단을 요구한다. 수리 시도 상태가 바뀌어도 같은 실패로 남고, 실패한 실행의 계약이 바뀌면 다른 실패가 된다.
- 준비: `installation_repair_state()`.
- 실행: `installation_failure(runtime, record)`를 네 번 부른다. (1) 처음. (2) 결박에 `status='failed'`, `attempted_by='EX-repair'`를 두고 처분 상태를 `installation_repair_waiting`으로 바꾼 뒤. (3) `EX-failed`의 `contract_sha256`을 `'changed-contract'`로 바꾼 뒤. (4) 진단 실행의 `outcome`을 `execution_incomplete`로 바꾼 뒤.
- 단언: (2)의 결과가 (1)과 같다(사전 전체 등식). (3)의 `failure_sha256`은 (1)과 다르다. (4)는 `ValueError`를 던진다. 예외 유형만 보고 메시지는 보지 않는다. 제품 메시지는 `'installation repair requires a preserved accepted diagnosis of an ended failure'`다.
- 대역: 없음.

### `test_unattempted_installation_diagnosis_is_not_starved_by_an_old_wait` (행 116–122)
- 성질: 오래된 설치 수리 대기(`installation_repair_waiting`)가 있어도, 아직 시도하지 않은 대기 중 진단(`installation_repair_pending`)이 먼저 선택된다.
- 준비: `installation_repair_state()`의 처분을 `installation_repair_waiting`으로 바꾼다. 그 사본으로 `OD-fresh`(`installation_repair_pending`)를 더한다.
- 실행: `pending_installation_repair(runtime)`.
- 단언: 반환 기록의 `id == 'OD-fresh'`.
- 대역: 없음.
- 비고: 제품은 상태 순서 `('installation_repair_pending', 'installation_repair_waiting')`로 찾는다(repair_execution.py 행 18–24).

### `test_pending_installation_repair_prevents_a_redundant_engine_start` (행 124–129)
- 성질: 엔진 상태에 설치 수리가 걸려 있으면 엔진 시작 관문은 시작하지 않고 설치 수리 대기를 알린다.
- 준비: `scheduled_operator.read_status`를 `{'status': 'ready', 'installation_repair': {'id': 'OD-pending'}}`로 패치한다.
- 실행: `operator.engine_start_guard(<임시>/repo, 'RI-test', <임시>/work)`.
- 단언: `outcome == 'installation_repair_waiting'`.
- 대역: `patch.object(operator, 'read_status', return_value=...)`.
- 비고: 작업 공간에 `HOLD.json`이 없으므로 보류 분기는 타지 않는다.

### `test_scheduler_drains_existing_calls_without_dispatching_new_work_during_installation_repair` (행 131–150)
- 성질: 설치 수리가 걸려 있는 동안 스케줄러 루프는 이미 진행 중인 호출만 거두고, 새 일은 배정하지 않는다. 끝나면 상태를 `waiting`으로 둔다.
- 준비: `installation_repair_state()`의 대기열을 `[{'id': 'AC-independent', 'role': 'research_work'}]`로 바꾼다. `ModelCalls`는 `create_autospec(..., instance=True)` 대역이다. 진행 중 호출 `futures={'existing': object()}`를 두고, `collect`는 두 번째 호출에서 `futures`를 비우게 한다. 엔진은 `bare_engine({'workspace': '.', 'id': 'RI-test', 'config': {}}, runtime)`이다. `_controls`, `_check_installation`, `_save`, `_settle_stops`를 `create_autospec` 대역으로 둔다(주석: 정지 판단은 이 규칙의 대상이 아님). `_dispatchable`은 부르면 `AssertionError('new work must not be dispatched')`를 던진다.
- 실행: `patch('do_math.scheduler.ModelCalls', return_value=calls)` 아래에서 `host._run_parallel()`.
- 단언: `calls.collect` 호출 수가 2다. `calls.close`가 불렸다. `runtime['status'] == 'waiting'`이다. 대기열이 원래 한 행 그대로다.
- 대역: 위의 `create_autospec` 대역들과 `ModelCalls` 패치.
- 비고: 제품 루프는 `pending_installation_repair`가 있으면 `stopping`으로 판단한다. 진행 중 호출이 남아 있으면 `wait` 후 계속하고, 비면 빠져나간다(scheduler.py 행 308–317). 루프 뒤 설치 수리가 걸려 있으면 상태를 `waiting`으로 둔다(행 382–384). `close`는 `finally`에서 부른다.

### `test_scheduler_dispatches_no_research_while_an_installation_recovery_has_not_ended` (행 152–170)
- 성질: 감독자가 잠금을 풀었더라도, 끝나지 않은 설치 회복 실행(`role='recovery'`, `status='stopping'`)이 있으면 스케줄러는 연구를 배정하지 않는다.
- 준비: 손으로 만든 런타임. 대기열에 `AC-independent`가 있고, 실행 `EX-repair`는 `role='recovery'`, `status='stopping'`이며, 설치 수리 처분은 없다. `ModelCalls` 대역의 `futures`는 비어 있다. `_controls`, `_check_installation`, `_save`, `_settle_stops`, `_refresh_readiness`, `_resume_formal_waits`를 `create_autospec`으로 바꾸고, `_scan_due`는 참을 돌려주게 한다. `_dispatchable`은 부르면 실패한다.
- 실행: `host._run_parallel()`.
- 단언: 대기열이 원래 한 행 그대로다.
- 대역: 위와 같은 종류의 `create_autospec` 대역과 `ModelCalls` 패치.
- 비고: 원문 주석(행 153–154)이 상황을 밝힌다: 재시작 회복이 수리 AI의 로컬 Job 종료를 확인하지 못해, 그 AI가 여전히 설치본을 바꾸고 있을 수 있다. 제품 조건은 scheduler.py 행 309–312다. 진행 중 호출이 없으므로 루프는 첫 판단에서 빠져나간다. 그래서 `_scan_due`와 `_refresh_readiness` 대역은 이 경로에서 불리지 않아도 된다. 이 시험은 루프 뒤의 `status`를 단언하지 않는다.

### `test_supervisor_routes_diagnosed_live_engine_defect_and_probe_stays_read_only` (행 172–196)
- 성질: 감독자의 탐침은 걸려 있는 설치 진단을 스냅숏에서 읽기만 하고 회복이나 예약을 부르지 않는다. 실제 점검은 회복 경로로 넘긴다. 로컬 보류가 있으면 회복을 부르지 않는다.
- 준비: `installation_repair_state()`. 엔진 상태는 `status='ready'`, `snapshot='head'`, `operator_enabled=True`, `installation_repair`(처분 사본)다. `ResearchRepository`는 `load(snapshot)`이 `(snapshot, {'config': {'operator_enabled': True}}, runtime)`을 돌려주는 `SimpleNamespace`다.
- 실행: (1) `operator.check(*args, probe=True)`. (2) `operator.check(*args)`. (3) `operator.hold(args[2], reason='user hold')`로 보류를 둔 뒤 회복 대역을 초기화하고 `operator.check(*args)`.
- 단언: (1)은 `outcome == 'installation_repair_pending'`이고 `failure['diagnosis_id']`가 처분 ID다. `recovery`와 `schedule`이 불리지 않았다. (2)는 `outcome == 'routed'`이고 `recovery`가 인자 `(repo, 'RI-test', work)`로 정확히 한 번 불렸다(주석: "Recovery rereads the pending diagnosis under its own lock."). (3)은 `outcome == 'held'`이고 `recovery`가 불리지 않았다.
- 대역: `patch.object(operator, 'read_status', ...)`, `patch.object(operator, 'ResearchRepository', return_value=repository)`, `patch.object(operator, 'recovery', return_value={'outcome': 'routed'})`, `patch.object(operator, 'schedule')`.
- 비고: `hold`는 실제로 임시 작업 공간의 운영자 폴더에 `HOLD.json`을 쓴다. 탐침의 `failure`는 실제 `installation_failure`가 계산한다.

### `test_installation_repair_continues_latest_rejected_bundles_without_resetting_count` (행 198–208)
- 성질: 설치 수리 뒤의 재개는 대기 행이 가진 최신 거부 묶음과 수리 횟수를 그대로 이어받는다. 처분은 `applied`가 되고 대기 행은 사라진다.
- 준비: `installation_repair_state()`. 대기 행의 `repair_attempt`는 2다.
- 실행: `resume_installation_repair(runtime, record, repaired_by='EX-repair', at='2026-09-22T01:00:00Z')`.
- 단언: 반환 행동의 `repair.execution_id == 'EX-failed'`, `repair_attempt == 2`, `continuation_of == 'EX-failed'`다. `waiting_actions`가 비어 있다. 처분의 `status == 'applied'`다. 활동 `AY-work`의 상태가 `'waiting'`이다. 대기열이 `[action]`이다.
- 대역: 없음.
- 비고: 제품 주석(repair_execution.py 행 89)은 "The waiting request owns the latest returned bundles and error report."라고 밝힌다. 활동 상태가 여전히 `waiting`이라는 단언은 현재 동작을 고정한다. `activities.continue_activity`는 조건 없이 불리면 이미 `waiting`인 활동의 상태를 바꾸지 않고, 그 밖의 활동만 `ready`로 둔다(activities.py 행 187–190). 활동의 대기 해소는 중앙 수명주기 관문의 몫이다(같은 함수 docstring).

## 관계

- 운영 처분의 다른 종류(`resume`, `retry`의 새 후속 생성, 봉인 입력 검증)는 `research` 조각의 `test_research_recovery`가 검사한다. 그 모듈은 같은 `start_repair_host`를 쓰고, `_complete_operational_disposition`을 부르는 시험 모듈은 이 모듈 밖에서 그 모듈과 `test_repetition`뿐이다. `test_supervisor_recovery`(예약 감독자)와 `test_input_recovery`(입력 초과의 공개 재시도)는 운영 처분을 다루지 않는다. 이 모듈의 첫 시험은 후속이 이미 있는 경우의 정산만 본다.
- 설치 수리의 실제 실행(수리 AI의 동결 사본, 설치 교체, 진단 뒤 재시작)은 `host` 조각의 `test_diagnosed_installation_recovery`, `test_operator`, `test_operator_bootstrap`이 다룬다. 이 모듈은 경로 배정 규칙을 대역 위에서 본다.
- 설치 정체성은 두 가지다. 수리에 쓰는 `installation_sha256`(스킬 전체, 시험 제외)은 이 모듈이 검사한다. 판본 manifest `_installation_manifest`(코드와 역할 문서)는 `test_installation_discovery`가 검사한다.
- 픽스처 의존은 다음과 같다(`consumers.json`). `engine_fixtures.start_repair_host`는 이 모듈과 `research` 조각의 `test_research_recovery`가 쓴다. `record_fixtures.installation_repair_state`는 이 모듈과 `host` 조각의 `test_diagnosed_installation_recovery`가 쓴다. 따라서 이 모듈의 경로 배정 시험과 그 모듈의 실제 설치 회복 시험은 같은 시작 상태를 공유한다. `research_fixtures.bare_engine`은 여러 모듈이 공유한다.

# test_execution_lifecycle

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_execution_lifecycle.py` (371행) |
| 클래스 / 테스트 | 4 / 15 |
| 시험 대상 제품 코드 | `do_math/activities.py`의 `open_activity`, `assign_execution`, `wait_for`, `finish_activity`, `validate_activities`, `bind_action`, `continue_activity`, `resume_activity`; `do_math/execution_lifecycle.py`의 `create_execution`, `transition_execution`, `record_submission_intent`, `recover_execution`, `end_recovered`, `begin_preparation`, `end_preparation`; `do_math/provider_wait.py`의 `retry_time`, `gate_open`; `do_math/provider_engine.py`의 `_provider_admit`, `_settle_recovered_execution`; `do_math/session_slots.py`의 `SessionSlots`; `do_math/control_transport.py`의 `ControlTransport`; `do_math/repository.py`의 `ResearchRepository` |
| 사용하는 픽스처 모듈 | `research_fixtures`의 `bare_engine`, `git_init`, `sealed_maintenance_submission`, `current_state`(뒤의 둘은 테스트 안에서 늦게 import) |
| 격리 표지 | 없음 |
| 시작 상태 | `ActivityContractTests`, `ExecutionLifecycleTests`, `ProviderAdmissionTests`의 첫 시험은 1단(사전 레코드에 대한 순수 전이 함수). `ProviderAdmissionTests`의 나머지 둘은 `bare_engine` 위의 손으로 쓴 상태. `StoredExecutionTests`는 `git_init`으로 만든 실제 Git 저장소에 최소 상태를 공개하고, 저장·재적재 왕복을 쓴다 |

## 목적

모듈 docstring은 "Activities and their executions: attempts, waits, recovery, provider admission and the stored execution record."이다. 활동(activity)은 하나의 일을 소유하고, 실행(execution)은 그 일의 시도 하나다. `execution_lifecycle.py`의 docstring은 "Execution state transitions, receipts, and recovery dispositions."이다. 실행 상태는 `queued → starting → running → stopping → ended`의 정해진 간선만 따른다. 끝난 실행은 종료 시각과 닫힌 결과(`output_accepted`, `execution_incomplete`, `cancelled`, `start_failed`)를 가져야 하고, `output_accepted`는 제출 영수증을 요구한다. 이 모듈은 네 층을 본다.

- 활동과 시도의 관계. 여러 시도를 소유하고, 모든 시도가 끝난 뒤에만 기다리며, 이어짐 관계는 정당해야 하고, 기다림은 배정으로 지워지지 않는다.
- 실행 전이. 제출 의향의 원자성과 재생, 복구 처분, 준비 실패.
- 공급자 입장. 재시도 시각과 관문, 입장 거부의 대기 기록, 실제 예약과 Job이 빈 뒤의 정산.
- 저장된 실행 레코드. Git 왕복, 종료 확인과 예약 반환, 일시정지의 큐 결합과 체크포인트 계보, 제출 의향과 권한 철회의 단일 공개, 준비 시도의 내구성.

## 모듈 수준 요소

- 행 8: `sys.path.insert(0, str(Path(__file__).resolve().parents[1]))`로 `scripts/` 폴더를 경로 앞에 넣는 공통 머리다.
- 행 20 `TIME`: `"2026-09-20T00:00:00+00:00"`. 모든 전이와 활동 기록의 시각으로 쓰는 고정 시각이다.
- 행 370–371: 직접 실행하면 `unittest.main(verbosity=2)`를 부른다.

## ActivityContractTests (행 23–75)

- 기반: `unittest.TestCase`. 표지와 클래스 속성은 없다.
- `setUp` (행 24–27): `runtime = {"activities": {}, "executions": {}}`에 활동 `AY-1`(종류 `research_work`, 소유자 `{"kind": "task", "id": "TK-1"}`, 입력 `["IN-1"]`)을 연다.
- `execution(self, execution_id, continuation_of=None)` (행 29–32): 활동 `AY-1` 소유의 `queued` AI 실행을 `create_execution`으로 만든다. 입력 명세는 `{"id": "IN-1"}`, 프로필 참조는 문자열 `"PF-1"`이다.
- `end_cancelled(self, execution)` (행 34–37): `starting → stopping → ended`(결과 `cancelled`)로 전이한다.

### `test_one_activity_owns_multiple_attempts_and_waits_after_them` (행 39–54)
- 성질: 한 활동은 이어지는 여러 시도를 소유하고, 모든 시도가 끝난 뒤 기다림으로 넘어가며, 그 상태는 활동 검증을 통과하고 끝낼 수 있다.
- 준비: `setUp`의 활동. `EX-1`과, `EX-1`을 잇는 `EX-2`를 차례로 배정하고 각각 취소로 끝낸다.
- 실행: `wait_for(runtime, "AY-1", reason="provider unavailable", condition={"kind": "provider_admission", "provider": "codex"}, next_owner={"kind": "engine"}, at=TIME)`, `validate_activities(runtime)`, `finish_activity(..., unresolved=["provider availability"], followups=["retry"])`.
- 단언: 기다림 뒤 활동의 `status`가 `"waiting"`이고 `assigned_execution_ids`가 `["EX-1", "EX-2"]`다. 검증 오류가 `[]`다. 끝낸 활동의 `status`가 `"finished"`다.
- 대역: 없음.

### `test_wait_and_continuation_reject_unjustified_relations` (행 56–64)
- 성질: 살아 있는 시도가 있으면 활동은 기다릴 수 없고, 끝나지 않은 시도를 잇는 시도는 활동 검증에서 오류가 된다.
- 준비: `EX-1`을 배정하고 끝내지 않는다.
- 실행: `wait_for(...)`를 부르고, 이어서 `EX-1`을 잇는 `EX-2`를 배정한 뒤 `validate_activities`를 부른다.
- 단언: `wait_for`가 `ValueError`를 메시지 조각 `"ended"`로 낸다. 제품 문구는 `"an activity may wait only after its assigned executions ended"`다. 검증 오류 가운데 `"continuation"`을 담은 것이 있다. 제품 문구는 `"<id>: continuation is not an ended execution in the same activity"`다.
- 대역: 없음.
- 비고: 이어짐의 부당함은 배정 때 거부되지 않고, 검증기가 오류로 보고한다. 시험도 배정이 성공한 뒤 검증 결과를 본다.

### `test_assignment_cannot_erase_an_unresolved_pause_wait` (행 66–75)
- 성질: 사용자 일시정지로 기다리는 활동에는 기다림이 풀리기 전까지 새 시도를 배정할 수 없고, 거부는 런타임을 바꾸지 않는다.
- 준비: `EX-1`을 배정하고 취소로 끝낸 뒤, `reason="user_pause"`, 조건 `{"kind": "user_resume"}`, 다음 소유자 `"user"`로 기다리게 한다. 런타임의 깊은 사본을 떠 둔다.
- 실행: `EX-1`을 잇는 `EX-2`를 배정한다.
- 단언: `ValueError`의 메시지 조각이 `"wait"`다. 제품 문구는 `"resolve the recorded activity wait before assigning an execution"`다. 런타임이 사본과 같다.
- 대역: 없음.

## ExecutionLifecycleTests (행 78–146)

- 기반: `unittest.TestCase`. 표지, 클래스 속성, 훅이 없다.
- `running(self)` (행 79–84): `EX-1`(활동 `AY-1`, 입력 `{"source": "fixed"}`, 프로필 `"PF-1"`)을 만들어 `starting → running`으로 전이해 돌려준다. 활동은 만들지 않는다.

### `test_accepted_output_requires_a_real_transport_receipt` (행 86–101)
- 성질: 실제 제어 전송이 낸 수락 영수증과 중앙에서 봉인한 제출 의향이 있으면, 실행은 `output_accepted`로 끝날 수 있다.
- 준비: 실행 중인 `EX-1`. 임시 폴더의 `ControlTransport`에서 `issue("EX-1", "GR-1")`로 결합을 받는다. 그 결합에 `request_id="CT-1"`, `kind="submit_intent"`를 붙인 요청을 `transport.receive(request, publish=...)`로 수락시켜 영수증을 얻는다. 게시 콜백은 `{"state": "accepted", "published": True, "snapshot": "SN-1"}`을 돌려준다. `sealed_maintenance_submission(workspace, 'EX-1')`로 실제 중앙 봉인 바이트에서 의향을 만든다.
- 실행: `record_submission_intent(execution, intent, receipt, at=TIME)`, `stopping`으로 전이(이미 `stopping`이므로 변화 없음), `ended`로 전이(결과 `output_accepted`, 처분 `"receiver_validation_pending"`).
- 단언: 실행의 `outcome`이 `"output_accepted"`다.
- 대역: 게시 콜백 람다.
- 비고: 이름은 "실제 전송 영수증을 요구한다"고 말하지만, 시험은 영수증이 있는 양성 경로만 본다. 영수증 없이 `output_accepted`로 끝내면 `check_termination`이 `"accepted output lacks submission receipt"`로 거부한다는 음성 경로는 이 시험에서 단언하지 않는다. `record_submission_intent`가 이미 `stopping`으로 전이하므로, 시험의 `stopping` 전이는 같은 상태로의 전이이고 제품은 그것을 변화 없이 받아들인다.

### `test_recovery_changes_only_the_recovered_execution_and_its_end_clears_the_disposition` (행 103–115)
- 성질: 복구 처분은 복구한 실행에만 적용되고, 그 실행을 끝내면 처분이 지워지며, 끝난 실행에는 다시 복구 처분을 줄 수 없다.
- 준비: 실행 중인 두 실행. 하나는 `lost`이고, 다른 하나는 `id`를 `EX-2`로 바꾼 `independent`다.
- 실행: `recover_execution(lost, at=TIME)`, `end_recovered(lost, outcome="execution_incomplete", disposition="preserved_for_followup")`, 다시 `recover_execution(lost)`.
- 단언: 복구 뒤 `lost`는 `("stopping", "reconcile_local_and_remote")`이고 `independent`는 여전히 `"running"`이다. 끝낸 뒤 `lost`는 `("ended", "execution_incomplete")`이고 `recovery_disposition` 키가 없다. 재복구는 `ValueError`를 메시지 조각 `"no recovery disposition"`으로 낸다. 제품 문구는 `"a ended execution has no recovery disposition"`이다.
- 대역: 없음.
- 비고: 주석(112행)은 끝난 실행이 더는 복구 처분에 의해 정리에서 보호되지 않는다고 설명한다. 제품의 `transition_execution`이 `ended`에서 `recovery_disposition`을 지운다.

### `test_submission_transition_replay_and_invalid_receipt_are_atomic` (행 117–135)
- 성질: 제출 의향 기록은 원자적이다. 다른 실행의 영수증은 아무것도 바꾸지 않고 거부된다. 같은 의향과 영수증의 재생은 멱등이다. 이미 기록된 뒤의 잘못된 의향은 거부되며 기록을 바꾸지 않는다.
- 준비: 실행 중인 `EX-1`. `sealed_maintenance_submission`의 의향. 손으로 만든 영수증 `{"id": "CT-submit", "kind": "submit_intent", "state": "accepted", "execution_id": "EX-1", "received_at": TIME}`.
- 실행: `record_submission_intent`를 네 번 부른다. 다른 실행의 영수증, 올바른 영수증, 같은 호출의 재생, `{"manifest": []}` 의향이다.
- 단언: 단계별로 확인하는 결과는 다음과 같다.
  - `execution_id`를 `EX-other`로 바꾼 영수증은 `ValueError`이고, 실행이 사본과 같다.
  - 올바른 영수증이면 `status`가 `"stopping"`이다.
  - 같은 호출을 다시 하면 실행이 첫 기록 직후의 사본과 같다.
  - 의향을 `{"manifest": []}`로 주면 `ValueError`이고, 실행이 그 사본과 같다.
- 대역: 없음.
- 비고: 마지막 거부는 "다른 의향이 이미 기록되었다" 검사(`"a different submission intent or receipt was already recorded"`)가 아니다. 그보다 앞선 의향 모양 검사(`candidate_id`와 `output_ref`가 문자열이어야 한다, `"submission intent requires a centrally sealed candidate"`)에서 난다(`execution_lifecycle.py` 94–96행). 시험은 예외 유형만 보므로 어느 검사가 거부했는지 고정하지 않는다. 따라서 올바른 모양의 다른 의향으로 재기록을 거부하는 경로는 이 시험이 실행하지 않는다. 제품은 모든 검사를 사본(`candidate`)에서 하고 끝에 원본을 교체하므로, 거부된 호출은 원본을 바꾸지 않는다.

### `test_failed_preparation_cannot_drop_an_existing_process` (행 137–146)
- 성질: 이미 용량과 프로세스가 붙은(입장한) 실행은 입력 준비 실패로 끝낼 수 없다. 먼저 예약과 프로세스를 정리해야 하며, 거부는 실행을 바꾸지 않는다.
- 준비: `queued` 실행에 `capacity`(프로세스 `{"job_name": "existing-job"}`, 종료 `unknown`)를 붙인다.
- 실행: `end_preparation(execution, at=TIME, stage="role_input", reason="input error", cancelled=False)`. `end_preparation`은 테스트 안에서 import한다.
- 단언: `ValueError`의 메시지 조각이 `"reconcile"`이다. 제품 문구는 `"admitted preparation must reconcile reservations and process before ending"`이다. 실행이 사본과 같다.
- 대역: 없음.

## ProviderAdmissionTests (행 149–221)

- 기반: `unittest.TestCase`. 표지, 클래스 속성, 훅, 도우미가 없다.

### `test_provider_wait_is_a_wait_record_not_a_capacity_claim` (행 150–157)
- 성질: 공급자 대기는 재시도 시각과 관문 상태의 기록일 뿐 용량 주장이 아니다. 재시도 간격은 지수로 늘되 상한에서 멈추고, 관문은 시각에 이르러야 열리며, 점검 중인 관문은 닫혀 있다.
- 준비: 없음(순수 함수).
- 실행: `retry_time({}, 2, 100, 20, 60)`, `retry_time({}, 9, 100, 20, 60)`, `gate_open`을 네 상태로 부른다.
- 단언: 재시도 시각은 140(100+min(60, 20·2¹))과 160(상한 60)이다. `retry_at=140`으로 기다리는 관문은 시각 139에서 닫혀 있고 140에서 열린다. `available`은 열려 있고, `checking`은 시각 140에서도 닫혀 있다.
- 대역: 없음.
- 비고: 이름의 "not a capacity claim"은 함수가 슬롯이나 예약을 다루지 않는다는 뜻이다. 시험은 이를 직접 단언하지 않는다. `retry_time`의 첫 인자(실패 기록)에 `retry_at`이 없으므로, 공급자가 알려 준 시각을 쓰는 분기는 보지 않는다.

### `test_provider_mixin_records_structured_wait_on_refused_admission` (행 159–175)
- 성질: 입장이 거부되면 엔진의 공급자 입장 함수는 슬롯 계산이 남긴 구조화된 대기를 요청의 `dispatch_wait`에 사본으로 기록한다.
- 준비: 지역 대역 클래스 `Slots`는 `admission_wait`가 공급자 한도 대기(`codex`, 재시도 시각, 다음 소유자 `scheduler`)이고 `acquire`가 언제나 `False`다. 공급자 재시도 설정만 가진 `bare_engine`의 `_session_slots`를 이 대역을 돌려주는 `create_autospec`으로 바꾼다. 요청 `AC-1`에는 모델 선택이 있다.
- 실행: `engine._provider_admit(action, "EX-1", profile={"id": "EP-1"}, execution={"id": "EX-1"})`.
- 단언: 반환값이 `False`다. `action["dispatch_wait"]`가 대기와 같지만 같은 객체는 아니다(`assertIsNot`).
- 대역: `Slots` 클래스, `_session_slots`의 autospec 대역.
- 비고: 제품은 `deepcopy(slots.admission_wait)`로 기록한다(`provider_engine.py` 57행). 동일 객체가 아니라는 단언이 이 복사를 고정한다.

### `test_provider_admission_reserves_runtime_capacity_and_settles_after_the_job_is_empty` (행 177–221)
- 성질: 공급자 입장은 실행을 런타임에 등록하고 예약을 잡는다. 복구 정산은 명명 Job이 빈 것이 확인될 때만 그 실행을 끝내고 예약을 돌려주며, 다른 실행의 예약은 건드리지 않는다.
- 준비: 세 등급 모두 `gpt-5.6-terra`이고 작업 슬롯이 2인 설정. 여기서 만든 프로필로 `bare_engine`을 만든다. 인스턴스 작업 공간은 시스템 임시 폴더다. `research_work` AI 프로필 하나를 고르고, 실행 `EX-git`(`starting`)과 요청 `AC-git`을 둔다.
- 실행: `engine._provider_admit`을 두 번, `engine._session_slots().started`를 한 번, `named_job_empty` 패치를 바꿔 가며 `engine._settle_recovered_execution("EX-git")`을 두 번, 끝으로 `slots.release("EX-git")`을 부른다.
- 단언: 단계별로 확인하는 결과는 다음과 같다.
  1. `_provider_admit`가 참이다. `EX-git`이 런타임 실행에 있고 예약이 비어 있지 않다.
  2. 둘째 `research_work` 실행 `EX-independent`도 입장한다(슬롯 2).
  3. `engine._session_slots().started("EX-git", {"job_name": 티켓의 이름}, at=TIME)` 뒤 `EX-git`의 `status`가 `"running"`이다.
  4. `named_job_empty`가 `False`이면 `_settle_recovered_execution("EX-git")`이 거짓이고, 상태는 `"running"` 그대로다.
  5. `True`이면 참이고, `(status, outcome)`이 `("ended", "execution_incomplete")`이며 `local_termination`이 `"confirmed"`다.
  6. `EX-independent`는 `"starting"` 그대로이고 그 예약은 모두 `held`다.
  7. `slots.release("EX-git")`가 참이다(이미 확인됨).
- 대역: `patch("do_math.windows_job.named_job_empty", return_value=False/True)`.
- 비고: `_settle_recovered_execution`은 사본에서 `end_recovered`를 한 뒤 `release`가 성공할 때만 원본을 교체한다(`provider_engine.py` 22–43행). 그래서 4에서 상태가 바뀌지 않는다. `acquire`는 넘겨받은 실행 사전을 제자리에서 갱신해 런타임에 넣으므로, 시험이 쥔 `execution` 객체로 상태 변화를 읽을 수 있다. 둘째 프로필은 `actor_kind` 조건 없이 첫 `research_work` 프로필을 다시 고르므로 첫 프로필과 같을 수 있다. 시험은 이것을 구별하지 않는다. 이 시험은 Windows 호스트를 전제한다. `_provider_admit`의 `acquire`는 `launch.ticket`에서 `windows_job.owner_identity()`를 부르고(Windows가 아니면 `WindowsJobUnsupportedError`), 정산의 `release`가 부르는 `launch.termination_confirmed`는 패치되지 않은 `owner_ended`로 현재 프로세스를 `OpenProcess`로 관찰한다. 패치되는 것은 `named_job_empty`뿐이다. 이 모듈에는 `skipUnless`가 없다.

## StoredExecutionTests (행 224–367)

- 기반: `unittest.TestCase`. 클래스 docstring은 "Real family storage; only the OS Job observation is replaced."다.
- `setUp` (행 226–250): 다음 시작 상태를 만든다.
  - 임시 폴더를 `git_init`으로 Git 저장소로 만든다. 정리는 `addCleanup`에 맡긴다.
  - `ResearchRepository(root, "RI-01ARZ3NDEKTSV4RRFFQ69G5FAV")`를 연다.
  - `current_state`로 `DEFAULT_CONFIG`와 그 프로필, 빈 실행·큐·예약을 가진 최소 상태를 만든다. 주석은 "Every stored state passes the current lifecycle gate."다.
  - `maintenance` 프로필을 `self.profile`로 둔다. 활동 `AY-audit`(종류 `maintenance`, 소유자 `"AC-audit"`)을 연다.
  - 실행 `EX-audit`(역할 `maintenance`, `action`은 `{"id": "AC-audit", "role": "maintenance"}`의 사본)을 만들어 배정한다.
  - 같은 요청 `self.action`을 큐에 넣는다.
  - `repo.initialize(instance, runtime)`로 공개하고 그 헤드를 `self.head`에 둔다.
- `reload(self)` (행 252–255): 현재 상태를 `save_with_state`로 공개한 뒤 새 헤드에서 다시 적재한다. `self.instance`, `self.runtime`, `self.execution`을 적재본으로 바꾼다. 곧 모든 단언이 Git 왕복을 거친 값을 본다.
- `running(self)` (행 257–259): `self.execution`을 `starting → running`으로 전이한다.

### `test_recovery_record_completion_round_trips_through_git` (행 261–267)
- 성질: 완료 시각이 있는 복구 기록이 Git 저장·적재 왕복에서 보존된다.
- 준비: `setUp`의 상태. 그 위에 `runtime["recoveries"]["RY-audit"]`를 둔다. 이 기록에는 시작·완료 시각, 대상 `EX-audit`, 처분 하나(지역 종료 미확인, 원격 종료 `unknown`, 다음 소유자 `operator`)가 있다.
- 실행: `self.reload()`.
- 단언: 적재한 `recoveries.RY-audit.finished_at`이 `TIME`이다.
- 대역: 없음.
- 비고: 저장 스키마가 복구 기록의 `finished_at`을 받아들인다는 것은 공개가 성공한 것으로 함께 확인된다.

### `test_confirmed_local_termination_releases_only_its_reservation` (행 269–298)
- 성질: 복구 정산은 명명 Job이 빈 것이 확인되어야 실행을 끝내고 그 실행의 예약을 전량 반환한다. 결과는 Git 왕복 뒤에도 남는다. 이미 끝난 적재 실행의 정산은 멱등이다.
- 준비: `setUp`의 실행을 `research_work` AI 프로필에 다시 묶는다. 주석(273–274행)은 작업 역할만 모델 슬롯을 예약하므로 반환을 확인할 예약이 있게 하려는 것이라고 설명한다. `SessionSlots`로 `starting` 전이 뒤 `acquire`한다. 반환값과 `reservation_ids`가 참이다. `started`로 티켓의 Job 이름을 기록한 뒤 `reload()`하고, 적재본으로 `bare_engine`을 만든다.
- 실행: `named_job_empty`를 `False`, `True`로 패치하며 `engine._settle_recovered_execution("EX-audit")`을 부르고, 재적재 뒤 한 번 더 부른다. 사이에 `reload()`로 Git 왕복을 한다.
- 단언: 단계별로 확인하는 결과는 다음과 같다.
  1. `named_job_empty=False`이면 `_settle_recovered_execution`이 거짓이고 상태는 `"running"`이다.
  2. `True`이면 참이다.
  3. `reload()` 뒤 `(status, outcome)`이 `("ended", "execution_incomplete")`이고 `local_termination`이 `"confirmed"`다. 단위가 `execution`인 모든 예약 행은 `returned == reserved`다.
  4. 엔진에 새 적재본을 붙이고 다시 정산하면 참이다. 주석은 "A loaded ended execution is reconciled idempotently, not silently excluded."다.
- 대역: `named_job_empty` 패치(클래스 docstring이 말하는 "OS Job observation").
- 비고: 이름의 "only its reservation"은 이 시험에서 직접 단언되지 않는다. 저장소에는 이 실행 하나뿐이고, 반환 단언도 단위 `execution` 행에만 한다. 다른 실행의 예약이 유지되는지는 `ProviderAdmissionTests`의 셋째 시험이 본다. `acquire`의 티켓 발급(`windows_job.owner_identity()`)과 정산의 `owner_ended`는 패치되지 않으므로, 이 시험도 Windows 호스트를 전제한다.

### `test_pause_keeps_original_queue_binding_and_checkpoint_lineage` (행 300–325)
- 성질: 사용자 일시정지로 끝난 시도의 후속은 원래 큐 요청에 묶인 채 기다린다. 재개 뒤 만든 후속 시도는 새 대화 문맥으로 시작하고, 이어짐은 체크포인트를 가진 옛 시도를 가리킨다. 이 모두가 Git 왕복을 견딘다.
- 준비: `setUp`의 상태.
- 실행:
  1. 요청의 작업 사본을 `activities.bind_action(runtime, working, "AY-audit")`으로 묶는다.
  2. 실행을 `running → stopping(reason="user_pause") → ended(cancelled)`로 보낸다.
  3. `runtime["checkpoints"]["EX-audit"]`을 둔다.
  4. `continue_activity(runtime, "EX-audit", reason="user_pause", condition={"kind": "user_resume"}, next_owner="user")`를 부르고 `reload()`한다.
  5. `resume_activity`를 부른다. 큐의 첫 요청에서 `owner_activity_id`, `continuation_of`, `context_origin`을 읽어 후속 실행 `EX-resumed`(역할 `maintenance`)를 만들고 배정한 뒤 `reload()`한다.
- 단언:
  - 1 뒤 원래 큐 요청 `self.action`의 `owner_activity_id`가 `"AY-audit"`다. 작업 사본이 아니라 같은 ID의 큐 요청도 묶인다.
  - 4 뒤 활동의 `status`가 `"waiting"`이고 `waiting.next_owner`가 `"user"`다.
  - 5 뒤 `EX-resumed`의 `context_origin`이 `[]`이고, `continuation_of`가 `checkpoints`의 키 가운데 하나다. `validate_activities`가 `[]`다.
- 대역: 없음.
- 비고: `continue_activity`의 docstring은 옛 체크포인트가 `continuation_of`로 계속 가리켜지지만, 새 대화가 옛 문맥을 물려받았다는 증거는 아니라고 설명한다. `context_origin == []`이 이것을 고정한다.

### `test_intent_stops_and_revokes_execution_authority_in_same_git_publication` (행 327–348)
- 성질: 제출 의향의 수락은 실행 정지, 실행 연구 권한 철회, 제어 영수증을 하나의 Git 공개에 함께 싣고, 전송 영수증은 그 공개의 스냅숏을 가리킨다.
- 준비: 실행을 `running`으로 보내고 `reload()`한다. 임시 폴더 아래 `delivery`에 `ControlTransport`를 두고, `submission-workspace`에 `sealed_maintenance_submission`으로 의향과 산출물을 만든다. `issue("EX-audit", "GR-audit", workspace=...)`로 결합을 받고, `submit_intent` 요청(`request-audit`, 초안 경로 `draft.json`)을 만든다.
- 실행: `transport.receive(request, publish=publish)`. 게시 콜백 `publish`는 다음 순서로 돈다.
  1. 영수증 `CT-audit`로 `record_submission_intent`를 부른다.
  2. 실행이 `stopping`이고 `authority_revocation.scope`가 `"execution_research"`임을 콜백 안에서 단언한다.
  3. `runtime["control_receipts"]`에 영수증을 넣고, 산출물과 함께 `save_with_state`로 공개한다.
  4. 새 헤드를 스냅숏으로 담은 수락을 돌려준다.
- 단언: 전송 영수증의 `snapshot`으로 적재한 상태에서 `EX-audit`의 `authority_revocation.receipt_id`가 `"CT-audit"`이고, `control_receipts.CT-audit.state`가 `"accepted"`다.
- 대역: 게시 콜백(엔진의 검증과 CAS를 대신한다). 저장소와 전송 파일은 실제다.
- 비고: 제품 `ControlTransport.receive`의 docstring은 게시자가 `published: true`와 비어 있지 않은 권위 스냅숏을 돌려줄 때만 `accepted`를 낼 수 있다고 밝힌다. 이 시험의 콜백이 그 계약을 따른다.

### `test_preparation_attempt_is_durable_before_input_and_failure` (행 350–367)
- 성질: 입력 준비 시도는 입력이 생기기 전에 `queued` 상태로 내구성 있게 기록된다. 준비 실패는 단계와 사유를 남기고 `start_failed`로 끝난다. 준비 중의 일시정지는 `cancelled`로 끝난다.
- 준비: `setUp`의 실행(`queued`, 입력 명세 `[]`).
- 실행: `lifecycle.begin_preparation`과 `lifecycle.end_preparation`을 저장된 실행에 한 번씩(각각 `reload()`와 함께), 저장하지 않는 `EX-paused`에 한 번씩 부른다.
- 단언: 단계별로 확인하는 결과는 다음과 같다.
  1. `begin_preparation(execution, at=TIME)` 뒤 `reload()`하면 `status`가 `"queued"`이고 `input_manifest`가 `[]`다.
  2. `end_preparation(stage="context", reason="input unavailable", cancelled=False)` 뒤 `reload()`하면 `(status, outcome)`이 `("ended", "start_failed")`다. `input_preparation`의 `reason`은 `"input unavailable"`, `stage`는 `"context"`다.
  3. 저장하지 않는 별도 실행 `EX-paused`에 `begin_preparation`을 하고, `end_preparation(stage="role_input", reason="test interruption", cancelled=True)`를 부른다. `(outcome, input_preparation.stage, input_manifest)`가 `("cancelled", "role_input", [])`다.
- 대역: 없음.
- 비고: 주석(361행)은 준비 중의 일시정지가 시작 실패가 아니라 취소로 끝난다고 설명한다. 3의 실행은 저장소에 넣지 않으므로, 이 부분은 Git 왕복 없이 전이 규칙만 본다.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈:
  - `test_budget`은 예약 산술과 정산 규칙을 순수 함수로 본다. 이 모듈의 공급자 입장과 저장 실행 시험은 그 예약이 실행 수명과 함께 잡히고 반환되는 과정을 본다.
  - `test_supervisor_recovery`는 설치 복구가 `release_or_hold`로 종료 장벽을 지키는 경로를 본다. 이 모듈은 엔진의 `_settle_recovered_execution` 경로를 본다.
  - `test_control_transport`는 제어 전송 자체의 요청·영수증 규칙을 본다. 이 모듈은 전송 영수증이 실행 레코드와 한 공개로 묶이는 것을 본다.
  - 공급자 대기의 관문 수명(점검 소유자, 재관찰)은 `test_execution_profiles`의 `test_provider_wait_is_canonical_and_serializes_retry_probe`가 본다.
- 픽스처 의존: `bare_engine`, `git_init`, `current_state`, `sealed_maintenance_submission`(모두 `research_fixtures`).
- 이 모듈에만 있는 도우미: `ActivityContractTests.execution`, `end_cancelled`; `ExecutionLifecycleTests.running`; `StoredExecutionTests.reload`, `running`; 지역 대역 클래스 `Slots`; 지역 게시 콜백 `publish`.

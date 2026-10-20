# test_controls

| 항목 | 값 |
|---|---|
| 조각 | `lifecycle` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_controls.py` (571행) |
| 클래스 / 테스트 | 8 / 24 |
| 시험 대상 제품 코드 | `do_math/engine.py`의 `control`, `ResearchEngine`(`process_controls`, `control_result`, `status`, `run`, `_controls`, `_apply_inbox`, `_upkeep`, `_enqueue`, `_register_execution`, `_publish_control_request`); `do_math/control_contracts.py`의 `control_request_id`; `do_math/maintenance_gate.py`의 `apply_control`, `settle`; `do_math/scheduled_operator.py`의 `engine_start_guard`; `do_math/observations.py`의 `ObservationTracker`(자기 점검 의무·안전 경계·제어 요청 결합); `do_math/submission.py`의 `seal_submission`(대역으로 교체), `PREVIEW_CONTRACT_ID`; CLI `resume`, `quiesce`, `pause`, `release-quiesce` |
| 사용하는 픽스처 모듈 | `engine_fixtures`: `initialized`, `initialized_instance`, `routing_engine`, `start_submission_history`; `research_fixtures`: `install_adapter_fixture`, `new_instance`, `observe`, `restore_template`, `run_cli`, `write_checkpoint`(모듈 수준), `Clock`, `observation_rule`, `self_check_response`, `cli_result`(함수 안); `runner_fixtures`: `ScriptedRunner`; `state_fixtures`: `active_instance`, `start_active_copy`(함수 안) |
| 격리 표지 | 없음 |
| 시작 상태 | 클래스마다 다르다. `engine_fixtures.initialized_instance` 템플릿(공개 `initialize`만 돈 상태), 2단 `state_fixtures.active_instance` 템플릿과 그 위의 `start_submission_history`, 시험마다 공개 `initialize`를 새로 도는 경로(`new_instance`, `initialized`), 저장소 없는 엔진 대역 `routing_engine`, 순수 함수 호출(1단)이 섞여 있다 |

## 목적

모듈 docstring은 "사용자와 운영자의 제어: 전이, 수령증(receipt)과 그 식별, 큐잉, 유지보수 울타리(maintenance fence)"를 시험한다고 밝힌다. 제어는 두 갈래다. 사용자·운영자 제어는 공개 `control`이 인스턴스 작업 공간의 받은함(`control/<인스턴스>/<요청 ID>.json`)에 쓰고, 소유 엔진이 `process_controls`나 `_apply_inbox`로 적용한다(`engine.py` 252행 docstring "Queue user commands; only the owning engine publishes authority changes"). 실행 제어 요청(제출 의도, 미리보기, 안전 경계, 자기 점검 응답)은 전송 계층이 `_publish_control_request`로 넘기고, 엔진은 그 게시(CAS)의 성공을 수령증으로 돌려준다(1169–1170행 docstring "A transport acceptance acknowledges this CAS, not mathematical acceptance").

이 모듈이 지키는 계약은 다섯 무리다. 공개적으로 닫힌 인스턴스는 제어로 다시 열리지 않고, 낡은 요청은 소비되어 뒤를 막지 않는다. 수령증은 게시가 성공했을 때만 발급되고, 재전송은 다시 적용되지 않는다. 사용자 제어의 요청 ID는 결정적이고, 같은 요청은 상태가 바뀐 뒤에도 원래 결과로 재생된다. 큐에 들어간 사용자 제어는 안정된 행동 ID를 갖는다. 유지보수 울타리는 알 수 없는 실행을 놓아주지 않고 사용자 일시정지를 보존한다.

## 모듈 수준 요소

- 행 11: `sys.path.insert(0, ...)`로 `scripts/` 폴더를 경로 맨 앞에 넣는 공통 머리.
- 행 22–23 `CONFIG`: `scholarly_enabled=False`, `operator_enabled=False`, `lean_command=['test-lean']`, `tool_review_window_seconds=60`, `self_check_response_window_seconds=5`. `ControlTransitionTests.start`와 `paused_then_resumed`가 템플릿 매개변수로 넘긴다.
- `paused_then_resumed(**pause)` (행 409–423): `restore_template(initialized_instance, config=CONFIG, goal="pause identity fixture")`로 초기화 템플릿을 복원한다. 엔진 하나를 열어 `pause`(인자는 `**pause`)를 보내고 `process_controls()`, 이어 `resume`을 보내고 `process_controls()`를 부른다. 상태가 여전히 `paused`면 `AssertionError('the fixture's resume did not apply')`를 던진다. docstring은 "`pause`로 일시정지했다가 재개한 초기화 중 인스턴스"라고 적고, 저장소 경로, 인스턴스 ID, 첫 `pause`의 수령증을 돌려준다. `UserControlIdentity`의 두 시험이 쓴다.
- 행 570–571: 직접 실행하면 `unittest.main(verbosity=2)`를 부른다.

## ControlTransitionTests (행 26–129)

`unittest.TestCase`를 그대로 상속하고 표지가 없다.

- `setUp` (행 27–28): `research_fixtures.install_adapter_fixture(self)`. `do_math.initialization.adapter_for`를 `FixtureAdapter`를 돌려주는 대역으로 바꾸고, 정리 때 되돌린다. 저장소는 도우미가 만든다.
- `start(build, **parameters)` (행 30–34): `restore_template(build, config=CONFIG, **parameters)`로 템플릿을 복원하고 `self.root`, `self.iid`, `self.repo = root/'repository'`, `self.store = ResearchRepository(self.repo, self.iid)`를 세운다. docstring: "템플릿 상태를 복사한다".
- `initializing()` (행 36–37): `start(initialized_instance, goal="control transition fixture")`. 공개 `initialize`만 돈 상태의 템플릿이다.
- `active_with_preparation()` (행 39–45): `start(active_instance)`로 2단 템플릿을 복원하고, `ScriptedRunner`를 가진 엔진에 `research_preparation` 행동 하나를 큐에 넣어 저장한 뒤 그 엔진을 돌려준다. docstring: "큐에 AI 행동 하나(연구 준비)가 있는 활성 상태".
- `update(change)` (행 47–50): 저장소에서 현재 상태를 읽어 `change(instance, runtime)`를 적용하고 `save_with_state`로 게시한다. 엔진을 거치지 않고 게시된 상태를 바꾸는 수단이다.

### `test_pause_and_resume_cannot_reopen_a_publicly_closed_instance` (행 52–71)
- 성질: 공개적으로 닫힌 인스턴스는 뒤이은 `pause`나 `resume`으로 다시 열리지 않으며, 거부된 `resume`은 소비되어 대기 제어로 남지 않는다.
- 준비: `initializing()`.
- 실행: `close`를 보내고 새 엔진의 `process_controls()`. 이어 `pause`를 보내 처리하고, `resume`을 보내 그 접수 반환값을 변수 `rejected`에 받은 뒤 처리한다. 끝으로 프로세스 안 CLI `run_cli("resume", "--repository", ..., "--instance", ...)`를 부른다.
- 단언: 세 번의 처리 뒤 모두 `status()["status"]`가 `"closed"`다. 마지막 처리 뒤 `pending_controls`가 0이다. 게시된 런타임의 마지막 이력 행이 `kind="rejected_user_control"`이고 그 `request.id`가 `resume`의 요청 ID다. CLI 호출의 `returncode`가 0이고 표준 출력 JSON의 `result.effect`가 `"rejected"`다.
- 대역: `install_adapter_fixture`(어댑터 관측). CLI는 `run_cli`로 프로세스 안에서 부른다.
- 비고: CLI의 `_control`(`cli.py` 221–236행)은 `control`이 이미 처리된 결과(재생)를 돌려주면 그것을 그대로 내고, 아니면 `process_controls` 뒤의 결과를 낸다. 단언은 CLI가 어느 경로로 거부를 돌려주었는지 가르지 않고, 닫힌 인스턴스에 대한 `resume`의 결과가 CLI 층에서도 거부로 보인다는 것만 확인한다.

### `test_stale_request_is_consumed_and_does_not_poison_later_controls` (행 73–97)
- 성질: 받은 뒤 상태가 바뀌어 낡은 요청은 거부 기록과 함께 소비되고, 뒤따르는 제어의 적용을 막지 않는다.
- 준비: `active_with_preparation()`. 엔진을 `run(max_steps=1)`로 최대 8번 몰며, 매번 `planning.task_ready(...)['state'] == 'ready'`인 과제가 생기면 멈춘다.
- 실행: 준비된 과제를 대상으로 `request`(`role="supplemental_research"`)를 보낸다. `update`로 게시 상태의 그 과제를 `status="active"`로 바꿔 요청을 낡게 만든다. `pause`를 보낸 뒤 새 엔진의 `process_controls()`를 부른다.
- 단언: 준비된 과제가 생긴다(실패 메시지는 마지막 이력 3행). 처리 뒤 상태가 `"paused"`이고 `pending_controls`가 0이다. 게시된 런타임의 `processed_controls`에 요청 ID가 있고, 과제 상태는 여전히 `"active"`이며, 그 요청에 대한 `rejected_user_control` 이력 행이 있다.
- 대역: `ScriptedRunner`(역할 출력 대역), `install_adapter_fixture`.
- 비고: 엔진 구동은 단계 상한 1을 8번까지 반복하는 조건 정지 루프다. `ScriptedRunner`는 역할 호출마다 실제 로컬 Windows Job을 띄운다(`research_fixtures.local_job_runner`).

### `test_request_accepted_before_public_close_does_not_reopen_it` (행 99–108)
- 성질: 닫기 전에 받은 요청도 닫힌 뒤 처리되면 인스턴스를 다시 열지 않고 행동을 큐에 남기지 않는다.
- 준비: `initializing()`.
- 실행: `request`(`role="maintenance"`), 이어 `close`를 보낸 뒤 새 엔진의 `process_controls()`.
- 단언: 상태가 `"closed"`, `pending_actions`가 0, `pending_controls`가 0이다.
- 대역: `install_adapter_fixture`.

### `test_crash_marks_owning_activity_unresolved` (행 110–129)
- 성질: 실행 중에 소유 엔진이 죽으면 다음 엔진은 그 실행을 결과 없이 `stopping`으로 두고, 소유 활동에 묶은 채 로컬·원격 종료가 확인되지 않은 복구 처분을 운영자에게 넘긴다.
- 준비: `active_with_preparation()`. 큐의 첫 행동으로 실행 `EX-crashed`(`status='running'`, 입력 스냅숏은 현재 헤드, 입력 목록 없음)를 `_register_execution`으로 등록하고 저장한다. 이 엔진은 그대로 버려 충돌을 흉내 낸다.
- 실행: 새 `ResearchEngine(..., runner=ScriptedRunner()).run(max_steps=1)`.
- 단언: 게시된 `EX-crashed`의 `status`가 `'stopping'`이고 `outcome` 키가 없으며 `recovery_disposition`이 `'reconcile_local_and_remote'`다. 그 `owner_activity_id`가 가리키는 활동의 `assigned_execution_ids`에 `EX-crashed`가 있다. `runtime['recoveries']`가 비어 있지 않고, 그 안의 `EX-crashed` 처분 행은 `local_termination_confirmed=False`, `remote_termination='unknown'`, `next_owner='operator'`다.
- 대역: `ScriptedRunner`, `install_adapter_fixture`.
- 비고: 이름은 소유 활동이 "미해결(unresolved)로 표시된다"고 말하지만, 활동에 대한 단언은 실행이 여전히 그 활동에 배정되어 있다는 것뿐이다. 활동 상태 필드는 보지 않는다.

## SourceControlReceiptTests (행 132–163)

`unittest.TestCase`를 그대로 상속하고 표지·훅·도우미가 없다.

### `test_unchanged_source_control_publishes_one_replayable_receipt` (행 133–163)
- 성질: 내용이 바뀌지 않은 원천 제어는 원천 기록을 바꾸지 않은 채 적용 수령증 하나를 게시하고, 같은 요청은 그 수령증으로 재생되며, 내용이 바뀐 원천은 새 개정으로 저장된다.
- 준비: 임시 폴더에 `source.txt`(`'fixed source\n'`)를 쓰고 `research_fixtures.new_instance(repo, goal=..., workspace=root/'work', sources=[source])`로 새 저장소와 인스턴스를 만든다(공개 `initialize`). 엔진을 열고 첫 원천 기록의 `deepcopy`를 떠 둔다.
- 실행: 같은 경로로 `source` 제어를 `request_id='UC-unchanged-source'`로 보내고, `_apply_inbox(pump=False)`와 `_upkeep()`를 부른다. 같은 요청을 한 번 더 보낸다. 파일을 `'updated source\n'`로 바꿔 `UC-changed-source`로 보내고 다시 적용한다.
- 단언: 첫 전송의 `effect`가 `'pending engine processing'`이다. 수령증(`control_result`)의 `effect`가 `'applied'`, `reason`이 `'source content unchanged'`다. 원천 기록이 사본과 같다. 재전송의 `snapshot`이 수령증의 `snapshot`과 같다. 이력에서 그 요청 ID의 행은 정확히 하나다. 바뀐 원천의 `revision`이 2이고, 저장소의 그 경로를 현재 헤드에서 읽은 바이트가 파일 바이트와 같다.
- 대역: 없음.
- 비고: 실제 Git 저장소(`new_instance`는 `git_init`을 쓴다)와 공개 `initialize`를 시험마다 새로 돈다.

## ControlReceipts (행 166–343)

`unittest.TestCase`를 그대로 상속하고 표지와 설정 훅이 없다. 모든 시험이 저장소 없는 엔진 대역에서 `_publish_control_request`를 직접 부른다.

- `make_engine()` (행 167–186): `engine_fixtures.routing_engine()`을 받아 `head="parent"`, `events=[]`, `pending_events=[]`를 둔다. 정리 등록한 임시 폴더를 작업 공간으로 삼고 `max_artifact_bytes`를 1MiB로 두며 `runs/EX-work/workspace/.control`을 만든다. `store`는 `ResearchRepository`의 `create_autospec` 대역이고 `read.side_effect`가 `canonical_json({})` 두 번이다. 허가 `GR-one`(로컬, 활성, 역할 `research_work`, 만료 없음)과 `running` 실행 `EX-work`(허가 `GR-one`, 입력 묶음 `BA-input`)를 둔다. `_clock_guard`는 `usable=True`를 돌려주는 대역이고, `_save`는 호출되면 `head`를 `"published"`로 바꾸는 `create_autospec` 대역이다. 제출 의도 요청(`request_id="request-one"`, `capability="delivery-only"`, `kind="submit_intent"`, `payload={"draft_path": "draft.json"}`)과 함께 돌려준다.
- `sealed()` (행 189–195, `@staticmethod`): `submission.seal_submission`의 반환 대역. `passed=True`, `capture_eligible=True`, 빈 검사 결과, 후보 `CS-one`의 의도 기록, 네 산출물 바이트를 담는다.

### `test_receipt_requires_successful_cas_and_replay_does_not_reapply` (행 197–210)
- 성질: 게시가 성공한 제출 의도는 게시된 스냅숏을 담은 수락 수령증을 받고 실행을 결과 없는 `stopping`으로 옮기며, 같은 요청의 재전송은 다시 게시하지 않는다.
- 준비: `make_engine()`.
- 실행: `seal_submission`을 `sealed()`로 바꾼 채 `_publish_control_request(request)`. `store.read.side_effect`를 다시 채운 뒤 같은 요청으로 한 번 더 부른다.
- 단언: 수령증의 `snapshot`이 `"published"`, `state`가 `"accepted"`다. `EX-work`의 `status`가 `"stopping"`이고 `outcome` 키가 없다. 저장된 수령증의 `request`에 `capability` 키가 없다(능력 토큰은 저장되지 않는다). 두 번째 호출 뒤 `_save.call_count`가 1이다.
- 대역: `routing_engine`, `create_autospec(ResearchRepository)`, `_clock_guard`·`_save` autospec, `patch("do_math.engine.submission.seal_submission", return_value=sealed())`.
- 비고: 이름의 "CAS 성공이 필요하다"는 쪽, 곧 CAS 실패 시 수령증이 없다는 것은 이 시험이 아니라 `test_failed_cas_does_not_acknowledge_submission`이 본다.

### `test_preview_control_is_nonpublishing_and_returns_sanitized_result` (행 212–221)
- 성질: 제출 미리보기 요청은 아무것도 게시하지 않고 상태를 바꾸지 않으며 미리보기 결과만 돌려준다.
- 준비: `make_engine()`. 요청 `kind`를 `"submission_preview"`로 바꾸고, `_preview_submission`을 `{"contract_id": submission.PREVIEW_CONTRACT_ID, "passed": True, "authoritative": False}`를 돌려주는 대역으로 바꾼다. 인스턴스·런타임의 `deepcopy`를 떠 둔다.
- 실행: `_publish_control_request(request)`.
- 단언: 반환값이 정확히 `{"state": "previewed", "result": result}`다. `_save`가 호출되지 않았다. 인스턴스·런타임이 사본과 같다.
- 대역: `_preview_submission` autospec과 `make_engine`의 대역들.
- 비고: 이름은 결과가 "정제된다(sanitized)"고 말하지만, 대역이 돌려준 결과가 그대로 전달된다는 것만 단언한다. 정제 자체는 대역 뒤의 제품 `_preview_submission`에서 일어나며 이 시험의 대상이 아니다.

### `test_safety_boundary_releases_the_held_deadline_only_after_publication` (행 223–256)
- 성질: 안전 경계 보고는 관측된 진행 중 연구 호출을 모두 덮어야 수락되고, 수락이 게시된 뒤에만 자기 점검 의무의 보류된 마감을 푼다.
- 준비: `make_engine()`. 새 임시 폴더를 작업 공간으로 삼는다. `research_fixtures.Clock()`을 시계로, 규칙 `observation_rule()`과 창 설정(60초, 5초)을 가진 `ObservationTracker("EX-work", ...)`를 만든다. `observe`로 명령 실행 호출 `C`의 시작을 알리고, `write_checkpoint(..., counters={"attempts": 2})` 뒤 `tick`을 관측해 `self_check_due` 의무를 얻는다. 엔진에 추적기를 붙이고 `_transport`를 `Mock()`, `_transport_bindings`를 `{"EX-work": {}}`로 둔다. 요청을 `kind="safety_boundary"`, `payload={"inflight_calls": False, "call_ids": ["C"]}`로 바꾸고, 그 경계 보고를 `control_submit` MCP 도구 호출 `BOUNDARY`의 시작으로 추적기에 관측시킨다.
- 실행: 호출 ID가 빈 경계 보고 `uncovered`를 게시한다. `_save`가 `ValueError("CAS failed")`를 던지게 하고 원 요청을 게시한다. `_save`를 성공 대역으로 되돌리고 다시 게시한다.
- 단언: 의무의 `(deadline_offset_ms, deadline_held_offset_ms)`가 `(5000, 0)`이다(주석: 의무가 열릴 때 연구 호출 `C`가 돌고 있었으므로 마감이 보류된다). `BOUNDARY`는 추적기의 `boundary_call_ids`에 있고 `self_check_call_ids`에는 없다. `uncovered`는 `"rejected"`다. CAS 실패 게시도 `"rejected"`이고, 그 뒤 추적기 의무에 `deadline_held_offset_ms`가 남아 있다. 성공 게시는 `"accepted"`이고, 그 뒤 추적기 의무에서 `deadline_held_offset_ms`가 빠지며 `deadline_offset_ms`가 5000이고, `runtime["self_check_obligations"]`의 같은 의무도 5000이다.
- 대역: `make_engine`의 대역들, `_transport`의 `Mock`, `Clock`(시계 주입), `_save`의 `side_effect` 교체로 CAS 실패를 흉내 낸다.
- 비고: 거부 사유 메시지는 고정하지 않는다. 제품에서 `uncovered`는 `"safe boundary omits observed inflight research calls"`로 거부된다(`engine.py` 1233–1234행).

### `test_rejected_self_check_is_preserved_but_not_acknowledged_as_accepted` (행 258–280)
- 성질: 증거가 현행이 아닌 자기 점검 응답은 기록으로 보존되고 작업자에게 되먹임되지만 수령증은 거부이며, 그 사유가 실제 오류를 밝힌다.
- 준비: `make_engine()`과 새 작업 공간. `ObservationTracker`를 만들고 체크포인트·`tick`으로 `self_check_due` 의무를 얻는다. `_control_evidence_refs`를 빈 집합을 돌려주는 대역으로 바꾼다. 요청을 `kind="self_check_response"`, 페이로드를 의무 ID와 `self_check_response(obligation)`로 둔다.
- 실행: `_publish_control_request(request)`.
- 단언: `state`가 `"rejected"`이고 `reason`에 `"evidence_not_current"`가 있다(주석: 작업자가 읽는 수령증이 실제 거부 오류를 밝힌다). `runtime["self_check_responses"]`가 비어 있지 않다. 큐 길이가 1이다. `runs/EX-work/workspace/.control/observation-feedback.json`이 파일로 있다.
- 대역: `_control_evidence_refs` autospec, `Clock`, `make_engine`의 대역들.
- 비고: 큐의 행동 하나는 제품이 거부 기록의 후속이 `operational_review_due`일 때 넣는 실시간 운영 검토다(`engine.py` 1257–1260행). 시험은 행동의 역할을 단언하지 않는다.

### `test_self_check_transport_and_native_call_bind_in_both_arrival_orders` (행 282–315)
- 성질: 자기 점검 응답의 전송 요청과 작업자의 네이티브 도구 호출은 어느 쪽이 먼저 도착하든 같은 페이로드 해시와 수령증 ID로 묶이고, 의무는 답변됨이 되며, 재전송은 다시 게시하지 않는다.
- 준비: `subTest(first=...)`마다 새 `make_engine()`. 작업 공간 `runs/EX-work/workspace`에 추적기와 체크포인트를 만들고 `self_check_due` 의무를 얻는다. 요청 ID를 `"self-check-" + 의무 ID`로, 페이로드를 의무 ID와 응답으로 둔다. 같은 페이로드를 인자로 한 `control_self_check` MCP 호출 `CALL-SC`의 시작 사건을 만든다. `_control_evidence_refs`는 `{"EV-1"}`을 돌려준다.
- 실행: `first="native"`면 사건을 먼저 관측하고 게시하며, `first="receipt"`면 게시한 뒤 사건을 관측한다. 끝으로 같은 요청을 다시 게시한다.
- 단언: 수령증 `state`가 `"accepted"`다. 추적기 의무의 `status`가 `"answered"`다. `tracker.control_calls["CALL-SC"]["payload_sha256"]`이 `tracker.control_requests[요청 ID]["payload_sha256"]`과 같다. 그 요청의 `receipt_id`가 수령증의 `publication_id`와 같다. 큐가 비어 있다. 재전송 뒤 `_save.call_count`가 1이다.
- 대역: `_control_evidence_refs` autospec, `Clock`, `make_engine`의 대역들.
- 비고: `subTest` 두 경우는 `native`, `receipt`다.

### `test_self_check_failed_publication_does_not_publish_tracker_binding` (행 317–335)
- 성질: 자기 점검 응답의 게시가 실패하고 이미 게시된 수령증도 없으면, 추적기에는 요청 결합도 의무 답변도 남지 않는다.
- 준비: `make_engine()`. 기본 작업 공간(`engine.instance["workspace"]`)에 추적기와 체크포인트를 만들고 의무를 얻는다. 요청을 앞 시험과 같이 만든다. `_control_evidence_refs`는 `{"EV-1"}`, `_save`는 `OSError("publication failed")`, `store.load`는 `OSError("no committed receipt")`를 낸다.
- 실행: `_publish_control_request(request)`.
- 단언: `state`가 `"rejected"`다. `tracker.control_requests`가 `{}`이고, 의무 `status`가 `"open"`이다.
- 대역: `_save`·`store.load`의 실패 대역, `_control_evidence_refs` autospec, `Clock`.
- 비고: 제품은 추적기의 사본에 변경을 적용하고, 게시가 성공했을 때만 살아 있는 추적기에 옮긴다(`engine.py` 1210–1212·1277–1279행). 실패 시 `_reload`로 이미 게시된 수령증을 찾는데, 그 읽기도 실패하게 해 "게시 후 확인 응답만 잃은" 경우를 배제한다.

### `test_failed_cas_does_not_acknowledge_submission` (행 337–343)
- 성질: 제출 의도의 게시(CAS)가 실패하면 수령증은 거부이고 실행에 제출 수령증이 남지 않는다.
- 준비: `make_engine()`. `_save`가 `ValueError("CAS failed")`를 낸다.
- 실행: `seal_submission`을 `sealed()`로 바꾼 채 `_publish_control_request(request)`.
- 단언: `state`가 `"rejected"`이고 `EX-work`에 `submission_receipt` 키가 없다.
- 대역: `seal_submission` 패치, `_save` 실패 대역, `make_engine`의 대역들.

## SelfCheckStorageTests (행 346–406)

`unittest.TestCase`를 그대로 상속하고 표지가 없다. docstring: "엔진이 실제 저장소에 실제 저장 계약을 거쳐 저장한 자기 점검 제어". `ControlReceipts`가 엔진 대역에서 본 것을 실제 저장 경로에서 다시 본다.

- `setUp` (행 349–355): `engine_fixtures.start_submission_history(self)`. `state_fixtures.start_active_copy`로 2단 템플릿(`ACTIVE_CONFIG`)의 사본을 만들고(`FixtureAdapter` 패치 포함), 실행 `EX-history`(역할 `maintenance`, `running`)를 등록한다. 입력 묶음 `BA-history-input`의 프롬프트·검사 문맥·스키마를 게시하고, 작업 공간에 제출 도구를 설치하며, `ControlTransport`로 결합(`self.binding`)을 발급한다. 이어 `Clock()`과 규칙 `observation_rule()`을 가진 `ObservationTracker("EX-history", self.workspace, ...)`를 만들어 `self.engine._trackers`에 붙인다.
- `due()` (행 357–359): 체크포인트(`attempts=2`)를 쓰고 `tick`을 관측해 `self_check_due` 의무를 돌려준다.

### `test_self_check_response_and_its_rule_update_are_saved` (행 361–375)
- 성질: 규칙 개정 제안을 담은 자기 점검 응답은 수락되고, 응답 기록과 규칙 갱신과 의무 답변이 실제 저장소에 저장된다.
- 준비: 클래스 절의 `setUp`과 `due()`. 응답에 `rule_proposal`(`current_revision=0`, 규칙 `observation_rule(repeat_interval=2)`)을 더한다. `_control_evidence_refs`는 `{"EV-1"}`을 돌려준다. 요청은 결합에 요청 ID·종류·페이로드를 더한 것이다.
- 실행: `self.engine._publish_control_request(request)` 뒤 `self.engine.store.load()`.
- 단언: 수령증 `state`가 `"accepted"`다. 저장된 첫 `self_check_responses` 기록의 `kind`가 `"self_check_received"`, 그 `rule_update.kind`가 `"observation_rules_accepted"`다. 저장된 의무 `status`가 `"answered"`다.
- 대역: `_control_evidence_refs` autospec, `Clock`.

### `test_self_check_response_may_cite_the_executions_own_checkpoint` (행 377–390)
- 성질: 자기 점검 응답은 실행 자신의 체크포인트 파일(`workspace:checkpoint.json`)을 증거로 인용할 수 있다.
- 준비: `setUp`의 추적기를 필요 증거가 `["workspace:checkpoint.json"]`인 규칙의 추적기로 바꾼다. `due()`로 의무를 얻는다. 이 시험은 `_control_evidence_refs`를 대역으로 바꾸지 않는다.
- 실행: `_publish_control_request(request)` 뒤 `store.load()`.
- 단언: 수령증 `state`가 `"accepted"`이고, 저장된 응답 기록의 `kind`가 `"self_check_received"`다.
- 대역: `Clock`. 증거 판정은 실제 제품 `_control_evidence_refs`다.

### `test_safety_boundary_is_saved_and_releases_the_held_deadline` (행 392–406)
- 성질: 안전 경계는 실제 저장소에 저장되며 보류된 마감을 풀고, 새 엔진으로 재전송하면 다시 적용하지 않고 게시된 수령증을 돌려준다.
- 준비: `setUp` 뒤 명령 실행 호출 `C`의 시작을 관측하고 `due()`로 의무를 얻는다. 요청은 `request_id="boundary-one"`, `kind="safety_boundary"`, `payload={"inflight_calls": False, "call_ids": ["C"]}`다.
- 실행: `_publish_control_request(request)`, `store.load()`, 그리고 새 `ResearchEngine(self.repo, self.identifier)._publish_control_request(request)`.
- 단언: 의무의 `(deadline_offset_ms, deadline_held_offset_ms)`가 `(5000, 0)`이다. 수령증이 `"accepted"`다. 저장된 의무에 `deadline_held_offset_ms`가 없고 `deadline_offset_ms`가 5000이다. 재전송의 `(state, publication_id)`가 `("accepted", 원 수령증의 publication_id)`다(주석: 재생은 게시된 수령증을 돌려줄 뿐 경계를 다시 적용하지 않는다).
- 대역: `Clock`.

## UserControlIdentity (행 426–496)

`unittest.TestCase`를 그대로 상속하고 표지·훅·도우미가 없다.

### `test_same_request_replays_before_changed_state_admission` (행 427–442)
- 성질: 같은 요청 ID의 같은 요청은 인스턴스 상태가 바뀐 뒤에도 상태 검사보다 먼저 재생되고, 같은 ID에 다른 내용을 실으면 거부된다.
- 준비: 임시 폴더. `routing_engine()`의 작업 공간을 `root/"work"`로 두고, `load`가 `("snapshot", instance, runtime)`을 돌려주는 `ResearchRepository` autospec을 `do_math.engine.ResearchRepository`에 건다.
- 실행: `control(root, "RI-test", "request", config={"role": "maintenance"}, request_id="UC-explicit")`. 런타임 상태를 `"closed"`로 바꾸고 같은 호출을 반복한다. 끝으로 `text="changed"`를 더해 같은 ID로 부른다.
- 단언: 재전송의 `request_id`가 첫 호출과 같고 `replayed`가 참이다. 받은함 `work/control/RI-test`의 `*.json`이 하나다. 내용이 다른 호출은 메시지 조각 `"different"`로 고정된 `ValueError`다.
- 대역: `routing_engine`, `patch("do_math.engine.ResearchRepository", return_value=store)`.

### `test_git_replay_keeps_original_outcome_and_snapshot_after_close` (행 445–462)
- 성질: 실제 Git 상태에서도 같은 `pause`의 재전송은 인스턴스가 닫힌 뒤에 원래 결과와 원래 스냅숏을 돌려주며, 요청 ID는 `control_request_id`로 결정된다.
- 준비: 임시 폴더에 `engine_fixtures.initialized(root/"repo", goal="Control replay", workspace=root/"work")`로 새 저장소와 인스턴스를 만든다(공개 `initialize`).
- 실행: `pause`(`text="pause once"`)를 보내고 처리한 뒤 `control_result`를 원래 결과로 읽는다. `close`를 보내 처리한다. 같은 `pause`를 다시 보낸다.
- 단언: 원래 결과의 `status`가 `"paused"`다. 닫힌 뒤 런타임 상태가 `"closed"`다. 재전송의 `replayed`가 참이고, 원래 결과의 키만 뽑은 재전송 값이 원래 결과와 같다. 엔진 헤드가 원래 결과의 `snapshot`과 다르다(닫기 게시로 헤드가 옮겨갔는데도 옛 스냅숏을 돌려준다). 첫 요청 ID가 `control_request_id(identifier, "pause", text="pause once")`와 같다.
- 대역: 없음.
- 비고: 실제 Git 저장소와 공개 `initialize`를 시험 안에서 돈다.

### `test_default_pause_after_resume_is_a_new_request_that_pauses` (행 464–471)
- 성질: 재개 뒤에 같은 내용으로 보낸 기본 `pause`는 새 요청이 되어 실제로 다시 일시정지한다.
- 준비: `paused_then_resumed(text="hold")`.
- 실행: 같은 `pause`(`text="hold"`)를 다시 보내고 새 엔진의 `process_controls()`.
- 단언: 새 요청 ID가 첫 `pause`의 ID와 다르고, 반환값에 `replayed` 키가 없다. 처리 뒤 상태가 `"paused"`다.
- 대역: 없음.
- 비고: 제품은 반대 제어(`pause`/`resume`) 뒤의 요청 ID를 마지막 반대 제어에 묶어 계산한다(`engine.py` 275–279행의 `after`).

### `test_explicit_idempotency_key_keeps_its_request_id_and_replays_after_resume` (행 473–481)
- 성질: 명시적 멱등 키를 준 `pause`는 재개 뒤에도 같은 요청 ID를 유지해 재생되고 다시 일시정지하지 않는다.
- 준비: `paused_then_resumed(text="hold", idempotency_key="hold-once")`.
- 실행: 같은 인자로 `pause`를 다시 보낸다.
- 단언: 요청 ID가 첫 `pause`와 같고, `control_request_id(identifier, "pause", text="hold", idempotency_key="hold-once")`와도 같다. `replayed`가 참이다. 새 엔진의 상태가 `"paused"`가 아니다.
- 대역: 없음.
- 비고: 바로 앞 시험과 짝을 이룬다. 차이는 멱등 키 하나이고, 결과는 새 요청 대 재생으로 갈린다.

### `test_normalized_source_has_one_identity_and_rejects_wrong_bytes` (행 483–496)
- 성질: 정규화된 원천 명세의 요청 ID는 그 명세로 계산한 `control_request_id`와 같고, 선언한 크기가 본문과 다르면 거부된다.
- 준비: `routing_engine()`과 `ResearchRepository` autospec(앞 시험과 같은 방식). 원천 명세는 `name="source.txt"`, 본문 `b"original"`의 base64, 그 SHA-256, `bytes=8`이다.
- 실행: `control(root, "RI-test", "source", config=spec, idempotency_key="source-once")`, 이어 `bytes=7`로 바꾼 명세의 `control`.
- 단언: 첫 요청 ID가 `control_request_id("RI-test", "source", config=spec, idempotency_key="source-once")`와 같다. 둘째 호출은 메시지 조각 `"hash or size"`로 고정된 `ValueError`다.
- 대역: `routing_engine`, `patch("do_math.engine.ResearchRepository", ...)`.

## ControlQueueConnections (행 499–527)

`unittest.TestCase`를 그대로 상속하고 표지와 설정 훅이 없다.

- `engine(request)` (행 500–509): `routing_engine()`에 `head="parent"`, `DEFAULT_CONFIG` 사본 설정, `lifecycle={"state": "active"}`, 빈 `processed_controls`를 둔다. `_inbox`는 `[request]`를 돌려주는 autospec, `_save`는 autospec이다. 확장 제어 처리기 넷(`_review_recovery_control`, `_knowledge_io_control`, `_academic_control`, `_apply_extended_control`)은 `False`를 돌려주는 autospec, 후속 정비 넷(`_schedule_operational_reviews`, `_retry_submission_publications`, `_retry_impact_reviews`, `_run_pending_operational_repairs`)은 아무것도 하지 않는 autospec이다. 제어 적용의 핵심 경로만 남긴 엔진이다.

### `test_every_queued_user_control_has_a_stable_queue_identity` (행 511–520)
- 성질: 큐에 행동을 넣는 사용자 제어는 `AC-` 행동 ID를 받고, 그 ID가 계보 ID(`lineage_id`)와 같다.
- 준비: `subTest(action=...)`마다 `engine({"id": "UC-one", "action": action, "config": config, "text": "Explicit request"})`. 경우는 `("input", {})`와 `("request", {"role": "maintenance"})`다.
- 실행: `engine._controls()`.
- 단언: 큐 길이가 1이고, 그 행동의 `id`가 `"AC-"`로 시작하며, `id`가 `lineage_id`와 같다.
- 대역: `engine()` 도우미의 autospec들.
- 비고: 원문 주석(512행)은 `resume`이 수명주기만 되돌리고 활동을 큐에 넣지 않으므로(`lifecycle_engine._resume_lifecycle`) 경우에서 빠진다고 적는다.

### `test_distinct_approved_cleanup_scopes_are_not_merged` (행 522–527)
- 성질: 서로 다른 요청이 승인한 정리 범위는 한 유지보수 행동으로 합쳐지지 않는다.
- 준비: `routing_engine()`(도우미 `engine`은 쓰지 않는다).
- 실행: `_enqueue("maintenance", requested_by="UC-one", cleanup_execution_ids=["EX-one"])`와 `requested_by="UC-two"`, `["EX-two"]`의 두 번째 호출.
- 단언: 큐 길이가 2이고, 각 행의 `cleanup_execution_ids`가 `[["EX-one"], ["EX-two"]]` 순서다.
- 대역: `routing_engine`.

## MaintenanceFenceTests (행 530–544)

`unittest.TestCase`를 그대로 상속하고 표지·훅·도우미가 없다.

### `test_quiescence_does_not_release_unknown_execution_or_user_pause` (행 531–544)
- 성질: 유지보수 울타리는 상태를 모르는 실행이 남아 있으면 해제되지 않고, 해제되어도 사용자 일시정지를 지우지 않는다.
- 준비: 런타임 사전. `starting` 상태의 실행 `EX-one`, 빈 예약, 사용자 일시정지 `{'request_id': 'UC-user'}`, 상태 `paused`. 운영자 `quiesce` 요청 `UC-maint`와, 그 울타리를 이름으로 대는 `release_quiesce` 요청 `UC-release`.
- 실행: `maintenance_gate.apply_control(runtime, quiesce)`, `settle(runtime)`, 해제 시도, `EX-one`을 `ended`로 바꾼 뒤 `settle`, 해제 재시도.
- 단언: `quiesce` 적용이 `True`를 돌려준다. 첫 `settle` 뒤 울타리 `state`가 `'blocked'`다. 첫 해제는 `ValueError`다(유형만 확인). 실행이 끝난 뒤 해제는 성공하고, `user_pause`가 `{'request_id': 'UC-user'}` 그대로이며 상태가 `'paused'`다.
- 대역: 없음.
- 비고: 1단(순수 함수). 제품의 첫 해제 거부 사유는 `'maintenance has not reached its termination barrier'`다(`maintenance_gate.py` 22–23행). 제품 docstring은 "유지보수 울타리는 실행을 비우되 사용자 일시정지가 되지 않는다"고 적는다.

## PublicMaintenanceFenceTests (행 547–567)

`unittest.TestCase`를 그대로 상속하고 표지·훅·도우미가 없다.

### `test_public_maintenance_fence_survives_restart_and_preserves_user_pause` (행 548–567)
- 성질: 공개 CLI로 세운 유지보수 울타리는 게시된 상태로 남아 새 엔진이 읽고 엔진 시작을 막으며, 해제되어도 그 사이의 사용자 일시정지를 보존한다.
- 준비: `state_fixtures.start_active_copy(self)`(2단 템플릿 사본, `FixtureAdapter` 패치).
- 실행: 프로세스 안 CLI `cli_result(self.root, 'quiesce', ..., '--origin', 'operator', '--reason', ...)`. 새 엔진을 열어 울타리를 읽고 `engine_start_guard(repo, identifier, 작업 공간, status=engine.status())`를 부른다. 이어 CLI `pause`(`--origin user`, 사유 `'separate user pause'`)와 `release-quiesce`(`--origin operator`, `--fence` 울타리 ID)를 부르고, 또 새 엔진을 연다.
- 단언: 첫 새 엔진의 울타리 `state`가 `'quiescent'`이고 `request_id`가 CLI 결과의 `request_id`와 같다. 시작 가드의 `outcome`이 `'startable'`이 아니다. 해제 뒤 새 엔진의 런타임에 `maintenance_fence` 키가 없고, 상태가 `'paused'`이며, `user_pause.reason`이 `'separate user pause'`다.
- 대역: `FixtureAdapter` 패치(`start_active_copy`). CLI는 `cli_result`(내부 `run_cli`)로 프로세스 안에서 부른다.
- 비고: 이름의 "재시작"은 실제 프로세스 재시작이 아니라 새 `ResearchEngine` 객체가 게시된 상태를 다시 읽는 것이다.

## 관계

- 같은 제품 기능의 다른 층: `test_control_shapes`는 제어의 모양 경계를, 이 모듈은 상태 전이와 식별을 본다. 둘은 `ControlTransitionTests.test_stale_request_...`(상태가 낡은 요청)과 `test_control_shapes.ControlShapeBoundaryTests.test_receiver_rejects_bad_payload_...`(모양이 틀린 요청)에서 "한 번 소비되고 뒤를 막지 않는다"는 같은 성질을 서로 다른 원인으로 확인한다. `_publish_control_request`는 `test_submission_flow`도 부르며, 전송 계층 자체(요청·수령증 파일, MCP 자식)는 `test_control_transport`가 다룬다. `control_request_id`는 `test_cli`에서도, `maintenance_gate`와 `quiesce`는 `test_trust_continuation`, `test_session_scheduler`에서도 쓰인다. 관측 추적기의 규칙·의무 자체는 `test_live_observation`, `test_observations`가 다룬다.
- 픽스처 의존: `engine_fixtures`(`routing_engine`, `initialized`, `initialized_instance`, `start_submission_history`), `research_fixtures`(`restore_template`, `install_adapter_fixture`, `new_instance`, 관측 도우미 `observe`·`write_checkpoint`·`Clock`·`observation_rule`·`self_check_response`, CLI 도우미 `run_cli`·`cli_result`), `state_fixtures`(`active_instance`, `start_active_copy`), `runner_fixtures.ScriptedRunner`.
- 이 모듈에만 있는 도우미: 모듈 함수 `paused_then_resumed`, 클래스 도우미 `ControlTransitionTests.start`·`initializing`·`active_with_preparation`·`update`, `ControlReceipts.make_engine`·`sealed`, `SelfCheckStorageTests.due`, `ControlQueueConnections.engine`.
- 겹침과 보완: 안전 경계는 `ControlReceipts.test_safety_boundary_..._only_after_publication`(엔진 대역, CAS 실패 포함)과 `SelfCheckStorageTests.test_safety_boundary_is_saved_...`(실제 저장소, 재생 포함)가 두 층에서 본다. 자기 점검 응답도 `ControlReceipts`(대역)와 `SelfCheckStorageTests`(실제 저장)로 나뉜다. 유지보수 울타리는 순수 함수 층(`MaintenanceFenceTests`)과 공개 CLI 층(`PublicMaintenanceFenceTests`)에서 본다.
- 실제 외부 자원: 실제 Git 저장소를 쓰는 시험은 `ControlTransitionTests`, `SourceControlReceiptTests`, `SelfCheckStorageTests`, `UserControlIdentity`의 Git 세 시험(`test_git_replay_...`, 그리고 `paused_then_resumed`로 초기화 템플릿을 복원하는 `test_default_pause_...`와 `test_explicit_idempotency_key_...`), `PublicMaintenanceFenceTests`다. `ControlTransitionTests`에서 `run`을 쓰는 두 시험은 `ScriptedRunner`를 러너로 준다. `ScriptedRunner`는 역할 호출마다 실제 로컬 Windows Job을 띄우므로(`research_fixtures.local_job_runner`), 준비된 과제가 생길 때까지 엔진을 모는 `test_stale_request_...`은 실제 Job을 쓴다. `test_crash_...`의 한 단계가 새 호출을 시작하는지는 단언하지 않는다. 자식 프로세스 CLI는 없다(`run_cli`는 프로세스 안).

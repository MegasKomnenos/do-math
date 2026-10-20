# test_provider_recovery

| 항목 | 값 |
|---|---|
| 조각 | `lifecycle` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_provider_recovery.py` (184행) |
| 클래스 / 테스트 | 3 / 4 (`QuotaRunner`는 시험 클래스가 아닌 러너 대역) |
| 시험 대상 제품 코드 | `do_math/provider_engine.py`의 엔진 메서드 `_publish_provider_result`, `_schedule_provider_wake`, `_requeue_provider_action`, 그리고 같은 엔진의 `_provider_outcome`, `_provider_status`, `_session_slots`, `run`, `_enqueue`; `do_math/scheduled_operator.py`의 `wake`, `hold`, `check`, `reconcile_wake`, `supervision_facts`, `schedule`(대역으로 대체), `read_status`·`engine_start_guard`(한 곳에서 대역); `do_math/session_slots.py`의 `SessionSlots`(`provider_snapshot`), 시각 `time.time`; `do_math/provider_wait.py`의 `epoch_seconds` |
| 사용하는 픽스처 모듈 | `research_fixtures`: `install_adapter_fixture`, `local_job_runner`, `producer_result`, `restore_template`, `send_control`, `bare_engine`, `git_init`; `runner_fixtures`: `common`, `context_from`, `ScriptedRunner`; `state_fixtures`: `active_instance`; `provider_fixtures`: `PROVIDER_LIMIT_FAILURE`, `admit`, `finish`, `provider_repository`, `report` |
| 격리 표지 | 없음. 다만 `QuotaRunner.run`은 `local_job_runner`로 모델 호출마다 실제 Windows Job 자식 프로세스를 띄운다 |
| 시작 상태 | `RecoveryTests`: 2단(`restore_template(state_fixtures.active_instance, config=...)`, 시험마다 설정이 달라 서로 다른 템플릿). `ProviderConnections`: 임시 디렉터리의 새 Git 저장소에 `provider_fixtures.provider_repository`로 준비 상태 인스턴스 하나를 직접 쓴 뒤 `bare_engine`으로 적재한 것 |

## 목적

모듈 docstring은 "공급자 관문은 시각을 보고하는 데 그치지 않고 엔진의 복구를 바꿔야 한다"고 밝힌다.

공급자 한도(provider limit)는 모델 공급자가 사용량 한도로 호출을 거부한 상황이다. 제품은 그 공급자에 대한 대기(`provider_waits`, 재시도 시각 `retry_at`과 세대 `generation`)를 기록하고, 한도에 걸린 행동을 `waiting_actions`로 옮기지 않고 관문 대기(`dispatch_wait.kind == 'provider_limit'`)를 단 채 대기열에 되돌린다(`_requeue_provider_action`의 docstring: "공급자 한도에 걸린 요청은 다른 수락 대기처럼 대기열에서 관문을 기다린다"). 결과는 먼저 Git에 공개하고, 그다음 운영자 예약 작업에 한 번짜리 깨우기(wake)를 예약한다(`_publish_provider_result`의 docstring: "스케줄러가 Git 원장을 다시 읽기 전에 결과 처분을 공개한다"). 깨우기는 모델을 부르지 않고 엔진 진입점만 깨운다(`scheduled_operator.wake`의 docstring: "No model ping").

이 모듈은 그 흐름의 네 성질을 검사한다. 한도에 걸린 원래 행동이 진단 호출 없이 보존되었다가 재시도 시각 뒤에 이전 출력 파일과 함께 재개되는 것, 깨우기가 운영자 보류(HOLD)와 사용자 일시정지를 존중하는 것, 결과 관찰만으로는 예약이 일어나지 않는 것, 저장된 대기가 깨우기 예약을 이끌고 예약 실패가 복구 가능한 것이다.

## 모듈 수준 요소

- 행 10: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 조건 없이 넣는다.
- 행 11–15: 제품 `scheduled_operator`, `ResearchEngine`과 픽스처 `install_adapter_fixture`, `local_job_runner`, `producer_result`, `restore_template`, `common`, `context_from`, `ScriptedRunner`, `active_instance`를 가져온다. `provider_fixtures`와 나머지는 시험 안에서 지역 import한다.
- 행 183–184: 직접 실행하면 `unittest.main()`.

모듈 함수와 모듈 상수는 없다.

## QuotaRunner (행 18–33)

기반 클래스가 없는 일반 클래스다. 시험을 담지 않으며, `RecoveryTests.test_quota_preserves_original_action_without_diagnostic_calls_then_restores_files`가 쓰는 러너 대역이다.

- `__init__()` (행 19–20): 받은 문맥을 적을 `calls` 목록을 만든다.
- `run(**arguments)` (행 23–33): `research_fixtures.local_job_runner`로 장식되어 있어 호출마다 실제 Windows Job 자식 프로세스(`python -c "import time; time.sleep(600)"`)를 띄워 `on_started`에 그 정체를 알리고, 호출이 끝나면 종료한다(종료 확인 상한 10초). 본문은 프롬프트에서 `context_from`으로 문맥을 읽어 `calls`에 적고 `on_started({'fixture': 'quota model'})`을 부른다. 첫 호출이면 작업공간에 `partial.txt`('retained evidence')를 남기고 공급자 한도 실패(`status='failed'`, `error_kind='provider_limit'`, `failure.provider='claude'`, `retry_at=None`, `evidence_ref='stdout.jsonl'`)를 `producer_result`로 돌려준다. 이후 호출은 그 역할의 `common(role)` 출력으로 완료 결과를 돌려준다.

## RecoveryTests (행 36–98)

`unittest.TestCase`를 그대로 상속한다. 클래스 표지와 속성은 없다.

- `setUp` (행 37–38): `research_fixtures.install_adapter_fixture(self)`. `do_math.initialization.adapter_for`를 호출마다 `FixtureAdapter`를 돌려주는 대역으로 바꾸고 시험 끝에 되돌린다. 주석은 없지만 픽스처 docstring은 "외부 관찰만 바꾸고 증거 해싱과 능력 관문은 유지한다"고 밝힌다. 시작 상태는 각 시험이 직접 `restore_template`로 받는다.

### `test_quota_preserves_original_action_without_diagnostic_calls_then_restores_files` (행 40–78)
- 성질: 모델 호출이 공급자 한도로 실패하면 원래 행동이 관문 대기를 단 채 대기열에 보존되고, 진단용 운영 검토 호출이나 질문이 생기지 않으며, 재시도 시각이 지나면 그 행동이 이전 출력 파일을 넘겨받아 재개된다.
- 준비: 2단 템플릿. 설정은 세 등급 모두 `claude-opus-5`, `scholarly_enabled=False`, `operator_enabled=False`, `tool_review_window_seconds=60`, `self_check_response_window_seconds=5`, `plan_settle_seconds=1`, 작업 슬롯 `{'claude-opus-5': 1}`, `lean_command=['test-lean']`. 엔진은 `ResearchEngine(root/'repository', instance_id, runner=QuotaRunner())`. `_enqueue('research_preparation', reason=...)`와 `_save()`로 AI 행동 하나를 대기열에 둔다. 주석(행 41–42): 시험 대상은 러너의 공급자 실패부터이며 활성화는 검사하지 않는다. 대기 중인 AI 행동 하나가 다른 계획이 공급자 탐침(probe)을 차지하지 못하게 한다.
- 실행: `engine.run(max_steps=2)`. 이어 `do_math.session_slots.time.time`을 현재 시각 + 301초로 패치하고 `run(max_steps=1)`을 최대 세 번, 원래 행동 ID를 가진 문맥이 첫 호출 뒤 `calls`에 나타나면 멈춘다.
- 단언: 첫 실행 뒤 러너 호출이 하나다. `operational_review` 역할의 실행이 없다. 대기열에서 `recovery.reason == 'provider admission retry'`인 행동이 하나이고, 그 `dispatch_wait`가 `kind='provider_limit'`, `provider='claude'`이며, 그 ID가 `waiting_actions`에 없다. `questions`가 비어 있다. 시각을 넘긴 뒤 원래 행동을 가진 재개 문맥이 정확히 하나이고, 그 `previous_output_files`에 `path == 'partial.txt'`인 행이 있다. 여전히 `operational_review` 실행이 없고, 원래 행동이 `provider_limit` 관문 대기를 단 채 대기열에 남아 있지 않다.
- 대역: `QuotaRunner`, `adapter_for` 대역(`setUp`), `patch('do_math.session_slots.time.time', return_value=current + 301)`로 시각 주입.
- 비고: 실제 외부 자원은 `local_job_runner`가 띄우는 Windows Job 자식 프로세스다(호출이 둘 이상이므로 둘 이상). 재개 탐색은 최대 세 단계로 제한된 반복이다. 주석(행 66–67)이 이유를 밝힌다: 이미 대기 중인 독립 계획이 성공한 공급자 탐침을 먼저 쓸 수 있으므로, 호출 순번이 아니라 보존된 행동 ID를 따라간다. 301초는 제품의 재시도 시각이 그 안에 온다는 전제이며, 그 값의 근거는 원문에 적혀 있지 않다.

### `test_wake_keeps_hold_and_user_pause_and_only_requests_engine` (행 80–98)
- 성질: 운영자의 깨우기는 모델을 부르지 않고 엔진 시작만 예약하며, 사용자 일시정지나 운영자 보류가 있으면 아무것도 예약하지 않는다.
- 준비: 2단 템플릿(설정 `operator_enabled=False`, `scholarly_enabled=False`, `lean_command=['test-lean']`, 관찰 창 60/5). `ResearchEngine(repo, instance_id, runner=ScriptedRunner())`, 작업공간 경로.
- 실행: `scheduled_operator.schedule`을 `{}`를 돌려주는 대역으로 바꾼 채, `wake`를 세 번 부른다. 처음은 그대로, 둘째는 `research_fixtures.send_control(engine, 'pause', text=...)`로 공개 일시정지를 적용한 뒤, 셋째는 `scheduled_operator.hold(workspace, reason='Explicit temporary HOLD fixture')` 뒤.
- 단언: 첫 `wake`의 `outcome == 'engine_requested'`이고 `schedule`이 `('start-engine', repository=repo, instance=..., workspace=workspace)`로 정확히 한 번 불렸다. 둘째 `outcome == 'paused'`, 셋째 `outcome == 'held'`이며 두 경우 모두 `schedule`이 불리지 않았다.
- 대역: `patch.object(scheduled_operator, 'schedule', return_value={})`, `adapter_for` 대역. `ScriptedRunner`는 엔진 생성에만 쓰이고 호출되지 않는다.
- 비고: 이름의 "keeps hold and user pause"는 깨우기가 두 상태를 풀지 않는다는 뜻이다. 시험은 결과 값과 예약 부재를 보고, 보류 파일이나 일시정지 상태가 그대로 남았는지는 따로 단언하지 않는다.

## ProviderConnections (행 101–180)

`unittest.TestCase`를 그대로 상속한다. 표지·훅·도우미·클래스 속성이 없다. 두 시험 모두 `self.enterContext(tempfile.TemporaryDirectory())`로 임시 디렉터리를 만들고, `git_init(root)`로 빈 Git 저장소를 만든 뒤 `provider_fixtures.provider_repository(root)`로 준비(`ready`) 상태 인스턴스 하나를 초기 저장한다. 이 인스턴스는 `DEFAULT_CONFIG`에 학술 검색을 끄고 세 등급 모두 픽스처 공급자 모델, 작업 슬롯 3을 둔 설정과 그 실행 프로필을 갖는다. 엔진은 `bare_engine(store=그 저장소)`이고 `store.load()`로 헤드·인스턴스·런타임을 싣는다. 제품 `initialize`나 활성화를 거치지 않은 최소 상태다.

`provider_fixtures`의 도우미는 다음과 같다. `admit(slots, instance, runtime, identifier, current=...)`는 역할의 마지막 프로필로 실행을 만들어 슬롯을 얻고 활동에 배정한다. `report(slots, instance, identifier, current, failure)`는 합성 러너 결과(공급자 한도 실패)를 `slots.provider_result_from_run`에 적용해 관문을 돌려준다. `finish(slots, runtime, identifier, current, close_activity=False)`는 슬롯을 놓고 실행을 `start_failed`로 끝낸다. `PROVIDER_LIMIT_FAILURE`는 `provider='claude'`, `retry_at=None`, 증거 `synthetic-provider-limit.json`인 실패 사전이다.

### `test_result_observation_has_no_prepublication_schedule_effect` (행 102–111)
- 성질: 공급자 결과의 관찰(`_provider_outcome`)은 공개 전에 깨우기 예약이라는 외부 효과를 일으키지 않는다.
- 준비: 클래스 절의 최소 Git 상태. `admit(engine._session_slots(), instance, runtime, 'EX-limit')`이 참임을 단언한다.
- 실행: `_schedule_provider_wake`를 `create_autospec` 대역으로 바꾸고 `engine._provider_outcome('EX-limit', {'status': 'failed', 'error_kind': 'provider_limit', 'failure': PROVIDER_LIMIT_FAILURE})`.
- 단언: `_schedule_provider_wake`가 불리지 않았다.
- 대역: `_schedule_provider_wake` 대역.

### `test_saved_wait_drives_wake_and_schedule_failure_is_recoverable` (행 113–180)
- 성질: 공개된 공급자 대기가 깨우기 예약을 이끈다. 예약이 실패해도 대기는 Git에 남고 다음 공개나 점검에서 한 번만 다시 예약되며, 예약은 대기와 대기열이 Git에 저장된 뒤에만 일어나고, 저장이 실패하면 예약하지 않으며, 운영자 보류 중에는 예약을 취소한다.
- 준비: 클래스 절의 최소 Git 상태에 `operator_enabled=True`, `tasks={}`(주석: 제품 저장이 읽는 과제 표를 이 최소 상태가 빠뜨렸다). `admit(..., 'EX-limit', current=time.time())`이 참임을 단언한다. 주석(행 127): 관찰은 공개와 분리되며 외부 효과는 Git을 읽는다. `report(...)`로 관문 `gate`를 얻고 `finish(..., close_activity=False)`. 행동 `AC-held`(`research_work`, 마지막 프로필)를 대기열에 두고 `_requeue_provider_action(action, 'EX-limit', gate)`.
- 실행과 단언: 여러 단계로 나뉜다.
  1. 재배치 뒤 대기열 마지막 행동의 `dispatch_wait.kind == 'provider_limit'`.
  2. 지역 함수 `saved_status()`는 저장소에서 다시 읽은 상태로 `supervision_facts`와 `SessionSlots(persisted, instance, observer=True).provider_snapshot()`을 합친 상태 보고를 만든다. 지역 함수 `schedule(command, **kwargs)`는 호출을 `calls`에 적고, 매번 저장소에서 다시 읽은 런타임에서 `provider_waits['PW-claude'].retry_at`이 `epoch_seconds(gate['retry_at'])`와 같고 대기열에 `AC-held`가 있음을 단언한다. 곧 예약은 대기와 대기열이 Git에 공개된 뒤에만 일어난다. `status` 명령에는 기억해 둔 깨우기를, `schedule-wake`에는 그 깨우기(`description=wake_key`, `next_run=wake_at`, `state='Ready'`)를 기억시킨다.
  3. `schedule`이 `OSError('scheduler unavailable')`를 던지게 하고 `_publish_provider_result()`. 저장된 `provider_wake.status == 'failed'`, 대기의 `retry_at`은 그대로다.
  4. `schedule`을 지역 대역으로, `read_status`를 `saved_status()` 값으로, `engine_start_guard`를 `{'outcome': 'provider_waiting'}`으로 바꾸고 `scheduled_operator.check(root, 인스턴스, root)`. 결과 `provider_wake.status == 'scheduled'`. 이어 같은 `schedule` 대역 아래에서 `_publish_provider_result()`를 다시 부른다. `schedule-wake` 호출이 모두 합쳐 정확히 한 번이고, 그 `wake_at`이 `gate['retry_at']`, `wake_key`가 `'claude:' + str(gate['generation'])`이다. 점검이 이미 예약했으므로 뒤의 공개는 다시 예약하지 않는다.
  5. `engine._save`가 `OSError('Git failed')`를 던지게 하고 `schedule`을 빈 대역으로 둔 채 `_publish_provider_result()`. `OSError`를 메시지 `'Git failed'`로 던지고 `schedule`이 불리지 않았다.
  6. `schedule`을 지역 대역으로 두고 `scheduled_operator.hold(root, reason='Synthetic HOLD')`. `check`의 `outcome == 'held'`이고 `calls`가 늘지 않았다. `reconcile_wake(root, 인스턴스, root, facts={'status': 'ready'}, providers=engine._provider_status()['providers'])`의 `status == 'held'`이고 마지막 호출이 `'cancel-wake'`다.
- 단언: 위 여섯 단계에 적은 것을 요약하면 다음과 같다. 재배치된 행동이 `provider_limit` 관문 대기를 단다. 예약 대역은 호출될 때마다 대기와 대기열이 이미 Git에 저장되었음을 확인한다. 예약 실패는 `provider_wake.status == 'failed'`로 저장되고 대기는 남는다. 점검이 예약을 복구하며 `schedule-wake`는 전체에서 한 번, 시각과 키가 관문의 것과 같다. 저장 실패 시 예약하지 않는다. 보류 중에는 점검이 아무것도 부르지 않고 조정이 `cancel-wake`로 끝난다.
- 대역: `scheduled_operator.schedule`(실패 대역, 기록 대역, 빈 대역), `scheduled_operator.read_status`, `scheduled_operator.engine_start_guard`, `engine._save`(실패 대역).
- 비고: 작업공간이 저장소 루트와 같은 `root`다(`provider_repository`가 `workspace=str(root)`로 인스턴스를 만든다). 보류 표지와 깨우기 등록 파일은 그 작업공간의 운영자 폴더에 실제로 쓰인다. 제품 `reconcile_wake`는 이전 등록(`wake-registration.json`)이 있고 보류 중이면 `cancel_wake`를 부르며, 그 호출이 `schedule` 대역에 `'cancel-wake'`로 기록된 것으로 읽힌다.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈: 공급자 대기와 슬롯의 순수 산술은 `provider_fixtures`를 쓰는 다른 모듈(세션 슬롯·공급자 대기 영역)이, 운영자 예약 작업의 설치·상태·복구는 `scheduled_operator`를 검사하는 운영자 모듈들이 다룬다. 입력 초과와 함께 공급자 수락이 미뤄지는 경우는 `test_input_recovery.InputRecoveryPublicTests.test_resolved_retry_marker_survives_provider_deferral_and_repreparation`이 `_provider_admit` 대역으로 본다.
- 픽스처 의존: `research_fixtures.install_adapter_fixture`(`setUp`), `local_job_runner`·`producer_result`(`QuotaRunner`), `restore_template`·`state_fixtures.active_instance`(2단), `send_control`(공개 일시정지), `bare_engine`·`git_init`(최소 Git 상태); `runner_fixtures.common`, `context_from`, `ScriptedRunner`; `provider_fixtures.PROVIDER_LIMIT_FAILURE`, `admit`, `finish`, `provider_repository`, `report`.
- 이 모듈에만 있는 도우미: 러너 대역 `QuotaRunner`, 마지막 시험의 지역 함수 `saved_status`와 `schedule`.
- 겹침과 보완: `RecoveryTests`는 실제 엔진 구동(2단, 러너 호출, 시각 주입)으로 행동 보존과 재개를, `ProviderConnections`는 최소 Git 상태에서 공개와 예약의 순서, 실패 복구, 보류를 본다. 깨우기의 보류 존중은 `test_wake_keeps_hold_and_user_pause_and_only_requests_engine`(`wake`)와 마지막 시험의 6단계(`check`, `reconcile_wake`)가 두 입구에서 확인한다.

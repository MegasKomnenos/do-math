# test_stop_flags

| 항목 | 값 |
|---|---|
| 조각 | `lifecycle` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_stop_flags.py` (367행) |
| 클래스 / 테스트 | 5 / 16 (하네스 `StopFlagHarness`는 시험 0개) |
| 시험 대상 제품 코드 | `do_math/parallel.py`의 `ModelCalls`(`start_call`, `judge`, `close`, 호출 미래의 `stop` 플래그); `do_math/scheduler.py`의 `SchedulerMixin._settle_stops`, `_stop_time_due`, `_observation_failed`, `_local_call_returned`; `do_math/engine.py`의 `ResearchEngine._call_steps`, `_apply_inbox`, `_upkeep`, `_save`, `_stop_deadlines`, `_goal_basis_key`, `control`; `do_math/execution_lifecycle.py`의 `record_submission_intent`; `do_math/lifecycle_engine.py`의 대화 임대 처리(`conversation_lost`); `do_math/windows_job.py`의 `WindowsJob`, `process_identity` |
| 사용하는 픽스처 모듈 | `research_fixtures`: `charter_change`, `policy_change`, `restore_template`, `FixtureAdapter`(모듈 수준), `prepared_rule_conditions`(빌드 안); `state_fixtures`: `active_instance`; `runner_fixtures`: `ScriptedRunner`; `engine_fixtures`: `reviewed_task`(빌드 안) |
| 격리 표지 | 없음 |
| 시작 상태 | 2단 템플릿 `state_fixtures.active_instance`(설정 `CONFIG`) 위에 쌓은 모듈 전용 빌드 `waiting_action(case=...)`을 `restore_template`로 복원한다. 사례는 넷(`preparation`, `record`, `goal_audit`, `work`)이다. 그 위에서 시험마다 실제 Windows Job과 호출 하나를 새로 시작한다 |

## 목적

모듈 docstring의 계약은 이렇다. 정지 사유는 실행 중인 계산에 오직 소유자(owner)가 세운 플래그로만 닿는다. 각 사례는 실제 AI 실행 하나(실제 Git 상태, 실제 로컬 Job)를 시작하고, 정지 사유 하나를 그 실제 경로로 바꾼다. 소유자의 게시(publication)나 시각 비교가 계산의 플래그를 세우고, 정지 전이를 한 번 기록해야 한다. 계산 자체는 소유자를 펌프하지 않는다.

제품 좌표는 다음과 같다. `ModelCalls.start_call`은 계산 함수를 별도 스레드에서 돌리며 `should_stop` 콜백으로 미래(future)의 `stop` 이벤트를 읽게 한다. 소유자는 상태가 바뀐 `_save`(게시)와 `_reload` 뒤에 `_evaluate_stops` → `ModelCalls.judge`로 살아 있는 호출의 정지 판정을 돌린다(`engine.py` 765–786행, `scheduler.py` 40–44행). 바뀐 것이 없는 `_save`는 아무것도 게시하지 않으므로 판정도 돌지 않는다. `_settle_stops`(46–53행)는 대기 중인 소유자 변경을 게시하고, 시각에 묶인 정지 사유(허가 만료, 호출 마감, 대화 임대)가 도래했으면 판정을 한 번 더 돌린다. 이 모듈은 사유별로 "게시 전에는 플래그가 서지 않고, 게시나 시각 비교 뒤에는 서며, 실행 기록은 `stopping`으로 한 번 전이하고, 계산은 소유자 왕복 없이 플래그를 관측한다"를 확인한다.

## 모듈 수준 요소

- 행 18: `sys.path.insert(0, ...)`로 `scripts/` 폴더를 경로 맨 앞에 넣는 공통 머리.
- 행 29–30 `CONFIG`: `operator_enabled=False`, `scholarly_enabled=False`, `lean_command=['test-lean']`, `tool_review_window_seconds=60`, `self_check_response_window_seconds=5`. 템플릿 `active_instance`의 설정이며, 모든 사례가 같은 설정으로 복원된다.
- `apply(engine, repository, action, **kwargs)` (행 33–39): 공개 `control`로 요청을 받은함에 쓰고, `engine._apply_inbox(pump=False)`와 `engine._upkeep()`로 소유자 한 바퀴를 돌린 뒤, 그 요청 ID의 `rejected_user_control` 이력 행 목록을 돌려준다. docstring은 "소유자 한 바퀴가 대기 중인 공개 제어를 적용한다; 거부 기록을 돌려준다"고 적는다. `applied`와 `StopFlagHarness.apply`가 쓴다.
- `applied(engine, repository, action, **kwargs)` (행 42–45): `apply`의 결과가 비어 있지 않으면 `AssertionError('The fixture control was rejected: ...')`를 던진다. 빌드 함수 `prepare_record`, `prepare_work`가 준비 제어를 넣을 때 쓴다.
- `prepare_preparation(engine, root)` (행 48–51): `research_preparation` 행동 하나를 큐에 넣고 저장한다. 빈 사전을 돌려준다.
- `prepare_record(engine, root)` (행 54–70): `root/'basis.txt'`에 `'original'`을 쓰고 `source` 제어로 등록한다. 그 원천을 `source_refs`로 인용하는 관찰 지식 "Computation"을 `knowledge` `import` 제어로 들여온다. 큐를 비운 뒤, 그 지식을 대상으로 하는 `research_preparation`을 큐에 넣고 저장한다. `{'kid': 지식 ID}`를 돌려준다. docstring은 "원천 파일을 인용하는 들여온 기록에 묶인 준비"라고 적는다.
- `prepare_goal_audit(engine, root)` (행 73–78): 큐를 비우고 `_ensure_goal_audit_requests(engine._goal_basis_key(), 'EX-goal-request')`로 목표 감사 요청을 만든 뒤, 큐를 첫 `goal_audit` 행동 하나로 줄이고 저장한다.
- `prepare_work(engine, root)` (행 81–105): 관찰 지식 "Input fact"를 들여온다. `research_work` 역할을 가진 허가를 찾는다. 봉인된 과제 기록이 이름을 대는 생산자 `EX-preparation`과 검토자 `EX-review-TK-stop`을 `_register_execution`으로 등록하고 `stopping` → `ended`(`outcome='execution_incomplete'`)로 전이한다. `engine_fixtures.reviewed_task`로 검토된 과제 `TK-stop`(입력은 그 지식, 권한은 그 허가, 초기 관찰 규칙은 `prepared_rule_conditions(['TK-stop'])`의 것)을 만든다. 큐를 비우고 `TK-stop`에 대한 `research_work`를 모델 평가(`difficulty`·`importance`가 `low`)와 함께 큐에 넣고 저장한다. `{'kid': 지식 ID}`를 돌려준다.
- `PREPARE` (행 108–109): 사례 이름에서 위 네 준비 함수로 가는 사전.
- `waiting_action(root, shared, *, case)` (행 112–123): `restore_template` 빌드. `active_instance(root, shared, config=CONFIG)`로 2단 상태를 만들고, `work-0/runs` 폴더를 만든다. `do_math.initialization.adapter_for`를 `FixtureAdapter`로 바꾼 채 `ScriptedRunner`를 가진 엔진을 열어 `PREPARE[case]`를 돌린다. `{'instance_id', **준비 결과}`를 돌려준다. docstring은 "실행 중인 호출은 복사할 수 없으므로(실행기가 그것을 복구한다) 각 시험이 호출을 스스로 시작한다"고 적는다. `research_fixtures` docstring의 "What to use"도 이 빌드를 `test_stop_flags` 전용으로 적는다.
- 행 366–367: 직접 실행하면 `unittest.main()`을 부른다.

## StopFlagHarness (행 126–184)

`unittest.TestCase`를 상속한 하네스로, 자기 시험은 없다. 네 시험 클래스가 이것을 상속한다.

- 클래스 속성 `case` (행 127): `'preparation'`. 하위 클래스가 바꾼다.
- `setUp` (행 129–135): `do_math.initialization.adapter_for`를 `FixtureAdapter`로 바꾸는 패치를 시험 끝까지 건다(`enterContext`). `restore_template(waiting_action, case=self.case)`로 복원하고, `self.repo = root/'repository'`, `self.engine = ResearchEngine(self.repo, instance_id, runner=ScriptedRunner())`, `self.kid`(빌드가 준 지식 ID 또는 `None`), `self.source = root/'basis.txt'`를 세운다. 복원된 큐의 첫 행동이 시험이 시작할 호출이다.
- `running()` (행 138–168, `@contextmanager`): docstring은 "플래그만 읽는 계산을 가진, 시작된 운영 역할 실행 하나"라고 적는다. 엔진에 새 `ModelCalls(on_returned=e._local_call_returned, on_observation_error=e._observation_failed)`를 붙이고, `e._call_steps(queue[0])` 생성기에서 첫 인자를 얻는다. 실제 `WindowsJob([sys.executable, '-c', 'import time; time.sleep(600)'], cwd=작업공간, name=발사 표의 job_name)`을 만든다. 계산 함수 `calculate(should_stop, **_)`는 해제 이벤트가 설 때까지 0.01초마다 `should_stop()`을 읽어 `reads`에 붙이고, 참이면 `{'status': 'stopped', ..., 'error': 'flag observed'}`를 돌려준다. 이어 `on_started`에 Job의 프로세스 식별을 알리고, Job을 재개하고, `e._calls.start_call(steps, calculate, arguments, execution_id=...)`로 호출을 시작한다. 시작 직후 `future.stop`이 서 있지 않음을 단언한다(메시지 "nothing requires a stop at start"). `(engine, execution_id, future, reads)`를 내준다. 정리 단계에서 해제 이벤트를 세우고, `ModelCalls`와 생성기를 닫고, Job을 종료한 뒤 `job.wait(10)`이 참임을 단언하고 Job을 닫는다.
- `assertStopped(engine, execution_id, future, reads, reason=None)` (행 170–180): `future.stop`이 섰고, `future.judge_error`가 `None`이며, 실행 기록의 `status`가 `'stopping'`임을 단언한다. `reason`이 주어지면 `stop_reason`이 그 값인지도 본다. 이어 5초 상한 안에서 0.01초 간격으로 `reads`의 마지막 값이 참이 되기를 폴링하고, 참임을 단언한다(메시지 "the calculation observes the flag without an owner round trip").
- `apply(action, **kwargs)` (행 182–184): 모듈 함수 `apply`의 거부 목록이 `[]`임을 단언한다. docstring은 "소유자 한 바퀴가 대기 중인 공개 제어를 적용하고, 그 게시가 정지를 판정한다"고 적는다.

## PreparationStopTests (행 187–289)

`StopFlagHarness`를 상속하고 `case='preparation'`(기본값)을 쓴다. docstring: "준비 하나(운영 역할): 수명주기, 권한, 거버넌스, 시계 사유". 모든 시험의 준비는 하네스 `setUp`과 `running()`이다.

### `test_pause_publishes_a_stop` (행 190–193)
- 성질: 공개 `pause` 제어의 게시는 실행 중인 준비를 `user_pause` 사유로 멈춘다.
- 준비: 하네스 절의 `setUp`과 `running()`.
- 실행: `self.apply('pause', text='Stop the running preparation')`.
- 단언: `assertStopped(..., 'user_pause')`.
- 대역: `FixtureAdapter`(어댑터 관측), `ScriptedRunner`(엔진 러너; 호출 자체는 하네스의 `calculate`가 대신한다).
- 비고: 실제 Git 상태 복사본, 실제 Windows Job 자식 프로세스. 폴링 상한 5초, Job 종료 대기 10초.

### `test_close_publishes_a_stop` (행 195–198)
- 성질: 공개 `close` 제어의 게시는 실행 중인 준비를 `closed` 사유로 멈춘다.
- 준비: 하네스 절과 같다.
- 실행: `self.apply('close', text='Close the research')`.
- 단언: `assertStopped(..., 'closed')`.
- 대역: `FixtureAdapter`, `ScriptedRunner`.
- 비고: 실제 Git 상태 복사본, 실제 Windows Job.

### `test_revoked_grant_publishes_a_stop` (행 200–204)
- 성질: 실행이 쓰는 허가를 철회하는 결정의 게시는 그 실행을 멈춘다.
- 준비: 하네스 절과 같다. 실행 기록의 `grant_id`를 읽는다.
- 실행: `self.apply('decision', config={'change': {'kind': 'revoke', 'grant_id': grant}})`.
- 단언: `assertStopped`(사유 값은 고정하지 않는다).
- 대역: `FixtureAdapter`, `ScriptedRunner`.
- 비고: 실제 Git 상태 복사본, 실제 Windows Job.

### `test_governance_revision_publishes_a_stop` (행 206–211)
- 성질: 새 정책 결정의 게시는 실행을 `governance_changed` 사유로 멈추고 현행성 변화를 기록한다.
- 준비: 하네스 절과 같다.
- 실행: `self.apply('decision', config={'change': policy_change(e, 'A newly effective policy.')})`. `policy_change`는 현재 목표를 범위로, 현재 헌장을 근거로 하는 정책 `PO-...` 개정 1을 만든다.
- 단언: `assertStopped(..., 'governance_changed')`, 실행 기록의 `currentness_changes`가 비어 있지 않다.
- 대역: `FixtureAdapter`, `ScriptedRunner`.
- 비고: 원문 주석(209행)은 "정책 결정이 소비자를 표시하고, 판정은 바뀐 개정도 기록한다"고 적는다.

### `test_goal_change_publishes_a_stop` (행 213–216)
- 성질: 목표를 바꾸는 헌장 결정의 게시는 실행을 멈춘다.
- 준비: 하네스 절과 같다.
- 실행: `self.apply('decision', config={'change': charter_change(e, goal='Prove a revised target')})`. `charter_change`는 현재 헌장을 대체하는 다음 개정을 만든다.
- 단언: `assertStopped`(사유 값은 고정하지 않는다).
- 대역: `FixtureAdapter`, `ScriptedRunner`.

### `test_accepted_submission_intent_publishes_a_stop` (행 218–227)
- 성질: 수락된 제출 의도는 게시되기 전에는 정지 사유가 아니고, 게시되면 실행을 `submission_intent` 사유로 멈춘다.
- 준비: 하네스 절과 같다.
- 실행: `record_submission_intent(execution, {'candidate_id': 'SC-fixture', 'manifest': [], 'output_ref': 'runtime/artifacts/BA-x/output.json'}, {'id': 'CT-fixture', 'kind': 'submit_intent', 'state': 'accepted', ...})`로 실행 기록을 직접 바꾼 뒤 `e._save()`로 게시한다.
- 단언: 게시 전 `future.stop`이 서 있지 않다(메시지 "an unpublished change is not a stop reason"). 게시 뒤 `assertStopped(..., 'submission_intent')`.
- 대역: `FixtureAdapter`, `ScriptedRunner`. 전송 계층의 수락 경로는 부르지 않고, 원문 주석(221행)이 말하는 그 경로의 끝(게시)만 재현한다.

### `test_unpublished_owner_change_is_published_by_the_next_pass` (행 229–234)
- 성질: 소유자가 실행 기록에 정지 요청을 적어도 게시되기 전에는 플래그가 서지 않고, 다음 소유자 한 바퀴(`_settle_stops`)가 그것을 게시해 멈춘다.
- 준비: 하네스 절과 같다.
- 실행: 실행 기록에 `stop_requested='operational_retry'`를 적고, `e._settle_stops()`를 부른다.
- 단언: 적은 직후 `future.stop`이 서 있지 않다. `_settle_stops` 뒤 `assertStopped(..., 'operational_retry')`.
- 대역: `FixtureAdapter`, `ScriptedRunner`.

### `test_call_deadline_and_finish_notice_are_clock_comparisons` (행 236–255)
- 성질: 호출의 마무리 통지와 마감은 소유자의 시각 비교로 판정되며, 마무리 통지는 통지 파일만 쓰고 권한을 거두지 않고, 마감은 실행을 멈춘다.
- 준비: 하네스 절과 같다. `e._stop_deadlines[eid]`에서 `(notice, deadline)` 단조 시각을 읽는다. 지역 함수 `at(instant)`은 실제 `time` 모듈의 공개 이름을 모두 복사한 `SimpleNamespace`에서 `monotonic`만 `instant`를 돌려주게 바꾸고, 그것을 `do_math.engine.time`과 `do_math.scheduler.time`에 거는 패치 두 개를 돌려준다.
- 실행: 먼저 실제 시각으로 `_settle_stops()`를 한 번 불러 시계 기준(`_stop_clock`)을 세운다. 이어 `notice + 0.001`로 패치한 채 `_settle_stops()`, 다음에 `deadline + 0.001`로 패치한 채 `_settle_stops()`를 부른다.
- 단언: 통지 시각 뒤 `runs/<eid>/workspace/.control/finish-request.json`이 존재하고 `future.stop`은 서 있지 않다(메시지 "a finish notice does not revoke authority"). 마감 뒤 `assertStopped(..., 'user_or_deadline_stop')`.
- 대역: `do_math.engine.time`, `do_math.scheduler.time`의 시계 주입(`monotonic`만 이동). 원문 주석(241행)은 "실행기의 마감 시계만 움직이고, 시계 가드는 실제 시각을 유지한다"고 적는다.

### `test_grant_expiry_is_a_clock_comparison` (행 257–269)
- 성질: 허가 만료는 소유자의 시각 비교로 판정되어, 만료 시각이 지나면 실행을 `authority_changed` 사유로 멈춘다.
- 준비: 하네스 절과 같다. 실행의 허가에서 `expires_at`을 읽어 1초 뒤 시각 `later`를 만든다. 템플릿 허가의 만료는 빌드 하루 뒤다(`research_fixtures` docstring "Rules of a copy").
- 실행: 실제 시각으로 `_settle_stops()`를 한 번 부른다. 이어 `e.lifecycle_clock`을 `later`로 고정하고, `now`가 `later`를 돌려주는 `datetime` 하위 클래스 `Clock`을 `do_math.governance.datetime`에 건 채 `_settle_stops()`를 부른다.
- 단언: 첫 호출 뒤 `future.stop`이 서 있지 않다. 둘째 호출 뒤 `assertStopped(..., 'authority_changed')`.
- 대역: `e.lifecycle_clock` 주입, `patch('do_math.governance.datetime', Clock)`.

### `test_conversation_lease_expiry_stops_under_the_pause_policy` (행 271–284)
- 성질: 연결 끊김 정책이 `pause`인 대화의 임대가 만료되면 실행이 `conversation_lost` 사유로 멈춘다.
- 준비: 하네스 `setUp` 뒤, `running()`에 들어가기 전에 `e.lifecycle_clock`을 "실제 시각 + `offset[0]`"으로 바꾼다. `conversation` `attach` 제어(`id='CV-fixture'`, `generation=1`, `lease_seconds=60`, `disconnect_policy='pause'`)를 보내고 `_apply_inbox(pump=False)`와 `_upkeep()`으로 적용한다. 이 시험은 하네스의 `apply`를 쓰지 않으므로 거부 여부를 단언하지 않는다.
- 실행: `running()` 안에서 `_settle_stops()`를 부르고, `offset[0]`을 61초로 옮긴 뒤 다시 `_settle_stops()`를 부른다.
- 단언: 첫 호출 뒤 `future.stop`이 서 있지 않다. 둘째 호출 뒤 `assertStopped(..., 'conversation_lost')`.
- 대역: `e.lifecycle_clock` 주입.
- 비고: `_settle_stops`는 `clock=True`일 때 `_check_conversations()`를 먼저 부른다(`scheduler.py` 50–51행). 제품의 임대 만료 처리는 `lifecycle_engine.py` 503–508행(`_request_stop_all('conversation_lost')`)이다.

### `test_failed_observation_is_the_recorded_stop_reason` (행 286–289)
- 성질: 적용하지 못한 관측은 그 실행을 멈추고, 오류가 기록된 정지 사유가 된다.
- 준비: 하네스 절과 같다.
- 실행: `e._observation_failed(eid, ValueError('provider row differs'))`.
- 단언: `assertStopped(..., 'observation_failed: ValueError: provider row differs')`.
- 대역: `FixtureAdapter`, `ScriptedRunner`.
- 비고: `_observation_failed`는 `stop_requested`를 `setdefault`하고 `_save`로 게시한다(`scheduler.py` 97–101행). 이 시험은 `ModelCalls`의 관측 적용 실패 경로를 거치지 않고 콜백을 직접 부른다.

## RecordStopTests (행 292–312)

`StopFlagHarness`를 상속하고 클래스 속성 `case='record'`(행 295)를 둔다. docstring: "기록에 묶인 실행: 지식과 원천 변경이 게시를 통해 닿는다". 큐의 첫 행동은 `prepare_record`가 만든, 들여온 지식에 묶인 준비이고, 그 지식은 `root/'basis.txt'`를 인용한다.

### `test_knowledge_revision_publishes_a_decision_basis_stop` (행 297–305)
- 성질: 실행이 읽은 지식의 개정 게시는 그 실행을 멈추고 현행성 변화를 기록한다.
- 준비: 하네스 절과 이 클래스 절. `knowledge.plan_impact(e.instance, e.runtime, revision_roots(e.instance, self.kid), [])`로 영향을 계산한다.
- 실행: `self.apply('knowledge', config={'operation': 'revise', 'id': self.kid, 'changes': {'statement': 'The result is two.'}, 'declared_impact': impact['computed_impact'], 'reason': ...})`.
- 단언: `assertStopped`(사유 값은 고정하지 않는다), 실행 기록의 `currentness_changes`가 비어 있지 않다.
- 대역: `FixtureAdapter`, `ScriptedRunner`.
- 비고: 이름은 "결정 기반(decision basis) 정지"를 말하지만 단언은 `currentness_changes`가 비어 있지 않다는 것만 보며, 변화 행의 종류는 고정하지 않는다.

### `test_source_change_publishes_a_currentness_stop` (행 307–312)
- 성질: 실행이 간접으로 읽는 원천 파일의 새 내용이 게시되면 실행이 멈추고 현행성 변화가 기록된다.
- 준비: 하네스 절과 이 클래스 절.
- 실행: `self.source`에 `'corrected'`를 쓰고 `self.apply('source', config={'path': str(self.source)})`.
- 단언: `assertStopped`(사유 값은 고정하지 않는다), `currentness_changes`가 비어 있지 않다.
- 대역: `FixtureAdapter`, `ScriptedRunner`.

## GoalAuditStopTests (행 316–338)

`StopFlagHarness`를 상속하고 클래스 속성 `case='goal_audit'`(행 319)을 둔다. docstring: "목표 감사는 완결된 기반 하나를 판정한다; 게시된 기반 변화는 무엇이든 그것을 멈춘다". 큐의 첫 행동은 목표 감사 한 자리다.

### `test_goal_basis_change_publishes_a_stop_and_is_judged_once_per_head` (행 321–338)
- 성질: 같은 게시 헤드에서는 목표 기반을 많아야 한 번 계산하고, 새 지식의 게시로 기반이 바뀌면 목표 감사가 멈추며 `goal_audit_basis` 변화가 기록된다.
- 준비: 하네스 절과 이 클래스 절. `ResearchEngine._goal_basis_key`를 호출 때마다 `engine.head`를 `calls`에 기록한 뒤 원래 함수를 부르는 `counted`로 바꾼다(`patch.object(type(e), '_goal_basis_key', counted)`).
- 실행: 패치 안에서 `e._calls.judge()`를 두 번 부르고, 이어 관찰 지식 "New evidence"를 `knowledge` `import` 제어로 들여온다(`self.apply`).
- 단언: 두 번 판정한 뒤 `future.stop`이 서 있지 않고, `len(calls) <= 1`이다(메시지 "one goal basis per published head"). 들여온 뒤 `assertStopped`(사유 값은 고정하지 않는다), `currentness_changes`에 `field == 'goal_audit_basis'`인 행이 있다.
- 대역: `_goal_basis_key`의 계수 래퍼, `FixtureAdapter`, `ScriptedRunner`.
- 비고: 제품의 메모는 `scheduler.py` 72–77행의 `_goal_basis_key_at_head`다("정지 판정은 게시된 상태를 읽으므로 한 헤드의 모든 판정에 목표 기반 하나가 쓰인다"). 단언이 `<= 1`이므로, 시작 시점에 이미 메모가 차 있어 한 번도 계산하지 않아도 통과한다.

## WorkStopTests (행 342–363)

`StopFlagHarness`를 상속하고 클래스 속성 `case='work'`(행 345)를 둔다. docstring: "검토된 과제의 연구 작업: 사용 조건과 과제 계약". 큐의 첫 행동은 `prepare_work`가 만든 `TK-stop`의 `research_work`이고, 그 과제의 입력은 들여온 지식 `self.kid`다.

### `test_unusable_input_publishes_a_use_condition_stop` (행 347–355)
- 성질: 작업 입력 지식을 무효화하는 게시는 작업을 멈추고 `required_use_conditions` 변화를 기록한다.
- 준비: 하네스 절과 이 클래스 절. `plan_impact`로 영향을 계산한다.
- 실행: `self.apply('knowledge', config={'operation': 'invalidate', 'id': self.kid, 'declared_impact': ..., 'reason': 'The input was found wrong.'})`.
- 단언: `assertStopped`(사유 값은 고정하지 않는다), `currentness_changes`에 `field == 'required_use_conditions'`인 행이 있다.
- 대역: `FixtureAdapter`, `ScriptedRunner`.

### `test_changed_task_contract_stops_once_the_owner_publishes_it` (행 357–363)
- 성질: 과제 계약의 변경은 소유자가 게시하기 전에는 정지 사유가 아니고, 게시하면 작업을 `authority_changed` 사유로 멈춘다.
- 준비: 하네스 절과 이 클래스 절.
- 실행: 런타임의 `TK-stop.question`을 `'Does P hold for every case?'`로 직접 바꾸고 `e._settle_stops()`를 부른다.
- 단언: 바꾼 직후 `future.stop`이 서 있지 않다(메시지 "an unpublished change is not a stop reason"). `_settle_stops` 뒤 `assertStopped(..., 'authority_changed')`.
- 대역: `FixtureAdapter`, `ScriptedRunner`.

## 관계

- 같은 제품 기능의 다른 층: `_settle_stops`를 부르는 다른 시험 모듈은 `test_repair_execution`이다. `should_stop` 콜백은 `test_engine`, `test_formal`, `test_formal_engine`, `test_machine_parallel`, `test_model_runner`, `test_session_scheduler`, `test_submission_tools` 등 10여 모듈에 나오며, 대개 러너나 계산 쪽에서 플래그를 읽는 모습을 본다. 이 모듈은 사유마다 "누가 플래그를 세우는가"를 소유자 쪽에서 본다. 대화 임대와 수명주기 제어의 상태 전이 자체는 `test_lifecycle_engine`, `test_controls`가 다룬다.
- 픽스처 의존: `state_fixtures.active_instance`(2단 템플릿)와 `research_fixtures.restore_template`. 빌드 안에서 `engine_fixtures.reviewed_task`, `research_fixtures.prepared_rule_conditions`를 쓴다. 결정 변경은 `research_fixtures.charter_change`·`policy_change`로 만든다.
- 이 모듈에만 있는 것: 빌드 `waiting_action`과 준비 함수 넷(`PREPARE`), 모듈 함수 `apply`·`applied`, 하네스 `StopFlagHarness`(`running`, `assertStopped`). 실제 Windows Job 위에서 플래그만 읽는 계산 대역을 돌리는 방식은 `research_fixtures.local_job_runner`(실제 Job 수명을 주는 래퍼로, `runner_fixtures.ScriptedRunner.run`에 붙는다)와 같은 Job 형태를 쓰지만, 계산은 이 모듈의 `calculate`가 대신한다.
- 시험 기법: 모든 시험이 "변경 → (게시 전 플래그 미설정 확인) → 게시 또는 시각 비교 → `assertStopped`"의 한 형태를 따른다. 시각 사유 셋(호출 마감, 허가 만료, 대화 임대)은 각자 다른 시계를 주입한다(`time.monotonic`, `governance.datetime`과 `lifecycle_clock`, `lifecycle_clock`).
- 실제 외부 자원: 16개 시험 모두 실제 Windows Job(Python 자식 프로세스 `time.sleep(600)`)을 만들고 종료한다. 계산 스레드가 실제로 돈다. 그런데도 `test_group('resource')` 표지가 없다. 이 모듈이 단언하는 것은 프로세스 수명이 아니라 플래그 판정이다. Job은 `on_started`에 넘길 프로세스 식별(`process_identity(job)`)을 대고, 정리 단계의 `job.wait(10)` 단언만이 그 수명을 본다. 모듈 docstring은 이 실제 Job을 사례 구성의 일부로 명시한다("real Git state, real local Job").

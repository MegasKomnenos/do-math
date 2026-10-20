# test_formal_engine

| 항목 | 값 |
|---|---|
| 조각 | `lifecycle` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_formal_engine.py` (256행) |
| 클래스 / 테스트 | 4 / 11 |
| 시험 대상 제품 코드 | `do_math/formal_engine.py`의 `_formal`(형식 검사 행동의 실행과 대기 전환), `_resume_formal_waits`, `_formal_environment`; `do_math/lifecycle_engine.py`의 `_apply_extended_control`(`FakeEngine.control`이 부른다); `do_math/engine.py`의 모듈 함수 `control`(`send_control`이 부른다), `ResearchEngine._unchanged`, `_save`; `do_math/governance.py`의 `authorize`(대역으로 대체); `do_math/execution_profiles.py`의 `build_profiles`; `do_math/knowledge_records.py`의 `create_candidate`; `do_math/knowledge_io.py`의 `import_candidate` |
| 사용하는 픽스처 모듈 | `engine_fixtures`: `formal_check_engine`, `formal_verification`, `routing_engine`; `research_fixtures`: `await_stop`, `send_control`, `trust_environment`, `trust_fixture`; `state_fixtures`: `owner_calls`, `start_active_copy` |
| 격리 표지 | 없음 |
| 시작 상태 | `FormalContinuationTests`: 메모리 엔진 대역 `FakeEngine`(`formal_check_engine`). `FormalAttemptLineageTests`: 2단(`start_active_copy`, 곧 `restore_template(state_fixtures.active_instance, config=ACTIVE_CONFIG)`). `FormalAuthority`: `routing_engine` 위의 모듈 함수 `parked_formal_check`. `FormalBindingConnections`: `routing_engine`과 합성 신뢰 환경(`trust_fixture`) |

## 목적

모듈 docstring은 "컴파일러 대역을 쓴 엔진의 형식 검사"를 시험하며, 세 무리를 든다. 제어 뒤의 계속(continuation after controls), 요구되는 환경(the required environment), 검증기의 결속(the verifier's binding)이다. 모든 시험이 실제 Lean을 부르지 않는다. 컴파일러 자리에는 `FakeEngine`의 `formal_behavior`, 엔진의 `formal_verifier` 속성에 꽂은 함수나 `Mock`이 선다.

시험 대상은 `do_math/formal_engine.py`의 형식 검사 경로다. `_formal(action)`은 활성 신뢰 환경을 고르고(`_formal_environment`), 권한을 확인하며(`governance.authorize`), 환경이나 권한이 없으면 행동을 `waiting_actions`에 `formal_authority` 대기로 옮긴다(`formal_engine.py` 행 344–356). 둘 다 있으면 실행을 등록하고 검증기를 부르며, 결과에 따라 실행을 끝내고 결과물(`formal.json`, `proposal.lean`)을 저장하거나, 정지된 검사를 `formal_stopped` 대기로 남긴다. `_resume_formal_waits`의 docstring(행 97–106)은 재개 규칙을 정한다. `formal_authority` 대기와 "일시정지 또는 권한·환경·입력 변경으로만 멈춘" `formal_stopped` 대기는 활성 환경이 형식 검사를 받고 행동이 허가되면 다시 대기열에 들어간다. 명시적 실행 정지로 멈춘 검사는 대기에 남는다. 코드(행 125–129)는 대기에 `execution_id`가 있을 때만 재개된 행동의 `continuation_of`에 그 실행을 적는다.

## 모듈 수준 요소

- 행 10: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 조건 없이 넣는다.
- 행 11–17: 제품 `execution_profiles`, `DEFAULT_CONFIG`, `ResearchEngine`, `ResearchRepository`와 픽스처 `formal_check_engine`, `formal_verification`, `routing_engine`, `await_stop`, `owner_calls`, `start_active_copy`를 가져온다. `send_control`, `trust_environment`, `trust_fixture`는 쓰는 자리에서 지역 import한다.
- `parked_formal_check()` (행 143–162): `FormalAuthority`의 공통 시작 상태를 만든다. docstring: "활성인 사전 승인 환경이 없어서 형식 검사 `AC-formal`이 기다리는 엔진". `routing_engine()`에서 시작해 활성 신뢰 환경·환경 목록·원천을 비우고, 설정을 `DEFAULT_CONFIG` 사본으로 바꾼 뒤 `build_profiles`로 실행 프로필을 채운다. `knowledge_io.import_candidate`로 정리 후보(`lean_code='theorem t : True := by trivial'`, 선언 `t`)를 들인다. 이어 엔진 메서드 `_action_lifecycle_gate`, `_require_action_clock`, `_save`를 `create_autospec` 대역으로 바꾸고, `runtime['trust_transitions'] = {}`, `formal_verifier = Mock()`을 둔 뒤 `_formal({'id': 'AC-formal', 'role': 'formal_check', 'target': kid})`를 한 번 부른다. 환경이 없으므로 이 호출은 행동을 `formal_authority` 대기로 옮기고 끝난다. 주석(행 154–155)이 대역의 이유를 밝힌다: 실제 신뢰 환경 관문만 떼어 보려는 것이고, 공개 수명주기·허가 수락은 `PublicGitFlow`와 LIFECYCLE의 주인 시험이 다룬다.
- 행 255–256: 직접 실행하면 `unittest.main()`(다른 모듈과 달리 `verbosity` 인자가 없다).

## FormalContinuationTests (행 20–93)

`unittest.TestCase`를 그대로 상속한다. 표지·설정 훅·클래스 속성은 없고, 시험마다 도우미 `make`로 새 엔진을 만든다.

- `make()` (행 21–22): `engine_fixtures.formal_check_engine(self)`를 돌려준다. 이 픽스처는 `do_math.initialization.adapter_for`를 `FixtureAdapter`로 패치하고(정리는 시험 종료 시), 임시 디렉터리 위의 `FakeEngine`을 활성화한 뒤, 후보 `K1`(`theorem k1 : 1 = 1 := rfl`)을 만들고, 활성 신뢰 환경의 구성 명령으로 `formal_check` 역할 프로필을 다시 만들어, `queue = [{'id': 'AC-formal', 'role': 'formal_check', 'target': 'K1'}]`인 `(engine, action)`을 반환한다. 시작 상태는 메모리 엔진 대역이다. 저장소 자리에는 메모리 `StateStore` 대역이 서고, `FakeEngine._save`는 공개하지 않고 상태와 결과물의 사본을 엔진의 `saves` 목록에 적는다(`engine_fixtures.py` 행 109–110). `FakeEngine`은 형식 검사를 부를 때마다 인자를 `formal_calls`에 적고, `formal_behavior`가 있으면 그 결과를, 없으면 `formal_verification`(모든 선언을 `Eq Nat 1 1`로 검증된 것으로 만드는 컴파일러 대역)의 결과를 돌려준다.
- `stopped_check(arguments)` (행 24–28): `formal_behavior`로 꽂는 컴파일러 대역. docstring: "검사는 주인의 판정이 정지 플래그를 세울 때까지 그 플래그를 읽는다." `research_fixtures.await_stop(arguments['should_stop'], timeout=5)`로 0.01초 간격 폴링을 하다가 5초 안에 플래그가 서지 않으면 `AssertionError('the owner control did not reach the check')`를 던지고, 서면 `{'status': 'stopped'}`를 돌려준다.
- `run_with_control(engine, action, operation)` (행 30–36): docstring: "검사를 시작하고, 주인에게 제어를 적용한 뒤, 공개가 하듯 정지를 판정한다." `formal_behavior = stopped_check`로 두고 `state_fixtures.owner_calls(engine)` 블록 안에서 `engine._formal(action)`, `engine.control(operation, {})`, `calls.judge()`를 차례로 부른다. `owner_calls`는 블록 안에서 시작된 호출을 `ModelCalls` 위에서 스케줄러처럼 돌리고, 블록을 떠날 때 모든 호출을 거둬 계속을 한 번 재개한다. 그래서 검사는 다른 스레드에서 정지 플래그를 기다리고, 주인은 제어를 적용한 뒤 `judge()`로 플래그를 세운다.

### `test_pause_resume_retains_one_action_and_reaches_identity_review` (행 38–56)
- 성질: 실행 중인 형식 검사가 일시정지로 멈추면 그 실행은 끝나되 같은 행동이 계속 행동으로 대기열에 하나만 남고, 재개(두 번 보내도) 뒤 다시 돌면 이전 실행을 잇는 두 번째 시도가 검증되어 동일성 검토로 이어진다.
- 준비: `make()`의 `FakeEngine`과 `AC-formal`.
- 실행: `run_with_control(engine, action, 'pause')`. 이어 `engine.control('resume', {})`를 두 번. 그다음 `formal_behavior = None`(기본 컴파일러 대역)으로 두고 `owner_calls` 안에서 대기열의 그 행동으로 `_formal`을 다시 부른다.
- 단언: 첫 `formal_check` 실행의 `status == 'ended'`. 대기열에 같은 ID의 행동이 있고 `continuation_of`가 첫 실행 ID다. 첫 실행의 소유 활동은 `finished`가 아니다. 재개를 두 번 한 뒤 대기열에서 그 행동 ID는 정확히 하나다. 두 번째 실행 뒤 `formal_check` 실행이 둘이고, 마지막 실행의 `continuation_of`가 첫 실행이며 `formal_status == 'verified'`다. 대기열에 `identity_review` 역할 행동이 있다.
- 대역: `FakeEngine`, `formal_behavior`(첫 시도 `stopped_check`, 둘째 시도 기본 `formal_verification`), `adapter_for` 패치(`formal_check_engine` 안).
- 비고: `stopped_check`의 폴링 상한 5초.

### `test_check_stopped_before_start_ends_and_returns_its_capacity` (행 58–68)
- 성질: 인스턴스가 이미 일시정지된 상태에서 형식 검사가 배정되면 컴파일러를 부르지 않고 실행을 끝내며, 로컬 종료를 확인해 용량을 반환하고, 행동은 계속 행동으로 남는다.
- 준비: `make()`의 엔진. `engine.control('pause', {})`를 검사 전에 적용한다.
- 실행: `owner_calls` 안에서 `engine._formal(action)`.
- 단언: `formal_calls == []`(컴파일러 호출 없음). 실행의 `(status, capacity.local_termination) == ('ended', 'confirmed')`. 대기열의 그 행동의 `continuation_of`가 그 실행 ID다.
- 대역: `FakeEngine`, `adapter_for` 패치.
- 비고: 주석(행 65)이 의도를 적는다. 아무것도 시작되지 않았으므로 실행 요청은 돌아왔고 용량은 비어 있으며, 검사를 복구용으로 붙잡아 두지 않는다.

### `test_close_preserves_the_ended_check_without_continuation` (행 70–74)
- 성질: 실행 중인 형식 검사가 종료(`close`) 제어로 멈추면 계속 행동을 남기지 않는다.
- 준비: `make()`의 엔진.
- 실행: `run_with_control(engine, action, 'close')`.
- 단언: 대기열에 그 행동 ID가 없고, `waiting_actions`가 비어 있다.
- 대역: `FakeEngine`, `stopped_check`, `adapter_for` 패치.
- 비고: 이름은 끝난 검사가 "보존된다"고 말하지만, 시험은 실행 기록의 존재나 상태를 단언하지 않는다. 계속이 없다는 것만 본다.

### `test_resume_rechecks_source_trust_and_authority_before_another_call` (행 76–93)
- 성질: 일시정지 뒤 재개된 계속 행동은 다시 컴파일러를 부르기 전에 원천, 신뢰 환경, 권한을 새로 확인한다.
- 준비: `subTest`마다 `make()`로 새 엔진을 만들고, `run_with_control(..., 'pause')`와 `control('resume', {})`로 계속 행동을 만든다. 그 뒤 조건 하나를 바꾼다.
- 실행: `formal_behavior = None`으로 두고 `owner_calls` 안에서 계속 행동으로 `_formal`.
- 단언: 세 경우 모두 `len(engine.formal_calls) == 1`, 곧 첫 시도(정지된 호출) 외에 컴파일러가 다시 불리지 않는다.
- 대역: `FakeEngine`, `stopped_check`, `adapter_for` 패치.
- 비고: `subTest` 케이스 `changed`는 셋이다. `'source'`: `K1`의 형식 결과 `lean_code` 끝에 `'\n-- changed candidate'`를 붙인다. `'trust'`: 활성 신뢰 환경의 `status`를 `'inactive'`로. `'authority'`: 허가 `GR-research`의 `status`를 `'revoked'`로. 단언은 호출이 없다는 것만 본다. 대기의 종류, 사유, 새 검증 여부처럼 각 경우가 어떤 경로로 거부되는지는 고정하지 않는다.

## FormalAttemptLineageTests (행 96–140)

`unittest.TestCase`를 그대로 상속한다. 클래스 표지와 속성은 없다.

- `setUp` (행 97–98): `state_fixtures.start_active_copy(self)`. `do_math.initialization.adapter_for`를 `FixtureAdapter`로 바꾸는 패치를 시험 수명 동안 걸고, `restore_template(active_instance, config=ACTIVE_CONFIG)`의 사본을 받아 `self.root`, `self.repo`, `self.identifier`를 둔다. 2단 시작 상태다.

### `test_public_pause_restart_resume_preserves_formal_attempt_lineage` (행 100–140)
- 성질: 공개 제어로 형식 검사를 일시정지하고, 엔진을 새로 적재한 뒤 공개 재개를 보내면, 저장소에 남은 계속 행동이 첫 시도를 잇고 두 번째 시도가 검증되어 동일성 검토로 이어진다. 시도의 계보가 Git 저장과 재적재를 지나서도 보존된다.
- 준비: 2단 사본에 `ResearchEngine(self.repo, self.identifier)`를 연다. 활성 환경의 구성 명령을 `config['lean_command']`로 두고 `build_profiles`로 `formal_check` 프로필 판본을 갱신한다. `create_candidate`로 보조정리 `KN-formal-resume`(`theorem resume_fixture : 1 = 1 := rfl`)를 만들고(원천은 인스턴스 입력 ID, 행위자는 첫 실행 ID), `_enqueue('formal_check', ...)`와 `_save()`로 저장한다.
- 실행: (1) `formal_verifier`를 지역 함수 `pause`로 둔다. 이 함수는 `await_stop(should_stop, timeout=5)`로 정지 플래그를 기다리고 `{'status': 'stopped', 'reason': 'Explicit test pause; no Lean process'}`를 돌려준다. `owner_calls` 안에서 `_formal`로 검사를 시작하고 `research_fixtures.send_control(engine, 'pause', config={})`로 공개 제어를 보낸다. (2) 새 `ResearchEngine`을 열어 `send_control(restarted, 'resume', config={})`. (3) 재적재된 엔진의 `formal_verifier`를 `formal_verification(source, declarations, expected_toolchain)`을 부르는 람다로 두고 `owner_calls` 안에서 대기열의 계속 행동으로 `_formal`. (4) 또 새 엔진을 열어 결과를 읽는다.
- 단언: (1) 뒤 첫 실행의 `status == 'ended'`. (2) 뒤 대기열의 `formal_check` 행동의 `continuation_of`가 첫 실행 ID. (4)에서 `formal_check` 실행이 둘이고, 그 가운데 `continuation_of`가 첫 실행이고 `formal_status == 'verified'`인 것이 있다. 대기열에 `identity_review` 행동이 있다.
- 대역: `formal_verifier` 함수 둘(정지 대역, `formal_verification` 컴파일러 대역), `adapter_for` 패치(`setUp`).
- 비고: 정지 대역의 폴링 상한 5초. `send_control`은 `do_math.engine`의 공개 모듈 함수 `control`로 저장소에 요청을 넣고 `process_controls`로 처리한 뒤, 거부 기록이 있으면 `AssertionError`를 던진다. `FormalContinuationTests.test_pause_resume_retains_one_action_and_reaches_identity_review`와 같은 흐름을 메모리 엔진이 아니라 실제 Git 저장소와 공개 제어, 엔진 재적재로 확인한다.

## FormalAuthority (행 165–196)

`unittest.TestCase`를 그대로 상속한다. 표지·훅·도우미·클래스 속성이 없다. 모든 시험이 모듈 함수 `parked_formal_check()`로 시작한다(모듈 수준 요소 참조).

### `test_missing_preapproved_environment_never_runs_or_autoapproves` (행 166–170)
- 성질: 사전 승인된 신뢰 환경이 없으면 형식 검사는 컴파일러를 부르지 않고, 환경을 스스로 승인하지도 않으며, 활동이 대기 상태가 된다.
- 준비: `parked_formal_check()`.
- 실행: 준비 안의 `_formal` 호출이 곧 실행이다.
- 단언: `formal_verifier`(`Mock`)가 불리지 않았다. `active_trust_environment`가 여전히 `None`이다. 첫 활동의 `status == 'waiting'`.
- 대역: `formal_verifier = Mock()`, `create_autospec`으로 바꾼 `_action_lifecycle_gate`, `_require_action_clock`, `_save`.

### `test_parked_check_returns_to_the_queue_once_an_environment_and_authority_admit_it` (행 172–180)
- 성질: 대기 중인 형식 검사는 환경과 권한이 모두 허락하기 전에는 대기에 머물고, 둘 다 허락하면 대기열로 돌아온다.
- 준비: `parked_formal_check()`. `AC-formal`은 `formal_authority` 대기다.
- 실행: `_resume_formal_waits()`를 환경 없이 한 번, 이어 `_formal_environment`가 `{'id': 'TE-new'}`를 돌려주고 `governance.authorize`가 `{'allowed': True, 'grant_id': 'GR-one'}`을 돌려주게 한 뒤 다시 한 번.
- 단언: 첫 호출 뒤 `AC-formal`이 `waiting_actions`에 남아 있다. 둘째 호출 뒤 `waiting_actions`에 없고 대기열 행동 ID에 있다.
- 대역: `create_autospec(engine._formal_environment, return_value={'id': 'TE-new'})`, `patch('do_math.governance.authorize', ...)`, 그리고 준비의 대역들.
- 비고: 환경만 있고 권한이 없는 경우나 그 반대는 따로 보지 않는다. 이름의 "environment and authority"는 둘을 함께 허락했을 때의 재진입만 확인한다.

### `test_only_a_check_stopped_by_changed_conditions_resumes` (행 182–196)
- 성질: 정지된 형식 검사 가운데 권한·입력 변경처럼 회복 가능한 사유로만 멈춘 것은 재개되어 이전 실행을 잇고, 명시적 실행 정지로 멈춘 것은 대기에 남는다.
- 준비: `parked_formal_check()`의 `AC-formal` 대기를 꺼내 그 행동을 본으로 삼는다. `formal_stopped` 대기 둘을 직접 넣는다. `AC-changed`는 `stop_reasons=['authority_changed', 'input_changed']`, `AC-stopped`는 `['execution_stop_requested']`이며, 각각 `execution_id = 'EX-' + ID`, `next_owner='trust_governance'`다.
- 실행: 환경·권한 대역을 둔 채 `_resume_formal_waits()`.
- 단언: `waiting_actions`의 키가 `['AC-stopped']`뿐이다. 대기열의 `AC-changed` 행동의 `continuation_of == 'EX-AC-changed'`.
- 대역: 앞 시험과 같은 `_formal_environment`·`authorize` 대역과 준비의 대역들.
- 비고: 제품 규칙은 `_resume_formal_waits`의 `recoverable = {'instance_paused', 'authority_changed', 'trust_environment_changed', 'input_changed'}`이며, 대기의 `stop_reasons`가 이 집합의 부분집합일 때만 재개한다.

## FormalBindingConnections (행 199–252)

`unittest.TestCase`를 그대로 상속한다. 표지·설정 훅·클래스 속성은 없다.

- `run_verifier(result)` (행 200–222): `routing_engine()` 위에 합성 신뢰 환경을 붙이고 형식 검사를 한 번 돌려 `(engine, environment)`를 돌려준다. 단계는 다음과 같다.
  1. 임시 디렉터리를 만들고 `addCleanup`으로 정리를 건다.
  2. 설정을 `DEFAULT_CONFIG`에 `lean_command=[sys.executable]`을 얹은 것으로 두고, `research_fixtures.trust_fixture(dir, [sys.executable])`로 합성 도구 모음 설치(가짜 `lean.exe` 등의 파일, 실제 `formal.py`를 검사기 정체로 쓰는 도구 모음 기록)를 만든 뒤 `trust_environment(..., environment_id='TE-one', source_ref='fixture')`로 환경 기록과 결속을 얻는다.
  3. 인스턴스에 작업공간·빈 원천·설정·활성 환경 `TE-one`을 넣고 `runtime['trust_bindings']`에 결속을 넣는다. 그 설정으로 `build_profiles`를 한 뒤, 설정의 `lean_command`만 `['unapproved-config-command']`로 바꾼다. 이 바꿈이 핵심이다. 프로필과 환경은 승인된 명령을 갖고, 현재 설정만 승인되지 않은 명령을 갖는다.
  4. `import_candidate`로 정리 후보를 들인다. `lean_code`는 `'-- é\r\ntheorem t : True := by trivial'`로, 결합 문자(e + U+0301)와 CRLF를 담는다.
  5. `engine.head = 'fixed-input'`으로 두고 `_save`, `_controls`, `_check_conversations`(`False` 반환), `_action_lifecycle_gate`, `_formal_environment`(환경 사본 반환)를 `create_autospec` 대역으로 바꾼다. `formal_verifier = Mock(return_value=result)`.
  6. `patch('do_math.engine.governance.authorize', return_value={'allowed': True, 'grant_id': 'GR-one'})`와 `owner_calls(engine)` 아래에서 `_formal({'id': 'AC-formal', 'role': 'formal_check', 'target': kid})`.

  시작 상태는 `routing_engine`(메모리 상태, 저장소 없음 `NoRepository`) 위에 합성 신뢰 환경 파일을 임시 디렉터리에 실제로 쓴 것이다.

### `test_verifier_uses_the_fixed_environment_command_and_fingerprint` (행 224–231)
- 성질: 형식 검사는 현재 설정의 명령이 아니라 고정된 신뢰 환경의 명령과 도구 모음 지문, 허용 공리로 검증기를 부르고, 시간 상한 인자 `timeout_seconds`를 건네지 않는다.
- 준비: `run_verifier({'status': 'failed', 'reason': 'compiler double, no proof claim'})`.
- 실행: `run_verifier` 안의 `_formal`.
- 단언: 검증기 호출 키워드에서 `lean_command == [sys.executable]`(설정의 `unapproved-config-command`가 아니다), `timeout_seconds` 키가 없음, `expected_toolchain`이 환경의 `toolchain`과 같음, `allowed_axioms`의 집합이 환경의 것과 같음. `formal_check` 실행의 `outcome == 'execution_incomplete'`(검증 실패 결과가 실행을 미완으로 끝낸다).
- 대역: `run_verifier`의 대역 전부.
- 비고: `timeout_seconds`가 없다는 단언은 `시험-지침.md` 1절이 말하는 "제품 Lean의 무제한 계산 계약"과 맞닿는다.

### `test_exact_compiler_keys_and_source_survive_result_artifacts` (행 233–241)
- 성질: 검증기 결과는 유니코드 정규화로 같아지는 키까지 서로 다른 키로 보존된 채 `formal.json` 결과물에 그대로 저장되고, 검증기에 넘긴 원천은 `proposal.lean` 결과물에 바이트 그대로(결합 문자와 CRLF 포함)저장된다.
- 준비: `run_verifier({'status': 'failed', 'reason': 'compiler double retains exact names', 'axioms': {'K': [], 'K': []}})`. `axioms`의 첫 키는 라틴 대문자 K(U+004B)이고, 둘째 키는 켈빈 기호 K(U+212A)다.
- 실행: `run_verifier` 안의 `_formal`.
- 단언: `_save` 대역의 호출 인자 가운데 첫 위치 인자(경로→바이트 사전)를 모두 모은다. `formal.json`으로 끝나는 결과물의 JSON 값이 `result`와 같다. `proposal.lean`으로 끝나는 결과물이 검증기에 넘긴 `source`의 UTF-8 인코딩과 같고, 그 안에 `'é\r\n'`의 UTF-8 바이트가 들어 있다.
- 대역: `run_verifier`의 대역 전부. 저장은 `_save`의 `create_autospec` 대역이 가로챈다.
- 비고: 켈빈 기호 U+212A는 NFC와 NFKC 모두에서 U+004B로 정규화되지만, Python 문자열 리터럴은 정규화되지 않으므로 두 키는 사전에서 합쳐지지 않는다. 따라서 `json.loads(raw) == result` 단언은 두 키가 모두 따로 남았는지를 실제로 검사한다. 이름의 "exact compiler keys"가 가리키는 것이 이것이다. 제품 경로는 `json_safe`(`payloads.py`, 키를 `str(k)`로만 바꾼다)를 거쳐 `canonical_json`(`repository.py` 행 214–219, docstring "without changing Unicode", `ensure_ascii=False`, `sort_keys=True`)으로 `formal.json`을 쓰며(`formal_engine.py` 행 469), 어느 단계도 키를 정규화하지 않는다.

### `test_publication_signature_distinguishes_exact_unicode_payload` (행 243–252)
- 성질: 엔진이 "변경 없음"을 판정할 때 유니코드 정규화로 같은 문자열(결합 문자 대 합성 문자)을 다른 내용으로 구별한다.
- 준비: `routing_engine()`, `head = 'snapshot'`. 형식 결과 `FR-one`의 `lean_code`를 `'-- "é"'`로 둔다. `engine.store`를 `create_autospec(ResearchRepository, instance=True)`로 바꾸고 `published_state`가 현재 인스턴스·런타임의 깊은 사본을 돌려주게 한다.
- 실행: `engine._unchanged()`를 두 번. 두 번째 전에 `lean_code`를 합성 문자 `'-- "é"'`로 바꾼다.
- 단언: 첫 호출은 참이고 `published_state`가 `'snapshot'`으로 불렸다. 둘째 호출은 거짓이다.
- 대역: `ResearchRepository`의 `create_autospec` 인스턴스.
- 비고: 주석(행 244)이 연결을 적는다. `_save`는 `_unchanged()`가 이 헤드의 공개 상태와 같다고 판정하지 않는 한 공개한다. 제품 `_unchanged`의 docstring은 비교가 `updated_at`만 빼고 이루어진다고 밝힌다.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈: 실제 Lean으로 형식 검사를 돌리는 시험은 `lean` 표지를 단 모듈들이 맡고, 이 모듈은 컴파일러 대역으로 엔진의 분기만 본다. 공개 수명주기와 허가 수락은 `parked_formal_check`의 주석이 가리키듯 `test_engine.PublicGitFlow`와 수명주기 주인 시험(`test_lifecycle_engine`)이 다룬다. 신뢰 환경의 등록·검증은 신뢰 영역 모듈들이 다룬다.
- 픽스처 의존: `engine_fixtures.formal_check_engine`(`FormalContinuationTests.make`), `formal_verification`(재적재 뒤 컴파일러 대역), `routing_engine`(`parked_formal_check`, `run_verifier`, 마지막 시험); `research_fixtures.await_stop`(정지 대역의 폴링), `send_control`(공개 제어), `trust_fixture`·`trust_environment`(합성 신뢰 환경); `state_fixtures.owner_calls`(주인 루프 흉내), `start_active_copy`(2단 사본).
- 이 모듈에만 있는 도우미: 모듈 함수 `parked_formal_check`, 클래스 도우미 `make`, `stopped_check`, `run_with_control`, `run_verifier`.
- 겹침과 보완: 일시정지·재개·계속의 흐름은 `FormalContinuationTests`(메모리 엔진, 반복 재개와 조건 변경까지)와 `FormalAttemptLineageTests`(Git 저장과 재적재)가 두 층에서 본다. 대기 재개 규칙은 `FormalAuthority`가 `_resume_formal_waits`를 직접 불러 좁게 본다. `FormalBindingConnections`는 검증기 호출 인자와 저장 결과물의 정확성을 본다.

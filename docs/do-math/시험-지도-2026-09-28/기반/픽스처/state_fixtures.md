# state_fixtures

| 항목 | 값 |
|---|---|
| 원문 | `.claude/skills/do-math/scripts/tests/state_fixtures.py` (147행) |
| 정의 수 | 모듈 함수 6(`active_instance`, `active_repository`, `start_active_copy`, `owner_calls`, `start_model_call`, `complete_academic_task`), 클래스 0, 모듈 수준 상수 2(`ACTIVE_LEAN_COMMAND`, `ACTIVE_CONFIG`) |
| 이 모듈을 쓰는 시험 모듈 | 20개(`consumers.json` 기준). 이 밖에 픽스처 모듈 `engine_fixtures`, `purpose_fixtures`가 이 모듈을 쓴다 |
| 모듈 수준 import | 제품 `do_math.repository`의 `ResearchRepository`, `new_id`. 픽스처(`engine_fixtures`, `research_fixtures`)는 함수 안에서 늦게 import한다 |

## 목적

모듈 docstring(행 1–14)은 이 모듈을 "초기화 뒤를 검사하는 시험을 위한 검증된 시작 상태와 소유자 루프 도우미"라고 부른다. 이 모듈은 두 가지를 맡는다.

1. **2단 시작 상태.** `active_instance`는 `research_fixtures.restore_template`에 넘기는 템플릿 빌드다. 합성 어댑터 증거, 신뢰 증거, 해석 증거를 `engine_fixtures.FakeEngine`으로 조립하고, 그 결과를 실제 저장소 검증을 거쳐 게시한다. docstring(행 6–7)에 따르면 이 빌드는 공개 초기화 워크플로가 작동함을 입증하지 않는다. `active_repository()`는 이 상태를 `ACTIVE_CONFIG`로 복원한 사본이다. `start_active_copy(test)`는 어댑터 관찰을 바꾼 채 그 사본을 시험에 준다. `시험-지침.md` 4절 규칙 3의 2단이 바로 `restore_template(state_fixtures.active_instance, config=...)`이며, 지침은 이 상태가 "약 1초 만에" 준비된다고 적는다.
2. **소유자 루프 도우미.** `owner_calls(engine)`와 `start_model_call(engine, action)`는 스케줄러의 소유자 루프가 하듯 기계 단계와 모델 호출을 돌린다. `complete_academic_task`는 합성 반환 보고서로 과제 하나를 완료한다.

## 구성

화살표(→)는 "부른다"를 뜻한다.

1. **2단 시작 상태.** `active_instance` → `research_fixtures.git_init`·`FixtureAdapter`, `engine_fixtures.FakeEngine`(`activate`), 제품 `ResearchRepository.initialize`·`new_id`. `active_repository` → `research_fixtures.restore_template(active_instance, config=ACTIVE_CONFIG)`. `start_active_copy` → `active_repository`, `research_fixtures.FixtureAdapter`. 상수 `ACTIVE_LEAN_COMMAND`와 `ACTIVE_CONFIG`가 이 무리에 속한다.
2. **소유자 루프.** `owner_calls` → 제품 `parallel.ModelCalls`, 엔진의 `_local_call_returned`·`_observation_failed`·`_transport`·`_publish_control_request`. `start_model_call` → 엔진의 `_action_lifecycle_gate`·`_call_steps`·`_calls.start_call`·`runner.run`.
3. **과제 완료.** `complete_academic_task` → `research_fixtures.assessment`, 제품 `execution_lifecycle.transition_execution`·`task_scope.apply_task_assessments`, 엔진의 `_register_execution`·`_lifecycle_now`·`_record_academic_assessment`·`_ensure_academic_followup`·`_save`.

## 2단 시작 상태

### `active_instance(root, shared, *, config, external_policy='explicit_grants', review_policy=None)` (행 29–54)
- 종류: 템플릿 빌드(`research_fixtures.restore_template`에 넘긴다).
- 하는 일과 반환값: 합성 활성 상태를 만들고 인스턴스 ID를 돌려준다. 절차는 다음과 같다.
  1. `git_init(root / "repository")`로 빈 저장소를 만들고, 작업 공간 `root / "work-0"`을 만든다.
  2. `do_math.initialization.adapter_for`를 `FixtureAdapter()` 하나를 돌려주는 패치(`return_value`)로 덮는다. 이 패치 안에서 3–4를 한다.
  3. `FakeEngine(workspace, config=config)`로 메모리 씨앗 엔진을 만든다. 씨앗의 인스턴스 ID는 `RI-test`이고 작업 공간은 `work-0`이다. 설정은 `DEFAULT_CONFIG`에 관찰 창 두 값과 `config`를 덮은 것이며, `research_reconsider_seconds=60`이 붙는다.
  4. 씨앗의 `root`를 `Path(shared)`로 바꾼 뒤 `seed.activate(external_policy=..., review_policy=...)`를 부른다. `FakeEngine.activate`의 동작은 다음과 같다.
     - 권한 둘을 준다.
     - 헌장 `CH-test`를 채택한다.
     - AI 프로필마다 `FixtureAdapter().describe()`로 능력 증거를 기록한다.
     - 초기화 채택 결정을 적용한다.
     - `environment('base', True)`로 신뢰 환경을 등록하고 전환한다. 이때 `trust_fixture(self.root/'base', ['synthetic-lean','base'])`를 쓰므로 합성 도구 사슬이 `shared/base` 아래에 생긴다.
     - `research_fixtures.intent_response`로 해석과 확인을 메모리 안에서 적용한다.
     - 활성화를 마친다.
  5. 씨앗 런타임을 정리한다. `processed_controls=[]`, `reservations={}`, `provider_waits={}`로 비우고, `updated_at`은 `last_observed_utc`로 맞춘다. `next_research_reconsider_at`은 `"2100-01-01T00:00:00+00:00"`으로 둔다. 원문에는 이 값을 고른 이유가 적혀 있지 않다.
  6. 새 ID `new_id("RI")`를 만든다. `[instance, runtime]`을 JSON 문자열로 직렬화해 모든 `"RI-test"`를 새 ID로 치환한 뒤 다시 읽는다.
  7. 제품 `ResearchRepository(repository, identifier).initialize(instance, runtime)`로 게시한다. docstring(행 5–6)의 "실제 저장소 검증을 거쳐 게시한다"가 이 단계다.

  docstring(행 34–35)에 따르면 `external_policy`와 `review_policy`는 `research_fixtures.activate`에서처럼 채택 결정으로 가고, `review_policy=None`이면 기본 정책을 채택한다. `external_policy` 기본값은 `'explicit_grants'`다. `research_fixtures.activated_instance`의 기본값 `'disabled'`와 다르다.
- 부작용: `root/repository`에 Git 저장소와 첫 게시 상태가 생기고, `root/work-0` 디렉터리가 생긴다. `shared/base` 아래에는 합성 도구 사슬과 기록이 생긴다. docstring(행 33)에 따르면 도구 사슬을 `shared`에 두는 까닭은 복원된 사본이 그 지문을 유지하게 하려는 것이다. 공개 `initialize`, 공개 제어, 실제 해석 실행, 모델 실행 자식 프로세스는 쓰지 않는다. Git 자식 프로세스는 쓴다. `git_init`의 프로세스당 첫 `git init`이 하나이고, 7단계의 `ResearchRepository.initialize`가 제품 `GitStateStore._git`(`git_store.py` 행 540)을 거쳐 Git 명령마다 자식 프로세스를 띄운다.
- 의존: `research_fixtures.git_init`·`FixtureAdapter`, `engine_fixtures.FakeEngine`, 제품 `ResearchRepository.initialize`, `new_id`.
- 시작 상태의 단: 2단.
- 소비자: `purpose_fixtures`, `test_academic_engine`, `test_controls`, `test_currentness`, `test_engine`, `test_input_recovery`, `test_lifecycle_engine`, `test_provider_recovery`, `test_purpose_engine`, `test_research_recovery`, `test_session_scheduler`, `test_stop_flags`, `test_submission_boundaries`. 모듈 안에서는 `active_repository`가 부른다.

### `active_repository()` (행 61–69)
- 종류: 함수.
- 하는 일과 반환값: `restore_template(active_instance, config=ACTIVE_CONFIG)`를 불러 `(root, root / "repository", 인스턴스 ID)`를 돌려준다. docstring(행 64–65)에 따르면 작업 공간은 `root / 'work-0'`이고, 인스턴스가 그 경로를 이름으로 가진다. `external_policy`와 `review_policy`는 기본값으로 채워진다. `restore_template`는 기본값을 열쇠에 넣으므로, 같은 설정을 명시한 다른 호출과 같은 템플릿을 공유한다.
- 부작용: `restore_template`와 같다. 프로세스의 첫 호출은 빌드하고, 이후 호출은 앞 사본을 지우고 새로 복사한다.
- 의존: `active_instance`, `ACTIVE_CONFIG`, `research_fixtures.restore_template`.
- 시작 상태의 단: 2단.
- 소비자: `test_research_recovery`, `test_trust_continuation`. 모듈 안에서는 `start_active_copy`가 부른다.

### `start_active_copy(test)` (행 72–79)
- 종류: 함수(시험 준비 도우미).
- 하는 일과 반환값: `test.enterContext(patch("do_math.initialization.adapter_for", return_value=FixtureAdapter()))`로 어댑터 관찰을 시험이 끝날 때까지 합성 대역으로 바꾼다. 그다음 `active_repository()`의 세 값을 `test.root`, `test.repo`, `test.identifier`에 넣는다. 반환값은 없다.
- 부작용: 시험 수명 동안의 `mock.patch` 하나, 템플릿 사본 복원, 시험 객체 속성 세 개.
- 의존: `active_repository`, `research_fixtures.FixtureAdapter`. `TestCase.enterContext`(Python 3.11+)를 쓴다.
- 시작 상태의 단: 2단.
- 소비자: `engine_fixtures`, `test_academic_engine`, `test_controls`, `test_formal_engine`, `test_initialization_probe_batch`, `test_input_recovery`, `test_review_engine`, `test_session_scheduler`.

## 소유자 루프

### `owner_calls(engine)` (행 83–105)
- 종류: 함수(`@contextmanager` 하네스).
- 하는 일과 반환값: 블록 안에서 시작된 호출을 제품 `ModelCalls` 위에서 스케줄러처럼 돌린다(docstring 행 84–89). docstring에 따르면 엔진에는 동기 호출 경로가 없고, 기계 단계와 모델 호출은 모두 `engine._calls`에서 시작한다. 동작은 다음과 같다.
  - **진입.** 새 `ModelCalls(on_returned=engine._local_call_returned, on_observation_error=engine._observation_failed)`를 만들어 `engine._calls`에 넣고 블록에 `yield`한다.
  - **블록 종료 뒤.** 블록이 정상으로 끝나면 `calls.futures`가 빌 때까지 다음을 되풀이한다.
    1. `calls.wait(0.05)`
    2. `calls.pump()`로 콜백에 응답한다.
    3. `engine._transport`가 있으면 `engine._transport.pump(engine._publish_control_request)`로 제어 수송 요청을 받는다. 주석(행 99)에 따르면 소유자 루프는 매 회차 수송을 펌프한다(`engine._controls`). docstring(행 87–88)에 따르면 제출 의도는 그 영수증을 기다린다.
    4. `calls.collect()`로 호출을 수거하고 이어서 할 일을 재개한다.
  - **정리.** `finally`에서 `calls.close()`하고 `engine._calls = None`으로 되돌린다. 블록 안에서 예외가 나면 대기 반복 없이 이 정리만 한다.
- 부작용: 호출이 띄우는 실행과 자식 프로세스(러너에 따라 다르다). 엔진 속성 `_calls`의 일시 교체.
- 의존: 제품 `do_math.parallel.ModelCalls`, 엔진의 비공개 메서드 `_local_call_returned`, `_observation_failed`, `_publish_control_request`와 속성 `_transport`.
- 소비자: `test_formal_engine`, `test_knowledge_import_engine`, `test_lifecycle_engine`, `test_machine_parallel`, `test_review_engine`.

### `start_model_call(engine, action)` (행 108–121)
- 종류: 함수.
- 하는 일과 반환값: AI 행동 하나의 호출을 스케줄러처럼 시작한다. `owner_calls` 블록 안에서 쓴다. docstring(행 111–112)에 따르면 스케줄러는 호출을 시작하는 회차에 그 행동의 수명 주기 관문(`_dispatchable`)을 통과시킨다. 그래서 이 함수도 먼저 `engine._action_lifecycle_gate(action)`를 부른다. 이어서 다음을 한다.
  1. 엔진의 생성기 `engine._call_steps(action)`를 만들고 첫 값을 꺼낸다.
  2. 생성기가 곧바로 끝나면(`StopIteration`) 그 반환값을 돌려준다.
  3. 아니면 `engine._calls.start_call(generator, engine.runner.run, arguments, execution_id=arguments.get('execution_id'))`로 러너 호출을 시작하고 `False`를 돌려준다.
- 부작용: 엔진 상태 변경(실행 등록 등, 제품 동작), 러너 호출 시작.
- 의존: 엔진의 `_action_lifecycle_gate`, `_call_steps`, `_calls`(`owner_calls`가 설정), `runner.run`.
- 소비자: `test_review_engine`.

## 과제 완료

### `complete_academic_task(engine, task, basis)` (행 124–147)
- 종류: 함수.
- 하는 일과 반환값: 합성 반환 보고서를 공급하고, 실제 독립 평가 규칙을 적용한다(docstring 행 125). 절차는 다음과 같다.
  1. **실행 두 개 등록.** 역할 `research_work`와 `research_plan`마다 새 행동(`new_id("AC")`, 대상은 과제)과 실행(`new_id("EX")`, `status="running"`, `input_solution_basis`는 `basis`의 깊은 사본)을 `engine._register_execution`으로 등록한다.
  2. **실행 종료.** 두 실행 모두 `engine._lifecycle_now()` 시각으로 제품 `transition_execution`을 두 번 적용한다. 먼저 `stopping`, 이어서 `ended`(`outcome="execution_incomplete"`)다.
  3. **보고서 공급.** 인자 `task`의 `results`를 작업 실행 ID와 보고서 "Synthetic returned academic account." 한 행으로 덮는다.
  4. **평가 적용.** `research_fixtures.assessment(task)`로 완료 평가를 만든다. 제품 `apply_task_assessments(instance, runtime, [평가], execution_id=계획 실행, input_tasks=런타임 과제의 깊은 사본)`로 적용하고, 결과를 엔진 상태에 넣는다.
  5. **학술 평가 기록.** `engine._record_academic_assessment(런타임 과제, 평가, 계획 실행)`, `engine._ensure_academic_followup()`, `engine._save()`를 차례로 부른다.

  반환값은 없다.
- 부작용: 인자 `task`의 `results` 필드를 바꾼다. 엔진 상태를 바꾸고, `_save`로 게시한다. 실제 모델 호출이나 자식 프로세스는 없다.
- 의존: `research_fixtures.assessment`, 제품 `execution_lifecycle.transition_execution`, `task_scope.apply_task_assessments`, `new_id`, 엔진의 비공개 메서드 다섯.
- 소비자: `test_academic_engine`.

## 상수와 모듈 수준 이름

- `ACTIVE_LEAN_COMMAND` (행 26): `('synthetic-lean', 'base')`. 주석(행 23–25)에 따르면 `FakeEngine.activate`는 자기 활성 신뢰 환경을 이 명령으로 등록한다(`environment('base', ...)`가 명령 `['synthetic-lean', 'base']`를 쓴다). 형식 검사는 설정된 명령을 고정하고, 그 명령은 이 환경과 같아야 한다. 공개 활성화에서는 활성화가 이 일치를 맞춰 주지만, 합성 상태에서는 형식 검사가 필요한 호출자가 설정에 이 명령을 넣는다. `research_fixtures` docstring(행 131–132)은 그 방법으로 `lean_command=list(state_fixtures.ACTIVE_LEAN_COMMAND)`를 지시한다. 소비자: `test_engine`, `test_purpose_engine`, `test_review_research`, `test_session_scheduler`, `test_submission_boundaries`, `test_submission_tools`.
- `ACTIVE_CONFIG` (행 58): `{'tool_review_window_seconds': 60, 'self_check_response_window_seconds': 5}`. 주석(행 57)에 따르면 대부분의 시험이 시작하는 사본(`active_repository`)의 설정이다. 값은 `research_fixtures.activate`가 명시적으로 승인하는 관찰 창 두 값과 같다. 소비자: `test_input_recovery`. 모듈 안에서는 `active_repository`가 쓴다.

## 관계

**다른 픽스처 모듈과의 의존.** 이 모듈은 `research_fixtures`(`restore_template`, `git_init`, `FixtureAdapter`, `assessment`)와 `engine_fixtures`(`FakeEngine`)에 기댄다. 모두 함수 안에서 늦게 import한다. 반대 방향으로는 `engine_fixtures`가 `start_active_copy`를, `purpose_fixtures`가 `active_instance`를 쓴다. `active_instance`와 `FakeEngine` 사이에는 계약이 하나 있다. `active_instance`는 씨앗의 `root`를 `shared`로 바꾸고, `FakeEngine.environment`는 그 `root` 아래에 신뢰 도구 사슬을 만든다. 그래서 도구 사슬이 복사되지 않는 `shared`에 놓인다.

**시작 상태 체계에서 맡는 자리.** 이 모듈은 `시험-지침.md` 4절 규칙 3의 2단을 맡는다. 2단은 공개 해석 실행과 공개 제어 없이 검증된 활성 상태를 만들므로 3단(`research_fixtures.activated_instance`)보다 싸다. 대신 docstring(행 6–7)이 말하듯 공개 초기화 경로가 작동함을 입증하지 않는다. `owner_calls`와 `start_model_call`은 시작 상태가 아니라 구동 도구다. 2단이나 3단 사본에서 만든 엔진, 또는 메모리 엔진으로 기계 단계와 모델 호출을 스케줄러 없이 한 단계씩 돌릴 때 쓴다.

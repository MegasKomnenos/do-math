# 결과-K시험: 시험 기반 커널

- worktree: `C:/math-worktrees/r2-ktest` (브랜치 `r2-ktest`)
- 커밋: `a278e60` (58개 파일, 704줄 추가, 826줄 삭제)

아래 경로는 따로 적지 않으면 `.claude/skills/do-math/scripts/` 기준이다.

시험 파일 변환은 네 작업자(A~D)에게 파일 단위로 나눠 맡겼다. 이들은 같은 worktree에서 서로 겹치지 않는 파일만 고쳤다. 공통 계약과 작업자별 결과는 `C:/math-worktrees/reports/r2-ktest/`에 있다(`파견-공통.md`, `결과-A.md`~`결과-D.md`). 파일별 변환 수와 좌표는 그 결과 파일에 있다.

## 1. ID별 처분

### TST-01: 구현함. 제품 쪽 `_save` 부분은 전제가 틀려 변형했다(5절)

**제품 쪽**
- `ResearchEngine.__init__`에서 프로세스 상태 초기화를 `_init_process_state(self, *, transport=None)`로 추출했다(`do_math/engine.py`).
  - 이 메서드는 `_task_readiness`, `_live_execution_ids`, `_executor_running`, `_calls`, `_slots`, `_next_installation_check`, `_preparing_input`, `_transport`, `_transport_bindings`, `_trackers`를 초기화한다. 조사 제안대로 `_stop_deadlines`, `_stop_clock`, `_clock_anchor`의 초기값도 여기서 준다.
  - `__init__`은 `_require_current_contract` 뒤에 이 메서드를 부르고, 실제 `ControlTransport`는 여기에만 넘긴다. `_saved_state`와 `_require_current_contract`는 `__init__`에 남겼다.
- 방어 `getattr` 14곳(15개 식)을 직접 접근으로 바꿨다.
  - `engine.py`: `_slots` 2, `_transport` 2, `_trackers` 1, `_calls` 1
  - `governance_engine.py:56-57`: 3
  - `lifecycle_engine.py`: 3
  - `scheduler.py:31, 86, 198`: 3
- 줄 이동·재정렬은 하지 않았다.

**시험 쪽**
- `tests/research_fixtures.py`에 `bare_engine(instance=None, runtime=None, *, head, store, runner, formal_verifier)`을 두었다. 이 함수는 `object.__new__(ResearchEngine)` 뒤에 `_init_process_state()`를 부르고, `_saved_state`를 `None`으로 둔다.
- 우회 생성 29곳과 `routing_engine`을 `bare_engine`으로 바꿨다. 조사 목록에 없던 믹스인 직접 인스턴스와 `SimpleNamespace` 엔진 대역도 같은 방식으로 바꿨다.
  - `DecisionEngineMixin()`, `ProviderEngineMixin()`, `GovernanceEngineMixin()`, `ReviewEngineMixin()`
  - `test_approved_five_repairs`의 `SimpleNamespace` 엔진 대역
- `FakeEngine`(`tests/test_lifecycle_engine.py`)을 `class FakeEngine(ResearchEngine)`로 바꿨다.
  - 대입 차용 6줄, `_evaluation_context`·`_enqueue` 재구현, 속성 복제를 지웠다.
- 믹스인을 조합한 지역 클래스는 모두 없앴다.
  - 대부분은 `bare_engine()` 위에서 재정의하던 메서드만 autospec으로 바꿨다.
  - `test_review_engine.FakeEngine`은 제품에 없는 시험 전용 이름(`pending`, `execute` 등)을 더하므로 `ResearchEngine` 하위 클래스로 두었다.
  - `test_connection_repairs.FormalEngine`은 지웠다.
- `test_stop_flags.py:56`의 제품 초기화 줄 복제를 지웠다.
- `test_governance_engine`의 클래스 속성 `_live_execution_ids = set()`(모든 인스턴스가 공유하던 것)도 사라졌다.

### TST-02: 구현함

- 인스턴스 메서드 대체를 `engine.X = create_autospec(engine.X, return_value=… | side_effect=…)` 형태로 바꿨다.
  - `Mock`·`MagicMock` 대입, 람다, 함수 대입, `setattr` 루프가 대상이다.
  - `test_redesign_ENGINE` 96곳과 나머지 파일의 약 90곳이다.
- store 대역(`Mock()`, `SimpleNamespace`)을 `create_autospec(ResearchRepository, instance=True)`로 바꾸고 필요한 반환만 설정했다.
  - 조사가 센 25곳에 `_repository` patch로 넘기던 지역 store 3곳을 더했다.
  - `store = object()`는 `None`으로 바꿨다(5절).
- `test_walkthrough_contract_repairs`의 손 `Calls`를 `create_autospec(ModelCalls, instance=True)`로 바꿨다.
- 조사 제안의 `patch.object(..., autospec=True)` + `enterContext` 대신 대입형 `create_autospec`을 표준으로 정했다(5절).
- 바꾸지 않은 곳은 다음과 같다.
  - 상태 속성: `_transport = Mock()`, `lifecycle_clock`, `formal_verifier`
  - store·ModelCalls 밖의 협력자: `runner`, `SessionSlots` 대역

### TST-03: 부분 구현

- `_enqueue` 재구현 8곳과 `_remove_action` 재구현 4곳을 모두 지웠다. 이제 제품 판이 돈다.
- 실제 `ResearchRepository` 위에서 게시와 재적재를 다시 적은 `_save`는 지웠다. 이제 제품 `_save`가 그 store에 게시한다.
  - `test_repair_execution.RepositoryHost`
  - `test_redesign_ENGINE` 2곳
  - `test_six_connections` 1곳
- 남은 범위: `FakeEngine._save`(사본을 `saves`에 기록)와 `FakeEngine._controls`(무동작)는 남겼다. 이유는 5절의 전제 오류다.
  - 다른 지역 대역의 기록·무동작 `_save`·`_controls`는 `create_autospec(engine._save)`와 `create_autospec(engine._controls)`로 바꿨다.
  - `test_machine_parallel.Host`의 `_save` 래퍼(소유 스레드 검사와 `_evaluate_stops`)도 남겼다.

### TST-04: 구현함

- `FixtureAdapter(capabilities=FIXTURE_CAPABILITIES)`를 정본 하나로 두었다.
- `AdapterDouble`과 그 `IDENTITY`를 지웠다.
- 사용처 48곳(import 18줄 포함)을 `FixtureAdapter()`로 바꿨다. `test_lifecycle_engine`은 공유 `IDENTITY`를 참조한다.
- `test_initialization_probe_batch`의 지역 변형 3곳은 `FixtureAdapter` 하위 클래스로 두고 `describe`만 재정의했다.
- 같은 파일 24행의 `Mock()` 어댑터는 두었다. 호출 횟수를 관찰하는 대역이라 `describe`만 다른 변형이 아니기 때문이다.
- 두 대역의 `scope` 차이는 기본 능력 3개가 모두 command surface 안이라 상태 판정에 영향이 없다. 증거 ID는 바뀌지만, 증거 ID를 단언하는 시험은 없다.

### TST-05: 구현함

- `research_fixtures.review_items(evidence_refs, *, decision, next_owner, findings)`를 두었다. `contract_review`는 이 함수를 부른다.
- 다음 조립 7곳과 항목 리터럴 2곳(`test_redesign_TASKS.approve`, `FakeEngine.approve`)을 이 함수 호출로 바꿨다.
  - `test_contracts`
  - `test_redesign_CONTRACTS` (`"MISSING"`을 인자로 넘김)
  - `test_redesign_EVIDENCE`
  - `test_redesign_GOVERNANCE`
  - `test_redesign_TASKS` 3곳

### TST-07: 구현함

- `run_tests._module_keys`의 원천을 `tests/*.py` 전체로 넓혔다. `MODULE_IMPORT`는 모든 모듈 이름을 추적하고, 소스 키 집합과의 교집합이 `tests/` 밖 이름을 거른다.
- `_input_key`는 `tests/*.py`를 뺀다(`_is_test_source`).
- 모듈 설명문을 고쳤다.
- 시험 `test_a_fixture_module_is_keyed_with_the_test_modules_it_imports`를 더했다. 이 시험은 두 가지를 확인한다.
  - 픽스처를 거친 시험 모듈 의존이 추적된다.
  - 픽스처 수정이 그 픽스처를 import하는 모듈만 무효화한다.

### TST-09: 구현함

`trust_fixture`의 지역 람다를 지우고 `do_math.file_io.sha256_file`을 직접 부른다.

### TST-10: 부분 구현

- `research_fixtures.new_instance(repository, *, goal, workspace=None, **options) -> instance_id`를 두었다.
- 21곳을 바꿨다.
  - `test_lifecycle_engine` 5
  - `test_redesign_ENGINE` 4
  - `test_static_review_repairs` 2
  - `test_provider_recovery` 2
  - `test_knowledge_import_engine`, `test_connection_repairs`, `test_initial_intent_connection`, `test_observation_admission`, `test_governance_engine`, `test_redesign_SURFACE`, `test_delegation_storage`, `test_session_scheduler`, `test_controls` 각 1
- 남은 범위와 그 이유는 다음과 같다.
  - **저수준 초기화:** `git init` 뒤가 공개 `initialize`가 아니라 저수준 `ResearchRepository.initialize`/`GitStateStore`인 곳(약 20곳)은 다른 일이라 두었다.
  - **`initialize` 반환의 다른 키:** `test_query_records`는 `initialize`의 반환에서 `snapshot`을 쓰므로 두었다.
  - **setUp 저장소를 두 경로가 함께 쓰는 곳:** `PurposeHarness.setUp`, `test_engine.EngineTests.setUp`, `test_redesign_STORAGE.setUp`, `ParallelEngineTests.setUp`은 setUp에서 만든 저장소를 공개 `initialize`와 `state_fixtures.active_engine`(저수준 초기화)이 함께 쓴다. `new_instance`로 바꾸면 `git init`이 중복되거나 `active_engine` 경로가 깨진다. 바꾸려면 `active_engine`의 저장소 생성 계약을 먼저 정해야 한다(4절 후속).

### TST-06, TST-08

설계 5절에 따라 하지 않았다.

## 2. 만든 공유 정의와 위치

| 정의 | 위치 | 쓰임 |
|---|---|---|
| `ResearchEngine._init_process_state(*, transport=None)` | `do_math/engine.py` | 제품 생성자, `bare_engine`, `FakeEngine`, 시험 전용 하위 클래스 |
| `bare_engine(...)` | `tests/research_fixtures.py` | 저장소 없이 상태만 주는 엔진 |
| `new_instance(...)` | `tests/research_fixtures.py` | `git init`과 공개 `initialize` |
| `review_items(...)` | `tests/research_fixtures.py` | 모든 계약 항목에 같은 판정을 주는 검토 출력 |
| `FIXTURE_CAPABILITIES`, `FixtureAdapter(capabilities=…)` | `tests/research_fixtures.py` | 어댑터 관찰 대역의 정본 |
| `FakeEngine(ResearchEngine)` | `tests/test_lifecycle_engine.py` | 메모리 상태 위의 제품 엔진. 게시 대신 사본을 기록한다 |
| `run_tests.MODULE_IMPORT`, `_is_test_source` | `run_tests.py` | `tests/` 전체 모듈 의존 키 |

메서드 대체의 표준 형태는 `engine.X = create_autospec(engine.X, ...)`이다.
- 없는 이름은 `AttributeError`, 서명이 틀린 호출은 `TypeError`로 실패한다.
- 같은 메서드를 두 번 대체하면 `InvalidSpecError`가 난다. 두 번째 대체는 첫 가짜의 `side_effect`나 `return_value`를 고친다.
- 제품에 순수 픽스처 판별이 있어서, "`load`가 없는 store"가 필요하면 autospec store에서 `del store.load`를 한다(`test_lifecycle_engine`의 artifact 문맥 시험 1곳).

그룹 작업자가 이 기반 위에서 시험을 고칠 때 알아야 할 사실이 둘 있다.
- 제품 `_enqueue`는 모든 실행 행의 `status`를 읽는다.
- 제품 `_save`는 `runtime['tasks']`를 읽는다.

그래서 손으로 만든 최소 상태에는 실제 상태가 늘 가진 이 키가 있어야 한다. 이번에 그렇게 맞춘 곳이 7곳이다.

## 3. 필요한 문서 변경

- `C:/math/.claude/skills/do-math/AGENTS.md`의 검증 문단은 캐시 입력을 "그 시험 모듈과 그 모듈이 import하는 시험 모듈"로 설명한다. TST-07 뒤에는 이렇게 바꾼다: "시험 모듈과 그 모듈이 import하는 `tests/`의 모든 모듈(공용 픽스처 포함, 전이적으로)". 이 파일은 스킬 트리 밖(저장소 루트 쪽 스킬 디렉터리의 개발 원칙)이라 문서 단계가 판단한다.
- `docs/do-math/검사-경량화-이음새-계약.md`의 시험 픽스처 절에 2절의 정의를 추가한다. 커널 단계 뒤 통합자가 이음새 계약을 옮길 때 함께 옮긴다.

## 4. 시험

모든 명령은 worktree의 `scripts`에서 `python run_tests.py --group unit --group integration --match ...`로 돌렸다. 결과 디렉터리는 `C:/math-worktrees/reports/r2-ktest/<이름>/report.json`이다.

| 실행 | 범위 | 결과 |
|---|---|---|
| K-2 | test_lifecycle_engine, test_machine_parallel, test_test_runner | 97 통과 |
| A-1, A-3 | test_redesign_ENGINE | 64 통과, 2 오류. 기준선 1건과 `tasks` 키 1건이었고, 후자는 고친 뒤 A-3에서 통과 |
| B-1, B-2 | B의 17개 모듈 | 266 통과, 2 오류. 1건은 고친 뒤 통과, 1건은 T-1·T-2로 넘어감 |
| C-2, C-3 | C의 19개 모듈과 RecoveryBoundaryRepairs | 417 통과, 9 실패. 새 실패 3건은 고친 뒤 C-3에서 통과, 나머지 6건은 기준선 |
| D-2 | D의 21개 모듈 | 280 통과, 5 실패. 5건 모두 기준선 |
| F-0, F-1 | 영향 모듈 86개(중단) | 381 통과, 실패 0. 불필요한 재실행이라 중단(아래) |
| T-1, T-2 | 뒤늦은 변경에 닿는 시험만 | 26개 가운데 23 통과, 3 오류. 셋 모두 합성 실행 행의 `status` 누락이었고, 고친 뒤 T-2에서 통과 |

- **새 실패: 0건.** 남은 실패는 모두 M-0348의 기준선이다.
  - `test_session_scheduler.ParallelEngineTests` 4건
  - `test_redesign_ENGINE` resume 1건
  - `test_redesign_GOVERNANCE` 4건
  - `test_purpose_engine` live_continue 1건
  - `test_walkthrough_repairs` 2건
- 기준선 가운데 `ParallelEngineTests.live_operations`는 D-2에서 통과했다.
- `test_submission_tools.ReviewFailureTests` 5건은 이번에 돌리지 않았다. 이 모듈은 바뀐 도우미를 쓰지 않는다.

**시험 캐시.** 작업자 실행은 다른 작업자가 파일을 고치는 동안 돌았다. 그래서 `changed_during_run` 표시가 붙었고 결과 캐시가 기록되지 않았다. 통과 증거는 각 `report.json`에 있지만, 통합 단계의 첫 실행은 캐시 없이 돈다.

**F-0·F-1 중단.** 처음에는 바뀐 시험 모듈을 import 폐포로 가진 86개 모듈을 다시 돌렸다. 사용자의 검토 요청으로 선택 기준을 다시 확인했더니 대부분이 불필요한 재실행이었다.
- 35개는 이미 통과했고, 그 뒤 의존 파일이 바뀌지 않았다.
- 30개는 바뀌지 않은 도우미만 import할 뿐이었다.

그래서 이 실행은 약 10분 만에 중단했다. 그 대신 늦게 바뀐 도우미(C의 수정 3건과 `test_review_research` 수정)를 실제로 호출하는 시험만 T-1로 돌렸다.

## 5. 전제가 틀렸거나 계획을 바꾼 지점

1. **TST-03 `_controls`**
   - 조사 전제: 제품 `_controls`는 `_calls`와 `_transport`가 없고 inbox가 비면 아무것도 하지 않는다.
   - 실제: inbox 처리 뒤에 `_schedule_operational_reviews`, `_retry_submission_publications`, `_retry_impact_reviews`, 검토 자원 정리, `continue_initial_retries`, `_run_pending_operational_repairs` 등을 한다(`do_math/engine.py`의 `_controls` 끝부분).
   - 조치: 무동작 재정의는 지우지 않고 autospec 무동작으로 두었다. `FakeEngine._controls`도 남겼다.
2. **TST-03 `_save`**
   - 조사 방안은 autospec store의 `save_with_state.side_effect`에 게시를 맡기는 것이었다. 이 방안은 제품의 순수 픽스처 분기와 충돌한다.
   - `lifecycle_engine._verify_current_head`와 `_apply_extended_control`의 거부 보존 경로는 `callable(getattr(store, 'load', None))`일 때 store에서 현재 상태를 읽어 검사한다. autospec store는 `load`가 호출 가능하므로 이 검사가 가짜를 읽고 "damaged current state"로 거부한다.
   - 조치: `FakeEngine`은 `store=None`과 기록형 `_save`를 유지한다.
   - 후속 후보: 이 분기(`# Pure mixin fixtures have no persisted head.`) 자체가 시험을 위한 제품 방어다. 엔진 대역이 모두 파생된 지금, 대역에 store 계약을 주는 방식으로 이 분기를 없앨 수 있는지 검토할 수 있다. 이것은 K-시험 범위 밖이다.
3. **남은 방어 `getattr`**
   - `_init_process_state`가 `_clock_anchor`, `_stop_deadlines`, `_stop_clock`을 초기화하므로 다음 5곳도 이제 불필요하다.
     - `engine.py`의 `_clock_anchor`, `_stop_deadlines`
     - `lifecycle_engine.py:83`
     - `scheduler.py:56, 68`
   - 파견 범위(조사의 14곳)를 지켜 두었다. 엔진 영역 그룹이 지울 수 있다.
4. **메서드 대체 형태.** TST-02 제안의 `patch.object(..., autospec=True)` + `enterContext`는 TestCase 밖의 모듈 수준 도우미에서 쓸 수 없다. 대입형 `create_autospec(engine.X)`는 같은 검사(존재·서명)를 주면서 어디서나 쓸 수 있어 표준으로 택했다.
5. **대기열 병합 때 `import_id` 소실(확인 요청, 결함 판정 아님)**
   - `governance_engine._governance_control`은 `research_preparation`을 두 번 넣는다. 그중 하나(`governance_engine.py:196`)만 `import_id`를 가진다.
   - 제품 `_enqueue`는 `import_id`가 비교 키에 없으므로 두 요청을 한 행으로 병합하고, `import_id`를 옮기지 않는다.
   - `import_id`로 대기 행을 찾는 곳(`governance_engine.py:186`)은 해석 행동만 거른다. `research_preparation` 행의 `import_id`를 읽는 소비자는 찾지 못했다.
   - 시험(`test_governance_engine...queues_followup`)은 사유 문자열로 후속 요청을 확인하도록 바꿨다. 의도인지는 통합자가 확인한다.
6. **조사 좌표 차이**
   - TST-10의 `test_engine.formal_fail`에는 `git init`이 없다.
   - 조사가 TST-10으로 센 곳 가운데 다수는 저수준 초기화다.
   - `test_six_connections.py:336, 354`의 엔진은 순수 픽스처가 아니라 실제 저장소를 쓴다.
   - 조사 목록 밖의 믹스인 직접 인스턴스 5곳을 찾아 함께 바꿨다.
   - 기준선의 `test_redesign_GOVERNANCE` 4건의 실제 이름은 `C:/math-worktrees/reports/r2-ktest/결과-C.md` 2절에 있다.
7. **남긴 믹스인 직접 인스턴스**
   - `test_decision_basis.py:18, 61`(`DecisionEngineMixin()`)과 `test_questions.py:59, 73, 91, 166`(`QuestionEngineMixin()`)은 배분 목록 밖이라 바꾸지 않았다.
   - 두 모듈을 제품 변경 위에서 돌렸고 22개가 모두 통과했다(`C:/math-worktrees/reports/r2-ktest/T-3`). 지금은 프로세스 속성을 읽는 경로를 타지 않는다. 다만 믹스인 단독 인스턴스라는 구조는 남아 있으므로, 후속으로 `bare_engine`으로 바꿀 후보다.

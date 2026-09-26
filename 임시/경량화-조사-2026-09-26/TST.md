# TST: 시험 기반 영역 경량화 조사

조사 대상은 `C:/math/.claude/skills/do-math/scripts/tests/`(파일 140개, 약 40,659행)와 그 실행기 `run_tests.py`·`test_categories.py`다. 파견문이 정한 대로 공유 픽스처와 실행기는 전문을 읽었다. 나머지 파일은 세 발견 절차(가짜 객체, 복제된 도우미, 리터럴 재기술)를 grep으로 전수 수행해 찾은 곳만 읽었다. 이 문서의 경로는 모두 `C:/math/.claude/skills/do-math/scripts/` 아래이며, 줄여서 `tests/…`, `do_math/…`로 적는다.

## 1. 읽은 범위

**전문을 읽은 파일**

- `C:/math/임시/경량화-조사-2026-09-26/기준.md` (121행)
- `C:/math/docs/do-math/검사-경량화-이음새-계약.md` (160행)
- `tests/research_fixtures.py` (529행). 121개의 import 줄이 이 모듈을 가리킨다. 검색식은 `^\s*(from|import) research_fixtures`다.
- `tests/state_fixtures.py` (60행). 9개 import가 가리킨다.
- `run_tests.py` (412행)
- `test_categories.py` (34행)

**일부만 읽은 파일** (테스트 쪽)

- `tests/test_lifecycle_engine.py` 1-260: `AdapterDouble`, `FakeEngine`, `PublicInitializationRunner`. 다른 테스트 모듈이 이 모듈에서 가장 많이 import한다(`AdapterDouble` 18회, `FakeEngine` 16회).
- `tests/test_purpose_engine.py` 1-130, 370-499: `PurposeRunner`, `PurposeHarness`, `ActiveStateHarness`
- `tests/test_review_engine.py` 1-80
- `tests/test_redesign_LIFECYCLE.py` 1-70
- `tests/test_redesign_ENGINE.py` 26-66, 1110-1135
- `tests/test_revision_obligations.py` 1-60
- `tests/test_governance_engine.py` 1-75
- `tests/test_machine_parallel.py` 18-90, 378-392
- `tests/test_walkthrough_contract_repairs.py` 250-300
- `tests/test_walkthrough_repairs.py` 15-50, 205-250, 312-325
- `tests/test_redesign_TASKS.py` 1-75
- `tests/test_model_runner.py` 1-62
- `tests/test_codex_adapter.py` 15-40
- `tests/test_redesign_OBSERVATION.py` 14-30
- `tests/test_redesign_EVIDENCE_walkthroughs.py` 80-95
- `tests/test_stop_flags.py` 50-60, 176-190
- `tests/test_static_review_repairs.py` 178-200
- `tests/test_redesign_CONTRACTS.py` 26-45, 188-217, 609-613
- `tests/test_repair_execution.py` 18-30
- `tests/test_relation_dependencies.py` 14-22
- `tests/test_initialization_efficiency.py` 166-172
- `tests/test_six_connections.py` 421-428
- `tests/test_control_shapes.py` 36-40
- 그 밖에 아래 후보의 위치에 적은 grep 적중 줄의 전후 5행 안팎

**일부만 읽은 파일** (이음새 판정에 필요한 제품 쪽)

- `do_math/engine.py` 67-75, 570-689, 867-875, 878-957, 2594-2605, 3794-3847, 4302-4312
- `do_math/lifecycle_engine.py` 824-850
- `do_math/scheduler.py` 540-560
- `do_math/launch.py` 15-60
- `do_math/model_runner.py` 350-375
- `do_math/codex_adapter.py` 120-175
- `do_math/execution_profiles.py` 356-381
- `do_math/initialization.py` 27-35
- `do_math/repository.py` 117-이하(메서드 목록만)

**기억 노드**

- `기억/layer1/M-0348.md` 40-99
- `기억/layer3/L-0020.md`(시험 관련 줄을 grep으로 확인)

**읽지 않은 문서**

파견문에 따라 `docs/do-math/테스트-비용-전수검토-2026-09-24.md`는 읽지 않았고, 같은 폴더의 CSV도 열지 않았다.

**실행한 읽기 전용 확인**

아래 명령은 모두 저장소를 바꾸지 않는다. 테스트 스위트는 실행하지 않았다.

- `python -c "…subprocess.run([sys.executable,'-c','pass'])…"`를 5회 반복했다. Python 프로세스 하나의 기동과 종료에 0.067, 0.082, 0.057, 0.041, 0.039초가 걸렸다.
- `python -c "import run_tests as r; …"`로 해시 도우미의 소요 시간을 쟀다. `_input_key` 0.919초, `_edition` 0.066초(파일 225개), `_module_keys` 0.179초(모듈 136개)였다.
- `ResearchEngine`과 `tests/test_lifecycle_engine.FakeEngine`의 속성 집합을 비교했다(TST-01).
- 테스트가 엔진 인스턴스에 대입하는 이름을 `ResearchEngine`의 속성 집합과 대조했다(TST-02).
- `run_tests._module_keys`의 전이 폐포에 `state_fixtures`의 의존 모듈이 들어가는지 확인했다(TST-07).

## 2. 후보

#### TST-01: 엔진 대역을 제품이 소유한 단일 초기화 경로 위에 세운다

- 유형: 이음새중복

- 위치:
  - 제품 생성자: `do_math/engine.py:592-609`. `ResearchEngine.__init__`이 저장소와 무관한 프로세스 속성 11개를 설정한다(`_task_readiness`, `_live_execution_ids`, `_executor_running`, `_calls`, `_slots`, `_next_installation_check`, `_preparing_input`, `_transport`, `_transport_bindings`, `_trackers`, `_saved_state`).
  - 느슨하게 만들어지는 속성: `do_math/scheduler.py:552`의 `_stop_deadlines`·`_stop_clock`, `do_math/lifecycle_engine.py:102`의 `_clock_anchor`
  - 제품의 `getattr` 방어 14곳. `__init__`이 항상 설정하는 속성을 기본값을 붙여 읽는다.
    - `do_math/engine.py:909, 946, 1252, 1542, 1717, 4609`
    - `do_math/governance_engine.py:56-57`
    - `do_math/lifecycle_engine.py:1270, 1367, 1458`
    - `do_math/scheduler.py:31, 86, 198`
  - 믹스인 부분집합을 조합한 테스트 전용 엔진 16개. 검색식은 `^\s*class \w+\([^)]*(Mixin|FakeEngine|FixtureEngine|OwnerHarness)`다.
    - `tests/test_lifecycle_engine.py:30-53`(`FakeEngine`: 믹스인 5개, 제품 메서드 6개를 대입으로 차용 31-36, `__init__` 복제 40-53)
    - `tests/test_machine_parallel.py:23-52`(`Host(FakeEngine)`: 제품 메서드 6개를 추가 차용 24-29, `_calls`·`_live_execution_ids` 복제 34-35, `_transport_bindings` 51)
    - `tests/test_governance_engine.py:62-72`(`Host`: `_executor_running`, `_calls`, `_live_execution_ids = set()`, `_slots`를 클래스 속성으로 복제)
    - `tests/test_review_engine.py:27-83`(두 번째 `FakeEngine`)
    - `tests/test_redesign_LIFECYCLE.py:23-44`(`FixtureEngine`)
    - `tests/test_revision_obligations.py:17-32`(`OwnerHarness`)
    - `tests/test_connection_repairs.py:16`
    - `tests/test_initialization_probe_batch.py:15`
    - `tests/test_redesign_ACTIVITIES.py:234, 273`
    - `tests/test_redesign_GOVERNANCE.py:253, 351, 532`
    - `tests/test_redesign_STORAGE.py:1286`
    - `tests/test_walkthrough_contract_repairs.py:265`
    - `tests/test_walkthrough_repairs.py:22, 211`
  - `__init__`을 우회하는 생성 29곳(20개 파일). 검색식은 `__new__\(ResearchEngine\)|ResearchEngine\.__new__`와 `engine_module.ResearchEngine.__new__`다.
    - `tests/test_approved_five_repairs.py:21`
    - `tests/test_completion_settlement.py:18`
    - `tests/test_input_recovery.py:243`
    - `tests/test_knowledge_import_engine.py:112, 230, 246`
    - `tests/test_performance_repairs.py:99, 143, 171, 202`
    - `tests/test_provider_final_contract.py:61`
    - `tests/test_provider_wait.py:139`
    - `tests/test_purpose_engine.py:310`
    - `tests/test_redesign_ENGINE.py:27`(`routing_engine`, 56회 호출)
    - `tests/test_redesign_EVIDENCE.py:51`
    - `tests/test_redesign_KNOWLEDGE.py:705`
    - `tests/test_redesign_SURFACE.py:203`
    - `tests/test_redesign_TASKS.py:350`
    - `tests/test_repair_plan.py:20`
    - `tests/test_review_engine.py:863`
    - `tests/test_six_connections.py:336, 354`
    - `tests/test_static_review_repairs.py:43, 86, 253`
    - `tests/test_submission_flow.py:236, 259`
    - `tests/test_walkthrough_contract_repairs.py:40, 152`
  - 제품 초기화 줄의 복제: `tests/test_stop_flags.py:56`이 `do_math/scheduler.py:552`와 같은 줄을 다시 적는다.

- 현상:
  - 제품에서 엔진 믹스인 9개를 조합하는 클래스는 `ResearchEngine` 하나뿐이다(`do_math/engine.py:570`). 검색식 `^\s*class \w+\([^)]*Mixin`을 `do_math/*.py`와 `scripts/*.py`에 적용한 결과 1건이다. 제품 안에는 `__new__`로 `__init__`을 우회하는 경로도 없다.
  - 테스트는 이와 별도로 엔진 생성 경로 45개(믹스인 조합 16 + 우회 29)를 두고, 경로마다 `__init__`의 속성을 손으로 복제하거나 빠뜨린다. 그 결과 세 가지 문제가 생긴다.
  - 첫째, 제품이 새 속성이나 메서드를 쓰기 시작하면 대역마다 따로 깨진다. 직전 라운드의 회귀 8건 가운데 "가짜 객체에 새 이음새(`wait`, `git_dir`, `_check_conversations`)가 빠진 것"이 여기에 해당한다(`기억/layer1/M-0348.md:74`). 그 수리 흔적도 남아 있다. `tests/test_walkthrough_contract_repairs.py:263`은 `Calls.wait`를, `:269`는 `_settle_stops`를 손으로 추가했다.
  - 둘째, 제품이 이런 대역을 받아 주려고 방어 코드를 지닌다. `__init__`이 항상 설정하는 속성을 `getattr(self, '_calls', None)` 같은 형태로 읽는 곳이 14곳이다. 실제 엔진에서는 이 기본값이 쓰일 일이 없다.
  - 셋째, `tests/test_governance_engine.py:65`의 `_live_execution_ids = set()`은 클래스 속성이므로 `Host`의 모든 인스턴스가 집합 하나를 공유한다.
  - 규모 측정: `FakeEngine`에는 `ResearchEngine`의 속성 121개가 없다. 확인 방법은 `dir(ResearchEngine)` 가운데 `hasattr(FakeEngine, n)`이 거짓인 이름을 센 것이다.

- 제안:
  1. 제품: `ResearchEngine.__init__`에서 저장소와 무관한 초기화 줄(`do_math/engine.py:597, 600-605, 607-608`)을 메서드 하나로 추출한다. 예를 들어 `_init_process_state(self, *, transport=None)`이다. `scheduler.py:552`가 만드는 `_stop_deadlines`·`_stop_clock`과 `_clock_anchor = None`도 여기서 초기값을 갖게 한다. `__init__`은 `store.load()` 뒤에 이 메서드를 부르고, `_transport`에만 실제 `ControlTransport`를 넘긴다. `_saved_state`와 `_require_current_contract`는 `__init__`에 남긴다.
  2. 테스트: `tests/research_fixtures.py`에 `bare_engine(instance=None, runtime=None, *, head='fixture-head', store=None, runner=None, formal_verifier=None)`를 하나 둔다. 이 함수는 `object.__new__(ResearchEngine)` 뒤에 `_init_process_state()`를 부르고 상태를 대입한다. 우회 29곳과 `routing_engine`은 이 함수를 부른다.
  3. `FakeEngine`을 `class FakeEngine(ResearchEngine)`로 바꾼다. `__init__`은 지금처럼 상태를 만든 뒤 `self._init_process_state()`를 부른다. 그러면 대입 차용(`tests/test_lifecycle_engine.py:31-36`, `tests/test_machine_parallel.py:24-29`)과 속성 복제(`tests/test_machine_parallel.py:34-35`, `tests/test_governance_engine.py:63-66`, `tests/test_stop_flags.py:56`)가 필요 없어진다. 믹스인을 조합한 지역 클래스는 `bare_engine()`으로 만들고, 대체할 메서드만 TST-02의 방식으로 바꾼다.
  4. 후속(엔진 영역): 방어 `getattr` 14곳을 직접 속성 접근으로 바꿀 수 있다.
  5. 세 방안의 판정:
     - 공유 가짜 하나로 합치면 복제 지점은 한 곳으로 줄지만, 그 한 곳이 여전히 제품 `__init__`을 손으로 복제한다. 다음 속성이 추가될 때 또 깨진다.
     - `spec` 강제는 Mock 대역에만 적용된다. 믹스인을 조합한 평범한 클래스와 `object.__new__` 인스턴스에는 적용할 수 없다.
     - 제품 클래스에서 파생하고 속성 초기화를 제품이 소유하게 하면, 새 메서드와 속성이 모든 엔진 대역에 자동으로 따라온다.
     - 따라서 **엔진 자체에는 파생**이 가장 단순하다. **협력자(store, 호출 관리자, 러너)에는 spec**이 가장 단순하다(TST-02). 공유 가짜로의 통합은 같은 인터페이스를 흉내 내는 대역이 이미 둘 이상 있을 때만 쓴다(TST-04).

- 동작: 보존
  - 제품 쪽 변경은 초기화 줄의 추출이므로 관찰 동작이 바뀌지 않는다.
  - 테스트 쪽에서는 `FakeEngine`이 지금 없는 `ResearchEngine` 메서드를 얻는다. 파생하면 MRO에서 믹스인 판 대신 제품 판이 잡히는 메서드는 `_validate_external` 하나다. 이 메서드는 `ResearchEngine` 자신과 `LifecycleEngineMixin`이 둘 다 정의한다. 제품 판(`do_math/engine.py:4302-4311`)은 학술 바인딩을 붙인 뒤 `super()`로 믹스인 판(`do_math/lifecycle_engine.py:824-826`)을 부른다.

- 실익:
  - 추정: 엔진 생성 경로가 45개에서 제품 생성자 1개와 `bare_engine` 1개로 준다. 삭제되는 줄은 대입 차용 12줄과 속성 복제 약 8줄이다.
  - 제품에 프로세스 속성이 추가될 때 대역을 고쳐야 하는 지점이 사실상 0개가 된다. 직전 라운드의 `wait`·`_settle_stops`·`_check_conversations` 유형 회귀가 여기서 사라진다.
  - 제품의 방어 `getattr` 14곳을 없앨 수 있게 된다.
  - 실행 시간은 줄지 않는다.

- 위험과 보호:
  - 이전에는 `AttributeError`로 막히거나 믹스인 판만 돌던 경로에서 제품 메서드가 돌게 된다. 그 결과 기존 단언이 바뀔 수 있다.
  - 믹스인 부분집합만으로 동작함을 의도적으로 보이려는 테스트가 있다면 따로 판단해야 한다. 예로 `tests/test_governance_engine.py:50-54`의 `mixin()`은 모듈의 존재를 단언한다.
  - 보호: `FakeEngine` 생성 46곳, `routing_engine` 호출 56곳, 우회 29곳의 테스트가 곧 보호 장치다. 핵심은 `tests/test_lifecycle_engine.py`의 `LifecycleTests`(39개), `Audit2LifecycleTests`(12개), `tests/test_machine_parallel.py` 전체, `tests/test_redesign_ENGINE.py` 전체다.

- 확신: 중간. 구조적 근거는 전수로 확인했다. 다만 파생 뒤 바뀌는 단언의 수는 실행 없이 알 수 없다.

- 다른 영역: `do_math/engine.py`, `do_math/scheduler.py`, `do_math/lifecycle_engine.py`, `do_math/governance_engine.py`(엔진 영역, 방어 `getattr` 14곳)

#### TST-02: 메서드 대체와 협력자 대역에 존재와 서명 검사를 강제한다

- 유형: 이음새중복

- 위치:
  - 엔진 인스턴스의 메서드를 대입으로 대체하는 곳. 검색식은 `\b(engine|e|host|h|self\.engine)\.(_\w+)\s*=\s*(Magic)?Mock\(`(123곳)와 `\b(engine|e|host|h|audit|owner)\.(_\w+)\s*=\s*lambda`(45곳)다. 대상이 많은 순서는 `_save` 23, `_check_conversations` 8, `_controls` 7, `_record_task_receipt`·`_execution_profile`·`_evaluation_context`·`_enqueue` 각 4다.
  - `engine.store`를 대체하는 곳 25곳(12개 파일). 검색식은 `\.store\s*=\s*(Mock\(|SimpleNamespace\(|object\(\))`다.
    - `tests/test_approved_five_repairs.py:30`
    - `tests/test_completion_settlement.py:103`
    - `tests/test_lifecycle_engine.py:609`
    - `tests/test_machine_parallel.py:49`
    - `tests/test_performance_repairs.py:101, 150, 173`
    - `tests/test_redesign_ENGINE.py:189, 306, 430, 1046, 1145, 1181, 1288, 1395, 1452, 1486`
    - `tests/test_redesign_GOVERNANCE.py:642, 656`
    - `tests/test_redesign_SURFACE.py:205`
    - `tests/test_repair_plan.py:92`
    - `tests/test_review_engine.py:74`
    - `tests/test_static_review_repairs.py:46, 256`
    - `tests/test_task_scope.py:29`
  - `ModelCalls`를 손으로 흉내 낸 대역: `tests/test_walkthrough_contract_repairs.py:257-263`
  - `spec`이나 `autospec`을 쓰는 파일은 3개뿐이다(`test_context_store`, `test_redesign_GOVERNANCE`, `test_repository`).

- 현상:
  - `engine._save = Mock()`처럼 인스턴스에 대입하는 방식은 제품이 메서드 이름을 바꾸거나 없애도 실패하지 않는다. 새 속성 하나가 생길 뿐이고, 제품의 실제 메서드는 대체되지 않은 채 돈다. 제품이 서명을 바꿔도 Mock은 어떤 인자든 받는다. 이것이 조용한 표류다.
  - store 대역은 방식에 따라 반대 방향으로 어긋난다. `SimpleNamespace` store는 제품이 새 속성을 읽는 순간 깨진다. 직전 라운드의 `git_dir` 회귀가 이 경우다. 그 수리는 `git_dir='fixture-git'`를 다섯 곳에 손으로 더하는 것이었다(`tests/test_approved_five_repairs.py:30`, `tests/test_performance_repairs.py:150`, `:173`, `tests/test_redesign_ENGINE.py:1181`, `:1395`, `tests/test_repair_plan.py:92`). 반대로 spec 없는 `Mock()` store는 없는 속성도 조용히 흡수한다.
  - 현재 이미 표류한 대입이 있는지 확인했다. 대입된 이름 가운데 `ResearchEngine`의 속성 집합(`dir` + `__init__`의 대입 대상)에 없는 이름은 3개다.
    - `_clock_anchor`(`tests/test_lifecycle_currentness.py:30`)와 `_stop_clock`(`tests/test_stop_flags.py:56`)은 제품 믹스인이 느슨하게 만드는 속성이다(`do_math/lifecycle_engine.py:102`, `do_math/scheduler.py:56`).
    - `_trust_fixture_directory`(`tests/test_redesign_EVIDENCE.py:133`)는 테스트 자신의 속성이다.
    - 따라서 지금 표류한 대입은 없다. 위험은 앞으로의 변경에 있다.

- 제안:
  - 메서드 대체는 `self.enterContext(patch.object(engine, '_save', autospec=True))`로 바꾼다. 반환값이나 부작용이 필요하면 `return_value`·`side_effect`를 준다. `patch.object`는 `create=False`가 기본이므로 없는 속성이면 `AttributeError`를 낸다. `autospec`은 호출 서명을 검사한다.
  - store 대역은 `create_autospec(ResearchRepository, instance=True)`로 만들고 필요한 반환만 설정한다(`store.read.side_effect = …`, `store.git_dir = 'fixture-git'`).
  - 손으로 만든 `Calls`는 실제 `ModelCalls`로 바꾼다. 다른 시험은 이미 실제를 쓴다(`tests/test_machine_parallel.py:336`, `tests/test_redesign_ACTIVITIES.py:372`). 실제 객체가 맞지 않으면 `create_autospec(ModelCalls, instance=True)`를 쓴다.
  - 새 공유 가짜는 만들지 않는다. 제품 클래스가 곧 인터페이스의 정본이 된다.

- 동작: 보존

- 실익:
  - 추정: 이름이나 서명이 바뀌어도 조용히 통과하던 대역 168곳이 즉시 실패로 바뀐다.
  - store에 속성이 추가될 때 `SimpleNamespace` 수리 지점이 사라진다.
  - 행 수는 거의 변하지 않는다. 실행 시간은 `autospec` 생성 비용만큼 조금 늘 수 있다(미측정).

- 위험과 보호:
  - 지금 잘못된 인자로 불리던 대역이 드러나 실패할 수 있다. 그것이 이 후보의 목적이다.
  - `instance=True` autospec에서 property(`git_dir`)는 명시해서 설정해야 한다.
  - 보호: 해당 테스트들 자체다. 제품 동작에는 닿지 않는다.

- 확신: 높음. 표준 라이브러리 기능이고 제품 변경이 필요 없다.

- 다른 영역: 없음. `do_math/repository.ResearchRepository`와 `do_math/parallel.ModelCalls`의 인터페이스를 참조만 한다.

#### TST-03: 제품 동작을 다시 구현한 가짜 메서드를 없앤다

- 유형: 이음새중복

- 위치:
  - `_enqueue` 재구현 8곳. 제품 판은 `do_math/engine.py:3794-3847`이다.
    - `tests/test_lifecycle_engine.py:54-57`
    - `tests/test_governance_engine.py:67-71`
    - `tests/test_redesign_GOVERNANCE.py:543`
    - `tests/test_redesign_LIFECYCLE.py:42-43`
    - `tests/test_redesign_STORAGE.py:1287`
    - `tests/test_review_engine.py:82`
    - `tests/test_revision_obligations.py:26-32`
    - 인스턴스 대입 `tests/test_walkthrough_repairs.py:216-217`
  - `_remove_action` 재구현 4곳. 제품 판은 `do_math/engine.py:2594-2597`이다.
    - `tests/test_machine_parallel.py:70-71`
    - `tests/test_redesign_ACTIVITIES.py:240-241`
    - `tests/test_redesign_GOVERNANCE.py:538-539`
    - `tests/test_revision_obligations.py:23-24`
  - `_save` 재구현 5곳. 제품 판은 `do_math/engine.py:878-912`이다.
    - `tests/test_lifecycle_engine.py:65-66`
    - `tests/test_machine_parallel.py:53-57`
    - `tests/test_repair_execution.py:20-23`
    - `tests/test_review_engine.py:79`
    - `tests/test_walkthrough_contract_repairs.py:268`
  - `_controls` 재구현 3곳. 제품 판은 `do_math/engine.py:943-947`이다.
    - `tests/test_lifecycle_engine.py:64`
    - `tests/test_machine_parallel.py:59-62`
    - `tests/test_walkthrough_contract_repairs.py:266`

- 현상:
  - **`_enqueue`**:
    - 제품 판은 다섯 가지 일을 한다. `id`와 `lineage_id`를 부여하고, 17개 키를 비교해 대기 중인 같은 행동과 병합하며, 사유·근거·개정 대상을 병합한다. 또 `_bind_revision_action`과 `_cancel_selected_revision_targets`를 부르고, `front` 인자를 처리한다.
    - `FakeEngine._enqueue`는 `row not in queue`일 때 붙이기만 한다. `id`를 붙이지 않고, `front=True`가 들어오면 `**fields`에 섞여 행의 필드가 된다.
    - 테스트 판들끼리도 서로 다르다. `id`를 붙이는 판(`tests/test_governance_engine.py:69`, `tests/test_revision_obligations.py:28`)과 붙이지 않는 판으로 갈린다.
  - **`_remove_action`**:
    - 제품 판은 `id`가 있으면 `id`로, 없으면 동등성으로 거른 새 리스트를 대입한다.
    - 테스트 판은 셋으로 갈린다. `id` 기준 제자리 치환이 2곳, 동일성(`is not`) 기준이 1곳이다.
  - **`_save`**:
    - 제품 판은 여섯 가지 일을 한다. 게시 전에 `active_executions`를 파생하고 `pending_withdrawal`을 종결한다. 무변경이면 생략하고, 변경이 있으면 store에 게시한다. 게시 뒤에는 slots 상태를 동기화하고 `_evaluate_stops()`를 부른다.
    - `FakeEngine._save`는 사본만 기록한다.
    - `tests/test_machine_parallel.py:57`은 그 위에 `_evaluate_stops()`만 다시 적었다(주석 "The real publication point judges stops after every save").
    - `RepositoryHost._save`는 게시와 재적재만 다시 적었다.
  - 결과적으로 믹스인이 대기열과 게시 의미에 기대는 경로를, 테스트는 제품과 다른 의미로 검증한다. 이 차이는 테스트를 통과시킨 채 남는다.

- 제안:
  - TST-01을 적용한 뒤 `FakeEngine`과 지역 호스트에서 `_enqueue`·`_remove_action` 재정의를 지우고 제품 판을 쓴다.
  - `_save`는 재정의하지 않는다. 대신 store 대역(TST-02의 `create_autospec(ResearchRepository, instance=True)`)에 게시를 맡긴다. `save_with_state.side_effect`가 사본을 기록하고 `(새 head, instance, runtime)`을 돌려주게 한다. `saves`를 읽던 단언은 그 기록을 읽는다.
  - `_controls` 재정의는 제품 판의 동작을 확인한 뒤 지운다. 제품 판은 `_calls`와 `_transport`가 없고 inbox 폴더가 비어 있으면 아무것도 하지 않는다(`do_math/engine.py:924-947`).

- 동작: 보존. 제품 동작은 그대로이고, 테스트가 검증하는 의미가 제품 쪽으로 정렬된다.

- 실익: 추정으로 재구현 20곳, 약 40행을 삭제한다. 대기열과 게시 규칙이 두 번 정의되는 상태가 사라진다.

- 위험과 보호:
  - 제품 `_enqueue`는 `id`를 붙이고 병합하므로, 대기열 행을 사전 동등성으로 단언하는 테스트가 바뀐다.
  - 제품 `_save`는 무변경이면 게시를 생략하므로, `len(saves)`를 세는 단언이 바뀔 수 있다.
  - 보호: `FakeEngine` 생성 46곳의 테스트와 `tests/test_revision_obligations.py`, `tests/test_machine_parallel.py` 전체다.

- 확신: 중간. 재구현이 제품과 다르다는 사실은 원문으로 확인했다. 다만 제거 뒤 고쳐야 할 단언의 수는 실행 없이 알 수 없다.

- 다른 영역: 없음.

#### TST-04: 어댑터 대역 두 벌을 하나로 합친다

- 유형: 이음새중복

- 위치:
  - 제품 인터페이스: `do_math/codex_adapter.py:124-175`(`LocalCLIAdapter`의 `capability_identity`, `observation_key`, `describe`)
  - 제품 소비자: `do_math/initialization.py:27-35, 46, 79-82`, `do_math/lifecycle_engine.py:235-236`, `do_math/execution_profiles.py:356-381`
  - 첫 번째 대역: `tests/research_fixtures.py:301-323`(`FixtureAdapter`, `install_adapter_fixture`)
  - 두 번째 대역: `tests/test_lifecycle_engine.py:22-28`(`IDENTITY`, `AdapterDouble`)
  - 지역 변형: `tests/test_initialization_probe_batch.py:49, 70, 82`
  - `adapter_for` patch 38곳. 그중 `return_value=AdapterDouble()`이 23곳이다.

- 현상:
  - 같은 제품 인터페이스를 흉내 내는 공유 대역이 두 벌 있고, 지역 변형도 셋 있다. 두 공유 대역은 세 가지가 다르다. 신원 사전(`IDENTITY`)이 다르고, `describe()['scope']` 문자열이 다르다. 또 `FixtureAdapter`만 `version_sha256`·`exec_help_sha256`·`unknown`을 낸다.
  - `capability_evidence`는 `scope`, `supported`, `unknown`, `verified`, `version_sha256`, `exec_help_sha256`를 읽는다(`do_math/execution_profiles.py:363-379`). 따라서 제품이 `describe()`에서 새 필드를 읽기 시작하면 대역 다섯 곳을 모두 고쳐야 한다.
  - `state_fixtures.py:22`는 공유 픽스처이면서 테스트 모듈에서 `AdapterDouble`을 가져온다.

- 제안:
  - `FixtureAdapter`를 정본 하나로 둔다. `AdapterDouble`의 신원 사전과 기본 능력 집합을 생성자 인자의 기본값으로 흡수한다.
  - `AdapterDouble`은 삭제한다. 23곳의 `patch(…, return_value=AdapterDouble())`는 `install_adapter_fixture(self)`로 바꾸거나, 같은 patch에 `FixtureAdapter(...)`를 넣는다.
  - `tests/test_lifecycle_engine.py:950, 955`는 공유 `IDENTITY`를 참조한다.
  - `tests/test_initialization_probe_batch.py`의 세 변형은 `FixtureAdapter`의 하위 클래스로 `describe`만 다르게 둔다.

- 동작: 보존

- 실익: 추정으로 대역 클래스가 5개에서 1개로 준다. 제품이 어댑터 계약을 바꿀 때 고칠 곳이 5곳에서 1곳으로 준다. `state_fixtures`가 테스트 모듈을 import하는 역방향 의존도 줄어든다(TST-07과 연결).

- 위험과 보호:
  - `scope`와 `version_sha256`이 바뀌면 능력 증거 기록의 ID가 바뀐다. 이 ID는 `exact_content_hash`로 만들어진다(`do_math/execution_profiles.py:380`). 증거 ID를 직접 단언하는 곳은 grep에서 찾지 못했다. 검색식은 `IDENTITY|synthetic_test_evidence_not_host_verification|adapter_sha256`다.
  - 보호: `tests/test_lifecycle_engine.py` 전체와 `tests/test_initialization_probe_batch.py`다.

- 확신: 높음

- 다른 영역: 없음

#### TST-05: 계약 검토 출력의 조립을 한 도우미로 모으고 항목 목록의 리터럴을 없앤다

- 유형: 이음새중복

- 위치:
  - 정본 상수: `do_math/contracts.py:146`(`CONTRACT_REVIEW_ITEMS`)
  - 공유 도우미: `tests/research_fixtures.py:77-84`(`contract_review`)
  - 조립 복제 7곳:
    - `tests/test_contracts.py:68-69`
    - `tests/test_redesign_CONTRACTS.py:610-612`
    - `tests/test_redesign_EVIDENCE.py:104-105`
    - `tests/test_redesign_GOVERNANCE.py:582-584`
    - `tests/test_redesign_TASKS.py:255-256`
    - `tests/test_redesign_TASKS.py:364-365`
    - `tests/test_lifecycle_engine.py:170-174`(`FakeEngine.approve`)
  - 같은 조립에 항목 튜플까지 리터럴로 다시 적은 곳: `tests/test_redesign_TASKS.py:36-40`(`approve`, 다른 파일이 8회 import)

- 현상:
  - "모든 계약 항목을 승인한 `item_reviews`"를 만드는 코드가 공유 도우미 1곳 외에 7곳 더 있다. 그중 2곳(`tests/test_redesign_TASKS.py:37`, `tests/test_lifecycle_engine.py:173`)은 제품 상수 `CONTRACT_REVIEW_ITEMS`의 다섯 항목을 문자열 튜플로 다시 적었다.
  - 같은 `tests/test_redesign_TASKS.py`의 251행과 341행은 제품 상수를 import해 쓰므로, 한 파일 안에서도 두 방식이 섞여 있다.
  - 제품이 항목을 추가하거나 이름을 바꾸면 리터럴 두 곳이 불완전한 검토를 만든다. 나머지 복제는 제품 상수를 쓰지만, 레코드 필드(`findings`, `missing_inputs`, `next_owner`)가 바뀌면 7곳을 따로 고쳐야 한다.

- 제안:
  - `tests/research_fixtures.py`에 `review_items(evidence_refs, *, decision='approved', next_owner='research_plan', findings=())`를 둔다. 이 함수는 `CONTRACT_REVIEW_ITEMS`를 순회해 `{'item_reviews': [...]}`를 돌려준다.
  - `contract_review(context, …)`는 이 함수를 부른다.
  - 7곳과 `approve`는 이 함수를 부른다. 증거 참조가 일부러 다른 곳(`tests/test_redesign_CONTRACTS.py:611`의 `"MISSING"`)은 인자로 넘긴다.

- 동작: 보존

- 실익: 추정으로 조립 8곳, 약 20행이 호출 8줄로 바뀐다. 제품 상수 리터럴 2곳이 제거된다.

- 위험과 보호: `next_owner` 값이 곳마다 다르다(`research_preparation`, `research_plan`, `research`). 인자 기본값을 잘못 고르면 단언이 바뀐다. 보호: 해당 7개 파일의 테스트다.

- 확신: 높음

- 다른 영역: 없음

#### TST-06: 다른 모듈의 TestCase를 픽스처 보관소로 쓰는 의존을 모듈 수준 함수로 바꾼다

- 유형: 복잡성

- 위치:
  - 교차 모듈 사용 79곳(31개 파일). TestCase 인스턴스를 만들어 픽스처 메서드를 부르거나 `X.setUp(self)`로 setUp을 빌리는 경우다. 대상 클래스를 많이 가진 모듈은 다음과 같다(괄호는 사용 수).
    - `test_redesign_TASKS`(14): `AssessmentApplicationTests().apply`, `.fixture`
    - `test_input_recovery`(9): `InputRecoveryPublicTests`
    - `test_redesign_KNOWLEDGE`(7): `KnowledgeRedesign().verified`
    - `test_redesign_GOVERNANCE`(6): `DomainGovernanceTests().initial`, `AuditRepairTests().checked_import`
    - `test_lifecycle_engine`(6)
    - `test_governance_engine`(5): `CentralGovernanceTests().host`
    - `test_review_cycle`(5): `ReviewCycleTests().output`
  - 대표 위치:
    - `tests/test_redesign_TASKS.py:25`(`approved_fixture`가 `DomainGovernanceTests().initial()`을 부른다)
    - `tests/test_governance_engine.py:57-60`
    - `tests/test_redesign_ENGINE.py:1116-1117`
    - `tests/test_connection_repairs.py:434-435`

- 현상:
  - 픽스처를 만드는 논리가 다른 모듈의 테스트 클래스 메서드에 들어 있다. 그래서 테스트 클래스 하나를 고치면 31개 파일의 픽스처가 조용히 바뀐다. 사용하는 쪽은 TestCase를 기본 `methodName='runTest'`로 만들고, `setUp`·`doCleanups`를 수명 규칙에 맞춰 손으로 부른다.
  - 공유 픽스처 모듈도 이 방식에 기댄다. `approved_fixture`(11회 import)는 `DomainGovernanceTests().initial()`을 거친다.
  - 정리 누락은 확인하지 못했다. 읽은 사용처 여섯 곳은 모두 `addCleanup(fixture.doCleanups)`나 `tearDown`을 등록했거나(`tests/test_relation_dependencies.py:16-17`, `tests/test_initialization_efficiency.py:168-170`, `tests/test_six_connections.py:423-425`, `tests/test_control_shapes.py:37-38`), 정리할 자원이 없는 `setUp`을 빌렸다(`tests/test_redesign_CONTRACTS.py:209-`).

- 제안:
  - 다른 모듈이 부르는 픽스처 메서드(`initial`, `checked_import`, `audited`, `fixture`, `apply`, `verified`, `output`, `host` 등)를 같은 모듈의 모듈 수준 함수로 옮긴다. 각 테스트 클래스는 그 함수를 부른다. 이렇게 하면 import 그래프는 그대로라서 `run_tests.py`의 모듈 키 범위가 바뀌지 않는다.
  - `setUp`을 빌리는 사용처(`InputRecoveryPublicTests.setUp(self)` 등 9곳)에는 컨텍스트 관리자 함수 하나(예: `recovery_instance()`)를 제공한다.

- 동작: 보존

- 실익: 추정. 행 수는 거의 변하지 않는다. 픽스처의 소유 위치가 명시되고, TestCase를 수동으로 생성하는 곳 79개가 사라진다.

- 위험과 보호: 픽스처 메서드가 `self.assert*`를 쓰면 함수로 옮길 때 예외 형태가 바뀐다. 보호: 해당 31개 파일의 테스트다.

- 확신: 중간. 결합 관계는 전수로 확인했다. 다만 픽스처 메서드마다 `self`에 기대는 정도는 표본만 읽었다.

- 다른 영역: 없음

#### TST-07: 결과 캐시의 모듈 키가 픽스처 모듈을 거친 테스트 모듈 의존을 따라가게 한다

- 유형: 기타(문제 발생 여지: 캐시 무효화 누락의 잠재 경로)

- 위치:
  - `run_tests.py:44`(`TEST_IMPORT`가 `test_\w+`만 추적)
  - `run_tests.py:47-48`(`_is_test_module`이 `test_*.py`만 테스트 모듈로 인정)
  - `run_tests.py:51-64`(`_module_keys`)
  - `run_tests.py:67-80`(`_input_key`: 그 밖의 `tests/*.py`를 공유 키에 넣음)
  - `tests/state_fixtures.py:22`(`from test_lifecycle_engine import AdapterDouble, FakeEngine`)

- 현상:
  - 시험 모듈의 캐시 키는 자기 파일과 전이적으로 import한 `test_*` 모듈의 바이트로 만든다. `state_fixtures`·`research_fixtures`는 공유 키(제품·문서와 같은 층)에 들어간다.
  - 그런데 `state_fixtures`는 테스트 모듈 `test_lifecycle_engine`을 import한다. 어떤 시험 모듈이 `state_fixtures`만 import하고 `test_lifecycle_engine`은 import하지 않는다고 하자. 그러면 `FakeEngine`을 고쳐도 그 모듈의 공유 키와 모듈 키가 모두 그대로여서, 이전 통과가 캐시에서 보고된다.
  - 현재는 이 경로가 실현되지 않았다. `state_fixtures`를 import하는 7개 모듈을 확인한 결과, 모두 `test_lifecycle_engine`이 폐포에 들어 있었다. 폐포에 들게 한 import는 다음과 같다.
    - `tests/test_purpose_engine.py:448`의 함수 안 import
    - `test_academic_engine`, `test_efficiency`, `test_engine`, `test_session_scheduler`, `test_stop_flags`, `test_submission_boundaries`는 각자의 import 경로로 폐포에 닿는다.
  - 즉 지금의 정확성은 우연에 기대고 있다.

- 제안:
  - `_module_keys`의 원천을 `tests/*.py` 전체로 넓힌다. `TEST_IMPORT`를 "`tests/`에 있는 모듈 이름" 전체로 매칭하게 하고, `_input_key`에서는 `tests/*.py`를 뺀다.
  - 그러면 `research_fixtures` 수정은 그것을 import하는 모듈만 무효화한다. `state_fixtures` → `test_lifecycle_engine` 의존도 추적된다.
  - `run_tests.py:6-12`의 설명문 "shared fixtures"를 함께 고친다.
  - TST-04가 `state_fixtures`의 역방향 import를 없애면 잠재 경로 하나는 저절로 사라진다. 그러나 이 규칙을 고쳐야 같은 유형의 재발을 막는다.

- 동작: 변경. 운영자(시험 실행자)가 관찰하는 캐시 적중 범위가 달라진다.
  - `research_fixtures`만 고친 경우: 지금은 캐시 전체가 무효가 된다. 바뀐 뒤에는 그것을 import하는 모듈만 무효가 된다. 121개 import 줄이 가리키므로 실제 차이는 작다.
  - `state_fixtures`를 거친 테스트 모듈 의존: 지금은 추적되지 않는다. 바뀐 뒤에는 추적된다.

- 실익: 캐시가 틀린 통과를 보고할 수 있는 경로 하나가 막힌다. 시간 차이는 작다(추정).

- 위험과 보호: 매칭 규칙이 넓어지면 `tests/` 밖 이름과의 충돌 가능성이 생긴다. 소스 키 집합과 교집합을 취하는 현 구조(`run_tests.py:54`)가 이를 막는다. 보호: `tests/test_test_runner.py`(195행)다. 이 파일의 캐시 관련 시험은 이번 조사에서 읽지 않았다.

- 확신: 높음. 규칙과 의존 경로를 원문과 읽기 전용 계산으로 확인했다.

- 다른 영역: 없음

#### TST-08: 공개 활성화를 시작 조건으로만 쓰는 시험을 검증된 활성 상태에서 시작하게 한다

- 유형: 운영비용

- 위치:
  - 공개 활성화 경로: `tests/test_purpose_engine.py:418-429`(`PurposeHarness.make`) → `tests/research_fixtures.py:438-497`(`activate` → `engine.run(until_active=True)`)
  - 이미 있는 대안: `tests/test_purpose_engine.py:443-455`(`ActiveStateHarness`) → `tests/state_fixtures.py:21-34`
  - `make`를 직접 부르는 시험 22개. 검색 방법은 `PurposeHarness`에서 직접 파생한 클래스 안의 `self.make(` 호출이다.
    - `test_academic_engine`: 4개
    - `test_lifecycle_currentness`: 2개
    - `test_model_assessment_flow`: 1개
    - `test_purpose_engine`: 12개(`GitPurposeTests` 1개 포함)
    - `test_question_flow`: 1개
    - `test_run_feedback`: 1개
    - `test_submission_tools`: 1개
  - 도우미를 거쳐 `make`를 부르는 곳: `tests/test_review_research.py:82-88`의 `make_research`(8회 호출), `tests/test_run_feedback.py:19-20`의 `prepare`(3회 호출)

- 현상:
  - 직전 라운드는 공개 활성화 픽스처의 비용을 약 95초로 기록했다. 활성화와 무관한 시험 16개에서 이 비용이 14회 반복되는 것을 찾아 검증된 활성 상태로 옮겼고, 대상 22개의 합이 2238초에서 1473초로 줄었다(`기억/layer1/M-0348.md:50`). 이 측정은 에이전트 4개가 동시에 시험을 돌리던 부하 조건의 값이다(같은 문서 40행).
  - 옮기지 않은 시험도 남아 있다. 위 목록의 시험은 여전히 시험마다 공개 활성화를 거친다. 이 활성화에는 초기화 해석 호출이 들어 있고, 호출마다 실제 Job을 기동한다(`tests/research_fixtures.py:216-246`, `tests/test_engine.py:63`).
  - 같은 라운드에서 `ParallelEngineTests` 네 개는 옮기자 판정이 바뀌어 되돌렸다(`기억/layer1/M-0348.md:50`). 따라서 옮길 수 있는지는 시험마다 판단해야 한다.
  - 공개 경로의 연결 검증은 전용 시험 3개가 맡는다(같은 줄).

- 제안:
  - 위 목록 가운데 시험 대상이 활성화 뒤에 시작되는 것은 `ActiveStateHarness`로 옮긴다. 후보로 보이는 것은 currentness, 학술 요구, 질문 흐름, 대기열 중복, 도구 검토다.
  - 대상이 초기 공개 제어의 효과에 기대는 것은 남긴다. 예를 들어 `tests/test_run_feedback.py:21-23`의 주석은 초기 공개 제어가 만든 재고 사건을 계획이 소비해야 한다고 적는다. `tests/test_purpose_engine.py`의 전 흐름 시험도 남긴다.
  - 판정 기준은 직전 라운드와 같다. 옮긴 뒤 판정이 바뀌면 되돌린다.

- 동작: 보존

- 실익: 추정. 옮긴 시험마다 공개 활성화 1회를 아낀다. 직전 라운드의 평균 절감은 시험당 약 35초였다((2238−1473)/22, 부하 조건). 이번 목록에서 옮길 수 있는 수는 미확인이다. 실행 없이 판정할 수 없기 때문이다.

- 위험과 보호: 공개 경로와 검증된 시작 상태의 차이가 시험 판정을 바꿀 수 있다(직전 라운드의 선례). 보호: 공개 활성화 전용 시험 3개와 각 시험 자신이다.

- 확신: 낮음. 비용 근거는 직전 라운드의 측정이고, 옮길 수 있는지는 시험마다 판단해야 한다.

- 다른 영역: 없음

#### TST-09: 신뢰 픽스처의 파일 해시를 제품의 정본 함수로 계산한다

- 유형: 이음새중복

- 위치:
  - 복제: `tests/research_fixtures.py:370`(`digest = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()`)
  - 사용처: `tests/research_fixtures.py:373-376`
  - 정본: `do_math/file_io.py`의 `sha256_file`(`docs/do-math/검사-경량화-이음새-계약.md` 2절)

- 현상: 픽스처가 만드는 툴체인 기록의 `sha256`, `verifier_sha256`, `executables` 값은, 제품이 게시 관문에서 파일 전 바이트의 SHA-256으로 다시 계산해 대조하는 값이다. 픽스처는 이 규칙을 지역 람다로 한 번 더 구현한다. 이음새 계약 2절은 파일 해시 도우미를 모듈 안에 새로 만들지 말라고 정한다.

- 제안: 람다를 지우고 `from do_math.file_io import sha256_file`로 바꾼다.

- 동작: 보존. 두 방식 모두 전 바이트 SHA-256이므로 값이 같다.

- 실익: 1행 삭제. 해시 규칙의 정의가 하나로 준다.

- 위험과 보호: 없음에 가깝다. 보호: `trust_fixture`를 쓰는 시험 전부다(`trust_fixture` import 17회).

- 확신: 높음

- 다른 영역: 없음

#### TST-10: 저장소와 인스턴스를 만드는 세 줄 도우미를 공유 픽스처로 모은다

- 유형: 복잡성

- 위치:
  - 저장소 생성(`git init`)과 `initialize(...)`를 함께 하는 비시험 도우미 10곳. 검색 방법은 함수 본문에 `'git' … 'init'`과 `initialize(`가 함께 있는지를 파이썬 정규식으로 찾은 것이다.
    - `tests/test_boundary_repairs.py` setUp
    - `tests/test_controls.py` setUp
    - `tests/test_engine.py` `formal_fail`
    - `tests/test_governance_engine.py` `initialized`
    - `tests/test_knowledge_import_engine.py` setUp
    - `tests/test_preflight.py` setUp
    - `tests/test_redesign_ACTIVITIES.py` setUp
    - `tests/test_repair_execution.py` setUp
    - `tests/test_review_engine.py` `_staged_activation_git_round_trip`
    - `tests/test_session_scheduler.py` setUp
  - 시험 메서드 안에서 같은 일을 하는 곳 38곳(19개 파일). 예: `tests/test_lifecycle_engine.py:204-209`, `tests/test_static_review_repairs.py:178-180`
  - `PurposeHarness.setUp`: `tests/test_purpose_engine.py:393`
  - 전체적으로는 `git init` 호출이 78줄, `initialize(` 호출이 122곳(39개 파일)이다.

- 현상: "임시 폴더에 Git 저장소를 만들고 인스턴스를 초기화한 뒤 엔진을 연다"는 세 줄이 약 50곳에 복제돼 있다. `initialize`의 호출 형태가 바뀌면 이 복제 전부를 고쳐야 한다.

- 제안: `tests/research_fixtures.py`에 `new_instance(root, *, goal, workspace=None, config=None, **kwargs) -> (repo, instance_id)`를 하나 둔다. 엔진이 필요한 곳은 `ResearchEngine(repo, instance_id, …)`만 덧붙인다.

- 동작: 보존

- 실익:
  - 추정으로 약 50곳에서 2~3행씩, 100행 안팎이 준다. `initialize`의 호출 이음새가 한 곳으로 모인다.
  - 실행 시간은 줄지 않는다. 템플릿 저장소를 복사하는 방식으로 비용을 줄이는 방안도 있다. 그러나 `git init`과 `initialize`의 비용을 측정하지 않았으므로 여기서는 제안하지 않는다.

- 위험과 보호: 호출 인자(`config`, `instance_id`)가 곳마다 달라 기본값을 잘못 고르면 시험 전제가 바뀐다. 보호: 해당 시험들이다.

- 확신: 중간. 복제는 전수로 확인했다. 다만 50곳의 인자 차이는 표본만 읽었다.

- 다른 영역: 없음

## 3. 보존 판정

1. **스크립트 모델 호출마다 실제 Job을 띄우는 `local_job_runner`** (`tests/research_fixtures.py:216-246`, 적용 31곳)
   - 겉보기 문제: 스크립트 역할 호출 하나마다 Python 프로세스를 담은 WindowsJob을 기동하고, 종료하고, 대기한다. Python 프로세스의 기동과 종료만 해도 0.039~0.082초가 걸렸다(5회 측정).
   - 유지 이유: 엔진은 시작 보고의 프로세스 신원을 실제로 검사한다. `do_math/launch.py:28-31`은 소유자 신원의 형식을 요구하고, `do_math/model_runner.py:363-367`은 게시된 프로세스와 수집된 신원의 일치를 요구한다. 가짜 신원으로 바꾸려면 제품이 합성 신원을 받아들여야 하므로 검증 경계가 약해진다. 시험당 비용 합계는 측정하지 않았다.

2. **문서 속 예시를 제품 코드에 실행하는 시험**
   - 위치:
     - `tests/test_walkthrough_repairs.py:235-244`(`references/과제-착수조건.md`의 JSON 블록을 `planning.validate_condition`에 통과시킨다)
     - `tests/test_walkthrough_repairs.py:314-322`(`references/초기화-운전.md`의 권한 예시)
     - `tests/test_static_review_repairs.py:183-`(같은 문서의 PowerShell 조회 줄을 실행한다)
   - 겉보기 문제: 테스트가 문서 문장을 리터럴로 찾는다.
   - 유지 이유: 문장을 다시 적어 단언하는 것이 아니다. 문서의 예시가 곧 정본이고, 시험은 그 예시가 현재 제품 문법을 통과하는지 실행으로 확인한다. 문서와 코드를 잇는 유일한 실행 검사다. `test_documented_research_grant_permits_formal_check`는 기존 실패 기준선에 들어 있다(`기억/layer1/M-0348.md:84`). 그 원인은 문서 쪽 자리표시자이므로 이 판정과는 무관하다.

3. **관측 창 설정값의 반복** (`tool_review_window_seconds`와 `self_check_response_window_seconds`의 리터럴이 20개 파일에 있다)
   - 겉보기 문제: 같은 설정을 여러 파일이 적는다.
   - 유지 이유: 제품은 이 두 값에 기본값을 두지 않는다(`do_math/engine.py:133`의 `OPTIONAL_CONFIG`, `tests/research_fixtures.py:445-446`의 주석 "Production deliberately has no implicit defaults"). 시험마다 창 길이를 시나리오 조건으로 고른다. 공유 픽스처 세 곳(`tests/research_fixtures.py:448`, `tests/test_lifecycle_engine.py:44-45`, `tests/test_purpose_engine.py:414`)은 모두 60/5라서 상수 하나로 묶을 수 있다. 그러나 실익이 3행 수준이라 후보로 올리지 않는다.

4. **프로세스 경계를 흉내 내는 손 대역**
   - 위치: `tests/test_model_runner.py:7-22`(`Job`, `Execution`, `Adapter`; 10회 import), `tests/test_codex_adapter.py:19-21`(`_FakeJob`), `tests/test_test_runner.py:79, 126, 144`(`Job`)
   - 겉보기 문제: 제품 인터페이스(`LocalCLIAdapter`, `WindowsJob`)를 손으로 복제한다.
   - 유지 이유: 이 대역들은 메서드가 빠지면 `AttributeError`로 크게 실패하므로 조용히 어긋나지 않는다. 제품 클래스에서 파생하면 빠진 메서드 자리에 실제 CLI나 프로세스 호출이 끼어들 위험이 생긴다. spec을 걸면 서명 검사를 얻지만, 반환값을 모두 새로 설정해야 해서 지금보다 단순하지 않다.

5. **`test_categories.UNIT_MODULES`의 손 목록** (`test_categories.py:6-15`)
   - 겉보기 문제: 모듈 이름을 파일과 따로 적는다.
   - 유지 이유: 목록이 어긋나면 해당 모듈이 `integration`으로 분류된다(`test_categories.py:34`). 즉 어긋남이 보수적인 쪽으로만 작용한다. 목록 28개가 모두 실재함도 확인했다. 확인 명령은 `python -c "from test_categories import UNIT_MODULES; …"`이고 결과는 누락 없음이다.

6. **`run_tests.py`의 해시 두 벌** (`_edition` 305-307, `_input_key` 67-80)
   - 겉보기 문제: 원천 파일을 두 가지 범위로 두 번씩(시작과 끝) 해시한다.
   - 유지 이유: 목적이 다르다. `_edition`은 실행 중에 시험 코드가 바뀌었는지 판정하고 보고서의 `source_sha256`을 만든다. `_input_key`는 캐시 키다. 측정 결과 `_edition`은 0.066초, `_input_key`는 0.919초였다. 둘을 합쳐 줄일 수 있는 시간은 `_edition` 몫인 0.1초 안팎이라 실익이 없다.

7. **`PurposeHarness`와 `ActiveStateHarness`의 모듈 수준 import** (11개 모듈)
   - 겉보기 문제: `unittest` 발견기는 모듈 네임스페이스의 TestCase 서브클래스를 모두 수집하므로 중복 실행이 걱정된다.
   - 유지 이유: 두 클래스에는 `test_` 메서드가 없다(`tests/test_purpose_engine.py:385-455`). 따라서 중복 실행이 없다. `test_` 메서드를 가진 TestCase 클래스를 모듈 수준에서 import하는 곳은 없었다. 검색식은 `^(from|import) test_\w+ import .*Tests`이고, 나머지 import는 모두 함수 안에 있다.

## 4. 후보 없음

- `tests/research_fixtures.py`: TST-04·TST-05·TST-09 외에는 후보가 없다. `activate`는 공개 제어만으로 활성화를 채운다. `trust_fixture`·`validation_fixture`는 이음새 계약 6절이 지정한 신뢰 픽스처의 정본이다.
- `tests/state_fixtures.py`: 역방향 import(TST-04, TST-07) 외에는 후보가 없다.
- `test_categories.py`: 후보가 없다(3절 5항).
- `run_tests.py`: TST-07 외에는 후보가 없다. 격리 워커, 단계별 시한, 실패 증거의 즉시 게시, 캐시 불변식(실패는 저장하지 않음, 실행 중 입력이 바뀌면 저장하지 않음)은 모두 한 번씩만 정의돼 있다.
- 시계 대역(`tests/test_redesign_OBSERVATION.py:16-18`, `tests/test_redesign_EVIDENCE_walkthroughs.py:83-85`, `tests/test_machine_parallel.py:382-384`, `tests/test_stop_flags.py:181-183`): 2~3줄이고, 호출형 단조 시계와 `datetime.now` 대체라는 서로 다른 개념이라 합칠 대상이 아니다.
- 고정 sleep: 테스트 쪽의 긴 sleep은 모두 자식 프로세스 안에서 수명을 만드는 용도다(`time.sleep(30)`, `time.sleep(600)` 등). 종료나 정지로 끊기므로 벽시계를 그만큼 쓰지 않는다. 테스트 스레드에서 실제로 기다리는 곳은 `time.sleep(1.05)` 두 곳뿐이다(`tests/test_purpose_engine.py:108`, `tests/test_submission_tools.py:235`). 이 두 곳은 실제 관측 창 1초가 지나야 하는 시나리오이며, 합계 약 2초라 후보로 올리지 않는다.

## 5. 미완료

없음. 파견문의 발견 절차 세 가지를 모두 전수로 수행했다. 다만 다음 두 가지는 조사 범위 안에서 실행 없이 확정할 수 없었으므로 해당 후보의 확신과 실익에 반영했다.

- TST-01·TST-03의 변경 뒤에 고쳐야 할 단언의 수
- TST-08의 시험별 이전 가능 여부와 절감 시간

## 6. 작업 중 사건

- **판정을 철회한 곳**: 처음에는 `tests/test_redesign_ENGINE.py:1117`과 `tests/test_redesign_STORAGE.py:422-423`이 빌린 `ImpactReviewTests.setUp()`의 정리 작업을 부르지 않아 임시 폴더와 patch가 샐 수 있다고 보았다. `grep -A12`의 출력 줄이 바로 앞 클래스 `AuditRepairTests`(`tests/test_redesign_CONTRACTS.py:36-`)의 것이었고, `ImpactReviewTests.setUp`(209행 이하)에는 정리 작업 등록이 없다. 따라서 누수 주장은 철회했고 TST-06에도 넣지 않았다.
- **셈이 두 번 달랐던 곳**: 우회 생성의 수가 첫 검색에서 29, 두 번째 검색에서 25로 달랐다. 차이는 `tests/test_performance_repairs.py`의 `engine_module.ResearchEngine.__new__(…)` 4곳이었다. 최종 수는 29다. 같은 파일에는 `ResearchRepository.__new__`(229행)와 `GitStateStore.__new__`(367행)도 있으나 엔진 대역이 아니므로 세지 않았다.
- **비어 있는 폴더**: `tests/fixtures/`는 파일이 없는 폴더다. Git이 추적하지 않고(`git ls-files` 결과 없음), 참조하는 곳도 없다. `scripts/probe_native_isolation.py:206`의 `root / "fixtures"`는 자기 루트 아래의 별개 경로다. 저장소 계약 밖의 로컬 잔재이므로 후보로 올리지 않았다.
- **기억 기록과 파견문의 차이**: 직전 라운드 회귀의 원인 가운데 기억 노드에는 `_check_conversations`가 적혀 있고, 파견문에는 `_settle_stops`가 적혀 있다. 원문을 확인하니 `tests/test_walkthrough_contract_repairs.py:269`에 `_settle_stops`, `:263`에 `wait`가 손으로 추가돼 있다. 따라서 둘 다 같은 유형이다.

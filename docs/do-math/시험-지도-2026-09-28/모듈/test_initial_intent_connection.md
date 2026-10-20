# test_initial_intent_connection

| 항목 | 값 |
|---|---|
| 조각 | `lifecycle` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_initial_intent_connection.py` (165행) |
| 클래스 / 테스트 | 2 / 6 |
| 시험 대상 제품 코드 | `do_math/initialization.py`의 `initial_intent_evidence`, `adapter_for`; `do_math/governance.py`의 `apply_decision`, `authorize`; `do_math/engine.py`의 `initialize`(`research_fixtures.new_instance` 경유), `control`, `ResearchEngine`(`run`, `process_controls`, `_retry_input_overflow_action`); `do_math/repository.py`의 `ResearchRepository`(`initialize`, `load`, `read`), `new_id`, `exact_content_hash`; `do_math/model_policy.py`의 `selection`; `do_math/execution_profiles.py`의 `capability_evidence` |
| 사용하는 픽스처 모듈 | `research_fixtures`(`git_init`, `new_instance`, `charter_record`, `install_adapter_fixture`); `record_fixtures`(`applied_initial_intent`); `engine_fixtures`(`FakeEngine`, `PublicInitializationRunner`) |
| 격리 표지 | 없음 |
| 시작 상태 | `test_public_initialization_stores_exact_text_and_source_filename`은 4단(공개 `initialize`). 나머지 `InitialIntentConnectionTests`는 1단(`applied_initial_intent`가 만든 메모리 상태에 순수 함수 호출). `InitialFailureRetryTests`는 `FakeEngine`으로 조립한 채택 직전 상태를 실제 Git 저장소에 직접 게시하고, 그 위에서 공개 제어와 엔진 실행을 돈다 |

## 목적

모듈 docstring은 없다. 시험 이름과 단언으로 보면 이 모듈은 사용자의 원 입력이 초기화에서 활성화까지 어떻게 이어지는지를 검사한다. 대상은 다섯 가지다.

- 원 입력의 정확한 텍스트와 원자료 파일 이름이 공개 초기화에서 그대로 보존된다.
- 초기 의도 증거(`initial_intent_evidence`)는 봉인되고 독립 검사되어 실제로 적용된 해석에서만 나온다. 제품 docstring은 이 함수를 "봉인되고 독립 검사되고 실제 적용된 원문을 해석한다(Resolve the sealed, independently checked and actually applied original)"고 설명한다(`initialization.py` 행 103–104).
- 초기화 중 준 권한이 연구를 열지 않는다.
- 활성 뒤 권한 변경이 계획의 근거는 되지만 그 계획의 실행 권한은 되지 않는다.
- 실패한 초기 해석을 공개 제어로 재시도할 때 원 입력과 끝난 앞 시도가 보존된다.

## 모듈 수준 요소

- 행 7: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 넣는다.
- 행 8–11: 모듈 import `governance as gov`, `initial_intent_evidence`, `git_init`, `applied_initial_intent`.
- 행 165: 직접 실행하면 `unittest.main()`.

`record_fixtures.applied_initial_intent(text)`가 이 모듈 1단 시험의 공통 시작 상태를 만든다. 그 과정은 다음과 같다.

1. `initialize_state`로 인스턴스 `RI-case`를 만들고, 헌장 하나를 통치 원문 `GS-adoption`(원문 `text`)과 승인 `DC-adopt`로 채택한다.
2. 원 입력을 `import_input_source`로 원천 기록으로 바꾼다.
3. 원문 전체 범위를 헌장에 귀속하는 해석 단위 `IU-goal` 하나를 작성자 `EX-author`의 `prepare_import`로 묶는다.
4. 검사자 `EX-check`가 승인한 뒤 `apply_import`로 적용한다.
5. `(instance, runtime, bundle_id)`를 돌려준다. 적용 수신증이 `applied`가 아니거나 원천 ID가 입력 ID와 같으면 `AssertionError`를 던진다.

## InitialIntentConnectionTests (행 14–69)

`unittest.TestCase`를 상속한다. 설정 훅과 도우미가 없다.

### `test_public_initialization_stores_exact_text_and_source_filename` (행 15–31)
- 성질: 공개 초기화는 결합 문자와 켈빈 기호를 담은 원 입력 텍스트를 바꾸지 않고 저장하며, 첨부 원자료의 파일 이름과 바이트를 보존한다.
- 준비: 4단. 텍스트 `'é and K are exact source text'`를 이름이 `'é.txt'`인 파일에 UTF-8로 쓴다. `new_instance(root/'repo', goal=text, sources=[source], ...)`로 Git 저장소를 만들고 공개 `initialize`를 돈다.
- 실행: `ResearchRepository(...).load()`, 원자료 경로의 `read(path, head)`.
- 단언: `lifecycle.immutable_input.text`가 원 텍스트와 같다. 첫 원자료의 `name`이 파일 이름과 같고, `path`가 파일 이름을 담으며, 저장된 바이트가 파일 바이트와 같다.
- 대역: 없음.
- 비고: 실제 Git 저장소를 쓴다(`git_init`은 프로세스 안에서 초기화한다).

### `test_applied_import_uses_original_input_reference_and_exact_bytes` (행 33–39)
- 성질: 적용된 초기 해석의 증거는 원 입력 바이트의 해시와 작성자·검사자 실행을 가리킨다.
- 준비: 1단. `subTest`로 두 텍스트(`'A mathematical goal'`, 결합 문자·켈빈 기호 텍스트)마다 `applied_initial_intent(text)`.
- 실행: `initial_intent_evidence(instance, runtime)`.
- 단언: 반환이 정확히 `{'input_sha256': sha256(text.encode()), 'interpretation_execution_id': 'EX-author', 'check_execution_id': 'EX-check'}`다.
- 대역: 없음.
- 비고: `subTest` 케이스는 두 텍스트다.

### `test_changed_input_or_unapplied_result_cannot_complete_initialization` (행 41–47)
- 성질: 적용 기록이 없거나 해석 묶음의 입력 참조가 다른 입력을 가리키면 초기 의도 증거가 나오지 않는다.
- 준비: 1단. `applied_initial_intent`를 두 번 만든다. 첫째는 묶음의 `application`을 지우고, 둘째는 `input_ref`를 `'UI-other'`로 바꾼다.
- 실행: 각각 `initial_intent_evidence`.
- 단언: 두 경우 모두 `ValueError`(유형만)다.
- 대역: 없음.
- 비고: 이름의 "바뀐 입력"은 입력 참조를 바꾸는 것으로 재현한다. 원문 바이트 자체를 바꾸는 경우는 `test_lifecycle_engine.LifecycleTests.test_initial_intent_receipt_cannot_replace_import_evidence`의 `source` 케이스가 엔진 쪽에서 본다.

### `test_initial_grants_wait_for_activation_to_open_research` (행 49–54)
- 성질: 초기화 중에 준 연구 권한은 활성이 되지만 연구 행동을 큐에 넣지 않는다.
- 준비: 1단. `applied_initial_intent` 상태(수명 `initializing`).
- 실행: `gov.apply_decision`으로 `research_work` 역할의 재사용 로컬 권한 `GR-work`(원천 `GS-adoption`).
- 단언: 큐가 `[]`이고 권한 상태가 `active`다.
- 대역: 없음.
- 비고: `test_lifecycle_engine.LifecycleTests.test_initial_grant_does_not_queue_research_before_activation`이 같은 성질을 `FakeEngine`의 확장 제어로 본다.

### `test_grant_change_is_plan_basis_and_not_the_plan_execution_authority` (행 56–69)
- 성질: 활성 상태에서 권한이 바뀌면 그 결정을 근거로 행동 하나가 큐에 들어가지만, 그 행동의 실행 권한은 바뀐 권한이 아니라 계획 권한이다.
- 준비: 1단. `applied_initial_intent` 상태에서 수명을 `active`로 바꾸고, `research_plan` 권한 `GR-plan`을 적용한 뒤 큐를 비운다.
- 실행: `apply_decision`으로 `research_work` 권한 `GR-work`를 적용해 사건을 받는다. 이어서 큐 행동으로 `gov.authorize(instance, action, runtime=runtime)`.
- 단언: 큐 길이가 1이다. 인가가 `allowed`이고 `grant_id`가 `GR-plan`이다. 행동의 `decision_id`가 권한 결정 사건의 ID와 같다.
- 대역: 없음.
- 비고: 행동의 역할은 단언하지 않는다. 다만 인가가 `research_plan`만 가진 `GR-plan`을 골랐으므로 그 행동은 계획 역할의 요청이다.

## InitialFailureRetryTests (행 72–163)

`unittest.TestCase`를 상속한다. 설정 훅과 도우미가 없다.

### `test_public_retry_preserves_original_input_and_ended_predecessor` (행 73–163)
- 성질: 모델 시작 전에 실패한 초기 해석은 실행 실패 대기로 보존되고, 공개 요청 제어로 재시도하면 같은 행동이 앞 시도의 계보와 같은 활동으로 다시 돌아 해석을 적용하며, 원 입력과 끝난 앞 시도 기록은 바뀌지 않는다. 재시도의 전제(앞 시도의 종료, 원천, 권한, 로컬 종료 확인)가 하나라도 깨지면 재시도는 거부된다.
- 준비:
  - `install_adapter_fixture`로 능력 관측을 대체한다. 지역 러너 `FailingRunner`의 `run`은 항상 `ValueError('synthetic pre-start binding failure')`를 던진다.
  - `FakeEngine(workspace, config)`을 씨앗으로 쓴다. 설정은 학술 검색·운전자 끔, 도구 검토 창 60초, 자기 점검 창 5초다. 여기에 초기 권한 `GR-init`와 연구 권한 `GR-research`, 헌장 `charter_record`, AI 프로필마다 `adapter_for(profile).describe()`로 만든 능력 증거, 채택 결정을 적용한다. 채택 결정의 `initial_profile_ref`는 `model_policy.selection`이 고른 해석 프로필이고, 외부 정책은 `disabled`, 기본 검토 정책을 채택한다.
  - 런타임에 `processed_controls`, `reservations`, `provider_waits`, `updated_at`를 채운다.
  - 인스턴스와 런타임을 JSON 문자열 치환으로 새 ID(`new_id('RI')`)로 옮긴 뒤 `ResearchRepository(repo, identifier).initialize(...)`로 실제 Git 저장소에 게시한다.
  - 그 위에 `FailingRunner`를 단 엔진을 연다. 이 상태는 채택까지 끝나 첫 해석이 큐에 들어갈 초기화 상태이며, 공개 `initialize`를 거치지 않았다.
- 실행:
  1. `engine.run(max_steps=1)`로 첫 해석 시도가 실패하게 한다.
  2. 실패 상태를 사본으로 두고, `subTest`로 네 가지 변조(`live`, `source`, `grant`, `termination`)마다 `_retry_input_overflow_action({'id': 'UC-negative', 'config': {'retry_action': aid}})`를 부른다.
  3. 상태를 되돌리고 공개 `control(repo, identifier, 'request', config={'retry_action': aid}, request_id='UC-initial-retry')`를 보낸다.
  4. `PublicInitializationRunner`를 단 재시작 엔진에서 `process_controls()`를 부른다.
  5. `named_job_empty`를 참으로 패치하고 `run(max_steps=1)`.
- 단언:
  - 실패 뒤 종류 `execution_failure`인 대기가 있다. 그 실행(앞 시도)이 `ended`이고 `started_at`이 없다.
  - 네 변조는 각각 `ValueError`로 거부되고, 대기 행동이 그대로 남는다. `live`는 앞 시도를 `running`으로, `source`는 대기 행동의 `target`을 `UI-other`로, `grant`는 `GR-init`를 `revoked`로, `termination`은 앞 시도 용량의 `local_termination`을 `unknown`으로 바꾼다.
  - 공개 요청은 `accepted`다. 재시작 엔진의 제어 처리 뒤 그 행동이 대기에서 빠져 큐에 있고, `continuation_of`가 앞 시도다. 앞 시도 기록은 사본과 같고, 앞 시도를 대상으로 한 `operational_review`가 큐에 없다.
  - 실행 뒤 앞 시도를 잇는 후속 실행의 `outcome`이 `output_accepted`이고 `owner_activity_id`가 같다. `intent_imports`가 비어 있지 않고, `immutable_input`이 처음 값과 같다.
- 대역: `FixtureAdapter`(`install_adapter_fixture`, `adapter_for`), `FailingRunner`, `PublicInitializationRunner`(합성 해석 작성자·검사자, 실제 생산자·수신자 경로), `named_job_empty` 패치.
- 비고:
  - `subTest` 케이스는 네 변조다.
  - `termination` 케이스의 주석은 "로컬 종료를 확인하는 것은 `SessionSlots.release`뿐이고, 그것이 실행의 예약을 먼저 정산하며, 확인되지 않은 종료는 예약을 계속 잡는다"고 설명한다.
  - 이름의 "public retry"는 재시도 요청과 그 처리가 공개 제어 경로라는 뜻이다. 시작 상태 자체는 공개 `initialize`로 만든 것이 아니라 `FakeEngine`으로 조립해 직접 게시한 것이다.
  - 실제 Git 저장소를 쓴다.

## 관계

- **다른 층의 같은 기능.** 엔진 쪽의 초기 의도 완료(`_complete_initial_intent`)와 입력 초과 재시도(`_retry_input_overflow_action`)는 `test_lifecycle_engine`의 `test_initial_intent_receipt_cannot_replace_import_evidence`와 `test_retry_reuses_the_exact_held_action_and_current_authority`가 `FakeEngine`으로 본다. 해석 묶음의 작성·검사·적용 자체(`prepare_import`, `check_import`, `apply_import`)는 `test_governance`와 `test_governance_engine`이 다룬다. 공개 초기화에서 활성화까지의 끝단 연결은 `test_engine.EngineTests.test_public_initialization_reaches_active_with_distinct_interpretation`이 지킨다.
- **픽스처 의존.** `record_fixtures.applied_initial_intent`(1단 공통 상태), `research_fixtures.new_instance`와 `git_init`(공개 초기화와 실제 저장소), `engine_fixtures.FakeEngine`(씨앗 상태 조립)과 `PublicInitializationRunner`.
- **이 모듈에만 있는 도우미.** 지역 러너 `FailingRunner`.
- **겹치거나 보완하는 시험.** 원 입력의 유니코드 보존은 `test_lifecycle_engine.PublicLifecycleTests.test_public_unicode_original_survives_restart`와 `LifecycleBoundaryTests.test_original_unicode_bytes_survive_canonical_roundtrip`도 본다. 이 모듈은 원자료 파일 이름까지 넓혀 본다.

# 결과-KS: 커널 단계 K-저장

## 1. 브랜치, 커밋, 바꾼 파일

- 브랜치는 `c-ks`이고, worktree는 `C:/math-worktrees/c-ks`다. main `9b434f4`에서 시작했다.
- 마지막 커밋은 `ec2c1da`다. 파일 71개를 바꿨고, 523줄을 넣고 701줄을 뺐다.
- 아래 경로의 기준은 `.claude/skills/do-math/scripts/`다.

**제품 (36개)**

`do_math/`의 다음 파일을 바꿨다.

- `academic.py`, `academic_engine.py`, `activities.py`, `budget.py`, `cli.py`, `context_store.py`, `contracts.py`, `delegations.py`
- `engine.py`, `execution_profiles.py`, `external.py`, `formal.py`, `governance.py`, `initialization.py`, `input_basis.py`
- `knowledge_io.py`, `knowledge_records.py`, `lifecycle_engine.py`, `payloads.py`, `planning.py`, `preflight.py`
- `question_engine.py`, `questions.py`, `record_schemas/__init__.py`, `record_schemas/schemas.py`, `repository.py`
- `review_cycle.py`, `review_engine.py`, `review_policy.py`, `state_contract.py`, `submission.py`
- `task_contracts.py`, `task_scope.py`, `trust_inventory.py`, `trust_validation.py`

`do_math/` 밖에서는 `setup_lean.py`를 바꿨다.

**시험 (34개)**

`tests/`의 다음 파일을 바꿨다.

- `research_fixtures.py`, `test_boundary_repairs.py`, `test_decision_basis.py`, `test_delegation_storage.py`, `test_digest_characterization.py`
- `test_efficiency.py`, `test_external.py`, `test_governance_engine.py`, `test_initialization_efficiency.py`, `test_lifecycle_engine.py`
- `test_model_assessment_flow.py`, `test_performance_repairs.py`, `test_planning.py`, `test_preflight.py`
- `test_redesign_ACTIVITIES.py`, `test_redesign_CONTRACTS.py`, `test_redesign_ENGINE.py`, `test_redesign_EVIDENCE.py`, `test_redesign_EVIDENCE_walkthroughs.py`
- `test_redesign_GOVERNANCE.py`, `test_redesign_KNOWLEDGE.py`, `test_redesign_LIFECYCLE.py`, `test_redesign_PROFILES.py`, `test_redesign_REVIEWS.py`
- `test_redesign_STORAGE.py`, `test_redesign_SURFACE.py`, `test_redesign_TASKS.py`
- `test_review_cycle.py`, `test_review_engine.py`, `test_review_research.py`, `test_review_scope_wire.py`
- `test_state_checks.py`, `test_static_review_repairs.py`, `test_walkthrough_repairs.py`

**문서 (1개)**

- `docs/do-math/검사-경량화-이음새-계약.md`의 2.1절과 11절 표를 고쳤다. 스킬 문서가 아니라 저장소 문서이므로 파견 범위 안이다.
- 스킬 문서는 고치지 않았다.

**저장 계약**

- `state_contract.STATE_CONTRACT_ID`를 `do-math-state/7`로 올렸다.
- 아래 항목의 저장 형식 변경을 모두 이 판본 하나에 담았다.
- 호환 계층, 옛 필드를 읽는 기본값, 변환기는 두지 않았다.

## 2. ID별 처분

모든 ID의 처분은 `구현함`이다. 좌표는 모두 `do_math/` 기준이다.

**판본 표지와 응답 계약 ID**

- **STO-09 — 구현함.** 판본 식별은 루트 manifest의 `contract`와 기록 봉투의 `contract_id`에만 남겼다. 봉투는 상수를 참조하므로 판본을 올릴 때 고칠 곳이 아니다. 지운 표지는 다음과 같다.
  - research·runtime metadata의 `feature_version`·`contract_id`: 스키마, metadata 집합, `initialization`, `engine.initialize`
  - `execution_profiles.feature_version`: `seal_profile`, `validate_profile`
  - `tasks.feature_version`
  - `reservations.schema_version`: `budget._new_record`
  - `review_policy.version`
  - `preflight`의 `feature_version` 검사
  - 설치 manifest의 `feature_version`

  `review_policy.version`과 결속된 값도 함께 지웠다. 평가 레코드와 scope wire의 `policy_version`, `review_policy.py`의 대조, `policy_ref` 형식(`id@version:hash` → `id:hash`)이다. `STATE_FORMAT_VERSION`은 소비자가 없어져서 지웠다.
- **STO-08 — 구현함.**
  - 역할 입력 manifest의 `feature_version`은 STO-09에 따라 지웠다(`context_store` 생산자와 `validate_role_manifest`).
  - 응답 계약 ID는 `contracts.RESPONSE_CONTRACT_ID` 하나로 두었다. 여섯 곳이 이 이름을 참조한다: `contracts` 세 곳, `context_store`, `cli._emit`, `engine.validate_config`의 오류 문구.
  - `academic_engine`의 `feature_version` 사본은 RES-17과 함께 지웠다.
- **RES-17 — 구현함.** `academic_engine`의 `feature_version: 5`, 과제 스키마의 선택 필드, 시험 단언 1줄(`test_redesign_GOVERNANCE`)을 지웠다.

**digest와 값 영역**

- **RES-13 — 구현함.** `delegations.validate_delegation`과 `_basis`의 자원 검사를 `type(v) is int and v >= 0`으로 좁혔다. RES-08보다 먼저 적용했다.
- **RES-08 — 구현함.** 상태 값 식별을 `exact_content_hash`로 옮겼다. 대상은 다음과 같다.
  - `academic`의 전부
  - `academic_engine`의 `task_assessment_sha256`
  - `delegations`의 전부
  - `external`의 `request_sha256`과 멱등 키의 입력
  - `formal`의 ASCII 이스케이프 변종 3곳(`dependency_hashes`, `signature_hash`, `dependency_hash`)
  - `record_schemas/__init__.py` 수신자의 세 대조

  `formal.py`의 다른 두 곳은 옮기지 않았다.
  - `project_source_identity`의 `untracked_sha256`은 공유 툴체인 기록(저장 계약 밖, 디스크의 `TC-*.json`)과 비교되는 식별값이다. 바꾸면 기존 툴체인 기록이 결정 1의 범위 밖에서 어긋난다.
  - 363행은 프로세스 메모 키다.

  특성 시험(`test_digest_characterization`)도 고쳤다. 옛 도우미와의 바이트 동일성 단언 3건을 지우고, 현행 계약 단언 2건을 넣었다. 하나는 저장 값 digest가 값 영역 밖의 소수를 거부한다는 단언이고, 다른 하나는 학술·외부 작업 식별이 `exact_content_hash`를 쓴다는 단언이다.

**생산자 없는 필드와 신호**

- **ENG-13 — 구현함.** `_run_executor`에서 `runtime.installation`과 `implementation_history`를 쓰는 부분을 지웠다. 기동 때 `self._installation`을 한 번 평가하는 줄은 남겼다. 스키마의 두 필드도 지웠다.
- **STO-05 — 구현함.**
  - 38개 이름(가족별 40개 속성)을 스키마에서 지웠다. 이름마다 제품·시험을 다시 검색해 생산자와 소비자가 없음을 확인했다.
  - 참조표의 `subject_ref`와 `source_execution_id`를 지웠다.
  - `test_redesign_ACTIVITIES.test_03`의 `reservation_reconciled`를 실제 생산자(`engine` 복구) 모양으로 고쳤다.
- **REV-09 — 구현함.** 검토 주기의 `reviewers`, `judges`, `execution_accounting.reserved_execution_slots`를 대입하는 네 곳과 스키마의 NAT 두 항목을 지웠다. 입장 결과의 `reserved_execution_slots`는 남겼다.
- **ENG-12 — 구현함.** `_save`의 `pending_withdrawal` 루프와 스키마 필드를 지웠다.
- **OPS-11 — 구현함.** `coordinate_unit`과 `basis_scope`를 묶음, 스키마, required에서 지웠다.
- **RES-04 — 구현함.**
  - 지운 것: `wake_at`, `due_conditions`, `condition_states`, 대기 종류 `time`, `task_wake_due`와 `task_condition_due`, 스키마 세 항목, 초기화 항목
  - 쓰는 곳이 없어진 `evaluation_context` 인자를 `collect_due_events`와 `apply_event_schedule`에서 지우고, `lifecycle_engine`의 호출 한 줄을 고쳤다.
  - 이 기능만 검사하던 `test_planning` 시험 2건을 지웠다.
  - 시험 3건을 고쳤다. `test_planning` 1건은 남은 사건으로 단언하게 했다. `test_lifecycle_engine`의 시험은 `..._refresh_and_dispatch`로 이름을 바꿨다. `test_static_review_repairs`는 시간 깨우기를 실제 생산자가 있는 `selection_disposition.revisit`로 바꿨다.
- **OPS-04 — 구현함.**
  - 결정 스키마의 `revoked`, `status`, `revoked_at`을 지웠다.
  - 소비자 7행을 지웠다: `governance` 세 곳, `delegations` 두 곳, `task_scope.decision_is_current`. `decision_is_current`의 같은 줄에 있던 `lifecycle`과 `current` 조건도 닫힌 스키마에 없는 필드라 함께 지웠다.
  - 조건 문법의 `'decision'` 항목 전체를 지웠다.
  - 시험 10행은 철회를 흉내 내는 대신 실제 거부 사유로 바꿨다. 결정의 `source_sha256`을 바꿔 결정이 원천과 결속하지 않게 한다. 바꾼 뒤 모두 통과했다.
  - `test_redesign_TASKS`의 mutation 목록에서는 철회 두 항목을 지우고, 시험 이름에서 revoked를 뺐다.
- **STO-13 — 구현함.**
  - `_eligible`을 "길이 `LIMIT // 6` 이상의 문자열"로 좁혔다. 루트 payload의 `'manifest'` 자리표시 호출도 함께 고쳤다.
  - `FrozenDict`, `FrozenList`, `frozen()`을 지웠다. `repository`의 두 구별은 `FrozenText`로 좁혔다.
  - decode는 문자열이 아닌 payload를 봉인하기 전에 거부한다.
  - 폐기된 기능만 검사하던 시험 두 부분을 지웠다(`test_boundary_repairs`, `test_initialization_efficiency`).

**상태 값과 모양의 정본**

- **RES-01 — 구현함.** 소유 모듈 상수를 만들고, 스키마·조건 문법·검증기가 모두 이것을 참조하게 했다.
  - `knowledge_records.RECORD_LIFECYCLES`, `ASSESSMENT_USE_STATUSES`
  - `knowledge_io.KIND_STATUSES`
  - `governance.GOVERNANCE_STATUSES`(`validate_governance_state`도 참조)
  - `trust_validation.ENVIRONMENT_STATUSES`
  - 정본 enum이 없던 두 곳은 계약을 좁혔다. `input_basis.SOURCE_STATUSES = {"active"}`는 실제 생산자 값이고, `review_cycle.CYCLE_STATUSES`도 새로 두었다. 결정 항목은 OPS-04로 지웠다.

  `LIFECYCLE_VALUES`는 `planning.lifecycle_values()` 함수로 바꿨다. 지식 가족의 소유 모듈이 `planning`을 최상위에서 import하기 때문이다. 이 함수는 캐시 없이 호출할 때 상수로 표를 만든다. `EXPOSED_FIELDS`에서는 knowledge의 `/value`와 governance의 `/lifecycle`을 지웠다.
- **RES-02 — 구현함.** RES-01로 해결했다. 신뢰 환경의 조건 문법 값이 `ENVIRONMENT_STATUSES`, 곧 registered/active/superseded/invalid가 되었다.
- **RES-03 — 구현함.**
  - 네 가족 스키마의 `family`를 `const`와 required로 두었다.
  - `_validate_family_record`와 그 등록을 지웠다.
  - `validate_knowledge_records`에는 두 고유성 규칙만 남겼다.
  - `validate_activities`에서 상태 enum과 `assigned_execution_ids` 고유성의 중복 줄을 지웠다.
- **RES-12 — 구현함.**
  - 스키마 `_REQUIREMENT`를 공개 이름 `ACADEMIC_REQUIREMENT`로 바꾸고 엄격하게 만들었다. 텍스트는 `contracts.TEXT`(pattern `\S`), `criteria`는 minItems 1, 효과의 `id`와 `scope`는 비지 않은 텍스트, `grant_id`는 ID 형식이다.
  - `academic._requirement`는 이 스키마로 검사한 뒤 효과 ID 고유성과 기본값만 더한다. 요건 ID 고유성은 `requirement_record`에 남아 있다.
  - 검사기는 `lru_cache`로 한 번 만든다(3절 비용).
- **RES-14 — 구현함.**
  - `questions.QUESTION_OWNERS`와 `OPERATIONS_ROLES`를 두었다.
  - 참조하는 곳은 `link`, `resolution_error`의 두 곳, `question_engine`, `submission`의 wire enum(값을 정렬했다), 저장 스키마의 `owner` enum이다.
- **REV-17 — 구현함.**
  - `task_contracts.DISPOSITION_KINDS`를 wire `contracts.ITEM_DISPOSITION`의 종류에서 파생시켰다. 순환이 없어 지연 import 없이 최상위 import로 된다.
  - 이음새 계약 11절에 행을 더했다.
- **REV-19 — 구현함.**
  - 저장 `PROFILE_REF.revision`을 minimum 1로 좁혔다.
  - `validate_contract_rules`를 지우고, 과제 가족 검증기와 `validate_task_contract`가 `validate_contract_meaning`을 쓰게 했다.
- **OPS-05 — 구현함.**
  - `trust_validation`에 다음을 두었다: `RECORD_ID_PATTERN`, `BINDING_SCHEMA`(`BINDING_FIELDS`에서 파생), `ENVIRONMENT_PROPERTIES`와 `ENVIRONMENT_REQUIRED`, `ENVIRONMENT_STATUSES`.
  - 저장 스키마의 `trust_environments`와 `trust_bindings`, `trust_inventory.RECORD_SCHEMA`의 ID 패턴, `environment_errors`의 필드 집합이 이 조각을 참조한다.
  - 저장된 `toolchain_record.id`는 이제 패턴으로 좁혀진다. 전에는 TEXT였고, 같은 제약은 활성 환경의 의미 검사에만 있었다.
  - 파일 경로 규칙은 `trust_inventory.record_path` 하나로 모았다. `setup_lean` 두 곳, `record_reference_errors`, `records_for`의 glob이 이것을 쓴다.

**수명 관문**

- **STO-04 — 구현함.**
  - 관문은 `record_schemas.validate_lifecycle`(예외 기반)로 옮겼다. 검사하는 것은 수명·상태의 존재, 영구 종료, UTC 최고 수위다.
  - `lifecycle.state`와 runtime `status`의 값 집합은 스키마 enum이 되었다.
  - `derived_readiness`와 `inspect_current_state`를 지웠다.
  - `preserve_rejected_candidate`는 유일한 호출자가 있는 `lifecycle_engine`의 모듈 함수로 옮겼다.
  - `preflight`에는 스킬 구조 검사만 남았다.
  - 시험 네 곳을 예외 단언으로 고쳤다: `test_preflight`, `test_lifecycle_engine`, `test_redesign_LIFECYCLE`, `research_fixtures`의 docstring. 수명 규칙 시험은 `test_lifecycle_rules_reject_a_state_without_its_utc_high_water`로 이름을 바꿨다.

**집계**

- 구현함 22건
- 구현하지 않음 0건
- 조건 불성립 0건
- 끝내지 못함 0건

## 3. 공유 정의와 지운 공개 이름

**새로 만든 공유 정의**

모두 `docs/do-math/검사-경량화-이음새-계약.md` 11절에 행을 더했다.

| 정의 | 위치 |
|---|---|
| `RESPONSE_CONTRACT_ID` | `contracts.py` |
| `RECORD_LIFECYCLES`, `ASSESSMENT_USE_STATUSES` | `knowledge_records.py` |
| `KIND_STATUSES` | `knowledge_io.py` |
| `GOVERNANCE_STATUSES` | `governance.py` |
| `SOURCE_STATUSES` | `input_basis.py` |
| `CYCLE_STATUSES` | `review_cycle.py` |
| `QUESTION_OWNERS`, `OPERATIONS_ROLES` | `questions.py` |
| `ENVIRONMENT_STATUSES`, `ENVIRONMENT_PROPERTIES`, `ENVIRONMENT_REQUIRED`, `BINDING_SCHEMA`, `RECORD_ID_PATTERN` | `trust_validation.py` |
| `record_path(directory, record_id)` | `trust_inventory.py` |
| `ACADEMIC_REQUIREMENT`(옛 `_REQUIREMENT`) | `record_schemas/schemas.py` |
| `validate_lifecycle(instance, runtime)` | `record_schemas/__init__.py` |
| `lifecycle_values()` | `planning.py` |

옮긴 정의는 `preserve_rejected_candidate` 하나다(`preflight` → `lifecycle_engine`).

**새 상태 비용**

- `academic._requirement_checker`는 `lru_cache`로 만든 프로세스 전역 검사기 하나다. 입력인 스키마가 상수여서 수명 규칙과 무효화가 필요 없다.
- 이 캐시를 둔 이유는 검증 파일(RES-12 보충)이 적은 비용 때문이다. `governance_view`가 호출마다 요건을 검사하므로, 호출마다 검사기를 새로 만들면 비용이 쌓인다.
- 그 밖의 새 캐시와 새 상태는 없다.

**지운 공개 이름**

- `state_contract.STATE_FORMAT_VERSION`
- `preflight.inspect_current_state`, `preflight.preserve_rejected_candidate`(옮김)
- `planning.LIFECYCLE_VALUES`(→ `lifecycle_values()`)
- `task_contracts.validate_contract_rules`
- `knowledge_records._validate_family_record`
- `payloads.FrozenDict`, `FrozenList`, `frozen`
- `trust_validation.ENVIRONMENT_FIELDS`, `OPTIONAL_FIELDS`(모듈 비공개 `_ENVIRONMENT_FIELDS`, `_OPTIONAL_FIELDS`로 바꿈)
- `record_schemas.schemas._REQUIREMENT`(→ `ACADEMIC_REQUIREMENT`)

`engine.CONTRACT` 별칭은 ENG-06 범위라 남겼다.

## 4. 필요한 문서 변경

스킬 문서라 고치지 않았다. 통합자나 문서 그룹이 반영할 내용이다.

- **`README.md` 15행:** "저장 계약은 `do-math-state/6`" → `do-math-state/7`.
- **`references/CLI-실행-계약.md`:**
  - 5행과 54행의 `do-math-state/6` → `do-math-state/7`.
  - 저장 형식 설명에 "판본 식별은 루트 manifest만 싣고, 기록과 metadata에는 판본 표지가 없다"는 사실을 더할 수 있다.
- **`계약/동일성-검토.md` 13행:** "`policy_id`와 `policy_version=5`는 실제 적용한 정책" → "`policy_id`는 실제 적용한 정책". scope wire 스키마와 수신 검사에서 `policy_version`이 없어졌고, 검토 정책에도 `version`이 없다.
- **`references/과제-착수조건.md` 허용 포인터 표:**
  - `knowledge` 행에서 `/value`를 지운다(26행).
  - `governance` 행에서 `/lifecycle`을 지운다(30행).
  - `test_walkthrough_repairs`의 문서·코드 대조 시험이 이 표를 `planning.EXPOSED_FIELDS`와 비교하므로, 이 수정이 들어가야 통과한다.
  - 표 위 문장의 기록 가족 목록에 있는 `decision`은 `planning.RECORD_FAMILIES`에 그대로 있으므로 유지한다. 조건 문법에서 `record_lifecycle_is`의 decision 값만 없어졌다.
- **`.agents/` 생성 사본:** 통합자가 재생성한다.

## 5. 실행한 시험

**수정 도중의 부분 실행 (편집 확인)**

- 명령: `python -B scripts/run_tests.py test_state_contract_registration test_redesign_STORAGE test_planning test_academic test_digest_characterization test_preflight test_boundary_repairs test_redesign_LIFECYCLE test_state_checks test_questions test_delegation_storage test_external test_review_cycle test_contracts`
- 결과: 통과 194, 실패 3, 오류 1. 네 건 모두 내 변경을 따라오지 못한 시험이었다.
  - `test_delegation_storage`: 원천 status `superseded`를 흉내 냈다. 실제 필드인 `revision` 변경으로 바꿨다.
  - `test_redesign_STORAGE`의 학술 해소 시험: 시험이 `json_digest`로 다시 봉인했다. `exact_content_hash`로 바꿨다.
  - `test_redesign_STORAGE`의 수명 관문 시험: 문구가 스키마 enum 문구로 바뀌었다. 단언을 `runtime/status`로 고쳤다.
  - `test_state_checks.test_unknown_version...`: 같은 이유로 단언을 `^runtime/status/`로 고쳤다.
- 수정 뒤 이 넷과 `test_state_checks`, `test_external`을 다시 돌려 25건 모두 통과했다.

**넓은 인계 확인**

- grep으로 고른 약 75개 모듈을 백그라운드로 돌렸다.
- 통합자 지시로 중단했고, 실행하지 않은 것으로 센다. 결과는 없다.

**import 확인**

- 바꾼 `.py` 전부를 `python -m py_compile`로 확인했다.
- 모든 시험 모듈 135개를 `importlib`로 적재하는 확인도 했다.
- 바꾼 제품 모듈은 각각 새 프로세스에서 단독 import해 순환이 없음을 확인했다.
- 모두 통과했다.

**새로 쓰거나 고친 시험의 ID 단위 실행**

- 명령: `python -B scripts/run_tests.py <ID 77개>`. 목록은 diff에서 고친 줄을 둘러싼 시험 메서드로 뽑았다. 모듈 수준 도우미를 고친 작은 모듈은 모듈 단위로 넣었다(`test_digest_characterization`, `test_external`, `test_planning`, `test_redesign_LIFECYCLE`, `test_redesign_REVIEWS`, `test_redesign_EVIDENCE`, `test_redesign_EVIDENCE_walkthroughs`, `test_redesign_SURFACE`, `test_review_cycle`, `test_performance_repairs`, `test_model_assessment_flow`).
- 결과: 통과 290, 실패 1, 미실행 12. 약 184초가 걸렸다.
- 실패 1건은 `test_performance_repairs.StorageValueTests.test_inspection_builds_no_json_bytes_and_publication_checks_the_value_domain`이었다. 소수 값을 넣는 수단으로 지운 필드 `runtime.installation`을 썼기 때문이다. 수단을 남은 EVIDENCE 필드 `provider_wake`로 바꾸고, 이 ID만 다시 돌려 통과했다.
- 미실행 12건은 `test_redesign_EVIDENCE.TraceabilityCheckerTests`의 `setUpClass` 오류로 돌지 않은 것이다.
  - 원인: 추적표(동결)가 옛 시험 좌표 `test_redesign_TASKS...test_bare_unrelated_revoked_expired_or_changed_authority_cannot_transfer`를 가리키는데, OPS-04 때문에 이 시험의 이름이 바뀌었다.
  - 결정 2에 따라 추적표를 검사하는 시험은 지울 대상이고, 시험 이름이 추적표 좌표와 달라져도 된다. 그래서 내 수정 대상이 아니다.
  - 내가 이름을 바꾼 다른 시험 셋도 같은 종류다: `test_lifecycle_engine...refresh_and_dispatch`, `test_redesign_TASKS...changed_decision_source...`, `test_redesign_LIFECYCLE...lifecycle_rules_reject...`.
- 변경 전부터 실패하던 것은 확인하지 못했다. 기준 판본 실행이 없다.

**돌리지 않은 관련 시험**

- 고친 제품 이름이 나오는 나머지 모듈 전체다. 통합자 지시로 통합 확인에 맡겼다.
- `test_walkthrough_repairs`의 문서 대조 시험은 4절의 문서 수정 전까지 실패할 것으로 예상한다. `EXPOSED_FIELDS`와 `references/과제-착수조건.md`가 다르기 때문이다. 돌리지는 않았다.

## 6. 기능이나 시험 범위가 바뀐 것

- **저장 형식(`do-math-state/7`)**
  - 이유: 결정 5.
  - 잃는 것: 기존 인스턴스와의 호환. 현재 인스턴스는 없다. 저장된 판본 이력(`implementation_history`)도 잃는다. 이를 읽는 소비자는 없었다.
  - 얻는 것: 판본을 올릴 때 고칠 곳이 루트 상수 하나다. 저장 크기가 준다(runtime에서 설치 manifest 약 10KB와 판본 변경당 약 21KB).
- **시각·조건 깨우기(RES-04)**
  - 이유: 생산자가 없다.
  - 잃는 것: 시험만 쓰던 기능과 시험 2건, 시험 한 건의 schedule 단언.
  - 얻는 것: 갱신마다 돌던 조건 평가 루프가 사라진다.
- **결정 철회 흉내(OPS-04)**
  - 잃는 것: 존재하지 않던 "철회된 결정 거부"의 시험 단언.
  - 얻는 것: 원천 결속 위반이라는 실제 거부 사유로 같은 경로를 검사한다.
- **dict 봉인(STO-13)**
  - 잃는 것: 폐기된 manifest 봉인의 시험 두 부분.
- **digest 특성 시험(RES-08)**
  - 잃는 것: 옛 도우미와의 바이트 동일성 단언 3건.
  - 얻는 것: 값 영역과 식별 규칙에 대한 현행 단언.
- **계약을 좁힌 것**
  - 지금은 거부되는 것: 원천 status `active` 밖의 값, 검토 주기 status 세 값 밖의 값, 질문 owner 세 값 밖의 값, `toolchain_record.id` 형식, 학술 요건의 빈 텍스트·빈 criteria·ID 형식이 아닌 `grant_id`, 프로필 참조 `revision` 0.
  - 이유: RES-01, RES-12, RES-14, OPS-05, REV-19.
  - 제품 생산자는 이 값들을 만들지 않으므로 잃는 기능은 없다.
- **조건 문법**
  - 이제 제출 때 거부되는 것: governance의 `withdrawn`, knowledge의 `/value`, governance의 `/lifecycle`, decision 상태 조건. 전에는 평가 오류가 되거나 영원히 참이 되지 않았다.
  - 신뢰 환경의 `registered`는 이제 허용된다.

## 7. 막힌 지점, 접근을 바꾼 지점, 예상과 달랐던 결과

- **`LIFECYCLE_VALUES`를 모듈 상수로 둘 수 없었다.** `knowledge_records`와 `knowledge_io`가 `planning`을 최상위에서 import하기 때문이다. 그래서 `lifecycle_values()` 함수로 바꿨다. 처음에는 `lru_cache`를 붙였다가 새 상태가 불필요해서 지웠다.
- **stale 결정의 대체 수단.** 결정 철회를 흉내 내던 시험을 대체할 수단으로 `source_sha256` 변경을 골랐다. 모든 해당 시험이 같은 예외 경로로 통과했다.
- **`test_redesign_STORAGE`의 manifest 시험.** `feature_version` 컨테이너 삭제를 단언하던 시험은 실제로 metadata 소속 불일치를 검사하고 있었다. 같은 성질을 `status` 컨테이너로 다시 단언했다.
- **줄바꿈 처리 착오.** 편집 도구의 줄바꿈 처리 때문에 파일 하나가 한때 CRLF로 바뀌었다. 곧바로 원래의 LF로 되돌렸다. 이음새 계약 문서는 원래 CRLF여서 그대로 두었다.
- **commit-harness를 적용하지 않았다.** 병렬 worktree에서 기억 노드를 만들면 번호와 색인이 충돌한다. 그래서 파견과 통합자 지시대로 브랜치 커밋만 했다. 이 작업의 기억 노드 결정화는 통합 커밋에 맡긴다.

## 8. 다른 그룹 범위에서 발견한 문제

- **REV 영역 — 상태 값 digest.** `review_cycle`(`proposal_digest`, `sealed_input_sha256`, 조사 `request_digest`, finding 키), `review_engine`(924행 `event_sha256`), `input_basis`(`review_input_basis.sha256`, STO-10)는 여전히 상태 값을 `json_digest`로 식별한다. 이음새 계약 2.1과 다르다. RES-08은 RES 영역만 옮겼다.
- **REV·ENG 영역 — 결정의 다른 생산자 없는 필드.** `task_scope.decision_is_current`가 읽는 `expires_at`, `valid_from`, `source_basis`는 닫힌 결정 스키마에 없다. OPS-04처럼 도달하지 않는 조건이다.
- **STO·RES 영역 — 원천의 생산자 없는 필드.** `sources` 스키마의 `replaced_by`와 `revoked_at`은 생산자가 없다. STO-05의 이름 단위 검색이 놓친 종류다.
- **K-구조(ENG-10)와의 겹침.** `engine.validate_config`의 오류 문구 줄을 STO-08 때문에 고쳤다. `validate_config`를 옮기는 K-구조의 변경과 같은 함수이므로 병합 때 충돌할 수 있다. 결과는 "문구가 `RESPONSE_CONTRACT_ID`를 참조한다" 하나다.
- **`review_policy.py` 문구.** `"review-policy-v5-default"` ID와 `"...differ from v5 contract"` 문구 둘은 판본 표지가 아닌 이름으로 남아 있다. 내가 고친 문구 하나만 바꿨다.
- **K-구조(REV-23)와의 겹침.** `trust_validation.ENVIRONMENT_PROPERTIES`는 저장 스키마에서 `record()`로 감싸 쓰므로 하위 노드를 공유한다. REV-23의 제자리 변경 방어와 겹치는지 확인이 필요하다.

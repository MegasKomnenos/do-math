# 경량화 조사 — 저장과 상태 영역 (STO)

작성: 2026-09-26. 계약은 `C:/math/임시/경량화-조사-2026-09-26/기준.md`를 따른다.

경로 표기: 따로 밝히지 않으면 `C:/math/.claude/skills/do-math/scripts/`를 기준으로 한 상대 경로다. 예를 들어 `do_math/repository.py:230`은 `C:/math/.claude/skills/do-math/scripts/do_math/repository.py`의 230행이다. 행 번호는 커밋 `8d2ffd0`의 작업 트리 기준이다.

## 1. 읽은 범위

### 전문을 읽은 파일

| 파일 | 행 수 |
|---|---|
| `do_math/repository.py` | 803 |
| `do_math/git_store.py` | 603 |
| `do_math/context_store.py` | 938 |
| `do_math/state_contract.py` | 207 |
| `do_math/state_checks.py` | 498 |
| `do_math/record_schemas/__init__.py` | 608 |
| `do_math/record_schemas/domains.py` | 500 |
| `do_math/record_schemas/schemas.py` | 248 |
| `do_math/file_io.py` | 178 |
| `do_math/retention.py` | 286 |
| `do_math/events.py` | 81 |
| `do_math/operation_trace.py` | 224 |
| `do_math/input_basis.py` | 110 |
| `do_math/input_recovery.py` | 52 |
| `do_math/payloads.py` | 155 |
| `do_math/relation_refs.py` | 16 |
| `C:/math/.claude/skills/do-math/references/입력-소비자.md` | 54 |
| `C:/math/임시/경량화-조사-2026-09-26/기준.md` | 120 |
| `C:/math/docs/do-math/검사-경량화-이음새-계약.md` | 159 |

### 일부만 읽은 파일

이음새를 따라 판정에 필요한 범위만 읽었다.

- `do_math/engine.py`: 72-76, 89, 133, 156, 163-186, 255-300, 380-392, 590-602, 830-925, 1123-1138, 1520-1580, 1612-1624, 2100-2110, 2285-2380, 2410-2425, 3355-3372, 3460-3470, 4197-4300, 4412-4430, 4740-4800
- `do_math/execution_profiles.py`: 22-23, 49-56, 235-275
- `do_math/execution_lifecycle.py`: 8-10, 40-80, 165-185
- `do_math/preflight.py`: 1-140
- `do_math/planning.py`: 18-36, 480-500
- `do_math/submission.py`: 66-82, 414-445
- `do_math/governance.py`: 40-110, 740-775, 848-905, 930-950
- `do_math/governance_engine.py`: 122-171
- `do_math/control_contracts.py`: 1-140
- `do_math/integration.py`: 500-540
- `do_math/academic_engine.py`: 1-40
- `do_math/knowledge.py`: 17-21
- `do_math/task_contracts.py`: 13-15, 181-206
- `do_math/lifecycle_engine.py`: 880-900
- `do_math/scheduler.py`: 488-502
- `do_math/reporting.py`: 140-175
- `do_math/session_slots.py`: 10-32
- `tests/test_git_store.py`: 316-330
- `tests/test_state_checks.py`: 46-62
- 테스트 이름 목록: `tests/test_state_checks.py`, `tests/test_performance_save.py`, `tests/test_git_store.py`

## 2. 후보

#### STO-01: 상태 점검(`inspect_state`)이 적재 검증에서 이미 성립한 조건을 다시 검사한다

- 유형: 수신재검사중복
- 위치:
  - 점검 쪽(재검사)
    - `do_math/state_checks.py:220-234`: 모든 영역의 가족 행마다 스키마를 다시 검사한다.
    - `do_math/state_checks.py:236-249`: 저장 값 영역과 레코드 ID 중복을 검사한다.
    - `do_math/state_checks.py:253-254`: `feature_version`을 검사한다.
    - `do_math/state_checks.py:288`, `:308`, `:310`, `:314-315`, `:318-319`, `:327-331`, `:333-344`, `:350-355`, `:384-391`, `:394-397`, `:403`, `:407-414`, `:462`(뒤이은 `context_store.py:793`에서 같은 함수를 다시 부른다), `:474-488`, `:492-493`
    - `do_math/engine.py:4787`(`check`의 `_require_current_contract`), `:4799`(`check`의 `validate_knowledge_records`), `:4758`(`_inspect_before_write`), `:599`(`__init__`)
  - 적재 쪽(정본 검사)
    - `do_math/repository.py:185`(`contract.validate`)
    - `do_math/state_contract.py:163-178`: 스키마, 가족 검증기, ID 경로 안전성, 전역 유일성을 검사한다.
    - `do_math/state_contract.py:184-192`: 참조 무결성(`REFERENCES`)을 검사한다.
    - `do_math/record_schemas/__init__.py:218-222`: `inspect_current_state`를 부른다.
    - `do_math/record_schemas/__init__.py`의 의미 검사: `:231-232`, `:248-262`, `:274-277`, `:347-348`, `:356-359`, `:369-387`, `:402-421`, `:514-521`
    - `do_math/repository.py:546`: 정규 바이트 대조가 저장 값 영역을 함축한다.
- 현상:
  - `inspect_state` 호출자는 넷이다. 모두 방금 `store.load`로 검증을 통과한 스냅숏을 넘긴다. `engine.py:1539`(status)는 `load` 뒤에 `_evaluate_stops`만 거친다. `engine.py:1529`와 `:1620`은 `load` 직후 `_inspect_before_write`를 부른다. `engine.py:4779`(check)와 `reporting.py:157-158`도 `load` 뒤에 부른다. `load`는 `_read_documents`에서 `contract.validate`를 돌리고, 그 안에서 스키마, 가족 검증기, 참조와 `validate_semantics`가 모두 실행된다.
  - `inspect_state`는 같은 조건 상당수를 다른 코드로 다시 검사한다. 대응은 다음과 같다.
    - 스키마: `state_checks.py:233-234`가 `state_contract.py:164`를 다시 한다.
    - 가족 검증기 `validate_task_contract`, `validate_profile`, `_validate_reservation`: `state_checks.py:310/328/350`이 `record_schemas/__init__.py:125-126`을 다시 한다.
    - 참조: `state_checks.py:351-355`(예약의 제약·소유자)와 `:478-479`(자기 점검 의무의 실행)가 `record_schemas/__init__.py:52`, `:47`을 다시 한다.
    - 의미 검사
      - `validate_governance_state`: `state_checks.py:288`이 `record_schemas/__init__.py:232`와 같다.
      - `validate_activities`: `:308`이 `:249`와 같다.
      - `validate_knowledge_records`: `:403`이 `:248`과 같다. `engine.py:4799`까지 치면 세 번째다.
      - 실행과 프로필의 결속: `:340-344`가 `:252-258`과 같다.
      - `stop_phase`: `:336-337`이 `:261-262`와 같다. 같은 조건을 `state_checks.py:492-493`이 파일 안에서 한 번 더 검사한다.
      - 외부 작업의 confirmed·failed와 요청 결속: `:388-391`, `:394-397`이 `:369-379`와 같다.
      - 형식 증거와 동일성 전제: `:407-414`가 `:406-421`과 같다.
      - 관찰 규칙, 처분, 자기 점검 응답: `:474-488`이 `:358-359`, `:380-387`, `:402-404`와 같다.
    - `feature_version`: `state_checks.py:253-254`가 `preflight.py:39-42`와 같다.
    - `_require_current_contract`: `engine.py:599`, `:4758`, `:4787`이 `record_schemas/__init__.py:219-222`와 같다. 다만 뒤쪽은 `lifecycle`이 있을 때만 돈다.
  - 실측(합성 자료, 6절 명령 참조)
    - 실행 레코드 2000행의 스키마 재검사에 1.065초가 걸렸다.
    - 11.3MB 합성 상태의 `validate_storage_value` 순회에 1.750초가 걸렸다.
  - `_inspect_before_write`는 모든 `run`과 `process_controls` 시작마다 `record_storage` 영역을 돈다. 이 영역에는 순회와 스키마 재검사가 포함된다. `status`는 모든 영역을 돈다.
- 제안:
  1. `inspect_state`의 전제를 "적재 검증을 통과한 스냅숏"으로 명시한다. 위에 적은 재검사 항목은 지운다.
  2. 각 영역의 `checked_invariants`에는 `"load-time state contract validation"` 한 줄을 넣는다. 적재 때 성립했다는 사실을 보고에 남기기 위해서다.
  3. 점검에만 있는 조건은 남긴다. 해당하는 것은 다음과 같다.
     - 종료 과제에 살아 있는 작업자가 있는지
     - 의무 이전 대상이 있는지
     - `outcome ∈ OUTCOMES`
     - 예약 원장의 합계
     - 외부 작업과 EX 실행의 대응
     - `formal_usable`
     - 목표 감사와 학술 요건
     - 준비·선택의 단일성
     - 입력 manifest 바이트
     - 반복 계보
     - 정리 실패
     - 출처의 `name` 누락과 `name`·`path` 중복
  4. `engine.check`의 `_require_current_contract`와 `validate_knowledge_records` 재호출도 지운다. `state_checks.py:462`의 `validate_role_manifest` 단독 호출도 지운다. 이 호출은 `verify_manifest_artifacts`가 안에서 다시 한다.
  5. `lifecycle`이 없는 상태를 `_require_current_contract`가 거부하는 차이는 보존해야 한다. 방법은 둘 중 하나다.
     - `validate_semantics`가 `inspect_current_state`를 조건 없이 부르게 한다. 이 경우 적재 거부가 되므로 동작이 바뀐다.
     - `engine.__init__`의 한 곳만 남긴다.
- 동작: 변경. 합격과 불합격 판정은 호출자 넷 모두에서 보존된다. 적재가 이미 같은 조건으로 거부하기 때문이다. 달라지는 것은 두 가지다.
  - 보고서의 `checked_invariants` 이름 목록
  - 검증되지 않은 상태를 `inspect_state`에 직접 넘기는 용도(현재는 시험만 이렇게 쓴다)
- 실익:
  - 측정: 2000행 스키마 재검사 약 1.07초, 11MB 저장 값 순회 약 1.75초. 합성 자료다.
  - 추정: `status` 한 번에 수 초, `run`·`process_controls` 시작마다 약 2초 이상(11MB 기준). 코드는 `state_checks.py`에서 약 60행이 줄어든다.
  - 같은 조건의 두 표현이 어긋날 경로가 없어진다. 이미 어긋난 예가 있다. `outcome`은 적재 쪽은 참 여부만 보고, 점검 쪽은 `OUTCOMES` 소속까지 본다.
- 위험과 보호:
  - `tests/test_state_checks.py`는 손으로 변형한 상태를 `inspect_state`에 직접 넘긴다. 해당 테스트는 다음과 같다.
    - `test_execution_state_lineage_profile_and_activity_mutations`
    - `test_separated_knowledge_and_source_mutations`
    - `test_external_error_http_remains_unknown_and_reconciliation_is_distinct`
    - `test_reservation_requires_balanced_settlement_and_existing_owner`
  - 이 시험들은 같은 변형이 `contract.validate`에서 거부되는지를 보는 형태로 옮겨야 한다.
  - 점검 결과 형식은 `tests/test_reporting.py`의 `test_status_reports_artifact_presence_and_length_in_one_batch_without_bytes`가 덮는다.
- 확신: 중간. 적재가 먼저 도는 것은 호출자 넷을 모두 읽어 확인했다. 점검에만 있는 항목 가운데 `validate_withdrawal_record`(`state_checks.py:311-313`)와 `self_check_feedback`(`:476-477`)이 적재 쪽에도 있는지는 미확인이다. 두 함수 본문을 읽지 않았다.
- 다른 영역: `do_math/engine.py`, `do_math/reporting.py`, `do_math/preflight.py`, `tests/test_state_checks.py`

#### STO-02: 상태 열거값이 스키마 리터럴, 도메인 상수, 의미 검사, 점검에 따로 적혀 있다

- 유형: 이음새중복
- 위치:
  - 실행 상태
    - 스키마 리터럴: `do_math/record_schemas/schemas.py:104`
    - 상수: `do_math/execution_lifecycle.py:8`
    - 점검: `do_math/state_checks.py:334`
  - `stop_phase`
    - 스키마 리터럴: `schemas.py:107`
    - 상수: `execution_lifecycle.py:9`
    - 점검: `state_checks.py:336`
    - 의미 검사: `record_schemas/__init__.py:261-262`
  - `outcome`
    - 스키마: `schemas.py:106`(`TEXT`)
    - 상수: `execution_lifecycle.py:10`
    - 점검: `state_checks.py:338`
    - 의미 검사: `record_schemas/__init__.py:259-260`(참 여부만 본다)
  - 과제 상태
    - 스키마 리터럴: `schemas.py:121`
    - 상수: `do_math/task_contracts.py:13`
    - 가족 검증기: `task_contracts.py:51`
    - 점검: `state_checks.py:314`
  - 외부 작업 상태
    - 스키마 리터럴: `schemas.py:179`, `do_math/record_schemas/domains.py:177`
    - 점검 상수: `state_checks.py:16-17`
- 현상:
  - 같은 값 집합을 스키마는 `enum("queued", ...)` 리터럴로 다시 적는다. 코드는 `frozenset` 상수로 적고, 점검은 그 상수나 로컬 집합으로 다시 비교한다.
  - 과제 상태는 같은 저장 시점에 스키마 enum과 가족 검증기(`task_contracts.py:51`)가 두 번 확인한다.
  - `outcome`은 이미 어긋났다. 스키마는 자유 문자열이고, 의미 검사는 참 여부만 보며, 점검만 `OUTCOMES` 소속을 본다.
- 제안:
  - 스키마가 상수에서 enum을 만든다. 예: `enum(*sorted(EXECUTION_STATUSES))`.
  - `state_checks.py:16-17`의 로컬 집합은 지운다. 외부 작업 상태 상수는 소유 모듈(`external.py` 추정, 미확인)에 하나 두고 스키마가 그것을 참조한다.
  - 레코드 하나의 실행 상태 불변식은 `execution_lifecycle.py`의 `execution_record_errors(row)` 하나로 모은다. 해당하는 불변식은 다음 셋이다.
    - 종료에는 `ended_at`와 `outcome`가 있어야 한다.
    - `stop_phase`는 정확히 `stopping`일 때만 있다.
    - `output_accepted`에는 영수증이 있어야 한다.
  - `validate_semantics`는 이 함수를 쓴다. 점검 쪽은 STO-01에 따라 지운다.
  - `task_contracts.py:51`의 enum 재검사는 지운다. 스키마가 먼저 돈다.
- 동작: 보존. 스키마를 상수에서 만들어도 값 집합이 같으므로 최종 스키마가 같다. `default_state_contract().manifest()['sha256']`가 변하지 않는 것으로 확인할 수 있다. `outcome ∈ OUTCOMES`를 적재 검사로 올리는 것은 선택이며, 그 경우는 변경이다.
- 실익: 값 집합의 정본이 하나가 된다. 새 상태를 추가할 때 고칠 곳이 4곳에서 1곳으로 준다. 행 수는 소폭(추정 10행) 줄어든다.
- 위험과 보호: 스키마 동일성은 manifest 다이제스트 비교로 기계 확인할 수 있다. `tests/test_state_checks.py`의 `test_execution_state_lineage_profile_and_activity_mutations`가 `status` 변형을 덮는다.
- 확신: 높음. 상수와 리터럴이 같은 집합인 것을 원문으로 확인했다.
- 다른 영역: `do_math/execution_lifecycle.py`, `do_math/task_contracts.py`, `do_math/external.py`(미확인)

#### STO-03: 후보 검증이 저장 값 영역을 통째로 순회한 뒤, 인코딩이 모든 레코드를 다시 순회하고 다시 직렬화한다

- 유형: 운영비용
- 위치:
  - `do_math/repository.py:230-231`: 상태 전체에 `validate_storage_value`를 돌린다.
  - `do_math/repository.py:265`, `:659-697`: `_encode_families`가 레코드마다 `canonical_json`을 부른다(`:689`, `:692`, `:695`). `canonical_json`은 `:108`에서 저장 값 영역을 다시 순회한다.
  - `do_math/repository.py:286-300`: 부모 파일 바이트(`old_files`)가 이미 메모리에 있다.
- 현상:
  - 한 번 저장할 때 상태 전체를 파이썬 재귀로 두 번 순회한다. 한 번은 `:230-231`의 전체 순회이고, 한 번은 레코드별 `canonical_json` 안의 순회다.
  - 게다가 부모와 같은 레코드까지 전부 다시 `json.dumps(indent=2)` 한다.
  - 부모와의 레코드별 비교는 이미 검증 생략에 쓰이고 있다(`state_contract.py:154-163`). 인코딩에는 쓰이지 않는다.
  - 실측(11.3MB 합성 상태)
    - 전체 순회: 1.750초
    - 레코드별 `canonical_json` 2000건: 2.203초
    - 같은 크기 dict의 동등 비교: 0.006초
- 제안:
  1. `_validate_candidate`의 `:230-231` 전체 순회를 지운다. 인코딩되는 모든 봉투는 `canonical_json`에서 같은 검사를 받는다. derived 가족은 인코딩하지 않지만 다른 가족에서 다시 계산되므로 누락되는 값이 없다.
  2. `save_with_state`는 `parent_state`와 `old_files`를 이미 갖고 있다. 이를 `_encode_families`에 넘겨, 같은 가족·같은 ID에서 부모 레코드와 `==`인 레코드는 부모의 파일 바이트를 그대로 쓴다. 정규 직렬화는 결정적이므로 바이트가 같다. 부모 봉투에 `payloads`가 있으면 해당 payload blob 경로도 함께 승계한다.
- 동작: 보존. 게시되는 바이트가 같다. 1은 오류가 나는 순서만 바꾼다. 스키마 오류가 저장 값 오류보다 먼저 보고될 수 있다.
- 실익: 측정 기준(11MB)으로 저장 한 번에 약 1.7초와, 미변경 레코드 비율만큼의 약 2.2초가 줄어든다. 실제 인스턴스 크기에서는 측정하지 않았다.
- 위험과 보호: 부모 바이트 승계가 잘못되면 다른 바이트가 게시될 수 있다. 다음 시험이 덮는다.
  - `tests/test_performance_save.py`
    - `test_changed_state_writes_the_same_canonical_files_and_returns_reload_views`
    - `test_save_reads_parent_family_bytes_once_and_preserves_reload_equivalence`
    - `test_reused_parent_bytes_still_reject_a_damaged_previous_snapshot`
    - `test_regular_save_still_rejects_invalid_input`
- 확신: 중간. 측정은 합성 자료다. 부모 바이트는 검증된 읽기이거나 자기 게시 후보이므로 정규형이 보장된다(`repository.py:192-206`).
- 다른 영역: 없음. 직전 라운드(8d2ffd0)의 부모 생략 검증과 인접하지만, 대상이 검증이 아니라 인코딩이므로 새 항목이다.

#### STO-04: 통합 묶음 게시에서 같은 후보를 두 번 전체 검증한다

- 유형: 수신재검사중복
- 위치:
  - `do_math/integration.py:507-510`: `validate_candidate` 단계 뒤에 `publish` 단계가 온다.
  - `do_math/engine.py:2289-2299`: `_validate_bundle_candidate`가 `store.validate_candidate`를 부른다.
  - `do_math/engine.py:2353-2361`: `publish`가 `store.save_with_state`를 부른다.
  - `do_math/repository.py:276-288`: `save_with_state`가 `_validate_candidate`를 다시 부른다.
  - `do_math/engine.py:2292`: `validate_knowledge_records`를 부른다. `validate_semantics`(`record_schemas/__init__.py:248`)가 같은 검사를 다시 한다.
- 현상:
  - 같은 프로세스에서 같은 `candidate_instance`·`candidate_runtime`에 대해 `validate_candidate`가 한 번 돌고, 곧바로 `save_with_state`가 `_validate_candidate`를 다시 돈다. `validate_candidate`는 입력을 깊은 복사로 다루므로 값이 바뀌지 않는다(`repository.py:226-227`). 두 호출 사이에 다른 코드는 없다(`integration.py:508-510`).
  - `_validate_candidate`가 하는 일은 다음과 같다. 두 번 도는 것이 이 전부다.
    - 깊은 복사
    - `seal_large`
    - 저장 값 순회
    - 이벤트 번호 부여
    - `contract.validate`
    - 전 가족 인코딩
    - artifact 증거 대조
- 제안:
  - `validate_candidate`의 반환 dict에 검증 기준을 싣는다. 기준은 `expected_head`와 `self.contract.validation_generation`이다.
  - `ResearchRepository.save_validated(expected_head, candidate, artifacts=None)`를 둔다. 이 함수는 기준이 같으면 `_validate_candidate`를 건너뛰고 `save_with_state`의 나머지(변경 계산과 `publish`)만 수행한다.
  - `integration.apply_bundles`의 `publish`는 검증 단계가 돌려준 후보를 넘긴다. 단계 구분(`candidate`와 `publication`)과 `next_owner`는 그대로 유지된다.
  - 미리보기 경로(`engine.py:2427`)는 게시하지 않으므로 지금대로 둔다.
- 동작: 보존. 검증 실패는 지금처럼 `candidate` 단계에서 나고, 게시 실패는 `publication` 단계에서 난다.
- 실익: 묶음 게시 한 번에 후보 전체 검증 한 번(인코딩 포함)이 준다. 11MB 기준으로 STO-03의 측정값(순회 1.75초와 인코딩 2.2초)과 의미 검사 시간이 줄어든다. 추정이다.
- 위험과 보호: 후보를 만든 뒤 입력을 고치는 경로가 생기면 검증되지 않은 값이 게시된다. `save_validated`가 기준 head와 계약 세대를 대조하는 것으로 막는다. 이를 덮는 테스트는 `tests/test_impact_bundle.py`, `tests/test_redesign_EVIDENCE*.py`로 추정되며, 테스트명은 미확인이다.
- 확신: 중간. 호출 순서는 원문으로 확인했다. 묶음 게시 빈도는 측정하지 않았다.
- 다른 영역: `do_math/integration.py`, `do_math/engine.py`

#### STO-05: "이미 대조했는가 확인 후 대조" 패턴이 10곳에 복제돼 있다

- 유형: 이음새중복
- 위치:
  - `do_math/engine.py:1123-1138`(`_sealed_bytes`, 가장 일반적인 형태)
  - `do_math/context_store.py:307-314`, `:808-825`
  - `do_math/retention.py:167-168`, `:206-207`
  - `do_math/planning.py:487-499`
  - `do_math/review_cycle.py:310-313`
  - `do_math/review_engine.py:1191-1192`
  - `do_math/submission.py:73-79`
  - `do_math/payloads.py:117-125`
  - 정본: `do_math/repository.py:38-53`
  - 키를 따로 조립하는 곳: `do_math/planning.py:24-25`, `:488`
- 현상:
  - 계약 S3(`검사-경량화-이음새-계약.md` 3절)의 소비 규칙이 호출자마다 다시 구현돼 있다. 규칙은 "`artifact_verified`면 해시하지 않고, 아니면 `verify_artifact`"다.
  - 변종이 셋이다.
    - `git_dir is None` 분기가 있는 형태
    - 선언 크기 대신 `len(raw)`를 넘기는 형태(`planning.py:494`, `submission.py:76`)
    - 읽기를 늦추는 형태(`engine.py:1129-1132`)
  - `git_dir=None`으로 `verify_artifact`를 부르면(`context_store.py:311`, `retention.py:168`, `:207`) `VERIFIED_ARTIFACTS`에 `('None', path, sha)` 키가 들어간다. 지금은 `None`으로 조회하는 곳이 없어 무해하다. 그래도 전역 캐시를 오염시킨다.
  - `planning._VALID_ARTIFACTS`는 키 형식 `(str(git_dir), path, sha256)`을 `repository.py:39`에서 복제해 조립한다.
- 제안:
  - `engine._sealed_bytes`를 `repository.sealed_bytes(git_dir, path, sha256, size, read, *, raw=None, needed=True)`로 옮긴다. 위 호출자는 모두 이 함수를 부른다.
  - `verify_artifact`는 `git_dir is None`이면 표시하지 않는다.
  - 키 조립은 `repository.artifact_key(git_dir, path, sha256)` 하나로 두고, `planning`이 이를 쓴다.
- 동작: 보존.
- 실익: 코드가 약 40행 준다. S3 규칙을 고칠 때 고칠 곳이 10곳에서 1곳으로 준다. 크기 대조를 빠뜨리는 변종이 생길 여지도 없어진다.
- 위험과 보호: 크기 인자의 의미(선언 크기인지 실제 길이인지)를 호출자마다 보존해야 한다. `tests/test_performance_save.py`의 `test_save_rereads_only_new_artifact_evidence`가 덮는다. 나머지 호출자의 시험은 미확인이다.
- 확신: 높음. 전수는 `grep -rn "artifact_verified(\|verify_artifact(" do_math`로 확인했다.
- 다른 영역: `do_math/engine.py`, `do_math/planning.py`, `do_math/review_cycle.py`, `do_math/review_engine.py`, `do_math/submission.py`

#### STO-06: 재분석 지점 검사, OID 형태, SHA-256 형태, artifact 참조 형태를 모듈마다 따로 구현한다

- 유형: 이음새중복
- 위치:
  - 재분석 지점(reparse)
    - `do_math/git_store.py:498-509`(`_no_reparse`)
    - `do_math/repository.py:87`, `:624-639`(`_assert_no_reparse_ancestor`, `_is_reparse`)
    - `do_math/context_store.py:17`, `:37-42`, `:62-67`(`_is_reparse`, `_physical_root`)
    - `do_math/retention.py:20-29`(`_physical`)
  - OID 형태
    - `do_math/context_store.py:423`, `:733`
    - `do_math/retention.py:124-125`
    - 정본: `do_math/git_store.py:55-59`(`oid_shape`)
  - SHA-256 16진 형태
    - `do_math/state_checks.py:15`, `:20-21`
    - `do_math/payloads.py:109`
    - `do_math/repository.py:718`
    - `do_math/context_store.py:720`, `:752`
    - 영역 밖: `planning.py:298`, `task_contracts.py:93`, `observations.py:782`, `review_policy.py:107`, `codex_worker.py:61`, `formal.py:296`, `:310`, `launch.py:19`, `trust_validation.py:20`
  - artifact 참조
    - `do_math/retention.py:123-129`
    - 정본: `do_math/git_store.py:417-434`
- 현상:
  - "경로나 그 조상에 심볼릭 링크 또는 `FILE_ATTRIBUTE_REPARSE_POINT`(0x400)가 있으면 거부한다"는 같은 규칙이 4벌 있다.
  - OID 형태 검사는 `oid_shape`가 있는데도 2모듈 3곳이 문자 비교로 다시 쓴다.
  - `retention._archive_reference`의 경로 검사는 뒤이은 읽기(`read_artifact` → `repository.read` → `git_store.read_bytes`)가 `_validate_oid`와 `_validate_path`로 다시 수행한다. 사용자 경로 규칙인 Windows 예약어와 끝 점은 오히려 정본보다 약하다.
- 제안:
  - `git_store._no_reparse(path, below=None)`를 공개 이름 `no_reparse`로 바꾸고 나머지 셋이 이를 쓴다. `context_store`가 이미 `git_store`를 import하므로(`context_store.py:14`) 새 의존은 없다.
  - 스냅숏 형태는 `oid_shape`를 쓴다.
  - SHA-256 형태는 `file_io.is_sha256(value)` 하나로 모은다. 이 영역에서는 `state_checks`, `payloads`, `repository`, `context_store`가 이를 쓴다.
  - `_archive_reference`는 `runtime/artifacts/` 접두 확인만 남긴다.
- 동작: 보존. 네 구현의 판정은 같다. 차이는 `repository._is_reparse`가 `os.stat(follow_symlinks=False)`를 쓰는 것뿐이고, 결과는 같다.
- 실익: 약 35행이 준다. 경로 안전 규칙을 고칠 때 고칠 곳이 하나가 된다.
- 위험과 보호: `tests/test_git_store.py`의 다음 시험이 덮는다.
  - `test_repository_junction_is_rejected_before_resolve`
  - `test_physical_boundary_refuses_a_reparse_point_below_its_root`
  - `test_oid_shape_is_separate_from_instance_format`

  나머지 모듈의 reparse 시험은 미확인이다.
- 확신: 높음. 전수는 `grep -rn "st_file_attributes\|0x400\|_REPARSE_POINT" --include=*.py`와 `grep -rn "(40, 64)\|{40, 64}"`로 확인했다. `operator_bootstrap.py:31`은 설계상 `do_math`를 import하지 않으므로 제외했다(계약 2.1).
- 다른 영역: SHA 형태의 영역 밖 끝점은 위에 적었다.

#### STO-07: ID 형식 규칙(ULID 접두 ID, 레코드 ID 경로 안전성)이 생성기, 스키마, 계약, Git 경로 검사에 따로 있다

- 유형: 이음새중복
- 위치:
  - ULID 생성: `do_math/repository.py:84-100`(`new_id`, `_CROCKFORD`)
  - ULID 판정
    - `do_math/git_store.py:46`(`RI-`)
    - `do_math/knowledge_io.py:257`(`KN-`), `:381`(`RL-`)
    - `do_math/submission.py:163`(`KN-` 스키마)
  - 레코드 ID
    - `do_math/record_schemas/schemas.py:10`(`ID`: `^[A-Za-z0-9][A-Za-z0-9_.-]*$`)
    - `do_math/state_contract.py:172`(`[A-Za-z0-9][A-Za-z0-9_.:-]*`, 콜론 허용)
    - `do_math/git_store.py:417-432`(`:`, 예약 장치명, 끝 점을 거부)
    - 경로 조립: `do_math/repository.py:651-652`
- 현상:
  - ULID 알파벳과 길이는 생성기에 한 번, 판정 정규식에 네 번 적혀 있다.
  - 레코드 ID 규칙은 세 표현이 서로 다르다.
    - 계약 정규식은 `:`를 허용한다.
    - 스키마 `ID`는 `:`를 거부한다.
    - 게시 때 경로 검사는 `:`, `CON` 같은 예약 장치명, 끝 공백·점을 거부한다.
  - 설치 가족은 모두 `record()`로 `id: ID`를 가지므로 계약 정규식은 결코 먼저 거부하지 못한다. 외부 등록 가족은 `:` ID를 통과시켰다가 게시에서 늦게 실패한다. `CON` 같은 ID는 스키마와 계약을 모두 통과하고 `research/<family>/CON.json` 게시에서 실패한다.
- 제안:
  - `repository.py`의 `new_id` 옆에 `new_id_pattern(prefix)`(또는 `is_new_id(prefix, value)`)를 둔다. `git_store`, `knowledge_io`, `submission`이 이를 쓴다. `git_store`는 `repository`를 import하지 않으므로, 상수는 `git_store`에 두고 `repository`가 가져오는 방향이 순환이 없다.
  - 레코드 ID 규칙은 `state_contract.RECORD_ID`(정규식 하나)로 정한다. `schemas.ID`는 그 패턴을 쓴다. 계약 검사(`state_contract.py:172`)도 그 패턴을 쓰되, 예약 장치명 확인은 `git_store` 경로 규칙 함수를 재사용한다.
- 동작: 보존. 설치 가족에서는 판정이 같다. 외부 등록 가족의 `:` ID가 저장 전에 거부되는 것은 실패 시점이 앞당겨지는 것뿐이다.
- 실익: 형식 규칙의 정본이 하나가 된다. 늦은 게시 실패 경로가 사라진다. 행 수는 소폭 준다.
- 위험과 보호: `tests/test_git_store.py`의 `test_only_registry_instance_ids_are_accepted_before_ref_use`, `test_invalid_and_case_colliding_paths_are_rejected`가 덮는다.
- 확신: 중간. ID 규칙 차이는 원문으로 확인했다. 외부 등록 가족의 실제 사용처는 미확인이다.
- 다른 영역: `do_math/knowledge_io.py`, `do_math/submission.py`

#### STO-08: 역할 입력을 한 커밋 안에서 두 번들에 이중으로 보관하고, 문맥 값을 다시 직렬화한다

- 유형: 파생상태
- 위치:
  - `do_math/engine.py:842-865`(`_input_artifacts`): `runtime/artifacts/{BA 번들}/...`
  - `do_math/engine.py:3369`: `artifact_prefix=f"runtime/artifacts/{execution_id}"`
  - `do_math/context_store.py:692-708`: `{EX 실행 ID}/input/catalog/*.json`, `/input/documents/{i}.txt`, `/input/prompt.txt`
  - `do_math/context_store.py:871`, `:907`: 이미 `catalog_files`가 있다.
- 현상:
  - `prepare_role_input`은 `artifact_prefix`가 있으면 모든 문맥 키의 카탈로그 바이트, 문서, 프롬프트를 `{EX}` 번들 artifact로 만든다. `engine._input_artifacts`는 같은 카탈로그 바이트(`fitted["catalog_files"]`), 문서(`input/implementation/...`), 프롬프트(`input.txt`)를 `{BA}` 번들에도 넣는다. 둘은 `artifacts.update(fitted["artifacts"])`(`engine.py:864`)로 한 저장에 함께 게시된다.
  - 소비자도 갈라져 있다.
    - `{EX}` 쪽은 `verify_manifest_artifacts`가 읽는다(manifest의 `artifact_ref`).
    - `{BA}` 쪽은 `check`(`engine.py:4788`)와 재시도 검사(`engine.py:4421-4428`)가 읽는다.
  - 또 `context_store.py:699`, `:703`은 `canonical_json(value[key])`를 다시 계산한다. `fit_context`가 같은 바이트를 `catalog_files`로 이미 돌려준 상태다.
- 제안:
  1. 동작 보존 부분: `context_store.py:699`, `:703`에서 `fitted["catalog_files"]["input/catalog/<key>.json"]`을 재사용한다.
  2. 동작 변경 부분: `prepare_role_input`의 `artifact_prefix`로 `{BA}` 기준 경로를 받는다. 이름은 한 벌로 맞춘다. 예를 들어 `input/prompt.txt`와 `input.txt`, `input/documents/{i}.txt`와 `input/implementation/{path}`를 하나로 통일한다. 이렇게 하면 manifest의 `artifact_ref`와 `engine`의 경로 조립이 같은 파일을 가리킨다.
- 동작: 변경. 새 실행의 artifact 경로가 바뀐다. 기존 기록의 참조는 그대로 유효하다.
- 실익:
  - 게시 한 번에 입력 바이트(프롬프트, 문서, 전체 문맥 카탈로그)의 임시 파일 쓰기와 `hash-object` 입력이 절반으로 준다. Git blob은 내용 주소라 저장 용량은 원래 중복되지 않는다.
  - 트리 항목이 준다.
  - "어느 사본이 정본인가"라는 경계가 사라진다.
  - 1은 전체 문맥의 재직렬화 한 번을 줄인다. 크기에 비례하며, 추정이다.
- 위험과 보호: 경로 문자열을 기대하는 시험이 깨질 수 있다. 입력 manifest 경로는 `tests/test_formal_input_manifest.py`, `tests/test_context_store.py`가 덮는 것으로 추정한다(테스트명 미확인).
- 확신: 중간. 두 번들 게시는 원문으로 확인했다. 두 사본의 바이트가 같다는 것은 코드로 추론했으며, 실측하지 않았다.
- 다른 영역: `do_math/engine.py`

#### STO-09: 한 스냅숏 경로의 Git 프로세스 수를 줄일 수 있다

- 유형: 운영비용
- 위치:
  - `do_math/git_store.py:95-117`(`read_snapshot`): `rev-parse`와 `cat-file --batch-check` 2회
  - `do_math/git_store.py:225`, `:251`(`_subtree_oids`)
  - `do_math/git_store.py:86-88`(초기화 `rev-parse` 2회)
  - `do_math/git_store.py:207-208`: 잠금 밖 precheck `_head()`가 2회다. `do_math/repository.py:282-284`가 이미 같은 precheck를 했다.
- 현상:
  - 실측: 이 기계에서 `git` 한 번 생성에 평균 36.3ms가 든다(6절).
  - 생산 코드는 `read_snapshot()`의 `.head`만 쓴다(`repository.py:137`, `:282`, `:523`). `research_tree`와 `runtime_tree`는 시험 두 곳에서만 읽는다(`tests/test_git_store.py:164`, `tests/test_redesign_STORAGE.py:769`).
  - 그런데도 게시마다 `_subtree_oids`를 한 번 더 부른다(총 7회 중 1회).
  - `GitStateStore` 생성마다 `rev-parse`를 두 번 부른다. `git rev-parse --absolute-git-dir --show-object-format`는 한 번에 두 줄을 준다(6절에서 확인).
  - `cat-file --batch-check`에 ref 이름을 직접 넣으면 OID와 형식을 한 번에 얻는다. 같은 호출로 `ref:research`와 `ref:runtime`도 얻을 수 있다(6절에서 확인).
- 제안:
  - `read_snapshot`은 `ref`, `ref:research`, `ref:runtime` 세 줄을 한 번의 `batch-check`로 묻는다. 첫 줄이 `missing`일 때만 지금의 `rev-parse --verify --quiet`로 "부재"와 "손상"을 가른다.
  - 게시의 `_subtree_oids`는 지운다. `StateSnapshot`의 트리 필드는 필요할 때만 계산하거나, 시험과 함께 없앤다.
  - 초기화는 `rev-parse` 한 번으로 한다.
  - 잠금 밖 저장에서 `publish`의 `_head()` precheck는 `save_with_state`가 방금 같은 비교를 했으므로 인자로 생략한다. 최종 CAS가 권위이므로 안전은 그대로다.
- 동작: 보존. 부재와 손상의 구분은 대체 경로로 유지된다(`tests/test_git_store.py`의 `test_non_commit_or_corrupt_existing_ref_is_not_treated_as_absent`).
- 실익: 측정된 36ms를 기준으로 추정하면 다음과 같다.
  - 현재 head 해석마다 약 36ms
  - 게시마다 약 36ms(7회 → 6회)
  - 저장소 객체 생성마다 약 36ms
  - 잠금 밖 저장마다 약 72ms
- 위험과 보호: `tests/test_git_store.py`의 다음 시험이 덮는다. `research_tree`를 없애면 이 중 뒤의 두 시험도 고쳐야 한다.
  - `test_non_commit_or_corrupt_existing_ref_is_not_treated_as_absent`
  - `test_own_publication_lists_the_new_tree_without_enumerating_it`
  - `test_runtime_only_update_preserves_research_tree_and_old_snapshot_bytes`
  - `tests/test_redesign_STORAGE.py:769`
- 확신: 높음. 호출 수와 생성 시간은 실측했다. 대체 명령의 출력도 실측했다.
- 다른 영역: 없음

#### STO-10: 일괄 읽기가 한 경로 부재로 전부 실패해, 호출자 셋이 경로별 재시도를 따로 구현한다

- 유형: 복잡성
- 위치:
  - 정본: `do_math/git_store.py:125-169`(`read_many`, `blob_sizes`)
  - 호출자
    - `do_math/state_checks.py:167-179`(`_artifact_sizes`)
    - `do_math/context_store.py:766-782`(`prefetch_artifacts`)
    - `do_math/engine.py:4766-4775`(`_inspect_before_write`)
- 현상:
  - `cat-file --batch`와 `--batch-check`는 없는 경로를 줄마다 `<name> missing`으로 알린다. 그런데 `read_many`와 `blob_sizes`는 이를 배치 전체의 예외로 바꾼다(`git_store.py:139-140`, `:166-167`).
  - 그래서 호출자마다 "배치 실패 → 경로별로 다시 부르기"를 구현한다. 실패 경로에서는 경로 하나당 Git 프로세스가 하나씩 더 뜬다.
- 제안:
  - `blob_sizes`와 `read_many`에 `missing="raise"|"omit"` 인자를 둔다. `omit`이면 없는 경로를 결과에서 빼고 돌려준다.
  - 세 호출자는 결과에 없는 경로를 결함으로 기록한다. 재시도 루프는 지운다.
- 동작: 보존. 결함이 보고되는 대상과 사유가 같다.
- 실익: 약 30행이 준다. 실패 경로에서 경로 수만큼의 Git 생성(각 약 36ms)이 1회로 준다.
- 위험과 보호: `tests/test_reporting.py`의 `test_status_reports_artifact_presence_and_length_in_one_batch_without_bytes`와 `tests/test_git_store.py`의 `test_batch_read_is_exact_and_missing_blob_is_an_error`가 덮는다.
- 확신: 높음.
- 다른 영역: `do_math/engine.py`

#### STO-11: 설정 필드 어휘를 저장 스키마, 제어 입력 형태, 엔진 검증이 각자 나열한다

- 유형: 이음새중복
- 위치:
  - 저장 스키마: `do_math/record_schemas/__init__.py:163-181`
  - 제어 입력 형태: `do_math/control_contracts.py:65-77`(`CONFIG_PATCH`)
  - 엔진 검증: `do_math/engine.py:89`(`DEFAULT_CONFIG`), `:133`(`OPTIONAL_CONFIG`), `:163-186`(`validate_config`)
- 현상:
  - 같은 설정 키 약 30개와 그 불리언·정수·사전 분류를 세 모듈이 손으로 나열한다.
  - 실측으로 저장 스키마와 `CONFIG_PATCH`의 키 집합이 같은 것을 확인했다(6절). 타입은 의도적으로 다르다. 입력 형태는 느슨하다.
  - 참고로 `control_contracts.GRANT`에는 `resource_limits`가 있지만, 저장 스키마 `grants`(`schemas.py:161-167`, `domains.py:242`, `:284-288`)에는 없다. 제어 입력은 통과하지만 저장에서 거부될 수 있는 모양이다. 실제 경로는 미확인이다.
- 제안:
  - 키 목록과 분류의 정본을 저장 스키마 하나로 둔다. `control_contracts`는 이미 `record_schemas.schemas`를 import하므로 `CONFIG_PATCH`의 키를 `RESEARCH` 설정 스키마에서 파생한다. 방법은 키마다 타입만 느슨하게 하는 것이다.
  - `engine.validate_config`의 불리언 목록(`engine.py:175-177`)과 정수 목록(`:182-186`)은 스키마가 이미 보증하므로 지운다. 범위 검사 같은 도메인 조건만 남긴다.
- 동작: 보존.
- 실익: 새 설정 키를 추가할 때 고칠 곳이 3곳에서 1곳으로 준다. 한쪽만 고쳐 제어 입력 단계를 통과하고 저장에서 실패하는 경로가 사라진다.
- 위험과 보호: `tests/test_control_shapes.py`와 `tests/test_redesign_CONTRACTS.py`가 덮는 것으로 추정한다(테스트명 미확인).
- 확신: 중간. 키 집합이 같은 것은 실측했다. `validate_config`의 전체 본문은 읽지 않았다.
- 다른 영역: `do_math/control_contracts.py`, `do_math/engine.py`

#### STO-12: 파생 가족 형태(`derived`)와 `task_readiness` 가족은 생산 경로에서 쓰이지 않는다

- 유형: 죽은코드
- 위치:
  - `do_math/record_schemas/__init__.py:72-74`, `:161-162`
  - `do_math/state_contract.py:36`, `:60`, `:64-65`, `:137-140`
  - `do_math/repository.py:256-261`, `:672-674`, `:707`, `:759-763`, `:791-792`
- 현상:
  - 파생 가족은 상태에 `runtime["task_readiness"]`가 있을 때만 활성화된다. 인코딩은 상태에 있는 키만 manifest에 적고(`repository.py:666`), 복원은 manifest에 선언된 것만 계산한다.
  - 생산 코드 어디에도 `runtime["task_readiness"]`를 두는 곳이 없다. 엔진은 메모리의 `self._task_readiness`(`engine.py:597`, `lifecycle_engine.py:888-891`)를 쓴다. 시험은 적재 결과에 이 키가 없음을 단언한다(`tests/test_efficiency.py:332`, `tests/test_lifecycle_engine.py:300`, `:386`).
  - 활성화되더라도 계산이 두 번 돈다. 한 번은 `_validate_candidate`의 갱신(`repository.py:261`)이고, 한 번은 `validate`의 비교(`state_contract.py:138`)다. 갱신 직후의 비교이므로 항상 참이다.
  - 전수 확인에 쓴 검색식: `grep -rn "task_readiness" --include=*.py --include=*.md`
- 제안: `derived` 형태, `task_readiness` 가족, 관련 분기를 지운다. 문서 `계약/연구-계획.md:24`와 `계약/연구-수행.md:17`의 `task_readiness`는 역할 입력 문맥 키(`engine.py:1881`)이므로 영향이 없다.
- 동작: 변경. `runtime["task_readiness"]`를 넣은 상태는 미등록 가족으로 거부된다. 생산 경로에는 그런 상태가 없다.
- 실익: 약 20행과 가족 형태 하나가 준다. 형태별 분기(인코딩, 복원, 검증)가 하나씩 준다.
- 위험과 보호: `tests/test_redesign_STORAGE.py:571-574`와 `tests/test_lifecycle_engine.py:600`은 이 키를 직접 넣으므로 고쳐야 한다. 과거 판본이 manifest에 `derived` 컨테이너를 적은 저장소가 있는지는 미확인이다. 현재 코드로는 생길 수 없다.
- 확신: 중간. 생산 경로의 부재는 grep 전수로 확인했다. 과거 저장소는 확인할 수 없다.
- 다른 영역: `do_math/lifecycle_engine.py`, `do_math/scheduler.py`(`task_readiness`는 대기 사유 문자열로만 쓰인다)

#### STO-13: 이벤트 가족의 맵 형식과 `EventPublisher.prepare`는 생산 경로에서 쓰이지 않는다

- 유형: 불필요기능
- 위치:
  - `do_math/events.py:5-13`(맵 분기), `:17-22`(`prepare`)
  - `do_math/repository.py:679-681`, `:750`
  - `do_math/state_contract.py:60`, `:145-147`, `:155-156`
  - `do_math/record_schemas/__init__.py:141`(`shape="events"`)
- 현상:
  - 생산 코드는 `runtime["events"]`를 항상 목록으로 만든다(`initialization.py:261`, `planning.py:740`, `:830`, `engine.py:2481`, `events.py:43`). 맵 형식은 `tests/test_redesign_STORAGE.py:656`, `:669`에만 있다.
  - `EventPublisher.prepare`는 시험에서만 부른다(`tests/test_performance_repairs.py:258`, `tests/test_redesign_STORAGE.py:654-703`).
  - 이 결과 `events` 형태는 "목록 + 맵 허용"이다. 저장소, 계약, 이벤트 모듈 세 곳이 이 분기를 가진다.
- 제안:
  - `events`를 `list` 형태로 등록한다. 번호 부여와 불변 검사(`assign_sequences_in_place`)는 그대로 둔다.
  - `event_rows`의 맵 분기와 `prepare`를 지운다. 시험은 `assign_sequences_in_place`를 복사본에 적용하는 형태로 바꾼다.
- 동작: 변경. 맵 형식 이벤트 상태는 거부된다. 생산 경로에는 없다.
- 실익: 약 15행과 형태 하나가 준다.
- 위험과 보호: `tests/test_redesign_STORAGE.py`(`EventPublisher.prepare` 사용 시험들)와 `tests/test_performance_repairs.py`를 고쳐야 한다. 과거 저장소의 맵 이벤트는 미확인이다.
- 확신: 중간.
- 다른 영역: 없음

#### STO-14: 이벤트 순번 연속성 규칙이 두 곳에 있고, 부모 이벤트를 두 번 검사한다

- 유형: 이음새중복
- 위치:
  - `do_math/repository.py:796-803`(`_validate_published_events`)
  - `do_math/events.py:33-40`(부모 순번 검사), `:75-81`(결과 순번 검사)
  - 호출: `do_math/repository.py:186`, `:240-242`
- 현상:
  - "번호는 1..n 연속, `event_cursor == n`"을 읽기 쪽과 쓰기 쪽이 서로 다른 코드로 표현한다.
  - 쓰기 쪽의 부모 이벤트는 항상 `_read_documents`가 막 검증한 부모에서 온다(`repository.py:238-241`). 그래서 `events.py:33-40`은 같은 프로세스에서 같은 값을 다시 검사한다.
- 제안:
  - `events.check_sequence(rows, cursor)` 하나를 두고, `repository._validate_published_events`와 `assign_sequences_in_place`의 결과 검사가 이를 쓴다.
  - 부모 재검사(`events.py:33-40`)는 지운다. 부모 번호는 이미 검증된 사실로 받는다.
- 동작: 보존.
- 실익: 약 10행이 준다. 규칙의 정본이 하나가 된다.
- 위험과 보호: `tests/test_redesign_STORAGE.py:654-703`의 이벤트 시험이 덮는다. 이 시험은 `prepare`에 임의의 부모를 넘기므로, 부모 검사를 지우면 시험 일부가 바뀐다.
- 확신: 중간.
- 다른 영역: 없음

#### STO-15: 레코드 스키마가 두 파일에 나뉘어 정의되고 뒤에서 덮어쓰인다

- 유형: 복잡성
- 위치:
  - `do_math/record_schemas/schemas.py:46-248`(기본 정의)
  - `do_math/record_schemas/domains.py:13-497`(`extend()`로 제자리 변형), `:500`(import 부수효과로 실행)
  - `do_math/record_schemas/__init__.py:2-3`
- 현상:
  - `executions` 스키마 하나의 `properties`가 `schemas.py:101-118`과 `domains.py:39`, `:70`, `:176-178`, `:268-271`, `:327-359`, `:377`, `:388`, `:465`, `:496`에 흩어져 있다.
  - 뒤에서 앞을 덮어쓰는 곳은 다음과 같다.
    - `grants.status`: `schemas.py:161`을 `domains.py:284`가 덮는다.
    - `executions.action`: `schemas.py:105`의 `EVIDENCE`를 `domains.py:496`의 action 스키마가 덮는다.
    - `decisions.anyOf[1].required`: `domains.py:50`을 `domains.py:249`가 덮는다.
    - `tasks.profile_refs`: `schemas.py:129`를 `domains.py:155`가 같은 값으로 다시 정의한다.
  - 기타
    - `domains.py`는 `deepcopy`를 두 번 import한다(`:112`, `:144`).
    - `schemas.py:6`의 `deepcopy`는 이 파일에서 쓰이지 않고, `import *`로 새어 나간다.
  - 최종 스키마를 알려면 두 파일을 순서대로 실행해 봐야 한다.
- 제안:
  - 가족마다 최종 스키마를 한 번에 정의한다. `domains.extend()`의 내용을 각 `RECORDS[...]` 정의에 합친다.
  - 합친 뒤 `default_state_contract().manifest()['sha256']`가 변하지 않음을 확인한다. `json_digest`는 키 순서와 무관하므로 같은 스키마면 같은 값이 나온다.
- 동작: 보존.
- 실익: 스키마를 읽고 고치는 비용이 준다. 덮어쓰기 순서 때문에 생기는 오류 여지도 사라진다. 행 수는 거의 같다.
- 위험과 보호: manifest 다이제스트 동일성이 기계적인 완전 보호다. `tests/test_redesign_STORAGE.py`, `tests/test_redesign_CONTRACTS.py`도 덮는다.
- 확신: 높음.
- 다른 영역: `do_math/control_contracts.py`(`RECORDS`를 가져다 쓴다)

#### STO-16: `resolve_profile`이 같은 이름, 같은 계약으로 두 벌 있다

- 유형: 이음새중복
- 위치:
  - `do_math/record_schemas/__init__.py:194-206`: 재해시하지 않고, 복사하지 않는다.
  - `do_math/execution_profiles.py:246-252`: `profile_ref` → `validate_profile`(재해시) + `deepcopy`
  - 호출자 20여 곳: `grep -rn "resolve_profile" do_math`
- 현상: 두 함수 모두 "ID·판본·sha256이 정확히 같은 프로필을 찾는다"는 같은 계약을 구현한다. 참조 형태 검사(`set(reference) != {"id","revision","sha256"}`)와 오류 문구가 복제돼 있다. 생산 호출자는 모두 재해시하는 쪽을 쓴다. 저장된 프로필은 적재·저장 때 가족 검증기(`validate_profile`)로 이미 검증된다.
- 제안:
  - `execution_profiles.match_profile_ref(profiles, reference)`를 정본으로 둔다. 이 함수는 형태를 확인하고 필드를 비교하며, 재해시하지 않고 복사하지 않는다.
  - `record_schemas`의 사본은 지우고 이 함수를 쓴다.
  - `execution_profiles.resolve_profile`은 `deepcopy(match_profile_ref(...))`로 두고, 재해시는 저장되지 않은 프로필을 다루는 호출자만 명시적으로 한다.
- 동작: 보존. 재해시를 유지하는 선택이면 보존이다. 재해시를 기본에서 빼면 메모리의 변조 프로필이 저장 때 검출되므로 검출 시점이 바뀐다.
- 실익: 중복 함수 하나가 줄어든다. 재해시를 뺄 경우에는 호출마다 프로필 해시 한 번이 준다(추정, 측정 안 함).
- 위험과 보호: `tests/test_redesign_PROFILES.py`가 덮는 것으로 추정한다(테스트명 미확인).
- 확신: 중간.
- 다른 영역: `do_math/execution_profiles.py`와 호출자들

#### STO-17: 정리(cleanup)가 후보마다 같은 head의 보존 상태를 처음부터 다시 만든다

- 유형: 운영비용
- 위치:
  - `do_math/engine.py:4197-4227`(`_retention_state`)
  - `do_math/engine.py:4292`(`current_state=lambda: self._retention_state(action)`)
  - `do_math/retention.py:226-242`(`cleanup`이 후보마다 `current_state()`를 호출)
  - `do_math/retention.py:53-63`, `:147-148`(`_references_run`)
- 현상:
  - `cleanup`은 적격 후보마다 `current_state()`를 부른다. `_retention_state`는 매번 다음을 한다.
    - `load_records()`(상태 전체와 서술자 깊은 복사)
    - 모든 레코드의 참조 재귀 수집
  - 쓰기 잠금 아래이고 `head != self.head`면 예외를 내므로(`engine.py:4199-4200`), 호출마다 입력 head가 같다. 결과가 같다는 뜻이다.
  - 또 `_references_run`은 실행마다 보호 경로 전부를 `_physical`(조상 전체 `lstat`)로 다시 해석한다.
- 제안:
  - `_retention_state` 결과를 `(self.head, action id)`로 메모이즈한다. 계약 S4의 head 키 메모이즈에 해당한다.
  - 보호 경로의 물리 해석은 `cleanup_candidates` 진입 때 한 번만 한다.
- 동작: 보존. 메모이즈는 보존이다. 물리 해석을 끌어올리면, 해석 불가 경로가 있을 때 모든 실행이 거부된다. 지금은 앞선 경로에서 일치해 조기 반환한 실행은 통과할 수 있다. 결과가 더 보수적이 될 뿐이다.
- 실익: 적격 후보 k개일 때 전체 상태 복사와 참조 수집이 k+1회에서 1회로 준다. `lstat` 호출은 (실행 수 × 경로 수 × 깊이)에서 (경로 수 × 깊이)로 준다. 추정이다.
- 위험과 보호: `tests/test_redesign_ENGINE.py`나 정리 관련 시험이 덮을 것으로 추정한다(테스트명 미확인).
- 확신: 중간.
- 다른 영역: `do_math/engine.py`

#### STO-18: 보존 참조 필드 어휘가 엔진과 정리 모듈에 따로 있다

- 유형: 이음새중복
- 위치:
  - `do_math/engine.py:4202-4204`(`reference_keys`, 19개)
  - `do_math/retention.py:81`(`reference_closure`의 7개 키)
- 현상:
  - 엔진은 19개 키로 각 레코드의 `references`를 만든다. `retention.reference_closure`는 `references`에 더해 자기 7개 키(`dependencies`, `source_refs`, `input_refs`, `artifact_ref`, `path`, `checkpoint_ref`)를 다시 읽는다.
  - 두 목록이 다르다. `checkpoint_ref`는 정리 쪽에만 있고, `origin_refs`, `evidence_refs`, `record_refs` 등은 엔진 쪽에만 있다.
  - 한 개념("정리로부터 보호해야 하는 참조 필드")을 두 곳이 반씩 안다.
- 제안:
  - 어휘를 `retention.PROTECTED_REFERENCE_KEYS` 하나로 둔다. 참조 수집 함수(엔진의 `references` 재귀)도 `retention`으로 옮긴다.
  - 엔진은 레코드만 넘긴다.
- 동작: 변경. 합집합을 쓰면 보호 대상이 조금 늘어난다(더 보수적). 교집합이 되면 보호가 줄어드므로 택하지 않는다.
- 실익: 정리 안전 규칙의 정본이 하나가 된다. 약 20행이 이동하거나 준다.
- 위험과 보호: 보호 누락은 되돌릴 수 없는 삭제로 이어진다. 정리 시험은 미확인이다.
- 확신: 중간.
- 다른 영역: `do_math/engine.py`

#### STO-19: 레코드 서술자를 즉시 복사·해시하고, 레코드 하나를 읽을 때도 상태 전체를 복사한다

- 유형: 운영비용
- 위치:
  - `do_math/repository.py:741-743`, `:784-787`: 서술자마다 `hashlib.sha256(raw)`와 `deepcopy(row)`를 한다.
  - `do_math/repository.py:147-156`(`_documents`의 전체 `deepcopy`)
  - `do_math/repository.py:365-381`(`load_records`, `records`, `read_record`)
- 현상:
  - 외부 head를 처음 읽을 때(`_read_documents`) 모든 레코드의 서술자를 만든다. 서술자에는 레코드의 깊은 복사와 파일 해시가 들어간다.
  - 서술자를 쓰는 곳은 `load_records`와 그 파생뿐이다. 이들은 반환 전에 어차피 전체를 다시 `deepcopy`한다(`:156`). 자기 게시 항목은 이미 서술자를 필요할 때 만든다(`:149-155`).
  - `read_record(id)`는 레코드 하나를 찾기 위해 인스턴스, 런타임, 모든 서술자를 깊은 복사한다.
  - 실측: 11.3MB 합성 상태의 `deepcopy`에 0.286초가 걸렸다.
- 제안:
  - `_decode_families`는 서술자를 만들지 않는다. 필요하면 `_documents`가 자기 게시 경로와 같은 방식으로 재구성한다.
  - 캐시 항목은 호출자에게 복사로만 나가므로 서술자 안의 `deepcopy(row)`는 지운다.
  - `records`와 `read_record`는 걸러낸 행만 복사한다.
- 동작: 보존.
- 실익: 첫 읽기마다 상태 크기만큼의 복사(11MB에서 약 0.29초)와 파일 해시가 준다. `read_record`마다 전체 복사가 준다. 측정값과 추정값이 섞여 있다.
- 위험과 보호: `tests/test_query_records.py`, `tests/test_redesign_STORAGE.py`(`read_record`와 `records` 시험들)가 덮는다.
- 확신: 중간.
- 다른 영역: 없음

#### STO-20: 엔진의 무변경 판정 서명은 저장소가 이미 캐시한 게시 상태의 두 번째 사본이다

- 유형: 파생상태
- 위치:
  - `do_math/engine.py:867-876`(`_state_signature`)
  - `_saved_state` 갱신 지점: `do_math/engine.py:598`, `:896`, `:908`, `:1531`, `:1540`, `:1622`, `:2376`, `:2557`, `do_math/scheduler.py:123`
  - `do_math/repository.py:56-77`, `:305`(`_VALIDATED_READS`, `_remember_published`)
- 현상:
  - `_save`는 상태 전체를 압축 JSON으로 직렬화한 문자열을 들고 있다가 다음 저장 때 비교한다. 이 문자열은 head가 움직이는 모든 지점(9곳)에서 다시 만들어야 한다.
  - 게시된 상태 자체는 저장소가 `(git_dir, head, contract)` 키로 이미 캐시한다.
  - 실측(11.3MB 합성 상태)
    - `json.dumps(indent=2)`: 0.658초. 압축 형식은 이보다 작을 것이다.
    - dict 동등 비교: 0.006초
- 제안:
  - `ResearchRepository.published_state(head)`로 캐시된 (instance, runtime)을 복사 없이 비교용으로 노출한다. `_save`는 `self.instance == cached_instance`와 `updated_at`을 제외한 runtime 동등성으로 무변경을 판정한다.
  - 캐시가 밀려났으면(LRU 4) 지금처럼 저장을 진행한다. 저장소의 `publish`가 변경 없음을 no-op로 처리하므로 정합성이 유지된다.
  - `_saved_state` 필드와 9개 갱신 지점을 지운다.
- 동작: 보존. 봉인 payload와 같은 값의 비봉인 값은 지금은 "변경"으로, 제안 후에는 "무변경"으로 판정된다. 어느 쪽이든 게시 결과는 no-op다.
- 실익: 저장 시도마다 전체 직렬화 두 번(판정과 갱신)이 동등 비교 한 번으로 준다. 측정 기준 약 0.6초 × 2에서 0.006초로 준다. 동기화 지점 9곳이 사라진다.
- 위험과 보호: `tests/test_performance_save.py`의 `test_unchanged_state_is_noop_and_returns_normalized_reload_views`가 덮는다.
- 확신: 낮음. 직전 라운드(R12)가 변경 세대 카운터 대신 서명을 택했다(`engine.py:868-871`의 주석). 이 제안은 서명을 저장소 캐시와의 이음새로 바꾸는 것이므로 새 항목으로 적는다. 통합자는 R12와의 관계를 판단해야 한다.
- 다른 영역: `do_math/engine.py`, `do_math/scheduler.py`

#### STO-21: OS 파일 잠금 구현이 세 모듈에 있다

- 유형: 이음새중복
- 위치:
  - `do_math/git_store.py:269-300`(`writer_lock`, 비차단)
  - `do_math/engine.py:273-300`(`_control_acceptance_lock`, `msvcrt.LK_LOCK`)
  - `do_math/session_slots.py:14-29`(`_lock`, 비차단)
- 현상:
  - "1바이트 파일을 만들고 `msvcrt.locking` 또는 `fcntl.flock`으로 잠근다"는 같은 절차가 세 번 구현돼 있다.
  - `engine`의 `LK_LOCK`은 Windows에서 1초 간격 10회 재시도 뒤 `OSError`를 낸다. POSIX 쪽 `LOCK_EX`는 무한 대기다. 같은 함수가 플랫폼마다 의미가 다르다.
- 제안: `file_io.os_lock(path, *, blocking)` 컨텍스트 관리자 하나를 두고 세 곳이 쓴다. 차단 의미(재시도 한도)는 인자로 명시한다.
- 동작: 보존.
- 실익: 약 30행이 준다. 잠금 해제 누락 같은 오류 여지가 한 곳으로 모인다.
- 위험과 보호: `tests/test_git_store.py`의 `test_writer_lock_is_an_os_lock_without_stale_pid_contents`와 `test_writer_lock_leaves_the_final_cas_as_the_only_ref_comparison`가 덮는다. 나머지 두 곳의 시험은 미확인이다.
- 확신: 중간.
- 다른 영역: `do_math/engine.py`, `do_math/session_slots.py`

#### STO-22: 의도 해석의 입력 소비자 payload 계약은 산문뿐이고, 생산자 자기 확인 도구가 수신 검사와 다른 코드로 일부만 검사한다

- 유형: 생산자자기확인부재
- 위치:
  - 산문 계약: `C:/math/.claude/skills/do-math/references/입력-소비자.md:9-54`
  - 저장 스키마: `do_math/record_schemas/domains.py:18-27`(governance `content`)
  - 수신 검사
    - `do_math/governance.py:48-86`(`validate_governance_record`)
    - `do_math/governance.py:848-897`(`validate_import_units`)
    - `do_math/control_contracts.py:46-54`, `:118-119`(`validate_decision_shape`)
  - 생산자 검사: `do_math/submission.py:414-440`(`_intent_import_issues`)
  - 출력 스키마: `do_math/governance.py:1149-1152`(`payload: {"type":"object"}`)
- 현상:
  - `intent_interpretation` 역할(AI 생산자)은 payload 형태를 산문 문서로만 받는다. 문서에는 예를 들어 헌장 `content`의 필드, `decision_authority="user"`, 성공 기준과 포함 범위가 비어 있으면 안 된다는 조건이 적혀 있다(`입력-소비자.md:15`).
  - 같은 조건이 두 곳에 더 있다.
    - `governance.validate_governance_record`(`governance.py:60-64`)가 코드로 검사한다.
    - 저장 스키마(`domains.py:18-22`)는 더 약하게 표현한다. `decision_authority`는 `TEXT`이고 `minItems`가 없다.
  - 생산자가 제출 전에 실행하는 검사(`submission.py:414-440`)는 다음 셋을 `validate_import_units`(`governance.py:862-876`)와 다른 코드로 다시 구현한다. payload 내용은 검사하지 않는다.
    - 구간 전수 덮기
    - 단위 ID 중복
    - 질문 참조
  - 그래서 payload 결함은 수신 검사(`prepare_import`, `governance.py:945`)나 적용 시점(`governance.py:97`, `:169`, `:298`)에야 드러나 반려·재작업 비용이 된다.
- 제안:
  - `submission`의 의도 해석 검사가 `governance.validate_import_units`를 직접 부른다(문맥의 instance와 runtime 보기로). payload 내용에는 소유자별 검증을 붙인다. 예를 들어 `validate_governance_record`를 `payload["record"]`에 적용한다.
  - 문서는 "형태는 이 검사가 정본"이라고 가리키고, 필드 나열은 줄인다.
  - 저장 스키마 `content`는 검증 함수와 같은 강도로 맞추거나, 검증 함수에 맡기고 `EVIDENCE`로 둔다.
- 동작: 변경. 생산자가 제출 전에 더 많은 결함을 발견한다. 수신 판정은 같다.
- 실익: 의도 해석 재작업 한 회(모델 호출 한 번)를 피할 기회가 생긴다. 구간 검사 코드 약 20행이 줄어든다. 빈도는 미확인이다.
- 위험과 보호: `tests/test_submission_tools.py`, `tests/test_initial_intent_connection.py`가 덮는 것으로 추정한다(테스트명 미확인). 제출 도구는 작업 공간 안에서 패키지 없이 돌 수 있으므로 `governance` import 가능 여부를 확인해야 한다. 이 점은 미확인이다.
- 확신: 중간. 검사 경로는 원문으로 확인했다. 제출 도구의 실행 환경은 확인하지 않았다.
- 다른 영역: `do_math/submission.py`, `do_math/governance.py`, `do_math/control_contracts.py`, `references/입력-소비자.md`

#### STO-23: 레코드를 검증할 때마다 JSON Schema 검증기를 새로 만든다

- 유형: 운영비용
- 위치:
  - `do_math/state_contract.py:164`
  - `do_math/state_checks.py:233-234`
  - `do_math/record_schemas/__init__.py:565`
- 현상: 변경된 레코드마다 `Draft202012Validator(family.schema)`를 생성한다. 실측 결과는 다음과 같다(6절).
  - 생성만: 1000회 0.0104초
  - 재사용 검증: 1000회 0.1079초
  - 생성 + 검증: 1000회 0.1255초

  약 16%의 추가 비용이다.
- 제안: `RegisteredFamily`에 검증기를 한 번 만들어 둔다. 등록 때 만들거나 지연 속성으로 만든다. 스키마는 등록 뒤 바뀌지 않는다(`state_contract.py:70-71`).
- 동작: 보존.
- 실익: 첫 읽기(전 레코드 검증)와 저장(변경 레코드)에서 스키마 검증 시간이 약 14% 준다. 측정 기반이다.
- 위험과 보호: `tests/test_redesign_STORAGE.py`가 덮는다.
- 확신: 높음.
- 다른 영역: 없음

## 3. 보존 판정

- **상태 저장 값에 쓰인 `json_digest`**(`do_math/input_basis.py:39`, `:46`, `do_math/record_schemas/__init__.py:366`, `:553`, `:569`, `do_math/state_contract.py:113`)
  - 겉보기 문제: 계약 2.1은 상태 값의 식별에 `exact_content_hash`를 쓰라고 정하는데, 이 값들은 `json_digest`를 쓴다.
  - 유지 이유: 다이제스트가 저장되고 다시 대조되므로, 바꾸면 기존 기록의 대조가 깨진다. 계약 2.1의 "기존 변종" 목록에 이 항목들을 추가해 명시하는 것만 권한다.
- **읽기 때 정규형 재인코딩 대조**(`do_math/repository.py:546`)와 **게시 이벤트 연속성 검사**(`:796-803`)
  - 겉보기 문제: 저장 때 이미 보장한 것을 다시 본다.
  - 유지 이유: 디스크의 기존 기록은 신뢰 경계 밖이다(기준 문서의 검사 위치 원칙).
- **`check` 명령의 artifact 전 바이트 해시**(`do_math/state_checks.py:270-280`)
  - 겉보기 문제: `VERIFIED_ARTIFACTS`를 쓰지 않는다.
  - 유지 이유: 계약 2절이 `check`를 명시적인 새 내용 확인으로 정했다.
- **경로 검사 세 번**(`do_math/repository.py:272`, `do_math/git_store.py:204`, `:218`, `:364`)
  - 겉보기 문제: 같은 경로를 여러 번 검사한다.
  - 유지 이유: `validate_candidate`는 단독으로도 쓰인다(`engine.py:2299`). 경로당 비용은 마이크로초 단위라 실익이 작다.
- **`relation_refs.relation_references`와 `REFERENCES["relations"]`**(`do_math/relation_refs.py:13-16`, `do_math/record_schemas/__init__.py:32-33`)
  - 겉보기 문제: 같은 관계의 참조 필드를 두 번 나열한다.
  - 유지 이유: 앞쪽은 탐색 씨앗이라 `evidence_refs`를 포함하고, 뒤쪽은 참조 무결성이라 자유 문자열인 `evidence_refs`를 제외한다. 합치면 증거 문자열에 무결성 검사가 걸린다.
- **`context_store._relative`와 `git_store._validate_path`**
  - 겉보기 문제: 비슷한 경로 규칙이 두 벌이다.
  - 유지 이유: 앞쪽은 작업 공간의 논리 경로이고, 뒤쪽은 상태 트리 경로다. 대상이 다른 개념이다.
- **정리 직전 로컬 파일 재조사**(`do_math/retention.py:232-242`)
  - 겉보기 문제: 후보를 계산할 때 이미 조사했다.
  - 유지 이유: 삭제 직전의 TOCTOU 방지다. 지문 표시(`marks`)로 이미 경량화돼 있다. STO-17은 상태 재구성만 대상으로 한다.
- **역할 manifest 검증의 생산자와 수신자 양쪽 실행**(`do_math/context_store.py:709`, `do_math/state_checks.py:466` 경유 `:793`)
  - 유지 이유: 수신 쪽은 디스크 기록을 다룬다. 원칙에 맞는 구조다. 같은 호출이 두 번 겹친 부분만 STO-01에 넣었다.
- **`input_recovery.validate_resolutions`**(`do_math/submission.py:851`, `do_math/engine.py:2815-2817`)
  - 유지 이유: 이미 생산자와 수신자가 공유 함수 하나를 쓰는 모범 형태다. 엔진의 두 번 호출(제공본과 현재본)은 서로 다른 값을 검사한다.
- **`_validate_candidate`와 `save_with_state` 반환의 깊은 복사**(`do_math/repository.py:226-227`, `:307`)
  - 유지 이유: 공유 캐시 항목을 호출자의 변형으로부터 격리한다. 봉인 payload는 복사 비용이 없다(`payloads.py:16`).
- **`_write_blobs`의 임시 파일 경유**(`do_math/git_store.py:171-191`)
  - 유지 이유: argv 한도와 경로 인용 문제를 피하고, 정확한 바이트를 보존한다. 프로세스 수는 이미 1회다.
- **payload 복원 뒤 재인코딩 대조**(`do_math/payloads.py:143-145`)
  - 유지 이유: 인코딩 하나만 허용하는 강제다. 대형 필드의 외부화 누락을 막는다.

## 4. 후보 없음

전문을 읽었으나 후보가 없었던 모듈이나 주제는 다음과 같다.

- `do_math/file_io.py`: 직전 라운드가 정한 공유 커널이다. 새 이음새 중복을 찾지 못했다. STO-06의 `is_sha256`과 STO-21의 `os_lock`은 이 모듈을 정본 위치로 제안할 뿐이다.
- `do_math/operation_trace.py`: 모든 공개 함수에 호출자가 있다(`grep -rn "phase_rows\|trace_rows\|child_environment\|workspace_operation\|progress("`). 이벤트마다 live 파일을 교체하는 비용은 진행 상황 보고 기능의 대가이며, 진행 이벤트는 초당 1회로 제한된다.
- `do_math/input_recovery.py`: 생산자와 수신자가 공유 함수를 쓴다(3절).
- `do_math/relation_refs.py`: 3절의 보존 판정 외에는 없다.
- `do_math/input_basis.py`: 3절의 `json_digest` 보존 외에는 없다. `results_sha256` 접두 해시(`:94`)는 생산자(`planning.py:36`)와 같은 `exact_content_hash`를 쓴다.
- 파견문의 네 관점 가운데 "같은 커밋·스냅숏 경로의 반복 직렬화"에서 게시 인코딩 외의 추가 후보는 없었다. STO-03, STO-08, STO-19, STO-20이 이 관점의 결과다.

## 5. 미완료

없음. 영역 모듈은 모두 전문을 읽었다. 판정에 확인하지 못한 세부(개별 함수 본문, 테스트명, 실제 인스턴스 크기)는 각 후보의 `미확인` 필드에 이유와 함께 적었다.

## 6. 작업 중 사건

- graphify는 쓰지 않았다. 대상 모듈을 전문으로 읽었고, 이음새 추적은 grep 전수로 충분했다.
- 읽기 전용 확인을 위해 다음 명령을 실행했다. 모두 `C:/math/.claude/skills/do-math/scripts`에서 실행했고, 저장소 상태를 바꾸지 않는다.
  1. Git 생성 비용: `python -c "…subprocess.run(['git','-C','C:/math','rev-parse','HEAD'])를 20회…"`. 결과는 `git spawn avg ms 36.33994499978144`다.
  2. 초기화 호출 병합 가능성: `git rev-parse --absolute-git-dir --show-object-format`. 결과는 `C:/math/.git`과 `sha1` 두 줄이다.
  3. ref 이름 batch-check: `printf 'refs/heads/main\nrefs/heads/absent-xyz\nrefs/heads/main^{tree}\n' | git cat-file --batch-check='%(objectname) %(objecttype)'`. 결과는 `<oid> commit`, `refs/heads/absent-xyz missing`, `<oid> tree`이고, 종료 코드는 0이다.
  4. 검증기 생성 비용: `Draft202012Validator(RECORDS['executions'])` 1000회. 결과는 `construct/1000=0.0104s iter(reuse)/1000=0.1079s construct+iter/1000=0.1255s`, jsonschema 4.26.0이다.
  5. 합성 상태(실행 레코드 2000개, 11,274,915바이트) 측정. 결과는 `walk=1.750s dumps=0.658s per-record canonical=2.203s deepcopy=0.286s eq=0.006s`다.
  6. 실행 레코드 2000행 스키마 검사: `2000 execution rows schema: 1.065s errors=0`.
  7. 설정 키 집합 비교(`default_state_contract()`의 config 스키마와 `control_contracts.CONFIG_PATCH`). 결과는 저장 쪽에만 있는 키 `[]`, 입력 쪽에만 있는 키 `[]`, 타입이 다른 키 28개, `GRANT`에만 있는 키 `['resource_limits']`다.
- 예상과 달랐던 결과가 둘 있다.
  - 파생 가족 `task_readiness`가 생산 상태에 한 번도 나타나지 않는다(STO-12).
  - `inspect_state`의 모든 호출자가 적재 검증 직후의 상태를 넘긴다(STO-01).
- 접근을 바꾼 지점이 하나 있다. STO-09에서 처음에는 `read_snapshot`을 batch-check 한 번으로 완전히 대체하려 했다. 그런데 `tests/test_git_store.py`의 `test_non_commit_or_corrupt_existing_ref_is_not_treated_as_absent`가 "부재"와 "손상"의 구분을 요구한다. 그래서 `missing`일 때만 기존 `rev-parse`로 내려가는 대체 경로를 제안에 넣었다.
- `tests/test_state_checks.py`는 검증되지 않은 상태를 `inspect_state`에 직접 넘긴다. 이 때문에 STO-01은 동작 보존이 아니라 변경으로 분류했다.

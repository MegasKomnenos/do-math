# 결과 — 그룹 B (저장·상태·보존 정리·역할 입력 보관)

이 문서는 do-math 경량화 2라운드 그룹 B의 반환이다. 설계 `docs/do-math/경량화-설계-2026-09-26.md` 6절의 다섯 항목을 순서대로 적는다. 통합자는 이 문서로 브랜치 `r2-b`를 합칠 때 확인할 이음새와 다른 그룹과의 충돌 지점을 판단한다.

- 브랜치·커밋: worktree `C:/math-worktrees/r2-b`, 브랜치 `r2-b`, 커밋 `5b02d03`(기준 `24682fd`, 커널 병합 상태)
- 변경 범위: 제품 21개 파일(`record_schemas/domains.py` 삭제 포함), 시험 37개 파일. 스킬 문서는 고치지 않았다(3절).
- 좌표: 따로 적지 않으면 경로는 `C:/math-worktrees/r2-b/.claude/skills/do-math/scripts/` 기준이다.
- 확인: 시험은 실행하지 않았다(설계 3.3). 바꾼 제품·시험 파일 전부가 `python -m py_compile`를 통과했다.

## 1. ID별 처분

표의 모든 ID와 추가 배정 셋을 구현했다. 조사 제안과 방법이 달라진 곳은 처분 칸에 이유와 좌표를 적었다.

| ID | 처분 | 내용 |
|---|---|---|
| STO-01, OPS-07 | 구현함 | `record_schemas/__init__.py`의 `validate_semantics`가 `preflight.inspect_current_state`를 조건 없이 실행한다. 따라서 적재·후보 검증을 통과한 모든 상태가 수명 주기 관문을 만족한다. 적재 뒤 재검사 넷을 지웠다. 엔진 생성자, `control`, `_inspect_before_write`, `check`의 `_require_current_contract`는 함수와 함께 삭제했다. `preflight.inspect_persisted_state`는 삭제했고, `preserve_rejected_candidate`는 `store.load`의 검증 실패를 `damaged current state cannot be rewritten`으로 바꾼다. `state_checks.inspect_state`에서는 적재가 이미 보는 조건을 지웠다. 대상은 스키마 재검사, 저장 값 영역, ID 중복, feature_version, 거버넌스·활동·과제 계약·과제 상태·프로필·실행 상태와 결속·예약·외부 작업 상태와 결속·지식·형식 증거·동일성 기준·관찰 규칙·자기 점검 결속·처분·stop phase, 그리고 `validate_role_manifest` 단독 호출이다. 점검에만 있는 조건(조사 3항 목록)은 남겼다. 각 영역 `checked_invariants`의 첫 항목은 `load-time state contract validation`이다. 엔진 `check`의 `validate_knowledge_records` 재호출도 지웠다. 동작 변화: `lifecycle`이 없는 상태는 적재 단계에서 거부된다. |
| STO-02 | 구현함(방법 변형) | 스키마 열거값을 상수에서 만든다. 실행 status는 `execution_lifecycle.EXECUTION_STATUSES`, stop_phase는 `STOP_PHASES`, 과제 status는 `task_contracts.LIFECYCLE_STATES`, 외부 작업 status와 실행 `effect_status`는 새 `record_schemas/schemas.OPERATION_STATUSES`다. `state_checks`의 로컬 집합과 `task_contracts.validate_task_contract`의 상태 재검사를 지웠다. 외부 작업 상태 상수는 조사가 추정한 `external.py`(그룹 D) 대신 설계 정정대로 그룹 B 모듈인 `schemas.py`에 두었다. 조사 제안의 `execution_record_errors(row)` 함수는 만들지 않았다. 실행 한 건의 세 불변식(종료 증거, stop_phase, 수락 영수증)의 사본은 점검 쪽뿐이었고 STO-01에서 지워졌으므로, `validate_semantics`의 한 곳이 이미 유일한 정의다. `outcome ∈ OUTCOMES`는 점검 전용으로 남겼다(STO-01 제안 3항). |
| STO-03 | 구현함 | `_validate_candidate`의 상태 전체 `validate_storage_value`를 지웠다. `_encode_families(..., parent=)`는 부모 레코드와 `==`인 레코드에 부모 파일 바이트를 쓴다. payload blob 경로와 바이트는 `encode`로 다시 얻는다(직렬화는 하지 않는다). |
| STO-04 | 구현함 | `validate_candidate` 결과에 `basis`(`head`, `validation_generation`)와 `artifacts`를 싣는다. `ResearchRepository.save_validated(expected_head, candidate)`는 기준이 같으면 재검증 없이 게시하고, 다르면 전체 검증한다. `integration.apply_bundles`는 `validate_candidate`의 결과를 `publish(instance, runtime, bundle, validated)`에 넘기고(그룹 C·D 모듈의 호출부 최소 변경), 엔진 `publish`는 `save_validated`를 쓴다. 조사의 `engine.py:2292` `validate_knowledge_records`는 `validate_semantics`가 다시 하므로 지웠다. |
| STO-07 잔여(추가 배정) | 구현함 | `git_store.check_path_segment(part)`가 경로 성분 규칙(빈 성분, `.`·`..`, 끝 점·공백, 구분자, 금지 문자, 예약 장치명)의 정본이다. `_validate_path`와 `StateContract.validate`의 `RECORD_ID` 검사가 이 함수를 부른다. `state_contract`가 `git_store`를 import하지만 순환은 없다. |
| STO-08, ENG-19 | 구현함 | 역할 입력을 한 벌만 보관한다. 엔진은 `input_bundle`을 입력 준비 전에 할당하고, `prepare_role_input(..., artifact_prefix="runtime/artifacts/<input_bundle>")`을 부른다. `context_store`가 그 아래에 프롬프트 `input.txt`, 역할 문서 `input/implementation/<path>`, 카탈로그 `input/catalog/<key>.json`(`fit_context`의 `catalog_files` 바이트 재사용), 세부 원천을 둔다. 이름은 엔진 쪽 경로로 통일했다. 문서 행의 sha256은 문서 dict의 `sha256`을 재사용한다. `engine._input_artifacts(bundle, schema, fitted, workspace)`는 여기에 schema·manifest·도구·support만 더한다. 실행의 `input_sha256` 필드를 없앴고, 소비자 다섯 곳이 `input_manifest.prompt`를 읽는다. 대상은 `model_runner.verified_native_final`, `review_engine` 결속 두 곳, `review_cycle.validate_review_execution`, `engine._inspect_before_write`(manifest의 prompt 경로 존재)다. 엔진 `check`의 `input.txt`↔`input_sha256` 비교는 지웠고, 같은 비교는 `start_import_input` 영역의 `verify_manifest_artifacts`가 한다. 진단 자료와 검토 프롬프트 봉인도 manifest의 `artifact_ref`를 쓴다. |
| STO-09 | 구현함(방법 변형) | `read_snapshot`은 `ref`, `ref:research`, `ref:runtime`을 batch-check 한 번으로 묻는다. 첫 줄이 missing일 때만 `rev-parse --verify --quiet`로 부재와 손상을 가른다. `GitStateStore` 생성은 `rev-parse` 한 번이다. `StateSnapshot`의 트리 필드와 `_subtree_oids`·`_head`를 지웠다(생산 소비자 없음, 시험은 `git rev-parse`로 대체). 게시의 두 하위 트리 존재는 이제 후보 경로 목록으로 확인한다(Git 프로세스 없음, 최초 외 게시에도 적용). `publish`의 잠금 밖 `_head()` 사전 비교는 인자로 생략하지 않고 지웠다. 근거: 생산 호출자 둘(`ResearchRepository.initialize`, 저장 경로의 `_precheck_head`)이 모두 바로 앞에서 같은 비교를 하고, 최종 CAS가 권위다. |
| STO-10 | 구현함 | `read_many`·`blob_sizes`(Git 저장과 `ResearchRepository`)에 `missing="raise"|"omit"`을 두었다. `state_checks._artifact_sizes` 재시도 루프, `prefetch_artifacts`의 경로별 재시도, `_inspect_before_write`의 재시도를 지웠다. 엔진 `status`·`check`·`_inspect_before_write`와 `reporting`이 `omit`을 넘긴다. 없는 경로는 `artifact is missing` 결함으로 기록된다. |
| STO-12 | 구현함 | `derived` 형태, `task_readiness` 가족과 관련 분기를 `state_contract`·`repository`·`record_schemas`에서 지웠다. |
| STO-13 | 구현함 | 이벤트 가족은 `list` 형태다. `event_rows`의 맵 분기와 `EventPublisher.prepare`를 지웠다. |
| STO-14 | 구현함 | `events.check_sequence(rows, cursor=None)`가 번호 규칙의 정본이다. 읽기(`_read_documents`)와 `assign_sequences_in_place`의 결과 검사가 이를 쓴다. 부모 이벤트 재검사는 지웠다. 순서 위반 문구는 모두 `published event sequence is not contiguous`가 되었다. |
| STO-15 | 구현함 | `domains.extend()`의 모든 수정을 `record_schemas/schemas.py`의 가족 정의에 합쳐 최종형으로 한 번만 정의했고, `domains.py`를 삭제했다. `record_schemas/__init__.py`는 `import *` 대신 쓰는 이름만 명시 import한다. 외부 모듈 import는 `_`로 시작하는 별칭이라 새지 않는다. manifest 다이제스트 동일성은 실행 금지로 확인하지 못했다. 열거값 정렬(STO-02)과 필드 삭제로 다이제스트는 바뀐다. 저장 manifest의 다이제스트는 형태만 검사되므로 기능 영향은 없다. |
| STO-17 | 구현함 | `_maintenance_cleanup`이 같은 head의 보존 상태를 한 번 만들고, `current_state`는 head가 같으면 재사용한다. 보호 경로의 물리 해석(`retention._protected_paths`)은 `cleanup_candidates` 진입 때 한 번 한다. 해석 불가 경로가 하나라도 있으면 모든 실행이 그 사유로 부적격이다(조사가 예고한 보수화). |
| STO-18, ENG-23 | 구현함 | `retention.PROTECTED_REFERENCE_KEYS`(엔진 19개 키와 조사가 짚은 `formal_result_refs`, `assessment_refs`의 합집합)와 `record_references`, `retention_inputs(instance, runtime, rows)`를 두었다. 엔진 `_retention_state`는 이를 부르고, 관계 기록에는 `relation_refs.relation_references`를 더한다. `reference_closure`는 각 기록의 `references`만 따른다. 차이 하나: 전에는 retention이 7개 키 아래 객체의 모든 문자열을 따라갔다. 이제는 목록 안 객체와 객체 값에서 `id`, `ref`, `artifact_ref`, `path`만 따라간다(엔진 규칙과 같고, 목록 안 객체의 ID는 새로 따라간다). |
| STO-19 | 구현함 | 스냅숏 읽기는 서술자를 만들지 않는다. `_descriptors(head)`가 요청 시 `_decode_families(..., describe=True)`로 한 번 만들어 캐시에 더한다. 서술자의 `deepcopy(row)`를 지웠고, `records`·`read_record`는 고른 행만 복사한다. |
| STO-20, ENG-14 | 구현함 | `_state_signature`와 `_saved_state`를 지웠다. `ResearchRepository.published_state(head)`는 캐시된 상태를 복사 없이 돌려준다. 엔진 `_unchanged()`는 이 값과 현재 상태를 `updated_at`을 빼고 비교한다. 캐시에서 밀려난 head는 거짓이고 저장이 진행된다. `_reload(snapshot=None)`가 재적재 여덟 곳(엔진 일곱, `scheduler` 하나)을 대신한다. `process_controls`의 적재·비교는 `self._save()` 한 줄이 되었다. |
| STO-23 | 구현함 | `RegisteredFamily.checker`(cached_property)가 스키마 검증기를 한 번 만든다. `StateContract.validate`와 위임 참조 검사가 이를 쓴다. `validate_semantics`는 `contract=` 키워드를 받는다. `state_checks`의 재검사는 STO-01에서 지웠다. |
| ENG-13 | 구현함(전제 오류) | 조사 전제 "저장소 `validate_candidate`에는 ID 중복 검사가 없다"는 틀렸다. 기준 커밋의 `state_contract.py` `StateContract.validate`가 전역 유일성을 검사하고(`record IDs must be globally unique`), `validate_candidate`가 이를 부른다. 그래서 `record_id_collisions`를 만들지 않았다. `engine._records`와 그 호출을 지워 정본 하나(`StateContract.validate`)만 남겼다. `state_checks` 사본은 STO-01에서 지웠다. `planning._records`는 조회 색인으로 둔다. |
| ENG-18 | 구현함 | `ResearchRepository.view(snapshot)`(복사 없는 읽기 전용 적재)를 두었다. 일곱 곳이 쓴다: `_validate_bundle_current`, `_apply_extensions`, 부수 통찰 기원, 후보 작성 환경, 운영 처분 평가, `_apply_plan`, `scheduler._apply_queue_plan`. 호출된 함수(`apply_task_dispositions`, `apply_task_assessments`, `_apply_task_plan`, `capture_basis`, `capture_sources`, `validate_plan_submission`)가 입력을 고치지 않는 것을 원문으로 확인했다. `decision_engine.py`의 같은 모양 적재는 조사 목록 밖이고 그룹 C 모듈이라 두었다. |
| ENG-20 | 구현함 | `ENGINE_SHA256`, 실행의 `engine_sha256` 기록 두 곳과 저장 스키마 필드를 지웠다(설계 1.2). `_receive_submission`의 대체값을 지우고 `context["submission_contract"]["tool_sha256"]`를 쓴다. |
| RUN-20 | 구현함 | 점검 경로를 `execution["capacity"]["reservation_ids"]`로 고쳤다. 스키마의 최상위 `reservation_ids`와 `capacity`의 미사용 7필드를 지웠다(생산자 `session_slots.py:195`가 쓰는 네 키만 남음). |
| 순수 픽스처 분기(추가 배정) | 구현함 | `lifecycle_engine`의 `callable(getattr(store, 'load', None))` 분기 둘을 없앴다. `_verify_current_head`는 함수째 지웠다. 이 함수가 검사하던 것은 엔진이 적재하거나 게시한 head가 검증된 상태로 읽히는지인데, STO-01 뒤에는 적재 검증이 같은 사실을 이미 보장하기 때문이다. `_apply_extended_control`의 실패 경로는 항상 `preserve_rejected_candidate(self.store, ...)`를 부른다. 시험 대역은 `tests/research_fixtures.StateStore(engine)`(`load`, `published_state`, `save_with_state`만 구현)를 받는다. `FakeEngine`이 이를 쓰고, `del e.store.load` 줄을 지웠다. |
| REV-14 잔여(추가 배정) | 구현함 | 결과-C.md REV-14 행이 넘긴 형태 조건을 저장된 `tasks` 스키마에 표현했다. `question`, scope 항목, `expected.research_change`와 outputs, 기준·의무의 `claim`은 비지 않은 텍스트(`minLength 1`, `pattern \S`)다. `expected.outputs`, `progress_criteria`, `completion_obligations`는 `minItems 1`이다. `revision`은 필수이며 `minimum 1`이다. `evidence_required`는 비지 않은 문자열의 고유 목록, `evidence_requirements`는 비지 않은 텍스트의 고유 목록이다. 완료 의무의 `judges`는 필수이고 비지 않은 텍스트 1개 이상이다. 프로필 참조 판본은 기존 `PROFILE_REF`가 이미 표현한다. 전역 `TEXT`·`NAT`는 모든 가족에 걸리므로 바꾸지 않고, 과제 기록 안에서만 강화했다. 지금의 `validate_task_contract`(가족 검증기)가 같은 조건을 이미 요구하므로, 저장 가능한 과제의 집합은 바뀌지 않는다. 바뀌는 것은 오류 문구가 스키마 문구로 먼저 난다는 점이다. |

## 2. 새로 만든 공유 정의와 위치

설계 정정(필요한 공유 정의가 커널에 없으면 개념을 소유한 자기 그룹 모듈에 하나만 만든다)에 따라 아래를 만들었다.

| 이름 | 위치 | 규칙 |
|---|---|---|
| `check_path_segment(part)` | git_store | 상태 경로 한 성분의 Windows 저장 규칙 |
| `read_many`·`blob_sizes`의 `missing=` | git_store, repository | 없는 경로를 빼는 일괄 읽기 |
| `check_sequence(rows, cursor=None)` | events | 공개 이벤트 번호 규칙 |
| `save_validated`, `view`, `published_state` | repository | 검증 결과 게시, 복사 없는 적재, 캐시 조회 |
| `RegisteredFamily.checker` | state_contract | 가족별 스키마 검증기 |
| `OPERATION_STATUSES` | record_schemas/schemas | 외부 작업 상태 값 |
| `PROTECTED_REFERENCE_KEYS`, `record_references`, `retention_inputs` | retention | 정리 보호 참조의 어휘와 수집 |
| `ResearchEngine._unchanged`, `_reload` | engine | 무변경 판정, 재적재 |
| `current_state`, `StateStore` | tests/research_fixtures | 최소 현행 상태, 메모리 엔진의 저장소 대역 |

삭제한 공개·내부 이름은 다음과 같다: `preflight.inspect_persisted_state`, `payloads.payload_identity_view`, `EventPublisher.prepare`, `engine._require_current_contract`·`_records`·`ENGINE_SHA256`·`_state_signature`·`_saved_state`, `lifecycle_engine._verify_current_head`, `git_store._head`·`_subtree_oids`·`_parse_subtree_oids`, `repository._documents`·`_validate_published_events`, `retention._references_run`, `state_checks._artifact_sizes`, `record_schemas._task_readiness`, `record_schemas.domains`. 저장 필드 `executions.engine_sha256`·`input_sha256`·`reservation_ids`와 `capacity`의 7필드도 삭제했다.

## 3. 필요한 문서 변경

- `references/CLI-실행-계약.md`
  - 56행: "낡은 파생 view는 공개 전에 거부된다"를 지운다(STO-12). 이벤트는 목록 형태만 허용한다는 점을 더한다(STO-13).
  - 60–68행 artifact 표: `input/implementation/<path>`는 "고정 사본"이 아니라 manifest `documents[].artifact_ref`가 가리키는 유일한 원문이다. `input/catalog/<key>.json`(문맥 카탈로그)과 `input.txt`가 manifest `prompt.artifact_ref`라는 점을 더한다(STO-08).
  - status·check·run 사전 점검 절: `check`의 역할 입력 비교는 `start_import_input` 영역이 manifest로 한다. 점검은 적재 검증을 통과한 상태만 보고, 적재 조건을 다시 보지 않는다(STO-01). 없는 artifact는 영역 결함으로 보고된다(STO-10).
- `references/공통-실행.md` 15행: "같은 원문은 … `input/implementation/<path>`에도 사본으로 저장되지만" 문장을 고친다. 원문은 입력 묶음의 `input/implementation/<path>` 한 벌이고, manifest `artifact_ref`가 그 경로다(ENG-19).
- `계약/의도-해석.md` 14행 "실행 봉투의 `input_sha256`": 실행 필드 `input_sha256`이 없어졌다. 위임 판정의 `input_sha256`(적용 기록의 기반 digest)을 가리킨다면 그대로 두고, 실행 입력을 가리킨다면 `input_manifest.prompt.sha256`으로 바꾼다. 문서 단계가 문맥으로 판정한다.
- `docs/do-math/검사-경량화-이음새-계약.md`: 2절 표에 1절의 새 정의(`check_path_segment`, `check_sequence`, `missing=`, `save_validated`, `retention_inputs`)를 옮길지 통합자가 정한다. 4절(S4)의 head 이동 지점 목록에 `_reload`를, 무변경 판정 항목(R12 서명)을 `published_state` 비교로 바꾼다.

## 4. 고친 시험과 확인하지 못한 위험

고친 시험 파일(37개, `tests/` 아래)은 다음과 같다. research_fixtures, test_boundary_repairs, test_execution_observation_profile, test_git_store, test_host_resources, test_initialization_efficiency, test_knowledge_io, test_lifecycle_engine, test_machine_parallel, test_native_final_submission, test_performance_repairs, test_performance_save, test_preflight, test_provider_wait, test_purpose_engine, test_redesign_ACTIVITIES, test_redesign_CONTRACTS, test_redesign_ENGINE, test_redesign_EVIDENCE, test_redesign_EVIDENCE_walkthroughs, test_redesign_GOVERNANCE, test_redesign_KNOWLEDGE, test_redesign_PROFILES, test_redesign_REVIEWS, test_redesign_STORAGE, test_redesign_SURFACE, test_redesign_TASKS, test_repair_execution, test_reporting, test_repository, test_review_engine, test_state_checks, test_static_review_repairs, test_storage_validation, test_submission_flow, test_unicode_flow, test_walkthrough_followup.

바꾼 성격은 다섯 가지다.

- 최소 상태(`{"feature_version": 5}` 등)를 `research_fixtures.current_state(...)`로 바꿨다(수명 주기 관문). 관문 밖의 runtime 상태값(`active`, `winner`, `ended` 등)은 허용 값으로 바꿨다.
- `test_state_checks`와 `test_redesign_SURFACE`에서 점검에서 지워진 조건의 단언을 `StateContract.validate` 거부 단언으로 옮겼다. 옮기지 못한 단언은 없다.
- 삭제·서명 변경 API를 따라 고쳤다: `_input_artifacts`, `publish` 네 인자와 `save_validated`, `store.view`, `input_manifest.prompt`, `StateSnapshot`, 이벤트 문구, `check`의 영역.
- 삭제한 시험은 하나다: `test_performance_repairs.CandidateCopyTests.test_public_event_prepare_still_returns_detached_state_and_protects_failures`(`prepare`만 검사). `test_redesign_STORAGE`의 파생 view 시험은 `task_readiness`가 미등록 가족으로 거부되는 시험으로 바꿨다.
- `SnapshotMetadataTests`는 한 번의 batch 읽기를 검사하도록 다시 썼다. 옛 단언 "모든 메타데이터가 하나의 해석된 OID에 묶인다"는 버렸다. ref 이름으로 한 batch에 묻는 설계에서는 성립 대상이 없다.

실행하지 않아 확인하지 못한 위험은 여섯 가지다.

1. **merge된 스키마의 의미 동등성.** 약 500행을 손으로 합쳤고 manifest 다이제스트 비교를 할 수 없었다. 누락·중복 필드가 있으면 첫 실행에서 `additionalProperties` 거부로 드러난다. 합친 뒤 줄 단위로 대조했다.
2. **오류 문구.** 시험의 거부 문구는 제품 원문에서 가져왔지만, 여러 오류 중 무엇이 먼저 나는지는 원문 순서로만 추론했다. jsonschema 경로 문구, `publish compare-and-swap`, `record list`, `artifact is missing`이 해당한다.
3. **값 동등과 형의 차이.** STO-03의 바이트 재사용과 기존 부모 생략 검증은 `==`로 같은 레코드를 판정한다. 파이썬에서 `1 == True`, `1 == 1.0`이므로, 같은 자리의 값이 이렇게 형만 바뀌면 부모 바이트가 게시되고 이 프로세스의 캐시에는 바뀐 형이 남는다. 생산 코드가 형만 바꾸는 경로는 찾지 못했다.
4. **수명 주기 관문의 적용 범위.** 모든 적재에 관문이 걸린다. 수명 주기가 없거나, 상태가 허용 값 밖이거나, `last_observed_utc`가 없는 상태를 저장하는 시험이 담당 밖 파일에 더 있으면 실패한다. 네 에이전트의 배정과 grep 전수로 찾은 범위는 모두 고쳤다.
5. **`_unchanged`와 `published_state`.** autospec 저장소 대역에서는 `published_state`가 MagicMock을 돌려주므로 비교는 거짓이 되고 저장이 진행된다(전의 `_saved_state=None`과 같다). 동작 차이 하나를 알린다. 전에는 `_apply_submission_bundles`가 게시하지 않은 메모리 변경까지 저장된 것으로 표시했다. 이제는 실제 게시 상태와 비교하므로, 그런 변경은 다음 `_save`에 게시된다.
6. **`_inspect_before_write`의 전제.** input_bundle이 있는 실행은 dict manifest의 `prompt.artifact_ref`를 가진다고 본다. 엔진이 만드는 실행은 늘 그렇다. `test_governance_engine`의 AUDITOR 대역은 input_bundle과 목록 manifest를 갖는다. 지금은 이 경로를 타지 않지만, 타면 TypeError가 난다.

## 5. 전제가 틀렸거나 계획을 바꾼 지점

- **ENG-13.** 조사 전제가 틀렸다(1절). 새 함수 없이 엔진 사본을 지웠다.
- **STO-02.** 외부 작업 상태 상수를 조사가 추정한 `external.py` 대신 그룹 B의 `schemas.py`에 두었다. `execution_record_errors`는 사본이 없어져 만들지 않았다.
- **STO-09.** `publish`의 사전 비교를 인자로 생략하지 않고 지웠다. 게시 뒤 하위 트리 조회(`_subtree_oids`) 대신 후보 경로 목록으로 두 루트의 존재를 확인한다.
- **순수 픽스처 분기.** 분기만 지우는 대신 `_verify_current_head` 전체를 지웠다. 이 함수의 검사는 STO-01 뒤 적재 검증과 같은 사실이다.
- **REV-14.** 결과-C가 적은 "`TEXT`·`NAT` 강화"는 전역 상수가 아니라 과제 기록 안에서만 적용했다. 전역으로 바꾸면 모든 가족의 텍스트·정수 필드가 바뀐다.

다른 그룹과 겹치는 지점:

- **그룹 A(결정 4).** 저장 스키마의 `operations_slots`, `total_slots`, `budget_kind`와 `state_checks`의 예약 풀 검사는 손대지 않았다. `domains.py`가 삭제되어 A가 그 파일에서 고친 부분은 병합 때 `schemas.py`의 해당 정의에 다시 적용해야 한다. 해당 정의는 `capacity_constraints`, `reservations`, `execution_profiles`, `grants`, `external_operations`, `_ACTION`이다.
- **그룹 C.** 두 가지를 병합 때 반영해야 한다. 첫째, ENG-04가 `domains.py`에서 지운 `RESEARCH_FIELDS["available_input_refs"]`를 `schemas.py`의 `RESEARCH_FIELDS`에서도 지운다. 둘째, REV-14 강화로 `validate_task_contract`에 남긴 형태 조건(비지 않은 텍스트·목록, 양수 revision, judges, 증거 고유성)을 저장 스키마가 표현하게 되었다. 그 검사를 지울지 통합자가 판단한다. 저장되지 않은 엔진 생성 계약에도 이 검사가 쓰이는지 확인이 필요하다.
- **그룹 D.** `integration.apply_bundles`에서 두 줄(검증 결과를 `publish`에 넘김)과 설명문 한 줄을 바꿨다.
- **그룹 D의 `academic_engine._academic_evidence`**(시험 에이전트가 보고한 기존 코드). `read_many([ref], head).get(ref)`는 없는 경로를 None으로 받으려는 것처럼 보이나 기본값 `raise`로 부른다. 새 `missing="omit"`이 의도에 맞는지 그룹 D가 판단한다.

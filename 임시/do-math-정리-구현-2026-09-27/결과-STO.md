# 결과-STO: 저장·상태 그룹

## 1. 브랜치, 커밋, 바꾼 파일

- 브랜치는 `c-sto`이고, worktree는 `C:/math-worktrees/c-sto`다. 통합 브랜치 `c-int`의 `78f00bb`에서 시작했다.
- 마지막 커밋은 `d7d1b39`(`d7d1b394aebc71c095b0bf14890dc86fe6d24d05`)다. 파일 38개를 바꿨고, 577줄을 넣고 555줄을 뺐다.
- 아래 경로의 기준은 `.claude/skills/do-math/scripts/`다.

**제품 (19개)**

- `do_math/`: `context_store.py`, `engine.py`(1줄), `file_io.py`, `git_store.py`, `input_basis.py`, `integration.py`(1줄), `lifecycle_engine.py`(2줄), `payloads.py`, `record_schemas/__init__.py`, `record_schemas/schemas.py`, `repository.py`, `retention.py`, `review_cycle.py`, `review_engine.py`, `state_checks.py`, `state_contract.py`, `submission.py`, `task_contracts.py`(2줄)
- `do_math/` 밖: `operator_bootstrap.py`

여러 그룹이 고치는 `engine.py`, `integration.py`, `lifecycle_engine.py`, `task_contracts.py`, `review_engine.py`에서는 담당 ID가 요구하는 줄만 바꿨다. 줄 이동과 서식 정리는 하지 않았다.

**시험 (18개)**

`tests/`의 `research_fixtures.py`, `test_initialization_efficiency.py`, `test_lifecycle_engine.py`, `test_observations.py`, `test_performance_repairs.py`, `test_preflight.py`, `test_redesign_CONTRACTS.py`, `test_redesign_PROFILES.py`, `test_redesign_REVIEWS.py`, `test_redesign_STORAGE.py`, `test_redesign_SURFACE.py`, `test_redesign_TASKS.py`, `test_repository.py`, `test_review_engine.py`, `test_state_checks.py`, `test_state_contract_registration.py`, `test_storage_validation.py`, `test_unicode_flow.py`

**문서 (1개)**

- `이음새-정본.md`의 3절 규칙 두 항목과 6절 표 행을 고쳤다(3절 참고). 파견이 허락한 범위다.
- 스킬 문서와 `AGENTS.md`는 고치지 않았다.

**저장 계약**

판본은 `do-math-state/7` 그대로다. 이 판본 안에서 바뀐 저장 형식은 넷이다.

- 실행 `outcome`이 스키마 enum(`execution_lifecycle.OUTCOMES`)이 되었다.
- `sources` 스키마에서 `replaced_by`와 `revoked_at`을 지웠다.
- 검토 주기의 `review_input_basis`는 `{"values": ...}`만 싣는다. 실행의 `decision_basis`는 `{"records", "sources"}`만 싣는다. 두 필드는 열린 `EVIDENCE`라 스키마는 그대로다.
- 위 변경으로 설치 manifest의 digest가 바뀐다.

## 2. ID별 처분

좌표는 커밋 `d7d1b39`의 `do_math/` 기준이다. 집계는 구현함 15건, 구현하지 않음 0건, 조건 불성립 0건, 끝내지 못함 0건이다. 파견문이 붙인 후속 항목 셋도 모두 처리했다(이 절 끝).

- **STO-01 — 구현함.** 설치 계약을 프로세스당 하나 두고 모든 저장소가 공유한다.
  - `state_contract.default_state_contract()`가 `lru_cache(maxsize=1)`로 `StateContract()`에 `install`을 한 번 적용해 돌려준다.
  - 지운 것: `StateContract.default()`, 템플릿 `deepcopy`, 재등록 합성 분기(이제 재등록은 `ValueError("record family already registered")`), `validation_generation`, `installed_generation`, `_default_template`, `installed_checker`, `check_schema`, `ResearchRepository.register_family`, `repository._contract_key`, `validate_candidate`·`save_validated`의 `basis.validation_generation`(기준은 `{"head"}`만 남음), `StateContract.validate`의 `re.fullmatch(RECORD_ID)` 재검사.
  - `check_path_segment`와 id가 문자열인지의 검사는 남겼다.
  - `_VALIDATED_READS`의 키는 `(git_dir, head, 계약 객체)`다. manifest digest는 한 번 계산하고, `register_family`만 그 memo를 비운다.
  - `task_contracts.validate_task_contract`와 시험은 `default_state_contract().family(root, name).checker`를 쓴다.
  - 가족을 더해야 하는 시험은 `research_fixtures.installed_contract()`로 자기 계약을 만든다. 설치 가족의 검증기를 바꿔야 하는 시험은 `with_validator(...)`를 쓴다.
- **STO-02 — 구현함.** 기록 하나로 판정되는 규칙을 `record_schemas.RECORD_RULES`에 모았다. `install`은 이 규칙과 `governance_sources`의 `validate_source`를 가족 검증기로 등록한다.
  - `RECORD_RULES`가 담는 규칙: 원래 입력(`lifecycle`), 실행 국소 규칙, 외부 작업, 운영 처분, 학술 봉인, 관찰 사실 원문, 의도 수입 봉인, 위임 적용의 두 digest·참조 집합·실행 고유성.
  - 수작업 생략 다섯 곳을 지웠다. `governance_sources`, `academic_resolution_records`(`_prior_rows`), `observation_facts`, `intent_imports`, `immutable_input` 비교다.
  - 활성 grant의 복합 생략은 남겼다(`validate_semantics`의 grant 루프). 이 검사는 grant, 원천, 결정 세 기록을 읽는다. 그래서 가족 검증기의 일반 생략으로 표현할 수 없다. 지우면 모든 활성 grant를 저장마다 다시 검사하게 될 뿐이다. 원 검토 파일 STO.md의 STO-02 제안도 이 규칙을 `validate_semantics`에 남긴다. 통합표의 "5곳"은 이 해석(네 곳 + 검증 정정의 `immutable_input`)과 수가 맞는다.
- **STO-03 — 구현함(계약 2절 7항의 좁힌 범위).**
  - 순수 함수 `review_cycle.staged_review_candidate(instance, runtime, transition_id, knowledge_id)`와 `review_cycle.review_proposal`, `PROPOSAL_FIELDS`를 두었다. 옮긴 곳은 `review_engine`의 `_staged_review_candidate`, `_proposal`, `_PROPOSAL_FIELDS`, `_FORMAL_FIELDS`다.
  - 엔진의 두 호출부는 이 함수를 직접 부르고, `_proposal`은 import 별칭으로 남겼다.
  - 저장 검증은 `ReviewEngineMixin`을 만들지 않는다. `review_cycle.identity_assessment`와 `staged_review_candidate`를 직접 부른다.
  - 진행 중 전이(`checking`/`ready`)의 staged 후보는 지금처럼 매번 다시 만든다. `transition_basis` 해시는 둘 중 하나일 때만 다시 계산한다.
    - 전이가 진행 중이다.
    - 사이클이나 그 전이가 부모와 다르다.
- **STO-06 — 구현함.** `repository._canonical_object`와 `ResearchRepository.records`를 지웠다. 시험 5곳은 `load_records(head)[3]`을 거르게 바꿨다. `test_redesign_STORAGE`의 공개 API 단언은 `load_records`로 바꿨다.
- **STO-07 — 구현함.** `retention.cleanup_candidates`에서 `recovery_pending`·`checkpoint_required` 조건과 `not waiting.get('resolved')`를 지웠다. `test_redesign_SURFACE`의 해당 시험은 실제 계약 값 `recovery_disposition: "retain_for_recheck"`로 같은 차단 사유를 단언한다.
- **STO-10 — 구현함.** `input_basis`의 두 기록에서 `version`과 자기 digest(`sha256`)를 뺐다. 비교 함수는 기록이 있는지만 확인한 뒤 필드를 비교한다. 없을 때의 사유 문자열은 `missing_basis`다(옛 `missing_or_unsupported_basis`와 `basis_digest_changed`는 없어졌다). 이 모듈의 `json_digest` import도 지웠다.
- **STO-11 — 구현함.**
  - 저장 계약으로 옮긴 규칙:
    - 외부 작업: `unknown`이면 `succeeded`가 None이어야 한다.
    - 외부 작업: `cancelled`면 미전송이 확인되어야 한다.
    - 외부 작업: `handling=reconciled`면 증거 참조가 있어야 한다.
    - 실행 `outcome`: 스키마 enum.
  - `state_checks`의 점검 사본 넷을 지웠다.
  - 규칙을 어기던 생산 경로 두 곳을 찾아 고쳤다(`lifecycle_engine.py`).
    - 재시도 준비: `reconciliation`만 지우고 `handling=reconciled`를 남겼다. `reconcile → failed → retry` 흐름에서 저장이 실패했을 경로다. 지우는 키에 `handling`을 더했다.
    - `_run_external_action`의 예외 경로: 첫 `prepared` 저장 전에 예외가 나면 `transmitted` 없이 `cancelled`를 저장했다. 그러면 이 연산은 재시도의 미전송 분기에도 들지 못했다. 예외 경로가 `transmitted=sent`를 함께 기록한다.
  - 그 밖의 생산자(`external.py`의 네 함수, `governance._dispose_grant_consumers`, 실행 `outcome` 기록 전부)는 규칙을 지키는 것을 원문으로 확인했다.
- **STO-12 — 구현함.** `prepare_role_input`은 줄이지 않은 프롬프트를 초과 분기 안에서만 렌더링한다. 반환값에서는 `original_bytes`를 명시적으로 뺀다(`fitted.pop('original_bytes')`). overflow 기록의 `original_bytes`는 그대로다.
- **STO-14 — 구현함.** `state_checks.state_errors`를 지웠다.
- **STO-15 — 구현함(②·③만).** `git_store._git`의 `-c commit.gpgSign=false`를 지웠다. `validate_semantics`의 지연 import는 함수 머리에 한 번씩 모았다. `StateSnapshot`(①)은 계약대로 두었다.
- **STO-16 — 구현함.**
  - 경로 키 메모 가운데 결과를 정하는 바이트의 식별이 키에 없는 것은 `submission._ISSUED_INPUTS` 하나였다. 이 메모의 키를 읽은 바이트의 sha256으로 바꿨다.
  - 그래서 `issued_input`은 매번 바이트를 읽는다. 저장소의 `_ARTIFACT_FACTS`가 최근 바이트를 들고 있다. 이제 쓰지 않는 `git_dir` 인자는 지우고, 호출부 셋(`submission`, `integration`, `engine`)도 고쳤다.
  - `VERIFIED_ARTIFACTS`와 `planning._VALID_ARTIFACTS`는 키에 봉인 sha256이 있다. 같은 경로를 재사용해도 남은 항목이 틀린 답을 내려면 새 저장소의 바이트가 자기 봉인 해시와 달라야 한다. 이것은 한 저장소 안에서 이미 대조한 행이 나중에 손상된 경우와 같은 범위이므로 바꾸지 않았다. 이 규칙을 `이음새-정본.md` 3절에 적었다.
  - 시험 기반의 `forget_repository_caches` 삭제는 TSB-14에 남겼다. 다만 이 함수가 새 키(바이트)를 경로로 읽다가 30건이 오류가 났다. 그래서 비우는 목록에서 `submission._ISSUED_INPUTS`만 뺐다.
- **STO-17 — 구현함.** `repository._artifact_lock`과 `threading` import를 지웠다. 저장소 전역 캐시 다섯이 소유 스레드 전용이라는 전제를 모듈 설명 한 곳에 적었다.
- **STO-18·HIS-15 — 구현함(한 수정).**
  - `payloads.seal_large`의 순회가 `float`를 거부한다. 부모와 `==`인 기록도 저장마다 이 순회를 지나므로, 소수는 생긴 저장에서 바로 거부된다.
  - bool과 정수가 뒤바뀐 경우는 수용한 공백이다. 그 이유를 `StateContract.validate` 설명 한 곳에 적었고, `_encode_families` 설명이 그곳을 가리킨다.
  - 수용한 이유는 측정이다. 3.6 MB 합성 상태에서 `==`는 5.2 ms, 형까지 보는 재귀 비교는 139 ms가 걸렸다. 재귀 비교는 저장마다 두 번 돈다.
- **OPS-07 — 구현함.** `no_reparse`를 `file_io.py`로 옮겼다.
  - `git_store`, `context_store`, `repository`, `retention`은 이것을 `file_io`에서 import한다.
  - `operator_bootstrap`은 `_ordinary_path`와 `_REPARSE_POINT`를 지웠다. 이제 root(또는 manifest 경로)를 한 번 검사하고, 파일은 `no_reparse(path, below=root)`로 root까지만 검사한다.
  - `freeze`와 `verify_snapshot`은 첫 검사 전에 `_file_io()`를 부른다. 스냅숏 검증 전 import가 `file_io` 하나라는 조건은 그대로다.
- **후속: `sources`의 `replaced_by`·`revoked_at` — 지움.** 제품 전수 검색 결과, `sources` 기록을 만드는 곳(`engine.py`의 초기화와 source 제어, `initialization.py`)은 두 필드를 쓰지 않는다. 읽는 곳도 없다. `governance.py`의 같은 이름은 grant·위임 가족의 필드라 그대로다. 스키마 두 속성을 지웠다.
- **후속: `semantic_content_hash`의 `projection` — 지움.** 인자와 분기를 지웠다. 시험은 호출자가 투영한 dict를 넘기는 형태로 같은 성질을 단언한다.
- **후속: `GitStateStore`의 `getattr`/`hasattr` — 직접 접근으로 바꿈.**
  - 두 방어가 필요했던 까닭: `__init__`의 첫 `rev-parse` 호출이 `_git_dir`와 `_git_boundary`를 정하기 전에 `_git`을 거친다.
  - 이제 `__init__`이 그 호출 전에 두 속성을 작업 트리 값(`self.repository`, `self._repository_boundary`)으로 두고, Git 보고 뒤에 덮어쓴다. `_git`은 두 속성을 조건 없이 읽는다.
  - `__new__`로 만드는 시험 객체(`test_performance_repairs.SnapshotMetadataTests`)는 `_git`을 모의하므로 영향이 없다.

## 3. 공유 정의와 지운 공개 이름

**새로 만들거나 옮긴 공유 정의**

모두 `이음새-정본.md` 6절 표에 올렸다.

| 정의 | 위치 |
|---|---|
| `default_state_contract()`(설치 계약 공유) | `state_contract.py` |
| `RECORD_RULES` | `record_schemas/__init__.py` |
| `review_proposal`, `PROPOSAL_FIELDS`, `staged_review_candidate` | `review_cycle.py` |
| `no_reparse(path, *, below=None)` | `file_io.py`(`git_store.py`에서 옮김) |

`installed_checker`의 행은 `default_state_contract().family(root, name).checker`로 바꿨다. `issued_input`의 행은 새 인자와 메모 키로 바꿨다. 3절(봉인 artifact 대조)에는 규칙 두 항목을 더했다. 하나는 메모 키가 결과를 정하는 바이트의 식별을 담는다는 규칙이고, 다른 하나는 저장소 캐시가 소유 스레드 전용이라는 규칙이다.

시험 도우미 `installed_contract()`와 `with_validator(contract, root, name, validator)`를 `tests/research_fixtures.py`에 두었다.

**새 상태 비용**: 새 캐시·메모·수명 규칙은 없다. 바뀐 비용은 셋이다.

- `issued_input`은 메모 적중 때도 바이트를 읽고 sha256을 계산한다. 약 500 KB 파일에서 해시는 1 ms 미만이다. 해석(`load_json` 약 44 ms)과 사본(`deepcopy` 약 20 ms)이 더 크다.
- 가족 검증기는 부모와 다른 기록마다 `deepcopy(record)`를 받는다. 이제 실행과 외부 작업 등 가족 여덟이 이 비용을 치른다.
- `lifecycle` 기록이 바뀔 때마다 원래 입력 해시를 다시 계산한다. 전에는 `immutable_input`이 바뀔 때만 계산했다.

**지운 공개 이름**

- `state_contract`: `StateContract.default`, `StateContract.validation_generation`, `StateContract.installed_generation`, `check_schema`, `installed_checker`
- `repository`: `ResearchRepository.register_family`, `ResearchRepository.records`, `semantic_content_hash`의 `projection` 인자
- `git_store.no_reparse`(→ `file_io.no_reparse`)
- `state_checks.state_errors`
- `review_engine.ReviewEngineMixin._staged_review_candidate`(→ `review_cycle.staged_review_candidate`)
- `submission.issued_input`의 `git_dir` 인자
- `prepare_role_input` 반환값의 `original_bytes` 키
- 사설 이름: `repository._contract_key`, `repository._canonical_object`, `repository._artifact_lock`, `record_schemas._prior_rows`, `state_contract._default_template`, `operator_bootstrap._ordinary_path`와 `_REPARSE_POINT`, `review_engine._PROPOSAL_FIELDS`와 `_FORMAL_FIELDS`

## 4. 필요한 문서 변경

없음. 확인한 범위는 다음과 같다. 스킬 문서(`SKILL.md`, `README.md`, `GLOSSARY.md`, `references/`, `계약/`), `AGENTS.md`, `docs/`(동결 문서 `검사-경량화-이음새-계약.md`와 추적표 제외)에서 이번에 바꾼 이름과 사유 문자열을 검색했다. 검색한 이름은 `register_family`, `state_errors`, `installed_checker`, `no_reparse`, `StateSnapshot`, `gpgSign`, `review_input_basis`, `decision_basis`, `original_bytes`, `semantic_content_hash`, `StateContract.default`, `validation_generation`, `replaced_by`, `revoked_at`, 옮긴 점검 문구다. 검색에 걸린 것은 `references/CLI-실행-계약.md` 973행의 `decision_basis` 비교 설명 하나였고, 이 설명은 바뀐 형식과 맞는다.

## 5. 실행한 시험

모두 `scripts/`에서 `python -B run_tests.py <대상>`으로 실행했다. 한 번에 프로세스 하나였다.

1. 편집 확인: `test_state_contract_registration test_storage_validation test_repository test_state_checks test_file_io test_git_store test_operator_bootstrap` → 통과 73, 실패 0.
2. 편집 확인: `test_review_engine`의 staged 왕복 두 시험과 `test_redesign_STORAGE`의 staged 저장 시험 → 통과 3.
3. 인계 확인: `test_context_store test_lifecycle_engine test_review_cycle test_review_engine test_submission_flow test_submission_boundaries test_submission_tools test_engine test_redesign_STORAGE test_redesign_REVIEWS test_initialization_efficiency test_unicode_flow test_preflight test_observations test_performance_repairs.StorageValueTests`, 그리고 고친 시험 ID 5개(`test_redesign_CONTRACTS`의 두 시험, `test_redesign_PROFILES`, `test_redesign_SURFACE`, `test_redesign_TASKS`의 각 한 시험). `DO_MATH_KNOWLEDGE_TEST_LEAN`에 계약 6절의 경로를 주었다.
   - 결과: 통과 351, 건너뜀 1, 오류 30.
   - 오류 30건의 원인은 하나다. `research_fixtures.forget_repository_caches`가 `_ISSUED_INPUTS`의 새 키(sha256 바이트)를 경로로 읽다가 `TypeError`를 냈다. 이 작업의 변경 때문이며, 수정은 2절 STO-16에 적었다.
   - 건너뜀 1건은 `test_context_store...test_outside_symlink_is_reported_when_supported`다. 이 기계에 symlink 권한이 없다(WinError 1314). 환경 원인이다.
4. 3의 오류 30건 ID 재실행(수정 뒤) → 통과 30.
5. 인계 확인 보충: `test_decision_basis test_external` → 통과 22.

기계적 확인도 했다.

- 바꾼 `.py` 전부를 `py_compile`로 확인했다.
- 시험 모듈 135개를 `importlib`로 적재했다. 오류는 0이다.
- 바꾼 제품 모듈 17개를 각각 새 프로세스에서 단독 import했다. 순환은 없다.
- 지운 이름을 제품·시험·스킬 문서에서 grep했다. 남은 것은 `test_git_store.py:495` 하나다. 시험이 직접 조립하는 `git commit-tree` 명령의 `commit.gpgSign=false`라 제품과 무관하다.

변경 전부터 실패하던 시험은 확인하지 못했다. 기준 판본 실행이 없다.

**돌리지 않은 관련 시험**

- 템플릿을 쓰는 나머지 모듈: `forget_repository_caches` 변경의 소비자다. 3의 오류 30건이 모두 이 경로였고 재실행에서 통과했다.
- `test_redesign_STORAGE`를 뺀 대형 redesign 모듈의 나머지 시험.
- `default_state_contract`, `RECORD_RULES`, `staged_review_candidate`, `no_reparse`의 다른 소비자 모듈.

셋 모두 시험 지침 2절에 따라 통합 확인에 맡긴다.

## 6. 기능이나 시험 범위가 바뀐 것

- **실행 중 가족 등록(STO-01)**
  - 잃는 것: 외부 스키마 등록, 설치 가족의 검증기·참조 재등록 합성, 등록 뒤 캐시 무효화. 제품 호출자가 없던 기능이다.
  - 지운 시험: `test_state_contract_registration`의 `test_repository_registration_checks_an_outside_schema`, `test_only_an_unchanged_default_contract_counts_as_installed`, `test_initialization_efficiency`의 `test_parent_cache_is_invalidated_when_a_family_validator_changes`.
  - 시험 다섯은 새 계약으로 다시 썼다. 공유와 독립 계약, 한 번 등록과 스키마 사본, manifest memo, 닫힌 스키마·재등록 거부·검증기 실행, 기록 국소 생략이다.
  - 얻는 것: 저장소 객체마다의 계약 복사가 사라진다. 캐시 키와 게시 기준에서 세대 차원이 빠진다.
- **점검 → 저장 거부(STO-11)**
  - 외부 작업 사실 셋과 실행 `outcome` 값 위반은 이제 게시 전에 거부된다. 전에는 게시 뒤 `inspect_state`가 blocked로 보고했다.
  - `test_state_checks`는 같은 위반을 적재 거부로 단언하고, `cancelled` 사례와 outcome enum 사례를 더했다.
  - 점검 영역 격리 시험은 여전히 점검 전용인 실행 예약 소유자 결함으로 바꿨다.
  - 점검의 `checked_invariants` 문구가 바뀌었다(`task transfers and execution reservation owners`, `external execution mappings`).
- **입력 기록의 자기 digest(STO-10)**
  - 잃는 것: 저장된 기록 안의 변조 탐지. 결정 D3("변조 방어: 없앤다")과 같은 방향이다.
- **bool/정수 교환(STO-18·HIS-15)**
  - 부모와 같은 기록 안에서 bool과 정수가 바뀐 경우는 탐지하지 않는 공백으로 남았고, 코드에 이유를 적었다.
  - 소수는 이제 생긴 저장에서 거부된다. `test_performance_repairs.test_a_float_equal_to_the_parent_integer_is_still_rejected`를 더했다.
- **끝난 staged 검토의 전이 해시(STO-03)**
  - 사이클과 전이가 부모와 같으면 다시 계산하지 않는다. `test_review_engine`의 두 왕복 시험이 두 가지를 단언한다. 부모에 없는 검토는 해시하고, 두 번째 전이 뒤의 저장은 해시하지 않는다.
- **외부 작업 생산 경로(STO-11)**
  - `test_lifecycle_engine`에 두 단언을 더했다. 하나는 재시도 뒤 `handling` 부재와 기록 규칙 통과이고, 다른 하나는 전송 전 실패의 `transmitted=False`다.
- **정리 적격 판정(STO-07)**
  - 판정 결과는 제품 경로에서 같다. 시험 하나의 입력이 스키마에 없는 필드에서 실제 계약 값으로 바뀌었다.

## 7. 막힌 지점, 접근을 바꾼 지점, 예상과 달랐던 결과

- **STO-11의 전제가 원문과 달랐다.** 통합표는 "생산 경로가 규칙을 잠깐이라도 어기면 저장이 실패하기 시작한다"를 위험으로 적었다. 실제로 그런 경로가 둘 있었다. 하나는 재시도 뒤 `handling=reconciled`가 증거 없이 남는 경로이고, 다른 하나는 전송 전 예외에서 `transmitted`가 빠지는 경로다. 둘 다 점검은 결함으로 보고했지만, 기존 시험은 이 상태를 점검하지 않아 드러나지 않았다. 규칙을 옮기면서 두 생산자를 고쳤다.
- **STO-16의 방식을 바꿨다.** 처음에는 통합표 (가)의 blob OID 키를 검토했다. 이 안은 `sealed_bytes` 호출자 24곳의 인자를 바꾼다. 그런데 봉인 행 메모 둘은 키에 sha256이 있어 경로 재사용에 건전했다. 해시 없는 메모는 `_ISSUED_INPUTS` 하나뿐이었다. 그래서 이 메모의 키만 바이트 해시로 바꿨다. 메모를 지우는 안도 재어 보았다. 약 500 KB 파일에서 `load_json`(44 ms)이 `deepcopy`(20 ms)보다 느려, 메모를 지우면 오히려 느려지므로 택하지 않았다. (나)안은 계약 2절 7항의 HIS-03 불채택과 같은 안이라 쓰지 않았다.
- **STO-18·HIS-15의 선택은 측정으로 정했다.** 형까지 보는 비교는 `==`의 약 27배였고, 저장마다 두 번 돈다. 그래서 소수 거부(순회에 분기 하나)와 bool 공백의 명시를 택했다.
- **시험 기반의 경로 해석이 깨졌다.** `forget_repository_caches`가 `_ISSUED_INPUTS`의 키 첫 원소를 경로로 쓰고 있어 인계 확인에서 30건이 오류가 났다. TSB-14의 삭제를 기다리지 않고, 목록에서 이 메모만 뺐다.
- **셸 도구 문제.** 편집 도구의 셸이 여러 줄 heredoc 두 개를 따옴표 짝 오류로 거부했다. worktree 안 임시 폴더(`.sto-scratch/`)에 편집 스크립트를 두고 실행했으며, 커밋 전에 지웠다.
- **commit-harness와 작문 독해 절차는 적용하지 않았다.** 파견문이 기억 노드 생성을 금하므로 브랜치 커밋만 했다. `write-for-reader`의 `writing_flow.py` 독해·판정은 합의 파일과 상태 파일을 새로 쓴다. 그런데 파견은 쓰기를 이 산출 파일 하나로 제한하므로 실행하지 않았다. 별도 독해 검증을 거치지 않은 보고서다.

## 8. 다른 그룹 범위에서 발견한 문제

- **ENG, `engine.py`의 `_unchanged`.** 무변경 판정도 Python `==`다(HIS-15가 지적한 둘째 자리). 메모리 상태만 `1.0`이나 `True`로 바뀌고 다른 변화가 없으면 게시 자체가 생략된다. 이 경우 소수는 다음 실제 저장의 `seal_large`에서야 거부되고, bool 교환은 메모리에만 남는다.
- **ENG·RES, `semantic_content_hash`.** `projection` 인자를 지운 뒤 이 함수는 `exact_content_hash`의 별칭이다. 호출자는 `engine.py:326`과 `knowledge.py:22`다. 이름으로 목적을 구별할 가치가 없으면 호출자를 `exact_content_hash`로 바꾸고 함수를 지울 수 있다.
- **REV·ENG, `ReviewEngineMixin._identity_assessment`.** `review_cycle.identity_assessment`를 부르기만 하는 staticmethod가 남아 있다. 제품의 두 호출부(`review_engine.py`)와 시험(`test_redesign_KNOWLEDGE`, `test_redesign_STORAGE`)이 쓴다.
- **STO 검증 파일의 정정 사항, `state_checks.py:281`.** `from .academic_engine import current_solution_basis`는 점검 층이 엔진 층을 import하는 셋째 자리다. STO-03의 좁힌 범위는 저장 검증의 믹스인 의존만 다루므로 두었다.
- **TSB, `research_fixtures.forget_repository_caches`.** 이제 `VERIFIED_ARTIFACTS`, `_VALIDATED_READS`, `planning._VALID_ARTIFACTS` 셋만 비운다. 셋 모두 키에 내용 식별(sha256 또는 커밋 OID)이 있어, TSB-14가 이 함수를 지워도 결과가 달라지지 않는다. 함수의 docstring은 "keyed by the Git directory's path"라고 여전히 적는데, 이 서술은 사실과 다르다.
- **RES, `planning._VALID_ARTIFACTS`.** TSB-14의 기존 지적대로, 키에 형식 검증기(`validate_artifact`)가 들어 있지 않다. 이번 변경과는 무관하다.

# 결과-KC: 커널 단계 K-구조

## 1. 브랜치, 커밋, 바꾼 파일

- 브랜치: `c-kc` (worktree `C:/math-worktrees/c-kc`, 기준 `9b434f4`)
- 마지막 커밋: `791c406` (98개 파일, 추가 2, 수정 96)
- 경로는 모두 `.claude/skills/do-math/` 기준이다. `docs/`만 저장소 루트 기준이다.

**제품 (37)**
- 새 파일: `scripts/do_math/configuration.py`
- 수정: `scripts/do_math/` 아래 `academic.py`, `academic_engine.py`, `activities.py`, `cli.py`, `codex_adapter.py`(주석), `context_store.py`, `contracts.py`, `control_transport.py`, `decision_engine.py`, `engine.py`, `execution_lifecycle.py`, `execution_profiles.py`, `file_io.py`, `formal_preview.py`, `governance.py`, `governance_engine.py`, `integration.py`, `knowledge.py`, `knowledge_io.py`, `observations.py`, `payloads.py`, `planning.py`, `question_engine.py`, `record_schemas/__init__.py`, `reporting.py`, `repository.py`, `retention.py`, `review_cycle.py`, `review_engine.py`, `review_policy.py`, `scheduler.py`, `submission.py`, `task_contracts.py`, `task_scope.py`
- 스크립트: `scripts/probe_cli.py`, `scripts/run_tests.py`

**시험 (54)**
- import 이동만: 46개 모듈. 목록은 `git show --stat 791c406 -- '*/tests/*'`로 확인할 수 있다.
- 내용 수정: `test_contracts.py`(새 시험), `test_cli.py`, `test_redesign_ENGINE.py`, `research_fixtures.py`, `test_performance_repairs.py`, `test_reporting.py`, `test_redesign_SURFACE.py`, `test_session_scheduler.py`, `test_submission_flow.py`, `test_impact_bundle.py`, `test_redesign_CONTRACTS.py`, `test_lifecycle_engine.py`, `test_connection_repairs.py`, `test_governance_engine.py`, `test_redesign_TASKS.py`, `test_redesign_STORAGE.py`, `test_context_store.py`, `test_submission_tools.py`, `test_native_final_submission.py`(주석)

**문서 (7)**
- 새 문서: `scripts/이음새-정본.md`
- 수정: `AGENTS.md`, `scripts/tests/시험-지침.md`(경로 오기 2곳만)
- 역사 기록 표지: `docs/do-math/검사-경량화-이음새-계약.md`, `검사-경량화-설계-2026-09-26.md`, `검사-경량화-설계-2026-09-26-검사분류.md`, `경량화-설계-2026-09-26.md`

## 2. ID별 처분

- **ENG-10: 구현함.**
  - `DEFAULT_CONFIG`와 `validate_config`를 새 설정 모듈 `configuration.py`로, `json_safe`를 `payloads`로, `now`를 `file_io`로 옮겼다. `_repository`는 지웠다. `ResearchRepository(repository, instance_id)` 생성자가 이미 `default_state_contract()`를 기본값으로 쓰므로 그 생성자를 직접 부른다.
  - 역방향 import 7곳을 모두 없앴다. 대상은 `academic_engine:54`, `governance_engine:40`, `governance:837`, `scheduler:89`, `reporting:23`, `cli:18`, `probe_cli:10`이다. `governance`의 import는 함수 안에 남는다. `record_schemas.schemas`가 `governance`를 import하므로, 최상단으로 올리면 순환이 생기기 때문이다. 이제 그 import의 대상은 엔진이 아니라 `configuration`이다.
  - `cli:401`·`:427`의 함수 안 `query_records`·`read_record` import는 최상단 import로 합쳤다.
  - 시험 46개 모듈의 import를 소유 모듈로 바꿨다.
- **ENG-18: 구현함.** 엔진의 함수 안 import 24건이 이제 0건이다(AST로 확인). 이 가운데 3건(`control_contracts`, `record_schemas`, `platform`)은 `validate_config`와 함께 `configuration`의 최상단 import가 되었다. `launch.termination_confirmed`는 이미 최상단에 있던 모듈 import를 쓴다. 각 대상 모듈을 새 프로세스에서 import해 `do_math.engine`이 적재되지 않음을 확인했다.
- **ENG-09: 구현함.** 비공개 결합 7곳을 모두 없앴다.
  - `ResearchRepository.first_descendant(parent, head)`를 두고 `ResearchRepository._git`를 지웠다.
  - 정리 보관 조립은 `retention.archive_run`으로 옮겼다. 엔진에는 게시와 `mark_artifact_verified`만 남는다.
  - `knowledge_io.lookup_definition`, `question_engine.resolve_pointer`, `ObservationTracker.fact`를 공개 이름으로 바꿨다.
  - `grep -nE "\b(store|retention|knowledge_io|candidate)\._[a-z]|question_engine import _" engine.py` 결과는 0건이다.
- **HIS-04: 구현함.** 스키마 빌더가 `file_io.json_copy`, 곧 JSON 왕복 사본을 돌려준다. `identify_schema`를 거치는 `with_integration_schema`, `action_schema`, `schema_for`가 여기에 든다. 국소 방어 두 곳도 정리했다. `review_cycle.research_schema`의 필드별 사본 도우미와 `review_engine`의 재결합 주석은 지웠고, 두 곳은 이제 제자리에서 대입한다.
- **REV-23: 구현함.**
  - `extension_schema`, `disposition_schema`, `impact_review_response_schema`, `stage_schema`, `research_schema`, `research_request_schema`가 사본을 돌려준다. 같은 규칙이 성립하도록 `governance.interpretation_schema`와 `record_schemas.config_schema`에도 적용했다. `config_schema`는 전역 `TEXT`와 `RECORDS["capacity_constraints"]`를 그대로 싣고 있었다.
  - 규칙은 `contracts` 모듈 설명과 정본 문서 5절에 적었다.
  - 새 시험 `test_contracts.ContractTests.test_schema_builders_return_copies_that_share_no_node`는 빌더 28개 반환값의 모든 dict·list가 두 번 나오지 않고 `do_math.*` 모듈 전역 노드와 `is`로 같지 않음을 단언한다. 수정 전에는 빌더 26개에서 실패했다(TDD).
  - 역할 스키마 46개의 digest가 기준 `9b434f4`와 같음을 `probe_cli --skill-only` 비교로 확인했다.
- **REV-06: 구현함.** `submission`의 세 곳(`read_sealed_submission`, `issued_input`, `summarize_snapshot_checks`)과 `planning.py:541`이 이제 `read_artifact(path, snapshot)`으로 부른다. `engine._evaluation_context_for`의 어댑터 서명도 `(path, commit)`으로 바꿨다. 엔진의 뒤집기 람다 9개와 `retention`으로 넘기는 동등 람다 1개를 `self.store.read`로 바꿨다.
- **REV-18: 구현함(영역 안).**
  - `execution_profiles.RESEARCH_PRODUCER_ROLES`와 `PLANNING_ROLES`(frozenset)를 새로 두었다.
  - `submission.PRODUCERS`·`PLANNERS`, `integration.PRODUCERS`를 지우고 리터럴 5곳을 이 이름으로 바꿨다. 대상은 `contracts`, `decision_engine`, `task_scope` 3곳이다.
  - 영역 밖 29행은 8절에 적었다.
- **HIS-12: 구현함. (b)를 골랐다.**
  - (b)가 코드 변경 없이 닫힌다. (a)는 `sealed_bytes`에 콜백 인자를 더하고 `payloads.decode`의 길이 비교와 정규성 건너뛰기를 다시 짜야 한다.
  - 정본 문서 3절에 `artifact_verified`·`mark_artifact_verified`를 `sealed_bytes` 밖에서 직접 쓰는 곳 넷을 적었다. `payloads.decode`는 등록된 변종이다. `context_store.verify_manifest_artifacts`는 거르기만 하고 대조는 `sealed_bytes`로 한다. `ResearchRepository._validate_artifact_evidence`는 정본 모듈 안에 있다. `engine._maintenance_cleanup`은 게시 뒤 기록만 한다. "새로 늘리지 않는다"는 규칙도 함께 적었다.
- **영역 밖 관찰, 비어 있지 않은 텍스트 검사: 구현함.**
  - `file_io.require_text`와 `file_io.distinct_texts`를 두었다.
  - 텍스트 도우미 7개를 바꿨다. `governance:462`, `knowledge:24`, `knowledge_io:89`, `activities:16`, `task_contracts:65`, `execution_lifecycle:23`은 정본으로 교체했다. `control_transport:78`은 NUL 금지를 더한 감싸기로 남겼다(다른 규칙이다).
  - 목록 도우미 3개를 교체했다: `governance:53`, `academic:11`, `review_policy:16`.
  - `retention.py:50`의 `_strings`는 값 안의 문자열을 모두 내놓는 순회기라 다른 개념이므로 그대로 두었다.
- **영역 밖 관찰, `context_store` 비공개 경로 규칙: 구현함.**
  - 공개 정본 다섯으로 바꿨다: `safe_path`, `read_stable`, `is_excluded`, `is_reparse`, `relative_path`.
  - 쓰는 모듈 다섯을 바꿨다: `submission`, `observations`, `retention`, `control_transport`, `formal_preview`. 시험 3개도 바꿨다.
  - `observations`의 함수 안 `read_stable` import는 최상단으로 올렸다.
- **경로 오기 4곳: 구현함.** `run_tests.py`의 docstring과 280행, `시험-지침.md`의 19행과 69행을 고쳤다.
- **HIS-01: 구현함.**
  - `scripts/이음새-정본.md`를 새로 썼다. 원칙, 1~5절 규칙, 6절 표로 이루어진다. 표는 옛 11절의 78행 전부에 이번 정본을 더했다.
  - `AGENTS.md`에 원칙 한 항목을 더했다.
  - 주석 12곳을 `이음새-정본.md §3`(S3 11곳)과 `§2`(R22 1곳)로 고쳤다.
- **HIS-05: 구현함.** 이음새 계약 첫머리에 역사 기록 표지를 두고, 현행 정본을 옮긴 곳을 안내했다. 본문은 동결했다.
- **HIS-06: 구현함.** 세 설계·분류 문서에 표지를 두었다. `검사-경량화-설계` 54행과 429행에는 작업 공간이 삭제되었다는 괄호를 더했다.

처분별 건수는 구현함 14, 구현하지 않음 0, 조건 불성립 0, 끝내지 못함 0이다.

## 3. 새 공유 정의, 지운 공개 이름

새 공유 정의는 모두 `scripts/이음새-정본.md`에 등록했다.

| 정본 | 위치 | 등록 위치 |
|---|---|---|
| `DEFAULT_CONFIG`, `validate_config` | `configuration.py` | 6절 |
| `now()`, `require_text`, `distinct_texts`, `json_copy` | `file_io.py` | 6절, `json_copy`는 5절 |
| `json_safe` | `payloads.py` | 6절 |
| `ResearchRepository(repository, instance_id)`(기본 계약 생성자), `ResearchRepository.first_descendant` | `repository.py` | 6절 |
| `read_artifact(path, snapshot)` 콜백 규약 | `repository.py`(`ResearchRepository.read`) | 6절 |
| `RESEARCH_PRODUCER_ROLES`, `PLANNING_ROLES` | `execution_profiles.py` | 6절 |
| `safe_path`, `relative_path`, `is_excluded`, `is_reparse`, `read_stable` | `context_store.py` | 6절 |
| `archive_run` | `retention.py` | 6절 |
| `lookup_definition` | `knowledge_io.py` | 6절 |
| `resolve_pointer` | `question_engine.py` | 6절 |
| `ObservationTracker.fact` | `observations.py` | 6절 |

정본 문서의 1~4절에는 옛 계약 1~3절 규칙과 4절 상태 판본 키 규칙을 현행 내용으로 옮겼다. 3절에는 `artifact_verified`, `verify_artifact`, `mark_artifact_verified`를 `sealed_bytes`와 함께 올렸다.

지운 공개 이름:
- `engine.DEFAULT_CONFIG`, `validate_config`, `json_safe`, `now`의 정의. 엔진 모듈에는 import한 이름으로 남아 있고, `do_math.engine.now`를 패치하는 시험은 계속 동작한다.
- `submission.PRODUCERS`, `submission.PLANNERS`, `integration.PRODUCERS`

비공개 이름에서 지운 것:
- `engine._repository`, `ResearchRepository._git`, `reporting._repository`
- `question_engine._pointer`, `knowledge_io._lookup_definition`, `ObservationTracker._fact`는 공개 이름으로 바뀌었다.
- 로컬 사본 `governance._require_text`·`_strings`, `knowledge._require_text`, `knowledge_io._text`, `activities._text`, `task_contracts._text`, `execution_lifecycle._nonempty`, `academic._strings`, `review_policy._strings`
- `context_store._safe_path`·`_read_stable`·`_excluded`·`_is_reparse`·`_relative`는 공개 이름으로 바뀌었다.

## 4. 필요한 문서 변경

- `references/CLI-실행-계약.md` 146행: "기본값의 기계 정본은 `scripts/do_math/engine.py`의 `DEFAULT_CONFIG`다"를 `scripts/do_math/configuration.py`의 `DEFAULT_CONFIG`로 바꿔야 한다.
- 선택 사항: `README.md`의 개발·시험 안내 부근(528행 근처)에 `scripts/이음새-정본.md`를 가리키는 한 줄을 둘 수 있다. `AGENTS.md`는 이미 가리킨다.
- `.agents/` 미러는 새 문서 `scripts/이음새-정본.md`를 포함해 통합자가 재생성해야 한다.

## 5. 실행한 시험

- **편집 확인**
  - 바꾼 `.py` 91개를 `python -m py_compile`로 컴파일했고 모두 통과했다.
  - `scripts/tests`의 `test_*.py` 135개 모듈을 `importlib.import_module`로 적재했다. 실패는 0이다.
  - `do_math` 모든 모듈을 각각 새 프로세스에서 import했다. 실패는 0이다.
  - 패키지 없는 `control_transport` 직접 적재도 통과했다.
  - AST로 정의되지 않은 이름을 훑었다. 바뀐 파일에서는 0건이다. `test_external.py`의 결과는 원래 있던 `import *`에서 나온 것이다.
- **새 시험**: `python scripts/run_tests.py test_contracts.ContractTests.test_schema_builders_return_copies_that_share_no_node`
  - 수정 전: 실패. 빌더 26개가 노드를 공유했다.
  - 수정 후: 1 통과.
- **넓은 인계 실행 `kc-run1`**(grep으로 잡은 81개 모듈): **통합자 지시로 중단, 미실행.** 통합 확인은 통합자가 한다. 중단 전에 끝난 부분에서 원인을 정적으로 분석하고 고친 것은 다음과 같다.
  - `test_cli.CliBoundaryTests.test_query_defaults_and_explicit_filters_reach_consumers_in_both_interfaces`(2개 subTest)와 `test_cli`의 `read_record` 패치: 이 시험들은 `do_math.engine.query_records`를 패치했다. `cli`가 최상단 import로 이름을 묶게 되어, 시험을 `do_math.cli.*` 패치로 고쳤다.
  - `test_redesign_ENGINE.ContinuationConnections.test_bundle_live_prior_hash_and_transitive_impact_are_required`, `test_redesign_ENGINE.ImpactReviewRouting.test_shared_candidate_applies_actual_domain_revision_without_mutating_preview_source`: 람다가 사라져 `self.store.read`를 인자 구성 시점에 읽게 되었고, 시험 대역 `NoRepository`에는 `read`가 없었다. `NoRepository`와 `research_fixtures.StateStore`에 읽으면 `AssertionError`를 내는 `read`를 더했다. 제품에는 예외를 넣지 않았다.
  - `test_redesign_EVIDENCE.TraceabilityCheckerTests.test_full_trace_is_structurally_valid_not_an_execution_pass`: "archive directory unavailable"로 실패했다. worktree에 보관소가 없어서 생기는 환경 원인이며(시험 지침 2절) 이 변경과 무관하다. 이 시험은 사용자 결정 2에 따라 다른 그룹이 지울 대상이다.
- **고친 시험의 ID 단위 실행**: `python scripts/run_tests.py test_impact_bundle.ImpactBundleTests <ID 26개>`. 편집한 행을 담은 시험 함수 전부이며, 목록은 REV-06 콜백 순서, 패치 대상, `fact`, `read_stable`, 저장소 생성자를 고친 시험이다. 결과는 32 통과, 실패 0, 오류 0이다(21+6+1+4).
- **마지막 확인**: `python scripts/run_tests.py test_contracts test_cli.CliBoundaryTests`는 23 통과다. `python scripts/probe_cli.py --skill-only`는 `verified`였고, 역할 스키마 digest 46개가 기준 `9b434f4`와 같았다.
- **돌리지 않은 관련 시험**: 이름이 겹치는 나머지 모듈이다. 커널이 바꾼 이름은 거의 모든 시험에 나오므로 이 범위는 사실상 전체다. 통합자 지시에 따라 병합 뒤 통합 확인에 맡긴다.

## 6. 기능이나 시험 범위가 바뀐 것

- **`review_policy`의 문자열 목록 검사**
  - 이유: 정본 `distinct_texts`로 합쳤다.
  - 잃는 것: 공백만 있는 perspective·judge slot·source ref 문자열을 받아들이던 동작. 이런 문자열은 이제 거부된다.
  - 얻는 것: "비어 있지 않은 텍스트" 규칙이 모든 모듈에서 같아진다.
- **오류 문구**
  - `knowledge`의 "must be nonempty", `activities`·`execution_lifecycle`의 "must be a nonempty string"이 "must be nonempty text"로 바뀌었다.
  - `academic`·`governance`·`review_policy`의 목록 문구는 "requires [a nonempty list of ]distinct nonempty strings"로 바뀌었다. `review_policy`의 "duplicate X"도 이 문구로 합쳐졌다.
  - `control_transport`는 빈 값에 "must be nonempty text", NUL에 "must be NUL-free"를 낸다.
  - 문구를 단언하는 시험은 없음을 grep으로 확인했다. 오류 종류(`ValueError`)는 같다.
- **스키마 빌더 반환값**: 공유 노드가 없는 JSON 왕복 사본이 된다. 튜플은 리스트가 된다(예: `config_schema`의 `required`). 스키마 내용 digest는 같다(5절).
- **시험 대역**: `NoRepository`와 `StateStore`에 `read`가 생겼다. 이 `read`로 읽으면 시험 결함으로 실패한다.
- **`test_performance_repairs`의 `_control_reader` 시험**: 패치 대상을 `ResearchRepository`로 바꿨다. 단언은 그대로다.

## 7. 막힌 지점, 접근을 바꾼 지점, 예상과 달랐던 결과

- **설정 정본의 위치**
  - 예상: 표의 제안인 `record_schemas` 옆에 둔다.
  - 달랐던 점: `record_schemas.schemas`가 `governance`를 import하고, `record_schemas/__init__`를 `control_contracts`가 import하는 순환 위험이 있었다. K-저장이 `record_schemas`를 동시에 고친다는 점도 걸렸다.
  - 결정: 설정 전용 모듈 `configuration.py`에 두었다. 이 모듈이 표가 허용한 "설정 전용 모듈"이다.
- **`_repository` 처리**: 이미 `ResearchRepository`의 기본 인자로 같은 계약이 생긴다는 점을 확인했다. 그래서 새 생성자를 만들지 않고 `_repository`를 지웠다.
- **`json_copy`의 위치**: 처음에는 `contracts`에 두려 했다. 그러나 `governance`, `record_schemas`, `scheduled_operator` 등 아래 모듈도 써야 하므로 최하위 `file_io`에 두었다.
- **REV-06의 부작용**: 람다를 `self.store.read`로 바꾸자 속성 조회가 앞당겨졌고, `read`가 없는 시험 대역 둘이 드러났다. 제품은 그대로 두고 대역을 고쳤다.
- **cli의 최상단 import**: `do_math.engine.query_records`를 패치하던 시험이 효과를 잃었다. 시험을 현행 결합 위치 `do_math.cli.*`로 고쳤다.
- **write-for-reader 적용 범위**: 작성 전에 압축 진술과 경중을 정했다.
  - 압축 진술: 두 모듈 이상이 쓰는 규칙은 정본 하나를 import해 쓴다. 없으면 import 그래프 아래의 소유 모듈에 하나 만들고 표에 올린다. 봉인 artifact 대조와 스키마 빌더처럼 쓰는 방법까지 정해진 규칙은 1~5절을 따른다.
  - 경중: 무거운 것은 원칙·소유 모듈 기준, 3절의 소비 규칙과 직접 사용 네 곳, 5절의 `deepcopy` 대신 `json_copy`를 쓰는 이유다. 가벼운 것은 표 행이다.
  - 수행하지 않은 것: 독해 단계(`writing_flow.py read`)다. 이 단계는 `codex exec` 공급자 CLI를 부르므로 계약 2절 1항(모델 호출 금지)과 충돌하고, worktree 밖에 파일을 만든다. 합의·독자 파일도 만들지 않았다. 대신 `경중_배분.md`의 "독해를 실행하지 않는 글" 점검을 했다. 가장 긴 세 대목(6절 표, 3절, 5절)이 모두 무거운 것이거나 조회용 표임을 확인했다.
- **커밋**: `commit-harness`의 기억 노드는 만들지 않았다. main 작업 트리의 `기억/`은 계약 5절에 따라 읽기 전용이다. 통합자가 결정화할 대상이다.

## 8. 다른 그룹 범위에서 발견한 문제

- **REV-18 영역 밖 리터럴 29행**: engine 7, scheduler 8, revision_engine 4, context_store 4, model_policy 3, planning 2, governance 1이다. 이 행들은 이제 `execution_profiles.RESEARCH_PRODUCER_ROLES`·`PLANNING_ROLES`로 바꿀 수 있다. `not review_cycle_id` 조건은 함께 보존해야 한다. 소유 ID가 없다.
- **`now()`와 같은 식의 사본**: `observations.utc_now`(247행, 시험 `test_observations.py:172`가 패치함)와 인라인 `datetime.now(timezone.utc).isoformat()` 20여 곳이 있다. 위치는 `codex_adapter`, `execution_window`, `external`, `knowledge_io`, `maintenance_gate`, `model_runner`, `operation_trace`, `review_engine`이다. 정본 `file_io.now`로 모을 수 있다.
- **정본 표에 없는 메모**: 통합표 2절의 STO→HIS 관찰에 따르면 9b434f4가 더한 `retain_reads`, `_ARTIFACT_FACTS`(`repository._known_artifact`·`_learn_artifact`), 프로세스 안 객체 쓰기는 이번에도 정본 표에 올리지 않았다. 담당 ID가 없어서다. 올릴지와 3절의 번들 불변 전제를 함께 적을지는 STO 판단이 필요하다.
- **`cli.py`의 비공개 호출**: `ResearchRepository._resolve_snapshot`을 부른다(`read` 명령). ENG-09와 같은 성격의 비공개 결합이다.
- **`task_scope.py:195`**: 최상단에서 이미 import한 `planning.contract_hash`를 함수 안에서 다시 import한다. ENG-18과 같은 성격이다.
- **`control_transport._TEXT`**: `{"type":"string","minLength":1}`로, `contracts.TEXT`(`pattern \S`)와 규칙이 다르다. worker가 패키지 없이 적재하는 모듈이라 따로 두었을 수 있다. 같은 뜻인지 IO 판단이 필요하다.
- **K-저장과 겹칠 수 있는 파일**: `record_schemas/__init__.py`의 `config_schema` 반환 1행과 import 1행을 바꿨다. 엔진 최상단 import 블록도 여러 행을 바꿨다. 병합 때 확인이 필요하다.

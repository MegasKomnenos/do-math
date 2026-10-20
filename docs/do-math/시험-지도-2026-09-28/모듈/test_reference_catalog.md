# test_reference_catalog

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_reference_catalog.py` (86행) |
| 클래스 / 테스트 | 1 / 4 |
| 시험 대상 제품 코드 | `do_math/submission.py`의 `reference_catalog`, `validate_reference`(내부 `_validate_reference`, `_reference_index`), `supplied_locators`, `reported_references`(내부 `reference_aliases`, `normalize_reference`), `payload_issues`; `do_math/contracts.py`의 `schema_for` |
| 사용하는 픽스처 모듈 | 없음 |
| 격리 표지 | 없음 |
| 시작 상태 | 1단(순수 함수 직접 호출). 저장소·엔진 없이 사전(dict) 맥락과 `tempfile.TemporaryDirectory` 작업 공간만 쓴다 |

## 목적

모듈 docstring은 "참조 힌트는 가시성의 투영일 뿐, 추가 권한이 아니다"라고 밝힌다. 역할에게 주는 참조 목록(`reference_catalog`)은 고정 입력이 이미 보여 주는 참조를 같은 검사기(`_validate_reference`)로 걸러 투영한 것이다. 따라서 그 목록 자체가 새 참조를 인용 가능하게 만들어서는 안 된다. 제품 쪽 근거는 `submission.py`의 `supplied_locators` 안 주석 "The projection cannot grant itself authority."(키 `reference_catalog`를 건너뜀)와 `reference_catalog` docstring "Project the same reference checker used by producers and receivers."다. 이 모듈은 네 가지를 검사한다. 첫째, 큰 매니페스트를 한 번만 색인한다. 둘째, 현재 레코드의 별칭과 과거 artifact 경로를 구별한다. 셋째, 고정 조사(`supplemental_research`)의 목록은 그 출처 집합으로 좁혀진다. 넷째, 작업 공간 루트를 가리키는 참조는 제출 문제(issue)로 돌아온다.

## 모듈 수준 요소

- 행 8: 스킬의 `scripts/` 폴더(`Path(__file__).resolve().parents[1]`)를 `sys.path` 앞에 넣어 `do_math`를 import하는 공통 머리다.
- 행 9: `reference_catalog`, `reported_references`, `validate_reference`를 모듈 수준에서 import한다. `submission` 모듈 자체와 `contracts`는 각 테스트 안에서 import한다.
- 행 85–86: 직접 실행하면 `unittest.main()`으로 이 모듈의 시험을 돈다.

## CatalogTests (행 12–82)

`unittest.TestCase`를 그대로 상속한다. 클래스 표지, 설정 훅, 도우미 메서드가 없다. 모든 테스트가 자기 안에서 임시 폴더와 맥락 사전을 만든다.

### `test_large_manifest_is_indexed_once_without_authorizing_the_projection` (행 13–30)
- 성질: 2000개 파일 매니페스트의 참조 목록은 위치자(locator) 색인을 한 번만 만들어 얻고, 목록에 적힌 투영(`reference_catalog` 키)이나 해석되지 않는 proposal 좌표는 목록에 들어가지 않으며, 매니페스트에서 빠진 경로는 검증을 통과하지 못한다.
- 준비: 임시 폴더를 작업 공간 `root`로 쓴다. 맥락은 네 키를 갖는다. `manifest.files`에는 `environment/module-{i}.olean` 경로 2000개가 있다. `reference_catalog`에는 `{"path": "invented"}`가 있다. `proposal`은 `{"valid": {}}`이다. `other`에는 `{"ref": "proposal:missing"}`이 있다.
- 실행: `submission.supplied_locators`를 `patch.object(..., wraps=...)`로 감싼 채 `reference_catalog(context, root)`를 부르고 행의 `value` 집합을 얻는다. 이어서 매니페스트의 마지막 파일을 `pop`한 뒤 `validate_reference(paths[-1], context, root)`를 부른다.
- 단언: 감싼 `supplied_locators`의 `call_count`가 1이다. 제품의 `reference_catalog`는 `_reference_index`를 한 번 불러 얻은 `known`과 `locators`를 모든 후보에 재사용한다. 2000개 경로가 모두 `value` 집합에 들어 있다. `'invented'`는 들어 있지 않다. `supplied_locators`가 `reference_catalog` 키를 건너뛰기 때문이다. `'proposal:missing'`도 들어 있지 않다. 이 값은 `other[].ref`를 통해 위치자로 수집되지만, `_validate_reference`가 위치자 대조보다 먼저 `proposal:` 좌표를 `review_cycle.proposal_value`로 해석하고, 거기서 `ValueError`("unknown proposal source coordinate")가 나서 후보에서 빠진다. 마지막 `validate_reference`는 `ValueError`를 던진다. 예외 유형만 확인하고 메시지는 보지 않는다.
- 대역: `patch.object(submission, 'supplied_locators', wraps=...)`. 동작은 바꾸지 않고 호출 횟수만 센다.

### `test_current_aliases_and_historical_bytes_remain_distinct` (행 32–54)
- 성질: 현재 레코드를 가리키는 입력 경로와 출처 이름은 현재 레코드 ID로 정규화되고, 과거 실행의 artifact 경로는 현재 레코드의 별칭이 되지 않은 채 과거 증거로 남는다. 참조 목록에 적힌 값은 인용 권한을 주지 않는다.
- 준비: 임시 작업 공간에 `input/knowledge/K.json`(내용 `{}`)을 쓴다. 맥락은 다섯 키를 갖는다. `action.role`은 `research_plan`이다. `knowledge_catalog`에는 ID `K`, 경로 `input/knowledge/K.json`인 행이 있다. `tasks`에는 `T`가 있다. `sources`에는 ID `S`, 이름 `paper`, 경로 `research/source/paper`, 로컬 경로 `input/sources/paper`인 출처가 있다. `previous_execution`은 ID `E`이고 `result_source.artifact_ref`가 `runtime/artifacts/old/result.json`이다.
- 실행: `reference_catalog(context, root)`로 행을 얻고, 모든 행의 `value`를 `validate_reference`로 다시 검증한다. 이어서 `reported_references`에 `used_sources` 네 값을 넘긴다. 네 값은 `workspace:input/knowledge/K.json`, `source:paper`, `S`, `runtime/artifacts/old/result.json`이다. 마지막으로 맥락의 `reference_catalog`를 `[{"value": "unprovided", "path": "unprovided"}]`로 바꾸고 `validate_reference("unprovided", ...)`를 부른다.
- 단언: 목록의 모든 값이 `validate_reference`를 통과한다. 곧 목록과 검사기가 같은 규칙을 쓴다. `input/knowledge/K.json` 행의 `canonical_ref`는 `"K"`다. `runtime/artifacts/old/result.json` 행의 `kind`는 `"historical_artifact"`다. 제품은 `ARTIFACT_ROOT`(`git_store.py`의 `"runtime/artifacts/"`)로 시작하는 경로를 이렇게 분류한다. `reported_references`의 결과는 `["K", "paper", "runtime/artifacts/old/result.json"]`와 같다. `workspace:` 접두를 떼고 별칭을 적용하므로, `source:paper`와 `S`가 모두 `paper`가 되어 중복이 제거되고 과거 artifact 경로는 그대로 남는다. 바꾼 뒤의 `validate_reference("unprovided")`는 `ValueError`를 던진다. 예외 유형만 확인한다.
- 대역: 없음.
- 비고: 제품 `normalize_reference`의 주석 "Historical artifact paths are not aliases of the current record."가 이 성질의 근거다.

### `test_fixed_question_catalog_only_exposes_its_source_set` (행 56–61)
- 성질: 검토 주기에 고정된 보충 조사(`supplemental_research`)의 참조 목록은 그 조사의 출처 집합만 드러낸다.
- 준비: 맥락은 세 키를 갖는다. `action`은 `{"role": "supplemental_research", "review_cycle_id": "R"}`이다. `knowledge_catalog`에는 `allowed`와 `other`가 있다. `review_research.sources`에는 `{"ref": "allowed"}`가 있다.
- 실행: `reference_catalog(context, Path(directory))`.
- 단언: 행 `value`의 목록이 정확히 `["allowed"]`다. 제품은 역할이 `supplemental_research`이고 `review_research`가 있으면 후보 집합을 `review_research.sources[].ref`로 바꾼다. 그래서 `knowledge_catalog`에 있는 `other`는 빠진다.
- 대역: 없음.

### `test_workspace_root_reference_returns_a_submission_issue` (행 63–82)
- 성질: 작업 공간 루트 자체를 가리키는 참조는 예외로 새지 않고, 해당 필드 좌표를 가진 제출 문제 하나로 보고된다. 보존된 작업 공간 파일을 가리키는 참조는 통과한다.
- 준비: 임시 작업 공간을 쓴다. 맥락의 `action`은 `{'id': 'AC-check', 'role': 'maintenance'}`이고, `execution_id`는 `'EX-check'`, `snapshot`은 `'fixed'`다. 유지보수 출력은 다섯 필드를 갖는다: `summary`, `used_sources`(빈 목록), `questions`, `report`, `remaining_work`. 스키마는 `contracts.schema_for('maintenance')`다.
- 실행: 참조 네 가지(`'.'`, `'./'`, `'workspace:.'`, `'workspace:./'`)를 하나씩 `used_sources`에 넣어 `submission.payload_issues(output, schema, context, {}, root)`를 부른다. 이어서 작업 공간에 `evidence.txt`를 쓰고 `used_sources=['workspace:evidence.txt']`로 다시 부른다.
- 단언: 네 경우 각각 문제가 정확히 하나다. 그 문제의 `path`는 `'output/used_sources/0'`이고, `message`는 `'unsafe relative path'`를 포함한다. 거부 사유를 메시지 조각까지 고정한다. 이 문구는 `context_store.relative_path`가 `.`, `..`, 빈 부분이나 부분이 없는 경로에 대해 던지는 오류에서 온다. 마지막 호출의 결과는 빈 목록 `[]`이다.
- 대역: 없음.
- 비고: `subTest(reference=...)` 네 케이스는 `'.'`, `'./'`, `'workspace:.'`, `'workspace:./'`다.

## 관계

- 같은 제품 기능의 다른 층: `reference_catalog`는 `install_tools`가 작업 공간을 준비할 때 `context["reference_catalog"]`에 싣는다. 그 설치 경로는 `test_preparation_cache`가 본다. 참조 검사가 실제 제출 검사 안에서 돌 때의 동작은 `test_submission_checks`가 본다. `payload_issues`의 전체 필드 규칙은 이 모듈이 아니라 제출 검사 쪽 모듈들이 넓게 다룬다.
- 픽스처 의존: 없다. 모든 입력을 테스트 안에서 사전으로 적는다.
- 이 모듈에만 있는 도우미: 없다.
- 겹치거나 보완하는 시험: 이 모듈의 첫 두 테스트는 "투영은 권한이 아니다"를 서로 다른 방식으로 확인한다. 첫 테스트는 맥락에 미리 있던 `reference_catalog` 키가 목록에 반영되지 않음을 보고, 둘째 테스트는 그 키를 바꾼 뒤 `validate_reference`가 거부함을 본다.

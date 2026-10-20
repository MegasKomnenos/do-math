# test_preparation_cache

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_preparation_cache.py` (70행) |
| 클래스 / 테스트 | 1 / 3 |
| 시험 대상 제품 코드 | `do_math/submission.py`의 `install_tools`, `_support_archive`(`functools.lru_cache(maxsize=2)`); `do_math/file_io.py`의 `cached_sha256`, `sha256_file`, `RACY_NS`, `fingerprint_settled`; `do_math/preflight.py`의 `_check_schema_pair`(`lru_cache(maxsize=128)`) |
| 사용하는 픽스처 모듈 | 없음 |
| 격리 표지 | 없음 |
| 시작 상태 | 1단(제품 함수를 임시 폴더 위에서 직접 호출). 저장소·엔진 없음 |

## 목적

모듈 docstring은 "코드와 스키마를 정확히 같은 값으로만 캐시하며, 가변 입력을 재사용하거나 편집을 숨기지 않는다"라고 밝힌다. 시험 대상은 두 캐시다. 첫째는 `install_tools`가 작업 공간마다 싣는 검사 도구 압축본 `input/tools/submission-support.zip`이다. `_support_archive`는 상대 이름과 digest가 정확히 같을 때만 압축을 재사용하고(docstring "Reuse compression only for exactly the same relative names and digests."), 코드의 digest는 `cached_sha256`가 파일 지문(fingerprint)으로 캐시한다. 둘째는 `preflight._check_schema_pair`의 스키마 형식 검사 캐시다. 이 모듈은 세 가지를 확인한다. 같은 코드는 한 번만 압축하되 작업 공간마다 제 맥락을 갖는다. 바뀌지 않은 코드는 다시 읽지 않지만 편집은 새 바이트로 나간다. 유효 스키마의 캐시가 바뀐 무효 스키마를 숨기지 않는다.

## 모듈 수준 요소

- 행 12: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리다.
- 행 13: `do_math`에서 `submission`과 `preflight`를 import한다.
- 행 69–70: 직접 실행하면 `unittest.main()`으로 이 모듈의 시험을 돈다.

## PreparationCacheTests (행 16–66)

`unittest.TestCase`를 그대로 상속한다. 표지, 설정 훅, 도우미 메서드가 없다. 앞의 두 테스트는 `submission._support_archive.cache_clear()`로 프로세스 전역 캐시를 비운 뒤 시작한다. 두 테스트는 `patch.object(submission, '__file__', ...)`로 제품의 패키지 위치를 임시 폴더로 돌린다. `install_tools`는 `Path(__file__).resolve().parent`를 패키지로 보고 그 아래의 `*.py`(`engine.py`와 `*_engine.py` 제외)를 압축하므로, 이렇게 하면 임시 `checker.py` 하나만 든 패키지가 압축 대상이 된다.

### `test_same_code_reuses_compression_but_each_workspace_keeps_its_own_context` (행 17–32)
- 성질: 같은 코드 판본을 두 작업 공간에 설치하면 압축은 한 번만 하고 두 압축본의 바이트는 같지만, 각 작업 공간의 `context.json`은 제 맥락을 담는다.
- 준비: 임시 `package/checker.py`(내용 `edition = 1\n`)를 둔다. 맥락 둘은 `action.role='maintenance'`이고 `snapshot`이 각각 `'first'`, `'second'`다. 캐시를 비운다.
- 실행: `submission.__file__`을 `package/submission.py`로 바꾸고 `submission.zipfile.ZipFile`을 `wraps=zipfile.ZipFile`로 감싼다. 그 상태에서 `install_tools(root/'left', 맥락1, {'type': 'object'}, 1024)`와 `install_tools(root/'right', 맥락2, ...)`를 차례로 부른다.
- 단언: 감싼 `ZipFile`의 `call_count`가 1이다. 두 번째 설치는 `_support_archive`의 `lru_cache`에 적중해 압축하지 않았다. `left`와 `right`의 `input/tools/submission-support.zip` 바이트가 같다. 각 작업 공간의 `input/submission/context.json`의 `snapshot`이 각각 `'first'`, `'second'`다.
- 대역: `patch.object(submission, '__file__', ...)`(패키지 위치 전환), `patch.object(submission.zipfile, 'ZipFile', wraps=zipfile.ZipFile)`(호출 횟수 계수).

### `test_unchanged_code_is_not_reread_and_an_edit_ships_new_bytes` (행 34–59)
- 성질: 지문이 안정된(settled) 코드는 두 번째 설치에서 내용을 다시 해시하지 않고, 같은 크기의 편집이라도 지문이 바뀌면 새 바이트가 압축본에 실린다.
- 준비: 임시 `package/checker.py`(`edition = 1\n`)의 수정·접근 시각을 `time.time_ns() - 10 * file_io.RACY_NS`로 되돌린다. 캐시를 비운다.
- 실행: `submission.__file__`을 바꾸고 `file_io.RACY_NS`를 0으로 패치한 상태에서 네 단계를 거친다.
  1. `first`에 설치한다.
  2. `file_io.sha256_file`을 `side_effect=AssertionError('unchanged code was reread')`로 패치하고 `again`에 설치한다.
  3. 파일을 `edition = 2\n`(같은 크기)으로 덮어쓰고, 수정 시각을 `settled + 10**9`로 바꾼다.
  4. `second`에 설치한다.
- 단언: 두 번째 설치가 `AssertionError` 없이 끝난다. 곧 `cached_sha256`가 지문 적중으로 `sha256_file`을 부르지 않았다. `first`와 `again`의 압축본 바이트는 같고, `first`와 `second`는 다르다. `second` 압축본의 `do_math/checker.py` 항목이 `b'edition = 2\n'`이다.
- 대역: `patch.object(submission, '__file__', ...)`, `patch.object(file_io, 'RACY_NS', 0)`, `patch.object(file_io, 'sha256_file', side_effect=AssertionError(...))`.
- 비고: 행 44의 주석은 `RACY_NS`를 0으로 두는 이유를 이렇게 설명한다. 새로 만든 파일의 생성 시각은 되돌릴 수 없으므로, 지나간 지문은 모두 안정된 것으로 본다. 제품의 지문(`stat_fingerprint`)은 크기, 수정 시각, 생성 시각 세 값이다. `fingerprint_settled`는 두 시각 가운데 늦은 것이 `RACY_NS`(기본 2초)보다 오래되었을 때만 지문으로 내용을 대신한다(`file_io.py` 행 173–181의 racy-git 주석). `utime`은 생성 시각을 되돌리지 못하므로 `RACY_NS`를 0으로 둔다. 편집 뒤 내용의 크기는 같고, 수정 시각을 1초 옮겨 지문을 바꾼다. "다시 읽지 않음"은 `sha256_file` 호출 금지로만 확인한다. `_support_archive` 안의 `read_bytes`는 패치하지 않으며, 그 경로는 `lru_cache` 적중으로 건너뛴다.

### `test_valid_schema_cache_does_not_hide_a_changed_invalid_schema` (행 61–66)
- 성질: 유효 스키마의 형식 검사 결과를 캐시해도, 다른 무효 스키마 텍스트는 검사를 받아 `SchemaError`로 거부된다.
- 준비: 스키마 텍스트 둘. 유효한 `'{"type":"object"}'`와 무효한 `'{"type":"not-a-json-schema-type"}'`.
- 실행: `preflight._check_schema_pair`에 유효 텍스트를 두 번, 무효 텍스트를 한 번 넘긴다.
- 단언: 유효 텍스트 두 번은 예외 없이 돌아온다. 무효 텍스트는 `jsonschema.exceptions.SchemaError`를 던진다. 예외 유형만 확인한다.
- 대역: 없음.
- 비고: 이 테스트는 캐시 적중 여부를 단언하지 않는다. 캐시 키가 스키마 텍스트 자체이므로(`lru_cache`), 서로 다른 텍스트가 같은 캐시 칸을 쓰지 않는다는 것만 확인한다. `_check_schema_pair`는 Draft 2020-12와 Draft 7(최상위 `$schema`, `x-contract-id` 제거) 두 검사기로 스키마를 검사한다.

## 관계

- 같은 제품 기능의 다른 층: `install_tools`가 싣는 `reference_catalog`는 `test_reference_catalog`가 본다. 설치된 압축본으로 실제 생산자 검사를 돌리는 경로는 `test_submission_checks`의 `test_installed_zip_runs_and_seals_real_producer_check`가 본다. `preflight`의 설치 구조 검사(`inspect_bundle`) 전체는 이 모듈의 범위가 아니다.
- 픽스처 의존: 없다.
- 이 모듈에만 있는 도우미: 없다.
- 겹치거나 보완하는 시험: 첫 테스트는 압축 캐시(`_support_archive`)를, 둘째 테스트는 digest 캐시(`cached_sha256`)와 편집 반영을 본다. 두 테스트가 함께 "같은 이름과 digest일 때만 재사용한다"는 계약의 양쪽을 확인한다.

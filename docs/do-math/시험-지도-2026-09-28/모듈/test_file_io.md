# test_file_io

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_file_io.py` (100행) |
| 클래스 / 테스트 | 2 / 8 |
| 시험 대상 제품 코드 | `do_math/file_io.py`의 `atomic_replace`, `_replace_once`(대역 대상), `shared_reader`, `read_bytes_shared`, `write_bytes_atomic`, `file_fingerprint`, `cached_sha256`, `sha256_file`(대역 대상), `RACY_NS`(패치 대상); `do_math/repository.py`의 `VERIFIED_ARTIFACTS`, `verify_artifact`, `artifact_verified`. `fingerprint_settled`는 import만 하고 직접 부르지 않는다 |
| 사용하는 픽스처 모듈 | 없음 |
| 격리 표지 | 없음 |
| 시작 상태 | 1단(순수 함수 직접 호출). 파일 시험은 `tempfile.TemporaryDirectory`의 실제 파일을 쓴다. 저장소·엔진·자식 프로세스는 쓰지 않는다 |

## 목적

모듈 docstring은 없다. 두 클래스가 `file_io.py`의 두 영역을 나눠 맡는다. `MetadataPublicationTests`는 모듈 docstring "Atomic local metadata publication under concurrent Windows readers"(`file_io.py` 1–5행)가 말하는 계약을 본다. 곧 한 판본을 열어 둔 독자가 있어도 경로의 원자적 교체가 막히지 않는다. 재시도는 같은 rename만 되풀이한다("Retries repeat only the same rename, never the operation described by the file."). 재시도 횟수에는 상한이 있다. `FingerprintTests`는 `cached_sha256`(346–357행)의 지문 캐시 규칙과 `repository.verify_artifact`/`artifact_verified`(53–71행)의 프로세스 단위 검증 기억을 본다.

제품 좌표는 다음과 같다. `atomic_replace`(20–29행)는 지연 `(0,.01,.025,.05,.1,.2)` 여섯 번을 시도하고, `winerror`가 `{5,32,33}`에 들지 않거나 마지막 시도이면 예외를 그대로 올린다. `_replace_once`(54–78행)는 Windows에서 `SetFileInformationByHandle`에 `FileRenameInfoEx`와 `REPLACE_IF_EXISTS | POSIX_SEMANTICS`를 준다. `shared_reader`(81–98행)는 공유 모드 7로 연다. `write_bytes_atomic`(106–117행)은 같은 폴더에 `<이름>.<무작위>.tmp` 임시 파일을 쓴 뒤 `atomic_replace`로 교체한다. `cached_sha256`는 지문(`stat_fingerprint`: 크기, 수정 시각, 생성 시각)이 같으면 저장된 해시를 돌려준다. 지문이 읽는 동안 그대로이고 `fingerprint_settled`(179–181행, `RACY_NS=2_000_000_000` 초과로 오래됨)일 때만 캐시에 넣는다.

## 모듈 수준 요소

- 행 7: `sys.path.insert(0, ...parents[1])`로 `scripts/`를 경로 맨 앞에 넣는다. 다른 모듈과 달리 이미 들어 있는지 확인하지 않는다.
- 행 8–10: 시험 대상 import. `fingerprint_settled`는 import되지만 본문에서 쓰이지 않는다.
- 행 100: 직접 실행하면 `unittest.main()`으로 돈다.

## MetadataPublicationTests (행 13–59)

`unittest.TestCase`를 상속한다. 표지, 클래스 속성, 설정·정리 훅, 도우미가 없다. 파일 시험은 각자 `tempfile.TemporaryDirectory`를 연다.

### `test_reader_keeps_one_version_without_blocking_atomic_replacement` (행 14–21)
- 성질: 한 판본을 연 독자가 있는 동안에도 원자적 쓰기가 경로를 교체하고, 독자는 연 판본을 끝까지 읽으며, 임시 파일은 남지 않는다.
- 준비: 임시 폴더의 `state.json`에 `b'old'`.
- 실행: `shared_reader(path)`로 연 상태에서 `write_bytes_atomic(path, b'new')`, 이어 `previous.read()`와 `read_bytes_shared(path)`.
- 단언: 열린 핸들은 `b'old'`를, 새로 읽은 경로는 `b'new'`를 돌려준다. 블록을 나온 뒤 폴더에 `*.tmp` 파일이 없다.
- 대역: 없음.
- 비고: Windows에서는 실제 `CreateFileW`와 `SetFileInformationByHandle` 경로를 지난다(`os.name=='nt'`). 다른 OS에서는 `open`과 `os.replace`로 같은 성질을 본다.

### `test_sharing_failure_retries_only_the_same_rename` (행 23–29)
- 성질: 공유 위반(`winerror=32`)이 나면 같은 인자의 rename 하나만 다시 시도한다.
- 준비: `winerror=32`를 단 `PermissionError('busy')`.
- 실행: `atomic_replace('pending', 'current')`. 실제 파일은 없다.
- 단언: `_replace_once`가 두 번 불리고, 첫째와 둘째 호출의 인자(`call_args_list[0] == [1]`)가 같다.
- 대역: `do_math.file_io._replace_once`를 `side_effect=[error, None]`로, `do_math.file_io.time.sleep`을 빈 대역으로 패치한다.

### `test_permanent_failure_is_bounded_and_unrelated_errors_are_not_retried` (행 31–39)
- 성질: 재시도할 수 있는 오류가 계속되면 정해진 횟수 뒤에 그 오류를 올리고, 재시도 대상이 아닌 오류는 한 번에 올린다.
- 준비: `winerror=5`(접근 거부)를 단 `PermissionError`, 그리고 `winerror`가 없는 `FileNotFoundError('missing')`.
- 실행: 두 경우 각각 `atomic_replace('pending', 'current')`.
- 단언: 첫 경우 `PermissionError`가 나고 `_replace_once` 호출은 6회다. 이 값은 제품의 지연 목록 길이와 같다. 둘째 경우 `FileNotFoundError`가 나고 호출은 1회다. 예외 유형만 보고 메시지는 보지 않는다.
- 대역: `_replace_once`의 `side_effect` 패치. 첫 경우에만 `time.sleep`을 패치한다. 둘째 경우는 첫 시도의 지연이 0이라 잠들지 않는다.
- 비고: 이름의 "unrelated errors"는 `winerror`가 없는 오류 하나로 확인한다. `winerror` 33은 이 모듈에서 쓰지 않는다.

### `test_missing_read_is_still_absence` (행 41–43)
- 성질: 공유 독자로 없는 파일을 읽으면 부재가 `FileNotFoundError`로 나타난다.
- 준비: 빈 임시 폴더의 `missing` 경로.
- 실행: `read_bytes_shared(path)`.
- 단언: `FileNotFoundError`가 난다(유형만). Windows에서는 `ctypes.WinError`가 errno 2에 대응하는 하위 클래스로 올라온다.
- 대역: 없음.

### `test_unicode_long_paths_and_changing_lengths_preserve_exact_target` (행 45–59)
- 성질: 한글·이모지가 든 긴 경로와 길이가 바뀌는 내용에서도 원자적 쓰기가 정확히 그 대상을 교체하고, 열린 독자는 옛 판본을 유지하며, 다른 이름의 파일을 만들지 않는다.
- 준비: `('한글🌐'*25)/('nested'*20)` 하위 폴더. 이름 세 개 `'a'`, `'다른이름🌐.json'`, `'long-name-'*10+'.json'`.
- 실행: 이름마다 `b'old'*800`을 쓴 뒤 `shared_reader`로 열어 둔 채 `b'x'`, `b''`, `b'new'*4000`을 차례로 `write_bytes_atomic`로 쓰고, 그때마다 `read_bytes_shared`로 읽는다.
- 단언: 매번 읽은 값이 방금 쓴 값과 같고, 열린 독자의 `read()`는 `b'old'*800`이다. 끝에 폴더의 이름 집합이 세 이름과 정확히 같으므로 임시 파일이나 다른 이름이 남지 않는다.
- 대역: 없음.
- 비고: `subTest(name=...)` 케이스 세 개. 경로 길이는 Windows의 `\\?\` 접두(`_windows_path`, 48–51행)가 있어야 다룰 수 있는 길이다.

## FingerprintTests (행 62–97)

`unittest.TestCase`를 상속한다. 표지, 클래스 속성, 설정·정리 훅, 도우미가 없다.

### `test_fingerprint_change_alone_triggers_rehash` (행 63–77)
- 성질: `cached_sha256`는 지문이 같으면 다시 읽지 않고, 지문이 바뀌면 다시 해시한다. 크기와 시각을 모두 보존한 내용 변경은 잡지 못한다(문서화된 한계).
- 준비: `RACY_NS`를 0으로 패치해 오래됨 판정을 끈다. `tool.exe`에 `b'one'`을 쓰고 수정 시각을 10초 전(`time.time_ns()-10**10`)으로 되돌린다.
- 실행: `cached_sha256`를 네 번 부른다. 첫 호출, `sha256_file` 대역 아래 둘째 호출, `b'two!'`로 바꾸고 수정 시각을 1ns 옮긴 뒤 셋째 호출, 크기와 시각을 그대로 두고 `b'TWO!'`로 바꾼 뒤 넷째 호출.
- 단언: 첫째는 `sha256(b'one')`이다. 둘째도 같은 값이고 `sha256_file`이 불리지 않는다(`assert_not_called`). 변경 뒤 `file_fingerprint`가 이전 값과 다르고, 셋째는 `sha256(b'two!')`다. 넷째는 여전히 `sha256(b'two!')`다. 곧 옛 캐시가 반환되며, 원문 주석 "Documented limit: content changed with size and times preserved."가 이를 밝힌다. 제품 근거는 `stat_fingerprint` docstring(151–160행)의 "A rewrite that preserves all three values is not detected"다.
- 대역: `do_math.file_io.RACY_NS`를 0으로, 둘째 호출에서 `do_math.file_io.sha256_file`을 패치한다.
- 비고: 이름의 "fingerprint change alone"은 "지문 변경만이 다시 해시하게 한다"로 읽으면 단언과 맞는다. 지문이 그대로면 다시 해시하지 않고(둘째 호출), 지문이 바뀌면 다시 해시하며(셋째 호출), 지문을 보존한 내용 변경은 다시 해시하지 않는다(넷째 호출). 셋째 호출 전의 변경은 크기(3→4)와 수정 시각을 함께 바꾸므로, 지문의 한 성분만 바꾼 경우는 따로 보지 않는다.

### `test_recent_fingerprint_is_not_cached` (행 79–85)
- 성질: 방금 쓴 파일의 지문은 오래되지 않았으므로 캐시에 들지 않고, 다음 호출에서 다시 해시한다.
- 준비: 새로 쓴 `fresh.json`(`b'a'`). `RACY_NS`는 기본값 2초다.
- 실행: `cached_sha256` 두 번. 둘째는 `sha256_file` 대역 아래에서 부른다.
- 단언: 둘째 호출에서 `sha256_file`이 정확히 한 번 불린다(`assert_called_once`).
- 대역: `do_math.file_io.sha256_file`을 `return_value='x'`로 패치한다.
- 비고: 제품 주석(173–176행)은 이 규칙을 Windows 파일 시각 틱(약 15.6ms) 때문에 생기는 racy-git 문제로 설명한다. 첫 호출이 파일을 쓴 뒤 2초 안에 일어나야 성립한다. 첫 호출이 그보다 늦으면 지문이 오래된 것으로 판정되어 캐시에 들고, 둘째 호출은 다시 해시하지 않는다. 첫 호출이 캐시에 넣지 않았으면 둘째 호출은 시각과 무관하게 다시 해시한다.

### `test_verified_artifact_is_scoped_to_repository_and_hash` (행 87–97)
- 성질: 산출물 검증 기억은 저장소(`git_dir`), 경로, 해시의 조합에 묶이고, 크기를 주면 크기도 맞아야 하며, 해시가 틀린 바이트는 기억하지 않는다.
- 준비: `raw=b'artifact'`와 그 SHA-256. 저장소 식별자 `'g1'`, `'g2'`, 경로 `'runtime/artifacts/a/x'`.
- 실행: `verify_artifact`를 틀린 바이트(`b'other'`)로, 이어 맞는 바이트와 크기로 부른다. 그 사이사이 `artifact_verified`를 부른다.
- 단언: 틀린 바이트는 `ValueError`를 낸다(유형만. 제품 메시지는 `"artifact evidence missing or hash differs: "`+경로). 그 뒤 `g1` 기억이 없다. 맞는 검증 뒤 `g1`은 참, `g2`는 거짓이다. 크기 `len(raw)`는 참, `len(raw)+1`은 거짓이다. 주석 "A row declaring another size is not the matched row."가 마지막 단언의 뜻을 밝힌다.
- 대역: 없음. 끝에 `VERIFIED_ARTIFACTS.pop(('g1', 'runtime/artifacts/a/x', digest), None)`으로 프로세스 전역 기억을 직접 치운다.
- 비고: 전역 사전을 다루므로 앞선 시험이 같은 키를 남기면 둘째 단언(`assertFalse`)이 영향을 받는다. 정리는 시험 끝에서만 하며 `try/finally`가 아니므로 중간 실패 때에는 남는다.

## 관계

- 원자적 교체의 소비자 쪽 실패 처리는 `test_operation_trace`가 `do_math.operation_trace.atomic_replace`를 패치해 검사한다. 이 모듈은 교체 자체의 재시도 규칙을 본다.
- `VERIFIED_ARTIFACTS`는 `test_native_final_submission`과 `test_submission_flow`가 `patch.dict(..., clear=True)`로 비워서 저장소 봉인 경로에서 쓴다. 이 모듈은 기억의 열쇠 범위만 1단에서 본다.
- 같은 `file_io.py`의 `json_digest`와 `compact_json_bytes`는 `test_json_digests`가 다룬다.
- 픽스처 모듈을 쓰지 않는다. 도우미도 없다.

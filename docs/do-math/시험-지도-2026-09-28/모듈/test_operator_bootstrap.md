# test_operator_bootstrap

| 항목 | 값 |
|---|---|
| 조각 | `host` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_operator_bootstrap.py` (84행) |
| 클래스 / 테스트 | 1 / 4 |
| 시험 대상 제품 코드 | 스크립트 `scripts/operator_bootstrap.py`(168행)의 `main`(행 140–164: `--freeze`, `--bootstrap-info`, 그 밖의 명령을 동결 사본의 `scheduled_operator.main`에 넘김), `freeze`(행 92–137), `verify_snapshot`(행 48 이하), 상수 `MARKS`(`bootstrap-fingerprints.json`); 스크립트 `scripts/do_math.py`(진입점); `do_math/file_io.py`의 `sha256_file`, `RACY_NS` |
| 사용하는 픽스처 모듈 | 없음 |
| 격리 표지 | 없음 |
| 시작 상태 | 네 단 밖. 세 시험은 스킬 폴더 전체를 임시 폴더에 복사하거나 동결 사본을 만들고 실제 자식 Python 프로세스로 진입점을 실행한다. 한 시험은 `operator_bootstrap`을 프로세스 안에서 import해 부른다 |

## 목적

원문에는 모듈 docstring이 없다. 제품 `operator_bootstrap.py`의 docstring은 "검증된 감독자를 그 수리 대상과 독립적으로 동결하고 시작한다"이다. 운영자(감독자)는 설치 결함을 고치는 주체이므로, 설치의 엔진이나 공유 모듈이 깨져도 스스로는 떠야 한다. `freeze`는 설치 파일 전체를 해시한 내용 주소 사본을 작업 공간의 `operator/bootstrap/<식별자>` 아래에 만들고(docstring "연구 상태나 작업은 바꾸지 않는다"), 동결 사본의 진입점은 적재 전에 매니페스트의 해시로 모든 파일을 검증한 뒤 자기 옆의 `do_math` 패키지만 import한다(행 157–158 주석, 행 159–161의 경로 삽입과 import). 검증은 파일 지문(fingerprint)이 바뀌지 않은 파일을 다시 해시하지 않도록 `MARKS` 파일에 확정된 지문을 캐시한다. 이 모듈은 엔진 import 실패 중의 감독자 시작, 살아 있는 설치의 손상에 대한 동결 사본의 독립성과 동결의 멱등성, 동결 코드 변경의 적재 전 거부, 지문 캐시에 의한 재해시 생략을 검사한다.

## 모듈 수준 요소

- 행 1–7: 표준 라이브러리만 import한다. `sys.path`를 모듈 수준에서 고치지 않는다(넷째 시험이 함수 안에서 고친다).
- 행 83–84: 직접 실행하면 `unittest.main()`.

## OperatorBootstrapTests (행 10–80)

`unittest.TestCase`를 그대로 상속한다. 표지·설정 훅·도우미·속성이 없다. 앞의 세 시험은 스킬 폴더(`Path(__file__).resolve().parents[2]`)를 기준으로 한다.

### `test_supervisor_starts_when_engine_cannot_be_imported` (행 11–26)
- 성질: 엔진 모듈에 문법 오류가 있어 일반 진입점은 실패해도, 운영자 부트스트랩 진입점은 시작되어 자기 명령 목록을 보여 준다.
- 준비: 스킬 폴더를 임시 `skill`로 복사하고(`__pycache__`, `*.pyc`, `.lake` 제외) `scripts/do_math/engine.py`를 `broken engine syntax !!!`로 덮어쓴다.
- 실행: 복사본의 `scripts/do_math.py --help`와 `scripts/operator_bootstrap.py --help`를 임시 폴더를 `cwd`로 각각 자식 Python으로 실행한다.
- 단언: 일반 진입점의 종료 코드가 0이 아니고 stderr에 `SyntaxError`가 있다(깨짐이 실제로 드러남을 확인하는 대조). 부트스트랩의 종료 코드가 0이고(실패 시 stderr) stdout에 `run-engine`이 있다.
- 대역: 없음. 손상된 엔진 파일이 결함 주입이다.
- 비고: 실제 자식 Python 프로세스 두 개와 스킬 폴더 전체 복사. 부트스트랩은 복사본에 매니페스트가 없으므로 살아 있는 모드로 돌며, `scheduled_operator`가 엔진을 늦게 import하므로 `--help`가 성공한다.

### `test_frozen_supervisor_survives_damage_to_live_shared_modules` (행 28–47)
- 성질: 동결은 같은 설치에 대해 같은 결과를 내고, 동결 사본은 살아 있는 설치의 공유 모듈이 손상되어도 시작되며, 자신이 동결한 설치 경로를 알고 있다.
- 준비: 스킬 폴더를 임시 `installation`으로 복사한다. 동결 명령 `[sys.executable, bootstrap, '--freeze', '--installation-root', live, '--workspace', 임시/workspace]`.
- 실행: 동결 명령을 두 번(`check=True`), 살아 있는 설치의 `scripts/do_math/repository.py`를 `damaged shared module !!!`로 덮어쓴 뒤 동결 진입점의 `--help`와 `--bootstrap-info`.
- 단언: 두 동결의 JSON 출력이 같다. 손상 뒤 동결 진입점 `--help`의 종료 코드가 0이다. `--bootstrap-info`의 `manifest.installation_root`가 살아 있는 설치의 resolve 경로다.
- 대역: 없음.
- 비고: 실제 자식 Python 네 개. 둘째 동결은 이미 있는 사본을 `verify_snapshot`으로 확인하고 같은 경로를 돌려준다(행 108–111).

### `test_changed_frozen_code_is_rejected_before_import` (행 49–62)
- 성질: 동결 사본의 코드가 바뀌면 진입점은 그 코드를 import하기 전에 해시 불일치로 거부한다.
- 준비: 실제 스킬 폴더를 설치 뿌리로 임시 작업 공간에 동결한다(`check=True`). 동결 사본의 `do_math/repository.py`를 `raise RuntimeError('unverified code executed')`로 바꾼다.
- 실행: 동결 진입점 `--help`를 자식 Python으로 실행한다.
- 단언: 종료 코드가 0이 아니다. stderr에 `bootstrap file hash mismatch`가 있고, `RuntimeError: unverified code executed`는 없다(바뀐 코드가 실행되지 않음).
- 대역: 없음.
- 비고: 이 시험은 복사본이 아니라 저장소의 실제 스킬 폴더를 동결 원천으로 쓴다. 쓰기는 임시 작업 공간 아래의 동결 사본에만 한다. 실제 자식 Python 두 개.

### `test_verified_frozen_files_are_rehashed_only_after_their_fingerprint_changes` (행 64–80)
- 성질: 한 번 검증된 동결 파일은 지문이 바뀌지 않는 한 다시 해시하지 않고, 지문이 바뀐 파일은 다시 해시해 불일치를 찾는다.
- 준비: 함수 안에서 `scripts/`를 `sys.path` 앞에 넣고 `operator_bootstrap`과 `do_math.file_io`를 import한다. `bootstrap.freeze(scripts.parent, 임시 폴더)`로 동결하고 매니페스트 경로를 얻는다.
- 실행: 아래 번호 단계에 적은 호출을 차례로 한다. 모든 단계는 `file_io.RACY_NS`를 0으로 패치한 채 진행한다.
- 단언: 각 단계의 단언은 아래 번호 단계에 함께 적는다. 단계 목록:
  1. `verify_snapshot(manifest)` 뒤 매니페스트 옆에 `MARKS` 파일이 있다.
  2. `file_io.sha256_file`을 `AssertionError('unchanged frozen file was rehashed')`로 패치하고 `verify_snapshot`을 다시 불러도 예외가 없다.
  3. 동결 사본의 `scripts/do_math/repository.py`를 `changed`로 바꾸고 `verify_snapshot`하면 `ValueError`(정규식 `bootstrap file hash mismatch`)다.
- 대역: `RACY_NS`와 `sha256_file` 패치.
- 비고: 주석(행 72)은 "새 사본은 생성 시각을 늙힐 수 없으므로 지난 지문을 모두 확정된 것으로 본다"고 `RACY_NS=0`의 이유를 밝힌다. 프로세스를 띄우지 않는다. 함수 안의 `sys.path.insert`는 시험 뒤에도 남는다.

## 관계

- 같은 제품 기능을 다른 층에서 보는 모듈: `test_operator`의 `test_real_probe_persists_failure_when_engine_has_syntax_error`는 같은 손상 엔진 상황에서 부트스트랩 `check --probe`가 실패를 보존하는지를 본다. `test_schedule_pythonw`는 예약 등록 전에 동결 JSON을 수집하는 어댑터를 본다. `test_installation_discovery`(`foundation` 조각)는 설치 파일 집합을 본다.
- 픽스처를 쓰지 않는다.
- 이 모듈에만 있는 도우미: 없음.
- 실제 외부 자원: 실제 자식 Python 프로세스 여덟 개와 스킬 폴더 복사 두 번. 표지가 없어 `run_tests.py`의 Job 격리 없이 돈다.

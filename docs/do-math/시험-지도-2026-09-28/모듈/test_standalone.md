# test_standalone

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_standalone.py` (62행) |
| 클래스 / 테스트 | 1 / 3 |
| 시험 대상 제품 코드 | `do_math/formal.py`의 `discover_lean`, `toolchain_root`; `scripts/probe_cli.py`의 `--skill-only`(→ `do_math/preflight.py`의 `inspect_bundle`); `scripts/setup_lean.py`의 `main`(설치 모드) |
| 사용하는 픽스처 모듈 | 없음 |
| 격리 표지 | 없음 |
| 시작 상태 | 1단 둘(패치한 함수 호출)과 실제 자식 프로세스 하나(복사한 스킬에서 `probe_cli.py` 실행) |

## 목적

모듈 docstring은 "The installed skill must work without its author's repository documents."다. 설치된 스킬은 저자 저장소의 `docs/`나 저장소 루트 구조 없이도 동작해야 한다. 이 모듈은 세 가지를 확인한다. 저장소 루트 없이 얕게 설치되었을 때 Lean 탐색이 조용히 `None`을 돌려준다. 스킬 폴더만 복사해도 자기 구조 점검이 통과한다. Lean 준비가 실패하면 이전의 준비 완료 표지를 남기지 않는다.

## 모듈 수준 요소

- 행 13: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 넣는다.
- 행 14: `from do_math import formal`.
- 행 61–62: 직접 실행하면 `unittest.main()`을 부른다.

## StandaloneTests (행 17–58)

`unittest.TestCase`를 그대로 상속한다. 표지, 클래스 속성, 설정 훅, 도우미가 없다.

### `test_shallow_installation_without_lean_reports_unavailable` (행 18–21)
- 성질: 저장소 루트 아래에 있지 않은 얕은 설치에서, PATH에 `lean`도 없으면 Lean 탐색 결과가 `None`이다.
- 준비: `formal.__file__`을 현재 드라이브 루트 바로 아래의 `do-math/scripts/do_math/formal.py`로 바꾼다. 이 경로의 조상은 넷뿐이어서 `toolchain_root()`가 `None`을 돌려준다(제품 조건 `len(parents) > 5`, `formal.py` 행 190–193).
- 실행: `formal.discover_lean()`.
- 단언: 반환값이 `None`이다.
- 대역: `patch.object(formal, "__file__", ...)`, `patch.object(formal.shutil, "which", return_value=None)`.
- 비고: 제품의 두 분기, 곧 준비 표지가 있는 Mathlib 프로젝트를 쓰는 분기와 휴대용 `lean.exe`를 쓰는 분기는 루트가 없으므로 이 시험에서 돌지 않는다.

### `test_copied_skill_checks_itself_without_repository_documents` (행 23–36)
- 성질: 스킬 폴더만 저장소 밖으로 복사해도 `probe_cli.py --skill-only`가 설치 구조 점검을 `verified`로 마친다.
- 준비: 스킬 폴더(`tests/`의 두 단계 위)를 임시 폴더 아래 `do-math/`로 복사한다. `__pycache__`는 뺀다.
- 실행: 실제 자식 프로세스 `sys.executable <복사본>/scripts/probe_cli.py --skill-only`를 `cwd=임시 루트`, `timeout=30`으로 실행한다.
- 단언: 종료 코드가 0이다(실패하면 stderr를 메시지로 보인다). stdout의 JSON에서 `status == "verified"`, `scope == "installed_skill_structure"`다. 임시 루트에 `docs` 폴더가 없다.
- 대역: 없음.
- 비고: 실제 자식 프로세스와 스킬 전체 복사를 쓴다. 인터프리터 시작과 설치본 import가 검사 대상에 들기 때문이다. 시간 상한은 `subprocess.run`의 30초다. 마지막 단언의 `docs` 부재는 복사가 저장소 문서를 가져오지 않았다는 전제의 확인이다. 점검 자체가 `docs`를 읽지 않았다는 것은 종료 코드 0과 `verified`에서 간접적으로 나온다. `inspect_bundle`의 반환은 `not_verified`에 `document_semantics`, `runtime_execution`, `research_roles`, `Lean`, `research_efficacy`를 명시한다(`preflight.py` 행 81–85). 이 시험도 그 범위만 확인한다.

### `test_failed_lean_preparation_invalidates_the_previous_ready_marker` (행 38–58)
- 성질: Lean 설치 모드가 실행 오류로 끝나면 종료 코드 2와 JSON `status: "error"`를 내고, 이전에 있던 준비 완료 표지(`READY_MARKER`)를 남기지 않는다.
- 준비: 임시 루트 아래 `setup_lean.portable_bin(root)/lean.exe`에 가짜 바이트를 쓴다(내려받기 분기를 건너뛰게 한다). `setup_lean.mathlib_project(root)`를 만들고, 그 안의 `READY_MARKER`에 `LEAN_VERSION`을 적는다.
- 실행: 인자 없는 설치 모드(`sys.argv=['setup_lean.py']`)로 `setup_lean.main()`. 제품은 먼저 표지를 지우고(`unlink`) `install(root)`로 들어간다. `lake-manifest.json`이 없으므로 `run([lake, "update"], ...)`을 부르고, 패치된 `run`이 `CalledProcessError`를 던진다.
- 단언: `SystemExit`의 코드가 2다. stdout의 JSON에서 `status == "error"`다. 표지 파일이 없다.
- 대역: `patch.object(sys, 'argv', ...)`, `patch.object(setup_lean, 'toolchain_root', return_value=root)`, `patch.object(setup_lean, 'run', side_effect=subprocess.CalledProcessError(1, ['lake', 'update']))`. stdout은 `redirect_stdout(io.StringIO())`로 받는다.
- 비고: 원문 주석(행 55)이 의도를 밝힌다: "An execution error is exit code 2 with a JSON status, and never leaves a ready marker." `setup_lean.py`의 docstring이 정한 종료 코드 규약(0 성공, 1 거부·실패·불일치, 2 실행 오류)과 같다. `install`은 `PROJECT_FILES`를 임시 프로젝트에 실제로 쓰지만, 이 시험은 그 파일을 단언하지 않는다.

## 관계

- `probe_cli.py`의 다른 모드와 `preflight`의 세부 점검은 `host` 조각의 `test_probe_cli`, `test_preflight`가 검사한다.
- `setup_lean.py`의 기록 모드(`--verify-only`, `--rerecord`, `--check-contents`)와 대표 컴파일은 `test_environment_validation`이 함수 단위로 검사한다. 이 모듈은 설치 모드의 실패 처리만 본다.
- `discover_lean`의 1초 재탐색 주기는 `test_installation_discovery`가 엔진 쪽에서 검사한다.
- 픽스처 모듈을 쓰지 않는다.

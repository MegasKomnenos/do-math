# test_background_processes

| 항목 | 값 |
|---|---|
| 조각 | `host` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_background_processes.py` (151행) |
| 클래스 / 테스트 | 1 / 3 |
| 시험 대상 제품 코드 | `do_math/git_store.py`의 `GitStateStore._git`(Git 자식 프로세스 실행, 행 527 이하), `GitStateStore.publish`, `read_bytes`, `_git_text`; `do_math/` 전체의 `subprocess.run`·`subprocess.Popen` 호출 자리(정적 검사) |
| 사용하는 픽스처 모듈 | 없음 |
| 격리 표지 | 없음(`test_group` 미사용). 대신 두 시험이 메서드 단위 `unittest.skipUnless`로 Windows 조건을 건다 |
| 시작 상태 | 네 단 밖. 두 시험은 임시 폴더에 실제 Git 저장소를 만들고 `pythonw.exe` 자식 프로세스 안에서 제품 코드를 돌린다. 한 시험은 제품 원문을 AST로 읽는 정적 검사다 |

## 목적

모듈 docstring은 "pythonw로 띄운 백그라운드 명령은 콘솔을 할당하지 않아야 한다"고 밝힌다. do-math는 예약 작업으로 `pythonw.exe` 아래에서 돌 수 있고, 콘솔이 없는 부모가 콘솔 프로그램(`git.exe` 등)을 띄우면 Windows는 기본으로 새 콘솔 창을 만든다. 제품은 이를 막기 위해 모든 자식 프로세스 호출에 `creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)`을 준다(예: `git_store.py` 행 553). 이 모듈은 그 약속을 세 방향에서 확인한다. 실제 Git 후손 프로세스에 콘솔과 보이는 창이 없는지 커널 API로 관찰하고, 제품의 모든 호출 자리가 `creationflags`를 명시하는지 정적으로 훑고, pythonw 아래에서 Git 저장이 콘솔 없이 이루어지면서 이진 자료와 부모 커밋을 보존하는지 본다.

## 모듈 수준 요소

- `SCRIPTS` (행 12): 스킬의 `scripts/` 폴더. 이 모듈은 `sys.path`를 고치지 않는다. 대신 자식 스크립트에 첫 인자로 넘겨 자식이 `sys.path.insert(0, sys.argv[1])`로 `do_math`를 import하게 하고, 정적 검사에서는 `SCRIPTS / 'do_math'`의 `*.py`를 훑는 기준으로 쓴다.
- 행 150–151: 직접 실행하면 `unittest.main()`을 부른다.

## BackgroundProcessTests (행 15–147)

`unittest.TestCase`를 그대로 상속한다. 클래스 표지·설정 훅·도우미·속성이 없다. 각 시험이 자기 임시 폴더를 `tempfile.TemporaryDirectory`로 만든다.

### `test_real_git_descendants_are_observed_without_visible_windows` (행 18–85)
- 성질: 제품이 Git을 띄울 때 쓰는 실제 인자 그대로 띄운 Git과 그 후손 프로세스에는 콘솔이 붙지 않고 보이는 창도 없다. 그리고 이 관찰 방법은 콘솔이 있는 경우를 실제로 검출한다(양성 대조).
- 준비: 임시 폴더에 자식 스크립트 `actual_git_probe.py`를 쓴다. 자식은 `git init -q`(자식 프로세스, `CREATE_NO_WINDOW`)로 `repo`를 만들고 `GitStateStore(repo, 'RI-00000000000000000000000000')`를 연다. 네 단 밖(실제 Git 저장소, 실제 자식 프로세스).
- 실행: 부모 시험이 `pythonw.exe`(현재 해석기 옆)로 자식 스크립트를 `SCRIPTS`, 임시 폴더 인자와 함께 실행한다(`capture_output`, `text`, `timeout=60`, `CREATE_NO_WINDOW`). 자식 안에서의 순서는 다음과 같다.
  1. `subprocess.run`을 잠시 `capture`로 바꿔치고 `store._git('cat-file', '--batch', input=b'')`를 불러, 제품이 Git에 넘기는 명령과 키워드 인자를 붙잡는다. 붙잡은 뒤 원래 함수로 되돌리고, 인자에서 `input`과 `check`를 뺀다.
  2. 붙잡은 명령·인자로 `Popen`을 두 번 띄운다(`stdin=PIPE` 추가). 첫 번째(`positive=True`)는 `creationflags`를 `CREATE_NEW_CONSOLE`로 바꾸고 `STARTUPINFO`로 창을 숨긴 양성 대조다. 두 번째는 제품 인자 그대로다.
  3. 각 프로세스에 가짜 객체 이름 40자 `0`을 보내고 답 줄에 `missing`이 있음을 `assert`로 확인해, 실제 Git이 살아 응답하는 중에 관찰하도록 한다.
  4. `psutil`로 Git과 재귀 후손 전부를 모은다. `user32.EnumWindows`로 그 PID들이 소유한 보이는 창을 찾고, 각 PID에 `kernel32.AttachConsole`을 시도해 성공하면 `GetConsoleWindow` 핸들을 기록한 뒤 `FreeConsole`한다. 실패하면 `ctypes.get_last_error()`가 6(`ERROR_INVALID_HANDLE`) 또는 87(`ERROR_INVALID_PARAMETER`)이어야 하고 콘솔 값 0을 기록한다.
  5. 마지막으로 `bytes(range(256))+b'\r\n'`을 `store.publish`로 `runtime/artifacts/actual/binary`에 쓰고 `read_bytes`로 같은 바이트가 돌아옴을 `assert`한 뒤, 두 관찰 결과를 `actual.json`에 쓴다.
- 단언: 자식의 종료 코드가 0이다(실패 시 stderr 표시). 양성 대조의 `consoles` 가운데 0이 아닌 값이 있다. 제품 인자 관찰의 `names`에 `git`이 든 이름이 있고, `consoles`가 비어 있지 않되 모두 0이며, `visible`이 빈 목록이다. 자식 안의 `assert`(Git 응답, 오류 코드 6·87, 이진 왕복)는 실패하면 종료 코드를 0이 아니게 만들어 첫 단언에서 드러난다.
- 대역: 자식 안에서 `subprocess.run`을 인자 수집용 `capture` 함수로 잠시 바꿔친다(실제 실행은 그대로 위임). 그 밖의 대역은 없다.
- 비고: 메서드 표지 `unittest.skipUnless(os.name == 'nt' and importlib.util.find_spec('psutil'), 'Windows process-tree observation requires psutil')`. 실제 외부 자원은 `pythonw.exe` 자식, 실제 Git 프로세스들, Win32 `kernel32`·`user32` API다. 시간 상한은 부모의 `timeout=60`과 자식의 `communicate(timeout=10)`이다. `test_group` 표지가 없어 `run_tests.py`의 Job 격리 없이 돈다.

### `test_all_managed_subprocess_calls_explicitly_prevent_console_creation` (행 87–107)
- 성질: 제품 `do_math/`의 모든 자식 프로세스 호출 자리는 `creationflags` 키워드를 명시하고, 검사는 알려진 호출 자리를 모두 훑는다.
- 준비: 1단에 준하는 정적 검사. `SCRIPTS / 'do_math'`의 모든 `*.py` 원문을 `ast.parse`한다.
- 실행: 모든 `ast.Call`을 걸러 `subprocess.run`·`subprocess.Popen` 직접 호출과, `scheduled_operator.py` 안에서 이름 `runner`로 하는 주입 호출을 모은다.
- 단언: 모은 호출마다 키워드 이름 집합에 `creationflags`가 있다(실패 메시지는 파일 이름과 행). 모은 호출이 10개 이상이다.
- 대역: 없음.
- 비고: 주석(행 103–106)이 하한 10의 근거를 밝힌다. 두 제공자가 능력 탐지(`codex_adapter`)와 작업자 실행(`cli_worker.run_cli`)을 공유하므로 호출 자리는 `cli` 2, `codex_adapter` 1, `cli_worker` 1, `formal` 2, `git_store` 1, `scheduled_operator` 3이다. 현재 원문에서 grep한 결과도 이 분포와 같다(`scheduled_operator.py`는 `subprocess.run` 두 곳과 행 154의 `runner(...)` 한 곳). 하한은 `>=`이므로 호출 자리가 늘어도 통과하고, 검사가 모듈을 놓쳐 줄어들면 실패한다. `subprocess.run`을 다른 이름으로 import하거나 `subprocess.call` 등을 쓰는 호출은 이 검사에 잡히지 않는다.

### `test_pythonw_git_calls_have_no_console_and_preserve_binary_state` (행 110–147)
- 성질: pythonw 아래에서 `GitStateStore`가 띄우는 Git 호출은 콘솔을 얻지 않고, 두 번의 게시를 거쳐도 이진 산출물과 부모 커밋 연결이 보존된다.
- 준비: 임시 폴더에 자식 스크립트 `probe.py`를 쓴다. 자식은 실제 `git init -q`로 저장소를 만든다. 네 단 밖(실제 Git 저장소, 실제 자식 프로세스).
- 실행: `pythonw.exe`로 자식을 실행한다(`check=True`, `timeout=60`, `CREATE_NO_WINDOW`). 자식은 `subprocess.run`을 `observed`로 바꿔친다. `observed`는 첫 호출에서만, 제품이 준 `creationflags`를 그대로 써서 `python.exe -c 'print(GetConsoleWindow())'`를 띄워 그 자식이 본 콘솔 핸들을 기록하고, 이어 원래 명령을 실제로 실행한다. 그 상태로 `GitStateStore`를 열고 `bytes(range(256))`을 담은 첫 `publish(None, ...)`, `runtime/state.json`만 바꾼 둘째 `publish(first.head, ...)`를 한다. 부모 자신의 `GetConsoleWindow`, 기록한 자식 콘솔 목록, 둘째 스냅숏에서 읽은 이진 파일의 동일성, `_git_text('rev-parse', second.head+'^')`가 첫 헤드와 같은지를 `result.json`에 쓴다.
- 단언: `parent_console`이 0(pythonw 부모에게 콘솔이 없음), `child_consoles`가 `[0]`(제품 플래그로 띄운 자식도 콘솔이 없음), `binary_unchanged`와 `parent_preserved`가 참이다.
- 대역: 자식 안에서 `subprocess.run`을 `observed`로 바꿔친다. 첫 호출에 콘솔 탐지 프로세스를 한 번 끼워 넣고 실제 실행은 그대로 위임하는 스파이다.
- 비고: 메서드 표지 `unittest.skipUnless(os.name == 'nt', 'Windows console semantics')`. `psutil`은 요구하지 않는다. 실제 외부 자원은 `pythonw.exe`, `python.exe` 탐지 자식, 실제 Git이다. 콘솔 관찰은 첫 Git 호출 하나에서만 한다.

## 관계

- 같은 `creationflags` 약속을 다른 층에서 보는 시험: `test_schedule_pythonw`는 예약 등록 어댑터를 pythonw로 실제 실행하고, `test_formal_runtime`·`test_windows_job`은 Lean·Job 자식 실행을 본다. 이 모듈은 Git 저장 경로와 제품 전체의 호출 자리에 집중한다.
- 픽스처를 쓰지 않는다. 저장소도 `research_fixtures.git_init`이 아니라 실제 `git init` 자식으로 만든다. 콘솔 할당 여부가 검사 대상이므로 시험-지침 4절 규칙 6의 "자식 프로세스를 유지하는" 경우에 해당한다.
- 첫 시험과 셋째 시험은 모두 pythonw 아래 Git 호출의 콘솔 부재를 본다. 첫 시험은 `psutil`로 후손 전부와 보이는 창까지 관찰하고 양성 대조를 둔다. 셋째 시험은 `psutil` 없이 첫 호출 하나의 콘솔만 보는 대신, 두 번의 게시에 걸친 이진 보존과 부모 연결을 더 확인한다. `psutil`이 없는 환경에서는 셋째 시험만 돈다.
- `git_store`의 게시·읽기 계약 자체는 `test_git_store`가 프로세스 안에서 검사한다.

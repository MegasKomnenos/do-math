# test_windows_job

| 항목 | 값 |
|---|---|
| 조각 | `host` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_windows_job.py` (281행) |
| 클래스 / 테스트 | 1 / 8 (조건부로 정의되는 ctypes 구조체 클래스 3개는 시험 클래스가 아니다) |
| 시험 대상 제품 코드 | `do_math/windows_job.py`의 `WindowsJob`(행 252 이하: 생성자, `job_handle`, `_create_job`, `_create_suspended_root`, `resume`, `wait`, `terminate`, `inspect`, `close`, 컨텍스트 관리자), `JobInspection`(행 50 이하의 `active_processes`, `process_ids`, `root_signaled`) |
| 사용하는 픽스처 모듈 | 없음 |
| 격리 표지 | 없음(`test_group` 미사용). 클래스 단위 `unittest.skipUnless(os.name == "nt", "requires a Windows host")` |
| 시작 상태 | 네 단 밖. 모든 시험이 실제 Windows Job과 실제 Python 자식·손자 프로세스를 만들고, `kernel32` API로 커널 상태를 직접 관찰한다 |

## 목적

모듈 docstring은 "초기 do-math 프로세스 어댑터에 대한 Windows 커널 직접 검사"라고 밝힌다. `WindowsJob`은 명령 하나를 일시정지된 루트 프로세스로 만들어 새 Job 객체에 넣고, 명시적 `resume` 전에는 사용자 코드를 돌리지 않는다. Job 핸들은 상속되지 않고, Job에는 `KILL_ON_JOB_CLOSE` 한도가 걸리며 이탈(breakaway)이 허용되지 않는다. 따라서 마지막 Job 핸들이 닫히면(소유 프로세스가 죽는 경우 포함) Job 안의 모든 프로세스가 끝난다. 이 모듈은 일시정지 루트, 대기 시간 초과 뒤의 소유 유지와 닫기 시 종료, 작업 폴더·환경 전달, 후손까지의 종료, 소유자 상실 시 종료, 핸들 비상속과 이탈 금지, 생성 실패, 무관한 상속 가능 핸들의 차단을 검사한다.

## 모듈 수준 요소

- `SCRIPTS` (행 15): 스킬의 `scripts/` 폴더. 행 16–17이 `sys.path`에 없을 때만 앞에 넣는다. 소유자 자식 프로세스의 `sys.path`에도 넣는다(행 179).
- 행 19: `WindowsJob`을 import한다.
- 행 22–57(`os.name == "nt"`일 때만): 시험이 커널을 직접 조회하기 위한 정의. `_kernel32`(`WinDLL('kernel32', use_last_error=True)`), 상수 `_HANDLE_FLAG_INHERIT = 0x1`, `_JobObjectExtendedLimitInformation = 9`, `_JOB_OBJECT_LIMIT_BREAKAWAY_OK = 0x800`, `_JOB_OBJECT_LIMIT_SILENT_BREAKAWAY_OK = 0x1000`, `_JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x2000`, 그리고 `QueryInformationJobObject`의 결과를 받을 ctypes 구조체 `_IO_COUNTERS`, `_BASIC_LIMITS`, `_EXTENDED_LIMITS`(Win32 `JOBOBJECT_EXTENDED_LIMIT_INFORMATION`의 배치). 사용처는 `test_job_handle_is_not_inheritable_and_breakaway_is_disabled`와 `test_root_cannot_signal_an_unrelated_inheritable_parent_handle`이다.
- 행 280–281: 직접 실행하면 `unittest.main(verbosity=2)`.

## WindowsJobTests (행 61–277)

`unittest.TestCase`를 상속하고 클래스 데코레이터 `unittest.skipUnless(os.name == "nt", "requires a Windows host")`가 붙는다. `test_group` 표지가 없다.

- `setUp` (행 62–64): 임시 폴더를 만들어 `self.path`로 둔다.
- `tearDown` (행 66–67): 임시 폴더를 정리한다.
- `wait_for(predicate, timeout=15.0)` (행 69–75): 조건이 참이 될 때까지 0.02초 간격으로 최대 15초 폴링하고, 넘으면 `self.fail('timed out waiting for Windows process state')`.

### `test_root_is_suspended_until_explicit_resume` (행 77–95)
- 성질: Job의 루트 프로세스는 명시적 재개 전까지 사용자 코드를 돌리지 않고, 재개 뒤 끝나면 Job은 비고 루트는 신호 상태가 된다.
- 준비: 표지 파일 `started`를 쓰는 Python 명령.
- 실행: `WindowsJob([...])` 안에서 재개 전 `inspect()`, `resume()`, 표지 파일 폴링, `wait(5.0)`, 활성 프로세스 0 폴링, `inspect()`.
- 단언: 재개 전: 표지 파일이 없고, `creation_filetime`이 0보다 크며, 활성 프로세스가 1이고 `process_ids`에 루트 PID가 있으며 `root_signaled`가 거짓이다. 재개 뒤: 표지 파일이 생기고 `wait(5.0)`이 참이며, 활성 프로세스 0, `process_ids`가 빈 튜플, `root_signaled`가 참이다.
- 대역: 없음.

### `test_wait_timeout_keeps_job_owned_until_explicit_close` (행 97–126)
- 성질: 대기 시간이 초과되어도 Job은 계속 소유되어 루트가 살아 있고, 명시적으로 닫으면 마지막 Job 핸들이 풀려 루트가 끝난다.
- 준비: 60초 자는 Python을 루트로 한 `WindowsJob`(컨텍스트 관리자 없이). 시험이 `OpenProcess(0x00100001, ...)`(SYNCHRONIZE|PROCESS_TERMINATE)로 루트 프로세스 핸들만 따로 잡는다(주석 행 106: Job이 아니라 프로세스를 잡아야 닫기가 마지막 Job 핸들을 푼다).
- 실행: `resume()`, `wait(0.01)`, `inspect()`, `close()`, `WaitForSingleObject(root_handle, 5000)`.
- 단언: 프로세스 핸들을 얻었다. `wait(0.01)`이 거짓이다. 활성 프로세스가 1 이상이고 루트 PID가 들어 있다. 닫은 뒤 5초 안에 루트가 신호 상태(반환값 0)가 된다(메시지 `a timed-out wait leaked a live root after close`).
- 대역: 없음.
- 비고: `finally`에서 다시 `close()`하고, 루트가 아직 살아 있으면(258, `WAIT_TIMEOUT`) `TerminateProcess`로 끝낸 뒤 핸들을 닫는다.

### `test_direct_createprocess_receives_requested_cwd_and_environment` (행 128–144)
- 성질: 루트 프로세스는 요청한 작업 폴더와 환경 블록을 그대로 받는다.
- 준비: 작업 폴더와 `DO_MATH_JOB_TEST` 값을 파일에 쓰는 Python 명령. 환경은 `DO_MATH_JOB_TEST=present`와 `SystemRoot`만이다.
- 실행: `WindowsJob([...], cwd=self.path, env=environment)`, `resume()`, 파일 폴링, `wait(5.0)`.
- 단언: `wait`가 참이다. 기록된 작업 폴더가 `self.path`와 같고 환경값이 `present`다.
- 대역: 없음.

### `test_terminate_ends_descendant_processes_and_job_becomes_empty` (행 146–166)
- 성질: Job을 끝내면 루트가 띄운 후손 프로세스까지 끝나고 Job이 빈다.
- 준비: 30초 자는 자식을 `Popen`하고 그 PID를 파일에 쓴 뒤 30초 자는 부모 Python 명령.
- 실행: `resume()`, PID 파일 폴링, `inspect()`, `terminate()`, `wait(5.0)`, 활성 프로세스 0 폴링, `inspect()`.
- 단언: 자식 PID가 Job의 `process_ids`에 있다(자식도 Job에 속함). 종료 뒤 `wait`가 참, `process_ids`가 빈 튜플, `root_signaled`가 참이다.
- 대역: 없음.

### `test_owner_process_loss_closes_job_and_ends_root` (행 168–227)
- 성질: Job을 소유한 프로세스가 사라지면 Job이 닫혀 실행 중인 루트가 끝난다.
- 준비: 소유자 역할의 자식 Python(`owner_code`)은 `SCRIPTS`를 경로에 넣고 60초 자는 루트로 `WindowsJob`을 만들어 재개하고, 루트 PID를 파일에 쓴 뒤 표준 입력 1바이트를 기다렸다가 `os._exit(0)`한다. 소유자를 `subprocess.Popen(..., stdin=PIPE, creationflags=CREATE_NO_WINDOW)`로 띄운다.
- 실행: 루트 PID 파일을 폴링하고 루트의 프로세스 핸들만 잡는다(주석 행 202–203: Job 핸들을 잡으면 소유자 상실이 마지막 Job 핸들을 닫지 못한다). 루트 시작 표지를 폴링한다. 소유자에게 1바이트를 보내고 끝나기를 기다린다.
- 단언: 핸들을 얻었다. 그 시점에 소유자가 살아 있고(`poll()`이 `None`) 루트가 살아 있다(`WaitForSingleObject(..., 0) == 258`). 소유자의 종료 코드가 0(10초 상한)이다. 이어 5초 안에 루트가 신호 상태가 된다(메시지 `the running root did not terminate after its Job owner exited`).
- 대역: 없음.
- 비고: 실제 자식(소유자)과 손자(루트) 프로세스. `finally`에서 소유자가 살아 있으면 죽이고, 루트가 살아 있으면 끝낸 뒤 핸들을 닫는다. 이 성질은 `test_launch_recovery`의 복구 확인이 기대는 커널 동작이다.

### `test_job_handle_is_not_inheritable_and_breakaway_is_disabled` (행 229–247)
- 성질: Job 핸들은 상속되지 않고, Job에는 닫힐 때 모두 끝내는 한도가 걸리며 이탈 한도는 꺼져 있다.
- 준비: 30초 자는 루트의 `WindowsJob`(재개하지 않음).
- 실행: `GetHandleInformation(job.job_handle)`, `QueryInformationJobObject(job.job_handle, 9, _EXTENDED_LIMITS)`.
- 단언: 두 API가 성공한다. 핸들 플래그에 `HANDLE_FLAG_INHERIT`가 없다. `LimitFlags`에 `KILL_ON_JOB_CLOSE`가 있고 `BREAKAWAY_OK`와 `SILENT_BREAKAWAY_OK`가 없다.
- 대역: 없음.

### `test_create_failure_leaves_no_live_job_root` (행 249–251)
- 성질: 실행 파일이 없어 루트를 만들 수 없으면 생성이 `OSError`로 실패한다.
- 준비: 없는 `not-an-executable.exe` 경로.
- 실행: `WindowsJob([경로])`.
- 단언: `OSError`가 난다.
- 대역: 없음.
- 비고: 이름은 "살아 있는 Job 루트를 남기지 않음"을 말하지만, 시험은 예외만 확인하고 Job이나 프로세스가 남지 않았는지는 관찰하지 않는다.

### `test_root_cannot_signal_an_unrelated_inheritable_parent_handle` (행 253–277)
- 성질: 부모가 가진 무관한 상속 가능 핸들은 루트에 상속되지 않아, 루트가 그 핸들 값으로 부모의 객체를 조작할 수 없다.
- 준비: 수동 재설정 이벤트를 `CreateEventW`로 만들고 `SetHandleInformation`으로 상속 가능하게 한다. 루트 코드는 그 핸들 값으로 `SetEvent`를 시도한 뒤 표지 파일 `handle-probe-ran`을 쓴다.
- 실행: `WindowsJob([...])`, `resume()`, `wait(15)`, `WaitForSingleObject(event, 0)`.
- 단언: 이벤트 생성과 상속 설정이 성공한다. `wait`가 참이고 표지 파일이 있다(루트 코드가 실제로 돌았음). 이벤트가 신호되지 않았다(258; 메시지 `root inherited and signaled an unrelated parent Event`).
- 대역: 없음.
- 비고: `finally`에서 이벤트 핸들을 닫는다.

## 관계

- 같은 제품 기능을 다른 층에서 보는 모듈: `test_host_resources`는 Job 자원 한도(메모리·CPU)와 이름 있는 Job 생성·설정 실패를, `test_launch_recovery`는 이름 충돌과 소유자 상실 뒤 복구 확인을, `test_formal`·`test_formal_runtime`·`test_machine_parallel`은 `_job_run`을 거친 Job 사용을, `test_owned_job_children`(`foundation` 조각)은 소유 Job 자식 관리를, `test_test_runner`(`foundation`)는 `run_tests.py`의 격리 Job 사용을 본다.
- 픽스처를 쓰지 않는다.
- 이 모듈에만 있는 도우미: `wait_for`와 조건부 ctypes 정의들.
- 표지: 모든 시험이 실제 Windows Job과 자식 프로세스를 쓰지만 `resource` 표지가 없어 `run_tests.py`의 Job 격리와 시간 상한 없이 돈다. 시간 상한은 각 시험 안의 폴링(15초)과 대기(5–15초)다.

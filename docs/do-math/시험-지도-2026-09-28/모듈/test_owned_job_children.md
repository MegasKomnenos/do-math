# test_owned_job_children

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_owned_job_children.py` (93행) |
| 클래스 / 테스트 | 1 / 4 |
| 시험 대상 제품 코드 | `do_math/windows_job.py`의 `WindowsJob`(`__init__`의 중단 상태 루트 생성, `resume`, `wait`, `terminate`, `inspect`, `_process_creation_filetime`, `close`/`__exit__`), `_kernel32`, `_WAIT_FAILED`; `do_math/control_transport.py`의 `ControlTransport.issue`, `worker_submit`, `pump` |
| 사용하는 픽스처 모듈 | 없음. 격리 표지 함수 `test_categories.test_group`을 `category`라는 이름으로 import한다 |
| 격리 표지 | 클래스 전체에 `unittest.skipUnless(os.name == 'nt', 'requires Windows Job host')`. `test_local_control_receipt_remains_responsive_during_child_cpu_load`에만 `category('resource')`(= `test_group('resource')`) |
| 시작 상태 | 네 단 밖. 실제 Windows Job과 실제 Python 자식 프로세스(`sys.executable -c ...`)를 쓴다 |

## 목적

모듈 docstring의 첫 문장은 "Windows Job ownership of child processes: suspended start, held identity, nested jobs and control under load."이다. 곧 네 시험은 각각 다음을 본다.

- 중단 상태로 만든 루트는 재개에 실패하면 실행되지 않는다.
- 소유한 프로세스의 신원은 보유 핸들에 묶이며 pid 필드를 따라가지 않는다.
- 중첩된 Job의 자식도 바깥 Job이 소유한다.
- 자식이 CPU를 쓰는 동안에도 지역 제어 전송의 영수증이 응답한다.

docstring은 범위도 밝힌다. 일회용 Windows 자식만 쓰고, 연구 호스트, 공급자, 일정은 쓰지 않는다. 보유 핸들 신원과 주입한 재개 실패는 자연적인 PID 재활용이나 완전한 엔진 충돌 시험이 아니다. 지역의 바쁜 자식에 대한 제어는 공급자 지연이 아니다. 제품 좌표는 `windows_job.py`의 `WindowsJob` docstring이다. 이 클래스는 kill-on-close Job에 원자적으로 넣은 중단 상태의 루트 하나이고, Job 핸들의 유일한 보유자이므로 닫으면 남은 루트와 후손을 죽인다.

## 모듈 수준 요소

- 행 16: `sys.path.insert(0, str(Path(__file__).resolve().parents[1]))`로 `scripts/` 폴더를 경로 앞에 넣는 공통 머리다. 이 머리 덕분에 `scripts/test_categories.py`도 import된다.
- 행 17: `from test_categories import test_group as category`. 격리 표지 함수를 `category`라는 이름으로 쓴다. 표지 이름은 `'resource'`이고, 실행기는 이 표지가 붙은 시험을 Windows Job이 소유한 별도 프로세스에서 제한 시간과 함께 돌린다(`시험-지침.md` 1절).
- 행 93: 직접 실행하면 `unittest.main(verbosity=2)`를 부른다.

## IsolatedHostTests (행 23–90)

- 기반: `unittest.TestCase`.
- 클래스 표지: `@unittest.skipUnless(os.name == 'nt', 'requires Windows Job host')`. Windows가 아니면 네 시험 모두 건너뛴다.
- 클래스 속성과 설정 훅: 없다. 각 시험이 `with jobs.WindowsJob(...) as job:`으로 Job을 만들고, 블록을 나갈 때 `close`가 핸들을 닫는다(kill-on-close).
- `until(self, predicate, timeout=10)` (행 24–29): 조건이 참이 될 때까지 0.02초 간격으로 폴링한다. 10초 안에 참이 되지 않으면 `'isolated child did not reach its boundary before timeout'`으로 실패한다. 시험-지침 4절 규칙 5의 "조건 폴링과 상한" 규칙을 따르는 도우미다.

### `test_resume_failure_never_runs_the_suspended_child` (행 31–41)
- 성질: 중단 상태로 만든 루트는 재개가 실패하면 한 줄도 실행되지 않고, 종료하면 Job이 비워진다.
- 준비: 임시 폴더의 표지 파일 경로. 자식 코드는 그 파일에 `"ran"`을 쓰는 한 줄이다. `jobs.WindowsJob([sys.executable, '-c', code])`로 중단 상태의 루트를 만든다.
- 실행: `patch.object(jobs._kernel32, 'ResumeThread', return_value=jobs._WAIT_FAILED)` 아래에서 `job.resume()`를 부른다. 패치를 푼 뒤 `job.terminate()`, `job.wait(5)`를 부르고, 활성 프로세스 수를 폴링한다.
- 단언: `resume`이 `OSError`를 던진다(유형만 본다). 표지 파일이 없다. `wait(5)`가 참이다. `inspect().active_processes`가 10초 안에 0이 된다.
- 대역: `ResumeThread`의 반환값 패치(`_WAIT_FAILED`, 곧 `0xFFFFFFFF`). 나머지는 실제 Job과 실제 자식 프로세스다.
- 비고: 제품 `resume`은 `ResumeThread`가 `_WAIT_FAILED`를 돌려주면 `_raise_last_error("ResumeThread")`로 `OSError`를 던지고 `_resumed`를 세우지 않는다(`windows_job.py` 461–472행). 실제 스레드는 재개되지 않았으므로 표지 파일의 부재는 경합 없이 확정된다. 다만 시험은 파일 부재를 재개 실패 직후 한 번만 본다. docstring이 밝히듯 이것은 주입한 실패이지 실제 커널 실패가 아니다.

### `test_owned_process_identity_does_not_follow_a_changed_pid_field` (행 43–53)
- 성질: 소유한 프로세스의 생성 시각과 종료는 Job이 보유한 핸들로 이루어진다. 공개 `pid` 필드를 다른 프로세스의 pid로 바꿔도 다른 프로세스를 가리키거나 건드리지 않는다.
- 준비: 30초 동안 잠드는 자식 둘을 각자의 Job(`first`, `other`)에 만든다. 둘 다 재개하지 않는다.
- 실행: `first`의 원래 pid와 `creation_filetime`을 기록하고, `first.pid = other.pid`로 바꾼다. 그 뒤 `first._process_creation_filetime()`, `first.terminate()`, `first.wait(5)`를 부른다.
- 단언: 원래 생성 시각이 0보다 크다. pid를 바꾼 뒤의 `_process_creation_filetime()`이 원래 값과 같다. `first.wait(5)`가 참이다. `other.inspect().root_signaled`가 거짓이다. 원래 pid가 `other.pid`와 다르다.
- 대역: 없음. 주석(48행)이 밝히듯 pid 교체는 "synthetic recycled locator, not OS PID reuse"다.
- 비고: `_process_creation_filetime`은 `GetProcessTimes(self.process_handle, ...)`를 쓰고, `terminate`는 `TerminateJobObject(self.job_handle, ...)`를 쓴다(`windows_job.py` 446–459, 489–494행). 둘 다 pid 필드를 읽지 않으므로 이 시험이 성립한다. 원래 pid가 `other.pid`와 다르다는 마지막 단언은 두 자식이 서로 다른 프로세스였음을 확인해, 위의 단언들이 자명하게 참이 되는 경우를 배제한다.

### `test_nested_job_child_remains_owned_by_outer_job` (행 55–70)
- 성질: 자식이 스스로 안쪽 Job을 만들어 손자를 띄워도, 그 손자는 바깥 Job의 프로세스 목록에 들고 바깥 Job의 종료로 함께 끝난다.
- 준비: 바깥 자식의 코드는 다음 순서로 돈다. `scripts/` 폴더를 `sys.path`에 넣고, `WindowsJob`으로 30초 잠드는 손자를 만들어 재개한다. 손자의 pid를 표지 파일에 쓰고 30초 잠든다.
- 실행: `outer.resume()`. 표지 파일이 생기고 내용이 비지 않을 때까지 `until`로 기다린다. 손자 pid를 읽은 뒤 `outer.terminate()`, `outer.wait(5)`를 부르고 활성 프로세스 수를 폴링한다.
- 단언: 손자 pid가 `outer.inspect().process_ids`에 있다. `wait(5)`가 참이다. 바깥 Job의 `active_processes`가 10초 안에 0이 된다.
- 대역: 없음. 실제 중첩 Job과 실제 손자 프로세스다.
- 비고: 이 시험의 자식은 제품 모듈 `do_math.windows_job`을 자식 인터프리터 안에서 import한다. 표지 파일은 자식이 손자를 재개한 뒤에 쓰므로, 그 시점에 손자는 이미 두 Job 모두에 속해 있다.

### `test_local_control_receipt_remains_responsive_during_child_cpu_load` (행 73–90)
- 성질: Job 안의 자식이 CPU를 계속 쓰는 동안에도, 지역 제어 전송의 제출과 수신이 교착 없이 끝나고 수락 영수증이 나온다.
- 준비: 자식 코드는 표지 파일에 `"ready"`를 쓴 뒤 `sum(range(10000))`을 무한히 반복한다. `job.resume()` 뒤 표지 파일이 생길 때까지 `until`로 기다린다. `ControlTransport(임시 폴더 / 'control')`에서 `issue('EX-isolated', 'GR-fixture')`로 결합을 발급한다(작업 공간 없음).
- 실행: 시각을 잰다. 작업자 쪽 정적 메서드 `ControlTransport.worker_submit(binding, request_id='CT-stop', kind='safety_boundary', payload={'inflight_calls': False})`를 부른다. 이어서 엔진 쪽 `transport.pump(...)`를 부른다. 게시 콜백은 `{'state': 'accepted', 'published': True, 'snapshot': 'fixture'}`를 돌려준다.
- 단언: 제출의 `state`가 `'submitted'`다. 첫 영수증의 `state`가 `'accepted'`다. 경과 시간이 10초 미만이다. 이어서 Job을 종료하고 `wait(5)`가 참이며, 활성 프로세스가 0이 된다.
- 대역: 게시 콜백 람다(엔진의 검증과 CAS 게시를 대신한다). Job과 자식은 실제다.
- 비고: 주석(87행)은 10초가 "A generous deadlock bound, not a latency or performance SLA"라고 밝힌다. 이 시험에만 `resource` 표지가 붙어, 실행기가 격리 프로세스에서 제한 시간과 함께 돌린다. 나머지 세 시험도 실제 Job과 자식 프로세스를 쓰지만 표지가 없으므로 격리하지 않은 채 돈다. 제어 전송의 `safety_boundary` 요청은 `payload.inflight_calls`가 정확히 `False`여야 받아들여진다(`control_transport.py`의 `_validate_request`).

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈:
  - `test_codex_adapter`는 `FakeJob`의 고정 `JobInspection`으로 수집기의 종료 장벽 판정을 본다. 이 모듈은 그 관찰을 실제 Job이 어떻게 내는지를 본다.
  - `test_control_transport`는 제어 전송의 요청·영수증·미리보기·MCP 자식을 실제 파일로 자세히 본다. 이 모듈의 넷째 시험은 부하 아래에서 응답한다는 한 성질만 본다.
  - `test_machine_parallel`의 docstring은 "real Job barriers"를 다룬다고 밝힌다. 기계 역할의 후속 처리에서 실제 Job 장벽을 보는 모듈이다.
  - `test_supervisor_recovery`는 Windows Job 사실을 합성해서 쓴다. 이 모듈은 실제 Job을 쓴다.
- 픽스처 의존: 없다. 격리 표지 함수만 `scripts/test_categories.py`에서 가져온다.
- 이 모듈에만 있는 도우미: `IsolatedHostTests.until`.

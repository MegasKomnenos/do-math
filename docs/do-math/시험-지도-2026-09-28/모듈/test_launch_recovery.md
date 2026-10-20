# test_launch_recovery

| 항목 | 값 |
|---|---|
| 조각 | `host` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_launch_recovery.py` (78행) |
| 클래스 / 테스트 | 1 / 4 |
| 시험 대상 제품 코드 | `do_math/launch.py`의 `ticket`(행 9–14), `validate`(행 17–41), `termination_confirmed`(행 74–87); `do_math/windows_job.py`의 `WindowsJob`(이름 있는 Job, 일시정지 루트), `owner_identity`(행 587–601), `owner_ended`(행 604 이하), 그리고 `termination_confirmed`가 부르는 `named_job_empty` |
| 사용하는 픽스처 모듈 | 없음 |
| 격리 표지 | 없음(`test_group` 미사용). 클래스 단위 `unittest.skipUnless(os.name == 'nt', 'Windows launch contract')` |
| 시작 상태 | 네 단 밖. 실제 현재 프로세스의 소유자 신원, 실제 자식 Python 프로세스, 실제 이름 있는 Windows Job을 쓴다. 저장소·엔진은 쓰지 않는다 |

## 목적

모듈 docstring은 "게시 전 실행 틈새에 걸친 실제 로컬 소유 관찰"이라고 밝힌다. 제품 `launch.py`의 docstring은 "지속되는 실행 전 신원. 콜백이 없다는 것은 결코 종료 영수증이 아니다"이다. 실행 발급권(`ticket`)은 실행 ID, 프로필 해시, 종류(`native_job` 또는 `owner_thread`), 소유 프로세스의 신원(PID, 생성 FILETIME, 호스트, 세션), Job 이름(`Local\DoMath-<32자 16진>`), 단계(`reserved`에서 시작)를 담는다. 소유자가 루트를 만들기 전이나 만든 뒤, 게시하기 전에 죽어도 복구자는 발급권만으로 종료를 확인할 수 있어야 한다. 복구 중(`recovering=True`)의 `termination_confirmed`는 소유자가 확실히 죽었을 때(`owner_ended`가 `True`)만 참이 될 수 있고, 그때 `native_job` 발급권은 이름 있는 Job이 비었을 때만 참이다. 단계가 `not_started`(로컬 시작 실패 영수증)이면 Job을 보지 않고 참이다. 복구 중이 아니면 `reserved`·`finished`·`not_started` 단계는 소유자가 살아 있어도 Job 관찰로 넘어간다(`launch.py` 행 74–87). 알 수 없는 접근·호스트·세션은 죽음의 증거가 아니다(`owner_ended` docstring). 이 모듈은 살아 있는 소유자와 다른 세션의 판정, 네 시점의 소유자 강제 종료 뒤 복구 확인, Job 이름 충돌, 발급권의 실행 결속을 검사한다.

## 모듈 수준 요소

- 행 10: `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리.
- 행 11–12: `ticket`, `termination_confirmed`, `validate`, `WindowsJob`, `owner_identity`, `owner_ended`를 import한다.
- `__main__` 블록이 없다. 파일을 직접 실행하면 클래스 정의만 하고 시험을 시작하지 않는다(시험-지침 1절의 "직접 실행해도 시험을 시작하지 않는" 파일에 해당).

## LaunchRecoveryTests (행 16–78)

`unittest.TestCase`를 그대로 상속하고 클래스 데코레이터 `unittest.skipUnless(os.name == 'nt', 'Windows launch contract')`가 붙는다. `test_group` 표지·설정 훅·도우미·속성이 없다. 모든 발급권은 프로필 `{'sha256': 'a'*64, 'actor_kind': 'ai', 'role': 'research_work'}`로 만들므로 종류가 `native_job`이다.

### `test_current_owner_and_foreign_session_are_not_dead` (행 17–24)
- 성질: 살아 있는 현재 소유자는 죽지 않았다고 판정되고, 다른 세션의 소유자는 "알 수 없음"이며, 살아 있는 소유자의 발급권은 복구 중이든 아니든 종료가 확인되지 않는다.
- 준비: 현재 프로세스의 `owner_identity()`. 발급권 `EX-test`.
- 실행: `owner_ended(identity)`, 세션 번호만 1 늘린 신원의 `owner_ended`, `reserved` 단계 발급권의 `termination_confirmed(t, recovering=True)`, 단계를 `dispatched`로 바꾼 `termination_confirmed(t)`.
- 단언: 첫째가 `False`, 둘째가 `None`, 셋째와 넷째가 거짓이다.
- 대역: 없음.
- 비고: 다른 세션을 `None`으로 보는 것은 `owner_ended`가 현재 프로세스의 세션과 신원의 세션을 비교하기 때문이다(행 610–611).

### `test_crash_before_and_after_suspended_root_creation_is_recoverable` (행 26–67)
- 성질: 소유자가 루트 생성 전, 일시정지 루트 생성 뒤, 루트 실행 중, 루트 완료 뒤의 어느 시점에 강제 종료되어도 복구자는 발급권만으로 종료를 확인할 수 있고, 소유자가 살아 있는 동안에는 확인하지 않는다.
- 준비: 네 `subTest(stage=...)`: `before_create`, `suspended`, `running`, `completed`. 각각 임시 폴더를 쓴다. 소유자 역할의 자식 프로그램(문자열 `program`)은 `dispatched` 단계 발급권 `EX-crash`를 `ticket.json`에 쓰고, `before_create`가 아니면 발급권의 Job 이름으로 `WindowsJob`을 만든다. 루트 명령은 `resumed` 파일을 쓰고 `running`이면 30초, 아니면 0초 잔다. `running`과 `completed`는 `resume` 뒤 `resumed` 파일을 기다리고, `completed`는 추가로 `inspect().root_signaled`를 기다린다. 마지막으로 `ready` 파일을 쓰고 30초 잔다.
- 실행: 자식을 `subprocess.Popen([sys.executable, '-c', program, scripts, root, stage], creationflags=CREATE_NO_WINDOW)`로 띄운다. 최대 10초 동안 `ready`를 폴링하며 그 사이 자식이 끝나면 `self.fail('owner exited before test boundary')`. 발급권을 읽고, `child.kill()`로 소유자를 강제 종료한 뒤, 최대 5초 동안 `termination_confirmed(t, recovering=True)`를 폴링한다.
- 단언: `ready`가 생겼다. 소유자가 살아 있을 때 `termination_confirmed`가 거짓이다. 강제 종료 뒤 참이 된다. `resumed` 파일의 존재가 `stage in {'running', 'completed'}`와 같다. 곧 일시정지 루트는 재개되지 않은 채 끝났고, 재개된 루트만 사용자 코드를 돌렸다.
- 대역: 없음.
- 비고: 실제 자식 Python(소유자), 그 안의 실제 이름 있는 Windows Job과 손자 프로세스를 쓴다. `resource` 표지가 없다. 폴링 상한은 10초와 5초이고, `finally`가 자식이 남아 있으면 죽인다. `running` 경우 루트가 30초 자는 중에 소유자가 죽어도 확인이 5초 안에 참이 되어야 하므로, 소유자 종료가 Job을 닫아 루트를 끝낸다는 성질(`test_windows_job`의 `test_owner_process_loss_closes_job_and_ends_root`)에 기대고 있다.

### `test_job_name_collision_cannot_attach_or_kill_the_original` (행 69–74)
- 성질: 같은 이름으로 둘째 Job을 만들려 하면 거부되고, 원래 Job에 붙거나 그 루트를 끝내지 않는다.
- 준비: 발급권 `EX-collision`의 Job 이름으로 `pass` 명령의 `WindowsJob`을 하나 만든다(재개하지 않음).
- 실행: 같은 이름으로 `WindowsJob` 생성.
- 단언: `FileExistsError`가 난다. 원래 Job의 `inspect().root_signaled`가 거짓이다(루트가 살아 있음).
- 대역: 없음.
- 비고: 실제 이름 있는 Windows Job.

### `test_ticket_cannot_be_rebound_to_another_execution` (행 76–78)
- 성질: 발급권은 다른 실행 ID로 다시 결속할 수 없다.
- 준비: 발급권 `EX-one`.
- 실행: `validate(t, execution_id='EX-two')`.
- 단언: `ValueError`다(메시지 미단언; 제품 문구 `launch ticket execution differs`).
- 대역: 없음.
- 비고: 발급권 생성에 `owner_identity()`가 필요하므로 Windows 전용 클래스 안에 있다. 프로세스를 띄우지 않는다.

## 관계

- 같은 제품 기능을 다른 층에서 보는 모듈: `test_windows_job`은 소유자 상실 시 Job이 닫히는 커널 동작을, `test_diagnosed_installation_recovery`와 `test_supervisor_recovery`는 `termination_confirmed`를 쓰는 복구 조율을, `test_host_resources`는 종료 불명 시 예약 유지(`named_job_empty`가 `None`)를, `test_owned_job_children`(`foundation` 조각)은 소유 Job의 자식 관리를 본다.
- 픽스처를 쓰지 않는다. 발급권은 제품 `ticket`으로 직접 만든다. `research_fixtures.dispatched_launch`와 같은 일을 손으로 한다(`phase`를 `dispatched`로 바꿈).
- 이 모듈에만 있는 도우미: 없음. 소유자 역할의 자식 프로그램은 시험 본문 안의 문자열이다.

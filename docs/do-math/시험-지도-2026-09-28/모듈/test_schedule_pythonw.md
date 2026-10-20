# test_schedule_pythonw

| 항목 | 값 |
|---|---|
| 조각 | `host` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_schedule_pythonw.py` (61행) |
| 클래스 / 테스트 | 1 / 2 |
| 시험 대상 제품 코드 | 스크립트 `scripts/operator_schedule.ps1`의 `install` 동작(행 41 이하: 행 45의 `& $Python $liveBootstrap --freeze ... \| Out-String`으로 동결 JSON 수집, 행 47의 종료 코드 확인과 `Could not freeze the supervisor installation.`, 행 61–62의 운영자·엔진 작업 등록, 행 88의 결과 JSON); 스크립트 `scripts/operator_bootstrap.py`의 `--freeze` |
| 사용하는 픽스처 모듈 | 없음 |
| 격리 표지 | 없음(`test_group` 미사용). 클래스 단위 `unittest.skipUnless(os.name == 'nt' and PYTHONW.is_file(), 'Windows pythonw required')` |
| 시작 상태 | 네 단 밖. 실제 `powershell.exe`가 제품 어댑터를 실행하고, 어댑터가 실제 `pythonw.exe`로 부트스트랩 동결을 돌린다. 작업 스케줄러 cmdlet은 PowerShell 함수 대역으로 가려 운영체제의 작업을 바꾸지 않는다 |

## 목적

모듈 docstring은 "운영체제 작업을 바꾸지 않고 운영 PowerShell 어댑터를 pythonw로 돌려 본다"고 밝힌다. 어댑터는 예약 작업을 등록하기 전에 `pythonw.exe`로 감독자 설치를 동결하고, 그 표준 출력 JSON에서 동결 진입점을 읽는다. `pythonw.exe`는 GUI 실행 파일이라 PowerShell이 기본으로 기다리지 않으므로, 제품은 명시적 파이프라인(`| Out-String`)으로 출력과 종료 코드를 모은다(`operator_schedule.ps1` 행 43–44 주석). 이 모듈은 실제 동결 JSON이 등록 전에 수집되는지와, 동결이 실패하면 표준 출력에 JSON 모양이 있어도 작업을 등록하지 않는지를 검사한다.

## 모듈 수준 요소

- `SCRIPTS` (행 11): 스킬의 `scripts/` 폴더. 제품 어댑터 경로의 기준이다. 이 모듈은 `sys.path`를 고치지 않는다.
- `PYTHONW` (행 12): 현재 해석기 옆의 `pythonw.exe` 경로. 클래스 skip 조건과 어댑터의 `-Python` 인자로 쓴다.
- `__main__` 블록이 없다. 파일을 직접 실행하면 시험을 시작하지 않는다.

## SchedulePythonwTests (행 16–61)

`unittest.TestCase`를 상속하고 클래스 데코레이터 `unittest.skipUnless(os.name == 'nt' and PYTHONW.is_file(), 'Windows pythonw required')`가 붙는다. `test_group` 표지가 없다.

- `run_adapter(root, adapter)` (행 17–38): 임시 폴더 `root`에 PowerShell 하네스 `scheduler-harness.ps1`을 쓴다. 하네스는 `Get-ScheduledTask`(항상 `$null`), `New-ScheduledTaskPrincipal`, `New-ScheduledTaskSettingsSet`, `New-ScheduledTaskTrigger`, `New-ScheduledTaskAction`, `New-ScheduledTask`(빈 객체)와 `Register-ScheduledTask`(등록 기록 파일에 `registered` 한 줄 추가)를 함수로 정의해 실제 cmdlet을 가린 뒤, 어댑터를 `-Action install -Repository <root/work> -Instance RI-test -Workspace <root/work> -Python <pythonw> -OperatorTask TestOperator -EngineTask TestEngine -WakeTask TestWake -IntervalSeconds 7200 -OperatorTimeoutSeconds 5400`으로 부른다. 하네스를 `powershell.exe -NoProfile -ExecutionPolicy Bypass -File`로 실행하고(`CREATE_NO_WINDOW`, `timeout=60`) `(완료 결과, 등록 기록 경로)`를 돌려준다.

### `test_real_freeze_json_is_collected_before_registration` (행 40–48)
- 성질: 어댑터는 pythonw로 돈 실제 동결의 JSON을 수집한 뒤에 작업을 등록하고, 동결 사본은 작업 공간에 하나 생긴다.
- 준비: 임시 폴더. 어댑터는 제품 `operator_schedule.ps1` 그대로다.
- 실행: `run_adapter(root, SCRIPTS / 'operator_schedule.ps1')`.
- 단언: 종료 코드가 0이다(실패 시 stderr). 등록 기록이 `['registered', 'registered']`(운영자와 엔진)다. 표준 출력 JSON의 키 집합이 `{'engine', 'operator', 'wake'}`다. stderr에 `Invalid argument`가 없다. `root/work/operator/bootstrap/*/bootstrap-manifest.json`이 정확히 하나다.
- 대역: 작업 스케줄러 cmdlet의 PowerShell 함수 대역.
- 비고: 실제 `powershell.exe`와 실제 `pythonw.exe`(동결)를 쓴다. 동결 원천은 저장소의 실제 스킬 설치이고, 쓰기는 임시 작업 공간 아래에만 한다. `Invalid argument`를 막는 이유는 원문에도, 이 시험을 도입한 커밋 `a0e6c2f`("repair scheduler registration")의 메시지에도 적혀 있지 않다. 같은 커밋이 어댑터에 `| Out-String` 파이프라인과 종료 코드 `$null` 확인을 넣었다.

### `test_failed_freeze_cannot_register_tasks_even_with_json_stdout` (행 50–61)
- 성질: 동결이 0이 아닌 종료 코드로 끝나면, 표준 출력이 JSON 모양이어도 어댑터는 실패하고 작업을 하나도 등록하지 않는다.
- 준비: 임시 `live/scripts`에 제품 어댑터를 복사하고, 그 옆의 `operator_bootstrap.py`를 `{}`를 출력한 뒤 `sys.exit(7)`하는 가짜로 둔다(주석 행 55: 어댑터는 자기 옆의 부트스트랩으로 동결한다).
- 실행: `run_adapter(root, 복사한 어댑터)`.
- 단언: 종료 코드가 0이 아니다. stderr에 `Could not freeze`가 있다. 등록 기록 파일이 생기지 않았다.
- 대역: 가짜 부트스트랩 스크립트와 cmdlet 함수 대역.
- 비고: 실제 `powershell.exe`와 `pythonw.exe`를 쓴다.

## 관계

- 같은 제품 기능을 다른 층에서 보는 모듈: `test_schedule_lifetime`은 같은 어댑터의 작업 설정 식을, `test_operator_bootstrap`은 동결 자체를, `test_operator`는 파이썬 쪽 `schedule` 호출을, `test_background_processes`는 pythonw 아래 Git 자식의 콘솔 부재를 본다.
- 픽스처를 쓰지 않는다.
- 이 모듈에만 있는 도우미: `run_adapter`.
- 표지: 실제 프로세스를 쓰지만 `resource` 표지가 없어 `run_tests.py`의 Job 격리 없이 돈다. 같은 어댑터를 다루는 `test_schedule_lifetime`은 클래스 표지 `resource`를 단다.

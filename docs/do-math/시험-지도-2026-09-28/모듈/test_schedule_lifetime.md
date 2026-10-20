# test_schedule_lifetime

| 항목 | 값 |
|---|---|
| 조각 | `host` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_schedule_lifetime.py` (56행) |
| 클래스 / 테스트 | 1 / 1 |
| 시험 대상 제품 코드 | 스크립트 `scripts/operator_schedule.ps1`의 설정 식 `$operatorSettings`(행 52: `-ExecutionTimeLimit (New-TimeSpan -Seconds ($OperatorTimeoutSeconds + 300))`)와 `$engineSettings`(행 53: `-ExecutionTimeLimit ([TimeSpan]::Zero)`), 두 식에 공통인 `-MultipleInstances IgnoreNew`, `-Hidden` |
| 사용하는 픽스처 모듈 | 없음. `test_categories.test_group`만 import한다 |
| 격리 표지 | 클래스 표지 `test_group('resource')`. 클래스 단위 `unittest.skipUnless(os.name == 'nt', 'Windows Task Scheduler required')`도 함께 붙는다 |
| 시작 상태 | 네 단 밖. 실제 `powershell.exe` 자식 프로세스가 제품 스크립트를 구문 분석하고 설정 식을 평가해, 등록하지 않은 작업 정의를 XML로 내보낸다 |

## 목적

모듈 docstring은 "작업을 등록하지 않고 실제 PowerShell 설정 식을 내보낸다"고 밝힌다. 예약 어댑터는 두 작업을 등록한다. 엔진 작업은 연구 계산이 끝날 때까지 돌아야 하므로 실행 시간 제한이 없어야 하고, 운영자(감독자) 작업은 설정한 운영자 시간 상한에 여유 300초를 더한 제한을 받는다. 이 모듈은 제품 스크립트 원문의 설정 식을 그대로 평가해 Windows 작업 스케줄러가 저장할 XML 값으로 이 계약을 확인한다. 등록(`Register-ScheduledTask`)은 하지 않으므로 운영체제의 작업 목록은 바뀌지 않는다.

## 모듈 수준 요소

- 행 9: `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리.
- 행 10: `test_categories.test_group`을 원래 이름으로 import한다. unittest는 `TestCase` 하위 클래스만 모으므로 이 함수는 시험으로 수집되지 않는다.
- 행 55–56: 직접 실행하면 `unittest.main()`.

## ScheduleLifetimeTests (행 15–52)

`unittest.TestCase`를 그대로 상속한다. 클래스 데코레이터는 위에서부터 `test_group('resource')`, `unittest.skipUnless(os.name == 'nt', 'Windows Task Scheduler required')`다. 설정 훅·도우미·속성이 없다.

### `test_exported_engine_is_unlimited_and_operator_remains_bounded` (행 16–52)
- 성질: 제품 스크립트의 엔진 작업 설정은 실행 시간 제한이 없고(겹쳐 실행 무시, 숨김), 운영자 작업 설정은 운영자 시간 상한에 300초를 더한 제한을 갖는다.
- 준비: 임시 폴더에 PowerShell 검사 스크립트 `inspect.ps1`을 쓴다. 이 스크립트는 제품 `operator_schedule.ps1`을 `Parser::ParseFile`로 구문 분석하고(오류가 있으면 `Scheduler script does not parse`를 던짐), `$OperatorTimeoutSeconds = 7`을 둔 뒤, AST에서 `$engineSettings`와 `$operatorSettings`의 대입문을 찾아 오른쪽 식을 스크립트 블록으로 평가한다. 평가한 설정으로 `cmd.exe /c exit 0` 동작의 작업 정의를 `New-ScheduledTask`로 만들고 `Export-ScheduledTask`로 XML을 얻어 `ExecutionTimeLimit`, `MultipleInstancesPolicy`, `Hidden`을 JSON으로 출력한다.
- 실행: `subprocess.run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', inspect.ps1, '-Source', 제품 스크립트], timeout=30, creationflags=CREATE_NO_WINDOW)`.
- 단언: 종료 코드가 0이다(실패 시 stderr). `engineSettings`가 정확히 `{'limit': 'PT0S', 'multiple': 'IgnoreNew', 'hidden': 'true'}`다. `operatorSettings.limit`이 `PT5M7S`(7초 + 300초)다.
- 대역: 없음. 운영자 시간 상한 7초는 검사 스크립트가 주입한 값이다.
- 비고: 클래스 표지 `test_group('resource')`, Windows 전용 skip. 실제 외부 자원은 `powershell.exe`와 ScheduledTasks 모듈의 `New-ScheduledTask`·`Export-ScheduledTask`다. 제품 스크립트의 설정 식 원문을 AST로 뽑아 평가하므로, 식을 다른 변수 이름으로 옮기면 `$ast.Find`가 찾지 못해 실패한다. 운영자 설정의 `multiple`과 `hidden`은 단언하지 않는다.

## 관계

- 같은 제품 기능을 다른 층에서 보는 모듈: `test_schedule_pythonw`는 같은 어댑터의 `install` 동작 전체를 등록 함수 대역과 함께 pythonw로 돌린다. `test_operator`는 파이썬 쪽 `schedule`이 어댑터에 넘기는 인자를 본다. `test_formal_runtime`은 엔진 쪽 형식 검사의 무기한 계약을 파이썬 층에서 본다.
- 픽스처를 쓰지 않는다.
- 이 모듈에만 있는 도우미: 없음. PowerShell 검사 스크립트는 시험 본문 안의 문자열이다.

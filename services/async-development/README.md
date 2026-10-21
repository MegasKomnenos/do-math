# 비동기 자동 개발

이 도구는 프로젝트의 목표와 현재 코드를 여러 Codex 세션에 전달해 개발을 이어 간다. 사용자는 만들 결과와 판단에 필요한 자료를 준비하고, 실행기는 작업을 시작한다. 이후에는 작업 결과를 읽은 manager가 무엇을 반영하고 다음에 무엇을 할지 결정한다.

개발을 맡길 한 단위를 **task**라고 부른다. task 하나는 Codex 세션 하나가 수행하며, 실행 중인 task 세션을 **worker**라고 부른다. **manager**는 task의 결과를 검토해 공용 코드에 반영하고 다음 task를 배정하는 세션이다. **review**는 구현된 결과를 사용자 요구와 대조하는 task다.

## 개발이 진행되는 방식

처음에는 manager가 프로젝트의 목표·현재 상태·남은 일을 읽고 작업을 나눈다. 실행기는 선행 결과가 준비된 task를 정해진 동시 실행 수 안에서 시작한다. 각 작업자는 자신의 코드 사본을 받아 구현하므로, 다른 작업자가 수정 중인 파일에 영향을 받지 않고 작업할 수 있다.

task가 끝나면 manager가 보고와 산출물을 읽는다. 결과를 받아들일 수 있으면 변경된 파일을 공용 코드에 통합하고 그 task를 수용한다. 수용된 결과가 필요한 후속 task는 새 공용 코드의 사본으로 시작한다. 보완이 필요하면 manager가 남은 일을 배정한다.

이 과정에서 다른 작업은 계속 실행된다. 예를 들어 문서 작성과 파서 구현이 함께 진행 중일 때 파서가 먼저 수용되면, 파서를 사용하는 명령행 기능의 개발을 시작할 수 있다. 문서 작성의 종료는 기다리지 않는다. manager는 한 번에 하나씩 실행되며, 판단 중 새로 끝난 task는 다음 manager가 처리한다.

세션 사이의 맥락은 공용 문서와 작업 보고로 전달된다. manager는 결과가 생길 때마다 현재 설명과 계획을 갱신한다. 필요한 구현을 마치면 review를 배정하고, 그 결과를 근거로 사용자 목표의 달성 여부를 판단한다.

그 문서와 결과는 작성자와 대화하지 않은 후속 작업자가 실제 진입점에서 읽고 이해·판단·수행할 수 있어야 한다. task는 필요한 배경과 조건을 본문에 설명하고 수행 과정을 작업 기록에 남긴다. manager와 review는 사용 경로를 따라 내용의 충분성과 근거의 정확성을 확인한다. 추출·요약 결과라면 원문의 중요한 내용이 제품에 남았는지도 대조한다. 구체적인 작성·수용 절차는 [작업 계약](protocol.md#2-task가-작업을-수행하는-순서)을 따른다.

## 프로젝트를 맡기기 전에 준비할 것

실행에는 Python과 Codex CLI가 필요하다. 모델 사용과 파일 접근에 필요한 인증·권한은 실행할 환경에 맞게 설정한다.

개발할 프로젝트의 공용 소스 디렉터리를 `REPO`, 개발 기록을 둘 디렉터리를 `RECORDS`, 이 도구가 설치된 디렉터리를 `ENGINE`이라고 부른다. 아래 명령에서는 이 표기를 실제 경로로 바꾼다.

먼저 `RECORDS`에 세 문서를 준비한다.

| 문서 | 세션이 이해해야 할 내용 |
|---|---|
| `context.md` | 누구를 위해 무엇을 만드는지, 실제 사용 흐름과 현재 구현, 확정된 요구와 중요한 선택·이유, 아직 모르는 사항 |
| `plan.md` | 남은 결과물과 우선순위, 작업 사이의 실제 선행 관계 |
| `seams.md` | 구성 요소 사이에서 제공하고 사용할 인터페이스의 위치·입출력·동작과 오류 의미 |

이 문서들은 작업자가 프로젝트의 목적과 자기 역할을 이해할 수 있을 만큼 구체적이어야 한다. 함수의 정의나 자료 형식이 이미 코드에 있으면 해당 파일과 심볼을 연결한다. 별도의 인터페이스가 없는 프로젝트라면 그 사실을 적는다.

다음으로 `settings.json`에 작업 사본의 범위와 실행 명령을 지정한다.

```json
{
  "snapshot_paths": ["src", "pyproject.toml"],
  "max_workers": 3,
  "command": ["codex", "exec", "--json"]
}
```

`snapshot_paths`는 `REPO` 안에 존재하는 파일·디렉터리의 상대 경로 목록이다. 작업자가 구현하고 확인하는 데 필요한 소스를 포함한다. 실행기는 지정한 경로의 현재 파일 내용을 복사한다. 큰 원자료는 작업 지시에서 읽기 전용 경로로 참조할 수 있다.

`max_workers`는 동시에 실행할 task 수다. 생략하면 3이며, manager 한 세션은 이 수와 별도로 실행된다. `command`는 실행 명령의 인수 목록이고, 생략하면 위 예시의 값을 사용한다. 모델·인증·권한 옵션도 이 목록에 지정할 수 있다. manager의 모델과 추론 설정을 따로 고르려면 `manager` 객체의 `model`·`effort`에 해당 CLI가 지원하는 값을 적는다.

마지막으로 작업 대기열인 `queue.json`을 만든다. manager에게 첫 배정을 맡길 때는 빈 목록으로 시작한다.

```json
{"status":"active","tasks":[],"accepted":[]}
```

작업을 미리 배정하려면 [작업 계약](protocol.md)에 따라 queue와 task별 `objective.md`를 준비한다.

## 실행하고 결과를 확인하기

실행기를 시작하는 세션은 호출 세션이 끝나도 살아 있는 **독립된 OS 프로세스**로 실행한다. `run.py`를 Codex의 `exec_command` 같은 명령 세션 안에 직접 실행하면 호출 CLI 종료 시 함께 종료될 수 있다. 명령 도구가 실행 세션 ID를 반환한 것만으로는 독립 실행이 성립하지 않는다.

현재 Windows 환경에서는 WMI/CIM으로 숨김 프로세스를 생성한다. 다음 REPO·RECORDS·ENGINE은 준비한 실제 절대경로로 바꾼다. 실행기가 이미 살아 있는지 먼저 확인한다.

```powershell
$asyncRepo = 'C:/stock2'
$asyncRecords = 'C:/stock2/runs/DATE/ID/execution'
$asyncEntry = 'C:/stock2/services/async-development/run.py'
$asyncArguments = @($asyncRepo, $asyncRecords)
$asyncPython = (& py -3.11 -c 'import sys; print(sys.executable)').Trim()
$asyncShell = (Get-Command pwsh.exe).Source
$asyncOut = (Join-Path $asyncRecords 'runner.stdout.log').Replace("'", "''")
$asyncErr = (Join-Path $asyncRecords 'runner.stderr.log').Replace("'", "''")
$asyncPayload = '& ' + ((@($asyncPython, '-u', $asyncEntry) + $asyncArguments |
    ForEach-Object { "'" + $_.Replace("'", "''") + "'" }) -join ' ')
$asyncPayload += " 1>> '$asyncOut' 2>> '$asyncErr'"
$asyncPayload += "`nexit `$LASTEXITCODE"
$asyncEncoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($asyncPayload))
$asyncStartup = New-CimInstance -ClassName Win32_ProcessStartup -ClientOnly -Property @{ShowWindow=[uint16]0}
$asyncCreated = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
    CommandLine = '"' + $asyncShell + '" -NoProfile -NonInteractive -WindowStyle Hidden -EncodedCommand ' + $asyncEncoded
    CurrentDirectory = $asyncRepo
    ProcessStartupInformation = $asyncStartup
}
if ($asyncCreated.ReturnValue -ne 0) { throw "실행기 기동 실패: $($asyncCreated.ReturnValue)" }
$asyncCreated | Select-Object ProcessId, ReturnValue
```

위 코드는 WMI가 별도 PowerShell 프로세스를 만들고 그 안에서 기존 `run.py REPO RECORDS`를 실행하게 한다. 출력과 오류는 RECORDS의 `runner.stdout.log`·`runner.stderr.log`에 남는다. 예측에서는 발행 후속 절차까지 이어지도록 `$asyncEntry`를 `C:/stock2/tools/forecast.py`, `$asyncArguments`를 `@('start', '실제 RUN 절대경로')`로 바꾸고 같은 방식으로 기동한다. worker 인계 재개는 run.py의 인수에 `--adopt-workers`를 추가한다. 다른 OS에서도 호출 터미널·명령 세션과 수명이 분리되는 OS 기동 방식을 사용한다.

기동 후 생성된 프로세스와 `state.json.runner_pid`가 실제로 살아 있는지, 새 manager/task의 `session.log`가 기록되는지 확인한다. WMI가 반환하는 PID는 바깥 PowerShell의 PID이고 `state.json.runner_pid`는 Python 실행기 PID다. 확인한 PID·RECORDS·로그 위치를 반환하면 준비 세션의 기동 업무는 끝난다. 이후 진행은 실행기와 manager에게 맡기며, 준비 세션을 유지하거나 완료까지 반복 조회·대기하지 않는다. 사용자가 상태나 결과를 요청하면 그때 기록과 실제 프로세스를 읽는다.

기동 실패: 프로세스가 즉시 종료되거나 새 기동 기록이 없으면 출력·오류 로그와 기존 실행 여부를 확인해 원인을 해결한 뒤 다시 기동한다. 살아 있는 기존 실행기가 있으면 중복 시작하지 않는다. 생성 성공 코드만 보고 넘기면 실제로 시작되지 않은 작업을 진행 중이라고 안내하게 된다.

빈 queue로 시작했다면 첫 manager가 작업 지시와 배정을 작성한다. 이후 실행기는 준비된 task를 파견하고, 종료 사건을 manager에게 전달한다. 모든 세션의 시작 메시지에는 [판단 원칙](principles.md)이 포함된다.

진행 상황을 볼 때는 프로세스 상태와 작업 결과를 구분한다.

| 확인할 내용 | 읽을 파일 |
|---|---|
| 어떤 task가 배정·수용·취소됐는가 | `queue.json` |
| 어떤 세션이 실행 중이거나 종료됐는가 | `state.json` |
| task가 무엇을 만들고 확인했으며 무엇이 남았는가 | `tasks/TASK/report.json` |
| 세션이 실제로 어떤 명령과 도구를 실행했는가 | 각 세션의 `session.log` |
| 프로젝트가 현재 어디까지 진행됐는가 | `context.md`, `plan.md` |

프로세스 종료는 작업의 성공을 뜻하지 않는다. manager가 보고와 결과를 확인해 수용해야 후속 task의 선행 조건이 충족된다.

동시 실행 수를 바꿀 때는 수정한 `settings.json`을 원자 교체한다. 즉, 별도 파일에 작성을 끝낸 뒤 원래 파일을 교체해 실행기가 작성 중인 내용을 읽지 않게 한다. `max_workers`는 실행 중에도 반영되며 적용된 값은 `state.json.max_workers`에 기록된다. 상한을 낮춰도 이미 실행 중인 task는 계속 진행한다. 다른 설정은 실행기 시작 시 읽는다.

## 완료·대기·중단을 처리하기

manager가 목표 달성과 최종 review의 수용을 확인하면 queue를 `complete`로 게시한다. 외부 입력이 있어야 진행할 수 있으면 필요한 입력과 이유를 남기고 `blocked`로 게시한다. 두 상태에서는 새 task를 파견하지 않는다. 다시 진행하려면 입력이나 목표·계획을 갱신한 뒤 queue를 `active`로 바꾸고 실행한다.

실행기가 중단됐을 때도 같은 REPO·RECORDS를 위 독립 프로세스 기동 절차에 넣어 재개한다. 종료된 task는 반복 파견하지 않으며, 중단됐거나 보고가 없는 작업은 manager가 남은 파일과 로그를 보고 처리한다. manager 프로세스가 0이 아닌 코드로 종료하면 실행기는 진행 중인 worker의 종료를 기다린 뒤 멈추고 미처리 사건을 남긴다.

queue가 `active`인데도 실행 가능한 task·실행 중인 세션·미처리 사건이 모두 없으면 실행기는 `idle`로 종료한다. 이때는 필요한 후속 배정이나 결과 수용이 빠졌는지 확인한다.

같은 기록에 실행기를 중복 실행할 수 없다. 살아 있는 manager나 worker가 남아 있으면 일반 재개는 거부된다. Windows에서 작업 세션을 유지한 채 실행기만 교체하려면 manager가 끝난 상태에서 실행기 프로세스만 종료한 뒤 다음 명령으로 worker를 인계한다.

독립 프로세스 기동 예시의 `$asyncArguments`를 `@($asyncRepo, $asyncRecords, '--adopt-workers')`로 지정한다. 호출 세션 안에서 전경 실행으로 재개하지 않는다.

인계받은 worker는 새 실행기의 OS 자식이 아니다. 전체 실행을 중단할 때는 `state.json`의 실행기·manager·실행 중 task PID와 각 자손을 함께 확인한다.

## 파일을 찾을 때

개발 기록의 기본 구조는 다음과 같다. 공용 문서와 queue는 manager가 갱신하고, 실행 상태와 작업 사본은 실행기가 관리한다. task는 자기 보고와 필요한 근거를 작성한다.

```text
RECORDS/
  settings.json
  context.md
  plan.md
  seams.md
  queue.json
  state.json
  runner.stdout.log
  runner.stderr.log
  managers/0001/
    inbox.json
    session.log
  tasks/TASK/
    objective.md
    task.json
    inputs/
    base/
    baseline.json
    workspace/
    report.json
    evidence/
    integration.json
    session.log
```

도구의 코드를 살펴볼 때는 `run.py`에서 파견과 manager 호출을, `workspaces.py`에서 사본 생성과 변경 통합을, `check.py`에서 배정·보고 형식 확인을 찾을 수 있다. 역할별 수행 절차와 JSON 형식은 [protocol.md](protocol.md)에 있다.

실행기의 작은 동작 시험은 다음 명령으로 실행한다. 선행 결과에 따른 후속 실행, 작업 사본 분리, 동시 실행 수 변경, 충돌하는 공용 수정의 보호를 확인한다.

```powershell
python ENGINE/tests/test_flow.py
```

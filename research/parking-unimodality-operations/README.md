# 주차 함수 연구의 2시간 주기 운영

이 구성은 Windows 작업 스케줄러가 2시간마다 별도 Codex 운영 담당을 실행하게 한다. 운영 담당은 연구 상태를 읽고 오류·입력 누락을 조사하며, 승인된 목표 안에서 조치하고 연구를 이어간다. 이 문서는 구성의 사용법이며, 실제 등록·실행 상태는 Windows 예약 작업과 로그에서 확인한다.

## 이 세션을 닫아도 되는가

두 예약 작업의 등록과 실제 호출 검사가 끝나면 **이 대화 세션과 Codex 앱 창을 닫아도 된다.** 운영 담당과 연구 실행은 Windows 작업 스케줄러가 각각 시작한다. 이 대화 세션의 자식 프로세스 수명에 의존하지 않는다.

현재 구성은 Windows 사용자 `DESKTOP\wogud`가 로그인한 상태에서 실행한다. 화면 잠금은 가능하지만 로그아웃하거나 PC를 끄면 실행할 수 없다. 절전 중에는 연구가 진행되지 않는다. 예약 시각을 놓치면 실행 가능한 상태로 돌아온 뒤 Windows가 작업을 시작할 수 있도록 StartWhenAvailable을 설정한다. 네트워크와 기존 Codex 인증도 사용할 수 있어야 한다.

## 두 작업의 역할

| 예약 작업 | 역할 |
|---|---|
| `DoMath-Parking-Operator-Cmath` | 2시간마다 상태를 확인하고 필요한 조치를 판단하는 Codex 운영 실행 |
| `DoMath-Parking-Engine-Cmath` | 운영 담당이 필요할 때 시작하는 do-math 연구 실행 |

두 작업은 각각 IgnoreNew를 사용해 자기 중복 실행을 막는다. 연구 정본의 동시 쓰기는 do-math의 writer lock도 보호한다. 운영 모델은 `gpt-5.6-sol`, 추론 수준은 high다. 운영 실행의 상한은 90분이며 Windows 작업의 종료 여유를 포함한 상한은 110분이다. 연구 실행은 인스턴스의 run 설정을 따르고, Windows 작업 상한은 150분이다. 이는 작업·운영 실행 횟수의 무제한 설정과 별개다.

현재 연구의 인스턴스·경로와 실행 파일은 [config.json](config.json)에 있다. 운영 판단 계약은 [OPERATOR.md](OPERATOR.md), 실행 진입점은 [supervisor.py](supervisor.py)다. 재설치는 `install.ps1`을 실행한다. 등록된 같은 이름의 두 작업만 갱신하며 다른 예약 작업은 변경하지 않는다.

## 상태와 보고서

```powershell
Get-ScheduledTask -TaskName 'DoMath-Parking-*' | Select-Object TaskName,State
Get-ScheduledTaskInfo -TaskName 'DoMath-Parking-Operator-Cmath'
Get-Content -Raw C:\math\.skill-workspace\parking-unimodality-20260915\operator\latest-check.json
```

latest-check.json은 마지막으로 끝난 운영 실행의 결과다. 현재 실행 중인 회차는 같은 디렉터리의 `check/` 아래에서 result.json·events.jsonl·report.json을 확인한다. 연구 실행 로그는 `engine/`에 남는다. 사용자 결정이 필요한 질문은 운영 보고서의 user_questions에 저장한다. 이 대화에 자동 알림을 보내는 기능은 포함하지 않는다.

## 일시 정지와 재개

예약 운영과 연구를 함께 일시 정지하려면 다음을 실행한다. HOLD 파일이 새 운영 조치와 연구 시작을 막고, 이미 실행 중인 운영 담당에는 종료 신호로 작동한다. 연구에는 do-math pause를 전달한다.

```powershell
python C:\math\research\parking-unimodality-operations\supervisor.py hold
```

다시 운영하도록 명시적으로 허용할 때는 HOLD를 해제하고 운영 작업을 시작한다. 운영 담당은 다른 유효한 정지 사유가 없는지 확인한 뒤 재개한다.

```powershell
python C:\math\research\parking-unimodality-operations\supervisor.py release
Start-ScheduledTask -TaskName 'DoMath-Parking-Operator-Cmath'
```

예약 호출 자체를 중지하려면 `Disable-ScheduledTask -TaskName 'DoMath-Parking-Operator-Cmath'`를 사용한다. 예약 비활성화는 이미 실행 중인 연구를 정지하지 않으므로, 연구도 멈출 때는 먼저 hold를 실행한다.

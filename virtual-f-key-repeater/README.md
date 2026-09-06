# Virtual F Key Repeater

이 프로그램은 UMDF 2 가상 HID 키보드에서 `F`와 `B`를 함께 누르고 뗀다. 200초 동안 반복 입력한 뒤 `F1`을 한 번 누르고, 500초 동안 입력을 정지한 뒤 `F1`을 한 번 눌러 다음 주기를 시작한다. 한 주기는 약 700초이며, 수동으로 정지할 때까지 반복한다.

## 구성

- `driver/`: Windows에서 HID 키보드로 열거되는 UMDF 2 드라이버
- `controller/`: 가상 키보드의 반복 상태와 간격을 제어하는 프로그램
- `build.cmd`: 드라이버와 제어 프로그램 빌드
- `install-driver.ps1`: 가상 키보드 장치 설치
- `uninstall-driver.ps1`: 가상 키보드 장치 제거
- `run.cmd`: 빌드된 제어 프로그램 실행

드라이버는 제어 프로그램의 신호가 1.5초 동안 끊기면 반복을 자동으로 중단한다. 제어 프로그램이 비정상 종료돼도 키 입력이 계속되는 상황을 막기 위한 안전장치다.

## 요구 사항

- Windows 11 빌드 22000 이상
- Visual Studio 2022의 **C++를 사용한 데스크톱 개발** 워크로드
- Windows 11 SDK 10.0.26100.0
- .NET 8 SDK
- 최초 빌드에서 WDK NuGet 패키지를 받을 인터넷 연결

빌드 스크립트는 Microsoft WDK NuGet 패키지를 복원한 뒤 MSVC로 UMDF 드라이버를 직접 빌드한다. Visual Studio용 WDK 확장은 필요하지 않다.

## 빌드

프로젝트 폴더에서 다음 명령을 실행한다.

```powershell
.\build.ps1
```

또는 `build.cmd`를 더블클릭한다. 결과는 다음 위치에 생성된다.

- 제어 프로그램: `out\controller\VirtualFRepeater.exe`
- x64 드라이버: `out\driver-x64`

## 드라이버 설치

드라이버 설치는 시스템 상태를 변경한다. 개발용 PC나 복구 가능한 테스트 환경에서 진행한다.

1. 시작 메뉴에서 PowerShell을 관리자 권한으로 연다.
2. 개발용 테스트 인증서를 만들고 드라이버 카탈로그를 서명한다.

```powershell
.\trust-and-sign-driver.ps1
```

3. 가상 키보드 장치를 설치한다.

```powershell
.\install-driver.ps1
```

서명 스크립트는 로컬 컴퓨터에 코드 서명용 인증서를 만들고 `LocalMachine\Root`와 `LocalMachine\TrustedPublisher` 저장소에 등록한다. 이 인증서는 이 PC에서 개발용 드라이버 패키지를 시험할 때만 사용한다. 실제 배포에는 Microsoft가 인정하는 드라이버 패키지 서명이 필요하다.

이 저장소는 Secure Boot 해제나 Windows 테스트 서명 모드 활성화를 자동으로 수행하지 않는다.

드라이버 장치를 제거하려면 관리자 PowerShell에서 다음 명령을 실행한다.

```powershell
.\uninstall-driver.ps1
```

테스트 인증서까지 함께 제거하려면 다음 명령을 사용한다.

```powershell
.\uninstall-driver.ps1 -RemoveTestCertificate
```

## 사용

이번 빌드의 드라이버를 설치한 뒤 `run.cmd`를 실행한다. 이전 F 전용 드라이버가 설치되어 있으면 실행 중인 제어 프로그램을 종료하고, 관리자 PowerShell에서 `trust-and-sign-driver.ps1` → `install-driver.ps1` 순서로 실행해 갱신한다. 설치 스크립트는 기존 장치가 있으면 드라이버를 갱신하고, 없으면 장치를 새로 설치한다.

- `F8`: 새 주기 시작 또는 전체 주기 정지. 다시 시작하면 200초 입력 단계부터 시작한다.
- `F9`: 반복을 중단하고 종료
- 기본 반복 간격: 100ms

자동 주기는 다음 순서로 진행한다. 여기서 700초는 주기 시작부터의 누적 시간이다.

| 주기 내 시점 | 동작 |
|---|---|
| 0~200초 | 설정한 간격으로 F·B를 동시에 누르고 뗌 |
| 200초 | 누른 키를 뗀 뒤 F1을 한 번 누르고 뗌 |
| 200~700초 | F·B 입력 정지 |
| 700초 | F1을 한 번 누르고 뗀 뒤 새 주기 시작 |

F1을 누르는 동안에는 F·B를 누르지 않는다. 실제 전환은 Windows 타이머와 HID 보고서 처리 지연만큼 늦어질 수 있다. F8로 정지하거나 F9로 종료하면 자동 F1 전환도 멈추며, 수동 정지 자체는 F1을 누르지 않는다.

반복 간격은 10~60,000ms 범위에서 지정할 수 있다.

```powershell
.\run.cmd --interval 50
```

연결 상태만 검사하려면 다음 명령을 사용한다.

```powershell
.\run.cmd --probe
```

## 동작 경계

이 장치는 Windows HID 계층에 가상 키보드로 나타나므로 Raw Input을 포함한 일반 키보드 소비 경로로 입력이 전달된다. 그러나 장치의 VID/PID와 제품 문자열을 조사하면 가상 장치임을 식별할 수 있다. 특정 프로그램의 보안 정책이나 이용 약관을 우회하기 위한 은폐 기능은 제공하지 않는다.

드라이버 기반 입력은 시스템 전체에 영향을 준다. 반복을 시작하기 전에 입력을 받을 창이 선택되어 있는지 확인한다.

## 검증

다음 명령은 HID 보고서 길이와 장치 ID·버전 일치, 실제 드라이버가 사용하는 주기 코드의 경계 시점·여러 주기 반복·정지·연결 단절·보고서 전달 재시도를 검사한다. 주기 검사는 C 컴파일러(`cl`, `cc` 또는 `gcc`)가 필요하며 가짜 시각을 주입하므로 실제 키 입력 없이 실행된다.

```powershell
python .\tests\validate.py
dotnet build .\controller\VirtualFRepeater.csproj --configuration Release
```

드라이버 구현은 Microsoft의 [UMDF 2 HID 미니드라이버 샘플](https://github.com/microsoft/Windows-driver-samples/tree/main/hid/vhidmini2)을 기반으로 한다.

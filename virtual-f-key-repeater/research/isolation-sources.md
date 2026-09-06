# 가상 HID 입력을 게임 환경에 격리하는 방안

## 조사 범위와 판정 기준

목표는 `F+B` 누름·해제를 200초 동안 반복하고 `F1`을 누른 뒤 500초 쉬는 주기를 반복하는 HID 키보드 입력을 MabinogiEternity가 실행되는 환경에만 귀속시키고, 같은 시간에 다른 일반 창을 입력 오염 없이 사용하는 것이다. `SendInput`, `PostMessage`처럼 특정 창에 소프트웨어 키 메시지를 보내는 방식은 범위에서 제외한다.

여기서 **실제 HID 경로**는 키 보고서가 운영체제의 HID/키보드 장치 경로로 들어가는지를 뜻한다. 물리 USB 장치만을 뜻하지는 않는다. 현재 구현은 `MsHidUmdf.inf`를 사용하는 **UMDF 2 HID minidriver**이며, 표준 키보드 top-level collection을 열거한다. 이는 [INF](../driver/umdf2/VirtualFKeyboard.inx)와 [드라이버 소스](../driver/vhidmini.c)에서 재확인했다. 이 가상 키보드도 Windows HID 경로에는 들어가지만, 같은 Windows 인스턴스 안에서는 일반적으로 포그라운드 데스크톱 입력으로 합쳐진다. 아래 방안은 그 합류 지점을 좌석, VM, 또는 별도 PC 경계로 옮긴다.

사용자는 현재 PC의 자원 부족 때문에 VM을 배제했고, 추가 PC·USB 장비·모니터·입력 장치도 추가할 수 없다고 확정했다. WMI `WmiMonitorID` 조회에서는 활성 디스플레이 1개가 관측되었지만, 이 조회가 시스템이 지원하는 모든 디스플레이 표면과 영상 출력을 전수 보장하지는 않는다. 따라서 ASTER가 **기존 장치만으로** 요구를 만족할 수 있는지를 중심으로 판정한다. 공식 자료에서 MabinogiEternity, 해당 게임의 보호 모듈, 현재 UMDF 2 HID minidriver 조합을 시험한 기록은 찾지 못했다. 따라서 게임 지원을 보장하지 않는다.

## 후보 비교

| 후보 | 격리 경계 | HID 경로 | 일반 창으로 입력 누출 | 주된 미검증·제약 |
|---|---|---|---|---|
| ASTER + Rust VDD | 한 Windows 안의 별도 workplace/session | 현재 가상 HID → 호스트 HID 스택 → ASTER가 게임 workplace에 할당 | 정상 할당이 실제로 적용되면 다른 workplace로 가지 않는 것이 제품 기능의 취지이다. 현재 가상 HID와 게임 입력 방식에서는 미검증 | VDD 가상 모니터의 workplace 할당은 ASTER v3 공식 구성. 로컬 화면 보기·게임·현재 HID 조합은 미검증 |
| 게임을 VMware Workstation VM에 배치 | 게스트 Windows | USB HID를 호스트에서 분리하여 게스트 USB/HID 스택으로 연결 | USB 장치를 `Connect (Disconnect from host)`로 게스트에 귀속하면 호스트는 그 장치를 사용할 수 없다 | Workstation 게스트 그래픽은 공식적으로 DirectX 11까지 명시; DX12 게임과 보호 모듈은 미검증 |
| 게임은 호스트, 업무를 VMware VM에 배치 | 업무용 게스트 Windows | 반복 가상 HID는 호스트/게임에 유지; 업무용 물리 키보드는 USB 전용 할당으로 게스트에 연결 가능 | 전용 USB 키보드는 연결 중 호스트에서 분리된다. VM 화면의 일반 키보드 캡처만 쓰면 포커스에 의존하므로 강한 장치 격리가 아니다 | 업무 VM 사용성·자원 비용. 게임은 네이티브 GPU/호스트에 남아 VM 그래픽·게임 호환성 위험을 피함 |
| Hyper-V VM | 게스트 Windows | Enhanced Session/RDP 장치 리디렉션; 직접 USB 패스스루는 아님 | 리디렉션 대상과 세션 상태에 의존 | Microsoft는 Hyper-V에 네이티브 직접 USB 패스스루가 없다고 명시. 키보드 HID의 전용 귀속 수단으로는 근거 부족 |
| 게임 전용 별도 PC + 현재 드라이버 | 별도 Windows 커널과 물리 PC | 현재 가상 HID → 게임 PC의 HID 스택 | 업무 PC로는 구조상 누출되지 않음 | PC 추가 비용·공간·전력. 게임/보호 모듈이 현재 드라이버를 허용하는지는 그대로 미검증 |
| 게임 PC + 물리 USB HID 생성기 | 별도 USB 장치와 게임 PC | 마이크로컨트롤러 USB device → 게임 PC USB/HID 스택 | 생성기를 게임 PC에만 꽂으면 업무 PC로 누출되지 않음 | 펌웨어 제작과 운용 장치 필요. 게임이 해당 HID 보고를 수용하는지는 실기 검증 필요 |

## 1. ASTER 멀티시트

### 구조

ASTER는 한 PC와 한 Windows 인스턴스에 여러 workplace를 만들고, 모니터·키보드·마우스를 workplace별로 할당한다. 게임을 한 workplace에서 실행하고 일반 작업을 다른 workplace에서 수행하는 구조다. 현재 가상 HID 키보드가 ASTER 제어판에 별도 키보드로 나타난다면 게임 workplace에만 할당하는 것이 후보가 된다.

### 실제 HID 경로와 누출 판정

입력은 현재 가상 HID에서 호스트 Windows HID 스택으로 들어간다. 그 뒤 ASTER의 좌석 할당 계층이 해당 키보드 입력을 게임 workplace에 귀속시키는 구조로 추정된다. 이 마지막 설명은 ASTER가 키보드를 workplace에 배분한다는 공식 기능 설명에서 도출한 **추론**이며, 벤더가 내부 입력 필터 구조를 공개한 근거는 아니다.

ASTER 공식 설정 문서는 키보드와 마우스를 특정 workplace에 할당한다고 명시한다. 따라서 정상적으로 인식·할당된 장치라면 다른 workplace에 키 입력이 나타나지 않는 것이 제품 기능의 취지다. 그러나 공식 제한 문서는 ASTER가 표준 시스템 이벤트를 기준으로 장치를 분리하며, 드라이버가 표준 Windows 메커니즘을 우회하면 분리할 수 없다고 밝힌다. 현재 UMDF 2 HID minidriver가 ASTER에서 별도 장치로 표시되는지, MabinogiEternity가 ASTER의 좌석 분리 뒤 입력만 읽는지는 공식 자료로 확인되지 않았다.

### 제약

- ASTER 설정 문서는 추가 workplace를 시작하기 전에 모니터를 할당해야 하고, 모니터가 연결되지 않은 workplace는 시작되지 않는다고 명시한다. 키보드·마우스 등 나머지 장치는 workplace를 시작한 뒤 할당할 수 있다고 별도로 설명한다. 따라서 별도 마우스의 부재를 **시작 불가 조건**으로 단언할 수는 없다. ASTER의 “모니터 없는 workplace” FAQ는 대안으로 더미 패널이나 한 물리 모니터의 여러 입력 단자에 PC 출력을 복수 연결하는 방법을 제시한다. 둘 다 사용 가능한 영상 출력과 연결 경로가 더 필요하다.
- ASTER의 현재 v3 공식 가이드는 MolotovCherry의 Rust Virtual Display Driver(VDD)가 만든 가상 모니터를 ASTER workplace에 할당하는 구성을 명시한다. 가이드는 VDD에서 최대 10개 모니터를 만들고, ASTER 제어판에서 `2.x`로 표시된 VDD 모니터를 각 workplace에 할당한 뒤 자동 로그인을 설정하는 절차를 제공한다. 따라서 `Rust VDD 가상 모니터 → ASTER workplace`라는 **기본 조합은 공식 지원 구성**이다. 일반적인 모든 IDD와 ASTER의 호환성까지 확장해서 해석하지 않는다.
- 가이드가 지정한 [MolotovCherry/virtual-display-rs](https://github.com/MolotovCherry/virtual-display-rs)는 Windows 10 2004 이상 x64에서 최대 10개의 가상 모니터·복수 해상도·주사율을 제공한다고 밝힌 공개 Rust 드라이버다. 저장소는 보관 상태가 아니며 GitHub API의 마지막 push는 2025-03-03이다. 최신 정식 릴리스는 v0.3.1(2023-10-22)이고, README는 인증서 설치 후 MSI 또는 portable driver를 설치하라고 안내한다. 즉 소스 저장소 활동은 확인되지만 최신 정식 릴리스가 최근이라고 표현해서는 안 된다.
- Microsoft의 IDD 모델도 소프트웨어 가상 모니터가 가능한 Windows 구조임을 뒷받침한다. 다만 Microsoft IddSample은 ASTER 가이드가 지정한 Rust VDD가 아니며, production용으로 완성된 드라이버도 아니다. 현재 설치 실험 금지 때문에 Rust VDD의 열거와 ASTER 할당은 이 PC에서 실측하지 않았다.
- 현재 가상 HID가 두 번째 workplace의 키보드로 인식될 가능성은 있지만 **미검증**이다. 공식 문서는 물리·가상 HID를 구분해 지원한다고 밝히지 않는다. 게임 workplace에 별도 마우스를 할당하지 않은 상태의 실제 조작 가능 범위도 초기 설정 시험 항목으로 남는다.
- 한 Windows 인스턴스이므로 CPU, 디스크, GPU, 네트워크 주소를 공유한다. ASTER 제한 문서도 무거운 작업이 다른 workplace의 입력 지연을 일으킬 수 있다고 명시한다.
- 공식 제한 문서는 최신 v3에서 Memory Integrity와의 비호환 및 Secure Boot 비활성화를 요구한다. 실제 설치 전에는 사용하려는 ASTER 판본과 현재 Windows 빌드의 요구사항을 다시 확인해야 한다.
- ASTER 이력에는 WDDM 2.5/2.6(DirectX 12) 지원 추가가 기록되어 있다. 이는 ASTER의 그래픽 계층 지원 기록일 뿐, MabinogiEternity나 그 보호 모듈의 호환성 증명이 아니다.
- 전체 화면 게임용 “special graphical modes”는 성능을 높일 수 있으나 동작하지 않거나 BSOD를 일으킬 수 있다고 공식 문서가 경고한다.
- 벤더는 게임에 쓸 수 있다고 광고하면서도, 보호 시스템과 공유 자원 때문에 일부 게임에 문제가 있을 수 있고 실제 소프트웨어·하드웨어 조합을 체험판으로 사전 시험하라고 안내한다. 그러므로 게임 지원 주장은 이 조사에서 채택하지 않는다.

### 공식 출처

- [ASTER v3 설정: 장치 할당](https://dokwiki.ibiksoft.com/en/v3/core/ugd/ugd_config) — workplace마다 모니터·키보드·마우스를 준비하고, 키보드/마우스를 특정 workplace에 드래그하거나 메뉴로 할당한다고 설명한다. 복합 입력 장치의 모든 부분을 함께 할당하라고도 명시한다.
- [ASTER v3 기능과 제한](https://dokwiki.ibiksoft.com/en/v3/core/faq/faq_limitations) — 표준 시스템 이벤트를 벗어나는 장치 드라이버는 좌석별로 분리할 수 없고, 단일 OS의 디스크·네트워크·자원을 공유한다고 설명한다. Memory Integrity, Secure Boot, 절전 관련 제한도 열거한다.
- [ASTER v3 시스템 요구사항](https://dokwiki.ibiksoft.com/en/v3/core/faq/faq_config) — Windows 8/8.1/10/11과 사용자별 입력 장치·모니터 요구를 설명하고, 실제 프로그램과 하드웨어의 사전 시험을 권한다.
- [ASTER 버전 이력](https://dokwiki.ibiksoft.com/en/v3/core/history) — v2.26에서 WDDM 2.5/2.6(DirectX 12) 지원을 추가했다고 기록한다.
- [ASTER 실험적 그래픽 설정](https://dokwiki.ibiksoft.com/en/v2/core/gui/gui_unsupportedsettings) — 전체 화면 게임용 특수 그래픽 모드가 실패하거나 BSOD를 낼 수 있다고 경고한다.
- [ASTER 가정용/게임 설명](https://dokwiki.ibiksoft.com/en/v2/core/solutions/typapplications/home) — “대부분의 게임”이라는 벤더 주장과 함께, 보호 시스템·공유 자원 때문에 실행 제약이 생길 수 있음을 명시한다. 전자는 광고성 일반론이며 이 게임의 호환 근거가 아니다.
- [ASTER: 모니터 없는 workplace FAQ](https://www.dokwiki.ibiksoft.com/en/v2/core/faq/faq_terminals) — workplace 실행에는 모니터 연결이 필요하고 더미 패널 또는 한 모니터의 여러 입력 단자에 출력을 복수 연결하는 방법을 제시한다. 이 FAQ의 물리 대안 외에 아래 v3 가상 디스플레이 가이드가 별도로 존재한다.
- [ASTER v3: 가상 디스플레이 원격 workplace 구성](https://dokwiki.ibiksoft.com/en/v3/core/article/virtualdispalys) — Rust VDD 설치, 가상 모니터 생성, ASTER workplace 할당, 사용자별 자동 로그인, Parsec의 Per User 설치와 원격 접속까지 설명한다. 작성자는 IBIKSOFT ASTER Tech Support Manager로 표시되어 있다.
- [MolotovCherry Rust Virtual Display Driver](https://github.com/MolotovCherry/virtual-display-rs) — ASTER 가이드가 지정한 VDD의 원 저장소다. Windows 10 2004+ x64, 최대 10개 가상 모니터와 제어 앱을 명시한다.
- [Rust VDD 릴리스](https://github.com/MolotovCherry/virtual-display-rs/releases) — 최신 정식 릴리스가 v0.3.1이며 인증서 설치 필요와 해당 릴리스의 하드웨어 커서 미지원 제한을 명시한다.
- [Microsoft: Indirect Display Driver 개요](https://learn.microsoft.com/en-us/windows-hardware/drivers/display/indirect-display-driver-model-overview) — IDD가 원격 표시와 가상 데스크톱용 가상 모니터를 만들 수 있는 UMDF 디스플레이 드라이버 모델임을 설명한다.
- [Microsoft: IddSample](https://github.com/microsoft/Windows-driver-samples/tree/main/video/IndirectDisplay) — 소프트웨어 장치를 인스턴스화하고 모니터 하나를 열거하는 샘플이지만, production 사용에는 INF 수정과 TODO 구현이 필요하다고 명시한다.

### 한 화면에 다른 workplace를 표시하는 우회

표준 RDP는 이 목적의 안전한 뷰어로 확인되지 않았다. ASTER v3 제한 문서는 Windows Home/Pro의 RDP가 다중 사용자용이 아니며 원격 로그인이 로컬 RDP workplace를 로그오프시키고 그래픽 분할과 충돌할 수 있다고 설명한다. 따라서 RDP를 ASTER 추가 workplace의 동시 표시 경로로 채택할 기술적 근거가 부족하다.

ASTER v3 가이드는 VDD workplace마다 Parsec을 **Per User**로 설치하고 계정별 로그인한 뒤, 원격 PC에서 해당 workplace에 접속하는 표시 경로를 공식 구성으로 제시한다. 이는 VDD가 ASTER workplace의 시작 전제를 해결하고 Parsec이 그 화면을 전달하는 구조다. 그러나 가이드는 별도 원격 PC를 전제로 한다. 같은 PC의 기존 모니터에 Parsec으로 자기 workplace를 연결하거나 view-only 썸네일로 띄우는 구성은 설명하지 않는다.

ASTER v2 FAQ는 TeamViewer·UltraVNC 같은 프로그램도 서비스/미러 드라이버 방식이면 추가 workplace에 연결할 수 없고, 각 세션에서 사용자 응용 프로그램 인스턴스로 실행해야 한다고 설명한다. 이는 기존 모니터에 추가 workplace를 창 또는 썸네일로 표시할 가능성을 시사하지만, 해당 화면이 게임의 DirectX 전체 화면을 안정적으로 캡처하는지, view-only 상태에서 UMDF HID가 게임 workplace에만 남는지, 성능이 충분한지는 공식 자료로 확인되지 않았다. 화면 전달 프로그램은 가상 키보드의 ASTER 장치 할당과 별개이므로, 화면을 보기만 한다고 HID 격리가 자동 보장된다고 추론하지 않는다.

공식 출처: [ASTER v3 가상 디스플레이+Parsec 구성](https://dokwiki.ibiksoft.com/en/v3/core/article/virtualdispalys), [ASTER v3 RDP 제한](https://dokwiki.ibiksoft.com/en/v3/core/faq/faq_limitations), [ASTER v2 원격 접근 FAQ](https://www.dokwiki.ibiksoft.com/en/v2/core/faq/faq_terminals).

## 2. VM을 이용한 격리

VM은 장치 경계를 분명하게 만들 수 있지만 현재 사용자 조건에서는 제외한다. 실측 환경은 Windows 11 Pro 22631, i5-4570 4코어/4스레드, RAM 약 16 GiB, GTX 970이며 펌웨어 가상화가 비활성화되어 있다. 사용자는 자원이 부족하다고 판단했고 가상화 활성화도 요구 범위를 벗어난다.

기능상 VMware는 USB HID를 `Connect (Disconnect from host)`로 게스트에 전용 연결하고, VID/PID·이름·포트 경로로 자동 연결할 수 있다. 기존 물리 키보드·마우스를 게스트에 독점 귀속할 수 있으므로 추가 장치가 항상 필수인 것은 아니다. 다만 그러면 호스트에서 그 장치를 사용할 수 없다. 게임을 VM에 넣으면 공식 그래픽 지원이 DirectX 11/OpenGL 4.3까지만 확인되어 DX12와 게임 보호 모듈을 검증할 수 없다. Hyper-V는 Microsoft 문서상 네이티브 직접 USB 패스스루가 없다.

공식 출처: [VMware USB HID 전용 연결](https://knowledge.broadcom.com/external/article?legacyId=1033435), [VMware USB 자동 연결](https://knowledge.broadcom.com/external/article/343950/automatically-connecting-usb-devices-at.html), [VMware 그래픽 지원](https://www.vmware.com/products/desktop-hypervisor/workstation-and-fusion), [Microsoft Hyper-V USB 제한](https://learn.microsoft.com/en-us/troubleshoot/windows-server/virtualization/usb-device-hyper-v-virtual-machine).

## 3. 별도 PC 또는 물리 USB HID 생성기

별도 게임 PC에서 현재 드라이버를 실행하면 별도 Windows 커널이 입력을 격리한다. 물리 USB HID 생성기는 `마이크로컨트롤러 → 게임 PC USB/HID 스택 → 게임` 경로를 만들어 업무 PC에 입력이 열거되지 않게 한다. Raspberry Pi 공식 예제는 USB keyboard descriptor와 보고 전송 구현을 제공한다. 두 방식은 각각 추가 PC 또는 USB 장비를 요구하므로 사용자 조건에서 제외한다. 게임·보호 모듈 호환성도 미검증이다.

공식 출처: [Raspberry Pi 공식 pico-examples](https://github.com/raspberrypi/pico-examples), [HID 보고 전송 코드](https://github.com/raspberrypi/pico-examples/blob/master/usb/device/dev_hid_composite/main.c), [HID keyboard descriptor](https://github.com/raspberrypi/pico-examples/blob/master/usb/device/dev_hid_composite/usb_descriptors.c).

## 현재 조건에서의 판정과 남은 검증

추가 하드웨어와 VM을 제외하면 **ASTER + MolotovCherry Rust VDD**가 공식 문서로 뒷받침되는 주력 실험 후보이다. WMI에서는 활성 디스플레이 1개만 관측됐지만, Rust VDD가 가상 모니터를 만들고 ASTER가 이를 workplace에 할당하는 기본 조합은 ASTER v3 공식 가이드에 있다. 설치가 허용되는 후속 단계에서 VDD 열거, ASTER 할당 또는 workplace 시작이 실패하면 이 경로를 중단해야 한다. 별도 원격 PC 없이 기존 모니터에 게임 workplace 화면을 표시하는 방법, 현재 UMDF 2 가상 키보드의 게임 workplace 전용 할당, 게임의 입력 수용과 성능은 별도 검증이 필요하다.

향후 제약이 바뀌거나 설치 없는 추가 검증이 가능해지면 다음 사실을 확인해야 한다.

1. MabinogiEternity의 현재 렌더러가 DX12를 필수로 쓰는지, DX11 경로가 있는지 확인한다.
2. 게임 및 보호 모듈의 VM, 멀티시트, 가상 HID, 물리 프로그래머블 HID 정책을 공식 약관·지원 답변으로 확인한다.
3. ASTER 후보에서는 체험판으로 현재 가상 HID가 독립 키보드로 표시되는지, 게임 workplace에만 할당되는지, 다른 workplace의 편집기에 F/B/F1이 한 번도 나타나지 않는지 시험한다.
4. VMware 업무 VM 후보에서는 두 번째 물리 키보드를 USB 전용 연결한 뒤 VM 창이 포커스를 잃어도 호스트에 키가 나타나지 않는지 시험한다.
5. 모든 후보에서 200초 반복 입력 종료와 중지·오류·전원 전환 때 F와 B의 key-up 보고가 보장되는지 확인한다.

공식 자료만으로 확인 가능한 범위에서는, ASTER v3가 Rust VDD 가상 모니터를 workplace에 할당하고 Parsec Per User로 원격 표시하는 기본 조합을 직접 안내한다. 이 조합은 추가 물리 모니터 없이 workplace를 시작하는 공식 지원 구성으로 볼 수 있다. 그러나 별도 원격 PC 없는 로컬 표시, MabinogiEternity, 현재 UMDF 2 HID minidriver의 workplace 전용 입력, 게임 보호 모듈과 성능은 가이드의 보장 범위 밖이며 검증되지 않았다. VM, 별도 PC, 물리 USB HID 생성기는 사용자가 확정한 자원·장비 제약 때문에 선택지가 아니다.

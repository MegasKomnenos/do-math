## 목적과 역할

G7의 실제 OS 예약 경계를 닫는다. 설계 8절의 T5는 시험 이름의 등록·pythonw 발화·해제를 요구한다. 현재 boundary.test_port_scheduler는 status만 실제 호출하며, boundary.test_operator_schedule_adapter의 등록 시험은 cmdlet 대역이다.010의 실제 pythonw 출력·Job 성공과012 Lean 성공으로 이 공백을 대신하지 않는다. 기존 제품 포트·PowerShell 어댑터·bootstrap을 그대로 사용해 최소 T5와 실제 예약 조회 녹화/재생을 추가한다.

이번 work는 새로운 시험·작은 helper·scheduler corpus/필요 최소 reader·지침·미러에 한정한다. runtime 결함이나 OS 조건이 드러나면 반례와 정확한 후속 범위를 반환한다. 학술·유료 공급자·Lean 재실행·L01 결정을 함께 묶지 않는다.

## 완료 조건

### A1 시험 소유 등록과 실제 설치 freeze를 확인

시작 소스와012 manager source-inspected를 대조하고 Windows/PowerShell/Python/pythonw의 경로·판본·SHA, Task Scheduler 서비스·현재 사용자 실행 조건을 비밀 없이 기록한다. 환경 전체나 인증 자료는 덤프하지 않는다. 자기 evidence 또는 공식 scratch 아래 새 repository 좌표와 workspace·새 instance 식별자를 사용한다. `supervision.task_names`가 만든 정확 세 이름이 OS에 모두 없음을 실제 status로 확인한 후에만 생성한다. 기존 이름이 있으면 덮지 말고 충돌 없는 새 좌표를 택한다. 생성 요청/성공과 cleanup 대상 이름을 실행 전에 자기 근거에 남긴다.

현재 `real_ports`와 `scheduled_operator.schedule`를 통해 실제 `PowerShellScheduler.run`·`operator_schedule.ps1`의 install을 실행한다. cmdlet·runner·bootstrap·스케줄러 포트를 대역으로 교체하지 않는다. 실제 pythonw freeze의 stdout JSON과 exit, manifest·snapshot 파일·등록 action/인자/WorkingDirectory·현재 Interactive/Limited principal·설정을 확인한다. engine의 무제한 실행 설정과 operator의 현행 설정 의미를 보존한다. 유효한 현 인자로 interval/timeout을 지정하며 새 제한을 제품에 추가하지 않는다.

새 workspace에는 현재 제품 `scheduled_operator.hold`로 HOLD를 먼저 기록하고 시험 동안 유지한다. 이는 공개 제품의 모델 호출 전 보류 경로를 사용해 OS 발화만 검사하기 위한 입력이다. 기존 연구를 생성·재개하거나 실제 모델 호출로 진행하지 않는다. 설치 freeze가 복제하는 것은 현재 제품이며 bootstrap을 합성 실행 파일로 바꾸지 않는다. 현 held 경로가 외부 호출을 막는지 코드와 필요한 자기 입력 대조로 확인한 뒤 실제 작업을 시작한다.

### A2 T5에서 실제 pythonw 발화·wake·해제를 입증

`smoke.test_scheduler_live`를 공식 T5 discovery와 `resource` 격리에 연결한다. install한 자기 operator/engine의 start 동작과 가까운 미래의 one-shot wake 등록을 실제 경로로 실행한다. wake는 실제 OS 시각 트리거로 발화해야 하며 직접 함수 호출이나 start 요청 수락으로 대체하지 않는다. `WakeAt/WakeKey`, task 이름·XML/action의 pythonw 및 live/frozen bootstrap 좌표, 등록·실행 전후의 실제 시각·상태·LastRunTime/LastTaskResult 등 원자료를 결속한다. 직전 결과0을 재사용하지 말고 이번 발화의 새 실행·종료를 관찰한다. 가능한 프로세스/작업 이벤트·PID/command 근거도 보존하되 관측하지 못한 stdout이나 내부 결과를 꾸미지 않는다. freeze에서 수집한 stdout과 OS task의 실행 관측을 구별한다.

보류된 실제 bootstrap의 정상 종료와 외부 모델/기존 연구에 부수 효과가 없음을 확인한다. 모델-free held 경로 성공은 연구 엔진의 실제 운전 성공을 뜻하지 않는다. 예약 조회만 성공하거나 권한 거부·환경 부재·발화 미관측이면 해당 A는 pass가 아니다. 실제 오류/환경 조건과 필요한 결정만 보고하고 권한 상승·서비스 설정·계정 정책을 변경하지 않는다.

자기 wake에 cancel-wake를 적용하고, 성공/실패 모두 finally에서 자기 세 task만 uninstall한다. cleanup 전 이름뿐 아니라 시험의 action/workspace 소유 증거도 확인한다. 실행 중이면 자기 것으로 결속된 작업/프로세스만 종료·회수하고 마지막 실제 status의 세 null과 자기 자원 종료를 확인한다. 다른 예약의 중지·재등록·해제를 하지 않는다. 소유 자원 정리에 실패하면 정확 이름·상태·오류와 필요한 후속 조치를 최우선 finding으로 남긴다. 시간은 소프트 기준이며 관찰 도구의 대기 만료를 성공·실패·변이 포착으로 바꾸지 않는다. 새 hard timeout을 도입하지 않는다.

### A3 새 실제 예약 녹화와 현재 parser를 연결

기존 scheduler_json reader와 manifest 계약을 읽고 실제 등록 상태와 해제 후 부재 상태를 작은 원출력 녹화로 추가한다. 정확 argv/cwd·판본·시각·exit·시험 이름·원바이트 SHA와 녹화 당시 판정을 결속한다. 재생은 현 `PowerShellScheduler`의 JSON 수신 경계를 사용한다. 가능하면 기존 reader를 그대로 사용하며 새 실제 입력이 요구할 때만 최소 확장한다. OS 관측 보조자료와 출하 corpus의 범위를 명시하고, 합성 출력이나 재직렬화 JSON을 원녹화라고 쓰지 않는다.

현재19항목·양쪽56파일·총112경로의 기존 비manifest 바이트/항목/verdict는 보존하고 manifest에는 새 항목만 추가한다. 기존 Lean full/preview·공급자 판정을 유지한다. 양쪽 corpus 전건의 명시 SHA·파일 선언·5MiB 상한·Git raw/clean·생성 바이트와 corpus3모듈을 확인한다. 유효한 등록이 불가능하면 부재/실패 자료만으로 실제 발화 완료를 주장하지 않는다.

### A4 관련 회귀·이력·미러와 인계를 완결

원문 설계3.3/4.5/5.1/8과 결함 범주9-C, 현 시험 지침을 대조한다. `0dd16a5e`의 예약 포트 분리 및 `a0e6c2f4`의 예약/pythonw freeze 수리 중 이번 경계의 실제 diff·현재 소비자·존재하는 원보고만 검토한다. 이 두 commit의 다른 Lean/도메인/저장 변경은 범위 밖이다. 현재 boundary 단언과010의 승인된 pythonw 성질은 유지하며 없는 역사 보고 counts를 새 성공으로 합산하지 않는다.

최종 정본 새 scheduler T5, `boundary.test_port_scheduler`, `boundary.test_operator_schedule_adapter`, `contracts.test_port_scheduler`, `structure.test_corpus`, `unit.test_corpus_replay`, `contracts.test_doubles_follow_corpus`, `structure.test_test_smells`, `structure.test_boundary_invariants`, `structure.test_ports`를 공식 runner로 확인한다. 새 helper가 실제 소비하는 계약에 꼭 필요한 선택만 추가한다. 선택/고유row/실제exit와 실행 전후 해시를 보존하며 skip/error/미실행을 pass로 세지 않는다. 전체 일반/T3/변이는 실행하지 않는다.

지침에 OS 권한·로그온 조건·시험 이름/소유 범위·보류 입력의 의미·실행 원자료·실패시 정리·한계를 적는다. 공식 생성기의 사전 계획을 writes에 대조하고 생성한다. 미러의 새 scheduler 실실행과 같은 관련 회귀를 순차 완료한 뒤 비용 캐시만 공식 재동기화하고 --check/skill-only를 확인한다. 기존 runtime124·공급자 입력3·host/Lean 입력·corpus의 불변과 도구 조건을 대조해 기존 승인 근거를 한정 재사용한다. 각 A, 외부 부수 효과와 정리, 미충족 조건·나머지 G를 report에 남긴다.

## 판단과 경계

모델은 gpt-6.1-sol/high. phase.json의 신규 smoke/helper·scheduler corpus/manifest·필요 최소 replay·시험 지침·캐시와 대응 미러만 수정한다. 제품 runtime·PS 어댑터·bootstrap·기존 boundary·생성 규칙/속성·공용 문서·engine·원보고는 수정하지 않는다. 실제 제품 결함이면 반례를 남기고 후속 work에 필요한 정확 파일/조건을 제안한다. 무관한 개선을 따라가지 않는다.

원문 G7에 따른 시험 소유 OS task의 생성·발화·취소·해제와 자기 workspace/snapshot 쓰기는 허용된다. 대상은 시작 때 부재를 확인한 새 좌표의 정확 세 task다. 기존 예약·연구·계정/서비스 설정 변경, 권한 상승, 설치/다운로드, 유료 호출, Git stage/commit/reset/checkout/push 및 graphify 갱신은 하지 않는다. 현재 코드·계약에서 확인 가능한 판단은 직접 해결한다. 계약/권한 개정이 필요하면 해당 부분만 미완료로 보고하고 가능한 독립 산출물은 완결한다. L01 Q1/Q2는 이 task가 결정하지 않는다.

## 검증 방법

cwd `C:\math`, Python `C:\Users\wogud\AppData\Local\Programs\Python\Python312\python.exe`. 정본/미러 공식 run_tests.py에 `-u -B`, 정확 선택과 `--jobs 1 --output <자기 evidence의 새 폴더>`를 사용한다. `--tier T5 --list`로 discovery만 확인하며 전체 T5를 실행해 공급자·Lean을 재호출하지 않는다. 동시에 한 검사 묶음만 실행하고 제품/시험 소스를 고정한다.

실제 argv/cwd/PID/시각/exit·stdout/stderr, OS task before/after·정리와 원자료 SHA를 보존한다. 진행 중 result.json은 기존 read_bytes_shared로 읽는다. 생성/실행 권한 거부는 원자료에 근거해 A 실패 또는 not_run과 finding을 연결한다. 자기 자원 cleanup은 실패 뒤에도 수행한다. 마지막 `python -B services/continuous-development/check.py report C:\math C:\math\docs\do-math\continuous-development-2026-10-13 013 scheduler-smoke`를 통과하고 report 경로와 상태를 반환한다. 학술·T4 adapter 보고·문서/의미 질문·G4~G6/G8 및 최종 review는 후속 manager의 책임이다.

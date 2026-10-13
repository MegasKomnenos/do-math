## 목적과 역할

G7의 남김 중 실제 Windows Job 작업자 연쇄와 pythonw 부모의 출력 회수를 공식 T5에 연결한다. 공급자 최소 호출은003/006에서 검수했고009까지 runtime·smoke입력·corpus가 보존됐다. 이 작업은 유료 모델 호출을 반복하지 않고 OS가 실제 제품 실행 경로의 가정을 만족하는지 확인한다. Lean/Mathlib·예약 등록/발화/해제·학술 MCP는 다른 후속 작업이다.

설계5.5의 T5와 결함-범주5.9의 B-01/B-25/C-09, 기존 boundary의 실제 Job/worker/pythonw 검사를 읽는다. 포트·worker·수신기를 대역으로 바꿔 통과시키지 않는다. 외부 모델 프로그램을 결정적 로컬 실행 파일로 대신한 부분은 실제 공급자 호출과 구별한다. 같은 phase의 reading-limits는 고정된 운전 문서/CLI와 호스트만 읽고 제품 시험·캐시·미러에 접근해 쓰지 않는다. 그 결과를 기다리지 않는다.

## 완료 조건

### A1 현재 실경계와 기존 검사의 책임을 특정

시작 HEAD·dirty·제품 소스 해시를009 manager 검수와 대조한다. manager의 관리 커밋과 제품 바이트를 구별한다. Job 생성/보류/시작/작업자/외부 자식/회수/종료 확인의 실제 호출 경로와 pythonw→PowerShell→제품 명령→JSON/exit 수집 경로를 각각 구체적 파일·심볼로 연결한다. 기존 boundary 중 이미 충분한 성질과 T5에 빠진 설치 연쇄를 구별한다. 현재 포트 계약과 시험 입력을 재사용하며 새 runtime API나 시험 등록부를 만들지 않는다.

관련 과거 검토는 closure-map prior-review-state의 Job/pythonw/프로세스 slice만 현재 코드·도입 diff·존재하는 원보고와 대조한다. 없는 원보고의 counts는 새 성공으로 쓰지 않는다. 다른 PR 영역까지 전수 감사하지 않는다. 재사용/교정/추가 판단과 근거를 자기 evidence의 review.md에 남긴다.

### A2 실제 Job·pythonw 연쇄를 최소 T5로 연결

`tests/smoke/test_host_live.py`와 필요하면 `tests/support/host_live.py`를 사용한다. 최소 성질은 실제 제품 worker의 시작 식별자와 실제 Job 소유, 정상 출력/종료 회수, 명시 취소 또는 owner 정리에 따른 자손 종료·빈 Job 확인, pythonw 부모에서 PowerShell이 실행한 제품 명령의 온전한 JSON과 정확한 exit 회수다. Python 실행 파일·PowerShell 판본·부모 console 유무·실제 argv/cwd·PID/FILETIME/Job 식별·stdout/stderr·원 출력 파일과 파싱 결과·정리 결과를 자기 evidence 또는 공식 runner의 보존 scratch에 기록한다. 값은 실제 관측으로 얻고 성공을 손으로 채우지 않는다.

기존 test_scheduling_windows_job/owned_job_children의 kernel 관측과 test_role_input_snapshot_reach의 pythonw 실제 read 연쇄를 출발점으로 삼는다. 공유할 필요가 있는 기존 준비/검사 코드는 허용된 support 한 곳으로 옮기고 양쪽이 사용하게 한다. 시험 모듈을 다른 시험에서 import하지 않으며 같은 성질의 큰 시나리오를 복사하지 않는다. 기존 단언을 제거하거나 대역으로 바꾸지 않는다. 새 경로에는 정상 출력과 정확한 비정상 exit/오류의 구별을 확인하되 제품 내부 패치로 음성을 만들지 않는다.

운전 인터프리터가 pythonw여도 제품이 지급하는 CLI 명령은 현 console_python 계약을 따른다. PowerShell 예약 cmdlet 대역으로 얻은 등록 결과를 실제 예약 성공으로 보고하지 않는다. OS 예약 변경은 하지 않는다. 명시 취소/해제는 자신이 생성·식별한 child/Job에만 적용하고 연구 인스턴스나 서비스 프로세스를 중단하지 않는다. 시간 경과만으로 성공/실패/변이 포착을 만들지 않는다.

### A3 공식 선택과 실제 결과·실패 근거를 보존

`run_tests.py --tier T5 --list`에 기존 provider 두 건과 새 host 시험이 포함됨을 확인한다. 실행은 `--tier T5 smoke.test_host_live`로 host만 선택하여 최소 한 번 완결하고 선택 ID·고유 결과 row·counts·실제 exit·소스 전후를 연결한다. 필요한 환경이 없거나 실제 경계 실패가 있으면 skip을 성공으로 세지 않고 해당 A를 fail/not_run으로 보고한다. 구현/시험 수리 후에는 실패 ID와 영향받는 관련 선택만 다시 실행하고 원 실패를 보존한다.

직접 변경·공유화한 기존 boundary 시험과 관련 port 계약/구조 시험을 검사한다. 기존 boundary의 충분한 정상/오류/종료 증거를 T5 보고와 연결하되 별개 실행을 한 실행처럼 합치지 않는다. 새 host 결과를 공급자·Lean·예약·학술 전체 T5 성공으로 넓히지 않는다. 실행 중에는 제품/시험을 고정하고 이 task만 jobs1·한 묶음씩 사용한다.

### A4 미러·사용법·후속 책임을 인계

시험-지침의 T5 설명에 host 선택·실제 자원·원자료 위치·한계를 필요한 만큼 추가한다. 공식 생성 계획이 phase writes 안인지 먼저 확인하고 정본 변경과 대응 미러만 생성한다. 미러 host 선택도 실제 실행하고 최종 비용 캐시는 공식 재동기화한다. 생성기 --check와 probe_cli --skill-only를 통과한다. 기존 공급자 runtime·smoke·corpus가 불변이면003/006~009의 한정 재사용 조건을 유지한다. 새 제품 경계 결함은 원재현·영향 G/A·필요한 쓰기 범위와 함께 반환하며 허용되지 않은 runtime을 임의 수정하지 않는다.

report에는 A1~A4, 실제 변경·검사·자원 정리, 새 T5가 검증한 성질과 미검증 부분을 기록한다. 녹화는 합성 corpus로 만들지 않고 원파일/해시/판본을 보존한다. 현재 corpus 형식에 없는 OS 자료를 넣으려고 manifest/parser 계약을 확장하지 않는다. 다른 G7 연쇄와 G4~G6/G8은 남는다.

## 판단과 경계

task 모델은 gpt-6.1-sol/high다. 쓰기는 phase.json의 host 시험/지원·공유화 대상3개 boundary·시험 지침·비용 캐시와 대응 미러로 한정한다. runtime·공급자 smoke·corpus·생성 규칙·공용 문서·engine·다른 task 자료·사용자 설정은 수정하지 않는다. 단일 task가 정본/미러와 공유 캐시를 소유하므로 미완성 타 구현이나 새 seam이 없다. 구현 선택은 위 성질 안에서 재량이다.

기존 연구 시작/재개/삭제, 유료 모델 호출, OS 예약 등록/변경, graphify 갱신, Git stage/commit/reset/checkout/push를 하지 않는다. 필요한 새 테스트 파일과 임시 입력은 자신이 소유한 출력/scratch에만 만들고 보존할 원자료를 지우지 않는다. 실패를 숨기려고 새 예외·fallback·환경 skip을 추가하지 않는다. manager가 검수와 Git 마감 및 후속 연결을 맡는다.

## 검증 방법

cwd C:\math, Python C:\Users\wogud\AppData\Local\Programs\Python\Python312\python.exe. 공식 정본 runner `.claude/skills/do-math/scripts/run_tests.py`, 미러 runner `.agents/skills/do-math/scripts/run_tests.py`에 `-u -B`, 정확 선택, `--jobs 1 --output <자기 evidence의 새 경로>`를 전달한다. 프로세스 argv/cwd/PID/시작·종료/exit와 stdout/stderr, 소스 전후를 보존한다. 실행 중 result 관찰은 file_io.read_bytes_shared를 사용한다.

관련 선택의 출발점은 boundary.test_scheduling_windows_job, boundary.test_scheduling_owned_job_children, boundary.test_scheduling_call_jobs, boundary.test_role_input_snapshot_reach, boundary.test_port_jobs 및 contracts.test_port_jobs다. A1에서 변경·검증 성질에 맞는 정확 ID를 정하고 근거를 남긴다. Pythonw 성공/반려는 현재 SnapshotReadToolTests의 실제 경로를 확인한다. 불필요한 전체 boundary/T5 유료 호출이나 전체 일반/T3/변이는 실행하지 않는다.

공식 미러 생성기 `.claude/skills/writing-skills/scripts/build_skill_mirrors.py`와 정본 `probe_cli.py --skill-only`를 사용한다. 마지막에 `python -B services/continuous-development/check.py report C:\math C:\math\docs\do-math\continuous-development-2026-10-13 010 host-smoke`를 통과하고 report 경로와 상태를 반환한다.

## 목적과 역할

G7의 미완료 중 Lean/Mathlib 실제 연쇄를 닫는다. 기존 설치의 존재와 --version 성공, Python 컴파일러 대역의 setup 시험, 옛 Lean 출력 재생을 실제 Mathlib 컴파일 성공으로 확대하지 않는다. 현재 `setup_lean.verify_environment`, `formal.inspect_toolchain/verify_lean`, `real_ports`를 사용해 T5 선택에 최소 실환경 검사를 연결하고 원자료를 보존한다. 011에서 검수한 host/회귀·공급자 경로와 읽기 문구는 보존한다.

이 work의 범위는 Lean smoke·그 녹화/재생·시험 지침과 대응 미러다. runtime·설치 상태를 바꿀 필요가 드러나면 재현과 필요한 쓰기 범위를 보고하고, 가능한 독립 산출물을 끝낸다. 예약·학술·공급자 재호출·읽기 한도는 이 task에 묶지 않는다. 새 소규모 helper와 smoke 파일의 분리는 내부 선택이며 새 제공자/소비자 seam은 없다.

## 완료 조건

### A1 현재 설치와 실제 대표 Mathlib 컴파일을 결속

시작 소스/설치 조건을 기록하고 011 manager source-inspected와 대조한다. `.skill-workspace/do-math-toolchains`의 실제 경로를 현 `toolchain_root/discover_lean`에서 확인한다. 001 당시 portable 경로는 탐색 단서이며 상수가 아니다. PATH 부재를 미설치로 단정하지 않는다. 명령·Lean/Lake 실행 파일 SHA/판본·Mathlib 프로젝트의 lean-toolchain/lake-manifest/ready marker 및 실제 의존 좌표를 확인한다. 토큰·인증 원문이나 사용자 전체 환경을 덤프하지 않는다.

현재 `real_ports`의 jobs/clock/environment/git_backend를 전달해 `inspect_toolchain`과 `setup_lean.verify_environment`를 실제로 실행한다. `trust_inventory.validation_program(identity)`가 선택한 Mathlib 대표 프로그램, 원 소스 SHA, 정확 argv/cwd, 시작/종료·Job/PID 및 exit/stdout/stderr와 validation.json을 보존한다. 기대 scope는 Mathlib 프로젝트를 반영한 현 계약이며, core-only 프로그램을 Mathlib 성공으로 세지 않는다. `import Mathlib`와 현재 대표 증명이 설치된 도구에서 통과해야 한다. `--version`·ready marker만으로 A1을 통과시키지 않는다.

기존 설치/신뢰 기록을 승인·재기록·수정하지 않는다. 설치기 main이나 다운로드/cache get/lake update를 실행하지 않는다. 읽기·기존 캐시 소비 외 쓰기가 필요하면 먼저 현재 명령의 실제 부수 효과를 확인하고, 자신의 evidence/공식 scratch 밖 설치 입력을 고치지 않는다. 환경 미충족은 정확한 실패·필요 조건으로 보고한다.

### A2 T5가 실제 검증 결과와 오류를 검사

새 `smoke.test_lean_live`를 공식 T5 discovery에 연결한다. 현재 분류 규약의 `lean` 격리를 사용하고 필요 최소 helper를 `support/lean_live.py`에 둔다. 기존 `support.entry`, real_ports, formal 및 setup helper를 재사용하며 compiler·Job·clock·parser·검증기를 대역으로 바꾸지 않는다. 현 Mathlib 명령으로 이름 있는 작은 정상 선언을 `verify_lean`에 전달해 실제 kernel 성공, 요청 선언의 정확 집합, 서명/서명 해시·axioms 및 해당 증거를 검사한다. 정상 source와 선언은 제품 계약/수학적 내용으로 정한다. 매 실행 출력에서 기대값을 그대로 복사해 검사를 만들지 않는다.

정상 선언과 짝을 이루는 명확한 Lean 형식/타입 오류 입력을 실제 실행해 nonzero exit·failed와 컴파일 진단을 확인한다. 거부/부재/환경 실패를 성공·포착으로 세지 않는다. 제품 전체 의존 증거를 새로 평가할 필요가 있으면 `extract_evidence=True`의 실제 결과를 사용하고, preview(`False`)는 그 한계를 명시한다. 최소 T5는 정상/오류와 대표 Mathlib 컴파일이 실제 경로를 지났음을 입증한다. 이전 경계 시험의 전체 입력축을 smoke로 복제하지 않는다.

실행은 jobs1, 한 묶음씩 한다. soft 예산 초과는 기록하되 시간 초과를 새 성공/실패/종료 규칙으로 만들지 않는다. 자신이 만든 Job의 종료와 자손 회수, 추가 자원 없음 및 자기 임시 파일 정리를 확인한다. 원자료는 공식 결과의 scratch 또는 evidence에 남기고 다른 프로세스·기존 연구는 건드리지 않는다.

### A3 새 실제 녹화와 현재 재생을 연결

실제로 얻은 작은 정상 Lean 출력·source·compiled input·판본/명령/시각/판정을 corpus에 추가한다. 기존 `lean_output` 계약과 현재 `unit.test_corpus_replay._lean_output`의 preview/full 범위를 먼저 확인한다. 가능한 기존 reader로 충분한 녹화를 사용한다. 실제 새 형식에 필요한 경우에만 해당 reader를 확장하고 기존 두 Lean 항목의 판정을 보존한다. 전체 evidence와 출하 corpus의 보존 범위를 구분하며, 자른 출력은 범위·원파일 SHA·절단 이유를 명시한다. 합성·다시 작성한 stdout을 실제 녹화라고 쓰지 않는다.

기존 18항목·각51파일(총102경로)의 원바이트/기존 verdict는 유지하고 manifest에 새 항목만 추가한다. 새 자료의 명시 SHA·모든 파일 선언·5MiB 상한을 검사한다. 원/미러 corpus 전건 Git raw/clean·생성 바이트를 확인한다. 공급자 녹화/속성/생성규칙은 바꾸지 않는다. 기존 `structure.test_corpus`, `unit.test_corpus_replay`, `contracts.test_doubles_follow_corpus`를 전체 실행해 옛/새 녹화의 제품 parser 결과와 대역 불변식을 확인한다.

### A4 관련 회귀·이력 검토·미러와 인계를 완결

원문 설계 3.3/4.5/5.1/5.6 및 9-C, 현재 시험 지침을 대조한다. 이 작업이 접하는 B38/8afa57c7의 formal/setup Git 포트 slice만 실제 diff·현 소비자·원보고 selector로 검토하고 유지/교정 필요를 적는다. 이미 검수된 host/console 성질은 새 반례 없이 재검토하지 않는다. 없는 원보고의 과거 counts를 새 성공으로 세거나 PR02 전체를 종료하지 않는다.

최종 새 Lean smoke를 정본에서 완결하고, 관련 오프라인 corpus 3모듈과 `boundary.test_setup_lean_compile`, `boundary.test_knowledge_lean_verifier`, `structure.test_test_smells`, `structure.test_boundary_invariants`, `structure.test_ports`를 현재 공식 선택으로 확인한다. 새 helper가 읽는 공유 계약에 따라 꼭 필요한 관련 선택을 더할 수 있으나 전체 일반/T3/변이를 실행하지 않는다. 선택/고유row/exit·전후 소스가 대응해야 하며 skip/error/미실행을 pass로 세지 않는다.

시험 지침에 새 T5의 실행·원자료·외부 조건·정리와 한계를 적는다. 공식 생성기의 사전 변경 계획을 writes와 대조한 뒤 생성하고 미러의 새 smoke 및 corpus/구조 관련 검사를 완결한다. 미러 Lean 실실행은 독립 경로 연결 확인이며 유료 호출이 아니다. 성공한 기존 host/공급자 T5는 입력/경로 불변을 근거로 재사용한다. 실행 뒤 비용 캐시만 공식 동기화하고 --check/skill-only를 확인한다. runtime124·공급자 입력3 및 host 입력의 불변을 대조한다. 각 A·검사·변경·실제 외부 상태·후속 G를 report에 기록한다.

## 판단과 경계

모델 gpt-6.1-sol/high. 쓰기는 phase.json의 신규 smoke/helper, Lean corpus 하위와 manifest, 필요 최소 replay 시험, 시험 지침·비용 캐시와 대응 미러뿐이다. 기존 Lean 녹화의 바이트는 보존한다. runtime/setup 본체·다른 시험·규칙·공용 context/plan/seams·engine·원보고는 수정하지 않는다. 새 검사·전체 생성기가 다른 미완성 시험과 캐시를 읽고 corpus manifest를 공유하므로 한 task가 소유한다. 이 phase에 병행 시험 task는 없다.

Git stage/commit/reset/checkout/push, graphify 갱신, 설치 다운로드/환경 설정 변경, 신뢰 기록 채택/수정, OS 예약 등록/변경, 새 유료 모델 호출, 기존 연구 시작·재개·삭제는 하지 않는다. 실제 기존 도구를 사용한 새 시험의 자기 evidence/scratch 쓰기와 자기 Job 정리는 허용된다. runtime 결함이나 설치 조건으로 A를 충족할 수 없으면 반례와 필요한 후속 조치를 반환한다. 이 작업은 L01의 Q1/Q2를 결정하지 않는다.

## 검증 방법

cwd `C:\math`, Python `C:\Users\wogud\AppData\Local\Programs\Python\Python312\python.exe`. 공식 정본 runner `.claude/skills/do-math/scripts/run_tests.py`, 미러 `.agents/skills/do-math/scripts/run_tests.py`에 `-u -B`, 정확 선택, `--jobs 1 --output <자기 evidence의 새 폴더>`를 사용한다. `--list`로 새 smoke가 T5 선택에 들어가는지 확인하되 전체 T5를 실행해 공급자를 다시 호출하지 않는다.

원 argv/cwd/PID/시각/exit·stdout/stderr와 선택/고유row·실행 전후/최종 소스 해시를 보존한다. result.json 관찰은 기존 read_bytes_shared를 사용한다. 실행이 길어져도 process가 살아 있는 상태를 timeout 실패로 바꾸지 않는다. 실제 실패 후에는 원자료를 보존하고 필요한 수정/검사만 반복한다. 구조 검사·형식 검사는 실컴파일 성공의 대체가 아니다.

최종 `python -B services/continuous-development/check.py report C:\math C:\math\docs\do-math\continuous-development-2026-10-13 012 lean-smoke`를 통과하고 report 경로와 상태를 반환한다. 전체 일반/fresh T3/전함수 변이, 실제 예약·학술, 나머지 문서/의미 질문 및 최종 review는 후속 manager의 책임이다.

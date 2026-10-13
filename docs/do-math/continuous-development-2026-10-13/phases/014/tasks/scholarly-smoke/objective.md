## 목적과 역할

G7의 학술 MCP 최소 실제 연결을 검증한다. 지금 corpus의 scholarly_config는 command/args 해석 녹화이고 실제 list_sources 성공이 아니다. probe_cli.run_case의 scholarly_actual_tool도 native 시작 사건의 도구명만 확인한다. 기존 제품의 Codex worker·실제 서버를 통해 성공 완료 응답을 확인하고, 현 T5와 원녹화 재생에 연결한다. 공급자 maintenance·host/Lean/예약 성공은 승인된 범위로 재사용한다. 새로운 학술 검색 기능이나 연구 운전을 구현하는 작업이 아니다.

## 완료 조건

### A1 실제 입력과 격리 경계를 확정

시작 소스를013 manager source-inspected와 대조한다. 현재 resolve_scholarly_server가 선택한 command/args와 해석 기준 파일, Codex 실행 파일/판본/SHA, 서버 실행 파일·Python/패키지 판본과 list_sources/registry 소스를 비밀 없이 기록한다. 다른 설정·환경·인증 파일 전문을 덤프하지 않는다. 실제 프로젝트 설정은 scholarly 테이블만 읽고 값은 현재 validator로 검증한다. 사용자·프로젝트 설정, 서비스·venv·설치·인증을 변경하지 않는다.

기존 ModelRunner/real_ports/worker/adapter/collector를 사용하고 worker의 실행별 scholarly-data 경로가 새 시험 workspace 안임을 실제 요청/worker snapshot/argv로 확인한다. 기존 probe_cli.run_case(files, scholarly=True)를 그대로 호출하고 그 결과를 추가 검증하는 방식 등 기존 경로를 우선 재사용한다. 제품 내부/실제 CLI/서버를 대역으로 바꾸거나 MCP 우회 호출만으로 제품 연결을 대신하지 않는다. 새 helper는 두 소비자가 공유할 검증이 있을 때만 둔다. 환경 부재나 runtime 결함이면 정확 실패·필요 조건과 후속 파일을 반환하고 해당 A를 pass로 만들지 않는다.

### A2 최소 실제 list_sources의 성공 완료와 종료를 T5로 확인

새 smoke.test_scholarly_live를 resource 격리와 T5 discovery에 연결한다. 정본에서 실제 Codex 호출 한 번을 기본으로 실행한다. 제품 실호출 기본은006에서 성공한 명시 model=gpt-6-astra, effort=low이며 CLI 경로/판본/실제 요청을 남긴다. 개발 task의 gpt-6.1-sol/high와 구별한다. 변경·실패로 새 호출이 필요하면 이유를 기록하고 최소화하며 성공한 동일 호출을 이유 없이 반복하지 않는다.

실제 list_sources 시작과 같은 요청의 성공 완료(native ID/server/tool/result 또는 현재 CLI의 대응 구조)를 연결한다. 요청 수락·도구명·모델의 성공 주장만으로 통과시키지 않는다. native 오류/isError·중단·응답 부재/파손은 실패다. 실제 응답의 status=ok와 sources의 유일한 ID 및 각 summary 필드를 설치 서버 registry/Source.summary의 현재 계약과 대조한다. 고정 개수/현재 출력 전체를 새 정본으로 복제하지 않는다. 공급자가 표현한 content/structuredContent를 구별하며 본문 전문 누락을 허용하지 않는다. MCP 초기화/도구 판본·서버 코드와 응답의 근거를 보존한다. 모든 자료원에 접근하거나 검색·fetch가 성공했다는 뜻으로 확대하지 않는다.

protocol_probe의 실제 파일/nonce·checkpoint·최종 구조화 결과, worker 요청/스냅샷과 native 원자료·종료 barrier/Job 회수를 확인한다. 호출은 list_sources 하나와 지정 로컬 파일 작업에 한정한다. 문헌 search/fetch·브라우저/로그인·다른 모델/에이전트 호출·기존 연구 재개는 하지 않는다. 실서버의 시험 데이터는 새 workspace에 두고 자기 자원을 회수한다. 인증/도구 조건 부재·응답 오류는 정확히 보고하며 시간만으로 실패/성공을 만들지 않는다.

### A3 실제 녹화와 현 parser의 재생·반례를 연결

실제 native stream/필요 최종 응답·stderr·요청/설정의 안전한 좌표·판본·시각·exit·SHA와 당시 판정을 corpus/scholarly에 추가한다. 원바이트를 재직렬화·발췌해 전체 원녹화로 표시하지 않는다. 필요 안전한 파생물은 원녹화와 별개로 출처/변환/제외 범위를 명시한다. 기존21항목/verdict·양쪽 비manifest122경로를 보존하고 manifest에는 새 항목만 추가한다. 민감한 환경값은 출하하지 않는다.

현재 codex_stream과 실제 수신 경계가 있는 경우 그 정의를 재사용해 녹화 재생을 연결한다. native MCP 결과에 제품 parser가 의미 판정을 제공하지 않으면 시험 전용 관찰자임을 밝히고 live와 replay가 공유하는 작은 정의를 사용한다. 새 범용 MCP parser나 제품 schema를 복제하지 않는다. 시작만 있음/오류 완료/누락·불완전 source 목록이 성공으로 판정되지 않는 의미 있는 반례를 기존 corpus 시험에 함께 검증한다. 정상 실제 녹화는 대조군이다. 생성 기대값을 같은 관찰자 결과만 복사해 정당화하지 않고 서버 계약/원자료와 대조한다.

양쪽 corpus 전건의 명시 SHA·파일 선언·5MiB 상한·Git raw/clean·미러 바이트와 corpus3모듈을 확인한다. scholarly_config의 기존 판정은 유지하며 실제 list_sources 녹화와 구별한다.

### A4 관련 회귀·이력·미러와 보고를 완결

설계3.3/4.5/5.1/8·9-C와 현 지침을 대조한다. 이번 입력/격리 경계의 과거 도입 commit은 git log로 좁혀 실제 diff·현재 소비자·존재하는 원보고만 확인한다. 이미 검수한003/006 공급자 slice를 전수 재검토하거나 없는 역사 counts를 새 성공으로 더하지 않는다. 검토 대상과 유지/추가/미확인 판단을 명시한다.

정본 새 T5 한 건, 관련 오프라인 unit.test_academic_scholarly_config, unit.test_academic_scholarly_validation, structure.test_corpus, unit.test_corpus_replay, contracts.test_doubles_follow_corpus, structure.test_test_smells, structure.test_boundary_invariants, structure.test_ports를 공식 runner로 실행한다. 기존 실제 입력/worker 배선에 새 변경이 있으면 해당 계약 선택만 추가한다. 선택/고유row/실제exit와 실행 전후 판본을 보존한다. skip/error/미실행을 통과로 세지 않는다. 전체 일반/T3/변이·기존 다른 T5는 실행하지 않는다.

지침에 실제 호출 설정·서버 조건·격리/정리·시작/완료 구별·녹화/관측 한계를 적는다. 공식 미러 생성 전 변경 계획을 writes에 대조하고 생성한다. 미러는 같은 관련 오프라인 선택·녹화 재생과 변환 바이트를 검증한다. 정본의 현재 실호출 경로와 미러의 변환 차이를 확인하고 재사용 범위를 명시한다. 미러의 유료 실호출은 기본으로 반복하지 않으며 오프라인 검사를 실제 미러 호출로 보고하지 않는다. 그 차이가 실호출 근거 재사용을 가리면 이유를 밝히고 필요한 최소 호출을 수행한다. 마지막 비용 캐시만 공식 동기화하고 --check/skill-only를 확인한다. 기존 runtime124·공급자/host/Lean/예약 입력과 원자료의 불변/도구 조건을 대조해 한정 재사용하고 다른 G의 미완료를 유지한다.

## 판단과 경계

phase.json의 새 smoke/helper·corpus/scholarly와 manifest·필요 최소 corpus 검사/reader·지침·캐시와 대응 미러만 수정한다. 제품 runtime/probe_cli/기존 공급자 smoke·scholarly 서버/registry·설정/설치·공용 문서·engine·원보고는 수정하지 않는다. runtime 또는 외부 서비스 수리가 필요하면 재현 입력·기대/실제·정확 후속 범위를 반환한다. 실제 서버 list_sources와 Codex 최소 실호출 및 자기 workspace 쓰기는 G7 범위에서 허용된다. 기존 연구·예약·다른 계정/서비스 변경, 권한 상승, Git stage/commit/reset/checkout/push·graphify 갱신은 하지 않는다. L01 운전 프로필·출력 단위 선택이나 전체 G 완료를 이 task가 결정하지 않는다.

## 검증 방법

cwd C:\math, Python C:\Users\wogud\AppData\Local\Programs\Python\Python312\python.exe. 공식 정본/미러 run_tests.py를 -u -B, 정확 선택, --jobs 1 --output <자기 evidence의 새 폴더>로 한 묶음씩 실행한다. --tier T5 --list는 discovery만 확인한다. 실제 실행/실호출/PID/시각/exit·요청/worker/native stdout/stderr·종료·원자료 SHA를 남긴다. 진행 중 result.json은 기존 read_bytes_shared로 읽는다. 실환경 검사를 못 하면 해당 A와 정확 외부 조건을 보고하고 독립 오프라인 작업은 완결한다. 시간은 소프트 기준이며 자동 timeout을 추가하지 않는다.

마지막 python -B services/continuous-development/check.py report C:\math C:\math\docs\do-math\continuous-development-2026-10-13 014 scholarly-smoke를 통과하고 report 경로/상태를 반환한다. T4 별도 adapter 보고·나머지 문서/의미 질문·L01·G4~G6/G8 및 최종 review는 후속 manager 책임이다.

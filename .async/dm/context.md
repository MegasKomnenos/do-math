# do-math 비동기 개발의 현재 맥락

## 전환과 권위

2026-10-15 사용자가 현재 개발을 멈추고 `services/async-development`로 재개하라고 지시했다. 이전 continuous-development 실행기와 실행 중이던029 manager 및 자손은 중지됐다. 이 실행의 source_repo는 C:/math, records는 C:/math/.async/dm, engine은 C:/math/services/async-development다. 현재 진행의 정본은 이곳의 context/plan/seams/queue/state이며 과거 phase 기록은 보존된 원자료다. 새 서비스의 protocol.md와 principles.md를 읽고 적용한다. 과거 phase barrier, manager.json/next, task의 공용소스 직접 수정 절차는 이 실행에 적용하지 않는다.

사용자 목표·판단·개별 성과의 세부 사항은 `sources/legacy/context.md`, `sources/legacy/plan.md`, `sources/legacy/seams.md`에 전환 직전 원문 그대로 보존했다. 원래 대화 결정은 C:/math/docs/do-math/continuous-development-2026-10-13/sources/user-decisions.md, 모델 지정과 묶음 지시는 같은 sources의 model-policy-2026-10-14.md와 document-batching-2026-10-14.md다. legacy 원문 속 run: 참조는 모두 C:/math/docs/do-math/continuous-development-2026-10-13 기준이다. repo:는 새 작업자의 workspace 내부 소스 또는 manager의 source_repo를 뜻한다. 과거 원보고의 경로·판본은 바꾸지 않는다.

## 이관 검수 완료와 현재 시작판

async manager 0001은 중단된 029/doc-names의 A1~A5와 F1의 지정 여덟 발견을 이관된 시작판의 성과로 수용했다. 현재 2675개 스킬 소스는 029 manager source-inspected 및 task 종료판과 전건 일치한다. 이관 snapshot 2681파일도 원래 해시와 같고, 추가 6파일은 루트 지침·설정이다. 원task 129파일은 불변이다. 현재 diff에서 정본10·미러10·비용캐시2의 범위, setup/probe의 실제 parser 공유, 문서 helper의 실제 정의 소비와 새 단언을 확인했다. 최종 c2/m2는 각각 183선택·183고유 passed·exit0이고 각875Python SHA가 현재와 같다. 기존38문서ID와 여덟 finding의 정확 시험ID도 그 결과에 포함된다. 새 제품 시험과 외부 호출은 실행하지 않았다.

판정의 정본은 `managers/0001/inheritance-review.json`과 `review.md`다. 과거 `phases/029/manager.pending.json`, 공용 문서와 M-0579는 중단 당시 초안으로 그대로 보존하며, 거기에 적힌 게시·압축·커밋 예정 표현을 완료 사실로 사용하지 않는다. 원task·제품 원바이트·중단로그·초안은 `managers/0001/legacy-029-raw.zip`과 `preservation.json`에 보존한다. 검수한20비캐시 제품경로의 관리 마감은 이번 manager의 commit 기록으로 연결한다. 기존 dirty/untracked·비용캐시·과거 관리초안은 이 작업의 제품 변경에 섞지 않는다.

029는 새 workspace task가 아니므로 integrate하거나 queue.accepted에 추가하지 않는다. 새 async 결과부터 실제 workspaces.py integrate와 accepted 절차를 따른다. 029 F2는 유지한다. parser·문구 변경은 설치/prompt hash를 바꾸므로 과거 전체 설치·실호출 판본 동등성이나 모델 독해를 재인증하지 않는다. 불변 하위경계 성질과 실제 관련 회귀만 재사용한다. L01 Q1/Q2와 원문 UTF-8 byte 미충족, Windows1314 symlink 실반려 미검사, G4~G8 및 다른 의미 질문은 열려 있다.

현재 새 배정은 r02(요청 생산·수신), r07(반환 소유권 모집단), r18(실제 외부 경계 호출)의 세 독립 work다. 기존030은 실행되지 않은 후보 원문이며 새 objective가 workspace/보고/경로 규약을 대체한다. 모두 제품 writes와 depends_on이 비어 있다. 같은 읽기 질문을 전수 감사나 문서 작업으로 확대하지 않으며, 각 완료 사건에서 확인된 공백만 후속 구현·관련 검증에 연결한다.

## 모델·권한·자원

worker는 gpt-6.1-sol/high, manager는 gpt-6-astra/xhigh, 독해 기본은 gpt-6.1-sol/high다. settings의 공통 model config와 각 task.model/effort에 명시하고 모델 부하 오류를 성공으로 바꾸지 않는다. max_workers=3. 개발 시간은 소프트 기준이며 정확성을 희생하거나시간만으로시험실패/변이포착을판정하지않는다. push·graphify갱신·기존연구재개/삭제는하지않는다. 서비스전환은 기존 외부실험권한을 확대하지않는다.

## 격리·비동기 통합의 실제 사용

worker는 base/inputs를 보존하고 workspace의writes만 수정한다. C:/math 공용소스와 다른task 기록은 읽기전용이다. manager만 workspaces.py integrate로 충돌확인 후 결과를 통합·수용한다. independent task는 최대3개 동시진행하며 완료사건마다 검수한다. 모든동료의종료를기다리는옛phase장벽을만들지않는다. depends_on은실제선행결과만표시한다. 같은파일/공유helper 수정은한task로묶거나수용뒤후속으로배정해불필요한통합충돌을줄인다. 독립소스사본의정적조사는병렬진행하고 캐시/미러도자기사본에서다룬다.

공식검사에는workspace의scripts/run_tests.py를쓰고 실제불확실성을해결하는최소범위를선택한다. worker당기본jobs1, 동시시험worker합계3이하. 공유실환경/예약/도구설치변경과전체관문은동시실행하지않도록manager가배정한다. 최종G4~G8은원래명시된완료요건이므로최소검증원칙을이유로삭제하지않는다. snapshot의Git메타데이터는없다. 과거Git조회는명시적으로 git -C C:/math를읽기전용사용하고, fixture는저장소밖짧은임시경로에자기Gitrepo를만든다. 실행환경 GIT_CEILING_DIRECTORIES는 records/tasks로두어workspace에서상위C:/math를자기repo로오인하지않게한다. --skip-git-repo-check는Codex기동용이다. 제품Git동작의대체근거가아니다.

snapshot_paths는현재skills정본·미러·생성규칙과필요한루트지침이다. 각workspace는그파일의당시바이트를받는다. 과거대형증거/docs/기억/설치toolchain은C:/math의원문을필요부분만읽는다. workspace에없는과거report를누락된제품파일로오인하지않는다. 실Lean/도구는절대경로로읽기전용연결하며제품설치루트의차이는검증입력에명시한다. 범위확장이필요하면manager가settings snapshot을수정하고README의재시작절차를따르되전체원자료를무작정복사하지않는다.

임시자료는 workspace밖 task/evidence 또는저장소밖짧은임시경로에쓴다. Windows의긴cwd/상위Git탐색문제를반복하지않게짧은task ID와출력경로를쓴다. live JSON관찰은do_math.file_io.read_bytes_shared를사용한다. 최종source고정·선택/실제row·exit·판본은필요한검증에서보존하고이미충분한근거를새이유없이반복하지않는다. task는Gitcommit하지않고manager만검수된자기변경을commit-harness의필수기억/색인과함께관리마감한다. 관리작문/기록을위해제품전개를매번과도하게멈추지않는다.

## C1 사용자 목표와 완료 기준

결함이 시험을 빠져나가는 기제를 막는 것이 목표다. 실제 제품 경로를 시험하고 대역은 외부 경계에 두며, 계약·불변식에서 기대값을 얻고, 이전 개선을 보존한다. 정확성·합리적인 개발 속도·유지 비용을 함께 만족해야 한다. 출발 요구와 사용자의 교정은 C:/math/docs/do-math/continuous-development-2026-10-13/sources/user-decisions.md, 원문 위치와 시작 상태는 C:/math/docs/do-math/continuous-development-2026-10-13/sources/baseline.json 및 C:/math/docs/do-math/continuous-development-2026-10-13/sources/requirements-index.json에 있다. 요구 목록이 아니라 검토 가능한 증거로 아래 기준을 충족해야 한다.

### G1 원문 기능·시험 의무

원래 1단계 19개와 2단계 11개 의무의 명시 모집단·입력축·성질을 현재 구현과 시험에 연결한다. 실제 생산/수신, 저장, 형식·부재/null, 전이, 진행성, 정산, 역할·근거, 대기·계수, 시간·발동, 기동·운전·문서를 포함한다. 각 ID에 충족한 성질, 증거 판본, 구체적 남김과 판정이 있다. 목록 존재·설명·형식 검사만으로 의미 검증을 대신하지 않는다. 원문에 없는 무한 입력 공간의 무결함 증명을 새 종료조건으로 만들지 않는다.

### G2 기존 개선과 기대값 보존

원래 K ID의 보존 성질 61개와 원래 P2 12개 ID를 각각 현행 근거에 연결한다. K ID는 K-01~K-78 안의 비연속 집합이며 sources/requirements-index.json의 preservation 모집단을 따른다. 과거 원문의 timeout 등 폐기된 수단은 최신 사용자 지시와 현재 계약으로 처리한다. 기존 변경 재검토는 실제 diff·현재 소비자·원보고를 사용해 유지/교정/제거/추가 판정 필요를 결정한다. B01~B109를 25영역에 매핑했다는 사실은 검토 완료가 아니다. 결함 동작을 정상 기대값으로 남기지 않는다.

### G3 검증 방식의 실질

실제 제품 코드를 대역으로 가리는 시험, 현재와 다른 fixture, 속도 때문에 약해진 단언, 실제 최종 반환을 증명하지 못하는 문서용 AST 추정 등을 해소한다. 부류·등록·일반 검사가 현재 구성원을 실제로 검사하며 누락을 실패로 드러내는지 확인한다. 구현 방식의 복잡성과 실익을 검토하고 불필요한 장치를 늘리지 않는다. 의미 검토와 최종 실행 대기를 구분한다.

### G4 최종 판본 전체 일반 검사

최종 제품·시험 판본에서 공식 run_tests.py의 기본 전체 선택을 완결한다. 선택과 실제 결과가 전건 대응하고 실패·오류·미실행이 없어야 한다. 조건부 환경 건너뜀은 원문 계약상 정당성을 별도 판정하고 통과로 세지 않는다. 실행 전후 소스 해시와 종료 상태를 보존한다. B129의 실패 보고와 이후 부분 수리를 더해 전체 성공으로 만들지 않는다.

### G5 재사용 없는 최종 T3

최종 판본의 --tier T3 --full 실행으로 측정 누락 없는 분기 합집합과 함수 진입/선택 색인을 확보한다. 미도달은 실제 누락을 수리하거나 원문상 정당한 제외의 근거를 검토한다. 과거 수치·증분 캐시·부분 선택을 fresh 전체 증거로 대체하지 않는다.

### G6 대상 함수 전체의 극단 변이와 정상 기준

현재 대상 함수·변이 종류·선택 시험·정상 기준의 모집단을 실제 코드와 T3 자료로 확정한다. 기존 17개 파일 분할은 실행 준비의 출발점이며 고정된 함수 수가 아니다. 정상 기준 통과와 각 변이의 실제 결과를 대응시킨다. 시간 초과·측정 부재·환경 실패를 변이 포착으로 세지 않으며 생존·미실행을 숨기지 않는다.

### G7 실제 경계와 말뭉치

T4의 실제 구현 계약, T5의 최소 공급자 실호출 및 Job·Lean/Mathlib·예약·학술 도구 등 요구된 실제 연쇄를 현재 환경에서 확인한다. 공급자별 최소 호출을 실제 녹화와 함께 사용하고 판본·조건·실패·파싱 결과를 보존한다. --version 성공이나 합성 출력을 모델 호출 성공으로 세지 않는다. 필요한 외부 조건이 없으면 해당 기준은 미충족이며 정확히 상신한다.

### G8 최종 검토와 인도 일치

G1~G7의 증거를 대상으로 제품 수정 없는 최종 review phase를 수행한다. 모든 기준의 근거, 이전 발견의 처분, 실제 연결, 남김을 대조한다. 검증한 제품·시험·제품 문서와 main·미러·지침이 일치한다. review 후 그 내용을 바꾸면 필요한 work와 review를 다시 배정한다. next:null은 이 전체 완료에만 사용하며 중단·문제 은폐에 사용하지 않는다. push는 하지 않는다.

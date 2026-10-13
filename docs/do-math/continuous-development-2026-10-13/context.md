# do-math 재편의 현재 공용 맥락

## C1 사용자 목표와 완료 기준

결함이 시험을 빠져나가는 기제를 막는 것이 목표다. 실제 제품 경로를 시험하고 대역은 외부 경계에 두며, 계약·불변식에서 기대값을 얻고, 이전 개선을 보존한다. 정확성·합리적인 개발 속도·유지 비용을 함께 만족해야 한다. 출발 요구와 사용자의 교정은 run:sources/user-decisions.md, 원문 위치와 시작 상태는 run:sources/baseline.json 및 run:sources/requirements-index.json에 있다. 요구 목록이 아니라 검토 가능한 증거로 아래 기준을 충족해야 한다.

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

## C2 시작 당시 실제 상태와 증거의 한계

준비 시 확인한 HEAD는 56e961ff2b4666a373839e6524a9701d1f9c1462(2026-10-06)다. 준비 파일을 커밋하면 HEAD는 바뀌므로 이것을 영구 실행 전제나 미래 판본으로 쓰지 않는다. 각 task는 자기 입력의 현재 해시와 변경 여부를 확인한다. baseline의 문서·코드 해시가 달라졌다면 새 근거로 상태를 재판정한다.

B129는 기본 3990개 실행이 완결됐지만 3988통과·1실패·1건너뜀, successful=false, 10724초였다. 유일한 실패는 Git 대역 시험의 예외 세부 단언 누락이며 이후 관련 2개가 통과했다. 건너뜀은 Windows 심볼릭 링크 권한 부족(1314)이었다. 현재 전체 성공을 입증한 것은 아니다.

B130~B134는 조회·CLI·역할 입력 metadata·복원·profile_selection 문서 필드를 실제 결과로 연결했다. 각 관련 검사 22/25/26/28/28개는 그 범위의 증거다. DOC-RETURN-PURE와 DOC-RETURN-CLI는 종료됐고 ROLE은 _context 관련 남김, REVIEW/TRUST는 별도 남김이다. field_schemas의 현재 코드와 문서별 실제 소비를 확인해야 하며 단순히 남은 AST 호출 수를 완료율로 쓰지 않는다.

기존 계획에는 109개 추적 항목이 있고 4 complete, 2 partial_complete, 1 implementation_reviewed, 1 reviewed_pending_evidence, 101 planned다. 서로 다른 크기의 구현·근거 연결·검토·관문이 섞였으므로 4/109 완료율이나 미구현 101개로 표현하지 않는다. 상위 의무의 낡은 남김 문장과 최신 상세 기록을 구분한다. phase 001이 이 차이를 해소할 유한한 산출물을 만든다.

기존 실제 제품 수리와 유효한 검증은 유지한다. 반면 B110~B114의 문서 소스 추론 확장은 이후 반례로 교체 대상이 됐다. 최근 성과에는 이 재작업 비용도 포함돼 있다. 커밋 수·검사 수·새 보고서 수로 전체 진척을 대신하지 않는다.

phase 001의 세 분석 task는 모두 A1~A4를 완료했고 manager의 report 형식 검사를 통과했다. manager가 현재 HEAD 77b8f132c056bcb222e7b6ee431742aa4dc1f27e에서 baseline 979파일(제품969·원자료6·engine4)의 바이트 불변, 원래 19/11/61/12 ID·원문 대응, B129 및 B130~B134/repair 원보고 14개의 해시·선택/row 대응을 재확인했다. B129와 현재 Python 소스 차이는 8개이며 B134 green의 28개 부분 성공은 현재 Python 판본과 일치한다. 분석 complete는 G 충족이나 제품 합격이 아니다. 근거는 run:phases/001/manager-evidence/verification.json 및 세 task의 report다.

phase 002 mutation-baseline은 A1~A5를 완료했고 manager의 report 검사와 원자료 대조를 통과했다. 수리 전 실제 child 반례 1 fail/대조군 1 pass, 최종 관련 시험 58선택/58 passed와 exit 0을 보존했다. manager는 task 종료 파일 해시 2206개와 공식 보고의 Python 해시 862개가 현재와 일치하고, 전후 변경 12개가 배정 쓰기 범위와 일치함을 확인했다. 그중 2개는 생성된 .timings 캐시다. 실제 child fixture 19개(수리 전 2·최종 17)의 보고·시도 파일·정상 기준 연결도 대조했다. 검수 시 HEAD는 6385880f821743dab59bfc4853970597175e91b4이며 이번 관리 커밋 이후에도 이 해시는 당시 검증 좌표로 남는다. 이 부분 성공으로 G4~G7의 전체 실행을 대신하지 않는다. 근거는 run:phases/002/manager-evidence/verification.json과 run:phases/002/tasks/mutation-baseline/report.json이다.

phase 003 provider-smoke는 partial이다. A1/A3/A4의 지정 범위와 A2/A5의 실패를 manager가 승인했다. report 검사 뒤 종료 파일 2254개, 정본/미러 공식 보고의 Python 864개 해시와 선택/실제 row/exit, 세 실제 호출의 schema·prompt·worker·파일·종료 원자료를 대조했다. 변경 62개가 모두 writes 안이고 현재 종료 해시 불일치는 0개다. Claude 최종 1개 실호출과 정본 오프라인 23개는 통과했으나 Codex schema HTTP 400 및 미러 4선택 중 2실패는 미해결이다. 관리 검수 당시 HEAD는 ea4b4f0fc04dbc0f2b384ff4d60d7de5a817611d이다. 근거는 run:phases/003/manager-evidence/verification.json 및 run:phases/003/tasks/provider-smoke/report.json이며 구체적 현재 조건은 C12에 둔다.

phase 004 mirror-corpus도 partial이다. manager는 report 검사 후 종료 소스 2624개, 변경 9개와 writes, 양쪽 공식 보고의 Python 각 864개 및 14선택/14passed/exit 0을 실제 파일과 대조했다. 생성기 22개 성공·수리 전 5개 하위 사례 실패와 최종 생성/구조 검사도 원출력·실행 전후 해시로 확인했다. 미러 치환 실패는 해결됐고 정본 녹화는 불변이다. A3의 Git clean에서는 양쪽 manifest 두 파일의 변환만 남는다. 관리 검수 당시 HEAD는 d97525b213bbf0e3f5680f17fc623601143664f0이며 근거는 run:phases/004/manager-evidence/verification.json과 task report다. A1/A2/A4의 부분 성과를 유지하고 A3 미충족은 phase 005로 넘긴다. G4~G8 전체 성공은 아니다.

phase 005 corpus-git-bytes는 A1~A3 complete로 검수했다. report 검사 후 현재 종료 소스 2624개와 작업 전후의 두 속성 변경, 양쪽 corpus 88개 경로의 실제 Git raw/clean 출력·각 41개 명시 SHA 참조를 대조했다. 불일치는 0개이고 manifest·녹화 바이트는 불변이다. 각 트리의 6바이트 감소는 속성 한 줄 변경이다. 공식 --check의 1297파일 일치와 skill-only verified, 기존 양쪽 Python 각 864개·재생 각 14개와 생성기 22개 성공의 재사용 조건을 확인했다. 검수 당시 HEAD는 f0764fb192a405e6cf95fd9500f103ac11180cf3이다. 근거는 run:phases/005/manager-evidence/verification.json과 task report이며 모델 호출과 최종 전체 관문을 새로 수행한 결과는 아니다.

phase 005 F2의 engine 문서 차이는 작업 시작 전부터 존재했다. protocol.md의 phase 004 종료 SHA256 cd47a1cff33fccc82f5a3cf284831fece663e805d0a30569c62d097c1d91f3b4와 phase 005 시작/종료 및 이번 검수 SHA256 07d63532457b3b5b8732bad449c779fa45c11e9be51fcec69cd35ca4a6cf002f를 구분한다. task와 manager는 현재 protocol을 읽었고 engine을 수정하지 않았다. 첫 보조 검산의 exit 1은 전체 소스 불변 가정이 이 기존 차이를 만난 결과이며 제품 실패가 아니다. 원 실패 출력·당시 스크립트는 보존한다. 해시만으로 변경 주체·내용의 의미를 추측하지 않는다.

phase 006 codex-schema는 partial로 검수했다. report 형식 검사 후 시작 2624파일이 phase 005 종료와 같고, 종료 2640파일과 현재 파일의 차이가 0개임을 확인했다. 실제 50변경은 report changes 및 쓰기 범위와 일치한다. 공식 9묶음의 선택/고유 row/exit와 각 판본을 대조했으며 Codex 실호출 1passed와 11개 판정, 원/전송 schema·worker·파일·checkpoint·종료를 원파일에서 확인했다. 정본 corpus 18passed와 미러 14passed는 최종 Python 각 865개와 일치한다. 양쪽 각 18항목·51파일·223685바이트·50개 명시 SHA, 총102경로 raw/clean 동등성을 확인했다. 직접 소비 45건 중 11실패와 저장 pair의 성공 표본 공백 때문에 A3/A5는 미충족이다. A1/A2/A4의 지정 성과만 승인한다. 검수 당시 HEAD는 9c917b644360ebdb0d6fd0e0cc8ef3191f4956b8이며 근거는 run:phases/006/manager-evidence/verification.json과 review.md다. 전체 관문의 성공은 아니다.

phase 007 provider-consumers는 A1~A5 complete로 검수했다. manager가 8개 공식 실행의 선택/고유 row/실제 exit와 소스 전후를 대조했고 최종 직접 소비98·경계74·corpus14·미러59개가 모두 passed였다. 이전11실패와 pair 두 성공 분기의 공백은 해소됐다. 시작2640파일은006 종료와 같고 task의26변경은 모두 writes와 report에 일치한다. 검수 시 현재와 종료 해시의 차이는 모델 정책에 따른 운영자 작문 도구4파일뿐이며 do-math는 불변이다. runtime124·smoke입력3과102 corpus 경로의 raw/clean을 검산했다. 검수 HEAD는 61f9e06fc15fb49ef30bf7d93c83c92e275eebad이고 근거는 run:phases/007/manager-evidence/verification.json 및 review.md다. 이 지정 회귀의 완료를 전체 일반/T3/변이/G7/최종 review의 완료로 확대하지 않는다.

phase 008 document-recovery는 A1~A4 pass·A5 fail의 partial로 검수했다. 현재2640파일과 task 종료 해시는 전건 같고30변경은 report/writes에 일치한다. 8개 공식 실행의 선택/고유row/exit·소스 전후를 대조했으며 최종 정본110건은106passed·4failed, 미러89건은85passed·4failed다. 두 최종 Python865파일은 현재와 같고 skip/error/미실행은 없다. P01 red2단언과 운영/복구·설치 지정 검사는 통과했으나 기존 CLI 함수 표기가 unowned field로 분류돼 전건 문서 검사4건이 실패한다. 현재/HEAD 원문과 당시 helper에서 같은 분류를 재현했고 현 함수 검사 표기로 해결 가능한 것을 확인했다. runtime124·smoke입력3·corpus102경로는 불변이며 Git raw/clean을 재확인했다. 검수 HEAD는12a751550dc06ac75cdc56058b622d8b621b21cd이고 근거는 run:phases/008/manager-evidence/verification.json 및 review.md다. 부분 성공을 최종 전체 관문이나 제품 합격으로 확대하지 않는다.

phase 009 document-callable은 A1~A3 complete로 검수했다. report 검사 후 현재2640파일과 종료 해시 전건 일치, 시작과008 종료 동일, 허용된 문서2·캐시2 변경만 있음을 확인했다. 원문에는 함수명 뒤 (...) 다섯 바이트만 추가됐다. 실제 callable·필드 검사와 nonexistent/noncallable 반려를 유지한 채 정본110·미러89 선택/고유row가 전건 passed·exit0이며008의 정확4실패가 양쪽 새 passed row에 연결된다. 각865개 Python과 문서의 실행 전후/현재 해시도 일치한다. task의 첫 mirror 계획 exit1은 개행 처리 오류로 제품 변화0이었고 수정 뒤 성공했다. manager 검산 첫 실행의 누락 인자 TypeError도 관리 스크립트만 고쳐 재검산했다. 검수 HEAD는 0af5dd66368b7409899b6eed5b04523db43db4c5, 근거는 run:phases/009/manager-evidence/verification.json·review.md다.008의 partial 원보고는 보존하고 그 F1/A5 남김만 새 근거로 닫는다. 전체 G 완료가 아니다.

## C3 현재 정본과 이력의 역할

이 서비스가 시작된 뒤 현재 실행 판단의 정본은 이 context.md와 plan.md다. 이전 단계-전환표 JSON/MD는 B134까지의 기준선과 상세 근거로 보존하며 현재 작업판으로 이중 갱신하지 않는다. 원문 의무·보존/P2 항목과 과거 보고는 계속 요구·증거의 진입점이다. 새로운 판정은 이 실행의 task report/evidence와 manager의 처분에 연결한다.

sources/requirements-index.json은 기존 표의 원문 식별자·요구와 위치를 추출한 찾아보기다. 새 요구나 충족 판정이 아니다. 판단이 달라지면 원래 설계·결함 범주·실제 코드·원보고로 돌아가며 최신 구현이 요구를 자동 대체하지 않는다. sources/baseline.json에는 원자료 해시, 시작 Git 상태와 기존 미추적 파일을 기록했다. 같은 과거 입력 사본을 phase마다 만들지 않는다.

## C4 새 세션과 한정된 작업

서비스는 task와 manager 모두 phase마다 새 codex exec 세션을 만든다. 이전 대화를 이어받거나 /goal을 다시 만들지 않는다. 각 objective에는 원문 구간·실제 대상·변경 가능 범위·검사·A 종료조건을 준다. 넓은 '의미 감사'나 '_context 전체 개선'을 그대로 배정하지 않는다. 한 문맥에 들어오지 않는 입력이면 구현 전 범위를 나누고 유효한 부분·정확한 후속 질문을 보고한다. 새 세션이라는 사실만으로 자동 압축이 없다고 보장하지 않는다.

task는 작업 중 발견한 무관한 개선을 따라가지 않는다. 현재 A를 만족하는 데 필요한 수리만 수행하고 다른 문제는 원래 G/의무에 연결한 finding으로 반환한다. 구현 결과는 계약상 실제 경계의 정상·반례를 검증한다. 자료를 읽는 작업도 답할 질문과 종료 산출물이 있어야 한다. 긴 파일·JSONL·보고서 전문을 도구 출력으로 쏟지 않고 필요한 원문/JSON 키를 선택한다.

task의 complete는 A 완료다. 검토 task는 결함을 발견해도 배정된 검토를 끝냈으면 complete일 수 있다. manager는 이를 제품 합격으로 바꾸지 않으며 모든 finding에 carry/resolve/reject와 근거를 남긴다. 다음 행동마다 어느 G의 어떤 남김이 줄어드는지 밝힌다.

## C5 병렬 실행과 검증 자원

phase 001~009는 종료됐고009의 문서4실패 해소를 검수했다.010은 host-smoke와 reading-limits 두 work task를 병렬 배정한다. host-smoke만 host 시험·공유화 대상3개 boundary·시험 지침·미러·비용 캐시를 쓰며 공식 검사를 jobs1·한 묶음씩 실행한다. reading-limits는 writes=[]로 고정된 SKILL/운전 문서·contracts/context_store/cli_worker 및 호스트 읽기 계약만 조사한다. 변경 중인 시험·지침·캐시·미러와 host 결과를 입력으로 쓰지 않고 공식 시험·유료 호출·생성기를 실행하지 않는다. 두 task는 DB/포트/잠금·임시 출력도 공유하지 않는다. 후속 Lean·예약·학술은 개별 실제 연쇄로 배정하며 이 phase의 미완성 구현에 기대지 않는다.

do-math 시험 프로세스는 전체 합계 worker 3 이하, 동시에 한 검사 묶음만 실행한다. 검사 중 제품·시험 정본을 고정한다. 공식 도구는 python -u -B .claude/skills/do-math/scripts/run_tests.py 이며 전체 일반 검사는 기본 선택을 쓴다. 긴 실행은 자기 evidence 아래 원보고와 실제 process/session·시작·종료 상태를 남긴다. 관찰 도구의 yield/대기 만료를 시험 실패로 해석하지 않는다. 실행 중 result.json은 do_math.file_io.read_bytes_shared로 읽어 Windows rename을 방해하지 않는다.

관련 수정은 관련 검사로 확인하고, 전체 일반 검사는 결합 변경 확인이나 최종 판본 관문에 배치한다. 이미 통과한 검사를 새 변경·실패·증거 무효화 이유 없이 반복하지 않는다. 시간 예산은 소프트 기준이다. 시간만으로 실패·미실행·변이 포착을 만들지 않는다. 빠른 검사를 만들기 위해 단언·실제 경로를 약화하지 않는다.

## C6 파일 소유와 Git 마감

task는 protocol의 writes와 자기 report/evidence에만 쓰며 Git commit/reset/checkout을 하지 않는다. 다른 task의 자료와 공용 context/plan/seams도 수정하지 않는다. 필요한 제품 문서 변경과 미러 생성 범위는 objective/writes에 포함한다. 생성기를 돌리기 전에 영향 범위를 확인하고 다른 작업의 변경을 덮지 않는다. 준비 시의 dirty/untracked는 일괄 stage·삭제·정리하지 않는다.

manager는 제품 코드나 제품 정본 문서를 직접 고치지 않는다. 검수 후 Git 커밋과 그에 필수인 기억 노드/색인 작성은 관리 마감으로 맡는다. .claude/skills/commit-harness/SKILL.md와 작성 직전 기억/세칙.md를 따른다. 작업당 관련 검증·검토·미러 근거가 충분한 뒤 정확한 자기 파일과 한 layer1 노드를 같은 커밋에 담는다. test/evidence의 거대한 scratch나 무관 파일을 git add -A로 포함하지 않는다. 원보고 bytes를 유지한다. Git 및 기억 마감은 manager 단독이며 병렬 task가 index를 공유하지 않는다.

manager는 next phase와 공용 문서·기억 등을 먼저 확정하고 pending handoff 검사를 통과한 뒤 manager.json을 게시한다. 이후 내용 변경 없이 필요한 정확 파일을 커밋한다. Git 행정 마감이 code 변경이나 G 축소로 변하지 않게 한다. 전체 검증 후 커밋용 기억·보고만 추가한 경우와 제품/시험 변경으로 증거가 무효화된 경우를 구별한다.

## C7 서비스의 기능과 운영 한계

정본은 repo:services/continuous-development/protocol.md다. run.py는 모든 task 종료 후 새 manager를 호출하고 next를 따른다. 자동 검사·자동 재시도·자동 재개·timeout·최대 phase 수는 없다. report/handoff 검사는 각 역할의 필수 제출 절차다. 형식 통과가 근거의 의미를 보증하지 않으므로 manager와 최종 review가 실제 파일과 주장을 대조한다. README에 남은 output/continuous-development 경로 대신 현재 services 경로를 사용한다.

첫 실행은 이 기록 디렉터리의 start.py로 검사한 뒤 기동한다. 같은 phase 재실행은 task를 다시 실행하고 로그를 덮을 수 있으므로 금지한다. 프로세스가 사라졌거나 report가 없다고 성공·timeout 원인을 추측하지 않는다. 실제 PID/종료/로그를 확인하고 새 복구 phase 또는 manager 재호출을 사람이 검토해 시작한다. 이전 report/evidence/manager.json을 고쳐 성공 보고로 만들지 않는다.

상신이 필요한 외부 결정이 있으면 finding과 context/plan에 정확한 질문·영향 G·확인한 증거를 남긴다. 독립적으로 진행할 일이 있으면 그 일을 배정한다. 모든 다음 행동이 같은 미해결 외부 조건에 막혔으면 빈 분석 phase를 계속 만들거나 next:null로 성공을 꾸미지 않는다. manager.json을 게시하지 않고 정확한 상신과 로그를 남겨 실행기를 오류로 종료시키며, 이 서비스에는 별도 paused 상태나 자동 복구가 없음을 알린다.

## C8 모델과 현재 준비의 범위

2026-10-14 사용자가 모델을 지정했다. 이후 서비스 task는 `gpt-6.1-sol` / `high`, manager는 `gpt-6-astra` / `xhigh`를 사용한다. 작문 도구의 독해 기본값도 `gpt-6.1-sol` / `high`다. 새 phase의 task에는 이 model/effort를 명시하며 임의로 다른 모델을 선택하지 않는다. start.py와 이번 교체 실행기의 공통 CLI 기본값은 task 설정이고 settings.json의 manager 설정이 이를 덮어쓴다. 서비스의 settings는 실행 시작 때 한 번 읽히므로 파일 수정만으로 기존 실행에 반영된다고 가정하지 않는다. 모델 전환 당시 phase 007 작업자(PID 33604)는 기존 `gpt-6-astra` / `max` 세션을 유지했다. 교체 실행기는 그 작업자의 exit 0을 확인한 뒤 007 manager를 새 설정으로 호출했다. 검수 때 상태는 manager_running이었으며 관찰 사본은 run:phases/007/manager-evidence/model-policy-observation.json에 있다. 원 실행기는 작업자를 종료하지 않고 교체했고 task와 로그도 재실행·덮어쓰지 않았다. 변경 근거와 실행 상태 위치는 run:sources/model-policy-2026-10-14.md다. 제품 T5 실호출에 지정하는 모델은 이 개발 담당 모델 설정과 구별한다.

준비 세션은 서비스 단위 검사(가짜 Codex 사용) 31개 중 30개 통과·권한 조건의 symlink 1개 건너뜀을 확인했다. 이것은 do-math나 실제 모델 호출 완료의 증거가 아니다. 준비 당시 실제 Codex 세션은 미기동이었다. 현재는 phase 001 세 task와 phase 002~008 각 한 task의 report를 각각 새 manager가 검사했다. phase 003은 실제 공급자 경계를 실행했으나 A2/A5가 실패한 partial이며, phase 004는 그 미러 실패를 수리했으나 당시 Git clean 조건 A3가 실패한 partial이다. phase 005는 A1~A3 complete이고 004의 clean 남김을 새 근거로 닫았다. phase 006은 A1/A2/A4의 한정 성과를 승인한 partial이며 A3/A5의 직접 소비 남김은007의 새 근거로 해소됐다. phase 007은 A1~A5 complete로 검수했다. phase 008은 A1~A4를 승인한 partial이고 A5의 문서4실패는009의 A1~A3 complete로 해소했다.010의 두 task도 gpt-6.1-sol/high로 배정한다. 이전 partial report 자체는 수정하지 않는다. 개발 서비스의 세션 수행과 제품의 공급자·역할 스키마 실호출은 다른 경계이며 실제 T4/T5의 책임은 G7에 남는다.

## C9 요구별 상태와 과거 검토의 재사용 범위

phase 001의 requirement-state.json은 원래 19/11/61/12 항목을 각각 한 번씩 연결했고 tracking-state.json은 기존 109개 작업을 연결했다. 이들은 역사 근거와 종료 질문의 진입점이며 새로 수행한 전수 의미 감사가 아니다. 현재 판정은 이 context와 후속 report/manager의 처분을 따른다. 1-D/11-A/11-B의 검토된 성질, R17과 R07의 완료 부분, DOC-RETURN-PURE/CLI 및 B132~B134의 지정 경계는 유지하고 최종 판본 근거를 연결한다. 9-A의 R18 현재 외부 호출 전건, 1-E의 최종 반환 소유권 처분은 별도로 남는다. K-27/38/72/75와 P2 A-31/B-32는 후속 수리 이전의 낡은 remaining만으로 재수리하지 않는다.

prior-review-state.json의 phase 001 당시 실제 이전 검토는 PR23/B107~B109 완료, PR06/B22 부분 완료, 나머지 23영역 미검토다. 같은 구현을 다루는 후속 task에 해당 review_slices의 실제 diff·현재 소비자·원보고만 결합한다. 25영역 전체를 모든 수리의 선행 장벽으로 두지 않는다. phase 002는 PR01/B56의 mutation child 결과·정상 기준·공유 passed 소비 slice를 실제 bbe64043/f56a2772 diff·현재 소비·새 58개 시험으로 재검토했다. B56 원보고 네 임시 경로는 현재 없으며 과거 counts를 합산하지 않았다. 정상 증거 처리 교정과 D9·모듈 비용 순서·시간 종료 제거의 유지 판단을 승인한다. PR01의 T3 저장소·전체 runner·provenance까지 완료로 바꾸지 않는다. 근거는 run:phases/002/tasks/mutation-baseline/evidence/review-notes.md 및 run:phases/002/manager-evidence/verification.json이다.

phase 003에서 PR15/B86/B87의 공급자 녹화·native background completion slice를 검토했다. 46a67a7f/87fd1c1b 도입 diff·현재 소비자·존재하는 네 원보고를 대조했고 Codex error/turn.failed 분류, Claude task_id/tool_use_id 및 시작/완료/선택 result 순서의 현 계약을 유지한다. 기존 background 원보고는 actual_wait_tool=false와 passed=false 그대로다. 현재 계약의 nonce 파일·native completion·로컬 종료 성질만 재사용하며 maintenance schema 수락이나 연구 저장 증거로 넓히지 않는다. PR15의 다른 slice는 미검토다. 근거는 run:phases/003/tasks/provider-smoke/evidence/review-notes.md와 run:phases/003/manager-evidence/verification.json이다.

phase 004는 2fc686ac7f215222702519dfaf10e6e1ec961171의 생성기 도입 diff와 현재 transform/build_target의 바이트 경계를 대조했다. verbatim 선적용과 일반 지시문 변환은 유지하고 corpus 적용 누락만 교정한 판단을 승인했다. a0b0cc2e030b49229573aea4bf617845f27c44e5의 corpus 속성 중 manifest text 예외는 실제 clean 반례가 있어 phase 005에서 -text로 교정했다. 이 한 줄과 대응 생성 사본의 변경·전건 clean 동등성을 manager가 확인해 해당 반례의 재검토를 종결한다. 새 근거는 run:phases/005/manager-evidence/verification.json이다. 생성기 본문이나 PR15 전체를 다시 여는 근거는 없다. 이전 검토 근거는 run:phases/004/tasks/mirror-corpus/evidence/review-notes.md와 history-mirror/history-attributes 원출력, manager의 verification.json이다.

phase 006은 B49/065a323a의 전달·반려·수치·종료 slice를 실제 도입 diff와 현재 소비자에 대조했다. 두 Temp 원보고가 없다는 관찰을 유지하고 역사 161/6 counts를 새 성공으로 합산하지 않는다. 새 related-01의 5실패는 수정한 4개 fixture의 related-02와 오류 단언을 보강한 semantic-final에서 해소됐음을 원 row로 확인했다. pinned 입력·worker 반려·canonical 값 거부·종료 보호를 유지한 이 slice의 판단을 승인한다. 직접 소비 11실패와 pair 공백은 별도 미해결이며 B49의 다른 관찰 가족이나 PR15 전체를 완료로 바꾸지 않는다. 근거는 run:phases/006/tasks/codex-schema/evidence/history-b49.diff, history-review.json, review-notes.md와 run:phases/006/manager-evidence/verification.json이다.

저장소 원보고 100개의 해시와 그중 39개의 선택·결과를 읽었다는 것은 closure-map의 관찰이다. 외부 임시 원보고 246개 위치 레코드(236개 고유 경로)는 현재 없다. 해당 slice의 판단에 필요할 때만 보존 근거를 찾고, 없으면 과거 counts와 현재 대체 재현을 구별한다. 삭제 원인을 추측하거나 사용자가 지운 작업을 복원하지 않는다. R05/R06의 현행 시험은 tests/flows/test_provider_native_storage.py의 NativeStorageTests.test_native_numbers_and_public_blocks_survive_actual_runner_and_repository이며 과거 test_provider_close_native_storage.py 경로는 쓰지 않는다.

1-A의 원문 인용은 보존하되 A20의 필수+선택 필드 역방향을 적용한다. 이 역방향 검사는 수신자가 선언한 필수·선택 필드 전부가 실제 생산 표본에서 나오는지 확인한다. SHARDS·메모리 저장 대역 이름·하드 timeout 같은 폐기된 수단은 복원하지 않으며 현재 보호 성질과 사건/임대 의미를 유지한다. 구체적 근거는 run:phases/001/tasks/closure-map/evidence/requirement-state.json, prior-review-state.json, evidence-catalog.json 및 closure-decisions.md다.

## C10 문서 결속에서 남은 고정 범위

document-closeout의 원목록은 실제24문서(계약11 포함), inline 필드189회·lexical owner79개·노출 owner84개와 당시 AST34지점이다. 이 수는 역사 목록의 크기이며 현 의미 검증 완료율이 아니다.008에서 P01의 운영/복구6 AST지점을 실제 _context/포장 객체와 저장·물질화 파일 검사로 교체했다. operational_evidence와 recovery_materials의 동명 source를 구별하고 정상·restoration_error·checkpoint_source=null·live 부재·activity_continuations와 반환 사본/제품 입력 반례를 확인했다. 일반 재개의 result_source와 B130~B134 기존 성질을 유지하며, 마지막 소비가 없어진 checkpoint_source/recovery_source/checkpoint_files/recovered_output_files 단독 입력은 제거했다. defer 두 입력의 실제 문서 검사 담당과 오기/누락 반례도 확인했다. 근거는 run:phases/008/tasks/document-recovery/evidence/binding-review.md 및 run:phases/008/manager-evidence/review.md다.

독립-운영.md의 LIVE_INSTALLATION_ROOT 문장은008에서 현 bootstrap.main의 manifest.installation_root 또는 snapshot_root를 scheduled_operator.main의 installation_root 인자로 전달하는 경계로 교정했다. 기존 bootstrap-info2개는 양쪽 최종 보고에서 통과했다. 옛 전역 이름은 제품에 복원하지 않았으며 N03의 다른 절은 미검토다.

008 F1/A5의 전건 관련 회귀 남김은009에서 해소됐다. CLI-실행-계약의 bare dotted 함수명을 provider_final.output_contract(...)로 교정해 기존 function_reference_issues의 실제 callable 검사에 연결했다. helper/schema/unknown/defer/runtime/시험 소스는 바꾸지 않았다. 정본110·미러89 선택은008과 같고 정확4실패가 모두 passed이며 현재 소스와 원보고 판본을 manager가 대조했다. P01 운영/복구와 N03-003 설치 설명의 지정 성과 및 관련 회귀를 닫고008~009 변경 단위를 마감한다. N03의 다른 절·P02~P11은 그대로 남는다. 근거는 run:phases/009/manager-evidence/verification.json·review.md다.

followup-packets.json의 P01~P11·N01~N03·L01은 유한한 후보 범위다. 15개 고정 phase를 예약한 것이 아니다. P01과009에서 종료한 지정 회귀, P02 원자료/과제 결과, P03 실행 안내/설치를 구별하고 REVIEW/TRUST·D-06·단독 이름을 실제 소비 경계별로 닫는다. instance는 명시 소비가 없는 제거 후보이며 config/profile/execution은 유지 근거가 있다. recovery_source 단독 입력은008에서 마지막 소비가 사라져 제거됐다는 위 처분을 따른다. 마지막 소비자가 없어지기 전 AST helper를 일괄 삭제하지 않는다.

L01은 실제 운전의 host/tool/version/read-call별 읽기·출력 한도와 그 측정 단위(byte 또는 token)가 미확정이다. 조사 대상은 현재 사용하는 Codex/Claude의 운전 문서 읽기 경로이며 역할 stdin 전달과 구별한다. 010 reading-limits가 현재 host/tool/version/read-call별 권위 있는 한도와 실제 절단·구간 회수 근거를 조사한다. 제품 구현이나 유료 호출과 독립화했고 확인 불가능한 경계는 정확한 외부 결정으로 반환한다. byte와 token 사이에 임의 환산 상한을 두지 않는다. 권위 있는 설정으로 판정할 수 없으면 필요한 외부 결정·영향 의무를 상신하며 13-C 통과로 바꾸지 않는다. 학술 외부 어휘도 그 실제 응답 계약에서 확인한다. 근거는 run:phases/001/tasks/document-closeout/evidence/binding-inventory.json, followup-packets.json, review-notes.md와 run:phases/001/manager-evidence/source-excerpts.json이다.

## C11 최종 관문을 막는 도구·실경계 공백

phase 001 gate-readiness F4의 정상 child 근거 부재에 의한 거짓 포착은 phase 002에서 재현·수리됐다. 현재 mutation.py는 selection/collected/rows/tests_run/load_error의 단일 결과를 생산자·수신자의 validate_result로 검사하고 PID·exit·오류를 attempt.json에 보존한다. 정상 시험 row가 실제 passed일 때만 mutant의 failure/error/unexpected success를 포착으로 인정한다. load 오류는 동일 batch의 정상 수집·실행·통과와 대조하며 오류 문자열을 시험 ID로 쓰지 않는다. 부재·파손·skip·expected failure·fixture 오류·빈 실행·미실행·비정상 exit는 execution_error로 구별한다. 정상 실패는 제외 후 다음 후보를 검사하되 baseline_failing으로 관문을 막는다. baselines와 outcomes[].attempts의 연결 및 별도 재시도 경로를 최종 G6의 근거로 사용한다. 이전 failing 문자열 결과·옛 출력 경로 설명은 현재 계약이 아니다. D9의 지연 정상 확인·동일 선택 재사용·모듈 비용 순서·timeout 없음은 유지한다. 근거는 run:phases/002/tasks/mutation-baseline/report.json과 run:phases/002/manager-evidence/review.md다. 전체 함수 모집단·fresh T3·전체 변이는 여전히 미완료다.

기존 변이17분할은 130파일이며 현재 LAYERS 1/2/3의 123모듈을 포함한다. adapter인 git_process/http_transport/powershell_scheduler/system_clock/windows_job 5개와 run_tests.py/test_categories.py는 해당 필터 밖이다. 설계 5.5/6.3 및 현재 도구 정본에 따라 이 7파일은 G6의 layer1/2/3 변이 분모에서 제외한다. adapter 5개는 T4 실제 계약·별도 분기 보고/T5로, runner·격리 표지는 관련 도구 시험과 G4/G5 선택·종료 검증으로 확인할 책임을 유지한다. 제외를 실행 성공으로 세지 않는다. 현 함수·rule·trivial·시험 진입 집합은 fresh T3 뒤 확정하고 오래된 1586함수나 17분할을 분모로 쓰지 않는다.

phase 001 당시 T5의 smoke 폴더에는 test_*.py가 없었고 runner는 빈 선택을 거부했다. phase 003이 현재 두 공급자 시험을 연결했으며 실제 결과와 남김은 C12를 따른다. probe_cli의 files/background는 작은 protocol_probe 경계라 실제 역할 schema·Job/pythonw·Lean/Mathlib·예약 등록/발화/해제·학술 list_sources의 전체 요구를 대신하지 않는다. G7 work에서 필요한 실제 연쇄와 녹화를 최종 소스 고정 전에 완결한다. 공급자 최소 smoke의 구현과 부분 실호출만으로 다른 연쇄를 대신하지 않는다. T4 단독은 Measurement를 만들지 않아 adapter 분기 보고가 없다. 별도 T4 측정 수리를 배정하며 최종 T3 모집단에 T4를 섞어 해결하지 않는다.

phase 003은 현행 maintenance action schema 전체로 공급자 최소 smoke를 구현·실행했다. Claude 역할 응답·파일·checkpoint·종료 회수는 최종 호출에서 성공했고 Codex는 동일 schema를 거부했다. 실제 원출력과 현재 parser 재생은 보존됐다. 미러 생성의 녹화 원바이트 변형은 phase 004에서, Git manifest 속성은 phase 005에서 수리·검수했다. Codex 역할 schema 거부는 phase 006의 원 의미를 보존하는 전송/수신 수리와 새 실호출로 해소됐다. 직접 소비 fixture·pair 공백은007에서 해소됐고 그 검수와 실호출 재사용 조건은 C12에 둔다. Job/pythonw 전용 경계·Lean/Mathlib·예약·학술·L01과 G7 전체는 후속 책임이며 PR15 전체 검토로 확대하지 않는다.

phase 001 gate-readiness 당시 설치 Codex는 0.162.1, 녹화 manifest는 0.160.0이며 Claude는 양쪽 2.1.289였다. phase 003은 현재 command-surface와 새 역할 호출을 녹화했고 이전 항목도 보존했다. corpus12항목/20파일의 해시 일치는 현재 인증·모델 호출 성공을 뜻하지 않는다. Claude background의 해당 native completion·파일·종료 조건 재판정은 phase 003과 C9/C12에서 완료했다. Lean/Lake/Mathlib·pythonw·학술 서버 자료의 존재/버전은 확인됐으나 인증·지원 모델·계정 한도·컴파일·예약 권한·MCP 응답은 미확인이다. 독립적으로 가능한 수리를 진행하면서 가까운 G7 작업에서 비밀 비노출 방식으로 조건을 확인하고, 부족한 외부 조건은 정확히 상신한다. 근거는 run:phases/001/tasks/gate-readiness/evidence/gate-readiness.json, population-and-corpus.json, environment.json, source-contracts.json 및 manager의 verification.json이다.

010 host-smoke는 기존 실제 Job·pythonw boundary 경로를 확인해 공식 T5의 해당 설치 연쇄를 연결한다. 새 스모크·필요한 공유화·원실행 녹화만 맡고 runtime/공급자/corpus 계약은 바꾸지 않는다. 실제 OS 예약 등록·발화·해제, Lean/Mathlib, 학술 MCP와 T4 별도 adapter 분기는 이후 책임이다.010 reading-limits의 조사 완료는13-C 충족과 구별한다. 구체적 A/쓰기/선택은 run:phases/010/phase.json과 두 objective다.

## C12 공급자 부분 성공과 원바이트 인도

phase 003이 추가한 T5 선택은 Codex/Claude maintenance 각 한 건이다. 003 당시 실 ModelRunner·real_ports·worker·adapter·parser를 사용했고 세 worker schema가 당시 action_schema 전체와 같았다. 새 호출은 Codex 1회·Claude 2회다. live-01은 2선택/2실패이며 Claude는 읽기 도구 출력에 checkpoint가 섞여 정확 비교가 실패했다. prompt를 명확히 한 live-02의 Claude 1선택은 모든 9개 판정과 공식 row가 통과했다. 003의 마지막 live와 종료 사이에는 호출 경로가 불변이고 오프라인 corpus 검사 세 파일만 바뀌었다. 003 검수 시 최종 정본 23개 및 미러 4개의 Python 864개 해시는 당시 종료 판본과 일치했다. 006 이후 판본은 아래의 새 근거를 따른다. 근거는 run:phases/003/manager-evidence/verification.json 및 task의 live-01/live-02/offline-01/mirror-replay 원보고다.

phase 003 F1은 실제 제품 전달 실패였다. Codex 0.162.1/gpt-6-astra/low는 보통 maintenance schema의 선택 필드 integration_bundles가 required에 없다는 HTTP 400 invalid_json_schema를 반환했다. worker exit 1, parse_complete=true, turn_failed=true, final/파일/checkpoint 부재와 로컬 종료 barrier는 역사 실패 그대로 보존한다. 인증 부재나 timeout 또는 연구 control_binding 실패로 해석하지 않는다. phase 006의 새 전달 표현과 대표 실호출은 아래의 범위에서 이 거부를 해소했다. 원 schema의 선택 필드 부재/null/값과 제약은 그대로다.

phase 003 F2의 미러 치환 위반은 phase 004에서 해결됐다. 당시 정본과 미러는 각각 17항목·44파일·200872바이트이고 정본 raw·manifest·역사 verdict는 불변이다. 기존/신규 두 Claude help는 원 SHA a58ca228…로 복구됐으며 각 트리의 41개 명시 SHA 참조가 모두 맞는다. 기존 _rules.json의 verbatim에 corpus 전체 경계 하나를 추가했고 경계 밖 지시문의 치환은 유지한다. 수리 전 공식 4선택/2통과/2실패는 역사 실패로 보존하며 양쪽 관련 14선택/14통과가 새 근거다. 생성기 전체 22개와 최종 --check/skill-only도 통과했다. 생성 규칙 일치·재생·Git 바이트 보존은 별개이며 당시 Git 남김 때문에 A3는 미충족이었다. phase 005의 새 해소 근거는 아래에 두며 G7/G8 전체는 여전히 미완료다. 근거는 run:phases/004/tasks/mirror-corpus/report.json과 run:phases/004/manager-evidence/verification.json이다.

phase 004 F1과 A3에 남았던 두 manifest의 Git clean 변환은 phase 005에서 해소됐다. 실제 하위 정본 corpus/.gitattributes의 `manifest.json text eol=lf whitespace`를 `manifest.json -text whitespace`로 바꾸고 공식 생성기로 대응 사본에 반영했다. 이전 manager 배정에 이 하위 위치가 빠져 상위 규칙으로 해결하지 못했던 경위는 004 report와 manager 기록에 보존한다. task가 무효한 상위 변경을 복원하고 partial로 반환한 판단은 유지한다. 양쪽 88개 경로의 raw/clean은 전건 같고 두 manifest는 원 raw db61141d…와 같은 clean 값을 갖는다. text가 unset인 상태에서 상속 eol=lf 표시는 남지만 실제 바이트는 보존된다. 005 검수 당시 각 트리는 17항목·44파일·200866바이트, 41개 명시 SHA 참조다. 두 속성 외 86개 파일·manifest 항목·역사 verdict는 불변이다. 기존 재생 각 14개·생성기 22개 성공과 최종 --check/skill-only 근거를 함께 검수했다. 이것은 작업트리와 실제 clean 결과이며 staged blob이나 최종 제품 커밋의 증거로 확대하지 않는다. 새 근거는 run:phases/005/tasks/corpus-git-bytes/report.json, run:phases/005/manager-evidence/verification.json 및 git-clean-observation.json이다. 수리 전 반례는 run:phases/004/tasks/mirror-corpus/evidence/attribute-probe.json, proposed-corpus-attributes.diff와 run:phases/004/manager-evidence/git-clean-observation.json에 보존한다.

phase 004 F2는 이전 세 파일 clean 관찰의 한계를 구체화했다. Git 2.50.0.windows.2에서 Lean/scheduler는 역슬래시 절대 경로일 때만 변환되고 슬래시 상대·절대 경로에서는 보존된다. manifest는 세 표기 모두 변환된다. manager가 같은 argv의 9개 관찰을 재확인했다. phase 003 기록에는 정확한 argv가 없으므로 당시 표기를 단정하지 않으며 원 관찰은 그대로 보존한다. 현재 정본 인도 판정은 cwd와 슬래시 경로의 실제 argv를 남기는 검사에 따른다. Lean/scheduler 녹화를 다시 쓸 근거는 없다. 근거는 run:phases/004/manager-evidence/path-spelling-observation.json이다.

phase 003 F3의 한정 재사용을 승인했다. 보존된 Claude background 원자료 9파일의 해시, 같은 task/tool ID와 시작<완료<result 순서, nonce 파일과 종료 barrier 및 현재 직접 코드 판본을 manager가 대조했다. 과거 passed=false를 유지하며 native completion·파일·로컬 종료 성질만 사용한다. 관련 B86/B87 판정은 C9에 있다. 별도 background 유료 호출은 필요하지 않다. 새 Claude 두 호출의 reported list cost 합계 약 USD 0.4631016은 실제 청구액이 아니며 Codex 거부 비용은 미보고다.

phase 006은 provider_final.output_contract/semantic_output에 Codex 문자열 봉투를 정의했다. ModelRunner는 원 prompt와 output.schema.json을 보존하고 transport.schema.json을 CLI에 전달한다. collector의 source_request·worker hash·native final 일치·종료 검사 뒤 classify_run이 봉투를 엄격히 해석해 canonical 값과 원 schema를 검증한다. 선택 필드 삭제/필수화, null/default 보충, 구형 fallback은 없다. Claude의 직접 JSON 및 control_binding의 중앙 제출 분기는 유지한다. 실제 코드와 의미 회귀를 검수했으며 이 제품 정의를 중복 schema로 다시 만들지 않는다.

006의 Codex 0.162.1 새 호출은 요청 model=gpt-6-astra/effort=low를 명시했고 1선택/1passed/exit0이며 11개 판정이 전부 참이다. 원/전송 schema·prompt·worker snapshot/hash·native final·파일·checkpoint와 종료의 대응을 확인했다. live 이후 runtime124파일과 smoke helper는 불변이며 이후 Python 변경은 corpus 검사3모듈뿐이다. 실제 모델명·비용·내부 요청 수는 미보고다. 새 성공 녹화는 codex-maintenance-transport-20261014이며 기존17항목과 실패 verdict는 유지한다. 현재 각 corpus는18항목·51파일·223685바이트·50명시SHA이고 manager도 전102경로 raw/clean을 검산했다. 정본18개·미러14개 corpus 회귀와 --check1305파일/skill-only 성공은 이 범위에서 승인한다. 근거는 run:phases/006/manager-evidence/verification.json 및 git-clean-observation.json이다.

006 F2/F3와 A3/A5의 직접 소비 남김은007의 새 근거로 해소했다. consumers45건의11실패를 최종98개 묶음의 정확한 passed ID에 연결했다. pair는 실제 runner/worker/collector로 두 공급자의 성공·결박·불완전·정지8표본을 만들고 status/output/collection/error_kind/정확 오류·원자료 해시·종료를 검사한다. 수리 전 새 단언의 두 성공 subTest 실패와 수리 후 성공은 원보고로 보존한다. 단일 chunk의20관찰/한callback과 설치 복구 두 사례도 최종 묶음에서 통과했다. raw ingress의 첫97통과/1실패는 정상 후속 행 위치가 별도 final mismatch를 만들던 fixture 오류였다. 같은 stream의 정상 대조군을 completed로 확인하고 malformed만 주입하는42사례에서 공급자별 정확 collector 반려와 저장/재전달 무효과를 확인했다. 이를 제품 parser 수리나 실패 기대값 완화로 읽지 않는다. 근거는 run:phases/007/tasks/provider-consumers/report.json 및 manager-evidence/verification.json과 review.md다.

006 F4의 Claude 재사용은 한정 승인한다. 원 smoke를 현 parser/collector/분류기로 재수신한 completed·정확 output, 같은 prompt/schema·worker/tool12모듈 및 경로·버전/help 근거를 확인했다. 당시 CLI 바이너리 SHA는 미기록이므로 실행 파일 바이트 동등성을 주장하지 않는다. 새 Claude/background 호출은 없다. 기존 background의 승인된 성질과 역사 passed=false도 그대로다. 이후 입력/실행 경로/도구 조건이 바뀌면 영향을 받는 실호출을 별도로 판단한다. 이번 Codex 성공은 유지된 실행 경로에 한해 후속 시험 수정 뒤에도 재사용할 수 있다. 근거는 run:phases/006/tasks/codex-schema/evidence/claude-reuse.json과 manager 검수다.

007 검수로 공급자 단위의 관련 회귀가 완료돼003~007의 검수된 제품·시험·문서·미러124파일을 하나의 커밋 단위로 마감한다. 비용 캐시는 실행 부산물로 Git 대상에서 제외한다. 이전 archive는 각 당시 판본의 원바이트 근거로 유지하며 자동 복원 지시가 아니다. staged corpus102경로와 선별 원보고의 바이트를 Git blob으로 확인한 후 커밋한다. 관리 기록·008 배정·기억도 같은 인계에 포함한다. 운영자 모델 전환의 작문 도구·settings/start/README 변경은 제품 단위에 섞지 않으며 C8과 정책 원문은 현재 공용 맥락으로 보존한다. 실제 commit/stage 수신 기록과 정확 경로는 run:phases/007/manager-evidence/preservation.json 및 로컬 commit.json에 남긴다. 다른 G1~G8 의무, 문서/의미 질문, Job/pythonw·Lean/Mathlib·예약·학술·L01 및 최종 관문은 유지한다.

008 F2의 보존 사실은 manager가 확인해 종결했다.008의 문서·시험 변경은 공급자 runtime124·smoke입력3·corpus102경로를 바꾸지 않았으므로 기존 실호출의 승인된 성질은 유지한다.007의 제품124파일 마감은 로컬 commit.json의 exit0 및 HEAD78d9c6d에서 확인했다.008 제품30경로(비용 캐시2 포함)는 문서4실패가 남아009 검증 뒤 커밋하며 현재 raw 바이트는008 manager-evidence의 archive로 보존한다. 이번 커밋은 관리 기록·선별 원근거·009 배정·기억만 포함한다. 원바이트/추적 범위는 run:phases/008/manager-evidence/preservation.json에 둔다. G4~G6/G8의 새 최종 판본 검증과 나머지 G7 책임은 유지한다.

009 F2의 보존 사실을 검수했다. 현재 runtime124·smoke입력3·양쪽 corpus102경로와 속성/생성 규칙은008과 같아 기존 실호출 및 명시SHA/Git clean의 한정 근거를 유지한다. --check1305파일·skill-only verified의 원출력과 판본도 확인했다.008~009의 승인된 제품·시험·문서·미러28경로를 이번 관리 마감에 포함하고 비용 캐시2개는 제외한다. 원근거의 raw archive와 Git staged blob은 별도로 대조한다. 정확 경로·해시·추적/로컬 보존 구분은 run:phases/009/manager-evidence/preservation.json, 행정 수신은 로컬 commit.json에 둔다. 제품 바이트를 고치지 않은 관리 커밋은 기존 검증을 무효화하지 않는다. G4~G6/G8 최종 관문, 나머지 문서/의미 질문과 G7 실연쇄는010 및 후속 계획으로 유지한다.

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

## C3 현재 정본과 이력의 역할

이 서비스가 시작된 뒤 현재 실행 판단의 정본은 이 context.md와 plan.md다. 이전 단계-전환표 JSON/MD는 B134까지의 기준선과 상세 근거로 보존하며 현재 작업판으로 이중 갱신하지 않는다. 원문 의무·보존/P2 항목과 과거 보고는 계속 요구·증거의 진입점이다. 새로운 판정은 이 실행의 task report/evidence와 manager의 처분에 연결한다.

sources/requirements-index.json은 기존 표의 원문 식별자·요구와 위치를 추출한 찾아보기다. 새 요구나 충족 판정이 아니다. 판단이 달라지면 원래 설계·결함 범주·실제 코드·원보고로 돌아가며 최신 구현이 요구를 자동 대체하지 않는다. sources/baseline.json에는 원자료 해시, 시작 Git 상태와 기존 미추적 파일을 기록했다. 같은 과거 입력 사본을 phase마다 만들지 않는다.

## C4 새 세션과 한정된 작업

서비스는 task와 manager 모두 phase마다 새 codex exec 세션을 만든다. 이전 대화를 이어받거나 /goal을 다시 만들지 않는다. 각 objective에는 원문 구간·실제 대상·변경 가능 범위·검사·A 종료조건을 준다. 넓은 '의미 감사'나 '_context 전체 개선'을 그대로 배정하지 않는다. 한 문맥에 들어오지 않는 입력이면 구현 전 범위를 나누고 유효한 부분·정확한 후속 질문을 보고한다. 새 세션이라는 사실만으로 자동 압축이 없다고 보장하지 않는다.

task는 작업 중 발견한 무관한 개선을 따라가지 않는다. 현재 A를 만족하는 데 필요한 수리만 수행하고 다른 문제는 원래 G/의무에 연결한 finding으로 반환한다. 구현 결과는 계약상 실제 경계의 정상·반례를 검증한다. 자료를 읽는 작업도 답할 질문과 종료 산출물이 있어야 한다. 긴 파일·JSONL·보고서 전문을 도구 출력으로 쏟지 않고 필요한 원문/JSON 키를 선택한다.

task의 complete는 A 완료다. 검토 task는 결함을 발견해도 배정된 검토를 끝냈으면 complete일 수 있다. manager는 이를 제품 합격으로 바꾸지 않으며 모든 finding에 carry/resolve/reject와 근거를 남긴다. 다음 행동마다 어느 G의 어떤 남김이 줄어드는지 밝힌다.

## C5 병렬 실행과 검증 자원

phase 001은 세 task 모두 프로젝트 writes=[]인 독립 분석으로 종료됐고 manager가 세 결과를 통합했다. phase 002는 변이 정상 기준 수리 task 하나로 운영한다. 이후에도 제품/시험을 수정하고 검사하는 phase는 기본 한 task로 운영한다. 같은 field_schemas나 Git index, 테스트 템플릿·캐시, 미완성 소스를 공유하는 작업을 파일 이름만 다르다는 이유로 병렬 배정하지 않는다. 고정판의 독립적인 읽기 검토에는 병렬성을 사용한다.

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

settings.manager={}와 task의 model/effort 생략으로 설치된 Codex 프로젝트 기본값을 사용한다. 이 준비는 지원 모델 목록을 검증하지 않았으므로 manager가 임의 모델 ID나 effort 조합을 발명하지 않는다. 명시 선택이 필요하면 실제 지원·사용자 환경을 먼저 확인한다. 전역 settings는 시작 때 한 번 읽히므로 manager가 실행 중 바꿔 반영된다고 가정하지 않는다.

준비 세션은 서비스 단위 검사(가짜 Codex 사용) 31개 중 30개 통과·권한 조건의 symlink 1개 건너뜀을 확인했다. 이것은 do-math나 실제 모델 호출 완료의 증거가 아니다. 준비 당시 실제 Codex 세션은 미기동이었다. 현재는 phase 001 세 task의 report가 제출됐고 새 manager 세션이 이를 검사했다. 개발 서비스의 세션 수행과 제품의 공급자·역할 스키마 실호출은 다른 경계이며 실제 T4/T5의 책임은 G7에 남는다.

## C9 요구별 상태와 과거 검토의 재사용 범위

phase 001의 requirement-state.json은 원래 19/11/61/12 항목을 각각 한 번씩 연결했고 tracking-state.json은 기존 109개 작업을 연결했다. 이들은 역사 근거와 종료 질문의 진입점이며 새로 수행한 전수 의미 감사가 아니다. 현재 판정은 이 context와 후속 report/manager의 처분을 따른다. 1-D/11-A/11-B의 검토된 성질, R17과 R07의 완료 부분, DOC-RETURN-PURE/CLI 및 B132~B134의 지정 경계는 유지하고 최종 판본 근거를 연결한다. 9-A의 R18 현재 외부 호출 전건, 1-E의 최종 반환 소유권 처분은 별도로 남는다. K-27/38/72/75와 P2 A-31/B-32는 후속 수리 이전의 낡은 remaining만으로 재수리하지 않는다.

prior-review-state.json에서 실제 이전 검토는 PR23/B107~B109 완료, PR06/B22 부분 완료, 나머지 23영역 미검토다. 같은 구현을 다루는 후속 task에 해당 review_slices의 실제 diff·현재 소비자·원보고만 결합한다. 25영역 전체를 모든 수리의 선행 장벽으로 두지 않는다. phase 002는 PR01/B56 중 mutation child 결과·정상 기준·공유 passed 소비에 닿는 slice만 재검토한다. PR01 전체를 완료로 바꾸지 않는다.

저장소 원보고 100개의 해시와 그중 39개의 선택·결과를 읽었다는 것은 closure-map의 관찰이다. 외부 임시 원보고 246개 위치 레코드(236개 고유 경로)는 현재 없다. 해당 slice의 판단에 필요할 때만 보존 근거를 찾고, 없으면 과거 counts와 현재 대체 재현을 구별한다. 삭제 원인을 추측하거나 사용자가 지운 작업을 복원하지 않는다. R05/R06의 현행 시험은 tests/flows/test_provider_native_storage.py의 NativeStorageTests.test_native_numbers_and_public_blocks_survive_actual_runner_and_repository이며 과거 test_provider_close_native_storage.py 경로는 쓰지 않는다.

1-A의 원문 인용은 보존하되 A20의 필수+선택 필드 역방향을 적용한다. SHARDS·메모리 저장 대역 이름·하드 timeout 같은 폐기된 수단은 복원하지 않으며 현재 보호 성질과 사건/임대 의미를 유지한다. 구체적 근거는 run:phases/001/tasks/closure-map/evidence/requirement-state.json, prior-review-state.json, evidence-catalog.json 및 closure-decisions.md다.

## C10 문서 결속에서 남은 고정 범위

document-closeout은 실제 24문서(계약11 포함), inline 필드189회·lexical owner79개·노출 owner84개와 잔여 AST 호출34지점을 연결했다. 이 수는 목록의 크기이며 의미 검증 완료율이 아니다. B130~B134의 실제 반환·원래 단언은 유지한다. 두 동명 생산자 오류를 구별해야 한다. 운영-점검.md의 operational_evidence.checkpoint_source와 recovery_materials 안의 result_source/checkpoint_source는 일반 재개 restore_continuation의 결과로 대신 입증할 수 없다. recovery의 restoration_error 및 checkpoint_source=null도 원문 지시에 반영해야 한다. manager가 문서·doc_code·core_engine 원문을 대조했으며 실제 재현과 수리는 P01 책임으로 남는다.

독립-운영.md의 LIVE_INSTALLATION_ROOT는 현재 operator_bootstrap.py에 없다. 현재 manifest 또는 snapshot_root에서 installation_root 인자를 전달한다. N03의 해당 절에서 문서를 교정하며 호환용 옛 전역 이름을 제품에 추가하지 않는다.

followup-packets.json의 P01~P11·N01~N03·L01은 유한한 후보 범위다. 15개 고정 phase를 예약한 것이 아니다. P01 운영/복구, P02 원자료/과제 결과, P03 실행 안내/설치를 구별하고 REVIEW/TRUST·D-06·단독 이름을 실제 소비 경계별로 닫는다. instance는 명시 소비가 없는 제거 후보이며 config/profile/execution/recovery_source는 유지 근거가 있다. 마지막 소비자가 없어지기 전 AST helper를 일괄 삭제하지 않는다.

L01은 실제 운전 host/tool/version/read-call과 같은 단위의 한도가 미확정이다. 조사 대상은 현재 사용하는 Codex/Claude의 운전 문서 읽기 경로이며 역할 stdin 전달과 구별한다. G7의 설치 CLI/실호출 확인 때 호스트의 실제 출력 절단·읽기 설정을 함께 조사한다. byte와 token 사이에 임의 환산 상한을 두지 않는다. 권위 있는 설정으로 판정할 수 없으면 필요한 외부 결정·영향 의무를 상신하며 13-C 통과로 바꾸지 않는다. 학술 외부 어휘도 그 실제 응답 계약에서 확인한다. 근거는 run:phases/001/tasks/document-closeout/evidence/binding-inventory.json, followup-packets.json, review-notes.md와 run:phases/001/manager-evidence/source-excerpts.json이다.

## C11 최종 관문을 막는 도구·실경계 공백

가장 가까운 수리는 mutation.run.fails_unmutated의 증거 부재 처리다. 현재는 정상 child의 반환 집합에 시험 ID가 없으면 통과로 기억하므로 CHILD_NO_RESULT·loader 오류·skip/빈 실행·비정상 exit를 실제 정상 통과와 구별할 정보가 부족하다. mutant의 결과 부재만 막는 검사로는 부족하다. manager는 실제 소스 분기를 대조했으며 아직 동적 재현하지 않았다. phase 002가 작은 실제 parent/child 경계와 정상 대조군으로 이를 재현·수리한다. 시간 경과는 포착 증거가 아니며 D9의 실패 후보에만 수행하는 지연 정상 기준 검사를 유지한다.

기존 변이17분할은 130파일이며 현재 LAYERS 1/2/3의 123모듈을 포함한다. adapter인 git_process/http_transport/powershell_scheduler/system_clock/windows_job 5개와 run_tests.py/test_categories.py는 해당 필터 밖이다. 설계 5.5/6.3 및 현재 도구 정본에 따라 이 7파일은 G6의 layer1/2/3 변이 분모에서 제외한다. adapter 5개는 T4 실제 계약·별도 분기 보고/T5로, runner·격리 표지는 관련 도구 시험과 G4/G5 선택·종료 검증으로 확인할 책임을 유지한다. 제외를 실행 성공으로 세지 않는다. 현 함수·rule·trivial·시험 진입 집합은 fresh T3 뒤 확정하고 오래된 1586함수나 17분할을 분모로 쓰지 않는다.

T5의 smoke 폴더에는 현재 test_*.py가 없고 runner는 빈 선택을 거부한다. probe_cli의 files/background는 작은 protocol_probe 경계라 실제 역할 schema·Job/pythonw·Lean/Mathlib·예약 등록/발화/해제·학술 list_sources의 전체 요구를 대신하지 않는다. G7 work에서 공식 T5 진입점에 실제 smoke를 연결하고 필요한 실호출·말뭉치를 최종 소스 고정 전에 취득한다. T4 단독은 Measurement를 만들지 않아 adapter 분기 보고가 없다. 별도 T4 측정 수리를 배정하며 최종 T3 모집단에 T4를 섞어 해결하지 않는다.

gate-readiness가 관찰한 설치 Codex는 0.162.1, 녹화 manifest는 0.160.0이며 Claude는 양쪽 2.1.289다. corpus12항목/20파일의 해시 일치는 현재 인증·모델 호출 성공을 뜻하지 않는다. Claude background는 실제 event 순서와 현 background_completed_before_result 조건을 재판정해야 한다. Lean/Lake/Mathlib·pythonw·학술 서버 자료의 존재/버전은 확인됐으나 인증·지원 모델·계정 한도·컴파일·예약 권한·MCP 응답은 미확인이다. 독립적으로 가능한 수리를 진행하면서 가까운 G7 작업에서 비밀 비노출 방식으로 조건을 확인하고, 부족한 외부 조건은 정확히 상신한다. 근거는 run:phases/001/tasks/gate-readiness/evidence/gate-readiness.json, population-and-corpus.json, environment.json, source-contracts.json 및 manager의 verification.json이다.

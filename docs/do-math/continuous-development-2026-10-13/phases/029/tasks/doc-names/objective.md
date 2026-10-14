## 목적과 역할

028의 고정판 N01 조사에서 반환한 여덟 issue를 문구·공유 문서 검사·실제 parser 연결·공식 미러·관련 회귀의 한 작업으로 수리한다. 대상은 operator-names F1~F3, cli-control-names F1~F3, role-glossary-names F1~F2다. 이름 조사288절을 다시 수행하지 않고, 아래의 정확 문장/예제와 현재 코드 정의를 사용한다. G1/G3의 확인된 공백을 닫고 이미 검수한 P/PURE/026~027 성질을 유지한다. 최종 review나 전체 관문 실행은 아니다.

## 완료 조건

### A1 수리 기준과 기존 성질 보존

시작 소스를028 manager source-inspected와 대조하고 여덟 finding의 원문·실제 owner·최소 정상/반례·기존 단언을 확인한다. report와 지정 관찰 JSON을 읽되 전체 section-decisions/owner inventory를 다시 쓰지 않는다. 제품 변경 전에 기존 helper의 거짓 통과14개(도구2·초기화JSON2·CLI5·단계/checkpoint5)와 모듈 목록의 실제 차이를 자기 evidence에 연결한다. 같은 현재판의028 순수 관찰을 재사용해도 되며 새 실행과 구분한다. 027 c3의 문서38개 test ID와 실제 기존 단언, P/PURE·line-local owner·배열·callable·정책·반환/단일지급 검사를 보존한다. 삭제/이동이 필요하면 대체 보호 성질과 정확 ID를 보고한다. 조사표를 제품 schema로 복제하지 않는다.

### A2 네 문구 묶음과 실제 동작의 일치

초기화-운전180행의 능력 식별 모듈을 CodexExecAdapter/ClaudePrintAdapter.identity_modules 전건과 맞추고, 그 문장의 집합을 실제 클래스 속성과 비교하는 좁은 검사로 정상·누락1개·타공급자 차용을 구별한다. 현재14/17은 관측값이며 기대 목록을 helper에 별도로 복제하지 않는다. capability_identity의 현재성 의미와 기존 생산자 단언을 유지한다.

CLI knowledge487/512/514/546/573행은 실제 여섯 operation, 새 canonical ID만 받는 import, revise의 새 replacement ID/supersedes/revision+1과 옛 기록·판정 보존, 변경되지 않고 현재 사용 가능한 formal의 재사용, withdrawn 종류 재등록 예외를 설명한다. 기존 ID import를 대체 경로로 안내하지 않는다. CLI external609행은 prepared 전송 표지와 별도 execution.running을 구분하고, 2xx confirmed/True·비2xx+effect_absent failed/False·효과 미입증 unknown/None을 설명한다. 인접 상태표를 함께 읽어 같은 생산/저장 범위를 모순되게 설명하지 않되 runtime/schema를 문서에 맞춰 변경하지 않는다.

CLI748행은 knowledge.kind의 TEXT 구조 검사와 수신자의 활성 또는 같은 묶음 제안 의미 검사를 구분한다. 신규 종류의 독립 검사/활성화 경계와 미등록 반려를 유지한다. 이 세 CLI 문구 묶음은 현재 직접 소비/스키마 단언과 관련 실행에 연결하고, 실제 함수 이름·정상 및 반례의 한계를 근거에 남긴다. 문장을 고쳤다는 이유만으로 기존 소비 시험을 복제하지 않는다.

### A3 도구 명령과 초기화 예제 결속

setup_lean.py/probe_cli.py의 실제 parser를 문서 검사에서 부수효과 없이 사용한다. 필요하면 각 main의 argparse 생성 부분을 작은 builder로 추출하고 main과 doc_code가 그 한 정의를 호출하게 한다. 옵션·기본값·choices·상호배타/필수 관계와 실제 main의 동작은 보존한다. parser 정의를 helper에 복제하거나 다른 도구 flag의 합집합으로 승인하지 않는다. 정상 setup --verify-only --trust-file new.json 및 probe --skill-only는 통과하고 setup --watch 차용·probe --verify-only 차용은 정확 소유 사유로 반려된다. 실제 main 연결은 기존 sim 도구 시험과 부수효과 전 입력 반려 경로에서 확인한다.

README N01-018 설정과 초기화 N01-272의 grant 요청 예제를 실제 configuration.validate_config 및 DECISION/GRANT 정의에 연결한다. 설정은 생략 기본값이 허용되는 정상 입력 예시다. session_limits 오타·grant의 budget_kind 차용과 필요한 필드/절/예제 부재를 반려한다. 날짜·ID·해시 placeholder를 실제 승인이나 실행값으로 처리하지 않는다. 다른 초기화 예제/응답 봉투와027의 부분 역할 JSON을 완전한 grant나 저장 설정으로 검사하지 않는다. 기존 문서 명령/operator mode 단언을 유지한다.

### A4 CLI 표·JSON·단계·checkpoint의 한정 검사

doc_code와 structure.test_doc_code의 실제 전체 문서 순회에 다음 결속을 넣는다. 정상 문서는 통과하고 아래 최소 변형은 해당 owner 사유로 반려돼야 하며, 대상 절·표·선언·fence의 부재가 빈 성공이 되면 안 된다.

- CLI runtime 상태표의 capacity_waiting 오타를 실제 runtime.status 정의에 대조한다. 과제/활동/실행/외부 operation의 동명 상태와126행의 명시 음성 예시를 섞지 않는다.
- 설정표의 단일키 기본값/enum을 실제 DEFAULT_CONFIG/config schema에 연결해 reviewers 2→200을 반려한다. 여러 키를 묶은 설명·생략/조건부 기본값은 실제 의미대로 구분한다.
- query direction synopsis의 both→sideways와 실제 잘못된 조회 조합은 실제 parser/_json_arguments 경계를 사용한다. 문법 placeholder를 사용자 요청으로 실행하지 않는다.
- knowledge 완전 JSON의 operation import→improt와 candidate summary→summray를 실제 control 정의 및 candidate_shape_errors에 연결한다. 개방 control shape만으로 candidate 의미 검사를 대신하지 않는다. relation_claim/academic_requirements·설정 fragment 등 부분 객체를 완전 응답으로 검사하지 않는다.
- CLI N01-250~253의 initial findings 오타, organize root decision 차용, answer answers 오타, judge issue_verdicts[].decision에 proposal의 match 차용을 실제 stage_schema의 정확 owner로 반려한다. 027의 다른 계약 문서 검사도 유지한다.
- CLI N01-256의 완전 checkpoint JSON을 CHECKPOINT_SCHEMA/checkpoint_value에 연결해 current_claim 오타를 반려한다. 주 응답의 checkpoint 문자열과 파일 객체를 구별한다.

전역 자연어 소유 추론기나 모든 단어 목록을 만들지 않는다. 실제 정의를 소비하는 좁은 결속을 재사용하고 중복 parser/schema를 추가하지 않는다. 원 반례와 정상 대조를 제품 회귀로 연결하되 기존 검사보다 약한 단언·통째 예외 처리로 통과시키지 않는다.

### A5 최종 관련 검증·미러·인도

변경을 고정한 정본과 공식 생성 미러에서 같은 관련 선택을 완결한다. 아래 필수 선택에 변경 영향상 필요한 좁은 검사만 더한다. 선택/고유 실제 row/종료 코드와 전후 소스 SHA를 보존한다. 027의38문서시험과 새 단언이 실제 선택/실행됐는지 확인하고 fail/error/not_run을 숨기지 않는다. 공식 mirror --check와 양쪽 skill-only를 확인한다. 이번 parser 추출이 기존 설치/도구 호출과 직접 소비에 영향을 주지 않는지 기존 sim 검사를 사용한다. 새 유료 공급자·Lean 설치/컴파일·OS 예약·학술 호출을 추가할 필요는 없다.

여덟 finding 각각의 해소 근거와 남김, 실제 수정 파일, 기존 단언 보존·판본 재사용 조건을 report에 남긴다. 큰 원시 bytes는 JSON에 억지 변환하지 말고 원파일과 연결한다. 최종 전체 관문·L01·symlink 남김을 유지하고 report 형식 검사에 통과한다.

## 판단과 경계

공유 doc_code/test_doc_code와 미러·캐시·관련 검사를 한 담당자가 소유한다. 수정 가능 제품 runtime은 setup_lean.py/probe_cli.py의 동작 보존 parser 추출뿐이다. do_math의 실제 schema·권한·knowledge/external/제출 의미·어댑터 목록은 변경하지 않는다. 제품 결함이 이 경계를 넘어 필요하면 최소 반례와 후속 책임을 반환한다. README는 지정 예제 결속에 꼭 필요한 표기만, 시험-지침은 이번 검사 책임을 달리 설명할 때만 좁게 고친다. writes에 있다고 무관한 개선을 추가하지 않는다. 이미 종결한 P/N/정책 의미나 과거 전체 PR을 재감사하지 않는다.

공식 검사는 jobs1·전체worker3 이하·동시에 한 묶음이며 실행 중 제품·시험·미러를 고정한다. 저장소 밖 짧은 전용 TEMP/TMP/TMPDIR를 Path.resolve의 실제 대소문자 표기로 지정하고 상위 Git 저장소 부재를 확인한다. resource output도 자기 evidence/c,m 등 짧은 경로를 쓴다. timeout·skip·기대값 완화로 경로/환경 실패를 숨기지 않는다. 기존 sim의 임시 저장·worker는 허용하지만 기존 연구/설치 신뢰/사용자 예약은 변경하지 않는다.

공용 문서·과거 report/evidence·engine·runner·graphify·Git index는 수정하지 않는다. task는 commit/reset/checkout/push를 수행하지 않는다. 기존 dirty/untracked를 덮거나 일괄 정리하지 않는다. G1~G8·원래 요구/보존 모집단은 유지한다. L01 Q1/Q2·원문 UTF-8 byte 미충족과 Windows1314 symlink 실제 반려 미검사, G4 기본전체·G5 freshT3·G6 전수변이·G7 최종판 연결·G8 review는 이번 완료와 별개다.

## 검증 방법

cwd C:/math, Python C:/Users/wogud/AppData/Local/Programs/Python/Python312/python.exe. 시작/끝 소스와 변경 경로를028 manager source-inspected에 대조한다. 필수 입력의 조사 JSON은 지정 반례/문장 위주로 선택해 읽고 실제 정의/현재 단언으로 돌아간다. 기존 관찰의 재사용과 새 실행을 구분한다. 구현 중에는 좁은 진단을 사용하고, 최종 판본에서 다음 관련 선택을 한 묶음으로 실행한다.

`python -u -B .claude/skills/do-math/scripts/run_tests.py structure.test_doc_code unit.test_configuration unit.test_engine_cli_contract sim.test_toolchain_tools sim.test_operator_probe_contract sim.test_provider_collection.IdentityTests sim.test_knowledge_import_control unit.test_knowledge_io_contracts unit.test_academic_external_operations unit.test_academic_external_sends unit.test_submission_extension_semantics unit.test_submission_contracts unit.test_review_cycle_stages unit.test_observation_checkpoint --jobs 1 --output <자기 evidence/c>`

미러는 같은 선택을 .agents/skills/do-math/scripts/run_tests.py로 evidence/m에 수행한다. 실제 수집된 ID와 기존 문서38개/새 시험의 대응을 확인한다. 도구 parser 추출의 영향 검증이 부족하면 해당 main의 기존 sim 소비에 좁은 정상/반려 검사를 추가한다. 외부 서비스를 실행하는 것으로 parser 공유를 입증할 필요는 없다.

공식 생성 절차는 writing-skills의 멀티런타임_동기화.md를 따른다. 생성 전에 변경될 경로를 확인하고 허용 범위 밖 drift는 덮지 않는다. --check와 skill-only의 실제 stdout/stderr/exit를 보존한다. 원 실패와 관찰 도구 오류는 유지하고 마지막 성공으로 덮어쓰지 않는다. 최종 `python services/continuous-development/check.py report C:/math C:/math/docs/do-math/continuous-development-2026-10-13 029 doc-names`를 지정 Python으로 통과한다.

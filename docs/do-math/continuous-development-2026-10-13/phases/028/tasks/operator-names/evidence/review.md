# 028 operator-names 판정

배정된 N01-001~046, N01-269~288의 66절을 판정했다. 제품·시험·미러·공유 문서·캐시를 수정하지 않았고, 공식 시험·OS/모델/네트워크 호출은 실행하지 않았다. 생성물은 이 task의 report/evidence뿐이다.

원packet 후보424회와 역사 all_inline_spans646회는 서로 다른 목록이다. 현재 원문에서 코드펜스를 제외한 inline 출현655회를 좌표와 함께 보존했고, 표의 bare 역할 이름·산문·명령펜스와 JSON 예시7개는 별도로 읽었다. 66절의 결론은 유지40, 기존 근거 재사용19, 검사 보강6, 문구 수정1이다. 같은 helper 공백이 여러 절에 적용되므로 보강6절을 독립 수리6건으로 해석하지 않는다. 이름 판정의 정본 표는 section-decisions.json 하나다.

원제목과 다음 원제목 사이를 현재 좌표로 연결했다. 새 하위 제목도 같은 원절에 포함했다. 특히 README의 원N01-018은39~124행의 실행 환경·모델 설정을, N01-022는192~211행의 책임·인계 판단 기준을 포함한다. SKILL 도입은 frontmatter 뒤 제목·설명까지1~9행이다. 원행번호를 현재 위치로 가정하지 않았다. 자기 절의 정확 합집합·현재 인용·owner/test 경로와 해시를 verify.py로 검사했다.

027 source-inspected의2675소스는 작업 시작과 같다. c3의 정확38문서 row는 모두 passed이며 현재875Python SHA와 전건 일치하고 원process는finished/exit0이다. 이 결과는 기존 실행의 재사용이다. 이번의66절 helper 호출·4개 최소 반례·7개 JSON 구조 확인은 새로운 공식 시험 통과 수가 아니다. defer된 상태/도구/신뢰 반환은 해당 실제 소비 시험의 책임으로 남기고, helper의 빈 목록만으로 그 반환을 인증하지 않았다.

## 후속 세 묶음

1. **도구 인자의 소유 검사(F1).** `setup_lean.py --verify-only --watch`, `probe_cli.py --skill-only --verify-only`는 각각 다른 명령의 flag를 차용한다. 현재 doc_code.command_issues는 do_math.py/$dmCli의 parser와 operator mode에는 결속되지만 이 도구 둘의 parser에는 결속되지 않아 두 반례 모두 빈 issue 목록이다. 실제 도구main의 parser 선언에는 해당flag가 없다. 이 반려는 정적 소스 대조이며 도구main을 실행한 관찰이 아니다. 현재 문서의 정상 도구 예시는 유지한다. 후속은 실제 parser를 부수효과 없이 소비할 수 있는 작은 정본 출구로 도구명/옵션/모드 결속을 추가하고, 기존 do_math/operator 단언을 유지한다. parser 정의를 문서 helper에 복제하지 않는다. README018/043/044와 초기화274·효율283의 같은 도구 범위를 묶는다.

2. **초기화 JSON 예시의 키 검사(F2).** README018의 설정 객체와 초기화272의 두grant 요청은 완전한 입력 예시다. 정상 설정은 실제 configuration.validate_config, 정상grant 구조는 control_contracts.DECISION/GRANT로 확인했다. `session_limits→session_limitz`, `grant.budget_kind="work"`는 실제검사기가 반려하지만 현재 문서helper는 JSON펜스 키를 보지 않아 빈 issue 목록이다. 이는 잘못된 현재 예시를 발견했다는 뜻이 아니라 문서 회귀 검출의 공백이다. 후속은 이 지정 예시의 실제 config/GRANT 정의에 연결하고 누락/오타·타가족 차용을 반려한다. 날짜/ID placeholder는 실행값·승인으로 처리하지 않는다. 초기화의 통치/전환/승인 예시, README의 응답 봉투와027의 부분 역할 JSON을 서로 다른 owner/예시종류로 유지한다.

3. **능력 식별 모듈 문구(F3).** 초기화-운전180행은 Codex 모듈7개와 Claude추가3개를 전부로 열거한다. 실제 CodexExecAdapter.identity_modules는14개이고 ClaudePrintAdapter는그14개+3개다. 빠진 이름은 control_protocol, values, codex_stream, provider_final, control_server, worker_request, cli_execution이다. LocalCLIAdapter.capability_identity는 선언된 전건을 module_sha256에 넣으므로 이들은 실제 능력증거 현재성의 소유자다. 기존 sim.test_provider_collection.IdentityTests.test_capability_identity_has_host_worker_and_cli_hashes는14/17전건을 단언하지만 해당문장을 읽지 않는다. 현재 helper도 이문구를 반려하지 않는다. 후속은문장과공식미러를현재선언에맞추고, 실제클래스속성의집합과문서의집합을대조하는한정검사를연결한다. 정상전건/누락1/타공급자차용을구별하며어댑터목록을줄여문서를맞추지않는다. capability_identity·describe 실호출은 이번에 수행하지 않았다.

세 결과는 같은 doc_code/test_doc_code·문서·공식미러/회귀 소유단위로 통합할 수 있다. F1의 parser 출구가 필요하면 setup_lean.py/probe_cli.py의 정확 변경도 그 work 쓰기범위에 포함한다. 이 task는 product writes가 비어 있으므로 수리하지 않았다. 후속이 이번 반례를 제품 전체 의미 재감사로 확장할 필요는 없다.

## 재사용과 제외의 경계

SKILL의10역할 읽기 표는 실제 reading_map 반환·문서 존재와 현재 reading-map 소비 시험에 연결했다. common은 AI 역할이 아니며 formal_check/모델없는감독도 표의새AI행이아니다. check/scope는각intent_interpretation/identity_review의단계다. 표에있는문서경로와현재순서확인은모델의읽기·독해·준수증거가아니다.

026의 conversation_loss_policy/model_policy/external_policy 지정 의미와027 기본방침 생성/명시우선·양쪽 연결정책 저장·probe분기 성질만 재사용했다. 026의 초기화182행 기본방침 옛문장/옛gap은027현재문장과공식row로 대체하고, 이미끝난질문을다시감사하지않았다. module 목록은그승인범위와다른문장이라F3로따로반환했다. 신뢰의project null/환경반환분기와입력/제출/수입은P/PURE/B132~134의정확owner/현재선언과기존manager근거만연결한다. 동일owner의모든산문을승인하지않았다. consumer-report-reuse.json은025의신뢰와024의status/trace중현재production/testfile이일치하는정확row만분리한다. 이전보고전체의현재판본동등성은주장하지않는다.

Win32_Process/ProcessId/ParentProcessId/CommandLine은013의실제PowerShell관측스크립트가읽는외부CIM이름이다. PT0S는Windows의무제한duration표현이며operator_schedule의TimeSpan.Zero·Task-View와013실예약row/현재소스에연결했다. FileRenameInfoEx와Flags는Win32 API표현이며file_io의22/3과018c4의실제atomic-replace4row/현재product+testSHA에연결했다. 이번OS실행은0건이며과거PID9492한정관측/환경·파일시스템전제와기존실패를유지한다. Python이름이아니라는이유로제품결함을만들지않았다.

파일명·동적경로·예시변수·Lean기호·외부모델ID·명시비지원예시는각문맥에서분류했다. `trust register/transition`은trust제어의JSON operation축약으로읽고현재실행문법인`trust --file`과구별했다. 런타임ID/OID/만료시각·해시placeholder는실값이나사용자승인이아니다.

L01 Q1/Q2·원문UTF-8 byte요구/미충족, Windows1314실제symlink반려미검사, 기본전체/freshT3/전수변이/최종G7판본연결/G8review는남는다. source-start/end와입력27파일의SHA를보존했고공용context/plan/seams·원report/evidence·graphify·Git상태를수정하지않았다. 이인도는배정된work의완료이며개발완료선언이아니다.

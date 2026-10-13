## 목적과 역할

phase 003 F1의 실제 Codex 역할 schema 거부를 제품의 전달·수신 경계에서 수리한다. Codex 0.162.1/gpt-6-astra/low는 보통 maintenance schema의 선택 필드 integration_bundles가 required에 없다는 HTTP 400 invalid_json_schema를 반환했다. worker exit 1, turn.failed, final 부재와 로컬 종료 barrier가 원자료에 있다. 인증 실패나 연구 control_binding 경로의 실패로 바꾸어 설명하지 않는다. 첫 거부 이후의 다른 공급자 제약은 아직 미확인이다.

phase 004~005는 미러 치환과 manifest Git clean 변환을 수리했다. 양쪽 corpus는 현재 각각 17항목·44파일·200866바이트, 41개 명시 SHA 참조이며 88개 경로의 raw/clean 값이 같다. 이전 Codex 실패와 Claude 성공 원자료를 보존하면서, G7의 대표 역할 실호출을 성공시키고 G1/G2의 선택 필드 의미와 기존 수신 검사를 유지하는 것이 이번 단위다. 전체 G7·문서 수리·최종 일반/T3/변이 관문은 후속 책임이다.

하나의 task가 실제 호출자 조사, 필요한 좁은 제품 수리, 관련 회귀, 새 실호출, 녹화·미러까지 맡는다. 공유 ModelRunner와 공식 검사 캐시·생성기를 사용하므로 구현과 시험을 병렬 task로 나누지 않는다. 같은 경계의 과거 변경은 실제 diff·현재 소비자·원보고에서 이번 전달/수신 slice만 대조한다. phase 003에서 이미 검수한 B86/B87 background slice나 PR15 전체를 다시 감사하지 않는다.

## 완료 조건

### A1 실제 실패와 현재 호출자의 계약을 결속

시작 소스 해시·Git 상태와 phase 005 종료 자료를 대조하고 제품 변경과 기존 engine 문서 변경을 구분한다. 원 Codex stream·worker 상태·schema·prompt, phase 003 live-01의 실제 선택/row/exit를 읽어 거부 입력을 확정한다. 같은 판본의 실패를 다시 보기 위한 유료 호출은 필요하지 않다.

contracts.action_schema/with_integration_schema, CoreEngineMixin._response_schema, ModelRunner.run, model_call.classify_run, worker_request.codex_argv 및 실제 호출자를 추적한다. control_binding 없는 직접 최종 응답 소비자와 연구의 중앙 제출 경로를 나눈다. scheduled_operator의 repair_report_schema 소비와 probe_cli·smoke 등 실제 비결박 소비자가 현재 사용하는 schema를 구체적으로 기록한다. 설치 CLI와 비밀 아닌 모델 설정은 실제 현재 상태로 확인한다. 역사 버전·모델을 무조건 고정하지 않는다.

현재 역할 schema의 선택 필드, 중첩 객체/배열, 필수 필드, null 허용 여부와 명시 제약의 의미를 확인한다. integration_bundles 외 선택 필드 repair_responses도 포함한다. 선택 필드 부재가 유효하다는 것과 명시적 null이 유효하다는 것을 혼동하지 않는다. 공급자 표현을 바꿔야 한다면 원 계약과 표현 사이에서 무엇이 보존되는지, 현재 호출자 범위와 실패 표현을 수리 전에 정한다. 설치 코드·원오류에 없는 공급자 제약을 추측으로 확정하지 말고 필요한 경우 공식 1차 문서로 확인한다.

### A2 원래 의미를 보존하는 제품 전달·수신 수리

최종적으로 Codex에 전달되는 형식이 공급자에 수락되고, ModelRunner의 성공 output은 호출자가 준 원래 schema를 통과한 의미 값이어야 한다. 호출자 소유 schema/객체를 제자리 변경하지 않는다. 선택 필드를 삭제하거나 역할 schema를 강제로 필수화해 문제를 덮지 않는다. null/기본값 자동 보충, 잘못된 필드 제거, 검사 비활성화로 부재·null·빈 값·비어 있지 않은 값을 합치지 않는다. 명시적 null이 원 계약상 금지된 경우에는 그대로 거부한다.

필요한 공급자 표현 변환·반환 해석은 제품의 한 소유 위치에서 정의하고 생산·수신·시험이 같은 정의를 사용한다. 기존 호출 흐름을 재사용하고 현 입력과 관계없는 범용 schema 프레임워크나 구판 호환 분기를 만들지 않는다. 표현 선택은 구현 재량이다. 공급자 제약에 직접 담을 수 없는 조건도 원 schema 검증에서 유지하며, 지원하지 못하는 실제 입력은 정확한 오류로 보고한다. 근거 없는 조용한 fallback이나 모델 변경은 허용하지 않는다.

원 역할 schema와 실제 CLI에 넘긴 schema/지시가 다르면 각각의 바이트·해시·관계를 근거로 보존한다. worker가 읽은 snapshot·schema hash, native stream이 선택한 final과 final 파일의 원바이트, 종료 확인의 의미를 유지한다. 전송 응답을 의미 output으로 변환하더라도 원자료를 바꾸거나 최종 응답 불일치를 숨기지 않는다. 원 schema 검증 실패는 성공으로 반환하지 않는다.

Claude와 control_binding 경로의 계약을 보존한다. 중앙 제출 schema를 새 Codex 최종 응답 표현으로 바꾸거나, 연구 경로에 없던 --output-schema를 넣지 않는다. 공통 파일을 바꿨다면 비변경 분기의 실제 회귀 근거를 남긴다. 새 helper가 필요하면 phase의 provider_schema.py 쓰기 위치를 사용할 수 있으나 기존 모듈이 적절하면 새 파일을 만들 필요는 없다. 현재 identity/등록 규칙의 해당 소비자도 함께 맞춘다.

### A3 제품 경로에서 의미 보존과 실패 검출을 확인

원 반례를 포착하는 오프라인 회귀를 수리 전에 관찰하고 최초 실패를 보존한다. 검사 기대값은 원 schema·명시 값과 실제 전달 계약에서 얻는다. 구현 함수를 다시 호출해 기대값을 만들거나 제품 ModelRunner/분류/변환 전체를 mock으로 바꾸지 않는다. 외부 CLI/Job 경계의 기존 대역은 허용하되 실제 제품의 전달부터 수신까지 연결된 결과를 검사한다.

현재 maintenance와 실제 다른 비결박 호출자에 대해 필수 필드 정상/누락, 선택 필드 부재/유효 값/금지된 null, 중첩 선택·배열의 유효/잘못된 값, 추가 필드, 잘못된 JSON/반환 표현을 확인한다. 원 계약이 허용하는 빈 값과 비어 있지 않은 값은 보존하고 허용하지 않는 값은 거부해야 한다. 기존 final mismatch·worker schema hash·native 실패·종료 barrier·Claude·control_binding 시험의 단언을 보존한다. 데이터·원 schema의 불변과 실제 소비자에게 반환된 output을 함께 확인한다.

schema 표현이 바뀌면 support.provider_live의 schema_unchanged 판정을 단순 삭제하지 않는다. 원 역할 schema 보존과 실제 전송 schema의 제품 정의 일치 및 worker 해시 결속으로 정확히 교체한다. 대역도 현재 요청/반환 계약을 따르게 하며 대역만 성공하는 별도 길을 만들지 않는다. 관련 검사 선택은 실제 수정 모듈과 새/수정 시험, 직접 소비 경계에 근거해 정한다. 무관한 전체 스위트를 반복하지 않는다.

### A4 최종 경로의 Codex 실제 호출과 종료를 입증

오프라인 수리가 끝난 판본에서 공식 smoke.test_provider_live.ProviderLiveTests.test_codex_maintenance_files_and_termination을 --jobs 1로 실행한다. 현재 실제 contracts.action_schema({'role': 'maintenance'}) 전체가 의미 계약이다. 실제 ModelRunner·real_ports·worker·adapter·parser와 기존 nonce 파일 쓰기/읽기·checkpoint·최종 응답·로컬 종료를 사용한다. transport가 따로 있으면 그 사실을 명시하며 schema 자체의 축소로 성공을 만들지 않는다.

새 evidence 디렉터리에 CLI 경로/버전, 명시 model/effort와 보고된 model, 원 schema와 실제 전송 schema/지시의 해시, argv·PID·시각·종료 코드, raw stdout/stderr/final·worker 상태, parser/의미 output과 각 판정을 보존한다. 선택과 실제 row 및 실제 프로세스 종료가 대응해야 한다. schema 수락뿐 아니라 유효 반환·파일·checkpoint·종료 조건이 모두 충족돼야 pass다. 실제 시도 전부와 보고된 비용을 세고 비밀 값·전체 환경은 출력하지 않는다.

기본 새 Codex 호출은 수리 후 1회다. 새로 확인한 결함을 고쳐 다시 확인할 때에는 이유와 변경을 붙여 필요한 호출만 추가한다. 반복 실패를 무한 재시도하지 않고 정확한 미완료와 다음 책임을 반환한다. Claude는 직접 경로·도구·입력 조건 불변을 diff와 회귀로 입증하면 phase 003의 성공을 그 범위에서 재사용한다. 그 조건이 깨지면 영향받은 Claude 대표 호출 1회도 수행하고 원자료를 보존한다. 기존 background 성공의 한정 재사용은 유지한다.

실제 외부 조건이 부족하거나 대표 호출이 실패하면 이 A는 fail/not_run이며 task는 partial/blocked다. 정당한 실패 제출과 제품 성공은 구별한다. 새 호출 뒤 실행 경로를 다시 바꿨다면 유효성이 깨진 근거와 필요한 재검증을 명시한다.

### A5 녹화·미러·문서와 인도 증거를 일치

새 성공/실패 원자료를 먼저 evidence에 받고 검사 사이에 corpus로 승격한다. 기존 17항목과 원녹화·실패 verdict는 유지하고 새 항목/부속 파일을 추가한다. manifest의 source/schema/recordings SHA와 버전·명령·role·verdict가 실제 바이트·의미와 대응해야 한다. 두 schema가 있으면 무엇을 뜻하는지 오독 없이 연결한다. 현재 parser의 새 raw 재생과 제품 의미 수신 검증을 구별해 연결하고 기존 전체 corpus 순회를 유지한다.

관련 회귀 및 정본/미러의 structure.test_corpus, unit.test_corpus_replay, contracts.test_doubles_follow_corpus를 통과한다. 녹화 최대 크기는 기존 5MB 계약을 유지한다. 공식 생성 전 변경 계획과 현재 dirty를 대조하고 허용된 대응 파일만 생성한다. --check와 probe_cli --skill-only를 통과하며, 현재 양쪽 corpus 전 파일의 raw/clean Git object ID 및 모든 명시 SHA 참조를 검산한다. cwd C:\math와 / 상대 경로의 실제 argv를 기록한다. phase 005의 -text 속성과 phase 004의 verbatim 규칙을 유지한다.

시험 지침과 필요한 CLI/이음새 문서에는 실제 원 계약·전송 표현·반환 검증·실행 입력·증거 범위를 반영한다. 마지막 소스 해시·선택/row/exit·검사 중 불변·미실행과 재사용 조건을 report에 남긴다. G7의 대표 호출 수리와 아직 남은 Job/pythonw·Lean/Mathlib·예약·학술·L01, G4~G6 및 최종 review를 구별한다.

## 판단과 경계

writes의 product 파일은 이번 전달·수신 수리에 필요한 위치만 허용한 것이다. 목록에 있다는 이유로 모두 고치지 않는다. contracts.py와 core_engine.py의 원 역할 의미, 연구 중앙 제출·저장·스케줄러는 읽기 전용이며 이 문제를 피하기 위해 의미를 바꾸지 않는다. 정의 위치가 writes 밖에서 실제로 필요하면 증거와 정확한 후속 범위를 반환한다. 제품·시험·문서 정본은 .claude이며 .agents 대응 파일은 공식 생성물이다.

기존 phase 003~005의 미커밋 제품 변경, 다른 task의 report/evidence, 공용 문서·engine·기존 자료를 보존한다. Git stage/commit/checkout/reset/push, graphify 갱신, 패키지·인증·전역 모델 설정 변경, 기존 연구 시작/재개/삭제와 OS 예약 변경은 수행하지 않는다. 이번 새 scratch와 원자료만 사용한다. 예전 manifest를 통째로 재직렬화해야 한다면 각 기존 entry/파일/해시/verdict의 불변을 검산한다.

검사 묶음은 순차, worker 합계 3 이하, 실제 공급자 검사는 --jobs 1이다. 정상 대기에 timeout을 추가하지 않는다. 실행 중 제품·시험·corpus를 고정하고 관찰 도구 yield를 실패로 세지 않는다. result.json 관찰에는 file_io.read_bytes_shared를 사용한다. 좁은 구현을 끝내는 데 필요한 새 사실만 찾고 unrelated 개선은 finding으로 반환한다.

## 검증 방법

cwd는 C:\math, Python은 C:\Users\wogud\AppData\Local\Programs\Python\Python312\python.exe다. 최초/최종 소스와 명령별 argv·비밀 아닌 지정 입력·시각·PID·stdout/stderr·실제 exit를 evidence에 남긴다. 기존 evidence를 덮어쓰지 않는다.

1. A1 입력과 실제 호출자를 대조하고 수리 전 오프라인 반례를 공식 run_tests.py의 정확한 시험 ID로 실행한다. 기존 live-01 원실패는 재사용한다. 작은 계약/변환 시험과 실제 runner 수신 회귀를 단계적으로 실행한다.
2. 변경 모듈의 관련 시험과 새/수정 시험을 `& '<Python>' -u -B .claude/skills/do-math/scripts/run_tests.py <실제 시험 ID들> --jobs 1 --output <새 evidence 경로>`로 수행한다. 소비자는 시험 지침에 따라 import/구문 및 직접 계약을 확인한다. 실패 후 수정이 없으면 같은 검사를 반복하지 않는다.
3. `run_tests.py --tier T5 --list`에서 기존 양 공급자가 선택되는지 확인한다. 현재 DO_MATH_SMOKE_* 입력을 확인해 지정한 뒤 `run_tests.py smoke.test_provider_live.ProviderLiveTests.test_codex_maintenance_files_and_termination --jobs 1 --output <새 live 경로>`로 실제 Codex를 검증한다. 모델 입력 정본과 세부 절차는 현재 시험-지침.md와 support.provider_live.py를 따른다. Claude 재호출은 A4의 판본/경로 판단에 따른다.
4. 녹화 승격 후 정본의 `run_tests.py structure.test_corpus unit.test_corpus_replay contracts.test_doubles_follow_corpus structure.test_test_smells --jobs 1 --output <새 경로>` 및 필요한 수신 회귀를 수행한다. 공식 build_skill_mirrors.py로 생성한 미러에서도 앞 세 corpus 모듈을 검사한다. cache 사본 정리는 허용된 .timings에 한정한다.
5. 같은 Python으로 `build_skill_mirrors.py --check`, `probe_cli.py --skill-only`, 양쪽 corpus 전건 Git raw/clean 비교와 원 SHA 검산을 수행한다. 원 schema와 전송/수신 표현을 실제 원파일에서 대조한다.
6. A1~A5와 수정 파일·모든 실패/재사용/남김을 report.json에 쓰고 `& '<Python>' -B services/continuous-development/check.py report 'C:\math' 'C:\math\docs\do-math\continuous-development-2026-10-13' 006 codex-schema`를 통과한다. report 경로와 상태를 반환하며 다음 phase를 직접 기동하지 않는다.

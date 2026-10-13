# Codex 전달/수신 slice

시작 HEAD는 9c917b644360ebdb0d6fd0e0cc8ef3191f4956b8이다. source-start의 2624개 해시는 phase 005 source-final과 전부 같다. protocol.md도 phase 005 종료 이후 달라지지 않았다. phase 004→005에서 관찰된 기존 engine 문서 변경과 이번 제품 변경을 섞지 않는다. Git 시작 dirty는 start-state.json에 보존했다.

## 원 실패와 현재 소비자

phase 003 live-01은 두 공급자 선택/두 실패/exit 1이다. 그 Codex는 worker exit 1, HTTP 400 invalid_json_schema, integration_bundles가 required에 없다는 오류, turn.failed, final 부재, confirmed local barrier다. 선택 필드 repair_responses도 원 required에 없으며, integration_bundles의 previous_hashes는 중첩 선택 사전이다. null을 허용하지 않는다. minItems/uniqueItems/minLength/pattern 및 additionalProperties 제약도 유효하다. caller-schemas.json은 현재 실제 생산자의 전체 결과를 보존한다.

contracts.action_schema → with_integration_schema → CoreEngineMixin._response_schema의 보통 maintenance 경로는 같은 전체 의미 스키마다. 연구 호출은 call_engine이 control_binding을 전달하고 중앙 제출/저장 관문에서 이 스키마를 적용한다. ModelRunner는 이 경로에 --output-schema를 전달하지 않고 최종 provider 증거만 수집한다. native_final.verified_native_final은 최종 원바이트·published prompt·worker 상태·Job 종료를 재검사하며 이번에 수정하지 않았다.

비결박 호출자는 (1) scheduled_operator.recovery의 repair_report_schema(diagnosed=False/True), (2) probe_cli.run_case의 status=CLI_OK/nonce const/phase enum 객체, (3) maintenance T5 smoke다. repair 스키마는 6필드 또는 진단 시 8필드 모두 필수이며 null을 허용하지 않는다. probe의 3필드도 전부 필수다. 이들이 소비하는 result.output은 원래 JSON 값이어야 한다. helper 이름이나 schema 존재만으로 실제 호출 성공을 주장하지 않는다.

## 표현 결정과 보존

provider_final.output_contract와 semantic_output을 유일한 제품 정의로 삼는다. 기존 provider_final은 이미 Codex/Claude identity_modules와 LAYERS 1에 포함되어 있다. 새 모듈·schema 변환 프레임워크·구판 fallback은 만들지 않는다.

Codex 비결박 응답은 필수 문자열 output_json 하나와 additionalProperties=false인 객체다. 문자열 설명에 원 schema 전체를 JSON으로 싣는다. 따라서 스키마 언어의 모든 제약을 공급자 언어로 번역하지 않아도 필드 부재/null/빈 값/값이 그대로 전달된다. input.txt/stdin은 원 prompt 그대로여서 pinned prompt seal/입력 byte 검사도 그대로다. output.schema.json은 원 schema, transport.schema.json은 CLI 전달용이며 worker snapshot/hash는 후자를 가리킨다. 원 schema는 전달 schema의 설명 안에도 완전하게 포함되므로 이 관계를 실제 바이트로 검산한다.

엄격한 envelope JSON 파싱·형식 검사 → 내부 JSON 파싱 → 기존 canonical_json 검사 → 호출자가 준 원 schema 검증 순서다. 잘못된 필드 삭제·null/default 보충·선택 필드 필수화는 없다. 의미 검증 실패는 output_validation이며 기존처럼 해석 가능한 원 값을 실패 output에 보존한다. 봉투나 JSON 자체가 잘못되면 output=None이다. raw final과 stream-selected final의 바이트 일치, worker hash, native 실패, 로컬 종료 검사는 변환 전에 기존 collector가 수행한다.

공식 근거는 2026-10-14 KST에 조회한 [OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses)의 모든 속성 required, 닫힌 객체와 지원 subset 규칙이다. 문서의 null union 권고는 원 역할에서 null 금지인 선택 필드의 부재 의미를 보존하지 않으므로 적용하지 않았다. CLI의 output-schema 전달은 설치 worker_request.codex_argv 및 실제 help로 확인했다. schema 수락 여부는 문서 추론과 별도로 이번 유료 실호출에서 판정한다.

Claude는 원 schema와 원 prompt, 기존 worker의 --json-schema 표현을 유지하고 새 수신 함수의 Claude 분기도 이전 strict_json_loads와 같다. control_binding은 semantic_output 전에 반환한다. 그 분기 및 원래 Claude actual tools/input 조건의 불변·관련 회귀가 재사용의 조건이며 전체 G7 성공으로 확대하지 않는다.

## 수리 전 반례와 회귀

red의 정확한 한 시험은 제품 수리 전에 required/properties 차이에 integration_bundles와 repair_responses를 보고하며 실패했다. 원 ModelRunner/worker/adapter/수집기를 모두 사용하고 외부 CLI/Jobs만 대역이다. semantic의 6개 시험은 선택 필드 부재/유효 배열/금지 null, 중첩 previous_hashes 부재/빈 사전/값/잘못된 값, 필수 누락, 추가 필드, 배열 제약, JSON/봉투 파손 및 native final mismatch를 검사했다. 정답은 원 schema와 명시 값에서 얻었다. semantic-final은 원 validator 오류 경로/문구까지 비교하도록 단언을 보강하고 실제 probe_cli 소비자도 새 전송 형식을 읽는 외부 대역으로 확인했다.

related-01의 5실패는 새 시험의 예외 세부 단언 1개와 구 final 표현을 보내던 4시험이다. 4시험은 현재 전송 표현으로 fixture를 바꾸고 기존 의미·수치·전달/종료 단언을 유지하여 related-02에서 통과했다. 냄새 검사는 원 schema validator 오류 경로/문구 단언을 더한 뒤 semantic-final에서 통과했다. 원 실패는 삭제하지 않는다.

## 배정 밖 소비자 실패

consumers는 45선택, 34통과, 11실패다. 9개 probe 시험의 support.operator_finish_scene.InputProcess / support.operator_probe_inputs.ProbeCLI는 --output-schema 파일의 top-level에서 nonce를 찾거나 원 구조와 같다고 가정한다. repair 실패 보존 시험 1개도 call.schema == OPERATOR_SCHEMA를 가정한다. native storage 시험 1개는 explicit stdout/final에 구 {}를 쓰므로 현재 봉투 수신에서 거부된다. 이 파일들은 이번 writes에 없다. CLI 대역에 실원자료를 조용히 재작성하는 길을 추가하거나 수신에 구형 fallback을 넣지 않았다. manager가 해당 fixture와 원 semantic schema/transport schema의 명시적 구분을 함께 배정해야 한다. exact IDs/traceback은 consumers 보고와 원 stderr에 있다. 이로 인해 A3은 미충족이며 부분 결과를 성공으로 올리지 않는다.

contracts.pairs._runner_result_samples는 source_request 없는 합성 collection을 직접 classify_run에 준다. 기존 수신/저장 pair 자체는 통과하지만 'collected' 명칭의 표본도 이제 output_validation이 되어 성공 branch 표본을 잃는다. 이 도우미도 writes 밖이다. 실 collector가 만드는 source_request를 사용하는 표본으로 고쳐 status/분기까지 명시 검사할 후속 범위다.

## 과거 검토

B49/065a323a의 실제 runner_gaps/worker_rejections 도입 diff를 history-b49.diff에 보존했다. 현재 caller/receiver와 원 board의 changed_area/structure report 좌표를 대조했다. 두 원 Temp report는 현재 없으며 161/6 통과라는 역사 수치를 새 검증으로 합산하지 않는다. pinned 입력/한도·중앙 binding·worker 반려/파일 무효과·canonical number 거부·Job 종료/정리 성질은 현재 관련 회귀로 유지한다. 수치 거부 시험의 native fixture만 전송 봉투로 바꿨으며 canonical value 거부 기대값은 유지한다. B49 이 slice 밖의 관찰 가족, B86/B87의 이미 승인된 background slice, PR15 전체는 새 검토 완료로 바꾸지 않는다.

## 최종 실호출과 인도

현재 PATH가 해소한 CLI는 C:/Users/wogud/.codex/packages/standalone/releases/0.162.1-x86_64-pc-windows-msvc/bin/codex.exe다. 설치 버전은 0.162.1, 현재 프로젝트 설정의 모델은 gpt-6-astra이고 cache가 지원하는 low를 명시했다. phase 003의 다른 절대 경로를 무조건 고정하지 않았다. 실제 새 호출은 Codex 한 번이며 공식 1선택/1passed/exit 0, 44.922초다. smoke의 11개 checks가 모두 true이고 worker CLI exit 0과 Job barrier를 확인했다. 원 schema/hash, 전송 schema/hash, prompt/hash, request snapshot, worker PID/creation_filetime, argv hash, native stdout/stderr/selected-final/final, semantic output과 파일/checkpoint는 live scratch에 있다. raw/native final은 봉투 그대로이며 semantic output으로 덮지 않았다.

Codex stream은 input_tokens=78318, cached_input_tokens=57984, output_tokens=502, reasoning_output_tokens=0, cache_write_input_tokens=0을 보고했다. 비용과 실제 모델명·내부 공급자 요청 수는 보고하지 않았으므로 0원/모델명 확인/한 API 요청으로 주장하지 않는다. 명시 model/effort와 ModelRunner 호출 횟수를 구분한다. 자동 재시도나 추가 Claude/background 호출은 없다.

claude-reuse.json은 phase 003 live-02 원자료를 현재 parser·collection_reasons·classify_run으로 다시 받아 completed와 정확한 semantic output을 확인한 결과다. 현재 smoke_request가 이전 nonce/workspace에서 만드는 prompt/schema/expected/checkpoint가 원자료와 같고 worker/parser/collector/tool 경계 12모듈은 이전 해시 그대로다. 실행 파일의 경로·버전·전체 help 원바이트도 같았다. 당시 surface의 identity는 빈 객체여서 역사 CLI 바이너리 SHA 동등성은 주장하지 않는다. 이 한계와 실제 코드 분기·관련 Claude 회귀를 근거로 기존 성공 범위만 재사용한다. 첫 보조 script가 그 미기록 SHA를 찾다가 KeyError로 실패한 출력/스크립트도 보존하고, 자료가 보장하는 비교로 교정한 reuse02를 구분한다.

새 녹화 codex-maintenance-transport-20261014는 native parser verdict와 별도의 semantic_output 및 원/전송 schema를 연결한다. 이전 17항목과 기존 43개 비manifest 파일은 각 트리에서 불변이다. 현재 각 트리는 18항목·51파일·223685바이트이며 50개 명시 SHA 참조가 일치한다. cwd C:/math와 / 상대 경로의 실제 argv를 기록한 Git raw/clean 102경로가 전건 같다. corpus 하위 -text와 생성기 verbatim 규칙은 불변이다.

정본 corpus+냄새 18/18, 미러 corpus 14/14는 최종 Python 각 865개와 동일 판본이다. 공식 생성 계획은 허용된 대응25파일만 가리켰고 생성 후 미러 시험이 갱신한 .timings 한 파일만 공식 생성기로 재동기화했다. --check는1305파일 drift 없음, --skill-only는 verified, 모두 exit0이다. source-final의2640파일 중 시작 대비50변경(양쪽25개씩)은 전부 writes에 있다. 최종 live 뒤 제품 runtime와 smoke helper는 불변이고 바뀐 Python은 corpus 검증3모듈뿐이다. 관련 시험의 전체 source hash 차이는 verification-final.json에 명시하며, 이전 부분 결과를 최종 전체 스위트 성공으로 합산하지 않는다.

시험 비용은 soft budget으로 보고한다. 최초 의미 반례 다축 시험은3.172초로 sim2초 기준을 넘었으며 원 schema로 실제 runner 호출을 반복해 각 제약 실패와 값 보존을 확인하는 비용이다. 후속 같은 축의 오류 문구 보강 실행에서는2초 이하였다. 전체 냄새 검사는 약12초로5초 기준을 넘었으나 범위를 줄이지 않았다. 시간 초과·실패로 재분류하지 않았다.

보조 environment 관찰의 첫 실행은 surface_report의 bytes를 그대로 JSON 저장하다 TypeError였고, 원출력과 script를 보존한 뒤 json_safe로 저장한 두 번째 관찰이 통과했다. 실제 모델 호출 시도가 아니며 제품 실패와 구분한다.

마지막 정적 직접소비 조회에서는 sim.test_observation_delivery.StreamChunkTests.test_one_native_chunk_is_one_owner_transaction도 구 {} final과 completed 기대를 함께 갖는 것을 확인했다. 이 시험은 이번 명령 선택에 포함하지 않았으므로 추가 실제 실패로 세지 않는다. 같은 외부 fixture 수리 범위에 포함해 현재 봉투와 원 관찰 바이트 단언을 함께 유지해야 한다. flows.test_provider_raw_ingress는 malformed row 거부를 검사하므로 이번에는 다시 실행하지 않았고, 후속 fixture 검토에서 원래 collector 반려 이유가 출력 형식 반려로 가려지지 않는지도 확인한다.

이번 인도는 A3/관련 회귀 인도 부분의 미충족 때문에 partial이다. manager가 배정 밖 fixture를 수리하고 실패한 직접 소비와 기존 단언을 다시 확인해야 한다. Codex 실제 호출 결과는 그 후 제품 실행 경로가 바뀌지 않는 한 이 범위에서 재사용할 수 있다. G4~G6·전체 T4/T5, Job/pythonw·Lean/Mathlib·예약·학술·L01·최종 review는 수행하지 않았다. Git stage/commit/reset/checkout/push와 graphify 갱신도 수행하지 않았다.

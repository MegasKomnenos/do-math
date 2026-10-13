# phase 007 provider-consumers의 판단 근거

## 시작 판본과 실제 공백

시작 HEAD는 61f9e06fc15fb49ef30bf7d93c83c92e275eebad다. source-start.json의 2,640개 경로와 SHA256이 phase 006 source-final.json과 전부 같다. 기존 미커밋·미추적 상태는 start-state.json에 원문으로 보존했다. 제품 runtime, 공용 계약, engine 및 다른 task 기록은 수정하지 않는다.

phase 006 consumers/report.json은 45선택, 34passed, 11failed다. 실패한 11개 ID와 원 traceback을 previous-failures.json에 추출했고 원보고도 그대로 둔다. 9개는 ProbeCLI가 전송 schema의 최상위에서 nonce를 찾는 문제, 1개는 복구 시험이 CLI schema를 OPERATOR_SCHEMA와 같다고 보는 문제, 1개는 native storage의 구 final 문제다. 이번 작업 전 같은 45개를 다시 실행하지 않았다.

phase 006 pair-observation.json의 Codex/Claude 비결박 collected 두 표본은 failed/output_validation과 source_request KeyError다. 원 pairs.py는 실 collector를 거치지 않는 합성 dict를 classify_run에 주고, test_pairs는 수신/저장 가능성만 검사했다. 기존 역방향 검사는 Pair.fields의 필수·선택 필드 전체에서 모든 생산 표본의 written 합집합을 빼는 방식이며 유지했다.

## 소비 범위와 유지할 기대값

| 입력 생산자/시험 | 직접 소비 범위 | 변경과 보존 성질 |
|---|---|---|
| support.provider_runs | ScriptedCLI, support.model.FakeCLI, operator/probe 및 sim.test_provider_schema | cli_schemas가 실제 worker argv의 schema를 읽는다. Codex description의 원 schema를 추출한 뒤 제품 output_contract와 전송 구조를 대조한다. cli_final이 같은 해석을 사용한다. 직접 worker가 명시하는 schema, Claude 직접 JSON, schema 없는 bound 경로와 explicit stdout/final 원바이트는 유지한다. |
| support.operator_finish_scene.InputProcess | sim.test_operator_finish_recovery/provider/cli/children/supervision, sim.test_operator_supervision_contract; flows.test_operator_recovery_contract/test_scheduling_close_repair_exit/test_scheduling_close_remaining_exits | call.schema는 실제 전송 계약, call.output_schema는 원 의미 계약이다. 응답 값과 반려값은 원 계약에서 만든다. 복구 정상/반려 출력·정확 오류·정산·provider limit·종료·저장 단언을 유지한다. |
| support.operator_probe_inputs.ProbeCLI | sim.test_operator_probe_contract | nonce는 원 schema의 const다. prompt의 checkpoint, 파일 내용, 학술 도구명과 정지 사건을 유지한다. explicit stream과 Codex final 파일은 같은 현재 봉투 바이트를 쓰며 모든 기존 checks를 유지한다. |
| support.cross_installation.recover_report | flows.test_cross_required_events.RequiredEventSeedTests의 installation_repair 두 사례; support.cross_research_machine.AlphabetMachine.installation_recovery | 원 repair_outcome 필드는 output_schema에서 확인한다. unresolved의 정산/재시도 금지와 repaired의 단일 후속을 검사한다. 모델/검증 port의 합성 보고이며 실제 설치 수리 성공은 주장하지 않는다. 상태기계의 전체 상태공간 실행은 배정 밖이다. |
| sim.test_observation_delivery.StreamChunkTests | 실제 runner의 한 chunk 전달 | 관찰 20개와 한 callback을 유지하고 현재 final을 명시한다. 전달된 행 바이트와 의미 output {}도 검사한다. |
| flows.test_provider_native_storage.NativeStorageTests | 실제 runner → 관찰 소유자 → Repository → 재읽기 | 0.25, 2^53, 2^53+1 수치, 공개 블록 4개, 역할/순서/source hash/원바이트/재읽기 단언 유지. 공개 assistant final은 native 봉투 바이트 그대로 저장하고 최종 의미 output은 {}다. |
| flows.test_provider_raw_ingress.RawIngressTests | worker → strict collector 및 live 관찰 → 실제 저장/중복 방지 | 두 공급자 정상 대조군과 7개 오형태 × 3개 observation mode × 2공급자 42사례. 정확 collector 반려·원 stream·정상 후속 한 번·adapter 소유·저장과 재전달 무효과를 검사한다. |
| contracts.pairs._runner_result_samples | stored artifact와 operator file의 실제 수신 검사, 새 분기 단언 | 실제 runner/worker/collector 결과 8개를 만들며 요청/raw/hash/termination, status/output/collection/error_kind/error를 검사한다. 저장 전 json_safe와 operator._json 수신 경로 및 필드 역방향 검사를 유지한다. |

읽기 탐색은 이 helper들의 소비와 명시 native final 경계로 한정했다. provider_final.output_contract/semantic_output, ModelRunner.run, model_call.classify_run, 실제 adapter.collect와 CLI-실행-계약의 비결박 최종 응답 절이 제품 정본이다. 새 제품 전송 정의나 fallback은 만들지 않았다. 기대 output·수치·오류는 명시 입력/기존 계약에서 얻으며 제품 decoder의 출력을 정답으로 재사용하지 않는다.

## 성공 표본 반례와 수리

새 test_runner_samples_cover_success_bound_incomplete_and_stopped를 기존 합성 표본에 실행한 pair-red는 공식 1선택/1failed, 두 subTest(Codex/Claude collected) 실패, exit 1이다. 기대 completed/{}/오류 없음과 실제 failed/None/output_validation의 차이를 원 stderr에 보존했다. 원 표본 이름이나 저장 가능성이 성공 증거를 대신할 수 없음을 재현했다.

표본은 ProviderJobs와 ScriptedCLI라는 기존 외부 경계 대역으로 실제 runner·worker·adapter·collector를 실행하도록 교체했다. bound는 실제 프로필, launch ticket, ControlTransport.issue로 만든 결박을 사용하고 native prose/None output/provider_evidence_only를 검사한다. incomplete는 실제 CLI exit 1에 따른 cli_nonzero_exit 수집 반려다. stopped는 worker가 응답을 쓴 뒤 Job이 살아 있다고 보고하는 외부 경계에서 소유자의 정지 요청을 전달한다. 시간 초과를 유발하는 표본이 아니다. Claude 비용 0.0123을 실제 stream에 남겨 json_safe 저장의 소수 입력도 유지했다.

pair-green의 같은 정확한 ID는 1선택/1passed, exit 0이다. 뒤의 직접 소비 최종 묶음에서도 전체 pair 수신·분기·필드 모집단을 확인한다.

## 첫 직접 소비 묶음에서 발견한 raw fixture 문제

첫 consumers는 98선택/97passed/1failed, exit 1이며 phase 006의 11실패는 모두 통과했다. 원자료 반려 시험의 보강 단언이 42사례에서 실패했다. 그 당시 시험 원문을 raw-ingress-first.py와 공식 원출력에 보존했다.

원 fixture는 Codex 최종 agent_message와 turn.completed 사이에 정상 후속 turn.started를 삽입했다. codex_stream.parse_jsonl의 final 선택은 종료 직전 agent_message를 요구하므로 이 순서는 malformed 행과 별개로 final_response_mismatch를 만든다. 이를 final 형식 오류의 정상 기대값으로 유지하지 않았다. 현재 _native_stream은 정상 후속 turn.started를 final보다 앞에 두고, 동일 함수에서 malformed 행만 뺀 정상 대조군을 두 공급자 모두 completed/{}로 검사한다. 기존 정상 후속 event의 type과 execution_id는 보존한다.

단, malformed 입력 자체에 따른 terminal/final 부재는 구분해야 한다. Codex는 nonobject 행을 unknown으로 기록하고 계속 읽으므로 이 5축은 jsonl_parse_incomplete 하나다. duplicate/nonfinite JSON에서는 즉시 반환해 terminal/final 선택을 보류하므로 turn_completed_missing/jsonl_parse_incomplete/final_response_mismatch가 된다. Claude는 모든 malformed 행에서 읽기를 멈추고 정상 종료/선택 final을 게시하지 않아 turn_completed_missing/jsonl_parse_incomplete/final_message_missing가 된다. 이 기대값은 codex_stream.py의 즉시 반환·final 인접 조건, claude_stream.py의 중단·parse_complete 조건과 cli_execution.collection_reasons의 순서에 근거한다. 원 final/정상 stream 대조와 exact error 목록을 함께 검사하므로 unrelated output_validation을 같은 통과로 세지 않는다.

## 검증·인도의 범위

공식 실행은 run_command.py가 argv/cwd/PID/시각/stdout/stderr/exit와 소스 전후 해시를 기록한다. 제품·시험을 실행 중 편집하지 않았으며 공식 비용 캐시 변화는 별도로 기록한다. 전체 worker 합계는 1이고 검사 묶음은 순차 실행한다. 원실패는 수정하지 않는다.

live-reuse.json은 phase 006 실호출의 정확한 runtime 124개와 smoke 입력 3개가 불변이며 현재 Codex/Claude의 경로·실행 파일 SHA·version/help가 phase 006과 같다는 별도 관찰이다. 모델 호출은 0회다. phase 003 Claude의 당시 바이너리 SHA 미기록 한계는 그대로다. phase 006의 재수신/입력/경로/버전/help 근거로 승인한 한정 재사용만 유지하고 background의 역사 passed=false를 바꾸지 않는다.

공식 mirror 계획이 허용된 대응 13파일만 가리킴을 dirty/overlay manifest와 대조한 뒤 생성했고 실제 변경 목록이 계획과 같았다. 미러 실행 뒤 .timings 한 파일만 공식 생성기로 다시 맞췄다. 최종 --check는 1,305파일 drift 없음, --skill-only는 installed_skill_structure verified, 각각 exit 0이다. 문서 의미나 실제 연구 연쇄의 합격으로 해석하지 않는다.

최종 source-final은 2,640개이고 실제 변경 26개(정본 13·미러 13)는 모두 writes 안이다. HEAD도 시작과 같다. runtime 및 기존 corpus는 불변이다. verification-final.json에서 전건 선택/고유 row/실제 exit/최종 Python 판본을 대조했으며 corpus-final.json에서 양쪽 각각 18항목·51파일·223,685바이트·50명시SHA 및 102개 Git raw/clean 경로의 동등성을 확인했다.

| 최종 묶음 | 선택/실제 고유 row/통과 | 공식 total_seconds | 종료 |
|---|---:|---:|---:|
| consumers-final | 98/98/98 | 258.0 | 0 |
| boundaries | 74/74/74 | 25.3 | 0 |
| corpus | 14/14/14 | 0.4 | 0 |
| mirror | 59/59/59 | 50.4 | 0 |

네 묶음 모두 실패·오류·skip·미실행이 없고 검사 중 Python 변화도 없었다. pair-red, pair-green 및 첫 consumers와 최종 판본의 차이는 verification-final의 python_changes_since_run에 남겼다. 중간 실패를 삭제하거나 부분 수치를 전체 일반 성공으로 합산하지 않는다.

시간은 soft budget으로 기록한다. 최종 새 pair 분기 시험은 0.375초, 기존 전체 pair 수신 시험은 2.266초로 단위 시험 200ms 기준을 넘었다. 양 공급자의 실제 runner/worker/collector 호출과 실제 직렬화 수신을 반복하는 비용이며, 합성 collection으로 돌아가거나 분기를 생략하지 않았다. raw ingress는 15.594초로 42사례의 실제 관찰 게시·저장·재읽기 비용을 유지했다. 최종 직접 소비 묶음 258초에는 기존 completed-goal 템플릿/실 저장 경로도 포함되며 timeout이나 실패 판정으로 바꾸지 않는다. 명령 자체의 시작/종료 시각과 준비 비용은 각 command.json에 별도로 있다.

실제 모델 재호출, 전체 일반/T3/극단 변이, 나머지 Job/pythonw·Lean/Mathlib·예약·학술·운전 출력 한도 및 G4~G8 최종 review는 수행하지 않았다. Git stage/commit/push, graphify 갱신, 실제 연구/예약 변경도 수행하지 않았다. 이번 task의 A1~A5와 프로젝트 전체 완료는 구별한다.

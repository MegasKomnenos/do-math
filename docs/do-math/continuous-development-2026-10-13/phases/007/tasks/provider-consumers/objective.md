## 목적과 역할

phase 006에서 바뀐 Codex 전송 계약을 직접 소비 시험에 반영하고, 성공 표본이 실패 결과로 바뀌어도 통과하던 검사 공백을 닫는다. 이 작업은 G1~G3의 실제 소비·기존 단언·검출력을 보존하고 공급자 수리 단위의 관련 회귀를 완료하는 work다.

현재 비결박 Codex의 CLI 응답은 문자열 `output_json` 하나를 담은 객체다. `provider_final.output_contract`가 이 전송 schema를 만들고 그 설명에 원 역할 schema 전체를 싣는다. `ModelRunner`는 원 schema를 `output.schema.json`, 실제 전달 schema를 `transport.schema.json`에 보존한다. collector가 원자료·worker·종료를 확인한 뒤 `model_call.classify_run`이 봉투를 해석하고 원 schema로 의미 값을 검증한다. Claude는 직접 JSON, 연구 `control_binding`은 중앙 제출이라는 기존 경로를 유지한다.

phase 006은 Codex 대표 실호출 1건과 11개 판정에 성공했으나 직접 소비 45건 중 11건이 실패해 partial이다. 외부 CLI fixture가 전송 schema를 원 역할 schema로 읽거나 구 final을 보낸다. 또 `contracts.pairs._runner_result_samples`의 비결박 성공 표본 두 개는 `source_request`가 없어 실패 결과가 되지만 저장 검사만은 통과한다. 이번에는 제품 실행 경로를 고정하고 해당 시험 입력·단언을 수정한다. 실제 모델 재호출, 전체 일반/T3/변이와 나머지 G7 연쇄는 이 task의 실행 범위가 아니다.

공용 문서와 phase.json의 필수 입력을 먼저 읽는다. phase 006 report의 F2/F3 및 `review-notes.md`, manager 검수의 근거가 원실패와 후속 책임을 연결한다. 보고에 없는 추가 정적 관찰은 `support.cross_installation.recover_report`의 `call['schema']['properties']` 가정이다. 이 항목과 단일 chunk 시험은 아직 새 실패로 실행 확인한 항목이 아니다.

## 완료 조건

### A1 현재 입력과 소비 범위를 확정

시작 소스를 phase 006 `source-final.json`과 대조하고 기존 미커밋 변경을 보존한다. `consumers/report.json`에서 11개 실패의 정확한 ID·원출력을 확인한다. 원실패를 다시 보기 위해 동일한 45개를 수정 전에 반복할 필요는 없다. 성공 표본 공백은 `pair-observation.json`과 현 `pairs.py`·`test_pairs.py`의 실제 status 및 수신 단언을 대조한다.

`operator_finish_scene`, `operator_probe_inputs`, `cross_installation`과 그 직접 소비를 추적해 수정할 fixture와 보존할 기대값을 표로 남긴다. `test_observation_delivery`의 단일 chunk와 `test_provider_raw_ingress`의 원 collector 반려를 포함한다. 읽기 탐색은 이 도우미들의 소비 및 명시 native final을 만드는 해당 시험 경계까지이며 무관한 전체 의미 감사를 다시 시작하지 않는다. `test_cross_required_events`의 설치 복구 두 사례와 `cross_research_machine`의 `recover_report` 호출도 읽되 후자의 전체 상태공간 실행은 배정하지 않는다.

### A2 외부 CLI 입력을 현 계약으로 교체하고 기존 의미를 보존

실제 worker가 전달한 schema에서 원 역할 schema와 전송 schema를 명시적으로 구분한다. 현재 제품의 한 전송 정의를 따르는 외부 CLI fixture를 사용하고, 기대 output·오류·관찰 바이트는 명시 값과 원 계약에서 얻는다. 제품 decoder를 다시 호출해 그 결과를 정답으로 삼지 않는다.

probe의 nonce·파일·checkpoint·정지·학술 도구명, repair의 정상/반려 output과 정확한 오류, native storage의 수치·공개 블록·저장/재읽기, 단일 chunk의 20개 관찰·한 번 전달 단언을 유지한다. 명시 stdout/final을 현재 봉투로 구성하되 기존 원자료를 자동 재작성하지 않는다. `test_provider_raw_ingress`는 오형태 행에 대한 collector의 구체적 반려를 확인하고, 그 실패가 final 형식의 다른 오류에 가려지지 않게 정상 final을 갖춘 대조 입력을 둔다. 원래 실패 status 하나만 보아 다른 오류를 같은 성공으로 세지 않는다.

같은 규칙은 기존 support helper의 한 위치에서 공유한다. 구 schema fixture를 살리기 위한 제품 fallback·기본값·null 보충이나 단언 약화는 허용하지 않는다. Claude와 연구 결박 경로의 입력/최종 응답 의미를 유지한다. 배정된 제품 runtime은 읽기 전용이다.

### A3 저장 pair가 실제 성공·결박·실패·정지 분기를 검사

`_runner_result_samples`가 각 공급자의 비결박 성공, 결박 수집, 불완전 수집, 정지를 실제로 대표하게 한다. 성공 표본은 현재 collector가 생산하는 요청·원바이트·결속 구조를 사용한다. ModelRunner/collector/분류기를 통째로 대체하거나 source_request 누락을 제품에서 허용하지 않는다. 실제 수집 경로와 기존 외부 CLI/Job 대역을 재사용하는 구체적 구성은 구현자가 정한다.

표본의 이름과 개수 외에 실제 status·output·collection/error_kind를 해당 분기의 계약과 대조한다. 예를 들어 비결박 성공의 실제 결과가 `output_validation`으로 바뀌면 저장 가능성 검사는 통과하더라도 분기 검사는 반드시 실패해야 한다. 이 반례를 새 단언으로 수리 전에 포착하고 원출력을 보존한다. 기존 stored artifact와 operator file 수신 검사는 계속 실제 생산 결과를 읽어야 하며, 필수·선택 필드 역방향 모집단 검사를 유지한다. 이는 `Pair.fields`가 선언한 수신 필드 전부가 생산 표본들의 `written` 합집합에 포함되는지 확인하는 기존 검사다.

### A4 수정된 경계와 직접 소비의 관련 회귀 완료

아래 검증 방법의 세 검사 묶음을 최종 시험 판본에서 수행한다. phase 006의 11개 실패가 모두 해소되고 성공 pair의 두 공급자 분기가 실제 completed로 검사돼야 한다. 추가로 확인된 chunk·설치 복구·오형태 반려도 기대한 성질로 통과해야 한다. 선택 ID, 실제 고유 row, 종료 코드, 소스 해시를 대응시키고 실패·미실행을 숨기지 않는다.

공유 fixture 변경의 영향은 직접 소비 시험에서 확인한다. 기존 Claude/control_binding/native final mismatch·worker hash·종료 barrier·원 schema 제약을 유지한다. 전체 일반 검사의 성공으로 확대하지 않는다. 쓰기 범위 밖의 제품 결함이나 입력이 새로 확인되면 재현 근거와 정확한 후속 범위를 findings에 반환하고 영향을 받는 A를 fail/not_run으로 남긴다.

### A5 기존 실호출·녹화의 재사용과 미러 인도 일치

phase 006 실호출 이후 제품 runtime 124개와 `support.provider_live`·smoke 입력 경계, 기존 corpus가 불변인지 실제 해시로 확인한다. runtime의 정확한 파일 목록은 필수 입력 `run:phases/006/manager-evidence/verification.json`의 `runtime_unchanged_since_live`에 있다. phase 006 Codex 실호출과 phase 003 Claude 한정 재사용의 조건을 보존한다. 코드/도구 조건을 확인하지 않은 새 호출 성공으로 표현하지 않는다. 해당 조건이 깨지면 원인을 보고하고 새 실호출 책임은 manager에 반환한다.

정본 수정 뒤 공식 생성 계획과 현재 dirty를 대조하고 허용된 대응 파일만 생성한다. 미러에서도 수정된 직접 소비·pair 및 corpus 검사를 실행한다. `.timings.json` 사본만 다시 맞춘 뒤 공식 `--check`와 `probe_cli.py --skill-only`를 통과한다. 양쪽 corpus 각 18항목·51파일의 바이트와 50개 명시 SHA 참조, 102개 경로 Git raw/clean을 유지한다. 제품 후보의 stage/commit은 manager 책임이다.

최종 report에는 A1~A5 결과, 변경 파일, 원실패와 새 성공, 검사 중 불변, 실호출 재사용의 범위, 미실행을 기록한다. 모든 A가 pass일 때만 complete다. G4~G8과 다른 문서·의미·실경계 의무는 이번 완료 판정에 포함하지 않는다.

## 판단과 경계

쓰기 권한은 phase.json의 시험 파일과 대응 미러·비용 캐시에 한정한다. helper의 표현과 작은 중복 제거는 재량이며 보존할 제품 의미·기존 단언은 완료 조건이 정한다. 미러는 공식 생성물이다. 실제 repository·runner·worker·adapter·collector·저장기를 시험 대역으로 바꾸지 않는다.

검사 묶음은 순차 실행하고 전체 worker 합계는 3 이하로 둔다. 아래 기본 명령은 `--jobs 1`이다. 검사 중 소스를 고정하고 시간은 소프트 기준으로 보고한다. 실행 중 result.json을 관찰할 때에는 `file_io.read_bytes_shared`를 사용한다. 유료 모델 호출, graphify 갱신, Git stage/commit/reset/checkout/push, 기존 연구 시작·재개·삭제, 실제 OS 예약 변경은 수행하지 않는다. 자체 격리 fixture의 파일/가짜 port 효과는 지정된 검사의 범위다.

제품과 시험의 불일치가 현 fixture 교체로 해결되지 않으면 부분 완료로 반환한다. 원실패 자료나 phase 006 report를 고치지 않으며 공용 계약·engine도 수정하지 않는다. 공용 완료 기준을 줄이거나 미해결을 허용 잔여사항으로 바꾸지 않는다.

## 검증 방법

cwd는 `C:\math`, Python은 `C:\Users\wogud\AppData\Local\Programs\Python\Python312\python.exe`다. 각 명령에 별도 새 evidence 출력 경로를 쓰고 실제 argv·시각·PID·stdout/stderr·exit와 소스 전후 해시를 남긴다. 도구의 yield는 프로세스 종료가 아니다.

1. A1 범위를 대조한 뒤 A3의 분기 단언이 현 공백을 포착하는 red를 정확한 시험 ID로 실행한다. 구 입력을 교체하고 동일 반례의 해소를 확인한다.
2. 직접 소비 묶음: `run_tests.py sim.test_operator_probe_contract sim.test_operator_finish_recovery sim.test_operator_finish_provider sim.test_operator_finish_cli sim.test_operator_finish_children sim.test_operator_finish_supervision sim.test_operator_supervision_contract sim.test_observation_delivery flows.test_provider_native_storage flows.test_provider_raw_ingress flows.test_operator_recovery_contract flows.test_scheduling_close_repair_exit flows.test_scheduling_close_remaining_exits boundary.test_provider_worker_roots contracts.test_pairs --jobs 1 --output <새 경로>`. 추가로 `flows.test_cross_required_events`에서 `test_installation_repair_unresolved_settles_and_does_not_repeat`와 `test_installation_repair_report_releases_one_successor`의 실제 클래스명을 확인해 두 정확한 ID를 실행한다.
3. 제품 경계 보존 묶음: `run_tests.py sim.test_provider_schema sim.test_provider_runner sim.test_provider_runner_gaps sim.test_provider_final_contract sim.test_provider_pinned_runner sim.test_provider_workers sim.test_provider_collection sim.test_provider_close_worker_rejections unit.test_provider_live unit.test_provider_cli_surface structure.test_test_smells structure.test_layers --jobs 1 --output <새 경로>`.
4. 정본 corpus 묶음: `run_tests.py structure.test_corpus unit.test_corpus_replay contracts.test_doubles_follow_corpus --jobs 1 --output <새 경로>`. 모든 명령에서 `run_tests.py`는 `& '<Python>' -u -B .claude/skills/do-math/scripts/run_tests.py`로 호출한다.
5. 공식 생성 후 미러의 `.agents/skills/do-math/scripts/run_tests.py`로 `sim.test_operator_probe_contract sim.test_operator_finish_recovery sim.test_observation_delivery flows.test_provider_native_storage contracts.test_pairs structure.test_corpus unit.test_corpus_replay contracts.test_doubles_follow_corpus`를 한 묶음으로 실행한다. 정본 대비 생성 변화·검사 결과·corpus 불변을 확인한다. 이어 같은 Python으로 `.claude/skills/writing-skills/scripts/build_skill_mirrors.py --check`와 `.claude/skills/do-math/scripts/probe_cli.py --skill-only`를 실행한다.
6. report를 쓰고 `& '<Python>' -B services/continuous-development/check.py report 'C:\math' 'C:\math\docs\do-math\continuous-development-2026-10-13' 007 provider-consumers`를 통과한다. 마지막 응답에는 complete/partial/blocked 상태와 report 경로를 알리고 종료한다. 다음 phase의 판단·기동은 manager와 실행기가 맡는다.

# 026 policy-semantics의 한정 판정

조사 완료이며 제품 합격이나 새 시험 통과 보고가 아니다. 제품·문서·시험·미러·공용 파일은 수정하지 않았다. 025 검수판과 시작 2,675 소스를 먼저 해시로 대조했다. 판정의 정본은 policy-decisions.json이며 원문 좌표/해시/전문 구간은 population.json과 source-excerpts.json, 정확한 기존 시험 ID·단언 위치는 test-bindings.json, 실제 원보고의 행과 판본 비교는 historical-execution.json에 있다.

모집단은 024가 기록한 이름 8회와 같은 절의 실행 예제 4회, 총 이름/행 쌍 12개다. 고유 원문 행은 8개이며 이름은 5개다. 001 binding-inventory의 정책 모집단과 024 historical occurrence가 같다. N01-020/218/230/268/273 가운데 해당 문장·예제만 판정했다. CLI의 model_policy 실패 행은 역사 991→현재 993이며 초기화-운전 문서의 전체 해시는 025 trust 설명 변경 때문에 024와 다르지만 해당 문장은 같다. 시작판은 025 source-inspected와 차이가 없으므로 그 변경을 정책 의미 변화로 오인하지 않는다.

| 이름 | 후속 처분 | 이유 |
|---|---|---|
| conversation_loss_policy | 유지 후보 | 현행 instance 정책이 대화 소실/dispatch/resume를 결정한다. continue_authorized는 대화 연결 의존만 제거하며 연구 grant, 사용자 정지, 감독 HOLD를 해제하지 않는다. pause도 초기화 관문을 통과할 수 있다. |
| disconnect_policy | 문장 유지·시험 보강 | 명시 attach와 생략은 코드상 양쪽 정책을 동일하게 저장한다. 기존 시험은 생략 후 live/resume와 explicit pause의 instance 저장을 관측하지만 연결 행의 선택 정책까지 독립 기대·restart 후 일치로 직접 단언하지 않는다. |
| model_policy | 두 의미를 구분해 유지 후보 | MODELS/ROLE_TIERS/LIMITS의 기본값 모듈과 lock 위반 error_kind를 구별한다. 실제 설정은 tier_models/role_tiers/session_limits/claude_only_assigned_model이다. 다른 reported 모델의 반려는 잠금 true 조건에서만 적용되고 reported 모델 부재는 그 반례가 아니다. |
| external_policy | 유지 후보 | explicit_grants는 현재 효과별 HTTP grant 검사의 상위 조건이다. disabled는 준비/dispatch를 막으며 승인 자체·송신·성공을 만들지 않는다. grant 범위/시각/철회는 송신 직전까지 다시 검사한다. |
| adopt_default_review_policy | 문구 교정·시험 보강 | 이미 채택한 객체를 읽는 플래그가 아니라 현재 설정으로 기본 객체를 생성·채택하고 실제 해시를 저장하는 동작이다. 사전 채택이 없는 initialize_state도 이 경로를 사용한다. |

기본 검토 방침의 최소 소스 반례는 현재 initializing 인스턴스에 review_policy가 없는 상태에서 `{kind:'initialization', operation:'adopt', config_sha256:현재해시, adopt_default_review_policy:true}`를 적용하는 분기다. 원문 182의 “이미 채택한 … 결박”으로 사전 정책 객체가 필요하거나 이전 기본 정책을 재사용한다고 읽히면 실제 initialization_engine 100~106과 다르다. 현재 코드의 기대는 설정 reviewers/review_rounds로 기본 정책을 만들고 그 실제 해시를 저장하는 것이다. 이 task는 이 입력을 실행하지 않았다. 제품 반례로 등급을 올리지 않고 문구 해석의 교정 후보로 반환한다. 명시 review_policy를 함께 보낼 때에는 그 객체를 채택한다는 예외도 유지한다.

통합 work에서는 초기화-운전.md182의 해당 문장과 공식 미러를 고치고 InitialAdoptionTests의 해당 동작을 직접 검사한다. reviewers=3/review_rounds=2, 기존 정책 absent 또는 다른 객체라는 최소 입력에서 minimum_initial_slots=3, round_limit=2, activity_execution_limit=17, 세 judge, 빈 required_perspectives, overflow=unresolved라는 독립 기대를 둔다. 제품 build_review_policy를 두 번 호출하여 기대를 만드는 검사로 대신하지 않는다. hash는 실제 저장된 객체의 canonical hash와 비교하고 기존 stale config 반려/정책 hash 불일치 활성화 missing 단언을 보존한다. 코드의 동작이나 사용자 권한을 바꾸지 않는다.

attach의 보강은 기존 PublicLifecycleTests의 생략/세대 시험에 둔다. instance continue_authorized→명시 pause attach→generation 증가·정책 생략→필요하면 반대 방향 continue_authorized를 공개 경로로 적용하고, 매 단계의 instance 정책과 연결 행의 disconnect_policy, generation/source_ref 및 restart 후 원장 복원을 독립 기대와 비교한다. 기존 heartbeat 전달 시점·정확 만료 경계·동세대 반려·명시 resume 필요·원문 재전달의 원자성 단언을 삭제하지 않는다. 현재 소스는 이미 문장대로 구현하므로 단언을 추가하기 위해 runtime 분기를 만드는 작업은 필요하지 않다.

30개의 정확한 기존 test ID를 확인했고 원보고에는 이 ID에 해당하는 31행이 있다(한 ID의 다른 보고 행을 포함). 이 행들의 passed는 과거 실행 사실이다. B129 자체는 complete=true/successful=false이며 전체 실패/skip을 지우지 않는다. B129 대비 model_call과 support/model, provider_runs, engine_context, operator_finish_scene, port_contracts/jobs 등이 다르다. 특히 현재 HOLD 시험 본문도 B129와 다르므로 그 옛 row로 현재 HOLD 시험을 실행했다고 말하지 않는다. 현재 HOLD의 판단은 scheduled_operator/supervision와 현 시험 본문 대조이며 새 실행은 미관측이다. 007의 모델 잠금 worker 시험과 018의 공개 CLI 저장 시험을 정확 row로 추가 확인했지만 그 뒤 support 변화가 있으므로 whole-edition green은 아니다. 025 보고의 원문/판본 대조도 그 보고에 실제 선택된 ID만 증명한다. 이 task의 소스 조사와 과거 실행 근거를 결합해 현재 배정의 한정 의미를 판단하며 후속 통합/최종 판본에서 실행 근거를 교체한다.

PR24/B57은 cd2f7fe4의 실제 diff와 현 doc_code의 정책 검사 세 함수, 현 DocumentCodeTests의 정확 단언을 대조했다. 세 함수 본문이 그대로이며 미정의 이름 반려/실제 소유 존재 검사는 유지한다. 전역 vocabulary green을 문장의 정책 의미 인증으로 사용하지 않는다. B57의 Temp 원보고 세 selector(두 고유 파일)와 B64의 두 selector(한 파일)는 현재 없다. 그 역사 12/6 counts를 새 성공에 넣지 않는다. B64의 실제 CLI diff에는 이번 다섯 정책의 의미를 변경한 hunk가 없으므로 다른 대기/복구/학술 hunk의 검토 완료를 선언하지 않는다. 해당 slice만 판단했으며 PR24/B57/B64 전체나 G2 전체가 끝난 것이 아니다.

제품 실행·공식 run_tests·미러 생성·유료/OS/Lean/예약/학술 호출·연구 조작·Git index 변경·graphify 갱신은 없다. Python -B는 자기 evidence의 JSON/소스/해시와 읽기 전용 Git 원바이트만 다뤘고 제품 모듈은 import하지 않았다. 다른 두 task의 결과를 읽거나 기다리지 않았다. 남은 N01 이름, L01 Q1/Q2와 원문 UTF-8 byte 요구/미충족, Windows symlink 1314 미검사, G4 기본 전체/G5 fresh T3/G6 전수 변이/G7 최종 판본/G8 review는 그대로다. source-end.json과 verification.json은 제출 직전의 전건 불변을 확인한다.

# 목적과 완료할 결과

원문10-A의 역할 입력·저장·작업자 도구 출력 크기 질문 R21/R22를 같은 실제 생산·포장·저장·읽기 경로에서 판단한다. 필수 자료를 버려 상한을 맞추지 않고, 선언된 규모·상수·바이트 상한이 현재 계약의 내용 보존과 함께 검사되는지 확인한다. 가까운 시험/helper와 허용된 runtime 결함의 수리·미러·필요한 최소 확인은 한 task에서 마친다. 이미 충분한 성질은 재사용하며 세 시험 모듈마다 별도 후속을 만들지 않는다.

## 입력과 현재 위치

SESSION_JSON의 workspace, 고정 inputs/context.md·plan.md·seams.md 및 task.json을 먼저 읽는다. C:/math/docs/do-math/continuous-development-2026-10-13의 sources/user-decisions.md·requirements-index.json·model-policy-2026-10-14.md·document-batching-2026-10-14.md가 사용자 원자료다. phases/001/tasks/closure-map/evidence의 tracking-state R21/R22, requirement-state 10-A, evidence-catalog current_work.engine_population_integration 및 prior-review-state PR17 중 직접 겹치는 입력 보존 slice만 읽는다. 원문 규모는 C:/math/docs/do-math/시험-재편-2026-09-29/조사/결함-범주.md의10-A와 단계-전환표-2026-10-03.json의10-A/engine_population_integration에서 확인한다. 큰 JSON 전문을 출력하지 않고 해당 행·원보고·실제 hunk를 읽으며 부재 보고의 숫자를 성공으로 합산하지 않는다.

repo:는 자기 workspace, 과거 run:은 위 continuous-development 루트다. C:/math/docs와 C:/math/.async/dm의 원자료·다른 task 기록은 읽기 전용이다. managers/0016/review.md가 이번 배정 이유다. 기존 R17은 구현 검토 완료·최종 판본 연결 대기여서 재감사하지 않는다. r06은 null 소비, r23-r24는10-B 호출 계수/idle, r14-fix는 관찰 진행성을 맡는다. 이들의 중간 workspace를 소비하거나 수정하지 않는다. r12-r13-fix는 위임 공개 원결정을 맡고 아직 선행 대기다. 독립 쓰기이므로 이 작업의 depends_on은 비어 있다.

## 종료할 질문

1. tests/support/engine_size_cases.py의 role_cases/VARIANTS, scale_state/scale_context/stored_scale_sim과 tests/unit/test_engine_role_input_scale.py를 실제 contracts.ROLES, context_store.input_scope/role_direct_keys/prepare_role_input 및 현재 역할 필수 입력 계약에 대응한다. 역할×대표 상태, 프로필37, 과제100×이력10의 범위를 보존한다. 표의 존재와 합성 포장 성공을 실제 엔진 생산 증거와 구별한다. 이미 역할 생산·봉인·읽기를 확인한 PR17 및 role_input_requirements의 직접 성질은 재사용하고 모든 역할 의미를 새로 감사하지 않는다. 현재 분기 차이 때문에 빠진 대표 입력이나 필수 자료 누락을 놓치는 단언이 있으면 같은 시험에서 보완한다.
2. 기본 max_input_bytes와 필수 문맥 예산, 실제 UTF-8 바이트·prompt/manifest SHA·source_ref의 정확 원값·검증 문맥을 함께 판단한다. 작은 요약을 되돌려 읽는 성공만으로 전체 원문 보존을 주장하지 않는다. 과제/프로필 원문, 선택/대조 모집단, 이력, private scope와 validation_context의 서로 다른 책임을 유지한다. 상한이나 기본값을 키우거나 필수 목록을 줄여 성공시키지 않는다. overflow의 정상 계약을 깨는 개선도 하지 않는다.
3. flows/test_engine_stored_input_scale.py의 실제 저장/restart/공개 input_tool 읽기에서100×10·현재37프로필, 대형 manifest의 한 벌 보존,56230항목 toolchain record의 참조 등록/재전달을 확인한다. 합성 파일 관찰값은 실제56230파일 설치·활성화가 아니다. 원문 저장 레코드 가족의 상수배 질문을 실제 생산/저장 경로와 기존 record/storage 시험의 해당 단언에 연결한다. 다른 객체 가족을 한 manifest 시험으로 전건 충족 처리하지 않는다. 기존 unit/test_record_family_storage.py와 test_producer_record_storage.py는 r06 소유라 읽기 전용이며 필요한 크기 단언은 자기 직접 시험/필요시 unit/test_engine_storage_scale.py에 묶는다. 원문에서 요구하지 않은 모든 레코드에 동일5MB payload를 넣는 요구를 만들지 않는다.
4. flows/test_engine_recorded_lean_scale.py와 support/engine_lean_recording.py의 실제 녹화5선언·603폐포·약5MB 원바이트/SHA를 actual verifier→실제worker→저장→검토/감사 입력과 공개 formal_preview/input_tool 출력에 연결한다. 외부 compiler 대역의 녹화 재생과 실제 Lean 재실행을 구별한다. 사전 검사 출력이 상한 이하의 JSON 하나이고 원출력은 파일로 온전히 회수되는지, 저장의 선언 상수와 중복 인라인 방지가 실제 바이트/내용 단언인지 판단한다.1MB/4096바이트 등 기존 경계와 녹화 원문을 임의로 줄이지 않는다. corpus는 읽기 전용이고 새 실Lean/모델 호출은 필요 없다.
5. 실제 현재 정의·입력축·정확 단언·원보고 판본으로 충분/수리/미확인을 연결한다. PR17 B66~B69 중 크기/필수 보존에 직접 필요한 hunk·소비자만 확인하며 R31~R33 전체를 추가 배정으로 해석하지 않는다. 알려진 구조 unpinned_rejection 중 실제 수정하는 가까운 단언은 함께 고치되 별도 전수 구조 감사로 확대하지 않는다.

## 수정 범위와 독립성

task.json writes가 권한 정본이다. 직접 크기 시험3개·필요시 engine_storage_scale, engine_size_cases/engine_tool_output helper와 미러가 기본 범위다. 재현된 해당 크기·원문 보존 결함에 한해 context_store.py/input_tool.py/formal_preview.py/formal.py/knowledge_records.py의 직접 경로를 수리할 수 있다. 해당 소비 회귀를 함께 확인한다. 이 허용은 전면 재설계나 문서에 없는 새 API 도입 배정이 아니다.

core/scheduler/parallel/model_runner·관찰·위임·contracts/record schema, repository/git_store/trust_inventory/lifecycle/setup_lean, 공유 Sim/record_builders/role_input_requirements/engine_lifecycle 및 다른 task 시험은 읽기 전용이다. 공용 정본 설명도 r12-r13-fix와 중복 쓰기를 피하려고 읽기 전용이다. 기존 계약 자체의 변경이나 범위 밖 생산자 수정이 필요하면 정확 입력·관측·영향·필요 파일을 보고한다. 자기 범위 안 유효한 결과는 마치며 다른 task 결과를 기다리지 않는다. 변동 중인 읽기 소비 runtime의 직접 심볼/시작 SHA를 남겨 manager가 이후 통합의 영향을 대조하게 한다.

## 최소 확인과 제출

현재 코드·단언·판본이 맞는 기존 원보고로 충분하면 새 실행을 하지 않는다. 새 수리/새 입력에만 자기 workspace의 공식 scripts/run_tests.py jobs1로 가장 작은 관련 ID를 실행한다. 필요한 원문 규모는 그대로 두고 불필요한 전수 반복을 줄인다. 실패를 먼저 읽고 제품/fixture/환경 오류를 구별해 수리한 뒤 해당 ID만 확인한다. 소프트 시간 기준 초과를 입력·단언 축소나 timeout 성공으로 바꾸지 않는다. 제품 메서드 대역은 새로 만들지 않으며 실제 기능을 유지하고 외부 경계의 기존 fixture를 쓴다.

소스 고정·선택/실제row·exit·SHA·최초 실패·fixture 오류·재사용 한계를 evidence에 보존한다. 서로 다른 판본의 통과를 단일 최종판 전체 성공으로 합산하지 않는다. 공식 build_skill_mirrors.py --target .agents와 --check --target .agents, 변경쌍 바이트를 확인한다. 비용 캐시2개는 evidence 보존 뒤 자기 base로 복원한다. report는 실제 변경 전부와 원문/현재 연결/정확 남김을 담고 check.py report C:/math/.async/dm r21-r22 PASS를 확인한다.

공용소스·context/plan/seams/queue/state·engine·다른 task·원자료·Git index는 수정하지 않는다. graphify 갱신·외부 예약·새 모델/Lean 실호출·전체 일반/T3/변이/T4/T5는 이 배정이 아니다. R21/R22의 해당 의미 질문과 최종 통합판 증거 대기를 구별하고 전체10-A/PR/K/P2 및 G4~G8·L01·Windows1314의 별도 남김을 숨기지 않는다.

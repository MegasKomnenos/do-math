# 템플릿 복원과 공개 활성화가 시험의 보호 성질을 보존하게 한다

빠른 시작 상태를 재사용해도 실제 활성화·저장·종결 결함을 가리지 않아야 한다. 같은 support/sim.py를 사용하는 KEEP-TEMPLATES와 KEEP-PUBLIC-PATH의 K-15~21·K-23·K-25·K-33~35를 한 작업으로 묶는다. 현재 충분한 성질은 재사용하고 확인된 공백은 helper·직접 시험·해당 설명·미러와 필요한 최소 확인까지 이 task에서 마친다. 전체 템플릿 소비자 전수 재실행이나 새 캐시 체계가 목표가 아니다.

SESSION_JSON과 task.json, inputs/context.md·plan.md·seams.md, do-math AGENTS.md·시험-지침.md를 읽는다. C:/math/docs/do-math/continuous-development-2026-10-13의 sources/user-decisions.md·requirements-index.json과 phases/001/tasks/closure-map/evidence/tracking-state.json의 위 두 KEEP 항목, requirement-state.json의 지정 12개 K 원문을 읽는다. C:/math/docs/do-math/시험-재편-2026-09-29/조사/대역-사각지대.md·단계-전환표의 지정 preservation과 현재 migration/dispositions/kernel.knowledge.json을 대조한다. 역사 PurposeHarness/purpose_state/solved_instance/_no_formal_check 이름을 현행 Sim·_Template·engine_purpose로 의미 대응하며 폐기 API를 복원하지 않는다. 실제 관련 이전 변경은 prior-review-state.json에서 해당 경로·성질로 좁혀 원 diff·현재 caller·원보고를 함께 읽는다. 표의 과거 actual_test_ids는 실제 단언을 대신하지 않는다.

## 판정할 유한 질문

1. K-15/16/19/20: _Template.__init__/restore와 Sim.process_state/restored가 같은 절대 live 경로·독립 사본·shared trust의 원 bytes/stat을 보존하는가. 한 사본 사용 뒤 다음 복원이라는 계약, 새 engine과 clock/Jobs/Git 대역 상태의 복원, 앞 사본의 가변값이 뒤 사본으로 새지 않는 성질을 실제 생산·저장·복원과 연결한다. 역사 '디스크 bytes만'과 현재 대역 process_state 복원은 구별하고, 연구의 실제 프로세스 상태를 메모리 사본으로 대신해 버린 곳이 있는지 이 경계에서 판단한다. 프로세스 안 재사용과 T3 측정 귀속을 디스크 영구 캐시로 확대하지 않는다. 시계/임대 실제 경과 질문은 기존 공개 시간 시험을 재사용하고 새로운 장시간 대기를 만들지 않는다.
2. K-17/18/21: template_inputs/warm_built의 JSON 정규화·명시/생략 기본값·builder 정체성·키별 실패 고정과 assert_template_quiescent의 ended executions/예약 반환/Jobs 종료/Calls 회수를 확인한다. 기존 pending queue·질문·대기가 허용되는 조건과 미정산 실행을 구별한다. 공유 quiescence 정의를 복제하지 않는다. 잘못된 입력·같은 실패키 재요청과 다른키의 독립 진행은 정확 사유/원값을 확인한다. 설정을 빌드 키 밖에서 바꿔 서로 다른 시작 상태를 같게 재사용하지 않는다.
3. K-23/25/33/34/35: Sim.activate/_apply/_check_applied와 engine_purpose.purpose_sim/drive의 공개 제어·초기화 승인·active 도달, 예상 밖 formal verifier/worker 호출 발견, 거부/조기 종료의 정확 설명을 현행 직접 시험과 연결한다. Sim.control은 제어를 게시하는 공개 수송 API이고 _apply/activate는 적용 결과를 확인하는 helper다. 모든 raw control에 즉시 성공 단언을 강요해 의도한 음성 시험을 깨지 않는다. 목표까지 필요한 시험은 목표 결말·후속 대역 단언을 보존하고, 값이 이미 확정된 경우만 일찍 멈춘다. 45 owner pass 같은 유한 시나리오 상한을 시간 강제종료와 혼동하지 않는다.

각 K ID를 실제 정의·정확 시험 메서드·단언·사용한 원보고/판본·충족 또는 구체적 남김으로 연결한다. support/sim.py의 현행 _Template/Sim, sim.test_template, unit.test_template_inputs, flows.test_activation, engine_purpose의 실제 소비자에서 출발한다. 같은 helper의 필요한 수리는 묶고 명명/목록 존재만으로 행동을 인증하지 않는다. 실제 저장이나 엔진이 검사 대상인 시험에서 그 경로를 원하는 값의 대역으로 지우지 않는다.

## 범위·검증·인계

쓰기 범위는 task.json의 sim/engine_purpose/cross_states helper와 지정 직접 시험·미러다. runtime engine/core/lifecycle/knowledge, branch_gate와 공개 schemas는 읽기 전용이다. 현재성의 r44-fix·기동의 r49-startup, 격리의 keep-isolation 사본을 소비하지 않는다. 시험 지침·공용 이음새는 다른 task가 소유하므로 관련 설명은 수정하는 helper/시험의 docstring에 반영하고 공용 설명에 필요한 변경은 보고로 인계한다. 새 helper나 직접 시험은 지정된 경로 안에서만 추가한다.

충분한 기존 근거는 정적 대조로 마친다. 실행이 필요하면 공식 run_tests.py --jobs 1로 변경 성질과 직접 소비자를 확인하는 최소 ID만 실행한다. 전체 일반/T3/변이/T4/T5·실 공급자/Lean/예약 호출은 하지 않는다. 실제 대상 경로와 외부 대역 경계를 밝히고 selected/실제 row·fixture/최초 실패·exit·소스 SHA·실행중 변경·소프트 초과를 보존한다. 이미 충분한 동일 판본 시험을 반복하지 않는다. 비용 캐시는 관측 bytes를 evidence에 보존한 뒤 own base로 복원한다. 공식 미러 생성/check를 하고 report.json을 check.py report C:/math/.async/dm keep-templates PASS로 제출한다. 지정 12개 보존 질문의 판정과 G2/G3·최종 관문 전체 완료를 구별한다. 공용 소스/문서/queue/state·engine·Git index·graphify·기존 연구 운전은 수정하지 않는다.

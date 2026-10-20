# 역할 입력과 대본 모델 제출의 보존 성질

시험의 대본 모델이 실제로 받은 자료만 읽고 답하며, 정상·반려 출력 모두 실제 봉인·제출·중앙 영수증 경로를 사용하게 한다. KEEP-ROLE-INPUT의 K-29/30/31/48과 KEEP-MODEL-SUBMIT의 K-27/32/46/49, 총8개의 유한 보존 질문을 현재 helper·직접 소비 시험에서 판정하고 필요한 수정·최소 확인·미러를 한 task에서 마친다. 과거 클래스 이름을 복원하거나 이미 충분한 근거를 다시 실행하는 작업이 아니다.

SESSION_JSON/task.json과 inputs/context.md·plan.md·seams.md, do-math AGENTS.md·시험-지침.md를 읽는다. 원자료 루트는 C:/math/docs/do-math/continuous-development-2026-10-13이며 sources/user-decisions.md·model-policy-2026-10-14.md·document-batching-2026-10-14.md·requirements-index.json, phases/001/tasks/closure-map/evidence/tracking-state.json의 위 두 묶음과 requirement-state.json의8개 K를 읽는다. C:/math/docs/do-math/시험-재편-2026-09-29/조사/대역-사각지대.md와 단계-전환표-2026-10-03.json의 같은 ID가 원래 보호 성질이다. 제품 tests/migration/dispositions/kernel.knowledge.json의 위치는 탐색 출발점이며 현재 원문과 단언으로 확인한다.

keep-templates 수용 뒤 시작한다. 두 작업이 support/engine_purpose.py와 unit/test_engine_purpose_responder.py·sim/test_engine_purpose_goal_audit.py를 공유하므로 그 수용된 변경을 보존하기 위한 실제 선행이다. keep-templates/report.json과 evidence의 직접 근거를 읽고 관련 심볼만 다시 대조한다. r31-r33/r31-fix의 실제 지급source·봉인/반려 수리, r34-r36의 필수입력/프로필, r02-fix/r04/r09의 요청·결과·제출 연결은 수용된 범위에서 재사용한다. 다른 task의 미완성 사본은 소비하지 않는다.

## 판정할 질문

1. K-29/30/31: support.role_answers.read_fixture_context가 실제 context_store.read_source의 ok/잘림 없음/원bytes와 JSON pointer를 소비하고 supplied task의 results/reviews/history를 제대로 읽는지 확인한다. 누락 자료·내용/길이 불일치와 정상 원값을 같은 입력 owner에서 구별한다. seal_response는 fixed tasks/knowledge_catalog의 content_sha256 없이 record mutation을 봉인하지 않아야 한다. bind_candidates도 지급 profile/grant 밖의 허가를 만들면 안 된다. contract_review의 구조화 scope/obligation, assessment의 실제 nonempty report, planning_model_assessments의 공급된 선택 task 평가, intent_response의 원문 전체, scope_response의 명시 관점이라는 각 보호 성질을 현재 responder와 연결한다. 모든 역할 전체 재실행이나 옛 fixture 모양 복원을 요구하지 않는다.
2. K-27/49: support.model.ModelDouble.output/render와 FakeCLI._submit/finish, default_responder.context_from 및 실제 workspace submission_tool/worker/central receipt가 제공하는 현재 연결을 확인한다. 정상 answer는 candidate binding→integration seal→실제 수신 schema 검사→제출/정확 terminal receipt를 거친다. 현재 모델 대역은 자체 schema validate를 하지 않으며 엔진 수신자가 검사한다. 검사 위치를 옛 문구에 맞추어 중복하거나 수신 검사를 대역으로 바꾸지 않는다. bound/standalone·sealed/raw·expected_receipt/returncode의 명시 계약과 동시 call별 Answer 보존을 확인하고, 의도한 음성 입력이 반려되면 성공인 시험과 정상 입력의 unexpected receipt를 구별한다. 수송 결속 누락/잘못된 영수증을 조용히 성공으로 처리하는 공백이 있으면 직접 helper/시험에서 고친다.
3. K-32: PurposeResponder.respond와 PurposeAnswers.answer가 repair가 달린 입력, 형식 효력 전 goal audit, 유효한 최종 동일성 평가가 아닌 근거, 예상 밖 role/non-live 운영 점검을 어떻게 거부하는지 각각 실제 소비·단언으로 연결한다. 실패가 responder.failures→drive로 전달돼 제품의 기술실패 처리에 가려지지 않는지 확인한다. keep-templates의 활성화/종결/drive 검증은 재사용하고, 이 task는 실제 입력의 의미 검사만 보완한다. 유효한 goal/형식/검토 producer를 쓰고 현재성 계약에 어긋난 인공 준비 오류를 제품 실패로 세지 않는다.
4. K-46/48: 현재 Overlap/ParallelWorkTests의 실제 동시 진입·owner 순차 적용·서로 다른 workspace, InvestigationRunner의 source SHA와 task 계약 비상속, RejectingResponder와 quota 대역의 실제 원 worker/제출/receipt 전달을 연결한다. 폐기120초 timeout을 복원하지 않고 현재 유한 owner-turn/명시 동시성 단언을 판정한다. cli_inputs.role_reach는 실제 고정 snapshot에 secret이 존재하는 held와 prompt/workspace/실제 자식 read-tool 경로의 reached를 함께 소비해야 한다. held가 빈 음성 결과를 기밀 격리 성공으로 해석하지 않는다. 실제 read subprocess와 합성 모델/호출 포트를 구별하며 기존 reach 근거가 충분하면 새 native 실행을 하지 않는다.

각 K ID에 실제 정의·정확 시험 메서드/단언·원보고/소스 판본·충족/필요 수리/구체적 남김을 연결한다. 기존 보고의 전체 실패와 지정 passed row를 구별하고 부재한 Temp 보고를 성공으로 추정하지 않는다. 과거 모델/producer 이름과 현행 경계를 대응하되 구판 호환 wrapper나 새로운 대본 runner를 추가하지 않는다.

## 범위와 검증

task.json의 role_answers/model/default_responder/engine_purpose/purpose_answers와 연결된 입력·연구·동시성·대역 helper, 지정 직접 시험·미러가 쓰기 범위다. runtime core/lifecycle/knowledge/submission/worker 및 support/sim.py, runner/WindowsJob, 공유 시험 지침·이음새 문서는 읽기 전용이다. r49-startup의 시간/기동, keep-isolation의 격리 소유 코드를 덮지 않는다. 현재 runtime 결함 또는 범위 밖 helper 수정이 필요하면 정확 입력·심볼·영향을 보고한다. 의미 없는 명칭 정리와 무관한 helper 재설계를 추가하지 않는다. 필요한 설명은 수정한 helper/시험의 docstring에 두고 공용 설명은 보고로 인계한다.

충분한 기존 성질은 코드/기존 원보고 대조로 끝낸다. 실행이 필요한 변경만 workspace의 공식 run_tests.py --jobs 1에서 가장 작은 직접 선택으로 확인한다. 실제 제품 경로와 외부 대역을 밝히고 selected/고유 실제row·exit·판본SHA·fixture/초기실패·실행중변경·소프트초과를 남긴다. 서로 다른 판본을 하나의 성공으로 합산하지 않는다. 전체 일반/T3/변이/T4/T5·실 공급자/Lean/HTTP/OS예약 호출은 하지 않는다. 비용캐시는 관측 bytes를 evidence에 보존한 뒤 own base로 복원하고 공식 미러 build/check를 한다.

report.json은8개 보존 질문의 실제 결과와 재사용·한계를 설명한다. 전체G2/G3·다른 K/P2·G4~G8·L01/Windows1314 완료를 주장하지 않는다. check.py report C:/math/.async/dm keep-inputs PASS로 제출한다. 공용소스/공용문서·queue/state·다른 task·engine/Git index·graphify·기존 연구 운전은 수정하지 않는다.

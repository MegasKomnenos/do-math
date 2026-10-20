# R06: import 반려 저장 결함과 남은 domain null 관계 마무리

현재 null 생산/소비를 사용 가능한 상태로 마친다. r06-domain의 F1 수리와 domain M4의 한정 남김을 한 작업에 묶는다. r06-domain/r06-edges 및 r12-r13-fix 수용판이 선행이다. 실행 중 배정을 바꾸거나 다른 workspace의 중간 결과를 가져오지 않는다.

SESSION_JSON의 workspace·task.json·inputs/context.md/plan.md/seams.md를 먼저 읽는다. C:/math/docs/do-math/continuous-development-2026-10-13/sources의 user-decisions.md/model-policy-2026-10-14.md/document-batching-2026-10-14.md와 requirements-index.json이 원 사용자 요구다. 원문 결함-범주.md의1-D와 tracking-state R06/requirement-state 해당 행을 읽는다. 과거 run:은 continuous-development 루트이며 C:/math/docs와 다른 task 기록은 읽기 전용이다.

## 실제 남김과 완료 결과

1. tasks/r06-domain/report.json·evidence/relations.md 29·remaining.json.F1·verification.json 및 managers/0020/review.md/source-review.json을 읽는다. 현재 prepare_import의 checking/check 없음 상태에 premature import_approval을 보내면 domain은 정확 사유로 반려하지만 _queue_intent_rework가 intent_repair.check_execution_id=null을 생산해 저장할 수 없다. 제출된 sim.test_null_domain_consumers.ImportNullTests.test_unchecked_import_rejection_does_not_enqueue_a_null_check_execution는1error인 올바른 회귀다. r12-r13-fix 후 현재 코드에서 여전히 성립하는지 먼저 확인하고 해당 생산/전이 결함을 고친다. 검사 전 잘못된 승인에 재해석이 필요한지부터 판단해 불필요한 routing을 없앨 수 있다. 실제 검사 기초가 필요한 정상 rework를 유지하고 가짜 check ID·schema nullable 완화·예방적 None 정규화를 하지 않는다.
2. 같은 _queue_intent_rework의 source-changed-before-check, 검사가 있는 rejected/unresolved 및 답변 후 재해석 caller를 현재 정의로 함께 판단한다. 새 null 필드가 없어졌다는 단언만으로 끝내지 말고 반려 뒤 publishable state와 정확 반려/재전달·정상 후속을 유지한다. 기존 실패 회귀를 통과시키고 필요한 경우 가장 작은 공개 control→owner 게시→load/restart 확인을 더한다. 실제 공개 문법/fixture는 현재 수용판을 사용한다. 직접 내부 호출 성공을 공개 CLI 전체 성공으로 적지 않는다.
3. remaining.json.domain_M4_alias_sites의117행을 중복/false positive·실제 object 관계별로 합친다. 원문은 실제 생산 필드 null과 모든 실제 소비의 의미를 묻는다. None 반환/지역값·키 부재·len/hash 결과·non-null container를 nullable 필드로 만들거나 모든 Python alias의 무한 전수 감사를 새 조건으로 삼지 않는다. core._enqueue/_context/_planning_history/_resume_input_overflow_action, context_store.restore_continuation/prepare_role_input, review recovery/history와 lifecycle/retention의 남은 실제 관계를 생산 조건→최종 사용으로 끝낸다. 진단 JSON/source catalog로 전달되어 끝나는 값은 그 사실로 정적 종료할 수 있다. 이미 설명된1~28 관계는 새 반례 없이 다시 실행하지 않는다.
4. r06-edges E01~E14, 수용된 r06/r04/r05/r03-fix slice를 재사용해 원래 R06의 충족/정확 남김을 정리한다. snapshot provider_waits=null은 live guard 입력 의무가 아니고 deadline_only followup은 부재다. 전건 새 실행이나 별도 null registry를 만들지 않는다. 런타임 수정과 가까운 단언·필요 확인을 이 task 안에서 끝낸다.

## 수정 경계

task.json writes만 수정한다. 주 수리는 governance_engine.py이고 필요하면 지정 core/context/lifecycle/retention/계획 전달 파일의 실제 확인 결함을 함께 고친다. 전용 unit/sim null 시험과 governance rework/반려 시험에 묶는다. review_engine/review_cycle/governance/delegations/record_schemas와 repository/payloads는 동시에 시작 가능한 r22-snapshots의 소유로 읽기 전용이다. 이들 alias는 현재 시작판으로 판단하고 정확 심볼을 남긴다. 저장 task가 해당 표현을 바꾸면 그 소비를 같이 고치는 책임을 갖는다. r15-r16의 scheduler/parallel/call/formal 정산과 corpus도 읽기 전용이다. 새 실제 결함이 쓰기 밖에 있으면 정확 입력/소비/필요 파일을 보고하되 나머지 결과를 마친다.

r12-r13-fix의 공개 원결정·동일 봉인 입력의 독립 판단과 기존 제어/관찰 수리를 보존한다. 구판 호환·기본값 보충을 추가하지 않는다. 공통 fixture는 기존 것을 읽기 전용 사용하고 필요한 직접 helper 변경은 허용 목록 안에서만 한다.

## 최소 확인과 제출

AGENTS.md와 scripts/tests/시험-지침.md를 따른다. 정적으로 충분한 관계는 실행하지 않는다. 변경/실제 불확실성에 필요한 최소 ID만 공식 run_tests.py jobs1로 실행한다. 최초 실패·fixture 오류·선택/실제row·관측exit·SHA·실행중변경·소프트초과를 보존한다. 다른 판본 counts를 합산하지 않는다. 공식 build_skill_mirrors.py --target .agents 및 --check --target .agents 완료 뒤 변경쌍 bytes를 확인하고 미러 시험은 반복하지 않는다. 비용 캐시는 evidence 보존 후 자기 base로 복원한다.

report.json은 F1과 R06의 남은 관계가 어떤 상태인지 설명한다. check.py report C:/math/.async/dm r06-finish PASS를 확인한다. 전체일반/fresh T3/변이/T4/T5·새 외부 실호출·graphify·예약·공용소스/문서/queue/state·Git index·다른 task 수정은 하지 않는다. G4~G8·B58 한정처분과 Temp 부재·L01·Windows1314의 별도 남김은 유지한다.

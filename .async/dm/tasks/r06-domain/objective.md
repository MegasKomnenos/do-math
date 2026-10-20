# R06의 제출·검토·계획 기록에서 남은 null 관계

수용된 r06에서 남긴 M1/M2와 해당 생산 파일의 M4를 마친다. 같은 record/producer 시험을 쓰는 가까운 보완과 실제 확인한 수리는 이 task에서 함께 끝낸다. runtime 경계의 M3/M5는 r06-edges가 독립 수행한다. 선행은 r06만 필요하다.

## 답할 결과

1. submission._producer_check/seal_submission의 check/schema_ref/intent와 review_cycle.accept_result/authorize_record_replacement/context_for 및 core_engine._context.recover의 answer/result/manifest/restoration을 실제 생성 조건부터 repair history·sealed replay·record·context·표시까지 연결한다. 최초 검사 전 null과 검사 실패 객체, 미답변과 답변, 미복구와 복구의 의미를 구별한다. r09 수용판의 제출 검사·issue 전체 비교는 보존한다.
2. knowledge.decision_reference/governance._knowledge_import_basis, input_basis.decision_basis_changes, planning.capture_task_basis/exhaustion_state, task_scope.assessment_basis/apply_task_dispositions의 nullable basis map·id=None·before/after·이전 preparation 없음·assessment hash를 currentness/revision/import/hold의 실제 소비까지 연결한다. runtime status/trace라는 동명 필드와 섞지 않는다. 미생산 nullable schema는 실제 producer로 세지 않는다.
3. scope 파일의 domain 생산 파일에 남은 간접 표현·전달 값을 기존 후보 처분에서 이어 마친다. map의 역할 입력/상태metadata·신뢰wait/권한진단 등 domain 생산자도 이 범위다. 이미 수용된 활동/실행·질문 관계와 B58은 지정 근거를 재사용한다. 위임 공개 원결정 기능 자체는 r12-r13-fix의 배정이며 새 정책이나 그 미완성 결과를 이 작업의 선행으로 만들지 않는다.
4. 결과에는 M1/M2 및 domain M4의 충족 관계와 구체적인 미결을 분리한다. 공유 read-only runtime에서 확인한 결함은 숨기지 않는다. 전용 null 시험과 기존 producer/record storage의 같은 수리를 한 번에 마무리한다.

허용 시험은 tests/unit/test_producer_record_storage.py·test_record_family_storage.py, 필요할 때 unit/test_null_domain_consumers.py·sim/test_null_domain_consumers.py·support/null_domain_consumers.py다. 허용 runtime은 submission.py·review_cycle.py·input_basis.py·planning.py·task_scope.py·knowledge.py·knowledge_io.py·revisions.py의 직접 확인한 null 결함에 한정한다. 계약 재설계는 맡지 않는다.

## 공통 입력·원칙

SESSION_JSON의 workspace와 고정 inputs/context.md·plan.md·seams.md, task.json을 읽는다. 제품 상대 경로는 자기 workspace다. C:/math/.async/dm와 C:/math/docs의 입력은 읽기 전용이다. 원래1-C/R06은 실제 명시 null 생산 필드와 그 필드의 모든 읽기 소비자를 묻는다. 원문 위치는 tasks/r06/objective.md 및 sources/requirements-index.json, phases/001/tasks/closure-map/evidence/tracking-state.json[R06]·requirement-state.json[1-C]에 있다. 과거 run:은 C:/math/docs/do-math/continuous-development-2026-10-13이다.

r06의 report.json·evidence/producer-consumer-map.json(27가족과 M1~M5), discovery.json·candidate-dispositions.json·indirect-candidates.json·read-sites.json·symbol-locations.json·reuse.json·verification.json 및 managers/0017/review.md·source-review.json을 이어받는다. r06의 활동/실행/질문/외부3ID, r04/r05와 r03-fix의 수용 slice를 새 반례 없이 재작성하거나 반복 실행하지 않는다. 기존 파일의 조사 자료를 먼저 이용하고 후보 검색부터 전부 다시 시작하지 않는다. r09의 integration.inspect_bundles 문자열 guard가 r06 시작 뒤 반영됐으며 그 밖의 r06 제품128파일은 manager 검수 당시 같다.

managers/0017/null-followup-scope.json의 tasks[자기ID]가 R06-M4의 생산 소스 분담이다. 자기 파일에서 실제 dict/record/receipt/JSON 필드 null을 생산하는 표현과 간접 .get/함수반환/동적 mapping의 미분류만 처리한다. 이미 판정된 후보는 근거를 재사용한다. 소비자는 파일 소유와 무관하게 마지막 사용까지 읽는다. 다른 배정의 생산 필드가 이어지면 정확 생산 위치와 해당 배정을 교차 참조하며 그 작업의 완료를 기다리지 않는다. source 목록은 탐색 시작판이지 실제 null 모집단의 완결 증거가 아니다. 새 생산 파일을 발견하면 의미상 해당 배정에 연결하고 누락 사실을 남긴다. nullable schema·동명 key·None 반환/지역 초기화·키 부재를 실제 필드 null로 바꾸지 않는다.

각 관계는 실제 생산 조건/필드→저장·전달→직접/최종 소비 심볼→null의 의미·정상값 또는 부재와의 구별→정적 근거/정확 단언·판본으로 끝낸다. 모든 코드 경로의 실행이나 새 등록체계를 요구하지 않는다. 정적으로 충분하면 종료하고 실제 불확실성만 가장 작은 실제 producer→consumer 호출로 확인한다. 범위의 소비자를 대표 한 곳으로 축소하지 말고, 읽기만 한 관계와 실제 실행한 관계를 구별한다. 기존 map의 단순 '이번에 실행하지 않음'은 미충족과 동의어가 아니므로 현재 코드로 충족/미결을 판단한다.

## 수정과 최소 확인

task.json writes만 수정한다. 지정 runtime은 자기 null 생산/소비에서 직접 확인한 현행 결함의 최소 수리에만 쓴다. 예방적 None 정규화, schema 완화, 없는 null 생산자/구판 호환, 새 API·범용 nullable 체계는 만들지 않는다. 기존 현재성/권한/참조/봉인/저장 의미와 수용된 수리를 보존한다. 공유 core/governance/review_engine/delegations/schema는 r14-fix 또는 r12-r13-fix의 소유이고 context_store/formal/formal_preview/input_tool/knowledge_records는 r21-r22의 소유이므로 읽기 전용이다. 범위 밖에서 실제 결함을 확인하면 정확 producer 입력·소비·기대/실제·필요 파일/심볼을 보고하고 자기 유효 결과를 마친다. 다른 task 기록/사본에 쓰거나 진행 중 결과를 가져오지 않는다.

공통 fixture·기존 실제 producer/validator/Repository와 외부 경계 대역을 재사용한다. 새 helper는 두 직접 시험의 실제 중복을 줄일 때만 만들며 제품 함수를 대체하지 않는다. 공식 run_tests.py jobs1로 변경/남은 불확실성에 필요한 최소 ID만 실행한다. 새 외부 실호출·전체일반/T3/변이/T4/T5는 이 배정에 없다. 선택/실제row·exit·소스SHA·실행 중 변경·실패/남김을 보존한다. 시험을 실행하지 않았으면 정적 근거를 기록한다.

제품을 바꾸면 공식 build_skill_mirrors.py --target .agents와 --check --target .agents로 해당 미러를 생성·확인한다. 바이트 일치한 미러 시험은 반복하지 않는다. 비용 캐시는 evidence 보존 후 자기 base로 복원한다. 보고는 이 배정의 생산 범위가 어디까지 완료됐는지 적고 전체 R06 완료로 확대하지 않는다. 원보고/역사 counts를 합산하지 않으며 B58의 수용된 한정 처분·원보고 부재와 G4~G8·L01·Windows1314를 유지한다. check.py report C:/math/.async/dm r06-domain의 PASS를 확인한다. 공용소스/문서/queue/state·engine·과거원자료·Git index를 수정하지 않고 graphify를 갱신하지 않는다.

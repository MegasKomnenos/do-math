# R06의 상태·관찰·외부 경계에서 남은 null 관계

수용된 r06에서 남긴 M3/M5와 나머지 생산 파일의 M4를 마친다. 상태/반환/진단 값의 직접 소비 시험과 실제 확인한 수리를 한 task에서 처리한다. 제출·검토·계획 기록의 M1/M2는 r06-domain이 독립 수행한다. 선행은 r06만 필요하다.

## 답할 결과

1. reporting.status_report의 dict.fromkeys(OBSERVED_FIELDS), repository._decode_families/query, operation_trace.emit/phase, trace_report.phase_rows, scheduled_operator.release, cli._schedule_failure, windows_job.process_identity/resource_usage, formal.verify_lean의 null 반환 필드와 실제 모든 읽기/표시/운전 소비를 연결한다. snapshot status와 live ResearchEngine.status를 구별한다. start_guard의 provider_waits .get 체인은 null에 안전하지 않지만 확인된 caller는 live status를 준다. 실제 입력 흐름 또는 현재 API 계약을 확정해 도달 결함/비대상/정확 미결 중 하나로 판단하고, 잠재식만으로 임의 None 보정을 하지 않는다.
2. observations.record_self_check_response/_self_check_obligation의 malformed response·no-window, session_slots.provider_result_from_run/acquire의 nullable evidence/projection, external_engine._external_control/_run_external_action의 외부 ledger→owner 관계를 끝낸다. r06의503·reconciliation/retry, r04/r05 결과와 r03-fix 관찰저장 성질은 재사용하고 모든 owner 관계를 그 성공으로 대신하지 않는다. deadline_only는 followup 부재이며 가상 followup=None을 생산하지 않는다.
3. scope 파일의 edges 생산 파일에 남은 간접 .get/nullable 반환·동적 mapping을 기존 후보 처분에서 이어 마친다. provider/CLI/OS·formal/trust·도구/trace·상태조회가 대상이다. 실제 외부 호출을 추가하지 않고 충분한 기존 외부 포트 fixture/정적 근거를 사용한다. 진행 중 r14-fix가 바꾸는 관찰/core와 r21-r22가 바꾸는 formal/tool은 자기 시작판을 읽고 정확 소비 심볼 SHA를 남긴다.
4. 결과에는 M3/M5 및 edges M4의 충족 관계와 구체적인 미결을 분리한다. 원래 null 질문을 운전·T5 전체 감사로 넓히지 않는다. 새 발견을 작은 후속 조사로만 남기지 말고 허용 범위의 수정·최소 확인까지 마친다.

허용 시험은 필요할 때 tests/unit/test_null_boundary_consumers.py·sim/test_null_boundary_consumers.py·support/null_boundary_consumers.py다. 기존 r06 producer/record storage 시험은 읽기 전용이다. 허용 runtime은 reporting.py·supervision.py·repository.py·operation_trace.py·trace_report.py·scheduled_operator.py·cli.py·session_slots.py·external.py·external_engine.py·model_call.py·native_final.py·windows_job.py의 직접 확인한 null 결함에 한정한다. 활성 OS 자원/설치/예약 변경이나 새 실호출 권한을 추가하지 않는다.

## 공통 입력·원칙

SESSION_JSON의 workspace와 고정 inputs/context.md·plan.md·seams.md, task.json을 읽는다. 제품 상대 경로는 자기 workspace다. C:/math/.async/dm와 C:/math/docs의 입력은 읽기 전용이다. 원래1-C/R06은 실제 명시 null 생산 필드와 그 필드의 모든 읽기 소비자를 묻는다. 원문 위치는 tasks/r06/objective.md 및 sources/requirements-index.json, phases/001/tasks/closure-map/evidence/tracking-state.json[R06]·requirement-state.json[1-C]에 있다. 과거 run:은 C:/math/docs/do-math/continuous-development-2026-10-13이다.

r06의 report.json·evidence/producer-consumer-map.json(27가족과 M1~M5), discovery.json·candidate-dispositions.json·indirect-candidates.json·read-sites.json·symbol-locations.json·reuse.json·verification.json 및 managers/0017/review.md·source-review.json을 이어받는다. r06의 활동/실행/질문/외부3ID, r04/r05와 r03-fix의 수용 slice를 새 반례 없이 재작성하거나 반복 실행하지 않는다. 기존 파일의 조사 자료를 먼저 이용하고 후보 검색부터 전부 다시 시작하지 않는다. r09의 integration.inspect_bundles 문자열 guard가 r06 시작 뒤 반영됐으며 그 밖의 r06 제품128파일은 manager 검수 당시 같다.

managers/0017/null-followup-scope.json의 tasks[자기ID]가 R06-M4의 생산 소스 분담이다. 자기 파일에서 실제 dict/record/receipt/JSON 필드 null을 생산하는 표현과 간접 .get/함수반환/동적 mapping의 미분류만 처리한다. 이미 판정된 후보는 근거를 재사용한다. 소비자는 파일 소유와 무관하게 마지막 사용까지 읽는다. 다른 배정의 생산 필드가 이어지면 정확 생산 위치와 해당 배정을 교차 참조하며 그 작업의 완료를 기다리지 않는다. source 목록은 탐색 시작판이지 실제 null 모집단의 완결 증거가 아니다. 새 생산 파일을 발견하면 의미상 해당 배정에 연결하고 누락 사실을 남긴다. nullable schema·동명 key·None 반환/지역 초기화·키 부재를 실제 필드 null로 바꾸지 않는다.

각 관계는 실제 생산 조건/필드→저장·전달→직접/최종 소비 심볼→null의 의미·정상값 또는 부재와의 구별→정적 근거/정확 단언·판본으로 끝낸다. 모든 코드 경로의 실행이나 새 등록체계를 요구하지 않는다. 정적으로 충분하면 종료하고 실제 불확실성만 가장 작은 실제 producer→consumer 호출로 확인한다. 범위의 소비자를 대표 한 곳으로 축소하지 말고, 읽기만 한 관계와 실제 실행한 관계를 구별한다. 기존 map의 단순 '이번에 실행하지 않음'은 미충족과 동의어가 아니므로 현재 코드로 충족/미결을 판단한다.

## 수정과 최소 확인

task.json writes만 수정한다. 지정 runtime은 자기 null 생산/소비에서 직접 확인한 현행 결함의 최소 수리에만 쓴다. 예방적 None 정규화, schema 완화, 없는 null 생산자/구판 호환, 새 API·범용 nullable 체계는 만들지 않는다. 기존 현재성/권한/참조/봉인/저장 의미와 수용된 수리를 보존한다. 공유 core/governance/review_engine/delegations/schema는 r14-fix 또는 r12-r13-fix의 소유이고 context_store/formal/formal_preview/input_tool/knowledge_records는 r21-r22의 소유이므로 읽기 전용이다. 범위 밖에서 실제 결함을 확인하면 정확 producer 입력·소비·기대/실제·필요 파일/심볼을 보고하고 자기 유효 결과를 마친다. 다른 task 기록/사본에 쓰거나 진행 중 결과를 가져오지 않는다.

공통 fixture·기존 실제 producer/validator/Repository와 외부 경계 대역을 재사용한다. 새 helper는 두 직접 시험의 실제 중복을 줄일 때만 만들며 제품 함수를 대체하지 않는다. 공식 run_tests.py jobs1로 변경/남은 불확실성에 필요한 최소 ID만 실행한다. 새 외부 실호출·전체일반/T3/변이/T4/T5는 이 배정에 없다. 선택/실제row·exit·소스SHA·실행 중 변경·실패/남김을 보존한다. 시험을 실행하지 않았으면 정적 근거를 기록한다.

제품을 바꾸면 공식 build_skill_mirrors.py --target .agents와 --check --target .agents로 해당 미러를 생성·확인한다. 바이트 일치한 미러 시험은 반복하지 않는다. 비용 캐시는 evidence 보존 후 자기 base로 복원한다. 보고는 이 배정의 생산 범위가 어디까지 완료됐는지 적고 전체 R06 완료로 확대하지 않는다. 원보고/역사 counts를 합산하지 않으며 B58의 수용된 한정 처분·원보고 부재와 G4~G8·L01·Windows1314를 유지한다. check.py report C:/math/.async/dm r06-edges의 PASS를 확인한다. 공용소스/문서/queue/state·engine·과거원자료·Git index를 수정하지 않고 graphify를 갱신하지 않는다.

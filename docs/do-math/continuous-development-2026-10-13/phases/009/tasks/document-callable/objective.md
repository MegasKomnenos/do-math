## 목적과 역할

phase 008의 P01 운영/복구 결속은 지정 의미 검증을 통과했지만 CLI 문서의 기존 함수 표기 때문에 최종 관련 검사가 정본·미러 각각4건 실패했다. 이 한정 원인을 고쳐008의 A5 남김을 닫고 문서·시험 변경 단위를 인도 가능하게 한다. G1/G3/G8의 이 부분을 다루며 다른 문서 패킷이나 전체 관문을 완료로 바꾸지 않는다.

manager가 현재 doc_code와 HEAD 원문을 대조했다. CLI-실행-계약.md의 공급자 전송 절에 있는 `provider_final.output_contract`는 실제 callable이지만 bare dotted 표기여서 unowned field로 분류된다. 기존 function_reference_issues는 `provider_final.output_contract(...)` 표기를 실제 callable로 검사한다. 이 정본 경로를 사용하면 검사를 바꾸지 않고 의미를 보존할 수 있다. 시작 좌표는008 manager-evidence/verification.json과 review.md다.

## 완료 조건

### A1 함수 참조의 의미를 보존하며 명시 표기로 교정

시작 Git 상태·HEAD·소스 해시를008 source-final 및 manager 검수와 대조하고 기존 dirty를 보존한다. 제품·시험·문서의 미커밋 변경은008에서 승인한 지정 성과이며 임의 복원하지 않는다. 공용 문서·관리 기록과 기억의 커밋만 바뀐 경우 제품 변화와 구별한다.

CLI-실행-계약.md의 공급자 전송 절에서 해당 함수 이름을 기존 함수 검사기가 인식하는 명시 호출 표기로 바꾼다. 원 schema와 transport schema의 구분, 선택 필드의 부재/null 의미, worker/native 원자료, Claude/control_binding 경계는 그대로 유지한다. 문서에서 이름을 지워 검사를 피하지 않으며 함수 owner를 상태 schema에 추가하거나 unknown/defer 검사를 완화하지 않는다. doc_code·제품 runtime·시험 소스는 이번 쓰기 범위가 아니다.

수리 전 원실패는008의 정본110/미러89 보고와 HEAD helper 재현을 재사용한다. 같은 실패를 얻으려고 전체 묶음을 다시 돌리지 않는다. 기존 function_reference_issues로 수정된 문서의 함수 참조가 실제 callable에 연결되고 unowned_field_references에서 해당 오분류가 사라지는지 확인한다. 기존 구조 시험의 nonexistent/noncallable 반례를 유지하며 이 표기만을 위한 중복 시험은 만들지 않는다.

### A2 실패했던 문서 검사와008 관련 회귀를 같은 최종 판본에서 확인

아래 최종 정본 선택과 미러 선택을 공식 run_tests.py로 각각 한 번 완결한다. 선택 ID·고유 결과 row·실제 exit·소스 전후를 보존하고 실패/오류/skip/미실행이 없음을 확인한다.008의 정확한4실패 ID가 새 결과에서 passed로 연결돼야 한다. 이전 red/중간실패/partial 보고는 수정하지 않는다.

운영/복구 실제 객체·파일·정상/오류/null/live 부재·소유자 교란, 일반 재개·manifest/profile_selection와 bootstrap-info의 기존 단언이 유지된 상태여야 한다. runtime·시험 소스를 고쳐 통과시키는 것은 이번 배정이 아니며 새로운 문제는 정확한 failing ID·원인·영향 A와 후속 책임으로 반환한다.

### A3 미러·판본·원바이트를 확인하여 정확히 인계

공식 생성 계획을 먼저 읽고 이번 문서와 비용 캐시 사본만 생성한다. 계획 밖 드리프트는 덮지 말고 보고한다. 최종 build_skill_mirrors.py --check와 probe_cli.py --skill-only를 통과한다. 미러 시험 후 비용 캐시만 공식 재동기화한다. 시작/종료 변경은 정본·미러 문서와 비용 캐시 범위에 있어야 한다.

008에서 검수한 runtime124·smoke 입력3·양쪽 corpus102경로와 그 외 시험 소스는 불변이어야 한다. 원바이트 해시가 같으면008의 명시SHA/Git clean 검수와 공급자 실호출 한정 재사용 근거를 연결하고 불필요한 실호출을 하지 않는다. 문서가 바뀌므로 G4~G6/G8은 후속 최종 판본 증거가 계속 필요하다. report에는 위3개 A, 최종 선택/row/exit, 네 실패의 새 결과, 실제 변경과 재사용 조건을 기록한다.008 P01/N03-003의 지정 부분과 이번 함수 표기만 닫으며 N03 전체·P02~P11·G7·최종 review 완료로 확대하지 않는다.

## 판단과 경계

task 모델은 gpt-6.1-sol/high다. 허용 쓰기는 CLI-실행-계약.md의 위 표기, 대응 공식 미러, 양쪽 시험 비용 캐시뿐이다. 기존 문서 검사기의 함수 표기를 사용하므로 새 seam·등록부·예외가 필요 없다. 다른 제품 수정이 필요하면 유효 부분을 보존하고 partial로 보고한다.

manager가 실제 파일·근거를 검수하고 Git 마감을 맡는다. Git stage/commit/reset/checkout/push, graphify 갱신, 기존 연구 시작/재개/삭제, OS 예약 변경과 실제 모델 호출은 배정하지 않는다. 전체 일반/T3/변이도 이번 검사가 아니다. 검사 중 소스를 고정하고 한 묶음씩 jobs1로 실행한다. 시간 경과를 실패나 자동 종료 근거로 쓰지 않는다.

## 검증 방법

cwd는 C:\math, Python은 C:\Users\wogud\AppData\Local\Programs\Python\Python312\python.exe다. 공식 실행은 이 Python에 `-u -B <runner> <선택> --jobs 1 --output <자기 evidence의 새 경로>`를 전달한다. argv/cwd/PID/시작·종료/stdout/stderr/exit와 소스 해시를 보존한다. 실행 중 result.json 관찰은 file_io.read_bytes_shared를 사용한다.

1. 변경 전 근거·현재 callable과 doc_code의 function_reference_issues/unowned_field_references 정의를 대조하고 A1의 표기를 고친다.
2. 정본 runner는 `.claude/skills/do-math/scripts/run_tests.py`이며 선택은 `structure.test_doc_code sim.test_role_input_context.OperationalInputTests sim.test_knowledge_currentness.RecoveryMaterialTests flows.test_knowledge_impact_retry.UnreadableBeforeReviewTests unit.test_role_input_packaging unit.test_role_input_scoped_packaging boundary.test_operator_bootstrap_info unit.test_engine_trace_report_corruption unit.test_storage_record_queries unit.test_storage_report_projections boundary.test_engine_cli`다.008에서110개였으며 실제 선택을 확인한다.
3. 생성기는 `.claude/skills/writing-skills/scripts/build_skill_mirrors.py`다. 현재 계획이 문서·비용 캐시 허용 범위인지 확인하고 생성한다. 미러 runner `.agents/skills/do-math/scripts/run_tests.py`에는2번 선택 중 `unit.test_role_input_scoped_packaging`을 제외한008의89개 선택을 사용한다. 이 제외는008에서 수정하지 않은 모듈의 정본 검증을 재사용하는 기존 책임 배분이며 실패한 ID를 빼는 것이 아니다.
4. 네 실패 ID는 `structure.test_doc_code.DocumentCodeTests.test_all_dotted_document_fields_have_an_owner`, `unit.test_engine_trace_report_corruption.TraceCorruptionTests.test_unreadable_error_sidecar_has_bounded_explicit_status`, `unit.test_role_input_packaging.RoleInputTests.test_role_input_uses_current_schema_documents_and_private_resume_bytes`, `unit.test_storage_report_projections.ReportProjections.test_human_report_preserves_loaded_initialization_blocker_and_machine_finding`다. 양쪽 새 보고의 정확한 passed row로 대응시킨다.
5. 비용 캐시 동기화 뒤 생성기 --check, 정본 probe_cli.py --skill-only와 A3 소스 대조를 수행한다. `python -B services/continuous-development/check.py report C:\math C:\math\docs\do-math\continuous-development-2026-10-13 009 document-callable`를 통과한 뒤 상태와 report.json 경로를 반환한다.

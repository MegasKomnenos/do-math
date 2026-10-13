## 목적과 역할

운영 점검·종료 후 복구 문서가 가리키는 필드를 실제 역할 입력과 연결한다. 일반 재개 결과에도 result_source가 있지만 운영 진단의 recovery_materials.result_source와는 생산자가 다르다. 현재 doc_code는 일부를 AST 추출 또는 다른 동명 생산자로 확인하므로, 이름이 존재해도 실제 전달·복원 오류·부재를 놓칠 수 있다. phase 001 P01의 이 유한한 남김을 닫아 G1/G3의 문서 지시와 검출력을 개선한다. 함께 다룰 설치 설명은 N03-003의 LIVE_INSTALLATION_ROOT 한 문장이다.

상류 공급자 수리는007에서 지정 회귀를 완료했다. 그 runtime·corpus는 고정한다. 이번 task의 모델은 gpt-6.1-sol/high이며 제품 시험의 공급자 모델 선택과 구별한다. 공용 문서와 phase.json의 inputs를 읽고, 긴 JSON은 P01 및 N03의 LIVE_INSTALLATION_ROOT 항목을 선택한다. 원문 의무는 결함-범주.md의13-C 및 P01에 기록된1181/1184/1201/1600/1613행 주변을 현재 제목으로 확인한다. 기록된 행 번호는 찾기 좌표이며 현 원문을 우선한다.

## 완료 조건

### A1 현재 생산자·문서 소비와 보존 범위를 확정

시작 파일 해시와 Git 상태를 남기고007 source-final 및 manager 검수와 대조한다. C2와007 manager verification에 기록된 운영자 작문 도구4파일 차이 및 이후 manager의 공용 문서/기억·Git 변경을 제품 변화와 구별한다. 모델 선택 정책은 C8을 따른다. 기존 dirty를 보존한다.

P01의 checkpoint_source, recovery_source, checkpoint_files, recovered_output_files, recovery_materials, operational_evidence를 문서별 실제 소비와 _context의 반환 객체에 대응시킨다. 일반 재개 restore_continuation의 result_source/rejected_response/previous_output_files는 별도 경계로 유지한다. 현재 doc_code의 해당 여섯 AST 추출 지점과 activity_continuations의 중첩 소비를 확인한다. 쓰이지 않는 이름이면 실제 소비 부재를 근거로 제거하고, 남은 소비가 있으면 그 경계를 보존한다. AST 호출 개수 감소를 의미 완료로 세지 않는다.

B132~B134의 manifest/prompt/documents/profile_selection와 B133 일반 재개 검사는 재구현하지 않는다. 바뀌는 doc_code를 import하는 현재6모듈과 새 소비를 찾아 검사 범위에 연결한다. 관찰·현재 처분·근거와 정확한 미결을 표 또는 짧은 기록에 남긴다.

### A2 운영·복구 지시를 실제 객체와 조건에 맞게 교정

운영-점검.md의 실행 중 증거는 operational_evidence.checkpoint_source/checkpoint_files로, 종료 후 진단은 recovery_materials.result_source/checkpoint_source/output_files로 소유자를 명시한다. 정상 파일의 local_path를 읽는 지시에는 그 필드가 존재하는 조건을 둔다. final_result_status=available만으로 복원 성공을 보증하지 않는지 현재 생산자와 대조한다. restoration_error가 있으면 원 artifact/snapshot/기대 해시·크기 및 관찰 오류를 진단 근거로 사용하고, 없는 local_path를 읽거나 검증되지 않은 바이트를 수학적 수락 근거로 쓰지 않는다. checkpoint_source=null과 live_review에서 recovery_materials 부재도 실제 조건대로 설명한다.

정상 결과·checkpoint_recovery·activity_result, 같은 원자료의 중복 계수 금지, 다른 실행의 live 공간으로 빈칸을 채우지 않는 기존 의무를 유지한다. CLI-실행-계약.md는 이 P01 문장과 필드 결속에 영향을 받는 절만 교정한다. 문서 의미를 시험 편의에 맞춰 줄이지 않는다.

### A3 실제 반환·파일과 반례가 문서 결속을 검증

기존 OperationalInputTests, RecoveryMaterialTests, UnreadableBeforeReviewTests 및 일반 재개 검사를 재사용한다. 실제 _context/입력 포장/저장·파일 생산을 유지하고 외부 포트에서만 대역을 둔다. 문서 검사기의 새 경계를 실제 반환 객체로 채워 검사한다. 현재 필드를 베낀 합성 표, 반환하지 않는 AST dict 또는 타 생산자의 동명 필드로 실제 결과 검사를 대체하지 않는다. AST helper 전체를 새 추론기로 확장하지 않는다.

정상 sealed checkpoint와 근거 파일의 local_path·바이트·sha256·bytes·snapshot, 종료 후 정상/복원 불가 자료, checkpoint_source=null, live에서 recovery_materials 부재, activity_continuations의 실제 문서 소비를 검사한다. 정상 객체 한 항목의 local_path 제거, 잘못된 해시/크기, 동명 운영/복구/일반 재개 소유자 교환이 해당 검사에서 실패해야 한다. 원제품 경로가 반려하는 입력은 정확한 반려 사유로 확인한다. 실제 반환을 얻은 뒤 그 사본을 교란하는 문서 검사 반례와 제품 경계의 손상 입력 검사를 구별한다.

현재 문서 결속 공백을 드러내는 새 단언을 수리 전에 실행해 red를 보존하고 수리 뒤 같은 성질의 통과를 연결한다. 문서 검사에서 입력 이름은 field_schemas()가 반환하는 dict의 키이며, 문서 필드 경로의 첫 이름이다. 예를 들어 operational_evidence.checkpoint_source.local_path의 입력 이름은 operational_evidence이고, recovery_materials.result_source.local_path의 입력 이름은 recovery_materials다. 이 두 입력의 구조를 AST 추정에서 실제 반환 검사로 옮기면, 일반 문서 순회는 실제 객체를 받는 회귀 시험에 그 검사를 맡겨야 한다. 작업자는 각 입력 이름을 실제 객체를 제공하는 시험 메서드와 대응시키고 해당 메서드가 문서의 필드를 검사하는지 확인한다. 기존 defer_* 방식처럼 일반 순회에서 이 검사를 잠시 건너뛰는 목록을 사용한다면, 이름 오기·빠진 담당 시험·다른 입력까지 함께 건너뛰는 경우를 검사로 거부한다. 함수 구성은 재량이며 새로운 전역 등록부를 요구하지 않는다. 정상/오류/null/부재를 필드 합집합 하나로 합쳐 누락을 숨기지 않는다.

### A4 설치 경로의 확정된 낡은 설명을 교정

독립-운영.md의 「설치본을 고정하고 live 수리 대상을 구별한다」 절에서 LIVE_INSTALLATION_ROOT 설명을 operator_bootstrap.main이 manifest의 installation_root 또는 snapshot_root를 scheduled_operator.main의 installation_root 인자로 전달하는 현 경계에 맞춘다. 고정 사본과 live 수리 대상 구별 및 manifest 검증의 한계를 유지한다. 기존 boundary.test_operator_bootstrap_info의 실제 실행을 근거로 연결한다. 옛 전역 이름을 제품에 추가하지 않는다. N03의 다른 절·문서 전체 이름 검토는 별도 남김이다.

### A5 관련 회귀·미러와 정확한 인계

아래 지정 검사를 최종 시험·문서 판본에서 완료하고 선택/고유 row/실제 종료·소스 전후 해시를 남긴다. 이전 반환 검사와 단언을 유지하며 실패·skip·미실행을 숨기지 않는다. 허용된 미러만 공식 생성하고 생성 계획·현재 dirty·실제 변경을 대조한다. 최종 --check와 --skill-only를 통과하고 runtime/corpus 불변을 확인한다. 제품 문서 변경은 후속 최종 판본 근거에 연결하되 공급자 runtime이 바뀐 것처럼 재호출하지 않는다.

report는 A1~A5, 실제 변경, red/green, 보존한 기존 성질, 미실행·권한 밖 발견과 다음 책임을 기록한다. 모든 A가 pass일 때만 complete다. 이번 완료는 P01 및 N03-003의 지정 문장에 한정되며 나머지 문서·G1~G8 전체나 최종 관문을 완료로 바꾸지 않는다.

## 판단과 경계

phase.json의 writes는 세 문서, doc_code와 기존 입력 helper, 명시한 직접 소비 시험 및 대응 미러/비용 캐시다. 여기에 파일이 나열됐어도 이번 경계와 무관한 성질을 바꿀 권한은 아니다. helper의 구체적 표현과 실제 반환을 연결하는 작은 공통 함수는 구현 재량이다. runtime/core_engine/context_store/bootstrap의 의미 수정은 쓰기 범위 밖이다.

제품 결함이나 추가 소비 범위가 확인되면 재현 근거와 영향 A를 fail/not_run으로 보고한다. 해결된 부분은 유지하고 다음 manager가 수리 범위를 배정하게 한다. 부분 완료를 피하려고 제품 검사를 완화하거나 새 문서 계약을 발명하지 않는다. 관할 밖 의무는 finding으로 반환한다.

검사 묶음은 순차 실행하고 worker 합계3 이하, 기본jobs1을 따른다. 검사 중 소스를 고정하며 시간은 소프트 기준이다. 실제 모델 호출·기존 연구 시작/재개/삭제·OS 예약 변경·graphify 갱신·Git stage/commit/reset/checkout/push는 이번 작업에 포함되지 않는다. manager와 서비스가 검수·커밋·다음 실행을 맡는다.

## 검증 방법

cwd는 C:\math, Python은 C:\Users\wogud\AppData\Local\Programs\Python\Python312\python.exe다. 공식 명령은 이 Python으로 `-u -B .claude/skills/do-math/scripts/run_tests.py <선택> --jobs 1 --output <자기 evidence의 새 경로>`를 실행한다. argv/cwd/PID/시작·종료/stdout/stderr/exit와 소스 전후를 보존한다. 실행 중 result.json은 file_io.read_bytes_shared로 관찰한다.

1. A1 표와 원문을 바탕으로 A3 반례의 정확한 ID를 먼저 실행한다. 기존 전체 묶음의 실패를 보기 위한 무의미한 반복은 하지 않는다.
2. 최종 정본의 `structure.test_doc_code`, `sim.test_role_input_context.OperationalInputTests`, `sim.test_knowledge_currentness.RecoveryMaterialTests`, `flows.test_knowledge_impact_retry.UnreadableBeforeReviewTests`, `unit.test_role_input_packaging`, `unit.test_role_input_scoped_packaging`, `boundary.test_operator_bootstrap_info`를 한 묶음으로 실행한다. 정확한 클래스명은 시작 때 현재 코드로 확인한다.
3. 공유 doc_code 소비 회귀는 `unit.test_engine_trace_report_corruption unit.test_storage_record_queries unit.test_storage_report_projections boundary.test_engine_cli`로 실행한다. 앞 묶음의 doc_code 직접 소비와 함께 현재6모듈을 덮는다. 수정하거나 새로 보강한 시험이 이 선택 밖이면 그 정확한 ID를 추가하고 이유를 남긴다. 전체 일반/T3/변이 실행은 이번 배정이 아니다.
4. 공식 build_skill_mirrors.py의 생성 계획을 확인한 뒤 대응 파일을 생성한다. 미러의 `.agents/skills/do-math/scripts/run_tests.py`로 2번과3번 선택 중 이번에 수정한 시험 모듈, `structure.test_doc_code`, 두 운영/복구 클래스 및 bootstrap-info를 중복 없이 한 묶음에 넣어 실행한다. 미러 실행 후 비용 캐시만 공식 재동기화하고 `build_skill_mirrors.py --check`, `probe_cli.py --skill-only`를 확인한다.
5. `python -B services/continuous-development/check.py report C:\math C:\math\docs\do-math\continuous-development-2026-10-13 008 document-recovery`를 통과한다. 마지막 응답에는 complete/partial/blocked와 자기 report.json 경로를 남긴다.

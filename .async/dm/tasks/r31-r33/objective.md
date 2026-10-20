# R31~R33: 실제 역할 입력의 광고와 양쪽 수신·계약 근거

사용자 원문 3-A/3-B에서 남은 역할 입력 질문을 마친다. 역할 계약이 요구하는 근거가 실제 지급 입력이나 정확한 참조로 도달하고, 광고된 선택/참조는 작업 공간 제출 검사와 중앙 수신에서 같은 의미로 처리되어야 한다. 준비·계획, 수행·학술·평가, 운영·유지보수는 같은 role_input_requirements/submission helper를 사용하므로 관계 판단·가까운 수리·필요한 확인을 한 task로 묶는다. 이미 충분한 과거 성질을 새 전수 실행으로 대체하지 않는다.

## 시작판과 원자료

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md를 읽고 자기 workspace만 수정한다. 원문은 `C:/math/docs/do-math/시험-재편-2026-09-29/조사/결함-범주.md` 3-A/3-B와 같은 단계-전환표, `C:/math/docs/do-math/continuous-development-2026-10-13/phases/001/tasks/closure-map/evidence`의 requirement-state/tracking-state R31/R32/R33·prior-review-state·evidence-catalog다. sources의 사용자 결정·모델/묶음 지시도 따른다. 과거 `run:`은 위 continuous-development 루트이며 해당 current_work.role_input_requirement_integration/role_input_variant_integration/role_input_evidence_integration/role_input_missing_guard_integration/submission_population_integration만 필요에 맞게 읽는다. 보존 보고가 없으면 counts를 성공으로 합산하지 않는다.

현재 수용된 r09의 실제 제출 반려/중앙 봉인, r12-r13-fix의 실제 검토·위임 입력, r21-r22의 큰 입력/전문 참조, r25-r26의 공개 CLI 성질은 해당 범위로 재사용한다. r06-finish/r22-snapshots/r29-r30의 중간 workspace는 소비하지 않는다. 현행 수용판의 공개 인터페이스를 사용하며 완료를 기다릴 실제 선행 결과는 없다. 이번 입력은 공용 문서와 함께 고정된다.

## 끝낼 유한 질문

1. 실제 `contracts.ROLES`, `role_input_requirements.ROLE_INPUT_REQUIREMENTS` 및 judgment_input_keys/paths/source_lists/source_refs, 역할 계약 문서 전건을 현재 producer/prepare_role_input의 live·복구·단계 변형과 연결한다. 역사 역할명/분기를 임의 복원하지 않는다. 요구표의 존재나 `set(table)==set(ROLES)`만으로 문서의 의미 입력 전건을 입증하지 않는다. 이미 명시된 근거와 허용된 부재/null, 다른 검토 자리의 비공개 정보를 구별한다. 읽을 근거가 없는 칸에 가짜 기본값을 채우지 않는다.
2. `context_store.prepare_role_input`의 실제 context/validation_context/manifest와 `submission.reference_catalog`, validate_reference, producer_check, 중앙 capture/application의 소비를 잇는다. 광고의 catalog·admissible_basis_refs·ready/returned task ID·허용 프로필·과제/자료 지목을 문서가 허용한 ID/이름/경로/별칭으로 확인한다. 각 집합의 원소/식별형식을 기존 시험이 실제로 순회하는지, workspace 수락과 중앙 수락이 같은 출력에 대응하는지 판정한다. 빈 과제만 있는 helper·등록 수·스키마 통과를 비빈 실제 적용 근거로 확대하지 않는다.
3. 광고 밖, 누락/과잉/중복은 그 입력을 지목하는 정확 사유로 거부되어야 한다. 실제 원자료에서 독립 기대값을 얻고 양성 출력을 먼저 확인한 뒤 필요한 최소 반례를 만든다. helper의 문제 은폐, 대역으로 producer/수신 대체, 반려만 확인하는 약한 단언을 발견하면 가까운 관련 수정과 함께 고친다. 이전 r09의 원 bytes/hash/receipt·재전달/정상 후속과 정상 기대값을 보존한다.
4. 계약상 필수 근거의 실제 read_source/봉인파일 도달과 필수 항목·파일 손상의 정확 반려를 판단한다. 직접 inline과 정확 참조는 같은 값/의미로 연결하되 모든 자료의 inline 복제를 요구하지 않는다. 기존 크기/참조 수리를 되돌리거나 큰 fixture를 다시 실행하지 않는다. 현재 분기별 실제 생산·소비와 충분한 증거, 정확 공백/수리를 남긴다. 10 base 역할을 동적 schema 전건의 외부 CLI 수용 증거로 세지 않는다(R19/R20 G7 별도).
5. 이 경계와 직접 관련된 과거 변경은 원 diff→현재 소비→기존 단언/원보고로 유지/교정/제거/추가판정만 연결한다. 다른 PR/K/P2 전수 감사, 새로운 역할 registry, 전수 명령 실행표, 기존 완료된 문서 P/N 작업의 재개방은 하지 않는다. 가까운 구조 반려 단언의 공백은 같은 수정에 묶는다.

## 수정 소유와 독립성

task.json의 writes가 정본이다. role_input_requirements.py·submission.py/submission_tool.py 및 지정 역할/제출 시험·전용 helper를 수정할 수 있다. 실제 판정한 규칙의 한 정본과 호출부를 유지하며 기존 schema/권한/현재성/근거 검사를 줄여 통과시키지 않는다. 지정 기존 helper로 표현이 충분하면 새 helper를 만들지 않는다. 새 회귀가 필요하면 지정 test_role_input_contract_reach.py/role_input_cases.py 안에서 묶는다.

core/call/governance_engine/context_store·planning/revision·review/governance/delegations·repository/schema/저장, 공통 Sim/model/ports/trust fixture와 역할 문서/이음새 정본은 읽기 전용이다. 실행 중 null/구조 저장 task 및 준비된 owner 실패 task와 의미 쓰기 범위가 겹치지 않는다. 실제 쓰기 밖 결함은 정확한 입력·producer/consumer·필요 파일·사용 영향으로 보고하고 자기 범위의 유효한 수리는 마친다. 표현 변경이 필요하다는 추측만으로 독립 작업을 기다리지 않는다.

## 최소 검증과 보고

정적으로 충분한 관계는 반복 실행하지 않는다. 바뀐 동작과 영향받는 직접 helper 소비만 workspace 공식 run_tests.py --jobs 1로 확인한다. 변경을 고정한 후 필요한 선택·고유 row·exit·소스 SHA/실행 중 변경·최초 실패/fixture 교정·소프트 초과를 보존한다. 전체 일반/T3/변이/T4/T5와 새 외부 모델·실환경 실행은 하지 않는다. 역할/상태 조합마다 전부 init부터 반복할 필요는 없다.

공식 build_skill_mirrors.py --target .agents와 --check로 지정 변경만 미러에 반영하고 대응 byte를 확인한다. 비용캐시는 원증거 보존 후 자기 base로 복원한다. report.json에는 R31~R33/3-A·3-B의 충분한 성질, 실제 수리, 구체적인 남김과 최종 통합판 대기를 구별해 적는다. `python C:/math/services/async-development/check.py report C:/math/.async/dm r31-r33`을 통과한다. 공용 소스/문서/queue/state·다른 task·Git index·graphify는 수정하지 않는다.

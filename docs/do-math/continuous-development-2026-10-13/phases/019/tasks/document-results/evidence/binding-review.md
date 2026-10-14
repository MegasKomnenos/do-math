# P02 문서 결속 검토와 인계

시작 HEAD는 a29f3c6a7889a74bc35af7360e36de9492ad814a다. 시작 skills/diff 2,675개 SHA256은 phase 018 manager source-inspected와 전건 일치한다. Git dirty의 canonical.py/repository.py·migration fixture, 두 미추적 시험의 양쪽 사본과 운영자 작문 도구·서비스 설정은 시작부터 존재하며 이 task에 귀속하지 않는다. 시작 Git diff·index·상태와 해시를 따로 보존했다. 제품 파일의 현재 변경은 지정 writes 안에서만 발생했다.

| P02 소유자 | 실제 생산·소비와 담당 | 확인한 성질 |
|---|---|---|
| source_ref | write_source_catalog / ContextStoreTests.test_new_catalog_is_hashed_from_the_bytes_it_wrote; fit_context와 prepare_role_input의 실제 참조 파일도 읽음 | canonical JSON 원바이트, path/SHA256/bytes/format, catalog total 및 축소 항목 total. 큰 목록의 catalog 참조와 과제 행의 input/details 참조·snapshot을 구별 |
| research_sources | _context의 sources → prepare_role_input / PackagedInputTests.test_planning_keeps_completed_report_and_active_work_as_readable_context | 문서 sources 별칭, 이번 workspace의 정확 input/sources 경로, 원 source record·artifact SHA·snapshot 원바이트, 완료 과제 읽기와 선택 모집단 분리 |
| materialized_output_files | _preserve_outputs와 _context / PackagedInputTests.test_task_result_paths_survive_packaging_without_entering_validation_hashes; 기존 600k 실제 흐름 | stored artifact_ref/path/hash/size와 새 input/task-results/<task>/<execution>/<path>를 대조. 동일 바이트라도 다른 과제·실행 경로 차용 반려 |
| results | _apply의 실제 저장 결과 / sim 수신 시험 및 AcceptanceTests.test_large_accepted_report_survives_revision_review_and_resumed_work | report 전바이트, 저장 output_files·복원 파일, 독립 knowledge/relations/integration_bundles의 결과 비중복, 개정·계약 검토·재개에서 600k 보고와 증거 파일 보존 |

수제 task.results fixture는 물질화 검사에만 사용한다. _apply 생산과 knowledge의 별도 권위 기록은 기존 KnowledgeConnections·ReceiptPreservationTests에서 직접 관측한다. 실제 제출의 bundle 분할/수신·재시도와 owns_response=False의 보고 비중복은 기존 수신 시험을 유지했다. integration.member_values는 manifest를 연구 응답 본문에서 분리하며 _apply도 같은 필드를 보존 결과에서 제외한다. 정상 bundle manifest를 task.results에 다시 저장하는 새 계약을 만들지 않았다. 파일 보존은 실제 600k 보고/부분 evidence의 저장과 재개 입력으로 연결한다. 엔진, 저장소, _context, _apply, _preserve_outputs, prepare_role_input을 대역으로 가리지 않았다. 기존 모델·Git·Lean의 외부 포트 대역 경계는 유지했다.

일반 scoped_field_issues는 네 소유자가 실제 입력 없이 검사될 때 기본 거부한다. 실제 경계를 가진 여섯 소비 모듈의 문서 순회만 명시 defer하며, structure의 로컬 담당 대응 검사가 네 owner와 담당 method의 실제 assert_result_documents 호출을 확인한다. 오기·담당 누락·없는 method·문서 검사가 없는 method로 교환하면 실패한다. 네 owner의 defer가 P01 operational_evidence, 일반 재개 result_source 또는 status까지 건너뛰지 않는 음성 단언을 유지했다. 새로운 전역 담당 등록부나 제품 AST 추론기를 만들지 않았다. 기존 AST helper는 다른 P03/REVIEW/TRUST 소비가 남아 있으므로 유지하고 P02의 source_ref/stored_file/restored_file/retained/result 조립만 제거했다.

반환 후 사본 교란은 실제 제품의 입력 반려와 구별한다. 실제 catalog 참조의 경로 차용·hash/size 변조, 복원 결과의 report 삭제·각 output file의 local_path 삭제·hash/size 변조·다른 실행의 동일 바이트 경로 차용, 원자료의 경로/hash/size 교란, 저장 execution에 local_path를 붙이는 대체 증거를 검사한다. 실제 값으로 문서 필드 오기와 다른 owner의 동명 필드를 반려한다. 두 output file을 각각 교란하므로 한 항목의 정상 필드로 다른 항목의 누락을 가리지 않는다. 정상 빈 sources/results와 명시 index의 부재도 검사하지만 빈 배열을 원소 필드의 정상 증거로 쓰지 않는다. 실제 _context의 source/task artifact hash 손상은 정확 ValueError와 미물질화를, 실제 read_source의 hash/size 손상은 정확 error_type/reason·빈 bytes·range=None을 확인한다.

수리 전 red는 한 test method의 8개 owner/별칭 subTest가 ValueError not raised로 실패했다. focus의 13error/22passed는 _context 관련 다른 소비가 쓰는 context_store import를 잘못 제거한 NameError와, 준비 역할의 좁은 tasks에서 다른 과제를 찾은 StopIteration이었다. import를 복구하고 조회 권한의 전건 task_catalog에서 다른 과제 원문을 찾게 교정했다. corrected 23passed를 연결했다. 첫 문서 편집 스크립트의 CRLF 가정 실패는 공통-실행의 첫 문장만 반영됐고 지식 문서 바이트는 쓰기 전이었다. 개행과 무관한 정확 문장 교체로 끝냈다. 초기 mirror-plan의 iter_files 반환형 가정과 출력 감사의 selected/진행 중 report 가정 오류는 자기 evidence 스크립트만 교정했다. 실패 출력과 원 스크립트를 제품 실패/정상 결과로 바꾸지 않았다.

B110~B114의 실제 도입 Git diff·현재 P02 소비·phase 001 분석을 대조했다. 해당 7개 저장소 원보고의 SHA256도 현재 파일과 같지만 역사 counts를 이번 성공에 합산하지 않는다. B113의 source_ref AST 결속과 B114의 stored/restored/results 문자열 조립은 실제 writer/_context/_apply 결과로 교체했다. B110~B112의 명시 owner·line-local 별칭·저장/역할 입력 구별은 유지한다. B114의 review_sources는 다른 REVIEW 경계이므로 그대로 둔다. PR24 전체나 다른 hunk의 재검토 완료를 주장하지 않는다. P01 및 B130~B134의 default-reject/defer/실제 반환·manifest/continuation/profile_selection 단언은 최종 관련 선택에서 유지됐다.

문서 수정은 공통-실행의 source_ref.sha256/bytes 명시와 지식-저작과-재사용의 sources[].local_path 및 해당 research_sources 별칭이다. 결과 읽기 권한과 선택 모집단의 차이, 과거 artifact와 이번 local_path 구별, 읽기 실패를 빈 목록으로 바꾸지 않는 설명은 보존했다. 입력 계약·입출력 스키마·runtime을 바꾸지 않았다.

정본과 미러는 동일 187 ID를 전부 실행해 각각 186passed·1skipped·exit0다. 실패·오류·미실행은 없고 공식 Python 875개 및 검사 tree의 비캐시 파일 전후 해시가 전건 일치한다. skip은 기존 ContextStoreTests의 실제 심볼릭 링크 생성이 Windows 1314로 반려된 권한 조건이며 해당 파일의 원래 skip 처리다. 권한을 바꾸거나 정상으로 세지 않는다. P02 필드/파일 결속 성질에는 이 skip이 없지만 G4의 조건부 환경 남김은 manager가 별도로 판정해야 한다. 소프트 예산 초과는 공식 보고에 보존하며 단언을 약화하지 않았다.

공식 생성 계획의 15개 변경은 모두 writes 안이었다. 생성 후 동일 선택의 미러 실행, 마지막 비용 캐시 동기화와 --check/skill-only를 확인한다. runtime/실호출 입력139·corpus144경로/150명시SHA·host8원자료·도구5SHA·과거baseline910/Git blob·기존 T4 runner/adapter/Job fixture를 보존했다. 이전 실호출의 승인된 성질만 같은 입력/도구 바이트에서 한정 재사용한다. 두 문장 변경은 향후 일반 역할 prompt 판본을 바꾸므로 역사 고정 smoke prompt의 성공을 새 문서 읽기/준수의 증거로 확대하지 않는다.

이 작업은 P02의 지정 문서 결속을 닫는다. P03, REVIEW/TRUST·다른 P/N, L01 운전 프로필·출력 단위, G4 기본전체·G5 fresh T3·G6 전수변이 및 G8 최종 review는 남는다. 전체 T4 재실행·새 T5/유료/예약/학술 호출·설치 신뢰 변경·기존 연구 재개/삭제·graphify 갱신·Git stage/commit/reset/checkout/push를 수행하지 않았다.

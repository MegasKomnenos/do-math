# 측정 시험의 자기 Git 기준판 준비와 실제 경계 확인

G4 full4의 unit.test_adapter_coverage에서 드러난 Git 경계 7개 행(3failed/2error/2not_run)과 setUpClass error1을 해결한다. 목적은 실제 작업 사본의 판본으로 기존 측정 meta 시험과 이후 fresh T3를 수행할 수 있게 하는 것이다. 먼저 실행 준비의 누락을 해소하며, Git 없는 제품 사용을 새 지원 요구로 만들지 않는다.

SESSION_JSON와 task.json, inputs/context.md·plan.md·seams.md를 먼저 읽는다. 작업 사본의 AGENTS.md·시험-지침과 manager0064/review.md, 저장 범위 사용자 지시를 적용한다. 추가 입력의 C:/math/.async/dm와 docs는 읽기 전용 원자료이며 제품은 자기 workspace만 사용한다. full4 원보고의 실패·subTest·fixture와 현재 정의/직접 소비자를 먼저 읽는다. 보고에 적힌 원인도 코드로 확인하고, 제품 결함과 현행 계약과 어긋난 fixture를 구별한다.

현재 원증거는 selected4288=실제4288, 4262passed/14failed/9error/1skipped/2not_run, fixture error1, exit1이다. manager는 정본시험2/공식미러2 수리만 통합·부분 수용했다. 서로 다른 판본의 부분 성공을 전체 통과로 합산하지 않는다. 이번 task는 지정된 실제 실패의 수리와 필요한 직접 확인을 끝내는 것이 목적이다. 전가족 저장 생산/전필드/새reader/옛head quota나 별도 감사·프레임워크를 만들지 않는다. 이미 충분한 공통 codec·업무 근거는 재사용한다.

원 실패 보고를 보존하고 코드를 읽어 충분한 부분은 정적으로 판정한다. 실행이 필요한 수리만 정확한 실패 ID 또는 관련 최소 묶음으로 공식 run_tests.py에서 확인한다. 단언 약화·skip 추가·선택 축소·구판 필드 복원·호환 계층·내부 검사 대역으로 성공을 만들지 않는다. 같은 문제를 문서 번호/실패 행마다 새 task로 나누지 않는다. 직접 관련 수리·helper 소비자·공식미러를 이 task에서 함께 마친다. 새 런타임 결함이면 원실패와 수리 이유·관련 확인을 남긴다. 범위 밖 결정이 필요하면 유효 결과와 정확한 남김을 보고한다.

시험은 한 번에 하나만 실행하며 전체 G4/T3/T4/T5·변이·유료 호출은 이번 배정에 덧붙이지 않는다. 아래 명시한 기존 측정 meta 시험의 작은 native 자식 호출은 해당 meta 동작 확인에 한해 포함한다. TEMP/TMP/TMPDIR는 저장소 밖의 짧고 고유한 경로를 쓰고 기존 GIT_CEILING_DIRECTORIES를 보존·추가한다. 실행 중 제품/시험/미러를 수정하지 않는다. 시간은 소프트 기준이며 timeout으로 종료/성공 판정하지 않는다. 실제 command/cwd/필요환경·exit·원 report/stdout/stderr와 제출판 SHA를 보존한다. 선택과 실제 row, fixture, skip, source 변경 여부를 함께 판정한다.

공식 build_skill_mirrors.py로 자기 수정의 미러만 생성/check한다. .timings.json 등 이번 관측 캐시는 evidence에 보존 후 자기 base로 복원해 통합 대상에서 제외한다. 원 자료는 task/evidence 또는 저장소 밖 새 경로에 둔다. 변경 이유·직접 확인·한계·남은 문제를 report.json에 쓰고 check.py report C:/math/.async/dm g4-measurement를 통과시킨다. 공용 소스/문서/queue/state·다른 task·engine·graphify·기존 연구·공용 Git index/commit은 수정하지 않는다. 제품 설명을 바꿀 필요가 있으면 배정된 설명 파일에 실제 계약을 연결하고, 다른 task 소유 문서의 필요한 변경은 report에 정확한 심볼/내용으로 남긴다.

## 먼저 제거할 불필요한 제약

현재 async snapshot에는 Git 메타데이터가 없다. support.branch_gate.repository_root는 실제 git rev-parse --show-toplevel, write_index는 HEAD를 요구한다. 소스 해시를 올바르게 결속하는 기존 측정 계약 자체를 이 환경 차이만으로 바꾸거나 예외/가짜 commit/null HEAD를 추가할 이유는 아직 없다. 상위 C:/math Git을 사용하거나 ceiling을 해제하면 다른 판본을 자기 측정판으로 오인하므로 금지한다.

**이번 배정의 명시적 예외:** 자기 workspace 루트에만 독립 .git을 초기화하고, snapshot의 실제 제품·시험·문서 바이트를 로컬 기준 commit으로 기록할 수 있다. workspace의 .git이 자기 소유이고 상위 공용 Git과 분리됐음을 먼저 확인한다. workspaces.py는 .git을 snapshot/diff/integration에서 제외하므로 공용 소스로 이 메타데이터를 통합하지 않는다. 공용 Git·원자료·다른 task에는 commit/index 변경을 하지 않는다. remote/push/hook 실행은 필요 없다. 전역 Git 설정을 바꾸지 않고 필요한 식별/설정은 사본 로컬이나 한 명령 옵션만 사용한다. 초기화/commit 전후 제품 bytes를 대조하고 EOL/filter로 실행 소스가 변하지 않았는지 확인한다. 이미 자기 .git이 있으면 지우지 말고 상태/소유부터 확인한다.

이 예외는 측정의 Git 전제를 충족하기 위한 가역적인 사본 준비다. 과거 'task는 Gitcommit하지 않는다' 문장의 공용 코드 관리 목적은 유지하며 이 task의 자기 기준판에 한해 예외를 둔다. 자기 commit은 C:/math main commit도 검증 통과 표시도 아니다. 새 프레임워크나 서비스 snapshot 정책 변경, 제품의 Git 없는 fallback을 우선 만들지 않는다.

## 수행과 최소 확인

1. g4-general 실패 원문과 repository_root/write_index·run_tests의 측정 초기화·test_adapter_coverage native 자식 준비를 확인한다. 로컬 기준판의 root/HEAD와 제출판 해시를 결속하고 외부 임시 fixture가 이 root를 우연히 찾지 않도록 ceiling을 유지한다.
2. 위 준비만으로 원 실패의 원인이 해소되는지 기존 정확 meta 시험을 공식 실행기로 확인한다. fixture 오류 아래 2개 not_run도 실제 실행돼야 한다. 작은 기존 T3/T4 및 OS Job 자식 호출은 meta 시험이 요구하는 기존 범위에서 수행한다. 부모/자식의 실패·skip·미실행, adapter source denominator/worker publication 불완결, T3 gate/선택색인·store 분리를 모두 보존한다. 제품 코드를 바꿀 필요가 없으면 변경 없음으로 완료한다.
3. Git 준비 뒤에도 실제 결함이 남으면 writes 범위의 관련 구현·소비 시험과 필요한 확인을 같은 task에서 처리한다. 다른 원인에 대한 성공을 미리 선언하지 않는다. .selection-index/T3 캐시 등 측정 산출물은 원증거로 보존하되 제품 소스로 제출하지 않는다.
4. 후속 G4/G5 task가 그대로 재현할 수 있도록 자기 기준판 준비의 정확한 명령·필수 파일 범위·제품 bytes 불변·root/HEAD 의미·산출물 위치를 task/evidence에 짧게 남긴다. full T3 write_index의 HEAD 전제를 현재 코드로 확인하고 기존 작은 시험으로 충분한지 판단한다. 새 full T3 실행이나 전수 도달 감사는 하지 않는다. 기준판 존재와 fresh 전체 측정 성공은 별개다.

## 자원·권한·완료

동시 시험 슬롯 최대2개다. 외부 공식 선택은 --jobs 1로 실행하며 그 안의 native meta 시험이 --jobs 2를 쓰는 동안 다른 시험을 동시에 띄우지 않는다. 병행 g4-contracts의1슬롯과 총3이하를 유지한다. 선택으로 격리 모듈을 다른 병렬 parent worker와 겹치게 실행하지 않는다. 시간 때문에 작은 meta 시험의 모집단/반례를 줄이지 않는다.

runner/측정 helper와 직접 unit/경계 시험·시험-지침만 이 task의 제품 수정 범위다. 다른 do_math runtime·README/CLI 문서·doc_code/저장 helper는 g4-contracts 소유다. 필요한 설명은 측정 모듈 docstring/시험-지침 및 task 보고로 연결한다. 새로 생긴 actual 결함만 수리하며 사본의 Git 준비를 제품 변경처럼 보고하지 않는다. 조건부 WinError1314 outside_symlink는 이 task의 해결 대상이 아니며 호스트 권한을 바꾸지 않는다. 최종 G4/G5/G6/G7은 계속 열려 있다.

## 지정 실패 ID

- measurement_git_boundary
  - `unit.test_adapter_coverage.NativeAdapterTests.test_measurement_preserves_failed_skipped_and_unrun_test_outcomes`
  - `unit.test_adapter_coverage.NativeAdapterTests.test_missing_worker_data_refuses_runner_success_even_when_all_tests_pass`
  - `unit.test_adapter_coverage.NativeAdapterTests.test_parallel_t4_keeps_runner_job_bookkeeping_out_of_adapter_reach`
  - `unit.test_adapter_coverage.NativeAdapterTests.test_t3_t4_union_keeps_t3_gate_entries_and_store_separate`
  - `unit.test_adapter_coverage.NativeAdapterTests.test_t4_observes_in_process_and_owned_worker_without_writing_t3_outputs`
  - `setUpClass (unit.test_adapter_coverage.PublicationTests)`
  - `unit.test_adapter_coverage.PublicationTests.test_an_actual_worker_merges_and_zero_reach_files_keep_the_source_denominator`
  - `unit.test_adapter_coverage.PublicationTests.test_missing_corrupt_foreign_and_changed_source_publications_are_incomplete`

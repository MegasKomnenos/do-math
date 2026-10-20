# Git 게시 응답 유실 수리와 남은 core 경로의 확인

사용자의 목표는 결함을 놓치는 시험 기제를 줄여 현재 제품과 시험을 실제로 쓰게 하는 것이다. g5-target의 유효한 30파일 변경은 부분 수용됐지만, 정리 게시가 Git ref를 이동한 뒤 응답 오류가 나면 후속 저장이 오래된 head로 CAS 충돌하는 실제 결함이 남았다. 이 결함과 같은 core 수신·복구·적용의 미확인 질문을 한 task에서 수리하고 필요한 직접 확인·설명·미러를 마친다. 이미 해결한 질문이나 전체 관문을 반복하지 않는다.

## 입력과 범위

SESSION_JSON, task.json, 고정 inputs/context·plan·seams, 자기 workspace의 do-math AGENTS.md·시험-지침.md·이음새-정본.md와 managers/0097/review.md·verification-review.json을 읽는다. sources/t3-targeted-direction-2026-10-16.md·storage-scope-direction-2026-10-15.md·archive-resume-2026-10-16.md를 적용한다. 최신 T3 지시는 전체 실행보다 우선한다.

직접 선행은 수용 g5-target 하나다. 그 report/integration과 evidence/judgment.md·outside-scope.json·remaining-original-coordinates.json·gap-disposition.json·source-comparison.json을 소비한다. 정확한 원 반례는 t3-c-execution.json의 명령, outside-scope.json의 failure 경로와 cleanup-ack-regression-edition.py에 있다. 후자는 시험 모듈 전체의 당시 bytes를 보존한 자료이며 그대로 제품 전체를 덮는 패치가 아니다. 필요한 메서드/장면만 현행 시험에 옮긴다. 최종본으로 돌아간 test_core_branch_contracts.py의 원 archive/settlement 장면과 구별한다.

과거 제품 파일이 필요하면 공식 `python C:/math/services/async-development/workspaces.py restore C:/math/.async/dm TASK baseline|result NEW_DIRECTORY PATH...`로 필요한 경로만 복원한다. 원 task workspace/base 존속을 전제로 삼지 않는다. 원자료는 읽기 전용이다.

## 한 작업에서 마칠 결과

1. **Git 응답 유실을 실제 저장 경계에서 고친다.** 현재 `GitStateStore._compare_and_swap`는 backend.update_ref의 False에서 head 캐시를 비우지만 GitBackendError 예외에서는 비우거나 GitStateStoreError로 정규화하지 않는다. `_call`의 저장 오류/물리 경계 재확인 계약과 `snapshot`의 잠금 head 캐시 소비를 읽고 가장 작은 일관된 수리를 선택한다. 성공한 ref 갱신의 응답 유실은 미게시를 뜻하지 않는다. 예외 이후 authoritative ref를 다시 읽을 수 있어야 하며 원 수용 영수증·게시·정리 이력을 보존하고 후속 저장 및 재수신에서 정리 이력을 중복 생성하지 않아야 한다. False CAS 충돌과 게시 전 오류는 각 의미를 유지한다. core에서 private head를 조작하거나 모든 예외를 성공으로 삼는 우회는 하지 않는다.

   원 `PublicationRecoveryRules.test_cleanup_git_failure_keeps_the_accepted_response_and_records_its_remaining_owner`의 acknowledgment 장면은 실제 ref 이동 뒤 오류를 낸다. 이 정확 반례를 현재 fixture에서 복원하고 수리 후 accepted response, durable receipt, 정리 결과/남은 owner와 후속 저장을 확인한다. 현재 구현을 대역으로 바꾸지 않고 Git 포트에서만 외부 실패를 준다. 기존 archive/settlement 두 장면의 기대값은 유지하며 필요 이상의 모든 Git 장애 조합을 새로 만들지 않는다. 수리한 경계의 직접 일반 시험과 이 core 소비 시험이면 충분한 부분은 그대로 마친다.

2. **남은 core 질문만 처리한다.** remaining-original-coordinates.json은 원 전체판의 미관측 15 arc/16행을 일곱 함수에 연결한 자료이지 최종판 새 gate가 아니다. g5-target의 정적 의미 판단은 재사용하고 아래 남김에 실제 소비와 최소 시험이 필요한 곳만 보완한다.

   - `_retry_submission_publications`: 예외 복구 시 live publication wait도 output_accepted도 아닌 경로. 기존 실패한 returned-settlement clock fixture를 그대로 반복하지 말고 현행 생산/전이에서 실제 도달 가능한지 먼저 판단한다.
   - `_validate_bundle_current`: source_basis/decision_basis 구별, 같은 revision의 academic 요구 hash 변경, 지급 외 추가 authority_refs의 현재 권한. 현재성·권한 검사를 숫자 때문에 제거하지 않는다.
   - `_receive_submission`: feedback 파일 OSError, 수용된 repair 뒤 로컬 정산 오류와 cleanup 이력 중복 제외. Git 응답 유실 수리/직접 장면이 해결하는 부분은 재사용한다.
   - `_finish_native_recovery`: 같은 activity의 ready 후속이 이미 남은 진입. 기존 recovery choices의 충분한 입력/성질을 재사용한다.
   - `_apply`: formal 환경 부재, 현재 개정 상태, delegated revision_request_action_id 보존, 현재 의존 순환, candidate kind 후속. 실제 producer와 현재 경계를 유지한다.
   - `_complete_operational_disposition`: 미확정 로컬 종료와 최신 checkpoint 불일치의 반려.
   - `_apply_plan`: 외부 issued_input의 snapshot/ready_task_ids 불일치 반려.

   정적 읽기로 불가능함을 입증한 중복 분기는 현행 모든 관련 생산/소비와 함께 줄일 수 있다. 유효 경로에는 독립 기대값과 기존 fixture를 이용한 필요한 직접 입력을 준다. 내부 메서드 대체, 도달만을 위한 불가능 상태, skip/no-cover/분모 변경은 하지 않는다. 한 입력의 여러 단언으로 충분하면 쪼개지 않는다. 실제 외부 조건이 없어서 확인할 수 없는 경우 정확한 조건을 남기고 독립 수리를 완료한다. 원39arc/43행 전체를 다시 감사하거나 이미 성공한 g5-target 장면을 모두 재실행하지 않는다.

3. **직접 관련 설명과 공식 미러를 함께 마친다.** 초기화-효율과-정비의 현재 Git 응답 유실 미해결 설명은 수리된 실제 계약과 남김에 맞게 교체한다. 필요하면 과제-착수조건/이음새-정본의 관련 부분도 갱신한다. 새 옵션·계측 의미를 도입하는 작업이 아니므로 시험-지침은 병행 g6-inputs 소유로 유지한다. 공식 build_skill_mirrors.py를 사용하고 허용 밖 변화는 제출에 섞지 않는다.

## 필요한 확인과 판본 인계

시험은 자기 workspace의 공식 run_tests.py로 jobs1·한 명령씩 실행한다. 우선 가장 작은 반례/수리 확인을 선택한다. 추가 T3가 필요한 부분은 지정5모듈 중 core의 남은/변경 경로를 직접 소비하는 유한한 시험 ID/모듈만 새 외부 store/output으로 측정한다. Git 경계의 직접 일반 시험과 core 소비 T3를 구분하고 git_store 전체의 새로운 coverage 의무를 만들지 않는다. 전체 일반/T3/T4/T5/변이 재실행은 배정하지 않는다. 새 T3에는 위치 선택 또는 정확 --match를 반드시 사용한다.

부분 T3는 closing_eligible=false이고 전체 index를 갱신하지 않는다. 기능 결과·관측 exit·미도달을 분리한다. 원전체+g5-target+이번 추가 결과의 통과 수를 합치거나 원 coverage/store/index를 편집하지 않는다. source/AST/body와 좌표가 바뀐 영향은 기록하되 좌표 대응을 새 도달로 주장하지 않는다. 환경6arc/10행은 기존 WinError1314/POSIX 입력 부재를 유지하고 새 권한·설치·환경 probe로 우회하지 않는다. 충분한 A22 공통 codec/저장/업무 보장을 재사용하며 가족별 quota·장기 감사를 만들지 않는다.

병행 g6-inputs는 mutation 명시 선택·decorator 직접시험·그 시작판의 모집단/선택을 준비한다. 서로 미완성 사본을 소비하거나 그 task의 mutation/trace/지침 파일을 수정하지 않는다. 이 task는 자기 최종 source SHA·변경 함수/시험/helper·필요 선택 ID와 원색인의 영향만 evidence에 남긴다. 두 수용판이 합쳐진 뒤 **G6 실행자가 실행 준비 안에서 해당 delta만 반영**한다. 별도 재준비 task나 전체 T3가 필요하다고 전제하지 않는다. 전체 pseudo_tested.json을 이 task에서 게시하지 않는다.

쓰기 범위는 task.json의 core/git_store, 지정 직접 시험과 한정 support 파일, 관련 설명과 미러다. 허용 목록의 모든 파일을 수정할 의무는 없다. 다른 runtime 제공자 수정이 실제 필요하면 최소 경계·원 반례·영향을 보고한다. TEMP/TMP/TMPDIR/output은 고유한 짧은 저장소 밖 경로, GIT_CEILING_DIRECTORIES는 기존 값을 보존하며 자기 부모/임시 root를 추가한다. PYTHONDONTWRITEBYTECODE를 자식에도 적용한다. 실행 중 source를 고정하고 생성 cache/index는 원증거를 보존한 후 baseline.json/objects의 시작 bytes/부재로 복원한다. 공용 Git·전역 설정·실모델·예약·외부 설치물은 변경하지 않는다.

## 제출

evidence/judgment.md에 원 반례→수리→직접 관측, 재사용한 기존 보장, 정확한 남김과 G5/G6 한계를 적는다. 실제 argv/cwd/환경/exit·원report·source SHA와 최종 source/선택 delta를 보존한다. report.json을 작성하고 `python C:/math/services/async-development/check.py report C:/math/.async/dm g5-remainder`를 통과시킨다. 공용 context/plan/seams/queue/state와 graphify는 수정하지 않는다.

# 공용 인터페이스와 작업 사본의 경계

## 현재 갱신: 0108 G8 수용과 Git 인도·외부 입력 경계

공용제품은 g6-finish 통합판이다. tasks/g6-finish/integration.json 및 evidence/final-edition.json·manager0105/verification-review.json이 실제판본을 연결한다. 정본36·미러36 수리와 공식1388파일 mirror check는 수용됐고 g1/g23-close는 제품변경0이다. 미수용/취소 g6p-run의 원자료와 부모미완료repair-b09는 완료로 승격하지 않는다.

`scripts/tests/support/mutation.py:run(..., function_selectors=())/main`은 반복 `--function scripts-relative-module:qualified-function-key`를 제공한다. `functions/changed_functions`의 중첩·반복이름 #n을 그대로 사용한다. layer1~3·--only·변경함수 범위에서 모든키가 해석돼야 child를 시작하며 --every는 변경없는함수도 포함한다. 오타/없는키/범위밖은 `_FunctionSelectionError(ValueError)`·CLI usage exit2, 일반base오류는 기존exit1이다. 생략시 기존선택·index ordinals+explicit_tests 합집합·fallback·cheap-first/failfast·정상확인·jobs1..3합계상한을 유지한다. 보고 function_selectors는 중복제거된정확키다. update_list는 실제 killed/survived만 소비하고 선택밖entry/사유를 보존한다. pseudo_tested.json의 LocalCLIAdapter.provider_failure는 무조건None/pass 동등1개다.

`tests/support/sim.py:warm_template/_template`는 Future에 준비결과/원오류를 한 번 보관하고 소비자가 읽거나 같은오류를 받는다. 실패준비를 재시도하지 않는다. `Sim.activate`는 실제run(max_steps=32, until_active=True)와 기존active/formal미호출단언으로 합성초기화를 한정한다. AcademicStoragePairs/EventStoragePairs의 실제생산/순서는 유지하며 소비시험본문에서 준비한다. `port_contracts/jobs.py`의 정리는 `run_tests.wait_for_worker`를 쓰고 제품termination_confirmed를 직접 검사한다. `provider_runs.collector_request`는 수집/Job수명시험의 공통요청생산자다.

현재 원30의무 연결 정본은 `tasks/g1-close/evidence/obligation-state.json:rows`다. 원ID/원문·requirement_property·accepted_basis는 이전수용의미를 보존하며 `prior_handoff`는 당시상태, `delta_connections/delta_assessment/semantic_disposition`은 현재영향/재사용판단, `remaining/next_conditions`는 정확남김을 나타낸다. `handoff_is_requirement_closure=false`이며 연결완료를 전체충족으로 해석하지 않는다. `accepted_delta_connections`의8묶음·`later_task_evidence`의14개 연결이 실제수용변경과현재producer/consumer/직접시험을 잇는다. manager0107은 영향12파일의현재공용/고정사본/baseline/인용SHA를 대조했다. AST177심볼/207참조는worker검수를 재사용한다.

`g1-close/evidence/gate-state.json`은 G4원전체성공/최종판단일전체보고부재, G5원전체/지정추가/환경6arc10행과부분도구제약, G6판본별1677처분, G7원T4/정확3수리·유효실경계/외부원자료, L01기존Q1/Q2·원UTF-8출력byte, G8미수행을 구별한다. G2_G3.outside_this_assignment는 해당worker의범위이며 현재프로젝트에서는 g23-close연결을0106이수용했다. edition-delta.json·post-g45-python-delta.json·post-g4-focused.diff는 G45이후직접영향을 설명한다. preserved-long-evidence.json의58passed는 원실행판이지 현재core/Sim의새LONG실행이 아니다. 원G4요구를 면제하거나 여러판의성공을 새전체성공으로 합치지 않는다.

G23 정본은 `g23-close/evidence/preservation-state.json:rows`(K61/P2 12), `prior-review-state.json:review_units`(PR25/109slice), `accepted-delta-connections.json:deltas`다. 기존72한정검토·이후37hunk판단·기반1a/1d9질문 및1b/1c17질문을 수용범위로 재사용한다. connection_complete는연결완료이고 whole_*인증은false다. reference_roots.repo의옛g23-handoff경로는보조metadata이며 current_*는조사한수용판에해석한다. 상속storage_scope의'최종freshT3'보다 final_gates.G5.next와사용자2026-10-16지시가우선한다.

g8-review의 `evidence/gate-verdicts.json:gates`는 G1~G8별 수용범위·유효판본·정확남김·다음조건을 제공한다. `report.status=complete`는 review 배정 완료이며 `project_goal_complete=false`다. manager0108은 무변경 integrate 후 수용했다. 기존 G1/G23 연결의 의미와 원실행 판본을 재사용하며 현재 검토의 한계를 확대하지 않는다.

`managers/0108/delivery-manifest.json:files`는 Git 제품2168개 각각의 `reviewed_sha256`, `git_blob`, `git_blob_sha256`, `relation`, `newly_staged`를 정의한다. `relation=exact`는1838개, `CRLF-to-LF-only`는330개다. Git 제외 생성자료268개는 `excluded_generated_files`에 따로 있으며 로컬에 보존한다. 이것은 실행결과나 새전체시험 인증이 아니라 인도 판본의 관계다. 실제 main 커밋은 `cbc7581b6ca80e216b1d188d1811aa94d2e538bc`이며 `delivery-state.json`이 commit 후 경로범위·제품diff0·신규미추적0·원바이트불변을 기록한다. 기존 G8 `delivery-state.json`의 옛 HEAD/미커밋 수치는 review 당시 관측으로 보존한다.

남은 G4 조건은 원최종판전체와 최신 정확회귀범위의 권위있는 처리다. G5는 실제환경6arc10행·부분index/store제약, G7/L01은 현지원원자료·기존Q1/Q2·delivered-output byte 계약/수신 조건을 소비한다. 현재 조사host를 운전자로 지정하거나 내부 input.txt hash를 실제도구 출력byte로 대체하지 않는다. 외부입력이 도착하기 전 반복질문/probe/전체실행을 배정하지 않는다. 제품무변경 인도만으로 work/review를 다시 만들지 않는다.

과거코드는 공식restore로 필요한파일만 새경로에 복원한다. 정리될workspace를 영구근거로 쓰지 않는다. 이번커밋에 선택한 결론/manifest 외 전체raw와objects는 로컬기록이며 별도보존 대상이다. 아래0104이하는 당시이력이며 현재판단은0108과 실제원문을 따른다.

## 0104 당시 갱신: 후보 이식·개별 결과·정확 선택의 경계

공용 runtime/시험은0101 mutation-parallel 수용판이다. g6p-run의 미완성수리는 아직 공용에 없다. managers/0104/candidate-manifest.json의 canonical_files는 baseline/source/result SHA와 candidate/보존파일을 연결한다. g6-finish는 새baseline과 대조한31정본만 자기사본에 이식하고 공식생성기로미러를 만든다. 옛생성index/timings/.hypothesis/listing·중간미러와 사본전체는 이식입력이 아니다. 원g6p-run은 cancelled·미수용으로 그대로보존하며 workspaces.integrate/accepted는 새task의 실제최종변경 검수뒤에만 처리한다.

현재 scripts/tests/support/mutation.py:run/main의 --only는 모듈glob이고 --test는 유효index선택과 합집합을 이루는 정확시험ID다. 함수별선택은 아직없다. g6-finish가 기존경로에 반복 --function scripts-relative-module:qualified-function-key와 같은의미API를 추가한다. 기존 functions/changed_functions의중첩키를 그대로소비하고 선택범위/존재를 child시작전에확인한다. 선택밖함수를 실행하거나 오타를 전체fallback/0건성공으로 바꾸지않는다. 이는 새배정의구현계약이며 이미수용된기능이 아니다. 기본동작·cheap-first/failfast·실패후보정상확인·jobs합계/중단/exit의 기존의미를 유지한다.

mutation.update_list는 killed로실제로보고된키만제거하고 survivor를추가한다. 정확함수선택은 다른기존entry를지우면안된다. parent미완료인repair-b09의listing미갱신을 실제함수실패로혼동하지않는다. managers/0104/remaining-functions.json은 원32문제의해결10·동등1·pending21을각출처와연결한다. 원1613killed/32trivial는기존판본/선택과assess-main/execution-summary를재사용한다. 원population/index는전수재생성하지않는다.

repair-b09의세문제함수는 managers/0104/evidence/repair-b09의mutant-0015/0021/0041과normal-0007/0010/0023(실제디렉터리명unmutated-*)에보존됐다. outcome.attempts[].baselines는정수ID이며이름/완료순서로추정하지않는다. 실제attempt.exit_code=0/finished, mutant비fixture실패row와정상passedrow의killed_by대응을0104가확인했다. 부모mutation.json/exit부재는그대로남으며개별함수만재사용한다. verification-review.json의보존manifest가원경로/SHA를제공한다.

candidate의support.sim warm_template/_template는Future로준비결과/원예외를실제소비자에게전달하고재시도를막는다. 합성Sim.activate는max_steps32와기존active/미호출단언을함께쓴다. AcademicStoragePairs/EventStoragePairs는기존실제생산/순서/표본을본문에서소비한다. port_contracts.jobs는run_tests.wait_for_worker로정리하고제품termination_confirmed는직접단언한다. 이는후보설명이며공용계약변경수용은새task통합시확정된다. 새로운가족별저장입증이나일반fixture프레임워크는없다.


제품의 정본은 각 workspace 안 `.claude/skills/do-math/scripts/do_math/`의 실제 정의와 `.claude/skills/do-math/scripts/tests/contracts/`, `.claude/skills/do-math/scripts/이음새-정본.md`다. 기존 상세 연결과 변경 이유는 sources/legacy/seams.md에 보존했다. 그 원문 속 run: 경로는 이전 실행 기록 루트 기준이다. 초기 세 읽기 작업 사이에 새 제공/소비 API는 없다.

- R02는 현재 역할 요청 생산자와 worker/정본 schema 수신자를, R07은 test_schema_builders의 실제 반환 경로와 소유 모집단을, R18은 현재 adapter/real port 호출과 실제 배선을 기존030 objective의 정확한 심볼로 연결한다. 서로의 미완성 결과를 소비하지 않는다.
- 새로운 인터페이스가 필요한 작업에서는 실제 정의의 파일·심볼, 입력·출력·실패·부수 효과와 소비 책임을 먼저 적는다. 기존 정의를 별도 문서 schema로 재발명하지 않는다.
- source_repo는 C:/math이고 manager가 통합하는 공용 판본이다. task는 workspace만 수정한다. task의 시작 inputs와 baseline.json/objects가 수행 중 고정되고(새 task에는 base 디렉터리가 없다), manager의 다른 결과 통합은 이미 실행 중인 workspace를 바꾸지 않는다.
- manager는 workspaces.py integrate의 충돌 결과를 존중한다. 같은 파일이 양쪽에서 달라졌다면 원본을 덮거나 workspace를 공용 소스에 통째로 복사하지 않고 필요한 조정 작업을 배정한다. 승인한 무변경 조사도 integrate의 변경 없음 기록 뒤 accepted에 넣는다.
- 정본 스킬과 대응 미러는 같은 task의 쓰기 범위에 함께 둔다. 공식 생성기가 자기 workspace에서 예상한 범위만 바꾸는지 확인한다. 공용 판본의 snapshot과 integration을 serialize하는 source.lock은 서비스가 관리하며 세션이 삭제하지 않는다.
- 실제 외부 자원·최종 전체 관문의 공유 경계는 manager가 충돌 없이 배정한다. 독립 workspace의 소규모 검증은 각jobs1로 수행할 수 있고 총시험worker3 이하를 유지한다. 제품 의미·판정·원자료 무결성을 줄여 속도를 맞추지 않는다.

## 0101 당시 갱신: 병렬 변이의 제공·소비 계약

`scripts/tests/support/mutation.py:MAX_JOBS/validate_jobs/run/main`은 CLI --jobs 1..3/API run(..., jobs=1)을 제공한다. 기본1이고 bool/범위밖/비정수는 거절한다. ThreadPool의 함수 계획 하나는 변이 또는 정상 child 하나만 소유하므로 명령 내 합계가 jobs 이하이다. 동일 정상 선택(tests/folders/exclude)은 lock 안에서 Future 하나를 설치해 실제 실행을 공유한다. source·시험·index·timings를 고정한 명령 안에서만 유효하며 별도 baseline pool·명령간 cache는 없다. 기존 선택 합집합·fallback·cheap-first/failfast·실패후보 정상 확인·오류 분류를 유지한다.

`mutation._child_run`은 `do_math/windows_job.py:WindowsJob`으로 suspended child를 소유하고 초기 attempt/PID를 쓴 뒤 resume한다. `run_tests.py:wait_for_worker(job, *, pause=None, cancelled=None)/worker_exit_code(job)`가 root·후손 종료와 실제exit의 공통 정의다. 취소 Event는 CancelledError를 내며 소유자가 Job terminate 뒤 취소 없는 대기로 종료를 확인한다. 시간에 따른 종료는 없다. child별 scratch/TEMP와 spec/result/attempt/output을 분리하며 main의 child 경로가 Python/native stdout/stderr를 보존한다.

`mutation.run`은 새/빈 output만 받는다. mutant 번호와 outcomes는 함수 계획 순서, baseline ID는 보고 안 최초 요청 순서다. 완료 outcome.json과 mutation.json의 jobs/interrupted, outcomes[].attempts[].baselines를 실제 연결에 쓴다. 부모가 join 뒤 update_list를 한 번 호출한다. 명시 중단은 interrupted=true·미완료 execution_error·passed=false·listing불변이다. 내부 예외나 부모 강제종료는 최종 mutation.json이 없을 수 있다. 원attempt/output을 보존하고 새 output에서 미완료 묶음을 실행하며 자동 함수재개/보고병합은 없다. 다른 완결batch의 재사용은 source·선택·정상·exit 유효성 판단을 필요로 한다.

`run_tests.py:_finish_t3`는 mutation-base 사용시 같은 args.jobs를 변이에 전달하고 T3 진입 전에1..3을 검사한다. 호출부 일치 설명이며 이번 전체T3 실행 또는 후속 전체T3 허가가 아니다. `tests/boundary/test_mutation_baseline.py:ParallelMutationTests`가 실제 child 동시수·동일판정·정상공유·native 출력·중단 후 후손 종료를 소비한다. 작은 fixture와 최종 제품 G6는 별개다.

새 소비자 g6p-run은 managers/0101/execution-arguments.json의20argv와 tasks/g6-run/evidence/population.json의 함수/선택을 소비한다. g5-remainder의15고유ID는 이 중단판 준비에 이미 들어 있다. 원4515시험 index SHA3d30a04e/commit4dae8591을 그대로 쓰고 실제 자기Git ancestry를 준비한다. 한 명령씩 --jobs 3을 쓰며 단일 listing/미러 소유자가 필요한 수리와 확인을 마친다. 기존0100의 doc_code 함수 표기 실패는 이 task에 묶고 원 b01은 읽기 전용이다. 영구 입력은 evidence/report/integration 및 보존 객체이며 과거코드는 공식 restore로 필요한 경로만 복원한다.

## 0100 당시 갱신: 중단 결과와 개선판 소비 경계

현재 실행 개선의 소유자는 mutation-parallel이다. 기존 `scripts/tests/support/mutation.py`의 실제 child 실행·정상 memo·cheap-first/failfast·명시 선택 합집합·오류 분류·pseudo_tested를 검토하고 필요한 변경을 그 task 범위에서 구현한다. 새 병렬 CLI/API와 기본값은 아직 수용되지 않았으므로 이 문서에서 가정하지 않는다. 총 mutant/normal child 상한은3이며 단일 결과 작성 또는 명시 병합, 독립 attempt/정상 결과, 실패/중단 시 자식 정리가 후속 사용 계약의 일부다. 수용 뒤 실제 심볼·입출력·실패 의미를 이곳에 연결한다.

`tasks/g6-run/evidence/population.json`·`static-check.json`·`source-snapshot.json`은 중단 작업의 준비 입력이며 수용된 실행 결과가 아니다. 원색인 SHA3d30a04e와 g6-inputs/g5-remainder의 입력delta를 재사용할 출발점이다. `b01-execution.json:exit_code=null`이며 최종 batch 보고/원 evidence 복사는 없다. manager0100이 외부 원출력40파일을 `managers/0100/evidence/g6-run-b01/`에 동일 바이트로 보존했다. 목록·SHA·attempt 요약은 verification-review.json, 후속 책임은 handoff-delta.json이다. 원 외부경로와 취소 workspace는 그대로 보존된다.

`unmutated-0001/attempt.json`은 exit0과 tests_run1·row failed를 함께 가진다. 프로세스 exit만으로 정상 통과를 판단하지 않는다. `mutant-0004/attempt-0001/attempt.json`은 exit4294967295·result null·파일부재를 기록하며 사용자 중단이다. mutant-0005의 result 존재는 관측 exit를 대신하지 않는다. 실패·부재·중단은 killed가 아니며 이후 완료 근거로 변환하지 않는다.

`scripts/tests/support/doc_code.py:unowned_field_references`는 backtick 안의 dotted field에서 namespace 소유권을 검사한다. 같은 파일의 `function_reference_issues`는 `module.function(...)` 표기를 실제 callable로 검사한다. `references/과제-착수조건.md:89`의 `submission.payload_issues` 표기가 전자의 입력으로 들어가 `unit/test_storage_report_projections.py:ReportProjections.test_human_report_preserves_loaded_initialization_blocker_and_machine_finding`의172행을 실패시킨다. `scripts/do_math/submission.py:payload_issues`는 존재하고 관련 네 파일은 공용판/중단판 SHA가 같다. 후속 G6는 기존 표기 계약으로 문서/미러를 보완하고 해당 정상 기준을 재확인하며 검사 약화나 제품runtime 우회는 추가하지 않는다.

기존0099 Git 오류 경계와 원 G6 delta는 유지한다. 새 G6는 개선 수용 뒤에만 배정하고 실제 옵션·동시 child 제한·결과 통합 방식을 소비한다. 아래0099의 g6-run 즉시실행·child1은 중단 전 이력이다. 부분T3/원index의 제약, 지정5모듈 추가만 허용하는 지시와 나머지 관문은 변함없다.

## 0099 당시 연결: Git 오류 경계와 G6 delta

`scripts/do_math/git_store.py:GitStateStore._compare_and_swap(new, old, operation)`는 유일한 ref 이동 경계다. 잠금 head 캐시를 먼저 무효화하고 `_call("update_ref", self.ref, new, old)`을 호출한다. False는 물리 경계를 재확인한 뒤 GitStateStoreConflict, GitBackendError는 기존 `_call`의 동일 경계 확인 뒤 GitStateStoreError다. 성공 응답을 관측한 CAS만 잠금 중 캐시를 채운다. `read_snapshot`은 캐시 부재 시 실제 ref/object를 조회한다. 성공 응답 유실을 성공/미게시 중 하나로 단정하지 않는다.

`core_engine.py:CoreEngineMixin._receive_submission`의 cleanup 수신은 typed 저장오류에서 `_reload()`로 실제 게시 상태를 읽고 미게시된 cleanup 이력만 보충한다. 원 수용 영수증·삭제 사실·잔여 owner를 보존하며 같은 제출 재수신은 원receipt를 사용한다. 이 소비자의 bytes는 선행 g5-target과 같고 새 provider 수정이 기존 오류 처리를 실제 연결한다. `tests/unit/test_git_state_store.py:GitStateStoreTests.test_ref_update_error_rereads_the_head_and_allows_the_next_publication`와 `test_core_branch_contracts.py:PublicationRecoveryRules.test_cleanup_git_failure_keeps_the_accepted_response_and_records_its_remaining_owner`가 직접 소비한다.

`tests/support/submission_receiver.py:history(*, bound=False, sim=None)`는 선택한 Sim의 실제 공개 source/grant 판본을 입력snapshot 이전에 준비하게 한다. `tests/support/core_remaining.py:operational_scene(sim, target, disposition)`는 실제 등록/문맥/schema/설치·중앙캡처/영수증을 사용하는 role 수신 장면이며 reviewer native process를 실행한 증거가 아니다. 새 직접시험은 원 현재성·권한·개정/순환·학술요구·정산/종료·issued input 검사를 유지한다.

`tasks/g5-remainder/evidence/G6-delta.json:required_additional_test_inputs_by_function`은8함수 연결과15고유 시험ID를 제공한다. runtime AST 변화는 git_store의 CAS 하나이고 core bytes는 불변이다. `source-delta.json`은 함수body/좌표·시험/helper 차이, `final-source-sha256.json`은 해당 작업판 SHA다. `inherited-gap-observations.json`의15arc/16행은 성공한 부분측정의 원좌표 관측이며 전체coverage 합집합이 아니다. cleanup-b/final-core/recovery는 각각 기능성공과 closing_eligible=false·branch_gate=false·exit1을 함께 가진다. helper docstring과 CRLF 변경의 재사용 근거는 passing-edition-reuse.json·newline-restoration.json이다.

g6-run은 이미 수용된 g6-inputs의 원색인/명시 선택/20argv와 위 delta를 자기 시작판에 반영한다. 원4515시험 SHA3d30a04e·commit4dae8591 index는 보존하고 명시ID를 관련 `--only` 모듈 묶음의 반복 `--test` 합집합으로 보충한다. 해당모듈의 이웃함수에도 명시ID가 적용되는 기존 CLI 의미를 유지하며 측정ordinal로 바꾸지 않는다. 단일 소유자가 pseudo_tested·명령/child1개·관련 수리를 맡는다. 전체T3/새색인병합/전수재준비는 필요 선행이 아니다. g5 작업판과 두 수용판을 합친 source를 구별한다.

환경6arc/10행·부분T3의 전체index 미갱신/자동store재사용 한계와 나머지 최종관문은 그대로다. 영구근거는 evidence/report/integration 및 baseline/result 객체이며 정리된 workspace는 필요파일만 공식 restore한다. 아래0098이하는 당시연결이다.

## 0098 당시 연결: 명시 선택과 G6 실행 인계

`scripts/tests/support/mutation.py:run(..., only=(), every=False, listing_path=PSEUDO_TESTED, explicit_tests=())`와 `main --test ID`가 실제 제공된다. 비어 있지 않은 only 범위가 필요하고 정확한 unittest 메서드 ID를 반복 입력한다. 각 대상 함수에 `tests_for`의 원색인 선택과 명시ID의 합집합을 적용하고 layer-folder fallback을 유지한다. 중복은 제거하며 기본호출은 기존 선택을 쓴다. `outcomes[].selection`의 indexed_ordinals/explicit_tests는 출처, tests/folders는 실제 입력이다. 명시ID는 측정 ordinal/진입이 아니다. 수집/실행 누락과 정상 결과 부재는 기존 `_evidence_error`·baseline 판정으로 남고 실제정상passed만 killed를 확인한다.

`do_math/operation_trace.py:measured/engine_operation` 및 각 decorate는 runtime 불변이다. `sim/test_engine_operation_trace.py:OperationTraceTests.test_measured_factory_preserves_return_and_exception_and_records_the_phase`와 `sim/test_engine_trace_failure_paths.py:TraceFailureTests.test_engine_operation_factory_preserves_body_and_binds_trace_to_instance`가 실행 중 factory/decorate를 호출하며 원반환/동일예외·phase/instance와 context 정리를 소비한다. 원색인 네 무진입키를 직접시험 입력으로 보충하며 원index를 바꾸지 않는다.

`tasks/g6-inputs/evidence/population.json`의 modules[].functions는 현재 source/AST/body·선택 참조·explicit_tests·execution_status를, batches[].arguments_from_workspace_root는 유한20argv를 제공한다.123모듈/1677함수·1393원참조는 준비판이며 전부 not_run이다. b08/b19/b20의 명시 입력은 해당모듈 이웃함수에도 적용된다. `selection-impact.json`의 본문4/좌표이동72·영향1591선택과 input/import closure는 기존판 영향 설명이며 새 도달 인증이 아니다. 원측정 index는 population.index.path/SHA3d30a04e/commit4dae8591/4515시험이고 기본bd3ae53f/2163시험판과 구별한다.

g6-run은 수용 g5-remainder의 report/integration/최종근거와 자기 시작판 delta만 이 입력에 반영한다. `selection.read_index/usable/is_ancestor_of_head`를 자기 실제 Git에서 확인하며0095 bundle과 raw-byte 설정을 사용한다. 자기 생성index에 보존bytes를 배치하고 종료시 시작bytes/부재로 복원한다. source/index/cache/원보고 판본을 구별하며 원자료는 편집하지 않는다. 단일실행자가 pseudo_tested를 소유하고 한 명령/child씩 수행한다. `mutation.update_list/passed`의 기존 의미와 원설계6.3/A24의 동등변이 사유 제한을 함께 적용한다. 비동등 survivor·오류는 직접수리/필요한 재확인 또는 정확한 남김으로 이어진다.

진행 중 GitStateStore/core 수리는 아래0097의 미완료 연결 그대로다. 새결과가 수용되기 전에 수정완료로 취급하지 않는다. G5 부분T3/전체index 미갱신·store 자동재사용 한계도 유지한다. 작업자 사본은 정리될 수 있으므로 영구입력은 task의 evidence/report/integration과 baseline/result 객체이며 필요한 과거파일만 restore한다. 아래0097이하는 당시연결이다.

## 0097 당시 갱신: 부분 측정과 Git 게시 후속

CoreEngineMixin._retry_submission_publications는 call_engine._receive_call의 release_or_hold 또는 committed goal-audit의 확인된 local termination/정산 뒤 만들어진 wait를 소비한다. SessionSlots.release는 이미 confirmed인 capacity를 재사용한다. 이번수용은 정산호출을 유지하고 그False중복분기만 줄였다. _recover_disappeared의 별도재관측/실패장벽은 유지한다. submission._payload_issues의 task_conditions가 정확한title/revised ID를 결박하므로 _apply의 같은목록검사를 줄였고 현재개정상태/조건평가/순환검사는 유지한다. contracts.disposition_schema와 세caller가 _complete_operational_disposition의 마지막user_decision을 한정하며 lifecycle저장enum은initializing/active/paused다.

현재 GitStateStore._compare_and_swap는 backend.update_ref를 직접호출한다. False에서는 boundary확인·_held_head무효화·GitStateStoreConflict가 있지만 GitBackendError경로에는 캐시무효화/typed오류정규화가 없다. _call의 저장오류/경계재확인계약과 snapshot의잠금head소비를 함께보아야 한다. 원ref갱신 뒤 응답유실은 미게시가 아니며 core._receive_submission cleanup catch가 실제게시를재조회할수있어야 한다. g5-remainder가 이제공자와 소비회귀를 함께고친다. 현재 API가 이미 고쳐졌다고 취급하지 않는다. 정확반례는g5-target/evidence/outside-scope.json·cleanup-ack-regression-edition.py다.

g5-target의remaining-original-coordinates.json은 core일곱함수 원15arc/16행과 환경6arc/10행의 미확인목록이다. gap-disposition/source-comparison은 원좌표→최종함수/판본 대응이며 새로운coverage/gate가 아니다. 추가a~f의실제argv/exit/source는각execution.json, 원report/행은audit.json이다. final-source와runtime-editions는기록아래보존되며 정리될workspace를 영구입력으로쓰지않는다. 부분T3의선택universe/plan.reuse와closing_eligible=false·전체index미갱신계약은 그대로다. helper top digest와함수좌표변화의자동재사용한계도 유지한다.

g6-inputs는기존mutation/trace직접시험/시험지침만, g5-remainder는core/git_store·지정소비시험·참조설명/이음새만수정한다. 두쓰기목록은교집합0이며시작사본은독립이다. g6-inputs의population은자기시작판기준이다. 두결과뒤G6실행자가최종source를고정하고새수리의함수·시험·입력delta만기존population/정확argv에반영한다. 명시선택은관측진입이아니고 부분T3를전체index로바꾸지않는다. 전체listing은후속단일실행자소유다.

## 0096 당시 갱신: 함수 모집단과 명시 선택의 후속 경계

tasks/g6-scope/evidence/population.json의 modules[].functions는 mutation.functions의 qualified key/#n·정의행·source/AST/body SHA·rule/trivial·selection_set을 담는다. selection_sets의 원index file/function 참조로 ordinals와 실제 test ID를 해석한다. batches는123모듈을 중복 없이20명령에 배정한다. 현재1677함수/1645비trivial은 고정판의 수이며 수용diff 뒤 무조건 유지할 quota가 아니다. 모든 실행상태는 not_run이다.

mutation.tests_for는 진입 ordinals가 있으면 blob 변경에도 기존 선택을 쓰고, 키가 없으면서 blob이 같으면 not_executed, 달라지거나 entry가 없으면 layer fallback이다. operation_trace.measured(193)·그 decorate(195)·engine_operation(204)·그 decorate(205)는 같은 blob의 원index에 키가 없다. import 때 factory 구성과 wrapper 시험 진입은 다른 관측이다. 현 CLI의 --only는 모듈 glob이고 명시 시험 입력은 아직 없다. g6-inputs가 이 입력과 직접시험을 구현하며 현재 제공되는 API로 미리 취급하지 않는다.

원색인 경로/SHA는 g45-final/evidence/G6-inputs.json의 preserved_selection_index이고 commit4dae85911f26f891fc3d79be9916bf4363e2d46f/4515시험이다. 기본 tests/.selection-index.json의bd3ae53f/2163시험 자료와 구별한다. selection.usable/is_ancestor_of_head는 실행자 자신의 실제 Git ancestry를 검사한다. managers/0095/index-baseline.json·g45-index-baseline.bundle은 원commit 객체를 보존하며 최종 제품 snapshot이 아니다. 자기 Git에서 실제원객체를 fetch하고 현재bytes를 보존하는 준비안은 g6-scope/execution-plan.md에 있다. 실행 실험은 아직 없고 raw-byte blob에 필요한 '* -filter -text -ident' 계약도 유지한다.

run_tests._t3_plan은 선택 시험모듈을 universe로 삼고 _finish_t3는 plan.reuse만 결합한다. 부분T3는 전체index를 쓰지 않고 closing_eligible=false다. t3_store.code_digests는 본문과 위치를 보므로 줄이동도 구arc재사용을 무효화할 수 있다. g5-target은 지정5모듈의 관련시험만 추가 측정하고 원전체의 유효 범위·추가판본·한계를 인계한다. g6-inputs는 그 수용diff와 g6-scope의 함수판본/입력readers/import closure를 소비해 영향범위만 갱신한다. 이번 명시 선택은 원자료의 관측된 진입으로 기록하지 않는다.

g6-inputs는 mutation.py와 직접 unit/sim/boundary 시험·시험지침·미러를 소유한다. runtime·selection/branch_gate/run_tests·층목록은 바꾸지 않는다. 선행 g5-target과 공통 쓰기를 겹치지 않도록 수용 뒤 시작한다. 한정 확인의 생성 index/cache/listing은 시작판으로 복원하며 전체 pseudo_tested 게시권은 후속 단일 G6 실행자에게 있다. 정상실패/skip/수집오류/미실행/시간 판정은 mutation.run/validate_result/passed의 현행 계약을 유지한다.

g45-final에서 수용한 기존 연결도 유지한다. LakeEnvironmentTests는 provider_inputs.actual_command()[0]의 형제 lake.exe를 소비하고 Mathlib 준비와 구별한다. submission 재시도는 research_work role·원 accepted_response, 반복재개는 continue_repetition의 정확 action_scope/ready/hold/affected, assessment 반려는 validate_plan_dispositions의 정확 ValueError를 사용한다. shallow 설치 시험은 toolchain_root의 실제 부모깊이 조건을 만든다. 이번 수용으로 runtime API가 바뀌지 않았다.

## 0094 당시 갱신: T4 수리와 실제 입력의 소비

`tests/boundary/test_mutation_baseline.py:ActualBaselineTests._run_fixture`는 외부scratch의독립Git/빈HEAD를기준으로새subject를만든다. mutation.SCRIPTS·CLI의branch_gate.repository_root·run_tests._finish_t3의SCRIPTS가같은fixture를소비한다. 실제child/정상기준·오류/skip/exit·후속witness와최종판정의기존단언은유지한다. 제품mutation구현은불변이다.

`tests/boundary/test_operator_bootstrap.py:BrokenEngineProbeTests`는 `do_math/scheduled_operator.py:execute`의 원failure·별도startup게시와 `{**result, 'startup': startup}` 반환계약을소비한다. 두게시레코드를읽어stdout전체를비교하고 live bootstrap/runtime/설치신원을단언한다. 원failure레코드에startup필드를추가하지않는다. 정본시험2·지침1/미러3의통합근거는tasks/g7-t4r/integration.json과managers/0094/accepted-diff.txt다.

남은 `LakeEnvironmentTests.test_lake_search_paths_are_observed_once_per_unchanged_project_input`는 `portable_bin(toolchain_root())`의snapshot기본경로를직접사용한다. compiler의 `support.provider_inputs.actual_command()`는 DO_MATH_KNOWLEDGE_TEST_LEAN을받는다. g45-final은실제공용설치의같은bin/lean.exe·lake.exe를읽기전용시험입력으로연결하고 real Job의검색경로/입력변경관측과신원단언을보존한다. 제품runtime에공용루트fallback을넣지않는다. manager는파일존재/SHA만확인했다.

`SharedInputProvenanceTests.assert_baseline_capture`와두exact_baseline시험은 SHARED_INPUT_BASELINE_SCRIPTS의별도pre-fix scripts와현판의ordinary/literal entered/opens/import_opens/coverage·marker차이/두worker raw union을비교한다. 입력정본은 `C:/math/docs/do-math/continuous-development-2026-10-13/phases/016/tasks/provenance-baseline/evidence/baseline-manifest.json`과그옆pre-provenance/scripts다. 도입bbe64043의실제부모010b0597·기존추출910파일근거를재사용한다. 과거코드는읽기전용비교입력이며현행제품호환분기가아니다.

g45-final의미시작배정에이세선택의 jobs1 최소확인/소수수리를기존준비로묶고, 다음전체일반/freshT3는 jobs3로순차실행한다. 원전체T4의301passed/1error/2skipped·exit1과새직접결과는별도로보존한다. T4 자식측정/변이는최종T3분모/색인/전체변이에합산하지않는다. 최종G4/G5·G6입력계약은기존대로다. manager0094/verification-review.json은직접대조한3worker/919Python/3미러쌍과task근거재사용범위를구별하며handoff-delta.json은g1/g23원인계를보충한다.

## 0093 당시 갱신: 기반1b/1c 판단의 소비

pr-base-ports-r는 제품 변경 없는 review이며 새 API를 만들지 않았다. evidence/decisions.json의17행·90정의 참조와 judgment.md가 여섯 포트 도입/기본값 제거·다섯 이동 단위의 처분과 한계를 제공한다. 경로는 scripts/ 기준이다. do_math/engine.py:ResearchEngine.__init__는 필수 ports를 Repository/ModelRunner/Lean verifier/ControlTransport에 전달하며 wiring.py:real_ports가 실제 구현을 조립한다. 내부 None/OS fallback 제거와 현재 입력 검사는 별개다.

do_math/model_call.py:runner_assignment는 profile·host 자원·launch owner·UTF-8 input seal을 검사한다. git_store.py:GitStateStore._call/_compare_and_swap는 오류/충돌 시 물리경계를 재확인하며, external.py:execute_operation은 현재 grant·요청을 검사하고 전송기록을 저장한 뒤 전송한다. 비성공/연결 오류는 효과 부재를 증명하지 않으므로 unknown이 될 수 있다. cli_execution.py:termination_confirmed는 root_signaled와 active_processes=0 및 process_ids=()를 모두 요구한다. Calls.close와 이 Job 장벽을 혼동하지 않는다.

engine.py:ResearchEngine._call_steps는 call_engine.py의 _prepare_call/_call_started/_call_stop_requested/_receive_call을 연결한다. 준비값에서 callback/deadline을 등록하고 yield 뒤 해제·수신하며 core_engine.py:CoreEngineMixin._retry_submission_publications의 수신→저장→정산→저장은0089 교정 그대로다. B38/B07·r07/r18의 수용 성질은 지정 범위만 재사용한다.

manager가50파일·90정의 참조의 판본/좌표와 핵심 정의를 대조했다. 21파일/38직접호출 검사는 유한 구문 검사이며 partial/callback 의미 읽기와 구별한다. 작업자의 네 AST 비교와 원32보고(완결메타데이터28·미완결4)는 근거 범위대로 소비하며 manager는 세 원보고를 직접 표본 대조했다. 1c/c5는 셋째단위 판본이므로 다섯째 실행 인증으로 쓰지 않는다. 넷째/다섯째 raw실행·과거parent exit 한계와 실패/skip을 유지한다. 상세근거는 task/evidence와 managers/0093/verification-review.json에 남고 workspace 전체 복원을 상시 요구하지 않는다.

g1/g23 원인계는 managers/0093/handoff-delta.json으로 이번 기반 처분만 보충한다. G2/G3/G8 전체 인증이나 새로운 전수감사를 만들지 않는다. g7-t4r와 g45-final의 입력/선행은 불변이다. 아래0092 이하 절은 당시 이력이다.

## 0092 당시 갱신: 기반1a/1d 판단의 소비

pr-base-tests는 제품 변경 없는 review이며 새 API를 만들지 않았다. evidence/decisions.json의 BT01~BT09와 judgment.md가 지정 기반 질문의 판단·처분·한계를 제공한다. 현재 정의는 scripts/run_tests.py의 test_modules/discover/TimedResult/_run_suite/_isolated, tests/support/known_defects.py:ledger_issues, tests/support/model.py:FakeCLI._submit/check_receipt/finish, tests/support/fakes/calls.py:DeterministicCalls.close/abandon_owner/_finish_turns, tests/support/sim.py:Sim.activate/_check_applied/restored와 assert_template_quiescent 등이다. source-references.json은 실제28파일·67정의의 위치와 SHA를 연결한다.

실행기는 선택 누락·fixture/subTest 오류·격리 미완료를 보고에 남긴다. 정상 bound 모델은 실제 workspace 제출과 지정 terminal receipt 일치를 확인한 뒤 provider 종료를 내며, 명시 standalone은 별도 계약이다. 정상 Calls.close는 원계산 결과/예외를 남기고 collect가 수신한다. Sim-only owner-loss는 미시작 계산 취소와 옛 owner 결과 폐기를 맡는다. 템플릿은 같은 절대 경로의 준비판을 새 engine/store/runner로 복원하며 미정산 실행/예약/Job/Calls를 반려한다. core_engine.CoreEngineMixin._retry_submission_publications의 수신→저장→정산→저장은0089 계약 그대로다.

재사용 비교 JSON은19연결·파일일치18·기록된 AST일치6이다. 원본문17/16/4는 ScenarioModel.render와 record_submissions 두 연결을 누락한 수치이며 managers/0092/verification-review.json에서 정정했다. file_io.os_lock의 과거파일 차이는 현재 잠금 후 초기화/해제 guard의 정적 판단으로 구분한다. 원8보고의 실패/skip·별도green·LF/CRLF·판본 한계와 B56/B36 원9보고 부재를 현행 전체 성공으로 바꾸지 않는다. 상세 원근거는 task/evidence에 계속 남으며 workspace 복원을 상시 요구하지 않는다.

g1/g23 원인계는 managers/0092/handoff-delta.json으로 기반1a/1d 처분만 보충한다. G2/G3/G8 전체 인증·새1932강도감사·저장 가족별quota를 추가하지 않는다. g7-t4r/pr-base-ports-r 및 g45-final의 입력/선행은 불변이다. 아래0091 이하 절은 당시 이력이다.

## 0091 당시 갱신: 기반review 기동 복구

제품 인터페이스와 기존 수용 의미는 바뀌지 않았다. pr-base-ports는 workspaces._prepare의 기존 사본 guard에서 거절됐으며 task.json/baseline.json/report가 없어 통합 결과를 생산하지 않았다. 원 scope/inputs와 불완전 base/workspace는 보존하지만 수용된 결과나 완료 시작판으로 소비하지 않는다. 파일 수만으로 변경0을 주장하지 않는다.

새 pr-base-ports-r의 scope.json은 원0089의 기반1b/1c 두 stage와 제외 범위를 그대로 제공한다. 새 task는 자기 고정 workspace·수용된 pr-ports와 core-recover 근거를 소비하고, evidence/decisions.json·judgment.md 및 changes=[] report로 실제hunk/현재소비/재사용성질의 판단을 반환한다. writes=[]·시험슬롯0이며 pr-base-tests·g7-t4r의 미완성 결과를 소비하지 않는다. 이 복구는 기반 의미 판단의 실행을 되살리는 것이며 G2/G3/G8 완료 인증이 아니다.

새 시작판은 baseline.json/objects이고 필요한 과거 파일만 공식 restore의 별도 새 디렉터리로 복원한다. 진행 중 두 배정과 g45-final의 입력/선행은 그대로다. g1/g23 및0089까지의 제품 handoff-delta도 변경 없이 재사용한다. managers/0091/review.md·recovery-review.json이 이번 운영 판단의 근거다. 아래0090 이하 절은 당시 이력이다.

## 0090 당시 갱신: 중단 작업과 시작판 복원

이번 manager에서 제품 인터페이스 변경은 없다. core의 현재 계약과 정확한 수용 범위는 아래0089 및 이전 절을 따른다. g5-core-recover는 기존 integration14경로와 accepted를 유지하며 재전달 사건을 새 통합으로 세지 않는다. 원 g7-t4는 report 없음·실제 변경0으로 취소됐으며 그 기록과 사본을 수용 결과로 소비하지 않는다.

새 g7-t4r가 공식 전체 T4의 selected/rows·t4_adapter.complete/problems·worker publication과 실제 source_sha256을 제공한다. g45-final은 이 task의 report.json/integration.json과 수용판을 소비한다. 두 파일은 선행 수용 때 생성되는 입력이다. 기본전체/fresh T3의 measurement_missing·재사용0·closing_eligible·branch_gate·함수진입색인 계약은 그대로다. pr-base-tests의 실행 배정은 불변이며 pr-base-ports의 inbox 이후 기동 실패는 다음 manager 사건으로 처리한다.

새 시작판의 파일 목록과 SHA는 tasks/ID/baseline.json, 내용은 records/objects에 있다. services/async-development/workspaces.py:restore(records, task_id, version, destination, paths)는 baseline|result와 필요한 상대 파일/디렉터리를 받아 새 별도 디렉터리에 복원하며, 기존 destination과 관리 workspace/base 아래 복원을 거절한다. 시작 목록에 없는 생성 캐시는 원래 부재다. task는 필요한 생성 근거를 evidence에 보존한 뒤 자기 쓰기 범위에서 시작 bytes/부재를 복원한다. 과거 report/evidence/integration은 기존 task 디렉터리에 남으며 archived workspace/base는 영구 입력이 아니다.

managers/0090/review.md·recovery-review.json은 이 운영 변경의 근거다. g1/g23 인계와0089까지의 제품 handoff-delta는 변경 없이 재사용한다. 새 제품 검증·완료 인증은 추가되지 않았다.

## 0089 당시 갱신: 복구 권한과 수용 후 정산

core_engine.CoreEngineMixin._retry_submission_publications는 원 publication wait/execution의 봉인 입력을 _issued_input으로 읽고 _receive_submission(..., preserved=True)의 결과를 _save한 뒤 _settle_activity와 그 저장을 진행한다. 로컬정산 예외 뒤 _reload가 accepted 결과를 볼 수 있어 원수용/receipt/owner를 새submission_failure로 바꾸지 않는다. 아직 같은execution의publication wait인 실제 수신실패는 기존failure owner로 보낸다. GitStateStoreError·재적재불능은 계속 전파한다. 직접정의와 references/초기화-효율과-정비.md가 의미 정본이다.

_review_recovery_control이 requested_by 있는 두 위임비교를 생산하고 _apply_inbox/_record_control_result가 같은 게시에 원user_control을 보존한다. _apply_delegation_judgment는 이 원요청을 소비하되 두 within_scope 뒤에도 현재권한을 확인한다. source ID 충돌·철회 grant는 원cycle/wait/source를 보존하며 거절한다. _register_execution→_activity_for_action의 ID 있는 action과 repair_execution.route_failed_action의 정확wait owner를 _recover_disappeared가 직접 소비한다. 종료 관측과 예약정산의 별도 확인은 유지한다.

_apply_operational_disposition은 operational_dispositions.admissible_basis_refs의 정본target 거절을 먼저 소비하고 target을 읽는다. 최신근거·현재checkpoint·원과제/정확assessment·user_decision 질문연결은 그대로다. _finish_native_recovery는 runtime 변경없으며 같은activity에check 후속이 남으면 ready가 정상이다. test_engine_recovery_choices의 원receipt/무새시도와 check/ready/result_refs/unresolved 단언이 연결된다. cleanup의live/종료미확정 archive gate와 기존 feedback/repair 저장 책임은 유지한다.

원6부분실행·최종시험5본문의 정확 근거는 managers/0089/verification-review.json이며 전체G5 도달 인증은 아니다. g7-t4는 run_tests --tier T4의 selected/rows·t4_adapter.complete/problems/worker publication을 소비한다. g45-final은 그 수용소스와 기본전체/fresh --tier T3 --full의 고정판·재사용0·measurement_missing/closing_eligible/branch_gate·함수진입색인을 제공한다. 제품 API를 새로 만들지 않는다. 두 기반review의 scope.json은1b/1c와1a/1d 원locator를 보존하고 evidence/decisions.json·judgment.md로 실제처분을 반환한다. 쓰기/시험권한0이며 관문 전체를 기다리지 않는다.

g1/g23의 원인계는 managers/0089/handoff-delta.json과 함께 소비한다. 충분한 성질재사용·A22범위와 최종관문/외부조건의남김을 유지한다. 아래 갱신은 당시 이력이다.

## 0088 당시 갱신: 제출 현재성과 실제 적용

core_engine.CoreEngineMixin._validate_bundle_current는 decision_engine._validate_decision_acceptance 뒤에도 원 input_snapshot의 source_basis를 다시 포착하고 현재 source·academic 요구 hash·실행 및 추가 grant 권한을 검사한다. call_engine._prepare_call은 task.inputs 또는 target knowledge.source_basis를 사용하므로 source_basis와 decision_basis는 같은 집합이 아니다. governance._install_record는 같은 revision 숫자의 charter 교체를 허용하므로 academic hash도 별도 책임이다. integration.inspect_bundles가 발급 grants/decisions에 authority_refs를 제한하며 decision은 불변 이력이므로 decision 소실의 중복 조건만 제거했다. 거절 후보·원 sealed 출력 보존과 producer/engine owner 구분은 기존 apply_bundles/_receive_submission 계약을 따른다.

integration.split_research·revisions.submission_errors·역할별 extension 검사는 일반 분할 연구에 mutation이 섞이지 않도록 한다. 개정/계획/준비 응답은 단일 bundle이다. 이에 따라 _hold_impact_reviews의 non-impact 필터를 제거했다. _apply_bundle_candidate의 유효한 mutation은 기존 task/knowledge를 대상으로 하며 bundle_impact_request가 plans.bundle을 만든다. 종속 기록이 없어도 plan은 있고 requires_independent_review만 false일 수 있다. _hold_unreadable_impact_submission은 stage와 producer를 모두 비교해 해당 생산자의 pending만 정리하며 다른 생산자 요청·일반 action을 보존한다.

_apply_extensions의 private_insights는 cycle별 source_execution을 보존하고 종료 때 원 author의 input_snapshot에서 basis/source를 읽는다. 바뀐 근거나 원 snapshot 읽기 실패는 suspension, 보류 통찰의 무효 kind/참조는 원 작성자의 finding/question으로 남긴다. 현재 새 통찰의 무효 kind는 적용 오류를 전파한다. tests/support/review_scene.py:ReviewScene.execute(registered=True)는 저장 소비에 필요한 실제 execution/activity·종료 전이와 명시적 합성 receipt를 준비한다. 모델 수송·중앙제출 증거로 쓰지 않으며 기존 기본 mixin 소비는 유지한다.

_apply의 task_contract_review는 바로 앞 _validate_decision_acceptance의 contract_sha256/capture_task_basis 검사를 소비한다. unscoped identity_review는 _prepare_call이 cycle 생성으로 처리하며 모델 응답에는 admitted cycle이 있다. action_schema/profile 및 machine dispatch 뒤 남는 마지막 모델 역할은 maintenance다. 중복 역할/계약 조건을 줄였으나 preparation의 unfinished status·원 formal 환경·조건 ID 결박/평가·순환·candidate kind 후속은 유지한다. _apply_plan은 issued_input의 실제 외부 artifact를 읽으므로 snapshot/ready_task_ids 검사를 유지하며 이번 AST는 base와 같다.

직접 변경은 g5-core-apply/report.json의12경로이고 보존 실행의 정확 범위는 managers/0088/verification-review.json을 따른다. 유한 계약 질문 완료는 최종 fresh T3 도달 인증이 아니다. g5-core-recover는 기존 objective/입력으로 이 수용판을 소비하고 복구/정산의12함수 질문만 이어받는다. managers/0088/handoff-delta.json이 이전 g1/g23 인계를 보충하며 원기록과 최종관문·외부조건의 남김을 유지한다. 아래 갱신들은 당시 이력이다.

## 0087 당시 갱신: continuation 응답과 역사 처분의 소비

CoreEngineMixin._submission_repair_context는 action의 continuation_of/repair.execution_id 계보에서 조상 영수증을 모은다. integration.split_research({"action": action})가 참일 때만 accepted_response의 원 integration_id/response_sha256를 고정한다. 단일bundle 역할의 서로 다른 수용 응답은 충돌이 아니며 양쪽 모두 accepted_integration_ids를 보존한다. split 연구의 원응답 변경/재배정 금지와 기존 receipt 재사용은 integration.inspect_bundles/apply_bundles 정본을 따른다. 원계보 충돌 guard는 유지하고 지원 생산·수신 불변식을 같은 행에 명시한다.

_save/_reload는 정상 store 반환 뒤 head/instance/runtime을 함께 채택하고 SchedulerMixin._evaluate_stops→ModelCalls._judge가 호출별 판단 예외를 보관한다. _publish_control_request의 재조회 실패는 원 instance/runtime을 복원하고 전파하며 최종반려를 만들지 않는다. 앞0084 native finally의 head 비교·원후보 복원은 그대로다. submit_control의 지원 writer는 acceptance lock 안의 재확인으로 동일ID를 처리하며 hardlink의 예기치 않은 외부충돌은 전파한다. 원파일을 덮거나 그 충돌을 정상 replay로 바꾸지 않는다.

_context의 operational_review는 등록된 실제 execution/action을 소비한다. 위임 원요청 guard와 task-result 물리경로 검사는 유지된다. overflow_requests의 현재 contract_revision과 원 selected_contract_sha256는 서로 다른 의미이며 _apply_input_overflow_resolutions가 현재계약 hash도 검사한다. support.submission_receiver.issue_input은 기존 _issue_input을 교체한 공유 시험helper로 봉인 입력 게시를 수행하며 별칭은 없다. support.engine_overflow.held_work는 waiting_action/questions.link 정본으로 저장 가능한 실제 질문과 사유를 만든다. 제품정의와 직접시험은 g5-core-edge/report.json의 변경목록을 따른다.

pr-records/governance/review/knowledge/boundary의 evidence/history-decisions.json은 각각7/6/7/7/8개 지정hunk의 처분·이유·현재파일/심볼·원자료 한계를 제공한다. g23의 추가검토37건은0086의2건과 이번35건으로 처분완료다. PR05 원수차이는 특성시험1개 추가→정확 retired row로 해명했다. 기존72구간의 한정근거, 원보고부재, 비B/이관강도·최종판 인증은 별개다. 원 g23/scope는 보존하고 managers/0087/handoff-delta.json과 review.md를 보충한다. accepted-core-review-delta.json은 이번 core와 직접 겹친 pr-review._context의 보호성질 유지 대조를 기록한다.

원8부분실행과 수정8시험의 passing AST 연결은 managers/0087/verification-review.json에 있으며 전체G5 성공이 아니다. apply/recover는 기존정의/objective를 유지하고 수용판을 순서대로 소비한다. 저장범위/A22의 공통보장 재사용, 최종관문·외부조건의 기존 남김을 유지한다. 아래 갱신들은 당시 이력이다.

## 0086 당시 갱신: Git 포트·wait 규칙의 역사 처분

pr-ports/evidence/history-decisions.json의 B38/B07 rows는 실제 historical_commit(s)·reviewed_hunks·current_references·재사용 근거·원자료 한계·처분을 제공한다. 두 지정질문의 judgment_complete=true는 PR02/PR03 전체나 G8 인증이 아니다. 원g23/pr-ports scope는 보존하며 이번 처분을 managers/0086/review.md·verification-review.json과 함께 보충해 소비한다. g23의 additional_historical_judgment_needed37개 중2개가 완료됐고35개는 기존 다섯review가 맡는다. 기존72개 한정근거의 범위는 넓히지 않는다.

do_math.cli._require_git는 create의 missing/empty 확인과 mkdir 뒤 주어진 backend.initialize_repository→repository_exists를 호출하며 init 실패 때 존재검사에 도달하지 않는다. GitProcess의 두 CLI 연산은 ambient 환경/종료상태만 소비한다. project_repository_root/project_snapshot은 _project_read의 주입 environment·각 읽기 전후 check_stop을 사용하고 storage_finish_git_output의 UTF-8/root/tree/path 해석 및 raw diff를 반환한다. 형식/stop/오류 의미는 ports/git_backend.py와 해당 실제 정의가 정본이다. engine/wiring/Host/preview/setup의 필수 backend 전달을 유지한다. B38의 불완전 .git 상위탐색과 preview 자식 env/ports 누락은 각각 0bb1af48/a29f3c6a에서 이미 교정돼 있다.

do_math.layers.LAYERS['do_math/wait_rules.py']='1'이며 tests/migration/regions.json의 engine.product_modules에 정확 한 번 등록한다. 옛scope의 scheduling 표현은 현재 사실이 아니다. test_migration_ledgers.MigrationLedgerTests의 계약은 단일 영역 소속이다. wait_rules는 deepcopy/values.require_text를 사용하는 순수 규칙이며 update_waiting_action은 후보를 waiting_action으로 검증한 뒤 원record를 변경하므로 반려 때 원값을 보존한다. SessionSlots가 실제 gate/시계/예약, activities.wait_for가 활동/실행 상태, reporting.waiting_action_rows가 표시를 소유한다. resolver 문자열만으로 실제 owner 동작을 인증하지 않는다.

과거G4의 관련30행은 과거 선택/결과에 한정해 재사용한다. 비교19파일 중 formal.py/session_slots.py/test_action_wait_contract.py는 SHA가 달라 현재 전체성공 근거가 아니다. 원Temp보고11개 부재와 최종소비판 관문은 별도로 남긴다. 제품 API 변경은 없고 core의 edge→apply→recover 순서·고정입력·기존0084capture/0083예약 수용도 그대로다.

## 0085 당시 갱신: 보존·역사 검토 인계의 소비 계약

tasks/g23-handoff/evidence/preservation-state.json의 rows는 원K61/P2 12의 id/group·원문·accepted_tasks·current_definitions/current_tests·confirmed_scope·remaining/minimum_next_action을 제공한다. task_evidence는 수용된 report/manager review/integration과 고정plan행을 연결한다. AST 정의 존재는 참조 확인이며 의미완료의 근거는 각 수용판정과 실제단언이다. whole_requirement_certified_here=false를 유지한다.

prior-review-state.json의 review_units25개는 원history_ids/review_slices109개를 보존한다. review_state=accepted_bounded_review_reused 72개는 해당 한정성질만 재사용하며 additional_historical_judgment_needed 37개는 이 인계에서 해당hunk 실제검토 근거를 확인하지 못했다는 뜻이다. mapping_is_not_review=true·whole_unit_review_complete=false다. non_b_material은 기반/이관의 원selector 길찾기이고 새전수검사quota가 아니다. PR05 원1931/당시1932 차이와 전체단언강도는 별도다.

pr-records/ports/governance/review/knowledge/boundary의 scope.json.rows는 이37구간을 중복없이7/2/6/7/7/8개로 나눈 고정입력이다. 각 review는 실제hunk→직접현재소비→원보고/정확단언을 보고 유지/이미교정/정당제거/구체수리필요/정확자료부재를 판단한다. evidence/history-decisions.json·judgment.md와 report.json으로 반환하며 제품 API를 만들지 않는다. writes=[]·시험슬롯0, 실제선행g23뿐이다. 진행중core의 미완성 결과는 소비하지 않고 영향을 받는 성질의 수용diff만 나중에 연결한다.

인계는 manager0082 고정판이고 managers/0085/handoff-delta.json이 0083예약·0084capture의 수용보충이다. 참조 중 현재diff는 core_engine.py/test_engine_control_receipts.py 두파일이며 unreadable ref의 확정반려 기대보다0084 미확정오류/원후보복원 계약이 우선한다. 0083 held/startup/실예약수용은 재사용하되 연구운전/전체G7로 확대하지 않는다. 기존 원자료는 덮지 않는다. A-31 자동생산/정확action과 A-42 동시성/독립운영 해명도 실행인증으로 확대하지 않는다. core후속의 정의/objective는 그대로다.

## 0084 당시 갱신: 미확정 capture 게시와 원후보 복원

do_math.core_engine.CoreEngineMixin._publish_control_request(request)는 capability를 뺀 원요청 digest와 보존영수증으로 재전달 신원을 확인한다. 게시 예외 뒤 _reload가 성공하면 정확 request_id/request_sha256의 durable receipt를 찾아 재사용하며, 영수증이 없을 때만 기존 rejected를 반환한다. 재조회 자체가 실패하면 그 오류를 전파하고 self.head가 원head인 경우에만 원 instance/runtime을 복원한다. ControlTransport.receive는 publish 반환 뒤 _store하므로 시험의 GitStateStoreError에서는 수송최종반려를 게시하지 않는다. tracker 후보도 성공확정 뒤 live tracker에 반영한다. 모든 후속예외의 반려 의미를 이번한정시험으로 일반화하지 않는다.

_capture_native_submission(execution,result,context,schema,workspace,raw,...)은 원 native receipt를 먼저찾아 같은final SHA에 재사용하고 다른final은 거절한다. staging/save 예외 뒤 재조회의 finally에서 원head의 instance/runtime을 복원한다. 새head를 이미채택했으면 durable상태를 보존한다. 재조회 오류는 계속전파하고 성공한 재조회에 원submission_checked receipt가 있으면 이를 반환한다. _save/_reload는 head채택 뒤 _evaluate_stops를 호출하므로 head전진뒤 예외의 세부질문은 남아있다. 실제정의·references/과제-착수조건.md·초기화-효율과-정비.md가 정본이다.

tests/unit/test_core_branch_contracts.py의 explicit/native 두회귀는 실제 Git CAS 뒤 응답유실과 object_info 읽기장애에서 원상태/원영수증/원bytes/무중복을 확인한다. tests/sim/test_engine_control_receipts.py의 자기점검회귀는 unreadable ref가 미확정오류이며 ref복원뒤 동일delivery가 수용됨을 확인한다. inbox삭제/wakeup과 관찰게시뒤 미전달도 직접단언했다. capture-after/capture-races-final/native-final은 서로다른부분판이며 전체관문 또는 공개owner복구완결/실제OS·provider증거로 합치지않는다.

후속 g5-core-edge/apply/recover는 같은core/helper/설명을 순차통합한다. 각 gap-scope의 final은0084수용좌표이므로 후행작업은 실제시작base심볼로 다시연결한다. 쓰기목록은 시험의무가 아니며 기존보장재사용·정적판단 우선이다. g23의고정입력은보존하고 managers/0084/handoff-delta.json으로 이번결과만 인계한다. 새제품API/registry는없다. 최종T4는 실제core소비판을, G6는 최종T3색인을 선행으로소비한다.

## 0083 당시 갱신: held/startup과 실제 예약 증거

tests/support/scheduler_live.py:run_scheduler_smoke는 frozen check/run-engine/wake마다 stdout 전체가 {'outcome':'held','startup':직후게시내용}인지 검사한다. held-<mode>.startup.json은 게시 원bytes를 보존한다. startup의 정확 root필드와 bootstrap의 mode=frozen/snapshot_sha256/installation_root/comparison=match/differences=[], 실제runtime_root, 독립부모 installation_evidence 전체, UTC시각의 child호출구간을 연결한다. 설치bytes신원은 필수이고 source_status=unavailable/null commit·원사유는 유효한 관측이다. 제품 execute→main/manifest API는0080절 그대로다.

tests/smoke/test_scheduler_live.py:SchedulerLiveTests.test_held_pythonw_tasks_start_wake_and_uninstall은 정확세mode와 각startup판정/전체반환을 확인한다. 기존 실제 schedule→PS/pythonw/freeze→OS새ticks/종료0→시각wake→소유확인/finally해제 계약은 유지한다. direct child 원출력과 OS task관찰은 별도다. 이번원자료의 마지막세null·자기process0·cleanup오류0/HOLD불변은 task evidence/t5-output의 smoke.json·ownership/requests·rawstatus/inspect에 연결된다. cancel_wake는 invoke 요청목록 밖의 공개scheduler포트를 직접 사용한다.

실제수용은 예약T5 정확1선택/exit0에 한정한다. 시각차(-11/-21/+2초)원인·OSstdout·모든역할PID·연구운전은 미확인이다. 전체T4는 향후 실제core소비판수용 뒤 선택/고유rows·t4_adapter.complete/problems/worker게시로 판단하며 도달률임계값을 만들지 않는다. 이전실증의 한정재사용과 환경/L01/공급자원자료 남김을 유지한다.

g5-core-tail·g23-handoff의 시작정의/입력은 그대로다. managers/0083/handoff-delta.json은 고정 g1/g23 입력에 이번예약성과만 더하는 인계이며 기존 원자료를 덮지 않는다. 새제품API/registry·새task는 없다. 독립인계는 이미g23소유이며 최종관문은 필요한소비판/색인만 선행으로 삼는다.

## 0082 당시 갱신: 영향 assignment·cleanup 보존과 의무 인계

do_math.integration.bundle_impact_request는 같은 integration_id/payload_sha256/producer_execution_id/input_snapshot header의 실제 검토 assignment를 유한 후보로 사용한다. 같은 assignment 검토들만 excluded_dependents로 제외해 실제 plan_impact를 계산하고 요청이 assignment와 정확히 같을 때 채택한다. 맞는 후보가 없으면 제외 없이 새 요청을 만든다. 이전 bounded loop/안정화 오류는 제거됐으며 이전hash·고정입력·독립 검토/봉인·receipt 소비 계약은 유지한다. references/과제-착수조건.md와 tests/unit/test_knowledge_impact_review.py의 원반례/수리 단언이 연결된다. 순수 domain graph의 수리를 전체 공개 owner 흐름 인증으로 확대하지 않는다.

CoreEngineMixin._receive_submission의 maintenance cleanup은 accepted 응답 게시 후의 로컬 효과다. ValueError/OSError/GitStateStoreError 때 최신 게시 상태를 다시 읽고, 아직 게시되지 않은 동일 execution_id의 maintenance_cleanup 삭제 사실만 복원한다. retention.record_cleanup_interruption은 history_start 뒤의 실제 deleted를 completed_paths로 남기고 승인 경로 중 나머지만 paths에 둔다. 다음 owner는 maintenance이고 원 accepted receipt/output_accepted는 유지된다. _reload 자체 실패는 전파한다. references/초기화-효율과-정비.md와 test_core_branch_contracts의 archive/final CAS 직접 단언이 실제 정의를 설명한다.

_resume_input_overflow_action은 정확 owner/wait/condition을 소비한다. 활동의 전실행 종료는 activities.wait_for, waiting 중 새 배정 거절은 assign_execution이 보장하므로 중복 live 검사를 제거했다. questions.link는 open을 만들고 close가 마지막 미해소 대상을 덮을 때만 닫는다. _resolve_input_overflow_question은 닫힌 질문의 원해소를 already_resolved로 보존한다. 공개 API/새 waiting 종류는 추가하지 않았다.

g1-handoff/evidence/obligation-state.json은 고정 manager0080판 원30의무의 원문·수용근거·정의·구체남김 인계다. 최신 core와 G7 수용분은 managers/0082/handoff-delta.json을 함께 읽는다. 원자료를 덮지 않으며 이것은 G1 최종 인증이 아니다. g23-handoff는 같은 방식으로 원K61/P2 12·PR25를 연결하고 실제 미검토 diff는 남김으로 유지한다. writes=[]·시험슬롯0이고 새 제품 인터페이스는 없다.

g5-core-tail의 정확 남김58arc/63행·수용SHA/현재좌표는 task gap-scope.json, 허용파일은 queue/task.json이다. core/integration/submission·관련 시험/helper·설명과 미러를 소유하며 g7-scheduler의 helper/smoke/시험지침은 읽기 전용이다. 예약 HOLD/기동 신원·명시manifest·소유정리는 이번 core 변경의 영향을 받지 않아 기존 배정을 유지한다. 최종T4는 실제 소비판 수용 뒤이고 부분T3나 T4자식도달을 최종전체 G5로 합치지 않는다.

## 0081 당시 갱신: 실경계 증거와 예약 smoke 수리

g7-boundary-scope/evidence/judgment.md는 기존 실경계 성질·원자료/외부 입력·최소 실행안을 제공하는 조사 결과다. 원source 비교와 raw 보존은 source-comparison.json·static-evidence.json, 현재 entry diff의 추가 판단은 managers/0081/verification-review.json·accepted-entry-diff.txt에 있다. 이미 수용된 worker/control/probe5파일의 주석 변경은 기존 전송/원bytes 보장을 바꾸지 않는다. bootstrap/scheduled_operator의 현재 API는 아래0080절의 installation_manifest 명시 전달이다. 진행 중 core/integration/submission은 결과 수용 뒤 해당 경계의 실제 diff만 추가 확인한다.

tests/support/scheduler_live.py:run_scheduler_smoke는 현재 direct frozen check/run-engine/wake 응답을 {'outcome':'held'}와 완전일치 비교한다. do_math/scheduled_operator.py:execute→main의 실제 출력은 outcome과 startup이며 startup.json도 게시된다. 이 F1은 정적 계약 불일치다. g7-scheduler는 held와 실제 manifest/설치/기동 근거를 함께 대조하도록 기존 helper·직접smoke·설명/미러를 고치고 기존 SchedulerLiveTests.test_held_pythonw_tasks_start_wake_and_uninstall을 T5로 실행한다. 새 제품API·공통registry는 없다. source Git을 못 읽은 unavailable와 설치bytes 신원은 별도이며 임의 source_commit을 만들지 않는다.

실예약 경계는 run_scheduler_smoke의 시작 세task부재→HOLD/ownership·requests선기록→실제 schedule/PowerShellScheduler·pythonw/freeze→새ticks/종료0·one-shot wake→소유확인/finally해제·세null/자기process0다. 직접pythonw JSON과 OS 관찰을 구별하고 실제 engine child 시작/유료연구를 인증하지 않는다. 새 task는 정본/미러 helper·smoke·시험지침 각3경로와1슬롯을 소유한다. core가 소비하는 연구처리는 HOLD 뒤라 불필요한 선행을 걸지 않는다.

전체T4는 최종소비판에서 현재 선택·고유rows와 t4_adapter.complete/problems/worker게시를 확인하며 도달률임계값은 없다. 과거295행이나 T4자식도달을 현재T3로 합치지 않는다. 공급자/host/Lean/학술은 조사에서 명시한 성질만 재사용한다. 실제 운전read는 공식run_tests 선택이 없으며 L01 Q1프로필/Q2단위의 명시 입력 전에는 실행command를 꾸미지 않는다. Q3문구는 해결 유지, byte기준은 결정 전 유지/미인증이다.

## 0080 당시 갱신: 명시 manifest 전달과 의무 인계

scripts/operator_bootstrap.py:main만 자기 입구의 인접 bootstrap-manifest.json을 찾고 verify_snapshot 후 검증된 package를 import한다. 원 installation_root와 installation_manifest:Path|None을 do_math/scheduled_operator.py:main→execute에 전달한다. 제거된 bootstrap_evidence 인자를 받는 호환 경로는 없다. execute는 전달된 manifest를 검증해 startup_evidence와 installation_evidence를 startup.json에 게시하고 같은 경로를 run_engine에 넘긴다. 경로 생략은 live/no_recorded_manifest이며 runtime 위치에서 자동 선택하지 않는다.

run_engine의 직접 installation_manifest API는 유지한다. 명시 manifest의 snapshot과 installation_root 일치를 검증한 뒤 live scripts/do_math.py run --watch 명령의 --installation-manifest에 절대 경로를 넣는다. 검증 실패·다른 설치 root는 child 시작 전에 반려한다. bootstrap의 import 전·execute의 기동 근거·run_engine의 child 시작 전 검증은 서로 다른 경계에서 유지된다. HOLD에서도 기동 근거를 기록하고 작업을 시작하지 않는다. 기동 runtime_root와 원 installation_root는 다를 수 있다. 설명 정본은 references/CLI-실행-계약.md, 원본 package 시험은 tests/sim/test_operator_supervision_contract.py다.

직접 worker/MCP/bootstrap/probe의 새 interpreter import·dispatch만 같은 행 사유로 T3에서 제외된다. 실제 책임은 tests/boundary/test_provider_worker_roots.py·test_provider_control_server.py·test_submission_mcp_server.py·test_operator_bootstrap.py·test_operator_standalone.py에 연결한다. 일반 처리/검사·manifest 판단은 T3에 남으며 T4 child/동결 파일의 도달을 T3 report/coverage/함수진입/index로 합치지 않는다. 과거13arc/25행 처분과 분모 변화는 tasks/g5-entry-gate/evidence/gap-disposition.json, manager판정은 managers/0080/review.md다.

g1-handoff는 제품 API를 만들지 않는다. 원 requirements-index의 stage1/stage2 30행을 이미 수용한 근거·현재 정의·정확 남김·필요한 최종 관문에 연결한다. writes=[]·시험슬롯0이며 core/G7 진행 중 결과는 소비하지 않는다. g7-boundary-scope의 시작판에 남은 옛 bootstrap 계약은 그 task 결과 수용 때 이번 diff로 해당 조건만 갱신한다. 기존 정의/objective를 중간 변경하지 않는다.

## 0079 당시 갱신: Lean·신뢰 계약과 실경계 후속

formal_engine.FormalEngineMixin._trust_control(register)는 register_request_errors→실제 toolchain record/선택 baseline→environment_errors를 거쳐 환경과 binding을 게시한다. transition/check는 이 형식 계약을 다시 검사하지 않는다. 실제 실행파일·기록·fingerprint는 trust_validation.check_environment가 검사한다. 공개 invalidate_environment는 진행 중 transition과 queued check를 지우지 않으므로 _trust_check_steps의 검사 전 invalid 거절은 유지한다. record_transition_result의 ready는 모든 target의 반환이며 모두 verified의 뜻이 아니다.

formal_check/trust_check/trust_activate의 실제 action은 새 활동 또는 자기 machine continuation을 소유한다. core_engine._register_execution의 review restoration None 경로는 AI 검토 활동에 해당하고, execution_profiles.build_profiles는 이 세 역할에 provider/model/host 예약을 만들지 않는다. 이 프로필의 session_slots.SessionSlots 입장에는 충돌할 예약이 없으며 core_engine._register_execution의 정상 반환은 실행이다. 세 caller의 중복 None 방어만 줄였고 공유 AI/external 입장 계약은 바꾸지 않았다. 입력 형식 밖의 내부 dict/가짜 capped profile을 정상 caller로 취급하지 않는다.

knowledge_io.import_candidate·knowledge.replace_knowledge의 공개 개정은 새 KN을 만들며 원문이 바뀌면 새 FR을 쓴다. 변하지 않은 사용 가능한 형식 증거는 원 FR을 재사용할 수 있지만 같은 KN의 원문/선언을 덮어쓰지는 않는다. FormalEngineMixin._formal_steps는 _preserve_machine_return 뒤 stop으로 원 decision basis·권한·고정 환경의 현재성을 판단한다. 그 뒤 정산/봉인 사이에 control을 적용하는 yield가 없다. 중복 환경 재비교 대신 _require_action_clock을 유지하고 knowledge_records.record_formal_result가 활성 환경·새 transition·정확 증거·기봉인 결과를 검사한다. 새 transition은 active 환경/KN이 같아 stop_reasons=[]여도 봉인을 거절할 수 있다. 이때 원 verified artifact와 failed 처분을 따로 보존하며 성공 receipt/identity_review를 만들지 않고 research_plan을 연다.

formal._job_run의 stopped 반환은 종료 확인·원 stdout/stderr 수집 뒤 수행되고 finally가 Job을 닫는다. if/return 두 행 표기로 실제 반환과 coverage 좌표를 연결했다. g5-trust-rest의 과거 남김0은 전체 통합판 T3 성공이 아니다. 실제 Lean/Mathlib·native Job은 별도 G7 경계다.

g7-boundary-scope는 새 제품 API를 만들지 않는다. 기존 scripts/tests/smoke/test_{provider,host,lean,scheduler,scholarly}_live.py와 support의 현재 호출, 과거 지정 실증, r19-r20의 원자료 남김, L01 Q1/Q2를 읽어 한정 재사용·구체 최소 실행·필요 외부 입력을 manager에 제공한다. 현재판 판단과 최종판 인증을 구분하고 g5-entry-gate/g5-core-gaps가 바꿀 수 있는 경계는 유효 조건으로 표시한다. writes=[]·새 시험/실호출0이며 진행 중 제공자 결과를 소비하지 않는다.

## 0078 당시 갱신: core 수신·게시의 전제와 남김

core_engine.CoreEngineMixin._apply_inbox는 validate_control_payload와 source/input/등록 handler 뒤 남는 request를 처리한다. handler는 후보를 준비하고 processed_controls/control receipt는 뒤 _save가 게시한다. 그 최종 게시의 acknowledgment 유실은 예외로 전파되며 재시작 후 durable receipt를 재사용한다. _publish_control_request의 preview 선행반환·submit/safety 분기 뒤 마지막 kind는 transport가 검증한 self-check다. tracker/신원/권한/봉인/현재성 검사는 유지한다.

knowledge_io.import_candidate는 기존ID를 거절하고 새기록을 만든다. core._knowledge_io_control은 같은ID 개정을 가정한 소비자 정지 루프를 제거했다. 기존 지식의 검토된 개정과 영향/현재성 처리는 별도 경로다. core._apply_bundle_candidate/_apply/_apply_kind_definition_check는 submission.extension_schema/EXTENSION_ROLES·_payload_issues·실제 _response_schema가 확인한 역할·제목·비공백 report·verdict를 소비한다. 적용 시점의 현재성/독립성/정확hash·findings 검사는 계속 필요하다.

external_requests의 grant부재는 제출 형식 오류가 아니다. 실제 중앙 편입은 origin_execution_id와 extensions/external_requests/N/purpose를 가진 user grant 질문을 저장하고 외부 operation/전송을 만들지 않는다. ExternalEngineMixin._external_control의 retry는 고정 grant 현재성을 먼저 검사한다. 미시도취소는 governance._dispose_grant_consumers의 철회로 생산되고 해당 grant로 재시도할 수 없다. 시도한 작업은 등록된 원execution/activity를 이어받는다. external.execute_operation의 persist callback은 같은 owner에서 같은 신원의 갱신을 동기 게시하며 전송 전 정지·시계·권한과 durable send marker를 유지한다.

retention.retention_inputs는 실제 source 생산자와 core._inspect_before_write→state_checks.inspect_state(record_storage)→_source_errors가 확인한 source.name으로 ID/name/source:name alias를 만든다. source 저장schema 자체가 name필수라는 뜻은 아니다. record_schemas.validate_semantics는 waiting_actions key와 보존action.id를 대조한다. activities.wait_for는 배정실행 종료를 요구하고 resume_activity가 waiting→ready, assign_execution이 ready→working을 맡는다. assign_execution은 waiting을 거절한다. 제품 설명은 references/과제-착수조건.md다.

ObservationTracker.observe에는 worker_feedback 생산자가 없다. 실제 self-check 응답/규칙 갱신 feedback은 core._publish_control_request/_redeliver_control_feedback이 전달한다. 파일전달 실패에도 durable receipt를 보존하고 뒤 upkeep에서 재전달한다. feedback의 실제 생성/전달 경로를 제거하지 않았다.

수용판 core69arc/93행과 integration.bundle_impact_request의 exclusion 안정화1arc/1행이 남아 있다. 새g5-core-gaps의 gap-scope.json은 원/수용판 좌표·SHA·현재 조건을 연결하며 원래 남김의 제안은 확정 계약이 아니다. 실제선행은 g5-core-rest뿐이고 정확 쓰기 범위는 queue/task.json이다. 진행 중 g5-trust-rest·g5-entry-gate 제공자는 읽기 전용이며 쓰기교집합0·각시험슬롯1을 유지한다. 최종 전체G5·실환경 성공으로 확대하지 않는다.

## 0077 당시 갱신: 직접 실행 입구와 측정 경계

codex_adapter.LocalCLIAdapter.start는 sys.executable·provider worker 파일·snapshot_request로 직접root를 만든다. claude_worker/codex_worker의 요청검사와 cli_worker.run_cli는 요청/prompt/schema/argv SHA·execution/profile신원과CLI종료를status에남긴다. worker자체exit0과외부CLIexit2를구별한다. 이번boundary의외부실행은현재Python이공급자flag를거부하는실경계이며실제모델성공이아니다.

control_server.mcp_server_config의파일명령은cli_worker.argv_inputs가소비한다. 직접main/bareimport·submit_draft의request_control이실제MCPchild에서입력/배달·영수증으로연결된다. 기존boundary.test_provider_control_server와boundary.test_submission_mcp_server의수용근거를재사용했다. 의미검증·봉인·게시의제품함수는대역으로바꾸지않는다.

operator_bootstrap.main은검증된동결package의scheduled_operator.main에원설치경로/bootstrap_evidence를전달한다. 실제check/HOLD에서도operator/startup.json을게시하며runtime_root는동결사본,installation.installation_root는원설치다. scheduled_operator.run_engine은명시manifest부재시SKILL_ROOT옆manifest를선택하고verify_snapshot뒤원설치가일치해야live scripts/do_math.py run의--installation-manifest절대경로를전달한다. 현재설명은references/CLI-실행-계약.md,직접시험은boundary.test_operator_bootstrap과sim.test_operator_supervision_contract다.

자식interpreter·동결파일의행동증거는원본경로rawT3와다르다. branch_gate.Measurement는runner프로세스의원본scripts경로를측정하며FunctionRecorder도prefix에묶인다. g5-entry-io의13arc/25행행동확인을원본도달에수동합치지않았다. 원설계5.5의같은행사유있는의도적미도달과일반로직을구별하는후속이g5-entry-gate다. bootstrap/manifest의검증·신원·명령·HOLD계약을유지하며필요한실제caller까지같이갱신한다. 층/실행기/측정모듈은읽기전용이고새framework를추가하지않는다.

context_store.collect_outputs의파일reparse omission현재182→183/183~185행과file_io의non-nt현재69→70,98→99,145→149,159→162,340→-336및7행은환경미검증이다. 실제파일symlink환경/실제POSIX가필요하다. 같은WinError1314·WSL시작불능probe를반복하지않고호스트부재로제외하지않는다. g5-entry-gate쓰기범위에서이두모듈을뺐고환경조건은plan에유지했다.

g5-entry-gate의정확25정본/25미러경로와13arc/25행좌표·SHA는task.json/gap-scope.json이다. 실제선행은g5-entry-io뿐이며g5-core-rest·g5-trust-rest의정의/소유는고정한다. 두running과쓰기교집합0·시험슬롯각1을유지한다.

## 0076 당시 갱신: 권위 영향 처분과 Lean·신뢰 남김

scripts/do_math/knowledge.py의 BASIS_FAMILIES→_basis_records와 plan_impact는 kind-definition/trust-environment를 계산/선언 영향에 포함할 수 있다. _confirmed_impact는 추가선언의 독립 확인과 정확한 합집합을 요구하고 integration.bundle_impact_request→apply_reviewed_impacts가 같은 정본을 소비한다. _apply_impact_effects는 두 권위와 execution/activity 원기록을 보존하며, affected_ids를 knowledge_reassessment_required 사건과 후속 research_plan에 남긴다. 닫힌 record_schemas/schemas.py의 kind_definitions 및 trust_validation.ENVIRONMENT_PROPERTIES에 없는 input_current/use_history를 추가하지 않는다. 종류의 효력 변경은 knowledge_io.withdraw_kind_definition, 환경의 효력 변경은 knowledge.invalidate_environment가 소유한다.

invalidate_environment는 해당환경 형식결과에 의존하는 use만 suspended/environment_revalidation으로 바꾸고 독립환경 use의 원상태를 유지한다. 실제전환의 역사적use와 새activeuse로 이 차이를 단언했다. 단일부분T3의 도메인독립확인 표본·실제검증게시/복원은 새봉인모델검토 또는 실Lean 성공의 증거가 아니다. 현재 설명은 references/지식-저작과-재사용.md와 scripts/이음새-정본.md다.

정책형식·의미검증은 initialization.activation_requirements→review_policy.build_review_policy이고 lifecycle_engine.LifecycleEngineMixin._activate_initialization가 그 요구를 소비한다. review_engine._retry_review_initialization는 active lifecycle와 채택policy의 정확hash로 이 검증을 이어받는다. 없는 activation_gaps 명칭과 잘못된 validate_lifecycle 주석을 정정했다.

새g5-trust-rest는 formal._job_run의 stopped return1arc와 FormalEngineMixin의 transition lexical guard·세machine등록None·trust_check 초기guard·같은K원문변경·최종게시오류8arc/10행을 맡는다. 정확좌표/SHA는 task gap-scope.json, 수용원근거는 g5-trust/evidence/{remaining-scope,coordinate-judgment}.json·final1/raw다. core_engine._register_execution/dispatch/review/SessionSlots는 자기시작판의 읽기전용 제공자다. uncapped만으로 None불가능을 단정하지 않으며, 현재성/종료/원결과보존을 유지한다. g5-core-rest·g5-entry-io의 정의/소유는 고정하고 새쓰기교집합0을 확인했다. 실제선행은g5-trust뿐이다.

## 0075 당시 갱신: 상태 적재 계약과 실제 실행 입구

dispatch_engine._dispatchable은 같은action을먼저거절하고 planning.task_ready가 다른action의미종료실행/queue/대기로not_ready를반환한다. 같은과제연구의뒤중복검사만없앴다. lifecycle_engine._limited_recovery_control은역할/정확프로필을승인하며 _recovery_action_basis가role/profile_ref를승인hash에포함한다. _check_limited_recovery는그binding·원승인·pause·기한·현재프로필identity·권한/능력을계속검사한다. _apply_extended_control의config객체형은공개control_contracts검사를소비한다.

core_engine._register_execution→SessionSlots.acquire의성공입장은launch_ticket을공급하고실패는None이다. lifecycle_engine._release_machine_execution은그ticket을mark_returned하며release_or_hold의실제종료장벽을유지한다. 실제owner_thread종료/재호출/저장시험은OS자식종료증거가아니다. 기존종료시험은KeyboardInterrupt의정확사유calculation interrupted와원결과/정산을고정했다.

state_checks.inspect_state는Repository가적재검사한상태를받는다. core_engine.check는store.load뒤호출하고 _inspect_area.run이영역고유불변식/증거오류를보고한다. unknown영역과artifactreader부재는incomplete, 현재학술요구미완료는blocked다. 비artifact학술참조는적재시해소되고academic.evidence_record가해당기록을먼저소비하므로뒤reader래퍼를제거했다. 현재심볼은scripts/do_math/{state_checks,lifecycle_engine,dispatch_engine}.py와record_schemas/__init__.py:validate_semantics, 사용자설명은계약/운영-점검.md다.

새g5-entry-io는claude_worker/codex_worker의directJobroot, control_server.mcp_server_config가생산하는실제MCPchild·control_transport bareimport, operator_bootstrap/probe_cli main, scheduled_operator.run_engine의frozen manifest선택을맡는다. context_store.collect_outputs의파일reparse omission과file_io._replace_once/shared_reader/os_lock/PhysicalBoundary.check의비Windows경로도같은작업이다. 원19arc/35행·수용SHA/좌표는task gap-scope.json, 허용경로와실제선행g5-worker/g5-io는queue/task.json이다. 로컬T4입구결과를T3에수동합치지않고환경부재와계약상제외를구별한다. g5-trust/g5-core-rest의제공자는읽기전용이며새쓰기교집합0이다.

## 0074 당시 갱신: 호출 격리와 내부 수신 전제

call_engine.CallEngineMixin._prepare_call은 review admission 거절 때 새 실행 없이 현재 검토 자원 처분을 저장한다. _context의 GitStateStoreError는 저장소 전체 오류로 전파한다. SealedSubmissionError에 맞는 현재 impact_review wait가 있으면 원생산자의 진단으로 연결하고, 이미 impact_review_changed로 바뀐 경우 준비 중인 실행만 input_preparation/start_failed로 끝내며 원생산자의 wait를 보존한다. prepare_role_input/로컬 context.json 읽기는 Repository를 호출하지 않는다. _receive_call은 실패handler 뒤에도 공개pause와 원결과/정산을 보존하며 실패한live검토는 부모에 operating_review_unavailable과 wait를 설정한다. 제품 설명은 references/과제-착수조건.md다.

core_engine._review_recovery_control은 review_engine._review_cycle의 정확 cycle/knowledge_id 검사를 재사용한다. _validate_initial_retry는 원활동의 waiting 조건·predecessor·종료/예약·queue/진단겹침을 검사한다. activities.wait_for는 모든 배정실행 종료를 요구하고 assign_execution은 waiting을 거절한다. resume_activity가 대기를 해소해 ready로 바꾼 뒤 assign_execution이 working으로 옮긴다. core의 새주석은 이 순서를 압축해 부정확하므로 g5-core-rest가 정정한다.

_apply_extensions의 제품caller는 _apply_bundle_candidate다. 역할별 확장은 submission.extension_schema, observation_rules 과제대상 및 academic effect/지정grant는 submission._payload_issues가 검사한다. _validate_bundle_current→decision_engine._validate_decision_acceptance가 적용 전 과제계약 현재성을 검증하고 planning.CONTRACT_FIELDS에 required_external_effects가 포함된다. 공개schema/권한/현재성 검사를 유지하면서 뒤 중복방어만 제거했다. 입력검사와 적용caller 순서를 바꾸는 작업은 이 전제를 함께 유지해야 한다.

새g5-core-rest는 core91arc/124행과 external_engine/integration/retention/submission5arc/2행을 맡는다. 특히 submission 남김은 external_requests의 grant부재 검사조건이며 학술영수증 전체의 미검증을 뜻하지 않는다. 정확수용SHA/좌표는 task gap-scope.json, 허용쓰기/실제선행은 게시queue/task.json이다. g5-state·g5-trust 정의/소유는 고정하고 쓰기교집합0을 확인했다. 부분시험21개passing본문과 원좌표도달을 최종전체G5·실외부경계 성공으로 확대하지 않는다.

## 0073 당시 갱신: 게시·지식 수용과 Lean·신뢰 후속

delegations.prepare_application은 동일 delegation/case의 보존 basis와 현재 basis를 먼저 검사하고 새 basis SHA에서 ID를 정한다. integration._reviewed_impact_request는 중앙 봉인검사의 maintenance 단일응답/확장금지 전제를 소비하면서 원지정 action·독립성·계산/선언합집합 승인·실제 게시 영수증을 검사한다. submission.payload_issues는 slice 배열의 정수좌표를 원member에 되돌리며 container 오류의 전역반려는 유지한다. 제공/소비는 scripts/do_math/{delegations,integration,submission}.py와 scripts/이음새-정본.md §3에 연결된다.

knowledge.replace_knowledge가 동일 usable Lean 원문을 재사용할 때 create_candidate의 임시formal을 제거하고 원FR을 연결한다. knowledge_records.proposal_view는 저장참조가 결속한 환경과 trust_validation.ENVIRONMENT_REQUIRED의 allowed_axioms를 직접 읽는다. retention._run_path는 check_path_segment와 _physical의 reparse반려를 소비한다. review_cycle.accept_result는 next_actions의 정확 action 뒤 continuity break/grant ID/hash를 확인한다. review_engine._research_source_spec는 저장 sources의 필수 path/sha256을 검증하고 fixed_research_reference_path가 None 아닌 경로를 준 경우에만 새보존증거를 추가한다.

정책검증의 실제정본은 initialization.activation_requirements→review_policy.build_review_policy이며 lifecycle_engine._activate_initialization가 소비한다. _retry_review_initialization는 활성상태·채택hash·보류formal의 현재성을 확인한다. 통합된 제품문서의 activation_gaps라는 없는 이름과 validate_lifecycle 주체주석은 작은미해결이며 g5-trust가 정정한다. 공용문서에서 없는심볼을 새계약으로 해석하지 않는다.

knowledge.BASIS_FAMILIES→_basis_records→_apply_impact_effects의 generic else는 kind-definition/trust-environment에도 닫힌형식 밖 input_current/use_history를 쓰는 가능성이 있다. 실제 영향생산자/참조방향·보존/무효화 의미는 아직미확인이다. g5-trust가 합법적도달과 의미를 먼저판정하며 형식확장을 미리요구하지 않는다. invalidate_environment의 독립active use 조건도 같은task다. record_schemas/schemas.py·trust_validation.py와 knowledge 제공/소비는 필요시 함께수리하되 running의 record_schemas/__init__.py·lifecycle_engine.py는 읽기전용이다.

새g5-trust는 formal.py/formal_engine.py/setup_lean.py의43arc/68행과 위knowledge2arc/1행·관련시험/helper·설명/미러를 맡는다. 정확SHA/좌표/허용경로는 task gap-scope.json/task.json, 실제선행은 g5-full/g5-publish다. g5-calls/g5-state의 정의·소유는고정하며 새정본36/미러36경로와교집합0이다. 제출판41passed는부분T3이며 최종전체G5나 실제Lean/G7 성공이 아니다. publish의나머지5arc/2행 및 worker/IO환경남김은 후속계약/경계묶음이다.

## 0072 당시 갱신: CLI·수송 입력과 수명/상태 후속

do_math.control_transport.ControlTransport.receive는 공개 입력의 객체형을 먼저 확인하고 _validate_request에 전달한다. 같은 검사만 내부에서 제거했다. publisher의 preview 객체·최종 accepted/rejected·published=true/비빈 snapshot 검사는 유지한다. 배달 중 파일소멸은 다음요청 처리를 막지 않으며, 거부 영수증 소멸은 RuntimeError로 보고한다. 손상된 state/outbox는 정확 사유·원bytes·closed의 unsettled_deliveries로 남긴다. unit/test_worker_control_branches.py가 OS파일 호출 경계만 제어해 이 계약을 단언한다.

do_math.cli.main→build_parser→execute는 닫힌 command 목록을 소비한다. 마지막 operator arm을 펼쳤으며 scheduled_operator.execute도 main의 check/run-engine/wake choices와 CLI의 고정 dispatch를 소비한다. LocalCLIAdapter.collect의 parse_response는 claude_adapter.ADAPTERS에 등록된 CodexExecAdapter/ClaudePrintAdapter가 제공한다. 호출되지 않는 기본 NotImplementedError만 제거했다. 공개 parser·등록되지 않은 provider 반려는 유지한다.

cli._control은 접수 후 아직 결과가 없으면 pending engine processing/next_owner=engine, 계약오류면 같은 request_id와 contract_error/next_owner=maintenance를 반환한다. cli.main의 파일 읽기/UTF-8/JSON 오류는 접수 전 input_error다. cli.execute의 HOLD는 wake 취소 OSError에도 hold_still_blocks_wake=true와 원오류를 보존하고 다음 wake는 held다. references/CLI-실행-계약.md와 실제 저장/재처리·원bytes 단언이 연결된다.

operator_bootstrap.freeze는 함수가 생성한 고정 .building-UUID와 file_io.no_reparse 확인 뒤 cleanup한다. startup_evidence의 unavailable은 frozen identity/manifest bytes를 유지하며, scheduled_operator.run_engine는 다른 설치 manifest를 spawn 전 반려한다. 사라진 live설치/다른manifest 시험은 실제 frozen runtime의 자동 manifest 선택 성공을 대신하지 않는다. g5-worker/evidence/gap-disposition.json의 남은13arc/25행은 worker/control_server/control_transport/operator_bootstrap/probe_cli의 직접 script/import 및 scheduled_operator.run_engine frozen manifest 경로다. 작은 실경계/지원계약 처분은 후속이며 T4 자식 도달을 T3로 합치지 않는다.

새g5-state의 제공범위는 dispatch_engine·engine·lifecycle_engine·record_schemas.__init__·repair_execution·repository·state_checks의 지정33arc/29행과 직접시험/helper·계약/운영-점검.md·미러다. 종료시험의 기존 unpinned_rejection1건도 함께 수리한다. 정확한 파일·좌표·수용SHA는 task gap-scope.json, writes는 task.json이다. 진행중g5-publish/g5-calls 정의·소유는 유지하며 core_engine/call_engine와 그helper/공유문서는 읽기전용이다. 각시험슬롯1로 합계3이고 전체관문·Lean/신뢰·실환경은 남는다.

## 0071 당시 갱신: 호출 준비와 입력·권한 경계

RevisionEngineMixin._selected_action_current는 planning.task_ready로 선택계약/승인/대기를 확인한다. CallEngineMixin._prepare_call은 처음 개정대기·현재성·goal basis와 입력준비 뒤 stop/설치/input_head 검사를 유지하며 같은상태의 중복 준비성/개정/basis 확인을 제거했다. 성공한 provider_engine._provider_admit→SessionSlots.acquire는 예약과 starting 전이를 candidate/원execution에 함께 반영한다. classify_run/collector는 completed/failed/stopped를 공급하고 _receive_call이 처리한다. handler 뒤 pause/close guard는 미완료로 남아 g5-calls가 판정한다.

payloads.decode→_decode_snapshot→_read_json_blob은 실제 canonical bytes와 SHA256 또는 이미 검증된 불변artifact 경계를 소비한다. size는 root에서만 공급되므로 뒤중복 길이확인을 제거했다. _decode_snapshot.visit의 active/seen 순환방어는 유지하되 실제 검증된 내용주소 그래프에서 hash fixed point/cycle 구성이 필요한 두경로만 사유있는 제외다. 공개출력/schema 불변이며 실제 DAG 중복은 반려한다. 제외는 원설계5.5/현재위협모델 한정이고 임의그래프에 대한 무결함 주장이 아니다.

governance.apply_decision은 control_contracts.validate_decision_shape가 검사한 GRANT 입력을 소비한다. governance_engine._configure_candidate는 host교체의 live/예약 반려와 model_selection 초기화 뒤 profile을 교체한다. planning.evaluate_condition은 validate_condition 뒤 닫힌문법을, task_contracts.validate_plan_dispositions는 returned-task집합을, session_slots.acquire는 budget.plan_reservations의 host/concurrency conflict만 소비한다. revisions의 반복계속은 history/dispatch한도만 해소하고 waiting_actions의 입력·권한·게시 대기는 소유자가 유지한다. 실제정의와 references/과제-착수조건.md가 연결된다.

g5-inputs/evidence/scope-coordinates.json은 원66arc/66행의 처분이다. 43raw arc도달과1예외대상행 도달은 다르며 제거15/제외2/남김5를 분리한다. part1~7은 서로다른 부분판이며 모두successful=false/exit1이다. 현재call남김은149→150,177→180,558→589,568→589,584→589와 행150/151/180/183/205다. 실제review등록0회였던 표본은 철회되어 그경로를 입증하지 못했다. 원coverage·모듈SHA·최종시험AST의 한정검수는 managers/0071/verification-review.json이다.

진행중 g5-worker/g5-publish의 정의·사본·쓰기소유는 고정한다. 새g5-calls는 core_engine/call_engine와 직접시험/helper·README/착수조건/초기화정비 설명·미러를 소유한다. 정확경로는 gap-scope.json/task.json에 있다. scripts/이음새-정본.md는 publish 소유로 읽기전용이다. 선행g5-core/g5-inputs는 실제 수리/좌표결과이며 시험슬롯 worker1·publish1·calls1로3이다. 나머지7core모듈·Lean/신뢰·환경·최종관문은 후속이다.

## 0070 당시 갱신: 커서 형식과 내부 읽기 전제

core_engine.query_records의 커서는 URL-safe Base64 JSON 객체이고 정확한 parameters/snapshot/last 키를 가진다. parameters는 instance_id·kind·text·related_to·direction의 조회 객체, snapshot/last는 비어 있지 않은 문자열이다. 형식 오류는 ValueError("invalid cursor"), 조회조건/명시snapshot 변경은 ValueError("cursor query or snapshot changed"), 고정조회에 없는 last는 ValueError("cursor does not name a record in the fixed query")다. 페이지 limit 변경은 허용하고 head가 전진해도 커서snapshot을 읽는다. 실제 반환은 snapshot/total/loaded/truncated/items/query_basis/next_cursor이며 각 item의 기록과 저장bytes 근거를 유지한다. 정의·관련 설명은 scripts/do_math/core_engine.py:query_records 및 scripts/이음새-정본.md의 공개 레코드 조회 절이다.

ResearchEngine.__init__는 installation_root/store/load 뒤 _init_process_state를 호출한다. GitStateStore는 PhysicalBoundary의 디렉터리·물리root 검사 뒤 사용하며 check/use threat model은 불변이다. lifecycle_engine은 StateContract의 validate_lifecycle가 확인한 last_observed_utc와 허용 lifecycle 상태를 소비하고, record_schemas._lifecycle_references는 스키마 검사 뒤 필수 input_id를 읽는다. repository._decode_families는 read_payload keyword가 필수이며 _descriptors/_read_documents가 봉인payload reader를 공급한다. 여섯 중복 방어만 제거했으며 공개 입력·저장 경계 검증은 유지한다.

g5-core/evidence/t3-changed와 t3-extra는 별도 부분측정27passed/11passed·gate=false/exit1이다. 소유제품11SHA는 동일하고 첫 측정 뒤5시험 파일은 달라졌다. 최종913PythonSHA만 제출판과 모두 같다. 원좌표의87arc/99행도달·6arc/6행제거·165arc/197행남김은 coordinate-judgment.json과 remaining-scope.json에서 현재함수/좌표로 이어진다. managers/0070/verification-review.json은 원coverage·SHA·실제행과의 대조다. 과거 원좌표 처분을 새 커서 분기까지 포함한 전체G5 결과로 세지 않는다.

진행중 g5-inputs/g5-worker의 정의·사본·배정은 고정한다. 새 g5-publish는 delegations/external_engine/integration/knowledge/knowledge_records/retention/review_cycle/review_engine/submission 및 소유직접시험/helper/이음새설명과 대응미러를 맡는다. 정본117/미러117의 정확한 상한은 task.json/gap-scope.json이다. unit/test_review_wait_contract.py는 g5-inputs 소유로 읽기전용이며 필요시 허용한 publication_branch_contracts/publication_branches에서 제공자를 소비한다. core_engine/schema/lifecycle 남김은 이 task의 수정범위가 아니다. 선행은 g5-full뿐이고 inputs1·worker1·publish1 시험슬롯을 유지한다. 이후 core잔여·Lean/신뢰·환경 처분과 최종G4~G8은 남는다.

## 0069 당시 갱신: I/O 불변식 단순화와 환경 남김

context_store.safe_path는 relative_path→_physical_root/no_reparse의 경로검증 뒤 candidate를 반환하며 중복 resolve/탈출검사는 없다. materialize_inputs/write_source_catalog도 같은 물리root 검사 뒤 작업한다. 이 함수들은 PhysicalBoundary가 명시한 check/use 변조 보장 범위를 확대하지 않는다. prepare_role_input의 planning 입력은 reader_tasks/runtime.tasks 집합동등성과 ready ID 유효성 검사 후 reader_task가 원문을 deepcopy한다. profile/snapshot/governance·review seat 원문·resume action/owner 반려는 유지한다.

file_io.atomic_replace는 첫5회 재시도와 최종1회로 구성된다. 지연0/.01/.025/.05/.1/.2, Windows5/32/33에서 동일source/destination 재시도, 그밖/마지막오류 전파·원bytes 보존을 유지한다. shared_reader는 CRT descriptor 전환 실패 때 native HANDLE을 닫는다. PhysicalBoundary는 경로/volume identity·NTFS 등 실제OS 판정을 유지하며 직접시험은 해당 OS 경계만 대역으로 제공한다.

observations.observe는 due boundary를 consumed_rules에 기록한 뒤 _self_check_obligation을 호출하며 규칙 revision/최대간격 basis로 새로운ID를 만든다. 중복ID 반환은 제거됐다. parallel.ModelCalls.start_call/_observed는 future별 callback을 고정한다. _apply_observations는 같은callback identity 재검사 없이 인자수/ObservationBatch·stream·barrier·수신시각·row 연속성을 확인해 합친다. scheduler의 _run_machine_steps/_call_steps는 등록된 execution_id를 공급하고 _abort_parallel_calls는 각 결과의 canonical JSON을 execution-recovery/ID/returned-result.json 및 기존 저장소 result_ref로 보존한다. 공개API/record/schema 변경은 없다.

g5-io/evidence/final1/raw와 final2/raw는 부분T3 측정이며 각각53passed/1passed, 제품동일·시험판상이·gate=false·exit1이다. gap-disposition.json의 원좌표/현재좌표/측정 연결은 managers/0069/verification-review.json에서 원coverage와 대조됐다. 최종docstring2개는 실행AST가 같다. 수치의 합은 전체G5가 아니며 이전전체G4를 변경된판의 성공으로 재사용하지 않는다.

collect_outputs의 원185→186/186~188행은 수용판182→183/183~185행이다. 파일symlink/reparse_file omission의 실제조건은 WinError1314로 미확인이다. file_io의 비Windows 원66→67,95→96,142→146,156→159,337→-333은 현재69→70,98→99,145→149,159→162,340→-336이다. 실제non-nt 측정 또는 지원범위/설계5.5의 구체처분이 남는다. directory junction·권한probe·별도child/T4 자료를 이T3도달로 세지 않는다. 구체 환경/경계 배정으로 이어가며 내부플랫폼패치/가짜fcntl/새skip은 없다.

g5-core와 g5-inputs의 기존 writes/objective는 고정한다. 새g5-worker는 claude_worker·cli·codex_adapter/codex_worker·control_server/control_transport·local_host/provider_final/reporting·scheduled_operator·operator_bootstrap/probe_cli와 소유직접시험/helper/CLI-실행-계약.md 및 대응미러를 맡는다. 정확한70정본/70미러는 task.json/gap-scope.json이다. core 소유 control 수송시험/helper를 수정하지 않고 필요시 허용한 worker_control_branches 시험/helper에서 같은 제공자를 확인한다. g5-full만 실제선행이며 세task는 각시험슬롯1이다. 미배정 게시/지식/검토·Lean/신뢰는 다음슬롯해제 때 독립배정한다.

## 0068 당시 갱신: 전체 T3 미도달과 수리 소유

제품 API 변경은 없다. run_tests.py:main/_finish_t3의 원보고는 전체4288실제행·4287passed/Windows1314 skip1·fixture0·complete/successful=true지만 branch_gate.passed/최상위passed=false·runner exit1이다. branch_gate.py:gate가 현재LAYERS1~3층123모듈을 원coverage와 대조해55모듈517arc/653행을 남겼고 기존제외15행·unmeasured/measurement_missing0이다. closing_eligible와 selection_index 생성은 gate통과를 의미하지 않는다.

원 report/coverage/entered/opened/worker/store와 SHA는 tasks/g5-full/evidence/full1/에 있다. gap-inventory.json의 module·missing_branches/lines·현재source/scope와 followup-scope.json은 좌표/소유 제안이며 도달가능성·기능결함·제외의 사전 판정이 아니다. manager는 같은좌표와 현재공용 소스를 대조했다. 전체912PythonSHA와 선택은 수용G4와 같다. 구체 검수는 managers/0068/verification-review.json이다.

원 selection index는 tasks/g5-full/evidence/observed-caches/.claude/skills/do-math/scripts/tests/.selection-index.json에 보존돼 있다. 보고의 workspace 생성위치는 base로 복원됐으므로 사용하지 않는다. 4280비격리시험·함수map311파일/실제진입275파일·3202함수key·287input은 관측값이며 G6 대상모집단/단언성공을 새로 정의하지 않는다. 독립로컬HEAD의 타사본 조상관계를 가정하거나 색인을 수동 보정하지 않는다. G6 최종연결은 수리판 전체 측정 후에 한다.

g5-core는 core_engine·activities·dispatch_engine·engine·git_store·lifecycle_engine·maintenance_gate·record_schemas/__init__·repair_execution·repository·state_checks와 직접시험/helper, README/정비/공통이음새를 소유한다. g5-inputs는 call_engine·governance/governance_engine·payloads·planning/planning_engine·provider_engine·revisions·role_input_requirements·session_slots·task_contracts/task_scope/wait_rules와 직접시험/helper·입력소비자/착수조건 문서를 소유한다. g5-io는 context_store·file_io·model_runner·observations·operation_trace·parallel·scheduler와 직접시험/helper를 소유한다. 모두 정본과 대응미러를 함께 제출하며 정확한 쓰기 경로와 원좌표는 각 task.json/gap-scope.json이다. 공통helper의 범위밖 수리가 필요하면 파일·소비자·원반례를 남긴다.

세task는 각jobs1로 최소공식선택을 확인한다. 필요시 부분선택T3의 원coverage로 지정분기 도달을 확인할 수 있으나 다른모듈 gap/exit1과 전체G5는 구별한다. 독립Git 준비는 도구가 필요할 때 자기workspace/실소스에만 허용하며 생성cache는 보존 후base복원한다. 공유 OS권한·설치·실예약·유료호출과 전체관문은 배정 밖이다. 다음manager는 한 시험슬롯이 풀리면 준비된 나머지 세영역을 파일충돌에 맞춰 배정한다.

A22의 저장검증/공통구조/T3책임을 유지한다. 현재 계약의 불필요한 중복방어·죽은분기는 제거/축소를 우선 검토하고, 필요한 의도적미도달 제외는 설계5.5와 같은행 구체사유/구조검사로 판단한다. 무근거 no-cover나 새skip·임계값/층완화로 도달을 대체하지 않는다. 기존codec/업무근거를 재사용하며 가족별 전수 재입증은 추가하지 않는다. 제품수리 후최종G4/G5·G6~G8·실경계/환경 남김은 별도다.

## 0067 당시 갱신: 전체 G4 수용과 fresh T3 인계

제품 API 변경은 없다. g4-final의 기본 전체 선택은 run_tests.py:DEFAULT_FOLDERS=TIERS['T3']인 structure/unit/contracts/sim/flows를 일반 모드로 실행했다. selected4288=고유실제4288,4287passed/조건부skip1·fixture오류0·exit0이며 공용912PythonSHA/정본·미러2410파일과 같다. unit/test_context_catalog.py의 symlink_to OSError→skipTest는 WinError1314를 기록했다. G4 환경skip 인정과 실제 outside_symlink 반려 미확인을 구별한다. 원보고·검수·판본은 tasks/g4-final/evidence/full1/report.json 및 managers/0067/verification-review.json에 있다.

run_tests.py:main은 --tier T3에서 Measurement와 _t3_plan을 구성한다. --full은 증분 측정 재사용을 끄며 기본 전체 위치선택/match 없음이 G5 입력이다. _finish_t3는 measurement.finish의 분기 합집합에 branch_gate.gate(report['files'], LAYERS, prefix)를 적용한다. branch_gate.py:gate는 LAYERS의1·2·3층 중 absent module을 unmeasured, missing line/branch를 gap으로 남긴다. 자료누락·gap이 있으면 passed가 아니다. T4 adapter 측정은 이 분모/도달/함수진입에 들어가지 않는다.

run_tests.py:closing_eligible(args,clean,missing,plan)은 전체 선택·clean·missing없음·plan재사용0을 뜻하고 gate통과를 뜻하지 않는다. _finish_t3의 index생성도 clean/전체선택 조건으로 실행되므로 selection_index 존재만으로 성공을 판정하지 않는다. report의 branch_gate·measurement_missing·closing_eligible·t3_store, 실제rows/fixture/exit·source_sha256/changed_during_run을 함께 읽는다. branch_gate.py:write_index는 실제root/HEAD/blob 및 함수진입/input을 do-math-selection-index/2에 연결한다. 원색인은 G6 입력이므로 생성바이트/원경로/HEAD/SHA를 보존하고 수동 갱신하지 않는다.

새 g5-full은 자기 수용판에서만 독립.git/로컬실소스commit을 준비하고 새 외부store·출력으로 공식전체 --tier T3 --full --jobs3을 실행한다. g4-final/evidence/prepare.py가 성공한 준비 참고이며 다른task.git을 복사하지 않는다. 생성 index·timing·store는 원자료 보존 뒤 자기base로 복원해 제품 변경에서 제외한다. 미도달의 실제 관련 수리는 제공/소비·시험·설명·미러와 함께 처리하고 기존 G4와 최종판이 달라지면 G5 성공판의 일반검사도 같은task에서 연결한다. 쓰기 소유와 상세 완료조건은 tasks/g5-full/objective.md다. A22의 공통저장/구조/쓰기분기 역할은 유지한다.

## 0066 당시 갱신: 계약 fixture·단언·문서 수용

제품 runtime/schema API는 바뀌지 않았다. governance.validate_independent_execution은 continuation_of로 작성자 계보를 반려한다. repair_execution.resume_installation_repair는 원 action/repair_attempt를 보존한 후속을 준비하고 정확 waiting.condition으로 활동을 ready로 재개한다. revisions.action_repetition_waits는 repetition_bases의 세 계보와 revision_targets/observation_rule_targets의 제안·계약 판본 계보를 함께 소비한다. 이번 시험은 이 현행 계약을 구성하며 폐기 history/parent_execution_id/conversation_id를 복원하지 않는다.

tests/support/engine_context.py:issue(engine, execution, context, bundle, schema=None)는 실제 input/submission/context.json을 게시하고 execution.input_bundle을 설정한다. sim/test_scheduling_task_dispositions의 운영 검토 fixture가 이 기존 helper를 사용해 submission.issued_input의 실제 저장 읽기에 snapshot/action/sources를 제공한다. input_snapshot의 원 과제판과 현재 head의 immutable bundle을 구별한다. scheduled_operator.execute의 HOLD 결과도 startup을 operator/startup.json 전체와, 나머지를 held 동작 결과와 각각 대조한다.

tests/support/engine_lifecycle.py:task_wait_report()는 승인된 실제 과제 TK-status-wait와 research_followup 대기를 저장·재적재하고 현재 evaluation_context를 넣어 reporting.status_report의 dict를 반환한다. tests/support/doc_code.py:status_field_schema(report, *, task_report=None)는 주 응답의 top-level 필드를 유지하며, 주 응답에 tasks가 있고 별도 응답 또는 주 응답의 tasks가 비어 있지 않을 때만 그 원소 필드를 결박한다. 빈 배열만으로 waits를 증명하지 않으며 별도 응답으로 주 응답에 없는 top-level 필드를 추가하지 않는다. unit/test_storage_report_projections와 boundary/test_engine_cli가 실제 반환을 소비한다. unit은 정확 wait 내용과 waits 삭제·빈 배열의 문서 반려를 함께 확인한다.

tests/support/storage_execution_pairs.py의 assert_stored_delegation_input/assert_stored_provider_failure/assert_stored_unsealed_return_preserves_the_exact_rejected_candidate_and_check_refs/assert_stored_maintenance_archive_writes_termination_and_collection_before_local_cleanup/assert_stored_prepared_call_and_returned_evidence_keep_their_own_inputs_after_reload, storage_action_pairs.py의 assert_merge_samples가 실제 단언 역할을 드러낸다. 정의·모든 import/호출을 함께 바꿨고 구이름 별칭은 없다. helper/직접소비5모듈 전체의 역이름변환AST는 base와 같다. provider.1.json은 legacy ID를 보존하고 new_ids를 현행 native 조각·수신시각 재생 시험으로 연결한다.

focused1의 실제19행=16passed/3error·exit1과 입력 교정 후 focused2의 해당3passed·exit0은 별도 판본이다. 두 실행의 소스불변·원보고와 focused2 제출판912PythonSHA를 확인했다. 전체 G4 증거는 아직 없으며 두 선행을 수용한 기존 g4-final이 기본 전체 선택을 맡는다. 정확 검수 범위는 managers/0066/review.md·verification-review.json이다.

## 0065 당시 갱신: 자기 측정판 준비의 확인과 G4 인계

tests/support/branch_gate.py:repository_root(start=SCRIPTS)는 실제 git rev-parse --show-toplevel을, write_index(measurement, report, tests)는 measurement.root의 실제HEAD와 작업트리blob을 소비한다. run_tests.py:_finish_t3는 전체 선택·완결·소스불변인 실행에서만 write_index를 호출한다. g4-measurement의 작은 T3 meta는 selection_index=None이고 full write_index 성공이 아니다.

services/async-development/workspaces.py:SKIP/files/changes/integrate는 .git을 제외한다. g4-measurement는 자기workspace만 root로 삼는 독립.git/로컬commit을 준비했고 외부temp의 root조회는exit128을 유지했다. 제품bytes는 불변이며 지정meta7passed·fixture0·exit0이 확인됐다. 재현의 실제 명령/파일범위/ceiling/EOL·filter/바이트대조는 tasks/g4-measurement/evidence/prepare.py·git-preparation.json·judgment.md에 있다. 이.git/HEAD는 공용main이나 성공증거가 아니며 통합하지 않는다. 새 g4-final은 자신의 수용판으로 같은 준비를 수행한다.

tests/unit/test_adapter_coverage.py는 실제 child/owned worker의 측정과 publication6반례를 검사한다. 실패·skip·not_run/fixture오류 보존, 시험이 성공해도 worker자료 유실이면 adapter불완결/exit1, T4의 T3 gate/store 분리와 분모보존을 현재 단언 그대로 확인했다. 부모의7passed와 유지된자식11passed가 근거이며 임시정리된 다른 자식 원파일의 별도보존은 주장하지 않는다.

g4-final은 수용된 g4-contracts·g4-measurement만 직접 선행으로 소비한다. 남김은 시작 시 report/수용맥락에서 확인해 관련수리와 전체확인을 한 task에서 처리한다. 기본전체jobs3은 run_tests.main의 _run_parallel 완료 뒤 resource클래스별 _isolated를 순차 호출하므로 현재 adapter meta내부jobs2와 겹치지 않는다. 일반G4/freshT3/전체T4·T5의 완료 의미는 구별하고 전체G4 성공은 아직 없다. 진행중g4-contracts의 인터페이스/쓰기소유는 변경하지 않았다.

## 0064 당시 전체 일반 부분 수용과 실패 수리 경계

tests/support/submission_owner_obligations.py:OwnerIngressAssertions.reject_and_replay는 잘못된 출력/확장 원bytes를 실제 submission.producer_check에 먼저 검사하고 같은 입력을 중앙 receiver에 전달한다. flows/test_submission_ingress_owner.py의 확장가족 시험은 rows×item_shapes=15회와 helper 모듈 caller를 모두 대조한다. 중앙 정확반려·원내용저장·소비1회·재전달·뒤정상수락은 유지한다.

do_math/scheduled_operator.py:execute는 bootstrap/installation/runtime_root/observed_at의 startup을 operator/startup.json에 게시하고 동작 반환에 startup을 더한다. run_engine이 저장하는 operator/latest-engine.json은 동작 결과다. flows/test_engine_cli_conditional_journey.py는 두 파일을 해당 반환 부분과 각각 전체값 대조한다. sim/test_operator_finish_cli의 HOLD 소비자에도 동일 계약을 반영할 후속이 남는다.

tests/support/branch_gate.py:repository_root(start=SCRIPTS)는 git rev-parse --show-toplevel, write_index는 measurement.root의 HEAD와 작업트리 blob을 써 do-math-selection-index/2를 만든다. 현재 async workspace는 .git이 없어 adapter meta가 초기화에서 실패했다. services/async-development/workspaces.py:SKIP/files/snapshot은 .git을 제외한다. g4-measurement는 자기 workspace에 독립 .git/로컬 기준commit을 준비할 수 있으며 제품 bytes 불변/root·HEAD/실행판SHA를 연결한다. 이 사본 commit은 공용 main/성공을 뜻하지 않는다. 상위 Git 탐색을 허용하거나 가짜 HEAD/새 비Git fallback을 먼저 넣지 않는다. 실제 준비·7행/fixture의 성공은 후속 확인 사항이다.

g4-contracts는 폐기 history/parent_execution_id/conversation_id를 현재 저장·continuation_of/형식실행 관계로 바꾸고 submission.issued_input의 실제 input_bundle·봉인 context/snapshot 소비를 복구한다. action의 세 repetition_bases와 revision_targets/observation_rule_targets의 판본 계보를 구별한다. storage_execution_pairs/storage_action_pairs의 실제 단언 정의·소비자, doc_code.status_field_schema의 빈 배열 한계와 실제 비빈 task waits, 문서 함수 참조/이행 원장 new_ids는 같은 작업자가 맡는다. runtime 변화가 필요하면 현재 원인/계약을 보고하며 구판 필드를 복원하지 않는다.

두 task의 제품 쓰기 경로는 겹치지 않는다. contracts는 runtime/지정시험·저장helper·doc_code/README/CLI/이음새 문서, measurement는 runner·branch_gate/adapter_coverage/selection/t3_store·직접시험/시험지침을 소유한다. 정본/공식미러를 함께 제출하며 캐시는 evidence 보존 후 base복원한다. 시험슬롯은 contracts1·measurement최대2다. 전체G4 성공·G5 freshT3는 후속 통합판에서 별도로 확인한다.

## 0063 당시 현재성 판정 수용과 전체 일반 검사

core_engine.submit_control은 supplemental_research의 runtime.tasks 대상과 planning.task_ready를 접수 시 검사한다. CoreEngineMixin._apply_inbox는 적용 때 같은 준비 조건을 다시 평가하고 없거나 not_ready면 `supplemental task is no longer ready`로 _reject_control 후 continue한다. _reject_control/_record_control_result는 processed_controls와 원request deepcopy·정확 사유·rejected 결과·publication_parent history를 저장한다. _inbox는 소비한 ID를 다시 적용하지 않는다. planning.evaluate_condition은 과제가 참조한 review-cycle 상태를 현재 record에서 읽으므로 무관한 cycle 종결과 실제 발생조건 소실을 구별한다.

review_engine._defer_review_for_research가 생산하는 knowledge target/review_cycle_id/research_request_id 결속 조사는 공개 task 요청과 별개다. knowledge_engine._knowledge_control의 공개 revise/invalidate, knowledge의 관련 queue 은퇴, review_engine._obsolete_review_reason/_pending_review_research와 call_engine의 준비/회수 경계가 종결/개정된 조사를 취소하거나 원결과로 보존한다. task_scope.apply_task_dispositions는 task record를 지우지 않고 closed/원처분/이력을 남긴다. retention.cleanup의 실제 rmtree는 승인된 local runs 디렉터리에 한정되고 execution map/보관원문은 남는다. 현재 확인한 task/execution/review-cycle 대상 공개삭제 생산자는 없다. 원 A-02 두 질문의 정확 판정/범위는 tasks/control-currentness/evidence/judgment.md와 managers/0063/review.md다.

g4-general은 run_tests.py:DEFAULT_FOLDERS=TIERS['T3']를 기본 선택으로 실행한다. 위치 인자/--tier/--match 없는 일반 실행은 structure/unit/contracts/sim/flows이며 측정 T3, boundary, smoke를 포함한 전체 인증이 아니다. run_tests.main이 기록하는 selected와 reports[].rows, counts/fixture_counts, complete/successful, source_sha256/changed_during_run 및 실제 exit를 함께 소비한다. scripts Python 해시 밖의 문서/공식 미러 판본은 별도 연결한다. skip/expected_failure는 passed로 세지 않으며 계약상 정당성을 판정한다. 이번 단독 일반 실행은 --jobs 3으로 기계 시험슬롯3개를 쓰고 다른 시험과 병행하지 않는다. 수리는 같은 task의 정본/미러 범위에서 마치며 실제 최종판 G4 수용 뒤 fresh T3로 넘긴다.

## 0062: 복구 저장 수용과 A22 범위 교정

CoreEngineMixin._recover_disappeared(core_engine.py)는 `_preserve_outputs` 뒤 `_settle_recovered_execution=False`인 경우에도 `_save(artifacts)`로 output/checkpoint 참조와 실제 bytes를 함께 게시한다. stopping·미정산 예약·원격 unknown은 보존한다. runtime.recoveries는 ID map이고 시작 execution_ids 순서·각 disposition·finished_at을 담는다. finished_at은 순회 완료다. 미생산 dispositions[].disposition은 허용하지 않으며 local_termination_confirmed/reason/next_owner/fact의 현재 의미를 유지한다.

record_schemas.__init__.REFERENCES['operational_dispositions']는 reviewer execution_id와 target_execution_id 모두 executions로 검증하고 question_id는 question_links로 확인한다. schema의 root applied_at/error는 미생산이라 제거했다. CoreEngineMixin._apply_operational_disposition/_complete_operational_disposition/_run_pending_operational_repairs와 repair_execution이 쓰는 원제안·obligation_ids·created_at/status·조건부 result/question_id는 유지한다. proposal의 도메인 검사는 operational_dispositions.validate_disposition→contracts.disposition_schema를 사용하고 열린 disposition/result EVIDENCE를 임의로 닫지 않는다.

maintenance_gate.apply_control/settle은 공개 원request의 id/origin/text/created_at을 fence request_id/origin/reason/created_at으로 보존하고 draining→blocked/quiescent 및 pending_executions/held_reservations/settled_at을 쓴다. 같은ID·허용origin·종료장벽을 확인한 release는 singleton을 지우고 원fence를 history에 남긴다. user_pause는 별개다. provider_engine.record_model_policy_violation은 실제 _receive_call의 배정/원결과 모델들을 복사하고 미종결 연구만 paused로 둔다. lifecycle의 명시 resume이 marker를 제거한다.

tests/support/storage_recovery_pairs.py:reader/StoredRecoveries.keep는 별도 installed_contract reader의 첫 load로 검증 게시와 옛head·manifest shape/부재를 확인한다. family_pair/proposal_pair는 기존 contracts.pairs.Pair/assert_pair와 storage_authority_pairs._named_fields에 실제 저장표본을 연결한다. recoveries11·operational_dispositions9·proposal17·fence8 명명필드와 실제 optional 추가3반례를 확인했다. 열린 model_policy_violation은 원내용/배정·중첩격리·재시작/제거로 판정한다. tests/contracts/test_storage_recovery_pairs.py의 복구 fixture 두 종류는 정상 자동 admission 생산 증명이 아니며 모든 쓰기분기/final판은 freshT3에 남는다.

사용자 추가 지시와 원설계3.3/A22에 따라 storage-questions/storage-task-state의 전가족 배정을 미시작 취소하고 storage-readiness 초안을 게시하지 않는다. 기존 정의·시험·원보고는 보존한다. ResearchRepository.validate_candidate/save_with_state/load의 실제 검증, tests/structure/test_storage_fields.py의 event 필드/제품 이름 검사, tests/unit/test_storage_codec_properties.py의 실제 codec/새contract/원bytes 보장을 공통으로 재사용한다. 이름 검사의 알려진 한계를 전생산자 실행 증명으로 부르지 않으며, 모든 가족의 새 장면을 그 대가로 요구하지 않는다. 쓰기분기 도달은 fresh T3가 맡는다.

새 control-currentness의 실제 연결은 control_contracts.REQUESTABLE_ROLES/PAYLOADS→core_engine.submit_control→CoreEngineMixin._apply_inbox다. 공개 supplemental_research는 runtime.tasks의 target과 planning.task_ready를 검사한다. 원 A-02의 review-cycle 직접 대상과 같은 의미인지, 현행 과제 개정/철회·검토 종결이 어떤 현재성 변화를 만드는지를 r08/r41의 실제 코드·단언으로 판단한다. 공개 삭제 생산자가 없다면 역사 입력을 임의 del/새API로 재현하지 않는다. 실제 입력/적용 사이 전제 소실에서 정확 반려·소비1회·뒤 pause 적용이 부족할 때만 기존 직접시험/제공자를 고친다. 대규모 가족 감사와 다른 public action 전수 재검토는 배정 밖이다.

기존 초기화 capability_evidence/review_policy, 질문/이력, 과제/규칙, checkpoint/외부처분의 저장 인터페이스를 바꾸지 않는다. managers/0062/scope-review.md가 재사용 근거와 한계를 연결한다. 과거74/84는 수행이력이며 현재 종료조건은 아니다. 관찰4/다른원요구/K/P2·G4~G8·L01/Windows1314·최종review는 별도다. 아래 번호별 절은 당시 이력이며 현재 판단은 이 절과 plan/queue 및 실제 정의를 따른다.

## 0061 공통 action 저장 필드와 과제 후속

tests/support/storage_authority_pairs.py:_named_fields는 boolean schema에 명명 의무가 없는 의미를 처리하고 object properties·map additionalProperties·배열 items/tuple prefixItems·nullable/anyOf/oneOf/allOf 및 if/then/else를 같은 함수로 순회한다. values가 주어지면 실제 존재하는 필드/원소만 생산된 것으로 센다. 빈 container가 자식 optional을 생산한 것으로 처리되지 않는다. 기존 contracts.pairs.Pair/assert_pair와 실제 schema optional 추가 반례를 유지하며 별도 registry/부분집합 면제는 없다.

storage_action_pairs.action_pair/actions는 runtime.queue, executions.action, waiting_actions.action, input_overflows.action, review_cycles.replacement_actions.authority_request의 유효 공통 수신을 모은다. waiting_pair는 전체 waiting schema로 수신을 검증하면서 action을 공통 Pair에 맡기고 행 자체의 의무를 검사한다. 공통action86최상위/171명명필드와 waiting24최상위/행52명명필드, 실제 queue75최상위·56저장상태를 구별한다. reader/keep와 StoredActions.read는 다른 installed_contract reader의 첫 load로 게시 blob을 decode하며 원내용·옛head의 기존 단언을 소비한다. 모든 자동 쓰기분기/freshT3 증거를 뜻하지 않는다.

record_schemas.schemas._ACTION은 미생산 activity_id/execution_id/created_at을 허용하지 않고 repetition_bases는 bind_repetition_bases가 실제 생산하는 import_rework/selection_failure/exhaustion_empty다. waiting행의 condition/waiting_reason/recovery도 미생산이라 제거했다. 원 owner는 action.owner_activity_id, 해소 조건은 activity.waiting.condition, 검토 복구는 waiting.detail이다. planner action.input_overflow의 without_restored_dialogue_bytes만 제외하며 공통 _OVERFLOW와 input_overflows.detail은 실제 검토 측정을 유지한다. action.reason은 생략/문자, waiting.reason은 실제 runner 오류 부재의 null도 보존한다. CoreEngineMixin._enqueue의 binding 전 전체 deepcopy와 병합/ID/lineage/live 의미는 유지되고 최초 삽입의 중복 payload 복사만 없어졌다.

기존 storage-recovery는 이 수용판을, storage-questions는 recovery의 core/call/schema/직접시험/설명을 소비한다. 정의와 objective를 바꾸지 않았다. 새 storage-task-state는 questions 수용판을 받아 runtime.tasks ID map과 task_observation_rules singleton mapping의 계약을 함께 맡는다. contracts.task_candidate_record/CoreEngineMixin._apply는 원 후보와 과거 계약을 연결해 과제를 생산하고 task_scope의 평가/처분과 PlanningEngineMixin의 model metadata/계획·개정이 그 값을 소비/갱신한다. CoreEngineMixin._apply_extensions와 observations.task_rules_from_execution은 실제 제출 규칙의 실행 subject를 재사용 $execution으로 보존하며 bind_task_rules/CallEngineMixin._prepare_call는 다음 실행에 바인딩한다. 과제 개정·평가 판본 변경에서 규칙 제거/재준비를 연결하고 task.initial_observation_rules·live tracker 규칙과 runtime map의 서로 다른 소유를 보존한다. 같은 producer/schema/helper/설명 수리를 한 task가 맡으며 충분한 이전 권한/현재성·정산 근거는 재사용한다.

원84 중70지정질문 충족·recovery4/questions4/task2배정·미배정4와 관찰4/최종관문을 구별한다. 아래 번호별 절은 당시 연결이며 현재 판단은 이 절과 plan/queue를 따른다.

## 0059 종류 표본 수용과 질문 저장 후속

tests/support/storage_kind_checks.py:kind_scene/propose_kinds/kind_checker는 실제 종류 제안·독립 검사 준비의 정본이다. 입력 helper/직접시험과 ontology helper가 함께 소비한다. 이 helper가 두 소비자를 import하지 않으므로 input→authority._named_fields 방향은 유지된다. kind_checker는 _context가 준 현재 정의/hash로 등록된 maintenance 실행의 input_basis를 만들고 실제 lifecycle로 종료한다. 모델/native 수송은 기존 시험 입력이며 실외부 호출 증거가 아니다.

storage_authority_pairs._core_kind_check_samples는 core unresolved 판정의 _save 뒤 매번 새 installed_contract/ResearchRepository로 첫 decode하고 생산값·옛 proposal head를 비교한다. 이 두 표본은 기존 ontology_samples 앞에 들어가 기존 최종 관계 표본의 위치를 보존한다. family_pair의 모든 닫힌 필드 역방향과 기존 Pair/assert_pair는 그대로이며 check의 열린 내용은 원 ID/hash/decision/findings/실행ID와 checker input_basis로 독립 대조한다. check는 현행 저장 필드이고 나머지11미생산필드는 여전히 정확 반려한다.0058의 F2 남김은 이 수용으로 해소됐다.

후속 storage-questions의 question_links는 record_schemas.schemas.RECORDS['question_links'] list item이다. questions.link는 원 execution/field 기준으로 같은 owner/대상/blocks의 재전달을 재사용하고 조용한 재경로를 거부한다. questions.close는 affected_ids만 미해소 목록에서 빼고 resolution_history에 기록하며 마지막 대상이 해소될 때 status/resolution_ref를 바꾼다. resolve_user는 현재 열린 사용자 질문과 실제 affected_ids를 확인한다. QuestionEngineMixin._apply_question_resolutions는 허용된 owner/role·원 증거를 검사하고 사본을 갱신한 뒤 목록을 교체한다.

question_engine.question_view는 저장 source_ref의 artifact, intent_import/review_cycle/history 또는 execution 원자료에서 origin_field를 따라 원문을 읽는다. 원자료 부재는 반환 view의 text=None/source_status=unavailable이며 저장 record 필드가 아니다. runtime.questions는 array(TEXT), history는 열린 HISTORY의 singleton이다. CoreEngineMixin._check_installation은 판본 불일치 안내문을 중복 없이 questions에 추가하고 저장한다. _apply_inbox 및 실제 실행/제어 owner가 history를 쓰므로 원request/실행·내용·순서를 독립 값으로 대조해야 한다.

CallEngineMixin._prepare_call은 실제 포장 초과의 action/detail/source_catalog를 runtime.input_overflows item에 쓴다. 일반 분기는 원overflow artifact·question link·waiting action·현재 owner 처분과 연결하고, identity_review의 현재 제안/필수자료 초과는 review resource 처분으로 넘긴다. 공유 _ACTION과 detail _OVERFLOW의 현재 계약, 열린 source_catalog 원내용을 구별하며 한 가족의 표본 부재로 공통 필드를 제거하지 않는다. 새 task는 storage-actions→storage-recovery가 바꾸는 core/call/중앙schema/직접시험/제품 설명의 수용판을 받는다. 기존 배정과 실행 중 사본은 바꾸지 않는다. 아래 이전 번호별 인터페이스 설명은 이 갱신과 실제 정의를 함께 읽는다.

## 이번 세 읽기의 실제 연결과 보고 경계

- r02: `do_math/model_runner.py:ModelRunner` 및 현재 adapter의 요청 조립, `worker_request.py`의 `check_codex_request`/`check_claude_request`, `codex_worker.py`/`claude_worker.py`의 load 경계가 대상이다. `tests/contracts/pairs.py:_worker_request_samples`와 `test_pairs.py`의 required/optional 역방향 단언이 실제 저장·수신까지 무엇을 입증하는지 구별한다. 이 문서는 새 요청 schema를 정의하지 않는다.
- r07: `tests/structure/test_schema_builders.py`의 `_calls`, `_composition_calls`, `_constant_object_calls`, `TRANSFORMERS`, `DELEGATED_SCHEMA_METHODS`가 현 등록이다. 실제 contracts/control/record schema와 engine·review_cycle·knowledge_io·planning 반환의 소유 계약에 대응한다. caller 입력을 빌리는 transformer나 read-only borrowed row를 임의 copy 의무로 바꾸지 않는다.
- r18: `tests/structure/test_boundary_invariants.py`의 `PROCESS_STARTS`, `INJECTED_STARTS`, `JOB_RUN_STARTS`, `INTERPRETER_USES`, `EXECUTABLE_IDENTITY` 및 발견 함수와 `file_io.py`의 소유 규칙을 실제 windows_job/git_process/cli_worker/formal/scheduler 및 최상위 도구 호출에 연결한다. 현재 누락과 장래 가상 우회 가능성을 구별한다.
- 세 task의 제품 경로는 자기 workspace 상대 경로다. `C:/math/docs/...`와 `C:/math/.async/dm/...` 입력은 읽기 전용 원자료다. 과거 문서 안 `run:`은 legacy 실행 루트, 과거 `repo:docs/...`는 공용소스의 원자료를 뜻한다. workspace에 없는 대형 기록을 제품 누락으로 판정하지 않는다.
- source 판본 비교는 task의 `baseline.json`과 자기 workspace를 기준으로 하고, 이관 기준은 `managers/0001/source-inspected.json`의 스킬2675파일과 교집합에서 대조한다. 실제 차이가 있으면 명시한다. 이후 manager가 공용소스에 다른 결과를 반영해도 이미 실행 중인 task는 자기 고정판으로 완료한다.
- 보고는 async protocol의 `status`, `summary`, 문자열 목록 `changes`/`findings`, `verification`을 사용한다. 제품 무변경 조사는 changes=[]이다. 각 finding 문자열에는 해당 요구·증거 파일/심볼·영향과 다음 행동을 함께 적고 자세한 표는 자기 evidence를 참조한다.

## r02-fix 수용 후 요청 시험의 실제 계약

새 제품 API는 없다. `ModelRunner.run` (`do_math/model_runner.py`)은 `model_call.runner_assignment`가 검사한 배정으로 `worker_request_fields`의 결과를 evidence/request.json에 쓴다. `codex_adapter.LocalCLIAdapter.start`는 공급자별 `load_request`로 이를 검사하고 prompt/schema를 사유 snapshot 경로로 옮긴다. `codex_worker.run` 또는 `claude_worker.run`은 snapshot 요청을 다시 읽어 CLI argv를 만든다. 수용된 r02-fix의 worker_request_run은 이 경로의 실제 저장값을 시험 표본으로 사용한다.

- pinned 입력은 execution_id와 AI profile, 해당 profile SHA의 dispatched ticket, 정확 prompt_seal을 함께 준다. model/effort가 profile.ai와 다르거나 seal이 입력과 다르면 runner가 거부한다. host limits가 있는 profile은 일치하는 host와 resume 전 `on_started` publication도 필요하다.
- pinned scholarly/model-lock 설정은 profile.ai에서만 온다. 같은 설정을 별도 caller override로 주면 거부된다. unpinned 호출은 identity/ref/limits/control 없이 caller 설정을 사용한다. control binding은 해당 execution과 workspace를 가리키며 control이 있으면 CLI output schema를 전달하지 않는다. unbound일 때 Codex는 전송 schema, Claude는 의미 schema를 받는다.
- 수신 필드 정본은 `worker_request.py`의 COMMON/CODEX/CLAUDE REQUIRED·OPTIONAL과 `check_codex_request`/`check_claude_request`다. `validate_execution_binding`은 profile_ref의 형식과 identity·limits·control 관계를 검사한다. 프로필 registry의 AI 의미까지 재검사하는 경계가 아니다.
- `tests/support/provider_runs.py:ProviderJobs`는 실제 worker를 실행하고 `ScriptedCLI`는 worker.spawn만 대체한다. `dispatched`와 `model_runner`도 기존 fixture다. 새 fake runner/adapter/collector를 만들거나 저장 요청을 다시 조립해 관찰값으로 대체하지 않는다.
- `tests/contracts/pairs.py:Pair.samples`는 `(branch, value)` 목록을, `receive`는 수신 검사/ValueError 반려를 제공한다. `fields`의 필수+선택 역방향과 현재 lock 두 값의 성질을 유지한다. 실제 profile의 lock/tool 설정 변경은 profile_ref를 바꿀 수 있으므로 각 요청 참조를 자기 profile에 대조한다. 서로 다른 실행의 경로·참조 차이와 CLI lock 효과를 구별하고 정규화로 binding 검사를 지우지 않는다.

공급자별 기존 유효20조합과 필드35행의 정의·한계는 tasks/r02/evidence/branch-field-map.json이다. scholarly args의 0/1/여럿은 목록 축이며 identity/control 객체를 여러 개 만드는 요구가 아니다. r02-fix는 이 조합과 정확 값 전달을 관련6개 공식 시험에서 확인했다. worker_request_runs가 실제20입력을 공급자별로 실행하며 request/staged와 fixture 기대 입력을 함께 돌려준다. 파일이 살아 있는 동안 assert_worker_run이 정확 profile_ref·limits·control·prompt/schema·CLI·collector를 확인한다. 최종 G4~G8의 전체 판본 실행은 별도 배정까지 남긴다.

## 수용된 반환 소유권 계약

do_math/provider_final.py:output_contract(provider, schema)는 JSON schema dict를 받아 공급자 전송 schema dict를 반환한다. Codex는 필수 문자열 output_json만 갖는 닫힌 객체를 만들고 원 schema를 description에 JSON으로 보존한다. Claude는 values.json_copy로 같은 값의 사본을 만들며 입력·다른 반환·반환 내부 가변 노드를 분리한다. 미지원 provider는 ValueError다. r07-fix가 정본 설명5절과 이 구현을 함께 통합했다.

ModelRunner.run은 unbound Codex에서만 output_contract로 transport.schema.json을 만든다. Claude는 원 schema를 output.schema.json에 바로 직렬화한다. provider_final.semantic_output도 Codex 봉투 검증에 이 함수를 쓴다. Claude 반환 내부 공유 수리를 실제 전송 실패와 혼동하지 않는다.

tests/structure/test_schema_builders.py:_composition_calls는 이름에 schema가 없는 생성자의 실제 호출 변형을 제공한다. output_contract 두 공급자에는 두 속성이 같은 leaf를 가리키는 입력을 준다. _isolation_problems는 반복 호출 후 결과를 보관하여 dict/list의 전역·다른 반환·결과 내부 ID 공유를 찾는다. test_output_contract_preserves_values_and_detaches_the_caller_input은 원 값/봉투 보존과 한 필드 변경 뒤 형제·입력·다른 반환 불변을 확인한다. 기존 transformer와 borrowed lookup에는 새 복사 의무가 없다. 전체 모집단 자동 발견을 주장하는 인터페이스도 아니다.

## 수용된 파일 교체 소유권 검사

do_math/file_io.py:_windows_files는 create·close·invalid handle·rename을 반환하며 rename은 kernel.SetFileInformationByHandle binding이다. _replace_once(source, destination)는 네 번째 값을 받아 rename(handle,22,buffer,size)으로 Windows 교체를 수행하고 finally에서 handle을 닫는다. 비Windows는 os.replace다. atomic_replace는 공유 위반5/32/33만 재시도하며 다른 오류는 전달한다. r18-fix에서 이 runtime은 바뀌지 않았다.

tests/structure/test_boundary_invariants.py:_sites(trees=None)는 실제 제품 또는 메모리 AST 입력에서 (relative, function, node)를 낸다. _replacement_sites(trees=None)는 (relative, function, kind, node)를 제공한다. kind는 python-call/native-binding/native-call이다. 기존 os.replace/shutil.move와 직접 SetFileInformationByHandle binding, tuple return/unpack으로 연결된 호출 및 absolute from-import 소비를 추적한다. 함수명 rename/_windows_files만으로 교체 호출을 판정하지 않으며 임의 동적 별칭 분석은 지원하지 않는다.

test_only_file_io_replaces_files는 _assert_file_io_replacements로 소유자가 file_io인지 검사하고 실제 native 두 위치를 정확히 대조한다. test_native_file_replacement_remains_visible_when_relocated는 실제 함수 AST에서 비Windows 분기만 빼고 전체 이동/소비만 이동을 같은 탐색·소유 판정에 보낸다. 정상 source는 수용하고 두 이동은 반려하며 일반 reader와 무관한 rename은 발견되지 않는다. 순수 AST 결과이므로 Windows 실교체 증거로 확대하지 않는다. 기존 MetadataPublicationTests의 실제 파일4ID/018 원보고는 그 판본·성질 범위에서 유지한다.

## 수용된 r04 조건·한도·결과 계약

새 API는 없다. contracts/pairs.py의 enumerated_pointers는 planning.EXPOSED_FIELDS·RECORD_FAMILIES와 StateContract의 노출 필드 enum을 연결한다. _condition_pairs는 저장 enum과 lifecycle 후보를 validate_condition에 보내 실제 수용값이 저장 enum 안인지, 역방향으로 필요한 값이 생산되는지 검사한다. enum 값과 객체 필드의 모집단은 구분한다.

task_contracts.REPEAT_LINEAGES는 현재 import_rework·selection_failure·exhaustion_empty·proposal_version·contract_revision이다. revisions.record_repetition은 instance.config의 lineage + '_limit'를 읽는다. test_storage_fields의 이름 사용/읽기 연결은 구조 성질이며 test_repetition_hold_contract의 실제 count·임계 hold·정확 사용자 계속·중복 불변이 행동 성질을 맡는다. r04는 이 좁은 연결의 충분성만 판단하고 반복/대기 전체 요구로 확대하지 않는다.

_runner_result_samples는 실제 runner/worker/collector의 두 공급자 × collected/bound/incomplete/stopped 여덟 결과다. _receive_stored_result는 call_engine·scheduler가 쓰는 canonical_json(payloads.json_safe(result))를, _receive_operator_record는 scheduled_operator._json의 실제 파일 출력을 사용한다. json_safe는 bytes를 증거 객체로, Path와 안전 정수 범위 밖 값을 문자열로, float를 reported_decimal 객체로 투영한다. _json은 bytes/Path를 변환하고 allow_nan=False의 JSON 파일을 원자 게시한다. 두 표현의 차이를 무조건 같은 값으로 정규화하지 않는다. r04는 계약에 따른 실제 내용 보존과 단순 무예외 직렬화를 구별한다.

r04 수용판의 두 receive helper는 실제 수신 JSON 값을 반환한다. stored_result는 canonical_json(json_safe(value))의 바이트를 json.loads로 읽고, operator_record는 _json으로 게시한 파일을 read_bytes_shared/json.loads로 읽는다. test_runner_samples_cover_success_bound_incomplete_and_stopped가 기존8결과에 두 수신을 적용하며 assert_received_runner_result가 key 집합·분기별 null/부재·중첩 영수증·원 bytes의 길이/SHA/text/base64·Claude 비용 표현을 단언한다. 원 요청40조합·args·lock과 결과 생산자는 보존됐다. 전체 엔진 운전·모든 외부 값 영역 검사가 아니며 다른 시험/runtime/비용 캐시는 바뀌지 않았다.

## 수용된 r03의 신뢰 등록·관찰 기록 연결

새 제품 API는 없다. setup_lean.record_installation은 설치 identity를 관측/검사한 뒤 기존 fingerprint와 같은 기록을 재사용하거나 새 baseline/record를 만든다. 이미 같은 내용 ID 경로가 있으면 재기록 필요를 Refused로 반환한다. rerecord는 같은 identity·내용을 확인한 뒤 검증한 baseline을 추가한다. _baseline은 대표 컴파일의 실패/정지와 관측 중 fingerprint 변경을 반려한다. write_trust_request는 저장 record를 다시 읽어 trust_inventory.registration_request와 정확 binding으로 요청 JSON 파일을 배타 생성한다.

trust_validation.REGISTER_FIELDS/register_request_errors는 등록 요청의 닫힌 필드와 identity·record 참조·binding의 어휘 계약이다. environment_errors는 채택된 환경의 source_ref·axioms·toolchain_record와 별도 runtime binding을 확인하는 저장 환경 계약이며 host IO를 하지 않는다. 등록 요청·toolchain record·저장 환경 세 객체를 같은 필드 집합으로 취급하지 않는다. 과거 trust_environment_errors/manifest 표기는 현행 함수/객체에 대응하고 옛 API를 복원하지 않는다.

observations.ObservationTracker의 stored_obligations 및 실제 self-check/관찰 record 생산은 default_state_contract().family('runtime', family).checker와 validate_record를 소비한다. contracts/pairs.py의 accepted_rule_ids/receive_stored_rule_ids는 rule ID 입력과 저장 필드만 검사하는 한정 pair다. 수용된 tracker_record_samples와 TrackerRecordContractTests는 실제 tracker 출구를 세 개별 record checker 및 observations metadata map checker에 보낸다. r03-fix에서 observation_pairs가 네 가족의 전체 record와 owner metadata를 일반 PAIRS의 전체 필드 역방향에 등록했다. rule ID 조각 pair는 텍스트 보존을 별도로 맡는다.

tests/support/trust_inputs.py:setup_recording은 작은 실제 toolchain 파일과 기존 LeanDouble/worker_jobs/OutputCompiler 외부 대역을 만들며 identity/record를 사후 보충하지 않는다. setup_request_runs(root)는 core와 project paths0/1/2 × new/reused/rerecorded의 (branch, run)12표본을 yield한다. run에는 fixture·result·실제 게시 request/path·record·compile_count가 있다. _trust_request_samples는 그 request를 일반 pair에 제공한다. 파일이 남아 있을 때 source와 validation.json, record/binding을 확인한다. 공개 owner 등록/store/restart는 두 대표의 별도 단언이다.

sim.test_public_record_storage의 test_tracker_open_boundary_rule_response_and_execution_stop_survive_reload는 기존 running_work의 실제 bound control 경로를 사용한다. 안전 경계 영수증은 execution.safe_boundary_report.receipt_id가 가리키는 control_receipts이며 의무 필드에 옛 boundary_receipt_ref를 추가하지 않는다. 응답은 의무를 answered로 바꾸고 rule_update를 response record 내부에 둔다. 정상 제출 뒤 execution.status=stopping과 게시된 record의 restart 읽기를 단언한다. native 종료나 tracker 메모리 복원은 이 결과의 인터페이스 보장이 아니다.

## 수용된 r03-fix의 관찰 저장 계약

record_schemas/schemas.py:RECORDS의 observation_facts/self_check_obligations/self_check_responses와 _OBSERVATION은 미생산16선택 필드 및 의무closed를 더 이상 허용하지 않는다. fact는 event_json/event_sha256/monotonic_offset_ms가 모두 필수인 단일형이며 record_schemas/__init__.py:_observation_fact_rules가 엄격 JSON과 원문SHA를 검사한다. 선택source의 스트림 좌표/수신 시각 정의는 같다. 의무open/answered·offset/delivery/ack/hold/response_ref와 응답response_json/errors 및 중첩_RULE_UPDATE는 유지한다.

runtime.observations는 execution_id별metadata map이다. CoreEngineMixin._observe_running은 실제 review/followup notice에 observation_refs를 붙여 저장한다. checkpoint_reminder_due는 저장하지 않고 capability notice는 fact봉투로 저장한다. 다른 가족/응답 내부의 동명 필드를 top-level 미생산 필드와 혼동하지 않는다.

tests/contracts/pairs.py:observation_pairs(contract=None)는 현재 StateContract의 네 가족을 받는다. 세 가족의 receive는 개별record를, observations는 metadata map을 validate_record와 family.validator에 보낸다. fields는 정본의 전체properties이며 metadata의 written은 map의 모든 row키 합집합이다. support.observation_inputs.tracker_record_samples와 owner_observation_samples의 실제 tracker/owner/store 생산값을 사용한다. owner 표본은 기존 running_work에서 execution 불일치 입력으로 next_owner/followup과 observation_refs를 생산하고 참조fact의JSON에 대조한다. 사후필드 보충·부분집합 면제는 없다.

ContractPairTests.assert_pair는 등록된 일반pair와 새미생산optional키 반례가 공유하는 순방향/역방향 검사다. TrackerRecordContractTests의 정상대조/삭제필드/closed/필수누락/JSON·SHA변조와 기존C-03 공개저장·재시작13ID를 제출판에서 확인했다. r10의 생산/수신runtime은 불변이며 r14의 queue/진행성 변경도 기록모양을 바꾸지 않았다. r14-fix의 수용된 관찰처리 변경도 이 현행 저장계약을 보존한다. 통합판 전체실행은 별도다.

## 수용된 r05의 값 경계와 r04와의 분담

canonical.py:validate_storage_value/canonical_json은 안전 정수·문자열·bool·null/list/dict의 저장 영역을 공유하며 float·안전 범위 밖 정수·bytes·surrogate 등은 반려한다. repository가 이 정본을 소비한다. values.compact_json_bytes/json_digest는 상태 트리 밖 JSON 값을 compact UTF-8로 직렬화/해시하며 유한 실수를 보존하고 NaN/무한대를 거부한다. 서로 다른 영역이므로 같은 값을 무조건 같은 표현으로 만들지 않는다.

payloads.json_safe는 bytes를 sha256/text/base64 증거로, Path·큰 정수를 문자열로, float를 reported_decimal 객체로 투영한다. 원 bytes 보존은 별도 artifact가 맡는다. r05는 실제 외부 수신·생산 경로와 이 소비 계약을 입력축별로 연결했다. 실제 null 생산과 키 부재를 구별한다. r04는 기존 runner 결과8표본·pairs 수신 단언을, r05는 네 외부 값 경계의 추가 입력축을 맡았다. provider_runs의 기존 외부 대역은 불변이다.

tests/support/provider_native_inputs.py:EXTERNAL_JSON_VALUES는 (label, value, wire_bytes)9행으로 유한 실수·안전 정수 경계·초과 정수2개·비ASCII/공백 문자열·null·빈 list/dict를 제공한다. bytes 자체는 JSON 값이 아니므로 별도 artifact/투영 단언을 사용한다. native_rejection_cases와 이 값 축은 서로 다른 모집단이다. test_provider_native_storage는 실제 두 worker/runner/collector·owner/store에서 public content와 usage.reported_values의 다른 저장 표현, raw row/offset/SHA와 null 필드·없는 error_kind를 검사한다.

academic._requirement/requirement_record는 ACADEMIC_REQUIREMENT와 validate_record로 ID 문자열을 확인하고 items를 정본 해시한다. Unicode와 주변 공백을 trim하지 않는다. external_effect.grant_id 생략은 null로 생산하며 effect_receipts는 null을 특정 grant 제약 없음으로 소비한다. test_external_value_boundaries의 두 학술 ID는 이 직접 생산·소비와 독립 직렬화 해시를 확인한다. 실제 charter 승인·scheduler 실행은 별도다.

submission.load_extensions/read_extensions는 load_json의 안전 저장 영역 검사 후 알려진 empty-list 가족만 제거한다. 부재 파일은 {}이고 root/family null은 그대로 check_submission에 전달돼 정확 형/integration 오류로 반려된다. 허용 객체 안 nested null 등은 보존된다. _check_hashes는 exact_content_hash를 사용하고 integration.member_values는 가족이 list가 아니면 ValueError를 낸다. test_external_value_boundaries의 실제 수신/check·원바이트·해시 단언은 이 계약을 확인하며 sealed replay·지식 적용의 실행 증거를 대신하지 않는다. runtime API는 변경되지 않았다.

## r11의 공개 run 반환 계약

engine.py:ResearchEngine.run은 _executor_running을 try/finally로 관리하고 _run_executor에 위임한다. _run_executor는 max_steps<1을 ValueError로 반려하고 writer lock·reload·검사·controls·복구 후 준비가 불가하면 status()를 반환한다. 정상 준비 후 scheduler.py:SchedulerMixin._run_parallel을 마치고 status()를 반환한다.

_run_parallel은 controls·stop 정산·collect·설치 검사를 거쳐 fence/_owner_stopping/until_active/draining 전제를 판단한다. 해당 종료 전제에 futures가 있으면 wait 후 반복하며 마지막 _calls.close와 _calls=None을 보장한다. dispatch_engine.py:DispatchEngineMixin의 _owner_stopping은 제한 복구 가능 pause와 일반 정지·종결·설치 수리·미종료 recovery를 구별한다. _idle_wait_status와 _settled_run_status가 반환 상태를 정한다. EXIT_CASES는 이 전제의 위치표이며 실행 증거를 대신하지 않는다. r11은 현재 정의와 실제 시험의 연결 및 until_active/live-future 도달 근거를 수용받았다. 시작 전 무착수와 이미 시작한 호출을 정산한 후 추가 착수 없음은 각각의 전제로 기술한다.

수용된 tests/support/scheduling_exit_contracts.py:assert_no_dispatch(test, sim, answer, executions, reservations, probe)는 정상 dict 봉투·execution/예약 전체 값·probe 실패 없음·owner 정리와 store.load(head)의 runtime을 대조한다. store.load는 (head, instance, runtime)을 반환한다. unknown recovery 재진입은 core_engine._recover_disappeared가 recovery_disposition=preserve_space_and_reservations를 추가하므로 호출 시험에서 정확 기대값을 구성한다. 무조건 이전 execution 바이트 불변을 요구하지 않는다.

lifecycle_engine._resume_lifecycle은 공개 user resume이 권한/시계/연결 조건을 충족하면 resume_lifecycle의 active/initializing을 복원한다. 미종결 execution 자체를 금지하지 않는다. limited_recovery_sim은 공개 활성화·pause·정확 승인으로 maintenance를 허용한 fixture다. test_until_active_waits_for_live_limited_recovery_after_public_resume은 이 호출 중 공개 resume을 보내 실제 scheduler wait의 active/미완료 future를 ObservedCalls로 관찰한다. OwnerProbe와 assert_settled는 실제 owner/collector·durable 기록·종료/예약을 검사하고 제품 메서드를 대체하지 않는다. 이 경로의 수용은 모든 적대 일정 진행성을 인증하지 않는다.

## 수용된 r14/r14-fix의 진행성 경계

parallel.ModelCalls의 _observed/_owner_call은 guard 아래 deque/events에 생산한다. scheduler._run_parallel은 같은 guard로 owner 바퀴 첫머리의 future별 callback 수를 _observation_limits에 고정한다. map은 바퀴 잔여량이며 standalone에서는 None이다. 반복 pump가 허용량을 재충전하지 않는다.

model_runner.OBSERVATION_BATCH_ROWS=4이며 ModelRunner.run.observe는1MiB read의 nonblank 완전 행을 최대4개씩 ObservationBatch로 보낸다. events/rows/offsets는 원 slice, first_row는 누적 행 번호, received_at/received_monotonic은 같은 read의 시각이다. 중간 end_offset은 마지막 완전 행, 끝 part는 원 read offset이다. 빈 idle/final과 unterminated 마지막 행은 기존 frame_rows 경로를 따른다.

observation_transport.ObservationBatch.ends_read는 기본 True인 local read 경계 metadata이며 runner 중간 part만 False다. provider JSON/저장 schema 필드가 아니다. caught_up은 ends_read와 end_offset>=stream_size()가 모두 참일 때다. receipt_key는 execution_id/event_index/offsets/raw SHA이므로 분할·재전달에도 동일하다.

ModelCalls._apply_observations는 호출 진입량/limit/owner 잔여량 이내만 적용하며 실제 소비 callback 수를 차감한다. pump는 진입 snapshot events를 처리한 뒤 owner allowance가 있으면 future마다 최대1관찰 callback을 적용하고 제어 수신으로 돌아간다. done future가 있으면 경쟁 관찰을 양보한다. collect는 진입 완료 tuple을 등록 순서로 고정하고 관찰 부채가 적은 결과부터 처리한다. callback 중 새 완료가 생기면 현재 게시 후 남은 관찰을 다음 owner 바퀴로 미룬다. 새 continuation은 다음 controls 뒤에 받고 자기 관찰이 남은 결과는 보유한다.

반환한 future 하나만 남으면 현재 허용량 안에서 같은 function·stream/probe identity·received 시각·연속 first_row의 part를 ends_read까지 합친다. 원 events/rows/offsets와 마지막 part의 end_offset/ends_read를 보존하고 read 경계를 넘지 않는다. 다른 future가 하나라도 있으면 합치지 않는다. 관찰 오류의 기존 stop/error와 후속 dependent 관찰 중단 책임은 유지한다.

core._observe_running의 candidate→게시→성공 뒤 tracker commit/실패 rollback은 불변이다. 미게시 상태에서 continuation을 재진입하지 않는다. scheduler의 controls→collect와 r08 제어/r03-fix 저장 계약도 유지된다. progress-final은5진행성+15Calls의20passed이고 뒤 read/entry 경계 회귀1개와 관련 관찰/저장은 related-final-2의16passed다. 별도 판본이며 마지막876 Python SHA가 제출판이다. 총입력1/64/1024·사건0.25초·고정1초/owner≤1 회귀이며 벽시계 SLA나 동기 HTTP 전건의 보장은 아니다.

## 수용된 r10의 관찰·공급자 입구 계약

observation_transport.decode_observation_row(raw)는 strict_json_loads로 dict를 읽고 Unicode/JSON/비객체 오류는 unparsed_observation 사건과 행 bytes 길이로 바꾼다. ObservationBatch는 event와 정확 raw row·offset·행 번호·수신 시각을 함께 보낸다. 공급자 입력의 JSON 필드가 이 출처를 임의로 대신하지 않는다. ModelRunner의 live 관찰 진행과 codex_stream/claude_stream의 최종 strict collector 판정은 다른 소비 책임이다.

ObservationTracker.observe는 실제 ingest의 ValueError를 observation_input_rejected·reason·next_owner=adapter로 표현한다. deadline_only는 followup을 생략하며 다른 mode는 operational_review_due를 만든다. CoreEngineMixin._observe_running은 publication_candidate와 실제 runtime/store로 기록을 게시하고 execution_id·event_index·offsets·raw SHA의 receipt_key로 재전달을 판정한다. 공개 내용은 ReviewEngineMixin._record_review_observation의 현재 실행/review 전제와 공급자 외곽 검사를 거친다. 형식 오류와 적용 시점 전제 소실은 각 실제 수신 위치에서 판단한다.

flows/test_provider_raw_ingress.py는 RAW_CASES와 정상 대조군으로 두 공급자/세 mode에서 live의 뒤 정상 행 저장 및 strict collector의 정확 incomplete 사유를 비교한다. 수용된 r10은 실제 runner batch 원 bytes·offset/receipt와 fresh tracker 재전달의 runtime/head 불변도 단언한다. test_provider_observation_ingress.py는 결속 receipt/event 양순서·충돌·mode별 review와 종결 뒤 사실 보존을 검사하며 send가 append할 때 이전 nonblank 행 수를 first_row로 전달한다. 실제 batch helper는 support/provider_live.py:batch다.

test_provider_native_inputs.py는 공개 native 외곽/하위 좌표·동일 batch/순서 역전의 owner 소비를 검사한다. support/provider_native_inputs.py:native_rejection_cases는 support.ingress.NOT_TEXTS를 소비하여 public role 비문자열5개를 포함한34입력을 낸다. malformed는 root object/properties를 펼치는 helper여서 root string에 호출하면 표본이 없다. 기존 EXTERNAL_JSON_VALUES/NATIVE_ROWS/nested_native_rows와 r05 값 영역은 보존됐다. native 반려의 정확 객체·원 artifact·뒤 정상 내용·durable reload·fresh tracker 재전달 불변을 단언한다.

r10은 runtime API를 바꾸지 않았다. r10의 생산/소비 runtime은 r03-fix 통합판과 같고, 좁아진 schema는 현재 생산 형태를 보존한다. native_targets의 revise/review 종료 반려는 정적으로 대조했으며 pending slot 소실·공개 record 삭제·전체 R06/2-A/진행성의 전건 실행 증거로 확대하지 않는다. 비용 캐시는 base로 복원돼 통합에 들어오지 않았다.

## 수용된 r08의 공개 제어·수송 경계

control_contracts.py:validate_control_payload는 PAYLOADS와 configure의 정본 validator를 사용하며 action/text/config의 오류를 ValueError로 반려한다. engine.control→core_engine.submit_control은 형식/권한·현재 전제를 검사해 inbox를 게시한다. 같은 request_id의 payload가 다르면 ValueError이고 같으면 pending/processed의 기존 결과를 돌려준다. CoreEngineMixin._inbox는 파일명/instance/order/action envelope를 확인하며 손상 입력은 untrusted_file·원 bytes 증거와 함께 반려하고 파일명을 소비 좌표로 사용한다. _apply_inbox는 현재 payload와 적용 전제를 다시 검사하고 _record_control_result/_reject_control을 통해 저장한다.

control_transport.py:ControlTransport.receive는 기존 request hash와 receipt를 먼저 비교한다. 내용 충돌은 ValueError, 같은 최종 receipt는 그대로 반환한다. 검증 실패는 rejected, 닫힌 수송은 closed, publisher가 없으면 received다. preview는 비게시 previewed/rejected이며 accepted는 실제 publisher의 published=True·비어 있지 않은 authoritative snapshot이 있어야 한다. _pump_paths는 파일 decode/receive의 ValueError를 delivery 반려 영수증으로 바꾸고 다음 파일로 진행한다. 최종 receipt의 fingerprint가 같으면 cached receipt를 반환하는 것이 정상 계약이다. 재작성·receiver 재시작·다른 transport의 같은 ID 점유는 실제 경로별로 판단한다.

r08 수용판의 submit_control은 validate_control_payload 뒤 source config에 path/body_base64가 모두 없으면 ValueError('source requires a file path or normalized bytes')를 낸다. host path의 resolve/read OSError·ValueError는 ValueError('source path must identify a readable file')로 연결한다. 정상 경로/정규형 bytes는 기존 normalized_source/normalized_source_bytes로 내용과 identity를 보존한다. 공개 config=None의 기본값 처리와 손상 inbox config=None은 다른 입구다.

ControlTransport.worker_submit은 REQUEST_KINDS membership 전에 문자열임을 검사해 list/dict도 ValueError('unsupported control kind')로 반려한다. _reject_delivery_file은 이미 inbox에서 발견한 path.stem을 반려 좌표로 사용한다. outbox의 같은 파일명에 stage=delivery_validation·reason·source·source_sha256·source_bytes를 배타 게시하고 다음 파일을 처리한다. worker_receipt/submit의 안전한 ID 검사는 그대로라 손상 파일 좌표는 pump 결과/원 outbox 증거로 읽는다. 이미 게시한 반려·재전달 충돌의 원 receipt 보존 정책은 바뀌지 않았다.

tests/sim/test_engine_control_receipts.py의 두 transport 회귀는 실제 receive로 A-first/B-first를 각각 강제하고 fresh receiver pump·각 sender receipt·실제 owner/CAS/store의 뒤 정상 draft를 확인한다. tests/sim/test_engine_controls.py의 stale 회귀는 내부 status 주입 대신 공개 task_scope revise로 ready 전제를 없앤다. 특정 역사 review-cycle 종료/공개 record 삭제 생산자 의미까지 확인한 것은 아니다. r14-fix는 수용된 세 제어 함수의 의미를 보존하며 관찰 부분만 수정한다. r09·r12-r13·r06은 해당 runtime과 제어 시험을 읽기 전용으로 사용한다.

## 수용된 r09의 제출 확장·참조 경계

submission.py:extension_schema는 EXTENSION_ROLES와 action의 role/phase/대상 조건으로 허용 확장을 정한다. validate_reference/_validate_reference는 고정 context가 공급한 ID/정확 artifact locator·proposal/issue 참조 또는 safe_path를 통과하는 보존 workspace 파일을 확인한다. supplied snapshot의 역사 참조와 최신 상태의 현재성 판단은 별개 책임이다. private helper의 string 전제를 owner의 임의 JSON 입력 계약으로 확대하지 않는다.

payload_issues는 비객체에 schema 진단을 반환하고, integration 봉투가 있으면 derived_bundles/inspect_bundles로 구조를 먼저 확인한다. 전역 구조 오류는 원 schema 오류와 함께 반환하며, split 연구는 각 bundle의 _payload_issues 진단을 원좌표로 복원한다. schema 실패가 있으면 repair coverage로 진행하지 않는다. check_submission은 rule_id/path/message 등을 담은 issues, passed, not_checked와 정확 input_hashes를 반환한다. not_checked에 적힌 의미/구조 생략을 모든 정상 sibling까지 검사하지 않았다는 뜻으로 확대하지 않는다. producer_check는 생산자 측 진단이며 중앙 권한을 부여하지 않는다. seal_submission과 core의 실제 중앙 수신·integration 적용/게시가 권한과 현재성을 판단한다. integration.failure_kind는 prose가 아닌 rule_id를 소비하며 currentness만 있는 실패와 다른 반려/게시 실패를 구별한다.

tests/support/submission_owner_obligations.py:OwnerIngressAssertions.reject_and_replay는 실제 worker_submit/receipt를 통해 rejected·candidate validation failed와 정확 check issue를 읽고 원 output/extensions artifact·도메인 불변·submission_checked 사건1개를 확인한다. 동일 request_id/동일 payload는 locator 파일 bytes가 바뀌어도 기존 영수증을 재사용하며 payload 충돌은 ValueError다. 뒤 정상 제출의 수락과 실제 적용은 각 owner 시험의 역할별 단언이 맡는다. r09 수용판의 expected는 모든(rule_id,path,message)의 순서 있는 목록이고 전체 issues와 비교한다. mode=receiver/passed=False·schema 실패의 not_checked, output/extensions input hash와 원artifact SHA를 함께 검사한다. 알려진 empty-list extension만 제거하는 정규화 계약을 독립 stdlib JSON/SHA 기대값에 반영한다. 재전달을 위해 변이한 sidecar는 원바이트로 복원한다.

integration.py:inspect_bundles는 mutation_members가 반환한 target이 문자열일 때만 mutation dictionary에 색인한다. 비문자 target의 형 반려는 기존 schema가 담당한다. 기존 manifest/member/reference·권한·현재성 검사는 유지한다. tests/support/submission_obligations.py:mutation_target_inputs는 knowledge_changes.id/task_dispositions.task_id/revision_resolutions.record_id에 NOT_TEXTS와 비빈list/dict를 공급하며 unit과 실제 role owner가 같이 소비한다. runtime API와 정본schema는 바뀌지 않았다.

r09는 정본7·미러7을 통합했다. owner helper의 직접 소비모듈4개를 함께 조정하고 계획/평가 및 완료증거의 실제 추가 진단을 명시했다. r05 null/hash·r08 수송 양순서 성질은 해당 범위만 재사용한다. 마지막5ID·Python876 SHA는 제출판과 같지만 앞 판본18passed와 현재 전체 통합판 실행으로 합산하지 않는다. 공개삭제 도달은 생산자가 확인된 경우만 세며 지정 경로의 미확인은 남긴다.

## 수용된 r12-r13과 r12-r13-fix의 위임 경계

tests/support/cross_machine.py의 ControlMachine.control은 실제 Sim.control→engine.process_controls→control_result를 소비한다. 새 사건은 새 idempotency_key를, 명시 재전달은 같은 키를 사용한다. contracts_after_every_event와 assert_machine은 실제 Hypothesis invariant/run_state_machine_as_test를 연결한다. SHORT2×4, LONG6×20과 별도live4×8은 각각의 설정이며 등록과 발생을 구별한다.

cross_contracts.py:ContractOracle.check는 실제 store.load와 현재 runtime/instance의 이력·결정·종결·요청 이유·용량·현재 모델·정지 권한·자리 소유권·봉인artifact·예약을 검사한다. cross_obligations의 RequestReasonLoss는 부가 진단 뒤 동일 실패를 다시 raise한다. 역사 classifier는 생성 실행의 예외 허용 목록이 아니다.

수용된 cross_research_machine.RoleInputSelection.ready는 복사 action으로 실제 _action_lifecycle_gate를 호출한다. 다섯 명시 권한 반려 문구와 traceback 최종 함수가 LifecycleEngineMixin._action_lifecycle_gate.__code__일 때만 False다. 그 밖의 ValueError는 그대로 전파한다. 실제 만료는 비선택이고 stale profile SHA는 정확 오류가 된다. gate 반환은 입력 선택에만 쓰며 용량/현재 모델 기대값을 재계산하는 oracle로 쓰지 않는다.

수용된 cross_states.assert_event는 arm→drive→선택 action ID→실제 ended/output_accepted→event/value→ContractOracle 순서다. drive 실패는 원 예외 그대로 전파한다. 수신 반려는 ('event not accepted', event, value, 실제 ended rows)의 AssertionError다. 없어진 cross_diagnostics를 다시 만들지 않는다. 최종19에는 직접 unit13·sim5·Planning LONG1이 포함되며 다른 machine 실행까지 인증하지 않는다.

delegations._basis는 같은 decision_kind의 실제 user 원결정, 정확 승인 change/source, 포함/제외/효과/자원/만료와 현재 target/basis refs를 검사한다. prepare_application은 basis의 정확 hash로 application을 만들며 judgment_input은 두 판단에 같은 basis/hash만 준다. core._review_recovery_control은 review_replacement 사례에서 interpret/check를 배정하고 _apply_delegation_judgment는 두 within_scope가 갖춰져야 현재 자리 교체 권한을 재검사한다. 다른 판정은 사용자 질문을 남긴다.

r12-r13-fix 수용판의 core._review_recovery_control은 request(review_replacement)와 decision(change.kind=review_replacement, allowed_action)을 연결한다. governance.apply_decision은 현재 사용자 원문/source SHA·cycle/stage/round/slot·실패 인덱스/원인과 실제 grant/effect를 decisions에 생산한다. 실제 교체 승인 실패 시 candidate를 되돌린다. 위임 승인 결정의 original_decision_sha256은 원결정 전체의 정확 hash이며 delegations._basis가 승인 범위·두 원문 SHA와 함께 검증한다. decisions.effect는 EVIDENCE, original_decision_sha256은 HASH다. 자동 위임 적용은 사용자 원결정을 만들지 않는다.

prepare_application은 같은 delegation/case ID를 찾으면 case 내용과 현재 basis 또는 적용 후 post_basis_sha256을 확인해 기존 사본을 돌려준다. 내용 충돌은 'delegation case ID reused with different content', 기초 변경은 'delegation application stale'이다. core는 queued/held/기존 실행과 판단/적용 receipt를 재사용한다. case.effect는 실제 실패 자리의 cycle/stage/round/slot/replacement_for/continuity_break_cause와 정확히 같아야 한다. 두 판단값 중 outside_scope/unresolved가 있으면 교체하지 않고 delegation_judgment 출처의 user 질문을 남긴다.

core._context는 review_engine._prepare_review_context(action, workspace, sources=..., execution_id=...)에 실제 입장 실행 ID를 전달한다. _review_replacement_authority→review_cycle.replacement_authority는 기존 input_bindings 또는 execution_accounting.admissions의 delegation_authority를 소비한다. 입장 자체의 cycle 변경은 허용하면서 적용 application SHA·승인/원문·두 판단 execution·grant를 검사한다. 외부 변경을 허용하는 새 예외가 아니다. 실제 공개 owner 경로와 domain fixture를 구별하며 최종107passed는 맡은 위임/교차 소비 범위의 증거다. r06-finish/r22-snapshots는 이 현재 계약을 선행으로 소비한다.

## r06/domain/edges 수용과 null 마무리의 생산·소비 경계

새 제품 API나 null registry는 없다. 실제 mapping/record/receipt/JSON에 None을 쓰는 코드와 그 전달값의 직접·최종 사용을 연결한다. nullable schema·동명 key·지역 None·키 부재는 실제 생산 필드와 구별한다. r04의 runner 8결과/두 JSON, r05의 grant_id·extension/native/runner null, r03-fix의 현재 저장 schema를 해당 판본·성질에 한정해 재사용한다. deadline_only는 followup을 생략한다.

r06 수용판 tests/unit/test_producer_record_storage.py는 실제 open_activity/create_execution/transition_execution/execution_window.publish→Repository.initialize/load와 activities.assign_execution·successor_state·recovery_attempt_counts·reporting.timeline/timeline_csv를 연결한다. stage/execution_limit, continuation_of/result_disposition/transition.reason, window 세 필드의 present null을 유지한다. limit=None은 두 번째 실행을 허용하고 deadline=None은 finish 요청을 만들지 않는다. 후속 계보가 없으면 successor_state는 None이며 CSV는 null을 빈 셀로 렌더링한다.

같은 파일의 외부 시험은 실제 prepare/503 execute→store·validate_operation의 정확 'operation is not startable'→effect_absent reconciliation→retry를 연결한다. credential_env/succeeded는 present null이고 503의 effect_absent는 absent다. reconciliation의 succeeded=False/effect_absent=True와 external_id/idempotency_evidence의 null을 구별한다. 질문 시험은 link의 resolution_ref/checked_by null→저장→question_view의 실제 미해결 text=null/source_status=unavailable→user_questions=[]→resolve_user와 재저장을 연결한다. 이 3ID만 이번에 실행됐고 전체 null 모집단이나 owner 운전으로 확대하지 않는다.

tasks/r06-domain/evidence/relations.md와 r06-edges/evidence/relations.md는 실제 생산부터 직접·최종 소비까지 null과 부재의 의미를 연결한다. M1/M2의 명시 관계와 M3/M5·edge M4의 맡은 범위를 판정했다. domain의 117개 탐색 표현은 nullable 필드 수가 아니며, 실제 객체의 남은 소비는 r06-finish에서 22관계군으로 묶어 판정했다. read_source의 실제 caller는 context_store.prepare_role_input과 submission._payload_issues이고 status와 완전성을 검사한 뒤 소비한다.

governance.prepare_import는 status=checking이고 check 키가 없는 bundle을 생산할 수 있다. governance_engine._governance_control은 import_approval 반려 시 상태를 복원한 뒤 _reject_governance_import를 부른다. 수리 전에는 check 없는 bundle도 rework로 보내 비nullable intent_repair.check_execution_id에 null을 넣었고, 반려 뒤 저장이 실패했다. r06-finish 수용판의 _reject_governance_import는 실제 check가 있는 미적용·비대체 bundle만 rework로 보내므로 checking의 기존 check queue를 유지한다. _queue_intent_rework는 check가 있을 때만 intent_repair를 만들고 필수 check.execution_id를 직접 사용한다. 첫 검사 전 source 변경은 previous_import_id와 intent_repair 없이 새 해석을 요청하며 기존 author/권한/lineage를 보존한다. 정상 독립 검사 후 rework는 정확 검사 근거를 유지한다. QUEUE_FIELDS의 문자열 ID 계약은 그대로이며 아래0024절이 현재 제공·소비의 세부 사항이다.

reporting.snapshot_report의 OBSERVED_FIELDS null은 미관측이다. 현재 start_guard caller는 scheduled_operator의 live ResearchEngine.status→SessionSlots.provider_snapshot이며 providers dict를 제공한다. snapshot null을 운전 guard로 전달하는 API 의무는 없다. query는 ID 없는 descriptor를 필터하고 next_cursor=null은 마지막 페이지를 뜻한다. timeline은 미완결 시간을 null과 CSV 빈 셀로 보존한다. tracker의 standalone malformed null ID와 ControlTransport.worker_self_check(response=None)의 poll을 구별하며 owner는 실제 issued ID를 먼저 비교한다. deadline_only followup은 부재다.

ordinary external transport OSError는 succeeded/effect_absent를 생략하지만 unexpected sent exception은 owner에서 둘 다 null을 생산한다. external_engine은 unknown을 ended/execution_incomplete·no receipt·user reconciliation wait로 투영하고 재시작에 보존한다. confirmed와 succeeded is True만 완료로 삼고 이미 ended인 실행은 나중 reconcile로 덮어쓰지 않는다. native provider의 미지 reset은 유한 backoff로, available의 null retry는 no-wake로 소비한다. operator_schedule.ps1의 null task/next_run은 실제 PowerShell 생산이며 schedule/check/wake는 존재를 확인한 뒤에만 쓴다. 새 시험의 unit5와 sim2는 별도 판본이며 나머지 관계는 정적 근거다.

## 수용된 r23-r24의 비용 계측·내용 보존 경계

tests/support/storage_obligations.py:COST_CASES는 B-27/D-10/B-03/D-08/A-18의 규모·상한과 원문을 선언하며 실행 결과 등록부가 아니다. Repository.export/query→GitStateStore.blob_sizes/read_many/read_bytes의 실제 호출과 support.storage_git.ObservedGit의 InProcessGit 포트 연산을 계측한다. N/byte batch는 유지됐고 실제 Git 프로세스 성능과 구별한다. export의 전체 원bytes와 query의 전체 path/size/SHA·cursor/snapshot·실제 hash 인수를 비교한다. query 페이지 3파일/2+1분할의 전체 행 단언을 이번에 보완했다.

support.storage_probes.Returns(function, snapshot=deepcopy)는 실제 함수 반환값과 반환 시점 사본을 보관한다. ObservedCalls는 실제 code 호출·인수를 관찰한다. test_storage_owner_costs의 readiness N=2/100·이력10은 전체 instance/runtime 보존과 owner 반환 N개 복사를 검사한다. 관찰용 snapshot 복사는 owner 계수와 분리하며 전체 상태 복사0 검사는 caller로 축소하지 않는다. 반환의 basis[0].id/profile_ids를 바꿔도 저장된 _task_readiness와 원 입력이 불변임을 확인한다.

support.storage_cost_owner.observe_idle은 같은 저장 상태의 새 ResearchEngine과 외부 clock/Git 포트만 연결한다. 첫 sleep까지 정착 게시를 허용하고 뒤 k=1/10 안정 구간에서 head/queue/executions/Jobs 불변과 commit0을 확인한다. 공개 pause 뒤 실제 run 반환은 paused/최종 head이며 그 head는 idle head와 다르다. Sim.restart 뒤 같은 head·processed request·빈 queue/executions·Jobs0을 보완했다. 활성 호출 정산과 필요한 게시를 무변경으로 취급하지 않는다.

trust의 실제 shared_reader/sha256_file 입력 계수와 전체 SHA 지도·등록/활성화 증거는 기존 판본·정확 B129 row·불변 소스로 재사용했다. 56,230개 소형 파일은 8.55GB 내용 재생이 아니다. 이번 직접 실행은 query/readiness/idle 각 1ID의 3passed이며 수정 시험 정본2·미러2만 통합했다. runtime/helper/캐시는 불변이고 다른 큰 규모와 합쳐 최종 통합판 7전건 통과로 세지 않는다.

## 부분 수용된 r21-r22와 저장 가족 후속의 경계

새 API를 정의하지 않는다. context_store.py:input_scope/role_direct_keys/prepare_role_input는 실제 역할 입력과 instance/runtime/profile/snapshot/workspace를 받아 prompt/context/validation_context/manifest/artifacts 및 actual_bytes/overflow를 제공한다. 직접 지급 입력, 원문 source_ref와 필수 validation 입력의 책임을 구별한다. verify_manifest_artifacts는 봉인 artifact의 실제 내용을 확인하고 input_tool.read_main은 공개 읽기 결과 JSON과 요청한 output 파일을 제공한다. 원문 보존은 요약 길이나 무예외 호출로 대체하지 않는다.

tests/support/engine_size_cases.py:role_cases는 contracts.ROLES와 VARIANTS의 모집단 일치를 요구한다. scale_state/scale_context는37프로필·100과제×10이력의 포장 입력을, stored_scale_sim은 실제 도메인 생산자/저장/restart로 만든 상태를 제공한다. 합성 포장 행과 엔진의 실제 _context 입력은 서로 다른 증거다. tests/support/role_input_requirements.py:assert_judgment_inputs와 제품 role_input_requirements의 기존 필수 자료 계약은 읽기 전용으로 재사용한다.

tests/support/engine_lean_recording.py의 녹화 원bytes/SHA·5선언/603폐포는 읽기 전용이다. formal.verify_lean→실제worker→knowledge_records.record_formal_result와 formal_preview.main의 PREVIEW_FIELDS, input_tool.read_main의 원문 output 파일을 직접 소비한다. tests/support/engine_tool_output.py:invoke_tool은 같은 프로세스의 공개 함수/주입ports 호출에서(code, raw UTF-8 stdout bytes)를 돌려준다. 실제 외부 Lean 실행이나 모든 저장가족 크기의 전건 증거로 자동 확대하지 않는다.

수용된 tests/support/engine_size_cases.py:assert_input_budget(test, prepared, role, profile)는 실제 prompt UTF-8 길이·actual_bytes·manifest.prompt의 bytes/SHA, 프로필 한도와 필수 direct 부분의 문맥 예산을 단언한다. unit의25대표 상태와 실제 stored/manifest·검토 cycle 포장에서 공유한다. source_ref는 read_source로 정확한 JSON 원값을 회수하며 blocked는 context/validation/catalog에서 부재여야 한다. planning의 ready_task_ids는 candidate_order의 봉인 순서를 따르고 원 모집단과 별도로 대조한다.

stored100×10은 실제 core._context→prepare_role_input→assert_judgment_inputs를 거쳐100과제와37프로필을 공개 input_tool로 읽는다. 모든 저장 파일 바이트≤논리 instance/runtime의2배+파일당1024는 이 상태의 codec 비용 성질이다. 생산자가 이미 복제한 내용도 분모에 포함될 수 있으므로 원천 대비 중복 전건 성질로 확대하지 않는다. review_engine._start_identity_review가 policy_ref를 포함한 cycle을 생산하고 context_for/accept_result로 scope/initial/organize/answer/judge의 필수 입력과 private_scope를 검사한다.

녹화의 전체5선언 원문은 유지하고 같은 source/603본문의1선언 투영을 formal.verify_lean→실제 worker→record_formal_result→store/load로 보낸다. BoundRecordingCompiler는 선언별 check_file 원bytes를 검사한다. 공유 해시표/source를1회 공제한 가변 record에5배+4096 상한을 두며 투영은 별도 실Lean 측정이 아니다. preview는 extract_evidence=False 계약의 stdout/stderr 원값과1MB JSON 상한을, 공개 원문 파일 회수는 전체 원bytes/SHA와4096 stdout 상한을 유지한다.

r22-storage의 정본 모집단은 state_contract.default_state_contract().families()다. repository._encode_families는 map/list/singleton마다 record 봉투를 한 번 쓰고 metadata를 root별 한 봉투에 모으며 manifest에는 container/ID를 둔다. payloads.seal_large는 큰 문자열을 FrozenText로 봉인한다. encode는 원bytes를 hash 경로로 반환하고 _encode_families의 files.update가 같은 경로를 공유한다. 각 좌표에는 참조를 둔다. 이 공통 구조와 원문을 만드는 생산자의 책임을 구별해 가족별 정적 근거와 필요한 단언을 연결한다. 새 제품 registry/API나 모든 가족별 새 실행 의무는 없다.

r22-storage는 88가족의 공통 저장과 실제 생산 관계를 대응했다. unit.test_engine_storage_scale은 academic.record_resolution→save_with_state/load/read_record의 독립 원천, 1·10참조, UTF-8·escape, 원문 정확 1벌을 확인한다. 봉투·metadata·manifest 비용과 생산자 복제를 구별한다. 당시 큰 문자열 seal만으로 남았던 구조 snapshot 질문은 아래0025절의 수용된 구조codec으로 이어진다.

review_cycle.start_review(previous)의 논리 previous_reviews/turns/transcript_manifest와 이전 cycle은 계속 보존된다. delegations._basis의target/references·governance의owner_basis·review의pending 문맥도 같은 논리값을 제공한다. r22-snapshots가 저장경계의구조공유로이중복을줄였으며현재제공·소비는아래0025절을따른다. review_inputs의수신/defer 제거·권한·현재성·null 의미는유지한다. r29-r30은기존core/governance_engine의단위실패를, r31-r33은역할요구표/제출을자기시작사본에서수행하며서로의중간결과를쓰지않는다.

## 수용된 r15-r16의 공개 반환 정산 경계

새 제품 API나 runtime 변경은 없다. engine.ResearchEngine.run/_run_executor·scheduler._run_parallel의 실제 반환 guard와 call_engine/formal_engine의 수신을 연결한다. idle은 live future가 있으면 wait/continue하며 until_active도 active인 동안 future를 먼저 정산한다. r11의 공개 제한복구/resume이 실제 live 사례다. trust_check/trust_activate는 같은 future 경계에서 다른 검증 결과를 생산한다. external_engine의 동기 HTTP send marker/효과 재조정은 future 수신과 별도다.

tests/support/scheduling_return_observer.py:OwnerProbe는 owner pass의 실제 Calls 객체를 calls로 보관한다. assert_drained(test, sim, probe)는 공개 반환 뒤 futures={}·events.empty()·stopping·살아 있는 thread0·engine._live_execution_ids=set()·_calls=None·_executor_running=False를 검사한다. 중간 collections의 pending은 r14-fix의 관찰 유예 때문에 허용하며 최종 완료 회수와 구별한다. 새 close_settlement 회귀가 실제 중간 pending·최종 receive1·원stdout bytes/SHA·restart/재수신0을 함께 단언한다. 예외 종료의 durable evidence는 별도 exception 시험이 맡는다.

assert_owned(test, runtime, execution_id)는 실제 activity의 id, assigned_execution_ids의 정확1회 포함과 유일 owner 연결을 검사하고 미종료 실행의 owner working을 요구한다. 종료된 activity의 후속 대기/업무 상태를 일률 finished로 강제하지 않는다. assert_settled와 scheduling_return_matrix.assert_returned는 저장 execution/activity/reservations 전체를 메모리와 대조하고 정상 ended/confirmed·예약 반환·결과 참조를 검사한다.

close_matrix는 실제 _local_call_returned 결과와 Lean raw_result_ref 전체 또는 trust_activate의 저장 validation_receipt/판정 artifact를 대조한다. 중단 환경은 environment.json 전체를 확인한다. ended 전이1회와 restart 뒤 callback0·예약불변·원artifact byte보존을 단언한다. scheduling_return_settlement의 unknown은 json_safe 원결과·실제 owner·held/returned0을 보존한다. fresh owner가 종료를 모르면 수신0/예약유지이며 양성 named Job 종료 뒤 core._recover_disappeared가 checkpoint-recovery result_ref와 ended/confirmed/정산을 만들 수 있다. 이전 원artifact는 보존한다.

관련17passed 이후 matrix의 두 환경 메서드를 보완한2passed는 별도 판본이다. 마지막876 Python SHA는 제출판과 같고 runtime124는 시작/공용판 불변이다. 단일 최종판19passed나 모든 반환 좌표의 새 실행으로 합산하지 않는다. manager 근거는0021/source-review.json이다.

## 부분 수용된 r19-r20의 녹화 재생 경계

tests/corpus/manifest.json은 지원 stream 판본과 실제 entry의 raw 경로·명령·판본·출처·verdict를 제공한다. structure.test_corpus는 실제 파일 선언·SHA·지원 provider의 원자료 존재를 확인하고 unit.test_corpus_replay.READERS는 kind별 실제 parser를 호출해 recorded verdict와 대조한다. contracts.test_doubles_follow_corpus는 기존 대역의 원자료 대응을 검사한다. 등록만으로 외부 출력 해석 함수 전건이나 역할 schema 전건을 인증하지 않는다.

현재 직접 정의는 codex_stream.parse_jsonl·claude_stream.parse_stream/provider_limit·model_call.classify_run·provider_final, lean_evidence.check_file/parse_evidence, scholarly_config._from_config, PowerShellScheduler.run, cli_execution.surface_report다. 보존 원bytes와 독립 판정을 현재 추출·반려·실제 소비까지 연결한다. 합성 변형과 실제 녹화를 구별하고 기존 raw는 재작성하지 않는다. 새 외부 호출 없이 가능한 오프라인 수리를 마친 뒤 없는 자료는 정확한 parser·판본·사건으로 G7에 연결한다. 다른 task의 runtime·공유 문서 쓰기는 없고 현재 새 제품 API는 없다.

## 부분 수용된 r25-r26의 공개 CLI 운전 여정 경계

do_math/cli.py:main은 cli_contract.build_parser의 공개 인자를 받아 execute를 호출하고 응답 봉투/종료코드를 낸다. tests/support/engine_cli_journey.py:CliSim은 실제 cli.main(init)으로 인스턴스를 만들고 Journey.call은 같은 main에 외부 ports/environment를 주입해 응답 result를 다음 입력으로 사용한다. Journey.state는 실제 Repository.load를, files는 같은 snapshot의 cursor 조회를 소비한다. document/decision은 사용자 요청 문서를 만드는 보조이며 내부 저장 JSON·승인 hash를 수제로 우회할 권한을 주지 않는다.

JOURNEY_STEPS는 문서 단계의 설명표이며 implemented/conditional_implemented/partial 문자열 자체가 실행 근거가 아니다. 초기 출처·원문·권한/설정→probe/adopt→공개 setup/trust→until-active와 조건부 답변/승인·HOLD/생명주기·재시도·재수신·신뢰 재기록은 실제 CLI 호출/정지점/원자료와 연결한다. 정상 native final 재수신은 새 모델 호출이 없는지, 후속 수리는 원활동/실행·종료/예약·실패 이력을 보존하는지 구별한다. 예약 대역→실제 연구 CLI/worker 연결과 OS발화는 각각의 경계다.

r25-r26의 runtime은 불변이며 두 CLI journey/초기 retry·engine_cli_conditions와 재기록 문서만 통합했다. source bytes/SHA/승인 source_ref, 실제 public retry/replay/restart, bounded repair/maintenance wait와 권한 대기를 단언한다. terminal trust transition은 같은키 재생으로 재실행되지 않고 새키의 같은env transition/run을 사용한다. F1의 중앙수신 실패는 수용된 r29-r30이 해결했으며 아래0026절이 현재 계약이다. import 반려/구조 snapshot의 중간 사본은 소비하지 않는다.

## r29-r30의 소유 루프 실패 경계 (수용 전 연결; 현재 계약은0026절)

engine.run/_run_executor는 공개 실행 봉투와 writer/reload 책임을, scheduler._run_parallel은 controls→stop→collect→준비/dispatch→반환 정산을 소유한다. 현재 최상위 BaseException 경로는 Calls.close→_abort_parallel_calls 뒤 원 예외를 다시 던진다. _abort_parallel_calls는 returned-result.json의 로컬 원증거·reload·interrupted 기록과 저장을 시도하며 이 경로를 정상 봉투와 동일시하지 않는다.

dispatch._observation_failed(execution_id,error)는 해당 실행의 stop_requested와 저장을 만들고 _record_interrupted_calls는 반환 원결과/종료 확인·owner/대기를 연결한다. parallel의 observation error/continuation, core의 control/observation publication, call/formal 준비와 중앙 수신의 실패 단위는 실제 정의로 판정한다. 같은 입력 반복 억제와 독립 단위 진행은 별도 성질이다. 새 공통 API나 포괄 catch는 아직 정하지 않았다.

r29-r30은 r06-finish의 core/governance_engine과 r15-r16의 drain, r25-r26의 native 재수신 실패 회귀를 선행으로 소비한다. 저장/review/schema/context·corpus/parser·CLI/repair와 공통fixture는 읽기 전용이다. 원문2-B의 단위 예외와 실제 봉인파일 읽기/해시 실패를 가장 작은 현행 입력으로 확인하며 전역 게시 불능의 원결과 보존/복구 책임을 유지한다. 수리한 실제 인터페이스·반환/오류 의미는 task 보고와 다음 manager가 갱신한다.

## 0023 수용과 추가 제공·소비

corpus는 기존22entry/지원판본을 그대로 두고 역사Claude2.1.276 raw2개를 추가해24entry다. test_corpus_replay는 현재 parser→final_bytes/semantic_output/classify_run의 실제 소비를 연결한다. HTTP400 schema거부는failed/execution_failure/최종부재이며 quota로 바꾸지 않는다. scholarly 원request/prompt/schema/status는 collection_reasons의 hash 소비에 연결되고 원timeout 설정에서 resolver는command/args만worker argv로 보낸다. preinit allowed와후속cleanup raw의 원SHA/원보고를 대조했지만cleanup live_passed=false는유지한다. 현지원판quota/다중result/cleanup·역할동적schema 실수용은 별도G7입력이다.

core._collect_submitted_result는 verified_native_final 및 _capture_native_submission의 중앙게시 오류를 top-level failed/execution_failure로 반환하고 call._receive_call은 그 값을 result.json에 저장한다. _continue_initial_execution은 현재권한검사 뒤 _resume_initial_native_final을 시도하지만 이 함수가 result.status=completed를 요구해 F1 정상원문을 재사용하지 못한다. 0023 당시 이 인터페이스는 미수리였으며0026에서 r29-r30 수리를 수용했다. 실패이력과 공급자완료증거를 보존하고 native_final.verified_native_final의 원응답/요청/모델/종료·봉인/현재권한 검사를 유지해야 한다. 재수신자체의 원해석중복과 다음정상독립단계 호출은 구분한다. 현재 원 provider 상태와 재수신 검사는 아래0026절을 따른다.

r31-r33은 context_store.prepare_role_input의 context/validation_context/manifest 및 read_source 반환을 읽기전용으로 소비한다. role_input_requirements의 judgment_input_keys/paths/source_lists/source_refs가 역할/단계의 의미 입력을 지정한다. submission.reference_catalog/validate_reference/producer_check와 실제 중앙capture/application의 광고/정확반려 관계를 지정시험에서 확인한다. OwnerIngressAssertions.install_family_probe의 workspace정상출력과중앙제출은같은입력에대응해야하며명단/빈모집단이전건적용을대신하지않는다. role_input_requirements/submission/submission_tool와전용시험/helper만소유하고core/context/저장/review/공통fixture는읽기전용이다. 새API나별도registry를전제하지않으며현재runtime수리는이task결과후에판단한다.

## 0024 수용: 검사 전 import 반려와 null 소비

GovernanceEngineMixin._reject_governance_import(request, reason)는 import_approval 반려 시 실제 check가 있는 미적용·비대체 bundle만 _queue_intent_rework로 보낸다. check 없는 checking bundle은 기존 독립 검사 queue가 유지된다. _governance_control은 후보를 원상복원하고 기존 정확 ValueError를 재전파하며 owner가 한 번 반려 결과를 게시한다. 동일 request_id 재전달은 그 결과를 재사용한다. sim.test_null_domain_consumers.ImportNullTests.test_unchecked_import_rejection_does_not_enqueue_a_null_check_execution가 저장/restart·재전달·남은 check와 정확 승인 적용까지 연결한다.

_queue_intent_rework(bundle, reason)는 author의 initialization/grant_id/profile_ref/owner_activity_id와 lineage를 보존한다. current source가 같으면 previous_import_id를 포함하고, check가 있을 때만 intent_repair={import_id,previous_sha256,check_execution_id,findings}를 만든다. check.execution_id는 필수 문자열이다. 첫 검사 전 원문 변경이면 previous_import_id/intent_repair 없이 새 원문을 해석한다. 기존 _apply_governance_intent의 check_import 실패/미해결과 _resume_import_question_waits의 답변 후 재해석은 실제 검사 근거를 소비한다. 저장 QUEUE schema와 governance.check_import 계약은 바뀌지 않았다.

domain M4는 tasks/r06-finish/evidence/alias-dispositions.json·relations.md에52현행심볼을 연결한다. _enqueue(target=None)는키생략, restore_continuation의선택적checkpoint/outcome/error는guard후JSON/catalog전달, prepare_role_input의overflow/private_scope/ongoing_work·task catalog는해당부재/진단의미를유지한다. review tool message의call=null은본문이고message identity가아니다. required source ID/revision·read/len/hash/container는null생산필드가아니다.117탐색행/22관계군은정적판정근거이며새제품registry가아니다. r22-snapshots와 r31-r33은자기시작판의기존배정으로작업하고표현을바꾸면가까운소비도확인한다. 이번수용을통합판전체시험이나외부모델성공으로확대하지않는다.

## 0025 수용: 불변 구조 저장과 후속 검사 경계

state_contract.STATE_CONTRACT_ID는 do-math-state/10이다. payloads._snapshot_selected(family,tokens,value)는 review_cycles/delegation_applications/intent_imports의 최상위 dict/list 및 singleton review_inputs 각자리문맥을 선택한다. scalar ID/revision/status는 inline이고 논리 record_schemas/producer 인자는같다. encode(envelope)는기존payloads행{tokens,path,sha256,bytes}와blob지도에구조root를추가한다. _encode_snapshot은정확UTF-8키의압축이진trie와list prefix노드를 runtime/artifacts/snapshot-<digest>/value.json에보존한다. 큰FrozenText는기존payload-blob을공유하며논리proposal/basis hash는바꾸지않는다.

decode(envelope,read_payload,git_dir)는 _read_json_blob의존재·bytes/SHA·정규JSON확인, _decode_snapshot의node/cell/참조검사와canonical재인코딩대조를사용한다. 누락/변조/중복좌표/필수구조분리누락은ValueError다. 참조한node문서만읽기내부에서공유하며반환dict/list는모든좌표에서분리한다. ResearchRepository.load/read_record와context_store.read_content가같은decoder를소비한다. 후자는원래부터record가아닌자료를text/base64로보여주는fallback을가져저장load의반려와같은API로해석하지않는다. 저장증가량은독립구조node·새목록행·참조좌표에비례하며Git압축률/속도상한이아니다.

review_engine._start_identity_review는새cycle.input_bindings={}를만든다. 이전cycle의원binding은보존되며review_cycle.validate_sealed_review가이전판본을유일한보존cycle에연결해재귀적으로검증한다. 전문복원은turns/transcript_manifest, 현재결과검증은현재execution binding을쓴다. test_review_engine_stages와기존sealed replay4개가최종26선택에포함됐다. support.storage_snapshot_cases.fresh_reader는새installed_contract로publisher메모를벗어난실제decode를확인한다. 도메인8판본/4application 표본과공개AI완료/승인횟수를혼동하지않는다.

제품README/CLI참조는아직state/9 세곳이남아문서F3로표시한다. structure-fixes는이두문서와구조반려35건의지정시험16개를소유한다. support.smell_rules.smell_issues(source,path)의현행unpinned_rejection은단순assertRaises만있고원인검사가없는시험을찾는다. 시험이나검사기수리는실제반려원인을보존하고오판최소반례로판정한다. 당시 r31-r33 소유였던 sim/test_role_input_context.py 9건은0026에서 미수리로 확인돼 r31-fix가 소유한다. structure-fixes에서는 계속 읽기 전용이다. 두진행task와새task의유일한writes교집합은증거보존뒤base로복원하는비용캐시이며새API/면제목록/제품runtime수리를추가하지않는다.

## 0026 수용: 단위 실패·native 재수신과 역할 입력

CallEngineMixin._fail_input_preparation(base,execution_id,error)는 reload 뒤 queued·capacity 없음·input_bundle 없음인 미입장 실행에만 적용한다. waiting_action의 execution_failure/failure_kind=input_preparation과 원action/input_snapshot·형/원인/traceback을 보존하고 기존 route_failed_action/_discard_prepared_input으로 start_failed·대기를 만든다. admission 후/저장소 전체 장애를 이 경계가 흡수하지 않는다. CoreEngineMixin._apply_inbox의 candidate 예외는 reload 뒤 이미 processed된 결과를 유지하거나 control_application_failed/정확ID 반려를 게시한다. _retry_submission_publications는 같은 execution의 publication wait만 submission_failure로 옮기며 accepted 결과/봉인 본문을 되돌리지 않는다. GitStateStoreError와 복구 저장 실패는 전파한다.

CoreEngineMixin._collect_submitted_result는 native 증거/중앙 capture 실패에서 status=failed,error_kind=execution_failure와 원 provider_result_status를 같이 보존한다. _resume_initial_native_final은 provider_result_status(없으면 원status)가 completed인 provider_evidence_only를 후보로 삼으며 native_final.verified_native_final이 실제 수락을 판정한다. verifier가 추가로 허용하는 failed 조합은 provider_evidence_only+execution_failure+provider_result_status=completed뿐이다. 원stream/final/request/profile/process/worker exit0/종료barrier/input-authority 검사는 그대로다. _capture_native_submission/_finish_native_recovery는 현재 권한/기초/출력 봉인을 검사한다. 공개 retry 후 원interpret1회·원bytes/owner/capacity/prior_failure 보존과 같은 request 재전달 불변, 뒤 독립check1회를 구별한다. failed를 무조건 completed로 바꾸는 API가 아니다.

SubmissionModel.preserve_reply(role,execution_id,output,extensions)는 검사한 응답 복사본의 execution별 규칙을 첫 순서에 둔다. OwnerIngressAssertions.install_family_probe와 CatalogPopulationTests.install_probe는 같은 출력을 생산/수신에 사용하고 read_sealed_submission의 output/extensions 전값을 비교한다. assert_candidate_admitted는 같은 bytes로 producer_check와 공개 submission_preview의 seal/currentness/apply/validate_candidate를 소비한다. preview는 authoritative=false·실instance/runtime 불변이며 마지막 실제submit/게시와 구분한다. reject_and_replay는 producer와 receiver의 issue 전목록을 같은 expected에 비교한다.

role_input_requirements.judgment_input_keys/paths/source_lists/source_refs는 현재 역할 문서의 설정·profile_selection.profiles_ref·task_catalog[].source_ref·sources 등을 지정한다. support.role_input_requirements는 각 root를 읽고 path/local_path를 실제 read_source의 hash/bytes/status로 검사한다. assert_missing_judgment_inputs_rejected는 시험 관찰자의 자기검사이며 제품 수신 guard가 아니다. 파일 삭제/동일 크기 변조의 제품 read_source는 각각 missing/source_missing과 error/source hash differs from reference를 반환한다. 허용null/복원실패/unresolved를 가짜 정상값이나 무조건 제출 반려로 바꾸지 않는다.

F4의 지급 local_path/자료 정체성 불일치는 r31-fix에서 해결됐다. 현재 계약은 아래0028절과 제품 task_scope.assessment_basis 정의를 따른다. r34-r36의 structure.test_rule_consistency.RULES 및 열한 쌍 차분 보완도 수용됐으며 서로 다른 목적의 근거를 합산하지 않는다.

## 0027 수용: 문서 반려와 대기 후속 경계

README/references/CLI-실행-계약.md의 저장 계약은 do-math-state/10이고 역할 wire는 do-math-cli/5다. payloads의 snapshot/payload 노드는 바이트 수·SHA·정규 JSON·구조 참조를 검사해 논리값/목록 순서와 독립 가변 반환을 복원한다. 이번 변경은 설명/시험뿐이며 runtime124는 불변이다. 문서 hash 변경을 이전 실호출 판본의 독해 재인증으로 쓰지 않는다.

tests/support/doc_code.py:_is_callable_reference는 실제 모듈/속성을 찾아 callable 여부를 반환하고 function_reference_issues의 명시 module.function(...) 검사가 소비한다. structure-finish 수용 후 입력-소비자.md는 governance.apply_decision(...)을 쓰며 governance_field_issues의 한국어 생산 문구 전용 분기는 제거됐다. 단독 이름/오타/alias는 필드 검사 대상이고 명시 함수의 오타도 function_reference_issues가 반려한다.

tests/support/engine_context.py:assert_review_documents(owner='role_review')는 실제 review_cycle.context_for 값과 지급 입력을 비교한다. structure-finish 수용 후 identity_basis/policy_ref의 존재 비교는 role_review.<field> presence, 값 비교는 role_review.<field> 진단을 붙인다. sim/test_submission_review_inputs는 각 필드의 누락을 해당 진단에만 결박하며 기존 단계 모집단·원입력·proposal/소유 좌표를 유지한다. r31-fix의 별도 role_input_requirements/helper와는 다른 시험 관찰자다.

r37-r38의 정본 연결은 do_math/wait_rules.py:WAITING_ACTION_RULES/ACTIVITY_WAIT_RULES/REVIEW_WAIT_RULES와 waiting_action/update_waiting_action/activity_wait_record, activities와 reporting의 실제 생산/조회다. 선언의 condition/resolvers/next_owner와 실제 owner 호출을 대조하고 support/wait_reporting.py의 JSON/사람 표시 단언을 연결한다. 등록/constructor 표본과 실제 조건 전후 전이를 구분한다. core/decision/task_scope/planning/context_store/lifecycle 등 현재 다른 task 소유 파일은 읽기 전용이며 새 API나 schema를 이 문서에서 선결정하지 않는다.

## 0028 수용: 지급 자료 기초와 규칙 차분의 실제 계약

CoreEngineMixin._apply_plan 및 _complete_operational_disposition은 submission.issued_input에서 복원한 고정 sources를 전달한다. decision_engine._apply_task_plan과 task_scope.apply_task_assessments의 키워드 input_sources는 이 목록이다. assessment_basis(task, assessment, instance, runtime, *, records=None, input_sources=())는 지급 source의 local_path와 같은 인용을 기존 basis의 {source_id, sha256} 값에 연결한다. 최초 sha256는 local_path를 제외한 지급 source 기록의 exact_content_hash다. 재검사에는 저장 source_id의 현행 기록 해시를 쓰며 소실 시 sha256가 null이다. 다른 참조는 기존 해시/null 표현을 유지한다.

task_scope.assessment_current는 이 재계산값과 저장 basis를 비교한다. 현재 순서·basename·다른 실행의 locator가 원 정체성을 대신하지 않는다. 원 missing_inputs와 봉인 output/extensions/check, receipt는 불변이고 상태 계약 state/10도 유지한다. flows.test_submission_missing_input_aliases의 실제 공개 저장/restart·재계획과 unit.test_planning_assessment_refs의 잘못된 재결박 대조가 근거다. 운영 판정의 새 전달은 정적 확인 범위다.

sim.test_lifecycle_engine_controls의 문서 grant 시험은 실제 두 예시 JSON을 producer에 승인하고 _action_lifecycle_gate→authorize/_execution_stop_requested를 연결한다. unit.test_activation_requirements는 build_profiles의 실제 registry를 select_profile에 보내 동일 역할 수용·다른 역할 정확 반려를 검사한다. unit.test_role_input_packaging의 실제 prepare_role_input→fit_context는 required_direct_keys의 snapshot/action/governance/execution_profile을 보존하고 goal/policies 선택 사본은 read_source의 bytes로 복원한다. JSON 전체 필수 크기에 더한1200byte와 역사 전체1200byte 입력을 구별한다. 이 변경에서 runtime124는 불변이다.

## r39-r42 제공·소비 경계

questions.py의 QUESTION_OWNERS/link/user_waits/resolve_user/resolution_error와 question_engine의 실제 적용이 질문 소유·정확 대상·부분 해소의 정본이다. revisions.py의 record_repetition/record_execution_outcome/repetition_hold/action_repetition_waits/continue_repetition과 task_contracts.py의 REPETITION_OUTCOMES/REPEAT_LINEAGES/repetition_lineages가 반복 생산·계수·한도·공개 계속을 연결한다. lifecycle_engine 및 core/decision/governance/revision/planning owner의 실제 소비와 기존 시험에서 조건 전후를 확인한다. 새 registry나 API를 이 문서에서 선결정하지 않는다.

r39-r42는 자신의 owner/직접 시험만 수정해 수용됐으며 r37-r38의 wait_rules/activities/reporting/wait_reporting은 고정 시작판으로 읽었다. 실제 status_report/render_human_report의 F2는 r39-report가 수용된 두 task 위에서 이어받는다. 별도 표시기나 진행 중 task의 미완성 결과를 소비하지 않는다.

## 0029 수용: 활동 조건과 대기 후속의 소유 경계

activities.resume_activity(runtime, activity_id, *, condition, at)는 알려진 waiting 활동만 받으며 canonical.same_json_value로 저장된 waiting.condition과 전달 조건의 JSON 정체성을 비교한다. 1/true·0/false 및 중첩값은 다르다. 불일치/재해소는 ValueError이며 원상태를 보존한다. 정확 조건이면 ready/resumed_at을 기록하고 waiting을 지운다. 이는 caller가 지정한 정확 조건을 비교하는 API이며 조건 문자열의 충족 여부를 추론하는 범용 평가기가 아니다.

reporting.render_waiting_activities는 각 대기의 기존 사유/담당자와 coordinates JSON 뒤에 condition JSON 한 줄을 표시한다. 저장 schema와 status_report 투영은 바뀌지 않았다. tests/support/wait_reporting.assert_activity_wait_row는 실제 activity.waiting·activity_kind·owner/실행 좌표와 공개 JSON/사람 출력을 대조하고 반환 가변값의 독립성을 검사한다. assert_wait_report는 실제 action의 owner가 waiting이면 이 helper도 호출한다. constructor/API 33표본과 실제 owner의 조건 전후는 구별한다.

미수리 F2의 생산은 core_engine.CoreEngineMixin._register_execution의 review admission 반려다. waiting_actions의 action/detail과 활동 condition에는 admission을 보존하지만 review_engine.ReviewEngineMixin._release_review_wait는 recovery.review_cycle_id/action(stage,round,slot) 또는 condition.action_ids에 맞는 활동만 해소한다. raw admission은 이 좌표가 없어 정확 _authorize_review_replacement 뒤 action wait는 없어도 activity가 남는다. 다음 실제 registration은 해소한다. r37-review가 두 owner의 생산/소비와 직접 시험을 함께 수리하며 새 계약의 구체 형식은 구현 전에 선결정하지 않는다.

r37-review는 r39-r42 수용 후 core/review owner를 소유하며0030에서 선행이 충족됐다. r37-edges는 formal_engine의 _resume_formal_waits/_trust_activation_steps/_trust_check_steps와 external_engine의 _external_control/_external_execution_record를 소유한다. r40-r43은 provider_engine/provider_wait/session_slots·repair_execution/scheduled_operator·integration.SUBMISSION_OUTCOMES와 control_protocol.SELF_CHECK_PROGRESS/observations의 실제 계수 소비를 소유한다. 각 task의 정확 경로는 task.json/objective.md에 있고 이 세 task에서 공유 wait_rules/activities/reporting/wait_reporting은 읽기 전용이다. 현재 충분한 helper를 쓰며 실제 범위 밖 결함은 입력·관측·필요 파일로 인계한다. r37의 과제대기/일부 core 소유 남김은 plan의R41 후속을 따른다.

## 0030 수용: 시계 pause의 동일 사건과 상태 표시 후속

lifecycle_engine.LifecycleEngineMixin._refresh_readiness는 unusable clock guard를 runtime.clock_guard/availability에 보존한다. 인스턴스가 종결되지 않았고 lifecycle.state가 paused가 아니거나 stop_requested가 clock_regression이 아닐 때만 _pause_lifecycle('clock_regression')를 호출한다. 같은 retained failure를 보는 추가 refresh는 새 PA 이력·실행 정지를 재발행하지 않는다. 같은 owner의 wall이 따라잡아도 실패는 유지되며 새 owner가 시계를 다시 관측하고 공개 user resume을 받아야 재개된다. 초기/다른 사유 pause·명시 해소 권한은 기존 계약이다.

questions.QUESTION_OWNERS는 user/research/operations다. 실제 봉인 output/extensions의 question_routes·question_resolutions는 기존 link와 정확 대상/권한 검사를 소비한다. user의 부분 답변은 unresolved_target_ids를 남기고 AI의 resolved/superseded는 자기 질문만 닫는다. revisions의 반복11결과·계보5종과 계수 API는 바뀌지 않았다. continue_repetition은 현재 hold_event_ref와 정확 action scope를 요구하며 다음 주기에는 새로운 hold가 생겨 이전 승인을 재사용할 수 없다. 이 전이/계수 보완과 다음 표시 인터페이스 수리는 구분한다.

question_engine.question_view(instance,runtime,read_many)는 저장 원문 좌표에서 질문 text와 상태/owner/대상을 복원한다. reporting.status_report가 이를 question_links와 user 질문목록으로 반환한다. revisions.active_repetition_holds(runtime)는 현재 history를 소비해 (lineage,lineage_id)별 active hold를 돌려주므로 JSON 투영 시 tuple key를 그대로 노출하지 않는다. 현재 보고에는 이 구조적 hold 투영이 없으며 human에도 질문/hold가 없다. runtime.user_pause의 request_id/reason/created_at는 supervision_facts를 통해 최상위 JSON에 있으나 operating_summary의 user_pause blocker는 request_id를 생략하고 human은 reason도 생략한다.

r39-report는 reporting.py·기존 직접 소비시험·필요 wait_reporting helper·해당 제품 설명과 미러를 소유한다. 위 세 공급자를 소비해 질문/보류/중단의 사유·다음 소유자·정확 좌표와 해소 후 상태를 한 status_report/render_human_report 경로에 연결한다. 구체 필드/표시 형식은 task가 실제 정의와 함께 확정한다. 상태 저장 스키마나 새 전역 blocker 우선순위를 미리 정하지 않는다. render_human_report는 전달 report만 읽고 현재 host 사실을 재조회하지 않는 계약을 유지한다. 다른 세 owner task는 자기 시작판의 reporting/helper API를 계속 사용하며 기존 action/activity/condition 표시 API는 보존한다.

## 0031 수용: 형식·외부·설치의 정확 활동 해소와 시간 후속

formal_engine.FormalEngineMixin._resume_formal_waits는 기존 FORMAL_WAIT_RULES/environment_changed/현재 권한 관문을 통과한 waiting action의 원 owner를 유지한다. 행동을 큐에 돌려놓고 waiting_actions에서 지운 뒤, 같은 owner의 status=waiting·같은kind이고 condition이 직접 {kind,knowledge_id} 또는 해소된 action_ids를 참조할 때만 activities.resume_activity(runtime,id,condition=저장조건,at=현재시각)를 호출한다. action_ids가 여러 개면 남은 waiting action이 없어야 한다. 일치하지 않는 owner/kind/조건은 건드리지 않는다. _formal_steps의 stop 함수는 governance가 실제 생산한 stop_requested=grant_revoked를 authority_changed로 분류하고 나머지는 execution_stop_requested로 보존한다. FORMAL_RECOVERABLE_STOPS·실제 재입장 권한/환경/고정입력 검사는 유지한다.

external_engine.ExternalEngineMixin._external_control의 retry는 같은 현행 grant·request-bound evidence·academic prerequisite 검사를 통과한 뒤 previous.execution_id의 원 실행이 있으면 continuation_of/owner_activity_id를 _enqueue에도 명시한다. 그 원 owner가 external_reconciliation/external_followup으로 기다리고 condition이 정확 {operation_id:entry.id,status:previous.status}일 때만 기존 resume_activity로 해소한다. 원 실행이 없는 전송전 준비도 기존 경로로 처리하며 새 가짜 원실행을 만들지 않는다. ledger history/attempts·원 ended execution과 전송/재조정의 의미는 유지한다. 실제 unknown의 confirmed+succeeded 재조정은 기존 _external_execution_record에서 해당 활동만 끝낸다.

repair_execution.resume_installation_repair(runtime,record,repaired_by,at)는 검증된 복구가 target의 후속을 만들고 처분을 applied로 기록한 뒤 그 target의 owner 활동이 waiting이면 저장된 condition을 resume_activity에 넘긴다. 기존 continue_activity는 waiting을 자동 해소하지 않는 API이므로 이 owner가 검증 성공을 소비해 해소한다. 기존 successor가 있을 때의 early branch·원결과/봉인·진단·로컬종료/예약정산은 바뀌지 않았다. 실제 operational_repair와 output_validation 경로를 직접 시험하며 다른 활동은 보존한다.

integration.SUBMISSION_OUTCOMES/submission_outcome→repair_execution.route_submission_return의5분류는 output_rejected만+1이다. repair_execution.RECOVERY_OUTCOMES/recovery_attempt_counts는6결과의 report/termination 의미를 소비하고 scheduled_operator.recovery가 실제 결과를 기록한다. control_protocol.SELF_CHECK_PROGRESS→observations.ObservationTracker.record_self_check_response는3값의reset/increment/retain을 소비하며 acknowledge_review는reset이다. provider_wait의attempts/generation은 공급자 재관측/backoff이며 위 계수나 revisions의 반복계보와 별개다. r40-r43의finite-populations.json/assertions.json은 선언·실제소비·기존단언을 연결한 근거이며 전건 새 실행이 아니다.

신규 r47-r48은 execution_window.AI_CALL_TIME_RULES/call_deadline/deadline_passed/publish와 call_engine._prepare_call/_call_started/_call_stop_requested, observations.OBSERVATION_PHASE_RULES/ObservationTracker 및 observation_transport의 source 시각 생산을 판정한다. 현행 호출 기한은 입력 게시 뒤 고정 profile로 만들고 monotonic으로 비교하며 UTC는 설명에 사용한다. work는 무기한, operational은 프로필 call_timeout_seconds다. 공개 정지는 즉시이며 전체run 기한/checkpoint 유예는 없다. 관찰의 source received_at/received_monotonic/행offset과 뒤 처리 시각, live/evaluate/running·stopping·ended를 현행 코드와 직접 소비시험으로 구별한다. 현재 충분한 표/시험을 재사용하고 새 타이머나 schema를 먼저 정하지 않는다.

r37-review의core/review와 r39-report의reporting/wait_reporting·제품 설명은 기존 소유를 유지한다. r47-r48은 이 파일들을 읽기만 하고 별도의 call/observation5파일·지정 시험/전용helper·미러를 소유한다. R41의 task/core대기는 r37-review수용 뒤 다룬다. 정확 쓰기는 task.json/objective.md이며 공통timings는 증거 보존 뒤 own base복원한다. 검수된18제품경로의통합과 판본 한계는 managers/0031/integration-check.json·source-review.json·reuse-check.json에 있다.

## 0032 수용: 정확 검토 해소와 현재 질문·반복·pause 투영

이 절은0029의 미수리F2와0030의 표시 누락/후속 예정,0031의 r37-review/r39-report 진행 상태를 갱신한다. CoreEngineMixin._register_execution은 held가 아닌 review admission 반려에서 activity.waiting.condition을 {**admission, action_ids:[action.id]}로 생산한다. 기존 ReviewEngineMixin._release_review_wait는 waiting_actions의 같은 review_cycle_id/stage/round/slot을 해소한 ID와 condition.action_ids의 교집합을 소비한다. 기존 recovery 좌표 소비와 REVIEW_WAITS/활동 상태 필터를 유지하며 다음 실행 등록 없이 원 활동을 ready로 만든다. held 경로는 원 조건/담당자를 보존한다. unit.test_review_wait_contract의 exact reauthorization 메서드와 기존 owner_guards가 직접 근거다.

review_input_restoration의 실제 생산은 call_engine의 materialization 실패→review_preparation_wait이며 _retry_review_restoration이 정확 복원 뒤 같은 원 action/owner를 해소한다. sim.test_review_owner_path.PreparationFailureTests의 실제 EBUSY/복원/저장/restart·후속1개와 표시 부재가 근거다. review_resource_deferred는 _settle_review_resource_dispositions에서 고정 cycle_id/proposal_digest 조건을 생산하고 제안 supersession/withdrawal·instance 종료 때 ended/unresolved·finished로 정리한다. unit.test_review_resource_evidence의 실제 scope 반려/knowledge.replace_knowledge·다른owner 보존이 근거다. 새 자원/시각이나 별도 resume API를 의미하지 않는다. wait_rules의 부정확한 산문은 r41이 현재 출구로 교정할 제품 후속이며 manager가 제품을 직접 고치지 않는다.

reporting.status_report의 question_links는 question_engine.question_view의 전건이며 기존 user questions도 유지한다. 새 repetition_holds는 revisions.active_repetition_holds(runtime)의 독립 값 목록으로 tuple key를 노출하지 않는다. history의 repetition_hold를 (lineage,lineage_id)별로 모으고 같은 계보의 task_repetition/outcome=continued가 해소한다. 행의 kind/lineage/lineage_id/event_ref/count/limit/owner/next_owner/reason/release_condition/question은 유지한다. task0의 active hold도 표시하며 primary_blocker 우선순위는 바뀌지 않는다.

operating_summary의 user_pause blocker는 supervision_facts의 저장 pause reason/request_id/created_at를 kind/next_owner와 함께 보존한다. render_human_report는 report만 읽어 open 질문의 본문·사유·owner·blocks·원문/실행 좌표·원/미해소 대상, 현재 보류의 계보·사건·계수/한도·담당자·해소 조건, pause의 세 필드를 표시한다. resolved/superseded 질문은 JSON 이력에만 남고 현재 질문 표시에서 제외한다. source 복원불가는 text=null/source_status=unavailable 그대로다. 새 상태/호스트/시계 조회는 없다.

tests/support/wait_reporting.assert_status_report(test,engine)는 실제 store.load의 한 head로 status_report를 만들고 JSON 왕복값을 renderer에 전달해 snapshot과 저장값 불변을 확인한 뒤 report,human을 반환한다. 기존 action/activity helper API는 불변이다. sim.test_governance_questions의 세owner/부분답변, sim.test_planning_repetition_engine의 task0 hold/정확continue, sim.test_lifecycle_engine_public의 operator반려/user resume가 실제 생산·저장·해소와 연결된다. unit.test_storage_report_projections의 문서 필드 소비/삭제 반례도 새 공개필드를 확인한다.

r41은 task/core/planning·관련 reporting와 현재 설명을 소유하며 r47-r48의 call/observation owner는 읽기 전용이다. r44-r46은 input_basis/planning/task_scope·readiness/trust·봉인 준비 입력/편입의 다섯 축을 고정 사본에서 읽기만 한다. 진행 중 r41의 결과를 소비하지 않으며 source SHA와 실제 심볼을 남겨 이후 관련 변경만 재대조한다. 확인된 근거와 필요한 수리를 구별하고 새로운 제품 registry/API를 사전 결정하지 않는다. 정확 범위는 두 task의 objective.md/task.json이다.

## 0033 수용: 관찰 수신 시각과 전달 뒤 응답 창

이 절은0031/0032의 r47-r48 진행 표기를 갱신한다. ObservationTracker._snapshot의 observed_at은 observation_source.received_at이고 observe의 explicit review 비교도 같은 원 수신UTC를 사용한다. 자기점검 wall_time_reached 규칙과 예약 검토가 지연 처리만으로 앞당겨지지 않는다. fact/의무 기록의 observed_at과 core가 게시하는 observation_stream.applied_at은 계속 실제 처리 시각이다. received_monotonic은 기존 경과/순서 정본이다. 도구/관찰 source와 대화 임대의 실제 처리 UTC는 다른 입력 의미다.

ObservationTracker.issue_self_check는 실제 전달 시각에 응답 창/기존 hold를 다시 시작한다. _hold_deadlines의 새 hold 시작은 max(사건offset, deadline-response_window)이고 종료 시 deadline에 max(0, 종료offset-held시작)을 더한다. 전달 전 수신된 start/completion을 뒤에 소비해도 전달 뒤 창을 소급 단축하거나 과거 도구 시간을 과잉 더하지 않는다. 열린 의무·deadline 존재·기한 뒤 새 도구 비hold와 복수 도구/safe boundary 규칙은 유지한다. 새 저장 필드는 없다. unit.test_observation_tracker.DeadlineHoldTests의 buffered_tools 메서드가 두 순서의16초 보존과 응답 수신을 확인한다.

ModelRunner.run.observe→frame_rows→ObservationBatch는 한 read의 원 시각/bytes/offset을 최대4행 part에 보존한다. first_row는 연속 행좌표, 마지막part만 ends_read/caught_up이다. core._observe_running은 행 evaluate=False와 caught_up tick·fresh 종료증거의 live를 소비한다. sim.test_observation_delivery.StreamChunkTests의 실제 worker/runner/외부대역 경로와 flows.test_observation_application의 실제 owner/Repository 지연tick은 서로 다른 경계의 근거다. ended replay는 사실과 원source/뒤처리시각을 보존하고 새 의무를 만들지 않는다.

call_engine._prepare_call은 고정 profile로 입력 게시 후 기한을 만들고 _call_started/_call_stop_requested는 그 monotonic 기한을 소비한다. sim.test_engine_queue.QueuedPreparationTests의 새 호출창 시험은 준비500초/기동1초·현재설정 변경에도 고정 기한과 최초 stop bytes/정산을 보존한다. 이 시험의 window-final1passed는 F2수리 전 별도판본이며 마지막57passed에 합산하지 않는다. 기존 work 무기한·공개 즉시정지와 도구 timeout1/3600/누락과 관찰창의 분리는 유지한다.

r50은 operator_bootstrap.freeze/verify_snapshot/main, supervision.OPERATOR_SCHEMA/repair_report_schema, scheduled_operator.main/check/run_engine/recovery와 repair_execution의 수리 결과 제공/소비를 소유한다. core/engine/cli 기동은 고정 사본에서 읽고 실제 남김을 r49-startup에 인계한다. r49-startup은 수용된 r41의 core와 r47-r48 관찰 계약 위에서 _schedule_operational_reviews·conversation_lease_live/_conversation_control/_check_conversations 및 엔진 기동 결과를 처리한다. r50의 exact 원보고/소스SHA를 입력으로 받고 관련 core 변경만 다시 대조한다. 공유 제품 설명은 r49-startup에서 현재 정의와 함께 갱신한다. 새 필드/registry/API는 공용 문서가 사전 확정하지 않는다.

## 0034 조사 당시 현재성 수리 경계 (수리 후 계약은0037절)

이 절은 r44-r46 진행 표기와 r49-startup의 선행 설명을 갱신한다. 제품 API는 이번 manager에서 변경하지 않았다. r44-r46의 judgment-matrix.json J01~J15는 판정별 실제 producer/consumer·근거 필드·관리/내용/모집단/봉인 뒤/동시상태 축을 연결한다. source-editions의56파일과 test-assertions의63ID AST는 manager0034 시점 공용판과 같다. 수리 담당은 이 중 선행 r41이 실제 바꾼 관련 함수만 다시 읽는다.

현재 lifecycle_engine.LifecycleEngineMixin._refresh_readiness는 required={revision,contract_sha256,goal_revision,policy_revision}를 만든다. contract_review_current는 현행 전체 근거로 결과의 유효성을 판단하고, blocked_review는 같은 basis/key를 소비한다. live_review도 전체 required equality를 사용하므로 정책만 바뀐 동일 과제 계약의 실행을 놓친다(F1). core._enqueue는 미착수 queue를 병합하는 별도 책임이다. 수리는 같은 과제 판본의 running/stopping 중복 억제와 ended 뒤 최신 근거의 후속 개설을 구별한다. 원 action/봉인·다른target·실제 계약개정의 의미를 유지한다. 기존 live-review 시험은 profile 변경의 running/ended만 직접 단언하며 stopping 사이 refresh는 후속에서 확인한다.

knowledge.capture_basis(instance,runtime,record_ids)는 서로 다른 기존 ID를 받아 {id,sha256,status} 목록을 생산하고 validate_basis는 {valid,reasons}를 돌려준다. KN에는 _hash가 전체 레코드를 쓰므로 review_cycle_id/history만 바뀌어도 hash_changed다(F2). formal_results/expositions의 record_digest 분기, 좁은 인용 projection인 decision_reference, 원문/봉인 bytes용 exact_content_hash는 각각 다른 계약이다. core._goal_basis_key도 knowledge map 전체를 넣으며 goal 호출 중 stop/수락/slot 그룹이 소비한다.

실제 연결은 review_engine._start_identity_review의 KN.review_cycle_id 생산, governance_engine._apply_governance_goal_audit의 record_basis 저장→knowledge_engine._invalidate_goal_currentness, knowledge_io.import_candidate의 relation_endpoint_basis→knowledge_records.record_premises_current, core._apply_extensions의 research_insights capture/validate다. 수리는 기존 owner에서 수학 내용·판본·효력/use·trust/source/verification·모집단에 필요한 근거를 선언·공유하고 관리 정보의 불필요한 민감도만 제거한다. 저장 basis 모양을 사전 변경하거나 exact 무결성 검사를 약화하지 않는다. 순수 probe는 두 dict의 해시 성질만 관측했고 저장/엔진 여정은 후속의 유효 producer·기존 직접 harness가 맡는다.

r44-fix는 r44-r46·r41 선행이며 knowledge/core/lifecycle와 직접시험/설명·미러를 소유한다. 독립 r50의 bootstrap/supervision/operator/repair는 읽기만 한다. 미착수 r49-startup에 r44-fix 선행/보고 입력을 추가해 공유 core/lifecycle·test_call_stop_flags·이음새 설명이 수용판에서 이어지도록 한다. r41·r50의 시작 정의는 바꾸지 않는다. 정확 writes/inputs는 새 queue entry와 각 objective.md다.

## 0035 수용: 원 대기 정산과 운영자 판본 근거

이 절은 r41/r50 진행 예정 표기를 갱신한다. CoreEngineMixin._register_execution은 machine acquire가 성공한 뒤 waiting 활동을 resume한다. 동일 machine_capacity condition은 same_json_value로 대조해 원 waiting/시각을 보존한다. task_scope.apply_task_assessments과 RevisionEngineMixin의 대기 생산은 reason/basis_ref를 보존하며 일반 계약검토 반려는 core._apply에서 contract_revision 준비 owner로 연결한다. 학술 전용 preparation은 원 계약을 보존하는 기존 경로를 쓴다.

RevisionEngineMixin._settle_revision_owner(entry)는 action.owner_activity_id, ended execution의 owner, waiting.kind=revision_dependency와 condition.action_ids의 해당 action을 대조하고 기존 _settle_activity(execution.id)를 호출한다. 정확 처분/위임·대상은퇴의 waiting_action 삭제 뒤 남은 요청/실행/의무에 따른 원 활동 정산이다. finished를 목표/과제 성공과 동일시하지 않는다. reporting.task_status의 targets_task는 직접 target 또는 research_preparation의 assessment_targets/observation_rule_targets를 queue와 live execution에 같이 적용한다. tests/support/wait_reporting.assert_task_wait_report는 실제 저장값의 사유/담당자/좌표·JSON/사람표시·조회 불변을 소비한다.

supervision.OPERATOR_SCHEMA와 repair_report_schema는 installation_version:string, source_commit:string|null을 필수로 생산한다. preflight.inspect_bundle는 recovery/recovery_diagnosed를 둘 다 소비한다. repair_execution.installation_evidence(root,backend=...)는 installation_files/installation_sha256의 전체 설치 bytes와 GitBackend의 source HEAD/subtree/raw_diff/미추적 설치목록을 관측한다. Git 불가는 source_status=unavailable/source_commit=null/사유이며 설치 hash 자체 실패도 별도 installation_error/null로 남긴다. 관측 HEAD는 연구 snapshot이나 clean/커밋 반영 인증이 아니다.

scheduled_operator.recovery는 input/installation-before.json과 execution.input_manifest.installation_before를 생산하고 모델 종료 뒤 installation-after.json 및 result의 전후관측을 저장한다. repaired 수신에서는 supervision.check_repair_version(output,observed)가 두 필드 equality를 검사하며 불일치 ValueError는 원output을 보존한 recovery_failed로 정산하고 receipt/검증child/restart를 막는다. 원 provider/model-policy 결과는 판본수집 실패만으로 교체하지 않는다. 실제 ModelRunner/worker schema 수신, 설치bytes변화/가짜commit 반례와 예약해제/저장은 flows.test_operator_recovery_contract와 sim.test_provider_schema의 직접 근거다.

operator_bootstrap.startup_evidence(manifest)는 verify_snapshot을 통과한 원manifest와 live target을 비교해 match/different와 파일별 expected/observed SHA 또는 unavailable을 반환한다. manifest 없음은 live/no_recorded_manifest다. main은 이를 scheduled_operator.main의 bootstrap_evidence로 넘긴다. 후자는 실행 전 operator/startup.json을 쓰고 결과에 startup={bootstrap,installation,runtime_root,observed_at}를 붙인다. 직접 cli.execute(operator check/probe/wake/run-engine)는 현재 이 main을 우회한다. 엔진 _installation_manifest의 기존 부분모집단/시작자체baseline과 이 전체설치 hash는 의미가 달라 그대로 equality를 요구할 수 없다.

r49-startup은 수용된 r50의 이 세 관측/대조 정본을 재사용하고 직접CLI/예약 기동의 기록을 공유하도록 scheduled_operator와 필요한 CLI계약·직접시험의 쓰기를 추가로 소유한다. schema/supervision/repair_execution/bootstrap은 읽기만 한다. r44-fix 뒤 같은 core/lifecycle를 이어 받고 읽기전용status 해시지연·시작후polling/terminal 흡수를 보존한다. 제품설명은 이 후속이 실제 정의에 맞게 마친다.

독립 keep-runner의 입력/출력 정본은 scripts/run_tests.py:test_modules/discover/main/TimedResult/_run_suite/_worker/_edition이다. FOLDERS/TIERS와 디스크수집·오류/빈선택 exit2, selected/실제row·fixture/not_run·subTest·진행중실패파일/최종보고·source_sha256/changed_during_run의 현재 의미를13개 원K ID와 연결한다. 폐기 SHARDS를 복원하지 않는다. 일반 결과와 T3 측정store는 별개이며 전체관문 실행을 뜻하지 않는다. 새 task가 필요한 수리·직접시험·시험지침/미러를 소유하고 core/operator 또는 다른task의 미완성 코드를 소비하지 않는다.

## 0036 수용과 템플릿·격리 후속 경계

keep-runner의 runtime API는 불변이다. tests/support/runner_contracts.py:runner_tree(case)는 TestCase.enterContext로 임시 scripts/tests 아래 FOLDERS 패키지와 budgets.json을 만들고 run_tests.SCRIPTS/TESTS/TIMINGS·sys.path/modules만 격리하여 tests 경로를 반환한다. 실제 discover/main/_edition/TimedResult는 대체하지 않는다. 임시 소스 변경 표본은 공식 검증 중인 workspace 밖에서 실행한다. unit.test_runner_regressions와 test_runner_tiers.ReportTests가 이 준비를 공유한다.

run_tests.main은 새/빈 output에서 실제 시험을 실행하고 비빈 output을 SystemExit2로 반려해 원 보고 bytes를 보존한다. _run_suite는 class/module 준비 오류를 fixture error와 선택별 not_run으로 남기며 준비 skip은 fixture skipped와 선택별 skipped다. complete는 보고 완결성이고 성공 여부는 successful·counts/fixture_counts·exit와 함께 읽는다. _edition은 실제 scripts Python bytes의 실행 전후 추가/삭제/변경을 검사하고 변경된 실행의 successful/exit를 반려한다. 실패 즉시 게시하는 complete=false 파일은 최종 보고가 아니다. 지정27ID 실행은 전체 일반/T3나 실제 OS 완료의 증거가 아니다.

keep-templates는 support/sim.py의 template_inputs/warm_built/_Template/Sim.process_state/restored/activate/_apply와 support/engine_purpose.py:purpose_sim/drive 및 직접 소비시험을 소유한다. template_inputs는 명시·생략 기본값을 같은 정규 JSON으로 만들고 capture/가변인자/비문자 object key를 반려한다. warm_built는 이름·builder 모듈/qualname·JSON 입력별로 프로세스 내 템플릿/실패를 보존한다. _Template은 같은 live 절대경로에 복원하고 shared는 복사하지 않는다. assert_template_quiescent는 제품 session_slots.quiescence와 Jobs/Calls 미정산을 검사한다. 현재 process_state는 clock/대역 Job ID/대역 Git 객체를 복원하므로 역사 '디스크만' 표현을 현행 의미와 구별한다. 구체 수리 여부는 이 정의·실제 단언을 task가 판정하며 core/lifecycle/runtime와 공유 시험 지침은 읽기 전용이다.

keep-isolation은 run_tests의 표지별 묶음·_isolated/_worker/wait_for_worker/_empty/_exit_code와 test_categories.isolation_for, WindowsJob 및 지정 직접 경계시험을 소유한다. _isolated는 requested.json과 scratch 환경을 준비해 실제 worker를 시작하고 root+소유 자식의 종료를 기다린 뒤 native exit와 result.json을 함께 판정한다. 진행 중 row는 오류 시 not_run으로 남기며 준비 skip과 구별한다. 실제 native exit7 시험과 합성 상태 wait 단위시험은 다른 근거다. 제품 소유와 바깥 공식 시험 Job의 의미, 환경 변수의 설치 경로 소비를 판정하고 폐기 timeout/helper를 복원하지 않는다. 이 task만 시험 지침을 수정한다. 두 새 task와 r49-startup은 캐시 외 쓰기가 독립이고 캐시는 각 base복원한다. r44-fix는0037에서 수용됐으며 현재 계약은 아래0037절을 따른다.

## 0037 수용: 의미 근거와 계약판본, 역할 입력 후속

knowledge.basis_record(record:dict)->dict는 deepcopy한 현재성 투영이다. knowledge/formal_results/expositions/assessment_uses의 최상위 history/use_history와 knowledge의 review_cycle_id/previous_review_cycle_id만 제외한다. identity_assessments와 다른 가족은 전체를 남기며 unknown field·시각·내용·revision·출처·참조·lifecycle/publication/use·신뢰/검증은 유지한다. capture_basis의 {id,sha256,status} 목록과 validate_basis의 {valid,reasons} 형식·missing/hash_changed/status_changed 등의 기존 오류는 같다. formal_results/expositions는 기존 _hash→record_digest 소비를 유지한다. exact storage/봉인 원문·영향계획의 해시는 이 projection으로 바꾸지 않았다.

CoreEngineMixin._goal_basis_key는 knowledge_records.FAMILIES의 다섯 가족 전체ID/각 basis_record와 trust_environments/active_trust_environment를 함께 결박한다. 기존 goal/task/source/user input/정책/입력계약 좌표도 유지한다. review_engine._start_identity_review의 새 KN 검토일정은 goal을 중단시키지 않는다. governance_engine._apply_governance_goal_audit→record_basis→knowledge_engine._invalidate_goal_currentness와 knowledge_io.import_candidate→relation_endpoint_basis→knowledge_records.record_premises_current는 같은 capture/validate를 소비한다. content/use 변화는 goal unsolved/research_plan·호출 stop으로 이어지고 관리 이력 변화는 현재 수락/slot/관계근거를 유지한다. research_insights의 기존 원snapshot capture/현재validate는 정적 확인 범위다.

LifecycleEngineMixin._refresh_readiness는 contract_edition={revision,contract_sha256}와 전체 required={**contract_edition,**governance_revisions}를 구별한다. live_review는 동일 target와 contract_edition의 status!=ended 실행을 찾아 정책/외부근거 변화의 중복 개설을 막는다. 결과 currentness·blocked_review·미착수 queue와 ended 뒤 개설은 최신 전체 basis/key를 계속 사용한다. 다른 target/내용/revision 판본은 별개이며 원 action·core._enqueue·대기/입장 owner는 불변이다. r49-startup이 이어받을 변경은 이 함수, core._goal_basis_key, knowledge의 세 함수와 직접 goal-stop/현재성 시험·이음새 설명이다. 시간·기동 기능은 이 수리에서 수정하지 않았다.

keep-inputs는 support/role_answers의 실제 context source 읽기·candidate binding·seal_response와 support/model의 ModelDouble.render/output→FakeCLI.finish/_submit→실제 workspace submission_tool/worker/중앙receipt를 연결한다. 현재 model double은 schema를 자체 검사하지 않고 실제 수신자가 검사한다. bound/standalone·expected_receipt는 호출별 Answer이며 잘못된 영수증을 정상 returncode가 숨기지 않는다. PurposeResponder/PurposeAnswers와 InvestigationRunner·Overlap·role_reach는 각각 역할 입력의 의미 반려·정확 원source SHA·실제 동시 진입·held와 reached의 두 결과를 제공한다. 구체 보호성질의 충족/수리 판단은 task의 현재 정의/단언/원보고에 맡긴다. engine_purpose/직접시험을 공유하는 keep-templates 수용판에서 시작하고 runtime/sim/runner 및 공유설명은 읽기 전용이다.

## 0038 수용: 템플릿 복원과 요청별 공개 적용, drive의 현재 상태

tests/support/sim.py:Sim.control(action, **options)은 공개 제어의 수송 결과(request_id와 pending effect)를 반환한다. Sim._apply는 그 request_id를 받아 실제 engine.process_controls 뒤 _check_applied([request_id])를 호출한다. _check_applied(request_ids)는 각 engine.control_result의 durable receipt가 존재하고 effect=applied인지 검사하며, 없거나 rejected이면 ID와 원 결과/사유를 포함한 AssertionError다. 같은 거부 요청 재전달도 실패한다. 다른 이전 요청의 의도적 거부는 유효한 현재 요청을 오염시키지 않는다. ID를 생략한 _check_applied()는 support/scheduling_initial.py의 전체 준비 이력 검사로 남는다. 구판 호환 분기가 아니라 서로 다른 현행 소비 범위다.

Sim.activate는 초기 governance/grant/probe/trust 제어 묶음의 모든 ID를 검사하고 후속 trust transition/initialization adoption은 _apply를 사용한다. formal.verify_lean/_worker의 ObservedCalls와 formal Job/Lean checks, 실제 active 도달 검사는 유지한다. flows/test_activation.py의 네 시험은 빈 경로 양성·실제 verifier 진입 음성·공개 pause·거부 뒤 정상 저장을 확인한다. 음성 verifier는 empty declarations로 반려되며 native Lean/worker 실호출의 증거가 아니다.

tests/support/engine_purpose.py:drive(test, sim, predicate=None, limit=45)는 현재 responder.failures부터 실패시키고 predicate가 참이면 반환하며, 그 전에 만족되지 않은 paused/closed/waiting은 질문/queue/실행 요약으로 실패한다. 필요한 경우만 sim.step하고 최대 limit pass 뒤의 결과도 같은 순서로 검사한다. 기본 predicate는 goal_status=mathematically_solved다. 조기 predicate는 후속 대역 입력검사와 모든 단언 값이 이미 확정된 소비자에서만 사용한다. unit/test_engine_purpose_responder.py:PurposeDriveTests는 순수 loop 정책이고 실제 저장/owner 실행은 flows의 근거다.

flows/test_engine_purpose_solution.py:SolvedPurposeTests.test_public_activation_reaches_the_solution_with_archived_role_inputs는 매번 자기 TemporaryDirectory의 빈 경로를 Sim.activated(root, config=PURPOSE_CONFIG)에 전달한다. 실제 intent_interpretation 호출을 확인한 뒤 PurposeResponder/drive를 통해 목표해결, accepted receipt, 역할입력 원문SHA와 실제 형식결과 저장을 확인한다. 일반 purpose_sim(**config)는 정규 JSON settings를 빌드 키에 포함하는 템플릿 복원을 계속 제공한다.

_Template은 동일 절대 live 경로에 새 Sim/ResearchEngine을 복원하고 shared trust bytes/stat은 복사·삭제하지 않는다. Sim.process_state/restored는 외부 clock/Job ID·owner/Git 객체·worktree/format 대역 상태만 전달하고 엔진 readiness는 전달하지 않는다. sim/test_template.py는 실제 configure publication과 소비자 상태 변경이 다음 복원으로 새지 않음을 확인한다. support/cross_states.py:_restore_start의 실제 task_ready/_record_readiness 재계산·durable facts 불변은 기존 정의를 재사용한다. template_inputs/warm_built의 정규화·키별 실패·assert_template_quiescent의 제품 quiescence/Jobs/Calls 정산 계약은 유지한다.

정본7·미러7 통합, 작업판25passed/889PythonSHA의 범위는 managers/0038의 검수와 tasks/keep-templates/evidence/judgment-matrix.json에 연결한다. 이후 r44-fix가 바꾼 현재성 runtime3/직접시험5가 통합판에 있으므로 최종판 전체 성공을 뜻하지 않는다. keep-inputs는 이 수용된 engine_purpose와 직접시험을 소비하고 sim.py는 읽기 전용이다. keep-isolation/r49-startup은 자신의 고정 사본에서 계속하며 세 작업 사이 의미 있는 쓰기 겹침은 없다.

## 0039 수용: 격리 중단 보고와 저장 후속 경계

run_tests._isolated(tests,directory,measure=False)는 격리 wait_for_worker의 Exception/KeyboardInterrupt에서 자기 WindowsJob.terminate() 뒤 다시 전체 종료를 기다리고 원 오류를 보고한다. KeyboardInterrupt는 interrupted=true·complete=false·successful=false·worker_error이며 진행 중/미시작 선택은 not_run으로 worker-report.json에 남는다. _worker는 BaseException traceback을 redirected stderr에 기록하고 다시 전파한다. main의 jobs1 순차 경로는 interrupted 보고를 받으면 이후 묶음을 시작하지 않고 남은 선택을 group=interrupted의 not_run으로 채워 최종 실패 보고를 게시한다. in-process 부모중단이나 병렬pool취소를 새로 다루는 계약은 아니다.

wait_for_worker는 root wait signal과 _empty의 root_signaled/active_processes=0/process_ids=()가 모두 성립할 때 반환한다. 경과시간 기한은 없고 _exit_code의 native 결과가0이어야 JSON successful도 유지된다. 실제 OS/환경/진행·중단은 boundary.test_runner_isolation과 기존 test_runner_native_exit, 분류/묶음/후속 마감은 unit.test_runner_regressions가 확인한다. actual root 종료 뒤 소유 자식 PID 잔류를 관측하며 잔여 PID 개수를1로 고정하지 않는다. WindowsJob 구현은 불변이다.

tests/support/provider_inputs.actual_command()는 DO_MATH_KNOWLEDGE_TEST_LEAN을 우선하고 생략 시 portable_bin(toolchain_root())/lean.exe를 반환한다. boundary.test_knowledge_lean_verifier의 설치 계약도 이 명령을 inspect_toolchain/verify_lean에 전달한다. ToolchainInputTests는 순수 환경 입력 검사이며 현재 설치/실Lean 성공은 별도다. 시험 지침은 바깥 공식 Job/제품 안쪽 Job의 수명 책임과 주트리 도구 읽기 전용 사용을 연결한다.

keep-storage는 support.storage_records.engine_on/record_store·Sim에서 실제 ResearchRepository/StateContract로 이어지는 저장 guard와 artifact/reader/snapshot·published_state/save_with_state를 소비한다. 구조 공유 state/10·현재 검토 결말은 수용된 r22-snapshots/keep-templates/r03-fix의 소스에서 시작한다. K-45의 실제 owner는 core._save/_reload와 Calls 경계로 읽으며 core는 r49-startup 소유이므로 수정하지 않는다. K-52의 review_research는 keep-inputs 소유로 읽기만 하고 나머지 knowledge_roundtrip/review_inputs/knowledge_impact와 저장 직접시험은 새 task가 필요한 수리를 맡는다. API 변경은 조사 전 확정하지 않는다. 실제 필요가 범위를 넘으면 정확 입력/원인/소유파일을 report로 인계한다.

## 0040 수용: 예약 복구 순서와 독립 기동 판본

ResearchEngine.run(*,max_steps=None,watch=False,until_active=False,installation_manifest:Path|None=None)는 writer lock 안에서 reload/inspect 후 _record_installation_startup을 수행한다. 이 함수는 operator_bootstrap.verify_snapshot/startup_evidence와 repair_execution.installation_evidence를 소비하고 <workspace>/execution-control/<instance>/startup.json을 canonical_json/write_bytes_atomic으로 게시한다. 반환 startup은 manifest_path, bootstrap, installation, runtime_root, polling_edition, observed_at을 담으며 run의 모든 정상 반환에도 포함된다. 생성자/status는 이 수집을 실행하지 않는다. CLI run --installation-manifest와 JSON payload.installation_manifest는 같은 Path 입력이다.

manifest는 검증된 동결 bootstrap의 파일로 installation_root가 현재 설치와 같아야 한다. 손상/다른root는 오류로 전파한다. bootstrap.comparison=different|unavailable이면 dispatch 전에 installation_startup_mismatch로 pause하고 종결은 유지한다. manifest 부재는 {mode:live,comparison:no_recorded_manifest}이며 독립 대조 성공이 아니다. 실제 설치/Git 관측의 source_commit은 HEAD 또는 null/사유이며 연구 snapshot·미커밋 bytes의 커밋 반영 인증이 아니다. 전체 installation_files 해시와 기존 _installation_manifest의 code/역할 문서 polling_edition을 같은 모집단으로 비교하지 않는다.

_run_executor는 기동 관문 뒤 _apply_inbox→_recover_disappeared→_upkeep→_prepare_executor_pass→_run_parallel 순서다. 이전 owner의 running을 복구하기 전에 예약 검토를 열지 않는다. CoreEngineMixin._upkeep(*,schedule_reviews=True)는 기존 upkeep 중 _schedule_operational_reviews만 선택적으로 억제한다. ResearchEngine.process_controls는 생존 복구를 하지 않으므로 schedule_reviews=False로 호출한다. 실제 수락 continue가 만든 operational_continuation.next_review는 running·기한이상·tracker없음·미dispatch일 때만 fallback queue를 만들며 stopping/ended의 원예약은 보존한다. tracker explicit/periodic은 기존 caught-up tick 경계이고 임대는 처리UTC의 expiry>now를 유지한다.

scheduled_operator.execute(action,repository,instance,workspace,*,ports,environment,host_id,codex_home,installation_root=SKILL_ROOT,bootstrap_evidence=None,probe=False)는 operator/startup.json을 동작 전에 쓰고 check/wake/run-engine 결과에 startup을 붙인다. main과 직접 CLI check/probe/wake/engine이 같은 함수로 연결된다. run_engine(...,installation_manifest=None)은 명시 manifest 또는 동결 runtime의 manifest를 검증·root대조 후 live child 명령의 --installation-manifest로 전달한다. 운영자 기동의 차이 표시는 수리를 허용하며 엔진 배정 관문과 책임이 다르다. 기존 수리 schema/owner·HOLD·lock/예약·provider 원결과는 불변이다.

직접 근거는 tests/flows/test_observation_application.py:OperationalReviewTriggerTests, tests/sim/test_lifecycle_engine_public.py:PublicControlBoundaryTests, tests/sim/test_planning_document_context.py:InstallationEditionTests, tests/sim/test_operator_supervision_contract.py:SupervisionContractTests와 tests/unit/test_engine_cli_contract.py:RequestModeTests다. 제출판의 마지막3passed와 앞 별도판본 통과·소프트 비용은 managers/0040/verification-review.json을 따른다.

keep-evidence는 tests/support/lean.py:LeanDouble.allow/FakeLean.wait의 정확 입력과 synthetic facts, trust_inputs.trust_fixture의 실제 formal.py checker, fakes.host/clock/jobs의 외부 경계와 contracts.test_doubles_follow_corpus/test_port_clock/test_port_jobs를 소비한다. keep-templates의 Sim/drive·공개 활성화와 r03의 setup producer 근거는 수용판에서 읽으며, 진행 중 keep-inputs/keep-storage의 모델 원문/저장 helper·test_knowledge_formal_engine은 읽기 전용이다. 인터페이스 변경은 실제 공백을 확인한 뒤 task가 필요한 수리를 맡고 report로 연결한다.

## 0041 수용: 역할 원문 반려와 목표감사 대역의 근거

tests/support/role_answers.py:read_fixture_context(prompt, workspace)는 top-level source_ref가 dict이면 path 유무와 관계없이 context_store.read_source에 전달한다. read(reference)는 필수 bytes 값을 사용한 limit=max(1, reference['bytes'])로 원bytes를 요청해 status='ok'이면서 truncated가 아닐 때만 JSON과 json_pointer를 소비한다. 실제 reader의 missing/size/hash/path 오류는 원 결과를 포함한 AssertionError로 드러난다. tasks의 source_ref와 results/reviews/revision_history/assessment_history_source도 같은 read를 사용한다. JSON pointer의 이번 직접 근거는 중첩 객체·배열 인덱스이며 새 범용 pointer codec을 구현한 것이 아니다.

tests/support/purpose_answers.py:PurposeAnswers.answer의 goal_audit 분기는 nonempty eligible_knowledge, 각 항목의 nonempty links/identity_assessments, 평가 id 집합과 link.assessment_id 집합 일치 및 모든 decision=match를 요구한다. 근거가 없으면 기존 두 AssertionError 메시지로 반려한다. PurposeResponder.respond의 failures와 engine_purpose.drive는 만족한 종료 predicate보다 먼저 그 오류를 드러낸다. 효과/현재성·유효 link 선택은 실제 제품 knowledge_records.usable_links와 context producer의 책임이고 대역에 복제하지 않는다. 실제 중앙 형식검사·봉인 평가로 만든 정상 입력과 지정 필드만 훼손한 음성을 함께 확인했다.

tests/support/model.py:ModelDouble.output은 (output, Answer)를 반환하며 render는 binding→선택 after_binding→seal을 사용한다. FakeCLI.finish는 bound일 때 실제 workspace submission_tool/ControlTransport를 통해 정확 expected_receipt를 비교한 뒤 returncode/출력을 적용한다. standalone은 명시 계약이고 호출별 Answer가 서로 섞이지 않는다. model 자체에는 schema 중복 검사를 두지 않는다. tests/support/engine_flow.py:record_submissions는 receipt_received에서 설치된 input/submission/schema.json의 원bytes를 기록한다. PublicGitFlow의 기존 공개 여정은 그 bytes와 immutable input_bundle/issued schema, read_sealed_submission의 실제 receiver input_hashes.schema/context 및 후보 grant/profile을 대조한다.

K-46의 Overlap/InvestigationRunner/RejectingResponder/quota와 K-48의 role_reach는 수용된 현재 정의·원보고의 지정 row 범위로 재사용한다. role_reach의 held 비어 있지 않음과 reached=[]는 둘 다 필요하며 실제 child read-tool 검사와 외부 모델/Job 대역은 다른 근거다. 새 native 호출이나 별도 판본 성공의 합산은 없다. 정확 좌표는 tasks/keep-inputs/evidence/judgment-matrix.json과 managers/0041/source-review.json에 있다.

keep-contracts는 0044에서 부분 수용됐다. support.smell_rules의 구문상 신호와 정확 reason/한 성질의 의미 판정을 구별하고 정본 fixture/현행 model 상수·공통 port 계약의 소유 관계를 확인했다. 실제 observe 변경과 K-71 후속 범위는 아래 0044 절을 따른다. 기존 task의 읽기 전용 범위를 새 후속 task에 자동 적용하지 않으며 keep-rejections는 지정 공통 Git 계약과 소비자의 단언만 수정한다.

## 0042 수용: 저장 원문·검토 결말·게시 후 stop과 후속 범위

tests/support/review_inputs.py:reviewed_candidate(root,verified=False)의 반환(instance,runtime,kid,aid)은 같다. 실제 순수 review_cycle 생산의 status/decision이 verified=True이면 completed/match, False이면 unresolved/unresolved여야 하며 identity_assessment.decision도 같은 decision이어야 한다. 다르면 AssertionError다. 저장 caller인 test_producer_record_storage.KnowledgeRecordTests의 두 시험은 저장 직전 이 독립 결말을 명시하고 기존 실제 Repository의 참조/봉인/환경 연속성 검사를 유지한다. 공개 수송/입장 성공을 순수 fixture의 결말만으로 인증하지 않는다.

test_knowledge_formal_engine.FormalBindingConnections의 source/result 시험은 실제 formal_steps에 지급한 독립 SOURCE 문자열과 산출 proposal.lean bytes/SHA를 비교한다. 같은 head의 result artifact를 독립 compiler 결과와 비교하고 Sim.restart 뒤 원 head를 load해 result_ref·결과 원bytes·source 원bytes를 다시 확인한다. ResearchRepository/StateContract는 실제이고 Git·Lean/실행 일정은 해당 포트 대역이다. 새 native Lean/Git 성공은 아니다.

tests/unit/test_engine_storage_publication.py:PublicationStopTests는 support.storage_records.engine_on/record_store에서 실제 ResearchEngine/Repository를 만들고 fake_ports.calls.new를 쓴다. DeterministicCalls는 ModelCalls를 상속하며 start_call/_judge/judge/collect는 제품 구현이고 _spawn/wait의 일정이 대역이다. 시험 predicate는 owner의 engine.head와 store.load의 head, 메모리/저장의 status를 관찰한다. CoreEngineMixin._save/_reload는 저장/로드 반환의 head·두 root를 먼저 채택한 후 _evaluate_stops를 실행한다. paused 게시 뒤 stop Event, 계산의 stopped 반환, collect 후 빈 futures와 이전 initializing snapshot을 단언한다. artifact 없는 실제 no-op은 추가 판단을 만들지 않는다. 임의 off-thread 저장의 동적 거부나 개별 모든 stop 정책을 새 계약으로 추가하지 않았다.

Repository.published_state는 전체 검증 views를 반환하고 eviction이면 None이다. _unchanged는 그 경우 False, 그 외 updated_at을 제외한 runtime와 전체 instance를 same_json_value로 비교한다. Unicode 및 bool/int 구별, 실제 저장 검증/reader·봉인/구조공유 state/10은 기존 정의와 한정 원보고로 유지한다. 전체 schema 필드의 역방향이 확인된 관찰4가족과 이름 사용/보이는 event keyword를 보는 StorageFieldTests의 범위를 구별한다.

storage-knowledge는 tasks/keep-storage/evidence/families.json의 trust4/knowledge5/snapshots4를 현재 provider→실제 검증 receiver에 연결한다. 기존 Pair의 fields는 required+optional이며 samples는 실제 생산값, receive는 실제 checker, written은 해당 shape의 실제 작성 필드다. 저장13가족 모두에 동일 Pair 형식을 강제하지 않으며 metadata/list/scalar의 정본 의미를 따른다. 같은 helper 수리를 한 task가 소유하고 진행 중 trust_inputs/state_builders/review_scene/Lean 및 role_answers/규칙은 읽기 전용이다. 나머지71가족과 fresh T3의 실제 쓰기분기 도달은 별도 남김이다.

keep-proof의 읽기 배정은0045에서 무변경 수용됐다. 수용된 네 task 원보고와 legacy mutation-baseline의 실제 red/child/정상 기준, 현행 run_tests 및 support.mutation의 validate_result/run/passed를 연결했다. K-70/76/77 지정질문과 K-73의 남은 수리 무력화 확인은 아래0045절을 따른다. 과거 극단 변이·수리 전 실패·특정 수리 무력화는 서로 다른 근거이며 미수용 작업판에 의존하지 않는다.

## 0043 수용: 합성 증거 소비와 설정·프로필 저장 후속

제품/fixture 인터페이스 변경은 없다. tests/support/lean.py:LeanDouble.allow(source,declarations,*,signatures,declaration_evidence,axioms,dependencies)는 실제 lean_evidence.check_file의 정확 UTF-8 bytes·순서 있는 선언·extract 여부로 표를 등록한다. 표의 키 전건성과 공유 상수 충돌을 검사하며 preview-only는 extraction 등록을 지운다. FakeLean.wait는 실제 파일 원bytes로 조회하고 미등록이면 exit1·정확 미등록 사유를 낸다. 출력은 별도 실제 parse_evidence의 signature/공리/전체증거 검사를 소비한다. 새 LeanDoubleOutputTests 두 메서드가 선언 역순/부분목록·개행/문자 정규화 변경의 반려와 입력/반환 격리·빈 signature 반려를 고정했다.

tests/unit/test_synthetic_evidence.py:SyntheticEvidenceTests는 Sim.activated의 실제 capability_evidence scope, initial_governance 승인 원문/SHA, 채택 charter evidence_boundary와 repository 재적재를 확인한다. trust_fixture는 현재 formal.__file__ 경로/SHA로 toolchain을 만들고 실제 trust_inventory record/binding·formal.verify_lean을 소비한다. 정상 launch_not_created=False는 외부 Jobs 포트의 논리 FakeJob이 시작됐다는 뜻이며 Lean check에는 synthetic=true가 남는다. checker SHA/합성 executable 변경 뒤에는 실제 identity 반려와 추가 Job/Lean 호출0을 검사한다. native Lean/host 검증을 뜻하는 표지는 없다.

ReviewScene.execute(changes=None,record_first=False)는 실제 _admit_review_execution이 admitted인 경우 _apply_identity_review를 거친 뒤 ended/output_accepted를 기록하고 (context,output,execution_id)를 반환한다. 거부는 그 disposition의 ValueError를 전파한다. 새 직접시험은 실제 입장으로 한도를 소비하고 거부된 시도에 output/outcome과 새 cycle result가 없음을 확인했다. start의 이미 정한 scope와 모델/제출 생략은 검토 mixin의 layer2 입력 경계다. 전체 scope/owner/worker/제출·프로세스 종료는 기존 직접 caller와 수용된 keep-templates/r15-r16/keep-isolation의 별도 근거를 따른다.

storage-profiles의 대상은 research.config/capacity_constraints/execution_profiles/host_capacity_ref/role_profile_refs와 runtime.reservations다. execution_profiles.build_profiles(config,host=...)는 프로필/제약/선택참조/host참조를 생산하고 apply_editions가 기존 instance에 채택한다. host_constraint/with_host_resources는 authority·scope·한도/요구를 연결한다. SessionSlots._admission은 정본 profile/ref와 채택된 현재 한도를 대조하고 plan_reservations의 후보를 반환하며 acquire는 실제 execution/capacity/launch_ticket 및 예약을 게시한다. 단순 admission_check 성공은 예약 게시가 아니다. 실제 StateContract 가족별 checker/validator와 Repository 검증/재적재가 수신 경계다.

기존 test_producer_record_storage의 host/profile/reservation/configure 단언을 재사용하고 필요한 필드·생산분기 보완은 새 전용 helper/계약시험에 모을 수 있다. scalar host참조·역할별 참조목록·config singleton과 map record를 구별한다. 일반 Pair의 samples/receive/fields/written은 재사용 가능한 시험 인터페이스이며 새 registry를 요구하지 않는다. 중앙 schema·일반 PAIRS·공용producer시험·storage_records는 실행 중 storage-knowledge가 소유하므로 시작판만 읽는다. 실제 범위 밖 결함은 반례와 필요한 경로로 report에 인계한다. 양방향 필드 근거와 모든 쓰기분기의 최종 fresh T3 측정은 다른 완료 증거다.

## 0044 수용: 관찰 입력 시계와 정확 반려 단언 후속

support.observation_inputs.observe(tracker,event,**options)는 이전 observation_source.end_offset 또는0을 시작점으로 한 stdout.jsonl의 다음 한 바이트 좌표를 구성하고 tracker.observe에 넘긴다. received_at은 tracker.time_port.now(), received_monotonic은 같은 포트의 tracker.clock()이다. 실제 ObservationTracker._snapshot은 수신 UTC를 wall_time_reached 판정에, observe는 explicit review의 at 비교에 쓴다. 처리 시각을 남기는 record 필드와 수신 시각은 별개다. 이 helper는 주입 시계에서 새 수신을 만드는 입력이며 서로 다른 수신/처리 시각의 ObservationBatch 재생을 대체하지 않는다. 반환은 실제 tracker의 발동 record 목록 그대로다.

새 unit.test_fixture_contracts.ObservationFixtureTests는 경계 전 []와 경계 도달 self_check_due/explicit_review_due, source 좌표0→1→2·단조1000→1002·snapshot UTC·opened/deadline2000/7000ms를 확인한다. 기존 unit.test_observation_tracker54개와 함께55passed가 제출판 근거다. smell_rules.no_assertion/unpinned_rejection은 호출 존재/예외 접근을 찾는 구문 신호이며 의미 있는 성질·정확 사유를 자동 증명하지 않는다. 해당 함수 동작은 변경하지 않았다.

keep-rejections가 소비할 F2의 실제 경계는 supervision.repair_report_schema(diagnosed=...)와 jsonschema.validate다. diagnosed 두 값에서 installation_version/source_commit을 각각 제거하며 required validator·루트 path·같은 누락 필드 사유를 확인한다. F3의 두 backend.project_snapshot(project_root,repository_root)는 repository_root=None이면 빈 ProjectSnapshot, 명시 root 밖이면 Path.relative_to에서 ValueError다. F4의 FakeGitBackend.ref_oid는 손상 REF를 'broken reference: '+ref로 거부하고 GitProcessBackend.ref_oid는 rev-parse --verify --quiet ref의 nonzero/stderr를 _fail의 GitBackendError로 전달한다. 실제 absent ref의1/no-stderr는 None이며 유효 OID/없는 object는 별도 정상 입력이다. 오류 표현 차이를 지우지 않고 각 실제 사유를 같은 입력에 결박한다.

공통 assertion의 owner는 tests/support/port_contracts/git_backend.py:GitBackendContract다. 실제 소비는 contracts.test_port_git_backend의 FakeGitBackendContract/FakeSha256GitBackendContract와 boundary.test_port_git_backend의 GitProcessBackendContract/GitProcessSha256BackendContract다. 두 메서드의 네 inherited ID와 단위 메서드 하나가 기본 최소 확인 범위다. 필요한 양측 assertion 준비는 직접 소비 파일에 두고 제품/fake backend/포트 API·smell 검사기는 읽기 전용으로 유지한다. native Git은 자기 임시 fixture에서만 확인한다. runtime API 변경이나 전체 T4 인증이 아니다.

## 0045 수용: 변이 정상 기준과 증거 판본, 한정 probe 후속

제품 API 변경은 없다. scripts/tests/support/mutation.py:run(base,index,layers,root,directory,*,only=(),every=False,listing_path=...)의 내부 baseline(chosen)은 tests/folders/exclude 선택을 키로 같은 run 안에서만 정상 기준을 재사용한다. 실제 _child_run에 target=None·mutant=None을 주고 attempt의 error 또는 _evidence_error(result), normal load_error를 검사한다. 정상 rows의 실패를 failing으로 보존하고 status는 evidence_error/failing/passed로 나눈다. 결과 부재를 passed로 취급하지 않는다. mutant failing ID마다 해당 정상 기준이 passed여야 killer이고 정상 evidence_error는 outcome.execution_error로 이어진다. load_error 변이도 같은 batch의 실제 정상 통과가 필요하다. elapsed는 포착 근거가 아니다.

같은 파일 validate_result는 수집/선택/rows/tests_run/load_error의 증거 모양을 검사하며 실제 child와 부모가 함께 소비한다. passed(report)는 unreasoned_entries·baseline_failing 및 execution_error/mutation_error/not_executed/baseline_failing counts가 없어야 true다. CLI main과 scripts/run_tests.py:_finish_t3가 이 판정을 소비한다. 각 attempt의 실제 exit·spec/result/output 및 baseline ID는 report의 근거다. legacy child19표본과 최종58passed의 mutation.py/unit.test_mutation.py/boundary.test_mutation_baseline.py SHA가 현재와 같다는 사실은 이 하위 성질의 재사용 근거이며 현재 전체 T3/변이 성공은 아니다.

scripts/tests/boundary/test_mutation_baseline.py:ActualBaselineTests._run_fixture는 value()==2인 정상 child를 exit17로 끝내 결과 부재를 만들고, value 반환을 None으로 바꾼 mutant의 실제 실패와 대조한다. test_missing_normal_child_result_never_certifies_a_kill은 killed 아님·passed=False·baseline evidence_error·exit17/result=None/FileNotFoundError·baseline ID 연결을 단언한다. test_actual_normal_pass_certifies_the_mutant_failure는 일반/하위단언 정상 passed가 실제 killed를 인증하는 대조다. _run_fixture는 실제 repository_root/Git blob/HEAD와 그 저장소 아래 scratch를 필요로 한다.

proof-baseline은 별도 정상/프로브 사본에서 위 두 ID를 그대로 소비하고 baseline의 부재/child 오류 분류 한 곳만 무력화한다. 기대값·실제 child·다른 검사와 raw 오류는 유지한다. 실험 사본의 의도한 diff이며 제출 제품 writes=[]다. 공용소스를 임시 Git root로 쓰지 않고 필요하면 자기 폐기용 fixture의 최소 HEAD를 구성한다. 자료 읽기/사본 준비는 즉시 가능하지만 기존 storage-knowledge/storage-profiles/keep-rejections 중 첫 exited 관측 뒤 예약된 시험 슬롯을 쓴다. 다음 manager도 그 슬롯을 proof-baseline 종료 전 다른 신규 시험task에 중복 배정하지 않는다.

현재 run_tests._edition/main은 scripts 아래 Python의 실행 전후 SHA를 비교하고 changed_during_run이면 성공을 거부한다. 비빈 output 재사용은 exit2, TimedResult._outcome의 최초 실패 중간보고는 complete=false다. 최종 selected/actual rows/counts/fixture_counts/complete/successful/exit를 함께 읽는다. 이것은 문서까지의 물리적 잠금이나 모든 기록 작성자의 준수 인증이 아니다. keep-proof가 확인한 storage/격리 교정은 각각 시험1파일이 다른 판본이며 최초 실패와 교정성공을 별도로 보존한다. 정확 원자료와 한계는 tasks/keep-proof/evidence/judgment.md 및 managers/0045/verification-review.json에 있다.

## 0046 수용: 실제 프로필 저장과 반려 원인, 실행 가족 후속

tests/support/storage_profile_pairs.py:profile_cases(root)는 네 독립 patch로 공개 engine.initialize→ResearchRepository.initialize/load를 거친 ProfileCase(name,patch,instance,runtime,store,head,inputs) 목록을 반환한다. Git/host/clock/Jobs는 포트 대역이고 초기화·프로필생산·저장은 실제다. family_receiver(family)는 설치된 checker.iter_errors와 validator를 소비하고 오류면 ValueError를 낸다. profile_pairs(cases)는 config/execution_profiles/capacity_constraints/role_profile_refs의 실제 저장 표본과 전체schema.properties를 기존 Pair에 연결한다. host_capacity_ref의scalar와 reservations는 자기 shape로 확인한다. 중앙PAIRS/schema/API 변경은 없다.

같은 helper의 acquire_roles(root,case,roles)는 실제 activity/execution 생성·SessionSlots.admission_check/acquire·save를 거쳐(store,slots,head,instance,runtime)를 반환한다. acquire_profile(slots,instance,runtime,reference,*,index)는 등록된 특정판본에 입장하며 확인 중runtime불변/실제acquire성공을 요구한다. 계약시험은0/1/3/4/7예약과 정산 row·reobserve제거·옛head, configure 뒤 옛profile/window와 현재capacity의 실제 재입장을 단언한다. SessionSlots._admission의 현재한도회계와 profile권한, admission_check와 실제게시의 차이를 보존한다. 실제native종료/원격사용 인증은 아니다.

keep-rejections 수용 뒤 unit.test_operator_rules의 해당 메서드는 ValidationError.validator=='required', absolute_path==[], 같은 누락필드 message를 함께 확인한다. GitBackendContract는 outside/repository 경로를 repr 그대로 relative_to 진단에 결박한다. broken_ref_message는 FakeGitBackendContract의'broken reference: {ref}'와 GitProcessBackendContract의'rev-parse --verify --quiet' 실패/broken-ref경고로 각 측이 선언한다. 공통시험은 두malformed raw와같은REF를 써 네SHA1/SHA256소비자에서 직접 비교하며 정상 absent/없는object 대조를 유지한다. 현재 Python/Git 진단 표현 변경 시 해당 측 기대값의 검토가 필요하다.

storage-execution은 runtime.activities/executions/provider_waits/provider_wake를 현재 계약으로 읽고 실제생산→검증저장/재적재의 필드 역방향을 보완한다. activities와 execution_lifecycle의 수명, SessionSlots.provider_result_from_run/acquire/release의 provider gate, scheduler.SchedulerMixin._schedule_provider_wake→scheduled_operator.reconcile_wake 반환이 제공 경계다. provider_wake는 observed를 뺀 singleton이고 열린 EVIDENCE 계약의 필드명면제와 실제내용보존을 구별한다. scheduler포트대역만 쓰며 OS예약변경은 하지 않는다. 전용storage_execution_pairs/계약시험과 해당제공자/직접시험이 소유범위이며 중앙schema/일반PAIRS/공용storage_records·producer시험은 storage-knowledge 소유로 읽기만 한다. tasks/queue 전체 역방향은 남기고 reservations는 수용근거를 재사용한다. 상세는 tasks/storage-execution/objective.md다.

## 0047 수용: 저장 필드 역방향·전이 기초·baseline 반례와 다음 소유

0047 당시 배정은 storage-execution과 storage-authority였으며, 현재 배정과 수용 경계는 아래0049절을 따른다. 이전0042~0046절에서 실행 중으로 쓴 storage-knowledge/proof-baseline은 수용됐으며 proof 시험예약은 해제됐다. 기존 storage-execution의 시작판/정의는 바뀌지 않는다. 중앙schema의 새수리는 storage-authority가 대상8가족 범위에서 맡고, 진행 중 실행제공자 및 그 전용시험은 읽기 전용이다.

contracts/pairs.py:assert_pair(case,pair,samples)는 비빈 실제 생산표본을 각각 deepcopy해 pair.receive에 전달한다. ValueError 반려목록은 AssertionError가 되고 그밖의 예외는 전파된다. pair.fields가 None이 아니면 전체 required+optional 필드 집합에서 실제 pair.written의 합집합을 빼 남은 필드가 없어야 한다. 반환값은 없고 같은 함수가 기존 ContractPairTests와 새 KnowledgeFieldPairs를 검사한다. 기존 일반pair의 특정 관찰/setup 원bytes 추가단언은 ContractPairTests.assert_pair에 유지된다.

support/storage_knowledge_pairs.py:family_pair(store,root,family,samples,contract=None)는 실제 저장/load된 (instance,runtime)를 소비한다. map record는 schema.properties와 각 row키, singleton map은 schema.additionalProperties.properties와 각 item키, metadata는 /value 슬롯을 사용한다. receive는 설치 family checker와 validator를 실행하며 지원하지 않는 shape는 ValueError다. 이 함수는 임의 list/모든singleton에 통용되는 범용 shape 추론기가 아니다. 전체 관계/봉인 검증은 각 sample의 실제 Repository 게시/load에서 이미 수행하며 가족별 순회에서 전체 상태 검증을 중복하지 않는다.

record_schemas.schemas.RECORDS의 knowledge/formal_results/expositions/identity_assessments/assessment_uses/review_cycles는 생산자없는 optional27개를 제거했다. COMMON 일괄필드는 없고 실제 provenance/봉인/관계/환경/현재성 필드는 개별정의에 유지한다. review cycle은 producer_execution_ids를 쓴다. 삭제된 이름을 저장하면 닫힌schema의 additional properties 오류이며 구판변환은 없다. 목록·생산/수신 좌표는 tasks/storage-knowledge/evidence/families.json, 실제정본 설명은 scripts/이음새-정본.md 8절이다.

knowledge.begin_transition의 targets[].basis.sha256와 activate_transition의 현재기초 비교는 기존 basis_record를 해시한다. formal_engine._trust_check_steps/review_cycle.staged_review_candidate의 validate_basis와 같은 정본이며 basis_record 자체는 불변이다. 지식의 검토일정포인터를 제외하되 authored 제목/수명/참조/내용/provenance는 보존하고 formal/exposition의 별도봉인기초를 검사한다. reviewed→staged→activation 저장과 제목변경 반려를 확인했다. target/result/권한·환경검사와 반환형식은 유지된다.

proof-baseline은 제품API를 바꾸지 않았다. support.mutation.run의 정상baseline은 actual child오류/result부재를 evidence_error로, 해당 변이결과를 execution_error로 보존한다. 별도probe는 이 status 식만 passed로 바꿔 기존 ActualBaselineTests.test_missing_normal_child_result_never_certifies_a_kill의 assertNotEqual에서 정확 killed==killed 실패를 냈다. 정상대조ID와 일반/subTest 두fixture는 보존됐다. 상세 원spec/child결과/부재·exit·판본은 tasks/proof-baseline/evidence/verification.json과 normal/probe 아래에 있다. 현재 수리 한건의 반례이며 전체변이/최종판을 뜻하지 않는다.

storage-authority의 제공자는 governance.preserve_source/initialize_governance/_install_record/normalized_grant/apply_decision와 knowledge_io.ensure_ontology/register_kind_definition/check_kind_definition/activate_kind_definition/withdraw_kind_definition/import_relation이다. 소비자는 record_schemas.install이 등록한 각shape/checker/validator/references 및 실제 Repository 저장/load다. governance_approval은 singleton 등록의boolean/object값, relations는list item, 나머지는map record이며 빈properties를 역방향성공으로 쓰지 않는다. 새 전용 storage_authority_pairs/계약시험은 위 assert_pair를 재사용하고 실제 승인원문/SHA·권한/철회·관계endpoint/증거를 보존한다. schema/같은checker수리·관련회귀·미러를 한task가 맡는다. 선행은 storage-knowledge뿐이며 상세범위는 tasks/storage-authority/objective.md다.

## 0048 수용: 실제 실행 저장 표본과 남은 필드·메타데이터 경계

0048 당시 storage-execution은 부분 수용, storage-authority는 기존 배정 유지였다. 현재 authority 수용과 후속 경계는 아래0049절을 따른다. execution-fields는 두 결과를 소비해 실행 한 가족을 마무리하고 storage-metadata는 독립 다섯 연구 메타데이터를 맡는다. 후속 제품 쓰기/선행은 각 objective와 queue가 정하며 실행 중 정의를 바꾸지 않는다.

tests/support/storage_execution_pairs.py:execution_scene(root, case)는 storage_profile_pairs.profile_cases가 공개 initialize로 저장한 입력을 실제 engine_on/record_store에 넘긴다. 장면마다 FakeClock/Calls/Jobs/scheduler 이력은 분리하며 저장·engine·StateContract는 실제다. ExecutionScene.publish(branch)는 engine._save 뒤 새 Repository로 같은 head를 load하고 (branch, head, deepcopy(runtime)) 표본을 보존한다. new_attempt는 실제 create_execution/assign_execution을 쓰며 native process를 시작하지 않는다.

stored_pair(family_name, snapshots)는 activities/provider_waits 같은 닫힌 map row의 schema.properties 전체와 실제 저장 표본을 Pair/family_receiver로 연결한다. provider_wake는 열린 singleton이므로 같은 객체 field walk를 강제하지 않고 실제 reconcile 결과 dict·marker·포트 순서·오류 내용을 직접 단언한다. executions102필드 후보 표도 실제 생산/저장 인증이 아니다. 전용 StorageExecutionPairTests.assert_pair는 시작판 당시의 로컬 구현이며, 후속 execution-fields가0047의 contracts.pairs.assert_pair로 연결한다. 내용/정확 반려 단언은 유지한다.

provider_result_from_run은 admitted capacity.provider와 failure.provider를 대조하고, checking은 정확 probe_owner만 해소한다. local release만으로 available을 인증하지 않으며 응답 관측 뒤 available은 연구 성공/원격 종료와 다른 뜻이다. retry/generation/attempts·원실패 reported_fields_json은 저장한다. scheduler._schedule_provider_wake는 reconcile_wake 반환에서 observed를 제거한 값을 저장하며 status/schedule/cancel 포트 오류의 원문은 failed/error로 보존된다.

0048 당시 RECORDS['executions']는 required8+optional94를 허용했다. 현재0052 수용판은 아래 절의 required8+optional84를 따른다. 최상위 pid/conversation_id/finished_at의 생산자가 확인되지 않았고 governance.validate_independent_execution은 conversation_id/provider_session_id를 읽는다. launch/capacity.process 신원, continuation_of 계보와 ended_at의 현재 생산·소비 정본을 함께 검토해야 한다. execution-fields는 storage-authority가 수용될 governance/schema 판본을 입력으로 이 관계와 남은 필드·수신·저장·직접시험을 함께 맞춘다. 필드 복사/자동 구판변환/독립성 검사 약화는 승인된 해결책이 아니다.

독립 storage-metadata의 제공자는 initialization.initialize_state(instance_id, goal, workspace, config, source_input, title, created_at, clock, host)와 ResearchRepository._save의 실제 object_format 설정이다. title은 명시값 또는 goal[:80], created_at은 명시값/주입clock의 timestamp 정규화이며 Repository는 Git 형식 불일치를 거절한다. 수신자는 StateContract에 metadata로 등록된 research.id/object_format/title/workspace/created_at 및 repository._encode_families/_decode_families다. root metadata 포장과 scalar /value 검사를 구별하고 원값·정확 반려·별도 load를 확인한다. 중앙schema/권한/실행 제공자는 읽기 전용이며 initialization/repository/state_contract와 직접 저장시험만 쓴다. runtime 상태·시각 및 다른 연구 메타데이터는 이 다섯 가족의 결론에 포함하지 않는다.

## 0049 수용: 권한·온톨로지 필드 계약과 목표·학술 후속

0049 당시 storage-authority는 수용됐고 기존 execution-fields의 선행이 충족됐다. storage-metadata의 후속 수용과 신규 경계는0050절을 따른다. storage-academic은 execution-fields가 제공할 실행 독립성/중앙schema 수용판을 소비하며 metadata는 선행이 아니다. 실제 쓰기 범위는 각 objective와 queue가 정한다.

tests/support/storage_authority_pairs.py:authority_samples(root)/ontology_samples(root)는 (branch,(instance,runtime)) 표본을 반환한다. _keep는 실제 Repository initialize/save_with_state/load 뒤 생산값 전체와 재적재값을 비교하고 이전 head의 내용을 다시 읽어 불변을 확인한다. 승인·종류·관계 생산은 실제 domain/API이고 Git/clock/host/compiler 관측만 기존 대역이다. 관계 검토의 scope/initial 답은 합성 입력이며 실제 모델 호출은 아니다.

family_pair(store,family,samples,contract=None)는 설치된 research 가족 checker/validator를 소비하는 Pair다. map은 각 record, list는 각 item을 검사한다. governance_approval의 boolean/object singleton은 /value 슬롯을 쓰며 실제 표본은 초기 부재/무권한과 정확 승인 object다. _named_fields는 닫힌 중첩 object/list item의 이름도 역방향에 넣고 열린 evidence/map의 내용은 독립 값 보존 단언으로 확인한다. schema 필드에서 실제 표본에 없는 필드가 남으면 공통 contracts.pairs.assert_pair가 실패한다. 지원하지 않는 shape는 ValueError다. 전체 관계/봉인은 각 실제 저장 경계에서 검사된다.

RECORDS['decisions']는 coverage/intent_check/author_execution_ids, kind_definitions는 history/checks/activation, relations는 lifecycle/created_at/actor_ref/origin_refs/source_basis를 허용하지 않는다. 현재 미생산 optional은11개다. 0049에서 함께 제거했던 kind_definitions.check는 실제 CoreEngineMixin._apply_kind_definition_check가 생산하므로0058에서 EVIDENCE로 복원했다. check는 원 definition_id/definition_sha256/decision/findings와 execution_id를 보존한다. check_ref/checked_by/approval_ref/activated_by와 관계 imported_at/imported_by/source_ref, history/use_history·formal_result_refs/assessment_refs는 유지한다. 기존 ontology 표본/제거 단언은 이 복원을 아직 반영하지 못해 storage-ontology-fix에서 수리한다. 과거 tasks/storage-authority/evidence/families.json의12개 제거 판정은 당시 근거로 보존하며 현행 계약은0058절과 scripts/이음새-정본.md를 따른다.

후속 storage-academic의 제공 경계는 GovernanceEngineMixin._apply_governance_goal_audit와 academic.apply_goal_assurance/current_solution_basis, AcademicEngineMixin._record_academic_assessment/_academic_control/_apply_academic_resolutions, academic.assess/record_resolution/unresolved_rejections다. 목표 judgment는 list item이며 goal_assessment_basis는 현재 TEXT singleton, goal_status는 metadata다. academic_assessments는 ID 없는 닫힌 item list를 담는 typed singleton이며 external_rejections/academic_resolution_records는 list item이다. 현재 shape를 빈 properties 성공으로 오해하지 않는다.

목표판정은 같은 basis의 완전한 독립 슬롯/실행·formal evidence·현재성을 소비한다. 학술평가는 실제 적용된 TASKS 평가·solution/requirements 해시·criterion·외부효과 receipt를 소비한다. 외부반려의 원 actor/text/source/time/solution은 불변이며 해소는 별도 ledger의 rejection/evidence hash·지정planner input_solution_basis에 봉인된다. academic.stored_evidence는 해당 head에서 빠진 ref에 None을 반환하며 미해소 의미를 보존한다. 이 여섯 가족의 실제 저장/필드 대응과 수리를 한 task에서 마치고 실행·권한/관계 가족의 기존 성질과 다른42가족은 구별한다. 전 쓰기분기의 fresh T3 증거는 별도 남김이다.

## 0050 수용: 초기화 scalar 저장과 수명 메타데이터 후속

storage-metadata는 수용됐다. 제공자는 initialization.initialize_state(instance_id, goal, workspace, config, source_input, title, created_at, clock, host)이며 id/title/workspace/created_at을 작성한다. title은 명시값 또는 goal[:80], workspace는 str(input), created_at은 timestamp로 정규화한 명시값/clock.now다. object_format의 현재 정본은 ResearchRepository.validate_candidate이며 GitStateStore.object_format을 넣고 명시 불일치를 게시 전에 반려한다.0048/원objective의 역사적 _save 지칭은 이 현재 심볼과 save_with_state로 읽는다.

record_schemas.install은 research의 다섯 필드를 identity=False인 metadata로 등록한다. _encode_families는 root당 _state/metadata.json의 record에 원값을 모으고 manifest.containers에 각 shape=metadata를 둔다. _decode_families는 포장/선언 membership·shape·Git 형식을 검사하며 StateContract.validate/validate_record가 각 scalar checker를 실행한다. 개념상 /value는 필드 역방향의 값 단위이고 실제 pointer는 research/_state/metadata.json#/record/<name>이다. 새 저장 wrapper/registry는 없다.

tests/unit/test_record_family_storage.py:FamilyRecordStorageTests.test_scalar_metadata_is_one_closed_record_per_root는 실제 초기화 두 입력을 SHA1/SHA256 저장소에 게시한다. 새 installed_contract 객체를 받은 별도 reader의 첫 load는 기존 validated-read cache와 구별되어 Git bytes decode/전체검증을 실행한다. 독립 title/80codepoint fallback·정확 Unicode/개행·Path/raw workspace·UTC와 microseconds·caller ID를 저장값에 연결하고 정상 title 변경 뒤 옛head/원metadata bytes를 보존한다. 숫자17의 각 scalar 반려·손상 id와 미선언 metadata의 read 반려는 정확 원인을 확인한다. ContractEditionTests.test_storage_object_format_and_contract_versions_are_enforced는 형식 불일치의 정확 사유와 head 불변/write0을 검사한다. 비검증 publish는 손상 반례에만 사용한다.

storage-lifecycle은 runtime.status/cycles/updated_at/recovery_checked/last_observed_utc/resume_lifecycle/stop_requested/next_research_reconsider_at8가족을 소비한다. 생산은 initialize_state와 LifecycleEngineMixin의 활성화/pause/resume/관측·planning의 재고 예약, core_engine._save/_apply다. updated_at은 현재 _save의 clock.now이며 last_observed_utc는 검증 관측과 정상 게시에 따른 high-water다. pause는 원 lifecycle을 resume_lifecycle에 보존하고 stop_requested를 쓰며 resume은 현재 권한/시계/대화 조건을 확인한 뒤 두 marker를 제거한다. recovery_checked는 활성화의 quiescence 결과, cycles는 실제 research 결과 적용의 계수다. 이 설명은 새8가족 전체 검증 완료가 아니며 해당 task가 기존 근거와 보완을 판정한다.

신규 task는 storage-metadata 수용판의 scalar 저장·별도 decode 방법을 입력으로 받고 중앙schema/core/call/session/governance/academic은 읽기 전용이다. lifecycle/planning/초기화/Repository/StateContract와 직접시험의 필요한 수리는 자기 writes에서 마친다. 기존 execution-fields→storage-academic의 실행/목표 판정 계약과 순서는 유지한다. availability/clock_guard/user_pause 객체, event_cursor/events/pending_events와 다른34미배정 가족은 새8가족의 결론에 포함하지 않는다. 전 쓰기분기 fresh T3와 최종 통합판은 별도다.

## 0051 수용: 수명 metadata와 대화·제어 저장 경계

storage-lifecycle은 수용됐다. tests/sim/test_lifecycle_engine_public.py:assert_runtime_metadata(test,engine,expected,absent=(),head=None)는 actual engine publication을 새 installed_contract를 가진 Repository로 읽고 root metadata/manifest·정확 값/type·설치 checker와 지정 부재를 확인한다. head를 주면 옛 publication을 읽는다. _read_key는 contract 객체를 포함하므로 이 reader의 첫 load는 Git bytes decode와 전체검증을 거친다. production API 추가는 없다.

initialize_state의 runtime scalar 초기값, _activate_initialization의 quiescence 결과와 ready/재고시각, _pause_lifecycle/_resume_lifecycle의 원phase·stop marker/제거, core_engine._apply의 일반 research_preparation cycles 증가가 실제 저장과 연결됐다. core_engine._save의 updated_at은 clock.now이며 last_observed_utc는 승인된 anchor high-water다. clock 관측 자체가 publication을 만들지 않으며 회귀 pause에서도 두 시각을 같은 값으로 만들지 않는다. planning.collect_due_events/schedule_reconsideration은 원 만기의 단일 사건과 관측시각+설정 간격의 다음 예약을 생산한다. 외부 OS예약은 다른 경계다.

tests/unit/test_record_family_storage.py의 기존 scalar 시험은8가족 초기값/선택 부재·정확 타입/enum/minimum 반려와 head/write 불변, cycles 손상 read를 확인한다. next_research_reconsider_at의 숫자 반려는 현 nullable anyOf의 원문 오류다. boolean stop_requested와 null deadline의 실제 root producer 미확인, 이번 미실행 enum 생산/예약 분기의 정적·기존 근거 한계와 전쓰기 fresh T3를 남긴다. 원metadata5 단언은 보존됐다.

후속 storage-conversation의 제공자는 lifecycle_engine._conversation_control/_lose_conversation/_check_conversations/_conversation_live/_apply_extended_control/_resume_lifecycle/_activate_initialization/_refresh_readiness와 initialization_engine._initialization_control이다. conversations는 attach/heartbeat가 현세대 lease/source_ref를 기록하고 detach/만기가 lost_at/loss_reason을 추가한다. pause 정책에서 잃은 ID→generation을 lost_conversation_generations에 보존하며 재개는 살아 있는 새 세대를 요구한다. conversation_loss_policy는 명시 adopt/attach의 pause 또는 continue_authorized이고 초기 부재·기존 권한과 구별한다. 공개 lease_seconds는 control_contracts의 양의 정수다.

user_pause는 명시 사용자 pause의 request_id/reason/created_at 객체이며 사용자 resume이 제거한다. 저장 계약의 boolean/object 허용과 실제 작성 형태를 구별한다. availability는 state 필수·reason/next_owner 선택 객체이며 초기화 blocked/user, 활성화 available, 시계 blocked 등의 실제 생산값을 연결한다. core/call 등 다른 writer도 읽되 해당 파일은 기존 실행 task 소유다. metadata 저장 모양과 scalar 타입은 동의어가 아니다. conversations/availability는 전체 닫힌 필드 역방향, lost mapping/open user_pause/scalar policy는 실제 내용·/value 검사를 사용한다. 저장/수신 정본은 record_schemas.install·Repository이고 새 wrapper/registry를 만들지 않는다.

storage-conversation은 storage-lifecycle 수용판만 선행으로 받는다. 기존 execution-fields→storage-academic의 제공자·중앙schema·정본 설명과 공통 pairs는 읽기 전용이다. 새 task와 의미 있는 writes 교집합은 없고 캐시는 관측 보존 뒤 own base로 복원한다. 다른29미배정 가족·clock_guard/research.lifecycle 전체·events/queue와 최종 통합판은 별도 남김이다. 이전0050의 신규/수명task 진행 표현은 당시 이력이며 현재 상태는 이 절과 plan/queue를 따른다.

## 0052 부분 수용: 실행 저장 정본과 남은19필드

현재 record_schemas.schemas.RECORDS['executions']는 required8+optional84=92필드다. pid/conversation_id/finished_at/workspace/parent_execution_id/profile_ref/submission_check/started/currentness/integration_id의10슬롯은 허용하지 않으며 추가 시 runtime/executions/<id>/의 additional-properties 오류로 게시가 반려된다. 종료는 execution_lifecycle.transition_execution의 ended_at, 프로필은 execution_profile_ref, process 신원은 SessionSlots가 작성하는 launch_ticket/capacity.process다. CoreEngineMixin._apply_bundle_candidate의 integration_id는 내부 후보에서만 쓰고 검증/게시 전에 pop하며 실제 참조는 integration_result/result_disposition에 남는다. 구판 보충/변환은 없다.

governance.validate_independent_execution은 checker 부재/작성자 동일성·continuation_of 반복/작성자 도달/미해결을 반려한다. context_origin은 제공 record 계보이며 provider 세션 재개가 아니다. worker_request.codex_argv/claude_argv의 새 exec --ephemeral/--print --no-session-persistence와 폐쇄 요청검사가 실제 입력 경계다. native session ID 원문은 stream에 남고 사용자 연결 임대 runtime.conversations와 구별한다. session별칭 dead read와 core recovery-material의 parent_execution_id 조건은 제거됐으며 formal_check checkpoint 예외는 유지한다.

tests/unit/test_provider_stored_executions.py의 StoredCallEvidenceTests/StoredExecutionTests는 실제 준비/수신·unsealed 반려·maintenance archive·live-review/recovery의 저장값, 원bytes/hash/ref와 별도 Repository load·옛head를 연결한다. tests/unit/test_governance_checker_lineage.py는 실제 stored checker/hash와 두 공급자 worker argv/추가 session 입력 정확 반려를 확인한다. test_storage_execution_pairs.StorageExecutionPairTests.assert_pair는 공통 contracts.pairs.assert_pair를 소비한다. 현재 이 pair의 activity/provider 표본이 executions92필드 전체 역방향을 자동으로 검사하는 것은 아니다.

새 execution-storage가 소비할 실제 남김은 CallEngineMixin._prepare_call의 academic_requirements_sha256/delegation_input_sha256/input_solution_basis/input_basis/observation_rules, GovernanceEngineMixin._bind_governance_input의 additional_audit_input, CallEngineMixin._receive_call의 preserved_reason/failure/error_kind와 usage_segments/model_usage_reported/usage_scope/reported_models다. CoreEngineMixin._apply/_apply_operational_disposition은 output/operational_continuation/pending_operational_disposition을, scheduled_operator.recovery는 runner status/evidence_ref와 output을 작성한다. CoreEngineMixin._observe_running의 observation_fact_sequence와 CallEngineMixin._call_stop_requested의 첫 stop_reason도 독립 저장 의미 연결이 남는다. 각 정확 심볼/판본·필요한 표본은 tasks/execution-fields/evidence/execution-fields.json의19행이다.

execution-storage는 새19행을 기존73행의 실제 근거와 연결하고 유효92필드의 실제 표본으로 공통 역방향 검사를 완성한다. 열린evidence의 값/참조와 닫힌 필드 모집단을 구별하며 별도 알고리즘/합성 전체필드 fixture는 쓰지 않는다. 기존73행의 범위 한정 성질과 전체쓰기 fresh T3도 구별한다. 직접 선행은 execution-fields 하나이며 storage-academic은 같은 수용판의 목표/학술 가족, storage-conversation은 기존 lifecycle/제어 가족을 병행한다. 새task에서 두 기존task의 중앙schema/governance/academic/lifecycle/저장 기반·공통pairs/공유설명은 읽기 전용이다. 의미 있는 writes 교집합은 없고 캐시는 own base복원, 동시시험 최대3task·각jobs1이다.

## 0053 수용: 대화 저장값과 수명·제어 후속의 정확 경계

tests/sim/test_lifecycle_engine_public.py:read_publication(engine,head=None)는 새 installed_contract 객체의 ResearchRepository 첫 load를 사용해 reader/head/instance/runtime을 돌려준다. assert_runtime_metadata는 scalar와 object의 독립 expected, 선택 absent·옛head를 검사하고 runtime을 반환한다. assert_conversation_publication은 runtime/conversations/<id>.json의 /record, research/_state/metadata.json의 policy, runtime/lost_conversation_generations/state.json의 /record와 manifest/원값을 비교하고 실제 conversation record를 반환한다. assert_closed_family_samples는 공통 contracts.pairs.assert_pair와 해당 family checker/validator로 실제 표본의 필수+선택 필드를 역방향으로 검사한다. 제품 API 추가는 없다.

conversations의 heartbeat는 마지막 live 신호의 source_ref를 바꾼다. detach는 loss event에 요청 ref를 남기며 record의 ref를 바꾸지 않는다. 새 generation은 lost_at/loss_reason을 갖지 않는 새 record를 쓰며 살아 있는 새 세대만 resume을 연다. pause 상실은 ID→generation을 저장하고 continue_authorized의 후속 상실은 이전 lost mapping/권한을 바꾸지 않는다. user_pause는 실제 user 요청의 request_id/text/created_at이며 user resume 뒤 metadata/manifest에서 제거된다. availability는 초기 blocked/reason, 미충족 활성화의 user owner, active available, clock blocked 및 core operator owner를 저장하고 뒤 replacement는 선택 owner를 제거한다. call_engine의 동일 clock writer와 허용 boolean user_pause root writer 미확인은 이번 새 실행 근거 밖이다.

FamilyRecordStorageTests.test_conversation_control_values_are_rejected_before_publication_and_on_corrupt_read는 실제 control producer의 기준 상태를 저장한 뒤 공개 lease1.5/True/0 및 다섯 가족의 잘못된 값·누락·미선언 필드의 정확 사유/head불변/write0을 확인한다. 저장float는 family integer 전에 JSON floating-point 금지로 반려된다. 손상 lost singleton의 음수값은 새 reader의 minimum 반려이며 비검증 publish는 이 반례에만 쓰인다. 전체 쓰기분기/T3와 최종판은 별도다.

후속 storage-control-state의 제공자는 initialization.initialize_state, InitializationEngineMixin._initialization_control, LifecycleEngineMixin._activate_initialization/_pause_lifecycle/_resume_lifecycle/_clock_guard/_refresh_readiness/_apply_extended_control이다. research.lifecycle은 원input의 text/UTF-8 bytes/SHA·명시 adoption/activation/intent_check/history/영구close를 갖는 singleton이며 schema의 중첩 닫힌 필드와 validate_lifecycle/_immutable_input_rules를 함께 소비한다. permanently_closed와 runtime.status=closed는 lifecycle.state enum과 다르다. clock_guard는 계산된 메모리 guard와 실제 게시된 metadata를 구별한다. 현재 optional observed_at의 root writer는 미확인 후보이고 실제 실패는 observed_utc/last_observed_utc/expected_at_least를 사용한다.

processed_controls는 core_engine의 공개 제어 처리 후 요청ID 배열이고, extended_controls는 요청ID→행 singleton이다. _apply_extended_control은 실제 request/action/processed_at를 작성하고 exact_content_hash(old['request'])로 동일 재전달/내용 충돌을 구별한다. _limited_recovery_control은 이 원request를 소비한다. source_ref/status/result의 미생산 후보를 map 안 닫힌 행의 필드로 판정하며 열린 request evidence의 임의 키와 혼동하지 않는다. pause/resume은 early return하므로 모든 제어가 이 ledger를 생산한다는 가정을 두지 않는다. 정확 처리시각/원문/순서/부재와 옛head·재시작 성질이 새 task의 질문이다.

새 task는 storage-conversation의 수용 직접시험과 storage-academic의 중앙schema 수용판을 선행으로 받는다. 중앙schema 슬롯 처분·소비·정본 설명을 같은 task에서 처리하기 위한 소유 순서이며 execution-storage는 기다리지 않는다. execution/core/call 제공자와 공통pairs는 읽기 전용이다. academic과의 의미 있는 writes는 선행으로 직렬화하고 execution-storage와는 복원할 캐시만 겹친다. 다른25미배정 가족과 관찰4/전쓰기freshT3/최종관문은 남긴다. 앞0051/0052의 진행 표현은 해당 시점 이력이다.

## 0054 수용: 목표·학술 저장과 사건·영수증 후속 경계

storage-academic은 수용됐다. tests/support/storage_academic_pairs.py:family_pair(contract,root,family,samples)는 research/runtime state 쌍의 list item 세 가족, scalar 두 가족과 academic_assessments typed singleton 전체 목록을 실제 설치 checker/validator에 보낸다. scalar는 /value, typed list는 items[] 아래 닫힌 item/solution_basis/evidence를 storage_authority_pairs._named_fields로 투영하고 contracts.pairs.assert_pair의 공통 역방향을 쓴다. 열린 evidence/hash map과 HISTORY에 임의 필드 의무를 만들지 않는다.

goal_samples/assessment_samples/resolution_samples는 실제 감사 적용·TASKS 평가·반려/해소 생산자를 호출한다. _keep는 각 대상의 게시전 원내용/존재 여부를 보존하고 engine._save 뒤 새 installed_contract의 ResearchRepository 첫 load로 blobs를 decode해 비교한다. 이전 head와 artifact bytes도 보존한다. 외부 포트는 기존 대역이다. goal_judgments는 created_at/findings/input_basis를 허용하지 않으며 reason과 current/invalidated_reason/use_history는 유지한다. 실행 자체의 동명 필드와 동일성검토 findings는 별도 계약이다.

새 storage-events의 events는 list item, pending_events는 ID배열 singleton, event_cursor는 NAT metadata, control_receipts/integrations는 ID map이다. events.EventPublisher.assign_sequences_in_place(runtime,published_events=...)는 Repository 후보에만 새 event_seq/현재 cursor를 작성한다. 부모 내용/순서/번호를 유지하고 pending은 소비 대기ID이므로 게시 자체로 제거하지 않는다. planning.record_due_events와 lifecycle_engine._lifecycle_event 등이 실제 사건을 만들며 core_engine._consume_action_events는 입장 action.event_refs와 같은 task_new_input request_id를 소비한다. 문자열 pending 계약에 남은 dict 보존 분기는 새 task의 현재성 판정 대상이다.

CoreEngineMixin._publish_control_request는 실행/권한/시계와 실제 request를 확인하고 capability를 제외한 safe_request의 exact_content_hash, 원request, parent_snapshot/received_at와 처리 결과를 control_receipts에 검증 게시한다. 같은 ID/해시의 재전달과 내용 충돌, preview 비게시, CAS 뒤 ack유실의 durable 재조회는 구별한다. 저장optional과 response projection/request 안 동명 키를 같은 writer로 세지 않는다. integration.apply_bundles는 허용된 실제 bundle 적용 뒤 execution_id/payload_sha256/members/input_snapshot·조건부 response_sha256를 integrations에 기록한다. 일치 재수신은 원receipt를 보존하고 달라진 내용은 반려한다.

새 task는 execution-storage의 core/직접시험과 storage-control-state의 lifecycle/Repository/중앙schema/직접시험 수용판을 실제 선행으로 받는다. 관련 필드 정리와 소비/시험/설명/미러를 같은 task가 맡는다. 기존 두 task는 독립 유지, 새5가족의 대응과 전쓰기 freshT3/다른20가족/최종관문은 구별한다. 앞0052/0053의 학술진행 표현은 당시 이력이다.

## 0055 수용: 실행 저장 역방향·소수 보존과 입력 후속 경계

CallEngineMixin._receive_call은 release_or_hold가 False인 종료 미확정 분기에서도 payloads.json_safe(result)를 한 번 계산한다. 그 결과의 error_kind/failure를 실행에 복사하고 같은 결과를 canonical_json으로 result_ref artifact에 쓴다. 원소수의 reported_decimal 표현이 두 저장 위치에서 같으며 float를 허용하도록 schema를 열지 않는다. stopping/unknown·예약/종료 장벽과 원 native stream은 보존한다. 원보고의 failure.native_info.utilization=0.75는 해당 저장 반려를 드러낸 실제 parser/runner 입력이다.

tests/support/storage_execution_pairs.py:StoredExecutions.read(engine,branch,identifiers=None,head=None)는 새 record_store/ResearchRepository로 온전한 head를 검증 적재하고 그 뒤 필요한 execution만 표본에 고른다. stored_pair('executions',snapshots)는 현행 StateContract family.schema.properties 전체를 공통 contracts.pairs.Pair.fields로 전달한다. test_executions_cover_every_required_and_optional_receiver_field는 실제 생산·저장과 내용 단언을 실행한 동일 표본의92필드를 assert_pair로 검사하고 미생산 optional 추가의 역방향 실패도 확인한다. 별도 registry나 역방향 알고리즘은 없다.

stored_execution_inputs/stored_delegation_input/stored_kind_input은 실제 준비의 학술/위임/종류 hash·solution basis·추가감사 내용을 독립 입력과 연결한다. delegated_judgment_scene은 기존 sim 입력시험과 새 저장시험의 공통 준비이며 실제 호출에서는 모호하지 않도록 이미 채택된 research grant 하나를 명시한다. stored_provider_returns/stored_provider_failure는 실제 parser→runner→owner·검증저장의 비빈 사용량/scopes/실패와 원bytes/SHA를 연결한다. stored_observation_and_stop은0/1/3개 fact와 첫 stop_reason/시각·실행 binding을, stored_operational_dispositions는 continue/retry/resume과 종료 후 marker 제거/같은 owner를, stored_operator_runner/stored_late_return은 원 runner file/늦은 원결과와 옛head를 검사한다. 기존 세 StoredCallEvidence 장면도 helper로 옮겨 기존 단위시험이 소비한다. 앞0052의 역방향/19필드 남김은 여기서 수용됐으며 전체 쓰기분기/최종판은 남는다.

후속 storage-inputs의 research.sources는 list item이다. initialization.initialize_state는 빈 sources를 만들며 core_engine.initialize_instance가 전달된 파일의 bytes/name/path/SHA/크기를 저장한다. CoreEngineMixin._apply_inbox는 source 요청의 normalized_source_bytes(control_contracts.py)를 소비해 동일내용이면 기록만 남기고, 변경이면 같은 source ID의 revision/history와 새 artifact/source_ref를 쓴다. runtime.inputs는 초기화의 원text/SHA/config/시각과 이후 실제 input request를 저장하는 list item이며 영구close에서는 새입력을 반려한다. 제어요청과 저장record의 optional 집합을 혼동하지 않는다.

runtime.private_insights는 cycle ID→HISTORY의 열린 singleton이다. _apply_extensions는 identity/운영 검토의 원 research_insights를 source_execution에 연결해 진행 중 cycle에 보류하고 completed/unresolved에서 해제한다. 열린 내용은 원문/순서/작성자/비공개 상태의 독립 값 단언이 필요하다. runtime.pending_kind_checks는 닫힌 item 배열 singleton이며 _propose_kind가 family/token/definition_id/source_ref/actor_ref를 쓴다. _apply_kind_definition_check는 현재 정의hash와 독립 checker input_basis를 대조하고 정확 해당 definition 항목을 제거하며 approved/수정요구/미해결 처분을 수행한다. item의 optional execution_id 생산 여부는 후속 판정 질문이다.

새 task는 이 네 가족의 실제 생산/검증 게시/새 reader decode와 closed field 역방향·open content를 보완하고 필요한 schema/소비자/시험/설명/미러 수리를 함께 맡는다. 같은 core/초기화/Repository/중앙schema/공유설명을 수정하는 storage-events 수용판이 직접 선행이다. storage-control-state와 storage-events의 기존 배정은 유지한다. 원84 중55질문수용·기존4진행/5대기·새4대기·16미배정이며 관찰4/전쓰기freshT3/최종관문과 구별한다.

## 0056 수용: 수명·시계·제어 저장과 action 후속 경계

storage-control-state는 수용됐다. record_schemas.schemas의 lifecycle은 required state/immutable_input/input_id를 유지하고 미생산 required_capabilities/activation.completed를 허용하지 않는다. 원input 검증은 original_input_bytes와 Repository의 같은 연구 원문 불변 검사, 명시채택은 InitializationEngineMixin._initialization_control, intent_check는 _complete_initial_intent의 실제 독립 import에 연결한다. 영구종료는 permanently_closed와 runtime.status=closed다. _activate_initialization의 activation은 missing/observation_errors를 기록하며 프로필 capability는 별도 유지한다.

LifecycleEngineMixin._clock_guard의 실패와 _refresh_readiness가 게시한 runtime metadata clock_guard를 구별한다. 저장 필드는 state/usable/reason/observed_utc/last_observed_utc/expected_at_least이고 observed_at는 제거했다. guard의 last_observed_utc는 실패 당시 persisted 값이며 CoreEngineMixin._save는 이미 승인된 더 늦은 _clock_anchor를 root high-water로 보존할 수 있다. 따라서 둘의 시각 일치는 저장 불변식이 아니다. 같은 owner의 retained failure, cold owner 재관측과 명시 resume은 그대로다.

processed_controls는 _apply_inbox/_reject_control이 기록한 ID 순서이고 _inbox가 재적용을 막는다. extended_controls의 행은 request/action/processed_at만 허용하며 source_ref/status/result는 제거했다. LifecycleEngineMixin._apply_extended_control은 원request를 deepcopy하고 동일ID 내용 hash를 대조한다. pause/resume/close는 early return하므로 이 행을 만들지 않는다. _check_limited_recovery의 원request/approval binding 소비와 공개receipt는 유지한다.

tests/sim/test_lifecycle_engine_public.assert_closed_family_samples(test,name,samples,root='runtime')는 installed family의 닫힌 nested 필드를 _named_fields와 공통 Pair에 연결한다. extended_controls는 map 내부 행 schema를 사용한다. assert_control_singleton은 read_publication의 새 contract reader 첫 load, singleton blob/manifest와 독립 expected를 비교한다. ID 배열은 값·순서로 검사한다. 단위시험은 제거 슬롯/잘못된 타입·불변원문 변경의 정확 pre-write 반려와 손상원문 cold read를 보완한다. 기존58시험메서드는 AST가 불변이며 그 밖의 모든 의미를 새로 보장한다는 뜻은 아니다.  전쓰기/final관문은 남는다.

새 storage-actions의 queue는 record_schemas.RECORDS['queue']=_ACTION을 소비하는 list item이고 waiting_actions는 _ACTION을 포함한 닫힌 행의 singleton mapping이다. 공통 _ACTION은 executions.action 등 여러 저장 위치에도 쓰인다. 특정 가족의 부재를 공통 미생산으로 판정하지 않으며 실제 각 producer·수신 경계와 저장 표본을 연결한다. CoreEngineMixin._enqueue는 호환·비live 요청의 refs/reasons/revision 근거를 병합하고 비호환 payload는 별도 ID/lineage로 추가한다. wait_rules.waiting_action/update_waiting_action은 실제 owner가 보류를 쓰는 정본이며 원 action/owner·입력 snapshot·조건/다음owner와 진단/복구/검토/위임 관련 의미를 연결한다. 각 helper 반환만으로 저장 성공을 대신하지 않는다.

storage-events→storage-inputs가 수정하는 core/중앙schema/저장기반/설명을 수용한 뒤 storage-actions가 두 가족의 필요한 수리·직접시험·설명·미러를 함께 맡는다. 직접 선행은 storage-inputs 하나다. 기존70개 정의는 유지하며59수용·기존9배정·새2대기·14미배정과 관찰4/freshT3/최종관문을 구별한다.

## 0057 수용: 사건·영수증 저장과 복구·정비 후속 경계

storage-events는 수용됐다. tests/support/storage_event_pairs.py:family_pair는 runtime.events/control_receipts/integrations의 설치된 checker/validator와 닫힌 필드를 공통 Pair/_named_fields에 연결한다. pending_events/event_cursor는 /value 및 정확 배열/정수 내용을 검사한다. reader/keep는 새 installed_contract를 가진 ResearchRepository의 첫 load로 다섯 게시 가족과 옛head를 비교한다. bundle CAS 뒤 아직 저장하지 않은 execution.integration_result는 별개이므로 전체 owner를 게시됐다고 주장하지 않는다. lifecycle/control/bundle/external/trust 실제 생산 표본과 tests/contracts/test_storage_event_pairs.py의 독립 내용/반려 단언을 공유한다.

record_schemas.schemas.RECORDS의 events 미생산15필드와 control_receipts root5필드는 제거됐다. CoreEngineMixin._consume_action_events는 문자열 ID만 소비하며 task.newinput이 사건의 request_id와 같을 때만 제거한다. 실제 request 안 grant_id/transport_id·원payload, 반환 projection의 snapshot/publication_id와 _stage_submission_capture의 저장 payload는 유지한다. 사건의 번호는 EventPublisher가 후보 게시에서 부여하고 pending은 게시만으로 비우지 않는다. integration.apply_bundles의 payload hash는 선언/좌표별 값·member순서를 포함하고 output 소유 bundle만 response hash를 갖는다. 직접 snapshot 부재는 null을 보존하며 execution.integration_id 저장 슬롯은 복원하지 않는다.

후속 storage-recovery의 recoveries는 core_engine._recover_disappeared가 미종료 execution IDs/started_at과 각 사실·local termination/remote unknown·후속 owner를 dispositions에 쓰고 순회 완료에 finished_at을 기록하는 map이다. 완료시각을 모든 원격 실행 정산의 증거로 해석하지 않는다. operational_dispositions는 core의 _apply_operational_disposition/_complete_operational_disposition/_run_pending_operational_repairs 및 repair_execution이 실제 검토·발급입력/현재성·종료장벽을 소비해 쓴다. disposition은 operational_dispositions.validate_disposition과 contracts.disposition_schema의 실제 계약을 따르며 열린 evidence의 임의 키를 root 필드로 세지 않는다.

maintenance_gate.apply_control(runtime,request)는 user/operator의 quiesce에 원 request_id/origin/reason/created_at·draining을 기록한다. settle은 실제 quiescence의 pending_executions/held_reservations와 settled_at·blocked/quiescent를 갱신한다. release는 현재 fence ID/origin/장벽을 검사하고 history에 원fence를 보존한 뒤 제거하며 user_pause는 별개다. provider_engine.record_model_policy_violation은 call_engine._receive_call의 원result에서 reported_models를 deepcopy해 execution_id/assigned_model과 저장하고 종료되지 않은 연구를 paused로 둔다. lifecycle의 명시 resume이 marker를 제거한다. 열린 EVIDENCE singleton은 독립 값/부재·저장/별도decode로 판단한다.

새 task는 이 네 가족의 생산/필드/내용 질문과 필요한 provider·소비자·schema·직접시험/설명/미러 수리를 함께 맡는다. 같은 core/중앙schema/저장시험·설명의 storage-actions 수용판 하나가 직접 선행이다. 기존71개 정의는 유지한다. 원84 중64수용·기존6/새4배정·10미배정이며 관찰4/전쓰기freshT3·최종관문은 별도다.

## 0058 부분 수용: 입력 저장 계약과 ontology 표본 수리 경계

tests/support/storage_input_pairs.py:family_pair(contract,root,name,samples)는 설치된 checker/validator와 기존 contracts.pairs.Pair/assert_pair를 연결한다. sources/inputs는 list item, pending_kind_checks는 닫힌 nested item 배열 singleton, private_insights는 cycle ID→열린 항목배열 singleton이다. 닫힌 필드는 storage_authority_pairs._named_fields, 열린 통찰은 /value와 독립 원문/순서/작성자 검사를 소비한다. keep(engine,samples,branch,previous=None)는 매번 새 installed_contract를 쓰는 ResearchRepository의 첫 decode와 필요시 옛head를 비교한다. 실제 저장 직전 필드 보충은 없다.

public_input_samples는 실제 초기 파일·초기 빈 목록·원input, source 동일/변경/신규·추가input/재전달/restart를 생산한다. sources.created_at과 pending item.execution_id는 현재 허용하지 않는다. 최초input.sha256와 후속 제어요청 기반 input의 선택필드는 서로 다르며 같은 모양으로 보충하지 않는다. pending_kind_scene/kind_checker는 실제 확장제안·정확 정의_context·등록된 독립 checker·실제 종료 lifecycle을 준비한다. _apply_kind_definition_check는 정확 현재 definition/hash·input_basis·작성자 독립성을 확인하고 원판정을 check에 저장하며 해당 pending만 제거한다. approved는 active, revision_required는 withdrawn, unresolved는 candidate 유지와 준비 후속이다. check는 열린 EVIDENCE object이고 그 안의 ID/hash/verdict/findings/실행ID는 원output과 독립 대조한다.

review_insight_scene은 실제 scope/initial 검토의 등록/입장·종료·적용과 _apply_extensions를 사용한다. 모델 수송/중앙제출은 합성 입력이다. working 동안 cycle별 비공개이고 completed/unresolved 뒤 원작성자·내용·순서로 해제/발행/계획하며 다른cycle은 남긴다. 현행 종류 철회로 원통찰이 무효해지면 history/question은 원작성자에게 귀속하므로 catch는 현재 의미를 가진다.

storage_authority_pairs.ontology_samples의 domain-only 표본과 AuthorityFieldPairs.test_ontology_fields_reach_the_actual_map_and_list_receivers의 check 제거 기대가 남아 공통 역방향/정확 반려 단언이 실패한다. storage-ontology-fix는 실제 core 표본의 검증게시/cold decode를 같은 ontology Pair에 추가하고 원check 내용/남은11필드 반려를 보존한다. 현재 입력 helper→authority._named_fields의 import 방향을 고려해 필요하면 작은 storage_kind_checks 공유 helper로 실제 준비만 옮기고 두 소비자를 함께 수정한다. runtime/schema/공유 제품설명은 쓰지 않아 storage-actions/recovery와 독립이다. 기존72개 배정 정의는 유지하며 네가족수용·kind1재개방과 전쓰기/final관문을 구별한다.

## 0060 당시 연결: 요청 입력 소유권과 저장 필드 마무리

CoreEngineMixin._enqueue(core_engine.py)는 action 전체를 deepcopy한 뒤 _bind_revision_action을 호출한다. 최초 요청의 assessment/observation target map, refs/observation/revision_followup 및 revision basis가 호출자와 분리된다. 기존 compare_keys/merged_keys·첫ID/lineage·순서/중복제거·live action 비병합과 소비/제거 의미는 유지한다. 반복 whole deepcopy 뒤 남은 payload별 복사의 필요성은 후속이 같은 소유권 계약 안에서 판단할 수 있다.

tests/support/storage_action_pairs.py:preparation_case는 call/planning이 실제로 만드는 observation_rules/observation_configuration/model_assessment_input/observation_rule_input 네 보류를 기존 sim 해소시험과 새 저장시험에 제공한다. reader는 새 installed_contract와 ResearchRepository를 만들고 keep의 첫 load는 검증 게시 blob을 decode해 원 instance/runtime·옛head와 비교한다. queue는 manifest의 IDs로 순서를 유지하고 waiting_actions는 runtime/waiting_actions/state.json singleton으로 저장한다. 현재6직접시험+3기존sim의 최종9passed는 원입력·revision부모·병합/live·준비보류내용·정확반려/write0의 범위다.

공통 record_schemas.schemas._ACTION은 queue/executions.action/waiting_actions.action/input_overflows.action 등에 쓰인다. 시작판89필드/행27필드 전체의 생산/내용/역방향은 미완료다. tests/support/storage_authority_pairs.py:_named_fields는 child.items=False에 .get을 호출해 현재에도 실패한다. storage-actions-fix는 이 기존 순회를 boolean/object 및 실제 닫힌 중첩 의무에 맞게 고치며 contracts.pairs.assert_pair를 계속 쓴다. 최신 storage-ontology-fix의 실제 check producer/소비를 보존하고, 별도 registry나 부분집합 면제 없이 공통 필드와 두 가족 각각의 실제 표본을 구별한다. 합성 enqueue refs를 실제 모든 owner 생산으로 확대하지 않는다.

storage-actions-fix는 이미 수용된 storage-actions와 storage-ontology-fix를 받아 공용helper·action/wait 표본·필요한 제공/소비/schema/시험·설명/미러를 함께 소유한다. 미착수 storage-recovery의 선행은 이 마무리 수용판이며 storage-questions는 그 뒤다. 시작된 배정은 바꾸지 않았다. 아래0059절과 번호별 절은 해당 시점의 연결이며 현재 의존/미완료 판단은 이 절과 plan/queue를 따른다.

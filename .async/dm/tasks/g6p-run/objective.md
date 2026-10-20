# 수용된 병렬 실행기로 전체 G6를 실행하고 직접 관련 공백을 마감한다

현재 1~3층 제품 함수의 결과를 시험이 실제 확인하는지 판단하는 작업이다. mutation-parallel의 실행 개선은 수용됐다. 준비된 20묶음을 그 개선판으로 실행하고 변이 결과와 실제 정상 통과를 대응하며, 생존·미실행·오류에 필요한 수리와 확인까지 이 task에서 마친다. 기존 g6-run은 사용자 중단·취소 상태 그대로 보존한다. 그 ID나 외부 출력에 이어 쓰지 않는다.

## 실제 선행과 재사용 입력

SESSION_JSON·task.json·고정 inputs/context.md/plan.md/seams.md, 자기 do-math AGENTS.md·시험-지침.md·이음새-정본.md를 읽는다. sources의 mutation-parallel-direction-2026-10-16.md, t3-targeted-direction-2026-10-16.md, storage-scope-direction-2026-10-15.md, archive-resume-2026-10-16.md와 managers/0101/review.md·handoff-delta.json이 현재 지시다. 원설계 설계.md 6.3/A24의 동등 변이와 사용자 user-decisions.md·document-batching-2026-10-14.md의 최소검증·묶음·소프트 시간 원칙을 유지한다.

직접 선행은 **mutation-parallel 수용**이다. g6-inputs와 g5-remainder는 그 선행으로 이미 수용됐다. mutation-parallel/report.json·integration.json·evidence/judgment.md와 현재 `scripts/tests/support/mutation.py:run/main/validate_jobs/passed/update_list`, `scripts/run_tests.py:wait_for_worker/worker_exit_code`, `do_math/windows_job.py:WindowsJob`의 실제 계약을 소비한다. 실행 개선의 작은 fixture는 전체 제품 G6의 증거가 아니다.

`tasks/g6-run/evidence/population.json`은 g6-inputs의 원선택과 g5-remainder의 추가15고유ID를 반영한 중단판 준비다. 123모듈/1677함수(비trivial1645·trivial32), 20묶음은 출발판의 수이지 quota가 아니다. 원 population의 선택·함수·판본과 managers/0101/execution-arguments.json의 새 argv를 재사용한다. 후자는 모든 --base/--every/--only/--test를 보존하고 --jobs 3 및 새 output만 적용한 제출용 입력이다. 현재 소스와 실제 변경 delta만 대조하며 전체 모집단·일반/T3를 다시 준비하지 않는다. g5-remainder/evidence/G6-delta.json·source-delta.json·final-source-sha256.json은 delta의 근거이며 추가 ID를 중복 적용하지 않는다. g6-inputs의 population·execution-plan·selection-impact는 선택 의미가 필요한 경우에 읽는다.

G6 대상·변이 규칙 정본은 do_math/layers.py:LAYERS와 mutation.py:functions/body/rule_of/mutate/tests_for다. 이번 실행 개선은 runtime 대상123모듈을 바꾸지 않았다. 시험/도구/문서 판본은 개선 전과 다르므로 새 실행 기록에 실제 판본을 표시한다. 원색인 진입 ordinal과 반복 --test로 추가한 직접 입력을 구별한다. 유효한 기본선택을 빼거나 명시 선택을 진입 측정으로 표시하지 않는다.

## 작은 선행 보완과 자기 사본 준비

manager0100이 보존한 정상 실패를 실행 준비에 함께 고친다. `references/과제-착수조건.md:89`의 `submission.payload_issues`는 함수임에도 필드 표기로 검사된다. 기존 `tests/support/doc_code.py:function_reference_issues/unowned_field_references` 계약에 맞는 callable 표기로 문서·미러를 보완하고 `unit.test_storage_report_projections.ReportProjections.test_human_report_preserves_loaded_initialization_blocker_and_machine_finding`을 공식 run_tests.py/jobs1의 정확 선택으로 필요한 만큼 확인한다. 함수는 존재한다. 검사/단언 약화나 runtime 우회를 추가하지 않는다. 원실패는 managers/0100/evidence/g6-run-b01/unmutated-0001에 보존됐다. 같은 원인으로 드러나는 가까운 표기 보완은 함께 마친다.

자기 workspace에 독립 .git을 준비할 권한이 있다. managers/0095/g45-index-baseline.bundle의 실제 commit `4dae85911f26f891fc3d79be9916bf4363e2d46f`를 fetch하고 작업 bytes를 바꾸지 않는 mixed reset·현재 수용 snapshot 자식 commit으로 연결한다. 기존 g6-run/evidence의 실행 준비와 g45-final/evidence/prepare.py의 raw-byte 설정을 필요한 부분만 재사용한다. `.git/info` 생성, core.autocrlf=false, hooks/gpgsign/fsmonitor 비활성, info/attributes의 `* -filter -text -ident`를 적용한다. 실제 root/Git-dir/ancestor와 준비 전후 bytes를 확인한다. checkout/--hard, 공용 Git·bundle·전역 설정 수정은 금지다.

원색인은 population.index.path의4515시험판이며 SHA256은 `3d30a04ea8e68cb138995e0f5a913981faa6cb0afc02fa0b8d682fa9b9a58824`다. 자기 기본 index의 시작 bytes/부재를 보존하고 이 원색인을 자기 생성입력 위치에만 byte-exact 배치한다. selection.py:read_index/usable/is_ancestor_of_head로 실제 사용 가능성을 확인한다. 준비 오류 때문에 전체 layer fallback을 반복하지 않는다. 유효 색인 자체의 함수별 fallback 의미는 유지한다. 원자료를 편집하거나 부분T3를 전체색인으로 위장하지 않는다.

TEMP/TMP/TMPDIR/output은 저장소 밖 짧고 고유한 경로를 사용한다. 예정 출력은 `C:/g6p-g6p-run/b01`~`b20`이다. 새/빈 경로인지 확인하고 이미 자료가 있으면 원자료를 보존한 채 새 task 전용 경로로 argv를 갱신한다. 기존 GIT_CEILING_DIRECTORIES를 보존하며 자기 parent/외부 scratch를 추가한다. 원 g6-run/외부 b01, 다른 task, 공용소스는 읽기 전용이다. 영구 증거는 자기 evidence와 보존 객체를 사용하고 사라질 workspace/Git에만 의존하지 않는다. 과거 코드는 공식 workspaces.py restore로 필요한 경로만 복원한다.

## 실행과 판정

1. 이 task가 pseudo_tested.json과 마지막 공식 미러를 단독 소유한다. **20명령은 하나씩, 명령 내부는 --jobs 3**으로 실행한다. jobs는 변이·정상 child 합계이며 별도 정상 pool을 추가하지 않는다. 이 task에 현재 총 시험3슬롯을 배정한다. 다른 시험/수리 확인은 변이 명령을 마친 뒤 실행한다. 추후 manager가 별도 시험을 배정할 경우 공유 상한에 맞춰 jobs를 낮추는 조정이 필요하다. 모델 worker 상한10을 시험 child10 허가로 해석하지 않는다. source·시험·index·timings를 명령 중 변경하지 않는다. 임의 timeout이나 경과시간에 따른 종료/포착은 없다.
2. 현재 source와 선택을 고정한 evidence/population.json·execution-plan.md에 실제 argv와 원입력 참조를 남기고 준비한 묶음을 실제 실행한다. 각 mutation.json 및 mutant/normal spec·result·attempt·output·PID/exit·판본을 보존한다. outcomes는 함수 계획 순서이고 baseline ID는 해당 보고에서 최초 요청 순서다. ID로 연결하며 완료 순서로 추정하지 않는다. 한 명령 안 동일 정상 선택만 공유된다. 명령간 baseline cache·함수별 자동 재개·자동 outcome 병합 기능은 없다.
3. 정상 기준은 실패후보만 실제 실행하는 기존 cheap-first/failfast 의미를 유지한다. 전건 정상 실행을 별도로 추가하지 않는다. 정상실패·skip/0건·load/fixture/결과부재·비정상 exit·사용자 중단은 killed가 아니다. 이전 b01은 최종보고가 없으므로 이 batch를 새 output에서 실행한다. 부분 raw attempt를 이어 붙여 완료로 만들지 않는다. 다른 **완결된** batch 결과는 source/선택/실제 정상 기준/종료의 유효 범위를 대조해 재사용할 수 있다.
4. 명시 중단은 interrupted=true·미완료 execution_error이며 listing을 갱신하지 않는다. 소유 Windows Job root/후손 종료를 확인한다. 예기치 못한 내부 예외나 부모 강제종료에서는 최종보고가 없을 수 있으므로 원attempt/PID/output을 보존한다. 재개는 새 output에서 미완료 묶음을 실행한다. 기존 결과가 있는 output을 비우거나 덮지 않는다.
5. survivor는 실제 계약과 단언을 읽어 처분한다. 비동등 변이가 생존하면 실제 결과·효과를 확인하는 최소 단언을 관련 기존 시험에 보완하고 직접 관련 제품 결함도 함께 고친다. 원동작과 극단 변이가 동등할 때만 설계6.3/A24에 맞는 정확한 사유를 listing에 쓴다. 비용·어려움·환경·기존 목록 존재를 면제 사유로 쓰지 않는다. 앞선 survivor의 unreasoned_entries 때문에 뒤 batch의 exit가 실패할 수 있으므로 exit만으로 모든 함수가 미실행이라고 하지 않는다.
6. 수리 후 필요한 일반 검사는 공식 run_tests.py/jobs1의 정확 ID로, 변이·정상 재확인은 해당 함수를 포함하는 최소 모듈 범위와 같은 명시 입력으로 수행한다. 새 함수별 실행 framework를 만들지 않는다. helper/시험/입력의 영향은 기존 선택 근거와 실제 delta로 필요한 만큼 판단한다. 불변 결과는 재사용하고 별도 판본의 부분 성공을 한 번의 전체 재실행으로 합산하지 않는다. 원실패/수리판/최종판을 구별하며 포착 기준·분모·층·기존 단언을 약화하지 않는다.

관련 수리·필요 확인·설명·미러를 같은 task에서 마친다. 외부 결정/권한 또는 독립 제공자 수리가 필요하면 정확 함수·입력·원실패·사용 영향과 남은 결과를 보고한다. 새 전수 준비를 반복하는 것만으로 마치지 않는다.

## 범위와 제출

쓰기 범위는 do-math 정본·미러이며 실제 G6 공백에 필요한 runtime/직접 시험/helper/설명과 pseudo_tested로 제한한다. 공식 build_skill_mirrors.py로 관련 미러를 갱신한다. 생성 index·timings 등은 증거를 보존한 뒤 시작 bytes/부재로 복원한다. listing은 실제 결과와 정당한 동등 사유를 반영해 제출하며 원시 보고를 대신하지 않는다.

추가/전체 T3·전체 일반/T4/T5·실공급자 호출·설치·예약·외부 운영정리는 이 배정에 넣지 않는다. 지정5모듈 관련 추가T3/전체T3 반복금지와 A22의 공통 저장 보장 재사용을 유지한다. 가족별 quota·전수 재입증·장기감사는 추가하지 않는다. G5 환경6arc/10행·부분index/자동재사용 한계, 원G4/전체T3와 조건부skip·14910.2초 소프트초과, G1~G3 최종연결·남은G7/G8·L01/공급자 조건은 별개다. 공용 context/plan/seams/queue/state·graphify·공용 Git/push·기존 연구 인스턴스는 수정하지 않는다.

완료는 현재 대상 함수와 outcome의 누락/중복 없는 연결, 비동등 변이의 실제 포착·정상 통과, 정당한 동등 사유, 오류/미실행/정상실패의 정확한 처분이 있는 상태다. 실제 공백이 남으면 report는 partial/blocked와 정확 남김으로 작성하며 G6 전체 성공을 선언하지 않는다. evidence/judgment.md와 실행 요약에 범위·판본·정상 기준·수리 이유·재사용·최종 남김을 설명한다. 모든 raw 결과를 영구 evidence에 연결하고 `python C:/math/services/async-development/check.py report C:/math/.async/dm g6p-run`을 통과시킨다.

## 실행 중 사용자 추가 지시

> **사용자 최신 지시 — 변이 재확인(2026-10-17):** C:/math/.async/dm/sources/mutation-recheck-direction-2026-10-17.md를 적용한다. 현재 첫 전체 실행은 유지하되 후속 재확인은 문제가 발견된 정확 함수·시험과 수리의 직접 영향 범위만 수행한다. 전체20묶음 또는 무관한 정상함수를 함께 재실행하지 않는다. 이전 최소모듈 범위 문구보다 이 지시가 우선하며 기존 유효 결과는 판본·선택을 구분해 재사용한다.

상세 지시 원문을 읽고 수리 뒤 재확인 계획에 반영한다. task.json의 배정 ID·writes·선행은 그대로이며 최초 전체측정을 취소하거나 재시작하지 않는다.

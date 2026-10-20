# 수용판의 G6 전체 극단 변이와 정상 기준을 실행하고 실제 공백을 마감한다

G6의 목적은 현재 1~3층 제품 함수가 시험에서 실제 결과를 확인받는지 판단하는 것이다. 준비된 모집단과 유한 20묶음을 실제로 실행하고, 정상 소스의 실제 통과로 포착을 확인하며, 생존·미실행·오류를 숨기지 않는다. 실행 중 발견한 직접 관련 결함·시험 공백·소수 설명/미러 보완과 필요한 확인을 이 task에서 함께 마친다. 준비를 다시 조사하는 task가 아니다.

## 실제 선행과 입력

SESSION_JSON·task.json·고정 inputs/context.md·plan.md·seams.md, 자기 do-math AGENTS.md·scripts/tests/시험-지침.md·scripts/이음새-정본.md를 읽는다. 공용 records/sources의 t3-targeted-direction-2026-10-16.md·storage-scope-direction-2026-10-15.md·archive-resume-2026-10-16.md와 managers/0098/review.md·verification-review.json이 현재 판단이다. 원설계 설계.md 6.3절/A24와 사용자 user-decisions.md·document-batching-2026-10-14.md의 목적·소프트 시간 기준·묶음 원칙을 유지한다.

실제 선행은 **수용된 g6-inputs와 g5-remainder**다. g6-inputs/evidence/population.json·execution-plan.md·selection-impact.json·static-check.json·judgment.md 및 report/integration은 g5-target 수용판과 명시 선택 도구의 준비 결과다. 준비판은 123모듈/1677함수(비trivial1645·trivial32), 원선택 참조1393, 20묶음이며 전부 not_run이다. 함수 수는 새 판본의 quota가 아니다. g5-remainder의 수용 report/integration과 보고가 가리키는 최종 source/시험/추가T3 근거를 읽고 **그 실제 변경 delta만** 기존 population·선택에 반영한다. 해당 수용 manager의 판단과 미완료 항목도 기록한다. g5-remainder 수용은 G5 전체 성공을 뜻하지 않는다. 미완성 사본이나 미래의 성공을 전제로 삼지 않는다.

실제 규칙은 scripts/do_math/layers.py:LAYERS와 tests/support/mutation.py:functions/body/rule_of/mutate/tests_for/run/main/passed/update_list, selection.py:read_index/usable/is_ancestor_of_head다. 준비의 원값·직접 선택을 재사용하며 변경 함수 본문/좌표, 변경 시험/helper/입력과 직접 소비 경계만 갱신한다. 원색인의 유효 ID를 이유 없이 빼지 않는다. g5-remainder의 새 직접 시험은 필요한 기존 batch의 반복 --test로 보충하고 기존 명시 ID를 유지한다. 명시 선택은 --only 범위 모든 함수에 기존 색인/fallback과 합집합으로 적용되며 새 관측 진입이 아니다. 함수별 registry·새 색인 병합·전체 모집단 재감사를 만들지 않는다.

## 자기 사본의 실행 준비

기존 population의 batches[].arguments_from_workspace_root가 정확한 20 argv의 출발점이다. g5-remainder delta에 필요한 모듈/시험 인자와 고유 output 경로만 갱신하고 evidence/population.json·execution-plan.md에 실행할 배열을 고정한다. 기존 분할을 유지하되 실제 추가/삭제 함수는 현재 코드와 대조한다. G1~G3의 최종 문서 연결을 추가 선행으로 요구하지 않는다.

자기 workspace의 독립 Git 준비를 허용한다. managers/0095/g45-index-baseline.bundle의 실제 commit `4dae85911f26f891fc3d79be9916bf4363e2d46f`를 fetch하고 작업 bytes를 바꾸지 않는 mixed reset·현재 수용 snapshot 자식 commit으로 연결한다. g6-inputs의 git-preparation.json·final-snapshot.json과 g45-final/evidence/prepare.py의 raw-byte filter 설정을 필요한 만큼 재사용한다. `.git/info` 생성, `core.autocrlf=false`, hooks/gpgsign/fsmonitor 비활성, info/attributes의 `* -filter -text -ident`를 적용하고 실제 root/Git-dir/ancestor·준비 전후 bytes를 확인한다. checkout/--hard로 현재 소스를 덮지 않는다. 공용 Git·bundle·전역 설정은 수정하지 않는다.

원보존 index는 g6-inputs population.index.path 또는 g45-final/evidence/G6-inputs.json의 preserved_selection_index다. SHA256은 `3d30a04ea8e68cb138995e0f5a913981faa6cb0afc02fa0b8d682fa9b9a58824`, 원4515시험판이다. 기본 tests/.selection-index.json의 오래된bd3ae53f/2163시험판과 구별한다. 자기 기본 index의 시작 bytes/부재를 보관하고 보존 index를 **자기 생성입력 위치에만 byte-exact** 배치한다. 원보존 index와 coverage/entered/store는 읽기 전용이다. read_index/usable과 실제 ancestry를 확인해 전체 실행에 쓸 입력을 준비한다. 준비 오류로 index가 무효가 되면 이를 고치고 시작하며 무심코 전체 layer fallback을 반복하지 않는다. 유효 색인 안의 함수별 fallback 의미는 유지한다. index를 직접 편집하거나 부분T3를 전체index로 위장하지 않는다.

TEMP/TMP/TMPDIR/output은 저장소 밖 짧고 고유한 경로다. 예정 C:/g6run-g6-exec의 존재를 확인하고 충돌하면 새 경로로 배열을 갱신한다. 기존 GIT_CEILING_DIRECTORIES 값을 보존해 자기 parent/외부 scratch를 추가하며 상위 공용 Git 오인식을 막는다. 다른 task·원자료를 덮어쓰지 않는다. 과거 코드가 필요하면 `python C:/math/services/async-development/workspaces.py restore C:/math/.async/dm TASK baseline|result NEW_DIRECTORY PATH...`로 필요한 파일만 복원한다. 과거 workspace/base·정리될 자기 Git의 존속을 영구 근거로 삼지 않는다.

## 실행·수리·판정

1. 이 task가 전체 pseudo_tested.json과 마지막 미러 게시를 단독 소유한다. 명령과 실제 child는 하나씩 순차 실행한다. mutation CLI에는 --jobs가 없으며 이 실행은 시험 슬롯1이다. 다른 시험을 포함한 동시worker 상한3을 유지한다. 명령이 실행되는 동안 소스를 수정하지 않는다. 시간은 소프트 기준이고 임의 timeout을 넣거나 시간경과로 killed/실패/완료를 정하지 않는다.
2. 갱신한 유한20묶음을 실제 실행한다. 각 mutation.json, mutant/normal child의 spec·result·attempt·output·PID/exit와 source/선택 판본을 자기 evidence에 보존한다. 원실패와 최종 성공의 판본을 구별한다. 앞선 survivor 때문에 뒤 명령의 unreasoned_entries/exit가 실패할 수 있으므로 exit만으로 그 묶음 전체가 미실행이라고 하지 않는다. 각 함수의 실제 outcome과 정상 기준을 대응한다. 준비 단계의 작은 fixture 결과를 제품 함수 결과에 넣지 않는다.
3. survivor는 실제 계약과 현재 단언을 읽어 판정한다. 비동등 변이가 살아남으면 실제 결과·효과를 확인하는 최소 단언을 관련 기존 시험에 보완하고 직접 관련 구현 결함이 있으면 함께 고친다. `return None`/빈 본문/생성기 변이가 원래 동작과 동등할 때만 원설계가 허용하는 정확한 사유를 pseudo_tested에 쓴다. 단순히 어려움·비용·환경·기존 목록 존재를 면제 사유로 쓰지 않는다. mutation.passed의 bool/사유 있는 개수만으로 의미 판단을 대신하지 않는다.
4. 수리 뒤 필요한 일반 시험은 공식 run_tests.py/jobs1의 정확 ID로 확인하고, 해당 함수가 들어 있는 최소 모듈 범위에 같은 명시 입력을 공급해 변이·정상 기준을 다시 확인한다. 기존 도구가 모듈 범위만 지원한다는 한계를 드러내고 새 함수별 실행/선택 프레임워크를 만들지 않는다. 수리로 달라진 helper/시험/입력의 영향을 기존 population/selection-impact 근거로 필요한 만큼만 추적한다. 불변 결과는 재사용하고 서로 다른 판본의 결과를 한 번의 전체 실행으로 주장하지 않는다. 모든 원자료를 다시 돌리는 blanket 재실행은 하지 않는다.
5. 실행오류·not_executed·정상실패·skip·0건·원자료 부재를 포착으로 바꾸지 않는다. 배정 안에서 필요한 작은 입력 수리는 같은 task에서 마친다. 외부 결정/권한이나 독립 제공자 수리가 필요하면 정확 함수·입력·원실패·사용에 미치는 영향·남은 결과를 보고한다. 아무 성과 없이 준비 반복으로 끝내거나 정상 기준 없는 성공을 만들지 않는다.

완료 판정은 현재 대상 함수의 누락/중복 없는 outcome 대응, 비동등 변이의 실제 포착과 정상 통과, 정당한 동등 변이 사유, 해결되지 않은 오류/미실행/정상실패의 명시적 처분이다. 해결되지 않은 실제 공백이 있으면 report를 partial/blocked와 정확 남김으로 작성하고 G6 전체 성공을 선언하지 않는다. 실패를 숨기려고 분모·층·변이 규칙·passed 기준·기존 단언을 약화하지 않는다.

## 범위와 제출

쓰기 범위는 do-math 정본·미러이며, 실제 G6 공백에 필요한 runtime/직접 시험/helper/시험 지침·관련 설명과 pseudo_tested로 제한한다. 스킬 전체를 임의 재편하는 권한이 아니다. 관련 수리·확인·설명·미러를 한 task에서 마친다. 제품 변경에 따라 공식 build_skill_mirrors.py로 갱신하고 허용된 실제 변경만 제출한다. 생성 index·비용cache 등은 원자료를 보존한 뒤 시작 bytes/부재로 복원한다. pseudo_tested는 이번 단일 소유자가 실제 결과와 동등 사유를 반영해 제출하며 원시 보고를 대신하지 않는다.

추가/전체 T3·전체 일반/T4/T5·실공급자 호출·설치·예약·외부 운영정리는 이 배정에 추가하지 않는다. 최신 지시의 전체T3 금지를 유지한다. g45-final의 원전체G4/T3, g5-target/remainder의 추가판본, G5 환경6arc/10행·조건부skip·14910.2초 소프트초과와 다른 G1~G3/G7/G8·L01/공급자 원자료 조건을 자동 종료하지 않는다. 기존 충분한 저장 A22 보장을 재사용하며 가족별 quota·전수 재입증·장기감사를 만들지 않는다. 공용 context/plan/seams/queue/state·graphify·공용 Git/push·기존 연구 인스턴스는 수정하지 않는다.

evidence/judgment.md는 실제 실행 범위·판본·정상 기준·생존/오류 처분·수리 이유와 필요한 재확인·최종 남김을 설명한다. evidence/population.json과 실행 요약은 원20묶음의 outcome/원자료 및 현재 함수의 연결을 제공한다. 새 전수 관리 원장을 만드는 대신 기존 준비/실행 보고를 활용한다. 자기 report.json의 changes/verification/findings를 실제와 맞추고 `python C:/math/services/async-development/check.py report C:/math/.async/dm g6-run`을 통과시킨다.

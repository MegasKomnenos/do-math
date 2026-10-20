# core·생명주기·저장의 실제 미도달 수리와 직접 확인

G5 전체 fresh T3는 실제4288행 중4287passed/Windows1314 조건부skip1이지만, 123대상 중55모듈의517arc/653행 미도달로 gate=false·runner exit1이다. 제품변경 없이 그 측정이 부분 수용됐다. 이 task는 `gap-scope.json`에 지정한 11모듈의 258arc/302행만 현행 계약에 따라 판정하고, 필요한 실제 제품/시험 수리·직접 확인·관련 설명·공식 미러를 함께 끝낸다. 각 좌표는 관측된 공백이지 도달가능성 또는 제품결함의 사전 판정이 아니다.

## 입력과 시작 상태

SESSION_JSON·task.json·inputs/context.md/plan.md/seams.md와 자기 workspace의 do-math AGENTS.md·scripts/tests/시험-지침.md를 먼저 읽는다. 공용 원자료는 읽기 전용이다. managers/0068/review.md·verification-review.json, tasks/g5-full/report.json·evidence/judgment.md 및 full1/report.json·coverage.json·gap-inventory.json을 필요한 범위에서 소비한다. 자기 gap-scope.json은 같은 원좌표의 부분집합과 기존 시험 파일 쓰기 범위이며 새로운 계약표가 아니다. 시작판이 원측정과 다르면 해당 파일의 실제 차이로 좌표를 연결한다.

사용자 저장범위 지시 sources/storage-scope-direction-2026-10-15.md와 원설계3.3/A22·5.5, 사용자 시간정정을 적용한다. 공통 codec/저장검증과 기존 업무 단언을 재사용한다. 원84가족 quota, 전생산자·전필드·새reader·옛head의 일괄 재입증, 새 검증 framework/장기감사는 만들지 않는다. g5-full의 index 보존사본은 evidence/observed-caches/.claude/skills/do-math/scripts/tests/.selection-index.json이다. 보고의 workspace index 경로는 base로 복원됐으므로 소비하지 않는다. 이 색인의 함수 진입은 결과 단언의 증거가 아니며, 독립 Git의 HEAD 조상 관계도 가정하지 않는다.

## 맡은 범위와 판단

core_engine의174arc/222행을 같은 소유자가 맡는다. _artifact_format_valid, 복구·산출물 보존, 공개 inbox/제어, 실행·활동·대기·종료 전제와 저장 참조의 실제 caller를 확인한다. 같은 상태가 검사된 뒤 불가능해지는 방어 분기는 먼저 불필요한 전제를 줄일 수 있는지 판단하되, 공개 입력의 형식·참조·권한·현재성 검사는 유지한다. record_schemas의 관계 검사는 실제 schema/생산자와 대조하며 전가족 필드 시나리오를 추가하지 않는다.

대상 모듈:
- `do_math/activities.py`
- `do_math/core_engine.py`
- `do_math/dispatch_engine.py`
- `do_math/engine.py`
- `do_math/git_store.py`
- `do_math/lifecycle_engine.py`
- `do_math/maintenance_gate.py`
- `do_math/record_schemas/__init__.py`
- `do_math/repair_execution.py`
- `do_math/repository.py`
- `do_math/state_checks.py`

1. 각 미도달 좌표의 현재 함수·caller·입력 불변식과 기존 시험/단언을 읽는다. 먼저 불필요한 중복 방어·죽은 계약·더는 필요 없는 분기를 제거하거나 줄일 수 있는지 검토한다. 입력/저장 경계의 실제 검증을 약하게 하거나 원래 요구를 지우는 것은 축소가 아니다.
2. 실제 도달 가능한 누락은 가장 싼 기존 시험에 유효한 시작 상태와 정확한 입력/결과·반려·상태/저장 단언을 보완한다. 관련 결함은 같은 task에서 고친다. 모든 소유 파일을 수정/재실행할 필요는 없다. 새 시험/helper 경로는 기존 시험 자리가 맞지 않을 때만 사용한다. 내부 코드 패치·호출만 하는 시험·반려문구/상태를 확인하지 않는 예외 포착·빈 단언은 해결책이 아니다.
3. 의도적으로 도달하지 않는 분기는 원설계5.5와 현재 caller/불변식의 구체 근거를 남긴다. 불필요한 코드는 제거를 우선 검토하고, 필요한 제외는 같은 행의 실제 사유와 기존 구조검사 계약을 따른다. 편의를 위한 blanket no-cover, 층/분모 재분류·임계값 완화·새skip은 금지한다. T4 또는 subprocess의 별도 실행을 T3 도달로 수동 합치지 않는다. 환경/측정 불확실성은 정확한 원인/좌표로 남긴다.
4. 유효한 수리와 필요한 확인을 완료한다. 배정 밖 제공자/공유helper 수정이 실제로 필요하면 그 파일·caller·요구 변화·원반례를 report에 남긴다. 다른 task 사본을 바꾸거나 진행 중 결과를 소비하지 않는다. 쓰기 범위의 상한을 새로운 전수시험 의무로 읽지 않는다.

## 검증과 자원

이 task에 시험슬롯1개를 배정한다. 기본 `--jobs 1`·한 공식명령씩이며, 내부에 여러 worker를 만드는 meta/전체 관문은 실행하지 않는다. 다른 두 독립 task와 합계3이하를 유지한다. 새 전체G4/T3·전체변이·T4/T5·유료호출·실예약/설치변경은 이번 범위가 아니다. 세 task의 종료를 기다리는 barrier는 없으며, manager는 결과가 오는 순서로 수용한다. 충분한 정적 판단은 재실행하지 않는다.

관련 확인은 자기 `scripts/run_tests.py`의 가장 작은 선택으로 수행한다. 새/수정 시험이 지정 분기를 실제로 통과하는지 불확실하면 그 선택에 `--tier T3`를 붙여 공식 측정의 원coverage를 보존할 수 있다. 부분선택의 다른 모듈 미도달/exit1은 전체실패와 구별하고 지정 좌표의 도달·실제행/fixture/단언 결과로 한정 판단한다. 필요하지 않으면 이미 확인한 시험을 일반/T3로 두 번 돌리지 않는다. 동일 기능의 최소 판정이 끝나면 멈춘다. 실행 중 자기 소스는 고정한다.

T3 도구의 실제 Git root가 필요한 경우에만 자기 workspace에 독립 .git/실소스 로컬 기준commit을 준비할 수 있다. g5-full/evidence/prepare.py를 자기 task/짧은 경로에 맞춰 사용하고 준비 전후 제품bytes·자기root/HEAD를 남긴다. 다른 .git 복사·공용Git/index/commit·global 설정·가짜HEAD·remote/push는 금지한다. 기존 GIT_CEILING_DIRECTORIES를 보존하고 자기 task 부모/외부 임시root를 더한다. 임시자료와 새 store/output은 자기 evidence 또는 저장소밖 짧은 고유 경로를 쓴다. 외부권한 변경은 하지 않는다.

보고에는 command/cwd·관측exit·원report/stdout/stderr·선택/고유실제행·fixture·판본SHA·실행중변경을 필요한 검증 범위에서 보존한다. coverage를 사용했다면 해당 모듈의 원좌표/변경후좌표·도달/남김을 함께 기록한다. 서로 다른 판본의 부분 결과를 전체통과로 합산하지 않는다. 소프트 시간초과는 기록하되 중단/skip/포착으로 쓰지 않는다. 생성 index/timing/store는 원자료 보존 후 base의 바이트/부재로 복원해 제품 변경에서 제외한다.

## 완료와 제출

evidence/judgment.md에는 지정 좌표별 또는 같은 원인의 좌표 묶음별로 수리·불필요 분기 제거·근거 있는 제외·외부/배정밖 남김을 기록한다. 기존 근거 재사용의 범위와 새로 해소한 불확실성을 설명한다. 미도달을 덮는 새 quota나 관리 체계를 만들지 않는다. 배정 범위의 실제 남김이 있으면 partial/blocked로 사실대로 보고한다. 이 부분 수리의 완료는 G5 전체 충족이 아니다.

정본 변경과 관련 설명은 허용 범위에서 함께 수정하고 공식 build_skill_mirrors.py로 대응 미러를 생성/check한다. 생성기가 변경한 범위 밖 파일은 제출하지 않는다. 공용 설명에 필요한 계약 변화는 report에 정확한 파일·심볼로 남긴다. 공용 source/context/plan/seams/queue/state, engine, 다른 task·스킬·기존연구, graphify는 수정하지 않는다.

report.json의 changes는 실제 변경만 기록하며 `python C:/math/services/async-development/check.py report C:/math/.async/dm g5-core`를 통과시킨다. 통합 후 남은 공백이 정리된 판본에서 G4/G5 전체를 별도 배정한다. G6~G8·G1~G3 최종연결·L01/Windows1314 실반려는 별도다.
